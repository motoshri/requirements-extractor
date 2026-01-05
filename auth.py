#!/usr/bin/env python3
"""
Authentication Module for ReqIQ
Handles user registration, login, and session management.
Supports both SQLite (local) and PostgreSQL (cloud).
"""

import sqlite3
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
import hashlib
import secrets
import bcrypt

# Try to import PostgreSQL driver
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

# Database path for SQLite (fallback)
DB_PATH = Path.home() / ".reqiq_subscriptions.db"

def get_database_url():
    """Get database URL from environment or Streamlit secrets."""
    # Check environment variable first
    db_url = os.getenv('DATABASE_URL', '')
    
    # Check Streamlit secrets
    if not db_url:
        try:
            import streamlit as st
            if hasattr(st, 'secrets') and 'DATABASE_URL' in st.secrets:
                db_url = st.secrets['DATABASE_URL']
        except:
            pass
    
    # Validate and fix URL if needed
    if db_url and '@' in db_url:
        # Check if password might have @ symbol (malformed URL)
        # Format should be: postgresql://user:password@host:port/db
        # If we see multiple @, the password likely contains @
        parts = db_url.split('@')
        if len(parts) > 2:
            # Password contains @, need to URL-encode it
            import urllib.parse
            # Reconstruct: everything before last @ is user:password, rest is host
            user_pass = '@'.join(parts[:-1])
            host_db = parts[-1]
            
            # Split user:password
            if '://' in user_pass:
                protocol_user = user_pass.split('://')
                if len(protocol_user) == 2:
                    protocol = protocol_user[0]
                    user_pass_part = protocol_user[1]
                    if ':' in user_pass_part:
                        user, password = user_pass_part.split(':', 1)
                        # URL-encode the password
                        password_encoded = urllib.parse.quote(password, safe='')
                        # Reconstruct URL
                        db_url = f"{protocol}://{user}:{password_encoded}@{host_db}"
    
    return db_url


class AuthManager:
    """Manage user authentication."""
    
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.database_url = get_database_url()
        self.use_postgres = bool(self.database_url and POSTGRES_AVAILABLE)
        self._init_database()
    
    def _get_connection(self):
        """Get database connection (PostgreSQL or SQLite)."""
        if self.use_postgres:
            return psycopg2.connect(self.database_url)
        else:
            return self._get_connection()
    
    def _get_placeholder(self):
        """Get parameter placeholder for SQL queries."""
        return '%s' if self.use_postgres else '?'
    
    def _query(self, sql: str) -> str:
        """Convert SQL query placeholders for the active database."""
        if self.use_postgres:
            return sql.replace('?', '%s')
        return sql
    
    def _init_database(self):
        """Initialize database tables for authentication."""
        conn = self._get_connection()
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
        except Exception:
            pass  # Column already exists
        
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN approved_at TIMESTAMP")
        except Exception:
            pass  # Column already exists
        
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN approved_by TEXT")
        except Exception:
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
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(self._query("SELECT user_id FROM users WHERE email = ?"), (email.lower(),))
        existing = cursor.fetchone()
        
        if existing:
            conn.close()
            return {"success": False, "error": "Email already registered"}
        
        # Check if this is the first user or admin email (auto-approve)
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        # Get admin email from environment or Streamlit secrets
        admin_email = os.getenv('ADMIN_EMAIL', '').lower()
        try:
            import streamlit as st
            if hasattr(st, 'secrets') and 'ADMIN_EMAIL' in st.secrets:
                admin_email = st.secrets['ADMIN_EMAIL'].lower()
        except:
            pass
        
        # Auto-approve if: first user OR email matches admin
        is_first_user = user_count == 0
        is_admin_email = admin_email and email.lower() == admin_email
        auto_approve = is_first_user or is_admin_email
        
        # Create user
        user_id = hashlib.sha256(f"{email}{datetime.now().isoformat()}{secrets.token_hex(8)}".encode()).hexdigest()[:16]
        password_hash = self.hash_password(password)
        approval_status = 'approved' if auto_approve else 'pending'
        
        try:
            cursor.execute("""
                INSERT INTO users (user_id, email, password_hash, approval_status)
                VALUES (?, ?, ?, ?)
            """, (user_id, email.lower(), password_hash, approval_status))
            conn.commit()
            conn.close()
            
            return {
                "success": True,
                "user_id": user_id,
                "email": email,
                "auto_approved": auto_approve,
                "approval_status": approval_status
            }
        except Exception as e:
            conn.close()
            return {"success": False, "error": f"Registration failed: {str(e)}"}
    
    def login_user(self, email: str, password: str) -> Dict[str, Any]:
        """Authenticate user and create session."""
        conn = self._get_connection()
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
        
        # Check if this is admin email - auto-approve if pending
        admin_email = os.getenv('ADMIN_EMAIL', '').lower()
        try:
            import streamlit as st
            if hasattr(st, 'secrets') and 'ADMIN_EMAIL' in st.secrets:
                admin_email = st.secrets['ADMIN_EMAIL'].lower()
        except:
            pass
        
        is_admin = admin_email and email.lower() == admin_email
        
        # Check approval status
        approval_status = approval_status or 'pending'
        if approval_status != 'approved':
            # Auto-approve admin users
            if is_admin:
                cursor.execute("""
                    UPDATE users SET approval_status = 'approved', approved_at = CURRENT_TIMESTAMP, approved_by = 'auto_admin'
                    WHERE user_id = ?
                """, (user_id,))
                conn.commit()
                approval_status = 'approved'
            else:
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
        conn = self._get_connection()
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
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM user_sessions WHERE session_id = ?", (session_id,))
            conn.commit()
            conn.close()
            return True
        except Exception:
            return False
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user information by email."""
        conn = self._get_connection()
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
        conn = self._get_connection()
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
            conn = self._get_connection()
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
            conn = self._get_connection()
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
        conn = self._get_connection()
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
        conn = self._get_connection()
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
        
        conn = self._get_connection()
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
        conn = self._get_connection()
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


