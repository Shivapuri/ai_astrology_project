# Ashtakavarga Engine Architecture & Mathematical Foundations

## 1. Classical Philosophy & Authority
The Ashtakavarga (literally *eight-fold division*) is Maharishi Parashara's quantitative evaluation framework expounded in Chapters 66–72 of the *Brihat Parashara Hora Shastra* (BPHS). It evaluates the collective auspiciousness of the 12 zodiacal signs by measuring the benefic points (*Bindus*) contributed by 8 foundational astrological reference points:
1. **Surya** (Sun)
2. **Chandra** (Moon)
3. **Mangala** (Mars)
4. **Budha** (Mercury)
5. **Guru** (Jupiter)
6. **Shukra** (Venus)
7. **Shani** (Saturn)
8. **Lagna** (Ascendant)

In Ernst Wilhelm's Kala methodology and software configuration, the classical Parashari definitions are strictly observed. Notably, textual corruptions found in later commentaries (such as Varahamihira's *Brihat Jataka*) are resolved in favor of the authentic BPHS verses:
- **Moon's BAV from Jupiter**: Benefic in the **2nd** house (not the 12th).
- **Venus's BAV from Mars**: Benefic in the **4th** house (not the 5th).

---

## 2. Benefic Houses Table (Prastarashtakavarga Grid)

Each of the 8 reference bodies contributes 1 bindu to specific houses reckoned from its natal sign position:

| Planet / Ref | Sun (48) | Moon (49) | Mars (39) | Mercury (54) | Jupiter (56) | Venus (52) | Saturn (39) | Lagna (49) |
|---|---|---|---|---|---|---|---|---|
| **Sun** | 1, 2, 4, 7, 8, 9, 10, 11 | 3, 6, 7, 8, 10, 11 | 3, 5, 6, 10, 11 | 5, 6, 9, 11, 12 | 1, 2, 3, 4, 7, 8, 9, 10, 11 | 8, 11, 12 | 1, 2, 4, 7, 8, 10, 11 | 3, 4, 6, 10, 11, 12 |
| **Moon** | 3, 6, 10, 11 | 1, 3, 6, 7, 10, 11 | 3, 6, 11 | 2, 4, 6, 8, 10, 11 | 2, 5, 7, 9, 11 | 1, 2, 3, 4, 5, 8, 9, 11, 12 | 3, 6, 11 | 3, 6, 10, 11, 12 |
| **Mars** | 1, 2, 4, 7, 8, 9, 10, 11 | 2, 3, 5, 6, 9, 10, 11 | 1, 2, 4, 7, 8, 10, 11 | 1, 2, 4, 7, 8, 9, 10, 11 | 1, 2, 4, 7, 8, 10, 11 | 3, 4, 6, 9, 11, 12 | 3, 5, 6, 10, 11, 12 | 1, 3, 6, 10, 11 |
| **Mercury**| 3, 5, 6, 9, 10, 11, 12 | 1, 3, 4, 5, 7, 8, 10, 11 | 3, 5, 6, 11 | 1, 3, 5, 6, 9, 10, 11, 12 | 1, 2, 4, 5, 6, 9, 10, 11 | 3, 5, 6, 9, 11 | 6, 8, 9, 10, 11, 12 | 1, 2, 4, 6, 8, 10, 11 |
| **Jupiter**| 5, 6, 9, 11 | 1, 2, 4, 7, 8, 10, 11 | 6, 10, 11, 12 | 6, 8, 11, 12 | 1, 2, 3, 4, 7, 8, 10, 11 | 5, 8, 9, 10, 11 | 5, 6, 11, 12 | 1, 2, 4, 5, 6, 7, 9, 10, 11 |
| **Venus** | 6, 7, 12 | 3, 4, 5, 7, 9, 10, 11 | 6, 8, 11, 12 | 1, 2, 3, 4, 5, 8, 9, 11 | 2, 5, 6, 9, 10, 11 | 1, 2, 3, 4, 5, 8, 9, 10, 11 | 6, 11, 12 | 1, 2, 3, 4, 5, 8, 9 |
| **Saturn**| 1, 2, 4, 7, 8, 9, 10, 11 | 3, 5, 6, 11 | 1, 4, 7, 8, 9, 10, 11 | 1, 2, 4, 7, 8, 9, 10, 11 | 3, 5, 6, 12 | 3, 4, 5, 8, 9, 10, 11 | 3, 5, 6, 11 | 1, 3, 4, 6, 10, 11 |
| **Lagna** | 3, 4, 6, 10, 11, 12 | 3, 6, 10, 11 | 1, 3, 6, 10, 11 | 1, 2, 4, 6, 8, 10, 11 | 1, 2, 4, 5, 6, 7, 9, 10, 11 | 1, 2, 3, 4, 5, 8, 9, 11 | 1, 3, 4, 6, 10, 11 | 3, 6, 10, 11 |

