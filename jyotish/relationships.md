# AI Documentation: relationships.py

## Core Concept
This file is the foundational astrological relationship engine based on Parashara and Ernst Wilhelm's Kala software.

## Critical Rules to Maintain
1. **Three-Tier Friendship:**
   - `get_natural_relationship()` (Naisargika): Permanent inborn friendship. Calculated from the planet's *Moolatrikona* sign. Returns: "Friend", "Neutral", "Enemy".
   - `get_temporary_relationship()` (Tatkalika): Based purely on physical distance in the D1 (Rasi) chart. "3 signs in front, 3 behind" = Friend. Others = Enemy.
   - `get_compound_relationship()` (Panchadha): Mathematical sum of Natural + Temporary. Returns 5 levels: "Great Friend", "Friend", "Neutral", "Enemy", "Great Enemy".

2. **Dignity Logic (`get_dignity`):**
   - Must check fixed dignities FIRST (Exalted, Debilitated, Moolatrikona, Own Sign).
   - If none match, it returns the sign lord's relationship (e.g., "Great Friend's Sign", "Enemy's Sign").

3. **Rasi Aspects (`get_rasi_aspects`):**
   - Returns whole-sign aspects (Drishti).
   - Cardinal aspects Fixed (except adjacent). Fixed aspects Cardinal (except adjacent). Dual aspects Dual.
