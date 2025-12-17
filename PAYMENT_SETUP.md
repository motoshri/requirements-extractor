# 💳 Payment Gateway Setup Guide

## Overview

ReqIQ now supports Stripe payment gateway with region-based currency conversion. Users can purchase Pro and Enterprise subscriptions directly through the app.

## Features

✅ **Stripe Integration** - Secure payment processing  
✅ **Region Detection** - Automatic currency conversion  
✅ **Multi-Currency Support** - Shows prices in local currency (INR, USD, EUR, GBP, etc.)  
✅ **Subscription Management** - Automatic subscription activation after payment  

## Setup Instructions

### 1. Create Stripe Account

1. Go to https://stripe.com
2. Sign up for a free account
3. Complete account verification

### 2. Get API Keys

1. Go to Stripe Dashboard → Developers → API keys
2. Copy your **Publishable key** (starts with `pk_`)
3. Copy your **Secret key** (starts with `sk_`)

**Important:** Use test keys for development, live keys for production.

### 3. Configure Environment Variables

#### Option A: Environment Variables (Recommended)

```bash
export STRIPE_SECRET_KEY="sk_test_your_secret_key_here"
export STRIPE_PUBLISHABLE_KEY="pk_test_your_publishable_key_here"
```

#### Option B: Streamlit Secrets (for Cloud Deployment)

Create `.streamlit/secrets.toml`:

```toml
stripe_secret_key = "sk_test_your_secret_key_here"
stripe_publishable_key = "pk_test_your_publishable_key_here"
```

#### Option C: Local Config File

The app will automatically use environment variables if set.

### 4. Test Payment Flow

1. Start the app: `streamlit run app.py`
2. You'll see the subscription page
3. Click "Subscribe to Pro" or "Subscribe to Enterprise"
4. You'll be redirected to Stripe Checkout
5. Use Stripe test card: `4242 4242 4242 4242`
6. Complete payment
7. You'll be redirected back with active subscription

## Currency Support

### Supported Regions & Currencies

- **India (IN)**: ₹ INR
- **United States (US)**: $ USD
- **United Kingdom (GB)**: £ GBP
- **Canada (CA)**: C$ CAD
- **Australia (AU)**: A$ AUD
- **Japan (JP)**: ¥ JPY
- **China (CN)**: ¥ CNY
- **Singapore (SG)**: S$ SGD
- **UAE (AE)**: د.إ AED
- **European Union**: € EUR (DE, FR, IT, ES, NL, BE, AT, PT, IE, FI, GR)

### Currency Conversion

- Base prices are in USD
- Automatic conversion to local currency
- Exchange rates are approximate (update regularly in production)
- For production, integrate with a real currency API

## Pricing

### Current Pricing (USD)

- **Free**: $0/month
- **Pro**: $9.99/month
- **Enterprise**: $49.99/month

### Example Conversions

- **India**: Pro = ₹829/month, Enterprise = ₹4,147/month
- **UK**: Pro = £7.89/month, Enterprise = £39.49/month
- **EU**: Pro = €9.19/month, Enterprise = €45.99/month

## Testing

### Stripe Test Cards

- **Success**: `4242 4242 4242 4242`
- **Decline**: `4000 0000 0000 0002`
- **3D Secure**: `4000 0025 0000 3155`

Use any future expiry date and any 3-digit CVC.

### Test Mode

1. Use test API keys (start with `sk_test_` and `pk_test_`)
2. No real charges will be made
3. Test cards work in test mode only

## Production Deployment

### 1. Switch to Live Keys

Replace test keys with live keys:
- `sk_live_...` (Secret key)
- `pk_live_...` (Publishable key)

### 2. Update Currency Rates

In `payment_gateway.py`, update `CURRENCY_RATES` with current exchange rates or integrate with a currency API:

```python
# Option 1: Use exchangerate-api.com (free tier available)
import requests
response = requests.get('https://api.exchangerate-api.com/v4/latest/USD')
rates = response.json()['rates']
```

### 3. Webhook Setup (Optional but Recommended)

For production, set up Stripe webhooks to handle:
- Payment success
- Payment failure
- Subscription cancellation
- Subscription renewal

Webhook endpoint: `https://your-domain.com/stripe-webhook`

## Troubleshooting

### Payment button not showing

- Check if Stripe keys are set in environment variables
- Verify `stripe` package is installed: `pip install stripe`
- Check console for errors

### Currency not converting

- Verify region detection is working
- Check `CURRENCY_RATES` dictionary in `payment_gateway.py`
- Update exchange rates if outdated

### Payment succeeds but subscription not activated

- Check database connection
- Verify payment verification logic
- Check logs for errors

### Redirect not working

- Verify `success_url` and `cancel_url` are correct
- Check if app URL is accessible
- Ensure query parameters are preserved

## Security Notes

⚠️ **Never commit API keys to Git**  
⚠️ **Use environment variables or secrets management**  
⚠️ **Rotate keys regularly**  
⚠️ **Use HTTPS in production**  
⚠️ **Verify payments server-side (webhooks recommended)**

## Support

For payment issues:
1. Check Stripe Dashboard → Payments
2. Verify API keys are correct
3. Check app logs for errors
4. Contact Stripe support if needed

## Next Steps

1. ✅ Set up Stripe account
2. ✅ Add API keys to environment
3. ✅ Test payment flow
4. ✅ Update currency rates (production)
5. ✅ Set up webhooks (production)
6. ✅ Switch to live keys (production)



