# Houses of Life (Vic DiCara / Phaladīpikā Chapter 15 Evaluation System)

## 1. Overview & Foundational Mathematical Architecture

The **Houses of Life** system is an advanced quantitative astrological engine developed by Vic DiCara, rooted in Chapter 15 of Mantreśvara's classical authority *Phaladīpikā*. It provides a rigorous, multi-stage evaluation of the 12 houses (*Bhāvas*) and 7 classical physical planets (*Grahas*): Sun, Moon, Mars, Mercury, Jupiter, Venus, and Saturn.

Unlike qualitative traditions that rely on broad rules of thumb, Houses of Life computes continuous mathematical scores across nine distinct phases without rounding intermediate arc-minutes or arc-seconds.

$$\text{Composite House Score}_H = 0.30\,\text{Basic}_H + 0.25\,\text{Lord}_H + 0.25\,\text{Yoga}_H + 0.10\,\text{Relative}_H + 0.10\,\text{Wall}_H$$

*(Note: When a house is unwalled ($\text{is\_walled} = \text{False}$), the $10\%$ wall weight is redistributed proportionally across the remaining active components by dividing by $0.90$).*

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

Derived from *Phaladīpikā* Chapter 15 and *BPHS* Chapter 34, the functional nature of each planet relative to the Ascendant is quantified via sequential rules with *Yogakāraka* and *Kendrādhipatya* adjustments:

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
* **Rule 4 (Inherent Natural Temperament & BPHS Ch. 34 Adjustments):**
  * Extreme natural benefics (Jupiter, Venus): $+1$.
  * Extreme natural malefics (Mars, Saturn): $-1$.
  * Mild/neutral planets (Sun, Moon, Mercury): $0$.
  * **Supreme Rāja Yogakāraka Bonus (*BPHS* 34.40–43):** If a planet simultaneously owns a Kendra ($4, 7, 10$) and a Trine ($5, 9$) (e.g., Mars for Cancer/Leo Lagna, Saturn for Taurus/Libra Lagna), its natural maleficence is waived and it receives $+1$ (`inherent_score = max(0, inherent_score) + 1`).
  * **Māraka & Triṣaḍāya Preservation:** Natural malefics owning a Kendra without a Trine (such as Saturn for Aries owning H10/H11, or Mars for Libra owning H2/H7) retain their inherent maleficence ($-1$) because their second sign is always a Māraka ($2$) or Triṣaḍāya ($3, 11$) house (*BPHS* 34.22, 34.33, 34.41–42).

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
   * Computes incoming planetary influences using the Phase 3 `scale_by_dignity` law:
     $$\text{scaled\_mag} = \text{scale\_by\_dignity}(I_{Q \to P}, d_Q, F_Q)$$
     $$\text{Impact}_{Q \to P} = \begin{cases} \text{scaled\_mag} \times (1.0 + 0.20 \times (F_Q - 1)) & \text{if } F_Q > 0 \\ -\text{scaled\_mag} \times (1.0 + 0.20 \times (|F_Q| - 1)) & \text{if } F_Q < 0 \\ \text{scaled\_mag} & \text{if } F_Q = 0 \end{cases}$$
   * Normalized by average active aspect count ($2.5$) and clamped to $[-150, +150]$:
     $$\text{Inf}_P = \max\left(-150.0, \min\left(150.0, \frac{\sum_{Q \neq P} \text{Impact}_{Q \to P}}{2.5}\right)\right)$$
3. **Cusp Alignment ($\text{Align}_P$):**
   * Capped dominance-adjusted conjunction $\min(100.0, C_{P, \text{final}})$ multiplied by:
     * Prominent houses ($1, 4, 5, 9, 10$): $\times 1.50$
     * Regular houses ($2, 7, 11$): $\times 1.00$
     * Hidden houses ($3, 6, 8, 12$): Differentiated by classical role:
       * Dusthāna lord in Dusthāna ($6, 8, 12$): $\times 1.00$ (Viparīta resilience)
       * 3rd lord or natural malefics (Sun, Mars, Saturn) in 3rd Upacaya: $\times 0.75$
       * Other planets in 3rd: $\times 0.25$ (mild Upacaya growth)
       * Natural malefics in 6th Upacaya: $\times 0.50$ (conquering obstacles)
       * Venus or dignified planet ($d_P \ge 0.4$) in 12th: $\times (-0.25)$
       * Other Dusthāna placements: $\times (-0.50)$ (moderated penalty)
