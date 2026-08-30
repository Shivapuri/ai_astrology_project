# UI Scaling Guidelines for Astra Grid

This document defines the strict rules for how widgets inside the Split.js grid must scale and adapt.

## Rule 1: No Scrolling for Data Tables
Data tables (Dignities, Avasthas, Dashas, Aspects, Metrics) must **NEVER** scroll. 
They must dynamically scale up or down to use the **absolute maximum** horizontal and vertical space available inside their parent `.grid-cell`. 

## Rule 2: JS ResizeObserver is Mandatory
CSS `clamp()` or `cqmin` alone are insufficient for perfect bounding box scaling because table row heights and column widths are intrinsically tied to their content. 
To achieve maximum efficiency without clipping:
1. The table must be wrapped in a `.scale-wrapper`.
2. The wrapper must have an explicit unscaled width/height (or `max-content`).
3. A JavaScript `ResizeObserver` attached to `.grid-cell` must calculate the exact bounding box ratio: 
   `scale = Math.min(cellWidth / contentWidth, cellHeight / contentHeight)`
4. Apply `transform: scale(scale)` to the `.scale-wrapper`.

## Rule 3: Exceptions (Context Info)
The ONLY widgets permitted to use `overflow: auto` (scrollbars) are text-heavy widgets like the **Context Info** panel. 
These widgets should bypass the ResizeObserver logic and rely on standard CSS block flow.

## Rule 4: Centering
Scaled tables should be perfectly centered horizontally and vertically within their grid cells using flexbox on the parent container.
