# PDF Exporter Engine (`jyotish/pdf_exporter.py`)

## Purpose & Architectural Role
The `pdf_exporter` module generates publication-grade astrological reports and plans for offline analysis. It formats astronomical chart SVGs and comprehensive diagnostic tables into print-optimized HTML rendered to vector-sharp PDF using headless Chromium (via Playwright).

## Core Design Principles
1. **Ernst Wilhelm "Kala" Integrated Methodology**:
   - **Tropical Rasis (Signs)** for all basic placements and divisional Vargas.
   - **Campanus House System** for all Bhava calculations and cusps.
   - **Sidereal Equatorial Nakshatras** anchored to the Dhruva Galactic Center (Middle of Mula).
   - Dynamic ephemeris computation with zero hard-coding.
2. **Naturally Clustered Visual Hierarchy**:
    - **Page 1: D1 Rāśi Master Diagnostic Hub (3 Balanced Columns)**:
      - **Column 1 (~330px)**:
        - D1 Rāśi Chart (vector SVG in North, South, or Circular style).
        - Campanus Bhava Chalita Cusps (12 houses with cusp degrees, lords, and occupant planets).
        - Vimśottarī Daśā Major Cycles (120-year Parashari cycle with active period badge).
      - **Column 2 (~1.25fr)**:
        - Planetary Placements & Nakshatras (Degrees, motion, sidereal Nakshatra pada, ruler, and Campanus house).
        - Pañcadhā Sambandha (5-Fold Compound Dignities: Natural + Temporal Maitri).
        - **Unified Qualitative & Lajjitādi Avasthās Grid**: Matches the software's `tmpl-avasthas-calc` format (rows: Bālādi, Jāgradādi, Dīptādi, Lajjitādi; columns: 7 classical planets), eliminating duplication.
        - **Strengths Matrix • Yoga Judgment**: Matches the software's `tmpl-yoga-judgment` format (Ishta/Kashta, Subha/Asubha, Subha/Asubha Dig Bala with compound impacts, Uccha/Cheṣṭā balas, and an average column, styled with a distinct warm brown border and green/red values).
      - **Column 3 (~1.45fr)**:
        - **Ṣaḍbala Strength Breakdown Grid**: Comprehensive 25-row Parashara breakdown matching `.shadbala-breakdown-grid` from the software, covering Sthāna Bala (Uccha, Saptavargaja, Ojhayugmarasyamsa, Kendrādi, Drekkāṇa), Dig Bala, Kāla Bala (Natonnata, Pakṣa, Tribhāga, Varṣa, Māsa, Dina, Horā), Ayana Bala, Cheṣṭā Bala, Other Balas (Naisargika, Dṛk, Yuddha), and Summary & Rankings (Total Virūpas, Total Rūpas, Parashara sufficiency benchmarks, and relative rank #1–#7).
    - **Page 2: Divisional Architecture (Vargas)**:
      - Modular cards pairing each Divisional Chart with its specific placements and key indicators:
        - **D9 Navāṃśa**: Soul destiny, Dharma, Swāṃśa, Kārakāṃśa, and Vargottama planets.
        - **D10 Daśāṃśa**: Career, public status, 10th house lord, and Kendra occupants.
        - **D7 Saptāṃśa**: Progeny, creative output, 5th and 7th house dynamics.
      - **16-Varga Viṃśopaka Dignity Matrix**: 20-point dignity scoring across all 16 divisional charts with Vaiśeṣikāṃśa honorific classifications.
3. **Kala Warm Parchment Visual Identity**:
   - Palette strictly matches Kala UI: warm cream headers (`#eee5d3`), dark walnut text (`#4a3325`), sand borders (`#dcb594`, `#e5dccb`), crisp white cells (`#fffdfa`), and soft parchment row headers (`#fcfaf5`).
4. **Format Support**:
   - **A3 Landscape (Default Master Plan)**: Generous 420mm × 297mm canvas providing high density with zero page overflow across 2 strict master pages.
   - **A4 Portrait / Multi-Page Dossier**: Optimized for standard desktop document printers.
   - **Current View / Browser Print Preview**: Instant interactive preview in the browser with print stylesheet support.
