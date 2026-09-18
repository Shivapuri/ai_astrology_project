# 📘 Astra Master Graha Diagnostics & Planetary Evaluation Engine
**The Definitive Mathematical & Astrological Specification for Planetary Vitality, Dignity, and Behavioral Archetypes**

> **Module Location:** `jyotish/planetary_evaluation/planetary_evaluation.py`  
> **Companion Engines:** `jyotish/planetary_evaluation/lagna_evaluation.py` & `jyotish/yogas/chandal_yogas.py`  
> **PDF Exporter:** `jyotish/pdf_exporter.py`  
> **Frontend Cockpit:** `templates/index.html`  
> **Classical Foundations:** *Brihat Parashara Hora Shastra* (Chapters 3, 26, 34, 45–50), *Phaladeepika* (Chapters 2, 3, 4, 15, 18), and Ryan Kurczak & Vic DiCara Vault Teachings.

---

## 🧭 1. Executive Summary & Epistemological Rationale

The **Planetary Evaluation & Master Graha Diagnostics** engine provides an independent, holistic diagnostic evaluation for every planet in the horoscope. It evaluates:
1. **Moral Character & Intent (Dignity / Quality):** Does the planet express noble archetypal ideals (courage, wisdom, grace) or frustrated, corrupt reactions (cruelty, greed, blame)?
2. **Kinetic Muscle & Stamina (Shadbala / Quantity):** Does the planet possess the kinetic resources, stamina, and real-world leverage to execute its agenda?
3. **Dispositor Bedrock (Host Foundation):** Is the planet supported by an honorable, solvent host, or trapped in a strained foundation?
4. **Ascendant Functional Alignment (Lagna Vector):** How is the planet programmed by the rising sign (*BPHS* Ch. 34)—as a supportive benefactor (*Śubha*), an aggressive materialist (*Trishadāya*), an obstacle (*Bādhaka*), or a life protector (*Lagneśa*)?
5. **Environmental Sky-Weather (Drishti & Yuti):** Aspect rays, conjunction intensity, and qualitative aspect transmission (Recursive Drishti).
6. **Psychological & Biological States (Lajjitadi & Baladi):** Internal trauma/confidence and biological operational efficiency.

---

## 🧮 2. The Master Dignity Scale (Kurczak 12.5% Step Scale & Panchadha Maitri)

Essential dignity is computed using Sage Parashara's 5-Fold Compound Relationship (*Panchadha Maitri*), combined with Ryan Kurczak's 12.5% mathematical step scale, odd/even sign gender polarity, and classical Moolatrikona degree bounds:

| Compound Dignity State | Canonical Sanskrit Term | Percentage Score | Archetypal Meaning & Psychological Foundation |
| :--- | :--- | :---: | :--- |
| **Exalted** | *Uccha* | **100.0%** | Peak sovereign nobility; flawless archetypal expression; selfless, expansive virtue. |
| **Moolatrikona** | *Moolatrikona* | **87.5%** | Royal office; planetary duty fulfilled with joyful mastery and purposeful command. |
| **Own Positive Sign** (Odd/Male) | *Sva-kshetra (Puruṣa)* | **75.0%** | Domicile authority; active, assertive, outward projection of planetary gifts. |
| **Own Sign Midpoint** | *Sva-kshetra* | **68.75%** | Neutral baseline when sign polarity is not explicitly evaluated. |
| **Own Negative Sign** (Even/Female) | *Sva-kshetra (Strī)* | **62.5%** | Receptive domicile; inward, introspective, grounded, and self-contained power. |
| **Great Friend** | *Adhi Mitra* | **60.0%** | Warm, honored guest; highly cooperative, generous, and comfortable foundation. |
| **Friend** | *Mitra* | **50.0%** | Welcomed companion; pleasant relations, steady support, constructive baseline. |
| **Neutral** | *Sama* | **37.5% – 50.0%** | Pragmatic business partner; dynamic tilt based on host support and aspect weather. |
| **Enemy** | *Shatru* | **25.0%** | Strained friction; defensive, guarded, or awkward operational environment. |
| **Great Enemy** | *Adhi Shatru* | **20.0%** | Severe hostility; heavy resistance, deep friction, and high effort required. |
| **Debilitated** | *Neecha* | **12.5%** | Acute distress, inverted values, deep vulnerability; raw material for transmutation. |