4. **Bhāva Sandhi ($\text{Sandhi}_P$):**
   * Within $4.0^\circ$ of either sign border:
     $$\text{SandhiPenalty}_P = \max\left(0.0, 1.0 - \frac{\Delta_{\text{border}}}{4.0}\right)$$
5. **Combustion & Solar Gain:**
   * For $P \neq \text{Sun}$: If $\Delta_{\text{Sun}} < \text{Orb}_P$, $\text{CombLoss}_P = 1.0 - \frac{\Delta_{\text{Sun}}}{\text{Orb}_P}$.
   * For Sun: $\text{SolarGainRatio} = \min\left(0.50, \sum_{Q \neq \text{Sun}} \text{CombLoss}_Q \times 0.25\right)$, multiplier $= 1.0 + \text{SolarGainRatio}$.
6. **Planetary Synthesis (Sign-Safe Application of Sandhi & Combustion):**
   $$\text{BaseScore}_P = \frac{D_{\text{pct}, P} + \text{Inf}_P + \text{Align}_P}{3.0}$$
   * **When $\text{BaseScore}_P \ge 0$:**
     $$\text{FinalScore}_{\text{Sun}} = \text{BaseScore} \times (1.0 - 0.5 \times \text{SandhiPenalty}) \times (1.0 + \text{SolarGainRatio})$$
     $$\text{FinalScore}_{P \neq \text{Sun}} = \text{BaseScore} \times (1.0 - 0.5 \times \text{SandhiPenalty}) \times (1.0 - 0.75 \times \text{CombLoss}_P)$$
   * **When $\text{BaseScore}_P < 0$ (Adds Structural Strain):**
     $$\text{StrainMult}_{\text{Sun}} = 1.0 + 0.25 \times \text{SandhiPenalty}$$
     $$\text{FinalScore}_{\text{Sun}} = (\text{BaseScore} \times \text{StrainMult}) + 10.0 \times \text{SolarGainRatio}$$
     $$\text{StrainMult}_{P \neq \text{Sun}} = 1.0 + 0.25 \times \text{SandhiPenalty} + 0.35 \times \text{CombLoss}_P$$
     $$\text{FinalScore}_{P \neq \text{Sun}} = \text{BaseScore} \times \text{StrainMult}$$

---

### Phase 6: Basic House Condition — Direct Evaluation

For each house $H \in \{1, \dots, 12\}$:
1. Impact $I_{P \to H} = \max(\text{AspectPct}_{P \to \text{Cusp}_H}, \text{DominanceConjPct}_{P \to H})$.
2. Dignity $d_P$: Extracted via `_get_dignity_status()`, strictly prioritizing compound 5-fold friendship (*Pañcadhā Maitrī*, `final_dignity`) over uncompounded sign dignity.
3. Functional Nature $F_{P, H}$:
   * If $P$ rules House $H$: $F_{P, H} = +2$ (House Lord override).
   * Otherwise: $F_{P, H} = F_P$.
4. Scaled Signed Impact with Damped Functional Multiplier:
   $$\text{scaled\_i} = \text{scale\_by\_dignity}(I_{P \to H}, d_P, F_{P, H})$$
   If $F_{P, H} \neq 0$:
   $$f_{\text{mult}} = \left(1.0 + 0.65 \times (|F_{P, H}| - 1)\right) \times \text{sgn}(F_{P, H})$$
   $$\text{Impact}_{P \to H} = \text{scaled\_i} \times f_{\text{mult}}$$
   If $F_{P, H} = 0$:
   $$\text{Impact}_{P \to H} = \text{scaled\_i}$$
   *(Note: `scale_by_dignity` already incorporates the sign of $d_P$ when $F = 0$, preventing double negation).*
