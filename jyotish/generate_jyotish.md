# Jyotish Engine: Master Orchestrator, Nakshatras & Dashas (generate_jyotish.py)

This file documents the core orchestration script `generate_jyotish.py`, which integrates all subsidiary mathematical models into a unified chart computation. In particular, it houses the explicit algorithms for the **Campanus House System**, **Sidereal Equatorial Nakshatras**, and **Vimshottari Dashas**.

---

## 1. Simple Description (For the Layperson)

The `generate_jyotish.py` script is the "Grand Conductor" of the astrology engine. When you provide a birth date, time, and location, this script does the following:
1. **Finds the Planets (Ecliptic):** It looks up exactly where the planets were in the sky using standard Western (Tropical) signs for the main charts.
2. **Calculates the Houses (Campanus):** It divides the sky into 12 "Houses" to see which areas of life the planets affect. It uses a highly accurate 3D method called "Campanus."
3. **Calculates the Stars (Nakshatras):** Instead of looking at the Zodiac along the path of the Sun (Ecliptic), it measures the planets along the Earth's Equator. It anchors this stellar wheel by locking the center of our Galaxy to the middle of the star *Mula*.
4. **Calculates the Timelines (Vimshottari Dasha):** Using the exact position of the Moon in the Nakshatras, it calculates the lifetime timeline (Dashas). It uses a special year length (the Saura year of ~359 days) to calculate when life chapters begin and end.

---

## 2. Technical AI Description (Logic Constraints)

If you are modifying `generate_jyotish.py`, you must strictly observe the following mathematical rules:

### A. House System (Campanus)
*   **Methodology:** Ernst Wilhelm's Kala software explicitly uses the **Campanus House System** for all Bhava Chalita calculations. Campanus divides the Prime Vertical into equal $30^\circ$ segments and projects them onto the ecliptic.
*   **Algorithm:** We use the Swiss Ephemeris flag `b'C'` (`swe.houses(jd, lat, lon, b'C')`).
*   **Rule:** Planets are placed into houses based on whether their Tropical longitude falls between the Start and End points of a Bhava (which often spans across multiple signs, causing intercepted signs at high latitudes).

### B. Sidereal Equatorial Nakshatras (Dhruva Galactic Center)
*   **Ayanamsa Definition:** The zodiac of Nakshatras is distinct from Rasis. It is anchored to the **Galactic Center** (GC). The GC is locked precisely to the middle of the Nakshatra *Mula* ($246^\circ 40'$, or $246.6667^\circ$).
*   **Equatorial Projection:** Nakshatras are not measured on the Ecliptic. Ecliptic longitudes must be converted to Equatorial Right Ascension (RA) using `swe.cotrans`.
*   **Mathematical Formula:**
    1. Calculate GC Right Ascension (RA).
    2. `ayanamsa_eq = ra_gc - 246.6667`
    3. Calculate Planet's Equatorial RA.
    4. `sidereal_ra = (planet_ra - ayanamsa_eq) % 360`
    5. `nakshatra_index = floor(sidereal_ra / 13.3333333)`

### C. Vimshottari Dasha (Saura Year)
*   **Lordship:** Determined by the Moon's Sidereal RA Nakshatra.
*   **Fraction Passed:** The exact degree penetration of the Moon into its current $13^\circ 20'$ Nakshatra span determines the balance of years remaining in the first Mahadasha.
*   **Year Length:** Dashas are calculated using the **Saura Year** (Solar Year) exactly defined as `359.0016` days, not the standard Gregorian 365.24 days or the Savana 360 days.
*   **Mathematical Formula:**
    1. `fraction_left = 1.0 - ((moon_sid_ra % 13.3333) / 13.3333)`
    2. `balance_days = fraction_left * total_mahadasha_years * 359.0016`
    3. Add `balance_days` to the birth Julian Day to find the start of the next Dasha.

---

## 3. Textual Grounding & Quotations (MANDATORY)

These algorithms are grounded in classical scripture, cross-referenced with modern astronomical precision by Ernst Wilhelm (avoiding his earlier *Vault of the Heavens* concepts in favor of his mature *Kala* research).

### The Primacy of Vimshottari Dasha
Sage Parashara explicitly states that out of the multitude of Dasha systems, Vimshottari is the primary and most universally applicable system for humanity in the Kali Yuga.

> **Brihat Parashara Hora Shastra, Chapter 49, Verse 3:**
> दशाबहुविधास्तासु मुख्या विंशोत्तरी मता । कैश्चिदष्टोत्तरी कैश्चित्।ह् कथिता षोडशोत्तरी ॥ ३॥
> *dashAbahuvidhAstAsu mukhyA viMshottarI matA | kaishchidaShTottarI kaishchit.h kathitA ShoDashottarI || 3||*
> **Translation:** "There are many kinds of Dashas. Among them, the Vimshottari Dasha is considered the main/most prominent (mukhya). Some others speak of Ashtottari, and some of Shodashottari."

### Nakshatras & Equatorial Measurement
Ernst Wilhelm's later research conclusively demonstrated that the ancient Vedic concept of the *Dhruva* (Polar) point necessitates measuring Nakshatras along the Equatorial plane (Right Ascension), as they are fixed star groups, unlike the Rasis (Signs) which are bound to the Earth-Sun seasonal Ecliptic. The anchoring of Mula to the Galactic Center aligns the Nakshatra wheel with the physical core of our galaxy.
