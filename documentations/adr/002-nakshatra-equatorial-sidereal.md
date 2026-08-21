# ADR 002: Nakshatra Zodiac System (Equatorial Sidereal)

## Status
Accepted

## Context
Standard Vedic astrology universally uses the Ecliptic Sidereal zodiac for Nakshatras, most commonly anchored to the Lahiri (Chitra Paksha) Ayanamsa. In this standard model, both Rasi (Signs) and Nakshatras share the exact same starting point on the ecliptic.
Ernst Wilhelm's Kala methodology diverges from this by using a hybrid system: Rasis are purely Tropical, but Nakshatras are Sidereal. Furthermore, the Nakshatras are not measured along the ecliptic, but rather projected onto the celestial equator anchored to the Dhruva Galactic Center (Middle of Mula).

## Decision
We will calculate Nakshatras using the **Equatorial Sidereal** method anchored to the Dhruva Galactic Center, completely separate from the Tropical ecliptic calculations used for Rasis.

## Justification
- This is the cornerstone of Ernst Wilhelm's astronomical research and the core requirement for the Astra project.
- It perfectly resolves edge cases where planetary Nakshatra positions differ between Kala software and standard software like Jagannatha Hora (which uses Ecliptic Sidereal).

## Trade-offs
- **Pros:** Astronomically precise mapping of stars to the equator. Matches Kala perfectly.
- **Cons:** Calculation requires complex 3D spherical trigonometry (converting ecliptic to equatorial coordinates, subtracting equatorial Ayanamsa, and converting back). It also means our Nakshatra calculations will conflict with almost all other standard Jyotish software, requiring careful user education.
