"""
jyotish/yogas/power_yogas.py
Chapter 7 Kingly Power Yogas (Multi-Planet Kendras, Digbala Sovereignty, Vargottama Formations,
Full Moon Imperial Alignments, Shining Retrogression, and Upachaya Formations).
Scripture: Phaladeepika Ch. 7, Verses 1–30.
"""

from typing import List, Dict, Any, Set
from jyotish.yogas.models import (
    YogaInstance, YogaCategory, YogaStatus, YogaBreakerDetail
)
from jyotish.yogas.breakers import (
    get_house_of_planet, get_sign_of_planet, get_house_rulers, get_planets_data,
    get_lagna_sign, get_aspect_score,
    OWN_SIGNS, EXALTATION_SIGNS, DEBILITATION_SIGNS, SIGN_LORDS, ZODIAC_SIGNS,
    ASPECT_PALPABLE_THRESHOLD, ASPECT_MARGINAL_THRESHOLD
)
from jyotish.yogas.neechabhanga import audit_neecha_bhanga

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
WATER_SIGNS = {"Cancer", "Scorpio", "Pisces"}
KENDRA_HOUSES = (1, 4, 7, 10)
UPACHAYA_HOUSES = (3, 6, 11)
CLASSICAL_PLANETS = ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn")
RETROGRADE_CAPABLE_PLANETS = ("Mars", "Mercury", "Jupiter", "Venus", "Saturn")
NATURAL_BENEFICS = ("Jupiter", "Venus", "Mercury")
NATURAL_MALEFICS = ("Sun", "Mars", "Saturn", "Rahu", "Ketu")


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


