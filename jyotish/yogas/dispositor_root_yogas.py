"""
jyotish/yogas/dispositor_root_yogas.py
Dispositor Root Yogas: Kāhala Yoga (Variants A & B), Parvata Yoga (Authentic, Self-Dispositor & BPHS),
and Puṣkala Yoga.
Scripture: Phaladeepika 6.18, 6.33–36, BPHS Ch. 36.
"""

from typing import List, Dict, Any
from jyotish.yogas.models import (
    YogaInstance, YogaCategory, YogaStatus, YogaBreakerDetail
)
from jyotish.yogas.breakers import (
    get_house_of_planet, get_sign_of_planet, get_house_rulers, get_planets_data,
    get_lagna_sign, get_aspect_score, _first_ruler,
    audit_trishadaya_interference, audit_combustion, audit_dusthana_placement,
    audit_dispositor_vitality, audit_shadbala_muscle, resolve_yoga_score_and_status,
    audit_neecha_bhanga,
    SIGN_LORDS, OWN_SIGNS, EXALTATION_SIGNS, DEBILITATION_SIGNS, ZODIAC_SIGNS,
    ASPECT_PALPABLE_THRESHOLD, ASPECT_MARGINAL_THRESHOLD
)
from jyotish.relationships.relationships import (
    get_natural_relationship, get_temporary_relationship, get_compound_relationship
)

KENDRA_TRIKONA_HOUSES = (1, 4, 5, 7, 9, 10)
KENDRA_HOUSES = (1, 4, 7, 10)
BENEFICS = ("Jupiter", "Venus", "Mercury")
MALEFICS = ("Sun", "Mars", "Saturn", "Rahu", "Ketu")


