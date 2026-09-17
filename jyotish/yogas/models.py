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
        d = asdict(self)
        d["category"] = self.category.value
        d["status"] = self.status.value
        d["breakers"] = [b.to_dict() for b in self.breakers]
        return d