def _get_navamsha_sign(chart: Dict[str, Any], entity: str) -> str:
    """Gets the D9 Navāṁśa sign for a planet or Lagna."""
    if entity in ("Lagna", "Ascendant"):
        d9_lagna = chart.get("vargas", {}).get("D9", {}).get("lagna", {}).get("sign")
        if d9_lagna:
            return d9_lagna
        d9_l2 = chart.get("lagna", {}).get("navamsha_sign")
        if d9_l2:
            return d9_l2
        d1_lagna = chart.get("vargas", {}).get("D1", {}).get("lagna", {})
        deg = d1_lagna.get("degree_0_to_30")
        if deg is None:
            deg = chart.get("lagna", {}).get("degree_0_to_30")
        if deg is None and "longitude" in d1_lagna:
            deg = d1_lagna["longitude"] % 30.0
        if deg is None:
            deg = 15.0
        sign = get_lagna_sign(chart)
    else:
        d9_graha = chart.get("vargas", {}).get("D9", {}).get("grahas", {}).get(entity, {}).get("sign")
        if d9_graha:
            return d9_graha
        d9_p2 = chart.get("planetary_evaluation", {}).get("planets", {}).get(entity, {}).get("d9_sign")
        if d9_p2:
            return d9_p2
        p_info = get_planets_data(chart).get(entity, {})
        deg = p_info.get("degree_0_to_30", (p_info.get("longitude", 0.0) % 30.0))
        sign = p_info.get("sign", "")

    if not sign or sign not in ZODIAC_SIGNS:
        return ""

    sign_idx = ZODIAC_SIGNS.index(sign)
    element = sign_idx % 4
    start = (element * 9) % 12
    pada = int(deg // (30.0 / 9.0))
    d9_idx = (start + min(pada, 8)) % 12
    return ZODIAC_SIGNS[d9_idx]


def _is_planet_retrograde(chart: Dict[str, Any], planet: str) -> bool:
    """Checks whether a planet is retrograde."""
    p_info = get_planets_data(chart).get(planet, {})
    if p_info.get("is_retrograde") is True:
        return True
    eval_p = chart.get("planetary_evaluation", {}).get("planets", {}).get(planet, {})
    if eval_p.get("is_retrograde") is True:
        return True
    speed = p_info.get("speed")
    if speed is not None and speed < 0:
        return True
    return False


def detect_chapter7_power_yogas(chart: Dict[str, Any]) -> List[YogaInstance]:
    """
    Scans chart for Chapter 7 Royal Power Yogas according to Phaladeepika Ch. 7.
    """
    detected: List[YogaInstance] = []
    lagna_sign = get_lagna_sign(chart)
    planets_data = get_planets_data(chart)
    house_rulers = get_house_rulers(chart)

    if not lagna_sign or not planets_data:
        return detected

    planet_houses = {p: get_house_of_planet(chart, p) for p in planets_data}

    # =========================================================================
    # 1. MULTI-PLANET KENDRAS (Phaladeepika 7.2–3)
    # =========================================================================
    # 3 or more planets in Kendras (1, 4, 7, 10) in own sign or exaltation sign.
    dignified_kendra_planets = []
    for p in CLASSICAL_PLANETS:
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
    # 2 to 3 planets with Digbala -> Victorious ruler.
    # 4 to 5 planets with Digbala (SATURN EXPLICITLY EXCLUDED) -> Supreme kingly command.
    digbala_planets = [
        p for p in CLASSICAL_PLANETS
        if p in planets_data and planet_houses.get(p, 0) == DIGBALA_HOUSES.get(p)
    ]
    non_saturn_digbala = [p for p in digbala_planets if p != "Saturn"]
    dig_count = len(digbala_planets)
    non_sat_count = len(non_saturn_digbala)

    if non_sat_count >= 4:
        # Supreme Kingly Sovereignty: 4 or 5 planets excluding Saturn
        detected.append(YogaInstance(
            id=f"digbala_sovereignty_{dig_count}",
            name=f"Supreme Kingly Digbala Sovereignty ({non_sat_count} Grahas without Saturn)",
            category=YogaCategory.POWER,
            status=YogaStatus.PURE,
            plausibility_score=96.0,
            participating_planets=non_saturn_digbala,
            participating_houses=[planet_houses[p] for p in non_saturn_digbala],
            scripture_ref="Phaladeepika 7.4–7",
            archetype=f"Supreme Imperial Directional Force: {non_sat_count} planets (excluding Saturn) attain full Digbala, creating unstoppable royal momentum.",
            manifestation_effects=[
                "Unstoppable vocational traction, decisive strategic command, and authoritative leadership.",
                "Ascends to the highest echelons of authority, ruling institutions or state command."
            ],
            positive_factors=[
                f"Grahas achieving directional strength (excluding Saturn): {', '.join(f'{p} in H{planet_houses[p]}' for p in non_saturn_digbala)}."
            ],
            breakers=[]
        ))
    elif dig_count >= 2:
        # 2 to 3 planets with Digbala
        breakers: List[YogaBreakerDetail] = []
        score = 88.0
        if "Saturn" in digbala_planets and dig_count >= 4:
            breakers.append(YogaBreakerDetail(
                factor="Saturn Excluded from Supreme Digbala",
                culprit_planet="Saturn",
                description="Saturn in 7th House (Digbala) without high dignity signifies servitude or heavy labor rather than kingship (Phaladeepika 7.4–7). Excluded from 4-planet royal count.",
                penalty=10.0
            ))
            score -= 10.0

        detected.append(YogaInstance(
            id=f"digbala_sovereignty_{dig_count}",
            name=f"Digbala Sovereignty ({dig_count} Planets with Directional Force)",
            category=YogaCategory.POWER,
            status=YogaStatus.PURE if score >= 80.0 else YogaStatus.STAINED,
            plausibility_score=score,
            participating_planets=digbala_planets,
            participating_houses=[planet_houses[p] for p in digbala_planets],
            scripture_ref="Phaladeepika 7.4–7",
            archetype=f"Directional Mastery: {dig_count} planets occupy their thrones of directional strength (Digbala), maximizing kinetic force.",
            manifestation_effects=[
                "Decisive strategic command, vocational eminence, and triumph over competitors.",
                "Commands high respect and easily overcomes opponents through structural alignment."
            ],
            positive_factors=[
                f"Planets achieving full Digbala: {', '.join(f'{p} in H{planet_houses[p]}' for p in digbala_planets)}."
            ],
            breakers=breakers
        ))

    # =========================================================================
    # 3. VARGOTTAMA SOVEREIGN FORMATIONS (Phaladeepika 7.14)
    # =========================================================================
    # Form A: Lagna or Moon is Vargottama and aspected by 4+ planets (excluding Moon)
    d1_lagna_sign = lagna_sign
    d9_lagna_sign = _get_navamsha_sign(chart, "Lagna")
    d1_moon_sign = get_sign_of_planet(chart, "Moon")
    d9_moon_sign = _get_navamsha_sign(chart, "Moon")

    is_lagna_vargottama = bool(d1_lagna_sign and d1_lagna_sign == d9_lagna_sign)
    is_moon_vargottama = bool(d1_moon_sign and d1_moon_sign == d9_moon_sign)

    if is_lagna_vargottama:
        aspecting_lagna = [
            p for p in CLASSICAL_PLANETS
            if p != "Moon" and get_aspect_score(chart, p, "Lagna") >= ASPECT_MARGINAL_THRESHOLD
        ]
        if len(aspecting_lagna) >= 4:
            detected.append(YogaInstance(
                id="vargottama_royal_yoga_lagna",
                name="Vargottama Sovereign Configuration (Lagna Aspected by 4+ Planets)",
                category=YogaCategory.POWER,
                status=YogaStatus.PURE,
                plausibility_score=95.0,
                participating_planets=aspecting_lagna,
                participating_houses=[1],
                scripture_ref="Phaladeepika 7.14",
                archetype="Sovereign Harmonic Foundation: Ascendant is Vargottama and aspected by 4+ planets, conferring majestic presence and sovereign authority.",
                manifestation_effects=[
                    "Commands widespread institutional respect and authority through exceptional alignment between inner nature and outer destiny.",
                    "Attains lasting prominence, leadership, and public renown."
                ],
                positive_factors=[
                    f"Lagna is Vargottama in {d1_lagna_sign}, aspected by {len(aspecting_lagna)} planets ({', '.join(aspecting_lagna)})."
                ],
                breakers=[]
            ))

    if is_moon_vargottama:
        aspecting_moon = [
            p for p in CLASSICAL_PLANETS
            if p != "Moon" and get_aspect_score(chart, p, "Moon") >= ASPECT_MARGINAL_THRESHOLD
        ]
        if len(aspecting_moon) >= 4:
            detected.append(YogaInstance(
                id="vargottama_royal_yoga_moon",
                name="Vargottama Sovereign Configuration (Moon Aspected by 4+ Planets)",
                category=YogaCategory.POWER,
                status=YogaStatus.PURE,
                plausibility_score=95.0,
                participating_planets=["Moon"] + aspecting_moon,
                participating_houses=[planet_houses.get("Moon", 0)],
                scripture_ref="Phaladeepika 7.14",
                archetype="Luminous Harmonic Crown: Chandra is Vargottama and aspected by 4+ planets, endowing deep psychological magnetism and royal stature.",
                manifestation_effects=[
                    "Profound charisma, emotional depth, and effortless authority over the public and large groups.",
                    "Attains kingly influence and enduring popularity."
                ],
                positive_factors=[
                    f"Moon is Vargottama in {d1_moon_sign}, aspected by {len(aspecting_moon)} planets ({', '.join(aspecting_moon)})."
                ],
                breakers=[]
            ))

    # Form B: 1st lord is Vargottama in Kendra or 9th house while 9th lord is in own sign or exalted
    lord_1 = house_rulers.get(1, [None])[0]
    lord_9 = house_rulers.get(9, [None])[0]
    if lord_1 and lord_9 and lord_1 in planets_data and lord_9 in planets_data:
        l1_d1_s = get_sign_of_planet(chart, lord_1)
        l1_d9_s = _get_navamsha_sign(chart, lord_1)
        l1_h = planet_houses.get(lord_1, 0)
        l9_s = get_sign_of_planet(chart, lord_9)

        is_l1_vargottama = bool(l1_d1_s and l1_d1_s == l1_d9_s)
        is_l1_kendra_or_9 = l1_h in (1, 4, 7, 10, 9)
        is_l9_dignified = (l9_s in OWN_SIGNS.get(lord_9, []) or l9_s == EXALTATION_SIGNS.get(lord_9))

        if is_l1_vargottama and is_l1_kendra_or_9 and is_l9_dignified:
            detected.append(YogaInstance(
                id="vargottama_royal_yoga_l1_l9",
                name="Vargottama 1st Lord with Fortified 9th Lord Sovereign Yoga",
                category=YogaCategory.POWER,
                status=YogaStatus.PURE,
                plausibility_score=94.0,
                participating_planets=[lord_1, lord_9],
                participating_houses=[l1_h, planet_houses.get(lord_9, 0)],
                scripture_ref="Phaladeepika 7.14",
                archetype="Unshakeable Sovereign Integrity: 1st Lord is Vargottama in an angle/9th while 9th Lord is domiciled or exalted, producing a righteous ruler of great fortitude.",
                manifestation_effects=[
                    "High executive authority guided by profound moral purpose and philosophical conviction.",
                    "Builds lasting legacies and commands deep institutional loyalty."
                ],
                positive_factors=[
                    f"1st Lord ({lord_1}) is Vargottama in {l1_d1_s} in House {l1_h}.",
                    f"9th Lord ({lord_9}) is exalted or domiciled in {l9_s}."
                ],
                breakers=[]
            ))

    # =========================================================================
    # 4. FULL / BRIGHT MOON SOVEREIGN CONFIGURATIONS (Phaladeepika 7.15–18)
    # =========================================================================
    sun_lon = planets_data.get("Sun", {}).get("longitude")
    moon_lon = planets_data.get("Moon", {}).get("longitude")
    moon_h = planet_houses.get("Moon", 0)

    if sun_lon is not None and moon_lon is not None and moon_h > 0:
        elongation = abs(moon_lon - sun_lon) % 360.0
        if elongation > 180.0:
            elongation = 360.0 - elongation
        is_full_moon = (elongation > 150.0)

        # Full Moon Config 1: Full Moon in Kendra (4, 7, 10 - excluding 1st) aspected by an exalted or domiciled planet
        if is_full_moon and moon_h in (4, 7, 10):
            dignified_aspectors = []
            for p in CLASSICAL_PLANETS:
                if p in planets_data and p != "Moon":
                    p_s = get_sign_of_planet(chart, p)
                    if p_s in OWN_SIGNS.get(p, []) or p_s == EXALTATION_SIGNS.get(p):
                        if get_aspect_score(chart, p, "Moon") >= ASPECT_MARGINAL_THRESHOLD:
                            dignified_aspectors.append(p)

            if dignified_aspectors:
                detected.append(YogaInstance(
                    id="power_yoga_full_moon_kendra",
                    name="Full Moon Kendra Sovereignty (Aspected by Dignified Graha)",
                    category=YogaCategory.POWER,
                    status=YogaStatus.PURE,
                    plausibility_score=92.0,
                    participating_planets=["Moon"] + dignified_aspectors,
                    participating_houses=[moon_h],
                    scripture_ref="Phaladeepika 7.15",
                    archetype="The Radiating Sovereign: Full Moon in an angle aspected by a planet in peak dignity bestows public adoration, vast resources, and royal command.",
                    manifestation_effects=[
                        "Enjoys radiant public eminence, wealth, cultural honor, and leadership.",
                        "Gains magnetic public devotion and administrative power."
                    ],
                    positive_factors=[
                        f"Full Moon in Kendra H{moon_h} receives aspect from dignified: {', '.join(dignified_aspectors)}."
                    ],
                    breakers=[]
                ))

        # Full Moon Config 2: Full Moon in water sign in House 1 in own Navāṁśa (Cancer), with no malefics in Kendras
        if is_full_moon and moon_h == 1:
            moon_s = get_sign_of_planet(chart, "Moon")
            d9_m_s = _get_navamsha_sign(chart, "Moon")
            if moon_s in WATER_SIGNS and d9_m_s == "Cancer":
                malefics_in_kendra = [
                    p for p in ("Sun", "Mars", "Saturn", "Rahu", "Ketu")
                    if planet_houses.get(p, 0) in KENDRA_HOUSES
                ]
                if not malefics_in_kendra:
                    detected.append(YogaInstance(
                        id="power_yoga_full_moon_water_lagna",
                        name="Full Moon Water Lagna Imperial Sovereignty",
                        category=YogaCategory.POWER,
                        status=YogaStatus.PURE,
                        plausibility_score=96.0,
                        participating_planets=["Moon"],
                        participating_houses=[1],
                        scripture_ref="Phaladeepika 7.16",
                        archetype="The Imperial Nectar: Full Moon in watery Lagna in own Navāṁśa completely unblemished by angular malefics bestows peaceful imperial dominion and unmatched grace.",
                        manifestation_effects=[
                            "Unrivaled charisma, serenity, diplomatic genius, and peaceful authority over lands and people.",
                            "Commands universal respect and lives in abundant prosperity."
                        ],
                        positive_factors=[
                            f"Full Moon in watery sign {moon_s} in Lagna in own Navāṁśa (Cancer), completely free of angular malefics."
                        ],
                        breakers=[]
                    ))

        # Full Moon Config 3: Full Moon in Navāṁśa of 'friend of the lotus' (Cancer or Leo) with benefics in Kendras and no malefics in Kendras
        if is_full_moon:
            d9_m_s = _get_navamsha_sign(chart, "Moon")
            if d9_m_s in ("Cancer", "Leo"):
                benefics_in_kendra = [
                    p for p in NATURAL_BENEFICS
                    if planet_houses.get(p, 0) in KENDRA_HOUSES
                ]
                malefics_in_kendra = [
                    p for p in ("Sun", "Mars", "Saturn", "Rahu", "Ketu")
                    if planet_houses.get(p, 0) in KENDRA_HOUSES
                ]
                if benefics_in_kendra and not malefics_in_kendra:
                    detected.append(YogaInstance(
                        id="power_yoga_full_moon_lotus_friend_navamsha",
                        name="Full Moon Imperial Navāṁśa Sovereignty",
                        category=YogaCategory.POWER,
                        status=YogaStatus.PURE,
                        plausibility_score=94.0,
                        participating_planets=["Moon"] + benefics_in_kendra,
                        participating_houses=[moon_h] + [planet_houses[p] for p in benefics_in_kendra],
                        scripture_ref="Phaladeepika 7.17",
                        archetype="The Lotus King: Full Moon in royal solar/lunar Navāṁśa supported purely by angular benefics produces a noble, universally cherished sovereign.",
                        manifestation_effects=[
                            "Commands high civil, philanthropic, and state leadership with flawless reputation.",
                            "Endowed with generosity, visionary statecraft, and spiritual wisdom."
                        ],
                        positive_factors=[
                            f"Full Moon in {d9_m_s} Navāṁśa ('friend of the lotus') with benefics in Kendras ({', '.join(benefics_in_kendra)}) and zero angular malefics."
                        ],
                        breakers=[]
                    ))

        # Full Moon Config 4: Jupiter and Moon together in Kendra aspected by Venus, with no planet debilitated without cancellation
        jup_h = planet_houses.get("Jupiter", 0)
        if jup_h == moon_h and jup_h in KENDRA_HOUSES:
            ven_aspect_moon = get_aspect_score(chart, "Venus", "Moon") >= ASPECT_MARGINAL_THRESHOLD
            ven_aspect_jup = get_aspect_score(chart, "Venus", "Jupiter") >= ASPECT_MARGINAL_THRESHOLD
            if ven_aspect_moon or ven_aspect_jup:
                all_planets_clean = True
                for cp in CLASSICAL_PLANETS:
                    if get_sign_of_planet(chart, cp) == DEBILITATION_SIGNS.get(cp):
                        is_rescued, _, _ = audit_neecha_bhanga(cp, chart)
                        if not is_rescued:
                            all_planets_clean = False
                            break

                if all_planets_clean:
                    detected.append(YogaInstance(
                        id="power_yoga_gaja_kesari_venus_aspect",
                        name="Gajakesarī Imperial Crown Yoga (Jupiter + Moon in Kendra Aspected by Venus)",
                        category=YogaCategory.POWER,
                        status=YogaStatus.PURE,
                        plausibility_score=95.0,
                        participating_planets=["Moon", "Jupiter", "Venus"],
                        participating_houses=[moon_h],
                        scripture_ref="Phaladeepika 7.18",
                        archetype="The Crowned Preceptor: Guru and Chandra together in an angle blessed by Venus's gaze without unredeemed debilities create a monarch endowed with supreme wisdom and fortune.",
                        manifestation_effects=[
                            "Supreme academic, spiritual, and administrative authority; revered by kings and commoners alike.",
                            "Attains everlasting wealth, fame, and indestructible royal status."
                        ],
                        positive_factors=[
                            f"Jupiter and Moon conjoin in Kendra H{moon_h}, receiving aspect from Venus, free of unredeemed debility."
                        ],
                        breakers=[]
                    ))

    # =========================================================================
    # 5. SHINING RETROGRESSION SOVEREIGNTY (Vakra Bala — Phaladeepika 7.19)
    # =========================================================================
    # Planet is retrograde in House 1, 4, 5, 7, 9, 10, or 11.
    # Even if debilitated, retrogression confers extreme kinetic brilliance (Vakra Bala).
    # 1 planet = King-like; 2-3 planets = Praised Monarch.
    auspicious_houses_vakra = (1, 4, 5, 7, 9, 10, 11)
    vakra_planets = [
        p for p in RETROGRADE_CAPABLE_PLANETS
        if p in planets_data and _is_planet_retrograde(chart, p) and planet_houses.get(p, 0) in auspicious_houses_vakra
    ]
    vakra_count = len(vakra_planets)

    if vakra_count >= 1:
        if vakra_count >= 2:
            score = 94.0
            archetype = f"Praised Monarch of Unstoppable Drive: {vakra_count} retrograde planets in auspicious houses unleash luminous kinetic brilliance (Vakra Bala), producing an exalted leader praised across the land."
            name = f"Vakra Bala Sovereignty ({vakra_count} Brilliant Retrograde Planets)"
        else:
            score = 88.0
            archetype = f"The Luminous Challenger: Retrograde {vakra_planets[0]} in an auspicious seat shines with intense kinetic brightness (Vakra Bala), conferring royal dignity and bold independence."
            name = f"Vakra Bala Sovereignty (1 Brilliant Retrograde Planet - {vakra_planets[0]})"

        detected.append(YogaInstance(
            id=f"vakra_bala_sovereignty_{vakra_count}",
            name=name,
            category=YogaCategory.POWER,
            status=YogaStatus.PURE,
            plausibility_score=score,
            participating_planets=vakra_planets,
            participating_houses=[planet_houses[p] for p in vakra_planets],
            scripture_ref="Phaladeepika 7.19",
            archetype=archetype,
            manifestation_effects=[
                "Exceptional unconventional drive, unrelenting persistence, and decisive strategic leadership.",
                "Draws intense kinetic resources and achieves monumental worldly recognition."
            ],
            positive_factors=[
                f"Retrograde Grahas with Vakra Bala in auspicious seats: {', '.join(f'{p} in H{planet_houses[p]}' for p in vakra_planets)}."
            ],
            breakers=[]
        ))

    # =========================================================================
    # 6. MALEFICS IN UPACHAYAS & SPECIFIC FORMATIONS (Phaladeepika 7.20–23)
    # =========================================================================
    # Malefics in Upachayas (3, 6, 11 from Lagna OR from 1st Lord)
    active_malefics = [p for p in ("Mars", "Saturn", "Sun") if p in planets_data]
    if active_malefics:
        all_in_upachaya_lagna = all(planet_houses.get(p, 0) in UPACHAYA_HOUSES for p in active_malefics)
        l1_h = planet_houses.get(lord_1, 0) if lord_1 else 0
        all_in_upachaya_l1 = (
            l1_h > 0 and
            all(((planet_houses.get(p, 0) - l1_h) % 12 + 1) in UPACHAYA_HOUSES for p in active_malefics)
        )

        if all_in_upachaya_lagna or all_in_upachaya_l1:
            ref_source = "Lagna" if all_in_upachaya_lagna else f"1st Lord ({lord_1})"
            detected.append(YogaInstance(
                id="malefics_upachaya_sovereignty",
                name="Malefics in Upachāyas Sovereign Power Yoga",
                category=YogaCategory.POWER,
                status=YogaStatus.PURE,
                plausibility_score=92.0,
                participating_planets=active_malefics,
                participating_houses=[planet_houses[p] for p in active_malefics],
                scripture_ref="Phaladeepika 7.20",
                archetype=f"The Invincible Conqueror: Natural malefics ({', '.join(active_malefics)}) stationed in Upachāya houses (3, 6, 11) from {ref_source} crush enemies, debts, and obstacles, converting raw friction into unstoppable worldly triumph.",
                manifestation_effects=[
                    "Total vanquishing of adversaries, litigation, and competitive resistance.",
                    "Surges in wealth, professional authority, and public respect through relentless determination."
                ],
                positive_factors=[
                    f"Natural malefics ({', '.join(active_malefics)}) occupy Upachāya houses (3, 6, 11) from {ref_source}."
                ],
                breakers=[]
            ))

    # Specific Combo 1: Mars & Mercury in 2nd house (Military Intellect)
    mars_h = planet_houses.get("Mars", 0)
    merc_h = planet_houses.get("Mercury", 0)
    if mars_h == 2 and merc_h == 2:
        detected.append(YogaInstance(
            id="power_yoga_mars_mercury_h2",
            name="Military Intellect Power Yoga (Mars + Mercury in H2)",
            category=YogaCategory.POWER,
            status=YogaStatus.PURE,
            plausibility_score=90.0,
            participating_planets=["Mars", "Mercury"],
            participating_houses=[2],
            scripture_ref="Phaladeepika 7.21",
            archetype="The Strategic Commander: Mars and Mercury combine in the 2nd House of speech and treasury, forging razor-sharp analytical intellect and commanding oratory.",
            manifestation_effects=[
                "Piercing intellect, surgical debate skills, and commanding administrative speech.",
                "Excels in logistics, engineering, military command, finance, and tactical execution."
            ],
            positive_factors=[
                "Mars and Mercury unite in the 2nd House of speech and assets."
            ],
            breakers=[]
        ))

    # Specific Combo 2: Sun & Venus in 4th house (Intelligence & Secrecy)
    sun_h = planet_houses.get("Sun", 0)
    ven_h = planet_houses.get("Venus", 0)
    if sun_h == 4 and ven_h == 4:
        detected.append(YogaInstance(
            id="power_yoga_sun_venus_h4",
            name="Crown Intellect & Statecraft Yoga (Sun + Venus in H4)",
            category=YogaCategory.POWER,
            status=YogaStatus.PURE,
            plausibility_score=90.0,
            participating_planets=["Sun", "Venus"],
            participating_houses=[4],
            scripture_ref="Phaladeepika 7.22",
            archetype="The Imperial Statesman: Sun and Venus occupy the 4th House (Bandhu Bhava), endowing deep intelligence, political secrecy, and luxurious estates.",
            manifestation_effects=[
                "Profound administrative intuition, diplomatic discretion, and control over property and conveyances.",
                "Enjoys state favor, luxury vehicles, and honorable domestic peace."
            ],
            positive_factors=[
                "Sun and Venus occupy the 4th House of mind, estates, and alliances."
            ],
            breakers=[]
        ))

    # Specific Combo 3: Mars in 10th, Saturn in 11th, Jupiter in 1st
    sat_h = planet_houses.get("Saturn", 0)
    jup_h = planet_houses.get("Jupiter", 0)
    if mars_h == 10 and sat_h == 11 and jup_h == 1:
        detected.append(YogaInstance(
            id="power_yoga_mars10_sat11_jup1",
            name="Supreme Tri-Pillar Kingly Configuration (Mars H10, Saturn H11, Jupiter H1)",
            category=YogaCategory.POWER,
            status=YogaStatus.PURE,
            plausibility_score=99.0,
            participating_planets=["Jupiter", "Mars", "Saturn"],
            participating_houses=[1, 10, 11],
            scripture_ref="Phaladeepika 7.23",
            archetype="The Sovereign Triumvirate: Jupiter in 1st grants divine wisdom, Mars in 10th Digbala gives decisive conquest, and Saturn in 11th secures perpetual gains and lasting dominion.",
            manifestation_effects=[
                "Absolute monarchical command, profound strategic vision, and unending worldly expansion.",
                "Revered as an unshakeable leader across generations."
            ],
            positive_factors=[
                "Jupiter in Lagna (supreme dharma & wisdom).",
                "Mars in 10th House (peak Digbala & vocational conquest).",
                "Saturn in 11th House (unshakeable wealth, influence, and longevity)."
            ],
            breakers=[]
        ))

    # =========================================================================
    # 7. CLASSICAL SPECIFIC POWER YOGAS (Phaladeepika 7.8–13)
    # =========================================================================

    # Power Yoga: Venus Rising in Aśvinī (Phaladeepika 7.8a)
    if ven_h == 1:
        ven_nak = _get_nakshatra_of_planet(chart, "Venus")
        ven_sign = get_sign_of_planet(chart, "Venus")
        is_asvini = ("Ashwini" in ven_nak or "Aswini" in ven_nak or "Asvini" in ven_nak or (ven_sign == "Aries" and not ven_nak))
        if is_asvini:
            aspecting_planets = [
                p for p in CLASSICAL_PLANETS
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

    # Power Yoga: First Lord with Venus in the 2nd House (Phaladeepika 7.8b–9)
    if lord_1 and lord_1 in planets_data and "Venus" in planets_data:
        l1_h = planet_houses.get(lord_1, 0)
        v_h = planet_houses.get("Venus", 0)
        if l1_h == 2 and v_h == 2:
            l1_s = get_sign_of_planet(chart, lord_1)
            v_s = get_sign_of_planet(chart, "Venus")
            if l1_s != DEBILITATION_SIGNS.get(lord_1) and v_s != DEBILITATION_SIGNS.get("Venus"):
                detected.append(YogaInstance(
                    id="power_yoga_l1_venus_h2",
                    name="Patriarchal Treasury Power Yoga (1st Lord + Venus in H2)",
                    category=YogaCategory.POWER,
                    status=YogaStatus.PURE,
                    plausibility_score=88.0,
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

    # Power Yoga: Mars in Fire Sign Aspected by a Friend (Phaladeepika 7.10)
    mars_sign = get_sign_of_planet(chart, "Mars")
    if mars_sign in FIRE_SIGNS and mars_h > 0:
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
                participating_houses=[mars_h],
                scripture_ref="Phaladeepika 7.10",
                archetype="The Bold Commander: Mars blazes in a fire sign aspected by a friendly luminary/preceptor, conferring decisive executive power.",
                manifestation_effects=[
                    "Bold, fearless executive command; decisive courage in high-stakes crises.",
                    "Commands respect from subordinates; thrives in military, legal, athletic, or high-level strategic arenas."
                ],
                positive_factors=[
                    f"Mars in fire sign {mars_sign} (House {mars_h}) receives palpable aspect from: {', '.join(friendly_aspects)}."
                ],
                breakers=[]
            ))

    # Power Yoga: Exchange of 9th and 10th Lords (Phaladeepika 7.11)
    lord_10_p = house_rulers.get(10, [None])[0]
    if lord_9 and lord_10_p:
        if lord_9 in planets_data and lord_10_p in planets_data:
            h9_pos = planet_houses.get(lord_9, 0)
            h10_pos = planet_houses.get(lord_10_p, 0)
            if h9_pos == 10 and h10_pos == 9:
                detected.append(YogaInstance(
                    id="power_yoga_dharma_karma_exchange",
                    name="Dharma-Karma Parivartana Rāja Yoga (9th & 10th Lords Exchange)",
                    category=YogaCategory.POWER,
                    status=YogaStatus.PURE,
                    plausibility_score=98.0,
                    participating_planets=[lord_9, lord_10_p],
                    participating_houses=[9, 10],
                    scripture_ref="Phaladeepika 7.11",
                    archetype="The Sacred Crown: Mutual reception between 9th Lord (highest grace) and 10th Lord (highest action), producing an illustrious righteous ruler.",
                    manifestation_effects=[
                        "Supreme executive authority fused with flawless moral righteousness and civic virtue.",
                        "Beloved leader whose governance and initiatives stand the test of time."
                    ],
                    positive_factors=[
                        f"9th Lord ({lord_9}) in House 10 and 10th Lord ({lord_10_p}) in House 9 form the supreme mutual exchange (Parivartana)."
                    ],
                    breakers=[]
                ))

    # Power Yoga: Overpowering Immovable Commander (Phaladeepika 7.12–13)
    moon_house = planet_houses.get("Moon", 0)
    mars_sign = get_sign_of_planet(chart, "Mars")
    sun_sign = get_sign_of_planet(chart, "Sun")

    sun_deg = planets_data.get("Sun", {}).get("degree_0_to_30", 15.0)
    is_day_birth = sun_h in (7, 8, 9, 10, 11, 12)
    sun_in_sag_mid = (sun_sign == "Sagittarius" and 5.0 <= sun_deg <= 25.0)
    is_new_moon = (sun_h == moon_house and sun_h > 0)
    is_sat_lagna = (sat_h == 1)
    is_mars_exalted = (mars_sign == "Capricorn")

    if sun_in_sag_mid and is_day_birth and is_new_moon and is_sat_lagna and is_mars_exalted:
        detected.append(YogaInstance(
            id="power_yoga_immovable_commander",
            name="The Overpowering Immovable Commander Yoga",
            category=YogaCategory.POWER,
            status=YogaStatus.PURE,
            plausibility_score=99.0,
            participating_planets=["Sun", "Moon", "Saturn", "Mars"],
            participating_houses=[sun_h, 1, planet_houses.get("Mars", 0)],
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
