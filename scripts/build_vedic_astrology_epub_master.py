#!/usr/bin/env python3
"""
Publication-Grade PDF to EPUB 3 Conversion Pipeline
===================================================
Book: The Art and Science of Vedic Astrology (Vol. 1: The Foundation Course)
Authors: Richard Fish & Ryan Kurczak
Publisher: Asheville Vedic Astrology (2012)
"""

import os
import sys
import re
import html
import shutil
import zipfile
import posixpath
import fitz  # PyMuPDF
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup

PDF_PATH = "/Users/hajnaljanos/PycharmProjects/astra/source-material/anki_decks/The Art and Science of Vedic Astrology-Vol-01.pdf"
OUTPUT_PATHS = [
    "/Users/hajnaljanos/PycharmProjects/astra/source-material/anki_decks/The Art and Science of Vedic Astrology-Vol-01.epub",
    "/Users/hajnaljanos/Documents/Astrology/The Art and Science of Vedic Astrology-Vol-01.epub"
]
WORK_DIR = "/tmp/vedic_astro_epub_build"
IMG_DIR = os.path.join(WORK_DIR, "images")
os.makedirs(IMG_DIR, exist_ok=True)

WORD_REPAIRS = {
    "spontane- ously": "spontaneously",
    "practi- ces": "practices",
    "sub- conscious": "subconscious",
    "psycho- logical": "psychological",
    "practi- ce": "practice",
    "over- whelming": "overwhelming",
    "sect- ions": "sections",
    "intel- ligence": "intelligence",
    "tow- ards": "towards",
    "mool- atrikona": "moolatrikona",
    "both- ways": "both-ways",
    "self- love": "self-love",
    "cont- entment": "contentment",
    "well- being": "well-being",
    "rela- tionships": "relationships",
    "plac- ed": "placed",
    "above- mentioned": "above-mentioned",
    "self- con": "self-con",
    "un- derstanding": "understanding",
    "sub- cycles": "sub-cycles",
    "sub- sub": "sub-sub",
    "Naksha- tra": "Nakshatra",
    "birth- chart": "birth chart",
    "con- sideration": "consideration",
    "com- munication": "communication",
    "dis- tracted": "distracted",
    "pen- dant": "pendant",
    "Na- vamsha": "Navamsha",
    "Self- determined": "Self-determined",
    "non- attachment": "non-attachment",
    "Self- inquiry": "Self-inquiry",
    "prac- tice": "practice",
    "Neelakan- tha": "Neelakantha",
    "midand": "mid- and",
    "Span ofYears": "Span of Years",
    "CHAPTER THREEE": "CHAPTER THREE",
}

