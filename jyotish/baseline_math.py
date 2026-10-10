"""
jyotish/baseline_math.py
Pure Mathematical & Geometric Algorithms for Astra Stage 1.

Stateless, standalone coordinate transformations, harmonic varga calculators,
spherical obliquity transformations, solar crossing solvers, and classical
boundary lookups (D30 Trimsamsa, D60 Shastiamsa, Baladi Avastha).
"""

import math
import os
from typing import Dict, Any, Tuple, Optional
import swisseph as swe

# Set ephemeris path to absolute path of 'ephe' directory in project root
_base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_ephe_path = os.path.join(_base_dir, 'ephe')
if os.path.exists(_ephe_path):
    swe.set_ephe_path(_ephe_path)

from jyotish.baseline_tables import (
    ZODIAC_SIGNS,
    SIGN_LORDS,
    PLANET_SYMBOLS,
    VIMSHOTTARI_SEQUENCE,
    VIMSHOTTARI_YEARS,
    SHASTIAMSA_DEITIES,
    SHASTIAMSA_MALEFIC_ODD,
)


def calculate_sub_lord(nakshatra_fraction: float, nakshatra_lord: str) -> str:
    """Calculates Vimshottari Sub-Lord for a fractional position in a Nakshatra."""
    start_idx = VIMSHOTTARI_SEQUENCE.index(nakshatra_lord)
    current_fraction = 0.0
    for i in range(9):
        lord = VIMSHOTTARI_SEQUENCE[(start_idx + i) % 9]
        span_fraction = VIMSHOTTARI_YEARS[lord] / 120.0
        if current_fraction + span_fraction >= nakshatra_fraction:
            return lord
        current_fraction += span_fraction
    return nakshatra_lord


