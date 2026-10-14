"""
jyotish/yogas/models.py
Data models and enumerations for Classical Yoga Detection and Yoga Breaker analysis.
"""

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import List, Dict, Any, Optional

class YogaCategory(str, Enum):
    MAHAPURUSHA = "Pancha Mahapurusha"
    RAJA = "Raja Yoga"
    DHANA = "Dhana (Wealth)"
    DARIDRYA = "Daridrya (Poverty)"
    LUNAR = "Chandra (Lunar)"
    SOLAR = "Ravi (Solar)"
    PARIVARTANA = "Parivartana (Exchange)"
    VIPARITA = "Viparita Raja (Reversal)"
    KARTARI = "Kartari (Hemming)"
    CHANDAL = "Chāṇḍāla & Doṣa (Afflictions)"
    CONTEXTUAL = "Contextual & Macro Yogas"
    CHARACTER = "Character & Growth"
    DISPOSITOR_ROOT = "Dispositor Root Yogas"
    DEITY = "Deity (Trimūrti & Tridevī)"
    BHAVA = "12 Bhava Yogas"
    POWER = "Chapter 7 Power Yogas"
    NEECHABHANGA = "Nīcabhaṅga (Debility Cancellation)"

class YogaStatus(str, Enum):
    PURE = "Pure & Eminent"
    STAINED = "Stained / Challenged"
    RESCUED = "Rescued (Neecha Bhanga / Reversal)"
    BROKEN = "Broken (Yoga Bhanga)"

@dataclass
class YogaBreakerDetail:
    factor: str             # e.g. "11th Lord Intrusion", "Combustion", "Debilitated Dispositor"
    culprit_planet: str     # Planet responsible, or "House" / "System"
    description: str        # Plain-English intuitive explanation
    penalty: float          # Subtracted percentage (e.g. 40.0)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class YogaInstance:
    id: str                         # Machine ID, e.g. "ruchaka_mars"
    name: str                       # Display name, e.g. "Ruchaka Yoga"
    category: YogaCategory          # Broad category
    status: YogaStatus              # Pure, Stained, Rescued, Broken
    plausibility_score: float       # 0.0 to 100.0%
    participating_planets: List[str]# Grahas involved
    participating_houses: List[int] # Bhavas involved (1-12)
    scripture_ref: str              # e.g. "BPHS 75.1-4, Phaladeepika 6.1"
    archetype: str                  # Intuitive 1-2 sentence core meaning
    manifestation_effects: List[str]# Key psychological and worldly outcomes
    positive_factors: List[str]     # Supportive features (dignity, Kendra, benefic aspects)
    breakers: List[YogaBreakerDetail] = field(default_factory=list) # Disruptive factors

    def to_dict(self) -> Dict[str, Any]:
        serialized_breakers = []
        for b in (self.breakers or []):
            if b is None:
                continue
            if hasattr(b, "to_dict") and callable(b.to_dict):
                serialized_breakers.append(b.to_dict())
            elif isinstance(b, dict):
                serialized_breakers.append(dict(b))

        return {
            "id": self.id,
            "name": self.name,
            "category": self.category.value if isinstance(self.category, Enum) else str(self.category or ""),
            "status": self.status.value if isinstance(self.status, Enum) else str(self.status or ""),
            "plausibility_score": max(0.0, min(100.0, float(self.plausibility_score or 0.0))),
            "participating_planets": list(self.participating_planets or []),
            "participating_houses": list(self.participating_houses or []),
            "scripture_ref": self.scripture_ref or "",
            "archetype": self.archetype or "",
            "manifestation_effects": list(self.manifestation_effects or []),
            "positive_factors": list(self.positive_factors or []),
            "breakers": serialized_breakers,
        }
