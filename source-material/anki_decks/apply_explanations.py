import sqlite3
import zipfile
import tempfile
import os
import re
import time
import hashlib

def get_csum(sfld):
    stripped = re.sub('<[^<]+>', '', sfld).strip()
    return int(hashlib.sha1(stripped.encode('utf-8')).hexdigest()[:8], 16)

# Map of note_id -> (new_front, new_back)
EXPLANATION_UPDATES = {
    # 1. Mars Aspects
    1787890619934: (
        "What are the specific additional aspects for <b>Mars</b>?",
        "<b>Mars</b> casts a full aspect on planets and signs that are <b>4th</b>, <b>7th</b>, and <b>8th</b> houses away from it.<br><br>"
        "<i><b>Why / Astrological Dynamic:</b> Mars is the cosmic warrior, protector, and defender. Beyond the standard 7th opposite sight, Mars watches over the <b>4th house</b> (protecting the home, land, and mother with martial vigilance) and the <b>8th house</b> (guarding against sudden vulnerability, unexpected attacks, crisis, and surgical danger).</i>"
    ),

    # 2. Saturn Aspects
    1787890619935: (
        "What are the specific additional aspects for <b>Saturn</b>?",
        "<b>Saturn</b> casts a full aspect on planets and signs that are <b>3rd</b>, <b>7th</b>, and <b>10th</b> houses away from it.<br><br>"
        "<i><b>Why / Astrological Dynamic:</b> Saturn represents duty, discipline, and karmic consequence. Beyond the standard 7th sight, Saturn casts his gaze on the <b>3rd house</b> (curbing rash courage and impulse with caution, fear, and endurance) and the <b>10th house</b> (demanding relentless duty, structural effort, and humble service in one's career).</i>"
    ),

    # 3. Jupiter Aspects
    1787890619936: (
        "What are the specific additional aspects for <b>Jupiter</b>?",
        "<b>Jupiter</b> casts a full aspect on planets and signs that are <b>5th</b>, <b>7th</b>, and <b>9th</b> houses away from it.<br><br>"
        "<i><b>Why / Astrological Dynamic:</b> Jupiter is the Guru of divine wisdom and grace. Beyond the standard 7th sight, Jupiter projects his sight onto the <b>5th and 9th houses</b> (the Dharma trines), blessing creative intelligence, mantras, moral purpose, and higher philosophical knowledge wherever his glance falls.</i>"
    ),

    # 4. Functional Malefics
    1787890619962: (
        "Which house lords generally get in the way of success or are considered <b>functional malefics</b>?",
        "Lords of the <b>3rd, 6th, and 11th</b> houses, as well as <i>Maraka</i> (killer) houses like the <b>2nd and 7th</b>.<br><br>"
        "<i><b>Why / Astrological Dynamic:</b> <ul>"
        "<li><b>3rd, 6th, and 11th:</b> Known as <i>Trishadaya</i> houses. They represent personal egoic striving, competition, and intense worldly desires (the 11th is 6th from the 6th; the 3rd is 8th from the 8th via <i>Bhavat Bhavam</i>), which directly clash with peaceful Dharma.</li>"
        "<li><b>2nd and 7th:</b> Known as <i>Marakas</i> (depleters) because they are the 12th (loss) from the 3rd and 8th houses of vitality and longevity.</li>"
        "</ul></i>"
    ),

    # 5. Sun for Libra Ascendant
    1787890619963: (
        "Why is the <b>Sun</b> considered a difficult planet for a <b>Libra ascendant</b>?",
        "Because it rules the <b>11th house</b>, which is considered a primary obstacle builder and Raja Yoga breaker.<br><br>"
        "<i><b>Why / Astrological Dynamic:</b> Libra is ruled by Venus, the natural adversary of the Sun. For a cardinal (movable) sign like Libra, the 11th house is the <b>Badhaka Sthana</b> (the house of primary obstruction). Furthermore, the Sun is debilitated in Libra's 1st house. Thus, the Sun's fiery individual ego clashes with Libra's path of harmonious partnership, inflating personal desires and creating stubborn obstacles.</i>"
    ),

    # 6. Friendly Planets for Aries
    1787890619961: (
        "For an <b>Aries ascendant</b>, which planets are considered <b>friendly (functional benefics)</b>?",
        "<ul><li><b>Sun</b> (rules 5th house)</li><li><b>Moon</b> (rules 4th house)</li><li><b>Mars</b> (rules 1st house)</li><li><b>Jupiter</b> (rules 9th house)</li></ul><br>"
        "<i><b>Why / Astrological Dynamic:</b> Aries is ruled by Mars. The trines (1st, 5th, 9th) are houses of pure Dharma and Lakshmi: the Sun's Moolatrikona sign falls in the 5th (Leo), and Jupiter's Moolatrikona falls in the 9th (Sagittarius). Because their primary strength is anchored in the trines, their natural capacity to bestow wisdom and life purpose directly elevates the Aries soul.</i>"
    ),

    # 7. Jupiter Universality
    1787890619816: (
        "Is the planet <b>Jupiter</b> universally helpful for all ascendants in Vedic astrology?",
        "<b>No.</b> While it is a great natural benefic, it can hinder the <i>dharma</i> and purpose for certain ascendants.<br><br>"
        "<i><b>Why / Astrological Dynamic:</b> In Vedic astrology, <b>house lordship overrides natural benevolence</b>. If Jupiter rules difficult houses (like the 3rd, 6th, or Kendras for dual signs through <i>Kendradhipati Dosha</i>), its expansive energy can expand debts, health issues, or disputes rather than peace.</i>"
    ),

    # 8. Moon and Mercury in Mental Illness
    1787890619998: (
        "Why are both the <b>Moon</b> and <b>Mercury</b> afflicted in cases of severe mental illness?",
        "Because the <b>Moon</b> rules the receptive emotional mind (<i>Manas</i>) and <b>Mercury</b> rules the rational intellect and nervous system (<i>Buddhi</i>).<br><br>"
        "<i><b>Why / Astrological Dynamic:</b> Mental stability requires two healthy faculties: the Moon provides the emotional foundation, comfort, and psychological resilience, while Mercury provides the logical discrimination and neural wiring to process reality. If only the Moon is afflicted, one experiences emotional sorrow but retains logic. If both are afflicted, the brain can neither regulate emotional pain nor rationally make sense of it.</i>"
    ),

    # 9. Angles (Kendras)
    1787890619922: (
        "What do the <b>Angles</b> (1st, 4th, 7th, 10th houses) represent in a person's life?",
        "The four concrete pillars of daily life: <b>Self (1st)</b>, <b>Home/Heart (4th)</b>, <b>Partner (7th)</b>, and <b>Career/Action (10th)</b>.<br><br>"
        "<i><b>Why / Astrological Dynamic:</b> Known as <b>Kendras</b> (Vishnu Sthanas), they represent the four pillars of the temple of life. They correspond to the cardinal directions and the daily solar cycle (Sunrise, Midnight, Sunset, Noon), providing the concrete stage where our primary worldly actions and conscious karma unfold.</i>"
    ),

    # 10. Trines (Trikonas)
    1787890619924: (
        "What role do the <b>Trines</b> (1st, 5th, 9th houses) play in a person's life?",
        "They are the houses of <b>Dharma</b>, spiritual purpose, fortune, and effortless grace.<br><br>"
        "<i><b>Why / Astrological Dynamic:</b> Known as <b>Trikonas</b> (Lakshmi Sthanas), they form an equilateral triangle of divine harmony. They bring effortless merit accumulated from past lives (<i>Purva Punya</i> in the 5th) and divine guidance/grace (<i>Dharma</i> in the 9th), naturally supporting the Soul (1st) without intense friction.</i>"
    ),

    # 11. Dusthanas (6, 8, 12)
    1787890619945: (
        "What do the <b>6th, 8th, and 12th houses</b> indicate for the Sun or Moon?",
        "Difficulties, depleted vitality, emotional vulnerability, sudden crises, loss, or foreign isolation.<br><br>"
        "<i><b>Why / Astrological Dynamic:</b> Known as <b>Dusthanas</b> (houses of sorrow and purification). The Sun (vitality/Soul) and Moon (mind/emotional comfort) are the two primary lights of consciousness. Placing either light in houses of acute struggle (6th), sudden crisis and ego death (8th), or dissolution and surrender (12th) casts a shadow over physical vitality or emotional peace.</i>"
    ),

    # 12. Good Placements for the Moon
    1787890619932: (
        "Which houses are generally considered good placements for the <b>Moon</b> to feel comfortable, and why?",
        "The Moon is most comfortable in the <b>4th House</b> and <b>9th House</b>.<br><br>"
        "<i><b>Why / Astrological Dynamic:</b> The Moon represents emotional peace, the heart, and our receptive mind. In the <b>4th house</b> (the natural home/seat of emotions), the Moon gains Digbala (directional strength) and feels safe and nurtured. In the <b>9th house</b> (the highest Dharma trine), emotional clarity aligns effortlessly with higher wisdom, optimism, and divine grace.</i>"
    ),

    # 13. Kuja Dosha Matching
    1787890619942: (
        "What is <b>Kuja Dosha</b> (Mars affliction), and why can it be beneficial if both partners have it?",
        "Kuja Dosha occurs when Mars is in the <b>1st, 4th, 7th, 8th, or 12th houses</b> from the Ascendant or Moon. If both partners have it, the affliction is neutralized.<br><br>"
        "<i><b>Why / Astrological Dynamic:</b> Mars carries intense, combustible energy and a desire for friction. If only one partner has it, their martial intensity can overwhelm a gentler partner. When both partners have it, their energy levels match, creating mutual respect and preventing one partner from dominating the other.</i>"
    ),

    # 14. Positive Role of Saturn
    1787890619958: (
        "What positive, necessary role does <b>Saturn</b> play despite being a malefic?",
        "The capacity to <b>endure</b>, have patience, face the hard road, do tedious work, and develop genuine <b>spiritual detachment</b>.<br><br>"
        "<i><b>Why / Astrological Dynamic:</b> Saturn forces us to face reality without delusions. Without Saturn's delays and friction, human beings would remain self-indulgent and undisciplined. By denying superficial comforts, Saturn builds true inner strength, humility, and the renunciation necessary for authentic spiritual liberation.</i>"
    ),

    # 15. Saturn's Fears vs. Rahu's Fears
    1787890620006: (
        "What is the difference between <b>Saturn's fears</b> and <b>Rahu's fears</b>?",
        "<b>Saturn</b> fears reality, poverty, physical aging, and failing to meet responsibilities; <b>Rahu</b> fears the unknown, paranoia, and missing out on worldly desires.<br><br>"
        "<i><b>Why / Astrological Dynamic:</b> Saturn's fear is grounded in <b>tangible reality and physical time</b> (running out of resources, getting old, concrete limitation). Rahu's fear is grounded in <b>illusion and the unlived future</b> (irrational phobias, paranoia, and the terror of not getting to experience worldly desires).</i>"
    ),

    # 16. Dual Signs (First vs Last 15 Degrees)
    1787890619903: (
        "How do the first and last 15 degrees of a <b>Dual (mutable) sign</b> behave?",
        "<ul><li><b>First 15 degrees (0°–15°):</b> Acts like a <b>Fixed sign</b> (stabilizing energy).</li><li><b>Last 15 degrees (15°–30°):</b> Acts like an <b>Active/Cardinal sign</b> (initiating change).</li></ul><br>"
        "<i><b>Why / Astrological Dynamic:</b> Dual signs (Gemini, Virgo, Sagittarius, Pisces) are bridges connecting Fixed and Cardinal qualities. In the first half, the sign stabilizes and integrates the energy of the previous fixed state; in the second half, the momentum shifts outward to prepare for the upcoming Cardinal transition.</i>"
    ),

    # 17. Mars + Saturn on Ascendant
    1787890619846: (
        "Which planetary influences on the Ascendant can cause frustration and overly high expectations?",
        "<b>Mars and Saturn</b> located on, aspecting, or impacting the Ascendant or Ascendant lord.<br><br>"
        "<i><b>Why / Astrological Dynamic:</b> Mars creates urgent ambition and impatient drive, while Saturn creates cold realism, delay, and exacting standards. When both influence the Ascendant (the self), the person feels an excruciating inner conflict between wanting immediate perfection and hitting constant walls of delay.</i>"
    ),

    # 18. Retrograde Debilitation Cancellation
    1787890619983: (
        "Does a retrograde status mathematically 'cancel' a planet's debilitation?",
        "<b>No.</b> It provides high <b>Chestabala</b> (motivational drive/effort), but the planet still struggles in its sign placement.<br><br>"
        "<i><b>Why / Astrological Dynamic:</b> In Shadbala, retrograde motion gives maximum <b>Chestabala</b> (motivational force), making the person try very hard in that planetary domain. However, it does not change <b>Uchchabala</b> (dignity/sign quality). The person has immense drive to make the debilitated area work, but must take unorthodox or circuitous paths to achieve results.</i>"
    )
}

