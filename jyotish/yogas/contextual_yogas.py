"""
jyotish/yogas/contextual_yogas.py
Contextual & Macro Setup Yogas Engine (Hemisphere A: Pure Foundational Calculus).

Scripture: Phaladeepika Ch. 6 (Verses 14-16, 19-20, 37-39, 42-43) & BPHS Ch. 35, 37-38.
Architecture: Strictly adheres to YOGA_ARCHITECTURE.md Category 11 (CONTEXTUAL).

Categories Evaluated:
1. Sāṅkhya Yogas (7 Nabhasa sign-count yogas: Gola, Yuga, Śūla, Kedāra, Pāśa, Dāminī/Dāma, Vallakī/Vīṇā)
   - Standalone per Phaladeepika 6.39 (anya-pūrva-muktān vihāya) — ZERO Layer 2 breakers applied.
2. Candrādhi & Lagnādhi Yogas (Benefics in 6th, 7th, OR 8th from Moon/Lagna)
   - Classical 'vā' (OR) graded across Netā (6th), Mantrī (7th), Bhūpati (8th).
   - Moon strictly excluded; audit_dusthana_placement FORBIDDEN; continuous Sphuṭa Dṛṣṭi + combustion + Shadbala audited.
3. Mahābhāgya Yoga (Day/Night + Odd/Even sign synergy across Lagna, Sun, Moon for Male/Female charts, including 3/4 partial confluence).
4. Sun–Moon Quadrant Yogas (Adhama, Sama, Variṣṭha — Kendra, Paṇaphara, Apoklima from Sun to Moon).
5. Solitary 1st House Yogas (Śubha Tanu & Aśubha Tanu).
6. Dual-Lagna Rāja Yoga (Ubhayalagna Kendra-Koṇa Synchrony).
"""

from typing import List, Dict, Any, Set, Tuple, Optional
from jyotish.yogas.models import (
    YogaInstance, YogaCategory, YogaStatus, YogaBreakerDetail
)
from jyotish.yogas.breakers import (
    get_lagna_sign, get_planets_data, get_sign_of_planet, get_house_of_planet,
    get_aspect_score, resolve_yoga_score_and_status,
    audit_combustion, audit_shadbala_muscle, audit_trishadaya_interference,
    audit_dusthana_placement,
    NATURAL_BENEFICS, NATURAL_MALEFICS, ZODIAC_SIGNS, SIGN_LORDS,
    ASPECT_PALPABLE_THRESHOLD, ASPECT_MARGINAL_THRESHOLD
)

CLASSICAL_7_GRAHAS: List[str] = [
    "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"
]

ADHI_BENEFICS: Tuple[str, ...] = ("Mercury", "Jupiter", "Venus")

ODD_SIGNS: Set[str] = {"Aries", "Gemini", "Leo", "Libra", "Sagittarius", "Aquarius"}
EVEN_SIGNS: Set[str] = {"Taurus", "Cancer", "Virgo", "Scorpio", "Capricorn", "Pisces"}


