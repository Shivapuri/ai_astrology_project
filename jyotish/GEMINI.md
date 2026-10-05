# ASTRA AI AGENT PROTOCOLS: STRICT DEVELOPMENT FRAMEWORK

You are operating within "Astra", a high-precision Vedic Astrology engine reverse-engineered to match Ernst Wilhelm's Kala software. 

## 1. THE DEVELOPMENT PIPELINE
You must strictly follow this 4-step pipeline when adding new features or fixing math:
1. **Ground the Logic:** Read the associated `Twin Markdown` (`.md`) file. If the rule is unclear, query the database using `python jyotish/scripture_db.py search <keyword>`.
2. **Write the Math:** Implement the rule in the appropriate Python module. **DO NOT format UI elements (like colors or HTML strings) in the math engines.** Return pure floats/dicts.
3. **Write the Test:** Open the corresponding file in `tests/` and write a Pytest assertion against the baseline CSVs located in `source-material/software-setup/sample-case/`.
4. **Verify:** Run `pytest tests/`. You are forbidden from committing code that breaks the test suite. Never use `@pytest.mark.skip` to hide a failing math test.

## 2. THE TWO-HEMISPHERE ARCHITECTURAL LAW

The codebase is strictly partitioned into two non-overlapping hemispheres:

### HEMISPHERE A: Foundational Calculus (Pure Astrological Facts)
Files:
- `baseline.py`, `baseline_math.py`, `baseline_tables.py`, `calc_utils.py`
- `relationships/relationships.py`
- `aspects/aspects.py`
- `shadbala/shadbala.py`
- `avasthas/bala.py`, `avasthas/jagrat.py`, `avasthas/deepti.py`, `avasthas/lajjita.py`, `avasthas/shayana.py`, `avasthas/quantitative.py`
- `bhavas/bhava_bala.py` (Pure House Bala, Harsha Bala, House Atmosphere)
- `vimshopaka/vimshopaka.py`
- `ashtakavarga/ashtakavarga.py`
- `dashas/vimshottari.py`
- `yogas/*.py` (Classical rule detection & breaker audits)
- `karakas.py` (Chara Karaka rankings, whole-sign functional rulerships)
- `transits/transits.py` (Transit coordinates & planetary aspects)

**Strict Restrictions for Hemisphere A:**
1. **Zero Psychological Archetypes:** Never inject modern behavioral archetypes (e.g., "The Armed Dictator", "The Generous King", "The Toothless Bully") into these files.
2. **Zero Subjective Heuristic Scales:** Never calculate non-classical composite vitality scores (e.g. 1.0 to 10.0 scales) here.
3. **Pure Classical Output:** Return strictly floats, ints, bools, and classical Sanskrit categorical terms (*Uccha*, *Nīca*, *Sva*, *Adhimitra*, *Pāpakartarī*, *Harṣa*, *Virūpas*, *Rūpas*, *Bindus*).
4. **No UI or Reporting Payloads:** Never build table column definitions, HTML markup, color strings, or display badges in these files.
5. **Dependency Invariance:** Hemisphere A must NEVER import, call, or depend on Hemisphere B (`planetary_evaluation` or `report`).

---

### HEMISPHERE B: Interpretive Synthesis & Diagnostics (Counseling Layer)
Files:
- `planetary_evaluation/planetary_evaluation.py`
- `planetary_evaluation/lagna_evaluation.py`
- `report/interpretation_engine.py`
- `report/report_engine.py`
- `report/prominence.py`
- `report/varga_environment.py`

**Scope & Permissions for Hemisphere B:**
1. This layer is permitted to synthesize raw calculus into psychological models, behavioral archetypes (ADR-001 through ADR-010), 1–10 vitality scores, and narrative reports.
2. It ingests Hemisphere A data as read-only inputs.
3. It must NEVER modify or overwrite the underlying mathematical calculations (e.g., an archetype must never alter a planet's actual Shadbala or Shadvarga score).

---

## 3. THE REVISED CALCULATION DAG

You must respect the mathematical hierarchy. Never import or calculate a higher level within a lower level.
* **Level 1 (Astronomy):** Swiss Ephemeris (`swisseph`) Base Longitudes, 3D Declinations, Julian Day UTC (`baseline.py`).
* **Level 2 (Zodiac & Stars):** Tropical Rasis, Sidereal Equatorial Nakshatras, Upagrahas, Core Sphutas (`baseline.py`, `baseline_math.py`).
* **Level 3 (Divisions & Houses):** 16 Divisional Vargas, Campanus Cusps, Whole Sign Houses (`baseline.py`, `baseline_math.py`).
* **Level 4 (Interactions):** Dignities (Panchadha Maitri), Graha Drishti (0-60 Virupas), Rasi Drishti (`relationships.py`, `aspects.py`).
* **Level 5 (Planetary Strengths):** Shadbala (6 Pillars), Ishta/Kashta Phala, Saptavarga Bala, Classical Avasthas, Vimshopaka, Ashtakavarga (`shadbala.py`, `avasthas/`, `vimshopaka/`, `ashtakavarga/`).
* **Level 6 (House & Timing Calculus):** Bhava Bala, Harsha Bala, House Atmosphere, Vimshottari Timeline, Classical Yogas, Transits (`bhavas/bhava_bala.py`, `dashas/`, `yogas/`, `transits/`).
* **Level 7 (Evaluative Synthesis - Hemisphere B):** Prominence Ranking, Macro Environment, 9-Tier Behavioral Archetypes, 1–10 Vitality Scores, 5-Pillar Decomposition (`planetary_evaluation/`, `report/`).
* **Level 8 (Presentation & Delivery):** Visual SVG Charts (`draw_chart.py`), PDF Dossiers (`pdf_exporter.py`), Web Templates.

---

## 4. CODE SMELLS TO AVOID
*   **No "God Objects":** Do not add more calculations to `generate_jyotish.py`. If you build a new engine (e.g., Yogas or Dashas), create a new file in the appropriate subdirectory, write the math there, and simply import the function into the main orchestrator.
*   **No Hardcoding:** Never hardcode a final value (e.g., `if planet == "Sun": return 45.3`) to make a test pass. Fix the underlying algebra.
*   **DRY (Don't Repeat Yourself):** Always reuse the established functions in `aspects.py` and `relationships.py`.

## 5. UI VISUAL VERIFICATION
If you change `templates/index.html` or `draw_chart.py`:
1. Start the Flask server locally.
2. Run `python screenshot.py` (which uses Playwright to capture the UI).
3. Inspect the screenshot to ensure tables don't overflow, SVG text isn't colliding, and colors match the Pergamon palette.
