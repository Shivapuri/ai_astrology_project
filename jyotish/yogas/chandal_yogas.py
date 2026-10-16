"""
jyotish/yogas/chandal_yogas.py
Classical Chandal and Nodal Affliction / Catalyst Yogas.
Scripture: BPHS Ch. 45 (Avasthas & Graha Yoga), Phaladeepika Ch. 6, Saravali Ch. 31,
and Vic DiCara's Rahu-Ketu Masterclasses.

Evaluates:
1. Guru-Chāṇḍāla Yoga (Jupiter + Rahu): Ideological ambition, unorthodox doctrines, taboo zeal.
2. Guru-Ketu Jñāna Yoga (Jupiter + Ketu): Ascetic contemplation, spiritual discernment, moksha focus.
3. Śrāpita Yoga (Saturn + Rahu): Heavy karmic debt, systemic friction, perseverance crucible.
4. Aṅgāraka Yoga (Mars + Rahu): Volcanic drive, tactical courage, explosive friction.

Architecture Invariant (YOGA_ARCHITECTURE.md Row 7 & Section 5 Rule 3):
- Same-sign longitudinal separation is strictly `abs(deg1 - deg2)` in `[0.0, 30.0)` — NEVER `abs(30.0 - diff)`.
- Affliction combinations in Category `CHANDAL` must use `YogaStatus.STAINED` when active/unmitigated
  and `YogaStatus.RESCUED` when mitigated by exaltation, own sign, Nīcabhaṅga, palpable benefic aspect
  (>= 45.0 Virūpas), or Ketu spiritualization — NEVER `YogaStatus.PURE`!
- NEVER call `audit_dusthana_placement` on `CHANDAL` yogas.
"""

from typing import List, Dict, Any
from jyotish.yogas.models import (
    YogaInstance, YogaCategory, YogaStatus, YogaBreakerDetail
)
from jyotish.yogas.breakers import (
    get_house_of_planet, get_sign_of_planet, get_planets_data, get_aspect_score,
    audit_neecha_bhanga,
    EXALTATION_SIGNS, OWN_SIGNS, DEBILITATION_SIGNS,
    ASPECT_PALPABLE_THRESHOLD, ASPECT_MARGINAL_THRESHOLD
)


def _safe_deg_in_sign(planets_data: Dict[str, Any], planet: str) -> float:
    """Safely extracts degree within sign [0.0, 30.0) without failing on None."""
    p_info = planets_data.get(planet)
    if not isinstance(p_info, dict):
        return 0.0
    deg = p_info.get("degree_0_to_30")
    if deg is not None:
        try:
            return float(deg) % 30.0
        except (ValueError, TypeError):
            pass
    lon = p_info.get("longitude")
    if lon is not None:
        try:
            return float(lon) % 30.0
        except (ValueError, TypeError):
            pass
    return 0.0


