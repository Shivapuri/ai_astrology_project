# Divisional Charts (Ṣoḍaśavarga) Engine: Architectural & Mathematical Specification

**Module References:**
- Primary Calculus: [`jyotish/baseline_tables.py`](file:///Users/hajnaljanos/PycharmProjects/astra/jyotish/baseline_tables.py), [`jyotish/baseline_math.py`](file:///Users/hajnaljanos/PycharmProjects/astra/jyotish/baseline_math.py)
- Chart Baseline Orchestration: [`jyotish/baseline.py`](file:///Users/hajnaljanos/PycharmProjects/astra/jyotish/baseline.py)
- Pipeline & House Scaffolding: [`jyotish/pipeline.py`](file:///Users/hajnaljanos/PycharmProjects/astra/jyotish/pipeline.py)
- Verification Test Suite: [`tests/test_vargas.py`](file:///Users/hajnaljanos/PycharmProjects/astra/tests/test_vargas.py)

---

## 1. Simple Intuitive Explanation

Think of your birth chart (*Rāśi* / D1) like an overall snapshot of a house from the outside. It tells you the general shape and appearance of the building. 

Divisional charts (*Vargas*, sub-charts created by slicing each 30° zodiac sign into smaller equal portions) are like walking into specific rooms of that house with a magnifying glass:
- If you want to examine **career**, you look into the career room (**D10 Daśāṁśa**).
- If you want to understand **relationships and marriage**, you look into the partnership room (**D9 Navāṁśa**).
- If you want to check **parents and lineage**, you look into the ancestral room (**D12 Dvādaśāṁśa**).
- If you want to inspect **hidden obstacles and health challenges**, you examine the bound divisions (**D30 Triṁśāṁśa**).

In Sanskrit:
- An ***aṁśa*** is an individual fractional slice (a mathematical subdivision of a sign).
- A ***varga*** is the collection or harmonic grouping of those slices across the entire zodiac.
- When an Ascendant (*Lagna*, the rising degree on the eastern horizon) is calculated within that specific slice, the collection forms a complete divisional chart (*Varga Cakra*).

---

## 2. Classical Scriptural Grounding

This engine is strictly built upon the foundational authorities of classical Jyotiṣa:
1. **Mantreśvara's *Phaladīpikā* (Ch. 3–4):** Provides explicit rules for Horā, Drekkāṇa, Navāṁśa, Triṁśāṁśa bounds, and the exact 24 malefic Ṣaṣṭiāṁśa arcs.
2. **Maharṣi Parāśara's *Bṛhat Parāśara Horā Śāstra* (BPHS, Ch. 6):** Details the mathematical construction, counting directions (odd vs. even signs), and ruling deities across the sixteen divisional charts (*Ṣoḍaśavarga*).
3. **Kalyāṇavarmā's *Sārāvalī* (Ch. 3):** Cross-references the planetary allocations, triplicities, and varga dignities.

---

## 3. Architectural Taxonomy & Structural Families

In classical Jyotiṣa, not all divisional charts are identical in structure. They fall into three distinct structural families:

| Family | Divisional Charts | Fundamental Nature & House Engine |
| :--- | :--- | :--- |
| **1. Graha Vargas** *(Planetary Domains)* | **D2 (Horā), D3 (Drekkāṇa), D30 (Triṁśāṁśa)** | **Not full 12-sign zodiacs!** Governed directly by planetary rulers and astronomical glyphs (`☉`, `☽`, `♂`, `☿`, `♃`, `♀`, `♄`). D2 operates in a **2-Chamber Binary Structure** (Solar vs. Lunar) rather than 12 houses. |
| **2. Rāśi Vargas** *(Zodiacal Harmonics)* | **D1, D4, D7, D9, D10, D12, D16, D20, D24, D27, D40, D45** | **True 12-sign harmonic projections** (Aries through Pisces). Governed by sign domicile lords; evaluated via **Whole Sign Houses** (*Rāśi Bhāva*) anchored to each divisional Ascendant. |
| **3. Aṁśa Varga** *(Polarity Arcs)* | **D60 (Ṣaṣṭiāṁśa)** | **60 half-degree arcs per sign.** Evaluated primarily as qualitative **Śubha** (benefic / auspicious) versus **Aśubha** (malefic / inauspicious) zones per *Phaladīpikā* 3.5, with deity names and sign harmonics. |

### Classical Collections (Varga Tiers)
Classical texts group these charts into standardized hierarchical tiers for evaluating planetary strength (*Vimśopaka Bala*):
- **Ṣaḍvarga (6-fold tier):** D1, D2, D3, D9, D12, D30.
- **Saptavarga (7-fold tier):** D1, D2, D3, D7, D9, D12, D30.
- **Daśavarga (10-fold tier):** D1, D2, D3, D7, D9, D10, D12, D16, D30, D60.
- **Ṣoḍaśavarga (16-fold tier):** All 16 divisional charts (D1 through D60).

---

## 4. In-Depth Mathematical Specification for All 16 Charts

### 1. D1 – Rāśi (The Primary Physical Field / Kṣetra)
- **Significance:** Physical incarnation, body constitution, general vitality, and the base reality where all events unfold.
- **Slice Geometry:** $1 \times 30^\circ00'00"$ per sign (Full 30° span).
- **Scriptural Source:** *Phaladīpikā* 3.1; *BPHS* 6.3–4.
- **Algorithm:**
  $$\lambda_{\text{D1}} = \lambda_{\text{natal}} \pmod{360^\circ}$$
- **Rulership Model:** Zodiacal (`is_planetary_varga = False`). Domicile lord from `SIGN_LORDS`.
- **Bhāva Engine:** Campanus House System (with Whole Sign overlay).

---

### 2. D2 – Horā (The Solar & Lunar Binary Chambers)
- **Significance:** Wealth, material sustenance, vitality polarity (Solar / Pingalā vs. Lunar / Iḍā).
- **Slice Geometry:** $2 \times 15^\circ00'00"$ per sign (24 divisions across the zodiac).
- **Scriptural Source:** *BPHS* 6.5–6; *Phaladīpikā* 3.4, 3.17.
- **Algorithm (`d2_mode = "parashari"`):**
  Let $\text{sign\_idx} = \lfloor \lambda / 30 \rfloor$, $\text{deg} = \lambda \pmod{30}$, $\text{is\_odd} = (\text{sign\_idx} \pmod 2 == 0)$, and $\text{div\_idx} = \lfloor \text{deg} / 15.0 \rfloor$:
  $$\text{varga\_sign} = \begin{cases} 4 \text{ (Leo / Sun)}, & \text{if } (\text{is\_odd} \land \text{div\_idx} = 0) \lor (\neg\text{is\_odd} \land \text{div\_idx} = 1) \\ 3 \text{ (Cancer / Moon)}, & \text{if } (\text{is\_odd} \land \text{div\_idx} = 1) \lor (\neg\text{is\_odd} \land \text{div\_idx} = 0) \end{cases}$$
  $$\lambda_{\text{D2}} = (\text{varga\_sign} \times 30.0) + \left(\frac{\text{deg} \pmod{15.0}}{15.0} \times 30.0\right)$$
- **Rulership Model:** Planetary Domain (`is_planetary_varga = True`).
  - Sun half: `ruler = "Sun"`, `ruler_symbol = "☉"`, `display_entity = "☉ Sun"`, `hora_polarity = "Solar / Pingala"`.
  - Moon half: `ruler = "Moon"`, `ruler_symbol = "☽"`, `display_entity = "☽ Moon"`, `hora_polarity = "Lunar / Ida"`.
- **Bhāva Engine:** **Two-Chamber Binary Model.** D2 does **not** generate 12 houses. It forms two distinct chambers:
  1. *Chamber 1 (Solar / Pingala)*: Ruler Sun (`☉`). Contains planets where `hora_lord == "Sun"`.
  2. *Chamber 2 (Lunar / Ida)*: Ruler Moon (`☽`). Contains planets where `hora_lord == "Moon"`.
  The Ascendant (`Asc`) is placed into whichever chamber contains the Horā Lagna.

---

### 3. D3 – Drekkāṇa (The Trinal Thirds)
- **Significance:** Siblings, physical courage, vitality, energy, and bold initiative.
- **Slice Geometry:** $3 \times 10^\circ00'00"$ per sign (36 divisions across the zodiac).
- **Scriptural Source:** *BPHS* 6.7–8; *Phaladīpikā* 3.5.
- **Algorithm:**
  $$\text{div\_idx} = \lfloor \text{deg} / 10.0 \rfloor \quad (\in \{0, 1, 2\})$$
  $$\text{target\_sign} = (\text{sign\_idx} + \text{div\_idx} \times 4) \pmod{12}$$
  $$\lambda_{\text{D3}} = (\text{target\_sign} \times 30.0) + \left(\frac{\text{deg} \pmod{10.0}}{10.0} \times 30.0\right)$$
- **Rulership Model:** Planetary Triad (`is_planetary_varga = True`).
  - Governed by the planetary lord of the trinal sign (`ruler = SIGN_LORDS[ZODIAC_SIGNS[target_sign]]`).
  - `display_entity = f"{ruler_symbol} {ruler}"` (e.g. `"♂ Mars"`, `"☉ Sun"`).
  - Computational `sign` stores the sign name to guarantee mathematical dignity calculations do not break.
- **Bhāva Engine:** Whole Sign Houses ($1$ through $12$) anchored to the Drekkāṇa Lagna sign.

---

### 4. D4 – Caturthāṁśa / Turyāṁśa (The Quadrants)
- **Significance:** Fixed property, real estate, conveyances, fixed fortune, and domestic home.
- **Slice Geometry:** $4 \times 7^\circ30'00"$ ($7.5^\circ$) per sign (48 divisions across the zodiac).
- **Scriptural Source:** *BPHS* 6.9–10 (Kendras from base sign: $+0, +3, +6, +9$).
- **Algorithm:**
  $$\text{div\_idx} = \lfloor \text{deg} / 7.5 \rfloor \quad (\in \{0, 1, 2, 3\})$$
  $$\text{varga\_sign} = (\text{sign\_idx} + \text{div\_idx} \times 3) \pmod{12}$$
  $$\lambda_{\text{D4}} = (\text{varga\_sign} \times 30.0) + \left(\frac{\text{deg} \pmod{7.5}}{7.5} \times 30.0\right)$$
- **Rulership Model:** Zodiacal (`is_planetary_varga = False`).
- **Bhāva Engine:** Whole Sign Houses anchored to D4 Lagna.

---

### 5. D7 – Saptāṁśa (The Sevenths)
- **Significance:** Progeny, children, grandchildren, dynastic lineage, creative outputs.
- **Slice Geometry:** $7 \times 4^\circ17'08.57"$ ($30^\circ/7$) per sign (84 divisions across the zodiac).
- **Scriptural Source:** *BPHS* 6.11–12; *Phaladīpikā* 3.4 (Odd signs start from base sign; even signs start from 7th sign / $+6$).
- **Algorithm:**
  $$\text{start\_sign} = \text{sign\_idx if is\_odd else } (\text{sign\_idx} + 6) \pmod{12}$$
  $$\text{div\_idx} = \lfloor \text{deg} / (30.0 / 7.0) \rfloor \quad (\in \{0, \dots, 6\})$$
  $$\text{varga\_sign} = (\text{start\_sign} + \text{div\_idx}) \pmod{12}$$
  $$\lambda_{\text{D7}} = (\text{varga\_sign} \times 30.0) + \left(\frac{\text{deg} \pmod{30.0/7.0}}{30.0/7.0} \times 30.0\right)$$
- **Rulership Model:** Zodiacal (`is_planetary_varga = False`).
- **Bhāva Engine:** Whole Sign Houses anchored to D7 Lagna.

---

### 6. D9 – Navāṁśa (The Soul's Dharma & True Dignity)
- **Significance:** Soul purpose (*Dharma*), marital compatibility, hidden inner strength, and true planetary dignity (*Vargottama* anchor).
- **Slice Geometry:** $9 \times 3^\circ20'00"$ ($3.3333^\circ$) per sign (108 divisions, matching the 108 Nakṣatra Pādas).
- **Scriptural Source:** *BPHS* 6.13–14; *Phaladīpikā* 3.4, 3.11.
  - Fiery Signs (Aries, Leo, Sagittarius): Count begins at **Aries** ($0$).
  - Earthy Signs (Taurus, Virgo, Capricorn): Count begins at **Capricorn** ($9$).
  - Airy Signs (Gemini, Libra, Aquarius): Count begins at **Libra** ($6$).
  - Watery Signs (Cancer, Scorpio, Pisces): Count begins at **Cancer** ($3$).
- **Algorithm:**
  $$\text{element} = \text{sign\_idx} \pmod 4 \quad (0=\text{Fire}, 1=\text{Earth}, 2=\text{Air}, 3=\text{Water})$$
  $$\text{start\_sign} = (\text{element} \times 9) \pmod{12}$$
  $$\text{div\_idx} = \lfloor \text{deg} / 3.3333333 \rfloor \quad (\in \{0, \dots, 8\})$$
  $$\text{varga\_sign} = (\text{start\_sign} + \text{div\_idx}) \pmod{12}$$
  $$\lambda_{\text{D9}} = (\text{varga\_sign} \times 30.0) + \left(\frac{\text{deg} \pmod{3.3333333}}{3.3333333} \times 30.0\right)$$
- **Rulership Model:** Zodiacal (`is_planetary_varga = False`). Identical D1 and D9 signs confer **Vargottama** status.
- **Bhāva Engine:** Whole Sign Houses anchored to D9 Lagna.

---

### 7. D10 – Daśāṁśa (Career, Authority & Public Status)
- **Significance:** Profession, career success, executive rank, public honor, and accomplishments (*Karmaphala*).
- **Slice Geometry:** $10 \times 3^\circ00'00"$ per sign (120 divisions across the zodiac).
- **Scriptural Source:** *BPHS* 6.15–16. Odd signs count from sign itself; even signs count from 9th sign ($+8$).
- **Algorithm:**
  $$\text{div\_idx} = \lfloor \text{deg} / 3.0 \rfloor \quad (\in \{0, \dots, 9\})$$
  $$\text{varga\_sign} = \begin{cases} (\text{sign\_idx} + \text{div\_idx}) \pmod{12}, & \text{if is\_odd} \\ (\text{sign\_idx} + 8 - \text{div\_idx}) \pmod{12}, & \text{if even \& } \text{d10\_mode}=\text{"reverse" (Kala default)} \\ (\text{sign\_idx} + 8 + \text{div\_idx}) \pmod{12}, & \text{if even \& } \text{d10\_mode}=\text{"direct"} \end{cases}$$
  $$\lambda_{\text{D10}} = (\text{varga\_sign} \times 30.0) + \left(\frac{\text{deg} \pmod{3.0}}{3.0} \times 30.0\right)$$
- **Rulership Model:** Zodiacal (`is_planetary_varga = False`).
- **Bhāva Engine:** Whole Sign Houses anchored to D10 Lagna.

---

### 8. D12 – Dvādaśāṁśa (Parents & Ancestral Lineage)
- **Significance:** Father, mother, ancestral heritage, and inherited family karma.
- **Slice Geometry:** $12 \times 2^\circ30'00"$ ($2.5^\circ$) per sign (144 divisions across the zodiac).
- **Scriptural Source:** *BPHS* 6.17–18; *Phaladīpikā* 3.4. Counting starts directly from the sign itself.
- **Algorithm:**
  $$\text{div\_idx} = \lfloor \text{deg} / 2.5 \rfloor \quad (\in \{0, \dots, 11\})$$
  $$\text{varga\_sign} = (\text{sign\_idx} + \text{div\_idx}) \pmod{12}$$
  $$\lambda_{\text{D12}} = (\text{varga\_sign} \times 30.0) + \left(\frac{\text{deg} \pmod{2.5}}{2.5} \times 30.0\right)$$
- **Rulership Model:** Zodiacal (`is_planetary_varga = False`).
- **Bhāva Engine:** Whole Sign Houses anchored to D12 Lagna.

---

### 9. D16 – Ṣoḍaśāṁśa / Kalāṁśa (Vehicles & Contentment)
- **Significance:** Vehicles, conveyances, material comforts, luxuries, and inner emotional contentment.
- **Slice Geometry:** $16 \times 1^\circ52'30"$ ($1.875^\circ$) per sign (192 divisions across the zodiac).
- **Scriptural Source:** *BPHS* 6.19–21 (Modal progression: Movable $\to$ Aries, Fixed $\to$ Leo, Dual $\to$ Sagittarius).
- **Algorithm:**
  $$\text{modality} = \text{sign\_idx} \pmod 3 \quad (0=\text{Movable}, 1=\text{Fixed}, 2=\text{Dual})$$
  $$\text{start\_sign} = (\text{modality} \times 4) \pmod{12}$$
  $$\text{div\_idx} = \lfloor \text{deg} / 1.875 \rfloor \quad (\in \{0, \dots, 15\})$$
  $$\text{varga\_sign} = (\text{start\_sign} + \text{div\_idx}) \pmod{12}$$
  $$\lambda_{\text{D16}} = (\text{varga\_sign} \times 30.0) + \left(\frac{\text{deg} \pmod{1.875}}{1.875} \times 30.0\right)$$
- **Rulership Model:** Zodiacal (`is_planetary_varga = False`).
- **Bhāva Engine:** Whole Sign Houses anchored to D16 Lagna.

---

### 10. D20 – Viṁśāṁśa (Spiritual Practice & Devotion)
- **Significance:** Spiritual practices (*Upāsanā*), meditation, religious faith, and mantra attainment.
- **Slice Geometry:** $20 \times 1^\circ30'00"$ ($1.5^\circ$) per sign (240 divisions across the zodiac).
- **Scriptural Source:** *BPHS* 6.22–23 (Modal progression: Movable $\to$ Aries $0$, Fixed $\to$ Sagittarius $8$, Dual $\to$ Leo $4$).
- **Algorithm:**
  $$\text{start\_sign} = 0 \text{ if mod}=0 \text{ else } (8 \text{ if mod}=1 \text{ else } 4)$$
  $$\text{div\_idx} = \lfloor \text{deg} / 1.5 \rfloor \quad (\in \{0, \dots, 19\})$$
  $$\text{varga\_sign} = (\text{start\_sign} + \text{div\_idx}) \pmod{12}$$
  $$\lambda_{\text{D20}} = (\text{varga\_sign} \times 30.0) + \left(\frac{\text{deg} \pmod{1.5}}{1.5} \times 30.0\right)$$
- **Rulership Model:** Zodiacal (`is_planetary_varga = False`).
- **Bhāva Engine:** Whole Sign Houses anchored to D20 Lagna.

---

### 11. D24 – Caturviṁśāṁśa / Siddhāṁśa (Intellect & Learning)
- **Significance:** Higher education, academic scholarship, mental memory, and spiritual learning.
- **Slice Geometry:** $24 \times 1^\circ15'00"$ ($1.25^\circ$) per sign (288 divisions across the zodiac).
- **Scriptural Source:** *BPHS* 6.24–25 (Odd signs start at Leo $4$; even signs start at Cancer $3$).
- **Algorithm:**
  $$\text{div\_idx} = \lfloor \text{deg} / 1.25 \rfloor \quad (\in \{0, \dots, 23\})$$
  $$\text{varga\_sign} = \begin{cases} (4 + \text{div\_idx}) \pmod{12}, & \text{if is\_odd} \\ (3 - \text{div\_idx}) \pmod{12}, & \text{if even \& } \text{d24\_mode}=\text{"reverse" (Kala default)} \\ (3 + \text{div\_idx}) \pmod{12}, & \text{if even \& } \text{d24\_mode}=\text{"direct"} \end{cases}$$
  $$\lambda_{\text{D24}} = (\text{varga\_sign} \times 30.0) + \left(\frac{\text{deg} \pmod{1.25}}{1.25} \times 30.0\right)$$
- **Rulership Model:** Zodiacal (`is_planetary_varga = False`).
- **Bhāva Engine:** Whole Sign Houses anchored to D24 Lagna.

---

### 12. D27 – Saptaviṁśāṁśa / Bhāṁśa (Subconscious Vitality)
- **Significance:** Physical stamina, general strength, subconscious vulnerabilities, and immune resilience.
- **Slice Geometry:** $27 \times 1^\circ06'40"$ ($1.111111^\circ$) per sign (324 divisions across the zodiac).
- **Scriptural Source:** *BPHS* 6.26–27 (Elemental progression: Fire $\to$ Aries $0$, Earth $\to$ Cancer $3$, Air $\to$ Libra $6$, Water $\to$ Capricorn $9$).
- **Algorithm:**
  $$\text{element} = \text{sign\_idx} \pmod 4$$
  $$\text{start\_sign} = (\text{element} \times 3) \pmod{12}$$
  $$\text{div\_idx} = \lfloor \text{deg} / (30.0 / 27.0) \rfloor \quad (\in \{0, \dots, 26\})$$
  $$\text{varga\_sign} = (\text{start\_sign} + \text{div\_idx}) \pmod{12}$$
  $$\lambda_{\text{D27}} = (\text{varga\_sign} \times 30.0) + \left(\frac{\text{deg} \pmod{30.0/27.0}}{30.0/27.0} \times 30.0\right)$$
- **Rulership Model:** Zodiacal (`is_planetary_varga = False`).
- **Bhāva Engine:** Whole Sign Houses anchored to D27 Lagna.

---

### 13. D30 – Triṁśāṁśa (The Unequal Planetary Bounds)
- **Significance:** Misfortunes, chronic diseases, karmic debts, and moral vulnerabilities.
- **Slice Geometry:** **5 Unequal Bounds** allotted exclusively to Mars, Saturn, Jupiter, Mercury, and Venus.
  - *Sun and Moon do not possess bounds; Cancer and Leo do not exist in classical Triṁśāṁśa.*
- **Scriptural Source:** *BPHS* 6.28–31; *Phaladīpikā* 3.7.
  - **In Odd Signs:**
    1. $0^\circ$–$5^\circ$ ($5^\circ$ span): **Mars** $\to$ Aries ($0$)
    2. $5^\circ$–$10^\circ$ ($5^\circ$ span): **Saturn** $\to$ Aquarius ($10$)
    3. $10^\circ$–$18^\circ$ ($8^\circ$ span): **Jupiter** $\to$ Sagittarius ($8$)
    4. $18^\circ$–$25^\circ$ ($7^\circ$ span): **Mercury** $\to$ Gemini ($2$)
    5. $25^\circ$–$30^\circ$ ($5^\circ$ span): **Venus** $\to$ Libra ($6$)
  - **In Even Signs:**
    1. $0^\circ$–$5^\circ$ ($5^\circ$ span): **Venus** $\to$ Taurus ($1$)
    2. $5^\circ$–$12^\circ$ ($7^\circ$ span): **Mercury** $\to$ Virgo ($5$)
    3. $12^\circ$–$20^\circ$ ($8^\circ$ span): **Jupiter** $\to$ Pisces ($11$)
    4. $20^\circ$–$25^\circ$ ($5^\circ$ span): **Saturn** $\to$ Capricorn ($9$)
    5. $25^\circ$–$30^\circ$ ($5^\circ$ span): **Mars** $\to$ Scorpio ($7$)
- **Algorithm:**
  $$\text{frac} = \frac{\text{deg} - \text{start}}{\text{span}}, \quad \text{scaled\_deg} = \text{frac} \times 30.0$$
  $$\lambda_{\text{D30}} = (\text{target\_sign\_idx} \times 30.0) + \text{scaled\_deg}$$
- **Rulership Model:** Planetary Bounds (`is_planetary_varga = True`).
  - `bound_ruler`: Governing planet (`"Mars"`, `"Saturn"`, `"Jupiter"`, `"Mercury"`, `"Venus"`).
  - `bound_symbol`: Glyphs (`"♂"`, `"♄"`, `"♃"`, `"☿"`, `"♀"`).
  - `display_entity = f"{bound_symbol} {bound_ruler}"`.
  - Computational `sign` preserves the assigned bound sign name for mathematical dignity calculations.
- **Bhāva Engine:** Whole Sign Houses anchored to the bound sign of the D30 Lagna.

---

### 14. D40 – Khavedāṁśa / Catvāriṁśāṁśa (Subtle Auspiciousness)
- **Significance:** Subtle karmic impressions, overall auspiciousness, and spiritual purity.
- **Slice Geometry:** $40 \times 0^\circ45'00"$ ($0.75^\circ$) per sign (480 divisions across the zodiac).
- **Scriptural Source:** *BPHS* 6.32–33 (Odd signs start at Aries $0$; even signs start at Libra $6$).
- **Algorithm:**
  $$\text{start\_sign} = 0 \text{ if is\_odd else } 6$$
  $$\text{div\_idx} = \lfloor \text{deg} / 0.75 \rfloor \quad (\in \{0, \dots, 39\})$$
  $$\text{varga\_sign} = (\text{start\_sign} + \text{div\_idx}) \pmod{12}$$
  $$\lambda_{\text{D40}} = (\text{varga\_sign} \times 30.0) + \left(\frac{\text{deg} \pmod{0.75}}{0.75} \times 30.0\right)$$
- **Rulership Model:** Zodiacal (`is_planetary_varga = False`).
- **Bhāva Engine:** Whole Sign Houses anchored to D40 Lagna.

---

### 15. D45 – Akṣavedāṁśa (Ethical Integrity & Character)
- **Significance:** Moral character, ethical disposition, and overall life conduct.
- **Slice Geometry:** $45 \times 0^\circ40'00"$ ($0.666667^\circ$) per sign (540 divisions across the zodiac).
- **Scriptural Source:** *BPHS* 6.34–35 (Modal progression: Movable $\to$ Aries $0$, Fixed $\to$ Leo $4$, Dual $\to$ Sagittarius $8$).
- **Algorithm:**
  $$\text{modality} = \text{sign\_idx} \pmod 3$$
  $$\text{start\_sign} = (\text{modality} \times 4) \pmod{12}$$
  $$\text{div\_idx} = \lfloor \text{deg} / (30.0 / 45.0) \rfloor \quad (\in \{0, \dots, 44\})$$
  $$\text{varga\_sign} = (\text{start\_sign} + \text{div\_idx}) \pmod{12}$$
  $$\lambda_{\text{D45}} = (\text{varga\_sign} \times 30.0) + \left(\frac{\text{deg} \pmod{30.0/45.0}}{30.0/45.0} \times 30.0\right)$$
- **Rulership Model:** Zodiacal (`is_planetary_varga = False`).
- **Bhāva Engine:** Whole Sign Houses anchored to D45 Lagna.

---

### 16. D60 – Ṣaṣṭiāṁśa (The Root of Cumulative Karma)
- **Significance:** The deepest root of *Prārabdha Karma* (destiny in action), minute life events, and spiritual sensitivity. Carries the highest weight in classical evaluation (4 points in Ṣoḍaśavarga; 5 points in Daśavarga).
- **Slice Geometry:** $60 \times 0^\circ30'00"$ ($0.5^\circ$ or $30'$) per sign (720 divisions across the zodiac).
- **Scriptural Source:** *Phaladīpikā* 3.5–6; *BPHS* 6.36–41.
  - Sign progression: Begins from base sign and runs through direct zodiac order.
  - 60 Classical Deities: Slices $1 \to 60$ in odd signs; reversed $60 \to 1$ in even signs.
  - **The 24 Malefic (*Aśubha*) Slices (*Phaladīpikā* 3.5):**
    In odd signs, slices **1, 2, 8, 9, 10, 11, 12, 15, 16, 30, 31, 32, 33, 34, 35, 39, 40, 42, 43, 44, 48, 51, 52, 59** are malefic. In even signs, the malefic assignment is inverted.
- **Algorithm:**
  $$\text{part\_idx} = \min(59, \lfloor \text{deg} / 0.5 \rfloor) \quad (\in \{0, \dots, 59\})$$
  $$\text{slice\_num} = \text{part\_idx} + 1 \quad (1\text{-indexed})$$
  $$\text{varga\_sign} = (\text{sign\_idx} + \text{part\_idx}) \pmod{12}$$
  $$\lambda_{\text{D60}} = (\text{varga\_sign} \times 30.0) + \left(\frac{\text{deg} \pmod{0.5}}{0.5} \times 30.0\right)$$
  $$\text{deity\_idx} = \text{part\_idx} \text{ if is\_odd else } (59 - \text{part\_idx})$$
  $$\text{deity\_num} = \text{deity\_idx} + 1$$
  $$\text{is\_malefic} = (\text{deity\_num} \in \text{SHASTIAMSA\_MALEFIC\_ODD})$$
  $$\text{is\_benefic} = \neg\text{is\_malefic}$$
- **Rulership Model:** Polarity/Deity Varga. Displays sign lord, glyph, deity name, deity number, and explicit nature flags (`nature = "Shubha / Benefic"` or `"Ashubha / Malefic"`).
- **Bhāva Engine:** Whole Sign Houses anchored to D60 Lagna.

---

## 5. The Six Operational Pipeline Rules

### Rule 1: D60 Malefic Catalog Integrity (*Phaladīpikā* 3.5)
In Mantreśvara’s *Phaladīpikā* (Ch. 3, Text 5), the malefic sixtieths in odd signs explicitly include **39** and **40**, and do **not** include **41**:
> *"The malefic sixtieths are the 1st, 2nd, 8th through 12th, 15th, 16th, 30th through 35th, **39th and 40th**, 42nd through 44th, 48th, 51st, 52nd, and 59th."*
- `SHASTIAMSA_MALEFIC_ODD` in `baseline_tables.py` retains index **39** and excludes index **41**.
- Slices evaluate `is_benefic`, `is_malefic`, and `nature` directly matching Mantreśvara's Sanskrit text.

### Rule 2: Horā (D2) Binary Engine
- In classical Parāśarī mode (`d2_mode = "parashari"`), D2 allocates bodies strictly to the Sun's domain (Leo) or Moon's domain (Cancer).
- D2 **never** constructs 12 dummy whole-sign houses with 10 empty signs. Its `bhavas` array constructs exactly two chambers:
  1. `Chamber 1` (Solar / Pingala, `☉`)
  2. `Chamber 2` (Lunar / Ida, `☽`)
  with `is_binary_varga = True`.

### Rule 3: Triṁśāṁśa (D30) Parāśarī Bound Protection
- In classical mode (`trimsamsa_mode = "parashari"`), `ChartPipeline` protects unequal Parāśarī bounds as primary coordinates.
- D30 is **never** overwritten with modulo harmonic coordinates (`(lon * 30.0) % 360.0`) unless `trimsamsa_mode == "harmonic"` is explicitly requested.

### Rule 4: Whole Sign House (*Rāśi Bhāva*) Scaffolding for Divisional Charts
- Intermediate 3D Campanus cusps from D1 are **never** multiplied modulo 360 to form house boundaries in divisional charts.
- For all zodiacal divisional charts (D4 through D60), houses are generated as **Whole Sign Houses** anchored to the divisional Ascendant (`v_dict["lagna"]["sign"]`).

### Rule 5: Dual-Layer Entity Decoupling (Computation vs. Display)
- To prevent downstream DAG calculators (e.g. Shadbala, Avasthas, Dignities) from crashing on sign lookups like `ZODIAC_SIGNS.index(sign)`:
  - **Computational Layer:** `sign`, `sign_index`, `longitude`, `degree_0_to_30` preserve standard valid zodiac coordinates.
  - **Display Layer:** `display_entity` and `display_symbol` supply clean astrological glyphs for non-zodiacal vargas (`"☉ Sun"` for D2, `"♂ Mars"` for D3, `"♃ Jupiter"` for D30).

### Rule 6: Absolute Removal of `exact_dignity`
- The non-classical `exact_dignity` module is completely excluded from the calculation DAG and serialization payloads.
- All planetary dignity calculations adhere strictly to classical *Panchadha Maitri* (5-fold temporal/natural friendship) and *Vimśopaka Bala*.