CSS_STYLE = """@charset "utf-8";

body {
    font-family: "Bookerly", "Georgia", "Times New Roman", serif;
    font-size: 1.05em;
    line-height: 1.6;
    margin: 4% 5%;
    text-align: justify;
    color: #1a1a1a;
    background-color: #ffffff;
}

header.chapter-header {
    text-align: center;
    margin-top: 2.2em;
    margin-bottom: 2em;
    page-break-after: avoid;
    break-after: avoid;
}

p.chapter-number {
    font-family: "Bookerly", "Georgia", serif;
    font-size: 1em;
    font-weight: bold;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #b8860b;
    margin-bottom: 0.4em;
}

h1.chapter-title {
    font-family: "Bookerly", "Georgia", serif;
    font-size: 1.65em;
    font-weight: bold;
    color: #8b4513;
    line-height: 1.25;
    margin-top: 0;
    margin-bottom: 0.6em;
    padding-bottom: 0.4em;
    border-bottom: 2px solid #b8860b;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}

h1.frontmatter-title {
    font-family: "Bookerly", "Georgia", serif;
    font-size: 1.6em;
    font-weight: bold;
    color: #8b4513;
    text-align: center;
    margin-top: 1.8em;
    margin-bottom: 1.2em;
    padding-bottom: 0.3em;
    border-bottom: 2px solid #b8860b;
    letter-spacing: 0.04em;
}

h2.section-title {
    font-family: "Bookerly", "Georgia", serif;
    font-size: 1.28em;
    font-weight: bold;
    color: #8b4513;
    text-align: left;
    margin-top: 1.8em;
    margin-bottom: 0.6em;
    border-left: 4px solid #b8860b;
    padding-left: 0.5em;
    line-height: 1.3;
    page-break-after: avoid;
    break-after: avoid;
}

h3.subsection-title {
    font-family: "Bookerly", "Georgia", serif;
    font-size: 1.12em;
    font-weight: bold;
    color: #2c3e50;
    text-align: left;
    margin-top: 1.4em;
    margin-bottom: 0.4em;
    page-break-after: avoid;
    break-after: avoid;
}

h4.subsubsection-title {
    font-family: "Bookerly", "Georgia", serif;
    font-size: 1.02em;
    font-weight: bold;
    color: #4a6b82;
    text-align: left;
    margin-top: 1.1em;
    margin-bottom: 0.3em;
}

p {
    margin-top: 0;
    margin-bottom: 0;
    text-indent: 1.25em;
}

h1 + p, h2 + p, h3 + p, h4 + p, figure + p, blockquote + p, div + p, table + p, ul + p, ol + p, dl + p {
    text-indent: 0;
}

blockquote.sutra-verse {
    margin: 1.3em 1.2em;
    background-color: #fdfaf6;
    border-left: 4px solid #b8860b;
    padding: 0.9em 1.2em;
    border-radius: 4px;
    text-align: left;
    font-style: italic;
    box-shadow: 0 1px 3px rgba(0,0,0,0.03);
}

blockquote.sutra-verse p {
    text-indent: 0;
    margin: 0.2em 0;
    color: #4a2e18;
}

span.sutra-ref {
    font-weight: bold;
    color: #8b4513;
    font-style: normal;
    margin-right: 0.4em;
}

blockquote.scripture-quote {
    margin: 1.3em 1.2em;
    background-color: #f6f8fa;
    border-left: 4px solid #4a6b82;
    padding: 0.9em 1.2em;
    border-radius: 4px;
    text-align: left;
    font-style: italic;
    box-shadow: 0 1px 3px rgba(0,0,0,0.03);
}

blockquote.scripture-quote p {
    text-indent: 0;
    margin: 0.2em 0;
    color: #243342;
}

figure.chart-figure {
    margin: 1.8em auto;
    text-align: center;
    max-width: 100%;
    page-break-inside: avoid;
    break-inside: avoid;
}

figure.chart-figure img {
    max-width: 96%;
    height: auto;
    display: block;
    margin: 0 auto;
    border-radius: 3px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.12);
}

figcaption {
    font-size: 0.9em;
    font-style: italic;
    color: #555555;
    margin-top: 0.6em;
    text-align: center;
}

.table-responsive {
    width: 100%;
    overflow-x: auto;
    margin: 1.5em 0;
    page-break-inside: avoid;
    break-inside: avoid;
}

table.astrology-table {
    width: 100%;
    border-collapse: collapse;
    margin: 0.5em 0;
    font-size: 0.94em;
    line-height: 1.4;
}

table.astrology-table th, table.astrology-table td {
    border: 1px solid #d4c5b0;
    padding: 7px 10px;
    text-align: left;
    vertical-align: top;
}

table.astrology-table th {
    background-color: #f4ece1;
    color: #8b4513;
    font-weight: bold;
}

table.astrology-table tr:nth-child(even) {
    background-color: #fcfbfa;
}

div.ascendant-card {
    margin: 1.4em 0;
    border: 1px solid #dcd3c3;
    border-radius: 6px;
    padding: 0.8em 1.2em;
    background-color: #fdfbf8;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}

div.ascendant-card h3 {
    margin-top: 0.2em;
    margin-bottom: 0.5em;
    color: #8b4513;
}

dl.glossary-list {
    margin: 1em 0;
}

dl.glossary-list dt {
    font-weight: bold;
    color: #8b4513;
    font-size: 1.06em;
    margin-top: 0.9em;
}

dl.glossary-list dd {
    margin-left: 1.2em;
    margin-bottom: 0.5em;
    text-indent: 0;
    text-align: justify;
}

ul.toc-list {
    list-style-type: none;
    padding-left: 0;
    margin: 1.2em 0;
}

li.toc-item-ch {
    font-weight: bold;
    font-size: 1.05em;
    margin-top: 0.9em;
    border-bottom: 1px dashed #dcd3c3;
    padding-bottom: 0.3em;
}

li.toc-item-ch a {
    color: #8b4513;
    text-decoration: none;
}

li.toc-item-ch a:hover {
    text-decoration: underline;
}

li.toc-item-sec {
    font-size: 0.94em;
    font-weight: normal;
    margin-left: 1.4em;
    margin-top: 0.3em;
}

li.toc-item-sec a {
    color: #4a6b82;
    text-decoration: none;
}

div.titlepage {
    text-align: center;
    margin: 4em 0 3em 0;
}

h1.book-title {
    font-size: 2.1em;
    font-weight: bold;
    color: #8b4513;
    line-height: 1.2;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    margin-bottom: 0.2em;
}

p.book-subtitle {
    font-size: 1.25em;
    font-style: italic;
    color: #b8860b;
    margin-top: 0.4em;
    margin-bottom: 2em;
}

p.book-authors {
    font-size: 1.2em;
    font-weight: bold;
    color: #1a1a1a;
    letter-spacing: 0.06em;
    margin-top: 2em;
}

div.copyright-page {
    margin-top: 3em;
    font-size: 0.9em;
    line-height: 1.6;
    color: #444444;
}

div.copyright-page p {
    text-indent: 0;
    margin-bottom: 0.6em;
}

a {
    color: #8b4513;
    text-decoration: none;
}
"""

