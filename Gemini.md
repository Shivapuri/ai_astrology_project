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
