import math
import jyotish.relationships as rel
import jyotish.aspects as aspects
from jyotish.relationships import (
    SIGN_LORDS,
    get_natural_relationship,
    get_temporary_relationship,
    get_compound_relationship
)

SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", 
         "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

MOOLATRIKONA_SIGNS = {
    "Sun": "Leo", "Moon": "Taurus", "Mars": "Aries", "Mercury": "Virgo",
    "Jupiter": "Sagittarius", "Venus": "Libra", "Saturn": "Aquarius"
}

OWN_SIGNS = {
    "Sun": ["Leo"], "Moon": ["Cancer"], "Mars": ["Aries", "Scorpio"], 
    "Mercury": ["Gemini", "Virgo"], "Jupiter": ["Sagittarius", "Pisces"], 
    "Venus": ["Taurus", "Libra"], "Saturn": ["Capricorn", "Aquarius"]
}

def get_saptavarga_points(planet: str, sign: str, compound_rel: str) -> float:
    """Returns the Virupa points based on dignity for Saptavarga Bala."""
    if MOOLATRIKONA_SIGNS.get(planet) == sign:
        return 45.0
    if sign in OWN_SIGNS.get(planet, []):
        return 30.0
    
    if "Great Friend" in compound_rel: return 20.0
    if "Friend" in compound_rel: return 15.0
    if "Neutral" in compound_rel: return 10.0
    if "Great Enemy" in compound_rel: return 2.0
    if "Enemy" in compound_rel: return 4.0
    return 10.0 # fallback neutral

def calculate_saptavarga_bala(planet: str, planet_positions: dict) -> float:
    """
    Calculates Saptavarga (7-Divisional) Strength.
    Evaluates dignity in D1, D2, D3, D7, D9, D12, D30.
    """
    from jyotish.generate_jyotish import calculate_varga_longitude

    vargas = ["D1", "D2", "D3", "D7", "D9", "D12", "D30"]
    total_virupas = 0.0
    
    # 1. Calculate the planet's D1 sign index for temporary relationships
    p1_d1_lon = planet_positions[planet]
    p1_d1_idx = int(p1_d1_lon / 30.0)
    
    for varga in vargas:
        varga_lon = calculate_varga_longitude(p1_d1_lon, varga)
        varga_sign_idx = int((varga_lon % 360.0) / 30.0)
        varga_sign_name = SIGNS[varga_sign_idx]
        
        sign_lord = SIGN_LORDS[varga_sign_name]
        
        if sign_lord == planet:
            # It's either Moolatrikona or Own Sign, handled in the helper
            total_virupas += get_saptavarga_points(planet, varga_sign_name, "")
            continue
            
        # For other signs, calculate compound relationship with the sign lord
        lord_d1_lon = planet_positions.get(sign_lord)
        if lord_d1_lon is None:
            total_virupas += 10.0 # Neutral fallback if lord position unknown
            continue
            
        lord_d1_idx = int(lord_d1_lon / 30.0)
        
        natural = get_natural_relationship(planet, sign_lord)
        temporary = get_temporary_relationship(p1_d1_idx, lord_d1_idx)
        compound = get_compound_relationship(natural, temporary)
        
        total_virupas += get_saptavarga_points(planet, varga_sign_name, compound)
        
    return total_virupas

def calculate_naisargika_bala() -> dict:
    """
    Calculates the Naisargika Bala (Natural Strength) of the 7 primary planets.
    Returns a dictionary mapping planet names to their strength in Virupas.
    According to BPHS/Graha Sutras, the Sun is naturally brightest, Saturn weakest.
    """
    # Fixed values in Virupas (60 Virupas = 1 Rupa)
    return {
        "Sun": 60.0,
        "Moon": 51.4,
        "Venus": 42.8,
        "Jupiter": 34.3,
        "Mercury": 25.7,
        "Mars": 17.1,
        "Saturn": 8.6
    }


