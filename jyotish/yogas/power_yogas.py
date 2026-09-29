"""
jyotish/yogas/power_yogas.py
Chapter 7 Kingly Power Yogas (Multi-Planet Kendras, Digbala Sovereignty, Specific Power Yogas).
Scripture: Phaladeepika Ch. 7, Verses 1–13.
"""

from typing import List, Dict, Any, Set
from jyotish.yogas.models import (
    YogaInstance, YogaCategory, YogaStatus, YogaBreakerDetail
)
from jyotish.yogas.breakers import (
    get_house_of_planet, get_sign_of_planet, get_house_rulers, get_planets_data,
    get_lagna_sign, get_aspect_score, audit_combustion,
    OWN_SIGNS, EXALTATION_SIGNS, DEBILITATION_SIGNS,
    ASPECT_PALPABLE_THRESHOLD, ASPECT_MARGINAL_THRESHOLD
)

DIGBALA_HOUSES = {
    "Sun": 10,
    "Mars": 10,
    "Jupiter": 1,
    "Mercury": 1,
    "Moon": 4,
    "Venus": 4,
    "Saturn": 7
}

FIRE_SIGNS = {"Aries", "Leo", "Sagittarius"}
KENDRA_HOUSES = (1, 4, 7, 10)


def _get_nakshatra_of_planet(chart: Dict[str, Any], planet: str) -> str:
    """Extracts nakshatra name for a given planet across different chart data shapes."""
    n1 = chart.get("nakshatras", {}).get("grahas", {}).get(planet, {}).get("nakshatra")
    if isinstance(n1, str) and n1:
        return n1
    n2 = chart.get("planetary_evaluation", {}).get("planets", {}).get(planet, {}).get("nakshatra")
    if isinstance(n2, dict):
        return n2.get("name", "")
    elif isinstance(n2, str) and n2:
        return n2
    grahas = get_planets_data(chart)
    n3 = grahas.get(planet, {}).get("nakshatra")
    if isinstance(n3, str) and n3:
        return n3
    return ""


