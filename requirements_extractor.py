#!/usr/bin/env python3
"""
Requirements Extractor from Teams Meeting Transcripts
Extracts and structures requirements from Microsoft Teams meeting discussions.
"""

import json
import re
import argparse
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import openai
from openai import OpenAI


class TranscriptParser:
    """Parse different transcript formats from Teams meetings."""
    
    @staticmethod
    def parse_text(transcript_path: str) -> List[Dict[str, Any]]:
        """Parse plain text transcript file."""
        with open(transcript_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Try to extract speaker and text patterns
        # Common formats: "Speaker Name: text" or "[Speaker] text"
        lines = content.split('\n')
        messages = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Pattern: "Speaker: message"
            match = re.match(r'^([^:]+):\s*(.+)$', line)
            if match:
                speaker, text = match.groups()
                messages.append({
                    'speaker': speaker.strip(),
                    'text': text.strip(),
                    'timestamp': None
                })
            # Pattern: "[Speaker] message"
            elif re.match(r'^\[([^\]]+)\]\s*(.+)$', line):
                match = re.match(r'^\[([^\]]+)\]\s*(.+)$', line)
                speaker, text = match.groups()
                messages.append({
                    'speaker': speaker.strip(),
                    'text': text.strip(),
                    'timestamp': None
                })
            else:
                # Assume continuation or standalone message
                if messages:
                    messages[-1]['text'] += ' ' + line
                else:
                    messages.append({
                        'speaker': 'Unknown',
                        'text': line,
                        'timestamp': None
                    })
        
        return messages
    
    @staticmethod
    def parse_vtt(transcript_path: str) -> List[Dict[str, Any]]:
        """Parse WebVTT format transcript."""
        with open(transcript_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        messages = []
        lines = content.split('\n')
        current_cue = None
        current_text = []
        
        for line in lines:
            line = line.strip()
            
            # Skip VTT header and empty lines
            if not line or line.startswith('WEBVTT') or line.startswith('NOTE'):
                continue
            
            # Timestamp line (e.g., "00:00:10.000 --> 00:00:15.000")
            if '-->' in line:
                if current_cue and current_text:
                    messages.append({
                        'speaker': current_cue.get('speaker', 'Unknown'),
                        'text': ' '.join(current_text),
                        'timestamp': current_cue.get('timestamp')
                    })
                current_cue = {'timestamp': line}
                current_text = []
            # Speaker identification (often in brackets or as first part)
            elif line.startswith('<v ') or line.startswith('['):
                if current_text:
                    current_text.append(line)
            else:
                # Extract speaker if in format <v Speaker>text</v>
                speaker_match = re.match(r'<v\s+([^>]+)>(.+)</v>', line)
                if speaker_match:
                    speaker, text = speaker_match.groups()
                    current_cue['speaker'] = speaker.strip()
                    current_text.append(text.strip())
                else:
                    current_text.append(line)
        
        # Add last message
        if current_cue and current_text:
            messages.append({
                'speaker': current_cue.get('speaker', 'Unknown'),
                'text': ' '.join(current_text),
                'timestamp': current_cue.get('timestamp')
            })
        
        return messages
    
    @staticmethod
    def parse_json(transcript_path: str) -> List[Dict[str, Any]]:
        """Parse JSON format transcript (Teams export format)."""
        with open(transcript_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        messages = []
        
        # Handle different JSON structures
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    messages.append({
                        'speaker': item.get('speaker', item.get('name', 'Unknown')),
                        'text': item.get('text', item.get('content', '')),
                        'timestamp': item.get('timestamp', item.get('time'))
                    })
        elif isinstance(data, dict):
            # Check for common structures
            if 'transcript' in data:
                return TranscriptParser.parse_json_items(data['transcript'])
            elif 'items' in data:
                return TranscriptParser.parse_json_items(data['items'])
            else:
                # Try to extract from any list in the dict
                for key, value in data.items():
                    if isinstance(value, list):
                        return TranscriptParser.parse_json_items(value)
        
        return messages
    
    @staticmethod
    def parse_json_items(items: List[Dict]) -> List[Dict[str, Any]]:
        """Helper to parse JSON items."""
        messages = []
        for item in items:
            messages.append({
                'speaker': item.get('speaker', item.get('name', item.get('user', 'Unknown'))),
                'text': item.get('text', item.get('content', item.get('message', ''))),
                'timestamp': item.get('timestamp', item.get('time', item.get('startTime')))
            })
        return messages


class RequirementsExtractor:
    """Extract requirements from meeting transcripts using AI."""
    
    def __init__(self, api_key: str = None, model: str = "gpt-4o-mini", use_ollama: bool = False, ollama_model: str = "llama3.2"):
        """
        Initialize the extractor.
        
        Args:
            api_key: OpenAI API key. If None, will try to get from environment.
            model: Model to use for extraction (default: gpt-4o-mini)
            use_ollama: If True, use Ollama local LLM instead of OpenAI
            ollama_model: Ollama model name (default: llama3.2)
        """
        self.use_ollama = use_ollama
        self.ollama_model = ollama_model
        
        if use_ollama:
            # Check if Ollama is available
            try:
                import requests
                try:
                    response = requests.get("http://localhost:11434/api/tags", timeout=3)
                    if response.status_code == 200:
                        self.ollama_available = True
                        # Check if the specified model is available
                        models_data = response.json()
                        available_models = [model.get('name', '').split(':')[0] for model in models_data.get('models', [])]
                        if ollama_model and ollama_model not in available_models:
                            # Model not found, but Ollama is running - warn but continue
                            print(f"⚠️ Warning: Model '{ollama_model}' not found in Ollama. Available models: {', '.join(available_models) if available_models else 'none'}")
                            print(f"💡 Run: ollama pull {ollama_model}")
                    else:
                        self.ollama_available = False
                except requests.exceptions.ConnectionError:
                    self.ollama_available = False
                except requests.exceptions.Timeout:
                    self.ollama_available = False
            except ImportError:
                raise ValueError(
                    "The 'requests' library is required for Ollama support.\n"
                    "Install it with: pip install requests"
                )
            except Exception as e:
                self.ollama_available = False
            
            if not self.ollama_available:
                # Provide detailed installation instructions
                install_instructions = (
                    "Ollama is not running or not installed.\n\n"
                    "📥 To install Ollama:\n"
                    "  macOS: brew install ollama\n"
                    "  Linux: curl -fsSL https://ollama.ai/install.sh | sh\n"
                    "  Windows: Download from https://ollama.ai\n\n"
                    "🚀 To start Ollama:\n"
                    "  macOS/Linux: ollama serve\n"
                    "  (Or it may start automatically after installation)\n\n"
                    "📦 To pull a model:\n"
                    f"  ollama pull {ollama_model}\n\n"
                    "💡 Alternative: Switch to 'OpenAI API' in the sidebar if you have an API key."
                )
                raise ValueError(install_instructions)
        else:
            if api_key:
                self.client = OpenAI(api_key=api_key)
            else:
                try:
                    self.client = OpenAI()
                except Exception as e:
                    raise ValueError(
                        "OpenAI API key not found. Please set OPENAI_API_KEY environment variable "
                        "or pass api_key parameter, or use Ollama (use_ollama=True)."
                    )
        self.model = model
    
    def extract_requirements(self, messages: List[Dict[str, Any]], feedback: str = None) -> Dict[str, Any]:
        """
        Extract requirements from transcript messages.
        
        Args:
            messages: List of message dictionaries with speaker and text
            feedback: Optional feedback or corrections to incorporate into extraction
            
        Returns:
            Dictionary containing extracted requirements
        """
        # Combine messages into conversation text
        conversation = self._format_conversation(messages)
        
        # Create prompt for requirement extraction
        prompt = self._create_extraction_prompt(conversation, feedback)
        
        # Call API (OpenAI or Ollama)
        try:
            if self.use_ollama:
                # Use Ollama local LLM
                import requests
                
                system_prompt = """You are an expert business analyst who extracts requirements from meeting discussions. 
Extract functional requirements, non-functional requirements, constraints, assumptions, and action items. Return structured JSON.

IMPORTANT: Correct common transcription errors:
- "Pyo number" or "P.O. number" should be "PO number" (Purchase Order number)
- "sublatures" or "subletters" should be "suppliers"
- Always use standard business terminology in extracted requirements."""
                
                full_prompt = f"{system_prompt}\n\n{prompt}\n\nIMPORTANT: Return ONLY valid JSON, no other text."
                
                response = requests.post(
                    "http://localhost:11434/api/generate",
                    json={
                        "model": self.ollama_model,
                        "prompt": full_prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.3
                        }
                    },
                    timeout=300  # 5 minutes timeout for large transcripts
                )
                
                if response.status_code != 200:
                    raise Exception(f"Ollama API error: {response.status_code} - {response.text}")
                
                result_text = response.json().get("response", "")
                
                # Try to extract JSON from response (Ollama might add extra text)
                json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                else:
                    # Try parsing the whole response
                    result = json.loads(result_text)
                
                return result
            else:
                # Use OpenAI API
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an expert business analyst who extracts requirements from meeting discussions. Extract functional requirements, non-functional requirements, constraints, assumptions, and action items. Return structured JSON.\n\nIMPORTANT: Correct common transcription errors:\n- \"Pyo number\" or \"P.O. number\" should be \"PO number\" (Purchase Order number)\n- \"sublatures\" or \"subletters\" should be \"suppliers\"\n- Always use standard business terminology in extracted requirements."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.3
                )
                
                result = json.loads(response.choices[0].message.content)
                return result
            
        except json.JSONDecodeError as e:
            raise Exception(f"Error parsing JSON response: {str(e)}\n\nResponse was: {result_text[:500] if 'result_text' in locals() else 'N/A'}")
        except Exception as e:
            raise Exception(f"Error extracting requirements: {str(e)}")
    
    def _clean_transcript_text(self, text: str) -> str:
        """Clean and correct common speech-to-text transcription errors."""
        if not text:
            return text
        
        # Common business term corrections
        corrections = {
            # PO number corrections
            r'\b(Pyo|PYO|p\.o\.|P\.O\.)\s+number\b': 'PO number',
            r'\b(Pyo|PYO)\s+Number\b': 'PO Number',
            r'\b(Pyo|PYO)\b(?=\s*(number|Number))': 'PO',
            
            # Supplier corrections
            r'\bsublatures\b': 'suppliers',
            r'\bsublature\b': 'supplier',
            r'\bSublatures\b': 'Suppliers',
            r'\bSublature\b': 'Supplier',
            r'\bsubletters\b': 'suppliers',
            r'\bsubletter\b': 'supplier',
            
            # Common abbreviations
            r'\bS\.O\.W\.\b': 'SOW',
            r'\bR\.F\.P\.\b': 'RFP',
            r'\bP\.O\.\b': 'PO',
            
            # Common word corrections in business context
            r'\bforcast\b': 'forecast',
            r'\bforcasting\b': 'forecasting',
        }
        
        cleaned = text
        for pattern, replacement in corrections.items():
            cleaned = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE)
        
        return cleaned
    
    def _format_conversation(self, messages: List[Dict[str, Any]]) -> str:
        """Format messages into a readable conversation."""
        formatted = []
        for msg in messages:
            speaker = msg.get('speaker', 'Unknown')
            text = msg.get('text', '')
            # Clean transcription errors
            text = self._clean_transcript_text(text)
            timestamp = msg.get('timestamp', '')
            
            if timestamp:
                formatted.append(f"[{timestamp}] {speaker}: {text}")
            else:
                formatted.append(f"{speaker}: {text}")
        
        return '\n'.join(formatted)
    
    def _create_extraction_prompt(self, conversation: str, feedback: str = None) -> str:
        """Create prompt for requirement extraction."""
        feedback_section = ""
        if feedback and feedback.strip():
            feedback_section = f"""

**USER FEEDBACK AND CORRECTIONS:**
{feedback}

Please incorporate this feedback into your extraction:
- Apply any corrections mentioned in the feedback
- Focus on areas highlighted in the feedback
- Adjust extraction based on user guidance
"""
        
        return f"""Analyze the following meeting transcript and extract all requirements, decisions, and action items.{feedback_section}

**IMPORTANT: Business Terminology Context**
- "PO number" or "P.O. number" refers to Purchase Order number
- "supplier" or "vendor" refers to external suppliers/vendors (NOT "sublatures", "subletters", or similar)
- Correct any speech-to-text transcription errors in business terms
- Recognize common business abbreviations: PO (Purchase Order), SOW (Statement of Work), RFP (Request for Proposal), etc.

Meeting Transcript:
{conversation}

Please extract and structure the following information in JSON format:
1. **Functional Requirements**: Features, functionalities, and capabilities discussed
2. **Non-Functional Requirements**: Performance, security, usability, scalability requirements
3. **Business Rules**: Rules, constraints, and business logic mentioned (including PO numbers, supplier requirements, etc.)
4. **Assumptions**: Any assumptions made during the discussion
5. **Action Items**: Tasks assigned with owners and deadlines if mentioned
6. **Decisions**: Key decisions made during the meeting
7. **Stakeholders**: People mentioned and their roles/interests (including suppliers, vendors, partners)

**Terminology Guidelines:**
- Always use "PO number" or "Purchase Order number" (never "Pyo number", "P.O.", etc.)
- Always use "supplier" or "vendor" (never "sublatures", "subletters", etc.)
- Correct common speech-to-text errors in business terminology
- Preserve exact numbers, codes, and identifiers mentioned

For each requirement, include:
- ID (auto-generated)
- Description (with corrected business terminology)
- Priority (if mentioned: High/Medium/Low)
- Source speaker
- Related discussion context

Return the result as a JSON object with the following structure:
{{
  "functional_requirements": [
    {{
      "id": "FR-001",
      "description": "...",
      "priority": "High/Medium/Low",
      "speaker": "...",
      "context": "..."
    }}
  ],
  "non_functional_requirements": [...],
  "business_rules": [...],
  "assumptions": [...],
  "action_items": [
    {{
      "id": "AI-001",
      "task": "...",
      "owner": "...",
      "deadline": "...",
      "status": "Open"
    }}
  ],
  "decisions": [
    {{
      "id": "D-001",
      "decision": "...",
      "rationale": "...",
      "decision_maker": "..."
    }}
  ],
  "stakeholders": [
    {{
      "name": "...",
      "role": "...",
      "interests": "..."
    }}
  ]
}}"""


