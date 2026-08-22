#!/usr/bin/env python3
"""
Comprehensive Database Builder for Classical Jyotisha Sanskrit Scriptures.
Builds SQLite databases (with FTS5 full-text search) and JSON databases for all 10 classical texts
utilized in Ernst Wilhelm's Kala astrological framework:

1. Brihat Parashara Hora Shastra (Maharishi Parashara)
2. Brihat Jataka (Varahamihira)
3. Phaladeepika (Mantreswara)
4. Jataka Parijata (Vaidyanatha Dikshita)
5. Taittiriya Brahmana / Nakshatra Sutras (Krishna Yajurveda)
6. Upadesa Sutras / Jaimini Sutras (Sage Jaimini)
7. Saravali (Kalyana Varma)
8. Sarvartha Chintamani (Acharya Venkatesha)
9. Jataka Tattva (Mahadeva Pathaka)
10. Bhavartha Ratnakara (Sri Ramanujacharya)
"""

import os
import sys
import re
import json
import sqlite3

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from indic_transliteration import sanscript
SANSKRIT_DIR = os.path.join(BASE_DIR, "source-material", "sanskrit_texts")

DEVANAGARI_NUMERALS = {'०':0, '१':1, '२':2, '३':3, '४':4, '५':5, '६':6, '७':7, '८':8, '९':9}

def parse_deva_num(s):
    res = 0
    found = False
    for ch in str(s):
        if ch in DEVANAGARI_NUMERALS:
            res = res * 10 + DEVANAGARI_NUMERALS[ch]
            found = True
        elif ch.isdigit():
            res = res * 10 + int(ch)
            found = True
    return res if found else 0

def clean_text_for_search(text):
    cleaned = re.sub(r'[।॥\d\s\|\.,;:\-\(\)\\\{\}\%]+', ' ', text)
    return cleaned.strip()

def create_sqlite_database(db_path, chapters_data, scripture_name, author_name):
    """Create a standardized SQLite database with FTS5 for a scripture."""
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE metadata (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    cur.execute("INSERT INTO metadata VALUES ('scripture', ?), ('author', ?)", (scripture_name, author_name))

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

    total_verses = 0
    for ch in chapters_data:
        cur.execute("""
            INSERT INTO chapters (chapter_num, title_sanskrit, title_translit, title_english, source_file, total_verses)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            ch['chapter_num'],
            ch.get('title_sanskrit', ''),
            ch.get('title_translit', ''),
            ch.get('title_english', ''),
            ch.get('source_file', ''),
            len(ch.get('verses', []))
        ))

        for v in ch.get('verses', []):
            clean_s = clean_text_for_search(v.get('sanskrit', ''))
            cur.execute("""
                INSERT INTO verses (chapter_num, verse_num, sanskrit, translit, clean_sanskrit)
                VALUES (?, ?, ?, ?, ?)
            """, (
                ch['chapter_num'],
                v['verse_num'],
                v.get('sanskrit', ''),
                v.get('translit', ''),
                clean_s
            ))

            cur.execute("""
                INSERT INTO verses_fts (chapter_num, verse_num, title_sanskrit, title_english, sanskrit, translit)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                ch['chapter_num'],
                v['verse_num'],
                ch.get('title_sanskrit', ''),
                ch.get('title_english', ''),
                v.get('sanskrit', ''),
                v.get('translit', '')
            ))
            total_verses += 1

    conn.commit()
    conn.close()
    return total_verses

def save_json_database(json_path, scripture_name, author_name, chapters_data):
    """Save structured JSON database for a scripture."""
    total_verses = sum(len(c.get('verses', [])) for c in chapters_data)
    data = {
        'shastra': scripture_name,
        'author': author_name,
        'total_chapters': len(chapters_data),
        'total_verses': total_verses,
        'chapters': chapters_data
    }
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return total_verses


# ==============================================================================
# 1. BRIHAT PARASHARA HORA SHASTRA (BPHS)
# ==============================================================================
def build_bphs():
    print("[*] Building Brihat Parashara Hora Shastra (BPHS)...")
    from scripts.build_bphs_database import build_database as bphs_builder
    bphs_builder()
    
    # Copy/Link directly into bphs directory
    bphs_dir = os.path.join(SANSKRIT_DIR, "bphs")
    db_src = os.path.join(SANSKRIT_DIR, "bphs.db")
    json_src = os.path.join(SANSKRIT_DIR, "bphs_database.json")
    
    db_dst = os.path.join(bphs_dir, "bphs.db")
    json_dst = os.path.join(bphs_dir, "bphs_database.json")
    
    import shutil
    shutil.copyfile(db_src, db_dst)
    shutil.copyfile(json_src, json_dst)
    print(f"    [+] BPHS built successfully in {bphs_dir}")


# ==============================================================================
# 2. BRIHAT JATAKA (Varahamihira)
# ==============================================================================
BRIHAT_JATAKA_TITLES = {
    1: ("राशिप्रभेदः", "rAshiprabhedaH", "Sign Characteristics and Planetary Divisions"),
    2: ("ग्रहगुणाध्यायः", "grahaguNAdhyAyaH", "Planetary Characteristics, Gunas and Strengths"),
    3: ("वियोनिजन्माध्यायः", "viyonijanmAdhyAyaH", "Animal and Manifold Non-Human Births"),
    4: ("निषेकाध्यायः", "niShekAdhyAyaH", "Impregnation and Conception Details"),
    5: ("जन्मकाललक्षणाध्यायः", "janmakAlalakShaNAdhyAyaH", "Circumstances of Birth Moment"),
    6: ("अरिष्टाध्यायः", "ariShTAdhyAyaH", "Early Mortality and Fatal Planetary Afflictions"),
    7: ("आयुर्दायाध्यायः", "AyurdAyAdhyAyaH", "Longevity Computations and Span of Life"),
    8: ("दशान्तर्दशाध्यायः", "dashAntardashAdhyAyaH", "Planetary Major and Sub-Periods"),
    9: ("अष्टकवर्गाध्यायः", "aShTakavargAdhyAyaH", "Ashtakavarga Eightfold Matrix Computations"),
    10: ("कर्मजीवाध्यायः", "karmajIvAdhyAyaH", "Livelihood, Career and Profession"),
    11: ("राजयोगाध्यायः", "rAjayogAdhyAyaH", "Royal Status and Power Combinations"),
    12: ("नाभसयोगाध्यायः", "nAbhasayogAdhyAyaH", "Celestial Geometrical Patterns (Nabhasa Yogas)"),
    13: ("चन्द्रयोगाध्यायः", "chandrayogAdhyAyaH", "Lunar Combinations and Moon Configurations"),
    14: ("द्विग्रहयोगाध्यायः", "dvigrahayogAdhyAyaH", "Two-Planet Conjunction Combinations"),
    15: ("प्रव्रज्यायोगाध्यायः", "pravrajyAyogAdhyAyaH", "Renunciation, Monasticism and Asceticism"),
    16: ("राशिशीलाध्यायः", "rAshishIlAdhyAyaH", "Effects of Planetary Placements in Signs"),
    17: ("भावफलाध्यायः", "bhAvaphalAdhyAyaH", "Effects of Planets Across the 12 Houses"),
    18: ("ग्रहदृष्टिफलाध्यायः", "grahadR^iShTiphalAdhyAyaH", "Planetary Aspect Combinations and Results"),
    19: ("दशाफलाध्यायः", "dashAphalAdhyAyaH", "Detailed Predictions of Planetary Dasa Periods"),
    20: ("भावकारकाध्यायः", "bhAvakArakAdhyAyaH", "Houses and Karakas Determinations"),
    21: ("आश्रययोगाध्यायः", "AshrayayogAdhyAyaH", "Special Sign Placement Yogas"),
    22: ("संकीर्णकाध्यायः", "saMkIrNakAdhyAyaH", "Miscellaneous Astrological Rules and Permutations"),
    23: ("अनिष्टाध्यायः", "aniShTAdhyAyaH", "Inauspicious Placements and Misfortunes"),
    24: ("स्त्रीजातकाध्यायः", "strIjAtakAdhyAyaH", "Female Horoscopy and Considerations"),
    25: ("निर्याणाध्यायः", "niryANAdhyAyaH", "Manner, Nature and Timing of Death"),
    26: ("नष्टजातकाध्यायः", "naShTajAtakAdhyAyaH", "Lost Horoscopy and Unknown Birth Time"),
    27: ("द्रेष्काणाध्यायः", "dreShkANAdhyAyaH", "Decanates (Drekkana) and Bodily Limbs"),
    28: ("उपसंहाराध्यायः", "upasaMhArAdhyAyaH", "Epilogue and Conclusion of Brihat Jataka")
}

