"""
Transit Calculation Engine for Astra (Kala Methodology)

Calculates real-time and date-specific planetary transits (Gochara) relative to 
the native's birth chart. Supports both Ernst Wilhelm's Dhruva Equatorial Nakshatras 
and Vic DiCara's Chitra Paksha Nakshatras with Tropical Rasis.
"""

from typing import Dict, Any, List, Optional, Tuple
from jyotish import generate_jyotish
from jyotish.aspects.aspects import get_graha_drishti

SIGNS_LIST = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

PLANET_ORDER = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]


def calculate_transits(
    natal_chart: Dict[str, Any],
    transit_year: int,
    transit_month: int,
    transit_day: int,
    transit_hour: int = 12,
    transit_minute: int = 0,
    transit_second: int = 0,
    transit_latitude: float = 51.5074,
    transit_longitude: float = -0.1278,
    transit_timezone: float = 0.0,
    nakshatra_system: str = "ERNST_DHRUVA",
    debilitation_mode: str = "kala_degree",
    aspect_orb_degrees: float = 3.3333
) -> Dict[str, Any]:
    """
    Computes transiting planetary positions and evaluates their aspects
    and house positions relative to the native's natal chart.
    """
    # 1. Compute Transit Chart using Astra's Swiss Ephemeris engine
    transit_chart = generate_jyotish.generate_kala_chart(
        name="Transit",
        year=transit_year,
        month=transit_month,
        day=transit_day,
        hour=transit_hour,
        minute=transit_minute,
        second=transit_second,
        latitude=transit_latitude,
        longitude=transit_longitude,
        timezone_offset=transit_timezone,
        nakshatra_system=nakshatra_system,
        debilitation_mode=debilitation_mode
    )

    natal_d1 = natal_chart.get("vargas", {}).get("D1", {})
    transit_d1 = transit_chart.get("vargas", {}).get("D1", {})

    natal_grahas = natal_d1.get("grahas", {})
    natal_lagna = natal_d1.get("lagna", {})
    transit_grahas = transit_d1.get("grahas", {})
    transit_lagna = transit_d1.get("lagna", {})

    natal_lagna_sign = natal_lagna.get("sign", "Aries")
    natal_lagna_idx = SIGNS_LIST.index(natal_lagna_sign) if natal_lagna_sign in SIGNS_LIST else 0

    natal_moon_sign = natal_grahas.get("Moon", {}).get("sign", natal_lagna_sign)
    natal_moon_idx = SIGNS_LIST.index(natal_moon_sign) if natal_moon_sign in SIGNS_LIST else 0

    # 2. Process Transiting Planets: House from Lagna & Moon
    processed_transit_planets = {}
    for p_name in PLANET_ORDER:
        if p_name not in transit_grahas:
            continue
        g = transit_grahas[p_name]
        p_sign = g.get("sign", "Aries")
        s_idx = SIGNS_LIST.index(p_sign) if p_sign in SIGNS_LIST else 0

        # Whole-sign houses (1-indexed)
        h_from_lagna = ((s_idx - natal_lagna_idx + 12) % 12) + 1
        h_from_moon = ((s_idx - natal_moon_idx + 12) % 12) + 1

        processed_transit_planets[p_name] = {
            "name": p_name,
            "sign": p_sign,
            "sign_idx": s_idx,
            "longitude": g.get("longitude", 0.0),
            "degree_0_to_30": g.get("degree_0_to_30", 0.0),
            "degree": int(g.get("degree_0_to_30", 0.0)),
            "minute": int(round((g.get("degree_0_to_30", 0.0) % 1.0) * 60)),
            "is_retrograde": g.get("is_retrograde", False),
            "nakshatra": g.get("nakshatra", ""),
            "pada": g.get("pada", 1),
            "house_from_lagna": h_from_lagna,
            "house_from_moon": h_from_moon
        }

    # 3. Detect Active Transit Aspects onto Natal Planets
    active_aspects = get_transit_aspects(
        transit_grahas=transit_grahas,
        natal_grahas=natal_grahas,
        natal_lagna=natal_lagna,
        orb_degrees=aspect_orb_degrees
    )

    return {
        "transit_chart": transit_chart,
        "transit_planets": processed_transit_planets,
        "transit_lagna": transit_lagna,
        "natal_lagna_sign": natal_lagna_sign,
        "natal_moon_sign": natal_moon_sign,
        "active_aspects": active_aspects,
        "transit_time_info": {
            "year": transit_year,
            "month": transit_month,
            "day": transit_day,
            "hour": transit_hour,
            "minute": transit_minute,
            "second": transit_second,
            "formatted": f"{transit_day:02d}/{transit_month:02d}/{transit_year:04d} {transit_hour:02d}:{transit_minute:02d}:{transit_second:02d}"
        }
    }


