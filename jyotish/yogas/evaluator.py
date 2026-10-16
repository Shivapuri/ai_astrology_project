"""
jyotish/yogas/evaluator.py
Master Yoga Evaluator and Orchestration Engine.
Integrates all sub-modules, performs global deduplication, and computes chart-wide metrics.
"""

from typing import List, Dict, Any, Set
from jyotish.yogas.models import YogaInstance, YogaCategory, YogaStatus
from jyotish.yogas.breakers import (
    get_house_rulers, get_house_of_planet, get_lagna_sign, get_planets_data, _first_ruler
)
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
    # Kemadruma variants
    "kemadruma_yoga": "KEMADRUMA",
    "kemadruma_bhanga_yoga": "KEMADRUMA",
    # Mahabhagya variants
    "mahabhagya_yoga": "MAHABHAGYA",
    "mahabhagya_male_yoga": "MAHABHAGYA",
    "mahabhagya_female_yoga": "MAHABHAGYA",
    # Sun-Moon Quadrant Scope variants
    "adhama_yoga": "SUN_MOON_QUADRANT",
    "madhya_yoga": "SUN_MOON_QUADRANT",
    "sama_yoga": "SUN_MOON_QUADRANT",
    "varishtha_yoga": "SUN_MOON_QUADRANT",
    "kendra_scope_yoga": "SUN_MOON_QUADRANT",
    "panaphara_scope_yoga": "SUN_MOON_QUADRANT",
    "apoklima_scope_yoga": "SUN_MOON_QUADRANT",
    # Kartari variants
    "shubha_kartari_lagna": "KARTARI_LAGNA_SHUBHA",
    "subha_kartari_lagna": "KARTARI_LAGNA_SHUBHA",
    "shubhakartari_lagna_yoga": "KARTARI_LAGNA_SHUBHA",
    "shubha_kartari_lagna_(ascendant)": "KARTARI_LAGNA_SHUBHA",
    "papa_kartari_lagna": "KARTARI_LAGNA_PAPA",
    "papakartari_lagna_yoga": "KARTARI_LAGNA_PAPA",
    "papa_kartari_lagna_(ascendant)": "KARTARI_LAGNA_PAPA",
    "shubha_kartari_moon": "KARTARI_MOON_SHUBHA",
    "papa_kartari_moon": "KARTARI_MOON_PAPA",
    # Solar Flanking variants
    "vesi_yoga": "SOLAR_VESI",
    "subha_vesi_yoga": "SOLAR_VESI",
    "papa_vesi_yoga": "SOLAR_VESI",
    "vosi_yoga": "SOLAR_VOSI",
    "vasi_yoga": "SOLAR_VOSI",
    "subha_vosi_yoga": "SOLAR_VOSI",
    "papa_vosi_yoga": "SOLAR_VOSI",
    "ubhayacari_yoga": "SOLAR_UBHAYACARI",
    "ubhayachari_yoga": "SOLAR_UBHAYACARI",
    "subha_ubhayacari_yoga": "SOLAR_UBHAYACARI",
    "papa_ubhayacari_yoga": "SOLAR_UBHAYACARI",
    "misra_ubhayacari_yoga": "SOLAR_UBHAYACARI",
    # Lakshmi Yoga cross-module overlap (dhana_daridrya.py vs deity_yogas.py)
    "lakshmi_yoga": "LAKSHMI_YOGA",
    "tridevi_lakshmi_yoga": "LAKSHMI_YOGA",
    "deity_lakshmi_yoga": "LAKSHMI_YOGA",
    # Viparita vs Bhava 6/8/12 Reversal overlap (viparita.py vs bhava_yogas.py)
    "harsha_viparita_yoga": "VIPARITA_HARSHA",
    "harsha_yoga": "VIPARITA_HARSHA",
    "sarala_viparita_yoga": "VIPARITA_SARALA",
    "sarala_yoga": "VIPARITA_SARALA",
    "vimala_viparita_yoga": "VIPARITA_VIMALA",
    "vimala_yoga": "VIPARITA_VIMALA",
    # Dharma-Karmadhipati Exchange (raja_yogas.py vs parivartana.py vs power_yogas.py)
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
    if not isinstance(chart, dict):
        chart = {}

    categories = [cat.value for cat in YogaCategory]

    # Guard against empty chart payloads or missing Lagna/planets data
    if not get_lagna_sign(chart) or not get_planets_data(chart):
        return {
            "total_count": 0,
            "summary": {
                "pure": 0,
                "stained": 0,
                "rescued": 0,
                "broken": 0
            },
            "yogas": [],
            "categories": categories
        }

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
    house_rulers = get_house_rulers(chart)
    lord_9 = _first_ruler(house_rulers, 9)
    lord_10 = _first_ruler(house_rulers, 10)
    if lord_9 and lord_10 and lord_9 != lord_10:
        h9_pos = get_house_of_planet(chart, lord_9)
        h10_pos = get_house_of_planet(chart, lord_10)
        if h9_pos == 10 and h10_pos == 9:
            p1 = lord_9.lower()
            p2 = lord_10.lower()
            for prefix in (
                "maha_parivartana",
                "dharma_karma_raja_yoga",
                "dharma_karmadhipati_yoga",
                "dharma_karmadhipati_raja_yoga",
                "raja_yoga",
            ):
                canonical_groups[f"{prefix}_{p1}_{p2}"] = "DHARMA_KARMA_EXCHANGE"
                canonical_groups[f"{prefix}_{p2}_{p1}"] = "DHARMA_KARMA_EXCHANGE"

    # Global Deduplication (retaining first-seen canonical group after prioritizing more complete/higher-plausibility instances)
    seen_ids: Set[str] = set()
    seen_canonical_groups: Set[str] = set()
    deduped_yogas: List[YogaInstance] = []

    for yoga in raw_yogas:
        if not isinstance(yoga, YogaInstance):
            continue
        if yoga.id in seen_ids:
            continue

        group_key = canonical_groups.get(yoga.id)
        if group_key:
            if group_key in seen_canonical_groups:
                continue
            seen_canonical_groups.add(group_key)

        seen_ids.add(yoga.id)
        deduped_yogas.append(yoga)

    # Deterministic sort by plausibility score descending, then ID ascending
    deduped_yogas.sort(key=lambda y: (-float(y.plausibility_score or 0.0), str(y.id or "")))

    pure_count = sum(1 for y in deduped_yogas if y.status == YogaStatus.PURE)
    stained_count = sum(1 for y in deduped_yogas if y.status == YogaStatus.STAINED)
    rescued_count = sum(1 for y in deduped_yogas if y.status == YogaStatus.RESCUED)
    broken_count = sum(1 for y in deduped_yogas if y.status == YogaStatus.BROKEN)

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
