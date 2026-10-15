# Astrological Aspects (Drishti)

This document explains the mathematical rules and astrological logic for how aspects (Drishtis) are calculated in the Astra engine. The accompanying Python module is `aspects.py`.

## Overview
In Jyotish (Vedic Astrology), *Drishti* literally means "glance" or "sight." It is how planets and signs influence each other across the zodiac. Ernst Wilhelm's methodology, strictly based on Sage Parashara's teachings, separates aspects into two completely distinct categories: **Rasi Drishti** (Sign Aspects) and **Graha Drishti** (Planetary Aspects).

---

## 1. Rasi Drishti (Sign-to-Sign Aspects)

### Scriptural Citation
***Bṛhat Parāśara Horā Śāstra* (BPHS Ch. 8, v. 1–5 — *Rāśi-Dṛṣṭi-Kathanādhyāyaḥ*):**
> राशयोऽभिमुखं विप्र तथा पश्यन्ति पार्श्वभे ।  
> यथा चरः स्थिरानेवं स्थिरः पश्यति वै चरान् ॥ २॥  
> द्विस्वभावो विनाऽऽत्मानां द्विस्वभावान् प्रपश्यति ।  
> समीपस्थं परित्यज्य खेटास्तत्र गतास्तथा ॥ ३॥  
> 
> *"O Brahmin, the signs aspect each other frontally, except the adjacent sign. A Moveable (Cardinal) sign aspects all Fixed signs except the adjacent one; a Fixed sign aspects all Moveable signs except the adjacent one; and a Dual (Mutable) sign aspects all other Dual signs except itself. The planets situated in these signs also aspect similarly."*

### The Simple Explanation
Imagine the zodiac signs are rooms in a house. Some rooms have windows that look directly into other rooms. If a planet is sitting in one room, it can clearly see (and be seen by) anyone in the rooms connected by windows. 
- **Binary:** The window is either open or closed. You either aspect the sign 100%, or 0%. There is no halfway.
- **Mutual:** If you can see them, they can see you.

### The Technical Rules
The 12 signs are divided into three modalities: Moveable (Cardinal), Fixed, and Dual (Mutable). 

1. **Moveable Signs** (Aries, Cancer, Libra, Capricorn) aspect all **Fixed Signs**, *except* the one immediately adjacent to them.
   * *Example:* Aries (Moveable) aspects Leo, Scorpio, and Aquarius. It does *not* aspect Taurus because Taurus is right next door.
2. **Fixed Signs** (Taurus, Leo, Scorpio, Aquarius) aspect all **Moveable Signs**, *except* the one immediately adjacent to them.
   * *Example:* Taurus (Fixed) aspects Cancer, Libra, and Capricorn. It does *not* aspect Aries because Aries is right next door.
3. **Dual Signs** (Gemini, Virgo, Sagittarius, Pisces) aspect **all other Dual Signs**.

### How it is Used
Rasi Drishtis form the structural bedrock of the chart. They are used to detect *Yogas* (planetary combinations), determine long-term permanent influences, and calculate sign-based timing periods (like Jaimini Dashas).

---

## 2. Graha Drishti (Planetary Longitude Aspects)

### Scriptural Citations
- **BPHS Ch. 26, v. 1–13 (*Graha-Sphuṭa-Dṛṣṭi-Kathanādhyāyaḥ*):** Parāśara outlines the exact piecewise angular longitudinal aspect curve (*Dṛṣṭi Kendra*) and special planetary additions (*Viśeṣa Dṛṣṭi*).
- ***Phaladīpikā* Ch. 2, v. 23 & Ch. 4, v. 9:**
  > शौर्याज्ञे रविजो गुरुर्गुरुसुतौ भौमश्चतुर्थाष्टमौ  
  > पूर्णं पश्यति सप्तमं च सकलास्तेष्वंघ्रिवृद्ध्या क्रमात् ॥  
  > 
  > *"Saturn fully aspects the 3rd and 10th houses; Jupiter fully aspects the 5th and 9th houses; Mars fully aspects the 4th and 8th houses; all planets fully aspect the 7th house (opposition), while their aspects on other houses increase by quarters respectively."*

