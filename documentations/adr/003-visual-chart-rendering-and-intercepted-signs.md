# ADR 003: Visual Chart Rendering & Intercepted Signs

## Status
Accepted

## Context
When drawing North Indian and South Indian Rasi charts, standard Jyotish software places exactly one house cusp (1 through 12) in each of the 12 signs. However, because we use the Campanus house system (ADR-001) at high latitudes (e.g., 52°N), signs become intercepted. This results in multiple cusps falling into a single sign, while other signs have zero cusps.
Initially, drawing these cusps directly into the Rasi sign boxes confused the user because the physical squares of the North Indian Rasi chart looked like "houses", but contained the "wrong" cusps.

## Decision
1. We will explicitly draw the Campanus house cusp numbers (1-12) directly into the sign boxes of the **Tropical South Indian (Rasi)** and **Tropical North Indian (Rasi)** charts, exactly where they mathematically fall, even if multiple cusps land in one box.
2. We will provide a distinct, third visual chart called **Bhava Chalita (Proper Houses)** drawn in the North Indian diamond format. In this chart, the diamonds literally represent Houses 1-12 (rather than signs), and planets/cusps are placed by their house bounds.

## Justification
- Replicating the exact UI of Kala software requires showing the mathematical reality of intercepted signs in the Rasi chart.
- Adding the dedicated Bhava Chalita visual chart separates the concept of "Sign placement" from "House placement", resolving the visual ambiguity of intercepted signs.

## Trade-offs
- **Pros:** Full transparency into the astronomical house division. The dedicated Bhava Chalita chart provides a clear view of house occupancy.
- **Cons:** Rasi charts with intercepted signs (e.g. empty boxes, or boxes with two cusp numbers) can look messy and unintuitive to traditional Vedic astrologers who are used to Whole Sign houses.
