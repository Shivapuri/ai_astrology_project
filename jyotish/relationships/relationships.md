# Jyotish Engine: Planetary Friendships & Dignity (relationships.py)

This file serves as the foundational astrological relationship engine based on *Bṛhat Parāśara Horā Śāstra* (BPHS), Mantreśvara's *Phaladīpikā*, and Ernst Wilhelm's Kala software.

---

## 1. Simple Description (For the Layperson)
In Jyotish, planets are like people. They have their own inborn personalities, but they also react to who is sitting next to them in a room. To figure out how two planets feel about each other, the software does a 3-step calculation:

1. **Natural Friendship (Naisargika):** This is the permanent, inborn "chemistry" between two planets. Just like some people naturally get along, Jupiter and the Sun are natural friends.
2. **Temporary Friendship (Tatkalika):** This is based purely on physical distance in the sky on the exact day you were born. Even if two planets are natural enemies, if they give each other enough "personal space," they agree to a temporary truce. If they are crammed into the same room, they annoy each other and become temporary enemies.
3. **Compound Friendship (Panchadha):** This is the final, ultimate score. The software simply adds the Natural score and the Temporary score together to get 5 final levels (Great Friend, Friend, Neutral, Enemy, Great Enemy).

Whenever the software says a planet is in a "Great Friend's Sign," it is using this final, 5-level Compound Friendship score.

---

## 2. Technical AI Description (Logic Constraints)
If you are modifying `relationships.py`, strictly observe these mathematical rules:

1. **Three-Tier Friendship System & Matrix Scope:**
   - Evaluates a complete $9 \times 9$ bidirectional matrix covering all 7 physical planets plus Rāhu and Ketu (`natural_relationships`, `temporary_relationships`, `compound_relationships`), preventing `KeyError` exceptions when physical planets query nodes.
   - `get_natural_relationship()` (*Naisargika*):
     - Physical planets follow BPHS Ch. 15 *Moolatrikona* derivations.
     - Rāhu and Ketu follow Mantreśvara’s *Phaladīpikā* (Ch. 8 & 20) Asura coalition: Friends with Mercury, Venus, Saturn; Neutral with Mars; Enemies with Sun, Moon, Jupiter.
   - `get_temporary_relationship()` (*Tātkālika*): Based purely on physical distance in the $D_1$ (Rasi) chart. Houses 2, 3, 4, 10, 11, 12 ($+1, +2, +3, +9, +10, +11$) = Friend. Others (conjunct, or 5, 6, 7, 8, 9 away) = Enemy. Same body comparison ($p_1 == p_2$) returns `"Self"`.
   - `get_compound_relationship()` (*Pañcadhā*): Mathematical sum of Natural + Temporary $(-2 \text{ to } +2)$. Returns 5 levels: `"Great Friend"`, `"Friend"`, `"Neutral"`, `"Enemy"`, `"Great Enemy"` (or `"Self"`).

2. **Dignity Logic (`get_dignity`):**
   - Must check fixed dignities FIRST (Exalted, Debilitated, Moolatrikona, Own Sign).
   - Rahu fixed dignities: Exalted in Taurus, Debilitated in Scorpio, Moolatrikona in Gemini, Own Sign in Aquarius.
   - Ketu fixed dignities: Exalted in Scorpio, Debilitated in Taurus, Moolatrikona in Sagittarius, Own Sign in Pisces (*Mīna*, resolving dual Jupiter-Saturn rulership symmetry).
   - Co-rulership identity: Rāhu in Aquarius and Ketu in Pisces evaluate `effective_lord = p_name`, yielding `"Self"` for natural, temporary, and compound relationships, outputting pure `"Own Sign"` (*Sva-kṣetra* / *Svastha*).
   - If none match, it returns the sign lord's compound relationship (e.g., `"Great Friend's Sign"`, `"Enemy's Sign"`).

