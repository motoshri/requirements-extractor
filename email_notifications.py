#!/usr/bin/env python3
"""
Email Notification System for ReqIQ
Handles sending emails for user approvals and notifications.
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, Any
from pathlib import Path


class EmailNotifier:
    """Handle email notifications."""
    
    def __init__(self):
        self.smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_user = os.getenv('SMTP_USER', '')
        self.smtp_password = os.getenv('SMTP_PASSWORD', '')
        self.smtp_from = os.getenv('SMTP_FROM', self.smtp_user)
        self.app_name = os.getenv('APP_NAME', 'ReqIQ')
        self.app_url = os.getenv('APP_URL', 'http://localhost:8501')
        self.admin_email = os.getenv('ADMIN_EMAIL', '')
        
        # Try to get from Streamlit secrets if available
        try:
            import streamlit as st
            if hasattr(st, 'secrets'):
                secrets = st.secrets
                if 'email' in secrets:
                    email_config = secrets['email']
                    self.smtp_host = email_config.get('smtp_host', self.smtp_host)
                    self.smtp_port = int(email_config.get('smtp_port', self.smtp_port))
                    self.smtp_user = email_config.get('smtp_user', self.smtp_user)
                    self.smtp_password = email_config.get('smtp_password', self.smtp_password)
                    self.smtp_from = email_config.get('smtp_from', self.smtp_user)
                if 'admin' in secrets:
                    self.admin_email = secrets['admin'].get('email', self.admin_email)
                if 'app' in secrets:
                    self.app_name = secrets['app'].get('name', self.app_name)
                    self.app_url = secrets['app'].get('url', self.app_url)
        except:
            pass  # Not in Streamlit context
    
    def _send_email(self, to_email: str, subject: str, body_html: str, body_text: str = None) -> bool:
        """Send an email."""
        if not self.smtp_user or not self.smtp_password:
            print(f"⚠️ Email not configured. Would send to {to_email}: {subject}")
            return False
        
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = self.smtp_from
            msg['To'] = to_email
            msg['Subject'] = subject
            
            if body_text:
                msg.attach(MIMEText(body_text, 'plain'))
            msg.attach(MIMEText(body_html, 'html'))
            
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            return True
        except Exception as e:
            print(f"❌ Failed to send email to {to_email}: {str(e)}")
            return False
    
    def notify_admin_new_signup(self, user_email: str, user_id: str) -> bool:
        """Notify admin of new user signup."""
        if not self.admin_email:
            print("⚠️ Admin email not configured. Cannot send notification.")
            return False
        
        subject = f"🔔 New User Signup: {user_email}"
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #1f77b4;">New User Signup</h2>
                <p>A new user has signed up and is pending approval:</p>
                <div style="background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p><strong>Email:</strong> {user_email}</p>
                    <p><strong>User ID:</strong> {user_id}</p>
                </div>
                <p>Please log in to the admin panel to approve or reject this user.</p>
                <div style="margin: 30px 0; text-align: center;">
                    <a href="{self.app_url}" 
                       style="background: #1f77b4; color: white; padding: 12px 30px; 
                              text-decoration: none; border-radius: 5px; display: inline-block;">
                        Go to Admin Panel
                    </a>
                </div>
                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                <p style="color: #666; font-size: 12px;">
                    This is an automated notification from {self.app_name}.
                </p>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
New User Signup

A new user has signed up and is pending approval:

Email: {user_email}
User ID: {user_id}

Please log in to the admin panel to approve or reject this user.
Admin Panel: {self.app_url}

---
This is an automated notification from {self.app_name}.
        """
        
        return self._send_email(self.admin_email, subject, html_body, text_body)
    
    def notify_user_approved(self, user_email: str) -> bool:
        """Notify user their account has been approved."""
        subject = f"✅ Your {self.app_name} Account Has Been Approved!"
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #28a745;">🎉 Account Approved!</h2>
                <p>Great news! Your account has been approved and you can now access {self.app_name}.</p>
                <div style="background: #d4edda; border: 1px solid #c3e6cb; padding: 15px; 
                            border-radius: 5px; margin: 20px 0;">
                    <p style="margin: 0;"><strong>Your account is now active!</strong></p>
                </div>
                <p>You can now log in and start using all the features:</p>
                <ul>
                    <li>Extract requirements from meeting transcripts</li>
                    <li>Export to PDF, Excel, or Markdown</li>
                    <li>Use local or cloud-based transcription</li>
                    <li>And much more!</li>
                </ul>
                <div style="margin: 30px 0; text-align: center;">
                    <a href="{self.app_url}" 
                       style="background: #28a745; color: white; padding: 12px 30px; 
                              text-decoration: none; border-radius: 5px; display: inline-block;">
                        Login Now
                    </a>
                </div>
                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                <p style="color: #666; font-size: 12px;">
                    If you have any questions, please contact support.
                </p>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
Account Approved!

Great news! Your account has been approved and you can now access {self.app_name}.

Your account is now active!

You can now log in and start using all the features:
- Extract requirements from meeting transcripts
- Export to PDF, Excel, or Markdown
- Use local or cloud-based transcription
- And much more!

Login here: {self.app_url}

---
If you have any questions, please contact support.
        """
        
        return self._send_email(user_email, subject, html_body, text_body)
    
    def notify_user_rejected(self, user_email: str, reason: str = None) -> bool:
        """Notify user their account has been rejected."""
        subject = f"❌ Your {self.app_name} Account Request"
        
        reason_text = f"<p><strong>Reason:</strong> {reason}</p>" if reason else ""
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #dc3545;">Account Request Status</h2>
                <p>We're sorry, but your account request has been declined at this time.</p>
                {reason_text}
                <div style="background: #f8d7da; border: 1px solid #f5c6cb; padding: 15px; 
                            border-radius: 5px; margin: 20px 0;">
                    <p style="margin: 0;">Your account is not active and you cannot access the application.</p>
                </div>
                <p>If you believe this is an error or would like more information, please contact support.</p>
                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                <p style="color: #666; font-size: 12px;">
                    If you have any questions, please contact support.
                </p>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
Account Request Status

We're sorry, but your account request has been declined at this time.
{('Reason: ' + reason) if reason else ''}

Your account is not active and you cannot access the application.

If you believe this is an error or would like more information, please contact support.

---
If you have any questions, please contact support.
        """
        
        return self._send_email(user_email, subject, html_body, text_body)


# Singleton instance
_email_notifier = None

def get_email_notifier() -> EmailNotifier:
    """Get the email notifier instance."""
    global _email_notifier
    if _email_notifier is None:
        _email_notifier = EmailNotifier()
    return _email_notifier