5. **Upacaya (3, 6, 11) Malefic Occupant Attenuation (*BPHS* 50.5 / *Phaladīpikā* 26.2):**
   When a natural malefic (Sun, Mars, Saturn) physically occupies an Upacaya house ($3, 6, 11$) as a non-lord occupant ($P \in \text{Occupants}_H, P \neq \text{Lord}_H$) with negative functional nature ($F_{P, H} < 0$), its negative impact on its occupied cusp is attenuated:
   $$\text{Impact}_{P \to H} = \begin{cases} \text{Impact}_{P \to H} \times 0.35 & \text{if } H \in \{3, 6\} \\ \text{Impact}_{P \to H} \times 0.50 & \text{if } H = 11 \end{cases}$$
   This ensures that malefics building resilience, defeating adversaries, and generating material gains in Upacaya houses do not destroy the very cusps where they classically excel.
6. **Smooth Continuous Active Divisor:**
   $$\text{ActiveWeights}_H = \sum_{P=1}^{7} \min\left(1.0, \frac{I_{P \to H}}{45.0}\right)$$
   $$\text{EffDivisor}_H = \max(4.0, \text{ActiveWeights}_H)$$
   $$\text{BasicHouseScore}_H = \frac{\sum_{P=1}^{7} \text{Impact}_{P \to H}}{\text{EffDivisor}_H}$$
   *(Eliminates step-function cliffs at the $25\%$ threshold, keeping scores smooth and balanced in $[-100, +100]$).*

---

### Phase 7: Relative House Technique — *Bhavāt Bhavam* (*Phaladīpikā* 15.2 & 15.4)

Treats each target house $H$ as House 1:
1. Relative house of planet $P$: $R_{P, H} = ((\text{House}_P - H) \pmod{12}) + 1$.
   * **Core Kendra-Koṇa (KK) Group (*Phaladīpikā* 15.2):** Relative houses $2, 4, 5, 7, 9, 10$ (weight $1.0$).
   * **Secondary Support Group:**
     * Relative House $11$ (weight $0.50$).
     * Relative House $1$ is included **only** when $F_{P \mid H} > 0$ (weight $0.50$), rewarding houses occupied by their own lord or relative benefics while preventing quadruple-counting of malefic occupants.
   * **Dusthāna Group:** Relative houses $6, 8, 12$.
2. Relative Functional Nature $F_{P \mid H}$: Re-computed with House $H$ as 1st house. If a planet has a raw relative functional score of $0$ (neutral), its dignity unit $d_P$ serves as its functional nature, scaled cleanly without double dignity squaring.
3. KK and secondary support planets contribute their dignity-scaled score.
4. Dusthāna relative malefics generate negative points; mitigated by average aspect percentage cast onto them by relative benefics ($\overline{\text{Mit}}$) and benefic co-occupancy ($+15\%$ per benefic). Relative benefics in Dusthānas contribute $0$ and do not increment $N_{\text{active}}$.
5. Denominator floored at $4.0$: $\text{RelScore}_H = \frac{\text{KK\_Points} + \text{Dusthana\_Mitigated}}{\max(4.0, N_{\text{active}})}$.

---

### Phase 8: Quantified House Walls — *Kartarī Yoga*

* Evaluates physical planets within $(0^\circ, 30^\circ)$ before and after $\text{Cusp}_H$.
* Flanking planets occupying the same Whole Sign house are attenuated by $0.5$ to prevent double-counting direct cusp conjunctions.
* Compressed into $[-120, +120]$ range via hyperbolic tangent:
  $$\text{WallScore}_H = 120.0 \times \tanh\left(\frac{\text{RawScore}_H}{180.0}\right)$$

---

### Phase 9: Numerical House Yoga Scoring (Certified Classical Yoga Engine)

