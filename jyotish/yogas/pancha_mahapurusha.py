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
    audit_dispositor_vitality, audit_shadbala_muscle, audit_dusthana_placement
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
    house_rulers = get_house_rulers(chart)
    lagna_rulers = house_rulers.get(1) or []
    lagna_lord = lagna_rulers[0] if lagna_rulers else ""
    
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
        moon_diff = 0
        is_kendra_moon = False
        if moon_house > 0 and p_house > 0:
            moon_diff = (p_house - moon_house) % 12 + 1
            is_kendra_moon = moon_diff in (1, 4, 7, 10)
            
        if not (is_kendra_lagna or is_kendra_moon):
            continue
            
        # Base plausibility: 80.0 for primary Lagna Kendra, 70.0 for secondary Chandra-only Kendra (indāvapi)
        score = 80.0 if is_kendra_lagna else 70.0
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
                positive_factors.append(
                    f"Confluence: Also angular from the Moon (Kendra H{moon_diff} from Chandra), reinforcing experiential manifestation."
                )
                score += 5.0
        else:
            positive_factors.append(
                f"Lunar angularity (indāvapi): Situated in Kendra H{moon_diff} from the Moon (occupies House {p_house} from Lagna)."
            )
            
        if p == lagna_lord:
            positive_factors.append(f"Ascendant Lord merger: {p} rules the Lagna, identifying the native's core vitality with the archetype.")
            score += 10.0
            
        # Run Breaker Audits
        breakers = []
        
        # 1. Trishadaya intrusion
        breakers.extend(audit_trishadaya_interference([p], chart))
        
        # 2. Combustion
        breakers.extend(audit_combustion([p], chart))
        
        # 3. Dispositor condition (if exalted, check dispositor)
        if is_exalted:
            breakers.extend(audit_dispositor_vitality([p], chart))
            
        # 4. Dusthana placement from Lagna (applies when formed only from Chandra Kendra in H6, H8, or H12)
        dusthana_breaker = audit_dusthana_placement([p_house], YogaCategory.MAHAPURUSHA.value)
        if dusthana_breaker is not None:
            breakers.append(dusthana_breaker)

        # 5. Shadbala muscle
        shad_breakers, shad_pos = audit_shadbala_muscle([p], chart)
        breakers.extend(shad_breakers)
        positive_factors.extend(shad_pos)
        
        # Cap positive confluence score at 100.0 before deducting breakers
        score = min(100.0, score)
        for b in breakers:
            score -= b.penalty
            
        score = max(5.0, min(100.0, score))
        
        has_major_breaker = any(b.penalty >= 20.0 for b in breakers)
        if score >= 75.0 and not has_major_breaker:
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
