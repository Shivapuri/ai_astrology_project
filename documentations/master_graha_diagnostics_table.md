# ★ Master Graha Diagnostics: Complete Architecture & Reference Guide

This document explains the mathematical foundations, classical Vedic citations, and diagnostic mechanics of the **Master Graha Diagnostics Table** in the Astra computational engine.

---

## 📍 Documentation Locations

1. **Obsidian Knowledge Vault Guide:**
   - Path: `vault/Lajjitaadi Avasthas/The Master Guide to Lajjitadi Strength Matrices and Planetary Influences.md`
   - Master Progress Tracker: `vault/Lajjitaadi Avasthas - Syllabus & Progress.md`
2. **Astra Codebase Documentation:**
   - Path: `documentations/master_graha_diagnostics_table.md` (this file)

---

## 🧭 Core Architectural Purpose

Students and practitioners often struggle when viewing separate tables for Shadbala, Dignity, Lajjitādi Avasthās, and Aspects:
- *Why does a planet have high Shadbala but feel starved in Lajjitādi Avasthā?*
- *Why does the Moon cast +29 Virūpas of benefic sky-light (Subha Drishti) on Venus, but subtract 268 points in the Lajjitādi Strength Matrix?*
- *How do we see a planet's overall vitality at a glance across all 16 divisional charts (Vargas)?*

The **Master Graha Diagnostics** table consolidates all planetary diagnostics into a single unified matrix.

---

## 📊 Table Anatomy & Column Breakdown

| Column | Metric | Description & Classical Sourcing |
| :--- | :--- | :--- |
| **Graha & Kāraka** | Glyph, Planet & Soul Role | Includes **[R]** (Retrograde) and **[C]** (Combust), plus the 7 **Chara Kārakas** (BPHS Ch. 32): `👑 AK` (Ātmakāraka / Soul), `💼 AmK` (Amātyakāraka / Career), `📿 BK` (Bhrātṛkāraka / Guru), `🏡 MK` (Mātṛkāraka / Home), `🌱 PK` (Putrakāraka / Children), `⚔️ GK` (Jñātikāraka / Obstacles), and `💍 DK` (Dārakāraka / Spouse). For Rahu/Ketu: Chhāyā catalyst. |
| **Placement & Role** | Sign, House & Functional Role | Whole Sign House + 3D Campanus Bhava shift badge. Displays **House Rulerships** (e.g. `Rules: H5, H10`) and functional titles (BPHS Ch. 34): `⭐ Yogakāraka` (simultaneous Kendra + Trikona lord), `🛡️ Lagneśa` (Ascendant lord), `Māraka` (H2/H7), and `Bādhaka`. Displays D1 Nakshatra. |
| **Dignity (5-Fold)** | *Panchadhā Maitrī* | 9 dignities: Exalted, Moolatrikona, Own Sign, Great Friend, Friend, Neutral, Enemy, Great Enemy, Debilitated. For Rahu/Ketu: displays Dispositor reflection (`Reflects: [Lord]`). |
| **Shadbala Power** | 6-Fold Cumulative Strength | Total Rupas, % of required minimum, and relative chart rank (#1 to #7). Baseline soul capacity. |
| **Lajjitādi Avasthās** | Psychological Feeling States | The 6 Parashari states: *Mudita* (Delighted), *Garvita* (Proud), *Kshudhita* (Starved), *Kshobhita* (Agitated), *Lajjita* (Ashamed), *Trushita* (Thirsty), with exact cause tags. |
| **Influences & Net Dṛṣṭi** | Conjunctions & Continuous Aspects | **YUTI:** Conjunct companions. **DRISHTI:** Continuous Virūpas received with explicit `+` (green) and `-` (red) signs. **Net Dṛṣṭi Pill:** `🟢 Net Support`, `🔴 Net Pressure`, or `⚖️ Balanced`. |
| **Karmic Fruit (I/K)** | *Ishta / Kashta Phala* | Innate capacity for sweet blessings (*Ishta*) versus arduous grit (*Kashta*), on a scale of 0 to 60. |
| **★ Vitality Score** | 5-Pillar Composite (1–10) | Weighted synthesis of Sign Dignity, Shadbala, Avasthā Mood, Environmental Weather, and Karmic Fruit. |

---

## 🎛️ Multi-Varga Divisional Chart Support (D1 through D60)

The widget toolbar contains an interactive **Varga selector dropdown**:
- Select any divisional chart: **D1 (Rāśi)**, **D2 (Horā)**, **D3 (Drekkāṇa)**, **D4 (Caturthāṁśa)**, **D7 (Saptāṁśa)**, **D9 (Navāṁśa)**, **D10 (Daśāṁśa)**, up to **D60 (Ṣaṣṭyāṁśa)**.
- When switched, the table dynamically recalculates and renders:
  1. That Varga's Lagna sign and lord.
  2. Each planet's sign, degree, and Whole Sign house (from Varga Lagna).
  3. The 5-fold dignity in that specific Varga.
  4. The qualitative Lajjitādi Avasthās occurring in that specific Varga.
  5. The conjunctions and continuous Graha Drishti aspects (+/- Virūpas) in that specific Varga.
  6. The 5-Pillar Vitality Score tailored to that Varga's dignity and weather.

---

## 🔬 Sourcing & Verification

1. **Textbook & Classical References:**
   - *Brihat Parashara Hora Shastra (BPHS)*: Chapter 32 (*Kārakādhyāya* for Chara Kārakas) and Chapter 34 (*Yogakārakādhyāya* for Functional Benefics, Malefics, and Yogakārakas).
   - *Vedic Astrology: An Integrated Approach* by P.V.R. Narasimha Rao: Chapters 8 and 13.2 (Table 30).
   - *The Art and Science of Vedic Astrology (Vol 1)* by Ryan Kurczak & Richard Fish: Chapters 4, 5, 6, 7, 8, and 16.
   - *Phaladeepika* by Mantreswara: Chapters 3 and 4 (translated by Vic DiCara).
2. **Automated Verification:**
   - Automated UI Suite: `pytest tests/test_new_widgets_ui.py` (15/15 passed).
   - Kala Software Ground-Truth Verification: `python scripts/generate_all_varga_proofs.py` (0 diverging cells across all 16 Vargas).