3. **Rāśi Aspects (`get_rasi_drishti`):**
   - Rāśi Dṛṣṭi resides in `jyotish/aspects/aspects.py` as `get_rasi_drishti` (rather than inside `relationships.py`) and is imported where needed.
   - Returns whole-sign mutual aspects: Moveable (Cardinal) signs aspect Fixed signs (except adjacent); Fixed signs aspect Moveable signs (except adjacent); Dual (Mutable) signs aspect all other Dual signs.

---

## 3. Scriptural Foundation (Sanskrit Quotes)
The rules in this file are directly grounded in the **Brihat Parashara Hora Shastra** as translated by Ernst Wilhelm.

### Natural Friendship (Naisargika)
> “From Mulatrikona, the owner of the 4th, 2nd, 12th, 5th, 9th, and 8th as well as the lord of its exaltation Rasi are friendly. Inimical are the others. Neutral are those that indicate both (friendly on one count and inimical on another count, which may happen for those Grahas that rule two Rasis).”
> *— Brihat Parashara Hora Shastra: Nature and Form of the Grahas, 55*

### Temporary Friendship (Tatkalika)
> “Those standing in the 10th, 4th, 11th, 3rd, 2nd and 12th from each other are at that time friendly, those standing elsewhere are enemies.”
> *— Brihat Parashara Hora Shastra: Nature and Form of the Grahas, 56*

### Compound Friendship (Panchadha)
> “Friendly at the time as well as naturally so – great friendship. Friendship if friendly and neutral. Enemies if inimical and neutral. Neutral if friendly and inimical. Both inimical – great enmity. Thus should the astrologer examine the nativity when pronouncing effects.”
> *— Brihat Parashara Hora Shastra: Nature and Form of the Grahas, 57-58*

---

## 4. Special Astrological Exceptions & Limits
As implemented in `generate_jyotish.py` and `relationships.py`:

- **Varga-Specific Distances (Tātkālika Anchored to $D_1$):**
  *Tātkālika Maitrī* (Temporary Friendship) is ALWAYS calculated using the planetary positions in the physical sky of the $D_1$ (Rāśi) chart, even when determining Dignity for higher Vargas like $D_9$ or $D_{60}$. Divisional charts are mathematical harmonics, not physical sky positions.

- **Intra-Varga Invariance Rule:**
  - In all higher divisional vargas ($D_2$ through $D_{60}$, with `is_varga=True`), whole-sign rules govern cleanly and unconditionally across all modes:
    - Primary Moolatrikona signs (Aries for Mars, Leo for Sun, Sagittarius for Jupiter, Libra for Venus, Aquarius for Saturn) confer full `"Moolatrikona"` dignity (yielding the classical 45 Virūpas in *Saptavargaja Bala*), while secondary signs confer pure `"Own Sign"` (30 Virūpas).
    - Exaltations and debilitations govern the entire $30^\circ$ sign: Moon in Taurus and Mercury in Virgo are universally `"Exalted"`, and Moon in Scorpio / Mercury in Pisces are universally `"Debilitated"`.
  - Sub-degree degree bounds ($0^\circ\text{--}12^\circ$, $0^\circ\text{--}20^\circ$) belong exclusively to the physical sky of the $D_1$ (Rāśi) chart.

- **Debilitation Calculation Modes (`debilitation_mode`):**
  - `kala_degree` (Empirical Option):
    Derived from Ernst Wilhelm's *Kala* software. Deep debilitation (*Parama Nīca*) degree limits are treated as boundaries:
    - Moon: Debilitated strictly between 0° and 3° Scorpio. Beyond 3°, reverts to Pañcadhā Maitrī with Mars.
    - Mercury: Debilitated strictly between 0° and 15° Pisces. Beyond 15°, reverts to Pañcadhā Maitrī with Jupiter.
  - `whole_sign` / `traditional` (Canonical Classical Standard):
    Adheres strictly to *BPHS* Ch. 3 and *Phaladīpikā* Ch. 2 orthodoxy, where debilitation governs the entire $30^\circ$ sign:
    - Moon: Debilitated across all 0°–30° of Scorpio.
    - Mercury: Debilitated across all 0°–30° of Pisces.