IMAGE_CAPTIONS = {
    (23, 1): ('“Aum Shri Ganeshaya Namaha” — Salutations to Ganesha, The Lord of Astrology', 'Lord Ganesha'),
    (28, 1): ('Ayanamsha Ephemeris Values: 1900 to 1933', 'Ayanamsha 1900-1933'),
    (29, 1): ('Ayanamsha Ephemeris Values: 1934 to 1967', 'Ayanamsha 1934-1967'),
    (30, 1): ('Ayanamsha Ephemeris Values: 1968 to 2000', 'Ayanamsha 1968-2000'),
    (34, 1): ('Symbols of the Planets and Signs of the Zodiac', 'Planetary and Sign Symbols'),
    (36, 1): ('South Indian Birth Chart Diagram', 'South Indian Chart'),
    (37, 1): ('North Indian Birth Chart Diagram', 'North Indian Chart'),
    (38, 1): ('Western Circular Horoscope vs. Vedic Square Chart Format', 'Chart Formats Comparison'),
    (50, 1): ('Birth Chart of Albert Einstein', 'Albert Einstein Chart'),
    (53, 1): ('Example Horoscope: Combustion of Mars with the Sun', 'Combustion Example Chart'),
    (57, 1): ('Table of Planetary Dignities (Part 1: Signs and Rulerships)', 'Planetary Dignities Part 1'),
    (57, 2): ('Table of Planetary Dignities (Part 2: Exaltation and Debilitation)', 'Planetary Dignities Part 2'),
    (59, 1): ('Birth Chart of Margaret Thatcher (Moolatrikona Example)', 'Margaret Thatcher Chart'),
    (78, 1): ('The Twelve Houses in the North Indian Chart Diagram', 'The Twelve Houses'),
    (80, 1): ('The Upachaya (Growth and Improvement) Houses', 'Upachaya Houses'),
    (85, 1): ('Margaret Thatcher Horoscope: Planetary Aspects Example', 'Margaret Thatcher Aspects Chart'),
    (101, 1): ('Natural Planetary Friendships Diagram', 'Friendly Planets Diagram'),
    (102, 1): ('Natural Planetary Enmities by Sign Diagram', 'Enemy Planets by Sign Diagram'),
    (105, 1): ('Birth Chart of Adolf Hitler: Ruchaka Yoga Example', 'Adolf Hitler Chart'),
    (106, 1): ('Horoscope Example: Malavya Yoga with Saturn Aspect', 'Malavya Yoga Chart'),
    (108, 1): ('Horoscope of a Tibetan Lama in Exile: Gaja Keshari Yoga', 'Tibetan Lama Chart'),
    (118, 1): ('Navamsha (D9) Division and Calculation Table', 'Navamsha Table'),
    (119, 1): ('Comparative Horoscope: Rashi (D1) and Navamsha (D9) Charts', 'Rashi and Navamsha Charts'),
    (120, 1): ('Dwadamsha (D12) Harmonic Calculation Table', 'Dwadamsha Table'),
    (121, 1): ('Trimsamsa (D30) Harmonic Calculation Table', 'Trimsamsa Table'),
    (150, 1): ('Planetary Maturation and Natural Ages of Life Table', 'Planetary Maturation Ages Table'),
    (154, 1): ('Dosha Attributes and Planetary Correspondences Table', 'Dosha Attributes Table'),
    (155, 1): ('Medical Astrology Example: Libra Ascendant Horoscope', 'Libra Lagna Medical Horoscope'),
    (162, 1): ('Planetary Gemstones, Substitute Stones, Metals and Fingers Table', 'Gemstones and Metals Table'),
    (171, 1): ('Vocation Assessment: Example Chart 1 (Rashi and Navamsha)', 'Vocation Assessment Chart 1'),
    (172, 1): ('Vocation Assessment: Example Chart 2 (Rashi and Navamsha)', 'Vocation Assessment Chart 2'),
    (175, 1): ('Horoscope of Mary Baker Eddy (Chandra Lagna Example)', 'Mary Baker Eddy Chart'),
    (178, 1): ('Horoscope Example: Cancellation of Debility (Neecha Bhanga)', 'Cancellation of Debility Chart')
}

def clean_text(s):
    if not s:
        return ""
    s = s.replace('\ufb01', 'fi').replace('\ufb02', 'fl')
    for broken, fixed in WORD_REPAIRS.items():
        s = s.replace(broken, fixed)
    return s

def is_sentence_end(txt):
    if not txt:
        return False
    t = txt.strip()
    return any(t.endswith(p) for p in ['.', '!', '?', '.”', '!”', '?”', '.”', '”', '"', '’', ':'])

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')

doc = fitz.open(PDF_PATH)

# Extract images
print("Extracting images from PDF...")
images_data = {}
for pno in range(len(doc)):
    page = doc[pno]
    info = page.get_image_info(xrefs=True)
    for idx, item in enumerate(info):
        xref = item.get('xref')
        if xref:
            img = doc.extract_image(xref)
            ext = img['ext']
            fname = f"img_p{pno+1:03d}_{idx+1}.{ext}"
            fpath = os.path.join(IMG_DIR, fname)
            with open(fpath, "wb") as img_f:
                img_f.write(img['image'])
            images_data[(pno+1, idx+1)] = {
                'fname': fname,
                'fpath': fpath,
                'xref': xref,
                'width': img['width'],
                'height': img['height'],
                'bytes': img['image'],
                'ext': ext,
                'bbox': item.get('bbox')
            }

print(f"Extracted {len(images_data)} images.")

