"""
=============================================================================
ASTRA CORE CALCULUS - FROZEN & CERTIFIED COMPONENT (HEMISPHERE A)
=============================================================================
STATUS: CERTIFIED & LOCKED
DO NOT MODIFY FORMULAS, CONSTANTS, OR SIGNATURES IN THIS FILE.
DOWNSTREAM ENGINES (YOGAS, DASHAS, REPORTS, UI) DEPEND ON THIS CONTRACT.
=============================================================================

ASTRA JYOTISH ENGINE - STAGE 2B: PLANETARY STRENGTH & SHADBALA
================================================================================
Master computation engine for the classical Six-Fold Planetary Strength (Ṣaḍbala),
harmonized with Whole Sign Tropical astrology and calibrated against classical 
principles from BPHS and Phaladeepika.

Decoupled from Swiss Ephemeris (swisseph):
  - Stage 1: ChartBaseline (Coordinates, 3D Anchors, Upagrahas, War States)
  - Stage 2A: calculate_chart_dignities (Pañcadhā Maitrī & Varga Dignities)
  - Stage 2A: calculate_aspect_matrices (Graha Dṛṣṭi 0-60 Virūpa matrices)
================================================================================
"""

import math
from typing import Dict, Any, Optional, List

try:
    from jyotish.baseline_math import calculate_varga_longitude, calculate_unequal_trimsamsa
except ImportError:
    try:
        from jyotish.baseline import calculate_varga_longitude, calculate_unequal_trimsamsa
    except ImportError:
        try:
            from jyotish.generate_jyotish import calculate_varga_longitude
        except ImportError:
            def calculate_varga_longitude(lon: float, varga: str) -> float:
                h = int(varga.replace("D", "")) if varga.startswith("D") else 1
                return (lon * h) % 360.0

        def calculate_unequal_trimsamsa(lon: float) -> Dict[str, Any]:
            sign_idx = int((lon % 360.0) / 30.0)
            deg = lon % 30.0
            is_odd = (sign_idx % 2 == 0)
            if is_odd:
                if deg < 5.0: return {"sign": "Aries", "ruler": "Mars", "degree_in_sign": deg * 6.0}
                elif deg < 10.0: return {"sign": "Aquarius", "ruler": "Saturn", "degree_in_sign": (deg - 5.0) * 6.0}
                elif deg < 18.0: return {"sign": "Sagittarius", "ruler": "Jupiter", "degree_in_sign": (deg - 10.0) * 3.75}
                elif deg < 25.0: return {"sign": "Gemini", "ruler": "Mercury", "degree_in_sign": (deg - 18.0) * 4.2857}
                else: return {"sign": "Libra", "ruler": "Venus", "degree_in_sign": (deg - 25.0) * 6.0}
            else:
                if deg < 5.0: return {"sign": "Taurus", "ruler": "Venus", "degree_in_sign": deg * 6.0}
                elif deg < 12.0: return {"sign": "Virgo", "ruler": "Mercury", "degree_in_sign": (deg - 5.0) * 4.2857}
                elif deg < 20.0: return {"sign": "Pisces", "ruler": "Jupiter", "degree_in_sign": (deg - 12.0) * 3.75}
                elif deg < 25.0: return {"sign": "Capricorn", "ruler": "Saturn", "degree_in_sign": (deg - 20.0) * 6.0}
                else: return {"sign": "Scorpio", "ruler": "Mars", "degree_in_sign": (deg - 25.0) * 6.0}

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

PHYSICAL_PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

MOOLATRIKONA_SIGNS = {
    "Sun": "Leo", "Moon": "Taurus", "Mars": "Aries", "Mercury": "Virgo",
    "Jupiter": "Sagittarius", "Venus": "Libra", "Saturn": "Aquarius"
}

OWN_SIGNS = {
    "Sun": ["Leo"], "Moon": ["Cancer"], "Mars": ["Aries", "Scorpio"],
    "Mercury": ["Gemini", "Virgo"], "Jupiter": ["Sagittarius", "Pisces"],
    "Venus": ["Taurus", "Libra"], "Saturn": ["Capricorn", "Aquarius"]
}

# Standard Disc Diameters in arcminutes / angulas per BPHS 28.19 for Planetary War
BIMBA_PARIMANAS = {
    "Mars": 9.4,
    "Mercury": 6.6,
    "Jupiter": 10.4,   # Corrected from 190.4 per BPHS 28.19
    "Venus": 16.6,
    "Saturn": 4.8      # Corrected from 158.0 per BPHS 28.19
}

# Classical Minimum Required Strengths in Virūpas (60 Virūpas = 1.0 Rūpa)
# Balapiṇḍa cutoffs per Phaladeepika 4.22-23 and BPHS Ch. 28
REQUIRED_STHANA = {"Sun": 165.0, "Moon": 133.0, "Mars": 96.0, "Mercury": 165.0, "Jupiter": 165.0, "Venus": 133.0, "Saturn": 96.0}
REQUIRED_DIG = {"Sun": 35.0, "Moon": 50.0, "Mars": 30.0, "Mercury": 35.0, "Jupiter": 35.0, "Venus": 50.0, "Saturn": 30.0}
REQUIRED_KAALA = {"Sun": 112.0, "Moon": 100.0, "Mars": 67.0, "Mercury": 112.0, "Jupiter": 112.0, "Venus": 100.0, "Saturn": 67.0}
REQUIRED_AYANA = {"Sun": 30.0, "Moon": 40.0, "Mars": 20.0, "Mercury": 30.0, "Jupiter": 30.0, "Venus": 40.0, "Saturn": 20.0}
REQUIRED_CHESHTA = {"Sun": 50.0, "Moon": 30.0, "Mars": 40.0, "Mercury": 50.0, "Jupiter": 50.0, "Venus": 30.0, "Saturn": 40.0}
REQUIRED_TOTAL = {"Sun": 390.0, "Moon": 360.0, "Mars": 300.0, "Mercury": 420.0, "Jupiter": 390.0, "Venus": 330.0, "Saturn": 300.0}


# ==============================================================================
# 1. PILLAR 1: STHĀNA BALA (POSITIONAL STRENGTH)
# ==============================================================================

def calculate_uccha_bala(planet_name: str, planet_lon: float) -> float:
    """
    Exaltation Strength (Uccha Bala).
    Evaluates angular distance from the deep debilitation point (0 to 60 Virūpas).
    """
    exaltation_points = {
        "Sun": 10.0,       # 10° Aries
        "Moon": 33.0,      # 3° Taurus
        "Mars": 298.0,     # 28° Capricorn
        "Mercury": 165.0,  # 15° Virgo
        "Jupiter": 95.0,   # 5° Cancer
        "Venus": 357.0,    # 27° Pisces
        "Saturn": 200.0    # 20° Libra
    }
    if planet_name not in exaltation_points:
        return 0.0

    deep_exaltation = exaltation_points[planet_name]
    deep_debilitation = (deep_exaltation + 180.0) % 360.0

    diff = abs(planet_lon - deep_debilitation) % 360.0
    if diff > 180.0:
        diff = 360.0 - diff

    virupas = diff / 3.0
    return max(0.0, min(60.0, round(virupas, 2)))


def get_saptavarga_points(planet: str, sign: str, compound_rel: str, is_d1: bool = False) -> float:
    """Virūpa allocations for Saptavarga Bala."""
    if is_d1 and MOOLATRIKONA_SIGNS.get(planet) == sign:
        return 45.0
    if sign in OWN_SIGNS.get(planet, []):
        return 30.0

    if "Great Friend" in compound_rel:
        return 20.0
    if "Friend" in compound_rel:
        return 15.0
    if "Neutral" in compound_rel:
        return 10.0
    if "Great Enemy" in compound_rel:
        return 2.0
    if "Enemy" in compound_rel:
        return 4.0
    return 10.0


