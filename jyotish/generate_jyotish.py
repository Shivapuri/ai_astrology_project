import json
from jyotish.shadbala.shadbala import calculate_shadbala
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import math
import jyotish.relationships.relationships as rel
import jyotish.aspects.aspects as aspects
import jyotish.avasthas as avasthas
from jyotish.dashas.vimshottari import calculate_vimshottari_timeline, SAURA_YEAR_DAYS
import jyotish.ashtakavarga as ashtakavarga
import jyotish.vimshopaka as vimshopaka
import jyotish.sign_attributes as sign_attributes
import jyotish.planetary_evaluation as planetary_evaluation
import jyotish.karakas as karakas
import jyotish.report.report_engine as report_engine
from jyotish.bhavas.bhava_bala import calculate_bhava_bala

from jyotish.baseline import (
    calculate_varga_longitude,
    ZODIAC_SIGNS,
    NAKSHATRAS,
    NITYA_YOGAS,
    calculate_sub_lord,
    VIMSHOTTARI_SEQUENCE,
    VIMSHOTTARI_YEARS,
    ChartBaseline
)

DASHA_LORDS = ['Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury']
DASHA_YEARS = [7, 20, 6, 10, 7, 18, 16, 19, 17]

MEAN_DAILY_SPEEDS = {
    "Sun": 0.9856,
    "Moon": 13.1764,
    "Mars": 0.5240,
    "Mercury": 1.3833,
    "Jupiter": 0.0831,
    "Venus": 1.2000,
    "Saturn": 0.0335,
    "Rahu": 0.05295,
    "Ketu": 0.05295
}

# Geocentric mean daily speeds used in Ernst Wilhelm's Kala software
KALA_MEAN_DAILY_SPEEDS = {
    "Sun": 0.9856,
    "Moon": 13.1764,
    "Mars": 0.5240,
    "Mercury": 0.9856,
    "Jupiter": 0.0831,
    "Venus": 0.9856,
    "Saturn": 0.0334568,
    "Rahu": 0.05295,
    "Ketu": 0.05295
}


PLANET_ABBREVIATIONS = {
    "Sun": "Su", "Moon": "Mo", "Mars": "Ma", "Mercury": "Me",
    "Jupiter": "Ju", "Venus": "Ve", "Saturn": "Sa", "Rahu": "Ra", "Ketu": "Ke",
    "Lagna": "Lg"
}




