"""
jyotish/yogas/evaluator.py
Master Yoga Evaluator and Orchestration Engine.
Integrates all sub-modules, performs global deduplication, and computes chart-wide metrics.
"""

from typing import List, Dict, Any, Set
from jyotish.yogas.models import YogaInstance, YogaCategory, YogaStatus
from jyotish.yogas.pancha_mahapurusha import detect_pancha_mahapurusha_yogas
from jyotish.yogas.raja_yogas import detect_raja_yogas
from jyotish.yogas.dhana_daridrya import detect_dhana_and_daridrya_yogas
from jyotish.yogas.lunar_solar_yogas import detect_lunar_and_solar_yogas
from jyotish.yogas.parivartana import detect_parivartana_yogas
from jyotish.yogas.viparita import detect_viparita_raja_yogas
from jyotish.yogas.kartari import detect_kartari_yogas
from jyotish.yogas.chandal_yogas import detect_chandal_yogas
from jyotish.yogas.character_growth_yogas import detect_character_and_growth_yogas
from jyotish.yogas.dispositor_root_yogas import detect_dispositor_root_yogas
from jyotish.yogas.deity_yogas import detect_deity_yogas
from jyotish.yogas.bhava_yogas import detect_bhava_yogas
from jyotish.yogas.power_yogas import detect_chapter7_power_yogas
from jyotish.yogas.contextual_yogas import detect_contextual_yogas
from jyotish.yogas.neechabhanga import detect_neechabhanga_yogas

# Cross-module deduplication groups: maps variant IDs to a single canonical concept
CANONICAL_DUPLICATE_GROUPS = {
    "kemadruma_yoga": "KEMADRUMA",
    "kemadruma_bhanga_yoga": "KEMADRUMA",
    "mahabhagya_yoga": "MAHABHAGYA",
    "mahabhagya_male_yoga": "MAHABHAGYA",
    "mahabhagya_female_yoga": "MAHABHAGYA",
    "adhama_yoga": "SUN_MOON_QUADRANT",
    "madhya_yoga": "SUN_MOON_QUADRANT",
    "varishtha_yoga": "SUN_MOON_QUADRANT",
    "kendra_scope_yoga": "SUN_MOON_QUADRANT",
    "panaphara_scope_yoga": "SUN_MOON_QUADRANT",
    "apoklima_scope_yoga": "SUN_MOON_QUADRANT",
    "shubha_kartari_lagna": "KARTARI_LAGNA_SHUBHA",
    "subha_kartari_lagna": "KARTARI_LAGNA_SHUBHA",
    "shubhakartari_lagna_yoga": "KARTARI_LAGNA_SHUBHA",
    "shubha_kartari_lagna_(ascendant)": "KARTARI_LAGNA_SHUBHA",
    "papa_kartari_lagna": "KARTARI_LAGNA_PAPA",
    "papakartari_lagna_yoga": "KARTARI_LAGNA_PAPA",
    "papa_kartari_lagna_(ascendant)": "KARTARI_LAGNA_PAPA",
    "vesi_yoga": "SOLAR_VESI",
    "subha_vesi_yoga": "SOLAR_VESI",
    "papa_vesi_yoga": "SOLAR_VESI",
    "vosi_yoga": "SOLAR_VOSI",
    "subha_vosi_yoga": "SOLAR_VOSI",
    "papa_vosi_yoga": "SOLAR_VOSI",
    "ubhayacari_yoga": "SOLAR_UBHAYACARI",
    "ubhayachari_yoga": "SOLAR_UBHAYACARI",
    "subha_ubhayacari_yoga": "SOLAR_UBHAYACARI",
    "papa_ubhayacari_yoga": "SOLAR_UBHAYACARI",
    "misra_ubhayacari_yoga": "SOLAR_UBHAYACARI",
    "power_yoga_dharma_karma_exchange": "DHARMA_KARMA_EXCHANGE",
}


