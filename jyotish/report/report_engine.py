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
    advanced_aspects: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Implements the canonical 4-step Nakshatra scoring system:
    1. Filter out unoccupied nakshatras.
    2. Key point weights: Moon = 8 pts, Lagna = 4 pts, Sun = 2 pts, ordinary grahas = 1 pt each.
    3. Tally multi-occupant nakshatras.
    4. Aspectual refinement: multiply occupying planet's aspect percentage on Moon (x8), Lagna (x4), and Sun (x2).
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
                "aspect_points": 0.0,
                "total_points": 0.0,
                "dominance_pct": 0.0,
                "aspect_receipts": []
            }

        weight = base_weights.get(ent, 1.0)
        occupied[nak_name]["occupants"].append({
            "entity": ent,
            "weight": weight,
            "pada": ent_data.get("pada", 1),
            "lord": ent_data.get("nakshatra_lord", "--"),
            "sub_lord": ent_data.get("sub_lord", "--")
        })
        occupied[nak_name]["base_points"] += weight

    # Step 4: Aspectual Refinement
    if advanced_aspects:
        planets_aspects = advanced_aspects.get("planets", {})
        cusps_aspects = advanced_aspects.get("cusps", {})

        for nak_name, data in occupied.items():
            for occ in data["occupants"]:
                p_name = occ["entity"]
                if p_name == "Lagna":
                    continue  # Lagna degree does not cast Graha Drishti

                # Aspect on Moon (multiplier 8)
                raw_moon = planets_aspects.get(p_name, {}).get("Moon", {}).get("raw", 0.0)
                pct_moon = min(1.0, max(0.0, raw_moon / 60.0))
                moon_aspect_score = pct_moon * 8.0

                # Aspect on Lagna (Cusp 1, multiplier 4)
                raw_lagna = cusps_aspects.get(1, {}).get(p_name, {}).get("raw", 0.0)
                pct_lagna = min(1.0, max(0.0, raw_lagna / 60.0))
                lagna_aspect_score = pct_lagna * 4.0

                # Aspect on Sun (multiplier 2)
                raw_sun = planets_aspects.get(p_name, {}).get("Sun", {}).get("raw", 0.0)
                pct_sun = min(1.0, max(0.0, raw_sun / 60.0))
                sun_aspect_score = pct_sun * 2.0

                total_aspect = moon_aspect_score + lagna_aspect_score + sun_aspect_score
                if total_aspect > 0.05:
                    data["aspect_points"] += total_aspect
                    data["aspect_receipts"].append({
                        "planet": p_name,
                        "on_moon": round(moon_aspect_score, 2),
                        "on_lagna": round(lagna_aspect_score, 2),
                        "on_sun": round(sun_aspect_score, 2),
                        "total_bonus": round(total_aspect, 2)
                    })

    # Tally totals
    grand_total = 0.0
    for data in occupied.values():
        data["base_points"] = round(data["base_points"], 2)
        data["aspect_points"] = round(data["aspect_points"], 2)
        data["total_points"] = round(data["base_points"] + data["aspect_points"], 2)
        grand_total += data["total_points"]

    if grand_total <= 0.0:
        grand_total = 1.0

    # Sort descending
    sorted_nakshatras = sorted(occupied.values(), key=lambda x: x["total_points"], reverse=True)
    for idx, item in enumerate(sorted_nakshatras):
        item["rank"] = idx + 1
        item["dominance_pct"] = round((item["total_points"] / grand_total) * 100.0, 1)

    # 7-Group Temperament Distribution
    group_totals: Dict[str, float] = {g: 0.0 for g in ALL_NAKSHATRA_GROUPS}
    for item in sorted_nakshatras:
        g = item["group"]
        if g in group_totals:
            group_totals[g] += item["total_points"]

    temperament_breakdown: List[Dict[str, Any]] = []
    for g in ALL_NAKSHATRA_GROUPS:
        pts = round(group_totals[g], 2)
        pct = round((pts / grand_total) * 100.0, 1)
        meta = NAKSHATRA_GROUP_METADATA.get(g, {})
        temperament_breakdown.append({
            "group": g,
            "label": meta.get("label", g),
            "sanskrit": meta.get("sanskrit", ""),
            "nature": meta.get("nature", ""),
            "color": meta.get("color", "#64748b"),
            "bg": meta.get("bg", "#f8fafc"),
            "points": pts,
            "percentage": pct
        })

    temperament_breakdown.sort(key=lambda x: x["points"], reverse=True)
    dominant_temperament = temperament_breakdown[0] if temperament_breakdown else None
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


