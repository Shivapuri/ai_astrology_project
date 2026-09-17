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

## 📊 Table Anatomy & Column Breakdown (8-Column Unified Matrix)

| Column | Metric | Description & Classical Sourcing |
| :--- | :--- | :--- |
| **1. Graha & Soul** | Glyph, Planet & Soul Role | Includes **[R]** (Retrograde / *Vakra*) and **[C]** (Combust / *Asta*), plus the 7 **Chara Kārakas** (BPHS Ch. 32): `👑 AK` (Ātmakāraka / Soul), `💼 AmK` (Amātyakāraka / Career), `📿 BK` (Bhrātṛkāraka / Guru), `🏡 MK` (Mātṛkāraka / Home), `🌱 PK` (Putrakāraka / Children), `⚔️ GK` (Jñātikāraka / Obstacles), and `💍 DK` (Dārakāraka / Spouse). For Rahu/Ketu: Chhāyā catalyst. |
| **2. Placement & Role** | Sign, House & Functional Role | Whole Sign House + 3D Campanus Bhava shift badge. Displays **House Rulerships** (e.g. `Rules: H5, H10`) and functional titles (BPHS Ch. 34): `⭐ Yogakāraka` (simultaneous Kendra + Trikona lord), `🛡️ Lagneśa` (Ascendant lord), `Māraka` (H2/H7), and `Bādhaka`. Displays D1 Nakshatra & Pada. |
| **3. Essential Dign.** | *Panchadhā Maitrī* (5-Fold Dignity) | 9 classical dignities: Exalted (*Uccha*), Moolatrikona, Own Sign (*Svastha*), Great Friend (*Adhi Mitra*), Friend (*Mitra*), Neutral (*Sama*), Enemy (*Shatru*), Great Enemy (*Adhi Shatru*), Debilitated (*Neecha*). Shows % dignity score. For Rahu/Ketu: displays Dispositor proxy reflection (`Proxy ([Lord])`). |
| **4. Host Dispositor** | Bedrock Foundation & Rescue | The planetary ruler governing the sign where the planet sits. Evaluates host essential dignity % and host Shadbala muscle %. Determines **Neecha Bhanga** (cancellation of debility) alchemical rescue: `🏡 Self-Hosted`, `🛡️ Fortified Host`, `✨ Rescued (Neecha Bhanga)`, `⚠️ Strained Host`, or `⚖️ Neutral Host`. |
| **5. Shadbala Power** | 6-Fold Cumulative Potency (*Virūpas*) | Total Virūpas / Rūpas, % of required minimum threshold, and relative chart rank (#1 to #7). Displays capacity descriptor (*Abundant*, *Capable*, *Deficit*) and Parashari karmic harvest balance (*Ishta* & *Kashta Phala*). For Rahu/Ketu: inherits proxy muscle via host dispositor. |
| **6. Aspect Weather** | Conjunctions & Continuous Rays | **YUTI:** Conjunct companions. **DRISHTI:** Continuous Virūpas received with explicit `+` (green benefic) and `-` (red malefic) signs. **Net Dṛṣṭi Pill:** `🟢 Net Support (+Xv)`, `🔴 Net Pressure (-Xv)`, or `⚖️ Net Neutral`. |
| **7. Avastha & Age** | Biological Age & Psychological Mood | **Bālādi Avasthās** (*Phaladeepika* 3.10 with odd/even sign inversion): Biological age cycle (*Bala* infant 50%, *Kumara* youth 75%, *Taruna* prime 100%, *Pravaya* elder 50%, *Mrita* dormant 25%). Plus the 6 Parashari **Lajjitādi feeling states** (BPHS Ch. 45): *Mudita*, *Garvita*, *Kshudhita*, *Kshobhita*, *Lajjita*, *Trushita*. |
| **8. ★ Functional Archetype** | 4-Quadrant Matrix & Vitality Score | Vic DiCara's 4-Quadrant Behavioral Matrix: `🌟 Generous King` (High Quality + High Muscle), `🤝 Sincere Friend` (High Quality + Low Muscle), `⛓️ Toothless Bully` (Low Quality + Low Muscle), or `⚔️ Armed Dictator` (Low Quality + High Muscle). Displays calibrated Net Functional Vitality Score (1.0 to 10.0) and tier title. |

---

## 🎛️ Multi-Varga Divisional Chart Support (D1 through D60)

The widget toolbar contains an interactive **Varga selector dropdown**:
- Select any divisional chart: **D1 (Rāśi)**, **D2 (Horā)**, **D3 (Drekkāṇa)**, **D4 (Caturthāṁśa)**, **D7 (Saptāṁśa)**, **D9 (Navāṁśa)**, **D10 (Daśāṁśa)**, up to **D60 (Ṣaṣṭyāṁśa)**.
- When switched, the table dynamically recalculates and renders:
  1. That Varga's Lagna sign, lord, and lord's host foundation.
  2. Each planet's sign, degree, and Whole Sign house (from Varga Lagna).
  3. The 5-fold dignity in that specific Varga.
  4. The Host Dispositor metrics and rescue status.
  5. The biological Bālādi Avasthā and qualitative Lajjitādi Avasthās occurring in that specific Varga.
  6. The conjunctions and continuous Graha Drishti aspects (+/- Virūpas) in that specific Varga.
  7. The 4-Quadrant Behavioral Archetype and calibrated Vitality Score tailored to that Varga.

---

## 💡 Interactive Hover Tooltips (Pedagogical Guidance)

Every element across the Master Graha Diagnostics table is equipped with instant, learner-friendly hover tooltips. Technical astrological terminology is always paired with intuitive explanations and definitions in parentheses:

1. **Table Headers (Column Guides):**
   - Hovering any column header reveals its diagnostic definition, classical measurement units (e.g. Virūpas), and role in chart evaluation.
2. **Graha & Soul:**
   - **Planet Name:** Explains the graha's core archetype and psychological drive.
   - **Motional Status Badges:** `[R]` explains Retrograde (*Vakra*) motion (optical proximity to Earth, maximum motional power / Cheṣṭa Bala, non-linear unconventional thinking). `[C]` explains Combustion (*Asta*) (proximity within solar orb, humility, internalizing self-worth).
   - **Chara Kārakas:** Explains the soul role (e.g., `👑 AK` Ātmakāraka, `💼 AmK` Amātyakāraka), traverse degree, rank, and developmental life focus.
3. **Placement & Role:**
   - **Sign & Degrees:** Element, modality, and host sign lord (*dispositor*).
   - **Whole Sign House:** Functional sphere of activity.
   - **Campanus 3D Bhava Shift:** Explains when astronomical cusps diverge from whole-sign houses (outer social circumstances vs. inner psychological experience).
   - **House Rulerships & Functional Badges:** Details domains managed, including `⭐ Yogakāraka`, `🛡️ Lagneśa`, `Māraka`, and `Bādhaka`.
   - **Nakshatra:** Lunar mansion and Navāṁśa pada mapping.
4. **Essential Dignity (5-Fold Compound / *Panchadhā Maitrī*):**
   - Explains the complete derivation: **Sign Lord host** + **Natural Relationship** (*Naisargika*) + **Temporary Relationship** (*Tātkālika*, based on 2, 3, 4, 10, 11, 12 house distance) = **5-Fold Compound Dignity** (*Panchadhā*).
   - Details peak states: Exalted (*Uccha*), Moolatrikona (office of duty), Own Sign (*Svastha*), or Debilitated (*Neecha*).
   - For Rahu & Ketu: Explains why mathematical shadow nodes (*Chhāyā Grahas*) do not take direct 5-fold dignity and details their dispositor proxy reflection.
5. **Host Dispositor (Bedrock Foundation & Rescue):**
   - Details the host planet governing the sign, its essential dignity %, and its Shadbala stamina %.
   - Explains **Neecha Bhanga** alchemical rescue: when a debilitated planet is hosted by an exalted or dignified planet with high muscle, the fallen nature is transmuted into extraordinary grit, humility, and mastery.
6. **Shadbala Power (6-Fold Potency):**
   - **Total Virūpas & Rūpas:** Compares total points against classical minimum requirements (e.g. 390 Virūpas for the Sun).
   - **Chart Ranking:** Identifies the planet's rank (#1 through #7) among physical grahas.
   - **Capacity Assessment:** Categorizes engine stamina as *Abundant Surplus* (≥125%), *Adequate & Capable* (≥100%), *Mild Deficit* (85–99%), or *Significant Deficit* (<85%).
   - **Karmic Fruits (*Ishta* & *Kashta Phala*):** Clarifies *Ishta Phala* (sweet harvest) vs. *Kashta Phala* (arduous character-building trials).
7. **Aspect Weather & Net Dṛṣṭi:**
   - Breaks down conjunction companions (*Yuti*) and aspect rays (*Graha Drishti*) with positive (+) and negative (-) Virūpa values and net environmental weather.
8. **Avastha & Age:**
   - **Bālādi Avasthās:** Explains the biological maturity stage based on degree progression in odd vs. even signs (Infant *Bala*, Youth *Kumara*, Adult *Taruna*, Elder *Pravaya*, Incapacitated *Mrita*).
   - **Lajjitādi Avasthās:** Explains emotional feeling states (*Mudita* delighted, *Garvita* proud, *Kshudhita* starved, *Kshobhita* agitated, *Lajjita* ashamed, *Trushita* thirsty).
9. **★ Functional Archetype & Vitality Score:**
   - **4-Quadrant Behavioral Matrix (Vic DiCara):**
     - `🌟 Generous King` (High Quality + High Muscle): Noble character with vast resources to execute good.
     - `🤝 Sincere Friend` (High Quality + Low Muscle): Pure intentions, but lacks executive horsepower.
     - `⛓️ Toothless Bully` (Low Quality + Low Muscle): Agitated or corrupt intent, but harmless because it lacks kinetic force.
     - `⚔️ Armed Dictator` (Low Quality + High Muscle): Corrupt intent armed with devastating kinetic weaponry.
   - **Calibrated Vitality Score (1.0–10.0):** Synthesizes moral quality, physical muscle, host foundation, biological efficiency, and aspect weather without false equivalence.

---

## 🔬 Sourcing & Verification

1. **Textbook & Classical References:**
   - *Brihat Parashara Hora Shastra (BPHS)*: Chapter 32 (*Kārakādhyāya* for Chara Kārakas), Chapter 34 (*Yogakārakādhyāya* for Functional Benefics, Malefics, and Yogakārakas), and Chapter 45 (*Lajjitādyavasthādhyāya* for the 6 feeling states).
   - *Phaladeepika* by Mantreswara: Chapter 3, Verse 10 (Bālādi Avasthās with odd/even sign reversal).
   - *Vic DiCara's Planetary Evaluation Rule Book*: 4-Quadrant Behavioral Matrix (Quality vs. Muscle) and Dispositor Foundation dynamics.
   - *Vedic Astrology: An Integrated Approach* by P.V.R. Narasimha Rao: Chapters 8 and 13.2 (Table 30).
   - *The Art and Science of Vedic Astrology (Vol 1)* by Ryan Kurczak & Richard Fish: Chapters 4, 5, 6, 7, 8, and 16.
2. **Automated Verification:**
   - Automated UI Suite: `pytest tests/test_new_widgets_ui.py` (15/15 passed).
   - Backend Evaluation Engine: `pytest tests/test_planetary_evaluation.py` (5/5 passed).
   - PDF Exporter Matrix: `pytest tests/test_export_pdf.py` (7/7 passed).

