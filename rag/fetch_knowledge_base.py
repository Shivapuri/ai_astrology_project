import os
import csv
import json
import requests
import re
import unicodedata
from bs4 import BeautifulSoup
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

DATA_DIR = os.path.join(os.path.dirname(__file__), "astrology_rag_data")

def ensure_data_dir():
    """Ensure destination directory exists."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        print(f"Created directory: {DATA_DIR}")

def download_tetrabiblos():
    """Download and carefully parse Ptolemy's Tetrabiblos, avoiding footnote corruption."""
    base_url = "https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Ptolemy/Tetrabiblos/"
    pages = ["1A*.html", "1B*.html", "2A*.html", "2B*.html", "2C*.html", "3A*.html", "3B*.html", "3C*.html", "3D*.html", "4A*.html", "4B*.html", "4C*.html"]
    
    file_path = os.path.join(DATA_DIR, "tetrabiblos.txt")
    print(f"Downloading and cleaning Ptolemy's Tetrabiblos...")
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    full_text = ["=== PTOLEMY'S TETRABIBLOS ===\n"]

    for page in pages:
        try:
            resp = requests.get(base_url + page, headers=headers, verify=False, timeout=30)
            resp.encoding = 'utf-8'
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # DESTROY NOISE: Remove footnotes, tables, and navigational elements
            for noise in soup.find_all(['table', 'script', 'style', 'sup']):
                noise.decompose()
            for a_tag in soup.find_all('a'):
                # Remove hyperlinks that point to footnotes
                if a_tag.get('href', '').startswith('#note') or a_tag.get('onmouseover'):
                    a_tag.decompose()

            # EXTRACT ONLY PARAGRAPHS
            paragraphs = soup.find_all('p')
            for p in paragraphs:
                text = p.get_text(strip=True)
                # Normalize and remove weird unicode spacing
                text = unicodedata.normalize('NFKC', text)
                if len(text) > 50 and "LacusCurtius" not in text: # Skip tiny fragments
                    full_text.append(text + "\n")
                    
            print(f"  [+] Cleaned and saved {page}")
        except Exception as e:
            print(f"  [-] Error on {page}: {e}")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write("\n".join(full_text))

