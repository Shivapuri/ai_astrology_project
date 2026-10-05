"""
jyotish/bhavas/bhava_bala.py
============================
Enterprise-Grade House Capacity & Bhāva Synthesis Engine for Astra Jyotish.

Calibrated against:
- Parāśara's BPHS (Ch. 27–31, 74)
- Mantreśvara's Phaladeepika (Ch. 4, 6, 14, 15)

Key Pillars & Diagnostics:
1. Quantitative 3-Pillar Parāśarī Bhāva Bala (Virūpas & Rūpas).
2. Phaladeepika Lord Digbala amplification & Sign/Sect matching (Ch. 4).
3. Aspect ray ingestion with qualified House Lord & Lagneśa Protection (Ch. 15.1–3, 9).
4. Triad Triangulation (Janma Lagna, Chandra Lagna, Kāraka Lagna: Ch. 15.6).
5. 3-Focal-Point Cumulative Analysis (Bhāva, Bhāveśa, Kāraka: Ch. 15.1–3, 18).
6. Bhāva Sandhi, Kartarī Yogas, and Jīva-Kārakobhāvanāśāya.
7. Harsha Bala (PVR Narasimha Rao Ch. 28.3) and Dusthāna Joy Reversals.
8. Unified 12-House Atmosphere & Environmental Weather Model.
"""

from typing import Dict, List, Any, Optional, Tuple

try:
    from jyotish.baseline_tables import (
        ZODIAC_SIGNS,
        SIGN_LORDS,
        NATURAL_MALEFICS,
        NATURAL_BENEFICS,
        UPACAYA_HOUSES,
        KENDRA_HOUSES,
        TRIKONA_HOUSES,
        DUHSTHANA_HOUSES,
        EXALTATION_SIGNS,
        FIXED_DIGNITIES,
    )
except ImportError:
    ZODIAC_SIGNS = [
        "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
        "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
    ]
    SIGN_LORDS = {
        "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury", "Cancer": "Moon",
        "Leo": "Sun", "Virgo": "Mercury", "Libra": "Venus", "Scorpio": "Mars",
        "Sagittarius": "Jupiter", "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter"
    }
    NATURAL_MALEFICS = {"Sun", "Mars", "Saturn", "Rahu", "Ketu"}
    NATURAL_BENEFICS = {"Jupiter", "Venus", "Moon", "Mercury"}
    UPACAYA_HOUSES = {3, 6, 10, 11}
    KENDRA_HOUSES = {1, 4, 7, 10}
    TRIKONA_HOUSES = {1, 5, 9}
    DUHSTHANA_HOUSES = {6, 8, 12}
    EXALTATION_SIGNS = {
        "Sun": "Aries", "Moon": "Taurus", "Mars": "Capricorn",
        "Mercury": "Virgo", "Jupiter": "Cancer", "Venus": "Pisces", "Saturn": "Libra"
    }
    FIXED_DIGNITIES = {}

SIGNS: List[str] = ZODIAC_SIGNS
VALID_PLANETS = {"Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"}

HARSHA_JOY_HOUSES: Dict[str, int] = {
    "Sun": 9,
    "Moon": 3,
    "Mars": 6,
    "Mercury": 1,
    "Jupiter": 11,
    "Venus": 5,
    "Saturn": 12,
}

FEMININE_PLANETS = {"Moon", "Mercury", "Venus", "Saturn"}
MASCULINE_PLANETS = {"Sun", "Mars", "Jupiter"}
FEMININE_HOUSES = {1, 2, 3, 7, 8, 9}
MASCULINE_HOUSES = {4, 5, 6, 10, 11, 12}

ZERO_HOUSES: Dict[str, int] = {
    "Nara": 7,          # Human signs peak in 1st, zero in 7th
    "Jalachara": 10,    # Watery signs peak in 4th, zero in 10th
    "Keeta": 1,         # Insect signs peak in 7th, zero in 1st
    "Chathushpada": 4   # Quadruped signs peak in 10th, zero in 4th
}

BHAVA_KARAKAS: Dict[int, List[str]] = {
    1: ["Sun"],
    2: ["Jupiter"],
    3: ["Mars"],
    4: ["Moon", "Mercury"],
    5: ["Jupiter"],
    6: ["Mars", "Saturn"],
    7: ["Venus"],
    8: ["Saturn"],
    9: ["Jupiter", "Sun"],
    10: ["Mercury", "Sun", "Jupiter", "Saturn"],
    11: ["Jupiter"],
    12: ["Saturn", "Ketu"]
}

PLANET_REQUIRED_VIRUPAS: Dict[str, float] = {
    "Mercury": 420.0, "Sun": 390.0, "Jupiter": 390.0,
    "Moon": 360.0, "Venus": 330.0, "Mars": 300.0, "Saturn": 300.0
}

DEBILITATION_SIGNS: Dict[str, str] = {
    "Sun": "Libra", "Moon": "Scorpio", "Mars": "Cancer",
    "Mercury": "Pisces", "Jupiter": "Capricorn", "Venus": "Virgo", "Saturn": "Aries"
}


def get_sign_genus(sign_name: str, deg_in_sign: float) -> str:
    """Classifies sign degree into Nara, Jalachara, Chathushpada, or Keeta per BPHS Ch. 27."""
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
    """Computes Bhava Digbala (0 to 60 Virūpas)."""
    sign_idx = int((bhava_madhya_lon % 360.0) / 30.0)
    deg_in_sign = bhava_madhya_lon % 30.0
    genus = get_sign_genus(SIGNS[sign_idx], deg_in_sign)
    
    zero_h = ZERO_HOUSES[genus]
    dist = abs(bhava_num - zero_h) % 12
    if dist > 6:
        dist = 12 - dist
        
    return round(dist * 10.0, 2)


def _extract_cusp_drishti(
    cusp_drishti_matrix: Optional[Dict[str, Any]], 
    planet: str, 
    house_num: int
) -> Optional[float]:
    """Safely extracts raw aspect ray from dual-indexed cusp drishti matrix."""
    if not cusp_drishti_matrix or not isinstance(cusp_drishti_matrix, dict):
        return None

    # Check nested "by_planet" (from calculate_aspect_matrices)
    by_planet = cusp_drishti_matrix.get("by_planet")
    if isinstance(by_planet, dict) and planet in by_planet and isinstance(by_planet[planet], dict):
        p_sub = by_planet[planet]
        if house_num in p_sub:
            return float(p_sub[house_num])
        if str(house_num) in p_sub:
            return float(p_sub[str(house_num)])

    # Check nested "by_house" (from calculate_aspect_matrices)
    by_house = cusp_drishti_matrix.get("by_house")
    if isinstance(by_house, dict):
        for h_key in (house_num, str(house_num)):
            if h_key in by_house and isinstance(by_house[h_key], dict):
                h_sub = by_house[h_key]
                if planet in h_sub:
                    return float(h_sub[planet])
        
    # Format 1: matrix[planet][house_num]
    if planet in cusp_drishti_matrix and isinstance(cusp_drishti_matrix[planet], dict):
        p_sub = cusp_drishti_matrix[planet]
        if house_num in p_sub:
            return float(p_sub[house_num])
        if str(house_num) in p_sub:
            return float(p_sub[str(house_num)])
            
    # Format 2: matrix[house_num][planet]
    for h_key in (house_num, str(house_num)):
        if h_key in cusp_drishti_matrix and isinstance(cusp_drishti_matrix[h_key], dict):
            h_sub = cusp_drishti_matrix[h_key]
            if planet in h_sub:
                return float(h_sub[planet])
                
    return None


