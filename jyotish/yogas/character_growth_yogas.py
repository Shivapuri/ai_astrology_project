"""
jyotish/yogas/character_growth_yogas.py
Character & Growth Yogas (Gaja Kesarī, Śakaṭa, Vasumatī, Amalā).
Scripture: Phaladeepika Ch. 6.13–17, BPHS Ch. 36–37.
"""

from typing import List, Dict, Any
from jyotish.yogas.models import (
    YogaInstance, YogaCategory, YogaStatus, YogaBreakerDetail
)
from jyotish.yogas.breakers import (
    get_house_of_planet, get_sign_of_planet, get_planets_data, get_lagna_sign,
    audit_trishadaya_interference, audit_combustion, audit_dusthana_placement,
    audit_dispositor_vitality, audit_shadbala_muscle, audit_neecha_bhanga,
    resolve_yoga_score_and_status,
    OWN_SIGNS, EXALTATION_SIGNS, DEBILITATION_SIGNS
)

BENEFICS = ("Jupiter", "Venus", "Mercury")
MAJOR_BENEFICS = ("Jupiter", "Venus")
MALEFICS = ("Sun", "Mars", "Saturn", "Rahu", "Ketu")
UPACHAYA_HOUSES = (3, 6, 10, 11)
KENDRA_HOUSES = (1, 4, 7, 10)


