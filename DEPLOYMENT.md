# Cloud Deployment Guide

## Option 1: Streamlit Cloud (Recommended - Easiest & Free)

Streamlit Cloud is the easiest way to deploy Streamlit apps. It has a free tier and is specifically designed for Streamlit applications.

### Prerequisites

1. **GitHub Repository**: Your code must be in a GitHub repository
   - ✅ Already done: https://github.com/motoshri/requirements-extractor

2. **Streamlit Cloud Account**: Sign up at https://streamlit.io/cloud

### Deployment Steps

#### Step 1: Sign Up for Streamlit Cloud

1. Go to: https://streamlit.io/cloud
2. Click "Get started" or "Sign up"
3. Sign in with your GitHub account
4. Authorize Streamlit Cloud to access your repositories

#### Step 2: Deploy Your App

1. In Streamlit Cloud dashboard, click **"New app"**
2. Select your repository: `motoshri/requirements-extractor`
3. Select branch: `main` (or your default branch)
4. Main file path: `app.py`
5. App URL: Choose a custom subdomain (e.g., `requirements-extractor`)
6. Click **"Deploy"**

#### Step 3: Configure Secrets (API Keys)

1. In your app settings, go to **"Secrets"** tab
2. Add your OpenAI API key (if using OpenAI):

```toml
OPENAI_API_KEY = "sk-your-actual-key-here"
```

3. Save secrets

#### Step 4: Access Your App

Your app will be available at:
```
https://requirements-extractor.streamlit.app
```
(Or your custom subdomain)

### Streamlit Cloud Limitations

- **File Upload**: Max 200MB per file (free tier)
- **Memory**: 1GB RAM (free tier)
- **CPU**: Shared resources
- **Storage**: Ephemeral (files deleted after session)
- **Uptime**: May sleep after inactivity (free tier)

### Updating Your App

Simply push to GitHub - Streamlit Cloud auto-deploys:
```bash
git add .
git commit -m "Update app"
git push
```

---

## Option 2: Heroku

### Prerequisites

1. Heroku account: https://heroku.com
2. Heroku CLI installed

### Deployment Steps

1. **Create Procfile**:
```
web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

2. **Create runtime.txt** (if needed):
```
python-3.11.0
```

3. **Deploy**:
```bash
heroku create your-app-name
heroku config:set OPENAI_API_KEY=your-key-here
git push heroku main
```

---

## Option 3: AWS (EC2 or Elastic Beanstalk)

### Using EC2

1. Launch EC2 instance (Ubuntu)
2. Install dependencies
3. Run with systemd or screen
4. Configure security groups for port 8501

### Using Elastic Beanstalk

1. Create Python environment
2. Deploy application
3. Configure environment variables

---

## Option 4: Google Cloud Platform

### Using Cloud Run

1. Create Dockerfile
2. Build container
3. Deploy to Cloud Run
4. Configure environment variables

---

## Option 5: Railway

1. Sign up at https://railway.app
2. Connect GitHub repository
3. Deploy automatically
4. Set environment variables

---

## Option 6: Render

1. Sign up at https://render.com
2. Create new Web Service
3. Connect GitHub repository
4. Set build command and start command
5. Configure environment variables

---

## Environment Variables to Set

For cloud deployment, set these environment variables:

- `OPENAI_API_KEY`: Your OpenAI API key (if using OpenAI)
- `STREAMLIT_SERVER_PORT`: Port (usually auto-set by platform)
- `STREAMLIT_SERVER_ADDRESS`: `0.0.0.0` (to accept external connections)

---

## Important Notes for Cloud Deployment

### 1. File Size Limits

Cloud platforms have file size limits:
- **Streamlit Cloud**: 200MB max
- **Heroku**: 100MB max
- **AWS/GCP**: Varies by plan

For larger files, consider:
- Client-side processing
- Chunking files
- Using cloud storage (S3, GCS)

### 2. Local Whisper

Local Whisper (openai-whisper) requires significant resources:
- **Not recommended** for free cloud tiers
- Use OpenAI Whisper API instead for cloud deployment
- Or upgrade to paid tier with more resources

### 3. Ollama

Ollama requires local installation:
- **Not available** on most cloud platforms
- Use OpenAI API for cloud deployment
- Or deploy on VM with Ollama installed

### 4. Temporary Files

Cloud platforms use ephemeral storage:
- Files are deleted after session ends
- No persistent storage on free tiers
- Consider cloud storage for file persistence

### 5. API Keys Security

- **Never commit** API keys to GitHub
- Use platform's secrets management
- Streamlit Cloud: Use Secrets tab
- Heroku: Use `heroku config:set`
- AWS: Use Parameter Store or Secrets Manager

---

## Recommended Setup for Cloud

### For Streamlit Cloud (Free Tier)

1. Use **OpenAI Whisper API** for transcription (not local Whisper)
2. Use **OpenAI GPT** for requirements extraction (not Ollama)
3. Set file upload limit to 200MB
4. Configure API keys in Secrets tab

### For Paid Cloud Services

1. Can use local Whisper with sufficient resources
2. Can install Ollama on VM-based services
3. Higher file size limits
4. Better performance

---

## Quick Start: Streamlit Cloud

1. ✅ Code is in GitHub: `motoshri/requirements-extractor`
2. Go to: https://streamlit.io/cloud
3. Sign in with GitHub
4. Click "New app"
5. Select repository and branch
6. Deploy!
7. Add API keys in Secrets tab

Your app will be live in minutes!

---

## Troubleshooting

### App won't start
- Check requirements.txt is complete
- Verify app.py is the main file
- Check logs in Streamlit Cloud dashboard

### API key errors
- Verify secrets are set correctly
- Check environment variable names match code

### File upload issues
- Check file size limits
- Verify maxUploadSize in config.toml

### Memory errors
- Reduce file sizes
- Use API-based processing instead of local
- Upgrade to paid tier

---

## Next Steps

1. Choose your deployment platform
2. Follow platform-specific steps above
3. Configure secrets/environment variables
4. Test your deployed app
5. Share the URL with your team!



