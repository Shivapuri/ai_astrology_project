"""
jyotish/yogas/deity_yogas.py
Cosmic Deity Yogas (Trimūrti: Śrīkaṇṭha, Viriñci, Śrīnātha; Tridevī: Gaurī, Sarasvatī; Mālā: Śubhamālā, Aśubhamālā).
Scripture: Phaladeepika 6.24–31, 6.38.
"""

from typing import List, Dict, Any, Tuple
from jyotish.yogas.models import (
    YogaInstance, YogaCategory, YogaStatus, YogaBreakerDetail
)
from jyotish.yogas.breakers import (
    get_house_of_planet, get_sign_of_planet, get_house_rulers, get_planets_data,
    get_lagna_sign, audit_trishadaya_interference, audit_combustion, audit_dusthana_placement,
    SIGN_LORDS, OWN_SIGNS, EXALTATION_SIGNS
)
from jyotish.relationships.relationships import get_natural_relationship

KENDRA_TRIKONA_HOUSES = (1, 4, 5, 7, 9, 10)
BENEFICS = ("Jupiter", "Venus", "Mercury")
MALEFICS = ("Sun", "Mars", "Saturn", "Rahu", "Ketu")


def _is_in_dignity_or_friend(chart: Dict[str, Any], planet: str) -> Tuple[bool, str]:
    """Checks if a planet is in exaltation, own sign, or friendly sign."""
    p_sign = get_sign_of_planet(chart, planet)
    if not p_sign:
        return False, "Unknown sign"

    if p_sign == EXALTATION_SIGNS.get(planet):
        return True, f"Exalted in {p_sign}"
    if p_sign in OWN_SIGNS.get(planet, []):
        return True, f"In own sign {p_sign}"

    host = SIGN_LORDS.get(p_sign)
    if host and get_natural_relationship(planet, host) == "Friend":
        return True, f"In friendly sign {p_sign} (ruled by {host})"

    return False, f"In neutral/inimical sign {p_sign}"