def get_chapter_stream(start_p, end_p):
    stream = []
    for pno in range(start_p, end_p + 1):
        page = doc[pno-1]
        d = page.get_text('dict')
        
        # 1. Images
        for idx, im in enumerate(page.get_image_info(xrefs=True)):
            xref = im.get('xref')
            if xref:
                stream.append({
                    'type': 'image',
                    'page': pno,
                    'idx': idx + 1,
                    'xref': xref,
                    'y0': im['bbox'][1],
                    'x0': im['bbox'][0]
                })
                
        # 2. Text lines
        lines = []
        for b in d['blocks']:
            if b.get('type') == 0:
                for l in b['lines']:
                    txt = ''.join(s['text'] for s in l['spans']).strip()
                    if not txt:
                        continue
                    span_htmls = []
                    for s in l['spans']:
                        t = clean_text(s['text'])
                        t_esc = html.escape(t)
                        f = s['font']
                        flags = s['flags']
                        is_b = 'Bold' in f or (flags & 16)
                        is_i = 'Italic' in f or (flags & 2)
                        if is_b and is_i:
                            span_htmls.append(f'<b><i>{t_esc}</i></b>')
                        elif is_b:
                            span_htmls.append(f'<b>{t_esc}</b>')
                        elif is_i:
                            span_htmls.append(f'<i>{t_esc}</i>')
                        else:
                            span_htmls.append(t_esc)
                    main_s = max(l['spans'], key=lambda s: len(s['text']))
                    lines.append({
                        'type': 'line',
                        'page': pno,
                        'y0': round(l['bbox'][1], 1),
                        'y1': round(l['bbox'][3], 1),
                        'x0': round(l['bbox'][0], 1),
                        'x1': round(l['bbox'][2], 1),
                        'text': clean_text(txt),
                        'html': ''.join(span_htmls),
                        'size': round(main_s['size'], 1),
                        'font': main_s['font'],
                        'flags': main_s['flags']
                    })
        lines.sort(key=lambda x: (x['y0'], x['x0']))
        
        # Merge lines sharing y0
        merged = []
        for l in lines:
            if merged and abs(merged[-1][0]['y0'] - l['y0']) <= 2.5:
                merged[-1].append(l)
            else:
                merged.append([l])
        for r in merged:
            r.sort(key=lambda x: x['x0'])
            if len(r) > 1 and any(r[i+1]['x0'] - r[i]['x1'] > 15 for i in range(len(r)-1)):
                stream.append({
                    'type': 'table_row',
                    'page': pno,
                    'y0': r[0]['y0'],
                    'x0': r[0]['x0'],
                    'cells': r
                })
            else:
                # Merge into single line if not a multi-column table
                m_text = " ".join(item['text'] for item in r)
                m_html = " ".join(item['html'] for item in r)
                stream.append({
                    'type': 'line',
                    'page': pno,
                    'y0': r[0]['y0'],
                    'y1': r[0]['y1'],
                    'x0': r[0]['x0'],
                    'x1': r[-1]['x1'],
                    'text': m_text,
                    'html': m_html,
                    'size': r[0]['size'],
                    'font': r[0]['font'],
                    'flags': r[0]['flags']
                })
                    
    # Handle page 159 table line continuation
    if start_p <= 159 <= end_p:
        cleaned_stream = []
        for it in stream:
            if it['type'] == 'line' and it.get('page') == 159 and it['x0'] > 200 and 240 < it['y0'] < 600:
                # Continuation of previous table row's 3rd cell!
                if cleaned_stream and cleaned_stream[-1]['type'] == 'table_row':
                    prev_cells = cleaned_stream[-1]['cells']
                    prev_cells[-1]['text'] += " " + it['text']
                    prev_cells[-1]['html'] += " " + it['html']
                    continue
            cleaned_stream.append(it)
        stream = cleaned_stream

    stream.sort(key=lambda x: (x['page'], x['y0'], x['x0']))
    return stream

def stream_to_html_blocks(stream, is_ch17=False):
    blocks = []
    curr_p_html = []
    curr_table_rows = []
    
    def flush_p():
        nonlocal curr_p_html
        if curr_p_html:
            p_text = " ".join(curr_p_html)
            p_text = re.sub(r'(\b[a-zA-Z]+)-\s+([a-zA-Z]+\b)', r'\1\2', p_text)
            p_text = re.sub(r'\s+', ' ', p_text).strip()
            
            # Subhead for Lennon timeline
            clean_check = re.sub(r'<[^>]+>', '', p_text).strip()
            if clean_check in ['RahuMahadasha:', 'Rahu Mahadasha:']:
                blocks.append(('h4', '<h4 class="subsubsection-title">Rahu Mahadasha</h4>'))
                curr_p_html = []
                return
            if clean_check in ['JupiterMahadasha:', 'Jupiter Mahadasha:']:
                blocks.append(('h4', '<h4 class="subsubsection-title">Jupiter Mahadasha</h4>'))
                curr_p_html = []
                return
                
            # Standalone scripture quotes
            if (p_text.startswith('“') or p_text.startswith('"')) and (p_text.endswith('”') or p_text.endswith('"')) and len(p_text) > 35:
                blocks.append(('quote', f'<blockquote class="scripture-quote"><p>{p_text}</p></blockquote>'))
            else:
                blocks.append(('p', f'<p>{p_text}</p>'))
            curr_p_html = []
            
    def flush_table():
        nonlocal curr_table_rows
        if curr_table_rows:
            html_rows = []
            for idx, r in enumerate(curr_table_rows):
                tag = 'th' if idx == 0 else 'td'
                cells_html = "".join(f"<{tag}>{c['html']}</{tag}>" for c in r['cells'])
                html_rows.append(f"  <tr>{cells_html}</tr>")
            t_html = (
                '<div class="table-responsive">\n'
                '<table class="astrology-table">\n'
                + "\n".join(html_rows) + "\n"
                '</table>\n'
                '</div>'
            )
            blocks.append(('table', t_html))
            curr_table_rows = []

    for it in stream:
        itype = it['type']
        
        if itype == 'table_row':
            flush_p()
            curr_table_rows.append(it)
            continue
        else:
            flush_table()
            
        if itype == 'image':
            flush_p()
            cap_tuple = IMAGE_CAPTIONS.get((it['page'], it['idx']), ('Chart Diagram', 'Diagram'))
            cap_text, alt_text = cap_tuple
            img_fname = f"img_p{it['page']:03d}_{it['idx']}.jpeg"
            fig_html = (
                f'<figure class="chart-figure">\n'
                f'  <img src="images/{img_fname}" alt="{html.escape(alt_text)}" />\n'
                f'  <figcaption>{html.escape(cap_text)}</figcaption>\n'
                f'</figure>'
            )
            blocks.append(('figure', fig_html))
            continue
            
        if itype == 'line':
            text = it['text']
            html_text = it['html']
            size = it['size']
            x0 = it['x0']
            font = it['font']
            is_bold = 'Bold' in font
            
            # Skip chapter headers in text (handled in chapter header)
            if 'CHAPTER ' in text or (size > 20.0 and is_bold):
                flush_p()
                continue
                
            # Patanjali Sutras for Chapter 17
            if is_ch17 and re.match(r'^(I|II|III|IV)\.\d+', text):
                flush_p()
                m = re.match(r'^((?:I|II|III|IV)\.\d+(?:-\d+)?)\s*(.*)$', text)
                if m:
                    s_ref, s_txt = m.group(1), m.group(2)
                    blocks.append(('sutra', f'<blockquote class="sutra-verse"><p><span class="sutra-ref">{s_ref}</span> {html.escape(s_txt)}</p></blockquote>'))
                else:
                    blocks.append(('sutra', f'<blockquote class="sutra-verse"><p>{html_text}</p></blockquote>'))
                continue
                
            # Check for H2 section titles
            if (size > 16.0 and is_bold) or (size > 16.0 and len(text) < 60 and not text.endswith('.')):
                flush_p()
                blocks.append(('h2', f'<h2 class="section-title">{html_text}</h2>'))
                continue
                
            # Check for H3 subsections
            if (size > 14.5 and is_bold and len(text) < 50 and not text.endswith('.') and not text.endswith(',')):
                flush_p()
                blocks.append(('h3', f'<h3 class="subsection-title">{html_text}</h3>'))
                continue
                
            # Paragraph text: only start new paragraph if previous sentence actually ended!
            if curr_p_html:
                prev_clean = clean_text(re.sub(r'<[^>]+>', '', curr_p_html[-1])).strip()
                if is_sentence_end(prev_clean) and (x0 > 92.0 or text.startswith('•') or re.match(r'^\d+\.', text)):
                    flush_p()
                    curr_p_html.append(html_text)
                else:
                    curr_p_html.append(html_text)
            else:
                curr_p_html.append(html_text)

    flush_p()
    flush_table()
    return blocks

