"""
jyotish/report/houses_of_life.py

Stage 4 Report Engine: Vic DiCara's "Houses of Life" Quantitative House & Planetary
Evaluation System (based on Phaladīpikā Chapters 3, 4, 6, and 15).

Consumes the read-only serialized chart_dict from ChartPipeline.to_dict() without
modifying any Frozen Core Calculus modules (Stages 1-3).
"""

import math
import unicodedata
from typing import Dict, Any, List, Tuple, Optional
import jyotish.aspects.aspects as aspects
from jyotish.baseline import (
    ZODIAC_SIGNS,
    SIGN_LORDS,
    COMBUSTION_ORBS,
    COMBUSTION_ORBS_RETROGRADE,
    EXALTATION_SIGNS,
)
from jyotish.relationships.relationships import get_natural_relationship

CLASSICAL_PLANETS: List[str] = [
    "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"
]

# Moolatrikona root sign per Phaladeepika Ch. 15 / DiCara rules
DICARA_MOOLATRIKONA_SIGNS: Dict[str, str] = {
    "Sun": "Leo",
    "Moon": "Taurus",       # Exaltation sign serves as root for Moon
    "Mars": "Aries",
    "Mercury": "Virgo",     # Female sign exception for Mercury
    "Jupiter": "Sagittarius",
    "Venus": "Libra",
    "Saturn": "Aquarius",
}

# Regular domicile signs for dual-ruling planets
DICARA_DOMICILE_SIGNS: Dict[str, Optional[str]] = {
    "Sun": None,
    "Moon": "Cancer",
    "Mars": "Scorpio",
    "Mercury": "Gemini",
    "Jupiter": "Pisces",
    "Venus": "Taurus",
    "Saturn": "Capricorn",
}

# D1 Rashi Dignity mapping to DiCara's [-1.0, +1.0] scale
DICARA_D1_DIGNITY_MAP: Dict[str, float] = {
    "Exalted": 1.0,
    "Deep Exaltation": 1.0,
    "Moolatrikona": 0.9,
    "Own Sign": 0.8,
    "Great Friend": 0.6,
    "Great Friend's Sign": 0.6,
    "Friend": 0.4,
    "Friend's Sign": 0.4,
    "Neutral": 0.0,
    "Neutral's Sign": 0.0,
    "Enemy": -0.4,
    "Enemy's Sign": -0.4,
    "Great Enemy": -0.7,
    "Great Enemy's Sign": -0.7,
    "Debilitated": -1.0,
    "Deep Debilitation": -1.0,
}

# Base natural temperaments for Rule 4
NATURAL_TEMPERAMENT: Dict[str, float] = {
    "Jupiter": 1.0,
    "Venus": 1.0,
    "Mars": -1.0,
    "Saturn": -1.0,
    "Sun": -0.5,
    "Moon": 0.5,
    "Mercury": 0.5,
}

# Digbala canonical peak houses per Phaladeepika Ch. 4
DIGBALA_PEAK_HOUSES: Dict[str, int] = {
    "Jupiter": 1,
    "Mercury": 1,
    "Sun": 10,
    "Mars": 10,
    "Saturn": 7,
    "Moon": 4,
    "Venus": 4,
}

# Bhava Karakas per Phaladeepika Ch. 15 / DiCara disclosures
DICARA_HOUSE_KARAKAS: Dict[int, List[str]] = {
    1: ["Sun"],
    2: ["Jupiter"],
    3: ["Mars"],
    4: ["Moon", "Mercury"],       # Phaladeepika 15.15-16 merges Moon & Mercury for 4th
    5: ["Jupiter"],
    6: ["Saturn", "Mars"],
    7: ["Venus"],
    8: ["Saturn"],
    9: ["Jupiter", "Sun"],
    10: ["Mercury", "Sun", "Jupiter", "Saturn"],
    11: ["Jupiter"],
    12: ["Saturn"],
}


def _shortest_distance(lon1: float, lon2: float) -> float:
    """Calculates the minimal angular distance between two longitudes on a 360-degree circle."""
    diff = abs(lon1 - lon2) % 360.0
    return 360.0 - diff if diff > 180.0 else diff


def _shortest_house_dist(h1: int, h2: int) -> int:
    """Calculates the minimal house distance between two houses on a 12-house circle."""
    diff = abs(h1 - h2) % 12
    return 12 - diff if diff > 6 else diff


def _get_dignity_status(p_data: Dict[str, Any]) -> str:
    """Returns compound Pancadha Maitri final_dignity if available, else base dignity."""
    bd = p_data.get("dignity_breakdown")
    if isinstance(bd, dict) and bd.get("final_dignity"):
        return str(bd["final_dignity"])
    return str(p_data.get("dignity") or "Neutral")


def _get_composite_dignity_unit(
    p_name: str,
    chart_dict: Optional[Dict[str, Any]],
    d1_grahas: Dict[str, Any]
) -> float:
    """
    Computes multi-varga dignity blending D1 and D9 (Navāṁśa per Phaladīpikā 3.4 & 3.11).
    Accounts for Vargottama (acting like own sign per Phaladīpikā 3.4, floored at 0.80).
    """
    d1_status = _get_dignity_status(d1_grahas.get(p_name, {}))
    d_d1 = DICARA_D1_DIGNITY_MAP.get(d1_status, 0.0)

    if not chart_dict:
        return d_d1

    d9_grahas = chart_dict.get("vargas", {}).get("D9", {}).get("grahas", {})
    if p_name in d9_grahas:
        d9_status = _get_dignity_status(d9_grahas[p_name])
        d_d9 = DICARA_D1_DIGNITY_MAP.get(d9_status, 0.0)
        d1_sign = d1_grahas.get(p_name, {}).get("sign")
        d9_sign = d9_grahas[p_name].get("sign")
        is_vargottama = (d1_sign is not None and d1_sign == d9_sign)

        if is_vargottama:
            effective_d = max(d_d1, 0.80)
        else:
            effective_d = 0.65 * d_d1 + 0.35 * d_d9
        return max(-1.0, min(1.0, effective_d))

    return d_d1


def _get_bala_and_digbala_bonus(
    p_name: str,
    p_house: int,
    chart_dict: Optional[Dict[str, Any]] = None
) -> Tuple[float, float]:
    """
    Extracts canonical Digbala factor in [-1.0, +1.0] and returns (bala_ratio, digbala_pts).
    Formula: DigFactor_P = 1.0 - (shortest_house_dist(H_P, H_peak) / 3.0)
    digbala_pts = 20.0 * DigFactor_P
    """
    h_peak = DIGBALA_PEAK_HOUSES.get(p_name, 1)
    dist = _shortest_house_dist(p_house, h_peak)
    dig_factor = 1.0 - (dist / 3.0)
    digbala_pts = 20.0 * dig_factor

    bala_ratio = 1.0
    if chart_dict and "shadbala" in chart_dict:
        sb_entry = chart_dict["shadbala"].get(p_name, {})
        if isinstance(sb_entry, dict) and "shadbala_ratio" in sb_entry:
            bala_ratio = float(sb_entry["shadbala_ratio"])
            clamped_bala = max(0.75, min(1.25, bala_ratio))
            if digbala_pts >= 0.0:
                digbala_pts = digbala_pts * clamped_bala
            else:
                digbala_pts = digbala_pts / clamped_bala
            digbala_pts += (clamped_bala - 1.0) * 20.0

    return bala_ratio, digbala_pts


