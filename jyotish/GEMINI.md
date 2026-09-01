# ASTRA AI AGENT PROTOCOLS: STRICT DEVELOPMENT FRAMEWORK

You are operating within "Astra", a high-precision Vedic Astrology engine reverse-engineered to match Ernst Wilhelm's Kala software. 

## 1. THE DEVELOPMENT PIPELINE
You must strictly follow this 4-step pipeline when adding new features or fixing math:
1. **Ground the Logic:** Read the associated `Twin Markdown` (`.md`) file. If the rule is unclear, query the database using `python jyotish/scripture_db.py search <keyword>`.
2. **Write the Math:** Implement the rule in the appropriate Python module. **DO NOT format UI elements (like colors or HTML strings) in the math engines.** Return pure floats/dicts.
3. **Write the Test:** Open the corresponding file in `tests/` and write a Pytest assertion against the baseline CSVs located in `source-material/software-setup/sample-case/`.
4. **Verify:** Run `pytest tests/`. You are forbidden from committing code that breaks the test suite. Never use `@pytest.mark.skip` to hide a failing math test.

## 2. THE CALCULATION DAG (Directed Acyclic Graph)
You must respect the mathematical hierarchy. Never debug a higher level if a lower level is failing.
*   **Level 1:** Swiss Ephemeris (`swisseph`) Base Longitudes & Heliocentric Nodes.
*   **Level 2:** Tropical Rasis & Sidereal Equatorial Nakshatras.
*   **Level 3:** House Cusps (Campanus) & Vargas (Exact Fractional Degrees).
*   **Level 4:** Relationships (Naisargika/Tatkalika) & Drishti (Rasi/Graha).
*   **Level 5:** Shadbala (The 6 Pillars) & Ishta/Subha Phala.
*   **Level 6:** Avasthas (Qualitative States & Quantitative Matrices).

## 3. CODE SMELLS TO AVOID
*   **No "God Objects":** Do not add more calculations to `generate_jyotish.py`. If you build a new engine (e.g., Yogas or Dashas), create a new file in the appropriate subdirectory, write the math there, and simply import the function into the main orchestrator.
*   **No Hardcoding:** Never hardcode a final value (e.g., `if planet == "Sun": return 45.3`) to make a test pass. Fix the underlying algebra.
*   **DRY (Don't Repeat Yourself):** Always reuse the established functions in `aspects.py` and `relationships.py`.

## 4. UI VISUAL VERIFICATION
If you change `templates/index.html` or `draw_chart.py`:
1. Start the Flask server locally.
2. Run `python screenshot.py` (which uses Playwright to capture the UI).
3. Inspect the screenshot to ensure tables don't overflow, SVG text isn't colliding, and colors match the Pergamon palette.
