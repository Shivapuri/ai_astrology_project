import os
import re
import sqlite3
import json
from bs4 import BeautifulSoup
from indic_transliteration import sanscript

def build_saravali():
    src_path = "/Users/hajnaljanos/.gemini/antigravity-cli/brain/ce4eb0ca-5500-441f-b0e5-7078d315c84f/.system_generated/steps/217/content.md"
    with open(src_path, 'r', encoding='utf-8') as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")
    content = soup.find(id="mw-content-text")
    
    if not content:
        print("Could not find content")
        return
        
    text = content.get_text()
    
    lines = text.splitlines()
    
    chapters = []
    curr_chapter_num = 0
    curr_chapter_title = ""
    curr_verses = []
    
    verse_pattern = re.compile(r'॥\s*([०-९\d]+)\s*॥')
    
    current_verse_text = ""
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # check for chapter
        if "ध्यायः[सम्पाद्यताम्]" in line or "ध्यायः[ सम्पाद्यताम् ]" in line:
            # Save previous chapter
            if curr_verses:
                chapters.append({
                    'chapter_num': curr_chapter_num,
                    'title_sanskrit': curr_chapter_title,
                    'verses': curr_verses
                })
            
            curr_chapter_num += 1
            curr_chapter_title = line.replace("[सम्पाद्यताम्]", "").replace("[ सम्पाद्यताम् ]", "").strip()
            curr_verses = []
            current_verse_text = ""
            continue
            
        if "॥" in line:
            parts = re.split(r'(॥\s*[०-९\d]+\s*॥)', line)
            for p in parts:
                p = p.strip()
                if verse_pattern.match(p):
                    current_verse_text += " " + p
                    
                    # Extract verse number
                    m = verse_pattern.search(p)
                    num_str = m.group(1).translate(str.maketrans("०१२३४५६७८९", "0123456789"))
                    try:
                        v_num = int(num_str)
                    except:
                        v_num = 0
                        
                    v_text = current_verse_text.strip()
                    # clean out brackets and extra spaces
                    v_text = re.sub(r'\[.*?\]', '', v_text)
                    v_text = re.sub(r'\s+', ' ', v_text)
                    
                    curr_verses.append({
                        'verse_num': v_num,
                        'sanskrit': v_text,
                        'translit': sanscript.transliterate(v_text, sanscript.DEVANAGARI, sanscript.ITRANS)
                    })
                    current_verse_text = ""
                else:
                    current_verse_text += " " + p
        else:
            current_verse_text += " " + line + "\n"

    if curr_verses:
        chapters.append({
            'chapter_num': curr_chapter_num,
            'title_sanskrit': curr_chapter_title,
            'verses': curr_verses
        })
        
    print(f"Extracted {len(chapters)} chapters.")
    
    db_path = "saravali/saravali.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    os.makedirs("saravali", exist_ok=True)
        
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
        """, (ch['chapter_num'], ch['title_sanskrit'], sanscript.transliterate(ch['title_sanskrit'], sanscript.DEVANAGARI, sanscript.ITRANS), '', 'sa.wikisource.org', len(ch['verses'])))
        
        for v in ch['verses']:
            clean_s = v['sanskrit'].replace('॥', '').replace('।', '').strip()
            cur.execute("""
                INSERT INTO verses (chapter_num, verse_num, sanskrit, translit, clean_sanskrit)
                VALUES (?, ?, ?, ?, ?)
            """, (ch['chapter_num'], v['verse_num'], v['sanskrit'], v['translit'], clean_s))
            
            cur.execute("""
                INSERT INTO verses_fts (chapter_num, verse_num, title_sanskrit, title_english, sanskrit, translit)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (ch['chapter_num'], v['verse_num'], ch['title_sanskrit'], '', v['sanskrit'], v['translit']))
            v_count += 1
            
    conn.commit()
    conn.close()
    
    json_path = "saravali/saravali_database.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(chapters, f, ensure_ascii=False, indent=2)
        
    print(f"Saved {v_count} verses to Saravali database.")

if __name__ == "__main__":
    build_saravali()
