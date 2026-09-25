"""
Astra Astrological Synthesis Report Engine
Computes the multi-layered chart baseline profile:
1. Polarity Core (Ascendant Nakshatra / Ahamkara ⟷ Moon Nakshatra / Manas)
2. Canonical 4-Step Nakshatra Dominance & Temperament Scoring
3. Operational Axis (Rising Rashi ⟷ Rising Navamsha Pada with Vargottama check)
4. Macro Environmental Tally (Elements, Gunas, Rising Mode, Ayurvedic Doshas)
5. Planetary Prominence & Dignity Leaderboard
"""

import math
from typing import Dict, Any, List, Optional
import jyotish.relationships.relationships as rel
from jyotish.nakshatras.lore import (
    get_nakshatra_lore,
    get_nakshatra_group,
    NAKSHATRA_GROUP_METADATA,
    ALL_NAKSHATRA_GROUPS
)

ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

ELEMENT_MAP = {
    "Aries": "Fire", "Leo": "Fire", "Sagittarius": "Fire",
    "Taurus": "Earth", "Virgo": "Earth", "Capricorn": "Earth",
    "Gemini": "Air", "Libra": "Air", "Aquarius": "Air",
    "Cancer": "Water", "Scorpio": "Water", "Pisces": "Water"
}

GUNA_MAP = {
    "Aries": "Rajas (Movable)", "Cancer": "Rajas (Movable)", "Libra": "Rajas (Movable)", "Capricorn": "Rajas (Movable)",
    "Taurus": "Tamas (Fixed)", "Leo": "Tamas (Fixed)", "Scorpio": "Tamas (Fixed)", "Aquarius": "Tamas (Fixed)",
    "Gemini": "Sattva (Dual)", "Virgo": "Sattva (Dual)", "Sagittarius": "Sattva (Dual)", "Pisces": "Sattva (Dual)"
}

RISING_MODE_MAP = {
    "Gemini": "Shirshodaya (Head-Rising)", "Leo": "Shirshodaya (Head-Rising)", "Virgo": "Shirshodaya (Head-Rising)",
    "Libra": "Shirshodaya (Head-Rising)", "Scorpio": "Shirshodaya (Head-Rising)", "Aquarius": "Shirshodaya (Head-Rising)",
    "Aries": "Prishtodaya (Back-Rising)", "Taurus": "Prishtodaya (Back-Rising)", "Cancer": "Prishtodaya (Back-Rising)",
    "Sagittarius": "Prishtodaya (Back-Rising)", "Capricorn": "Prishtodaya (Back-Rising)",
    "Pisces": "Ubhayodaya (Both-Ways)"
}

SHADBALA_REQUIRED_RUPAS = {
    "Sun": 5.0,
    "Moon": 6.0,
    "Mars": 5.0,
    "Mercury": 7.0,
    "Jupiter": 6.5,
    "Venus": 5.5,
    "Saturn": 5.0,
    "Rahu": 5.0,
    "Ketu": 5.0
}


