"""
aspects.py

Core engine for calculating astrological aspects (Drishti).
Implements Ernst Wilhelm / Kala Software methodology, including:
1. Rasi Drishti (Sign-to-Sign Aspects) - Mutual and binary.
2. Graha Drishti (Planetary Longitude Aspects) - Continuous fractional strength.
"""

from typing import List, Dict, Any, Optional, Union
from jyotish.baseline import (
    ChartBaseline,
    ALL_BODIES,
    ZODIAC_SIGNS,
    PLANETS_ORDER,
    SIGN_LORDS,
)

PHYSICAL_PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
NON_CASTING_BODIES = ["Rahu", "Ketu", "Lagna", "MC"]


def get_rasi_drishti(sign: str) -> List[str]:
    """
    Returns a list of signs that the given sign aspects via Rasi Drishti.
    - Cardinal/Moveable signs (Aries, Cancer, Libra, Capricorn) aspect all Fixed signs EXCEPT the adjacent one.
    - Fixed signs (Taurus, Leo, Scorpio, Aquarius) aspect all Cardinal signs EXCEPT the adjacent one.
    - Dual/Mutable signs (Gemini, Virgo, Sagittarius, Pisces) aspect all other Dual signs.
    """
    cardinal = ["Aries", "Cancer", "Libra", "Capricorn"]
    fixed = ["Taurus", "Leo", "Scorpio", "Aquarius"]
    dual = ["Gemini", "Virgo", "Sagittarius", "Pisces"]
    
    if sign in cardinal:
        # Avoid the fixed sign immediately next to it
        if sign == "Aries": return ["Leo", "Scorpio", "Aquarius"]
        if sign == "Cancer": return ["Scorpio", "Aquarius", "Taurus"]
        if sign == "Libra": return ["Aquarius", "Taurus", "Leo"]
        if sign == "Capricorn": return ["Taurus", "Leo", "Scorpio"]
        
    elif sign in fixed:
        # Avoid the cardinal sign immediately before it
        if sign == "Taurus": return ["Cancer", "Libra", "Capricorn"]
        if sign == "Leo": return ["Libra", "Capricorn", "Aries"]
        if sign == "Scorpio": return ["Capricorn", "Aries", "Cancer"]
        if sign == "Aquarius": return ["Aries", "Cancer", "Libra"]
        
    elif sign in dual:
        return [s for s in dual if s != sign]
        
    return []

def get_graha_drishti(aspecting_planet: str, aspecting_lon: float, aspected_lon: float, aspecting_sign: str = None, aspected_sign: str = None) -> float:
    """
    Calculates the exact fractional strength of the planetary aspect (Graha Drishti)
    cast by `aspecting_planet` upon the longitude `aspected_lon`.
    Returns a float from 0.0 to 60.0 (Virupas).
    """
    if aspecting_planet in NON_CASTING_BODIES:
        return 0.0
        
    diff = (aspected_lon - aspecting_lon) % 360.0
    
    # Base Drishti (calculated according to BPHS/BV Raman piecewise function)
    raw_drishti = 0.0
    if diff <= 30.0:
        raw_drishti = 0.0
    elif diff <= 60.0:
        raw_drishti = (diff - 30.0) / 2.0
    elif diff <= 90.0:
        raw_drishti = (diff - 60.0) + 15.0
    elif diff <= 120.0:
        raw_drishti = (120.0 - diff) / 2.0 + 30.0
    elif diff <= 150.0:
        raw_drishti = (150.0 - diff)
    elif diff <= 180.0:
        raw_drishti = (diff - 150.0) * 2.0
    elif diff <= 300.0:
        raw_drishti = (300.0 - diff) / 2.0
    else:
        raw_drishti = 0.0

    # Visesha Drishti (Special Aspects) using Triangle Wave interpolation (Kala exact math)
    def apply_special_bonus(current_raw, peak_degree, peak_bonus):
        # The bonus applies within +/- 30 degrees of the peak
        dist = abs(diff - peak_degree)
        if dist < 30.0:
            bonus = peak_bonus * (1.0 - (dist / 30.0))
            return current_raw + bonus
        return current_raw

    if aspecting_planet == "Saturn":
        raw_drishti = apply_special_bonus(raw_drishti, 60.0, 45.0)  # 3rd aspect
        raw_drishti = apply_special_bonus(raw_drishti, 270.0, 45.0) # 10th aspect
    elif aspecting_planet == "Jupiter":
        raw_drishti = apply_special_bonus(raw_drishti, 120.0, 30.0) # 5th aspect
        raw_drishti = apply_special_bonus(raw_drishti, 240.0, 30.0) # 9th aspect
    elif aspecting_planet == "Mars":
        raw_drishti = apply_special_bonus(raw_drishti, 90.0, 15.0)  # 4th aspect
        raw_drishti = apply_special_bonus(raw_drishti, 210.0, 15.0) # 8th aspect
            
    return float(min(max(raw_drishti, 0.0), 60.0))

