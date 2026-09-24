"""
Astra Nakshatra Lore & Classification Interface
Loads the comprehensive 27-Nakshatra database and provides normalized lookups
for classical groups, devatas, symbols, and psychological profiles.
"""

import os
import json
from typing import Dict, Any, Optional

try:
    from jyotish.nakshatras.nakshatra_data import NAKSHATRA_DATABASE
except ImportError:
    _CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    _DB_PATH = os.path.join(_CURRENT_DIR, "nakshatra_database.json")
    with open(_DB_PATH, "r", encoding="utf-8") as f:
        NAKSHATRA_DATABASE: Dict[str, Dict[str, Any]] = json.load(f)

# Normalized alias map for robust lookup
_ALIAS_MAP: Dict[str, str] = {}
for canonical_key, data in NAKSHATRA_DATABASE.items():
    _ALIAS_MAP[canonical_key.lower()] = canonical_key
    for alias in data.get("aliases", []):
        _ALIAS_MAP[alias.lower()] = canonical_key

NAKSHATRA_GROUP_METADATA: Dict[str, Dict[str, str]] = {
    "Tikshna": {
        "sanskrit": "Tīkṣṇa / Dāruṇa",
        "label": "Bitter, Sharp & Dreadful",
        "nature": "Cathartic disruption, penetrating strategy, relentless truth-seeking",
        "color": "#991b1b",
        "bg": "#fef2f2"
    },
    "Ugra": {
        "sanskrit": "Ugra / Krūra",
        "label": "Fierce, Severe & Strong",
        "nature": "Formidable ambition, boundary defense, rigorous discipline",
        "color": "#c2410c",
        "bg": "#fff7ed"
    },
    "Dhruva": {
        "sanskrit": "Dhruva / Sthira",
        "label": "Fixed, Permanent & Enduring",
        "nature": "Lasting foundations, institutional legacy, patient stability",
        "color": "#15803d",
        "bg": "#f0fdf4"
    },
    "Mridu": {
        "sanskrit": "Mṛdu",
        "label": "Soft, Mild & Tender",
        "nature": "Aesthetic refinement, cooperative harmony, deep empathy",
        "color": "#0d9488",
        "bg": "#f0fdfa"
    },
    "Laghu": {
        "sanskrit": "Kṣipra / Laghu",
        "label": "Light, Swift & Quick",
        "nature": "Agility, rapid healing, technical dexterity, effortless realization",
        "color": "#2563eb",
        "bg": "#eff6ff"
    },
    "Chara": {
        "sanskrit": "Cara / Cala",
        "label": "Movable, Dynamic & Mobile",
        "nature": "Locomotion, rhythm, trade, independent individuation",
        "color": "#7c3aed",
        "bg": "#f5f3ff"
    },
    "Mishra": {
        "sanskrit": "Miśra / Sādhāraṇa",
        "label": "Mixed (Sharp & Soft)",
        "nature": "Universal catalysis, one-pointed focus coupled with devotion",
        "color": "#b45309",
        "bg": "#fffbeb"
    }
}

ALL_NAKSHATRA_GROUPS = list(NAKSHATRA_GROUP_METADATA.keys())


def normalize_nakshatra_name(name: str) -> str:
    """Normalizes any nakshatra string (case-insensitive, trims spaces)."""
    if not name:
        return "Ashwini"
    clean = name.strip().lower()
    return _ALIAS_MAP.get(clean, name.strip())


def get_nakshatra_lore(name: str) -> Dict[str, Any]:
    """
    Returns the complete psychological and astrological dossier for a Nakshatra.
    Falls back gracefully if an unknown name is provided.
    """
    norm = normalize_nakshatra_name(name)
    if norm in NAKSHATRA_DATABASE:
        return NAKSHATRA_DATABASE[norm]
    
    # Generic fallback
    return {
        "name": name,
        "aliases": [name],
        "group": "Mishra",
        "group_description": "General Asterism",
        "astronomical_star": "Vedic Constellation",
        "zodiacal_span": "--",
        "presiding_deity": "Universal Cosmic Intelligence",
        "symbol_etymology": "Asterism",
        "varahamihira_moon": "Endowed with vitality and purpose.",
        "core_psychology": "Expresses distinctive celestial nature and life momentum.",
        "real_world_manifestations": "Diverse creative, executive, and intellectual pursuits."
    }


def get_nakshatra_group(name: str) -> str:
    """Returns the group category (Tikshna, Ugra, Dhruva, Mridu, Laghu, Chara, Mishra)."""
    lore = get_nakshatra_lore(name)
    return lore.get("group", "Mishra")
