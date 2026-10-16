# Houses of Life (Vic DiCara / Phaladīpikā Chapter 15 Evaluation System)

## 1. Overview & Foundational Mathematical Architecture

The **Houses of Life** system is an advanced quantitative astrological engine developed by Vic DiCara, rooted in Chapter 15 of Mantreśvara's classical authority *Phaladīpikā*. It provides a rigorous, multi-stage evaluation of the 12 houses (*Bhāvas*) and 7 classical physical planets (*Grahas*): Sun, Moon, Mars, Mercury, Jupiter, Venus, and Saturn.

Unlike qualitative traditions that rely on broad rules of thumb, Houses of Life computes continuous mathematical scores across nine distinct phases without rounding intermediate arc-minutes or arc-seconds.

$$\text{Composite House Score}_H = \frac{\text{Basic}_H + \text{Lord}_H + \text{Relative}_H + \text{Wall}_H + \text{Yoga}_H}{5.0}$$

---

## 2. Phase-by-Phase Computational Workflow

### Phase 1: Chart Geometry & Sensitive House Cusps

1. **Whole Sign House Framework (*Rāśi Bhāva*):**
   * The zodiac sign containing the Ascendant (*Lagna*) forms the 1st House.
   * Subsequent signs in natural zodiacal order constitute Houses 2 through 12.
   * Each house encompasses a complete $30^\circ$ sign boundary.

2. **Sensitive Cusp Degree ("The Front Door"):**
   * The exact degree of the Ascendant within its sign ($\lambda_{\text{Asc}} \pmod{30^\circ}$) establishes the sensitive cusp center for all 12 houses.
   * **Cusp Longitude Formula:**
     $$\text{Cusp}_H = \left( (S_{\text{Asc}} + H - 1) \times 30^\circ + (\lambda_{\text{Asc}} \pmod{30^\circ}) \right) \pmod{360^\circ}$$
     where $S_{\text{Asc}} \in \{0, \dots, 11\}$ is the 0-indexed sign of the Ascendant, and $H \in \{1, \dots, 12\}$.

---

### Phase 2: Planetary Functional Nature Quantification ($F_P$)

Derived verbatim from *Phaladīpikā* Chapter 15, the functional nature of each planet relative to the Ascendant is quantified via four sequential rules:

#### 1. Mūlatrikoṇa (Root) vs. Regular Domicile Definitions
* Dual-ruling planets assign the **male (odd) sign** as Mūlatrikoṇa root and the **female (even) sign** as regular domicile.
* **Sun:** Leo (male Mūlatrikoṇa).
* **Exception 1 (Moon):** As the Moon owns no male sign, its exaltation sign **Taurus** acts as its Mūlatrikoṇa root, while **Cancer** is its regular domicile.
* **Exception 2 (Mercury):** Because Mercury derives higher strength from femininity, **Virgo** (female) serves as its Mūlatrikoṇa root, while **Gemini** (male) is regular domicile.
* **Mars:** Aries (Mūlatrikoṇa), Scorpio (Domicile).
* **Jupiter:** Sagittarius (Mūlatrikoṇa), Pisces (Domicile).
* **Venus:** Libra (Mūlatrikoṇa), Taurus (Domicile).
* **Saturn:** Aquarius (Mūlatrikoṇa), Capricorn (Domicile).

#### 2. The Four Sequential Rules
* **Rule 1 (1st House Lord):**
  If planet $P$ rules House 1, assign $F_P = +3$ and **STOP** (skip Rules 2, 3, and 4).
  * *Unblemished Sovereign:* Even if the 1st lord is a natural malefic or simultaneously rules a Dusthāna (e.g., Mars for Aries Lagna ruling 8th Scorpio, or Saturn for Capricorn Lagna), it receives a flat $+3$.
* **Rule 2 (Trine Lords — Houses 5 and 9):**
  * Mūlatrikoṇa sign on House 5 or 9: $+2$.
  * Regular domicile sign on House 5 or 9: $+1$.
