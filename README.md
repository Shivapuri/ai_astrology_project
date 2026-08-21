# Astra: Astrological Calculations Core

Astra is a precision astrology calculation repository containing two independent horoscope engines:

1. **Vedic Astrology (Jyotish)**: Sidereal calculations powered by `jyotishganit` and NASA JPL ephemeris (`skyfield`).
2. **Western Astrology (Hellenistic)**: Tropical zodiac calculations and whole sign house mechanics powered by Swiss Ephemeris (`swisseph` / `kerykeion`).

---

## Repository Structure

* [`jyotish/`](file:///Users/hajnaljanos/PycharmProjects/astra/jyotish) - Vedic calculation engine:
  * [`jyotish/generate_jyotish.py`](file:///Users/hajnaljanos/PycharmProjects/astra/jyotish/generate_jyotish.py) - Generates full Parashari chart data (Panchanga, D1 Rasi, D9 Navamsha, Vimshottari Dasha).
  * [`jyotish/bulk_test_jyotish.py`](file:///Users/hajnaljanos/PycharmProjects/astra/jyotish/bulk_test_jyotish.py) - Automated 100-chart stress tester across global coordinates.
  * [`jyotish/jyotish_rules.txt`](file:///Users/hajnaljanos/PycharmProjects/astra/jyotish/jyotish_rules.txt) - Core rules reference for dignities, aspects, and dashas.
* [`western/`](file:///Users/hajnaljanos/PycharmProjects/astra/western) - Western calculation engine:
  * [`western/generate_chart.py`](file:///Users/hajnaljanos/PycharmProjects/astra/western/generate_chart.py) - Western tropical chart generator.
  * [`western/test_accuracy.py`](file:///Users/hajnaljanos/PycharmProjects/astra/western/test_accuracy.py) - Accuracy test suite for degrees, lots, and dignities.
  * [`western/bulk_test_engine.py`](file:///Users/hajnaljanos/PycharmProjects/astra/western/bulk_test_engine.py) - Western engine stress test pipeline.
* [`source-material/`](file:///Users/hajnaljanos/PycharmProjects/astra/source-material) - Astrological diagrams, reference audio, and study resources.
* [`cache/`](file:///Users/hajnaljanos/PycharmProjects/astra/cache) - Astronomical ephemeris files (NASA DE421 ephemeris & Hipparcos star catalog `hip_main.dat`).

---

## Setup & Running

This project uses Python 3.12.

1. Activate virtual environment:
   ```bash
   source venv/bin/activate
   ```

2. Run Vedic chart calculation:
   ```bash
   python jyotish/generate_jyotish.py
   ```

3. Run Western chart accuracy test:
   ```bash
   python western/test_accuracy.py
   ```