def build_brihat_jataka():
    print("[*] Building Brihat Jataka (Varahamihira)...")
    dir_path = os.path.join(SANSKRIT_DIR, "brihat_jataka")
    itx_path = os.path.join(dir_path, "brihajjAtakam.itx")

    with open(itx_path, 'r', encoding='utf-8') as f:
        text = f.read()

    lines = [l.strip() for l in text.splitlines()]
    chapters = []
    curr_ch = None
    curr_lines = []

    for line in lines:
        if not line or line.startswith('%') or line.startswith('\\') or line.startswith('#'):
            continue
        
        # Check chapter start
        ch_m = re.search(r'([a-zA-Z\^\~]+)\.adhyAyaH', line, re.I)
        if ch_m:
            if curr_ch and curr_lines:
                v_text = ' '.join(curr_lines)
                curr_ch['verses'].append({
                    'verse_num': len(curr_ch['verses']) + 1,
                    'translit': v_text,
                    'sanskrit': sanscript.transliterate(v_text, sanscript.ITRANS, sanscript.DEVANAGARI)
                })
                curr_lines = []
            if curr_ch:
                chapters.append(curr_ch)

            ch_num = len(chapters) + 1
            meta = BRIHAT_JATAKA_TITLES.get(ch_num, (f"अध्यायः {ch_num}", f"adhyAya {ch_num}", f"Chapter {ch_num}"))
            curr_ch = {
                'chapter_num': ch_num,
                'title_sanskrit': meta[0],
                'title_translit': meta[1],
                'title_english': meta[2],
                'source_file': 'brihajjAtakam.itx',
                'verses': []
            }
            continue

        v_m = re.search(r'\|\|\s*(\d+)\s*\|\|', line)
        if v_m:
            v_num = int(v_m.group(1))
            curr_lines.append(line)
            v_text = ' '.join(curr_lines)
            if curr_ch:
                curr_ch['verses'].append({
                    'verse_num': v_num,
                    'translit': v_text,
                    'sanskrit': sanscript.transliterate(v_text, sanscript.ITRANS, sanscript.DEVANAGARI)
                })
            curr_lines = []
        else:
            curr_lines.append(line)

    if curr_ch and curr_lines:
        v_text = ' '.join(curr_lines)
        curr_ch['verses'].append({
            'verse_num': len(curr_ch['verses']) + 1,
            'translit': v_text,
            'sanskrit': sanscript.transliterate(v_text, sanscript.ITRANS, sanscript.DEVANAGARI)
        })
    if curr_ch:
        chapters.append(curr_ch)

    db_path = os.path.join(dir_path, "brihat_jataka.db")
    json_path = os.path.join(dir_path, "brihat_jataka_database.json")
    v_cnt = create_sqlite_database(db_path, chapters, "Brihat Jataka", "Varahamihira")
    save_json_database(json_path, "Brihat Jataka", "Varahamihira", chapters)
    print(f"    [+] Brihat Jataka: {len(chapters)} chapters, {v_cnt} verses -> {db_path}")


# ==============================================================================
# 3. PHALADEEPIKA (Mantreswara)
# ==============================================================================
PHALADEEPIKA_TITLES = {
    1: ("संज्ञाऽध्यायः", "saMj~nAdhyAyaH", "Definitions, Zodiac Signs & Fundamental Astrological Symbols"),
    2: ("ग्रहगुणाध्यायः", "grahaguNAdhyAyaH", "Planetary Characteristics, Natures & Descriptions"),
    3: ("ग्रहबलाध्यायः", "grahabalAdhyAyaH", "Planetary Strengths, Shadbala & Exaltation Points"),
    4: ("भावकारकाध्यायः", "bhAvakArakAdhyAyaH", "House Significations & Primary Astrological Portfolios"),
    5: ("विशेषलग्नाध्यायः", "visheShalagnAdhyAyaH", "Special Lagnas, Upagrahas & Secondary Ascendants"),
    6: ("योगाध्यायः", "yogAdhyAyaH", "Planetary Yogas & Major Planetary Combinations"),
    7: ("राजयोगाध्यायः", "rAjayogAdhyAyaH", "Royal Combinations, Fame, Wealth and Status Yogas"),
    8: ("विविधयोगाध्यायः", "vividhayogAdhyAyaH", "Miscellaneous Auspicious and Inauspicious Yogas"),
    9: ("भावफलाध्यायः", "bhAvaphalAdhyAyaH", "Effects of Planetary Placements in the 12 Houses"),
    10: ("भावेशाध्यायः", "bhAveshAdhyAyaH", "Results of the 12 House Lords Across All Houses"),
    11: ("स्त्रीजातकाध्यायः", "strIjAtakAdhyAyaH", "Female Horoscopy, Marriage, and Children"),
    12: ("गर्भाधानाध्यायः", "garbhAdhAnAdhyAyaH", "Conception, Pregnancy and Delivery Timing"),
    13: ("बालारिष्टाध्यायः", "bAlAriShTAdhyAyaH", "Early Childhood Afflictions & Infant Mortality"),
    14: ("आयुर्दायाध्यायः", "AyurdAyAdhyAyaH", "Longevity Calculations and Span of Life"),
    15: ("भावविवेकाध्यायः", "bhAvavivekAdhyAyaH", "Comprehensive Assessment & Judgment of Houses"),
    16: ("कालचक्रदशाध्यायः", "kAlachakradashAdhyAyaH", "Kalachakra Dasa Principles and Structures"),
    17: ("अष्टकवर्गाध्यायः", "aShTakavargAdhyAyaH", "Foundations of the Eightfold Ashtakavarga System"),
    18: ("अष्टकवर्गफलाध्यायः", "aShTakavargaphalAdhyAyaH", "Applications and Interpretations of Ashtakavarga"),
    19: ("दशाफलसामान्याध्यायः", "dashAphalasAmAnyAdhyAyaH", "General Principles of Planetary Dasa Results"),
    20: ("महादशाफलाध्यायः", "mahAdashAphalAdhyAyaH", "Predictions for Individual Planet Mahadasas"),
    21: ("अन्तर्दशाफलाध्यायः", "antardashAphalAdhyAyaH", "Sub-Period Effects (Antardasa Predictions)"),
    22: ("कालचक्रदशाफलाध्यायः", "kAlachakradashAphalAdhyAyaH", "Results of Kalachakra Dasa Sub-Divisions"),
    23: ("गोचरफलाध्यायः", "gocharaphalAdhyAyaH", "Transits of Planets (Gochara Principles)"),
    24: ("विशेषगोचराध्यायः", "visheShagocharAdhyAyaH", "Special Transits from Moon and Ashtakavarga"),
    25: ("उपग्रहगोचराध्यायः", "upagrahagocharAdhyAyaH", "Transits of Shadow Planets and Non-Luminous Upagrahas"),
    26: ("रोगनिर्णयाध्यायः", "roganirNayAdhyAyaH", "Medical Astrology, Diseases and Bodily Afflictions"),
    27: ("प्रव्रज्यायोगाध्यायः", "pravrajyAyogAdhyAyaH", "Monasticism, Asceticism and Renunciation Yogas"),
    28: ("उपसंहाराध्यायः", "upasaMhArAdhyAyaH", "Epilogue and Conclusion of Phaladeepika")
}

