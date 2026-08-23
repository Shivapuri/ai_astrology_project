# ADR-007: Temporary Friendship (Tatkalika Maitri) Calculated Only in D1 Rasi

## Context
When calculating the 5-fold Compound Friendship (Panchadha Maitri) in Vedic Astrology, the standard practice in many modern software programs is to calculate the Temporary Friendship (Tatkalika) independently for every Divisional Chart (Varga) based on the spatial positions of planets in that specific Varga. 

## Decision
In the Astra Engine, following Ernst Wilhelm's Kala methodology, Temporary Friendship is calculated **STRICTLY ONCE in the D1 (Rasi) birth chart** and then transferred down identically to all Varga charts.

## Rationale
1. **Sanskrit Translation:** Sage Parashara defines Temporary Friendship using the phrase "at that time" (*tatkAle mitratAM yAnti*). 
2. **Astronomical Reality:** Time in Vedic astrology is universally derived from the physical, astronomical zodiac (the Rasi chart). Planets that are 180 degrees apart in the physical sky (Rasi) might randomly fall into the same sign in a mathematical Varga (like D9). Recalculating their temporary friendship based on Varga placement treats a mathematical derivative as physical space, which is astronomically and logically inconsistent.
3. **Empirical Validation:** Ernst Wilhelm's extensive predictive research over 20+ years demonstrates that transferring the D1 Temporary Friendship down to the Vargas yields vastly superior predictive accuracy.
