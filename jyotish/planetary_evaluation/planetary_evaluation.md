# Vic DiCara's Planetary Evaluation & Positive-to-Negative Scale

## 1. Classical Astrological Philosophy & Purpose

In classical Sanskrit astrology (*Phaladeepika* Chapters 3 & 4), planetary effects do not operate like a naive binary switch (where a planet is simply "good" or "bad"). Instead, astrological archetypes express themselves across a **continuous diagnostic spectrum** from positive to negative:

1. **High Expression (Positive, > +30%):** Constructive, noble, gracious, and flourishing.
2. **Mixed Expression (Neutral / Mundane, -30% to +30%):** Everyday responsibilities, balanced performance, and mixed ups and downs.
3. **Low Expression (Negative, < -30%):** Stressed, conflicted, defensive, or disruptive.

This module implements Vic DiCara's complete diagnostic evaluation framework, providing:
- An **independent diagnostic table** that operates alongside Ernst Wilhelm's Kala calculations without altering or interfering with any existing planetary strengths or avasthas.
- A fully transparent, step-by-step mathematical trace ("how it calculates") for every planet in the horoscope.

---

## 2. The Two Fundamental Pillars: Dignity vs. Strength

The central foundation of Vic DiCara's teaching is separating **Dignity** (*Avastha / Sthana*) from **Strength** (*Bala / Virya*):

| Dimension | Sanskrit Term | What It Measures | Intuitive Analogy |
| :--- | :--- | :--- | :--- |
| **Dignity** | *Avastha / Sthana* | **Moral attitude, character, and mood** (Positive vs. Negative spectrum) | *Is the person a noble, generous benefactor, or a bitter, resentful adversary?* |
| **Strength** | *Bala / Virya* | **Raw physical horsepower, brightness, and kinetic muscle** | *Does the person have armies, capital, and energy, or are they bankrupt and bedridden?* |

### The 4 Archetypal Quadrants Matrix (*Phaladeepika* 4.4–4.5)

Combining Dignity and Strength yields four distinct planetary archetypes:

```
                         THE 4 PLANETARY QUADRANTS
      ┌─────────────────────────────────┬─────────────────────────────────┐
      │ High Dignity + High Strength    │ Low Dignity + High Strength     │
      │ (Exalted / Own Sign + Bright)   │ (Debilitated / Enemy + Vakra)   │
      │ ─────────────────────────────── │ ─────────────────────────────── │
      │ 🌟 Generous King with Armies    │ 💣 Ruthless Armed Dictator      │
      │ Has noble, benevolent intentions│ Has bitter, malevolent intentions│
      │ AND the raw power to manifest   │ AND the brute muscle to force   │
      │ massive, lasting blessings.     │ real damage into reality.       │
      │                                 │ (Worst-case scenario)           │
      ├─────────────────────────────────┼─────────────────────────────────┤
      │ High Dignity + Low Strength     │ Low Dignity + Low Strength      │
      │ (Exalted / Own Sign + Combust)  │ (Debilitated / Enemy + Dim)     │
      │ ─────────────────────────────── │ ─────────────────────────────── │
      │ 🕊️ Sincere Friend with No Money│ 🪰 Toothless Bully Behind Bars  │
      │ Has a wonderful heart and wishes│ Has petty, spiteful intentions, │
      │ the best, but lacks the resources│ but is powerless to execute them.│
      │ or muscle to deliver results.   │ (Easily mitigated nuisance)     │
      └─────────────────────────────────┴─────────────────────────────────┘
```

> [!IMPORTANT]
> **Dignity vs. Situational Scale Score:**
> The vertical axis of the 4 Quadrants measures **Inherent Planetary Dignity** (*Avastha / Sthana* derived from Step 1 Shadvarga and Step 2 Dispositor Host Rescue). It is **not** conflated with external house placements (Step 4) or aspect friction (Step 3). An exalted planet in D1/D9 remains a **High Dignity** planet (e.g. *Generous King*), even if placed in the 8th house; its house placement determines its *situational field* and *expression mode* (e.g., Mixed Expression in a demanding house), but never demotes its inherent moral nobility into an "Armed Dictator".


---

## 3. The 4-Step Diagnostic Algorithm

