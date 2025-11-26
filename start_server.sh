#!/bin/bash
# Start Streamlit server with proper configuration

cd /Users/Shrikant/Requirements_from_calls

# Ensure credentials file exists to skip onboarding
mkdir -p ~/.streamlit
if [ ! -f ~/.streamlit/credentials.toml ]; then
    echo '[general]
email = ""' > ~/.streamlit/credentials.toml
fi

echo "🚀 Starting Streamlit server..."
echo "📋 Config file: .streamlit/config.toml"
echo "📊 Max upload size: 10GB"
echo ""
echo "The server will be available at: http://localhost:8501"
echo "Press Ctrl+C to stop the server"
echo ""

# Start the server
python3 -m streamlit run app.py --server.port 8501


