# GitHub Setup Instructions

## Step 1: Configure Git (if not already done)

Set your Git username and email (use your GitHub account details):

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

Or set it just for this repository:

```bash
cd /Users/Shrikant/Requirements_from_calls
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

## Step 2: Create Initial Commit

```bash
cd /Users/Shrikant/Requirements_from_calls
git commit -m "Initial commit: Requirements Extractor from Teams Meetings"
```

## Step 3: Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `requirements-extractor` (or any name you prefer)
3. Description: "Extract structured requirements from Teams meeting transcripts and videos"
4. Choose: **Private** (recommended) or **Public**
5. **DO NOT** initialize with README, .gitignore, or license (we already have these)
6. Click **"Create repository"**

## Step 4: Connect and Push to GitHub

After creating the repository, GitHub will show you commands. Use these:

```bash
cd /Users/Shrikant/Requirements_from_calls

# Rename branch to main (if needed)
git branch -M main

# Add your GitHub repository as remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/requirements-extractor.git

# Push to GitHub
git push -u origin main
```

**If you use SSH instead of HTTPS:**

```bash
git remote add origin git@github.com:YOUR_USERNAME/requirements-extractor.git
git push -u origin main
```

## Step 5: Verify

Check your GitHub repository - all files should be there!

## Troubleshooting

### Authentication Issues

If you get authentication errors:

1. **For HTTPS**: Use a Personal Access Token instead of password
   - Go to: https://github.com/settings/tokens
   - Generate new token (classic)
   - Select scopes: `repo`
   - Use token as password when pushing

2. **For SSH**: Set up SSH keys
   - Follow: https://docs.github.com/en/authentication/connecting-to-github-with-ssh

### Already have a repository?

If you want to push to an existing repository:

```bash
git remote set-url origin https://github.com/YOUR_USERNAME/REPO_NAME.git
git push -u origin main
```

---

**Note**: All commits will be under YOUR GitHub account, not mine. I'm just helping you set it up!