def detect_sankhya_yogas(chart: Dict[str, Any]) -> List[YogaInstance]:
    """
    Evaluates the 7 Sāṅkhya Yogas based on the number of unique zodiac signs
    occupied by the classical 7 physical planets (Sun through Saturn).
    Scripture: Phaladeepika 6.37-39 (anya-pūrva-muktān vihāya), BPHS Ch. 35.
    Standing Rule: Sāṅkhya yogas stand completely alone with ZERO Layer 2 breakers.
    """
    detected: List[YogaInstance] = []
    occupied_signs: Set[str] = set()
    participating_grahas: List[str] = []

    for p in CLASSICAL_7_GRAHAS:
        sign = get_sign_of_planet(chart, p)
        if sign and sign in ZODIAC_SIGNS:
            occupied_signs.add(sign)
            participating_grahas.append(p)

    # All 7 classical planets must be present to evaluate whole-chart sign distribution
    if len(participating_grahas) < 7:
        return detected

    num_signs = len(occupied_signs)
    if num_signs == 0:
        return detected

    sankhya_definitions = {
        1: {
            "id": "sankhya_gola_yoga",
            "name": "Gola Yoga (Singular Focus)",
            "archetype": "Extremely concentrated, intense, narrow life focus. All energy is channeled into a single existential sphere.",
            "manifestations": [
                "Unwavering single-minded intensity or potential dogmatism.",
                "All major karmic lessons and resources converge into one singular department of life.",
                "Tremendous potential for extreme specialization or ascetic detachment."
            ]
        },
        2: {
            "id": "sankhya_yuga_yoga",
            "name": "Yuga Yoga (Dualistic Tension)",
            "archetype": "Life pivots around strong dualities, intense polarization, and heavy interdependence on key partners or counterparts.",
            "manifestations": [
                "Continuous push-and-pull between two primary areas of life or core relationships.",
                "Reliance on alliances, contracts, or strong counterparties to make progress.",
                "Tendency to experience life in high-contrast terms."
            ]
        },
        3: {
            "id": "sankhya_shula_yoga",
            "name": "Śūla Yoga (Trident Resolve)",
            "archetype": "Piercing ambition, austere courage, sharp and incisive resolve. Endures hardship to conquer goals.",
            "manifestations": [
                "Sharp, incisive willpower and readiness to overcome formidable obstacles.",
                "Displays an uncompromising, focused, or battle-ready disposition.",
                "High tolerance for adversity and rigorous physical or mental endurance."
            ]
        },
        4: {
            "id": "sankhya_kedara_yoga",
            "name": "Kedāra Yoga (Agricultural Patience)",
            "archetype": "Steadfast, grounded, hardworking, and patient. Builds enduring tangible assets like fertile fields.",
            "manifestations": [
                "Constructive, methodical builder mindset with long-term stamina.",
                "Pragmatic approach to resources, real estate, and tangible security.",
                "High dependability and dutiful support to family and community."
            ]
        },
        5: {
            "id": "sankhya_pasa_yoga",
            "name": "Pāśa Yoga (Ties of Duty)",
            "archetype": "Strong bonds to family, duty, and community. Skilled in worldly negotiations, administration, and social webs.",
            "manifestations": [
                "Entangled in extensive familial, professional, or social obligations.",
                "Resourceful administrative ability, diplomatic skill, and social networking.",
                "Progress is achieved through navigating obligations and managing complex networks."
            ]
        },
        6: {
            "id": "sankhya_dama_yoga",
            "name": "Dāminī (Dāma) Yoga (Generous & Dutiful Benefactor)",
            "archetype": "Self-controlled, dutiful, generous, and helpful to many, endowed with versatile talents and public respect.",
            "manifestations": [
                "Generous and philanthropic outlook, naturally inclined to support and protect others.",
                "Strong sense of moral duty (Dharma) and self-discipline across worldly responsibilities.",
                "Honored in society for fairness, benevolence, and balanced judgment."
            ]
        },
        7: {
            "id": "sankhya_veena_yoga",
            "name": "Vallakī (Vīṇā) Yoga (Harmonious Versatility)",
            "archetype": "Balanced, artistic, cultured, and multifaceted. Life unfolds with melodic grace and widespread intellectual curiosity.",
            "manifestations": [
                "Love of music, literature, aesthetics, sciences, and cultural refinement.",
                "Widespread intellectual curiosity and ability to adapt effortlessly to multiple disciplines.",
                "Harmonious distribution of planetary energy across the entire horoscope."
            ]
        }
    }

    if num_signs in sankhya_definitions:
        defn = sankhya_definitions[num_signs]
        detected.append(YogaInstance(
            id=defn["id"],
            name=defn["name"],
            category=YogaCategory.CONTEXTUAL,
            status=YogaStatus.PURE,
            plausibility_score=90.0,
            participating_planets=participating_grahas,
            participating_houses=sorted(list({
                get_house_of_planet(chart, p)
                for p in participating_grahas
                if get_house_of_planet(chart, p) > 0
            })),
            scripture_ref="Phaladeepika 6.37-39, BPHS Ch. 35 (Nabhasa Sāṅkhya Yogas)",
            archetype=defn["archetype"],
            manifestation_effects=defn["manifestations"],
            positive_factors=[
                f"Classical 7 grahas distributed cleanly across exactly {num_signs} unique signs ({', '.join(sorted(occupied_signs))}).",
                "Operates as a standalone macro cognitive filter (anya-pūrva-muktān vihāya)."
            ],
            breakers=[]
        ))

    return detected


def _extract_focal_longitude(chart: Dict[str, Any], target: str) -> Optional[float]:
    """Extracts longitudinal degree (0..360 or 0..30) for Moon or Lagna if available."""
    if not isinstance(chart, dict):
        return None
    if target == "Lagna":
        lagna_obj = chart.get("lagna") or chart.get("ascendant")
        if isinstance(lagna_obj, dict):
            lon = lagna_obj.get("longitude", lagna_obj.get("degree"))
            if lon is not None:
                try:
                    return float(lon)
                except (TypeError, ValueError):
                    pass
        d1_lagna = ((chart.get("vargas") or {}).get("D1") or {}).get("lagna")
        if isinstance(d1_lagna, dict):
            lon = d1_lagna.get("longitude", d1_lagna.get("degree"))
            if lon is not None:
                try:
                    return float(lon)
                except (TypeError, ValueError):
                    pass
        return None

    planets_data = get_planets_data(chart)
    p_info = planets_data.get(target)
    if isinstance(p_info, dict):
        lon = p_info.get("longitude", p_info.get("degree"))
        if lon is not None:
            try:
                return float(lon)
            except (TypeError, ValueError):
                pass
    return None


