#!/usr/bin/env python3
"""
Comprehensive Database Builder for Classical Jyotisha Sanskrit Scriptures.
Builds SQLite databases (with FTS5 full-text search) and JSON databases for the 8 clean classical texts
utilized in Ernst Wilhelm's Kala astrological framework.

(Note: Sarvartha Chintamani and Bhavartha Ratnakara are temporarily excluded pending clean Sanskrit sources).
"""

import os
import sys
import subprocess

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SANSKRIT_DIR = os.path.join(BASE_DIR, "source-material", "sanskrit_texts")

def run_script(script_name):
    script_path = os.path.join(SANSKRIT_DIR, script_name)
    if not os.path.exists(script_path):
        print(f"[!] Error: Script not found: {script_path}")
        return False
    
    print(f"\n============================================================")
    print(f"[*] Running {script_name}...")
    print(f"============================================================")
    
    # Use the python executable from the virtual environment if possible
    python_exe = sys.executable
    
    result = subprocess.run([python_exe, script_path], cwd=SANSKRIT_DIR)
    if result.returncode != 0:
        print(f"[!] {script_name} failed with code {result.returncode}")
        return False
    return True

def main():
    print(f"{'='*75}")
    print("  BUILDING 8 VERIFIED JYOTISHA SCRIPTURE DATABASES (SQLITE FTS5 & JSON)")
    print(f"{'='*75}\n")
    
    success = True
    
    # 1. Build the 5 ITX-based texts (BPHS, Brihat Jataka, Phaladeepika, Jataka Parijata, Taittiriya)
    if not run_script("build_clean_itx.py"): success = False
    
    # 2. Build Jaimini Sutras
    if not run_script("build_jaimini_db.py"): success = False
    
    # 3. Build Saravali
    if not run_script("build_saravali_db.py"): success = False
    
    # 4. Build Jataka Tattva
    if not run_script("build_jataka_tattva_db.py"): success = False
    
    print(f"\n{'='*75}")
    if success:
        print("  ALL 8 SCRIPTURE DATABASES BUILT SUCCESSFULLY!")
    else:
        print("  SOME DATABASES FAILED TO BUILD. CHECK LOGS.")
    print(f"{'='*75}\n")

if __name__ == '__main__':
    main()
