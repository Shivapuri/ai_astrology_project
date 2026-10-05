"""
Astra Astrological Engine — Stage 2A: Relational Calculus & Dignity Matrix
Canonical implementation supporting both Ernst Wilhelm (Kala) and Mantreśvara (Phaladīpikā).
"""

from typing import Dict, Any, List, Optional
from jyotish.baseline import (
    ChartBaseline,
    SIGN_LORDS,
    VIMSHOTTARI_SEQUENCE,
    ZODIAC_SIGNS,
    PLANETS_ORDER,
    VARGAS_LIST,
    ALL_BODIES,
    NAISARGIKA_SAMBANDHA,
    FIXED_DIGNITIES,
)

# Canonical 9 Diptadi Avastha Categorization (Phaladipika Ch. 3 v. 18-19)
DIPTADI_AVASTHA_MAP = {
    "Exalted": "Pradipta",
    "Moolatrikona": "Sukhita",
    "Own Sign": "Svastha",
    "Great Friend's Sign": "Mudita",
    "Friend's Sign": "Mudita",
    "Neutral's Sign": "Santa",
    "Enemy's Sign": "Dina",
    "Great Enemy's Sign": "Dina",
    "Debilitated": "Khala",
    "Combust": "Vikala",
    "Defeated in War": "Nipidita",
}

# Vaisesikamsha Ladder across Dasavarga (Phaladipika Ch. 3 v. 6-7)
VAISESIKAMSA_NAMES = {
    2: "Pārijāta",
    3: "Uttama",
    4: "Gopura",
    5: "Siṁhāsana",
    6: "Parvata",
    7: "Devaloka",
    8: "Suraloka",
    9: "Airāvata",
    10: "Brahmapada",
}

# Phaladipika Ch. 8 & 20 Nodal Alliances (Asura Coalition)
PHALADIPIKA_NODE_RELATIONSHIPS = {
    "Friends": ["Mercury", "Venus", "Saturn"],
    "Neutrals": ["Mars"],
    "Enemies": ["Sun", "Moon", "Jupiter"],
}


def get_natural_relationship(
    planet1: str,
    planet2: str,
    nodal_methodology: str = "ernst_wilhelm"
) -> str:
    """
    Returns 'Friend', 'Neutral', or 'Enemy' for planet1's view of planet2.
    - Physical planets follow BPHS Ch. 15 Moolatrikona derivations.
    - Nodal evaluation supports two modes:
        1. 'ernst_wilhelm' (Default): Rahu = Saturn proxy, Ketu = Mars proxy (Sanivad Rahu, Kujavad Ketu).
        2. 'phaladipika': Both nodes follow Mantresvara's Asura coalition.
    """
    if planet1 == planet2:
        return "Self"

    # Nodal Evaluation
    if nodal_methodology == "ernst_wilhelm":
        if planet1 in ("Rahu", "Ketu"):
            proxy = "Saturn" if planet1 == "Rahu" else "Mars"
            if planet2 in NAISARGIKA_SAMBANDHA.get(proxy, {}).get("Friends", []):
                return "Friend"
            if planet2 in NAISARGIKA_SAMBANDHA.get(proxy, {}).get("Enemies", []):
                return "Enemy"
            return "Neutral"

        if planet2 in ("Rahu", "Ketu"):
            # Physical planet's view of node under proxy reflection
            proxy = "Saturn" if planet2 == "Rahu" else "Mars"
            if proxy in NAISARGIKA_SAMBANDHA.get(planet1, {}).get("Friends", []):
                return "Friend"
            if proxy in NAISARGIKA_SAMBANDHA.get(planet1, {}).get("Enemies", []):
                return "Enemy"
            return "Neutral"

    else:  # phaladipika
        if planet1 in ("Rahu", "Ketu"):
            if planet2 in PHALADIPIKA_NODE_RELATIONSHIPS["Friends"]:
                return "Friend"
            if planet2 in PHALADIPIKA_NODE_RELATIONSHIPS["Enemies"]:
                return "Enemy"
            return "Neutral"

        if planet2 in ("Rahu", "Ketu"):
            if planet1 in ("Saturn", "Venus", "Mercury"):
                return "Friend"
            if planet1 in ("Sun", "Moon", "Jupiter"):
                return "Enemy"
            return "Neutral"

    # Classical 7 Grahas
    if planet2 in NAISARGIKA_SAMBANDHA.get(planet1, {}).get("Friends", []):
        return "Friend"
    elif planet2 in NAISARGIKA_SAMBANDHA.get(planet1, {}).get("Enemies", []):
        return "Enemy"
    return "Neutral"


def get_temporary_relationship(p1_d1_idx: int, p2_d1_idx: int) -> str:
    """Calculates Tatkalika Maitri based on physical D1 positions (BPHS Ch. 15.56)."""
    if p1_d1_idx == p2_d1_idx:
        return "Enemy"

    distance = (p2_d1_idx - p1_d1_idx) % 12
    if distance in [1, 2, 3, 9, 10, 11]:
        return "Friend"
    return "Enemy"


