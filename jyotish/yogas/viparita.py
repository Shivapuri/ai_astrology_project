"""
jyotish/yogas/viparita.py
Viparita Raja Yogas (Reversal of Misfortune Royal Combinations).
Scripture: Phaladeepika Ch. 6, Verses 63, 65, 69 & BPHS Ch. 36.
"""

from typing import List, Dict, Any, Optional
from jyotish.yogas.models import (
    YogaInstance, YogaCategory, YogaStatus, YogaBreakerDetail
)
from jyotish.yogas.breakers import (
    get_house_of_planet, get_sign_of_planet, get_house_rulers, get_aspect_score,
    _first_ruler, audit_combustion, audit_dispositor_vitality,
    audit_shadbala_muscle, audit_neecha_bhanga, resolve_yoga_score_and_status,
    DEBILITATION_SIGNS, EXALTATION_SIGNS,
    ASPECT_PALPABLE_THRESHOLD, ASPECT_MARGINAL_THRESHOLD
)

VIPARITA_CONFIGS = {
    6: {
        "id": "harsha_yoga",
        "name": "Harṣa Viparīta Rāja Yoga",
        "scripture_ref": "Phaladeepika 6.63, BPHS 36.27",
        "archetype": "Cheerful Invincibility: The 6th lord trapped in a Duṣṭhāna destroys enemies and disease, granting joyful immunity.",
        "effects": [
            "Conquers opponents and competitors effortlessly; rivals exhaust and destroy themselves.",
            "Robust physical immunity, freedom from chronic debts, and cheerful disposition in adversity."
        ]
    },
    8: {
        "id": "sarala_yoga",
        "name": "Sarala Viparīta Rāja Yoga",
        "scripture_ref": "Phaladeepika 6.65, BPHS 36.27",
        "archetype": "Fearless Resilience: The 8th lord trapped in a Duṣṭhāna eliminates sudden catastrophes, bestowing fearless longevity.",
        "effects": [
            "Fearless mind, resilient longevity, and the ability to turn sudden crises into decisive victories.",
            "Gains through unexpected windfalls, research, esoteric knowledge, or outlasting competitors."
        ]
    },
    12: {
        "id": "vimala_yoga",
        "name": "Vimala Viparīta Rāja Yoga",
        "scripture_ref": "Phaladeepika 6.69, BPHS 36.27",
        "archetype": "Untouchable Purity & Savings: The 12th lord trapped in a Duṣṭhāna neutralizes ruinous expenditure, ensuring steady accumulation.",
        "effects": [
            "Protected from ruinous financial loss; frugal, self-contained, and financially independent.",
            "Spiritual contentment, righteous conduct, and happiness through noble service."
        ]
    }
}