class RequirementsFormatter:
    """Format extracted requirements into readable output."""
    
    @staticmethod
    def format_markdown(requirements: Dict[str, Any], output_path: str = None) -> str:
        """Format requirements as Markdown."""
        md = []
        md.append("# Requirements Extracted from Meeting\n")
        md.append(f"*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
        md.append("---\n")
        
        # Functional Requirements
        if requirements.get('functional_requirements'):
            md.append("## Functional Requirements\n")
            for req in requirements['functional_requirements']:
                md.append(f"### {req.get('id', 'N/A')}\n")
                md.append(f"**Description:** {req.get('description', 'N/A')}\n")
                md.append(f"**Priority:** {req.get('priority', 'Not specified')}\n")
                md.append(f"**Source:** {req.get('speaker', 'Unknown')}\n")
                if req.get('context'):
                    md.append(f"**Context:** {req.get('context')}\n")
                md.append("\n")
        
        # Non-Functional Requirements
        if requirements.get('non_functional_requirements'):
            md.append("## Non-Functional Requirements\n")
            for req in requirements['non_functional_requirements']:
                md.append(f"### {req.get('id', 'N/A')}\n")
                md.append(f"**Description:** {req.get('description', 'N/A')}\n")
                md.append(f"**Priority:** {req.get('priority', 'Not specified')}\n")
                md.append(f"**Source:** {req.get('speaker', 'Unknown')}\n")
                if req.get('context'):
                    md.append(f"**Context:** {req.get('context')}\n")
                md.append("\n")
        
        # Business Rules
        if requirements.get('business_rules'):
            md.append("## Business Rules\n")
            for rule in requirements['business_rules']:
                md.append(f"### {rule.get('id', 'N/A')}\n")
                md.append(f"**Rule:** {rule.get('description', rule.get('rule', 'N/A'))}\n")
                md.append(f"**Source:** {rule.get('speaker', 'Unknown')}\n")
                md.append("\n")
        
        # Assumptions
        if requirements.get('assumptions'):
            md.append("## Assumptions\n")
            for assumption in requirements['assumptions']:
                md.append(f"- **{assumption.get('id', 'N/A')}:** {assumption.get('description', assumption.get('assumption', 'N/A'))}\n")
        
        # Action Items
        if requirements.get('action_items'):
            md.append("\n## Action Items\n")
            md.append("| ID | Task | Owner | Deadline | Status |\n")
            md.append("|----|------|-------|----------|--------|\n")
            for item in requirements['action_items']:
                md.append(f"| {item.get('id', 'N/A')} | {item.get('task', 'N/A')} | {item.get('owner', 'TBD')} | {item.get('deadline', 'TBD')} | {item.get('status', 'Open')} |\n")
        
        # Decisions
        if requirements.get('decisions'):
            md.append("\n## Decisions\n")
            for decision in requirements['decisions']:
                md.append(f"### {decision.get('id', 'N/A')}\n")
                md.append(f"**Decision:** {decision.get('decision', 'N/A')}\n")
                md.append(f"**Rationale:** {decision.get('rationale', 'N/A')}\n")
                md.append(f"**Decision Maker:** {decision.get('decision_maker', 'Unknown')}\n")
                md.append("\n")
        
        # Stakeholders
        if requirements.get('stakeholders'):
            md.append("## Stakeholders\n")
            for stakeholder in requirements['stakeholders']:
                md.append(f"### {stakeholder.get('name', 'Unknown')}\n")
                md.append(f"**Role:** {stakeholder.get('role', 'N/A')}\n")
                md.append(f"**Interests:** {stakeholder.get('interests', 'N/A')}\n")
                md.append("\n")
        
        result = '\n'.join(md)
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(result)
        
        return result
    
    @staticmethod
    def format_json(requirements: Dict[str, Any], output_path: str = None) -> str:
        """Format requirements as JSON."""
        json_str = json.dumps(requirements, indent=2, ensure_ascii=False)
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(json_str)
        
        return json_str


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Extract requirements from Teams meeting transcripts'
    )
    parser.add_argument(
        'transcript',
        type=str,
        help='Path to transcript file (supports .txt, .vtt, .json)'
    )
    parser.add_argument(
        '-o', '--output',
        type=str,
        default=None,
        help='Output file path (default: requirements_<timestamp>.md)'
    )
    parser.add_argument(
        '-f', '--format',
        choices=['markdown', 'json', 'both'],
        default='markdown',
        help='Output format (default: markdown)'
    )
    parser.add_argument(
        '--api-key',
        type=str,
        default=None,
        help='OpenAI API key (or set OPENAI_API_KEY env var)'
    )
    parser.add_argument(
        '--model',
        type=str,
        default='gpt-4o-mini',
        help='OpenAI model to use (default: gpt-4o-mini)'
    )
    
    args = parser.parse_args()
    
    # Parse transcript
    transcript_path = Path(args.transcript)
    if not transcript_path.exists():
        print(f"Error: Transcript file not found: {args.transcript}")
        return 1
    
    print(f"Parsing transcript: {args.transcript}")
    parser = TranscriptParser()
    
    if transcript_path.suffix.lower() == '.vtt':
        messages = parser.parse_vtt(str(transcript_path))
    elif transcript_path.suffix.lower() == '.json':
        messages = parser.parse_json(str(transcript_path))
    else:
        messages = parser.parse_text(str(transcript_path))
    
    print(f"Parsed {len(messages)} messages from transcript")
    
    # Extract requirements
    print("Extracting requirements using AI...")
    extractor = RequirementsExtractor(api_key=args.api_key, model=args.model)
    requirements = extractor.extract_requirements(messages)
    
    # Format output
    formatter = RequirementsFormatter()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if args.format in ['markdown', 'both']:
        output_path = args.output or f"requirements_{timestamp}.md"
        formatter.format_markdown(requirements, output_path)
        print(f"Requirements saved to: {output_path}")
    
    if args.format in ['json', 'both']:
        json_output = args.output or f"requirements_{timestamp}.json"
        if args.format == 'both':
            json_output = json_output.replace('.md', '.json')
        formatter.format_json(requirements, json_output)
        print(f"JSON requirements saved to: {json_output}")
    
    print("\nExtraction complete!")
    return 0


if __name__ == '__main__':
    exit(main())

