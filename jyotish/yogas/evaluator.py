"""
jyotish/yogas/evaluator.py
Master Yoga Evaluator and Orchestration Engine.
Integrates all sub-modules, performs global deduplication, and computes chart-wide metrics.
"""

from typing import List, Dict, Any
from jyotish.yogas.models import YogaInstance, YogaCategory, YogaStatus
from jyotish.yogas.pancha_mahapurusha import detect_pancha_mahapurusha_yogas
from jyotish.yogas.raja_yogas import detect_raja_yogas
from jyotish.yogas.dhana_daridrya import detect_dhana_and_daridrya_yogas
from jyotish.yogas.lunar_solar_yogas import detect_lunar_and_solar_yogas
from jyotish.yogas.parivartana import detect_parivartana_yogas
from jyotish.yogas.viparita import detect_viparita_raja_yogas
from jyotish.yogas.kartari import detect_kartari_yogas
from jyotish.yogas.chandal_yogas import detect_chandal_yogas

def detect_all_yogas(chart: Dict[str, Any]) -> Dict[str, Any]:
    """
    Master entry point for Classical Yoga Detection in Astra.
    Scans the chart across all 9 classical categories, audits Yoga Breakers,
    and returns a structured, categorized payload.
    """
    all_yogas: List[YogaInstance] = []
    
    # 1. Pancha Mahapurusha Yogas
    all_yogas.extend(detect_pancha_mahapurusha_yogas(chart))
    
    # 2. Raja Yogas (Single-planet & Multi-planet)
    all_yogas.extend(detect_raja_yogas(chart))
    
    # 3. Dhana & Daridrya Yogas
    all_yogas.extend(detect_dhana_and_daridrya_yogas(chart))
    
    # 4. Lunar and Solar Yogas
    all_yogas.extend(detect_lunar_and_solar_yogas(chart))
    
    # 5. Parivartana Yogas
    all_yogas.extend(detect_parivartana_yogas(chart))
    
    # 6. Viparita Raja Yogas
    all_yogas.extend(detect_viparita_raja_yogas(chart))
    
    # 7. Kartari Yogas
    all_yogas.extend(detect_kartari_yogas(chart))
    
    # 8. Chandal & Nodal Affliction Yogas
    all_yogas.extend(detect_chandal_yogas(chart))
    
    # Sort by plausibility score descending
    all_yogas.sort(key=lambda y: y.plausibility_score, reverse=True)
    
    pure_count = sum(1 for y in all_yogas if y.status == YogaStatus.PURE)
    stained_count = sum(1 for y in all_yogas if y.status == YogaStatus.STAINED)
    rescued_count = sum(1 for y in all_yogas if y.status == YogaStatus.RESCUED)
    broken_count = sum(1 for y in all_yogas if y.status == YogaStatus.BROKEN)
    
    categories = [
        YogaCategory.MAHAPURUSHA.value,
        YogaCategory.RAJA.value,
        YogaCategory.DHANA.value,
        YogaCategory.DARIDRYA.value,
        YogaCategory.LUNAR.value,
        YogaCategory.SOLAR.value,
        YogaCategory.PARIVARTANA.value,
        YogaCategory.VIPARITA.value,
        YogaCategory.KARTARI.value,
        YogaCategory.CHANDAL.value
    ]
    
    return {
        "total_count": len(all_yogas),
        "summary": {
            "pure": pure_count,
            "stained": stained_count,
            "rescued": rescued_count,
            "broken": broken_count
        },
        "yogas": [y.to_dict() for y in all_yogas],
        "categories": categories
    }
