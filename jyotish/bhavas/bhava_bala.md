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

## 2. Technical Architecture & Mathematical Foundations

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
- **Parāśarī Quantitative Purity (BPHS Ch. 27 v. 28–29):** The Ascendant Lord (*Lagneśa*) aspecting other houses does NOT receive $+1.0$ inversion in quantitative Virūpas (preventing Kuja Doṣa on the 7th cusp from registering as a benefic ray). Rather, Lagneśa aspect is evaluated qualitatively in House Atmosphere per DPK 15.9 ($+15.0$).
- **Jupiter & Benefic Mercury:** $+1.0 \times \text{Ray}$ (scaled down to $+0.5 \times \text{Ray}$ if combust or debilitated).
- **Venus & Benefic Moon ($\text{Paksha Bala} \ge 30$):** $+0.25 \times \text{Ray}$.
- **Natural Malefics (Sun, Mars, Saturn, Dark Moon, Afflicted Mercury):** $-0.25 \times \text{Ray}$ (unless aspecting own house).

---

### B. Mantreśvara’s *Phaladeepika* Diagnostic Layer (Ch. 4, 6, 14, 15, 16)

1. **Lord's Digbala Re-Count (DPK Ch. 4):** Houses are directional structures (*diśā*). The directional strength of the house lord (`Dig_Bala`) is added as an augmented bonus to the house.
2. **Sign Gender vs. Diurnal Sect (DPK Ch. 4):**
   - Day birth + Odd (masculine) sign: $+15$ Virūpas.
   - Night birth + Even (feminine) sign: $+15$ Virūpas.
3. **Bhāva Sandhi & Wall Leakage (DPK Ch. 14):**
   - Cusps or occupants within $1.0^\circ$ of a sign border ($<1^\circ$ or $>29^\circ$) exhibit cross-border energy leakage with a directional transfer ratio. Non-planetary points (Lagna, MC) are excluded from occupant calculations.
4. **Neutralization of Malefics in Own Sign & Upacaya Dynamics (DPK 15.1, 4.23):** 
   - When a natural malefic occupies its own sign (*svakṣetra*), it functions as a supportive house lord (*svakṣetre śubhakṛt*), routing to benefics and receiving $+15.0$ atmospheric bonus rather than malefic non-upacaya penalties.
   - In Upacaya houses (3, 6, 11), a malefic lord in its own sign also empowers growth and activates the `satruhanta_active` flag in House 6 (conqueror of enemies/obstacles).
   - When any house lord occupies an Upacaya house (3, 6, 10, 11) from Janma Lagna without dusthāna corruption, it experiences steady expansion and growth per DPK 4.23 (`is_in_upacaya_from_lagna`).
5. **Upacaya Malefic Dynamics & Śatruhantā:** Malefics occupying Upacaya houses (3, 6, 11) empower the native. Malefics in the 6th house activate the `satruhanta_active` flag.
6. **Lagneśa Flourishing Rule & Major Ray Threshold (DPK 15.9):** 
   - Presence of the Ascendant lord in houses $h \neq 1$ confers an automatic $+15.0$ flourishing bonus (in House 1, the bonus is cleanly awarded once under resident lord).
   - An aspect from the Ascendant lord must carry at least a palpable half-glance ($\ge 30.0$ Virūpas) to trigger the $+15.0$ flourishing bonus, preventing sub-perceptual non-zero aspects from artificially inflating the chart.
7. **Bhavāt Bhavam Upacayas vs. Trika Dusthāna Displacement:**
   - Uncorrupted growth from the evaluated house is fostered strictly by Upacayas **3, 10, and 11** from that house.
   - Displacement into the **6th, 8th, or 12th from its home sign** is a Trika dusthāna displacement causing house decay (*bhāva-nāśa* per DPK 15.2–3) and receives a $-15.0$ penalty without simultaneous Upacaya reward. This penalty applies strictly to non-dusthāna houses ($h \notin \{6, 8, 12\}$); dusthāna houses are governed by Harsha/Sarala/Vimala yogas and Upacaya expansion dynamics.
