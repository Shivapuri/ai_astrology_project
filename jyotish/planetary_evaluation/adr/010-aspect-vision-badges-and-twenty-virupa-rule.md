# ADR-010: Aspect Vision Badges, the 3-Tier Virūpa Filter, and Dignity Transmutation

## Context & The Shortcomings Identified
During master diagnostic chart reviews, usability and pedagogical shortcomings were identified in the environmental aspect analysis (Cell 6) and overall vitality summary (Cell 8):
1. **Aspect Clutter & Cognitive Overload:** In classical Jyotish, every planet casts some partial glance on every house/planet. Displaying all minor glancing angles in a flat text string cluttered the cell, burying the decisive planetary lines of sight that actually dominate character and manifestation.
2. **Missing Dignity Transmutation in Rays:** Aspect indicators treated malefic and benefic rays uniformly without communicating how the casting planet's *dignity* transforms the nature of its gaze. For example, an exalted Saturn gazing on a planet provides stabilizing boundary and mastery ("Strict Discipline"), whereas a fallen Saturn projects venom and breakdown ("Toxic Friction"). Similarly, a debilitated Jupiter projects overextended or dogmatic advice ("Compromised Support").
3. **Colloquial Terminology Disconnect:** Abstract UI labels like "Benefic Skylight" or "Challenging Pressure" obscured the classical Sanskrit concept of *Dṛṣṭi* (literally "vision" or "glance") and the scriptural distinction between *Śubha Dṛṣṭi (Supportive Vision)* and *Pāpa Dṛṣṭi (Confrontational Vision)*.
4. **Opaque Vitality Composition in Cell 8:** In Cell 8, vitality scores sat above the archetype badge without immediate visual reinforcement of the two foundational axes: Inherent Intent (*Dignity %*) and Raw Horsepower (*Shadbala %*).

## Decision
1. **The 3-Tier Visual Filter (Virūpa Strength / 60v = 100%):**
   - **Tier 1: < 20 Virūpas (Negligible):** Ignored entirely. Omitted from both the cell and the tooltip to eliminate noise.
   - **Tier 2: 20 to 44 Virūpas (Subtle Background):** Rendered **ONLY** inside the cell's interactive hover tooltip. Does not generate standalone badges in the table cell.
   - **Tier 3: >= 45 Virūpas (Decisive Force / 75%+):** Rendered directly in the main table cell as clean 2-line visual badges.
2. **Two-Line Dignity-Transmuted Synthesis Badges (for >= 45v):**
   - **Line 1 (The Fact):** Nature indicator (`🟢`/`🔴`) + Planet Name + Virūpas (`[X]v`).
     - Example: `🟢 Jupiter (45v)` or `🔴 Saturn (52v)`.
   - **Line 2 (The Qualitative Synthesis):** A 1-to-2 word summary indicating *how* the aspect acts based on the planet's dignity status:
     - *High Dignity Benefic (Exalted / Own):* `"Pure Grace"` or `"Strong Support"`
     - *Low Dignity Benefic (Debilitated / Enemy):* `"Compromised Support"` or `"Misguided Help"`
     - *High Dignity Malefic (Exalted / Own):* `"Strict Discipline"` or `"Constructive Pressure"`
     - *Low Dignity Malefic (Debilitated / Enemy):* `"Toxic Friction"` or `"Destructive Pressure"`
     - *Average Dignity:* `"Supportive Gaze"` (benefic) or `"Harsh Demand"` (malefic).
3. **Classical Vision (*Dṛṣṭi*) Terminology:**
   - Column 6 header is strictly **"Environmental Vision (Aspects/Yuti)"**.
   - Tooltips consistently use **"Śubha Dṛṣṭi (Supportive Vision)"** for benefics and **"Pāpa Dṛṣṭi (Confrontational Vision)"** for malefics.
   - Net totals display as `🟢 Net Śubha Dṛṣṭi (+Xv)`, `🔴 Net Pāpa Dṛṣṭi (-Xv)`, and `⚖️ Net Neutral`.
4. **Explicit Intent & Power Subcaption in Cell 8:**
   - Display `Intent: XX% | Power: YY%` directly beneath the net vitality score for all Grahas and the Lagna row, making the relationship between moral quality and physical muscle immediately intuitive.

## Proof & Validation
This architecture brings total visual clarity to chart diagnosis: astrologers immediately see the dominant psychological dialogues between planets at a glance, while retaining complete, unabridged mathematical receipts on hover.
