# Varga Vimshopaka & Vaisheshikamsa Engine Architecture

## 1. Classical Philosophy & Scriptural Authority
Varga Vimshopaka (literally *twenty-part strength*) is Maharishi Parashara's overarching metric of planetary dignity across divisional charts (*Vargas*), detailed in Chapters 6 and 46 of the *Brihat Parashara Hora Shastra* (BPHS). While Shadbala measures dynamic astronomical forces (motion, direction, diurnal cycle, aspects), Vimshopaka measures the **essential institutional dignity** of the planets across harmonic slices of the zodiac.

In Ernst Wilhelm's Kala software, Vimshopaka is evaluated across four classical tiers:
1. **Shadvarga** (6 primary divisional charts)
2. **Saptavarga** (7 divisional charts)
3. **Dasavarga** (10 divisional charts)
4. **Shodashavarga** (16 divisional charts)

---

## 2. 20-Point Dignity Scale (BPHS Chapter 46, Verses 24–25)

Every planet occupying a varga receives a base score on a 20-point scale:

25905\text{Score} = \begin{cases}
20.0 & \text{Exaltation (EX), Moolatrikona (MT), or Own House (OH)} \\
18.0 & \text{Great Friend's Sign (Adhimitra / GF)} \\
15.0 & \text{Friend's Sign (Mitra / F)} \\
10.0 & \text{Neutral's Sign (Sama / N)} \\
7.0  & \text{Enemy's Sign (Shatru / E)} \\
5.0  & \text{Great Enemy's Sign (Adhishatru / GE)} \\
0.0  & \text{Debilitation (Neecha / DB)}
\end{cases}25905

---

## 3. Parashari Scheme Weights (Total = 20.0)

Each divisional chart carries an exact proportional weight within its Parashari scheme:

| Varga | Chart | Shadvarga (6) | Saptavarga (7) | Dasavarga (10) | Shodashavarga (16) |
|---|---|---|---|---|---|
| **D1** | Rasi | 6.0 | 5.0 | 3.0 | 3.5 |
| **D2** | Hora | 2.0 | 2.0 | 1.5 | 1.0 |
| **D3** | Drekkana | 4.0 | 3.0 | 1.5 | 1.0 |
| **D4** | Chaturthamsa | — | — | — | 0.5 |
| **D7** | Saptamsa | — | 1.0 | 1.5 | 0.5 |
| **D9** | Navamsa | 5.0 | 2.5 | 1.5 | 3.0 |
| **D10**| Dasamsa | — | — | 1.5 | 0.5 |
| **D12**| Dvadasamsa | 2.0 | 4.5 | 1.5 | 0.5 |
| **D16**| Shodamsa | — | — | 1.5 | 2.0 |
| **D20**| Vimsamsa | — | — | — | 0.5 |
| **D24**| Chaturvimsamsa | — | — | — | 0.5 |
| **D27**| Bhamsa | — | — | — | 0.5 |
| **D30**| Trimsamsa | 1.0 | 2.0 | 1.5 | 1.0 |
| **D40**| Khavedamsa | — | — | — | 0.5 |
| **D45**| Akshavedamsa | — | — | — | 0.5 |
| **D60**| Shastiamsa | — | — | 5.0 | 4.0 |
| **Total** | | **20.0** | **20.0** | **20.0** | **20.0** |

**Final Score Calculation**:
25905\text{Vimshopaka Score} = \frac{1}{20} \sum_{v \in \text{Scheme}} \left( w_v \times \text{Dignity}(p, v) \right)25905

---

## 4. Vaisheshikamsa Honorific Classifications (BPHS Chapter 6, Verses 42–52)

When a planet repeatedly attains an auspicious dignity (**Exaltation, Moolatrikona, or Own House**) across the charts of a Parashari scheme, it earns an honorific classification:

### 4.1 Shadvarga
- 2 auspicious vargas: **(2) Kimsuka** (Palash Tree)
- 3: **(3) Vyanjana** (Insignia)
- 4: **(4) Chamara** (Fly-whisk)
- 5: **(5) Chatra** (Parasol/Umbrella)
- 6: **(6) Kundala** (Ear-ring)

### 4.2 Saptavarga & Dasavarga
- 2 auspicious vargas: **(2) Kimsuka** (Palash Tree)
- 3: **(3) Uttama** (Excellent)
- 4: **(4) Gopura** (Temple gate)
- 5: **(5) Simhasana** (Throne)
- 6: **(6) Paravata** (Pigeon)
- 7: **(7) Devaloka** (Divine realm)
- 8: **(8) Brahmaloka** (Realm of Brahma)
- 9: **(9) Shakravahana** (Mount of Indra)
- 10: **(10) Shridhama** (Abode of Lakshmi)

### 4.3 Shodashavarga
- 2 auspicious vargas: **(2) Bhedaka** (Distinctive)
- 3: **(3) Kusuma** (Blossom)
- 4: **(4) Nagapushpa** (Type of plant)
- 5: **(5) Kanduka** (Playing ball)
- 6: **(6) Kerala** (a Hora)
- 7: **(7) Kalpavriksha** (Wish-fulfilling tree)
- 8: **(8) Chandanavana** (Sandalwood forest)
- 9: **(9) Purnachandra** (Full Moon)
- 10: **(10) Uchchaishrava** (Divine steed)
- 11: **(11) Dhanvantari** (Divine physician)
- 12: **(12) Suryakanta** (Sun gem)
- 13: **(13) Vidruma** (Coral)
- 14: **(14) Shakrasimhasana** (Indra Throne)
- 15: **(15) Goloka** (Highest celestial realm)
- 16: **(16) Shrivallabha** (Beloved of Lakshmi)
