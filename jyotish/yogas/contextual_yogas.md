# Contextual & Macro Setup Yogas Engine

## Overview & Foundational Purpose
Contextual Setup Yogas evaluate the macrocosmic architecture of the native's chart before individual grahas and house rulers are analyzed in isolation. They reveal the **overall distribution pattern, command projection, and structural support** of the native's life canvas.

Per `YOGA_ARCHITECTURE.md` Category 11 (`CONTEXTUAL`), this subsystem consolidates:
1. **Sāṅkhya Yogas (Pattern of Distribution - 7 Yogas)**: Tallying the number of unique zodiac signs occupied by all 7 classical grahas.
   - Strictly standalone per *Phaladīpikā* 6.39 (*anya-pūrva-muktān vihāya*) — ZERO Layer 2 breakers applied.
2. **Candrādhi & Lagnādhi Yogas (The Configurations of Command)**: Benefics in the 6th, 7th, or 8th from Moon or Lagna.
   - Graded across the three classical command pillars: 6th (*Netā* / Enforcer), 7th (*Mantrī* / Advisor), and 8th (*Bhūpati* / Landholder).
   - Evaluates continuous Sphuṭa Dṛṣṭi onto the focal point and horizon axis alignment.
   - Layer 2 Breakers: `audit_combustion` and `audit_shadbala_muscle` applied; `audit_dusthana_placement` strictly forbidden.
3. **Mahābhāgya Yoga (Supreme Fortune Synergies)**: Synergizing Day/Night sect with gender and sign polarities across Lagna, Sun, and Moon.
   - Full 4/4 Alignment: `YogaStatus.PURE` (`95.0`).
   - Partial 3/4 Alignment: `YogaStatus.STAINED` (`65.0`).
4. **General Scope Yogas (Sun-Moon Quadrant Geometry - 3 Yogas)**: Whole-sign angular distance from Sun to Moon (*Phaladīpikā* 6.14 & 6.19; *BPHS* 38.1–3).
   - **Kendra Scope (1, 4, 7, 10): Adhama Yoga** — High-friction baseline (`0.75` multiplier); rescued if anchored in Lagna Kendra or Full Moon in 7th.
   - **Paṇaphara Scope (2, 5, 8, 11): Sama (Madhya) Yoga** — Balanced succedent baseline (`1.0` multiplier).
   - **Apoklima Scope (3, 6, 9, 12): Variṣṭha Yoga** — Harmonious cadent expanse (`1.25` multiplier).
5. **Solitary 1st House Yogas (3 Yogas)**: Solitary occupants of the Ascendant (*Aśubha Tanu* Mars/Saturn; *Śubha Tanu* Jupiter/Venus/Mercury).
6. **Dual-Lagna Raja Yoga (Ubhayalagna Synchrony)**: Simultaneous Kendra-Koṇa combinations operating from both Janma Lagna and Candra Lagna.

*(Note: Sunaphā, Anaphā, Durudharā, 4-Tier Kemadruma, Budhāditya, and Solar Flanking are canonically computed in `lunar_solar_yogas.py`; Śubha and Pāpa Kartarī are canonically computed in `kartari.py`.)*

---

## 1. Sāṅkhya Yogas (Signs Occupied by Classical 7 Grahas)
- **Contestants:** Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn (all 7 must be resolved).
- **Rules:**
  - **1 Sign: Gola Yoga** — Extreme concentration, narrow one-pointed focus.
  - **2 Signs: Yuga Yoga** — Dualistic tension, polarization, reliance on partners.
  - **3 Signs: Śūla Yoga** — Trident resolve, sharp ambition, austere fortitude.
  - **4 Signs: Kedāra Yoga** — Agricultural patience, grounded endurance, steady builder.
  - **5 Signs: Pāśa Yoga** — Tied to family, societal obligations, administrative networking.
  - **6 Signs: Dāma Yoga** — Generous benefactor, broad-minded, widely accomplished.
  - **7 Signs: Vīṇā Yoga** — Harmonious versatility, musical/aesthetic grace, balanced life.

---

## 2. Candrādhi & Lagnādhi Yogas
- **Formation:** Natural benefics (*Mercury, Jupiter, Venus*) in 6th, 7th, or 8th from Moon (*Candrādhi*) or Lagna (*Lagnādhi*). Moon is strictly excluded from participating.
- **Pillars of Command:**
  - **Netā (6th):** Enforcer / Commander; projects aspect across to 12th and 1st.
  - **Mantrī (7th):** Advisor / Prime Minister; directly aspects the 1st focal point.
  - **Bhūpati (8th):** Landholder / Sovereign; projects aspect to the 2nd house of accumulated wealth.

---

## 3. Mahābhāgya Yoga
- **Male Configuration:** Day birth + Odd Lagna + Odd Sun + Odd Moon.
- **Female Configuration:** Night birth + Even Lagna + Even Sun + Even Moon.
- **Unverified Gender:** Penalized via Layer 2 breaker to block unearned `PURE` status.
- **Graded Synergy:** Charts with 3 of 4 factors aligned emit partial Mahābhāgya synergy.

---

## 4. Sun-Moon Quadrants (Adhama, Sama, Variṣṭha)
- **Adhama (Kendra):** Sun-Moon square or opposition tension; mitigated by Lagna Kendra anchoring or Full Moon (7th) brightness.
- **Sama (Paṇaphara):** Stable resource accumulation without harsh friction.
- **Variṣṭha (Apoklima):** Free from solar combustion and square tension; acts as a 1.25 multiplier on other chart yogas.

---

## 5. Solitary 1st House Yogas
- **Aśubha Tanu (Mars / Saturn):** Solitary malefic in 1st house; bestows physical grit and endurance with high emotional self-containment.
- **Śubha Tanu (Jupiter / Venus / Mercury):** Solitary benefic in 1st house; radiates charm, benevolence, and natural social protection.

---

## 6. Dual-Lagna Raja Yoga (Ubhayalagna)
- Formed when Kendra-Koṇa lords from Janma Lagna and Candra Lagna share a conjunction or palpable mutual aspect ($\ge 45.0$ Virūpas), aligning outer worldly career with inner emotional peace.
