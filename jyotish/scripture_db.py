#!/usr/bin/env python3
"""
Unified Jyotisha Scripture Database Engine.
Provides high-performance SQLite FTS5 search, chapter browsing, and verse retrieval
across all 10 foundational Sanskrit scriptures used by Ernst Wilhelm:

1. bphs: Brihat Parashara Hora Shastra (Sage Parashara)
2. brihat_jataka: Brihat Jataka (Varahamihira)
3. phaladeepika: Phaladeepika (Mantreswara)
4. jataka_parijata: Jataka Parijata (Vaidyanatha Dikshita)
5. taittiriya_nakshatra: Taittiriya Nakshatra Sutras (Krishna Yajurveda)
6. jaimini_sutras: Upadesa Sutras / Jaimini Sutras (Sage Jaimini)
7. saravali: Saravali (Kalyana Varma)
8. sarvartha_chintamani: Sarvartha Chintamani (Acharya Venkatesha)
9. jataka_tattva: Jataka Tattva (Mahadeva Pathaka)
10. bhavartha_ratnakara: Bhavartha Ratnakara (Sri Ramanujacharya)
"""

import os
import sys
import sqlite3
import argparse
from typing import List, Dict, Any, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SANSKRIT_DIR = os.path.join(BASE_DIR, "source-material", "sanskrit_texts")

SCRIPTURE_REGISTRY = {
    'bphs': {
        'name': 'Brihat Parashara Hora Shastra',
        'author': 'Maharishi Parashara',
        'folder': 'bphs',
        'db_file': 'bphs.db',
        'json_file': 'bphs_database.json',
        'type': 'Verses (Shlokas)'
    },
    'brihat_jataka': {
        'name': 'Brihat Jataka',
        'author': 'Varahamihira',
        'folder': 'brihat_jataka',
        'db_file': 'brihat_jataka.db',
        'json_file': 'brihat_jataka_database.json',
        'type': 'Verses (Shlokas)'
    },
    'phaladeepika': {
        'name': 'Phaladeepika',
        'author': 'Mantreswara',
        'folder': 'phaladeepika',
        'db_file': 'phaladeepika.db',
        'json_file': 'phaladeepika_database.json',
        'type': 'Verses (Shlokas)'
    },
    'jataka_parijata': {
        'name': 'Jataka Parijata',
        'author': 'Vaidyanatha Dikshita',
        'folder': 'jataka_parijata',
        'db_file': 'jataka_parijata.db',
        'json_file': 'jataka_parijata_database.json',
        'type': 'Verses (Shlokas)'
    },
    'taittiriya_nakshatra': {
        'name': 'Taittiriya Nakshatra Sutras',
        'author': 'Krishna Yajurveda (Taittiriya Brahmana)',
        'folder': 'taittiriya_nakshatra',
        'db_file': 'taittiriya_nakshatra.db',
        'json_file': 'taittiriya_nakshatra_database.json',
        'type': 'Vedic Mantras (Nakshatra Suktam)'
    },
    'jaimini_sutras': {
        'name': 'Jaimini Upadesa Sutras',
        'author': 'Sage Jaimini',
        'folder': 'jaimini_sutras',
        'db_file': 'jaimini_sutras.db',
        'json_file': 'jaimini_sutras_database.json',
        'type': 'Aphorisms (Sutras)'
    },
    'saravali': {
        'name': 'Saravali',
        'author': 'Kalyana Varma',
        'folder': 'saravali',
        'db_file': 'saravali.db',
        'json_file': 'saravali_database.json',
        'type': 'Verses (Shlokas)'
    },
    'sarvartha_chintamani': {
        'name': 'Sarvartha Chintamani',
        'author': 'Acharya Venkatesha',
        'folder': 'sarvartha_chintamani',
        'db_file': 'sarvartha_chintamani.db',
        'json_file': 'sarvartha_chintamani_database.json',
        'type': 'Verses (Shlokas)'
    },
    'jataka_tattva': {
        'name': 'Jataka Tattva',
        'author': 'Mahadeva Pathaka',
        'folder': 'jataka_tattva',
        'db_file': 'jataka_tattva.db',
        'json_file': 'jataka_tattva_database.json',
        'type': 'Aphorisms (Sutras)'
    },
    'bhavartha_ratnakara': {
        'name': 'Bhavartha Ratnakara',
        'author': 'Sri Ramanujacharya',
        'folder': 'bhavartha_ratnakara',
        'db_file': 'bhavartha_ratnakara.db',
        'json_file': 'bhavartha_ratnakara_database.json',
        'type': 'Astrological Principles'
    }
}