def build_phaladeepika():
    print("[*] Building Phaladeepika (Mantreswara)...")
    dir_path = os.path.join(SANSKRIT_DIR, "phaladeepika")
    itx_path = os.path.join(dir_path, "phaladIpika.itx")

    with open(itx_path, 'r', encoding='utf-8') as f:
        text = f.read()

    lines = [l.strip() for l in text.splitlines()]
    chapters = []
    curr_ch = None
    curr_lines = []

    for line in lines:
        if not line or line.startswith('%') or line.startswith('#'):
            continue
        
        # Check chapter start \section{...}
        ch_m = re.search(r'\\section\{([^}]+)\}', line)
        if ch_m:
            if curr_ch and curr_lines:
                v_text = ' '.join(curr_lines)
                curr_ch['verses'].append({
                    'verse_num': len(curr_ch['verses']) + 1,
                    'translit': v_text,
                    'sanskrit': sanscript.transliterate(v_text, sanscript.ITRANS, sanscript.DEVANAGARI)
                })
                curr_lines = []
            if curr_ch:
                chapters.append(curr_ch)

            ch_num = len(chapters) + 1
            meta = PHALADEEPIKA_TITLES.get(ch_num, (f"अध्यायः {ch_num}", f"adhyAya {ch_num}", f"Chapter {ch_num}"))
            curr_ch = {
                'chapter_num': ch_num,
                'title_sanskrit': meta[0],
                'title_translit': meta[1],
                'title_english': meta[2],
                'source_file': 'phaladIpika.itx',
                'verses': []
            }
            continue

        if line.startswith('\\'):
            continue

        v_m = re.search(r'\|\|\s*(\d+)\s*\|\|', line)
        if v_m:
            v_num = int(v_m.group(1))
            curr_lines.append(line)
            v_text = ' '.join(curr_lines)
            if curr_ch:
                curr_ch['verses'].append({
                    'verse_num': v_num,
                    'translit': v_text,
                    'sanskrit': sanscript.transliterate(v_text, sanscript.ITRANS, sanscript.DEVANAGARI)
                })
            curr_lines = []
        else:
            curr_lines.append(line)

    if curr_ch and curr_lines:
        v_text = ' '.join(curr_lines)
        curr_ch['verses'].append({
            'verse_num': len(curr_ch['verses']) + 1,
            'translit': v_text,
            'sanskrit': sanscript.transliterate(v_text, sanscript.ITRANS, sanscript.DEVANAGARI)
        })
    if curr_ch:
        chapters.append(curr_ch)

    db_path = os.path.join(dir_path, "phaladeepika.db")
    json_path = os.path.join(dir_path, "phaladeepika_database.json")
    v_cnt = create_sqlite_database(db_path, chapters, "Phaladeepika", "Mantreswara")
    save_json_database(json_path, "Phaladeepika", "Mantreswara", chapters)
    print(f"    [+] Phaladeepika: {len(chapters)} chapters, {v_cnt} verses -> {db_path}")


# ==============================================================================
# 4. JATAKA PARIJATA (Vaidyanatha Dikshita)
# ==============================================================================
JATAKA_PARIJATA_TITLES = {
    1: ("राशिशीलाध्यायः", "rAshishIlAdhyAyaH", "Sign Characteristics, Dignities & Planetary Divisions"),
    2: ("ग्रहस्वरूपगुणाध्यायः", "grahasvarUpaguNAdhyAyaH", "Planetary Natures, Gunas and Strengths"),
    3: ("वियोनिजन्माध्यायः", "viyonijanmAdhyAyaH", "Animal & Manifold Birth Formations"),
    4: ("अरिष्टाध्यायः", "ariShTAdhyAyaH", "Fatal Afflictions and Infant Mortality"),
    5: ("आयुर्दायाध्यायः", "AyurdAyAdhyAyaH", "Longevity Calculations and Span of Life"),
    6: ("जातकभङ्गाध्यायः", "jAtakabha~NgAdhyAyaH", "Cancellation of Yogas and Afflictions (Arishta Bhanga)"),
    7: ("राजयोगाध्यायः", "rAjayogAdhyAyaH", "Royal Combinations, Power and High Eminence"),
    8: ("द्व्यादिग्रहयोगाध्यायः", "dvyAdigrahayogAdhyAyaH", "Conjunctions of Two or More Planets"),
    9: ("मान्द्यादिफलाध्यायः", "mAndyAdiphalAdhyAyaH", "Effects of Gulika, Mandi and Shadow Upagrahas"),
    10: ("अष्टकवर्गाध्यायः", "aShTakavargAdhyAyaH", "The Ashtakavarga System and Transits"),
    11: ("प्रथमाद्वितीयभावफलाध्यायः", "prathamadvitIyabhAvaphalAdhyAyaH", "Results of the 1st & 2nd Houses (Tanu & Dhana)"),
    12: ("तृतीयाचतुर्थभावफलाध्यायः", "tR^itIyachaturthabhAvaphalAdhyAyaH", "Results of the 3rd & 4th Houses (Sahaja & Sukha)"),
    13: ("पञ्चमषष्ठभावफलाध्यायः", "pa~nchamaShaShThabhAvaphalAdhyAyaH", "Results of the 5th & 6th Houses (Putra & Shatru)"),
    14: ("सप्तमाष्टमनवमभावफलाध्यायः", "saptamAShTamanavamabhAvaphalAdhyAyaH", "Results of the 7th, 8th & 9th Houses (Kalatra, Ayur & Bhagya)"),
    15: ("दशमैकादशद्वादशभावफलाध्यायः", "dashamaikAdashadvAdashabhAvaphalAdhyAyaH", "Results of the 10th, 11th & 12th Houses (Karma, Labha & Vyaya)"),
    16: ("स्त्रीजातकाध्यायः", "strIjAtakAdhyAyaH", "Female Horoscopy and Marriage Analysis"),
    17: ("कालचक्रदशाध्यायः", "kAlachakradashAdhyAyaH", "Kalachakra Dasa System and Timing"),
    18: ("दशाफलाध्यायः", "dashAphalAdhyAyaH", "Planetary Period Predictions (Dasa Phala)")
}

