# Requirements Extractor from Teams Meetings

A Python tool to automatically extract and structure requirements from Microsoft Teams meeting transcripts.

## Features

- 🖥️ **Simple Web UI** - Easy-to-use Streamlit interface
- 📝 Supports multiple transcript formats (Text, VTT, JSON)
- 🎬 **Video File Support** - Upload MP4, MOV, AVI, MKV files and automatically transcribe
- 🎤 **Automatic Transcription** - Uses OpenAI Whisper API for speech-to-text
- 🤖 AI-powered requirement extraction using OpenAI
- 📊 Structured output in Markdown and JSON formats
- 🎯 Extracts:
  - Functional Requirements
  - Non-Functional Requirements
  - Business Rules
  - Assumptions
  - Action Items
  - Decisions
  - Stakeholders

## Installation

1. **Clone or download this repository**

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install FFmpeg (Required for video processing):**
   
   **macOS:**
   ```bash
   brew install ffmpeg
   ```
   
   **Linux (Ubuntu/Debian):**
   ```bash
   sudo apt-get install ffmpeg
   ```
   
   **Windows:**
   - Download from https://ffmpeg.org/download.html
   - Add to PATH
   
   *Note: FFmpeg is only needed if you want to process video files. Text transcripts don't require it.*

4. **Set up OpenAI API key:**
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```
   
   Or pass it directly when running the script with `--api-key` parameter.

## Usage

### 🖥️ Web UI (Recommended)

The easiest way to use the tool is through the web interface:

```bash
python3 -m streamlit run app.py
```

Or use the convenience script:
```bash
./run_ui.sh
```

This will open a web browser with an intuitive interface where you can:
- Upload transcript files or paste text directly
- Configure API key and model settings
- View extracted requirements in organized tabs
- Download results as Markdown or JSON

**Features:**
- 📁 File upload support (drag & drop)
- 🎬 Video file support (MP4, MOV, AVI, MKV)
- 📝 Text paste option
- ⚙️ Easy configuration in sidebar
- 📊 Interactive results display
- 💾 One-click download

### Command Line Usage

#### Basic Usage

```bash
python requirements_extractor.py transcript.txt
```

### With Options

```bash
# Specify output file
python requirements_extractor.py transcript.txt -o my_requirements.md

# Output as JSON
python requirements_extractor.py transcript.txt -f json -o requirements.json

# Output both formats
python requirements_extractor.py transcript.txt -f both

# Use specific OpenAI model
python requirements_extractor.py transcript.txt --model gpt-4o
```

### Supported File Formats

#### Transcript Files:
1. **Plain Text (.txt)**
   - Format: `Speaker Name: message text`
   - Or: `[Speaker Name] message text`

2. **WebVTT (.vtt)**
   - Standard VTT format with timestamps
   - Supports speaker identification

3. **JSON (.json)**
   - Teams export format
   - Flexible structure parsing

#### Video Files:
4. **Video Files (.mp4, .mov, .avi, .mkv, .webm)**
   - Automatically extracts audio and transcribes using OpenAI Whisper
   - Supports Teams meeting recordings
   - **No file size limit** - Large files are automatically chunked
   - Progress indicators show chunk processing status

## Getting Teams Transcripts

### Method 1: From Teams Recording
1. Open the Teams meeting recording
2. Click on "..." (More options)
3. Select "Download transcript" or "Copy transcript"
4. Save as `.txt` or `.vtt` file

### Method 2: From Live Transcription
1. During the meeting, enable live transcription
2. After the meeting, go to the meeting chat
3. Find the transcript and copy it
4. Save to a text file

### Method 3: Using Teams API (Advanced)
- Use Microsoft Graph API to retrieve transcripts programmatically
- Requires appropriate permissions and authentication

## Example Output

The tool generates structured requirements like:

```markdown
# Requirements Extracted from Meeting

## Functional Requirements

### FR-001
**Description:** User should be able to login with email and password
**Priority:** High
**Source:** John Doe
**Context:** Discussed during authentication flow review

## Action Items

| ID | Task | Owner | Deadline | Status |
|----|------|-------|----------|--------|
| AI-001 | Create login mockup | Jane Smith | 2024-01-15 | Open |
```

## Command Line Options

```
positional arguments:
  transcript            Path to transcript file (supports .txt, .vtt, .json)

optional arguments:
  -h, --help           Show help message
  -o, --output         Output file path (default: requirements_<timestamp>.md)
  -f, --format         Output format: markdown, json, or both (default: markdown)
  --api-key            OpenAI API key (or set OPENAI_API_KEY env var)
  --model              OpenAI model to use (default: gpt-4o-mini)
```

## Configuration

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (optional if using --api-key flag)

### Model Selection

- `gpt-4o-mini`: Fast and cost-effective (default)
- `gpt-4o`: More accurate but slower and more expensive
- `gpt-3.5-turbo`: Alternative option

## Troubleshooting

### "OpenAI API key not found"
- Set the `OPENAI_API_KEY` environment variable, or
- Use the `--api-key` parameter when running the script

### "Error parsing transcript"
- Check that your transcript file is in a supported format
- For text files, ensure speaker names are separated by colons or brackets
- For VTT files, verify the format is valid WebVTT

### "No requirements extracted"
- The transcript might not contain clear requirements
- Try using a more powerful model (e.g., `gpt-4o`)
- Ensure the transcript is complete and readable

### "Error processing video" or "moviepy is required"
- Install moviepy: `pip3 install moviepy`
- Install FFmpeg (see Installation section above)
- Install pydub for large file chunking: `pip3 install pydub`
- **No file size limit**: Large files are automatically chunked and processed
- The app handles files of any size by splitting them into smaller chunks for the Whisper API

### "Error transcribing audio"
- Check your OpenAI API key is valid
- Ensure you have sufficient API credits
- Verify the audio file was extracted correctly
- Check OpenAI API status for any service issues

## Advanced Usage

### Processing Multiple Transcripts

```bash
for file in transcripts/*.txt; do
    python requirements_extractor.py "$file" -o "outputs/$(basename $file .txt)_requirements.md"
done
```

### Custom Extraction

You can modify the extraction prompt in `requirements_extractor.py` to customize what gets extracted based on your specific needs.

## License

This tool is provided as-is for extracting requirements from meeting transcripts.

## Contributing

Feel free to extend this tool with additional features:
- Support for more transcript formats
- Integration with Teams API
- Custom requirement templates
- Export to other formats (Excel, Jira, etc.)

