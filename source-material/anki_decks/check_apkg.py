import sqlite3
import zipfile
import os
import tempfile
import sys

def check_apkg(apkg_path):
    if not os.path.exists(apkg_path):
        print(f"Error: File not found - {apkg_path}")
        return

    print(f"Reading {apkg_path}...")
    
    with tempfile.TemporaryDirectory() as tmpdirname:
        try:
            with zipfile.ZipFile(apkg_path, 'r') as z:
                if 'collection.anki21b' in z.namelist():
                    z.extract('collection.anki21b', tmpdirname)
                    compressed_path = os.path.join(tmpdirname, 'collection.anki21b')
                    db_path = os.path.join(tmpdirname, 'collection.db')
                    os.system(f"zstd -d -q {compressed_path} -o {db_path}")
                elif 'collection.anki21' in z.namelist():
                    z.extract('collection.anki21', tmpdirname)
                    db_path = os.path.join(tmpdirname, 'collection.anki21')
                elif 'collection.anki2' in z.namelist():
                    z.extract('collection.anki2', tmpdirname)
                    db_path = os.path.join(tmpdirname, 'collection.anki2')
                else:
                    print("Error: Could not find collection database in the .apkg file.")
                    return
        except zipfile.BadZipFile:
            print("Error: The file is not a valid zip archive.")
            return

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check total reps
        cursor.execute("SELECT sum(reps) FROM cards")
        total_reps = cursor.fetchone()[0] or 0
        
        # Check revlog
        cursor.execute("SELECT count(*) FROM revlog")
        total_reviews = cursor.fetchone()[0] or 0

        print(f"Total Repetitions (from cards table): {total_reps}")
        print(f"Total Review Logs (from revlog table): {total_reviews}")

        if total_reps > 0:
            print("\nConclusion: This .apkg file DOES contain your scheduling/repetition history!")
        else:
            print("\nConclusion: This .apkg file does NOT contain scheduling history. You likely unchecked 'Include scheduling information' when exporting.")

        conn.close()

if __name__ == "__main__":
    apkg_file = sys.argv[1] if len(sys.argv) > 1 else "First11.apkg"
    check_apkg(apkg_file)
