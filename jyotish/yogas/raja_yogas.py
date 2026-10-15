"""
jyotish/yogas/raja_yogas.py
Core Kendra-Koṇa & Yogakāraka Engine.
Evaluates True Raja Yoga (9th + 10th), Śaṅkha Yoga (other Kendra-Koṇa alliances),
and Single-Planet Yogakārakas according to Mantreswara's Phaladeepika (Ch. 6 & 7) and BPHS (Ch. 34 & 39).
"""

from typing import List, Dict, Any, Tuple, Set, Optional
from jyotish.yogas.models import (
    YogaInstance, YogaCategory, YogaStatus, YogaBreakerDetail
)
from jyotish.yogas.breakers import (
    get_house_of_planet, get_sign_of_planet, get_house_rulers, get_planets_data,
    get_lagna_sign, get_aspect_score, _first_ruler,
    audit_trishadaya_interference, audit_combustion, audit_dispositor_vitality,
    audit_dusthana_placement, audit_shadbala_muscle, resolve_yoga_score_and_status,
    DEBILITATION_SIGNS, EXALTATION_SIGNS,
    ASPECT_PALPABLE_THRESHOLD, ASPECT_MARGINAL_THRESHOLD
)
from jyotish.yogas.neechabhanga import audit_neecha_bhanga

# Single Planet Raja Yoga Karakas (simultaneous Kendra + Trikona lords)
SINGLE_PLANET_YOGAKARAKAS = {
    "Taurus": ("Saturn", [9, 10]),
    "Cancer": ("Mars", [5, 10]),
    "Leo": ("Mars", [4, 9]),
    "Libra": ("Saturn", [4, 5]),
    "Capricorn": ("Venus", [5, 10]),
    "Aquarius": ("Venus", [4, 9])
}

# Fixed Natural Friendships / Enemies (Naisargika Sambandha)
NAISARGIKA_SAMBANDHA = {
    "Sun": {"Friends": ["Moon", "Mars", "Jupiter"], "Neutrals": ["Mercury"], "Enemies": ["Venus", "Saturn"]},
    "Moon": {"Friends": ["Sun", "Mercury"], "Neutrals": ["Mars", "Jupiter", "Venus", "Saturn"], "Enemies": []},
    "Mars": {"Friends": ["Sun", "Moon", "Jupiter"], "Neutrals": ["Venus", "Saturn"], "Enemies": ["Mercury"]},
    "Mercury": {"Friends": ["Sun", "Venus"], "Neutrals": ["Mars", "Jupiter", "Saturn"], "Enemies": ["Moon"]},
    "Jupiter": {"Friends": ["Sun", "Moon", "Mars"], "Neutrals": ["Saturn"], "Enemies": ["Mercury", "Venus"]},
    "Venus": {"Friends": ["Mercury", "Saturn"], "Neutrals": ["Mars", "Jupiter"], "Enemies": ["Sun", "Moon"]},
    "Saturn": {"Friends": ["Mercury", "Venus"], "Neutrals": ["Jupiter"], "Enemies": ["Sun", "Moon", "Mars"]}
}

KENDRA_HOUSES = [1, 4, 7, 10]
TRIKONA_HOUSES = [1, 5, 9]


def _degree_in_sign(p_info: Dict[str, Any]) -> Optional[float]:
    """Safely extracts degree within sign [0.0, 30.0) from planet dictionary."""
    if not isinstance(p_info, dict):
        return None
    deg = p_info.get("degree_0_to_30")
    if deg is not None:
        try:
            return float(deg) % 30.0
        except (ValueError, TypeError):
            pass
    lon = p_info.get("longitude")
    if lon is not None:
        try:
            return float(lon) % 30.0
        except (ValueError, TypeError):
            pass
    return None


