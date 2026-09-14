"""
jyotish/yogas/raja_yogas.py
Raja Yogas (Royal Combinations for Worldly Status, Authority & Purpose).
Scripture: BPHS Ch. 34 (Yogakarakas), Ch. 39-40 (Raja Yogas), Phaladeepika Ch. 7.
"""

from typing import List, Dict, Any, Tuple
from jyotish.yogas.models import (
    YogaInstance, YogaCategory, YogaStatus, YogaBreakerDetail
)
from jyotish.yogas.breakers import (
    get_house_of_planet, get_sign_of_planet, get_house_rulers, get_planets_data,
    get_lagna_sign, get_aspect_score,
    audit_trishadaya_interference, audit_combustion,
    audit_neecha_bhanga, audit_dusthana_placement, audit_shadbala_muscle,
    DEBILITATION_SIGNS, EXALTATION_SIGNS
)

# Single Planet Raja Yoga Karakas (simultaneous Kendra + Trikona lords)
SINGLE_PLANET_YOGAKARAKAS = {
    "Taurus": ("Saturn", [9, 10]),
    "Cancer": ("Mars", [5, 10]),
    "Leo": ("Mars", [4, 9]),
    "Libra": ("Saturn", [4, 5]),
    "Capricorn": ("Venus", [5, 10]),
    "Aquarius": ("Venus", [4, 9])
}

KENDRA_HOUSES = [1, 4, 7, 10]
TRIKONA_HOUSES = [1, 5, 9]

