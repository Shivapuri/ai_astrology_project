"""
jyotish/yogas/viparita.py
Viparita Raja Yogas (Reversal of Misfortune Royal Combinations).
Scripture: Phaladeepika Ch. 6, Verses 57-69; Ch. 7, Verses 8-10.
"""

from typing import List, Dict, Any
from jyotish.yogas.models import (
    YogaInstance, YogaCategory, YogaStatus, YogaBreakerDetail
)
from jyotish.yogas.breakers import (
    get_house_of_planet, get_sign_of_planet, get_house_rulers, get_aspect_score
)

VIPARITA_CONFIGS = {
    6: {
        "id": "harsha_yoga",
        "name": "Harṣa Viparīta Rāja Yoga",
        "archetype": "Cheerful Invincibility: The 6th lord trapped in a Dusthana destroys enemies and disease, granting joyful immunity.",
        "effects": [
            "Conquers opponents and competitors effortlessly; rivals exhaust and destroy themselves.",
            "Robust physical immunity, freedom from chronic debts, and cheerful disposition in adversity."
        ]
    },
    8: {
        "id": "sarala_yoga",
        "name": "Sarala Viparīta Rāja Yoga",
        "archetype": "Fearless Resilience: The 8th lord trapped in a Dusthana eliminates sudden catastrophes, bestowing fearless longevity.",
        "effects": [
            "Fearless mind, resilient longevity, and the ability to turn sudden crises into decisive victories.",
            "Gains through unexpected windfalls, research, esoteric knowledge, or outlasting competitors."
        ]
    },
    12: {
        "id": "vimala_yoga",
        "name": "Vimala Viparīta Rāja Yoga",
        "archetype": "Untouchable Purity & Savings: The 12th lord trapped in a Dusthana neutralizes ruinous expenditure, ensuring steady accumulation.",
        "effects": [
            "Protected from ruinous financial loss; frugal, self-contained, and financially independent.",
            "Spiritual contentment, righteous conduct, and happiness through noble service."
        ]
    }
}

def detect_viparita_raja_yogas(chart: Dict[str, Any]) -> List[YogaInstance]:
    """Scans for Harsha, Sarala, and Vimala yogas."""
    detected = []
    house_rulers = get_house_rulers(chart)
    lagna_lord = house_rulers.get(1, [None])[0]
    
    for h_origin, config in VIPARITA_CONFIGS.items():
        lord = house_rulers.get(h_origin, [None])[0]
        if not lord:
            continue
            
        # If the dusthana lord is also the Lagna lord, it protects the native directly
        h_placed = get_house_of_planet(chart, lord)
        if h_placed in (6, 8, 12):
            score = 85.0
            pos = [f"Lord of H{h_origin} ({lord}) occupies Dusthana House {h_placed}."]
            breakers = []
            
            # Check if an auspicious Kendra/Trikona lord is conjoined or strongly aspecting
            kendra_trikona_lords = set()
            for kh in (1, 4, 5, 7, 9, 10):
                for kl in house_rulers.get(kh, []):
                    if kl != lord:
                        kendra_trikona_lords.add(kl)
            for ktl in kendra_trikona_lords:
                ktl_house = get_house_of_planet(chart, ktl)
                if ktl_house == h_placed:
                    breakers.append(YogaBreakerDetail(
                        factor="Auspicious Lord Contaminated",
                        culprit_planet=ktl,
                        description=f"Auspicious Kendra/Trikona Lord {ktl} conjoins {lord} in House {h_placed}, absorbing the dusthana damage.",
                        penalty=25.0
                    ))
                    score -= 25.0
                    break
                aspect_score = get_aspect_score(chart, ktl, lord)
                if aspect_score >= 30.0:
                    breakers.append(YogaBreakerDetail(
                        factor="Auspicious Lord Aspect Contamination",
                        culprit_planet=ktl,
                        description=f"Auspicious Lord {ktl} casts a strong {aspect_score:.0f}-Virupa aspect on {lord}, linking noble houses with crisis.",
                        penalty=15.0
                    ))
                    score -= 15.0
                    break
                    
            status = YogaStatus.PURE if score >= 75 else YogaStatus.STAINED
            
            detected.append(YogaInstance(
                id=config["id"],
                name=config["name"],
                category=YogaCategory.VIPARITA,
                status=status,
                plausibility_score=round(score, 1),
                participating_planets=[lord],
                participating_houses=[h_placed],
                scripture_ref=f"Phaladeepika 6.{56+h_origin}",
                archetype=config["archetype"],
                manifestation_effects=config["effects"],
                positive_factors=pos,
                breakers=breakers
            ))
            
    return detected