### 2.1 Deep Exaltation & Debilitation Degrees (*Paramoccha* & *Parama-Neecha*)
* **Sun:** Exalted at $10^\circ$ Aries / Debilitated at $10^\circ$ Libra
* **Moon:** Exalted at $3^\circ$ Taurus / Debilitated at $3^\circ$ Scorpio
* **Mars:** Exalted at $28^\circ$ Capricorn / Debilitated at $28^\circ$ Cancer
* **Mercury:** Exalted at $15^\circ$ Virgo / Debilitated at $15^\circ$ Pisces
* **Jupiter:** Exalted at $5^\circ$ Cancer / Debilitated at $5^\circ$ Capricorn
* **Venus:** Exalted at $27^\circ$ Pisces / Debilitated at $27^\circ$ Virgo
* **Saturn:** Exalted at $20^\circ$ Libra / Debilitated at $20^\circ$ Aries
* **Rahu:** Exalted in Taurus $20^\circ$ (or Gemini $15^\circ$) / Debilitated in Scorpio $20^\circ$ (or Sagittarius $15^\circ$)
* **Ketu:** Exalted in Scorpio $20^\circ$ (or Sagittarius $15^\circ$) / Debilitated in Taurus $20^\circ$ (or Gemini $15^\circ$)

### 2.2 Strict Moolatrikona Boundaries (BPHS Ch. 3)
* **Sun:** Leo $0^\circ 00' - 20^\circ 00'$ (beyond $20^\circ$ = Own Positive Sign, 75.0%)
* **Moon:** Taurus $3^\circ 00' - 30^\circ 00'$ ($0^\circ - 3^\circ$ = Exalted, 100.0%)
* **Mars:** Aries $0^\circ 00' - 12^\circ 00'$ (beyond $12^\circ$ = Own Positive Sign, 75.0%)
* **Mercury:** Virgo $15^\circ 00' - 20^\circ 00'$ ($0^\circ - 15^\circ$ = Exalted, 100.0%; $20^\circ - 30^\circ$ = Own Negative Sign, 62.5%)
* **Jupiter:** Sagittarius $0^\circ 00' - 10^\circ 00'$ (beyond $10^\circ$ = Own Positive Sign, 75.0%)
* **Venus:** Libra $0^\circ 00' - 15^\circ 00'$ (beyond $15^\circ$ = Own Positive Sign, 75.0%)
* **Saturn:** Aquarius $0^\circ 00' - 20^\circ 00'$ (beyond $20^\circ$ = Own Positive Sign, 75.0%)

---

## 🛡️ 3. Strict Neecha Bhanga & Dispositor Host Dynamics

