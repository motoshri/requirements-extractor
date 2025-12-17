# Fix 403 Error: Write Access Not Granted

## Error Message
```
remote: Write access to repository not granted.
fatal: unable to access 'https://github.com/motoshri/requirements-extractor.git/': The requested URL returned error: 403
```

## Common Causes & Solutions

### 1. Token Doesn't Have `repo` Scope

**Problem**: Your Personal Access Token doesn't have repository write permissions.

**Solution**:
1. Go to: https://github.com/settings/tokens
2. Find your token (or create a new one)
3. Make sure **`repo`** scope is checked
4. If you created a new token, use the new one

### 2. Repository Doesn't Exist

**Problem**: The repository `motoshri/requirements-extractor` doesn't exist on GitHub.

**Solution**: Create the repository first:
1. Go to: https://github.com/new
2. Repository name: `requirements-extractor`
3. Owner: `motoshri` (your username)
4. Choose Private or Public
5. **DO NOT** initialize with README
6. Click "Create repository"

### 3. Wrong Repository Name or Owner

**Problem**: Repository name or owner doesn't match.

**Check**:
```bash
git remote -v
```

Should show: `https://github.com/motoshri/requirements-extractor.git`

If wrong, fix it:
```bash
git remote set-url origin https://github.com/motoshri/requirements-extractor.git
```

### 4. Token Expired or Revoked

**Problem**: Your token is no longer valid.

**Solution**: Generate a new token:
1. Go to: https://github.com/settings/tokens
2. Generate new token (classic)
3. Check `repo` scope
4. Copy the new token
5. Use it when pushing

### 5. Using Wrong Credentials

**Problem**: macOS Keychain might have old credentials stored.

**Solution**: Clear stored credentials:
```bash
# Remove old credentials from Keychain
git credential-osxkeychain erase
host=github.com
protocol=https
[Press Enter twice]

# Or use credential helper to update
git config --global credential.helper osxkeychain
```

Then try pushing again - it will ask for new credentials.

---

## Step-by-Step Fix

### Step 1: Verify Repository Exists

1. Go to: https://github.com/motoshri/requirements-extractor
2. If you see "404 Not Found", create the repository:
   - Go to: https://github.com/new
   - Name: `requirements-extractor`
   - Don't initialize with README
   - Create it

### Step 2: Generate/Verify Token

1. Go to: https://github.com/settings/tokens
2. If you have a token, check it has `repo` scope
3. If not, create new token:
   - Name: `Requirements Extractor`
   - Expiration: Your choice
   - **Scopes**: Check `repo` (full control of private repositories)
   - Generate and copy token

### Step 3: Update Remote URL (if needed)

```bash
cd /Users/Shrikant/Requirements_from_calls
git remote set-url origin https://github.com/motoshri/requirements-extractor.git
```

### Step 4: Clear Old Credentials

```bash
# Remove from Keychain
git credential reject <<EOF
protocol=https
host=github.com
EOF
```

### Step 5: Push with New Token

```bash
git push -u origin main
```

When prompted:
- **Username**: `motoshri`
- **Password**: Paste your Personal Access Token (starts with `ghp_`)

---

## Alternative: Use SSH Instead

If tokens keep causing issues, switch to SSH:

### Step 1: Check for SSH Key

```bash
ls -la ~/.ssh/id_*.pub
```

### Step 2: Generate SSH Key (if needed)

```bash
ssh-keygen -t ed25519 -C "your.email@example.com"
# Press Enter to accept defaults
```

### Step 3: Add to GitHub

```bash
# Copy public key
cat ~/.ssh/id_ed25519.pub
# Copy the output
```

1. Go to: https://github.com/settings/keys
2. Click "New SSH key"
3. Paste the key
4. Save

### Step 4: Change to SSH URL

```bash
git remote set-url origin git@github.com:motoshri/requirements-extractor.git
git push -u origin main
```

---

## Quick Test

Test if your token works:

```bash
# Replace YOUR_TOKEN with your actual token
curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/user
```

If you see your user info, token works. If you see an error, token is invalid.

---

## Still Having Issues?

1. **Check repository exists**: https://github.com/motoshri/requirements-extractor
2. **Verify token has repo scope**: https://github.com/settings/tokens
3. **Try SSH instead**: Often more reliable
4. **Check repository is not archived**: Can't push to archived repos


