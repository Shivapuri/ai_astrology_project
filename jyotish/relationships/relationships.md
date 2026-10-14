# Jyotish Engine: Planetary Friendships & Dignity (relationships.py)

This file serves as the foundational Stage 2A astrological relationship and dignity engine (Hemisphere A) based on *Bṛhat Parāśara Horā Śāstra* (BPHS), Mantreśvara's *Phaladīpikā*, Dr. B.V. Raman's *Graha and Bhava Balas*, and Ernst Wilhelm's *Kala* software.

---

## 1. Simple Description (For the Layperson)
In Jyotish, planets are like people. They have their own inborn personalities, but they also react to who is sitting next to them in a room. To figure out how two planets feel about each other, the software does a 3-step calculation:

1. **Natural Friendship (Naisargika):** This is the permanent, inborn "chemistry" between two planets. Just like some people naturally get along, Jupiter and the Sun are natural friends.
2. **Temporary Friendship (Tatkalika):** This is based purely on physical distance in the sky on the exact day you were born. Even if two planets are natural enemies, if they give each other enough "personal space," they agree to a temporary truce. If they are crammed into the same room, they annoy each other and become temporary enemies.
3. **Compound Friendship (Panchadha):** This is the final, ultimate score. The software simply adds the Natural score and the Temporary score together to get 5 final levels (Great Friend, Friend, Neutral, Enemy, Great Enemy).

Whenever the software says a planet is in a "Great Friend's Sign," it is using this final, 5-level Compound Friendship score.

---

## 2. Technical AI Description (Logic Constraints)
If you are inspecting or maintaining `relationships.py`, strictly observe these mathematical rules:

1. **Three-Tier Friendship System & Matrix Scope:**
   - Evaluates a complete $9 \times 9$ bidirectional matrix covering all 7 physical planets plus Rāhu and Ketu (`natural_relationships`, `temporary_relationships`, `compound_relationships`), preventing `KeyError` exceptions when physical planets query nodes.
   - `get_natural_relationship()` (*Naisargika*):
     - Physical planets follow *BPHS* Ch. 3 v. 55 (Ch. 15 in standard editions) *Moolatrikona* derivations and *Phaladīpikā* Ch. 2 v. 21–22 (*Graha and Bhava Balas* Art. 24).
     - Rāhu and Ketu support dual methodologies via `nodal_methodology`:
       - `"ernst_wilhelm"` (Default): Rāhu acts as Saturn's proxy and Ketu acts as Mars's proxy (*Śanivad Rāhuḥ, Kujavad Ketuḥ*, grounded in *Phaladīpikā* Ch. 8 v. 34).
       - `"phaladipika"`: Both nodes follow Mantreśvara’s *Phaladīpikā* (Ch. 2 v. 23) Asura coalition: Friends with Mercury, Venus, Saturn; Neutral with Mars; Enemies with Sun, Moon, Jupiter.
   - `get_temporary_relationship(p1_d1_idx, p2_d1_idx)` (*Tātkālika*):
     - Based purely on physical sign indices (`0..11`) in the $D_1$ (Rāśi) chart (*BPHS* Ch. 3 v. 56; *Phaladīpikā* Ch. 2 v. 23).
     - Houses 2, 3, 4, 10, 11, 12 away (`distance in [1, 2, 3, 9, 10, 11]`) = `"Friend"`.
     - Others (conjunct `p1_d1_idx == p2_d1_idx`, or 5, 6, 7, 8, 9 away) = `"Enemy"`.
     - *Note:* The same-body identity check (`"Self" if p1 == p2`) is enforced by the master orchestrator `calculate_chart_dignities()` before calling `get_temporary_relationship()`.
   - `get_compound_relationship()` (*Pañcadhā*):
     - Mathematical sum of Natural + Temporary ($-2 \text{ to } +2$) per *BPHS* Ch. 3 v. 57–58, *Phaladīpikā* Ch. 2 v. 24, and *Graha and Bhava Balas* Art. 26.
     - Returns 5 levels: `"Great Friend"`, `"Friend"`, `"Neutral"`, `"Enemy"`, `"Great Enemy"` (or `"Self"` if `natural == "Self"`).

