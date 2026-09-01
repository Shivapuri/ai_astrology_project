# AI Agent Instructions for Astra Repository

## Project Context
Astra is a precision astrological computation project dedicated to Ernst Wilhelm's "Kala" methodology. 
It utilizes a unified, **Integrated Approach**:
- **Tropical Rasis (Signs)** for all basic placements and Vargas.
- **Campanus House System** for all Bhava calculations.
- **Sidereal Equatorial Nakshatras** anchored to the Dhruva Galactic Center (Middle of Mula).
- **Calculations are powered exclusively by the Swiss Ephemeris (`swisseph`).**

## Core Development Philosophy & Scriptural Integrity (CRITICAL)
- **No Hard-Coding**: You must NEVER hard-code specific values or bypass mathematical formulas to "fake" a good result or make a test pass. Every calculation must be dynamically derived from the Swiss Ephemeris base.
- **Scriptural & Reference Authority**: Never change any core calculation or astrological logic without confirming it aligns with the foundational texts and project references located in `/source-material/software-setup/`.
- **Sources of Truth for Math & Strengths**:
  - `Vedic Astrology An Integrated Approach.pdf`: The core source for Shadbala, Lagna Bala, and Avastha calculations.
  - `Bhava and Graha Balas.pdf`: The absolute source of truth for all planetary and house strengths.
  - **Brihat Parashara Hora Shastra (BPHS)**: (Chapters 41-50) is used as a foundational cross-reference.
- **Rationale & Epistemology**:
  - `The Mystery of the Zodiac.pdf` and `transcript.txt` detail exactly *why* this system uses the Tropical Zodiac, Campanus houses, etc.
- **System Configuration Baseline**:
  - The `/source-material/software-setup/software-parameters/` folder dictates the exact settings that must be adhered to (True Node, Dhruva Galactic Center, etc.).

## Architecture & Math Documentation
- All core chart generation and engine logic resides in the `/jyotish/` directory.
- The project previously used a dual Western/Vedic engine approach; this has been deprecated. Do not recreate the `/western/` folder.
- **Twin Markdown Pattern**: EVERY mathematical module in `/jyotish/` has a strict companion `.md` file that you MUST read before touching the Python code. These files contain the exact logical rules and Sanskrit proofs:
  - `jyotish/generate_jyotish.md` -> Rules for `generate_jyotish.py` (Orchestration, Dashas, Nakshatras, Houses)
  - `jyotish/relationships.md` -> Rules for `relationships.py`
  - `jyotish/shadbala/shadbala.md` -> Rules for `shadbala.py`
  - `jyotish/avasthas/*.md` -> Rules for all Avastha submodules (`bala.py`, `jagrat.py`, etc.)
- Before calculating or guessing astrological logic, always read the corresponding `.md` file and verify against BPHS.

## Reference & Cache
- Ephemeris cache and star data are stored in `/cache/` and `/jyotish/cache/`.
- Astrological reference diagrams, audio transcripts, and Sanskrit texts reside in `/source-material/`.

## UI Development & Verification Protocol (MANDATORY)
- **Visual Verification Loop**: Never make significant UI/Frontend changes blindly. You must always verify your changes visually before reporting back to the user.
- **Automated Screenshots**: You must run the local Flask server, execute the Playwright screenshot script (`screenshot.py`), and use your file viewing tools to physically inspect the screenshot image.
- **Use the Design Subagent**: For major UI/UX overhauls or layout changes, it is mandatory to invoke a specialized "Gemini 3.7" design subagent (using the `pro` model). Delegate the visual iteration loop (edit -> screenshot -> inspect -> refine) completely to this subagent. 
- **Do Not Interrupt**: Do not come back to the user after every small, untested incremental update. Wait until the design subagent has fully verified the UI is polished and unbroken before responding.

## Test-Driven Development & Regression Testing (MANDATORY)
- **Zero Breakage Policy**: You must never introduce a change that silently breaks existing mathematical calculations, API responses, or UI functionality.
- **Write Tests for Changes**: Whenever you make significant structural changes to the `/jyotish/` backend engines, Flask API routes, or the frontend layout, you MUST write or update the corresponding tests in the `/tests/` directory.
- **Run the Suite**: It is STRICTLY MANDATORY after EACH AND EVERY change to run the entire test suite (`pytest tests/`) to guarantee everything is "Green" (passing). Never report back to the user without running the tests first.
- **Test Categories**:
  - `test_math_engines.py` & `test_quantitative_avasthas.py`: Verify that Vargas, Avasthas, and Dignities calculate exactly to established baseline JSON/CSV files.
  - `test_api.py`: Verify that Flask JSON endpoints return 200 OK and expected schemas.
  - `test_svg_generation.py`: Verify that chart SVGs have correct safe margins (`viewBox`), transparent backgrounds, and labels.
  - `test_ui_e2e.py`: Playwright tests to verify the UI layout, Split.js, tabs, and hotkeys.

## Anki Flashcard Strategy & Data Structuring (MANDATORY)
When creating or updating Anki flashcards (especially for broad concepts like Planets, Houses, and Signs), you must **strictly adhere** to the following cognitive rules to avoid cognitive overload and "Anki purgatory":

1. **Atomization (Rule of 4)**: Never put a long list of attributes on a single card. You must consistently break down Planets, Houses, and Signs into **exactly four separate sub-cards** based on their natural astrological categories:
   - **Card 1: Core/Psychological Themes** (What is the primary nature, behavior, or core area of life? e.g., Wealth, delay, aggression, Dharma).
   - **Card 2: Physical/Biological** (What specific body parts, organs, or diseases does this govern? e.g., Head, nerves, immune system).
   - **Card 3: People & Relational** (Which specific family members, societal roles, or relationships are represented? e.g., Mother, enemies, the Guru).
   - **Card 4: Material & Environmental** (What external objects, places, careers, or environments are signified? e.g., Vehicles, foreign lands, dark forests).

2. **No "Reverse" Guessing**: Avoid creating basic "reverse" cards (e.g., *Front: "Which planet is the wise Guru?" Back: "Jupiter"*). These are too easy because the prompt gives away the answer immediately. Testing should always flow from the astrological concept to its specific manifestation (e.g., *Front: "What specific family members and societal roles does Jupiter represent?" Back: "Children, elder brothers, and teachers/counselors"*).

3. **Mnemonic Isolation**: If a mnemonic is used to remember an entity's core pillars, it must be isolated onto its own specific card (e.g., *Front: "What is the mnemonic phrase for Jupiter?"*). Do not bundle it with the other attributes.