class ScriptureDatabase:
    """High-performance query engine for an individual Jyotisha scripture."""

    def __init__(self, scripture_key: str):
        key = scripture_key.lower().replace('-', '_').replace(' ', '_')
        if key not in SCRIPTURE_REGISTRY:
            # Match partial name
            matched = [k for k in SCRIPTURE_REGISTRY if key in k or key in SCRIPTURE_REGISTRY[k]['name'].lower()]
            if matched:
                key = matched[0]
            else:
                raise ValueError(f"Unknown scripture '{scripture_key}'. Available: {list(SCRIPTURE_REGISTRY.keys())}")

        self.key = key
        self.meta = SCRIPTURE_REGISTRY[key]
        self.folder_path = os.path.join(SANSKRIT_DIR, self.meta['folder'])
        self.db_path = os.path.join(self.folder_path, self.meta['db_file'])
        
        # Backward compatibility for root BPHS database location
        if not os.path.exists(self.db_path) and key == 'bphs':
            root_db = os.path.join(SANSKRIT_DIR, 'bphs.db')
            if os.path.exists(root_db):
                self.db_path = root_db

        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Database for '{self.meta['name']}' not found at {self.db_path}. Run scripts/build_all_databases.py first.")

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def get_info(self) -> Dict[str, Any]:
        """Get summary metadata of the scripture."""
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM chapters")
            ch_cnt = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM verses")
            v_cnt = cur.fetchone()[0]
            return {
                'key': self.key,
                'name': self.meta['name'],
                'author': self.meta['author'],
                'type': self.meta['type'],
                'total_chapters': ch_cnt,
                'total_verses': v_cnt,
                'db_path': self.db_path
            }

    def list_chapters(self) -> List[Dict[str, Any]]:
        """List all chapters / sections with metadata."""
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT chapter_num, title_sanskrit, title_translit, title_english, total_verses
                FROM chapters
                ORDER BY chapter_num ASC
            """)
            return [dict(r) for r in cur.fetchall()]

    def get_chapter(self, chapter_num: int) -> Optional[Dict[str, Any]]:
        """Retrieve chapter metadata and all its verses."""
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT chapter_num, title_sanskrit, title_translit, title_english, total_verses
                FROM chapters
                WHERE chapter_num = ?
            """, (chapter_num,))
            ch = cur.fetchone()
            if not ch:
                return None
            result = dict(ch)
            cur.execute("""
                SELECT verse_num, sanskrit, translit
                FROM verses
                WHERE chapter_num = ?
                ORDER BY verse_num ASC
            """, (chapter_num,))
            result['verses'] = [dict(v) for v in cur.fetchall()]
            return result

    def get_verse(self, chapter_num: int, verse_num: int) -> Optional[Dict[str, Any]]:
        """Retrieve a specific verse by chapter and verse number."""
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT v.chapter_num, v.verse_num, v.sanskrit, v.translit,
                       c.title_sanskrit, c.title_english
                FROM verses v
                JOIN chapters c ON v.chapter_num = c.chapter_num
                WHERE v.chapter_num = ? AND v.verse_num = ?
            """, (chapter_num, verse_num))
            res = cur.fetchone()
            return dict(res) if res else None

    def search(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search verses across Sanskrit Devanagari, Transliteration, Chapter titles, and English topics.
        Uses SQLite FTS5 full-text indexing with fallback to LIKE substring matching.
        """
        results = []
        with self._get_connection() as conn:
            cur = conn.cursor()

            # 1. FTS5 Search
            try:
                clean_query = query.replace('"', '""')
                fts_sql = """
                    SELECT f.chapter_num, f.verse_num, f.title_sanskrit, f.title_english,
                           f.sanskrit, f.translit, rank
                    FROM verses_fts f
                    WHERE verses_fts MATCH ?
                    ORDER BY rank
                    LIMIT ?
                """
                cur.execute(fts_sql, (f'"{clean_query}"*', limit))
                rows = cur.fetchall()
                for r in rows:
                    item = dict(r)
                    item['scripture_key'] = self.key
                    item['scripture_name'] = self.meta['name']
                    results.append(item)
            except Exception:
                pass

            # 2. LIKE Search Fallback
            if not results:
                like_pattern = f"%{query}%"
                like_sql = """
                    SELECT v.chapter_num, v.verse_num, c.title_sanskrit, c.title_english,
                           v.sanskrit, v.translit
                    FROM verses v
                    JOIN chapters c ON v.chapter_num = c.chapter_num
                    WHERE v.sanskrit LIKE ? 
                       OR v.translit LIKE ? 
                       OR c.title_sanskrit LIKE ? 
                       OR c.title_english LIKE ?
                    LIMIT ?
                """
                cur.execute(like_sql, (like_pattern, like_pattern, like_pattern, like_pattern, limit))
                rows = cur.fetchall()
                for r in rows:
                    item = dict(r)
                    item['scripture_key'] = self.key
                    item['scripture_name'] = self.meta['name']
                    results.append(item)

        return results


