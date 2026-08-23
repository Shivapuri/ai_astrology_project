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
