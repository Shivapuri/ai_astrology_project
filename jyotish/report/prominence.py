"""
jyotish/report/prominence.py
Parāśarī Planetary Prominence & Opportunity Engine.

Calculates the stage volume and opportunity a planet possesses to manifest its raw strength:
    Prominence Score = SBR × (1.0 + Σ Opportunity Weights)

Where:
    SBR (Shadbala Ratio) = Calculated Rupas / 6.0 (uniform standard baseline of 6.0 Rupas,
    eliminating artificial bias from individual textbook minimum requirements).

Architecture & Features:
1. Classical Graha Yuddha (Planetary War):
   - Strictly applies to the 5 true physical grahas (Mars through Saturn within 1°00').
   - Venusian immunity (Venus never loses a planetary war).
   - Northern celestial declination (Krānti) determines victor for all other pairs.
   - Virūpa/Rupa auto-detection scales values > 30.0 to Rupas before point transfer.
2. 4 Parāśarī Opportunity Groups (8 Canonical Interaction Vectors):
   - Group 1: Core Anchors
     * Sudarśana Cakra Alignment: Conjunction (10°) and Sphuṭa Dṛṣṭi aspects cast onto
       Ascendant degree (100%), Moon degree (75%), and Sun degree (50%).
     * Sensitive Cusp Doors: Proximity to numerical degrees of Ascendant, Moon, and Sun
       with cyclical 30° boundary wrapping (Bhāva Madhya equal doorways).
     * Ascendant Lord Sovereign Alignment: Calibrated sovereign anchor bonus (+0.10) for
       Lagna Lord plus aspects and conjunctions cast onto the Lagna Lord by other planets.
   - Group 2: Aspect Flow Volume
     * Total Sphuṭa Dṛṣṭi Volume: Quantifiable aspect units cast (classical 7 grahas only)
       and received (all 9 bodies), scaling at +0.05 per 60-Virūpa unit.
   - Group 3: Houses & Stage Sharing
     * House Prominence & Stage Sharing: Kendras (10th highest, then 1st, 4th, 7th) and
       Koṇas (9th, 5th) with points divided equally among co-occupants (stage sharing).
     * Lordship Prominence: Dynamic derivation of ruled houses (H10: +0.15, H1: +0.15,
       H9: +0.12, H4/H7/H5: +0.10, H11: +0.05) with independent credit for dual-Kendra rulers.
   - Group 4: Miscellaneous Catalysts & Roots
     * Dispositor Tree Mechanics: Direct dispositorship of Lagna Lord (+0.10), Sun (+0.05),
       and Moon (+0.05). Terminating root dispositor bonus capped at +0.15 with luminary
       deduplication to prevent dark-house planets from overpowering angle placements.
     * Nodal Amplification & Magnetism: Conjunction with Rāhu/Ketu (+0.25) and nodal
       magnetism bonuses for nodes hosting physical grahas.
     * Birth Daśā Lord: Initial life-ruler boost (+0.25) with dynamic Moon nakshatra fallback.
3. Decoupling of Prominence from Dignity:
   - Prominence measures volume/stage visibility (Vector A).
   - Ingests independent 20-point Daśavarga Viṃśopaka dignity scores, Dīptādi/Bālādi avasthās,
     and Net Scale Score as descriptive psychological tone (Vector B).
4. Leaderboard & #1 Chart Commander (Kārakādhipati) designation.
"""

import math
from typing import Dict, Any, List, Optional, Tuple
import jyotish.relationships.relationships as rel
from jyotish.aspects.aspects import get_graha_drishti

ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

SHADBALA_REQUIRED_RUPAS = {
    "Mercury": 7.0,
    "Jupiter": 6.5,
    "Moon": 6.0,
    "Venus": 5.5,
    "Sun": 5.0,
    "Mars": 5.0,
    "Saturn": 5.0,
    "Rahu": 5.0,
    "Ketu": 5.0
}

TRUE_PLANETS_FOR_WAR = ["Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
CLASSICAL_7_GRAHAS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
ALL_9_GRAHAS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]