def calculate_dig_bala(planet_name: str, planet_lon: float, ascendant_lon: float, mc_lon: float) -> float:
    """
    Calculates Dig Bala (Directional Strength) for a given planet.
    Requires the exact planet longitude, Ascendant longitude (1st House Cusp),
    and Midheaven longitude (10th House Cusp).
    Returns the strength in Virupas (0 to 60).
    """
    ic_lon = (mc_lon + 180.0) % 360.0
    descendant_lon = (ascendant_lon + 180.0) % 360.0
    
    # Map each planet to its WEAKEST point (opposite of its strongest cusp).
    # Strength = 60 Virupas at strongest, 0 at weakest.
    # We find the shortest angular distance from the WEAKEST point.
    weakest_points = {
        "Sun": ic_lon,           # Strong at MC(10th), Weak at IC(4th)
        "Mars": ic_lon,          # Strong at MC(10th), Weak at IC(4th)
        "Moon": mc_lon,          # Strong at IC(4th), Weak at MC(10th)
        "Venus": mc_lon,         # Strong at IC(4th), Weak at MC(10th)
        "Jupiter": descendant_lon, # Strong at Asc(1st), Weak at Desc(7th)
        "Mercury": descendant_lon, # Strong at Asc(1st), Weak at Desc(7th)
        "Saturn": ascendant_lon    # Strong at Desc(7th), Weak at Asc(1st)
    }
    
    if planet_name not in weakest_points:
        return 0.0
        
    weakest_lon = weakest_points[planet_name]
    
    # Shortest angular distance between planet and its weakest point
    # Max distance is 180 degrees (which is its strongest point).
    diff = abs(planet_lon - weakest_lon)
    if diff > 180.0:
        diff = 360.0 - diff
        
    # 180 degrees = 60 Virupas, so 1 degree = 60/180 = 1/3 Virupa
    virupas = diff / 3.0
    return round(virupas, 2)


def calculate_uccha_bala(planet_name: str, planet_lon: float) -> float:
    """
    Calculates Uccha Bala (Exaltation Strength) for a given planet.
    Based on the angular distance from its point of deep debilitation.
    Returns the strength in Virupas (0 to 60).
    """
    exaltation_points = {
        "Sun": 10.0,
        "Moon": 33.0,     # 3 deg Taurus
        "Mars": 298.0,    # 28 deg Capricorn
        "Mercury": 165.0, # 15 deg Virgo
        "Jupiter": 95.0,  # 5 deg Cancer
        "Venus": 357.0,   # 27 deg Pisces
        "Saturn": 200.0   # 20 deg Libra
    }
    
    if planet_name not in exaltation_points: return 0.0
        
    deep_exaltation = exaltation_points[planet_name]
    deep_debilitation = (deep_exaltation + 180.0) % 360.0
    
    diff = abs(planet_lon - deep_debilitation)
    if diff > 180.0: diff = 360.0 - diff
        
    virupas = diff / 3.0
    return round(virupas, 2)


def calculate_ojayugmarasyamsa_bala(planet_name: str, planet_lon: float) -> float:
    """
    Odd/Even Rasi and Navamsa Strength.
    Moon and Venus gain 15 Virupas in Even Rasi and 15 in Even Navamsa.
    Other planets gain 15 in Odd Rasi and 15 in Odd Navamsa.
    Returns total Virupas (max 30).
    """
    rasi_sign = int(planet_lon / 30.0)  # 0=Aries (Odd), 1=Taurus (Even), etc.
    navamsa_lon = (planet_lon * 9.0) % 360.0
    navamsa_sign = int(navamsa_lon / 30.0)
    
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


def calculate_kendra_bala(planet_lon: float, ascendant_lon: float) -> float:
    """
    Angular Strength (Kendra Bala).
    """
    planet_sign = int(planet_lon / 30.0)
    asc_sign = int(ascendant_lon / 30.0)
    house_num = ((planet_sign - asc_sign) % 12) + 1
    
    if house_num in [1, 4, 7, 10]: return 60.0
    elif house_num in [2, 5, 8, 11]: return 30.0
    else: return 15.0


def calculate_drekkana_bala(planet_name: str, planet_lon: float) -> float:
    """Drekkana (Decanate) Strength."""
    deg_in_sign = planet_lon % 30.0
    if planet_name in ["Sun", "Mars", "Jupiter"] and deg_in_sign < 10.0: return 15.0
    if planet_name in ["Moon", "Venus"] and 10.0 <= deg_in_sign < 20.0: return 15.0
    if planet_name in ["Mercury", "Saturn"] and deg_in_sign >= 20.0: return 15.0
    return 0.0

# --- KALA BALA (TIME STRENGTH) COMPONENTS ---

def calculate_nathonnatha_bala(planet: str, sun_lon: float, mc_lon: float) -> float:
    """Day/Night Strength."""
    if planet == "Mercury": return 60.0
    ic_lon = (mc_lon + 180.0) % 360.0
    dist_from_ic = abs(sun_lon - ic_lon)
    if dist_from_ic > 180.0: dist_from_ic = 360.0 - dist_from_ic
    day_strength = dist_from_ic / 3.0
    if planet in ["Sun", "Jupiter", "Venus"]: return round(day_strength, 2)
    elif planet in ["Moon", "Mars", "Saturn"]: return round(60.0 - day_strength, 2)
    return 0.0