* **Strict Signs of Fall (Exclusivity Rule):** Neecha Bhanga is strictly granted ONLY to true signs of fall (Sun in Lib, Moon in Sco, Mars in Can, Mer in Pis, Jup in Cap, Ven in Vir, Sat in Ari, Rah in Sco, Ket in Tau). Enemy signs (like Mars in Virgo) are NOT debilitated and can never receive Neecha Bhanga.
* **Full Alchemical Rescue (*Neecha Bhanga Raja Yoga*):** Dispositor Host Dignity $\ge 62.5\%$ AND Shadbala $\ge 90\% \to \text{Effective Dignity} = \text{clamp}(\text{dignity} + 50.0 \times (\text{host\_dignity}/100.0),\, 20.0,\, 85.0)$. Unlocks **`⚡ The Transmuted Hero`**!
* **Neutral Sign Dynamic Tilt (*Sama Kshetra*):** Benefic rays and Mudita/Garvita avasthas lift neutral dignity up to **$54.9\%$**, ensuring that disciplined powerhouse placements (like Shivapuri Baba's Mars & Saturn) are diagnosed as **`⚒️ The Pragmatic Executive`** rather than false Armed Dictators.

---

## 🧭 4. The 12-Ascendant Functional Matrix (BPHS Ch. 34)

* **Lagnesha Protection:** Conjunction or aspect from the Ascendant Lord grants a **$+0.35$ protective modifier**.
* **Trishadāya Rulership (3, 6, 11):** Intense Functional Malefics driven by worldly appetite and competitive friction.
* **Single Yogakārakas:** Saturn (Taurus, Libra), Mars (Cancer, Leo), Venus (Capricorn, Aquarius).
* **The Aquarius Ascendant & Himmler Paradigm:**
  - Aquarius Lagna: Jupiter rules 2nd (Maraka) and 11th (Trishadāya) $\to$ Functional Malefic.
  - Himmler's Jupiter in Sagittarius (Moolatrikona H11, 143% Shadbala) conjoined Rahu ($4.9^\circ \to$ **Guru-Chāṇḍāla Yoga**) and Saturn ($8.4^\circ \to$ **Deeptādi Vikala Avasthā**, besieged by 2 cruel planets).
  - Score is accurately calibrated to **★ 7.9 / 10 Capable** (preserving real executive capacity) while re-synthesizing the archetype to **`⚡ Ideological Mobilizer`** with explicit red warning badges.

---

## 🐉 5. The Complete Rahu & Ketu (R1 & K2) Protocol

* **Dispositor Proxy Rule:** Nodes inherit 85% host dignity and 90% host Shadbala.
* **Sign Affinity Boost (+15%):** Rahu in Taurus, Gemini, Virgo, Aquarius; Ketu in Scorpio, Sagittarius, Pisces.
* **Conjunction Orbs:** Exact/Intimate ($< 3^\circ 20'$ / One Navamsha) $\to$ Nodal Possession; Moderate ($3^\circ 20' - 10^\circ 00'$); Wide ($> 10^\circ$).
* **Classical Nodal Affliction Yogas (`jyotish/yogas/chandal_yogas.py`):**
  - **Guru-Chāṇḍāla Yoga (Jupiter + Rahu):** Subversive zeal, taboo doctrine, ideological fanaticism.
  - **Guru-Ketu Jñāna Yoga (Jupiter + Ketu):** Direct spiritual discernment, skepticism of dogma, pure jñāna (not a dosha).
  - **Shrapit Yoga (Saturn + Rahu):** Karmic curse, chronic institutional toil.
  - **Angaraka Yoga (Mars + Rahu):** Explosive drive, technical audacity, violence risk.

---

## ⚔️ 6. Graha Yuddha (Planetary War) & Deeptādi Vikala Avasthā

* **Graha Yuddha:** 5 starry planets within $|\Delta \lambda| \le 1^\circ 00'$ in same sign.
  - **Venus Invariance:** Venus NEVER loses war due to supreme natural luminosity (*Bahula-Ruchi*).
  - **Northern Latitude Rule:** Higher celestial latitude (*Udaka*) wins; loser is *Nipidita* ($-0.60$); victor absorbs $\Delta \text{Bala}$ and inherits **Combat Stain**.
* **Deeptādi Vikala Avasthā:** Conjunction with 2 or more cruel malefics (Sun, Mars, Saturn, Rahu, Ketu) penalizes vitality by **$-0.30$** and flags `🩸 Vikala (Besieged)`.

---

## 🔢 7. The Calibrated Vitality Score Formula (1.0 to 10.0)

$$\text{Final Vitality Score} = \text{clamp}\Big(5.0 + (\text{PreScore} - 5.0) \times (0.6 + 0.4 \times E_{\text{baladi}}),\, 1.0,\, 10.0\Big)$$

$$\text{PreScore} = \text{BaseVit} + \text{EnvMod} + \text{MotMod} + \text{PsyMod} + \text{WarMod} + \text{NodeMod} + \text{VikalaMod}$$

### Score Tiers:
* $\ge 8.5$: **`🌟 Sovereign`**
* $7.0 - 8.4$: **`🟢 Capable`**
* $5.5 - 6.9$: **`🟡 Resilient`**
* $4.0 - 5.4$: **`🟠 Strained`**
* $< 4.0$: **`🔴 Fragile`** / **`🔴 Severe Hazard`**

---

## 🧘 8. Deeptādi & Lajjitādi Avasthā Systems (*Art & Science of Vedic Astrology, Vol 2*)

### 8.1 Innate Mental Mood: Deeptādi Avasthā (Saravali Ch. 5 & Vol 2 Ch. 4)
While dignity sets the functional foundation, **Deeptādi** determines the internal psychological attitude, mood, and subjective state of the planet:
1. **Nipeedita (Harmed):** Defeated in Graha Yuddha (planetary war). Bruised, obstructed, requires healing.
2. **Vikala (Mutilated):** Combust within solar orb (*Astangata*). Outer material expressions scorched, forced inward.
3. **Bhita (Alarmed):** In the sign of its fall (Debilitated). Anxious, vulnerable, guarded.
4. **Deeptha (Radiant):** In its exaltation sign. Luminous sovereign confidence, peak benevolence.
5. **Swastha (Confident):** In its own sign or Moolatrikona. Grounded self-reliance, comfortable authority.
6. **Sakta (Strong):** Retrograde with high brightness/horsepower. Focused, potent determination.
7. **Mudita (Rejoicing):** In a friend's sign. Welcomed and honored guest, cooperative ease.
8. **Khala (Sorrowful / Mischievous):** In an enemy's sign. Defensive friction, stubborn uphill struggle.
9. **Santa (Peaceful / Serene):** In a neutral sign. Pragmatic composure, steady baseline.

### 8.2 House Management & Alertness: Jagradādi Avasthā (Vol 2 Ch. 10)
Alertness (*Jagrat*, *Svapna*, *Sushupti*) determines the planet's capacity to manage and manifest house affairs, as well as the potency with which it influences other planets:
* **Jagrat (Awake - 1.00 / 100%):** Exalted, Moolatrikona, or Own Sign. Full executive management; 100% full-force impact when influencing other grahas.
* **Svapna (Sleepy - 0.50 / 50%):** Friend's or Neutral Sign. Half management capacity; moderate, bearable impact on other grahas.
* **Sushupti (Asleep - 0.10 / 10%):** Enemy's or Debilitated Sign. Cannot sustain house results alone; sluggish, muted, or minimal impact on other grahas.

### 8.3 Social & Relational Complexes: Lajjitādi Alertness Calibration (Vol 2 Ch. 10 & 11)
Lajjitādi states (Proud, Delighted, Starved, Agitated, Bashful, Thirsty) describe relational dynamics between planets. Crucially, Kurczak formulates that **the intensity of a Lajjitādi feeling state is directly governed by the influencer's Jagradādi alertness**:
* **Full Severity:** If an enemy starver (causing *Kshudhita*) is **Jagrat (Awake)**, the starvation is acute and demanding.
* **Muted Severity:** If the enemy starver is **Sushupti (Asleep)**, the starvation is sluggish and harmless, easily overcome through steadfast commitment.
* **Self-Stamina Resilience:** If the native planet is itself **Jagrat (Awake)**, it possesses high self-resilience, reducing negative relational friction by 25%.

### 8.4 Psychological Reality Diagnosis
Each planet's evaluation synthesizes these three layers into a rich 3-sentence diagnostic narrative:
1. **Baseline Mood & Alertness:** Internal attitude (*Deeptādi*) + operational capacity (*Jagradādi*).
2. **Relational Dynamic:** Calibrated social complexes (*Lajjitādi*) noting specific influencing planets and their alertness levels.
3. **Developmental Path:** Core developmental guidance (*Kurczak Vol 2*) tailored to the planet's true psychological reality.

---
*Authoritative specification for Astra Engine Master Graha Diagnostics.*
