"""
jyotish/yogas/pancha_mahapurusha.py
Pancha Mahapurusha Yogas (Five Great Person Combinations).
Scripture: Brihat Parashara Hora Shastra Ch. 75, Phaladeepika Ch. 6, Verses 1-4.
"""

from typing import List, Dict, Any
from jyotish.yogas.models import (
    YogaInstance, YogaCategory, YogaStatus, YogaBreakerDetail
)
from jyotish.yogas.breakers import (
    EXALTATION_SIGNS, OWN_SIGNS,
    get_house_of_planet, get_sign_of_planet, get_planets_data, get_house_rulers,
    audit_trishadaya_interference, audit_combustion,
    audit_dispositor_vitality, audit_shadbala_muscle
)

MAHAPURUSHA_CONFIGS = {
    "Mars": {
        "id": "ruchaka_yoga",
        "name": "Rucaka Mahāpuruṣa Yoga",
        "scripture_ref": "BPHS 75.1-4, Phaladeepika 6.1",
        "archetype": "The Fearless Warrior & Commander: Glows with radiant fire, executive boldness, and the power to destroy obstacles.",
        "effects": [
            "Fearless, courageous demeanor; naturally confronts and eliminates life's obstacles.",
            "Strong physical constitution, well-defined jawline/bone structure, and military/athletic capability.",
            "Commands authority, leads projects decisively, and emerges victorious in competitive struggles."
        ]
    },
    "Mercury": {
        "id": "bhadra_yoga",
        "name": "Bhadra Mahāpuruṣa Yoga",
        "scripture_ref": "BPHS 75.5-8, Phaladeepika 6.2",
        "archetype": "The Auspicious Scholar & Organizer: Blessed with razor-sharp analytical intellect, hygienic cleanliness, and scholarly eloquence.",
        "effects": [
            "Extraordinary intelligence, vast retention of technical details, facts, and oratory eloquence.",
            "Praised by scholars and educated minds; master of commerce, calculation, writing, and counseling.",
            "Long life, disciplined hygienic habits, and exceptional organizational efficiency."
        ]
    },
    "Jupiter": {
        "id": "hamsa_yoga",
        "name": "Haṃsa Mahāpuruṣa Yoga",
        "scripture_ref": "BPHS 75.9-12, Phaladeepika 6.3",
        "archetype": "The Spiritual Swan & Preceptor: Revered by the virtuous, embodying moral clarity, spiritual wisdom, and righteous fortune.",
        "effects": [
            "Deep moral integrity (Dharma), broad-minded philosophical wisdom, and devotion to sacred ideals.",
            "Revered by teachers and spiritual seekers; natural preceptor, mentor, and protector of community resources.",
            "Peaceful disposition, graceful speech, and continuous divine fortune throughout life."
        ]
    },
    "Venus": {
        "id": "malavya_yoga",
        "name": "Mālavya Mahāpuruṣa Yoga",
        "scripture_ref": "BPHS 75.13-16, Phaladeepika 6.3-4",
        "archetype": "The Cultured Creator & Diplomat: Endowed with aesthetic refinement, luxurious comfort, deep patience, and serene senses.",
        "effects": [
            "Refined aesthetic discernment, love of fine arts, music, and luxurious surroundings.",
            "Deep patience (Dhriti), graceful magnetic presence, and tranquility of the senses (Prasannendriya).",
            "Fortunate in marriage, partnerships, wealth accumulation, and diplomatic relations."
        ]
    },
    "Saturn": {
        "id": "sasa_yoga",
        "name": "Śaśa Mahāpuruṣa Yoga",
        "scripture_ref": "BPHS 75.17-20, Phaladeepika 6.4",
        "archetype": "The Master of Discipline & Endurance: Respected by all social classes for peerless work ethic, surviving grueling trials where others fail.",
        "effects": [
            "Unshakeable discipline, emotional self-mastery, and willingness to tackle grueling, unglamorous responsibilities.",
            "Commands the loyalty of workers and subordinates; authority recognized across all walks of society (Sarvajanai).",
            "Exceptional longevity, resilience in adversity, and enduring institutional legacy built through patience."
        ]
    }
}

