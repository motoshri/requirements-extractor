#!/usr/bin/env python3
"""
Authentication Module for ReqIQ
Handles user registration, login, and session management.
"""

import sqlite3
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
import hashlib
import secrets
import bcrypt

# Database path (same as subscription manager)
DB_PATH = Path.home() / ".reqiq_subscriptions.db"


class AuthManager:
    """Manage user authentication."""
    
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize database tables for authentication."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Users table (enhanced with password and approval status)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                is_active INTEGER DEFAULT 1,
                approval_status TEXT DEFAULT 'pending',
                approved_at TIMESTAMP,
                approved_by TEXT
            )
        """)
        
        # Admin users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admin_users (
                admin_id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active INTEGER DEFAULT 1
            )
        """)
        
        # Add approval columns if table already exists (migration)
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN approval_status TEXT DEFAULT 'pending'")
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN approved_at TIMESTAMP")
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN approved_by TEXT")
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        # Sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_sessions (
                session_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_approval ON users(approval_status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_user ON user_sessions(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_admin_email ON admin_users(email)")
        
        conn.commit()
        conn.close()
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt."""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash."""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
        except Exception:
            return False
    
    def register_user(self, email: str, password: str) -> Dict[str, Any]:
        """Register a new user."""
        # Validate email format
        if not email or '@' not in email:
            return {"success": False, "error": "Invalid email address"}
        
        # Validate password
        if not password or len(password) < 6:
            return {"success": False, "error": "Password must be at least 6 characters"}
        
        # Check if user already exists
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM users WHERE email = ?", (email.lower(),))
        existing = cursor.fetchone()
        
        if existing:
            conn.close()
            return {"success": False, "error": "Email already registered"}
        
        # Create user
        user_id = hashlib.sha256(f"{email}{datetime.now().isoformat()}{secrets.token_hex(8)}".encode()).hexdigest()[:16]
        password_hash = self.hash_password(password)
        
        try:
            cursor.execute("""
                INSERT INTO users (user_id, email, password_hash)
                VALUES (?, ?, ?)
            """, (user_id, email.lower(), password_hash))
            conn.commit()
            conn.close()
            
            return {
                "success": True,
                "user_id": user_id,
                "email": email
            }
        except Exception as e:
            conn.close()
            return {"success": False, "error": f"Registration failed: {str(e)}"}
    
    def login_user(self, email: str, password: str) -> Dict[str, Any]:
        """Authenticate user and create session."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Get user
        cursor.execute("""
            SELECT user_id, password_hash, is_active, approval_status
            FROM users
            WHERE email = ?
        """, (email.lower(),))
        user = cursor.fetchone()
        
        if not user:
            conn.close()
            return {"success": False, "error": "Invalid email or password"}
        
        user_id, password_hash, is_active, approval_status = user
        
        if not is_active:
            conn.close()
            return {"success": False, "error": "Account is inactive"}
        
        # Verify password
        if not self.verify_password(password, password_hash):
            conn.close()
            return {"success": False, "error": "Invalid email or password"}
        
        # Check approval status
        approval_status = approval_status or 'pending'
        if approval_status != 'approved':
            conn.close()
            return {
                "success": False,
                "error": f"Account is {approval_status}. Please wait for admin approval.",
                "approval_status": approval_status
            }
        
        # Update last login
        cursor.execute("""
            UPDATE users
            SET last_login = CURRENT_TIMESTAMP
            WHERE user_id = ?
        """, (user_id,))
        
        # Create session
        session_id = secrets.token_urlsafe(32)
        from datetime import timedelta
        expires_at = datetime.now() + timedelta(days=30)  # 30-day session
        
        cursor.execute("""
            INSERT INTO user_sessions (session_id, user_id, expires_at)
            VALUES (?, ?, ?)
        """, (session_id, user_id, expires_at.isoformat()))
        
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "user_id": user_id,
            "email": email,
            "session_id": session_id
        }
    
    def verify_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Verify session and return user info."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT s.user_id, s.expires_at, u.email, u.is_active
            FROM user_sessions s
            JOIN users u ON s.user_id = u.user_id
            WHERE s.session_id = ?
        """, (session_id,))
        session = cursor.fetchone()
        
        if not session:
            conn.close()
            return None
        
        user_id, expires_at_str, email, is_active = session
        
        # Check if session expired
        expires_at = datetime.fromisoformat(expires_at_str)
        if datetime.now() > expires_at:
            # Delete expired session
            cursor.execute("DELETE FROM user_sessions WHERE session_id = ?", (session_id,))
            conn.commit()
            conn.close()
            return None
        
        if not is_active:
            conn.close()
            return None
        
        conn.close()
        return {
            "user_id": user_id,
            "email": email,
            "session_id": session_id
        }
    
    def logout_user(self, session_id: str) -> bool:
        """Logout user by deleting session."""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute("DELETE FROM user_sessions WHERE session_id = ?", (session_id,))
            conn.commit()
            conn.close()
            return True
        except Exception:
            return False
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user information by email."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute("""
            SELECT user_id, email, created_at, last_login, approval_status
            FROM users
            WHERE email = ?
        """, (email.lower(),))
        user = cursor.fetchone()
        conn.close()
        
        if not user:
            return None
        
        return {
            "user_id": user[0],
            "email": user[1],
            "created_at": user[2],
            "last_login": user[3],
            "approval_status": user[4] if len(user) > 4 else 'pending'
        }
    
    def get_user_approval_status(self, user_id: str) -> Optional[str]:
        """Get user approval status."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT approval_status FROM users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return None
        
        return result[0] or 'pending'
    
    def approve_user(self, user_id: str, admin_id: str) -> bool:
        """Approve a user."""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users
                SET approval_status = 'approved',
                    approved_at = CURRENT_TIMESTAMP,
                    approved_by = ?
                WHERE user_id = ?
            """, (admin_id, user_id))
            conn.commit()
            conn.close()
            return True
        except Exception:
            return False
    
    def reject_user(self, user_id: str, admin_id: str) -> bool:
        """Reject a user."""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users
                SET approval_status = 'rejected',
                    approved_at = CURRENT_TIMESTAMP,
                    approved_by = ?
                WHERE user_id = ?
            """, (admin_id, user_id))
            conn.commit()
            conn.close()
            return True
        except Exception:
            return False
    
    def get_pending_users(self) -> list:
        """Get all users pending approval."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute("""
            SELECT user_id, email, created_at
            FROM users
            WHERE approval_status = 'pending' OR approval_status IS NULL
            ORDER BY created_at DESC
        """)
        users = cursor.fetchall()
        conn.close()
        
        return [
            {
                "user_id": user[0],
                "email": user[1],
                "created_at": user[2]
            }
            for user in users
        ]
    
    def get_all_users(self) -> list:
        """Get all users with approval status."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute("""
            SELECT user_id, email, created_at, approval_status, last_login
            FROM users
            ORDER BY created_at DESC
        """)
        users = cursor.fetchall()
        conn.close()
        
        return [
            {
                "user_id": user[0],
                "email": user[1],
                "created_at": user[2],
                "approval_status": user[3] or 'pending',
                "last_login": user[4]
            }
            for user in users
        ]
    
    # Admin functions
    def create_admin(self, email: str, password: str) -> Dict[str, Any]:
        """Create an admin user."""
        if not email or '@' not in email:
            return {"success": False, "error": "Invalid email address"}
        
        if not password or len(password) < 8:
            return {"success": False, "error": "Password must be at least 8 characters"}
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Check if admin already exists
        cursor.execute("SELECT admin_id FROM admin_users WHERE email = ?", (email.lower(),))
        if cursor.fetchone():
            conn.close()
            return {"success": False, "error": "Admin already exists"}
        
        # Create admin
        admin_id = hashlib.sha256(f"{email}admin{datetime.now().isoformat()}{secrets.token_hex(8)}".encode()).hexdigest()[:16]
        password_hash = self.hash_password(password)
        
        try:
            cursor.execute("""
                INSERT INTO admin_users (admin_id, email, password_hash)
                VALUES (?, ?, ?)
            """, (admin_id, email.lower(), password_hash))
            conn.commit()
            conn.close()
            
            return {
                "success": True,
                "admin_id": admin_id,
                "email": email
            }
        except Exception as e:
            conn.close()
            return {"success": False, "error": f"Failed to create admin: {str(e)}"}
    
    def verify_admin(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Verify admin credentials."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT admin_id, password_hash, is_active
            FROM admin_users
            WHERE email = ?
        """, (email.lower(),))
        admin = cursor.fetchone()
        
        if not admin:
            conn.close()
            return None
        
        admin_id, password_hash, is_active = admin
        
        if not is_active:
            conn.close()
            return None
        
        if not self.verify_password(password, password_hash):
            conn.close()
            return None
        
        conn.close()
        return {
            "admin_id": admin_id,
            "email": email
        }


