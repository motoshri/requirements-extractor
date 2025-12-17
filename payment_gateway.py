#!/usr/bin/env python3
"""
Payment Gateway Integration for ReqIQ
Supports Stripe with region-based currency conversion.
"""

import os
import json
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
import requests

# Currency conversion rates (updated periodically)
# In production, use a real currency API like exchangerate-api.com
CURRENCY_RATES = {
    'USD': 1.0,
    'INR': 83.0,  # Approximate rate, update regularly
    'EUR': 0.92,
    'GBP': 0.79,
    'CAD': 1.35,
    'AUD': 1.52,
    'JPY': 149.0,
    'CNY': 7.2,
    'SGD': 1.34,
    'AED': 3.67,
}

# Region to currency mapping
REGION_CURRENCY = {
    'IN': 'INR',
    'US': 'USD',
    'GB': 'GBP',
    'CA': 'CAD',
    'AU': 'AUD',
    'JP': 'JPY',
    'CN': 'CNY',
    'SG': 'SGD',
    'AE': 'AED',
    'DE': 'EUR',
    'FR': 'EUR',
    'IT': 'EUR',
    'ES': 'EUR',
    'NL': 'EUR',
    'BE': 'EUR',
    'AT': 'EUR',
    'PT': 'EUR',
    'IE': 'EUR',
    'FI': 'EUR',
    'GR': 'EUR',
}

# Currency symbols
CURRENCY_SYMBOLS = {
    'USD': '$',
    'INR': '₹',
    'EUR': '€',
    'GBP': '£',
    'CAD': 'C$',
    'AUD': 'A$',
    'JPY': '¥',
    'CNY': '¥',
    'SGD': 'S$',
    'AED': 'د.إ',
}


class PaymentGateway:
    """Handle payment processing with Stripe."""
    
    def __init__(self, stripe_secret_key: Optional[str] = None):
        self.stripe_secret_key = stripe_secret_key or os.getenv('STRIPE_SECRET_KEY')
        self.stripe_publishable_key = os.getenv('STRIPE_PUBLISHABLE_KEY', '')
        
        if self.stripe_secret_key:
            try:
                import stripe
                stripe.api_key = self.stripe_secret_key
                self.stripe = stripe
                self.available = True
            except ImportError:
                self.available = False
                print("Warning: Stripe not installed. Install with: pip install stripe")
        else:
            self.available = False
    
    def detect_region(self) -> str:
        """Detect user's region based on IP or browser settings."""
        # Try to get from environment (can be set by reverse proxy/CDN)
        region = os.getenv('USER_REGION', '')
        if region:
            return region.upper()
        
        # Default to US if not detected
        # In production, use a geolocation service
        return 'US'
    
    def get_currency_for_region(self, region: str) -> str:
        """Get currency code for a region."""
        return REGION_CURRENCY.get(region.upper(), 'USD')
    
    def convert_price(self, usd_price: float, target_currency: str) -> float:
        """Convert USD price to target currency."""
        if target_currency == 'USD':
            return usd_price
        
        rate = CURRENCY_RATES.get(target_currency, 1.0)
        converted = usd_price * rate
        
        # Round to 2 decimal places (or 0 for JPY)
        if target_currency == 'JPY':
            return round(converted, 0)
        return round(converted, 2)
    
    def format_price(self, amount: float, currency: str) -> str:
        """Format price with currency symbol."""
        symbol = CURRENCY_SYMBOLS.get(currency, currency)
        
        if currency == 'JPY':
            return f"{symbol}{int(amount):,}"
        return f"{symbol}{amount:,.2f}"
    
    def create_checkout_session(
        self,
        tier: str,
        user_id: str,
        currency: str = 'USD',
        success_url: str = None,
        cancel_url: str = None
    ) -> Optional[Dict]:
        """Create Stripe checkout session."""
        if not self.available:
            return None
        
        # Pricing in USD
        usd_prices = {
            'pro': 9.99,
            'enterprise': 49.99,
        }
        
        if tier not in usd_prices:
            return None
        
        usd_price = usd_prices[tier]
        local_price = self.convert_price(usd_price, currency)
        
        # Convert to cents (or smallest unit)
        if currency == 'JPY':
            amount = int(local_price)
        else:
            amount = int(local_price * 100)
        
        try:
            session = self.stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': currency.lower(),
                        'product_data': {
                            'name': f'ReqIQ {tier.capitalize()} Subscription',
                            'description': f'Monthly subscription for {tier} tier',
                        },
                        'unit_amount': amount,
                        'recurring': {
                            'interval': 'month',
                        },
                    },
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=success_url or f'http://localhost:8501/?payment=success&tier={tier}&session_id={session.id}',
                cancel_url=cancel_url or f'http://localhost:8501/?payment=cancelled',
                metadata={
                    'user_id': user_id,
                    'tier': tier,
                },
                client_reference_id=user_id,
            )
            
            return {
                'session_id': session.id,
                'url': session.url,
                'amount': local_price,
                'currency': currency,
            }
        except Exception as e:
            print(f"Error creating Stripe session: {e}")
            return None
    
    def verify_payment(self, session_id: str) -> Optional[Dict]:
        """Verify payment was successful."""
        if not self.available:
            return None
        
        try:
            session = self.stripe.checkout.Session.retrieve(session_id)
            
            if session.payment_status == 'paid':
                return {
                    'success': True,
                    'tier': session.metadata.get('tier'),
                    'user_id': session.metadata.get('user_id'),
                    'amount_paid': session.amount_total / 100,
                    'currency': session.currency.upper(),
                }
            return None
        except Exception as e:
            print(f"Error verifying payment: {e}")
            return None


def get_user_region() -> str:
    """Get user's region (simplified - in production use geolocation)."""
    # Try to detect from browser (if available in Streamlit)
    # For now, default to US
    return os.getenv('USER_REGION', 'US')


def get_currency_info(region: str = None) -> Dict:
    """Get currency information for a region."""
    if not region:
        region = get_user_region()
    
    currency = REGION_CURRENCY.get(region.upper(), 'USD')
    symbol = CURRENCY_SYMBOLS.get(currency, currency)
    
    return {
        'region': region,
        'currency': currency,
        'symbol': symbol,
    }

