"""
nakshatra_metadata.py

Astronomical and Vedic metadata for all 27 Nakshatras (Lunar Mansions).
Includes:
- Presiding Vedic deities (Devatas) per Krishna Yajurveda (Taittiriya Brahmana / Samhita)
  and classical Parashari Jyotish (BPHS).
- Planetary rulers (Vimshottari Overlords).
- Classical natures (Mridu, Ugra, Tikshna, Chara, Sthira, Laghu, Mishra).
- Subconscious psychological drive and core motivation.
- Calculation system constants for dual-engine toggling:
  * ERNST_DHRUVA: Ernst Wilhelm's Dhruva Galactic Center Equatorial Right Ascension.
  * VIC_CHITRA: Vic DiCara's Tropical Rasis + Ecliptic Sidereal (Chitra / Lahiri) system.
"""

from typing import Dict, Any

NAKSHATRA_SYSTEM_DHRUVA = "ERNST_DHRUVA"
NAKSHATRA_SYSTEM_VIC = "VIC_CHITRA"

NAKSHATRA_METADATA: Dict[str, Dict[str, str]] = {
    "Ashwini": {
        "name": "Ashwini",
        "deity": "Ashwini Kumaras",
        "ruler": "Ketu",
        "nature": "Laghu / Light & Swift",
        "core_drive": "Swift healing, pioneering initiative, and vitality restoration."
    },
    "Bharani": {
        "name": "Bharani",
        "deity": "Yama",
        "ruler": "Venus",
        "nature": "Ugra / Fierce & Severe",
        "core_drive": "Bearing cosmic burdens, radical transformation, and enduring restraint."
    },
    "Krittika": {
        "name": "Krittika",
        "deity": "Agni",
        "ruler": "Sun",
        "nature": "Mishra / Mixed (Sharp & Soft)",
        "core_drive": "Purifying fire, cutting through illusions, and digestive power."
    },
    "Rohini": {
        "name": "Rohini",
        "deity": "Prajapati",
        "ruler": "Moon",
        "nature": "Sthira / Fixed & Enduring",
        "core_drive": "Fertile growth, sensory beauty, charm, and artistic creation."
    },
    "Mrigashira": {
        "name": "Mrigashira",
        "deity": "Soma",
        "ruler": "Mars",
        "nature": "Mridu / Soft & Gentle",
        "core_drive": "Restless searching, seeking spiritual nectar, and gentle curiosity."
    },
    "Ardra": {
        "name": "Ardra",
        "deity": "Rudra",
        "ruler": "Rahu",
        "nature": "Tikshna / Sharp & Dreadful",
        "core_drive": "Cathartic storms, emotional breakthrough, and overcoming suffering."
    },
    "Punarvasu": {
        "name": "Punarvasu",
        "deity": "Aditi",
        "ruler": "Jupiter",
        "nature": "Chara / Movable & Ephemeral",
        "core_drive": "Renewal of light, restorative sanctuary, and return of goodness."
    },
    "Pushya": {
        "name": "Pushya",
        "deity": "Brihaspati",
        "ruler": "Saturn",
        "nature": "Laghu / Light & Nurturing",
        "core_drive": "Spiritual nourishment, wisdom cultivation, and ethical protection."
    },
    "Ashlesha": {
        "name": "Ashlesha",
        "deity": "Sarpas",
        "ruler": "Mercury",
        "nature": "Tikshna / Sharp & Dreadful",
        "core_drive": "Kundalini awakening, intuitive perception, and psychological defense."
    },
    "Magha": {
        "name": "Magha",
        "deity": "Pitris",
        "ruler": "Ketu",
        "nature": "Ugra / Fierce & Severe",
        "core_drive": "Ancestral honor, regal authority, tradition, and lineage pride."
    },
    "Purva Phalguni": {
        "name": "Purva Phalguni",
        "deity": "Bhaga",
        "ruler": "Venus",
        "nature": "Ugra / Fierce & Severe",
        "core_drive": "Creative recreation, marital affection, passion, and gracious living."
    },
    "Uttara Phalguni": {
        "name": "Uttara Phalguni",
        "deity": "Aryaman",
        "ruler": "Sun",
        "nature": "Sthira / Fixed & Enduring",
        "core_drive": "Noble contracts, benevolent leadership, and lasting social alliances."
    },
    "Hasta": {
        "name": "Hasta",
        "deity": "Savitar",
        "ruler": "Moon",
        "nature": "Laghu / Light & Swift",
        "core_drive": "Dexterous craftsmanship, skillful hands, healing, and manifest detail."
    },
    "Chitra": {
        "name": "Chitra",
        "deity": "Tvashtar",
        "ruler": "Mars",
        "nature": "Mridu / Soft",
        "core_drive": "Intellectual design and craftsmanship."
    },
    "Swati": {
        "name": "Swati",
        "deity": "Vayu",
        "ruler": "Rahu",
        "nature": "Chara / Movable & Ephemeral",
        "core_drive": "Independent movement, flexible diplomacy, and freedom of expression."
    },
    "Vishakha": {
        "name": "Vishakha",
        "deity": "Indragni",
        "ruler": "Jupiter",
        "nature": "Mishra / Mixed (Sharp & Soft)",
        "core_drive": "Single-pointed ambition, focused triumph, and overcoming hurdles."
    },
    "Anuradha": {
        "name": "Anuradha",
        "deity": "Mitra",
        "ruler": "Saturn",
        "nature": "Mridu / Soft & Tender",
        "core_drive": "Devotional allegiance, harmonious fellowship, and organizational loyalty."
    },
    "Jyeshtha": {
        "name": "Jyeshtha",
        "deity": "Indra",
        "ruler": "Mercury",
        "nature": "Tikshna / Sharp & Dreadful",
        "core_drive": "Elder guardianship, protective sovereignty, and safeguarding status."
    },
    "Mula": {
        "name": "Mula",
        "deity": "Nirriti",
        "ruler": "Ketu",
        "nature": "Tikshna / Sharp & Dreadful",
        "core_drive": "Root investigation, shattering superficiality, and transformative truth."
    },
    "Purva Ashadha": {
        "name": "Purva Ashadha",
        "deity": "Apas",
        "ruler": "Venus",
        "nature": "Ugra / Fierce & Severe",
        "core_drive": "Invincible confidence, purifying renewal, and unyielding conviction."
    },
    "Uttara Ashadha": {
        "name": "Uttara Ashadha",
        "deity": "Vishvedevas",
        "ruler": "Sun",
        "nature": "Sthira / Fixed & Enduring",
        "core_drive": "Universal integrity, permanent achievement, and righteous victory."
    },
    "Shravana": {
        "name": "Shravana",
        "deity": "Vishnu",
        "ruler": "Moon",
        "nature": "Chara / Movable & Ephemeral",
        "core_drive": "Attentive listening, oral tradition transmission, and preservation of order."
    },
    "Dhanishtha": {
        "name": "Dhanishtha",
        "deity": "Vasus",
        "ruler": "Mars",
        "nature": "Chara / Movable & Ephemeral",
        "core_drive": "Rhythmic harmony, material abundance, fame, and orchestral coordination."
    },
    "Shatabhisha": {
        "name": "Shatabhisha",
        "deity": "Varuna",
        "ruler": "Rahu",
        "nature": "Chara / Movable & Ephemeral",
        "core_drive": "Secret healing, 100 remedies, veiled contemplation, and cosmic laws."
    },
    "Purva Bhadrapada": {
        "name": "Purva Bhadrapada",
        "deity": "Aja Ekapada",
        "ruler": "Jupiter",
        "nature": "Ugra / Fierce & Severe",
        "core_drive": "Ascetic tapas, intense purification, and spiritual zeal."
    },
    "Uttara Bhadrapada": {
        "name": "Uttara Bhadrapada",
        "deity": "Ahirbudhnya",
        "ruler": "Saturn",
        "nature": "Sthira / Fixed & Enduring",
        "core_drive": "Deep ocean stability, serene wisdom, and grounded contemplation."
    },
    "Revati": {
        "name": "Revati",
        "deity": "Pushan",
        "ruler": "Mercury",
        "nature": "Mridu / Soft & Gentle",
        "core_drive": "Gentle nourishment, safe guidance of journeys, and spiritual release."
    }
}


def get_nakshatra_metadata(nak_name: str) -> Dict[str, str]:
    """
    Retrieves full metadata for a given Nakshatra by name.
    Falls back gracefully if an un-canonical or formatted string is provided.
    """
    clean_name = nak_name.strip()
    if clean_name in NAKSHATRA_METADATA:
        return NAKSHATRA_METADATA[clean_name]
    
    # Attempt case-insensitive or partial match
    c_lower = clean_name.lower()
    for key, data in NAKSHATRA_METADATA.items():
        if key.lower() == c_lower or key.lower() in c_lower or c_lower in key.lower():
            return data
            
    return {
        "name": clean_name,
        "deity": "Universal Divine",
        "ruler": "Ketu",
        "nature": "Sadharana / General",
        "core_drive": "Subconscious motivation and cosmic trajectory."
    }
