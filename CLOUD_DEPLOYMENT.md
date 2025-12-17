# ☁️ Cloud Deployment Guide for ReqIQ

This guide covers deploying ReqIQ to make it publicly accessible.

## 🚀 Option 1: Streamlit Cloud (Recommended - Easiest)

### Prerequisites
1. GitHub account
2. Code pushed to GitHub repository
3. Streamlit Cloud account (free): https://streamlit.io/cloud

### Steps

1. **Push code to GitHub** (already done ✅)

2. **Deploy to Streamlit Cloud:**
   - Go to https://share.streamlit.io/
   - Click "New app"
   - Connect your GitHub repository
   - Select branch: `main` (or `master`)
   - Main file path: `app.py`
   - Click "Deploy"

3. **Configure Secrets:**
   - In Streamlit Cloud dashboard, go to "Settings" → "Secrets"
   - Add your secrets in TOML format:
   ```toml
   openai_api_key = "sk-your-key-here"
   ```

4. **Environment Variables (Optional):**
   - In Streamlit Cloud settings, you can also set environment variables
   - `OPENAI_API_KEY=sk-your-key-here`

5. **Access your app:**
   - Your app will be available at: `https://your-app-name.streamlit.app`

### Streamlit Cloud Configuration

Create `.streamlit/config.toml` in your repo:
```toml
[server]
maxUploadSize = 1073741824  # 1GB
maxMessageSize = 1073741824

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f8f9fa"
textColor = "#000000"
```

## 🐳 Option 2: Docker Deployment

### Create Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Build and Run

```bash
# Build image
docker build -t reqiq:latest .

# Run container
docker run -d \
  -p 8501:8501 \
  -e OPENAI_API_KEY=sk-your-key \
  --name reqiq \
  reqiq:latest
```

### Docker Compose

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  reqiq:
    build: .
    ports:
      - "8501:8501"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./data:/app/data
    restart: unless-stopped
```

## ☁️ Option 3: Cloud Platforms

### AWS (EC2 / ECS / Elastic Beanstalk)

1. **EC2 Instance:**
   ```bash
   # SSH into EC2
   git clone https://github.com/your-username/requirements-extractor.git
   cd requirements-extractor
   pip install -r requirements.txt
   streamlit run app.py --server.port=8501 --server.address=0.0.0.0
   ```

2. **Use Nginx as reverse proxy:**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://localhost:8501;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "upgrade";
           proxy_set_header Host $host;
       }
   }
   ```

### Google Cloud Platform (Cloud Run)

1. **Create `Dockerfile`** (see Option 2)

2. **Deploy:**
   ```bash
   gcloud run deploy reqiq \
     --source . \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars OPENAI_API_KEY=sk-your-key
   ```

### Azure (App Service / Container Instances)

1. **Create `Dockerfile`** (see Option 2)

2. **Deploy via Azure CLI:**
   ```bash
   az container create \
     --resource-group myResourceGroup \
     --name reqiq \
     --image reqiq:latest \
     --dns-name-label reqiq-app \
     --ports 8501 \
     --environment-variables OPENAI_API_KEY=sk-your-key
   ```

### Heroku

1. **Create `Procfile`:**
   ```
   web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
   ```

2. **Deploy:**
   ```bash
   heroku create reqiq-app
   heroku config:set OPENAI_API_KEY=sk-your-key
   git push heroku main
   ```

## 🔒 Security Considerations for Cloud Deployment

1. **API Keys:**
   - Never commit API keys to Git
   - Use environment variables or secrets management
   - Rotate keys regularly

2. **HTTPS:**
   - Always use HTTPS in production
   - Set up SSL certificates (Let's Encrypt is free)

3. **Rate Limiting:**
   - Implement rate limiting (already included)
   - Monitor usage patterns

4. **Database:**
   - For production, use PostgreSQL instead of SQLite
   - Set up database backups

5. **File Storage:**
   - Consider using cloud storage (S3, GCS, Azure Blob) for uploaded files
   - Implement file size limits per subscription tier

6. **Authentication:**
   - Consider adding user authentication (OAuth, email/password)
   - Implement session management

## 📊 Database Setup for Cloud

### PostgreSQL (Recommended for Production)

Update `subscription_manager.py` to support PostgreSQL:

```python
import os
import psycopg2
from psycopg2.extras import RealDictCursor

# Use PostgreSQL if DATABASE_URL is set, otherwise SQLite
DATABASE_URL = os.getenv('DATABASE_URL')

if DATABASE_URL:
    # PostgreSQL connection
    conn = psycopg2.connect(DATABASE_URL)
else:
    # SQLite (local development)
    conn = sqlite3.connect(str(db_path))
```

Add to `requirements.txt`:
```
psycopg2-binary>=2.9.0
```

## 🎯 Quick Start: Streamlit Cloud

The fastest way to deploy:

1. **Ensure code is on GitHub** ✅
2. **Go to:** https://share.streamlit.io/
3. **Click:** "New app"
4. **Select:** Your repository
5. **Main file:** `app.py`
6. **Add secrets:** OpenAI API key (optional if using local models)
7. **Deploy!**

Your app will be live in minutes at: `https://your-app-name.streamlit.app`

## 🔧 Environment Variables for Cloud

Set these in your cloud platform:

```bash
OPENAI_API_KEY=sk-your-key-here  # Optional if using local models
DATABASE_URL=postgresql://...     # Optional, uses SQLite by default
ENVIRONMENT=production
```

## 📝 Post-Deployment Checklist

- [ ] Test subscription system
- [ ] Test coupon code redemption
- [ ] Verify file upload limits
- [ ] Check usage tracking
- [ ] Test PDF/Excel export
- [ ] Monitor error logs
- [ ] Set up monitoring/alerts
- [ ] Configure custom domain (optional)
- [ ] Set up SSL certificate
- [ ] Test rate limiting

## 🆘 Troubleshooting

### App not accessible
- Check firewall rules
- Verify port is exposed (8501)
- Check security groups (AWS) or network rules

### Database errors
- Ensure database is accessible
- Check connection strings
- Verify database migrations ran

### File upload issues
- Check `maxUploadSize` in config
- Verify file size limits match subscription tiers
- Check disk space on server

### API key errors
- Verify secrets are set correctly
- Check environment variables
- Ensure keys are not expired



