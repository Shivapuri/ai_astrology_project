"""
jyotish/yogas/breakers.py
The Yoga Breaker (Yoga Bhanga) and Cancellation (Neecha Bhanga) auditing engine.
Implements classical Parashari (BPHS Ch. 34) and Mantreswara (Phaladeepika Ch. 7) rules.
"""

from typing import List, Dict, Any, Tuple, Optional
from jyotish.yogas.models import YogaBreakerDetail, YogaStatus

ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

# Natural benefics and malefics
NATURAL_BENEFICS = {"Jupiter", "Venus", "Moon", "Mercury"}
NATURAL_MALEFICS = {"Saturn", "Mars", "Rahu", "Ketu", "Sun"}

# Exaltation & Debilitation Signs
EXALTATION_SIGNS = {
    "Sun": "Aries", "Moon": "Taurus", "Mars": "Capricorn",
    "Mercury": "Virgo", "Jupiter": "Cancer", "Venus": "Pisces", "Saturn": "Libra"
}
DEBILITATION_SIGNS = {
    "Sun": "Libra", "Moon": "Scorpio", "Mars": "Cancer",
    "Mercury": "Pisces", "Jupiter": "Capricorn", "Venus": "Virgo", "Saturn": "Aries"
}
OWN_SIGNS = {
    "Sun": ["Leo"], "Moon": ["Cancer"], "Mars": ["Aries", "Scorpio"],
    "Mercury": ["Gemini", "Virgo"], "Jupiter": ["Sagittarius", "Pisces"],
    "Venus": ["Taurus", "Libra"], "Saturn": ["Capricorn", "Aquarius"]
}
SIGN_LORDS = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury", "Cancer": "Moon",
    "Leo": "Sun", "Virgo": "Mercury", "Libra": "Venus", "Scorpio": "Mars",
    "Sagittarius": "Jupiter", "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter"
}

def get_lagna_sign(chart: Dict[str, Any]) -> str:
    """Returns the Ascendant (Lagna) sign name."""
    sign = chart.get("vargas", {}).get("D1", {}).get("lagna", {}).get("sign")
    if not sign:
        sign = chart.get("ascendant", {}).get("sign", "Aries")
    return sign

def get_planets_data(chart: Dict[str, Any]) -> Dict[str, Any]:
    """Returns the D1 grahas dictionary."""
    grahas = chart.get("vargas", {}).get("D1", {}).get("grahas")
    if not grahas:
        grahas = chart.get("planets", {})
    return grahas

def get_sign_of_planet(chart: Dict[str, Any], planet: str) -> str:
    """Returns the zodiac sign of a planet."""
    return get_planets_data(chart).get(planet, {}).get("sign", "")

def get_house_of_planet(chart: Dict[str, Any], planet: str) -> int:
    """Returns the Whole Sign House (1-12) of a planet relative to Lagna."""
    lagna = get_lagna_sign(chart)
    p_sign = get_sign_of_planet(chart, planet)
    if not lagna or not p_sign or lagna not in ZODIAC_SIGNS or p_sign not in ZODIAC_SIGNS:
        return 0
    l_idx = ZODIAC_SIGNS.index(lagna)
    p_idx = ZODIAC_SIGNS.index(p_sign)
    return (p_idx - l_idx) % 12 + 1

def get_aspect_score(chart: Dict[str, Any], giver: str, receiver: str) -> float:
    """Returns Graha Drishti aspect value (0-60 Virupas) from giver to receiver."""
    aspects = chart.get("advanced_aspects", {}).get("planets", {})
    if giver in aspects and receiver in aspects[giver]:
        val = aspects[giver][receiver]
        if isinstance(val, dict):
            return float(val.get("raw", val.get("net", 0.0)))
        return float(val)
    return 0.0

def get_house_rulers(chart: Dict[str, Any]) -> Dict[int, List[str]]:
    """Maps house number (1-12) to ruling planet(s) based on Lagna sign."""
    lagna_sign = get_lagna_sign(chart)
    if lagna_sign not in ZODIAC_SIGNS:
        return {h: [] for h in range(1, 13)}
    
    start_idx = ZODIAC_SIGNS.index(lagna_sign)
    house_rulers = {}
    for h in range(1, 13):
        sign = ZODIAC_SIGNS[(start_idx + h - 1) % 12]
        lord = SIGN_LORDS.get(sign)
        house_rulers[h] = [lord] if lord else []
    return house_rulers

