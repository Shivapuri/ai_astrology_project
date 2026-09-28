"""
Astra Astrological Synthesis Report Engine (jyotish/report/report_engine.py)

Master orchestrator for the complete four-stage chart assessment and synthesis architecture:
1. Stage 1: Mathematical Foundations & Tallies
   - Parāśarī Prominence Engine (Graha Yuddha, 8 opportunity vectors, #1 Chart Commander)
   - 10-Varga (Daśavarga) Macro-Environmental Balance (Prominence-scaled thermodynamics)
   - 6-Category Nakshatra Dominance & Temperament Balance (with Universal Catalyst rule)
2. Stage 2: Macrocosmic Context & Background Canvas
   - Contextual Setup Yogas (~25 yogas: Sāṅkhya, Kemadruma, Sun-Moon geometry, Solar flanking)
   - 4-String Background Personality Canvas (Introversion, Practicality, Defiance, Intellect)
3. Stage 3: Sequential Planetary Interpretation
   - Target prioritization by Prominence (#1 Commander first)
   - 5-Pillar Archetypal Decomposition (Symbolism, Sign, House, Nakshatra, Lordships)
   - Dynamic Semantic Interactions (Elements and Modalities Commonalities vs Clashes)
   - Contextual Redirection through Canvas and Tone Modulation via existing Dignity
4. Stage 4: Continuous Harmonic Degree Overlays
   - Projecting D9, D7, and D10 harmonic longitudes onto the 360° D1 wheel (flagging <= 3°20' conjunctions)
"""

import math
import os
import json
from typing import Dict, Any, List, Optional
import jyotish.relationships.relationships as rel
from jyotish.nakshatras.lore import (
    get_nakshatra_lore,
    get_nakshatra_group,
    get_temperament_relationship,
    NAKSHATRA_GROUP_METADATA,
    NAKSHATRA_TEMPERAMENT_DOSSIER,
    ALL_NAKSHATRA_GROUPS
)
from jyotish.report.prominence import compute_planetary_prominence
from jyotish.report.varga_environment import (
    compute_varga_environment,
    DASAVARGA_ENVIRONMENTAL_WEIGHTS,
    TOTAL_DASAVARGA_WEIGHT
)
from jyotish.yogas.contextual_yogas import detect_contextual_yogas
from jyotish.report.interpretation_engine import (
    synthesize_background_canvas,
    generate_planetary_interpretations,
    compute_harmonic_overlays
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

POLARITY_MAP = {
    "Aries": "Active", "Gemini": "Active", "Leo": "Active",
    "Libra": "Active", "Sagittarius": "Active", "Aquarius": "Active",
    "Taurus": "Passive", "Cancer": "Passive", "Virgo": "Passive",
    "Scorpio": "Passive", "Capricorn": "Passive", "Pisces": "Passive"
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

# 10-Varga (Daśavarga) Environmental Weights summing to 13.33 (Vic DiCara model)
SHADVARGA_ENVIRONMENTAL_WEIGHTS = DASAVARGA_ENVIRONMENTAL_WEIGHTS


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

    # Map classical Parashari classes to the 6 canonical display labels (16.7% baseline)
    TEMPERAMENT_CANONICAL = [
        {"group": "Chara", "label": "Mobile", "sanskrit": "Cara / Cala"},
        {"group": "Laghu", "label": "Quick", "sanskrit": "Kṣipra / Laghu"},
        {"group": "Mridu", "label": "Sweet", "sanskrit": "Mṛdu"},
        {"group": "Dhruva", "label": "Enduring", "sanskrit": "Dhruva / Sthira"},
        {"group": "Ugra", "label": "Strong", "sanskrit": "Ugra / Krūra"},
        {"group": "Tikshna", "label": "Bitter", "sanskrit": "Tīkṣṇa / Dāruṇa"}
    ]

    expected_baseline = round(100.0 / 6.0, 1)  # 16.7%
    group_totals: Dict[str, float] = {g["group"]: 0.0 for g in TEMPERAMENT_CANONICAL}
    catalyst_occupants: List[str] = []

    for item in sorted_nakshatras:
        nak_name = item["nakshatra"]
        pts = item["total_points"]
        # Universal Catalyst Rule: Krittika & Vishakha distribute to all 6 groups simultaneously
        if nak_name in ["Krittika", "Vishakha"]:
            catalyst_occupants.append(nak_name)
            for g in group_totals:
                group_totals[g] += pts
        else:
            g = item["group"]
            if g in group_totals:
                group_totals[g] += pts

    tot_temperament_points = sum(group_totals.values())
    if tot_temperament_points <= 0.0:
        tot_temperament_points = 1.0

    temperament_breakdown: List[Dict[str, Any]] = []
    for meta in TEMPERAMENT_CANONICAL:
        g = meta["group"]
        pts = round(group_totals[g], 2)
        pct = round((pts / tot_temperament_points) * 100.0, 1)
        deviation = round(pct - expected_baseline, 1)
        orig_meta = NAKSHATRA_GROUP_METADATA.get(g, {})
        dossier = NAKSHATRA_TEMPERAMENT_DOSSIER.get(g, {})

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
            "bg": bg,
            "dossier": dossier
        })

    dominant_temperament = max(temperament_breakdown, key=lambda x: x["points"]) if temperament_breakdown else None
    dominant_nakshatra = sorted_nakshatras[0] if sorted_nakshatras else None

    # Relationship detection (Resonances vs Dissonances between top groups)
    surplus_groups = [item["group"] for item in temperament_breakdown if item["status"] == "Surplus"]
    active_relationships: List[Dict[str, Any]] = []
    if len(surplus_groups) >= 2:
        for i in range(len(surplus_groups)):
            for j in range(i + 1, len(surplus_groups)):
                rel_info = get_temperament_relationship(surplus_groups[i], surplus_groups[j])
                if rel_info:
                    active_relationships.append({
                        "group1": surplus_groups[i],
                        "group2": surplus_groups[j],
                        **rel_info
                    })
    if not active_relationships and len(temperament_breakdown) >= 2:
        sorted_by_pts = sorted(temperament_breakdown, key=lambda x: x["points"], reverse=True)
        rel_info = get_temperament_relationship(sorted_by_pts[0]["group"], sorted_by_pts[1]["group"])
        if rel_info:
            active_relationships.append({
                "group1": sorted_by_pts[0]["group"],
                "group2": sorted_by_pts[1]["group"],
                **rel_info
            })

    return {
        "grand_total_points": round(grand_total, 2),
        "total_temperament_points": round(tot_temperament_points, 2),
        "occupied_count": len(sorted_nakshatras),
        "dominant_nakshatra": dominant_nakshatra,
        "dominant_temperament": dominant_temperament,
        "leaderboard": sorted_nakshatras,
        "temperament_breakdown": temperament_breakdown,
        "active_relationships": active_relationships,
        "universal_catalysts": catalyst_occupants
    }


