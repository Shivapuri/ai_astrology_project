"""
Astra Astrological Computation Engine - Karakas and Functional Roles
====================================================================
Implements:
1. Chara Karakas (7-Graha Variable Significators: AK through DK, BPHS Ch. 32)
2. Functional House Rulerships, Yogakarakas, Marakas, and Badhakas (BPHS Ch. 34)
3. Naisargika Karakas (Natural Fixed Significators)

All calculations are purely dynamic, anchored in Swiss Ephemeris longitudes and Whole Sign Ascendants.
"""

from typing import Dict, Any, List, Optional

ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer",
    "Leo", "Virgo", "Libra", "Scorpio",
    "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

SIGN_LORDS = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury", "Cancer": "Moon",
    "Leo": "Sun", "Virgo": "Mercury", "Libra": "Venus", "Scorpio": "Mars",
    "Sagittarius": "Jupiter", "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter"
}

# Sign Modality for Badhaka Determination:
# Movable (Chara) -> 11th House is Badhaka
# Fixed (Sthira) -> 9th House is Badhaka
# Dual (Dvisvabhava) -> 7th House is Badhaka
SIGN_MODALITY = {
    "Aries": "Movable", "Cancer": "Movable", "Libra": "Movable", "Capricorn": "Movable",
    "Taurus": "Fixed", "Leo": "Fixed", "Scorpio": "Fixed", "Aquarius": "Fixed",
    "Gemini": "Dual", "Virgo": "Dual", "Sagittarius": "Dual", "Pisces": "Dual"
}

CHARA_KARAKA_ORDER = ["AK", "AmK", "BK", "MK", "PK", "GK", "DK"]

CHARA_KARAKA_DETAILS = {
    "AK": {
        "symbol": "AK",
        "name": "Ātmakāraka",
        "title": "Soul Significator (King)",
        "description": "Primary vehicle of the soul; represents core lessons, willpower, and divine purpose."
    },
    "AmK": {
        "symbol": "AmK",
        "name": "Amātyakāraka",
        "title": "Career & Intellect (Prime Minister)",
        "description": "Advises the soul; represents intellect, professional actions, and worldly achievement."
    },
    "BK": {
        "symbol": "BK",
        "name": "Bhrātṛkāraka",
        "title": "Guru & Peers (Companions)",
        "description": "Represents spiritual guides, mentors, gurus, brothers, and kindred souls."
    },
    "MK": {
        "symbol": "MK",
        "name": "Mātṛkāraka",
        "title": "Mother & Foundations (Roots)",
        "description": "Represents mother, emotional grounding, home, land, and foundational learning."
    },
    "PK": {
        "symbol": "PK",
        "name": "Putrakāraka",
        "title": "Children & Intelligence (Creative Fruit)",
        "description": "Represents children, creative intelligence, disciples, and future merit."
    },
    "GK": {
        "symbol": "GK",
        "name": "Jñātikāraka",
        "title": "Obstacles & Rivals (Karmic Friction)",
        "description": "Represents kinsmen, competitors, sickness, debts, and karmic resilience."
    },
    "DK": {
        "symbol": "DK",
        "name": "Dārakāraka",
        "title": "Spouse & Partner (Intimate Mirror)",
        "description": "Represents spouse, romantic partners, and deep collaborative relationships."
    }
}

NAISARGIKA_KARAKAS = {
    "Sun": "Soul, Father, Vitality, Authority, Dharma",
    "Moon": "Mind, Mother, Emotions, Peace, Nourishment",
    "Mars": "Energy, Siblings, Courage, Real Estate, Ambition",
    "Mercury": "Intellect, Speech, Education, Trade, Discernment",
    "Jupiter": "Wisdom, Children, Guru, Wealth, Divine Grace",
    "Venus": "Love, Spouse, Pleasure, Vehicles, Aesthetic Arts",
    "Saturn": "Longevity, Discipline, Hard Work, Grief, Endurance",
    "Rahu": "Ambition, Foreign Lands, Research, Unconventional Path",
    "Ketu": "Moksha, Spiritual Intuition, Renunciation, Mastery"
}


