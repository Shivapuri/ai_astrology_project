# Jyotish Engine: Planetary Friendships & Dignity (relationships.py)

This file serves as the foundational astrological relationship engine based on Parashara and Ernst Wilhelm's Kala software.

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

1. **Three-Tier Friendship System:**
   - `get_natural_relationship()` (Naisargika): Calculated from the planet's *Moolatrikona* sign. Returns: "Friend", "Neutral", "Enemy".
   - `get_temporary_relationship()` (Tatkalika): Based purely on physical distance in the D1 (Rasi) chart. "3 signs in front, 3 behind" = Friend. Others (conjunct, or 5, 6, 7, 8, 9 away) = Enemy.
   - `get_compound_relationship()` (Panchadha): Mathematical sum of Natural + Temporary. Returns 5 levels: "Great Friend", "Friend", "Neutral", "Enemy", "Great Enemy".

2. **Dignity Logic (`get_dignity`):**
   - Must check fixed dignities FIRST (Exalted, Debilitated, Moolatrikona, Own Sign).
   - If none match, it returns the sign lord's compound relationship (e.g., "Great Friend's Sign", "Enemy's Sign").

3. **Rasi Aspects (`get_rasi_aspects`):**
   - Returns whole-sign aspects (Drishti).
   - Cardinal aspects Fixed (except adjacent). Fixed aspects Cardinal (except adjacent). Dual aspects Dual.

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

## 4. Special Astrological Exceptions & Limits
As implemented in `generate_jyotish.py` and `relationships.py`:
- **Varga Specific Distances (Tatkalika):** Tatkalika (Temporary Friendship) is ALWAYS calculated using the planetary positions in the D1 (Rasi) chart, even when determining Dignity for higher Vargas like D9 or D60.
- **Deep Debilitation Limits:** A planet is only considered 'Debilitated' (DB) if it falls within specific degree limits. If it exceeds these limits, it reverts to standard compound friendship with the sign lord.
  - **Moon:** Only debilitated between 0° and 3° of Scorpio.
  - **Mercury:** Only debilitated between 0° and 15° of Pisces.
- **Even Rasi Varga Reversals:** Dasamsa (D10) and Chaturvimsamsa (D24) strictly follow the Parashara rule: "Reverse for Even Rasis". This means for Even signs, we start from the 9th sign (or Cancer for D24) and count **backwards** instead of forwards.