def calculate_paksha_bala(planet: str, moon_lon: float, sun_lon: float) -> float:
    """Moon Phase Strength."""
    diff = abs(moon_lon - sun_lon)
    if diff > 180.0: diff = 360.0 - diff
    benefic_strength = diff / 3.0
    if planet in ["Moon", "Mercury", "Jupiter", "Venus"]: return round(benefic_strength, 2)
    elif planet in ["Sun", "Mars", "Saturn"]: return round(60.0 - benefic_strength, 2)
    return 0.0

def calculate_tribhaga_bala(planet: str, sun_lon: float, asc_lon: float) -> float:
    """Third-portion of Day/Night Strength."""
    if planet == "Jupiter": return 60.0
    desc_lon = (asc_lon + 180.0) % 360.0
    time_elapsed = (asc_lon - sun_lon) % 360.0
    is_day = time_elapsed <= 180.0
    fraction = time_elapsed / 180.0 if is_day else (time_elapsed - 180.0) / 180.0
    
    if is_day:
        if fraction <= 0.3333 and planet == "Mercury": return 60.0
        if 0.3333 < fraction <= 0.6666 and planet == "Sun": return 60.0
        if fraction > 0.6666 and planet == "Saturn": return 60.0
    else:
        if fraction <= 0.3333 and planet == "Moon": return 60.0
        if 0.3333 < fraction <= 0.6666 and planet == "Venus": return 60.0
        if fraction > 0.6666 and planet == "Mars": return 60.0
    return 0.0

import swisseph as swe

def calculate_ayana_bala(planet: str, birth_time_jd: float) -> float:
    """
    Ayana Bala (Declination Strength).
    Evaluated using true Equatorial Declination (Kranti).
    Sun, Mars, Jupiter, Venus are strong in the North (+).
    Moon, Saturn are strong in the South (-).
    Mercury is strong at both extremes and gets 30 at the equator.
    """
    planet_map = {
        "Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS,
        "Mercury": swe.MERCURY, "Jupiter": swe.JUPITER, 
        "Venus": swe.VENUS, "Saturn": swe.SATURN
    }
    
    if planet not in planet_map: return 0.0
        
    pl_id = planet_map[planet]
    res, _ = swe.calc_ut(birth_time_jd, pl_id, swe.FLG_SWIEPH | swe.FLG_EQUATORIAL)
    decl = res[1] 
    
    max_decl = 24.0
    
    if planet in ["Sun", "Mars", "Jupiter", "Venus"]:
        virupas = 60.0 * (decl + max_decl) / (2.0 * max_decl)
    elif planet in ["Moon", "Saturn"]:
        virupas = 60.0 * (max_decl - decl) / (2.0 * max_decl)
    elif planet == "Mercury":
        virupas = 30.0 + (abs(decl) / max_decl) * 30.0
    else:
        virupas = 0.0
        
    return max(0.0, min(60.0, round(virupas, 2)))

def calculate_cheshta_bala(planet: str, birth_time_jd: float, planet_geo_lon: float, sun_geo_lon: float) -> float:
    """
    Cheshta Bala (Motional Strength).
    Based on the Cheshta Kendra (distance from Seeghrocca).
    For Superior planets (Mars, Jupiter, Saturn), Seeghrocca = Sun's longitude.
    For Inferior planets (Mercury, Venus), Seeghrocca = Planet's Heliocentric longitude.
    """
    if planet in ["Sun", "Moon"]:
        return 0.0 # Handled separately via Ayana/Paksha
        
    planet_map = {
        "Mars": swe.MARS, "Mercury": swe.MERCURY, 
        "Jupiter": swe.JUPITER, "Venus": swe.VENUS, "Saturn": swe.SATURN
    }
    
    if planet not in planet_map: return 0.0
        
    if planet in ["Mars", "Jupiter", "Saturn"]:
        seeghrocca = sun_geo_lon
    else:
        # Get true heliocentric longitude
        pl_id = planet_map[planet]
        res, _ = swe.calc_ut(birth_time_jd, pl_id, swe.FLG_SWIEPH | swe.FLG_HELCTR)
        seeghrocca = res[0]
        
    kendra = abs(seeghrocca - planet_geo_lon)
    if kendra > 180.0: kendra = 360.0 - kendra
    
    # 180 degrees = 60 Virupas
    virupas = kendra / 3.0
    return round(virupas, 2)




