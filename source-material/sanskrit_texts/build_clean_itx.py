import os
import re
import sqlite3
import json
import glob
from indic_transliteration import sanscript

def clean_text_for_search(text):
    if not text:
        return ""
    text = re.sub(r'[।॥\-\.,;:!\?\(\)\[\]]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def create_sqlite_database(db_path, chapters):
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
        """, (ch['chapter_num'], ch['title_sanskrit'], ch['title_translit'], ch.get('title_english', ''), ch.get('source_file', ''), len(ch['verses'])))
        
        for v in ch['verses']:
            clean_s = clean_text_for_search(v['sanskrit'])
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
    return v_count

def parse_itx_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.read().splitlines()
        
    chapters = []
    curr_verses = []
    curr_lines = []
    ch_num = 1
    ch_title_candidates = []
    
    in_doc = False
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('%') or line.startswith('#'):
            continue
            
        if '\\begin{document}' in line:
            in_doc = True
            continue
        if '\\end{document}' in line:
            in_doc = False
            continue
            
        if not in_doc and ('\\documentstyle' in line or '\\def' in line or '\\let' in line):
            continue
            
        if line.startswith('\\engtitle') or line.startswith('\\itxtitle') or line.startswith('\\endtitles'):
            continue
            
        v_m = re.search(r'(?:\|\|\s*(\d+)(?:-\d+)?\s*\|\||\.\.\s*(\d+)(?:-\d+)?\s*\.\.)\s*$', line)
        if v_m:
            v_num = int(v_m.group(1) or v_m.group(2))
            
            # If we see verse 1, and we already have verses in the current chapter, it's a new chapter
            if v_num == 1 and curr_verses:
                title = " ".join(ch_title_candidates[-3:]) if ch_title_candidates else f"Chapter {ch_num}"
                title = re.sub(r'\\section\{([^\}]+)\}', r'\1', title)
                chapters.append({
                    'chapter_num': ch_num,
                    'title_translit': title,
                    'verses': curr_verses
                })
                ch_num += 1
                curr_verses = []
                ch_title_candidates = []
                
            curr_lines.append(line)
            # Remove any # # from the verse text
            verse_text = ' '.join(curr_lines).replace('#', '')
            curr_verses.append({'verse_num': v_num, 'translit': verse_text})
            curr_lines = []
            ch_title_candidates = [] # reset title candidates after a verse
        else:
            # Check if it's a chapter section marker but without verse numbers
            if '\\section' in line:
                m = re.search(r'\\section\{([^\}]+)\}', line)
                if m:
                    ch_title_candidates.append(m.group(1))
            elif not line.startswith('\\'): 
                curr_lines.append(line)
                ch_title_candidates.append(line)
                
    if curr_verses:
        title = " ".join(ch_title_candidates[-3:]) if ch_title_candidates else f"Chapter {ch_num}"
        chapters.append({
            'chapter_num': ch_num,
            'title_translit': title,
            'verses': curr_verses
        })
        
    for ch in chapters:
        ch['title_sanskrit'] = sanscript.transliterate(ch['title_translit'], sanscript.ITRANS, sanscript.DEVANAGARI)
        for v in ch['verses']:
            t = v['translit']
            t = re.sub(r'[\`\'\"]', '', t) 
            t = re.sub(r'\{([^\}]+)\}', r'\1', t)
            t = re.sub(r'\+', '', t)
            v['translit'] = t
            s = sanscript.transliterate(t, sanscript.ITRANS, sanscript.DEVANAGARI)
            v['sanskrit'] = s
            
    return chapters

if __name__ == "__main__":
    targets = [
        ("brihat_jataka/brihat_jataka.db", "brihat_jataka/brihajjAtakam.itx"),
        ("phaladeepika/phaladeepika.db", "phaladeepika/phaladIpika.itx"),
        ("jataka_parijata/jataka_parijata.db", "jataka_parijata/jAtakapArijAtaH.itx"),
        ("taittiriya_nakshatra/taittiriya_nakshatra.db", "taittiriya_nakshatra/nakshatra.itx"),
    ]
    
    # Also BPHS has many itx files
    bphs_files = sorted(glob.glob("bphs/*.itx"))
    
    for db_path, itx_path in targets:
        if not os.path.exists(itx_path):
            print(f"Skipping {itx_path}, not found.")
            continue
        print(f"Processing {itx_path} -> {db_path}...")
        chapters = parse_itx_file(itx_path)
        v_count = create_sqlite_database(db_path, chapters)
        
        json_path = db_path.replace(".db", "_database.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(chapters, f, ensure_ascii=False, indent=2)
            
        print(f"  Saved {len(chapters)} chapters, {v_count} verses.")
        
    # Process BPHS
    if bphs_files:
        print(f"Processing BPHS ITX files -> bphs/bphs.db...")
        all_bphs_chapters = []
        ch_offset = 1
        for f in bphs_files:
            chaps = parse_itx_file(f)
            # Re-number chapters sequentially since they are split across files
            for ch in chaps:
                ch['chapter_num'] = ch_offset
                ch_offset += 1
                all_bphs_chapters.append(ch)
                
        v_count = create_sqlite_database("bphs/bphs.db", all_bphs_chapters)
        with open("bphs/bphs_database.json", 'w', encoding='utf-8') as f:
            json.dump(all_bphs_chapters, f, ensure_ascii=False, indent=2)
        print(f"  Saved BPHS: {len(all_bphs_chapters)} chapters, {v_count} verses.")