def build_jataka_parijata():
    print("[*] Building Jataka Parijata (Vaidyanatha Dikshita)...")
    dir_path = os.path.join(SANSKRIT_DIR, "jataka_parijata")
    itx_path = os.path.join(dir_path, "jAtakapArijAtaH.itx")

    with open(itx_path, 'r', encoding='utf-8') as f:
        text = f.read()

    lines = [l.strip() for l in text.splitlines()]
    chapters = []
    curr_ch = None
    curr_lines = []

    for line in lines:
        if not line or line.startswith('%') or line.startswith('#'):
            continue
        
        # Check chapter start \section{...}
        ch_m = re.search(r'\\section\{([^}]+)\}', line)
        if ch_m:
            sec_title = ch_m.group(1).strip()
            if 'upasaMhAra' in sec_title.lower():
                continue
            if curr_ch and curr_lines:
                v_text = ' '.join(curr_lines)
                curr_ch['verses'].append({
                    'verse_num': len(curr_ch['verses']) + 1,
                    'translit': v_text,
                    'sanskrit': sanscript.transliterate(v_text, sanscript.ITRANS, sanscript.DEVANAGARI)
                })
                curr_lines = []
            if curr_ch:
                chapters.append(curr_ch)

            ch_num = len(chapters) + 1
            meta = JATAKA_PARIJATA_TITLES.get(ch_num, (f"अध्यायः {ch_num}", f"adhyAya {ch_num}", f"Chapter {ch_num}"))
            curr_ch = {
                'chapter_num': ch_num,
                'title_sanskrit': meta[0],
                'title_translit': meta[1],
                'title_english': meta[2],
                'source_file': 'jAtakapArijAtaH.itx',
                'verses': []
            }
            continue

        if line.startswith('\\'):
            continue

        v_m = re.search(r'\|\|\s*(\d+)\s*\|\|', line)
        if v_m:
            v_num = int(v_m.group(1))
            curr_lines.append(line)
            v_text = ' '.join(curr_lines)
            if curr_ch:
                curr_ch['verses'].append({
                    'verse_num': v_num,
                    'translit': v_text,
                    'sanskrit': sanscript.transliterate(v_text, sanscript.ITRANS, sanscript.DEVANAGARI)
                })
            curr_lines = []
        else:
            curr_lines.append(line)

    if curr_ch and curr_lines:
        v_text = ' '.join(curr_lines)
        curr_ch['verses'].append({
            'verse_num': len(curr_ch['verses']) + 1,
            'translit': v_text,
            'sanskrit': sanscript.transliterate(v_text, sanscript.ITRANS, sanscript.DEVANAGARI)
        })
    if curr_ch:
        chapters.append(curr_ch)

    db_path = os.path.join(dir_path, "jataka_parijata.db")
    json_path = os.path.join(dir_path, "jataka_parijata_database.json")
    v_cnt = create_sqlite_database(db_path, chapters, "Jataka Parijata", "Vaidyanatha Dikshita")
    save_json_database(json_path, "Jataka Parijata", "Vaidyanatha Dikshita", chapters)
    print(f"    [+] Jataka Parijata: {len(chapters)} chapters, {v_cnt} verses -> {db_path}")


# ==============================================================================
# 5. TAITTIRIYA BRAHMANA NAKSHATRA SUTRAS (Nakshatra Suktam)
# ==============================================================================
NAKSHATRA_NAMES = [
    (1, "कृत्तिका", "kR^ittikA", "Krittika (Deity: Agni)", "Pleiades"),
    (2, "रोहिणी", "rohiNI", "Rohini (Deity: Prajapati)", "Aldebaran"),
    (3, "मृगशीर्ष", "mR^igashIrSha", "Mrigashira (Deity: Soma / Chandra)", "Orion's Head"),
    (4, "आर्द्रा", "ArdrA", "Ardra (Deity: Rudra)", "Betelgeuse"),
    (5, "पुनर्वसु", "punarvasu", "Punarvasu (Deity: Aditi)", "Castor and Pollux"),
    (6, "पुष्य", "puShya", "Pushya (Deity: Brihaspati)", "Praesepe"),
    (7, "आश्लेषा", "AshleShA", "Ashlesha (Deity: Sarpas)", "Hydrae"),
    (8, "मघा", "maghA", "Magha (Deity: Pitris)", "Regulus"),
    (9, "पूर्वफाल्गुनी", "pUrvaphalgunI", "Purva Phalguni (Deity: Bhaga)", "Delta Leonis"),
    (10, "उत्तरफाल्गुनी", "uttaraphalgunI", "Uttara Phalguni (Deity: Aryaman)", "Denebola"),
    (11, "हस्त", "hasta", "Hasta (Deity: Savitar)", "Corvus"),
    (12, "चित्रा", "chitrA", "Chitra (Deity: Tvashtar)", "Spica"),
    (13, "स्वाती", "svAtI", "Swati (Deity: Vayu)", "Arcturus"),
    (14, "विशाखा", "vishAkhA", "Vishakha (Deity: Indragni)", "Libra Stars"),
    (15, "अनुराधा", "anurAdhA", "Anuradha (Deity: Mitra)", "Delta Scorpii"),
    (16, "ज्येष्ठा", "jyeShThA", "Jyeshtha (Deity: Indra)", "Antares"),
    (17, "मूला", "mUlA", "Mula (Deity: Nirriti / Prajapati)", "Galactic Center"),
    (18, "पूर्वाषाढा", "pUrvAShADhA", "Purva Ashadha (Deity: Apas)", "Kaus Media"),
    (19, "उत्तराषाढा", "uttarAShADhA", "Uttara Ashadha (Deity: Vishvedevas)", "Nunki"),
    (20, "अभिजित्", "abhijit", "Abhijit (Deity: Brahma)", "Vega"),
    (21, "श्रवण", "shravaNa", "Shravana (Deity: Vishnu)", "Altair"),
    (22, "धनिष्ठा", "dhaniShThA", "Dhanishta (Deity: Vasus)", "Delphini"),
    (23, "शतभिषक्", "shatabhiShak", "Shatabhisha (Deity: Varuna)", "Aquarii"),
    (24, "पूर्वभाद्रपदा", "pUrvabhAdrapadA", "Purva Bhadrapada (Deity: Aja Ekapada)", "Markab"),
    (25, "उत्तरभाद्रपदा", "uttarabhAdrapadA", "Uttara Bhadrapada (Deity: Ahirbudhnya)", "Algenib"),
    (26, "रेवती", "revatI", "Revati (Deity: Pushan)", "Zeta Piscium"),
    (27, "अश्विनी", "ashvinI", "Ashwini (Deity: Ashvins)", "Hamal"),
    (28, "भरणी", "bharaNI", "Bharani (Deity: Yama)", "Musca / 41 Arietis")
]

def build_taittiriya_nakshatra():
    print("[*] Building Taittiriya Brahmana Nakshatra Sutras...")
    dir_path = os.path.join(SANSKRIT_DIR, "taittiriya_nakshatra")
    itx_path = os.path.join(dir_path, "nakshatra.itx")

    with open(itx_path, 'r', encoding='utf-8') as f:
        text = f.read()

    lines = [l.strip() for l in text.splitlines()]
    chapters = []
    curr_lines = []
    nak_idx = 0

    for line in lines:
        if not line or line.startswith('%') or line.startswith('\\') or line.startswith('#'):
            continue
        if line.startswith('taittirIya') or line.startswith('OM'):
            continue

        v_m = re.search(r'\.\.\s*(\d+)\s*\.\.', line)
        if v_m:
            v_num = int(v_m.group(1))
            curr_lines.append(line)
            v_text = ' '.join(curr_lines)
            
            # Clean accent marks (` ' ") for cleaner readable transliteration
            clean_translit = re.sub(r"[`'\"]", "", v_text)
            deva_v = sanscript.transliterate(clean_translit, sanscript.ITRANS, sanscript.DEVANAGARI)
            
            meta = NAKSHATRA_NAMES[nak_idx] if nak_idx < len(NAKSHATRA_NAMES) else (
                f"नक्षत्रम् {v_num}", f"nakShatra {v_num}", f"Nakshatra Mantra {v_num}", ""
            )
            nak_idx += 1

            chapters.append({
                'chapter_num': v_num,
                'title_sanskrit': meta[0],
                'title_translit': meta[1],
                'title_english': f"{meta[2]} - Star: {meta[3]}",
                'source_file': 'nakshatra.itx',
                'verses': [{
                    'verse_num': 1,
                    'translit': clean_translit,
                    'sanskrit': deva_v
                }]
            })
            curr_lines = []
        else:
            curr_lines.append(line)

    db_path = os.path.join(dir_path, "taittiriya_nakshatra.db")
    json_path = os.path.join(dir_path, "taittiriya_nakshatra_database.json")
    v_cnt = create_sqlite_database(db_path, chapters, "Taittiriya Nakshatra Sutras", "Krishna Yajurveda")
    save_json_database(json_path, "Taittiriya Nakshatra Sutras", "Krishna Yajurveda", chapters)
    print(f"    [+] Taittiriya Nakshatra: {len(chapters)} nakshatra sutras -> {db_path}")


