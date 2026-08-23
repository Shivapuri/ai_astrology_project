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

### 1. Radial Text Stacking (NO Rotation)
- The text for each planet must form a vertical stack along an invisible radial line pointing towards the center of the chart.
- The SVG `<text>` elements MUST remain completely upright (horizontal baseline). **Do not use `transform="rotate(...)"`** to turn the letters sideways.
- The stacking order, reading from the outer edge (Rasi inner border) inward towards the center (House outer border), MUST be exactly:
  1. **Planet Glyph** (e.g. ♂) - furthest out
  2. **Degree** (e.g. 25°)
  3. **Sign** (e.g. ♍)
  4. **Minute** (e.g. 31') - closest to the center

### 2. Ascendant (Lagna) Line and Spacing
- A single, thin red line (`#C0392B`) is drawn for the Ascendant (House 1 Cusp) going from the inner house border to the inner sign border, capped with a red arrowhead.
- To prevent the Ascendant text stack ("Asc", "9°", "♌", "35'") from overlapping this red line, the `angle` for the Lagna stack is slightly offset (e.g., `+2.2` degrees). This makes the text float perfectly above the line.
- Because "Asc" is a wide string, its specific stacking radii must be spaced out more generously (e.g., `-5`, `-24`, `-35`, `-46` pixels from the border) compared to standard planets (which use `-10`, `-22`, `-32`, `-42`).

## Justification
These highly specific visual spacing rules are required to achieve the exact aesthetic cleanliness and readability of professional astrology software. Without these rules, the circular chart becomes a chaotic overlap of text and lines.

## Trade-offs
- **Pros:** A beautiful, readable, professional-grade circular chart UI that exactly matches user expectations and reference material.
- **Cons:** Introduces highly specific, hardcoded SVG radius values (`r_deg_base = r_rasi_inner - 26 if p_name == 'Lagna' else r_rasi_inner - 22`) which could require manual tweaking if the overall SVG canvas size changes in the future.
