from typing import Dict, Any, List, Optional
from jyotish.baseline import (
    ChartBaseline,
    SIGN_LORDS,
    VIMSHOTTARI_SEQUENCE,
    ZODIAC_SIGNS,
    PLANETS_ORDER,
    VARGAS_LIST,
    ALL_BODIES,
)

# Fixed Natural Friendships (Naisargika Sambandha) based on Moolatrikona rules
NAISARGIKA_SAMBANDHA = {
    "Sun": {"Friends": ["Moon", "Mars", "Jupiter"], "Neutrals": ["Mercury"], "Enemies": ["Venus", "Saturn"]},
    "Moon": {"Friends": ["Sun", "Mercury"], "Neutrals": ["Mars", "Jupiter", "Venus", "Saturn"], "Enemies": []},
    "Mars": {"Friends": ["Sun", "Moon", "Jupiter"], "Neutrals": ["Venus", "Saturn"], "Enemies": ["Mercury"]},
    "Mercury": {"Friends": ["Sun", "Venus"], "Neutrals": ["Mars", "Jupiter", "Saturn"], "Enemies": ["Moon"]},
    "Jupiter": {"Friends": ["Sun", "Moon", "Mars"], "Neutrals": ["Saturn"], "Enemies": ["Mercury", "Venus"]},
    "Venus": {"Friends": ["Mercury", "Saturn"], "Neutrals": ["Mars", "Jupiter"], "Enemies": ["Sun", "Moon"]},
    "Saturn": {"Friends": ["Mercury", "Venus"], "Neutrals": ["Jupiter"], "Enemies": ["Sun", "Moon", "Mars"]}
}

# Specific fixed dignities (Exaltation, Moolatrikona, Own Sign)
FIXED_DIGNITIES = {
    "Sun": {"Exalted": "Aries", "Debilitated": "Libra", "Moolatrikona": "Leo", "Own": ["Leo"]},
    "Moon": {"Exalted": "Taurus", "Debilitated": "Scorpio", "Moolatrikona": "Taurus", "Own": ["Cancer"]},
    "Mars": {"Exalted": "Capricorn", "Debilitated": "Cancer", "Moolatrikona": "Aries", "Own": ["Aries", "Scorpio"]},
    "Mercury": {"Exalted": "Virgo", "Debilitated": "Pisces", "Moolatrikona": "Virgo", "Own": ["Gemini", "Virgo"]},
    "Jupiter": {"Exalted": "Cancer", "Debilitated": "Capricorn", "Moolatrikona": "Sagittarius", "Own": ["Sagittarius", "Pisces"]},
    "Venus": {"Exalted": "Pisces", "Debilitated": "Virgo", "Moolatrikona": "Libra", "Own": ["Taurus", "Libra"]},
    "Saturn": {"Exalted": "Libra", "Debilitated": "Aries", "Moolatrikona": "Aquarius", "Own": ["Capricorn", "Aquarius"]},
    # Kala standard rules for Nodes
    "Rahu": {"Exalted": "Taurus", "Debilitated": "Scorpio", "Moolatrikona": "Gemini", "Own": ["Aquarius"]},
    "Ketu": {"Exalted": "Scorpio", "Debilitated": "Taurus", "Moolatrikona": "Sagittarius", "Own": ["Scorpio"]}
}

def get_natural_relationship(planet1: str, planet2: str) -> str:
    """Returns 'Friend', 'Neutral', or 'Enemy' for planet1's view of planet2."""
    if planet1 in ["Rahu", "Ketu"]:
        proxy = "Saturn" if planet1 == "Rahu" else "Mars"
        if planet2 in NAISARGIKA_SAMBANDHA.get(proxy, {}).get("Friends", []): return "Friend"
        if planet2 in NAISARGIKA_SAMBANDHA.get(proxy, {}).get("Enemies", []): return "Enemy"
        return "Neutral"
        
    if planet2 in ["Rahu", "Ketu"]:
        return "Neutral"

    if planet2 in NAISARGIKA_SAMBANDHA.get(planet1, {}).get("Friends", []): return "Friend"
    elif planet2 in NAISARGIKA_SAMBANDHA.get(planet1, {}).get("Enemies", []): return "Enemy"
    return "Neutral"

