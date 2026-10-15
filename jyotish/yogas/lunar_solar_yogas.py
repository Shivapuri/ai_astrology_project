"""
jyotish/yogas/lunar_solar_yogas.py
Lunar (Chandra) and Solar (Ravi) Yogas (Hemisphere A: Pure Foundational Calculus).

Scripture: Phaladeepika Ch. 6 (Verses 5-13), BPHS Ch. 37-38.
Architecture: Strictly adheres to YOGA_ARCHITECTURE.md Categories 8 (LUNAR) & 9 (SOLAR).

Evaluates:
1. Lunar Flanking & Isolation Yogas:
   - Sunaphā (2nd from Moon), Anaphā (12th from Moon), Durudharā (both 2nd & 12th from Moon)
     * Strictly restricted to the 5 starry planets (Mars, Mercury, Jupiter, Venus, Saturn) — Sun, Rahu, Ketu excluded.
     * Audits combustion, dispositor vitality, and Shadbala on flanking planets.
   - Kemadruma Yoga & 4-Tier Bhaṅga Hierarchy:
     * Tier 1: Physical planets in Kendra (1, 4, 7, 10) from Moon.
     * Tier 2: Moon in Kendra (1, 4, 7, 10) from Lagna.
     * Tier 3: Sign Modality / Quadruplicity (Chatuṣṭaya) alignment between Lagna and Moon.
     * Tier 4: Physical planets in Kendra from Moon in D9 Navāṃśa.
     * Affliction status invariant: STAINED when active, RESCUED when cancelled — NEVER PURE.
   - Candra-Maṅgala Yoga (Moon + Mars conjunction or aspect).
2. Solar Flanking & Illumination Yogas:
   - Budhāditya Yoga (Sun + Mercury; uses audit_combustion(..., deep_only=True) so only < 3.0° penalizes).
   - Veśi (2nd from Sun), Vāsi/Vośi (12th from Sun), Ubhayacarī (both 2nd & 12th from Sun)
     * Strictly restricted to the 5 starry planets (Mars, Mercury, Jupiter, Venus, Saturn) — Moon, Rahu, Ketu excluded.
     * Audits deep combustion (< 3.0°), dispositor vitality, and Shadbala.
"""

from typing import List, Dict, Any, Tuple
from jyotish.yogas.models import (
    YogaInstance, YogaCategory, YogaStatus, YogaBreakerDetail
)
from jyotish.yogas.breakers import (
    get_lagna_sign, get_house_of_planet, get_sign_of_planet, get_planets_data,
    get_aspect_score, resolve_yoga_score_and_status,
    NATURAL_BENEFICS, NATURAL_MALEFICS, ZODIAC_SIGNS,
    audit_trishadaya_interference, audit_combustion, audit_dispositor_vitality,
    audit_dusthana_placement, audit_shadbala_muscle,
    ASPECT_PALPABLE_THRESHOLD, ASPECT_MARGINAL_THRESHOLD
)

# Strictly the 5 non-luminary physical planets (Sun, Moon, Rahu, Ketu excluded)
FIVE_STARRY_GRAHAS: Tuple[str, ...] = ("Mars", "Mercury", "Jupiter", "Venus", "Saturn")


def _audit_lunar_flankers(
    flankers: List[str],
    chart: Dict[str, Any],
    base_score: float,
) -> Tuple[float, YogaStatus, List[str], List[YogaBreakerDetail]]:
    """
    Applies Category 8 (LUNAR) Layer 2 breakers to 2nd/12th lunar flanking planets:
    - Benefic vs. Malefic flavor modulation
    - audit_combustion(flankers, chart)
    - audit_dispositor_vitality(flankers, chart)
    - audit_shadbala_muscle(flankers, chart)
    """
    benefics = [p for p in flankers if p in NATURAL_BENEFICS]
    malefics = [p for p in flankers if p in NATURAL_MALEFICS]

    score = base_score
    pos: List[str] = []
    breakers: List[YogaBreakerDetail] = []

    if benefics:
        pos.append(f"Natural benefics flanking ({', '.join(benefics)}) bestow refinement, generosity, and smooth prosperity.")
        score += 8.0
    if malefics:
        breakers.append(YogaBreakerDetail(
            factor="Malefics Flanking Moon",
            culprit_planet=", ".join(malefics),
            description=f"Natural malefics ({', '.join(malefics)}) in 2nd/12th from Moon add hard-edged grit and emotional friction.",
            penalty=15.0 if benefics else 20.0
        ))

    breakers.extend(audit_combustion(flankers, chart))
    breakers.extend(audit_dispositor_vitality(flankers, chart))
    sb_breakers, sb_pos = audit_shadbala_muscle(flankers, chart)
    breakers.extend(sb_breakers)
    pos.extend(sb_pos)

    final_score, status = resolve_yoga_score_and_status(score, breakers)
    return final_score, status, pos, breakers