def detect_chandal_yogas(chart: Dict[str, Any]) -> List[YogaInstance]:
    """
    Scans the chart for classical nodal combinations with Jupiter, Saturn, and Mars.
    Distinguishes sharply between Rahu's outward worldly amplification (Chāṇḍāla)
    and Ketu's inward spiritualizing detachment (Jñāna).
    """
    detected: List[YogaInstance] = []
    planets_data = get_planets_data(chart)

    if not planets_data:
        return detected

    # -------------------------------------------------------------
    # 1. GURU-CHĀṆḌĀLA YOGA (Jupiter + Rahu Conjunction)
    # -------------------------------------------------------------
    if "Jupiter" in planets_data and "Rahu" in planets_data:
        j_sign = get_sign_of_planet(chart, "Jupiter")
        r_sign = get_sign_of_planet(chart, "Rahu")

        if j_sign and j_sign == r_sign:
            j_house = get_house_of_planet(chart, "Jupiter")
            j_deg = _safe_deg_in_sign(planets_data, "Jupiter")
            r_deg = _safe_deg_in_sign(planets_data, "Rahu")
            # Within the same sign [0°, 30°), separation is strictly abs(j_deg - r_deg)
            diff = abs(j_deg - r_deg)

            breakers: List[YogaBreakerDetail] = []
            positive_factors: List[str] = []

            if diff <= (10.0 / 3.0):  # Exact Navamsha orb (<= 3°20')
                orb_desc = f"Exact / Intimate Orb ({diff:.2f}°): Direct psychological eclipse between wisdom and ambition."
                plausibility = 92.0
            elif diff <= 10.0:
                orb_desc = f"Moderate Orb ({diff:.2f}°): Strong philosophical amplification and unorthodox doctrine."
                plausibility = 82.0
            else:
                orb_desc = f"Wide Sign Conjunction ({diff:.2f}°): Mild unorthodox coloring across common sign field."
                plausibility = 68.0

            is_mitigated = False

            # Dignity check (Exaltation / Own Sign / Debilitation with Neecha Bhanga)
            if j_sign == EXALTATION_SIGNS.get("Jupiter"):
                is_mitigated = True
                positive_factors.append("Jupiter is Exalted in Cancer (Uccha): Converts taboo zeal into revolutionary, compassionate reform.")
            elif j_sign in OWN_SIGNS.get("Jupiter", []):
                is_mitigated = True
                positive_factors.append(f"Jupiter in Domicile ({j_sign}): Immense administrative and institutional organizing power.")
            elif j_sign == DEBILITATION_SIGNS.get("Jupiter"):
                is_nb, nb_reasons, _ = audit_neecha_bhanga("Jupiter", chart)
                if is_nb:
                    is_mitigated = True
                    positive_factors.extend(nb_reasons)
                else:
                    breakers.append(YogaBreakerDetail(
                        factor="Debilitated Dispositor (Nīca Guru)",
                        culprit_planet="Jupiter",
                        description="Jupiter is debilitated in Capricorn without cancellation; worldly opportunism overrides moral restraint.",
                        penalty=25.0
                    ))

            # Benefic aspects (Venus, Moon, Mercury) using Sphuṭa Dṛṣṭi thresholds (45.0 / 30.0 Virūpas)
            for ben in ("Venus", "Moon", "Mercury"):
                asp = get_aspect_score(chart, ben, "Jupiter")
                if asp >= ASPECT_PALPABLE_THRESHOLD:
                    is_mitigated = True
                    positive_factors.append(f"Palpable aspect from natural benefic {ben} ({asp:.1f} Virūpas) softens dogmatic intensity.")
                    plausibility -= 8.0
                elif asp >= ASPECT_MARGINAL_THRESHOLD:
                    positive_factors.append(f"Marginal aspect from natural benefic {ben} ({asp:.1f} Virūpas) tempers ideological extremes.")
                    plausibility -= 4.0

            # Cruel co-conjunctions (Saturn or Mars in same sign -> Vikala / Besieged)
            has_cruel_conj = False
            for mal in ("Saturn", "Mars"):
                if get_sign_of_planet(chart, mal) == j_sign:
                    has_cruel_conj = True
                    breakers.append(YogaBreakerDetail(
                        factor=f"{mal} Co-Conjunction (Vikala Avasthā)",
                        culprit_planet=mal,
                        description=f"{mal} conjoins Jupiter and Rahu in {j_sign}, severely besieging Jupiter's ethical clarity into combative or rigid dogma.",
                        penalty=20.0
                    ))

            # Affliction Status Invariant: RESCUED when mitigated without cruel siege, else STAINED — never PURE
            status = YogaStatus.RESCUED if (is_mitigated and not has_cruel_conj) else YogaStatus.STAINED

            detected.append(YogaInstance(
                id="guru_chandal_yoga",
                name="Guru-Chāṇḍāla Yoga",
                category=YogaCategory.CHANDAL,
                status=status,
                plausibility_score=round(max(20.0, min(100.0, plausibility)), 1),
                participating_planets=["Jupiter", "Rahu"],
                participating_houses=[j_house] if j_house > 0 else [],
                scripture_ref="BPHS Ch. 45, Phaladeepika 6.34, Saravali Ch. 31",
                archetype="The Taboo Zealot & Reformer: Rahu eclipses Jupiter's traditional wisdom, amplifying beliefs into unconventional, dogmatic, or revolutionary crusades.",
                manifestation_effects=[
                    "Constructive: Shatters outmoded dogmas, pioneers non-traditional philosophies, and mobilizes large unconventional networks.",
                    "Strained: Vulnerability to fanaticism, ideological extremism, or using moral rhetoric to justify ruthless worldly ends.",
                    orb_desc
                ],
                positive_factors=positive_factors,
                breakers=breakers
            ))

    # -------------------------------------------------------------
    # 2. GURU-KETU JÑĀNA YOGA (Jupiter + Ketu Conjunction)
    # -------------------------------------------------------------
    if "Jupiter" in planets_data and "Ketu" in planets_data:
        j_sign = get_sign_of_planet(chart, "Jupiter")
        k_sign = get_sign_of_planet(chart, "Ketu")

        if j_sign and j_sign == k_sign:
            j_house = get_house_of_planet(chart, "Jupiter")
            j_deg = _safe_deg_in_sign(planets_data, "Jupiter")
            k_deg = _safe_deg_in_sign(planets_data, "Ketu")
            diff = abs(j_deg - k_deg)

            pos_gk = [f"Ketu spiritualizes Jupiter in {j_sign}; promotes introspection and liberation (Mokṣa) over worldly ambition."]
            breakers_gk: List[YogaBreakerDetail] = []
            score_gk = 85.0

            if j_sign == DEBILITATION_SIGNS.get("Jupiter"):
                is_nb, nb_reasons, _ = audit_neecha_bhanga("Jupiter", chart)
                if is_nb:
                    pos_gk.extend(nb_reasons)
                else:
                    breakers_gk.append(YogaBreakerDetail(
                        factor="Unredeemed Debilitation of Jupiter",
                        culprit_planet="Jupiter",
                        description="Jupiter is debilitated in Capricorn without cancellation, dampening philosophical clarity.",
                        penalty=20.0
                    ))
                    score_gk -= 20.0

            # Affliction category invariant: RESCUED (spiritualized nodal inversion) when unafflicted, STAINED when debilitated
            status_gk = YogaStatus.STAINED if breakers_gk else YogaStatus.RESCUED

            detected.append(YogaInstance(
                id="guru_ketu_jnana_yoga",
                name="Guru-Ketu Jñāna Yoga",
                category=YogaCategory.CHANDAL,
                status=status_gk,
                plausibility_score=round(max(20.0, min(100.0, score_gk)), 1),
                participating_planets=["Jupiter", "Ketu"],
                participating_houses=[j_house] if j_house > 0 else [],
                scripture_ref="Phaladeepika 6.35, Vic DiCara Lesson 5 (Rahu-Ketu Masterclass)",
                archetype="The Ascetic Seeker: Ketu internalizes Jupiter's philosophical nature, fostering profound spiritual discernment, detachment from superficial dogmas, and direct mystical perception.",
                manifestation_effects=[
                    "Deep spiritual skepticism toward ritualistic religion; pursuit of direct esoteric truth and liberation (Moksha).",
                    "Exceptional capacity for research, contemplation, and philosophical detachment.",
                    f"Conjoined within {diff:.2f}° in House {j_house} ({j_sign}); favors inner wisdom over outward ambition."
                ],
                positive_factors=pos_gk,
                breakers=breakers_gk
            ))

    # -------------------------------------------------------------
    # 3. ŚRĀPITA YOGA (Saturn + Rahu Conjunction)
    # -------------------------------------------------------------
    if "Saturn" in planets_data and "Rahu" in planets_data:
        s_sign = get_sign_of_planet(chart, "Saturn")
        r_sign = get_sign_of_planet(chart, "Rahu")

        if s_sign and s_sign == r_sign:
            s_house = get_house_of_planet(chart, "Saturn")
            s_deg = _safe_deg_in_sign(planets_data, "Saturn")
            r_deg = _safe_deg_in_sign(planets_data, "Rahu")
            diff = abs(s_deg - r_deg)

            breakers = []
            positive_factors = []
            is_mitigated = False
            plausibility = 88.0 if diff <= (10.0 / 3.0) else (82.0 if diff <= 10.0 else 72.0)

            if s_sign == EXALTATION_SIGNS.get("Saturn"):
                is_mitigated = True
                positive_factors.append("Saturn is Exalted in Libra: Forges karmic friction into extraordinary, unbreakable endurance.")
            elif s_sign in OWN_SIGNS.get("Saturn", []):
                is_mitigated = True
                positive_factors.append(f"Saturn in Domicile ({s_sign}): Sturdy structural grounding resists chaotic disruption.")
            elif s_sign == DEBILITATION_SIGNS.get("Saturn"):
                is_nb, nb_reasons, _ = audit_neecha_bhanga("Saturn", chart)
                if is_nb:
                    is_mitigated = True
                    positive_factors.extend(nb_reasons)
                else:
                    breakers.append(YogaBreakerDetail(
                        factor="Debilitated Saturn (Nīca Śani)",
                        culprit_planet="Saturn",
                        description="Saturn is debilitated in Aries without cancellation, intensifying systemic frustration and delays.",
                        penalty=25.0
                    ))

            asp_jup = get_aspect_score(chart, "Jupiter", "Saturn")
            if asp_jup >= ASPECT_PALPABLE_THRESHOLD:
                is_mitigated = True
                positive_factors.append(f"Palpable Jupiter aspect ({asp_jup:.1f} Virūpas) provides moral guidance and mitigates karmic strain.")
                plausibility -= 8.0
            elif asp_jup >= ASPECT_MARGINAL_THRESHOLD:
                positive_factors.append(f"Marginal Jupiter aspect ({asp_jup:.1f} Virūpas) offers philosophical perspective.")
                plausibility -= 4.0

            status = YogaStatus.RESCUED if (is_mitigated and not breakers) else YogaStatus.STAINED

            detected.append(YogaInstance(
                id="shrapit_yoga",
                name="Śrāpita Yoga",
                category=YogaCategory.CHANDAL,
                status=status,
                plausibility_score=round(max(20.0, min(100.0, plausibility)), 1),
                participating_planets=["Saturn", "Rahu"],
                participating_houses=[s_house] if s_house > 0 else [],
                scripture_ref="BPHS Ch. 45, Nadi Shastras",
                archetype="The Karmic Crucible: Rahu amplifies Saturnian burdens, delays, and structural pressure, requiring persistent patience to forge mastery.",
                manifestation_effects=[
                    "Heavy karmic duties and trials in early life; learning through hard labor, resilience, and slow realization.",
                    "Constructive: Bestows monumental patience, realism, and mastery over difficult material structures over time.",
                    f"Conjoined within {diff:.2f}° in House {s_house} ({s_sign})."
                ],
                positive_factors=positive_factors,
                breakers=breakers
            ))

    # -------------------------------------------------------------
    # 4. AṄGĀRAKA YOGA (Mars + Rahu Conjunction)
    # -------------------------------------------------------------
    if "Mars" in planets_data and "Rahu" in planets_data:
        m_sign = get_sign_of_planet(chart, "Mars")
        r_sign = get_sign_of_planet(chart, "Rahu")

        if m_sign and m_sign == r_sign:
            m_house = get_house_of_planet(chart, "Mars")
            m_deg = _safe_deg_in_sign(planets_data, "Mars")
            r_deg = _safe_deg_in_sign(planets_data, "Rahu")
            diff = abs(m_deg - r_deg)

            breakers = []
            positive_factors = []
            is_mitigated = False
            plausibility = 88.0 if diff <= (10.0 / 3.0) else (82.0 if diff <= 10.0 else 72.0)

            if m_sign == EXALTATION_SIGNS.get("Mars"):
                is_mitigated = True
                positive_factors.append("Mars is Exalted in Capricorn: Extreme tactical discipline harnesses raw volcanic energy constructively.")
            elif m_sign in OWN_SIGNS.get("Mars", []):
                is_mitigated = True
                positive_factors.append(f"Mars in Domicile ({m_sign}): Strong martial self-command channels competitive heat.")
            elif m_sign == DEBILITATION_SIGNS.get("Mars"):
                is_nb, nb_reasons, _ = audit_neecha_bhanga("Mars", chart)
                if is_nb:
                    is_mitigated = True
                    positive_factors.extend(nb_reasons)
                else:
                    breakers.append(YogaBreakerDetail(
                        factor="Debilitated Mars (Nīca Kuja)",
                        culprit_planet="Mars",
                        description="Mars is debilitated in Cancer without cancellation, producing volatile emotional reactivity.",
                        penalty=25.0
                    ))

            if m_house in (3, 6, 10, 11):
                positive_factors.append(f"Placed in Upachaya House {m_house}: Martial fire aggressively crushes obstacles and competition.")

            asp_jup = get_aspect_score(chart, "Jupiter", "Mars")
            if asp_jup >= ASPECT_PALPABLE_THRESHOLD:
                is_mitigated = True
                positive_factors.append(f"Palpable Jupiter aspect ({asp_jup:.1f} Virūpas) cools martial aggression into principled courage.")
                plausibility -= 8.0
            elif asp_jup >= ASPECT_MARGINAL_THRESHOLD:
                positive_factors.append(f"Marginal Jupiter aspect ({asp_jup:.1f} Virūpas) moderates impulsiveness.")
                plausibility -= 4.0

            status = YogaStatus.RESCUED if (is_mitigated and not breakers) else YogaStatus.STAINED

            detected.append(YogaInstance(
                id="angaraka_yoga",
                name="Aṅgāraka Yoga",
                category=YogaCategory.CHANDAL,
                status=status,
                plausibility_score=round(max(20.0, min(100.0, plausibility)), 1),
                participating_planets=["Mars", "Rahu"],
                participating_houses=[m_house] if m_house > 0 else [],
                scripture_ref="Saravali Ch. 31, BPHS Ch. 45",
                archetype="The Volcanic Catalyst: Rahu injects high-octane fuel into Mars's tactical fire, producing relentless courage or volatile aggression.",
                manifestation_effects=[
                    "Explosive energy drive, fearlessness, decisive physical action, and tactical prowess.",
                    "Strained: Risk of impulsive temper, burn-out, or disputes if not channeled toward a disciplined craft.",
                    f"Conjoined within {diff:.2f}° in House {m_house} ({m_sign})."
                ],
                positive_factors=positive_factors,
                breakers=breakers
            ))

    return detected
