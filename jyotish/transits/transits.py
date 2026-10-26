"""
Transit Calculation Engine for Astra (Kala Methodology)

Calculates real-time and date-specific planetary transits (Gochara) relative to 
the native's birth chart. Supports both Ernst Wilhelm's Dhruva Equatorial Nakshatras 
and Vic DiCara's Chitra Paksha Nakshatras with Tropical Rasis.
"""

import copy
import swisseph as swe
from typing import Dict, Any, List, Optional, Tuple
from jyotish.baseline import ChartBaseline
from jyotish.aspects.aspects import get_graha_drishti

SIGNS_LIST = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

PLANET_ORDER = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]

MEAN_DAILY_SPEEDS = {
    "Sun": 0.9856,
    "Moon": 13.1764,
    "Mars": 0.5240,
    "Mercury": 1.0000,
    "Jupiter": 0.0831,
    "Venus": 1.0000,
    "Saturn": 0.0335,
    "Rahu": 0.0530,
    "Ketu": 0.0530
}

STATIONARY_PLANETS = {"Mars", "Mercury", "Jupiter", "Venus", "Saturn"}

SWE_PLANET_MAP = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mars": swe.MARS,
    "Mercury": swe.MERCURY,
    "Jupiter": swe.JUPITER,
    "Venus": swe.VENUS,
    "Saturn": swe.SATURN,
    "Rahu": swe.TRUE_NODE,
    "Ketu": swe.TRUE_NODE
}


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
    Computes transiting planetary positions and evaluates their aspects,
    velocities, stationary states, and house positions relative to the native's natal chart.
    """
    # 1. Compute Transit Baseline snapshot using certified Stage 1 (zero redundant chart generation)
    transit_baseline = ChartBaseline(
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
        nakshatra_system=nakshatra_system
    )

    jd_ut = swe.julday(
        transit_year,
        transit_month,
        transit_day,
        transit_hour + transit_minute / 60.0 + transit_second / 3600.0 - transit_timezone
    )

    transit_d1 = copy.deepcopy(transit_baseline.vargas["D1"])
    t_naks = transit_baseline.nakshatras["grahas"]
    for p_name, g in transit_d1["grahas"].items():
        if p_name in t_naks:
            g["nakshatra"] = t_naks[p_name]["nakshatra"]
            g["pada"] = t_naks[p_name]["pada"]
    if "Lagna" in t_naks and "lagna" in transit_d1:
        transit_d1["lagna"]["nakshatra"] = t_naks["Lagna"]["nakshatra"]
        transit_d1["lagna"]["pada"] = t_naks["Lagna"]["pada"]

    transit_chart = {
        "vargas": {"D1": transit_d1},
        "baseline": transit_baseline.to_dict()
    }
    natal_d1 = natal_chart.get("vargas", {}).get("D1", {})
    natal_grahas = natal_d1.get("grahas", {})
    natal_lagna = natal_d1.get("lagna", {})
    transit_grahas = transit_d1.get("grahas", {})
    transit_lagna = transit_d1.get("lagna", {})

    natal_lagna_sign = natal_lagna.get("sign", "Aries")
    natal_lagna_idx = SIGNS_LIST.index(natal_lagna_sign) if natal_lagna_sign in SIGNS_LIST else 0

    natal_moon_sign = natal_grahas.get("Moon", {}).get("sign", natal_lagna_sign)
    natal_moon_idx = SIGNS_LIST.index(natal_moon_sign) if natal_moon_sign in SIGNS_LIST else 0

    # 2. Process Transiting Planets: Velocity, Station States, House from Lagna & Moon
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

        # Extract daily speed from coordinates or baseline
        coord_info = transit_baseline.coordinates.get(p_name, {})
        raw_speed = coord_info.get("speed")
        if raw_speed is None:
            p_id = SWE_PLANET_MAP.get(p_name)
            if p_id is not None:
                raw_speed = swe.calc_ut(jd_ut, p_id)[0][3]
            else:
                raw_speed = 0.0
        daily_speed = float(raw_speed)

        mean_speed = MEAN_DAILY_SPEEDS.get(p_name, 1.0)
        speed_ratio = round(abs(daily_speed) / mean_speed, 3) if mean_speed > 0 else 1.0
        is_retro = g.get("is_retrograde", False)

        is_stationary = False
        station_type: Optional[str] = None

        if p_name in STATIONARY_PLANETS:
            # Stationary threshold: <= 10% of mean speed
            if speed_ratio <= 0.10:
                is_stationary = True
                p_id = SWE_PLANET_MAP.get(p_name)
                if p_id is not None:
                    sp_plus = swe.calc_ut(jd_ut + 0.5, p_id)[0][3]
                    sp_minus = swe.calc_ut(jd_ut - 0.5, p_id)[0][3]
                    accel = sp_plus - sp_minus
                    if accel < 0:
                        station_type = "SR"
                    elif accel > 0:
                        station_type = "SD"
            else:
                # Direction change within +/- 48h
                p_id = SWE_PLANET_MAP.get(p_name)
                if p_id is not None:
                    sp_m2 = swe.calc_ut(jd_ut - 2.0, p_id)[0][3]
                    sp_p2 = swe.calc_ut(jd_ut + 2.0, p_id)[0][3]
                    if (sp_m2 * daily_speed <= 0) or (sp_p2 * daily_speed <= 0):
                        is_stationary = True
                        accel = sp_p2 - sp_m2
                        station_type = "SR" if accel < 0 else "SD"

        if is_stationary:
            if station_type == "SR":
                motion_state = "Stationary Retrograde"
            elif station_type == "SD":
                motion_state = "Stationary Direct"
            else:
                motion_state = "Stationary"
            gati_sanskrit = "Stambhana"
        elif speed_ratio <= 0.50:
            motion_state = "Slow Retrograde" if is_retro else "Slow Direct"
            gati_sanskrit = "Mandatara"
        elif is_retro:
            motion_state = "Retrograde"
            gati_sanskrit = "Vakri"
        elif speed_ratio >= 1.20:
            motion_state = "Fast"
            gati_sanskrit = "Atichara"
        else:
            motion_state = "Direct"
            gati_sanskrit = "Rju"

        processed_transit_planets[p_name] = {
            "name": p_name,
            "sign": p_sign,
            "sign_idx": s_idx,
            "longitude": g.get("longitude", 0.0),
            "degree_0_to_30": g.get("degree_0_to_30", 0.0),
            "degree": int(g.get("degree_0_to_30", 0.0)),
            "minute": int(round((g.get("degree_0_to_30", 0.0) % 1.0) * 60)),
            "is_retrograde": is_retro,
            "daily_speed": round(daily_speed, 6),
            "speed_ratio": speed_ratio,
            "is_stationary": is_stationary,
            "station_type": station_type,
            "motion_state": motion_state,
            "gati_sanskrit": gati_sanskrit,
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
        orb_degrees=aspect_orb_degrees,
        processed_transit_planets=processed_transit_planets
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
    orb_degrees: float = 3.3333,
    processed_transit_planets: Optional[Dict[str, Any]] = None
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

        t_proc = (processed_transit_planets or {}).get(t_name, {})
        asp_is_stationary = bool(t_proc.get("is_stationary", False))
        asp_station_type = t_proc.get("station_type")
        asp_speed_ratio = float(t_proc.get("speed_ratio", 1.0))

        for n_name, n_info in natal_targets.items():
            n_lon = n_info.get("longitude", 0.0)
            diff = (n_lon - t_lon) % 360.0
            is_retro = t_info.get("is_retrograde", False)

            # 1. Conjunction (Yuti, 0°)
            orb_conj = diff if diff <= 180.0 else (360.0 - diff)
            if orb_conj <= orb_degrees:
                # Direct planet applies when moving towards n_lon (diff <= 180); retro applies when diff > 180
                is_applying = (diff <= 180.0) if not is_retro else (diff > 180.0)

                orb_closeness = max(0.0, 1.0 - (orb_conj / orb_degrees))
                virupa_factor = 60.0 / 60.0
                speed_factor = 2.0 if asp_is_stationary else (1.4 if asp_speed_ratio <= 0.50 else 1.0)
                intensity_weight = round(orb_closeness * virupa_factor * speed_factor, 3)

                aspects.append({
                    "aspecting": t_name,
                    "target": n_name,
                    "type": "Conjunction",
                    "code": "CONJ",
                    "angular_diff": round(diff, 2),
                    "orb": round(orb_conj, 2),
                    "virupas": 60.0,
                    "is_benefic": t_name in ["Jupiter", "Venus", "Mercury"],
                    "is_applying": is_applying,
                    "aspecting_is_stationary": asp_is_stationary,
                    "aspecting_station_type": asp_station_type,
                    "aspecting_speed_ratio": asp_speed_ratio,
                    "intensity_weight": intensity_weight,
                    "motion_status": "Applying" if is_applying else "Separating",
                    "description": f"Transiting {t_name} is conjunct Natal {n_name} (orb {round(orb_conj, 1)}°, {'Applying' if is_applying else 'Separating'})"
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
                signed_diff = (diff - nominal_angle + 180.0) % 360.0 - 180.0
                angle_error = abs(signed_diff)
                if angle_error <= orb_degrees:
                    virupas = get_graha_drishti(t_name, t_lon, n_lon) if t_name not in ["Rahu", "Ketu"] else 45.0
                    is_benefic = t_name in ["Jupiter", "Venus"]
                    # Direct planet applies when signed_diff > 0 (before exact aspect); retro applies when signed_diff < 0
                    is_applying = (signed_diff > 0) if not is_retro else (signed_diff < 0)

                    orb_closeness = max(0.0, 1.0 - (angle_error / orb_degrees))
                    virupa_factor = min(1.0, max(0.1, virupas / 60.0))
                    speed_factor = 2.0 if asp_is_stationary else (1.4 if asp_speed_ratio <= 0.50 else 1.0)
                    intensity_weight = round(orb_closeness * virupa_factor * speed_factor, 3)

                    aspects.append({
                        "aspecting": t_name,
                        "target": n_name,
                        "type": glance_type,
                        "code": "DRISHTI",
                        "angular_diff": round(diff, 2),
                        "orb": round(angle_error, 2),
                        "virupas": round(virupas, 1),
                        "is_benefic": is_benefic,
                        "is_applying": is_applying,
                        "aspecting_is_stationary": asp_is_stationary,
                        "aspecting_station_type": asp_station_type,
                        "aspecting_speed_ratio": asp_speed_ratio,
                        "intensity_weight": intensity_weight,
                        "motion_status": "Applying" if is_applying else "Separating",
                        "description": f"Transiting {t_name} casts {glance_type} on Natal {n_name} (orb {round(angle_error, 1)}°, {'Applying' if is_applying else 'Separating'})"
                    })

    # Sort aspects by intensity weight descending so stationary / exact hits come first
    aspects.sort(key=lambda a: a.get("intensity_weight", 0.0), reverse=True)
    return aspects
