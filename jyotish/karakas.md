# ★ Karakas & Functional Planetary Roles (Kāraka & Yogakāraka Adhyāya)

This module implements the mathematical calculation and classification of planetary significators (**Kārakas**) and functional roles (**Yogakārakas**, Functional Benefics, Functional Malefics, Mārakas, and Bādhakas) in the Astra engine.

---

## 📜 Classical Scriptural Foundations

### 1. Brihat Parashara Hora Shastra (BPHS)
* **Chapter 32: *Kārakādhyāya* (The Chapter on Significators)**
  * *Śloka 2–4:* The planets that have advanced the highest longitude within a sign (0° to 30°) are the Chara (temporal/movable) Kārakas.
  * *Śloka 5–12:* The 7 Chara Kārakas:
    1. **Ātmakāraka (AK):** Highest degree. Represents the Soul, the Self, the King of the horoscope.
    2. **Amātyakāraka (AmK):** 2nd highest. Represents the Mind, intellect, career, advisor/counselor.
    3. **Bhrātṛkāraka (BK):** 3rd highest. Represents brothers, mentors, spiritual preceptors, companions.
    4. **Mātṛkāraka (MK):** 4th highest. Represents mother, emotional stability, home, education.
    5. **Putrakāraka (PK):** 5th highest. Represents children, disciples, intellect, creative fruits.
    6. **Jñātikāraka / Gñātikāraka (GK):** 6th highest. Represents kinsmen, rivals, illnesses, disputes.
    7. **Dārakāraka (DK):** Lowest degree (7th). Represents spouse, partner, intimate relationships.
  * *Rāhu & Ketu:* As shadow nodes (Chhāyā Grahas), they do not hold Chara Kāraka seats in the classical 7-Kāraka Parashari system.

* **Chapter 34: *Yogakārakādhyāya* (The Chapter on Yogakārakas and Functional Rulerships)**
  * *Śloka 13:* *"kendre koNe sthito vā.asau viśeṣādyogakārakaḥ"* — A planet that simultaneously owns a Kendra (quadrant: houses 1, 4, 7, 10) and a Trikona (trine: houses 1, 5, 9) becomes especially endowed with Yogakāraka status (bestower of royal union and success).
  * *Śloka 14–45:* Systematic definition of functional benefics (*Śubha*), functional malefics (*Aśubha*), and Yogakārakas for all 12 Lagnas.

### 2. Vedic Astrology: An Integrated Approach (P.V.R. Narasimha Rao)
* **Chapter 8 (Significators) & Chapter 13.2 (Functional Nature):**
  * Table 30 defines the exact functional classifications for each Lagna.
  * Only 6 Lagnas have a single Yogakāraka:
    * **Taurus:** Saturn (rules 9th Trikona & 10th Kendra)
    * **Cancer:** Mars (rules 5th Trikona & 10th Kendra)
    * **Leo:** Mars (rules 4th Kendra & 9th Trikona)
    * **Libra:** Saturn (rules 4th Kendra & 5th Trikona)
    * **Capricorn:** Venus (rules 5th Trikona & 10th Kendra)
    * **Aquarius:** Venus (rules 4th Kendra & 9th Trikona)

---

## 🧮 Mathematical Definitions

### 1. Chara Kārakas (7-Graha Scheme)
For each planet $p \in \{\text{Sun}, \text{Moon}, \text{Mars}, \text{Mercury}, \text{Jupiter}, \text{Venus}, \text{Saturn}\}$:
$$\text{degree\_in\_sign}(p) = \text{longitude}(p) \pmod{30.0}$$
Planets are sorted in strictly descending order of $\text{degree\_in\_sign}(p)$:
* Rank 1 $\rightarrow$ `AK` (Ātmakāraka)
* Rank 2 $\rightarrow$ `AmK` (Amātyakāraka)
* Rank 3 $\rightarrow$ `BK` (Bhrātṛkāraka)
* Rank 4 $\rightarrow$ `MK` (Mātṛkāraka)
* Rank 5 $\rightarrow$ `PK` (Putrakāraka)
* Rank 6 $\rightarrow$ `GK` (Jñātikāraka)
* Rank 7 $\rightarrow$ `DK` (Dārakāraka)

### 2. House Rulerships from Ascendant
Given Ascendant sign index $L \in [0..11]$ (where $0 = \text{Aries}, \dots, 11 = \text{Pisces}$):
For each house $h \in [1..12]$:
$$\text{sign\_index}(h) = (L + h - 1) \pmod{12}$$
The lord of house $h$ is the traditional ruler of $\text{sign\_index}(h)$.

### 3. Functional Status Classification
* **Yogakāraka:** Rules at least one Kendra from $\{4, 7, 10\}$ AND at least one Trikona from $\{5, 9\}$.
* **Lagneśa:** Rules House 1 (always a primary benefic).
* **Māraka:** Rules House 2 or House 7.
* **Bādhaka:**
  * Movable Lagnas (Aries, Cancer, Libra, Capricorn) $\rightarrow$ 11th lord.
  * Fixed Lagnas (Taurus, Leo, Scorpio, Aquarius) $\rightarrow$ 9th lord.
  * Dual Lagnas (Gemini, Virgo, Sagittarius, Pisces) $\rightarrow$ 7th lord.
* **Duṣṭhāna Lord:** Rules House 6, 8, or 12.

---

## 🔒 Epistemological Rules & Zero Hard-Coding
1. Every calculation is dynamically derived from Swiss Ephemeris longitudes and the Ascendant sign.
2. Chara Kārakas are calculated on D1 longitudes and remain constant across all Vargas.
3. Functional house rulerships can be dynamically evaluated for both D1 and any divisional chart (Varga) Lagna.
