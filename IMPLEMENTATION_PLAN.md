# Email Approval System - Implementation Plan

## 🎯 What We're Building

A complete email-based approval system where:
1. User signs up → Status: "pending"
2. Admin receives email notification
3. Admin logs into admin panel
4. Admin approves/rejects user
5. User receives email notification
6. Approved users can access the app

---

## 📋 Implementation Steps

### Step 1: Update Database Schema (auth.py)
- Add `approval_status` column (pending/approved/rejected)
- Add `approved_at` timestamp
- Add `approved_by` admin ID
- Create `admin_users` table

### Step 2: Create Email Notification System (email_notifications.py)
- SMTP email sending
- Email templates for:
  - Admin: "New user signup"
  - User: "Account approved"
  - User: "Account rejected"

### Step 3: Create Admin Panel (admin_panel.py)
- Admin login
- Dashboard showing pending users
- Approve/Reject buttons
- View all users
- User management

### Step 4: Update Authentication Flow (app.py)
- Check approval status on login
- Show "Pending Approval" message
- Block access until approved

### Step 5: Configuration
- Admin email setup
- Email service configuration (SMTP)
- Environment variables

---

## 🚀 Quick Start Guide

Once implemented, here's how to use:

1. **Set Admin Email**:
   ```python
   # In .streamlit/secrets.toml or environment
   ADMIN_EMAIL = "admin@yourcompany.com"
   ADMIN_PASSWORD = "your-secure-password"
   ```

2. **Configure Email** (choose one):
   ```python
   # Option 1: Gmail SMTP
   SMTP_HOST = "smtp.gmail.com"
   SMTP_PORT = 587
   SMTP_USER = "your-email@gmail.com"
   SMTP_PASSWORD = "your-app-password"
   
   # Option 2: SendGrid
   SENDGRID_API_KEY = "your-sendgrid-key"
   ```

3. **Create First Admin**:
   Run admin creation script or sign up first user as admin

4. **Deploy**:
   - Users sign up → Admin gets email
   - Admin approves → User gets email
   - User can now login and use app

---

## 📁 Files to Create/Update

### New Files:
1. `email_notifications.py` - Email sending functionality
2. `admin_panel.py` - Admin interface
3. `create_admin.py` - Script to create first admin

### Files to Update:
1. `auth.py` - Add approval status support
2. `app.py` - Integrate approval checks
3. `requirements.txt` - Add email dependencies

---

## 🔧 Configuration Template

Create `.streamlit/secrets.toml`:
```toml
[admin]
email = "admin@yourcompany.com"
password = "secure-password-here"

[email]
# Option 1: SMTP
smtp_host = "smtp.gmail.com"
smtp_port = 587
smtp_user = "your-email@gmail.com"
smtp_password = "your-app-password"
smtp_from = "noreply@yourcompany.com"

# Option 2: SendGrid
# sendgrid_api_key = "your-key-here"

[app]
name = "ReqIQ"
url = "https://yourapp.streamlit.app"
```

---

## ⚡ Status

- [x] Implementation plan created
- [ ] Database schema updated
- [ ] Email system created
- [ ] Admin panel created
- [ ] Auth flow updated
- [ ] Configuration setup
- [ ] Testing completed

---

**Next**: Starting implementation now!


