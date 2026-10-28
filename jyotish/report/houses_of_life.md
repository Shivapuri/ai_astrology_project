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
* **Compound Friendship (*Pañcadhā Maitrī*):** Evaluates planetary dignity using the classical 5-Fold Compound Relationship (`dignity_breakdown["final_dignity"]`), blending eternal Natural Friendship (*Naisargika Sambandha*) with chart-specific Temporary Friendship (*Tātkālika Sambandha* based on 3-sign separation) to determine how comfortable the planet feels in its host sign:
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
* **Functionally Positive ($F \ge 0.25$):**
  * $d_P \ge 0 \implies S = B \times (1.0 + d_P)$ (Up to $2\times$ intensification).
  * $d_P < 0 \implies S = B \times (1.0 - 0.80 \times |d_P|)$ (Severe debilitation retains only $0.20\times$ good results per *Phaladīpikā* 15.18).
* **Functionally Negative ($F \le -0.25$):**
  * $d_P \le 0 \implies S = B \times (1.0 + |d_P|)$ (Bad mood intensifies malice up to $2\times$).
  * $d_P > 0 \implies S = B \times (1.0 - \frac{d_P}{2.0})$ (Good mood mitigates malice by up to half).
* **Continuous Functional Transition ($-0.25 < F < 0.25$):**
  * Continuous linear blend anchored at neutral $S = B \times d_P$ at $F = 0$, eliminating cliff edges and abrupt sign inversions.

---

### Phase 4: Conjunctions, Cross-Border Halving & Cusp Dominance

1. **Continuous Exact-Degree Aspects (*Sphuṭa Dṛṣṭi*):**
   * Derived continuously from exact angular distance $\Delta\theta = (\lambda_{\text{cusp}} - \lambda_{\text{planet}}) \pmod{360^\circ}$ via Parāśara's exact *Sphuṭa Dṛṣṭi* formulation (`aspects.get_graha_drishti`), expressed on a $0\%$ to $100\%$ scale: $\frac{\text{Virūpas}}{60.0} \times 100.0$.
   * Natural classical blind spots ($0^\circ\text{–}60^\circ$, exact $150^\circ$, and $300^\circ\text{–}360^\circ$) are evaluated organically through the continuous degree calculus, perfectly matching the *Sphuṭa Dṛṣṭi* aspect matrix for sensitive Whole Sign cusps.
2. **Conjunction Proximity:**
   * Within $30^\circ$: $C_{\text{raw}} = \max\left(0.0, \left(1.0 - \frac{\Delta\lambda}{30.0}\right) \times 100.0\right)$.
3. **Cross-Border Attenuation:**
   * If a conjunction spans across a sign boundary, potency is halved ($\times 0.5$).
4. **Multi-Planet Cusp Dominance ("Potency Stealing"):**
   * Co-occupants of the same Whole Sign house share cusp alignment. In multi-planet stelliums ($\ge 2$ co-occupants), planets are sorted descending by their initial cusp proximity ($C_{\text{raw}}$).
   * Across all pairs, any closer co-occupant $P_{\text{near}}$ absorbs conjunction points from a farther co-occupant $P_{\text{far}}$ when $C_{\text{raw}, \text{near}} > C_{\text{raw}, \text{far}}$ and their separation is within $15^\circ$:
     $$\Delta_{\text{steal}} = C_{\text{far}} \times \frac{C_{\text{near}}}{C_{\text{near}} + C_{\text{far}}} \times \left(1.0 - \frac{\Delta\theta_{P_{\text{near}}, P_{\text{far}}}}{15^\circ}\right)$$
     $$C_{\text{near, final}} = \min(125.0, C_{\text{near}} + \Delta_{\text{steal}}), \qquad C_{\text{far, final}} = \max(0.0, C_{\text{far}} - \Delta_{\text{steal}})$$
   * Equidistant co-occupants retain their respective conjunctions without arbitrary asymmetric theft, and pairwise processing ensures order-independence across 3+ planet stelliums.
