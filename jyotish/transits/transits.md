# Transit Calculation & Analysis Engine (Gochara)

## 1. Philosophical & Scriptural Grounding
In Vedic Astrology (Jyotish), natal horoscopy establishes the fixed karmic blueprint (*Prarabdha Karma*), while **Transits (*Gochara*)** represent the dynamic unfolding of time as planets traverse the zodiac relative to that natal blueprint.

### Scriptural References:
* **Phaladeepika (Mantreswara), Chapter 26 (Gochara Phala):**
  * Transits must be evaluated primarily from the **Natal Moon (*Janma Rasi / Chandra Lagna*)**, as the Moon governs the conscious mind (*Manas*) and personal experience of events.
  * Transits are secondarily evaluated from the **Natal Ascendant (*Janma Lagna*)**, which governs bodily health, status, and physical reality.
  * **Navamsha Orb Rule:** Significant transit triggers occur when a transiting planet occupies the same Navamsha (3°20' arc or 3.3333°) or forms exact degree aspects with natal planets.
* **Brihat Parashara Hora Shastra (BPHS), Chapters on Drishti:**
  * Aspect glances (*Graha Drishti*):
    * All planets cast full aspect onto the 7th house (180° opposition).
    * **Mars** casts special full aspects on the 4th (90°) and 8th (210°) houses.
    * **Jupiter** casts special full aspects on the 5th (120°) and 9th (240°) houses (Dharma trines).
    * **Saturn** casts special full aspects on the 3rd (60°) and 10th (270°) houses.
    * **Rahu & Ketu** cast trine glances on the 5th (120°) and 9th (240°) houses.

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

## 3. Planetary Speed, Station States (*Gati* / *Stambhana*), & Transit Physics
The speed of a transiting body determines the psychological depth and enduring impact of its transit.

### Mean Daily Longitudinal Speeds (degrees / day):
* **Sun**: `0.9856°/day`
* **Moon**: `13.1764°/day`
* **Mars**: `0.5240°/day`
* **Mercury**: `1.0000°/day` (mean orbital longitude ~0.9856° solar-locked, 1.0° baseline)
* **Jupiter**: `0.0831°/day`
* **Venus**: `1.0000°/day` (1.0° baseline)
* **Saturn**: `0.0335°/day`
* **Rahu / Ketu**: `0.0530°/day` (mean true node oscillation baseline)

### Station States & Classical Motion Classifications (*Gati*):
* **Stationary Threshold (`is_stationary`)**:
  * Applies to the 5 star planets: Mars, Mercury, Jupiter, Venus, Saturn.
  * A planet is defined as stationary when its relative speed ratio `abs(daily_speed) / mean_daily_speed <= 0.10` (moving at less than or equal to 10% of its normal daily motion), or within ±48 hours of an exact mathematical speed root (`daily_speed == 0.0`).
* **Stationary Retrograde (`SR` / *Vakra-ārambha / Stambhana*)**:
  * The planet slows to a halt while transitioning from direct (positive) to retrograde (negative) motion ($d(\text{speed})/dt < 0$).
* **Stationary Direct (`SD` / *Vakra-tyāga / Stambhana*)**:
  * The planet halts while transitioning from retrograde (negative) to direct (positive) motion ($d(\text{speed})/dt > 0$).
* **Slow (*Mandatara*)**:
  * Motion where `0.10 < speed_ratio <= 0.50`.
* **Retrograde (*Vakri*)**:
  * Planetary longitudinal speed is negative (`daily_speed < 0`) and `speed_ratio > 0.10`.
* **Accelerated / Fast (*Atichara*)**:
  * Motion exceeding typical bounds (`speed_ratio >= 1.20`).
* **Direct / Normal (*Rju*)**:
  * Standard forward motion (`speed_ratio > 0.50` and positive).

---

## 4. Transit Milestone Scanner Architecture (Coarse-to-Fine Ephemeris Scan)
To avoid manual day-by-day scrubbing, `jyotish/transits/milestone_scanner.py` provides automated chronological milestone detection:
1. **Scanning Horizon**: Scans a configurable window (default `-90` days to `+270` days, 360 days total).
2. **Algorithmic Strategy**:
   * Evaluates daily positions and speeds via direct `swisseph` (`swe.calc_ut`) in ~30 milliseconds.
   * Performs root-finding (bisection) to locate event timestamps down to 1-minute precision.
3. **Four Milestone Event Tiers**:
   * **`NATAL_STATION` (Tier 1 - Critical)**: A planet crosses `daily_speed == 0.0` (`SR` or `SD`) while within `3°20'` (Navamsha orb) of a conjunction or classical Graha Drishti to a natal planet or natal Lagna.
   * **`EXACT_ASPECT` (Tier 2 - High)**: A major slow planet (Mars, Jupiter, Saturn, Rahu, Ketu) reaches exact `0°00'` of a conjunction or Graha Drishti with a natal planet or Lagna. Tagged with pass number (`Pass 1`, `Pass 2`, `Pass 3`) across retrograde loops.
   * **`SKY_STATION` (Tier 3 - Medium)**: A planet turns `SR` or `SD` outside natal orb, shifting house energy from Lagna and Moon.
   * **`SIGN_INGRESS` (Tier 3 - Medium)**: A major planet crosses a 30° Tropical sign boundary (`0°00'`), changing Whole-Sign house placement from Lagna and Moon.
4. **Output Integrity**: Pure dictionary conforming to Hemisphere A rules (floats, ints, booleans, strings; zero HTML, zero CSS styling).
