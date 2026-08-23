# Simple Guide: How the Avasthas (Planetary States) Work

"Avastha" simply means the "State" or "Condition" of a planet. Imagine a planet as a person: they have a physical age, a level of alertness, a psychological mood, and a social reaction to the people around them. 

The software currently calculates 4 sets of Avasthas for each planet:

## 1. Bala Avastha (Age & Vitality)
**The Concept:** Tells us the physical age and energy level of the planet to get things done in the real world.
**The Jyotish Rule:** The software ignores friendships entirely for this. It simply looks at the exact **Degree (0° to 30°)** of the planet. It chops the 30-degree sign into 5 slices of 6 degrees each. 

**What are Odd and Even Signs?**
*   **Odd Signs (1, 3, 5, 7, 9, 11):** Aries, Gemini, Leo, Libra, Sagittarius, Aquarius. These are considered masculine, active, and outward-moving signs. Energy flows straight forward here.
*   **Even Signs (2, 4, 6, 8, 10, 12):** Taurus, Cancer, Virgo, Scorpio, Capricorn, Pisces. These are considered feminine, receptive, and inward-moving signs. Because their energy flows inward, the age cycle runs in reverse!

**The Exact Degree Slices:**

**If the planet is in an ODD Sign (Energy moves forward):**
*   **0° to 6° — Infant (Bala):** 25% energy. Just waking up, lots of potential but easily distracted.
*   **6° to 12° — Youth (Kumara):** 50% energy. Excited, active, but lacking full maturity.
*   **12° to 18° — Adult (Yuva):** 100% full power. Mature, capable, and ready to conquer.
*   **18° to 24° — Old (Vriddha):** ~12% weak energy. Tired, relying on wisdom rather than physical force.
*   **24° to 30° — Dead (Mrita):** 0% external physical energy. The planet operates completely internally or spiritually.

**If the planet is in an EVEN Sign (Energy moves in reverse):**
*   **0° to 6° — Dead (Mrita):** 0% external energy.
*   **6° to 12° — Old (Vriddha):** ~12% weak energy.
*   **12° to 18° — Adult (Yuva):** 100% full power (Notice that Adult is always in the exact middle, between 12° and 18°, regardless of the sign!).
*   **18° to 24° — Youth (Kumara):** 50% energy.
*   **24° to 30° — Infant (Bala):** 25% energy.

## 2. Jagradadi Avastha (Consciousness / Alertness)
**The Concept:** Tells us if the planet is wide awake and paying attention, daydreaming, or fast asleep on the job.
**The Jyotish Rule:** The software looks at the planet's dignity (using **Compound Friendship**):
- **Awake (Jagrat - 100%):** If the planet is **Exalted** (at its absolute peak) or in its **Own Sign**.
- **Dreaming (Svapna - 50%):** If the planet is in the sign of a **Great Friend, Friend, or Neutral**. It acts half-asleep.
- **Sleeping (Sushupti - 0%):** If the planet is **Debilitated** (at its weakest) or in an **Enemy's sign**. It is totally unconscious to the outside world.

## 3. Deeptadi Avasthas (The 9 Moods)
**The Concept:** This describes the psychological attitude and mood of the planet.
**The Jyotish Rule:** The software first checks if the planet is physically stressed in the sky:
- **Angry:** If it is **Combust** (burning up because it is too close to the Sun).
- **Powerful/Driven:** If it is **Retrograde** (moving backward).
- **Agitated/Crippled:** If it is physically conjunct a natural malefic (like Saturn or Rahu).
If there is no physical stress, it assigns a mood based on **Compound Friendship**:
- **Radiant (Deepta):** Exalted.
- **Confident (Swastha):** Own Sign.
- **Happy (Mudita):** Great Friend's sign.
- **Miserable (Dukhita):** Enemy's sign.

## 4. Lajjitadi Avasthas (Social Behaviors)
**The Concept:** Describes how a planet feels based on the "social pressure" of who is in the room with it, or who is staring at it from across the room.
**The Jyotish Rule:** The software uses **Natural Friendships** (inborn chemistry) and **Rasi Aspects** (whole-sign staring). A planet can have multiple social states at once:
- **Proud (Garvita):** If it is **Exalted** or in its **Moolatrikona** (favorite office).
- **Ashamed (Lajjita):** If it is placed in the 5th house with harsh planets (Rahu, Ketu, Sun, Saturn, Mars).
- **Starved (Kshudhita):** If it is in an Enemy's sign, and an Enemy or Saturn is staring at it.
- **Delighted (Mudita):** If it is in a Friend's sign, and a Friend or Jupiter is staring at it.

## 5. Shayanadi Avasthas (The 12 Activity States & Sub-States)
**The Concept:** Describes what the planet is actively doing in real time (e.g. resting, sitting, eating, dancing, or sleeping) and how actively that activity manifests in the physical world.
**The Jyotish Rule:** The software uses Ernst Wilhelm's exact algorithm combining:
1. `(Planet Nakshatra × Planet Serial × Nakshatra Pada)`
2. `+ Lagna Sign Index + Moon Nakshatra + Ishta Ghati (Elapsed 24-minute ghatis from sunrise)`
3. Modulo 12 produces one of 12 activity states (Shayana to Nidra).
4. Sub-states (**Cheshta**, **Drishti**, **Vicheshta**) determine whether the activity acts with 100%, 50%, or 10% manifestation strength using the sound of the native's first name.
