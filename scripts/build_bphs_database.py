#!/usr/bin/env python3
"""
Build Complete Searchable Database of Brihat Parashara Hora Shastra (BPHS)
Generates:
1. SQLite Database with FTS5: source-material/sanskrit_texts/bphs.db
2. JSON Database: source-material/sanskrit_texts/bphs_database.json
"""

import os
import re
import json
import sqlite3

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BPHS_DIR = os.path.join(BASE_DIR, "source-material", "sanskrit_texts", "bphs")
OUTPUT_DB = os.path.join(BASE_DIR, "source-material", "sanskrit_texts", "bphs.db")
OUTPUT_JSON = os.path.join(BASE_DIR, "source-material", "sanskrit_texts", "bphs_database.json")

DEVANAGARI_NUMERALS = {'०':0, '१':1, '२':2, '३':3, '४':4, '५':5, '६':6, '७':7, '८':8, '९':9}

def parse_deva_num(s):
    res = 0
    for ch in s:
        if ch in DEVANAGARI_NUMERALS:
            res = res * 10 + DEVANAGARI_NUMERALS[ch]
    return res

CHAPTER_ENGLISH_TITLES = {
    1: 'Creation and Cosmic Inception (Srishti Krama)',
    2: 'Incarnations of the Divine (Avatara)',
    3: 'Planetary Characters and Descriptions (Graha Guna Svarupa)',
    4: 'Zodiac Signs and Kala Purusha Limbs (Rashi Svarupa)',
    5: 'Special Ascendants and Lagnas (Vishesha Lagna)',
    6: 'The Sixteen Divisional Charts (Shodashavarga)',
    7: 'Divisional Chart Considerations (Varga Viveka)',
    8: 'Planetary and Sign Aspects (Rashi Drishti)',
    9: 'Early Mortality and Afflictions (Arishta)',
    10: 'Cancellation of Afflictions (Arishta Bhanga)',
    11: 'House Considerations and Judgments (Bhava Viveka)',
    12: 'First House Effects - Physical Body & Personality (Tanu Bhava Phala)',
    13: 'Second House Effects - Wealth & Speech (Dhana Bhava Phala)',
    14: 'Third House Effects - Siblings & Courage (Sahaja Bhava Phala)',
    15: 'Fourth House Effects - Mother, Home & Property (Bandhu / Sukha Bhava Phala)',
    16: 'Fifth House Effects - Children & Intellect (Putra Bhava Phala)',
    17: 'Sixth House Effects - Enemies, Debts & Disease (Shatru Bhava Phala)',
    18: 'Seventh House Effects - Spouse & Partnerships (Kalatra / Jaya Bhava Phala)',
    19: 'Eighth House Effects - Longevity & Transformations (Ayur Bhava Phala)',
    20: 'Ninth House Effects - Fortune, Dharma & Guru (Bhagya Bhava Phala)',
    21: 'Tenth House Effects - Profession & Actions (Karma Bhava Phala)',
    22: 'Eleventh House Effects - Gains & Aspirations (Labha Bhava Phala)',
    23: 'Twelfth House Effects - Expenses & Liberation (Vyaya Bhava Phala)',
    24: 'Effects of House Lords Across Houses (Bhavesha Phala)',
    25: 'Effects of Non-Luminous Planets / Upagrahas (Aprakasha Graha)',
    26: 'Detailed Aspect Calculations (Graha Sphuta Drishti)',
    27: 'Planetary Strengths and Shadbala (Spashta Bala)',
    28: 'Auspicious and Inauspicious Rays / Ishta-Kashta Bala',
    29: 'Arudha Padas of Houses (Pada Adhyaya)',
    30: 'Upapada Lagna and Marriage Analysis (Upapada Adhyaya)',
    31: 'Planetary Obstructions and Interventions (Argala Adhyaya)',
    32: 'Significators and Karakas (Karaka Adhyaya)',
    33: 'Effects of Karakamsha and Ishta Devata (Karakamsha Phala)',
    34: 'Yogakarakas and Functional Benefics/Malefics (Yogakaraka Adhyaya)',
    35: 'Nabhasa Yogas / Celestial Patterns (Nabhasa Yoga)',
    36: 'Various Auspicious & Inauspicious Combinations (Vividha Yoga)',
    37: 'Lunar Combinations (Chandra Yoga)',
    38: 'Solar Combinations (Ravi Yoga)',
    39: 'Royal Combinations and High Status (Raja Yoga)',
    40: 'Combinations for Royal Association (Raja Sambandha Yoga)',
    41: 'Special Wealth Combinations (Vishesha Dhana Yoga)',
    42: 'Poverty Combinations (Daridrya Yoga)',
    43: 'Longevity Calculations and Span of Life (Ayurdaya)',
    44: 'Death-Inflicting Planets and Killers (Maraka Bheda)',
    45: 'Planetary States and Conditions (Graha Avastha)',
    46: 'Planetary Periods and Dasas Overview (Dasa Adhyaya)',
    47: 'General Effects of Dasa Periods (Dasa Phala)',
    48: 'Special Nakshatra Dasa Effects (Vishesha Nakshatra Dasa)',
    49: 'Kalachakra Dasa System (Kalachakra Dasa)',
    50: 'Chara Dasa and Rasi Dasa Effects (Chara Dasa Phala)',
    51: 'Sub-Periods Overview (Antardasa Adhyaya)',
    52: 'Sun Mahadasa - Antardasa Effects (Surya Dasa Antardasa)',
    53: 'Moon Mahadasa - Antardasa Effects (Chandra Dasa Antardasa)',
    54: 'Mars Mahadasa - Antardasa Effects (Kuja Dasa Antardasa)',
    55: 'Rahu Mahadasa - Antardasa Effects (Rahu Dasa Antardasa)',
    56: 'Jupiter Mahadasa - Antardasa Effects (Guru Dasa Antardasa)',
    57: 'Saturn Mahadasa - Antardasa Effects (Shani Dasa Antardasa)',
    58: 'Mercury Mahadasa - Antardasa Effects (Budha Dasa Antardasa)',
    59: 'Ketu Mahadasa - Antardasa Effects (Ketu Dasa Antardasa)',
    60: 'Venus Mahadasa - Antardasa Effects (Shukra Dasa Antardasa)',
    61: 'Sub-Sub Periods Effects (Pratyantardasa Phala)',
    62: 'Micro Sub-Periods (Sookshma Dasa Phala)',
    63: 'Prana Dasa Sub-Divisions (Prana Dasa Phala)',
    64: 'Kalachakra Antardasa Effects (Kalachakra Antardasa)',
    65: 'Kalachakra Navamsa Dasa Effects (Kalachakra Navamsa Dasa)',
    66: 'Ashtakavarga System Overview (Ashtakavarga Adhyaya)',
    67: 'Trikona Reduction in Ashtakavarga (Trikona Shodhana)',
    68: 'Ekadhipatya Reduction (Ekadhipatya Shodhana)',
    69: 'Pinda Sadhana and Ashtakavarga Reductions (Pinda Sadhana)',
    70: 'Effects of Ashtakavarga Points (Ashtakavarga Phala)',
    71: 'Longevity from Ashtakavarga (Ashtakavarga Ayurdaya)',
    72: 'Collective Ashtakavarga Table (Samudaya Ashtakavarga)',
    73: 'Planetary Rays and Potency (Rashmi Phala)',
    74: 'Sudarshana Chakra System (Sudarshana Chakra)',
    75: 'Pancha Mahapurusha Yogas (Pancha Mahapurusha)',
    76: 'Five Great Elements and Body Types (Pancha Mahabhuta)',
    77: 'Three Gunas / Temperament Effects (Sattvadi Guna Phala)',
    78: 'Lost Horoscopy and Unknown Birth Time (Nashta Jataka)',
    79: 'Renunciation and Monastic Yogas (Pravrajya Yoga)',
    80: 'Female Horoscopy and Special Considerations (Stri Jataka)',
    81: 'Body Marks and Physical Features (Anga Lakshana)',
    82: 'Moles, Marks and Spots (Tiladi Lanchana)',
    83: 'Curses from Past Lives and Remedial Measures (Purvajanma Shapa)',
    84: 'Planetary Propitiation and Shanti Rituals (Graha Shanti)',
    85: 'Inauspicious Birth Times (Ashubha Janma Kathana)',
    86: 'Amavasya Birth Remedies (Darsha Janma Shanti)',
    87: 'Krishna Chaturdashi Birth Remedies (Krishna Chaturdashi Shanti)',
    88: 'Bhadra and Vyatipata Birth Remedies (Bhadradi Dur-Yoga Shanti)',
    89: 'Same Nakshatra Birth Remedies (Eka-Nakshatra Janma Shanti)',
    90: 'Sankranti / Solar Ingress Birth Remedies (Sankranti Janma Shanti)',
    91: 'Eclipse Birth Remedies (Grahana Janma Shanti)',
    92: 'Gandanta Birth Remedies (Gandanta Janma Shanti)',
    93: 'Abhukta Moola Birth Remedies (Abhukta Moola Shanti)',
    94: 'Jyeshtha Gandanta Remedies (Jyeshthadi Ganda Shanti)',
    95: 'Tritara Birth Remedies (Tritara Janma Shanti)',
    96: 'Unnatural Birth and Delivery Anomalies (Prasava Vikara Shanti)',
    97: 'Conclusion of the Shastra (Upasamhara Adhyaya)'
}