2. **Dignity Logic (`get_dignity`):**
   - Must check fixed dignities FIRST (Exalted, Debilitated, Moolatrikona, Own Sign).
   - **Physical Planets in $D_1$:** Degree bounds follow *BPHS* Ch. 3 v. 51–54 and *Phaladīpikā* Ch. 1 v. 7:
     - Sun in Leo: $0^\circ\text{--}20^\circ$ `"Moolatrikona"`, $>20^\circ$ `"Own Sign"`.
     - Moon in Taurus: $0^\circ\text{--}3^\circ$ `"Exalted"`, $>3^\circ$ `"Moolatrikona"`.
     - Mars in Aries: $0^\circ\text{--}12^\circ$ `"Moolatrikona"`, $>12^\circ$ `"Own Sign"`.
     - Mercury in Virgo: $0^\circ\text{--}15^\circ$ `"Exalted"`, $15^\circ\text{--}20^\circ$ `"Moolatrikona"`, $>20^\circ$ `"Own Sign"`.
     - Jupiter in Sagittarius: $0^\circ\text{--}10^\circ$ `"Moolatrikona"`, $>10^\circ$ `"Own Sign"`.
     - Venus in Libra: $0^\circ\text{--}15^\circ$ `"Moolatrikona"`, $>15^\circ$ `"Own Sign"` *(follows BPHS 3.53 and Kala's $15^\circ$ bound rather than Phaladīpikā 1.7's $5^\circ$ bound)*.
     - Saturn in Aquarius: $0^\circ\text{--}20^\circ$ `"Moolatrikona"`, $>20^\circ$ `"Own Sign"`.
   - **Nodal Fixed Dignities (*Kala* / *BPHS* / *Uttara Kālāmṛta* Synthesis):**
     - Rāhu: Exalted in Taurus, Debilitated in Scorpio, Moolatrikona in Gemini, Own Sign in Aquarius.
     - Ketu: Exalted in Scorpio, Debilitated in Taurus, Moolatrikona in Sagittarius, Own Sign in `ketu_own_sign` (default `"Pisces"`, *Mīna*, resolving dual Jupiter-Saturn rulership symmetry).
   - **Co-Rulership Identity:** In `calculate_chart_dignities()`, Rāhu in Aquarius and Ketu in `ketu_own_sign` (Pisces) set `is_own_house = True` and `effective_lord = p_name`, yielding `"Self"` for natural, temporary, and compound relationships and outputting pure `"Own Sign"` (*Sva-kṣetra* / *Svastha*). *(Note: When Rāhu is in Gemini or Ketu is in Sagittarius, `get_dignity()` returns `"Moolatrikona"`, while `effective_lord` remains Mercury or Jupiter respectively).*
   - If no fixed dignity matches, `get_dignity()` returns `f"{compound_rel}'s Sign"` (e.g., `"Great Friend's Sign"`, `"Enemy's Sign"`).

3. **Rāśi Aspects (`get_rasi_drishti`):**
   - Rāśi Dṛṣṭi (*BPHS* Ch. 8 v. 1–5) resides in `jyotish/aspects/aspects.py` as `get_rasi_drishti` (rather than inside `relationships.py`) and is imported where needed.
   - Returns whole-sign mutual aspects: Moveable (Cardinal) signs aspect Fixed signs (except adjacent); Fixed signs aspect Moveable signs (except adjacent); Dual (Mutable) signs aspect all other Dual signs.

---

## 3. Scriptural Foundation (Sanskrit Quotes)
The rules in this file are directly grounded in *Bṛhat Parāśara Horā Śāstra* (BPHS) and Mantreśvara's *Phaladīpikā*.

### Natural Friendship (Naisargika)
> *त्रिकोणात् स्वात्सुखस्वाऽन्त्यधीधर्मायुःस्वतुङ्गपाः । सुहृदो रिपवश्चान्ये समाश्चोभयलक्षणाः ॥*
> “From Mulatrikona, the owner of the 4th, 2nd, 12th, 5th, 9th, and 8th as well as the lord of its exaltation Rasi are friendly. Inimical are the others. Neutral are those that indicate both (friendly on one count and inimical on another count, which may happen for those Grahas that rule two Rasis).”
> *— Brihat Parashara Hora Shastra: Ch. 3 v. 55 (Ch. 15 v. 55 in standard editions); see also Phaladīpikā Ch. 2 v. 21–22*

### Nodal Natural Relationships (Dual Modes)
* **Asura Coalition (`nodal_methodology="phaladipika"`):**
  > “For Rāhu and Ketu, friends are Mercury, Venus, and Saturn; Mars is neutral; Sun, Moon, and Jupiter are enemies.”
  > *— Phaladīpikā: Ch. 2 v. 23*
* **Saturn/Mars Proxy (`nodal_methodology="ernst_wilhelm"`):**
  > *शनिवद्राहुः कुजवत्केतुः फलदाता स्यादिह सम्प्रोक्तः ।*
  > “Rāhu acts like Saturn and Ketu acts like Mars.”
  > *— Phaladīpikā: Ch. 8 v. 34*

### Temporary Friendship (Tatkalika)
> *दशबन्ध्वायसहजस्वान्त्यस्थास्तु परस्परम् । तत्काले मित्रतां यान्ति रिपवोऽन्यत्र संस्थिताः ॥*
> “Those standing in the 10th, 4th, 11th, 3rd, 2nd and 12th from each other are at that time friendly, those standing elsewhere are enemies.”
> *— Brihat Parashara Hora Shastra: Ch. 3 v. 56; Phaladīpikā: Ch. 2 v. 23*

