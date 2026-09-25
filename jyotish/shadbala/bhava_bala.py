"""
jyotish/shadbala/bhava_bala.py
Complete 12-House Strength (Bhava Bala) Engine.
Implements the 3 classical pillars of Bhava Bala per BPHS Chapters 28-30:
1. Bhavadhipathi Bala (House Lord's Total Shadbala Virupas)
2. Bhava Digbala (Directional House Strength based on Nara, Jalachara, Chathushpada, Keeta)
3. Bhava Drishti Bala (Aspectual rays cast on the Bhava Madhya / Cusp)
"""

import math
import jyotish.aspects.aspects as aspects
from jyotish.relationships.relationships import SIGN_LORDS

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", 
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

def get_sign_genus(sign_name: str, deg_in_sign: float) -> str:
    """Classifies sign degree into Nara, Jalachara, Chathushpada, or Keeta."""
    if sign_name in ["Gemini", "Virgo", "Libra", "Aquarius"]:
        return "Nara"
    if sign_name == "Sagittarius":
        return "Nara" if deg_in_sign < 15.0 else "Chathushpada"
    if sign_name in ["Cancer", "Pisces"]:
        return "Jalachara"
    if sign_name == "Capricorn":
        return "Chathushpada" if deg_in_sign < 15.0 else "Jalachara"
    if sign_name in ["Aries", "Taurus", "Leo"]:
        return "Chathushpada"
    if sign_name == "Scorpio":
        return "Keeta"
    return "Nara"

def calculate_bhava_dig_bala(bhava_num: int, bhava_madhya_lon: float) -> float:
    """Computes Bhava Digbala (0 to 60 Virupas)."""
    sign_idx = int((bhava_madhya_lon % 360.0) / 30.0)
    deg_in_sign = bhava_madhya_lon % 30.0
    genus = get_sign_genus(SIGNS[sign_idx], deg_in_sign)
    
    zero_houses = {
        "Nara": 7,          # Human signs powerless in 7th
        "Jalachara": 10,    # Watery signs powerless in 10th
        "Keeta": 1,         # Insect signs powerless in 1st
        "Chathushpada": 4   # Quadruped signs powerless in 4th
    }
    
    zero_h = zero_houses[genus]
    dist = abs(bhava_num - zero_h) % 12
    if dist > 6:
        dist = 12 - dist
        
    return round(dist * 10.0, 2)

def calculate_bhava_drishti_bala(
    bhava_madhya_lon: float, 
    planet_positions: dict, 
    is_moon_benefic: bool = True,
    is_mercury_malefic: bool = False
) -> float:
    """
    Computes aspectual strength on the Bhava Madhya.
    Jupiter and Mercury cast full strength; others cast 1/4th strength.
    Benefics add strength, malefics subtract strength.
    """
    malefics = ["Sun", "Mars", "Saturn"]
    if not is_moon_benefic:
        malefics.append("Moon")
    if is_mercury_malefic:
        malefics.append("Mercury")
        
    net_drishti = 0.0
    for planet, p_lon in planet_positions.items():
        if planet not in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
            continue
            
        raw_aspect = aspects.get_graha_drishti(planet, p_lon, bhava_madhya_lon)
        if raw_aspect <= 0:
            continue
            
        if planet in malefics:
            net_drishti -= raw_aspect / 4.0
        else:
            if planet in ["Jupiter", "Mercury"]:
                net_drishti += raw_aspect
            else:
                net_drishti += raw_aspect / 4.0
                
    return round(net_drishti, 2)

def calculate_bhava_bala(
    bhava_madhyas: list, 
    shadbala_results: dict, 
    planet_positions: dict
) -> dict:
    """
    Calculates composite Bhava Bala for all 12 houses.
    
    Args:
        bhava_madhyas: List of 12 midpoints/cusps (supports Whole Sign or Campanus).
        shadbala_results: Output dictionary from calculate_shadbala().
        planet_positions: Dict containing 'Sun', 'Moon', etc. longitudes.
        
    Returns:
        Dictionary mapping house numbers 1-12 to their strength breakdown.
    """
    bhava_results = {}
    
    moon_paksha = shadbala_results.get("Moon", {}).get("Paksha_Bala", 30.0)
    is_moon_benefic = moon_paksha >= 30.0
    
    sun_lon = planet_positions.get("Sun", 0.0)
    merc_lon = planet_positions.get("Mercury", 0.0)
    merc_sun_dist = abs(merc_lon - sun_lon) % 360.0
    if merc_sun_dist > 180.0:
        merc_sun_dist = 360.0 - merc_sun_dist
    is_mercury_malefic = merc_sun_dist < 14.0
    
    for i in range(12):
        house_num = i + 1
        cusp_lon = bhava_madhyas[i] % 360.0
        sign_idx = int(cusp_lon / 30.0)
        lord = SIGN_LORDS[SIGNS[sign_idx]]
        
        # Pillar 1: Bhavadhipati Bala (Lord's Total Virupas)
        adhipathi_bala = shadbala_results.get(lord, {}).get("Total_Virupas", 0.0)
        
        # Pillar 2: Bhava Digbala
        dig_bala = calculate_bhava_dig_bala(house_num, cusp_lon)
        
        # Pillar 3: Bhava Drishti Bala
        drishti_bala = calculate_bhava_drishti_bala(
            cusp_lon, 
            planet_positions, 
            is_moon_benefic=is_moon_benefic,
            is_mercury_malefic=is_mercury_malefic
        )
        
        total_virupas = round(adhipathi_bala + dig_bala + drishti_bala, 2)
        total_rupas = round(total_virupas / 60.0, 2)
        
        bhava_results[house_num] = {
            "house": house_num,
            "lord": lord,
            "bhava_madhya": round(cusp_lon, 2),
            "bhavadhipathi_bala": adhipathi_bala,
            "bhava_digbala": dig_bala,
            "bhava_drishti_bala": drishti_bala,
            "total_virupas": total_virupas,
            "total_rupas": total_rupas
        }
        
    return bhava_results