def _evaluate_single_adhi_yoga(
    chart: Dict[str, Any],
    focal_label: str,
    focal_target: str,
    focal_house: int,
    focal_lon: Optional[float],
    yoga_id: str,
    yoga_name: str,
    scripture_ref: str,
) -> List[YogaInstance]:
    """
    Evaluates Candrādhi or Lagnādhi Yoga (Phaladeepika 6.14-15 / 6.19-20, 6.42-43).
    - Classical 'vā' (OR) rule across 6th (Netā), 7th (Mantrī), and 8th (Bhūpati).
    - Strictly excludes Moon (only Mercury, Jupiter, Venus participate).
    - NEVER calls audit_dusthana_placement (requires houses 6, 7, 8!).
    - Audits continuous Sphuṭa Dṛṣṭi & longitudinal alignment onto the 12th/1st/2nd focal axis,
      plus audit_combustion and audit_shadbala_muscle.
    """
    planets_data = get_planets_data(chart)
    planet_houses = {p: get_house_of_planet(chart, p) for p in planets_data}

    h6 = ((focal_house + 4) % 12) + 1
    h7 = ((focal_house + 5) % 12) + 1
    h8 = ((focal_house + 6) % 12) + 1

    b6 = [p for p in ADHI_BENEFICS if planet_houses.get(p) == h6]
    b7 = [p for p in ADHI_BENEFICS if planet_houses.get(p) == h7]
    b8 = [p for p in ADHI_BENEFICS if planet_houses.get(p) == h8]
    all_adhi = b6 + b7 + b8

    if not all_adhi:
        return []

    archetype_roles: List[str] = []
    if b6:
        archetype_roles.append(f"Netā (Enforcer/Commander in H{h6}: {', '.join(b6)})")
    if b7:
        archetype_roles.append(f"Mantrī (Advisor/Minister in H{h7}: {', '.join(b7)})")
    if b8:
        archetype_roles.append(f"Bhūpati (Landholder/Sovereign in H{h8}: {', '.join(b8)})")

    pillars_count = int(bool(b6)) + int(bool(b7)) + int(bool(b8))
    base_map = {1: 68.0, 2: 80.0, 3: 90.0}
    score = base_map[pillars_count] + max(0, len(all_adhi) - pillars_count) * 4.0

    pos: List[str] = [
        f"Benefics in 6th/7th/8th from {focal_label} ({pillars_count}/3 command pillars): {', '.join(archetype_roles)}."
    ]
    breakers: List[YogaBreakerDetail] = []

    best_focal_virupas = 0.0
    best_axis_alignment_bonus = 0.0
    weak_alignment_planets: List[str] = []
    focal_deg_in_sign = (float(focal_lon) % 30.0) if focal_lon is not None else None

    for p in all_adhi:
        virupas = get_aspect_score(chart, p, focal_target)
        if virupas > best_focal_virupas:
            best_focal_virupas = virupas

        p_lon = (planets_data.get(p) or {}).get("longitude")
        if p_lon is None:
            p_lon = (planets_data.get(p) or {}).get("degree")
        if focal_deg_in_sign is not None and p_lon is not None:
            try:
                p_deg_in_sign = float(p_lon) % 30.0
                orb = abs(p_deg_in_sign - focal_deg_in_sign)
                if orb <= 12.0:
                    best_axis_alignment_bonus = max(best_axis_alignment_bonus, 8.0)
                elif orb >= 22.0 and virupas < ASPECT_MARGINAL_THRESHOLD:
                    weak_alignment_planets.append(f"{p} (orb {orb:.1f}°)")
            except (TypeError, ValueError):
                pass

    if best_focal_virupas >= ASPECT_PALPABLE_THRESHOLD:
        score += 8.0
        pos.append(
            f"Palpable Sphuṭa Dṛṣṭi ({best_focal_virupas:.1f} Virūpas) directly fortifies {focal_label}."
        )
    elif best_focal_virupas >= ASPECT_MARGINAL_THRESHOLD:
        score += 5.0
        pos.append(
            f"Moderate Sphuṭa Dṛṣṭi ({best_focal_virupas:.1f} Virūpas) projects onto {focal_label}."
        )
    elif best_axis_alignment_bonus > 0.0:
        score += best_axis_alignment_bonus
        pos.append(
            f"Close longitudinal alignment with the 12th/1st/2nd {focal_label} horizon axis."
        )
    elif focal_lon is None and pillars_count >= 1:
        # When degree coordinates are omitted, grant baseline structural credit
        score += 7.0
    elif weak_alignment_planets and len(all_adhi) == len(weak_alignment_planets):
        breakers.append(YogaBreakerDetail(
            factor="Wide Focal-Axis Orb",
            culprit_planet=", ".join(all_adhi),
            description=(
                f"Participating benefic(s) ({', '.join(weak_alignment_planets)}) are widely separated "
                f"in degree from {focal_label} on the 12th/1st/2nd axis."
            ),
            penalty=10.0
        ))

    # Layer 2 Breakers per YOGA_ARCHITECTURE.md Row 11:
    # audit_combustion = YES, audit_shadbala = YES, audit_dusthana = FORBIDDEN
    breakers.extend(audit_combustion(all_adhi, chart))
    sb_breakers, sb_pos = audit_shadbala_muscle(all_adhi, chart)
    breakers.extend(sb_breakers)
    pos.extend(sb_pos)

    final_score, status = resolve_yoga_score_and_status(score, breakers)

    participating_planets = (["Moon"] + all_adhi) if focal_target == "Moon" else list(all_adhi)
    participating_houses = sorted(list(
        ({focal_house} if focal_house > 0 else set())
        | {planet_houses[p] for p in all_adhi if planet_houses.get(p, 0) > 0}
    ))

    return [YogaInstance(
        id=yoga_id,
        name=f"{yoga_name} ({', '.join(archetype_roles)})",
        category=YogaCategory.CONTEXTUAL,
        status=status,
        plausibility_score=final_score,
        participating_planets=participating_planets,
        participating_houses=participating_houses,
        scripture_ref=scripture_ref,
        archetype=(
            f"The Configuration of Command ({focal_label}): Surrounds the {focal_label} focal axis "
            f"with {', '.join(archetype_roles)}."
        ),
        manifestation_effects=[
            "Conquers rivals and commands respect through diplomacy, intellect, and protective grace.",
            f"Command manifest ({pillars_count}/3 pillars): {'; '.join(archetype_roles)}."
        ],
        positive_factors=pos,
        breakers=breakers
    )]