### Compound Friendship (Panchadha)
> “Friendly at the time as well as naturally so – great friendship (*Adhimitra*). Friendship if friendly and neutral (*Mitra*). Enemies if inimical and neutral (*Śatru*). Neutral if friendly and inimical (*Sama*). Both inimical – great enmity (*Adhiśatru*). Thus should the astrologer examine the nativity when pronouncing effects.”
> *— Brihat Parashara Hora Shastra: Ch. 3 v. 57–58; Phaladīpikā: Ch. 2 v. 24*

---

## 4. Special Astrological Exceptions & Limits

- **Varga-Specific Distances (Tātkālika Anchored to $D_1$):**
  *Tātkālika Maitrī* (Temporary Friendship) is ALWAYS calculated using the planetary positions in the physical sky of the $D_1$ (Rāśi) chart, even when determining Dignity for higher Vargas like $D_9$ or $D_{60}$. Divisional charts are mathematical harmonics, not physical sky positions.

- **Intra-Varga Invariance Rule (`is_varga=True`):**
  - In all higher divisional vargas ($D_2$ through $D_{60}$, with `is_varga=True`), whole-sign rules govern cleanly and unconditionally across all modes:
    - Primary Moolatrikona signs (Aries for Mars, Leo for Sun, Sagittarius for Jupiter, Libra for Venus, Aquarius for Saturn) confer full `"Moolatrikona"` dignity (yielding the classical 45 Virūpas in *Saptavargaja Bala*), while secondary signs confer pure `"Own Sign"` (30 Virūpas).
    - Exaltations and debilitations govern the entire $30^\circ$ sign: Moon in Taurus and Mercury in Virgo are universally `"Exalted"`, and Moon in Scorpio / Mercury in Pisces are universally `"Debilitated"`.
  - Sub-sign degree bounds ($0^\circ\text{--}3^\circ$, $0^\circ\text{--}10^\circ$, $0^\circ\text{--}12^\circ$, $0^\circ\text{--}15^\circ$, $0^\circ\text{--}20^\circ$) belong exclusively to the physical sky of the $D_1$ (Rāśi) chart.

- **Debilitation Calculation Modes (`debilitation_mode`):**
  - `kala_degree` (Empirical Option — Default):
    Derived from Ernst Wilhelm's *Kala* software. Deep debilitation (*Parama Nīca*) degree limits are treated as boundaries for the two planets whose exaltation signs contain both Exaltation and Moolatrikona zones:
    - Moon: Debilitated strictly between $0^\circ$ and $3^\circ$ Scorpio. Beyond $3^\circ$, reverts to *Pañcadhā Maitrī* with Mars.
    - Mercury: Debilitated strictly between $0^\circ$ and $15^\circ$ Pisces. Beyond $15^\circ$, reverts to *Pañcadhā Maitrī* with Jupiter.
  - `whole_sign` / `traditional` (Canonical Classical Standard):
    Adheres strictly to *BPHS* Ch. 3 v. 49–50 and *Phaladīpikā* Ch. 1 v. 5–7 orthodoxy, where debilitation governs the entire $30^\circ$ sign:
    - Moon: Debilitated across all $0^\circ\text{--}30^\circ$ of Scorpio.
    - Mercury: Debilitated across all $0^\circ\text{--}30^\circ$ of Pisces.

- **Upstream Even Rāśi Varga Reversals ($D_{10}$ and $D_{24}$):**
  Handled upstream in Stage 1 (`baseline.py` / `baseline_math.py`) before `relationships.py` is called: Dasamsa ($D_{10}$) and Chaturvimsamsa ($D_{24}$) follow the Parashara rule where Even signs count backwards rather than forwards.

---

## 5. Stage 2A Master Dignity Orchestrator (`calculate_chart_dignities`)
The master function `calculate_chart_dignities(baseline: ChartBaseline, debilitation_mode: str = "kala_degree", nodal_methodology: str = "ernst_wilhelm", ketu_own_sign: str = "Pisces") -> Dict[str, Any]` connects the Stage 1 `ChartBaseline` directly to the relationship engine:

1. **Precalculates Full $9 \times 9$ Friendship Matrices:** Bidirectional natural, temporary, and compound relationships for all 7 physical planets and nodes.
2. **Decomposes Varga Dignities Across All 16 Divisional Charts:** Evaluates each planet's dignity in $D_1$ through $D_{60}$ with `is_varga = (v_name != "D1")`.
3. **Functional Avasthā Overrides (*Phaladīpikā* Ch. 3 v. 19):**
   In $D_1$ (`not is_varga`), physical celestial impairment takes functional precedence over sign placement (with Planetary War checked prior to Combustion):
   - **Defeated in War (*Nipīḍita*):** If a planet is defeated in planetary war (*Graha Yuddha* $\le 1^\circ$), its $D_1$ avasthā is set to `"Nipidita"` (vanquished / oppressed).
   - **Combust (*Vikala*):** If a planet (other than Sun, Rāhu, or Ketu) is combust within orb by the Sun, its $D_1$ avasthā is set to `"Vikala"` (impaired / deprived of rays).