def compute_polarity_core(
    vargas_data: Dict[str, Any],
    nakshatras_grahas: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Evaluates the Polarity Core:
    Ascendant Nakshatra (Action / Ahamkara) ⟷ Moon Nakshatra (Perception / Manas).
    Computes bidirectional Five-Fold Friendship (Panchadha Maitri) between rulers,
    conjunction harmonic awareness, elemental compatibility, and friction score.
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
    moon_element = ELEMENT_MAP.get(moon_sign, "Earth")  # Consistent fallback: Taurus is Earth

    p1 = asc_ruler
    p2 = moon_ruler

    rel_friction = {
        "Great Friend": 10,
        "Friend": 25,
        "Neutral": 50,
        "Enemy": 75,
        "Great Enemy": 95
    }

    if p1 == p2:
        friendship_status = f"Unified Consciousness (Both stars ruled by {p1})"
        base_friction = 15  # Base unity
        cmp_rel = "Self"
    else:
        # 1. Bidirectional Natural Friendship (P1 -> P2 and P2 -> P1)
        nat_1_to_2 = rel.get_natural_relationship(p1, p2)
        nat_2_to_1 = rel.get_natural_relationship(p2, p1)

        # 2. Temporary Relationship (Tatkalika) with Conjunction Awareness
        p1_sign = d1_grahas.get(p1, {}).get("sign", asc_sign)
        p2_sign = d1_grahas.get(p2, {}).get("sign", moon_sign)
        p1_idx = ZODIAC_SIGNS.index(p1_sign) if p1_sign in ZODIAC_SIGNS else 0
        p2_idx = ZODIAC_SIGNS.index(p2_sign) if p2_sign in ZODIAC_SIGNS else 0

        distance = (p2_idx - p1_idx) % 12
        if distance == 0:
            # Conjunct in D1: In psychological synthesis, conjunct rulers create intense focus,
            # not blind hostility. We treat mutual presence as cooperative alliance.
            tmp_rel = "Friend"
        elif distance in [1, 2, 3, 9, 10, 11]:
            tmp_rel = "Friend"
        else:
            tmp_rel = "Enemy"

        # 3. Bidirectional Compound Synthesis
        cmp_1 = rel.get_compound_relationship(nat_1_to_2, tmp_rel)
        cmp_2 = rel.get_compound_relationship(nat_2_to_1, tmp_rel)

        f1 = rel_friction.get(cmp_1, 50)
        f2 = rel_friction.get(cmp_2, 50)
        base_friction = round((f1 + f2) / 2.0)

        cmp_rel = cmp_1 if cmp_1 == cmp_2 else f"{cmp_1} / {cmp_2}"
        friendship_status = f"{cmp_rel} ({p1} views {p2}: {nat_1_to_2} | {p2} views {p1}: {nat_2_to_1} + Temp: {tmp_rel})"

    friction_points = base_friction

    # 4. Elemental Compatibility (Tattva)
    element_pair = f"{asc_element} + {moon_element}"
    tattva_harmonic = True

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
        tattva_note = "Water extinguishes Fire / Fire boils Water: internal emotional needs contradict external execution."
        tattva_harmonic = False
        friction_points = min(100, friction_points + 25)
    elif (asc_element == "Fire" and moon_element == "Earth") or (asc_element == "Earth" and moon_element == "Fire"):
        tattva_status = "Smoldering Dissonance"
        tattva_note = "Earth smothers Fire: impulsive ambitions run into heavy hesitation."
        tattva_harmonic = False
        friction_points = min(100, friction_points + 10)
    elif (asc_element == "Air" and moon_element == "Earth") or (asc_element == "Earth" and moon_element == "Air"):
        tattva_status = "Dry Friction"
        tattva_note = "Air vs Earth: abstract concepts clash with physical realities."
        tattva_harmonic = False
        friction_points = min(100, friction_points + 10)
    elif (asc_element == "Air" and moon_element == "Water") or (asc_element == "Water" and moon_element == "Air"):
        tattva_status = "Turbulent Mist"
        tattva_note = "Air vs Water: intellectual detachment challenged by emotional tides."
        tattva_harmonic = False
        friction_points = min(100, friction_points + 10)
    else:
        tattva_status = "Neutral Alignment"
        tattva_note = "Balanced environmental exchange."

    friction_score = min(100, max(0, friction_points))

    # Evaluate State based on combined friction and harmony flag
    if friction_score <= 35 and tattva_harmonic:
        polarity_state = "Harmonic Flow"
        polarity_badge = "success"
        polarity_summary = "External actions seamlessly satisfy internal emotional desires with minimal internal contradiction."
    elif friction_score <= 65:
        polarity_state = "Dynamic Creative Tension"
        polarity_badge = "warning"
        polarity_summary = "Occasional friction between how you instinctively act and what you privately feel, driving continuous growth."
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
            "tropical_sign": asc_sign,
            "element": asc_element,
            "sign_element": asc_element,
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
            "tropical_sign": moon_sign,
            "element": moon_element,
            "sign_element": moon_element,
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
    prominence_map: Optional[Dict[str, float]] = None,
    lagna_boost: float = 1.0
) -> Dict[str, Any]:
    """
    Tallies the balance of Elements, Gunas, Polarities, and Ayurvedic Doshas
    using Vic DiCara's 10-Varga (Daśavarga) model (D1:2.0, D60:3.33, 8 others: 1.0 each, total 13.33),
    scaled by Planetary Prominence.
    """
    return compute_varga_environment(vargas_data, prominence_map=prominence_map, lagna_boost=lagna_boost)