def get_aspect_explanation(
    aspecting_planet: str,
    aspecting_lon: float,
    aspected_lon: float,
    aspected_name: str = "",
    aspecting_dignity: str = "Neutral",
    is_moon_bright: bool = True,
    is_mercury_afflicted: bool = False,
) -> Dict[str, Any]:
    """
    Returns detailed explanation for Graha Drishti between two coordinates,
    including exact angular separation, Virūpa potency, Parāśara rule name,
    whether the aspect is Benefic (Śubha) or Malefic (Aśubha), and suggested line style.
    Anchored to exact angular milestone proximity (Sphuṭa Dṛṣṭi).
    """
    if aspecting_planet in NON_CASTING_BODIES:
        return {
            "aspecting": aspecting_planet,
            "aspected": aspected_name,
            "separation_deg": round((aspected_lon - aspecting_lon) % 360.0, 1),
            "virupas": 0.0,
            "rule_name": f"{aspecting_planet} does not cast Graha Dṛṣṭi",
            "is_benefic": False,
            "line_style": "none",
            "nature_label": "Non-Casting Point",
            "dignity": aspecting_dignity,
        }

    diff = (aspected_lon - aspecting_lon) % 360.0
    virupas = get_graha_drishti(aspecting_planet, aspecting_lon, aspected_lon)

    if virupas == 0.0:
        rule_name = f"No Aspect / Blind Angle ({round(diff, 1)}° separation)"
        line_style = "none"
        nature_label = "No Aspect (0 Virūpas)"
        is_benefic = False
    else:
        # Classical Benefic/Malefic Determination (BPHS Ch. 3 / Phaladīpikā Ch. 2)
        if aspecting_planet in ["Jupiter", "Venus"]:
            is_benefic = True
        elif aspecting_planet == "Mercury":
            is_benefic = not is_mercury_afflicted
        elif aspecting_planet == "Moon":
            is_benefic = is_moon_bright
        else:
            is_benefic = False

        line_style = "continuous" if is_benefic else "dashed"
        nature_label = (
            "Benefic Light (Śubha Dṛṣṭi — Continuous line)"
            if is_benefic
            else "Malefic Tension (Aśubha Dṛṣṭi — Dashed line)"
        )

        # Milestone proximity rules
        if aspecting_planet == "Mars" and abs(diff - 210.0) < 30.0:
            rule_name = f"Mars Special 8th Glance / Randhra ({round(diff, 1)}° separation)"
        elif aspecting_planet == "Mars" and abs(diff - 90.0) < 30.0:
            rule_name = f"Mars Special 4th Glance / Caturasra ({round(diff, 1)}° separation)"
        elif aspecting_planet == "Jupiter" and abs(diff - 120.0) < 30.0:
            rule_name = f"Jupiter Special 5th Glance / Trikona ({round(diff, 1)}° separation)"
        elif aspecting_planet == "Jupiter" and abs(diff - 240.0) < 30.0:
            rule_name = f"Jupiter Special 9th Glance / Dharma ({round(diff, 1)}° separation)"
        elif aspecting_planet == "Saturn" and abs(diff - 60.0) < 30.0:
            rule_name = f"Saturn Special 3rd Glance / Upachaya ({round(diff, 1)}° separation)"
        elif aspecting_planet == "Saturn" and abs(diff - 270.0) < 30.0:
            rule_name = f"Saturn Special 10th Glance / Karma ({round(diff, 1)}° separation)"
        elif abs(diff - 180.0) <= 15.0:
            rule_name = f"7th Full Opposition Glance ({round(diff, 1)}° separation)"
        else:
            rule_name = f"General Parāśarī Graduated Glance ({round(diff, 1)}° separation)"

    return {
        "aspecting": aspecting_planet,
        "aspected": aspected_name,
        "separation_deg": round(diff, 1),
        "virupas": round(virupas, 1),
        "rule_name": rule_name,
        "is_benefic": is_benefic,
        "line_style": line_style,
        "nature_label": nature_label,
        "dignity": aspecting_dignity,
    }

