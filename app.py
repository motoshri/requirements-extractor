#!/usr/bin/env python3
"""
Streamlit UI for Requirements Extractor from Teams Meetings
Simple web interface for extracting requirements from transcripts.
"""

import streamlit as st
import tempfile
import os
from pathlib import Path
from datetime import datetime
import json

from requirements_extractor import (
    TranscriptParser,
    RequirementsExtractor,
    RequirementsFormatter
)

# Configure FFmpeg path before importing moviepy
try:
    import imageio_ffmpeg
    ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
    os.environ["IMAGEIO_FFMPEG_EXE"] = ffmpeg_path
    os.environ["FFMPEG_BINARY"] = ffmpeg_path
    os.environ["FFMPEG_EXE"] = ffmpeg_path
    # Also set for moviepy
    os.environ["MOVIEPY_FFMPEG_BINARY"] = ffmpeg_path
    
    # Create ffprobe wrapper (ffmpeg can act as ffprobe)
    import os.path as osp
    temp_bin_dir = osp.join(osp.expanduser("~"), ".requirements_extractor_bin")
    os.makedirs(temp_bin_dir, exist_ok=True)
    ffprobe_wrapper = osp.join(temp_bin_dir, "ffprobe")
    
    # Create a shell script that calls ffmpeg with probe-like behavior
    if not osp.exists(ffprobe_wrapper):
        with open(ffprobe_wrapper, 'w') as f:
            f.write(f"""#!/bin/bash
# Wrapper to use ffmpeg as ffprobe
# ffmpeg can handle most probe operations when called correctly
exec "{ffmpeg_path}" -hide_banner -loglevel error "$@"
""")
        os.chmod(ffprobe_wrapper, 0o755)
    
    os.environ["FFPROBE_BINARY"] = ffprobe_wrapper
    os.environ["FFPROBE"] = ffprobe_wrapper
    # Add to PATH so subprocess calls can find it
    os.environ["PATH"] = temp_bin_dir + os.pathsep + os.environ.get("PATH", "")
except Exception as e:
    pass  # If imageio_ffmpeg is not available, try system FFmpeg

# Try to import video processing libraries
try:
    # Try new moviepy 2.x import first
    try:
        from moviepy import VideoFileClip
    except ImportError:
        # Fallback to old moviepy 1.x import
        from moviepy.editor import VideoFileClip
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False

try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False

# Try to import local Whisper (no API key needed)
try:
    import whisper
    WHISPER_LOCAL_AVAILABLE = True
except ImportError:
    WHISPER_LOCAL_AVAILABLE = False

