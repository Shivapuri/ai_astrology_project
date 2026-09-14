---
name: astrology-case-study-generator
description: Generates interactive, pedagogical Vedic astrology case studies for historical, celebrity, or client horoscopes. Integrates the Astra computation engine (Python/Kala methodology, Classical Yogas & Breakers) with the Ryan Kurczak Vedic Astrology knowledge vault, produces both an Obsidian Markdown study guide (.md) and a standalone interactive HTML file (.html) with collapsible active-recall self-testing controls, and mandates independent subagent critic reviews.
---

# 🎓 Astrology Case Study & Learning Material Generator

## Overview
This skill defines the standardized end-to-end workflow for transforming raw astrological birth data into rigorous, interactive, and pedagogically sound case studies. It connects precision astronomical calculations from the **Astra** engine with the classical Parashari and Jaimini teachings preserved in the **Vedic Astrology Vault** (`/Users/hajnaljanos/PycharmProjects/vedic-astrology-vault/vault/`).

Every case study produces two matching, companion deliverables saved in `case_studies/` or `vault/Case Studies/`:
1. **Obsidian Markdown Note (`.md`):** Uses native foldable callouts (`> [!success]-`) for vault-native linking and search.
2. **Standalone Interactive HTML Guide (`.html`):** A zero-dependency, self-contained interactive web document with top study controls (`Reveal All` / `Hide All` / `Print to PDF`), custom dark theme, and mobile-friendly responsive cards.

---

## 🧭 The 5-Phase Production Pipeline

1. **Phase 1: Compute Chart via Astra Engine** (Execute the extraction engine in Astra virtualenv to calculate degrees, signs, Campanus cusps, Jaimini Charakarakas, Lajjitaadi avasthas, Shadbala sub-balas, Ashtakavarga, Vimshottari Dashas, and the Classical Yogas & Yoga Breakers detection suite).
2. **Phase 2: Synthesize with Vedic Astrology Vault** (Map chart findings to house archetypes, dignity rules, yogas, dasha timings, and feeling states using local vault notes).
3. **Phase 3: Generate Obsidian Markdown Note (`.md`)** (Format active-recall modules using native Obsidian folding callouts `> [!success]-`).
4. **Phase 4: Generate Standalone Interactive HTML Guide (`.html`)** (Compile a self-contained web app with `<details>/<summary>`, sticky reveal/hide study controls, and printer stylesheets).
5. **Phase 5: Audit via Independent Critic Subagent** (Invoke an independent critic subagent to verify calculations, clarity, non-fatalism, and citation accuracy).

---

## 🛠️ Phase 1: Precision Astronomical Computation (Astra Engine)

Always compute planetary data, yogas, and time cycles using the local **Astra** platform (`/Users/hajnaljanos/PycharmProjects/astra`).

### 1. Execution Environment
* **Python Executable:** `/Users/hajnaljanos/PycharmProjects/astra/venv/bin/python`
* **Core Calculation Modules:**
  * Chart Computation: `from jyotish.generate_jyotish import generate_kala_chart`
  * Native Profile Loader: `from jyotish import native_manager`
  * Complete App Engine: `from app import compute_chart_data`
  * Classical Yogas Engine: `from jyotish.yogas.evaluator import detect_all_yogas`
