# Astra Calculation Hierarchy & Mathematical Workflow

Because astrological mathematics are highly interdependent (e.g., you cannot calculate Lajjitadi Avasthas without first knowing Planetary Aspects, and you cannot know Aspects without Longitudes), the backend logic must strictly follow this Directed Acyclic Graph (DAG) hierarchy.

## The Hierarchy

### Level 1: Core Astronomy (The Swiss Ephemeris Foundation)
Everything is built on pure astronomical data. **Do not hardcode anything.**
*   **Geocentric Longitudes** (Tropically anchored)
*   **Declinations & Latitudes**
*   **Speed/Motion** (Direct, Retrograde, Stationary)
*   *Calculated via:* `swisseph` calls in `jyotish/generate_jyotish.py`.

### Level 2: Chart Foundations
*   **House Cusps & Bhavas:** Using the Campanus system.
*   **Nakshatras:** Using Sidereal Equatorial calculations anchored to the Dhruva Galactic Center.
*   **Ayanamsa:** Applied only to Nakshatra calculations (and related Dasa systems), not to Rasis.

### Level 3: Vargas (Divisional Charts) & Dignity
*   **D1 through D60 Calculations:** Deriving specific signs for every planet in every Varga based on their Tropical D1 longitude.
*   **Sign Lords & Dispositors:** Establishing who rules what.
*   **Dignities:** Determining Exaltation, Moolatrikona, Own Sign, Enemy Sign, Debilitation.

### Level 4: Relationships & Aspects
*   **Planetary Relationships:**
    *   *Naisargika* (Natural Friendship based on BPHS rules).
    *   *Tatkalika* (Temporary Friendship based on chart placement).
    *   *Panchadha* (Compound Friendship).
*   **Drishti (Aspects):**
    *   *Rasi Drishti* (Sign aspects).
    *   *Graha Drishti* (Planetary longitude aspects in Virupas 0-60).

### Level 5: Strengths (Balas)
*   **Bhava Bala:** House strengths.
*   **Graha Bala (Shadbala):** The six-fold strength of planets.
    *   Positional (Sthana Bala)
    *   Directional (Dig Bala)
    *   Temporal (Kala Bala)
    *   Motortional (Cheshta Bala)
    *   Natural (Naisargika Bala)
    *   Aspectual (Drik Bala)
*   *Sources of Truth:* `Vedic Astrology An Integrated Approach.pdf` and `Bhava and Graha Balas.pdf` (in `/source-material/software-setup/`).

### Level 6: Advanced States (Avasthas)
These are the final calculations because they depend heavily on Levels 3, 4, and 5.
*   **Jagradadi & Baladi Avasthas:** Evaluated dynamically per Varga to determine multiplier states (Alertness & Age).
*   **Shayanadi Avasthas:** Based on Nakshatra, Navamsa, and planetary combinations.
*   **Lajjitadi Avasthas:** The quantitative interaction matrix (Garvita, Mudita, Lajjita, Kshobhita, Kshudhita, Trushita).
    *   *Dependency Check:* Lajjitadi Avasthas require the Base Strength from Shadbala (Level 5), Natural Friendship (Level 4), and Graha Drishti aspects (Level 4).

## Rule Framework for Testing & Development
1.  **Scriptural Verification:** If a mathematical test fails, do not arbitrarily change the formula. Cross-reference the formula with BPHS (Chapters 41-50) first.
2.  **Test-Driven Development (TDD):** Use the provided JSON/CSV baseline matrices in `sample-case/` to write Pytest assertions.
3.  **No Faking:** If a test requires a complex intermediate value (like Ishta Phala), calculate it via the ephemeris pipeline. Do not mock or hardcode the output to pass a test.
