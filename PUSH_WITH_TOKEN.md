# Push to GitHub Using Personal Access Token

## The Problem
"Write access to repository not granted" means your token either:
1. Doesn't have `repo` scope
2. Is being cached incorrectly
3. Needs to be used differently

## Solution: Use Token in URL (Temporary)

**Option 1: Embed token in URL (one-time push)**

```bash
cd /Users/Shrikant/Requirements_from_calls

# Replace YOUR_TOKEN with your actual token (starts with gph_)
git remote set-url origin https://YOUR_TOKEN@github.com/motoshri/requirements-extractor.git

# Push
git push -u origin main

# After successful push, remove token from URL for security
git remote set-url origin https://github.com/motoshri/requirements-extractor.git
```

**Option 2: Use credential helper properly**

```bash
cd /Users/Shrikant/Requirements_from_calls

# Clear old credentials
git credential reject <<EOF
protocol=https
host=github.com
EOF

# Try pushing - it will prompt for credentials
git push -u origin main
```

When prompted:
- **Username**: `motoshri`
- **Password**: Paste your Personal Access Token (NOT your GitHub password)

## Verify Your Token Has Correct Permissions

1. Go to: https://github.com/settings/tokens
2. Find your token (or create a new one)
3. **Must have these scopes checked**:
   - ✅ `repo` (Full control of private repositories)
   - This includes: `repo:status`, `repo_deployment`, `public_repo`, `repo:invite`

4. If your token doesn't have `repo` scope:
   - Create a new token
   - Check `repo` scope
   - Use the new token

## Alternative: Use SSH (More Reliable)

SSH is often more reliable than tokens:

### Step 1: Check for SSH Key
```bash
ls -la ~/.ssh/id_*.pub
```

### Step 2: Generate SSH Key (if needed)
```bash
ssh-keygen -t ed25519 -C "your.email@example.com"
# Press Enter 3 times (accept defaults, no passphrase)
```

### Step 3: Copy Public Key
```bash
cat ~/.ssh/id_ed25519.pub
# Copy the entire output
```

### Step 4: Add to GitHub
1. Go to: https://github.com/settings/keys
2. Click "New SSH key"
3. Title: `My Mac`
4. Key: Paste the copied key
5. Click "Add SSH key"

### Step 5: Change Remote to SSH
```bash
cd /Users/Shrikant/Requirements_from_calls
git remote set-url origin git@github.com:motoshri/requirements-extractor.git
git push -u origin main
```

No password/token needed with SSH!

## Quick Test: Verify Token Works

Test your token (replace YOUR_TOKEN):
```bash
curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/user
```

If you see your user info (JSON), token works. If you see an error, token is invalid.

## Still Not Working?

1. **Create a fresh token**: https://github.com/settings/tokens
   - Name: `Requirements Extractor`
   - Expiration: 90 days or 1 year
   - Scopes: Check **`repo`** (this is critical!)
   - Generate and copy immediately

2. **Verify repository exists**: https://github.com/motoshri/requirements-extractor
   - If 404, create it first

3. **Try SSH method** (often more reliable)