5. **Mutual Sign Exchange Connection (*Mitho Yoga / Parivartana*, *Phaladīpikā* 15.30):**
   * Two planets in mutual reception / sign exchange act as connected (*yukta* / *bandha*), receiving a $50.0\%$ mutual influence floor in `planet_to_planet` ($\max(\text{AspectPct}, \text{ConjPct}, 50.0\%)$) even when separated by disparate signs without physical Graha Dṛṣṭi.

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
     $$\text{BaseDigBala}_P = 20.0 \times \text{DigFactor}_P$$
   * **Sign-Safe Shadbala Scaling:** Clamped within $[0.75, 1.25]$:
     * If $\text{BaseDigBala}_P \ge 0$: $\text{DigBalaPts}_P = \text{BaseDigBala}_P \times \text{ClampedBala} + (\text{ClampedBala} - 1.0) \times 20.0$
     * If $\text{BaseDigBala}_P < 0$: $\text{DigBalaPts}_P = \frac{\text{BaseDigBala}_P}{\text{ClampedBala}} + (\text{ClampedBala} - 1.0) \times 20.0$
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
6. **Bhāva Sandhi & Cusp Proximity Relief (*Phaladīpikā* 15.14 & 8.34–35):**
   * A planet within $4.0^\circ$ of a sign border faces junction weakness: $\text{RawSandhiPen} = \max(0.0, 1.0 - \frac{\Delta\lambda_{\text{border}}}{4.0^\circ})$.
   * Per *Phaladīpikā* 15.14 (*bhāveṣu bhāvasphuṭatulyabhāgas tadbhāvajaṃ pūrṇaphalaṃ vidhatte*) and 8.34–35:
     * If the sensitive house cusp itself is near the border ($< 4.0^\circ$) and the planet is inside the house between the cusp and sign center ($\Delta\lambda_{\text{border}} \ge \Delta\lambda_{\text{cusp, border}}$), or if the planet is tightly conjunct the cusp ($\Delta\lambda_{\text{cusp}} \le 5.0^\circ$), the planet is situated directly at the cusp door inside the house and is completely relieved of sandhi penalty ($\text{CuspRelief} = 0.0, \text{SandhiPenalty} = 0.0$).
     * For distances $5.0^\circ < \Delta\lambda_{\text{cusp}} < 10.0^\circ$, relief scales smoothly via linear interpolation:
       $$\text{CuspRelief} = \frac{\Delta\lambda_{\text{cusp}} - 5.0^\circ}{5.0^\circ}$$
     * If $\Delta\lambda_{\text{cusp}} \ge 10.0^\circ$, full sandhi penalty applies ($\text{CuspRelief} = 1.0$).
     * Final penalty: $\text{SandhiPenalty} = \text{RawSandhiPen} \times \text{CuspRelief}$.
7. **Combustion & Solar Gain:** Proximity to Sun within combustion orb.
8. **Sign-Safe Synthesis:** Produces `final_assessment_score`.

---

### Phase 6: Basic House Condition — Direct Evaluation

For each house $H \in \{1, \dots, 12\}$:
1. Impact $I_{P \to H} = \max(\text{AspectPct}_{P \to \text{Cusp}_H}, \text{DominanceConjPct}_{P \to H})$.
   * All continuous aspects contribute directly and proportionally without artificial step cutoffs.
2. Dignity $d_P$ and Effective Functional Nature $F_{P, H}$:
   * **House Lord:** $F_{\text{eff}} = 2.0$.
   * **Non-Lord Planets:**
     * **Exaltation / Mūlatrikoṇa / Domicile Sign Override:** If the target house sign $H$ is planet $P$'s Exaltation, Mūlatrikoṇa root, or regular Domicile sign (e.g., Moon on Taurus $H=10$ for Leo Lagna), and the planet is non-malefic ($\text{InherentScore} \ge 0.0$ or $F_{\text{lagna}} \ge 0.0$), the planet intrinsically harmonizes with and enriches the sign itself, setting $\text{FriendMod} = +0.50$ regardless of interpersonal friction with the house lord.
     * **Natural Friendship Matrix (*Naisargika Sambandha*, *Phaladīpikā* 15.5 & 15.7):** For other signs, bidirectional relationship ($P \to \text{Lord}$ and $\text{Lord} \to P$) modifies the baseline:
       * If both are Friends: $\text{FriendMod} = +0.50$
       * If either considers the other an Enemy: $\text{FriendMod} = -0.50$
       * If one is Friend and the other Neutral: $\text{FriendMod} = +0.25$
       * Otherwise: $\text{FriendMod} = 0.0$
     * **Effective Functional Formula:**
       $$F_{\text{eff}} = 0.50 \times F_{\text{lagna}} + 0.50 \times \text{InherentScore} + 0.35 \times \text{FriendMod}$$
       *(Scales $F_{\text{lagna}}$ by $0.50$ so non-lords remain bounded on the $[-2.0, +2.0]$ scale below or equal to the House Lord $2.00$, preserving Rāja Yogakāraka status and natural benefic cushions while factoring archetypal relationship with the house lord).*
