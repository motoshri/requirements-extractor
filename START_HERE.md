# 🚀 START HERE - Quick Setup

## Step-by-Step Instructions

### Step 1: Install Dependencies (One-time setup)

Open Terminal and run:
```bash
cd /Users/Shrikant/Requirements_from_calls
pip3 install -r requirements.txt
```

Wait for installation to complete (takes 1-2 minutes).

### Step 2: Start the Web UI

Run this command:
```bash
python3 -m streamlit run app.py
```

**Important:** Use `python3 -m streamlit` (not just `streamlit`)

### Step 3: Open in Browser

The app will automatically try to open in your browser. If it doesn't:

1. Look at the terminal output - it will show a URL like:
   ```
   Local URL: http://localhost:8501
   ```

2. Open your browser and go to: **http://localhost:8501**

### Step 4: Use the App

1. **Enter your OpenAI API key** in the sidebar (or set `OPENAI_API_KEY` environment variable)
2. **Upload a transcript file** or paste text
3. **Click "Extract Requirements"**
4. **View and download results**

## ✅ That's It!

The web interface should now be accessible.

## ❌ Still Not Working?

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for detailed help.

## 💡 Quick Tips

- Keep the terminal window open while using the app
- Press `Ctrl+C` in the terminal to stop the server
- The app runs on `http://localhost:8501` by default


