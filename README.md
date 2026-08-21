# Astra Astrological Engine

Astra is a precision astrological computation project dedicated to Ernst Wilhelm's "Kala" methodology.

## Core Methodology
- **Tropical Rasis (Signs)** for all basic placements and 16 Divisional Charts (Vargas).
- **Sidereal Equatorial Nakshatras** anchored to the Dhruva Galactic Center (Middle of Mula).
- **Campanus House System** used for all Bhava Chalita calculations, properly supporting high-latitude intercepted signs.
- Powered exclusively by the Swiss Ephemeris (`swisseph`).

## Architecture
- **`/jyotish/`**: Contains the unified calculation engine.
  - `generate_jyotish.py`: Core math, Julian day conversion, Varga harmonic multiplication, and Bhava bounds.
  - `calc_utils.py`: Interpolated node and Ayanamsa utilities.
  - `draw_chart.py`: SVG generation for South Indian, North Indian, and Bhava Chalita visual charts.
  - `native_manager.py`: JSONL database management for charts.
- **`app.py`**: Flask web server providing the API and frontend UI.
- **`documentations/adr/`**: Architecture Decision Records detailing edge cases, trade-offs, and design choices.

## Running the Application
1. Activate your virtual environment: `source venv/bin/activate`
2. Start the Flask server: `python app.py`
3. Open your browser to `http://localhost:5000`

## Documentation
- **[Vargas Functioning & Calculation Guide](documentations/vargas_functioning.md)**: Detailed technical reference on algorithms, rules, degree scaling, and cusp projection for all 16 Shodashavarga charts.
- **[Architecture Decision Records (ADRs)](documentations/adr/)**: Architectural rationale covering House Systems (ADR 001), Nakshatras (ADR 002), Intercepted Signs (ADR 003), Engine Unification (ADR 004), and Vargas Functioning (ADR 005).

