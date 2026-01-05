# Supabase Connection Guide for Streamlit Cloud

## ⚠️ Issue: Direct Connection Fails on Streamlit Cloud

Streamlit Cloud has network restrictions that prevent direct PostgreSQL connections.

## ✅ Solution: Use Connection Pooling

Supabase provides **Connection Pooling** URLs that work with serverless platforms.

---

## 🔧 How to Get Connection Pooling URL

### Step 1: Go to Supabase Dashboard
1. Open: https://supabase.com/dashboard
2. Click your project
3. Click **⚙️ Settings** → **Database**

### Step 2: Get Connection Pooling String
1. Scroll to **"Connection string"** section
2. Click **"Connection pooling"** tab (NOT "URI")
3. Select **"Session mode"** (or "Transaction mode")
4. Copy the connection string

It will look like:
```
postgresql://postgres.cpoggomvbfejvqclyfpi:[YOUR-PASSWORD]@aws-0-us-east-1.pooler.supabase.com:6543/postgres
```

Or:
```
postgresql://postgres.cpoggomvbfejvqclyfpi:[YOUR-PASSWORD]@db.cpoggomvbfejvqclyfpi.supabase.co:6543/postgres?pgbouncer=true
```

**Key differences:**
- Port is **6543** (not 5432)
- Uses `.pooler.` or `?pgbouncer=true`
- Works with serverless platforms

---

## 📋 Update Streamlit Secrets

In Streamlit Cloud → Settings → Secrets:

```toml
DATABASE_URL = "postgresql://postgres.cpoggomvbfejvqclyfpi:YOUR_PASSWORD@aws-0-us-east-1.pooler.supabase.com:6543/postgres"
```

**Replace:**
- `YOUR_PASSWORD` with your actual password
- The host/port with what Supabase shows you

---

## 🔄 Alternative: Use SQLite (No Setup)

If connection pooling doesn't work, the app will automatically fall back to SQLite (in-memory, resets on reboot).

To disable PostgreSQL and use SQLite only, remove or comment out:
```toml
# DATABASE_URL = "..."
```

---

## 🆘 Still Having Issues?

1. **Check Connection Pooling tab** - Make sure you're using the pooling URL, not direct
2. **Try Session mode** - Usually works better than Transaction mode
3. **Fall back to SQLite** - Remove DATABASE_URL to use SQLite (data won't persist but app will work)