def get_compound_relationship(natural: str, temporary: str) -> str:
    """Calculates Panchadha Sambandha (BPHS Ch. 15.57-58)."""
    if natural == "Self":
        return "Self"

    score = 0
    if natural == "Friend":
        score += 1
    elif natural == "Enemy":
        score -= 1

    if temporary == "Friend":
        score += 1
    elif temporary == "Enemy":
        score -= 1

    if score == 2:
        return "Great Friend"
    if score == 1:
        return "Friend"
    if score == 0:
        return "Neutral"
    if score == -1:
        return "Enemy"
    if score == -2:
        return "Great Enemy"

    return "Neutral"


def get_dignity(
    planet: str,
    sign: str,
    compound_rel: str,
    degree: float = 0.0,
    debilitation_mode: str = "kala_degree",
    is_varga: bool = False,
    ketu_own_sign: str = "Scorpio",
) -> str:
    """
    Evaluates final planetary dignity.
    - Preserves Ernst Wilhelm's kala_degree default bounds while supporting classical whole_sign.
    - Supports Ketu own sign in Scorpio (Ernst Wilhelm) or Pisces (orthodox alternative).
    """
    is_kala = (debilitation_mode == "kala_degree")

    # 1. SUN
    if planet == "Sun":
        if sign == "Aries":
            return "Exalted"
        if sign == "Libra":
            return "Debilitated"
        if sign == "Leo":
            if is_varga and not is_kala:
                return "Moolatrikona"
            return "Moolatrikona" if degree <= 20.0 else "Own Sign"

    # 2. MOON
    elif planet == "Moon":
        if sign == "Taurus":
            if is_varga and not is_kala:
                return "Exalted"
            return "Exalted" if degree <= 3.0 else "Moolatrikona"
        if sign == "Scorpio":
            if is_varga or debilitation_mode in ("traditional", "whole_sign"):
                return "Debilitated"
            if degree <= 3.0:
                return "Debilitated"
        elif sign == "Cancer":
            return "Own Sign"

    # 3. MARS
    elif planet == "Mars":
        if sign == "Capricorn":
            return "Exalted"
        if sign == "Cancer":
            return "Debilitated"
        if sign == "Aries":
            if is_varga and not is_kala:
                return "Moolatrikona"
            return "Moolatrikona" if degree <= 12.0 else "Own Sign"
        if sign == "Scorpio":
            return "Own Sign"

    # 4. MERCURY
    elif planet == "Mercury":
        if sign == "Virgo":
            if is_varga and not is_kala:
                return "Exalted"
            if degree <= 15.0:
                return "Exalted"
            elif degree <= 20.0:
                return "Moolatrikona"
            return "Own Sign"
        if sign == "Pisces":
            if is_varga or debilitation_mode in ("traditional", "whole_sign"):
                return "Debilitated"
            if degree <= 15.0:
                return "Debilitated"
        elif sign == "Gemini":
            return "Own Sign"

    # 5. JUPITER
    elif planet == "Jupiter":
        if sign == "Cancer":
            return "Exalted"
        if sign == "Capricorn":
            return "Debilitated"
        if sign == "Sagittarius":
            if is_varga and not is_kala:
                return "Moolatrikona"
            return "Moolatrikona" if degree <= 10.0 else "Own Sign"
        if sign == "Pisces":
            return "Own Sign"

    # 6. VENUS
    elif planet == "Venus":
        if sign == "Pisces":
            return "Exalted"
        if sign == "Virgo":
            return "Debilitated"
        if sign == "Libra":
            if is_varga and not is_kala:
                return "Moolatrikona"
            return "Moolatrikona" if degree <= 15.0 else "Own Sign"
        if sign == "Taurus":
            return "Own Sign"

    # 7. SATURN
    elif planet == "Saturn":
        if sign == "Libra":
            return "Exalted"
        if sign == "Aries":
            return "Debilitated"
        if sign == "Aquarius":
            if is_varga and not is_kala:
                return "Moolatrikona"
            return "Moolatrikona" if degree <= 20.0 else "Own Sign"
        if sign == "Capricorn":
            return "Own Sign"

    # 8. RAHU
    elif planet == "Rahu":
        if sign == "Taurus":
            return "Exalted"
        if sign == "Scorpio":
            return "Debilitated"
        if sign == "Gemini":
            return "Moolatrikona"
        if sign == "Aquarius":
            return "Own Sign"

    # 9. KETU
    elif planet == "Ketu":
        if sign == "Scorpio":
            return "Exalted"  # Exaltation takes precedence in Scorpio
        if sign == "Taurus":
            return "Debilitated"
        if sign == "Sagittarius":
            return "Moolatrikona"
        if sign == ketu_own_sign:
            return "Own Sign"

    return f"{compound_rel}'s Sign"