def detect_viparita_raja_yogas(chart: Dict[str, Any]) -> List[YogaInstance]:
    """Scans for Harṣa (6L), Sarala (8L), and Vimala (12L) Viparīta Rāja Yogas."""
    detected: List[YogaInstance] = []
    house_rulers = get_house_rulers(chart)
    lagna_lord = _first_ruler(house_rulers, 1)
    if not lagna_lord:
        return detected

    for h_origin, config in VIPARITA_CONFIGS.items():
        lord = _first_ruler(house_rulers, h_origin)
        if not lord:
            continue

        h_placed = get_house_of_planet(chart, lord)
        if h_placed not in (6, 8, 12):
            continue

        p_sign = get_sign_of_planet(chart, lord)
        score = 85.0
        pos: List[str] = [f"Lord of H{h_origin} ({lord}) occupies Duṣṭhāna House {h_placed} ({p_sign})."]
        breakers: List[YogaBreakerDetail] = []

        # 1. Own-Sign (Svakṣetra) vs. Auspicious Co-Rulership Guard
        co_ruled_auspicious = [
            kh for kh in (1, 4, 5, 7, 9, 10)
            if lord in (house_rulers.get(kh) or [])
        ]
        if h_placed == h_origin:
            pos.append(f"Svakṣetra Containment: {lord} occupies its own Duṣṭhāna (H{h_origin}), containing and mastering the house's crises (+5%).")
            score += 5.0
        elif co_ruled_auspicious:
            if 1 in co_ruled_auspicious:
                breakers.append(YogaBreakerDetail(
                    factor="Lagna Co-Rulership Vulnerability",
                    culprit_planet=lord,
                    description=f"{lord} also rules Lagna (H1) and is placed in foreign Duṣṭhāna H{h_placed}, exposing physical vitality to friction alongside the reversal.",
                    penalty=20.0
                ))
            elif any(th in co_ruled_auspicious for th in (5, 9)):
                trik_h = [th for th in (5, 9) if th in co_ruled_auspicious][0]
                breakers.append(YogaBreakerDetail(
                    factor="Trikoṇa Co-Rulership Leakage",
                    culprit_planet=lord,
                    description=f"{lord} simultaneously rules auspicious Trikoṇa H{trik_h}; placement in foreign Duṣṭhāna H{h_placed} diverts fortune into crisis management.",
                    penalty=20.0
                ))
            else:
                kend_h = co_ruled_auspicious[0]
                breakers.append(YogaBreakerDetail(
                    factor="Kendra Co-Rulership Leakage",
                    culprit_planet=lord,
                    description=f"{lord} simultaneously rules Kendra H{kend_h}; placement in foreign Duṣṭhāna H{h_placed} injects structural friction.",
                    penalty=15.0
                ))

        if p_sign == EXALTATION_SIGNS.get(lord):
            pos.append(f"Exalted in {p_sign} (+5%).")
            score += 5.0
        elif p_sign == DEBILITATION_SIGNS.get(lord):
            is_rescued, r_reasons, _ = audit_neecha_bhanga(lord, chart)
            if is_rescued:
                pos.extend(r_reasons)
            else:
                breakers.append(YogaBreakerDetail(
                    factor="Unredeemed Debilitation of Reversal Lord",
                    culprit_planet=lord,
                    description=f"Duṣṭhāna lord {lord} is in fall in {p_sign} in H{h_placed} without cancellation, weakening its capacity to command the reversal.",
                    penalty=25.0
                ))

        # 2. Inverse Breaker: Contamination by an Auspicious Kendra/Trikoṇa Lord
        # Collect in deterministic house order and pick the strongest contamination
        kendra_trikona_lords: List[str] = []
        for kh in (1, 4, 5, 7, 9, 10):
            for kl in (house_rulers.get(kh) or []):
                if kl and kl != lord and kl not in kendra_trikona_lords:
                    kendra_trikona_lords.append(kl)

        best_contamination: Optional[YogaBreakerDetail] = None
        for ktl in kendra_trikona_lords:
            ktl_house = get_house_of_planet(chart, ktl)
            candidate: Optional[YogaBreakerDetail] = None

            if ktl_house == h_placed and h_placed > 0:
                candidate = YogaBreakerDetail(
                    factor="Auspicious Lord Contaminated",
                    culprit_planet=ktl,
                    description=f"Auspicious Kendra/Trikoṇa Lord {ktl} conjoins {lord} in House {h_placed}, absorbing the Duṣṭhāna damage.",
                    penalty=25.0
                )
            else:
                aspect_score = get_aspect_score(chart, ktl, lord)
                if aspect_score >= ASPECT_PALPABLE_THRESHOLD:
                    candidate = YogaBreakerDetail(
                        factor="Auspicious Lord Aspect Contamination",
                        culprit_planet=ktl,
                        description=f"Auspicious Lord {ktl} casts a strong {aspect_score:.0f}-Virūpa aspect on {lord}, linking noble houses with crisis.",
                        penalty=25.0
                    )
                elif aspect_score >= ASPECT_MARGINAL_THRESHOLD:
                    candidate = YogaBreakerDetail(
                        factor="Auspicious Lord Aspect Contamination (Marginal)",
                        culprit_planet=ktl,
                        description=f"Auspicious Lord {ktl} casts a marginal {aspect_score:.0f}-Virūpa aspect on {lord}.",
                        penalty=12.5
                    )

            if candidate and (best_contamination is None or candidate.penalty > best_contamination.penalty):
                best_contamination = candidate

        if best_contamination is not None:
            breakers.append(best_contamination)

        # 3. Pure Duṣṭhāna-Lord Conjunction Synergy (when another pure Duṣṭhāna lord conjoins in h_placed)
        for other_dh in (6, 8, 12):
            if other_dh == h_origin:
                continue
            other_dl = _first_ruler(house_rulers, other_dh)
            if other_dl and other_dl != lord and other_dl not in kendra_trikona_lords:
                if get_house_of_planet(chart, other_dl) == h_placed:
                    pos.append(f"Duṣṭhāna-Lord Synergy: {lord} (H{h_origin} lord) conjoins pure Duṣṭhāna lord {other_dl} (H{other_dh} lord) in H{h_placed} (+5%).")
                    score += 5.0

        # 4. Layer 2 Breakers per YOGA_ARCHITECTURE.md (NO audit_dusthana_placement!)
        breakers.extend(audit_combustion([lord], chart))
        breakers.extend(audit_dispositor_vitality([lord], chart))
        shad_brk, shad_pos = audit_shadbala_muscle([lord], chart)
        breakers.extend(shad_brk)
        pos.extend(shad_pos)

        net_score, status = resolve_yoga_score_and_status(score, breakers)

        detected.append(YogaInstance(
            id=config["id"],
            name=config["name"],
            category=YogaCategory.VIPARITA,
            status=status,
            plausibility_score=round(net_score, 1),
            participating_planets=[lord],
            participating_houses=[h_placed],
            scripture_ref=config["scripture_ref"],
            archetype=config["archetype"],
            manifestation_effects=config["effects"],
            positive_factors=pos,
            breakers=breakers
        ))

    return detected
