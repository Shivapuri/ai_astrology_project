import sqlite3
import zipfile
import os
import tempfile
import sys
import shutil

def clean_anki_database(apkg_path, csv_path, output_apkg):
    if not os.path.exists(apkg_path):
        print(f"Error: {apkg_path} not found.")
        return
        
    print(f"Reading target CSV: {csv_path}")
    # Load the 173 target cards from the CSV
    target_notes = {}
    with open(csv_path, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip() or line.startswith('#'):
                continue
            parts = line.split('\t')
            if len(parts) >= 2:
                q = parts[0].strip()
                a = parts[1].strip()
                t = parts[2].strip() if len(parts) > 2 else ""
                target_notes[q] = (a, t)
                
    print(f"Found {len(target_notes)} target questions in CSV.")

    print(f"Extracting {apkg_path}...")
    tmpdir = tempfile.mkdtemp()
    
    try:
        with zipfile.ZipFile(apkg_path, 'r') as z:
            z.extractall(tmpdir)
            
        # Determine database format
        is_zstd = False
        if os.path.exists(os.path.join(tmpdir, 'collection.anki21b')):
            is_zstd = True
            compressed_path = os.path.join(tmpdir, 'collection.anki21b')
            db_path = os.path.join(tmpdir, 'collection.db')
            os.system(f"zstd -d -q {compressed_path} -o {db_path}")
        elif os.path.exists(os.path.join(tmpdir, 'collection.anki21')):
            db_path = os.path.join(tmpdir, 'collection.anki21')
        elif os.path.exists(os.path.join(tmpdir, 'collection.anki2')):
            db_path = os.path.join(tmpdir, 'collection.anki2')
        else:
            print("Error: Could not find collection database in the .apkg file.")
            return

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Fetch all notes
        cursor.execute("SELECT id, flds, tags FROM notes")
        all_notes = cursor.fetchall()
        
        notes_to_keep = []
        notes_to_delete = []
        
        questions_found = set()
        
        for nid, flds, current_tags in all_notes:
            fields = flds.split('\x1f')
            if not fields:
                notes_to_delete.append(nid)
                continue
                
            q = fields[0].strip()
            
            # Check if this question is in our target list and hasn't been added yet (handles duplicates)
            if q in target_notes and q not in questions_found:
                questions_found.add(q)
                a, t = target_notes[q]
                
                # Reconstruct flds keeping any potential extra fields the user's template might have empty
                new_fields = [q, a] + fields[2:]
                new_flds = '\x1f'.join(new_fields)
                
                # Ensure Anki tags format (space separated with leading/trailing space)
                new_tags = f" {t} " if t else ""
                
                notes_to_keep.append((new_flds, new_tags, nid))
            else:
                # It's either a redundant question from the old CSV, or a duplicate
                notes_to_delete.append(nid)

        print(f"Updating {len(notes_to_keep)} correct notes...")
        cursor.executemany("UPDATE notes SET flds = ?, tags = ? WHERE id = ?", notes_to_keep)

        print(f"Deleting {len(notes_to_delete)} redundant/duplicate notes...")
        for nid in notes_to_delete:
            cursor.execute("DELETE FROM notes WHERE id = ?", (nid,))
            # We must also delete the associated cards for these notes
            cursor.execute("SELECT id FROM cards WHERE nid = ?", (nid,))
            card_ids = [row[0] for row in cursor.fetchall()]
            for cid in card_ids:
                cursor.execute("DELETE FROM cards WHERE id = ?", (cid,))
                # And the revlog entries
                cursor.execute("DELETE FROM revlog WHERE cid = ?", (cid,))
                
        conn.commit()
        
        # Verify final count
        cursor.execute("SELECT count(*) FROM notes")
        final_count = cursor.fetchone()[0]
        print(f"Final note count in database: {final_count}")
        
        conn.close()

        print("Repackaging the .apkg file...")
        # Re-compress if necessary
        if is_zstd:
            os.remove(compressed_path)
            os.system(f"zstd -q {db_path} -o {compressed_path}")
            os.remove(db_path)
            
        with zipfile.ZipFile(output_apkg, 'w', zipfile.ZIP_DEFLATED) as z_out:
            for root, _, files in os.walk(tmpdir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, tmpdir)
                    z_out.write(file_path, arcname)
                    
        print(f"SUCCESS! Cleaned deck saved to {output_apkg}")

    finally:
        shutil.rmtree(tmpdir)

if __name__ == "__main__":
    apkg_in = sys.argv[1] if len(sys.argv) > 1 else "MessyDeck.apkg"
    csv_target = sys.argv[2] if len(sys.argv) > 2 else "foundation_vids_01_11_restored.csv"
    apkg_out = sys.argv[3] if len(sys.argv) > 3 else "CleanDeck.apkg"
    
    clean_anki_database(apkg_in, csv_target, apkg_out)
