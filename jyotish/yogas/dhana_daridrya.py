"""
jyotish/yogas/dhana_daridrya.py
Dhana (Wealth) and Daridrya (Poverty/Depletion) Yogas.
Scripture: BPHS Ch. 41 (Vishesha Dhana Yoga), Ch. 42 (Daridrya Yoga), Phaladeepika Ch. 6.
"""

from typing import List, Dict, Any, Tuple, Set
from jyotish.yogas.models import (
    YogaInstance, YogaCategory, YogaStatus, YogaBreakerDetail
)
from jyotish.yogas.breakers import (
    get_lagna_sign, get_house_of_planet, get_sign_of_planet, get_house_rulers,
    get_planets_data, get_aspect_score, _first_ruler,
    audit_trishadaya_interference, audit_combustion, audit_dispositor_vitality,
    audit_dusthana_placement, audit_shadbala_muscle, audit_neecha_bhanga,
    resolve_yoga_score_and_status,
    EXALTATION_SIGNS, OWN_SIGNS, DEBILITATION_SIGNS, SIGN_LORDS,
    ASPECT_PALPABLE_THRESHOLD, ASPECT_MARGINAL_THRESHOLD
)

DHANA_HOUSES = (1, 2, 5, 9, 11)
KENDRA_TRIKONA_HOUSES = (1, 4, 5, 7, 9, 10)
DUSTHANA_HOUSES = (6, 8, 12)
BENEFICS = ("Jupiter", "Venus", "Mercury")


