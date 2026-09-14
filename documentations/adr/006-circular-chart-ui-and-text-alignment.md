# ADR 006: Circular Chart UI and Text Alignment

## Status
Accepted

## Context
The Circular Chart in Astra required strict visual alignment to match the professional output of the reference *Kala* software, specifically regarding how planets, degrees, signs, and minutes are stacked along the radial lines (spokes) of the circular chart. 

During development, there were two major UI bugs caused by misinterpreting "radial alignment":
1. **The Rotation Bug**: The SVG `<text>` elements were physically rotated (e.g. `transform="rotate(...)"`) sideways to align with the radius. This made the text unreadable and violated the reference design.
2. **The Horizontal Line Bug**: The degree, sign, and minute were printed horizontally next to each other in a single string under the planet, rather than being stacked vertically in a column pointing towards the center.

Furthermore, the Ascendant (Lagna) text ("Asc", "9°", "♌", "35'") was overlapping the red Ascendant indicator line, and the horizontal spacing was too cramped because "Asc" is a wide word compared to single-character planet glyphs.

## Decision
To ensure the circular chart always looks completely polished and matches the reference design, the following strict UI rules MUST be adhered to permanently:

### 1. Radial Text Stacking (NO Rotation, Sign Glyph Omitted)
- The text for each planet forms a vertical stack along an invisible radial line pointing towards the center of the chart.
- The SVG `<text>` elements MUST remain completely upright (horizontal baseline). **Do not use `transform="rotate(...)"`** to turn the letters sideways.
- The stacking order, reading from the outer edge (Rasi inner border) inward towards the center (House outer border), is simplified to 3 rows:
  1. **Planet Glyph** (e.g. ♂) - furthest out (`r = r_rasi_inner - 9 = 146`)
  2. **Degree** (e.g. 25°) - middle (`r = r_rasi_inner - 21 = 134`)
  3. **Minute** (e.g. 31' or 31'R) - innermost (`r = r_rasi_inner - 32 = 123`)
- The zodiac sign glyph is omitted from the planet stack because each planet is already located within its 30° zodiac sign segment on the wheel (which has its sign symbol clearly displayed in the outer ring). This saves over 20px of radial space.

### 2. Ascendant (Lagna) Line and Clearance
- A single, thin red line (`#C0392B`) is drawn for the Ascendant (House 1 Cusp) going from the inner house border to the inner sign border, capped with a red arrowhead.
- To prevent the Ascendant text stack ("Asc", "9°", "35'") from overlapping this red line or conjunct planets (e.g. Venus in Cancer), relaxation enforces `MIN_SEP = 6.0°` for Lagna, and offsets the text slightly below the horizontal axis (`182.5°`).

### 3. Expanded Inner Aspect Circle & Graha Drishti
- The inner circle is enlarged to `r_bhava_inner = 76` and `r_bhava_outer = 92` (providing a central aspect drawing diameter of 152px, a +185% area expansion).
- Campanus house cusps are positioned at `r_bhava_outer + 12 = 104`, maintaining a safe 15+ pixel margin from the planet text stack.
- Inside the inner circle ($r \le 76$), Parashara Graha Drishti chords with directional arrowheads connect aspecting and aspected planets:
  - **Exalted / Benefic (Gold/Green)**: Uplifting blessings (`#D4AC0D` / `#27AE60`).
  - **Malefic / Debilitated (Red)**: Pressure glances (`#C0392B`).
  - **Neutral (Blue)**: Moderate glances (`#2980B9`).
- **Interactive Focus & Toggle**: Clicking any planet isolates its incoming/outgoing aspects; clicking the center circle clears the filter or toggles aspect visibility.

## Justification
These visual spacing and aspect rules achieve high aesthetic cleanliness, zero text overlap, and deep astrological clarity based on Parashara's teachings and Ernst Wilhelm's Kala methodology.

## Trade-offs
- **Pros:** A beautiful, readable, professional-grade circular chart UI with clear planetary glance interactions and ample space.
- **Cons:** Slightly smaller whole-sign house radial ring thickness (16px), which is still comfortably sized for house numbers (font size 9.5).

