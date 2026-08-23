import os
import re
import sqlite3
import json
from indic_transliteration import sanscript

def build_jataka_tattva():
    src_path = "jataka_tattva/jataka_tattva_raw.md"
    with open(src_path, 'r', encoding='utf-8') as f:
        text = f.read()

    lines = text.splitlines()
    
    chapters = []
    curr_chapter_num = 0
    curr_chapter_title = ""
    curr_verses = []
    
    # We match chapter headings like **A. I.संज्ञातत्त्वम् - Samjna Tatva** or **D. अथ धनविवेकः Dhana Viveka.**
    chapter_regex1 = re.compile(r'^\*\*[A-Z]\.\s*[IVX]*\.*\s*([^\-]+)[\-\.]?\s*([A-Za-z]+.*)\*\*$')
    chapter_regex2 = re.compile(r'^\*\*[A-Z]\.\s*(.*?)\s*[\-\.]?\s*([A-Za-z]+.*)\*\*$')
    
    # Match verse: optionally starts with **, then numbers, then dot.
    verse_regex = re.compile(r'^(?:\*\*)?\s*([०-९0-9]+)\.\s*(.*)')
    
    in_verse = False
    current_verse_num = 0
    current_verse_text = ""
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        if 'N.B' in line:
            continue
            
        m_chap = None
        if chapter_regex1.match(line):
            m_chap = chapter_regex1.match(line)
        elif chapter_regex2.match(line):
            m_chap = chapter_regex2.match(line)
            
        if m_chap:
            if curr_verses:
                chapters.append({
                    'chapter_num': curr_chapter_num,
                    'title_sanskrit': curr_chapter_title,
                    'verses': curr_verses
                })
            curr_chapter_num += 1
            sans_title = m_chap.group(1).strip()
            # clean title
            sans_title = sans_title.replace('अथ ', '').replace('अथ', '').replace('॥', '').strip()
            curr_chapter_title = sans_title
            curr_verses = []
            in_verse = False
            continue
            
        m_verse = verse_regex.match(line)
        if m_verse:
            if in_verse and current_verse_text:
                pass 
                
            num_str = m_verse.group(1).translate(str.maketrans("०१२३४५६७८९", "0123456789"))
            current_verse_num = int(num_str)
            current_verse_text = m_verse.group(2)
            
            # Immediately clean out bold markers
            current_verse_text = current_verse_text.replace('**', '').strip()
            
            curr_verses.append({
                'verse_num': current_verse_num,
                'sanskrit': current_verse_text,
                'translit': sanscript.transliterate(current_verse_text, sanscript.DEVANAGARI, sanscript.ITRANS)
            })
            in_verse = True
            
        else:
            pass

    if curr_verses:
        chapters.append({
            'chapter_num': curr_chapter_num,
            'title_sanskrit': curr_chapter_title,
            'verses': curr_verses
        })
        
    print(f"Extracted {len(chapters)} chapters.")
    
    db_path = "jataka_tattva/jataka_tattva.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    os.makedirs("jataka_tattva", exist_ok=True)
        
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
        """, (ch['chapter_num'], ch['title_sanskrit'], sanscript.transliterate(ch['title_sanskrit'], sanscript.DEVANAGARI, sanscript.ITRANS), '', 'jAtakatattavam.md', len(ch['verses'])))
        
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
    
    json_path = "jataka_tattva/jataka_tattva_database.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(chapters, f, ensure_ascii=False, indent=2)
        
    print(f"Saved {v_count} verses to Jataka Tattva database.")

if __name__ == "__main__":
    build_jataka_tattva()
