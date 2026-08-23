# Astra Astrological Engine

Astra is a precision astrological computation and visualization platform dedicated to Ernst Wilhelm's "Kala" methodology.

## Core Methodology
- **Tropical Rasis (Signs)** for all basic placements and all 16 Divisional Charts (Shodashavargas: D1 through D60).
- **Sidereal Equatorial Nakshatras** anchored to the Dhruva Galactic Center (Middle of Mula).
- **Campanus House System** used for all Bhava Chalita calculations, properly supporting high-latitude intercepted signs.
- **Panchadha Sambandha** (5-fold relationship) and classical **Baladi** & **Jagradadi Avasthas**.
- Powered exclusively by the Swiss Ephemeris (`swisseph`).

## Architecture & Calculation Engines
- **`/jyotish/`**: Core modular calculation engines.
  - `generate_jyotish.py`: Master orchestrator, Julian day conversions, all 16 Varga algorithms (`calculate_varga_longitude`), Campanus house cusps, and Bhava Chalita bounds.
  - `avasthas/bala.py`: Baladi Avastha engine (5-stage physical vitality based on odd/even sign degree brackets).
  - `avasthas/jagrat.py`: Jagradadi Avastha engine (3-stage consciousness/alertness based on natural dignity).
  - `relationships.py`: Panchadha Sambandha (Natural + Temporary = Compound planetary friendships and dignities).
  - `calc_utils.py`: Interpolated node and Dhruva Galactic Center Ayanamsa calculations.
  - `draw_chart.py`: Responsive SVG generation for South Indian, North Indian, and Bhava Chalita charts.
  - `native_manager.py`: Atomic JSONL database management for saved charts.
  - `bphs_db.py` & `scripture_db.py`: Brihat Parashara Hora Shastra and classical scripture databases.
- **`app.py`**: Flask web server providing the API and frontend UI.
- **`templates/index.html`**: Full-width Split.js dashboard featuring resizable chart/info panes, native top toolbar, Pergamon color palette, and keyboard hotkeys (`S`, `N`, `C`).

## Running the Application
1. Activate your virtual environment: `source venv/bin/activate`
2. Start the Flask server: `python app.py`
3. Open your browser to `http://localhost:5001`

## UI Verification Protocol
Astra mandates visual verification via Playwright screenshots before finalizing any UI updates. See [`GEMINI.md`](GEMINI.md) for full developer protocols.

## Documentation
- **[System & UI Blueprint](documentations/BLUEPRINT.md)**: Architectural roadmap, UI interaction pipeline, and circular chart specifications.
- **[Vargas Functioning & Calculation Guide](documentations/vargas_functioning.md)**: Detailed technical reference on algorithms, rules, degree scaling, and cusp projection for all 16 Shodashavarga charts.
- **[Architecture Decision Records (ADRs)](documentations/adr/)**: Architectural rationale covering House Systems (ADR 001), Nakshatras (ADR 002), Intercepted Signs (ADR 003), Engine Unification (ADR 004), and Vargas Functioning (ADR 005).