def degree_separation_in_sign(deg1: float, deg2: float) -> float:
    """
    Computes the shortest angular distance between two degrees within a 30° span.
    Properly handles cyclical sign boundaries (e.g. 0.5° vs 29.5° = 1.0°).
    """
    diff = abs((deg1 % 30.0) - (deg2 % 30.0))
    return min(diff, 30.0 - diff)


def calculate_declination(
    planet: str,
    longitude: float,
    latitude: float = 0.0,
    jd: Optional[float] = None
) -> float:
    """
    Computes celestial declination (Krānti) in degrees (-90.0 to +90.0).
    Uses exact spherical coordinate transformation from ecliptic coordinates.
    """
    eps = math.radians(23.4392911)
    lam = math.radians(longitude % 360.0)
    beta = math.radians(latitude)
    sin_dec = math.sin(beta) * math.cos(eps) + math.cos(beta) * math.sin(eps) * math.sin(lam)
    sin_dec = max(-1.0, min(1.0, sin_dec))
    return math.degrees(math.asin(sin_dec))


def resolve_graha_yuddha(
    d1_grahas: Dict[str, Any],
    shadbala_data: Optional[Dict[str, Any]],
    jd: Optional[float] = None
) -> Tuple[Dict[str, float], List[Dict[str, Any]]]:
    """
    Detects and resolves classical Planetary War (Graha Yuddha):
    - Applies strictly to the classical 5 true planets: Mars, Mercury, Jupiter, Venus, Saturn.
    - Occurs when two planets are within 1°00' (60 arcminutes) of longitude in D1.
    - Venus never loses a planetary war (Bhrigu immunity / Asura Guru power).
    - For all other combinations, the planet with the higher Northern Declination wins.
    - Point transfer: The winner absorbs the difference between their Shadbala scores;
      the loser loses that exact difference (floored at 0.0).
    """
    adjusted_rupas: Dict[str, float] = {}
    for p in ALL_9_GRAHAS:
        sb_entry = (shadbala_data or {}).get(p, {})
        val = sb_entry.get("Total_Rupas")
        if val is None:
            val = SHADBALA_REQUIRED_RUPAS.get(p, 5.0)
        val = float(val)
        if val > 30.0:  # Supplied in Virupas (e.g. 300 - 500)
            val = val / 60.0
        adjusted_rupas[p] = val

    war_events: List[Dict[str, Any]] = []
    checked_pairs = set()

    for i in range(len(TRUE_PLANETS_FOR_WAR)):
        p1 = TRUE_PLANETS_FOR_WAR[i]
        node1 = d1_grahas.get(p1, {})
        lon1 = node1.get("longitude")
        if lon1 is None:
            continue

        for j in range(i + 1, len(TRUE_PLANETS_FOR_WAR)):
            p2 = TRUE_PLANETS_FOR_WAR[j]
            pair_key = tuple(sorted([p1, p2]))
            if pair_key in checked_pairs:
                continue

            node2 = d1_grahas.get(p2, {})
            lon2 = node2.get("longitude")
            if lon2 is None:
                continue

            # Angular distance on 360° circle
            dist = min((lon1 - lon2) % 360.0, (lon2 - lon1) % 360.0)
            if dist <= 1.0:
                checked_pairs.add(pair_key)

                # Determine Winner
                dec1 = calculate_declination(p1, lon1, node1.get("latitude", 0.0), jd=jd)
                dec2 = calculate_declination(p2, lon2, node2.get("latitude", 0.0), jd=jd)

                if p1 == "Venus":
                    winner, loser = p1, p2
                    reason = "Venusian Immunity (Venus never loses a Planetary War)"
                elif p2 == "Venus":
                    winner, loser = p2, p1
                    reason = "Venusian Immunity (Venus never loses a Planetary War)"
                else:
                    if dec1 >= dec2:
                        winner, loser = p1, p2
                        reason = f"{p1} higher northern declination ({dec1:.2f}° vs {dec2:.2f}°)"
                    else:
                        winner, loser = p2, p1
                        reason = f"{p2} higher northern declination ({dec2:.2f}° vs {dec1:.2f}°)"

                # Score Transfer
                score_w = adjusted_rupas[winner]
                score_l = adjusted_rupas[loser]
                delta = abs(score_w - score_l)

                adjusted_rupas[winner] = round(score_w + delta, 3)
                adjusted_rupas[loser] = round(max(0.0, score_l - delta), 3)

                war_events.append({
                    "planet1": p1,
                    "planet2": p2,
                    "separation_deg": round(dist, 4),
                    "winner": winner,
                    "loser": loser,
                    "dec_winner": round(dec1 if winner == p1 else dec2, 2),
                    "dec_loser": round(dec2 if winner == p1 else dec1, 2),
                    "point_transfer": round(delta, 3),
                    "reason": reason
                })

    return adjusted_rupas, war_events