def detect_raja_yogas(chart: Dict[str, Any]) -> List[YogaInstance]:
    """Scans chart for single-planet and multi-planet Raja Yogas."""
    detected = []
    lagna_sign = get_lagna_sign(chart)
    house_rulers = get_house_rulers(chart)
    planets_data = get_planets_data(chart)
    
    # 1. Single-Planet Raja Yoga Karaka
    if lagna_sign in SINGLE_PLANET_YOGAKARAKAS:
        yk_planet, owned_houses = SINGLE_PLANET_YOGAKARAKAS[lagna_sign]
        if yk_planet in planets_data:
            yk_house = get_house_of_planet(chart, yk_planet)
            yk_sign = get_sign_of_planet(chart, yk_planet)
            
            score = 85.0
            positive_factors = [
                f"Natural Yogakāraka: {yk_planet} simultaneously rules Kendra H{owned_houses[0]} and Trikona H{owned_houses[1]} for {lagna_sign} Lagna.",
                f"Resides in House {yk_house} ({yk_sign})."
            ]
            
            if yk_house in (1, 4, 5, 7, 9, 10, 11):
                positive_factors.append(f"Favorable seat: Resides in supportive House {yk_house}.")
                score += 5.0
            if yk_sign == EXALTATION_SIGNS.get(yk_planet):
                positive_factors.append(f"Exalted in {yk_sign}.")
                score += 10.0
                
            breakers = []
            # Check Debilitation / Neecha Bhanga
            if yk_sign == DEBILITATION_SIGNS.get(yk_planet):
                is_rescued, reasons, bonus = audit_neecha_bhanga(yk_planet, chart)
                if is_rescued:
                    positive_factors.extend(reasons)
                    score += bonus * 0.3
                else:
                    breakers.append(YogaBreakerDetail(
                        factor="Unredeemed Debilitation",
                        culprit_planet=yk_planet,
                        description=f"Yogakāraka {yk_planet} is in fall in {yk_sign} without cancellation.",
                        penalty=45.0
                    ))
                    
            breakers.extend(audit_trishadaya_interference([yk_planet], chart))
            breakers.extend(audit_combustion([yk_planet], chart))
            dust_brk = audit_dusthana_placement([yk_house], "Raja Yoga")
            if dust_brk:
                breakers.append(dust_brk)
            shad_brk, shad_pos = audit_shadbala_muscle([yk_planet], chart)
            breakers.extend(shad_brk)
            positive_factors.extend(shad_pos)
            
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
                id=f"single_yogakaraka_{yk_planet.lower()}",
                name=f"Rāja Yogakāraka ({yk_planet})",
                category=YogaCategory.RAJA,
                status=status,
                plausibility_score=round(score, 1),
                participating_planets=[yk_planet],
                participating_houses=[yk_house],
                scripture_ref="BPHS 34.15-20, Phaladeepika 7.4",
                archetype=f"The Natural Sovereign: {yk_planet} embodies both divine grace (Trikona) and executive horsepower (Kendra) within a single body.",
                manifestation_effects=[
                    f"Elevates {lagna_sign} natives into leadership, worldly recognition, and institutional respect.",
                    f"Functions as the primary driver of worldly fortune during {yk_planet}'s Daśā periods."
                ],
                positive_factors=positive_factors,
                breakers=breakers
            ))
            
    # 2. Multi-Planet Alliances (Dharma-Karma Adhipati and Kendra-Trikona Alliances)
    # Gather pairs of (kendra_lord, trikona_lord)
    kendra_lords = {}
    for kh in KENDRA_HOUSES:
        for lord in house_rulers.get(kh, []):
            kendra_lords.setdefault(lord, []).append(kh)
            
    trikona_lords = {}
    for th in TRIKONA_HOUSES:
        for lord in house_rulers.get(th, []):
            trikona_lords.setdefault(lord, []).append(th)
            
    evaluated_pairs = set()
    
    for kl, k_houses in kendra_lords.items():
        for tl, t_houses in trikona_lords.items():
            if kl == tl:
                continue  # Single planet handled above
            pair_key = tuple(sorted([kl, tl]))
            if pair_key in evaluated_pairs:
                continue
            evaluated_pairs.add(pair_key)
            
            kl_house = get_house_of_planet(chart, kl)
            tl_house = get_house_of_planet(chart, tl)
            if kl_house == 0 or tl_house == 0:
                continue
                
            is_conjoined = (kl_house == tl_house)
            aspect_kl_tl = get_aspect_score(chart, kl, tl)
            aspect_tl_kl = get_aspect_score(chart, tl, kl)
            is_mutual_aspect = (aspect_kl_tl >= 30.0 and aspect_tl_kl >= 30.0)
            
            # Check Sign Exchange (Parivartana)
            kl_sign = get_sign_of_planet(chart, kl)
            tl_sign = get_sign_of_planet(chart, tl)
            is_exchange = (get_house_rulers(chart).get(kl_house, [None])[0] == tl and
                           get_house_rulers(chart).get(tl_house, [None])[0] == kl)
                           
            if not (is_conjoined or is_mutual_aspect or is_exchange):
                continue
                
            is_supreme = (9 in t_houses and 10 in k_houses)
            yoga_title = "Dharma-Karma Adhipati Rāja Yoga" if is_supreme else f"Kendra-Trikona Rāja Yoga ({kl} + {tl})"
            yoga_id = f"raja_yoga_{kl.lower()}_{tl.lower()}"
            
            score = 90.0 if is_supreme else 80.0
            positive_factors = []
            
            if is_supreme:
                positive_factors.append(f"Supreme Alliance: {tl} (Lord of H9 Dharma) and {kl} (Lord of H10 Karma) combine.")
            else:
                positive_factors.append(f"Kendra-Trikona Union: {kl} (Lord of H{k_houses}) and {tl} (Lord of H{t_houses}) combine.")
                
            if is_conjoined:
                positive_factors.append(f"Conjoined in House {kl_house}.")
            elif is_mutual_aspect:
                positive_factors.append(f"Mutual Aspect: {kl} and {tl} gaze upon each other ({aspect_kl_tl:.0f} & {aspect_tl_kl:.0f} Virupas).")
            elif is_exchange:
                positive_factors.append(f"Mutual Reception (Parivartana): {kl} and {tl} exchange signs.")
                score += 5.0
                
            # Breakers
            breakers = []
            breakers.extend(audit_trishadaya_interference([kl, tl], chart, is_supreme_pairing=is_supreme))
            breakers.extend(audit_combustion([kl, tl], chart))
            dust_brk = audit_dusthana_placement([kl_house, tl_house], "Raja Yoga")
            if dust_brk:
                breakers.append(dust_brk)
            shad_brk, shad_pos = audit_shadbala_muscle([kl, tl], chart)
            breakers.extend(shad_brk)
            positive_factors.extend(shad_pos)
            
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
                id=yoga_id,
                name=yoga_title,
                category=YogaCategory.RAJA,
                status=status,
                plausibility_score=round(score, 1),
                participating_planets=[kl, tl],
                participating_houses=list(set([kl_house, tl_house])),
                scripture_ref="BPHS 39.1-15, Phaladeepika 7.8-10",
                archetype="The Marriage of Grace and Action: Harmonizes ethical purpose (Dharma) with worldly executive platform (Karma).",
                manifestation_effects=[
                    "Commands respect, social influence, professional eminence, and leadership in large organizations.",
                    "Manifests major career breakthroughs during the conjoined or operational Daśā periods."
                ],
                positive_factors=positive_factors,
                breakers=breakers
            ))
            
    return detected