def compute_nakshatra_dominance(
    vargas_data: Dict[str, Any],
    nakshatras_grahas: Dict[str, Any],
    advanced_aspects: Optional[Dict[str, Any]] = None,
    prominence_map: Optional[Dict[str, float]] = None
) -> Dict[str, Any]:
    """
    Implements empirical Nakshatra dominance via Prominence-Scaled Occupancy:
    1. Filter out unoccupied nakshatras (strictly empirical bodily presence / Sthana).
    2. Key point weights scaled by Planetary Prominence:
       - Moon Nakshatra: 8.0 * Prominence_Moon
       - Lagna Nakshatra: 4.0 * 1.0 (foundational anchor)
       - Sun Nakshatra: 2.0 * Prominence_Sun
       - Ordinary Grahas: 1.0 * Prominence_Graha
    3. Tally multi-occupant nakshatras.
    Aspects are omitted from Nakshatra scoring because Grahas cast aspects, not stars,
    avoiding double-counting prominence and keeping asterisms strictly tied to physical presence.
    """
    occupied: Dict[str, Dict[str, Any]] = {}

    # Step 1 & 2: Base points and occupants
    entities = ["Lagna", "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
    base_weights = {
        "Moon": 8.0,
        "Lagna": 4.0,
        "Sun": 2.0,
        "Mars": 1.0,
        "Mercury": 1.0,
        "Jupiter": 1.0,
        "Venus": 1.0,
        "Saturn": 1.0,
        "Rahu": 1.0,
        "Ketu": 1.0
    }

    for ent in entities:
        ent_data = nakshatras_grahas.get(ent, {})
        nak_name = ent_data.get("nakshatra")
        if not nak_name:
            continue

        if nak_name not in occupied:
            occupied[nak_name] = {
                "nakshatra": nak_name,
                "lore": get_nakshatra_lore(nak_name),
                "group": get_nakshatra_group(nak_name),
                "occupants": [],
                "base_points": 0.0,
                "total_points": 0.0,
                "dominance_pct": 0.0
            }

        # Prominence scaling
        prom = 1.0
        if prominence_map is not None:
            prom = float(prominence_map.get(ent, 1.0)) if ent != "Lagna" else 1.0
        base_w = base_weights.get(ent, 1.0)
        effective_weight = round(base_w * prom, 2)

        occupied[nak_name]["occupants"].append({
            "entity": ent,
            "base_weight": base_w,
            "prominence": round(prom, 2),
            "weight": effective_weight,
            "pada": ent_data.get("pada", 1),
            "lord": ent_data.get("nakshatra_lord", "--"),
            "sub_lord": ent_data.get("sub_lord", "--")
        })
        occupied[nak_name]["base_points"] += effective_weight

    # Tally totals
    grand_total = 0.0
    for data in occupied.values():
        data["base_points"] = round(data["base_points"], 2)
        data["total_points"] = data["base_points"]
        grand_total += data["total_points"]

    if grand_total <= 0.0:
        grand_total = 1.0

    # Sort descending
    sorted_nakshatras = sorted(occupied.values(), key=lambda x: x["total_points"], reverse=True)
    for idx, item in enumerate(sorted_nakshatras):
        item["rank"] = idx + 1
        item["dominance_pct"] = round((item["total_points"] / grand_total) * 100.0, 1)

    # Map classical Parashari classes to the 7 canonical display labels
    TEMPERAMENT_CANONICAL = [
        {"group": "Chara", "label": "Mobile", "sanskrit": "Cara"},
        {"group": "Laghu", "label": "Quick", "sanskrit": "Laghu / Kṣipra"},
        {"group": "Mridu", "label": "Sweet", "sanskrit": "Mṛdu"},
        {"group": "Dhruva", "label": "Enduring", "sanskrit": "Dhruva / Sthira"},
        {"group": "Ugra", "label": "Strong", "sanskrit": "Ugra / Krūra"},
        {"group": "Tikshna", "label": "Bitter", "sanskrit": "Tīkṣṇa / Dāruṇa"},
        {"group": "Mishra", "label": "Mixed", "sanskrit": "Miśra / Sādhāraṇa"}
    ]

    expected_baseline = round(100.0 / 7.0, 1)  # 14.3%
    group_totals: Dict[str, float] = {g["group"]: 0.0 for g in TEMPERAMENT_CANONICAL}
    for item in sorted_nakshatras:
        g = item["group"]
        if g in group_totals:
            group_totals[g] += item["total_points"]

    temperament_breakdown: List[Dict[str, Any]] = []
    for meta in TEMPERAMENT_CANONICAL:
        g = meta["group"]
        pts = round(group_totals[g], 2)
        pct = round((pts / grand_total) * 100.0, 1)
        deviation = round(pct - expected_baseline, 1)
        orig_meta = NAKSHATRA_GROUP_METADATA.get(g, {})

        # Color coding: Green for surplus, Coral/Red for deficit, Sage for neutral
        if deviation > 2.0:
            status = "Surplus"
            color = "#16a34a"  # Green
            bg = "#dcfce7"
        elif deviation < -2.0:
            status = "Deficit"
            color = "#dc2626"  # Coral / Red
            bg = "#fee2e2"
        else:
            status = "Balanced"
            color = "#65a30d"  # Sage / Olive
            bg = "#f7fee7"

        temperament_breakdown.append({
            "group": g,
            "display_name": meta["label"],
            "sanskrit": meta["sanskrit"],
            "label": f"{meta['label']} ({meta['sanskrit']})",
            "nature": orig_meta.get("nature", ""),
            "points": pts,
            "percentage": pct,
            "baseline_pct": expected_baseline,
            "deviation_pct": deviation,
            "status": status,
            "color": color,
            "bg": bg
        })

    dominant_temperament = max(temperament_breakdown, key=lambda x: x["points"]) if temperament_breakdown else None
    dominant_nakshatra = sorted_nakshatras[0] if sorted_nakshatras else None

    return {
        "grand_total_points": round(grand_total, 2),
        "occupied_count": len(sorted_nakshatras),
        "dominant_nakshatra": dominant_nakshatra,
        "dominant_temperament": dominant_temperament,
        "leaderboard": sorted_nakshatras,
        "temperament_breakdown": temperament_breakdown
    }


def compute_polarity_core(
    vargas_data: Dict[str, Any],
    nakshatras_grahas: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Evaluates the Polarity Core:
    Ascendant Nakshatra (Action / Ahamkara) ⟷ Moon Nakshatra (Perception / Manas).
    Computes Five-Fold Friendship (Panchadha Maitri) between rulers,
    elemental compatibility (Tattvas), and an intuitive friction index.
    """
    d1_data = vargas_data.get("D1", {})
    d1_lagna = d1_data.get("lagna", {})
    d1_grahas = d1_data.get("grahas", {})

    asc_nak_data = nakshatras_grahas.get("Lagna", {})
    moon_nak_data = nakshatras_grahas.get("Moon", {})

    asc_nak_name = asc_nak_data.get("nakshatra", "Ashwini")
    moon_nak_name = moon_nak_data.get("nakshatra", "Ashwini")

    asc_lore = get_nakshatra_lore(asc_nak_name)
    moon_lore = get_nakshatra_lore(moon_nak_name)

    asc_ruler = asc_nak_data.get("nakshatra_lord", "Ketu")
    moon_ruler = moon_nak_data.get("nakshatra_lord", "Ketu")

    asc_sign = d1_lagna.get("sign", "Aries")
    moon_sign = d1_grahas.get("Moon", {}).get("sign", "Taurus")

    asc_element = ELEMENT_MAP.get(asc_sign, "Fire")
    moon_element = ELEMENT_MAP.get(moon_sign, "Water")

    # Evaluate Five-Fold Friendship between Ascendant Star Lord and Moon Star Lord
    p1 = asc_ruler
    p2 = moon_ruler

    if p1 == p2:
        nat_rel = "Self"
        tmp_rel = "Self"
        cmp_rel = "Self"
        friendship_status = "Unified Consciousness (Same Planetary Ruler)"
        friction_points = 0
    else:
        nat_rel = rel.get_natural_relationship(p1, p2)
        # Temporary relationship based on D1 placement
        p1_sign = d1_grahas.get(p1, {}).get("sign", asc_sign)
        p2_sign = d1_grahas.get(p2, {}).get("sign", moon_sign)
        p1_idx = ZODIAC_SIGNS.index(p1_sign) if p1_sign in ZODIAC_SIGNS else 0
        p2_idx = ZODIAC_SIGNS.index(p2_sign) if p2_sign in ZODIAC_SIGNS else 0
        tmp_rel = rel.get_temporary_relationship(p1_idx, p2_idx)
        cmp_rel = rel.get_compound_relationship(nat_rel, tmp_rel)

        rel_friction = {
            "Great Friend": 10,
            "Friend": 25,
            "Neutral": 45,
            "Enemy": 75,
            "Great Enemy": 95
        }
        friction_points = rel_friction.get(cmp_rel, 50)
        friendship_status = f"{cmp_rel} (Natural {nat_rel} + Temporary {tmp_rel})"

    # Elemental Compatibility (Tattva)
    element_pair = f"{asc_element} + {moon_element}"
    tattva_harmonic = True
    tattva_note = ""

    if (asc_element == "Fire" and moon_element == "Air") or (asc_element == "Air" and moon_element == "Fire"):
        tattva_status = "Dynamic Resonance"
        tattva_note = "Air fuels Fire: intellectual visions spark immediate, decisive action."
        friction_points = max(0, friction_points - 10)
    elif (asc_element == "Earth" and moon_element == "Water") or (asc_element == "Water" and moon_element == "Earth"):
        tattva_status = "Material Resonance"
        tattva_note = "Water softens Earth: emotional instincts find grounding and practical containment."
        friction_points = max(0, friction_points - 10)
    elif asc_element == moon_element:
        tattva_status = "Harmonic Congruence"
        tattva_note = f"Shared {asc_element} Element: external approach and emotional filter move with identical cadence."
        friction_points = max(0, friction_points - 15)
    elif (asc_element == "Fire" and moon_element == "Water") or (asc_element == "Water" and moon_element == "Fire"):
        tattva_status = "Severe Clashing (Fire vs Water)"
        tattva_note = "Water extinguishes Fire / Fire boils Water: internal emotional needs contradict external execution, creating sudden mood swings or emotional burnout."
        tattva_harmonic = False
        friction_points = min(100, friction_points + 20)
    elif (asc_element == "Fire" and moon_element == "Earth") or (asc_element == "Earth" and moon_element == "Fire"):
        tattva_status = "Smoldering Dissonance"
        tattva_note = "Earth smothers Fire: impulsive ambitions run into heavy, cautious hesitation."
        friction_points = min(100, friction_points + 10)
    elif (asc_element == "Air" and moon_element == "Earth") or (asc_element == "Earth" and moon_element == "Air"):
        tattva_status = "Dry Friction"
        tattva_note = "Air vs Earth: abstract conceptual theories clash with stubborn physical realities."
        friction_points = min(100, friction_points + 10)
    elif (asc_element == "Air" and moon_element == "Water") or (asc_element == "Water" and moon_element == "Air"):
        tattva_status = "Turbulent Mist"
        tattva_note = "Air vs Water: intellectual detachment vaporized by deep tides of feeling, creating mental restlessness."
        friction_points = min(100, friction_points + 10)
    else:
        tattva_status = "Neutral Alignment"
        tattva_note = "Balanced environmental exchange."

    friction_score = min(100, max(0, friction_points))
    if friction_score <= 35:
        polarity_state = "Harmonic Flow"
        polarity_badge = "success"
        polarity_summary = "External actions seamlessly satisfy internal emotional desires with minimal internal contradiction."
    elif friction_score <= 65:
        polarity_state = "Dynamic Creative Tension"
        polarity_badge = "warning"
        polarity_summary = "Occasional friction between how you instinctively act and what you privately feel, driving continuous growth and problem-solving."
    else:
        polarity_state = "Internal Friction Baseline"
        polarity_badge = "danger"
        polarity_summary = "Marked contrast between outward behavior and private inner feelings. Outer momentum often requires emotional self-compromise."

    return {
        "ascendant_nakshatra": {
            "name": asc_nak_name,
            "pada": asc_nak_data.get("pada", 1),
            "ruler": asc_ruler,
            "sub_lord": asc_nak_data.get("sub_lord", "--"),
            "group": get_nakshatra_group(asc_nak_name),
            "sign": asc_sign,
            "element": asc_element,
            "role": "Action / Ahaṃkāra (External Approach & Bodily Vehicle)",
            "lore": asc_lore
        },
        "moon_nakshatra": {
            "name": moon_nak_name,
            "pada": moon_nak_data.get("pada", 1),
            "ruler": moon_ruler,
            "sub_lord": moon_nak_data.get("sub_lord", "--"),
            "group": get_nakshatra_group(moon_nak_name),
            "sign": moon_sign,
            "element": moon_element,
            "role": "Perception / Manas (Sensory Mind & Emotional Digest)",
            "lore": moon_lore
        },
        "relationship": {
            "ruler_asc": asc_ruler,
            "ruler_moon": moon_ruler,
            "panchadha_maitri": cmp_rel,
            "friendship_status": friendship_status,
            "elements": element_pair,
            "tattva_status": tattva_status,
            "tattva_note": tattva_note,
            "tattva_harmonic": tattva_harmonic,
            "friction_score": friction_score,
            "state": polarity_state,
            "badge": polarity_badge,
            "summary": polarity_summary
        }
    }


def compute_operational_axis(vargas_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Computes the Operational Axis:
    Rising Rashi (D1 Outer Form / Tree) ⟷ Rising Navamsha (D9 Inner Fruit / Soul Purpose).
    Checks for Vargottama Lagna (+30% resilience boost).
    """
    d1_data = vargas_data.get("D1", {})
    d9_data = vargas_data.get("D9", {})

    d1_lagna = d1_data.get("lagna", {})
    d9_lagna = d9_data.get("lagna", {})

    rashi_sign = d1_lagna.get("sign", "Aries")
    navamsha_sign = d9_lagna.get("sign", "Aries")

    rashi_lord = rel.SIGN_LORDS.get(rashi_sign, "Mars")
    navamsha_lord = rel.SIGN_LORDS.get(navamsha_sign, "Mars")

    is_vargottama = (rashi_sign == navamsha_sign)

    # Dignity of Navamsha Lord in D1
    nav_lord_d1 = d1_data.get("grahas", {}).get(navamsha_lord, {})
    nav_lord_dignity = nav_lord_d1.get("dignity_breakdown", {}).get("final_dignity", "Neutral's Sign")

    return {
        "rashi_lagna": {
            "sign": rashi_sign,
            "lord": rashi_lord,
            "element": ELEMENT_MAP.get(rashi_sign, "Fire"),
            "guna": GUNA_MAP.get(rashi_sign, "Rajas"),
            "rising_mode": RISING_MODE_MAP.get(rashi_sign, "Shirshodaya"),
            "interpretation": "Physical constitution, worldly environment, and initial instinctual response."
        },
        "navamsha_lagna": {
            "sign": navamsha_sign,
            "lord": navamsha_lord,
            "element": ELEMENT_MAP.get(navamsha_sign, "Fire"),
            "guna": GUNA_MAP.get(navamsha_sign, "Rajas"),
            "lord_d1_dignity": nav_lord_dignity,
            "interpretation": "Inner soul trajectory, subconscious purpose, and what the worldly tree ultimately yields."
        },
        "is_vargottama": is_vargottama,
        "vargottama_boost": "+30% Vitality, Psychological Resilience & Integrated Destiny" if is_vargottama else None
    }


def compute_environmental_tally(
    vargas_data: Dict[str, Any],
    prominence_map: Optional[Dict[str, float]] = None
) -> Dict[str, Any]:
    """
    Tallies the placements of the 9 Grahas + Lagna across Elements, Gunas,
    Sign Rise Orientations, and Ayurvedic Doshas, weighted by Planetary Prominence.
    """
    d1_data = vargas_data.get("D1", {})
    d1_grahas = d1_data.get("grahas", {})
    d1_lagna = d1_data.get("lagna", {})

    entities = ["Lagna", "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]

    elements_count = {"Fire": 0, "Earth": 0, "Air": 0, "Water": 0}
    elements_points = {"Fire": 0.0, "Earth": 0.0, "Air": 0.0, "Water": 0.0}

    gunas_count = {"Rajas (Movable)": 0, "Tamas (Fixed)": 0, "Sattva (Dual)": 0}
    gunas_points = {"Rajas (Movable)": 0.0, "Tamas (Fixed)": 0.0, "Sattva (Dual)": 0.0}

    rising_mode_count = {"Shirshodaya": 0, "Prishtodaya": 0, "Ubhayodaya": 0}
    rising_mode_points = {"Shirshodaya": 0.0, "Prishtodaya": 0.0, "Ubhayodaya": 0.0}

    dosha_count = {"Vata": 0, "Pitta": 0, "Kapha": 0}
    dosha_points = {"Vata": 0.0, "Pitta": 0.0, "Kapha": 0.0}

    # Planetary dosha signatures
    graha_doshas = {
        "Sun": "Pitta",
        "Moon": "Vata/Kapha",
        "Mars": "Pitta",
        "Mercury": "Vata",
        "Jupiter": "Kapha",
        "Venus": "Kapha",
        "Saturn": "Vata",
        "Rahu": "Vata",
        "Ketu": "Pitta",
        "Lagna": "Vata"
    }

    for ent in entities:
        if ent == "Lagna":
            sign = d1_lagna.get("sign", "Aries")
            score = 1.0
        else:
            sign = d1_grahas.get(ent, {}).get("sign", "Aries")
            score = float(prominence_map.get(ent, 1.0)) if prominence_map is not None else 1.0

        elem = ELEMENT_MAP.get(sign, "Fire")
        elements_count[elem] += 1
        elements_points[elem] += score

        guna = GUNA_MAP.get(sign, "Rajas (Movable)")
        gunas_count[guna] += 1
        gunas_points[guna] += score

        rm = RISING_MODE_MAP.get(sign, "Shirshodaya")
        if "Shirshodaya" in rm:
            rising_mode_count["Shirshodaya"] += 1
            rising_mode_points["Shirshodaya"] += score
        elif "Prishtodaya" in rm:
            rising_mode_count["Prishtodaya"] += 1
            rising_mode_points["Prishtodaya"] += score
        else:
            rising_mode_count["Ubhayodaya"] += 1
            rising_mode_points["Ubhayodaya"] += score

        # Dosha allocation (blend sign element and graha nature)
        if elem == "Fire":
            dosha_count["Pitta"] += 1
            dosha_points["Pitta"] += score
        elif elem == "Air":
            dosha_count["Vata"] += 1
            dosha_points["Vata"] += score
        elif elem == "Earth":
            dosha_count["Kapha"] += 1
            dosha_points["Kapha"] += score
        elif elem == "Water":
            dosha_count["Kapha"] += 1
            dosha_points["Kapha"] += score

    tot_elem_pts = sum(elements_points.values()) or 1.0
    tot_guna_pts = sum(gunas_points.values()) or 1.0
    tot_rm_pts = sum(rising_mode_points.values()) or 1.0
    tot_dosha_pts = sum(dosha_points.values()) or 1.0

    dominant_element = max(elements_points, key=elements_points.get)
    dominant_guna = max(gunas_points, key=gunas_points.get)
    dominant_dosha = max(dosha_points, key=dosha_points.get)

    return {
        "elements": {
            "counts": elements_count,
            "points": {k: round(v, 2) for k, v in elements_points.items()},
            "percentages": {k: round((v / tot_elem_pts) * 100.0, 1) for k, v in elements_points.items()},
            "dominant": dominant_element
        },
        "gunas": {
            "counts": gunas_count,
            "points": {k: round(v, 2) for k, v in gunas_points.items()},
            "percentages": {k: round((v / tot_guna_pts) * 100.0, 1) for k, v in gunas_points.items()},
            "dominant": dominant_guna
        },
        "rising_modes": {
            "counts": rising_mode_count,
            "points": {k: round(v, 2) for k, v in rising_mode_points.items()},
            "percentages": {k: round((v / tot_rm_pts) * 100.0, 1) for k, v in rising_mode_points.items()}
        },
        "ayurvedic_doshas": {
            "counts": dosha_count,
            "points": {k: round(v, 2) for k, v in dosha_points.items()},
            "percentages": {k: round((v / tot_dosha_pts) * 100.0, 1) for k, v in dosha_points.items()},
            "dominant": dominant_dosha
        }
    }


def compute_planetary_prominence_rankings(
    vargas_data: Dict[str, Any],
    shadbala_data: Optional[Dict[str, Any]],
    planetary_eval: Optional[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Ranks planets along two vectors:
    Vector A: Prominence (Volume = SBR * (1 + sum(Opportunity Weights)))
    Vector B: Dignity (Mood = Vimshopak, Deeptaadi, Balaadi, Net Scale)
    Highlights the #1 Chart Commander.
    """
    d1_data = vargas_data.get("D1", {})
    d1_grahas = d1_data.get("grahas", {})
    d1_lagna = d1_data.get("lagna", {})
    lagna_sign = d1_lagna.get("sign", "Aries")
    lagna_lord = rel.SIGN_LORDS.get(lagna_sign, "Mars")
    d1_cusps = d1_data.get("cusps", [])
    mc_deg = d1_cusps[9].get("longitude", 270.0) if len(d1_cusps) >= 10 else 270.0

    eval_planets = (planetary_eval or {}).get("planets", {})

    ranked_list = []
    planets_to_rank = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]

    # -------------------------------------------------------------------------
    # Pre-compute Jaimini Chara Karakas (AK & AmK) with dynamic fallback
    # -------------------------------------------------------------------------
    classical_7 = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

    def _get_planet_deg(g_name: str) -> float:
        g_node = d1_grahas.get(g_name, {})
        return float(g_node.get("degree_0_to_30", g_node.get("longitude", 0.0) % 30.0))

    # Rank classical 7 grahas by degree descending
    sorted_by_deg = sorted(
        [g for g in classical_7 if g in d1_grahas],
        key=_get_planet_deg,
        reverse=True
    )

    ak_planet = sorted_by_deg[0] if len(sorted_by_deg) > 0 else None
    amk_planet = sorted_by_deg[1] if len(sorted_by_deg) > 1 else None

    # Check for AK-AmK Raja Yoga Connection (Conjunction or Mutual 1/7 Axis)
    has_ak_amk_yoga = False
    if ak_planet and amk_planet:
        ak_sign = d1_grahas.get(ak_planet, {}).get("sign")
        amk_sign = d1_grahas.get(amk_planet, {}).get("sign")
        if ak_sign in ZODIAC_SIGNS and amk_sign in ZODIAC_SIGNS:
            ak_s_idx = ZODIAC_SIGNS.index(ak_sign)
            amk_s_idx = ZODIAC_SIGNS.index(amk_sign)
            sign_dist = (amk_s_idx - ak_s_idx) % 12
            # Conjunct (0) or Opposite 7th house (6)
            if sign_dist in (0, 6):
                has_ak_amk_yoga = True

    for p in planets_to_rank:
        p_data = d1_grahas.get(p, {})
        p_lon = p_data.get("longitude", 0.0)
        p_sign = p_data.get("sign", "Aries")
        p_eval = eval_planets.get(p, {})

        # 1. Shadbala Ratio (SBR)
        sb_entry = (shadbala_data or {}).get(p, {})
        calculated_rupas = sb_entry.get("Total_Rupas")
        if calculated_rupas is None:
            # Fallback for Rahu/Ketu or missing
            calculated_rupas = 5.0
        req_rupas = SHADBALA_REQUIRED_RUPAS.get(p, 5.0)
        sbr = round(calculated_rupas / max(0.1, req_rupas), 2)

        # 2. Opportunity Weights
        weights = 0.0
        weight_reasons = []

        # In Kendra (1, 4, 7, 10 from Lagna)
        lagna_idx = ZODIAC_SIGNS.index(lagna_sign) if lagna_sign in ZODIAC_SIGNS else 0
        p_idx = ZODIAC_SIGNS.index(p_sign) if p_sign in ZODIAC_SIGNS else 0
        house_num = (p_idx - lagna_idx) % 12 + 1
        if house_num in [1, 4, 7, 10]:
            weights += 0.30
            weight_reasons.append("In Kendra (+0.30)")

        # Ascendant connection (within 10° orb)
        asc_lon = d1_lagna.get("longitude", 0.0)
        dist_asc = min((p_lon - asc_lon) % 360, (asc_lon - p_lon) % 360)
        if dist_asc <= 10.0:
            weights += 0.40
            weight_reasons.append("Conjunct Ascendant (+0.40)")

        # Midheaven connection (within 10° orb)
        dist_mc = min((p_lon - mc_deg) % 360, (mc_deg - p_lon) % 360)
        if dist_mc <= 10.0:
            weights += 0.25
            weight_reasons.append("Conjunct Midheaven (+0.25)")

        # Ascendant Lord connection
        if p == lagna_lord:
            weights += 0.30
            weight_reasons.append("Is Lagna Lord (+0.30)")

        # Luminary alignment (Sun / Moon)
        if p not in ["Sun", "Moon"]:
            sun_lon = d1_grahas.get("Sun", {}).get("longitude", 0.0)
            moon_lon = d1_grahas.get("Moon", {}).get("longitude", 0.0)
            if min((p_lon - sun_lon) % 360, (sun_lon - p_lon) % 360) <= 8.0:
                weights += 0.25
                weight_reasons.append("Aligned with Sun (+0.25)")
            if min((p_lon - moon_lon) % 360, (moon_lon - p_lon) % 360) <= 8.0:
                weights += 0.25
                weight_reasons.append("Aligned with Moon (+0.25)")

        # Jaimini Karaka Evaluation (AK, AmK, and Raja Yoga Connection)
        ck_role = str(p_data.get("chara_karaka", {}).get("role", ""))
        is_ak = (p == ak_planet) or ("Atmakaraka" in ck_role and "Amatya" not in ck_role)
        is_amk = (p == amk_planet) or ("Amatyakaraka" in ck_role or "AmK" in ck_role)

        if is_ak:
            weights += 0.30
            weight_reasons.append("Atmakaraka Soul Signifier (+0.30)")
        elif is_amk:
            weights += 0.15
            weight_reasons.append("Amatyakaraka Executive Mind (+0.15)")

        if has_ak_amk_yoga and (is_ak or is_amk):
            weights += 0.15
            weight_reasons.append("Jaimini Raja Yoga: AK-AmK Connection (+0.15)")

        prominence_score = round(sbr * (1.0 + weights), 2)

        # Vector B: Dignity
        avasthas = p_data.get("avasthas", {})
        deeptadi_obj = avasthas.get("deeptadi", "Swastha")
        deeptadi = deeptadi_obj.get("state", "Swastha") if isinstance(deeptadi_obj, dict) else str(deeptadi_obj)
        balaadi_obj = avasthas.get("bala", "Yuva")
        balaadi = balaadi_obj.get("state", "Yuva") if isinstance(balaadi_obj, dict) else str(balaadi_obj)
        vimshopak = p_eval.get("varga_score", 12.0)
        net_scale = p_eval.get("net_scale_score", 0.0)
        expression_mode = p_eval.get("expression_mode", "Constructive")

        ranked_list.append({
            "planet": p,
            "sign": p_sign,
            "house": house_num,
            "prominence_score": prominence_score,
            "shadbala_rupas": round(calculated_rupas, 2),
            "shadbala_ratio": sbr,
            "opportunity_weights": round(weights, 2),
            "opportunity_reasons": weight_reasons,
            "dignity_mood": deeptadi,
            "maturity": balaadi,
            "vimshopak_score": round(vimshopak, 1),
            "net_scale_score": round(net_scale, 1),
            "expression_mode": expression_mode
        })

    # Sort descending by Prominence Score
    ranked_list.sort(key=lambda x: x["prominence_score"], reverse=True)
    for idx, r in enumerate(ranked_list):
        r["rank"] = idx + 1

    commander = ranked_list[0] if ranked_list else None

    return {
        "leaderboard": ranked_list,
        "chart_commander": commander
    }


def generate_report_payload(chart_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Master orchestrator: Builds the complete Astrological Synthesis Report payload.
    """
    vargas_data = chart_data.get("vargas", {})
    nakshatras_grahas = chart_data.get("nakshatras", {}).get("grahas", {})
    advanced_aspects = chart_data.get("advanced_aspects", {})
    shadbala_data = chart_data.get("shadbala", {})
    planetary_eval = chart_data.get("planetary_evaluation", {})

    # 1. Calculate Prominence first
    planetary_rankings = compute_planetary_prominence_rankings(vargas_data, shadbala_data, planetary_eval)
    prominence_map = {
        p["planet"]: p["prominence_score"]
        for p in planetary_rankings.get("leaderboard", [])
    }

    # 2. Pass prominence_map into Nakshatra and Environmental engines
    nak_dominance = compute_nakshatra_dominance(
        vargas_data, nakshatras_grahas, advanced_aspects, prominence_map=prominence_map
    )
    polarity_core = compute_polarity_core(vargas_data, nakshatras_grahas)
    operational_axis = compute_operational_axis(vargas_data)
    env_tally = compute_environmental_tally(vargas_data, prominence_map=prominence_map)

    # Ingredients Checklist for Astrologer Desk
    synthesis_ingredients = {
        "action_mode": polarity_core["ascendant_nakshatra"]["name"],
        "action_group": polarity_core["ascendant_nakshatra"]["group"],
        "perception_mode": polarity_core["moon_nakshatra"]["name"],
        "perception_group": polarity_core["moon_nakshatra"]["group"],
        "polarity_friction": polarity_core["relationship"]["friction_score"],
        "polarity_state": polarity_core["relationship"]["state"],
        "dominant_nakshatra": nak_dominance["dominant_nakshatra"]["nakshatra"] if nak_dominance["dominant_nakshatra"] else "--",
        "dominant_temperament": nak_dominance["dominant_temperament"]["label"] if nak_dominance["dominant_temperament"] else "--",
        "dominant_element": env_tally["elements"]["dominant"],
        "dominant_guna": env_tally["gunas"]["dominant"],
        "dominant_dosha": env_tally["ayurvedic_doshas"]["dominant"],
        "chart_commander": planetary_rankings["chart_commander"]["planet"] if planetary_rankings["chart_commander"] else "--",
        "commander_prominence": planetary_rankings["chart_commander"]["prominence_score"] if planetary_rankings["chart_commander"] else "--",
        "is_vargottama": operational_axis["is_vargottama"]
    }

    return {
        "title": "Astrological Synthesis Report (Master Ingredients Desk)",
        "polarity_core": polarity_core,
        "nakshatra_dominance": nak_dominance,
        "operational_axis": operational_axis,
        "environmental_tally": env_tally,
        "planetary_rankings": planetary_rankings,
        "synthesis_ingredients": synthesis_ingredients
    }
