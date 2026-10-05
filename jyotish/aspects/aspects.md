# Astrological Aspects (Drishti)

This document explains the mathematical rules and astrological logic for how aspects (Drishtis) are calculated in the Astra engine. The accompanying Python module is `aspects.py`.

## Overview
In Jyotish (Vedic Astrology), *Drishti* literally means "glance" or "sight." It is how planets and signs influence each other across the zodiac. Ernst Wilhelm's methodology, strictly based on Sage Parashara's teachings, separates aspects into two completely distinct categories: **Rasi Drishti** (Sign Aspects) and **Graha Drishti** (Planetary Aspects).

---

## 1. Rasi Drishti (Sign-to-Sign Aspects)

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

### The Simple Explanation
If Rasi Drishti is like rooms with windows, Graha Drishti is like a person shining a flashlight. The flashlight is brightest exactly where it is pointed, but the light gently fades the further away you get from the center of the beam. 
- **Continuous (Fractional):** The strength of the aspect is measured on a scale from 0 to 60 *Virupas* (points). 60 is a full, blinding aspect; 0 is no aspect at all.
- **Not Mutual:** Just because the Sun is shining its light on the Moon, does *not* mean the Moon is shining its light back on the Sun.
- **Degrees Matter:** It is calculated based on the exact mathematical degrees of the planets, not just the signs they occupy.

### The Technical Rules
By default, every planet "looks" directly across the sky (180 degrees) with full strength (60 Virupas). As you move away from 180 degrees, the strength of the glance fades mathematically. 
*Note: In this strict system, the shadow nodes Rahu and Ketu do **not** cast Graha Drishti (they do not aspect other planets), but they **do receive** aspects from the classical planets and form conjunctions (Yutis) with planets sharing the same sign.*

**Special Planetary Glances:**
Three planets have "special" glances that are added on top of the base calculation:
1. **Mars (Kuja):** As the warrior, Mars is highly protective of its inner territory (4th house / ~90°) and highly alert to external threats (8th house / ~210°). It gets a massive strength boost at these angles.
2. **Jupiter (Guru):** As the wise counselor, Jupiter looks upon the houses of future creativity (5th / ~120°) and higher purpose (9th / ~240°) with supreme grace. It gets a strength boost here.
3. **Saturn (Shani):** As the stern worker, Saturn keeps a watchful eye on its immediate efforts (3rd / ~60°) and its heavy burdens/career (10th / ~270°). It gets a strength boost at these angles.

### How it is Used
Graha Drishti reveals the psychological and qualitative influence planets have on one another. It is used heavily in *Shadbala* (the 6-fold strength calculation) and for timing events using planetary periods (like Vimshottari Dasha).

### Sphuṭa Dṛṣṭi Milestone Proximity Labeling (`get_aspect_explanation`)
To preserve pure degree-based continuous longitudinal glancing without sign or house binning distortion, aspect labels and classical rules are identified via angular proximity to exact Parāśarī milestones rather than integer sign/house bins:
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
3. **Natural Benefic Ray Invariance (*BPHS* Ch. 3.21):** Jupiter and Venus unconditionally cast Śubha (benefic continuous) rays. Dignity affects their strength/manifestation, not their intrinsic benefic glance.
4. **Mercury Malefic Affliction (*BPHS* Ch. 3.21 / *Phaladīpikā* Ch. 2.27):** The Sun is an inherent natural malefic (*Krūra*). Mercury conjoined with the Sun (even outside combustion orb) or with Mars, Saturn, Rahu, or Ketu becomes functionally malefic.

---

## 3. Stage 2A Master Aspect Orchestrator (`calculate_aspect_matrices`)
The master function `calculate_aspect_matrices(baseline: ChartBaseline) -> Dict[str, Any]` connects `ChartBaseline` directly to the aspect engine in a single pass:

1. **Graha Dṛṣṭi — Planet-to-Planet ($11 \times 11$ Matrix):**
   - Evaluates Graha Dṛṣṭi (0–60 Virūpas) between all 11 bodies in `ALL_BODIES` using the precomputed angular distances in `baseline.separation_matrix`.
   - Rahu, Ketu, Lagna, and MC cast 0 Virūpas, but receive incoming aspects from the 7 physical planets.
   - Dual-indexed for $O(1)$ lookups without matrix transpositions:
     - `graha_drishti["outgoing"][aspecting][aspected]`: Virūpas cast (used for planetary expression & yoga detection).
     - `graha_drishti["incoming"][aspected][aspecting]`: Virūpas received (used for Dṛk Bala in Shadbala).