def get_temporary_relationship(p1_d1_idx: int, p2_d1_idx: int) -> str:
    """
    Calculates Temporary (Tatkalika) Friendship based on Rasi (D1) positions.
    Returns 'Friend' (2nd, 3rd, 4th, 10th, 11th, 12th) or 'Enemy' (1st, 5th, 6th, 7th, 8th, 9th)
    """
    distance = (p2_d1_idx - p1_d1_idx) % 12
    # Distance is 0-indexed: 0 = 1st house (conjunction), 1 = 2nd house, etc.
    if distance in [1, 2, 3, 9, 10, 11]:
        return "Friend"
    return "Enemy"

def get_compound_relationship(natural: str, temporary: str) -> str:
    """Calculates the 5-Fold Compound Relationship (Panchadha Sambandha)."""
    score = 0
    if natural == "Friend": score += 1
    elif natural == "Enemy": score -= 1
    
    if temporary == "Friend": score += 1
    elif temporary == "Enemy": score -= 1
    
    if score == 2: return "Great Friend"
    if score == 1: return "Friend"
    if score == 0: return "Neutral"
    if score == -1: return "Enemy"
    if score == -2: return "Great Enemy"
    
    return "Neutral"

def get_dignity(planet: str, sign: str, compound_rel: str, degree: float = 0.0, debilitation_mode: str = "kala_degree") -> str:
    """Evaluates final planetary dignity based on sign, precise degree (for MT/OH), and compound relationship to sign lord."""
    if planet == "Sun":
        if sign == "Aries": return "Exalted"
        if sign == "Libra": return "Debilitated"
        if sign == "Leo":
            if degree <= 20: return "Moolatrikona"
            else: return "Own Sign"
    elif planet == "Moon":
        if sign == "Taurus":
            if degree <= 3: return "Exalted"
            else: return "Moolatrikona"
        if sign == "Scorpio":
            if debilitation_mode in ("traditional", "whole_sign") or degree <= 3:
                return "Debilitated"
            # If > 3 degrees in kala_degree mode, falls back to sign lord relationship below
        if sign == "Cancer": return "Own Sign"
    elif planet == "Mars":
        if sign == "Capricorn": return "Exalted"
        if sign == "Cancer": return "Debilitated"
        if sign == "Aries":
            if degree <= 12: return "Moolatrikona"
            else: return "Own Sign"
        if sign == "Scorpio": return "Own Sign"
    elif planet == "Mercury":
        if sign == "Virgo":
            if degree <= 15: return "Exalted"
            elif degree <= 20: return "Moolatrikona"
            else: return "Own Sign"
        if sign == "Pisces":
            if debilitation_mode in ("traditional", "whole_sign") or degree <= 15:
                return "Debilitated"
            # If > 15 degrees in kala_degree mode, falls back to sign lord relationship below
        if sign == "Gemini": return "Own Sign"
    elif planet == "Jupiter":
        if sign == "Cancer": return "Exalted"
        if sign == "Capricorn": return "Debilitated"
        if sign == "Sagittarius":
            if degree <= 10: return "Moolatrikona"
            else: return "Own Sign"
        if sign == "Pisces": return "Own Sign"
    elif planet == "Venus":
        if sign == "Pisces": return "Exalted"
        if sign == "Virgo": return "Debilitated"
        if sign == "Libra":
            if degree <= 15: return "Moolatrikona"
            else: return "Own Sign"
        if sign == "Taurus": return "Own Sign"
    elif planet == "Saturn":
        if sign == "Libra": return "Exalted"
        if sign == "Aries": return "Debilitated"
        if sign == "Aquarius":
            if degree <= 20: return "Moolatrikona"
            else: return "Own Sign"
        if sign == "Capricorn": return "Own Sign"
    elif planet == "Rahu":
        if sign == "Taurus": return "Exalted"
        if sign == "Scorpio": return "Debilitated"
        if sign == "Gemini": return "Moolatrikona"
        if sign == "Aquarius": return "Own Sign"
    elif planet == "Ketu":
        if sign == "Scorpio": return "Exalted"
        if sign == "Taurus": return "Debilitated"
        if sign == "Sagittarius": return "Moolatrikona"
        if sign == "Scorpio": return "Own Sign"

    return f"{compound_rel}'s Sign"