FILE_CHAPTER_RANGES = [
    ('par0110', 1, 10),
    ('par1120', 11, 20),
    ('par2130', 21, 30),
    ('par3140', 31, 40),
    ('par4145', 41, 45),
    ('par4650', 46, 50),
    ('par5160', 51, 60),
    ('par6170', 61, 70),
    ('par7180', 71, 80),
    ('par8190', 81, 90),
    ('par9197', 91, 97)
]

def clean_text_for_search(text):
    """Normalize text for full-text search indexing."""
    cleaned = re.sub(r'[।॥\d\s\|\.,;:\-\(\)]+', ' ', text)
    return cleaned.strip()

def parse_html_files():
    """Extract chapters and verses from HTML files."""
    chapters = {}
    for base, start_ch, end_ch in FILE_CHAPTER_RANGES:
        fpath = os.path.join(BPHS_DIR, f"{base}.html")
        if not os.path.exists(fpath):
            continue
        with open(fpath, "r", encoding="utf-8") as f:
            html = f.read()
            
        idx = re.search(r'<pre[^>]*>', html, re.I)
        if not idx:
            continue
        body = html[idx.end():]
        body = re.sub(r'</pre>.*', '', body, flags=re.I | re.DOTALL)
        lines = [re.sub(r'<[^>]+>', '', l).strip() for l in body.split('\n')]
        
        current_ch_num = start_ch
        current_verses = []
        current_verse_lines = []
        current_title = ''
        
        for line in lines:
            if not line:
                continue
                
            # Check chapter heading
            ch_m = re.search(r'^(?:[^\n।॥]*?(?:ध्याय|ध्यय|द्याय)[^\n।॥]*?)\s*॥\s*([०-९]+)\s*॥$', line)
            if ch_m:
                detected_num = parse_deva_num(ch_m.group(1))
                if start_ch <= detected_num <= end_ch:
                    if current_verse_lines:
                        current_verses.append({
                            'verse_num': len(current_verses) + 1,
                            'sanskrit': '\n'.join(current_verse_lines)
                        })
                        current_verse_lines = []
                    if current_verses:
                        chapters[current_ch_num] = {
                            'chapter_num': current_ch_num,
                            'title_sanskrit': current_title,
                            'source_file': f"{base}.html",
                            'verses': current_verses
                        }
                        current_verses = []
                    current_ch_num = detected_num
                    current_title = line
                    continue
                    
            # Check verse end
            v_m = re.search(r'॥\s*([०-९]+)\s*॥$', line)
            if v_m:
                v_num = parse_deva_num(v_m.group(1))
                current_verse_lines.append(line)
                current_verses.append({
                    'verse_num': v_num,
                    'sanskrit': '\n'.join(current_verse_lines)
                })
                current_verse_lines = []
            else:
                current_verse_lines.append(line)
                
        if current_verse_lines:
            current_verses.append({
                'verse_num': len(current_verses) + 1,
                'sanskrit': '\n'.join(current_verse_lines)
            })
        if current_verses:
            chapters[current_ch_num] = {
                'chapter_num': current_ch_num,
                'title_sanskrit': current_title,
                'source_file': f"{base}.html",
                'verses': current_verses
            }
            
    return chapters

