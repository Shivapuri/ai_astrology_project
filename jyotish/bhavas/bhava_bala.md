# Jyotish Engine: Bhāva Bala (House Strength & Synthesis)

This module calculates **Bhāva Bala** (the overall strength and capacity of each of the 12 astrological houses) and combines it with classical diagnostics from Mantreśvara's *Phaladeepika*.

---

## 1. Simple Description (For the Layperson)

Think of a **House (Bhāva)** in astrology like a room or department in a person's life (for example, career, relationships, health, or wealth). 

For that department to succeed, three things are needed:
1. **The Manager's Capacity (Bhavādhipati Bala):** The planet that owns the house is the manager. If the manager is strong, energetic, and well-resourced (measured by its *Shadbala*, or six-fold strength), the house runs smoothly.
2. **The Room's Setup and Orientation (Bhava Digbala):** Each zodiac sign represents a specific type of creature or environment (human, four-legged animal, water creature, or insect). Just like humans do best in the living room and fish do best in water, houses gain directional power depending on which type of sign occupies them.
3. **Outside Help and Support (Bhava Dṛṣṭi Bala):** Are friendly, helpful planets looking into this house with encouraging light, or are stressful planets creating friction? Furthermore, if the manager itself looks back at its own department, it always protects and strengthens it, even if the manager has a tough or demanding personality.

Beyond raw strength, this engine also evaluates practical health checks:
- **Boundary Leaks (Bhāva Sandhi):** Planets sitting right on the edge of a sign boundary (within $1^\circ$) leak their energy into the neighboring room.
- **Flanking Conditions (Kartarī):** Is the house protected by gentle benefics on both sides (*Śubhakartarī*), or squeezed by harsh malefics (*Pāpakartarī*)?
- **Triangulation (The Triad):** Evaluating the house not only from the physical Ascendant (*Janma Lagna*), but also from the Moon's viewpoint (*Chandra Lagna*) and the natural significator's viewpoint (*Kāraka Lagna*).

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

#### 3. Bhava Dṛṣṭi Bala (Aspect Rays on Bhava Madhya)
Aspect rays cast upon the cusp longitude ($0\text{--}60$ Virūpas):
- **Phaladeepika 15.1–3 House Lord Protection Rule:** If the aspecting planet is the lord of the aspected house, its aspect is unconditionally protective ($+1.0 \times \text{Ray}$), even for natural malefics (e.g. Saturn aspecting Capricorn/Aquarius, Mars aspecting Aries/Scorpio).
- Jupiter & Benefic Mercury: $+1.0 \times \text{Ray}$.
- Venus & Benefic Moon ($\text{Paksha Bala} \ge 30$): $+0.25 \times \text{Ray}$.
- Malefics (Sun, Mars, Saturn, Dark Moon, Afflicted Mercury): $-0.25 \times \text{Ray}$ (unless aspecting own house).

---

### B. Mantreśvara’s *Phaladeepika* Diagnostic Layer (Ch. 4, 14, 15)

1. **Lord's Digbala Re-Count (DPK Ch. 4):** Houses are directional structures (*diśā*). The directional strength of the house lord (`Dig_Bala`) is added as an augmented bonus to the house.
2. **Sign Gender vs. Diurnal Sect (DPK Ch. 4):**
   - Day birth + Odd (masculine) sign: $+15$ Virūpas.
   - Night birth + Even (feminine) sign: $+15$ Virūpas.
3. **Bhāva Sandhi & Wall Leakage (DPK Ch. 14):**
   - Cusps or occupants within $1.0^\circ$ of a sign border ($<1^\circ$ or $>29^\circ$) exhibit cross-border energy leakage with a directional transfer ratio.
4. **Upacaya Malefic Dynamics & Śatruhantā:** Malefics occupying Upacaya houses (3, 6, 11) empower the native. Malefics in the 6th house activate the `satruhanta_active` flag (conqueror of enemies/obstacles).
5. **Kārakobhāvanāśāya Exception:** Solitary occupancy by the primary significator impairs living significations, EXCEPT Saturn in the 8th house, which protects longevity (*Āyuṣkāraka*).
6. **DPK Triad Triangulation (DPK Ch. 15 Text 6):**
   - Evaluated from Janma Lagna (Weight 1.0), Chandra Lagna (Weight 0.5), and Kāraka Lagna (Weight 0.25).
7. **3-Focal-Point Rule (DPK Ch. 15 Texts 1–3, 18):**
   - Assesses simultaneous affliction across (1) Bhāva itself, (2) Bhāveśa (Lord), and (3) Bhāva Kāraka. Affliction of $\ge 2$ points flags the house as ruined/decayed (*bhad-bhāva*).
8. **Final Synthesis:** Synthesizes qualitative classification into:
   - **Puṣṭa** (Fortified/Flourishing)
   - **Miśra** (Balanced/Mixed)
   - **Hīna** (Depleted/Afflicted)

---

### C. Harsha Bala (P.V.R. Narasimha Rao Ch. 28.3 & Dusthana Joy Reversals)

Harsha Bala ("Strength of Cheerfulness") measures the inner joy, comfort, and natural resilience of the seven classical planets:
1. **Sthāna Bala (Joy House):** Sun in 9th, Moon in 3rd, Mars in 6th, Mercury in 1st, Jupiter in 11th, Venus in 5th, Saturn in 12th ($+5$ units).
2. **Uccha / Sva Kṣetra (Exaltation or Own Sign):** $+5$ units.
3. **Strī / Puruṣa Bhāva (Gender & House Match):** Feminine planets (Moon, Mercury, Venus, Saturn) in houses 1, 2, 3, 7, 8, 9; Masculine planets (Sun, Mars, Jupiter) in houses 4, 5, 6, 10, 11, 12 ($+5$ units).
4. **Dina / Rātri Bala (Diurnal / Nocturnal Sect Match):** Day birth rewards masculine planets ($+5$ units); Night birth rewards feminine planets ($+5$ units).

**Dusthana Harsha & Viparita Reversals:**
- **6th House (Harsha Yoga):** 6th lord in 6th house OR Mars in 6th house converts debt and enemies into victory and immunity.
- **8th House (Sarala Yoga):** 8th lord in 8th house converts crisis into fearless endurance and longevity.
- **12th House (Vimala Yoga):** 12th lord in 12th house OR Saturn in 12th house converts loss and solitude into spiritual release and detachment.

---

### D. Unified House Atmosphere & Environmental Weather Model

Synthesizes the net constructive vs friction forces acting on each house into a continuous score ($-100.0$ to $+100.0$):
- **Positive Forces:** Lord strength ($>1.0\times$), benefic occupants, protective drishti rays, Śubhakartarī, Upacaya malefic channeling, and Harsha/Viparita dusthana joy.
- **Negative Forces:** Combust/defeated lord, malefic occupants in non-upacaya houses, confrontational drishti, Pāpakartarī, Bhāva Sandhi, and Kārakobhāvanāśāya.
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
