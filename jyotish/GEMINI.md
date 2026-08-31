# ASTRA AI AGENT PROTOCOLS (MANDATORY STRICT GUIDELINES)

You are operating within "Astra", a high-precision Vedic Astrology engine reverse-engineered to match Ernst Wilhelm's Kala software. 

## 1. THE CALCULATION DAG (Directed Acyclic Graph)
You must respect the mathematical hierarchy. Never debug a higher level if a lower level is failing.
*   **Level 1:** Swiss Ephemeris (`swisseph`) Geocentric Longitudes.
*   **Level 2:** Tropical Rasis & Sidereal Equatorial Nakshatras.
*   **Level 3:** Panchadha Sambandha (Relationships) & Drishti (Aspects).
*   **Level 4:** Shadbala (6-fold strength) & Ishta/Kashta Phala.
*   **Level 5:** Qualitative Avasthas (Lajjitadi, Shayanadi).
*   **Level 6:** Quantitative Avasthas (Multiplier Matrices).

## 2. ZERO BREAKAGE & TDD POLICY
*   **NO BYPASSING HOOKS:** You are strictly forbidden from using `git commit --no-verify`. If tests fail, you must fix the code or revert your changes.
*   **Verify against Baselines:** All math changes must be checked against the CSVs in `/source-material/software-setup/sample-case/`.
*   **Run the Audit:** If you touch `shadbala.py` or `quantitative.py`, you MUST run `python scripts/audit_shadbala.py` and report the specific discrepancies before proceeding.

## 3. EPISTEMOLOGY & SOURCES OF TRUTH
*   **Do Not Hallucinate Rules:** Do not apply standard Lahiri or Sri Pati rules. We strictly use Campanus houses, Tropical signs, and exact fractional degrees for Vargas.
*   **The Twin Markdown Pattern:** Before editing *any* `.py` file in `/jyotish/`, you MUST read its corresponding `.md` companion file. The `.md` file contains the exact Sanskrit logic and mathematical formulas you must implement.
*   **If you don't know, Query the DB:** Use `python jyotish/scripture_db.py search <keyword>` to find the exact BPHS sutra if a rule is ambiguous.

## 4. CODE SMELLS & ANTI-PATTERNS TO AVOID
*   **No Hardcoding:** Never hardcode a final Virupa value to make a test pass. Fix the underlying algebra.
*   **DRY (Don't Repeat Yourself):** Do not write custom aspect or dignity logic inside higher-level modules (like Avasthas). Always import and use `jyotish/aspects/aspects.py` and `jyotish/relationships/relationships.py`.

## 5. UI VISUAL VERIFICATION
If you change `templates/index.html` or `draw_chart.py`:
1. Run the Flask server locally.
2. Run `python screenshot.py`.
3. Visually verify the SVG alignment (especially radial stacking in Circular charts, per ADR-006) before concluding your task.
