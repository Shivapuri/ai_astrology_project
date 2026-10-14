# Jyotish Engine: Bhāva Bala (House Strength & Synthesis)

This module calculates **Bhāva Bala** (the overall strength and capacity of each of the 12 astrological houses) and combines it with classical diagnostics from Mantreśvara's *Phaladeepika*.

---

## 1. Simple Description (For the Layperson)

Think of a **House (Bhāva)** in astrology like a room or department in a person's life (for example, career, relationships, health, or wealth). 

For that department to succeed, three things are needed:
1. **The Manager's Capacity (Bhavādhipati Bala):** The planet that owns the house is the manager. If the manager is strong, energetic, and well-resourced (measured by its *Shadbala*, or six-fold strength), the house runs smoothly.
2. **The Room's Setup and Orientation (Bhava Digbala):** Each zodiac sign represents a specific type of creature or environment (human, four-legged animal, water creature, or insect). Just like humans do best in the living room and fish do best in water, houses gain directional power depending on which type of sign occupies them.
3. **Outside Help and Support (Bhava Dṛṣṭi Bala):** Are friendly, helpful planets looking into this house with encouraging light, or are stressful planets creating friction?
   - When the manager (house lord) looks back into its own room, it acts as a dedicated guardian and protects it—**provided it is not burned out by the Sun (*combust*) or deeply exhausted (*debilitated*)**. If weakened, its protective power is reduced.
   - When the overall chart ruler (*Lagneśa*, the Ascendant lord) looks into any room, it brings royal patronage and blessing to that life area.
   - If a demanding planet (like Saturn or Mars) lives in its own home sign, it takes pride in its property and acts constructively as a protector, rather than causing disturbance.

Beyond raw strength, this engine also evaluates practical health checks:
- **Boundary Leaks (Bhāva Sandhi):** Planets sitting right on the edge of a sign boundary (within $1^\circ$) leak their energy into the neighboring room.
- **Flanking Conditions (Kartarī):** Is the house protected by gentle benefics on both sides (*Śubhakartarī*), or squeezed by harsh malefics (*Pāpakartarī*)?
- **Triangulation (The Triad):** Evaluating the house from three distinct viewpoints: physical life (*Janma Lagna*), emotional experience (*Chandra Lagna*), and the natural cosmic significator (*Kāraka Lagna*), normalized to a fair scale.
- **Three Focal Points (DPK Ch. 15):** Checking if the house room itself, its manager, and its natural significator are thriving or under severe stress (*Bhavāt Bhavam* displacement into the 6th, 8th, or 12th from its home).
- **Living Beings Signification (*Kārakobhāvanāśāya*):** A solitary planet in the house it naturally rules can smother tangible relationships (e.g., Jupiter alone in the 5th for children, or Venus alone in the 7th for marriage), but Saturn alone in the 8th is an exception because it grants a long, enduring life (*Āyuṣkāraka*).

---

## 2. Architectural Boundaries & Separation of Concerns

To avoid circular dependency and diagnostic distortion, the pipeline enforces strict architectural separation between **Stage 3** (House Capacity & Environmental Health) and **Stage 4** (Event Yogas & Predictive Destiny):