def apply_updates(apkg_path):
    print(f"Applying astrological dynamic explanations to {apkg_path}...")
    with tempfile.TemporaryDirectory() as tmpdirname:
        with zipfile.ZipFile(apkg_path, 'r') as z:
            z.extractall(tmpdirname)
            
        zstd_db = os.path.join(tmpdirname, 'collection.anki21b')
        sqlite_db = os.path.join(tmpdirname, 'db.sqlite')
        os.system(f"zstd -d -q '{zstd_db}' -o '{sqlite_db}'")

        conn = sqlite3.connect(sqlite_db)
        conn.create_collation('unicase', lambda a, b: (a.lower() > b.lower()) - (a.lower() < b.lower()))
        cur = conn.cursor()

        updated_count = 0
        for nid, (new_q, new_a) in EXPLANATION_UPDATES.items():
            cur.execute("SELECT flds FROM notes WHERE id = ?", (nid,))
            row = cur.fetchone()
            if row:
                parts = row[0].split('\x1f')
                new_flds = f"{new_q}\x1f{new_a}" + ("\x1f" + "\x1f".join(parts[2:]) if len(parts) > 2 else "")
                new_csum = get_csum(new_q)
                cur.execute("UPDATE notes SET flds = ?, sfld = ?, csum = ?, mod = ? WHERE id = ?",
                            (new_flds, new_q, new_csum, int(time.time()), nid))
                updated_count += 1
            else:
                print(f"Warning: Note {nid} not found in database.")

        print(f"Successfully updated {updated_count} cards with intuitive 'Why / Astrological Dynamic' explanations!")

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

    print(f"Finished updating {apkg_path}!")

if __name__ == "__main__":
    apply_updates("All Decks_Cleaned.apkg")