def _extract_whole_sign_geometry(chart_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extracts Whole Sign house geometry (Phase 1).
    Ascendant degree inside its sign defines the sensitive cusp for all 12 houses.
    """
    d1 = chart_dict["vargas"]["D1"]
    lagna = d1["lagna"]
    asc_sign = lagna["sign"]
    asc_deg_in_sign = float(lagna.get("degree_0_to_30", lagna["longitude"] % 30.0))
    asc_sign_idx = ZODIAC_SIGNS.index(asc_sign)

    d1_grahas = d1["grahas"]

    houses: Dict[int, Dict[str, Any]] = {}
    for h in range(1, 13):
        sign_idx = (asc_sign_idx + h - 1) % 12
        sign_name = ZODIAC_SIGNS[sign_idx]
        lord = SIGN_LORDS[sign_name]
        cusp_lon = (sign_idx * 30.0 + asc_deg_in_sign) % 360.0

        occupants = [
            p for p in CLASSICAL_PLANETS
            if d1_grahas.get(p, {}).get("sign") == sign_name
        ]

        houses[h] = {
            "house": h,
            "sign": sign_name,
            "sign_index": sign_idx,
            "lord": lord,
            "cusp_longitude": round(cusp_lon, 4),
            "cusp_degree": round(asc_deg_in_sign, 4),
            "occupants": occupants
        }

    return {
        "ascendant_sign": asc_sign,
        "ascendant_degree": round(asc_deg_in_sign, 4),
        "ascendant_longitude": round(float(lagna["longitude"]), 4),
        "houses": houses
    }


def calculate_functional_nature(
    reference_sign: str,
    d1_grahas: Optional[Dict[str, Any]] = None
) -> Dict[str, Dict[str, Any]]:
    """
    Implements Phase 2: Planetary Functional Nature Quantification (F_P).
    Incorporates Phaladīpikā Ch. 15 Rules 1-4, Svakṣetra dual-lordship overrides (15.29),
    Moon Pakṣa Bala elongation, Mercury malefic association, and BPHS Ch. 34 Yogakaraka adjustments.
    """
    ref_idx = ZODIAC_SIGNS.index(reference_sign)

    def house_of_sign(sign_name: str) -> int:
        idx = ZODIAC_SIGNS.index(sign_name)
        return ((idx - ref_idx) % 12) + 1

    results: Dict[str, Dict[str, Any]] = {}

    # Calculate Moon brightness (Pakṣa Bala) if chart planetary positions exist
    moon_inherent = 0.5
    if d1_grahas and "Moon" in d1_grahas and "Sun" in d1_grahas:
        try:
            m_lon = float(d1_grahas["Moon"]["longitude"])
            s_lon = float(d1_grahas["Sun"]["longitude"])
            delta_moon_sun = _shortest_distance(m_lon, s_lon)
            paksa_factor = delta_moon_sun / 180.0
            if delta_moon_sun >= 165.0:
                moon_inherent = 1.0
            else:
                moon_inherent = round(-0.5 + 1.5 * paksa_factor, 4)
        except (KeyError, TypeError, ValueError):
            moon_inherent = 0.5

    # Check Mercury condition: afflicted if within 10 deg of malefic in same sign
    merc_inherent = 0.5
    if d1_grahas and "Mercury" in d1_grahas:
        try:
            merc_sign = d1_grahas["Mercury"].get("sign")
            merc_lon = float(d1_grahas["Mercury"]["longitude"])
            for mal in ["Mars", "Saturn", "Rahu", "Ketu"]:
                if mal in d1_grahas and d1_grahas[mal].get("sign") == merc_sign:
                    mal_lon = float(d1_grahas[mal]["longitude"])
                    if _shortest_distance(merc_lon, mal_lon) <= 10.0:
                        merc_inherent = -0.5
                        break
        except (KeyError, TypeError, ValueError):
            merc_inherent = 0.5

    for p in CLASSICAL_PLANETS:
        mt_sign = DICARA_MOOLATRIKONA_SIGNS[p]
        dom_sign = DICARA_DOMICILE_SIGNS[p]

        # Owned houses for actual sign lordships (Moon owns Cancer; Taurus is MT root)
        owned_houses: List[int] = []
        if p == "Sun":
            owned_houses = [house_of_sign("Leo")]
        elif p == "Moon":
            owned_houses = [house_of_sign("Cancer")]
        else:
            owned_houses = [house_of_sign(mt_sign)]
            if dom_sign:
                owned_houses.append(house_of_sign(dom_sign))

        # Base inherent temperament
        if p == "Moon":
            inherent_score = moon_inherent
        elif p == "Mercury":
            inherent_score = merc_inherent
        elif p == "Sun":
            inherent_score = -0.5
        else:
            inherent_score = NATURAL_TEMPERAMENT.get(p, 0.0)

        # Rule 1: 1st House Lord check (unconditional flat +3)
        if 1 in owned_houses:
            results[p] = {
                "score": 3.0,
                "classification": "Benefic",
                "rule_breakdown": {
                    "is_first_lord": True,
                    "trine_score": 0.0,
                    "dusthana_score": 0.0,
                    "inherent_score": inherent_score
                }
            }
            continue

        # Rule 2 & 3: Trines (5, 9) and Dusthānas (6, 8, 12)
        trine_score = 0.0
        dusthana_score = 0.0

        h_mt = house_of_sign(mt_sign)
        h_dom = house_of_sign(dom_sign) if dom_sign else None

        # Special Edge Case for Moon: Sagittarius Lagna (Taurus = H6, Cancer = H8)
        if p == "Moon" and h_mt in [6, 8, 12] and h_dom in [6, 8, 12]:
            dusthana_score = -2.0
        else:
            if h_mt in [5, 9]:
                trine_score += 2.0
            elif h_mt in [6, 8, 12]:
                dusthana_score -= 2.0

            if h_dom:
                if h_dom in [5, 9]:
                    trine_score += 1.0
                elif h_dom in [6, 8, 12]:
                    dusthana_score -= 1.0

        # Svakṣetra Dual-Lordship Override (Phaladīpikā 15.29):
        # When a planet physically occupies one of its own signs corresponding to a non-Dusthāna house,
        # its secondary Dusthāna lordship blemish is waived.
        if d1_grahas and p in d1_grahas:
            p_sign = d1_grahas[p].get("sign")
            valid_own = [mt_sign]
            if dom_sign:
                valid_own.append(dom_sign)
            if p_sign in valid_own:
                h_occ = house_of_sign(p_sign)
                if h_occ not in [6, 8, 12]:
                    dusthana_score = 0.0

        # Rule 4: Inherent temperament + Classical Yogakāraka adjustment (BPHS Ch. 34)
        owns_kendra = any(h in [4, 7, 10] for h in owned_houses)
        owns_trine = any(h in [5, 9] for h in owned_houses)

        if owns_kendra and owns_trine:
            # Supreme Raja Yogakaraka (Mars for Cancer/Leo, Saturn for Taurus/Libra)
            inherent_score = max(0.0, inherent_score) + 1.0

        net_f = trine_score + dusthana_score + inherent_score
        classification = "Benefic" if net_f > 0 else ("Malefic" if net_f < 0 else "Neutral")

        results[p] = {
            "score": round(net_f, 2),
            "classification": classification,
            "rule_breakdown": {
                "is_first_lord": False,
                "trine_score": round(trine_score, 2),
                "dusthana_score": round(dusthana_score, 2),
                "inherent_score": round(inherent_score, 2)
            }
        }

    return results


def scale_by_dignity(base_val: float, dignity_unit: float, functional_score: float) -> float:
    """
    Universal Dignity-Scaling Law (Phase 3).
    Scales a non-negative base magnitude by the planet's dignity d_P in [-1.0, +1.0]
    according to functional score F.
    Severe debilitation (d = -1.0) retains only 0.20x of good results per Phaladīpikā 15.18.
    """
    b = abs(base_val)
    d = max(-1.0, min(1.0, float(dignity_unit)))

    if functional_score == 0.0:
        return b * d
    elif functional_score > 0:
        if d >= 0:
            return b * (1.0 + d)
        else:
            return b * (1.0 - 0.80 * abs(d))
    else:  # functional_score < 0
        if d <= 0:
            return b * (1.0 + abs(d))
        else:
            return b * (1.0 - d / 2.0)


def _compute_signed_ray_impact(
    base_val: float,
    dignity_unit: float,
    functional_score: float,
    slope: float = 0.65
) -> float:
    """
    Computes smooth continuous signed ray impact across the functional spectrum,
    eliminating cliff edges and deadband sign inversions across [-0.25, +0.25].
    """
    b = abs(base_val)
    d = max(-1.0, min(1.0, float(dignity_unit)))
    f = float(functional_score)

    if f >= 0.25:
        scaled_pos = scale_by_dignity(b, d, 1.0)
        f_mult = 1.0 + slope * (f - 1.0)
        return scaled_pos * f_mult
    elif f <= -0.25:
        scaled_neg = scale_by_dignity(b, d, -1.0)
        f_mult = -(1.0 + slope * (abs(f) - 1.0))
        return scaled_neg * f_mult
    else:
        signed_zero = b * d
        if f >= 0.0:
            w = f / 0.25
            val_pos = scale_by_dignity(b, d, 1.0) * (1.0 + slope * (0.25 - 1.0))
            return (1.0 - w) * signed_zero + w * val_pos
        else:
            w = -f / 0.25
            val_neg = scale_by_dignity(b, d, -1.0) * -(1.0 + slope * (0.25 - 1.0))
            return (1.0 - w) * signed_zero + w * val_neg


def calculate_cusp_and_planet_influences(
    geometry: Dict[str, Any],
    d1_grahas: Dict[str, Any],
    adv_aspects: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Computes degree-specific aspects and conjunctions on a 0-100% scale (Phase 4),
    applying cross-border halving and multi-planet cusp dominance (potency stealing).
    """
    planet_to_planet: Dict[str, Dict[str, float]] = {p: {} for p in CLASSICAL_PLANETS}

    # 1. Planet to Planet interactions
    for sender in CLASSICAL_PLANETS:
        s_lon = float(d1_grahas[sender]["longitude"])
        s_sign = d1_grahas[sender]["sign"]

        for receiver in CLASSICAL_PLANETS:
            if sender == receiver:
                continue
            r_lon = float(d1_grahas[receiver]["longitude"])
            r_sign = d1_grahas[receiver]["sign"]

            # Aspect Virūpas
            virupas = 0.0
            p_aspects = adv_aspects.get("planets", {}).get(sender, {})
            if receiver in p_aspects:
                entry = p_aspects[receiver]
                virupas = entry.get("raw", 0.0) if isinstance(entry, dict) else float(entry)
            else:
                virupas = aspects.get_graha_drishti(sender, s_lon, r_lon)

            aspect_pct = (virupas / 60.0) * 100.0

            # Conjunction within 30 deg
            dist = _shortest_distance(s_lon, r_lon)
            conj_pct = 0.0
            if dist < 30.0:
                raw_c = (1.0 - dist / 30.0) * 100.0
                conj_pct = raw_c * 0.5 if s_sign != r_sign else raw_c

            # Mutual sign exchange (Parivartana / Mitho Yoga per Phaladīpikā 15.30)
            is_parivartana = (
                s_sign != r_sign
                and SIGN_LORDS.get(s_sign) == receiver
                and SIGN_LORDS.get(r_sign) == sender
            )
            pariv_pct = 50.0 if is_parivartana else 0.0

            planet_to_planet[sender][receiver] = max(aspect_pct, conj_pct, pariv_pct)

    # 2. Planet to House Cusp interactions with Multi-Planet Cusp Dominance
    raw_conjunctions: Dict[str, Dict[int, float]] = {p: {} for p in CLASSICAL_PLANETS}
    adjusted_conjunctions: Dict[str, Dict[int, float]] = {p: {} for p in CLASSICAL_PLANETS}
    planet_to_cusp: Dict[str, Dict[int, float]] = {p: {} for p in CLASSICAL_PLANETS}

    houses_dict = geometry["houses"]

    # Compute raw conjunctions and aspect percentages to each house cusp
    for h, h_data in houses_dict.items():
        cusp_lon = h_data["cusp_longitude"]
        occupants = h_data["occupants"]

        # Raw conjunction for occupants in this sign (linear 30° orb per Phase 4.2)
        occ_raw: Dict[str, float] = {}
        for p in occupants:
            p_lon = float(d1_grahas[p]["longitude"])
            dist = _shortest_distance(p_lon, cusp_lon)
            raw_c = max(0.0, (1.0 - dist / 30.0) * 100.0)
            raw_conjunctions[p][h] = raw_c
            occ_raw[p] = raw_c

        # Multi-planet cusp dominance stealing within the sign (order-independent pairwise stealing)
        if len(occupants) == 1:
            p_solo = occupants[0]
            adjusted_conjunctions[p_solo][h] = occ_raw[p_solo]
        elif len(occupants) >= 2:
            sorted_occ = sorted(occupants, key=lambda p: occ_raw[p], reverse=True)
            cur_conjunctions = {p: occ_raw[p] for p in sorted_occ}

            for i in range(len(sorted_occ)):
                near_p = sorted_occ[i]
                near_lon = float(d1_grahas[near_p]["longitude"])
                for j in range(i + 1, len(sorted_occ)):
                    far_p = sorted_occ[j]
                    far_lon = float(d1_grahas[far_p]["longitude"])
                    dist_between = _shortest_distance(near_lon, far_lon)
                    c_near = cur_conjunctions[near_p]
                    c_far = cur_conjunctions[far_p]

                    if dist_between < 15.0 and occ_raw[near_p] > occ_raw[far_p] and (c_near + c_far) > 0:
                        orb_factor = 1.0 - (dist_between / 15.0)
                        steal = c_far * (c_near / (c_near + c_far)) * orb_factor
                        steal = min(steal, cur_conjunctions[far_p])
                        avail_cap = max(0.0, 125.0 - cur_conjunctions[near_p])
                        steal = min(steal, avail_cap)
                        cur_conjunctions[far_p] = max(0.0, cur_conjunctions[far_p] - steal)
                        cur_conjunctions[near_p] = min(125.0, cur_conjunctions[near_p] + steal)

            for p in occupants:
                adjusted_conjunctions[p][h] = cur_conjunctions[p]

        # Non-occupants: cross-border conjunction (if within 30 deg) and Graha Drishti aspect
        for p in CLASSICAL_PLANETS:
            if p in occupants:
                continue
            p_lon = float(d1_grahas[p]["longitude"])
            dist = _shortest_distance(p_lon, cusp_lon)
            raw_c = max(0.0, (1.0 - dist / 30.0) * 100.0) if dist < 30.0 else 0.0
            # Spans across sign boundary -> halved
            halved_c = raw_c * 0.5
            raw_conjunctions[p][h] = halved_c
            adjusted_conjunctions[p][h] = halved_c

        # Final planet_to_cusp impact: pure Parāśara Sphuṭa Dṛṣṭi degree-based aspect
        for p in CLASSICAL_PLANETS:
            p_lon = float(d1_grahas[p]["longitude"])
            virupas = aspects.get_graha_drishti(p, p_lon, cusp_lon)
            asp_pct = (virupas / 60.0) * 100.0
            final_c = adjusted_conjunctions[p][h]
            planet_to_cusp[p][h] = max(asp_pct, final_c)

    return {
        "planet_to_planet": planet_to_planet,
        "planet_to_cusp": planet_to_cusp,
        "raw_conjunctions": raw_conjunctions,
        "adjusted_conjunctions": adjusted_conjunctions
    }


def evaluate_planets_hol(
    geometry: Dict[str, Any],
    d1_grahas: Dict[str, Any],
    func_natures: Dict[str, Any],
    influences: Dict[str, Any],
    chart_dict: Optional[Dict[str, Any]] = None
) -> Dict[str, Dict[str, Any]]:
    """
    Implements Phase 5: Comprehensive Planetary Assessment across 5 factors.
    Strictly separates Intrinsic Quality (Dignity, Aspects, Digbala) from
    Prominence (Cusp Alignment & House Category), preventing Kendra cusps from
    flipping debilitated planets positive. Incorporates Phaladīpikā 3.9 vilagna protection.
    """
    planet_results: Dict[str, Dict[str, Any]] = {}
    p2p = influences["planet_to_planet"]
    adj_conj = influences["adjusted_conjunctions"]
    raw_conj = influences["raw_conjunctions"]

    # First pass: gather combustion losses
    sun_lon = float(d1_grahas["Sun"]["longitude"])
    combustion_losses: Dict[str, float] = {}

    for p in CLASSICAL_PLANETS:
        if p == "Sun":
            continue
        p_data = d1_grahas[p]
        p_lon = float(p_data["longitude"])

        dist_sun = p_data.get("sun_distance")
        if dist_sun is None:
            dist_sun = _shortest_distance(p_lon, sun_lon)
        else:
            dist_sun = float(dist_sun)

        orb = p_data.get("combustion_orb")
        if orb is None:
            is_retro = p_data.get("is_retrograde", False)
            if p == "Venus" and is_retro:
                orb = 8.0
            elif p == "Mercury" and is_retro:
                orb = 12.0
            else:
                orb = COMBUSTION_ORBS.get(p, 10.0)
        else:
            orb = float(orb)

        if dist_sun <= orb and orb > 0:
            loss = max(0.0, min(1.0, 1.0 - (dist_sun / orb)))
        else:
            loss = 0.0
        combustion_losses[p] = loss

    solar_gain_sum = sum(combustion_losses.values())

    # Second pass: compute full planetary condition
    for p in CLASSICAL_PLANETS:
        p_data = d1_grahas[p]
        p_lon = float(p_data["longitude"])
        p_sign = p_data["sign"]
        p_deg_in_sign = float(p_data.get("degree_0_to_30", p_data["longitude"] % 30.0))
        p_ruled = p_data.get("ruled_houses", [])

        # Find house occupied
        p_house = 1
        for h, h_data in geometry["houses"].items():
            if h_data["sign"] == p_sign:
                p_house = h
                break

        # 1. Multi-Varga Composite Dignity (D1 + D9 per Phaladīpikā 3.4 & 3.11)
        d_p = _get_composite_dignity_unit(p, chart_dict, d1_grahas)
        d_pct = d_p * 100.0
        dignity_status = _get_dignity_status(p_data)
        d_d1 = DICARA_D1_DIGNITY_MAP.get(dignity_status, 0.0)

        # 3. Canonical Digbala & Bala Points (Phaladīpikā Ch. 4)
        _, digbala_pts = _get_bala_and_digbala_bonus(p, p_house, chart_dict)

        # 2. Combined Incoming Influences
        incoming_breakdown: Dict[str, float] = {}
        raw_net_inf = 0.0
        for q in CLASSICAL_PLANETS:
            if q == p:
                continue
            i_val = p2p[q][p]
            d_q = _get_composite_dignity_unit(q, chart_dict, d1_grahas)
            f_q = func_natures[q]["score"]

            # Smooth continuous signed ray impact across functional spectrum (slope=0.20 for planet-to-planet)
            signed_impact = _compute_signed_ray_impact(i_val, d_q, f_q, slope=0.20)

            # Attenuate same-house Dusthāna conjunction boosts by 0.50x if planet is in Enemy/Debility with negative Digbala
            q_sign = d1_grahas[q]["sign"]
            q_house = 1
            for h_chk, h_data_chk in geometry["houses"].items():
                if h_data_chk["sign"] == q_sign:
                    q_house = h_chk
                    break

            if d_d1 < 0 and p_house in [6, 8, 12] and digbala_pts < 0:
                if q_house == p_house and signed_impact > 0:
                    signed_impact *= 0.50

            incoming_breakdown[q] = round(signed_impact, 2)
            raw_net_inf += signed_impact

        # Nodal Conjunction & Eclipse Affliction (Phaladīpikā Ch. 3 / Ch. 15)
        eclipse_loss = 0.0
        p_lon = float(p_data["longitude"])
        for node in ["Rahu", "Ketu"]:
            if node in d1_grahas and d1_grahas[node].get("sign") == p_sign:
                n_lon = float(d1_grahas[node].get("longitude", 0.0))
                dist_to_node = _shortest_distance(p_lon, n_lon)
                if dist_to_node <= 15.0:
                    node_conj = (1.0 - dist_to_node / 15.0) * 100.0
                    if p in ["Sun", "Moon"]:
                        node_pen = 0.85 * node_conj
                        loss_factor = 0.15 * (1.0 - dist_to_node / 15.0)
                        if p == "Sun" and p_house in [3, 6, 11] and d_p >= 0.4:
                            node_pen *= 0.50
                            loss_factor *= 0.50
                        if dist_to_node <= 12.0:
                            eclipse_loss = max(eclipse_loss, loss_factor)
                    else:
                        node_pen = 0.50 * node_conj
                        if p_house in [3, 6, 11]:
                            node_pen *= 0.50
                    incoming_breakdown[node] = round(-node_pen, 2)
                    raw_net_inf -= node_pen

        net_inf = max(-150.0, min(150.0, raw_net_inf / 2.5))

        # 4. Intrinsic Quality Base (Quality does NOT include raw cusp proximity points)
        quality_base = 0.50 * d_pct + 0.35 * net_inf + 0.15 * digbala_pts

        # 5. Cusp Alignment & House Placement Prominence
        raw_c = raw_conj[p].get(p_house, 0.0)
        adj_c = adj_conj[p].get(p_house, 0.0)
        capped_base = min(100.0, adj_c)
        cusp_prox_factor = 0.80 + 0.40 * (capped_base / 100.0)

        if p_house in [1, 4, 5, 9, 10]:
            h_category = "Prominent"
            base_h_mult = 1.25
        elif p_house in [2, 7, 11]:
            h_category = "Regular"
            base_h_mult = 1.00
        else:  # [3, 6, 8, 12]
            h_category = "Hidden"
            if p_house in [6, 8, 12] and any(rh in [6, 8, 12] for rh in p_ruled):
                base_h_mult = 1.00  # Dusthāna lord in Dusthāna (Viparīta resilience)
            elif p_house == 3 and (3 in p_ruled or p in ["Sun", "Mars", "Saturn"]):
                base_h_mult = 0.90  # 3rd lord or natural malefics in 3rd Upacaya
            elif p_house == 3:
                base_h_mult = 0.75  # Mild Upacaya house
            elif p_house == 6 and p in ["Sun", "Mars", "Saturn"]:
                base_h_mult = 0.85  # Natural malefics in 6th Upacaya conquer obstacles
            elif p_house == 12 and (p == "Venus" or d_p >= 0.4):
                base_h_mult = 0.90  # Venus or dignified planet in 12th
            else:
                base_h_mult = 0.75  # Moderated Dusthāna expression
            if p_house in [6, 8, 12] and d_d1 < 0:
                base_h_mult *= 0.70

        effective_h_mult = base_h_mult * cusp_prox_factor

        # Apply House Placement Modifier to QualityBase
        if quality_base >= 0.0:
            base_avg = quality_base * effective_h_mult
        else:
            if p_house == 1:
                # Phaladīpikā 3.9 vilagna protection: softens negative dignity strain in 1st house by 0.5x
                base_avg = quality_base * 0.50 * cusp_prox_factor
            elif p_house in [4, 5, 9, 10]:
                base_avg = quality_base * effective_h_mult
            elif p_house in [6, 8, 12]:
                if any(rh in [6, 8, 12] for rh in p_ruled):
                    base_avg = quality_base * 0.90 * cusp_prox_factor
                else:
                    base_avg = quality_base * 1.20 * cusp_prox_factor
            else:
                base_avg = quality_base * effective_h_mult

        # 6. Bhāva Sandhi (4.0 deg border threshold, relieved by Cusp Proximity per Phaladīpikā 15.14 & 8.34-35)
        dist_border = min(p_deg_in_sign, 30.0 - p_deg_in_sign)
        if dist_border < 4.0:
            raw_sandhi_pen = max(0.0, 1.0 - (dist_border / 4.0))
            cusp_lon_h = float(geometry["houses"][p_house].get("cusp_longitude", p_lon))
            cusp_deg = cusp_lon_h % 30.0
            cusp_dist_border = min(cusp_deg, 30.0 - cusp_deg)
            dist_to_cusp = _shortest_distance(p_lon, cusp_lon_h)

            # Phaladīpikā 15.14 & 8.34-35:
            # If the house cusp itself is near the border (< 4.0°) and the planet is inside the house
            # between the cusp and sign center (dist_border >= cusp_dist_border), or tightly conjunct
            # the cusp (dist_to_cusp <= 5.0), the planet is at the cusp door, not drifting into the junction.
            if (cusp_dist_border < 4.0 and dist_border >= cusp_dist_border) or dist_to_cusp <= 5.0:
                cusp_relief = 0.0
            elif dist_to_cusp < 10.0:
                cusp_relief = (dist_to_cusp - 5.0) / 5.0
            else:
                cusp_relief = 1.0

            sandhi_penalty = raw_sandhi_pen * cusp_relief
            in_sandhi = sandhi_penalty > 0.0
        else:
            sandhi_penalty = 0.0
            in_sandhi = False
        retention_multiplier = 1.0 - sandhi_penalty

        # 7. Combustion & Solar Transfer
        if p == "Sun":
            is_combust = False
            dist_sun = 0.0
            tolerance_orb = None
            loss_ratio = 0.0
            solar_gain_ratio = round(min(0.50, solar_gain_sum * 0.25), 4)
            combustion_multiplier = 1.0 + solar_gain_ratio
        else:
            loss_ratio = combustion_losses.get(p, 0.0)
            is_combust = loss_ratio > 0.0
            dist_sun = float(p_data.get("sun_distance", _shortest_distance(float(p_data["longitude"]), sun_lon)))
            tolerance_orb = p_data.get("combustion_orb")
            solar_gain_ratio = 0.0
            combustion_multiplier = 1.0 - loss_ratio

        # Synthesis (Sign-Safe Application of Sandhi, Combustion & Eclipse)
        if base_avg >= 0.0:
            if p == "Sun":
                final_assessment = base_avg * (1.0 - 0.5 * sandhi_penalty) * combustion_multiplier * (1.0 - eclipse_loss)
            else:
                final_assessment = base_avg * (1.0 - 0.5 * sandhi_penalty) * (1.0 - 0.75 * loss_ratio) * (1.0 - eclipse_loss)
        else:
            if p == "Sun":
                strain_mult = 1.0 + 0.25 * sandhi_penalty + eclipse_loss
                final_assessment = (base_avg * strain_mult) + (10.0 * solar_gain_ratio)
            else:
                strain_mult = 1.0 + 0.25 * sandhi_penalty + 0.35 * loss_ratio + eclipse_loss
                final_assessment = base_avg * strain_mult

        planet_results[p] = {
            "sign": p_sign,
            "house": p_house,
            "degree_in_sign": round(p_deg_in_sign, 2),
            "ruled_houses": p_ruled,
            "functional_nature": func_natures[p],
            "dignity": {
                "status": dignity_status,
                "unit_score": round(d_p, 2),
                "pct_score": round(d_pct, 2)
            },
            "combined_influences": {
                "net_score": round(net_inf, 2),
                "incoming_breakdown": incoming_breakdown
            },
            "cusp_alignment": {
                "raw_conjunction_pct": round(raw_c, 2),
                "dominance_adjusted_pct": round(adj_c, 2),
                "capped_base_pct": round(capped_base, 2),
                "house_category": h_category,
                "house_multiplier": round(effective_h_mult, 4),
                "alignment_score": round(capped_base * effective_h_mult, 2),
                "digbala_points": round(digbala_pts, 2),
            },
            "bhava_sandhi": {
                "distance_to_border": round(dist_border, 2),
                "in_sandhi_zone": in_sandhi,
                "penalty_ratio": round(sandhi_penalty, 4),
                "retention_multiplier": round(retention_multiplier, 4)
            },
            "combustion": {
                "is_combust": is_combust,
                "distance_to_sun": round(dist_sun, 2),
                "tolerance_orb": tolerance_orb,
                "loss_ratio": round(loss_ratio, 4),
                "solar_gain_ratio": solar_gain_ratio,
                "combustion_multiplier": round(combustion_multiplier, 4)
            },
            "eclipse": {
                "is_eclipsed": eclipse_loss > 0.0,
                "loss_ratio": round(eclipse_loss, 4)
            },
            "quality_base_score": round(quality_base, 2),
            "cusp_proximity_factor": round(cusp_prox_factor, 2),
            "base_average_score": round(base_avg, 2),
            "final_assessment_score": round(final_assessment, 2)
        }

    return planet_results


def evaluate_basic_house_conditions(
    geometry: Dict[str, Any],
    func_natures: Dict[str, Any],
    d1_grahas: Dict[str, Any],
    influences: Dict[str, Any],
    planets_eval: Optional[Dict[str, Any]] = None
) -> Dict[int, Dict[str, Any]]:
    """
    Implements Phase 6: Basic House Condition — Direct Evaluation.
    Condition-gates cusp influences by combustion and Bhāva Sandhi (Phaladīpikā 15.1 amūḍha-hīnāḥ).
    Transforms natural malefics in Upacayas (3, 6, 11) into resilience boosters (15.18).
    Evaluates Rāhu & Ketu cusp occupancy, proximity, and malefic aggravation (15.8).
    Uses a fixed baseline divisor (4.0) with hyperbolic tangent saturation guaranteeing strict monotonicity.
    """
    house_results: Dict[int, Dict[str, Any]] = {}
    p2c = influences["planet_to_cusp"]

    for h, h_data in geometry["houses"].items():
        lord = h_data["lord"]
        occupants = set(h_data.get("occupants", []))
        cusp_lon = float(h_data.get("cusp_longitude", 0.0))
        contributions: Dict[str, float] = {}
        total_signed = 0.0

        for p in CLASSICAL_PLANETS:
            i_val = p2c[p][h]
            if planets_eval and p in planets_eval and "dignity" in planets_eval[p]:
                d_p = float(planets_eval[p]["dignity"].get("unit_score", 0.0))
            else:
                dignity_status = _get_dignity_status(d1_grahas[p])
                d_p = DICARA_D1_DIGNITY_MAP.get(dignity_status, 0.0)

            # House Lord vs Non-Lord on House Cusp (Phaladīpikā 15.1–15.5, 15.7)
            if p == lord:
                f_eff = 2.0
            else:
                lagna_f = float(func_natures[p]["score"])
                inh_score = float(func_natures[p].get("rule_breakdown", {}).get("inherent_score", 0.0))
                h_sign = h_data.get("sign")

                # Check if target house sign is planet P's Exaltation or Mūlatrikoṇa / Domicile sign
                # Restrict to non-malefics (inh_score >= 0.0 or lagna_f >= 0.0) so functional malefics
                # don't receive an artificial +0.50 friendship bonus when aspecting an enemy sign
                is_exalt_or_root = (
                    (
                        h_sign == DICARA_MOOLATRIKONA_SIGNS.get(p)
                        or h_sign == EXALTATION_SIGNS.get(p)
                        or SIGN_LORDS.get(h_sign) == p
                    )
                    and (inh_score >= 0.0 or lagna_f >= 0.0)
                )

                rel_p_to_l = get_natural_relationship(p, lord)
                rel_l_to_p = get_natural_relationship(lord, p)
                if is_exalt_or_root:
                    # If target sign is planet's own exaltation or root sign (e.g. Moon on Taurus),
                    # it loves that sign and never receives negative friendship
                    friend_mod = 0.50
                elif rel_p_to_l == "Friend" and rel_l_to_p == "Friend":
                    friend_mod = 0.50
                elif "Enemy" in (rel_p_to_l, rel_l_to_p):
                    friend_mod = -0.50
                elif "Friend" in (rel_p_to_l, rel_l_to_p):
                    friend_mod = 0.25
                else:
                    friend_mod = 0.0

                # Scale lagna_f by 0.50 so non-lords stay bounded on the [-2.0, +2.0] scale
                # below or equal to the House Lord (2.0), preserving Yogakāraka status and natural benefic cushions (15.1, 15.7):
                f_eff = 0.50 * lagna_f + 0.50 * inh_score + 0.35 * friend_mod

            eff_i_val = i_val

            # Continuous scaling across functional spectrum (eliminates 0.15 deadband cliff)
            signed_impact = _compute_signed_ray_impact(eff_i_val, d_p, f_eff, slope=0.65)

            # Upacaya (3, 6, 11) Malefic Occupant Rule (Phaladīpikā 15.18 & Ch. 4):
            # Only converts when the planet is functioning as a malefic (f_eff < 0).
            # Benefic 1st Lords / Yogakārakas are NEVER slashed.
            # Dignity scales the resilience boost positively (exalted gives strong resilience; debilitated weak).
            is_upacaya_occ = False
            if p in occupants and p != lord and p in ["Sun", "Mars", "Saturn"] and h in [3, 6, 11] and f_eff < 0.0:
                pos_scaled = scale_by_dignity(eff_i_val, d_p, 1.0)
                signed_impact = pos_scaled * 0.35
                is_upacaya_occ = True

            # Condition-Gate Cusp Influences by Combustion & Bhāva Sandhi (Phaladīpikā 15.1 amūḍha-hīnāḥ)
            # Attenuate positive rays from planets afflicted by negative multi-varga dignity (arinīca-mūḍha)
            p_lon_val = float(d1_grahas[p].get("longitude", 0.0))
            p_sign = d1_grahas[p].get("sign") or ZODIAC_SIGNS[int(p_lon_val // 30) % 12]
            p_occ_house = 1
            if planets_eval and p in planets_eval and "house" in planets_eval[p]:
                p_occ_house = int(planets_eval[p]["house"])
            else:
                for h_chk, h_data_chk in geometry["houses"].items():
                    if h_data_chk.get("sign") == p_sign:
                        p_occ_house = int(h_chk)
                        break

            comb_loss = 0.0
            sandhi_pen = 0.0
            if planets_eval and p in planets_eval:
                comb_loss = float(planets_eval[p].get("combustion", {}).get("loss_ratio", 0.0))
                sandhi_pen = float(planets_eval[p].get("bhava_sandhi", {}).get("penalty_ratio", 0.0))

            condition_integrity = (1.0 - 0.75 * comb_loss) * (1.0 - 0.50 * sandhi_pen)
            if signed_impact > 0:
                # Use composite dignity d_p (Phaladīpikā 3.4 & 3.11: D9/Vargottama rescues D1)
                # Soften attenuation smoothly based on negative composite dignity
                if not is_upacaya_occ and d_p < 0.0:
                    condition_integrity *= (1.0 - 0.40 * abs(d_p))
                    if p_occ_house in [6, 8, 12]:
                        condition_integrity *= 0.75
                signed_impact *= condition_integrity
            elif signed_impact < 0:
                signed_impact *= (1.0 + 0.35 * comb_loss) * (1.0 - 0.30 * sandhi_pen)

            contributions[p] = round(signed_impact, 2)
            total_signed += signed_impact

        # Rāhu and Ketu Cusp Occupancy / Proximity Impact (Phaladīpikā 15.8)
        for node in ["Rahu", "Ketu"]:
            if node in d1_grahas:
                node_data = d1_grahas[node]
                node_sign = node_data.get("sign")
                node_lon = float(node_data.get("longitude", 0.0))
                dist_node = _shortest_distance(node_lon, cusp_lon)
                if node_sign == h_data["sign"] or dist_node <= 15.0:
                    if node_sign == h_data["sign"]:
                        c_node = max(35.0, (1.0 - dist_node / 30.0) * 100.0)
                    else:
                        c_node = 0.50 * (1.0 - dist_node / 30.0) * 100.0

                    if h in [3, 6, 11]:
                        node_impact = 0.35 * c_node
                    else:
                        node_dignity = _get_dignity_status(node_data)
                        is_mitigated = ("Friend" in node_dignity or "Own" in node_dignity or "Exalt" in node_dignity)
                        if not is_mitigated:
                            for b in ["Jupiter", "Venus"]:
                                if b in d1_grahas:
                                    b_lon = float(d1_grahas[b].get("longitude", 0.0))
                                    b_sign = d1_grahas[b].get("sign")
                                    if b_sign == node_sign:
                                        is_mitigated = True
                                        break
                                    if aspects.get_graha_drishti(b, b_lon, node_lon) >= 30.0:
                                        is_mitigated = True
                                        break

                        # Check malefic aggravation by Mars or Saturn (Phaladīpikā 15.8)
                        is_aggravated = False
                        if not is_mitigated:
                            for m in ["Mars", "Saturn"]:
                                if m in d1_grahas:
                                    m_lon = float(d1_grahas[m].get("longitude", 0.0))
                                    m_sign = d1_grahas[m].get("sign")
                                    if m_sign == node_sign or aspects.get_graha_drishti(m, m_lon, node_lon) >= 30.0:
                                        is_aggravated = True
                                        break

                        mit_factor = 0.50 if is_mitigated else (1.25 if is_aggravated else 1.00)
                        node_impact = -0.60 * c_node * mit_factor
                    contributions[node] = round(node_impact, 2)
                    total_signed += node_impact

        # Fixed baseline divisor (4.0) with hyperbolic tangent saturation (monotonicity guarantee per Phase 8/9 standard)
        raw_house_score = total_signed / 4.0
        bounded_score = 120.0 * math.tanh(raw_house_score / 120.0)

        house_results[h] = {
            "score": round(bounded_score, 2),
            "planet_contributions": contributions
        }

    return house_results


def evaluate_relative_houses_bhavat_bhavam(
    geometry: Dict[str, Any],
    d1_grahas: Dict[str, Any],
    influences: Dict[str, Any],
    planets_eval: Optional[Dict[str, Any]] = None,
    func_natures: Optional[Dict[str, Any]] = None
) -> Dict[int, Dict[str, Any]]:
    """
    Implements Phase 7: Relative House Technique — Bhavāt Bhavam (Phaladīpikā 15.2, 15.3, 15.5).
    Corrects the House Lord in relative 6/8/12 inversion (Bhāva-nāśa ruination).
    Includes degree-aspect proximity bonuses for the Lord in Kendra/Trine/2nd.
    Evaluates relative Dusthāna/Triṣaḍāya lords in Relative H1.
    Removes unclassical b_dust_count global mitigations per Phaladīpikā 15.4.
    Blends relative functional nature with natal functional nature (70/30) and protects Lagna Lord.
    """
    results: Dict[int, Dict[str, Any]] = {}
    p2p = influences["planet_to_planet"]

    planet_houses: Dict[str, int] = {}
    for p in CLASSICAL_PLANETS:
        p_sign = d1_grahas[p]["sign"]
        for h, h_data in geometry["houses"].items():
            if h_data["sign"] == p_sign:
                planet_houses[p] = h
                break

    asc_sign = geometry.get("ascendant_sign") or geometry.get("houses", {}).get(1, {}).get("sign", "Aries")
    asc_first_lord = SIGN_LORDS.get(asc_sign, "Mars")

    for h, h_data in geometry["houses"].items():
        lord = h_data["lord"]
        cusp_lon = float(h_data.get("cusp_longitude", 0.0))
        h_sign = h_data.get("sign", "Aries")
        rel_func = calculate_functional_nature(h_sign, d1_grahas=d1_grahas)
        raw_rel_scores: Dict[str, float] = {}
        eff_rel_scores: Dict[str, float] = {}
        rel_func_pts: Dict[str, float] = {}

        for p in CLASSICAL_PLANETS:
            if planets_eval and p in planets_eval and "dignity" in planets_eval[p]:
                d_p = float(planets_eval[p]["dignity"].get("unit_score", 0.0))
            else:
                dignity_status = _get_dignity_status(d1_grahas[p])
                d_p = DICARA_D1_DIGNITY_MAP.get(dignity_status, 0.0)
            raw_f = float(rel_func[p]["score"])
            if func_natures and p in func_natures:
                natal_f = float(func_natures[p]["score"])
                raw_f = 0.70 * raw_f + 0.30 * natal_f
                if p == asc_first_lord:
                    raw_f = max(0.50, raw_f)
            raw_rel_scores[p] = raw_f
            eff_f = raw_f if raw_f != 0.0 else d_p
            eff_rel_scores[p] = eff_f
            rel_func_pts[p] = eff_f * 50.0

        kk_points = 0.0
        dusthana_raw = 0.0
        m_dust: List[str] = []
        b_rel = [p for p in CLASSICAL_PLANETS if eff_rel_scores[p] > 0]
        active_planets_count = 0

        for p in CLASSICAL_PLANETS:
            p_house = planet_houses.get(p)
            if p_house is None:
                continue
            r_ph = ((p_house - h) % 12) + 1
            raw_f = raw_rel_scores[p]
            f_rel = eff_rel_scores[p]

            if planets_eval and p in planets_eval and "dignity" in planets_eval[p]:
                d_p = float(planets_eval[p]["dignity"].get("unit_score", 0.0))
            else:
                dignity_status = _get_dignity_status(d1_grahas[p])
                d_p = DICARA_D1_DIGNITY_MAP.get(dignity_status, 0.0)

            # Single dignity scaling
            if raw_f != 0.0:
                scaled_pts = scale_by_dignity(abs(raw_f) * 50.0, d_p, raw_f)
                signed_pts = scaled_pts if raw_f > 0 else -scaled_pts
            else:
                signed_pts = scale_by_dignity(50.0, d_p, 0.0)

            # SPECIAL HANDLING FOR HOUSE LORD (Phaladīpikā 15.2, 15.3, 15.5)
            if p == lord:
                if r_ph in [1, 2, 4, 5, 7, 9, 10]:
                    # Strongly nourishes foundation (weight 1.0 + degree proximity to major aspect angles)
                    p_lon = float(d1_grahas[lord].get("longitude", 0.0)) if lord in d1_grahas else 0.0
                    ang_dist = _shortest_distance(p_lon, cusp_lon)
                    min_delta = min(abs(ang_dist - a) for a in [0.0, 90.0, 120.0, 180.0])
                    aspect_bonus = (1.0 - min_delta / 10.0) * 15.0 if min_delta < 10.0 else 0.0
                    active_planets_count += 1
                    kk_points += (signed_pts + aspect_bonus)
                elif r_ph in [3, 11]:
                    # Upacaya growth placement (weight 0.50)
                    active_planets_count += 1
                    kk_points += signed_pts * 0.50
                elif r_ph in [6, 8, 12]:
                    # Lord in relative Dusthāna (Bhāva-nāśa ruin per Phaladīpikā 15.3 & 15.5)
                    active_planets_count += 1
                    p_sign = d1_grahas[lord].get("sign")
                    valid_own = [DICARA_MOOLATRIKONA_SIGNS[lord]]
                    if DICARA_DOMICILE_SIGNS[lord]:
                        valid_own.append(DICARA_DOMICILE_SIGNS[lord])
                    # If Lord occupies its other own sign, penalty is waived per 15.29
                    if p_sign in valid_own and p_sign != h_data["sign"]:
                        bhava_nasa_penalty = 0.0
                    else:
                        base_pen = -110.0 if r_ph == 8 else (-80.0 if r_ph == 12 else -70.0)
                        comb_loss = 0.0
                        if planets_eval and lord in planets_eval:
                            comb_loss = float(planets_eval[lord].get("combustion", {}).get("loss_ratio", 0.0))
                        if d_p >= 0.4 and comb_loss == 0.0:
                            bhava_nasa_penalty = base_pen * 0.50
                        elif d_p < 0.0 or comb_loss > 0.0:
                            bhava_nasa_penalty = base_pen * (1.0 + 0.50 * abs(min(0.0, d_p)) + 0.40 * comb_loss)
                        else:
                            bhava_nasa_penalty = base_pen

                    dusthana_raw += bhava_nasa_penalty
                    if bhava_nasa_penalty < 0.0:
                        m_dust.append(lord)
                continue

            # NON-LORD PLANETS
            if r_ph in [2, 4, 5, 7, 9, 10] and f_rel != 0:
                active_planets_count += 1
                kk_points += signed_pts
            elif r_ph in [3, 11] and f_rel != 0:
                active_planets_count += 1
                w_upacaya = 0.40 if r_ph == 3 else 0.50
                kk_points += signed_pts * w_upacaya
            elif r_ph == 1:
                if f_rel > 0:
                    active_planets_count += 1
                    kk_points += signed_pts * 0.50
                elif f_rel < 0 and p != asc_first_lord:
                    # Relative Dusthāna / Triṣaḍāya lords occupying House H (Phaladīpikā 15.5 & 15.8)
                    active_planets_count += 1
                    kk_points += signed_pts * 0.75
            elif r_ph in [6, 8, 12]:
                if f_rel < 0:
                    active_planets_count += 1
                    m_dust.append(p)
                    dusthana_raw += signed_pts

        # Benefic Aspect & Co-Occupancy Mitigation on Dusthāna Malefics (Phaladīpikā 15.3–15.4)
        if m_dust and b_rel:
            mit_ratios: List[float] = []
            for m in m_dust:
                aspects_sum = sum(p2p[b][m] for b in b_rel if b != m)
                mit_m = aspects_sum / len(b_rel)
                mit_ratios.append(mit_m / 100.0)
            avg_mit = sum(mit_ratios) / len(m_dust)
            avg_mit = max(0.0, min(0.85, avg_mit))
        else:
            avg_mit = 0.0

        dusthana_mitigated = dusthana_raw * (1.0 - avg_mit)
        denom = max(3.0, float(active_planets_count))
        final_rel_score = (kk_points + dusthana_mitigated) / denom if active_planets_count > 0 else 0.0

        results[h] = {
            "score": round(final_rel_score, 2),
            "kk_group_points": round(kk_points, 2),
            "dusthana_raw_points": round(dusthana_raw, 2),
            "benefic_mitigation_pct": round(avg_mit * 100.0, 2),
            "dusthana_mitigated_points": round(dusthana_mitigated, 2),
            "active_planets_count": active_planets_count,
            "relative_functional_natures": {p: round(rel_func_pts[p], 2) for p in CLASSICAL_PLANETS}
        }

    return results


def evaluate_house_karakas_hol(
    geometry: Dict[str, Any],
    d1_grahas: Dict[str, Any],
    planets_eval: Dict[str, Any],
    basic_houses: Dict[int, Any],
    sign_baselines: Optional[Dict[int, float]] = None
) -> Dict[int, Dict[str, Any]]:
    """
    Implements Phase 7B: Bhāva Kāraka & Kāraka Lagna Engine (Phaladīpikā 15.5-6, 15.15-20, 15.25).
    Evaluates:
      1. Direct condition of natural representative (k_planet_score).
      2. Kāraka Lagna: Hth house counted from Kāraka's sign (k_lagna_house_score).
      3. Relative placement & proximity between Kāraka and House H (k_rel_bonus, Phaladīpikā 15.25).
    """
    asc_sign = geometry.get("ascendant_sign") or geometry.get("houses", {}).get(1, {}).get("sign", "Aries")
    asc_sign_idx = ZODIAC_SIGNS.index(asc_sign)

    karaka_houses: Dict[int, Dict[str, Any]] = {}

    for h in range(1, 13):
        karakas = DICARA_HOUSE_KARAKAS.get(h, ["Jupiter"])
        k_scores: List[float] = []
        k_planet_scores: Dict[str, float] = {}
        k_lagna_houses: Dict[str, int] = {}
        k_lagna_scores: Dict[str, float] = {}
        k_rel_houses: Dict[str, int] = {}
        k_proximities: Dict[str, str] = {}

        for k in karakas:
            p_eval = planets_eval.get(k, {})
            k_p_score = float(p_eval.get("final_assessment_score", 0.0))
            k_planet_scores[k] = round(k_p_score, 2)

            k_house = int(p_eval.get("house", 1))
            r_kh = ((k_house - h) % 12) + 1
            k_rel_houses[k] = r_kh
            if r_kh in [1, 2, 4, 5, 7, 9, 10, 11]:
                k_rel_bonus = 15.0
                k_proximities[k] = "Close / Nourishing"
            elif r_kh in [6, 8, 12]:
                k_rel_bonus = -15.0
                k_proximities[k] = "Distant / Dusthāna"
            else:  # r_kh == 3
                k_rel_bonus = 5.0
                k_proximities[k] = "Moderate / Upacaya"

            # Kāraka Lagna target house
            k_sign = d1_grahas.get(k, {}).get("sign", asc_sign)
            k_sign_idx = ZODIAC_SIGNS.index(k_sign)
            target_sign_idx = (k_sign_idx + h - 1) % 12
            h_natal = ((target_sign_idx - asc_sign_idx) % 12) + 1
            k_lagna_houses[k] = h_natal
            if sign_baselines and h_natal in sign_baselines:
                k_l_score = float(sign_baselines[h_natal])
            else:
                k_l_score = float(basic_houses.get(h_natal, {}).get("score", 0.0))
            k_lagna_scores[k] = round(k_l_score, 2)

            score_k = 0.55 * k_p_score + 0.30 * k_l_score + 0.15 * k_rel_bonus
            k_scores.append(score_k)

        avg_k_score = sum(k_scores) / len(k_scores) if k_scores else 0.0
        avg_lagna_score = sum(k_lagna_scores.values()) / len(k_lagna_scores) if k_lagna_scores else 0.0

        karaka_houses[h] = {
            "score": round(avg_k_score, 2),
            "karakas": karakas,
            "karaka_planet_scores": k_planet_scores,
            "karaka_lagna_house": k_lagna_houses,
            "karaka_lagna_score": round(avg_lagna_score, 2),
            "karaka_relative_houses": k_rel_houses,
            "karaka_proximity": k_proximities,
        }

    return karaka_houses


def evaluate_house_walls_kartari(
    geometry: Dict[str, Any],
    d1_grahas: Dict[str, Any],
    func_natures: Dict[str, Any],
    planets_eval: Optional[Dict[str, Any]] = None
) -> Dict[int, Dict[str, Any]]:
    """
    Implements Phase 8: Quantified House Walls — Kartarī Yoga.
    Evaluates physical planets within (0, 30 deg) before and after each house cusp.
    """
    results: Dict[int, Dict[str, Any]] = {}

    for h, h_data in geometry["houses"].items():
        cusp_lon = h_data["cusp_longitude"]
        lord = h_data["lord"]

        candidates_before: List[Tuple[str, float]] = []
        candidates_after: List[Tuple[str, float]] = []

        for p in CLASSICAL_PLANETS:
            p_lon = float(d1_grahas[p]["longitude"])
            delta_before = (cusp_lon - p_lon) % 360.0
            delta_after = (p_lon - cusp_lon) % 360.0

            if 0.0 < delta_before < 30.0:
                candidates_before.append((p, delta_before))
            if 0.0 < delta_after < 30.0:
                candidates_after.append((p, delta_after))

        if candidates_before and candidates_after:
            p_before, dist_before = min(candidates_before, key=lambda x: x[1])
            p_after, dist_after = min(candidates_after, key=lambda x: x[1])

            p_before_sign = d1_grahas[p_before].get("sign") or ZODIAC_SIGNS[int(float(d1_grahas[p_before]["longitude"]) // 30) % 12]
            p_after_sign = d1_grahas[p_after].get("sign") or ZODIAC_SIGNS[int(float(d1_grahas[p_after]["longitude"]) // 30) % 12]
            h_sign = h_data.get("sign") or ZODIAC_SIGNS[int(float(h_data.get("cusp_longitude", 0.0)) // 30) % 12]
            h_sign_idx = ZODIAC_SIGNS.index(h_sign)
            prev_sign = ZODIAC_SIGNS[(h_sign_idx - 1) % 12]
            next_sign = ZODIAC_SIGNS[(h_sign_idx + 1) % 12]

            # True Kartari check (Phaladīpikā 15.6 & DiCara Ep. 4):
            # Flanking planets within 30° before and after the cusp must sit in
            # (prev_sign or h_sign) before the cusp and (h_sign or next_sign) after the cusp,
            # and cannot both sit exclusively in prev_sign or exclusively in next_sign.
            is_valid_kartari = (
                p_before_sign in (prev_sign, h_sign)
                and p_after_sign in (h_sign, next_sign)
            )

            if is_valid_kartari:
                def planet_quality(p_name: str) -> float:
                    if planets_eval and p_name in planets_eval and "dignity" in planets_eval[p_name]:
                        d_p = float(planets_eval[p_name]["dignity"].get("unit_score", 0.0))
                    else:
                        dignity_status = _get_dignity_status(d1_grahas[p_name])
                        d_p = DICARA_D1_DIGNITY_MAP.get(dignity_status, 0.0)
                    f_p = func_natures[p_name]["score"]

                    if p_name == lord:
                        base = 200.0
                        f_eval = 2
                    elif f_p == 0:
                        base = d_p * 100.0
                        f_eval = 1 if base > 0 else (-1 if base < 0 else 0)
                    else:
                        base = f_p * 100.0
                        f_eval = f_p

                    scaled = scale_by_dignity(abs(base), d_p, f_eval)
                    sgn = 1.0 if base > 0 else (-1.0 if base < 0 else 0.0)
                    return scaled * sgn

                q_before = planet_quality(p_before)
                q_after = planet_quality(p_after)

                occ_set = set(h_data.get("occupants", []))
                mult_before = 0.5 if p_before in occ_set else 1.0
                mult_after = 0.5 if p_after in occ_set else 1.0

                raw_score = (
                    q_before * mult_before * (1.0 - dist_before / 30.0)
                    + q_after * mult_after * (1.0 - dist_after / 30.0)
                )
                score = 120.0 * math.tanh(raw_score / 180.0)

                if q_before > 0 and q_after > 0:
                    wall_type = "Shubha Kartari"
                elif q_before < 0 and q_after < 0:
                    wall_type = "Papa Kartari"
                else:
                    wall_type = "Mishra Kartari"

                results[h] = {
                    "is_walled": True,
                    "wall_type": wall_type,
                    "score": round(score, 2),
                    "planet_before": p_before,
                    "planet_after": p_after
                }
            else:
                results[h] = {
                    "is_walled": False,
                    "wall_type": "None",
                    "score": 0.0,
                    "planet_before": None,
                    "planet_after": None
                }
        else:
            results[h] = {
                "is_walled": False,
                "wall_type": "None",
                "score": 0.0,
                "planet_before": None,
                "planet_after": None
            }

    return results


def _trace_dispositor_chains(
    geometry: Dict[str, Any],
    d1_grahas: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Traces the dispositor chain for each planet and house by stepping from
    planet -> sign lord until a planet is encountered for the SECOND time.
    That second-hit planet is the unique Final Dispositor for that starting point.
    """
    has_valid_classical = (
        all(p in d1_grahas for p in CLASSICAL_PLANETS)
        and all(d1_grahas[p].get("sign") in SIGN_LORDS for p in CLASSICAL_PLANETS)
    )

    if not has_valid_classical:
        planet_chains: Dict[str, Dict[str, Any]] = {}
        for p in CLASSICAL_PLANETS:
            ruled = []
            if p in d1_grahas:
                ruled = [int(rh) for rh in d1_grahas[p].get("ruled_houses", []) if 1 <= int(rh) <= 12]
            planet_chains[p] = {
                "start_planet": p,
                "chain_planets": [p, p],
                "traversed_houses": [1],
                "final_dispositor": p,
                "final_dispositor_houses": ruled,
                "hops_to_repeat": 1,
                "is_svakshetra": True,
                "returns_to_self": False,
            }
        house_chains: Dict[int, Dict[str, Any]] = {}
        for h, h_data in geometry.get("houses", {}).items():
            lord = h_data.get("lord", "Sun")
            p_info = planet_chains.get(lord, planet_chains["Sun"])
            h_int = int(h) if str(h).isdigit() else 1
            house_chains[h_int] = {
                "house": h_int,
                "lord": lord,
                "chain_planets": p_info["chain_planets"],
                "traversed_houses": [h_int],
                "final_dispositor": p_info["final_dispositor"],
                "final_dispositor_houses": p_info["final_dispositor_houses"],
                "hops_to_repeat": 1,
                "is_svakshetra": True,
                "returns_to_self": False,
            }
        return {
            "planets": planet_chains,
            "houses": house_chains,
            "is_mock": True,
        }

    planet_house: Dict[str, int] = {}
    sign_lord_of_planet: Dict[str, str] = {}

    for p in CLASSICAL_PLANETS:
        p_sign = d1_grahas[p]["sign"]
        sign_lord_of_planet[p] = SIGN_LORDS[p_sign]
        planet_house[p] = 1
        for h, h_data in geometry["houses"].items():
            if h_data.get("sign") == p_sign:
                planet_house[p] = int(h)
                break

    planet_chains: Dict[str, Dict[str, Any]] = {}
    for start_p in CLASSICAL_PLANETS:
        counts: Dict[str, int] = {start_p: 1}
        chain_planets: List[str] = [start_p]
        traversed_houses: List[int] = [planet_house[start_p]]

        curr = start_p
        while True:
            next_lord = sign_lord_of_planet[curr]
            chain_planets.append(next_lord)
            counts[next_lord] = counts.get(next_lord, 0) + 1

            if counts[next_lord] == 2:
                final_dispositor = next_lord
                break

            traversed_houses.append(planet_house[next_lord])
            curr = next_lord

        hops = len(chain_planets) - 1
        final_disp_houses = [
            int(rh) for rh in d1_grahas[final_dispositor].get("ruled_houses", [])
            if 1 <= int(rh) <= 12
        ]

        planet_chains[start_p] = {
            "start_planet": start_p,
            "chain_planets": chain_planets,
            "traversed_houses": traversed_houses,
            "final_dispositor": final_dispositor,
            "final_dispositor_houses": final_disp_houses,
            "hops_to_repeat": hops,
            "is_svakshetra": (hops == 1 and final_dispositor == start_p),
            "returns_to_self": (hops >= 2 and final_dispositor == start_p),
        }

    house_chains: Dict[int, Dict[str, Any]] = {}
    for h, h_data in geometry["houses"].items():
        lord = h_data["lord"]
        h_int = int(h) if str(h).isdigit() else 1
        p_info = planet_chains[lord]
        house_chains[h_int] = {
            "house": h_int,
            "lord": lord,
            "chain_planets": p_info["chain_planets"],
            "traversed_houses": [h_int] + [th for th in p_info["traversed_houses"] if th != h_int],
            "final_dispositor": p_info["final_dispositor"],
            "final_dispositor_houses": p_info["final_dispositor_houses"],
            "hops_to_repeat": p_info["hops_to_repeat"],
            "is_svakshetra": p_info["is_svakshetra"],
            "returns_to_self": p_info["returns_to_self"],
        }

    return {
        "planets": planet_chains,
        "houses": house_chains,
        "is_mock": False,
    }


def _extract_yoga_field(yoga_item: Any, field: str, default: Any = None) -> Any:
    """Safely extracts a field from either a YogaInstance object or a serialized dict."""
    if isinstance(yoga_item, dict):
        val = yoga_item.get(field, default)
    else:
        val = getattr(yoga_item, field, default)
    if hasattr(val, "value"):
        return str(val.value)
    return val


def evaluate_house_yogas_hol(
    geometry: Dict[str, Any],
    d1_grahas: Dict[str, Any],
    yogas_input: Optional[Dict[str, Any]] = None
) -> Dict[int, Dict[str, Any]]:
    """
    Implements Phase 9: Numerical House Yoga Scoring using Astra's Certified Classical Yoga Engine.
    Credits yogas strictly to occupied houses (1.00x) and participating houses (0.75x) without
    multi-hop dispositor smearing. Rescales base points and enforces smooth [-100, +100] saturation.
    Awards full positive points to Houses 6, 8, 12 for Viparīta Rāja Yogas (Phaladīpikā 6.57–70).
    """
    house_yoga_data: Dict[int, Dict[str, Any]] = {
        h: {
            "total_yoga_score": 0.0,
            "parivartana_score": 0.0,
            "raja_yoga_score": 0.0,
            "mahapurusha_score": 0.0,
            "daridra_yoga_score": 0.0,
            "active_yogas": []
        }
        for h in range(1, 13)
    }

    planet_house_map: Dict[str, int] = {}
    for p in CLASSICAL_PLANETS + ["Rahu", "Ketu"]:
        if p in d1_grahas:
            p_sign = d1_grahas[p]["sign"]
            for h, h_data in geometry["houses"].items():
                if h_data["sign"] == p_sign:
                    planet_house_map[p] = h
                    break

    raw_yogas_list: List[Any] = []
    if isinstance(yogas_input, dict):
        raw_yogas_list = yogas_input.get("yogas", [])
    elif isinstance(yogas_input, list):
        raw_yogas_list = yogas_input

    for y_item in raw_yogas_list:
        status_raw = str(_extract_yoga_field(y_item, "status", "PURE")).upper()
        if "BROKEN" in status_raw:
            continue

        y_name = str(_extract_yoga_field(y_item, "name", "Classical Yoga"))
        y_id = str(_extract_yoga_field(y_item, "id", "")).lower()
        cat_raw = str(_extract_yoga_field(y_item, "category", "")).upper()
        plausibility = float(_extract_yoga_field(y_item, "plausibility_score", 100.0) or 100.0)
        plaus_mult = max(0.25, min(1.0, plausibility / 100.0))

        planets = list(_extract_yoga_field(y_item, "participating_planets", []) or [])
        part_houses = [
            int(h) for h in (_extract_yoga_field(y_item, "participating_houses", []) or [])
            if isinstance(h, (int, float)) and 1 <= int(h) <= 12
        ]

        occ_houses = sorted({
            planet_house_map[p] for p in planets if p in planet_house_map
        })
        owned_houses = sorted({
            int(rh)
            for p in planets if p in CLASSICAL_PLANETS and p in d1_grahas
            for rh in d1_grahas[p].get("ruled_houses", [])
            if 1 <= int(rh) <= 12
        })

        norm_name = unicodedata.normalize("NFKD", y_name).encode("ASCII", "ignore").decode("utf-8").upper()
        norm_cat = unicodedata.normalize("NFKD", cat_raw).encode("ASCII", "ignore").decode("utf-8").upper()

        is_negative_yoga = (
            any(k in norm_cat for k in [
                "DARIDRYA", "DARIDRA", "ARISHTA", "DOSHA", "PAPA", "AFFLICTION", "AVAYOGA",
                "DUSTHANA", "NEGATIVE", "INAUSPICIOUS", "PENALTY", "MALEFIC"
            ])
            or any(k in norm_name for k in [
                "DARIDRYA", "DARIDRA", "DAINYA", "KEMADRUMA", "SHAKATA", "GRAHANA",
                "CHANDALA", "CANDALA", "KALA SARPA", "KALASARPA", "VISH ", "VISHA",
                "ANGARAKA", "PAPA", "ARISHTA", "DUR YOGA", "DURYOGA", "KUJA DOSHA",
                "NIHSVA", "DUSKRITI", "DUSKRTI", "MRTI", "MRITI", "SATRU", "SHATRU", "ADHAMA",
                "ASHUBHA", "ASUBHA", "DEPLETED", "DISGRACED", "BROKEN INITIATIVES",
                "FRICTION", "DISSIPATION", "STAGNATION", "POVERTY", " LOSS", "AFFLICT",
                "PAPAKARTARI", "PAPA KARTARI", "BANDHANA", "APAKIRTI"
            ])
            or any(k in y_id for k in [
                "daridrya", "daridra", "dainya", "kemadruma", "shakata", "grahana", "arishta",
                "nihsva", "duskriti", "mrti", "mriti", "satru", "shatru", "adhama", "ashubha",
                "asubha", "duryoga", "avayoga", "papa"
            ])
        )
        is_parivartana = "PARIVARTANA" in norm_cat or "PARIVARTANA" in norm_name or "parivartana" in y_id
        is_mahapurusha = "MAHAPURUSHA" in norm_cat or "MAHAPURUSHA" in norm_name or "mahapurusha" in y_id
        is_viparita = "VIPARITA" in norm_cat or "VIPARITA" in norm_name or any(
            k in norm_name for k in ["HARSHA", "SARALA", "VIMALA"]
        )
        is_major_auspicious = any(
            k in norm_cat or k in norm_name
            for k in ["RAJA", "DHANA", "LAKSHMI", "YOGAKARAKA", "GAJAKESARI", "CHANDRA MANGALA", "ADHI", "AMALA", "BHAGYA", "JALADHI"]
        )

        # Status multiplier (Yoga Bhaṅga / Mitigation)
        if is_negative_yoga:
            if "RESCUED" in status_raw:
                status_mult = 0.25
            elif "STAINED" in status_raw:
                status_mult = 0.60
            else:
                status_mult = 1.00
        else:
            if "PURE" in status_raw:
                status_mult = 1.00
            elif "RESCUED" in status_raw:
                status_mult = 0.70
            elif "STAINED" in status_raw:
                status_mult = 0.50
            else:
                status_mult = 0.75

        # 1. Negative / Affliction Yogas (base = -60.0)
        if is_negative_yoga:
            base_pen = -60.0 * plaus_mult * status_mult
            if len(planets) >= 6:
                base_pen *= 0.35
                afflicted_targets = occ_houses
            else:
                afflicted_targets = part_houses if part_houses else (owned_houses + occ_houses)
            for h_t in set(afflicted_targets):
                pts = round(base_pen * 0.5 if h_t in [6, 8, 12] and h_t in occ_houses else base_pen, 2)
                role = "Occupied house" if h_t in occ_houses else "Afflicted house axis"
                if is_parivartana:
                    house_yoga_data[h_t]["parivartana_score"] += pts
                else:
                    house_yoga_data[h_t]["daridra_yoga_score"] += pts
                house_yoga_data[h_t]["active_yogas"].append({
                    "type": y_name,
                    "role": f"{role} ({status_raw})",
                    "planets": planets,
                    "points": pts
                })
            continue

        # 2. Auspicious Parivartana Yogas (base = 65.0)
        if is_parivartana:
            base_pts = 65.0 * plaus_mult * status_mult
            pariv_targets = part_houses if part_houses else occ_houses
            for h_t in set(pariv_targets):
                pts = round(base_pts, 2)
                house_yoga_data[h_t]["parivartana_score"] += pts
                house_yoga_data[h_t]["active_yogas"].append({
                    "type": y_name,
                    "role": f"Exchange between houses ({status_raw})",
                    "planets": planets,
                    "points": pts
                })
            continue

        # 3. Pañca Mahāpuruṣa Yogas (base = 65.0)
        if is_mahapurusha:
            base_pts = 65.0 * plaus_mult * status_mult
            for h_occ in occ_houses:
                pts = round(base_pts, 2)
                house_yoga_data[h_occ]["mahapurusha_score"] += pts
                house_yoga_data[h_occ]["active_yogas"].append({
                    "type": y_name,
                    "role": f"Occupied Kendra ({status_raw})",
                    "planets": planets,
                    "points": pts
                })
            for h_own in owned_houses:
                if h_own in occ_houses or h_own in [6, 8, 12]:
                    continue
                pts = round(base_pts * 0.75, 2)
                house_yoga_data[h_own]["mahapurusha_score"] += pts
                house_yoga_data[h_own]["active_yogas"].append({
                    "type": y_name,
                    "role": f"Owned by Mahāpuruṣa planet ({status_raw})",
                    "planets": planets,
                    "points": pts
                })
            continue

        # 4. Viparīta Rāja Yogas (base = 65.0, full points to Dusthānas 6, 8, 12 per Phaladīpikā 6.57–70)
        if is_viparita:
            base_pts = 65.0 * plaus_mult * status_mult
            vip_targets = set(part_houses) | set(occ_houses)
            for h_t in sorted(vip_targets):
                is_occ = h_t in occ_houses
                pts = round(base_pts * (1.0 if is_occ else 0.75), 2)
                role = "Occupied by participating planet" if is_occ else "Owned/activated by participating planet"
                house_yoga_data[h_t]["raja_yoga_score"] += pts
                house_yoga_data[h_t]["active_yogas"].append({
                    "type": y_name,
                    "role": f"{role} ({status_raw})",
                    "planets": planets,
                    "points": pts
                })
            continue

        # 5. Rāja, Dhana, Yogakāraka & Auspicious Classical Yogas (Direct Attribution, no multi-hop smearing)
        base_pts = (60.0 if is_major_auspicious else 30.0) * plaus_mult * status_mult
        is_nabhasa_sankhya = len(planets) >= 6
        if is_nabhasa_sankhya:
            base_pts *= 0.35
            candidate_houses = set(occ_houses)
        else:
            candidate_houses = set(occ_houses) | set(part_houses) | set(owned_houses)

        for h_t in sorted(candidate_houses):
            is_occ = h_t in occ_houses
            is_part = h_t in part_houses
            if h_t in [6, 8, 12]:
                scale = 0.25 if is_occ else 0.0
                role = "Occupied Dusthāna spillover"
            elif is_occ:
                scale = 1.00
                role = "Occupied by participating planet"
            elif is_part:
                scale = 0.75
                role = "Participating yoga house"
            else:
                scale = 0.50
                role = "Owned by participating planet"

            if scale <= 0.0:
                continue

            pts = round(base_pts * scale, 2)
            house_yoga_data[h_t]["raja_yoga_score"] += pts
            house_yoga_data[h_t]["active_yogas"].append({
                "type": y_name,
                "role": f"{role} ({status_raw})",
                "planets": planets,
                "points": pts
            })

    # Apply smooth hyperbolic tangent saturation into [-100, +100] scale
    for h in range(1, 13):
        data = house_yoga_data[h]
        raw_tot = (
            data["parivartana_score"]
            + data["raja_yoga_score"]
            + data["mahapurusha_score"]
            + data["daridra_yoga_score"]
        )
        saturated_tot = 100.0 * math.tanh(raw_tot / 120.0)
        data["total_yoga_score"] = round(saturated_tot, 2)
        data["parivartana_score"] = round(data["parivartana_score"], 2)
        data["raja_yoga_score"] = round(data["raja_yoga_score"], 2)
        data["mahapurusha_score"] = round(data["mahapurusha_score"], 2)
        data["daridra_yoga_score"] = round(data["daridra_yoga_score"], 2)

    return house_yoga_data


def evaluate_houses_of_life(chart_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main Orchestrator for Vic DiCara's "Houses of Life" Evaluation System (Phaladīpikā Ch. 15).
    Executes Phases 1 through 10, synthesizes composite scores across 6 classical components,
    and formats the complete output schema.
    """
    # Phase 1: Chart Geometry
    geometry = _extract_whole_sign_geometry(chart_dict)
    d1_grahas = chart_dict["vargas"]["D1"]["grahas"]
    adv_aspects = chart_dict.get("advanced_aspects", {})

    # Phase 2: Functional Nature relative to Lagna
    func_natures = calculate_functional_nature(geometry["ascendant_sign"], d1_grahas=d1_grahas)

    # Phase 4: Interactions & Cusp Dominance
    influences = calculate_cusp_and_planet_influences(geometry, d1_grahas, adv_aspects)

    # Phase 5: Planetary Evaluation (with D9 multi-varga dignity & Digbala)
    planets_eval = evaluate_planets_hol(geometry, d1_grahas, func_natures, influences, chart_dict=chart_dict)

    # Phase 6: Basic House Condition (with condition gating, Upacaya malefic boost, Rahu/Ketu)
    basic_houses = evaluate_basic_house_conditions(geometry, func_natures, d1_grahas, influences, planets_eval=planets_eval)

    # Phase 7: Relative Houses (Bhavāt Bhavam with Lord relative 6/8/12 Bhāva-nāśa fix)
    rel_houses = evaluate_relative_houses_bhavat_bhavam(
        geometry, d1_grahas, influences, planets_eval=planets_eval, func_natures=func_natures
    )

    # Phase 10: Dispositor Chain Tracking for House Lord Synthesis
    disp_chains = _trace_dispositor_chains(geometry, d1_grahas)

    # Evaluate House Lord and Occupants for all houses to establish sign-level baselines
    lord_evaluations: Dict[int, Dict[str, Any]] = {}
    lord_and_occ_avg_map: Dict[int, float] = {}

    for h, h_data in geometry["houses"].items():
        h_int = int(h) if str(h).isdigit() else 1
        lord = h_data["lord"]
        occupants = h_data["occupants"]

        lord_score = planets_eval[lord]["final_assessment_score"]
        occ_scores = {occ: planets_eval[occ]["final_assessment_score"] for occ in occupants}

        # Resolve House Lord through Immediate Dispositor, Final Dispositor, and Lord Digbala
        h_chain = disp_chains["houses"].get(h_int, {})
        final_disp = h_chain.get("final_dispositor", lord)
        final_disp_score = planets_eval.get(final_disp, {}).get("final_assessment_score", lord_score)

        chain_planets = h_chain.get("chain_planets", [lord, lord])
        immediate_disp = chain_planets[1] if len(chain_planets) > 1 else lord
        immediate_disp_score = planets_eval.get(immediate_disp, {}).get("final_assessment_score", lord_score)

        loop_houses = disp_chains["planets"].get(lord, {}).get("traversed_houses", [])
        has_dusthana = any(th in [6, 8, 12] for th in loop_houses)
        has_non_dusthana = any(th not in [6, 8, 12] for th in loop_houses)
        is_dainya_exchange = (has_dusthana and has_non_dusthana)

        if h_chain.get("is_svakshetra", False) or lord in occupants:
            effective_lord_score = lord_score + 15.0
        elif h_chain.get("returns_to_self", False) and h_chain.get("hops_to_repeat", 0) == 2:
            partner = immediate_disp
            partner_score = immediate_disp_score
            if is_dainya_exchange:
                # Dainya Parivartana between good house and Dusthāna
                effective_lord_score = (0.80 * lord_score + 0.20 * partner_score) - 10.0
            else:
                # Mahā Parivartana or Viparīta loop
                effective_lord_score = (0.80 * lord_score + 0.20 * partner_score) + 15.0
        else:
            effective_lord_score = 0.65 * lord_score + 0.20 * immediate_disp_score + 0.15 * final_disp_score

        # Add House Lord's extra Digbala bonus (Phaladīpikā Ch. 4)
        lord_house = int(planets_eval[lord]["house"])
        _, lord_digbala_pts = _get_bala_and_digbala_bonus(lord, lord_house, chart_dict)
        effective_lord_score += 0.15 * lord_digbala_pts

        # Direct Lord-in-Dusthāna Structural Penalty (Phaladīpikā 15.18 & 6.57)
        lord_d1_status = _get_dignity_status(d1_grahas[lord])
        lord_d1 = DICARA_D1_DIGNITY_MAP.get(lord_d1_status, 0.0)
        r_lord = ((lord_house - h_int) % 12) + 1
        is_own_exalt = (lord_d1 >= 0.8)
        if not is_own_exalt:
            lord_ruled = [int(rh) for rh in d1_grahas[lord].get("ruled_houses", []) if 1 <= int(rh) <= 12]
            is_viparita_waived = any(rh in [6, 8, 12] for rh in lord_ruled) and (lord_d1 >= 0.4) and (lord_house in [6, 8, 12])
            if not is_viparita_waived:
                dust_pen = 0.0
                if r_lord in [6, 8, 12]:
                    dust_pen = -12.0 if r_lord == 8 else -8.0
                elif lord_house in [6, 8, 12] and r_lord not in [1, 2, 3, 4, 5, 7, 9, 10, 11]:
                    dust_pen = -8.0

                if lord_d1 < 0.0 and lord_score >= 0.0:
                    dust_pen *= 2.0
                effective_lord_score += dust_pen

        # Sign-Correct Occupant Synthesis
        non_lord_contribs: List[float] = []
        for occ in occupants:
            if occ == lord:
                continue
            occ_final_score = planets_eval[occ]["final_assessment_score"]
            is_first_lord = func_natures.get(occ, {}).get("rule_breakdown", {}).get("is_first_lord", False)
            fn_sc = func_natures.get(occ, {}).get("score", 0.0)

            # Check if Moon is bright waxing/full and not eclipsed
            is_bright_moon = False
            if occ == "Moon":
                m_inh = float(func_natures.get("Moon", {}).get("rule_breakdown", {}).get("inherent_score", 0.5))
                m_lon = float(d1_grahas["Moon"].get("longitude", 0.0))
                m_sign = d1_grahas["Moon"].get("sign")
                is_eclipsed_moon = False
                for node in ["Rahu", "Ketu"]:
                    if node in d1_grahas and d1_grahas[node].get("sign") == m_sign:
                        n_lon = float(d1_grahas[node].get("longitude", 0.0))
                        if _shortest_distance(m_lon, n_lon) <= 10.0:
                            is_eclipsed_moon = True
                            break
                if m_inh >= 0.5 and not is_eclipsed_moon:
                    is_bright_moon = True

            if is_first_lord and h_int not in [6, 8, 12]:
                polarity = 1.0
            elif h_int in [3, 6, 11] and occ in ["Sun", "Mars", "Saturn"]:
                polarity = 0.50
            elif is_bright_moon and occ_final_score > 0:
                polarity = 0.75
            elif fn_sc > 0.15:
                polarity = 1.0
            elif fn_sc <= -0.50 or (occ in ["Mars", "Saturn", "Sun"] and h_int not in [3, 6, 11] and not is_first_lord):
                polarity = -1.0
            else:
                polarity = 0.0

            if polarity > 0:
                occ_contrib = occ_final_score * polarity
            elif polarity < 0:
                # Baseline malefic occupant pressure (-45.0), softened up to 50% if dignified (occ_final_score > 0)
                # and intensified up to 2x (-90.0) if afflicted/debilitated (occ_final_score < 0) per Phaladīpikā 15.1 & 15.18
                if occ_final_score >= 0.0:
                    occ_contrib = -45.0 * (1.0 - 0.50 * min(1.0, occ_final_score / 100.0))
                else:
                    occ_contrib = -45.0 * (1.0 + min(1.0, abs(occ_final_score) / 100.0))
            else:
                occ_contrib = occ_final_score * 0.25

            non_lord_contribs.append(occ_contrib)

        if non_lord_contribs:
            occ_mean = sum(non_lord_contribs) / len(non_lord_contribs)
            lord_and_occ_avg = 0.70 * effective_lord_score + 0.30 * occ_mean
        else:
            lord_and_occ_avg = effective_lord_score

        lord_and_occ_avg_map[h_int] = lord_and_occ_avg
        lord_evaluations[h_int] = {
            "lord": lord,
            "lord_final_score": lord_score,
            "immediate_dispositor": immediate_disp,
            "final_dispositor": final_disp,
            "effective_lord_score": round(effective_lord_score, 2),
            "occupants_scores": occ_scores,
            "occupants_final_scores": occ_scores,
            "combined_score": round(lord_and_occ_avg, 2)
        }

    # Pre-compute sign-level baselines (Phaladīpikā Ch. 15 / DiCara System)
    sign_baselines: Dict[int, float] = {}
    for h in range(1, 13):
        sign_baselines[h] = round(
            0.50 * basic_houses[h]["score"]
            + 0.30 * lord_and_occ_avg_map[h]
            + 0.20 * rel_houses[h]["score"],
            2
        )

    # Phase 7B: House Karakas (Phaladīpikā Ch. 15)
    karaka_houses = evaluate_house_karakas_hol(
        geometry, d1_grahas, planets_eval, basic_houses, sign_baselines=sign_baselines
    )

    # Phase 7C: Chandra Lagna (Lunar Reference Frame) Assessment
    h_moon = int(planets_eval.get("Moon", {}).get("house", 1))
    chandra_houses: Dict[int, Dict[str, Any]] = {}
    for h in range(1, 13):
        h_chandra = ((h_moon - 1 + h - 1) % 12) + 1
        ch_score_val = sign_baselines.get(h_chandra, basic_houses[h_chandra]["score"])
        chandra_houses[h] = {
            "moon_house": h_moon,
            "moon_occupied_house": h_moon,
            "chandra_house_number": h_chandra,
            "chandra_house_num": h_chandra,
            "score": round(ch_score_val, 2),
            "chandra_house_score": round(ch_score_val, 2)
        }

    # Phase 8: House Walls (Kartari)
    wall_houses = evaluate_house_walls_kartari(geometry, d1_grahas, func_natures, planets_eval=planets_eval)

    # Phase 9: House Yogas (Direct Attribution, Rescaled Base Points)
    yoga_houses = evaluate_house_yogas_hol(geometry, d1_grahas, chart_dict.get("yogas", {}))

    # House Synthesis
    final_houses: Dict[str, Any] = {}

    for h, h_data in geometry["houses"].items():
        h_int = int(h) if str(h).isdigit() else 1
        lord = h_data["lord"]
        occupants = h_data["occupants"]

        b_score = basic_houses[h]["score"]
        l_eval = lord_evaluations[h_int]
        lord_score = l_eval["lord_final_score"]
        lord_and_occ_avg = lord_and_occ_avg_map[h_int]

        r_score = rel_houses[h]["score"]
        ch_score = chandra_houses[h]["score"]
        r_score_combined = round(0.80 * r_score + 0.20 * ch_score, 2)
        chandra_houses[h]["combined_relative_score"] = r_score_combined
        k_score = karaka_houses[h]["score"]
        w_score = wall_houses[h]["score"]
        is_walled = wall_houses[h]["is_walled"]
        y_score = yoga_houses[h]["total_yoga_score"]

        # Weighted Composite Hierarchy:
        # 30% Basic, 30% Lord, 15% Relative (blended with Chandra Lagna), 10% Karaka, 10% Yoga, 5% Wall
        if is_walled:
            composite = (
                0.30 * b_score
                + 0.30 * lord_and_occ_avg
                + 0.15 * r_score_combined
                + 0.10 * k_score
                + 0.10 * y_score
                + 0.05 * w_score
            )
        else:
            composite = (
                0.30 * b_score
                + 0.30 * lord_and_occ_avg
                + 0.15 * r_score_combined
                + 0.10 * k_score
                + 0.10 * y_score
            ) / 0.95

        composite_round = round(composite, 2)

        # Health Rating & Classical Tier per Section C thresholds
        if composite_round >= 100.0:
            health_rating = "Exceptional / Off the Chart"
            classical_tier = "Puṣṭa"
        elif composite_round >= 25.0:
            health_rating = "Flourishing / Fortified"
            classical_tier = "Puṣṭa"
        elif composite_round >= -20.0:
            health_rating = "Mixed / Resilient"
            classical_tier = "Miśra"
        elif composite_round >= -100.0:
            health_rating = "Strained / Challenged"
            classical_tier = "Hīna"
        else:
            health_rating = "Severely Afflicted / Obstructed"
            classical_tier = "Hīna"

        # Dominant drivers extraction
        drivers: List[str] = []
        if abs(lord_score) >= 50.0:
            adj = "fortified" if lord_score > 0 else "strained"
            drivers.append(f"House Lord {lord} is {adj} ({lord_score:+.1f})")

        cusp_contribs = basic_houses[h]["planet_contributions"]
        if cusp_contribs:
            extreme_p = max(cusp_contribs.keys(), key=lambda k: abs(cusp_contribs[k]))
            extreme_val = cusp_contribs[extreme_p]
            if abs(extreme_val) >= 40.0:
                verb = "aspectual support from" if extreme_val > 0 else "aspectual pressure from"
                drivers.append(f"Significant {verb} {extreme_p} on Cusp ({extreme_val:+.1f})")

        if abs(y_score) >= 50.0:
            active_yogas = yoga_houses[h]["active_yogas"]
            if active_yogas:
                drivers.append(f"Net Structural Yogas ({y_score:+.1f})")

        if wall_houses[h]["is_walled"]:
            drivers.append(f"{wall_houses[h]['wall_type']} ({w_score:+.1f})")

        if not drivers:
            drivers.append("Balanced, moderate planetary configurations")

        final_houses[str(h)] = {
            "house": h,
            "sign": h_data["sign"],
            "lord": lord,
            "cusp_degree": h_data["cusp_degree"],
            "cusp_longitude": h_data["cusp_longitude"],
            "occupants": occupants,
            "components": {
                "basic_house_condition": basic_houses[h],
                "lord_assessment": l_eval,
                "relative_house_bhavat_bhavam": rel_houses[h],
                "relative_houses_combined_score": r_score_combined,
                "karaka_assessment": karaka_houses[h],
                "chandra_lagna_assessment": chandra_houses[h],
                "house_walls_kartari": wall_houses[h],
                "house_yogas": yoga_houses[h]
            },
            "synthesis": {
                "composite_score": composite_round,
                "health_rating": health_rating,
                "classical_tier": classical_tier,
                "dominant_drivers": drivers
            }
        }

    # Summary Rankings
    sorted_houses = sorted(
        range(1, 13),
        key=lambda h: final_houses[str(h)]["synthesis"]["composite_score"],
        reverse=True
    )
    sorted_planets = sorted(
        CLASSICAL_PLANETS,
        key=lambda p: planets_eval[p]["final_assessment_score"],
        reverse=True
    )

    comp_mean = round(sum(final_houses[str(h)]["synthesis"]["composite_score"] for h in range(1, 13)) / 12.0, 2)

    summary_rankings = {
        "houses_by_composite_score": sorted_houses,
        "house_dna_code": "-".join(str(h) for h in sorted_houses),
        "planets_by_final_score": sorted_planets,
        "top_flourishing_houses": sorted_houses[:3],
        "most_challenged_houses": sorted_houses[-3:],
        "composite_mean_score": comp_mean
    }

    return {
        "metadata": {
            "report_type": "Houses of Life (Vic DiCara / Phaladeepika System)",
            "house_system": "Whole Sign (Ascendant Degree Sensitive Cusps)",
            "ascendant_sign": geometry["ascendant_sign"],
            "ascendant_degree": geometry["ascendant_degree"],
            "varga_evaluated": "D1"
        },
        "planets": planets_eval,
        "houses": final_houses,
        "summary_rankings": summary_rankings
    }
