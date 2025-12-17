#!/usr/bin/env python3
"""
Subscription Management System for ReqIQ
Handles subscriptions, coupon codes, and usage tracking.
"""

import sqlite3
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import hashlib
import secrets
import json
import sys

# Database path
DB_PATH = Path.home() / ".reqiq_subscriptions.db"

# Subscription tiers
SUBSCRIPTION_TIERS = {
    "free": {
        "name": "Free",
        "price": 0,
        "max_extractions_per_month": 10,
        "max_file_size_mb": 50,
        "features": ["Basic extraction", "Markdown export", "PDF export", "Excel export"]
    },
    "pro": {
        "name": "Pro",
        "price": 9.99,
        "max_extractions_per_month": 100,
        "max_file_size_mb": 500,
        "features": ["All free features", "Priority processing", "Unlimited exports", "Email support"]
    },
    "enterprise": {
        "name": "Enterprise",
        "price": 49.99,
        "max_extractions_per_month": -1,  # Unlimited
        "max_file_size_mb": -1,  # Unlimited
        "features": ["All pro features", "API access", "Custom integrations", "Dedicated support"]
    }
}


class SubscriptionManager:
    """Manage user subscriptions and coupon codes."""
    
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize database tables."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                email TEXT UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        """)
        
        # Subscriptions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS subscriptions (
                subscription_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                tier TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'active',
                start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                end_date TIMESTAMP,
                coupon_code TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        # Coupon codes table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS coupon_codes (
                code TEXT PRIMARY KEY,
                tier TEXT NOT NULL,
                discount_percent INTEGER DEFAULT 100,
                max_uses INTEGER DEFAULT -1,
                current_uses INTEGER DEFAULT 0,
                valid_from TIMESTAMP,
                valid_until TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Usage tracking table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usage_tracking (
                usage_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                action_type TEXT NOT NULL,
                action_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_subscriptions_user ON subscriptions(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_usage_user_date ON usage_tracking(user_id, action_date)")
        
        conn.commit()
        conn.close()
    
    def create_user(self, user_id: str, email: Optional[str] = None) -> bool:
        """Create a new user."""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR IGNORE INTO users (user_id, email) VALUES (?, ?)",
                (user_id, email)
            )
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error creating user: {e}")
            return False
    
    def get_or_create_user(self, user_id: str) -> str:
        """Get or create a user ID."""
        self.create_user(user_id)
        return user_id
    
    def create_coupon_code(
        self,
        code: str,
        tier: str,
        discount_percent: int = 100,
        max_uses: int = -1,
        valid_until: Optional[datetime] = None
    ) -> bool:
        """Create a coupon code for free subscription."""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO coupon_codes 
                (code, tier, discount_percent, max_uses, valid_until)
                VALUES (?, ?, ?, ?, ?)
            """, (
                code.upper(),
                tier,
                discount_percent,
                max_uses,
                valid_until.isoformat() if valid_until else None
            ))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False  # Code already exists
        except Exception as e:
            print(f"Error creating coupon: {e}")
            return False
    
    def validate_coupon_code(self, code: str) -> Optional[Dict[str, Any]]:
        """Validate a coupon code and return tier info if valid."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute("""
            SELECT tier, discount_percent, max_uses, current_uses, valid_from, valid_until
            FROM coupon_codes
            WHERE code = ?
        """, (code.upper(),))
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return None
        
        tier, discount_percent, max_uses, current_uses, valid_from, valid_until = result
        
        # Check if code is expired
        if valid_until:
            valid_until_dt = datetime.fromisoformat(valid_until)
            if datetime.now() > valid_until_dt:
                return None
        
        # Check if code has reached max uses
        if max_uses > 0 and current_uses >= max_uses:
            return None
        
        return {
            "tier": tier,
            "discount_percent": discount_percent,
            "max_uses": max_uses,
            "current_uses": current_uses
        }
    
    def apply_coupon_code(self, user_id: str, code: str) -> Dict[str, Any]:
        """Apply a coupon code to create a subscription."""
        coupon_info = self.validate_coupon_code(code)
        if not coupon_info:
            return {"success": False, "error": "Invalid or expired coupon code"}
        
        # Increment usage count
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE coupon_codes
            SET current_uses = current_uses + 1
            WHERE code = ?
        """, (code.upper(),))
        
        # Create subscription
        tier = coupon_info["tier"]
        subscription_id = f"sub_{secrets.token_hex(16)}"
        
        # Calculate end date (e.g., 1 month for free tier)
        if tier == "free":
            end_date = datetime.now() + timedelta(days=30)
        else:
            end_date = datetime.now() + timedelta(days=365)  # 1 year for paid tiers
        
        cursor.execute("""
            INSERT INTO subscriptions 
            (subscription_id, user_id, tier, status, end_date, coupon_code)
            VALUES (?, ?, ?, 'active', ?, ?)
        """, (subscription_id, user_id, tier, end_date.isoformat(), code.upper()))
        
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "subscription_id": subscription_id,
            "tier": tier,
            "end_date": end_date.isoformat()
        }
    
    def get_user_subscription(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user's current active subscription."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute("""
            SELECT subscription_id, tier, status, start_date, end_date, coupon_code
            FROM subscriptions
            WHERE user_id = ? AND status = 'active'
            ORDER BY start_date DESC
            LIMIT 1
        """, (user_id,))
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return None
        
        subscription_id, tier, status, start_date, end_date, coupon_code = result
        
        # Check if subscription is expired
        if end_date:
            end_date_dt = datetime.fromisoformat(end_date)
            if datetime.now() > end_date_dt:
                # Mark as expired
                self._expire_subscription(subscription_id)
                return None
        
        tier_info = SUBSCRIPTION_TIERS.get(tier, SUBSCRIPTION_TIERS["free"])
        
        return {
            "subscription_id": subscription_id,
            "tier": tier,
            "status": status,
            "start_date": start_date,
            "end_date": end_date,
            "coupon_code": coupon_code,
            "tier_info": tier_info
        }
    
    def _expire_subscription(self, subscription_id: str):
        """Mark subscription as expired."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE subscriptions
            SET status = 'expired'
            WHERE subscription_id = ?
        """, (subscription_id,))
        conn.commit()
        conn.close()
    
    def track_usage(self, user_id: str, action_type: str, metadata: Optional[Dict] = None):
        """Track user usage for rate limiting."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO usage_tracking (user_id, action_type, metadata)
            VALUES (?, ?, ?)
        """, (user_id, action_type, json.dumps(metadata) if metadata else None))
        conn.commit()
        conn.close()
    
    def get_monthly_usage(self, user_id: str, action_type: str = "extraction") -> int:
        """Get user's usage count for current month."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM usage_tracking
            WHERE user_id = ? 
            AND action_type = ?
            AND action_date >= datetime('now', 'start of month')
        """, (user_id, action_type))
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def check_usage_limit(self, user_id: str, action_type: str = "extraction") -> Dict[str, Any]:
        """Check if user has exceeded usage limits."""
        subscription = self.get_user_subscription(user_id)
        
        if not subscription:
            # No subscription - use free tier limits
            tier_info = SUBSCRIPTION_TIERS["free"]
        else:
            tier_info = subscription["tier_info"]
        
        max_extractions = tier_info["max_extractions_per_month"]
        current_usage = self.get_monthly_usage(user_id, action_type)
        
        if max_extractions == -1:  # Unlimited
            return {"allowed": True, "current": current_usage, "limit": "unlimited"}
        
        allowed = current_usage < max_extractions
        remaining = max(0, max_extractions - current_usage)
        
        return {
            "allowed": allowed,
            "current": current_usage,
            "limit": max_extractions,
            "remaining": remaining
        }


def generate_user_id() -> str:
    """Generate a unique user ID based on session."""
    try:
        import streamlit as st
        if 'user_id' not in st.session_state:
            # Generate a unique ID based on session info
            session_info = f"{st.session_state.get('_session_id', '')}_{datetime.now().isoformat()}"
            user_id = hashlib.sha256(session_info.encode()).hexdigest()[:16]
            st.session_state.user_id = user_id
        return st.session_state.user_id
    except ImportError:
        # Fallback if streamlit is not available
        return hashlib.sha256(f"{os.getpid()}_{datetime.now().isoformat()}".encode()).hexdigest()[:16]