8. **Own-Dusthāna Lord Exemption & Viparīta Yogas (Houses 6, 8, 12):**
   - When a lord of house 6, 8, or 12 resides in ANY dusthāna (6, 8, 12), it forms an auspicious *Harṣa*, *Sarala*, or *Vimala* Yoga per DPK 6.57–70.
   - It is exempt from `is_in_dusthana` displacement penalties (`(lord_house in DUHSTHANA_HOUSES) and not (house_num in DUHSTHANA_HOUSES)`).
9. **Kārakobhāvanāśāya (Restricted to Living Significations / Jīva-Kārakas):**
   Solitary occupancy by the primary natural significator impairs living relationships:
   - House 3: Mars (Younger siblings)
   - House 5: Jupiter (Progeny)
   - House 7: Venus (Spouse/Partner)
   - House 9: Sun (Father)
   - **Canonical Exceptions:** 
     - House 8 with solitary Saturn is explicitly protected (*Āyuṣkāraka* promotes longevity).
     - **DPK 16.1–3 Exemption:** A solitary kāraka occupying its own sign (*svabhavana*) or sign of exaltation (*svoccha*) is fortified and exempt from Kārakobhāvanāśāya.
   - Non-living houses (2, 4, 10, 11, 12) never trigger Kārakobhāvanāśāya.
10. **Normalized DPK Triad Triangulation (DPK Ch. 15 Text 6):**
    Evaluated from Janma Lagna (Weight 1.0), Chandra Lagna (Weight 0.5), and Kāraka Lagna (Weight 0.25), normalized by total weight ($1.75$):
    Per DPK 15.6, the Kāraka Lagna evaluation averages both the potency of the house dispositor counted from the Kāraka and the natural Kāraka planet itself:
    $$p_{\text{karaka}} = \frac{p_{\text{karaka\_house\_lord}} + p_{\text{karaka\_graha}}}{2.0}$$
    $$\text{composite\_potency} = \frac{(1.0 \times p_{\text{asc}}) + (0.5 \times p_{\text{chandra}}) + (0.25 \times p_{\text{karaka}})}{1.75}$$
11. **3-Focal-Point Rule (DPK Ch. 15 Texts 1–3, 18) & Bhavāt Bhavam:**
    - **Point 1 (The Bhāva):** Afflicted if strictly besieged between malefics (*Pāpakartarī* without benefic relief) or occupied by $\ge 2$ malefics (excluding its lord). Dusthāna houses (6, 8, 12) are not self-ruining.
    - **Point 2 (The Lord / Bhāveśa):** Afflicted if placed in the 6th, 8th, or 12th from its own sign (except own-dusthāna lords residing in dusthānas), strictly besieged, depleted in Ṣaḍbala ($< 90\%$), debilitated (*Hīna*), or combust (*Mūḍha* per DPK 15.1).
    - **Point 3 (The Kāraka):** Afflicted if placed in a dusthāna from Lagna (except Saturn in the 8th), strictly besieged, depleted in Ṣaḍbala ($< 90\%$), debilitated, or combust. Missing kārakas are safely handled without defaulting to $0.0^\circ$ Aries.
    - **Ruination Verdict:** If $\ge 2$ focal points are afflicted, the house is classified as ruined (*vad-bhāva / bhad-bhāva*).
12. **Single Source of Truth Synthesis:** Root `classification` and `summary_verdict` are synchronized directly from the continuous 12-House Atmosphere model, eliminating split classification discrepancies across consumers:
    - **Puṣṭa** (Fortified/Flourishing)
    - **Miśra** (Balanced/Mixed)
    - **Hīna** (Depleted/Afflicted)

---

### C. Harsha Bala (P.V.R. Narasimha Rao Ch. 28.3 & Dusthana Joy Reversals)

Harsha Bala ("Strength of Cheerfulness") measures the inner joy, comfort, and natural resilience of the seven classical planets:
1. **Sthāna Bala (Joy House):** Sun in 9th, Moon in 3rd, Mars in 6th, Mercury in 1st, Jupiter in 11th, Venus in 5th, Saturn in 12th ($+5$ units). Missing planets do not default to $0.0^\circ$ Aries.
2. **Uccha / Sva Kṣetra (Exaltation or Own Sign):** $+5$ units.
3. **Strī / Puruṣa Bhāva (Gender & House Match):** Feminine planets (Moon, Mercury, Venus, Saturn) in houses 1, 2, 3, 7, 8, 9; Masculine planets (Sun, Mars, Jupiter) in houses 4, 5, 6, 10, 11, 12 ($+5$ units).
4. **Dina / Rātri Bala (Diurnal / Nocturnal Sect Match):** Day birth rewards masculine planets ($+5$ units); Night birth rewards feminine planets ($+5$ units).