def _audit_solar_flankers(
    flankers: List[str],
    chart: Dict[str, Any],
    base_score: float,
) -> Tuple[str, float, YogaStatus, List[str], List[YogaBreakerDetail]]:
    """
    Applies Category 9 (SOLAR) Layer 2 breakers to 2nd/12th solar flanking planets:
    - Distinguishes Śubha (benefic), Pāpa (malefic -> STAINED), and Miśra (mixed) flavors (Phaladeepika 6.8-13).
    - audit_combustion(flankers, chart, deep_only=True) (< 3.0° only).
    - audit_dispositor_vitality(flankers, chart).
    - audit_shadbala_muscle(flankers, chart).
    """
    benefics = [p for p in flankers if p in NATURAL_BENEFICS]
    malefics = [p for p in flankers if p in NATURAL_MALEFICS]

    score = base_score
    pos: List[str] = []
    breakers: List[YogaBreakerDetail] = []

    if benefics and not malefics:
        prefix = "Śubha-"
        pos.append(f"Pure natural benefics ({', '.join(benefics)}) flanking the Sun bestow eloquence, nobility, and royal favor.")
        score += 5.0
    elif malefics and not benefics:
        prefix = "Pāpa-"
        breakers.append(YogaBreakerDetail(
            factor="Pāpa Solar Flanking (Malefic Neighbors)",
            culprit_planet=", ".join(malefics),
            description=f"Malefics ({', '.join(malefics)}) flanking the Sun create harshness, dampened splendor, or competitive friction (Phaladeepika 6.12).",
            penalty=20.0
        ))
    else:
        prefix = "Miśra-"
        pos.append(f"Mixed benefics ({', '.join(benefics)}) and malefics ({', '.join(malefics)}) flanking the Sun grant versatile executive grit.")
        breakers.append(YogaBreakerDetail(
            factor="Mixed Malefic Solar Flanking",
            culprit_planet=", ".join(malefics),
            description=f"Co-flanking malefics ({', '.join(malefics)}) introduce competitive strain alongside benefic support.",
            penalty=10.0
        ))

    # Category 9 Rule: deep_only=True (< 3.0° only) so normal solar proximity (3.0°–8.0°) is NOT penalized
    breakers.extend(audit_combustion(flankers, chart, deep_only=True))
    breakers.extend(audit_dispositor_vitality(flankers, chart))
    sb_breakers, sb_pos = audit_shadbala_muscle(flankers, chart)
    breakers.extend(sb_breakers)
    pos.extend(sb_pos)

    final_score, status = resolve_yoga_score_and_status(score, breakers)
    if prefix == "Pāpa-" and status == YogaStatus.PURE:
        status = YogaStatus.STAINED

    return prefix, final_score, status, pos, breakers