Ingests certified classical yogas directly from Astra's `jyotish/yogas/` engine (`chart_dict["yogas"]`), eliminating synthetic pairwise pseudo-yogas and respecting *Yoga Bhaṅga* status:
1. **Broken Yogas:** Yogas marked as `BROKEN` are completely excluded.
2. **Mitigation / Bhaṅga Multipliers:**
   * Negative / Affliction Yogas: `RESCUED` reduces penalty to $25\%$; `STAINED` reduces penalty to $60\%$.
   * Auspicious Yogas (Rāja, Dhana, Mahāpuruṣa, Viparīta): `PURE` $\times 1.00$, `RESCUED` $\times 0.70$, `STAINED` $\times 0.50$.
3. **Classical Categories Evaluated:**
   * **Negative / Affliction Yogas:** Broadened detection catches Dāridrya, Dainya, Kemadruma, Śakaṭa, Grahaṇa, Guru-Caṇḍāla, Kāla Sarpa, Viṣa, Kuja Doṣa, and all Arishta/Doṣa/Pāpa afflictions. Base penalty $-80.0 \times \text{plaus\_mult} \times \text{status\_mult}$ afflicts designated participating/owned houses and hosting Dusthānas (hosting Dusthāna receives $-50\%$ penalty, never an artificial positive reward).
   * **Auspicious Parivartana Yogas (Mahā / Kahala):** $+95.0$ base points to exchanged houses.
   * **Pañca Mahāpuruṣa Yogas:** $+90.0$ base points to occupied Kendra, $+67.5$ points to owned houses (excluding Dusthānas $6, 8, 12$).
   * **Rāja, Dhana, Yogakāraka, Viparīta Yogas:**
     * Viparīta Yogas receive $+80.0$ base points.
     * Major Rāja and Dhana Yogas receive $+90.0$ base points.
     * Minor solar / lunar yogas (*Sunaphā*, *Anaphā*, *Veśi*, *Vaśi*, *Budha-Āditya*, etc.) receive $+45.0$ base points.
     * Secondary Dusthāna lordships ($6, 8, 12$) are strictly excluded from receiving Rāja/Dhana ownership points.
     * When a non-Viparīta Rāja/Dhana yoga occurs inside a Dusthāna ($6, 8, 12$), the hosting Dusthāna receives only $25\%$ spillover ($0.25\times$) so it never outranks the owned houses.
4. **Dispositor-Routed Ownership Attribution (Anti-Smearing):**
   When planets with dual rulerships (Mars, Mercury, Jupiter, Venus, Saturn) participate in an auspicious yoga, their owned houses are no longer smeared with uniform credit. Instead, credit is strictly channeled through the active dispositor chain:
   * **Occupied Houses:** Receive full intensity ($1.00\times$) where participating planets physically reside.
   * **Yoga-Initiating / Traversed Chain Houses:** Houses whose signs initiate the yoga or form part of the direct energy chain receive $0.75\times$ (single rulers Sun and Moon also receive $0.75\times$).
   * **Final Dispositor's Secondary Houses:** The fallback houses owned by the Final Dispositor (the planet tracked a second time) receive $0.60\times$ credit.
   * **Unvisited Secondary Signs:** Secondary houses of non-final planets that do not participate in the active energy loop are strictly excluded ($0.0\times$).
   * **Dusthāna Spillover:** Occupied Dusthānas receive only $0.25\times$ spillover; unoccupied Dusthānas receive $0.0\times$.
5. **Smooth Saturation:**
   $$\text{TotalYogaScore}_H = 150.0 \times \tanh\left(\frac{Y_{\text{raw}, H}}{150.0}\right)$$
   Guarantees that multi-yoga clusters remain bounded within $[-150.0, +150.0]$.

---

### Phase 10: Dispositor Chain Tracking & House Lord Synthesis

In astrology, a **dispositor** is simply the planetary "landlord" of the sign where another planet sits. Just as a tenant depends on their landlord for house maintenance, a planet's strength depends on the health of its dispositor.