def detect_deity_yogas(chart: Dict[str, Any]) -> List[YogaInstance]:
    """Scans chart for Trimūrti, Tridevī, and Mālā deity yogas."""
    detected: List[YogaInstance] = []
    lagna_sign = get_lagna_sign(chart)
    planets_data = get_planets_data(chart)
    house_rulers = get_house_rulers(chart)

    if not lagna_sign or not planets_data:
        return detected

    planet_houses = {p: get_house_of_planet(chart, p) for p in planets_data}

    # =========================================================================
    # 1. TRIMŪRTI YOGAS (Phaladeepika 6.28–31)
    # =========================================================================

    # 1A. Śrīkaṇṭha Yoga (Lord Śiva — 1st House Anchor)
    # 1st Lord + Sun + Moon in Kendras/Trikoṇas in own/exalted/friendly signs.
    lord_1 = house_rulers.get(1, [None])[0]
    if lord_1 and lord_1 in planets_data:
        trio_shiva = [lord_1, "Sun", "Moon"]
        shiva_valid = True
        shiva_details = []
        shiva_houses = []
        for p in trio_shiva:
            h = planet_houses.get(p, 0)
            shiva_houses.append(h)
            is_kt = h in KENDRA_TRIKONA_HOUSES
            is_dig, dig_reason = _is_in_dignity_or_friend(chart, p)
            if not (is_kt and is_dig):
                shiva_valid = False
                break
            shiva_details.append(f"{p} in House {h} ({dig_reason})")

        if shiva_valid:
            score = 90.0
            breakers = audit_combustion(["Moon", lord_1], chart)
            for b in breakers:
                score -= b.penalty
            score = max(35.0, score)
            status = YogaStatus.PURE if score >= 75.0 else YogaStatus.STAINED

            detected.append(YogaInstance(
                id="srikantha_yoga",
                name="Śrīkaṇṭha Yoga (Lord Śiva)",
                category=YogaCategory.DEITY,
                status=status,
                plausibility_score=round(score, 1),
                participating_planets=list(set(trio_shiva)),
                participating_houses=shiva_houses,
                scripture_ref="Phaladeepika 6.28–29",
                archetype="The Cosmic Ascetic: 1st Lord, Sun, and Moon blaze in dignified angular/trinal seats, conferring radiant aura and unwavering integrity.",
                manifestation_effects=[
                    "Devoted to universal welfare, moral truth, and spiritual transcendence.",
                    "Endows fearless commanding presence, revered character, and immunity to petty corruptions."
                ],
                positive_factors=shiva_details,
                breakers=breakers
            ))

    # 1B. Viriñci Yoga (Lord Brahmā — 5th House Anchor)
    # 5th Lord + Jupiter + Saturn in Kendras/Trikoṇas in own/exalted/friendly signs.
    lord_5 = house_rulers.get(5, [None])[0]
    if lord_5 and lord_5 in planets_data:
        trio_brahma = [lord_5, "Jupiter", "Saturn"]
        brahma_valid = True
        brahma_details = []
        brahma_houses = []
        for p in trio_brahma:
            h = planet_houses.get(p, 0)
            brahma_houses.append(h)
            is_kt = h in KENDRA_TRIKONA_HOUSES
            is_dig, dig_reason = _is_in_dignity_or_friend(chart, p)
            if not (is_kt and is_dig):
                brahma_valid = False
                break
            brahma_details.append(f"{p} in House {h} ({dig_reason})")

        if brahma_valid:
            score = 90.0
            breakers = audit_combustion(["Jupiter", "Saturn", lord_5], chart)
            for b in breakers:
                score -= b.penalty
            score = max(35.0, score)
            status = YogaStatus.PURE if score >= 75.0 else YogaStatus.STAINED

            detected.append(YogaInstance(
                id="virinci_yoga",
                name="Viriñci Yoga (Lord Brahmā)",
                category=YogaCategory.DEITY,
                status=status,
                plausibility_score=round(score, 1),
                participating_planets=list(set(trio_brahma)),
                participating_houses=brahma_houses,
                scripture_ref="Phaladeepika 6.30–31",
                archetype="The Master of Knowledge: 5th Lord, Jupiter, and Saturn dignified in Kendras/Trikoṇas, bestowing profound intellect and cosmic insight.",
                manifestation_effects=[
                    "Master of Vedic lore, deep contemplative philosophy, and intellectual creation.",
                    "Fertile mind, respected educator, renowned counselor, and long, fulfilling lifespan."
                ],
                positive_factors=brahma_details,
                breakers=breakers
            ))

    # 1C. Śrīnātha Yoga (Lord Viṣṇu — 9th House Anchor)
    # 9th Lord + Venus + Mercury in Kendras/Trikoṇas in own/exalted/friendly signs.
    lord_9 = house_rulers.get(9, [None])[0]
    if lord_9 and lord_9 in planets_data:
        trio_vishnu = [lord_9, "Venus", "Mercury"]
        vishnu_valid = True
        vishnu_details = []
        vishnu_houses = []
        for p in trio_vishnu:
            h = planet_houses.get(p, 0)
            vishnu_houses.append(h)
            is_kt = h in KENDRA_TRIKONA_HOUSES
            is_dig, dig_reason = _is_in_dignity_or_friend(chart, p)
            if not (is_kt and is_dig):
                vishnu_valid = False
                break
            vishnu_details.append(f"{p} in House {h} ({dig_reason})")

        if vishnu_valid:
            score = 90.0
            breakers = audit_combustion(["Venus", "Mercury", lord_9], chart)
            for b in breakers:
                score -= b.penalty
            score = max(35.0, score)
            status = YogaStatus.PURE if score >= 75.0 else YogaStatus.STAINED

            detected.append(YogaInstance(
                id="srinatha_yoga",
                name="Śrīnātha Yoga (Lord Viṣṇu)",
                category=YogaCategory.DEITY,
                status=status,
                plausibility_score=round(score, 1),
                participating_planets=list(set(trio_vishnu)),
                participating_houses=vishnu_houses,
                scripture_ref="Phaladeepika 6.30–31",
                archetype="The Radiant Preserver: 9th Lord, Venus, and Mercury dignified in Kendras/Trikoṇas, granting grace, wealth, and elegance.",
                manifestation_effects=[
                    "Blessed by the lord of preservation; splendid wealth, magnetic beauty, and sweet eloquence.",
                    "Commands devotion and affection from everyone; enjoys enduring comfort and righteous progeny."
                ],
                positive_factors=vishnu_details,
                breakers=breakers
            ))

    # =========================================================================
    # 2. TRIDEVĪ YOGAS (Gaurī & Sarasvatī — Phaladeepika 6.24, 6.26–27)
    # =========================================================================

    # 2A. Gaurī Yoga (Śiva's Consort — Phaladeepika 6.24)
    # Moon in own sign (Cancer) or exaltation (Taurus) in Kendra or Trikoṇa (1, 4, 5, 7, 9, 10).
    moon_sign = get_sign_of_planet(chart, "Moon")
    moon_h = planet_houses.get("Moon", 0)
    if moon_h in KENDRA_TRIKONA_HOUSES and moon_sign in ("Cancer", "Taurus"):
        is_exalted_m = (moon_sign == "Taurus")
        score = 88.0
        breakers = audit_combustion(["Moon"], chart)
        for b in breakers:
            score -= b.penalty
        score = max(30.0, score)
        status = YogaStatus.PURE if score >= 75.0 else YogaStatus.STAINED

        detected.append(YogaInstance(
            id="gauri_yoga",
            name="Gaurī Yoga (Goddess of Grace)",
            category=YogaCategory.DEITY,
            status=status,
            plausibility_score=round(score, 1),
            participating_planets=["Moon"],
            participating_houses=[moon_h],
            scripture_ref="Phaladeepika 6.24",
            archetype="The Queen of Radiant Grace: Moon occupies own sign or exaltation in an angular/trinal house, purifying the emotional core.",
            manifestation_effects=[
                "Charming personality, luminous reputation, praise from leaders, and serene domestic bliss.",
                "Pure conduct, high cultural refinement, and magnetic public appeal."
            ],
            positive_factors=[
                f"Moon is {'exalted in Taurus' if is_exalted_m else 'in own sign Cancer'} in supportive House {moon_h}."
            ],
            breakers=breakers
        ))

    # 2B. Sarasvatī Yoga (Goddess of Wisdom — Phaladeepika 6.26–27)
    # Mercury, Jupiter, and Venus in Kendras, Trikoṇas, or 2nd house (1, 2, 4, 5, 7, 9, 10),
    # with Jupiter dignified in own, exaltation, or friendly sign.
    sar_houses = (1, 2, 4, 5, 7, 9, 10)
    mer_h = planet_houses.get("Mercury", 0)
    jup_h = planet_houses.get("Jupiter", 0)
    ven_h = planet_houses.get("Venus", 0)

    if mer_h in sar_houses and jup_h in sar_houses and ven_h in sar_houses:
        jup_dig, jup_reason = _is_in_dignity_or_friend(chart, "Jupiter")
        if jup_dig:
            score = 90.0
            breakers = audit_combustion(["Mercury", "Venus", "Jupiter"], chart)
            for b in breakers:
                score -= b.penalty
            score = max(35.0, score)
            status = YogaStatus.PURE if score >= 75.0 else YogaStatus.STAINED

            detected.append(YogaInstance(
                id="sarasvati_yoga",
                name="Sarasvatī Yoga (Goddess of Learning)",
                category=YogaCategory.DEITY,
                status=status,
                plausibility_score=round(score, 1),
                participating_planets=["Mercury", "Jupiter", "Venus"],
                participating_houses=[mer_h, jup_h, ven_h],
                scripture_ref="Phaladeepika 6.26–27",
                archetype="The Fountain of Genius: Mercury, Jupiter, and Venus occupy supportive intellectual seats with a fortified Guru, creating peerless scholarship.",
                manifestation_effects=[
                    "Peerless mastery in literature, poetry, mathematics, rhetoric, and profound fine arts.",
                    "Famed for brilliant erudition, highly revered by academics and dignitaries alike."
                ],
                positive_factors=[
                    f"Mercury (H{mer_h}), Jupiter (H{jup_h}), and Venus (H{ven_h}) all occupy auspicious seats (Kendras, Trikoṇas, or 2nd).",
                    f"Jupiter is fortified: {jup_reason}."
                ],
                breakers=breakers
            ))

    # =========================================================================
    # 3. THE 2 MĀLĀ (STRAND) YOGAS (Phaladeepika 6.38)
    # =========================================================================

    # 3A. Śubhamālā Yoga (Garland of Blessings)
    # All natural benefics (Jupiter, Venus, Mercury) occupy houses 5, 6, and 7.
    ben_in_567 = [p for p in BENEFICS if planet_houses.get(p, 0) in (5, 6, 7)]
    if len(ben_in_567) == 3:
        score = 85.0
        breakers = audit_combustion(ben_in_567, chart)
        for b in breakers:
            score -= b.penalty
        score = max(30.0, score)
        status = YogaStatus.PURE if score >= 75.0 else YogaStatus.STAINED

        detected.append(YogaInstance(
            id="subhamala_yoga",
            name="Śubhamālā Yoga (Garland of Blessings)",
            category=YogaCategory.DEITY,
            status=status,
            plausibility_score=round(score, 1),
            participating_planets=ben_in_567,
            participating_houses=[planet_houses[p] for p in ben_in_567],
            scripture_ref="Phaladeepika 6.38",
            archetype="The Protective Garland: All natural benefics span houses 5, 6, and 7, forming a protective barrier of virtue, health, and diplomacy.",
            manifestation_effects=[
                "Unbroken series of worldly comforts, affectionate domestic life, and diplomatic victory over rivals.",
                "Command over resources and lifelong protection against sudden adversity."
            ],
            positive_factors=[
                f"Natural benefics ({', '.join(ben_in_567)}) occupy houses 5, 6, and 7."
            ],
            breakers=breakers
        ))

    # 3B. Aśubhamālā Yoga (Garland of Entanglement)
    # Natural benefics trapped in Dusthanas (6, 8, 12), while malefics occupy Kendras (1, 4, 7, 10).
    ben_in_dusthana = [p for p in BENEFICS if planet_houses.get(p, 0) in (6, 8, 12)]
    mal_in_kendra = [p for p in MALEFICS if planet_houses.get(p, 0) in (1, 4, 7, 10)]

    if len(ben_in_dusthana) >= 2 and len(mal_in_kendra) >= 2:
        score = 75.0
        detected.append(YogaInstance(
            id="asubhamala_yoga",
            name="Aśubhamālā Yoga (Submerged Talents)",
            category=YogaCategory.DEITY,
            status=YogaStatus.STAINED,
            plausibility_score=score,
            participating_planets=ben_in_dusthana + mal_in_kendra,
            participating_houses=[planet_houses[p] for p in ben_in_dusthana + mal_in_kendra],
            scripture_ref="Phaladeepika 6.38",
            archetype="Submerged Talents: Natural benefics are trapped in struggle houses (6, 8, 12) while natural malefics dominate public angles.",
            manifestation_effects=[
                "High personal potential and intellectual gifts struggle for external appreciation and fair compensation.",
                "Requires hard discipline and perseverance to overcome feeling blocked by worldly bureaucracy."
            ],
            positive_factors=[],
            breakers=[
                YogaBreakerDetail(
                    factor="Benefic Submersion / Malefic Angles",
                    culprit_planet=", ".join(ben_in_dusthana),
                    description=f"Benefics ({', '.join(ben_in_dusthana)}) trapped in Dusthanas while malefics ({', '.join(mal_in_kendra)}) occupy public Kendras.",
                    penalty=25.0
                )
            ]
        ))

    return detected
