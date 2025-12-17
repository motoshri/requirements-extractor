#!/usr/bin/env python3
"""
Security Module for ReqIQ
Handles authentication, authorization, input validation, and rate limiting.
"""

import re
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from pathlib import Path
import streamlit as st

# File upload security
ALLOWED_EXTENSIONS = {'.txt', '.vtt', '.json', '.mp4', '.mov', '.avi', '.mkv', '.webm', '.mpeg4'}
MAX_FILE_SIZE_MB = 1024  # 1GB default, can be overridden by subscription

# Input validation patterns
EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
COUPON_CODE_PATTERN = re.compile(r'^[A-Z0-9]{4,20}$')


class SecurityManager:
    """Manage security features including validation and rate limiting."""
    
    @staticmethod
    def validate_file_upload(uploaded_file, max_size_mb: int = MAX_FILE_SIZE_MB) -> Dict[str, Any]:
        """Validate uploaded file for security."""
        errors = []
        
        # Check file extension
        file_extension = Path(uploaded_file.name).suffix.lower()
        if file_extension not in ALLOWED_EXTENSIONS:
            errors.append(f"File type '{file_extension}' is not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}")
        
        # Check file size (-1 means unlimited)
        file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
        if max_size_mb > 0 and file_size_mb > max_size_mb:
            errors.append(f"File size ({file_size_mb:.2f} MB) exceeds maximum allowed size ({max_size_mb} MB)")
        
        # Check for suspicious file names
        if any(char in uploaded_file.name for char in ['..', '/', '\\', '<', '>', '|', ':', '*', '?']):
            errors.append("File name contains invalid characters")
        
        if errors:
            return {"valid": False, "errors": errors}
        
        return {"valid": True, "file_size_mb": file_size_mb}
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format."""
        if not email or not isinstance(email, str):
            return False
        return bool(EMAIL_PATTERN.match(email.strip()))
    
    @staticmethod
    def validate_coupon_code(code: str) -> bool:
        """Validate coupon code format."""
        if not code or not isinstance(code, str):
            return False
        return bool(COUPON_CODE_PATTERN.match(code.strip().upper()))
    
    @staticmethod
    def sanitize_input(text: str, max_length: int = 10000) -> str:
        """Sanitize user input to prevent injection attacks."""
        if not isinstance(text, str):
            return ""
        
        # Remove null bytes
        text = text.replace('\x00', '')
        
        # Truncate if too long
        if len(text) > max_length:
            text = text[:max_length]
        
        # Remove potentially dangerous characters (but keep newlines for transcripts)
        # Only remove script tags and similar
        text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'javascript:', '', text, flags=re.IGNORECASE)
        
        return text.strip()
    
    @staticmethod
    def validate_api_key_format(api_key: str) -> bool:
        """Validate OpenAI API key format."""
        if not api_key or not isinstance(api_key, str):
            return False
        return api_key.startswith('sk-') and len(api_key) > 20
    
    @staticmethod
    def check_rate_limit(user_id: str, action: str, max_requests: int = 10, window_minutes: int = 60) -> Dict[str, Any]:
        """Check rate limit for user actions."""
        # Use Streamlit session state for rate limiting
        rate_limit_key = f"rate_limit_{action}_{user_id}"
        
        if rate_limit_key not in st.session_state:
            st.session_state[rate_limit_key] = {
                "count": 0,
                "window_start": datetime.now()
            }
        
        rate_data = st.session_state[rate_limit_key]
        window_start = datetime.fromisoformat(rate_data["window_start"]) if isinstance(rate_data["window_start"], str) else rate_data["window_start"]
        
        # Reset if window expired
        if datetime.now() - window_start > timedelta(minutes=window_minutes):
            rate_data["count"] = 0
            rate_data["window_start"] = datetime.now().isoformat()
        
        # Check limit
        if rate_data["count"] >= max_requests:
            return {
                "allowed": False,
                "message": f"Rate limit exceeded. Maximum {max_requests} requests per {window_minutes} minutes.",
                "retry_after": (window_start + timedelta(minutes=window_minutes) - datetime.now()).total_seconds()
            }
        
        # Increment counter
        rate_data["count"] += 1
        st.session_state[rate_limit_key] = rate_data
        
        return {
            "allowed": True,
            "remaining": max_requests - rate_data["count"]
        }
    
    @staticmethod
    def generate_csrf_token() -> str:
        """Generate CSRF token for forms."""
        if 'csrf_token' not in st.session_state:
            st.session_state.csrf_token = secrets.token_urlsafe(32)
        return st.session_state.csrf_token
    
    @staticmethod
    def validate_csrf_token(token: str) -> bool:
        """Validate CSRF token."""
        return token == st.session_state.get('csrf_token', '')


def require_subscription(func):
    """Decorator to require active subscription for a function."""
    def wrapper(*args, **kwargs):
        from subscription_manager import SubscriptionManager, generate_user_id
        
        user_id = generate_user_id()
        manager = SubscriptionManager()
        subscription = manager.get_user_subscription(user_id)
        
        if not subscription:
            st.error("❌ Subscription required. Please subscribe to continue.")
            st.info("💡 Use a coupon code to get a free subscription!")
            st.stop()
            return None
        
        return func(*args, **kwargs)
    return wrapper



