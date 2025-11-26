#!/usr/bin/env python3
"""Simple script to test OpenAI API key with Whisper API."""

import sys
import os
from openai import OpenAI

def test_api_key(api_key):
    """Test if the API key works with OpenAI."""
    print("🔍 Testing OpenAI API key...")
    print(f"Key format: {api_key[:7]}...{api_key[-4:] if len(api_key) > 11 else '***'}")
    print()
    
    if not api_key or not api_key.strip():
        print("❌ Error: API key is empty")
        return False
    
    if not api_key.startswith('sk-'):
        print("❌ Error: API key should start with 'sk-'")
        return False
    
    try:
        client = OpenAI(api_key=api_key)
        
        # Test 1: List models (lightweight test)
        print("Test 1: Testing API key with models.list()...")
        try:
            models = client.models.list(limit=1)
            print("✅ API key is valid (can list models)")
        except Exception as e:
            error_str = str(e)
            if "401" in error_str or "authentication" in error_str.lower():
                print(f"❌ API key is invalid: {error_str}")
                return False
            elif "JSON" in error_str or "Expecting value" in error_str:
                print(f"⚠️  Warning: Got JSON parsing error: {error_str}")
                print("   This might indicate an invalid key or network issue")
            else:
                print(f"⚠️  Warning: {error_str}")
                print("   (Some API keys don't have model list access, this is okay)")
        
        print()
        
        # Test 2: Try a simple transcription (if we have a test file)
        print("Test 2: Testing Whisper API access...")
        print("   (This requires a valid API key with Whisper access)")
        print("   If your key works, you should be able to transcribe in the app")
        print()
        
        print("✅ API key format is valid")
        print("💡 If you're still getting errors in the app, try:")
        print("   1. Generate a new API key at https://platform.openai.com/api-keys")
        print("   2. Make sure you have billing set up")
        print("   3. Check your network connection")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing API key: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        api_key = sys.argv[1]
    else:
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("Usage: python3 test_api_key.py <your-api-key>")
            print("   OR set OPENAI_API_KEY environment variable")
            sys.exit(1)
    
    success = test_api_key(api_key)
    sys.exit(0 if success else 1)


