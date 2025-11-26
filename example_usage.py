#!/usr/bin/env python3
"""
Example usage of the Requirements Extractor
Demonstrates how to use the tool programmatically.
"""

from requirements_extractor import (
    TranscriptParser,
    RequirementsExtractor,
    RequirementsFormatter
)

def example_usage():
    """Example of using the extractor programmatically."""
    
    # Step 1: Parse transcript
    print("Parsing transcript...")
    parser = TranscriptParser()
    messages = parser.parse_text("example_transcript.txt")
    print(f"Parsed {len(messages)} messages")
    
    # Step 2: Extract requirements (requires OpenAI API key)
    print("\nExtracting requirements...")
    try:
        extractor = RequirementsExtractor()  # Uses OPENAI_API_KEY env var
        requirements = extractor.extract_requirements(messages)
        
        # Step 3: Format output
        print("\nFormatting output...")
        formatter = RequirementsFormatter()
        
        # Save as Markdown
        markdown_output = formatter.format_markdown(
            requirements,
            "example_output.md"
        )
        print("✓ Saved to example_output.md")
        
        # Save as JSON
        json_output = formatter.format_json(
            requirements,
            "example_output.json"
        )
        print("✓ Saved to example_output.json")
        
        # Print summary
        print("\n" + "="*50)
        print("EXTRACTION SUMMARY")
        print("="*50)
        print(f"Functional Requirements: {len(requirements.get('functional_requirements', []))}")
        print(f"Non-Functional Requirements: {len(requirements.get('non_functional_requirements', []))}")
        print(f"Business Rules: {len(requirements.get('business_rules', []))}")
        print(f"Action Items: {len(requirements.get('action_items', []))}")
        print(f"Decisions: {len(requirements.get('decisions', []))}")
        print(f"Stakeholders: {len(requirements.get('stakeholders', []))}")
        
    except ValueError as e:
        print(f"\nError: {e}")
        print("\nTo use this example:")
        print("1. Set your OpenAI API key: export OPENAI_API_KEY='your-key'")
        print("2. Or modify the code to pass api_key parameter")
    except Exception as e:
        print(f"\nError during extraction: {e}")

if __name__ == '__main__':
    example_usage()


