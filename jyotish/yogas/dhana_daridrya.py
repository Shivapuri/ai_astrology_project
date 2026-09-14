"""
jyotish/yogas/dhana_daridrya.py
Dhana (Wealth) and Daridrya (Poverty/Depletion) Yogas.
Scripture: BPHS Ch. 41 (Vishesha Dhana Yoga), Ch. 42 (Daridrya Yoga), Phaladeepika Ch. 6.
"""

from typing import List, Dict, Any
from jyotish.yogas.models import (
    YogaInstance, YogaCategory, YogaStatus, YogaBreakerDetail
)
from jyotish.yogas.breakers import (
    get_house_of_planet, get_sign_of_planet, get_house_rulers, get_planets_data,
    get_aspect_score,
    audit_trishadaya_interference, audit_combustion, audit_shadbala_muscle,
    EXALTATION_SIGNS, OWN_SIGNS, DEBILITATION_SIGNS
)

DHANA_HOUSES = [1, 2, 5, 9, 11]

def detect_dhana_and_daridrya_yogas(chart: Dict[str, Any]) -> List[YogaInstance]:
    """Scans chart for wealth (Dhana) and poverty/depletion (Daridrya) yogas."""
    detected = []
    house_rulers = get_house_rulers(chart)
    planets_data = get_planets_data(chart)
    
    lord_1 = house_rulers.get(1, [None])[0]
    lord_2 = house_rulers.get(2, [None])[0]
    lord_5 = house_rulers.get(5, [None])[0]
    lord_9 = house_rulers.get(9, [None])[0]
    lord_11 = house_rulers.get(11, [None])[0]
    
    # -------------------------------------------------------------
    # 1. LAKSHMI YOGA (9th Lord + Venus fortified in Kendras/Trikonas)
    # -------------------------------------------------------------
    if lord_9 and "Venus" in planets_data:
        l9_house = get_house_of_planet(chart, lord_9)
        l9_sign = get_sign_of_planet(chart, lord_9)
        v_house = get_house_of_planet(chart, "Venus")
        v_sign = get_sign_of_planet(chart, "Venus")
        
        is_l9_strong = (l9_house in (1, 4, 5, 7, 9, 10)) and (l9_sign == EXALTATION_SIGNS.get(lord_9) or l9_sign in OWN_SIGNS.get(lord_9, []))
        is_v_strong = (v_house in (1, 4, 5, 7, 9, 10)) and (v_sign == EXALTATION_SIGNS.get("Venus") or v_sign in OWN_SIGNS.get("Venus", []))
        
        if is_l9_strong and is_v_strong:
            score = 95.0
            detected.append(YogaInstance(
                id="lakshmi_yoga",
                name="Lakṣmī Yoga",
                category=YogaCategory.DHANA,
                status=YogaStatus.PURE,
                plausibility_score=score,
                participating_planets=list(set([lord_9, "Venus"])),
                participating_houses=list(set([l9_house, v_house])),
                scripture_ref="Phaladeepika 6.28-29",
                archetype="The Golden Grace: Bestows boundless wealth, aesthetic charm, virtuous livelihood, and noble character.",
                manifestation_effects=[
                    "Immense wealth, royal vehicles, widespread social goodwill, and ethical integrity.",
                    "Enjoyment of all life comforts without loss of moral principles."
                ],
                positive_factors=[
                    f"9th Lord {lord_9} is fortified in House {l9_house} ({l9_sign}).",
                    f"Venus is fortified in House {v_house} ({v_sign})."
                ],
                breakers=[]
            ))
            
    # -------------------------------------------------------------
    # 2. CORE DHANA YOGAS (Interlocking 1, 2, 5, 9, 11 lords)
    # -------------------------------------------------------------
    dhana_pairs = [
        (lord_2, lord_11, "Treasury (H2) & Profit (H11) Alliance"),
        (lord_1, lord_2, "Self (H1) & Wealth (H2) Union"),
        (lord_5, lord_9, "Supreme Trinal Merit (H5 & H9) Fusion"),
        (lord_2, lord_9, "Wealth (H2) & Divine Fortune (H9) Alliance"),
        (lord_5, lord_11, "Intellect (H5) & Large Gains (H11) Polarity")
    ]
    
    evaluated_dhana = set()
    for p1, p2, desc in dhana_pairs:
        if not p1 or not p2 or p1 == p2:
            continue
        key = tuple(sorted([p1, p2]))
        if key in evaluated_dhana:
            continue
        evaluated_dhana.add(key)
        
        h1 = get_house_of_planet(chart, p1)
        h2 = get_house_of_planet(chart, p2)
        if h1 == 0 or h2 == 0:
            continue
            
        is_conj = (h1 == h2)
        aspect_val = max(get_aspect_score(chart, p1, p2), get_aspect_score(chart, p2, p1))
        is_aspect = (aspect_val >= 30.0)
        
        if is_conj or is_aspect:
            score = 85.0
            pos = [f"{desc}: {p1} and {p2} combine in House {h1}." if is_conj else f"{desc}: {p1} and {p2} aspect mutually ({aspect_val:.0f} Virupas)."]
            breakers = []
            
            # Dusthana check
            if h1 in (6, 8, 12) or h2 in (6, 8, 12):
                breakers.append(YogaBreakerDetail(
                    factor="Wealth Trapped in Dusthana",
                    culprit_planet="House Placement",
                    description=f"Dhana combination resides in House {h1}/{h2}. Wealth fluctuates through litigation, debts, or foreign expenditure.",
                    penalty=25.0
                ))
                score -= 25.0
                
            breakers.extend(audit_combustion([p1, p2], chart))
            for b in breakers:
                score -= b.penalty
            score = max(10.0, min(100.0, score))
            
            status = YogaStatus.PURE if score >= 75 else YogaStatus.STAINED
            
            detected.append(YogaInstance(
                id=f"dhana_yoga_{p1.lower()}_{p2.lower()}",
                name=f"Dhana Yoga ({p1} + {p2})",
                category=YogaCategory.DHANA,
                status=status,
                plausibility_score=round(score, 1),
                participating_planets=[p1, p2],
                participating_houses=list(set([h1, h2])),
                scripture_ref="BPHS 41.1-12",
                archetype="Resource Flow: Systematic connection between wealth, earnings, intellect, and fortune.",
                manifestation_effects=[
                    "Substantial capacity to generate, retain, and expand financial assets.",
                    "High earnings during the conjoined or operational Daśā periods."
                ],
                positive_factors=pos,
                breakers=breakers
            ))
            
    # -------------------------------------------------------------
    # 3. DARIDRYA YOGAS (POVERTY & LEAKAGE - BPHS Ch. 42)
    # -------------------------------------------------------------
    # Rule 1: 2nd or 11th lord trapped in 6, 8, or 12
    for p_lord, h_num in [(lord_2, 2), (lord_11, 11)]:
        if not p_lord:
            continue
        h_pos = get_house_of_planet(chart, p_lord)
        if h_pos in (6, 8, 12):
            sign_pos = get_sign_of_planet(chart, p_lord)
            is_deb = (sign_pos == DEBILITATION_SIGNS.get(p_lord))
            score = 65.0 if is_deb else 45.0
            
            detected.append(YogaInstance(
                id=f"daridrya_h{h_num}_{p_lord.lower()}",
                name=f"Dāridrya Yoga (H{h_num} Lord {p_lord} in H{h_pos})",
                category=YogaCategory.DARIDRYA,
                status=YogaStatus.STAINED,
                plausibility_score=score,
                participating_planets=[p_lord],
                participating_houses=[h_pos],
                scripture_ref="BPHS 42.1-5",
                archetype="Financial Leakage: Ruler of earnings or treasury sits in a Dusthana of loss, debt, or crisis.",
                manifestation_effects=[
                    "Tendency for wealth to leak into sudden expenses, medical bills, legal battles, or bad debts.",
                    "Requires strict conscious budgeting and avoiding speculative gambles."
                ],
                positive_factors=[],
                breakers=[YogaBreakerDetail(
                    factor=f"Lord of H{h_num} in Dusthana H{h_pos}",
                    culprit_planet=p_lord,
                    description=f"{p_lord} (ruler of House {h_num}) is relegated to House {h_pos}, causing financial drains.",
                    penalty=30.0
                )]
            ))
            
    return detected