### In Scope for Stage 3 (`jyotish/bhavas/bhava_bala.py`):
- **Quantitative Parāśarī 3 Pillars (Virūpas / Rūpas):**
  1. Bhavādhipati Bala (Lord's total Ṣaḍbala Virūpas) [BPHS Ch. 27–30].
  2. Bhava Digbala (Sign genus directional strength: 0–60 Virūpas).
  3. Bhava Dṛṣṭi Bala (Aspect rays on cusp with universal Lord protection).
- **Mantreśvara Diagnostic Additions (Phaladīpikā Ch. 4, 14, 15):**
  1. Lord Digbala recount and Sign Gender vs. Diurnal Sect match (+15 Virūpas).
  2. Structural Boundary Checks: Bhāva Sandhi (<1° or >29° edge leakage).
  3. Ambient Room Flanking: Kartarī analysis (Śubhakartarī vs. Pāpakartarī as environmental weather, attenuated by lord presence).
  4. Lord Health & Displacement: Lord combustion, debilitation, war defeat, and Bhavāt Bhavam distance (6/8/12 from home sign vs. Upacaya growth).
  5. The Three Focal Points Rule (Bhāva, Bhāveśa, Kāraka per DPK 15.1–3, 18).
  6. Triad Triangulation (DPK 15.6: Janma Lagna, Candra Lagna, Kāraka Lagna).
  7. Kārakobhāvanāśāya (Strictly Jīva-kārakas, honoring Saturn in 8th and own-sign exemptions).
- **Output Deliverable:** Baseline House Capacity and Atmosphere rating classified strictly into three tiers:
  - `Puṣṭa` (Fortified / Flourishing: $\ge +25.0$)
  - `Miśra` (Mixed / Dynamic / Resilient: $-20.0 \text{ to } +25.0$)
  - `Hīna` (Deficient / Afflicted: $\le -20.0$)

### Strictly Out of Scope for Stage 3 (Delegated to Stage 4 `yogas/`):
- **NO Event-Producing Yogas:** Do not inject point bonuses or penalties for Rāja Yogas, Dhana Yogas, Mahāpuruṣa Yogas, or Parivartana Yogas into Bhāva Bala.
- **NO Formal Viparīta Points Injection:** Tajika Planetary Joy (Mars in 6th, Saturn in 12th) and Harsha Bala joy units may be reported as informational planetary joy metrics, but formal Viparīta Rāja Yogas (Harṣa, Sarala, Vimala) must NOT inject flat $+25.0$ bonuses that override structural house assessments.
- **NO Predictive Destiny Scoring:** Stage 3 evaluates the **structural room and manager**; Stage 4 evaluates the **destiny events occurring within that room**.

---

## 3. Technical Architecture & Mathematical Foundations

Modifications to `jyotish/bhavas/bhava_bala.py` must strictly adhere to the following mathematical laws and scriptural proofs:

### A. The 3 Quantitative Parāśarī Pillars

#### 1. Bhavādhipati Bala (*Tulyaṃ Svāmibalena*)
Baseline house strength equals the total Shadbala Virūpas of the house lord:
$$\text{Bhavādhipati Bala} = \text{Shadbala}_{\text{Virūpas}}(\text{Lord})$$

*Potency Normalization:* Assess lord strength against Parāśarī required minimum virūpas (BPHS Ch. 27–30):
- Mercury: 420.0 Virūpas
- Sun / Jupiter: 390.0 Virūpas
- Moon: 360.0 Virūpas
- Venus: 330.0 Virūpas
- Mars / Saturn: 300.0 Virūpas

$$\text{Potency Ratio} = \frac{\text{Lord Virūpas}}{\text{Required Virūpas}}$$

*Continuous Gradient (Elimination of Binary Cliff):*
Rather than penalizing planets right below 100% threshold with a flat $-10.0$ cliff, Stage 3 provides a 5% grace tolerance ($Ratio \ge 0.95$). If $Ratio < 0.95$, calculate proportional deficit:
$$\text{Deficit Ratio} = \frac{\text{Required} - \text{Virūpas}}{\text{Required}}$$
$$\text{Penalty} = \text{round}(\text{Deficit Ratio} \times 10.0, 1)$$
*(A planet at 96.8% incurs 0 penalty. A planet at 70% incurs $-3.0$ points.)*

#### 2. Bhava Digbala (Directional Capacity: 0 to 60 Virūpas)
Signs are classified by biological genus per BPHS Ch. 27:
- **Nara (Human):** Gemini, Virgo, Libra, Aquarius, Sagittarius $0^\circ\text{--}15^\circ$.
  - Peak: 1st House (60 Virūpas), Zero: 7th House (0 Virūpas).
- **Chathushpada (Quadruped):** Aries, Taurus, Leo, Sagittarius $15^\circ\text{--}30^\circ$, Capricorn $0^\circ\text{--}15^\circ$.
  - Peak: 10th House (60 Virūpas), Zero: 4th House (0 Virūpas).
- **Jalachara (Watery):** Cancer, Pisces, Capricorn $15^\circ\text{--}30^\circ$.
  - Peak: 4th House (60 Virūpas), Zero: 10th House (0 Virūpas).
- **Keeta (Insect):** Scorpio.
  - Peak: 7th House (60 Virūpas), Zero: 1st House (0 Virūpas).

$$\text{Distance} = |h - \text{Zero House}| \pmod{12}$$
$$\text{If } \text{Distance} > 6: \quad \text{Distance} = 12 - \text{Distance}$$
$$\text{Bhava Digbala} = \text{Distance} \times 10.0 \text{ Virūpas}$$

##### 3. Bhava Dṛṣṭi Bala (Aspect Rays on Bhava Madhya)
Aspect rays cast upon the cusp longitude ($0\text{--}60$ Virūpas):
- **Phaladeepika 15.1–3 House Lord Protection Rule (Conditioned by Combustion & Debilitation):**
  - If the aspecting planet is the lord of the aspected house, its aspect is protective ($+1.0 \times \text{Ray}$), even for natural malefics (e.g. Saturn aspecting Capricorn/Aquarius, Mars aspecting Aries/Scorpio).
  - **Canonical Qualification:** If the lord is combust (*mūḍha/asta*) or debilitated (*hīna/nīca*), its defense is severely impaired and scaled down to $+0.25 \times \text{Ray}$.
- **Parāśarī & Dr. B.V. Raman Beneficence Calibration (*Graha and Bhava Balas* Art. 132 & Example 59 Footnote):**
  - Mercury (*Budha*) and Jupiter (*Guru*) are ALWAYS evaluated as full benefics for Bhava Drishti Bala per the classical dictum *Gurugnabhyam tu yuktasya poornamekam tu yojayet*. Mercury is **never** treated as a $-0.25$ malefic in Bhava Drishti Bala, even when combust or associated with malefics.
  - In `dpk_qualified` mode (default): Jupiter & Mercury receive $+1.0 \times \text{Ray}$ (scaled down to $+0.5 \times \text{Ray}$ if combust or debilitated). Venus and benefic Moon receive $+0.25 \times \text{Ray}$. Natural malefics receive $-0.25 \times \text{Ray}$.
  - In `sripati_raman` mode: Jupiter and Mercury receive $+1.0 \times \text{Ray}$ unconditionally. Venus and benefic Moon receive $+0.25 \times \text{Ray}$. Natural malefics receive $-0.25 \times \text{Ray}$ without house-lord inversion.
- **Parāśarī Quantitative Purity (BPHS Ch. 27 v. 28–29):** The Ascendant Lord (*Lagneśa*) aspecting other houses does NOT receive $+1.0$ inversion in quantitative Virūpas (preventing Kuja Doṣa on the 7th cusp from registering as a benefic ray). Rather, Lagneśa aspect is evaluated qualitatively in House Atmosphere per DPK 15.9 ($+15.0$).

---

### B. Mantreśvara’s *Phaladeepika* Diagnostic Layer (Ch. 4, 6, 14, 15, 16)

1. **Lord's Digbala Re-Count (DPK Ch. 4):** Houses are directional structures (*diśā*). The directional strength of the house lord (`Dig_Bala`) is added as an augmented bonus to the house.
2. **Sign Gender vs. Diurnal Sect (DPK Ch. 4):**
   - Day birth + Odd (masculine) sign: $+15$ Virūpas.
   - Night birth + Even (feminine) sign: $+15$ Virūpas.
3. **Bhāva Sandhi, Residential Strength & Wall Leakage (*Graha and Bhava Balas* Ch. II & DPK Ch. 14):**
   - **Residential Strength:** Evaluated for all occupants from $0.0$ at sign/bhava borders (*Arambha/Virama Sandhi*) to $1.0$ at the house midpoint (*Bhavamadhya* at $15^\circ$) per Dr. B.V. Raman Art. 14–16.
   - **Wall Leakage:** Occupants within $1.0^\circ$ of a sign border ($<1^\circ$ or $>29^\circ$) exhibit cross-border energy leakage with a proportional leakage ratio, penalizing the house in Atmosphere.
   - **Whole-Sign Cusp Isolation:** In `whole_sign` mode, an Ascendant degree near borders ($<1^\circ$ or $>29^\circ$) isolates `cusp_in_sandhi` strictly to House 1 rather than broadcasting a blanket penalty across all 12 houses.
4. **Neutralization of Malefics in Own Sign & Upacaya Dynamics (DPK 15.1, 4.23):** 
   - When a natural malefic occupies its own sign (*svakṣetra*), it functions as a supportive house lord (*svakṣetre śubhakṛt*), routing to benefics and receiving $+15.0$ atmospheric bonus rather than malefic non-upacaya penalties.
   - In Upacaya houses (3, 6, 10, 11), a malefic lord in its own sign also empowers growth ($+10.0$) and activates the `satruhanta_active` flag in House 6 (conqueror of enemies/obstacles).
   - When any house lord occupies an Upacaya house (3, 6, 10, 11) from Janma Lagna without dusthāna corruption, it experiences steady expansion and growth per DPK 4.23 (`is_in_upacaya_from_lagna`).
5. **Ambient Room Flanking (Kartarī) & Resident Lord Dampening:**
   - **Śubhakartarī:** House flanked by benefics on both sides ($+20.0$).
   - **Pāpakartarī:** House besieged between malefics ($-20.0$).
   - Dynamic classification of Moon (by Paksha Bala) and Mercury (combustion/malefic conjunction) is strictly unified across Kartari and Focal Point diagnostics.
   - **50% Dampening Rule:** When `lord_resident_unblemished` is True, the scissor siege constricts worldly ease but cannot demolish the internal room; the penalty is dampened by 50% (from $-20.0$ to $-10.0$).
6. **Context-Sensitive Dispositor Modulation for Lunar Nodes (*Yad Yad Bhāvagatāvapi...*):**
   - In *Phaladīpikā* Ch. 14 & 20, Rahu and Ketu reflect their dispositor and conjunctions.
   - Conjoined an unblemished domicile lord in non-upacaya houses (e.g. Ketu with Jupiter in 5th Sagittarius), node penalty is attenuated from $-15.0$ to $-3.0$ reflecting ascetic renunciation (*Jñāna*), spiritual intellect (*Dhī*), and *Mantra Siddhi*.
7. **Lagneśa Flourishing Rule & Major Ray Threshold (DPK 15.9):** 
   - Presence of the Ascendant lord in houses $h \neq 1$ confers an automatic $+15.0$ flourishing bonus (in House 1, the bonus is cleanly awarded once under resident lord).
   - An aspect from the Ascendant lord must carry at least a palpable half-glance ($\ge 30.0$ Virūpas) to trigger the $+15.0$ flourishing bonus, preventing sub-perceptual non-zero aspects from artificially inflating the chart.
8. **Bhavāt Bhavam Upacayas vs. Lagna Dusthāna & Displaced Lord Penalties (DPK 15.1, 15.3, 15.5 & 15.29):**
   - **Enemy Sign (Ari-kṣetra):** Per DPK 15.1 (*nīcamūḍhārihīnaiḥ*) and DPK 15.3 (*nīcārātigṛhaṃ gato*), a house lord in an enemy sign cannot be classified as strong (`is_strong = False`) and incurs a $-10.0$ penalty in Atmosphere.
   - **Lagna Dusthāna Placement (DPK 15.5):** When a house lord is placed in the 6th, 8th, or 12th from Lagna without own-sign or exaltation status, it suffers dusthāna corruption ($-15.0$ in Atmosphere), even if its Bhavāt Bhavam distance is not 6, 8, or 12.
   - **Incoming Dusthāna Lords (DPK 15.5 & 15.29):** An incoming 6th, 8th, or 12th lord occupying another house incurs $-10.0$ per unexempted lord. Per DPK 15.29 (*duḥsthānapastaditarasvagṛhasthitaścet*), if a dusthāna lord occupies its own other sign, it produces only the auspicious results of its own sign and incurs zero dusthāna blemish.
   - **Bhavāt Bhavam Upacayas:** Uncorrupted growth from the evaluated house is fostered strictly by Upacayas **3, 10, and 11** from that house ($+10.0$).
9. **Kārakobhāvanāśāya (Restricted to Living Significations / Jīva-Kārakas per BPHS & DPK Ch. 15–16):**
   Evaluated strictly across the six living relationship houses:
   - House 3: Mars (Younger siblings)
   - House 4: Moon (Mother)
   - House 5: Jupiter (Progeny)
   - House 7: Venus (Spouse/Partner)
   - House 9: Sun (Father)
   - House 11: Jupiter (Elder siblings)
   - **Affliction & Relief Rules:**
     - The affliction triggers when the natural significator occupies the house without another dynamic benefic.
     - Co-occupancy by another dynamic benefic relieves the affliction.
     - **Canonical Exceptions:**
       - House 8 with solitary Saturn is explicitly protected (*Āyuṣkāraka* promotes longevity).
       - **DPK 16.1–3 Exemption:** A kāraka occupying its own sign (*svabhavana*) or sign of exaltation (*svoccha*) is fortified and exempt from Kārakobhāvanāśāya.
   - Non-living houses (1, 2, 6, 10, 12) never trigger Kārakobhāvanāśāya.
10. **Normalized DPK Triad Triangulation (DPK Ch. 15 Text 6):**
    Evaluated from Janma Lagna (Weight 1.0), Chandra Lagna (Weight 0.5), and Kāraka Lagna (Weight 0.25), normalized by total weight ($1.75$):
    Per DPK 15.6, the Kāraka Lagna evaluation averages both the potency of the house dispositor counted from the Kāraka and the natural Kāraka planet(s) (averaging all primary karakas for multi-karaka houses like House 9):
    $$p_{\text{karaka}} = \frac{p_{\text{karaka\_house\_lord}} + p_{\text{karaka\_graha}}}{2.0}$$
    $$\text{composite\_potency} = \frac{(1.0 \times p_{\text{asc}}) + (0.5 \times p_{\text{chandra}}) + (0.25 \times p_{\text{karaka}})}{1.75}$$
11. **3-Focal-Point Rule (DPK Ch. 15 Texts 1–3, 6, 18) & Sva-kṣetra Veto Floor:**
    - **Point 1 (The Bhāva):** Afflicted if strictly besieged between malefics (*Pāpakartarī* without benefic relief) or occupied by $\ge 2$ malefics (excluding its lord). Dusthāna houses (6, 8, 12) are not self-ruining.
    - **Point 2 (The Lord / Bhāveśa):** Afflicted if placed in the 6th, 8th, or 12th from its own sign or in Lagna Dusthāna (without own/exaltation sign), strictly besieged, depleted in Ṣaḍbala ($< 90\%$), debilitated (*Hīna*), combust (*Mūḍha*), or in enemy sign (*Ari-kṣetra* per DPK 15.1/15.3).
    - **Point 3 (The Kāraka):** Afflicted if placed in a dusthāna from Lagna (except Saturn in the 8th), strictly besieged, depleted in Ṣaḍbala ($< 90\%$), debilitated, or combust. Missing kārakas are safely handled without defaulting to $0.0^\circ$ Aries.
    - **Ruination Verdict & Sva-kṣetra Veto Floor:** Total ruin (*vad-bhāva*) requires $\ge 2$ focal points afflicted per DPK 15.6 (*dvitrisaṃvādabhāvāt*). When an unblemished house lord is resident at home (`lord_resident_unblemished`), Bhāva and Bhāveśa are anchored:
      - Vad-Bhāva ruination penalty is vetoed.
      - An unconditional mathematical floor is enforced: house score cannot drop below $-10.0$.
      - The house CANNOT be classified as `Hīna` under any circumstances.
12. **Single Source of Truth Synthesis:** Root `classification` and `summary_verdict` are synchronized directly from the continuous 12-House Atmosphere model:
    - **Puṣṭa** (Fortified / Flourishing: $\ge +25.0$)
    - **Miśra** (Mixed / Dynamic / Resilient: $-20.0 \text{ to } +25.0$)
    - **Hīna** (Deficient / Afflicted: $\le -20.0$)

---

### C. Harsha Bala (P.V.R. Narasimha Rao Ch. 28.3 & Informational Planetary Joy)

Harsha Bala ("Strength of Cheerfulness") measures the inner joy, comfort, and natural resilience of the seven classical planets:
1. **Sthāna Bala (Joy House):** Sun in 9th, Moon in 3rd, Mars in 6th, Mercury in 1st, Jupiter in 11th, Venus in 5th, Saturn in 12th ($+5$ units). Missing planets do not default to $0.0^\circ$ Aries.
2. **Uccha / Sva Kṣetra (Exaltation or Own Sign):** $+5$ units.
3. **Strī / Puruṣa Bhāva (Gender & House Match):** Feminine planets (Moon, Mercury, Venus, Saturn) in houses 1, 2, 3, 7, 8, 9; Masculine planets (Sun, Mars, Jupiter) in houses 4, 5, 6, 10, 11, 12 ($+5$ units).
4. **Dina / Rātri Bala (Diurnal / Nocturnal Sect Match):** Day birth rewards masculine planets ($+5$ units); Night birth rewards feminine planets ($+5$ units).

**Dusthana Reversals: Informational Diagnostics vs. Stage 4 Event Yogas:**
- **Harsha, Sarala, and Vimala Yogas:**
  Reported strictly as informational metrics in Stage 3 (`bhava_results[h]["harsha_bala"]`). Formal Viparīta Rāja Yogas do NOT inject flat $+25.0$ bonuses into Stage 3 atmosphere, allowing dusthāna houses (6, 8, 12) to be evaluated cleanly on their actual structural capacity.
- **Tajika Planetary Joy:**
  - **Mars in 6th House:** Planetary joy and Upacaya courage (*Śatruhantā*).
  - **Saturn in 12th House:** Planetary joy and ascetic detachment.

---

### D. Unified House Atmosphere & Environmental Weather Model

Synthesizes the net constructive vs friction forces acting on each house into a continuous score ($-100.0$ to $+100.0$):
- **Baseline Capacity:** Ingests `augmented_virupas` (incorporating Parāśarī capacity, lord Digbala re-count, and sign/sect bonuses per DPK Ch. 4).
- **Positive Forces:**
  - Fortified lord ($\ge 1.0\times$ without debilitation, combustion, or war defeat): $+15.0$.
  - Dynamic benefic occupants (including bright Moon and unafflicted Mercury): $+10.0$.
  - Resident house lord: $+15.0$.
  - Ascetic node moderation (Rahu/Ketu with unblemished resident lord): $-3.0$ (attenuated from $-15.0$).
  - Lagneśa presence or major aspect ray ($\ge 30$v): $+15.0$.
  - Net supportive drishti rays ($\text{drishti} > 10.0$v): up to $+25.0$.
  - Śubhakartarī (flanked by benefics): $+20.0$.
  - Lord in Lagna Upacaya growth (DPK 4.23): $+10.0$.
  - Constructive malefic lord in own Upacaya sign (3, 6, 10, 11) (Śatruhantā active in H6): $+10.0$.
  - Constructive malefic in Upacaya (3, 6, 10, 11): $+10.0$.
  - Exceptional Triad concordance: $+10.0$.
- **Negative Forces:**
  - Debilitated lord (DPK 15.1 *Hīna*): $-20.0$.
  - Combust lord (DPK 15.1 *Mūḍha*): $-20.0$.
  - Defeated lord in planetary war (*Nīpīḍita*): $-15.0$.
  - Lord in enemy sign (Ari-kṣetra per DPK 15.1/15.3): $-10.0$.
  - Lord in Lagna Dusthāna (6, 8, 12 per DPK 15.5): $-15.0$ (when not already penalized by Bhavat Bhavam).
  - Incoming Dusthāna lord occupying (DPK 15.5, excluding Lagna lord and own-sign per DPK 15.29): $-10.0$.
  - Proportional Ṣaḍbala deficit ($Ratio < 0.95$): up to $-10.0$ gradient ($0.0$ penalty if $Ratio \ge 0.95$).
  - Dynamic malefic occupants in non-upacaya houses: $-15.0$.
  - Net confronting drishti rays ($\text{drishti} < -10.0$v): up to $-25.0$.
  - Pāpakartarī siege: $-20.0$ (dampened to $-10.0$ if lord is resident unblemished).
  - Bhāva Sandhi border leakage ($<1^\circ$ or $>29^\circ$): $-15.0$.
  - Wall leakage: up to $-10.0$ (scaled to occupant boundary proximity ratio $\text{round}(10.0 \times \text{max\_ratio}, 1)$).
  - Bhavāt Bhavam dusthāna displacement ($+6, +8, +12$ for non-dusthāna houses): $-15.0$.
  - Afflicted Kārakobhāvanāśāya (living significations only): $-15.0$.
  - Latent Triad concordance: $-10.0$.
  - Vad-Bhāva ruination under 3 Focal Points (DPK 15.18): $-25.0$ (vetoed if lord is resident unblemished).
- **Sva-kṣetra Veto Floor:**
  - If `lord_resident_unblemished`, score cannot drop below $-10.0$.
- **Classifications:**
  - `Puṣṭa` ($\ge +25.0$): Radiant & Unopposed ($\ge 40.0$) or Supportive & Productive ($\ge 20.0$).
  - `Miśra` ($-20.0 \text{ to } +25.0$): Tempered & Resilient ($\ge 0.0$) or Frictional & Demanding ($< 0.0$).
  - `Hīna` ($\le -20.0$): Turbulent & Obstructed.

---

### E. Hemisphere A Pure Return Schemas & Dictionary Signatures

In strict accordance with the Two-Hemisphere Architectural Law in `GEMINI.md`, `jyotish/bhavas/bhava_bala.py` is certified Hemisphere A (Foundational Calculus). It produces pure mathematical primitives (floats, ints, bools, string enums) and zero UI HTML or Hemisphere B psychological archetypes:

#### 1. `calculate_bhava_bala` Return Schema (`Dict[int, Dict[str, Any]]`)
For each house $h \in [1..12]$:
```python
{
    "house": int,                     # 1 to 12
    "lord": str,                      # Sanskrit planet name (e.g., "Mars", "Jupiter")
    "bhava_madhya": float,            # Cusp longitude in degrees [0.0, 360.0)
    "bhavadhipathi_bala": float,      # Total Shadbala Virupas of house lord
    "bhava_digbala": float,           # Directional Virupas (0.0 to 60.0)
    "bhava_drishti_bala": float,      # Net aspect rays on cusp (Virupas)
    "total_virupas": float,           # Adhipati + Digbala + Drishti
    "total_rupas": float,             # total_virupas / 60.0
    "augmented_virupas": float,       # Virupas + Lord Digbala + Sect bonus
    "lord_dig_bala_bonus": float,     # DPK Ch. 4 Lord Digbala Virupas
    "sect_bonus": float,              # DPK Ch. 4 Day/Night Sign Sect Virupas (0.0 or 15.0)
    "sign": str,                      # Zodiac sign name (e.g., "Aries")
    "sign_genus": str,                # "Nara", "Chathushpada", "Jalachara", "Keeta"
    "occupants": list,                # Raw list of occupant records
    "occupant_diagnostics": {
        "benefics": list[str],
        "malefics": list[str],
        "is_upacaya": bool,
        "upacaya_empowered": bool,
        "satruhanta_active": bool,
        "lagnesha_present": bool,
        "dusthana_lords_occupying": list[str]
    },
    "sandhi_analysis": {
        "cusp_in_sandhi": bool,
        "cusp_dist_to_border": float,
        "wall_leakages": list[dict],
        "residential_strengths": dict[str, float]
    },
    "kartari_yoga": {
        "type": str,                  # "neutral", "shubhakartari", "papakartari", "mixed"
        "flanking_12th": dict,
        "flanking_2nd": dict
    },
    "lord_status": {
        "lord": str,
        "placed_house": int,
        "placed_sign": str,
        "bhavat_bhavam_distance": int,
        "is_in_kendra": bool,
        "is_in_trikona": bool,
        "is_in_dusthana": bool,
        "is_in_upacaya_from_bhava": bool,
        "is_in_upacaya_from_lagna": bool,
        "is_debilitated": bool,
        "is_combust": bool,
        "in_war": bool,
        "is_defeated": bool,
        "is_in_enemy_sign": bool,
        "is_strong": bool,
        "potency_ratio": float
    },
    "karaka_analysis": {
        "primary_karakas": list[str],
        "is_afflicted": bool,
        "details": str
    },
    "dpk_triad": {
        "from_janma_lagna": dict,
        "from_chandra_lagna": dict,
        "from_karaka_lagna": dict,
        "concordance": str,
        "concordance_score": float,
        "weighted_triad_potency": float
    },
    "three_focal_points": {
        "afflicted_points_count": int,
        "is_ruined": bool,
        "details": str
    },
    "lagnesha_aspecting": bool,
    "classification": str,            # "Puṣṭa", "Miśra", or "Hīna" (synchronized with Atmosphere)
    "summary_verdict": str,
    "harsha_bala": dict,              # Dusthana joy diagnostic entry for this house
    "atmosphere": dict                # Complete House Atmosphere payload
}
```

#### 2. `calculate_harsha_bala` Return Schema (`Dict[str, Any]`)
```python
{
    "planets": {
        "<PlanetName>": {
            "planet": str,
            "placed_house": int,
            "placed_sign": str,
            "sthana_bala_units": float,       # 0.0 or 5.0
            "uccha_swakshetra_units": float,  # 0.0 or 5.0
            "stree_purusha_units": float,     # 0.0 or 5.0
            "dina_ratri_units": float,        # 0.0 or 5.0
            "total_units": float,             # 0.0 to 20.0
            "max_units": 20.0,
            "strength_category": str,         # Sanskrit classification
            "is_in_joy_house": bool
        }
    },
    "dusthana_joy": {
        6: {
            "house": 6,
            "yoga_name": "Harsha",
            "is_active": bool,
            "lord_in_house": bool,
            "viparita_active": bool,
            "karaka_joy_in_house": bool,
            "planetary_joy_active": bool,
            "bonus_units": float,
            "effect": str
        },
        8: { ... },
        12: { ... }
    }
}
```

#### 3. `calculate_house_atmosphere` Return Schema (`Dict[int, Dict[str, Any]]`)
```python
{
    "house": int,
    "sign": str,
    "lord": str,
    "net_atmosphere_score": float,       # Continuous score between -100.0 and +100.0
    "base_virupas": float,
    "augmented_virupas": float,
    "classification": str,               # "Puṣṭa (Fortified / Flourishing)", "Miśra (Mixed / Dynamic / Resilient)", or "Hīna (Deficient / Afflicted)"
    "environmental_weather": str,        # "Radiant & Unopposed", "Supportive & Productive", "Tempered & Resilient", "Frictional & Demanding", or "Turbulent & Obstructed"
    "auspicious_influences": list[str],  # Itemized positive factors
    "inauspicious_influences": list[str],# Itemized negative factors
    "harsha_bala_active": bool,
    "verdict": str
}
```


