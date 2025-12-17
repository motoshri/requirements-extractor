#!/usr/bin/env python3
"""
Admin Setup Script for ReqIQ
Run this to create an admin account and approve users.
"""

import sys
import os
from pathlib import Path

# Add the current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from auth import AuthManager

def main():
    auth = AuthManager()
    
    print("=" * 50)
    print("ReqIQ Admin Setup")
    print("=" * 50)
    
    while True:
        print("\nOptions:")
        print("1. Create admin account")
        print("2. Approve a pending user")
        print("3. List pending users")
        print("4. List all users")
        print("5. Auto-approve user by email")
        print("6. Exit")
        
        choice = input("\nEnter choice (1-6): ").strip()
        
        if choice == "1":
            email = input("Admin email: ").strip()
            password = input("Admin password: ").strip()
            
            if not email or not password:
                print("❌ Email and password are required")
                continue
            
            result = auth.create_admin(email, password)
            if result.get("success"):
                print(f"✅ Admin account created: {email}")
            else:
                print(f"❌ Error: {result.get('error')}")
        
        elif choice == "2":
            pending = auth.get_pending_users()
            if not pending:
                print("No pending users")
                continue
            
            print("\nPending users:")
            for i, user in enumerate(pending, 1):
                print(f"  {i}. {user['email']} (ID: {user['user_id'][:8]}...)")
            
            try:
                idx = int(input("Select user number to approve: ")) - 1
                if 0 <= idx < len(pending):
                    user_id = pending[idx]['user_id']
                    if auth.approve_user(user_id, "admin_setup"):
                        print(f"✅ Approved: {pending[idx]['email']}")
                    else:
                        print("❌ Failed to approve user")
                else:
                    print("Invalid selection")
            except ValueError:
                print("Invalid input")
        
        elif choice == "3":
            pending = auth.get_pending_users()
            if not pending:
                print("No pending users")
            else:
                print("\nPending users:")
                for user in pending:
                    print(f"  - {user['email']} (created: {user['created_at']})")
        
        elif choice == "4":
            users = auth.get_all_users()
            if not users:
                print("No users found")
            else:
                print("\nAll users:")
                for user in users:
                    status = user.get('approval_status', 'unknown')
                    print(f"  - {user['email']} [{status}]")
        
        elif choice == "5":
            email = input("Email to approve: ").strip()
            user = auth.get_user_by_email(email)
            if not user:
                print(f"❌ User not found: {email}")
            else:
                if auth.approve_user(user['user_id'], "admin_setup"):
                    print(f"✅ Approved: {email}")
                else:
                    print("❌ Failed to approve user")
        
        elif choice == "6":
            print("Goodbye!")
            break
        
        else:
            print("Invalid choice")


if __name__ == "__main__":
    main()

