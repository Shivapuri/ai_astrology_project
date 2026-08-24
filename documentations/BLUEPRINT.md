# Astra UI & Architecture Blueprint

This document outlines the strategic pipeline and technical architecture for the Astra software. It establishes a clear, scalable design philosophy for adding new features (Dashas, Yogas, Avasthas) and a modern, flexible UI layout inspired by professional tools like *Kala* and *Aries*.

---

## 1. UI/UX Dashboard Architecture

The interface is built as a **Full-Screen, Resizable Split-Pane Dashboard** utilizing the authentic **Pergamon Color Palette** (`#f7f3eb` background, `#fffdfa` cards, `#4a3325` text, and `#d35400` accents).

### Layout Structure
1.  **Top Menu Bar / Native Toolbar:**
    *   Compact, native app style header.
    *   Contains app title, saved person selector dropdown, "Load" button, "+ Add Person" modal trigger, chart title/subtitle, and Display Settings.
2.  **Left Pane (Main Chart Area - 60% default width):**
    *   Full-height responsive SVG container that scales with the window size.
    *   Varga dropdown with all 16 divisions (D1 to D60).
    *   Keyboard shortcut hot-swapping: `S` for South Indian, `N` for North Indian, `C` for Circular.
3.  **Right Pane (Information & Metrics Dashboard - 40% default width):**
    *   Split vertically into two sub-windows with a horizontal drag handle:
    *   **Top Sub-Window (Context Info):** Dynamic panel displaying details about whatever planet, sign, or house is clicked in the main chart.
    *   **Bottom Sub-Window (Tabbed Metrics):**
        *   **Tab 1: Nakshatras:** Table of Graha longitudes, degrees (0-30°), signs, Nakshatras, and Padas.
        *   **Tab 2: Metrics / Dignity:** Planetary Sambandha, 5-fold dignity (Panchadha), Baladi Avasthas, and Jagradadi Avasthas.

---

## 2. Calculation Engine Architecture (`/jyotish/`)

All calculation logic is modular, deterministic, and isolated from the UI layer:

| Component | File Path | Method / Description |
|---|---|---|
| **Vargas (D1–D60)** | `jyotish/generate_jyotish.py` | `calculate_varga_longitude()`: Implements all 16 Parashara/Ernst Wilhelm harmonic and unequal divisions. |
| **Baladi Avastha** | `jyotish/avasthas/bala.py` | 5-state physical age/vitality based on odd/even sign degree brackets. |
| **Jagradadi Avastha** | `jyotish/avasthas/jagrat.py` | 3-state consciousness/alertness based on natural dignity (*Naisargika*). |
| **Panchadha Sambandha** | `jyotish/relationships.py` | Natural + Temporary = Compound relationship and final planetary dignity. |
| **Bhava Chalita** | `jyotish/generate_jyotish.py` | Campanus house cusps + intermediate midpoint boundaries (*Sandhis*). |
| **Equatorial Nakshatras** | `jyotish/generate_jyotish.py` | Dhruva Galactic Center Ayanamsa calculation anchored to the middle of Mula. |
| **SVG Visuals** | `jyotish/draw_chart.py` | Responsive South Indian and North Indian vector chart generators with tagged interactive elements. |

---

## 3. UI Interaction Pipeline (How Clicks Work)

1.  **Tagging SVGs in Python:** When `draw_chart.py` builds the SVG, every element receives CSS classes and data attributes:
    *   *Example:* `<text class="interactive" data-type="planet" data-id="Sun">☉</text>`
    *   *Example:* `<text class="interactive" data-type="sign" data-id="Leo">♌</text>`
2.  **Central JSON State:** Flask passes the full calculation dictionary (`currentChartData`) into the browser session.
3.  **Event Listeners:** The UI listens for click events on `.interactive`.
4.  **Dynamic Rendering:** Clicking a planet populates the "Context Info" sub-window with degrees, dignity, and avasthas without reloading the page.

---

## 4. Circular Chart (Aries Inspiration - Phase 3)

The Circular (Western-style) chart with Nakshatras will be built using concentric SVG rings:

**Structural Layers (Outer to Inner):**
1.  **Outer Ring (Nakshatras):** 27 segments of $13^\circ 20'$ each, labeled with Nakshatra names/glyphs.
2.  **Middle Ring (Tropical Rasis):** 12 segments of $30^\circ$ each.
3.  **Inner Ring (Houses/Bhavas):** Campanus house slices.
4.  **Data Layer (Planets):** Planetary glyphs plotted along the circle circumference via `polar_to_cartesian()`.
5.  **Core (Aspects):** Center lines connecting aspecting planets.

---

## 5. Development Roadmap & Status

*   [x] **Phase 1: Full-Screen Split Dashboard & Toolbar** (Completed)
    *   Full-width edge-to-edge layout with `Split.js`.
    *   Compact native app top toolbar with "+ Add Person" modal.
    *   All 16 Vargas restored (D1 to D60).
    *   Pergamon aesthetic styling.
    *   Mandatory automated UI verification protocol locked into `GEMINI.md`.
*   [ ] **Phase 2: Enhanced Context Info & Knowledge Base**
    *   Expand click handlers for houses and signs to show classical BPHS descriptions.
    *   Live highlights when clicking planets/houses.
*   [x] **Phase 3: Circular Western / Nakshatra Chart Engine**
    *   Polar math helper functions.
    *   Concentric ring SVG renderer.
    *   Hotkey `C` integration.
*   [ ] **Phase 4: Additional Jyotish Engines**
    *   [x] Vimshottari Dasha engine (Integrated with full timeline).
    *   [x] Shadbala engine (Fully integrated in UI).
    *   [x] Aspects (Drishti) engine - Rasi and Graha Drishti.
    *   [ ] Yoga detection engine.
*   [ ] **Phase 5: Documentation & Refining**
    *   [ ] Update `avasthas.md` to document Deeptadi, Lajjitadi, and Shayanadi logic.
