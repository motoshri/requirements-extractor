# Troubleshooting Guide

## "Site Can't Be Reached" Error

If you see "This site can't be reached" when trying to access the UI, try these solutions:

### 1. Check if Dependencies are Installed

```bash
pip3 install -r requirements.txt
```

### 2. Use the Correct Command

**Important:** Use `python3 -m streamlit` instead of just `streamlit`:

```bash
python3 -m streamlit run app.py
```

Or use the provided script:
```bash
./run_ui.sh
```

### 3. Check if Server is Running

After running the command, you should see output like:
```
You can now view your Streamlit app in your browser.

Local URL: http://localhost:8501
Network URL: http://192.168.x.x:8501
```

### 4. Manual Browser Access

If the browser doesn't open automatically:
- Open your browser manually
- Go to: `http://localhost:8501`
- Or try: `http://127.0.0.1:8501`

### 5. Check Port Availability

If port 8501 is already in use, Streamlit will try the next available port (8502, 8503, etc.). Check the terminal output for the actual URL.

### 6. Firewall Issues

If you're on a corporate network or have a firewall:
- Make sure localhost connections are allowed
- Try disabling firewall temporarily to test

### 7. Check for Errors

Look at the terminal output for any error messages. Common issues:

**Import Error:**
```
ModuleNotFoundError: No module named 'streamlit'
```
**Solution:** Run `pip3 install -r requirements.txt`

**Port Already in Use:**
```
Address already in use
```
**Solution:** 
- Kill the existing process: `lsof -ti:8501 | xargs kill -9`
- Or use a different port: `python3 -m streamlit run app.py --server.port 8502`

### 8. Verify Python Installation

```bash
python3 --version
```
Should show Python 3.7 or higher.

### 9. Check File Permissions

Make sure `app.py` is readable:
```bash
ls -l app.py
chmod +x run_ui.sh  # If script doesn't run
```

## Still Having Issues?

1. **Check the terminal output** - Streamlit shows helpful error messages
2. **Try running in verbose mode:**
   ```bash
   python3 -m streamlit run app.py --logger.level=debug
   ```
3. **Verify all files are present:**
   ```bash
   ls -la *.py *.txt
   ```

## Quick Test

To verify everything works:
```bash
# 1. Install dependencies
pip3 install -r requirements.txt

# 2. Run the app
python3 -m streamlit run app.py

# 3. Open browser to http://localhost:8501
```

If you see the Requirements Extractor interface, everything is working! ✅