def get_all_graha_drishtis(planets_data: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, float]]:
    """
    Calculates the incoming Graha Drishti (aspect strength) for all planets from all other planets.
    Returns a nested dictionary: { aspected_planet: { aspecting_planet: virupas } }
    """
    results = {}
    for aspected, aspected_info in planets_data.items():
        results[aspected] = {}
        for aspecting, aspecting_info in planets_data.items():
            if aspected == aspecting:
                continue
                
            aspected_lon = aspected_info.get("longitude", 0.0)
            aspecting_lon = aspecting_info.get("longitude", 0.0)
            
            drishti_val = get_graha_drishti(aspecting, aspecting_lon, aspected_lon)
            if drishti_val > 0.0:
                results[aspected][aspecting] = round(drishti_val, 2)
                
    return results

def get_all_rasi_drishtis(planets_data: Dict[str, Dict[str, Any]]) -> Dict[str, List[str]]:
    """
    Calculates incoming Rasi Drishtis for planets.
    Returns { aspected_planet: [list of aspecting planets] }
    """
    # Map which planets are in which signs
    signs_to_planets = {sign: [] for sign in ZODIAC_SIGNS}
    for p_name, p_data in planets_data.items():
        sign = p_data.get("sign")
        if sign in signs_to_planets:
            signs_to_planets[sign].append(p_name)
            
    results = {p: [] for p in planets_data.keys()}
    
    for aspecting_planet, aspecting_data in planets_data.items():
        aspecting_sign = aspecting_data.get("sign")
        if not aspecting_sign: continue
            
        aspected_signs = get_rasi_drishti(aspecting_sign)
        for aspected_sign in aspected_signs:
            for aspected_planet in signs_to_planets[aspected_sign]:
                if aspecting_planet != aspected_planet:
                    results[aspected_planet].append(aspecting_planet)
                    
    return results

