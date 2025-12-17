# API Key Automation & Deployment Guide

## 📋 Table of Contents
1. [API Key Automation](#api-key-automation)
2. [Sharing & Deployment Options](#sharing--deployment-options)
3. [Implementation Details](#implementation-details)

---

## 🔑 API Key Automation

### Option 1: Environment Variables (Recommended for Local Use)
**Best for:** Personal use, development, local deployment

**How it works:**
- Set the API key as an environment variable
- The app automatically reads it on startup
- No need to enter it in the UI

**Setup:**
```bash
# macOS/Linux
export OPENAI_API_KEY="sk-your-api-key-here"

# Windows (PowerShell)
$env:OPENAI_API_KEY="sk-your-api-key-here"

# Windows (CMD)
set OPENAI_API_KEY=sk-your-api-key-here

# Make it permanent (macOS/Linux - add to ~/.zshrc or ~/.bashrc)
echo 'export OPENAI_API_KEY="sk-your-api-key-here"' >> ~/.zshrc
source ~/.zshrc
```

**Pros:**
- ✅ Secure (not stored in code)
- ✅ Works across sessions
- ✅ No UI interaction needed
- ✅ Standard practice

**Cons:**
- ❌ Need to set up on each machine
- ❌ Not user-friendly for non-technical users

---

### Option 2: Streamlit Secrets (Recommended for Cloud Deployment)
**Best for:** Streamlit Cloud, sharing with team

**How it works:**
- Store API keys in Streamlit's secure secrets management
- Accessible via `st.secrets["openai_api_key"]`
- Encrypted and secure

**Setup:**
1. For **Streamlit Cloud:**
   - Go to your app settings
   - Click "Secrets"
   - Add: `openai_api_key = "sk-your-key-here"`

2. For **Local use:**
   - Create `.streamlit/secrets.toml`:
   ```toml
   openai_api_key = "sk-your-api-key-here"
   ```
   - Add `.streamlit/secrets.toml` to `.gitignore` (already done)

**Pros:**
- ✅ Secure and encrypted
- ✅ Easy to manage
- ✅ Works for team sharing
- ✅ Built into Streamlit

**Cons:**
- ❌ Requires Streamlit Cloud or local secrets file
- ❌ Each user needs their own key

---

### Option 3: Local Config File (User-Friendly)
**Best for:** Single-user local deployment, non-technical users

**How it works:**
- Save API key to a local encrypted file
- App reads it automatically on startup
- User enters once, saved forever

**Setup:**
- First time: Enter API key in UI, check "Remember API Key"
- Key is saved to `~/.reqiq_config.json` (encrypted)
- Future sessions: Key loaded automatically

**Pros:**
- ✅ User-friendly
- ✅ No command-line setup needed
- ✅ Works for non-technical users

**Cons:**
- ❌ Less secure than environment variables
- ❌ File-based (can be deleted)

---

### Option 4: Session State Persistence
**Best for:** Quick testing, temporary use

**How it works:**
- API key stored in Streamlit session state
- Persists during the session
- Lost when browser closes

**Pros:**
- ✅ Simple
- ✅ No file system access needed

**Cons:**
- ❌ Lost on browser refresh
- ❌ Not persistent across sessions

---

## 🌐 Sharing & Deployment Options

### Option 1: Streamlit Cloud (Easiest - Recommended)
**Best for:** Quick sharing, free hosting, team collaboration

**Steps:**
1. **Push code to GitHub:**
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Deploy to Streamlit Cloud:**
   - Go to https://share.streamlit.io
   - Sign in with GitHub
   - Click "New app"
   - Select your repository
   - Choose branch: `main`
   - Main file: `app.py`
   - Click "Deploy"

3. **Configure Secrets:**
   - In app settings → Secrets
   - Add: `openai_api_key = "sk-your-key"`
   - App restarts automatically

4. **Share the URL:**
   - Your app will be at: `https://your-app-name.streamlit.app`
   - Share this URL with anyone

**Pros:**
- ✅ Free hosting
- ✅ Automatic HTTPS
- ✅ Easy deployment
- ✅ Built-in secrets management
- ✅ Auto-updates on git push
- ✅ No server management

**Cons:**
- ❌ Public apps are visible to anyone with URL
- ❌ Free tier has resource limits
- ❌ Requires GitHub account

**Cost:** Free (with usage limits)

---

### Option 2: Docker Container
**Best for:** Enterprise, self-hosting, full control

**Steps:**
1. **Create Dockerfile:**
   ```dockerfile
   FROM python:3.11-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   COPY . .
   EXPOSE 8501
   CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
   ```

2. **Build and run:**
   ```bash
   docker build -t reqiq .
   docker run -p 8501:8501 -e OPENAI_API_KEY="sk-your-key" reqiq
   ```

3. **Deploy to cloud:**
   - AWS ECS, Google Cloud Run, Azure Container Instances
   - Or any Docker hosting service

**Pros:**
- ✅ Full control
- ✅ Scalable
- ✅ Works anywhere Docker runs
- ✅ Isolated environment

**Cons:**
- ❌ Requires Docker knowledge
- ❌ Need to manage hosting
- ❌ More complex setup

**Cost:** Varies (cloud hosting costs)

---

### Option 3: Local Network Sharing
**Best for:** Internal team, same network, quick sharing

**Steps:**
1. **Find your local IP:**
   ```bash
   # macOS/Linux
   ifconfig | grep "inet " | grep -v 127.0.0.1
   
   # Windows
   ipconfig
   ```

2. **Run Streamlit on network:**
   ```bash
   streamlit run app.py --server.address=0.0.0.0 --server.port=8501
   ```

3. **Share IP address:**
   - Others access: `http://YOUR_IP:8501`
   - Example: `http://192.168.1.100:8501`

**Pros:**
- ✅ No cloud setup needed
- ✅ Fast (local network)
- ✅ Free
- ✅ Private (local network only)

**Cons:**
- ❌ Only works on same network
- ❌ Requires firewall configuration
- ❌ Not accessible from outside

**Cost:** Free

---

### Option 4: Self-Hosted Server (VPS/Cloud VM)
**Best for:** Production, enterprise, full control

**Steps:**
1. **Get a VPS:**
   - AWS EC2, DigitalOcean, Linode, etc.
   - Ubuntu/Debian recommended

2. **Install dependencies:**
   ```bash
   sudo apt update
   sudo apt install python3-pip python3-venv
   git clone your-repo
   cd your-repo
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Run with systemd (auto-start):**
   ```bash
   # Create service file: /etc/systemd/system/reqiq.service
   [Unit]
   Description=ReqIQ Streamlit App
   After=network.target
   
   [Service]
   User=your-user
   WorkingDirectory=/path/to/app
   Environment="PATH=/path/to/venv/bin"
   ExecStart=/path/to/venv/bin/streamlit run app.py --server.port=8501 --server.address=0.0.0.0
   Restart=always
   
   [Install]
   WantedBy=multi-user.target
   ```

4. **Start service:**
   ```bash
   sudo systemctl enable reqiq
   sudo systemctl start reqiq
   ```

5. **Configure reverse proxy (Nginx):**
   - For HTTPS and domain name
   - Point domain to server IP

**Pros:**
- ✅ Full control
- ✅ Custom domain
- ✅ Scalable
- ✅ Professional setup

**Cons:**
- ❌ Requires server management
- ❌ Need to handle security
- ❌ Ongoing maintenance

**Cost:** $5-50/month (VPS hosting)

---

### Option 5: Railway/Render/Fly.io (Platform as a Service)
**Best for:** Easy deployment, managed hosting

**Steps:**
1. **Connect GitHub repo**
2. **Set environment variables:**
   - `OPENAI_API_KEY=sk-your-key`
3. **Deploy automatically**

**Pros:**
- ✅ Easy setup
- ✅ Auto-deploy from Git
- ✅ Managed infrastructure
- ✅ Free tiers available

**Cons:**
- ❌ Platform-specific
- ❌ May have usage limits

**Cost:** Free tier available, paid plans for production

---

## 🎯 Recommended Approach

### For Personal Use:
1. **Local:** Use environment variables
2. **Sharing:** Streamlit Cloud (free, easy)

### For Team/Organization:
1. **Quick:** Streamlit Cloud with team secrets
2. **Production:** Docker + Cloud hosting (AWS/GCP/Azure)
3. **Internal:** Local network sharing or self-hosted

### For Enterprise:
1. **Docker container** on Kubernetes/ECS
2. **Self-hosted** with reverse proxy
3. **Custom authentication** layer

---

## 🔒 Security Best Practices

1. **Never commit API keys to Git**
   - Use `.gitignore` for config files
   - Use environment variables or secrets

2. **Use different keys for different environments**
   - Development key
   - Production key
   - Testing key

3. **Rotate keys regularly**
   - Change keys every 90 days
   - Revoke old keys

4. **Limit API key permissions**
   - Use keys with minimal required permissions
   - Set usage limits in OpenAI dashboard

5. **Monitor usage**
   - Check OpenAI dashboard regularly
   - Set up billing alerts

---

## 📝 Implementation Status

The app currently supports:
- ✅ Environment variable: `OPENAI_API_KEY`
- ✅ Session state (temporary)
- ✅ Manual input in UI

**Next steps to implement:**
- [ ] Streamlit secrets support
- [ ] Local config file with encryption
- [ ] "Remember API Key" checkbox
- [ ] API key validation and caching

---

## 🚀 Quick Start Examples

### Example 1: Local with Environment Variable
```bash
export OPENAI_API_KEY="sk-your-key"
streamlit run app.py
```

### Example 2: Streamlit Cloud
1. Push to GitHub
2. Deploy on share.streamlit.io
3. Add secret: `openai_api_key`
4. Share URL

### Example 3: Docker
```bash
docker run -p 8501:8501 -e OPENAI_API_KEY="sk-key" reqiq
```

---

## 📞 Need Help?

- **Streamlit Cloud:** https://docs.streamlit.io/streamlit-community-cloud
- **Docker:** https://docs.docker.com
- **Environment Variables:** Check your OS documentation



