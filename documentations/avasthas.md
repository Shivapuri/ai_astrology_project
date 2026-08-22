# Planetary Avasthas

This document outlines the detailed calculation rules, implementation logic, and astrological usage of the Planetary Avasthas (States of the Planets) used in the Astra engine. These are based on the classical principles from *Brihat Parashara Hora Shastra* and the teachings of Ernst Wilhelm.

---

## 1. Bala Avastha (Age / Vitality)

### Source Reference
*Brihat Parashara Hora Shastra, Chapter 45 (Avasthadhyaya), Verses 3-4:*
> क्रमाद् बालः कुमारोऽथ युवा वृद्धस्तथा मृतः ।
> षडंशैरसमे खेटः समे ज्ञेयो विपर्ययात् ॥ ३॥
> फलं पादमितं बाले फलार्धं च कुमारके ।
> यूनि पूर्णं फलं ज्ञेयं वृद्धे किञ्चित् मृते च खम् ॥ ४॥

### Overview
Bala Avastha literally translates to the "Age" of a planet. It measures the physical capacity, vitality, and external strength of a planet to yield its karmic results in the material world. It is strictly a sign-based (Rasi) measurement.

### How it is Calculated
A zodiac sign consists of exactly 30 degrees. The Bala Avastha divides these 30 degrees into five equal segments of 6 degrees each. The state and the percentage of strength depend on whether the planet is placed in an Odd (Masculine) sign or an Even (Feminine) sign.

**Odd Signs (Masculine):** Aries, Gemini, Leo, Libra, Sagittarius, Aquarius
**Even Signs (Feminine):** Taurus, Cancer, Virgo, Scorpio, Capricorn, Pisces

**Degrees for Odd Signs:**
- **0° to 6°:** Bala (Infant) — Yields 1/4 strength (25%)
- **6° to 12°:** Kumara (Youth) — Yields 1/2 strength (50%)
- **12° to 18°:** Yuva (Adult/Prime) — Yields full strength (100%)
- **18° to 24°:** Vriddha (Elderly) — Yields minimal strength (~10%)
- **24° to 30°:** Mrita (Dead) — Yields 0 strength (0%)

**Degrees for Even Signs (Reversed):**
- **0° to 6°:** Mrita (Dead) — Yields 0 strength (0%)
- **6° to 12°:** Vriddha (Elderly) — Yields minimal strength (~10%)
- **12° to 18°:** Yuva (Adult/Prime) — Yields full strength (100%)
- **18° to 24°:** Kumara (Youth) — Yields 1/2 strength (50%)
- **24° to 30°:** Bala (Infant) — Yields 1/4 strength (25%)

### Implementation and Use
In the codebase, this is implemented in `jyotish/avasthas/bala.py`. 
- An **"Adult" (Yuva)** planet has the physical force to make things happen easily in the external world.
- A **"Dead" (Mrita)** planet completely lacks external physical force. Instead, its energy is highly internalized, operating on a psychological, subconscious, or spiritual level. The native must often rely on non-traditional methods or other people to achieve material success in areas ruled by a Dead planet.

---

## 2. Jagrat Avastha (Consciousness / Alertness)

### Source Reference
*Brihat Parashara Hora Shastra, Chapter 45 (Avasthadhyaya), Verses 5-6:*
> स्वभोच्चयोः समसुहृद्भयोः शत्रुभनीचयोः ।
> जाग्रत्स्वप्नसुषुप्त्याख्या अवस्था नामदृक्फलाः ॥ ५॥
> जागरे च फलं पूर्णं स्वप्ने मध्यफलं तथा ।
> सुषुप्तौ तु फलं शून्यं विज्ञेयं द्विजसत्तम ॥ ६॥

### Overview
Jagrat Avastha measures the "alertness" or state of consciousness of a planet. It tells us whether a planet's effects are fully awake, muffled as in a dream, or completely dormant and sleeping.

### How it is Calculated
Unlike Bala Avastha which uses degrees, Jagrat Avastha is determined strictly by the planet's **Dignity** (its relationship with the sign it is placed in).

The Dignities map to three states of consciousness:

1. **Jagrat (Awake) — 100% Alertness**
   - **Condition:** The planet is in Exaltation, Moolatrikona, or its Own Sign.
   - **Effect:** The planet is fully active, aware, and brings obvious, tangible results to the surface.

2. **Svapna (Dreaming) — 50% Alertness**
   - **Condition:** The planet is in a Great Friend's, Friend's, or Neutral's Sign.
   - **Effect:** The planet operates in a semi-conscious, internal state. Its results may be half-manifested, happening more in the mind or requiring a "wake-up call" to fully materialize.

3. **Sushupti (Sleeping / Slumbering) — 0% Alertness**
   - **Condition:** The planet is in an Enemy's, Great Enemy's, or Debilitation Sign.
   - **Effect:** The planet's energy is completely muffled, dormant, and inactive. It is unaware of its surroundings and struggles to produce clear results.

### Implementation and Use
In the codebase, this is implemented in `jyotish/avasthas/jagrat.py`. It reads the `final_dignity` calculated by the compound relationship engine and assigns the appropriate state of consciousness.

---
*(Further Avasthas such as Deeptadi, Lajjitadi, and Shayanadi will be added here as they are implemented.)*
