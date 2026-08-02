#!/usr/bin/env python3
"""
Astrological Reading PDF Report Generator.

Converts Markdown astrological reading reports into styled, publication-grade PDF documents
using HTML5 + CSS3 and Chrome headless rendering.
"""

import os
import sys
import re
import argparse
import subprocess


def markdown_to_html(md_content: str, title: str = "Western Astrology Reading") -> str:
    """Converts Markdown text into styled HTML with custom typography and CSS styling."""
    html_lines = []
    in_list = False
    
    lines = md_content.split("\n")
    for line in lines:
        stripped = line.strip()
        
        # Headers
        if stripped.startswith("# "):
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append(f'<h1 class="report-title">{stripped[2:]}</h1>')
            continue
        elif stripped.startswith("## "):
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append(f'<h2 class="section-title">{stripped[3:]}</h2>')
            continue
        elif stripped.startswith("### "):
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append(f'<h3 class="subsection-title">{stripped[4:]}</h3>')
            continue

        # Bullet lists
        if stripped.startswith("- ") or stripped.startswith("* "):
            if not in_list:
                html_lines.append('<ul class="report-list">')
                in_list = True
            content = stripped[2:]
            # Format bold text in list items
            content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', content)
            html_lines.append(f'  <li>{content}</li>')
            continue

        if in_list and not stripped.startswith("- ") and not stripped.startswith("* "):
            html_lines.append("</ul>")
            in_list = False

        if not stripped:
            continue

        # Day-in-the-Life Callout Box
        if "Day-in-the-Life Reality" in stripped:
            content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', stripped)
            html_lines.append(f'<div class="callout-box"><div class="callout-header">💡 Day-in-the-Life Reality</div><p>{content}</p></div>')
            continue

        # Standard Paragraphs
        content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', stripped)
        html_lines.append(f'<p class="report-p">{content}</p>')

    if in_list:
        html_lines.append("</ul>")

    body_html = "\n".join(html_lines)

    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700&family=Inter:wght@300;400;500;600;700&display=swap');

        @page {{
            size: A4;
            margin: 20mm 15mm 20mm 15mm;
        }}

        body {{
            font-family: 'Inter', system-ui, -apple-system, sans-serif;
            color: #1e293b;
            line-height: 1.65;
            background-color: #ffffff;
            margin: 0;
            padding: 20px;
            font-size: 10.5pt;
        }}

        .header-banner {{
            border-bottom: 3px double #3b82f6;
            padding-bottom: 12px;
            margin-bottom: 25px;
            text-align: center;
        }}

        .report-title {{
            font-family: 'Cinzel', serif;
            color: #0f172a;
            font-size: 22pt;
            margin: 0 0 8px 0;
            letter-spacing: 0.5px;
        }}

        .subtitle {{
            font-size: 10pt;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            margin: 0;
        }}

        .section-title {{
            font-family: 'Cinzel', serif;
            color: #1e3a8a;
            font-size: 14pt;
            border-bottom: 1px solid #e2e8f0;
            padding-bottom: 6px;
            margin-top: 25px;
            margin-bottom: 12px;
            page-break-after: avoid;
        }}

        .subsection-title {{
            color: #334155;
            font-size: 11.5pt;
            margin-top: 18px;
            margin-bottom: 8px;
            page-break-after: avoid;
        }}

        .report-p {{
            margin-bottom: 12px;
            text-align: justify;
        }}

        .report-list {{
            margin: 10px 0 15px 20px;
            padding: 0;
        }}

        .report-list li {{
            margin-bottom: 6px;
        }}

        .callout-box {{
            background-color: #f8fafc;
            border-left: 4px solid #3b82f6;
            border-radius: 0 6px 6px 0;
            padding: 12px 16px;
            margin: 16px 0;
            page-break-inside: avoid;
        }}

        .callout-header {{
            font-weight: 600;
            color: #1d4ed8;
            margin-bottom: 4px;
            font-size: 10pt;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .callout-box p {{
            margin: 0;
            font-size: 10pt;
            color: #334155;
        }}

        strong {{
            color: #0f172a;
            font-weight: 600;
        }}

        .footer {{
            margin-top: 40px;
            padding-top: 12px;
            border-top: 1px solid #e2e8f0;
            text-align: center;
            font-size: 8.5pt;
            color: #94a3b8;
        }}
    </style>
</head>
<body>

<div class="header-banner">
    <div class="subtitle">Astra Hellenistic & Psychological Astrology Engine</div>
</div>

{body_html}

<div class="footer">
    Astra Western Astrology Framework • Classical RAG Ground Truth Report
</div>

</body>
</html>
"""
    return full_html


def generate_pdf(input_md_path: str, output_pdf_path: str = None) -> str:
    if not os.path.exists(input_md_path):
        raise FileNotFoundError(f"Input markdown file not found: {input_md_path}")

    if not output_pdf_path:
        base_name = os.path.splitext(input_md_path)[0]
        output_pdf_path = f"{base_name}.pdf"

    with open(input_md_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    # Extract title from markdown
    title_match = re.search(r'^#\s+(.+)$', md_text, re.MULTILINE)
    title = title_match.group(1) if title_match else "Astrological Reading Report"

    # Convert to HTML
    html_content = markdown_to_html(md_text, title=title)

    # Save temporary HTML file
    temp_html_path = output_pdf_path.replace(".pdf", "_temp.html")
    with open(temp_html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    chrome_bin = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    cmd = [
        chrome_bin,
        "--headless",
        "--disable-gpu",
        f"--print-to-pdf={output_pdf_path}",
        temp_html_path
    ]

    print(f"📄 Generating PDF from {input_md_path}...")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if os.path.exists(temp_html_path):
        os.remove(temp_html_path)

    if result.returncode == 0 and os.path.exists(output_pdf_path):
        size_kb = os.path.getsize(output_pdf_path) / 1024
        print(f"✅ Successfully generated PDF: {output_pdf_path} ({size_kb:.1f} KB)")
        return output_pdf_path
    else:
        raise RuntimeError(f"Failed to generate PDF. Chrome output:\n{result.stderr}")


def main():
    parser = argparse.ArgumentParser(description="Convert Astrological Reading Markdown to PDF.")
    parser.add_argument("report", help="Path to input markdown file (e.g. western/kailash_Full_Pipeline_Reading.md)")
    parser.add_argument("--output", help="Optional output PDF path")

    args = parser.parse_args()
    generate_pdf(args.report, args.output)


if __name__ == "__main__":
    main()