2. **Graha Dṛṣṭi — Planet-to-Cusp ($7 \times 12$ Matrix):**
   - Evaluates Graha Dṛṣṭi cast by the 7 physical planets onto the 12 Whole-Sign sensitive cusps ($D_{\text{asc}}$ projected from the natal Ascendant's sign):
     $$\text{Target Sign Index}_h = (\text{asc\_sign\_idx} + h - 1) \pmod{12}$$
     $$\text{Cusp Longitude}_h = (\text{Target Sign Index}_h \times 30^\circ + \text{sensitive\_cusp\_degree}) \pmod{360^\circ}$$
   - Dual-indexed:
     - `cusp_drishti["by_planet"][planet][house_num]`: Virūpas cast on house $h$.
     - `cusp_drishti["by_house"][house_num][planet]`: Virūpas received by house $h$.

3. **Rāśi Dṛṣṭi (Sign & Planetary Mutual Glances):**
   - Sign aspects: Moveable aspects Fixed (except adjacent); Fixed aspects Moveable (except adjacent); Dual aspects Dual.
   - Binary mutual glance between bodies and whole-sign houses:
     - `rasi_drishti["planet_to_planet"][p1]`: List of planets aspected by $p1$.
     - `rasi_drishti["house_to_planets"][h]`: List of planets aspecting whole-sign house $h$ (used for House Atmosphere scoring).

4. **Benefic / Malefic Qualitative Totals (+ / - Net Virūpas):**
   - **Natural Benefics:** Jupiter, Venus.
   - **Dynamic Benefics:**
     - Mercury: Benefic if not combust (`baseline.combustion_status["Mercury"]["is_combust"]` is False) and not conjoined in the same sign with natural malefics (*BPHS* Ch. 3 / *Phaladeepika* Ch. 2.27).
     - Moon: Benefic if bright/waxing (`baseline.lunar_phase["is_benefic"]` is True).
   - **Natural Malefics:** Sun, Mars, Saturn, Rahu, Ketu.
   - **House Lord Protection Rule (*Phaladeepika* Ch. 15.1–3):** When scoring aspects striking whole-sign house cusps, a house lord's aspect on its own sign is always classified as positive/protective, preserving and defending the house regardless of whether that ruler is a natural malefic (such as Mars or Saturn).
   - Net balance: $\text{Net Virūpas} = \text{Benefic Virūpas} - \text{Malefic Virūpas}$ precomputed for all planets and all 12 house cusps.


---

## 4. Multi-Varga Aspect Adapter (`calculate_varga_aspects`)
`calculate_varga_aspects(baseline, varga="D1") -> Dict[str, Any]` provides a clean, unified adapter that consumes `baseline.vargas[varga]` directly without requiring callers to unpack longitude lists, cusps, and ascendant coordinates.

In the legacy helper `calculate_advanced_graha_aspects`, Yutis (same-sign conjunctions) are bidirectional between all planets and shadow nodes (Rāhu and Ketu), excluding only mathematical sensitive points (`Lagna`, `MC`).

---

## 5. Downstream Pipeline Contract (Stage 2A $\rightarrow$ Stage 3)
In `calculate_aspect_matrices`, `totals_cusps` calculates the qualitative balance by summing raw Virūpa values directly ($1.0 \times \text{Ray}$), representing the **unattenuated qualitative envelope**.

When Stage 3 (`bhava_bala.py`) calculates canonical **Bhāva Dṛṣṭi Bala** under Maharishi Parāśara (*BPHS* Ch. 27), it consumes `cusp_drishti["by_house"][h][p]` and applies scriptural fractional multipliers:
- **Jupiter and Benefic Mercury:** Full positive value ($\times +1.0$, scaled to $/2.0$ if combust or debilitated).
- **Venus and Bright Moon:** Quarter positive value ($\times +0.25$).
- **Natural Malefics (Sun, Mars, Saturn, Dark Moon, Afflicted Mercury):** Negative quarter value ($\times -0.25$).
- **House Lord on its own house cusp (*Phaladīpikā* Ch. 15.1–3):** Full positive value ($\times +1.0$, reduced to $+0.25$ if combust or debilitated), defending its own house even if a natural malefic.