def calculate_chart_dignities(baseline: "ChartBaseline", debilitation_mode: str = "kala_degree") -> Dict[str, Any]:
    """
    High-Level Dignity Orchestrator for Stage 2A.
    Precalculates D1 Tatkalika Maitri (Temporary Friendship), Panchadha Maitri (5-Fold Compound Relationship),
    and decomposes planetary dignities across all 16 Divisional Charts (D1 through D60).
    """
    physical_planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    coords = baseline.coordinates

    # 1. Natural Relationships (Naisargika Sambandha)
    natural_relationships = {}
    for p1 in physical_planets:
        natural_relationships[p1] = {}
        for p2 in physical_planets:
            natural_relationships[p1][p2] = get_natural_relationship(p1, p2)

    # 2. D1 Temporary Friendship (Tatkalika Maitri)
    # Distance in signs (s2 - s1) % 12:
    # Houses 2, 3, 4, 10, 11, 12 (dist 1, 2, 3, 9, 10, 11) are Friend;
    # Houses 1, 5, 6, 7, 8, 9 (dist 0, 4, 5, 6, 7, 8) are Enemy.
    temporary_relationships = {}
    for p1 in physical_planets:
        temporary_relationships[p1] = {}
        p1_idx = coords[p1]["sign_index"]
        for p2 in physical_planets:
            p2_idx = coords[p2]["sign_index"]
            temporary_relationships[p1][p2] = get_temporary_relationship(p1_idx, p2_idx)

    # 3. Panchadha Maitri (5-Fold Compound Relationship)
    compound_relationships = {}
    for p1 in physical_planets:
        compound_relationships[p1] = {}
        for p2 in physical_planets:
            nat = natural_relationships[p1][p2]
            tmp = temporary_relationships[p1][p2]
            compound_relationships[p1][p2] = get_compound_relationship(nat, tmp)

    # Apply proxy rules for Rahu (Saturn) and Ketu (Mars)
    for node, proxy in [("Rahu", "Saturn"), ("Ketu", "Mars")]:
        natural_relationships[node] = {}
        compound_relationships[node] = {}
        temporary_relationships[node] = {}
        node_idx = coords[node]["sign_index"]
        for p2 in physical_planets:
            p2_idx = coords[p2]["sign_index"]
            nat = get_natural_relationship(node, p2)
            tmp = get_temporary_relationship(node_idx, p2_idx)
            natural_relationships[node][p2] = nat
            temporary_relationships[node][p2] = tmp
            compound_relationships[node][p2] = get_compound_relationship(nat, tmp)

    # 4. Decompose Varga Dignities Across all 16 Divisional Charts (D1 through D60)
    varga_dignities = {}
    vargas_data = baseline.vargas

    for v_name in VARGAS_LIST:
        v_grahas = vargas_data.get(v_name, {}).get("grahas", {})
        varga_dignities[v_name] = {}

        for p_name in PLANETS_ORDER:
            if p_name not in v_grahas:
                continue
            p_data = v_grahas[p_name]
            sign = p_data["sign"]
            lord = SIGN_LORDS[sign]
            deg_in_sign = p_data.get("degree_0_to_30", p_data.get("degree_in_sign", 0.0))

            if lord == p_name:
                nat = "Self"
                tmp = "Self"
                cmp_rel = "Self"
                final_dignity = get_dignity(p_name, sign, "Self", deg_in_sign, debilitation_mode=debilitation_mode)
            else:
                nat = get_natural_relationship(p_name, lord)
                p_d1_idx = coords[p_name]["sign_index"]
                lord_d1_idx = coords[lord]["sign_index"]
                tmp = get_temporary_relationship(p_d1_idx, lord_d1_idx)
                cmp_rel = get_compound_relationship(nat, tmp)
                final_dignity = get_dignity(p_name, sign, cmp_rel, deg_in_sign, debilitation_mode=debilitation_mode)

            varga_dignities[v_name][p_name] = {
                "sign": sign,
                "sign_lord": lord,
                "natural_relationship": nat,
                "temporary_relationship": tmp,
                "compound_relationship": cmp_rel,
                "dignity": final_dignity
            }

    return {
        "natural_relationships": natural_relationships,
        "temporary_relationships": temporary_relationships,
        "compound_relationships": compound_relationships,
        "varga_dignities": varga_dignities
    }
