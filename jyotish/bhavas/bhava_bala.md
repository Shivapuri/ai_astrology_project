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
