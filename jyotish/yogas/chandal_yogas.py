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
"""

from typing import List, Dict, Any
from jyotish.yogas.models import (
    YogaInstance, YogaCategory, YogaStatus, YogaBreakerDetail
)
from jyotish.yogas.breakers import (
    get_house_of_planet, get_sign_of_planet, get_planets_data, get_aspect_score,
    EXALTATION_SIGNS, OWN_SIGNS, DEBILITATION_SIGNS, NATURAL_BENEFICS
)

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

    def get_lon(p: str) -> float:
        return float(planets_data.get(p, {}).get("longitude", 0.0))

    def get_deg_in_sign(p: str) -> float:
        return float(planets_data.get(p, {}).get("degree_0_to_30", get_lon(p) % 30.0))

    # -------------------------------------------------------------
    # 1. GURU-CHĀṆḌĀLA YOGA (Jupiter + Rahu Conjunction)
    # -------------------------------------------------------------
    if "Jupiter" in planets_data and "Rahu" in planets_data:
        j_sign = get_sign_of_planet(chart, "Jupiter")
        r_sign = get_sign_of_planet(chart, "Rahu")
        
        if j_sign == r_sign and j_sign != "":
            j_house = get_house_of_planet(chart, "Jupiter")
            j_deg = get_deg_in_sign("Jupiter")
            r_deg = get_deg_in_sign("Rahu")
            diff = abs(j_deg - r_deg)
            if diff > 15.0:
                diff = abs(30.0 - diff)
                
            breakers: List[YogaBreakerDetail] = []
            positive_factors: List[str] = []
            
            # Orb classification
            if diff <= (10.0 / 3.0):  # Exact Navamsha orb (<= 3°20')
                orb_desc = f"Exact / Intimate Orb ({diff:.2f}°): Direct psychological eclipse between wisdom and ambition."
                plausibility = 92.0
            elif diff <= 10.0:
                orb_desc = f"Moderate Orb ({diff:.2f}°): Strong philosophical amplification and unorthodox doctrine."
                plausibility = 82.0
            else:
                orb_desc = f"Wide Sign Conjunction ({diff:.2f}°): Mild unorthodox coloring across common sign field."
                plausibility = 68.0

            status = YogaStatus.STAINED
            
            # Exaltation rescue (Jupiter in Cancer)
            if j_sign == EXALTATION_SIGNS.get("Jupiter"):
                status = YogaStatus.RESCUED
                positive_factors.append("Jupiter is Exalted in Cancer (Uchcha): Converts taboo zeal into revolutionary, compassionate reform.")
                plausibility += 5.0
            elif j_sign in OWN_SIGNS.get("Jupiter", []):
                positive_factors.append(f"Jupiter in Domicile ({j_sign}): Immense administrative and institutional organizing power.")
                
            # Benefic aspects (Venus or Moon)
            for ben in ["Venus", "Moon"]:
                asp = get_aspect_score(chart, ben, "Jupiter")
                if asp >= 20.0:
                    positive_factors.append(f"Aspect from natural benefic {ben} ({asp:.1f} Virūpas) softens dogmatic intensity.")
                    plausibility -= 5.0  # Softens the harshness of the dosha

            # Cruel co-conjunctions (Saturn or Mars in same sign -> Vikala / Besieged)
            for mal in ["Saturn", "Mars"]:
                if get_sign_of_planet(chart, mal) == j_sign:
                    breakers.append(YogaBreakerDetail(
                        factor=f"{mal} Co-Conjunction (Vikala Avasthā)",
                        culprit_planet=mal,
                        description=f"{mal} conjoins Jupiter and Rahu in {j_sign}, severely besieging Jupiter's ethical clarity into combative or rigid dogma.",
                        penalty=20.0
                    ))

            # Debilitated Jupiter in Capricorn
            if j_sign == DEBILITATION_SIGNS.get("Jupiter"):
                breakers.append(YogaBreakerDetail(
                    factor="Debilitated Dispositor (Neecha Guru)",
                    culprit_planet="Jupiter",
                    description="Jupiter is debilitated in Capricorn; worldly opportunism completely overrides moral restraint.",
                    penalty=25.0
                ))

            detected.append(YogaInstance(
                id="guru_chandal_yoga",
                name="Guru-Chāṇḍāla Yoga",
                category=YogaCategory.CHANDAL,
                status=status,
                plausibility_score=round(max(20.0, min(100.0, plausibility)), 1),
                participating_planets=["Jupiter", "Rahu"],
                participating_houses=[j_house],
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
        
        if j_sign == k_sign and j_sign != "":
            j_house = get_house_of_planet(chart, "Jupiter")
            j_deg = get_deg_in_sign("Jupiter")
            k_deg = get_deg_in_sign("Ketu")
            diff = abs(j_deg - k_deg)
            if diff > 15.0:
                diff = abs(30.0 - diff)
                
            detected.append(YogaInstance(
                id="guru_ketu_jnana_yoga",
                name="Guru-Ketu Jñāna Yoga",
                category=YogaCategory.CHANDAL,
                status=YogaStatus.PURE,
                plausibility_score=85.0,
                participating_planets=["Jupiter", "Ketu"],
                participating_houses=[j_house],
                scripture_ref="Phaladeepika 6.35, Vic DiCara Lesson 5 (Rahu-Ketu Masterclass)",
                archetype="The Ascetic Seeker: Ketu internalizes Jupiter's philosophical nature, fostering profound spiritual discernment, detachment from superficial dogmas, and direct mystical perception.",
                manifestation_effects=[
                    "Deep spiritual skepticism toward ritualistic religion; pursuit of direct esoteric truth and liberation (Moksha).",
                    "Exceptional capacity for research, contemplation, and philosophical detachment.",
                    f"Conjoined within {diff:.2f}° in House {j_house} ({j_sign}); favors inner wisdom over outward ambition."
                ],
                positive_factors=[f"Ketu spiritualizes Jupiter in {j_sign}; promotes introspection rather than worldly ambition."],
                breakers=[]
            ))

    # -------------------------------------------------------------
    # 3. ŚRĀPITA YOGA (Saturn + Rahu Conjunction)
    # -------------------------------------------------------------
    if "Saturn" in planets_data and "Rahu" in planets_data:
        s_sign = get_sign_of_planet(chart, "Saturn")
        r_sign = get_sign_of_planet(chart, "Rahu")
        
        if s_sign == r_sign and s_sign != "":
            s_house = get_house_of_planet(chart, "Saturn")
            s_deg = get_deg_in_sign("Saturn")
            r_deg = get_deg_in_sign("Rahu")
            diff = abs(s_deg - r_deg)
            if diff > 15.0:
                diff = abs(30.0 - diff)
                
            breakers: List[YogaBreakerDetail] = []
            positive_factors: List[str] = []
            
            status = YogaStatus.STAINED
            plausibility = 85.0
            
            if s_sign == EXALTATION_SIGNS.get("Saturn"):
                status = YogaStatus.RESCUED
                positive_factors.append("Saturn is Exalted in Libra: Forges karmic friction into extraordinary, unbreakable endurance.")
                plausibility += 5.0
            elif s_sign in OWN_SIGNS.get("Saturn", []):
                positive_factors.append(f"Saturn in Domicile ({s_sign}): Sturdy structural grounding resists chaotic disruption.")
                
            asp_jup = get_aspect_score(chart, "Jupiter", "Saturn")
            if asp_jup >= 20.0:
                positive_factors.append(f"Jupiter aspect ({asp_jup:.1f} Virūpas) provides moral guidance and mitigates karmic strain.")

            detected.append(YogaInstance(
                id="shrapit_yoga",
                name="Śrāpita Yoga",
                category=YogaCategory.CHANDAL,
                status=status,
                plausibility_score=round(max(20.0, min(100.0, plausibility)), 1),
                participating_planets=["Saturn", "Rahu"],
                participating_houses=[s_house],
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
        
        if m_sign == r_sign and m_sign != "":
            m_house = get_house_of_planet(chart, "Mars")
            m_deg = get_deg_in_sign("Mars")
            r_deg = get_deg_in_sign("Rahu")
            diff = abs(m_deg - r_deg)
            if diff > 15.0:
                diff = abs(30.0 - diff)
                
            breakers: List[YogaBreakerDetail] = []
            positive_factors: List[str] = []
            
            status = YogaStatus.STAINED
            plausibility = 85.0
            
            if m_sign == EXALTATION_SIGNS.get("Mars"):
                status = YogaStatus.RESCUED
                positive_factors.append("Mars is Exalted in Capricorn: Extreme tactical discipline harnesses raw volcanic energy constructively.")
                plausibility += 5.0
            elif m_house in [3, 6, 10, 11]:
                positive_factors.append(f"Placed in Upachaya House {m_house}: Martial fire aggressively crushes obstacles and competition.")
                
            asp_jup = get_aspect_score(chart, "Jupiter", "Mars")
            if asp_jup >= 20.0:
                positive_factors.append(f"Jupiter aspect ({asp_jup:.1f} Virūpas) cools martial aggression into principled courage.")

            detected.append(YogaInstance(
                id="angaraka_yoga",
                name="Aṅgāraka Yoga",
                category=YogaCategory.CHANDAL,
                status=status,
                plausibility_score=round(max(20.0, min(100.0, plausibility)), 1),
                participating_planets=["Mars", "Rahu"],
                participating_houses=[m_house],
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
