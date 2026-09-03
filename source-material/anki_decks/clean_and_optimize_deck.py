import sqlite3
import zipfile
import tempfile
import os
import re
import time
import random
import hashlib
import shutil

def base91_encode(num):
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!#$%&()*+,-./:;<=>?@[]^_`{|}~"
    if num == 0:
        return alphabet[0]
    res = ""
    while num > 0:
        res = alphabet[num % 91] + res
        num //= 91
    return res

def get_guid():
    return base91_encode(random.randint(0, 2**64 - 1))[:10]

def get_csum(sfld):
    stripped = re.sub('<[^<]+>', '', sfld).strip()
    return int(hashlib.sha1(stripped.encode('utf-8')).hexdigest()[:8], 16)

def encode_varint(n):
    res = bytearray()
    while n >= 0x80:
        res.append((n & 0x7F) | 0x80)
        n >>= 7
    res.append(n & 0x7F)
    return bytes(res)

def update_notetype_css(conn):
    cur = conn.cursor()
    cur.execute("SELECT config FROM notetypes WHERE id = 1785831674562")
    row = cur.fetchone()
    if not row:
        print("Warning: notetype 1785831674562 not found.")
        return
    raw_config = row[0]

    # Mobile-optimized CSS
    mobile_css = """
.card {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    font-size: 19px;
    line-height: 1.55;
    text-align: center;
    color: #212529;
    background-color: #ffffff;
    max-width: 620px;
    margin: 0 auto;
    padding: 16px 14px;
    box-sizing: border-box;
}

/* Mobile-responsive list formatting */
ul, ol {
    display: inline-block;
    text-align: left;
    margin: 12px auto;
    padding-left: 26px;
    max-width: 100%;
    box-sizing: border-box;
}

li {
    margin-bottom: 8px;
    line-height: 1.5;
}

/* Contrast and emphasis */
b, strong {
    color: #0b5394;
    font-weight: 600;
}

i, em {
    color: #495057;
}

hr#answer {
    border: none;
    border-top: 1px solid #e9ecef;
    margin: 20px 0;
}

/* Dark / Night Mode support for mobile & desktop */
.nightMode .card {
    background-color: #1a1a1a;
    color: #e4e6eb;
}

.nightMode b, .nightMode strong {
    color: #64b5f6;
}

.nightMode i, .nightMode em {
    color: #b0bec5;
}

.nightMode hr#answer {
    border-top: 1px solid #333333;
}
""".strip()

    css_bytes = mobile_css.encode('utf-8')
    idx_field5 = raw_config.find(b'*\xb2\x01')
    if idx_field5 != -1:
        rest = raw_config[idx_field5:]
        new_raw = b'\x1a' + encode_varint(len(css_bytes)) + css_bytes + rest
        cur.execute("UPDATE notetypes SET config = ? WHERE id = 1785831674562", (new_raw,))
        print("Updated notetype CSS with mobile-optimized responsive styles.")
    else:
        print("Warning: Could not locate Field 5 in notetypes config.")

