# Classical Yoga Detection & Yoga Breaker (Bhaṅga) Engine

## 1. Philosophical Epistemology & Astrological Foundation

In classical Vedic astrology (*Brihat Parashara Hora Shastra* Chapters 34–42, 75; *Phaladeepika* Chapters 6–8; and Ryan Kurczak's *The Art and Science of Vedic Astrology*), a **Yoga** (Sanskrit for *union* or *yoking*) is a specific structural combination of planetary energies, zodiac signs, and house domains (*Bhavas*).

Yogas are not fatalistic, binary "on/off" switches. A textbook royal yoga (*Rāja Yoga*) or great person combination (*Pañca Mahāpuruṣa Yoga*) does not automatically guarantee worldly eminence. Its actual manifestation in a human life is governed by:
1. **The Dispositor Tree Principle ("Strong Roots"):** A planet is only as strong as its host dispositor (landlord). If the host is fallen or ruined in a dusthana without rescue, the yoga lacks ground and collapses.
2. **Structural Integrity:** Whether the yoga is formed purely by dignified rulers in auspicious houses (*Kendras* and *Trikoṇas*) with palpable aspect power (*Sphuṭa Dṛṣṭi* $\ge 45$ Virūpas / 75%).
3. **Yoga Breakers (*Yoga Bhaṅga*):** Whether the combination is corrupted, hindered, or shattered by the intrusion of evil house rulers (*Triṣaḍāya* — 3rd, 6th, and 11th lords), deep planetary combustion (*Astaṅgata*), or host dispositor collapse.
4. **Redemption (*Nīca Bhaṅga*):** Whether initial debility is converted into extraordinary resilience and late-life triumph through classical cancellation anchors.

This module provides Astra with an automated, high-precision detection engine that scans a horoscope, identifies classical combinations across fifteen categories, audits potential breakers, and outputs an objective **Plausibility Score (0% to 100%)**.

> [!NOTE]
> For the comprehensive, definitive rule book detailing all yogas from *Phaladeepika* Chapters 6–8, the *Sphuṭa Dṛṣṭi* continuous aspect gradient doctrine, and the complete taxonomy of yoga breakers, see [`yoga_rule_book.md`](file:///Users/hajnaljanos/PycharmProjects/astra/jyotish/yogas/yoga_rule_book.md).

---

## 2. Master Yoga Categories (*Phaladeepika* Chapters 6–8)

### 2.1 Pañca Mahāpuruṣa Yogas (Five Great Archetypes)
* **Sanskrit Citation:** *BPHS Ch. 75, Verses 1–20; Phaladeepika Ch. 6, Verses 1–4.*
* **Prerequisites:** One of the five physical planets (Mars, Mercury, Jupiter, Venus, Saturn) must be in an **angular house (*Kendra*: 1, 4, 7, 10)** from the Ascendant or the Moon, AND occupy its **own sign (*Sva-kṣetra*)** or **exaltation sign (*Uccha*)**.
* **The 5 Archetypes:**
  1. **Rucaka Yoga (Mars):** Bold, fearless, victorious in conflict, commands authority, athletic/military prowess.
  2. **Bhadra Yoga (Mercury):** Analytical genius, scholarly eloquence, oratory excellence, mastery of trade and details.
  3. **Haṃsa Yoga (Jupiter):** Spiritual swan, moral integrity (*Dharma*), philosophical clarity, revered by the virtuous.
  4. **Mālavya Yoga (Venus):** Aesthetic refinement, luxury, diplomatic tact, fortunate in love and marriage.
  5. **Śaśa Yoga (Saturn):** Immense endurance, unshakable discipline, commanding loyalty from workers, outlasting adversity.
* **Astronomical Modality Constraint on Mahāpuruṣa Yogas (Vic DiCara, Lecture 4):**
  - **Venus (*Mālavya*):** Can occur for **all 12 Ascendants** because its signs of strength span all three modalities: Taurus (Fixed), Libra (Cardinal), Pisces (Dual).
  - **Mars, Jupiter, and Saturn:** Can occur for **8 Ascendants each** (their own and exaltation signs span two modalities).
  - **Mercury (*Bhadra Yoga*):** Can **ONLY occur for the 4 Dual / Mutable Ascendants (Gemini, Virgo, Sagittarius, Pisces)**.
    - *Geometric Proof:* Mercury's signs of strength are Gemini (own sign) and Virgo (own and exaltation sign), both of which are Dual/Mutable signs. For Cardinal rising signs, all Kendras are Cardinal; for Fixed rising signs, all Kendras are Fixed. Therefore, Mercury can never occupy an angular house from the Ascendant for any Cardinal or Fixed rising sign.

---

### 2.2 Rāja Yoga vs. Śaṅkha Yoga (*Phaladeepika 6.37–38*)
* **Sanskrit Citation:** *Phaladeepika Ch. 6, Verses 37–38; BPHS Ch. 34 & 39.*
* **Mantreśwara's Precise Distinction:**
  - **Rāja Yoga (*The King*):** Strictly and exclusively the alliance between the **9th Lord (*Dharma*)** and the **10th Lord (*Karma*)** through conjunction, mutual aspect (*Dṛṣṭi* $\ge 45$ Virūpas), or sign exchange (*Parivartana*). Represents supreme royal sovereignty.
  - **Śaṅkha Yoga (*The Royal Herald / Conch*):** The alliance between any *other* Kendra Lord (1, 4, 7) and Trikoṇa Lord (1, 5, 9). Just as the conch heralds the arrival of the monarch, Śaṅkha Yoga announces and supports status without holding supreme sovereignty.
* **Single-Planet Rāja Yogakārakas:**
  - **Cancer & Leo:** Mars (rules 5 & 10 for Cancer; rules 4 & 9 for Leo).
  - **Taurus & Libra:** Saturn (rules 9 & 10 for Taurus; rules 4 & 5 for Libra).
  - **Capricorn & Aquarius:** Venus (rules 5 & 10 for Capricorn; rules 4 & 9 for Aquarius).
* **Rāja Yoga vs. Dhana Yoga — The Nature of Kingly Wealth (Vic DiCara, Lecture 5):**
  - **Dhana Yoga (Houses 2 & 11):** Signifies *private wealth, personal savings, liquid capital, and personal financial income*.
  - **Rāja Yoga (Houses 9 & 10):** Signifies *sovereign command, executive authority, and high governance*.
  - **Why Rāja Yoga confers immense wealth:** *"A king is never poor! Even the king of the poorest country in the world is not poor. Raja Yoga gives wealth because sovereign command over territory inherently commands resources (treasury, transport, attendants, infrastructure, and revenue)."* While a Dhana Yoga builds private bank accounts, a Rāja Yoga entrusts the keys to the entire societal treasury.

---

### 2.3 Candra & Ravi Yogas (Lunar & Solar Alignments)
* **Sanskrit Citation:** *Phaladeepika Ch. 6, Verses 5–15.*
* **Lunar Flanking Yogas:**
  - *Sunaphā:* Non-Sun physical planets in 2nd from Moon (resourcefulness, self-earned wealth).
  - *Anaphā:* Non-Sun physical planets in 12th from Moon (peace, generosity, health).
  - *Durudharā:* Non-Sun physical planets in both 2nd and 12th from Moon (balanced wealth and expenditure).
  - *Kemadruma:* Moon completely isolated with no flanking non-Sun physical planets in 2nd or 12th (subjective emotional vulnerability).
  - *The 4-Tier Kemadruma Bhaṅga (Cancellation Hierarchy — Phaladeepika 6.7 & Lecture 1):*
    1. **Tier 1 (Primary Lunar Kendra):** Physical planets occupy angular houses (1, 4, 7, 10) from the Moon.
    2. **Tier 2 (Primary Ascendant Kendra):** The Moon itself occupies an angular house (1, 4, 7, 10) from the Ascendant (*Lagna*).
    3. **Tier 3 (Modality / Quadruplicity Alignment):** The Ascendant and Moon share the same sign modality (both Movable/Cardinal, both Fixed, or both Dual/Mutable), creating angularity by sign modality (*Chatuṣṭaya*) that grants inner self-reliance.
    4. **Tier 4 (Navāṃśa Kendra Rescue):** Physical planets occupy angles from the Moon in the Navāṃśa (D9) divisional chart, providing subtle psychological grounding.
* **Solar Flanking Parallel Spectrum:**
  - *Veśi:* Benefics in 2nd from Sun (*Śubha-Veśi*) vs. Malefics in 2nd (*Pāpa-Veśi*).
  - *Vośi:* Benefics in 12th from Sun (*Śubha-Vośi*) vs. Malefics in 12th (*Pāpa-Vośi*).
  - *Ubhayacarī:* Flanked on both sides (*Śubha* vs. *Pāpa*).
* **Budhāditya Yoga:** Sun and Mercury conjoined (intellectual brilliance), with separation $\ge 3^\circ$ to prevent incinerating combustion.
* **Solar-Lunar Angular Baselines (*Phaladeepika 6.14*):**
  - *Adhama Yoga (Inferior / Lowest — 0.75 Toning):* Moon in a Kendra (1, 4, 7, 10) from the Sun (angular placement brings either New Moon combustion or harsh square/opposition tensions).
  - *Sama Yoga (Medium / Equal — 1.0 Baseline):* Moon in a Panaphara (2, 5, 8, 11) from the Sun (moderate, steady vitality).
  - *Variṣṭha Yoga (Superior / Highest — 1.25 Boost):* Moon in an Apoklima (3, 6, 9, 12) from the Sun (harmonious waxing/waning distances free from harsh angular friction).

---

### 2.4 Character, Growth & Life-Pillar Yogas
* **Sanskrit Citation:** *Phaladeepika Ch. 6, Verses 14–18.*
* **Kesarī Yoga (6.14):** Moon in Kendra (1, 4, 7, 10) from Jupiter (lion-like courage, unshakeable virtue; distinguished from Gaja Kesarī).
* **Śakaṭa Yoga (6.14):** Moon in 6th, 8th, or 12th from Jupiter while not in a Kendra from Lagna (pulling a heavy cart; fluctuating fortune; canceled if Moon is angular from Lagna).
* **Mahābhāgya Yoga (6.15):** Male born in day with Sun, Moon, Lagna in male signs; Female born at night with Sun, Moon, Lagna in female signs (universal polarity synergy).
* **Vasumatī Yoga (6.16):** Natural benefics (Jupiter, Venus, Mercury) occupy houses of growth (*Upachayas*: 3, 6, 10, 11) from the Ascendant or Moon. Mantreśwara defines an authentic **three-tiered graded wealth scale** (*Uttama, Madhyama, Svalpa*):
  - *Full / Supreme (Uttama):* All three benefics in Upachayas $\rightarrow$ Peerless, vast wealth. The native *"never lacks money without leaving home"* (*tiṣṭhed gṛhe*).
  - *Middling (Madhyama):* Any two benefics in Upachayas $\rightarrow$ Substantial, durable wealth.
  - *Minor (Svalpa / Alpa):* Any one benefic in an Upachaya $\rightarrow$ Modest prosperity and financial self-reliance.
  *(Note on Lecture 7: Vic DiCara's remark about Mercury being optional applied to Amalā Yoga, not Vasumatī; in Vasumatī, any benefic contributes to the graded tier).*
* **Amalā Yoga (6.17):** Unblemished natural benefic alone in 10th from Lagna or Moon (spotless moral renown).
* **Puṣkala Yoga (6.18):** Lord of the Moon sign joins the Lagna Lord in a Kendra or in an intimate friend's sign (*adhi-mitra*), while a powerful planet aspects the Lagna (magnificent honors and royal wealth).

---

### 2.5 Ādhi Yoga (The "OR" Rule — *Phaladeepika 6.19–20, 6.42–43*)
* **Rule:** Natural benefics occupy the **6th, 7th, OR 8th** from the Moon (*Candrādhi*) or Ascendant (*Lagnādhi*). Does not require all three houses filled.
  - *6th Alone:* Aspects 12th house -> **Netā** (leader and financier who conquers loss).
  - *7th Alone:* Aspects 1st house -> **Mantrī** (brilliant counselor and diplomat).
  - *8th Alone:* Aspects 2nd house -> **Bhūpati** (territorial ruler, long-lived protector).
* *Crucial Rule:* In *Lagnādhi*, the Moon cannot act as a participating benefic.

---

### 2.6 The Trimūrti & Tridevī Yogas (Cosmic Deity Yogas)
* **Sanskrit Citation:** *Phaladeepika Ch. 6, Verses 28–31.*
* Paired with the three sacred trine pillars (*Trikoṇas*: 1st = Shiva, 5th = Brahma, 9th = Vishnu):
  - **Śrīkaṇṭha (Śiva):** 1st Lord, Sun, and Moon in Kendra/Kona in own/exalted/friendly signs (fearless truth, self-mastery).
  - **Viriñci (Brahmā):** 5th Lord, Jupiter, and Saturn in Kendra/Kona in good dignity (deep Vedic knowledge, fertile intellect).
  - **Śrīnātha (Viṣṇu):** 9th Lord, Venus, and Mercury in Kendra/Kona in good dignity (splendid wealth, magnetic grace).
  - Consorts: **Gaurī** (Moon in own sign or exalted in a Kendra or Trikoṇa — the Lunar counterpart to Lakṣmī without requiring Jupiter's aspect per *Phaladeepika 6.24*), **Lakṣmī** (9th lord + Venus in Kendra/Kona in high dignity), and **Sarasvatī** (Mercury, Jupiter, Venus in Kendras/Trikoṇas/2nd with strong Jupiter).

---

### 2.7 Parivartana Yogas (Mutual Sign Exchanges — The Exact 66 Combinations)
* **Sanskrit Citation:** *Phaladeepika Ch. 6, Verses 32–34.*
* Total pairwise combinations across 12 houses = $\binom{12}{2} = \mathbf{66 \text{ total exchanges}}$:
  1. **Mahā Yoga (Exactly 28 Varieties):** Pairwise exchanges strictly among the 8 auspicious houses {1, 2, 4, 5, 7, 9, 10, 11}. $\binom{8}{2} = \frac{8 \times 7}{2} = \mathbf{28}$ (NOT 30!). Conveys royal elevation.
  2. **Khala Yoga (Exactly 8 Varieties):** Exchanges between the **3rd house** and any of the 8 auspicious houses (alternating arrogance and defeat; hard work with fluctuating return).
  3. **Dainya Yoga (Exactly 30 Varieties):** Exchanges involving dusthanas **6, 8, or 12** ($11 + 10 + 9 = \mathbf{30}$). Conveys karmic hardships and unexpected losses.
  - Total: $28 + 8 + 30 = \mathbf{66 \text{ combinations}}$.

---

### 2.8 Dispositor Root Yogas — Kāhala & Parvata
* **Sanskrit Citation:** *Phaladeepika Ch. 6, Verses 35–36.*
* **Kāhala Yoga ("Large / Drum Yoga"):** Governed by two scriptural traditions (*Phaladeepika 6.35*):
  - *Variant A (Mutual Kendra Alliance):* Lords of the 4th and 10th houses occupy mutual Kendras (angles) from each other, while the Lagna Lord is fortified in strength.
  - *Variant B (The Dispositor Chain — "Strong Roots"):* The dispositor of the 1st Lord is in its own sign or exalted in a Kendra (1, 4, 7, 10) or Trikoṇa (1, 5, 9). Vic DiCara emphasizes Variant B as the foundational proof of generational root vitality.
* **Parvata Yoga ("Mountainous Yoga"):** BOTH the Lagna Lord AND its host dispositor are in high dignity (own sign or exalted) in an angle (*Kendra*) or trine (*Trikoṇa*), granting unshakeable nobility and enduring prosperity.
  - *The "Self-Dispositor" Loophole (Vic DiCara, Lecture 1):* When the 1st Lord sits in the 1st house in its own sign (e.g. Mars in Aries rising, Saturn in Capricorn rising), it acts as its own dispositor in an angle. Naive algorithms flag this as Parvata Yoga. However, authentic Parvata requires an external, two-tier dispositor chain showing generational root strength. The 1st Lord in 1st in own sign is a **Self-Dispositor Variant**, calibrated at ~70% plausibility rather than a full 100% two-tier tree.

---

### 2.9 The 7 Saṅkhyā Yogas (Planetary Distribution)
* **Sanskrit Citation:** *Phaladeepika Ch. 6, Verses 39–41.*
* Governed by the number of signs occupied by the 7 physical planets.
* **The Inversion Principle:** Fewer conjunctions = superior yoga! 7 signs (*Vallakī*) is supreme; 1 sign (*Golā*) is crude and congested.
* **The Life-Filter Principle:** Saṅkhyā yogas act as the permanent cognitive lens through which the native processes reality.
  - *Vallakī (7 signs):* Cultured scholar and artist.
  - *Dāma (6 signs):* Generous, wealthy public servant.
  - *Pāśa (5 signs):* Practical, crafty, bonded to family.
  - *Kedāra (4 signs):* Grounded, hard-working landowner.
  - *Śūla (3 signs):* Sharp, aggressive, courageous in conflict.
  - *Yuga (2 signs):* Carries heavy burdens, struggles against social strictures.
  - *Golā (1 sign):* Crude, crowded, unhygienic, erratic fortune.

---

### 2.10 The 2 Mālā (Strand) Yogas
* **Sanskrit Citation:** *Phaladeepika Ch. 6, Verse 38.*
* **Śubhamālā:** All benefics occupy houses 5, 6, and 7 (garland of protection, royal comforts).
* **Aśubhamālā:** Benefics trapped in 6, 8, 12 while malefics occupy angles (submerged potential).

---

### 2.11 The 12 Bhava Good & Converse Yogas
* **Sanskrit Citation:** *Phaladeepika Ch. 6, Verses 44–69.*
* Every house produces a Hero Yoga (*Śubha*) when its lord is fortified in angles/trines by benefics, and an Affliction Yoga (*Aśubha*) when its lord goes to dusthanas (6, 8, 12).
* **The Complete 12 Bhava Good & Converse Matrix:**

| House | Good Yoga (*Śubha*) | Authentic Meaning | Converse Yoga (*Aśubha* / Reversal) | Authentic Meaning |
| :---: | :--- | :--- | :--- | :--- |
| **1st** | **Cāmara** | Royal Fly-Whisk: Splendor, long life | **Ava** | Obscurity, frail body, low recognition |
| **2nd** | **Dhenu** | Milch Cow: Abundant resources, sweet voice | **Niḥsva** | Poverty, harsh speech, depleted savings |
| **3rd** | **Śaurya** | The Hero: Valorous, supportive siblings | **Mṛti / Mṛta** | Timid, broken initiatives, sibling strife |
| **4th** | **Jaladhi** | Ocean / Wealthy Home: Palatial estates | **Kuhu** | Empty Home / Dark Moon: Bereft of domestic peace |
| **5th** | **Chatra** | Royal Canopy: Brilliant scholar, wise counsel | **Pāmara** | Ignorant / Indiscriminate: Lacks discernment |
| **6th** | **Astra** | The Weapon: Conquers enemies and debts | **Harṣa** *(Converse Reversal)* | Cheerful triumph over rivals, radiant health |
| **7th** | **Kāma** | The Lover: Beautiful, loving, loyal spouse | **Śatru** | Hostility: Bitter marital friction and estrangement |
| **8th** | **Asura** | The Titanic Fighter: Fierce, volatile power | **Sarala** *(Converse Reversal)* | Sincere, long-lived, righteous success |
| **9th** | **Bhāgya** | The Fortunate: Righteous father, divine grace | **Nirbhāgya** | Stripped of Fortune: Rejects legacy, misfortune |
| **10th**| **Khyāti** | The Renowned: Praised by rulers, noble work | **Duṣkṛti** | Disgraced reputation, corrupt or wasted effort |
| **11th**| **Pārijāta**| Celestial Jasmine: Continuous gains | **Daridra** | Poverty of Gains: Stagnant earnings, debt |
| **12th**| **Musala**  | Ascetic Wand: Spiritual peace, wise spend | **Vimala** *(Converse Reversal)* | Frugal, independent, immune to ruinous losses |

* **The Dusthana Reversal Paradox:** When lords of 6, 8, or 12 sit in dusthanas, the two negatives destroy each other, producing positive reversal yogas (Harṣa, Sarala, Vimala).
* **The 8th House Paradox (Asura vs. Sarala):**
  - Fortified 8th Lord = **Asura Yoga** (Phaladeepika 6.51 — titanic, hyper-ambitious, aggressive, ethically volatile, easily angered).
  - Dusthana 8th Lord = **Sarala Yoga** (Phaladeepika 6.65 — noble, straightforward, enduring vitality).

---

### 2.12 Chapter 7 Kingly Power Yogas (*Phaladeepika 7.1–13*)
* **Retrogression Sovereignty (*Vakra Bala* — 7.1):** Retrograde planets possess extraordinary kinetic potency equivalent to exaltation.
* **Multi-Planet Kendras (7.2–3):** 3+ planets in Kendra in dignity = celebrated ruler; 5 planets = royal command from humble birth.
* **Directional Strength Sovereignty (*Digbala* — 7.4–7):** 4–5 planets (excluding Saturn) with Digbala confers supreme executive authority.
* **The Five Specific Power Yogas of Command (7.8–13):**
  1. **Venus Rising in Aśvinī (7.8a):** Venus sits in the 1st House (*Lagna*) in Aśvinī nakshatra aspected by 3+ planets. Conquers opposition through charisma, charm, and popularity.
  2. **1st Lord with Venus in the 2nd House (7.8b–9):** 1st Lord (*Lagneśa*) joins Venus in the 2nd house without debility or enmity. Creates an economic sovereign or protective patriarch whose life is grounded in sustained wealth.
  3. **Mars in a Fire Sign aspected by a Friend (7.10):** Mars (*Bhauma*) in Aries, Leo, or Sagittarius anywhere in the chart (*kujē hari-cāpa-ajē mitra-dṛṣṭē* — not restricted to 1st house) aspected by a friendly planet ($\ge 45$ Virūpas). Produces a commanding, martial, assertive leader.
  4. **9th & 10th House Exchange (7.11):** Mutual reception (*Parivartana*) between 9th and 10th lords (*Karmeśo navamagatas...*). A righteous governor and organizer of people (*Nṛpa*) celebrated for civic and ethical service.
  5. **The Overpowering Immovable Commander (7.12–13):** Sun in mid-Sagittarius blazing brightly above the horizon conjoined with the Moon. The Moon is at New Moon (*Amāvāsyā*) and completely dark/invisible, which acts as the psychological engine of the yoga by stripping away emotional hesitation, shyness, and softness. Saturn rises in the 1st House with great strength (*Lagne'tivīryaḥ*), and Mars is exalted in Capricorn (*Ativīrya*). Produces an immovable, feared military commander whose opponents surrender from afar out of sheer intimidation (*trastāva-nāmantitā*).

---

## 3. The Science of Yoga Breakers (*Yoga Bhaṅga*)

```
                         THE YOGA BREAKER AUDIT MATRIX
                         
      BREAKER FACTOR          SCRIPTURAL PRINCIPLE      ASTRA COMPUTATIONAL PENALTY
 ───────────────────────────────────────────────────────────────────────────────────
  11th Lord Intrusion          BPHS Ch. 34 (Triṣaḍāya)   -40% (Supreme Saboteur)
  6th Lord Intrusion           BPHS Ch. 34 (Triṣaḍāya)   -25% (Litigation/Debts)
  3rd Lord Intrusion           BPHS Ch. 34 (Triṣaḍāya)   -15% (Distraction/Ego)
  Deep Combustion (< 3°)       Surya Siddhanta           -40% (Burned Rays)
  Moderate Combustion (< 8°)   Surya Siddhanta           -20% (Egoic Friction)
  Host Dispositor Debilitated  Phaladeepika 3.11         -25% (Bankrupt Foundation)
  Dusthana Trapping (6, 8, 12) Phaladeepika 6.57         -25% per house
  Weak Aspect (< 45 Virūpas)   Phaladeepika 6.37         -30% (Hollow Connection)
  Low Ṣaḍbala (< 0.85 Ratio)   Bhava & Graha Balas       -15% (No Muscle)
```

> [!NOTE]
> **Astra Algorithmic Heuristic Notice:**
> The percentage deduction matrix above represents Astra's internal mathematical modeling system to rank pattern integrity (0%–100%). In classical scripture (*Phaladeepika* and *BPHS*), yogas are qualitative archetypes evaluated via gradients and root health, not mechanical arithmetic point subtractions.

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
5. **Dispositor Aspect (+25%):** The ruler of the debilitation sign directly aspects the fallen planet with palpable strength ($\ge 45$ Virūpas).
6. **Angular Placement (+20%):** The fallen planet itself occupies an angle (*Kendra*) from Lagna or the Moon.

---

## 5. Plausibility & Status Classification

Astra normalizes every detected yoga to a standard **0.0% to 100.0% Plausibility Scale**:
- **$\ge 75.0\%$:** `🌟 Pure & Eminent` (Uncorrupted manifestation during its Daśā).
- **$50.0\% - 74.9\%$:** `⚖️ Stained / Challenged` (Functional, but requires conscious effort and overcomes minor friction).
- **$30.0\% - 49.9\%$:** `🛡️ Rescued (Nīca Bhaṅga / Reversal)` (Initial hardship converted into late-life authority).
- **$< 30.0\%$:** `❌ Broken (Yoga Bhaṅga)` (Promises greatness on paper, but ruined by saboteur intrusion or collapse).
