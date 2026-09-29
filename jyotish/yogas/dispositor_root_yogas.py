"""
jyotish/yogas/dispositor_root_yogas.py
Dispositor Root Yogas: Kāhala Yoga (Variants A & B) and Parvata Yoga (Authentic & Self-Dispositor).
Scripture: Phaladeepika 6.35–36, BPHS Ch. 36.
"""

from typing import List, Dict, Any
from jyotish.yogas.models import (
    YogaInstance, YogaCategory, YogaStatus, YogaBreakerDetail
)
from jyotish.yogas.breakers import (
    get_house_of_planet, get_sign_of_planet, get_house_rulers, get_planets_data,
    get_lagna_sign, audit_trishadaya_interference, audit_combustion, audit_dusthana_placement,
    SIGN_LORDS, OWN_SIGNS, EXALTATION_SIGNS
)

KENDRA_TRIKONA_HOUSES = (1, 4, 5, 7, 9, 10)
KENDRA_HOUSES = (1, 4, 7, 10)


def detect_dispositor_root_yogas(chart: Dict[str, Any]) -> List[YogaInstance]:
    """Scans chart for Kāhala and Parvata dispositor-root yogas."""
    detected: List[YogaInstance] = []
    lagna_sign = get_lagna_sign(chart)
    planets_data = get_planets_data(chart)
    house_rulers = get_house_rulers(chart)

    if not lagna_sign or not planets_data:
        return detected

    lagna_lord = house_rulers.get(1, [None])[0]
    if not lagna_lord or lagna_lord not in planets_data:
        return detected

    planet_houses = {p: get_house_of_planet(chart, p) for p in planets_data}
    ll_house = planet_houses.get(lagna_lord, 0)
    ll_sign = get_sign_of_planet(chart, lagna_lord)
    ll_dispositor = SIGN_LORDS.get(ll_sign)

    # =========================================================================
    # 1. KĀHALA YOGA (Dual Scriptural Traditions — Phaladeepika 6.35)
    # =========================================================================

    # Variant A: 4th & 10th lords in mutual Kendras (1, 4, 7, 10 from each other)
    # with 1st lord fortified (e.g. not in 6, 8, 12).
    lord_4 = house_rulers.get(4, [None])[0]
    lord_10 = house_rulers.get(10, [None])[0]

    if lord_4 and lord_10 and lord_4 in planets_data and lord_10 in planets_data:
        h4_pos = planet_houses.get(lord_4, 0)
        h10_pos = planet_houses.get(lord_10, 0)

        if h4_pos > 0 and h10_pos > 0:
            diff_4_10 = ((h10_pos - h4_pos) % 12) + 1
            if diff_4_10 in KENDRA_HOUSES:
                score_a = 85.0
                breakers_a = []
                if ll_house in (6, 8, 12):
                    breakers_a.append(YogaBreakerDetail(
                        factor="Lagnesha in Dusthana",
                        culprit_planet=lagna_lord,
                        description=f"Ascendant Lord ({lagna_lord}) sits in Dusthana House {ll_house}, weakening the foundational root of the 4th/10th alliance.",
                        penalty=25.0
                    ))
                    score_a -= 25.0

                breakers_a.extend(audit_combustion([lord_4, lord_10], chart))
                for b in breakers_a:
                    score_a -= b.penalty
                score_a = max(30.0, score_a)
                status_a = YogaStatus.PURE if score_a >= 75.0 else YogaStatus.STAINED

                detected.append(YogaInstance(
                    id="kahala_yoga_variant_a",
                    name="Kāhala Yoga (Variant A: Mutual Kendra Alliance)",
                    category=YogaCategory.DISPOSITOR_ROOT,
                    status=status_a,
                    plausibility_score=round(score_a, 1),
                    participating_planets=list(set([lord_4, lord_10, lagna_lord])),
                    participating_houses=list(set([h4_pos, h10_pos, ll_house])),
                    scripture_ref="Phaladeepika 6.35 (Tradition A)",
                    archetype="The Resounding Drum: 4th Lord (inner base) and 10th Lord (outer action) occupy mutual angles, generating dynamic organizational rhythm.",
                    manifestation_effects=[
                        "Dynamic executive stamina, unwavering resolve, and organizational leadership.",
                        "Ability to lead teams and mobilize resources toward prominent civic or corporate success."
                    ],
                    positive_factors=[
                        f"4th Lord ({lord_4} in H{h4_pos}) and 10th Lord ({lord_10} in H{h10_pos}) occupy mutual Kendra ({diff_4_10}th from each other).",
                        f"Ascendant Lord is {lagna_lord} in House {ll_house}."
                    ],
                    breakers=breakers_a
                ))

    # Variant B: Dispositor of 1st Lord is in high dignity (own/exalted) in Kendra/Trikona
    if ll_dispositor and ll_dispositor in planets_data:
        disp_house = planet_houses.get(ll_dispositor, 0)
        disp_sign = get_sign_of_planet(chart, ll_dispositor)

        disp_is_exalted = (disp_sign == EXALTATION_SIGNS.get(ll_dispositor))
        disp_is_own = (disp_sign in OWN_SIGNS.get(ll_dispositor, []))
        disp_in_kt = disp_house in KENDRA_TRIKONA_HOUSES

        if (disp_is_exalted or disp_is_own) and disp_in_kt:
            score_b = 90.0
            breakers_b = []
            breakers_b.extend(audit_combustion([ll_dispositor, lagna_lord], chart))
            for b in breakers_b:
                score_b -= b.penalty
            score_b = max(30.0, score_b)
            status_b = YogaStatus.PURE if score_b >= 75.0 else YogaStatus.STAINED

            detected.append(YogaInstance(
                id="kahala_yoga_variant_b",
                name="Kāhala Yoga (Variant B: Dispositor Root Chain)",
                category=YogaCategory.DISPOSITOR_ROOT,
                status=status_b,
                plausibility_score=round(score_b, 1),
                participating_planets=list(set([lagna_lord, ll_dispositor])),
                participating_houses=list(set([ll_house, disp_house])),
                scripture_ref="Phaladeepika 6.35 (Tradition B & Vic DiCara Lecture 1)",
                archetype="Strong Dispositor Roots: The host of the Ascendant Lord blazes with dignity in an angle or trine, infusing the personality with unshakeable fortitude.",
                manifestation_effects=[
                    "Deep inner confidence, generational endurance, and unyielding courage under pressure.",
                    "The native stands firm against setbacks because their underlying dispositor root is deeply anchored."
                ],
                positive_factors=[
                    f"Ascendant Lord ({lagna_lord}) hosted in {ll_sign} by {ll_dispositor}.",
                    f"Host dispositor ({ll_dispositor}) is {'exalted' if disp_is_exalted else 'in own sign'} in supportive House {disp_house} ({disp_sign})."
                ],
                breakers=breakers_b
            ))

    # =========================================================================
    # 2. PARVATA YOGA (Mountainous / Enduring Nobility — Phaladeepika 6.36)
    # =========================================================================
    # BOTH the 1st House Lord AND its host dispositor are in high dignity
    # (own sign or exaltation) AND situated in Kendra or Trikoṇa (1, 4, 5, 7, 9, 10).
    ll_is_exalted = (ll_sign == EXALTATION_SIGNS.get(lagna_lord))
    ll_is_own = (ll_sign in OWN_SIGNS.get(lagna_lord, []))
    ll_in_kt = ll_house in KENDRA_TRIKONA_HOUSES

    if (ll_is_exalted or ll_is_own) and ll_in_kt and ll_dispositor:
        # Check if dispositor is itself (Self-Dispositor Loophole)
        is_self_dispositor = (ll_dispositor == lagna_lord)

        if is_self_dispositor:
            # Self-Dispositor Variant: 1st lord in 1st house in own sign (e.g. Mars in Aries rising)
            # Weighted at ~70% plausibility per Vic DiCara Lecture 1
            score = 70.0
            breakers = [
                YogaBreakerDetail(
                    factor="Single-Tier Self-Dispositor Loophole",
                    culprit_planet=lagna_lord,
                    description=f"{lagna_lord} hosts itself in House {ll_house}. Lacks the authentic external multi-tier dispositor root chain.",
                    penalty=30.0
                )
            ]
            detected.append(YogaInstance(
                id="parvata_yoga_self_dispositor",
                name="Parvata Yoga (Self-Dispositor Variant)",
                category=YogaCategory.DISPOSITOR_ROOT,
                status=YogaStatus.STAINED,
                plausibility_score=round(score, 1),
                participating_planets=[lagna_lord],
                participating_houses=[ll_house],
                scripture_ref="Phaladeepika 6.36 & Vic DiCara Lecture 1",
                archetype="Self-Hosted Mountain: Ascendant Lord sits in its own sign in an angle, providing strong self-reliance (~70% weight).",
                manifestation_effects=[
                    "High personal autonomy, dignified bearing, and reliable self-generated fortune.",
                    "Represents strong single-tier self-anchoring rather than multi-generational dispositor tree depth."
                ],
                positive_factors=[
                    f"Ascendant Lord ({lagna_lord}) resides in House {ll_house} in its own sign ({ll_sign})."
                ],
                breakers=breakers
            ))
        else:
            # Multi-tier Authentic Parvata Yoga: External dispositor chain
            disp_house = planet_houses.get(ll_dispositor, 0)
            disp_sign = get_sign_of_planet(chart, ll_dispositor)
            disp_is_exalted = (disp_sign == EXALTATION_SIGNS.get(ll_dispositor))
            disp_is_own = (disp_sign in OWN_SIGNS.get(ll_dispositor, []))
            disp_in_kt = disp_house in KENDRA_TRIKONA_HOUSES

            if (disp_is_exalted or disp_is_own) and disp_in_kt:
                score = 95.0
                breakers = []
                breakers.extend(audit_combustion([lagna_lord, ll_dispositor], chart))
                for b in breakers:
                    score -= b.penalty
                score = max(35.0, score)
                status = YogaStatus.PURE if score >= 75.0 else YogaStatus.STAINED

                detected.append(YogaInstance(
                    id="parvata_yoga_authentic",
                    name="Parvata Yoga (Authentic Multi-Tier Root)",
                    category=YogaCategory.DISPOSITOR_ROOT,
                    status=status,
                    plausibility_score=round(score, 1),
                    participating_planets=[lagna_lord, ll_dispositor],
                    participating_houses=[ll_house, disp_house],
                    scripture_ref="Phaladeepika 6.36 & Vic DiCara Lecture 1",
                    archetype="The Mountain of Enduring Nobility: Both Lagna Lord and its host dispositor blaze in high dignity in Kendras/Trikoṇas, guaranteeing permanent status.",
                    manifestation_effects=[
                        "Unshakeable societal stature, illustrious renown, and generational prosperity.",
                        "Enduring moral character; like a mountain, cannot be shaken by passing political or social storms."
                    ],
                    positive_factors=[
                        f"Ascendant Lord ({lagna_lord}) is {'exalted' if ll_is_exalted else 'in own sign'} in supportive House {ll_house} ({ll_sign}).",
                        f"Host dispositor ({ll_dispositor}) is {'exalted' if disp_is_exalted else 'in own sign'} in supportive House {disp_house} ({disp_sign})."
                    ],
                    breakers=breakers
                ))

    return detected