```
[Step 1: Base Shadvarga Dignity (0% to 100%)]
                    │
                    ▼
[Step 2: Dispositor Anchor & Host Rescue Rule]
                    │
                    ▼
[Step 3: Conjunctions & Aspect Gradients (Drishti)]
                    │
                    ▼
[Step 4: House Field & Dusthana Reversals (6, 8, 12)]
                    │
                    ▼
     FINAL SCALE POSITION (-100% to +100%)
```

---

### Step 1: Base Dignity Across the 6 Subdivisions (Shadvarga)

A planet's mood (*Avastha*) originates in its zodiac sign. Classical astrology examines the planet across the **Shadvarga** (the 6 foundational divisional layers):
1. **D1 (Rashi):** Whole sign (30°), physical reality and general manifestation.
2. **D2 (Hora):** Half-sign (15°), solar/lunar energetic polarity and wealth.
3. **D3 (Drekkana):** One-third sign (10°), kinetic drive, courage, and action.
4. **D9 (Navamsha):** One-ninth sign (3°20′), internal *dharma*, destiny, and soul-level fulfillment.
5. **D12 (Dwadashamsha):** One-twelfth sign (2°30′), ancestral heritage and conditioning.
6. **D30 (Trimshamsha):** Harmonic bounds, inner character and purification.

#### Dignity Percentage Mapping (0% to 100% Scale):
- **Deep Exaltation (*Paramoccha*) / Exaltation (*Uccha*):** `100.0%`
- **Moolatrikona:** `95.0%`
- **Own Sign / Domicile (*Sva-kshetra*):** `90.0%`
- **Great Friend Sign (*Adhi-mitra*):** `80.0%`
- **Friend Sign (*Mitra*):** `60.0%`
- **Neutral Sign (*Sama*):** `50.0%`
- **Enemy Sign (*Shatru*):** `40.0%`
- **Great Enemy Sign (*Adhi-shatru*):** `20.0%`
- **Debilitation (*Neecha*):** `0.0%`

#### Predominance Rule (*Shubhamsha Bahule* - Phaladeepika 3.11):
- Shadvarga Average $D_{\text{shad}} = \frac{1}{6} \sum_{v \in \text{Shadvarga}} \text{Score}(p, v)$.
- **$D_{\text{shad}} \ge 60\%$:** *Shubhamsha Bahule* (Auspicious Predominance) ➔ Long life (*chiranjeevi*) and enduring prosperity (*shrimat*).
- **$40\% \le D_{\text{shad}} < 60\%$:** *Madhyamsha* (Mixed / Balanced).
- **$D_{\text{shad}} < 40\%$:** *Kruramsha Bahule* (Hostile Predominance) ➔ Vulnerability to struggle.

#### Centering to Bipolar Scale:
$$S_{\text{base}} = 2 \times (D_{\text{shad}} - 50.0)$$
- A 50% neutral dignity maps to $0.0$.
- A 100% exalted dignity maps to $+100.0\%$.
- A 0% debilitated dignity maps to $-100.0\%$.

---

### Step 2: The Dispositor Anchor (Host Rescue Rule)

A planet in a sign is a **guest**, and the ruler of that sign is the **host** (*dispositor*).
- **The Alchemical Exception (*Phaladeepika* 3.11):** If a planet occupies a difficult, low-dignity division ($D_{\text{shad}} < 50\%$), but its host is well-dignified ($D_{\text{host}} \ge 65\%$), the host **rescues** the guest!
- Instead of being crushed by hardship, the friction acts as a forge: early hardship develops grit, transforming into commanding authority (*Neecha Bhanga*).
  $$B_{\text{rescue}} = +25.0\% \times \frac{D_{\text{host}}}{100.0}$$
- If the guest already enjoys good dignity ($D_{\text{shad}} \ge 50\%$) and the host is strong ($D_{\text{host}} \ge 65\%$), the host fortifies it: $B_{\text{host}} = +10.0\%$.
- If both guest and host are weak ($< 40\%$), the guest is unsaved: $B_{\text{host}} = -10.0\%$.

---

### Step 3: Conjunctions and Aspect Gradients (*Drishti*)

Planets modify each other's mood through aspects (*Drishti*) and conjunctions along continuous mathematical gradients:
- **Opposition (180° / 7th house):** Full 100% aspect sight.
- **Conjunction (0°):** 100% influence, tapering linearly to 50% at 15° separation and 0% at 30°.
- **The Blind Spot (150° / 6th house distance):** 0% aspect. Continuous gradient between 150° and 180°.
- **Special Full Aspects:** Mars on 4th & 8th signs (90° & 210°), Jupiter on 5th & 9th trines (120° & 240°), Saturn on 3rd & 10th (60° & 270°).

