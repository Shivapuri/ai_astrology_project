# Houses of Life (Vic DiCara / Phaladīpikā Chapter 15 Evaluation System)

## 1. Overview & Foundational Mathematical Architecture

The **Houses of Life** system is an advanced quantitative astrological engine developed by Vic DiCara, rooted in Chapters 3, 4, 6, and 15 of Mantreśvara's classical authority *Phaladīpikā*. It provides a rigorous, multi-stage evaluation of the 12 houses (*Bhāvas*) and 7 classical physical planets (*Grahas*): Sun, Moon, Mars, Mercury, Jupiter, Venus, and Saturn, alongside the nodal axes (Rāhu and Ketu).

Unlike qualitative traditions that rely on broad rules of thumb, Houses of Life computes continuous mathematical scores across distinct phases without rounding intermediate arc-minutes or arc-seconds:

$$\text{Composite House Score}_H = 0.30\,\text{Basic}_H + 0.30\,\text{Lord}_H + 0.15\,\text{Relative}_H + 0.10\,\text{Kāraka}_H + 0.10\,\text{Yoga}_H + 0.05\,\text{Wall}_H$$

*(Note: When a house is unwalled ($\text{is\_walled} = \text{False}$), the $5\%$ wall weight is redistributed proportionally across the remaining active components by dividing by $0.95$).*

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

Derived from *Phaladīpikā* Chapter 15 and *BPHS* Chapter 34, the functional nature of each planet relative to the Ascendant is quantified via sequential rules with *Yogakāraka*, *Kendrādhipatya*, and *Svakṣetra* adjustments:

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
  * *Svakṣetra Dual-Lordship Override (Phaladīpikā 15.29):* When planet $P$ physically occupies one of its own signs ($P_{\text{sign}} \in \{\text{MT}, \text{Dom}\}$) corresponding to a non-Dusthāna house ($H \notin \{6, 8, 12\}$), its secondary Dusthāna score is set to $0$ (`dusthana_score = 0`).
* **Rule 4 (Inherent Natural Temperament & BPHS Ch. 34 Adjustments):**
  * Natural benefics: `Jupiter` ($+1.0$), `Venus` ($+1.0$).
  * Natural malefics: `Mars` ($-1.0$), `Saturn` ($-1.0$).
  * `Sun`: $-0.5$ (mild *Krūra* / natural malefic so it properly triggers Upacaya rules in $3, 6, 11$).
  * `Moon`: Evaluated via *Pakṣa Bala* (brightness elongation $\Delta_{\text{Moon-Sun}} \in [0^\circ, 180^\circ]$ per *Phaladīpikā* Ch. 4 & 15.1):
    $$\text{PakṣaFactor} = \frac{\Delta_{\text{Moon-Sun}}}{180.0} \in [0.0, 1.0], \qquad \text{Inherent}_{\text{Moon}} = -0.5 + 1.5 \times \text{PakṣaFactor}$$
    (ranges from $-0.5$ at New Moon to $+1.0$ at Full Moon; defaults to $+0.5$ if positions are absent).
  * `Mercury`: Defaults to $+0.5$ (natural benefic), unless within $10^\circ$ of a natural malefic (`Mars`, `Saturn`, `Rahu`, `Ketu`) in the same sign, in which case it assumes $-0.5$.
  * **Supreme Rāja Yogakāraka Bonus (*BPHS* 34.40–43):** If a planet simultaneously owns a Kendra ($4, 7, 10$) and a Trine ($5, 9$) (e.g., Mars for Cancer/Leo Lagna, Saturn for Taurus/Libra Lagna), its natural maleficence is waived and it receives $+1$ (`inherent_score = max(0, inherent_score) + 1`).
  * **Māraka & Triṣaḍāya Preservation:** Natural malefics owning a Kendra without a Trine retain their inherent maleficence ($-1.0$).

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
  * $d_P < 0 \implies S = B \times (1.0 - 0.80 \times |d_P|)$ (Severe debilitation retains only $0.20\times$ good results per *Phaladīpikā* 15.18).
* **Functionally Negative ($F < 0$):**
  * $d_P \le 0 \implies S = B \times (1.0 + |d_P|)$ (Bad mood intensifies malice up to $2\times$).
  * $d_P > 0 \implies S = B \times (1.0 - \frac{d_P}{2.0})$ (Good mood mitigates malice by up to half).