def detect_adhi_yogas(chart: Dict[str, Any]) -> List[YogaInstance]:
    """
    Evaluates Candrādhi Yoga (from Moon) and Lagnādhi Yoga (from Lagna).
    Scripture: Phaladeepika 6.14-15 (6.19-20, 6.42-43), BPHS 37.9-10.
    """
    detected: List[YogaInstance] = []

    moon_house = get_house_of_planet(chart, "Moon")
    if moon_house > 0:
        moon_lon = _extract_focal_longitude(chart, "Moon")
        detected.extend(_evaluate_single_adhi_yoga(
            chart=chart,
            focal_label="Chandra (Moon)",
            focal_target="Moon",
            focal_house=moon_house,
            focal_lon=moon_lon,
            yoga_id="candradhi_yoga",
            yoga_name="Candrādhi Yoga",
            scripture_ref="Phaladeepika 6.14-15, 6.42-43"
        ))

    lagna_sign = get_lagna_sign(chart)
    if lagna_sign and lagna_sign in ZODIAC_SIGNS:
        lagna_lon = _extract_focal_longitude(chart, "Lagna")
        detected.extend(_evaluate_single_adhi_yoga(
            chart=chart,
            focal_label="Lagna (Ascendant)",
            focal_target="Lagna",
            focal_house=1,
            focal_lon=lagna_lon,
            yoga_id="lagnadhi_yoga",
            yoga_name="Lagnādhi Yoga",
            scripture_ref="Phaladeepika 6.14-15, 6.42-43"
        ))

    return detected


def detect_general_scope_yogas(chart: Dict[str, Any]) -> List[YogaInstance]:
    """
    Evaluates the 3 Sun-Moon Quadrant Yogas (Adhama, Sama, Variṣṭha).
    Scripture: Phaladeepika 6.14 & 6.19, BPHS 38.1-3.
    - Kendra (1, 4, 7, 10 from Sun) -> Adhama Yoga (Inferior baseline; mitigated if angular from Lagna or Full Moon in 7th)
    - Panaphara (2, 5, 8, 11 from Sun) -> Sama (Madhya) Yoga (Equal/Moderate baseline)
    - Apoklima (3, 6, 9, 12 from Sun) -> Variṣṭha Yoga (Superior baseline)
    """
    detected: List[YogaInstance] = []
    sun_sign = get_sign_of_planet(chart, "Sun")
    moon_sign = get_sign_of_planet(chart, "Moon")
    sun_house = get_house_of_planet(chart, "Sun")
    moon_house = get_house_of_planet(chart, "Moon")

    if sun_sign in ZODIAC_SIGNS and moon_sign in ZODIAC_SIGNS:
        rel_house = ((ZODIAC_SIGNS.index(moon_sign) - ZODIAC_SIGNS.index(sun_sign)) % 12) + 1
    elif sun_house > 0 and moon_house > 0:
        rel_house = ((moon_house - sun_house) % 12) + 1
    else:
        return detected

    participating_houses = sorted(list({h for h in (sun_house, moon_house) if h > 0}))

    if rel_house in (1, 4, 7, 10):
        is_full_moon = (rel_house == 7)
        is_lagna_kendra = (moon_house in (1, 4, 7, 10)) or (sun_house in (1, 4, 7, 10))
        pos = [f"Moon is in sign/house {rel_house} (Kendra) from the Sun."]
        if is_full_moon:
            pos.append("Moon is in the 7th from the Sun (Pūrṇimā / Full Moon Pakṣabala), mitigating dark-moon friction.")
        if is_lagna_kendra:
            pos.append("Luminaries occupy a Kendra from Lagna, channeling angular tension into visible worldly action.")

        is_mitigated = is_full_moon or is_lagna_kendra
        breakers = [
            YogaBreakerDetail(
                factor="Angular Solar-Lunar Friction (Adhama)",
                culprit_planet="Moon",
                description=(
                    f"Moon is angular ({rel_house}th) from Sun, producing New Moon combustion (1st) "
                    f"or square/opposition stress (4th, 7th, 10th)."
                ),
                penalty=15.0 if is_mitigated else 25.0
            )
        ]
        detected.append(YogaInstance(
            id="adhama_yoga",
            name="Adhama Yoga (Kendra Solar-Lunar Scope)",
            category=YogaCategory.CONTEXTUAL,
            status=YogaStatus.RESCUED if is_mitigated else YogaStatus.STAINED,
            plausibility_score=72.0 if is_mitigated else 65.0,
            participating_planets=["Sun", "Moon"],
            participating_houses=participating_houses,
            scripture_ref="Phaladeepika 6.14, 6.19; BPHS 38.1-3",
            archetype="Moon in Kendra (1, 4, 7, 10) from Sun: Angular solar-lunar friction (0.75 toning multiplier unless anchored in Lagna Kendra).",
            manifestation_effects=[
                "Requires conscious perseverance and grit to materialize wealth and public harmony.",
                "Fosters resilience and self-examination through overcoming ego-emotion tension."
            ],
            positive_factors=pos,
            breakers=breakers
        ))
    elif rel_house in (2, 5, 8, 11):
        detected.append(YogaInstance(
            id="sama_yoga",
            name="Sama (Madhya) Yoga (Paṇaphara Solar-Lunar Scope)",
            category=YogaCategory.CONTEXTUAL,
            status=YogaStatus.PURE,
            plausibility_score=75.0,
            participating_planets=["Sun", "Moon"],
            participating_houses=participating_houses,
            scripture_ref="Phaladeepika 6.14, 6.19; BPHS 38.1-3",
            archetype="Moon in Paṇaphara (2, 5, 8, 11) from Sun: Balanced succedent baseline (1.0 baseline multiplier).",
            manifestation_effects=[
                "Moderate wealth, steady fortune, and predictable returns corresponding to personal effort.",
                "Patience, persistence, and steady mid-life resource consolidation."
            ],
            positive_factors=[f"Moon is in sign/house {rel_house} (Paṇaphara) from the Sun."],
            breakers=[]
        ))
    else:  # 3, 6, 9, 12
        detected.append(YogaInstance(
            id="varishtha_yoga",
            name="Variṣṭha Yoga (Apoklima Solar-Lunar Scope)",
            category=YogaCategory.CONTEXTUAL,
            status=YogaStatus.PURE,
            plausibility_score=85.0,
            participating_planets=["Sun", "Moon"],
            participating_houses=participating_houses,
            scripture_ref="Phaladeepika 6.14, 6.19; BPHS 38.1-3",
            archetype="Moon in Apoklima (3, 6, 9, 12) from Sun: Harmonious cadent expanse (1.25 boost multiplier).",
            manifestation_effects=[
                "Abundant wealth, vehicles, fame, learning, and broad public stature (1.25 boost multiplier).",
                "Multiplies and accelerates the fruits of other positive yogas in the horoscope."
            ],
            positive_factors=[
                f"Moon is in sign/house {rel_house} (Apoklima) from the Sun.",
                "Non-combust, harmonious angle free from harsh square or direct opposition stress."
            ],
            breakers=[]
        ))

    return detected