3. **Continuous Signed Ray Impact Synthesis (`_compute_signed_ray_impact`):**
   * Eliminates deadband cliffs and sign inversions across the functional transition $[-0.25, +0.25]$:
     * If $F_{\text{eff}} \ge 0.25$: $\text{signed\_impact} = \text{scale\_by\_dignity}(I, d_P, 1.0) \times (1.0 + \text{slope} \times (F_{\text{eff}} - 1.0))$
     * If $F_{\text{eff}} \le -0.25$: $\text{signed\_impact} = \text{scale\_by\_dignity}(I, d_P, -1.0) \times -(1.0 + \text{slope} \times (|F_{\text{eff}}| - 1.0))$
     * If $-0.25 < F_{\text{eff}} < 0.25$: continuous linear blend anchored at neutral $I \times d_P$.
   * Utilized consistently in Phase 5 ($\text{slope} = 0.20$ for planet-to-planet aspects) and Phase 6 ($\text{slope} = 0.65$ for cusp rays).
4. **Upacaya (3, 6, 11) Malefic Occupant Rule (*Phaladīpikā* 15.18):**
   * Triggered **strictly when functioning as a malefic ($F_{\text{eff}} < 0$)**. Benefic 1st House Lords and Rāja Yogakārakas are never slashed by friendly fire.
   * Scaled **positively** by dignity (exalted gives strong resilience; debilitated gives weak resilience):
     $$\text{Impact}_{P \to H} = \text{scale\_by\_dignity}(I, d_P, 1.0) \times 0.35$$
5. **Condition-Gating (*Amūḍha-Hīnāḥ*, *Phaladīpikā* 15.1, 15.5):**
   $$\text{ConditionIntegrity} = (1.0 - 0.75 \times \text{CombLoss}_P) \times (1.0 - 0.50 \times \text{SandhiPen}_P)$$
   * Benefic impacts ($\text{signed\_impact} > 0$) are multiplied by $\text{ConditionIntegrity}$.
   * **Multi-Varga Negative Dignity Attenuation (*Arinīca-Mūḍha*):** Evaluated against composite multi-varga dignity ($d_P < 0$). If $d_P < 0$, positive rays are attenuated smoothly: $\text{ConditionIntegrity} \times (1.0 - 0.40 \times |d_P|)$, and by an additional $0.75\times$ if occupying a Dusthāna ($6, 8, 12$). Planets rescued by D9 or Vargottama ($d_P \ge 0$) are not penalized.
   * Malefic impacts ($\text{signed\_impact} < 0$) are intensified by combustion: $(1.0 + 0.35 \times \text{CombLoss}_P) \times (1.0 - 0.30 \times \text{SandhiPen}_P)$.
6. **Rāhu & Ketu Cusp Impact (*Phaladīpikā* 15.8):**
   * Upacaya houses ($3, 6, 11$): $+0.35 \times C_{\text{node}}$.
   * Non-Upacaya houses: $-0.60 \times C_{\text{node}} \times \text{MitFactor}$ (where $\text{MitFactor} = 0.50$ if node is dignified or aspected/conjoined by Jupiter or Venus; $1.25$ if aggravated by Mars/Saturn; $1.00$ otherwise).