def _calculate_fallback_drishti_ray(planet: str, p_lon: float, target_lon: float) -> float:
    """Parāśarī graduated aspect curve fallback (0-60 Virūpas)."""
    try:
        from jyotish.aspects.aspects import get_graha_drishti
        return float(get_graha_drishti(planet, p_lon, target_lon))
    except Exception:
        pass

    diff = (target_lon - p_lon) % 360.0
    val = 0.0
    
    if 30.0 <= diff < 60.0:
        val = (diff - 30.0) / 2.0
    elif 60.0 <= diff < 90.0:
        val = 15.0 + (diff - 60.0)
    elif 90.0 <= diff < 120.0:
        val = 45.0 + (diff - 90.0) / 2.0
    elif 120.0 <= diff < 150.0:
        val = 60.0 - (diff - 120.0) * 2.0
    elif 150.0 <= diff < 180.0:
        val = (diff - 150.0) * 2.0
    elif 180.0 <= diff < 300.0:
        val = 60.0 - (diff - 180.0) / 2.0
    else:
        val = 0.0

    if planet == "Mars":
        if 90.0 <= diff < 120.0:
            val = max(val, 60.0 - abs(diff - 90.0) * 2.0)
        elif 210.0 <= diff < 240.0:
            val = max(val, 60.0 - abs(diff - 210.0) * 2.0)
    elif planet == "Jupiter":
        if 120.0 <= diff < 150.0:
            val = max(val, 60.0 - abs(diff - 120.0) * 2.0)
        elif 240.0 <= diff < 270.0:
            val = max(val, 60.0 - abs(diff - 240.0) * 2.0)
    elif planet == "Saturn":
        if 60.0 <= diff < 90.0:
            val = max(val, 60.0 - abs(diff - 60.0) * 2.0)
        elif 270.0 <= diff < 300.0:
            val = max(val, 60.0 - abs(diff - 270.0) * 2.0)
            
    return max(0.0, min(60.0, val))


def calculate_bhava_drishti_bala(
    bhava_madhya_lon: float,
    planet_positions: Dict[str, Any],
    aspect_matrices: Optional[Dict[str, Any]] = None,
    house_num: Optional[int] = None,
    target_house_lord: Optional[str] = None,
    is_moon_benefic: bool = True,
    is_mercury_malefic: bool = False,
    lagna_lord: Optional[str] = None,
    combustion_map: Optional[Dict[str, Any]] = None,
    **kwargs
) -> float:
    """
    Computes aspectual Virūpas on the Bhava Madhya per Parāśara BPHS Ch. 27 v. 28–29.
    - Phaladeepika Ch. 15.1-3 / BPHS Ch. 27: Only the Lord of the aspected house gets
      positive ray inversion (+1.0), UNLESS combust or debilitated (+0.25 impaired protection).
    - Note: Lagneśa aspect is an environmental flourishing factor in Atmosphere (DPK 15.9),
      not a quantitative Parāśarī Virūpas inverter (avoiding Kuja Dosha registration as benefic).
    - Jupiter & Benefic Mercury: +1.0 ray weight (scaled down to /2.0 if combust/debilitated).
    - Venus & Benefic Moon: +0.25 ray weight.
    - Natural Malefics: -0.25 ray weight.
    """
    if isinstance(aspect_matrices, bool):
        is_moon_benefic = aspect_matrices
        aspect_matrices = None
    if isinstance(house_num, bool):
        is_mercury_malefic = house_num
        house_num = None

    cusp_drishti_matrix = None
    if aspect_matrices and isinstance(aspect_matrices, dict):
        cusp_drishti_matrix = aspect_matrices.get("cusp_drishti", aspect_matrices)

    combustion_map = combustion_map or {}
    malefics = ["Sun", "Mars", "Saturn"]
    if not is_moon_benefic:
        malefics.append("Moon")
    if is_mercury_malefic:
        malefics.append("Mercury")

    net_drishti = 0.0
    for planet in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
        if planet not in planet_positions:
            continue

        raw_aspect = None
        if cusp_drishti_matrix and house_num is not None:
            raw_aspect = _extract_cusp_drishti(cusp_drishti_matrix, planet, house_num)

        if raw_aspect is None:
            p_val = planet_positions[planet]
            p_lon = p_val if isinstance(p_val, (int, float)) else getattr(p_val, 'lon', p_val.get('lon', p_val.get('longitude', 0.0)))
            raw_aspect = _calculate_fallback_drishti_ray(planet, float(p_lon), bhava_madhya_lon)

        if raw_aspect <= 0.0:
            continue

        p_val = planet_positions[planet]
        if isinstance(p_val, (int, float)):
            p_lon_deg = float(p_val) % 360.0
        elif isinstance(p_val, dict):
            p_lon_deg = float(p_val.get("lon", p_val.get("longitude", 0.0))) % 360.0
        else:
            p_lon_deg = float(getattr(p_val, 'lon', getattr(p_val, 'longitude', 0.0))) % 360.0

        p_sign = SIGNS[int(p_lon_deg / 30.0)]
        is_debilitated = (DEBILITATION_SIGNS.get(planet) == p_sign)
        
        c_status = combustion_map.get(planet, False)
        if isinstance(c_status, dict):
            is_combust = bool(c_status.get("is_combust", False))
        else:
            is_combust = bool(c_status)

        # 1. House Lord Aspect (DPK 15.1-3 / BPHS Ch. 27)
        if target_house_lord and planet == target_house_lord:
            if is_combust or is_debilitated:
                net_drishti += (raw_aspect * 0.25)
            else:
                net_drishti += raw_aspect
        # 2. Malefic Aspect
        elif planet in malefics:
            net_drishti -= (raw_aspect / 4.0)
        # 3. Standard Benefic Aspect
        else:
            if planet in ["Jupiter", "Mercury"]:
                net_drishti += (raw_aspect if not (is_combust or is_debilitated) else raw_aspect / 2.0)
            else:
                net_drishti += (raw_aspect / 4.0)

    return round(net_drishti, 2)


def _evaluate_occupants(
    house_num: int, 
    occupants: List[Dict[str, Any]], 
    is_moon_benefic: bool = True, 
    is_mercury_malefic: bool = False,
    house_lord: str = "",
    lagna_lord: Optional[str] = None
) -> Dict[str, Any]:
    """
    Evaluates occupants. 
    - Filters out non-planetary bodies (Lagna, MC, etc.).
    - DPK 15.1: Malefics in their own sign act as protective lords.
    - DPK 15.9: Lagnesha presence causes the house to flourish.
    """
    is_upacaya = house_num in UPACAYA_HOUSES
    benefics_here = []
    malefics_here = []
    lagnesha_present = False

    for occ in occupants:
        p = occ["name"]
        if p not in VALID_PLANETS:
            continue

        if lagna_lord and p == lagna_lord:
            lagnesha_present = True

        is_malefic_nature = (
            p in ["Sun", "Mars", "Saturn", "Rahu", "Ketu"]
            or (p == "Moon" and not is_moon_benefic)
            or (p == "Mercury" and is_mercury_malefic)
        )

        # Malefic in own sign acts as a supportive ruler (DPK 15.1).
        # In Upacayas (3, 6, 11), its malefic drive empowers growth and vanquishes enemies (Śatruhantā).
        if house_lord and p == house_lord:
            benefics_here.append(p)
            if is_malefic_nature and is_upacaya:
                malefics_here.append(p)
            continue

        if is_malefic_nature:
            malefics_here.append(p)
        else:
            benefics_here.append(p)

    upacaya_empowered = is_upacaya and len(malefics_here) > 0 and house_num in {3, 6, 11}

    return {
        "benefics": benefics_here,
        "malefics": malefics_here,
        "is_upacaya": is_upacaya,
        "upacaya_empowered": upacaya_empowered,
        "satruhanta_active": upacaya_empowered and house_num == 6,
        "lagnesha_present": lagnesha_present
    }