# Specialized Builders
def build_title_html():
    return """<div class="titlepage">
  <h1 class="book-title">The Art and Science of Vedic Astrology</h1>
  <p class="book-subtitle">The Foundation Course &bull; Volume 1</p>
  <p class="book-authors">RICHARD FISH &amp; RYAN KURCZAK</p>
</div>
<div class="copyright-page">
  <hr style="border: 0; border-top: 1px solid #dcd3c3; margin: 2em 0;" />
  <p><strong>Copyright &copy; 2012 by Ryan Kurczak &amp; Richard Fish</strong></p>
  <p>ISBN-13: 978-1475267655</p>
  <p>Published by Asheville Vedic Astrology<br />
  Asheville, NC<br />
  Telephone: 828-423-6636<br />
  Email: ryan@ashevillevedicastrology.com<br />
  Web site: www.ashevillevedicastrology.com</p>
  <p style="margin-top: 1.5em; font-size: 0.88em; color: #666;">All rights reserved. No part of this publication may be reproduced, stored in a retrieval system, or transmitted in any form or by any means, electronic, mechanical, photocopying, recording, or otherwise, without the prior written permission of the authors.</p>
</div>"""

def build_backcover_html():
    return """<div style="text-align: center; margin: 0; padding: 0;">
  <img src="images/img_p201_1.jpeg" alt="Back Cover: The Art and Science of Vedic Astrology Vol. 1" style="max-width: 100%; height: auto; display: block; margin: 0 auto;" />
</div>"""

def build_glossary_html():
    glossary_text = []
    for pno in range(190, 199):
        glossary_text.append(doc[pno-1].get_text())
    full_text = '\n'.join(glossary_text)
    full_text = re.sub(r'^\s*GLOSSARY\s*', '', full_text)
    entries = re.split(r'\n(?=[A-Z][a-zA-Z\s\(\)]+\s*[–—-])', full_text)
    dl_items = []
    for e in entries:
        e = e.strip().replace('\n', ' ')
        e = clean_text(re.sub(r'\s+', ' ', e))
        m = re.match(r'^([A-Z][a-zA-Z\s\(\)\'\"]+?)\s*[–—-]\s*(.*)$', e)
        if m:
            term, defn = m.group(1).strip(), m.group(2).strip()
            dl_items.append(f"  <dt>{html.escape(term)}</dt>\n  <dd>{html.escape(defn)}</dd>")
    
    return (
        '<h1 class="frontmatter-title">Glossary</h1>\n'
        '<dl class="glossary-list">\n'
        + "\n".join(dl_items) + "\n"
        '</dl>'
    )

def build_about_html():
    return """<h1 class="frontmatter-title">About the Authors</h1>

<h2 class="section-title">Richard Fish</h2>
<p>In the early 1970s Richard made an intensive study of astrology. Having also studied under various Vedic teachers and astrologers, in 1977 he was initiated by Swami Premananda into the Kriya Yoga lineage of Paramahansa Yogananda. He has practiced Vedic astrology and taught meditation for over three decades, bringing depth, clarity, and compassionate spiritual guidance to thousands of clients worldwide.</p>

<h2 class="section-title">Ryan Kurczak</h2>
<p>Ryan Kurczak was initiated into Kriya Yoga in 2000 by Roy Eugene Davis, a direct disciple of Paramahansa Yogananda. He has worked as a professional Vedic astrologer, teacher, and author for over a decade. Ryan is the founder of the Asheville Vedic Astrology apprenticeship program, which trains students worldwide in the rigorous mathematical and intuitive art of Jyotish.</p>

<h2 class="section-title">Other Books by the Authors</h2>
<h3 class="subsection-title">By Richard Fish and Ryan Kurczak</h3>
<ul>
  <li><em>The Art and Science of Vedic Astrology Vol. II: Intermediate Techniques and Applied Chart Assessment</em> (September 2013)</li>
</ul>

<h3 class="subsection-title">By Ryan Kurczak</h3>
<ul>
  <li><em>Kriya Yoga: Continuing the Lineage of Enlightenment</em> (September 2012)</li>
  <li><em>A Course In Tranquility: Integrating Spiritual Practice, Effective Living, &amp; Non Duality</em> (October 2012)</li>
</ul>"""