* **Functionally Neutral ($|F| \le 0.15$):**
  * Proportional continuous scaling: $S = B \times d_P$ (where $d_P > 0$ yields positive support and $d_P < 0$ yields negative strain, without artificial step-jumps or double negation).

---

### Phase 4: Conjunctions, Cross-Border Halving & Cusp Dominance

1. **Degree-Specific Aspects (*Sphuṭa Dṛṣṭi*):**
   * Expressed on a $0\%$ to $100\%$ scale: $\frac{\text{Virūpas}}{60.0} \times 100.0$.
   * **Classical Whole Sign Distance Gating:** Raw continuous aspect virūpas from `aspects.get_graha_drishti` are strictly gated by Whole Sign distance between the aspecting planet and the target cusp:
     * If the planet is in the 1st (same sign), 2nd, 6th, or 12th sign from the cusp, `virupas = 0.0` (planets do not aspect adjacent or 6th signs classically).
     * If in the 8th sign and the planet is not Mars, `virupas = 0.0` (special 8th aspect belongs strictly to Mars in Parāśara and Phaladīpikā; non-Mars planets cast zero aspect onto 8th sign).
2. **Conjunction Proximity:**
   * Within $30^\circ$: $C_{\text{raw}} = \max\left(0.0, \left(1.0 - \frac{\Delta\lambda}{30.0}\right) \times 100.0\right)$.
3. **Cross-Border Attenuation:**
   * If a conjunction spans across a sign boundary, potency is halved ($\times 0.5$).
4. **Multi-Planet Cusp Dominance ("Potency Stealing"):**
   * Co-occupants of the same Whole Sign house share cusp alignment. The closer planet $P_{\text{near}}$ absorbs conjunction points from farther co-occupants $P_{\text{far}}$:
     $$\Delta_{\text{steal}} = C_{\text{far}} \times \frac{C_{\text{near}}}{C_{\text{near}} + C_{\text{far}}}$$
     $$C_{\text{near, final}} = C_{\text{near}} + \Delta_{\text{steal}}, \qquad C_{\text{far, final}} = C_{\text{far}} - \Delta_{\text{steal}}$$

---

### Phase 5: Comprehensive Planetary Assessment (Quality vs. Prominence)

1. **Multi-Varga Dignity Blending ($d_P$):**
   * Incorporates D1 and D9 (*Navāṃśa*, *Phaladīpikā* 3.4 & 3.11).
   * **Vargottama** ($S_{\text{D1}} == S_{\text{D9}}$): Effective dignity is floored at $\max(d_{\text{D1}}, 0.80)$ (acting as own sign).
   * Otherwise: $d_P = 0.65 \times d_{\text{D1}} + 0.35 \times d_{\text{D9}}$.
   * *Active across all house phases:* This composite dignity unit $d_P$ is passed into and utilized across Phase 6 (Basic House Conditions), Phase 7 (Relative Houses), and Phase 8 (House Walls).
2. **Directional Strength (*Digbala*, *Phaladīpikā* Ch. 4):**
   * Canonical directional strength based on peak house $H_{\text{peak}}$ (Jupiter/Mercury in H1, Sun/Mars in H10, Saturn in H7, Moon/Venus in H4):
     $$\text{DigFactor}_P = 1.0 - \frac{\text{shortest\_house\_dist}(H_P, H_{\text{peak}})}{3.0} \in [-1.0, +1.0]$$
     $$\text{DigBalaPts}_P = 20.0 \times \text{DigFactor}_P \times \text{clamp}(\text{ShadbalaRatio}_P, 0.75, 1.25)$$
3. **Intrinsic Quality ($\text{QualityBase}_P$):**
   * Combines Dignity, Incoming Aspects, and Digbala without raw cusp proximity additions:
     $$\text{QualityBase}_P = 0.50 \times D_{\text{pct}, P} + 0.35 \times \text{Inf}_P + 0.15 \times \text{DigBalaPts}_P$$
