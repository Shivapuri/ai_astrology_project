# Parāśarī Planetary Prominence & Opportunity Engine (`prominence.py`)

## 1. Overview & Foundational Mathematical Architecture

Planetary Prominence calculates the **stage volume and opportunity** a planet possesses to express its raw kinetic strength in the native's life. While raw strength (*Bala*) reflects internal muscle, Prominence reflects whether the native's chart gives that planet a microphone, a central spotlight, and clear channels of manifestation.

$$\text{Prominence Score} = \text{SBR} \times (1.0 + \sum \text{Opportunity Weights})$$

### A. The Shadbala Ratio (SBR) & Uniform Normalization Baseline
* **Formula:**
  $$\text{SBR} = \frac{\text{Calculated Rupas}}{6.0}$$
* **Standard Normalization Base ($6.0\text{ Rupas}$):** $6.0\text{ Rupas}$ ($360\text{ Virūpas}$) represents the classical Parāśarī standard unit of planetary potency.
* **Deprecation of Individual Required Rupas (`SHADBALA_REQUIRED_RUPAS`):**
  * In earlier iterations, the engine divided each planet's calculated strength by its textbook minimum requirement (e.g. Mercury: 7.0, Jupiter: 6.5, Moon: 6.0, Venus: 5.5, Sun: 5.0, Mars: 5.0, Saturn: 5.0).
  * **The Distortion:** This division introduced severe artificial bias. For example, in Steve Jobs's chart, Jupiter has an exceptional $7.39\text{ Rupas}$, but dividing by $6.5$ slashed its ratio to $1.137\times$. Meanwhile, Mars ($8.14\text{ Rupas}$) divided by $5.0$ surged to $1.628\times$ (+43% artificial advantage over Jupiter).
  * **The Parāśarī Resolution:** In Vic DiCara's Kala synthesis model, opportunity multiplies the raw Shadbala score directly. Using a uniform baseline of $6.0\text{ Rupas}$ ensures all planets scale naturally according to their true astronomical horsepower without penalizing high-standard benefics or artificially inflating malefics.

---

## 2. Classical Graha Yuddha (Planetary War) Engine

Prior to computing the Shadbala Ratio, the engine resolves any planetary wars between qualifying celestial bodies:

* **Eligible Contestants:** Strictly limited to the 5 true physical planets (*Tāra Grahas*): Mars ($\text{♂}$), Mercury ($\text{☿}$), Jupiter ($\text{♃}$), Venus ($\text{♀}$), and Saturn ($\text{♄}$). The luminaries (Sun, Moon) and shadow nodes (Rāhu, Ketu) do not engage in planetary wars.
* **Orb of Engagement:** Longitudinal separation $\le 1^\circ 00'$ ($1.0^\circ$) on the $D_1$ physical wheel.
* **Winner Determination:**
  1. **Venusian Exception (*Bhṛgu* Immunity):** Venus never loses a planetary war under any celestial circumstance (*Asura Guru* sovereign power).
  2. **Northern Declination (*Uttara Krānti*):** For all other pairs, celestial declination is calculated from the true obliquity of the ecliptic. The planet with the higher Northern declination (positive declination > negative declination) wins.
* **Point Transfer & Unit Normalization:**
  $$\Delta = |\text{Rupas}_1 - \text{Rupas}_2|$$
  * The engine auto-detects Virūpas ($>30.0$) and scales them to Rupas before calculating $\Delta$.
  * Winner gains $\Delta$: $\text{Rupas}_{\text{winner}} = \text{Rupas}_{\text{winner}} + \Delta$
  * Loser is penalized by $\Delta$: $\text{Rupas}_{\text{loser}} = \max(0.0, \text{Rupas}_{\text{loser}} - \Delta)$

---

## 3. The 4 Parāśarī Opportunity Groups (8 Vectors)

Opportunity weights represent the stage access granted to each planet across 4 hierarchical tiers:

### Group 1: Core Anchors (Sudarśana Cakra & Sensitive Doors)
The primary tripod of consciousness: the Ascendant (*Tanu* / Body), the Moon (*Manas* / Mind), and the Sun (*Ātman* / Soul).

1. **Vector 1: Sudarśana Cakra Alignment & Aspects:**
   * Evaluates bodily proximity ($\le 10^\circ$) and quantified *Sphuṭa Dṛṣṭi* aspects cast onto the three primary degrees:
     * **Ascendant Degree ($100\%$ weight, multiplier $1.00$):** Conjunction up to $+0.35$; direct aspect up to $+0.30$.
     * **Moon Degree ($75\%$ weight, multiplier $0.75$):** Conjunction up to $+0.26$; direct aspect up to $+0.23$.
     * **Sun Degree ($50\%$ weight, multiplier $0.50$):** Conjunction up to $+0.18$; direct aspect up to $+0.15$.
2. **Vector 2: Sensitive Cusp Doors (*Bhāva Madhya* Doorways):**
   * Every house door in equal-arc resonance shares the numerical degree of the Ascendant. Degree proximity is calculated with cyclical $30^\circ$ sign-boundary wrapping (`degree_separation_in_sign(deg1, deg2)`):
     * Proximity to Ascendant degree across any sign: up to $+0.25$.
     * Proximity to Moon degree across any sign: up to $+0.19$.
     * Proximity to Sun degree across any sign: up to $+0.13$.