def detect_pancha_mahapurusha_yogas(chart: Dict[str, Any]) -> List[YogaInstance]:
    """Scans chart for Pancha Mahapurusha Yogas from Lagna and Chandra."""
    detected = []
    planets_data = get_planets_data(chart)
    moon_house = get_house_of_planet(chart, "Moon")
    lagna_lord = get_house_rulers(chart).get(1, [""])[0]
    
    for p, config in MAHAPURUSHA_CONFIGS.items():
        if p not in planets_data:
            continue
            
        p_house = get_house_of_planet(chart, p)
        p_sign = get_sign_of_planet(chart, p)
        
        is_exalted = (p_sign == EXALTATION_SIGNS.get(p))
        is_own = (p_sign in OWN_SIGNS.get(p, []))
        
        if not (is_exalted or is_own):
            continue
            
        # Check angularity from Lagna (1, 4, 7, 10)
        is_kendra_lagna = p_house in (1, 4, 7, 10)
        
        # Check angularity from Moon
        is_kendra_moon = False
        if moon_house > 0 and p_house > 0:
            moon_diff = (p_house - moon_house) % 12 + 1
            is_kendra_moon = moon_diff in (1, 4, 7, 10)
            
        if not (is_kendra_lagna or is_kendra_moon):
            continue
            
        # Start plausibility scoring
        score = 80.0
        positive_factors = []
        
        if is_exalted:
            positive_factors.append(f"{p} is exalted in {p_sign}.")
            score += 10.0
        elif is_own:
            positive_factors.append(f"{p} is in its own home sign {p_sign} (acts as its own dispositor).")
            score += 10.0
            
        if is_kendra_lagna:
            positive_factors.append(f"Angular prominence: Situated in Kendra House {p_house} from the Ascendant.")
            if p_house in (1, 10):
                score += 5.0  # Extra prominence on Lagna/Midheaven
                
        if is_kendra_moon:
            positive_factors.append(f"Confluence: Also angular from the Moon (Chandra Kendra), reinforcing experiential manifestation.")
            score += 5.0
            
        if p == lagna_lord:
            positive_factors.append(f"Ascendant Lord merger: {p} rules the Lagna, identifying the native's core vitality with the archetype.")
            score += 10.0
            
        # Run Breaker Audits
        breakers = []
        
        # 1. Trishadaya intrusion
        trish_breakers = audit_trishadaya_interference([p], chart)
        breakers.extend(trish_breakers)
        
        # 2. Combustion
        comb_breakers = audit_combustion([p], chart)
        breakers.extend(comb_breakers)
        
        # 3. Dispositor condition (if exalted, check dispositor)
        if is_exalted:
            disp_breakers = audit_dispositor_vitality([p], chart)
            breakers.extend(disp_breakers)
            
        # 4. Shadbala muscle
        shad_breakers, shad_pos = audit_shadbala_muscle([p], chart)
        breakers.extend(shad_breakers)
        positive_factors.extend(shad_pos)
        
        # Calculate net score
        for b in breakers:
            score -= b.penalty
            
        score = max(5.0, min(100.0, score))
        
        if score >= 75.0:
            status = YogaStatus.PURE
        elif score >= 50.0:
            status = YogaStatus.STAINED
        elif score >= 30.0:
            status = YogaStatus.RESCUED
        else:
            status = YogaStatus.BROKEN
            
        detected.append(YogaInstance(
            id=config["id"],
            name=config["name"],
            category=YogaCategory.MAHAPURUSHA,
            status=status,
            plausibility_score=round(score, 1),
            participating_planets=[p],
            participating_houses=[p_house],
            scripture_ref=config["scripture_ref"],
            archetype=config["archetype"],
            manifestation_effects=config["effects"],
            positive_factors=positive_factors,
            breakers=breakers
        ))
        
    return detected
