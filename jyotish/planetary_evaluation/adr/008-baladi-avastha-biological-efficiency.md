# ADR-008: Bālādi Avasthās & Biological Operational Efficiency

## Context & The Shortcoming in the Naive Model
Standard astrological software often evaluates a planet solely on whether it is in an exalted or friendly sign. 

However, ancient masters observed that degree position inside the sign determines the planet's **biological and physical maturity** (*Bālādi Avasthās*, *Phaladeepika* 3.10). A planet at 29°50' in an odd sign is in *Mrita Avasthā* (exhausted / dormant / incapacitated). Even if exalted, its tangible, real-world manifestation will be delayed or sluggish because its biological battery is spent.

## Decision
1. **Implement Classical Odd/Even Sign Degree Inversion:**
   - **Odd Signs** (Aries, Gemini, Leo, Libra, Sagittarius, Aquarius) progress from birth to death:
     - $0^\circ - 6^\circ$: **Bala** (Infant, 50% operational efficiency)
     - $6^\circ - 12^\circ$: **Kumara** (Youth, 75% efficiency)
     - $12^\circ - 18^\circ$: **Yuva** (Prime Adult, 100% efficiency)
     - $18^\circ - 24^\circ$: **Vriddha** (Elder/Aging, 50% efficiency)
     - $24^\circ - 30^\circ$: **Mrita** (Incapacitated/Dormant, 25% efficiency)
   - **Even Signs** (Taurus, Cancer, Virgo, Scorpio, Capricorn, Pisces) invert from death to birth:
     - $0^\circ - 6^\circ$: **Mrita** (25%)
     - $6^\circ - 12^\circ$: **Vriddha** (50%)
     - $12^\circ - 18^\circ$: **Yuva** (100%)
     - $18^\circ - 24^\circ$: **Kumara** (75%)
     - $24^\circ - 30^\circ$: **Bala** (50%)
2. **Operational Efficiency Factor ($E_{\text{baladi}}$):**
   The final calibrated Vitality Score scales with biological efficiency:
   $$\text{Final Score} = \text{clamp}\Big(5.0 + (\text{PreScore} - 5.0) \times (0.6 + 0.4 \times E_{\text{baladi}}),\, 1.0,\, 10.0\Big)$$
   This ensures that an incapacitated planet's extreme swings are cushioned toward a moderate baseline, realistically reflecting biological latency without falsifying its core character.

## Proof & Validation
All 9 planets correctly compute their odd/even Bālādi age segments and efficiency factors in both Python (`calculate_baladi_avastha`) and the frontend UI, displaying exact degree bounds and classical Sanskrit titles (*Nripa*, *Sukhi*, *Vadhishnu*, *Gada*, *Mrita*).
