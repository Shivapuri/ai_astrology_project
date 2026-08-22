#!/usr/bin/env python3
"""
BPHSDatabase: High-performance search and retrieval interface for Brihat Parashara Hora Shastra (BPHS).
Provides SQLite FTS5 full-text search, chapter lookups, verse retrievals, and CLI commands.
"""

import os
import sys
import sqlite3
import argparse
from typing import List, Dict, Any, Optional

DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "source-material", "sanskrit_texts", "bphs.db"
)

class BPHSDatabase:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"BPHS database not found at {self.db_path}. Please run scripts/build_bphs_database.py first.")
            
    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def list_chapters(self) -> List[Dict[str, Any]]:
        """List all 97 chapters with metadata."""
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
        Uses FTS5 with fallback to LIKE for flexible substring matching.
        """
        results = []
        with self._get_connection() as conn:
            cur = conn.cursor()
            
            # 1. Try FTS5 search
            try:
                # Escape special FTS characters
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
                    results.append(dict(r))
            except Exception:
                pass
                
            # 2. If no FTS results or for direct substring match, use LIKE
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
                    results.append(dict(r))
                    
        return results

def main():
    parser = argparse.ArgumentParser(description="Brihat Parashara Hora Shastra (BPHS) Search Engine")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Search command
    search_p = subparsers.add_parser("search", help="Search verses by keyword or topic")
    search_p.add_argument("query", type=str, help="Search term (Sanskrit, ITRANS, or English keyword)")
    search_p.add_argument("--limit", type=int, default=10, help="Maximum number of results (default: 10)")

    # Chapter command
    chap_p = subparsers.add_parser("chapter", help="View all verses of a chapter")
    chap_p.add_argument("chapter_num", type=int, help="Chapter number (1 to 97)")

    # Verse command
    verse_p = subparsers.add_parser("verse", help="View a specific verse")
    verse_p.add_argument("chapter_num", type=int, help="Chapter number (1 to 97)")
    verse_p.add_argument("verse_num", type=int, help="Verse number")

    # List command
    subparsers.add_parser("list", help="List all 97 chapters of BPHS")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    db = BPHSDatabase()

    if args.command == "list":
        chapters = db.list_chapters()
        print(f"\n{'='*75}")
        print(f"  BRIHAT PARASHARA HORA SHASTRA (97 CHAPTERS)")
        print(f"{'='*75}")
        for ch in chapters:
            print(f"[{ch['chapter_num']:02d}] {ch['title_sanskrit']} ({ch['total_verses']} verses)")
            print(f"     English: {ch['title_english']}")
        print(f"{'='*75}\n")

    elif args.command == "chapter":
        ch = db.get_chapter(args.chapter_num)
        if not ch:
            print(f"Error: Chapter {args.chapter_num} not found.")
            sys.exit(1)
        print(f"\n{'='*75}")
        print(f"  Chapter {ch['chapter_num']}: {ch['title_sanskrit']}")
        print(f"  English: {ch['title_english']}")
        print(f"  Total Verses: {ch['total_verses']}")
        print(f"{'='*75}\n")
        for v in ch['verses']:
            print(f"--- Verse {v['verse_num']} ---")
            print(v['sanskrit'])
            if v.get('translit'):
                print(f"[Translit]: {v['translit']}")
            print()

    elif args.command == "verse":
        v = db.get_verse(args.chapter_num, args.verse_num)
        if not v:
            print(f"Error: Verse {args.chapter_num}:{args.verse_num} not found.")
            sys.exit(1)
        print(f"\n{'='*75}")
        print(f"  BPHS Chapter {v['chapter_num']}:{v['verse_num']} — {v['title_sanskrit']}")
        print(f"  English: {v['title_english']}")
        print(f"{'='*75}\n")
        print(v['sanskrit'])
        if v.get('translit'):
            print(f"\n[Transliteration]:\n{v['translit']}")
        print(f"{'='*75}\n")

    elif args.command == "search":
        results = db.search(args.query, limit=args.limit)
        print(f"\nSearch results for '{args.query}' ({len(results)} matches):\n")
        if not results:
            print("No matching verses found.")
        for idx, r in enumerate(results, 1):
            print(f"[{idx}] BPHS Ch {r['chapter_num']}:{r['verse_num']} — {r['title_sanskrit']} ({r['title_english']})")
            print(f"    {r['sanskrit'].replace(chr(10), ' ')}")
            if r.get('translit'):
                print(f"    ITRANS: {r['translit'].replace(chr(10), ' ')}")
            print()

if __name__ == "__main__":
    main()
