# Quick Start Guide

## 🚀 Get Started in 3 Steps

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Set Your API Key (Optional)

You can either:
- Set environment variable: `export OPENAI_API_KEY="your-key"`
- Or enter it in the UI sidebar when you run the app

### Step 3: Launch the UI

**Option A: Using the script**
```bash
./run_ui.sh
```

**Option B: Direct command**
```bash
python3 -m streamlit run app.py
```

The web interface will automatically open in your browser at `http://localhost:8501`

## 📋 Using the UI

1. **Upload or Paste**: 
   - Upload a transcript file (.txt, .vtt, or .json)
   - OR paste transcript text directly

2. **Configure** (in sidebar):
   - Enter your OpenAI API key (if not set as env var)
   - Select the model (gpt-4o-mini is recommended for cost-effectiveness)

3. **Extract**:
   - Click the "🚀 Extract Requirements" button
   - Wait for processing (usually 10-30 seconds)

4. **Review & Download**:
   - Browse extracted requirements in organized tabs
   - Download as Markdown or JSON

## 📝 Example Transcript Format

```
John Doe: We need to implement user authentication.
Jane Smith: Yes, with multi-factor authentication support.
John Doe: That's a high priority requirement.
```

## 🎬 Video File Support

You can now upload video files (MP4, MOV, AVI, MKV) of **any size**:
1. Upload your Teams meeting recording (no size limit!)
2. The app will automatically:
   - Extract audio from the video
   - Split large files into chunks (if needed)
   - Transcribe each chunk using OpenAI Whisper
   - Combine all transcripts
   - Extract requirements from the complete transcript

**Features:**
- ✅ **No file size limit** - Upload files of any size
- ✅ **Automatic chunking** - Large files are split automatically
- ✅ **Progress tracking** - See real-time progress for each chunk

**Requirements:**
- FFmpeg installed on your system
- moviepy and pydub Python packages (included in requirements.txt)
- OpenAI API key with access to Whisper API

## 💡 Tips

- **File Upload**: Works best with properly formatted transcripts
- **Text Paste**: Great for quick testing or small transcripts
- **Model Selection**: 
  - `gpt-4o-mini`: Fast, cost-effective (recommended)
  - `gpt-4o`: More accurate, slower, more expensive
- **API Key**: You can enter it in the UI - it's stored only in your session

## 🆘 Need Help?

Check the main [README.md](README.md) for detailed documentation and troubleshooting.