def audit_trishadaya_interference(
    yoga_planets: List[str],
    chart: Dict[str, Any],
    is_supreme_pairing: bool = False
) -> List[YogaBreakerDetail]:
    """
    Audits intrusion of the Trishadaya lords (3rd, 6th, and 11th).
    11th Lord: Strongest saboteur (-40%): vanity, prestige obsession, greed.
    6th Lord: Moderate saboteur (-25%): litigation, debts, acute disputes.
    3rd Lord: Weakest saboteur (-15%): hobbies, distraction, restless ego.
    """
    breakers = []
    house_rulers = get_house_rulers(chart)
    lagna_lord = house_rulers.get(1, [None])[0]
    
    lord_11 = house_rulers.get(11, [None])[0]
    lord_6 = house_rulers.get(6, [None])[0]
    lord_3 = house_rulers.get(3, [None])[0]
    
    saboteurs = [
        (lord_11, 11, 40.0, "11th Lord Intrusion (Primary Saboteur)",
         "Rules Labha (desires/gains). Corrupts higher purpose (Dharma) into vanity, applause-seeking, and social distraction."),
        (lord_6, 6, 25.0, "6th Lord Intrusion",
         "Rules Shatru/Roga. Injects litigation, chronic workplace friction, debts, and competitive animosity into the combination."),
        (lord_3, 3, 15.0, "3rd Lord Intrusion",
         "Rules Sahaja/Bhratri. Dissipates focus into petty hobbies, sibling drama, and restless, unfocused effort.")
    ]
    
    for saboteur, house_num, base_penalty, title, desc in saboteurs:
        if not saboteur or saboteur in yoga_planets:
            continue
        # Lagnesha exemption: Ascendant lord never destroys the native's yoga
        if saboteur == lagna_lord:
            continue
            
        penalty = base_penalty
        if is_supreme_pairing and house_num == 3:
            penalty = 7.5  # Supreme 9th+10th alliance easily resists minor 3rd lord distraction
            
        saboteur_house = get_house_of_planet(chart, saboteur)
        
        for yp in yoga_planets:
            yp_house = get_house_of_planet(chart, yp)
            
            # 1. Conjunction in same house
            if saboteur_house == yp_house and yp_house != 0:
                breakers.append(YogaBreakerDetail(
                    factor=title,
                    culprit_planet=saboteur,
                    description=f"{saboteur} (rules H{house_num}) conjoins {yp} in House {yp_house}. {desc}",
                    penalty=penalty
                ))
                break
                
            # 2. Strong Graha Drishti aspect (> 30 Virupas)
            aspect_score = get_aspect_score(chart, saboteur, yp)
            if aspect_score >= 30.0:
                breakers.append(YogaBreakerDetail(
                    factor=f"{title} (Aspectual)",
                    culprit_planet=saboteur,
                    description=f"{saboteur} (rules H{house_num}) casts strong {aspect_score:.0f}-Virupa aspect on {yp}. {desc}",
                    penalty=penalty * (aspect_score / 60.0)
                ))
                break
                
    return breakers

def audit_combustion(yoga_planets: List[str], chart: Dict[str, Any]) -> List[YogaBreakerDetail]:
    """
    Audits whether participating planets are combust (< 8° from Sun).
    Deep combustion (< 3°) burns independent manifestation capacity.
    """
    breakers = []
    planets_data = get_planets_data(chart)
    sun_lon = planets_data.get("Sun", {}).get("longitude")
    if sun_lon is None:
        return breakers
        
    for p in yoga_planets:
        if p in ("Sun", "Rahu", "Ketu"):
            continue
        p_lon = planets_data.get(p, {}).get("longitude")
        if p_lon is None:
            continue
            
        diff = abs(p_lon - sun_lon) % 360.0
        if diff > 180.0:
            diff = 360.0 - diff
            
        if diff < 3.0:
            breakers.append(YogaBreakerDetail(
                factor="Deep Planetary Combustion (Astangata)",
                culprit_planet="Sun",
                description=f"{p} is deeply combust within {diff:.1f}° of the Sun. Its independent rays and tangible manifestation power are burned.",
                penalty=40.0
            ))
        elif diff < 8.0:
            breakers.append(YogaBreakerDetail(
                factor="Moderate Planetary Combustion (Astangata)",
                culprit_planet="Sun",
                description=f"{p} is combust within {diff:.1f}° of the Sun. May produce internal egoic conflict or diminished visibility.",
                penalty=20.0
            ))
            
    return breakers