def detect_puskala_yoga(chart: Dict[str, Any]) -> List[YogaInstance]:
    """
    Detects Puṣkala Yoga (Phaladeepika 6.18):
    1. Lord of Moon sign (Candra-rāśīśa) and Lord of Ascendant (Lagneśa) conjoin in a Kendra
       in a friendly (or own/exalted) sign.
    2. A strong/auspicious planet palpably aspects the Ascendant (>= 45.0 Virūpas).
    3. The Ascendant is occupied or fortified by a strong/auspicious planet.
    """
    detected: List[YogaInstance] = []
    lagna_sign = get_lagna_sign(chart)
    planets_data = get_planets_data(chart)
    if not lagna_sign or not planets_data:
        return detected

    house_rulers = get_house_rulers(chart)
    lagna_lord = _first_ruler(house_rulers, 1)
    moon_sign = get_sign_of_planet(chart, "Moon")
    moon_lord = SIGN_LORDS.get(moon_sign)

    if not lagna_lord or not moon_lord or lagna_lord not in planets_data or moon_lord not in planets_data:
        return detected

    planet_houses = {p: get_house_of_planet(chart, p) for p in planets_data}
    ll_house = planet_houses.get(lagna_lord, 0)
    ml_house = planet_houses.get(moon_lord, 0)
    moon_house = planet_houses.get("Moon", 0)

    # Guard against single-planet self-conjunction tautology when lagna_lord == moon_lord
    # (unless the Moon itself is conjoined with lagna_lord in that Kendra)
    if lagna_lord == moon_lord and moon_house != ll_house:
        return detected

    if ll_house != ml_house or ll_house not in KENDRA_HOUSES:
        return detected

    shared_sign = get_sign_of_planet(chart, lagna_lord)
    sign_host = SIGN_LORDS.get(shared_sign)
    if not shared_sign or not sign_host:
        return detected

    # Reject if either lord is debilitated in shared_sign without Neecha Bhanga
    for lord_p in dict.fromkeys([lagna_lord, moon_lord]):
        if shared_sign == DEBILITATION_SIGNS.get(lord_p):
            is_rescued, _, _ = audit_neecha_bhanga(lord_p, chart)
            if not is_rescued:
                return detected

    # Check if shared_sign is a friendly, own, or exaltation sign
    is_friendly_host = False
    if (
        sign_host in (lagna_lord, moon_lord)
        or shared_sign == EXALTATION_SIGNS.get(lagna_lord)
        or shared_sign == EXALTATION_SIGNS.get(moon_lord)
    ):
        is_friendly_host = True
    else:
        host_actual_sign = get_sign_of_planet(chart, sign_host)
        nat_rel_ll = get_natural_relationship(lagna_lord, sign_host)
        nat_rel_ml = get_natural_relationship(moon_lord, sign_host)
        if shared_sign in ZODIAC_SIGNS and host_actual_sign in ZODIAC_SIGNS:
            ll_idx = ZODIAC_SIGNS.index(shared_sign)
            host_idx = ZODIAC_SIGNS.index(host_actual_sign)
            temp_rel = get_temporary_relationship(ll_idx, host_idx)
            comp_ll = get_compound_relationship(nat_rel_ll, temp_rel)
            comp_ml = get_compound_relationship(nat_rel_ml, temp_rel)
            is_friendly_host = (
                comp_ll in ("Friend", "Great Friend")
                or comp_ml in ("Friend", "Great Friend")
                or nat_rel_ll == "Friend"
                or nat_rel_ml == "Friend"
            )
        else:
            is_friendly_host = (nat_rel_ll == "Friend" or nat_rel_ml == "Friend")

    if not is_friendly_host:
        return detected

    # Pillar 2: Check aspect on Lagna (palpable >= 45.0 Virūpas from a strong planet, or marginal >= 30.0)
    palpable_aspectors: List[str] = []
    marginal_aspectors: List[str] = []
    for p in planets_data:
        if p in ("Rahu", "Ketu"):
            continue
        asp = get_aspect_score(chart, p, "Lagna")
        if asp >= ASPECT_PALPABLE_THRESHOLD:
            palpable_aspectors.append(p)
        elif asp >= ASPECT_MARGINAL_THRESHOLD:
            marginal_aspectors.append(p)

    # Pillar 3: Check if Lagna (House 1) is occupied by a strong/benefic planet
    h1_occupants = [
        p for p, h in planet_houses.items()
        if h == 1 and (
            p in BENEFICS
            or p in (lagna_lord, moon_lord)
            or get_sign_of_planet(chart, p) == EXALTATION_SIGNS.get(p)
            or get_sign_of_planet(chart, p) in OWN_SIGNS.get(p, [])
        )
    ]

    score = 85.0
    yoga_planets = list(dict.fromkeys(
        [lagna_lord, moon_lord] + (["Moon"] if lagna_lord == moon_lord else [])
    ))
    pos_factors = [
        f"Ascendant Lord ({lagna_lord}) and Moon Dispositor ({moon_lord}) unite in Kendra House {ll_house} ({shared_sign}).",
        f"Hosted favorably in {shared_sign} (ruled by {sign_host})."
    ]
    breakers: List[YogaBreakerDetail] = []

    if palpable_aspectors:
        score += 5.0
        pos_factors.append(
            f"Ascendant receives a palpable aspect (>= 45 Virūpas) from {', '.join(palpable_aspectors)}."
        )
    elif marginal_aspectors:
        breakers.append(YogaBreakerDetail(
            factor="Marginal Aspect on Lagna",
            culprit_planet="Lagna",
            description=f"Ascendant receives only a marginal aspect (30–44.9 Virūpas) from {', '.join(marginal_aspectors)}.",
            penalty=10.0
        ))
    else:
        breakers.append(YogaBreakerDetail(
            factor="Missing Palpable Aspect on Lagna",
            culprit_planet="Lagna",
            description="The Ascendant does not receive a palpable aspect from a strong planet.",
            penalty=15.0
        ))

    if h1_occupants:
        score += 5.0
        pos_factors.append(
            f"Ascendant (House 1) is directly fortified by {', '.join(h1_occupants)}."
        )

    # Layer 2 Breakers (Category 12: DISPOSITOR_ROOT)
    dust_brk = audit_dusthana_placement([ll_house], YogaCategory.DISPOSITOR_ROOT.value)
    if dust_brk:
        breakers.append(dust_brk)
    breakers.extend(audit_trishadaya_interference(yoga_planets, chart))
    breakers.extend(audit_combustion(yoga_planets, chart))
    breakers.extend(audit_dispositor_vitality(yoga_planets, chart))
    shadbala_brk, shadbala_pos = audit_shadbala_muscle(yoga_planets, chart)
    breakers.extend(shadbala_brk)
    pos_factors.extend(shadbala_pos)

    final_score, status = resolve_yoga_score_and_status(score, breakers)

    detected.append(YogaInstance(
        id="puskala_yoga",
        name="Puṣkala Yoga",
        category=YogaCategory.DISPOSITOR_ROOT,
        status=status,
        plausibility_score=final_score,
        participating_planets=yoga_planets,
        participating_houses=list(dict.fromkeys([ll_house, 1])),
        scripture_ref="Phaladeepika 6.18",
        archetype="Abundant Splendor: Ascendant Lord and Moon Dispositor combine in an auspicious angular seat, bestowing magnetic prestige and wealth.",
        manifestation_effects=[
            "Overflowing material wealth, sweet and persuasive speech, and high social renown.",
            "Honored by government or corporate superiors; broad civic influence."
        ],
        positive_factors=pos_factors,
        breakers=breakers
    ))
    return detected