def get_transit_aspects(
    transit_grahas: Dict[str, Any],
    natal_grahas: Dict[str, Any],
    natal_lagna: Dict[str, Any],
    orb_degrees: float = 3.3333
) -> List[Dict[str, Any]]:
    """
    Finds all active Graha Drishti aspects and conjunctions cast by
    transiting planets onto natal planets and the natal Ascendant.
    """
    aspects = []
    natal_targets = dict(natal_grahas)
    if natal_lagna:
        natal_targets["Lagna"] = natal_lagna

    for t_name, t_info in transit_grahas.items():
        if t_name not in PLANET_ORDER:
            continue
        t_lon = t_info.get("longitude", 0.0)

        for n_name, n_info in natal_targets.items():
            n_lon = n_info.get("longitude", 0.0)
            diff = (n_lon - t_lon) % 360.0

            # 1. Conjunction (Yuti, 0°)
            orb_conj = diff if diff <= 180.0 else (360.0 - diff)
            if orb_conj <= orb_degrees:
                aspects.append({
                    "aspecting": t_name,
                    "target": n_name,
                    "type": "Conjunction",
                    "code": "CONJ",
                    "angular_diff": round(diff, 2),
                    "orb": round(orb_conj, 2),
                    "virupas": 60.0,
                    "is_benefic": t_name in ["Jupiter", "Venus", "Mercury"],
                    "description": f"Transiting {t_name} is conjunct Natal {n_name} (orb {round(orb_conj, 1)}°)"
                })
                continue

            # 2. Classical Graha Drishti (Glances & Special Aspects)
            candidate_aspects = [("7th Opposition", 180.0)]
            if t_name == "Mars":
                candidate_aspects.extend([("4th Aspect", 90.0), ("8th Aspect", 210.0)])
            elif t_name == "Jupiter":
                candidate_aspects.extend([("5th Trine Aspect", 120.0), ("9th Trine Aspect", 240.0)])
            elif t_name == "Saturn":
                candidate_aspects.extend([("3rd Aspect", 60.0), ("10th Aspect", 270.0)])
            elif t_name in ["Rahu", "Ketu"]:
                candidate_aspects.extend([("5th Trine Aspect", 120.0), ("9th Trine Aspect", 240.0)])

            for glance_type, nominal_angle in candidate_aspects:
                angle_error = abs((diff - nominal_angle + 180.0) % 360.0 - 180.0)
                if angle_error <= orb_degrees:
                    virupas = get_graha_drishti(t_name, t_lon, n_lon) if t_name not in ["Rahu", "Ketu"] else 45.0
                    is_benefic = t_name in ["Jupiter", "Venus"]
                    aspects.append({
                        "aspecting": t_name,
                        "target": n_name,
                        "type": glance_type,
                        "code": "DRISHTI",
                        "angular_diff": round(diff, 2),
                        "orb": round(angle_error, 2),
                        "virupas": round(virupas, 1),
                        "is_benefic": is_benefic,
                        "description": f"Transiting {t_name} casts {glance_type} on Natal {n_name} (orb {round(angle_error, 1)}°)"
                    })

    return aspects
