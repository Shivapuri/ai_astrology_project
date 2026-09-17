# Master Graha Diagnostics - Audit & Evaluation

## Goal Description
The objective of this document is to audit the Master Graha Diagnostics table and its underlying engine in the Astra codebase. The focus is on identifying where astrological factors are "metered twice" (double counting) and highlighting architectural and UI/UX improvements to make the frontend more transparent and easier to read without losing any fine-grained details.

*Note: The system utilizes a 9-tier expanded evaluation matrix, intentionally designed to provide a finer-grained resolution than Vic DiCara's original 4-Quadrant Matrix.*

## Deep Evaluation & Audit Findings

### 1. The "Metered Twice" Problem (Double & Triple Counting)
The current `calculate_graha_vitality` function applies multiple overlapping additive modifiers (`mot_mod`, `drishti_mod`, `conj_mod`, `psy_mod`) to reach a final "Vitality Score". This results in several factors being double-counted:

- **Retrograde Motion:** A `mot_mod` of `+0.3` is added for retrograde planets. *However*, retrograde planets already receive maximum **Cheshta Bala** (Motional Strength) natively within the core Shadbala calculation. This meters retrograde motion twice.
- **Aspects (Drishti):** `drishti_mod` and `conj_mod` modify the score based on benefic/malefic rays and conjunctions. *However*, **Drik Bala** (Aspectual Strength) within Shadbala already mathematically accounts for planetary aspects.
- **Lajjitadi Avasthas:** `psy_mod` adds or subtracts points based on psychological states (e.g., Kshudhita, Mudita). *However*, Lajjitadi states are derived purely from aspects, conjunctions, and dispositors. Applying them as an additive score modifier while also having `drishti_mod` and `conj_mod` means aspects and conjunctions are metered for a third time.

### 2. Edge Cases: Neecha Bhanga & Planetary War
- **Transmuted Hero (Neecha Bhanga):** The engine forces rescued planets into a 10th archetype tier. Neecha Bhanga should strictly act as an alchemical multiplier to the *Dignity* percentage, naturally elevating the planet's standing based on its host's strength.
- **Graha Yuddha (Planetary War):** Venus Invariance is correctly applied, but the war modifier (`war_mod`) is applied flatly to the vitality score. It should remain a descriptive badge or integrate cleanly into the Shadbala/Dignity evaluation rather than acting as an arbitrary mathematical additive.

### 3. Frontend vs. Backend Logic Duplication
- **The Issue:** The entire diagnostic logic is calculated in Python (`jyotish/planetary_evaluation/planetary_evaluation.py`), but then `updateMasterDiagnosticWidget` in `templates/index.html` (lines 5880-6000) completely re-calculates the 9 tiers, net vitality, and modifiers in JavaScript.
- **The Solution:** The JavaScript frontend should be streamlined to act purely as a rendering layer that consumes the JSON output from the Python backend. This will ensure a single source of truth for the mathematics and significantly reduce UI overhead.

---

## Frontend UI & Transparency Enhancements

To make the table easier to read and mathematically transparent (so the user always knows what "6.3 of 10 stars" actually means), we will implement the following UI/UX upgrades:

### A. Demystifying the "Vitality Score" (The Math Breakdown)
Currently, a score like `★ 6.3 / 10` is a "black box." We need to expose the math cleanly without cluttering the main view.
- **Visual Hierarchy in the Cell:**
  - **Primary:** `★ 6.3 / 10` (Large, bold text)
  - **Secondary:** `Intent: 65% | Power: 95%` (Small, muted text beneath the score)
- **Mathematical Tooltip (Hover State):**
  When hovering over the score, the tooltip will display a clean, step-by-step receipt of how the score was calculated:
  ```text
  🧮 VITALITY SCORE CALCULATION
  ------------------------------------
  Base Engine:      5.0 (Default)
  Quality (Dignity): +1.5 (65% Noble)
  Muscle (Shadbala): -0.2 (95% Avg)
  Host Rescue:      +0.0 (No lift)
  ------------------------------------
  Final Actualized: ★ 6.3 / 10
  ```

### B. Clarifying Column Headers & Aspect Terminology
The current terminology in the frontend uses terms like "Benefic Skylight" and "Challenging Pressure" to describe aspects. As seen in **Vic DiCara's Lesson 05** (Authentic Vedic Aspects), an aspect (*Drishti*) is fundamentally about **line-of-sight vision or gaze**. A planet "looks" at another house or planet and influences its behavior. Ryan Kurczak similarly teaches aspects as **supportive or antagonistic influences** (friendly vs. enemy aspects).

