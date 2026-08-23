# AI Agent Instructions for Astra Repository

## Project Context
Astra is a precision astrological computation project dedicated to Ernst Wilhelm's "Kala" methodology. 
It utilizes a unified, hybrid astronomical approach:
- **Tropical Rasis (Signs)** for all basic placements and Vargas.
- **Sidereal Equatorial Nakshatras** anchored to the Dhruva Galactic Center (Middle of Mula).
- Calculations are powered exclusively by the Swiss Ephemeris (`swisseph`).

## Architecture
- All core chart generation and engine logic resides in the `/jyotish/` directory.
- The project previously used a dual Western/Vedic engine approach; this has been deprecated. Do not recreate the `/western/` folder.

## Reference & Cache
- Ephemeris cache and star data are stored in `/cache/` and `/jyotish/cache/`.
- Astrological reference diagrams, audio transcripts, and study materials reside in `/source-material/`.

## UI Development & Verification Protocol (MANDATORY)
- **Visual Verification Loop**: Never make significant UI/Frontend changes blindly. You must always verify your changes visually before reporting back to the user.
- **Automated Screenshots**: You must run the local Flask server, execute the Playwright screenshot script (`screenshot.py`), and use your file viewing tools to physically inspect the screenshot image.
- **Use the Design Subagent**: For major UI/UX overhauls or layout changes, it is mandatory to invoke a specialized "Gemini 3.7" design subagent (using the `pro` model). Delegate the visual iteration loop (edit -> screenshot -> inspect -> refine) completely to this subagent. 
- **Do Not Interrupt**: Do not come back to the user after every small, untested incremental update. Wait until the design subagent has fully verified the UI is polished and unbroken before responding.

## Test-Driven Development & Regression Testing (MANDATORY)
- **Zero Breakage Policy**: You must never introduce a change that silently breaks existing mathematical calculations, API responses, or UI functionality.
- **Write Tests for Changes**: Whenever you make significant structural changes to the `/jyotish/` backend engines, Flask API routes, or the frontend layout, you MUST write or update the corresponding tests in the `/tests/` directory.
- **Run the Suite**: Before reporting back to the user after a major modification, run the entire test suite (`pytest tests/`) to guarantee everything is "Green" (passing).
- **Test Categories**:
  - `test_math_engines.py`: Verify that Vargas, Avasthas, and Dignities calculate exactly to established baselines.
  - `test_api.py`: Verify that Flask JSON endpoints return 200 OK and expected schemas.
  - `test_svg_generation.py`: Verify that chart SVGs have correct safe margins (`viewBox`), transparent backgrounds, and labels.
  - `test_ui_e2e.py`: Playwright tests to verify the UI layout, Split.js, tabs, and hotkeys.