def detect_mahabhagya_yogas(chart: Dict[str, Any]) -> List[YogaInstance]:
    """
    Evaluates Mahābhāgya Yoga (Supreme Fortune Synergy — Phaladeepika 6.14/6.16, BPHS 38.4-5).
    - Male Native: Day birth + Odd Lagna + Odd Sun + Odd Moon (4/4 = PURE; 3/4 = Partial STAINED).
    - Female Native: Night birth + Even Lagna + Even Sun + Even Moon (4/4 = PURE; 3/4 = Partial STAINED).
    """
    detected: List[YogaInstance] = []
    lagna_sign = get_lagna_sign(chart)
    sun_sign = get_sign_of_planet(chart, "Sun")
    moon_sign = get_sign_of_planet(chart, "Moon")

    if not lagna_sign or not sun_sign or not moon_sign:
        return detected

    sun_house = get_house_of_planet(chart, "Sun")
    moon_house = get_house_of_planet(chart, "Moon")

    is_day_birth = chart.get("is_day_birth")
    if is_day_birth is None and isinstance(chart.get("meta"), dict):
        is_day_birth = chart["meta"].get("is_day_birth")
    if is_day_birth is None and isinstance(chart.get("panchanga"), dict):
        is_day_birth = chart["panchanga"].get("is_day_birth")
    if is_day_birth is None:
        is_day_birth = (sun_house in (7, 8, 9, 10, 11, 12)) if sun_house > 0 else True

    gender = str(chart.get("gender") or (chart.get("meta") or {}).get("gender", "")).strip().lower()
    participating_houses = sorted(list({h for h in (1, sun_house, moon_house) if h > 0}))

    male_factors = {
        "Day Birth": bool(is_day_birth),
        f"Odd Lagna ({lagna_sign})": lagna_sign in ODD_SIGNS,
        f"Odd Sun ({sun_sign})": sun_sign in ODD_SIGNS,
        f"Odd Moon ({moon_sign})": moon_sign in ODD_SIGNS,
    }
    female_factors = {
        "Night Birth": not bool(is_day_birth),
        f"Even Lagna ({lagna_sign})": lagna_sign in EVEN_SIGNS,
        f"Even Sun ({sun_sign})": sun_sign in EVEN_SIGNS,
        f"Even Moon ({moon_sign})": moon_sign in EVEN_SIGNS,
    }

    male_count = sum(1 for v in male_factors.values() if v)
    female_count = sum(1 for v in female_factors.values() if v)

    if male_count == 4 and gender != "female":
        breakers: List[YogaBreakerDetail] = []
        if gender != "male":
            breakers.append(YogaBreakerDetail(
                factor="Unverified Biological Gender",
                culprit_planet="Lagna",
                description="Chart satisfies all 4 masculine polarity factors, but native's biological gender is unspecified.",
                penalty=20.0
            ))
        final_score, status = resolve_yoga_score_and_status(95.0, breakers)
        detected.append(YogaInstance(
            id="mahabhagya_male_yoga",
            name="Mahābhāgya Yoga (Supreme Fortune - Male Configuration)",
            category=YogaCategory.CONTEXTUAL,
            status=status,
            plausibility_score=final_score,
            participating_planets=["Sun", "Moon"],
            participating_houses=participating_houses,
            scripture_ref="Phaladeepika 6.14-16, BPHS 38.4-5",
            archetype="Supreme Fortune through complete solar-masculine congruence: Day birth with Lagna, Sun, and Moon all in active Odd signs.",
            manifestation_effects=[
                "Effortless public authority, natural dignity, and command over large groups.",
                "Strong generosity, high reputation, and widespread societal recognition."
            ],
            positive_factors=[k for k, v in male_factors.items() if v],
            breakers=breakers
        ))

    elif female_count == 4 and gender != "male":
        breakers = []
        if gender != "female":
            breakers.append(YogaBreakerDetail(
                factor="Unverified Biological Gender",
                culprit_planet="Lagna",
                description="Chart satisfies all 4 feminine polarity factors, but native's biological gender is unspecified.",
                penalty=20.0
            ))
        final_score, status = resolve_yoga_score_and_status(95.0, breakers)
        detected.append(YogaInstance(
            id="mahabhagya_female_yoga",
            name="Mahābhāgya Yoga (Supreme Fortune - Female Configuration)",
            category=YogaCategory.CONTEXTUAL,
            status=status,
            plausibility_score=final_score,
            participating_planets=["Sun", "Moon"],
            participating_houses=participating_houses,
            scripture_ref="Phaladeepika 6.14-16, BPHS 38.4-5",
            archetype="Supreme Fortune through complete lunar-feminine congruence: Night birth with Lagna, Sun, and Moon all in receptive Even signs.",
            manifestation_effects=[
                "Deep poise, magnetic grace, and natural harmony within family and community.",
                "Long-lasting prosperity, domestic contentment, and high social respect."
            ],
            positive_factors=[k for k, v in female_factors.items() if v],
            breakers=breakers
        ))

    elif gender == "male" and male_count == 3:
        missing = [k for k, v in male_factors.items() if not v][0]
        breakers = [YogaBreakerDetail(
            factor="Partial Polarity Alignment (3/4 Factors)",
            culprit_planet="Sun" if "Sun" in missing or "Day" in missing else ("Moon" if "Moon" in missing else "Lagna"),
            description=f"3 of 4 masculine Mahābhāgya factors align; missing factor: {missing}.",
            penalty=20.0
        )]
        final_score, status = resolve_yoga_score_and_status(85.0, breakers)
        detected.append(YogaInstance(
            id="mahabhagya_partial_male_yoga",
            name="Partial Mahābhāgya Yoga (3/4 Masculine Synergy)",
            category=YogaCategory.CONTEXTUAL,
            status=status,
            plausibility_score=final_score,
            participating_planets=["Sun", "Moon"],
            participating_houses=participating_houses,
            scripture_ref="Phaladeepika 6.14-16",
            archetype="Substantial masculine polarity synergy (3 of 4 factors aligned), granting strong vitality and charisma.",
            manifestation_effects=[
                "Marked personal confidence and leadership presence, slightly tempered by one receptive polarity factor."
            ],
            positive_factors=[k for k, v in male_factors.items() if v],
            breakers=breakers
        ))

    elif gender == "female" and female_count == 3:
        missing = [k for k, v in female_factors.items() if not v][0]
        breakers = [YogaBreakerDetail(
            factor="Partial Polarity Alignment (3/4 Factors)",
            culprit_planet="Sun" if "Sun" in missing or "Night" in missing else ("Moon" if "Moon" in missing else "Lagna"),
            description=f"3 of 4 feminine Mahābhāgya factors align; missing factor: {missing}.",
            penalty=20.0
        )]
        final_score, status = resolve_yoga_score_and_status(85.0, breakers)
        detected.append(YogaInstance(
            id="mahabhagya_partial_female_yoga",
            name="Partial Mahābhāgya Yoga (3/4 Feminine Synergy)",
            category=YogaCategory.CONTEXTUAL,
            status=status,
            plausibility_score=final_score,
            participating_planets=["Sun", "Moon"],
            participating_houses=participating_houses,
            scripture_ref="Phaladeepika 6.14-16",
            archetype="Substantial feminine polarity synergy (3 of 4 factors aligned), granting poise and magnetic charm.",
            manifestation_effects=[
                "Strong intuitive grace and social magnetism, blended with one assertive masculine factor."
            ],
            positive_factors=[k for k, v in female_factors.items() if v],
            breakers=breakers
        ))

    return detected


