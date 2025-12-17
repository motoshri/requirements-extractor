#!/usr/bin/env python3
"""
Script to create coupon codes for ReqIQ subscriptions.
Run this to generate free subscription coupon codes.
"""

import sys
from subscription_manager import SubscriptionManager, SUBSCRIPTION_TIERS
from datetime import datetime, timedelta

def create_coupon():
    """Create a coupon code interactively."""
    print("🎟️ ReqIQ Coupon Code Generator\n")
    print("Available tiers:")
    for tier, info in SUBSCRIPTION_TIERS.items():
        print(f"  - {tier}: {info['name']} (${info['price']}/month)")
    
    print("\n")
    code = input("Enter coupon code (or press Enter to generate): ").strip().upper()
    if not code:
        import secrets
        code = f"FREE{secrets.token_hex(4).upper()}"
        print(f"Generated code: {code}")
    
    print("\nAvailable tiers: free, pro, enterprise")
    tier = input("Enter tier (default: free): ").strip().lower() or "free"
    
    if tier not in SUBSCRIPTION_TIERS:
        print(f"❌ Invalid tier. Must be one of: {', '.join(SUBSCRIPTION_TIERS.keys())}")
        return False
    
    max_uses_input = input("Max uses (-1 for unlimited, default: 1): ").strip()
    max_uses = int(max_uses_input) if max_uses_input else 1
    
    days_valid_input = input("Days valid (default: 365): ").strip()
    days_valid = int(days_valid_input) if days_valid_input else 365
    valid_until = datetime.now() + timedelta(days=days_valid)
    
    manager = SubscriptionManager()
    success = manager.create_coupon_code(
        code=code,
        tier=tier,
        discount_percent=100,
        max_uses=max_uses,
        valid_until=valid_until
    )
    
    if success:
        print(f"\n✅ Coupon code created successfully!")
        print(f"   Code: {code}")
        print(f"   Tier: {tier}")
        print(f"   Max uses: {max_uses if max_uses > 0 else 'Unlimited'}")
        print(f"   Valid until: {valid_until.strftime('%Y-%m-%d')}")
        return True
    else:
        print(f"\n❌ Failed to create coupon code. It may already exist.")
        return False

if __name__ == "__main__":
    try:
        create_coupon()
    except KeyboardInterrupt:
        print("\n\nCancelled.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)