def build_ch9_ascendant_cards():
    ascendants_data = {}
    curr_asc = None
    curr_cat = None

    for pno in [99, 100, 101]:
        page = doc[pno-1]
        lines = [l.strip() for l in page.get_text().split('\n') if l.strip()]
        for l in lines:
            if 'ASCENDANT' in l:
                curr_asc = l.replace('ASCENDANT', '').strip().title()
                ascendants_data[curr_asc] = {'Friends': '', 'Neutrals': '', 'Enemies': ''}
                curr_cat = None
            elif l in ['Friends:', 'Neutrals:', 'Enemies:']:
                curr_cat = l.replace(':', '')
            elif curr_asc and curr_cat:
                ascendants_data[curr_asc][curr_cat] = (ascendants_data[curr_asc][curr_cat] + ' ' + l).strip()

    cards_html = []
    for sign, rels in ascendants_data.items():
        friends = clean_text(rels.get('Friends', ''))
        neutrals = clean_text(rels.get('Neutrals', ''))
        enemies = clean_text(rels.get('Enemies', ''))
        cards_html.append(f"""<div class="ascendant-card">
  <h3 class="subsection-title">{sign} Ascendant</h3>
  <table class="astrology-table">
    <tr><th style="width: 25%;">Friends</th><td>{html.escape(friends)}</td></tr>
    <tr><th>Neutrals</th><td>{html.escape(neutrals)}</td></tr>
    <tr><th>Enemies</th><td>{html.escape(enemies)}</td></tr>
  </table>
</div>""")
    return "\n".join(cards_html)

def build_toc_page_html():
    toc_html = [
        '<h1 class="frontmatter-title">Contents</h1>\n',
        '<ul class="toc-list">\n',
        '  <li class="toc-item-ch"><a href="intro.xhtml">Introduction</a></li>\n',
        '  <li class="toc-item-ch"><a href="ch01.xhtml">1. Study and Practice</a></li>\n',
        '  <li class="toc-item-ch"><a href="ch02.xhtml">2. Meditation and Astrology</a></li>\n',
        '  <li class="toc-item-ch"><a href="ch03.xhtml">3. Fundamental Terminology</a></li>\n',
        '  <li class="toc-item-ch"><a href="ch04.xhtml">4. The Planets</a></li>\n',
        '  <li class="toc-item-ch"><a href="ch05.xhtml">5. Planetary Conditions</a></li>\n',
        '  <li class="toc-item-ch"><a href="ch06.xhtml">6. Planets and Signs</a></li>\n',
        '  <li class="toc-item-ch"><a href="ch07.xhtml">7. The Houses</a></li>\n',
        '  <li class="toc-item-ch"><a href="ch08.xhtml">8. Planetary Aspects</a></li>\n',
        '  <li class="toc-item-ch"><a href="ch09.xhtml">9. The All Important Ascendant</a></li>\n',
        '  <li class="toc-item-ch"><a href="ch10.xhtml">10. Planetary Yogas</a></li>\n',
        '  <li class="toc-item-ch"><a href="ch11.xhtml">11. Divisional Charts</a></li>\n',
        '  <li class="toc-item-ch"><a href="ch12.xhtml">12. The Vimshotari Dasha System</a></li>\n',
        '  <li class="toc-item-ch"><a href="ch13.xhtml">13. Transits</a></li>\n',
        '  <li class="toc-item-ch"><a href="ch14.xhtml">14. Jyotish and Ayurveda</a></li>\n',
        '  <li class="toc-item-ch"><a href="ch15.xhtml">15. Remedial Measures</a></li>\n',
        '  <li class="toc-item-ch"><a href="ch16.xhtml">16. Practical Chart Work</a></li>\n',
        '  <li class="toc-item-ch"><a href="ch17.xhtml">17. The Yoga Sutras of Patanjali</a></li>\n',
        '  <li class="toc-item-ch"><a href="glossary.xhtml">Glossary</a></li>\n',
        '  <li class="toc-item-ch"><a href="about.xhtml">About the Authors</a></li>\n',
        '</ul>'
    ]
    return "".join(toc_html)

