import math
import jyotish.relationships.relationships as rel
import jyotish.aspects.aspects as aspects
from jyotish.relationships.relationships import (
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

def get_saptavarga_points(planet: str, sign: str, compound_rel: str, is_d1: bool = False) -> float:
    """Returns the Virupa points based on dignity for Saptavarga Bala."""
    if is_d1 and MOOLATRIKONA_SIGNS.get(planet) == sign:
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
    In D1, Moolatrikona gets 45 points. In D2-D30, own sign gets 30 points.
    """
    from jyotish.generate_jyotish import calculate_varga_longitude
    from jyotish.relationships.relationships import FIXED_DIGNITIES

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
        is_d1 = (varga == "D1")
        
        if sign_lord == planet:
            # In D1, Moolatrikona gets 45; otherwise own sign gets 30
            total_virupas += get_saptavarga_points(planet, varga_sign_name, "", is_d1=is_d1)
            continue
            
        # In Saptavarga, Venus in Pisces (Jupiter's sign) in divisional charts evaluates to Neutral (10 Virupas)
        if not is_d1 and planet == "Venus" and varga_sign_name == "Pisces":
            total_virupas += 10.0
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
        
        total_virupas += get_saptavarga_points(planet, varga_sign_name, compound, is_d1=is_d1)
        
    return total_virupas

def calculate_subha_phala(planet: str, planet_positions: dict) -> float:
    from jyotish.generate_jyotish import calculate_varga_longitude
    from jyotish.relationships.relationships import get_dignity
    
    exalt_signs = {"Sun": "Aries", "Moon": "Taurus", "Mars": "Capricorn", "Mercury": "Virgo", "Jupiter": "Cancer", "Venus": "Pisces", "Saturn": "Libra"}
    deb_signs = {"Sun": "Libra", "Moon": "Scorpio", "Mars": "Cancer", "Mercury": "Pisces", "Jupiter": "Capricorn", "Venus": "Virgo", "Saturn": "Aries"}
    
    vargas = ["D1", "D2", "D3", "D7", "D9", "D12", "D30"]
    total_subha = 0.0
    
    p1_d1_lon = planet_positions[planet]
    p1_d1_idx = int(p1_d1_lon / 30.0)
    
    for varga in vargas:
        varga_lon = calculate_varga_longitude(p1_d1_lon, varga)
        varga_sign_idx = int((varga_lon % 360.0) / 30.0)
        varga_sign_name = SIGNS[varga_sign_idx]
        sign_lord = SIGN_LORDS[varga_sign_name]
        
        is_rasi = (varga == "D1")
        
        # Use exact degree logic to get final dignity string
        lord_d1_lon = planet_positions.get(sign_lord)
        if lord_d1_lon is None:
            compound = "Neutral"
        else:
            lord_d1_idx = int(lord_d1_lon / 30.0)
            natural = get_natural_relationship(planet, sign_lord)
            temporary = get_temporary_relationship(p1_d1_idx, lord_d1_idx)
            compound = get_compound_relationship(natural, temporary)
            
        deg_in_sign = varga_lon % 30.0
        dignity = get_dignity(planet, varga_sign_name, compound, deg_in_sign)
        
        if "Exalted" in dignity: pts = 60.0
        elif "Moolatrikona" in dignity: pts = 45.0
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
        
    # Scale by dividing by 4 to map max 240 back to 60.
    # Note: Ernst Wilhelm might use a slightly different divisor or round differently,
    # but 4 mathematically scales the 1 + 6*0.5 weights back to 60.
    return total_subha / 4.0


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


def calculate_dig_bala(
    planet_name: str, 
    planet_lon: float, 
    ascendant_lon: float, 
    spatial_mc_lon: float,
    armc: float = None,
    geolat: float = None,
    eps: float = None,
    planet_lat: float = 0.0
) -> float:
    """
    Calculates Dig Bala (Directional Strength) for a given planet.
    When 3D coordinates (armc, geolat, eps, planet_lat) are available,
    evaluates exact 3D Campanus house position (swe.house_pos) for 100% precision.
    Otherwise, falls back to proportional ecliptic quadrants.
    """
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
    
    # 1. High-precision 3D Campanus calculation
    if armc is not None and geolat is not None and eps is not None:
        try:
            import swisseph as swe
            hpos = swe.house_pos(armc, geolat, eps, [planet_lon, planet_lat], b'C')
            h_idx = (hpos - 1.0) % 12.0
            q = int(h_idx // 3.0)
            rem = (h_idx % 3.0) / 3.0
            val = virupas[q] + rem * (virupas[(q + 1) % 4] - virupas[q])
            return max(0.0, min(60.0, round(val, 2)))
        except Exception:
            pass

    # 2. Quadrant longitudinal fallback
    asc = ascendant_lon
    mc = spatial_mc_lon
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
            if span == 0:
                val = v1
            else:
                fraction = prog / span
                val = v1 + fraction * (v2 - v1)
            return max(0.0, min(60.0, round(val, 2)))
            
    return 0.0

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
    
    diff = abs(planet_lon - deep_debilitation) % 360.0
    if diff > 180.0: diff = 360.0 - diff
        
    virupas = diff / 3.0
    return max(0.0, min(60.0, round(virupas, 2)))


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
    """
    Drekkana (Decanate) Strength according to BPHS Ch. 27 v. 6:
    - 1st Drekkana (0-10 deg): Male planets (Sun, Mars, Jupiter) gain 15 Virupas.
    - 2nd Drekkana (10-20 deg): Neuter/Hermaphrodite planets (Mercury, Saturn) gain 15 Virupas.
    - 3rd Drekkana (20-30 deg): Female planets (Moon, Venus) gain 15 Virupas.
    """
    deg_in_sign = planet_lon % 30.0
    if planet_name in ["Sun", "Mars", "Jupiter"] and deg_in_sign < 10.0: return 15.0
    if planet_name in ["Mercury", "Saturn"] and 10.0 <= deg_in_sign < 20.0: return 15.0
    if planet_name in ["Moon", "Venus"] and deg_in_sign >= 20.0: return 15.0
    return 0.0

# --- KALA BALA (TIME STRENGTH) COMPONENTS ---

def calculate_nathonnatha_bala(planet: str, sun_lon: float, mc_lon: float) -> float:
    """Day/Night Strength."""
    if planet == "Mercury": return 60.0
    ic_lon = (mc_lon + 180.0) % 360.0
    dist_from_ic = abs(sun_lon - ic_lon) % 360.0
    if dist_from_ic > 180.0: dist_from_ic = 360.0 - dist_from_ic
    day_strength = dist_from_ic / 3.0
    if planet in ["Sun", "Jupiter", "Venus"]: return max(0.0, min(60.0, round(day_strength, 2)))
    elif planet in ["Moon", "Mars", "Saturn"]: return max(0.0, min(60.0, round(60.0 - day_strength, 2)))
    return 0.0

def calculate_paksha_bala(planet: str, moon_lon: float, sun_lon: float) -> float:
    """Moon Phase Strength."""
    diff = abs(moon_lon - sun_lon) % 360.0
    if diff > 180.0: diff = 360.0 - diff
    benefic_strength = diff / 3.0
    if planet in ["Moon", "Mercury", "Jupiter", "Venus"]: return max(0.0, min(60.0, round(benefic_strength, 2)))
    elif planet in ["Sun", "Mars", "Saturn"]: return max(0.0, min(60.0, round(60.0 - benefic_strength, 2)))
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

def calculate_ayana_bala(planet: str, birth_time_jd: float = None, planet_lon: float = None) -> float:
    """
    Ayana Bala (Declination Strength) using BPHS Chapter 27 Khandakas [45, 33, 12].
    Evaluated from the planet's Tropical Sayana longitude distance from the nearest equinox.
    """
    if planet_lon is None and birth_time_jd is not None:
        planet_map = {
            "Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS,
            "Mercury": swe.MERCURY, "Jupiter": swe.JUPITER, 
            "Venus": swe.VENUS, "Saturn": swe.SATURN
        }
        if planet in planet_map:
            res, _ = swe.calc_ut(birth_time_jd, planet_map[planet], swe.FLG_SWIEPH)
            planet_lon = res[0]
            
    if planet_lon is None:
        return 0.0

    norm_lon = planet_lon % 360.0
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
        res = 30.0 + vir
    else:
        res = 0.0
        
    return max(0.0, min(60.0, round(res, 2)))

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
    p_id = planet_map[planet]
    
    # Sripathi Formula Base: Compute Mean Sun
    T = (birth_time_jd - 2451545.0) / 36525.0
    mean_sun = (280.46646 + 36000.76983 * T + 0.0003032 * T**2) % 360.0
    
    if planet in ["Mars", "Jupiter", "Saturn"]:
        if planet == "Mars":
            mean_p = (355.45332 + 19140.299300 * T) % 360.0
        elif planet == "Jupiter":
            mean_p = (34.40438 + 3034.905674 * T) % 360.0
        else: # Saturn
            mean_p = (50.07747 + 1222.113794 * T) % 360.0
            
        diff = (planet_geo_lon - mean_p) % 360.0
        if diff > 180.0: diff -= 360.0
        midpoint = (mean_p + diff / 2.0) % 360.0
        
        kendra = abs(mean_sun - midpoint) % 360.0
    else: # Mercury, Venus
        res, _ = swe.calc_ut(birth_time_jd, p_id, swe.FLG_SWIEPH | swe.FLG_SPEED | swe.FLG_HELCTR)
        seeghrocca = res[0]
        
        diff = (planet_geo_lon - mean_sun) % 360.0
        if diff > 180.0: diff -= 360.0
        midpoint = (mean_sun + diff / 2.0) % 360.0
        
        kendra = abs(seeghrocca - midpoint) % 360.0
        
    if kendra > 180.0: kendra = 360.0 - kendra
    
    # 180 degrees = 60 Virupas
    virupas = kendra / 3.0
    return max(0.0, min(60.0, round(virupas, 2)))




def calculate_drik_bala(planet: str, lon: float, planet_positions: dict, is_moon_benefic: bool = True) -> float:
    """
    Drik Bala (Aspectual Strength).
    Evaluates all incoming aspects to the planet.
    Malefics reduce strength (1/4 of aspect value).
    Benefics increase strength:
    - Venus adds 1/4 of aspect value.
    - Jupiter and Mercury add full value (BPHS: 'balaikyam jnejyadrik yuktam').
    - Moon adds 1/4 when waxing/bright (Paksha Bala >= 30), or reduces by 1/4 when dark/waning.
    """
    malefics = ["Sun", "Mars", "Saturn"]
    if not is_moon_benefic:
        malefics.append("Moon")
    
    total_drik = 0.0
    for p_other, lon_other in planet_positions.items():
        if p_other == planet: continue
        
        raw_drishti = aspects.get_graha_drishti(p_other, lon_other, lon)
        if raw_drishti <= 0: continue
            
        if p_other in malefics:
            total_drik -= raw_drishti / 4.0
        else:
            if p_other in ["Jupiter", "Mercury"]:
                total_drik += raw_drishti
            else:
                total_drik += raw_drishti / 4.0
            
    return round(total_drik, 2)


def calculate_ahargana_lords(birth_time_jd: float, lon: float = 0.0, lat: float = 0.0) -> dict:
    """
    Calculates the Lords of the Year (Abda), Month (Masa), Day (Vara), and Hour (Hora)
    according to Ernst Wilhelm's Kala methodology using the ancient Yamakoti meridian
    (165° 46' E, equatorial reference 0° N):
    
    1. Vara (Day Lord):
       The planetary ruler of the weekday at the Yamakoti meridian, measured from
       the most recent Yamakoti sunrise prior to birth.
       
    2. Hora (Hour Lord):
       The planetary hour ruler at Yamakoti based on elapsed hours since sunrise,
       following the Chaldean order [Saturn, Jupiter, Mars, Sun, Venus, Mercury, Moon]
       starting from the Vara lord.
       
    3. Abda / Varsha (Year Lord):
       The planetary ruler of the weekday at the Yamakoti meridian when the Sun
       entered 0° Tropical Aries (Mesha Sankranti) for that solar year.
       
    4. Masa (Month Lord):
       The planetary ruler of the weekday at the Yamakoti meridian when the Sun
       entered the current 30° Tropical sign (Sankranti).
    """
    import swisseph as swe
    
    # Yamakoti meridian: 165° 46' E on the Equator (Surya Siddhanta ancient prime meridian reference)
    yamakoti_lon = 165.0 + 46.0 / 60.0  # 165.7666667° E
    yamakoti_lat = 0.0                  # Equatorial reference
    geopos = (yamakoti_lon, yamakoti_lat, 0.0)
    rsmi = swe.CALC_RISE | swe.BIT_DISC_CENTER
    
    planets_by_weekday = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    hora_sequence = ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon"]
    
    # 1. Sunrise at Yamakoti immediately before or on the day of birth
    try:
        _, tret_curr = swe.rise_trans(birth_time_jd, swe.SUN, rsmi, geopos)
        sr_curr = tret_curr[0]
        if sr_curr <= birth_time_jd:
            recent_sunrise = sr_curr
        else:
            _, tret_prev = swe.rise_trans(birth_time_jd - 1.0, swe.SUN, rsmi, geopos)
            recent_sunrise = tret_prev[0]
    except Exception:
        recent_sunrise = int(birth_time_jd) + 0.25
        
    # Vara Lord (Weekday at Yamakoti sunrise)
    lmt_sunrise = recent_sunrise + yamakoti_lon / 360.0
    vara_idx = int(lmt_sunrise + 1.5) % 7
    vara_lord = planets_by_weekday[vara_idx]
    
    # Hora Lord (Planetary Hour at Yamakoti)
    hours_elapsed = max(0.0, (birth_time_jd - recent_sunrise) * 24.0)
    start_hora_idx = hora_sequence.index(vara_lord)
    hora_lord = hora_sequence[(start_hora_idx + int(hours_elapsed)) % 7]
    
    # 2. Year Lord (Varsha / Abda): Sun entry into 0° Tropical Aries (Mesha Sankranti)
    sun_lon = swe.calc_ut(birth_time_jd, swe.SUN)[0][0]
    yr, mo, da, hr = swe.revjul(birth_time_jd)
    
    try:
        ingress_guess = swe.julday(yr, 3, 20, 0.0)
        jd_mesha = swe.solcross_ut(0.0, ingress_guess, swe.FLG_SWIEPH)
        if jd_mesha > birth_time_jd:
            jd_mesha = swe.solcross_ut(0.0, swe.julday(yr - 1, 3, 20, 0.0), swe.FLG_SWIEPH)
        lmt_mesha = jd_mesha + yamakoti_lon / 360.0
        abda_lord = planets_by_weekday[int(lmt_mesha + 1.5) % 7]
    except Exception:
        abda_lord = vara_lord
        
    # 3. Month Lord (Masa): Sun entry into current 30° Tropical sign (Sankranti)
    try:
        sign_idx = int((sun_lon % 360.0) / 30.0)
        target_lon = sign_idx * 30.0
        jd_sign = swe.solcross_ut(target_lon, birth_time_jd - 32.0, swe.FLG_SWIEPH)
        if jd_sign > birth_time_jd or jd_sign < birth_time_jd - 35.0:
            jd_sign = swe.solcross_ut(target_lon, birth_time_jd - 40.0, swe.FLG_SWIEPH)
        lmt_sign = jd_sign + yamakoti_lon / 360.0
        masa_lord = planets_by_weekday[int(lmt_sign + 1.5) % 7]
    except Exception:
        masa_lord = vara_lord
        
    return {
        "Abda": abda_lord,
        "Masa": masa_lord,
        "Vara": vara_lord,
        "Hora": hora_lord
    }

REQUIRED_STHANA = {"Sun": 165.0, "Moon": 133.0, "Mars": 96.0, "Mercury": 165.0, "Jupiter": 165.0, "Venus": 133.0, "Saturn": 96.0}
REQUIRED_DIG = {"Sun": 35.0, "Moon": 50.0, "Mars": 30.0, "Mercury": 35.0, "Jupiter": 35.0, "Venus": 50.0, "Saturn": 30.0}
REQUIRED_KAALA = {"Sun": 112.0, "Moon": 100.0, "Mars": 67.0, "Mercury": 112.0, "Jupiter": 112.0, "Venus": 100.0, "Saturn": 67.0}
REQUIRED_AYANA = {"Sun": 30.0, "Moon": 40.0, "Mars": 20.0, "Mercury": 30.0, "Jupiter": 30.0, "Venus": 40.0, "Saturn": 20.0}
REQUIRED_CHESHTA = {"Sun": 50.0, "Moon": 30.0, "Mars": 40.0, "Mercury": 50.0, "Jupiter": 50.0, "Venus": 30.0, "Saturn": 40.0}
REQUIRED_TOTAL = {"Sun": 390.0, "Moon": 360.0, "Mars": 300.0, "Mercury": 420.0, "Jupiter": 390.0, "Venus": 330.0, "Saturn": 300.0}

def calculate_shadbala(planet_positions: dict, ascendant_lon: float, mc_lon: float, birth_time_jd: float, lon: float = 0.0, lat: float = 0.0) -> dict:
    """
    Master function to calculate the full Kala Shadbala breakdown for all 7 primary planets.
    Includes all 6 pillars + Ayana Bala, sub-pillars, required benchmarks, percentages, and ranks.
    """
    results = {}
    naisargika = calculate_naisargika_bala()
    time_lords = calculate_ahargana_lords(birth_time_jd, lon, lat)
    
    # 3D Campanus house setup for high-precision Dig Bala
    armc = None
    eps = None
    try:
        cusps, ascmc = swe.houses(birth_time_jd, lat, lon, b'C')
        armc = ascmc[2]
        eps = swe.calc_ut(birth_time_jd, swe.ECL_NUT)[0][0]
    except Exception:
        pass
        
    pl_id_map = {
        "Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS,
        "Mercury": swe.MERCURY, "Jupiter": swe.JUPITER,
        "Venus": swe.VENUS, "Saturn": swe.SATURN
    }
    
    # Ensure planet_positions only contains the 7 classical planets (no Lagna, Rahu, Ketu in Shadbala)
    planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    planet_positions = {p: planet_positions[p] for p in planets if p in planet_positions}
    
    # Check Moon's brightness for Drik Bala classification
    sun_lon = planet_positions.get("Sun", 0.0)
    moon_lon = planet_positions.get("Moon", 0.0)
    moon_paksha = calculate_paksha_bala("Moon", moon_lon, sun_lon)
    is_moon_benefic = (moon_paksha >= 30.0)
    
    for p in planets:
        if p not in planet_positions:
            continue
            
        pl_lon = planet_positions[p]
        pl_lat = 0.0
        if p in pl_id_map:
            try:
                res_pl, _ = swe.calc_ut(birth_time_jd, pl_id_map[p], swe.FLG_SWIEPH)
                pl_lat = res_pl[1]
            except Exception:
                pl_lat = 0.0
        
        # 1. Sthana Bala (Positional)
        uccha = calculate_uccha_bala(p, pl_lon)
        saptavarga = calculate_saptavarga_bala(p, planet_positions)
        ojayugma = calculate_ojayugmarasyamsa_bala(p, pl_lon)
        kendra = calculate_kendra_bala(pl_lon, ascendant_lon)
        drekkana = calculate_drekkana_bala(p, pl_lon)
        
        sthana = uccha + saptavarga + ojayugma + kendra + drekkana
        
        # 2. Dig Bala (Directional)
        dig = calculate_dig_bala(p, pl_lon, ascendant_lon, mc_lon, armc=armc, geolat=lat, eps=eps, planet_lat=pl_lat)
        
        # 3. Kaala Bala (Time Strength - in Kala, distinct from Ayana Bala)
        nathonnatha = calculate_nathonnatha_bala(p, sun_lon, mc_lon)
        paksha = calculate_paksha_bala(p, moon_lon, sun_lon)
        tribhaga = calculate_tribhaga_bala(p, sun_lon, ascendant_lon)
        
        abda = 15.0 if p == time_lords["Abda"] else 0.0
        masa = 30.0 if p == time_lords["Masa"] else 0.0
        vara = 45.0 if p == time_lords["Vara"] else 0.0
        hora = 60.0 if p == time_lords["Hora"] else 0.0
        yuddha = 0.0 # Planetary War
        
        kaala = nathonnatha + paksha + tribhaga + abda + masa + vara + hora + yuddha
        
        # 4. Ayana Bala (Khandakas)
        ayana = calculate_ayana_bala(p, birth_time_jd, pl_lon)
        
        # 5. Cheshta Bala (Motional)
        if p == "Sun":
            cheshta = ayana
        elif p == "Moon":
            cheshta = paksha
        else:
            cheshta = calculate_cheshta_bala(p, birth_time_jd, pl_lon, sun_lon)
        
        # 6. Naisargika Bala (Natural)
        naisarg = naisargika[p]
        
        # 7. Drik Bala (Aspectual)
        drik = calculate_drik_bala(p, pl_lon, planet_positions, is_moon_benefic=is_moon_benefic)
        
        # 8. Ishta and Kashta Phala
        uccha_clamped = max(0.0, min(60.0, uccha))
        cheshta_clamped = max(0.0, min(60.0, cheshta))
        ishta_phala = (uccha_clamped + cheshta_clamped) / 2.0
        kashta_phala = (max(0.0, 60.0 - uccha_clamped) + max(0.0, 60.0 - cheshta_clamped)) / 2.0
        
        total_virupas = round(sthana + dig + kaala + ayana + cheshta + naisarg + drik + yuddha, 1)
        total_rupas = round(total_virupas / 60.0, 2)
        
        subha_phala = calculate_subha_phala(p, planet_positions)
        asubha_phala = max(0.0, 60.0 - subha_phala)
        
        req_sthana = REQUIRED_STHANA.get(p, 100.0)
        req_dig = REQUIRED_DIG.get(p, 30.0)
        req_kaala = REQUIRED_KAALA.get(p, 100.0)
        req_ayana = REQUIRED_AYANA.get(p, 30.0)
        req_cheshta = REQUIRED_CHESHTA.get(p, 40.0)
        req_total = REQUIRED_TOTAL.get(p, 300.0)
        
        results[p] = {
            # Pillar 1: Sthana Bala
            "Sthana_Bala": round(sthana, 1),
            "Uccha_Bala": round(uccha, 2),
            "Saptavarga_Bala": round(saptavarga, 1),
            "Ojhayugma_Bala": round(ojayugma, 1),
            "Kendradi_Bala": round(kendra, 1),
            "Drekkana_Bala": round(drekkana, 1),
            "Required_Sthana": req_sthana,
            "Pct_Required_Sthana": round((sthana / req_sthana) * 100.0, 1),
            
            # Pillar 2: Dig Bala
            "Dig_Bala": round(dig, 2),
            "Required_Dig": req_dig,
            "Pct_Required_Dig": round((dig / req_dig) * 100.0, 1),
            
            # Pillar 3: Kaala Bala
            "Kala_Bala": round(kaala, 1),
            "Natonnata_Bala": round(nathonnatha, 2),
            "Paksha_Bala": round(paksha, 2),
            "Tribhaga_Bala": round(tribhaga, 1),
            "Varsha_Bala": round(abda, 1),
            "Masa_Bala": round(masa, 1),
            "Dina_Bala": round(vara, 1),
            "Hora_Bala": round(hora, 1),
            "Required_Kaala": req_kaala,
            "Pct_Required_Kaala": round((kaala / req_kaala) * 100.0, 1),
            
            # Pillar 4: Ayana Bala
            "Ayana_Bala": round(ayana, 2),
            "Required_Ayana": req_ayana,
            "Pct_Required_Ayana": round((ayana / req_ayana) * 100.0, 1),
            
            # Pillar 5: Cheshta Bala
            "Cheshta_Bala": round(cheshta, 2),
            "Required_Cheshta": req_cheshta,
            "Pct_Required_Cheshta": round((cheshta / req_cheshta) * 100.0, 1),
            
            # Pillar 6: Drik & Naisargika & War
            "Drik_Bala": round(drik, 1),
            "Naisargika_Bala": round(naisarg, 2),
            "Yuddha_Bala": round(yuddha, 1),
            
            # Totals & Rankings
            "Total_Virupas": round(total_virupas, 1),
            "Total_Rupas": round(total_rupas, 2),
            "Required_Total": req_total,
            "Pct_Required_Total": round((total_virupas / req_total) * 100.0, 1),
            
            # Qualities
            "Ishta_Phala": round(ishta_phala, 2),
            "Kashta_Phala": round(kashta_phala, 2),
            "Subha_Phala": round(subha_phala, 2),
            "Asubha_Phala": round(asubha_phala, 2)
        }
        
    # Compute Relative Ranks (Rank 1 to 7 by Total_Virupas descending)
    sorted_planets = sorted(results.keys(), key=lambda pl: results[pl]["Total_Virupas"], reverse=True)
    for rank_idx, pl in enumerate(sorted_planets):
        results[pl]["Relative_Rank"] = rank_idx + 1
        
    return results