#### Influence Capacities (*Phaladeepika* 4.11):
- **Jupiter (*Guru*):** 100% supreme flaw-destroying and nourishing ray (*Nishesha Dosha-harana*) ➔ $+35.0\% \times I_{\text{Ju}}$.
- **Venus (*Shukra*):** 50% harmonic ray ➔ $+17.5\% \times I_{\text{Ve}}$.
- **Waxing Moon (*Chandra*):** Gentle emotional nourishment ➔ $+12.25\% \times I_{\text{Mo}} \times \text{Paksha Ratio}$.
- **Mercury (*Budha*):** 25% intellectual support ➔ $+8.75\% \times I_{\text{Me}}$.
- **Saturn (*Shani*):** Contraction, delay, and cold pressure ➔ $-35.0\% \times I_{\text{Sa}}$.
- **Mars (*Mangala*):** Aggression, friction, and conflict ➔ $-35.0\% \times I_{\text{Ma}}$.
- **Sun Combustion (*Surya Astangata*):** Within 8°, burns rays ➔ up to $-30.0\% \times (1.0 - \text{dist}/8.0)$.
- **Rahu / Ketu Affliction:** Within 15°, erratic shock ➔ up to $-15.0\% \times (1.0 - \text{dist}/15.0)$.

Net aspect modifier $M_{\text{aspect}} = \sum \text{Benefic Rays} + \sum \text{Malefic Rays}$, clamped to $[-40\%, +40\%]$.

---

### Step 4: House Field (*Bhava*) and Dusthana Reversals

Where the planet resides in the physical chart:
- **Angles (*Kendras*: 1, 4, 7, 10):** Maximum prominence and public execution leverage.
  - 1st House: $+20.0\%$ (Horizon / physical presence, 100% kendra strength)
  - 10th House: $+15.0\%$ (Midheaven / zenith, 75% kendra strength)
  - 7th House: $+10.0\%$ (Descendant / social sphere, 50% kendra strength)
  - 4th House: $+5.0\%$ (Nadir / domestic base, 25% kendra strength)
- **Trines (*Trikonas*: 5, 9):** $+15.0\%$ (Dharma, ethical grace, and creative flow).
- **Growth Houses (*Upachayas*: 3, 11):** $+10.0\%$ (Steady progress and accumulation over time).
- **2nd House:** $+5.0\%$ (Resources and sustenance).
- **Dusthana Reversals (Houses 6, 8, and 12):**
  - Natural benefics in Dusthanas suffer a $-15.0\%$ penalty (too accommodating; vulnerable to exploitation).
  - Natural malefics in Dusthanas gain a $+10.0\%$ shield (crush enemies, endure crisis).
  - **Viparita Raja Yoga (Dusthana Lord in Dusthana):**
    - *Harsha Yoga (6th Lord in 6, 8, 12):* $+20.0\%$ (Cheerfully defeats rivals, invincible immunity).
    - *Sarala Yoga (8th Lord in 6, 8, 12):* $+20.0\%$ (Fearless in crisis, resilient longevity, victory from setbacks).
    - *Vimala Yoga (12th Lord in 6, 8, 12):* $+20.0\%$ (Frugal, spiritually independent, protected from ruinous loss).

---

## 4. Final Synthesis & Formula

$$\text{Net Scale Score} = \text{clamp}(S_{\text{base}} + B_{\text{host}} + M_{\text{aspect}} + M_{\text{house}}, -100.0, +100.0)$$

### The Three Master Lords (*Phaladeepika* 3.11):
1. **Navamsha Lord (*Navamsha-isha*):** Ruler of the rising Navamsha (D9) sign ➔ Governs soul-level happiness, dharma, and internal contentment (*sukhi*).
2. **Drekkana Lord (*Drekkana-isha*):** Ruler of the rising Drekkana (D3) sign ➔ Governs physical stamina, executive courage, and worldly power (*prabhu*).
3. **Lagna Lord (*Lagna-isha*):** Ruler of the physical Ascendant (D1) sign ➔ Governs overall life mastery, fortune, and vitality (*bhagyavan prabhu*).
