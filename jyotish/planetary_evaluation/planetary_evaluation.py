"""
planetary_evaluation.py

Precision implementation of Vic DiCara's Planetary Evaluation & Positive-to-Negative Scale.
Based on classical Sanskrit astrology (Phaladeepika Chapters 3 & 4) and Vic DiCara's methodology:
1. Two Fundamental Pillars: Dignity (Avastha / Mood) vs. Strength (Bala / Raw Kinetic Muscle).
2. The 4 Archetypal Quadrants (King with Armies, Armed Dictator, Sincere Friend, Bully Behind Bars).
3. The 4-Step Diagnostic Algorithm:
   - Step 1: Base Shadvarga Dignity (0% to 100% mapped to centered -100% to +100% spectrum).
   - Step 2: The Dispositor Anchor & Host Rescue Rule (Alchemical Exception / Neecha Bhanga).
   - Step 3: Conjunctions & Aspect Gradients (Continuous Drishti, Jupiter 100% healing ray, Sun combustion).
   - Step 4: House Field & Dusthana Reversals (Harsha, Sarala, Vimala Yogas).
4. The Three Master Lords of Destiny (Lagna-isha, Navamsha-isha, Drekkana-isha).
5. Comprehensive mathematical audit trail for transparent pedagogical display.
"""

from typing import Dict, List, Any, Optional, Tuple
import math
import jyotish.relationships.relationships as rel
import jyotish.aspects.aspects as aspects
from jyotish.planetary_evaluation.lagna_evaluation import evaluate_lagna_vitality
from jyotish.karakas import calculate_functional_roles
from jyotish.nakshatra_metadata import get_nakshatra_metadata

ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

PLANET_GLYPHS = {
    "Sun": "☉",
    "Moon": "☽",
    "Mars": "♂",
    "Mercury": "☿",
    "Jupiter": "♃",
    "Venus": "♀",
    "Saturn": "♄",
    "Rahu": "☊",
    "Ketu": "☋"
}

# Dignity Score mapping based on Ryan Kurczak (The Art and Science of Vedic Astrology Vol 1 Ch 6)
# and classical Panchadha Maitri 5-fold compound relationships:
# Exalted: 100%, Moolatrikona: 87.5%, Own Positive: 75%, Own Negative: 62.5%,
# Great Friend: 60%, Friend: 50%, Neutral: 37.5%, Enemy: 25%, Great Enemy: 20%, Debilitated: 12.5%
DIGNITY_SCORE_MAP: Dict[str, float] = {
    "Exalted": 100.0,
    "Exaltation": 100.0,
    "Paramoccha": 100.0,
    "Uccha": 100.0,
    "Moolatrikona": 87.5,
    "Own Positive Sign": 75.0,
    "Own Negative Sign": 62.5,
    "Own Sign": 68.75,  # Balanced midpoint if gender is unspecified
    "Own House": 68.75,
    "Sva-kshetra": 68.75,
    "Great Friend's Sign": 60.0,
    "Great Friend": 60.0,
    "Adhi-mitra": 60.0,
    "Friend's Sign": 50.0,
    "Friend": 50.0,
    "Mitra": 50.0,
    "Neutral's Sign": 37.5,
    "Neutral": 37.5,
    "Sama": 37.5,
    "Enemy's Sign": 25.0,
    "Enemy": 25.0,
    "Shatru": 25.0,
    "Great Enemy's Sign": 20.0,
    "Great Enemy": 20.0,
    "Adhi-shatru": 20.0,
    "Debilitated": 12.5,
    "Debilitation": 12.5,
    "Neecha": 12.5
}

ODD_SIGNS = {"Aries", "Gemini", "Leo", "Libra", "Sagittarius", "Aquarius"}
EVEN_SIGNS = {"Taurus", "Cancer", "Virgo", "Scorpio", "Capricorn", "Pisces"}

MOOLATRIKONA_RANGES = {
    "Sun": ("Leo", 0.0, 20.0),
    "Moon": ("Taurus", 3.0, 30.0),
    "Mars": ("Aries", 0.0, 12.0),
    "Mercury": ("Virgo", 15.0, 20.0),
    "Jupiter": ("Sagittarius", 0.0, 10.0),
    "Venus": ("Libra", 0.0, 15.0),
    "Saturn": ("Aquarius", 0.0, 20.0),
}

TRUE_DEBILITATION_MAP = {
    "Sun": "Libra",
    "Moon": "Scorpio",
    "Mars": "Cancer",
    "Mercury": "Pisces",
    "Jupiter": "Capricorn",
    "Venus": "Virgo",
    "Saturn": "Aries",
    "Rahu": "Scorpio",
    "Ketu": "Taurus"
}

# Signs where nodes gain special strength (Phaladeepika 4.5 & Lesson 19)
RAHU_STRONG_SIGNS = {"Aries", "Taurus", "Cancer", "Scorpio", "Aquarius"}
KETU_STRONG_SIGNS = {"Taurus", "Gemini", "Virgo", "Sagittarius", "Pisces"}

SHADVARGA_LIST = ["D1", "D2", "D3", "D9", "D12", "D30"]

def get_dignity_score(
    dignity_str: str,
    planet: Optional[str] = None,
    sign: Optional[str] = None,
    degree: float = 0.0
) -> float:
    """
    Normalizes dignity string and returns its 0-100% score per Ryan Kurczak's 12.5% step scale
    and classical Panchadha Maitri. Dynamically handles own positive/negative signs,
    single-ruling luminary domicile parity (75.0%), and moolatrikona degree bounds.
    """
    if not dignity_str:
        return 37.5
    cleaned = dignity_str.strip()
    c_low = cleaned.lower()

    if "exalt" in c_low:
        return 100.0
    if "moola" in c_low:
        if planet and degree is not None and planet in MOOLATRIKONA_RANGES:
            mt_sign, min_d, max_d = MOOLATRIKONA_RANGES[planet]
            if sign and sign == mt_sign and (degree < min_d or degree > max_d):
                if planet in ("Sun", "Moon"):
                    return 75.0
                return 75.0 if sign in ODD_SIGNS else 62.5
        return 87.5
    if "own" in c_low or "svastha" in c_low or "house" in c_low:
        # Luminary Domicile Parity (Light on Life): Sun in Leo, Moon in Cancer = 75.0%
        if planet in ("Sun", "Moon") and sign in ("Leo", "Cancer"):
            return 75.0
        if sign and sign in ODD_SIGNS:
            return 75.0
        elif sign and sign in EVEN_SIGNS:
            return 62.5
        return 68.75
    if "great friend" in c_low or "adhi-mitra" in c_low:
        return 60.0
    if "friend" in c_low and "great" not in c_low:
        return 50.0
    if "neutral" in c_low or "sama" in c_low:
        return 37.5
    if "great enemy" in c_low or "adhi-shatru" in c_low:
        return 20.0
    if "enemy" in c_low:
        return 25.0
    if "debilit" in c_low or "neecha" in c_low:
        return 12.5

    if planet in ("Sun", "Moon") and sign in ("Leo", "Cancer") and "moola" not in c_low and "exalt" not in c_low:
        return 75.0

    if cleaned in DIGNITY_SCORE_MAP:
        return DIGNITY_SCORE_MAP[cleaned]
    for key, val in DIGNITY_SCORE_MAP.items():
        if key.lower() == c_low:
            return val

    return 37.5


def clamp(val: float, min_val: float, max_val: float) -> float:
    return max(min_val, min(max_val, val))


# -------------------------------------------------------------------------
# 1. Step 1: Base Dignity & Luminary Domicile Parity (Ruleset 1)
# -------------------------------------------------------------------------
def calculate_shadvarga_dignity(v_breakdown: Dict[str, Any], planet: str) -> float:
    """
    Parāśara's classical 20-point Shadvarga weights (BPHS Ch. 6, Verse 4):
    D1: 6.0, D9: 5.0, D3: 4.0, D2: 2.0, D12: 2.0, D30: 1.0 (Total = 20.0).
    Moolatrikona applies STRICTLY to D1; elsewhere, evaluates as Own Sign.
    Luminaries in Domicile evaluate to 75.0% parity.
    """
    SHADVARGA_WEIGHTS = {"D1": 6.0, "D9": 5.0, "D3": 4.0, "D2": 2.0, "D12": 2.0, "D30": 1.0}
    weighted_sum = 0.0
    for v_name, weight in SHADVARGA_WEIGHTS.items():
        score = v_breakdown[v_name]["score"]
        sign = v_breakdown[v_name]["sign"]
        dignity = v_breakdown[v_name]["dignity"]
        
        # Enforce D1-only restriction for Moolatrikona
        if v_name != "D1" and ("moola" in dignity.lower()):
            if planet in ("Sun", "Moon"):
                score = 75.0
            else:
                score = 75.0 if sign in ODD_SIGNS else 62.5
        elif planet in ("Sun", "Moon") and sign in ("Leo", "Cancer") and ("moola" not in dignity.lower()) and ("exalt" not in dignity.lower()):
            score = 75.0  # Domicile baseline for single-ruling luminaries
            
        weighted_sum += score * (weight / 20.0)
    return round(weighted_sum, 1)


# -------------------------------------------------------------------------
# 2. Step 4: Complete Lordship Agenda with Moolatrikona Predominance & Viparita (Ruleset 4)
# -------------------------------------------------------------------------
BASE_LORD_BONUS = {
    1: 20.0,   # Lagnesha (Protective captain)
    5: 15.0, 9: 15.0,  # Trikonas (Lakshmi grace & dharma)
    4: 5.0, 7: 5.0, 10: 5.0,  # Kendras (Pillars of action; 7th Lord per Phaladipika 1.17)
    2: 0.0,    # Neutral / Follows secondary house coloring
    3: -5.0,   # Trishadaya friction / restless desire
    11: -10.0, # Trishadaya acquisitiveness / functional malefic bias
    6: -15.0, 8: -15.0, 12: -15.0  # Dusthanas visiting non-dusthana
}

def _evaluate_single_house_agenda(h: int, placed_house: int, is_multi_viparita: bool = False) -> float:
    """Evaluates the base agenda of a single house, properly isolating Viparita states."""
    if h in (6, 8, 12):
        if placed_house == h:
            return 0.0   # Svakshetra: protects its own house, zero penalty
        if placed_house in (6, 8, 12):
            return 25.0 if is_multi_viparita else 15.0   # Viparita Reversal: dusthana lord trapped in another dusthana
        return -15.0     # Contaminating a non-dusthana house
    return BASE_LORD_BONUS.get(h, 0.0)

def calculate_lordship_modifier(
    ruled_houses: List[int], 
    planet: str, 
    placed_house: int, 
    lagna_idx: int,
    is_multi_viparita: bool = False
) -> float:
    """
    Calculates the net lordship agenda modifier applying Moolatrikona predominance
    (100% MT house / 50% Secondary house per Phaladipika 15.11).
    Exception: Lagnesha (H1) ALWAYS retains 100% potency (+20.0%), regardless of whether H1 is MT or non-MT.
    lagna_idx: 0-indexed integer (0 = Aries, ..., 11 = Pisces).
    """
    if not ruled_houses:
        return 0.0
        
    # Single-ruled planets (Sun, Moon)
    if len(ruled_houses) == 1 or planet in ("Sun", "Moon"):
        return _evaluate_single_house_agenda(ruled_houses[0], placed_house, is_multi_viparita)
    
    # Dual-ruled planets (Mars, Mercury, Jupiter, Venus, Saturn)
    mt_sign = MOOLATRIKONA_RANGES.get(planet, ("", 0, 0))[0]
    
    mt_house = None
    sec_house = None
    for h in ruled_houses:
        s_name = ZODIAC_SIGNS[(lagna_idx + h - 1) % 12]
        if s_name == mt_sign:
            mt_house = h
        else:
            sec_house = h
            
    if mt_house is None and ruled_houses:
        mt_house = ruled_houses[0]
        sec_house = ruled_houses[1] if len(ruled_houses) > 1 else ruled_houses[0]
    elif sec_house is None:
        sec_house = mt_house
        
    b_mt = _evaluate_single_house_agenda(mt_house, placed_house, is_multi_viparita)
    b_sec = _evaluate_single_house_agenda(sec_house, placed_house, is_multi_viparita)
    
    # Lagnesha (H1) exception: ALWAYS retains 100% potency (+20.0%)
    if sec_house == 1:
        return round(b_mt + b_sec, 2)
    elif mt_house == 1:
        return round(b_mt + 0.5 * b_sec, 2)
    else:
        return round(b_mt + 0.5 * b_sec, 2)


# -------------------------------------------------------------------------
# 3. Ruleset 8: Classical Lunar Benefic Window
# -------------------------------------------------------------------------
def calculate_lunar_nature_weight(moon_lon: float, sun_lon: float) -> float:
    """
    Ruleset 8: Classical Lunar Benefic Window (Light on Life & Phaladipika 2.27)
    Elongation: (Moon_lon - Sun_lon) % 360.
    Benefic Window: 48° (Shukla Panchami) to 300° (Krishna Dashami).
    Scales from +0.50 (at 48°/300°) to +1.00 (at 180° Full Moon).
    Malefic Window: outside 48° to 300°.
    Scales from -0.50 (at 48°/300°) to -1.00 (at 0°/360° New Moon).
    """
    elongation = (moon_lon - sun_lon) % 360.0
    if 48.0 <= elongation <= 300.0:
        if elongation <= 180.0:
            return round(0.50 + 0.50 * ((elongation - 48.0) / (180.0 - 48.0)), 2)
        else:
            return round(0.50 + 0.50 * ((300.0 - elongation) / (300.0 - 180.0)), 2)
    else:
        if elongation < 48.0:
            return round(-1.00 + 0.50 * (elongation / 48.0), 2)
        else:
            return round(-0.50 - 0.50 * ((elongation - 300.0) / (360.0 - 300.0)), 2)


# -------------------------------------------------------------------------
# 4. Ruleset 9: Aspect Vector Overrides, Variable Moon & Virupa Clamping
# -------------------------------------------------------------------------
def get_sambhanda(sender: str, receiver: str, sender_sign: str, receiver_sign: str) -> str:
    """Calculates compound Panchadha Maitri relationship between sender and receiver."""
    if sender in ("Rahu", "Ketu") or receiver in ("Rahu", "Ketu"):
        return "Neutral"
    if sender_sign not in ZODIAC_SIGNS or receiver_sign not in ZODIAC_SIGNS:
        return "Neutral"
    s_idx = ZODIAC_SIGNS.index(sender_sign)
    r_idx = ZODIAC_SIGNS.index(receiver_sign)
    nat = rel.get_natural_relationship(sender, receiver)
    temp = rel.get_temporary_relationship(s_idx, r_idx)
    return rel.get_compound_relationship(nat, temp)


def get_aspect_direction_vector(
    sender: str, 
    receiver: str, 
    contact_type: str, 
    sambhanda: str, 
    host_dispositor: Optional[str] = None,
    lunar_nature_weight: Optional[float] = None
) -> float:
    """
    Calculates the directional vector (+1.0 to -1.0) of an incoming aspect or conjunction
    based on classical Sambandha, variable Moon nature, and authentic Lajjitadi mechanics.
    """
    # 1. Classical Lajjitādi Mandatory Overrides (BPHS Ch. 45 & ASVA Vol II)
    if sender == "Saturn" and contact_type == "Conjunction":
        if receiver == "Rahu":
            return 0.2   # Shared Tamasic/Air affinity ("Shani-vat Rahu")
        if receiver == "Ketu":
            return 0.0   # Ascetic detachment / Neutral
        return -1.0  # Saturn conjunction ALWAYS starves co-present planets (Kshudhita)
        
    if sender == "Mars" and receiver == "Moon":
        return -1.0  # Mars gaze/contact agitates the Moon (Kshobhita)

    # 2. Variable Moon Arc Override (Ruleset 8)
    if sender == "Moon" and lunar_nature_weight is not None:
        return lunar_nature_weight

    # 3. Lunar Nodes (Rahu & Ketu) with Priority Exceptions
    if sender in ("Rahu", "Ketu"):
        if contact_type == "Conjunction":
            # 1. Universal Dispositor Immunity: Node never afflicts its host lord
            if host_dispositor and receiver == host_dispositor:
                return 0.5
            # 2. Ketu Jnana Combinations
            if sender == "Ketu":
                if receiver == "Jupiter":
                    return 0.3   # Guru-Ketu Jnana Yoga
                if receiver == "Mercury":
                    return 0.2   # Esoteric / Analytical discernment
                if receiver in ("Venus", "Saturn"):
                    return 0.0   # Ascetic detachment / Neutral
            # 3. Rahu Material Ambition Allies
            if sender == "Rahu":
                if receiver in ("Venus", "Mercury", "Saturn"):
                    return 0.2   # Rahu collaborates with friendly materialists
        return -1.0  # Default eclipsing / obsessive pressure

    # Symmetrical handling when receiver is a Node
    if receiver in ("Rahu", "Ketu") and contact_type == "Conjunction":
        if host_dispositor and sender == host_dispositor:
            return 0.5
        if receiver == "Ketu":
            if sender == "Jupiter":
                return 0.3
            if sender == "Mercury":
                return 0.2
            if sender in ("Venus", "Saturn"):
                return 0.0
        if receiver == "Rahu":
            if sender in ("Venus", "Mercury", "Saturn"):
                return 0.2

    # 4. Standard Sambandha Direction Vectors
    if "Great Friend" in sambhanda or "Friend" in sambhanda:
        return 1.0   # Delighting / Mudita Vector
    if "Great Enemy" in sambhanda or "Enemy" in sambhanda:
        return -1.0  # Starving / Agitating Vector
        
    return 0.0      # Neutral / Baseline footing


def calculate_aspect_shift(aspect_virupas: float, alertness: float, direction: float) -> float:
    ray_ratio = min(1.0, max(0.0, aspect_virupas / 60.0))
    return ray_ratio * alertness * direction * 20.0


# -------------------------------------------------------------------------
# 4.1 Continuous Vedic Aspect (Drishti) Line Graph Engine (Brihat Jataka 2.13)
# -------------------------------------------------------------------------
ANCHOR_DEGREES = [0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330, 360]

def get_aspect_anchor_points(planet: str) -> List[Tuple[float, float]]:
    """Returns the (degree, percentage) anchor points for a given planet per Brihat Jataka 2.13."""
    p = planet.strip().capitalize()
    anchors = []
    for d in ANCHOR_DEGREES:
        if d in (0, 30, 150, 300, 330, 360):
            pct = 0.0
        elif d == 180:
            pct = 100.0
        elif d in (90, 210):
            pct = 100.0 if p == "Mars" else 75.0
        elif d in (120, 240):
            pct = 100.0 if p in ("Jupiter", "Rahu", "Ketu") else 50.0
        elif d in (60, 270):
            pct = 100.0 if p == "Saturn" else 25.0
        else:
            pct = 0.0
        anchors.append((float(d), pct))
    return anchors

def calculate_continuous_drishti(planet: str, relative_deg: float) -> float:
    """Calculates exact aspect percentage at any intermediate degree using linear interpolation."""
    d = relative_deg % 360.0
    anchors = get_aspect_anchor_points(planet)
    
    for i in range(len(anchors) - 1):
        d1, p1 = anchors[i]
        d2, p2 = anchors[i + 1]
        if d1 <= d <= d2:
            if d2 == d1:
                return p1
            return p1 + ((d - d1) / (d2 - d1)) * (p2 - p1)
    return 0.0