CHAPTER_CONFIGS = [
    {"id": "title", "file": "title.xhtml", "title": "Title Page", "type": "title", "start_p": 2, "end_p": 4},
    {"id": "toc", "file": "toc.xhtml", "title": "Table of Contents", "type": "toc", "start_p": 5, "end_p": 5},
    {"id": "intro", "file": "intro.xhtml", "title": "Introduction", "type": "chapter", "start_p": 6, "end_p": 12, "num": None, "ch_title": "Introduction"},
    {"id": "ch01", "file": "ch01.xhtml", "title": "Chapter 1: Study and Practice", "type": "chapter", "start_p": 13, "end_p": 16, "num": "Chapter 1", "ch_title": "Study and Practice"},
    {"id": "ch02", "file": "ch02.xhtml", "title": "Chapter 2: Meditation and Astrology", "type": "chapter", "start_p": 17, "end_p": 23, "num": "Chapter 2", "ch_title": "Meditation and Astrology"},
    {"id": "ch03", "file": "ch03.xhtml", "title": "Chapter 3: Fundamental Terminology", "type": "chapter", "start_p": 24, "end_p": 38, "num": "Chapter 3", "ch_title": "Fundamental Terminology"},
    {"id": "ch04", "file": "ch04.xhtml", "title": "Chapter 4: The Planets", "type": "chapter", "start_p": 39, "end_p": 48, "num": "Chapter 4", "ch_title": "The Planets"},
    {"id": "ch05", "file": "ch05.xhtml", "title": "Chapter 5: Planetary Conditions", "type": "chapter", "start_p": 49, "end_p": 55, "num": "Chapter 5", "ch_title": "Planetary Conditions"},
    {"id": "ch06", "file": "ch06.xhtml", "title": "Chapter 6: Planets and Signs", "type": "chapter", "start_p": 56, "end_p": 64, "num": "Chapter 6", "ch_title": "Planets and Signs"},
    {"id": "ch07", "file": "ch07.xhtml", "title": "Chapter 7: The Houses", "type": "chapter", "start_p": 65, "end_p": 83, "num": "Chapter 7", "ch_title": "The Houses"},
    {"id": "ch08", "file": "ch08.xhtml", "title": "Chapter 8: Planetary Aspects", "type": "chapter", "start_p": 84, "end_p": 90, "num": "Chapter 8", "ch_title": "Planetary Aspects"},
    {"id": "ch09", "file": "ch09.xhtml", "title": "Chapter 9: The All Important Ascendant", "type": "chapter", "start_p": 91, "end_p": 102, "num": "Chapter 9", "ch_title": "The All Important Ascendant"},
    {"id": "ch10", "file": "ch10.xhtml", "title": "Chapter 10: Planetary Yogas", "type": "chapter", "start_p": 103, "end_p": 113, "num": "Chapter 10", "ch_title": "Planetary Yogas"},
    {"id": "ch11", "file": "ch11.xhtml", "title": "Chapter 11: Divisional Charts", "type": "chapter", "start_p": 114, "end_p": 124, "num": "Chapter 11", "ch_title": "Divisional Charts"},
    {"id": "ch12", "file": "ch12.xhtml", "title": "Chapter 12: The Vimshotari Dasha System", "type": "chapter", "start_p": 125, "end_p": 142, "num": "Chapter 12", "ch_title": "The Vimshotari Dasha System"},
    {"id": "ch13", "file": "ch13.xhtml", "title": "Chapter 13: Transits", "type": "chapter", "start_p": 143, "end_p": 151, "num": "Chapter 13", "ch_title": "Transits"},
    {"id": "ch14", "file": "ch14.xhtml", "title": "Chapter 14: Jyotish and Ayurveda", "type": "chapter", "start_p": 152, "end_p": 160, "num": "Chapter 14", "ch_title": "Jyotish and Ayurveda"},
    {"id": "ch15", "file": "ch15.xhtml", "title": "Chapter 15: Remedial Measures", "type": "chapter", "start_p": 161, "end_p": 169, "num": "Chapter 15", "ch_title": "Remedial Measures"},
    {"id": "ch16", "file": "ch16.xhtml", "title": "Chapter 16: Practical Chart Work", "type": "chapter", "start_p": 170, "end_p": 179, "num": "Chapter 16", "ch_title": "Practical Chart Work"},
    {"id": "ch17", "file": "ch17.xhtml", "title": "Chapter 17: The Yoga Sutras of Patanjali", "type": "chapter", "start_p": 180, "end_p": 189, "num": "Chapter 17", "ch_title": "The Yoga Sutras of Patanjali"},
    {"id": "glossary", "file": "glossary.xhtml", "title": "Glossary", "type": "glossary", "start_p": 190, "end_p": 198},
    {"id": "about", "file": "about.xhtml", "title": "About the Authors", "type": "about", "start_p": 199, "end_p": 200},
    {"id": "backcover", "file": "backcover.xhtml", "title": "Back Cover", "type": "backcover", "start_p": 201, "end_p": 201}
]

def generate_chapter_html(cfg):
    ctype = cfg['type']
    
    if ctype == 'title':
        body = build_title_html()
    elif ctype == 'toc':
        body = build_toc_page_html()
    elif ctype == 'glossary':
        body = build_glossary_html()
    elif ctype == 'about':
        body = build_about_html()
    elif ctype == 'backcover':
        body = build_backcover_html()
    else:
        is_ch17 = (cfg['id'] == 'ch17')
        
        header_parts = ['<header class="chapter-header">']
        if cfg.get('num'):
            header_parts.append(f'  <p class="chapter-number">{html.escape(cfg["num"])}</p>')
        header_parts.append(f'  <h1 class="chapter-title">{html.escape(cfg["ch_title"])}</h1>')
        header_parts.append('</header>\n')
        
        if cfg['id'] == 'ch09':
            st_p1 = get_chapter_stream(91, 98)
            blocks_p1 = stream_to_html_blocks(st_p1)
            cards = build_ch9_ascendant_cards()
            fig101 = f'<figure class="chart-figure">\n  <img src="images/img_p101_1.jpeg" alt="Friendly Planets Diagram" />\n  <figcaption>{html.escape(IMAGE_CAPTIONS[(101,1)][0])}</figcaption>\n</figure>'
            fig102 = f'<figure class="chart-figure">\n  <img src="images/img_p102_1.jpeg" alt="Enemy Planets by Sign Diagram" />\n  <figcaption>{html.escape(IMAGE_CAPTIONS[(102,1)][0])}</figcaption>\n</figure>'
            
            body_blocks = [b[1] for b in blocks_p1]
            body_blocks.append('<h2 class="section-title">Relationship Of Planets To Each Ascendant</h2>')
            body_blocks.append('<p>Based on the above consideration, we give the temporary status of each planet according to the Ascendant sign:</p>')
            body_blocks.append(cards)
            body_blocks.append(fig101)
            body_blocks.append(fig102)
            body = "\n".join(header_parts) + "\n" + "\n\n".join(body_blocks)
        else:
            stream = get_chapter_stream(cfg['start_p'], cfg['end_p'])
            blocks = stream_to_html_blocks(stream, is_ch17=is_ch17)
            body_blocks = [b[1] for b in blocks]
            body = "\n".join(header_parts) + "\n" + "\n\n".join(body_blocks)

    full_xhtml = (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<!DOCTYPE html>\n'
        '<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="en">\n'
        '<head>\n'
        f'  <title>{html.escape(cfg["title"])}</title>\n'
        '  <link rel="stylesheet" type="text/css" href="style/style.css" />\n'
        '</head>\n'
        '<body>\n'
        f'{body}\n'
        '</body>\n'
        '</html>\n'
    )
    return full_xhtml