def detect_all_yogas(chart: Any) -> Dict[str, Any]:
    """
    Master entry point for Classical Yoga Detection in Astra.
    Scans the chart across all classical categories, audits Yoga Breakers,
    deduplicates overlapping definitions, and returns a structured, categorized payload.
    Supports either ChartPipeline or standard chart dict.
    """
    if hasattr(chart, "to_dict") and not isinstance(chart, dict):
        chart = chart.to_dict()
    raw_yogas: List[YogaInstance] = []

    # 1. Pancha Mahapurusha Yogas
    raw_yogas.extend(detect_pancha_mahapurusha_yogas(chart))

    # 2. Raja Yogas (Single-planet & Multi-planet)
    raw_yogas.extend(detect_raja_yogas(chart))

    # 3. Dhana & Daridrya Yogas
    raw_yogas.extend(detect_dhana_and_daridrya_yogas(chart))

    # 4. Lunar and Solar Yogas (Flanking, Sun-Moon quadrants, Candradhi, Lagnadhi)
    raw_yogas.extend(detect_lunar_and_solar_yogas(chart))

    # 5. Parivartana Yogas (Maha, Khala, Dainya)
    raw_yogas.extend(detect_parivartana_yogas(chart))

    # 6. Viparita Raja Yogas (Harsha, Sarala, Vimala)
    raw_yogas.extend(detect_viparita_raja_yogas(chart))

    # 7. Kartari Yogas (Universal Hemming)
    raw_yogas.extend(detect_kartari_yogas(chart))

    # 8. Chandal & Nodal Affliction Yogas
    raw_yogas.extend(detect_chandal_yogas(chart))

    # 9. Character & Growth Yogas (Vasumati, Amala, Puskala, Sakata)
    raw_yogas.extend(detect_character_and_growth_yogas(chart))

    # 10. Dispositor Root Yogas (Kahala Variants A/B, Parvata Authentic & Self-Dispositor)
    raw_yogas.extend(detect_dispositor_root_yogas(chart))

    # 11. Cosmic Deity Yogas (Trimurti, Tridevi, Mala)
    raw_yogas.extend(detect_deity_yogas(chart))

    # 12. 12 Bhava Good & Converse Yogas
    raw_yogas.extend(detect_bhava_yogas(chart))

    # 13. Chapter 7 Royal Power Yogas (Multi-Kendra, Digbala, Specific Power Yogas)
    raw_yogas.extend(detect_chapter7_power_yogas(chart))

    # 14. Contextual & Macro Setup Yogas (Sankhya, Solitary Bhavas, Dual-Lagna)
    raw_yogas.extend(detect_contextual_yogas(chart))

    # 15. Neechabhanga Yogas (Universal Debilitation Reversal & Cancellation)
    raw_yogas.extend(detect_neechabhanga_yogas(chart))

    # Dynamic Duplicate Grouping: 9th–10th Lord Parivartana Cross-Module Deduplication
    canonical_groups = dict(CANONICAL_DUPLICATE_GROUPS)
    from jyotish.yogas.breakers import get_house_rulers, get_house_of_planet
    house_rulers = get_house_rulers(chart)
    lord_9 = house_rulers.get(9, [None])[0]
    lord_10 = house_rulers.get(10, [None])[0]
    if lord_9 and lord_10 and lord_9 != lord_10:
        h9_pos = get_house_of_planet(chart, lord_9)
        h10_pos = get_house_of_planet(chart, lord_10)
        if h9_pos == 10 and h10_pos == 9:
            p1 = lord_9.lower()
            p2 = lord_10.lower()
            canonical_groups[f"maha_parivartana_{p1}_{p2}"] = "DHARMA_KARMA_EXCHANGE"
            canonical_groups[f"maha_parivartana_{p2}_{p1}"] = "DHARMA_KARMA_EXCHANGE"
            canonical_groups[f"dharma_karma_raja_yoga_{p1}_{p2}"] = "DHARMA_KARMA_EXCHANGE"
            canonical_groups[f"dharma_karma_raja_yoga_{p2}_{p1}"] = "DHARMA_KARMA_EXCHANGE"

    # Global Deduplication
    seen_ids: Set[str] = set()
    seen_canonical_groups: Set[str] = set()
    deduped_yogas: List[YogaInstance] = []

    for yoga in raw_yogas:
        if yoga.id in seen_ids:
            continue

        group_key = canonical_groups.get(yoga.id)
        if group_key:
            if group_key in seen_canonical_groups:
                continue
            seen_canonical_groups.add(group_key)

        seen_ids.add(yoga.id)
        deduped_yogas.append(yoga)

    # Sort by plausibility score descending
    deduped_yogas.sort(key=lambda y: y.plausibility_score, reverse=True)

    pure_count = sum(1 for y in deduped_yogas if y.status == YogaStatus.PURE)
    stained_count = sum(1 for y in deduped_yogas if y.status == YogaStatus.STAINED)
    rescued_count = sum(1 for y in deduped_yogas if y.status == YogaStatus.RESCUED)
    broken_count = sum(1 for y in deduped_yogas if y.status == YogaStatus.BROKEN)

    categories = [cat.value for cat in YogaCategory]

    return {
        "total_count": len(deduped_yogas),
        "summary": {
            "pure": pure_count,
            "stained": stained_count,
            "rescued": rescued_count,
            "broken": broken_count
        },
        "yogas": [y.to_dict() for y in deduped_yogas],
        "categories": categories
    }