def build_aspect_graph_data(
    source_planet: str,
    source_deg: float,
    aspected_planets: List[Dict[str, Any]]
) -> Dict[str, Any]:
    anchors = get_aspect_anchor_points(source_planet)
    
    # SVG Dimensions: Width 720 (x: 50 to 770), Height 140 (y: 180 = 0%, y: 40 = 100%)
    points_str = " ".join(
        f"{50 + (d / 360.0) * 720:.1f},{180 - (pct / 100.0) * 140:.1f}"
        for d, pct in anchors
    )
    
    anchor_nodes = []
    for d, pct in anchors:
        if d in (60, 90, 120, 180, 210, 240, 270):  # Active Parashari anchor points
            label = "Full (100%)" if pct == 100 else ("¾" if pct == 75 else ("½" if pct == 50 else ("¼" if pct == 25 else f"{int(pct)}%")))
            anchor_nodes.append({
                "deg": d,
                "pct": int(pct),
                "label": label,
                "cx": round(50 + (d / 360.0) * 720, 1),
                "cy": round(180 - (pct / 100.0) * 140, 1)
            })
            
    target_markers = []
    for tgt in aspected_planets:
        tgt_name = tgt["name"]
        tgt_abs_deg = float(tgt["longitude"])
        rel_deg = (tgt_abs_deg - source_deg) % 360.0
        pct = calculate_continuous_drishti(source_planet, rel_deg)
        
        x = 50 + (rel_deg / 360.0) * 720
        y = 180 - (pct / 100.0) * 140
        
        target_markers.append({
            "name": tgt_name,
            "symbol": tgt.get("symbol", tgt_name),
            "rel_deg": round(rel_deg, 1),
            "pct": round(pct, 1),
            "cx": round(x, 1),
            "cy": round(y, 1),
            "is_target": tgt.get("is_target", True)
        })
        
    return {
        "source_planet": source_planet,
        "polyline_points": points_str,
        "anchors": anchor_nodes,
        "targets": target_markers
    }


def calculate_conjunction_power(orb_degrees: float) -> Tuple[float, float, str]:
    """
    Evaluates conjunction power according to the canonical 3-Band Navāṁśa Rule (Ruleset 9):
    - Exact / Intimate: <= 3°20' (1 Navāṁśa) -> 60.0 Virūpas (100%)
    - Moderate: 3°20' to 10°00' -> 36.0 Virūpas (60%)
    - Wide (Same Sign): > 10°00' -> 15.0 Virūpas (25%)
    """
    clamped_orb = abs(orb_degrees)
    one_navamsha = 10.0 / 3.0  # 3.3333° (3°20')
    
    if clamped_orb <= (one_navamsha + 1e-7):
        return 60.0, 100.0, "Exact (Intimate)"
    elif clamped_orb <= (10.0 + 1e-7):
        return 36.0, 60.0, "Moderate"
    else:
        return 15.0, 25.0, "Wide"