def detect_dhana_and_daridrya_yogas(chart: Dict[str, Any]) -> List[YogaInstance]:
    """Scans chart for wealth (Dhana) and poverty/depletion (Daridrya) yogas."""
    detected: List[YogaInstance] = []
    lagna_sign = get_lagna_sign(chart)
    planets_data = get_planets_data(chart)
    if not lagna_sign or not planets_data:
        return detected

    house_rulers = get_house_rulers(chart)
    lord_1 = _first_ruler(house_rulers, 1)
    lord_2 = _first_ruler(house_rulers, 2)
    lord_5 = _first_ruler(house_rulers, 5)
    lord_9 = _first_ruler(house_rulers, 9)
    lord_11 = _first_ruler(house_rulers, 11)

    # -------------------------------------------------------------
    # 1. LAKṢMĪ YOGA (9th Lord + Venus fortified in Kendras/Trikoṇas + Lagneśa check)
    # -------------------------------------------------------------
    if lord_9 and lord_9 in planets_data and "Venus" in planets_data:
        l9_house = get_house_of_planet(chart, lord_9)
        l9_sign = get_sign_of_planet(chart, lord_9)
        v_house = get_house_of_planet(chart, "Venus")
        v_sign = get_sign_of_planet(chart, "Venus")

        is_l9_strong = (
            l9_house in KENDRA_TRIKONA_HOUSES and
            (l9_sign == EXALTATION_SIGNS.get(lord_9) or l9_sign in OWN_SIGNS.get(lord_9, []))
        )
        is_v_strong = (
            v_house in KENDRA_TRIKONA_HOUSES and
            (v_sign == EXALTATION_SIGNS.get("Venus") or v_sign in OWN_SIGNS.get("Venus", []))
        )

        if is_l9_strong and is_v_strong:
            score = 95.0
            participants = list(dict.fromkeys([lord_9, "Venus"]))
            houses_inv = list(dict.fromkeys([l9_house, v_house]))
            pos_factors = [
                f"9th Lord ({lord_9}) is fortified in House {l9_house} ({l9_sign}).",
                f"Venus is fortified in House {v_house} ({v_sign})."
            ]
            breakers: List[YogaBreakerDetail] = []

            # Phaladeepika 6.28 & BPHS 36.27-28: Check Ascendant Lord (Lagnesha) strength
            if lord_1 and lord_1 in planets_data:
                l1_house = get_house_of_planet(chart, lord_1)
                l1_sign = get_sign_of_planet(chart, lord_1)
                l1_dignified = (
                    l1_sign == EXALTATION_SIGNS.get(lord_1) or
                    l1_sign in OWN_SIGNS.get(lord_1, [])
                )
                l1_deb = (l1_sign == DEBILITATION_SIGNS.get(lord_1))
                l1_rescued = audit_neecha_bhanga(lord_1, chart)[0] if l1_deb else False

                if l1_dignified or l1_house in KENDRA_TRIKONA_HOUSES:
                    score += 3.0
                    pos_factors.append(f"Ascendant Lord ({lord_1}) supports from House {l1_house} ({l1_sign}).")
                elif (l1_deb and not l1_rescued) or (l1_house in DUSTHANA_HOUSES and not l1_dignified):
                    breakers.append(YogaBreakerDetail(
                        factor="Weakened Ascendant Lord (Lagneśa)",
                        culprit_planet=lord_1,
                        description=f"1st Lord ({lord_1}) is in House {l1_house} ({l1_sign}), reducing the vessel's capacity to hold Lakṣmī Yoga's full splendor.",
                        penalty=20.0
                    ))

            # Category 6 (DHANA) Layer 2 Breakers: NEVER penalize 11th lord!
            breakers.extend(audit_trishadaya_interference(participants, chart, exclude_houses=(11,)))
            breakers.extend(audit_combustion(participants, chart))
            breakers.extend(audit_dispositor_vitality(participants, chart))
            sb_brk, sb_pos = audit_shadbala_muscle(participants, chart)
            breakers.extend(sb_brk)
            pos_factors.extend(sb_pos)

            final_score, status = resolve_yoga_score_and_status(score, breakers)

            detected.append(YogaInstance(
                id="lakshmi_yoga",
                name="Lakṣmī Yoga",
                category=YogaCategory.DHANA,
                status=status,
                plausibility_score=final_score,
                participating_planets=participants,
                participating_houses=houses_inv,
                scripture_ref="Phaladeepika 6.24 & 6.28, BPHS 36.27-28",
                archetype="The Golden Grace: Bestows boundless wealth, aesthetic charm, virtuous livelihood, and noble character.",
                manifestation_effects=[
                    "Immense wealth, royal vehicles, widespread social goodwill, and ethical integrity.",
                    "Enjoyment of all life comforts without loss of moral principles."
                ],
                positive_factors=pos_factors,
                breakers=breakers
            ))

    # -------------------------------------------------------------
    # 2A. CORE MULTI-PLANET DHANA YOGAS (All 10 Classical BPHS Ch. 41 Pairs)
    # -------------------------------------------------------------
    dhana_pairs: List[Tuple[str, str, str, float]] = [
        (lord_2, lord_11, "Treasury (H2) & Profit (H11) Primary Wealth Alliance", 88.0),
        (lord_1, lord_2, "Self (H1) & Wealth (H2) Union", 85.0),
        (lord_1, lord_11, "Self (H1) & Gains (H11) Union", 85.0),
        (lord_5, lord_9, "Supreme Trinal Merit (H5 & H9) Fusion", 88.0),
        (lord_2, lord_5, "Treasury (H2) & Creative Merit (H5) Alliance", 86.0),
        (lord_2, lord_9, "Wealth (H2) & Divine Fortune (H9) Alliance", 88.0),
        (lord_5, lord_11, "Intellect (H5) & Large Gains (H11) Polarity", 86.0),
        (lord_9, lord_11, "Divine Fortune (H9) & Gains (H11) Alliance", 88.0),
        (lord_1, lord_5, "Self (H1) & Merit (H5) Wealth-Grace Union", 84.0),
        (lord_1, lord_9, "Self (H1) & Fortune (H9) Wealth-Grace Union", 85.0),
    ]

    evaluated_dhana: Set[Tuple[str, str]] = set()
    for p1, p2, desc, base_score in dhana_pairs:
        if not p1 or not p2 or p1 == p2 or p1 not in planets_data or p2 not in planets_data:
            continue
        key = tuple(sorted([p1, p2]))
        if key in evaluated_dhana:
            continue

        h1 = get_house_of_planet(chart, p1)
        h2 = get_house_of_planet(chart, p2)
        if h1 <= 0 or h2 <= 0:
            continue

        s1 = get_sign_of_planet(chart, p1)
        s2 = get_sign_of_planet(chart, p2)
        is_conj = (h1 == h2) or (bool(s1) and s1 == s2)
        is_exchange = (SIGN_LORDS.get(s1) == p2 and SIGN_LORDS.get(s2) == p1)

        aspect_val = max(get_aspect_score(chart, p1, p2), get_aspect_score(chart, p2, p1))
        is_aspect = (aspect_val >= ASPECT_PALPABLE_THRESHOLD)
        is_marginal_aspect = (not is_conj) and (not is_exchange) and (not is_aspect) and (aspect_val >= ASPECT_MARGINAL_THRESHOLD)

        if not (is_conj or is_exchange or is_aspect or is_marginal_aspect):
            continue

        evaluated_dhana.add(key)
        score = base_score
        pos: List[str] = []
        breakers: List[YogaBreakerDetail] = []

        if is_conj:
            pos.append(f"{desc}: {p1} and {p2} unite in House {h1} ({s1}).")
        elif is_exchange:
            pos.append(f"{desc}: {p1} (H{h1}) and {p2} (H{h2}) exchange signs (Parivartana).")
            score += 4.0
        else:
            pos.append(f"{desc}: {p1} and {p2} connect via aspect ({aspect_val:.0f} Virūpas).")

        # Dignity bonus / unredeemed debility check
        for dp in (p1, p2):
            dp_sign = get_sign_of_planet(chart, dp)
            if dp_sign == EXALTATION_SIGNS.get(dp) or dp_sign in OWN_SIGNS.get(dp, []):
                score += 4.0
                pos.append(f"{dp} is fortified in dignity in {dp_sign}.")
            elif dp_sign == DEBILITATION_SIGNS.get(dp):
                is_rescued, nb_reasons, _ = audit_neecha_bhanga(dp, chart)
                if is_rescued:
                    pos.extend(nb_reasons)
                else:
                    breakers.append(YogaBreakerDetail(
                        factor="Unredeemed Debilitation",
                        culprit_planet=dp,
                        description=f"Wealth lord {dp} is debilitated in {dp_sign} without cancellation.",
                        penalty=25.0
                    ))

        if is_marginal_aspect:
            breakers.append(YogaBreakerDetail(
                factor="Marginal Aspect Connection",
                culprit_planet=f"{p1}/{p2}",
                description=f"Aspect strength ({aspect_val:.0f} Virūpas) is below the palpable 45.0 Virūpa threshold.",
                penalty=25.0
            ))

        houses_inv = list(dict.fromkeys([h1, h2]))
        dust_brk = audit_dusthana_placement(houses_inv, YogaCategory.DHANA.value)
        if dust_brk is not None:
            breakers.append(dust_brk)

        # Category 6 (DHANA) Layer 2 Breakers: NEVER penalize the 11th lord!
        breakers.extend(audit_trishadaya_interference([p1, p2], chart, exclude_houses=(11,)))
        breakers.extend(audit_combustion([p1, p2], chart))
        if not is_exchange:
            breakers.extend(audit_dispositor_vitality([p1, p2], chart))
        sb_brk, sb_pos = audit_shadbala_muscle([p1, p2], chart)
        breakers.extend(sb_brk)
        pos.extend(sb_pos)

        final_score, status = resolve_yoga_score_and_status(score, breakers)

        detected.append(YogaInstance(
            id=f"dhana_yoga_{p1.lower()}_{p2.lower()}",
            name=f"Dhana Yoga ({p1} + {p2})",
            category=YogaCategory.DHANA,
            status=status,
            plausibility_score=final_score,
            participating_planets=[p1, p2],
            participating_houses=houses_inv,
            scripture_ref="BPHS 41.1-15",
            archetype="Resource Flow: Systematic connection between wealth, earnings, intellect, and fortune.",
            manifestation_effects=[
                "Substantial capacity to generate, retain, and expand financial assets.",
                "High earnings during the conjoined or operational Daśā periods."
            ],
            positive_factors=pos,
            breakers=breakers
        ))

    # -------------------------------------------------------------
    # 2B. SINGLE-PLANET MULTI-DHANA LORDSHIP (BPHS 41.2–12)
    # (e.g., Taurus Mercury H2+H5, Leo Mercury H2+H11, Virgo Venus H2+H9,
    #  Scorpio Jupiter H2+H5, Aquarius Jupiter H2+H11, Pisces Mars H2+H9)
    # -------------------------------------------------------------
    planet_dhana_houses: Dict[str, List[int]] = {}
    for dh in (2, 5, 9, 11):
        ruler = _first_ruler(house_rulers, dh)
        if ruler:
            planet_dhana_houses.setdefault(ruler, []).append(dh)

    for p_dhana, owned_dh in planet_dhana_houses.items():
        if len(owned_dh) >= 2 and (2 in owned_dh or 11 in owned_dh) and p_dhana in planets_data:
            p_h = get_house_of_planet(chart, p_dhana)
            p_s = get_sign_of_planet(chart, p_dhana)
            is_dignified = (p_s == EXALTATION_SIGNS.get(p_dhana) or p_s in OWN_SIGNS.get(p_dhana, []))
            is_deb = (p_s == DEBILITATION_SIGNS.get(p_dhana))

            if p_h in (1, 2, 4, 5, 7, 9, 10, 11) and not is_deb:
                score = 86.0 + (6.0 if is_dignified else 0.0)
                owned_str = " & ".join(f"H{h}" for h in owned_dh)
                pos = [
                    f"Single-Planet Dual Dhana Kāraka: {p_dhana} simultaneously rules wealth houses {owned_str} for {lagna_sign} Lagna and occupies House {p_h} ({p_s})."
                ]
                if is_dignified:
                    pos.append(f"{p_dhana} is fortified in dignity in {p_s}.")

                breakers = []
                breakers.extend(audit_trishadaya_interference([p_dhana], chart, exclude_houses=(11,)))
                breakers.extend(audit_combustion([p_dhana], chart))
                breakers.extend(audit_dispositor_vitality([p_dhana], chart))
                sb_brk, sb_pos = audit_shadbala_muscle([p_dhana], chart)
                breakers.extend(sb_brk)
                pos.extend(sb_pos)

                final_score, status = resolve_yoga_score_and_status(score, breakers)

                detected.append(YogaInstance(
                    id=f"single_dhana_yoga_{p_dhana.lower()}",
                    name=f"Viśeṣa Dhana Kāraka Yoga ({p_dhana} — Rules {owned_str})",
                    category=YogaCategory.DHANA,
                    status=status,
                    plausibility_score=final_score,
                    participating_planets=[p_dhana],
                    participating_houses=list(dict.fromkeys([p_h] + owned_dh)),
                    scripture_ref="BPHS 41.2-12",
                    archetype=f"Unified Wealth Conduit: {p_dhana} unites the lordships of {owned_str} within a single planet in House {p_h}.",
                    manifestation_effects=[
                        f"Direct, self-contained wealth generation during {p_dhana}'s operational periods.",
                        "Links liquid savings with investment or career gains without requiring an external partner."
                    ],
                    positive_factors=pos,
                    breakers=breakers
                ))

    # -------------------------------------------------------------
    # 3. DĀRIDRYA YOGAS (POVERTY & LEAKAGE - BPHS Ch. 42)
    # Affliction Status Invariant (YOGA_ARCHITECTURE.md Row 7):
    # - NEVER call audit_dusthana_placement (already a Dusthana affliction yoga!)
    # - Use YogaStatus.STAINED when unmitigated, YogaStatus.RESCUED when mitigated — NEVER PURE!
    # -------------------------------------------------------------
    for p_lord, h_num in [(lord_2, 2), (lord_11, 11)]:
        if not p_lord or p_lord not in planets_data:
            continue
        h_pos = get_house_of_planet(chart, p_lord)
        if h_pos in DUSTHANA_HOUSES:
            sign_pos = get_sign_of_planet(chart, p_lord)
            is_exalted = (sign_pos == EXALTATION_SIGNS.get(p_lord))
            is_own = (sign_pos in OWN_SIGNS.get(p_lord, []))
            is_deb = (sign_pos == DEBILITATION_SIGNS.get(p_lord))
            is_nb_rescued = audit_neecha_bhanga(p_lord, chart)[0] if is_deb else False

            benefic_aspects = [
                bp for bp in BENEFICS
                if bp != p_lord and get_aspect_score(chart, bp, p_lord) >= ASPECT_PALPABLE_THRESHOLD
            ]

            is_mitigated = bool(is_exalted or is_own or is_nb_rescued or benefic_aspects)
            pos_factors: List[str] = []
            if is_exalted or is_own:
                pos_factors.append(
                    f"Dāridrya Bhaṅga (Dignity Rescue): {p_lord} occupies {'exalted' if is_exalted else 'own'} sign ({sign_pos}) in House {h_pos}, protecting assets from depletion."
                )
            if is_nb_rescued:
                pos_factors.append(
                    f"Dāridrya Bhaṅga (Nīcabhaṅga): Debility of {p_lord} in House {h_pos} is cancelled."
                )
            if benefic_aspects:
                pos_factors.append(
                    f"Dāridrya Bhaṅga (Śubha Dṛṣṭi): {p_lord} receives palpable benefic aspect from {', '.join(benefic_aspects)}."
                )

            if is_mitigated:
                status = YogaStatus.RESCUED
                score = 52.0
                penalty_val = 15.0
            else:
                status = YogaStatus.STAINED
                score = 72.0 if is_deb else 62.0
                penalty_val = 30.0

            detected.append(YogaInstance(
                id=f"daridrya_h{h_num}_{p_lord.lower()}",
                name=f"Dāridrya Yoga (H{h_num} Lord {p_lord} in H{h_pos})" + (" (Mitigated)" if is_mitigated else ""),
                category=YogaCategory.DARIDRYA,
                status=status,
                plausibility_score=score,
                participating_planets=[p_lord],
                participating_houses=[h_pos],
                scripture_ref="BPHS 42.1-5",
                archetype="Financial Leakage: Ruler of earnings or treasury sits in a Dusthana of loss, debt, or crisis.",
                manifestation_effects=[
                    "Tendency for wealth to leak into sudden expenses, medical bills, legal battles, or bad debts."
                    if not is_mitigated else
                    "Initial financial volatility or high overhead in House " + str(h_pos) + " is cushioned and stabilized by planetary dignity/benefic support.",
                    "Requires strict conscious budgeting and avoiding speculative gambles."
                ],
                positive_factors=pos_factors,
                breakers=[YogaBreakerDetail(
                    factor=f"Lord of H{h_num} in Dusthana H{h_pos}",
                    culprit_planet=p_lord,
                    description=f"{p_lord} (ruler of House {h_num}) is relegated to House {h_pos}, causing financial drains.",
                    penalty=penalty_val
                )]
            ))

    return detected
