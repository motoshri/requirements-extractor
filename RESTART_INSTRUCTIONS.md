# ⚠️ IMPORTANT: Restart Required for File Size Limit Changes

## The Problem
Streamlit has a default 200MB upload limit. To remove this limit, you need to:

1. **Update the config file** (already done ✅)
2. **Restart the Streamlit server** (required!)

## How to Restart

### If the server is running:
1. **Stop the current server**: Press `Ctrl+C` in the terminal where Streamlit is running
2. **Start it again**: Run `./run_ui.sh` or `python3 -m streamlit run app.py`

### Quick Restart Command:
```bash
# Kill any existing Streamlit processes
pkill -f streamlit

# Start fresh
./run_ui.sh
```

## Verify the Config is Working

After restarting, check the terminal output. You should see Streamlit starting with the new config.

The config file is at: `.streamlit/config.toml`

It should contain:
```toml
[server]
maxUploadSize = 10737418240  # 10GB
maxMessageSize = 10737418240  # 10GB
```

## Alternative: Use Command Line (No Restart Needed)

You can also start with command line arguments:
```bash
python3 -m streamlit run app.py --server.maxUploadSize=10737418240 --server.maxMessageSize=10737418240
```

This bypasses the config file and sets the limit directly.

## Still Having Issues?

If you're still seeing the 200MB limit after restarting:
1. Check that the `.streamlit/config.toml` file exists and has the correct values
2. Make sure you're restarting the server (not just refreshing the browser)
3. Try the command line method above
4. Clear your browser cache and try again