def compute_planetary_prominence_rankings(
    vargas_data: Dict[str, Any],
    shadbala_data: Optional[Dict[str, Any]],
    planetary_eval: Optional[Dict[str, Any]],
    nakshatras_grahas: Optional[Dict[str, Any]] = None,
    advanced_aspects: Optional[Dict[str, Any]] = None,
    vimshottari_at_birth: Optional[Dict[str, Any]] = None,
    vimshopaka_data: Optional[Dict[str, Any]] = None,
    jd: Optional[float] = None
) -> Dict[str, Any]:
    """
    Ranks planets along two decoupled vectors using Sage Parāśara's 8 Opportunity Factors & Graha Yuddha:
    Vector A: Prominence (Volume = SBR * (1 + sum(Opportunity Weights)))
              where SBR = Calculated Rupas / 6.0 (uniform standard baseline)
    Vector B: Dignity (Mood = Vimśopaka 20pt, Dīptādi, Bālādi, Net Scale Score)
    Highlights the #1 Chart Commander (Kārakādhipati).
    Delegates calculation to the dedicated jyotish.report.prominence engine.
    """
    return compute_planetary_prominence(
        vargas_data=vargas_data,
        shadbala_data=shadbala_data,
        advanced_aspects=advanced_aspects,
        nakshatras_grahas=nakshatras_grahas,
        vimshottari_at_birth=vimshottari_at_birth,
        planetary_eval=planetary_eval,
        vimshopaka_data=vimshopaka_data,
        jd=jd
    )