def audit_neecha_bhanga(planet: str, chart: Dict[str, Any]) -> Tuple[bool, List[str], float]:
    """
    Audits the 6 Classical Cancellation of Debility (Neecha Bhanga) rules
    according to Phaladeepika 7.24-30 and VA Vol 1 Ch. 16.
    Returns: (is_rescued, reasons, redemption_bonus_percentage)
    """
    planets_data = get_planets_data(chart)
    p_info = planets_data.get(planet, {})
    p_sign = p_info.get("sign", "")
    
    if p_sign != DEBILITATION_SIGNS.get(planet):
        return False, [], 0.0  # Planet is not debilitated
        
    reasons = []
    bonus = 0.0
    
    debilitation_sign = p_sign
    dispositor = SIGN_LORDS.get(debilitation_sign)
    exaltation_sign = EXALTATION_SIGNS.get(planet)
    exaltation_lord = SIGN_LORDS.get(exaltation_sign)
    
    moon_house = get_house_of_planet(chart, "Moon")
    p_house = get_house_of_planet(chart, planet)
    
    # Condition 1: Exalted Co-occupant in same sign (e.g. Einstein Mercury + exalted Venus)
    for other_p, data in planets_data.items():
        if other_p != planet and data.get("sign") == debilitation_sign:
            if data.get("sign") == EXALTATION_SIGNS.get(other_p):
                reasons.append(f"Exalted co-occupant: {other_p} is exalted in {debilitation_sign} sharing the sign with fallen {planet}.")
                bonus += 35.0
                break
                
    # Condition 2: Dispositor of debilitation sign in Kendra from Lagna (1,4,7,10) or Moon
    if dispositor:
        disp_house = get_house_of_planet(chart, dispositor)
        if disp_house in (1, 4, 7, 10):
            reasons.append(f"Dispositor in Kendra from Lagna: {dispositor} (lord of {debilitation_sign}) occupies Kendra H{disp_house}.")
            bonus += 30.0
        elif moon_house > 0 and ((disp_house - moon_house) % 12 + 1) in (1, 4, 7, 10):
            reasons.append(f"Dispositor in Kendra from Moon: {dispositor} is in an angle from Chandra.")
            bonus += 25.0
            
    # Condition 3: Planet that exalts in this sign is in Kendra from Lagna or Moon
    if exaltation_lord:
        ex_lord_house = get_house_of_planet(chart, exaltation_lord)
        if ex_lord_house in (1, 4, 7, 10):
            reasons.append(f"Exaltation lord in Kendra from Lagna: {exaltation_lord} occupies Kendra H{ex_lord_house}.")
            bonus += 25.0
        elif moon_house > 0 and ((ex_lord_house - moon_house) % 12 + 1) in (1, 4, 7, 10):
            reasons.append(f"Exaltation lord in Kendra from Moon: {exaltation_lord} is in an angle from Chandra.")
            bonus += 20.0
            
    # Condition 4: Dispositor of debilitation sign is itself exalted
    if dispositor:
        disp_sign = get_sign_of_planet(chart, dispositor)
        if disp_sign == EXALTATION_SIGNS.get(dispositor):
            reasons.append(f"Exalted dispositor: {dispositor} (ruler of {debilitation_sign}) is exalted in {disp_sign}.")
            bonus += 30.0
            
    # Condition 5: Dispositor aspects the fallen planet
    if dispositor:
        aspect_score = get_aspect_score(chart, dispositor, planet)
        if aspect_score >= 30.0:
            reasons.append(f"Dispositor aspect: {dispositor} directly aspects fallen {planet} with {aspect_score:.0f} Virupas.")
            bonus += 25.0
            
    # Condition 6: Fallen planet itself is in Kendra from Lagna or Moon
    if p_house in (1, 4, 7, 10):
        reasons.append(f"Angular fallen planet: {planet} is in Kendra H{p_house} from Lagna, forcing public engagement.")
        bonus += 20.0
    elif moon_house > 0 and ((p_house - moon_house) % 12 + 1) in (1, 4, 7, 10):
        reasons.append(f"Angular fallen planet from Moon: {planet} is in Kendra from Chandra.")
        bonus += 15.0
        
    is_rescued = len(reasons) >= 1 and bonus >= 30.0
    return is_rescued, reasons, min(bonus, 100.0)

