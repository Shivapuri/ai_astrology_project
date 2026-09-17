# ADR-010: Aspect Vision Badges, the 20-Virūpa Threshold, and Dignity Transmutation

## Context & The Shortcomings Identified
During master diagnostic chart reviews, four usability and pedagogical shortcomings were identified in the environmental aspect analysis (Cell 6) and overall vitality summary (Cell 8):
1. **Aspect Clutter & Cognitive Overload:** In classical Jyotish, every planet casts some partial glance on every house/planet. Displaying all tiny glancing angles (e.g., 2v to 15v) in a flat text string cluttered the cell, burying the dominant planetary lines of sight that actually shape character.
2. **Missing Dignity Transmutation in Rays:** Aspect indicators treated malefic and benefic rays uniformly without communicating how the casting planet's *dignity* transforms the nature of its gaze. For example, an exalted Saturn gazing on a planet provides stabilizing boundary and mastery ("Strict Discipline"), whereas a fallen Saturn projects frustration and venom ("Toxic Pressure"). Similarly, a debilitated Jupiter projects overextended or compromised advice ("Compromised Support").
3. **Colloquial Terminology Disconnect:** Terminology like "Sky-Light" and generic aspect labels obscured the classical Sanskrit concept of *Dṛṣṭi* (literally "vision" or "glance") and the scriptural distinction between *Śubha Dṛṣṭi* (benefic vision) and *Pāpa Dṛṣṭi* (malefic vision).
4. **Opaque Vitality Composition in Cell 8:** In Cell 8, vitality scores sat above the archetype badge without immediate visual reinforcement of the two foundational axes: Inherent Intent (*Dignity %*) and Raw Horsepower (*Shadbala %*).

## Decision
1. **The 20-Virūpa Threshold Filter:**
   - Divide all incoming Dṛṣṭi into two distinct categories:
     - **Primary Aspects ($\ge 20$ Virūpas / $\ge 33.3\%$ strength):** Rendered as prominent, color-coded 2-line visual badges.
     - **Background Glances ($< 20$ Virūpas):** Collapsed into a clean summary note (e.g., `+ 3 background glances (<20v)`), with full mathematical ray details preserved inside the interactive hover tooltip. No astronomical data is lost.
2. **Two-Line Dignity-Transmuted Synthesis Badges:**
   - **Line 1 (Astronomy & Strength):** Nature indicator (`🟢`/`🔴`) + Planet name + Glyph + Dignity icon (`👑`/`🏰`/`🤝`/`⚖️`/`⚔️`/`🥀`) + Strength in Virūpas (`XXv`).
   - **Line 2 (Psychological Manifestation):** Clear qualitative synthesis reflecting the planet's dignity:
     - *Benefic + High Dignity:* `Pure Grace (Fortified)`
     - *Benefic + Friendly/Neutral:* `Strong Support (Friendly)`
     - *Benefic + Debilitated/Distorted:* `Compromised Support (Debilitated)`
     - *Benefic + Enemy Sign:* `Misguided Help (Enemy Sign)`
     - *Malefic + High Dignity:* `Strict Discipline (Exalted / Own)`
     - *Malefic + Friendly/Neutral:* `Constructive Pressure (Tempered)`
     - *Malefic + Debilitated:* `Toxic Pressure (Debilitated)`
     - *Malefic + Enemy Sign:* `Destructive Friction (Enemy Sign)`
3. **Classical Vision (*Dṛṣṭi*) Terminology:**
   - Rebrand Column 6 header to **Environmental Vision (Aspects/Yuti)**.
   - Update vitality receipts and tooltips to **Aspect Vision (Dṛṣṭi)** and categorize net aspect totals as *Śubha Dṛṣṭi* (benefic vision) or *Pāpa Dṛṣṭi* (malefic vision).
4. **Explicit Intent & Power Subcaption in Cell 8:**
   - Display `Intent: XX% | Power: YY%` directly beneath the net vitality score for all Grahas and the Lagna row, making the relationship between moral quality and physical muscle immediately intuitive.

## Proof & Validation
This architecture brings total visual clarity to chart diagnosis: astrologers immediately see the dominant psychological dialogues between planets at a glance, while retaining complete, unabridged mathematical receipts on hover.