def _evaluate_sandhi_leakage(
    house_num: int,
    cusp_lon: float,
    occupants: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Detects Bhāva Sandhi border weakness and cross-border wall leakage."""
    deg_in_sign = cusp_lon % 30.0
    cusp_in_sandhi = (deg_in_sign < 1.0) or (deg_in_sign > 29.0)
    cusp_dist_to_border = min(deg_in_sign, 30.0 - deg_in_sign)

    leakages = []
    for occ in occupants:
        p_name = occ["name"]
        if p_name not in VALID_PLANETS:
            continue
        p_deg = float(occ.get("deg_in_sign", occ.get("lon", 0.0) % 30.0))
        p_lon = float(occ.get("lon", p_deg))
        
        if p_deg < 1.0:
            target_house = 12 if house_num == 1 else house_num - 1
            leakages.append({
                "planet": p_name,
                "lon": p_lon,
                "deg_in_sign": round(p_deg, 3),
                "leakage_direction": "backward",
                "target_house": target_house,
                "leakage_ratio": round((1.0 - p_deg) / 1.0, 3)
            })
        elif p_deg > 29.0:
            target_house = 1 if house_num == 12 else house_num + 1
            leakages.append({
                "planet": p_name,
                "lon": p_lon,
                "deg_in_sign": round(p_deg, 3),
                "leakage_direction": "forward",
                "target_house": target_house,
                "leakage_ratio": round((p_deg - 29.0) / 1.0, 3)
            })

    return {
        "cusp_in_sandhi": cusp_in_sandhi,
        "cusp_dist_to_border": round(cusp_dist_to_border, 2),
        "wall_leakages": leakages
    }


def _evaluate_kartari_yoga(
    house_num: int, 
    house_occupant_map: Dict[int, List[Dict[str, Any]]],
    is_moon_benefic: bool,
    is_mercury_malefic: bool
) -> Dict[str, Any]:
    """Identifies Śubhakartarī or Pāpakartarī yogas hemmed around the house."""
    h_12 = 12 if house_num == 1 else house_num - 1
    h_2 = 1 if house_num == 12 else house_num + 1

    def classify_planets(planets: List[Dict[str, Any]]) -> Tuple[List[str], List[str]]:
        ben, mal = [], []
        for pl in planets:
            name = pl["name"]
            if name not in VALID_PLANETS:
                continue
            if name in ["Sun", "Mars", "Saturn", "Rahu", "Ketu"]:
                mal.append(name)
            elif name == "Moon":
                (ben if is_moon_benefic else mal).append(name)
            elif name == "Mercury":
                (mal if is_mercury_malefic else ben).append(name)
            else:
                ben.append(name)
        return ben, mal

    b12, m12 = classify_planets(house_occupant_map.get(h_12, []))
    b2, m2 = classify_planets(house_occupant_map.get(h_2, []))

    yoga_type = "neutral"
    if len(m12) > 0 and len(m2) > 0 and len(b12) == 0 and len(b2) == 0:
        yoga_type = "papakartari"
    elif len(b12) > 0 and len(b2) > 0 and len(m12) == 0 and len(m2) == 0:
        yoga_type = "shubhakartari"
    elif (len(m12) > 0 and len(m2) > 0) or (len(b12) > 0 and len(b2) > 0):
        yoga_type = "mixed"

    return {
        "type": yoga_type,
        "flanking_12th": {"benefics": b12, "malefics": m12},
        "flanking_2nd": {"benefics": b2, "malefics": m2}
    }


def _evaluate_karako_bhava_nasaya(
    house_num: int, 
    occupants: List[Dict[str, Any]],
    sign_name: str = ""
) -> Dict[str, Any]:
    """
    Checks Kārakobhāvanāśāya strictly for Living Significations (Jīva-Kārakas).
    Enforces classical exceptions:
    - Saturn in the 8th protects longevity (Āyuṣkāraka).
    - DPK 16.1–3: A kāraka in its own sign or exaltation sign is exempted.
    """
    LIVING_KARAKAS: Dict[int, str] = {
        3: "Mars",     # Younger siblings
        5: "Jupiter",  # Progeny
        7: "Venus",    # Spouse
        9: "Sun",      # Father
    }
    target_karaka = LIVING_KARAKAS.get(house_num)
    occ_names = [o["name"] for o in occupants if o.get("name") in VALID_PLANETS]
    
    afflicted = False
    details = "Harmonious"

    if house_num == 8 and len(occ_names) == 1 and occ_names[0] == "Saturn":
        afflicted = False
        details = "Saturn in 8th house exception: Promotes longevity (Āyuṣkāraka)."
    elif target_karaka and len(occ_names) == 1 and occ_names[0] == target_karaka:
        is_own_sign = (SIGN_LORDS.get(sign_name) == target_karaka) if sign_name else False
        is_exalted = (EXALTATION_SIGNS.get(target_karaka) == sign_name) if sign_name else False
        if is_own_sign or is_exalted:
            afflicted = False
            details = (
                f"Kārakobhāvanāśāya exempted (DPK 16.1–3): Solitary {target_karaka} "
                f"is fortified in {'own sign' if is_own_sign else 'exaltation'} ({sign_name}) in Bhāva {house_num}."
            )
        else:
            afflicted = True
            details = f"Kārakobhāvanāśāya triggered: Solitary {target_karaka} in living Bhāva {house_num}."

    return {
        "primary_karakas": BHAVA_KARAKAS.get(house_num, []),
        "is_afflicted": afflicted,
        "details": details
    }


def _evaluate_dpk_triad(
    house_num: int,
    asc_sign_idx: int,
    chandra_sign_idx: int,
    planet_positions: Dict[str, float],
    shadbala_results: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Triangulates house through Phaladeepika Ch. 15 Text 6 Triad:
    Weights: Janma Lagna (1.0), Chandra Lagna (0.5), Kāraka Lagna (0.25).
    Normalized by 1.75 total weight.
    """
    primary_karakas = BHAVA_KARAKAS.get(house_num, ["Jupiter"])
    main_karaka = primary_karakas[0]

    h_asc_sign = (asc_sign_idx + house_num - 1) % 12
    lord_asc = SIGN_LORDS[SIGNS[h_asc_sign]]
    
    h_chandra_sign = (chandra_sign_idx + house_num - 1) % 12
    lord_chandra = SIGN_LORDS[SIGNS[h_chandra_sign]]
    
    if main_karaka in planet_positions:
        k_val = planet_positions[main_karaka]
        karaka_lon = float(k_val if isinstance(k_val, (int, float)) else getattr(k_val, 'lon', k_val.get('lon', 0.0)))
        karaka_sign_idx = int(karaka_lon / 30.0)
        h_karaka_sign = (karaka_sign_idx + house_num - 1) % 12
    else:
        karaka_sign_idx = asc_sign_idx
        h_karaka_sign = h_asc_sign
    lord_karaka = SIGN_LORDS[SIGNS[h_karaka_sign]]

    def get_lord_potency(lrd: str) -> float:
        virupas = float(shadbala_results.get(lrd, {}).get("Total_Virupas", 0.0))
        req = PLANET_REQUIRED_VIRUPAS.get(lrd, 360.0)
        return virupas / req

    p_asc = get_lord_potency(lord_asc)
    p_chandra = get_lord_potency(lord_chandra)
    
    # DPK 15.6: Evaluate both Kāraka Lagna dispositor AND Kāraka planet itself
    p_karaka_house_lord = get_lord_potency(lord_karaka)
    p_karaka_graha = get_lord_potency(main_karaka)
    p_karaka = round((p_karaka_house_lord + p_karaka_graha) / 2.0, 2)

    composite_potency = ((1.0 * p_asc) + (0.5 * p_chandra) + (0.25 * p_karaka)) / 1.75
    strong_count = sum(1 for p in (p_asc, p_chandra, p_karaka) if p >= 1.0)

    concordance = "partial"
    if strong_count == 3:
        concordance = "exceptional"
    elif strong_count == 2:
        concordance = "strong"
    elif strong_count == 0:
        concordance = "latent"

    return {
        "from_janma_lagna": {"house": house_num, "sign": SIGNS[h_asc_sign], "lord": lord_asc, "potency_ratio": round(p_asc, 2)},
        "from_chandra_lagna": {"house": house_num, "sign": SIGNS[h_chandra_sign], "lord": lord_chandra, "potency_ratio": round(p_chandra, 2)},
        "from_karaka_lagna": {
            "house": house_num,
            "sign": SIGNS[h_karaka_sign],
            "lord": lord_karaka,
            "karaka": main_karaka,
            "potency_ratio": round(p_karaka, 2),
            "dispositor_potency": round(p_karaka_house_lord, 2),
            "karaka_graha_potency": round(p_karaka_graha, 2)
        },
        "concordance": concordance,
        "concordance_score": round(strong_count / 3.0, 2),
        "weighted_triad_potency": round(composite_potency, 2)
    }


def _evaluate_three_focal_points(
    house_num: int,
    lord: str,
    lord_house: int,
    main_karaka: str,
    planet_positions: Dict[str, float],
    asc_sign_idx: int,
    house_occupant_map: Dict[int, List[Dict[str, Any]]],
    shadbala_results: Dict[str, Any],
    combustion_map: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Evaluates the 3 Essential Focal Points per Phaladeepika Ch. 15 (Texts 1-3, 18):
    1. The Bhāva: Afflicted if strictly besieged (Pāpakartarī without benefic relief)
       or occupied by >=2 malefics (excluding lord). Dusthāna houses (6, 8, 12) are not self-ruining.
    2. The Lord: Afflicted if placed in 6, 8, 12 from Bhāva (except own-dusthana/Viparita),
       besieged, depleted in Shadbala (<0.90), debilitated (Hīna), or combust (Mūḍha).
    3. The Kāraka: Afflicted if placed in dusthāna from Lagna (except Saturn in 8th),
       besieged, depleted in Shadbala (<0.90), debilitated, or combust.
    """
    combustion_map = combustion_map or {}

    def is_strictly_papakartari(h: int) -> bool:
        h12 = 12 if h == 1 else h - 1
        h2 = 1 if h == 12 else h + 1
        occ12 = house_occupant_map.get(h12, [])
        occ2 = house_occupant_map.get(h2, [])
        m12 = [p["name"] for p in occ12 if p["name"] in NATURAL_MALEFICS]
        m2 = [p["name"] for p in occ2 if p["name"] in NATURAL_MALEFICS]
        b12 = [p["name"] for p in occ12 if p["name"] in NATURAL_BENEFICS]
        b2 = [p["name"] for p in occ2 if p["name"] in NATURAL_BENEFICS]
        # Pure Papakartari requires malefics on both flanks AND no benefics on either flank
        return len(m12) > 0 and len(m2) > 0 and len(b12) == 0 and len(b2) == 0

    # Focal Point 1: Bhāva Affliction (Houses 6, 8, 12 are NOT inherently ruined)
    bhava_malefics = [
        p["name"] for p in house_occupant_map.get(house_num, [])
        if p["name"] in NATURAL_MALEFICS and p["name"] != lord
    ]
    bhava_afflicted = is_strictly_papakartari(house_num) or (len(bhava_malefics) >= 2)

    # Own dusthāna lords in dusthānas (Harsha, Sarala, Vimala) are exempt from displacement ruin
    bhavat_dist = ((lord_house - house_num) % 12) + 1
    lord_in_bhava_dusthana = (
        (bhavat_dist in {6, 8, 12}) 
        and not (house_num in DUHSTHANA_HOUSES and lord_house in DUHSTHANA_HOUSES)
    )
    lord_virupas = float(shadbala_results.get(lord, {}).get("Total_Virupas", 0.0))
    lord_weak = (lord_virupas / PLANET_REQUIRED_VIRUPAS.get(lord, 360.0)) < 0.90 if lord in shadbala_results else False

    if lord in planet_positions:
        l_lon = float(planet_positions[lord]) % 360.0
        l_sign = SIGNS[int(l_lon / 30.0)]
    else:
        l_sign = SIGNS[(asc_sign_idx + lord_house - 1) % 12]
    lord_debilitated = (DEBILITATION_SIGNS.get(lord) == l_sign)

    c_status = combustion_map.get(lord, False)
    lord_combust = bool(c_status.get("is_combust", False)) if isinstance(c_status, dict) else bool(c_status)

    lord_afflicted = (
        lord_in_bhava_dusthana 
        or is_strictly_papakartari(lord_house) 
        or lord_weak 
        or lord_debilitated 
        or lord_combust
    )

    # Focal Point 3: Kāraka Affliction (Safe lookup without defaulting to 0.0 Aries)
    if main_karaka in planet_positions:
        k_val = planet_positions[main_karaka]
        karaka_lon = float(k_val if isinstance(k_val, (int, float)) else getattr(k_val, 'lon', k_val.get('lon', 0.0))) % 360.0
        karaka_sign_idx = int(karaka_lon / 30.0)
        karaka_sign = SIGNS[karaka_sign_idx]
        karaka_house = (karaka_sign_idx - asc_sign_idx) % 12 + 1
        karaka_dusthana = (karaka_house in DUHSTHANA_HOUSES) and not (house_num == 8 and main_karaka == "Saturn")
        karaka_flanked = is_strictly_papakartari(karaka_house)
        karaka_debilitated = (DEBILITATION_SIGNS.get(main_karaka) == karaka_sign)
        c_k_status = combustion_map.get(main_karaka, False)
        karaka_combust = bool(c_k_status.get("is_combust", False)) if isinstance(c_k_status, dict) else bool(c_k_status)
    else:
        karaka_house = None
        karaka_dusthana = False
        karaka_flanked = False
        karaka_debilitated = False
        karaka_combust = False

    karaka_virupas = float(shadbala_results.get(main_karaka, {}).get("Total_Virupas", 0.0))
    karaka_weak = (karaka_virupas / PLANET_REQUIRED_VIRUPAS.get(main_karaka, 360.0)) < 0.90 if main_karaka in shadbala_results else False
    karaka_afflicted = (
        karaka_dusthana 
        or karaka_flanked 
        or karaka_weak 
        or karaka_debilitated 
        or karaka_combust
    )

    afflictions = sum([bhava_afflicted, lord_afflicted, karaka_afflicted])
    return {
        "afflicted_points_count": afflictions,
        "is_ruined": afflictions >= 2,
        "details": f"{afflictions} of 3 focal points afflicted (Bhāva: {bhava_afflicted}, Lord: {lord_afflicted}, Kāraka: {karaka_afflicted})."
    }


def calculate_bhava_bala(
    baseline: Any,
    shadbala_results: Dict[str, Any],
    aspect_matrices: Optional[Dict[str, Any]] = None,
    house_system: str = "whole_sign",
    **kwargs
) -> Dict[int, Any]:
    """
    Synthesizes complete 12-House Bhāva Bala and Phaladeepika diagnostics.
    Supports both Modern ChartBaseline pipeline and Legacy Calling parity.
    """
    # ---------------------------------------------------------
    # 1. Pipeline Normalization
    # ---------------------------------------------------------
    planet_positions: Dict[str, float] = {}
    planet_metadata: Dict[str, Dict[str, Any]] = {}
    ascendant_lon = 0.0
    sensitive_cusp_degree = 0.0
    bhava_madhyas: List[float] = []
    is_day_birth = True

    if isinstance(baseline, (list, tuple)):
        bhava_madhyas = [float(x) % 360.0 for x in baseline]
        ascendant_lon = bhava_madhyas[0] if bhava_madhyas else 0.0
        sensitive_cusp_degree = ascendant_lon % 30.0
        p_dict = None
        if isinstance(aspect_matrices, dict) and ("Sun" in aspect_matrices or "planets" in aspect_matrices):
            p_dict = aspect_matrices
            aspect_matrices = None
        elif "planet_positions" in kwargs:
            p_dict = kwargs["planet_positions"]
        if p_dict:
            for p, pos in p_dict.items():
                if p not in VALID_PLANETS and p not in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
                    continue
                lon_val = pos if isinstance(pos, (int, float)) else getattr(pos, 'lon', pos.get('lon', pos.get('longitude', 0.0)))
                p_lon = float(lon_val) % 360.0
                planet_positions[p] = p_lon
                planet_metadata[p] = {"lon": p_lon, "is_combust": False, "in_war": False}
    else:
        anchors = getattr(baseline, "astronomical_anchors", {})
        ascendant_lon = float(anchors.get("asc_longitude", anchors.get("ascendant", anchors.get("ascendant_lon", 0.0)))) % 360.0
        sensitive_cusp_degree = float(anchors.get("sensitive_cusp_degree", ascendant_lon % 30.0))
        is_day_birth = bool(anchors.get("is_day_birth", True))

        if house_system == "whole_sign":
            asc_sign_idx = int(ascendant_lon / 30.0)
            bhava_madhyas = [
                ((asc_sign_idx + h) % 12 * 30.0 + sensitive_cusp_degree) % 360.0
                for h in range(12)
            ]
        else:
            cusps = anchors.get("raw_campanus_cusps") or anchors.get("cusps") or getattr(baseline, "houses", [])
            bhava_madhyas = [float(c) % 360.0 for c in cusps] if len(cusps) == 12 else [
                (ascendant_lon + h * 30.0) % 360.0 for h in range(12)
            ]

        planets_data = getattr(baseline, "planets", getattr(baseline, "coordinates", {}))
        combustion_map = getattr(baseline, "combustion_status", {})
        for p, p_data in planets_data.items():
            if p not in VALID_PLANETS and p not in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
                continue
            if isinstance(p_data, (int, float)):
                p_lon = float(p_data) % 360.0
                planet_positions[p] = p_lon
                planet_metadata[p] = {"lon": p_lon, "is_combust": False, "in_war": False}
            else:
                p_lon = float(getattr(p_data, 'lon', p_data.get('lon', p_data.get('longitude', 0.0)))) % 360.0
                planet_positions[p] = p_lon
                is_combust = bool(getattr(p_data, 'is_combust', p_data.get('is_combust', False)))
                if not is_combust and isinstance(combustion_map, dict):
                    c_entry = combustion_map.get(p, {})
                    is_combust = bool(c_entry.get("is_combust", False)) if isinstance(c_entry, dict) else bool(c_entry)
                planet_metadata[p] = {
                    "lon": p_lon,
                    "is_combust": is_combust,
                    "in_war": bool(getattr(p_data, 'in_war', p_data.get('in_war', False))),
                    "speed": float(getattr(p_data, 'speed', p_data.get('speed', 1.0)))
                }

    # ---------------------------------------------------------
    # 2. Beneficence Calibration
    # ---------------------------------------------------------
    moon_paksha = shadbala_results.get("Moon", {}).get("Paksha_Bala", 30.0)
    is_moon_benefic = moon_paksha >= 30.0

    sun_lon = planet_positions.get("Sun", 0.0)
    merc_lon = planet_positions.get("Mercury", 0.0)
    merc_dist = abs(merc_lon - sun_lon) % 360.0
    if merc_dist > 180.0:
        merc_dist = 360.0 - merc_dist
    is_mercury_malefic = merc_dist < 14.0 or planet_metadata.get("Mercury", {}).get("is_combust", False)

    asc_sign_idx = int(ascendant_lon / 30.0)
    lagna_sign_name = SIGNS[asc_sign_idx]
    lagna_lord = SIGN_LORDS[lagna_sign_name]
    chandra_sign_idx = int(planet_positions.get("Moon", ascendant_lon) / 30.0)

    # Build combustion dictionary
    is_combust_map = {p: meta.get("is_combust", False) for p, meta in planet_metadata.items()}
    if "combustion_map" in kwargs and isinstance(kwargs["combustion_map"], dict):
        is_combust_map.update(kwargs["combustion_map"])

    # ---------------------------------------------------------
    # 3. Map Occupants to Whole Sign Houses (FILTER NON-PLANETARY BODIES)
    # ---------------------------------------------------------
    house_occupant_map: Dict[int, List[Dict[str, Any]]] = {h: [] for h in range(1, 13)}
    for p_name, p_lon in planet_positions.items():
        if p_name not in VALID_PLANETS:
            continue
        p_sign_idx = int(p_lon / 30.0)
        h_idx = (p_sign_idx - asc_sign_idx) % 12 + 1
        house_occupant_map[h_idx].append({
            "name": p_name,
            "lon": round(p_lon, 3),
            "deg_in_sign": round(p_lon % 30.0, 3)
        })

    # ---------------------------------------------------------
    # 4. Synthesize 12 Houses
    # ---------------------------------------------------------
    bhava_results: Dict[int, Any] = {}

    for i in range(12):
        house_num = i + 1
        cusp_lon = bhava_madhyas[i] % 360.0
        sign_idx = int(cusp_lon / 30.0)
        sign_name = SIGNS[sign_idx]
        deg_in_sign = cusp_lon % 30.0
        genus = get_sign_genus(sign_name, deg_in_sign)
        lord = SIGN_LORDS[sign_name]
        primary_karakas = BHAVA_KARAKAS.get(house_num, ["Jupiter"])
        main_karaka = primary_karakas[0]

        # Quantitative Pillar 1: Bhavādhipati Bala
        adhipathi_bala = float(shadbala_results.get(lord, {}).get("Total_Virupas", 0.0))

        # Quantitative Pillar 2: Bhava Digbala
        dig_bala = calculate_bhava_dig_bala(house_num, cusp_lon)

        # Quantitative Pillar 3: Bhava Dṛṣṭi Bala (Lord & Lagnesha protection enabled, combustion mitigated)
        drishti_bala = calculate_bhava_drishti_bala(
            cusp_lon,
            planet_positions,
            aspect_matrices=aspect_matrices,
            house_num=house_num,
            target_house_lord=lord,
            is_moon_benefic=is_moon_benefic,
            is_mercury_malefic=is_mercury_malefic,
            lagna_lord=lagna_lord,
            combustion_map=is_combust_map
        )

        # Phaladeepika Ch. 4 Modifiers
        # 1. Lord's Directional Strength counted again
        lord_dig_bala = float(shadbala_results.get(lord, {}).get("Dig_Bala", 0.0))
        
        # 2. Gender vs Diurnal Sect (+15 Virūpas)
        is_odd_sign = (sign_idx % 2 == 0)
        sect_bonus = 15.0 if (is_day_birth and is_odd_sign) or (not is_day_birth and not is_odd_sign) else 0.0

        # Total Virūpas (3 Classical Pillars)
        total_virupas = round(adhipathi_bala + dig_bala + drishti_bala, 2)
        total_rupas = round(total_virupas / 60.0, 2)

        # Augmented Virūpas (Phaladeepika Ch. 4 additions)
        augmented_virupas = round(total_virupas + lord_dig_bala + sect_bonus, 2)

        # Qualitative Diagnostic 1: Occupants & Upacaya Dynamics (with DPK 15.1 and 15.9 compliance)
        occupants = house_occupant_map.get(house_num, [])
        occ_diag = _evaluate_occupants(
            house_num=house_num,
            occupants=occupants,
            is_moon_benefic=is_moon_benefic,
            is_mercury_malefic=is_mercury_malefic,
            house_lord=lord,
            lagna_lord=lagna_lord
        )

        # Qualitative Diagnostic 2: Sandhi & Cross-Border Leakage
        sandhi_diag = _evaluate_sandhi_leakage(house_num, cusp_lon, occupants)

        # Qualitative Diagnostic 3: Kartarī Yogas
        kartari_diag = _evaluate_kartari_yoga(
            house_num, house_occupant_map, is_moon_benefic, is_mercury_malefic
        )

        # Qualitative Diagnostic 4: Lord Displacement & Bhavāt Bhavam
        if lord in planet_positions:
            lord_lon = float(planet_positions[lord])
            lord_sign_idx = int(lord_lon / 30.0)
            lord_house = (lord_sign_idx - asc_sign_idx) % 12 + 1
            lord_sign = SIGNS[lord_sign_idx]
        else:
            lord_sign_idx = sign_idx
            lord_house = house_num
            lord_sign = sign_name

        bhavat_dist = (lord_house - house_num) % 12 + 1
        lord_meta = planet_metadata.get(lord, {})
        req_virupas = PLANET_REQUIRED_VIRUPAS.get(lord, 360.0)
        
        # DPK 15.1: Lord cannot be classified as strong if debilitated (Hīna) or combust (Mūḍha)
        is_lord_debilitated = (DEBILITATION_SIGNS.get(lord) == lord_sign)
        is_lord_combust = bool(lord_meta.get("is_combust", is_combust_map.get(lord, False)))
        is_lord_strong = (
            ((adhipathi_bala / req_virupas) >= 1.0) 
            and not is_lord_debilitated 
            and not is_lord_combust
        )

        # Upacayas from the bhāva that foster growth without dusthāna corruption: 3, 10, 11
        lord_in_upacaya_from_bhava = bhavat_dist in {3, 10, 11}
        is_lord_displaced_in_dusthana = (lord_house in DUHSTHANA_HOUSES) and not (house_num in DUHSTHANA_HOUSES)
        lord_in_upacaya_from_lagna = lord_house in UPACAYA_HOUSES

        lord_status = {
            "lord": lord,
            "placed_house": lord_house,
            "placed_sign": lord_sign,
            "bhavat_bhavam_distance": bhavat_dist,
            "is_in_kendra": lord_house in KENDRA_HOUSES,
            "is_in_trikona": lord_house in TRIKONA_HOUSES,
            "is_in_dusthana": is_lord_displaced_in_dusthana,
            "is_in_upacaya_from_bhava": lord_in_upacaya_from_bhava,
            "is_in_upacaya_from_lagna": lord_in_upacaya_from_lagna,
            "is_debilitated": is_lord_debilitated,
            "is_combust": is_lord_combust,
            "in_war": lord_meta.get("in_war", False),
            "is_strong": is_lord_strong,
            "potency_ratio": round(adhipathi_bala / req_virupas, 2)
        }

        # Qualitative Diagnostic 5: Kārakobhāvanāśāya (strictly Jīva-Kārakas, exempted in own/exaltation sign)
        karaka_diag = _evaluate_karako_bhava_nasaya(house_num, occupants, sign_name=sign_name)

        # Qualitative Diagnostic 6: Phaladeepika Triad Triangulation
        triad_diag = _evaluate_dpk_triad(
            house_num, asc_sign_idx, chandra_sign_idx, planet_positions, shadbala_results
        )

        # Qualitative Diagnostic 7: 3 Focal Points Rule (DPK Ch. 15 Texts 1-3, 18)
        focal_diag = _evaluate_three_focal_points(
            house_num, lord, lord_house, main_karaka, planet_positions,
            asc_sign_idx, house_occupant_map, shadbala_results,
            combustion_map=is_combust_map
        )

        # Check if Lagnesha aspects cusp (for DPK 15.9 Flourishing rule)
        lagna_lord_lon = planet_positions.get(lagna_lord)
        lagnesha_aspects = False
        if lagna_lord_lon is not None and not occ_diag.get("lagnesha_present", False):
            cusp_drishti_matrix = aspect_matrices.get("cusp_drishti", aspect_matrices) if isinstance(aspect_matrices, dict) else None
            raw_lagna_aspect = None
            if cusp_drishti_matrix:
                raw_lagna_aspect = _extract_cusp_drishti(cusp_drishti_matrix, lagna_lord, house_num)
            if raw_lagna_aspect is None:
                raw_lagna_aspect = _calculate_fallback_drishti_ray(lagna_lord, float(lagna_lord_lon), cusp_lon)
            # Require a palpable aspect ray (>= 30.0 Virūpas, i.e., at least half-glance per classical Jyotiṣa)
            if raw_lagna_aspect and raw_lagna_aspect >= 30.0:
                lagnesha_aspects = True

        bhava_results[house_num] = {
            # Legacy Parāśarī contract
            "house": house_num,
            "lord": lord,
            "bhava_madhya": round(cusp_lon, 2),
            "bhavadhipathi_bala": adhipathi_bala,
            "bhava_digbala": dig_bala,
            "bhava_drishti_bala": drishti_bala,
            "total_virupas": total_virupas,
            "total_rupas": total_rupas,
            
            # Phaladeepika Extensions
            "augmented_virupas": augmented_virupas,
            "lord_dig_bala_bonus": lord_dig_bala,
            "sect_bonus": sect_bonus,
            "sign": sign_name,
            "sign_genus": genus,
            "occupants": occupants,
            "occupant_diagnostics": occ_diag,
            "sandhi_analysis": sandhi_diag,
            "kartari_yoga": kartari_diag,
            "lord_status": lord_status,
            "karaka_analysis": karaka_diag,
            "dpk_triad": triad_diag,
            "three_focal_points": focal_diag,
            "lagnesha_aspecting": lagnesha_aspects,
            "classification": "Pending",
            "summary_verdict": ""
        }

    # ---------------------------------------------------------
    # 5. Synthesize Harsha Bala & House Atmosphere Model
    # ---------------------------------------------------------
    harsha_data = calculate_harsha_bala(
        baseline=baseline,
        planet_positions=planet_positions,
        ascendant_lon=ascendant_lon,
        is_day_birth=is_day_birth
    )
    atmosphere_data = calculate_house_atmosphere(
        baseline=baseline,
        bhava_results=bhava_results,
        harsha_data=harsha_data,
        aspect_matrices=aspect_matrices
    )

    for h in range(1, 13):
        atm = atmosphere_data.get(h, {})
        bhava_results[h]["harsha_bala"] = harsha_data["dusthana_joy"].get(h, {})
        bhava_results[h]["atmosphere"] = atm
        
        # Single Source of Truth: Synchronize root classification with Atmosphere
        raw_class = atm.get("classification", "Miśra")
        clean_class = raw_class.split()[0]  # Extracts "Puṣṭa", "Miśra", or "Hīna"
        bhava_results[h]["classification"] = clean_class
        bhava_results[h]["summary_verdict"] = (
            f"House {h} ({bhava_results[h]['sign']}) is {clean_class}: "
            f"{bhava_results[h]['total_rupas']} Rūpas (Atmosphere: {atm.get('net_atmosphere_score', 0.0):+.1f}, "
            f"{atm.get('environmental_weather', 'Balanced')}). "
            f"Lord {bhava_results[h]['lord']} in H{bhava_results[h]['lord_status']['placed_house']}."
        )

    return bhava_results


# =============================================================================
# HARSHA BALA (P.V.R. Narasimha Rao Ch. 28.3 & Dusthana Joy Reversals)
# =============================================================================

def calculate_harsha_bala(
    baseline: Any,
    planet_positions: Optional[Dict[str, float]] = None,
    ascendant_lon: Optional[float] = None,
    is_day_birth: Optional[bool] = None
) -> Dict[str, Any]:
    """
    Calculates Harsha Bala (Strength of Cheerfulness) per P.V.R. Narasimha Rao
    (Vedic Astrology: An Integrated Approach Ch. 28.3) and classical Parāśarī texts.

    Evaluated across 4 sources of strength for 7 planets (each gives 5 units, max 20 units):
    1. Sthāna / Joy House (Bhavana Bala):
       Sun in 9th, Moon in 3rd, Mars in 6th, Mercury in 1st, Jupiter in 11th, Venus in 5th, Saturn in 12th.
    2. Uccha / Sva Kṣetra (Exaltation or Own Sign):
       Planet in exaltation or own sign.
    3. Strī / Puruṣa Bhāva (Gender & House Match):
       Feminine planets (Moon, Mercury, Venus, Saturn) in houses 1, 2, 3, 7, 8, 9.
       Masculine planets (Sun, Mars, Jupiter) in houses 4, 5, 6, 10, 11, 12.
    4. Dina / Rātri Bala (Diurnal / Nocturnal Sect Match):
       Day birth: masculine planets (Sun, Mars, Jupiter) get 5 units.
       Night birth: feminine planets (Moon, Mercury, Venus, Saturn) get 5 units.

    Also evaluates dusthana joy (Houses 6, 8, 12) disentangling canonical Viparīta Yogas
    (DPK 6.57-70) from Tajika planetary joy:
    - House 6: Harsha Yoga (6th lord in 6th) and Mars joy in 6th.
    - House 8: Sarala Yoga (8th lord in 8th).
    - House 12: Vimala Yoga (12th lord in 12th) and Saturn joy in 12th.
    """
    if planet_positions is None or ascendant_lon is None or is_day_birth is None:
        anchors = getattr(baseline, "astronomical_anchors", {})
        asc_val = anchors.get("asc_longitude", anchors.get("ascendant", 0.0))
        ascendant_lon = float(asc_val) % 360.0
        is_day_birth = bool(anchors.get("is_day_birth", True))

        coords = getattr(baseline, "coordinates", getattr(baseline, "planets", {}))
        planet_positions = {}
        for p, p_data in coords.items():
            if p not in VALID_PLANETS and p not in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
                continue
            if isinstance(p_data, (int, float)):
                planet_positions[p] = float(p_data) % 360.0
            elif isinstance(p_data, dict):
                planet_positions[p] = float(p_data.get("longitude", p_data.get("lon", 0.0))) % 360.0

    asc_sign_idx = int((ascendant_lon % 360.0) // 30)

    # 1. Planetary Harsha Bala (7 Planets)
    planets_harsha = {}
    for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
        p_lon = planet_positions.get(p, 0.0) % 360.0
        p_sign_idx = int(p_lon // 30)
        p_sign = SIGNS[p_sign_idx]
        h_num = (p_sign_idx - asc_sign_idx) % 12 + 1

        # Source 1: Sthana / Joy house (5 units)
        s1 = 5.0 if h_num == HARSHA_JOY_HOUSES.get(p) else 0.0

        # Source 2: Exaltation or Own sign (5 units)
        is_exalted = EXALTATION_SIGNS.get(p) == p_sign
        is_own = SIGN_LORDS.get(p_sign) == p
        s2 = 5.0 if (is_exalted or is_own) else 0.0

        # Source 3: Gender / House match (5 units)
        is_fem_p = p in FEMININE_PLANETS
        is_fem_h = h_num in FEMININE_HOUSES
        is_masc_p = p in MASCULINE_PLANETS
        is_masc_h = h_num in MASCULINE_HOUSES
        s3 = 5.0 if ((is_fem_p and is_fem_h) or (is_masc_p and is_masc_h)) else 0.0

        # Source 4: Diurnal / Nocturnal Sect (5 units)
        s4 = 5.0 if ((is_day_birth and is_masc_p) or (not is_day_birth and is_fem_p)) else 0.0

        total_units = s1 + s2 + s3 + s4
        if total_units >= 20.0:
            category = "Exceedingly Strong (Ati Bala)"
        elif total_units >= 15.0:
            category = "Fully Strong (Poorna Bala)"
        elif total_units >= 10.0:
            category = "Average Strength (Madhya Bala)"
        elif total_units >= 5.0:
            category = "Little Strength (Alpa Bala)"
        else:
            category = "No Strength (Nirbala)"

        planets_harsha[p] = {
            "planet": p,
            "placed_house": h_num,
            "placed_sign": p_sign,
            "sthana_bala_units": s1,
            "uccha_swakshetra_units": s2,
            "stree_purusha_units": s3,
            "dina_ratri_units": s4,
            "total_units": total_units,
            "max_units": 20.0,
            "strength_category": category,
            "is_in_joy_house": bool(s1 > 0)
        }

    # 2. Dusthana Harsha & Viparita Reversals (Houses 6, 8, 12)
    h6_sign = SIGNS[(asc_sign_idx + 5) % 12]
    h8_sign = SIGNS[(asc_sign_idx + 7) % 12]
    h12_sign = SIGNS[(asc_sign_idx + 11) % 12]

    l6 = SIGN_LORDS[h6_sign]
    l8 = SIGN_LORDS[h8_sign]
    l12 = SIGN_LORDS[h12_sign]

    def _get_planet_house(p_name: str) -> Optional[int]:
        if p_name not in planet_positions:
            return None
        p_val = planet_positions[p_name]
        if isinstance(p_val, (int, float)):
            p_deg = float(p_val) % 360.0
        elif isinstance(p_val, dict):
            p_deg = float(p_val.get("lon", p_val.get("longitude", 0.0))) % 360.0
        else:
            p_deg = float(getattr(p_val, 'lon', getattr(p_val, 'longitude', 0.0))) % 360.0
        return (int(p_deg // 30) - asc_sign_idx) % 12 + 1

    l6_h = _get_planet_house(l6)
    l8_h = _get_planet_house(l8)
    l12_h = _get_planet_house(l12)

    mars_h = _get_planet_house("Mars")
    saturn_h = _get_planet_house("Saturn")

    h6_harsha_yoga = (l6_h in DUHSTHANA_HOUSES) if l6_h is not None else False
    h6_mars_joy = (mars_h == 6) if mars_h is not None else False
    h6_active = h6_harsha_yoga or h6_mars_joy

    h8_sarala_yoga = (l8_h in DUHSTHANA_HOUSES) if l8_h is not None else False
    h8_active = h8_sarala_yoga

    h12_vimala_yoga = (l12_h in DUHSTHANA_HOUSES) if l12_h is not None else False
    h12_saturn_joy = (saturn_h == 12) if saturn_h is not None else False
    h12_active = h12_vimala_yoga or h12_saturn_joy

    dusthana_joy = {
        6: {
            "house": 6,
            "yoga_name": "Harsha",
            "is_active": h6_active,
            "lord_in_house": (l6_h == 6) if l6_h is not None else False,
            "viparita_active": h6_harsha_yoga,
            "karaka_joy_in_house": h6_mars_joy,
            "planetary_joy_active": h6_mars_joy,
            "bonus_units": 20.0 if h6_active else 0.0,
            "effect": (
                f"Harsha Yoga (6th lord {l6} in H{l6_h}): Immunity, overcoming competitors, turning debt and adversity into victory" if h6_harsha_yoga
                else ("Mars Joy in 6th: Śatruhantā courage and defeat of obstacles" if h6_mars_joy else "Standard Dusthana friction")
            )
        },
        8: {
            "house": 8,
            "yoga_name": "Sarala",
            "is_active": h8_active,
            "lord_in_house": (l8_h == 8) if l8_h is not None else False,
            "viparita_active": h8_sarala_yoga,
            "karaka_joy_in_house": False,
            "planetary_joy_active": False,
            "bonus_units": 20.0 if h8_active else 0.0,
            "effect": f"Sarala Yoga (8th lord {l8} in H{l8_h}): Fearlessness, longevity, endurance, sudden resilience under crisis" if h8_active else "Standard Dusthana vulnerability"
        },
        12: {
            "house": 12,
            "yoga_name": "Vimala",
            "is_active": h12_active,
            "lord_in_house": (l12_h == 12) if l12_h is not None else False,
            "viparita_active": h12_vimala_yoga,
            "karaka_joy_in_house": h12_saturn_joy,
            "planetary_joy_active": h12_saturn_joy,
            "bonus_units": 20.0 if h12_active else 0.0,
            "effect": (
                f"Vimala Yoga (12th lord {l12} in H{l12_h}): Spiritual independence, honorable expenditure, contentment, meditative release" if h12_vimala_yoga
                else ("Saturn Joy in 12th: Ascetic solitude and detachment" if h12_saturn_joy else "Standard Dusthana expenditure/loss")
            )
        }
    }

    return {
        "planets": planets_harsha,
        "dusthana_joy": dusthana_joy
    }


# =============================================================================
# HOUSE ATMOSPHERE & BASE SCORES (Unified Stage 3 Life-Department Weather)
# =============================================================================

def calculate_house_atmosphere(
    baseline: Any,
    bhava_results: Dict[int, Any],
    harsha_data: Optional[Dict[str, Any]] = None,
    aspect_matrices: Optional[Dict[str, Any]] = None
) -> Dict[int, Any]:
    """
    Computes synthesized House Atmosphere (-100 to +100).
    Properly incorporates:
    - Base Virūpas and DPK Ch. 4 Augmented bonuses (Lord Digbala, Sign/Sect match).
    - Neutralization of malefics in own sign.
    - DPK 15.9 Lagnesha protection/presence.
    - True Viparita reversals (Harsha, Sarala, Vimala) and planetary joy.
    """
    if harsha_data is None:
        harsha_data = calculate_harsha_bala(baseline)

    atmosphere_results: Dict[int, Any] = {}

    for h in range(1, 13):
        b = bhava_results.get(h, {})
        virupas = float(b.get("total_virupas", 360.0))
        augmented_virupas = float(b.get("augmented_virupas", virupas))
        lord = b.get("lord", "")
        sign = b.get("sign", "")
        lord_status = b.get("lord_status", {})
        occupants = b.get("occupants", [])
        sandhi = b.get("sandhi_analysis", {})
        kartari = b.get("kartari_yoga", {})
        occ_diag = b.get("occupant_diagnostics", {})
        karaka_diag = b.get("karaka_analysis", {})
        triad_diag = b.get("dpk_triad", {})
        focal_diag = b.get("three_focal_points", {})
        drishti_bala = float(b.get("bhava_drishti_bala", 0.0))
        h_harsha = harsha_data.get("dusthana_joy", {}).get(h, {})

        auspicious = []
        inauspicious = []
        score = 0.0

        # 1. Base Parashari Virupas + DPK Ch. 4 Augmentation
        v_diff = augmented_virupas - 360.0
        score += (v_diff * 0.15)
        if augmented_virupas >= 450.0:
            auspicious.append(f"Abundant Augmented Virūpas ({augmented_virupas:.1f}v / {augmented_virupas/60.0:.2f} Rūpas)")
        elif augmented_virupas < 320.0:
            inauspicious.append(f"Sub-baseline Virūpas ({augmented_virupas:.1f}v / {augmented_virupas/60.0:.2f} Rūpas)")

        # 2. Lord Capacity & Placements (DPK 15.1 Hīnāri-mūḍha)
        if lord_status.get("is_strong"):
            score += 15.0
            auspicious.append(f"Fortified Lord {lord} ({lord_status.get('potency_ratio', 1.0)}x required minimum)")
        else:
            score -= 10.0
            inauspicious.append(f"Lord {lord} below required minimum virūpas or deficient in dignity")

        if lord_status.get("is_debilitated"):
            score -= 20.0
            inauspicious.append(f"Lord {lord} debilitated in {lord_status.get('placed_sign')} (Hīna per DPK 15.1)")

        if lord_status.get("is_combust"):
            score -= 20.0
            inauspicious.append(f"Lord {lord} combust the Sun (Mūḍha per DPK 15.1)")

        if lord_status.get("in_war"):
            score -= 15.0
            inauspicious.append(f"Lord {lord} defeated in planetary war (Nīpīḍita)")

        # Bhavat Bhavam displacement vs Viparita
        placed_h = lord_status.get("placed_house", 1)
        bhavat_dist = lord_status.get("bhavat_bhavam_distance", 1)
        
        if h in DUHSTHANA_HOUSES and h_harsha.get("is_active"):
            score += 25.0
            if h_harsha.get("viparita_active"):
                auspicious.append(f"{h_harsha.get('yoga_name')} Yoga active in Dusthana H{h}")
            elif h_harsha.get("karaka_joy_in_house"):
                auspicious.append(f"Tajika Planetary Joy active in Dusthana H{h} ({'Mars' if h == 6 else 'Saturn'})")
            else:
                auspicious.append(f"{h_harsha.get('yoga_name')} Yoga active in Dusthana H{h}")
        elif (bhavat_dist in {6, 8, 12}) and (h not in DUHSTHANA_HOUSES):
            score -= 15.0
            inauspicious.append(f"Lord {lord} displaced into 6/8/12 from its own sign (+{bhavat_dist}h)")

        if lord_status.get("is_in_upacaya_from_bhava"):
            score += 10.0
            auspicious.append(f"Lord {lord} in Bhavāt Bhavam Upacaya (+{bhavat_dist}h)")

        if lord_status.get("is_in_upacaya_from_lagna") and not lord_status.get("is_in_dusthana"):
            score += 10.0
            auspicious.append(f"Lord {lord} in Lagna Upacaya H{placed_h} (DPK 4.23 growth)")

        # 3. Occupants & Lagneśa (with DPK 15.1 and 15.9 compliance)
        # Avoid double-counting Lagneśa in House 1 (already covered under 'resident in own sign')
        if occ_diag.get("lagnesha_present") and h != 1:
            score += 15.0
            auspicious.append("Lagnesha present in the house (DPK 15.9 flourishing)")
        elif b.get("lagnesha_aspecting"):
            score += 15.0
            auspicious.append("Lagnesha aspecting the house with major ray (DPK 15.9 flourishing)")

        for occ in occupants:
            p_name = occ.get("name")
            if p_name not in VALID_PLANETS:
                continue

            if p_name == lord:
                score += 15.0
                auspicious.append(f"House lord {p_name} resident in own sign {sign}")
            elif p_name in NATURAL_BENEFICS:
                score += 10.0
                auspicious.append(f"Benefic occupant {p_name} in sign {sign}")
            elif p_name in NATURAL_MALEFICS:
                if h in UPACAYA_HOUSES:
                    score += 10.0
                    auspicious.append(f"Constructive malefic {p_name} in Upacaya H{h}")
                else:
                    score -= 15.0
                    inauspicious.append(f"Malefic occupant {p_name} in non-upacaya H{h}")

        # 4. Aspect Rays
        if drishti_bala > 10.0:
            score += min(25.0, drishti_bala * 0.4)
            auspicious.append(f"Net supportive drishti ({drishti_bala:+.1f} Virūpas)")
        elif drishti_bala < -10.0:
            score -= min(25.0, abs(drishti_bala) * 0.4)
            inauspicious.append(f"Net confronting drishti ({drishti_bala:+.1f} Virūpas)")

        # 5. Kartarī Yoga
        if kartari.get("type") == "shubhakartari":
            score += 20.0
            auspicious.append("Śubhakartarī (house flanked by benefic planets)")
        elif kartari.get("type") == "papakartari":
            score -= 20.0
            inauspicious.append("Pāpakartarī (house besieged between malefic planets)")

        # 6. Sandhi Leakage
        if sandhi.get("cusp_in_sandhi"):
            score -= 15.0
            inauspicious.append("Bhāva Sandhi (cusp degree within 1° of sign border)")

        # 7. Kārakobhāvanāśāya Check (Living Significations)
        if karaka_diag.get("is_afflicted"):
            score -= 15.0
            inauspicious.append(karaka_diag.get("details", "Kārakobhāvanāśāya active"))

        # 8. Phaladeepika Triad Concordance (DPK 15.6)
        concordance = triad_diag.get("concordance")
        if concordance == "exceptional":
            score += 10.0
            auspicious.append("Exceptional Triad Concordance (Lagna, Moon, and Kāraka alignments strong)")
        elif concordance == "latent":
            score -= 10.0
            inauspicious.append("Latent Triad Concordance (all three Lagnas lack requisite strength)")

        # 9. Three Focal Points Ruination Verdict (DPK 15.18 Vad-Bhāva)
        if focal_diag.get("is_ruined"):
            score -= 25.0
            inauspicious.append(f"Vad-Bhāva Ruination (DPK 15.18): {focal_diag.get('details')}")

        net_score = round(max(-100.0, min(100.0, score)), 1)

        if net_score >= 25.0:
            classification = "Puṣṭa (Fortified / Flourishing)"
        elif net_score <= -20.0:
            classification = "Hīna (Deficient / Strained)"
        else:
            classification = "Miśra (Mixed / Dynamic)"

        if net_score >= 40.0:
            weather = "Radiant & Unopposed"
        elif net_score >= 20.0:
            weather = "Supportive & Productive"
        elif net_score >= 0.0:
            weather = "Tempered & Resilient"
        elif net_score >= -20.0:
            weather = "Frictional & Demanding"
        else:
            weather = "Turbulent & Obstructed"

        verdict = f"House {h} ({sign}) Atmosphere: {net_score:+.1f} ({weather}). {classification}."

        atmosphere_results[h] = {
            "house": h,
            "sign": sign,
            "lord": lord,
            "net_atmosphere_score": net_score,
            "base_virupas": virupas,
            "augmented_virupas": augmented_virupas,
            "classification": classification,
            "environmental_weather": weather,
            "auspicious_influences": auspicious,
            "inauspicious_influences": inauspicious,
            "harsha_bala_active": bool(h_harsha.get("is_active", False)),
            "verdict": verdict
        }

    return atmosphere_results