def audit_dispositor_vitality(yoga_planets: List[str], chart: Dict[str, Any]) -> List[YogaBreakerDetail]:
    """
    Audits the condition of the dispositor (host) for the yoga-forming planets.
    If the host is ruined, the foundation of the yoga is hollow.
    """
    breakers = []
    
    for p in yoga_planets:
        sign = get_sign_of_planet(chart, p)
        dispositor = SIGN_LORDS.get(sign)
        if not dispositor or dispositor == p:
            continue
            
        disp_sign = get_sign_of_planet(chart, dispositor)
        disp_house = get_house_of_planet(chart, dispositor)
        
        # Dispositor debilitated without Neecha Bhanga
        if disp_sign == DEBILITATION_SIGNS.get(dispositor):
            is_rescued, _, _ = audit_neecha_bhanga(dispositor, chart)
            if not is_rescued:
                breakers.append(YogaBreakerDetail(
                    factor="Debilitated Host Dispositor",
                    culprit_planet=dispositor,
                    description=f"{p}'s dispositor {dispositor} is in fall in {disp_sign} without cancellation. The guest lacks institutional backing.",
                    penalty=25.0
                ))
                
        # Dispositor trapped in Dusthana (6, 8, 12)
        if disp_house in (6, 8, 12):
            breakers.append(YogaBreakerDetail(
                factor="Host Dispositor Trapped in Dusthana",
                culprit_planet=dispositor,
                description=f"{p}'s dispositor {dispositor} resides in difficult House {disp_house}. Energy leaks into friction or isolation.",
                penalty=15.0
            ))
            
    return breakers

def audit_dusthana_placement(
    yoga_houses: List[int],
    category_name: str
) -> Optional[YogaBreakerDetail]:
    """
    Auspicious worldly yogas (Raja, Dhana, Mahapurusha) placed in 6, 8, 12
    dissipate public authority into internal struggle, health issues, or seclusion.
    """
    dusthana_count = sum(1 for h in yoga_houses if h in (6, 8, 12))
    if dusthana_count > 0:
        return YogaBreakerDetail(
            factor="Dusthana Trapping (Houses 6, 8, 12)",
            culprit_planet="House Placement",
            description=f"Yoga manifests in Dusthana houses ({[h for h in yoga_houses if h in (6, 8, 12)]}). Results manifest privately, spiritually, or after severe crisis rather than public eminence.",
            penalty=25.0 * dusthana_count
        )
    return None

def audit_shadbala_muscle(yoga_planets: List[str], chart: Dict[str, Any]) -> Tuple[List[YogaBreakerDetail], List[str]]:
    """
    Audits whether planets possess the raw horsepower (Shadbala) to deliver results.
    Standard: >= 1.0 Rupa (>= 100% requirement).
    """
    breakers = []
    positive_notes = []
    shadbala = chart.get("shadbala", {})
    
    for p in yoga_planets:
        p_bala = shadbala.get(p, {})
        rupas = p_bala.get("Rupas", 1.0)
        ratio = p_bala.get("Ratio_to_Req", 1.0)
        
        if ratio < 0.85:
            breakers.append(YogaBreakerDetail(
                factor="Low Kinetic Horsepower (Shadbala)",
                culprit_planet=p,
                description=f"{p} has only {rupas:.2f} Rupas ({ratio*100:.0f}% of required strength). Lacks kinetic muscle to deliver tangible promises.",
                penalty=15.0
            ))
        elif ratio >= 1.25:
            positive_notes.append(f"{p} is muscular in Shadbala ({rupas:.2f} Rupas / {ratio*100:.0f}% of requirement).")
            
    return breakers, positive_notes
