"""
jyotish/yogas/neechabhanga.py
Universal Debilitation Reversal Engine (Nīcabhaṅga Rāja Yoga & Simple Cancellation).
Evaluates debilitated planets across all classical conditions from Phaladeepika Ch. 7 (Verses 24–30)
and Brihat Parashara Hora Shastra (BPHS Ch. 39).
"""

from typing import List, Dict, Any, Tuple
from jyotish.yogas.models import (
    YogaInstance, YogaCategory, YogaStatus, YogaBreakerDetail
)
from jyotish.yogas.breakers import (
    get_house_of_planet, get_sign_of_planet, get_planets_data,
    get_lagna_sign, get_aspect_score,
    audit_combustion, audit_shadbala_muscle,
    DEBILITATION_SIGNS, EXALTATION_SIGNS, SIGN_LORDS, PLANET_EXALTED_IN_SIGN,
    ASPECT_PALPABLE_THRESHOLD, ASPECT_MARGINAL_THRESHOLD
)

CLASSICAL_PLANETS = ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn")


def audit_neecha_bhanga_details(
    planet: str,
    chart: Dict[str, Any]
) -> Tuple[bool, List[str], float, Dict[str, Any]]:
    """
    Audits the Classical Cancellation of Debility (Nīcabhaṅga) conditions
    according to Phaladeepika 7.24-30:
    1. Dispositor of debilitation sign in Kendra (1, 4, 7, 10) from Lagna or Moon (+30%).
    2. Exaltation lord (tad-uccāṃśa-nātha) or planet exalted in debilitation sign in Kendra (+30%).
    3. Cumulative Dual Lord Prominence: Both #1 and #2 met by distinct planets (+20% bonus).
    4. Dispositor directly aspects the debilitated planet (>= 45 Virūpas: +30%, >= 30 Virūpas: +15%)
       or dispositor is itself exalted (+30%).
    5. Exalted co-occupant sharing the sign (+35%).
    6. Fallen planet in Kendra from Lagna or Moon alongside distinct dispositor/exaltation lord (+30%),
       or angular on its own when not already counted via self-exaltation lordship (+20% Lagna / +15% Moon).

    Returns:
        (is_rescued, reasons, cumulative_score, metadata)
    """
    planets_data = get_planets_data(chart)
    p_info = planets_data.get(planet) or {}
    p_sign = p_info.get("sign", "") if isinstance(p_info, dict) else ""

    if not p_sign or p_sign != DEBILITATION_SIGNS.get(planet):
        return False, [], 0.0, {}

    debilitation_sign = p_sign
    dispositor = SIGN_LORDS.get(debilitation_sign)
    exaltation_sign = EXALTATION_SIGNS.get(planet)
    exaltation_lord = SIGN_LORDS.get(exaltation_sign)
    exalted_in_deb_sign = PLANET_EXALTED_IN_SIGN.get(debilitation_sign)

    moon_house = get_house_of_planet(chart, "Moon")
    p_house = get_house_of_planet(chart, planet)
    disp_house = get_house_of_planet(chart, dispositor) if dispositor else 0
    exalt_lord_house = get_house_of_planet(chart, exaltation_lord) if exaltation_lord else 0
    exalted_guest_house = get_house_of_planet(chart, exalted_in_deb_sign) if exalted_in_deb_sign else 0

    reasons: List[str] = []
    bonus = 0.0
    conditions_met: Dict[str, bool] = {}
    rescuing_planets: List[str] = []

    def _add_rescuer(p_name: str) -> None:
        if p_name and p_name != planet and p_name not in rescuing_planets:
            rescuing_planets.append(p_name)

    # Condition 1: Dispositor of debilitation sign in Kendra from Lagna (1,4,7,10) or Moon (+30%)
    # Guard: Moon is trivially H1 from itself; never count dispositor == "Moon" as Kendra from Moon.
    c1_met = False
    if dispositor and disp_house > 0:
        disp_from_moon = (
            ((disp_house - moon_house) % 12 + 1)
            if (dispositor != "Moon" and moon_house > 0)
            else 0
        )
        if disp_house in (1, 4, 7, 10):
            c1_met = True
            _add_rescuer(dispositor)
            reasons.append(f"Condition 1 (Dispositor in Lagna Kendra): {dispositor} (lord of {debilitation_sign}) occupies Kendra H{disp_house} (+30%).")
            bonus += 30.0
        elif disp_from_moon in (1, 4, 7, 10):
            c1_met = True
            _add_rescuer(dispositor)
            reasons.append(f"Condition 1 (Dispositor in Chandra Kendra): {dispositor} (lord of {debilitation_sign}) is in Kendra H{disp_from_moon} from Moon (+30%).")
            bonus += 30.0
    conditions_met["c1"] = c1_met

    # Condition 2: Exaltation lord in Kendra from Lagna or Moon (+30%)
    # 2A: Lord of the planet's exaltation sign (tad-uccāṃśa-nātha)
    # 2B: Planet that exalts in the debilitation sign (if distinct from dispositor and planet)
    c2_met = False
    c2_via_self = False
    c2_distinct = False
    if exaltation_lord and exalt_lord_house > 0:
        el_from_moon = (
            ((exalt_lord_house - moon_house) % 12 + 1)
            if (exaltation_lord != "Moon" and moon_house > 0)
            else 0
        )
        if exalt_lord_house in (1, 4, 7, 10):
            c2_met = True
            c2_via_self = (exaltation_lord == planet)
            c2_distinct = (exaltation_lord != planet and exaltation_lord != dispositor)
            _add_rescuer(exaltation_lord)
            reasons.append(f"Condition 2 (Exaltation Lord in Kendra): {exaltation_lord} (rules exaltation sign {exaltation_sign}) occupies Kendra H{exalt_lord_house} from Lagna (+30%).")
            bonus += 30.0
        elif el_from_moon in (1, 4, 7, 10):
            c2_met = True
            c2_via_self = (exaltation_lord == planet)
            c2_distinct = (exaltation_lord != planet and exaltation_lord != dispositor)
            _add_rescuer(exaltation_lord)
            reasons.append(f"Condition 2 (Exaltation Lord in Kendra): {exaltation_lord} occupies Kendra H{el_from_moon} from Moon (+30%).")
            bonus += 30.0

    # Evaluate 2B if 2A was not met by a distinct planet, and exalted_in_deb_sign is not already co-occupying debilitation_sign (Cond 5)
    if (not c2_distinct) and exalted_in_deb_sign and exalted_in_deb_sign != dispositor and exalted_in_deb_sign != planet and exalted_guest_house > 0 and exalted_guest_house != p_house:
        eg_from_moon = (
            ((exalted_guest_house - moon_house) % 12 + 1)
            if (exalted_in_deb_sign != "Moon" and moon_house > 0)
            else 0
        )
        if exalted_guest_house in (1, 4, 7, 10):
            c2_distinct = True
            _add_rescuer(exalted_in_deb_sign)
            reasons.append(f"Condition 2 (Planet Exalted in Sign in Kendra): {exalted_in_deb_sign} occupies Kendra H{exalted_guest_house} from Lagna (+30%).")
            if not c2_met:
                bonus += 30.0
            c2_met = True
        elif eg_from_moon in (1, 4, 7, 10):
            c2_distinct = True
            _add_rescuer(exalted_in_deb_sign)
            reasons.append(f"Condition 2 (Planet Exalted in Sign in Kendra): {exalted_in_deb_sign} occupies Kendra H{eg_from_moon} from Moon (+30%).")
            if not c2_met:
                bonus += 30.0
            c2_met = True
    conditions_met["c2"] = c2_met

    # Condition 3: Cumulative Dual Lord Prominence (both #1 and #2 met by distinct planets -> extra +20%)
    c3_met = c1_met and c2_distinct
    if c3_met:
        reasons.append("Condition 3 (Dual Lord Prominence): Both dispositor and exaltation lord occupy Kendras (+20% cumulative prestige bonus).")
        bonus += 20.0
    conditions_met["c3"] = c3_met

    # Condition 4: Dispositor directly aspects the debilitated planet or is itself exalted
    c4_met = False
    if dispositor:
        asp_disp = get_aspect_score(chart, dispositor, planet)
        if asp_disp >= ASPECT_PALPABLE_THRESHOLD:
            c4_met = True
            _add_rescuer(dispositor)
            reasons.append(f"Condition 4 (Direct Aspect by Dispositor): {dispositor} aspects fallen {planet} with palpable {asp_disp:.0f} Virūpas (+30%).")
            bonus += 30.0
        elif asp_disp >= ASPECT_MARGINAL_THRESHOLD:
            c4_met = True
            _add_rescuer(dispositor)
            reasons.append(f"Condition 4 (Direct Aspect by Dispositor, Marginal): {dispositor} aspects fallen {planet} with {asp_disp:.0f} Virūpas (+15%).")
            bonus += 15.0

        disp_sign = get_sign_of_planet(chart, dispositor)
        if disp_sign and disp_sign == EXALTATION_SIGNS.get(dispositor):
            c4_met = True
            _add_rescuer(dispositor)
            reasons.append(f"Condition 4B (Exalted Dispositor): {dispositor} (ruler of {debilitation_sign}) is itself exalted in {disp_sign} (+30%).")
            bonus += 30.0
    conditions_met["c4"] = c4_met

    # Condition 5: Exalted co-occupant sharing the sign (+35%)
    c5_met = False
    for other_p, data in planets_data.items():
        if not isinstance(data, dict):
            continue
        if other_p != planet and data.get("sign") == debilitation_sign:
            if data.get("sign") == EXALTATION_SIGNS.get(other_p):
                c5_met = True
                _add_rescuer(other_p)
                reasons.append(f"Condition 5 (Exalted Co-occupant): {other_p} is exalted in {debilitation_sign} alongside fallen {planet} (+35%).")
                bonus += 35.0
                break
    conditions_met["c5"] = c5_met

    # Condition 6: Fallen planet in Kendra from Lagna or Moon
    c6_met = False
    p_from_moon = (
        ((p_house - moon_house) % 12 + 1)
        if (planet != "Moon" and p_house > 0 and moon_house > 0)
        else 0
    )
    p_kendra_lagna = p_house in (1, 4, 7, 10)
    p_kendra_moon = p_from_moon in (1, 4, 7, 10)
    p_is_kendra = p_kendra_lagna or p_kendra_moon

    # Check if conjoined with dispositor or exaltation lord not already counted in C1/C2/C5
    uncredited_co_lord = None
    if dispositor and dispositor != planet and disp_house > 0 and p_house == disp_house and not c1_met:
        uncredited_co_lord = dispositor
    elif exaltation_lord and exaltation_lord != planet and exalt_lord_house > 0 and p_house == exalt_lord_house and not c2_met:
        uncredited_co_lord = exaltation_lord

    kendra_label = f"Kendra H{p_house} from Lagna" if p_kendra_lagna else f"Kendra H{p_from_moon} from Chandra (H{p_house})"

    if p_is_kendra and uncredited_co_lord:
        c6_met = True
        _add_rescuer(uncredited_co_lord)
        reasons.append(f"Condition 6 (Fallen Planet Angular with Lord): Fallen {planet} is in {kendra_label} conjoined with {uncredited_co_lord} (+30%).")
        bonus += 30.0
    elif p_is_kendra and not c2_via_self:
        c6_met = True
        pts = 20.0 if p_kendra_lagna else 15.0
        reasons.append(f"Condition 6 (Angular Fallen Planet): Fallen {planet} occupies {kendra_label}, forcing active public engagement (+{pts:.0f}%).")
        bonus += pts
    conditions_met["c6"] = c6_met

    is_rescued = len(reasons) >= 1 and bonus >= 30.0

    metadata = {
        "conditions_met": conditions_met,
        "dispositor": dispositor,
        "exaltation_lord": exaltation_lord,
        "rescuing_planets": rescuing_planets,
        "p_house": p_house,
        "debilitation_sign": debilitation_sign,
    }

    return is_rescued, reasons, min(100.0, bonus), metadata