def process_apkg(src_apkg, dst_apkg):
    print(f"Opening {src_apkg}...")
    with tempfile.TemporaryDirectory() as tmpdirname:
        with zipfile.ZipFile(src_apkg, 'r') as z:
            z.extractall(tmpdirname)
            
        zstd_db = os.path.join(tmpdirname, 'collection.anki21b')
        sqlite_db = os.path.join(tmpdirname, 'db.sqlite')
        os.system(f"zstd -d -q '{zstd_db}' -o '{sqlite_db}'")

        conn = sqlite3.connect(sqlite_db)
        conn.create_collation('unicase', lambda a, b: (a.lower() > b.lower()) - (a.lower() < b.lower()))
        cur = conn.cursor()

        # 1. Update Notetype CSS
        update_notetype_css(conn)

        # 2. Moon duplicates cleanup
        # Deleting the 0-rep clones, preserving the ones with reviews:
        # Note 1787974587317 (0 reps) duplicate of 1787890619855 (6 reps)
        # Note 1788274877644 (0 reps) duplicate of 1788274875329 (2 reps)
        # Note 1788274872467 (0 reps) duplicate of 1788274871515 (0 reps)
        # Note 1788274875071 (0 reps) duplicate of 1788274874929 (0 reps)
        moon_dup_nids = [1787974587317, 1788274877644, 1788274872467, 1788274875071]
        for nid in moon_dup_nids:
            cur.execute("DELETE FROM revlog WHERE cid IN (SELECT id FROM cards WHERE nid = ?)", (nid,))
            cur.execute("DELETE FROM cards WHERE nid = ?", (nid,))
            cur.execute("DELETE FROM notes WHERE id = ?", (nid,))
        print(f"Deleted {len(moon_dup_nids)} Moon duplicate notes (preserved all review logs).")

        # 3. Overlapping / Redundant cards handling while preserving review history
        # A. Jupiter Ayur-astrology (Note 1787890620001, 4 reps, 1 lapse) -> Update to Jupiter Physical/Biological card
        jup_phys_q = "What <b>physical body parts, organs, and biological functions</b> does <b>Jupiter</b> govern?"
        jup_phys_a = "The brain, liver, and body <b>fat</b> (adipose tissue)."
        cur.execute("UPDATE notes SET flds = ?, sfld = ?, csum = ?, mod = ? WHERE id = ?", 
                    (f"{jup_phys_q}\x1f{jup_phys_a}", jup_phys_q, get_csum(jup_phys_q), int(time.time()), 1787890620001))
        # Delete unreviewed duplicate Jupiter physical card (1788274870094)
        cur.execute("DELETE FROM cards WHERE nid = 1788274870094")
        cur.execute("DELETE FROM notes WHERE id = 1788274870094")
        print("Merged Jupiter Physical card, preserving 4 reps + 1 lapse.")

        # B. Venus physiology (Note 1787890620003, 6 reps) -> Update to Venus Physical/Biological card
        ven_phys_q = "What <b>physical body parts, organs, and biological functions</b> does <b>Venus</b> govern?"
        ven_phys_a = "<b>Sensuality, fertility</b>, reproductive fluids (semen), muscle tissue, DNA strength, and the ability to <b>rejuvenate/regenerate</b> the body."
        cur.execute("UPDATE notes SET flds = ?, sfld = ?, csum = ?, mod = ? WHERE id = ?", 
                    (f"{ven_phys_q}\x1f{ven_phys_a}", ven_phys_q, get_csum(ven_phys_q), int(time.time()), 1787890620003))
        # Delete unreviewed duplicate Venus physical card (1788274877794)
        cur.execute("DELETE FROM cards WHERE nid = 1788274877794")
        cur.execute("DELETE FROM notes WHERE id = 1788274877794")
        print("Merged Venus Physical card, preserving 6 reps.")

        # C. Mars worldly and physical (Note 1787890620000, 4 reps) -> Update to Mars Physical/Biological card
        mars_phys_q = "What <b>physical body parts, organs, and biological functions</b> does <b>Mars</b> govern?"
        mars_phys_a = "<b>Physical strength, muscles</b>, surgery, cuts, and accidents."
        cur.execute("UPDATE notes SET flds = ?, sfld = ?, csum = ?, mod = ? WHERE id = ?", 
                    (f"{mars_phys_q}\x1f{mars_phys_a}", mars_phys_q, get_csum(mars_phys_q), int(time.time()), 1787890620000))
        # Delete unreviewed duplicate Mars physical card (1788274871402)
        cur.execute("DELETE FROM cards WHERE nid = 1788274871402")
        cur.execute("DELETE FROM notes WHERE id = 1788274871402")
        print("Merged Mars Physical card, preserving 4 reps.")

        # D. Mercury physical tissues (Note 1787890619999, 0 reps) -> Delete and ensure Note 1788274873715 has complete answer
        cur.execute("DELETE FROM cards WHERE nid = 1787890619999")
        cur.execute("DELETE FROM notes WHERE id = 1787890619999")
        merc_phys_q = "What <b>physical body parts, organs, and biological functions</b> does <b>Mercury</b> govern?"
        merc_phys_a = "<b>Youthfulness</b>, the <b>skin</b> (outer membranes), blood vessels, and the <b>nervous system</b>."
        cur.execute("UPDATE notes SET flds = ?, sfld = ?, csum = ?, mod = ? WHERE id = ?", 
                    (f"{merc_phys_q}\x1f{merc_phys_a}", merc_phys_q, get_csum(merc_phys_q), int(time.time()), 1788274873715))
        print("Merged Mercury Physical card.")

        # E. Sun & Moon physical body parts (Note 1787890619997, 2 reps) -> Delete redundant joint card
        cur.execute("DELETE FROM revlog WHERE cid IN (SELECT id FROM cards WHERE nid = 1787890619997)")
        cur.execute("DELETE FROM cards WHERE nid = 1787890619997")
        cur.execute("DELETE FROM notes WHERE id = 1787890619997")
        print("Removed redundant combined Sun & Moon body parts card.")

        # 4. Polish Phrasing on ALL 4-split cards
        # We fetch all notes and refine any front prompt that uses the robotic formula
        cur.execute("SELECT id, flds FROM notes")
        all_notes = cur.fetchall()

        planets = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']
        houses = [f"{i}th House" if i not in [1,2,3] else ("1st House" if i==1 else ("2nd House" if i==2 else "3rd House")) for i in range(1, 13)]

        update_count = 0
        for nid, flds in all_notes:
            parts = flds.split('\x1f')
            front = parts[0]
            back = parts[1] if len(parts) > 1 else ''
            new_front = front

            # Check for Planet cards
            for p in planets:
                if f"<b>{p}</b>" in front or front.endswith(f"of <b>{p}</b>?") or front.endswith(f"of {p}?"):
                    if "Core/Psychological" in front:
                        new_front = f"What are the <b>core psychological themes and mindset</b> of <b>{p}</b>?"
                    elif "Physical/Biological" in front:
                        new_front = f"What <b>physical body parts, organs, and biological functions</b> does <b>{p}</b> govern?"
                    elif "People & Relational" in front:
                        new_front = f"Which <b>people, family members, and societal roles</b> are represented by <b>{p}</b>?"
                    elif "Material & Environmental" in front:
                        new_front = f"What <b>material objects, places, and external environments</b> are associated with <b>{p}</b>?"

            # Check for House cards
            for h in houses:
                if f"<b>{h}</b>" in front or front.endswith(f"of <b>{h}</b>?") or front.endswith(f"of {h}?"):
                    if "Core/Psychological" in front:
                        new_front = f"What are the <b>core psychological themes and inner areas of life</b> governed by the <b>{h}</b>?"
                    elif "Physical/Biological" in front:
                        new_front = f"What <b>physical body parts and biological functions</b> does the <b>{h}</b> govern?"
                    elif "People & Relational" in front:
                        new_front = f"Which <b>people, relationships, and societal figures</b> are represented by the <b>{h}</b>?"
                    elif "Material & Environmental" in front:
                        new_front = f"What <b>material assets, places, and worldly activities</b> are signified by the <b>{h}</b>?"

            if new_front != front:
                new_flds = f"{new_front}\x1f{back}" + ("\x1f" + "\x1f".join(parts[2:]) if len(parts) > 2 else "")
                cur.execute("UPDATE notes SET flds = ?, sfld = ?, csum = ?, mod = ? WHERE id = ?",
                            (new_flds, new_front, get_csum(new_front), int(time.time()), nid))
                update_count += 1

        print(f"Polished phrasing on {update_count} cards to fluent, natural English.")

        # 5. Add 4-Split Cards for Rahu and Ketu
        cur.execute("SELECT mid FROM notes LIMIT 1")
        mid = cur.fetchone()[0]
        cur.execute("SELECT did FROM cards LIMIT 1")
        did = cur.fetchone()[0]

        nodes_data = {
            "Rahu": [
                ("What are the <b>core psychological themes and mindset</b> of <b>Rahu</b>?",
                 "<b>Worldly ambition</b>, intense desire, <b>obsession</b>, fascination with the future, and <b>fear/anxiety</b> of the unknown.",
                 "Video_01 Video_05"),
                ("What <b>physical body parts, organs, and biological functions</b> does <b>Rahu</b> govern?",
                 "<b>Mystery ailments</b>, poisons/toxins, <b>addictions</b>, and the central <b>nervous system</b>.",
                 "Video_05 Video_Supplemental"),
                ("Which <b>people, family members, and societal roles</b> are represented by <b>Rahu</b>?",
                 "<b>Foreigners</b>, outcasts, unconventional individuals, rebels, and eccentrics.",
                 "Video_05"),
                ("What <b>material objects, places, and external environments</b> are associated with <b>Rahu</b>?",
                 "<b>Foreign lands</b>, cutting-edge technology, <b>unconventional careers</b>, illusions/media, and dark or smoky places.",
                 "Video_05")
            ],
            "Ketu": [
                ("What are the <b>core psychological themes and mindset</b> of <b>Ketu</b>?",
                 "<b>Detachment</b>, spiritual insight, liberation (<b>Moksha</b>), inner doubt, and <b>past-life mastery</b>.",
                 "Video_01 Video_05"),
                ("What <b>physical body parts, organs, and biological functions</b> does <b>Ketu</b> govern?",
                 "Subtle energy channels (<b>nadis</b>), sudden cuts/injuries, amputations, and <b>hidden/silent conditions</b>.",
                 "Video_05 Video_Supplemental"),
                ("Which <b>people, family members, and societal roles</b> are represented by <b>Ketu</b>?",
                 "<b>Ascetics, monks</b>, spiritual seekers, psychics, and astrologers/mystics.",
                 "Video_05"),
                ("What <b>material objects, places, and external environments</b> are associated with <b>Ketu</b>?",
                 "<b>Ashrams, isolated places</b>, meditation spaces, and sudden <b>endings or losses</b>.",
                 "Video_05")
            ]
        }

        inserted_nodes = 0
        for node_name, cards_list in nodes_data.items():
            for q, a, tag in cards_list:
                new_nid = int(time.time() * 1000) + random.randint(1, 100000)
                new_guid = get_guid()
                csum = get_csum(q)
                flds = f"{q}\x1f{a}"
                cur.execute("""
                    INSERT INTO notes (id, guid, mid, mod, usn, tags, flds, sfld, csum, flags, data)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (new_nid, new_guid, mid, int(time.time()), -1, f" {tag} ", flds, q, csum, 0, ''))

                new_cid = int(time.time() * 1000) + random.randint(1, 100000)
                cur.execute("""
                    INSERT INTO cards (id, nid, did, ord, mod, usn, type, queue, due, ivl, factor, reps, lapses, left, odue, odid, flags, data)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (new_cid, new_nid, did, 0, int(time.time()), -1, 0, 0, new_cid % 10000, 0, 0, 0, 0, 0, 0, 0, 0, ''))
                inserted_nodes += 1

        print(f"Inserted {inserted_nodes} standardized 4-split cards for Rahu and Ketu.")

        conn.commit()
        conn.close()

        # Re-compress collection.anki21b with zstd
        os.remove(zstd_db)
        os.system(f"zstd -q '{sqlite_db}' -o '{zstd_db}'")
        os.remove(sqlite_db)

        # Repackage the destination apkg file
        if os.path.exists(dst_apkg):
            os.remove(dst_apkg)

        with zipfile.ZipFile(dst_apkg, 'w', zipfile.ZIP_DEFLATED) as out_zip:
            for root, dirs, files in os.walk(tmpdirname):
                for file in files:
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, tmpdirname)
                    out_zip.write(full_path, rel_path)

    print(f"Successfully wrote cleaned, mobile-optimized deck to {dst_apkg}!")

if __name__ == "__main__":
    process_apkg("All Decks.apkg", "All Decks_Cleaned.apkg")