_SIGNIFICATIONS_FLOWCHARTS_CACHE: Optional[Dict[str, Any]] = None
_SIGNIFICATIONS_DATA_CACHE: Optional[Dict[str, Any]] = None


def get_significations_flowcharts() -> Dict[str, Any]:
    """
    Loads and caches jyotish/report/significations_flowcharts.json containing
    the raw Mermaid flowchart definitions for planets, signs, and houses.
    """
    global _SIGNIFICATIONS_FLOWCHARTS_CACHE
    if _SIGNIFICATIONS_FLOWCHARTS_CACHE is not None:
        return _SIGNIFICATIONS_FLOWCHARTS_CACHE

    json_path = os.path.join(os.path.dirname(__file__), "significations_flowcharts.json")
    if os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                _SIGNIFICATIONS_FLOWCHARTS_CACHE = json.load(f)
                return _SIGNIFICATIONS_FLOWCHARTS_CACHE
        except Exception:
            pass
    return {"planets": {}, "signs": {}, "houses": {}}


def get_significations_data() -> Dict[str, Any]:
    """
    Loads and caches jyotish/report/significations_data.json containing
    the structured multi-pillar definitions for planets, signs, and houses.
    """
    global _SIGNIFICATIONS_DATA_CACHE
    if _SIGNIFICATIONS_DATA_CACHE is not None:
        return _SIGNIFICATIONS_DATA_CACHE

    json_path = os.path.join(os.path.dirname(__file__), "significations_data.json")
    if os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                _SIGNIFICATIONS_DATA_CACHE = json.load(f)
                return _SIGNIFICATIONS_DATA_CACHE
        except Exception:
            pass
    return {"planets": {}, "signs": {}, "houses": {}}


def generate_report_payload(chart_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Master orchestrator: Builds the complete Astrological Synthesis Report payload.
    """
    vargas_data = chart_data.get("vargas", {})
    nakshatras_grahas = chart_data.get("nakshatras", {}).get("grahas", {})
    advanced_aspects = chart_data.get("advanced_aspects", {})
    shadbala_data = chart_data.get("shadbala", {})
    planetary_eval = chart_data.get("planetary_evaluation", {})
    vimshottari_at_birth = chart_data.get("vimshottari_dasha", {}).get("at_birth", {})
    vimshopaka_data = chart_data.get("varga_vimshopaka") or chart_data.get("vimshopaka")
    jd = chart_data.get("astronomy", {}).get("julian_day")

    # 1. Calculate Prominence first using dedicated Parāśarī Prominence Engine
    planetary_rankings = compute_planetary_prominence_rankings(
        vargas_data=vargas_data,
        shadbala_data=shadbala_data,
        planetary_eval=planetary_eval,
        nakshatras_grahas=nakshatras_grahas,
        advanced_aspects=advanced_aspects,
        vimshottari_at_birth=vimshottari_at_birth,
        vimshopaka_data=vimshopaka_data,
        jd=jd
    )
    prominence_map = planetary_rankings.get("prominence_map", {})

    # 2. Pass prominence_map into Nakshatra and Environmental engines
    nak_dominance = compute_nakshatra_dominance(
        vargas_data, nakshatras_grahas, advanced_aspects, prominence_map=prominence_map
    )
    polarity_core = compute_polarity_core(vargas_data, nakshatras_grahas)
    operational_axis = compute_operational_axis(vargas_data)
    env_tally = compute_environmental_tally(vargas_data, prominence_map=prominence_map)

    # 3. Contextual Setup Yogas
    contextual_yogas_list = detect_contextual_yogas(chart_data)

    # 4. Background Canvas Synthesis
    background_canvas = synthesize_background_canvas(
        polarity_core=polarity_core,
        operational_axis=operational_axis,
        env_tally=env_tally,
        nak_dominance=nak_dominance
    )

    # 5. Sequential Planetary Interpretations (5 Pillars, Commonalities vs Clashes, Tone)
    planetary_interpretations = generate_planetary_interpretations(
        prominence_rankings=planetary_rankings,
        vargas_data=vargas_data,
        nakshatras_grahas=nakshatras_grahas,
        planetary_eval=planetary_eval,
        canvas=background_canvas
    )

    # 6. Harmonic Degree Overlays (D9, D7, D10 onto D1)
    harmonic_overlays = compute_harmonic_overlays(vargas_data=vargas_data)

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
        "dominant_polarity": env_tally["polarity"]["dominant"],
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
        "synthesis_ingredients": synthesis_ingredients,
        "contextual_yogas": [y.to_dict() for y in contextual_yogas_list],
        "background_canvas": background_canvas,
        "planetary_interpretations": planetary_interpretations,
        "harmonic_overlays": harmonic_overlays,
        "significations_data": get_significations_data(),
        "flowcharts": get_significations_flowcharts()
    }
