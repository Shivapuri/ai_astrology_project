"""
jyotish/yogas/character_growth_yogas.py
Character & Growth Yogas (Vasumatī, Amalā, Puṣkala, Śakaṭa).
Scripture: Phaladeepika Ch. 6.14–18, BPHS Ch. 37.
"""

from typing import List, Dict, Any, Set
from jyotish.yogas.models import (
    YogaInstance, YogaCategory, YogaStatus, YogaBreakerDetail
)
from jyotish.yogas.breakers import (
    get_house_of_planet, get_sign_of_planet, get_house_rulers, get_planets_data,
    get_lagna_sign, get_aspect_score,
    audit_trishadaya_interference, audit_combustion, audit_dusthana_placement,
    SIGN_LORDS, ZODIAC_SIGNS, ASPECT_PALPABLE_THRESHOLD, ASPECT_MARGINAL_THRESHOLD
)
from jyotish.relationships.relationships import (
    get_natural_relationship, get_temporary_relationship, get_compound_relationship
)

BENEFICS = ("Jupiter", "Venus", "Mercury")
MALEFICS = ("Sun", "Mars", "Saturn", "Rahu", "Ketu")
UPACHAYA_HOUSES = (3, 6, 10, 11)


def detect_character_and_growth_yogas(chart: Dict[str, Any]) -> List[YogaInstance]:
    """Scans chart for Vasumatī, Amalā, Puṣkala, and Śakaṭa Yogas."""
    detected: List[YogaInstance] = []
    lagna_sign = get_lagna_sign(chart)
    planets_data = get_planets_data(chart)
    if not lagna_sign or not planets_data:
        return detected

    planet_houses = {p: get_house_of_planet(chart, p) for p in planets_data}
    moon_house = planet_houses.get("Moon", 0)
    jup_house = planet_houses.get("Jupiter", 0)

    # =========================================================================
    # 1. VASUMATĪ YOGA (Immense Self-Generating Wealth — Phaladeepika 6.16)
    # =========================================================================
    # Natural benefics (Jupiter, Venus, Mercury) in Upachayas (3, 6, 10, 11)
    # from Lagna OR from Moon.
    # Graded 3-tier system:
    #   Uttama (Full): All 3 benefics in Upachayas
    #   Madhyama (Middling): Any 2 benefics in Upachayas
    #   Svalpa (Minor): Any 1 benefic in Upachaya

    benefics_in_upachaya_lagna = [
        p for p in BENEFICS
        if planet_houses.get(p, 0) in UPACHAYA_HOUSES
    ]

    benefics_in_upachaya_moon = []
    if moon_house > 0:
        benefics_in_upachaya_moon = [
            p for p in BENEFICS
            if ((planet_houses.get(p, 0) - moon_house) % 12 + 1) in UPACHAYA_HOUSES
        ]

    # Evaluate best count between Lagna and Moon orientation
    count_lagna = len(benefics_in_upachaya_lagna)
    count_moon = len(benefics_in_upachaya_moon)

    if count_lagna > 0 or count_moon > 0:
        if count_lagna >= count_moon:
            best_count = count_lagna
            best_planets = benefics_in_upachaya_lagna
            base_ref = "Ascendant (Lagna)"
            houses_inv = [planet_houses[p] for p in best_planets]
        else:
            best_count = count_moon
            best_planets = benefics_in_upachaya_moon
            base_ref = "Moon (Chandra)"
            houses_inv = [planet_houses[p] for p in best_planets]

        if best_count == 3:
            tier_name = "Uttama (Peerless Riches)"
            score = 90.0
            effect_desc = "Grants inexhaustible, self-generating wealth; the native commands abundant independent income without financial want."
        elif best_count == 2:
            tier_name = "Madhyama (Substantial Wealth)"
            score = 80.0
            effect_desc = "Grants strong financial stability, comfortable assets, and enduring commercial independence."
        else:
            tier_name = "Svalpa (Modest Independence)"
            score = 70.0
            effect_desc = "Grants solid self-sufficiency, steady earning capacity, and gradual freedom from debt."

        breakers = []
        breakers.extend(audit_combustion(best_planets, chart))
        for b in breakers:
            score -= b.penalty
        score = max(30.0, score)
        status = YogaStatus.PURE if score >= 75.0 else YogaStatus.STAINED

        detected.append(YogaInstance(
            id=f"vasumati_yoga_{best_count}",
            name=f"Vasumatī Yoga — {tier_name}",
            category=YogaCategory.CHARACTER,
            status=status,
            plausibility_score=round(score, 1),
            participating_planets=best_planets,
            participating_houses=houses_inv,
            scripture_ref="Phaladeepika 6.16",
            archetype=f"Growth-House Fortification: {best_count} natural benefic(s) occupy Upachayas from {base_ref}, driving steady accumulation of wealth.",
            manifestation_effects=[
                effect_desc,
                f"Continuous asset generation represented by {', '.join(best_planets)} in growth houses (Upachayas)."
            ],
            positive_factors=[
                f"{best_count} natural benefic(s) ({', '.join(best_planets)}) occupy Upachaya houses ({', '.join(str(h) for h in houses_inv)}) from {base_ref}."
            ],
            breakers=breakers
        ))

    # =========================================================================
    # 2. AMALĀ YOGA (The Spotless Reputation — Phaladeepika 6.17)
    # =========================================================================
    # Natural benefic alone in the 10th house from Lagna OR Moon, free from malefics.
    h10_lagna = 10
    h10_moon = ((moon_house + 9) % 12) + 1 if moon_house > 0 else 0

    for base_name, target_h in [("Lagna", h10_lagna), ("Moon", h10_moon)]:
        if target_h <= 0:
            continue
        benefics_in_10 = [p for p in BENEFICS if planet_houses.get(p) == target_h]
        malefics_in_10 = [p for p in MALEFICS if planet_houses.get(p) == target_h]

        if benefics_in_10:
            score = 85.0
            breakers = []
            if malefics_in_10:
                breakers.append(YogaBreakerDetail(
                    factor="Malefic Corruption in 10th House",
                    culprit_planet=", ".join(malefics_in_10),
                    description=f"Natural malefic(s) ({', '.join(malefics_in_10)}) share the 10th house, tarnishing spotless public standing.",
                    penalty=35.0
                ))
                score -= 35.0

            breakers.extend(audit_combustion(benefics_in_10, chart))
            for b in breakers:
                score -= b.penalty
            score = max(25.0, score)
            status = YogaStatus.PURE if score >= 75.0 else YogaStatus.STAINED

            detected.append(YogaInstance(
                id=f"amala_yoga_{base_name.lower()}",
                name=f"Amalā Yoga (from {base_name})",
                category=YogaCategory.CHARACTER,
                status=status,
                plausibility_score=round(score, 1),
                participating_planets=benefics_in_10,
                participating_houses=[target_h],
                scripture_ref="Phaladeepika 6.17",
                archetype=f"The Spotless Legacy: Pure benefic ({', '.join(benefics_in_10)}) in the 10th house from {base_name}, bestowing civic virtue and lasting honor.",
                manifestation_effects=[
                    "Spotless public reputation, respected career standing, and unblemished character.",
                    "Lasting societal honor, philanthropic achievements, and moral leadership."
                ],
                positive_factors=[
                    f"Natural benefic(s) ({', '.join(benefics_in_10)}) occupy the 10th house (House {target_h}) from {base_name}."
                ],
                breakers=breakers
            ))
            # If detected from Lagna, avoid duplicate Moon detection unless different
            if base_name == "Lagna" and h10_lagna == h10_moon:
                break

    # =========================================================================
    # 3. PUṢKALA YOGA (Abundant Splendor — Phaladeepika 6.18)
    # =========================================================================
    # Lord of Moon sign + Lord of Ascendant join together in a Kendra in a friendly sign,
    # with the Ascendant aspected by a strong planet.
    house_rulers = get_house_rulers(chart)
    lagna_lord = house_rulers.get(1, [None])[0]

    moon_sign = get_sign_of_planet(chart, "Moon")
    moon_lord = SIGN_LORDS.get(moon_sign)

    if lagna_lord and moon_lord:
        ll_house = planet_houses.get(lagna_lord, 0)
        ml_house = planet_houses.get(moon_lord, 0)

        # Must join in the same house and that house must be a Kendra (1, 4, 7, 10)
        if ll_house == ml_house and ll_house in (1, 4, 7, 10) and ll_house > 0:
            shared_sign = get_sign_of_planet(chart, lagna_lord)
            sign_host = SIGN_LORDS.get(shared_sign)

            # Check friendliness to sign host
            # Evaluate compound relationship if host is different
            is_friendly_host = False
            if sign_host:
                if sign_host in (lagna_lord, moon_lord):
                    is_friendly_host = True  # In own sign
                else:
                    host_idx = ZODIAC_SIGNS.index(shared_sign) if shared_sign in ZODIAC_SIGNS else 0
                    ll_idx = ZODIAC_SIGNS.index(get_sign_of_planet(chart, lagna_lord))
                    nat_rel = get_natural_relationship(lagna_lord, sign_host)
                    temp_rel = get_temporary_relationship(ll_idx, host_idx)
                    comp = get_compound_relationship(nat_rel, temp_rel)
                    is_friendly_host = comp in ("Friend", "Great Friend")

            # Check aspect on Lagna
            aspect_on_lagna = False
            for p in planets_data:
                asp = get_aspect_score(chart, p, "Lagna")
                if asp >= ASPECT_MARGINAL_THRESHOLD:
                    aspect_on_lagna = True
                    break

            if is_friendly_host:
                score = 85.0
                pos_factors = [
                    f"Ascendant Lord ({lagna_lord}) and Moon Lord ({moon_lord}) unite in Kendra House {ll_house} ({shared_sign}).",
                    f"Hosted favorably in {shared_sign} (ruled by {sign_host})."
                ]
                breakers = []
                if not aspect_on_lagna:
                    breakers.append(YogaBreakerDetail(
                        factor="Missing Palpable Aspect on Lagna",
                        culprit_planet="Lagna",
                        description="The Ascendant does not receive a palpable aspect from a strong planet.",
                        penalty=15.0
                    ))
                    score -= 15.0

                breakers.extend(audit_combustion([lagna_lord, moon_lord], chart))
                for b in breakers:
                    score -= b.penalty
                score = max(30.0, score)
                status = YogaStatus.PURE if score >= 75.0 else YogaStatus.STAINED

                detected.append(YogaInstance(
                    id="puskala_yoga",
                    name="Puṣkala Yoga",
                    category=YogaCategory.CHARACTER,
                    status=status,
                    plausibility_score=round(score, 1),
                    participating_planets=list(set([lagna_lord, moon_lord])),
                    participating_houses=[ll_house, 1],
                    scripture_ref="Phaladeepika 6.18",
                    archetype="Abundant Splendor: Ascendant Lord and Moon Lord combine in an auspicious angular seat, bestowing magnetic prestige and wealth.",
                    manifestation_effects=[
                        "Overflowing material wealth, sweet and persuasive speech, and high social renown.",
                        "Honored by government or corporate superiors; broad civic influence."
                    ],
                    positive_factors=pos_factors,
                    breakers=breakers
                ))

    # =========================================================================
    # 4. ŚAKAṬA YOGA (The Heavy Cart & Setbacks — Phaladeepika 6.14)
    # =========================================================================
    # Moon in 6th, 8th, or 12th from Jupiter.
    # Cancellation (Bhaṅga): If Moon is in Kendra (1, 4, 7, 10) from Lagna!
    if moon_house > 0 and jup_house > 0:
        rel_from_jup = ((moon_house - jup_house) % 12) + 1
        if rel_from_jup in (6, 8, 12):
            moon_in_lagna_kendra = moon_house in (1, 4, 7, 10)

            if moon_in_lagna_kendra:
                detected.append(YogaInstance(
                    id="sakata_yoga_rescued",
                    name="Śakaṭa Yoga (Rescued / Bhaṅga)",
                    category=YogaCategory.CHARACTER,
                    status=YogaStatus.RESCUED,
                    plausibility_score=75.0,
                    participating_planets=["Moon", "Jupiter"],
                    participating_houses=[moon_house, jup_house],
                    scripture_ref="Phaladeepika 6.14",
                    archetype="Neutralized Cart Friction: Moon sits in a dusthana from Jupiter but is anchored in a Lagna Kendra, averting chronic loss.",
                    manifestation_effects=[
                        "Initial fluctuations between sudden success and temporary setbacks resolve into steady worldly balance.",
                        "Lagna angular anchor protects reputation and maintains overall career stability."
                    ],
                    positive_factors=[
                        f"Moon in Kendra House {moon_house} from Lagna completely rescues the {rel_from_jup}th-house dusthana tension from Jupiter."
                    ],
                    breakers=[]
                ))
            else:
                breakers = [
                    YogaBreakerDetail(
                        factor="Adverse Lunar-Jupiter Axis",
                        culprit_planet="Moon",
                        description=f"Moon is placed in House {rel_from_jup} (Dusthana) from Jupiter without Kendra anchor from Lagna.",
                        penalty=30.0
                    )
                ]
                detected.append(YogaInstance(
                    id="sakata_yoga",
                    name="Śakaṭa Yoga (The Heavy Cart)",
                    category=YogaCategory.CHARACTER,
                    status=YogaStatus.STAINED,
                    plausibility_score=60.0,
                    participating_planets=["Moon", "Jupiter"],
                    participating_houses=[moon_house, jup_house],
                    scripture_ref="Phaladeepika 6.14",
                    archetype="The Rolling Cart: Fortunes oscillate like a heavy cartwheel; periods of progress alternate with exhausting setbacks.",
                    manifestation_effects=[
                        "Cycles of rapid financial/professional gain followed by unexpected downturns or fatigue.",
                        "Feels like pulling a heavy cart alone; requires emotional resilience and steadfast perseverance."
                    ],
                    positive_factors=[
                        f"Moon in House {moon_house}, Jupiter in House {jup_house}."
                    ],
                    breakers=breakers
                ))

    return detected