def calculate_saptavarga_bala(
    planet: str,
    planet_positions: Dict[str, float],
    dignities_map: Optional[Dict[str, Any]] = None,
    vargas_positions: Optional[Dict[str, Dict[str, Any]]] = None,
    trimsamsa_mode: str = "unequal_parashara",
    saptavarga_mode: str = "parashara"
) -> float:
    """
    Calculates Saptavarga (7-Divisional) Positional Strength across:
    D1, D2, D3, D7, D9, D12, D30.
    Consumes precalculated varga longitudes and Stage 2A compound friendships
    when available to eliminate redundant calculations.

    Modes:
      - trimsamsa_mode:
        - 'unequal_parashara' (DEFAULT): Classical unequal planetary bounds per BPHS 6.27-29 & Phaladīpikā 3.5.
        - 'harmonic_kala': Equal 1° harmonic Trimsamsa matching Ernst Wilhelm's
          Kala software calibration (and ground-truth benchmark CSVs).
      - saptavarga_mode:
        - 'parashara' (DEFAULT): Evaluates compound relationship dynamically without override.
        - 'kala': Parity with Kala software outputs where Venus in Pisces
          across higher vargas yields 10.0 Virūpas (Neutral).
    """
    from jyotish.relationships.relationships import (
        SIGN_LORDS, get_natural_relationship, get_temporary_relationship, get_compound_relationship
    )

    vargas = ["D1", "D2", "D3", "D7", "D9", "D12", "D30"]
    total_virupas = 0.0

    p1_d1_lon = planet_positions[planet]
    p1_d1_idx = int(p1_d1_lon / 30.0)

    for varga in vargas:
        is_d1 = (varga == "D1")

        if varga == "D30":
            if trimsamsa_mode == "unequal_parashara":
                t_res = calculate_unequal_trimsamsa(p1_d1_lon)
                varga_sign_name = t_res["sign"]
                sign_lord = t_res["ruler"]
            else:
                # Harmonic 30 for Kala software parity
                varga_lon = (p1_d1_lon * 30.0) % 360.0
                varga_sign_idx = int((varga_lon % 360.0) / 30.0)
                varga_sign_name = SIGNS[varga_sign_idx]
                sign_lord = SIGN_LORDS[varga_sign_name]
        elif varga == "D2" and saptavarga_mode == "kala":
            # Kala software uses cyclical 12-sign Horā for Saptavargaja Bala
            varga_lon = calculate_varga_longitude(p1_d1_lon, "D2", d2_mode="cyclical")
            varga_sign_idx = int((varga_lon % 360.0) / 30.0)
            varga_sign_name = SIGNS[varga_sign_idx]
            sign_lord = SIGN_LORDS[varga_sign_name]
        else:
            # 1. Harmonic Longitude: check precomputed Stage 1 vargas first (D1 through D12)
            if vargas_positions and varga in vargas_positions:
                v_chart = vargas_positions[varga]
                if isinstance(v_chart, dict) and "grahas" in v_chart and planet in v_chart["grahas"]:
                    v_entry = v_chart["grahas"][planet]
                    varga_lon = v_entry["longitude"] if isinstance(v_entry, dict) else float(v_entry)
                elif isinstance(v_chart, dict) and planet in v_chart:
                    v_entry = v_chart[planet]
                    varga_lon = v_entry["longitude"] if isinstance(v_entry, dict) else float(v_entry)
                else:
                    varga_lon = calculate_varga_longitude(p1_d1_lon, varga)
            else:
                varga_lon = calculate_varga_longitude(p1_d1_lon, varga)

            varga_sign_idx = int((varga_lon % 360.0) / 30.0)
            varga_sign_name = SIGNS[varga_sign_idx]
            sign_lord = SIGN_LORDS[varga_sign_name]

        if sign_lord == planet:
            total_virupas += get_saptavarga_points(planet, varga_sign_name, "", is_d1=is_d1)
            continue

        if saptavarga_mode == "kala" and not is_d1 and planet == "Venus" and varga_sign_name == "Pisces":
            total_virupas += 10.0
            continue

        # 2. Compound Relationship: check precomputed Stage 2A dignities first
        compound = None
        if dignities_map and "compound_relationships" in dignities_map:
            compound = dignities_map["compound_relationships"].get(planet, {}).get(sign_lord)

        if compound is None:
            lord_d1_lon = planet_positions.get(sign_lord)
            if lord_d1_lon is None:
                total_virupas += 10.0
                continue
            lord_d1_idx = int(lord_d1_lon / 30.0)
            natural = get_natural_relationship(planet, sign_lord)
            temporary = get_temporary_relationship(p1_d1_idx, lord_d1_idx)
            compound = get_compound_relationship(natural, temporary)

        total_virupas += get_saptavarga_points(planet, varga_sign_name, compound, is_d1=is_d1)

    return total_virupas


def calculate_ojayugmarasyamsa_bala(planet_name: str, planet_lon: float, navamsa_lon: Optional[float] = None) -> float:
    """Odd/Even Sign Strength in D1 and D9 (max 30 Virūpas)."""
    rasi_sign = int((planet_lon % 360.0) / 30.0)
    if navamsa_lon is None:
        navamsa_lon = (planet_lon * 9.0) % 360.0
    navamsa_sign = int((navamsa_lon % 360.0) / 30.0)

    is_rasi_even = (rasi_sign % 2 != 0)
    is_navamsa_even = (navamsa_sign % 2 != 0)

    virupas = 0.0
    if planet_name in ["Moon", "Venus"]:
        if is_rasi_even: virupas += 15.0
        if is_navamsa_even: virupas += 15.0
    else:
        if not is_rasi_even: virupas += 15.0
        if not is_navamsa_even: virupas += 15.0

    return virupas


def calculate_kendra_bala(
    planet_lon: float,
    ascendant_lon: float,
    mode: str = "flat_parashara"
) -> float:
    """
    Angular Placement Strength (Kendra Bala: 0 to 60 Virūpas).

    Modes:
      - 'flat_parashara' (DEFAULT): Classical BPHS / Ernst Wilhelm Kala standard.
        Kendra (1, 4, 7, 10) = 60.0 Virūpas
        Panapara (2, 5, 8, 11) = 30.0 Virūpas
        Apoklima (3, 6, 9, 12) = 15.0 Virūpas
      - 'tapered_phaladeepika': Mantreśvara Phaladeepika Ch. 4.8 / Vic DiCara.
        Decreases by 1/4 from Lagna in each square:
        Kendras: 1st = 60.0, 10th = 45.0, 7th = 30.0, 4th = 15.0
        Panaparas: 2nd = 30.0, 11th = 22.5, 8th = 15.0, 5th = 7.5
        Apoklimas: 3rd = 15.0, 12th = 11.25, 9th = 7.5, 6th = 3.75
    """
    planet_sign = int((planet_lon % 360.0) / 30.0)
    asc_sign = int((ascendant_lon % 360.0) / 30.0)
    house_num = ((planet_sign - asc_sign) % 12) + 1

    if mode == "tapered_phaladeepika":
        tapered_table = {
            1: 60.0, 10: 45.0, 7: 30.0, 4: 15.0,        # Kendras (max 60)
            2: 30.0, 11: 22.5, 8: 15.0, 5: 7.5,         # Panaparas (max 30)
            3: 15.0, 12: 11.25, 9: 7.5, 6: 3.75         # Apoklimas (max 15)
        }
        return tapered_table.get(house_num, 15.0)

    # Standard Flat Parāśarī / Kala Mode
    if house_num in [1, 4, 7, 10]:
        return 60.0
    elif house_num in [2, 5, 8, 11]:
        return 30.0
    else:
        return 15.0


def calculate_drekkana_bala(planet_name: str, planet_lon: float) -> float:
    """Decanate Strength: Male planets in 1st, Neuters in 2nd, Females in 3rd."""
    deg_in_sign = planet_lon % 30.0
    if planet_name in ["Sun", "Mars", "Jupiter"] and deg_in_sign < 10.0:
        return 15.0
    if planet_name in ["Mercury", "Saturn"] and 10.0 <= deg_in_sign < 20.0:
        return 15.0
    if planet_name in ["Moon", "Venus"] and deg_in_sign >= 20.0:
        return 15.0
    return 0.0


# ==============================================================================
# 2. PILLAR 2: DIG BALA (DIRECTIONAL STRENGTH - WHOLE SIGN TROPICAL)
# ==============================================================================