def calculate_chart_dignities(
    baseline: "ChartBaseline",
    debilitation_mode: str = "kala_degree",
    nodal_methodology: str = "ernst_wilhelm",
    ketu_own_sign: str = "Scorpio",
) -> Dict[str, Any]:
    """
    Stage 2A Master Orchestrator.
    Generates symmetric 9x9 relationship matrices, evaluates dignities across
    all 16 Divisional Charts, and computes Diptadi Avasthas and Vaisesikamsha.
    """
    all_grahas = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
    coords = baseline.coordinates

    # 1. Full Bidirectional Natural Relationships (Naisargika)
    natural_relationships = {
        p1: {
            p2: get_natural_relationship(p1, p2, nodal_methodology=nodal_methodology)
            for p2 in all_grahas
        }
        for p1 in all_grahas
    }

    # 2. Full Bidirectional D1 Temporary Friendship (Tatkalika)
    temporary_relationships = {
        p1: {
            p2: (
                "Self" if p1 == p2 else
                get_temporary_relationship(coords[p1]["sign_index"], coords[p2]["sign_index"])
            )
            for p2 in all_grahas
        }
        for p1 in all_grahas
    }

    # 3. Full Bidirectional Panchadha Maitri (Compound 5-Fold)
    compound_relationships = {
        p1: {
            p2: (
                "Self" if p1 == p2 else
                get_compound_relationship(natural_relationships[p1][p2], temporary_relationships[p1][p2])
            )
            for p2 in all_grahas
        }
        for p1 in all_grahas
    }

    # 4. Decompose Dignities Across all 16 Divisional Charts
    varga_dignities = {}
    vargas_data = baseline.vargas
    comb_status = getattr(baseline, "combustion_status", {}) or {}

    for v_name in VARGAS_LIST:
        v_grahas = vargas_data.get(v_name, {}).get("grahas", {})
        varga_dignities[v_name] = {}
        is_varga = (v_name != "D1")

        # Iterate over all 9 bodies present in the varga
        for p_name in all_grahas:
            if p_name not in v_grahas:
                continue
            p_data = v_grahas[p_name]
            sign = p_data["sign"]
            raw_lord = SIGN_LORDS[sign]

            # Co-rulership resolution for Aquarius (Rahu) and Scorpio/Pisces (Ketu)
            is_own_house = (
                (raw_lord == p_name)
                or (p_name == "Rahu" and sign == "Aquarius")
                or (p_name == "Ketu" and sign == ketu_own_sign)
            )
            effective_lord = p_name if is_own_house else raw_lord
            deg_in_sign = p_data.get("degree_0_to_30", p_data.get("degree_in_sign", 0.0))

            if is_own_house:
                nat = "Self"
                tmp = "Self"
                cmp_rel = "Self"
            else:
                nat = natural_relationships[p_name][effective_lord]
                tmp = temporary_relationships[p_name][effective_lord]
                cmp_rel = compound_relationships[p_name][effective_lord]

            final_dignity = get_dignity(
                p_name, sign, cmp_rel, deg_in_sign,
                debilitation_mode=debilitation_mode,
                is_varga=is_varga,
                ketu_own_sign=ketu_own_sign,
            )

            # Functional Diptadi Avastha Overrides (Phaladipika Ch. 3 v. 19)
            is_combust = comb_status.get(p_name, {}).get("is_combust", False) or coords.get(p_name, {}).get("is_combust", False)
            is_war_loser = coords.get(p_name, {}).get("is_war_loser", False) or (
                coords.get(p_name, {}).get("is_in_planetary_war", False)
                and coords.get(p_name, {}).get("war_details", {}).get("is_loser", False)
            )

            if is_war_loser and not is_varga:
                avastha = "Nipidita"
            elif is_combust and p_name not in ("Sun", "Rahu", "Ketu") and not is_varga:
                avastha = "Vikala"
            else:
                avastha = DIPTADI_AVASTHA_MAP.get(final_dignity, "Santa")

            varga_dignities[v_name][p_name] = {
                "sign": sign,
                "sign_lord": effective_lord,
                "natural_relationship": nat,
                "temporary_relationship": tmp,
                "compound_relationship": cmp_rel,
                "dignity": final_dignity,
                "avastha": avastha,
            }

    # 5. Compute Vaisesikamsha Ladder across Dasavarga for 7 Physical Grahas
    dasavarga_keys = ["D1", "D2", "D3", "D7", "D9", "D10", "D12", "D16", "D30", "D60"]
    vaisesikamsha = {}
    physical_planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

    for p_name in physical_planets:
        favorable_count = 0
        for v in dasavarga_keys:
            if v in varga_dignities and p_name in varga_dignities[v]:
                dig = varga_dignities[v][p_name]["dignity"]
                if any(x in dig for x in ("Exalted", "Moolatrikona", "Own Sign", "Great Friend", "Friend")):
                    favorable_count += 1
        title = VAISESIKAMSA_NAMES.get(favorable_count, "Sāmānya")
        vaisesikamsha[p_name] = {
            "favorable_count": favorable_count,
            "title": title
        }

    return {
        "natural_relationships": natural_relationships,
        "temporary_relationships": temporary_relationships,
        "compound_relationships": compound_relationships,
        "varga_dignities": varga_dignities,
        "vaisesikamsha": vaisesikamsha,
    }
