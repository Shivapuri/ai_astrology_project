"""
jyotish/yogas/kartari.py
Kartarī Yogas (The Universal Hemming Principle — Hemisphere A: Pure Foundational Calculus).

Scripture: Phaladeepika Ch. 6, Verses 7 & 11-13; BPHS Ch. 34.
Architecture: Strictly adheres to YOGA_ARCHITECTURE.md Category 10 (KARTARI):
- Zero generic Layer 2 breakers (no Trishadaya, Dusthana, Combustion, Dispositor, or Shadbala).
- Verifies strict benefic/malefic purity of BOTH the 2nd AND 12th houses around Lagna (and Moon).
- Evaluates opposing/direct aspects onto the hemmed focal point (Suśubha enhancement vs. benefic rescue mitigation).
- Enforces Affliction Status Invariant: Pāpa Kartarī is STAINED when unmitigated and RESCUED when mitigated by a strong benefic aspect/occupant — NEVER PURE.
"""

from typing import List, Dict, Any, Set
from jyotish.yogas.models import (
    YogaInstance, YogaCategory, YogaStatus, YogaBreakerDetail
)
from jyotish.yogas.breakers import (
    get_lagna_sign, get_house_of_planet, get_planets_data, get_aspect_score,
    NATURAL_BENEFICS, NATURAL_MALEFICS, ZODIAC_SIGNS,
    ASPECT_PALPABLE_THRESHOLD
)

VALID_KARTARI_GRAHAS: Set[str] = set(NATURAL_BENEFICS) | set(NATURAL_MALEFICS)


