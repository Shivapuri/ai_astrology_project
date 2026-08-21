# Vargas Functioning

This document provides a comprehensive technical and astronomical reference for the calculation engine in Astra, detailing the exact algorithms, zodiac frameworks, cusp projection rules, and harmonic mappings used for all 16 **Shodashavarga (Divisional)** charts according to Ernst Wilhelm's "Kala" methodology.

---

## 1. Astronomical Framework & Zodiac Setup

Astra employs a unified, mathematically rigorous astronomical framework powered by the **Swiss Ephemeris (`swisseph`)**:

### A. Tropical Rasis (Signs) for Placements & Vargas
* **Definition**: All base longitudes ($0^\circ \text{ to } 360^\circ$) for Grahas (planets), Lagna (Ascendant), and Bhava Cusps (House Cusps) are calculated on the **Tropical (Sayana) Ecliptic**.
* **Rationale**: Following Ernst Wilhelm's Kala research, Vedic Rasis are fundamentally defined by the Earth-Sun seasonal cycle (Solstices and Equinoxes). Consequently, all 16 divisional charts (Vargas) are derived directly from these Tropical coordinates.
* **Division**: The $360^\circ$ circle is divided into 12 equal $30^\circ$ Rasis (Aries through Pisces).

### B. Sidereal Equatorial Nakshatras (Dhruva Galactic Center)
* **Definition**: Nakshatra positions are computed along the **Equatorial Plane** (Right Ascension, RA) anchored to the **Galactic Center** as the middle of the Nakshatra Mula ($246^\circ 40' = 246.6667^\circ \text{ RA}$).
* **Formula**:
  $$\text{Ayanamsa}_{\text{Eq}} = \text{RA}_{\text{Galactic Center}} - 246.6667^\circ$$
  $$\text{Sidereal RA} = (\text{RA}_{\text{Tropical}} - \text{Ayanamsa}_{\text{Eq}}) \pmod{360^\circ}$$
* **Separation of Concerns**: Nakshatras and Vimshottari Dashas use Equatorial Sidereal coordinates, while Rasis, Cusps, and all Vargas operate on Tropical Ecliptic coordinates.

---

## 2. House System & Cusp Projections

### A. Campanus House System (ADR 001)
* **Computation**: 3D spatial house divisions are computed via Swiss Ephemeris (`swe.houses(jd, lat, lon, b'C')`).
* **High-Latitude Handling**: Campanus accurately reflects celestial sphere division at extreme northern and southern latitudes, correctly generating intercepted signs.

### B. Projection of Cusps into Vargas
* **Individual Cusp Mapping**: In Astra, house cusps (Cusps 1 through 12) are **not** artificially forced to be $30^\circ$ apart in divisional charts. Instead, each of the 12 D1 Campanus cusps is treated as a distinct astronomical point and projected into the Varga using the exact same mathematical formula as the planets.
* **Bhava Chalita Bounds**:
  For each house $i$ in a Varga:
  $$\text{Start}_i = \left(\text{Cusp}_{i-1} + \frac{(\text{Cusp}_i - \text{Cusp}_{i-1}) \pmod{360^\circ}}{2}\right) \pmod{360^\circ}$$
  $$\text{End}_i = \left(\text{Cusp}_i + \frac{(\text{Cusp}_{i+1} - \text{Cusp}_i) \pmod{360^\circ}}{2}\right) \pmod{360^\circ}$$
* **Result**: Planets in a Varga are evaluated against these actual projected house bounds rather than whole sign boundaries, providing genuine Bhava Chalita analysis across all divisional charts.

---

## 3. Mathematical Varga Engine

### Core Formula for Exact Intra-Sign Degrees
Rather than simply assigning a sign index, Astra calculates the **exact continuous fractional degree** ($0^\circ \text{ to } 30^\circ$) of every body within its mapped Varga sign:

1. **Sign Index & Degree in Sign**:
   $$\text{sign\_idx} = \lfloor \text{longitude} / 30 \rfloor \quad (0 = \text{Aries}, \dots, 11 = \text{Pisces})$$
   $$\text{deg} = \text{longitude} \pmod{30}$$
2. **Division Size & Slice Index**:
   $$\text{div\_size} = \frac{30^\circ}{\text{Harmonic}}$$
   $$\text{div\_index} = \lfloor \text{deg} / \text{div\_size} \rfloor$$
3. **Fraction Traversed**:
   $$\text{fraction} = \frac{\text{deg} \pmod{\text{div\_size}}}{\text{div\_size}}$$
4. **Varga Absolute Longitude**:
   $$\text{Varga Longitude} = (\text{Varga Sign Index} \times 30^\circ) + (\text{fraction} \times 30^\circ)$$

---

## 4. Shodashavarga (16 Divisional Charts) Specifications

Below is the complete mathematical definition for all 16 harmonic divisions implemented in [`jyotish/generate_jyotish.py`](file:///Users/hajnaljanos/PycharmProjects/astra/jyotish/generate_jyotish.py):

| Varga | Harmonic | Name | Division Size | Mapping Algorithm & Starting Sign Rule |
| :--- | :--- | :--- | :--- | :--- |
| **D1** | 1 | **Rasi** | $30^\circ00'$ | **Identity**: $\text{Longitude}$ unchanged. |
| **D2** | 2 | **Hora** | $15^\circ00'$ | **Kala Distributed (Opposite Sign)**:<br>• 1st half ($0^\circ-15^\circ$) $\rightarrow$ Same sign ($\text{sign\_idx}$)<br>• 2nd half ($15^\circ-30^\circ$) $\rightarrow$ Opposite sign ($(\text{sign\_idx} + 6) \pmod{12}$) |
| **D3** | 3 | **Drekkana** | $10^\circ00'$ | **Parashari (1-5-9 Triplicity)**:<br>• Decanate 1 ($0^\circ-10^\circ$) $\rightarrow$ Same sign (1st)<br>• Decanate 2 ($10^\circ-20^\circ$) $\rightarrow$ 5th sign from root ($+4$)<br>• Decanate 3 ($20^\circ-30^\circ$) $\rightarrow$ 9th sign from root ($+8$) |
| **D4** | 4 | **Chaturthamsa** | $7^\circ30'$ | **Parashari (1-4-7-10 Kendra)**:<br>• Slices 1 to 4 map to 1st, 4th ($+3$), 7th ($+6$), and 10th ($+9$) signs from root. |
| **D7** | 7 | **Saptamsa** | $4^\circ17'08.57''$ | **Parashari Odd/Even Shift**:<br>• Odd signs: Count starts from root sign ($\text{sign\_idx}$)<br>• Even signs: Count starts from 7th sign ($(\text{sign\_idx} + 6) \pmod{12}$) |
| **D9** | 9 | **Navamsa** | $3^\circ20'$ | **Parashari Elemental Quadriplicities**:<br>• Fire signs (Ar, Le, Sg) $\rightarrow$ Start from Aries ($0$)<br>• Earth signs (Ta, Vi, Cp) $\rightarrow$ Start from Capricorn ($9$)<br>• Air signs (Ge, Li, Aq) $\rightarrow$ Start from Libra ($6$)<br>• Water signs (Cn, Sc, Pi) $\rightarrow$ Start from Cancer ($3$) |
| **D10** | 10 | **Dasamsa** | $3^\circ00'$ | **Parashari Odd/Even Shift**:<br>• Odd signs: Count starts from root sign ($\text{sign\_idx}$)<br>• Even signs: Count starts from 9th sign ($(\text{sign\_idx} + 8) \pmod{12}$) |
| **D12** | 12 | **Dwadasamsa** | $2^\circ30'$ | **Consecutive Zodiac Progression**:<br>• Count starts from root sign ($\text{sign\_idx}$) and progresses continuously 1 through 12. |
| **D16** | 16 | **Shodashamsa** | $1^\circ52'30''$ | **Modality Triplicities**:<br>• Moveable (Chara: 1, 4, 7, 10) $\rightarrow$ Start from Aries ($0$)<br>• Fixed (Sthira: 2, 5, 8, 11) $\rightarrow$ Start from Leo ($4$)<br>• Dual (Dvisvabhava: 3, 6, 9, 12) $\rightarrow$ Start from Sagittarius ($8$) |
| **D20** | 20 | **Vimsamsa** | $1^\circ30'$ | **Modality Shift**:<br>• Moveable $\rightarrow$ Start from Aries ($0$)<br>• Fixed $\rightarrow$ Start from Sagittarius ($8$)<br>• Dual $\rightarrow$ Start from Leo ($4$) |
| **D24** | 24 | **Chaturvimsamsa (Siddhamsa)** | $1^\circ15'$ | **Odd/Even Luminary Origins**:<br>• Odd signs: Start from Leo (Sun, $4$)<br>• Even signs: Start from Cancer (Moon, $3$) |
| **D27** | 27 | **Saptavimsamsa (Nakshatramsa / Bhamsa)** | $1^\circ06'40''$ | **Elemental Quadriplicities**:<br>• Fire signs $\rightarrow$ Start from Aries ($0$)<br>• Earth signs $\rightarrow$ Start from Cancer ($3$)<br>• Air signs $\rightarrow$ Start from Libra ($6$)<br>• Water signs $\rightarrow$ Start from Capricorn ($9$) |
| **D30** | 30 | **Trimsamsa** | *Unequal Slices* | **Parashari Planetary Degree Bands**:<br>**Odd Signs**:<br>• $0^\circ-5^\circ$ ($5^\circ$ Mars) $\rightarrow$ Aries ($0$)<br>• $5^\circ-10^\circ$ ($5^\circ$ Saturn) $\rightarrow$ Aquarius ($10$)<br>• $10^\circ-18^\circ$ ($8^\circ$ Jupiter) $\rightarrow$ Sagittarius ($8$)<br>• $18^\circ-25^\circ$ ($7^\circ$ Mercury) $\rightarrow$ Gemini ($2$)<br>• $25^\circ-30^\circ$ ($5^\circ$ Venus) $\rightarrow$ Libra ($6$)<br>**Even Signs**:<br>• $0^\circ-5^\circ$ ($5^\circ$ Venus) $\rightarrow$ Taurus ($1$)<br>• $5^\circ-12^\circ$ ($7^\circ$ Mercury) $\rightarrow$ Virgo ($5$)<br>• $12^\circ-20^\circ$ ($8^\circ$ Jupiter) $\rightarrow$ Pisces ($11$)<br>• $20^\circ-25^\circ$ ($5^\circ$ Saturn) $\rightarrow$ Capricorn ($9$)<br>• $25^\circ-30^\circ$ ($5^\circ$ Mars) $\rightarrow$ Scorpio ($7$)<br>*Fractional degree is scaled proportionally within the active degree band.* |
| **D40** | 40 | **Khavedamsa** | $0^\circ45'$ | **Odd/Even Polarities**:<br>• Odd signs: Start from Aries ($0$)<br>• Even signs: Start from Libra ($6$) |
| **D45** | 45 | **Akshavedamsa** | $0^\circ40'$ | **Modality Triplicities**:<br>• Moveable $\rightarrow$ Start from Aries ($0$)<br>• Fixed $\rightarrow$ Start from Leo ($4$)<br>• Dual $\rightarrow$ Start from Sagittarius ($8$) |
| **D60** | 60 | **Shashtiamsa** | $0^\circ30'$ | **Consecutive Progression**:<br>• Count starts from root sign ($\text{sign\_idx}$) and cycles through the 12 signs 5 full times ($60 \div 12 = 5$). |

---

## 5. Visual Rendering & Dual-Slot Comparison

* **Rendering Engine ([`jyotish/draw_chart.py`](file:///Users/hajnaljanos/PycharmProjects/astra/jyotish/draw_chart.py))**:
  * **Tropical South Indian (Grid Layout)**: Fixed sign boxes with dynamic planet labels, cusp numbers, and retrogrades.
  * **Tropical North Indian (Diamond Layout)**: Fixed house diamonds with dynamic sign numbers and occupants based on the Varga Lagna.
* **Dual Comparison UI ([`templates/index.html`](file:///Users/hajnaljanos/PycharmProjects/astra/templates/index.html))**:
  * Provides independent **Left Chart** and **Right Chart** dropdown selectors.
  * Allows simultaneous side-by-side inspection of any two Vargas (e.g., D1 Rasi next to D9 Navamsa or D2 Hora).
  * Dynamically updates the corresponding **Equatorial Sidereal Nakshatra** table and **Bhava Chalita House Cusp** breakdown.