def calculate_chara_karakas(d1_grahas: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """
    Calculates the 7 Chara Karakas (AK through DK) based on classical Parashari degrees.
    Takes 7 physical Grahas (Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn).
    Ranks them strictly by degree traversed in sign (degree_0_to_30, descending).
    """
    classical_planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    
    planet_degrees = []
    for p in classical_planets:
        if p in d1_grahas:
            g_data = d1_grahas[p]
            # Use degree_0_to_30 or longitude % 30
            deg = g_data.get("degree_0_to_30")
            if deg is None:
                lon = g_data.get("longitude", 0.0)
                deg = lon % 30.0
            planet_degrees.append((p, float(deg)))
            
    # Sort descending by degree. If identical, secondary sort preserves classical planetary order
    planet_degrees.sort(key=lambda x: x[1], reverse=True)
    
    chara_dict: Dict[str, Dict[str, Any]] = {}
    
    for idx, (planet, deg) in enumerate(planet_degrees):
        if idx < len(CHARA_KARAKA_ORDER):
            code = CHARA_KARAKA_ORDER[idx]
            info = CHARA_KARAKA_DETAILS[code]
            chara_dict[planet] = {
                "karaka": code,
                "name": info["name"],
                "title": info["title"],
                "description": info["description"],
                "rank": idx + 1,
                "degree_in_sign": round(deg, 4)
            }
            
    # Add Nodes as Chhaya Catalysts
    for node in ["Rahu", "Ketu"]:
        if node in d1_grahas:
            chara_dict[node] = {
                "karaka": "—",
                "name": "Chhāyā Catalyst",
                "title": "Karmic Shadow Catalyst",
                "description": "Shadow node; operates through its dispositor and conjunct planets rather than holding a Chara Karaka post.",
                "rank": None,
                "degree_in_sign": round(float(d1_grahas[node].get("degree_0_to_30", 0.0)), 4)
            }
            
    return chara_dict


def calculate_functional_roles(lagna_sign: str) -> Dict[str, Dict[str, Any]]:
    """
    Computes house rulerships, Yogakaraka status, Maraka, and Badhaka for all planets
    from a given Ascendant sign (Whole Sign houses, BPHS Ch. 34).
    """
    if lagna_sign not in ZODIAC_SIGNS:
        return {}
        
    lagna_idx = ZODIAC_SIGNS.index(lagna_sign)
    
    # 1. Map each of the 12 houses to its zodiac sign and lord
    house_lords = {}
    house_signs = {}
    for h in range(1, 13):
        s_idx = (lagna_idx + h - 1) % 12
        s_name = ZODIAC_SIGNS[s_idx]
        house_signs[h] = s_name
        house_lords[h] = SIGN_LORDS[s_name]
        
    # 2. Determine Badhaka house based on Lagna modality
    modality = SIGN_MODALITY.get(lagna_sign, "Movable")
    badhaka_house = 11 if modality == "Movable" else (9 if modality == "Fixed" else 7)
    
    # 3. For each planet, collect ruled houses and analyze functional nature
    classical_planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    roles: Dict[str, Dict[str, Any]] = {}
    
    for p in classical_planets:
        ruled = [h for h in range(1, 13) if house_lords[h] == p]
        
        # Kendra (Action / Vishnu): 1, 4, 7, 10
        # Trikona (Grace / Lakshmi): 1, 5, 9
        # Pure Kendra (excluding 1): 4, 7, 10
        # Pure Trikona (excluding 1): 5, 9
        has_pure_kendra = any(h in [4, 7, 10] for h in ruled)
        has_pure_trikona = any(h in [5, 9] for h in ruled)
        is_lagnesha = (1 in ruled)
        
        # Classical Yogakaraka: Simultaneous lordship of a Kendra (4, 7, 10) AND a Trikona (5, 9)
        is_yogakaraka = bool(has_pure_kendra and has_pure_trikona)
        
        is_maraka = any(h in [2, 7] for h in ruled)
        is_badhaka = (badhaka_house in ruled)
        is_dusthana = any(h in [6, 8, 12] for h in ruled)
        is_trishadaya = any(h in [3, 6, 11] for h in ruled)
        
        # Classification & Badge
        role_badges = []
        if is_yogakaraka:
            role_badges.append("⭐ Yogakāraka")
        elif is_lagnesha:
            role_badges.append("🛡️ Lagneśa")
            
        if is_maraka:
            maraka_houses = [f"H{h}" for h in ruled if h in [2, 7]]
            role_badges.append(f"Māraka ({'/'.join(maraka_houses)})")
            
        if is_badhaka:
            role_badges.append(f"Bādhaka (H{badhaka_house})")
            
        if is_dusthana and not is_lagnesha and not is_yogakaraka:
            dusthana_houses = [f"H{h}" for h in ruled if h in [6, 8, 12]]
            role_badges.append(f"Duṣṭhāna ({'/'.join(dusthana_houses)})")
            
        # Summary functional status
        if is_yogakaraka:
            status = "Yogakāraka"
            summary_desc = f"Supreme benefic for {lagna_sign} Lagna; simultaneously commands Kendra and Trikona power."
        elif is_lagnesha:
            status = "Functional Benefic (Lagneśa)"
            summary_desc = f"Ruler of the Ascendant; primary protective pillar of self and physical vitality."
        elif has_pure_trikona and not is_trishadaya:
            status = "Functional Benefic"
            summary_desc = f"Trikona ruler; brings auspicious merit, wisdom, and favorable dharmic fruit."
        elif is_trishadaya and not has_pure_trikona:
            status = "Functional Malefic"
            summary_desc = f"Ruler of hard houses ({', '.join(f'H{h}' for h in ruled if h in [3, 6, 11])}); requires conscious effort and discipline."
        else:
            status = "Functional Neutral / Mixed"
            summary_desc = f"Dual rulership ({', '.join(f'H{h}' for h in ruled)}); results depend heavily on placement and dignity."
            
        roles[p] = {
            "planet": p,
            "ruled_houses": ruled,
            "ruled_houses_str": ", ".join(f"H{h}" for h in ruled),
            "is_yogakaraka": is_yogakaraka,
            "is_lagnesha": is_lagnesha,
            "is_maraka": is_maraka,
            "is_badhaka": is_badhaka,
            "is_dusthana": is_dusthana,
            "is_trishadaya": is_trishadaya,
            "status": status,
            "badges": role_badges,
            "summary_desc": summary_desc,
            "naisargika": NAISARGIKA_KARAKAS.get(p, "")
        }
        
    # Nodes
    for node in ["Rahu", "Ketu"]:
        roles[node] = {
            "planet": node,
            "ruled_houses": [],
            "ruled_houses_str": "None (Chhāyā)",
            "is_yogakaraka": False,
            "is_lagnesha": False,
            "is_maraka": False,
            "is_badhaka": False,
            "is_dusthana": False,
            "is_trishadaya": False,
            "status": "Shadow Catalyst",
            "badges": ["Chhāyā Graha"],
            "summary_desc": f"Shadow node with no physical house ownership; adopts the agenda of its dispositor and conjunct planets.",
            "naisargika": NAISARGIKA_KARAKAS.get(node, "")
        }
        
    return roles


def get_all_varga_functional_roles(vargas_data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """
    Computes functional roles for each divisional chart (D1 through D60)
    based on each Varga's own Ascendant sign.
    """
    varga_roles = {}
    for v_name, v_data in vargas_data.items():
        v_lagna = v_data.get("lagna", {})
        l_sign = v_lagna.get("sign")
        if l_sign:
            varga_roles[v_name] = calculate_functional_roles(l_sign)
        else:
            varga_roles[v_name] = {}
    return varga_roles