def assemble_unified_graha_cockpit(
    p: str,
    p_d1: Dict[str, Any],
    step1_info: Dict[str, Any],
    step2_info: Dict[str, Any],
    step3_info: Dict[str, Any],
    step4_info: Dict[str, Any],
    functional_dignity_pct: float,
    sb_entry: Dict[str, Any],
    host_sb_entry: Dict[str, Any],
    vit_res: Dict[str, Any],
    calibrated_lajj: List[Dict[str, Any]],
    jagradaadi_map: Dict[str, Dict[str, Any]],
    baladi_map: Dict[str, Dict[str, Any]],
    d1_grahas: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Assembles the 3-Column Diagnostic Cockpit payload for a single planet.
    """
    # -------------------------------------------------------------------------
    # STAGE 1: Shadvarga Foundation Table (Weights: D1:6, D9:5, D3:4, D2:2, D12:2, D30:1)
    # -------------------------------------------------------------------------
    v_weights = {"D1": 6.0, "D9": 5.0, "D3": 4.0, "D2": 2.0, "D12": 2.0, "D30": 1.0}
    v_breakdown = step1_info.get("varga_breakdown", {})
    shadvarga_rows = []
    
    for v_code in ["D1", "D2", "D3", "D9", "D12", "D30"]:
        v_data = v_breakdown.get(v_code, {})
        shadvarga_rows.append({
            "varga": v_code,
            "weight": v_weights.get(v_code, 1.0),
            "sign": v_data.get("sign", "-"),
            "dignity": v_data.get("dignity", "Neutral"),
            "score_pct": v_data.get("score", 50.0)
        })

    # -------------------------------------------------------------------------
    # STAGE 2: Peer Influences (Bālādi Contextual, Jāgradādi Multiplicative)
    # -------------------------------------------------------------------------
    target_lon = float(p_d1.get("longitude", 0.0))
    peer_influences = []

    # Map Lajjitadi states by influencing planet
    lajj_index = {}
    for item in calibrated_lajj:
        for inf in item.get("influencing_planets", []):
            pl = inf.get("planet")
            if pl:
                lajj_index.setdefault(pl, []).append({
                    "state": item.get("base_state"),
                    "severity": item.get("severity", "Moderate")
                })

    # 1. Incoming Conjunctions
    for c in step3_info.get("conjunctions", []):
        src = c.get("from_planet") or c.get("planet") or c.get("source") or ""
        orb_deg = float(c.get("degree_diff", 0.0))
        c_virupas, c_pct, c_band = calculate_conjunction_power(orb_deg)
        src_bal = baladi_map.get(src, {})
        src_jag = jagradaadi_map.get(src, {})

        peer_influences.append({
            "influencer": src,
            "glyph": PLANET_GLYPHS.get(src, ""),
            "contact_type": "Conjunction",
            "contact_metric": f"{c_band} ({orb_deg:.1f}° orb)",
            "contact_virupas": c_virupas,
            "contact_power_pct": c_pct,
            # Bālādi is contextual physical maturity; does NOT multiply shift:
            "baladi": {
                "state": src_bal.get("state", "Yuva"),
                "efficiency_pct": src_bal.get("efficiency_pct", 100.0)
            },
            # Jāgradādi is the sole mathematical capacity multiplier:
            "jagradadi": {
                "state": src_jag.get("sanskrit", "Jāgrata"),
                "multiplier_pct": int(src_jag.get("multiplier", 1.0) * 100)
            },
            "lajjitadi_states": lajj_index.get(src, []),
            "dignity_shift_pct": float(c.get("shift", 0.0))
        })

    # 2. Incoming Aspects (Drishti >= 12.0 Virūpas)
    incoming_aspect_graphs = []
    
    for asp in step3_info.get("aspects", []):
        src = asp.get("from_planet") or asp.get("source") or ""
        raw_v = float(asp.get("virupas", 0.0))
        pct_power = round((raw_v / 60.0) * 100.0, 1)
        src_bal = baladi_map.get(src, {})
        src_jag = jagradaadi_map.get(src, {})

        peer_influences.append({
            "influencer": src,
            "glyph": PLANET_GLYPHS.get(src, ""),
            "contact_type": "Aspect (Dṛṣṭi)",
            "contact_metric": f"{raw_v:.1f} Virūpas",
            "contact_virupas": raw_v,
            "contact_power_pct": pct_power,
            "baladi": {
                "state": src_bal.get("state", "Yuva"),
                "efficiency_pct": src_bal.get("efficiency_pct", 100.0)
            },
            "jagradadi": {
                "state": src_jag.get("sanskrit", "Jāgrata"),
                "multiplier_pct": int(src_jag.get("multiplier", 1.0) * 100)
            },
            "lajjitadi_states": lajj_index.get(src, []),
            "dignity_shift_pct": float(asp.get("shift", 0.0))
        })

        # Cutoff: Only generate aspect curves for significant rays (raw_v >= 12.0)
        if src in d1_grahas and raw_v >= 12.0:
            src_lon = float(d1_grahas[src].get("longitude", 0.0))
            graph_data = build_aspect_graph_data(
                source_planet=src,
                source_deg=src_lon,
                aspected_planets=[{
                    "name": p,
                    "longitude": target_lon,
                    "symbol": f"{PLANET_GLYPHS.get(p, '')} {p}".strip(),
                    "virupas": raw_v,
                    "is_target": True
                }]
            )
            incoming_aspect_graphs.append({
                "source": src,
                "glyph": PLANET_GLYPHS.get(src, ""),
                "virupas": raw_v,
                "power_pct": pct_power,
                "graph": graph_data
            })

    # -------------------------------------------------------------------------
    # STAGE 3: Kinetic Muscle (Shadbala Quota)
    # -------------------------------------------------------------------------
    required_virupas_map = {
        "Sun": 390.0, "Moon": 360.0, "Mars": 300.0,
        "Mercury": 420.0, "Jupiter": 390.0, "Venus": 330.0, "Saturn": 300.0
    }
    tot_vir = float(sb_entry.get("Total_Virupas", sb_entry.get("total_virupas", 0.0)))
    req_vir = required_virupas_map.get(p, 360.0)
    shadbala_pct = float(sb_entry.get("Pct_Required_Total", round((tot_vir / req_vir) * 100.0, 1) if req_vir > 0 else 100.0))

    quad_dict = vit_res.get("quadrant", {}) if isinstance(vit_res.get("quadrant"), dict) else {}

    return {
        "planet": p,
        "glyph": PLANET_GLYPHS.get(p, ""),
        "sign": p_d1.get("sign", ""),
        "degree": float(p_d1.get("degree_0_to_30", float(p_d1.get("longitude", 0.0)) % 30.0)),
        "stage1_shadvarga": {
            "rows": shadvarga_rows,
            "base_dignity_pct": step1_info.get("weighted_dignity_pct", 50.0)
        },
        "stage2_environment": {
            "host_bedrock": {
                "planet": step2_info.get("host_planet", "-"),
                "status": step2_info.get("rescue_status", "Neutral"),
                "bonus_pct": step2_info.get("bonus_pct", 0.0)
            },
            "peer_influences": peer_influences,
            "functional_dignity_pct": functional_dignity_pct
        },
        "stage3_kinetic_muscle": {
            "total_virupas": tot_vir,
            "required_virupas": req_vir,
            "shadbala_pct": shadbala_pct,
            "is_sufficient": shadbala_pct >= 100.0
        },
        "stage3_aspect_graphs": incoming_aspect_graphs,
        "stage4_synthesis": {
            "vitality_score": float(vit_res.get("vitality_score", 5.0)),
            "archetype_title": quad_dict.get("archetype", "Pragmatic Executive"),
            "vitality_tier": vit_res.get("vitality_tier", "Resilient"),
            "summary_text": quad_dict.get("description", ""),
            "baladi": vit_res.get("baladi", {}),
            "deepthaadi": vit_res.get("deepthaadi", {}),
            "affliction_badges": vit_res.get("affliction_badges", [])
        }
    }


# -------------------------------------------------------------------------
# 5. Ruleset 6: Classical Baladi Output & Gandanta Knots
# -------------------------------------------------------------------------
def calculate_baladi_avastha(sign: str, degree_in_sign: float, longitude: Optional[float] = None) -> Dict[str, Any]:
    """
    Calculates Baladi Avastha (BPHS Ch. 45.3-4 / Phaladeepika 3.3) with odd/even sign reversal.
    Odd signs (Aries, Gemini, Leo, Libra, Sagittarius, Aquarius):
      0-6°: Bala (25%), 6-12°: Kumara (50%), 12-18°: Yuva (100%),
      18-24°: Vriddha (10%), 24-30°: Mrita (0%).
    Even signs (Taurus, Cancer, Virgo, Scorpio, Capricorn, Pisces):
      Inverts from death to birth:
      0-6°: Mrita (0%), 6-12°: Vriddha (10%), 12-18°: Yuva (100%),
      18-24°: Kumara (50%), 24-30°: Bala (25%).
    Also detects Rasi Sandhi (0°-1° / 29°-30°) and Gandanta knots (3°20' of water/fire junctions).
    """
    odd_signs = {"Aries", "Gemini", "Leo", "Libra", "Sagittarius", "Aquarius"}
    is_odd = sign in odd_signs
    deg = max(0.0, min(29.9999, float(degree_in_sign)))
    segment = int(deg // 6.0)  # 0 to 4
    segment = max(0, min(4, segment))

    if is_odd:
        states = ["Bala", "Kumara", "Yuva", "Vriddha", "Mrita"]
        efficiency = [0.25, 0.50, 1.00, 0.10, 0.00]
        sanskrit_terms = [
            "Bāla (Infant / Learning)",
            "Kumāra (Youth / Playful)",
            "Yuvā (Prime Adult / Master)",
            "Vṛddha (Elder / Waning)",
            "Mṛta (Dormant / Incapacitated)"
        ]
        degree_ranges = ["0°00' - 5°59'", "6°00' - 11°59'", "12°00' - 17°59'", "18°00' - 23°59'", "24°00' - 29°59'"]
    else:
        states = ["Mrita", "Vriddha", "Yuva", "Kumara", "Bala"]
        efficiency = [0.00, 0.10, 1.00, 0.50, 0.25]
        sanskrit_terms = [
            "Mṛta (Dormant / Incapacitated)",
            "Vṛddha (Elder / Waning)",
            "Yuvā (Prime Adult / Master)",
            "Kumāra (Youth / Playful)",
            "Bāla (Infant / Learning)"
        ]
        degree_ranges = ["0°00' - 5°59'", "6°00' - 11°59'", "12°00' - 17°59'", "18°00' - 23°59'", "24°00' - 29°59'"]

    state_name = states[segment]

    # Rasi Sandhi check (0.0°-1.0° or 29.0°-30.0°)
    is_sandhi = (deg < 1.0 or deg >= 29.0)
    sandhi_badge = "⚠️ Rāśi Sandhi (Border Degree)" if is_sandhi else None

    # Gandanta check (within 3°20' = 3.3333° of water/fire junctions)
    sign_idx = ZODIAC_SIGNS.index(sign) if sign in ZODIAC_SIGNS else 0
    abs_lon = (sign_idx * 30.0 + deg) if longitude is None else longitude
    abs_lon = abs_lon % 360.0

    is_gandanta = False
    if (abs_lon >= (356.0 + 40.0/60.0) or abs_lon <= (3.0 + 20.0/60.0)):
        is_gandanta = True
    elif ((116.0 + 40.0/60.0) <= abs_lon <= (123.0 + 20.0/60.0)):
        is_gandanta = True
    elif ((236.0 + 40.0/60.0) <= abs_lon <= (243.0 + 20.0/60.0)):
        is_gandanta = True

    gandanta_badge = "🌊🔥 Gaṇḍānta (Karmic Knot)" if is_gandanta else None

    return {
        "state": state_name,
        "segment": segment,
        "degree_range": degree_ranges[segment],
        "efficiency_factor": efficiency[segment],
        "efficiency_pct": int(efficiency[segment] * 100),
        "sanskrit_term": sanskrit_terms[segment],
        "is_odd_sign": is_odd,
        "is_sandhi": is_sandhi,
        "sandhi_badge": sandhi_badge,
        "is_gandanta": is_gandanta,
        "gandanta_badge": gandanta_badge
    }


def calculate_deepthaadi_avastha(
    planet: str,
    sign: str,
    dignity_name: str,
    is_retrograde: bool = False,
    is_combust: bool = False,
    is_war_loser: bool = False,
    war_opponent: Optional[str] = None
) -> Dict[str, Any]:
    """
    Calculates Deepthaadi Avastha (Innate Mental Mood) based on Saravali Ch. 5
    and Richard Fish & Ryan Kurczak 'The Art and Science of Vedic Astrology, Vol 2', Ch. 4 (pp. 50-51).

    The 9 Canonical States from Saravali:
    1. Nipeedita (Harmed): Defeated in planetary war (Graha Yuddha).
    2. Vikala (Mutilated): Combust with the Sun (within solar orb).
    3. Bhita (Alarmed): In the sign of its fall (Debilitated).
    4. Deeptha (Radiant): In its exaltation sign.
    5. Swastha (Confident): In its own sign or Moolatrikona.
    6. Sakta (Strong): Retrograde with bright rays / high horsepower.
    7. Pramudita (Joyous Mood): In the sign of a friend (BPHS 45.7).
    8. Khala (Sorrowful / Mischievous): In an enemy sign.
    9. Santa (Peaceful / Serene): In a neutral sign or benefic varga.
    """
    d_low = (dignity_name or "").lower()

    if is_war_loser:
        opp_str = f" via {war_opponent}" if war_opponent else ""
        return {
            "state": "Nipeedita (Harmed)",
            "sanskrit": "Nipeedita",
            "english": "Harmed",
            "icon": "⚔️",
            "badge": f"⚔️ Nipeedita (War Defeat{opp_str})",
            "meaning": "Defeated in a close planetary war; bruised and obstructed, requiring recuperation before manifesting results.",
            "condition": f"Defeated by {war_opponent} in Graha Yuddha" if war_opponent else "Defeated in Graha Yuddha"
        }
    elif is_combust and planet not in ["Sun", "Rahu", "Ketu"]:
        return {
            "state": "Vikala (Mutilated)",
            "sanskrit": "Vikala",
            "english": "Mutilated",
            "icon": "🔥",
            "badge": "🔥 Vikala (Combust)",
            "meaning": "Combust with the Sun; outward material expression is scorched away, forcing energy to turn inward.",
            "condition": "Combust within solar orb (Astangata)"
        }
    elif "debilit" in d_low or "neecha" in d_low or "fall" in d_low:
        return {
            "state": "Bhita (Alarmed)",
            "sanskrit": "Bhita",
            "english": "Alarmed",
            "icon": "🔻",
            "badge": "🔻 Bhita (Alarmed)",
            "meaning": "In the sign of its fall; feels ungrounded, vulnerable, and exposed, demanding deep inner humility.",
            "condition": f"Debilitated in {sign}"
        }
    elif "exalt" in d_low or "paramoccha" in d_low or "uccha" in d_low:
        return {
            "state": "Deeptha (Radiant)",
            "sanskrit": "Deeptha",
            "english": "Radiant",
            "icon": "👑",
            "badge": "👑 Deeptha (Radiant)",
            "meaning": "In its exaltation sign; possesses sovereign nobility, supreme confidence, effortlessly radiating virtues.",
            "condition": f"Exalted in {sign}"
        }
    elif "own" in d_low or "moolatrikona" in d_low or "sva" in d_low:
        return {
            "state": "Swastha (Confident)",
            "sanskrit": "Swastha",
            "english": "Confident",
            "icon": "🏡",
            "badge": "🏡 Swastha (Confident)",
            "meaning": "In its own sign or prime mission; fully at home, self-reliant, comfortable, and in control of its resources.",
            "condition": f"In Own/Moolatrikona Sign ({sign})"
        }
    elif is_retrograde and planet not in ["Sun", "Moon", "Rahu", "Ketu"]:
        return {
            "state": "Sakta (Strong)",
            "sanskrit": "Sakta",
            "english": "Strong",
            "icon": "💪",
            "badge": "💪 Sakta (Strong)",
            "meaning": "Bright retrograde rays; high motional horsepower, persistent inner drive, and endurance.",
            "condition": "Retrograde motion with bright rays"
        }
    elif "friend" in d_low or "mitra" in d_low:
        return {
            "state": "Pramudita (Joyous)",
            "sanskrit": "Pramudita",
            "english": "Joyous Mood",
            "icon": "🤝",
            "badge": "🤝 Pramudita (Joyous)",
            "meaning": "In the sign of a friend; welcomed and honored as a valued guest in a supportive environment (BPHS 45.7).",
            "condition": f"In Friend's Sign ({sign})"
        }
    elif "enemy" in d_low or "shatru" in d_low:
        return {
            "state": "Khala (Sorrowful)",
            "sanskrit": "Khala",
            "english": "Sorrowful / Mischievous",
            "icon": "⚠️",
            "badge": "⚠️ Khala (Sorrowful)",
            "meaning": "In an enemy sign; feels defensive, facing environmental friction and demanding stubborn effort.",
            "condition": f"In Enemy's Sign ({sign})"
        }
    else:
        return {
            "state": "Santa (Peaceful)",
            "sanskrit": "Santa",
            "english": "Peaceful",
            "icon": "🕊️",
            "badge": "🕊️ Santa (Peaceful)",
            "meaning": "Neutral footing; operates with steady, pragmatic composure without extreme bias.",
            "condition": f"In Neutral Sign ({sign})"
        }


def calculate_jagradaadi_avastha(
    planet: str,
    sign: str,
    natural_dignity: str
) -> Dict[str, Any]:
    """
    Calculates Jagradaadi Avastha (Alertness & House Management Capacity)
    per Richard Fish & Ryan Kurczak 'The Art and Science of Vedic Astrology, Vol 2', Ch. 10 (pp. 136-139).

    Three States based on Natural Planetary Dignity:
    1. Jagrat (Awake - 1.00): Exalted, Moolatrikona, or Own Sign.
       - Full capacity (100%) to manage and produce house affairs.
       - Full impact (100%) when causing Lajjitaadi avasthas on other planets.
    2. Svapna (Sleepy - 0.50): Friend's or Neutral Sign.
       - Half capacity (50%) to manage house affairs.
       - Half impact (50%) when causing Lajjitaadi avasthas on other planets.
    3. Sushupti (Asleep - 0.10): Enemy's or Debilitated Sign.
       - Minimal capacity (10%) to manage house affairs; cannot sustain results alone.
       - Sluggish / muted impact (10%) when causing Lajjitaadi avasthas on other planets.
    """
    d_low = (natural_dignity or "").lower()

    if any(k in d_low for k in ["exalt", "moola", "own", "paramoccha", "uccha", "sva"]):
        return {
            "state": "Jagrat (Awake)",
            "sanskrit": "Jagrat",
            "english": "Awake",
            "icon": "👁️",
            "badge": "👁️ Jagrat (Awake - 100%)",
            "alertness": 1.00,
            "multiplier": 1.00,
            "capacity_pct": 100,
            "capacity_desc": "Full Capacity (100%)",
            "house_management": "Full capacity to manage and produce the affairs of its ruled houses; exerts full power in planetary interactions."
        }
    elif any(k in d_low for k in ["debilit", "enemy", "neecha", "shatru"]):
        return {
            "state": "Sushupti (Asleep)",
            "sanskrit": "Sushupti",
            "english": "Asleep / Slumbering",
            "icon": "💤",
            "badge": "💤 Sushupti (Asleep - 10%)",
            "alertness": 0.10,
            "multiplier": 0.10,
            "capacity_pct": 10,
            "capacity_desc": "Minimal Capacity (10%)",
            "house_management": "Cannot produce or manage house affairs alone; exerts minimal to sluggish impact in planetary interactions."
        }
    else:
        return {
            "state": "Svapna (Sleepy)",
            "sanskrit": "Svapna",
            "english": "Sleepy / Dreaming",
            "icon": "😴",
            "badge": "😴 Svapna (Sleepy - 50%)",
            "alertness": 0.50,
            "multiplier": 0.50,
            "capacity_pct": 50,
            "capacity_desc": "Half Capacity (50%)",
            "house_management": "Half capacity to produce and manage house affairs; exerts moderate impact in planetary interactions."
        }


def calibrate_lajjitadi_states(
    planet: str,
    sign: str,
    raw_lajjitadi_list: List[Dict[str, Any]],
    jagradaadi_map: Dict[str, Dict[str, Any]],
    self_jagradaadi: Dict[str, Any],
    d1_grahas: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Calibrates Lajjitaadi Avasthas by modulating each state with the alertness (Jagradaadi)
    and Aspect / Conjunction strength (Virupas) of the interacting planet, as formulated by
    Ryan Kurczak in Vol 2 (pp. 136-139) and Sage Parashara (BPHS Ch. 45).
    """
    calibrated = []
    graha_names = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
    self_mult = self_jagradaadi.get("multiplier", 0.50)

    p_d1 = d1_grahas.get(planet, {}) if d1_grahas else {}
    p_lon = p_d1.get("longitude", 0.0)
    p_sign = p_d1.get("sign", sign)

    for item in raw_lajjitadi_list:
        st = item.get("state", "") if isinstance(item, dict) else str(item)
        cond = item.get("condition", "") if isinstance(item, dict) else ""
        base_state = st.split(" ")[0].strip() if " " in st else st

        # Identify which planets are influencing this state
        found_influencers = [p for p in graha_names if p in cond and p != planet]

        # If no specific planet is in condition text, check if sign lord is the host
        if not found_influencers and ("enemy sign" in cond.lower() or "friend's sign" in cond.lower()):
            host_lord = rel.SIGN_LORDS.get(sign)
            if host_lord and host_lord != planet:
                found_influencers.append(host_lord)

        inf_details = []
        mult_values = []
        for inf_p in found_influencers:
            inf_jag = jagradaadi_map.get(inf_p, {})
            m = inf_jag.get("multiplier", 0.50)
            mult_values.append(m)

            # Determine connection mechanism and Virupas
            inf_d1 = d1_grahas.get(inf_p, {}) if d1_grahas else {}
            inf_sign = inf_d1.get("sign", "")
            inf_lon = inf_d1.get("longitude", 0.0)

            if inf_sign and inf_sign == p_sign:
                mechanism = "Conjunction"
                symbol = "☌"
                virupas = 60.0
            elif rel.SIGN_LORDS.get(p_sign) == inf_p:
                mechanism = "Sign Lord"
                symbol = "Lord"
                virupas = 60.0
            elif d1_grahas and inf_p in d1_grahas:
                v_asp = aspects.get_graha_drishti(inf_p, inf_lon, p_lon)
                virupas = round(float(v_asp), 1)
                mechanism = "Aspect"
                symbol = "👁"
            else:
                mechanism = "Conjunction" if "conjoined" in cond.lower() else "Aspect"
                symbol = "☌" if mechanism == "Conjunction" else "👁"
                virupas = 60.0 if mechanism == "Conjunction" else 30.0

            aspect_ratio = virupas / 60.0
            combined_force = round(aspect_ratio * m, 3)
            is_major = (virupas >= 30.0)

            inf_details.append({
                "planet": inf_p,
                "glyph": PLANET_GLYPHS.get(inf_p, inf_p),
                "mechanism": mechanism,
                "symbol": symbol,
                "virupas": virupas,
                "alertness_state": inf_jag.get("english", "Sleepy"),
                "alertness_sanskrit": inf_jag.get("sanskrit", ""),
                "alertness_pct": int(m * 100),
                "multiplier": m,
                "combined_force": combined_force,
                "combined_pct": round(combined_force * 100, 1),
                "is_major": is_major,
                "chip_label": f"{PLANET_GLYPHS.get(inf_p, inf_p)} {symbol} {virupas:.0f}v ({inf_jag.get('english', 'Sleepy')})"
            })

        # Sort influencers: Major contacts (conjunctions / higher virupas) first, then by combined force
        inf_details.sort(key=lambda x: (x["virupas"], x["combined_force"]), reverse=True)

        # Determine effective intensity based on influencer's Jagradaadi
        if base_state == "Garvita":
            effective_intensity = 1.00
            severity = "Peak (Regal Assurance)"
            badge = "👑 Garvita (Proud - Peak)"
            icon = "👑"
        elif inf_details:
            primary_inf = inf_details[0]
            base_intensity = primary_inf["multiplier"]
            # If self is Jagrat (Awake) and facing a negative state, self-stamina grants 25% resilience dampening (Kurczak p. 137)
            if self_mult == 1.00 and base_state in ["Kshudhita", "Kshobhita", "Lajjita", "Trushita"]:
                effective_intensity = round(base_intensity * 0.75, 2)
            else:
                effective_intensity = base_intensity

            inf_g = primary_inf["glyph"]
            inf_s = primary_inf["alertness_state"]
            inf_v = f"{primary_inf['virupas']:.0f}v"
            inf_sym = primary_inf["symbol"]

            if base_state == "Mudita":
                icon = "🟢"
                badge = f"🟢 Mudita (via {inf_g} {inf_sym} {inf_v} {inf_s})"
                severity = "Uplifting / Nourishing" if effective_intensity >= 0.8 else ("Warm / Steady" if effective_intensity >= 0.4 else "Subdued")
            elif base_state == "Kshudhita":
                icon = "🔴"
                badge = f"🔴 Kshudhita (via {inf_g} {inf_sym} {inf_v} {inf_s})"
                severity = "Acute / Severe" if effective_intensity >= 0.8 else ("Moderate / Bearable" if effective_intensity >= 0.4 else "Sluggish / Muted")
            elif base_state == "Kshobhita":
                icon = "🟠"
                badge = f"🟠 Kshobhita (via {inf_g} {inf_sym} {inf_v} {inf_s})"
                severity = "Intense Friction" if effective_intensity >= 0.8 else "Mild Agitation"
            elif base_state == "Lajjita":
                icon = "🟣"
                badge = f"🟣 Lajjita (via {inf_g} {inf_sym} {inf_v} {inf_s})"
                severity = "Acute Inhibitions" if effective_intensity >= 0.8 else "Mild Bashfulness"
            elif base_state == "Trushita":
                icon = "💧"
                badge = f"💧 Trushita (via {inf_g} {inf_sym} {inf_v} {inf_s})"
                severity = "Acute Thirst" if effective_intensity >= 0.8 else "Mild Yearning"
            else:
                icon = "⚪"
                badge = f"⚪ {base_state} (via {inf_g} {inf_sym} {inf_v} {inf_s})"
                severity = "Standard"
        else:
            effective_intensity = 0.50
            severity = "Moderate"
            icon = "⚪"
            badge = f"⚪ {st}"

        calibrated.append({
            "state": st,
            "base_state": base_state,
            "condition": cond,
            "icon": icon,
            "badge": badge,
            "effective_intensity": effective_intensity,
            "severity": severity,
            "influencing_planets": inf_details
        })

    return calibrated


def synthesize_psychological_narrative(
    planet: str,
    sign: str,
    deepthaadi: Dict[str, Any],
    jagradaadi: Dict[str, Any],
    calibrated_lajjitadi: List[Dict[str, Any]],
    functional_role: Optional[Dict[str, Any]] = None
) -> str:
    """
    Synthesizes a rich 2-3 sentence psychological reality diagnosis following
    Richard Fish & Ryan Kurczak 'The Art and Science of Vedic Astrology, Vol 2' (Chapters 4, 10 & 11).
    Integrates internal mood (Deepthaadi), management alertness (Jagradaadi), and outer social dynamics (Lajjitaadi).
    """
    d_state = deepthaadi.get("state", "Santa (Peaceful)")
    j_desc = jagradaadi.get("capacity_desc", "Full Capacity")

    # Sentence 1: Baseline mood and executive alertness
    s1 = f"Internally positioned in {d_state} within {sign}, operating with {j_desc} to manifest its portfolio."

    # Sentence 2: Relational complexes from Lajjitadi
    active_states = [c for c in calibrated_lajjitadi if "neutral" not in c.get("base_state", "").lower()]
    pos_states = [c for c in active_states if c.get("base_state") in ["Garvita", "Mudita"]]
    neg_states = [c for c in active_states if c.get("base_state") in ["Kshudhita", "Kshobhita", "Lajjita", "Trushita"]]

    pos_parts = []
    for c in pos_states:
        b = c.get("base_state")
        inf_names = [inf["planet"] for inf in c.get("influencing_planets", [])]
        inf_str = f" from {', '.join(inf_names)}" if inf_names else ""
        if b == "Garvita":
            pos_parts.append("stands tall with sovereign pride and regal self-assurance (Garvita)")
        elif b == "Mudita":
            pos_parts.append(f"enjoys nourishing validation and cooperative ease (Mudita){inf_str}")

    neg_parts = []
    for c in neg_states:
        b = c.get("base_state")
        inf_names = [f"{inf['planet']} ({inf['alertness_state']})" for inf in c.get("influencing_planets", [])]
        inf_str = f" via {', '.join(inf_names)}" if inf_names else ""
        if b == "Kshudhita":
            neg_parts.append(f"experiences resource starvation (Kshudhita){inf_str}, requiring steadfast commitments to overcome hesitation")
        elif b == "Kshobhita":
            neg_parts.append(f"faces internal friction and agitation (Kshobhita){inf_str}")
        elif b == "Lajjita":
            neg_parts.append(f"encounters bashfulness or self-doubt (Lajjita){inf_str} around asserting its desires")
        elif b == "Trushita":
            neg_parts.append(f"feels an emotional depletion or yearning thirst (Trushita){inf_str} in water signs")

    if pos_parts and neg_parts:
        s2 = f"While it {pos_parts[0]}, it simultaneously {neg_parts[0]}."
    elif pos_parts:
        s2 = f"Socially, it {pos_parts[0]}."
    elif neg_parts:
        s2 = f"Socially, it {neg_parts[0]}."
    else:
        s2 = "Socially, it operates in an undisturbed, peaceful baseline free of acute relational friction."

    # Sentence 3: Kurczak Vol 2 core developmental guidance per planet
    graha_advice = {
        "Sun": "Builds authentic authority through managing expectations and leading with healthy self-esteem without overcompensating.",
        "Moon": "Finds deep peace through emotional adaptability, accepting support, and maintaining genuine self-contentment.",
        "Mars": "Channels drive into constructive, principled action, avoiding rigid dogma or impetuous haste.",
        "Mercury": "Excels through curious exploration and adaptable intellect while avoiding nervous overthinking.",
        "Jupiter": "Expands wisdom and spiritual benevolence, anchored in genuine ethical dharma.",
        "Venus": "Cultivates graceful harmony and devoted discernment in partnerships, avoiding excessive reliance on outside counsel.",
        "Saturn": "Matures through patient endurance and steady discipline, transmuting hardship into enduring authority.",
        "Rahu": "Directs ambitious, unconventional worldly hunger into focused mastery while guarding against ideological illusions.",
        "Ketu": "Deepens inward discernment and spiritual detachment, cutting through worldly dogma to perceive core truth."
    }
    s3 = graha_advice.get(planet, "Cultivates balance and mastery across its natural significations.")

    return f"{s1} {s2} {s3}"


def classify_graha_archetype(
    effective_dignity: Optional[float] = None,
    effective_shadbala: Optional[float] = None,
    is_rescued: bool = False,
    is_node: bool = False,
    dignity_name: str = "",
    *,
    dignity_pct: Optional[float] = None,
    shadbala_pct: Optional[float] = None,
    is_neecha_bhanga: Optional[bool] = None,
    house_num: Optional[int] = None
) -> Dict[str, Any]:
    """
    Classifies a planet into the refined Behavioral Archetype Spectrum (+ Transmuted Hero / Simple Neecha Bhanga):
    Cross-references Moral Intent / Quality (Dignity) with Kinetic Power / Stamina (Shadbala).

    1. Royal Dignity (>= 75%):
       - High Muscle: The Generous King (Sovereign Monarch)
       - Balanced Muscle: The Noble Guardian (Constructive Sovereign)
       - Low Muscle: The Sincere Friend (Noble Intent / Low Muscle)
    2. High / Friendly Dignity (55% - 74%):
       - High Muscle: The Noble Guardian (Constructive Ally)
       - Balanced Muscle: The Capable Executive (Pragmatic Ally)
       - Low Muscle: The Quiet Supporter (Supportive Baseline)
    3. Neutral Dignity (35% - 54%):
       - High Muscle: The Pragmatic Executive (Tireless Champion)
       - Balanced Muscle: The Dutiful Realist (Steady Craftsman)
       - Low Muscle: The Modest Citizen (Quiet Baseline)
    4. Low Dignity (< 35%):
       - High Muscle: The Armed Dictator (Severe Hazard)
       - Balanced Muscle: The Embattled Striver (Strained Fighter)
       - Low Muscle: The Toothless Bully (Harmless Adversary)
    5. True Debilitation + Exalted/Fortified Host:
       - In Kendra/Kona: The Transmuted Hero (Alchemical Raja Yoga)
       - In Dusthana (6, 8, 12): Simple Neecha Bhanga (Overcoming Deficit)
    """
    if effective_dignity is None and dignity_pct is not None:
        effective_dignity = dignity_pct
    if effective_shadbala is None and shadbala_pct is not None:
        effective_shadbala = shadbala_pct
    if is_neecha_bhanga is not None:
        is_rescued = is_neecha_bhanga
    effective_dignity = 37.5 if effective_dignity is None else effective_dignity
    effective_shadbala = 100.0 if effective_shadbala is None else effective_shadbala

    simple_neecha_badge = None
    if is_rescued:
        if house_num in (6, 8, 12):
            simple_neecha_badge = "Simple Neecha Bhanga (Overcoming Deficit)"
        else:
            return {
                "archetype": "The Transmuted Hero",
                "badge": "✨ Transmuted Hero",
                "tier": "Alchemical Raja Yoga",
                "subtext": "Alchemical Rescue (Neecha Bhanga)",
                "description": "Initial vulnerability transformed by a noble host into profound resilience and hard-won wisdom.",
                "color": "#7c3aed",
                "bg": "#f3e8ff",
                "is_royal_dig": False,
                "is_high_dig": False,
                "is_high_dignity": True,
                "is_high_strength": (effective_shadbala >= 95.0)
            }

    # REFINED 4-TIER DIGNITY THRESHOLDS (Light on Life & Classical Panchadha Maitri)
    is_royal_dig = effective_dignity >= 75.0          # Exalted, Moolatrikona, Own Sign
    is_high_dig = 55.0 <= effective_dignity < 75.0     # Great Friend & Friend signs
    is_neutral_dig = 35.0 <= effective_dignity < 55.0  # Sama Kshetra / Neutral signs
    is_low_dig = effective_dignity < 35.0              # Enemy & Debilitated signs

    # KINETIC MUSCLE TIERS
    is_high_musc = effective_shadbala >= 110.0
    is_bal_musc = 88.0 <= effective_shadbala < 110.0
    is_low_musc = effective_shadbala < 88.0

    # 1. ROYAL DIGNITY (>= 75%)
    if is_royal_dig:
        if is_high_musc:
            archetype = "The Generous King"
            badge = "🌟 Generous King"
            tier = "Sovereign Monarch"
            subtext = "Peak Dignity + Peak Muscle"
            desc = "Sovereign nobility combined with vast executive horsepower; manifests lasting, magnificent triumphs."
            color = "#15803d"
            bg = "#dcfce7"
        elif is_bal_musc:
            archetype = "The Noble Guardian"
            badge = "🛡️ Noble Guardian"
            tier = "Constructive Sovereign"
            subtext = "Peak Dignity + Balanced Muscle"
            desc = "Flawless moral intentions with steady everyday capability; protects and enriches its domains."
            color = "#0284c7"
            bg = "#e0f2fe"
        else:
            archetype = "The Sincere Friend"
            badge = "🤝 Sincere Friend"
            tier = "Noble Intent / Low Muscle"
            subtext = "Peak Dignity + Low Muscle"
            desc = "Spiritual integrity and deep goodwill; provides harmony and peace, but lacks brute worldly output."
            color = "#4f46e5"
            bg = "#eef2ff"

    # 2. HIGH / FRIENDLY DIGNITY (55% - 74%)
    elif is_high_dig:
        if is_high_musc:
            archetype = "The Noble Guardian"
            badge = "🛡️ Noble Guardian"
            tier = "Constructive Ally"
            subtext = "High Quality + High Muscle"
            desc = "Welcomed guest equipped with robust executive drive; delivers reliable, honorable achievements."
            color = "#0284c7"
            bg = "#e0f2fe"
        elif is_bal_musc:
            archetype = "The Capable Executive"
            badge = "⚖️ Capable Executive"
            tier = "Pragmatic Ally"
            subtext = "High Quality + Balanced Muscle"
            desc = "Cooperative disposition with steady real-world stamina; operates with constructive ease."
            color = "#0f766e"
            bg = "#ccfbf1"
        else:
            archetype = "The Quiet Supporter"
            badge = "🕊️ Quiet Supporter"
            tier = "Supportive Baseline"
            subtext = "High Quality + Low Muscle"
            desc = "Friendly intentions operating with limited kinetic horsepower; thrives best in gentle environments."
            color = "#6366f1"
            bg = "#eef2ff"

    # 3. NEUTRAL DIGNITY (35% - 54%)
    elif is_neutral_dig:
        if is_high_musc:
            archetype = "The Pragmatic Executive"
            badge = "⚒️ Pragmatic Executive"
            tier = "Tireless Champion"
            subtext = "Neutral Quality + High Muscle"
            desc = "Unpretentious, highly productive powerhouse; fulfills duties through endurance and practical skill."
            color = "#0f766e"
            bg = "#ccfbf1"
        elif is_bal_musc:
            archetype = "The Dutiful Realist"
            badge = "⚖️ Dutiful Realist"
            tier = "Steady Craftsman"
            subtext = "Neutral Quality + Balanced Muscle"
            desc = "Pragmatic and balanced; delivers solid, reliable everyday results without drama."
            color = "#475569"
            bg = "#f1f5f9"
        else:
            archetype = "The Modest Citizen"
            badge = "🌾 Modest Citizen"
            tier = "Quiet Baseline"
            subtext = "Neutral Quality + Low Muscle"
            desc = "Low-profile and harmless; operates within familiar routines without grand worldly conquest."
            color = "#a16207"
            bg = "#fef9c3"

    # 4. LOW DIGNITY (< 35%)
    else:
        if is_high_musc:
            archetype = "The Armed Dictator"
            badge = "⚔️ Armed Dictator"
            tier = "Severe Hazard"
            subtext = "Low Quality + High Muscle"
            desc = "Rash or aggrieved disposition armed with forceful kinetic power; requires strict conscious discipline."
            color = "#b91c1c"
            bg = "#fee2e2"
        elif is_bal_musc:
            archetype = "The Embattled Striver"
            badge = "🌪️ Embattled Striver"
            tier = "Strained Fighter"
            subtext = "Low Quality + Balanced Muscle"
            desc = "Under persistent friction; requires hard labor and conscious vigilance to avert missteps."
            color = "#c2410c"
            bg = "#ffedd5"
        else:
            archetype = "The Toothless Bully"
            badge = "⛓️ Toothless Bully"
            tier = "Harmless Adversary"
            subtext = "Low Quality + Low Muscle"
            desc = "Strained disposition without the horsepower to execute its irritations; easily managed."
            color = "#854d0e"
            bg = "#fef3c7"

    res = {
        "archetype": archetype,
        "badge": badge,
        "tier": tier,
        "subtext": subtext,
        "description": desc,
        "desc": desc,
        "color": color,
        "bg": bg,
        "is_royal_dig": is_royal_dig,
        "is_high_dig": is_high_dig,
        "is_high_dignity": (is_royal_dig or is_high_dig),
        "is_high_strength": is_high_musc
    }
    if simple_neecha_badge:
        res["simple_neecha_badge"] = simple_neecha_badge
        res["neecha_bhanga_badge"] = simple_neecha_badge
    return res


def classify_graha_quadrant(
    dignity_pct: float,
    shadbala_pct: float,
    is_node: bool = False,
    is_rescued: bool = False,
    dignity_name: str = "",
    *,
    house_num: Optional[int] = None
) -> Dict[str, Any]:
    """Preserves backward compatibility while forwarding to the 9-tier archetype classifier."""
    return classify_graha_archetype(
        effective_dignity=dignity_pct,
        effective_shadbala=shadbala_pct,
        is_rescued=is_rescued,
        is_node=is_node,
        dignity_name=dignity_name,
        house_num=house_num
    )


TARA_GRAHAS = ["Mars", "Mercury", "Jupiter", "Venus", "Saturn"]


def detect_planetary_wars(
    grahas_data: Dict[str, Any],
    shadbala_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Dict[str, Any]]:
    """
    Detects Graha Yuddha (Planetary War) per Phaladeepika 4.2 & BPHS.

    Rules of Engagement:
    1. Only the 5 Tara Grahas engage in war: Mars, Mercury, Jupiter, Venus, Saturn.
       (Sun combusts, Moon occults, Rahu/Ketu swallow/shadow).
    2. Threshold: Residing in the SAME SIGN within <= 1°00' (60 arcminutes) of each other.
    3. Determination of Victor:
       - Venus Invariance: Venus NEVER loses a planetary war (peerless luminosity / Bahula-Ruchi).
       - For other pairs: The planet with the northern celestial latitude (higher numerical value) wins.
       - Fallback (if latitudes unavailable/equal): Higher Shadbala virupas / percentage wins.
         If still tied, natural brightness order: Jupiter > Mercury > Mars > Saturn.
    4. Consequences:
       - Victor (Jayi): war_mod = +0.30, inherits Combat Stain badge: '🏆 War Victor (Combat Stain: {loser})'
       - Defeated (Nipidita): war_mod = -0.60, badge: '⚔️ Nipidita (War Defeat via {winner})'
    """
    if not grahas_data:
        return {}

    war_results: Dict[str, Dict[str, Any]] = {}
    eligible = [p for p in TARA_GRAHAS if p in grahas_data]

    for i in range(len(eligible)):
        p1 = eligible[i]
        g1 = grahas_data[p1]
        s1 = g1.get("sign")
        d1 = float(g1.get("degree_0_to_30", g1.get("longitude", 0.0) % 30.0))
        lat1 = g1.get("latitude", g1.get("lat"))

        for j in range(i + 1, len(eligible)):
            p2 = eligible[j]
            g2 = grahas_data[p2]
            s2 = g2.get("sign")
            d2 = float(g2.get("degree_0_to_30", g2.get("longitude", 0.0) % 30.0))
            lat2 = g2.get("latitude", g2.get("lat"))

            if s1 != s2:
                continue

            deg_diff = abs(d1 - d2)
            if deg_diff <= 1.0:
                # Determine winner
                if p1 == "Venus":
                    winner, loser = p1, p2
                    reason = "Venus Invariance Rule (Supreme Natural Brilliance)"
                elif p2 == "Venus":
                    winner, loser = p2, p1
                    reason = "Venus Invariance Rule (Supreme Natural Brilliance)"
                else:
                    # Northern celestial latitude
                    if lat1 is not None and lat2 is not None and abs(float(lat1) - float(lat2)) > 0.001:
                        if float(lat1) > float(lat2):
                            winner, loser = p1, p2
                            reason = f"Northern Celestial Latitude ({float(lat1):+.2f}° vs {float(lat2):+.2f}°)"
                        else:
                            winner, loser = p2, p1
                            reason = f"Northern Celestial Latitude ({float(lat2):+.2f}° vs {float(lat1):+.2f}°)"
                    else:
                        sb1 = (shadbala_data or {}).get(p1, {})
                        sb2 = (shadbala_data or {}).get(p2, {})
                        v1 = float(sb1.get("Total_Virupas", sb1.get("Pct_Required_Total", 0.0)))
                        v2 = float(sb2.get("Total_Virupas", sb2.get("Pct_Required_Total", 0.0)))
                        if abs(v1 - v2) > 0.1:
                            if v1 > v2:
                                winner, loser = p1, p2
                                reason = f"Higher Shadbala Virupas ({v1:.1f}v vs {v2:.1f}v)"
                            else:
                                winner, loser = p2, p1
                                reason = f"Higher Shadbala Virupas ({v2:.1f}v vs {v1:.1f}v)"
                        else:
                            brightness_rank = {"Jupiter": 4, "Mercury": 3, "Mars": 2, "Saturn": 1}
                            if brightness_rank.get(p1, 0) >= brightness_rank.get(p2, 0):
                                winner, loser = p1, p2
                            else:
                                winner, loser = p2, p1
                            reason = "Natural Luminosity Order"

                war_results[winner] = {
                    "in_war": True,
                    "is_winner": True,
                    "is_loser": False,
                    "opponent": loser,
                    "war_mod": 0.30,
                    "badge": f"🏆 War Victor (Combat Stain: {loser})",
                    "reason": reason,
                    "orb_deg": round(deg_diff, 3),
                    "sign": s1,
                    "details": f"{winner} defeated {loser} in Graha Yuddha (orb: {deg_diff:.2f}° in {s1}) via {reason}."
                }
                war_results[loser] = {
                    "in_war": True,
                    "is_winner": False,
                    "is_loser": True,
                    "opponent": winner,
                    "war_mod": -0.60,
                    "badge": f"⚔️ Nipidita (War Defeat via {winner})",
                    "reason": reason,
                    "orb_deg": round(deg_diff, 3),
                    "sign": s1,
                    "details": f"{loser} defeated by {winner} in Graha Yuddha (orb: {deg_diff:.2f}° in {s1}) entering Nipidita Avastha."
                }

    return war_results


def calculate_graha_vitality(
    planet: str,
    sign: str,
    degree_in_sign: float,
    dignity_name: str,
    dignity_pct: float,
    host_planet: str,
    host_dignity_pct: float,
    host_shadbala_pct: float,
    planet_shadbala_pct: float,
    net_drishti_virupas: float = 0.0,
    conjunctions: Optional[List[str]] = None,
    lajjitadi_states: Optional[List[Any]] = None,
    is_retrograde: bool = False,
    is_combust: bool = False,
    is_node: bool = False,
    lagna_sign: str = "Leo",
    lagna_lord: Optional[str] = None,
    # New parameters for Graha Yuddha, Recursive Drishti (Option A), & Conjunction Orbs
    is_war_winner: bool = False,
    is_war_loser: bool = False,
    war_opponent: Optional[str] = None,
    war_badge: Optional[str] = None,
    conjunction_details: Optional[List[Dict[str, Any]]] = None,
    aspect_details: Optional[List[Dict[str, Any]]] = None,
    functional_role: Optional[Dict[str, Any]] = None,
    # New parameters for Deepthaadi, Jagradaadi, & Calibrated Lajjitaadi (Vol 2)
    deepthaadi: Optional[Dict[str, Any]] = None,
    jagradaadi: Optional[Dict[str, Any]] = None,
    calibrated_lajjitadi: Optional[List[Dict[str, Any]]] = None,
    psychological_narrative: Optional[str] = None,
    # New parameters for Functional Dignity & House Field integration
    functional_dignity_pct: Optional[float] = None,
    house_field_info: Optional[Dict[str, Any]] = None,
    sun_distance: Optional[float] = None,
    longitude: Optional[float] = None
) -> Dict[str, Any]:
    """
    Calibrated Net Functional Vitality calculation resolving architectural flaws:
    1. Replaces flat 1/5th average with true 9-Tier Quality vs Muscle dynamics.
    2. Enforces strict Neecha Bhanga exclusively for classical signs of fall.
    3. Factors Baladi biological efficiency (Phaladeepika 3.10).
    4. Dynamically tilts neutral signs based on host dispositor, benefic rays, and Lagnesha protection.
    5. Evaluates Rahu and Ketu through their dispositor proxy.
    6. Balances psychological feeling states (Lajjitadi) with physical stamina.
    7. Integrates Graha Yuddha (Planetary War): Nipidita (-0.60) / War Victor (+0.30) with Combat Stain.
    8. Integrates Recursive Drishti (Option A): Debilitated benefic rays dampened by 50% with distorted badge.
    9. Integrates Conjunction Dynamics: Nodal possession within 3°20' (Ketu suppression / Rahu obsession).
    10. Integrates Guru-Chāṇḍāla Yoga (Jupiter+Rahu taboo zeal vs Ketu+Jupiter jnana contemplation).
    11. Integrates Deeptādi Vikala Avasthā (mutilated/besieged by 2+ cruel malefics).
    """
    conjunctions = conjunctions or []
    lajjitadi_states = lajjitadi_states or []

    # 1. Baladi Avastha
    baladi = calculate_baladi_avastha(sign, degree_in_sign)
    efficiency = baladi["efficiency_factor"]

    # 2. Host Dispositor & Strict Debilitation Evaluation
    is_debilitated = (planet in TRUE_DEBILITATION_MAP and sign == TRUE_DEBILITATION_MAP[planet]) or \
                     ("debilit" in dignity_name.lower()) or ("neecha" in dignity_name.lower())
    is_self_hosted = (host_planet == planet)
    is_rescued = False
    effective_dignity = dignity_pct
    rescue_status = "Neutral Host Foundation"
    rescue_badge = "⚖️ Neutral Host"

    if is_node:
        affinity = 15.0 if ((planet == "Rahu" and sign in RAHU_STRONG_SIGNS) or (planet == "Ketu" and sign in KETU_STRONG_SIGNS)) else 0.0
        effective_dignity = clamp(host_dignity_pct * 0.85 + affinity, 15.0, 100.0)
        effective_shadbala = max(60.0, host_shadbala_pct * 0.90)
        rescue_status = f"Chhāyā Proxy via {host_planet}"
        rescue_badge = f"Reflects {host_planet}"
    elif is_self_hosted:
        rescue_status = "Self-Hosted / Domicile"
        rescue_badge = "🏡 Self-Hosted"
        effective_dignity = dignity_pct
        effective_shadbala = planet_shadbala_pct
    elif is_debilitated:
        if host_dignity_pct >= 62.5 and host_shadbala_pct >= 90.0:
            rescue_status = "Full Alchemical Rescue (Neecha Bhanga)"
            rescue_badge = "✨ Rescued (Neecha Bhanga)"
            effective_dignity = clamp(dignity_pct + 50.0 * (host_dignity_pct / 100.0), 20.0, 85.0)
            is_rescued = True
        elif host_dignity_pct >= 50.0:
            rescue_status = "Partially Rescued by Capable Host"
            rescue_badge = "✨ Partial Rescue"
            effective_dignity = clamp(dignity_pct + 25.0 * (host_dignity_pct / 100.0), 15.0, 65.0)
        elif host_dignity_pct < 25.0:
            rescue_status = "Unsaved / Strained Host"
            rescue_badge = "⚠️ Strained Host"
            effective_dignity = max(10.0, dignity_pct - 5.0)
        else:
            rescue_status = "Neutral Host Foundation"
            rescue_badge = "⚖️ Neutral Host"
            effective_dignity = dignity_pct
        effective_shadbala = planet_shadbala_pct
    else:
        if host_dignity_pct >= 60.0:
            if dignity_pct <= 25.0:
                effective_dignity = min(40.0, dignity_pct + 10.0 * (host_dignity_pct / 100.0))
                rescue_status = f"Stabilized by Exalted Host {host_planet}" if host_dignity_pct >= 85.0 else f"Stabilized by Fortified Host {host_planet}"
                rescue_badge = "🛡️ Fortified Host"
            else:
                effective_dignity = min(100.0, dignity_pct + 12.0 * (host_dignity_pct / 100.0))
                rescue_status = "Fortified by Dignified Host"
                rescue_badge = "🛡️ Fortified Host"
        elif host_dignity_pct < 25.0:
            rescue_status = "Slight Drag from Strained Host"
            rescue_badge = "⚠️ Strained Host"
            effective_dignity = max(10.0, dignity_pct - 6.0)
        else:
            rescue_status = "Neutral Host Foundation"
            rescue_badge = "⚖️ Neutral Host"
            effective_dignity = dignity_pct
        effective_shadbala = planet_shadbala_pct

    rescue_class = "neutral"
    if host_dignity_pct >= 85.0:
        rescue_class = "exalt"
    elif host_dignity_pct >= 65.0:
        rescue_class = "own"
    elif host_dignity_pct < 40.0:
        rescue_class = "debil"

    # Neutral Sign Tilting (Sama Kshetra)
    if "neutral" in dignity_name.lower() or "sama" in dignity_name.lower() or (35.0 <= dignity_pct <= 50.0):
        if net_drishti_virupas > 0:
            effective_dignity += min(12.0, (net_drishti_virupas / 35.0) * 10.0)
        for item in lajjitadi_states:
            st = (item.get("state", "") if isinstance(item, dict) else str(item)).lower()
            if "mudita" in st or "garvita" in st:
                effective_dignity += 4.0
                break
        effective_dignity = min(54.9, effective_dignity)

    # 2.5 Functional Dignity Integration (Layer 2: Psychological State)
    # ADR-006 & ADR-009: House field/lordship is never added to effective_dignity
    if functional_dignity_pct is not None:
        effective_dignity = functional_dignity_pct
    house_field_delta = float(house_field_info.get("bonus_pct", 0.0)) if house_field_info else 0.0
    h_num_val = house_field_info.get("house_num") if house_field_info else None

    # Transmuted Hero restriction: Kendra (1, 4, 7, 10) or Kona (1, 5, 9)
    is_kendra_or_kona = (h_num_val in (1, 4, 5, 7, 9, 10)) if h_num_val is not None else True
    is_rescued_raja_yoga = is_rescued and is_kendra_or_kona

    # 3. 9-Tier Behavioral Archetype Classification (Section 1.1)
    quad = classify_graha_archetype(
        effective_dignity=effective_dignity,
        effective_shadbala=planet_shadbala_pct,
        is_rescued=is_rescued_raja_yoga,
        is_node=is_node,
        dignity_name=dignity_name,
        house_num=h_num_val
    )

    # 4. Calibrated Functional Vitality Score (1.0 to 10.0)
    q_norm = effective_dignity / 10.0  # 1.0 to 10.0
    m_ratio = effective_shadbala / 100.0  # 1.0 = baseline (100%)

    if is_rescued_raja_yoga:
        base_vit = 5.5 + (q_norm - 5.5) * 0.8 + (m_ratio - 1.0) * 1.0 + 0.5
        base_vit = clamp(base_vit, 4.5, 9.0)
    elif is_rescued:
        base_vit = 5.0 + (q_norm - 5.0) * 0.7 + (m_ratio - 1.0) * 1.0
        base_vit = clamp(base_vit, 4.0, 7.5)
    elif q_norm >= 5.5:
        base_vit = 5.5 + (q_norm - 5.5) * 0.8 + (m_ratio - 1.0) * 1.2
    elif q_norm >= 3.5:
        base_vit = 5.0 + (q_norm - 3.5) * 0.5 + (m_ratio - 1.0) * 1.5
    else:
        q_deficit = 3.5 - q_norm
        if effective_shadbala >= 110.0:
            hazard_mult = min(1.3, 0.75 + 0.25 * m_ratio)
            base_vit = 3.8 - (q_deficit * hazard_mult) - (m_ratio - 1.0) * 1.0
        elif effective_shadbala < 88.0:
            base_vit = 3.5 - (q_deficit * 0.5) - max(0.0, 1.0 - m_ratio) * 0.5
        else:
            base_vit = 4.2 - (q_deficit * 0.6) + (m_ratio - 1.0) * 0.5

    # 5. Environmental Modifications (Option A Recursive Drishti & Conjunction Dynamics)
    processed_aspect_details = []
    if aspect_details:
        total_adj_virupas = 0.0
        for asp in aspect_details:
            from_p = asp.get("from_planet", asp.get("source", ""))
            vir = float(asp.get("virupas", 0.0))
            from_dig_pct = float(asp.get("from_dignity_pct", 50.0))
            from_dig_name = str(asp.get("from_dignity_name", ""))
            is_deb = asp.get("is_debilitated", (from_dig_pct <= 25.0) or ("debilit" in from_dig_name.lower()) or ("neecha" in from_dig_name.lower()))
            is_distorted = False
            badge = ""

            is_conj = "conjunction" in asp.get("type", "").lower()

            # Option A: Debilitated benefics (Jupiter, Venus) transmit distorted rays
            if from_p in ["Jupiter", "Venus"] and is_deb and not is_conj:
                is_distorted = True
                adj_vir = (vir * 0.5) if vir > 0 else vir  # 50% positive dampening
                if from_p == "Jupiter":
                    badge = "⚠️ Compromised Guidance / Dogmatic Light"
                else:
                    badge = "⚠️ Corrupted Indulgence / Compromised Harmony"
            else:
                adj_vir = vir

            if not is_conj:
                total_adj_virupas += adj_vir

            processed_aspect_details.append({
                "from_planet": from_p,
                "source": from_p,
                "raw_virupas": vir,
                "virupas": vir,
                "adjusted_virupas": adj_vir,
                "from_dignity_pct": from_dig_pct,
                "from_dignity_name": from_dig_name,
                "is_debilitated": is_deb,
                "is_distorted": is_distorted,
                "badge": badge,
                "type": asp.get("type", "Aspect (Drishti)"),
                "sambhanda": asp.get("sambhanda", ""),
                "direction": asp.get("direction", 0.0),
                "shift": asp.get("shift", 0.0),
                "impact": asp.get("impact", "")
            })
        drishti_mod = clamp(total_adj_virupas / 35.0, -1.0, 1.0) * 0.7
    else:
        drishti_mod = clamp(net_drishti_virupas / 35.0, -1.0, 1.0) * 0.7

    # Conjunction Dynamics, Nodal Possession & Classical Nodal Yogas
    conj_mod = 0.0
    node_mod = 0.0
    processed_conjunction_details = []

    is_guru_chandal = False
    guru_chandal_badge = None
    is_guru_ketu = False
    guru_ketu_badge = None
    is_grahan = False
    is_angaraka = False
    is_shrapit = False
    nodal_badges = []

    cruel_malefics_set = {"Saturn", "Mars", "Rahu", "Ketu", "Sun"}
    cruel_conjoined_names = []

    if conjunction_details:
        for c_item in conjunction_details:
            cp = c_item.get("planet", "")
            diff = float(c_item.get("degree_diff", 5.0))
            cp_sb = float(c_item.get("shadbala_pct", 100.0))
            band = "Exact (Intimate)" if diff <= (10.0 / 3.0) else ("Moderate" if diff <= 10.0 else "Wide")
            commands = (cp_sb > planet_shadbala_pct)

            if cp in cruel_malefics_set and cp != planet:
                cruel_conjoined_names.append(cp)

            # 1. Jupiter + Rahu: Guru-Chāṇḍāla Yoga
            if (planet == "Jupiter" and cp == "Rahu") or (planet == "Rahu" and cp == "Jupiter"):
                is_guru_chandal = True
                guru_chandal_badge = "⚡ Guru-Chāṇḍāla (Ideological Zeal / Ambition)"
                node_mod -= 0.20

            # 2. Jupiter + Ketu: Guru-Ketu Jñāna Yoga
            elif (planet == "Jupiter" and cp == "Ketu") or (planet == "Ketu" and cp == "Jupiter"):
                is_guru_ketu = True
                guru_ketu_badge = "🕉️ Jñāna Catalyst (Spiritual Discernment)"
                node_mod += 0.15
                if (planet == host_planet or cp == host_planet) and host_dignity_pct >= 60.0:
                    node_mod += 0.20

            # 3. Sun / Moon + Nodes: Grahan Yoga (Eclipse)
            elif (cp in ("Rahu", "Ketu") and planet in ("Sun", "Moon")) or (planet in ("Rahu", "Ketu") and cp in ("Sun", "Moon")):
                if diff <= 15.0:
                    is_grahan = True
                    luminary = planet if planet in ("Sun", "Moon") else cp
                    node_p = cp if cp in ("Rahu", "Ketu") else planet
                    badge = f"🌑 Grahan Yoga ({luminary} Eclipsed by {node_p})"
                    nodal_badges.append(badge)
                    if node_p == "Ketu" and diff <= (10.0 / 3.0):
                        efficiency *= 0.80  # biological/external suppression
                    node_mod -= 0.25 if diff <= (10.0 / 3.0) else 0.15

            # 4. Mars + Rahu: Angaraka Yoga
            elif (planet == "Mars" and cp == "Rahu") or (planet == "Rahu" and cp == "Mars"):
                is_angaraka = True
                badge = "🔥 Angaraka Yoga (Volatile Drive / High Engineering Friction)"
                nodal_badges.append(badge)
                node_mod -= 0.25 if diff <= 5.0 else 0.10

            # 5. Saturn + Rahu: Shrapit Yoga
            elif (planet == "Saturn" and cp == "Rahu") or (planet == "Rahu" and cp == "Saturn"):
                is_shrapit = True
                badge = "⛓️ Shrapit Yoga (Karmic Toil / Heavy Institutional Duty)"
                nodal_badges.append(badge)
                node_mod -= 0.25 if diff <= 5.0 else 0.10

            # 6. Ketu's Combinations with Non-Jupiter Planets
            elif (planet == "Mercury" and cp == "Ketu") or (planet == "Ketu" and cp == "Mercury"):
                badge = "💡 Jñāna Analysis (Mathematical & Systems Perception)"
                nodal_badges.append(badge)
                if (planet == host_planet or cp == host_planet) and host_dignity_pct >= 60.0:
                    node_mod += 0.20
                else:
                    node_mod += 0.10

            elif (planet == "Venus" and cp == "Ketu") or (planet == "Ketu" and cp == "Venus"):
                badge = "✨ Aesthetic Idealism (Ascetic Detachment / Subtle Arts)"
                nodal_badges.append(badge)
                if (planet == host_planet or cp == host_planet) and host_dignity_pct >= 60.0:
                    node_mod += 0.20
                else:
                    node_mod += 0.05

            elif (planet == "Mars" and cp == "Ketu") or (planet == "Ketu" and cp == "Mars"):
                badge = "⚡ Kujavat Ketu (Technical Precision / High Pitta Friction)"
                nodal_badges.append(badge)
                if (planet == host_planet or cp == host_planet) and host_dignity_pct >= 60.0:
                    node_mod += 0.20
                else:
                    node_mod -= 0.15 if diff <= 5.0 else 0.05

            # 7. Dispositor Protection: Node conjoined with its own Sign Lord
            elif (cp == host_planet or (planet == host_planet and cp in ("Rahu", "Ketu"))) and host_dignity_pct >= 60.0:
                node_mod += 0.20  # Magnifies host's constructive agenda

            # 8. Standard Nodal Dynamics for other planets
            elif cp == "Ketu":
                if diff <= (10.0 / 3.0):
                    efficiency *= 0.80  # biological/external suppression
                    node_mod -= 0.25
                elif diff <= 10.0:
                    conj_mod -= 0.15
            elif cp == "Rahu":
                if diff <= (10.0 / 3.0):
                    if host_dignity_pct >= 60.0 and host_shadbala_pct >= 90.0:
                        node_mod += 0.20  # constructive worldly amplification
                    else:
                        node_mod -= 0.35  # toxic obsession / delusion
                elif diff <= 10.0:
                    conj_mod -= 0.15
            elif cp in ["Jupiter", "Venus"]:
                conj_mod += 0.30
            elif cp == lagna_lord:
                conj_mod += 0.35
            elif cp in ["Saturn", "Mars"]:
                conj_mod -= 0.30
            elif cp in ["Rahu", "Ketu"] and diff > 10.0:
                conj_mod -= 0.10

            processed_conjunction_details.append({
                "planet": cp,
                "degree_diff": diff,
                "orb_band": band,
                "shadbala_pct": cp_sb,
                "commands": commands
            })
    else:
        for cp in conjunctions:
            if cp in cruel_malefics_set and cp != planet:
                cruel_conjoined_names.append(cp)

            if (planet == "Jupiter" and cp == "Rahu") or (planet == "Rahu" and cp == "Jupiter"):
                is_guru_chandal = True
                guru_chandal_badge = "⚡ Guru-Chāṇḍāla (Ideological Zeal / Ambition)"
                node_mod -= 0.20
            elif (planet == "Jupiter" and cp == "Ketu") or (planet == "Ketu" and cp == "Jupiter"):
                is_guru_ketu = True
                guru_ketu_badge = "🕉️ Jñāna Catalyst (Spiritual Discernment)"
                node_mod += 0.15
                if (planet == host_planet or cp == host_planet) and host_dignity_pct >= 60.0:
                    node_mod += 0.20
            elif (cp in ("Rahu", "Ketu") and planet in ("Sun", "Moon")) or (planet in ("Rahu", "Ketu") and cp in ("Sun", "Moon")):
                is_grahan = True
                luminary = planet if planet in ("Sun", "Moon") else cp
                node_p = cp if cp in ("Rahu", "Ketu") else planet
                badge = f"🌑 Grahan Yoga ({luminary} Eclipsed by {node_p})"
                nodal_badges.append(badge)
                node_mod -= 0.20
            elif (planet == "Mars" and cp == "Rahu") or (planet == "Rahu" and cp == "Mars"):
                is_angaraka = True
                badge = "🔥 Angaraka Yoga (Volatile Drive / High Engineering Friction)"
                nodal_badges.append(badge)
                node_mod -= 0.20
            elif (planet == "Saturn" and cp == "Rahu") or (planet == "Rahu" and cp == "Saturn"):
                is_shrapit = True
                badge = "⛓️ Shrapit Yoga (Karmic Toil / Heavy Institutional Duty)"
                nodal_badges.append(badge)
                node_mod -= 0.20
            elif (planet == "Mercury" and cp == "Ketu") or (planet == "Ketu" and cp == "Mercury"):
                badge = "💡 Jñāna Analysis (Mathematical & Systems Perception)"
                nodal_badges.append(badge)
                if (planet == host_planet or cp == host_planet) and host_dignity_pct >= 60.0:
                    node_mod += 0.20
                else:
                    node_mod += 0.10
            elif (planet == "Venus" and cp == "Ketu") or (planet == "Ketu" and cp == "Venus"):
                badge = "✨ Aesthetic Idealism (Ascetic Detachment / Subtle Arts)"
                nodal_badges.append(badge)
                if (planet == host_planet or cp == host_planet) and host_dignity_pct >= 60.0:
                    node_mod += 0.20
                else:
                    node_mod += 0.05
            elif (planet == "Mars" and cp == "Ketu") or (planet == "Ketu" and cp == "Mars"):
                badge = "⚡ Kujavat Ketu (Technical Precision / High Pitta Friction)"
                nodal_badges.append(badge)
                if (planet == host_planet or cp == host_planet) and host_dignity_pct >= 60.0:
                    node_mod += 0.20
                else:
                    node_mod -= 0.10
            elif (cp == host_planet or (planet == host_planet and cp in ("Rahu", "Ketu"))) and host_dignity_pct >= 60.0:
                node_mod += 0.20
            elif cp in ["Jupiter", "Venus"]:
                conj_mod += 0.30
            elif cp == lagna_lord:
                conj_mod += 0.35
            elif cp in ["Saturn", "Mars"]:
                conj_mod -= 0.30
            elif cp in ["Rahu", "Ketu"]:
                conj_mod -= 0.20

    # 4. Deeptādi Vikala Avasthā (Besieged by 2+ cruel malefics)
    is_vikala = False
    vikala_badge = None
    vikala_mod = 0.0
    if len(cruel_conjoined_names) >= 2 and planet not in ["Rahu", "Ketu"]:
        is_vikala = True
        vikala_badge = f"🩸 Vikala (Besieged by {', '.join(cruel_conjoined_names)})"
        vikala_mod = -0.30

    # ADR-006 & ADR-009 Decoupling:
    # Numeric environmental weather is driven strictly by conjunctions (Yuti).
    # Aspects (Dṛṣṭi) are already accounted for in Ṣaḍbala (Dṛk Bala) and Sambandha peer shift (Layer 2).
    # Lajjitādi states provide qualitative psychological feeling states.
    env_mod = clamp(conj_mod, -1.2, 1.2)

    # 6. Motional & Light Modifiers: Classical Sūrya Siddhānta Combustion (Ruleset 3)
    SS_COMBUSTION_ORBS = {
        "Mars": 17.0,
        "Jupiter": 11.0,
        "Saturn": 15.0,
        "Moon": 12.0,
        "Mercury": 12.0 if is_retrograde else 14.0,
        "Venus": 8.0 if is_retrograde else 10.0
    }
    is_budhaditya = False
    budhaditya_badge = None

    if sun_distance is not None and planet not in ("Sun", "Rahu", "Ketu"):
        orb_limit = SS_COMBUSTION_ORBS.get(planet, 8.0)
        if sun_distance < orb_limit:
            is_combust = True
            if sun_distance < 3.0:
                combust_mod = -0.50  # Deep combustion (< 3.0°)
            else:
                # Moderate combustion (3.0° to full orb)
                if planet in ("Mars", "Jupiter", "Saturn", "Moon"):
                    combust_mod = -0.25
                elif planet in ("Mercury", "Venus"):
                    combust_mod = -0.08 if is_retrograde else -0.15
                else:
                    combust_mod = -0.25
        else:
            is_combust = False
            combust_mod = 0.0

        # Budhāditya Illumination: Sun + Mercury separation 3.0°–14.0° without planetary war
        if planet == "Mercury" and 3.0 <= sun_distance <= 14.0 and not (is_war_winner or is_war_loser):
            is_budhaditya = True
            budhaditya_badge = "☀️ Budhāditya Illumination (Discriminative Intellect)"
    elif is_combust:
        combust_mod = -0.50
    else:
        combust_mod = 0.0

    # Lagneśa Sun Protection (Leo Lagna ONLY): combustion softened by 30%
    if is_combust and lagna_sign == "Leo":
        combust_mod = round(combust_mod * 0.70, 2)

    mot_mod = combust_mod

    # 7. Planetary War (Graha Yuddha) Modifier
    war_mod = 0.0
    if is_war_loser:
        war_mod = -0.60
        if not war_badge:
            war_badge = f"⚔️ Nipidita (War Defeat via {war_opponent})" if war_opponent else "⚔️ Nipidita (War Defeat)"
    elif is_war_winner:
        war_mod = 0.30
        if not war_badge:
            war_badge = f"🏆 War Victor (Combat Stain: {war_opponent})" if war_opponent else "🏆 War Victor"

    # 8. Psychological Feeling State (Lajjitadi & Alertness Modulation - ADR-009 & Vol 2)
    # Expressed primarily as qualitative badges, narrative interpretations, and neutral sign dynamic tilts.
    # Decoupled from numeric vitality score to prevent double-counting.
    psy_mod = 0.0
    has_garvita = False
    if calibrated_lajjitadi:
        for item in calibrated_lajjitadi:
            b_st = item.get("base_state", "")
            eff_int = float(item.get("effective_intensity", 1.0))
            if b_st == "Garvita":
                has_garvita = True
                psy_mod += 0.15 * eff_int
            elif b_st == "Mudita":
                psy_mod += 0.15 * eff_int
            elif b_st == "Kshudhita":
                psy_mod -= 0.15 * eff_int
            elif b_st == "Kshobhita":
                psy_mod -= 0.10 * eff_int
            elif b_st == "Lajjita":
                base_pen = 0.10 if has_garvita else 0.15
                psy_mod -= base_pen * eff_int
            elif b_st == "Trushita":
                psy_mod -= 0.10 * eff_int
    else:
        for item in lajjitadi_states:
            st = (item.get("state", "") if isinstance(item, dict) else str(item)).lower()
            if "garvita" in st:
                has_garvita = True
                psy_mod += 0.15
            elif "mudita" in st:
                psy_mod += 0.15
            elif "kshudhita" in st:
                psy_mod -= 0.15
            elif "kshobhita" in st:
                psy_mod -= 0.10
            elif "lajjita" in st:
                psy_mod -= (0.10 if has_garvita else 0.15)
            elif "trushita" in st:
                psy_mod -= 0.10
    psy_mod = clamp(psy_mod, -0.20, 0.20)

    # 9. Ascendant Functional Role Integration
    if functional_role is None and lagna_sign in ZODIAC_SIGNS:
        all_roles = calculate_functional_roles(lagna_sign)
        functional_role = all_roles.get(planet, {})
    elif functional_role is None:
        functional_role = {}

    fn_status = functional_role.get("status", "")
    is_functional_malefic = (fn_status == "Functional Malefic")
    is_trishadaya = functional_role.get("is_trishadaya", False)

    # Narrative synthesis update for High Dignity + High Muscle under Affliction / Functional Malefic
    if quad.get("archetype") == "The Generous King":
        if is_guru_chandal:
            quad["description"] = (
                f"High executive capability and expansive mobilization muscle (rules {functional_role.get('ruled_houses_str', 'H11')}), "
                f"harnessed to unorthodox, dogmatic, or ruthless ideological ambition (Guru-Chāṇḍāla). "
                f"Massive administrative scale carrying high risk of ethical blind spots."
            )
            quad["tier"] = "Ideological Mobilizer"
            quad["badge"] = "⚡ Ideological Mobilizer"
            quad["archetype"] = f"{quad['archetype']} (⚡ Ideological Mobilizer)"
            quad["desc"] = quad["description"]
        elif is_functional_malefic and is_trishadaya and is_vikala:
            quad["description"] = (
                f"High organizational competence and resource power (rules {functional_role.get('ruled_houses_str', '')}), "
                f"besieged by cruel planets into aggressive worldly appetite and intense friction."
            )
            quad["tier"] = "Embattled Executive"
            quad["badge"] = "⚡ Embattled Executive"
            quad["archetype"] = f"{quad['archetype']} (⚡ Embattled Executive)"
            quad["desc"] = quad["description"]

    # Section 1.2: Vitality Score Cleanup (Zero Double-Counting)
    # Aspect rays and conjunctions are factored into Functional Dignity (Layer 2).
    # PreScore strictly reflects physical and operational realities:
    pre_score = base_vit + combust_mod + war_mod + node_mod + vikala_mod
    final_score = 5.0 + (pre_score - 5.0) * (0.8 + 0.2 * efficiency)
    final_score = clamp(round(final_score, 1), 1.0, 10.0)

    if final_score >= 8.5:
        v_tier = "🌟 Sovereign"
        v_bg = "#fef3c7"; v_col = "#92400e"
    elif final_score >= 7.0:
        v_tier = "🟢 Capable"
        v_bg = "#dcfce7"; v_col = "#15803d"
    elif final_score >= 5.5:
        v_tier = "🟡 Resilient"
        v_bg = "#fef9c3"; v_col = "#854d0e"
    elif final_score >= 4.0:
        v_tier = "🟠 Strained"
        v_bg = "#ffedd5"; v_col = "#9a3412"
    else:
        v_tier = "🔴 Severe Hazard" if quad["archetype"] == "The Armed Dictator" else "🔴 Fragile"
        v_bg = "#fee2e2"; v_col = "#991b1b"

    raw_afflictions = [b for b in [guru_chandal_badge, guru_ketu_badge, vikala_badge, budhaditya_badge] + nodal_badges if b]
    seen_badges = set()
    affliction_badges = []
    for b in raw_afflictions:
        if b not in seen_badges:
            seen_badges.add(b)
            affliction_badges.append(b)

    # Detailed Step-by-Step Calculation Receipt (ADR-009 & Section 1.2)
    receipt_lines = [
        "🧮 VITALITY SCORE CALCULATION RECEIPT",
        "------------------------------------",
        f"1. Base Engine:          {base_vit:.1f} ({quad.get('archetype', 'Neutral')})",
        f"   • Moral Intent / Dignity: {effective_dignity:.1f}% ({dignity_name})",
    ]
    if functional_dignity_pct is not None:
        h_ter = house_field_info.get('terrain_type', '-') if house_field_info else '-'
        h_num = house_field_info.get('house_num', '-') if house_field_info else '-'
        receipt_lines.append(f"   • Functional Dignity:     {effective_dignity:.1f}% [Layer 2]")
    receipt_lines.extend([
        f"   • Kinetic Muscle / Power: {effective_shadbala:.1f}% of required",
        f"   • Host Dispositor:        {rescue_status}",
        f"2. Physical & Operational Modifiers:",
        f"   • Conjunctions (Yuti):    {conj_mod:+.1f} pts (Decoupled to Layer 2 Functional Dignity)",
        f"   • Aspect Vision (Dṛṣṭi):  {drishti_mod:+.1f} (Decoupled to Ṣaḍbala Dṛk Bala)",
    ])
    if deepthaadi and deepthaadi.get("badge"):
        receipt_lines.append(f"   • Deepthādi Mood:         {deepthaadi.get('badge')}")
    if jagradaadi and jagradaadi.get("badge"):
        receipt_lines.append(f"   • Jagradādi Alertness:    {jagradaadi.get('badge')}")
    if is_combust:
        receipt_lines.append(f"   • Combustion (Astangata): {combust_mod:+.1f} pts (Blinded by Sun)")
    if budhaditya_badge:
        receipt_lines.append(f"   • Solar Yoga:             {budhaditya_badge}")
    if is_war_winner or is_war_loser:
        receipt_lines.append(f"   • Planetary War (Yuddha): {war_mod:+.1f} pts ({'Victor' if is_war_winner else 'Defeated'})")
    if is_guru_chandal or is_guru_ketu or node_mod != 0.0:
        receipt_lines.append(f"   • Nodal Influence:        {node_mod:+.2f} pts")
    if is_vikala:
        receipt_lines.append(f"   • Besieged State (Vikala):{vikala_mod:+.2f} pts (2+ Cruel Planets)")
    if psy_mod != 0.0:
        receipt_lines.append(f"   • Psychological State:    {psy_mod:+.2f} (Decoupled to Lajjitādi Narrative)")
    actual_eff_pct = int(round(efficiency * 100))
    receipt_lines.extend([
        f"3. Biological Efficiency:   {actual_eff_pct}% ({baladi['state']} stage)",
        "------------------------------------",
        f"★ Final Actualized Vitality: ★ {final_score:.1f} / 10 ({v_tier})"
    ])
    receipt_text = "\n".join(receipt_lines)

    # Calculate equation parts representing the mathematical breakdown of vitality_score
    scale = 0.8 + 0.2 * efficiency
    combust_part = round(combust_mod * scale, 2)
    war_part = round(war_mod * scale, 2)
    node_part = round(node_mod * scale, 2)
    vikala_part = round(vikala_mod * scale, 2)

    parts = {}
    if combust_part != 0:
        parts["combustion"] = combust_part
    if war_part != 0:
        parts["planetary_war"] = war_part
    if node_part != 0:
        parts["nodal_influence"] = node_part
    if vikala_part != 0:
        parts["besieged_vikala"] = vikala_part

    base_part = round(final_score - sum(parts.values()), 2)
    equation_parts = {"base_engine": base_part, **parts}

    # Section 1.3: Subcaption Data Binding
    subcaption_intent_pct = round(effective_dignity, 1)
    subcaption_power_pct = round(effective_shadbala, 1)
    subcaption_text = f"Intent: {effective_dignity:.0f}% | Power: {effective_shadbala:.0f}%"

    calculation_receipt = {
        "base_vitality": round(base_vit, 1),
        "effective_dignity_pct": round(effective_dignity, 1),
        "house_field_delta_pct": round(house_field_delta, 1),
        "effective_shadbala_pct": round(effective_shadbala, 1),
        "env_mod": round(env_mod, 1),
        "drishti_mod": round(drishti_mod, 1),
        "conj_mod": round(conj_mod, 1),
        "combust_mod": round(combust_mod, 1),
        "war_mod": round(war_mod, 1),
        "node_mod": round(node_mod, 2),
        "vikala_mod": round(vikala_mod, 2),
        "psy_mod": round(psy_mod, 2),
        "efficiency_pct": actual_eff_pct,
        "final_score": final_score,
        "equation_parts": equation_parts,
        "receipt_text": receipt_text,
        "deepthaadi": deepthaadi,
        "jagradaadi": jagradaadi,
        "calibrated_lajjitadi": calibrated_lajjitadi,
        "psychological_narrative": psychological_narrative,
        "is_budhaditya": is_budhaditya,
        "budhaditya_badge": budhaditya_badge,
        "subcaption_intent_pct": subcaption_intent_pct,
        "subcaption_power_pct": subcaption_power_pct,
        "subcaption_text": subcaption_text,
        "host_shadbala_pct": round(host_shadbala_pct, 1)
    }

    return {
        "vitality_score": final_score,
        "vitality_tier": v_tier,
        "vitality_bg": v_bg,
        "vitality_col": v_col,
        "equation_parts": equation_parts,
        "effective_dignity_pct": round(effective_dignity, 1),
        "effective_shadbala_pct": round(effective_shadbala, 1),
        "host_shadbala_pct": round(host_shadbala_pct, 1),
        "subcaption_intent_pct": subcaption_intent_pct,
        "subcaption_power_pct": subcaption_power_pct,
        "subcaption_text": subcaption_text,
        "rescue_status": rescue_status,
        "rescue_desc": rescue_status,
        "rescue_badge": rescue_badge,
        "rescue_class": rescue_class,
        "is_rescued": is_rescued,
        "is_neecha_bhanga": is_rescued,
        "baladi": baladi,
        "quadrant": quad,
        "base_vitality": round(base_vit, 1),
        "env_mod": round(env_mod, 1),
        "drishti_mod": round(drishti_mod, 1),
        "mot_mod": round(mot_mod, 1),
        "combust_mod": round(combust_mod, 1),
        "psy_mod": round(psy_mod, 1),
        "war_mod": round(war_mod, 1),
        "node_mod": round(node_mod, 2),
        "vikala_mod": round(vikala_mod, 2),
        "is_guru_chandal": is_guru_chandal,
        "guru_chandal_badge": guru_chandal_badge,
        "is_guru_ketu": is_guru_ketu,
        "guru_ketu_badge": guru_ketu_badge,
        "is_budhaditya": is_budhaditya,
        "budhaditya_badge": budhaditya_badge,
        "is_grahan": is_grahan,
        "is_angaraka": is_angaraka,
        "is_shrapit": is_shrapit,
        "is_vikala": is_vikala,
        "vikala_badge": vikala_badge,
        "affliction_badges": affliction_badges,
        "functional_role": functional_role,
        "is_war_winner": is_war_winner,
        "is_war_loser": is_war_loser,
        "war_opponent": war_opponent,
        "war_badge": war_badge,
        "aspect_details": processed_aspect_details,
        "conjunction_details": processed_conjunction_details,
        "deepthaadi": deepthaadi,
        "jagradaadi": jagradaadi,
        "calibrated_lajjitadi": calibrated_lajjitadi or [],
        "psychological_narrative": psychological_narrative,
        "calculation_receipt": calculation_receipt
    }


def calculate_planetary_evaluation(
    vargas_data: Dict[str, Any],
    shadbala_data: Optional[Dict[str, Any]] = None,
    advanced_aspects: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Main evaluation engine. Calculates Vic DiCara's continuous Positive-to-Negative Scale,
    4-quadrant archetypes, master anchors of destiny, and audit equations for all planets.
    """
    if not vargas_data or "D1" not in vargas_data:
        return {}

    d1_data = vargas_data["D1"]
    d1_grahas = d1_data.get("grahas", {})
    d1_lagna = d1_data.get("lagna", {})
    lagna_sign = d1_lagna.get("sign", "Aries")
    lagna_idx = ZODIAC_SIGNS.index(lagna_sign) if lagna_sign in ZODIAC_SIGNS else 0
    functional_roles = calculate_functional_roles(lagna_sign)

    planets_eval_order = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
    
    # -------------------------------------------------------------------------
    # STEP 1: Calculate Base Shadvarga Dignity for all planets first
    # -------------------------------------------------------------------------
    shadvarga_scores: Dict[str, Dict[str, Any]] = {}

    for p in planets_eval_order:
        if p not in d1_grahas:
            continue
            
        v_breakdown = {}
        score_list = []
        
        for v_name in SHADVARGA_LIST:
            v_info = vargas_data.get(v_name, {})
            v_p = v_info.get("grahas", {}).get(p, {})
            sign = v_p.get("sign", "Aries")
            deg = float(v_p.get("degree_0_to_30", 0.0))
            dignity_str = v_p.get("dignity_breakdown", {}).get("final_dignity") or v_p.get("dignity") or "Neutral's Sign"
            score = get_dignity_score(dignity_str, planet=p, sign=sign, degree=deg)
            
            # Nodal adjustment for Rahu/Ketu
            if p == "Rahu" and sign in RAHU_STRONG_SIGNS:
                score = max(score, 75.0)
            elif p == "Ketu" and sign in KETU_STRONG_SIGNS:
                score = max(score, 75.0)
                
            v_breakdown[v_name] = {
                "sign": sign,
                "dignity": dignity_str,
                "score": round(score, 1)
            }
            score_list.append(score)
            
        weighted_score = calculate_shadvarga_dignity(v_breakdown, p)
        avg_score = sum(score_list) / max(1, len(score_list))
        base_centered = 2.0 * (weighted_score - 50.0)
        
        if weighted_score >= 60.0:
            predominance = "Shubhamsha Bahule"
            pred_desc = "Predominance of Auspicious Divisions (>60%)"
        elif weighted_score <= 40.0:
            predominance = "Kruramsha Bahule"
            pred_desc = "Predominance of Hostile Divisions (<40%)"
        else:
            predominance = "Madhyamsha"
            pred_desc = "Balanced / Moderate Divisions (40%–60%)"
            
        shadvarga_scores[p] = {
            "average_dignity_pct": round(avg_score, 1),
            "weighted_dignity_pct": round(weighted_score, 1),
            "base_centered_score": round(base_centered, 1),
            "predominance": predominance,
            "predominance_desc": pred_desc,
            "varga_breakdown": v_breakdown
        }

    planetary_wars = detect_planetary_wars(d1_grahas, shadbala_data)

    # Global Multi-Viparita Detection (Ruleset 4: >= 2 dusthana lords occupy dusthanas)
    dusthana_occupants = []
    for p_name in planets_eval_order:
        if p_name not in d1_grahas:
            continue
        p_s = d1_grahas[p_name].get("sign", "")
        p_s_idx = ZODIAC_SIGNS.index(p_s) if p_s in ZODIAC_SIGNS else 0
        h_num_check = (p_s_idx - lagna_idx) % 12 + 1
        if h_num_check in (6, 8, 12):
            p_rules = []
            for s_idx, s_name in enumerate(ZODIAC_SIGNS):
                if rel.SIGN_LORDS.get(s_name) == p_name:
                    p_rules.append((s_idx - lagna_idx) % 12 + 1)
            if any(r in (6, 8, 12) for r in p_rules):
                dusthana_occupants.append(p_name)
    has_multi_viparita = (len(dusthana_occupants) >= 2)

    # Precompute Jagradaadi and Baladi maps across all D1 planets for interaction calibration (Vol 2 Ch. 10 & 11)
    jagradaadi_map = {}
    baladi_map = {}
    for p_name in planets_eval_order:
        if p_name not in d1_grahas:
            continue
        p_d1_node = d1_grahas[p_name]
        p_sign_node = p_d1_node.get("sign", "Aries")
        p_nat_dig = p_d1_node.get("dignity_breakdown", {}).get("natural_dignity", "") or p_d1_node.get("dignity_breakdown", {}).get("final_dignity", "")
        jagradaadi_map[p_name] = calculate_jagradaadi_avastha(p_name, p_sign_node, p_nat_dig)
        p_deg_node = float(p_d1_node.get("degree_0_to_30", float(p_d1_node.get("longitude", 0.0)) % 30.0))
        baladi_map[p_name] = calculate_baladi_avastha(p_sign_node, p_deg_node)

    # -------------------------------------------------------------------------
    # Moon Illumination & Phase (Paksha Bala - BPHS 3.11 & Vol 1 p. 15)
    # -------------------------------------------------------------------------
    sun_d1_info = d1_grahas.get("Sun", {})
    moon_d1_info = d1_grahas.get("Moon", {})
    sun_lon_val = float(sun_d1_info.get("longitude", 0.0))
    moon_lon_val = float(moon_d1_info.get("longitude", 0.0))
    moon_elongation_val = (moon_lon_val - sun_lon_val) % 360.0
    moon_paksha_ratio = 1.0 - abs(moon_elongation_val - 180.0) / 180.0  # 1.0 = Full, 0.0 = New
    moon_illum_pct = round(moon_paksha_ratio * 100.0, 1)
    moon_is_waxing = (moon_elongation_val <= 180.0)
    moon_paksha_name = "Waxing (Shukla Paksha)" if moon_is_waxing else "Waning (Krishna Paksha)"
    moon_icon = "🌔" if moon_is_waxing else "🌘"

    # Continuous Gradual Illumination Spectrum (BPHS 28.10-11):
    # - 50% to 100% illumination: scales gradually from 0.0 to 1.0 (0% to +25% benefic terrain)
    # - 0% to 50% illumination: scales gradually from 1.0 to 0.0 (+25% to 0% malefic terrain)
    if moon_illum_pct >= 50.0:
        moon_gradual_factor = (moon_illum_pct - 50.0) / 50.0
        moon_light_type = "Bright Benefic Light (Pūrṇendu)" if moon_illum_pct >= 70.0 else "Waxing Intermediate Light"
        moon_terrain_spectrum = "bright_gradual"
    else:
        moon_gradual_factor = (50.0 - moon_illum_pct) / 50.0
        moon_light_type = "Dim/Dark Malefic Light (Kṣīṇendu)" if moon_illum_pct < 30.0 else "Waning Intermediate Light"
        moon_terrain_spectrum = "dark_gradual"

    moon_phase_summary = {
        "is_waxing": moon_is_waxing,
        "paksha": "Shukla" if moon_is_waxing else "Krishna",
        "paksha_name": moon_paksha_name,
        "elongation_deg": round(moon_elongation_val, 1),
        "illumination_pct": moon_illum_pct,
        "gradual_factor": round(moon_gradual_factor, 3),
        "light_type": moon_light_type,
        "terrain_spectrum": moon_terrain_spectrum,
        "badge": f"{moon_icon} {'Waxing' if moon_is_waxing else 'Waning'} ({moon_illum_pct:.0f}%)"
    }

    # -------------------------------------------------------------------------
    # STEPS 2, 3, 4 & SYNTHESIS: Full Evaluation per planet
    # -------------------------------------------------------------------------
    planets_result: Dict[str, Any] = {}

    for p in planets_eval_order:
        if p not in d1_grahas:
            continue
            
        p_d1 = d1_grahas[p]
        p_sign = p_d1.get("sign", "Aries")
        p_sign_idx = ZODIAC_SIGNS.index(p_sign) if p_sign in ZODIAC_SIGNS else 0
        p_lon = p_d1.get("longitude", 0.0)
        
        step1_info = shadvarga_scores[p]
        base_centered = step1_info["base_centered_score"]
        avg_dignity = step1_info["average_dignity_pct"]
        base_dignity = step1_info["weighted_dignity_pct"]
        d1_varga_info = step1_info.get("varga_breakdown", {}).get("D1", {})
        d1_score = d1_varga_info.get("score", 50.0)
        d1_dignity_name = d1_varga_info.get("dignity", "Neutral's Sign")
        d1_sign = d1_varga_info.get("sign", p_sign)
        d9_sign = step1_info.get("varga_breakdown", {}).get("D9", {}).get("sign", "")

        # ---------------------------------------------------------------------
        # Vargottama Potency (Ruleset 2: Tenacity vs Morality)
        # ---------------------------------------------------------------------
        is_vargottama = bool(d1_sign and d1_sign == d9_sign)
        is_debilitated_d1 = (p in TRUE_DEBILITATION_MAP and d1_sign == TRUE_DEBILITATION_MAP[p]) or \
                            ("debilit" in d1_dignity_name.lower()) or ("neecha" in d1_dignity_name.lower())
        
        sun_dist_val = min(abs(sun_lon_val - p_lon), 360.0 - abs(sun_lon_val - p_lon)) if p not in ("Sun", "Rahu", "Ketu") else 999.0
        is_deeply_combust = (p not in ("Sun", "Rahu", "Ketu") and sun_dist_val < 3.0)

        vargottama_bonus = 0.0
        vargottama_badge = None
        vargottama_floor = None

        if is_vargottama and not is_debilitated_d1 and not is_deeply_combust:
            is_auspicious = (d1_score >= 50.0) or any(k in d1_dignity_name.lower() for k in ["exalt", "own", "moola", "friend"])
            if is_auspicious:
                vargottama_bonus = 15.0
                vargottama_badge = "🌟 Vargottama Strength"
                vargottama_floor = 75.0
            else:
                vargottama_bonus = 0.0
                vargottama_badge = "⚡ Vargottama (Concentrated Tenacity)"
                vargottama_floor = None
        
        # ---------------------------------------------------------------------
        # STEP 2: The Dispositor Anchor & Host Rescue Rule
        # ---------------------------------------------------------------------
        sign_lord = p_d1.get("dignity_breakdown", {}).get("sign_lord")
        if not sign_lord or sign_lord not in rel.SIGN_LORDS.values():
            sign_lord = rel.SIGN_LORDS.get(p_sign, p)
            
        host_dignity = shadvarga_scores.get(sign_lord, {}).get("weighted_dignity_pct", 50.0)
        
        host_bonus = 0.0
        rescue_status = "Neutral Host Support"
        rescue_notes = f"Host {sign_lord} provides standard background stability."
        
        if sign_lord == p:
            rescue_status = "Domicile / Self-Hosted"
            rescue_notes = f"{p} resides in its own domicile ({p_sign}); self-reliant."
            host_bonus = 0.0
        else:
            if base_dignity < 50.0:
                if host_dignity >= 65.0:
                    host_bonus = round(25.0 * (host_dignity / 100.0), 1)
                    rescue_status = "Rescued by Fortified Host"
                    rescue_notes = (
                        f"Low base dignity ({base_dignity:.1f}%) is rescued by noble host {sign_lord} "
                        f"({host_dignity:.1f}% dignity). Converts vulnerability into enduring grit and authority."
                    )
                elif host_dignity >= 50.0:
                    host_bonus = round(12.0 * (host_dignity / 100.0), 1)
                    rescue_status = "Partially Supported by Friendly Host"
                    rescue_notes = f"Host {sign_lord} ({host_dignity:.1f}% dignity) buffers difficulty."
                elif host_dignity <= 25.0:
                    # Penalty strictly reserved for truly fallen/debilitated hosts (Light on Life)
                    host_bonus = -10.0
                    rescue_status = "Unsaved / Stressed Host"
                    rescue_notes = f"Host {sign_lord} is fallen/strained ({host_dignity:.1f}% dignity), offering no rescue."
                else:
                    # Neutral host provides a neutral baseline (0.0%), NOT -10%!
                    host_bonus = 0.0
                    rescue_status = "Neutral Host Foundation"
                    rescue_notes = f"Host {sign_lord} ({host_dignity:.1f}% dignity) provides standard neutral stability."
            else:
                if host_dignity >= 65.0:
                    host_bonus = 10.0
                    rescue_status = "Fortified by Dignified Host"
                    rescue_notes = f"Strong host {sign_lord} ({host_dignity:.1f}% dignity) reinforces positive manifestation."
                elif host_dignity <= 25.0:
                    host_bonus = -5.0
                    rescue_status = "Slight Drag from Stressed Host"
                    rescue_notes = f"Weak host {sign_lord} ({host_dignity:.1f}% dignity) creates slight drag on execution."
                else:
                    host_bonus = 0.0
                    rescue_status = "Neutral Host Foundation"
                    rescue_notes = f"Host {sign_lord} ({host_dignity:.1f}% dignity) provides standard neutral stability."

        step2_info = {
            "host_planet": sign_lord,
            "host_dignity_pct": round(host_dignity, 1),
            "rescue_status": rescue_status,
            "bonus_pct": round(host_bonus, 1),
            "notes": rescue_notes
        }

        # ---------------------------------------------------------------------
        # STEP 3: Conjunctions (Yuti) & Aspect Gradients (Drishti)
        # ---------------------------------------------------------------------
        conjunction_details = []
        aspect_details = []
        peer_shifts = []
        benefic_rays = 0.0
        malefic_pressure = 0.0

        for other_p in planets_eval_order:
            if other_p == p or other_p not in d1_grahas:
                continue
                
            o_d1 = d1_grahas[other_p]
            o_sign = o_d1.get("sign", "")
            o_lon = float(o_d1.get("longitude", 0.0))
            o_deg = float(o_d1.get("degree_0_to_30", o_lon % 30.0))
            my_deg = float(p_d1.get("degree_0_to_30", p_lon % 30.0))
            
            o_dig_info = shadvarga_scores.get(other_p, {}).get("varga_breakdown", {}).get("D1", {})
            o_dig_pct = float(o_dig_info.get("score", 50.0))
            o_dig_name = str(o_dig_info.get("dignity", "Neutral"))

            alertness = float(jagradaadi_map.get(other_p, {}).get("multiplier", 0.50))
            # Relationship must reflect how the RECEIVER (p) absorbs the incoming energy of other_p
            natural_rel = rel.get_natural_relationship(p, other_p)
            lunar_weight = calculate_lunar_nature_weight(moon_lon_val, sun_lon_val) if other_p == "Moon" else None

            # -----------------------------------------------------------------
            # 1. SAME SIGN -> CONJUNCTION (YUTI) ONLY (No Aspect Virūpas)
            # -----------------------------------------------------------------
            if o_sign == p_sign:
                deg_diff = abs(my_deg - o_deg)
                
                # Canonical 3-Band Navāṁśa Conjunction Scale (Ruleset 9)
                c_virupas, c_pct, c_band = calculate_conjunction_power(deg_diff)
                orb_factor = c_pct / 100.0
                band_label = c_band
                    
                direction = get_aspect_direction_vector(other_p, p, "Conjunction", natural_rel, sign_lord, lunar_weight)
                shift = orb_factor * alertness * direction * 20.0
                peer_shifts.append(shift)
                
                if shift > 0:
                    benefic_rays += shift
                elif shift < 0:
                    malefic_pressure += abs(shift)
                    
                rel_label = f"Bright Benefic ({lunar_weight:+.2f})" if other_p == "Moon" else natural_rel
                
                # Appended STRICTLY to conjunctions
                conjunction_details.append({
                    "planet": other_p,
                    "source": other_p,
                    "from_planet": other_p,
                    "type": f"Conjunction ({band_label})",
                    "degree_diff": round(deg_diff, 2),
                    "orb_band": band_label,
                    "orb_factor": orb_factor,
                    "power_pct": c_pct,
                    "sambhanda": rel_label,
                    "direction": direction,
                    "shift": round(shift, 1),
                    "impact": f"{shift:+.1f}% ({other_p} Conjunction in {p_sign})",
                    "from_dignity_pct": o_dig_pct,
                    "from_dignity_name": o_dig_name
                })

            # -----------------------------------------------------------------
            # 2. DIFFERENT SIGNS -> ASPECT (DRISHTI) ONLY
            # -----------------------------------------------------------------
            else:
                drishti_virupas = float(aspects.get_graha_drishti(other_p, o_lon, p_lon))
                
                # Ignore blind spots (0 Virūpas)
                if drishti_virupas < 0.5:
                    continue
                    
                ray_ratio = min(1.0, max(0.0, drishti_virupas / 60.0))
                direction = get_aspect_direction_vector(other_p, p, "Aspect (Drishti)", natural_rel, sign_lord, lunar_weight)
                shift = calculate_aspect_shift(drishti_virupas, alertness, direction)
                peer_shifts.append(shift)
                
                if shift > 0:
                    benefic_rays += shift
                elif shift < 0:
                    malefic_pressure += abs(shift)
                    
                rel_label = f"Bright Benefic ({lunar_weight:+.2f})" if other_p == "Moon" else natural_rel
                
                # Appended STRICTLY to aspects
                aspect_details.append({
                    "planet": other_p,
                    "source": other_p,
                    "from_planet": other_p,
                    "type": "Aspect (Drishti)",
                    "power_pct": round(ray_ratio * 100.0, 1),
                    "virupas": round(drishti_virupas, 1),
                    "sambhanda": rel_label,
                    "direction": direction,
                    "shift": round(shift, 1),
                    "impact": f"{shift:+.1f}% ({other_p} Aspect {drishti_virupas:.0f}v [{rel_label}])",
                    "from_dignity_pct": o_dig_pct,
                    "from_dignity_name": o_dig_name
                })

        # Net peer shift clamped to [-25%, +25%] per Ruleset 9
        clamped_aspect_net = clamp(round(sum(peer_shifts), 1), -25.0, 25.0)

        step3_info = {
            "benefic_rays_pct": round(benefic_rays, 1),
            "malefic_pressure_pct": round(-malefic_pressure, 1),
            "combustion_penalty_pct": 0.0,  # Decoupled to Layer 3 Vitality Score
            "nodal_penalty_pct": 0.0,       # Decoupled to Layer 3 Vitality Score
            "net_aspect_pct": round(clamped_aspect_net, 1),
            "conjunctions": conjunction_details,  # Separated
            "aspects": aspect_details,            # Separated
            "details": conjunction_details + aspect_details # Backward compatibility
        }

        # Calculate Layer 2: Functional Dignity %
        raw_func_dig = base_dignity + vargottama_bonus + host_bonus + clamped_aspect_net
        if vargottama_floor is not None:
            raw_func_dig = max(raw_func_dig, vargottama_floor)
        functional_dignity_pct = clamp(round(raw_func_dig, 1), 10.0, 100.0)

        # ---------------------------------------------------------------------
        # STEP 4: House Field & Dusthana Reversal Rule (Ruleset 4 & Ruleset 7)
        # ---------------------------------------------------------------------
        house_num = (p_sign_idx - lagna_idx) % 12 + 1
        
        # Check what houses this planet rules in D1
        ruled_houses = []
        for s_idx, s_name in enumerate(ZODIAC_SIGNS):
            if rel.SIGN_LORDS.get(s_name) == p:
                h_num = (s_idx - lagna_idx) % 12 + 1
                ruled_houses.append(h_num)

        is_dusthana_occupant = (house_num in [6, 8, 12])
        rules_dusthana = any(h in [6, 8, 12] for h in ruled_houses)
        is_viparita_candidate = is_dusthana_occupant and rules_dusthana

        # 4.1 Classical Parashari House Placement (Bhava Classification)
        HOUSE_CLASSIFICATIONS = {
            1: "Kendra & Trikona (Lagna)",
            2: "Dhana & Maraka Bhāva",
            3: "Upachaya & Bhrātṛ Bhāva",
            4: "Kendra (Sukha Bhāva)",
            5: "Trikona (Putra Bhāva)",
            6: "Dusthana & Upachaya (Ripu Bhāva)",
            7: "Kendra & Maraka (Kalatra Bhāva)",
            8: "Dusthana (Randhra Bhāva)",
            9: "Trikona (Dharma Bhāva)",
            10: "Kendra & Upachaya (Karma Bhāva)",
            11: "Upachaya (Lābha Bhāva)",
            12: "Dusthana (Vyaya Bhāva)"
        }
        house_type = HOUSE_CLASSIFICATIONS.get(house_num, f"House {house_num}")
        terrain_mod = 0.0
        terrain_type = house_type
        terrain_note = f"Occupying House {house_num} ({house_type})."

        # Bhava Madhya Proximity Check (Ruleset 7: within ±3.0° of house cusp for H2-H12)
        is_bhava_madhya = False
        bhava_madhya_badge = None
        if house_num in range(2, 13):
            cusps_list = d1_data.get("cusps", [])
            if cusps_list and len(cusps_list) >= 12:
                cusp_lon_val = float(cusps_list[house_num - 1].get("longitude", 0.0))
            else:
                cusp_lon_val = (float(d1_lagna.get("longitude", 0.0)) + (house_num - 1) * 30.0) % 360.0
            c_diff = min(abs(p_lon - cusp_lon_val), 360.0 - abs(p_lon - cusp_lon_val))
            if c_diff <= 3.0:
                is_bhava_madhya = True
                bhava_madhya_badge = "🎯 Bhava Madhya (Peak House Fruition)"

        # 4.2 House Lordship Modifiers (Ruleset 4: Moolatrikona Predominance & Viparita Tiers)
        is_multi_vip = bool(has_multi_viparita and is_viparita_candidate)
        viparita_badge = "⚡ Raja Sambandha Viparita" if is_multi_vip else None
        total_lordship_mod = calculate_lordship_modifier(ruled_houses, p, house_num, lagna_idx, is_multi_vip)
        expression_score = round(total_lordship_mod, 1)
        house_bonus = expression_score

        # Build math steps for formula string
        math_steps = [
            f"Base Dignity: {d1_score:.1f}% ({d1_dignity_name})",
            f"House Placement: House {house_num} ({house_type})",
            f"Lordship Agenda: {total_lordship_mod:+.1f}%"
        ]
        func_dig_formula_str = (
            f"Layer 2 Functional Dignity = {functional_dignity_pct:.1f}% | "
            f"Layer 4 Expression Mode = Lordship Agenda ({total_lordship_mod:+.1f}%) = {expression_score:+.1f}%"
        )

        house_type = f"{terrain_type} (House {house_num})"
        kendra_rank = None
        if house_num == 1:
            kendra_rank = "1st Rank (Lagna)"
        elif house_num == 10:
            kendra_rank = "2nd Rank (Midheaven / MC)"
        elif house_num == 7:
            kendra_rank = "3rd Rank (Descendant / DC)"
        elif house_num == 4:
            kendra_rank = "4th Rank (Nadir / IC)"

        house_notes = f"{terrain_note} Lordship modifier: {total_lordship_mod:+.1f}%."

        step4_info = {
            "house_num": house_num,
            "house_type": house_type,
            "terrain_type": terrain_type,
            "terrain_mod_pct": round(terrain_mod, 1),
            "terrain_dignity_pct": round(d1_score + terrain_mod, 1),
            "terrain_note": terrain_note,
            "lordship_mod_pct": round(total_lordship_mod, 1),
            "expression_score": expression_score,
            "kendra_rank": kendra_rank,
            "bonus_pct": round(house_bonus, 1),
            "viparita_yoga": "Multi-Viparita (Raja Sambandha)" if is_multi_vip else ("Viparita Reversal" if is_viparita_candidate else None),
            "is_multi_viparita": is_multi_vip,
            "viparita_badge": viparita_badge,
            "is_bhava_madhya": is_bhava_madhya,
            "bhava_madhya_badge": bhava_madhya_badge,
            "ruled_houses": ruled_houses,
            "functional_dignity_pct": round(functional_dignity_pct, 1),
            "math_formula": func_dig_formula_str,
            "math_steps": math_steps,
            "notes": house_notes
        }

        # ---------------------------------------------------------------------
        # FINAL SCALE SYNTHESIS & AUDIT TRAIL
        # ---------------------------------------------------------------------
        net_score = base_centered + host_bonus + clamped_aspect_net + house_bonus
        clamped_final = clamp(round(net_score, 1), -100.0, 100.0)

        # Expression Mode
        if clamped_final > 30.0:
            expr_mode = "High Expression (Constructive & Flourishing)"
            expr_class = "positive"
        elif clamped_final < -30.0:
            expr_mode = "Low Expression (Stressed & Disruptive)"
            expr_class = "negative"
        else:
            expr_mode = "Mixed Expression (Routine & Balanced)"
            expr_class = "mixed"

        # Required virupas according to BPHS / Kala methodology:
        required_virupas_map = {
            "Sun": 390.0,
            "Moon": 360.0,
            "Mars": 300.0,
            "Mercury": 420.0,
            "Jupiter": 390.0,
            "Venus": 330.0,
            "Saturn": 300.0
        }

        # Dynamically fetch the Host Dispositor's actual Shadbala percentage
        host_sb_entry = (shadbala_data or {}).get(sign_lord, {})
        if "Pct_Required_Total" in host_sb_entry:
            actual_host_sb_pct = float(host_sb_entry["Pct_Required_Total"])
        else:
            h_vir = float(host_sb_entry.get("Total_Virupas", host_sb_entry.get("total_virupas", 0.0)))
            h_req = required_virupas_map.get(sign_lord, 360.0)
            actual_host_sb_pct = round((h_vir / h_req) * 100.0, 1) if (h_req > 0 and h_vir > 0) else 100.0

        # Raw Strength (Virya / Bala)
        if p in ["Rahu", "Ketu"]:
            tot_virupas = float(host_sb_entry.get("Total_Virupas", host_sb_entry.get("total_virupas", 360.0))) * 0.90
            tot_rupas = tot_virupas / 60.0
            req_virupas = 360.0
            planet_shadbala_pct = round(actual_host_sb_pct * 0.90, 1)
            sb_ratio = round(planet_shadbala_pct / 100.0, 2)
            is_high_strength = (planet_shadbala_pct >= 95.0) or (sb_ratio >= 0.95)
        else:
            sb_entry = (shadbala_data or {}).get(p, {})
            if "Pct_Required_Total" in sb_entry:
                planet_shadbala_pct = float(sb_entry["Pct_Required_Total"])
                tot_virupas = float(sb_entry.get("Total_Virupas", sb_entry.get("total_virupas", 0.0)))
            else:
                tot_virupas = float(sb_entry.get("Total_Virupas", sb_entry.get("total_virupas", 0.0)))
                req_virupas = required_virupas_map.get(p, 360.0)
                planet_shadbala_pct = round((tot_virupas / req_virupas) * 100.0, 1) if req_virupas > 0 else 100.0

            tot_rupas = float(sb_entry.get("Total_Rupas", sb_entry.get("total_rupas", tot_virupas / 60.0)))
            req_virupas = required_virupas_map.get(p, 360.0)
            sb_ratio = round(planet_shadbala_pct / 100.0, 2)
            is_high_strength = (planet_shadbala_pct >= 100.0) or (tot_virupas >= req_virupas)

        # Inherent Planetary Dignity (Step 1 Shadvarga + Step 2 Host Rescue)
        # Dignity measures the internal mood/character (Avastha/Sthana),
        # which is strictly independent of external aspect pressure (Step 3) or house field (Step 4).
        net_dignity = base_centered + host_bonus
        d1_varga_info = step1_info.get("varga_breakdown", {}).get("D1", {})
        d1_score = d1_varga_info.get("score", 50.0)
        d1_dignity_name = d1_varga_info.get("dignity", "Neutral's Sign")
        avg_dignity = step1_info.get("average_dignity_pct", 50.0)
        weighted_dignity = step1_info.get("weighted_dignity_pct", 50.0)

        # A planet has High Dignity if:
        # 1. Its net dignity (base centered + host rescue) is positive (>= 0.0), OR
        # 2. Its average or weighted Shadvarga dignity is >= 50.0% (neutral or auspicious), OR
        # 3. It is exalted or in own sign in D1 (d1_score >= 80.0).
        is_high_dignity = (net_dignity >= 0.0) or (avg_dignity >= 50.0) or (d1_score >= 80.0)

        # 4-Quadrant Archetype Matrix & Expression Narrative
        if is_high_dignity and is_high_strength:
            arch_title = "Generous King with Armies"
            arch_icon = "🌟"
            if expr_class == "positive":
                arch_desc = "Noble, benevolent intentions AND the brute kinetic muscle to manifest massive, lasting blessings."
            elif expr_class == "mixed":
                arch_desc = "Noble, benevolent core character with strong executive muscle; operates in demanding or complex terrain requiring patient, balanced effort."
            else:
                arch_desc = "Benevolent, high-minded character possessing immense force, but facing severe environmental constraints or trials."
        elif not is_high_dignity and is_high_strength:
            arch_title = "Ruthless Armed Dictator"
            arch_icon = "💣"
            if expr_class == "negative":
                arch_desc = "Bitter, malevolent intentions AND the raw muscle to force real damage into reality (worst-case scenario)."
            elif expr_class == "mixed":
                arch_desc = "Demanding, defensive impulses with high physical drive; tempered into practical functionality by routine reality."
            else:
                arch_desc = "Intense worldly drive and aggressive power, channeled constructively through strong external support."
        elif is_high_dignity and not is_high_strength:
            arch_title = "Sincere Friend with No Money"
            arch_icon = "🕊️"
            if expr_class == "positive":
                arch_desc = "Wonderful heart and pure ethical vision; achieves gentle harmony despite limited physical horsepower."
            elif expr_class == "mixed":
                arch_desc = "Kind, supportive intentions with moderate resources; operates through gentle, steady cooperation."
            else:
                arch_desc = "Has goodwill and high ideals, but feels constrained or fatigued under heavy external demands."
        else:
            arch_title = "Toothless Bully Behind Bars"
            arch_icon = "🪰"
            if expr_class == "negative":
                arch_desc = "Petty, spiteful intentions, but powerless to execute them (easily mitigated nuisance)."
            elif expr_class == "mixed":
                arch_desc = "Vulnerable, easily frustrated disposition; lacks the stamina or authority to cause significant disturbance."
            else:
                arch_desc = "Stressed core disposition, but supported into harmless, quiet productivity by favorable external conditions."

        motional_factors = []
        if p_d1.get("is_retrograde"):
            motional_factors.append("Retrograde (Vakra - Maximum Kinetic Muscle)")
        if p_d1.get("is_combust"):
            motional_factors.append("Combust (Astangata - Stripped of Light)")
        if p == "Moon":
            if moon_paksha_ratio >= 0.6:
                motional_factors.append(f"Bright / Waxing Moon ({round(moon_paksha_ratio*100)}% Full)")
            else:
                motional_factors.append(f"Waning / Dim Moon ({round(moon_paksha_ratio*100)}% Full)")
        if p == "Sun" and house_num == 10:
            motional_factors.append("Supreme Dig Bala (Midday Apex / Noon)")

        strength_info = {
            "total_virupas": round(tot_virupas, 1),
            "shadbala_ratio": round(sb_ratio, 2),
            "strength_level": "High Strength" if is_high_strength else "Low Strength",
            "motional_factors": motional_factors,
            "is_proxy": p in ["Rahu", "Ketu"],
            "proxy_host": sign_lord if p in ["Rahu", "Ketu"] else None
        }

        # Human-readable calculation trail equation
        eq_parts = [
            {"label": "Base Shadvarga", "value": round(base_centered, 1), "op": ""},
            {"label": "Host Anchor", "value": round(host_bonus, 1), "op": "+" if host_bonus >= 0 else "-"},
            {"label": "Aspect Rays", "value": round(clamped_aspect_net, 1), "op": "+" if clamped_aspect_net >= 0 else "-"},
            {"label": "House Field", "value": round(house_bonus, 1), "op": "+" if house_bonus >= 0 else "-"}
        ]
        
        formula_str = (
            f"Final ({clamped_final:+.1f}%) = Base ({base_centered:+.1f}%) "
            f"{'+' if host_bonus >= 0 else '-'} Host ({abs(host_bonus):.1f}%) "
            f"{'+' if clamped_aspect_net >= 0 else '-'} Aspects ({abs(clamped_aspect_net):.1f}%) "
            f"{'+' if house_bonus >= 0 else '-'} House ({abs(house_bonus):.1f}%)"
        )

        human_readable = (
            f"1. Base Shadvarga dignity across D1, D2, D3, D9, D12, D30 averages {avg_dignity:.1f}% ({step1_info['predominance']}), "
            f"giving a centered base score of {base_centered:+.1f}%.\n"
            f"2. {rescue_notes} [{host_bonus:+.1f}%].\n"
            f"3. Aspect rays from benefics/malefics modify by {clamped_aspect_net:+.1f}%.\n"
            f"4. Placed in House {house_num} ({house_type}), adding {house_bonus:+.1f}%.\n"
            f"➔ Total Net Scale: {clamped_final:+.1f}% ({expr_mode})."
        )

        calc_trail = {
            "formula": formula_str,
            "equation_parts": eq_parts,
            "raw_result": round(net_score, 1),
            "clamped_result": clamped_final,
            "human_readable": human_readable
        }

        baladi_res = calculate_baladi_avastha(p_sign, p_d1.get("degree_0_to_30", p_lon % 30.0))
        quad_dig_pct = functional_dignity_pct if p not in ["Rahu", "Ketu"] else clamp(host_dignity * 0.85 + (15.0 if ((p == "Rahu" and p_sign in RAHU_STRONG_SIGNS) or (p == "Ketu" and p_sign in KETU_STRONG_SIGNS)) else 0.0), 10.0, 100.0)
        quad_sb_pct = sb_ratio * 100.0
        quad_res = classify_graha_quadrant(quad_dig_pct, quad_sb_pct, is_node=(p in ["Rahu", "Ketu"]))

        fn_role = functional_roles.get(p, {})
        step4_info["functional_role"] = fn_role

        # Build detailed conjunctions for calibrated vitality evaluation
        conj_details = []
        for other_p, other_d1 in d1_grahas.items():
            if other_p != p and other_d1.get("sign") == p_sign:
                o_deg = float(other_d1.get("degree_0_to_30", other_d1.get("longitude", 0.0) % 30.0))
                my_deg = float(p_d1.get("degree_0_to_30", p_lon % 30.0))
                deg_diff = abs(my_deg - o_deg)
                o_sb = 100.0
                if shadbala_data and other_p in shadbala_data:
                    o_sb = float(shadbala_data[other_p].get("Pct_Required_Total", 100.0))
                band = "Exact (Intimate)" if deg_diff <= (10.0 / 3.0) else ("Moderate" if deg_diff <= 10.0 else "Wide")
                conj_details.append({
                    "planet": other_p,
                    "degree_diff": round(deg_diff, 2),
                    "orb_band": band,
                    "shadbala_pct": o_sb,
                    "commands": (o_sb > (sb_ratio * 100.0))
                })

        war_info = planetary_wars.get(p, {})
        is_war_winner = war_info.get("is_winner", False)
        is_war_loser = war_info.get("is_loser", False)
        war_opponent = war_info.get("opponent")
        war_badge = war_info.get("badge")

        deepthaadi_res = calculate_deepthaadi_avastha(
            planet=p,
            sign=p_sign,
            dignity_name=d1_dignity_name,
            is_retrograde=bool(p_d1.get("is_retrograde")),
            is_combust=bool(p_d1.get("is_combust")),
            is_war_loser=is_war_loser,
            war_opponent=war_opponent
        )
        jagradaadi_res = jagradaadi_map.get(p, calculate_jagradaadi_avastha(p, p_sign, d1_dignity_name))

        raw_lajjitadi = p_d1.get("avasthas", {}).get("lajjitadi", [])
        calibrated_lajj = calibrate_lajjitadi_states(
            planet=p,
            sign=p_sign,
            raw_lajjitadi_list=raw_lajjitadi,
            jagradaadi_map=jagradaadi_map,
            self_jagradaadi=jagradaadi_res,
            d1_grahas=d1_grahas
        )

        psy_narrative = synthesize_psychological_narrative(
            planet=p,
            sign=p_sign,
            deepthaadi=deepthaadi_res,
            jagradaadi=jagradaadi_res,
            calibrated_lajjitadi=calibrated_lajj,
            functional_role=fn_role
        )

        vit_res = calculate_graha_vitality(
            planet=p,
            sign=p_sign,
            degree_in_sign=float(p_d1.get("degree_0_to_30", p_lon % 30.0)),
            dignity_name=d1_dignity_name,
            dignity_pct=d1_score,
            host_planet=sign_lord,
            host_dignity_pct=host_dignity,
            host_shadbala_pct=actual_host_sb_pct,
            planet_shadbala_pct=planet_shadbala_pct,
            net_drishti_virupas=clamped_aspect_net,
            conjunctions=[c.get("planet", c.get("source", "")) for c in step3_info.get("conjunctions", [])],
            lajjitadi_states=raw_lajjitadi,
            is_retrograde=bool(p_d1.get("is_retrograde")),
            is_combust=bool(p_d1.get("is_combust")),
            is_node=(p in ["Rahu", "Ketu"]),
            lagna_sign=lagna_sign,
            lagna_lord=rel.SIGN_LORDS.get(lagna_sign, "Mars"),
            is_war_winner=is_war_winner,
            is_war_loser=is_war_loser,
            war_opponent=war_opponent,
            war_badge=war_badge,
            conjunction_details=conj_details,
            aspect_details=step3_info.get("aspects", []),
            functional_role=fn_role,
            deepthaadi=deepthaadi_res,
            jagradaadi=jagradaadi_res,
            calibrated_lajjitadi=calibrated_lajj,
            psychological_narrative=psy_narrative,
            functional_dignity_pct=round(functional_dignity_pct, 1),
            house_field_info=step4_info,
            sun_distance=sun_dist_val,
            longitude=p_lon
        )

        # Resolve Nakshatra metadata for Subconscious Drive (Lunar Mansion)
        p_nak_name = p_d1.get("nakshatra")
        if not p_nak_name:
            n_idx = int(p_lon / (360.0 / 27.0)) % 27
            from jyotish.generate_jyotish import NAKSHATRAS
            p_nak_name = NAKSHATRAS[n_idx]

        nak_meta = get_nakshatra_metadata(p_nak_name)
        nak_ruler = p_d1.get("nakshatra_lord") or nak_meta.get("ruler", "Ketu")

        nakshatra_payload = {
            "name": nak_meta.get("name", p_nak_name),
            "deity": nak_meta.get("deity", "Universal Divine"),
            "ruler": nak_ruler,
            "nature": nak_meta.get("nature", "Sadharana / General"),
            "core_drive": nak_meta.get("core_drive", "Subconscious motivation and cosmic trajectory.")
        }

        # Consolidate all active badges for the planet
        planet_badges = []
        if vargottama_badge:
            planet_badges.append(vargottama_badge)
        if bhava_madhya_badge:
            planet_badges.append(bhava_madhya_badge)
        if viparita_badge:
            planet_badges.append(viparita_badge)
        if baladi_res.get("sandhi_badge"):
            planet_badges.append(baladi_res["sandhi_badge"])
        if baladi_res.get("gandanta_badge"):
            planet_badges.append(baladi_res["gandanta_badge"])
        for b in vit_res.get("affliction_badges", []):
            if b not in planet_badges:
                planet_badges.append(b)

        # Outgoing & Incoming Continuous Vedic Aspect Line Graphs (Brihat Jataka 2.13)
        all_chart_targets = [
            {
                "name": other_target,
                "longitude": float(d1_grahas[other_target].get("longitude", 0.0)),
                "symbol": f"{PLANET_GLYPHS.get(other_target, '')} {other_target[:2]}".strip(),
                "is_target": False
            }
            for other_target in planets_eval_order
            if other_target in d1_grahas
        ]

        outgoing_aspect_graph = build_aspect_graph_data(
            source_planet=p,
            source_deg=p_lon,
            aspected_planets=[
                t for t in all_chart_targets
                if t["name"] != p and calculate_continuous_drishti(p, (t["longitude"] - p_lon) % 360.0) > 0.0
            ]
        )

        incoming_aspect_graphs = {}
        for asp_item in aspect_details:
            src_p = asp_item.get("from_planet") or asp_item.get("source")
            raw_v = float(asp_item.get("virupas", 0.0))
            # Lower threshold to 12.0 Virupas to include noticeable minor aspects (Brihat Jataka)
            if src_p and src_p in d1_grahas and raw_v >= 12.0:
                src_lon = float(d1_grahas[src_p].get("longitude", 0.0))
                
                # FILTER ONLY THE TARGET PLANET (p)
                target_lon = float(d1_grahas[p].get("longitude", 0.0))
                rel_d = (target_lon - src_lon) % 360.0
                
                src_targets = [{
                    "name": p,
                    "longitude": target_lon,
                    "symbol": f"{PLANET_GLYPHS.get(p, '')} {p}".strip(),
                    "is_target": True
                }]
                
                # Build graph containing ONLY the target planet
                inc_g = build_aspect_graph_data(src_p, src_lon, src_targets)
                incoming_aspect_graphs[src_p] = inc_g
                asp_item["aspect_graph"] = inc_g

                # Sync to processed vitality aspect details
                for vit_asp in vit_res.get("aspect_details", []):
                    if (vit_asp.get("from_planet") == src_p) or (vit_asp.get("source") == src_p):
                        vit_asp["aspect_graph"] = inc_g

        cockpit_payload = assemble_unified_graha_cockpit(
            p=p,
            p_d1=p_d1,
            step1_info=step1_info,
            step2_info=step2_info,
            step3_info=step3_info,
            step4_info=step4_info,
            functional_dignity_pct=round(functional_dignity_pct, 1),
            sb_entry=sb_entry,
            host_sb_entry=host_sb_entry,
            vit_res=vit_res,
            calibrated_lajj=calibrated_lajj,
            jagradaadi_map=jagradaadi_map,
            baladi_map=baladi_map,
            d1_grahas=d1_grahas
        )

        planets_result[p] = {
            "planet": p,
            "glyph": PLANET_GLYPHS.get(p, ""),
            "sign": p_sign,
            "longitude": round(p_lon, 2),
            "net_scale_score": clamped_final,
            "expression_mode": expr_mode,
            "expression_class": expr_class,
            "moon_phase": moon_phase_summary if p == "Moon" else None,
            "nakshatra": nakshatra_payload,
            "archetype": {
                "title": arch_title,
                "icon": arch_icon,
                "dignity_status": f"High Dignity ({d1_dignity_name})" if is_high_dignity else f"Low Dignity ({d1_dignity_name})",
                "strength_status": "High Strength" if is_high_strength else "Low Strength",
                "description": arch_desc
            },
            "quadrant": quad_res,
            "baladi_avastha": baladi_res,
            "functional_role": fn_role,
            "vitality": vit_res,
            "vitality_score": vit_res["vitality_score"],
            "vitality_tier": vit_res["vitality_tier"],
            "subcaption_intent_pct": vit_res.get("subcaption_intent_pct", round(functional_dignity_pct, 1)),
            "subcaption_power_pct": vit_res.get("subcaption_power_pct", round(planet_shadbala_pct, 1)),
            "subcaption_text": vit_res.get("subcaption_text", f"Intent: {functional_dignity_pct:.0f}% | Power: {planet_shadbala_pct:.0f}%"),
            "equation_parts": vit_res.get("equation_parts", {}),
            "calculation_receipt": vit_res.get("calculation_receipt", {}),
            "is_guru_chandal": vit_res.get("is_guru_chandal", False),
            "is_guru_ketu": vit_res.get("is_guru_ketu", False),
            "is_grahan": vit_res.get("is_grahan", False),
            "is_angaraka": vit_res.get("is_angaraka", False),
            "is_shrapit": vit_res.get("is_shrapit", False),
            "is_vikala": vit_res.get("is_vikala", False),
            "is_vargottama": is_vargottama,
            "vargottama_badge": vargottama_badge,
            "is_bhava_madhya": is_bhava_madhya,
            "bhava_madhya_badge": bhava_madhya_badge,
            "viparita_badge": viparita_badge,
            "badges": planet_badges,
            "affliction_badges": vit_res.get("affliction_badges", []),
            "deepthaadi": deepthaadi_res,
            "jagradaadi": jagradaadi_res,
            "calibrated_lajjitadi": calibrated_lajj,
            "lajjitadi": calibrated_lajj,
            "psychological_narrative": psy_narrative,
            "planetary_war": war_info,
            "step1_shadvarga": step1_info,
            "step2_host_rescue": step2_info,
            "step3_aspects": step3_info,
            "step4_house_field": step4_info,
            "aspect_graph": outgoing_aspect_graph,
            "incoming_aspect_graphs": incoming_aspect_graphs,
            "functional_dignity": {
                "base_dignity_pct": round(d1_score, 1),
                "base_dignity_name": d1_dignity_name,
                "vargottama_bonus": round(vargottama_bonus, 1),
                "host_bonus": round(host_bonus, 1),
                "peer_shift": round(clamped_aspect_net, 1),
                "terrain_mod_pct": round(terrain_mod, 1),
                "terrain_dignity_pct": round(d1_score + terrain_mod, 1),
                "lordship_mod_pct": round(total_lordship_mod, 1),
                "functional_dignity_pct": round(functional_dignity_pct, 1),
                "math_formula": func_dig_formula_str,
                "math_steps": math_steps
            },
            "strength": strength_info,
            "calculation_trail": calc_trail,
            "unified_cockpit": cockpit_payload,
            "cockpit": cockpit_payload
        }

    # -------------------------------------------------------------------------
    # MASTER ANCHORS OF DESTINY (Phaladeepika 3.11)
    # -------------------------------------------------------------------------
    # 1. Lagna Lord (D1) -> Overall Life Mastery
    lagna_lord = rel.SIGN_LORDS.get(lagna_sign, "Mars")
    lagna_lord_eval = planets_result.get(lagna_lord, {})
    
    # 2. Navamsha Lord (D9) -> Inner Contentment & Dharma
    d9_lagna_sign = vargas_data.get("D9", {}).get("lagna", {}).get("sign", "Aries")
    navamsha_lord = rel.SIGN_LORDS.get(d9_lagna_sign, "Mars")
    navamsha_eval = planets_result.get(navamsha_lord, {})
    
    # 3. Drekkana Lord (D3) -> Physical Courage & Power
    d3_lagna_sign = vargas_data.get("D3", {}).get("lagna", {}).get("sign", "Aries")
    drekkana_lord = rel.SIGN_LORDS.get(d3_lagna_sign, "Mars")
    drekkana_eval = planets_result.get(drekkana_lord, {})

    master_lords = {
        "lagna_lord": {
            "planet": lagna_lord,
            "varga": "D1",
            "rising_sign": lagna_sign,
            "placed_sign": lagna_lord_eval.get("sign", ""),
            "placed_degree": lagna_lord_eval.get("longitude", 0.0),
            "scale_score": lagna_lord_eval.get("net_scale_score", 0.0),
            "expression_mode": lagna_lord_eval.get("expression_mode", "Mixed"),
            "expression_class": lagna_lord_eval.get("expression_class", "mixed"),
            "title": "Lagna Lord (Lagna-Isha)",
            "governs": "Overall Life Mastery, Health & Holistic Fortune (Bhagyavan Prabhu)"
        },
        "navamsha_lord": {
            "planet": navamsha_lord,
            "varga": "D9",
            "rising_sign": d9_lagna_sign,
            "placed_sign": navamsha_eval.get("sign", ""),
            "placed_degree": navamsha_eval.get("longitude", 0.0),
            "scale_score": navamsha_eval.get("net_scale_score", 0.0),
            "expression_mode": navamsha_eval.get("expression_mode", "Mixed"),
            "expression_class": navamsha_eval.get("expression_class", "mixed"),
            "title": "Navamsha Lord (Navamsha-Isha)",
            "governs": "Internal Contentment, Soul-level Dharma & Spiritual Happiness (Sukhi)"
        },
        "drekkana_lord": {
            "planet": drekkana_lord,
            "varga": "D3",
            "rising_sign": d3_lagna_sign,
            "placed_sign": drekkana_eval.get("sign", ""),
            "placed_degree": drekkana_eval.get("longitude", 0.0),
            "scale_score": drekkana_eval.get("net_scale_score", 0.0),
            "expression_mode": drekkana_eval.get("expression_mode", "Mixed"),
            "expression_class": drekkana_eval.get("expression_class", "mixed"),
            "title": "Drekkana Lord (Drekkana-Isha)",
            "governs": "External Force, Bodily Courage, Competitiveness & Worldly Drive (Prabhu)"
        }
    }

    # Chart Predominance Summary
    auspicious_count = sum(1 for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
                          if shadvarga_scores.get(p, {}).get("average_dignity_pct", 50.0) >= 60.0)
    hostile_count = sum(1 for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
                        if shadvarga_scores.get(p, {}).get("average_dignity_pct", 50.0) <= 40.0)

    if auspicious_count >= 4:
        overall_pred = "Shubhamsha Bahule (Predominance of Auspicious Divisions)"
        overall_meaning = "Chiranjeevi & Shrimat: Fortunate longevity, elegance, and enduring prosperity."
    elif hostile_count >= 4:
        overall_pred = "Kruramsha Bahule (Predominance of Strained Divisions)"
        overall_meaning = "Requires reliance on strong dispositors to forge struggle into authority."
    else:
        overall_pred = "Madhyamsha (Balanced Divisional Distribution)"
        overall_meaning = "Dynamic mixture of opportunities and worldly responsibilities."

    for p_name, p_dict in d1_grahas.items():
        if p_name in planets_result and "calibrated_lajjitadi" in planets_result[p_name]:
            p_dict.setdefault("avasthas", {})["calibrated_lajjitadi"] = planets_result[p_name]["calibrated_lajjitadi"]

    lagna_eval = evaluate_lagna_vitality(vargas_data, shadbala_data, advanced_aspects, "D1")

    return {
        "summary": {
            "title": "Planetary Evaluation & Positive-to-Negative Scale",
            "subtitle": "Continuous diagnostic spectrum (-100% to +100%) and 4-Quadrant Archetypes (Phaladeepika Chapters 3 & 4)",
            "master_lords": master_lords,
            "moon_phase": moon_phase_summary,
            "lagna_evaluation": lagna_eval,
            "planetary_wars": planetary_wars,
            "chart_predominance": {
                "auspicious_count": auspicious_count,
                "hostile_count": hostile_count,
                "overall_status": overall_pred,
                "meaning": overall_meaning
            }
        },
        "lagna_evaluation": lagna_eval,
        "planetary_wars": planetary_wars,
        "planets": planets_result
    }
