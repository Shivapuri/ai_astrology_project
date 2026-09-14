"""
jyotish/yogas/kartari.py
Kartari Yogas (The Universal Hemming Principle).
Scripture: Phaladeepika Ch. 6, Verses 11-13; Ryan Kurczak Lesson 42.
Evaluates Shubha Kartari (protection) and Papa Kartari (restriction).
"""

from typing import List, Dict, Any
from jyotish.yogas.models import (
    YogaInstance, YogaCategory, YogaStatus, YogaBreakerDetail
)
from jyotish.yogas.breakers import (
    get_house_of_planet, get_planets_data, NATURAL_BENEFICS, NATURAL_MALEFICS
)

def detect_kartari_yogas(chart: Dict[str, Any]) -> List[YogaInstance]:
    """Scans for Shubha Kartari and Papa Kartari on the Lagna and the Moon."""
    detected = []
    planets_data = get_planets_data(chart)
    planet_houses = {p: get_house_of_planet(chart, p) for p in planets_data}
    moon_house = planet_houses.get("Moon", 0)
    targets = [
        ("Lagna (Ascendant)", 1, "Ascendant / Physical Vessel", "Lagna"),
        ("Moon (Chandra)", moon_house, "Emotional Mind / Manas", "Moon")
    ]
    
    for target_name, target_house, domain, target_key in targets:
        if target_house == 0:
            continue
            
        h2 = (target_house % 12) + 1
        h12 = ((target_house - 2) % 12) + 1
        
        planets_h2 = [p for p in planets_data if planet_houses.get(p) == h2 and p != target_key]
        planets_h12 = [p for p in planets_data if planet_houses.get(p) == h12 and p != target_key]
        
        if not (planets_h2 and planets_h12):
            continue
            
        flanking_planets = planets_h2 + planets_h12
        benefics = [p for p in flanking_planets if p in NATURAL_BENEFICS]
        malefics = [p for p in flanking_planets if p in NATURAL_MALEFICS]
        
        # Shubha Kartari: Only benefics flanking
        if benefics and not malefics:
            detected.append(YogaInstance(
                id=f"shubha_kartari_{target_name.split()[0].lower()}",
                name=f"Śubha Kartarī Yoga ({target_name})",
                category=YogaCategory.KARTARI,
                status=YogaStatus.PURE,
                plausibility_score=90.0,
                participating_planets=benefics,
                participating_houses=[h12, target_house, h2],
                scripture_ref="Phaladeepika 6.11",
                archetype=f"The Protective Shield: {target_name} is cushioned on both sides by benefics, granting ease and continuous support.",
                manifestation_effects=[
                    f"Surrounds the {domain} with psychological safety, resource support, and physical resilience.",
                    "Quick recovery from life setbacks and natural protection from enemies."
                ],
                positive_factors=[f"Natural benefics ({', '.join(benefics)}) flank in houses {h12} and {h2}."],
                breakers=[]
            ))
            
        # Papa Kartari: Only malefics flanking
        elif malefics and not benefics:
            detected.append(YogaInstance(
                id=f"papa_kartari_{target_name.lower().replace(' ', '_')}",
                name=f"Pāpa Kartarī Yoga ({target_name})",
                category=YogaCategory.KARTARI,
                status=YogaStatus.STAINED,
                plausibility_score=75.0,  # Highly plausible challenging combination
                participating_planets=malefics,
                participating_houses=[h12, target_house, h2],
                scripture_ref="Phaladeepika 6.12-13",
                archetype=f"The Scissor Squeeze: {target_name} is compressed on both sides by harsh malefics, producing friction and restriction.",
                manifestation_effects=[
                    f"Creates tension, anxiety, and a feeling of being hemmed in regarding the {domain}.",
                    "Requires conscious emotional discipline, stress management, and boundary-setting during malefic Dashas."
                ],
                positive_factors=[],
                breakers=[YogaBreakerDetail(
                    factor="Malefic Scissors",
                    culprit_planet=", ".join(malefics),
                    description=f"Harsh malefics ({', '.join(malefics)}) flank houses {h12} and {h2}, trapping {target_name}.",
                    penalty=35.0
                )]
            ))
            
    return detected