3. **Vector 3: Ascendant Lord Sovereign Alignment & Aspects:**
   * **Sovereign Vehicle Self-Bonus:** The *Lagna Lord* receives a calibrated $+0.10$ sovereign bonus for piloting the physical vehicle (calibrated so House 1 ownership in Vector 5 is not double-counted).
   * **Influence from Other Planets:** Other planets aspecting the Lagna Lord receive up to $+0.25$ scaled by aspect virūpas; conjunction within $10^\circ$ grants up to $+0.25$.

### Group 2: Aspect Flow Volume (Total Sphuṭa Dṛṣṭi)
4. **Vector 4: Total Aspect Volume (Cast & Received):**
   * **Aspects Cast (Influence):** Sum of all quantifiable aspect units cast onto other planets and the Ascendant degree. *Safeguard: Strictly limited to the classical 7 physical planets.*
   * **Aspects Received (Focal Point):** Sum of all aspect units received from the classical 7 planets. All 9 bodies (including Rāhu and Ketu) can receive aspectual rays.
   * **Scaling:** Total aspect units (where 1 unit = $60\text{ Virūpas}$) contribute $+0.05$ per unit to the opportunity multiplier.

### Group 3: Houses & Stage Sharing
5. **Vector 5: House Prominence & Stage Sharing:**
   * **Kendra Baseline:** 10th house (highest, $+0.40$), 1st house ($+0.35$), 4th house ($+0.25$), 7th house ($+0.25$).
   * **Koṇa Baseline:** 9th house ($+0.30$), 5th house ($+0.25$).
   * **Stage Sharing:** If a house is occupied by multiple planets, the stage points are divided equally by the number of co-occupants:
     $$\text{Stage Score} = \frac{\text{Base House Score}}{\text{Co-occupants Count}}$$
   * **Lordship Prominence:** Houses ruled in $D_1$ grant inherent administrative authority (H10: $+0.15$, H1: $+0.15$, H9: $+0.12$, H4/H7/H5: $+0.10$ each, H11: $+0.05$). Dual-Kendra rulers (e.g. Jupiter for Virgo/Gemini or Mercury for Sagittarius/Pisces) receive independent credit for each house ruled ($+0.20$ total).

### Group 4: Miscellaneous Catalysts & Roots
6. **Vector 6: Dispositor Tree Mechanics (Calibrated Group 4 Scaling):**
   * Direct dispositor of Lagna Lord: $+0.10$.
   * Direct dispositor of the Sun or Moon: $+0.05$ each.
   * **Final Dispositor Deduplication & Ceiling:**
     * Traces terminating dispositor chains for all active classical planets.
     * Prevents double-counting: Planets already credited above (Lagna Lord, Sun, Moon) are removed from the per-dependent scaling.
     * Formula:
       $$\text{Bonus} = \min(0.15, 0.05 + 0.02 \times N_{\text{uncredited}})$$
     * Capped at $+0.15$ maximum so a miscellaneous factor cannot outweigh a central Kendra stage ($+0.40$) or core Ascendant aspect.
   * Solitary own-sign root anchor (*Swakṣetra*): $+0.05$.
7. **Vector 7: Nodal Amplification & Magnetism:**
   * **Planetary Amplification:** Any planet within $12^\circ$ of Rāhu or Ketu receives an amplification bonus up to $+0.25$.
   * **Nodal Magnetism:** Rāhu and Ketu receive up to $+0.20$ for each physical planet they host within $12^\circ$.
8. **Vector 8: Birth Daśā Lord:**
   * The ruler of the starting Vimśottarī Daśā at birth receives a $+0.25$ opportunity boost, dynamically falling back to the Moon's nakshatra ruler if timeline data is absent.

---

## 4. Decoupling of Prominence (Volume) from Dignity (Mood)

Astra enforces a strict structural decoupling between:

* **Vector A: Prominence (Volume / Stage Presence):**
  * Measures *how loud* the planet speaks, how much space it takes up, and how readily its events manifest externally.
  * Derived purely from raw Shadbala and the 8 opportunity factors.
* **Vector B: Dignity & Mood (Moral Quality / Attitude):**
  * Measures *the tone, psychological contentment, and constructive vs. defensive behavior* of the planet.
  * Ingests 20-point *Daśavarga* Viṃśopaka scores, *Dīptādi* avasthās (*Swastha*, *Mudita*, *Khala*), *Bālādi* maturity (*Yuva*, *Mṛta*), and the $-100\%$ to $+100\%$ Net Scale Score.
* **The Golden Rule:** Prominence never distorts dignity, and dignity never distorts prominence. A debilitated planet in the 10th house has massive prominence (loud, visible) but poor dignity mood (agitated, defensive); an exalted planet in the 12th house has high dignity mood (noble, self-reliant) but subdued prominence (quiet, behind the scenes).
