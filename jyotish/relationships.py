# jyotish/relationships.py

# Ernst Wilhelm / Parashara Sign Rulerships
SIGN_LORDS = {
    "Aries": "Mars",
    "Taurus": "Venus",
    "Gemini": "Mercury",
    "Cancer": "Moon",
    "Leo": "Sun",
    "Virgo": "Mercury",
    "Libra": "Venus",
    "Scorpio": "Mars",
    "Sagittarius": "Jupiter",
    "Capricorn": "Saturn",
    "Aquarius": "Saturn",
    "Pisces": "Jupiter"
}

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

def get_dignity(planet: str, sign: str, compound_rel: str) -> str:
    """Evaluates final planetary dignity based on sign and compound relationship to sign lord."""
    fixed = FIXED_DIGNITIES.get(planet, {})
    
    if sign == fixed.get("Exalted"): return "Exalted"
    if sign == fixed.get("Debilitated"): return "Debilitated"
    if sign == fixed.get("Moolatrikona"): return "Moolatrikona"
    if sign in fixed.get("Own", []): return "Own Sign"
    
    return f"{compound_rel}'s Sign"

