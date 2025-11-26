#!/usr/bin/env python3
"""
Convert DESIGN_DOCUMENT.md to PDF using markdown2 or weasyprint.
"""

import sys
import os

def convert_with_weasyprint():
    """Convert markdown to PDF using weasyprint."""
    try:
        from weasyprint import HTML, CSS
        from markdown import markdown
        
        with open('DESIGN_DOCUMENT.md', 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        # Convert markdown to HTML
        html_content = markdown(md_content, extensions=['tables', 'fenced_code', 'toc'])
        
        # Add CSS styling
        css = CSS(string='''
            @page {
                size: A4;
                margin: 2cm;
            }
            body {
                font-family: 'Helvetica', 'Arial', sans-serif;
                line-height: 1.6;
                color: #333;
            }
            h1 {
                color: #1f77b4;
                border-bottom: 3px solid #1f77b4;
                padding-bottom: 10px;
            }
            h2 {
                color: #2c3e50;
                margin-top: 30px;
                border-bottom: 2px solid #ecf0f1;
                padding-bottom: 5px;
            }
            h3 {
                color: #34495e;
                margin-top: 20px;
            }
            code {
                background-color: #f4f4f4;
                padding: 2px 5px;
                border-radius: 3px;
                font-family: 'Courier New', monospace;
            }
            pre {
                background-color: #f4f4f4;
                padding: 15px;
                border-radius: 5px;
                overflow-x: auto;
            }
            table {
                border-collapse: collapse;
                width: 100%;
                margin: 20px 0;
            }
            th, td {
                border: 1px solid #ddd;
                padding: 12px;
                text-align: left;
            }
            th {
                background-color: #1f77b4;
                color: white;
            }
            tr:nth-child(even) {
                background-color: #f2f2f2;
            }
        ''')
        
        # Convert to PDF
        HTML(string=html_content).write_pdf('DESIGN_DOCUMENT.pdf', stylesheets=[css])
        print("✅ PDF created successfully: DESIGN_DOCUMENT.pdf")
        return True
        
    except ImportError:
        return False
    except Exception as e:
        print(f"❌ Error with weasyprint: {e}")
        return False

def convert_with_markdown_pdf():
    """Convert markdown to PDF using markdown-pdf."""
    try:
        import subprocess
        result = subprocess.run(
            ['npx', '--yes', 'markdown-pdf', 'DESIGN_DOCUMENT.md', '-o', 'DESIGN_DOCUMENT.pdf'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("✅ PDF created successfully: DESIGN_DOCUMENT.pdf")
            return True
        else:
            print(f"❌ Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("📄 Converting DESIGN_DOCUMENT.md to PDF...")
    print("")
    
    # Try weasyprint first
    print("Attempting conversion with weasyprint...")
    if convert_with_weasyprint():
        return
    
    # Try markdown-pdf
    print("Attempting conversion with markdown-pdf (requires Node.js)...")
    if convert_with_markdown_pdf():
        return
    
    # If both fail, provide instructions
    print("")
    print("❌ Automatic PDF conversion not available.")
    print("")
    print("📖 To convert to PDF, you can:")
    print("")
    print("Option 1: Install pandoc and convert manually:")
    print("  brew install pandoc basictex")
    print("  pandoc DESIGN_DOCUMENT.md -o DESIGN_DOCUMENT.pdf")
    print("")
    print("Option 2: Use an online converter:")
    print("  - Upload DESIGN_DOCUMENT.md to https://www.markdowntopdf.com/")
    print("  - Or use https://dillinger.io/ and export as PDF")
    print("")
    print("Option 3: Install Python packages and try again:")
    print("  pip install weasyprint markdown")
    print("  python3 convert_to_pdf.py")
    print("")
    print("Option 4: Use VS Code with Markdown PDF extension")
    print("  - Install 'Markdown PDF' extension in VS Code")
    print("  - Open DESIGN_DOCUMENT.md")
    print("  - Right-click → 'Markdown PDF: Export (pdf)'")
    print("")

if __name__ == '__main__':
    main()

