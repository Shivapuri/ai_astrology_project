# Classical Yoga Detection & Yoga Breaker (Bhaṅga) Engine

## 1. Philosophical Epistemology & Astrological Foundation

In classical Vedic astrology (*Brihat Parashara Hora Shastra* Chapters 34–42, 75; *Phaladeepika* Chapters 6 & 7; and Ryan Kurczak's *The Art and Science of Vedic Astrology*), a **Yoga** (Sanskrit for *union* or *yoking*) is a specific structural combination of planetary energies, zodiac signs, and house domains (*Bhavas*).

Yogas are not fatalistic, binary "on/off" switches. A textbook royal yoga (*Rāja Yoga*) or great person combination (*Pañca Mahāpuruṣa Yoga*) does not automatically guarantee worldly eminence. Its actual manifestation in a human life is governed by:
1. **Structural Integrity:** Whether the yoga is formed purely by dignified rulers in auspicious houses (*Kendras* and *Trikoṇas*).
2. **Yoga Breakers (*Yoga Bhaṅga*):** Whether the combination is corrupted, hindered, or shattered by the intrusion of evil house rulers (*Triṣaḍāya* — 3rd, 6th, and 11th lords), deep planetary combustion (*Astaṅgata*), or host dispositor collapse.
3. **Redemption (*Nīca Bhaṅga*):** Whether initial debility is converted into extraordinary resilience and late-life triumph through classical cancellation anchors.

This module provides Astra with an automated, high-precision detection engine that scans a horoscope, identifies classical combinations across nine categories, audits potential breakers, and outputs an objective **Plausibility Score (0% to 100%)**.

---

## 2. Core Yoga Categories

### 2.1 Pañca Mahāpuruṣa Yogas (Five Great Archetypes)
* **Sanskrit Citation:** *BPHS Ch. 75, Verses 1–20; Phaladeepika Ch. 6, Verses 1–4.*
* **Prerequisites:** One of the five physical planets (Mars, Mercury, Jupiter, Venus, Saturn) must be in an **angular house (*Kendra*: 1, 4, 7, 10)** from the Ascendant or the Moon, AND occupy its **own sign (*Sva-kṣetra*)** or **exaltation sign (*Uccha*)**.
* **The 5 Archetypes:**
  1. **Rucaka Yoga (Mars):** Bold, fearless, victorious in conflict, commands authority, athletic/military prowess.
  2. **Bhadra Yoga (Mercury):** Analytical genius, scholarly eloquence, oratory excellence, mastery of trade and details.
  3. **Haṃsa Yoga (Jupiter):** Spiritual swan, moral integrity (*Dharma*), philosophical clarity, revered by the virtuous.
  4. **Mālavya Yoga (Venus):** Aesthetic refinement, luxury, diplomatic tact, fortunate in love and marriage.
  5. **Śaśa Yoga (Saturn):** Immense endurance, unshakable discipline, commanding loyalty from workers, outlasting adversity.

---

### 2.2 Rāja Yogas (The Marriage of Grace and Action)
* **Sanskrit Citation:** *BPHS Ch. 34, Verses 15–20; Ch. 39–40; Phaladeepika Ch. 7.*
* **The Fundamental Axiom:**
  $$\text{Rāja Yoga} = \text{Trikoṇa Lord (Grace / Dharma: 1, 5, 9)} + \text{Kendra Lord (Power / Karma: 1, 4, 7, 10)}$$
* **Single-Planet Rāja Yogakārakas:**
  - **Cancer & Leo:** Mars (rules 5 & 10 for Cancer; rules 4 & 9 for Leo).
  - **Taurus & Libra:** Saturn (rules 9 & 10 for Taurus; rules 4 & 5 for Libra).
  - **Capricorn & Aquarius:** Venus (rules 5 & 10 for Capricorn; rules 4 & 9 for Aquarius).
* **Supreme Rāja Yoga (*Dharma-Karma Adhipati*):** The alliance between the **9th Lord (highest Trikoṇa)** and the **10th Lord (highest Kendra)** through conjunction, mutual aspect (*Dṛṣṭi*), or sign exchange (*Parivartana*).

---

### 2.3 Dhana & Dāridrya Yogas (Wealth vs. Depletion)
* **Sanskrit Citation:** *BPHS Ch. 41 (Vishesha Dhana Yoga) & Ch. 42 (Daridrya Yoga).*
* **Dhana Yogas:** Interlocking connections among houses 1 (Self), 2 (Treasury), 5 (Intellect/Speculation), 9 (Fortune), and 11 (Gains).
  - *Lakṣmī Yoga:* 9th lord and Venus fortified in Kendras or Trikoṇas in high dignity.
* **Dāridrya Yogas:** Rulers of 2nd or 11th trapped in Dusthanas (6, 8, 12), combust, or debilitated, causing financial drain.

---

### 2.4 Candra & Ravi Yogas (Lunar and Solar Alignments)
* **Sanskrit Citation:** *BPHS Ch. 37–38; Phaladeepika Ch. 6, Verses 5–13, 19–20, 42–43.*
* **Gaja Kesarī Yoga:** Jupiter in Kendra (1, 4, 7, 10) from the Moon, shielding the emotional mind (*Manas*) with philosophical wisdom.
* **Flanking Moon Yogas:**
  - *Sunaphā Yoga:* Planets (except Sun/Nodes) in 2nd from Moon (resourcefulness).
  - *Anaphā Yoga:* Planets in 12th from Moon (peace and generosity).
  - *Durudharā Yoga:* Planets flanking both 2nd and 12th (balanced emotional support).
  - *Kemadruma Yoga:* Moon isolated with no flanking planets (emotional vulnerability), subject to *Kemadruma Bhaṅga* (cancellation) if Kendras are occupied.
* **Candra-Maṅgala Yoga:** Moon and Mars conjoined or mutually aspecting (commercial hustle and energetic wealth).
* **Candrādhi Yoga:** Benefics (Mercury, Jupiter, Venus) in 6th, 7th, and 8th from Moon (diplomatic command).
* **Budhāditya Yoga:** Sun and Mercury conjoined (intellectual brilliance), with distance $\ge 3^\circ$ to prevent incinerating combustion.
* **Solar Flanking:** *Veśi* (2nd from Sun), *Vośi* (12th from Sun), *Ubhayacarī* (flanking both).

---

### 2.5 Parivartana Yogas (Mutual Sign Exchanges)
* **Sanskrit Citation:** *Phaladeepika Ch. 6, Verses 32–34.*
* **Mahā Yoga (30 exchanges):** Exchanges among houses 1, 2, 4, 5, 7, 9, 10, 11 (royal elevation and lasting prosperity).
* **Khala Yoga (8 exchanges):** Involving the 3rd house (alternating cycles of hustle, arrogance, and triumph).
* **Dainya Yoga (30 exchanges):** Involving houses 6, 8, or 12 (karmic trials, unexpected expenditure, or health vulnerabilities).

---

### 2.6 Viparīta Rāja Yogas (Reversal of Misfortune)
* **Sanskrit Citation:** *Phaladeepika Ch. 6, Verses 57–69; Ch. 7, Verses 8–10.*
* **Mechanism:** When rulers of difficult houses (*Dusthanas*: 6, 8, 12) occupy *Dusthanas* without the association of auspicious Kendra/Trikona lords, the negative energies cancel each other out:
  - *Harṣa Yoga:* 6th Lord in 6, 8, or 12 (conquering enemies and disease cheerfully).
  - *Sarala Yoga:* 8th Lord in 6, 8, or 12 (fearless mind, longevity, victory from crisis).
  - *Vimala Yoga:* 12th Lord in 6, 8, or 12 (frugal, independent, protected from ruinous loss).

---

### 2.7 Kartarī Yogas (The Universal Hemming Principle)
* **Sanskrit Citation:** *Phaladeepika Ch. 6, Verses 11–13; Ryan Kurczak Lesson 42.*
* **Śubha Kartarī:** A house or planet flanked in 2nd and 12th exclusively by natural benefics (protective shield).
* **Pāpa Kartarī:** A house or planet flanked in 2nd and 12th by natural malefics (scissor compression and obstacle).

---

## 3. The Science of Yoga Breakers (*Yoga Bhaṅga*)

```
                         THE YOGA BREAKER AUDIT MATRIX
                         
      BREAKER FACTOR          SCRIPTURAL AUTHORITY      SEVERITY / PENALTY
 ─────────────────────────────────────────────────────────────────────────────
  11th Lord Intrusion          BPHS Ch. 34 (Triṣaḍāya)   -40% (Supreme Saboteur)
  6th Lord Intrusion           BPHS Ch. 34 (Triṣaḍāya)   -25% (Litigation/Debts)
  3rd Lord Intrusion           BPHS Ch. 34 (Triṣaḍāya)   -15% (Distraction/Ego)
  Deep Combustion (< 3°)       Surya Siddhanta           -40% (Burned Rays)
  Moderate Combustion (< 8°)   Surya Siddhanta           -20% (Egoic Friction)
  Host Dispositor Debilitated  Phaladeepika 3.11         -25% (Bankrupt Foundation)
  Dusthana Trapping (6, 8, 12) Phaladeepika 7.8          -25% per house
  Low Ṣaḍbala (< 0.85 Ratio)   Bhava & Graha Balas       -15% (No Muscle)
```

### 3.1 The Triṣaḍāya Axiom (BPHS Ch. 34)
Sage Parashara explicitly identifies the lords of houses 3, 6, and 11 as the primary saboteurs of Rāja Yogas:
- **The 11th Lord is the Most Insidious:** It rules *Lābha* (desires and personal gain). When it contaminates a Rāja Yoga, the native becomes seduced by vanity, chasing superficial titles, and social posturing, abandoning the selfless duty required for real leadership.
- **Hierarchy Resistance:** A supreme 9th + 10th lord union can easily resist 3rd lord distraction, so the penalty is halved (-7.5%). A modest 4th + 5th lord union collapses under 11th lord intrusion.

---

## 4. The 6 Classical Nīca Bhaṅga Conditions (*Phaladeepika 7.24–30*)

When a planet is in its fallen sign (*Nīca*), its debility is canceled or transformed into a **Nīca Bhaṅga Rāja Yoga** if:
1. **Exalted Co-occupant (+35%):** An exalted planet shares the same sign with the fallen planet (e.g. Einstein's fallen Mercury with exalted Venus).
2. **Dispositor in Kendra (+30%):** The ruler of the debilitation sign is in a Kendra (1, 4, 7, 10) from Lagna or the Moon.
3. **Exaltation Lord in Kendra (+25%):** The planet that exalts in that sign is in a Kendra from Lagna or the Moon.
4. **Exalted Dispositor (+30%):** The ruler of the debilitation sign is itself exalted.
5. **Dispositor Aspect (+25%):** The ruler of the debilitation sign directly aspects the fallen planet.
6. **Angular Placement (+20%):** The fallen planet itself occupies an angle (*Kendra*) from Lagna or the Moon.

---

## 5. Plausibility & Status Classification

Astra normalizes every detected yoga to a standard **0.0% to 100.0% Plausibility Scale**:
- **$\ge 75.0\%$:** `🌟 Pure & Eminent` (Uncorrupted manifestation during its Daśā).
- **$50.0\% - 74.9\%$:** `⚖️ Stained / Challenged` (Functional, but requires conscious effort and overcomes minor friction).
- **$30.0\% - 49.9\%$:** `🛡️ Rescued (Nīca Bhaṅga / Reversal)` (Initial hardship converted into late-life authority).
- **$< 30.0\%$:** `❌ Broken (Yoga Bhaṅga)` (Promises greatness on paper, but ruined by saboteur intrusion or collapse).
