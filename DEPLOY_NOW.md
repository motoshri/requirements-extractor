# 🚀 Deploy ReqIQ to Cloud - Quick Guide

## Your Deployment Options

| Platform | Difficulty | Cost | Best For |
|----------|------------|------|----------|
| **Streamlit Cloud** | ⭐ Easy | Free tier | Quick sharing, demos |
| **Railway** | ⭐⭐ Easy | Free tier | Simple production |
| **Render** | ⭐⭐ Easy | Free tier | Docker apps |
| **Google Cloud Run** | ⭐⭐⭐ Medium | Pay-per-use | Scalable production |
| **AWS ECS** | ⭐⭐⭐⭐ Hard | Variable | Enterprise |

---

## 🌟 RECOMMENDED: Streamlit Cloud (Easiest & Free)

### Step 1: Push Code to GitHub

```bash
cd /Users/Shrikant/Requirements_from_calls

# Initialize git if not already done
git init

# Add all files
git add .

# Commit
git commit -m "Ready for cloud deployment"

# Create repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/reqiq.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy to Streamlit Cloud

1. **Go to:** https://share.streamlit.io/
2. **Sign in** with GitHub
3. **Click:** "New app"
4. **Configure:**
   - Repository: `YOUR_USERNAME/reqiq`
   - Branch: `main`
   - Main file path: `app.py`
5. **Click:** "Deploy!"

### Step 3: Add Secrets (Optional)

In Streamlit Cloud dashboard → Settings → Secrets:

```toml
openai_api_key = "sk-your-openai-key"

# For email approval system (optional)
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = "587"
SMTP_USER = "your-email@gmail.com"
SMTP_PASSWORD = "your-app-password"
ADMIN_EMAIL = "admin@yourcompany.com"
```

### Step 4: Share Your App!

Your app will be live at:
```
https://your-app-name.streamlit.app
```

---

## 🚂 Alternative: Railway (Easy, Free Tier)

### Step 1: Create Railway Account
Go to https://railway.app and sign up with GitHub

### Step 2: Deploy from GitHub
1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Choose your repository
4. Railway auto-detects Dockerfile

### Step 3: Add Environment Variables
In Railway dashboard → Variables:
```
OPENAI_API_KEY=sk-your-key
PORT=8501
```

### Step 4: Get Your URL
Railway provides a public URL automatically.

---

## 🎨 Alternative: Render (Easy, Free Tier)

### Step 1: Create Render Account
Go to https://render.com and sign up

### Step 2: Create Web Service
1. Click "New +" → "Web Service"
2. Connect your GitHub repository
3. Configure:
   - Environment: Docker
   - Instance Type: Free

### Step 3: Add Environment Variables
```
OPENAI_API_KEY=sk-your-key
```

### Step 4: Deploy
Click "Create Web Service" - Render will build and deploy.

---

## 🐳 Docker Deployment (Any Cloud)

### Already Configured!

Your app has:
- ✅ `Dockerfile` - Ready to build
- ✅ `docker-compose.yml` - Ready to run
- ✅ `requirements.txt` - All dependencies

### Local Docker Test

```bash
cd /Users/Shrikant/Requirements_from_calls

# Build the image
docker build -t reqiq:latest .

# Run the container
docker run -d \
  -p 8501:8501 \
  -e OPENAI_API_KEY=sk-your-key \
  --name reqiq \
  reqiq:latest

# Access at http://localhost:8501
```

### Using Docker Compose

```bash
# Create .env file with your keys
echo "OPENAI_API_KEY=sk-your-key" > .env

# Start the app
docker compose up -d

# View logs
docker compose logs -f
```

---

## ☁️ Google Cloud Run

```bash
# Install gcloud CLI first, then:
cd /Users/Shrikant/Requirements_from_calls

# Deploy to Cloud Run
gcloud run deploy reqiq \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars OPENAI_API_KEY=sk-your-key \
  --memory 2Gi \
  --timeout 300
```

---

## ⚠️ Before Deploying - Important Notes

### 1. API Keys
- **Never commit API keys to GitHub**
- Use environment variables or secrets
- Set up secrets in your cloud platform

### 2. Local Whisper Won't Work on Streamlit Cloud
- Streamlit Cloud has limited resources
- Use OpenAI Whisper API for transcription
- Or use Docker deployment for local Whisper

### 3. Database
- SQLite works but is ephemeral on some platforms
- For production, consider PostgreSQL
- Streamlit Cloud resets database on each deployment

### 4. File Storage
- Uploaded files are temporary
- For permanent storage, consider S3 or similar

---

## 📋 Pre-Deployment Checklist

- [ ] Code pushed to GitHub
- [ ] OpenAI API key ready (if using)
- [ ] Email credentials ready (for approval system)
- [ ] Admin email set for approvals
- [ ] Tested locally with `docker compose up`

---

## 🎯 Quick Decision Guide

**Just want to share with team quickly?**
→ Use **Streamlit Cloud** (free, 5 minutes)

**Need more control and persistence?**
→ Use **Railway** or **Render** (free tier, Docker support)

**Enterprise/Production deployment?**
→ Use **Google Cloud Run** or **AWS ECS** (scalable, pay-per-use)

**Want to run locally for multiple users?**
→ Use **Docker Compose** on a server with a public IP

---

## 🆘 Need Help?

1. **Streamlit Cloud docs:** https://docs.streamlit.io/streamlit-community-cloud
2. **Railway docs:** https://docs.railway.app/
3. **Render docs:** https://render.com/docs
4. **Docker docs:** https://docs.docker.com/

---

## 🚀 Ready to Deploy?

**Fastest option:** Streamlit Cloud
1. Push to GitHub
2. Go to https://share.streamlit.io/
3. Click "New app"
4. Select your repo
5. Deploy!

Your app will be live in ~5 minutes.