def compute_environmental_tally(vargas_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Tallies the placements of the 9 Grahas + Lagna across Elements, Gunas,
    Sign Rise Orientations, and Ayurvedic Doshas.
    """
    d1_data = vargas_data.get("D1", {})
    d1_grahas = d1_data.get("grahas", {})
    d1_lagna = d1_data.get("lagna", {})

    entities = ["Lagna", "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]

    elements_count = {"Fire": 0, "Earth": 0, "Air": 0, "Water": 0}
    gunas_count = {"Rajas (Movable)": 0, "Tamas (Fixed)": 0, "Sattva (Dual)": 0}
    rising_mode_count = {"Shirshodaya": 0, "Prishtodaya": 0, "Ubhayodaya": 0}
    dosha_count = {"Vata": 0, "Pitta": 0, "Kapha": 0}

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
        else:
            sign = d1_grahas.get(ent, {}).get("sign", "Aries")

        elem = ELEMENT_MAP.get(sign, "Fire")
        elements_count[elem] += 1

        guna = GUNA_MAP.get(sign, "Rajas (Movable)")
        gunas_count[guna] += 1

        rm = RISING_MODE_MAP.get(sign, "Shirshodaya")
        if "Shirshodaya" in rm:
            rising_mode_count["Shirshodaya"] += 1
        elif "Prishtodaya" in rm:
            rising_mode_count["Prishtodaya"] += 1
        else:
            rising_mode_count["Ubhayodaya"] += 1

        # Dosha allocation (blend sign element and graha nature)
        if elem == "Fire":
            dosha_count["Pitta"] += 1
        elif elem == "Air":
            dosha_count["Vata"] += 1
        elif elem == "Earth":
            dosha_count["Kapha"] += 1
        elif elem == "Water":
            dosha_count["Kapha"] += 1

    total_ent = len(entities)
    dominant_element = max(elements_count, key=elements_count.get)
    dominant_guna = max(gunas_count, key=gunas_count.get)
    dominant_dosha = max(dosha_count, key=dosha_count.get)

    return {
        "elements": {
            "counts": elements_count,
            "percentages": {k: round((v / total_ent) * 100.0, 1) for k, v in elements_count.items()},
            "dominant": dominant_element
        },
        "gunas": {
            "counts": gunas_count,
            "percentages": {k: round((v / total_ent) * 100.0, 1) for k, v in gunas_count.items()},
            "dominant": dominant_guna
        },
        "rising_modes": {
            "counts": rising_mode_count,
            "percentages": {k: round((v / total_ent) * 100.0, 1) for k, v in rising_mode_count.items()}
        },
        "ayurvedic_doshas": {
            "counts": dosha_count,
            "percentages": {k: round((v / sum(dosha_count.values())) * 100.0, 1) for k, v in dosha_count.items()},
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

        # Atmakaraka check
        ak_name = p_data.get("chara_karaka", {}).get("role", "")
        if ak_name == "Atmakaraka (AK)" or "Atmakaraka" in str(ak_name):
            weights += 0.20
            weight_reasons.append("Atmakaraka Soul Signifier (+0.20)")

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

    nak_dominance = compute_nakshatra_dominance(vargas_data, nakshatras_grahas, advanced_aspects)
    polarity_core = compute_polarity_core(vargas_data, nakshatras_grahas)
    operational_axis = compute_operational_axis(vargas_data)
    env_tally = compute_environmental_tally(vargas_data)
    planetary_rankings = compute_planetary_prominence_rankings(vargas_data, shadbala_data, planetary_eval)

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
