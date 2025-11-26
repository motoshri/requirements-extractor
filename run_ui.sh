#!/bin/bash
# Quick start script for the Requirements Extractor UI

echo "🚀 Starting Requirements Extractor UI..."
echo ""
echo "The web interface will open in your browser."
echo "Press Ctrl+C to stop the server."
echo ""
echo "Note: File upload limit is set to 10GB in config."
echo ""

# Set max upload size via environment variable as well
export STREAMLIT_SERVER_MAX_UPLOAD_SIZE=10737418240
export STREAMLIT_SERVER_MAX_MESSAGE_SIZE=10737418240

python3 -m streamlit run app.py --server.maxUploadSize=10737418240 --server.maxMessageSize=10737418240