def compute_planetary_prominence(
    vargas_data: Dict[str, Any],
    shadbala_data: Optional[Dict[str, Any]],
    advanced_aspects: Optional[Dict[str, Any]] = None,
    nakshatras_grahas: Optional[Dict[str, Any]] = None,
    vimshottari_at_birth: Optional[Dict[str, Any]] = None,
    planetary_eval: Optional[Dict[str, Any]] = None,
    vimshopaka_data: Optional[Dict[str, Any]] = None,
    jd: Optional[float] = None
) -> Dict[str, Any]:
    """
    Computes Parāśarī Planetary Prominence along with Vector B (Dignity Mood).

    Prominence Score = Shadbala Ratio × (1.0 + Σ Opportunity Weights)

    Ingests:
        - vargas_data: Complete harmonic charts (D1 cusps, grahas, lagna)
        - shadbala_data: Ingested directly from Astra's Shadbala engine
        - advanced_aspects: Sphuta Drishti aspect matrix
        - nakshatras_grahas: Planetary nakshatra positions
        - vimshottari_at_birth: Starting Mahadasha info
        - planetary_eval: Dignity mood evaluation (Deeptaadi, Balaadi, Net Scale)
        - vimshopaka_data: 20-point Varga Vimshopaka calculations (Dasavarga / Shodasavarga)
        - jd: Julian Day for exact astronomical declination

    Returns:
        Structured dictionary containing:
        - leaderboard: Sorted list of grahas by prominence_score descending
        - chart_commander: Rank #1 planet details
        - prominence_map: {planet: prominence_score}
        - graha_yuddha_events: List of resolved planetary wars
    """
    d1_data = vargas_data.get("D1", {})
    d1_grahas = d1_data.get("grahas", {})
    d1_lagna = d1_data.get("lagna", {})
    lagna_sign = d1_lagna.get("sign", "Aries")
    lagna_lon = float(d1_lagna.get("longitude", 0.0))
    lagna_deg = float(d1_lagna.get("degree_0_to_30", lagna_lon % 30.0))
    lagna_lord = rel.SIGN_LORDS.get(lagna_sign, "Mars")

    eval_planets = (planetary_eval or {}).get("planets", {})

    # Extract vimshopaka scores if available, or compute dynamically if harmonic charts exist
    vim_scores: Dict[str, float] = {}
    if vimshopaka_data:
        scores_dict = vimshopaka_data.get("scores", {})
        vim_scores = (
            scores_dict.get("Dasavarga")
            or scores_dict.get("Shodasavarga")
            or scores_dict.get("Shadvarga")
            or vimshopaka_data.get("dasavarga")
            or vimshopaka_data.get("shadvarga")
            or {}
        )
    elif vargas_data and len(vargas_data) > 1:
        try:
            from jyotish.vimshopaka.vimshopaka import calculate_varga_vimshopaka_engine
            calculated_vim = calculate_varga_vimshopaka_engine({"vargas": vargas_data})
            vim_scores = calculated_vim.get("scores", {}).get("Dasavarga", {})
        except Exception:
            vim_scores = {}

    # 1. Resolve Classical Graha Yuddha (Planetary War)
    adjusted_rupas, war_events = resolve_graha_yuddha(d1_grahas, shadbala_data, jd=jd)

    # 2. Key Coordinates
    sun_lon = float(d1_grahas.get("Sun", {}).get("longitude", 0.0))
    sun_deg = float(d1_grahas.get("Sun", {}).get("degree_0_to_30", sun_lon % 30.0))
    moon_lon = float(d1_grahas.get("Moon", {}).get("longitude", 0.0))
    moon_deg = float(d1_grahas.get("Moon", {}).get("degree_0_to_30", moon_lon % 30.0))

    rahu_lon = float(d1_grahas.get("Rahu", {}).get("longitude", 0.0))
    ketu_lon = float(d1_grahas.get("Ketu", {}).get("longitude", 180.0))

    # Initial Daśā Lord with robust fallback to Moon nakshatra lord
    birth_dasha_lord = (vimshottari_at_birth or {}).get("mahadasha")
    if not birth_dasha_lord:
        birth_dasha_lord = (nakshatras_grahas or {}).get("Moon", {}).get("nakshatra_lord")

    # 3. Dispositor Tree Mechanics (Terminating chains for any planet)
    active_classical = [pl for pl in CLASSICAL_7_GRAHAS if pl in d1_grahas]
    if not active_classical:
        active_classical = list(CLASSICAL_7_GRAHAS)

    direct_parent: Dict[str, str] = {}
    for pl in active_classical:
        p_sign_name = d1_grahas.get(pl, {}).get("sign", "Aries")
        direct_parent[pl] = rel.SIGN_LORDS.get(p_sign_name, "Mars")

    terminating_dispositors: Dict[str, List[str]] = {pl: [] for pl in active_classical}
    for p_source in active_classical:
        visited = []
        curr = p_source
        while curr not in visited:
            visited.append(curr)
            parent = direct_parent.get(curr)
            if not parent or parent not in active_classical:
                break
            if parent == curr:  # Planet in its own sign terminates the chain
                terminating_dispositors[curr].append(p_source)
                break
            curr = parent

    # 4. House Occupancy Map (for stage sharing)
    lagna_idx = ZODIAC_SIGNS.index(lagna_sign) if lagna_sign in ZODIAC_SIGNS else 0
    house_occupants: Dict[int, List[str]] = {h: [] for h in range(1, 13)}

    for p in ALL_9_GRAHAS:
        p_data = d1_grahas.get(p, {})
        p_sign = p_data.get("sign", "Aries")
        p_idx = ZODIAC_SIGNS.index(p_sign) if p_sign in ZODIAC_SIGNS else 0
        h_num = (p_idx - lagna_idx) % 12 + 1
        house_occupants[h_num].append(p)

    ranked_list: List[Dict[str, Any]] = []

    for p in ALL_9_GRAHAS:
        p_data = d1_grahas.get(p, {})
        p_lon = float(p_data.get("longitude", 0.0))
        p_deg = float(p_data.get("degree_0_to_30", p_lon % 30.0))
        p_sign = p_data.get("sign", "Aries")
        p_idx = ZODIAC_SIGNS.index(p_sign) if p_sign in ZODIAC_SIGNS else 0
        h_num = (p_idx - lagna_idx) % 12 + 1

        p_eval = eval_planets.get(p, {})
        p_nak_node = (nakshatras_grahas or {}).get(p, {})
        p_nakshatra = p_nak_node.get("nakshatra", "--")
        p_nak_lord = p_nak_node.get("nakshatra_lord", "--")

        # Step 1: Shadbala Ratio (SBR)
        # Use uniform standard base 6.0 Rupas so Rupas scale naturally without distorting grahas:
        calc_rupas = adjusted_rupas.get(p, 5.0)
        sbr = round(calc_rupas / 6.0, 3)  # Uniform baseline: 6.0 Rupas = 1.0 standard strength

        # Step 2: Calculate the 8 Opportunity Vectors
        opp_weights = 0.0
        opp_reasons: List[str] = []

        # Vector 1: Sudarśana Cakra Alignment & Aspects
        # Unified Anchors: Ascendant (100%), Moon (75%), Sun (50%)
        sudarshana_anchors = [
            ("Ascendant", lagna_lon, 1.00),
            ("Moon", moon_lon, 0.75),
            ("Sun", sun_lon, 0.50)
        ]

        for name, anchor_lon, weight_mult in sudarshana_anchors:
            if name == "Moon" and p == "Moon":
                continue
            if name == "Sun" and p == "Sun":
                continue

            # Conjunction within 10°
            dist = min((p_lon - anchor_lon) % 360.0, (anchor_lon - p_lon) % 360.0)
            if dist <= 10.0:
                w_conj = round((1.0 - (dist / 10.0)) * 0.30 * weight_mult, 3)
                opp_weights += w_conj
                opp_reasons.append(f"Sudarśana: {name} Conjunction ({dist:.1f}°, +{w_conj:.2f})")

            # Aspect cast onto Anchor Point (Safe guard: classical 7 grahas only)
            if p in CLASSICAL_7_GRAHAS:
                asp_virupas = get_graha_drishti(p, p_lon, anchor_lon)
                asp_value = asp_virupas / 60.0
                if asp_value >= 0.20:
                    w_asp = round(asp_value * 0.25 * weight_mult, 3)
                    opp_weights += w_asp
                    opp_reasons.append(f"Sudarśana: Aspect onto {name} ({asp_value:.2f} unit, +{w_asp:.2f})")

        # Vector 2: Sensitive Cusp Doors (Equal-degree doorways with cyclical boundary wrap)
        # Degree resonance with Ascendant (100%), Moon (75%), and Sun (50%) across all signs
        door_anchors = [
            ("Ascendant", lagna_deg, 1.00),
            ("Moon", moon_deg, 0.75),
            ("Sun", sun_deg, 0.50)
        ]

        for name, anchor_deg, weight_mult in door_anchors:
            if name == "Moon" and p == "Moon":
                continue
            if name == "Sun" and p == "Sun":
                continue
            sep = degree_separation_in_sign(p_deg, anchor_deg)
            if sep <= 3.5:
                w_door = round((1.0 - (sep / 3.5)) * 0.25 * weight_mult, 3)
                opp_weights += w_door
                opp_reasons.append(f"Cusp Door: {name} Degree Resonance ({p_deg:.1f}° vs {anchor_deg:.1f}°, +{w_door:.2f})")

        # Vector 3: Ascendant Lord Sovereign Alignment & Aspect
        if p == lagna_lord:
            opp_weights += 0.10  # Calibrated so H1 ownership isn't double-counted
            opp_reasons.append("Lagna Lord: Primary Sovereign of Physical Vehicle (+0.10)")
        else:
            ll_lon = float(d1_grahas.get(lagna_lord, {}).get("longitude", 0.0))
            # Conjunction to Lagna Lord within 10°
            dist_ll = min((p_lon - ll_lon) % 360.0, (ll_lon - p_lon) % 360.0)
            if dist_ll <= 10.0:
                w_ll_c = round((1.0 - (dist_ll / 10.0)) * 0.25, 3)
                opp_weights += w_ll_c
                opp_reasons.append(f"Lagna Lord Conjunction ({dist_ll:.1f}°, +{w_ll_c:.2f})")
            # Aspect onto Lagna Lord (Safe guard: classical 7 grahas only)
            if p in CLASSICAL_7_GRAHAS:
                ll_virupas = get_graha_drishti(p, p_lon, ll_lon)
                ll_raw = ll_virupas / 60.0
                if ll_raw >= 0.20:
                    w_ll_a = round(ll_raw * 0.25, 3)
                    opp_weights += w_ll_a
                    opp_reasons.append(f"Aspect onto Lagna Lord {lagna_lord} ({ll_raw:.2f} unit, +{w_ll_a:.2f})")

        # Vector 4: Total Sphuṭa Dṛṣṭi Volume (Safe guard: classical grahas only)
        cast_units = 0.0
        if p in CLASSICAL_7_GRAHAS:
            for target_p in CLASSICAL_7_GRAHAS:
                if target_p == p:
                    continue
                t_lon = float(d1_grahas.get(target_p, {}).get("longitude", 0.0))
                cast_units += get_graha_drishti(p, p_lon, t_lon) / 60.0

        received_units = 0.0
        for source_p in CLASSICAL_7_GRAHAS:
            if source_p == p:
                continue
            s_lon = float(d1_grahas.get(source_p, {}).get("longitude", 0.0))
            received_units += get_graha_drishti(source_p, s_lon, p_lon) / 60.0

        total_drishti = cast_units + received_units
        if total_drishti > 0.0:
            w_drishti = round(total_drishti * 0.05, 3)
            opp_weights += w_drishti
            opp_reasons.append(f"Sphuṭa Dṛṣṭi Volume ({total_drishti:.2f} units, +{w_drishti:.2f})")

        # Vector 5: House Prominence & Stage Sharing
        kendra_kona_scores = {
            10: 0.40,
            1: 0.35,
            9: 0.35,
            4: 0.30,
            7: 0.30,
            5: 0.25,
            11: 0.20,
            2: 0.15,
            3: 0.15,
            6: 0.05,
            8: 0.05,
            12: 0.05
        }
        base_stage = kendra_kona_scores.get(h_num, 0.10)
        co_occupants_count = len(house_occupants.get(h_num, [p]))
        stage_sharing_score = round(base_stage / max(1, co_occupants_count), 3)
        opp_weights += stage_sharing_score

        stage_label = f"House {h_num} Placement"
        if h_num in [1, 4, 7, 10]:
            stage_label = f"Kendra (H{h_num})"
        elif h_num in [5, 9]:
            stage_label = f"Koṇa (H{h_num})"
        if co_occupants_count > 1:
            opp_reasons.append(f"{stage_label} Stage Sharing (/{co_occupants_count} occupants, +{stage_sharing_score:.2f})")
        else:
            opp_reasons.append(f"{stage_label} Unshared Stage (+{stage_sharing_score:.2f})")

        # House Ownership Prominence (Dynamic calculation fallback if ruled_houses is empty)
        ruled = p_data.get("ruled_houses", [])
        if not ruled:
            lagna_idx = ZODIAC_SIGNS.index(lagna_sign) if lagna_sign in ZODIAC_SIGNS else 0
            ruled = [
                h for h in range(1, 13)
                if rel.SIGN_LORDS.get(ZODIAC_SIGNS[(lagna_idx + h - 1) % 12]) == p
            ]

        owner_score = 0.0
        if 10 in ruled: owner_score += 0.15
        if 1 in ruled:  owner_score += 0.15
        if 9 in ruled:  owner_score += 0.12
        if 4 in ruled:  owner_score += 0.10
        if 7 in ruled:  owner_score += 0.10
        if 5 in ruled:  owner_score += 0.10
        if 11 in ruled: owner_score += 0.05

        if owner_score > 0.0:
            opp_weights += owner_score
            ruled_str = ", ".join(f"H{r}" for r in sorted(ruled))
            opp_reasons.append(f"Lordship Prominence ({ruled_str}, +{owner_score:.2f})")

        # Vector 6: Dispositor Tree Mechanics (Calibrated Group 4 Scaling)
        dispositor_score = 0.0
        already_credited = set()

        if p != lagna_lord and p == direct_parent.get(lagna_lord):
            dispositor_score += 0.10
            already_credited.add(lagna_lord)
            opp_reasons.append(f"Dispositor of Lagna Lord {lagna_lord} (+0.10)")

        if p != "Sun" and p == direct_parent.get("Sun"):
            dispositor_score += 0.05
            already_credited.add("Sun")
            opp_reasons.append("Dispositor of the Sun (+0.05)")

        if p != "Moon" and p == direct_parent.get("Moon"):
            dispositor_score += 0.05
            already_credited.add("Moon")
            opp_reasons.append("Dispositor of the Moon (+0.05)")

        all_dependents = [d for d in terminating_dispositors.get(p, []) if d != p]
        remaining_dependents = [d for d in all_dependents if d not in already_credited]

        if all_dependents:
            # Subtle nudge for being a terminating root, capped at +0.15
            w_disp = round(min(0.15, 0.05 + (0.02 * len(remaining_dependents))), 3)
            dispositor_score += w_disp
            dep_str = ", ".join(all_dependents)
            opp_reasons.append(f"Final Dispositor for [{dep_str}] (+{w_disp:.2f})")
        elif p in terminating_dispositors.get(p, []):
            dispositor_score += 0.05
            opp_reasons.append("Swakshetra Root Anchor (+0.05)")

        opp_weights += dispositor_score

        # Vector 7: Nodal Amplification & Magnetism
        if p in ["Rahu", "Ketu"]:
            node_lon = rahu_lon if p == "Rahu" else ketu_lon
            planets_near_node = []
            for other_p in CLASSICAL_7_GRAHAS:
                other_lon = float(d1_grahas.get(other_p, {}).get("longitude", 0.0))
                d = min((other_lon - node_lon) % 360.0, (node_lon - other_lon) % 360.0)
                if d <= 12.0:
                    planets_near_node.append((other_p, d))

            if planets_near_node:
                w_node = round(sum((1.0 - (d / 12.0)) * 0.20 for _, d in planets_near_node), 3)
                opp_weights += w_node
                p_names = ", ".join(name for name, _ in planets_near_node)
                opp_reasons.append(f"Nodal Magnetism: Hosting [{p_names}] (+{w_node:.2f})")
        else:
            dist_rahu = min((p_lon - rahu_lon) % 360.0, (rahu_lon - p_lon) % 360.0)
            dist_ketu = min((p_lon - ketu_lon) % 360.0, (ketu_lon - p_lon) % 360.0)
            closest_node_dist = min(dist_rahu, dist_ketu)
            closest_node_name = "Rāhu" if dist_rahu <= dist_ketu else "Ketu"

            if closest_node_dist <= 12.0:
                w_node = round((1.0 - (closest_node_dist / 12.0)) * 0.25, 3)
                opp_weights += w_node
                opp_reasons.append(f"Nodal Amplification: Conjunct {closest_node_name} ({closest_node_dist:.1f}°, +{w_node:.2f})")

        # Vector 8: Birth Daśā Lord
        if birth_dasha_lord and p == birth_dasha_lord:
            opp_weights += 0.25
            opp_reasons.append(f"Birth Daśā Lord: Starting Life Ruler ({birth_dasha_lord}, +0.25)")

        # Final Prominence Score
        opp_weights = round(opp_weights, 3)
        prominence_score = round(sbr * (1.0 + opp_weights), 2)

        # Vector B: Psychological Dignity Mood & Maturity
        avasthas = p_data.get("avasthas", {})
        deeptadi_obj = avasthas.get("deeptadi", "Swastha")
        deeptadi = deeptadi_obj.get("state", "Swastha") if isinstance(deeptadi_obj, dict) else str(deeptadi_obj)
        balaadi_obj = avasthas.get("bala", "Yuva")
        balaadi = balaadi_obj.get("state", "Yuva") if isinstance(balaadi_obj, dict) else str(balaadi_obj)

        # Vimśopaka 20-point Dignity Score (real Dasavarga/Shodasavarga or Shadvarga scaled)
        if p in vim_scores:
            vimshopak = float(vim_scores[p])
        elif "varga_score" in p_eval:
            vimshopak = float(p_eval["varga_score"])
        elif "step1_shadvarga" in p_eval and "weighted_dignity_pct" in p_eval["step1_shadvarga"]:
            # Map 0-100% dignity to 0-20 Vimśopaka scale (100% = 20.0, 50% = 10.0)
            vimshopak = round(float(p_eval["step1_shadvarga"]["weighted_dignity_pct"]) / 5.0, 1)
        elif "functional_dignity" in p_eval and "base_dignity_pct" in p_eval["functional_dignity"]:
            vimshopak = round(float(p_eval["functional_dignity"]["base_dignity_pct"]) / 5.0, 1)
        else:
            vimshopak = 10.0  # Classical Parāśarī Neutral midpoint is 10.0 out of 20.0

        net_scale = float(p_eval.get("net_scale_score", 0.0))
        expression_mode = str(p_eval.get("expression_mode", "Constructive"))

        ranked_list.append({
            "planet": p,
            "sign": p_sign,
            "house": h_num,
            "nakshatra": p_nakshatra,
            "nakshatra_lord": p_nak_lord,
            "prominence_score": prominence_score,
            "shadbala_rupas": round(calc_rupas, 2),
            "shadbala_ratio": sbr,
            "opportunity_weights": opp_weights,
            "opportunity_reasons": opp_reasons,
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
    prominence_map = {r["planet"]: r["prominence_score"] for r in ranked_list}

    return {
        "leaderboard": ranked_list,
        "chart_commander": commander,
        "prominence_map": prominence_map,
        "graha_yuddha_events": war_events
    }