* **Rule 3 (Dusthāna Lords — Houses 6, 8, and 12):**
  * Mūlatrikoṇa sign on House 6, 8, or 12: $-2$.
  * Regular domicile sign on House 6, 8, or 12: $-1$.
  * *Simultaneous Trine & Dusthāna Ownership:* Scores are summed side-by-side (e.g., Jupiter for Aries Lagna gets $+2$ for H9 Sagittarius and $-1$ for H12 Pisces).
  * *Moon Dual-Dusthāna Exception (Sagittarius Ascendant):* When Taurus is House 6 and Cancer is House 8, the Mūlatrikoṇa root and domicile are evaluated as an **OR** condition rather than cumulative, assigning Moon $-2$ (not $-3$).
* **Rule 4 (Inherent Natural Temperament):**
  * Extreme natural benefics (Jupiter, Venus): $+1$.
  * Extreme natural malefics (Mars, Saturn): $-1$.
  * Mild/neutral planets (Sun, Moon, Mercury): $0$.

#### 3. Net Functional Classification
$$F_P = \begin{cases} +3 & \text{if } P \text{ rules House 1} \\ \text{Score}_{\text{Trine}} + \text{Score}_{\text{Dusthāna}} + \text{Score}_{\text{Inherent}} & \text{otherwise} \end{cases}$$
* $F_P > 0 \implies$ Functionally Benefic.
* $F_P < 0 \implies$ Functionally Malefic.
* $F_P = 0 \implies$ Functionally Neutral.

---

### Phase 3: Rāśi Dignity Scale ($d_P$) & Universal Scaling Law

#### 1. D1 Rāśi Dignity Scale ($d_P \in [-1.0, +1.0]$, $D_{\text{pct}} \in [-100, +100]$)
* **Exaltation (*Uccha*):** $+1.0$ ($+100\%$)
* **Mūlatrikoṇa:** $+0.9$ ($+90\%$)
* **Domicile (*Svakṣetra*):** $+0.8$ ($+80\%$)
* **Very Friendly (*Adhi Mitra*):** $+0.6$ ($+60\%$)
* **Friendly (*Mitra*):** $+0.4$ ($+40\%$)
* **Neutral (*Sama*):** $0.0$ ($0\%$)
* **Inimical (*Śatru*):** $-0.4$ ($-40\%$)
* **Very Inimical (*Adhi Śatru*):** $-0.7$ ($-70\%$)
* **Debilitated (*Nīca*):** $-1.0$ ($-100\%$)

#### 2. Universal Dignity-Scaling Law (`scale_by_dignity`)
Scales any base impact $B \ge 0$ by dignity $d_P$ according to functional nature $F$:
* **Functionally Positive ($F > 0$):**
  * $d_P \ge 0 \implies S = B \times (1.0 + d_P)$ (Up to $2\times$ intensification).
  * $d_P < 0 \implies S = B \times (1.0 - \frac{|d_P|}{2.0})$ (Diminished by at most half; never flips negative).
* **Functionally Negative ($F < 0$):**
  * $d_P \le 0 \implies S = B \times (1.0 + |d_P|)$ (Bad mood intensifies malice up to $2\times$).
  * $d_P > 0 \implies S = B \times (1.0 - \frac{d_P}{2.0})$ (Good mood mitigates malice by up to half).
* **Functionally Neutral ($F = 0$):**
  * $S = B \times (1.0 + |d_P|) \times \text{sgn}(d_P)$

---

### Phase 4: Conjunctions, Cross-Border Halving & Cusp Dominance

1. **Degree-Specific Aspects (*Sphuṭa Dṛṣṭi*):**
   * Expressed on a $0\%$ to $100\%$ scale: $\frac{\text{Virūpas}}{60.0} \times 100.0$.
2. **Conjunction Proximity:**
   * Within $30^\circ$: $C_{\text{raw}} = \max\left(0.0, \left(1.0 - \frac{\Delta\lambda}{30.0}\right) \times 100.0\right)$.
