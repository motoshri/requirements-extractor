# Fix GitHub Authentication Error

## Problem
```
remote: Invalid username or token. Password authentication is not supported for Git operations.
fatal: Authentication failed
```

GitHub no longer accepts passwords for HTTPS. You need a **Personal Access Token (PAT)**.

## Solution: Use Personal Access Token

### Step 1: Generate a Personal Access Token

1. Go to: https://github.com/settings/tokens
2. Click **"Generate new token"** → **"Generate new token (classic)"**
3. Give it a name: `Requirements Extractor`
4. Select expiration: Choose how long it should be valid (90 days, 1 year, or no expiration)
5. **Select scopes**: Check `repo` (this gives full repository access)
6. Click **"Generate token"**
7. **IMPORTANT**: Copy the token immediately - you won't see it again!
   - It looks like: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

### Step 2: Use Token Instead of Password

When you push to GitHub, use:
- **Username**: Your GitHub username
- **Password**: The Personal Access Token (not your GitHub password)

### Step 3: Push Again

```bash
cd /Users/Shrikant/Requirements_from_calls
git push -u origin main
```

When prompted:
- Username: `your-github-username`
- Password: `ghp_your_token_here` (paste the token)

---

## Alternative: Use SSH (No Token Needed)

If you prefer SSH authentication:

### Step 1: Check if you have SSH keys

```bash
ls -la ~/.ssh
```

Look for `id_rsa.pub` or `id_ed25519.pub`

### Step 2: Generate SSH key (if you don't have one)

```bash
ssh-keygen -t ed25519 -C "your.email@example.com"
```

Press Enter to accept default location. Optionally set a passphrase.

### Step 3: Add SSH key to GitHub

1. Copy your public key:
   ```bash
   cat ~/.ssh/id_ed25519.pub
   ```
   (or `cat ~/.ssh/id_rsa.pub` if you used RSA)

2. Go to: https://github.com/settings/keys
3. Click **"New SSH key"**
4. Title: `My Mac` (or any name)
5. Key: Paste the public key content
6. Click **"Add SSH key"**

### Step 4: Change remote URL to SSH

```bash
cd /Users/Shrikant/Requirements_from_calls
git remote set-url origin git@github.com:YOUR_USERNAME/repo-name.git
git push -u origin main
```

---

## Quick Fix (Recommended: Use Token)

1. Generate token: https://github.com/settings/tokens
2. Copy the token (starts with `ghp_`)
3. When pushing, use token as password
4. Or store it in credential helper:

```bash
# Store token in macOS Keychain (one time setup)
git config --global credential.helper osxkeychain

# Then push - it will ask once and remember
git push -u origin main
```

Enter your token when prompted, and macOS will remember it.

---

## Verify Your Remote URL

Check your current remote:

```bash
git remote -v
```

If it shows HTTPS, you need a token. If it shows SSH (git@github.com), you need SSH keys.