4. **Canonical 9-State Dīptādi Avasthā Output (`DIPTADI_AVASTHA_MAP`):**
   Maps every sign dignity into a 1-to-1 classical state by synthesizing *Phaladīpikā* Ch. 3 v. 18–19 (`Pradīpta`, `Sukhita`, `Svastha`, `Mudita`, `Vikala`, `Nipīḍita`) with *BPHS* Ch. 45 / *Sārāvalī* Ch. 5 v. 36 (`Śānta` for Neutral's Sign, `Dīna` for Enemy's Sign, and `Khala` mapped to Debilitated so every sign dignity has a deterministic lookup key):

| Planetary Dignity | Code Output (`avastha`) | Classical Source & Note | Functional State |
| :--- | :--- | :--- | :--- |
| **Exalted** | `"Pradipta"` | *Phaladīpikā* 3.18 (*svocce pradīptaḥ*) | Radiant, effulgent, highly victorious |
| **Moolatrikona** | `"Sukhita"` | *Phaladīpikā* 3.18 (*sukhitas trikoṇe*) | Delighted, comfortable, prosperous |
| **Own Sign** | `"Svastha"` | *Phaladīpikā* 3.18 (*svasthaḥ svagehe*) | Confident, at home, independent |
| **Great Friend's Sign** | `"Mudita"` | *Phaladīpikā* 3.18 (*muditaḥ suhṛdbhe*) | Rejoicing, happy, supported |
| **Friend's Sign** | `"Mudita"` | *Phaladīpikā* 3.18 (*muditaḥ suhṛdbhe*) | Happy, friendly environment |
| **Neutral's Sign** | `"Santa"` | *Sārāvalī* 5.36 (*sama-bhavane*); DPK 3.18 uses *Śānta* for benefic varga | Calm, peaceful, steady |
| **Enemy's Sign** | `"Dina"` | *BPHS* Ch. 45 / *Sārāvalī*; DPK 3.19 calls this *Suduḥkhita* | Distressed, sorrowful, depressed |
| **Great Enemy's Sign** | `"Dina"` | *BPHS* Ch. 45 / *Sārāvalī*; DPK 3.19 calls this *Suduḥkhita* | Distressed, impoverished |
| **Debilitated** | `"Khala"` | *BPHS / Kala* convention; DPK 3.19 calls Debilitated *Atibhīta* and malefic varga *Khala* | Fallen, tormented, disruptive |
| **Combust ($D_1$)** | `"Vikala"` | *Phaladīpikā* 3.19 (*vikalo'stayātaḥ*) | Impaired, scorched by the Sun |
| **Defeated in War ($D_1$)** | `"Nipidita"` | *Phaladīpikā* 3.19 (*grahābhibhūtaḥ sa nipīḍitaḥ*) | Vanquished, suppressed in planetary war |

5. **Daśavarga Vaiśeṣikāṃśa Ladder (*Phaladīpikā* Ch. 3 v. 6–7 & *Jātaka Pārijāta*):**
   Computes the cumulative count of favorable vargas (`"Exalted"`, `"Moolatrikona"`, `"Own Sign"`, `"Great Friend"`, `"Friend"`) for the 7 physical planets across the 10 classical vargas ($D_1, D_2, D_3, D_7, D_9, D_{10}, D_{12}, D_{16}, D_{30}, D_{60}$). Including friendly signs alongside own and exaltation signs directly follows *Phaladīpikā* 3.7 (*suhṛt-sva-tuṅgopagateṣu kheṭe*):
   - 0–1 favorable vargas = `"Sāmānya"` (default fallback)
   - 2 favorable vargas = `"Pārijāta"`
   - 3 favorable vargas = `"Uttama"`
   - 4 favorable vargas = `"Gopura"`
   - 5 favorable vargas = `"Siṁhāsana"`
   - 6 favorable vargas = `"Parvata"` (*Pārāvata* in DPK 3.7; *Parvata* in *Jātaka Pārijāta* / Raman)
   - 7 favorable vargas = `"Devaloka"`
   - 8 favorable vargas = `"Suraloka"`
   - 9 favorable vargas = `"Airāvata"`
   - 10 favorable vargas = `"Brahmapada"` (*Jātaka Pārijāta* / *Sarvārtha Chintāmaṇi*; *Śrīdhāma* in *BPHS* Ch. 6)
   Returned under `"vaisesikamsha"` in the master dictionary.
