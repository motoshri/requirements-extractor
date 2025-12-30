#!/usr/bin/env python3
"""
Admin Panel for ReqIQ
Provides interface for admins to manage users and approve/reject registrations.
"""

import streamlit as st
from auth import AuthManager
from email_notifications import EmailNotifier
from typing import List, Dict, Any


def show_admin_login():
    """Show admin login page."""
    st.markdown("### 🔐 Admin Login")
    
    with st.form("admin_login_form"):
        email = st.text_input("Admin Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login", type="primary")
        
        if submit:
            auth = AuthManager()
            result = auth.verify_admin(email, password)
            
            if result:
                st.session_state.admin_authenticated = True
                st.session_state.admin_id = result['admin_id']
                st.session_state.admin_email = result['email']
                st.success("✅ Admin login successful!")
                st.rerun()
            else:
                st.error("❌ Invalid admin credentials")


def show_admin_dashboard():
    """Show admin dashboard with user management."""
    auth = AuthManager()
    email_notifier = EmailNotifier()
    
    st.markdown("## 🔧 Admin Dashboard")
    
    # Header with logout
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"**Logged in as:** {st.session_state.get('admin_email', 'Admin')}")
    with col2:
        if st.button("🚪 Logout", key="admin_logout"):
            st.session_state.admin_authenticated = False
            st.session_state.admin_id = None
            st.session_state.admin_email = None
            st.rerun()
    
    st.markdown("---")
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["📋 Pending Approvals", "👥 All Users", "📊 Statistics"])
    
    with tab1:
        show_pending_approvals(auth, email_notifier)
    
    with tab2:
        show_all_users(auth)
    
    with tab3:
        show_statistics(auth)


def show_pending_approvals(auth: AuthManager, email_notifier: EmailNotifier):
    """Show list of users pending approval."""
    st.markdown("### 📋 Pending User Approvals")
    
    pending_users = auth.get_pending_users()
    
    if not pending_users:
        st.success("✅ No pending approvals - all users are processed!")
        return
    
    st.info(f"**{len(pending_users)}** user(s) waiting for approval")
    
    for user in pending_users:
        with st.container():
            st.markdown("---")
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.markdown(f"**Email:** {user['email']}")
                st.markdown(f"**Registered:** {user.get('created_at', 'Unknown')}")
                st.markdown(f"**User ID:** `{user['user_id']}`")
            
            with col2:
                if st.button("✅ Approve", key=f"approve_{user['user_id']}", type="primary"):
                    admin_id = st.session_state.get('admin_id', 'admin')
                    if auth.approve_user(user['user_id'], admin_id):
                        st.success(f"✅ Approved {user['email']}")
                        
                        # Send approval email
                        try:
                            email_notifier.send_approval_notification(user['email'], approved=True)
                            st.info("📧 Approval email sent to user")
                        except Exception as e:
                            st.warning(f"⚠️ User approved, but email failed: {str(e)}")
                        
                        st.rerun()
                    else:
                        st.error("❌ Failed to approve user")
            
            with col3:
                if st.button("❌ Reject", key=f"reject_{user['user_id']}", type="secondary"):
                    admin_id = st.session_state.get('admin_id', 'admin')
                    if auth.reject_user(user['user_id'], admin_id):
                        st.success(f"✅ Rejected {user['email']}")
                        
                        # Send rejection email
                        try:
                            email_notifier.send_approval_notification(user['email'], approved=False)
                            st.info("📧 Rejection email sent to user")
                        except Exception as e:
                            st.warning(f"⚠️ User rejected, but email failed: {str(e)}")
                        
                        st.rerun()
                    else:
                        st.error("❌ Failed to reject user")


def show_all_users(auth: AuthManager):
    """Show all users with their approval status."""
    st.markdown("### 👥 All Users")
    
    all_users = auth.get_all_users()
    
    if not all_users:
        st.info("No users found")
        return
    
    # Filter options
    col1, col2 = st.columns([2, 1])
    with col1:
        filter_status = st.selectbox(
            "Filter by Status",
            ["All", "Approved", "Pending", "Rejected"],
            key="user_filter"
        )
    
    # Filter users
    if filter_status == "All":
        filtered_users = all_users
    else:
        filtered_users = [u for u in all_users if u.get('approval_status', 'pending').lower() == filter_status.lower()]
    
    st.markdown(f"**Total:** {len(filtered_users)} user(s)")
    
    # Display users in a table format
    if filtered_users:
        for user in filtered_users:
            status = user.get('approval_status', 'pending').upper()
            status_color = {
                'APPROVED': '🟢',
                'PENDING': '🟡',
                'REJECTED': '🔴'
            }.get(status, '⚪')
            
            st.markdown(f"""
            **{status_color} {user['email']}** - Status: {status}
            - User ID: `{user['user_id']}`
            - Created: {user.get('created_at', 'Unknown')}
            - Last Login: {user.get('last_login', 'Never')}
            """)
            st.markdown("---")


def show_statistics(auth: AuthManager):
    """Show user statistics."""
    st.markdown("### 📊 User Statistics")
    
    all_users = auth.get_all_users()
    
    if not all_users:
        st.info("No users to show statistics")
        return
    
    # Calculate stats
    total_users = len(all_users)
    approved = len([u for u in all_users if u.get('approval_status', '').lower() == 'approved'])
    pending = len([u for u in all_users if u.get('approval_status', '').lower() == 'pending'])
    rejected = len([u for u in all_users if u.get('approval_status', '').lower() == 'rejected'])
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Users", total_users)
    with col2:
        st.metric("Approved", approved, delta=f"{approved/total_users*100:.0f}%" if total_users > 0 else "0%")
    with col3:
        st.metric("Pending", pending, delta=f"{pending/total_users*100:.0f}%" if total_users > 0 else "0%")
    with col4:
        st.metric("Rejected", rejected, delta=f"{rejected/total_users*100:.0f}%" if total_users > 0 else "0%")


def is_admin_authenticated() -> bool:
    """Check if admin is authenticated."""
    return st.session_state.get('admin_authenticated', False)


def require_admin():
    """Require admin authentication, redirect to login if not."""
    if not is_admin_authenticated():
        show_admin_login()
        st.stop()