**Dusthana Reversals: Disentangling Canonical Viparīta Yogas from Tajika Joy:**
- **Canonical Viparīta Yogas (Phaladīpikā 6.57–70):**
  - **Harsha Yoga (6th House):** 6th lord in 6th, 8th, or 12th house converts debt and enemies into victory and immunity.
  - **Sarala Yoga (8th House):** 8th lord in 6th, 8th, or 12th house converts crisis into fearless endurance and longevity.
  - **Vimala Yoga (12th House):** 12th lord in 6th, 8th, or 12th house converts loss and solitude into spiritual release and detachment.
- **Tajika Planetary Joy:**
  - **Mars in 6th House:** Planetary joy and Upacaya courage (*Śatruhantā*), distinct from Harsha Yoga.
  - **Saturn in 12th House:** Planetary joy and ascetic detachment, distinct from Vimala Yoga.

---

### D. Unified House Atmosphere & Environmental Weather Model

Synthesizes the net constructive vs friction forces acting on each house into a continuous score ($-100.0$ to $+100.0$):
- **Baseline Capacity:** Ingests `augmented_virupas` (incorporating Parāśarī capacity, lord Digbala re-count, and sign/sect bonuses per DPK Ch. 4).
- **Positive Forces:** Fortified lord ($>1.0\times$ without debilitation or combustion: $+15.0$), benefic occupants, own-sign malefic protection ($+15.0$), Lagneśa presence or aspect ($+15.0$), protective drishti rays, Śubhakartarī, Upacaya from Lagna growth ($+10.0$), Upacaya malefic channeling, exceptional Triad concordance ($+10.0$), and Harsha/Viparita dusthana joy ($+25.0$).
- **Negative Forces:** Debilitated lord ($-20.0$ per DPK 15.1 *Hīna*), combust lord ($-20.0$ *Mūḍha*), defeated lord in war ($-15.0$ *Nīpīḍita*), deficient lord virūpas ($-10.0$), malefic occupants in non-upacaya houses, confrontational drishti, Pāpakartarī, Bhāva Sandhi border leakage, Bhavāt Bhavam dusthāna displacement ($+6, +8, +12$ for non-dusthāna houses: $-15.0$), afflicted Kārakobhāvanāśāya ($-15.0$), latent Triad concordance ($-10.0$), and Vad-Bhāva ruination under 3 Focal Points ($-25.0$ per DPK 15.18).
- **Classifications:**
  - `Puṣṭa` ($\ge +25.0$): Radiant, unopposed, or supportive.
  - `Miśra` ($-20.0 \text{ to } +25.0$): Tempered, dynamic, or resilient.
  - `Hīna` ($\le -20.0$): Frictional, demanding, or obstructed.

---

### E. Master Diagnostic Cockpit Payload (9-Column Architecture)

Stage 3 produces the authoritative backend payload matching ADR-006 design standards:
1. `Graha & Kāraka`: Motion state ([R], [C]), Chara Karaka soul role, and Master Lords.
2. `Longitude & Bhāva`: Formatted tropical coordinates, Whole Sign house, and expression.
3. `Dignity & Sambandha`: Synthesized Natural + Temporary (Pañcadhā Maitrī) dignity.
4. `Dispositor (Rāśi Lord)`: Host lord placement and cancellation rescue status.
5. `Ṣaḍbala Strength`: Virūpas, Rūpas, % of required minimum threshold, chart rank, and Ishta/Kashta.
6. `Dṛṣṭi & Yuti`: Conjunctions, palpable incoming aspects ($>20$v), and planetary war status.
7. `Nakṣatra & Pada`: Dhruva sidereal nakshatra, quarter pada, lords, deity, and Navatara.
8. `Avasthās`: Bālādi (age), Jāgradādi (alertness %), Dīptādi (mood), and Lajjitādi social states.
9. `Archetype & Vitality`: 9-Tier behavioral archetype, real-world manifesting vitality score ($1.0\text{--}10.0$), and hover receipt.
