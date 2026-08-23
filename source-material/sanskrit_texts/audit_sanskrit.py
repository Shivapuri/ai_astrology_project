import sqlite3
import glob
import re
import os
from collections import defaultdict

def generate_report():
    report_lines = []
    report_lines.append("# Sanskrit Database Audit Report\\n")
    
    dbs = glob.glob("**/*.db", recursive=True)
    dbs = [db for db in dbs if 'fts' not in db] 
    
    suspicious_chars_re = re.compile(r'[a-zA-Z_#@<>{}\[\]]') 
    
    total_db_verses = 0
    total_db_anomalies = 0
    
    for db_path in dbs:
        report_lines.append(f"## Database: `{db_path}`")
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT * FROM verses ORDER BY chapter_num, verse_num")
            verses = cursor.fetchall()
        except sqlite3.OperationalError:
            report_lines.append("_No 'verses' table found._\\n")
            continue

        chapter_verses = defaultdict(list)
        anomalies = []
        
        for v in verses:
            c_num = v['chapter_num']
            v_num = v['verse_num']
            sanskrit = v['sanskrit'] or ""
            translit = v['translit'] or ""
            
            chapter_verses[c_num].append(v_num)
            issues = []
            
            if not sanskrit.strip():
                issues.append("Empty sanskrit text")
            else:
                match = suspicious_chars_re.findall(sanskrit)
                if match:
                    issues.append(f"Corrupt/Non-Devanagari characters: {''.join(set(match))}")
                    
                if len(sanskrit) < 15:
                    issues.append(f"Unusually short ({len(sanskrit)} chars)")
                elif len(sanskrit) > 600:
                    issues.append(f"Unusually long ({len(sanskrit)} chars) - potential merged verses")
                    
            if not translit.strip():
                issues.append("Empty transliteration")
                
            if issues:
                anomalies.append({
                    'chapter': c_num,
                    'verse': v_num,
                    'issues': issues,
                    'sanskrit_snippet': sanskrit[:120].replace('\\n', ' ')
                })
                
        total_verses = len(verses)
        total_db_verses += total_verses
        total_db_anomalies += len(anomalies)
        
        report_lines.append(f"- **Total verses:** {total_verses}")
        report_lines.append(f"- **Verses with anomalies:** {len(anomalies)}")
        
        # Check gaps
        gaps = []
        for c_num, v_nums in chapter_verses.items():
            if not v_nums: continue
            try:
                v_nums_int = [int(x) for x in v_nums if x is not None]
                v_nums_int.sort()
                for i in range(len(v_nums_int)-1):
                    if v_nums_int[i+1] - v_nums_int[i] > 1:
                        gaps.append(f"Ch {c_num}: Gap between {v_nums_int[i]} and {v_nums_int[i+1]}")
                    elif v_nums_int[i+1] == v_nums_int[i]:
                        gaps.append(f"Ch {c_num}: Duplicate verse {v_nums_int[i]}")
            except ValueError:
                pass
                
        if gaps:
            report_lines.append(f"\\n**Numbering Gaps/Duplicates:** {len(gaps)}")
            for g in gaps[:5]:
                report_lines.append(f"  - {g}")
            if len(gaps) > 5:
                report_lines.append(f"  - ... and {len(gaps)-5} more.")
                
        if anomalies:
            report_lines.append(f"\\n**Sample Anomalies:**")
            for a in anomalies[:10]:
                issues_str = ", ".join(a['issues'])
                report_lines.append(f"  - **Ch {a['chapter']} V {a['verse']}** | *Issues: {issues_str}*")
                report_lines.append(f"    - `{a['sanskrit_snippet']}`")
                
        report_lines.append("\\n---\\n")
        conn.close()
        
    report_lines.insert(1, f"**Global Stats:** {total_db_verses} total verses across all DBs. {total_db_anomalies} anomalies detected.\\n")
    
    with open("audit_report.md", "w") as f:
        f.write("\\n".join(report_lines))

if __name__ == "__main__":
    generate_report()
