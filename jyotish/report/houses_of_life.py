"""
jyotish/report/houses_of_life.py

Stage 4 Report Engine: Vic DiCara's "Houses of Life" Quantitative House & Planetary
Evaluation System (based on Phaladīpikā Chapter 15).

Consumes the read-only serialized chart_dict from ChartPipeline.to_dict() without
modifying any Frozen Core Calculus modules (Stages 1-3).
"""

from typing import Dict, Any, List, Tuple, Optional
import jyotish.aspects.aspects as aspects
from jyotish.baseline import (
    ZODIAC_SIGNS,
    SIGN_LORDS,
    COMBUSTION_ORBS,
    COMBUSTION_ORBS_RETROGRADE,
)

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

# Natural temperament for Rule 4
NATURAL_TEMPERAMENT: Dict[str, int] = {
    "Jupiter": 1,
    "Venus": 1,
    "Mars": -1,
    "Saturn": -1,
    "Sun": 0,
    "Moon": 0,
    "Mercury": 0,
}


def _shortest_distance(lon1: float, lon2: float) -> float:
    """Calculates the minimal angular distance between two longitudes on a 360-degree circle."""
    diff = abs(lon1 - lon2) % 360.0
    return 360.0 - diff if diff > 180.0 else diff


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


def calculate_functional_nature(reference_sign: str) -> Dict[str, Dict[str, Any]]:
    """
    Implements Phase 2: Planetary Functional Nature Quantification (F_P).
    Derived verbatim from Phaladeepika Chapter 15 Rules 1-4 for any reference_sign.
    """
    ref_idx = ZODIAC_SIGNS.index(reference_sign)

    def house_of_sign(sign_name: str) -> int:
        idx = ZODIAC_SIGNS.index(sign_name)
        return ((idx - ref_idx) % 12) + 1

    results: Dict[str, Dict[str, Any]] = {}

    for p in CLASSICAL_PLANETS:
        mt_sign = DICARA_MOOLATRIKONA_SIGNS[p]
        dom_sign = DICARA_DOMICILE_SIGNS[p]

        # Rule 1: 1st House Lord check
        # For Sun: owns Leo
        # For Moon: owns Cancer (Taurus is its MT root, but Cancer is its owned domicile)
        # For dual rulers: owns MT and Dom
        rules_h1 = False
        if p == "Sun" and house_of_sign("Leo") == 1:
            rules_h1 = True
        elif p == "Moon" and house_of_sign("Cancer") == 1:
            rules_h1 = True
        elif p not in ["Sun", "Moon"]:
            if house_of_sign(mt_sign) == 1 or (dom_sign and house_of_sign(dom_sign) == 1):
                rules_h1 = True

        if rules_h1:
            results[p] = {
                "score": 3,
                "classification": "Benefic",
                "rule_breakdown": {
                    "is_first_lord": True,
                    "trine_score": 0,
                    "dusthana_score": 0,
                    "inherent_score": 0
                }
            }
            continue

        # Rule 2 & 3: Trines (5, 9) and Dusthanas (6, 8, 12)
        trine_score = 0
        dusthana_score = 0

        h_mt = house_of_sign(mt_sign)
        h_dom = house_of_sign(dom_sign) if dom_sign else None

        # Special Edge Case for Moon: Sagittarius Lagna (Taurus = H6, Cancer = H8)
        # Evaluated as OR condition -> -2 instead of -3
        if p == "Moon" and h_mt in [6, 8, 12] and h_dom in [6, 8, 12]:
            dusthana_score = -2
        else:
            # Evaluate MT sign
            if h_mt in [5, 9]:
                trine_score += 2
            elif h_mt in [6, 8, 12]:
                dusthana_score -= 2

            # Evaluate Domicile sign
            if h_dom:
                if h_dom in [5, 9]:
                    trine_score += 1
                elif h_dom in [6, 8, 12]:
                    dusthana_score -= 1

        # Rule 4: Inherent temperament
        inherent_score = NATURAL_TEMPERAMENT.get(p, 0)

        net_f = trine_score + dusthana_score + inherent_score
        classification = "Benefic" if net_f > 0 else ("Malefic" if net_f < 0 else "Neutral")

        results[p] = {
            "score": net_f,
            "classification": classification,
            "rule_breakdown": {
                "is_first_lord": False,
                "trine_score": trine_score,
                "dusthana_score": dusthana_score,
                "inherent_score": inherent_score
            }
        }

    return results