3. **Cross-Border Attenuation:**
   * If a conjunction spans across a sign boundary, potency is halved ($\times 0.5$).
4. **Multi-Planet Cusp Dominance ("Potency Stealing"):**
   * Co-occupants of the same Whole Sign house share cusp alignment. The closer planet $P_{\text{near}}$ absorbs conjunction points from farther co-occupants $P_{\text{far}}$:
     $$\Delta_{\text{steal}} = C_{\text{far}} \times \frac{C_{\text{near}}}{C_{\text{near}} + C_{\text{far}}}$$
     $$C_{\text{near, final}} = C_{\text{near}} + \Delta_{\text{steal}}, \qquad C_{\text{far, final}} = C_{\text{far}} - \Delta_{\text{steal}}$$

---

### Phase 5: Comprehensive Planetary Assessment (5 Factors)

1. **Dignity ($D_{\text{pct}, P}$):** D1 dignity percentage in $[-100, +100]$.
2. **Combined Influences ($\text{Inf}_P$):**
   $$\text{Inf}_P = \sum_{Q \neq P} \text{sgn}(F_Q) \cdot I_{Q \to P} \cdot (1.0 + |d_Q|)$$
3. **Cusp Alignment ($\text{Align}_P$):**
   * Capped dominance-adjusted conjunction $\min(100.0, C_{P, \text{final}})$ multiplied by:
     * Prominent houses ($1, 4, 5, 9, 10$): $\times 1.50$
     * Regular houses ($2, 7, 11$): $\times 1.00$
     * Hidden houses ($3, 6, 8, 12$): $\times (-1.00)$
     * *Exception:* Dusthāna lord in any Dusthāna ($6, 8, 12$) or 3rd lord in House 3 receives $\times (+1.00)$.
4. **Bhāva Sandhi ($\text{Sandhi}_P$):**
   * Within $4.0^\circ$ of either sign border:
     $$\text{SandhiPenalty}_P = \max\left(0.0, 1.0 - \frac{\Delta_{\text{border}}}{4.0}\right)$$
5. **Combustion & Solar Gain:**
   * For $P \neq \text{Sun}$: If $\Delta_{\text{Sun}} < \text{Orb}_P$, $\text{CombLoss}_P = 1.0 - \frac{\Delta_{\text{Sun}}}{\text{Orb}_P}$.
   * Multiplier for $P$: $(1.0 - \text{CombLoss}_P)$.
   * For Sun: $\text{SolarGain} = \sum_{Q \neq \text{Sun}} \text{CombLoss}_Q$, multiplier $= (1.0 + \text{SolarGain})$.
6. **Planetary Synthesis:**
   $$\text{BaseScore}_P = \frac{D_{\text{pct}, P} + \text{Inf}_P + \text{Align}_P}{3.0}$$
   $$\text{FinalScore}_P = \text{BaseScore}_P \times (1.0 - \text{SandhiPenalty}_P) \times \text{CombMultiplier}_P$$

---

### Phase 6: Basic House Condition — Direct Evaluation

For each house $H \in \{1, \dots, 12\}$:
1. Impact $I_{P \to H} = \max(\text{AspectPct}_{P \to \text{Cusp}_H}, \text{DominanceConjPct}_{P \to H})$.
2. Functional Nature $F_{P, H}$:
   * If $P$ rules House $H$: $F_{P, H} = +2$ (House Lord override).
   * Otherwise: $F_{P, H} = F_P$.
3. Scaled Signed Impact:
   $$\text{Impact}_{P \to H} = \begin{cases} \text{scale\_by\_dignity}(I_{P \to H}, d_P, F_{P, H}) \times F_{P, H} & \text{if } F_{P, H} \neq 0 \\ \text{scale\_by\_dignity}(I_{P \to H}, d_P, 0) & \text{if } F_{P, H} = 0 \end{cases}$$
   *(Note: `scale_by_dignity` already incorporates the sign of $d_P$ when $F = 0$, preventing double negation).*
