# PDF Exporter Engine (`jyotish/pdf_exporter.py`)

## Purpose & Architectural Role
The `pdf_exporter` module generates publication-grade astrological reports, dossier manuals, and master plans for offline analysis. It formats astronomical chart SVGs and comprehensive diagnostic tables into print-optimized HTML rendered to vector-sharp PDF using headless Chromium (via Playwright).

## Core Design Principles
1. **Ernst Wilhelm "Kala" Integrated Methodology**:
   - **Tropical Rasis (Signs)** for all basic placements and divisional Vargas.
   - **Campanus House System** for all Bhava calculations and cusps.
   - **Sidereal Equatorial Nakshatras** anchored to the Dhruva Galactic Center (Middle of Mula).
   - Dynamic ephemeris computation with zero hard-coding.

2. **Horizontal (Landscape) Mastery & Long-Table Optimization**:
   - Defaults to **A4 or A3 horizontal (landscape)** so that 9-column evaluation tables and dual chart cards fit comfortably without cramped text wrapping or horizontal clipping.

3. **Master Dossier Multi-Page Structure**:
   - **Page 1: D1 Rāśi Master Architecture & Core Astronomy**:
     - Column 1: D1 Rāśi Chart SVG (North, South, or Circular) + Campanus Bhava Chalita Cusps (12 houses with cusp degrees, lords, and occupant planets).
     - Column 2: Planetary Placements & Nakshatras (degrees, motion, pada, ruler, whole-sign and Campanus bhava) + Pañcadhā Sambandha 5-Fold Compound Dignities + Vimśottarī Daśā Major Cycles.
   - **Page 2: Harmonic Bi-Wheel Architecture (D1 Root + D9 Soul Navāṃśa)**:
     - Concentric dual-wheel vector SVG (D1 physical reality inner wheel, D9 soul trajectory outer wheel).
     - Cross-Varga Harmonic Alignment Matrix (Natal placement, divisional degree, sector slice/pada, whole-sign overlay bhava, dignity badge).
     - Subtle Soul Destiny & Vargottama Fortification Synthesis.
   - **Page 3: Master Graha Diagnostics • D1 Rāśi (Root Vitality)**:
     - Executive 5-Pillar Horizon Vitality Card.
     - 9-Column Master Graha Diagnostics Table (including Column 7: **Subconscious Drive Nakshatra**).
   - **Page 4: Master Graha Diagnostics • D9 Navāṃśa (Soul Trajectory & Swāṃśa)**:
     - Swāṃśa (D9 Navāṃśa Lagna) & Soul Purpose Architecture Card.
     - 9-Column Master Graha Diagnostics Table for D9.
   - **Page 5: Master Graha Diagnostics • D10 Daśāṃśa (Career, Status & Executive Karma)**:
     - Daśāṃśa Lagna & Professional Authority Executive Card.
     - 9-Column Master Graha Diagnostics Table for D10.
   - **Pages 6+: Divisional Architecture (Vargas) • Dual North & South Indian Charts Side-by-Side**:
     - Paired dual cards presenting North Indian (Diamond / BPHS) and South Indian (Fixed Square) charts side-by-side with 5-column placement tables and deep domain diagnostics for:
       - **D10 Daśāṃśa** (Career & Status) & **D7 Saptāṃśa** (Progeny & Partnerships)
       - **D2 Horā** (Wealth & Resources) & **D3 Drekkāṇa** (Courage & Siblings)
       - **D4 Caturthāṃśa** (Fixed Assets & Home) & **D12 Dvādaśāṃśa** (Ancestry & Lineage)
       - **D30 Triṃśāṃśa** (Arishta & Adversity) & **D60 Ṣaṣṭyāṃśa** (Root Karmic Blueprint)
   - **Page: 16-Varga Viṃśopaka Strength & Dignity Matrix**:
     - All 9 Grahas (including Rāhu and Ketu) evaluated across all 16 divisional charts (D1 to D60).
     - Color-coded cells: Exalted (`Ex`), Moolatrikona (`MT`), Own (`Sva`), Great Friend (`GF`), Friend (`F`), Neutral (`N`), Enemy (`E`), Great Enemy (`GE`), Debilitated (`Deb`).
     - **Dignified / Afflicted Counts**: Exact count of auspicious vs. inauspicious vargas.
     - 20-point Parāśari Viṃśopaka Score.
     - **Vaiśeṣikāṃśa Honorific Classifications** (Bhedaka, Vyañjana, Cāmara, Chatra, Kuṇḍala, Mukuta, Sārthakā) with classical meanings.
   - **Page: Vimśottarī Daśā 120-Year Parāśari Chronological Timeline**:
     - Birth Mahādaśā balance (Years, Months, Days).
     - Active Mahādaśā spotlight card.
     - Chronological 120-year timeline table covering all 9 major cycles with completed/active/future badges.
     - Complete 9 Antardaśā sub-periods schedule for the active Mahādaśā with `★ CURRENT` sub-period indicator.
     - Daśā Manifestation Dynamics pedagogical note.
   - **Page: Deep Planetary Strengths & Potencies**:
     - 4-Tier Qualitative & Lajjitādi Avasthās Grid (Bālādi, Jāgradādi, Dīptādi, Lajjitādi).
     - Strengths Matrix • Kala Yoga Judgment (Ishta/Kashta, Subha/Asubha, Subha/Asubha Dig Bala).
     - Ṣaḍbala Strength Breakdown Grid (Parāśara 6-fold virūpas, benchmarks, relative rank #1–#7).
   - **Page: Classical Yogas & Yoga Bhanga Plausibility Audit**:
     - 9 Classical Parāśari Yoga categories.
     - Trishādaya intrusion audit & 6-fold Nīca Bhaṅga redemption analysis.
   - **Page: Master Astrological Diagnostic Key & Pedagogical Reference Guide**:
     - 10 Educational cards decoding all badges, feeling states, and **Subconscious Drive Nakshatras** in plain English.

4. **Kala Warm Parchment Visual Identity**:
   - Palette matches Kala software UI: warm cream headers (`#eee5d3`), dark walnut text (`#4a3325`), sand borders (`#dcb594`, `#e5dccb`), crisp white cells (`#fffdfa`), and soft parchment accents (`#fcfaf5`).