def detect_solitary_first_house_yogas(chart: Dict[str, Any]) -> List[YogaInstance]:
    """
    Evaluates Solitary 1st House Occupancy (Śubha Tanu & Aśubha Tanu).
    Note: Lagna Kartarī is evaluated exclusively in jyotish/yogas/kartari.py.
    """
    detected: List[YogaInstance] = []
    planets_data = get_planets_data(chart)
    planet_houses = {p: get_house_of_planet(chart, p) for p in planets_data}

    h1_planets = [
        p for p in CLASSICAL_7_GRAHAS + ["Rahu", "Ketu"]
        if p in planets_data and planet_houses.get(p) == 1
    ]

    if h1_planets == ["Mars"]:
        detected.append(YogaInstance(
            id="solitary_mars_tanu_yoga",
            name="Solitary Mars in 1st House (Aśubha Fortitude)",
            category=YogaCategory.CONTEXTUAL,
            status=YogaStatus.STAINED,
            plausibility_score=70.0,
            participating_planets=["Mars"],
            participating_houses=[1],
            scripture_ref="BPHS Ch. 12 & 34",
            archetype="Mars stands alone in the 1st House, imparting formidable physical grit, sharp courage, and fierce independence.",
            manifestation_effects=[
                "Extreme physical resilience, athletic capacity, and warrior-like constitution.",
                "Fierce independence, intolerance for condescension, and quick temper."
            ],
            positive_factors=["Unyielding courage and physical stamina."],
            breakers=[YogaBreakerDetail(
                factor="Solitary Malefic in Ascendant",
                culprit_planet="Mars",
                description="Mars alone in 1st Bhava increases combative friction and headstrong impulsiveness.",
                penalty=15.0
            )]
        ))

    elif h1_planets == ["Saturn"]:
        detected.append(YogaInstance(
            id="solitary_saturn_tanu_yoga",
            name="Solitary Saturn in 1st House (Stoic Resilience)",
            category=YogaCategory.CONTEXTUAL,
            status=YogaStatus.STAINED,
            plausibility_score=70.0,
            participating_planets=["Saturn"],
            participating_houses=[1],
            scripture_ref="BPHS Ch. 12 & 34",
            archetype="Saturn stands alone in the 1st House, forging a stoic, disciplined, and sober personality through early self-reliance.",
            manifestation_effects=[
                "Deep patience, mature gravity from an early age, and realistic life expectations.",
                "Lifelong perseverance and ability to endure prolonged solitary toil."
            ],
            positive_factors=["Enduring discipline and grounded realism."],
            breakers=[YogaBreakerDetail(
                factor="Solitary Malefic in Ascendant",
                culprit_planet="Saturn",
                description="Saturn alone in 1st Bhava creates solemn hesitation and heavy emotional self-containment.",
                penalty=15.0
            )]
        ))

    elif len(h1_planets) == 1 and h1_planets[0] in NATURAL_BENEFICS:
        ben = h1_planets[0]
        breakers: List[YogaBreakerDetail] = []
        breakers.extend(audit_combustion([ben], chart))
        sb_breakers, sb_pos = audit_shadbala_muscle([ben], chart)
        breakers.extend(sb_breakers)
        final_score, status = resolve_yoga_score_and_status(90.0, breakers)
        detected.append(YogaInstance(
            id=f"solitary_{ben.lower()}_tanu_yoga",
            name=f"Solitary {ben} in 1st House (Śubha Tanu)",
            category=YogaCategory.CONTEXTUAL,
            status=status,
            plausibility_score=final_score,
            participating_planets=[ben],
            participating_houses=[1],
            scripture_ref="BPHS Ch. 12 & 37 (Chāmarā & Śubha Lagna)",
            archetype=f"A solitary natural benefic ({ben}) blesses the Ascendant, radiating charm, benevolence, and natural social protection.",
            manifestation_effects=[
                "Pleasing personal demeanor, gracious communication, and natural charisma.",
                "Strong protection against severe bodily harm and chronic disgrace."
            ],
            positive_factors=[f"{ben} occupying 1st house without disruptive co-occupants."] + sb_pos,
            breakers=breakers
        ))

    return detected