def scale_by_dignity(base_val: float, dignity_unit: float, functional_score: float) -> float:
    """
    Universal Dignity-Scaling Law (Phase 3).
    Scales a non-negative base magnitude by the planet's dignity d_P in [-1.0, +1.0]
    according to functional score F.
    """
    b = abs(base_val)
    d = max(-1.0, min(1.0, float(dignity_unit)))

    if functional_score > 0:
        if d >= 0:
            return b * (1.0 + d)
        else:
            return b * (1.0 - abs(d) / 2.0)
    elif functional_score < 0:
        if d <= 0:
            return b * (1.0 + abs(d))
        else:
            return b * (1.0 - d / 2.0)
    else:  # functional_score == 0
        sgn = 1.0 if d > 0 else (-1.0 if d < 0 else 0.0)
        return b * (1.0 + abs(d)) * sgn


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

            # Aspect Virupas
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

            planet_to_planet[sender][receiver] = max(aspect_pct, conj_pct)

    # 2. Planet to House Cusp interactions with Multi-Planet Cusp Dominance
    raw_conjunctions: Dict[str, Dict[int, float]] = {p: {} for p in CLASSICAL_PLANETS}
    adjusted_conjunctions: Dict[str, Dict[int, float]] = {p: {} for p in CLASSICAL_PLANETS}
    planet_to_cusp: Dict[str, Dict[int, float]] = {p: {} for p in CLASSICAL_PLANETS}

    houses_dict = geometry["houses"]

    # Compute raw conjunctions and aspect percentages to each house cusp
    for h, h_data in houses_dict.items():
        cusp_lon = h_data["cusp_longitude"]
        h_sign = h_data["sign"]
        occupants = h_data["occupants"]

        # Raw conjunction for occupants in this sign
        occ_raw: Dict[str, float] = {}
        for p in occupants:
            p_lon = float(d1_grahas[p]["longitude"])
            dist = _shortest_distance(p_lon, cusp_lon)
            raw_c = max(0.0, (1.0 - dist / 30.0) * 100.0)
            raw_conjunctions[p][h] = raw_c
            occ_raw[p] = raw_c

        # Multi-planet cusp dominance stealing within the sign
        if len(occupants) == 1:
            p_solo = occupants[0]
            adjusted_conjunctions[p_solo][h] = occ_raw[p_solo]
        elif len(occupants) >= 2:
            # Sort occupants by raw conjunction descending (closest first)
            sorted_occ = sorted(occupants, key=lambda p: occ_raw[p], reverse=True)
            c_near = occ_raw[sorted_occ[0]]

            # Sequential pairwise stealing
            for far_p in sorted_occ[1:]:
                c_far = occ_raw[far_p]
                if (c_near + c_far) > 0:
                    steal = c_far * (c_near / (c_near + c_far))
                else:
                    steal = 0.0
                adjusted_conjunctions[far_p][h] = max(0.0, c_far - steal)
                c_near += steal

            adjusted_conjunctions[sorted_occ[0]][h] = c_near

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

        # Final planet_to_cusp impact
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
    influences: Dict[str, Any]
) -> Dict[str, Dict[str, Any]]:
    """
    Implements Phase 5: Comprehensive Planetary Assessment across 5 factors.
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

    # Second pass: compute full 5-factor planetary condition
    for p in CLASSICAL_PLANETS:
        p_data = d1_grahas[p]
        p_sign = p_data["sign"]
        p_deg_in_sign = float(p_data.get("degree_0_to_30", p_data["longitude"] % 30.0))
        p_ruled = p_data.get("ruled_houses", [])

        # Find house occupied
        p_house = 1
        for h, h_data in geometry["houses"].items():
            if h_data["sign"] == p_sign:
                p_house = h
                break

        # 1. Dignity
        dignity_status = p_data.get("dignity")
        if not dignity_status:
            dignity_status = p_data.get("dignity_breakdown", {}).get("final_dignity", "Neutral")
        d_p = DICARA_D1_DIGNITY_MAP.get(dignity_status, 0.0)
        d_pct = d_p * 100.0

        # 2. Combined Influences
        incoming_breakdown: Dict[str, float] = {}
        net_inf = 0.0
        for q in CLASSICAL_PLANETS:
            if q == p:
                continue
            i_val = p2p[q][p]
            q_status = d1_grahas[q].get("dignity")
            if not q_status:
                q_status = d1_grahas[q].get("dignity_breakdown", {}).get("final_dignity", "Neutral")
            d_q = DICARA_D1_DIGNITY_MAP.get(q_status, 0.0)
            f_q = func_natures[q]["score"]

            if f_q > 0 or (f_q == 0 and d_q > 0):
                q_sgn = 1.0
            elif f_q < 0 or (f_q == 0 and d_q < 0):
                q_sgn = -1.0
            else:
                q_sgn = 0.0

            signed_impact = q_sgn * i_val * (1.0 + abs(d_q))
            incoming_breakdown[q] = round(signed_impact, 2)
            net_inf += signed_impact

        # 3. Cusp Alignment
        raw_c = raw_conj[p].get(p_house, 0.0)
        adj_c = adj_conj[p].get(p_house, 0.0)
        capped_base = min(100.0, adj_c)

        if p_house in [1, 4, 5, 9, 10]:
            h_category = "Prominent"
            h_multiplier = 1.50
        elif p_house in [2, 7, 11]:
            h_category = "Regular"
            h_multiplier = 1.00
        else:  # [3, 6, 8, 12]
            h_category = "Hidden"
            if p_house in [6, 8, 12] and any(rh in [6, 8, 12] for rh in p_ruled):
                h_multiplier = 1.00  # Dusthana lord in Dusthana exception
            elif p_house == 3 and 3 in p_ruled:
                h_multiplier = 1.00  # 3rd lord in 3rd exception
            else:
                h_multiplier = -1.00

        alignment_score = capped_base * h_multiplier

        # 4. Bhava Sandhi (4.0 deg threshold)
        dist_border = min(p_deg_in_sign, 30.0 - p_deg_in_sign)
        if dist_border < 4.0:
            sandhi_penalty = max(0.0, 1.0 - (dist_border / 4.0))
            in_sandhi = True
        else:
            sandhi_penalty = 0.0
            in_sandhi = False
        retention_multiplier = 1.0 - sandhi_penalty

        # 5. Combustion & Solar Transfer
        if p == "Sun":
            is_combust = False
            dist_sun = 0.0
            tolerance_orb = None
            loss_ratio = 0.0
            solar_gain_ratio = round(solar_gain_sum, 4)
            combustion_multiplier = 1.0 + solar_gain_sum
        else:
            loss_ratio = combustion_losses.get(p, 0.0)
            is_combust = loss_ratio > 0.0
            dist_sun = float(p_data.get("sun_distance", _shortest_distance(float(p_data["longitude"]), sun_lon)))
            tolerance_orb = p_data.get("combustion_orb")
            solar_gain_ratio = 0.0
            combustion_multiplier = 1.0 - loss_ratio

        # Synthesis
        base_avg = (d_pct + net_inf + alignment_score) / 3.0
        final_assessment = base_avg * retention_multiplier * combustion_multiplier

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
                "house_multiplier": h_multiplier,
                "alignment_score": round(alignment_score, 2)
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
            "base_average_score": round(base_avg, 2),
            "final_assessment_score": round(final_assessment, 2)
        }

    return planet_results


def evaluate_basic_house_conditions(
    geometry: Dict[str, Any],
    func_natures: Dict[str, Any],
    d1_grahas: Dict[str, Any],
    influences: Dict[str, Any]
) -> Dict[int, Dict[str, Any]]:
    """
    Implements Phase 6: Basic House Condition — Direct Evaluation.
    House Lord receives an unconditional +2 effective functional nature override.
    """
    house_results: Dict[int, Dict[str, Any]] = {}
    p2c = influences["planet_to_cusp"]

    for h, h_data in geometry["houses"].items():
        lord = h_data["lord"]
        contributions: Dict[str, float] = {}
        total_signed = 0.0

        for p in CLASSICAL_PLANETS:
            i_val = p2c[p][h]
            p_status = d1_grahas[p].get("dignity")
            if not p_status:
                p_status = d1_grahas[p].get("dignity_breakdown", {}).get("final_dignity", "Neutral")
            d_p = DICARA_D1_DIGNITY_MAP.get(p_status, 0.0)

            # House Lord +2 Exception
            f_eff = 2 if p == lord else func_natures[p]["score"]

            scaled_i = scale_by_dignity(i_val, d_p, f_eff)

            # Note: scale_by_dignity already incorporates sgn(d_p) when f_eff == 0
            if f_eff != 0:
                signed_impact = scaled_i * f_eff
            else:
                signed_impact = scaled_i

            contributions[p] = round(signed_impact, 2)
            total_signed += signed_impact

        house_results[h] = {
            "score": round(total_signed / 7.0, 2),
            "planet_contributions": contributions
        }

    return house_results


def evaluate_relative_houses_bhavat_bhavam(
    geometry: Dict[str, Any],
    d1_grahas: Dict[str, Any],
    influences: Dict[str, Any]
) -> Dict[int, Dict[str, Any]]:
    """
    Implements Phase 7: Relative House Technique — Bhavāt Bhavam (Phaladīpikā 15.2 & 15.4).
    """
    results: Dict[int, Dict[str, Any]] = {}
    p2p = influences["planet_to_planet"]

    # Planet house placements
    planet_houses: Dict[str, int] = {}
    for p in CLASSICAL_PLANETS:
        p_sign = d1_grahas[p]["sign"]
        for h, h_data in geometry["houses"].items():
            if h_data["sign"] == p_sign:
                planet_houses[p] = h
                break

    for h, h_data in geometry["houses"].items():
        rel_func = calculate_functional_nature(h_data["sign"])
        eff_rel_scores: Dict[str, float] = {}
        rel_func_pts: Dict[str, float] = {}

        for p in CLASSICAL_PLANETS:
            p_status = d1_grahas[p].get("dignity") or d1_grahas[p].get("dignity_breakdown", {}).get("final_dignity", "Neutral")
            d_p = DICARA_D1_DIGNITY_MAP.get(p_status, 0.0)
            raw_f = float(rel_func[p]["score"])
            # If neutral (0), use dignity unit as functional nature per Episode 4 & 5
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
            f_rel = eff_rel_scores[p]
            pts = rel_func_pts[p]

            p_status = d1_grahas[p].get("dignity") or d1_grahas[p].get("dignity_breakdown", {}).get("final_dignity", "Neutral")
            d_p = DICARA_D1_DIGNITY_MAP.get(p_status, 0.0)

            # KK Group: 2, 4, 5, 7, 9, 10
            if r_ph in [2, 4, 5, 7, 9, 10] and f_rel != 0:
                active_planets_count += 1
                scaled_pts = scale_by_dignity(abs(pts), d_p, f_rel)
                if f_rel < 0:
                    kk_points -= scaled_pts
                else:
                    kk_points += scaled_pts

            # Dusthana Group: 6, 8, 12
            # Only relative malefics are active here; benefics contribute 0 and do not increment active_planets_count
            elif r_ph in [6, 8, 12] and f_rel < 0:
                active_planets_count += 1
                m_dust.append(p)
                scaled_pts = scale_by_dignity(abs(pts), d_p, f_rel)
                dusthana_raw -= scaled_pts

        # Benefic Aspect Mitigation on Dusthana Malefics
        if m_dust and b_rel:
            mit_ratios: List[float] = []
            for m in m_dust:
                aspects_sum = sum(p2p[b][m] for b in b_rel)
                mit_m = aspects_sum / len(b_rel)
                mit_ratios.append(mit_m / 100.0)
            avg_mit = sum(mit_ratios) / len(m_dust)
            avg_mit = max(0.0, min(1.0, avg_mit))
        else:
            avg_mit = 0.0

        dusthana_mitigated = dusthana_raw * (1.0 - avg_mit)

        if active_planets_count > 0:
            final_rel_score = (kk_points + dusthana_mitigated) / active_planets_count
        else:
            final_rel_score = 0.0

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


def evaluate_house_walls_kartari(
    geometry: Dict[str, Any],
    d1_grahas: Dict[str, Any],
    func_natures: Dict[str, Any]
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

            def planet_quality(p_name: str) -> float:
                p_status = d1_grahas[p_name].get("dignity")
                if not p_status:
                    p_status = d1_grahas[p_name].get("dignity_breakdown", {}).get("final_dignity", "Neutral")
                d_p = DICARA_D1_DIGNITY_MAP.get(p_status, 0.0)
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

            score = q_before * (1.0 - dist_before / 30.0) + q_after * (1.0 - dist_after / 30.0)

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

    return results


def evaluate_house_yogas_hol(
    geometry: Dict[str, Any],
    d1_grahas: Dict[str, Any]
) -> Dict[int, Dict[str, Any]]:
    """
    Implements Phase 9: Numerical House Yoga Scoring (4 Structural Yogas).
    1. Parivartana Yoga (House Exchange)
    2. Rāja Yoga (Trine + Trine, Trine + Kendra, Node Kendra/Trine)
    3. Mahāpuruṣa Yoga (and Inverse Mahāpuruṣa in Kendras)
    4. Daridra Yoga (House Lord + Dusthāna Lord, with Dusthāna Reversal)
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

    # Planet house placements and lordships
    planet_house_map: Dict[str, int] = {}
    for p in CLASSICAL_PLANETS + ["Rahu", "Ketu"]:
        if p in d1_grahas:
            p_sign = d1_grahas[p]["sign"]
            for h, h_data in geometry["houses"].items():
                if h_data["sign"] == p_sign:
                    planet_house_map[p] = h
                    break

    house_lords = {h: geometry["houses"][h]["lord"] for h in range(1, 13)}

    # 1. Parivartana Yoga
    category_map = {
        1: "Trine", 5: "Trine", 9: "Trine",
        4: "Kendra", 7: "Kendra", 10: "Kendra",
        2: "Money", 11: "Money",
        3: "Third",
        6: "Dusthana", 8: "Dusthana", 12: "Dusthana"
    }
    cat_vals = {
        "Trine": 100.0,
        "Kendra": 90.0,
        "Money": 50.0,
        "Third": 0.0,
        "Dusthana": -100.0
    }

    for x in range(1, 13):
        for y in range(x + 1, 13):
            lx = house_lords[x]
            ly = house_lords[y]
            if lx != ly:
                if planet_house_map.get(lx) == y and planet_house_map.get(ly) == x:
                    cat_x = category_map[x]
                    cat_y = category_map[y]
                    if cat_x == cat_y:
                        pts = 150.0
                    else:
                        pts = (cat_vals[cat_x] + cat_vals[cat_y]) / 2.0

                    for occupied_h in [x, y]:
                        house_yoga_data[occupied_h]["parivartana_score"] += pts
                        house_yoga_data[occupied_h]["active_yogas"].append({
                            "type": "Parivartana Yoga",
                            "role": "Exchange between houses",
                            "planets": [lx, ly],
                            "points": round(pts, 2)
                        })

    # Helper: combination check between two bodies
    def bodies_combine(b1: str, b2: str) -> bool:
        if b1 not in d1_grahas or b2 not in d1_grahas:
            return False
        # Conjunction requires occupying the same sign per Episode 6
        if d1_grahas[b1]["sign"] == d1_grahas[b2]["sign"]:
            return True
        lon1 = float(d1_grahas[b1]["longitude"])
        lon2 = float(d1_grahas[b2]["longitude"])
        # Mutual aspect >= 36.0 Virupas (60%)
        asp1 = aspects.get_graha_drishti(b1, lon1, lon2)
        asp2 = aspects.get_graha_drishti(b2, lon2, lon1)
        if asp1 >= 36.0 and asp2 >= 36.0:
            return True
        # Node aspect reception
        if b1 in ["Rahu", "Ketu"] and asp2 >= 36.0:
            return True
        if b2 in ["Rahu", "Ketu"] and asp1 >= 36.0:
            return True
        # Exchange
        if b1 in CLASSICAL_PLANETS and b2 in CLASSICAL_PLANETS:
            r1 = d1_grahas[b1].get("ruled_houses", [])
            r2 = d1_grahas[b2].get("ruled_houses", [])
            h1 = planet_house_map.get(b1)
            h2 = planet_house_map.get(b2)
            if h1 in r2 and h2 in r1:
                return True
        return False

    # 2. Rāja Yoga
    all_yoga_bodies = CLASSICAL_PLANETS + ["Rahu", "Ketu"]
    checked_raja_pairs = set()

    for i in range(len(all_yoga_bodies)):
        for j in range(i + 1, len(all_yoga_bodies)):
            b1 = all_yoga_bodies[i]
            b2 = all_yoga_bodies[j]

            if not bodies_combine(b1, b2):
                continue

            pair_key = tuple(sorted([b1, b2]))
            if pair_key in checked_raja_pairs:
                continue

            is_raja = False
            # Both physical planets
            if b1 in CLASSICAL_PLANETS and b2 in CLASSICAL_PLANETS:
                r1 = set(d1_grahas[b1].get("ruled_houses", []))
                r2 = set(d1_grahas[b2].get("ruled_houses", []))
                t1 = r1.intersection({1, 5, 9})
                k1 = r1.intersection({1, 4, 7, 10})
                t2 = r2.intersection({1, 5, 9})
                k2 = r2.intersection({1, 4, 7, 10})

                if (t1 and t2) or (t1 and k2) or (t2 and k1):
                    is_raja = True

            # Node + Planet
            elif b1 in ["Rahu", "Ketu"] or b2 in ["Rahu", "Ketu"]:
                node = b1 if b1 in ["Rahu", "Ketu"] else b2
                graha = b2 if node == b1 else b1
                node_h = planet_house_map.get(node)
                r_graha = set(d1_grahas[graha].get("ruled_houses", []))

                if node_h in [1, 4, 7, 10] and r_graha.intersection({1, 5, 9}):
                    is_raja = True
                elif node_h in [1, 5, 9] and r_graha.intersection({1, 4, 7, 10}):
                    is_raja = True

            if is_raja:
                checked_raja_pairs.add(pair_key)
                # 1. Credit hosting/occupied house(s) (+100 per hosted yoga)
                occ_houses = {planet_house_map[b] for b in [b1, b2] if b in planet_house_map}
                for h_occ in occ_houses:
                    house_yoga_data[h_occ]["raja_yoga_score"] += 100.0
                    house_yoga_data[h_occ]["active_yogas"].append({
                        "type": "Rāja Yoga",
                        "role": "Occupied by participating planet",
                        "planets": [b1, b2],
                        "points": 100.0
                    })
                # 2. Separately credit all houses owned by participating planets (+100 per yoga)
                for b in [b1, b2]:
                    if b in CLASSICAL_PLANETS:
                        for h_own in d1_grahas[b].get("ruled_houses", []):
                            house_yoga_data[h_own]["raja_yoga_score"] += 100.0
                            house_yoga_data[h_own]["active_yogas"].append({
                                "type": "Rāja Yoga",
                                "role": "Owned by participating planet",
                                "planets": [b1, b2],
                                "points": 100.0
                            })

    # 3. Mahāpuruṣa Yoga (and Inverse Mahāpuruṣa)
    for p in CLASSICAL_PLANETS:
        p_house = planet_house_map.get(p)
        if p_house in [1, 4, 7, 10]:
            p_status = d1_grahas[p].get("dignity")
            if not p_status:
                p_status = d1_grahas[p].get("dignity_breakdown", {}).get("final_dignity", "Neutral")
            d_p = DICARA_D1_DIGNITY_MAP.get(p_status, 0.0)
            pts = d_p * 100.0

            # Occupied Kendra
            house_yoga_data[p_house]["mahapurusha_score"] += pts
            house_yoga_data[p_house]["active_yogas"].append({
                "type": "Mahāpuruṣa Yoga",
                "role": "Occupied Kendra",
                "planets": [p],
                "points": round(pts, 2)
            })

            # Owned houses
            for h_own in d1_grahas[p].get("ruled_houses", []):
                house_yoga_data[h_own]["mahapurusha_score"] += pts
                house_yoga_data[h_own]["active_yogas"].append({
                    "type": "Mahāpuruṣa Yoga",
                    "role": "Owned by Kendra planet",
                    "planets": [p],
                    "points": round(pts, 2)
                })

    # 4. Daridra Yoga (Misfortune Yoga & Dusthāna Reversal)
    checked_daridra_pairs = set()

    for i in range(len(CLASSICAL_PLANETS)):
        for j in range(i + 1, len(CLASSICAL_PLANETS)):
            p1 = CLASSICAL_PLANETS[i]
            p2 = CLASSICAL_PLANETS[j]

            if not bodies_combine(p1, p2):
                continue

            pair_key = tuple(sorted([p1, p2]))
            if pair_key in checked_daridra_pairs:
                continue

            r1 = set(d1_grahas[p1].get("ruled_houses", []))
            r2 = set(d1_grahas[p2].get("ruled_houses", []))

            # 1st-Lord Immunity: If a planet rules House 1, its secondary Dusthana ownership is unblemished
            d1_dust = r1.intersection({6, 8, 12}) if 1 not in r1 else set()
            d2_dust = r2.intersection({6, 8, 12}) if 1 not in r2 else set()

            # Requires at least one to rule a Dusthana
            if not (d1_dust or d2_dust):
                continue

            checked_daridra_pairs.add(pair_key)

            occ_houses = [planet_house_map[p1], planet_house_map[p2]]

            # Dusthana Reversal Exception:
            # When two Dusthana lords combine, or combination occurs inside a Dusthana (6, 8, 12)
            is_reversal = bool((d1_dust and d2_dust) or any(h in [6, 8, 12] for h in occ_houses))

            # Credit points per participating planet (no deduplication)
            for p in [p1, p2]:
                h_occ = planet_house_map[p]
                pts_occ = 100.0 if (is_reversal and h_occ in [6, 8, 12]) else -100.0
                house_yoga_data[h_occ]["daridra_yoga_score"] += pts_occ
                house_yoga_data[h_occ]["active_yogas"].append({
                    "type": "Daridra Yoga",
                    "role": "Occupied house",
                    "planets": [p1, p2],
                    "points": pts_occ
                })

                for h_own in d1_grahas[p].get("ruled_houses", []):
                    pts_own = 100.0 if (is_reversal and h_own in [6, 8, 12]) else -100.0
                    house_yoga_data[h_own]["daridra_yoga_score"] += pts_own
                    house_yoga_data[h_own]["active_yogas"].append({
                        "type": "Daridra Yoga",
                        "role": "Owned by participating planet",
                        "planets": [p1, p2],
                        "points": pts_own
                    })

    # Compute total yoga scores
    for h in range(1, 13):
        data = house_yoga_data[h]
        tot = (
            data["parivartana_score"] +
            data["raja_yoga_score"] +
            data["mahapurusha_score"] +
            data["daridra_yoga_score"]
        )
        data["total_yoga_score"] = round(tot, 2)
        data["parivartana_score"] = round(data["parivartana_score"], 2)
        data["raja_yoga_score"] = round(data["raja_yoga_score"], 2)
        data["mahapurusha_score"] = round(data["mahapurusha_score"], 2)
        data["daridra_yoga_score"] = round(data["daridra_yoga_score"], 2)

    return house_yoga_data