def get_sign(longitude: float) -> tuple[str, float]:
    sign_idx = int(longitude // 30)
    deg_in_sign = longitude % 30
    return ZODIAC_SIGNS[sign_idx], round(deg_in_sign, 2)


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
    output_filepath: Optional[str] = None,
    d10_mode: str = "reverse",
    d24_mode: str = "reverse",
    place: str = "",
    second: int = 0,
    nakshatra_system: str = "ERNST_DHRUVA",
    debilitation_mode: str = "kala_degree",
    dig_bala_mode: str = "campanus",
    kendra_bala_mode: str = "flat_parashara"
) -> Dict[str, Any]:
    
    # 1. Instantiate certified Stage 1 Baseline (Single-Pass Ephemeris Extraction)
    baseline = ChartBaseline(
        name=name,
        year=year,
        month=month,
        day=day,
        hour=hour,
        minute=minute,
        second=second,
        latitude=latitude,
        longitude=longitude,
        timezone_offset=timezone_offset,
        place=place,
        d10_mode=d10_mode,
        d24_mode=d24_mode,
        nakshatra_system=nakshatra_system
    )
    anchors = baseline.astronomical_anchors
    coords = baseline.coordinates

    jd = anchors["jd_utc"]
    jd_local = anchors["jd_local"]
    cal_flag = anchors["cal_flag"]
    asc_lon = anchors["asc_longitude"]
    mc_lon = anchors["mc_longitude"]
    cusps = anchors["raw_campanus_cusps"]
    asc_sign, asc_deg = get_sign(asc_lon)

    # Format a standard DD/MM/YYYY date-time string for the output
    sec_int = int(round(second))
    if year < 0:
        birth_dt_str = f"{day:02d}/{month:02d}/{year} {hour:02d}:{minute:02d}:{sec_int:02d}"
    else:
        birth_dt_str = f"{day:02d}/{month:02d}/{year:04d} {hour:02d}:{minute:02d}:{sec_int:02d}"

    vargas_harmonics = {
        "D1": 1, "D2": 2, "D3": 3, "D4": 4, "D7": 7, "D9": 9, 
        "D10": 10, "D12": 12, "D16": 16, "D20": 20, "D24": 24, 
        "D27": 27, "D30": 30, "D40": 40, "D45": 45, "D60": 60
    }
    
    # Pre-calculate base D1 longitudes from baseline
    d1_longitudes = {p: coords[p]["longitude"] for p in coords}

    # 2. Ingest Certified Stage 1 Divisional Vargas
    import copy
    vargas_data = copy.deepcopy(baseline.vargas)

    # Harmonize D30 coordinates for Kala harmonic varga calculations
    if "D30" in vargas_data:
        for p_name, g_entry in vargas_data["D30"]["grahas"].items():
            if "continuous_harmonic_longitude" in g_entry:
                g_entry["longitude"] = g_entry["continuous_harmonic_longitude"]
                g_entry["sign"] = g_entry["continuous_sign"]
                g_entry["degree_0_to_30"] = g_entry["continuous_degree_in_sign"]
        if "lagna" in vargas_data["D30"] and "continuous_harmonic_longitude" in vargas_data["D30"]["lagna"]:
            vargas_data["D30"]["lagna"]["longitude"] = vargas_data["D30"]["lagna"]["continuous_harmonic_longitude"]
            vargas_data["D30"]["lagna"]["sign"] = vargas_data["D30"]["lagna"]["continuous_sign"]
            vargas_data["D30"]["lagna"]["degree_0_to_30"] = vargas_data["D30"]["lagna"]["continuous_degree_in_sign"]

    # Populate bhava occupancy for each varga (pure math, zero ephemeris)
    for v_name, v_dict in vargas_data.items():
        v_cusps = [c["longitude"] for c in v_dict.get("cusps", [])]
        if len(v_cusps) == 12:
            bhavas = []
            for i in range(12):
                prev_cusp = v_cusps[(i - 1) % 12]
                curr_cusp = v_cusps[i]
                next_cusp = v_cusps[(i + 1) % 12]

                diff_prev = (curr_cusp - prev_cusp) % 360.0
                start = (prev_cusp + diff_prev / 2.0) % 360.0
                diff_next = (next_cusp - curr_cusp) % 360.0
                end = (curr_cusp + diff_next / 2.0) % 360.0

                bhavas.append({
                    "house": i + 1,
                    "start": round(start, 4),
                    "cusp": round(curr_cusp, 4),
                    "end": round(end, 4),
                    "planets": []
                })

            # Assign planets to bhavas
            for p_name in ["Lagna", "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
                p_lon = v_dict["lagna"]["longitude"] if p_name == "Lagna" else v_dict["grahas"][p_name]["longitude"]
                for bhava in bhavas:
                    s = bhava["start"]
                    e = bhava["end"]
                    in_house = (s <= p_lon < e) if s <= e else (p_lon >= s or p_lon < e)
                    if in_house:
                        bhava["planets"].append(p_name if p_name != "Lagna" else "Asc")
            v_dict["bhavas"] = bhavas

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
                nat_dig = rel.get_dignity(p_name, sign, nat, p_deg, debilitation_mode=debilitation_mode)
                cmp_dig = rel.get_dignity(p_name, sign, cmp, p_deg, debilitation_mode=debilitation_mode)
                
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
                    nat_dig = rel.get_dignity(p_name, sign, "Self", p_deg, debilitation_mode=debilitation_mode)
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
                    nat_dig = rel.get_dignity(p_name, sign, nat, p_deg, debilitation_mode=debilitation_mode)
                    cmp_dig = rel.get_dignity(p_name, sign, cmp, p_deg, debilitation_mode=debilitation_mode)
                    
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
                        
            is_retrograde = p_data.get("is_retrograde", False)

            # Combustion (Physical phenomenon, so calculated strictly from D1 physical longitudes)
            # Uses Surya Siddhanta / Varaha Mihira specific degree orbs for each planet,
            # in full alignment with "The Art and Science of Vedic Astrology" and Kala software parameters.
            is_combust = False
            sun_dist = None
            comb_orb = None
            comb_severity = None
            comb_range = None
            if p_name not in ["Sun", "Rahu", "Ketu"]:
                sun_lon = d1_longitudes["Sun"]
                p_lon_d1 = d1_longitudes[p_name]
                dist = min((sun_lon - p_lon_d1) % 360, (p_lon_d1 - sun_lon) % 360)
                sun_dist = round(dist, 4)
                
                # Classical Surya Siddhanta orbs (with retrograde contraction per scripture)
                if p_name == "Mercury":
                    orb = 12.0 if is_retrograde else 14.0
                elif p_name == "Venus":
                    orb = 8.0 if is_retrograde else 10.0
                elif p_name == "Moon":
                    orb = 12.0
                elif p_name == "Mars":
                    orb = 17.0
                elif p_name == "Jupiter":
                    orb = 11.0
                elif p_name == "Saturn":
                    orb = 15.0
                else:
                    orb = 8.0
                
                comb_ranges = {
                    "Moon": "12° - 15°",
                    "Mars": "8° - 17°",
                    "Mercury": "2° - 14°",
                    "Jupiter": "8° - 11°",
                    "Venus": "4° - 10°",
                    "Saturn": "8° - 15°"
                }
                comb_range = comb_ranges.get(p_name, f"{orb}°")
                comb_orb = orb
                is_combust = dist < orb
                if is_combust:
                    comb_severity = "Deep (< 3°)" if dist < 3.0 else "Moderate"
            
            p_data["is_combust"] = is_combust
            p_data["sun_distance"] = sun_dist
            p_data["combustion_orb"] = comb_orb
            p_data["combustion_severity"] = comb_severity
            p_data["combustion_range"] = comb_range
                
            malefics = ["Sun", "Mars", "Saturn", "Rahu", "Ketu"]
            is_conjunct_malefic = any(cp in malefics for cp in conjunct_planets)
            
            # House number: distance from Lagna in this Varga
            # We assume Whole Sign house system
            lagna_sign = v_data["lagna"]["sign"]
            lagna_idx = ZODIAC_SIGNS.index(lagna_sign)
            p_idx = ZODIAC_SIGNS.index(p_data["sign"])
            house_num = (p_idx - lagna_idx) % 12 + 1
            
            p_data["ruled_houses"] = [
                (s_idx - lagna_idx) % 12 + 1
                for s_idx, s_name in enumerate(ZODIAC_SIGNS)
                if rel.SIGN_LORDS.get(s_name) == p_name
            ]
            
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

    # 3. Ingest Certified Stage 1 Nakshatras & Coordinates
    nakshatras_sidereal = baseline.nakshatras["grahas"]
    ayanamsa_eq = baseline.nakshatras["equatorial_ayanamsa"]
    ayanamsa_ecl = baseline.nakshatras["ecliptic_ayanamsa"]

    # Galactic Center coordinates from baseline
    ra_gc = 266.0371
    lon_gc = 266.5179

    # Speeds and Relative Speeds directly from baseline.coordinates
    d1_speeds = {}
    d1_rel_speeds = {"Lagna": "--"}
    d1_rel_speeds_pct = {}
    for p_name in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
        spd = coords[p_name]["speed"]
        if p_name in ["Rahu", "Ketu"]:
            # Lunar nodes are permanently retrograde in classical Jyotish; project equatorial speed
            r_lon_rad = math.radians(coords[p_name]["longitude"])
            eps_rad = math.radians(23.4392911)
            d_ra_d_lon = math.cos(eps_rad) / (1.0 - math.sin(eps_rad)**2 * math.sin(r_lon_rad)**2)
            spd = -abs(spd * d_ra_d_lon * (1.0 - 0.0053))
        d1_speeds[p_name] = round(spd, 4)
        mean_speed = KALA_MEAN_DAILY_SPEEDS.get(p_name, 1.0)
        ratio = (spd / mean_speed) * 100.0 if mean_speed > 0 else 100.0
        d1_rel_speeds[p_name] = f"{ratio:.2f}%"
        d1_rel_speeds_pct[p_name] = round(ratio, 2)

    # Calculate Navatara & Lord/Sublord for all entities
    moon_nak_idx = NAKSHATRAS.index(nakshatras_sidereal["Moon"]["nakshatra"])
    for ent_name, n_info in nakshatras_sidereal.items():
        t_nak_idx = NAKSHATRAS.index(n_info["nakshatra"])
        tara_idx = ((t_nak_idx - moon_nak_idx) % 27 % 9) + 1
        n_info["tara"] = tara_idx
        n_info["tara_number"] = tara_idx
        
        pos = n_info.get("sidereal_longitude") if ent_name == "Lagna" else n_info.get("sidereal_ra", 0.0)
        nak_fraction = (pos % (360.0 / 27.0)) / (360.0 / 27.0)
        nak_lord = VIMSHOTTARI_SEQUENCE[t_nak_idx % 9]
        sub_lord = calculate_sub_lord(nak_fraction, nak_lord)
        
        n_info["nakshatra_lord"] = nak_lord
        n_info["sub_lord"] = sub_lord
        n_info["lord_sublord"] = f"{PLANET_ABBREVIATIONS.get(nak_lord, nak_lord[:2])}/{PLANET_ABBREVIATIONS.get(sub_lord, sub_lord[:2])}"
        n_info["relative_speed"] = d1_rel_speeds.get(ent_name, "--")

    # Add nakshatra, pada, lord/sublord, tara, and speed info to D1 grahas and lagna
    for p_name in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
        if p_name in vargas_data["D1"]["grahas"] and p_name in nakshatras_sidereal:
            vargas_data["D1"]["grahas"][p_name]["nakshatra"] = nakshatras_sidereal[p_name]["nakshatra"]
            vargas_data["D1"]["grahas"][p_name]["pada"] = nakshatras_sidereal[p_name]["pada"]
            vargas_data["D1"]["grahas"][p_name]["tara"] = nakshatras_sidereal[p_name]["tara"]
            vargas_data["D1"]["grahas"][p_name]["tara_number"] = nakshatras_sidereal[p_name]["tara"]
            vargas_data["D1"]["grahas"][p_name]["nakshatra_lord"] = nakshatras_sidereal[p_name]["nakshatra_lord"]
            vargas_data["D1"]["grahas"][p_name]["sub_lord"] = nakshatras_sidereal[p_name]["sub_lord"]
            vargas_data["D1"]["grahas"][p_name]["lord_sublord"] = nakshatras_sidereal[p_name]["lord_sublord"]
            vargas_data["D1"]["grahas"][p_name]["speed"] = d1_speeds.get(p_name, 0.0)
            vargas_data["D1"]["grahas"][p_name]["relative_speed"] = d1_rel_speeds.get(p_name, "--")
            vargas_data["D1"]["grahas"][p_name]["relative_speed_pct"] = d1_rel_speeds_pct.get(p_name)
            
    # Lunar nodes are permanently retrograde in classical Jyotish / Kala
    vargas_data["D1"]["grahas"]["Rahu"]["is_retrograde"] = True
    vargas_data["D1"]["grahas"]["Ketu"]["is_retrograde"] = True

    vargas_data["D1"]["lagna"]["nakshatra"] = nakshatras_sidereal["Lagna"]["nakshatra"]
    vargas_data["D1"]["lagna"]["pada"] = nakshatras_sidereal["Lagna"]["pada"]
    vargas_data["D1"]["lagna"]["tara"] = nakshatras_sidereal["Lagna"]["tara"]
    vargas_data["D1"]["lagna"]["tara_number"] = nakshatras_sidereal["Lagna"]["tara"]
    vargas_data["D1"]["lagna"]["nakshatra_lord"] = nakshatras_sidereal["Lagna"]["nakshatra_lord"]
    vargas_data["D1"]["lagna"]["sub_lord"] = nakshatras_sidereal["Lagna"]["sub_lord"]
    vargas_data["D1"]["lagna"]["lord_sublord"] = nakshatras_sidereal["Lagna"]["lord_sublord"]
    vargas_data["D1"]["lagna"]["relative_speed"] = "--"
        
    # --- 3.5 Calculate Shayanadi Avasthas ---
    
    # Sunrise from certified Stage 1 anchors
    sunrise_jd = anchors["sunrise_jd"]
    minutes_elapsed = max(0.0, (jd - sunrise_jd) * 24.0 * 60.0)
    ishta_ghati = math.ceil(minutes_elapsed / 24.0)
    if ishta_ghati <= 0:
        ishta_ghati = 1
    
    varnamashka = name_sound_value if name_sound_value else avasthas.get_varnamashka(name)
    moon_nakshatra_no = NAKSHATRAS.index(nakshatras_sidereal["Moon"]["nakshatra"]) + 1
    all_planets_shayana = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]

    for v_name, v_data in vargas_data.items():
        v_lagna_sign_no = ZODIAC_SIGNS.index(v_data["lagna"]["sign"]) + 1
        harmonic = vargas_harmonics.get(v_name, 1)

        for p_name in all_planets_shayana:
            if p_name in v_data["grahas"] and p_name in nakshatras_sidereal:
                v_data["grahas"][p_name]["nakshatra"] = nakshatras_sidereal[p_name]["nakshatra"]
                p_nak_no = NAKSHATRAS.index(nakshatras_sidereal[p_name]["nakshatra"]) + 1
                if v_name == "D1":
                    p_amsa = nakshatras_sidereal[p_name]["pada"]
                else:
                    lon = d1_longitudes[p_name]
                    deg_in_sign = lon % 30.0
                    p_amsa = avasthas.get_varga_amsa_factor(deg_in_sign, harmonic)

                shayanadi = avasthas.get_shayanadi_avastha(
                    p_name, p_nak_no, p_amsa, v_lagna_sign_no,
                    moon_nakshatra_no, ishta_ghati, name_sound_value=varnamashka
                )
                v_data["grahas"][p_name]["avasthas"]["shayanadi"] = shayanadi

        for p_name in ["Uranus", "Neptune", "Pluto"]:
            if p_name in v_data.get("grahas", {}) and p_name in nakshatras_sidereal:
                v_data["grahas"][p_name]["nakshatra"] = nakshatras_sidereal[p_name]["nakshatra"]
        if "Lagna" in nakshatras_sidereal and "lagna" in v_data:
            v_data["lagna"]["nakshatra"] = nakshatras_sidereal["Lagna"]["nakshatra"]

    # 4. Vimshottari Dasha (Using precalculated Moon from baseline)
    moon_nak = baseline.nakshatras["grahas"]["Moon"]
    if nakshatra_system == "VIC_CHITRA":
        moon_sid_lon = moon_nak["sidereal_longitude"]
        dasha_timeline = calculate_vimshottari_timeline(
            moon_sidereal_ra=moon_sid_lon,
            birth_jd_local=jd_local,
            cal_flag=cal_flag,
            total_cycles=1,
            dasha_year_days=SAURA_YEAR_DAYS,
            nakshatra_system=nakshatra_system,
            birth_jd_utc=jd,
            moon_sidereal_lon=moon_sid_lon
        )
    else:
        moon_sid_ra = moon_nak["sidereal_ra"]
        dasha_timeline = calculate_vimshottari_timeline(
            moon_sidereal_ra=moon_sid_ra,
            birth_jd_local=jd_local,
            cal_flag=cal_flag,
            total_cycles=1,
            dasha_year_days=SAURA_YEAR_DAYS,
            nakshatra_system=nakshatra_system,
            birth_jd_utc=jd
        )
        
    # 5. Shadbala (6-fold strength)
    dignities = rel.calculate_chart_dignities(baseline, debilitation_mode=debilitation_mode)
    aspect_matrices = aspects.calculate_aspect_matrices(baseline)

    # Certified Pipeline Ingestion:
    shadbala_data = calculate_shadbala(
        baseline,
        dignities=dignities,
        aspect_matrices=aspect_matrices,
        debilitation_mode=debilitation_mode,
        dig_bala_mode=dig_bala_mode,
        kendra_bala_mode=kendra_bala_mode
    )

    # Stage 3: House Capacity & Bhāva Bala
    bhava_bala_data = calculate_bhava_bala(
        baseline=baseline,
        shadbala_results=shadbala_data,
        aspect_matrices=aspect_matrices
    )
    
    # 6. Assemble JSON Context




    
    # 6. Vimshopaka Bala (Varga Dignity Scores)
    vimshopaka_data = vimshopaka.calculate_varga_vimshopaka_engine({"vargas": vargas_data})
    vimshopaka_export = {
        **vimshopaka_data,
        "shadvarga": vimshopaka_data["scores"].get("Shadvarga", {}),
        "saptavarga": vimshopaka_data["scores"].get("Saptavarga", {}),
        "dasavarga": vimshopaka_data["scores"].get("Dasavarga", {}),
        "shodashavarga": vimshopaka_data["scores"].get("Shodasavarga", {}),
        "vaisheshikamsa": {
            p: vimshopaka_data["vaisheshikamsa"].get("Shodasavarga", {}).get(p, {}).get("honorific", "-")
            for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
        }
    }

    # 7. Quantitative Lajjitadi Avasthas
    from jyotish.avasthas.quantitative import calculate_avastha_matrix

    avastha_matrices = {}
    planets_list = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    baseline_types = ["ShadBala", "Vimshopaka", "Subha", "Ishta", "Cheshta", "Uccha", "Dig", "Drishti Yuti", "Veda"]
    
    for v_key in vargas_data.keys():
        avastha_matrices[v_key] = {}
        for b_type in baseline_types:
            avastha_results = calculate_avastha_matrix(
                vargas_data[v_key]["grahas"],
                shadbala_data,
                vargas_data["D1"]["grahas"],
                baseline_type=b_type,
                varga_name=v_key,
                vimshopaka_data=vimshopaka_data
            )
            v_matrix = {}
            for p_give in planets_list:
                v_matrix[p_give] = {}
                for p_receive in planets_list:
                    v_matrix[p_give][p_receive] = avastha_results['matrix'][p_give][p_receive]
            avastha_matrices[v_key][b_type] = v_matrix
    # 8. Advanced Graha Aspects across all Vargas
    varga_aspects = {}
    for v_key in vargas_data.keys():
        varga_aspects[v_key] = aspects.calculate_varga_aspects(vargas_data[v_key])


    ashtakavarga_data = ashtakavarga.calculate_ashtakavarga_engine({"vargas": vargas_data})
    pindas = ashtakavarga_data.get('sodhya_pindas', {})
    r_tot = sum(pindas[p]['rasi_pinda'] for p in pindas if isinstance(pindas[p], dict) and 'rasi_pinda' in pindas[p])
    g_tot = sum(pindas[p]['graha_pinda'] for p in pindas if isinstance(pindas[p], dict) and 'graha_pinda' in pindas[p])
    ashtakavarga_data['sav'] = ashtakavarga_data['sarvashtakavarga']['total_sav']
    ashtakavarga_data['shodhya_pindas'] = {
        **pindas,
        'rasi_pinda_total': r_tot,
        'graha_pinda_total': g_tot,
        'yoga_pinda_total': r_tot + g_tot,
    }

    # 9. Karakas (Chara & Naisargika) and Functional Roles (Yogakaraka, Maraka, Badhaka)
    chara_karakas = karakas.calculate_chara_karakas(vargas_data["D1"]["grahas"])
    functional_roles_d1 = karakas.calculate_functional_roles(vargas_data["D1"]["lagna"]["sign"])
    varga_functional_roles = karakas.get_all_varga_functional_roles(vargas_data)

    for v_name, v_data in vargas_data.items():
        v_roles = varga_functional_roles.get(v_name, {})
        for p_name, p_data in v_data["grahas"].items():
            p_data["chara_karaka"] = chara_karakas.get(p_name, {})
            p_data["functional_role"] = v_roles.get(p_name, {})
            p_data["d1_functional_role"] = functional_roles_d1.get(p_name, {})

    # 10. Classical Yogas & Yoga Breaker Audit
    from jyotish.yogas import detect_all_yogas
    yogas_data = detect_all_yogas({
        "vargas": vargas_data,
        "shadbala": shadbala_data,
        "advanced_aspects": varga_aspects["D1"],
        "nakshatras": {"grahas": nakshatras_sidereal},
    })

    vedic_context = {

        "subject_info": {
            "name": name,
            "birth_datetime": birth_dt_str,
            "latitude": latitude,
            "longitude": longitude,
            "timezone_offset": timezone_offset,
            "place": place
        },
        "calculation_settings": {
            "d10_mode": d10_mode,
            "d24_mode": d24_mode,
            "debilitation_mode": debilitation_mode,
            "nakshatra_system": nakshatra_system,
            "ayanamsa_name": "Lahiri / Chitra Paksha" if nakshatra_system == "VIC_CHITRA" else "Dhruva Galactic Center (Middle of Mula)"
        },
        "astronomy": {
            "nakshatra_system": nakshatra_system,
            "ayanamsa_name": "Lahiri / Chitra Paksha" if nakshatra_system == "VIC_CHITRA" else "Dhruva Galactic Center (Middle of Mula)",
            "equatorial_ayanamsa_value": round(ayanamsa_eq, 4),
            "ecliptic_ayanamsa_value": round(ayanamsa_ecl, 4),
            "galactic_center_ra": round(ra_gc, 4),
            "galactic_center_lon": round(lon_gc, 4),
            "house_system": "Campanus (with Whole Sign overlay)",
            "dasha_year_length_days": SAURA_YEAR_DAYS,
            "julian_day": jd
        },
        "nakshatras": {
            "zodiac": "Sidereal Ecliptic (Lahiri / Chitra)" if nakshatra_system == "VIC_CHITRA" else "Sidereal Equatorial",
            "system": nakshatra_system,
            "grahas": nakshatras_sidereal
        },
        "vargas": vargas_data,
        "vimshottari_dasha": {
            "at_birth": dasha_timeline["at_birth"],
            "mahadashas": dasha_timeline["mahadashas"],
            "antardashas": dasha_timeline["antardashas"],
        },
        "shadbala": shadbala_data,
        "bhava_bala": bhava_bala_data,
        "avastha_matrix": avastha_matrices,
        "varga_lajjitadi_net_modifiers": avasthas.calculate_varga_lajjitadi_net_modifiers(vargas_data),
        "advanced_aspects": varga_aspects["D1"],
        "varga_advanced_aspects": varga_aspects,
        "ashtakavarga": ashtakavarga_data,
        "varga_vimshopaka": vimshopaka_data,
        "vimshopaka": vimshopaka_export,
        "sign_attributes": {v_k: sign_attributes.calculate_sign_distributions(v_data) for v_k, v_data in vargas_data.items()},
        "planetary_evaluation": planetary_evaluation.calculate_planetary_evaluation(vargas_data, shadbala_data, varga_aspects.get("D1")),
        "karakas": {
            "chara": chara_karakas,
            "functional": functional_roles_d1,
            "varga_functional": varga_functional_roles,
            "naisargika": karakas.NAISARGIKA_KARAKAS
        },
        "yogas": yogas_data
    }
    
    # 6.5 Astrological Synthesis Report (Master Ingredients Desk)
    vedic_context["report"] = report_engine.generate_report_payload(vedic_context)

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