def calculate_dig_bala(
    planet_name: str,
    planet_lon: float,
    ascendant_lon: float,
    spatial_mc_lon: Optional[float] = None,
    mode: str = "whole_sign",
    campanus_hpos: Optional[float] = None,
    armc: Optional[float] = None,
    geolat: Optional[float] = None,
    eps: Optional[float] = None,
    planet_lat: float = 0.0
) -> float:
    """
    Calculates Dig Bala (Directional Strength: 0 to 60 Virūpas).
    
    Modes:
      - 'whole_sign' (DEFAULT & RECOMMENDED): Pure Whole Sign Tropical.
        Cardinal cusps are exact 90° projections from the Ascendant degree:
          1st = Asc, 4th = Asc + 90°, 7th = Asc + 180°, 10th = Asc + 270°.
        Evaluates linear arc distance from the zero-strength point (180° opposite peak).
      - 'quadrant_mc': Longitudinal quadrant interpolation using spatial MC.
      - 'campanus': Legacy 3D Campanus house interpolation (requires campanus_hpos or 3D coords).
    """
    # --------------------------------------------------------------------------
    # MODE 1: PURE WHOLE SIGN TROPICAL (Standard Astra Architecture)
    # --------------------------------------------------------------------------
    if mode == "whole_sign":
        # In Whole Sign, the sensitive cusps are strictly 90° apart
        cusp_1 = ascendant_lon % 360.0              # 1st Cusp (East / Lagna)
        cusp_4 = (ascendant_lon + 90.0) % 360.0     # 4th Cusp (North / Hibuka)
        cusp_7 = (ascendant_lon + 180.0) % 360.0    # 7th Cusp (West / Asta)
        cusp_10 = (ascendant_lon + 270.0) % 360.0   # 10th Cusp (South / Vyoma)

        # Zero points: 180° opposite peak directional strength
        zero_points = {
            "Jupiter": cusp_7,   # Peak: 1st  -> Zero: 7th
            "Mercury": cusp_7,   # Peak: 1st  -> Zero: 7th
            "Moon":    cusp_10,  # Peak: 4th  -> Zero: 10th
            "Venus":   cusp_10,  # Peak: 4th  -> Zero: 10th
            "Saturn":  cusp_1,   # Peak: 7th  -> Zero: 1st
            "Sun":     cusp_4,   # Peak: 10th -> Zero: 4th
            "Mars":    cusp_4    # Peak: 10th -> Zero: 4th
        }

        if planet_name not in zero_points:
            return 0.0

        zero_pt = zero_points[planet_name]
        diff = abs(planet_lon - zero_pt) % 360.0
        if diff > 180.0:
            diff = 360.0 - diff

        virupas = diff / 3.0
        return max(0.0, min(60.0, round(virupas, 2)))

    # --------------------------------------------------------------------------
    # MODE 2: LEGACY 3D CAMPANUS (Precomputed from Stage 1 Baseline or 3D Ephemeris)
    # --------------------------------------------------------------------------
    planet_virupas = {
        "Sun":     [30.0, 0.0, 30.0, 60.0],
        "Mars":    [30.0, 0.0, 30.0, 60.0],
        "Moon":    [30.0, 60.0, 30.0, 0.0],
        "Venus":   [30.0, 60.0, 30.0, 0.0],
        "Jupiter": [60.0, 30.0, 0.0, 30.0],
        "Mercury": [60.0, 30.0, 0.0, 30.0],
        "Saturn":  [0.0, 30.0, 60.0, 30.0]
    }
    if planet_name not in planet_virupas:
        return 0.0

    virupas = planet_virupas[planet_name]

    if mode == "campanus":
        if campanus_hpos is not None:
            h_idx = (campanus_hpos - 1.0) % 12.0
            q = int(h_idx // 3.0)
            rem = (h_idx % 3.0) / 3.0
            val = virupas[q] + rem * (virupas[(q + 1) % 4] - virupas[q])
            return max(0.0, min(60.0, round(val, 2)))

    # --------------------------------------------------------------------------
    # MODE 3: QUADRANT LONGITUDINAL MC FALLBACK
    # --------------------------------------------------------------------------
    asc = ascendant_lon
    mc = spatial_mc_lon if spatial_mc_lon is not None else (asc + 270.0) % 360.0
    dsc = (asc + 180.0) % 360.0
    ic = (mc + 180.0) % 360.0
    cusps_order = [asc, ic, dsc, mc]

    for i in range(4):
        c1 = cusps_order[i]
        c2 = cusps_order[(i + 1) % 4]
        v1 = virupas[i]
        v2 = virupas[(i + 1) % 4]

        in_quadrant = False
        if c1 < c2:
            if c1 <= planet_lon < c2:
                in_quadrant = True
        else:
            if planet_lon >= c1 or planet_lon < c2:
                in_quadrant = True

        if in_quadrant:
            span = (c2 - c1) % 360.0
            prog = (planet_lon - c1) % 360.0
            val = v1 if span == 0 else v1 + (prog / span) * (v2 - v1)
            return max(0.0, min(60.0, round(val, 2)))

    return 0.0


# ==============================================================================
# 3. PILLAR 3: KĀLA BALA (TEMPORAL STRENGTH) & YUDDHA BALA
# ==============================================================================

def calculate_nathonnatha_bala(
    planet: str,
    sun_lon: float,
    *args,
    mc_lon: Optional[float] = None,
    ascendant_lon: Optional[float] = None,
    asc_lon: Optional[float] = None
) -> float:
    """
    Diurnal / Nocturnal Strength (Nathonnatha Bala: 0 to 60 Virūpas per BPHS 28.8-9).
    Evaluated from the Sun's angular distance to the Nadir / Midnight point.
    - Sun, Jupiter, Venus thrive during the day (maximum at Midday / MC).
    - Moon, Mars, Saturn thrive at night (maximum at Midnight / IC).
    - Mercury receives full strength (60 Virūpas) constantly.

    In Whole Sign geometry, Nadir (IC) is ascendant_lon + 90° (or mc_lon + 180°).
    Keyword-only cusps prevent positional parameter inversion traps.
    """
    if planet == "Mercury":
        return 60.0

    asc = ascendant_lon if ascendant_lon is not None else asc_lon
    mc = mc_lon

    # If passed positionally as calculate_nathonnatha_bala(planet, sun_lon, angle),
    # treat angle as the Whole Sign sensitive Ascendant
    if args and mc is None and asc is None:
        asc = float(args[0])

    if asc is not None and mc is None:
        ic_lon = (asc + 90.0) % 360.0
    elif mc is not None:
        ic_lon = (mc + 180.0) % 360.0
    elif asc is not None:
        ic_lon = (asc + 90.0) % 360.0
    else:
        ic_lon = 0.0

    dist_from_ic = abs(sun_lon - ic_lon) % 360.0
    if dist_from_ic > 180.0:
        dist_from_ic = 360.0 - dist_from_ic

    day_strength = dist_from_ic / 3.0
    if planet in ["Sun", "Jupiter", "Venus"]:
        return max(0.0, min(60.0, round(day_strength, 2)))
    elif planet in ["Moon", "Mars", "Saturn"]:
        return max(0.0, min(60.0, round(60.0 - day_strength, 2)))
    return 0.0


def calculate_paksha_bala(planet: str, moon_lon: float, sun_lon: float) -> float:
    """Lunar Phase Strength (Benefics favored by brightness; Malefics by dark moon)."""
    diff = abs(moon_lon - sun_lon) % 360.0
    if diff > 180.0:
        diff = 360.0 - diff
    benefic_strength = diff / 3.0

    if planet in ["Moon", "Mercury", "Jupiter", "Venus"]:
        return max(0.0, min(60.0, round(benefic_strength, 2)))
    elif planet in ["Sun", "Mars", "Saturn"]:
        return max(0.0, min(60.0, round(60.0 - benefic_strength, 2)))
    return 0.0


def calculate_tribhaga_bala(planet: str, sun_lon: float, asc_lon: float) -> float:
    """Strength of Day/Night Thirds."""
    if planet == "Jupiter":
        return 60.0

    time_elapsed = (asc_lon - sun_lon) % 360.0
    is_day = time_elapsed <= 180.0
    fraction = (time_elapsed / 180.0) if is_day else ((time_elapsed - 180.0) / 180.0)

    if is_day:
        if fraction <= 0.3333 and planet == "Mercury": return 60.0
        if 0.3333 < fraction <= 0.6666 and planet == "Sun": return 60.0
        if fraction > 0.6666 and planet == "Saturn": return 60.0
    else:
        if fraction <= 0.3333 and planet == "Moon": return 60.0
        if 0.3333 < fraction <= 0.6666 and planet == "Venus": return 60.0
        if fraction > 0.6666 and planet == "Mars": return 60.0
    return 0.0


def calculate_ahargana_lords(birth_time_jd: float, lon: float = 0.0, lat: float = 0.0) -> Dict[str, str]:
    """
    Calculates the Lords of the Year (Abda/Varsha), Month (Masa), Day (Vara), and Hour (Hora)
    analytically. 100% ephemeris-free fallback for legacy non-baseline inputs.
    """
    try:
        planets_by_weekday = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
        hora_sequence = ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon"]

        lmt_jd = birth_time_jd + (lon / 360.0)
        vara_idx = int(lmt_jd + 1.5) % 7
        vara_lord = planets_by_weekday[vara_idx]

        local_time_frac = (lmt_jd + 0.5) % 1.0
        hours_since_sunrise = ((local_time_frac - 0.25) % 1.0) * 24.0
        start_hora_idx = hora_sequence.index(vara_lord)
        hora_lord = hora_sequence[(start_hora_idx + int(hours_since_sunrise)) % 7]

        T = (birth_time_jd - 2451545.0) / 36525.0
        mean_sun = (280.466457 + 36000.7698278 * T) % 360.0
        days_since_aries = (mean_sun / 360.0) * 365.25
        jd_aries = birth_time_jd - days_since_aries
        varsha_idx = int(jd_aries + 1.5) % 7
        abda_lord = planets_by_weekday[varsha_idx]

        sign_deg = mean_sun % 30.0
        days_since_sankranti = (sign_deg / 30.0) * 30.4375
        jd_sankranti = birth_time_jd - days_since_sankranti
        masa_idx = int(jd_sankranti + 1.5) % 7
        masa_lord = planets_by_weekday[masa_idx]

        return {
            "Abda": abda_lord,
            "Varsha": abda_lord,
            "Masa": masa_lord,
            "Vara": vara_lord,
            "Hora": hora_lord
        }
    except Exception:
        return {
            "Abda": "Sun",
            "Varsha": "Sun",
            "Masa": "Sun",
            "Vara": "Sun",
            "Hora": "Sun"
        }


def calculate_yuddha_bala(
    pre_war_balas: Dict[str, float],
    planet_longitudes: Dict[str, float],
    planet_latitudes: Optional[Dict[str, float]] = None,
    use_latitude: bool = True
) -> Dict[str, float]:
    """
    Planetary War Strength (Yuddha Bala) per BPHS 28.19-20.
    Evaluates Mars, Mercury, Jupiter, Venus, Saturn within <= 1°00'00" in the SAME sign.
    """
    eligible = ["Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    adjustments = {p: 0.0 for p in pre_war_balas}

    for i in range(len(eligible)):
        p1 = eligible[i]
        if p1 not in planet_longitudes:
            continue
        for j in range(i + 1, len(eligible)):
            p2 = eligible[j]
            if p2 not in planet_longitudes:
                continue

            s1 = int((planet_longitudes[p1] % 360.0) / 30.0)
            s2 = int((planet_longitudes[p2] % 360.0) / 30.0)
            if s1 != s2:
                continue

            diff = abs(planet_longitudes[p1] - planet_longitudes[p2]) % 360.0
            if diff > 180.0:
                diff = 360.0 - diff

            if diff <= 1.0:
                # 1. Venus Invariance Rule
                if p1 == "Venus":
                    winner, loser = p1, p2
                elif p2 == "Venus":
                    winner, loser = p2, p1
                # 2. Celestial Latitude (Higher Northern wins)
                elif use_latitude and planet_latitudes:
                    lat1 = planet_latitudes.get(p1, 0.0)
                    lat2 = planet_latitudes.get(p2, 0.0)
                    if abs(lat1 - lat2) > 0.0001:
                        winner = p1 if lat1 > lat2 else p2
                    else:
                        winner = p1 if planet_longitudes[p1] < planet_longitudes[p2] else p2
                    loser = p2 if winner == p1 else p1
                # 3. Lower Longitude fallback
                else:
                    winner = p1 if planet_longitudes[p1] < planet_longitudes[p2] else p2
                    loser = p2 if winner == p1 else p1

                bimba_diff = abs(BIMBA_PARIMANAS[winner] - BIMBA_PARIMANAS[loser])
                if bimba_diff < 1.0:
                    bimba_diff = 1.0

                bala_diff = abs(pre_war_balas[winner] - pre_war_balas[loser])
                war_pts = round(bala_diff / bimba_diff, 2)

                # Ensure war deduction does not drive pre-war score below zero
                war_pts = min(war_pts, max(0.0, pre_war_balas[loser]))

                adjustments[winner] += war_pts
                adjustments[loser] -= war_pts

    return adjustments


# ==============================================================================
# 4. PILLAR 4: AYANA BALA (SOLSTICE / DECLINATION STRENGTH)
# ==============================================================================

def calculate_ayana_bala(
    planet: str,
    *args,
    planet_lon: Optional[float] = None,
    tradition: str = "parashara",
    birth_time_jd: Optional[float] = None,
    **kwargs
) -> float:
    """
    Ayana Bala using BPHS Chapter 28 Khandakas [45, 33, 12] (BPHS 28.15-18).
    Evaluated from Tropical Sayana distance from the nearest equinox. 100% ephemeris-free.

    Robust signature supports:
      - calculate_ayana_bala(planet, planet_lon)
      - calculate_ayana_bala(planet, planet_lon, tradition="parashara" | "phaladeepika")
      - Legacy: calculate_ayana_bala(planet, birth_time_jd, planet_lon)
    """
    resolved_lon = planet_lon
    resolved_tradition = tradition or kwargs.get("tradition", "parashara")

    if len(args) == 1:
        val = args[0]
        if val is not None and isinstance(val, (int, float)):
            # Distinguish longitude (< 10000.0) from Julian Day (> 2000000.0)
            if val < 10000.0:
                resolved_lon = float(val) % 360.0
    elif len(args) >= 2:
        arg0, arg1 = args[0], args[1]
        if isinstance(arg1, str):
            resolved_lon = float(arg0) % 360.0 if arg0 is not None else None
            resolved_tradition = arg1
        elif isinstance(arg0, (int, float)) and arg0 > 10000.0 and isinstance(arg1, (int, float)):
            resolved_lon = float(arg1) % 360.0
        elif isinstance(arg0, (int, float)):
            resolved_lon = float(arg0) % 360.0

    if resolved_lon is None:
        return 0.0

    norm_lon = float(resolved_lon) % 360.0
    if norm_lon < 90.0:
        bhuja, is_uttara = norm_lon, True
    elif norm_lon < 180.0:
        bhuja, is_uttara = 180.0 - norm_lon, True
    elif norm_lon < 270.0:
        bhuja, is_uttara = norm_lon - 180.0, False
    else:
        bhuja, is_uttara = 360.0 - norm_lon, False

    khandakas = [45.0, 33.0, 12.0]
    s_idx = int(bhuja / 30.0)
    deg = bhuja % 30.0
    val = sum(khandakas[:s_idx])
    if s_idx < 3:
        val += (deg / 30.0) * khandakas[s_idx]
    vir = val / 3.0

    if planet in ["Sun", "Mars", "Jupiter", "Venus"]:
        res = 30.0 + vir if is_uttara else 30.0 - vir
    elif planet in ["Moon", "Saturn"]:
        res = 30.0 - vir if is_uttara else 30.0 + vir
    elif planet == "Mercury":
        if resolved_tradition == "phaladeepika":
            # Mantreśvara Ch. 4.5: Mercury groups with Moon & Saturn (favors Southern course)
            res = 30.0 - vir if is_uttara else 30.0 + vir
        else:
            # Śrīpati / Ernst Wilhelm Kala standard: Mercury gains at both extremes
            res = 30.0 + vir
    else:
        res = 0.0

    return max(0.0, min(60.0, round(res, 2)))


# ==============================================================================
# 5. PILLAR 5: CHEṢṬĀ BALA (MOTIONAL ANOMALY STRENGTH)
# ==============================================================================

def calculate_cheshta_bala_analytical(
    planet: str,
    birth_time_jd: float,
    planet_geo_lon: float,
    seeghrocca: Optional[float] = None
) -> float:
    """
    Motional Strength (Cheṣṭā Bala).
    Evaluated from the planet's Seeghrocca (heliocentric anomaly)
    and Simon Newcomb mean solar polynomial.
    """
    if planet in ["Sun", "Moon"]:
        return 0.0

    T = (birth_time_jd - 2451545.0) / 36525.0
    mean_sun = (280.466457 + 36000.7698278 * T) % 360.0

    if planet in ["Mars", "Jupiter", "Saturn"]:
        if planet == "Mars":
            mean_p = (355.433275 + 19141.6964746 * T) % 360.0
        elif planet == "Jupiter":
            mean_p = (34.351484 + 3036.3027889 * T) % 360.0
        else:  # Saturn
            mean_p = (50.077471 + 1223.5110141 * T) % 360.0

        diff = (planet_geo_lon - mean_p) % 360.0
        if diff > 180.0:
            diff -= 360.0
        midpoint = (mean_p + diff / 2.0) % 360.0
        kendra = abs(mean_sun - midpoint) % 360.0
    else:
        # Inferior Planets (Mercury, Venus): Use precalculated seeghrocca
        if seeghrocca is None:
            # Analytical Simon Newcomb / Keplerian fallback (zero swisseph)
            seeghrocca = (252.250323 + 149474.0722491 * T) % 360.0 if planet == "Mercury" else (181.979099 + 58519.2130302 * T) % 360.0

        diff = (planet_geo_lon - mean_sun) % 360.0
        if diff > 180.0:
            diff -= 360.0
        midpoint = (mean_sun + diff / 2.0) % 360.0
        kendra = abs(seeghrocca - midpoint) % 360.0

    if kendra > 180.0:
        kendra = 360.0 - kendra

    virupas = kendra / 3.0
    return max(0.0, min(60.0, round(virupas, 2)))


def calculate_cheshta_bala(planet: str, birth_time_jd: float, planet_geo_lon: float, sun_geo_lon: float = 0.0) -> float:
    """Legacy wrapper for Cheshta Bala."""
    return calculate_cheshta_bala_analytical(planet, birth_time_jd, planet_geo_lon)


# ==============================================================================
# 6. PILLAR 6: DṚK BALA, NAISARGIKA BALA & PHALAS
# ==============================================================================

def calculate_naisargika_bala() -> Dict[str, float]:
    """Natural Strength (Naisargika Bala) based on immutable luminosity constants."""
    return {
        "Sun": 60.0,
        "Moon": round(60.0 * 6.0 / 7.0, 2),     # 51.43
        "Venus": round(60.0 * 5.0 / 7.0, 2),    # 42.86
        "Jupiter": round(60.0 * 4.0 / 7.0, 2),  # 34.29
        "Mercury": round(60.0 * 3.0 / 7.0, 2),  # 25.71
        "Mars": round(60.0 * 2.0 / 7.0, 2),     # 17.14
        "Saturn": round(60.0 * 1.0 / 7.0, 2)    # 8.57
    }


def calculate_drik_bala(
    planet: str,
    lon: Optional[float] = None,
    planet_positions: Optional[Dict[str, float]] = None,
    is_moon_benefic: bool = True,
    incoming_aspects: Optional[Dict[str, float]] = None,
    mode: str = "kala_weighted"
) -> float:
    """
    Aspectual Strength (Dṛk Bala per BPHS 28.29-31).
    Consumes precalculated incoming Graha Dṛṣṭi matrix from Stage 2A directly,
    or calculates from planet positions.

    Modes:
      - 'kala_weighted' (DEFAULT): Ernst Wilhelm / Kala software standard where
        Jupiter and Mercury add full aspect (100%), and Venus / Moon add 1/4 (25%).
      - 'symmetric_parashara': Classical BPHS 28.29-31 where all benefics add 1/4 (25%)
        and all malefics subtract 1/4 (25%).
    """
    malefics = ["Sun", "Mars", "Saturn"]
    if not is_moon_benefic:
        malefics.append("Moon")

    total_drik = 0.0

    # Fast Path: Precalculated matrix from calculate_aspect_matrices
    if incoming_aspects is not None:
        for p_other, raw_drishti in incoming_aspects.items():
            if p_other == planet or p_other not in PHYSICAL_PLANETS or raw_drishti <= 0:
                continue
            if p_other in malefics:
                total_drik -= raw_drishti / 4.0
            else:
                if mode == "kala_weighted" and p_other in ["Jupiter", "Mercury"]:
                    total_drik += raw_drishti
                else:
                    total_drik += raw_drishti / 4.0
        return round(total_drik, 2)

    # Fallback to direct calculation
    import jyotish.aspects.aspects as aspects
    if planet_positions:
        p_lon = lon if lon is not None else planet_positions[planet]
        for p_other, lon_other in planet_positions.items():
            if p_other == planet or p_other not in PHYSICAL_PLANETS:
                continue
            raw_drishti = aspects.get_graha_drishti(p_other, lon_other, p_lon)
            if raw_drishti <= 0:
                continue
            if p_other in malefics:
                total_drik -= raw_drishti / 4.0
            else:
                if mode == "kala_weighted" and p_other in ["Jupiter", "Mercury"]:
                    total_drik += raw_drishti
                else:
                    total_drik += raw_drishti / 4.0

    return round(total_drik, 2)


def calculate_subha_phala(
    planet: str,
    planet_positions: Dict[str, float],
    dignities_map: Optional[Dict[str, Any]] = None,
    debilitation_mode: str = "kala_degree",
    trimsamsa_mode: str = "unequal_parashara",
    saptavarga_mode: str = "kala"
) -> float:
    """Calculates Śubha Phala across Saptavargas (D1, D2, D3, D7, D9, D12, D30)."""
    from jyotish.relationships.relationships import (
        SIGN_LORDS, get_natural_relationship, get_temporary_relationship,
        get_compound_relationship, get_dignity
    )

    vargas = ["D1", "D2", "D3", "D7", "D9", "D12", "D30"]

    # Fast Path: Ingest precomputed Stage 2A dignities
    if dignities_map and "varga_dignities" in dignities_map:
        v_dignities = dignities_map["varga_dignities"]
        total_subha = 0.0
        for v in vargas:
            if v == "D30":
                p1_d1_lon = planet_positions[planet]
                p1_d1_idx = int(p1_d1_lon / 30.0)
                if trimsamsa_mode == "unequal_parashara":
                    t_res = calculate_unequal_trimsamsa(p1_d1_lon)
                    s_name = t_res["sign"]
                    sign_lord = t_res["ruler"]
                    deg_in_sign = t_res.get("degree_in_sign", p1_d1_lon % 30.0)
                else:
                    v_lon = (p1_d1_lon * 30.0) % 360.0
                    s_idx = int((v_lon % 360.0) / 30.0)
                    s_name = SIGNS[s_idx]
                    sign_lord = SIGN_LORDS[s_name]
                    deg_in_sign = v_lon % 30.0

                lord_d1_lon = planet_positions.get(sign_lord)
                if lord_d1_lon is None:
                    compound = "Neutral"
                else:
                    lord_d1_idx = int(lord_d1_lon / 30.0)
                    natural = get_natural_relationship(planet, sign_lord)
                    temporary = get_temporary_relationship(p1_d1_idx, lord_d1_idx)
                    compound = get_compound_relationship(natural, temporary)
                d_str = get_dignity(planet, s_name, compound, deg_in_sign, debilitation_mode=debilitation_mode)
            elif v == "D2" and saptavarga_mode == "kala":
                p1_d1_lon = planet_positions[planet]
                p1_d1_idx = int(p1_d1_lon / 30.0)
                v_lon = calculate_varga_longitude(p1_d1_lon, "D2", d2_mode="cyclical")
                s_idx = int((v_lon % 360.0) / 30.0)
                s_name = SIGNS[s_idx]
                sign_lord = SIGN_LORDS[s_name]
                deg_in_sign = v_lon % 30.0
                lord_d1_lon = planet_positions.get(sign_lord)
                if lord_d1_lon is None:
                    compound = "Neutral"
                else:
                    lord_d1_idx = int(lord_d1_lon / 30.0)
                    natural = get_natural_relationship(planet, sign_lord)
                    temporary = get_temporary_relationship(p1_d1_idx, lord_d1_idx)
                    compound = get_compound_relationship(natural, temporary)
                d_str = get_dignity(planet, s_name, compound, deg_in_sign, debilitation_mode=debilitation_mode)
            else:
                d_entry = v_dignities.get(v, {}).get(planet, {})
                d_str = d_entry.get("dignity", "Neutral") if isinstance(d_entry, dict) else str(d_entry)

            if "Exalted" in d_str: pts = 60.0
            elif "Moolatrikona" in d_str: pts = 45.0 if v == "D1" else 30.0
            elif "Own Sign" in d_str: pts = 30.0
            elif "Great Friend" in d_str: pts = 22.5
            elif "Friend" in d_str: pts = 15.0
            elif "Neutral" in d_str: pts = 7.5
            elif "Great Enemy" in d_str: pts = 1.875
            elif "Enemy" in d_str: pts = 3.75
            else: pts = 0.0  # Debilitated

            if v != "D1":
                pts /= 2.0
            total_subha += pts
        return total_subha / 4.0

    # Fallback to manual loop only if dignities_map is None
    total_subha = 0.0
    p1_d1_lon = planet_positions[planet]
    p1_d1_idx = int(p1_d1_lon / 30.0)

    for varga in vargas:
        if varga == "D30":
            if trimsamsa_mode == "unequal_parashara":
                t_res = calculate_unequal_trimsamsa(p1_d1_lon)
                varga_sign_name = t_res["sign"]
                sign_lord = t_res["ruler"]
                deg_in_sign = t_res.get("degree_in_sign", p1_d1_lon % 30.0)
            else:
                varga_lon = (p1_d1_lon * 30.0) % 360.0
                varga_sign_idx = int((varga_lon % 360.0) / 30.0)
                varga_sign_name = SIGNS[varga_sign_idx]
                sign_lord = SIGN_LORDS[varga_sign_name]
                deg_in_sign = varga_lon % 30.0
        elif varga == "D2" and saptavarga_mode == "kala":
            varga_lon = calculate_varga_longitude(p1_d1_lon, "D2", d2_mode="cyclical")
            varga_sign_idx = int((varga_lon % 360.0) / 30.0)
            varga_sign_name = SIGNS[varga_sign_idx]
            sign_lord = SIGN_LORDS[varga_sign_name]
            deg_in_sign = varga_lon % 30.0
        else:
            varga_lon = calculate_varga_longitude(p1_d1_lon, varga)
            varga_sign_idx = int((varga_lon % 360.0) / 30.0)
            varga_sign_name = SIGNS[varga_sign_idx]
            sign_lord = SIGN_LORDS[varga_sign_name]
            deg_in_sign = varga_lon % 30.0

        is_rasi = (varga == "D1")

        lord_d1_lon = planet_positions.get(sign_lord)
        if lord_d1_lon is None:
            compound = "Neutral"
        else:
            lord_d1_idx = int(lord_d1_lon / 30.0)
            natural = get_natural_relationship(planet, sign_lord)
            temporary = get_temporary_relationship(p1_d1_idx, lord_d1_idx)
            compound = get_compound_relationship(natural, temporary)

        dignity = get_dignity(planet, varga_sign_name, compound, deg_in_sign, debilitation_mode=debilitation_mode)

        if "Exalted" in dignity: pts = 60.0
        elif "Moolatrikona" in dignity: pts = 45.0 if is_rasi else 30.0
        elif "Own Sign" in dignity: pts = 30.0
        elif "Great Friend" in dignity: pts = 22.5
        elif "Friend" in dignity: pts = 15.0
        elif "Neutral" in dignity: pts = 7.5
        elif "Great Enemy" in dignity: pts = 1.875
        elif "Enemy" in dignity: pts = 3.75
        elif "Debilitated" in dignity: pts = 0.0
        else: pts = 7.5

        if not is_rasi:
            pts /= 2.0

        total_subha += pts

    return total_subha / 4.0


# ==============================================================================
# 7. MASTER SHADBALA ENGINE: calculate_shadbala()
# ==============================================================================

def calculate_shadbala(*args, **kwargs) -> Dict[str, Any]:
    """
    Decoupled Master Shadbala Engine.
    Consumes certified states from Stage 1 (ChartBaseline) and Stage 2A matrices,
    or legacy positional / keyword arguments.
    Operates natively under Whole Sign Tropical astrology with zero Swiss Ephemeris calls.
    
    Signatures supported:
      1. calculate_shadbala(baseline, dignities=..., aspect_matrices=..., dig_bala_mode="whole_sign", ...)
      2. calculate_shadbala(planet_positions, ascendant_lon, mc_lon, birth_time_jd, lon, lat, debilitation_mode=..., dig_bala_mode="whole_sign")
      3. Keyword-only calls with planet_positions=..., ascendant_lon=..., etc.
    """
    # --------------------------------------------------------------------------
    # A. Adapter: Universal Ingestion (Positional OR Keyword Arguments)
    # --------------------------------------------------------------------------
    coords = {}
    time_lords = {}
    lunar_phase = {}
    vargas_positions = None
    dignities = kwargs.get("dignities", None)
    aspect_matrices = kwargs.get("aspect_matrices", None)
    debilitation_mode = kwargs.get("debilitation_mode", "kala_degree")
    dig_bala_mode = kwargs.get("dig_bala_mode", "whole_sign")
    kendra_bala_mode = kwargs.get("kendra_bala_mode", "flat_parashara")
    pillar_mode = kwargs.get("pillar_mode", "kala_breakdown")
    ayana_tradition = kwargs.get("ayana_tradition", "parashara")

    # Harmonize sub-modes based on pillar_mode unless explicitly overridden
    trimsamsa_mode_arg = kwargs.get("trimsamsa_mode", None)
    saptavarga_mode_arg = kwargs.get("saptavarga_mode", None)
    drik_mode_arg = kwargs.get("drik_mode", None)
    phala_mode_arg = kwargs.get("phala_mode", None)

    if trimsamsa_mode_arg is not None:
        trimsamsa_mode = trimsamsa_mode_arg
    else:
        trimsamsa_mode = "unequal_parashara" if pillar_mode == "canonical_parashara" else "harmonic_kala"

    if saptavarga_mode_arg is not None:
        saptavarga_mode = saptavarga_mode_arg
    else:
        saptavarga_mode = "parashara" if pillar_mode == "canonical_parashara" else "kala"

    if drik_mode_arg is not None:
        drik_mode = drik_mode_arg
    else:
        drik_mode = "symmetric_parashara" if pillar_mode == "canonical_parashara" else "kala_weighted"

    if phala_mode_arg is not None:
        phala_mode = phala_mode_arg
    else:
        phala_mode = "parashara_geometric" if pillar_mode == "canonical_parashara" else "arithmetic"
    lon = kwargs.get("lon", kwargs.get("longitude", 0.0))
    lat = kwargs.get("lat", kwargs.get("latitude", 0.0))

    baseline_obj = None
    if len(args) >= 1:
        baseline_obj = args[0]
    elif "baseline" in kwargs:
        baseline_obj = kwargs["baseline"]

    # Case 1: Legacy Positional Invocation (planet_positions, asc_lon, mc_lon, jd, [lon, lat])
    if len(args) >= 4 and isinstance(args[0], dict) and isinstance(args[1], (int, float)):
        planet_positions = args[0]
        ascendant_lon = float(args[1])
        mc_lon = float(args[2])
        birth_time_jd = float(args[3])
        lon = float(args[4]) if len(args) > 4 and isinstance(args[4], (int, float)) else lon
        lat = float(args[5]) if len(args) > 5 and isinstance(args[5], (int, float)) else lat

    # Case 2: Certified Stage 1 Container (passed positionally or as baseline=...)
    elif baseline_obj is not None:
        if hasattr(baseline_obj, "coordinates") and hasattr(baseline_obj, "astronomical_anchors"):
            # Modern Stage 1 Container
            planet_positions = {p: baseline_obj.coordinates[p]["longitude"] for p in PHYSICAL_PLANETS if p in baseline_obj.coordinates}
            anchors = baseline_obj.astronomical_anchors
            ascendant_lon = anchors.get("asc_longitude", anchors.get("ascendant_lon", baseline_obj.coordinates.get("Lagna", {}).get("longitude", 0.0)))
            mc_lon = anchors.get("mc_longitude", anchors.get("spatial_mc_lon", anchors.get("mc_lon", (ascendant_lon + 270.0) % 360.0)))
            birth_time_jd = anchors.get("jd_utc", anchors.get("birth_time_jd", 0.0))
            time_lords = anchors.get("temporal_lords", {})
            lunar_phase = getattr(baseline_obj, "lunar_phase", {})
            coords = baseline_obj.coordinates
            vargas_positions = getattr(baseline_obj, "vargas", None)
            lon = getattr(baseline_obj, "longitude", lon)
            lat = getattr(baseline_obj, "latitude", lat)
        elif isinstance(baseline_obj, dict) and "coordinates" in baseline_obj:
            # Serialized Stage 1 dict
            coords = baseline_obj["coordinates"]
            planet_positions = {p: coords[p]["longitude"] for p in PHYSICAL_PLANETS if p in coords}
            anchors = baseline_obj.get("astronomical_anchors", {})
            ascendant_lon = anchors.get("asc_longitude", anchors.get("ascendant_lon", coords.get("Lagna", {}).get("longitude", 0.0)))
            mc_lon = anchors.get("mc_longitude", anchors.get("spatial_mc_lon", anchors.get("mc_lon", (ascendant_lon + 270.0) % 360.0)))
            birth_time_jd = anchors.get("jd_utc", anchors.get("birth_time_jd", 0.0))
            time_lords = anchors.get("temporal_lords", {})
            lunar_phase = baseline_obj.get("lunar_phase", {})
            vargas_positions = baseline_obj.get("vargas", None)
            lon = baseline_obj.get("longitude", lon)
            lat = baseline_obj.get("latitude", lat)
        else:
            planet_positions = baseline_obj if isinstance(baseline_obj, dict) else kwargs.get("planet_positions", {})
            ascendant_lon = kwargs.get("ascendant_lon", 0.0)
            mc_lon = kwargs.get("mc_lon", (ascendant_lon + 270.0) % 360.0)
            birth_time_jd = kwargs.get("birth_time_jd", 0.0)

        if len(args) > 1 and dignities is None and isinstance(args[1], dict):
            dignities = args[1]
        if len(args) > 2 and aspect_matrices is None and isinstance(args[2], dict):
            aspect_matrices = args[2]

    # Case 3: Keyword-only fallback (planet_positions={...}, ascendant_lon=...)
    else:
        planet_positions = kwargs.get("planet_positions", {})
        ascendant_lon = kwargs.get("ascendant_lon", 0.0)
        mc_lon = kwargs.get("mc_lon", (ascendant_lon + 270.0) % 360.0)
        birth_time_jd = kwargs.get("birth_time_jd", 0.0)

    if planet_positions is None:
        planet_positions = {}
    if ascendant_lon is None:
        ascendant_lon = 0.0
    if mc_lon is None:
        mc_lon = (ascendant_lon + 270.0) % 360.0
    if birth_time_jd is None:
        birth_time_jd = 0.0

    # Fallback to compute temporal lords if missing from baseline
    if not time_lords and birth_time_jd > 0:
        time_lords = calculate_ahargana_lords(birth_time_jd, lon, lat)

    planet_positions = {p: planet_positions[p] for p in PHYSICAL_PLANETS if p in planet_positions}
    sun_lon = planet_positions.get("Sun", 0.0)
    moon_lon = planet_positions.get("Moon", 0.0)

    # Moon Beneficence classification
    if "is_waxing" in lunar_phase and "illumination_pct" in lunar_phase:
        moon_paksha = (lunar_phase["illumination_pct"] / 100.0) * 60.0
    else:
        moon_paksha = calculate_paksha_bala("Moon", moon_lon, sun_lon)
    is_moon_benefic = (moon_paksha >= 30.0)

    naisargika = calculate_naisargika_bala()
    results: Dict[str, Any] = {}

    pre_war_scores: Dict[str, float] = {}
    preliminary_data: Dict[str, Any] = {}
    planet_lats: Dict[str, float] = {}

    # --------------------------------------------------------------------------
    # Pass 1: Compute Sthāna, Dig, and Preliminary Kāla Bala for Pre-War Scores
    # --------------------------------------------------------------------------
    for p in PHYSICAL_PLANETS:
        if p not in planet_positions:
            continue

        pl_lon = planet_positions[p]
        p_coord = coords.get(p, {})
        pl_lat = p_coord.get("latitude", 0.0)
        planet_lats[p] = pl_lat

        # 1. Sthāna Bala
        uccha = calculate_uccha_bala(p, pl_lon)
        saptavarga = calculate_saptavarga_bala(
            p,
            planet_positions,
            dignities_map=dignities,
            vargas_positions=vargas_positions,
            trimsamsa_mode=trimsamsa_mode,
            saptavarga_mode=saptavarga_mode
        )
        ojayugma = calculate_ojayugmarasyamsa_bala(p, pl_lon)
        kendra = calculate_kendra_bala(pl_lon, ascendant_lon, mode=kendra_bala_mode)
        drekkana = calculate_drekkana_bala(p, pl_lon)
        sthana = uccha + saptavarga + ojayugma + kendra + drekkana

        # 2. Dig Bala (Directional Strength - Whole Sign Tropical by default)
        campanus_hpos = p_coord.get("campanus_house_pos")
        dig = calculate_dig_bala(
            planet_name=p,
            planet_lon=pl_lon,
            ascendant_lon=ascendant_lon,
            spatial_mc_lon=mc_lon,
            mode=dig_bala_mode,
            campanus_hpos=campanus_hpos
        )

        # 3. Kāla Bala (Preliminary)
        nathonnatha = calculate_nathonnatha_bala(p, sun_lon, mc_lon=mc_lon, ascendant_lon=ascendant_lon)
        paksha = calculate_paksha_bala(p, moon_lon, sun_lon)
        tribhaga = calculate_tribhaga_bala(p, sun_lon, ascendant_lon)
        ayana = calculate_ayana_bala(p, planet_lon=pl_lon, tradition=ayana_tradition)

        abda_lord = time_lords.get("Varsha", time_lords.get("Abda"))
        abda = 15.0 if p == abda_lord else 0.0
        masa = 30.0 if p == time_lords.get("Masa") else 0.0
        vara = 45.0 if p == time_lords.get("Vara") else 0.0
        hora = 60.0 if p == time_lords.get("Hora") else 0.0

        kaala_pre = nathonnatha + paksha + tribhaga + abda + masa + vara + hora
        pre_war_scores[p] = sthana + dig + kaala_pre + (ayana if pillar_mode == "canonical_parashara" else 0.0)

        preliminary_data[p] = {
            "pl_lon": pl_lon,
            "sthana": sthana,
            "uccha": uccha,
            "saptavarga": saptavarga,
            "ojayugma": ojayugma,
            "kendra": kendra,
            "drekkana": drekkana,
            "dig": dig,
            "nathonnatha": nathonnatha,
            "paksha": paksha,
            "tribhaga": tribhaga,
            "abda": abda,
            "masa": masa,
            "vara": vara,
            "hora": hora,
            "ayana": ayana,
            "kaala_pre": kaala_pre
        }

    # Planetary War (Yuddha Bala)
    yuddha_adjustments = calculate_yuddha_bala(
        pre_war_scores, planet_positions, planet_lats, use_latitude=True
    )

    # --------------------------------------------------------------------------
    # Pass 2: Finalize Balas, Ayana, Cheṣṭā, Dṛk, Totals, and Phalas
    # --------------------------------------------------------------------------
    for p in PHYSICAL_PLANETS:
        if p not in planet_positions:
            continue

        p_data = preliminary_data[p]
        pl_lon = p_data["pl_lon"]
        sthana = p_data["sthana"]
        uccha = p_data["uccha"]
        saptavarga = p_data["saptavarga"]
        ojayugma = p_data["ojayugma"]
        kendra = p_data["kendra"]
        drekkana = p_data["drekkana"]
        dig = p_data["dig"]
        nathonnatha = p_data["nathonnatha"]
        paksha = p_data["paksha"]
        tribhaga = p_data["tribhaga"]
        abda = p_data["abda"]
        masa = p_data["masa"]
        vara = p_data["vara"]
        hora = p_data["hora"]
        kaala_pre = p_data["kaala_pre"]
        ayana = p_data["ayana"]

        yuddha = yuddha_adjustments.get(p, 0.0)
        kaala = kaala_pre + yuddha
        kaala_canonical = kaala + ayana

        # 4. Cheṣṭā Bala
        if p == "Sun":
            cheshta = ayana
        elif p == "Moon":
            cheshta = paksha
        else:
            p_coord = coords.get(p, {})
            seeghrocca = p_coord.get("seeghrocca")
            cheshta = calculate_cheshta_bala_analytical(
                p, birth_time_jd, pl_lon, seeghrocca=seeghrocca
            )

        # 5. Naisargika Bala
        naisarg = naisargika[p]

        # 6. Dṛk Bala
        incoming_aspects = None
        if aspect_matrices and "graha_drishti" in aspect_matrices:
            incoming_aspects = aspect_matrices["graha_drishti"].get("incoming", {}).get(p)

        drik = calculate_drik_bala(
            p,
            lon=pl_lon,
            planet_positions=planet_positions,
            is_moon_benefic=is_moon_benefic,
            incoming_aspects=incoming_aspects,
            mode=drik_mode
        )

        # 7. Qualities: Iṣṭa & Kaṣṭa Phala (BPHS 29.4-5 geometric mean vs Kala arithmetic mean)
        uccha_clamped = max(0.0, min(60.0, uccha))
        cheshta_clamped = max(0.0, min(60.0, cheshta))
        ishta_arithmetic = round((uccha_clamped + cheshta_clamped) / 2.0, 2)
        kashta_arithmetic = round(60.0 - ishta_arithmetic, 2)
        ishta_geometric = round(math.sqrt(uccha_clamped * cheshta_clamped), 2)
        kashta_geometric = round(math.sqrt(max(0.0, 60.0 - uccha_clamped) * max(0.0, 60.0 - cheshta_clamped)), 2)

        if phala_mode in ["geometric", "parashara_geometric"]:
            ishta_phala = ishta_geometric
            kashta_phala = kashta_geometric
        else:
            ishta_phala = ishta_arithmetic
            kashta_phala = kashta_arithmetic

        # Totals
        if pillar_mode == "canonical_parashara":
            total_virupas = round(sthana + dig + kaala_canonical + cheshta + naisarg + drik, 1)
        else:
            total_virupas = round(sthana + dig + kaala + ayana + cheshta + naisarg + drik, 1)
        total_rupas = round(total_virupas / 60.0, 2)

        subha_phala = calculate_subha_phala(
            p,
            planet_positions,
            dignities_map=dignities,
            debilitation_mode=debilitation_mode,
            trimsamsa_mode=trimsamsa_mode,
            saptavarga_mode=saptavarga_mode
        )
        asubha_phala = max(0.0, 60.0 - subha_phala)

        req_sthana = REQUIRED_STHANA.get(p, 100.0)
        req_dig = REQUIRED_DIG.get(p, 30.0)
        req_kaala = REQUIRED_KAALA.get(p, 100.0)
        req_ayana = REQUIRED_AYANA.get(p, 30.0)
        req_cheshta = REQUIRED_CHESHTA.get(p, 40.0)
        req_total = REQUIRED_TOTAL.get(p, 300.0)

        results[p] = {
            # Pillar 1: Sthāna Bala
            "Sthana_Bala": round(sthana, 1),
            "Uccha_Bala": round(uccha, 2),
            "Saptavarga_Bala": round(saptavarga, 1),
            "Ojhayugma_Bala": round(ojayugma, 1),
            "Kendradi_Bala": round(kendra, 2),
            "Drekkana_Bala": round(drekkana, 1),
            "Required_Sthana": req_sthana,
            "Pct_Required_Sthana": round((sthana / req_sthana) * 100.0, 1),

            # Pillar 2: Dig Bala
            "Dig_Bala": round(dig, 2),
            "Required_Dig": req_dig,
            "Pct_Required_Dig": round((dig / req_dig) * 100.0, 1),

            # Pillar 3: Kāla Bala
            "Kala_Bala": round(kaala_canonical if pillar_mode == "canonical_parashara" else kaala, 1),
            "Kala_Bala_Canonical": round(kaala_canonical, 1),
            "Natonnata_Bala": round(nathonnatha, 2),
            "Paksha_Bala": round(paksha, 2),
            "Tribhaga_Bala": round(tribhaga, 1),
            "Varsha_Bala": round(abda, 1),
            "Masa_Bala": round(masa, 1),
            "Dina_Bala": round(vara, 1),
            "Hora_Bala": round(hora, 1),
            "Required_Kaala": req_kaala,
            "Pct_Required_Kaala": round(((kaala_canonical if pillar_mode == "canonical_parashara" else kaala) / req_kaala) * 100.0, 1),
            "Pct_Required_Kaala_Canonical": round((kaala_canonical / req_kaala) * 100.0, 1),

            # Pillar 4: Ayana Bala
            "Ayana_Bala": round(ayana, 2),
            "Required_Ayana": req_ayana,
            "Pct_Required_Ayana": round((ayana / req_ayana) * 100.0, 1),

            # Pillar 5: Cheṣṭā Bala
            "Cheshta_Bala": round(cheshta, 2),
            "Required_Cheshta": req_cheshta,
            "Pct_Required_Cheshta": round((cheshta / req_cheshta) * 100.0, 1),

            # Pillar 6: Dṛk, Naisargika & War
            "Drik_Bala": round(drik, 1),
            "Naisargika_Bala": round(naisarg, 2),
            "Yuddha_Bala": round(yuddha, 2),

            # Canonical 6 Pillars (BPHS Ch. 27-28 aggregation)
            "Canonical_6_Pillars": {
                "Sthana_Bala": round(sthana, 1),
                "Dig_Bala": round(dig, 2),
                "Kala_Bala": round(kaala_canonical, 1),
                "Cheshta_Bala": round(cheshta, 2),
                "Naisargika_Bala": round(naisarg, 2),
                "Drik_Bala": round(drik, 1),
                "Total_Virupas": round(sthana + dig + kaala_canonical + cheshta + naisarg + drik, 1)
            },

            # Totals & Ratios
            "Total_Virupas": round(total_virupas, 1),
            "Total_Rupas": round(total_rupas, 2),
            "Required_Total": req_total,
            "Pct_Required_Total": round((total_virupas / req_total) * 100.0, 1),
            "is_strong": round(total_virupas / req_total, 2) >= 1.0,
            "is_strong_all_pillars": (
                total_virupas >= req_total and
                sthana >= req_sthana and
                dig >= req_dig and
                kaala_canonical >= req_kaala and
                cheshta >= req_cheshta and
                ayana >= req_ayana
            ),

            # Qualities (Mood & Auspiciousness)
            "Ishta_Phala": round(ishta_phala, 2),
            "Kashta_Phala": round(kashta_phala, 2),
            "Ishta_Phala_Geometric": round(ishta_geometric, 2),
            "Kashta_Phala_Geometric": round(kashta_geometric, 2),
            "Ishta_Phala_Arithmetic": round(ishta_arithmetic, 2),
            "Kashta_Phala_Arithmetic": round(kashta_arithmetic, 2),
            "Subha_Phala": round(subha_phala, 2),
            "Asubha_Phala": round(asubha_phala, 2)
        }

    # Relative Rank 1 to 7 by descending Total_Virūpas
    sorted_planets = sorted(results.keys(), key=lambda pl: results[pl]["Total_Virupas"], reverse=True)
    for rank_idx, pl in enumerate(sorted_planets):
        results[pl]["Relative_Rank"] = rank_idx + 1

    return results
