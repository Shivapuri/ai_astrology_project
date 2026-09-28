# 10-Varga Macro Environment Engine (Daśavarga Environmental Weighting)

## Overview & Methodology
The Macro Environment engine evaluates the holistic thermodynamic balance of a natal chart across four foundational dimensions:
1. **Elements (*Mahābhūtas* / Tattvas)**: Fire (*Agni*), Earth (*Pṛthvī*), Air (*Vāyu*), Water (*Jala*).
2. **Modalities (*Guṇas* / Gatis)**: Movable (*Rajas* / *Cara*), Fixed (*Tamas* / *Sthira*), Dual (*Sattva* / *Dvisvabhāva*).
3. **Polarities**: Active / Masculine (Odd signs: Aries, Gemini, Leo, Libra, Sagittarius, Aquarius), Passive / Feminine (Even signs: Taurus, Cancer, Virgo, Scorpio, Capricorn, Pisces).
4. **Ayurvedic Doshas (*Prakṛti*)**: *Pitta* (Fire), *Vāta* (Air), *Kapha* (Earth & Water).

Rather than analyzing only the physical birth chart ($D_1$), the system implements Vic DiCara's exact **10-Varga (Daśavarga)** harmonic model. This integrates the subtle internal layers of consciousness and life experience ($D_2$ through $D_{60}$) with each planet's Parāśarī Prominence.

---

## 1. Daśavarga Weight Distribution ($W_v$)

In Parāśarī Jyotiṣa, the Daśavarga represents the 10 critical divisional charts that govern personal incarnation and destiny:

| Varga | Sanskrit Name | Signification | Weight ($W_v$) |
|---|---|---|---|
| **$D_1$** | *Rāśi* | Physical body, environment, and tangible outer reality | **2.00** |
| **$D_{60}$** | *Ṣaṣṭyaṁśa* | Root karmic blueprint, past-life impressions (*Saṁskāras*), and destiny seeds | **3.33** ($3\frac{1}{3}$) |
| **$D_2$** | *Horā* | Wealth, resources, nourishment, and material sustenance | **1.00** |
| **$D_3$** | *Drekkāṇa* | Courage, vitality, siblings, and energetic initiative | **1.00** |
| **$D_7$** | *Saptāṁśa* | Children, creative legacy, and progeny | **1.00** |
| **$D_9$** | *Navāṁśa* | Soul purpose (*Dharma*), inner fruit, and enduring partnerships | **1.00** |
| **$D_{10}$** | *Daśāṁśa* | Career, profession, social standing, and public action | **1.00** |
| **$D_{12}$** | *Dvādaśāṁśa* | Ancestry, parents, lineage, and inherited genetic habits | **1.00** |
| **$D_{16}$** | *Ṣoḍaśāṁśa* | Vehicles, comforts, inner emotional contentment, and luxuries | **1.00** |
| **$D_{30}$** | *Triṁśāṁśa* | Misfortunes, subconscious shadows, arishta, and inner demons | **1.00** |
| **Total** | | | **13.33** |

$$\sum W_v = 2.0 + 3.33 + (8 \times 1.0) = 13.33$$

---

## 2. Scaled Planetary & Ascendant Contributions

Each entity's sign placement in each divisional chart contributes points scaled by its **Prominence Score** (its opportunity and capacity to make an impact in the native's life):

$$\text{Contribution}(e, v) = \text{Prominence}(e) \times \left( \frac{W_v}{13.33} \right)$$

Where:
- For the 9 Grahas ($g \in \{\text{Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, Ketu}\}$):
  $$\text{Prominence}(g) = \text{prominence\_map}[g]$$
- For the Ascendant (*Lagna*):
  $$\text{Prominence}(\text{Lagna}) = 1.0 \times \text{lagna\_boost} \quad (\text{default boost} = 1.0)$$

---

## 3. Thermodynamic Deviation & Classification

The points accumulated by each category are converted into percentages of the category's total points:

$$\text{Percentage}(c) = \frac{\text{Points}(c)}{\text{Total Category Points}} \times 100\%$$

Each category is then compared against its natural equilibrium baseline:
- **Four Elements:** $100\% / 4 = 25.0\%$
- **Three Modalities:** $100\% / 3 \approx 33.3\%$
- **Two Polarities:** $100\% / 2 = 50.0\%$
- **Three Ayurvedic Doshas:** $100\% / 3 \approx 33.3\%$

$$\text{Deviation} = \text{Percentage} - \text{Baseline}$$

### Classification Thresholds:
- **Surplus:** $\text{Deviation} > +2.0\%$ (Category is over-emphasized, supplying abundant behavioral fuel).
- **Deficit:** $\text{Deviation} < -2.0\%$ (Category is under-represented, requiring conscious cultivation).
- **Balanced:** $-2.0\% \le \text{Deviation} \le +2.0\%$ (Category is in equilibrium).