def parse_itx_files():
    """Extract transliterated verses from ITX files."""
    itx_chapters = {}
    for base, start_ch, end_ch in FILE_CHAPTER_RANGES:
        fpath = os.path.join(BPHS_DIR, f"{base}.itx")
        if not os.path.exists(fpath):
            continue
        with open(fpath, "r", encoding="utf-8") as f:
            itx_text = f.read()
            
        lines = [l.strip() for l in itx_text.split('\n')]
        current_ch_num = start_ch
        current_verses = []
        current_verse_lines = []
        current_title = ''
        
        for line in lines:
            if not line or line.startswith('%'):
                continue
            if line.startswith('\\'):
                m_sec = re.search(r'\\(?:section|subsection)\{([^}]+)\}', line)
                if m_sec:
                    line = m_sec.group(1).strip()
                else:
                    continue
                    
            ch_m = re.search(r'^(?:[^\n|]*?(?:adhyAya|adhyaya|dhyAya|dhyaya)[^\n|]*?)\s*\|\|\s*(\d+)\s*\|\|$', line, re.I)
            if ch_m:
                detected_num = int(ch_m.group(1))
                if start_ch <= detected_num <= end_ch:
                    if current_verse_lines:
                        current_verses.append({
                            'verse_num': len(current_verses) + 1,
                            'translit': '\n'.join(current_verse_lines)
                        })
                        current_verse_lines = []
                    if current_verses:
                        itx_chapters[current_ch_num] = {
                            'title_translit': current_title,
                            'verses': current_verses
                        }
                        current_verses = []
                    current_ch_num = detected_num
                    current_title = line
                    continue
                    
            v_m = re.search(r'\|\|\s*(\d+)\s*\|\|$', line)
            if v_m:
                v_num = int(v_m.group(1))
                current_verse_lines.append(line)
                current_verses.append({
                    'verse_num': v_num,
                    'translit': '\n'.join(current_verse_lines)
                })
                current_verse_lines = []
            else:
                current_verse_lines.append(line)
                
        if current_verse_lines:
            current_verses.append({
                'verse_num': len(current_verses) + 1,
                'translit': '\n'.join(current_verse_lines)
            })
        if current_verses:
            itx_chapters[current_ch_num] = {
                'title_translit': current_title,
                'verses': current_verses
            }
            
    return itx_chapters