# ==============================================================================
# 6. UPADESA SUTRAS / JAIMINI SUTRAS (Sage Jaimini)
# ==============================================================================
JAIMINI_PADA_TITLES = {
    1: ("प्रथम अध्याय - प्रथम पाद (संज्ञा, दृष्टि, अर्गला, आत्मकारक)", "1.1 Samjna, Rashi Drishti, Argala, Atmakaraka", "Significators, Aspects, Obstructions and Chara Karakas"),
    2: ("प्रथम अध्याय - द्वितीय पाद (कारकांश एवं स्वांश फल)", "1.2 Karakamsha & Swamsha Phala", "Effects of Karakamsha, Ishta Devata and Spiritual Aptitude"),
    3: ("प्रथम अध्याय - तृतीय पाद (पद फलादेश एवं धन-दारिद्र्य योग)", "1.3 Pada Phala & Dhana Yogas", "Results of Arudha Padas, Wealth & Poverty Combinations"),
    4: ("प्रथम अध्याय - चतुर्थ पाद (उपपद फलादेश एवं विवाह विचार)", "1.4 Upapada Phala & Marriage", "Analysis of Upapada Lagna, Spouse, Marriage & Progeny"),
    5: ("द्वितीय अध्याय - प्रथम पाद (आयुर्दाय एवं दीर्घायु-मध्यमायु विचार)", "2.1 Ayurdaya & Longevity", "Longevity Computation, Kakshya Vriddhi and Hrasa Rules"),
    6: ("द्वितीय अध्याय - द्वितीय पाद (रुद्र एवं महेश्वर, मारक निर्णय)", "2.2 Rudra, Maheshwara & Marakas", "Death-Inflicting Planets, Rudra & Maheshwara Determinations"),
    7: ("द्वितीय अध्याय - तृतीय पाद (मृत्यु प्रकार एवं व्याधि निर्णय)", "2.3 Nature of Death & Diseases", "Circumstances, Timing and Causes of Mortality"),
    8: ("द्वितीय अध्याय - चतुर्थ पाद (चर दशा एवं राश्यान्तर्दशा विचार)", "2.4 Chara Dasa & Rasi Periods", "Sign Dasa Progression and Timing of Major Life Events"),
    9: ("तृतीय अध्याय - प्रथम पाद (राजयोग एवं अधिकार योग)", "3.1 Raja Yogas & High Status", "Royal Combinations, Fame and Political Authority"),
    10: ("तृतीय अध्याय - द्वितीय पाद (स्त्री जातक एवं विशेष फलादेश)", "3.2 Stri Jataka & Special Considerations", "Female Horoscopy, Temperament and Special Combinations"),
    11: ("तृतीय अध्याय - तृतीय पाद (वर्णद, घटिका एवं होरा लग्न)", "3.3 Varnada, Ghatika & Special Lagnas", "Application of Varnada Lagna and Sub-Divisional Ascendants"),
    12: ("तृतीय अध्याय - चतुर्थ पाद (ब्रह्मदशा एवं स्थिर दशा निर्णय)", "3.4 Brahma Dasa & Sthira Dasa", "Brahma Dasa Computations and Longevity Confirmations"),
    13: ("चतुर्थ अध्याय - प्रथम पाद (दृग्दशा एवं त्रिकोण दशा)", "4.1 Drig Dasa & Trikona Dasa", "Vision Periods (Drig Dasa) and Trinal Progression"),
    14: ("चतुर्थ अध्याय - द्वितीय पाद (आयुर्दाय सूक्ष्म निर्णय)", "4.2 Subtle Longevity Assessments", "Advanced Corrections and Fine-tuning of Life Span"),
    15: ("चतुर्थ अध्याय - तृतीय पाद (विशेष योग एवं गोचर)", "4.3 Special Yogas & Transits", "Special Planetary Configurations and Sign Influences"),
    16: ("चतुर्थ अध्याय - चतुर्थ पाद (संन्यास एवं मोक्ष विचार)", "4.4 Sannyasa & Moksha Viveka", "Renunciation, Asceticism, Spiritual Liberation & Epilogue")
}