7. **Strict Monotonicity & Cusp Score Normalization:**
   * Fixed baseline divisor ($4.0$) matching the natural 7-planet continuous aspect density with hyperbolic tangent saturation:
     $$\text{RawHouseScore}_H = \frac{\sum \text{SignedImpact}}{4.0}$$
     $$\text{BoundedScore}_H = 120.0 \times \tanh\left(\frac{\text{RawHouseScore}_H}{120.0}\right)$$
   * Guaranteed monotonicity: every additional benefic aspect strictly increases the house score, and every additional malefic aspect strictly decreases it.
8. **Spreadsheet-Grade Calculation Ledger (`calculation_ledger`):**
   * Serializes full tabular disclosure for all 12 houses across 10 analytical columns:
     1. `Graha`: Monochrome glyph (`\uFE0E`), planet name, and role (`Lord`, `Occupant`, `Aspect`, `Node`).
     2. `Pos & ΔCusp`: D1 sign, degree in sign, and shortest angular distance ($\Delta\theta^\circ$) to $\text{Cusp}_H$.
     3. `Aspect %`: Exact Parāśara *Sphuṭa Dṛṣṭi* onto $\text{Cusp}_H$: $(\text{Virūpas}/60) \times 100\%$.
     4. `Conj %`: $30^\circ$ linear conjunction proximity ($0.5\times$ if cross-border) $\to$ after cusp dominance stealing.
     5. `Base Ray (I)`: $I_{P \to H} = \max(\text{Aspect\%}, \text{Conj}_{\text{dom}}\%)$.
     6. `Func (F_eff)`: Effective functional nature: $2.00$ for Lord; else $0.50\,F_{\text{lagna}} + 0.50\,\text{Inh} + 0.35\,\text{FriendMod}$.
     7. `Dignity (d_P)`: Composite D1+D9 dignity unit $d_P \in [-1.00, +1.00]$ (or Vargottama $\ge +0.80$).
     8. `Scaled Ray`: Ray after `scale_by_dignity` and functional multiplier $f_{\text{mult}}$ (or $+0.35\times$ Upacaya malefic boost).
     9. `Gate Mult`: *Amūḍha-hīnāḥ* integrity multiplier from Combustion, Sandhi, and negative $d_P$.
     10. `Net Ray`: Exact signed points contributed by this row ($\text{Scaled Ray} \times \text{Gate Mult}$).
   * **9 Canonical Graha/Node Rows:** Always ordered `Sun`, `Moon`, `Mars`, `Mercury`, `Jupiter`, `Venus`, `Saturn`, `Rahu`, `Ketu`.
   * **3 Summary Footer Proofs:**
     1. $\sum \text{Raw Signed Cusp Rays}$ ($\text{raw\_total\_signed}$)
     2. $\div \text{Fixed Baseline Divisor } 4.0$ ($\text{raw\_divided\_score}$)
     3. $\text{Final Basic Score } (120 \times \tanh(\text{Raw} / 120))$ (matching the `Basic (30%)` column in the 12-House Matrix).

---

### Phase 7: Relative House Technique — *Bhavāt Bhavam* (*Phaladīpikā* 15.2–15.5)

Treats each target house $H$ as House 1:
1. **Functional Nature Blending:**
   * Relative functional nature from sign $H$ is blended with the native's natal functional nature:
     $$F_{\text{rel}} = 0.70 \times F_{\text{relative}} + 0.30 \times F_{\text{natal}}$$
   * The native's Ascendant Lord (Lagneśa) is protected across all relative house examinations: $\max(0.50, F_{\text{rel}})$.
2. **House Lord Relative Placement ($R_{\text{Lord}, H}$):**
   * **Relative 1, 2, 4, 5, 7, 9, 10 (*Kendra / Trikoṇa / 2nd*, 15.2):** Weight $1.0$, plus degree-aspect proximity bonus when close to exact $0^\circ, 90^\circ, 120^\circ, 180^\circ$ aspect angles.
   * **Relative 3, 11 (*Upacaya*, 15.18):** Weight $0.50$.
   * **Relative 6, 8, 12 (*Bhāva-Nāśa*, 15.3 & 15.5):**
     * If the Lord is in its other own sign (*Svakṣetra* per 15.29), penalty is $0.0$.
     * Otherwise, base penalty: $-110.0$ in R8, $-80.0$ in R12, $-70.0$ in R6.
     * Halved ($0.50\times$) if the Lord is dignified ($d_P \ge 0.4$) and uncombust; amplified if debilitated or combust.
     * Benefic aspects onto the Lord mitigate this penalty.