def calculate_drik_bala(planet: str, lon: float, planet_positions: dict) -> float:
    """
    Drik Bala (Aspectual Strength).
    Evaluates all incoming aspects to the planet.
    Malefics reduce strength (1/4 of aspect value).
    Benefics increase strength (1/4 of aspect value), EXCEPT Jupiter and Mercury which add full value.
    """
    benefics = ["Jupiter", "Mercury", "Venus", "Moon"] 
    malefics = ["Sun", "Mars", "Saturn"]
    
    total_drik = 0.0
    for p_other, lon_other in planet_positions.items():
        if p_other == planet: continue
        
        raw_drishti = aspects.get_graha_drishti(p_other, lon_other, lon)
        if raw_drishti <= 0: continue
            
        if p_other in benefics:
            if p_other in ["Jupiter", "Mercury"]:
                total_drik += raw_drishti
            else:
                total_drik += raw_drishti / 4.0
        elif p_other in malefics:
            total_drik -= raw_drishti / 4.0
            
    return round(total_drik, 2)


def calculate_shadbala(planet_positions: dict, ascendant_lon: float, mc_lon: float, birth_time_jd: float) -> dict:
    """
    Master function to calculate the full 6-fold Shadbala for all planets.
    
    Args:
        planet_positions (dict): Dictionary mapping planet names to their exact ecliptic longitudes.
        ascendant_lon (float): The exact longitude of the Ascendant.
        mc_lon (float): The exact longitude of the Midheaven (10th cusp).
        birth_time_jd (float): Julian Day of birth for time-based (Kala) and motional (Cheshta) calculations.
        
    Returns:
        dict: A nested dictionary containing the total Shadbala and its 6 sub-components for each planet.
    """
    results = {}
    naisargika = calculate_naisargika_bala()
    
    planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    
    for p in planets:
        if p not in planet_positions:
            continue
            
        lon = planet_positions[p]
        
        # 1. Sthana Bala (Positional)
        # Sthana Bala is the sum of 5 components. All 5 are now implemented.
        uccha = calculate_uccha_bala(p, lon)
        saptavarga = calculate_saptavarga_bala(p, planet_positions)
        ojayugma = calculate_ojayugmarasyamsa_bala(p, lon)
        kendra = calculate_kendra_bala(lon, ascendant_lon)
        drekkana = calculate_drekkana_bala(p, lon)
        
        sthana = uccha + saptavarga + ojayugma + kendra + drekkana
        
        # 2. Dig Bala (Directional)
        dig = calculate_dig_bala(p, lon, ascendant_lon, mc_lon)
        
        # 3. Kala Bala (Time)
        nathonnatha = calculate_nathonnatha_bala(p, planet_positions.get("Sun", 0.0), mc_lon)
        paksha = calculate_paksha_bala(p, planet_positions.get("Moon", 0.0), planet_positions.get("Sun", 0.0))
        tribhaga = calculate_tribhaga_bala(p, planet_positions.get("Sun", 0.0), ascendant_lon)
        ayana = calculate_ayana_bala(p, birth_time_jd)
        
        kala = nathonnatha + paksha + tribhaga + ayana # TODO: Add Abda, Masa, Vara, Hora, Yuddha
        
        # 4. Cheshta Bala (Motional)
        # Sun inherits its Ayana Bala. Moon inherits its Paksha Bala.
        if p == "Sun":
            cheshta = ayana
        elif p == "Moon":
            cheshta = paksha
        else:
            cheshta = calculate_cheshta_bala(p, birth_time_jd, lon, planet_positions.get("Sun", 0.0))
        
        # 5. Naisargika Bala (Natural)
        naisarg = naisargika[p]
        
        # 6. Drik Bala (Aspectual)
        drik = calculate_drik_bala(p, lon, planet_positions)
        
        # 7. Ishta and Kashta Phala (Auspicious / Inauspicious Effects)
        # Ishta Phala = sqrt(Ochcha Bala * Cheshta Bala)
        # Kashta Phala = sqrt((60 - Ochcha Bala) * (60 - Cheshta Bala))
        ishta_phala = math.sqrt(uccha * cheshta)
        kashta_phala = math.sqrt((60.0 - uccha) * (60.0 - cheshta))
        
        total_virupas = sthana + dig + kala + cheshta + naisarg + drik
        
        results[p] = {
            "Total_Virupas": round(total_virupas, 2),
            "Total_Rupas": round(total_virupas / 60.0, 4),
            "Sthana_Bala": round(sthana, 2),
            "Dig_Bala": round(dig, 2),
            "Kala_Bala": round(kala, 2),
            "Cheshta_Bala": round(cheshta, 2),
            "Naisargika_Bala": round(naisarg, 2),
            "Drik_Bala": round(drik, 2),
            "Ishta_Phala": round(ishta_phala, 2),
            "Kashta_Phala": round(kashta_phala, 2)
        }
        
    return results
