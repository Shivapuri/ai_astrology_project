"""
jyotish/yogas/neechabhanga.py
Universal Debilitation Reversal Engine (Nīcabhaṅga Rāja Yoga & Simple Cancellation).
Evaluates debilitated planets across all 6 classical conditions from Phaladeepika Ch. 7 (Verses 24–30)
and Brihat Parashara Hora Shastra (BPHS Ch. 39).
"""

from typing import List, Dict, Any, Tuple
from jyotish.yogas.models import (
    YogaInstance, YogaCategory, YogaStatus, YogaBreakerDetail
)
from jyotish.yogas.breakers import (
    get_house_of_planet, get_sign_of_planet, get_planets_data,
    get_lagna_sign, get_aspect_score,
    DEBILITATION_SIGNS, EXALTATION_SIGNS, SIGN_LORDS, PLANET_EXALTED_IN_SIGN,
    ASPECT_PALPABLE_THRESHOLD, ASPECT_MARGINAL_THRESHOLD
)

CLASSICAL_PLANETS = ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn")


def audit_neecha_bhanga_details(
    planet: str,
    chart: Dict[str, Any]
) -> Tuple[bool, List[str], float, Dict[str, Any]]:
    """
    Audits the 6 Classical Cancellation of Debility (Nīcabhaṅga) conditions
    according to Phaladeepika 7.24-30:
    1. Dispositor of debilitation sign in Kendra (1, 4, 7, 10) from Lagna or Moon (+30%).
    2. Exaltation lord of the sign in Kendra from Lagna or Moon (+25%).
    3. Cumulative Dual Lord Prominence: If BOTH #1 and #2 are met simultaneously (+20% bonus).
    4. Dispositor directly aspects the debilitated planet with >= 45.0 Virūpas (+25%).
    5. Exalted co-occupant sharing the sign (+35%).
    6. Fallen planet in Kendra from Lagna or Moon alongside dispositor or exaltation lord (+30%).

    Returns:
        (is_rescued, reasons, cumulative_score, metadata)
    """
    planets_data = get_planets_data(chart)
    p_info = planets_data.get(planet, {})
    p_sign = p_info.get("sign", "")

    if p_sign != DEBILITATION_SIGNS.get(planet):
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

    # Condition 1: Dispositor of debilitation sign in Kendra from Lagna (1,4,7,10) or Moon (+30%)
    c1_met = False
    if dispositor and disp_house > 0:
        disp_from_moon = ((disp_house - moon_house) % 12 + 1) if moon_house > 0 else 0
        if disp_house in (1, 4, 7, 10):
            c1_met = True
            reasons.append(f"Condition 1 (Dispositor in Lagna Kendra): {dispositor} (lord of {debilitation_sign}) occupies Kendra H{disp_house} (+30%).")
            bonus += 30.0
        elif disp_from_moon in (1, 4, 7, 10):
            c1_met = True
            reasons.append(f"Condition 1 (Dispositor in Chandra Kendra): {dispositor} (lord of {debilitation_sign}) is in Kendra H{disp_from_moon} from Moon (+25%).")
            bonus += 25.0
    conditions_met["c1"] = c1_met

    # Condition 2: Exaltation lord in Kendra from Lagna or Moon (+25%)
    # Checks either:
    # 2A: Lord of the planet's exaltation sign (tad-uccāṃśa-nātha)
    # 2B: Planet that exalts in the debilitation sign
    c2_met = False
    if exaltation_lord and exalt_lord_house > 0:
        el_from_moon = ((exalt_lord_house - moon_house) % 12 + 1) if moon_house > 0 else 0
        if exalt_lord_house in (1, 4, 7, 10):
            c2_met = True
            reasons.append(f"Condition 2 (Exaltation Lord in Kendra): {exaltation_lord} (rules exaltation sign {exaltation_sign}) occupies Kendra H{exalt_lord_house} from Lagna (+25%).")
            bonus += 25.0
        elif el_from_moon in (1, 4, 7, 10):
            c2_met = True
            reasons.append(f"Condition 2 (Exaltation Lord in Kendra): {exaltation_lord} occupies Kendra H{el_from_moon} from Moon (+25%).")
            bonus += 25.0

    if not c2_met and exalted_in_deb_sign and exalted_guest_house > 0:
        eg_from_moon = ((exalted_guest_house - moon_house) % 12 + 1) if moon_house > 0 else 0
        if exalted_guest_house in (1, 4, 7, 10):
            c2_met = True
            reasons.append(f"Condition 2 (Planet Exalted in Sign in Kendra): {exalted_in_deb_sign} occupies Kendra H{exalted_guest_house} from Lagna (+25%).")
            bonus += 25.0
        elif eg_from_moon in (1, 4, 7, 10):
            c2_met = True
            reasons.append(f"Condition 2 (Planet Exalted in Sign in Kendra): {exalted_in_deb_sign} occupies Kendra H{eg_from_moon} from Moon (+25%).")
            bonus += 25.0
    conditions_met["c2"] = c2_met

    # Condition 3: Cumulative Dual Lord Prominence (both #1 and #2 met -> extra +20%)
    c3_met = c1_met and c2_met
    if c3_met:
        reasons.append("Condition 3 (Dual Lord Prominence): Both dispositor and exaltation lord occupy Kendras (+20% cumulative prestige bonus).")
        bonus += 20.0
    conditions_met["c3"] = c3_met

    # Condition 4: Dispositor directly aspects the debilitated planet (>= 45.0 Virūpas -> +25%)
    c4_met = False
    if dispositor:
        asp_disp = get_aspect_score(chart, dispositor, planet)
        if asp_disp >= ASPECT_PALPABLE_THRESHOLD:
            c4_met = True
            reasons.append(f"Condition 4 (Direct Aspect by Dispositor): {dispositor} aspects fallen {planet} with palpable {asp_disp:.0f} Virūpas (+25%).")
            bonus += 25.0
        elif asp_disp >= ASPECT_MARGINAL_THRESHOLD:
            c4_met = True
            reasons.append(f"Condition 4 (Direct Aspect by Dispositor, Marginal): {dispositor} aspects fallen {planet} with {asp_disp:.0f} Virūpas (+15%).")
            bonus += 15.0
    conditions_met["c4"] = c4_met

    # Condition 5: Exalted co-occupant sharing the sign (+35%)
    c5_met = False
    for other_p, data in planets_data.items():
        if other_p != planet and data.get("sign") == debilitation_sign:
            if data.get("sign") == EXALTATION_SIGNS.get(other_p):
                c5_met = True
                reasons.append(f"Condition 5 (Exalted Co-occupant): {other_p} is exalted in {debilitation_sign} alongside fallen {planet} (+35%).")
                bonus += 35.0
                break
    conditions_met["c5"] = c5_met

    # Condition 6: Fallen planet in Kendra from Lagna or Moon alongside dispositor or exaltation lord (+30%)
    c6_met = False
    p_from_moon = ((p_house - moon_house) % 12 + 1) if (p_house > 0 and moon_house > 0) else 0
    p_is_kendra = (p_house in (1, 4, 7, 10)) or (p_from_moon in (1, 4, 7, 10))
    alongside_lord = (
        (disp_house > 0 and p_house == disp_house) or
        (exalt_lord_house > 0 and p_house == exalt_lord_house) or
        (exalted_guest_house > 0 and p_house == exalted_guest_house)
    )

    if p_is_kendra and alongside_lord:
        c6_met = True
        reasons.append(f"Condition 6 (Fallen Planet Angular with Lord): Fallen {planet} is in Kendra H{p_house} alongside its ruler/exaltation lord (+30%).")
        bonus += 30.0
    elif p_is_kendra:
        # Fallen planet angular on its own
        c6_met = True
        reasons.append(f"Condition 6 (Angular Fallen Planet): Fallen {planet} occupies Kendra H{p_house} forcing active public engagement (+20%).")
        bonus += 20.0
    conditions_met["c6"] = c6_met

    is_rescued = len(reasons) >= 1 and bonus >= 30.0

    metadata = {
        "conditions_met": conditions_met,
        "dispositor": dispositor,
        "exaltation_lord": exaltation_lord,
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
        dispositor = meta.get("dispositor")

        participating_planets = [planet]
        if dispositor and dispositor not in participating_planets:
            participating_planets.append(dispositor)

        participating_houses = [p_house]
        if dispositor:
            d_h = get_house_of_planet(chart, dispositor)
            if d_h > 0 and d_h not in participating_houses:
                participating_houses.append(d_h)

        # Output Classification
        if p_house in (1, 4, 5, 7, 9, 10):
            # Angular or Trinal placement -> Rāja Yoga Upgrade
            status = YogaStatus.PURE if score >= 75.0 else YogaStatus.RESCUED
            detected.append(YogaInstance(
                id=f"neechabhanga_raja_yoga_{planet.lower()}",
                name=f"Nīcabhaṅga Rāja Yoga ({planet})",
                category=YogaCategory.NEECHABHANGA,
                status=status,
                plausibility_score=round(score, 1),
                participating_planets=participating_planets,
                participating_houses=participating_houses,
                scripture_ref="Phaladeepika 7.24–30, BPHS 39.1-15",
                archetype=f"Adversity Transmuted to Sovereignty: Fallen {planet} in {deb_sign} is fully redeemed in auspicious House {p_house}, turning profound vulnerability into royal resilience.",
                manifestation_effects=[
                    f"Converts early limitations or structural deficits of {planet} into unshakeable personal tenacity and worldly distinction.",
                    f"Bestows sovereign authority, respect, and executive eminence, culminating during {planet}'s Daśā periods."
                ],
                positive_factors=reasons,
                breakers=[]
            ))
        elif p_house in (6, 8, 12):
            # Duṣṭhāna placement -> Simple Cancellation
            detected.append(YogaInstance(
                id=f"neecha_bhanga_simple_{planet.lower()}",
                name=f"Nīca Bhaṅga Cancellation ({planet})",
                category=YogaCategory.NEECHABHANGA,
                status=YogaStatus.RESCUED,
                plausibility_score=round(score, 1),
                participating_planets=participating_planets,
                participating_houses=participating_houses,
                scripture_ref="Phaladeepika 7.24–30",
                archetype=f"Deficit Overcome without Worldly Command: Debility of {planet} in House {p_house} is cancelled, neutralizing acute distress without granting wide institutional authority.",
                manifestation_effects=[
                    f"Overcomes health, litigation, or psychological burdens associated with fallen {planet} in House {p_house}.",
                    "Brings internal peace and recovery from hardship, but lacks the angular foundation to confer public sovereignty."
                ],
                positive_factors=reasons,
                breakers=[]
            ))
        else:
            # 2nd, 3rd, 11th houses
            detected.append(YogaInstance(
                id=f"neecha_bhanga_simple_{planet.lower()}",
                name=f"Nīca Bhaṅga Cancellation ({planet})",
                category=YogaCategory.NEECHABHANGA,
                status=YogaStatus.RESCUED,
                plausibility_score=round(score, 1),
                participating_planets=participating_planets,
                participating_houses=participating_houses,
                scripture_ref="Phaladeepika 7.24–30",
                archetype=f"Deficit Overcome without Worldly Command: Debility of {planet} in House {p_house} is cancelled through consistent personal effort.",
                manifestation_effects=[
                    f"Steadily resolves deficits of fallen {planet} in House {p_house} into practical competence.",
                    "Provides financial or communicative recovery through persistent discipline."
                ],
                positive_factors=reasons,
                breakers=[]
            ))

    return detected