def evaluate_houses_of_life(chart_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main Orchestrator for Vic DiCara's "Houses of Life" Evaluation System.
    Executes Phases 1 through 9, synthesizes composite scores, and formats the output schema.
    """
    # Phase 1: Chart Geometry
    geometry = _extract_whole_sign_geometry(chart_dict)
    d1_grahas = chart_dict["vargas"]["D1"]["grahas"]
    adv_aspects = chart_dict.get("advanced_aspects", {})

    # Phase 2: Functional Nature relative to Lagna
    func_natures = calculate_functional_nature(geometry["ascendant_sign"])

    # Phase 4: Interactions & Cusp Dominance
    influences = calculate_cusp_and_planet_influences(geometry, d1_grahas, adv_aspects)

    # Phase 5: Planetary Evaluation
    planets_eval = evaluate_planets_hol(geometry, d1_grahas, func_natures, influences)

    # Phase 6: Basic House Condition
    basic_houses = evaluate_basic_house_conditions(geometry, func_natures, d1_grahas, influences)

    # Phase 7: Relative Houses (Bhavat Bhavam)
    rel_houses = evaluate_relative_houses_bhavat_bhavam(geometry, d1_grahas, influences)

    # Phase 8: House Walls (Kartari)
    wall_houses = evaluate_house_walls_kartari(geometry, d1_grahas, func_natures)

    # Phase 9: House Yogas
    yoga_houses = evaluate_house_yogas_hol(geometry, d1_grahas)

    # House Synthesis
    final_houses: Dict[str, Any] = {}

    for h, h_data in geometry["houses"].items():
        lord = h_data["lord"]
        occupants = h_data["occupants"]

        b_score = basic_houses[h]["score"]

        lord_score = planets_eval[lord]["final_assessment_score"]
        occ_scores = {occ: planets_eval[occ]["final_assessment_score"] for occ in occupants}

        if occ_scores:
            lord_and_occ_avg = (lord_score + sum(occ_scores.values())) / (1.0 + len(occ_scores))
        else:
            lord_and_occ_avg = lord_score

        r_score = rel_houses[h]["score"]
        w_score = wall_houses[h]["score"]
        y_score = yoga_houses[h]["total_yoga_score"]

        composite = (b_score + lord_and_occ_avg + r_score + w_score + y_score) / 5.0
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

        # Basic cusp impact
        cusp_contribs = basic_houses[h]["planet_contributions"]
        if cusp_contribs:
            extreme_p = max(cusp_contribs.keys(), key=lambda k: abs(cusp_contribs[k]))
            extreme_val = cusp_contribs[extreme_p]
            if abs(extreme_val) >= 40.0:
                verb = "aspectual support from" if extreme_val > 0 else "aspectual pressure from"
                drivers.append(f"Significant {verb} {extreme_p} on Cusp ({extreme_val:+.1f})")

        # Yoga driver
        if abs(y_score) >= 50.0:
            active_yogas = yoga_houses[h]["active_yogas"]
            if active_yogas:
                top_y = max(active_yogas, key=lambda y: abs(y["points"]))
                drivers.append(f"{top_y['type']} ({top_y['points']:+.1f})")

        # Wall driver
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
                "lord_assessment": {
                    "lord": lord,
                    "lord_final_score": lord_score,
                    "occupants_final_scores": occ_scores
                },
                "relative_house_bhavat_bhavam": rel_houses[h],
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

    summary_rankings = {
        "houses_by_composite_score": sorted_houses,
        "planets_by_final_score": sorted_planets,
        "top_flourishing_houses": sorted_houses[:3],
        "most_challenged_houses": sorted_houses[-3:]
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
