# Sequential Planetary Interpretation & Macro Canvas Synthesis Engine

## Overview & Architecture
The Interpretation Engine implements the final two stages of Astra's chart assessment methodology:
1. **Macrocosmic Background Canvas Synthesis**:
   Synthesizes the two foundational molecules into a 4-string baseline personality canvas:
   - **Molecule 1**: Ascendant Nakshatra (*Ahaṁkāra* / Bodily Action) ⟷ Moon Nakshatra (*Manas* / Mental Perception).
   - **Molecule 2**: Rising Rāśi ($D_1$ physical form / outer tree) ⟷ Rising Navāṁśa ($D_9$ inner soul fruit / dharma).
   - **4 Macro Spectrums**:
     - *Introversion vs. Extroversion* (Solar/Lunar polarity + Active/Passive sign tallies).
     - *Practicality vs. Idealism* (Earth/Water tangible pragmatism vs. Fire/Air conceptual vision).
     - *Individual Defiance vs. Social Cooperation* (Tīkṣṇa/Ugra assertive fortitude vs. Mṛdu/Cala gentle harmony).
     - *Intellectual vs. Emotional Processing* (Air/Mercury/Sun analytical reason vs. Water/Moon/Venus feeling digest).

2. **Sequential Planetary Interpretation (5-Pillar Archetypal Decomposition)**:
   Interprets planets in strict priority sequence dictated by the **Parāśarī Prominence Leaderboard** (#1 Chart Commander first).

3. **Semantic Interaction Engine (Commonalities vs. Clashes)**:
   Compares theme pairs across the 5 pillars strictly using **Elements (Mahābhūtas)** and **Modalities (Guṇas)**:
   - **Commonalities (Resonances)**: Shared elements (Fire-Fire, Earth-Earth) or compatible elements (Fire-Air, Earth-Water) produce natural talents, effortless flow, and prominent gifts.
   - **Clashes (Dissonances)**: Incompatible elements (Fire-Water, Fire-Earth, Air-Earth, Air-Water) or conflicting modalities (Movable vs. Fixed) create dynamic developmental friction points, internal dilemmas, or growth engines.

4. **"Look Backwards" Macro Canvas Filter**:
   Filters individual planetary expressions through the background canvas.

5. **Tone Modulation via Existing Read-Only Dignity**:
   Ingests existing `expression_mode` ("Constructive" vs. "Challenging"), `net_scale_score`, and `deeptadi` / `balaadi` avasthas strictly for psychological tone color without altering any mathematical calculations.

6. **Harmonic Degree Overlays**:
   Projects continuous longitudes for $D_9$ (Navāṁśa), $D_7$ (Saptāṁśa), and $D_{10}$ (Daśāṁśa) onto the 360° natal wheel and identifies conjunctions with natal planets and angles within $\le 3^\circ 20'$ (one Navāṁśa pada).