def build_jaimini_sutras():
    print("[*] Building Jaimini Upadesa Sutras (Sage Jaimini)...")
    dir_path = os.path.join(SANSKRIT_DIR, "jaimini_sutras")
    src_path = os.path.join(dir_path, "raw_source_1.txt")

    with open(src_path, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()

    lines = [l.strip() for l in text.splitlines() if l.strip()]
    chapters = []
    
    pada_num = 1
    curr_ch = {
        'chapter_num': pada_num,
        'title_sanskrit': JAIMINI_PADA_TITLES[pada_num][0],
        'title_translit': JAIMINI_PADA_TITLES[pada_num][1],
        'title_english': JAIMINI_PADA_TITLES[pada_num][2],
        'source_file': 'raw_source_1.txt',
        'verses': []
    }
    
    sutra_count = 0
    for line in lines:
        m = re.search(r'([^\n।॥]+?)\s*॥\s*([०-९\d]+)\s*॥', line)
        if m:
            s_text = m.group(1).strip()
            v_num = parse_deva_num(m.group(2))
            
            if len(s_text) < 2 or 'रुपये' in s_text or 'मूल्य' in s_text:
                continue
            
            try:
                t_text = sanscript.transliterate(s_text, sanscript.DEVANAGARI, sanscript.ITRANS)
            except Exception:
                t_text = s_text
                
            curr_ch['verses'].append({
                'verse_num': len(curr_ch['verses']) + 1,
                'sanskrit': s_text + " ॥ " + str(v_num) + " ॥",
                'translit': t_text + " || " + str(v_num) + " ||"
            })
            sutra_count += 1
            
            if len(curr_ch['verses']) >= 45 and pada_num < 16:
                chapters.append(curr_ch)
                pada_num += 1
                curr_ch = {
                    'chapter_num': pada_num,
                    'title_sanskrit': JAIMINI_PADA_TITLES[pada_num][0],
                    'title_translit': JAIMINI_PADA_TITLES[pada_num][1],
                    'title_english': JAIMINI_PADA_TITLES[pada_num][2],
                    'source_file': 'raw_source_1.txt',
                    'verses': []
                }
                
    if curr_ch['verses']:
        chapters.append(curr_ch)

    db_path = os.path.join(dir_path, "jaimini_sutras.db")
    json_path = os.path.join(dir_path, "jaimini_sutras_database.json")
    v_cnt = create_sqlite_database(db_path, chapters, "Jaimini Upadesa Sutras", "Sage Jaimini")
    save_json_database(json_path, "Jaimini Upadesa Sutras", "Sage Jaimini", chapters)
    print(f"    [+] Jaimini Sutras: {len(chapters)} padas, {v_cnt} sutras -> {db_path}")


# ==============================================================================
# 7. SARAVALI (Kalyana Varma)
# ==============================================================================
SARAVALI_TITLES = {
    1: ("मङ्गलाचरणं शास्त्रप्रारम्भश्च", "Invocation and Astrological Fundamentals"),
    2: ("राशिस्वरूपगुणाध्यायः", "Zodiac Sign Characteristics and Cosmic Elements"),
    3: ("ग्रहगुणाध्यायः", "Planetary Attributes, Natures and Portfolios"),
    4: ("निषेकाध्यायः", "Impregnation and Conception Judgments"),
    5: ("जन्मकाललक्षणाध्यायः", "Circumstances and Conditions of Birth"),
    6: ("बालारिष्टाध्यायः", "Early Childhood Mortality and Fatal Afflictions"),
    7: ("अरिष्टभङ्गाध्यायः", "Cancellation of Planetary Afflictions"),
    8: ("आयुर्दायाध्यायः", "Longevity Computations and Span of Life"),
    9: ("ग्रहावस्थाध्यायः", "Planetary States, Avasthas and Conditions"),
    10: ("दशाफलसामान्याध्यायः", "General Principles of Planetary Dasa Periods"),
    11: ("सूर्यमहादशाफलाध्यायः", "Sun Mahadasa Effects and Results"),
    12: ("चन्द्रमहादशाफलाध्यायः", "Moon Mahadasa Effects and Results"),
    13: ("मङ्गलमहादशाफलाध्यायः", "Mars Mahadasa Effects and Results"),
    14: ("बुधमहादशाफलाध्यायः", "Mercury Mahadasa Effects and Results"),
    15: ("गुरुमहादशाफलाध्यायः", "Jupiter Mahadasa Effects and Results"),
    16: ("शुक्रमहादशाफलाध्यायः", "Venus Mahadasa Effects and Results"),
    17: ("शनेश्चरमहादशाफलाध्यायः", "Saturn Mahadasa Effects and Results"),
    18: ("मिश्रदशाफलाध्यायः", "Mixed Dasa Periods and Secondary Transitions"),
    19: ("अन्तर्दशाफलाध्यायः", "Sub-Period (Antardasa) Effects"),
    20: ("नाभसयोगाध्यायः", "Nabhasa Celestial Geometric Combinations"),
    21: ("रविप्रभवयोगाध्यायः", "Solar Combinations and Sun Yogas"),
    22: ("चन्द्रप्रभवयोगाध्यायः", "Lunar Combinations and Moon Yogas"),
    23: ("द्विग्रहयोगाध्यायः", "Two-Planet Conjunction Combinations"),
    24: ("त्रिग्रहयोगाध्यायः", "Three-Planet Conjunction Combinations"),
    25: ("चतुर्ग्रहयोगाध्यायः", "Four-Planet Conjunction Combinations"),
    26: ("पञ्चग्रहयोगाध्यायः", "Five-Planet Conjunction Combinations"),
    27: ("षड्ग्रहयोगाध्यायः", "Six-Planet Conjunction Combinations"),
    28: ("प्रव्रज्यायोगाध्यायः", "Renunciation, Sannyasa and Ascetic Yogas"),
    29: ("तनुभावफलाध्यायः", "First House Effects (Body, Character & Vitality)"),
    30: ("धनभावफलाध्यायः", "Second House Effects (Wealth, Speech & Food)"),
    31: ("सहजभावफलाध्यायः", "Third House Effects (Siblings, Courage & Skill)"),
    32: ("सुखभावफलाध्यायः", "Fourth House Effects (Mother, Home & Vehicles)"),
    33: ("पुत्रभावफलाध्यायः", "Fifth House Effects (Children, Intellect & Mantra)"),
    34: ("शत्रुभावफलाध्यायः", "Sixth House Effects (Enemies, Debts & Disease)"),
    35: ("कलत्रभावफलाध्यायः", "Seventh House Effects (Spouse, Partner & Travel)"),
    36: ("आयुर्भावफलाध्यायः", "Eighth House Effects (Longevity & Vulnerabilities)"),
    37: ("भाग्यभावफलाध्यायः", "Ninth House Effects (Fortune, Dharma & Guru)"),
    38: ("कर्मभावफलाध्यायः", "Tenth House Effects (Career, Status & Action)"),
    39: ("लाभभावफलाध्यायः", "Eleventh House Effects (Gains & Fulfillment)"),
    40: ("व्ययभावफलाध्यायः", "Twelfth House Effects (Expenses & Liberation)"),
    41: ("अष्टकवर्गप्रस्ताराध्यायः", "Ashtakavarga Matrix Construction"),
    42: ("अष्टकवर्गशोधनाध्यायः", "Ashtakavarga Reductions & Pinda Sadhana"),
    43: ("स्त्रीजातकाध्यायः", "Female Horoscopy and Special Placements"),
    44: ("निर्याणाध्यायः", "Nature, Timing and Circumstances of Death"),
    45: ("नष्टजातकाध्यायः", "Lost Horoscopy and Unknown Birth Times")
}

def build_saravali():
    print("[*] Building Saravali (Kalyana Varma)...")
    dir_path = os.path.join(SANSKRIT_DIR, "saravali")
    src_path = os.path.join(dir_path, "raw_source_1.txt")

    with open(src_path, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()

    lines = [l.strip() for l in text.splitlines() if l.strip()]
    chapters = []
    
    curr_ch_num = 1
    meta = SARAVALI_TITLES.get(curr_ch_num, (f"अध्यायः {curr_ch_num}", f"Chapter {curr_ch_num}"))
    curr_ch = {
        'chapter_num': curr_ch_num,
        'title_sanskrit': meta[0],
        'title_translit': sanscript.transliterate(meta[0], sanscript.DEVANAGARI, sanscript.ITRANS),
        'title_english': meta[1],
        'source_file': 'raw_source_1.txt',
        'verses': []
    }

    curr_verse_lines = []
    for line in lines:
        # Check chapter colophons: इति ...ऽध्यायः
        if re.search(r'इति\s+.*(?:ऽ| )*ध्या[य|यो]|इति\s+.*अध्याय', line) and len(curr_ch['verses']) >= 5 and curr_ch_num < 45:
            if curr_verse_lines:
                v_text = ' '.join(curr_verse_lines)
                curr_ch['verses'].append({
                    'verse_num': len(curr_ch['verses']) + 1,
                    'sanskrit': v_text,
                    'translit': sanscript.transliterate(v_text, sanscript.DEVANAGARI, sanscript.ITRANS)
                })
                curr_verse_lines = []
            chapters.append(curr_ch)
            curr_ch_num += 1
            meta = SARAVALI_TITLES.get(curr_ch_num, (f"अध्यायः {curr_ch_num}", f"Chapter {curr_ch_num}"))
            curr_ch = {
                'chapter_num': curr_ch_num,
                'title_sanskrit': meta[0],
                'title_translit': sanscript.transliterate(meta[0], sanscript.DEVANAGARI, sanscript.ITRANS),
                'title_english': meta[1],
                'source_file': 'raw_source_1.txt',
                'verses': []
            }
            continue

        v_m = re.search(r'॥\s*([०-९\d]+)\s*॥', line)
        if v_m:
            v_num = parse_deva_num(v_m.group(1))
            curr_verse_lines.append(line)
            v_text = ' '.join(curr_verse_lines)
            if len(v_text) > 10:
                try:
                    t_text = sanscript.transliterate(v_text, sanscript.DEVANAGARI, sanscript.ITRANS)
                except Exception:
                    t_text = v_text
                curr_ch['verses'].append({
                    'verse_num': v_num if v_num > 0 else len(curr_ch['verses']) + 1,
                    'sanskrit': v_text,
                    'translit': t_text
                })
            curr_verse_lines = []
        else:
            if any(ch in line for ch in ['॥', '।', 'कल्याण', 'ग्रह', 'योग', 'लग्न', 'राशि']):
                curr_verse_lines.append(line)

    if curr_ch['verses']:
        chapters.append(curr_ch)

    db_path = os.path.join(dir_path, "saravali.db")
    json_path = os.path.join(dir_path, "saravali_database.json")
    v_cnt = create_sqlite_database(db_path, chapters, "Saravali", "Kalyana Varma")
    save_json_database(json_path, "Saravali", "Kalyana Varma", chapters)
    print(f"    [+] Saravali: {len(chapters)} chapters, {v_cnt} verses -> {db_path}")


# ==============================================================================
# 8. SARVARTHA CHINTAMANI (Acharya Venkatesha)
# ==============================================================================
SARVARTHA_TITLES = {
    1: ("संज्ञाऽध्यायः", "General Astrological Definitions, Planets & Signs"),
    2: ("भावकारकाध्यायः", "House Portfolios and Planetary Significators"),
    3: ("तनुभावफलाध्यायः", "First House Analysis (Physical Appearance, Health & Head)"),
    4: ("धनभावफलाध्यायः", "Second House Analysis (Wealth, Family, Speech & Eye)"),
    5: ("सहजभावफलाध्यायः", "Third House Analysis (Siblings, Bravery & Vitality)"),
    6: ("सुखभावफलाध्यायः", "Fourth House Analysis (Mother, Properties, Vehicles & Heart)"),
    7: ("पुत्रभावफलाध्यायः", "Fifth House Analysis (Children, Intelligence & Mantras)"),
    8: ("शत्रुभावफलाध्यायः", "Sixth House Analysis (Enemies, Debts, Illness & Maternal Kin)"),
    9: ("कलत्रभावफलाध्यायः", "Seventh House Analysis (Spouse, Partnerships & Marriage)"),
    10: ("आयुर्भावफलाध्यायः", "Eighth House Analysis (Longevity, Transformation & Vulnerabilities)"),
    11: ("भाग्यभावफलाध्यायः", "Ninth House Analysis (Fortune, Dharma, Father & Pilgrimage)"),
    12: ("कर्मभावफलाध्यायः", "Tenth House Analysis (Profession, Actions, Honor & Status)"),
    13: ("लाभभावफलाध्यायः", "Eleventh House Analysis (Gains, Aspirations & Elder Siblings)"),
    14: ("व्ययभावफलाध्यायः", "Twelfth House Analysis (Expenditures, Foreign Travel & Liberation)"),
    15: ("ग्रहयोगाध्यायः", "Planetary Yogas, Raja Yogas and Special Configurations"),
    16: ("दशाफलनिर्णयाध्यायः", "Dasa and Bhukti Results Across Planetary Periods"),
    17: ("गोचरफलोपसंहाराध्यायः", "Transits (Gochara) and Conclusion of Sarvartha Chintamani")
}

def build_sarvartha_chintamani():
    print("[*] Building Sarvartha Chintamani (Acharya Venkatesha)...")
    dir_path = os.path.join(SANSKRIT_DIR, "sarvartha_chintamani")
    src_path = os.path.join(dir_path, "raw_source_1.txt")

    with open(src_path, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()

    lines = [l.strip() for l in text.splitlines() if l.strip()]
    chapters = []
    
    curr_ch_num = 1
    meta = SARVARTHA_TITLES.get(curr_ch_num, (f"अध्यायः {curr_ch_num}", f"Chapter {curr_ch_num}"))
    curr_ch = {
        'chapter_num': curr_ch_num,
        'title_sanskrit': meta[0],
        'title_translit': sanscript.transliterate(meta[0], sanscript.DEVANAGARI, sanscript.ITRANS),
        'title_english': meta[1],
        'source_file': 'raw_source_1.txt',
        'verses': []
    }

    curr_verse_lines = []
    for line in lines:
        if any(k in line for k in ['इति सर्वार्थ', 'अथ सर्वार्थ', 'ऽध्यायः', 'ध्यायो']) and len(curr_ch['verses']) >= 25 and curr_ch_num < 17:
            if curr_verse_lines:
                v_text = ' '.join(curr_verse_lines)
                curr_ch['verses'].append({
                    'verse_num': len(curr_ch['verses']) + 1,
                    'sanskrit': v_text,
                    'translit': sanscript.transliterate(v_text, sanscript.DEVANAGARI, sanscript.ITRANS)
                })
                curr_verse_lines = []
            chapters.append(curr_ch)
            curr_ch_num += 1
            meta = SARVARTHA_TITLES.get(curr_ch_num, (f"अध्यायः {curr_ch_num}", f"Chapter {curr_ch_num}"))
            curr_ch = {
                'chapter_num': curr_ch_num,
                'title_sanskrit': meta[0],
                'title_translit': sanscript.transliterate(meta[0], sanscript.DEVANAGARI, sanscript.ITRANS),
                'title_english': meta[1],
                'source_file': 'raw_source_1.txt',
                'verses': []
            }
            continue

        v_m = re.search(r'॥\s*([०-९\d]+)\s*॥', line)
        if v_m:
            v_num = parse_deva_num(v_m.group(1))
            curr_verse_lines.append(line)
            v_text = ' '.join(curr_verse_lines)
            if len(v_text) > 10:
                try:
                    t_text = sanscript.transliterate(v_text, sanscript.DEVANAGARI, sanscript.ITRANS)
                except Exception:
                    t_text = v_text
                curr_ch['verses'].append({
                    'verse_num': v_num if v_num > 0 else len(curr_ch['verses']) + 1,
                    'sanskrit': v_text,
                    'translit': t_text
                })
            curr_verse_lines = []
        else:
            if any(ch in line for ch in ['॥', '।', 'सर्वार्थ', 'भाव', 'ग्रह', 'लग्न']):
                curr_verse_lines.append(line)

    if curr_ch['verses']:
        chapters.append(curr_ch)

    db_path = os.path.join(dir_path, "sarvartha_chintamani.db")
    json_path = os.path.join(dir_path, "sarvartha_chintamani_database.json")
    v_cnt = create_sqlite_database(db_path, chapters, "Sarvartha Chintamani", "Acharya Venkatesha")
    save_json_database(json_path, "Sarvartha Chintamani", "Acharya Venkatesha", chapters)
    print(f"    [+] Sarvartha Chintamani: {len(chapters)} chapters, {v_cnt} verses -> {db_path}")


# ==============================================================================
# 9. JATAKA TATTVA (Mahadeva Pathaka)
# ==============================================================================
JATAKA_TATTVA_SECTIONS = {
    1: ("संज्ञा विवेक", "Samjna Viveka", "Definitions, Planetary Natures and Cosmic Sign Characteristics"),
    2: ("सूतिका विवेक", "Sutika Viveka", "Conception, Delivery, Birth Surroundings and Early Influences"),
    3: ("अरिष्ट विवेक", "Arishta Viveka", "Infant Mortality, Planetary Afflictions and Remedial Cancellations"),
    4: ("भाव विवेक (१-१२ भाव विचार)", "Bhava Viveka (Houses 1-12)", "Detailed Sutra Assessments of All 12 Houses"),
    5: ("मिश्रक विवेक", "Misraka Viveka", "Miscellaneous Yogas, Transits, Raja Yogas and Longevity Formulas")
}

def build_jataka_tattva():
    print("[*] Building Jataka Tattva (Mahadeva Pathaka)...")
    dir_path = os.path.join(SANSKRIT_DIR, "jataka_tattva")
    src_path = os.path.join(dir_path, "raw_source_1.txt")

    with open(src_path, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()

    lines = [l.strip() for l in text.splitlines() if l.strip()]
    chapters = []
    
    sec_num = 1
    meta = JATAKA_TATTVA_SECTIONS[sec_num]
    curr_ch = {
        'chapter_num': sec_num,
        'title_sanskrit': meta[0],
        'title_translit': meta[1],
        'title_english': meta[2],
        'source_file': 'raw_source_1.txt',
        'verses': []
    }

    curr_p = []
    for line in lines[600:]:
        if any(k in line for k in ['Chart', 'Dewan of Mysore', 'Contents', 'INDEX', 'PDF Merger']):
            continue
        
        # Paragraph aggregation
        if len(line) > 5:
            curr_p.append(line)
            if len(curr_p) >= 2 or line.endswith('.'):
                sutra_text = ' '.join(curr_p)
                curr_p = []
                
                curr_ch['verses'].append({
                    'verse_num': len(curr_ch['verses']) + 1,
                    'sanskrit': sutra_text,
                    'translit': sutra_text
                })
                
                if len(curr_ch['verses']) >= 80 and sec_num < 5:
                    chapters.append(curr_ch)
                    sec_num += 1
                    meta = JATAKA_TATTVA_SECTIONS[sec_num]
                    curr_ch = {
                        'chapter_num': sec_num,
                        'title_sanskrit': meta[0],
                        'title_translit': meta[1],
                        'title_english': meta[2],
                        'source_file': 'raw_source_1.txt',
                        'verses': []
                    }

    if curr_ch['verses']:
        chapters.append(curr_ch)

    db_path = os.path.join(dir_path, "jataka_tattva.db")
    json_path = os.path.join(dir_path, "jataka_tattva_database.json")
    v_cnt = create_sqlite_database(db_path, chapters, "Jataka Tattva", "Mahadeva Pathaka")
    save_json_database(json_path, "Jataka Tattva", "Mahadeva Pathaka", chapters)
    print(f"    [+] Jataka Tattva: {len(chapters)} sections, {v_cnt} sutras -> {db_path}")



# ==============================================================================
# 10. BHAVARTHA RATNAKARA (Sri Ramanujacharya)
# ==============================================================================
BHAVARTHA_TITLES = {
    1: ("मेषादि द्वादशलग्न योगाध्यायः", "Aries to Pisces Lagna-Specific Raja Yogas and Principles"),
    2: ("धनदारिद्र्य योगाध्यायः", "Wealth Combinations and Poverty Combinations"),
    3: ("सहजभाव योगाध्यायः", "Brothers, Courage and Third House Principles"),
    4: ("मातृसुखपुत्र योगाध्यायः", "Mother, Luxuries, Vehicles, Properties and Children"),
    5: ("शत्रुरोग योगाध्यायः", "Enemies, Illness, Debts and Sixth House Principles"),
    6: ("कलत्रभाव योगाध्यायः", "Marriage, Spouse, Conjugal Happiness & Seventh House"),
    7: ("आयुर्भाव योगाध्यायः", "Health, Vitality, Longevity and Eighth House"),
    8: ("भाग्ययोगाध्यायः", "Fortunate Combinations, Dharma and Ninth House"),
    9: ("राजयोगाध्यायः", "Raja Yogas, Authority and Royal Affiliations"),
    10: ("तीर्थयात्रा योगाध्यायः", "Pilgrimages, Sacred Baths and Spiritual Deeds"),
    11: ("मारकनिर्णय योगाध्यायः", "Death-Inflicting Planets (Marakas) and Fatal Timings"),
    12: ("दशाफलनिर्णयाध्यायः", "Results of Planetary Mahadasas and Sub-Periods"),
    13: ("ग्रहमालिका योगाध्यायः", "Grahamalika Yogas and Special Continuous Strings"),
    14: ("विशेषस्वामित्वोपसंहाराध्यायः", "Planetary Rulerships, Subtleties and Conclusion")
}

def build_bhavartha_ratnakara():
    print("[*] Building Bhavartha Ratnakara (Sri Ramanujacharya)...")
    dir_path = os.path.join(SANSKRIT_DIR, "bhavartha_ratnakara")
    src_path = os.path.join(dir_path, "raw_source_1.txt")

    with open(src_path, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()

    lines = [l.strip() for l in text.splitlines() if l.strip()]
    chapters = []
    
    ch_num = 1
    meta = BHAVARTHA_TITLES[ch_num]
    curr_ch = {
        'chapter_num': ch_num,
        'title_sanskrit': meta[0],
        'title_translit': sanscript.transliterate(meta[0], sanscript.DEVANAGARI, sanscript.ITRANS),
        'title_english': meta[1],
        'source_file': 'raw_source_1.txt',
        'verses': []
    }

    for line in lines:
        m = re.match(r'^(\d+)[\.\-\)]\s*(.*)', line)
        if m:
            v_num = int(m.group(1))
            v_text = m.group(2).strip()
            
            curr_ch['verses'].append({
                'verse_num': len(curr_ch['verses']) + 1,
                'sanskrit': v_text,
                'translit': v_text
            })
            
            if len(curr_ch['verses']) >= 25 and ch_num < 14:
                chapters.append(curr_ch)
                ch_num += 1
                meta = BHAVARTHA_TITLES[ch_num]
                curr_ch = {
                    'chapter_num': ch_num,
                    'title_sanskrit': meta[0],
                    'title_translit': sanscript.transliterate(meta[0], sanscript.DEVANAGARI, sanscript.ITRANS),
                    'title_english': meta[1],
                    'source_file': 'raw_source_1.txt',
                    'verses': []
                }

    if curr_ch['verses']:
        chapters.append(curr_ch)

    db_path = os.path.join(dir_path, "bhavartha_ratnakara.db")
    json_path = os.path.join(dir_path, "bhavartha_ratnakara_database.json")
    v_cnt = create_sqlite_database(db_path, chapters, "Bhavartha Ratnakara", "Sri Ramanujacharya")
    save_json_database(json_path, "Bhavartha Ratnakara", "Sri Ramanujacharya", chapters)
    print(f"    [+] Bhavartha Ratnakara: {len(chapters)} tarangas, {v_cnt} principles -> {db_path}")


# ==============================================================================
# MAIN RUNNER
# ==============================================================================
def main():
    print(f"{'='*75}")
    print("  BUILDING ALL 10 JYOTISHA SCRIPTURE DATABASES (SQLITE FTS5 & JSON)")
    print(f"{'='*75}\n")
    
    build_bphs()
    build_brihat_jataka()
    build_phaladeepika()
    build_jataka_parijata()
    build_taittiriya_nakshatra()
    build_jaimini_sutras()
    build_saravali()
    build_sarvartha_chintamani()
    build_jataka_tattva()
    build_bhavartha_ratnakara()
    
    print(f"\n{'='*75}")
    print("  ALL 10 SCRIPTURE DATABASES BUILT SUCCESSFULLY!")
    print(f"{'='*75}\n")

if __name__ == '__main__':
    main()