4. **Incoming Influences & Nodal Afflictions / Eclipses (*Grahaṇa*):**
   * **Incoming Planetary Rays:** When $|F_Q| \le 0.15$, signed impact adopts $S = B \times d_Q$ directly without double multiplication.
   * When Rāhu or Ketu is in the same sign within $15.0^\circ$ of planet $P$:
     * Conjunction intensity: $\text{node\_conj} = \left(1.0 - \frac{\Delta\lambda_{\text{node}}}{15.0}\right) \times 100.0$.
     * **Luminaries (Sun, Moon):** Subtract $0.85 \times \text{node\_conj}$. An eclipse strain factor $\text{eclipse\_loss} = 0.15 \times \left(1.0 - \frac{\Delta\lambda_{\text{node}}}{15.0}\right)$ attenuates intrinsic quality when $\Delta\lambda \le 12.0^\circ$. For the Sun placed in an Upacaya house ($3, 6, 11$) with composite dignity $d_P \ge 0.4$, both $\text{node\_pen}$ and $\text{eclipse\_loss}$ are halved.
     * **Other Planets:** Subtract $0.50 \times \text{node\_conj}$ (halved in Upacayas $3, 6, 11$).
   * **Dusthāna Enemy Conjunction Attenuation:** Conjunctions with a Dusthāna lord ($6, 8, 12$) who is a natural enemy are attenuated by $0.50\times$.
5. **House Placement & Cusp Proximity Prominence Multiplier:**
   * Prominent houses ($1, 4, 5, 9, 10$): Base $1.25\times$.
   * Regular houses ($2, 7, 11$): Base $1.00\times$.
   * Hidden houses ($3, 6, 8, 12$): Base $0.75\times$ to $1.00\times$.
   * **Afflicted Dusthāna Lord Penalty:** If a lord of $6, 8, 12$ sits in a Dusthāna with $d_{\text{D1}} < 0$, it receives a $0.70\times$ placement penalty.
   * **Cusp Proximity Factor:**
     $$\text{CuspProxFactor}_P = 0.80 + 0.40 \times \left(\frac{\text{CappedBase}_P}{100.0}\right)$$
     $$\text{EffectiveMultiplier}_P = \text{BaseMultiplier}_P \times \text{CuspProxFactor}_P$$
   * **Vilagna Protection (*Phaladīpikā* 3.9):** If a planet occupies House 1 with $\text{QualityBase} < 0$, its negative dignity strain is softened by $0.50 \times \text{CuspProxFactor}$.
6. **Bhāva Sandhi ($\text{Sandhi}_P$):** Within $4.0^\circ$ of either sign border.
7. **Combustion & Solar Gain:** Proximity to Sun within combustion orb.
8. **Sign-Safe Synthesis:** Produces `final_assessment_score`.

---

### Phase 6: Basic House Condition — Direct Evaluation

For each house $H \in \{1, \dots, 12\}$:
1. Impact $I_{P \to H} = \max(\text{AspectPct}_{P \to \text{Cusp}_H}, \text{DominanceConjPct}_{P \to H})$.
   * Non-occupant aspects with $I_{P \to H} < 25.0$ are filtered out ($0.0$).
2. Dignity $d_P$ and Effective Functional Nature $F_{P, H}$:
   * **House Lord:** $F_{\text{eff}} = 2.0$.
   * **Non-Lord Planets:** Blend $50\%$ Lagna functional nature + $50\%$ natural temperament ($\times 2.0$) $\pm 0.50$ friendship to house lord:
     $$F_{\text{eff}} = 0.50 \times F_{\text{lagna}} + 0.50 \times (\text{NatT} \times 2.0) \pm 0.50 \text{ (friendship to lord)}$$
3. **Condition-Gating (*Amūḍha-Hīnāḥ*, *Phaladīpikā* 15.1, 15.5):**
   $$\text{ConditionIntegrity} = (1.0 - 0.75 \times \text{CombLoss}_P) \times (1.0 - 0.50 \times \text{SandhiPen}_P)$$
   * Benefic impacts ($\text{signed\_impact} > 0$) are multiplied by $\text{ConditionIntegrity}$.
   * **Dusthāna Enemy Attenuation (*Arinīca-Mūḍha*):** If a planet has negative D1 dignity ($d_{\text{D1}} < 0$), its positive cusp rays are attenuated by $0.55\times$, and by an additional $0.75\times$ if occupying a Dusthāna ($6, 8, 12$), preventing afflicted planets from projecting runaway positive points.
   * Malefic impacts ($\text{signed\_impact} < 0$) are intensified by combustion: $(1.0 + 0.35 \times \text{CombLoss}_P) \times (1.0 - 0.30 \times \text{SandhiPen}_P)$.