def detect_dual_lagna_raja_yogas(chart: Dict[str, Any]) -> List[YogaInstance]:
    """
    Evaluates Dual-Lagna Raja Yoga (Ubhayalagna Synchrony).
    Validates classical Kendra-Koṇa lord combinations operating simultaneously
    from both Janma Lagna and Candra Lagna without duplicate emissions.
    """
    detected: List[YogaInstance] = []
    lagna_sign = get_lagna_sign(chart)
    moon_sign = get_sign_of_planet(chart, "Moon")

    if not lagna_sign or not moon_sign or lagna_sign not in ZODIAC_SIGNS or moon_sign not in ZODIAC_SIGNS:
        return detected

    l_idx = ZODIAC_SIGNS.index(lagna_sign)
    lagna_rulers: Dict[int, str] = {
        h: SIGN_LORDS[ZODIAC_SIGNS[(l_idx + h - 1) % 12]] for h in range(1, 13)
    }

    m_idx = ZODIAC_SIGNS.index(moon_sign)
    candra_rulers: Dict[int, str] = {
        h: SIGN_LORDS[ZODIAC_SIGNS[(m_idx + h - 1) % 12]] for h in range(1, 13)
    }

    KEY_PAIRS: List[Tuple[int, int]] = [
        (9, 10), (4, 9), (5, 10), (4, 5), (5, 7), (7, 9), (1, 9), (1, 5), (1, 4), (1, 10)
    ]

    lagna_pair_map: Dict[frozenset, List[str]] = {}
    for kh, knh in KEY_PAIRS:
        pair = frozenset({lagna_rulers[kh], lagna_rulers[knh]})
        if len(pair) == 2:
            lagna_pair_map.setdefault(pair, []).append(f"H{kh}+H{knh}")

    candra_pair_map: Dict[frozenset, List[str]] = {}
    for kh, knh in KEY_PAIRS:
        pair = frozenset({candra_rulers[kh], candra_rulers[knh]})
        if len(pair) == 2:
            candra_pair_map.setdefault(pair, []).append(f"H{kh}+H{knh}")

    common_pairs = set(lagna_pair_map.keys()) & set(candra_pair_map.keys())

    for pair in sorted(common_pairs, key=lambda s: sorted(list(s))):
        p1, p2 = sorted(list(pair))
        sign1 = get_sign_of_planet(chart, p1)
        sign2 = get_sign_of_planet(chart, p2)
        h1 = get_house_of_planet(chart, p1)
        h2 = get_house_of_planet(chart, p2)

        is_conjunct = bool(sign1 and sign2 and sign1 == sign2)
        asp_12 = get_aspect_score(chart, p1, p2)
        asp_21 = get_aspect_score(chart, p2, p1)
        is_mutual_aspect = (asp_12 >= ASPECT_PALPABLE_THRESHOLD and asp_21 >= ASPECT_PALPABLE_THRESHOLD)

        if not (is_conjunct or is_mutual_aspect):
            continue

        houses = sorted(list({h for h in (h1, h2) if h > 0}))
        breakers: List[YogaBreakerDetail] = []
        breakers.extend(audit_trishadaya_interference([p1, p2], chart))
        dust_brk = audit_dusthana_placement(houses, "Ubhayalagna Raja")
        if dust_brk:
            breakers.append(dust_brk)
        breakers.extend(audit_combustion([p1, p2], chart))
        sb_breakers, sb_pos = audit_shadbala_muscle([p1, p2], chart)
        breakers.extend(sb_breakers)

        final_score, status = resolve_yoga_score_and_status(95.0, breakers)

        link_desc = f"conjunct in {sign1}" if is_conjunct else f"in mutual palpable aspect ({asp_12:.0f}V / {asp_21:.0f}V)"
        detected.append(YogaInstance(
            id=f"ubhayalagna_raja_yoga_{p1.lower()}_{p2.lower()}",
            name=f"Ubhayalagna Rāja Yoga ({p1} + {p2})",
            category=YogaCategory.CONTEXTUAL,
            status=status,
            plausibility_score=final_score,
            participating_planets=[p1, p2],
            participating_houses=houses,
            scripture_ref="BPHS Ch. 34 (Raja Yoga Phala) & Ch. 37",
            archetype=f"Supreme Dual-Lagna Sovereign Synergy: {p1} and {p2} form a Kendra-Koṇa Rāja Yoga simultaneously from both Janma Lagna and Candra Lagna.",
            manifestation_effects=[
                "External achievement and internal emotional fulfillment operate in harmonic lockstep.",
                "Outer worldly accomplishments bring genuine satisfaction to the mind."
            ],
            positive_factors=[
                f"{p1} and {p2} are {link_desc}.",
                f"Rules Kendra/Koṇa from Lagna ({', '.join(lagna_pair_map[pair])}) and Candra Lagna ({', '.join(candra_pair_map[pair])})."
            ] + sb_pos,
            breakers=breakers
        ))

    return detected


