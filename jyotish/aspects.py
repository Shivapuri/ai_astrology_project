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

def get_graha_drishti(aspecting_planet: str, aspecting_lon: float, aspected_lon: float) -> float:
    """
    Calculates the exact fractional strength of the planetary aspect (Graha Drishti)
    cast by `aspecting_planet` upon the longitude `aspected_lon`.
    Returns a float from 0.0 to 60.0 (Virupas).
    
    Note: Rahu and Ketu do not cast Graha Drishti in strict Parashara methodology.
    """
    if aspecting_planet in ["Rahu", "Ketu"]:
        return 0.0
        
    diff = (aspected_lon - aspecting_lon) % 360.0
    
    # Base Drishti (calculated according to BPHS Ch 26 / 27 piecewise function)
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
        raw_drishti = 150.0 - diff
    elif diff <= 180.0:
        raw_drishti = (diff - 150.0) * 2.0
    elif diff <= 300.0:
        raw_drishti = (300.0 - diff) / 2.0
    else:
        raw_drishti = 0.0
        
    # Apply Special Planetary Aspects
    # Saturn 3/10 (60-90, 270-300). Center is 75 and 285.
    if aspecting_planet == "Saturn":
        if 60.0 <= diff <= 90.0:
            raw_drishti = max(raw_drishti, 60.0 - abs(diff - 75.0))
        elif 270.0 <= diff <= 300.0:
            raw_drishti = max(raw_drishti, 60.0 - abs(diff - 285.0))
            
    # Jupiter 5/9 (120-150, 240-270). Center is 135 and 255.
    elif aspecting_planet == "Jupiter":
        if 120.0 <= diff <= 150.0:
            raw_drishti = max(raw_drishti, 60.0 - abs(diff - 135.0))
        elif 240.0 <= diff <= 270.0:
            raw_drishti = max(raw_drishti, 60.0 - abs(diff - 255.0))
            
    # Mars 4/8 (90-120, 210-240). Center is 105 and 225.
    elif aspecting_planet == "Mars":
        if 90.0 <= diff <= 120.0:
            raw_drishti = max(raw_drishti, 60.0 - abs(diff - 105.0))
        elif 210.0 <= diff <= 240.0:
            raw_drishti = max(raw_drishti, 60.0 - abs(diff - 225.0))
            
    return min(max(raw_drishti, 0.0), 60.0)

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
