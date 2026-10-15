"""
jyotish/yogas/parivartana.py
Parivartana Yogas (Mutual House Sign Exchanges).
Scripture: Phaladeepika Ch. 6, Verses 32-34.
Classifies all 66 mutual sign exchanges into:
- 28 Mahā Parivartana (among 1, 2, 4, 5, 7, 9, 10, 11)
- 8 Khala Parivartana (3rd house with 1, 2, 4, 5, 7, 9, 10, 11)
- 30 Dainya Parivartana (involving 6, 8, or 12; including 3 Viparīta crossovers among 6, 8, 12)
"""

from typing import List, Dict, Any
from jyotish.yogas.models import (
    YogaInstance, YogaCategory, YogaStatus, YogaBreakerDetail
)
from jyotish.yogas.breakers import (
    get_house_of_planet, get_sign_of_planet, get_planets_data,
    audit_trishadaya_interference, audit_combustion, audit_shadbala_muscle,
    resolve_yoga_score_and_status, SIGN_LORDS
)

AUSPICIOUS_HOUSES = {1, 2, 4, 5, 7, 9, 10, 11}
DUSTHANA_HOUSES = {6, 8, 12}
CLASSICAL_PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]


def detect_parivartana_yogas(chart: Dict[str, Any]) -> List[YogaInstance]:
    """Scans for mutual sign exchanges among all 7 physical planets."""
    detected: List[YogaInstance] = []
    planets_data = get_planets_data(chart)

    for i in range(len(CLASSICAL_PLANETS)):
        for j in range(i + 1, len(CLASSICAL_PLANETS)):
            p1, p2 = CLASSICAL_PLANETS[i], CLASSICAL_PLANETS[j]
            if p1 not in planets_data or p2 not in planets_data:
                continue

            s1 = get_sign_of_planet(chart, p1)
            s2 = get_sign_of_planet(chart, p2)
            if not s1 or not s2 or s1 == s2:
                continue

            # Mutual exchange (anyonyam): p1 in p2's sign AND p2 in p1's sign
            lord_s1 = SIGN_LORDS.get(s1)
            lord_s2 = SIGN_LORDS.get(s2)

            if lord_s1 == p2 and lord_s2 == p1:
                # Dual-sign rulership disambiguation: use actual houses occupied by p1 and p2
                h1 = get_house_of_planet(chart, p1)
                h2 = get_house_of_planet(chart, p2)
                if h1 not in range(1, 13) or h2 not in range(1, 13) or h1 == h2:
                    continue

                exchanged_houses = sorted([h1, h2])
                positive_factors = [
                    f"{p1} (in {s1} / H{h1}) and {p2} (in {s2} / H{h2}) exchange signs (H{exchanged_houses[0]} ⇄ H{exchanged_houses[1]})."
                ]
                breakers: List[YogaBreakerDetail] = []

                # Precedence per Phaladeepika 6.32-34:
                # 1. Any involvement of 6, 8, 12 -> Dainya (30 pairs)
                # 2. Otherwise involvement of 3 -> Khala (8 pairs)
                # 3. Otherwise among {1, 2, 4, 5, 7, 9, 10, 11} -> Mahā (28 pairs)
                has_dusthana = bool({h1, h2} & DUSTHANA_HOUSES)
                both_dusthana = (h1 in DUSTHANA_HOUSES and h2 in DUSTHANA_HOUSES)
                has_third = (h1 == 3 or h2 == 3)

                # Layer 2 secondary auditors (Combustion & Shadbala across all Parivartanas)
                comb_brk = audit_combustion([p1, p2], chart)
                shad_brk, shad_pos = audit_shadbala_muscle([p1, p2], chart)
                positive_factors.extend(shad_pos)

                if has_dusthana:
                    y_id = f"dainya_parivartana_{p1.lower()}_{p2.lower()}"
                    y_name = f"Dainya Parivartana Yoga ({p1} in {s1} ⇄ {p2} in {s2})"

                    if both_dusthana:
                        # 3 Viparita Crossover Pairs: {6,8}, {6,12}, {8,12}
                        base_score = 68.0
                        positive_factors.append(
                            f"Viparīta Crossover: Both exchanged houses (H{exchanged_houses[0]} & H{exchanged_houses[1]}) are Duṣṭhānas, turning mutual crisis into protective resilience."
                        )
                        archetype = "The Reversal Exchange (Dainya-Viparīta Crossover): Two Duṣṭhāna lords swap difficult houses (6, 8, 12), neutralizing external rivals and containing loss."
                        effects = [
                            "Converts adversity, debt, or sudden crisis into unexpected resilience and protection.",
                            "Classically grouped among the 30 Dainya exchanges, yet functions as a mutual Viparīta reversal."
                        ]
                        breakers.extend(comb_brk)
                        breakers.extend(shad_brk)
                        score = base_score - sum(b.penalty for b in breakers)
                        score = round(max(5.0, min(74.0, score)), 1)
                        y_status = YogaStatus.RESCUED if score >= 30.0 else YogaStatus.BROKEN
                    else:
                        # 27 Contaminating Dainya Pairs: one Dusthana + one non-Dusthana
                        base_score = 80.0
                        archetype = "The Trial of Adversity: Sign exchange involving Duṣṭhāna houses (6, 8, 12), producing unexpected upheaval or karmic friction."
                        effects = [
                            "Periodic cycles of sudden expenditure, debt, health vulnerability, or institutional friction.",
                            "Directs energy into problem-solving, service, or spiritual detachment through crisis."
                        ]
                        breakers.append(YogaBreakerDetail(
                            factor="Dusthana Exchange (Dainya)",
                            culprit_planet=f"{p1}/{p2}",
                            description=f"Exchange links House {exchanged_houses[0]} and House {exchanged_houses[1]}. Significations of the auspicious house absorb Duṣṭhāna trials.",
                            penalty=35.0
                        ))
                        breakers.extend(comb_brk)
                        breakers.extend(shad_brk)
                        score = base_score - sum(b.penalty for b in breakers)
                        score = round(max(5.0, min(70.0, score)), 1)
                        # Affliction yoga invariant: Dainya is NEVER YogaStatus.PURE
                        y_status = YogaStatus.STAINED if score >= 30.0 else YogaStatus.BROKEN

                elif has_third:
                    # 8 Khala Pairs: 3rd house with {1, 2, 4, 5, 7, 9, 10, 11}
                    y_id = f"khala_parivartana_{p1.lower()}_{p2.lower()}"
                    y_name = f"Khala Parivartana Yoga ({p1} in {s1} ⇄ {p2} in {s2})"
                    base_score = 80.0
                    archetype = "The Cycle of Effort: Sign exchange involving the 3rd house of hustle, alternating between struggle and self-made triumph."
                    effects = [
                        "Alternating phases of bold initiative, intense hustle, setbacks, and sudden self-made victories.",
                        "Grants enterprise and courage, though results fluctuate according to personal persistence."
                    ]
                    breakers.append(YogaBreakerDetail(
                        factor="3rd House Hustle Intrusion (Khala)",
                        culprit_planet=f"{p1}/{p2}",
                        description=f"Exchange links House 3 with House {h1 if h2 == 3 else h2}; fortunes fluctuate with personal effort.",
                        penalty=15.0
                    ))
                    breakers.extend(comb_brk)
                    breakers.extend(shad_brk)
                    score = base_score - sum(b.penalty for b in breakers)
                    score = round(max(5.0, min(74.0, score)), 1)
                    y_status = YogaStatus.STAINED if score >= 30.0 else YogaStatus.BROKEN

                else:
                    # 28 Mahā Pairs: among {1, 2, 4, 5, 7, 9, 10, 11}
                    y_id = f"maha_parivartana_{p1.lower()}_{p2.lower()}"
                    y_name = f"Mahā Parivartana Yoga ({p1} in {s1} ⇄ {p2} in {s2})"
                    base_score = 90.0
                    is_supreme_exchange = ({h1, h2} == {9, 10})
                    if is_supreme_exchange:
                        base_score += 5.0
                        positive_factors.append("Supreme Dharma-Karma Exchange (H9 ⇄ H10).")

                    archetype = "The Royal Exchange: Mutual reception between auspicious Kendra/Trikoṇa/Dhana houses, multiplying mutual prosperity."
                    effects = [
                        "Endows sovereign authority, wealth, vehicles, fame, and enduring societal respect.",
                        "Both planets behave as honored guests in each other's homes, mutually fortifying their promises."
                    ]

                    # Apply Layer 2 breakers for Mahā Parivartana per YOGA_ARCHITECTURE.md
                    exclude_trishadaya = (11,) if 11 in (h1, h2) else ()
                    breakers.extend(audit_trishadaya_interference(
                        [p1, p2], chart,
                        is_supreme_pairing=is_supreme_exchange,
                        exclude_houses=exclude_trishadaya
                    ))
                    breakers.extend(comb_brk)
                    breakers.extend(shad_brk)

                    score, y_status = resolve_yoga_score_and_status(base_score, breakers)

                detected.append(YogaInstance(
                    id=y_id,
                    name=y_name,
                    category=YogaCategory.PARIVARTANA,
                    status=y_status,
                    plausibility_score=score,
                    participating_planets=[p1, p2],
                    participating_houses=exchanged_houses,
                    scripture_ref="Phaladeepika 6.32-34",
                    archetype=archetype,
                    manifestation_effects=effects,
                    positive_factors=positive_factors,
                    breakers=breakers
                ))

    return detected