def detect_lunar_and_solar_yogas(chart: Dict[str, Any]) -> List[YogaInstance]:
    """Scans chart for classical Lunar (Category 8) and Solar (Category 9) yogas."""
    detected: List[YogaInstance] = []
    planets_data = get_planets_data(chart)
    planet_houses = {p: get_house_of_planet(chart, p) for p in planets_data}

    moon_house = planet_houses.get("Moon", 0)
    sun_house = planet_houses.get("Sun", 0)

    # -------------------------------------------------------------
    # 1. LUNAR YOGAS (CHANDRA YOGAS — Category 8)
    # -------------------------------------------------------------
    if moon_house > 0:
        h2_moon = (moon_house % 12) + 1
        h12_moon = ((moon_house - 2) % 12) + 1

        # Strictly whitelist the 5 starry planets (Sun, Rahu, Ketu, Moon excluded)
        planets_in_h2 = [
            p for p in FIVE_STARRY_GRAHAS
            if p in planets_data and planet_houses.get(p) == h2_moon
        ]
        planets_in_h12 = [
            p for p in FIVE_STARRY_GRAHAS
            if p in planets_data and planet_houses.get(p) == h12_moon
        ]

        # A1. Durudharā Yoga (Both 2nd and 12th from Moon occupied)
        if planets_in_h2 and planets_in_h12:
            flankers = planets_in_h2 + planets_in_h12
            final_score, status, pos, breakers = _audit_lunar_flankers(flankers, chart, 85.0)
            pos.insert(0, f"Planets flank Moon in 2nd ({', '.join(planets_in_h2)}) and 12th ({', '.join(planets_in_h12)}).")

            detected.append(YogaInstance(
                id="durudhara_yoga",
                name="Durudharā Yoga",
                category=YogaCategory.LUNAR,
                status=status,
                plausibility_score=final_score,
                participating_planets=["Moon"] + flankers,
                participating_houses=sorted(list({moon_house, h2_moon, h12_moon})),
                scripture_ref="Phaladeepika 6.5-7, BPHS 37.1-2",
                archetype="The Emotionally Anchored Mind: Flanked by resources (2nd) and philosophical perspective (12th).",
                manifestation_effects=[
                    "Endows material comfort, reliable helpers (Sadbhṛtya), generous disposition, and verbal eloquence.",
                    "Enjoyment of vehicles, landed property, and consistent resource acquisition."
                ],
                positive_factors=pos,
                breakers=breakers
            ))

        # A2. Sunaphā Yoga (Only 2nd from Moon occupied)
        elif planets_in_h2:
            final_score, status, pos, breakers = _audit_lunar_flankers(planets_in_h2, chart, 80.0)
            pos.insert(0, f"Planets in 2nd from Moon: {', '.join(planets_in_h2)}.")

            detected.append(YogaInstance(
                id="sunapha_yoga",
                name="Sunaphā Yoga",
                category=YogaCategory.LUNAR,
                status=status,
                plausibility_score=final_score,
                participating_planets=["Moon"] + planets_in_h2,
                participating_houses=sorted(list({moon_house, h2_moon})),
                scripture_ref="Phaladeepika 6.5, BPHS 37.1",
                archetype="Resourceful Mind: Planets in the 2nd from the Moon provide self-made wealth and steady earnings.",
                manifestation_effects=[
                    "Self-made prosperity (Svabhujārjita-vitta), intelligent speech, and comfortable livelihood."
                ],
                positive_factors=pos,
                breakers=breakers
            ))

        # A3. Anaphā Yoga (Only 12th from Moon occupied)
        elif planets_in_h12:
            final_score, status, pos, breakers = _audit_lunar_flankers(planets_in_h12, chart, 80.0)
            pos.insert(0, f"Planets in 12th from Moon: {', '.join(planets_in_h12)}.")

            detected.append(YogaInstance(
                id="anapha_yoga",
                name="Anaphā Yoga",
                category=YogaCategory.LUNAR,
                status=status,
                plausibility_score=final_score,
                participating_planets=["Moon"] + planets_in_h12,
                participating_houses=sorted(list({moon_house, h12_moon})),
                scripture_ref="Phaladeepika 6.6, BPHS 37.1",
                archetype="Refined & Carefree Mind: Planets in the 12th from the Moon bestow dignity, health, and inner poise.",
                manifestation_effects=[
                    "Refined conduct (Śīlavān), physical vitality, sensory enjoyment, and moral contentment."
                ],
                positive_factors=pos,
                breakers=breakers
            ))

        # A4. Kemadruma Yoga & 4-Tier Bhaṅga Hierarchy (Neither 2nd nor 12th occupied)
        else:
            lagna_sign_cur = get_lagna_sign(chart)
            moon_sign_cur = get_sign_of_planet(chart, "Moon")

            CARDINAL_SIGNS = {"Aries", "Cancer", "Libra", "Capricorn"}
            FIXED_SIGNS = {"Taurus", "Leo", "Scorpio", "Aquarius"}
            DUAL_SIGNS = {"Gemini", "Virgo", "Sagittarius", "Pisces"}

            # Tier 1: Physical planets (Mars, Mercury, Jupiter, Venus, Saturn) in Kendra from Moon
            kendra_planets_moon = [
                p for p in FIVE_STARRY_GRAHAS
                if p in planets_data
                and planet_houses.get(p, 0) > 0
                and ((planet_houses[p] - moon_house) % 12 + 1) in (1, 4, 7, 10)
            ]

            # Tier 2: Moon itself occupying Kendra (1, 4, 7, 10) from Lagna
            moon_in_lagna_kendra = moon_house in (1, 4, 7, 10)

            # Tier 3: Sign Modality / Quadruplicity (Chatuṣṭaya) alignment between Lagna and Moon
            same_modality = bool(lagna_sign_cur and moon_sign_cur) and (
                (lagna_sign_cur in CARDINAL_SIGNS and moon_sign_cur in CARDINAL_SIGNS) or
                (lagna_sign_cur in FIXED_SIGNS and moon_sign_cur in FIXED_SIGNS) or
                (lagna_sign_cur in DUAL_SIGNS and moon_sign_cur in DUAL_SIGNS)
            )

            # Tier 4: Classical physical planets in Kendra from Moon in Navāṃśa (D9)
            d9_block = (chart.get("vargas") or {}).get("D9") or chart.get("D9") or chart.get("d9") or {}
            d9_grahas = d9_block.get("grahas") or d9_block.get("planets") or {}
            moon_d9_sign = (d9_grahas.get("Moon") or {}).get("sign", "")
            d9_kendra_planets: List[str] = []
            if moon_d9_sign in ZODIAC_SIGNS:
                m_d9_idx = ZODIAC_SIGNS.index(moon_d9_sign)
                for p in FIVE_STARRY_GRAHAS:
                    p_d9_sign = (d9_grahas.get(p) or {}).get("sign", "")
                    if p_d9_sign in ZODIAC_SIGNS:
                        diff_d9 = ((ZODIAC_SIGNS.index(p_d9_sign) - m_d9_idx) % 12) + 1
                        if diff_d9 in (1, 4, 7, 10):
                            d9_kendra_planets.append(p)

            cancellation_reasons: List[str] = []
            if kendra_planets_moon:
                cancellation_reasons.append(
                    f"Tier 1 Lunar Kendra: Rescued by physical planets in Kendra from Chandra ({', '.join(kendra_planets_moon)})."
                )
            if moon_in_lagna_kendra:
                cancellation_reasons.append(
                    f"Tier 2 Lagna Kendra: Rescued by Moon itself occupying Kendra House {moon_house} from Lagna."
                )
            if same_modality:
                cancellation_reasons.append(
                    f"Tier 3 Modality Alignment: Rescued by Ascendant ({lagna_sign_cur}) and Moon ({moon_sign_cur}) sharing the same quadruplicity (Chatuṣṭaya)."
                )
            if d9_kendra_planets:
                cancellation_reasons.append(
                    f"Tier 4 Navāṃśa Kendra: Rescued by planets in Kendra from Moon in D9 ({', '.join(d9_kendra_planets)})."
                )

            is_cancelled = bool(cancellation_reasons)
            # Affliction Yoga Invariant: STAINED when active/unmitigated; RESCUED when cancelled — NEVER PURE!
            status = YogaStatus.RESCUED if is_cancelled else YogaStatus.STAINED
            score = max(40.0, 75.0 - 10.0 * len(cancellation_reasons)) if is_cancelled else 80.0

            participating_planets: List[str] = ["Moon"]
            for p in kendra_planets_moon + d9_kendra_planets:
                if p not in participating_planets:
                    participating_planets.append(p)

            participating_houses = sorted(list(
                {moon_house} | {planet_houses[p] for p in kendra_planets_moon if planet_houses.get(p, 0) > 0}
            ))

            breakers = [YogaBreakerDetail(
                factor="Moon Isolation (No 2nd/12th Flanking Planets)",
                culprit_planet="Moon",
                description="No physical planets reside in 2nd or 12th from the Moon, creating subjective feelings of emotional solitude.",
                penalty=25.0 if is_cancelled else 50.0
            )]

            detected.append(YogaInstance(
                id="kemadruma_yoga",
                name="Kemadruma Yoga" + (" (Rescued / Bhaṅga)" if is_cancelled else ""),
                category=YogaCategory.LUNAR,
                status=status,
                plausibility_score=round(score, 1),
                participating_planets=participating_planets,
                participating_houses=participating_houses,
                scripture_ref="Phaladeepika 6.7, BPHS 37.11-16",
                archetype="The Solitary Mind: Moon sits without immediate 2nd/12th flanking planets.",
                manifestation_effects=[
                    "Feelings of psychological isolation, melancholy, or having to fend for oneself without external cushioning."
                    if not is_cancelled else
                    "Initial emotional solitude is rescued and transformed into deep self-reliance through angular Kendra support."
                ],
                positive_factors=cancellation_reasons,
                breakers=breakers
            ))

        # B. Candra-Maṅgala Yoga (Moon + Mars)
        mars_house = planet_houses.get("Mars", 0)
        if mars_house > 0:
            is_cm_conj = (mars_house == moon_house)
            aspect_mm = max(
                get_aspect_score(chart, "Mars", "Moon"),
                get_aspect_score(chart, "Moon", "Mars")
            )
            is_cm_aspect = aspect_mm >= ASPECT_PALPABLE_THRESHOLD
            is_cm_marginal = (not is_cm_conj) and (not is_cm_aspect) and (aspect_mm >= ASPECT_MARGINAL_THRESHOLD)

            if is_cm_conj or is_cm_aspect or is_cm_marginal:
                score = 80.0
                pos = [
                    f"Moon and Mars combine (House {moon_house})"
                    if is_cm_conj else
                    f"Moon and Mars link via {aspect_mm:.1f} Virūpa aspect."
                ]
                breakers = []
                if is_cm_marginal:
                    breakers.append(YogaBreakerDetail(
                        factor="Marginal Aspect Connection",
                        culprit_planet="Mars",
                        description=f"Aspect strength ({aspect_mm:.1f} Virūpas) is below the palpable 45.0 Virūpa threshold.",
                        penalty=25.0
                    ))
                breakers.extend(audit_trishadaya_interference(["Moon", "Mars"], chart))
                breakers.extend(audit_combustion(["Mars"], chart))
                breakers.extend(audit_dispositor_vitality(["Moon", "Mars"], chart))
                sb_breakers, sb_pos = audit_shadbala_muscle(["Moon", "Mars"], chart)
                breakers.extend(sb_breakers)
                pos.extend(sb_pos)

                final_score, status = resolve_yoga_score_and_status(score, breakers)

                detected.append(YogaInstance(
                    id="chandra_mangala_yoga",
                    name="Candra-Maṅgala Yoga",
                    category=YogaCategory.LUNAR,
                    status=status,
                    plausibility_score=final_score,
                    participating_planets=["Moon", "Mars"],
                    participating_houses=sorted(list({moon_house, mars_house})),
                    scripture_ref="BPHS 37.8, Phaladeepika 6.20",
                    archetype="Energetic Enterprise & Vigor: Unites the feeling mind with Martian drive, fostering commercial hustle.",
                    manifestation_effects=[
                        "Strong commercial acumen, financial enterprise, and capacity to generate liquid assets.",
                        "Dynamic emotional drive, though can produce occasional impatience or emotional heat."
                    ],
                    positive_factors=pos,
                    breakers=breakers
                ))

    # -------------------------------------------------------------
    # 2. SOLAR YOGAS (RAVI YOGAS — Category 9)
    # -------------------------------------------------------------
    if sun_house > 0:
        # A. Budhāditya Yoga (Sun + Mercury)
        merc_house = get_house_of_planet(chart, "Mercury")
        if merc_house == sun_house and "Mercury" in planets_data:
            score = 85.0
            pos = [f"Sun and Mercury conjoined in House {sun_house}."]
            breakers = []

            sun_lon = (planets_data.get("Sun") or {}).get("longitude")
            merc_lon = (planets_data.get("Mercury") or {}).get("longitude")
            if sun_lon is not None and merc_lon is not None:
                try:
                    dist = abs(float(merc_lon) - float(sun_lon)) % 360.0
                    if dist > 180.0:
                        dist = 360.0 - dist
                    pos[0] = f"Sun and Mercury conjoined in House {sun_house} (Separation: {dist:.1f}°)."
                    if 3.0 <= dist <= 14.0:
                        pos.append("Optimal illumination orb (3.0°–14.0°): Mercury absorbs solar brilliance without deep incineration.")
                        score += 5.0
                except (TypeError, ValueError):
                    pass

            # Category 9 Rule: audit_combustion(..., deep_only=True) (< 3.0° only)
            breakers.extend(audit_combustion(["Mercury"], chart, deep_only=True))
            dust_brk = audit_dusthana_placement([sun_house], "Budhaditya")
            if dust_brk:
                breakers.append(dust_brk)
            breakers.extend(audit_dispositor_vitality(["Sun", "Mercury"], chart))
            sb_breakers, sb_pos = audit_shadbala_muscle(["Sun", "Mercury"], chart)
            breakers.extend(sb_breakers)
            pos.extend(sb_pos)

            final_score, status = resolve_yoga_score_and_status(score, breakers)

            detected.append(YogaInstance(
                id="budhaditya_yoga",
                name="Budhāditya Yoga",
                category=YogaCategory.SOLAR,
                status=status,
                plausibility_score=final_score,
                participating_planets=["Sun", "Mercury"],
                participating_houses=[sun_house],
                scripture_ref="BPHS 38.1, Phaladeepika 6.8",
                archetype="The Solar Intellect: The Sun's soul-force illuminates Mercury's analytical brilliance.",
                manifestation_effects=[
                    "High intelligence, administrative tact, verbal eloquence, and scholarly distinction.",
                    "Respected in scientific, governmental, or educational circles."
                ],
                positive_factors=pos,
                breakers=breakers
            ))

        # B. Veśi, Vāsi (Vośi), and Ubhayacarī Yogas
        h2_sun = (sun_house % 12) + 1
        h12_sun = ((sun_house - 2) % 12) + 1

        # Strictly whitelist the 5 starry planets (Moon, Rahu, Ketu, Sun excluded)
        planets_in_h2_s = [
            p for p in FIVE_STARRY_GRAHAS
            if p in planets_data and planet_houses.get(p) == h2_sun
        ]
        planets_in_h12_s = [
            p for p in FIVE_STARRY_GRAHAS
            if p in planets_data and planet_houses.get(p) == h12_sun
        ]

        if planets_in_h2_s and planets_in_h12_s:
            flankers_s = planets_in_h2_s + planets_in_h12_s
            prefix, final_score, status, pos, breakers = _audit_solar_flankers(flankers_s, chart, 85.0)
            pos.insert(0, f"Flanked in 2nd ({', '.join(planets_in_h2_s)}) and 12th ({', '.join(planets_in_h12_s)}) from Sun.")

            detected.append(YogaInstance(
                id="ubhayacari_yoga",
                name=f"{prefix}Ubhayacarī Yoga",
                category=YogaCategory.SOLAR,
                status=status,
                plausibility_score=final_score,
                participating_planets=["Sun"] + flankers_s,
                participating_houses=sorted(list({h12_sun, sun_house, h2_sun})),
                scripture_ref="Phaladeepika 6.10, BPHS 38.4",
                archetype="Balanced Solar Aura: Planets flank both sides of the Sun, conferring executive poise and royal presence.",
                manifestation_effects=[
                    "Balanced personality, broad organizational capability, articulateness, and public stature."
                ],
                positive_factors=pos,
                breakers=breakers
            ))

        elif planets_in_h2_s:
            prefix, final_score, status, pos, breakers = _audit_solar_flankers(planets_in_h2_s, chart, 80.0)
            pos.insert(0, f"Planets in 2nd from Sun: {', '.join(planets_in_h2_s)}.")

            detected.append(YogaInstance(
                id="vesi_yoga",
                name=f"{prefix}Veśi Yoga",
                category=YogaCategory.SOLAR,
                status=status,
                plausibility_score=final_score,
                participating_planets=["Sun"] + planets_in_h2_s,
                participating_houses=sorted(list({sun_house, h2_sun})),
                scripture_ref="Phaladeepika 6.8, BPHS 38.2",
                archetype="Articulate Solar Expression: Planets in 2nd from Sun channel solar authority into speech and tangible resources.",
                manifestation_effects=[
                    "Steady memory, articulate communication, and tangible financial execution."
                ],
                positive_factors=pos,
                breakers=breakers
            ))

        elif planets_in_h12_s:
            prefix, final_score, status, pos, breakers = _audit_solar_flankers(planets_in_h12_s, chart, 80.0)
            pos.insert(0, f"Planets in 12th from Sun: {', '.join(planets_in_h12_s)}.")

            detected.append(YogaInstance(
                id="vosi_yoga",
                name=f"{prefix}Vāsi (Vośi) Yoga",
                category=YogaCategory.SOLAR,
                status=status,
                plausibility_score=final_score,
                participating_planets=["Sun"] + planets_in_h12_s,
                participating_houses=sorted(list({h12_sun, sun_house})),
                scripture_ref="Phaladeepika 6.9, BPHS 38.3",
                archetype="Charitable Solar Vision: Planets in 12th from Sun bestow philosophical foresight and strategic wisdom.",
                manifestation_effects=[
                    "Charitable nature, contemplative learning, and broad reputation."
                ],
                positive_factors=pos,
                breakers=breakers
            ))

    return detected
