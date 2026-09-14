"""
jyotish/yogas/parivartana.py
Parivartana Yogas (Mutual House Sign Exchanges).
Scripture: Phaladeepika Ch. 6, Verses 32-34.
Classifies all mutual sign exchanges into Maha, Khala, and Dainya.
"""

from typing import List, Dict, Any
from jyotish.yogas.models import (
    YogaInstance, YogaCategory, YogaStatus, YogaBreakerDetail
)
from jyotish.yogas.breakers import (
    get_house_of_planet, get_sign_of_planet, get_house_rulers, get_planets_data, SIGN_LORDS
)

AUSPICIOUS_HOUSES = {1, 2, 4, 5, 7, 9, 10, 11}
DUSTHANA_HOUSES = {6, 8, 12}

def detect_parivartana_yogas(chart: Dict[str, Any]) -> List[YogaInstance]:
    """Scans for mutual sign exchanges among all physical planets."""
    detected = []
    planets_data = get_planets_data(chart)
    planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    
    evaluated_pairs = set()
    
    for i in range(len(planets)):
        for j in range(i + 1, len(planets)):
            p1, p2 = planets[i], planets[j]
            if p1 not in planets_data or p2 not in planets_data:
                continue
                
            s1 = get_sign_of_planet(chart, p1)
            s2 = get_sign_of_planet(chart, p2)
            
            # Mutual exchange: p1 in p2's sign AND p2 in p1's sign
            lord_s1 = SIGN_LORDS.get(s1)
            lord_s2 = SIGN_LORDS.get(s2)
            
            if lord_s1 == p2 and lord_s2 == p1:
                h1 = get_house_of_planet(chart, p1)
                h2 = get_house_of_planet(chart, p2)
                
                # Classification per Phaladeepika 6.32-34
                has_dusthana = bool({h1, h2} & DUSTHANA_HOUSES)
                has_third = (h1 == 3 or h2 == 3)
                
                if has_dusthana:
                    # Dainya Yoga (Exchange with 6, 8, or 12)
                    y_id = f"dainya_parivartana_{p1.lower()}_{p2.lower()}"
                    y_name = f"Dainya Parivartana Yoga ({p1} in {s1} ⇄ {p2} in {s2})"
                    y_status = YogaStatus.STAINED
                    score = 45.0
                    archetype = "The Trial of Adversity: Sign exchange involving Dusthana houses (6, 8, 12), producing unexpected upheaval or loss."
                    effects = [
                        "Periodic cycles of sudden expenditure, debt, health vulnerability, or misunderstanding.",
                        "Directs energy into spiritual detachment, service, or learning through crisis."
                    ]
                    breakers = [YogaBreakerDetail(
                        factor="Dusthana Exchange",
                        culprit_planet=f"{p1}/{p2}",
                        description=f"Exchange links House {h1} and House {h2}. Matter related to these houses undergoes karmic trials.",
                        penalty=35.0
                    )]
                elif has_third:
                    # Khala Yoga (Exchange involving 3rd house)
                    y_id = f"khala_parivartana_{p1.lower()}_{p2.lower()}"
                    y_name = f"Khala Parivartana Yoga ({p1} in {s1} ⇄ {p2} in {s2})"
                    y_status = YogaStatus.STAINED
                    score = 65.0
                    archetype = "The Cycle of Effort: Sign exchange involving the 3rd house of hustle, alternating between struggle and triumph."
                    effects = [
                        "Alternating phases of arrogance, intense hustle, setbacks, and sudden self-made victories.",
                        "Gives courageous initiative, but success requires patient, persistent manual effort."
                    ]
                    breakers = [YogaBreakerDetail(
                        factor="3rd House Hustle Intrusion",
                        culprit_planet=f"{p1}/{p2}",
                        description="Involves 3rd house of personal effort; results fluctuate according to persistence.",
                        penalty=15.0
                    )]
                else:
                    # Maha Yoga (Exchange among auspicious houses 1, 2, 4, 5, 7, 9, 10, 11)
                    y_id = f"maha_parivartana_{p1.lower()}_{p2.lower()}"
                    y_name = f"Mahā Parivartana Yoga ({p1} in {s1} ⇄ {p2} in {s2})"
                    y_status = YogaStatus.PURE
                    score = 90.0
                    archetype = "The Royal Exchange: Mutual reception between auspicious Kendra/Trikona/Dhana houses, multiplying mutual prosperity."
                    effects = [
                        "Endows sovereign authority, wealth, vehicles, fame, and enduring societal respect.",
                        "Both planets behave as honored guests in each other's homes, mutually fortifying their promises."
                    ]
                    breakers = []
                    
                detected.append(YogaInstance(
                    id=y_id,
                    name=y_name,
                    category=YogaCategory.PARIVARTANA,
                    status=y_status,
                    plausibility_score=score,
                    participating_planets=[p1, p2],
                    participating_houses=[h1, h2],
                    scripture_ref="Phaladeepika 6.32-34",
                    archetype=archetype,
                    manifestation_effects=effects,
                    positive_factors=[f"{p1} (in {s1}/H{h1}) and {p2} (in {s2}/H{h2}) exchange signs perfectly."],
                    breakers=breakers
                ))
                
    return detected