def audit_intervening_planet(
    planet1: str,
    planet2: str,
    chart: Dict[str, Any],
    exempt_planets: Set[str] = frozenset()
) -> List[YogaBreakerDetail]:
    """
    If two planets are in the same sign, verifies whether another planet sits
    between them in longitude. If an enemy or non-exempt natural malefic intervenes,
    it breaks the energetic circuit (-35% penalty).
    """
    breakers = []
    planets_data = get_planets_data(chart)
    p1_info = planets_data.get(planet1) or {}
    p2_info = planets_data.get(planet2) or {}
    if not isinstance(p1_info, dict) or not isinstance(p2_info, dict):
        return breakers

    s1 = p1_info.get("sign")
    s2 = p2_info.get("sign")
    if not s1 or s1 != s2:
        return breakers

    deg1 = _degree_in_sign(p1_info)
    deg2 = _degree_in_sign(p2_info)
    if deg1 is None or deg2 is None:
        return breakers

    min_deg = min(deg1, deg2)
    max_deg = max(deg1, deg2)

    for other_p, data in planets_data.items():
        if other_p in (planet1, planet2):
            continue
        if not isinstance(data, dict) or data.get("sign") != s1:
            continue
        other_deg = _degree_in_sign(data)
        if other_deg is None:
            continue
        if min_deg < other_deg < max_deg:
            is_malefic = other_p in ("Sun", "Mars", "Saturn", "Rahu", "Ketu")
            is_enemy = (
                other_p in NAISARGIKA_SAMBANDHA.get(planet1, {}).get("Enemies", []) or
                other_p in NAISARGIKA_SAMBANDHA.get(planet2, {}).get("Enemies", [])
            )
            # A fellow Lagna/Trikoṇa lord is exempt unless it is a hostile enemy to either planet
            if other_p in exempt_planets and not is_enemy:
                continue

            if is_malefic or is_enemy:
                desc_role = "natural malefic" if is_malefic else "planetary enemy"
                breakers.append(YogaBreakerDetail(
                    factor="Intervening Planet Obstruction",
                    culprit_planet=other_p,
                    description=f"{other_p} ({desc_role}) sits at {other_deg:.1f}° between {planet1} ({deg1:.1f}°) and {planet2} ({deg2:.1f}°) in {s1}, breaking the energetic circuit.",
                    penalty=35.0
                ))
    return breakers