To align with this foundation, we will replace overly abstract terms with clear, intuitive Vedic/English pairings:
- **"Benefic Skylight"** ➔ **"Śubha Dṛṣṭi (Supportive Vision / Gaze)"**: A helpful, nurturing, or expansive line of sight (e.g., Jupiter's trine gaze).
- **"Challenging Pressure"** ➔ **"Pāpa Dṛṣṭi (Confrontational Vision / Gaze)"**: A demanding, intense, or critical line of sight (e.g., Saturn or Mars's gaze).

We will also rename the table headers to explain *what* the column measures in plain English:
- **"Dignity"** ➔ **"Intent & Quality (Dignity)"**
- **"Power"** ➔ **"Kinetic Muscle (Shadbala)"**
- **"Influences"** ➔ **"Environmental Vision (Aspects/Yuti)"**
- **"Functional Archetype"** ➔ **"Final Archetype & Vitality"**

### C. The 9-Tier Archetype Clarity
To ensure the 9-tier system is instantly understandable, the cell will explicitly pair the Archetype name with its structural coordinates.
- Instead of just showing the badge: `🛡️ The Noble Guardian`, we display:
  - **Badge:** `🛡️ The Noble Guardian`
  - **Subtext:** `High Quality + Balanced Muscle`

### D. Highlight "Master Lords" for Quick Scanning
In a complex table, it's hard to know which rows matter most. We will apply a subtle highlight or a distinct "Crown" icon `👑` next to the planets that are the **Three Master Lords of Destiny** (e.g., Lagna Lord, Navamsha Lord). This guides the eye immediately to the most important metrics.

### E. Consolidation of Avasthas and Badges
Currently, Lajjitadi Avasthas, Planetary War badges, and Combustion badges are scattered. We will group all "Affliction/Blessing" badges into a unified, color-coded tag system inside the "Environmental Friction" column. This keeps the final "Vitality" column clean, containing strictly the Score, the Tier, and the Archetype.

### F. Clear Aspect (Dṛṣṭi) Badges (The "> 20 Virūpa" Rule)
To make the Environmental Vision column instantly readable without being overwhelmed by data, we will implement a clean UI badge system for aspects. 
1. **Filtering:** We will only display aspects that carry real weight (e.g., **> 20 Virūpas**) directly in the table cell. Weaker background aspects (< 20v) will be hidden inside the hover tooltip to prevent clutter.
2. **Visual Structure:** Each significant aspect will be rendered as a compact, two-line badge in the cell:
   - **Line 1 (The Fact):** Natural Nature Icon (🟢/🔴) + Planet Name + Strength (Virūpas).
   - **Line 2 (The Synthesis):** A 1-2 word summarization of the *quality* of the gaze, derived by combining its natural benefic/malefic nature with its Dignity.

**Example Cell Rendering:**
```html
🟢 Jupiter (45v)
↳ Compromised Support (Debilitated)

🔴 Saturn (35v)
↳ Strict Discipline (Exalted)

🔴 Mars (25v)
↳ Toxic Pressure (Enemy Sign)
```

**The Logic for the "Summarization" Text:**
*   **High Dignity Benefic** (Exalted/Own): "Pure Grace" or "Strong Support"
*   **Low Dignity Benefic** (Debilitated): "Compromised Support" or "Misguided Help" (Because a debilitated Jupiter wants to help, but gives bad advice).
*   **High Dignity Malefic** (Exalted/Own): "Strict Discipline" or "Constructive Pressure" (Because an exalted Saturn is harsh, but fair and structural).
*   **Low Dignity Malefic** (Debilitated): "Toxic Pressure" or "Destructive Friction" (Because a debilitated Mars is just lashing out).

---

### G. Integrating Nakshatra Diagnostics (The "Overlord" Agenda)
Now that Nakshatra calculations (and the vast repository of vault knowledge) are available, we must integrate this critical layer into the Master Graha Diagnostics table. A planet's Rasi (Sign) shows *where* it is acting, but its Nakshatra shows its **subconscious motivation** and *who* it is secretly working for (the Nakshatra Lord).

To visualize this without cluttering the UI, we will add a new column immediately following the "Environmental Vision (Aspects/Yuti)" column. 

**New Column Header:** **"Subconscious Drive (Nakshatra)"**

**Visual Structure inside the Cell:**
We will use a clean, 2-line structure to instantly convey the Nakshatra's identity and its planetary Overlord.

*   **Line 1 (The Star & Deity):** The Nakshatra name and its presiding Deity (which defines the core psychological energy, per Vic DiCara).
*   **Line 2 (The Planetary Overlord):** The planetary ruler of the Nakshatra (which dictates the planet's agenda and Vimshottari timeline, per Ryan Kurczak).

**Example Cell Rendering:**
```html
✨ Chitra (Tvashtar)
↳ Overlord: Mars

✨ Pushya (Brihaspati)
↳ Overlord: Saturn

✨ Jyeshtha (Indra)
↳ Overlord: Mercury
```

**Hover Tooltip (The Deep Dive):**
When the user hovers over this cell, the tooltip will pull a brief synthesis from the knowledge vault:
```text
✨ CHITRA NAKSHATRA
------------------------------------
• Deity: Tvashtar (The Divine Architect)
• Overlord: Mars (Drives the Vimshottari agenda)
• Nature: Mridu (Soft / Creative)
• Core Drive: Intellectual design, craftsmanship, and fascinating aesthetic brilliance.
```

This ensures the user instantly sees who the "Overlord" is at a glance, while keeping the deep astrological meaning hidden safely within the tooltip.

---

## Implementation Roadmap

1. **Remove Double-Metering in Python:** Clean up `calculate_graha_vitality` by removing redundant modifiers (`mot_mod`, `drishti_mod`, `psy_mod`). Let aspects and avasthas organically affect Dignity and Shadbala without stacking additives.
2. **Expose Calculation Trail:** Update the Python backend to return an `equation_parts` array or dictionary so the frontend can easily render the math breakdown tooltip.
3. **Refactor JS Frontend:** Update `templates/index.html` to consume `peData.planets[graha]`, deleting the duplicated JS logic.
4. **Implement UI Enhancements:** Apply the visual hierarchy, renamed headers, step-by-step tooltips, and Master Lord highlights to the frontend table.
