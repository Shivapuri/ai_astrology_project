# Astra UI & Architecture Blueprint

This document outlines the strategic pipeline and technical architecture for the Astra software. It establishes a clear, scalable design philosophy for adding new features (Dashas, Yogas, Avasthas) and a modern, flexible UI layout inspired by professional tools like *Kala* and *Aries*.

---

## 1. UI/UX Design Philosophy

The application will transition from a static HTML page to a dynamic, dashboard-style interface. 

### Layout Structure
The interface will be divided into a **Resizable Split-Pane Layout**:
1.  **Left Pane (Main Chart Area - 60-70% width):**
    *   The single, large visual chart.
    *   Supports keyboard shortcuts to hot-swap the view instantly (e.g., `N` for North Indian, `S` for South Indian, `C` for Circular).
2.  **Right Pane (Information & Metrics Dashboard - 30-40% width):**
    *   A vertically stacked, accordion-style or grid-based layout of "Sub-Windows".
    *   **Top Window (Context Info):** A dynamic panel. When you click a planet, sign, or house in the Main Chart, this panel instantly updates with the relevant classical texts, dignities, and details.
    *   **Middle Window (Metrics/Strengths):** The Avasthas, Shadbala, and Ishta/Kashta metrics.
    *   **Bottom Windows (Future Additions):** Collapsible panels for Dashas, Yogas, and Nakshatra details.

### Tech Stack Recommendation for UI
Since Astra currently uses lightweight Python (Flask) and plain HTML/JS, we can keep the stack simple but professional:
*   **Grid/Sizing Engine:** Use a lightweight Vanilla JS library like **Split.js** or **Muuri.js**. This gives you professional drag-to-resize, expand, and collapse functionalities without needing a heavy framework like React (which Aries uses).
*   **Interactivity:** Vanilla JavaScript event listeners utilizing HTML5 `data-*` attributes.

---

## 2. Interaction Pipeline (How Clicks Work)

To make the SVGs interactive without "knitting" messy code together, we must establish a clean data contract between the SVG shapes and the UI panels.

1.  **Tagging SVGs in Python:** When `generate_html_chart.py` builds the SVG, every element must have a specific class and data attribute.
    *   *Example:* `<text class="interactive-element planet" data-id="Sun" x="10" y="20">☉</text>`
    *   *Example:* `<rect class="interactive-element house" data-id="1" ... />`
2.  **Central JSON State:** When the page loads, Flask passes the entire `vedic_context.json` into a JavaScript variable in the browser: `const chartData = {...}`.
3.  **Event Listeners:** A single JavaScript file (`ui_controller.js`) listens for clicks on any `.interactive-element`.
4.  **Dynamic Rendering:** When "Sun" is clicked, JS looks up `chartData.grahas.Sun` and injects its data (longitude, dignity, avasthas) into the Right Pane's HTML. No page reloads are required.

---

## 3. The Circular Chart (Aries Inspiration)

Inspired by the *Aries* software, the Circular (Western-style) chart should be built using concentric SVG rings.

**Structural Layers (Outer to Inner):**
1.  **Outer Ring (Nakshatras):** 27 segments of $13^\circ 20'$ each.
2.  **Middle Ring (Tropical Rasis):** 12 segments of $30^\circ$ each.
3.  **Inner Ring (Houses/Bhavas):** Equal House or Campanus cusps drawing the slices.
4.  **Data Layer (Planets):** Planetary glyphs plotted at their exact degree along the circumference.
5.  **Core (Aspects):** Lines drawn across the center connecting planets that aspect each other.

*Implementation Note:* Instead of hardcoding SVG coordinates, implement a Python math helper `polar_to_cartesian(center_x, center_y, radius, degree)` to calculate precise `x, y` SVG coordinates on the fly.

---

## 4. Backend Architecture: The Feature Pipeline

To prevent the software from becoming a tangled mess as you add Dashas, Yogas, and Avasthas, Astra will use a **Modular Engine Pipeline**. 

Whenever you want to build a new feature, you follow these exact steps:

### Step 1: Create the Engine Module
Create a new file in `jyotish/engines/` (e.g., `jyotish/engines/dasha_engine.py`).
This file contains a single class or function that takes the *Core Astronomical Data* (degrees of planets) and applies the astrological logic.

### Step 2: The Core Rule
**Engines never touch HTML or the UI.** They only take in floats/dicts and return raw Python dictionaries.
*Example:* `calculate_vimshottari(moon_deg)` returns `{"maha_dasha": "Venus", "balance_years": 12.4}`.

### Step 3: The Context Aggregator
In a `chart_context.py` file, you build the Master JSON. You simply plug your new engine into the aggregator:
```python
def build_master_context(birth_data):
    core_math = calculate_ephemeris(birth_data)
    
    context = {
        "astronomy": core_math,
        "strengths": avastha_engine.calculate(core_math),
        "dashas": dasha_engine.calculate(core_math),
        "yogas": yoga_engine.calculate(core_math)
    }
    return context
```

### Step 4: UI Registration
Because the new feature is cleanly packed into the Master JSON, the frontend immediately has access to `chartData.dashas`. You simply add a new HTML template block in the Right Pane to display it, and you're done.

---

## 5. Next Immediate Steps (Action Plan)

To transition to this professional structure, here is the recommended order of development:

1.  **Phase 1: The UI Shell (HTML/CSS)**
    *   Implement **Split.js** (or standard CSS Grid) in `index.html` to create a resizable Left Pane (Chart) and Right Pane (Info).
    *   Create the collapsible sub-windows in the Right Pane (Info, Metrics).
    *   Add Keyboard Event Listeners in JS for `N`, `S`, `C` to toggle SVG visibility.
2.  **Phase 2: Interactive SVG Upgrades**
    *   Refactor `generate_html_chart.py` to inject `class="clickable"` and `data-*` attributes into the SVG elements.
    *   Write the Javascript click-handler to update the Right Pane when a planet/house is clicked.
3.  **Phase 3: The Circular Chart Engine**
    *   Write the polar-to-cartesian math helpers in Python.
    *   Implement the concentric Nakshatra/Rasi SVG rings.
4.  **Phase 4: Engine Refactoring**
    *   Move the current Avasthas logic into a dedicated `jyotish/engines/avasthas.py` following the Pipeline rules above, ensuring it outputs pure JSON ready for the frontend.