def calculate_varga_longitude(
    longitude: float,
    varga: str,
    d10_mode: str = "reverse",
    d24_mode: str = "reverse",
    d2_mode: str = "parashari",
    trimsamsa_mode: str = "harmonic"
) -> float:
    """Harmonic coordinate transformation across 16 divisional charts."""
    sign_idx = int(longitude // 30)
    deg = longitude % 30.0
    is_odd = (sign_idx % 2 == 0)

    def uniform_varga(harmonic: int, start_sign: int) -> float:
        div_size = 30.0 / harmonic
        div_index = int(deg // div_size)
        varga_sign = (start_sign + div_index) % 12
        fraction = (deg % div_size) / div_size
        return (varga_sign * 30.0) + (fraction * 30.0)

    if varga == "D1":
        return longitude
    elif varga == "D2":
        div_size = 15.0
        div_index = min(1, int(deg // div_size))
        if d2_mode in ("cyclical", "parivritti", "12_signs"):
            varga_sign = (sign_idx + div_index * 6) % 12
            return (varga_sign * 30.0) + ((deg % div_size) / div_size * 30.0)
        else:
            # Classical Parāśarī Horā (bipolar Sun / Moon allocation):
            # Odd signs: 0°-15° -> Sun (Leo, sign index 4); 15°-30° -> Moon (Cancer, sign index 3)
            # Even signs: 0°-15° -> Moon (Cancer, sign index 3); 15°-30° -> Sun (Leo, sign index 4)
            if is_odd:
                varga_sign = 4 if div_index == 0 else 3
            else:
                varga_sign = 3 if div_index == 0 else 4
            return (varga_sign * 30.0) + ((deg % div_size) / div_size * 30.0)
    elif varga == "D3":
        div_size = 10.0
        div_index = int(deg // div_size)
        varga_sign = (sign_idx + div_index * 4) % 12
        return (varga_sign * 30.0) + ((deg % div_size) / div_size * 30.0)
    elif varga == "D4":
        div_size = 7.5
        div_index = int(deg // div_size)
        varga_sign = (sign_idx + div_index * 3) % 12
        return (varga_sign * 30.0) + ((deg % div_size) / div_size * 30.0)
    elif varga == "D7":
        start = sign_idx if is_odd else (sign_idx + 6) % 12
        return uniform_varga(7, start)
    elif varga == "D9":
        element = sign_idx % 4
        start = (element * 9) % 12
        return uniform_varga(9, start)
    elif varga == "D10":
        div_size = 3.0
        div_index = int(deg // div_size)
        if is_odd:
            varga_sign = (sign_idx + div_index) % 12
        else:
            if d10_mode in ("direct", "contemporary", "forward"):
                varga_sign = (sign_idx + 8 + div_index) % 12
            else:
                varga_sign = (sign_idx + 8 - div_index) % 12
        return (varga_sign * 30.0) + ((deg % div_size) / div_size * 30.0)
    elif varga == "D12":
        return uniform_varga(12, sign_idx)
    elif varga == "D16":
        modality = sign_idx % 3
        start = (modality * 4) % 12
        return uniform_varga(16, start)
    elif varga == "D20":
        modality = sign_idx % 3
        start = 0 if modality == 0 else (8 if modality == 1 else 4)
        return uniform_varga(20, start)
    elif varga == "D24":
        div_size = 30.0 / 24.0
        div_index = int(deg // div_size)
        if is_odd:
            varga_sign = (4 + div_index) % 12
        else:
            if d24_mode in ("direct", "contemporary", "forward"):
                varga_sign = (3 + div_index) % 12
            else:
                varga_sign = (3 - div_index) % 12
        return (varga_sign * 30.0) + ((deg % div_size) / div_size * 30.0)
    elif varga == "D27":
        element = sign_idx % 4
        start = (element * 3) % 12
        return uniform_varga(27, start)
    elif varga == "D30":
        if trimsamsa_mode == "harmonic":
            return (longitude * 30.0) % 360.0
        else:
            return calculate_unequal_trimsamsa(longitude)["longitude"]
    elif varga == "D40":
        start = 0 if is_odd else 6
        return uniform_varga(40, start)
    elif varga == "D45":
        modality = sign_idx % 3
        start = (modality * 4) % 12
        return uniform_varga(45, start)
    elif varga == "D60":
        return uniform_varga(60, sign_idx)
    else:
        harmonic = int(varga.replace("D", ""))
        return (longitude * harmonic) % 360.0


def calculate_unequal_trimsamsa(longitude: float) -> Dict[str, Any]:
    """Evaluates classical Parāśarī / Phaladeepika unequal Trimsamsa bounds (D30)."""
    sign_idx = int(longitude // 30)
    deg = longitude % 30.0
    is_odd = (sign_idx % 2 == 0)

    if is_odd:
        if deg < 5.0:
            ruler, t_sign, start, span = "Mars", "Aries", 0.0, 5.0
        elif deg < 10.0:
            ruler, t_sign, start, span = "Saturn", "Aquarius", 5.0, 5.0
        elif deg < 18.0:
            ruler, t_sign, start, span = "Jupiter", "Sagittarius", 10.0, 8.0
        elif deg < 25.0:
            ruler, t_sign, start, span = "Mercury", "Gemini", 18.0, 7.0
        else:
            ruler, t_sign, start, span = "Venus", "Libra", 25.0, 5.0
    else:
        if deg < 5.0:
            ruler, t_sign, start, span = "Venus", "Taurus", 0.0, 5.0
        elif deg < 12.0:
            ruler, t_sign, start, span = "Mercury", "Virgo", 5.0, 7.0
        elif deg < 20.0:
            ruler, t_sign, start, span = "Jupiter", "Pisces", 12.0, 8.0
        elif deg < 25.0:
            ruler, t_sign, start, span = "Saturn", "Capricorn", 20.0, 5.0
        else:
            ruler, t_sign, start, span = "Mars", "Scorpio", 25.0, 5.0

    t_s_idx = ZODIAC_SIGNS.index(t_sign)
    frac = max(0.0, min(0.999999, (deg - start) / span))
    scaled_deg = frac * 30.0
    mapped_lon = t_s_idx * 30.0 + scaled_deg

    return {
        "ruler": ruler,
        "sign": t_sign,
        "sign_index": t_s_idx,
        "start_degree": start,
        "end_degree": start + span,
        "span_degrees": span,
        "bound_degree": round(deg - start, 4),
        "fraction_in_bound": round(frac, 6),
        "degree_in_sign": round(scaled_deg, 4),
        "degree_0_to_30": round(scaled_deg, 4),
        "longitude": round(mapped_lon, 4)
    }


def calculate_shastiamsa_details(longitude: float) -> Dict[str, Any]:
    """Evaluates the 30-arcminute Shastiamsa (D60) deity, polarity, and harmonic sign."""
    sign_idx = int(longitude // 30)
    deg = longitude % 30.0
    is_odd = (sign_idx % 2 == 0)

    part_idx = min(59, int(deg // 0.5))  # 0 to 59
    classical_num = part_idx + 1         # 1 to 60 (sequential slice within sign)

    if is_odd:
        deity = SHASTIAMSA_DEITIES[part_idx]
        deity_num = classical_num
        is_malefic = deity_num in SHASTIAMSA_MALEFIC_ODD
    else:
        inverted_idx = 59 - part_idx
        deity = SHASTIAMSA_DEITIES[inverted_idx]
        deity_num = inverted_idx + 1
        is_malefic = deity_num in SHASTIAMSA_MALEFIC_ODD

    harmonic_lon = calculate_varga_longitude(longitude, "D60")
    h_idx = int(harmonic_lon // 30)

    return {
        "slice_number": classical_num,
        "shastiamsa_number": classical_num,
        "deity_number": deity_num,
        "deity": deity,
        "nature": "Ashubha / Malefic" if is_malefic else "Shubha / Benefic",
        "is_benefic": not is_malefic,
        "is_malefic": is_malefic,
        "harmonic_longitude": round(harmonic_lon, 4),
        "harmonic_sign": ZODIAC_SIGNS[h_idx],
        "degree_0_to_30": round(harmonic_lon % 30.0, 4)
    }


def get_varga_ruler_info(
    varga: str,
    sign_idx: int,
    deg_in_sign: float,
    d2_mode: str = "parashari",
    d10_mode: str = "reverse",
    d24_mode: str = "reverse",
    trimsamsa_mode: str = "parashari"
) -> Dict[str, Any]:
    """
    Returns planetary lord metadata, symbols, and classification across divisional charts.
    """
    is_odd = (sign_idx % 2 == 0)
    deg = deg_in_sign % 30.0

    if varga == "D2":
        div_size = 15.0
        div_index = min(1, int(deg // div_size))
        is_sun = (div_index == 0) if is_odd else (div_index == 1)
        hora_lord = "Sun" if is_sun else "Moon"
        hora_symbol = "☉" if is_sun else "☽"
        hora_polarity = "Solar" if is_sun else "Lunar"
        category = "Solar / Pingala" if is_sun else "Lunar / Ida"

        if d2_mode in ("cyclical", "parivritti", "12_signs"):
            v_sign_idx = (sign_idx + div_index * 6) % 12
            ruler = SIGN_LORDS[ZODIAC_SIGNS[v_sign_idx]]
            symbol = PLANET_SYMBOLS.get(ruler, "")
            return {
                "ruler": ruler,
                "symbol": symbol,
                "ruler_symbol": symbol,
                "category": category,
                "varga_type": "planetary",
                "is_planetary_varga": True,
                "hora_lord": hora_lord,
                "hora_symbol": hora_symbol,
                "hora_polarity": hora_polarity
            }
        else:
            return {
                "ruler": hora_lord,
                "symbol": hora_symbol,
                "ruler_symbol": hora_symbol,
                "category": category,
                "varga_type": "planetary",
                "is_planetary_varga": True,
                "hora_lord": hora_lord,
                "hora_symbol": hora_symbol,
                "hora_polarity": hora_polarity
            }

    elif varga == "D3":
        div_index = min(2, int(deg // 10.0))
        target_sign_idx = (sign_idx + div_index * 4) % 12
        ruler = SIGN_LORDS[ZODIAC_SIGNS[target_sign_idx]]
        symbol = PLANET_SYMBOLS.get(ruler, "")
        return {
            "ruler": ruler,
            "symbol": symbol,
            "ruler_symbol": symbol,
            "category": f"Drekkāṇa Trine {div_index + 1}",
            "varga_type": "planetary_triad",
            "is_planetary_varga": True
        }

    elif varga == "D30":
        base_lon = sign_idx * 30.0 + deg
        t_info = calculate_unequal_trimsamsa(base_lon)
        bound_ruler = t_info["ruler"]
        bound_symbol = PLANET_SYMBOLS.get(bound_ruler, "")

        if trimsamsa_mode == "harmonic":
            harmonic_lon = (base_lon * 30.0) % 360.0
            h_sign_idx = int(harmonic_lon // 30) % 12
            h_sign_name = ZODIAC_SIGNS[h_sign_idx]
            ruler = SIGN_LORDS[h_sign_name]
            symbol = PLANET_SYMBOLS.get(ruler, "")
            return {
                "ruler": ruler,
                "symbol": symbol,
                "ruler_symbol": symbol,
                "bound_ruler": bound_ruler,
                "bound_symbol": bound_symbol,
                "category": "Harmonic D30",
                "varga_type": "planetary_bounds",
                "is_planetary_varga": True
            }
        else:
            return {
                "ruler": bound_ruler,
                "symbol": bound_symbol,
                "ruler_symbol": bound_symbol,
                "bound_ruler": bound_ruler,
                "bound_symbol": bound_symbol,
                "bound_sign": t_info["sign"],
                "bound_degree": t_info["bound_degree"],
                "category": f"Triṁśāṁśa {bound_ruler}",
                "varga_type": "planetary_bounds",
                "is_planetary_varga": True
            }

    else:
        # Zodiacal Vargas (D1, D4, D7, D9, D10, D12, D16, D20, D24, D27, D40, D45, D60)
        base_lon = sign_idx * 30.0 + deg
        v_lon = calculate_varga_longitude(
            base_lon, varga, d10_mode=d10_mode, d24_mode=d24_mode, d2_mode=d2_mode, trimsamsa_mode=trimsamsa_mode
        )
        h_sign_idx = int((v_lon % 360.0) // 30) % 12
        h_sign_name = ZODIAC_SIGNS[h_sign_idx]
        ruler = SIGN_LORDS[h_sign_name]
        symbol = PLANET_SYMBOLS.get(ruler, "")
        return {
            "ruler": ruler,
            "symbol": symbol,
            "ruler_symbol": symbol,
            "category": f"{h_sign_name} Lord",
            "varga_type": "zodiacal",
            "is_planetary_varga": False
        }


def calculate_baladi_state(sign: str, deg_in_sign: float) -> Dict[str, Any]:
    """Calculates Baladi Avastha (5 physical age states per sign) with odd/even parity."""
    is_odd = (ZODIAC_SIGNS.index(sign) % 2 == 0)
    deg = max(0.0, min(29.9999, float(deg_in_sign)))
    segment = int(deg // 6.0)

    if is_odd:
        states = ["Bala (Infant)", "Kumara (Youth)", "Yuva (Adult/Prime)", "Vriddha (Elderly)", "Mrita (Dead)"]
        efficiency = [0.25, 0.50, 1.00, 0.10, 0.00]
    else:
        states = ["Mrita (Dead)", "Vriddha (Elderly)", "Yuva (Adult/Prime)", "Kumara (Youth)", "Bala (Infant)"]
        efficiency = [0.00, 0.10, 1.00, 0.50, 0.25]

    return {
        "state": states[segment],
        "segment": segment + 1,
        "efficiency_factor": efficiency[segment],
        "efficiency_pct": int(efficiency[segment] * 100),
        "is_odd_sign": is_odd
    }


def get_eq_from_ecl(ecl_lon: float, eps_degrees: float = 23.4392911) -> Tuple[float, float]:
    """
    Transforms Ecliptic Longitude (assuming ecliptic latitude 0) to Equatorial (RA, Dec).
    eps_degrees: Obliquity of the ecliptic in degrees.
    """
    eps = math.radians(eps_degrees)
    lam = math.radians(ecl_lon)
    sin_d = math.sin(eps) * math.sin(lam)
    dec = math.degrees(math.asin(max(-1.0, min(1.0, sin_d))))
    ra = math.degrees(math.atan2(math.cos(eps) * math.sin(lam), math.cos(lam))) % 360.0
    return ra, dec


def find_preceding_solar_crossing(target_deg: float, jd_current: float, sun_lon: Optional[float] = None) -> float:
    """
    Finds the exact Julian Day when the Sun crossed target_deg preceding jd_current.
    Uses Swiss Ephemeris solcross_ut with Newton-Raphson fallback.
    """
    if sun_lon is None:
        sun_res, _ = swe.calc_ut(jd_current, swe.SUN, swe.FLG_SWIEPH)
        sun_lon = sun_res[0] % 360.0

    deg_back = (sun_lon - target_deg) % 360.0
    if deg_back < 0.0001:
        deg_back = 360.0
    approx_jd = jd_current - (deg_back / 0.9856) - 1.5

    if hasattr(swe, 'solcross_ut'):
        try:
            cross_jd = swe.solcross_ut(target_deg, approx_jd, swe.FLG_SWIEPH)
            if cross_jd <= jd_current and (jd_current - cross_jd) <= 375.0:
                return cross_jd
        except Exception:
            pass

    # High precision Newton-Raphson fallback
    t = jd_current - (deg_back / 0.9856)
    for _ in range(12):
        res, _ = swe.calc_ut(t, swe.SUN, swe.FLG_SWIEPH | swe.FLG_SPEED)
        cur_lon = res[0] % 360.0
        speed = res[3]
        diff = (cur_lon - target_deg)
        diff = (diff + 180.0) % 360.0 - 180.0
        t -= diff / speed
        if abs(diff) < 1e-7:
            break
    if t > jd_current:
        t -= 365.25
    return t


def calculate_interpolated_node(target_jd: float) -> float:
    """
    Calculates Ernst Wilhelm's 'Interpolated True Node'.
    
    Determines the exact moments of the Moon's previous and next 
    ecliptic crossings (where Moon ecliptic latitude = 0) and linearly 
    interpolates the node's longitude between those two crossing epochs.
    Note: Specialized research utility; True Node in standard pipeline
    uses Swiss Ephemeris swe.TRUE_NODE directly.
    """
    import scipy.optimize as opt

    def _get_moon_lat(jd: float) -> float:
        res, _ = swe.calc_ut(jd, swe.MOON, swe.FLG_SWIEPH)
        return res[1]

    def _get_moon_lon(jd: float) -> float:
        res, _ = swe.calc_ut(jd, swe.MOON, swe.FLG_SWIEPH)
        return res[0]

    jd = target_jd
    while _get_moon_lat(jd) * _get_moon_lat(jd - 1) > 0:
        jd -= 1
    t1 = opt.brentq(_get_moon_lat, jd - 1, jd)

    jd = target_jd
    while _get_moon_lat(jd) * _get_moon_lat(jd + 1) > 0:
        jd += 1
    t2 = opt.brentq(_get_moon_lat, jd, jd + 1)

    lat_before_t1 = _get_moon_lat(t1 - 0.1)
    is_ascending_t1 = lat_before_t1 < 0
    lat_before_t2 = _get_moon_lat(t2 - 0.1)
    is_ascending_t2 = lat_before_t2 < 0

    def _get_rahu_at_crossing(t: float, is_asc: bool) -> float:
        moon_lon = _get_moon_lon(t)
        return moon_lon if is_asc else (moon_lon + 180.0) % 360.0

    rahu_1 = _get_rahu_at_crossing(t1, is_ascending_t1)
    rahu_2 = _get_rahu_at_crossing(t2, is_ascending_t2)

    # Handle 360 degree wrap around
    if rahu_1 - rahu_2 > 180:
        rahu_2 += 360
    elif rahu_2 - rahu_1 > 180:
        rahu_1 += 360

    fraction = (target_jd - t1) / (t2 - t1)
    interp_rahu = rahu_1 + fraction * (rahu_2 - rahu_1)
    return interp_rahu % 360.0