4. House Average:
   $$\text{BasicHouseScore}_H = \frac{1}{7} \sum_{P=1}^{7} \text{Impact}_{P \to H}$$

---

### Phase 7: Relative House Technique — *Bhavāt Bhavam* (*Phaladīpikā* 15.2 & 15.4)

Treats each target house $H$ as House 1:
1. Relative house of planet $P$: $R_{P, H} = ((\text{House}_P - H) \pmod{12}) + 1$.
   * **Kendra-Koṇa + 2nd (KK Group):** Relative houses $2, 4, 5, 7, 9, 10$.
   * **Dusthāna Group:** Relative houses $6, 8, 12$.
   * Houses $1, 3, 11$ are skipped.
2. Relative Functional Nature $F_{P \mid H}$: Re-computed with House $H$ as 1st house. If a planet has a raw relative functional score of $0$ (neutral), its dignity unit $d_P$ serves as its functional nature, scaled by $50.0$ points per unit.
3. KK planets contribute their dignity-scaled score.
4. Dusthāna relative malefics generate negative points; mitigated by average aspect percentage cast onto them by relative benefics ($\overline{\text{Mit}}$). Relative benefics in Dusthānas contribute $0$ and do not increment $N_{\text{active}}$.
5. Divided by active planet count $N_{\text{active}}$.

---

### Phase 8: Quantified House Walls — *Kartarī Yoga*

* Evaluates physical planets within $(0^\circ, 30^\circ)$ before and after $\text{Cusp}_H$.
* Base quality: $+200$ for house lord, $D_{\text{pct}}$ if neutral, $F_P \times 100$ otherwise, scaled by dignity.
* Proximity weighted:
  $$\text{WallScore}_H = \text{Quality}_{\text{before}} \left(1 - \frac{\Delta_{\text{before}}}{30}\right) + \text{Quality}_{\text{after}} \left(1 - \frac{\Delta_{\text{after}}}{30}\right)$$

---

### Phase 9: Numerical House Yoga Scoring (4 Structural Yogas)

1. **Parivartana Yoga (House Exchange):**
   * $\frac{\text{Val}(X) + \text{Val}(Y)}{2.0}$ credited to occupied houses $X$ and $Y$ (or $+150$ each if same category).
2. **Rāja Yoga:**
   * Trine + Trine, Trine + Kendra, or Nodal Kendra/Trine combinations. Conjunction requires same Whole Sign house; mutual aspect threshold is $\ge 36.0$ Virūpas ($60\%$).
   * $+100$ points credited per participating body to occupied house and each owned house (without set deduplication).
3. **Mahāpuruṣa (and Inverse Mahāpuruṣa):**
   * Any physical planet in Kendra $1, 4, 7, 10$ awards its $D_{\text{pct}, P}$ to occupied Kendra and to each owned house.
4. **Daridra Yoga (and Dusthāna Reversal):**
   * House lord combined with Dusthāna lord ($6, 8, 12$). 1st House Lord possesses immunity (its secondary Dusthāna ownership is unblemished and does not trigger Daridra).
   * $-100$ points per participating planet to occupied house and owned houses.
   * *Reversal:* If two Dusthāna lords combine, or combine in a Dusthāna, $+100$ points to Dusthāna houses, $-100$ to non-Dusthāna houses.

---

## 3. Qualitative Health Tiers (`synthesis.health_rating`)

* **$\ge +100.0$:** `"Exceptional / Off the Chart"` (`classical_tier`: `"Puṣṭa"`)
* **$+25.0 \text{ to } +99.9$:** `"Flourishing / Fortified"` (`classical_tier`: `"Puṣṭa"`)
* **$-20.0 \text{ to } +24.9$:** `"Mixed / Resilient"` (`classical_tier`: `"Miśra"`)
* **$-99.9 \text{ to } -20.1$:** `"Strained / Challenged"` (`classical_tier`: `"Hīna"`)
* **$\le -100.0$:** `"Severely Afflicted / Obstructed"` (`classical_tier`: `"Hīna"`)