#### 1. The "Second-Time Tracked = Final Dispositor" Rule
To find who truly holds ultimate authority over a house or planet, we follow the chain of landlords step-by-step:
1. Start at the House Lord $P_0$. Record visit count $\text{count}[P_0] = 1$.
2. Look at the zodiac sign where $P_0$ is located, and identify its ruler (its landlord) $P_1$.
3. Increment $\text{count}[P_1]$.
4. **Stopping Condition:** The exact instant any planet is visited for the **second time** ($\text{count}[P_k] = 2$), the chain halts immediately. That planet $P_k$ is declared the unique **Final Dispositor** for that starting point.

> [!NOTE]
> **Guaranteed Finite Termination (Pigeonhole Principle):**
> Because there are only 7 classical sign lords (Sun through Saturn), stepping along sign rulerships is mathematically guaranteed to encounter a repeat within at most 8 steps ($1 \le \text{hops} \le 7$). An infinite loop is impossible.

#### 2. Three Structural Dispositor Archetypes
1. **Planet in its Own Sign (*Svakṣetra*, 1-hop):**
   * Example: Mars in Scorpio $\to$ Mars's landlord is Mars ($\text{count}[\text{Mars}] = 2 \implies \text{STOP}$).
   * The planet is sovereign in its own home. It receives a $+20.0$ resilience protection bonus:
     $$\text{EffectiveLordScore}_H = \text{LordScore} + 20.0$$
2. **Mutual Exchange / Multi-Planet Loop (*Parivartana*, $\text{returns\_to\_self} = \text{True}$):**
   * Example: Venus in Cancer $\to$ Moon in Sagittarius $\to$ Jupiter in Libra $\to$ Venus ($\text{count}[\text{Venus}] = 2 \implies \text{STOP}$).
   * The chain loops back to the starting lord. The lord is buffered by its direct dispositor partner ($20\%$) and receives a $+15.0$ loop resonance bonus:
     $$\text{EffectiveLordScore}_H = (0.80 \times \text{LordScore} + 0.20 \times \text{PartnerScore}) + 15.0$$
3. **Fallback to Independent Final Dispositor ($\text{final\_dispositor} \neq \text{Lord}$):**
   * Example: Sun in Scorpio $\to$ Mars in Virgo $\to$ Mercury in Scorpio $\to$ Mars ($\text{count}[\text{Mars}] = 2 \implies \text{STOP}$). Mars is the Final Dispositor for the Sun.
   * The lord's baseline assessment is anchored $75\%$ on itself and $25\%$ on its Final Dispositor:
     $$\text{EffectiveLordScore}_H = 0.75 \times \text{LordScore} + 0.25 \times \text{FinalDispositorScore}$$

#### 3. House Lord & Occupants Synthesis
To prevent passing guests (planets temporarily visiting a house) from washing out the permanent master of the house, the combined assessment anchors $70\%$ on the House Lord and $30\%$ on non-lord occupants:
$$\text{CombinedLordScore}_H = \begin{cases} 0.70 \times \text{EffectiveLordScore}_H + 0.30 \times \overline{\text{Occupants}} & \text{if non-lord occupants exist} \\ \text{EffectiveLordScore}_H & \text{otherwise} \end{cases}$$

---

## 3. Qualitative Health Tiers (`synthesis.health_rating`)

* **$\ge +100.0$:** `"Exceptional / Off the Chart"` (`classical_tier`: `"Puṣṭa"`)
* **$+25.0 \text{ to } +99.9$:** `"Flourishing / Fortified"` (`classical_tier`: `"Puṣṭa"`)
* **$-20.0 \text{ to } +24.9$:** `"Mixed / Resilient"` (`classical_tier`: `"Miśra"`)
* **$-99.9 \text{ to } -20.1$:** `"Strained / Challenged"` (`classical_tier`: `"Hīna"`)
* **$\le -100.0$:** `"Severely Afflicted / Obstructed"` (`classical_tier`: `"Hīna"`)
