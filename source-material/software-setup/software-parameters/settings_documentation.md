# Astra Astrological Software - Foundational Settings

This document outlines the exact foundational calculation parameters derived from the reference setup screenshots. This ensures all custom calculations in the `astra` project align perfectly with the target methodology (Ernst Wilhelm's Kala / Tropical-Sidereal hybrid).

## 1. Zodiac, Ayanamsa & Nakshatras
*   **Zodiac (Signs/Rasis):** Tropical (Used for all basic placements, Vargas, Aspects, and Yogas).
*   **Ayanamsa:** Dhruva Galactic Center, Middle of Mula.
*   **Nakshatra System:** Sidereal Equatorial (Calculated using the Dhruva Equatorial Longitude).
    *   *Note:* The software explicitly checks "Use Tropical Rasis with the Above Ayanamsa For Nakshatras."
*   **Number of Nakshatras:** 28 Nakshatras (Short Abhijit).

## 2. House System
*   **House Calculation:** Campanus.
*   **House Cusp Definition:** Middle of House (The cusp degree represents the center of the house, not the beginning).

## 3. Planetary Calculations & Ephemeris
*   **Node:** True Node (for Rahu/Ketu).
*   **Planetary Positions:** Geocentric.
*   **Combustion:** Surya Siddhanta / Varaha Mihira Method.
*   **Sunrise Calculation:** Hindu.
*   **Fatal Degree of the Moon:** Phaladeepika.

## 4. Varga (Divisional) Calculations
*   **Trimsamsa (D30):** Rasi / 30° method.
*   **Dasamsa (D10):** Parashara - Reverse for Even Rasis.
*   **Chaturvimsamsa (D24):** Parashara - Reverse for Even Rasis.
*   **Ashtakavarga:** Parashara.

## 5. Dasa Systems
*   **Year Length (Nakshatra & Rasi Dasas):** Saura (365.2422 days - based on the Surya Siddhanta).
*   **Nakshatra Dasa Start:** Calculated from the Moon.
*   **Rasi Dasa Lengths:** Rasi-Based.
*   **Adarsa Rasi for Charanvamsa Dasa:** Cancer -> Aquarius; Capricorn -> Leo.

## 6. Jaimini Parameters
*   **Rasi Aspects:** Astronomically Correct.
*   **Jaimini Karakas:** Use Lagna as the 8th Karaka.
*   **Yogada Table:** Use Parivritti Drekkana.

## 7. Advanced Avasthas & Yogas
*   **Avasthas & Yoga Judgement:** Evaluated using Planetary Aspects and Conjunctions based on the **Rasi** chart (not Vargas).
*   **Search Yogas With:** Rasi Aspects.
*   **Temporal Friendships:** Derived from the Rasi Chart.
*   **Mundane Sankrantis:** Saura (according to Surya Siddhanta).
*   **Muhurta (Tithyamsa):** As Part of Tithi.
*   **Vara / Hora / Nadika:** Calculated for Yamakoti (Ancient Prime Meridian).
*   **PranaPada / Bhava / Hora / Ghatika Lagna:** Calculated for Yamakoti.

## 8. Balas & Dignities
*   **Debilitation Limits:** 
    *   Moon: 0-3° Scorpio.
    *   Mercury: 0-15° Pisces.
*   **Varsha Pati Calculation:** Use Exact Aspectual Value.
*   **Pindaadi Ayurdaya:** Uses Bhava Chalita.
*   **Gulika:** Calculated from the beginning of the portion.
