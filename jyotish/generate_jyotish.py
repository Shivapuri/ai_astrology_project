import json
from jyotish.shadbala.shadbala import calculate_shadbala
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import math
import jyotish.calc_utils as calc_utils
import jyotish.relationships.relationships as rel
import jyotish.aspects.aspects as aspects
import jyotish.avasthas as avasthas

try:
    import swisseph as swe
    # Set ephemeris path to absolute path of 'ephe' directory in project root
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    swe.set_ephe_path(os.path.join(base_dir, 'ephe'))
except ImportError:
    print("Error: 'pyswisseph' package is not installed. Please run 'pip install pyswisseph'.")
    sys.exit(1)

# Signs
ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

# Nakshatras
NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishtha", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

DASHA_LORDS = ['Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury']
DASHA_YEARS = [7, 20, 6, 10, 7, 18, 16, 19, 17]

# Ernst Wilhelm Saura Year length in days
SAURA_YEAR_DAYS = 359.0016

def get_sign(longitude: float) -> tuple[str, float]:
    sign_idx = int(longitude // 30)
    deg_in_sign = longitude % 30
    return ZODIAC_SIGNS[sign_idx], round(deg_in_sign, 2)

def calculate_varga_longitude(longitude: float, varga: str) -> float:
    sign_idx = int(longitude // 30)
    deg = longitude % 30
    is_odd = (sign_idx % 2 == 0) # 0=Aries (odd), 1=Taurus (even)
    
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
        div_index = int(deg // div_size)
        # Kala Distributed Hora: 1st half = same sign, 2nd half = opposite sign (7th)
        varga_sign = (sign_idx + div_index * 6) % 12
        fraction = (deg % div_size) / div_size
        return (varga_sign * 30.0) + (fraction * 30.0)
        
    elif varga == "D3":
        div_size = 10.0
        div_index = int(deg // div_size)
        varga_sign = (sign_idx + div_index * 4) % 12
        fraction = (deg % div_size) / div_size
        return (varga_sign * 30.0) + (fraction * 30.0)
        
    elif varga == "D4":
        div_size = 7.5
        div_index = int(deg // div_size)
        varga_sign = (sign_idx + div_index * 3) % 12
        fraction = (deg % div_size) / div_size
        return (varga_sign * 30.0) + (fraction * 30.0)
        
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
            varga_sign = (sign_idx + 8 - div_index) % 12
        fraction = (deg % div_size) / div_size
        return (varga_sign * 30.0) + (fraction * 30.0)
        
    elif varga == "D12":
        return uniform_varga(12, sign_idx)
        
    elif varga == "D16":
        modality = sign_idx % 3
        start = (modality * 4) % 12
        return uniform_varga(16, start)
        
    elif varga == "D20":
        modality = sign_idx % 3
        if modality == 0: start = 0
        elif modality == 1: start = 8
        else: start = 4
        return uniform_varga(20, start)
        
    elif varga == "D24":
        div_size = 30.0 / 24.0
        div_index = int(deg // div_size)
        if is_odd:
            varga_sign = (4 + div_index) % 12
        else:
            varga_sign = (3 - div_index) % 12
        fraction = (deg % div_size) / div_size
        return (varga_sign * 30.0) + (fraction * 30.0)
        
    elif varga == "D27":
        element = sign_idx % 4
        start = (element * 3) % 12
        return uniform_varga(27, start)
        
    elif varga == "D30":
        # Ernst Wilhelm / Kala uses the continuous 1-degree cyclical division for D30 (longitude * 30)
        return (longitude * 30.0) % 360.0
        
        
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

def generate_kala_chart(
    name: str = "Subject",
    year: int = 1995,
    month: int = 5,
    day: int = 15,
    hour: int = 14,
    minute: int = 30,
    latitude: float = 51.5074,
    longitude: float = -0.1278,
    timezone_offset: float = 1.0,
    name_sound_value: Optional[int] = None,
    output_filepath: Optional[str] = None
) -> Dict[str, Any]:
    
    # 1. Date and Time to Julian Day
    local_hour_fraction = hour + minute / 60.0
    
    # Determine calendar flag
    # Use Julian calendar for dates before Oct 15, 1582
    if year < 1582 or (year == 1582 and month < 10) or (year == 1582 and month == 10 and day < 15):
        cal_flag = swe.JUL_CAL
    else:
        cal_flag = swe.GREG_CAL
        
    jd_local = swe.julday(year, month, day, local_hour_fraction, cal_flag)
    
    # Calculate UTC JD by subtracting timezone offset (offset is in hours)
    jd = jd_local - (timezone_offset / 24.0)
    
    # Format a date string for the output
    birth_dt_str = f"{year:04d}-{month:02d}-{day:02d}T{hour:02d}:{minute:02d}:00"

    # 2. Tropical Ecliptic Calculations (Rasis & Vargas)
    flags_ecliptic = swe.FLG_SWIEPH | swe.FLG_SPEED
    
    # Houses (Campanus - standard Ernst Wilhelm Kala default)
    cusps, ascmc = swe.houses(jd, latitude, longitude, b'C')
    asc_lon = ascmc[0]
    mc_lon = ascmc[1]
    
    asc_sign, asc_deg = get_sign(asc_lon)
    
    vargas_harmonics = {
        "D1": 1, "D2": 2, "D3": 3, "D4": 4, "D7": 7, "D9": 9, 
        "D10": 10, "D12": 12, "D16": 16, "D20": 20, "D24": 24, 
        "D27": 27, "D30": 30, "D40": 40, "D45": 45, "D60": 60
    }
    
    # Pre-calculate base D1 longitudes and retrograde status for lagna and planets
    d1_longitudes = {"Lagna": asc_lon}
    d1_retrogrades = {"Lagna": False}
    
    planet_ids = {
        "Sun": swe.SUN,
        "Moon": swe.MOON,
        "Mars": swe.MARS,
        "Mercury": swe.MERCURY,
        "Jupiter": swe.JUPITER,
        "Venus": swe.VENUS,
        "Saturn": swe.SATURN,
        "Rahu": swe.TRUE_NODE
    }
    
    for p_name, p_id in planet_ids.items():
        if p_name == "Rahu":
            r_lon = calc_utils.calculate_interpolated_node(jd)
            d1_longitudes["Rahu"] = r_lon
            d1_longitudes["Ketu"] = (r_lon + 180.0) % 360.0
            d1_retrogrades["Rahu"] = False
            d1_retrogrades["Ketu"] = False
        else:
            res, _ = swe.calc_ut(jd, p_id, flags_ecliptic)
            d1_longitudes[p_name] = res[0]
            # Speed is res[3]. Negative speed indicates Retrograde (Vakri) motion
            speed = res[3]
            d1_retrogrades[p_name] = bool(speed < 0 and p_name not in ["Sun", "Moon"])
            
    # Calculate Vargas
    vargas_data = {}
    for v_name, harmonic in vargas_harmonics.items():
        vargas_data[v_name] = {
            "lagna": {},
            "grahas": {},
            "cusps": []
        }
        
        # Lagna
        l_lon = calculate_varga_longitude(d1_longitudes["Lagna"], v_name)
        l_sign, l_deg = get_sign(l_lon)
        vargas_data[v_name]["lagna"] = {
            "longitude": round(l_lon, 4),
            "sign": l_sign,
            "degree_0_to_30": l_deg
        }
        
        # Planets
        for p_name in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
            p_lon = calculate_varga_longitude(d1_longitudes[p_name], v_name)
            p_sign, p_deg = get_sign(p_lon)
            vargas_data[v_name]["grahas"][p_name] = {
                "longitude": round(p_lon, 4),
                "sign": p_sign,
                "degree_0_to_30": p_deg,
                "is_retrograde": d1_retrogrades.get(p_name, False)
            }
            
        # Cusps (Bhava Chalita)
        v_cusps = []
        for c in cusps:
            c_lon = calculate_varga_longitude(c, v_name)
            v_cusps.append(c_lon)
            
        bhavas = []
        for i in range(12):
            prev_cusp = v_cusps[(i - 1) % 12]
            curr_cusp = v_cusps[i]
            next_cusp = v_cusps[(i + 1) % 12]
            
            diff_prev = (curr_cusp - prev_cusp) % 360
            start = (prev_cusp + diff_prev / 2.0) % 360
            
            diff_next = (next_cusp - curr_cusp) % 360
            end = (curr_cusp + diff_next / 2.0) % 360
            
            bhavas.append({
                "house": i + 1,
                "start": round(start, 4),
                "cusp": round(curr_cusp, 4),
                "end": round(end, 4),
                "planets": []
            })
            
        # Assign planets to bhavas
        for p_name in ["Lagna", "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
            if p_name == "Lagna":
                p_lon = vargas_data[v_name]["lagna"]["longitude"]
            else:
                p_lon = vargas_data[v_name]["grahas"][p_name]["longitude"]
                
            for bhava in bhavas:
                s = bhava["start"]
                e = bhava["end"]
                in_house = False
                if s <= e:
                    if s <= p_lon < e:
                        in_house = True
                else:
                    if p_lon >= s or p_lon < e:
                        in_house = True
                if in_house:
                    bhava["planets"].append(p_name if p_name != "Lagna" else "Asc")
                    
        vargas_data[v_name]["bhavas"] = bhavas
        
        # We also keep the cusps list for drawing
        for c_lon in v_cusps:
            c_sign, c_deg = get_sign(c_lon)
            vargas_data[v_name]["cusps"].append({
                "longitude": round(c_lon, 4),
                "sign": c_sign,
                "degree_0_to_30": c_deg
            })

    # 2.5 Calculate Planetary Friendships, Dignity & Avasthas
    

    d1_grahas = vargas_data["D1"]["grahas"]


    for v_name, v_data in vargas_data.items():
        for p_name, p_data in v_data["grahas"].items():
            if p_name in ["Rahu", "Ketu"]:
                # Nodes use specific fixed dignities or their own special rules, but often follow Saturn/Mars
                proxy = "Saturn" if p_name == "Rahu" else "Mars"
                sign = p_data["sign"]
                sign_lord = rel.SIGN_LORDS[sign]
                p_v_idx = ZODIAC_SIGNS.index(sign)
                sign_lord_v_idx = ZODIAC_SIGNS.index(v_data["grahas"][sign_lord]["sign"])
                
                nat = rel.get_natural_relationship(p_name, sign_lord)
                # Use D1 chart positions for temporary relationship as per BPHS
                p_d1_idx = ZODIAC_SIGNS.index(d1_grahas[p_name]["sign"])
                sign_lord_d1_idx = ZODIAC_SIGNS.index(d1_grahas[sign_lord]["sign"])
                tmp = rel.get_temporary_relationship(p_d1_idx, sign_lord_d1_idx)
                cmp = rel.get_compound_relationship(nat, tmp)
                p_deg = p_data["degree_0_to_30"]
                nat_dig = rel.get_dignity(p_name, sign, nat, p_deg)
                cmp_dig = rel.get_dignity(p_name, sign, cmp, p_deg)
                
                p_data["dignity_breakdown"] = {
                    "sign_lord": sign_lord,
                    "natural_relationship": nat,
                    "temporary_relationship": tmp,
                    "compound_relationship": cmp,
                    "natural_dignity": nat_dig,
                    "final_dignity": cmp_dig
                }
            else:
                sign = p_data["sign"]
                sign_lord = rel.SIGN_LORDS[sign]
                
                if sign_lord == p_name:
                    nat, tmp, cmp = "Self", "Self", "Self"
                    p_deg = p_data["degree_0_to_30"]
                    nat_dig = rel.get_dignity(p_name, sign, "Self", p_deg)
                    cmp_dig = nat_dig
                else:
                    p_v_idx = ZODIAC_SIGNS.index(sign)
                    sign_lord_v_idx = ZODIAC_SIGNS.index(v_data["grahas"][sign_lord]["sign"])
                    
                    nat = rel.get_natural_relationship(p_name, sign_lord)
                    # Use D1 chart positions for temporary relationship as per BPHS
                    p_d1_idx = ZODIAC_SIGNS.index(d1_grahas[p_name]["sign"])
                    sign_lord_d1_idx = ZODIAC_SIGNS.index(d1_grahas[sign_lord]["sign"])
                    tmp = rel.get_temporary_relationship(p_d1_idx, sign_lord_d1_idx)
                    cmp = rel.get_compound_relationship(nat, tmp)
                    p_deg = p_data["degree_0_to_30"]
                    nat_dig = rel.get_dignity(p_name, sign, nat, p_deg)
                    cmp_dig = rel.get_dignity(p_name, sign, cmp, p_deg)
                    
                p_data["dignity_breakdown"] = {
                    "sign_lord": sign_lord,
                    "natural_relationship": nat,
                    "temporary_relationship": tmp,
                    "compound_relationship": cmp,
                    "natural_dignity": nat_dig,
                    "final_dignity": cmp_dig
                }
            
            # --- Prepare Data for Avasthas ---
            
            # Find conjunct planets (in the same sign in this Varga)
            conjunct_planets = [
                op_name for op_name, op_data in v_data["grahas"].items()
                if op_name != p_name and op_data["sign"] == p_data["sign"]
            ]
            
            # Find aspecting planets (via Rasi Drishti on this sign)
            aspecting_planets = []
            graha_aspecting_planets = []
            for op_name, op_data in v_data["grahas"].items():
                if op_name != p_name:
                    rasi_aspects = aspects.get_rasi_drishti(op_data["sign"])
                    if p_data["sign"] in rasi_aspects:
                        aspecting_planets.append(op_name)
                    
                    # Also calculate Graha Drishti for Avasthas
                    g_drishti = aspects.get_graha_drishti(
                        op_name, 
                        op_data["longitude"], 
                        p_data["longitude"], 
                        op_data["sign"], 
                        p_data["sign"]
                    )
                    if g_drishti > 0:
                        graha_aspecting_planets.append(op_name)
                        
            # Store what signs THIS planet aspects
            p_data["aspects_signs"] = aspects.get_rasi_drishti(p_data["sign"])
                        
            # Combustion (Physical phenomenon, so calculated strictly from D1 physical longitudes)
            # Uses Parashari/Surya Siddhanta specific degree orbs for each planet.
            is_combust = False
            if p_name not in ["Sun", "Rahu", "Ketu"]:
                sun_lon = d1_longitudes["Sun"]
                p_lon_d1 = d1_longitudes[p_name]
                dist = min((sun_lon - p_lon_d1) % 360, (p_lon_d1 - sun_lon) % 360)
                
                combustion_orbs = {
                    "Moon": 12.0,
                    "Mars": 17.0,
                    "Mercury": 14.0,
                    "Jupiter": 11.0,
                    "Venus": 10.0,
                    "Saturn": 15.0
                }
                orb = combustion_orbs.get(p_name, 8.0)
                is_combust = dist < orb
                
            is_retrograde = p_data.get("is_retrograde", False)
            malefics = ["Sun", "Mars", "Saturn", "Rahu", "Ketu"]
            is_conjunct_malefic = any(cp in malefics for cp in conjunct_planets)
            
            # House number: distance from Lagna in this Varga
            # We assume Whole Sign house system
            lagna_sign = v_data["lagna"]["sign"]
            lagna_idx = ZODIAC_SIGNS.index(lagna_sign)
            p_idx = ZODIAC_SIGNS.index(p_data["sign"])
            house_num = (p_idx - lagna_idx) % 12 + 1
            
            # Natural friends/enemies
            if p_name in ["Rahu", "Ketu"]:
                proxy = "Saturn" if p_name == "Rahu" else "Mars"
                natural_friends = rel.NAISARGIKA_SAMBANDHA.get(proxy, {}).get("Friends", [])
                natural_enemies = rel.NAISARGIKA_SAMBANDHA.get(proxy, {}).get("Enemies", [])
            else:
                natural_friends = rel.NAISARGIKA_SAMBANDHA.get(p_name, {}).get("Friends", [])
                natural_enemies = rel.NAISARGIKA_SAMBANDHA.get(p_name, {}).get("Enemies", [])

            # --- Calculate Avasthas ---
            # Jagradadi uses Natural Dignity per Parashara & Ernst Wilhelm
            bala_avastha = avasthas.get_bala_avastha(p_deg, p_data["sign"])
            jagrat_avastha = avasthas.get_jagrat_avastha(p_data["dignity_breakdown"]["natural_dignity"])
            deeptadi_avastha = avasthas.get_deeptadi_avastha(
                p_data["dignity_breakdown"]["final_dignity"],
                is_retrograde,
                is_combust,
                conjunct_planets
            )
            
            moon_lon = d1_longitudes["Moon"]
            sun_lon_d1 = d1_longitudes["Sun"]
            is_moon_waning = ((moon_lon - sun_lon_d1) % 360.0) >= 180.0
            is_waning_moon_as_enemy = is_moon_waning and ("Moon" in natural_enemies)
            
            lajjitadi_avastha = avasthas.get_lajjitadi_avasthas(
                p_name,
                p_data["sign"],
                house_num,
                p_data["dignity_breakdown"]["natural_dignity"],
                conjunct_planets,
                graha_aspecting_planets,
                natural_friends,
                natural_enemies,
                is_waning_moon_as_enemy
            )
            
            p_data["avasthas"] = {
                "bala": bala_avastha,
                "jagrat": jagrat_avastha,
                "deeptadi": deeptadi_avastha,
                "lajjitadi": lajjitadi_avastha
            }

    # 3. Equatorial Nakshatras & Galactic Center Ayanamsa
    flags_equatorial = swe.FLG_SWIEPH | swe.FLG_EQUATORIAL
    
    # Galactic Center RA
    try:
        res_gc, name_gc, _ = swe.fixstar2_ut("Galactic Center", jd, flags_equatorial)
        ra_gc = res_gc[0]
    except Exception:
        # Fallback approximation for ~1995 if fixstar fails
        ra_gc = 266.0
        
    # Ernst Wilhelm Ayanamsa: Mid of Mula is exactly 246.6667 degrees
    ayanamsa_eq = ra_gc - 246.6667
    
    # Get Equatorial positions of planets
    nakshatras_sidereal = {}
    
    # Calculate Ascendant Nakshatra
    eps = swe.calc_ut(jd, swe.ECL_NUT, 0)[0][0]
    asc_eq = swe.cotrans([asc_lon, 0.0, 1.0], -eps)
    asc_ra = asc_eq[0]
    sid_ra_asc = (asc_ra - ayanamsa_eq) % 360.0
    a_idx = int(sid_ra_asc / 13.3333333)
    a_pada = int((sid_ra_asc % 13.3333333) / 3.3333333) + 1
    nakshatras_sidereal["Lagna"] = {
        "nakshatra": NAKSHATRAS[a_idx],
        "pada": a_pada,
        "sidereal_ra": round(sid_ra_asc, 4)
    }

    for p_name, p_id in planet_ids.items():
        if p_name == "Rahu":
            r_lon = calc_utils.calculate_interpolated_node(jd)
            r_eq = swe.cotrans([r_lon, 0.0, 1.0], -eps)
            ra_planet = r_eq[0]
        else:
            res_eq, _ = swe.calc_ut(jd, p_id, flags_equatorial)
            ra_planet = res_eq[0]
        
        sidereal_ra = (ra_planet - ayanamsa_eq) % 360.0
        
        if p_name == "Rahu":
            ra_ketu = (ra_planet + 180.0) % 360.0
            sid_ra_ketu = (ra_ketu - ayanamsa_eq) % 360.0
            k_idx = int(sid_ra_ketu / 13.3333333)
            k_pada = int((sid_ra_ketu % 13.3333333) / 3.3333333) + 1
            nakshatras_sidereal["Ketu"] = {
                "nakshatra": NAKSHATRAS[k_idx],
                "pada": k_pada,
                "sidereal_ra": round(sid_ra_ketu, 4)
            }
            
        n_idx = int(sidereal_ra / 13.3333333)
        n_pada = int((sidereal_ra % 13.3333333) / 3.3333333) + 1
        
        nakshatras_sidereal[p_name] = {
            "nakshatra": NAKSHATRAS[n_idx],
            "pada": n_pada,
            "sidereal_ra": round(sidereal_ra, 4)
        }
        
    # --- 3.5 Calculate Shayanadi Avasthas ---
    
    # Calculate Sunrise (Center of Disk)
    res_rise = swe.rise_trans(jd, swe.SUN, swe.CALC_RISE | swe.BIT_DISC_CENTER, (longitude, latitude, 0.0), 0.0, 0.0)
    sunrise_jd = res_rise[1][0]
    
    # If birth was before today's sunrise, use yesterday's sunrise
    if sunrise_jd > jd:
        res_rise = swe.rise_trans(jd - 1.0, swe.SUN, swe.CALC_RISE | swe.BIT_DISC_CENTER, (longitude, latitude, 0.0), 0.0, 0.0)
        sunrise_jd = res_rise[1][0]
        
    minutes_elapsed = (jd - sunrise_jd) * 24.0 * 60.0
    ishta_ghati = math.ceil(minutes_elapsed / 24.0)
    if ishta_ghati <= 0: ishta_ghati = 1
    
    varnamashka = name_sound_value if name_sound_value else avasthas.get_varnamashka(name)
    lagna_rasi_no = ZODIAC_SIGNS.index(vargas_data["D1"]["lagna"]["sign"]) + 1
    moon_nakshatra_no = NAKSHATRAS.index(nakshatras_sidereal["Moon"]["nakshatra"]) + 1
    
    for p_name in planet_ids.keys():
        p_nak_no = NAKSHATRAS.index(nakshatras_sidereal[p_name]["nakshatra"]) + 1
        p_pada = nakshatras_sidereal[p_name]["pada"]
        
        shayanadi = avasthas.get_shayanadi_avastha(
            p_name, p_nak_no, p_pada, lagna_rasi_no, 
            moon_nakshatra_no, ishta_ghati, name_sound_value=varnamashka
        )
        
        # Add to D1 (and other vargas if they share the same dictionary ref, but let's safely add to all)
        for v_name in vargas_data:
            if p_name in vargas_data[v_name]["grahas"]:
                vargas_data[v_name]["grahas"][p_name]["avasthas"]["shayanadi"] = shayanadi

    # 4. Vimshottari Dasha (Basic calculation based on Equatorial Moon)
    moon_sid_ra = nakshatras_sidereal["Moon"]["sidereal_ra"]
    moon_n_idx = int(moon_sid_ra / 13.3333333)
    
    lord_idx = moon_n_idx % 9
    birth_md_lord = DASHA_LORDS[lord_idx]
    
    fraction_passed = (moon_sid_ra % 13.3333333) / 13.3333333
    fraction_left = 1.0 - fraction_passed
    
    total_md_years = DASHA_YEARS[lord_idx]
    balance_years = fraction_left * total_md_years
    
    # Calculate MD start and end based on Saura Years
    balance_days = balance_years * SAURA_YEAR_DAYS
    
    dashas_list = []
    current_end_jd = jd_local + balance_days
    
    # First dasha (balance at birth)
    md_end_y, md_end_m, md_end_d, _ = swe.revjul(current_end_jd, cal_flag)
    md_start_y, md_start_m, md_start_d, _ = swe.revjul(current_end_jd - (total_md_years * SAURA_YEAR_DAYS), cal_flag)
    
    dashas_list.append({
        "planet": birth_md_lord,
        "start": f"{md_start_y:04d}-{md_start_m:02d}-{md_start_d:02d}",
        "end": f"{md_end_y:04d}-{md_end_m:02d}-{md_end_d:02d}"
    })
    
    # Next 8 dashas
    for i in range(1, 9):
        next_idx = (lord_idx + i) % 9
        d_lord = DASHA_LORDS[next_idx]
        d_years = DASHA_YEARS[next_idx]
        
        start_jd = current_end_jd
        end_jd = start_jd + (d_years * SAURA_YEAR_DAYS)
        
        s_y, s_m, s_d, _ = swe.revjul(start_jd, cal_flag)
        e_y, e_m, e_d, _ = swe.revjul(end_jd, cal_flag)
        
        dashas_list.append({
            "planet": d_lord,
            "start": f"{s_y:04d}-{s_m:02d}-{s_d:02d}",
            "end": f"{e_y:04d}-{e_m:02d}-{e_d:02d}"
        })
        
        current_end_jd = end_jd
        
    # 5. Shadbala (6-fold strength)
    shadbala_data = calculate_shadbala(d1_longitudes, asc_lon, mc_lon, jd, longitude, latitude)
    
    # 6. Assemble JSON Context




    
    # 6. Quantitative Lajjitadi Avasthas
    from jyotish.avasthas.quantitative import calculate_avastha_matrix
    

    avastha_matrices = {}
    planets_list = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    baseline_types = ["ShadBala", "Subha", "Ishta", "Cheshta", "Uccha", "Dig", "Drishti Yuti"]
    
    for v_key in vargas_data.keys():
        avastha_matrices[v_key] = {}
        for baseline in baseline_types:
            avastha_results = calculate_avastha_matrix(vargas_data[v_key]["grahas"], shadbala_data, vargas_data["D1"]["grahas"], baseline_type=baseline)
            v_matrix = {}
            for p_receive in planets_list:
                v_matrix[p_receive] = {}
                for p_give in planets_list:
                    data = avastha_results['matrix'][p_give][p_receive]
                    
                    if p_give == p_receive:
                        v_matrix[p_receive][p_give] = {
                            "base": data["base"],
                            "base_negative": data["base_negative"],
                            "net_total": data["net_total"]
                        }
                        continue
                        
                    v_matrix[p_receive][p_give] = {
                        "positive_pull": data["positive_pull"],
                        "negative_pull": data["negative_pull"],
                        "isolated_positive": data["isolated_positive"],
                        "isolated_negative": data["isolated_negative"],
                        "net_pull": data["net_pull"],
                        "modifier": data["net_pull"],
                        "isolated_total": data["isolated_positive"] if data["net_pull"] >= 0 else data["isolated_negative"],
                        "is_positive": data["net_pull"] > 0
                    }
            avastha_matrices[v_key][baseline] = v_matrix
    vedic_context = {

        "subject_info": {
            "name": name,
            "birth_datetime": birth_dt_str,
            "latitude": latitude,
            "longitude": longitude,
            "timezone_offset": timezone_offset
        },
        "astronomy": {
            "ayanamsa_name": "Dhruva Galactic Center (Middle of Mula)",
            "equatorial_ayanamsa_value": round(ayanamsa_eq, 4),
            "galactic_center_ra": round(ra_gc, 4),
            "house_system": "Campanus (with Whole Sign overlay)",
            "dasha_year_length_days": SAURA_YEAR_DAYS,
            "julian_day": jd
        },
        "nakshatras": {
            "zodiac": "Sidereal Equatorial",
            "grahas": nakshatras_sidereal
        },
        "vargas": vargas_data,
        "vimshottari_dasha": {
            "at_birth": {
                "mahadasha": birth_md_lord,
                "mahadasha_balance_years": round(balance_years, 4),
            },
            "mahadashas": dashas_list
        },
        "shadbala": shadbala_data,
        "avastha_matrix": avastha_matrices,
        "advanced_aspects": aspects.calculate_advanced_graha_aspects(vargas_data["D1"]["grahas"], shadbala_data, vargas_data["D1"]["cusps"], asc_lon)
    }
    
    # 7. Write to file (only if requested)
    if output_filepath:
        with open(output_filepath, "w", encoding="utf-8") as f:
            json.dump(vedic_context, f, indent=2, ensure_ascii=False)
        print(f"Successfully generated Ernst Wilhelm Kala astrology context: {output_filepath}")
        
    return vedic_context

if __name__ == "__main__":
    generate_kala_chart(
        name="Arjuna",
        year=1995,
        month=5,
        day=15,
        hour=14,
        minute=30,
        latitude=28.6139,
        longitude=77.2090,
        timezone_offset=5.5,
        output_filepath="vedic_context.json"
    )