# Backward compatibility aliases pointing to lunar_solar_yogas
def detect_kemadruma_yoga(chart: Dict[str, Any]) -> List[YogaInstance]:
    """Backward compatibility alias: Kemadruma is canonically computed in lunar_solar_yogas.py."""
    from jyotish.yogas.lunar_solar_yogas import detect_lunar_and_solar_yogas
    return [y for y in detect_lunar_and_solar_yogas(chart) if "kemadruma" in y.id]


def detect_solar_flanking_yogas(chart: Dict[str, Any]) -> List[YogaInstance]:
    """Backward compatibility alias: Solar flanking is canonically computed in lunar_solar_yogas.py."""
    from jyotish.yogas.lunar_solar_yogas import detect_lunar_and_solar_yogas
    return [
        y for y in detect_lunar_and_solar_yogas(chart)
        if y.id in ("vesi_yoga", "vosi_yoga", "ubhayachari_yoga", "ubhayacari_yoga")
    ]


def detect_contextual_yogas(chart: Dict[str, Any]) -> List[YogaInstance]:
    """
    Master orchestrator for Contextual Setup Yogas:
    1. Sāṅkhya Yogas (7 yogas — zero Layer 2 breakers)
    2. Candrādhi & Lagnādhi Yogas (2 yogas — 'OR' graded + continuous Sphuṭa Dṛṣṭi)
    3. General Scope Yogas (Adhama, Sama, Variṣṭha — 3 yogas)
    4. Mahābhāgya Yoga (Full 4/4 & Partial 3/4 Male/Female configurations)
    5. Solitary 1st House Yogas (Śubha & Aśubha Tanu)
    6. Dual-Lagna Rāja Yoga (Ubhayalagna Synchrony)
    """
    all_contextual: List[YogaInstance] = []
    all_contextual.extend(detect_sankhya_yogas(chart))
    all_contextual.extend(detect_adhi_yogas(chart))
    all_contextual.extend(detect_general_scope_yogas(chart))
    all_contextual.extend(detect_mahabhagya_yogas(chart))
    all_contextual.extend(detect_solitary_first_house_yogas(chart))
    all_contextual.extend(detect_dual_lagna_raja_yogas(chart))
    return all_contextual
