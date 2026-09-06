#!/usr/bin/env python3
"""
Full-fledged PDF to EPUB 3 conversion for:
'The Art and Science of Vedic Astrology' (Vol 1)
by Richard Fish & Ryan Kurczak
"""

import os
import sys
import re
import html
import shutil
import zipfile
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
    "10th House Knees": "10th House: Knees",
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

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')

print("Definitions compiled.")