def detect_character_and_growth_yogas(chart: Dict[str, Any]) -> List[YogaInstance]:
    """Scans chart for Gaja Kesarī, Śakaṭa, Vasumatī, and Amalā Yogas."""
    detected: List[YogaInstance] = []
    lagna_sign = get_lagna_sign(chart)
    planets_data = get_planets_data(chart)
    if not lagna_sign or not planets_data:
        return detected

    planet_houses = {p: get_house_of_planet(chart, p) for p in planets_data}
    moon_house = planet_houses.get("Moon", 0)
    jup_house = planet_houses.get("Jupiter", 0)

    # =========================================================================
    # 1. GAJA KESARĪ YOGA (The Lion & Elephant Majesty — Phaladeepika 6.13 / 6.17)
    # =========================================================================
    # Jupiter in a Kendra (1, 4, 7, 10) from the Moon.
    if moon_house > 0 and jup_house > 0:
        jup_from_moon = ((jup_house - moon_house) % 12) + 1
        if jup_from_moon in KENDRA_HOUSES:
            score_gk = 82.0
            pos_factors_gk = [
                f"Jupiter (H{jup_house}) occupies Kendra position ({jup_from_moon}th house) from the Moon (H{moon_house})."
            ]
            breakers_gk: List[YogaBreakerDetail] = []

            # Lagna Kendra confluence bonus
            if jup_house in KENDRA_HOUSES and moon_house in KENDRA_HOUSES:
                score_gk += 8.0
                pos_factors_gk.append(
                    f"Both Jupiter (H{jup_house}) and Moon (H{moon_house}) also occupy Kendras from the Ascendant."
                )
            elif jup_house in KENDRA_HOUSES:
                score_gk += 5.0
                pos_factors_gk.append(f"Jupiter is additionally anchored in Lagna Kendra House {jup_house}.")

            # Planetary dignity check for Jupiter and Moon
            for gk_p in ("Jupiter", "Moon"):
                p_sign = get_sign_of_planet(chart, gk_p)
                if p_sign == EXALTATION_SIGNS.get(gk_p) or p_sign in OWN_SIGNS.get(gk_p, []):
                    score_gk += 5.0
                    pos_factors_gk.append(f"{gk_p} is fortified in dignity in {p_sign}.")
                elif p_sign == DEBILITATION_SIGNS.get(gk_p):
                    is_rescued, _, _ = audit_neecha_bhanga(gk_p, chart)
                    if not is_rescued:
                        breakers_gk.append(YogaBreakerDetail(
                            factor="Unrescued Planetary Debilitation",
                            culprit_planet=gk_p,
                            description=f"{gk_p} is debilitated in {p_sign} without Neecha Bhanga, dampening Gaja Kesarī majesty.",
                            penalty=25.0
                        ))

            gk_houses = list(dict.fromkeys([moon_house, jup_house]))
            dust_brk_gk = audit_dusthana_placement(gk_houses, YogaCategory.CHARACTER.value)
            if dust_brk_gk:
                breakers_gk.append(dust_brk_gk)
            breakers_gk.extend(audit_trishadaya_interference(["Moon", "Jupiter"], chart))
            breakers_gk.extend(audit_combustion(["Jupiter"], chart))
            breakers_gk.extend(audit_dispositor_vitality(["Moon", "Jupiter"], chart))
            shadbala_brk_gk, shadbala_pos_gk = audit_shadbala_muscle(["Moon", "Jupiter"], chart)
            breakers_gk.extend(shadbala_brk_gk)
            pos_factors_gk.extend(shadbala_pos_gk)

            final_score_gk, status_gk = resolve_yoga_score_and_status(score_gk, breakers_gk)

            detected.append(YogaInstance(
                id="gaja_kesari_yoga",
                name="Gaja Kesarī Yoga",
                category=YogaCategory.CHARACTER,
                status=status_gk,
                plausibility_score=final_score_gk,
                participating_planets=["Moon", "Jupiter"],
                participating_houses=gk_houses,
                scripture_ref="Phaladeepika 6.13 & 6.17",
                archetype="Lion-Like Majesty: Jupiter in an angle from the Moon fuses wisdom with emotional intelligence, conferring lasting reputation.",
                manifestation_effects=[
                    "Formidable personal dignity, sharp intellect, and self-reliant authority.",
                    "Enduring reputation, noble alliances, and victory over opposition like a lion before elephants."
                ],
                positive_factors=pos_factors_gk,
                breakers=breakers_gk
            ))

    # =========================================================================
    # 2. ŚAKAṬA YOGA (The Heavy Cart & Setbacks — Phaladeepika 6.13 / 6.14)
    # =========================================================================
    # Moon in 6th, 8th, or 12th from Jupiter.
    # Cancellation (Śakaṭa Bhaṅga): Moon in Kendra from Lagna, Jupiter in Kendra from Lagna,
    # or Moon in own/exalted sign.
    if moon_house > 0 and jup_house > 0:
        rel_from_jup = ((moon_house - jup_house) % 12) + 1
        if rel_from_jup in (6, 8, 12):
            moon_in_lagna_kendra = moon_house in KENDRA_HOUSES
            jup_in_lagna_kendra = jup_house in KENDRA_HOUSES
            moon_sign_cur = get_sign_of_planet(chart, "Moon")
            moon_dignified = (
                moon_sign_cur == EXALTATION_SIGNS.get("Moon")
                or moon_sign_cur in OWN_SIGNS.get("Moon", [])
            )

            if moon_in_lagna_kendra or jup_in_lagna_kendra or moon_dignified:
                rescue_reasons = []
                if moon_in_lagna_kendra:
                    rescue_reasons.append(
                        f"Moon in Kendra House {moon_house} from Lagna completely rescues the {rel_from_jup}th-house dusthana tension from Jupiter."
                    )
                if jup_in_lagna_kendra:
                    rescue_reasons.append(
                        f"Jupiter in Kendra House {jup_house} from Lagna provides angular protection (Śakaṭa Bhaṅga)."
                    )
                if moon_dignified:
                    rescue_reasons.append(
                        f"Moon is fortified in {moon_sign_cur}, stabilizing lunar fortunes against oscillation."
                    )
                rescued_score = 72.0 if moon_in_lagna_kendra else 68.0

                detected.append(YogaInstance(
                    id="sakata_yoga_rescued",
                    name="Śakaṭa Yoga (Rescued / Bhaṅga)",
                    category=YogaCategory.CHARACTER,
                    status=YogaStatus.RESCUED,
                    plausibility_score=rescued_score,
                    participating_planets=["Moon", "Jupiter"],
                    participating_houses=list(dict.fromkeys([moon_house, jup_house])),
                    scripture_ref="Phaladeepika 6.14",
                    archetype="Neutralized Cart Friction: Moon sits in a dusthana from Jupiter but is anchored by Lagna Kendra/dignity, averting chronic loss.",
                    manifestation_effects=[
                        "Initial fluctuations between sudden success and temporary setbacks resolve into steady worldly balance.",
                        "Angular/dignified protection preserves reputation and maintains overall career stability."
                    ],
                    positive_factors=rescue_reasons,
                    breakers=[]
                ))
            else:
                breakers_sk = [
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
                    participating_houses=list(dict.fromkeys([moon_house, jup_house])),
                    scripture_ref="Phaladeepika 6.14",
                    archetype="The Rolling Cart: Fortunes oscillate like a heavy cartwheel; periods of progress alternate with exhausting setbacks.",
                    manifestation_effects=[
                        "Cycles of rapid financial/professional gain followed by unexpected downturns or fatigue.",
                        "Feels like pulling a heavy cart alone; requires emotional resilience and steadfast perseverance."
                    ],
                    positive_factors=[
                        f"Moon in House {moon_house}, Jupiter in House {jup_house} ({rel_from_jup}th axis)."
                    ],
                    breakers=breakers_sk
                ))

    # =========================================================================
    # 3. VASUMATĪ YOGA (Immense Self-Generating Wealth — Phaladeepika 6.15 / 6.16)
    # =========================================================================
    # Natural benefics (Jupiter, Venus, Mercury) in Upachayas (3, 6, 10, 11)
    # from Lagna OR from Moon. Requires at least 2 benefics (never a single isolated benefic!).
    benefics_in_upachaya_lagna = [
        p for p in BENEFICS
        if planet_houses.get(p, 0) in UPACHAYA_HOUSES
    ]

    benefics_in_upachaya_moon = []
    if moon_house > 0:
        benefics_in_upachaya_moon = [
            p for p in BENEFICS
            if planet_houses.get(p, 0) > 0
            and ((planet_houses[p] - moon_house) % 12 + 1) in UPACHAYA_HOUSES
        ]

    count_lagna = len(benefics_in_upachaya_lagna)
    count_moon = len(benefics_in_upachaya_moon)

    if count_lagna >= 2 or count_moon >= 2:
        is_dual_upachaya = (count_lagna >= 2 and count_moon >= 2)

        if count_lagna >= count_moon:
            best_count = count_lagna
            best_planets = benefics_in_upachaya_lagna
            base_ref = "Ascendant (Lagna)"
            rel_house_desc = ", ".join(f"{p} in H{planet_houses[p]}" for p in best_planets)
        else:
            best_count = count_moon
            best_planets = benefics_in_upachaya_moon
            base_ref = "Moon (Chandra)"
            rel_house_desc = ", ".join(
                f"{p} in H{planet_houses[p]} ({((planet_houses[p] - moon_house) % 12) + 1}th from Moon)"
                for p in best_planets
            )

        houses_inv = list(dict.fromkeys([planet_houses[p] for p in best_planets]))

        if count_lagna == 3 and count_moon == 3:
            tier_name = "Uttama Dual-Reference (Supreme Riches)"
            score_v = 95.0
            effect_desc = "Grants inexhaustible, self-generating wealth anchored from both Ascendant and Moon; commands abundant independent assets."
        elif best_count == 3:
            tier_name = "Uttama (Peerless Riches)"
            score_v = 90.0 + (4.0 if is_dual_upachaya else 0.0)
            effect_desc = "Grants inexhaustible, self-generating wealth; the native commands abundant independent income without financial want."
        else:
            has_both_major = all(mb in best_planets for mb in MAJOR_BENEFICS)
            tier_name = "Madhyama (Substantial Wealth)"
            score_v = (82.0 if has_both_major else 76.0) + (4.0 if is_dual_upachaya else 0.0)
            effect_desc = "Grants strong financial stability, comfortable real assets (Vasu), and enduring commercial independence."

        pos_factors_v = [
            f"{best_count} natural benefics ({', '.join(best_planets)}) occupy Upachaya houses from {base_ref}: {rel_house_desc}."
        ]
        if is_dual_upachaya:
            pos_factors_v.append(
                f"Dual Upachaya alignment: {count_lagna} benefic(s) in Upachaya from Lagna and {count_moon} from Moon."
            )

        # Anti-Interference Rule (YOGA_ARCHITECTURE.md Row 13):
        # Exclude Upachaya houses (3, 6, 11) from Trishadaya penalties and NEVER penalize H6 in Vasumatī!
        breakers_v: List[YogaBreakerDetail] = []
        breakers_v.extend(audit_trishadaya_interference(best_planets, chart, exclude_houses=(3, 6, 11)))
        breakers_v.extend(audit_combustion(best_planets, chart))
        breakers_v.extend(audit_dispositor_vitality(best_planets, chart))
        shadbala_brk_v, shadbala_pos_v = audit_shadbala_muscle(best_planets, chart)
        breakers_v.extend(shadbala_brk_v)
        pos_factors_v.extend(shadbala_pos_v)

        final_score_v, status_v = resolve_yoga_score_and_status(score_v, breakers_v)

        detected.append(YogaInstance(
            id=f"vasumati_yoga_{best_count}",
            name=f"Vasumatī Yoga — {tier_name}",
            category=YogaCategory.CHARACTER,
            status=status_v,
            plausibility_score=final_score_v,
            participating_planets=best_planets,
            participating_houses=houses_inv,
            scripture_ref="Phaladeepika 6.16",
            archetype=f"Growth-House Fortification: {best_count} natural benefics occupy Upachayas from {base_ref}, driving steady accumulation of wealth.",
            manifestation_effects=[
                effect_desc,
                f"Continuous asset generation represented by {', '.join(best_planets)} in growth houses (Upachayas)."
            ],
            positive_factors=pos_factors_v,
            breakers=breakers_v
        ))

    # =========================================================================
    # 4. AMALĀ YOGA (The Spotless Reputation — Phaladeepika 6.15 / 6.17)
    # =========================================================================
    # Natural benefic(s) occupying the 10th house from Lagna OR Moon.
    h10_lagna = 10
    h10_moon = ((moon_house + 8) % 12) + 1 if moon_house > 0 else 0

    for base_name, target_h in [("Lagna", h10_lagna), ("Moon", h10_moon)]:
        if target_h <= 0:
            continue
        benefics_in_10 = [p for p in BENEFICS if planet_houses.get(p) == target_h]
        malefics_in_10 = [p for p in MALEFICS if planet_houses.get(p) == target_h]

        if benefics_in_10:
            score_am = 85.0
            pos_factors_am = [
                f"Natural benefic(s) ({', '.join(benefics_in_10)}) occupy the 10th house (House {target_h}) from {base_name}."
            ]
            if base_name == "Lagna" and h10_lagna == h10_moon:
                score_am += 5.0
                pos_factors_am.append("House 10 is simultaneously the 10th house from both Lagna and Moon.")

            breakers_am: List[YogaBreakerDetail] = []
            if malefics_in_10:
                breakers_am.append(YogaBreakerDetail(
                    factor="Malefic Corruption in 10th House",
                    culprit_planet=", ".join(malefics_in_10),
                    description=f"Natural malefic(s) ({', '.join(malefics_in_10)}) share the 10th house, tarnishing spotless public standing.",
                    penalty=35.0
                ))

            dust_brk_am = audit_dusthana_placement([target_h], YogaCategory.CHARACTER.value)
            if dust_brk_am:
                breakers_am.append(dust_brk_am)
            breakers_am.extend(audit_combustion(benefics_in_10, chart))
            breakers_am.extend(audit_dispositor_vitality(benefics_in_10, chart))
            shadbala_brk_am, shadbala_pos_am = audit_shadbala_muscle(benefics_in_10, chart)
            breakers_am.extend(shadbala_brk_am)
            pos_factors_am.extend(shadbala_pos_am)

            final_score_am, status_am = resolve_yoga_score_and_status(score_am, breakers_am)

            detected.append(YogaInstance(
                id=f"amala_yoga_{base_name.lower()}",
                name=f"Amalā Yoga (from {base_name})",
                category=YogaCategory.CHARACTER,
                status=status_am,
                plausibility_score=final_score_am,
                participating_planets=benefics_in_10,
                participating_houses=[target_h],
                scripture_ref="Phaladeepika 6.17",
                archetype=f"The Spotless Legacy: Benefic ({', '.join(benefics_in_10)}) in the 10th house from {base_name}, bestowing civic virtue and lasting honor.",
                manifestation_effects=[
                    "Spotless public reputation, respected career standing, and unblemished character.",
                    "Lasting societal honor, philanthropic achievements, and moral leadership."
                ],
                positive_factors=pos_factors_am,
                breakers=breakers_am
            ))
            if base_name == "Lagna" and h10_lagna == h10_moon:
                break

    return detected