class MultiScriptureEngine:
    """Unified search engine that orchestrates queries across all 10 Sanskrit databases."""

    def __init__(self, scriptures: Optional[List[str]] = None):
        if scriptures is None:
            self.keys = list(SCRIPTURE_REGISTRY.keys())
        else:
            self.keys = [k for k in scriptures if k in SCRIPTURE_REGISTRY]
            
        self.dbs = {}
        for k in self.keys:
            try:
                self.dbs[k] = ScriptureDatabase(k)
            except Exception as e:
                print(f"[!] Warning: Could not initialize '{k}': {e}", file=sys.stderr)

    def list_all_scriptures(self) -> List[Dict[str, Any]]:
        """List summary info for all registered scriptures."""
        return [db.get_info() for db in self.dbs.values()]

    def search_all(self, query: str, limit_per_scripture: int = 5) -> Dict[str, List[Dict[str, Any]]]:
        """Search for a keyword across all 10 scriptures simultaneously."""
        all_results = {}
        for k, db in self.dbs.items():
            res = db.search(query, limit=limit_per_scripture)
            if res:
                all_results[k] = res
        return all_results


# Backward compatibility aliases
BPHSDatabase = lambda: ScriptureDatabase('bphs')
BrihatJatakaDatabase = lambda: ScriptureDatabase('brihat_jataka')
PhaladeepikaDatabase = lambda: ScriptureDatabase('phaladeepika')
JatakaParijataDatabase = lambda: ScriptureDatabase('jataka_parijata')
TaittiriyaNakshatraDatabase = lambda: ScriptureDatabase('taittiriya_nakshatra')
JaiminiSutrasDatabase = lambda: ScriptureDatabase('jaimini_sutras')
SaravaliDatabase = lambda: ScriptureDatabase('saravali')
SarvarthaChintamaniDatabase = lambda: ScriptureDatabase('sarvartha_chintamani')
JatakaTattvaDatabase = lambda: ScriptureDatabase('jataka_tattva')
BhavarthaRatnakaraDatabase = lambda: ScriptureDatabase('bhavartha_ratnakara')


