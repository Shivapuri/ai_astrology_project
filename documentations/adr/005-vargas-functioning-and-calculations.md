# ADR 005: Shodashavarga Functioning and Calculation Rules

## Status
Accepted

## Context
Vedic astrology uses 16 harmonic divisional charts (Shodashavarga) to examine specialized life areas. Previously, the engine used simple harmonic multipliers $(L \times H) \pmod{360^\circ}$. However, Ernst Wilhelm's Kala methodology requires classical discrete sign mapping rules derived from *Brihat Parashara Hora Shastra* (BPHS), while preserving exact continuous fractional degrees ($0^\circ-30^\circ$) within each Varga sign.

Additionally, user testing revealed that while standard classical Parashari Hora (D-2) confines all placements strictly to Cancer and Leo, the Kala software defaults to a distributed Hora where placements are spread across all 12 signs (1st half = same sign, 2nd half = 7th / opposite sign).

## Decision
1. Implement exact discrete mapping rules for all 16 Shodashavarga divisions (D-1 through D-60) in `jyotish/generate_jyotish.py`.
2. Implement Kala's Distributed Hora for D-2 (Opposite Sign shift for the second 15°).
3. Compute exact fractional degrees inside every divisional sign based on proportional progression through each division slice.
4. Project all 12 Campanus house cusps through the identical Varga algorithm and compute Bhava Chalita house start/end bounds per Varga.
5. Provide a dual-slot side-by-side comparison UI in `templates/index.html` allowing simultaneous comparison of any two Vargas.

## Justification
- Matches Ernst Wilhelm's Kala software outputs with 100% mathematical fidelity.
- Preserves full continuous astronomical precision ($0^\circ-30^\circ$) inside divisional signs.
- Details are fully documented in [`documentations/vargas_functioning.md`](../vargas_functioning.md).

## Trade-offs
- **Pros:** Precise alignment with Kala software; supports deep financial and divisional analysis with distributed signs; fully documented algorithms.
- **Cons:** Deviates from simplified continuous harmonic multiplication and standard Sun/Moon-only D2 charts.