- **Even Rasi Varga Reversals:**
  Dasamsa ($D_{10}$) and Chaturvimsamsa ($D_{24}$) strictly follow the Parashara rule: "Reverse for Even Rasis". This means for Even signs, we start from the 9th sign (or Cancer for $D_{24}$) and count **backwards** instead of forwards.

---

## 5. Stage 2A Master Dignity Orchestrator (`calculate_chart_dignities`)
The master function `calculate_chart_dignities(baseline: ChartBaseline, debilitation_mode: str = "kala_degree", nodal_methodology: str = "ernst_wilhelm", ketu_own_sign: str = "Pisces") -> Dict[str, Any]` connects the Stage 1 `ChartBaseline` directly to the relationship engine:
1. **Precalculates Full 9x9 Friendship Matrices:** Bidirectional natural, temporary, and compound relationships for all 7 physical planets and nodes.
2. **Decomposes Varga Dignities Across All 16 Divisional Charts:** Evaluates each planet's dignity in $D_1$ through $D_{60}$ with `is_varga = (v_name != "D1")`.
3. **Functional Avasthā Overrides (*Phaladīpikā* Ch. 3 v. 19):**
   In $D_1$, physical celestial impairment takes functional precedence over sign placement:
   - **Combust (*Vikala*):** If a planet (other than Sun, Rahu, or Ketu) is combust within orb by the Sun, its $D_1$ avasthā is set to `"Vikala"` (impaired / deprived).
   - **Defeated in War (*Nīpīḍita*):** If a planet is defeated in planetary war (*Graha Yuddha* $\le 1^\circ$), its $D_1$ avasthā is set to `"Nipidita"` (vanquished / oppressed).
4. **Canonical Dīptādi Avasthā Output:** Maps every sign dignity directly into its classical physiological mood:

| Planetary Dignity | Sanskrit Dīptādi Avasthā | Psychological / Functional State |
| :--- | :--- | :--- |
| **Exalted** | *Pradīpta* | Radiant, effulgent, highly victorious |
| **Moolatrikona** | *Sukhita* | Delighted, comfortable, prosperous |
| **Own Sign** | *Svastha* | Confident, at home, independent |
| **Great Friend's Sign** | *Mudita* | Rejoicing, happy, affectionate, supported |
| **Friend's Sign** | *Mudita* | Happy (*suhṛd-gehe* per *Phaladīpikā* 3.18) |
| **Neutral's Sign** | *Śānta* | Calm, peaceful, steady (*sama-bhavane*) |
| **Enemy's Sign** | *Dīna* | Distressed, sorrowful, depressed |
| **Great Enemy's Sign** | *Dīna* | Distressed, impoverished |
| **Debilitated** | *Khala* | Fallen, tormented, disruptive |
| **Combust** | *Vikala* | Impaired, scorched by the Sun |
| **Defeated in War** | *Nīpīḍita* | Vanquished, suppressed in planetary war |

5. **Daśavarga Vaiśeṣikāṃśa Ladder (*Phaladīpikā* Ch. 3 v. 6–7):**
   Computes the cumulative count of favorable vargas (Exalted, Moolatrikona, Own Sign, Great Friend, Friend) across the 10 classical vargas ($D_1, D_2, D_3, D_7, D_9, D_{10}, D_{12}, D_{16}, D_{30}, D_{60}$):
   - 2 favorable vargas = *Pārijāta*
   - 3 favorable vargas = *Uttama*
   - 4 favorable vargas = *Gopura*
   - 5 favorable vargas = *Siṁhāsana*
   - 6 favorable vargas = *Parvata*
   - 7 favorable vargas = *Devaloka*
   - 8 favorable vargas = *Suraloka*
   - 9 favorable vargas = *Airāvata*
   - 10 favorable vargas = *Brahmapada*
   Returned under `"vaisesikamsha"` in the master dictionary.