* **Data Sources:** Swiss Ephemeris (`swisseph`) with Tropical Rasis, Campanus Bhavas, and Sidereal Equatorial Nakshatras (Dhruva Galactic Center at 246°40' RA).
* **Database:** `/Users/hajnaljanos/PycharmProjects/astra/database/Charts.jsonl` contains saved natives (e.g., Shivapuri, Donald Trump, Angelina Jolie, etc.).

### 2. Comprehensive Automation Script Template
To extract the complete multidimensional data payload, run a Python script following this engine pattern:

```python
import sys
import os
from datetime import datetime
from typing import Dict, Any, List

sys.path.append('/Users/hajnaljanos/PycharmProjects/astra')
from jyotish import native_manager
from jyotish.generate_jyotish import generate_kala_chart
from app import compute_chart_data

CHARTS_FILE = '/Users/hajnaljanos/PycharmProjects/astra/database/Charts.jsonl'

# Option A: Pull existing chart from database
# native = native_manager.get_native_by_id(CHARTS_FILE, "native-uuid-here")
# chart = compute_chart_data(native, d10_mode="reverse", d24_mode="reverse")

# Option B: Compute dynamically from raw parameters
chart = generate_kala_chart(
    name="Subject Name",
    year=1946, month=6, day=14,
    hour=10, minute=54, second=0,
    latitude=40.6833, longitude=-73.8000,
    timezone_offset=-4.0,
    d10_mode="reverse",
    d24_mode="reverse"
)

# 1. Extract Core Vargas
vargas = chart['vargas']
d1 = vargas['D1']
d2 = vargas['D2']   # Hora: Wealth and liquid resources
d9 = vargas['D9']   # Navamsha: Soul purpose & marriage
d10 = vargas['D10'] # Dashamsha: Career platform & status
asc = d1['lagna']

# 2. Calculate 7-Fold Jaimini Charakarakas & Karakamsa
CLASSICAL_7 = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
KARAKA_NAMES = [
    ("Atmakaraka", "AK", "Soul, Self, King of chart"),
    ("Amatyakaraka", "AmK", "Career, Intellect, Minister"),
    ("Bhratrukaraka", "BK", "Guru, Siblings, Mentors"),
    ("Matrukaraka", "MK", "Mother, Home, Emotional foundation"),
    ("Putrakaraka", "PK", "Children, Creative intelligence"),
    ("Gnatikaraka", "GK", "Obstacles, Competitors, Struggle"),
    ("Darakaraka", "DK", "Spouse, Long-term partners")
]

sorted_by_deg = sorted(
    [(p, d1['grahas'][p]['degree_0_to_30']) for p in CLASSICAL_7],
    key=lambda x: x[1],
    reverse=True
)

charakarakas = {}
for idx, (p_name, deg) in enumerate(sorted_by_deg):
    full_name, abbr, meaning = KARAKA_NAMES[idx]
    d9_sign = d9['grahas'][p_name]['sign']
    charakarakas[p_name] = {
        "role": full_name,
        "abbr": abbr,
        "meaning": meaning,
        "degree": deg,
        "d1_sign": d1['grahas'][p_name]['sign'],
        "d9_sign": d9_sign,
        "is_karakamsa": (idx == 0)
    }

ak_planet = sorted_by_deg[0][0]
karakamsa_sign = d9['grahas'][ak_planet]['sign']

# 3. Map Campanus Bhava Chalita Cusp Shifts
planet_to_campanus_bhava = {}
for bhava in d1['bhavas']:
    h_num = bhava['house']
    for p_in_house in bhava['planets']:
        p_clean = "Lagna" if p_in_house == "Asc" else p_in_house
        planet_to_campanus_bhava[p_clean] = h_num

# 4. Extract Detailed Planetary Matrix
ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]
asc_sign_idx = ZODIAC_SIGNS.index(asc['sign'])

planetary_matrix = {}
for p_name in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
    p_data = d1['grahas'][p_name]
    p_sign_idx = ZODIAC_SIGNS.index(p_data['sign'])
    
    whole_sign_house = (p_sign_idx - asc_sign_idx) % 12 + 1
    campanus_house = planet_to_campanus_bhava.get(p_name, whole_sign_house)
    has_cusp_shift = (whole_sign_house != campanus_house)
    av = p_data.get('avasthas', {})
    
    planetary_matrix[p_name] = {
        "sign": p_data['sign'],
        "degree": p_data['degree_0_to_30'],
        "longitude": p_data['longitude'],
        "whole_sign_house": whole_sign_house,
        "campanus_house": campanus_house,
        "has_cusp_shift": has_cusp_shift,
        "nakshatra": p_data.get('nakshatra'),
        "pada": p_data.get('pada'),
        "nakshatra_lord": p_data.get('nakshatra_lord'),
        "sub_lord": p_data.get('sub_lord'),
        "tara": p_data.get('tara'),
        "is_retrograde": p_data.get('is_retrograde', False),
        "is_combust": p_data.get('is_combust', False),
        "speed": p_data.get('speed', 0.0),
        "charakaraka": charakarakas.get(p_name, {}).get("abbr", "--"),
        "final_dignity": p_data.get('dignity_breakdown', {}).get('final_dignity'),
        "avasthas": {
            "lajjitadi": av.get('lajjitadi', []),
            "jagrat": av.get('jagrat', {}).get('state'),
            "bala": av.get('bala', {}).get('state'),
            "deeptadi": av.get('deeptadi', {}).get('state'),
            "shayanadi": av.get('shayanadi', {}).get('state')
        }
    }

# 5. Extract Shadbala Sub-balas & Ishta/Kashta Phala
shadbala_summary = {}
for p in CLASSICAL_7:
    sb = chart['shadbala'][p]
    shadbala_summary[p] = {
        "rank": sb.get("Relative_Rank"),
        "total_virupas": sb.get("Total_Virupas"),
        "total_rupas": sb.get("Total_Rupas"),
        "pct_required": sb.get("Pct_Required_Total"),
        "sthana_bala": sb.get("Sthana_Bala"),
        "dig_bala": sb.get("Dig_Bala"),
        "kaala_bala": sb.get("Kala_Bala"),
        "ayana_bala": sb.get("Ayana_Bala"),
        "cheshta_bala": sb.get("Cheshta_Bala"),
        "drik_bala": sb.get("Drik_Bala"),
        "ishta_phala": sb.get("Ishta_Phala"),
        "kashta_phala": sb.get("Kashta_Phala")
    }

# 6. Extract Classical Yogas & Yoga Breakers (Yoga Bhanga) Suite
yogas_payload = chart.get('yogas', {})
all_yogas = yogas_payload.get('yogas', [])
yogas_summary = yogas_payload.get('summary', {})
# Group yogas by category:
yogas_by_category = {}
for y in all_yogas:
    cat = y['category']
    yogas_by_category.setdefault(cat, []).append(y)

# 7. Extract Ashtakavarga & Vimshottari Timeline
ashtakavarga = {
    "total_sav_by_sign": chart['ashtakavarga']['sav'],
    "shodhya_pindas": chart['ashtakavarga']['shodhya_pindas']
}

dasha_raw = chart['vimshottari_dasha']

def get_dasha_at_date(target_date_str: str) -> Dict[str, Any]:
    target = datetime.strptime(target_date_str, "%Y-%m-%d")
    for ad in dasha_raw['antardashas']:
        s_date = datetime.strptime(ad['start'], "%Y-%m-%d") if 'start' in ad else datetime.strptime(ad['start_date'], "%Y-%m-%d")
        e_date = datetime.strptime(ad['end'], "%Y-%m-%d") if 'end' in ad else datetime.strptime(ad['end_date'], "%Y-%m-%d")
        if s_date <= target <= e_date:
            return {
                "period": ad['period'],
                "mahadasha": ad.get('mahadasha_lord', ad.get('lord')),
                "antardasha": ad.get('antardasha_lord', ad.get('sublord')),
                "start": s_date.strftime("%Y-%m-%d"),
                "end": e_date.strftime("%Y-%m-%d")
            }
    return {}
```

### 3. Required Output Metrics
Every case study must extract and present:
* **Ascendant Point:** Exact sign, degree, minute, Nakshatra, Pada, and Nakshatra Lord.
* **Planetary Matrix:** Sign, degree, Whole Sign House (*Rasi Bhava*), Campanus House (*Bhava Chalita*), Nakshatra, Pada, Retrograde status, Combustion flag, and Jaimini Karaka role.
* **Classical Yogas & Breakers:** Categorized breakdown across Raja Yogas, Dhana Yogas (wealth), Daridrya Yogas (poverty/loss), Pancha Mahapurusha, Lunar/Solar, Parivartana, Viparita Raja Yogas, and Kartari Yogas, with explicit plausibility scores and breaker auditing.
* **Jaimini Charakaraka Table:** Full 7-Karaka breakdown from Atmakaraka (soul King) down to Darakaraka (partner) with degrees and the Navamsha Karakamsa sign.
* **Avastha Profile:** Planetary feeling states from Lajjitaadi (*Mudita*, *Kshobhita*, *Kshudhita*, *Lajjita*) and alertness from Jagratadi (*Jagrat*, *Swapna*, *Sushupti*).
* **Shadbala & Ishta/Kashta Phala:** Total Rupas, percentage of required strength, relative rank (1 through 7), and the sweet/auspicious (*Ishta*) vs difficult (*Kashta*) karmic balance.
* **Vimshottari Dasha Correlation:** Balance at birth and the exact Mahadasha/Antardasha pair active during the native's key life pivot dates.

---

## 📚 Phase 2: Knowledge Synthesis (Vedic Astrology Vault)

Every interpretation must be directly grounded in the repository of wisdom at `/Users/hajnaljanos/PycharmProjects/vedic-astrology-vault/vault/`:
* **Classical Yogas & Life Purpose:**
  * `vault/Ryan Kurczak/Yogas/Lesson 01 - The Yogas in Vedic Astrology.md`
  * `vault/Ryan Kurczak/Yogas/Lesson 02 - Raja Yogas and Finding Purpose in an Astrological Horoscope.md`
  * `vault/Ryan Kurczak/Yogas/Lesson 03 - Jupiter and Venus Yogas in your Horoscope.md`
  * `vault/Ryan Kurczak/Yogas/Lesson 04 - The Best and Worst Planets for Success in Vedic Astrology.md`
* **Wealth & Prosperity Framework (*Dhana vs. Daridrya*):**
  * Dhana Yogas unite the lords of Houses 1 (self), 2 (treasury/savings), 5 (past-life merit/speculation), 9 (fortune/grace), and 11 (massive gains/windfalls).
  * Daridrya Yogas trap wealth lords in Dusthanas (6th debts/litigation, 8th sudden crises/bankruptcy, 12th expenditure/dissolution).
  * Natural wealth indicators: Jupiter (*Dhanakaraka* - growth, treasury, banking) and Venus (*Bhogakaraka* - luxury, vehicles, tangible assets).
  * Cross-reference: `vault/Vimshottari Dasha/Lesson 23 - 11th House - Gains, Wealth and Finances.md` and `vault/The Master Guide to Houses 6 to 12.md`.
* **Lajjitaadi Avasthas:** Planetary emotional conditions and subconscious fulfillment (`vault/Lajjitaadi Avasthas/`).
* **Jaimini Karakas & Atmakaraka:** Soul indicators and career ministry (`vault/Course Lessons/Lesson 39 - AtmaKaraka and Jaimini Karakas in Vedic Astrology.md`).
* **Combustion & Retrogrades:** Physical vs psychological effects (`vault/Course Lessons/Lesson 23 - Combustion and Retrograde Planets in Vedic Astrology.md`).
* **House Meanings:** Consult `[[The Complete Architecture of the 12 Houses]]` and `[[The 12 Houses Master Anatomy & Lifecycle Map]]`.
* **Timing & Cycles:** Cross-reference `[[Course Lessons/Lesson 45 - Dasha in Vedic Astrology]]`, `[[Course Lessons/Lesson 46 - Dasha Predictions in Vedic Astrology]]`, and `[[The Art and Science of Vedic Astrology/Chapter 12 - The Vimshotari Dasha System]]`.
* **Mandatory Rule:** Every module must include at least one verbatim or closely paraphrased source citation with a clickable markdown link.

---

## 📝 Phase 3: Obsidian Markdown Note Specification (`.md`)

Save the Obsidian note in `vault/Case Studies/<Native Name> - Astrological Case Study & Self-Study Guide.md`.

### Callout Syntax for Active Recall:
* **Question / Challenge:** `> [!question] 📝 1. The Challenge`
* **Guided Hints:** `> [!tip] 💡 2. Guided Clues`
* **Collapsible Hidden Solution:** `> [!success]- 👁️ Click to Reveal Solution & Analysis`
  *(Note: The trailing minus `-` is mandatory to keep the callout folded closed until clicked).*

Inside the solution block:
* State the technical astrological mechanics (degrees, houses, dignities, yogas, avasthas, karakas).
* Provide real-world manifestations without fatalism.
* Include the source citation block (`> **Source Citation:** ...`).

---

## 🌐 Phase 4: Standalone Interactive HTML Guide Specification (`.html`)

Save the companion HTML file in `vault/Case Studies/<Native Name> - Astrological Case Study & Self-Study Guide.html`.

### Key Design & Architecture Requirements:
1. **Zero External Dependencies:** Must run 100% offline. No external CDN fonts, scripts, or stylesheets.
2. **Modern Dark Theme UI:** Professional slate palette (background `#0f172a`, cards `#1e293b`, borders `#334155`, text `#f8fafc`, accents `#38bdf8`, `#10b981`, `#f59e0b`, `#f43f5e`).
3. **Sticky Active-Recall Control Bar:**
   ```html
   <div class="action-bar">
     <div>🎯 Active Recall Mode: Test your knowledge before revealing solutions.</div>
     <div class="action-group">
       <button class="btn primary" onclick="toggleAllSolutions(true)">🔓 Reveal All Solutions</button>
       <button class="btn" onclick="toggleAllSolutions(false)">🔒 Hide All Solutions</button>
       <button class="btn" onclick="window.print()">🖨️ Print / PDF</button>
     </div>
   </div>
   ```
4. **Interactive `<details>` / `<summary>` Widgets:**
   * Styled with custom rotating chevron (`▶` rotating to `▼` when `[open]`).
   * Subtle emerald background tint when active.
5. **Print-Ready Stylesheet (`@media print`):**
   * Automatically forces clean white background, black text, and shows all content clearly for paper printing or PDF export.
6. **Toggle Script:**
   ```javascript
   function toggleAllSolutions(open) {
     const detailsElements = document.querySelectorAll('details.solution-block');
     detailsElements.forEach(detail => { detail.open = open; });
   }
   ```

---

## 🕵️ Phase 5: Independent Critic Review Protocol

Never finalize a case study without running it through an independent subagent reviewer.

### Subagent Invocation Specification:
* **Tool:** `invoke_subagent`
* **TypeName:** `research` or `self`
* **Role:** `Astrological & Pedagogical Critic`
* **Prompt Mandates for the Critic:**
  1. **Astronomical Fidelity:** Verify that all degrees, signs, and house placements match the Astra engine output.
  2. **Conceptual Rigor:** Ensure Parashari rules (e.g., Yogakarakas, Kendra-Trikona relationships, Maraka lords, Cusp shifts, Jaimini Karakas, Lajjitaadi feeling states, Classical Yogas & Breakers) are applied correctly.
  3. **Tone & Clarity:** Verify explanations are simple, concise, intuitive (15-year-old learner friendly), and introduce Sanskrit terms with parenthetical definitions.
  4. **Dual Format Verification:** Confirm that both the `.md` (with `> [!success]-`) and `.html` (with `<details>` and study controls) have been generated and match.
  5. **Non-Fatalism Check:** Ensure karmas are framed as tendencies and subconscious impressions (*samskaras*) rather than unchangeable doom.
