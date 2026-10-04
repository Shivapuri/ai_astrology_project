# Transit Calculation & Analysis Engine (Gochara)

## 1. Philosophical & Scriptural Grounding
In Vedic Astrology (Jyotish), natal horoscopy establishes the fixed karmic blueprint (*Prarabdha Karma*), while **Transits (*Gochara*)** represent the dynamic unfolding of time as planets traverse the zodiac relative to that natal blueprint.

### Scriptural References:
* **Phaladeepika (Mantreswara), Chapter 26 (Gochara Phala):**
  * Transits must be evaluated primarily from the **Natal Moon (*Janma Rasi / Chandra Lagna*)**, as the Moon governs the conscious mind (*Manas*) and personal experience of events.
  * Transits are secondarily evaluated from the **Natal Ascendant (*Janma Lagna*)**, which governs bodily health, status, and physical reality.
  * **Navamsha Orb Rule:** Significant transit triggers occur when a transiting planet occupies the same Navamsha (3°20' arc) or forms exact degree aspects with natal planets.
* **Brihat Parashara Hora Shastra (BPHS), Chapters on Drishti:**
  * Aspect glances (*Graha Drishti*):
    * All planets cast full aspect onto the 7th house (180° opposition).
    * **Mars** casts special full aspects on the 4th (90°) and 8th (210°) houses.
    * **Jupiter** casts special full aspects on the 5th (120°) and 9th (240°) houses (Dharma trines).
    * **Saturn** casts special full aspects on the 3rd (60°) and 10th (270°) houses.

---

## 2. Integrated System Settings (Kala Methodology)
In accordance with Ernst Wilhelm's Kala configuration in Astra:
1. **Tropical Rasis (Signs):**
   * Transiting planetary longitudes are computed in the Tropical Zodiac.
   * A transit planet entering 0° Aries is physically at 0° Aries Tropical, perfectly overlaying the natal Tropical signs and Campanus houses.
2. **Sidereal Equatorial Nakshatras (Dhruva Galactic Center) & Vic DiCara (Chitra Paksha):**
   * The active user setting determines the nakshatra calculation:
     * `ERNST_DHRUVA`: Equatorial Right Ascension anchored to middle of Mula.
     * `VIC_CHITRA`: Ecliptic Sidereal Lahiri / Chitra Paksha.
   * Transiting planets receive their Nakshatra and Pada using the identical ayanamsa as the natal chart.

---

## 3. Computational Architecture
The module `jyotish/transits/transits.py` provides:
1. `calculate_transits(...)`:
   * Calculates real-time or user-specified planetary longitudes and motion using Swiss Ephemeris (`swisseph`).
   * Determines transit house placement relative to **Natal Lagna** and **Natal Moon**.
   * Identifies **Active Transit Triggers**:
     * Conjunctions (0° ± orb)
     * Oppositions (180° ± orb)
     * Special Graha Drishti aspects (Mars 4th/8th, Jupiter 5th/9th, Saturn 3rd/10th)
     * Computes exact separation, orb difference, and aspect virupas via `get_graha_drishti`.
2. Output formatting:
   * Pure dictionary returning floats, strings, and booleans with zero HTML formatting, respecting Astra Level 4 architecture.