def generate_sample_dataset():
    """Generate a structured CSV dataset of Hellenistic interpretations."""
    file_path = os.path.join(DATA_DIR, "classical_interpretations.csv")
    print("Generating classical interpretations CSV dataset...")
    
    rows = [
        ["planet", "sign", "house", "dignity", "sect", "classical_source", "interpretation"],
        ["Sun", "Aries", "House_1", "Exaltation", "Day", "Ptolemy / Vettius Valens", "The Sun exalted in Aries in the 1st House yields high leadership, noble character, and strong vitality."],
        ["Sun", "Libra", "House_7", "Fall", "Night", "Vettius Valens", "Sun in Fall in Libra in 7th house indicates loss of personal authority and dependence on partners."],
        ["Moon", "Taurus", "House_2", "Exaltation", "Night", "Dorotheus of Sidon", "Moon exalted in Taurus in 2nd House signifies steady material prosperity and abundant resources."],
        ["Moon", "Scorpio", "House_8", "Fall", "Day", "Vettius Valens", "Moon in Scorpio in 8th house brings financial anxieties, sudden shifts in fortune, and emotional depth."],
        ["Mars", "Cancer", "House_6", "Fall", "Day", "Vettius Valens", "Mars in Fall in Cancer in the 6th House during a Day Chart acts as a contrary malefic, causing acute illness, conflicts with subordinates, or sudden inflammation."],
        ["Mars", "Capricorn", "House_10", "Exaltation", "Night", "Ptolemy", "Mars exalted in Capricorn in the 10th House gives military power, executive command, and decisive success."],
        ["Venus", "Libra", "House_1", "Domicile", "Night", "Dorotheus of Sidon", "Venus in Domicile in Libra in the 1st House brings grace, artistic beauty, harmonious partnerships, and physical charm."],
        ["Venus", "Virgo", "House_12", "Fall", "Day", "Vettius Valens", "Venus in Fall in Virgo in the 12th House points to secret romantic troubles, emotional isolation, or expenditures on hidden vices."],
        ["Jupiter", "Cancer", "House_9", "Exaltation", "Day", "Ptolemy", "Jupiter exalted in Cancer in the 9th House indicates high wisdom, divine favors, successful long travels, and philosophical mastery."],
        ["Saturn", "Libra", "House_1", "Exaltation", "Day", "Vettius Valens", "Saturn exalted in Libra in the 1st House brings grave wisdom, patience, judicial authority, and longevity."],
        ["Saturn", "Aries", "House_7", "Fall", "Night", "Ptolemy", "Saturn in Fall in Aries in the 7th House causes delays in marriage, harsh obstacles in public relations, and heavy burdens through partners."]
    ]
    
    with open(file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(rows)
    print(f"Saved classical interpretations dataset to {file_path}")

def generate_core_rules():
    """Generate hellenistic_core_rules.txt containing foundational classical guidelines."""
    file_path = os.path.join(DATA_DIR, "hellenistic_core_rules.txt")
    print("Generating Hellenistic core rules document...")
    
    content = """==================================================
HELLENISTIC ASTROLOGY: CORE GROUND RULES & DOCTRINE
==================================================

1. SECT DOCTRINE (DAY VS NIGHT CHART)
- Day Chart (Diurnal): Sun is above the horizon (Houses 7, 8, 9, 10, 11, 12).
  * Diurnal Benefic: Jupiter (most constructive growth planet in day chart).
  * Diurnal Malefic: Saturn (tempered and less destructive in day chart).
  * Contrary Malefic: Mars (most destructive in day chart).
- Night Chart (Nocturnal): Sun is below the horizon (Houses 1, 2, 3, 4, 5, 6).
  * Nocturnal Benefic: Venus (most constructive harmonizing planet in night chart).
  * Nocturnal Malefic: Mars (tempered and productive warrior in night chart).
  * Contrary Malefic: Saturn (most destructive and cold in night chart).

2. ESSENTIAL DIGNITIES
- Domicile (Ruler at Home): Planet in its own sign (e.g., Sun in Leo, Venus in Libra/Taurus). Max strength.
- Exaltation (Honored Guest): Planet in sign of exaltation (e.g., Sun in Aries, Moon in Taurus, Saturn in Libra). High prestige.
- Detriment (Exile): Planet opposite its domicile (e.g., Sun in Aquarius, Venus in Aries/Scorpio). Constrained.
- Fall (Dishonor): Planet opposite its exaltation (e.g., Sun in Libra, Mars in Cancer, Saturn in Aries). Debilitated.
- Peregrine (Wandering): Planet with no major dignity in its current location.

3. THE 12 WHOLE SIGN HOUSES (TOPOLOGY)
- House 1 (Ascendant / Helm): Life, physical vitality, mind, overall direction.
- House 2 (Gate of Hades / Wealth): Material assets, livelihood, moveable property.
- House 3 (Goddess / Siblings): Brothers/sisters, short journeys, rituals, dreams.
- House 4 (Subterranean / Parents): Fathers, ancestors, home, property, end of life.
- House 5 (Good Fortune / Children): Children, pleasure, creativity, good luck.
- House 6 (Bad Fortune / Illness): Disease, bodily ailments, servants, hard labor.
- House 7 (Setting / Marriage): Spouse, open relationships, legal contracts, death location.
- House 8 (Idle / Death): Estate of others, inheritance, fear, loss, debt.
- House 9 (God / Higher Wisdom): Philosophy, divine science, long foreign travels, religion.
- House 10 (Midheaven / Career): Action, reputation, public honor, profession, mother.
- House 11 (Good Spirit / Friends): Allies, hopes, patronage, social awards.
- House 12 (Bad Spirit / Hidden Enemies): Secret enemies, self-undoing, exile, confinement.

4. INTERPRETATION MANDATE FOR LLMS
- Evaluate planets primarily by Sect, Essential Dignity, and Whole Sign House placement.
- Do NOT substitute classical Hellenistic conditions with modern psychological theories.
"""
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Saved core rules to {file_path}")

def main():
    print("--- Phase 1: Fetching & Building Hellenistic Knowledge Base ---")
    ensure_data_dir()
    download_tetrabiblos()
    generate_sample_dataset()
    generate_core_rules()
    print("--- Phase 1 Complete! Data stored in /astrology_rag_data/ ---")

if __name__ == "__main__":
    main()