def detect_kartari_yogas(chart: Dict[str, Any]) -> List[YogaInstance]:
    """
    Scans for Śubha Kartarī (protective benefic hemming) and Pāpa Kartarī (restrictive malefic scissors)
    around Lagna and Moon, including Suśubha aspect reinforcement and benefic aspect mitigation.
    """
    detected: List[YogaInstance] = []
    planets_data = get_planets_data(chart)
    planet_houses = {p: get_house_of_planet(chart, p) for p in planets_data}

    lagna_sign = get_lagna_sign(chart)
    moon_house = planet_houses.get("Moon", 0)

    targets = []
    if lagna_sign and lagna_sign in ZODIAC_SIGNS:
        targets.append(("Lagna (Ascendant)", 1, "Ascendant / Physical Vessel", "Lagna"))
    if moon_house > 0:
        targets.append(("Moon (Chandra)", moon_house, "Emotional Mind / Manas", "Moon"))

    for target_name, target_house, domain, target_key in targets:
        h2 = (target_house % 12) + 1
        h12 = ((target_house - 2) % 12) + 1

        # Filter strictly to recognized classical grahas + nodes in H2 and H12
        planets_h2 = [
            p for p in planets_data
            if p in VALID_KARTARI_GRAHAS and planet_houses.get(p) == h2 and p != target_key
        ]
        planets_h12 = [
            p for p in planets_data
            if p in VALID_KARTARI_GRAHAS and planet_houses.get(p) == h12 and p != target_key
        ]

        if not (planets_h2 and planets_h12):
            continue

        h2_benefics = [p for p in planets_h2 if p in NATURAL_BENEFICS]
        h12_benefics = [p for p in planets_h12 if p in NATURAL_BENEFICS]
        h2_malefics = [p for p in planets_h2 if p in NATURAL_MALEFICS]
        h12_malefics = [p for p in planets_h12 if p in NATURAL_MALEFICS]

        # Check occupants and palpable aspects (Suśubha / Mitigation) onto the hemmed focal point
        focal_occupants = [
            p for p in planets_data
            if p in VALID_KARTARI_GRAHAS and planet_houses.get(p) == target_house and p != target_key
        ]
        benefic_protectors = [p for p in focal_occupants if p in NATURAL_BENEFICS]
        malefic_afflictors = [p for p in focal_occupants if p in NATURAL_MALEFICS]

        for p in planets_data:
            if p not in VALID_KARTARI_GRAHAS or p == target_key or p in focal_occupants:
                continue
            if get_aspect_score(chart, p, target_key) >= ASPECT_PALPABLE_THRESHOLD:
                if p in NATURAL_BENEFICS and p not in benefic_protectors:
                    benefic_protectors.append(p)
                elif p in NATURAL_MALEFICS and p not in malefic_afflictors:
                    malefic_afflictors.append(p)

        # 1. Śubha Kartarī: BOTH H2 and H12 occupied exclusively by natural benefics (zero malefics)
        if h2_benefics and h12_benefics and not h2_malefics and not h12_malefics:
            flanking_benefics = h12_benefics + h2_benefics
            score = 90.0
            pos = [
                f"Natural benefics exclusively flank {target_name} in H{h12} ({', '.join(h12_benefics)}) and H{h2} ({', '.join(h2_benefics)})."
            ]
            breakers: List[YogaBreakerDetail] = []

            is_sushubha = bool(benefic_protectors and not malefic_afflictors)
            if is_sushubha:
                score = 95.0
                pos.append(
                    f"Suśubha Confluence: {target_name} is additionally fortified by benefic influence from {', '.join(benefic_protectors)}."
                )

            if malefic_afflictors:
                breakers.append(YogaBreakerDetail(
                    factor="Malefic Intrusion on Hemmed Focal Point",
                    culprit_planet=", ".join(malefic_afflictors),
                    description=(
                        f"Although flanked by benefics, {target_name} is occupied or palpably aspected by malefic(s) ({', '.join(malefic_afflictors)})."
                    ),
                    penalty=20.0
                ))
                score -= 20.0

            status = YogaStatus.PURE if (score >= 75.0 and not breakers) else YogaStatus.STAINED
            yoga_label = "Suśubha Kartarī Yoga" if is_sushubha else "Śubha Kartarī Yoga"

            detected.append(YogaInstance(
                id=f"shubha_kartari_{target_name.split()[0].lower()}",
                name=f"{yoga_label} ({target_name})",
                category=YogaCategory.KARTARI,
                status=status,
                plausibility_score=round(score, 1),
                participating_planets=flanking_benefics,
                participating_houses=[h12, target_house, h2],
                scripture_ref="Phaladeepika 6.7, 6.11",
                archetype=f"The Protective Shield: {target_name} is cushioned on both sides by natural benefics, granting ease and continuous support.",
                manifestation_effects=[
                    f"Surrounds the {domain} with psychological safety, resource support, and physical vitality.",
                    "Quick recovery from life setbacks and natural protection from hostility."
                ],
                positive_factors=pos,
                breakers=breakers
            ))

        # 2. Pāpa Kartarī: BOTH H2 and H12 occupied exclusively by natural malefics (zero benefics)
        elif h2_malefics and h12_malefics and not h2_benefics and not h12_benefics:
            flanking_malefics = h12_malefics + h2_malefics
            pos = []
            breakers = [YogaBreakerDetail(
                factor="Malefic Scissors (Pāpa Kartarī)",
                culprit_planet=", ".join(flanking_malefics),
                description=f"Natural malefics flank H{h12} ({', '.join(h12_malefics)}) and H{h2} ({', '.join(h2_malefics)}), compressing {target_name}.",
                penalty=35.0
            )]

            # Benefic occupant or palpable aspect on the hemmed house rescues the native (never PURE)
            is_rescued = bool(benefic_protectors)
            if is_rescued:
                pos.append(
                    f"Mitigated by benefic protection ({', '.join(benefic_protectors)}) occupying or palpably aspecting {target_name}."
                )
                status = YogaStatus.RESCUED
                score = 55.0
            else:
                status = YogaStatus.STAINED
                score = 75.0

            detected.append(YogaInstance(
                id=f"papa_kartari_{target_name.split()[0].lower()}",
                name=f"Pāpa Kartarī Yoga ({target_name})" + (" (Mitigated)" if is_rescued else ""),
                category=YogaCategory.KARTARI,
                status=status,
                plausibility_score=round(score, 1),
                participating_planets=flanking_malefics,
                participating_houses=[h12, target_house, h2],
                scripture_ref="Phaladeepika 6.7, 6.12-13",
                archetype=f"The Scissor Squeeze: {target_name} is hemmed on both sides by malefics, producing pressure and restriction.",
                manifestation_effects=[
                    f"Creates tension, obstacles, and a feeling of being boxed in regarding the {domain}.",
                    "Demands conscious emotional discipline, boundary-setting, and perseverance."
                ],
                positive_factors=pos,
                breakers=breakers
            ))

    return detected