### Algebraic Equivalence of Continuous *Sphuṭa Dṛṣṭi* and Triangle-Wave Bonus
In `get_graha_drishti`, the triangle-wave special aspect bonus (`apply_special_bonus`) is the exact algebraic equivalent of Parāśara's continuous *Sphuṭa Dṛṣṭi* equations across **BPHS Ch. 26, v. 10–12**:
1. **Saturn (BPHS 26.10):** `एकभे नवभे भागा...` — Saturn's base aspect is augmented by a triangle wave peaking at 45.0 additional Virūpas at 60° (3rd glance) and 270° (10th glance), yielding exactly 60.0 Virūpas at those milestones.
2. **Mars (BPHS 26.11):** `त्रिसप्तभे तु भौमस्य... रूपं सदाऽङ्गभे` — Mars is augmented by 15.0 Virūpas peaking at 90° (4th glance) and 210° (8th glance), yielding 60.0 Virūpas at 90° and maintaining a full 1 *Rūpa* (60.0 Virūpas) continuously across the entire 180°–210° span (`सदाऽङ्गभे रूपं`).
3. **Jupiter (BPHS 26.12):** `त्रिसप्तभे तु जीवस्य...` — Jupiter is augmented by 30.0 Virūpas peaking at 120° (5th glance) and 240° (9th glance), yielding exactly 60.0 Virūpas at those milestones.

### The Simple Explanation
If Rasi Drishti is like rooms with windows, Graha Drishti is like a person shining a flashlight. The flashlight is brightest exactly where it is pointed, but the light gently fades the further away you get from the center of the beam. 
- **Continuous (Fractional):** The strength of the aspect is measured on a scale from 0 to 60 *Virupas* (points). 60 is a full, blinding aspect; 0 is no aspect at all.
- **Not Mutual:** Just because the Sun is shining its light on the Moon, does *not* mean the Moon is shining its light back on the Sun.
- **Degrees Matter:** It is calculated based on the exact mathematical degrees of the planets, not just the signs they occupy.

### The Technical Rules
By default, every planet "looks" directly across the sky (180 degrees) with full strength (60 Virupas). As you move away from 180 degrees, the strength of the glance fades mathematically per the Parāśarī piecewise function:
- $0^\circ \le \Delta \le 30^\circ$: $0.0$ Virūpas
- $30^\circ < \Delta \le 60^\circ$: $(\Delta - 30^\circ) / 2$
- $60^\circ < \Delta \le 90^\circ$: $(\Delta - 60^\circ) + 15$
- $90^\circ < \Delta \le 120^\circ$: $(120^\circ - \Delta) / 2 + 30$
- $120^\circ < \Delta \le 150^\circ$: $(150^\circ - \Delta)$
- $150^\circ < \Delta \le 180^\circ$: $(\Delta - 150^\circ) \times 2$
- $180^\circ < \Delta \le 300^\circ$: $(300^\circ - \Delta) / 2$
- $300^\circ < \Delta < 360^\circ$: $0.0$ Virūpas

*Note: In this strict system, the shadow nodes Rahu and Ketu do **not** cast Graha Drishti (they do not aspect other planets), but they **do receive** aspects from the classical planets and form conjunctions (Yutis) with planets sharing the same sign or within degree orb.*

### How it is Used
Graha Drishti reveals the psychological and qualitative influence planets have on one another. It is used heavily in *Shadbala* (the 6-fold strength calculation) and for timing events using planetary periods (like Vimshottari Dasha).