def build_and_package_epub():
    print("\n=======================================================")
    print("ASSEMBLING PUBLICATION-GRADE EPUB 3 EBOOK")
    print("=======================================================")
    
    book = epub.EpubBook()
    book.set_identifier("urn:isbn:978-1475267655")
    book.set_title("The Art and Science of Vedic Astrology: The Foundation Course (Volume 1)")
    book.set_language("en")
    book.add_author("Richard Fish")
    book.add_author("Ryan Kurczak")
    book.add_metadata('DC', 'publisher', 'Asheville Vedic Astrology')
    book.add_metadata('DC', 'date', '2012')
    book.add_metadata('DC', 'description', 'The Foundation Course in Vedic Astrology (Volume 1) by Richard Fish and Ryan Kurczak. An integrated approach to astrological technique, yogic meditation, planetary conditions, houses, dashas, transits, and Ayurveda.')

    # Set Cover Image
    cover_path = os.path.join(IMG_DIR, "img_p001_1.jpeg")
    with open(cover_path, 'rb') as cf:
        cover_bytes = cf.read()
    book.set_cover("images/cover.jpeg", cover_bytes)

    # Add Stylesheet
    style_item = epub.EpubItem(
        uid="style_css",
        file_name="style/style.css",
        media_type="text/css",
        content=CSS_STYLE.encode('utf-8')
    )
    book.add_item(style_item)

    # Add all images
    for (pno, idx), idata in images_data.items():
        fname = idata['fname']
        fpath = idata['fpath']
        with open(fpath, 'rb') as img_f:
            c_bytes = img_f.read()
        im_item = epub.EpubItem(
            uid=f"img_p{pno:03d}_{idx}",
            file_name=f"images/{fname}",
            media_type="image/jpeg",
            content=c_bytes
        )
        book.add_item(im_item)

    # Generate Chapter XHTML items
    chapter_items = []
    toc_links = []
    
    for cfg in CHAPTER_CONFIGS:
        print(f"Generating XHTML: {cfg['file']} - {cfg['title']}...")
        xhtml_content = generate_chapter_html(cfg)
        
        c_item = epub.EpubHtml(
            title=cfg['title'],
            file_name=cfg['file'],
            lang='en'
        )
        c_item.content = xhtml_content.encode('utf-8')
        c_item.add_item(style_item)
        book.add_item(c_item)
        chapter_items.append(c_item)
        
        if cfg['type'] != 'backcover':
            link = epub.Link(cfg['file'], cfg['title'], slugify(cfg['title']))
            toc_links.append(link)

    book.toc = toc_links
    book.spine = chapter_items
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # Write EPUB
    out_epub_1 = OUTPUT_PATHS[0]
    os.makedirs(os.path.dirname(out_epub_1), exist_ok=True)
    epub.write_epub(out_epub_1, book)
    
    file_size_mb = os.path.getsize(out_epub_1) / (1024 * 1024)
    print(f"\nSuccessfully created primary EPUB at: {out_epub_1} ({file_size_mb:.2f} MB)")
    
    # Copy to secondary output destination
    out_epub_2 = OUTPUT_PATHS[1]
    os.makedirs(os.path.dirname(out_epub_2), exist_ok=True)
    shutil.copy2(out_epub_1, out_epub_2)
    print(f"Successfully copied to secondary path: {out_epub_2}")

    return out_epub_1

def validate_epub(epub_path):
    print(f"\nRunning validation on {epub_path}...")
    zf = zipfile.ZipFile(epub_path)
    all_files = set(zf.namelist())
    broken = 0
    words = 0
    headings = 0
    
    for name in all_files:
        if name.endswith(".xhtml"):
            data = zf.read(name).decode("utf-8")
            soup = BeautifulSoup(data, "html.parser")
            words += len(soup.get_text().split())
            headings += len(soup.find_all(["h1", "h2", "h3", "h4"]))
            
            doc_dir = posixpath.dirname(name)
            for img in soup.find_all("img"):
                src = img.get("src", "")
                target = posixpath.normpath(posixpath.join(doc_dir, src))
                if target not in all_files:
                    print(f"  [ERROR] Broken image in {name}: {src} (resolved: {target})")
                    broken += 1
            for a in soup.find_all("a", href=True):
                href = a["href"].split("#")[0]
                if href:
                    target = posixpath.normpath(posixpath.join(doc_dir, href))
                    if target not in all_files:
                        print(f"  [ERROR] Broken link in {name}: {a['href']} (resolved: {target})")
                        broken += 1
                        
    print(f"Validation summary: {words:,} words, {headings} headings, {broken} broken links/images.")
    return broken == 0

if __name__ == "__main__":
    epub_file = build_and_package_epub()
    validate_epub(epub_file)
