import sqlite3
import zipfile
import tempfile
import os
import re
import time
import random
import hashlib

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

def run_split(apkg_path):
    print(f"Splitting remaining joint Rahu/Ketu cards in {apkg_path}...")
    with tempfile.TemporaryDirectory() as tmpdirname:
        with zipfile.ZipFile(apkg_path, 'r') as z:
            z.extractall(tmpdirname)
            
        zstd_db = os.path.join(tmpdirname, 'collection.anki21b')
        sqlite_db = os.path.join(tmpdirname, 'db.sqlite')
        os.system(f"zstd -d -q '{zstd_db}' -o '{sqlite_db}'")

        conn = sqlite3.connect(sqlite_db)
        conn.create_collation('unicase', lambda a, b: (a.lower() > b.lower()) - (a.lower() < b.lower()))
        cur = conn.cursor()

        cur.execute("SELECT mid FROM notes LIMIT 1")
        mid = cur.fetchone()[0]
        cur.execute("SELECT did FROM cards LIMIT 1")
        did = cur.fetchone()[0]

        # ---------------------------------------------------------------------
        # 1. Note 1787890620014: Classical Dignity Opinions (9 reps)
        # Update in-place to Parashara (BPHS) opinion (keeps 9 reps)
        # ---------------------------------------------------------------------
        q_para = "According to classical authority (<b>Brihat Parashara Hora Shastra</b>), which signs are the <b>Exaltation</b> and <b>Fall</b> of <b>Rahu</b> and <b>Ketu</b>?"
        a_para = (
            "<ul>"
            "<li><b>Rahu:</b> Exalted in <b>Taurus</b>, Falls in <b>Scorpio</b>.</li>"
            "<li><b>Ketu:</b> Exalted in <b>Scorpio</b>, Falls in <b>Taurus</b>.</li>"
            "</ul><br>"
            "<i><b>Why / Astrological Dynamic:</b> Taurus is a grounded, earthy, Venusian sign where Rahu's chaotic material hunger stabilizes. "
            "Scorpio is a mystical, transformative, Martian water sign where Ketu's piercing insight and renunciation reach their highest power.</i>"
        )
        cur.execute("UPDATE notes SET flds = ?, sfld = ?, csum = ?, mod = ? WHERE id = 1787890620014",
                    (f"{q_para}\x1f{a_para}", q_para, get_csum(q_para), int(time.time())))
        print("Updated Note 1787890620014 -> Parashara Exaltation/Fall (preserved 9 reviews).")

        # Insert new Card: Ramadayalu (Sanketanidhi) Rulerships
        q_rama = "According to <b>Ramadayalu (Sanketanidhi)</b>, which signs are considered the <b>Own signs (rulerships)</b> of <b>Rahu</b> and <b>Ketu</b>?"
        a_rama = (
            "<ul>"
            "<li><b>Rahu:</b> Rules <b>Virgo</b> (shares with Mercury).</li>"
            "<li><b>Ketu:</b> Rules <b>Pisces</b> (shares with Jupiter).</li>"
            "</ul><br>"
            "<i><b>Why / Astrological Dynamic:</b> In Sanketanidhi, Rahu shares rulership of Virgo (intellect, detail-management, and worldly problem-solving), "
            "while Ketu shares rulership of Pisces (pure spiritual transcendence, dissolution of the ego, and Moksha at the end of the zodiac).</i>"
        )
        new_nid_rama = int(time.time() * 1000) + random.randint(1, 10000)
        cur.execute("""
            INSERT INTO notes (id, guid, mid, mod, usn, tags, flds, sfld, csum, flags, data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (new_nid_rama, get_guid(), mid, int(time.time()), -1, " Video_11 Video_Supplemental ", f"{q_rama}\x1f{a_rama}", q_rama, get_csum(q_rama), 0, ''))
        new_cid_rama = int(time.time() * 1000) + random.randint(1, 10000)
        cur.execute("""
            INSERT INTO cards (id, nid, did, ord, mod, usn, type, queue, due, ivl, factor, reps, lapses, left, odue, odid, flags, data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (new_cid_rama, new_nid_rama, did, 0, int(time.time()), -1, 0, 0, new_cid_rama % 10000, 0, 0, 0, 0, 0, 0, 0, 0, ''))
        print("Inserted new Card -> Ramadayalu Rulerships.")

        # ---------------------------------------------------------------------
        # 2. Note 1787890619862: Focus of Ketu vs Rahu (6 reps)
        # Update in-place to focus exclusively on Rahu (keeps 6 reps)
        # ---------------------------------------------------------------------
        q_rahu_focus = "What is the primary psychological focus and driving energy of <b>Rahu</b> (North Node)?"
        a_rahu_focus = (
            "<b>Outward / extroverted energy</b>, intense <b>worldly ambitions</b>, compulsions, and exploring the unfamiliar.<br><br>"
            "<i><b>Why / Astrological Dynamic:</b> Rahu is mythologically the head without a body. Because it has no stomach, it has an insatiable hunger to taste, explore, and master new worldly experiences in this lifetime.</i>"
        )
        cur.execute("UPDATE notes SET flds = ?, sfld = ?, csum = ?, mod = ? WHERE id = 1787890619862",
                    (f"{q_rahu_focus}\x1f{a_rahu_focus}", q_rahu_focus, get_csum(q_rahu_focus), int(time.time())))
        print("Updated Note 1787890619862 -> Dedicated Rahu Psychological Focus (preserved 6 reviews).")

        # Insert new Card: Ketu Psychological Focus
        q_ketu_focus = "What is the primary psychological focus and driving energy of <b>Ketu</b> (South Node)?"
        a_ketu_focus = (
            "<b>Inward / introverted energy</b>, past-life mastery, detachment, doubt, and <b>spiritual liberation (Moksha)</b>.<br><br>"
            "<i><b>Why / Astrological Dynamic:</b> Ketu is mythologically the body without a head. Having already experienced and exhausted worldly attachments in past lives, Ketu cannot swallow worldly things and naturally points inward toward divine realization.</i>"
        )
        new_nid_ketu_f = int(time.time() * 1000) + random.randint(10001, 20000)
        cur.execute("""
            INSERT INTO notes (id, guid, mid, mod, usn, tags, flds, sfld, csum, flags, data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (new_nid_ketu_f, get_guid(), mid, int(time.time()), -1, " Video_05 Video_Supplemental ", f"{q_ketu_focus}\x1f{a_ketu_focus}", q_ketu_focus, get_csum(q_ketu_focus), 0, ''))
        new_cid_ketu_f = int(time.time() * 1000) + random.randint(10001, 20000)
        cur.execute("""
            INSERT INTO cards (id, nid, did, ord, mod, usn, type, queue, due, ivl, factor, reps, lapses, left, odue, odid, flags, data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (new_cid_ketu_f, new_nid_ketu_f, did, 0, int(time.time()), -1, 0, 0, new_cid_ketu_f % 10000, 0, 0, 0, 0, 0, 0, 0, 0, ''))
        print("Inserted new Card -> Dedicated Ketu Psychological Focus.")

        # ---------------------------------------------------------------------
        # 3. Note 1787890619817: Incarnated Consciousness (1 rep)
        # Update in-place to focus exclusively on Rahu's karmic direction (keeps 1 rep)
        # ---------------------------------------------------------------------
        q_rahu_karmic = "In terms of our incarnated path of consciousness, what does <b>Rahu</b> indicate?"
        a_rahu_karmic = (
            "Our <b>future karmic direction</b>: the new, unfamiliar skills, desires, and experiences we came into this lifetime to develop.<br><br>"
            "<i><b>Why / Astrological Dynamic:</b> Rahu represents the cutting-edge frontier of our growth—the areas of life where we feel raw, inexperienced, yet intensely compelled to evolve.</i>"
        )
        cur.execute("UPDATE notes SET flds = ?, sfld = ?, csum = ?, mod = ? WHERE id = 1787890619817",
                    (f"{q_rahu_karmic}\x1f{a_rahu_karmic}", q_rahu_karmic, get_csum(q_rahu_karmic), int(time.time())))
        print("Updated Note 1787890619817 -> Dedicated Rahu Karmic Direction (preserved 1 review).")

        # Insert new Card: Ketu Karmic Direction
        q_ketu_karmic = "In terms of our incarnated path of consciousness, what does <b>Ketu</b> indicate?"
        a_ketu_karmic = (
            "Where we have <b>already been in past lifetimes</b>: our ingrained talents, masteries, and areas where we must develop non-attachment.<br><br>"
            "<i><b>Why / Astrological Dynamic:</b> Ketu shows where we already possess intuitive competence from past incarnations; attempting to find ultimate fulfillment there leads to stagnation because that karma is already spent fuel.</i>"
        )
        new_nid_ketu_k = int(time.time() * 1000) + random.randint(20001, 30000)
        cur.execute("""
            INSERT INTO notes (id, guid, mid, mod, usn, tags, flds, sfld, csum, flags, data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (new_nid_ketu_k, get_guid(), mid, int(time.time()), -1, " Video_01 Video_05 ", f"{q_ketu_karmic}\x1f{a_ketu_karmic}", q_ketu_karmic, get_csum(q_ketu_karmic), 0, ''))
        new_cid_ketu_k = int(time.time() * 1000) + random.randint(20001, 30000)
        cur.execute("""
            INSERT INTO cards (id, nid, did, ord, mod, usn, type, queue, due, ivl, factor, reps, lapses, left, odue, odid, flags, data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (new_cid_ketu_k, new_nid_ketu_k, did, 0, int(time.time()), -1, 0, 0, new_cid_ketu_k % 10000, 0, 0, 0, 0, 0, 0, 0, 0, ''))
        print("Inserted new Card -> Dedicated Ketu Karmic Mastery.")

        # ---------------------------------------------------------------------
        # 4. Note 1787890619861: Shadow Planets Nature (4 reps)
        # Polish into a clear, unified concept card (keeps 4 reps)
        # ---------------------------------------------------------------------
        q_shadow = "Astronomically and symbolically, what are <b>Rahu and Ketu</b> (the Lunar Nodes) and how do they function?"
        a_shadow = (
            "They are <b>shadow points (Chhaya Grahas)</b> where the orbits of the Sun and Moon intersect (producing eclipses). They give results by <b>adopting the energy of their sign/house lord</b> and casting a shadow over our consciousness.<br><br>"
            "<i><b>Why / Astrological Dynamic:</b> Unlike physical planets, the Lunar Nodes have no physical mass. They act as cosmic lenses or amplifiers, taking on the qualities of whichever sign, house, and ruling planet they occupy.</i>"
        )
        cur.execute("UPDATE notes SET flds = ?, sfld = ?, csum = ?, mod = ? WHERE id = 1787890619861",
                    (f"{q_shadow}\x1f{a_shadow}", q_shadow, get_csum(q_shadow), int(time.time())))
        print("Updated Note 1787890619861 -> Refined Shadow Points definition (preserved 4 reviews).")

        conn.commit()
        conn.close()

        # Recompress
        os.remove(zstd_db)
        os.system(f"zstd -q '{sqlite_db}' -o '{zstd_db}'")
        os.remove(sqlite_db)

        # Repackage
        if os.path.exists(apkg_path):
            os.remove(apkg_path)

        with zipfile.ZipFile(apkg_path, 'w', zipfile.ZIP_DEFLATED) as out_zip:
            for root, dirs, files in os.walk(tmpdirname):
                for file in files:
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, tmpdirname)
                    out_zip.write(full_path, rel_path)

    print(f"Successfully finished splitting Rahu and Ketu cards in {apkg_path}!")

if __name__ == "__main__":
    run_split("All Decks_Cleaned.apkg")