def audit_neecha_bhanga(planet: str, chart: Dict[str, Any]) -> Tuple[bool, List[str], float]:
    """
    Standard interface for checking if a planet's debility is cancelled.
    Compatible drop-in replacement for existing breaker calls.
    """
    is_rescued, reasons, bonus, _ = audit_neecha_bhanga_details(planet, chart)
    return is_rescued, reasons, bonus


def detect_neechabhanga_yogas(chart: Dict[str, Any]) -> List[YogaInstance]:
    """
    Scans the chart for any debilitated planets and produces distinct YogaInstance records:
    - Kendra/Koṇa (1, 4, 5, 7, 9, 10): Nīcabhaṅga Rāja Yoga (Royal eminence forged through adversity).
    - Duṣṭhāna (6, 8, 12): Nīca Bhaṅga Cancellation (Deficit overcome without worldly command).
    - Other Houses (2, 3, 11): Nīca Bhaṅga Cancellation (Overcoming vulnerability with personal effort).
    """
    detected: List[YogaInstance] = []

    for planet in CLASSICAL_PLANETS:
        is_rescued, reasons, score, meta = audit_neecha_bhanga_details(planet, chart)
        if not is_rescued:
            continue

        p_house = meta.get("p_house", get_house_of_planet(chart, planet))
        deb_sign = meta.get("debilitation_sign", get_sign_of_planet(chart, planet))
        rescuing_planets = meta.get("rescuing_planets") or []
        dispositor = meta.get("dispositor")

        participating_planets = [planet]
        for rp in rescuing_planets:
            if rp not in participating_planets:
                participating_planets.append(rp)
        if len(participating_planets) == 1 and dispositor and dispositor != planet:
            participating_planets.append(dispositor)

        participating_houses = [p_house] if p_house > 0 else []
        for rp in participating_planets[1:]:
            rp_h = get_house_of_planet(chart, rp)
            if rp_h > 0 and rp_h not in participating_houses:
                participating_houses.append(rp_h)

        # Audit secondary breakers on the fallen planet (combustion, Shadbala deficit)
        breakers: List[YogaBreakerDetail] = []
        breakers.extend(audit_combustion([planet], chart))
        shad_breakers, shad_pos = audit_shadbala_muscle([planet], chart)
        breakers.extend(shad_breakers)

        positive_factors = list(reasons) + shad_pos
        net_score = score
        for b in breakers:
            net_score -= b.penalty
        net_score = max(5.0, min(100.0, net_score))

        # Output Classification
        if p_house in (1, 4, 5, 7, 9, 10):
            if net_score >= 75.0 and not breakers:
                status = YogaStatus.PURE
            elif net_score >= 30.0:
                status = YogaStatus.RESCUED
            else:
                status = YogaStatus.BROKEN

            detected.append(YogaInstance(
                id=f"neechabhanga_raja_yoga_{planet.lower()}",
                name=f"Nīcabhaṅga Rāja Yoga ({planet})",
                category=YogaCategory.NEECHABHANGA,
                status=status,
                plausibility_score=round(net_score, 1),
                participating_planets=participating_planets,
                participating_houses=participating_houses,
                scripture_ref="Phaladeepika 7.24–30, BPHS 39.1-15",
                archetype=f"Adversity Transmuted to Sovereignty: Fallen {planet} in {deb_sign} is fully redeemed in auspicious House {p_house}, turning profound vulnerability into royal resilience.",
                manifestation_effects=[
                    f"Converts early limitations or structural deficits of {planet} into unshakeable personal tenacity and worldly distinction.",
                    f"Bestows sovereign authority, respect, and executive eminence, culminating during {planet}'s Daśā periods."
                ],
                positive_factors=positive_factors,
                breakers=breakers
            ))
        elif p_house in (6, 8, 12):
            capped_score = min(65.0, net_score)
            status = YogaStatus.RESCUED if capped_score >= 30.0 else YogaStatus.BROKEN
            detected.append(YogaInstance(
                id=f"neecha_bhanga_simple_{planet.lower()}",
                name=f"Nīca Bhaṅga Cancellation ({planet})",
                category=YogaCategory.NEECHABHANGA,
                status=status,
                plausibility_score=round(capped_score, 1),
                participating_planets=participating_planets,
                participating_houses=participating_houses,
                scripture_ref="Phaladeepika 7.24–30",
                archetype=f"Deficit Overcome without Worldly Command: Debility of {planet} in House {p_house} is cancelled, neutralizing acute distress without granting wide institutional authority.",
                manifestation_effects=[
                    f"Overcomes health, litigation, or psychological burdens associated with fallen {planet} in House {p_house}.",
                    "Brings internal peace and recovery from hardship, but lacks the angular foundation to confer public sovereignty."
                ],
                positive_factors=positive_factors,
                breakers=breakers
            ))
        else:
            capped_score = min(70.0, net_score)
            status = YogaStatus.RESCUED if capped_score >= 30.0 else YogaStatus.BROKEN
            detected.append(YogaInstance(
                id=f"neecha_bhanga_simple_{planet.lower()}",
                name=f"Nīca Bhaṅga Cancellation ({planet})",
                category=YogaCategory.NEECHABHANGA,
                status=status,
                plausibility_score=round(capped_score, 1),
                participating_planets=participating_planets,
                participating_houses=participating_houses,
                scripture_ref="Phaladeepika 7.24–30",
                archetype=f"Deficit Overcome without Worldly Command: Debility of {planet} in House {p_house} is cancelled through consistent personal effort.",
                manifestation_effects=[
                    f"Steadily resolves deficits of fallen {planet} in House {p_house} into practical competence.",
                    "Provides financial or communicative recovery through persistent discipline."
                ],
                positive_factors=positive_factors,
                breakers=breakers
            ))

    return detected