4. **Upacaya (3, 6, 11) Malefic Occupant Rule (*Phaladīpikā* 15.18):**
   When a natural malefic (Sun, Mars, Saturn) occupies an Upacaya house as a non-lord occupant, its negative cusp impact is converted to a positive resilience boost:
   $$\text{Impact}_{P \to H} = |\text{scaled\_i}| \times 0.35$$
5. **Rāhu & Ketu Cusp Impact (*Phaladīpikā* 15.8):**
   * If in the same sign as the cusp: $C_{\text{node}} = \max\left(35.0, \left(1.0 - \frac{\text{dist}}{30.0}\right) \times 100.0\right)$.
   * If in adjacent sign within $15^\circ$ of cusp: $C_{\text{node}} = 0.50 \times \left(1.0 - \frac{\text{dist}}{30.0}\right) \times 100.0$ (halved cross-border, no $35\%$ floor).
   * Upacaya houses ($3, 6, 11$): $+0.35 \times C_{\text{node}}$.
   * Non-Upacaya houses: $-0.60 \times C_{\text{node}} \times \text{MitFactor}$ (where $\text{MitFactor} = 0.50$ if node is dignified or aspected/conjoined by Jupiter or Venus; $1.00$ otherwise).
6. **Active Divisor Floor:**
   $$\text{EffDivisor}_H = \max(3.0, \text{ActiveWeights}_H)$$
   Scores clamped within $[-120.0, +120.0]$.

---

### Phase 7: Relative House Technique — *Bhavāt Bhavam* (*Phaladīpikā* 15.2–15.5)

Treats each target house $H$ as House 1:
1. **House Lord Relative Placement ($R_{\text{Lord}, H}$):**
   * **Relative 1, 2, 4, 5, 7, 9, 10 (*Kendra / Trikoṇa / 2nd*, 15.2):** Weight $1.0$, plus degree-aspect proximity bonus when close to exact $0^\circ, 90^\circ, 120^\circ, 180^\circ$ aspect angles.
   * **Relative 3, 11 (*Upacaya*, 15.18):** Weight $0.50$.
   * **Relative 6, 8, 12 (*Bhāva-Nāśa*, 15.3 & 15.5):**
     * If the Lord is in its other own sign (*Svakṣetra* per 15.29), penalty is $0.0$.
     * Otherwise, base penalty: $-110.0$ in R8, $-80.0$ in R12, $-70.0$ in R6.
     * Halved ($0.50\times$) if the Lord is dignified ($d_P \ge 0.4$) and uncombust; amplified if debilitated or combust.
     * Benefic aspects onto the Lord mitigate this penalty.
2. **Non-Lord Planets in Relative Houses:**
   * Relative 2, 4, 5, 7, 9, 10: Weight $1.0$.
   * Relative 11: Weight $0.50$; Relative 3: Weight $0.40$ (secondary Upacaya growth support).
   * Relative 1: $+0.50\times$ if $F_{\text{rel}} > 0$; $-0.75\times$ if $F_{\text{rel}} < 0$.
   * Relative 6, 8, 12: Adds to raw Dusthāna penalty if $F_{\text{rel}} < 0$.
3. **Benefic Mitigation:** Malefics in relative Dusthānas are mitigated strictly by direct aspects from relative benefics.
4. **Denominator Floor:** $\text{denom} = \max(3.0, N_{\text{active}})$.

---

### Phase 7B: Bhāva Kāraka & Kāraka Lagna Engine (*Phaladīpikā* 15.5–6, 15.15–20, 15.25)

Every house evaluation incorporates the condition and perspective of its natural representative (*Bhāva Kāraka*):
* **Kāraka Directory:**
  * House 1: Sun | House 2: Jupiter | House 3: Mars
  * House 4: Moon, Mercury | House 5: Jupiter | House 6: Saturn, Mars
  * House 7: Venus | House 8: Saturn | House 9: Jupiter, Sun
  * House 10: Mercury, Sun, Jupiter, Saturn | House 11: Jupiter | House 12: Saturn
