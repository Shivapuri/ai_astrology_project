# Nakshatra Metadata & Calculation System Specifications

## Overview
This module defines the foundational astronomical and Vedic metadata for the 27 Nakshatras (Lunar Mansions) and establishes the dual-engine calculation architecture for switching between:
1. **`ERNST_DHRUVA`**: Ernst Wilhelm's Dhruva Galactic Center Equatorial Right Ascension method.
2. **`VIC_CHITRA`**: Vic DiCara's Tropical Rasis + Ecliptic Sidereal (Chitra / Lahiri) method.

## Foundational References & Scripture
- **Krishna Yajurveda (Taittiriya Brahmana 3.1 & Taittiriya Samhita 3.5)**: The authoritative Vedic source for the 27 Nakshatra presiding deities (Devatas).
- **Brihat Parashara Hora Shastra (BPHS)**: Chapters 46 & 49 (Vimshottari Dasha periods and rulers) & Chapter 45 (Avasthas).
- **Phaladeepika & Ryan Kurczak / Vic DiCara Vault Teachings**: Psychological subconscious drives and planetary overlords.

## Dual Calculation Engine

### 1. Ernst Wilhelm (`ERNST_DHRUVA`)
- **Philosophy**: Rasis are Tropical (solar/seasonal). Nakshatras represent the stellar backdrop, anchored to the center of the galaxy (Dhruva Galactic Center at middle of Mula, 246°40').
- **Coordinate System**: Planets are projected onto the Celestial Equator via **Right Ascension (RA)**.
- **Vimshottari Balance**: Calculated from the Moon's Sidereal Equatorial Right Ascension.

### 2. Vic DiCara (`VIC_CHITRA`)
- **Philosophy**: Tropical Rasis + Ecliptic Sidereal Nakshatras anchored to Spica (Chitra Paksha / Lahiri).
- **Coordinate System**: Planets are calculated along the **Ecliptic** using Swiss Ephemeris Lahiri Sidereal Mode (`swe.SIDM_LAHIRI` + `swe.FLG_SIDEREAL`).
- **Vimshottari Balance**:
  1. `swe.set_sid_mode(swe.SIDM_LAHIRI)`
  2. `moon_sidereal_lon = swe.calc_ut(jd, swe.MOON, swe.FLG_SWIEPH | swe.FLG_SIDEREAL)[0]`
  3. `nak_idx = int(moon_sidereal_lon / 13.333333333) % 27`
  4. `fraction_passed = (moon_sidereal_lon % 13.333333333) / 13.333333333`
  5. `fraction_left = 1.0 - fraction_passed`
  6. Standard Vimshottari Mahadasha balance and Antardashas are calculated from this balance.

## Master Graha Diagnostics Integration
Each planet in the Master Graha Diagnostics table displays a clean 2-line badge:
- **Line 1**: `✨ [Nakshatra Name] ([Deity])`
- **Line 2**: `↳ Overlord: [Nakshatra Ruler]`
- **Hover Tooltip**: Monospace receipt breakdown of Deity, Overlord, Nature, and Core Drive.