Total planetary bindus =  + 49 + 39 + 54 + 56 + 52 + 39 = 337$ bindus.

---

## 3. Reductions (Shodhana)

### 3.1 Trikona Shodhana (Trinal Reduction)
Defined in BPHS Chapter 67, Trikona Shodhana purifies redundant energy across the four elemental triads (*Trikonas*):
- **Fire (Agni)**: Aries (0), Leo (4), Sagittarius (8)
- **Earth (Prithvi)**: Taurus (1), Virgo (5), Capricorn (9)
- **Air (Vayu)**: Gemini (2), Libra (6), Aquarius (10)
- **Water (Jala)**: Cancer (3), Scorpio (7), Pisces (11)

**Mathematical Rule**:
For any trine $ with bindu counts $:
25869x_i' = x_i - \min(x_1, x_2, x_3)25869

### 3.2 Ekadhipatya Shodhana (Dual-Lordship Reduction)
Defined in BPHS Chapter 68, Ekadhipatya Shodhana reconciles signs co-ruled by the same planetary lord:
- **Mars**: Aries (0) and Scorpio (7)
- **Venus**: Taurus (1) and Libra (6)
- **Mercury**: Gemini (2) and Virgo (5)
- **Jupiter**: Sagittarius (8) and Pisces (11)
- **Saturn**: Capricorn (9) and Aquarius (10)

*Exemptions*: Cancer (ruled by Moon) and Leo (ruled by Sun) possess single rulership and are never reduced in Ekadhipatya Shodhana.
*Occupancy Rule*: Only the 7 classical planets (Sun through Saturn) count as occupants. Rahu and Ketu are mathematical nodes and do not count as occupying grahas for this reduction.

**Rules for a Pair of Signs $ with Post-Trikona Bindus *:
1. **Zero Presence**: If  = 0$ or  = 0$, no reduction is performed.
2. **Both Occupied**: If both signs contain at least one planet, no reduction is performed.
3. **Neither Occupied**:
   Subtract the minimum from both:
   25869v_A' = v_A - \min(v_A, v_B), \quad v_B' = v_B - \min(v_A, v_B)25869
4. **One Occupied, One Unoccupied**:
   Let {occ}$ be the occupied sign and {unocc}$ be the empty sign.
   - If {occ} \ge v_{unocc}$: the empty sign is reduced to 0 ({unocc}' = 0$).
   - If {occ} < v_{unocc}$: the empty sign is reduced to equal the occupied sign ({unocc}' = v_{occ}$).

---

## 4. Sarvashtakavarga (SAV) Reductions

Sarvashtakavarga is the sum of the 7 planets' BAVs across all 12 signs (totaling exactly 337 points).
In Kala software:
1. **SAV Trikona Shodhana**:
   The trinal baseline reduces each sign's raw SAV count modulo 12 relative to the 26 baseline anchor:
   25869	ext{SAV\_Trikona}[s] = (	ext{Total\_SAV}[s] - 26) \pmod{12}25869
2. **SAV Ekadhipatya Shodhana**:
   Standard Parashari Ekadhipatya Shodhana rules are applied to the resulting SAV Trikona values using the natal planetary occupancy grid.

---

## 5. Shodhya Pindas (Purified Units)

Per BPHS Chapter 69:
- **Rasi Pinda**: $\sum_{i=0}^{11} (	ext{Shodhita\_Bindu}[i] 	imes 	ext{Rasi\_Multiplier}[i])$
  Where Rasi Multipliers are:
  - Aries: 7, Taurus: 10, Gemini: 8, Cancer: 4, Leo: 10, Virgo: 6,
  - Libra: 7, Scorpio: 8, Sagittarius: 9, Capricorn: 5, Aquarius: 11, Pisces: 12.
- **Graha Pinda**: $\sum_{p \in 	ext{Planets}} (	ext{Shodhita\_Bindu}[	ext{Sign}(p)] 	imes 	ext{Graha\_Multiplier}[p])$
  Where Graha Multipliers are:
  - Sun: 5, Moon: 5, Mars: 8, Mercury: 5, Jupiter: 10, Venus: 7, Saturn: 5.
- **Yoga Pinda (Shodhya Pinda)**: $	ext{Rasi Pinda} + 	ext{Graha Pinda}$.