# Page configuration
st.set_page_config(
    page_title="Requirements Extractor",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables."""
    if 'requirements' not in st.session_state:
        st.session_state.requirements = None
    if 'transcript_text' not in st.session_state:
        st.session_state.transcript_text = None
    if 'messages_parsed' not in st.session_state:
        st.session_state.messages_parsed = None
    if 'partial_requirements' not in st.session_state:
        st.session_state.partial_requirements = []
    if 'processing_status' not in st.session_state:
        st.session_state.processing_status = None


def parse_transcript_file(uploaded_file):
    """Parse uploaded transcript file."""
    parser = TranscriptParser()
    
    # Save uploaded file temporarily
    file_extension = Path(uploaded_file.name).suffix.lower()
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_path = tmp_file.name
    
    try:
        # Parse based on file extension
        if file_extension == '.vtt':
            messages = parser.parse_vtt(tmp_path)
        elif file_extension == '.json':
            messages = parser.parse_json(tmp_path)
        else:
            messages = parser.parse_text(tmp_path)
        
        return messages, None
    except Exception as e:
        return None, str(e)
    finally:
        # Clean up temp file
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def parse_transcript_text(text):
    """Parse transcript from text input."""
    parser = TranscriptParser()
    
    # Save to temp file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as tmp_file:
        tmp_file.write(text)
        tmp_path = tmp_file.name
    
    try:
        messages = parser.parse_text(tmp_path)
        return messages, None
    except Exception as e:
        return None, str(e)
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def extract_audio_from_video(video_path: str, output_audio_path: str = None) -> str:
    """Extract audio from video file."""
    if not MOVIEPY_AVAILABLE:
        raise ImportError("moviepy is required for video processing. Install it with: pip install moviepy")
    
    if output_audio_path is None:
        output_audio_path = video_path.rsplit('.', 1)[0] + '.mp3'
    
    try:
        # Ensure FFmpeg is configured before creating VideoFileClip
        try:
            import imageio_ffmpeg
            ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
            os.environ["FFMPEG_BINARY"] = ffmpeg_path
            # Use ffmpeg as ffprobe (ffmpeg can handle probe operations)
            os.environ["FFPROBE_BINARY"] = ffmpeg_path
            os.environ["FFPROBE"] = ffmpeg_path
            # Configure moviepy config directly
            try:
                import moviepy.config as mp_config
                mp_config.FFMPEG_BINARY = ffmpeg_path
                # Try to set ffprobe in moviepy config if it exists
                if hasattr(mp_config, 'FFPROBE_BINARY'):
                    mp_config.FFPROBE_BINARY = ffmpeg_path
            except:
                pass
        except:
            pass
        
        video = VideoFileClip(video_path)
        audio = video.audio
        # moviepy 2.x doesn't support verbose parameter
        try:
            # Try without verbose (moviepy 2.x)
            audio.write_audiofile(output_audio_path, logger=None)
        except TypeError:
            # Fallback for older versions
            try:
                audio.write_audiofile(output_audio_path, verbose=False, logger=None)
            except:
                # Last resort: try with minimal parameters
                audio.write_audiofile(output_audio_path)
        audio.close()
        video.close()
        return output_audio_path
    except Exception as e:
        raise Exception(f"Error extracting audio from video: {str(e)}")


def transcribe_audio_local_whisper(audio_path: str, progress_callback=None, model_size="base"):
    """Transcribe audio using local Whisper (no API key needed)."""
    if not WHISPER_LOCAL_AVAILABLE:
        raise ImportError("Local Whisper is not available. Install it with: pip install openai-whisper")
    
    try:
        # Check for NumPy before proceeding
        try:
            import numpy
        except ImportError:
            raise ImportError("NumPy is required for Whisper. Install it with: pip install numpy")
        
        # Configure ffmpeg path for Whisper (use imageio_ffmpeg's bundled ffmpeg)
        try:
            import imageio_ffmpeg
            ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
            
            # Set environment variables for ffmpeg
            os.environ["FFMPEG_BINARY"] = ffmpeg_path
            os.environ["FFMPEG_PATH"] = ffmpeg_path
            
            # Add ffmpeg directory to PATH so subprocess calls can find it
            ffmpeg_dir = os.path.dirname(ffmpeg_path)
            current_path = os.environ.get("PATH", "")
            if ffmpeg_dir not in current_path:
                os.environ["PATH"] = ffmpeg_dir + os.pathsep + current_path
            
            # Create a symlink named 'ffmpeg' in a temp directory that Whisper can find
            import os.path as osp
            temp_bin_dir = osp.join(osp.expanduser("~"), ".requirements_extractor_bin")
            os.makedirs(temp_bin_dir, exist_ok=True)
            ffmpeg_link = osp.join(temp_bin_dir, "ffmpeg")
            
            # Create symlink if it doesn't exist or is broken
            if not osp.exists(ffmpeg_link) or not osp.islink(ffmpeg_link):
                try:
                    if osp.exists(ffmpeg_link):
                        os.remove(ffmpeg_link)
                    os.symlink(ffmpeg_path, ffmpeg_link)
                except Exception:
                    # If symlink fails, try creating a wrapper script
                    with open(ffmpeg_link, 'w') as f:
                        f.write(f"""#!/bin/bash
exec "{ffmpeg_path}" "$@"
""")
                    os.chmod(ffmpeg_link, 0o755)
            
            # Add temp bin directory to PATH (at the beginning for priority)
            if temp_bin_dir not in os.environ.get("PATH", ""):
                os.environ["PATH"] = temp_bin_dir + os.pathsep + os.environ.get("PATH", "")
                
        except Exception as ffmpeg_error:
            # If we can't set ffmpeg path, continue - might work with system ffmpeg
            pass
        
        if progress_callback:
            progress_callback(0.1, f"📥 Loading Whisper model ({model_size})...")
        
        # Load Whisper model
        model = whisper.load_model(model_size)
        
        if progress_callback:
            progress_callback(0.3, "🎤 Transcribing audio (this may take a while)...")
        
        # Transcribe audio - explicitly set ffmpeg path if available
        try:
            result = model.transcribe(audio_path)
        except FileNotFoundError as e:
            if "ffmpeg" in str(e).lower():
                # Try to use imageio_ffmpeg's ffmpeg
                try:
                    import imageio_ffmpeg
                    ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
                    # Set as environment variable
                    os.environ["PATH"] = os.path.dirname(ffmpeg_path) + os.pathsep + os.environ.get("PATH", "")
                    os.environ["FFMPEG_BINARY"] = ffmpeg_path
                    # Retry transcription
                    result = model.transcribe(audio_path)
                except Exception as retry_error:
                    raise Exception(
                        f"FFmpeg not found. Whisper needs FFmpeg to process audio.\n\n"
                        f"Error: {str(e)}\n\n"
                        f"Solution: Install FFmpeg:\n"
                        f"  macOS: brew install ffmpeg\n"
                        f"  Linux: sudo apt-get install ffmpeg\n"
                        f"  Or ensure imageio_ffmpeg is installed: pip install imageio-ffmpeg"
                    )
            else:
                raise
        
        if progress_callback:
            progress_callback(0.9, "✅ Transcription complete!")
        
        # Extract text from result
        text = result.get("text", "")
        
        if not text or len(text.strip()) == 0:
            raise Exception("Received empty transcript from Whisper")
        
        return text, []
        
    except ImportError as e:
        # Re-raise import errors with helpful message
        raise Exception(f"Missing dependency: {str(e)}\n\nPlease install: pip install numpy")
    except Exception as e:
        error_msg = str(e)
        # Check if it's a NumPy-related error
        if "numpy" in error_msg.lower() or "NumPy" in error_msg:
            raise Exception(
                f"NumPy error: {error_msg}\n\n"
                "This might be a NumPy version compatibility issue.\n"
                "Try: pip install 'numpy<2.0'"
            )
        # Check if it's an ffmpeg error
        if "ffmpeg" in error_msg.lower() or "No such file" in error_msg:
            raise Exception(
                f"FFmpeg error: {error_msg}\n\n"
                "Whisper needs FFmpeg to process audio files.\n\n"
                "Install FFmpeg:\n"
                "  macOS: brew install ffmpeg\n"
                "  Linux: sudo apt-get install ffmpeg\n"
                "  Windows: Download from https://ffmpeg.org\n\n"
                "Or install imageio-ffmpeg: pip install imageio-ffmpeg"
            )
        raise Exception(f"Error transcribing with local Whisper: {error_msg}")


def transcribe_audio_with_whisper(audio_path: str, api_key: str = None, use_local: bool = False, progress_callback=None):
    """Transcribe audio file using OpenAI Whisper API. Handles large files by chunking."""
    try:
        from openai import OpenAI
        import json
        
        # Validate API key
        if not api_key or not api_key.strip():
            raise Exception("❌ OpenAI API key is missing. Please provide your API key in the sidebar.")
        
        # Validate API key format (should start with sk-)
        if not api_key.startswith('sk-'):
            raise Exception("❌ Invalid API key format. OpenAI API keys should start with 'sk-'. Please check your API key.")
        
        # Test API key with a simple request first
        try:
            client = OpenAI(api_key=api_key)
            # Try to list models to verify API key works
            # This is a lightweight test that doesn't cost anything
            try:
                models = client.models.list(limit=1)
                # If we get here, the API key is valid
                if progress_callback:
                    progress_callback(0.05, "✅ API key validated")
            except Exception as model_test_error:
                error_str = str(model_test_error)
                # If models.list fails, that's okay - we'll still try transcription
                # Some API keys might not have model list access
                if progress_callback:
                    progress_callback(0.05, "⚠️ Could not validate API key (will still try transcription)")
        except Exception as key_test_error:
            error_str = str(key_test_error)
            if "Invalid OpenAI API key" in error_str:
                raise  # Re-raise our custom error
            # Otherwise, continue - might be a network issue
        
        # Check file size (Whisper API limit is 25MB)
        file_size_mb = os.path.getsize(audio_path) / (1024 * 1024)
        max_size_mb = 25  # OpenAI Whisper API limit
        
        if file_size_mb <= max_size_mb:
            # File is small enough, transcribe directly
            with open(audio_path, 'rb') as audio_file:
                try:
                    # Verify file is readable
                    file_size = os.path.getsize(audio_path)
                    if file_size == 0:
                        raise Exception("Audio file is empty or corrupted")
                    
                    # Try transcription - catch all errors including JSON parsing
                    try:
                        # Reset file pointer to beginning
                        audio_file.seek(0)
                        
                        # Make the API call with explicit parameters
                        transcript = client.audio.transcriptions.create(
                            model="whisper-1",
                            file=audio_file,
                            response_format="text"  # Explicitly request text format
                        )
                    except Exception as create_error:
                        error_str = str(create_error)
                        error_type = type(create_error).__name__
                        
                        # Try to extract detailed error information
                        debug_info = []
                        debug_info.append(f"Error Type: {error_type}")
                        debug_info.append(f"Error Message: {error_str}")
                        
                        # Check for OpenAI API error attributes
                        if hasattr(create_error, 'response'):
                            try:
                                response = create_error.response
                                if hasattr(response, 'status_code'):
                                    debug_info.append(f"HTTP Status: {response.status_code}")
                                if hasattr(response, 'text'):
                                    response_text = response.text[:1000]
                                    debug_info.append(f"Response Text: {response_text}")
                                if hasattr(response, 'headers'):
                                    debug_info.append(f"Response Headers: {dict(response.headers)}")
                            except Exception as e:
                                debug_info.append(f"Could not extract response details: {e}")
                        
                        # Check for body attribute
                        if hasattr(create_error, 'body'):
                            try:
                                body = create_error.body
                                if isinstance(body, dict):
                                    debug_info.append(f"Error Body: {body}")
                                elif isinstance(body, str):
                                    debug_info.append(f"Error Body: {body[:1000]}")
                            except:
                                pass
                        
                        # Check if it's a JSON-related error (most common cause: invalid API key)
                        if "Expecting value" in error_str or "JSON" in error_str or "JSONDecodeError" in error_type or "json" in error_type.lower() or "decode" in error_str.lower():
                            # This error almost always means invalid API key
                            debug_details = "\n".join(debug_info)
                            raise Exception(
                                "❌ INVALID API KEY DETECTED\n\n"
                                "The error 'Expecting value: line 1 column 1 (char 0)' means the API returned\n"
                                "an empty or non-JSON response, which typically indicates an INVALID API KEY.\n\n"
                                "🔧 FIX THIS:\n"
                                "1. Open https://platform.openai.com/api-keys in your browser\n"
                                "2. Click 'Create new secret key'\n"
                                "3. Copy the NEW key (starts with 'sk-')\n"
                                "4. Paste it in the sidebar of this app\n"
                                "5. Make sure billing is set up: https://platform.openai.com/account/billing\n\n"
                                f"Debug Information:\n{debug_details}\n\n"
                                f"Original error: {error_str}"
                            )
                        raise
                    
                    # Handle response - OpenAI SDK returns an object with .text attribute
                    if hasattr(transcript, 'text'):
                        text = transcript.text
                    elif isinstance(transcript, str):
                        text = transcript
                    else:
                        text = str(transcript)
                    
                    if not text or len(text.strip()) == 0:
                        raise Exception("Received empty transcript from Whisper API")
                    
                    return text, []
                    
                except Exception as api_error:
                    error_msg = str(api_error)
                    error_type = type(api_error).__name__
                    
                    # Get more details from the exception if available
                    error_details = ""
                    raw_response = ""
                    
                    # Try to extract response details from OpenAI API error
                    if hasattr(api_error, 'response'):
                        try:
                            response = api_error.response
                            if hasattr(response, 'text'):
                                raw_response = response.text[:500]
                            elif hasattr(response, 'content'):
                                raw_response = str(response.content)[:500]
                            elif hasattr(response, 'body'):
                                raw_response = str(response.body)[:500]
                            
                            if hasattr(response, 'status_code'):
                                error_details += f"\nHTTP Status: {response.status_code}"
                            if hasattr(response, 'headers'):
                                error_details += f"\nResponse Headers: {str(response.headers)[:200]}"
                        except Exception as e:
                            pass
                    
                    # Also check for body attribute directly on the error
                    if hasattr(api_error, 'body'):
                        try:
                            if isinstance(api_error.body, dict):
                                raw_response = str(api_error.body)[:500]
                            elif isinstance(api_error.body, str):
                                raw_response = api_error.body[:500]
                        except:
                            pass
                    
                    # Check for common API errors
                    if "Invalid API key" in error_msg or "401" in error_msg or "authentication" in error_msg.lower() or "incorrect API key" in error_msg.lower() or "invalid_api_key" in error_msg.lower() or "401" in str(raw_response):
                        raise Exception("❌ Invalid OpenAI API key. Please check your API key in the sidebar and ensure it's correct.\n\nGet your API key at: https://platform.openai.com/api-keys")
                    elif "insufficient_quota" in error_msg or "429" in error_msg or "quota" in error_msg.lower() or "billing" in error_msg.lower() or "rate_limit" in error_msg.lower() or "429" in str(raw_response):
                        raise Exception("❌ OpenAI API quota exceeded or rate limit reached. Please check your account billing at https://platform.openai.com/account/billing")
                    elif "file_size" in error_msg.lower() or "too large" in error_msg.lower():
                        raise Exception(f"Audio file is too large ({file_size_mb:.2f}MB). The file will be chunked automatically.")
                    elif "JSON" in error_type or "json" in error_msg.lower() or "Expecting value" in error_msg or "decode" in error_msg.lower() or "JSONDecodeError" in error_type:
                        # JSON parsing error - likely API returned error HTML or empty response
                        detailed_msg = f"❌ API communication error: {error_msg}"
                        detailed_msg += "\n\nThis usually means:"
                        detailed_msg += "\n1. Invalid or expired API key (most common)"
                        detailed_msg += "\n2. Network/proxy/firewall blocking the request"
                        detailed_msg += "\n3. OpenAI API service issue"
                        detailed_msg += "\n4. API key doesn't have access to Whisper API"
                        detailed_msg += f"\n\nPlease verify your API key at: https://platform.openai.com/api-keys"
                        if error_details:
                            detailed_msg += error_details
                        if raw_response:
                            detailed_msg += f"\n\nRaw API Response (first 500 chars):\n{raw_response}"
                        raise Exception(detailed_msg)
                    elif "timeout" in error_msg.lower():
                        raise Exception("❌ Request timed out. The audio file might be too large. Try a smaller file or check your network connection.")
                    elif "connection" in error_msg.lower() or "network" in error_msg.lower():
                        raise Exception("❌ Network connection error. Please check your internet connection and try again.")
                    else:
                        detailed_msg = f"❌ Whisper API error: {error_msg}"
                        detailed_msg += "\n\nPlease check:"
                        detailed_msg += "\n1. Your API key is valid and active"
                        detailed_msg += "\n2. You have sufficient credits"
                        detailed_msg += "\n3. Your network connection is stable"
                        detailed_msg += "\n4. The audio file format is supported"
                        if error_details:
                            detailed_msg += error_details
                        if raw_response:
                            detailed_msg += f"\n\nRaw API Response (first 500 chars):\n{raw_response}"
                        raise Exception(detailed_msg)
        else:
            # File is too large, need to chunk it
            if not PYDUB_AVAILABLE:
                raise ImportError("pydub is required for processing large audio files. Install it with: pip install pydub")
            
            if progress_callback:
                progress_callback(0.1, "📦 Splitting large audio file into chunks...")
            
            # Load audio file
            audio = AudioSegment.from_file(audio_path)
            duration_seconds = len(audio) / 1000.0
            
            # Calculate chunk size (aim for ~20MB chunks to be safe)
            # Approximate: 1 minute of audio ≈ 1MB (compressed MP3)
            # So 20 minutes ≈ 20MB
            chunk_duration_ms = 20 * 60 * 1000  # 20 minutes in milliseconds
            total_chunks = int(duration_seconds / (chunk_duration_ms / 1000)) + 1
            
            all_text_parts = []
            all_segments = []
            
            # Process in chunks
            for i in range(total_chunks):
                start_ms = i * chunk_duration_ms
                end_ms = min((i + 1) * chunk_duration_ms, len(audio))
                
                if start_ms >= len(audio):
                    break
                
                if progress_callback:
                    progress = 0.1 + (i / total_chunks) * 0.8
                    progress_callback(progress, f"🎤 Transcribing chunk {i+1}/{total_chunks}...")
                
                # Extract chunk
                chunk = audio[start_ms:end_ms]
                
                # Save chunk temporarily
                chunk_path = audio_path.rsplit('.', 1)[0] + f'_chunk_{i}.mp3'
                chunk.export(chunk_path, format="mp3")
                
                try:
                    # Transcribe chunk
                    with open(chunk_path, 'rb') as chunk_file:
                        try:
                            transcript = client.audio.transcriptions.create(
                                model="whisper-1",
                                file=chunk_file
                            )
                            chunk_text = transcript.text if hasattr(transcript, 'text') else (transcript if isinstance(transcript, str) else str(transcript))
                            chunk_segments = []
                            
                            if not chunk_text or len(chunk_text.strip()) == 0:
                                # Skip empty chunks
                                continue
                        except Exception as chunk_api_error:
                            error_msg = str(chunk_api_error)
                            error_type = type(chunk_api_error).__name__
                            
                            # Check if it's a JSON-related error (invalid API key)
                            if "JSON" in error_msg or "Expecting value" in error_msg or "decode" in error_msg.lower() or "JSONDecodeError" in error_type:
                                # Critical error - invalid API key, stop processing
                                raise Exception(
                                    "❌ INVALID API KEY DETECTED\n\n"
                                    "The error 'Expecting value: line 1 column 1 (char 0)' means the API returned\n"
                                    "an empty or non-JSON response, which typically indicates an INVALID API KEY.\n\n"
                                    "🔧 FIX THIS:\n"
                                    "1. Open https://platform.openai.com/api-keys in your browser\n"
                                    "2. Click 'Create new secret key'\n"
                                    "3. Copy the NEW key (starts with 'sk-')\n"
                                    "4. Paste it in the sidebar of this app\n"
                                    "5. Make sure billing is set up: https://platform.openai.com/account/billing\n\n"
                                    f"Original error: {error_msg}"
                                )
                            # For other errors, skip this chunk but continue
                            if progress_callback:
                                progress_callback(progress, f"⚠️ Warning: Skipped chunk {i+1} due to error: {error_msg}")
                            continue
                    
                    # Adjust segment timestamps (segments are dicts from API)
                    offset_seconds = start_ms / 1000.0
                    for segment in chunk_segments:
                        if isinstance(segment, dict):
                            if 'start' in segment:
                                segment['start'] += offset_seconds
                            if 'end' in segment:
                                segment['end'] += offset_seconds
                        else:
                            # If it's an object, try to update attributes
                            if hasattr(segment, 'start'):
                                segment.start += offset_seconds
                            if hasattr(segment, 'end'):
                                segment.end += offset_seconds
                    
                    all_text_parts.append(chunk_text)
                    all_segments.extend(chunk_segments)
                    
                except Exception as chunk_error:
                    # Re-raise if it's our custom invalid API key error
                    error_msg = str(chunk_error)
                    if "INVALID API KEY" in error_msg:
                        raise
                    # If chunk fails for other reasons, log and continue with other chunks
                    if "JSON" in error_msg or "Expecting value" in error_msg or "decode" in error_msg.lower():
                        # Critical error - likely API key issue, stop processing
                        raise Exception(f"❌ API error while processing chunk {i+1}: {error_msg}\n\nThis usually indicates an invalid API key. Please check your API key.")
                    # For other errors, skip this chunk but continue
                    if progress_callback:
                        progress_callback(progress, f"⚠️ Warning: Skipped chunk {i+1} due to error")
                    continue
                finally:
                    # Clean up chunk file
                    if os.path.exists(chunk_path):
                        os.unlink(chunk_path)
            
            # Combine all transcripts
            combined_text = '\n'.join(all_text_parts)
            
            if progress_callback:
                progress_callback(0.95, "✅ Combining transcripts...")
            
            return combined_text, all_segments
            
    except Exception as e:
        error_msg = str(e)
        # Don't double-wrap our custom error messages - preserve them completely
        if "INVALID API KEY" in error_msg or "FIX THIS:" in error_msg or "Debug Information:" in error_msg:
            raise  # Re-raise our custom error as-is (it already has all the details)
        # For JSON errors, provide detailed help
        if "Expecting value" in error_msg or "JSON" in error_msg or "JSONDecodeError" in str(type(e).__name__):
            raise Exception(
                f"Error transcribing audio: {error_msg}\n\n"
                "This JSON parsing error typically means:\n"
                "1. ❌ INVALID API KEY (most common)\n"
                "2. Network/proxy blocking the request\n"
                "3. API service issue\n\n"
                "Please:\n"
                "1. Verify your API key at https://platform.openai.com/api-keys\n"
                "2. Generate a NEW key if needed\n"
                "3. Check billing at https://platform.openai.com/account/billing"
            )
        # Otherwise, wrap it but preserve the full message
        raise Exception(f"Error transcribing audio: {error_msg}")


def process_video_file(uploaded_file, api_key: str = None, progress_bar=None, status_text=None, use_local: bool = False):
    """Process video file: extract audio and transcribe. Handles files of any size."""
    file_extension = Path(uploaded_file.name).suffix.lower()
    
    # Save video temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_video:
        tmp_video.write(uploaded_file.getvalue())
        tmp_video_path = tmp_video.name
    
    tmp_audio_path = None
    transcript_text = None
    
    def update_progress(progress, message):
        """Helper to update progress bar and status."""
        if progress_bar:
            progress_bar.progress(progress)
        if status_text:
            status_text.info(message)
    
    try:
        # Step 1: Extract audio
        update_progress(0.1, "🎬 Extracting audio from video...")
        
        tmp_audio_path = tmp_video_path.rsplit('.', 1)[0] + '.mp3'
        extract_audio_from_video(tmp_video_path, tmp_audio_path)
        
        audio_size_mb = os.path.getsize(tmp_audio_path) / (1024 * 1024)
        update_progress(0.2, f"🎤 Audio extracted ({audio_size_mb:.2f} MB). Starting transcription...")
        
        # Step 2: Transcribe audio (with chunking for large files)
        def progress_callback(progress, message):
            # Map 0.1-0.95 to 0.2-0.9 range
            mapped_progress = 0.2 + (progress * 0.7)
            update_progress(mapped_progress, message)
        
        # Use local Whisper if available and requested, otherwise use API
        if use_local and WHISPER_LOCAL_AVAILABLE:
            transcript_text, segments = transcribe_audio_local_whisper(
                tmp_audio_path,
                progress_callback=progress_callback
            )
        else:
            if not api_key:
                raise Exception("❌ API key is required when using OpenAI API. Please provide your API key in the sidebar or enable local Whisper transcription.")
            transcript_text, segments = transcribe_audio_with_whisper(
                tmp_audio_path, 
                api_key,
                use_local=False,
                progress_callback=progress_callback
            )
        
        update_progress(0.9, "📝 Processing transcript...")
        
        # Step 3: Parse transcript
        parser = TranscriptParser()
        # Create a simple transcript format from Whisper output
        # Whisper doesn't identify speakers, so we'll create a single speaker transcript
        lines = transcript_text.split('\n')
        messages = []
        for line in lines:
            line = line.strip()
            if line:
                messages.append({
                    'speaker': 'Speaker',
                    'text': line,
                    'timestamp': None
                })
        
        update_progress(1.0, "✅ Transcription complete!")
        
        return messages, None
        
    except Exception as e:
        return None, str(e)
    finally:
        # Clean up temp files
        for path in [tmp_video_path, tmp_audio_path]:
            if path and os.path.exists(path):
                try:
                    os.unlink(path)
                except:
                    pass


def extract_requirements(messages, api_key, model, use_ollama=False, ollama_model="llama3.2", chunk_size=50, progress_callback=None):
    """
    Extract requirements from parsed messages.
    Processes in chunks and generates incremental reports.
    
    Args:
        messages: List of message dictionaries
        api_key: API key for OpenAI (if not using Ollama)
        model: Model name for OpenAI
        use_ollama: Whether to use Ollama
        ollama_model: Ollama model name
        chunk_size: Number of messages to process at a time
        progress_callback: Function to call with (progress, message) updates
    """
    try:
        extractor = RequirementsExtractor(
            api_key=api_key, 
            model=model,
            use_ollama=use_ollama,
            ollama_model=ollama_model
        )
        
        # If messages are small, process all at once
        if len(messages) <= chunk_size:
            if progress_callback:
                progress_callback(0.5, "🤖 Extracting requirements from transcript...")
            requirements = extractor.extract_requirements(messages)
            if progress_callback:
                progress_callback(1.0, "✅ Requirements extracted!")
            return requirements, None
        
        # For large transcripts, process in chunks
        total_chunks = (len(messages) + chunk_size - 1) // chunk_size
        all_requirements = {
            'functional_requirements': [],
            'non_functional_requirements': [],
            'business_rules': [],
            'action_items': [],
            'decisions': [],
            'stakeholders': []
        }
        
        for i in range(total_chunks):
            start_idx = i * chunk_size
            end_idx = min((i + 1) * chunk_size, len(messages))
            chunk_messages = messages[start_idx:end_idx]
            
            if progress_callback:
                progress = (i / total_chunks) * 0.9
                progress_callback(progress, f"🤖 Extracting requirements from chunk {i+1}/{total_chunks} ({len(chunk_messages)} messages)...")
            
            # Extract requirements for this chunk
            chunk_requirements = extractor.extract_requirements(chunk_messages)
            
            # Merge requirements
            for key in all_requirements.keys():
                if chunk_requirements.get(key):
                    all_requirements[key].extend(chunk_requirements[key])
            
            # Update session state with partial results
            if 'partial_requirements' in st.session_state:
                st.session_state.partial_requirements.append({
                    'chunk': i + 1,
                    'total_chunks': total_chunks,
                    'requirements': chunk_requirements,
                    'timestamp': datetime.now().isoformat()
                })
        
        if progress_callback:
            progress_callback(0.95, "📊 Combining all requirements...")
        
        # Deduplicate and merge requirements
        # Remove duplicates based on description
        seen_descriptions = set()
        for key in ['functional_requirements', 'non_functional_requirements', 'business_rules']:
            if all_requirements.get(key):
                unique_items = []
                for item in all_requirements[key]:
                    desc = item.get('description', item.get('rule', ''))
                    if desc and desc not in seen_descriptions:
                        seen_descriptions.add(desc)
                        unique_items.append(item)
                all_requirements[key] = unique_items
        
        # Merge stakeholders (by name)
        if all_requirements.get('stakeholders'):
            stakeholders_dict = {}
            for stakeholder in all_requirements['stakeholders']:
                name = stakeholder.get('name', 'Unknown')
                if name not in stakeholders_dict:
                    stakeholders_dict[name] = stakeholder
                else:
                    # Merge roles and interests
                    existing = stakeholders_dict[name]
                    if stakeholder.get('role') and not existing.get('role'):
                        existing['role'] = stakeholder['role']
                    if stakeholder.get('interests') and not existing.get('interests'):
                        existing['interests'] = stakeholder['interests']
            all_requirements['stakeholders'] = list(stakeholders_dict.values())
        
        if progress_callback:
            progress_callback(1.0, "✅ All requirements extracted and combined!")
        
        return all_requirements, None
        
    except Exception as e:
        return None, str(e)


def main():
    """Main application."""
    initialize_session_state()
    
    # Header
    st.markdown('<div class="main-header">📋 Requirements Extractor</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Extract structured requirements from Teams meeting transcripts</div>', unsafe_allow_html=True)
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Transcription method selection
        transcription_method = st.radio(
            "Transcription Method",
            options=["Local Whisper (No API Key)", "OpenAI API (Requires Key)"],
            index=0 if WHISPER_LOCAL_AVAILABLE else 1,
            help="Local Whisper runs on your computer (free, no API key). OpenAI API is faster but requires an API key."
        )
        st.session_state.use_local_whisper = (transcription_method == "Local Whisper (No API Key)")
        
        # Requirements extraction method
        extraction_method = st.radio(
            "Requirements Extraction Method",
            options=["Ollama (Local, No API Key)", "OpenAI API (Requires Key)"],
            index=0,
            help="Ollama runs locally (free, no API key). OpenAI API is faster but requires an API key."
        )
        st.session_state.use_ollama = (extraction_method == "Ollama (Local, No API Key)")
        
        # API Key input (only needed for OpenAI)
        if st.session_state.use_ollama:
            st.info("✅ Using Ollama for requirements extraction - no API key needed!")
            st.session_state.api_key = None
            
            # Ollama model selection
            ollama_model = st.text_input(
                "Ollama Model Name",
                value=st.session_state.get('ollama_model', 'llama3.2'),
                help="Name of the Ollama model to use (e.g., llama3.2, mistral, codellama). Make sure you've pulled it: ollama pull <model-name>"
            )
            st.session_state.ollama_model = ollama_model
        else:
            if st.session_state.use_local_whisper:
                st.info("💡 Using local Whisper for transcription (no API key needed for transcription)")
                api_key_input = st.text_input(
                    "OpenAI API Key (for Requirements Extraction)",
                    type="password",
                    help="Required for requirements extraction using GPT models. Transcription uses local Whisper (no key needed).",
                    value=st.session_state.get('api_key', '')
                )
            else:
                api_key_input = st.text_input(
                    "OpenAI API Key",
                    type="password",
                    help="Enter your OpenAI API key or leave empty to use OPENAI_API_KEY environment variable",
                    value=st.session_state.get('api_key', '')
                )
            st.session_state.api_key = api_key_input if api_key_input else None
            
            # Model selection (only for OpenAI)
            model = st.selectbox(
                "OpenAI Model",
                options=["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"],
                index=0,
                help="Select the OpenAI model to use for extraction"
            )
            st.session_state.model = model
        
        st.divider()
        
        # Instructions
        st.header("📖 How to Use")
        st.markdown("""
        1. **Upload a file** (transcript or video) or paste text
        2. **Configure** your API key and model
        3. **Click Extract** to process
        4. **Review** and download results
        
        **Supported formats:**
        - Text files (.txt)
        - WebVTT files (.vtt)
        - JSON files (.json)
        - Video files (.mp4, .mov, .avi, .mkv)
        """)
        
        st.divider()
        
        # Example format
        st.header("📝 Example Format")
        st.code("""
Speaker Name: Message text here
Another Speaker: Another message
        """, language="text")
    
    # Main content area
    tab1, tab2 = st.tabs(["📁 Upload File", "📝 Paste Text"])
    
    with tab1:
        st.subheader("Upload File")
        uploaded_file = st.file_uploader(
            "Choose a transcript file or video file",
            type=['txt', 'vtt', 'json', 'mp4', 'mov', 'avi', 'mkv', 'webm'],
            help="Upload a Teams meeting transcript file or video recording"
        )
        
        if uploaded_file is not None:
            file_extension = Path(uploaded_file.name).suffix.lower()
            is_video = file_extension in ['.mp4', '.mov', '.avi', '.mkv', '.webm']
            
            if is_video:
                st.success(f"✅ Video file uploaded: {uploaded_file.name}")
                file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
                st.info(f"📹 File size: {file_size_mb:.2f} MB")
                st.info("💡 Large files will be automatically chunked for processing.")
            else:
                st.success(f"✅ File uploaded: {uploaded_file.name}")
                
                # Show file preview for text files
                with st.expander("📄 Preview File Content"):
                    try:
                        content = uploaded_file.read().decode('utf-8')
                        st.text_area("File content", content, height=200, disabled=True)
                        uploaded_file.seek(0)  # Reset file pointer
                    except:
                        st.info("Preview not available for this file type")
                        uploaded_file.seek(0)  # Reset file pointer
    
    with tab2:
        st.subheader("Paste Transcript Text")
        transcript_text = st.text_area(
            "Enter transcript text",
            height=300,
            placeholder="Speaker Name: Message text here\nAnother Speaker: Another message",
            help="Paste your transcript text here. Use format: 'Speaker: message' or '[Speaker] message'"
        )
        st.session_state.transcript_text = transcript_text
    
    # Extract button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        extract_button = st.button(
            "🚀 Extract Requirements",
            type="primary",
            use_container_width=True,
            disabled=(uploaded_file is None and not st.session_state.transcript_text)
        )
    
    # Processing
    if extract_button:
        # Get settings
        use_local = st.session_state.get('use_local_whisper', False)
        use_ollama = st.session_state.get('use_ollama', False)
        api_key = None
        
        # API key only needed if using OpenAI for extraction
        if not use_ollama:
            api_key = st.session_state.api_key or os.getenv('OPENAI_API_KEY')
            if not api_key:
                if use_local:
                    st.error("❌ Please provide an OpenAI API key in the sidebar for requirements extraction, or switch to Ollama (Local, No API Key).")
                else:
                    st.error("❌ Please provide an OpenAI API key in the sidebar or set OPENAI_API_KEY environment variable, or switch to Ollama (Local, No API Key).")
                st.stop()
        
        # Get model settings
        if use_ollama:
            ollama_model = st.session_state.get('ollama_model', 'llama3.2')
            model = None  # Not used for Ollama
        else:
            model = st.session_state.get('model', 'gpt-4o-mini')
            ollama_model = None
        
        # Check if it's a video file
        is_video_file = False
        if uploaded_file:
            file_extension = Path(uploaded_file.name).suffix.lower()
            is_video_file = file_extension in ['.mp4', '.mov', '.avi', '.mkv', '.webm']
        
        # Process video or transcript
        if is_video_file:
            # Process video file
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                if not MOVIEPY_AVAILABLE:
                    st.error("❌ moviepy is required for video processing. Please install it: `pip3 install moviepy`")
                    st.stop()
                
                status_text.info("🎬 Processing video file...")
                use_local = st.session_state.get('use_local_whisper', False)
                messages, error = process_video_file(uploaded_file, api_key, progress_bar, status_text, use_local=use_local)
                
                if error:
                    st.error(f"❌ Error processing video: {error}")
                    # Show full error details in an expander
                    with st.expander("🔍 View Full Error Details (for debugging)"):
                        st.code(error, language="text")
                        st.info("💡 Copy this error message and share it for debugging")
                    st.stop()
                
                if not messages:
                    st.warning("⚠️ No transcript generated from video")
                    st.stop()
                
                progress_bar.progress(1.0)
                status_text.success(f"✅ Generated transcript with {len(messages)} segments")
                st.session_state.messages_parsed = messages
                
            except Exception as e:
                error_msg = str(e)
                st.error(f"❌ Error: {error_msg}")
                # Show full error details in an expander
                with st.expander("🔍 View Full Error Details (for debugging)"):
                    st.code(error_msg, language="text")
                    st.info("💡 Copy this error message and share it for debugging")
                st.stop()
            finally:
                # Keep progress bar visible briefly, then clear
                import time
                time.sleep(0.5)
                progress_bar.empty()
                status_text.empty()
        
        else:
            # Parse transcript
            with st.spinner("📖 Parsing transcript..."):
                if uploaded_file:
                    messages, error = parse_transcript_file(uploaded_file)
                elif st.session_state.transcript_text:
                    messages, error = parse_transcript_text(st.session_state.transcript_text)
                else:
                    st.error("❌ Please upload a file or paste transcript text")
                    st.stop()
                
                if error:
                    st.error(f"❌ Error parsing transcript: {error}")
                    st.stop()
                
                if not messages:
                    st.warning("⚠️ No messages found in transcript")
                    st.stop()
                
                st.session_state.messages_parsed = messages
                st.success(f"✅ Parsed {len(messages)} messages")
        
        # Extract requirements (incrementally for large transcripts)
        extraction_method_name = "Ollama (local)" if use_ollama else f"OpenAI ({model})"
        
        # Create progress tracking
        extraction_progress = st.progress(0)
        extraction_status = st.empty()
        results_container = st.container()
        
        def extraction_progress_callback(progress, message):
            """Update progress and show partial results."""
            extraction_progress.progress(progress)
            extraction_status.info(f"📊 {message}")
            
            # Show partial results if available
            if st.session_state.get('partial_requirements'):
                with results_container:
                    st.markdown("### 📋 Partial Results (Updated as chunks are processed)")
                    latest_chunk = st.session_state.partial_requirements[-1]
                    st.info(f"✅ Processed chunk {latest_chunk['chunk']}/{latest_chunk['total_chunks']}")
                    
                    # Show summary of latest chunk
                    chunk_req = latest_chunk['requirements']
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("FR", len(chunk_req.get('functional_requirements', [])))
                    with col2:
                        st.metric("NFR", len(chunk_req.get('non_functional_requirements', [])))
                    with col3:
                        st.metric("Action Items", len(chunk_req.get('action_items', [])))
                    with col4:
                        st.metric("Decisions", len(chunk_req.get('decisions', [])))
        
        # Clear previous partial results
        st.session_state.partial_requirements = []
        
        try:
            # Determine chunk size based on message count
            chunk_size = 50 if len(messages) > 100 else len(messages)
            
            requirements, error = extract_requirements(
                messages, 
                api_key, 
                model,
                use_ollama=use_ollama,
                ollama_model=ollama_model if use_ollama else None,
                chunk_size=chunk_size,
                progress_callback=extraction_progress_callback
            )
            
            if error:
                st.error(f"❌ Error extracting requirements: {error}")
                extraction_progress.empty()
                extraction_status.empty()
                st.stop()
            
            st.session_state.requirements = requirements
            extraction_progress.progress(1.0)
            extraction_status.success("✅ Requirements extracted successfully!")
            
            # Clear progress indicators after a moment
            import time
            time.sleep(1)
            extraction_progress.empty()
            extraction_status.empty()
            
        except Exception as e:
            error_msg = str(e)
            
            # Check if it's an Ollama-related error
            if "Ollama is not running" in error_msg or "Ollama" in error_msg:
                st.error("❌ Ollama is not running or not installed")
                with st.expander("📖 How to Install and Start Ollama"):
                    st.markdown("""
                    **Option 1: Install Ollama (Recommended for no API key)**
                    
                    1. **Install Ollama:**
                       ```bash
                       brew install ollama
                       ```
                       Or download from: https://ollama.ai
                    
                    2. **Start Ollama service:**
                       ```bash
                       ollama serve
                       ```
                       (It may start automatically after installation)
                    
                    3. **Pull a model:**
                       ```bash
                       ollama pull llama3.2
                       ```
                       (This downloads the model - may take a few minutes)
                    
                    **Option 2: Use OpenAI API instead**
                    
                    If you have an OpenAI API key, you can switch to "OpenAI API (Requires Key)" 
                    in the sidebar instead of using Ollama.
                    """)
            else:
                st.error(f"❌ Error extracting requirements: {error_msg}")
            
            extraction_progress.empty()
            extraction_status.empty()
            st.stop()
    
    # Display partial results if processing
    if st.session_state.get('partial_requirements') and not st.session_state.requirements:
        st.divider()
        st.header("📊 Processing in Progress...")
        st.info("🔄 Requirements are being extracted incrementally. Results will appear below as chunks are processed.")
        
        # Show latest chunk results
        if st.session_state.partial_requirements:
            latest = st.session_state.partial_requirements[-1]
            st.subheader(f"Latest Chunk ({latest['chunk']}/{latest['total_chunks']})")
            req = latest['requirements']
            
            col1, col2, col3, col4, col5, col6 = st.columns(6)
            with col1:
                st.metric("Functional", len(req.get('functional_requirements', [])))
            with col2:
                st.metric("Non-Functional", len(req.get('non_functional_requirements', [])))
            with col3:
                st.metric("Business Rules", len(req.get('business_rules', [])))
            with col4:
                st.metric("Action Items", len(req.get('action_items', [])))
            with col5:
                st.metric("Decisions", len(req.get('decisions', [])))
            with col6:
                st.metric("Stakeholders", len(req.get('stakeholders', [])))
    
    # Display final results
    if st.session_state.requirements:
        st.divider()
        st.header("📊 Extracted Requirements")
        
        # Summary statistics
        req = st.session_state.requirements
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        with col1:
            st.metric("Functional", len(req.get('functional_requirements', [])))
        with col2:
            st.metric("Non-Functional", len(req.get('non_functional_requirements', [])))
        with col3:
            st.metric("Business Rules", len(req.get('business_rules', [])))
        with col4:
            st.metric("Action Items", len(req.get('action_items', [])))
        with col5:
            st.metric("Decisions", len(req.get('decisions', [])))
        with col6:
            st.metric("Stakeholders", len(req.get('stakeholders', [])))
        
        # Detailed sections
        tabs = st.tabs([
            "📋 Functional Requirements",
            "⚙️ Non-Functional Requirements",
            "📜 Business Rules",
            "✅ Action Items",
            "🎯 Decisions",
            "👥 Stakeholders",
            "📄 Full Report"
        ])
        
        with tabs[0]:
            if req.get('functional_requirements'):
                for i, fr in enumerate(req['functional_requirements'], 1):
                    with st.expander(f"{fr.get('id', f'FR-{i:03d}')}: {fr.get('description', 'N/A')[:50]}..."):
                        st.write("**Description:**", fr.get('description', 'N/A'))
                        st.write("**Priority:**", fr.get('priority', 'Not specified'))
                        st.write("**Source:**", fr.get('speaker', 'Unknown'))
                        if fr.get('context'):
                            st.write("**Context:**", fr.get('context'))
            else:
                st.info("No functional requirements found")
        
        with tabs[1]:
            if req.get('non_functional_requirements'):
                for i, nfr in enumerate(req['non_functional_requirements'], 1):
                    with st.expander(f"{nfr.get('id', f'NFR-{i:03d}')}: {nfr.get('description', 'N/A')[:50]}..."):
                        st.write("**Description:**", nfr.get('description', 'N/A'))
                        st.write("**Priority:**", nfr.get('priority', 'Not specified'))
                        st.write("**Source:**", nfr.get('speaker', 'Unknown'))
                        if nfr.get('context'):
                            st.write("**Context:**", nfr.get('context'))
            else:
                st.info("No non-functional requirements found")
        
        with tabs[2]:
            if req.get('business_rules'):
                for i, rule in enumerate(req['business_rules'], 1):
                    with st.expander(f"{rule.get('id', f'BR-{i:03d}')}: {rule.get('description', rule.get('rule', 'N/A'))[:50]}..."):
                        st.write("**Rule:**", rule.get('description', rule.get('rule', 'N/A')))
                        st.write("**Source:**", rule.get('speaker', 'Unknown'))
            else:
                st.info("No business rules found")
        
        with tabs[3]:
            if req.get('action_items'):
                # Table view
                import pandas as pd
                df = pd.DataFrame(req['action_items'])
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No action items found")
        
        with tabs[4]:
            if req.get('decisions'):
                for i, decision in enumerate(req['decisions'], 1):
                    with st.expander(f"{decision.get('id', f'D-{i:03d}')}: {decision.get('decision', 'N/A')[:50]}..."):
                        st.write("**Decision:**", decision.get('decision', 'N/A'))
                        st.write("**Rationale:**", decision.get('rationale', 'N/A'))
                        st.write("**Decision Maker:**", decision.get('decision_maker', 'Unknown'))
            else:
                st.info("No decisions found")
        
        with tabs[5]:
            if req.get('stakeholders'):
                for stakeholder in req['stakeholders']:
                    with st.expander(stakeholder.get('name', 'Unknown')):
                        st.write("**Role:**", stakeholder.get('role', 'N/A'))
                        st.write("**Interests:**", stakeholder.get('interests', 'N/A'))
            else:
                st.info("No stakeholders identified")
        
        with tabs[6]:
            # Full markdown report
            formatter = RequirementsFormatter()
            markdown_report = formatter.format_markdown(st.session_state.requirements)
            st.markdown(markdown_report)
        
        # Download buttons
        st.divider()
        st.subheader("💾 Download Results")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Markdown download
            formatter = RequirementsFormatter()
            markdown_content = formatter.format_markdown(st.session_state.requirements)
            st.download_button(
                label="📄 Download as Markdown",
                data=markdown_content,
                file_name=f"requirements_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown",
                use_container_width=True
            )
        
        with col2:
            # JSON download
            json_content = json.dumps(st.session_state.requirements, indent=2, ensure_ascii=False)
            st.download_button(
                label="📊 Download as JSON",
                data=json_content,
                file_name=f"requirements_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )


# Streamlit automatically executes the script when run with 'streamlit run'
# Just call main() - Streamlit will handle the execution context
if __name__ == "__main__" or True:  # Always run in Streamlit
    try:
        main()
    except Exception as e:
        st.error(f"❌ Error loading application: {str(e)}")
        st.exception(e)
        st.info("Please check the terminal for more details or contact support.")