def calculate_advanced_graha_aspects(planets_data: dict, shadbala_data: dict, house_cusps: list = None, ascendant_lon: float = None) -> dict:
    """
    Calculates the advanced +/- Graha Aspects.
    Returns:
    {
        "planets": { aspected_planet: { aspecting_planet: {"raw": val, "plus": val, "minus": val, "net": val} } },
        "cusps": { house_num: { aspecting_planet: {"raw": val, "plus": val, "minus": val, "net": val} } },
        "equal_cusps": { house_num: { aspecting_planet: {"raw": val, "plus": val, "minus": val, "net": val} } },
        "totals": {
            "planets": { aspected_planet: {"plus": val, "minus": val, "net": val} },
            "cusps": { house_num: {"plus": val, "minus": val, "net": val} },
            "equal_cusps": { house_num: {"plus": val, "minus": val, "net": val} }
        }
    }
    """
    results = {"planets": {}, "cusps": {}, "equal_cusps": {}, "totals": {"planets": {}, "cusps": {}, "equal_cusps": {}}, "yutis": {}}
    
    # Helper to determine if planet is benefic or malefic for Drishti
    def is_benefic(p_name, moon_lon, sun_lon, aspecting_sign=None):
        if p_name in ["Jupiter", "Venus"]:
            return True
        if p_name == "Mercury":
            if aspecting_sign:
                has_mal = any(
                    other_info.get("sign") == aspecting_sign
                    for m_name, other_info in planets_data.items()
                    if m_name in ["Sun", "Mars", "Saturn", "Rahu", "Ketu"]
                )
                if has_mal:
                    return False
            return True
        if p_name == "Moon":
            diff = (moon_lon - sun_lon) % 360.0
            return 30.0 <= diff <= 330.0
        return False

    sun_lon = planets_data.get("Sun", {}).get("longitude", 0.0)
    moon_lon = planets_data.get("Moon", {}).get("longitude", 0.0)

    # Helper to calculate and store aspect
    def calc_aspects(aspected_key, aspected_lon, target_dict, totals_dict):
        target_dict[aspected_key] = {}
        totals_dict[aspected_key] = {"plus": 0.0, "minus": 0.0, "net": 0.0}
        
        for aspecting, aspecting_info in planets_data.items():
            if aspecting in NON_CASTING_BODIES or aspecting == aspected_key:
                continue
                
            aspecting_lon = aspecting_info.get("longitude", 0.0)
            sign1 = aspecting_info.get("sign")
            # If aspected_key is a planet, we might have its sign. If it's a house, sign2 is None.
            sign2 = planets_data.get(aspected_key, {}).get("sign") if isinstance(aspected_key, str) else None
            
            raw = get_graha_drishti(aspecting, aspecting_lon, aspected_lon, sign1, sign2)
            
            if raw > 0:
                plus = 0.0
                minus = 0.0
                
                # Check house lord protection on cusp evaluation
                target_lord = None
                if isinstance(aspected_key, int) and ascendant_lon is not None:
                    asc_sign_idx = int(ascendant_lon // 30) % 12
                    target_sign_idx = (asc_sign_idx + aspected_key - 1) % 12
                    target_lord = SIGN_LORDS[ZODIAC_SIGNS[target_sign_idx]]

                if aspecting == target_lord or is_benefic(aspecting, moon_lon, sun_lon, sign1):
                    plus = raw
                else:
                    minus = raw
                    
                net = plus - minus
                
                target_dict[aspected_key][aspecting] = {
                    "raw": round(raw, 2),
                    "plus": round(plus, 2),
                    "minus": round(minus, 2),
                    "net": round(net, 2)
                }
                
                totals_dict[aspected_key]["plus"] += plus
                totals_dict[aspected_key]["minus"] += minus
                totals_dict[aspected_key]["net"] += net
                
        # Round totals
        totals_dict[aspected_key]["plus"] = round(totals_dict[aspected_key]["plus"], 2)
        totals_dict[aspected_key]["minus"] = round(totals_dict[aspected_key]["minus"], 2)
        totals_dict[aspected_key]["net"] = round(totals_dict[aspected_key]["net"], 2)

    # 1. Aspects to Planets and Yutis
    for aspected, aspected_info in planets_data.items():
        # Rahu and Ketu cannot cast Graha Drishti, but they DO receive aspects
        # and form Yutis (conjunctions) with planets in the same sign.
        
        # Calculate Yutis (Conjunctions in same sign)
        results["yutis"][aspected] = []
        aspected_sign = aspected_info.get("sign")
        for other, other_info in planets_data.items():
            if other != aspected and other not in NON_CASTING_BODIES and aspected_sign and other_info.get("sign") == aspected_sign:
                results["yutis"][aspected].append(other)
                
        aspected_lon = aspected_info.get("longitude", 0.0)
        calc_aspects(aspected, aspected_lon, results["planets"], results["totals"]["planets"])

    # 2. Aspects to Bhava Chalita Cusps
    if house_cusps:
        for idx, cusp in enumerate(house_cusps):
            h_num = idx + 1
            cusp_lon = cusp.get("longitude", 0.0)
            calc_aspects(h_num, cusp_lon, results["cusps"], results["totals"]["cusps"])
            
    # 3. Aspects to Equal Houses
    if ascendant_lon is not None:
        for h_num in range(1, 13):
            equal_lon = (ascendant_lon + (h_num - 1) * 30.0) % 360.0
            calc_aspects(h_num, equal_lon, results["equal_cusps"], results["totals"]["equal_cusps"])

    return results

def calculate_varga_aspects(baseline: Any, varga: str = "D1") -> Dict[str, Any]:
    """
    High-Level Multi-Varga Aspect Helper.
    Directly accepts either a ChartBaseline instance and varga name,
    a vargas container dictionary, or directly a single varga dictionary (e.g., baseline.vargas[varga]).

    Refactors the legacy interface so callers in generate_jyotish.py and downstream
    engines do not need to manually unpack longitude lists, cusps, and ascendants.
    """
    if hasattr(baseline, "vargas"):
        varga_data = baseline.vargas.get(varga, {})
    elif isinstance(baseline, dict) and "vargas" in baseline:
        varga_data = baseline["vargas"].get(varga, {})
    elif isinstance(baseline, dict) and "grahas" in baseline:
        varga_data = baseline
    elif isinstance(baseline, dict) and varga in baseline:
        varga_data = baseline[varga]
    else:
        varga_data = {}

    planets_data = varga_data.get("grahas", {})
    house_cusps = varga_data.get("cusps", [])
    lagna_info = varga_data.get("lagna", {})
    ascendant_lon = lagna_info.get("longitude", 0.0) if isinstance(lagna_info, dict) else float(lagna_info or 0.0)

    return calculate_advanced_graha_aspects(
        planets_data=planets_data,
        shadbala_data={},
        house_cusps=house_cusps,
        ascendant_lon=ascendant_lon
    )


def calculate_aspect_matrices(baseline: "ChartBaseline") -> Dict[str, Any]:
    """
    Master Stage 2A Aspect Orchestrator.
    Consumes ChartBaseline directly to generate:
    1. Graha Drishti (0–60 Virupas): Planet-to-Planet (both outgoing & incoming)
    2. Graha Drishti to Cusps: 7 Physical Planets to 12 Whole-Sign House Cusps
    3. Rasi Drishti: Binary sign-to-sign and planet-to-planet mutual aspects
    4. Benefic / Malefic Breakdown: Subha (+) vs Asubha (-) Virūpa totals
    """
    coords = baseline.coordinates
    sep_matrix = baseline.separation_matrix
    sens_deg = baseline.astronomical_anchors["sensitive_cusp_degree"]
    asc_sign_idx = coords["Lagna"]["sign_index"]

    # 1. Graha Drishti: Planet-to-Planet (11x11)
    # Source separations directly from baseline.separation_matrix[b1][b2].
    # Rahu, Ketu, Lagna, and MC cast 0 Virupas, but receive aspects from the classical 7 planets.
    outgoing = {b1: {} for b1 in ALL_BODIES}
    incoming = {b2: {} for b2 in ALL_BODIES}

    for b1 in ALL_BODIES:
        for b2 in ALL_BODIES:
            if b1 == b2 or b1 in NON_CASTING_BODIES:
                val = 0.0
            else:
                sep = sep_matrix[b1][b2]
                val = round(get_graha_drishti(b1, 0.0, sep), 4)
            outgoing[b1][b2] = val
            incoming[b2][b1] = val

    # 2. Graha Drishti: Planet-to-Cusp (7x12)
    # Evaluates aspects from the 7 physical planets onto the 12 whole-sign sensitive cusps
    # (D_asc projected from the Ascendant's sign).
    cusp_longitudes = {}
    for h in range(1, 13):
        target_sign_idx = (asc_sign_idx + h - 1) % 12
        cusp_lon = (target_sign_idx * 30.0 + sens_deg) % 360.0
        cusp_longitudes[h] = round(cusp_lon, 4)

    cusp_by_planet = {p: {} for p in PHYSICAL_PLANETS}
    cusp_by_house = {h: {} for h in range(1, 13)}

    for p in PHYSICAL_PLANETS:
        p_lon = coords[p]["longitude"]
        for h in range(1, 13):
            c_lon = cusp_longitudes[h]
            val = round(get_graha_drishti(p, p_lon, c_lon), 4)
            cusp_by_planet[p][h] = val
            cusp_by_house[h][p] = val

    # 3. Rasi Drishti (Sign & Planetary Mutual Glances)
    sign_to_signs = {sign: get_rasi_drishti(sign) for sign in ZODIAC_SIGNS}

    # Planet aspects: For any two bodies, determine whether their D1 signs aspect each other via get_rasi_drishti
    rasi_planet_to_planet = {}
    for b1 in ALL_BODIES:
        s1 = coords[b1]["sign"]
        aspected_signs = sign_to_signs[s1]
        rasi_planet_to_planet[b1] = [
            b2 for b2 in ALL_BODIES
            if b2 != b1 and coords[b2]["sign"] in aspected_signs
        ]

    # House aspects: List of planets aspecting whole-sign house h
    rasi_house_to_planets = {}
    for h in range(1, 13):
        target_sign_idx = (asc_sign_idx + h - 1) % 12
        h_sign = ZODIAC_SIGNS[target_sign_idx]
        aspecting_signs = sign_to_signs[h_sign]
        rasi_house_to_planets[h] = [
            p for p in PLANETS_ORDER
            if coords[p]["sign"] in aspecting_signs
        ]

    # 4. Benefic / Malefic Qualitative Totals (+ / - Net Virupas)
    # Natural Benefics: Jupiter, Venus
    # Dynamic Benefics:
    #   Mercury: Benefic if not combust and not conjoined with natural malefics (BPHS Ch. 3 / Phaladeepika Ch. 2.27)
    #   Moon: Benefic if bright/waxing (lunar_phase["is_benefic"] is True)
    # Natural Malefics: Sun, Mars, Saturn, Rahu, Ketu
    is_merc_combust = baseline.combustion_status.get("Mercury", {}).get("is_combust", False)
    merc_sign_idx = coords["Mercury"]["sign_index"]
    merc_with_malefic = any(
        m in coords and coords[m]["sign_index"] == merc_sign_idx
        for m in ["Sun", "Mars", "Saturn", "Rahu", "Ketu"]
    )
    is_merc_benefic = (not is_merc_combust) and (not merc_with_malefic)
    is_moon_benefic = baseline.lunar_phase.get("is_benefic", False)

    benefic_classification = {
        "Jupiter": True,
        "Venus": True,
        "Mercury": is_merc_benefic,
        "Moon": is_moon_benefic,
        "Sun": False,
        "Mars": False,
        "Saturn": False,
        "Rahu": False,
        "Ketu": False,
    }

    totals_planets = {}
    for b in ALL_BODIES:
        ben_v = 0.0
        mal_v = 0.0
        for p in PHYSICAL_PLANETS:
            if p == b:
                continue
            aspect_val = incoming[b][p]
            if benefic_classification[p]:
                ben_v += aspect_val
            else:
                mal_v += aspect_val
        totals_planets[b] = {
            "benefic_virupas": round(ben_v, 4),
            "malefic_virupas": round(mal_v, 4),
            "net_virupas": round(ben_v - mal_v, 4),
            "plus": round(ben_v, 4),
            "minus": round(mal_v, 4),
            "net": round(ben_v - mal_v, 4),
        }

    totals_cusps = {}
    for h in range(1, 13):
        target_sign_idx = (asc_sign_idx + h - 1) % 12
        h_sign = ZODIAC_SIGNS[target_sign_idx]
        h_lord = SIGN_LORDS[h_sign]

        ben_v = 0.0
        mal_v = 0.0
        for p in PHYSICAL_PLANETS:
            aspect_val = cusp_by_house[h][p]
            # Lord of the house protects its own cusp regardless of natural malefic status (Phaladeepika 15.1-3)
            if benefic_classification[p] or p == h_lord:
                ben_v += aspect_val
            else:
                mal_v += aspect_val
        totals_cusps[h] = {
            "benefic_virupas": round(ben_v, 4),
            "malefic_virupas": round(mal_v, 4),
            "net_virupas": round(ben_v - mal_v, 4),
            "plus": round(ben_v, 4),
            "minus": round(mal_v, 4),
            "net": round(ben_v - mal_v, 4),
        }

    return {
        "graha_drishti": {
            "outgoing": outgoing,
            "incoming": incoming,
        },
        "cusp_drishti": {
            "by_planet": cusp_by_planet,
            "by_house": cusp_by_house,
            "cusp_longitudes": cusp_longitudes,
        },
        "rasi_drishti": {
            "sign_to_signs": sign_to_signs,
            "planet_to_planet": rasi_planet_to_planet,
            "house_to_planets": rasi_house_to_planets,
        },
        "benefic_malefic_totals": {
            "planets": totals_planets,
            "cusps": totals_cusps,
            "classification": benefic_classification,
        },
        # Backwards compatibility aliases
        "planet_to_planet": outgoing,
        "planet_to_cusp": cusp_by_planet,
        "totals": {
            "planets": totals_planets,
            "cusps": totals_cusps,
        },
        "benefic_malefic_breakdown": {
            "planets": totals_planets,
            "cusps": totals_cusps,
        },
    }

