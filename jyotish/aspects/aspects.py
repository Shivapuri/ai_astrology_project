"""
aspects.py

Core engine for calculating astrological aspects (Drishti).
Implements Ernst Wilhelm / Kala Software methodology, including:
1. Rasi Drishti (Sign-to-Sign Aspects) - Mutual and binary.
2. Graha Drishti (Planetary Longitude Aspects) - Continuous fractional strength.
"""

from typing import List, Dict, Any

ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

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
    if aspecting_planet in ["Rahu", "Ketu"]:
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
    results = {"planets": {}, "cusps": {}, "equal_cusps": {}, "totals": {"planets": {}, "cusps": {}, "equal_cusps": {}}}
    
    # Helper to determine if planet is benefic or malefic for Drishti
    def is_benefic(p_name, moon_lon, sun_lon):
        if p_name in ["Jupiter", "Venus", "Mercury"]:
            return True
        if p_name == "Moon":
            diff = (moon_lon - sun_lon) % 360.0
            return diff < 180.0
        return False

    sun_lon = planets_data.get("Sun", {}).get("longitude", 0.0)
    moon_lon = planets_data.get("Moon", {}).get("longitude", 0.0)

    # Helper to calculate and store aspect
    def calc_aspects(aspected_key, aspected_lon, target_dict, totals_dict):
        target_dict[aspected_key] = {}
        totals_dict[aspected_key] = {"plus": 0.0, "minus": 0.0, "net": 0.0}
        
        for aspecting, aspecting_info in planets_data.items():
            if aspecting in ["Rahu", "Ketu"] or aspecting == aspected_key:
                continue
                
            aspecting_lon = aspecting_info.get("longitude", 0.0)
            sign1 = aspecting_info.get("sign")
            # If aspected_key is a planet, we might have its sign. If it's a house, sign2 is None.
            sign2 = planets_data.get(aspected_key, {}).get("sign") if isinstance(aspected_key, str) else None
            
            raw = get_graha_drishti(aspecting, aspecting_lon, aspected_lon, sign1, sign2)
            
            if raw > 0:
                plus = 0.0
                minus = 0.0
                
                if is_benefic(aspecting, moon_lon, sun_lon):
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

    # 1. Aspects to Planets
    for aspected, aspected_info in planets_data.items():
        if aspected in ["Rahu", "Ketu"]: continue
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