def detect_dispositor_root_yogas(chart: Dict[str, Any]) -> List[YogaInstance]:
    """Scans chart for Parvata, Kāhala, and Puṣkala dispositor-root yogas."""
    detected: List[YogaInstance] = []
    lagna_sign = get_lagna_sign(chart)
    planets_data = get_planets_data(chart)
    house_rulers = get_house_rulers(chart)

    if not lagna_sign or not planets_data:
        return detected

    lagna_lord = _first_ruler(house_rulers, 1)
    if not lagna_lord or lagna_lord not in planets_data:
        return detected

    planet_houses = {p: get_house_of_planet(chart, p) for p in planets_data}
    ll_house = planet_houses.get(lagna_lord, 0)
    ll_sign = get_sign_of_planet(chart, lagna_lord)
    ll_dispositor = SIGN_LORDS.get(ll_sign)

    ll_is_exalted = (ll_sign == EXALTATION_SIGNS.get(lagna_lord))
    ll_is_own = (ll_sign in OWN_SIGNS.get(lagna_lord, []))
    ll_in_kt = ll_house in KENDRA_TRIKONA_HOUSES

    # =========================================================================
    # 1. PARVATA YOGA (Mountainous / Enduring Nobility — Phaladeepika 6.36 & BPHS 36.11–12)
    # =========================================================================
    authentic_parvata_formed = False

    if (ll_is_exalted or ll_is_own) and ll_in_kt and ll_dispositor:
        is_self_dispositor = (ll_dispositor == lagna_lord)

        if is_self_dispositor:
            # Self-Dispositor Variant: 1st lord in own sign in Kendra/Trikona (e.g. H1)
            # Pre-breaker base 100.0 minus 30.0 Single-Tier Loophole penalty = 70.0 net (STAINED) when unafflicted.
            pre_score = 100.0
            breakers_self: List[YogaBreakerDetail] = [
                YogaBreakerDetail(
                    factor="Single-Tier Self-Dispositor Loophole",
                    culprit_planet=lagna_lord,
                    description=f"{lagna_lord} hosts itself in House {ll_house}. Lacks an external multi-tier dispositor root chain.",
                    penalty=30.0
                )
            ]
            breakers_self.extend(audit_trishadaya_interference([lagna_lord], chart))
            breakers_self.extend(audit_combustion([lagna_lord], chart))
            shadbala_brk_s, shadbala_pos_s = audit_shadbala_muscle([lagna_lord], chart)
            breakers_self.extend(shadbala_brk_s)

            final_score_s, status_s = resolve_yoga_score_and_status(pre_score, breakers_self)
            pos_factors_s = [
                f"Ascendant Lord ({lagna_lord}) resides in House {ll_house} in its own sign ({ll_sign})."
            ] + shadbala_pos_s

            detected.append(YogaInstance(
                id="parvata_yoga_self_dispositor",
                name="Parvata Yoga (Self-Dispositor Variant)",
                category=YogaCategory.DISPOSITOR_ROOT,
                status=status_s,
                plausibility_score=final_score_s,
                participating_planets=[lagna_lord],
                participating_houses=[ll_house],
                scripture_ref="Phaladeepika 6.36 & Vic DiCara Lecture 1",
                archetype="Self-Hosted Mountain: Ascendant Lord sits in its own sign in an angle, providing strong self-reliance (~70% weight).",
                manifestation_effects=[
                    "High personal autonomy, dignified bearing, and reliable self-generated fortune.",
                    "Represents strong single-tier self-anchoring rather than multi-generational dispositor tree depth."
                ],
                positive_factors=pos_factors_s,
                breakers=breakers_self
            ))
        elif ll_dispositor in planets_data:
            # Multi-tier Authentic Parvata Yoga: External dispositor chain
            disp_house = planet_houses.get(ll_dispositor, 0)
            disp_sign = get_sign_of_planet(chart, ll_dispositor)
            disp_is_exalted = (disp_sign == EXALTATION_SIGNS.get(ll_dispositor))
            disp_is_own = (disp_sign in OWN_SIGNS.get(ll_dispositor, []))
            disp_in_kt = disp_house in KENDRA_TRIKONA_HOUSES

            if (disp_is_exalted or disp_is_own) and disp_in_kt:
                authentic_parvata_formed = True
                score_p = 95.0
                yoga_planets_p = [lagna_lord, ll_dispositor]
                yoga_houses_p = list(dict.fromkeys([ll_house, disp_house]))

                breakers_p: List[YogaBreakerDetail] = []
                dust_brk_p = audit_dusthana_placement(yoga_houses_p, YogaCategory.DISPOSITOR_ROOT.value)
                if dust_brk_p:
                    breakers_p.append(dust_brk_p)
                breakers_p.extend(audit_trishadaya_interference(yoga_planets_p, chart))
                breakers_p.extend(audit_combustion(yoga_planets_p, chart))
                breakers_p.extend(audit_dispositor_vitality(yoga_planets_p, chart))
                shadbala_brk_p, shadbala_pos_p = audit_shadbala_muscle(yoga_planets_p, chart)
                breakers_p.extend(shadbala_brk_p)

                final_score_p, status_p = resolve_yoga_score_and_status(score_p, breakers_p)
                pos_factors_p = [
                    f"Ascendant Lord ({lagna_lord}) is {'exalted' if ll_is_exalted else 'in own sign'} in supportive House {ll_house} ({ll_sign}).",
                    f"Host dispositor ({ll_dispositor}) is {'exalted' if disp_is_exalted else 'in own sign'} in supportive House {disp_house} ({disp_sign})."
                ] + shadbala_pos_p

                detected.append(YogaInstance(
                    id="parvata_yoga_authentic",
                    name="Parvata Yoga (Authentic Multi-Tier Root)",
                    category=YogaCategory.DISPOSITOR_ROOT,
                    status=status_p,
                    plausibility_score=final_score_p,
                    participating_planets=yoga_planets_p,
                    participating_houses=yoga_houses_p,
                    scripture_ref="Phaladeepika 6.36 & Vic DiCara Lecture 1",
                    archetype="The Mountain of Enduring Nobility: Both Lagna Lord and its host dispositor blaze in high dignity in Kendras/Trikoṇas, guaranteeing permanent status.",
                    manifestation_effects=[
                        "Unshakeable societal stature, illustrious renown, and generational prosperity.",
                        "Enduring moral character; like a mountain, cannot be shaken by passing political or social storms."
                    ],
                    positive_factors=pos_factors_p,
                    breakers=breakers_p
                ))

    # BPHS Parvata Variant (BPHS 36.11–12): Benefics in Kendras, with H6 and H8 empty or occupied only by benefics
    kendra_benefics = [p for p in BENEFICS if planet_houses.get(p, 0) in KENDRA_HOUSES]
    h6_8_malefics = [p for p in MALEFICS if planet_houses.get(p, 0) in (6, 8)]
    h6_8_all = [p for p, h in planet_houses.items() if h in (6, 8)]
    if len(kendra_benefics) >= 2 and not h6_8_malefics and not authentic_parvata_formed:
        score_bp = 85.0
        kb_houses = list(dict.fromkeys([planet_houses[p] for p in kendra_benefics]))
        breakers_bp: List[YogaBreakerDetail] = []
        breakers_bp.extend(audit_trishadaya_interference(kendra_benefics, chart))
        breakers_bp.extend(audit_combustion(kendra_benefics, chart))
        breakers_bp.extend(audit_dispositor_vitality(kendra_benefics, chart))
        shadbala_brk_bp, shadbala_pos_bp = audit_shadbala_muscle(kendra_benefics, chart)
        breakers_bp.extend(shadbala_brk_bp)

        final_score_bp, status_bp = resolve_yoga_score_and_status(score_bp, breakers_bp)
        h6_8_desc = (
            "Houses 6 and 8 are completely unoccupied."
            if not h6_8_all
            else f"Houses 6 and 8 contain only natural benefics ({', '.join(h6_8_all)}) with zero malefics."
        )
        detected.append(YogaInstance(
            id="parvata_yoga_bphs",
            name="Parvata Yoga (BPHS Kendra-Benefic Variant)",
            category=YogaCategory.DISPOSITOR_ROOT,
            status=status_bp,
            plausibility_score=final_score_bp,
            participating_planets=kendra_benefics,
            participating_houses=kb_houses,
            scripture_ref="BPHS 36.11-12",
            archetype="The Sanctuary Mountain: Natural benefics fortify the Kendras while Houses 6 and 8 remain pure of malefic agitation.",
            manifestation_effects=[
                "Enduring civic peace, charitable leadership, and lasting material prosperity.",
                "Protected from chronic enmity or sudden structural collapse."
            ],
            positive_factors=[
                f"Natural benefics ({', '.join(kendra_benefics)}) occupy Kendra houses ({', '.join(str(h) for h in kb_houses)}).",
                h6_8_desc
            ] + shadbala_pos_bp,
            breakers=breakers_bp
        ))

    # =========================================================================
    # 2. KĀHALA YOGA (Dual Scriptural Traditions — Phaladeepika 6.35 & BPHS 36)
    # =========================================================================

    # Variant A: 4th & 10th lords (or 4th & 9th / Jupiter per BPHS) in mutual Kendras
    # Strictly requires two distinct planets (p1 != p2) to prevent Dual-Lagna self-Kendra tautology!
    lord_4 = _first_ruler(house_rulers, 4)
    lord_9 = _first_ruler(house_rulers, 9)
    lord_10 = _first_ruler(house_rulers, 10)

    kahala_a_candidates = [
        (lord_4, lord_10, "4th Lord", "10th Lord"),
        (lord_4, lord_9, "4th Lord", "9th Lord"),
        (lord_4, "Jupiter", "4th Lord", "Jupiter"),
    ]

    for p1, p2, label1, label2 in kahala_a_candidates:
        if not p1 or not p2 or p1 == p2 or p1 not in planets_data or p2 not in planets_data:
            continue
        h1_pos = planet_houses.get(p1, 0)
        h2_pos = planet_houses.get(p2, 0)
        if h1_pos <= 0 or h2_pos <= 0:
            continue

        diff_pos = ((h2_pos - h1_pos) % 12) + 1
        if diff_pos in KENDRA_HOUSES:
            score_a = 85.0
            if ll_is_exalted or ll_is_own:
                score_a += 5.0

            yoga_planets_a = list(dict.fromkeys([p1, p2, lagna_lord]))
            yoga_houses_a = list(dict.fromkeys([h1_pos, h2_pos, ll_house]))

            breakers_a: List[YogaBreakerDetail] = []
            if ll_house in (6, 8, 12):
                breakers_a.append(YogaBreakerDetail(
                    factor="Lagnesha in Dusthana",
                    culprit_planet=lagna_lord,
                    description=f"Ascendant Lord ({lagna_lord}) sits in Dusthana House {ll_house}, weakening the foundational root of the {label1}/{label2} alliance.",
                    penalty=25.0
                ))

            dust_brk_a = audit_dusthana_placement([h1_pos, h2_pos], YogaCategory.DISPOSITOR_ROOT.value)
            if dust_brk_a:
                breakers_a.append(dust_brk_a)
            breakers_a.extend(audit_trishadaya_interference([p1, p2], chart))
            breakers_a.extend(audit_combustion(yoga_planets_a, chart))
            breakers_a.extend(audit_dispositor_vitality([p1, p2], chart))
            shadbala_brk_a, shadbala_pos_a = audit_shadbala_muscle(yoga_planets_a, chart)
            breakers_a.extend(shadbala_brk_a)

            final_score_a, status_a = resolve_yoga_score_and_status(score_a, breakers_a)
            pos_factors_a = [
                f"{label1} ({p1} in H{h1_pos}) and {label2} ({p2} in H{h2_pos}) occupy mutual Kendra ({diff_pos}th from each other).",
                f"Ascendant Lord is {lagna_lord} in House {ll_house}."
            ] + shadbala_pos_a

            detected.append(YogaInstance(
                id="kahala_yoga_variant_a",
                name="Kāhala Yoga (Variant A: Mutual Kendra Alliance)",
                category=YogaCategory.DISPOSITOR_ROOT,
                status=status_a,
                plausibility_score=final_score_a,
                participating_planets=yoga_planets_a,
                participating_houses=yoga_houses_a,
                scripture_ref="Phaladeepika 6.35 & BPHS Ch. 36 (Tradition A)",
                archetype=f"The Resounding Drum: {label1} and {label2} occupy mutual angles, generating dynamic organizational rhythm.",
                manifestation_effects=[
                    "Dynamic executive stamina, unwavering resolve, and organizational leadership.",
                    "Ability to lead teams and mobilize resources toward prominent civic or corporate success."
                ],
                positive_factors=pos_factors_a,
                breakers=breakers_a
            ))
            break

    # Variant B: Dispositor Root Chain (Phaladeepika 6.35)
    # 1. Requires external dispositor (ll_dispositor != lagna_lord)
    # 2. Avoids redundant double-emission when Authentic Parvata is already formed
    # 3. Supports both 1-step (1L -> disp1) and 2-step (1L -> disp1 -> disp2) dispositor roots
    if ll_dispositor and ll_dispositor != lagna_lord and ll_dispositor in planets_data and not authentic_parvata_formed:
        disp_house = planet_houses.get(ll_dispositor, 0)
        disp_sign = get_sign_of_planet(chart, ll_dispositor)
        disp_is_exalted = (disp_sign == EXALTATION_SIGNS.get(ll_dispositor))
        disp_is_own = (disp_sign in OWN_SIGNS.get(ll_dispositor, []))
        disp_in_kt = disp_house in KENDRA_TRIKONA_HOUSES

        root_planet = None
        root_house = 0
        root_sign = ""
        root_is_exalted = False
        yoga_planets_b: List[str] = []
        yoga_houses_b: List[int] = []
        chain_desc = ""

        if (disp_is_exalted or disp_is_own) and disp_in_kt:
            root_planet = ll_dispositor
            root_house = disp_house
            root_sign = disp_sign
            root_is_exalted = disp_is_exalted
            yoga_planets_b = list(dict.fromkeys([lagna_lord, ll_dispositor]))
            yoga_houses_b = list(dict.fromkeys([ll_house, disp_house]))
            chain_desc = f"Ascendant Lord ({lagna_lord}) hosted in {ll_sign} by {ll_dispositor}."
        else:
            # Check 2-step root: Dispositor of the 1st Lord's dispositor (1L -> disp1 -> disp2)
            disp2 = SIGN_LORDS.get(disp_sign)
            if disp2 and disp2 not in (lagna_lord, ll_dispositor) and disp2 in planets_data:
                disp2_house = planet_houses.get(disp2, 0)
                disp2_sign = get_sign_of_planet(chart, disp2)
                disp2_is_exalted = (disp2_sign == EXALTATION_SIGNS.get(disp2))
                disp2_is_own = (disp2_sign in OWN_SIGNS.get(disp2, []))
                disp2_in_kt = disp2_house in KENDRA_TRIKONA_HOUSES
                if (disp2_is_exalted or disp2_is_own) and disp2_in_kt:
                    root_planet = disp2
                    root_house = disp2_house
                    root_sign = disp2_sign
                    root_is_exalted = disp2_is_exalted
                    yoga_planets_b = list(dict.fromkeys([lagna_lord, ll_dispositor, disp2]))
                    yoga_houses_b = list(dict.fromkeys([ll_house, disp_house, disp2_house]))
                    chain_desc = (
                        f"Two-step dispositor chain: Ascendant Lord ({lagna_lord} in {ll_sign}) -> "
                        f"Dispositor ({ll_dispositor} in {disp_sign}) -> Root Dispositor ({disp2})."
                    )

        if root_planet:
            score_b = 90.0
            breakers_b: List[YogaBreakerDetail] = []
            dust_brk_b = audit_dusthana_placement(yoga_houses_b, YogaCategory.DISPOSITOR_ROOT.value)
            if dust_brk_b:
                breakers_b.append(dust_brk_b)
            breakers_b.extend(audit_trishadaya_interference(yoga_planets_b, chart))
            breakers_b.extend(audit_combustion(yoga_planets_b, chart))
            breakers_b.extend(audit_dispositor_vitality([lagna_lord], chart))
            shadbala_brk_b, shadbala_pos_b = audit_shadbala_muscle(yoga_planets_b, chart)
            breakers_b.extend(shadbala_brk_b)

            final_score_b, status_b = resolve_yoga_score_and_status(score_b, breakers_b)
            pos_factors_b = [
                chain_desc,
                f"Root dispositor ({root_planet}) is {'exalted' if root_is_exalted else 'in own sign'} in supportive House {root_house} ({root_sign})."
            ] + shadbala_pos_b

            detected.append(YogaInstance(
                id="kahala_yoga_variant_b",
                name="Kāhala Yoga (Variant B: Dispositor Root Chain)",
                category=YogaCategory.DISPOSITOR_ROOT,
                status=status_b,
                plausibility_score=final_score_b,
                participating_planets=yoga_planets_b,
                participating_houses=yoga_houses_b,
                scripture_ref="Phaladeepika 6.35 (Tradition B & Vic DiCara Lecture 1)",
                archetype="Strong Dispositor Roots: The root dispositor of the Ascendant Lord blazes with dignity in an angle or trine, infusing the personality with unshakeable fortitude.",
                manifestation_effects=[
                    "Deep inner confidence, steady growth (Vṛddhi), optimism (Prasanna), and unyielding courage.",
                    "The native stands firm against setbacks because their underlying dispositor root is deeply anchored."
                ],
                positive_factors=pos_factors_b,
                breakers=breakers_b
            ))

    # =========================================================================
    # 3. PUṢKALA YOGA (Abundant Splendor — Phaladeepika 6.18)
    # =========================================================================
    detected.extend(detect_puskala_yoga(chart))

    return detected