### Sphuṭa Dṛṣṭi Milestone Proximity Labeling (`get_aspect_explanation`)
`get_aspect_explanation` is a certified legacy bridge specifically retained for SVG ray rendering and visual chart readouts. To preserve pure degree-based continuous longitudinal glancing without sign or house binning distortion, aspect labels and classical rules are identified via angular proximity to exact Parāśarī milestones:
- **Opposition:** Peak at 180° ($\pm 15^\circ$ orb)
- **Mars Special 4th / Caturasra:** Peak at 90° ($\pm 30^\circ$ orb)
- **Mars Special 8th / Randhra:** Peak at 210° ($\pm 30^\circ$ orb)
- **Jupiter Special 5th / Trikona:** Peak at 120° ($\pm 30^\circ$ orb)
- **Jupiter Special 9th / Dharma:** Peak at 240° ($\pm 30^\circ$ orb)
- **Saturn Special 3rd / Upachaya:** Peak at 60° ($\pm 30^\circ$ orb)
- **Saturn Special 10th / Karma:** Peak at 270° ($\pm 30^\circ$ orb)
- **General Parāśarī Glance:** All other angles are labeled as continuous graduated Parāśarī glances.

#### Engine Contracts & Zero-State Rules
1. **Non-Casting Bodies Guard:** Non-physical points and shadow nodes (`Rahu`, `Ketu`, `Lagna`, `MC`) do not cast Graha Dṛṣṭi rays. Evaluated rays yield $0.0$ Virūpas with `line_style: "none"` and `nature_label: "Non-Casting Point"`.
2. **Zero-Virūpa Ray Neutrality:** Angular separations with $0.0$ Virūpas yield `line_style: "none"`, `nature_label: "No Aspect (0 Virūpas)"`, and `rule_name: "No Aspect / Blind Angle"`, preventing spurious malefic tension lines in frontend SVG charts.
92: 3. **Natural Benefic Ray Invariance (*BPHS* Ch. 27, v. 19 & 28–29):** Jupiter (`इज्य`), Mercury (`ज्ञ`), and Venus (`शुक्र`) unconditionally cast *Śubha* (benefic continuous) *Dṛṣṭi* rays (`ज्ञेज्यदृक्युक्तम्` / `ज्ञेज्यदृष्टियुतं`). Dignity affects their strength/manifestation, not their intrinsic benefic glance.
93: 4. **Mercury *Yuti* Affliction vs. *Dṛṣṭi* Invariance (*BPHS* Ch. 3, v. 11 vs. Ch. 27, v. 19 & 29):**
94:    > तत्रार्कशनिभूपुत्राः क्षीणेन्दुराहुकेतवः । क्रूराः शेषग्रहा सौम्याः क्रूरः क्रूरयुतो बुधः ॥ ११॥ (*BPHS* 3.11)  
95:    > पापदृक्पादहीनं तच्छुभदृक्पादयुक् तथा । बलैक्यं ज्ञेज्यदृक्युक्तमेवं खेटबलं भवेत् ॥ १९॥ (*BPHS* 27.19)  
96:    > सद्दृष्टिपादयुक्पापपापदृष्टिपादविवर्जितम् । ज्ञेज्यदृष्टियुतं तच्च स्वस्वस्वामिबलान्वितम् ॥ २८–२९॥ (*BPHS* 27.28–29)  
97:    
98:    In Parāśarī Jyotish, Mercury becomes functionally malefic **only by conjunction/co-presence (*क्रूरयुतो बुधः* / *सपापश्च वित्*)** when combust or occupying the same sign as an active malefic (`Sun`, `Mars`, `Saturn`, `Rahu`, `Ketu`, or dark/waning `Moon` [`क्षीणेन्दु`]). Its **distant aspect ray (*Dṛṣṭi*)** remains unconditionally benefic (*Śubha*) in both planetary aspects (*BPHS* 27.19) and house aspects (*BPHS* 27.28–29). Across both scopes, Parāśara pairs Mercury (`ज्ञ`) with Jupiter (`इज्य`) as casting an unconditionally benefic ray. (An optional toggle `mercury_drishti_always_benefic=False` is provided for *Śrīpati* conditional aspect mode).
99: 
100: ---
101: 
102: ## 3. Stage 2A Master Aspect Orchestrator (`calculate_aspect_matrices`)
103: The master function `calculate_aspect_matrices(baseline: ChartBaseline, enforce_dpk_lord_qualifications: bool = False, mercury_drishti_always_benefic: bool = True) -> Dict[str, Any]` connects `ChartBaseline` directly to the aspect engine in a single pass:
104: 
105: 1. **Graha Dṛṣṭi — Planet-to-Planet ($11 \times 11$ Matrix):**
106:    - Evaluates Graha Dṛṣṭi (0–60 Virūpas) between all 11 bodies in `ALL_BODIES` using the precomputed angular distances in `baseline.separation_matrix`.
107:    - Rahu, Ketu, Lagna, and MC cast 0 Virūpas, but receive incoming aspects from the 7 physical planets.
108:    - Dual-indexed for $O(1)$ lookups without matrix transpositions:
109:      - `graha_drishti["outgoing"][aspecting][aspected]`: Virūpas cast (used for planetary expression & yoga detection).
110:      - `graha_drishti["incoming"][aspected][aspecting]`: Virūpas received (used for Dṛk Bala in Shadbala).
111: 
112: 2. **Graha Dṛṣṭi — Planet-to-Cusp ($7 \times 12$ Matrix):**
113:    - Evaluates Graha Dṛṣṭi cast by the 7 physical planets onto the 12 Whole-Sign sensitive cusps ($D_{\text{asc}}$ projected from the natal Ascendant's sign):
114:      $$\text{Target Sign Index}_h = (\text{asc\_sign\_idx} + h - 1) \pmod{12}$$
115:      $$\text{Cusp Longitude}_h = (\text{Target Sign Index}_h \times 30^\circ + \text{sensitive\_cusp\_degree}) \pmod{360^\circ}$$
116:    - Dual-indexed:
117:      - `cusp_drishti["by_planet"][planet][house_num]`: Virūpas cast on house $h$.
118:      - `cusp_drishti["by_house"][house_num][planet]`: Virūpas received by house $h$.
119: 
120: 3. **Rāśi Dṛṣṭi (Sign & Planetary Mutual Glances):**
121:    - Sign aspects: Moveable aspects Fixed (except adjacent); Fixed aspects Moveable (except adjacent); Dual aspects Dual.
122:    - Binary mutual glance between bodies and whole-sign houses:
123:      - `rasi_drishti["planet_to_planet"][p1]`: List of planets aspected by $p1$.
124:      - `rasi_drishti["house_to_planets"][h]`: List of planets aspecting whole-sign house $h$ (used for House Atmosphere scoring).
125: 
126: 4. **Benefic / Malefic Qualitative Totals (+ / - Net Virūpas):**
127:    - **Natural Benefics:** Jupiter, Venus.
128:    - **Dynamic Benefics:**
129:      - **Mercury:**
130:        - **Dṛṣṭi Rays (`benefic_malefic_totals["classification"]`):** Benefic (`True`) by default per *BPHS* Ch. 27, v. 19 & 28–29 (`ज्ञेज्यदृक्युक्तम्` / `ज्ञेज्यदृष्टियुतं`). If `mercury_drishti_always_benefic=False`, follows conditional Yuti status.
131:        - **Yuti / Co-presence (`benefic_malefic_totals["yuti_classification"]`):** Conditionally malefic (`False`) if combust (`baseline.combustion_status["Mercury"]["is_combust"]` is True) or conjoined in the same sign with any active malefic (`Sun`, `Mars`, `Saturn`, `Rahu`, `Ketu`, or dark/waning `Moon` [`क्षीणेन्दु`]) per *BPHS* Ch. 3, v. 11 and *Phaladīpikā* Ch. 2, v. 27.
132:      - **Moon:** Benefic if bright/waxing (`baseline.lunar_phase["is_benefic"]` is True, corresponding to Paksha Bala $\ge 30$ Virūpas / elongation $\ge 90^\circ$).
133:    - **Natural Malefics:** Sun, Mars, Saturn, Rahu, Ketu.
134:    - **House Lord Protection Rule (*Phaladīpikā* Ch. 15, v. 1–3):**
135:      > पापाः सर्वे भवनपतयश्चेदिहाहुस्तथैव खेटैः सर्वैः शुभफलमिदं नीचमूढारिहीनैः ॥ १॥  
136:      > *"Even if the lords of the houses be malefics, they produce auspicious results for their own houses, provided they are free from debilitation (`नीच`), combustion (`मूढ`), and enemy sign (`अरि`)."*
137:      - **Unattenuated Envelope (`totals_cusps`):** By default, when scoring aspects striking whole-sign house cusps, a house lord's aspect on its own sign is classified as positive/protective, preserving and defending the house regardless of whether that ruler is a natural malefic (such as Mars or Saturn).
138:      - **Qualified Envelope (`cusps_dpk_qualified`):** When `enforce_dpk_lord_qualifications=True` (or inspected via `benefic_malefic_totals["cusps_dpk_qualified"]`), a natural malefic house lord receives positive protection credit only if it is free from debilitation, combustion, and enemy sign (*Nīca-Mūḍha-Ari-Hīnaiḥ*).
139:    - Net balance: $\text{Net Virūpas} = \text{Benefic Virūpas} - \text{Malefic Virūpas}$ precomputed for all planets and all 12 house cusps.

---

## 4. Multi-Varga Aspect Adapter (`calculate_varga_aspects`)
`calculate_varga_aspects(baseline, varga="D1") -> Dict[str, Any]` provides a clean, unified adapter that consumes `baseline.vargas[varga]` directly without requiring callers to unpack longitude lists, cusps, and ascendant coordinates.

In the helper `calculate_advanced_graha_aspects`, Yutis are harmonized with degree proximity (`CONJUNCTION_MAX_ORB = 10.0°`) and cross-border boundaries (`CROSS_BORDER_ATTENUATION = 0.75`) while retaining same-sign conjunction recognition. Conjunctions are bidirectional between all planets and shadow nodes (Rāhu and Ketu), excluding only mathematical sensitive points (`Lagna`, `MC`). The function returns a backwards-compatible list of strings by default, or an enriched dictionary format when requested (`yuti_format='dict'` or `as_dict=True`), with structured conjunction metadata always available under `results['yuti_details']`.

---

## 5. Downstream Pipeline Contract (Stage 2A $\rightarrow$ Stage 3 `bhava_bala.py`)
In `calculate_aspect_matrices`, `totals_cusps` calculates the qualitative balance by summing raw Virūpa values directly ($1.0 \times \text{Ray}$), representing the **unattenuated qualitative envelope**.

When Stage 3 (`bhava_bala.py`) calculates canonical **Bhāva Dṛṣṭi Bala** under Maharishi Parāśara (*BPHS* Ch. 27, v. 28–29: `सद्दृष्टिपादयुक्पापपापदृष्टिपादविवर्जितम् । ज्ञेज्यदृष्टियुतं तच्च`) and Mantreśvara (*Phaladīpikā* Ch. 15, v. 1–3), it consumes `cusp_drishti["by_house"][h][p]` and applies scriptural fractional multipliers:
- **Jupiter and Mercury (`ज्ञेज्यदृष्टियुतं`):** Always positive full benefic ray ($\times +1.0$ in pure Parāśarī / `sripati_raman` mode; scaled to $\times +0.5$ in `dpk_qualified` mode if combust, debilitated, or in an enemy sign per *Phaladīpikā* 15.1 & 15.3—never $\times -0.25$).
- **Venus and Bright/Waxing Moon (`सद्दृष्टिपादयुक्`):** Quarter positive value ($\times +0.25$).
- **Natural Malefics (Sun, Mars, Saturn) and Dark/Waning Moon (`पापदृष्टिपादविवर्जितम्`):** Negative quarter value ($\times -0.25$).
- **House Lord on its own house cusp (*Phaladīpikā* Ch. 15, v. 1–3):** In `dpk_qualified` mode, full positive value ($\times +1.0$ when free from debilitation, combustion, and enemy sign per `नीचमूढारिहीनैः`, or $\times +0.25$ if impaired), defending its own house even if a natural malefic.
