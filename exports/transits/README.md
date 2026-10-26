# Astra Transit Engine (Gochara System) Export Guide

Welcome to the **Astra Transit System** export bundle. This package contains all the essential files needed to understand, calculate, and visually display astrological transits (*Gochara*—the real-time movement of planets through the sky relative to a birth chart).

---

## 1. What is a Transit? (The Simple Intuition)

Think of a natal birth chart as the **architectural blueprint of a house**. It never changes. 
A **transit** (*Gochara*, meaning "planetary movement" or "cow pasture path") is like the **daily weather** moving across that house. When a storm or bright sunshine passes directly over a sensitive room (like the roof or the front door), you feel the effects immediately.

In this system, we track how transiting planets cross over the exact positions of your birth planets.

---

## 2. Directory Layout & Key Files

Here is how the files in this export bundle are structured:

```text
exports/transits/
├── README.md                      <-- This guide
├── docs/
│   └── transits.md                <-- Astrological rules, formulas & scriptural sources
├── engine/
│   ├── transits.py                <-- Core mathematical calculations (speeds, stations, aspects)
│   ├── milestone_scanner.py       <-- High-speed ephemeris scanner (finds major turning points)
│   └── draw_transit_biwheel.py    <-- SVG dual-ring chart generator
├── api/
│   └── transit_routes.py          <-- Flask web server endpoints & caching logic
├── ui/
│   ├── tmpl_transit_chart.html    <-- Interactive HTML template (Radar panel & chart view)
│   ├── transit_widget.js          <-- Frontend JavaScript controller (steppers, scrubbing, clicks)
│   └── transit_styles.css         <-- German DIN typography & clean editorial styles
└── tests/
    └── test_transits.py           <-- Automated test suite ensuring math and API accuracy
```

---

## 3. How the Pieces Work Together (The Pipeline)

The system is built on a strict **Two-Hemisphere Architecture**:
1. **Hemisphere A (Pure Math)**: Calculates planetary coordinates, speeds, and aspect angles using the Swiss Ephemeris (`swisseph`). It has no knowledge of colors, HTML, or buttons.
2. **Level 8 Presentation (UI & SVG)**: Takes the pure math and turns it into an interactive bi-wheel chart and a clickable event list.

### Step-by-Step Flow:
```text
[Swiss Ephemeris (swisseph)]
             │
             ▼
[jyotish/transits/transits.py] ──> Calculates speeds, stations (SR/SD), & aspect angles
             │
             ▼
[jyotish/transits/milestone_scanner.py] ──> Scans 360 days for major turning points
             │
             ▼
[app.py (REST API)] ──> Delivers JSON payload to browser
             │
             ├──────────────────────────┐
             ▼                          ▼
[draw_chart.py] (SVG Bi-Wheel)   [transit_widget.js] (Radar Panel)
```

---

## 4. Key Concepts to Understand

### A. Planetary Speeds & Stations (*Stambhana*)
When planets appear to stop and reverse direction from Earth's point of view:
- **Stationary Retrograde (`SR` / *Vakra-ārambha*):** The planet slows to a halt and begins moving backward. In the chart, it is marked with a bold crimson **`SR`** label and a dashed red halo.
- **Stationary Direct (`SD` / *Vakra-tyāga*):** The planet finishes its backward motion, halts, and starts moving forward again. It is marked with a green **`SD`** label.
- **Threshold:** A planet is considered stationary when its speed drops to **10% or less** of its normal average speed.

### B. The 4 Milestone Tiers
Instead of scrubbing through 365 days one by one, the [`milestone_scanner.py`](file:///Users/hajnaljanos/PycharmProjects/astra/exports/transits/engine/milestone_scanner.py) finds key events automatically:
1. **`NATAL_STATION` (Tier 1 - Critical):** A planet halts directly on top of (or in a classical glance to) one of your birth planets within a tight **3°20'** window (a *Navamsha orb*).
2. **`EXACT_ASPECT` (Tier 2 - High):** A slow-moving planet (Mars, Jupiter, Saturn, Rahu, Ketu) reaches exact `0°00'` alignment with a natal planet. It tracks whether this is **Pass 1** (direct), **Pass 2** (retrograde), or **Pass 3** (direct).
3. **`SKY_STATION` (Tier 3 - Medium):** A general direction change anywhere in the zodiac.
4. **`SIGN_INGRESS` (Tier 3 - Medium):** A planet crosses the boundary into a new zodiac sign (`0°00'`), changing house topics.

### C. The Bi-Wheel Chart Visuals
- **Inner Ring:** Your permanent birth chart (*D1 Natal*).
- **Outer Ring:** The moving transit planets on that date.
- **Aspect Lines:** Lines connecting outer transit planets to inner birth planets:
  - **Solid Lines:** *Applying* aspects (the transit planet is moving closer to exact alignment—energy is building up).
  - **Dashed Lines:** *Separating* aspects (the transit planet is moving away—the peak moment has passed).
- **Diamond Rim Pins:** Small clickable diamond markers on the outer circle showing where future planetary stations will occur. Clicking one instantly jumps the chart to that exact date.

---

## 5. File Reference Links

- Specification & Rules: [`docs/transits.md`](file:///Users/hajnaljanos/PycharmProjects/astra/exports/transits/docs/transits.md)
- Core Math Engine: [`engine/transits.py`](file:///Users/hajnaljanos/PycharmProjects/astra/exports/transits/engine/transits.py)
- Fast Horizon Scanner: [`engine/milestone_scanner.py`](file:///Users/hajnaljanos/PycharmProjects/astra/exports/transits/engine/milestone_scanner.py)
- SVG Bi-Wheel Generator: [`engine/draw_transit_biwheel.py`](file:///Users/hajnaljanos/PycharmProjects/astra/exports/transits/engine/draw_transit_biwheel.py)
- Flask API Endpoints: [`api/transit_routes.py`](file:///Users/hajnaljanos/PycharmProjects/astra/exports/transits/api/transit_routes.py)
- HTML Template: [`ui/tmpl_transit_chart.html`](file:///Users/hajnaljanos/PycharmProjects/astra/exports/transits/ui/tmpl_transit_chart.html)
- Frontend Logic: [`ui/transit_widget.js`](file:///Users/hajnaljanos/PycharmProjects/astra/exports/transits/ui/transit_widget.js)
- Editorial CSS Styles: [`ui/transit_styles.css`](file:///Users/hajnaljanos/PycharmProjects/astra/exports/transits/ui/transit_styles.css)
- Unit Tests: [`tests/test_transits.py`](file:///Users/hajnaljanos/PycharmProjects/astra/exports/transits/tests/test_transits.py)