3. **Non-Lord Planets in Relative Houses:**
   * Relative 2, 4, 5, 7, 9, 10: Weight $1.0$.
   * Relative 11: Weight $0.50$; Relative 3: Weight $0.40$ (secondary Upacaya growth support).
   * Relative 1: $+0.50\times$ if $F_{\text{rel}} > 0$; $-0.75\times$ if $F_{\text{rel}} < 0$.
   * Relative 6, 8, 12: Adds to raw Dusthāna penalty if $F_{\text{rel}} < 0$.
4. **Benefic Mitigation:** Malefics in relative Dusthānas are mitigated strictly by direct aspects from relative benefics.
5. **Denominator Floor:** $\text{denom} = \max(3.0, N_{\text{active}})$.

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
  2. Relative House Placement & Proximity ($R_{K, H} = ((\text{House}_K - H) \pmod{12}) + 1$, *Phaladīpikā* 15.25):
     * Kendra / Trine / 2nd / 11th: $+15.0$ (`"Close / Nourishing"`)
     * Dusthāna ($6, 8, 12$): $-15.0$ (`"Distant / Dusthāna"`)
     * Upacaya 3rd: $+5.0$ (`"Moderate / Upacaya"`)
     * *Phaladīpikā 15.25 Distinction:* Distinguishes relationship proximity/closeness (`karaka_relative_houses`, `karaka_proximity`) from inner happiness (*Saukhya*).
  3. Kāraka Lagna Score ($\text{k\_lagna\_house\_score}$): Comprehensive Sign-Level Baseline condition of the natal house corresponding to the $H$-th sign counted forward from Kāraka $K$:
     $$\text{SignBaseline}_H = 0.50 \times \text{Basic}_H + 0.30 \times \text{LordAndOccAvg}_H + 0.20 \times \text{Relative}_H$$
  $$\text{Score}_K = 0.55 \times \text{k\_planet\_score} + 0.30 \times \text{k\_lagna\_house\_score} + 0.15 \times \text{k\_rel\_bonus}$$

---

### Phase 7C: Chandra Lagna (Lunar Reference Frame) Assessment

* Computes the corresponding house counted from the Moon's occupied house:
  $$H_{\text{Chandra}} = ((H_{\text{Moon}} - 1 + H - 1) \pmod{12}) + 1$$
* Evaluates the lunar perspective utilizing the comprehensive Sign-Level Baseline $\text{SignBaseline}_{H_{\text{Chandra}}}$ (Cusp + Lord + Relative placement) rather than direct cusp rays alone.
* Exposed in `components["chandra_lagna_assessment"]` with baseline score from $H_{\text{Chandra}}$.
* **Active Mathematical Weight:** Blended directly with Relative Houses (*Bhavāt Bhavam*) before computing the house composite:
  $$R_{\text{combined}, H} = 0.80 \times \text{Relative}_H + 0.20 \times \text{Chandra}_H$$

---

### Phase 8: Quantified House Walls — *Kartarī Yoga*

* Evaluates physical planets within $(0^\circ, 30^\circ)$ before and after $\text{Cusp}_H$.
* **Symmetric Cross-Border Kartarī Sign Adjacency (*Phaladīpikā* 15.6 & DiCara Ep. 4):**
  Requires true flanking across sign borders:
  * $P_{\text{before}}$ within $30^\circ$ before the cusp must sit in $\text{Sign}_{H-1}$ or $\text{Sign}_H$.
  * $P_{\text{after}}$ within $30^\circ$ after the cusp must sit in $\text{Sign}_H$ or $\text{Sign}_{H+1}$.
  * Both cannot sit exclusively in $\text{Sign}_{H-1}$ or exclusively in $\text{Sign}_{H+1}$.
  * This fully supports late Ascendants/cusps ($15^\circ\text{–}30^\circ$) where $P_{\text{before}}$ sits in $\text{Sign}_H$ and $P_{\text{after}}$ sits in $\text{Sign}_{H+1}$.
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
