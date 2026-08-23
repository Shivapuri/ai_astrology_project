# AI Documentation: shayana.py (Shayanadi Avasthas)

## Core Astrological & Mathematical Constraints
* **Classical Source:** *Brihat Parashara Hora Shastra*, Chapter 45 (Avasthadhyaya), Verses 30-38.
* **Ernst Wilhelm / Kala Methodology:** *Vault of the Heavens*, Chapter 25.

### 1. Main Avastha Formula
$$\text{Remainder of } \left[ \frac{(\text{Planet Nakshatra No.} \times \text{Planet Serial No.} \times \text{Amsa Factor}) + \text{Lagna Sign No.} + \text{Moon Nakshatra No.} + \text{Ishta Ghati}}{12} \right]$$
*(If the remainder is 0, it represents the 12th Avastha).*

* **Planet Serial Numbers (1-9):**
  `Sun=1, Moon=2, Mars=3, Mercury=4, Jupiter=5, Venus=6, Saturn=7, Rahu=8, Ketu=9`
* **Amsa Factor (Ernst Wilhelm Rule):**
  Strictly uses the **Nakshatra Pada (1, 2, 3, or 4)**. (Not the degree or navamsa index; padas span $3^\circ20'$ and provide full uniform 1-4 coverage for each nakshatra).
* **Lagna Sign Number:**
  Sign number of the Ascendant counted from Aries (`Aries=1, Taurus=2, ..., Pisces=12`).
* **Moon Nakshatra Number:**
  Janma Nakshatra of the Moon (`Ashwini=1, ..., Revati=27`).
* **Ishta Ghati:**
  Elapsed Ghatis (24-minute blocks) from local sunrise to birth moment:
  $$\text{Ishta Ghati} = \lceil \frac{\text{elapsed minutes from sunrise}}{24.0} \rceil$$

### 2. The 12 Shayanadi States
1. **Shayana** (Lying Down / Resting)
2. **Upaveshana** (Sitting)
3. **Netrapani** (Hand on Eye / Eyes & Hands)
4. **Prakashana** (Illuminating / Shining)
5. **Gamana** (Departing / Moving)
6. **Agamana** (Arriving / Returning)
7. **Sabhavasati** (In Assembly / Council)
8. **Agama** (Acquiring / Gathering)
9. **Bhojana** (Eating / Feasting)
10. **Nrityalipsa** (Longing to Dance / Artistic)
11. **Kautuka** (Eagerness / Joyful Curiosity)
12. **Nidra** (Slumber / Deep Sleep)

### 3. Cheshtadi Sub-State Formula
$$\text{Step 1: } \text{Sub-Sum}_1 = ((\text{Avastha Index})^2 + \text{Varnamashka Value}) \pmod{12}$$
$$\text{Step 2: } \text{Sub-Sum}_2 = \text{Sub-Sum}_1 + \text{Planet Kshepaka}$$
$$\text{Step 3: } \text{Remainder} = \text{Sub-Sum}_2 \pmod 3$$

* **Varnamashka (Name Sound Value 1-5):**
  - Group 1: `A, AA, K, CH, T, P, Y, SH, Q`
  - Group 2: `I, EE, KH, CHH, TH, F, PH, R`
  - Group 3: `U, OO, G, J, D, B, L, S, Z`
  - Group 4: `E, AI, GH, JH, DH, BH, V, W, H`
  - Group 5: `O, AU, NG, NY, N, M`
* **Planet Kshepakas (Additive Constants):**
  `Sun=5, Moon=2, Mars=2, Mercury=3, Jupiter=5, Venus=3, Saturn=3, Rahu=4, Ketu=4`
* **Sub-State Classification:**
  - `Remainder = 1` $\to$ **Drishti** (Apparent / Medium effect, 50% strength)
  - `Remainder = 2` $\to$ **Cheshta** (Active / Great effect, 100% strength)
  - `Remainder = 0` $\to$ **Vicheshta** (Motionless / Minimal effect, 10% strength)