def detect_chapter7_power_yogas(chart: Dict[str, Any]) -> List[YogaInstance]:
    """Scans chart for Chapter 7 Royal Power Yogas."""
    detected: List[YogaInstance] = []
    lagna_sign = get_lagna_sign(chart)
    planets_data = get_planets_data(chart)
    house_rulers = get_house_rulers(chart)

    if not lagna_sign or not planets_data:
        return detected

    planet_houses = {p: get_house_of_planet(chart, p) for p in planets_data}
    classical_planets = ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn")

    # =========================================================================
    # 1. MULTI-PLANET KENDRAS (Phaladeepika 7.2–3)
    # =========================================================================
    # 3 or more planets in Kendras (1, 4, 7, 10) in own sign or exaltation sign.
    dignified_kendra_planets = []
    for p in classical_planets:
        if p in planets_data:
            h = planet_houses.get(p, 0)
            if h in KENDRA_HOUSES:
                s = get_sign_of_planet(chart, p)
                if s == EXALTATION_SIGNS.get(p) or s in OWN_SIGNS.get(p, []):
                    dignified_kendra_planets.append(p)

    k_count = len(dignified_kendra_planets)
    if k_count >= 3:
        score = 95.0 if k_count >= 5 else 90.0
        detected.append(YogaInstance(
            id=f"multi_kendra_sovereignty_{k_count}",
            name=f"Multi-Planet Kendra Sovereignty ({k_count} Dignified Planets)",
            category=YogaCategory.POWER,
            status=YogaStatus.PURE,
            plausibility_score=score,
            participating_planets=dignified_kendra_planets,
            participating_houses=[planet_houses[p] for p in dignified_kendra_planets],
            scripture_ref="Phaladeepika 7.2–3",
            archetype=f"Royal Pillar Dominance: {k_count} planets occupy angular houses in own signs or exaltation, guaranteeing sovereign status.",
            manifestation_effects=[
                "Supreme worldly leadership, state honors, and command over large institutions.",
                "Even if born into modest circumstances, rises to eminent executive command."
            ],
            positive_factors=[
                f"{k_count} planets ({', '.join(dignified_kendra_planets)}) occupy Kendras in peak dignity (own/exaltation)."
            ],
            breakers=[]
        ))

    # =========================================================================
    # 2. DIRECTIONAL STRENGTH SOVEREIGNTY (Digbala — Phaladeepika 7.4–7)
    # =========================================================================
    # 2 to 3 planets with Digbala -> Royal status.
    # 4 to 5 planets (excluding Saturn) -> Supreme kingly command.
    digbala_planets = [
        p for p in classical_planets
        if p in planets_data and planet_houses.get(p, 0) == DIGBALA_HOUSES.get(p)
    ]
    dig_count = len(digbala_planets)
    if dig_count >= 2:
        is_supreme = (dig_count >= 4)
        score = 95.0 if is_supreme else 88.0
        detected.append(YogaInstance(
            id=f"digbala_sovereignty_{dig_count}",
            name=f"Digbala Sovereignty ({dig_count} Planets with Directional Force)",
            category=YogaCategory.POWER,
            status=YogaStatus.PURE,
            plausibility_score=score,
            participating_planets=digbala_planets,
            participating_houses=[planet_houses[p] for p in digbala_planets],
            scripture_ref="Phaladeepika 7.4–7",
            archetype=f"Directional Mastery: {dig_count} planets occupy their thrones of directional strength (Digbala), maximizing kinetic force.",
            manifestation_effects=[
                "Unstoppable vocational traction, decisive strategic command, and authoritative leadership.",
                "Commands high respect and easily overcomes opponents through structural alignment."
            ],
            positive_factors=[
                f"Planets achieving full Digbala: {', '.join(f'{p} in H{planet_houses[p]}' for p in digbala_planets)}."
            ],
            breakers=[]
        ))

    # =========================================================================
    # 3. SPECIFIC CHAPTER 7 POWER YOGAS (Phaladeepika 7.8–13)
    # =========================================================================

    # Power Yoga 1: Venus Rising in Aśvinī (Phaladeepika 7.8a)
    # Venus in 1st house in Aśvinī nakshatra, aspected by 3+ planets.
    ven_house = planet_houses.get("Venus", 0)
    if ven_house == 1:
        ven_nak = _get_nakshatra_of_planet(chart, "Venus")
        ven_sign = get_sign_of_planet(chart, "Venus")
        # In Tropical or Sidereal Aries (Aśvinī starts at 0° Aries)
        is_asvini = ("Ashwini" in ven_nak or "Aswini" in ven_nak or "Asvini" in ven_nak or (ven_sign == "Aries" and not ven_nak))
        if is_asvini:
            aspecting_planets = [
                p for p in classical_planets
                if p != "Venus" and get_aspect_score(chart, p, "Venus") >= ASPECT_MARGINAL_THRESHOLD
            ]
            if len(aspecting_planets) >= 3:
                detected.append(YogaInstance(
                    id="power_yoga_venus_asvini",
                    name="Aśvinī Venus Imperial Charm Yoga",
                    category=YogaCategory.POWER,
                    status=YogaStatus.PURE,
                    plausibility_score=92.0,
                    participating_planets=["Venus"] + aspecting_planets,
                    participating_houses=[1],
                    scripture_ref="Phaladeepika 7.8a",
                    archetype="Imperial Charismatic Sovereignty: Venus rising in Aśvinī aspected by 3+ planets, enchanting rivals into eager allies.",
                    manifestation_effects=[
                        "Irresistible public magnetism and charisma; turns political opponents into cooperative allies.",
                        "Commands popular movements, cultural loyalty, and effortless social elevation."
                    ],
                    positive_factors=[
                        f"Venus in Lagna in Aśvinī, aspected by {len(aspecting_planets)} planets ({', '.join(aspecting_planets)})."
                    ],
                    breakers=[]
                ))

    # Power Yoga 2: First Lord with Venus in the 2nd House (Phaladeepika 7.8b–9)
    # 1st Lord placed in 2nd house with Venus, neither debilitated.
    lord_1 = house_rulers.get(1, [None])[0]
    if lord_1 and lord_1 in planets_data and "Venus" in planets_data:
        l1_h = planet_houses.get(lord_1, 0)
        v_h = planet_houses.get("Venus", 0)
        if l1_h == 2 and v_h == 2:
            l1_s = get_sign_of_planet(chart, lord_1)
            v_s = get_sign_of_planet(chart, "Venus")
            if l1_s != DEBILITATION_SIGNS.get(lord_1) and v_s != DEBILITATION_SIGNS.get("Venus"):
                score = 88.0
                detected.append(YogaInstance(
                    id="power_yoga_l1_venus_h2",
                    name="Patriarchal Treasury Power Yoga (1st Lord + Venus in H2)",
                    category=YogaCategory.POWER,
                    status=YogaStatus.PURE,
                    plausibility_score=score,
                    participating_planets=list(set([lord_1, "Venus"])),
                    participating_houses=[2],
                    scripture_ref="Phaladeepika 7.8b–9",
                    archetype="The Economic Patriarch: Ascendant Lord combines with Venus in the 2nd House, creating an economic fortress and protective leader.",
                    manifestation_effects=[
                        "Vast commercial assets, profound financial stability, and patriarchal protection over dependants.",
                        "Guides family, business, or kingdom with steady nourishment and prosperous vision."
                    ],
                    positive_factors=[
                        f"1st Lord ({lord_1}) and Venus unite in House 2 in {l1_s}, free from debility."
                    ],
                    breakers=[]
                ))

    # Power Yoga 3: Mars in Fire Sign Aspected by a Friend (Phaladeepika 7.10)
    # Mars in Aries, Leo, or Sagittarius, receiving palpable aspect (>= 45 Virupas) from Sun, Moon, or Jupiter.
    mars_sign = get_sign_of_planet(chart, "Mars")
    mars_house = planet_houses.get("Mars", 0)
    if mars_sign in FIRE_SIGNS and mars_house > 0:
        friendly_aspects = []
        for fp in ("Sun", "Moon", "Jupiter"):
            asp_score = get_aspect_score(chart, fp, "Mars")
            if asp_score >= ASPECT_PALPABLE_THRESHOLD:
                friendly_aspects.append(f"{fp} ({asp_score:.0f} Virupas)")

        if friendly_aspects:
            detected.append(YogaInstance(
                id="power_yoga_mars_fire_friend",
                name="Martial Sovereignty (Mars in Fire Sign Aspected by Friend)",
                category=YogaCategory.POWER,
                status=YogaStatus.PURE,
                plausibility_score=90.0,
                participating_planets=["Mars"],
                participating_houses=[mars_house],
                scripture_ref="Phaladeepika 7.10",
                archetype="The Bold Commander: Mars blazes in a fire sign aspected by a friendly luminary/preceptor, conferring decisive executive power.",
                manifestation_effects=[
                    "Bold, fearless executive command; decisive courage in high-stakes crises.",
                    "Commands respect from subordinates; thrives in military, legal, athletic, or high-level strategic arenas."
                ],
                positive_factors=[
                    f"Mars in fire sign {mars_sign} (House {mars_house}) receives palpable aspect from: {', '.join(friendly_aspects)}."
                ],
                breakers=[]
            ))

    # Power Yoga 4: Exchange of 9th and 10th Lords (Phaladeepika 7.11)
    # Mutual reception between Dharma (H9) and Karma (H10).
    lord_9 = house_rulers.get(9, [None])[0]
    lord_10 = house_rulers.get(10, [None])[0]
    if lord_9 and lord_10 and lord_9 in planets_data and lord_10 in planets_data:
        h9_pos = planet_houses.get(lord_9, 0)
        h10_pos = planet_houses.get(lord_10, 0)
        # 9th lord in 10th house AND 10th lord in 9th house
        if h9_pos == 10 and h10_pos == 9:
            detected.append(YogaInstance(
                id="power_yoga_dharma_karma_exchange",
                name="Dharma-Karma Parivartana Rāja Yoga (9th & 10th Lords Exchange)",
                category=YogaCategory.POWER,
                status=YogaStatus.PURE,
                plausibility_score=98.0,
                participating_planets=[lord_9, lord_10],
                participating_houses=[9, 10],
                scripture_ref="Phaladeepika 7.11",
                archetype="The Sacred Crown: Mutual reception between 9th Lord (highest grace) and 10th Lord (highest action), producing an illustrious righteous ruler.",
                manifestation_effects=[
                    "Supreme executive authority fused with flawless moral righteousness and civic virtue.",
                    "Beloved leader whose governance and initiatives stand the test of time."
                ],
                positive_factors=[
                    f"9th Lord ({lord_9}) in House 10 and 10th Lord ({lord_10}) in House 9 form the supreme mutual exchange (Parivartana)."
                ],
                breakers=[]
            ))

    # Power Yoga 5: Overpowering Immovable Commander (Phaladeepika 7.12–13)
    # Sun in Sagittarius (10°-20°), day birth (Sun in H7-12), conjoined with Moon (New Moon),
    # Saturn strong in Lagna (House 1), Mars exalted in Capricorn.
    sun_sign = get_sign_of_planet(chart, "Sun")
    sun_house = planet_houses.get("Sun", 0)
    moon_house = planet_houses.get("Moon", 0)
    sat_house = planet_houses.get("Saturn", 0)
    mars_sign = get_sign_of_planet(chart, "Mars")

    sun_deg = planets_data.get("Sun", {}).get("degree_0_to_30", 15.0)
    is_day_birth = sun_house in (7, 8, 9, 10, 11, 12)
    sun_in_sag_mid = (sun_sign == "Sagittarius" and 5.0 <= sun_deg <= 25.0)
    is_new_moon = (sun_house == moon_house and sun_house > 0)
    is_sat_lagna = (sat_house == 1)
    is_mars_exalted = (mars_sign == "Capricorn")

    if sun_in_sag_mid and is_day_birth and is_new_moon and is_sat_lagna and is_mars_exalted:
        detected.append(YogaInstance(
            id="power_yoga_immovable_commander",
            name="The Overpowering Immovable Commander Yoga",
            category=YogaCategory.POWER,
            status=YogaStatus.PURE,
            plausibility_score=99.0,
            participating_planets=["Sun", "Moon", "Saturn", "Mars"],
            participating_houses=[sun_house, 1, planet_houses.get("Mars", 0)],
            scripture_ref="Phaladeepika 7.12–13",
            archetype="The Unshakable Imperator: Sun blazing in Sagittarius with dark New Moon, fortified Saturn in Lagna, and exalted Mars, creating invincible command.",
            manifestation_effects=[
                "Total absence of emotional hesitation or weakness; supreme strategic ruthlessness and military focus.",
                "Rivals and adversaries surrender from afar out of awe and sheer psychological intimidation."
            ],
            positive_factors=[
                "Sun blazing in mid-Sagittarius conjoined dark Moon under daylight.",
                "Saturn rises in 1st House with great strength.",
                "Mars blazes in exaltation in Capricorn."
            ],
            breakers=[]
        ))

    return detected