def detect_raja_yogas(chart: Dict[str, Any]) -> List[YogaInstance]:
    """
    Scans chart for single-planet and multi-planet Kendra-Koṇa Raja Yogas:
    - True Raja Yoga: 9th lord (Dharma) and 10th lord (Karma) alliance.
    - Śaṅkha Yoga: Any other Kendra lord (1, 4, 7, 10) combining with a Koṇa lord (1, 5, 9).
    - Single-Planet Yogakārakas: Taurus, Cancer, Leo, Libra, Capricorn, Aquarius.
    """
    detected: List[YogaInstance] = []
    lagna_sign = get_lagna_sign(chart)
    if not lagna_sign:
        return detected

    house_rulers = get_house_rulers(chart)
    planets_data = get_planets_data(chart)
    lagna_lord = _first_ruler(house_rulers, 1)

    # 1. Single-Planet Raja Yoga Karaka
    if lagna_sign in SINGLE_PLANET_YOGAKARAKAS:
        yk_planet, owned_houses = SINGLE_PLANET_YOGAKARAKAS[lagna_sign]
        if yk_planet in planets_data:
            yk_house = get_house_of_planet(chart, yk_planet)
            yk_sign = get_sign_of_planet(chart, yk_planet)
            if yk_house > 0:
                score = 85.0
                positive_factors = [
                    f"Natural Yogakāraka: {yk_planet} simultaneously rules Kendra H{owned_houses[0]} and Trikona H{owned_houses[1]} for {lagna_sign} Lagna.",
                    f"Resides in House {yk_house} ({yk_sign})."
                ]

                if yk_house in (1, 4, 5, 7, 9, 10, 11):
                    positive_factors.append(f"Favorable seat: Resides in supportive House {yk_house}.")
                    score += 5.0
                if yk_sign == EXALTATION_SIGNS.get(yk_planet):
                    positive_factors.append(f"Exalted in {yk_sign}.")
                    score += 10.0

                breakers: List[YogaBreakerDetail] = []
                is_broken = False
                dusthana_already_penalized = False

                # Check Debilitation / Neecha Bhanga
                if yk_sign == DEBILITATION_SIGNS.get(yk_planet):
                    is_rescued, reasons, bonus = audit_neecha_bhanga(yk_planet, chart)
                    if is_rescued:
                        if yk_house in (6, 8, 12):
                            breakers.append(YogaBreakerDetail(
                                factor="Incomplete Foundation (Simple Cancellation in Dusthana)",
                                culprit_planet=yk_planet,
                                description=f"Yogakāraka {yk_planet} has debility cancelled in House {yk_house}. Dusthana cancellation is merely a Simple Cancellation, incapable of conferring sovereign authority.",
                                penalty=60.0
                            ))
                            is_broken = True
                            dusthana_already_penalized = True
                        else:
                            positive_factors.extend(reasons)
                            score += bonus * 0.3
                    else:
                        breakers.append(YogaBreakerDetail(
                            factor="Unredeemed Debilitation",
                            culprit_planet=yk_planet,
                            description=f"Yogakāraka {yk_planet} is in fall in {yk_sign} without cancellation.",
                            penalty=50.0
                        ))
                        is_broken = True

                # Mahita Bhava Requirement (Dusthana Disqualification)
                if yk_house in (6, 8, 12) and not dusthana_already_penalized:
                    breakers.append(YogaBreakerDetail(
                        factor="Dusthana Placement (Bhanga)",
                        culprit_planet=yk_planet,
                        description=f"Yogakāraka {yk_planet} is placed in difficult House {yk_house}. Phaladeepika mandates placement in an auspicious house (Mahita Bhava); placement in a Dusthana breaks the Raja Yoga.",
                        penalty=60.0
                    ))
                    is_broken = True

                is_yk_supreme = (9 in owned_houses and 10 in owned_houses)
                breakers.extend(audit_trishadaya_interference([yk_planet], chart, is_supreme_pairing=is_yk_supreme))
                breakers.extend(audit_combustion([yk_planet], chart))
                breakers.extend(audit_dispositor_vitality([yk_planet], chart))
                shad_brk, shad_pos = audit_shadbala_muscle([yk_planet], chart)
                breakers.extend(shad_brk)
                positive_factors.extend(shad_pos)

                net_score, status = resolve_yoga_score_and_status(score, breakers)
                if is_broken:
                    status = YogaStatus.BROKEN
                    net_score = min(net_score, 25.0)

                detected.append(YogaInstance(
                    id=f"single_yogakaraka_{yk_planet.lower()}",
                    name=f"Rāja Yogakāraka ({yk_planet})",
                    category=YogaCategory.RAJA,
                    status=status,
                    plausibility_score=round(net_score, 1),
                    participating_planets=[yk_planet],
                    participating_houses=[yk_house],
                    scripture_ref="BPHS 34.15-20, Phaladeepika 7.4",
                    archetype=f"The Natural Sovereign: {yk_planet} embodies both divine grace (Trikona) and executive horsepower (Kendra) within a single body.",
                    manifestation_effects=[
                        f"Elevates {lagna_sign} natives into leadership, worldly recognition, and institutional respect.",
                        f"Functions as the primary driver of worldly fortune during {yk_planet}'s Daśā periods."
                    ],
                    positive_factors=positive_factors,
                    breakers=breakers
                ))

    # 2. Multi-Planet Alliances (True Raja Yoga vs. Śaṅkha Yoga)
    kendra_lords: Dict[str, List[int]] = {}
    for kh in KENDRA_HOUSES:
        for lord in house_rulers.get(kh, []):
            kendra_lords.setdefault(lord, []).append(kh)

    trikona_lords: Dict[str, List[int]] = {}
    for th in TRIKONA_HOUSES:
        for lord in house_rulers.get(th, []):
            trikona_lords.setdefault(lord, []).append(th)

    evaluated_pairs: Set[Tuple[str, str]] = set()

    for kl in kendra_lords:
        for tl in trikona_lords:
            if kl == tl:
                continue  # Single planet handled above
            pair_key = tuple(sorted([kl, tl]))
            if pair_key in evaluated_pairs:
                continue
            evaluated_pairs.add(pair_key)

            kl_house = get_house_of_planet(chart, kl)
            tl_house = get_house_of_planet(chart, tl)
            if kl_house == 0 or tl_house == 0:
                continue

            kl_sign = get_sign_of_planet(chart, kl)
            tl_sign = get_sign_of_planet(chart, tl)

            # All Kendra/Trikona houses ruled by each planet in the pair
            kl_all_kk = sorted(set(kendra_lords.get(kl, []) + trikona_lords.get(kl, [])))
            tl_all_kk = sorted(set(kendra_lords.get(tl, []) + trikona_lords.get(tl, [])))

            # Conjunction check: same house or same sign
            is_conjoined = (kl_house == tl_house) or (bool(kl_sign) and kl_sign == tl_sign)

            # Aspect checks via Sphuṭa Dṛṣṭi (0-60 Virūpas)
            aspect_kl_tl = get_aspect_score(chart, kl, tl)
            aspect_tl_kl = get_aspect_score(chart, tl, kl)
            min_aspect = min(aspect_kl_tl, aspect_tl_kl)

            is_mutual_aspect = (aspect_kl_tl >= ASPECT_PALPABLE_THRESHOLD and aspect_tl_kl >= ASPECT_PALPABLE_THRESHOLD)
            is_marginal_aspect = (not is_mutual_aspect) and (min_aspect >= ASPECT_MARGINAL_THRESHOLD)

            # Parivartana: Kendra lord in Koṇa house and Koṇa lord in Kendra house
            # Explicit rule: If either house is 6, 8, or 12, DO NOT create a Raja Yoga (Dainya Parivartana)
            is_exchange = False
            if kl_house not in (6, 8, 12) and tl_house not in (6, 8, 12):
                ruler_of_kl_h = _first_ruler(house_rulers, kl_house)
                ruler_of_tl_h = _first_ruler(house_rulers, tl_house)
                if ruler_of_kl_h == tl and ruler_of_tl_h == kl:
                    if ((kl_house in KENDRA_HOUSES and tl_house in TRIKONA_HOUSES) or
                        (kl_house in TRIKONA_HOUSES and tl_house in KENDRA_HOUSES)):
                        is_exchange = True

            # If none of the modes of combination are satisfied, skip
            if not (is_conjoined or is_mutual_aspect or is_marginal_aspect or is_exchange):
                continue

            is_marginal_only = (
                is_marginal_aspect and not is_conjoined and not is_mutual_aspect and not is_exchange
            )

            # Strict differentiation: True Raja Yoga (9 + 10) vs. Śaṅkha Yoga (other Kendra-Koṇa)
            is_supreme = (
                (9 in tl_all_kk and 10 in kl_all_kk) or
                (9 in kl_all_kk and 10 in tl_all_kk)
            )
            dharma_lord = tl if 9 in tl_all_kk else kl
            karma_lord = kl if dharma_lord == tl else tl

            if is_supreme:
                yoga_title = "Dharma-Karma Adhipati Rāja Yoga"
                yoga_id = f"dharma_karma_raja_yoga_{kl.lower()}_{tl.lower()}"
                scripture_ref = "Phaladeepika 6.36-37, BPHS 39.1-15"
                archetype = "The Marriage of Grace and Action (The King): Highest Dharma meets highest Karma, conferring supreme executive authority and sovereign command."
            else:
                yoga_title = f"Śaṅkha Yoga ({kl} + {tl})"
                yoga_id = f"shankha_yoga_{kl.lower()}_{tl.lower()}"
                scripture_ref = "Phaladeepika 6.36-38"
                archetype = f"The Royal Herald (Conch Shell): Kendra-Trikoṇa alliance between {kl} (Lord of H{kl_all_kk}) and {tl} (Lord of H{tl_all_kk}) announces status and supports worldly prosperity."

            score = 90.0 if is_supreme else 80.0
            positive_factors: List[str] = []
            breakers: List[YogaBreakerDetail] = []
            is_broken = False

            if is_supreme:
                positive_factors.append(f"Supreme Alliance (The King): {dharma_lord} (Lord of H9 Dharma) and {karma_lord} (Lord of H10 Karma) combine.")
            else:
                positive_factors.append(f"Kendra-Trikoṇa Herald (Śaṅkha): {kl} (Lord of H{kl_all_kk}) and {tl} (Lord of H{tl_all_kk}) combine.")

            # Natural Yogakāraka Amplification Bonus
            if lagna_sign in SINGLE_PLANET_YOGAKARAKAS:
                natural_yk_planet, yk_houses = SINGLE_PLANET_YOGAKARAKAS[lagna_sign]
                if natural_yk_planet in (kl, tl):
                    other_p = tl if kl == natural_yk_planet else kl
                    positive_factors.append(
                        f"Natural Yogakāraka Amplification: {natural_yk_planet} is an inherent Yogakāraka for {lagna_sign} Lagna (rules H{yk_houses[0]} & H{yk_houses[1]}), immensely amplifying this alliance with {other_p} (+10% bonus)."
                    )
                    score += 10.0

            dusthana_aspect_houses: List[int] = []

            if is_conjoined:
                positive_factors.append(f"Conjoined in House {kl_house} ({kl_sign}).")
                p_kl_info = planets_data.get(kl) or {}
                p_tl_info = planets_data.get(tl) or {}
                lon_kl = p_kl_info.get("longitude") if isinstance(p_kl_info, dict) else None
                lon_tl = p_tl_info.get("longitude") if isinstance(p_tl_info, dict) else None
                if lon_kl is not None and lon_tl is not None:
                    try:
                        diff = abs(float(lon_kl) - float(lon_tl)) % 360.0
                        if diff > 180.0:
                            diff = 360.0 - diff
                        if diff <= 3.33:
                            positive_factors.append(f"Close Conjunction (Navāṁśa Core): {kl} and {tl} within {diff:.2f}° (<= 3°20').")
                            score += 10.0
                        elif diff > 15.0:
                            breakers.append(YogaBreakerDetail(
                                factor="Wide Conjunction Orb",
                                culprit_planet=f"{kl}/{tl}",
                                description=f"{kl} and {tl} are separated by {diff:.1f}° (> 15°). The wide orb dilutes the energetic alliance.",
                                penalty=20.0
                            ))
                    except (ValueError, TypeError):
                        pass

                # Intervening planet obstruction check (exempt Lagna lord & Trikona lords)
                exempt_set = ({lagna_lord} if lagna_lord else set()) | set(trikona_lords.keys())
                intervening_brk = audit_intervening_planet(kl, tl, chart, exempt_planets=exempt_set)
                breakers.extend(intervening_brk)

                # Mahita Bhava Requirement (Dusthana Disqualification for Conjunction)
                if kl_house in (6, 8, 12):
                    breakers.append(YogaBreakerDetail(
                        factor="Dusthana Conjunction (Bhanga)",
                        culprit_planet=f"{kl}/{tl}",
                        description=f"The conjunction occurs in difficult House {kl_house}. Phaladeepika mandates placement in an auspicious house (Mahita Bhava); conjunction in a Dusthana completely breaks the Raja Yoga.",
                        penalty=65.0
                    ))
                    is_broken = True

            if is_exchange:
                positive_factors.append(f"Mutual Reception (Parivartana): {kl} in H{kl_house} and {tl} in H{tl_house} exchange signs.")
                score += 5.0

            if is_mutual_aspect or is_marginal_only:
                if is_mutual_aspect:
                    positive_factors.append(f"Palpable Mutual Aspect: {kl} and {tl} gaze upon each other ({aspect_kl_tl:.0f} & {aspect_tl_kl:.0f} Virūpas, >= 45V).")
                elif is_marginal_only:
                    positive_factors.append(f"Marginal Mutual Aspect: {kl} and {tl} aspect each other ({aspect_kl_tl:.0f} & {aspect_tl_kl:.0f} Virūpas, 30-44V).")
                    breakers.append(YogaBreakerDetail(
                        factor="Marginal Aspect Connection",
                        culprit_planet=f"{kl}/{tl}",
                        description=f"Mutual aspect between {kl} ({aspect_kl_tl:.0f}V) and {tl} ({aspect_tl_kl:.0f}V) is below palpable 45 Virupa threshold (75%).",
                        penalty=25.0
                    ))

                dusthana_aspect_houses = [h for h in (kl_house, tl_house) if h in (6, 8, 12)]
                if dusthana_aspect_houses:
                    breakers.append(YogaBreakerDetail(
                        factor="Dusthana Aspect Connection (Bhanga)",
                        culprit_planet=f"{kl}/{tl}",
                        description=f"Mutual aspect involves difficult House(s) {dusthana_aspect_houses}. Phaladeepika mandates placement in an auspicious house (Mahita Bhava); aspect across Dusthanas breaks the Raja Yoga.",
                        penalty=65.0
                    ))
                    is_broken = True

            # Audit Unredeemed Debility in both participating planets
            for p in (kl, tl):
                p_s = get_sign_of_planet(chart, p)
                if p_s == DEBILITATION_SIGNS.get(p):
                    is_rescued, r_reasons, r_bonus = audit_neecha_bhanga(p, chart)
                    p_h = get_house_of_planet(chart, p)
                    if is_rescued:
                        if p_h in (6, 8, 12):
                            breakers.append(YogaBreakerDetail(
                                factor="Incomplete Foundation (Simple Cancellation in Dusthana)",
                                culprit_planet=p,
                                description=f"Debilitated {p} has debility cancelled in House {p_h}, which yields only a Simple Cancellation. An angular or trinal seat is required to anchor a Raja Yoga.",
                                penalty=35.0
                            ))
                            is_broken = True
                        else:
                            positive_factors.extend(r_reasons)
                            score += r_bonus * 0.2
                    else:
                        breakers.append(YogaBreakerDetail(
                            factor="Unredeemed Debilitation",
                            culprit_planet=p,
                            description=f"Participating planet {p} is in fall in {p_s} without cancellation.",
                            penalty=50.0
                        ))
                        is_broken = True

            # Layer 2 Breakers per YOGA_ARCHITECTURE.md
            breakers.extend(audit_trishadaya_interference([kl, tl], chart, is_supreme_pairing=is_supreme))
            breakers.extend(audit_combustion([kl, tl], chart))
            if not is_exchange:
                breakers.extend(audit_dispositor_vitality([kl, tl], chart))

            if not is_conjoined and not dusthana_aspect_houses:
                dust_brk = audit_dusthana_placement([kl_house, tl_house], YogaCategory.RAJA)
                if dust_brk:
                    breakers.append(dust_brk)

            shad_brk, shad_pos = audit_shadbala_muscle([kl, tl], chart)
            breakers.extend(shad_brk)
            positive_factors.extend(shad_pos)

            net_score, status = resolve_yoga_score_and_status(score, breakers)

            if is_broken:
                status = YogaStatus.BROKEN
                net_score = min(net_score, 25.0)
            elif is_marginal_only:
                if status == YogaStatus.PURE:
                    status = YogaStatus.STAINED
                net_score = min(net_score, 74.0)
            elif status == YogaStatus.RESCUED and not any(
                "rescued" in f.lower() or "neecha" in f.lower() or "condition" in f.lower()
                for f in positive_factors
            ):
                status = YogaStatus.STAINED

            detected.append(YogaInstance(
                id=yoga_id,
                name=yoga_title,
                category=YogaCategory.RAJA,
                status=status,
                plausibility_score=round(net_score, 1),
                participating_planets=[kl, tl],
                participating_houses=sorted(set([kl_house, tl_house])),
                scripture_ref=scripture_ref,
                archetype=archetype,
                manifestation_effects=[
                    "Commands respect, social influence, professional eminence, and leadership in large organizations.",
                    "Manifests major career breakthroughs during the conjoined or operational Daśā periods."
                ],
                positive_factors=positive_factors,
                breakers=breakers
            ))

    return detected