* **Three-Factor Synthesis for each Kāraka $K$:**
  1. Direct Planet Condition ($\text{k\_planet\_score} = \text{planets\_eval}[K]$).
  2. Relative House Placement ($R_{K, H} = ((\text{House}_K - H) \pmod{12}) + 1$): $+15.0$ for Kendra/Trine/2nd/11th, $-15.0$ for Dusthāna ($6, 8, 12$), $+5.0$ for H3.
  3. Kāraka Lagna Score ($\text{k\_lagna\_house\_score}$): Baseline condition of the natal house corresponding to the $H$-th sign counted forward from Kāraka $K$.
  $$\text{Score}_K = 0.55 \times \text{k\_planet\_score} + 0.30 \times \text{k\_lagna\_house\_score} + 0.15 \times \text{k\_rel\_bonus}$$

---

### Phase 7C: Chandra Lagna (Lunar Reference Frame) Assessment

* Computes the corresponding house counted from the Moon's occupied house:
  $$H_{\text{Chandra}} = ((H_{\text{Moon}} - 1 + H - 1) \pmod{12}) + 1$$
* Exposed in `components["chandra_lagna_assessment"]` with baseline score from $H_{\text{Chandra}}$.
* **Active Mathematical Weight:** Blended directly with Relative Houses (*Bhavāt Bhavam*) before computing the house composite:
  $$R_{\text{combined}, H} = 0.80 \times \text{Relative}_H + 0.20 \times \text{Chandra}_H$$

---

### Phase 8: Quantified House Walls — *Kartarī Yoga*

* Evaluates physical planets within $(0^\circ, 30^\circ)$ before and after $\text{Cusp}_H$.
* **True Kartarī Sign Adjacency (*Phaladīpikā* 15.6):**
  Requires true flanking across sign borders: $P_{\text{before}}$ must sit in the immediately preceding sign ($\text{Sign}_{H-1}$) and $P_{\text{after}}$ in the house sign or immediately following sign ($\text{Sign}_H$ or $\text{Sign}_{H+1}$), or both planets in $\text{Sign}_H$. An empty preceding sign cannot form a Kartarī wall.
* Flanking planets occupying the same Whole Sign house are attenuated by $0.50$.
* Compressed into $[-120, +120]$ range via hyperbolic tangent:
  $$\text{WallScore}_H = 120.0 \times \tanh\left(\frac{\text{RawScore}_H}{180.0}\right)$$

---

### Phase 9: Numerical House Yoga Scoring (Certified Classical Yoga Engine)

* Ingests certified classical yogas directly from Astra's `jyotish/yogas/` engine (`chart_dict["yogas"]`).
* **Classical Affliction Detection:** Expands `is_negative_yoga` to catch all classical affliction, poverty, disgrace, and friction patterns (`Niḥsva`, `Duṣkṛti`, `Mṛti`, `Śatru`, `Adhama`, `Aśubha`, `Depleted`, `Disgraced`, `Broken Initiatives`, `Pāpakartarī`, `Bandhana`, `Apakīrti`, `Dusthāna`, `Inauspicious`, etc.).
* **Global Nabhasa Sankhya Restriction:** Broad pattern yogas formed by $\ge 6$ planets (e.g., `Dāma`, `Pāśa`, `Kedāra`, `Śūla`, `Yuga`, `Gola`, `Vallakī`) do NOT credit all 12 owned houses; instead, their impact is focused strictly on physically occupied houses with $0.35\times$ base points.
* **Direct Attribution (Anti-Smearing):** Credit is awarded strictly to:
  * **Occupied Houses:** $1.00\times$ where yoga-forming planets physically sit.
  * **Explicit Participating Houses:** $0.75\times$ (or directly owned houses at $0.50\times$).
* **Rescaled Base Points:**
  * Parivartana: $65.0$
  * Mahāpuruṣa: $65.0$
  * Major Rāja / Dhana: $60.0$
  * Viparīta Rāja: $65.0$ (awards full points to Dusthāna houses $6, 8, 12$ per *Phaladīpikā* 6.57–70)
  * Minor Auspicious: $30.0$
  * Negative / Affliction: $-60.0$
* **Smooth Saturation:**
  $$\text{TotalYogaScore}_H = 100.0 \times \tanh\left(\frac{Y_{\text{raw}, H}}{120.0}\right)$$

---

### Phase 10: Dispositor Chain Tracking & House Lord Synthesis