def main():
    parser = argparse.ArgumentParser(description="Unified Jyotisha Scripture Database Search Engine")
    parser.add_argument("--scripture", "-s", type=str, default="all",
                        help=f"Specific scripture to query ({', '.join(SCRIPTURE_REGISTRY.keys())}) or 'all' (default)")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Search command
    search_p = subparsers.add_parser("search", help="Search verses by keyword across scripture(s)")
    search_p.add_argument("query", type=str, help="Search term (Sanskrit Devanagari, ITRANS, or English keyword)")
    search_p.add_argument("--limit", type=int, default=10, help="Maximum number of results per scripture")

    # List command
    subparsers.add_parser("list", help="List all chapters / scriptures")

    # Chapter command
    chap_p = subparsers.add_parser("chapter", help="View all verses of a specific chapter")
    chap_p.add_argument("chapter_num", type=int, help="Chapter number")

    # Verse command
    verse_p = subparsers.add_parser("verse", help="View a specific verse")
    verse_p.add_argument("chapter_num", type=int, help="Chapter number")
    verse_p.add_argument("verse_num", type=int, help="Verse / Sutra number")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "list" and args.scripture == "all":
        engine = MultiScriptureEngine()
        all_info = engine.list_all_scriptures()
        print(f"\n{'='*85}")
        print(f"  FOUNDATIONAL SANSKRIT JYOTISHA SCRIPTURES (10 DATABASES)")
        print(f"{'='*85}")
        total_all_verses = 0
        for info in all_info:
            total_all_verses += info['total_verses']
            print(f"• [{info['key']}] {info['name']} — {info['author']}")
            print(f"    Format: {info['type']} | Chapters: {info['total_chapters']} | Total Entries: {info['total_verses']:,}")
            print(f"    Location: {info['db_path']}")
        print(f"{'-'*85}")
        print(f"  TOTAL CORPUS: {len(all_info)} SCRIPTURES | {total_all_verses:,} VERSES & SUTRAS")
        print(f"{'='*85}\n")
        return

    if args.scripture == "all" and args.command == "search":
        engine = MultiScriptureEngine()
        res = engine.search_all(args.query, limit_per_scripture=args.limit)
        total_found = sum(len(v) for v in res.values())
        print(f"\n{'='*85}")
        print(f"  MULTI-SCRIPTURE SEARCH FOR '{args.query}' ({total_found} matches across {len(res)} scriptures)")
        print(f"{'='*85}\n")
        if not res:
            print("No matching verses found across any scripture.")
        for skey, items in res.items():
            s_name = SCRIPTURE_REGISTRY[skey]['name']
            print(f"\n--- {s_name} ({len(items)} matches) ---")
            for idx, r in enumerate(items, 1):
                print(f"[{idx}] Ch {r['chapter_num']}:{r['verse_num']} — {r.get('title_sanskrit','')} ({r.get('title_english','')})")
                print(f"    {r.get('sanskrit','').replace(chr(10), ' ')}")
                if r.get('translit'):
                    print(f"    ITRANS: {r['translit'].replace(chr(10), ' ')}")
        print(f"\n{'='*85}\n")
        return

    # Single scripture commands
    skey = 'bphs' if args.scripture == 'all' else args.scripture
    db = ScriptureDatabase(skey)
    info = db.get_info()

    if args.command == "list":
        chaps = db.list_chapters()
        print(f"\n{'='*85}")
        print(f"  {info['name'].upper()} — {info['author']} ({len(chaps)} Chapters / Sections)")
        print(f"{'='*85}")
        for c in chaps:
            print(f"[{c['chapter_num']:02d}] {c['title_sanskrit']} ({c['total_verses']} verses/sutras)")
            print(f"     English: {c['title_english']}")
        print(f"{'='*85}\n")

    elif args.command == "chapter":
        ch = db.get_chapter(args.chapter_num)
        if not ch:
            print(f"Error: Chapter {args.chapter_num} not found in {info['name']}.")
            sys.exit(1)
        print(f"\n{'='*85}")
        print(f"  {info['name']} — Chapter {ch['chapter_num']}: {ch['title_sanskrit']}")
        print(f"  English: {ch['title_english']}")
        print(f"  Total Verses: {ch['total_verses']}")
        print(f"{'='*85}\n")
        for v in ch['verses']:
            print(f"--- Verse {v['verse_num']} ---")
            print(v['sanskrit'])
            if v.get('translit'):
                print(f"[Translit]: {v['translit']}")
            print()

    elif args.command == "verse":
        v = db.get_verse(args.chapter_num, args.verse_num)
        if not v:
            print(f"Error: Verse {args.chapter_num}:{args.verse_num} not found in {info['name']}.")
            sys.exit(1)
        print(f"\n{'='*85}")
        print(f"  {info['name']} Chapter {v['chapter_num']}:{v['verse_num']} — {v['title_sanskrit']}")
        print(f"  English: {v['title_english']}")
        print(f"{'='*85}\n")
        print(v['sanskrit'])
        if v.get('translit'):
            print(f"\n[Transliteration]:\n{v['translit']}")
        print(f"{'='*85}\n")

    elif args.command == "search":
        results = db.search(args.query, limit=args.limit)
        print(f"\nSearch results in {info['name']} for '{args.query}' ({len(results)} matches):\n")
        if not results:
            print("No matching verses found.")
        for idx, r in enumerate(results, 1):
            print(f"[{idx}] {info['name']} Ch {r['chapter_num']}:{r['verse_num']} — {r.get('title_sanskrit','')} ({r.get('title_english','')})")
            print(f"    {r.get('sanskrit','').replace(chr(10), ' ')}")
            if r.get('translit'):
                print(f"    ITRANS: {r['translit'].replace(chr(10), ' ')}")
            print()


if __name__ == "__main__":
    main()
