import os
import re
import sqlite3
import json
from indic_transliteration import sanscript

def clean_sanskrit_text(text):
    text = re.sub(r'\*\*', '', text)
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'<.*?>', '', text)
    text = re.sub(r'भा०\s*[:-].*', '', text)
    text = re.sub(r'व्याख्या\s*[:-].*', '', text)
    return text.strip()

def build_jaimini_perfect():
    src_path = "jaimini_sutras/jaimini_clean2.md"
    with open(src_path, 'r', encoding='utf-8') as f:
        text = f.read()

    # Pre-clean known typesetting quirks in the source markdown
    # 1. Pada 2 sutra 21 ending with single danda: 'राहौ ॥ २१ । **' -> 'राहौ ॥ २१ ॥ **'
    text = text.replace("राहौ ॥ २१ ।", "राहौ ॥ २१ ॥")
    # 2. Pada 2 sutra 50 unnumbered: 'शनिराहुभ्यां गुरुद्रोहः॥' -> 'शनिराहुभ्यां गुरुद्रोहः ॥ ५० ॥'
    text = text.replace("अन्यथा पापैः॥४९॥ शनिराहुभ्यां गुरुद्रोहः॥", "अन्यथा पापैः ॥ ४९ ॥ शनिराहुभ्यां गुरुद्रोहः ॥ ५० ॥")
    # 3. Pada 2 sutra 84 ending with dots: '॥ ८४…' -> '॥ ८४ ॥'
    text = text.replace("॥ ८४…", "॥ ८४ ॥")
    # 4. Pada 6 sutra 21 missing opening danda: 'वमनाद्यैः २१ ॥' -> 'वमनाद्यैः ॥ २१ ॥'
    text = text.replace("वमनाद्यैः २१ ॥", "वमनाद्यैः ॥ २१ ॥")

    lines = text.splitlines()
    sutras_raw = []

    for line in lines:
        line = line.strip()
        if '**' in line and '॥' in line:
            parts = re.split(r'(॥\s*[०-९\d]+\s*॥)', line)
            current_sutra = ""
            for p in parts:
                p = p.strip()
                if re.match(r'^॥\s*[०-९\d]+\s*॥$', p):
                    current_sutra += " " + p
                    sutras_raw.append(current_sutra.strip())
                    current_sutra = ""
                else:
                    current_sutra += " " + p

    pada_titles = [
        ("प्रथमाध्याये प्रथमः पादः (राशिदृष्टि, अर्गला, चरकारक निरूपण)", "Adhyaya 1, Pada 1: Aspects, Argalas & Chara Karakas"),
        ("प्रथमाध्याये द्वितीयः पादः (कारकांश विचार)", "Adhyaya 1, Pada 2: Karakamsha & Sign Placements"),
        ("प्रथमाध्याये तृतीयः पादः (आरूढपद विचार)", "Adhyaya 1, Pada 3: Arudha Lagna Principles"),
        ("प्रथमाध्याये चतुर्थः पादः (उपपद विचार एवं स्त्रीजातक)", "Adhyaya 1, Pada 4: Upapada Lagna & Conjugal Life"),
        ("द्वितीयाध्याये प्रथमः पादः (आयुर्दाय, रुद्र-ब्रह्म-महेश्वर निर्णय)", "Adhyaya 2, Pada 1: Longevity & Special Determinators"),
        ("द्वितीयाध्याये द्वितीयः पादः (कक्षावृद्धि-ह्रास एवं मारक विचार)", "Adhyaya 2, Pada 2: Kakshya Computations & Maraka Periods"),
        ("द्वितीयाध्याये तृतीयः पादः (चर, शूल, स्थिर एवं नवांश दशा)", "Adhyaya 2, Pada 3: Major Jaimini Dasa Systems"),
        ("द्वितीयाध्याये चतुर्थः पादः (वर्णदलग्न एवं विशेषायुर्दाय)", "Adhyaya 2, Pada 4: Varnada Lagna & Longevity Determinations")
    ]

    chapters = []
    curr_chapter_num = 0
    curr_verses = []

    for sr in sutras_raw:
        sr = clean_sanskrit_text(sr)
        m = re.search(r'॥\s*([०-९\d]+)\s*॥', sr)
        if m:
            num_str = m.group(1).translate(str.maketrans("०१२३४५६७८९", "0123456789"))
            v_num = int(num_str)
            
            # New pada when sutra number resets to 1
            if v_num == 1 and curr_verses and len(curr_verses) > 10:
                t_sans, t_eng = pada_titles[curr_chapter_num - 1] if curr_chapter_num <= len(pada_titles) else (f"पादः {curr_chapter_num}", f"Pada {curr_chapter_num}")
                chapters.append({
                    'chapter_num': curr_chapter_num,
                    'title_sanskrit': t_sans,
                    'title_english': t_eng,
                    'verses': curr_verses
                })
                curr_verses = []

            if not curr_verses:
                curr_chapter_num += 1

            verse_text = sr.replace(m.group(0), '').strip()
            if verse_text.startswith("व्याख्या") or verse_text.startswith("भा०") or "व्याख्या:-" in verse_text:
                continue

            curr_verses.append({
                'verse_num': v_num,
                'sanskrit': verse_text,
                'translit': sanscript.transliterate(verse_text, sanscript.DEVANAGARI, sanscript.ITRANS)
            })

    if curr_verses:
        t_sans, t_eng = pada_titles[curr_chapter_num - 1] if curr_chapter_num <= len(pada_titles) else (f"पादः {curr_chapter_num}", f"Pada {curr_chapter_num}")
        chapters.append({
            'chapter_num': curr_chapter_num,
            'title_sanskrit': t_sans,
            'title_english': t_eng,
            'verses': curr_verses
        })

    print(f"Extracted {len(chapters)} Pādas.")
    
    db_path = "jaimini_sutras/jaimini_sutras.db"
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

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

    v_count = 0
    for ch in chapters:
        cur.execute("""
            INSERT INTO chapters (chapter_num, title_sanskrit, title_translit, title_english, source_file, total_verses)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (ch['chapter_num'], ch['title_sanskrit'], sanscript.transliterate(ch['title_sanskrit'], sanscript.DEVANAGARI, sanscript.ITRANS), ch.get('title_english', ''), 'jaiminisUtram.md', len(ch['verses'])))

        for v in ch['verses']:
            clean_s = v['sanskrit'].replace('॥', '').replace('।', '').strip()
            cur.execute("""
                INSERT INTO verses (chapter_num, verse_num, sanskrit, translit, clean_sanskrit)
                VALUES (?, ?, ?, ?, ?)
            """, (ch['chapter_num'], v['verse_num'], v['sanskrit'], v['translit'], clean_s))

            cur.execute("""
                INSERT INTO verses_fts (chapter_num, verse_num, title_sanskrit, title_english, sanskrit, translit)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (ch['chapter_num'], v['verse_num'], ch['title_sanskrit'], ch.get('title_english', ''), v['sanskrit'], v['translit']))
            v_count += 1

    conn.commit()
    conn.close()

    json_path = "jaimini_sutras/jaimini_sutras_database.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(chapters, f, ensure_ascii=False, indent=2)

    print(f"Successfully saved {v_count} sutras across {len(chapters)} Pādas.")

if __name__ == "__main__":
    build_jaimini_perfect()