#### 1. The "Second-Time Tracked = Final Dispositor" Rule
Traverses planet $\to$ sign lord until a planet is encountered a second time.

#### 2. Dispositor Synthesis Archetypes
1. **Svakṣetra Lord (1-hop):** $\text{EffectiveLordScore}_H = \text{LordScore} + 15.0$.
2. **Loop Returning to Self (*Parivartana*):** Restricted strictly to true 2-planet mutual sign exchanges ($\text{hops\_to\_repeat} == 2$):
   * If *Mahā Parivartana* (no Dusthāna involved): $(0.80 \times \text{LordScore} + 0.20 \times \text{PartnerScore}) + 15.0$.
   * If *Dainya Parivartana* (Dusthāna exchange with good house): $(0.80 \times \text{LordScore} + 0.20 \times \text{PartnerScore}) - 10.0$.
3. **Fallback to Final Dispositor (including loops with $\text{hops} \ge 3$):**
   $$\text{EffectiveLordScore}_H = 0.65 \times \text{LordScore} + 0.20 \times \text{ImmediateDispScore} + 0.15 \times \text{FinalDispScore}$$
4. **House Lord Digbala Bonus:** Adds $+0.15 \times \text{DigBalaPts}_{\text{Lord}}$.
5. **Direct Lord-in-Dusthāna Structural Penalty (*Phaladīpikā* 15.18 & 6.57):**
   * Applied when the lord is in a Dusthāna from its own house ($r_{\text{lord}} \in [6, 8, 12]$) ($-12.0$ for R8, $-8.0$ for R6/R12) or in an unmitigated 12th house placement ($-8.0$).
   * Doubled only if $d_{\text{D1}} < 0$ and $\text{LordScore} \ge 0$ (avoiding double-counting when `LordScore` is already negative).
   * Waived if the lord is in own/exaltation sign or forms a dignified Viparīta Rāja Yoga ($d_{\text{D1}} \ge 0.40$).

#### 3. Sign-Correct Occupant Synthesis
Each non-lord occupant is evaluated by its effective house polarity ($+1.0$ for 1st lord in non-Dusthānas, $+0.50$ for malefics in Upacayas, $-1.0$ for malefics in non-Upacayas):
* **Deadband for Moon / Mild Benefics:** When $F \in [-0.15, +0.15]$, polarity is positive ($+1.0$) if $d_{\text{D1}} \ge 0$, and malefic ($-1.0$) only if $d_{\text{D1}} < 0$.
* For positive polarity ($\text{polarity} > 0$): $\text{occ\_contrib} = \text{Score}_P \times \text{polarity}$.
* For negative polarity ($\text{polarity} < 0$, non-lord malefic in non-Upacaya house per *Phaladīpikā* 15.1 & 15.18):
  * If $\text{Score}_P \ge 0$ (dignified malefic): $\text{occ\_contrib} = -45.0 \times \left(1.0 - 0.50 \times \min\left(1.0, \frac{\text{Score}_P}{100.0}\right)\right)$ (softened bad results up to half).
  * If $\text{Score}_P < 0$ (afflicted malefic): $\text{occ\_contrib} = -45.0 \times \left(1.0 + \min\left(1.0, \frac{|\text{Score}_P|}{100.0}\right)\right)$ (intensified bad results up to $2\times$).
$$\text{CombinedLordScore}_H = \begin{cases} 0.70 \times \text{EffectiveLordScore}_H + 0.30 \times \overline{\text{OccupantImpacts}} & \text{if non-lord occupants exist} \\ \text{EffectiveLordScore}_H & \text{otherwise} \end{cases}$$

---

## 3. Qualitative Health Tiers (`synthesis.health_rating`)

* **$\ge +100.0$:** `"Exceptional / Off the Chart"` (`classical_tier`: `"Puṣṭa"`)
* **$+25.0 \text{ to } +99.9$:** `"Flourishing / Fortified"` (`classical_tier`: `"Puṣṭa"`)
* **$-20.0 \text{ to } +24.9$:** `"Mixed / Resilient"` (`classical_tier`: `"Miśra"`)
* **$-99.9 \text{ to } -20.1$:** `"Strained / Challenged"` (`classical_tier`: `"Hīna"`)
* **$\le -100.0$:** `"Severely Afflicted / Obstructed"` (`classical_tier`: `"Hīna"`)