def build_database():
    print("[*] Parsing Sanskrit Devanagari text...")
    deva_data = parse_html_files()
    print(f"    Extracted {len(deva_data)} chapters from HTML.")
    
    print("[*] Parsing ITRANS transliterated text...")
    itx_data = parse_itx_files()
    print(f"    Extracted {len(itx_data)} chapters from ITX.")
    
    # Merge and build JSON structure
    merged_data = []
    total_verses = 0
    
    for ch_num in range(1, 98):
        deva_ch = deva_data.get(ch_num, {})
        itx_ch = itx_data.get(ch_num, {})
        
        title_sanskrit = deva_ch.get('title_sanskrit', f"अध्यायः {ch_num}")
        title_translit = itx_ch.get('title_translit', f"adhyaya {ch_num}")
        title_english = CHAPTER_ENGLISH_TITLES.get(ch_num, f"Chapter {ch_num}")
        source_file = deva_ch.get('source_file', '')
        
        deva_verses = deva_ch.get('verses', [])
        itx_verses = itx_ch.get('verses', [])
        
        itx_map = {v['verse_num']: v['translit'] for v in itx_verses}
        
        merged_verses = []
        for v in deva_verses:
            v_num = v['verse_num']
            s_text = v['sanskrit']
            t_text = itx_map.get(v_num, '')
            merged_verses.append({
                'verse_num': v_num,
                'sanskrit': s_text,
                'translit': t_text
            })
            total_verses += 1
            
        merged_data.append({
            'chapter_num': ch_num,
            'title_sanskrit': title_sanskrit,
            'title_translit': title_translit,
            'title_english': title_english,
            'source_file': source_file,
            'total_verses': len(merged_verses),
            'verses': merged_verses
        })
        
    print(f"[+] Total Chapters: {len(merged_data)} | Total Verses: {total_verses}")
    
    # Save JSON database
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump({
            'shastra': 'Brihat Parashara Hora Shastra',
            'author': 'Maharishi Parashara',
            'total_chapters': len(merged_data),
            'total_verses': total_verses,
            'chapters': merged_data
        }, f, ensure_ascii=False, indent=2)
    print(f"[+] Saved JSON Database: {OUTPUT_JSON}")
    
    # Build SQLite Database
    if os.path.exists(OUTPUT_DB):
        os.remove(OUTPUT_DB)
        
    conn = sqlite3.connect(OUTPUT_DB)
    cur = conn.cursor()
    
    # Create tables
    cur.execute("""
        CREATE TABLE chapters (
            chapter_num INTEGER PRIMARY KEY,
            title_sanskrit TEXT,
            title_translit TEXT,
            title_english TEXT,
            source_file TEXT,
            total_verses INTEGER
        )
    """)
    
    cur.execute("""
        CREATE TABLE verses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chapter_num INTEGER,
            verse_num INTEGER,
            sanskrit TEXT,
            translit TEXT,
            clean_sanskrit TEXT,
            FOREIGN KEY (chapter_num) REFERENCES chapters(chapter_num)
        )
    """)
    
    cur.execute("CREATE INDEX idx_verses_chap_num ON verses(chapter_num, verse_num);")
    
    # Full Text Search virtual table
    cur.execute("""
        CREATE VIRTUAL TABLE verses_fts USING fts5(
            chapter_num UNINDEXED,
            verse_num UNINDEXED,
            title_sanskrit,
            title_english,
            sanskrit,
            translit,
            tokenize = 'unicode61'
        )
    """)
    
    for ch in merged_data:
        cur.execute("""
            INSERT INTO chapters (chapter_num, title_sanskrit, title_translit, title_english, source_file, total_verses)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            ch['chapter_num'],
            ch['title_sanskrit'],
            ch['title_translit'],
            ch['title_english'],
            ch['source_file'],
            ch['total_verses']
        ))
        
        for v in ch['verses']:
            clean_s = clean_text_for_search(v['sanskrit'])
            cur.execute("""
                INSERT INTO verses (chapter_num, verse_num, sanskrit, translit, clean_sanskrit)
                VALUES (?, ?, ?, ?, ?)
            """, (
                ch['chapter_num'],
                v['verse_num'],
                v['sanskrit'],
                v['translit'],
                clean_s
            ))
            
            cur.execute("""
                INSERT INTO verses_fts (chapter_num, verse_num, title_sanskrit, title_english, sanskrit, translit)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                ch['chapter_num'],
                v['verse_num'],
                ch['title_sanskrit'],
                ch['title_english'],
                v['sanskrit'],
                v['translit']
            ))
            
    conn.commit()
    conn.close()
    print(f"[+] Saved SQLite FTS5 Database: {OUTPUT_DB}")

if __name__ == "__main__":
    build_database()
