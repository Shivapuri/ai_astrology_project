"""
Sign Attributes & Planetary Distribution Engine for Astra (Kala Integrated Approach)

Classifies planets and signs across classical Jyotish dimensions:
1. Core Triad of Sign Attributes:
   - Polarity & Gender (Active/Masculine/Odd vs Passive/Feminine/Even)
   - Quality & Mobility (Movable/Chara, Fixed/Sthira, Dual/Dvisvabhava)
   - Four Elements (Agni/Fire, Prithvi/Earth, Vayu/Air, Jala/Water)
2. Social Archetypes (Varnas) & Ayurvedic Humors (Doshas):
   - Kshatriya (Fire / Pitta), Shudra (Earth / Kapha), Vaishya (Air / Vata), Brahmin (Water / Kapha)
3. Rising Orientation (Udaya):
   - Shirshodaya (Head-rising), Prishtodaya (Back-rising), Ubhayodaya (Both-ways)
4. Kalapurusha Body Regions (Head-to-toe Anatomy):
   - 12 anatomical regions from Head (Aries) to Feet (Pisces)

Pure calculation functions returning primitive dicts/lists/ints.
No hardcoded values; dynamically derived from varga placement.
"""

# Ordered list of the 12 tropical zodiac signs
SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer",
    "Leo", "Virgo", "Libra", "Scorpio",
    "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

SIGN_NUMBERS = {s: i + 1 for i, s in enumerate(SIGNS)}

# 1. Elements (Tattvas)
ELEMENT_MAP = {
    "Aries": "Fire", "Leo": "Fire", "Sagittarius": "Fire",
    "Taurus": "Earth", "Virgo": "Earth", "Capricorn": "Earth",
    "Gemini": "Air", "Libra": "Air", "Aquarius": "Air",
    "Cancer": "Water", "Scorpio": "Water", "Pisces": "Water"
}

ELEMENT_ATTRIBUTES = {
    "Fire": {
        "sanskrit": "Agni",
        "varna": "Kshatriya",
        "varna_desc": "Leaders & Protectors (Law, courage, enterprise)",
        "dosha": "Pitta",
        "dosha_desc": "Metabolic fire, heat, vitality",
        "traits": "Assertive, courageous, aspirational, visionary",
        "color": "#c0392b"
    },
    "Earth": {
        "sanskrit": "Prithvi",
        "varna": "Shudra",
        "varna_desc": "Craftsmen & Builders (Service, manual craft, stability)",
        "dosha": "Kapha",
        "dosha_desc": "Physical structure, stability, endurance",
        "traits": "Practical, grounded, sensory, steady",
        "color": "#795548"
    },
    "Air": {
        "sanskrit": "Vayu",
        "varna": "Vaishya",
        "varna_desc": "Merchants & Communicators (Trade, intellect, commerce)",
        "dosha": "Vata",
        "dosha_desc": "Nervous energy, movement, mental speed",
        "traits": "Sociable, communicative, rational, mentally curious",
        "color": "#1976d2"
    },
    "Water": {
        "sanskrit": "Jala",
        "varna": "Brahmin",
        "varna_desc": "Scholars & Counselors (Teaching, wisdom, spirituality)",
        "dosha": "Kapha",
        "dosha_desc": "Fluids, lubrication, emotional receptivity",
        "traits": "Sensitive, instinctive, emotional, intuitive",
        "color": "#00897b"
    }
}

# 2. Quality & Mobility (Gunas / Charadi)
MOBILITY_MAP = {
    "Aries": "Movable", "Cancer": "Movable", "Libra": "Movable", "Capricorn": "Movable",
    "Taurus": "Fixed", "Leo": "Fixed", "Scorpio": "Fixed", "Aquarius": "Fixed",
    "Gemini": "Dual", "Virgo": "Dual", "Sagittarius": "Dual", "Pisces": "Dual"
}

MOBILITY_ATTRIBUTES = {
    "Movable": {
        "sanskrit": "Chara",
        "english": "Cardinal / Movable",
        "nature": "Outgoing, enterprising, initiatory, indicates sudden movement or change"
    },
    "Fixed": {
        "sanskrit": "Sthira",
        "english": "Fixed",
        "nature": "Steadfast, resistant to sudden change, preserving the status quo"
    },
    "Dual": {
        "sanskrit": "Dvisvabhava",
        "english": "Mutable / Dual",
        "nature": "Adaptable, flexible junction points between change and stability"
    }
}

# 3. Polarity & Gender
POLARITY_MAP = {
    "Aries": "Active", "Gemini": "Active", "Leo": "Active",
    "Libra": "Active", "Sagittarius": "Active", "Aquarius": "Active",
    "Taurus": "Passive", "Cancer": "Passive", "Virgo": "Passive",
    "Scorpio": "Passive", "Capricorn": "Passive", "Pisces": "Passive"
}

POLARITY_ATTRIBUTES = {
    "Active": {
        "sanskrit": "Odd / Masculine / Day",
        "nature": "Extroverted, expressive, direct; naturally supports Sun, Mars, Jupiter"
    },
    "Passive": {
        "sanskrit": "Even / Feminine / Night",
        "nature": "Introverted, reflective, receptive; naturally supports Moon, Venus"
    }
}

# 4. Rising Orientation (Udaya)
RISING_MAP = {
    "Gemini": "Shirshodaya", "Leo": "Shirshodaya", "Virgo": "Shirshodaya",
    "Libra": "Shirshodaya", "Scorpio": "Shirshodaya", "Aquarius": "Shirshodaya",
    "Aries": "Prishtodaya", "Taurus": "Prishtodaya", "Cancer": "Prishtodaya",
    "Sagittarius": "Prishtodaya", "Capricorn": "Prishtodaya",
    "Pisces": "Ubhayodaya"
}

RISING_ATTRIBUTES = {
    "Shirshodaya": {
        "sanskrit": "Head-rising",
        "nature": "Favorable; delivers fruits in the early stages of life or beginning of planetary cycles (Dashas)"
    },
    "Prishtodaya": {
        "sanskrit": "Back-rising",
        "nature": "Delivers fruits in the later stages of life or the end of planetary cycles (Dashas)"
    },
    "Ubhayodaya": {
        "sanskrit": "Both-ways rising",
        "nature": "Fruitful at all times throughout life"
    }
}

# 5. Kalapurusha Body Regions (Head-to-Toe Anatomy)
KALAPURUSHA_ANATOMY = [
    {
        "sign": "Aries",
        "number": 1,
        "region": "Head & Brain",
        "organs": "Head, brain, scalp, and eyes",
        "symbol": "♈\uFE0E"
    },
    {
        "sign": "Taurus",
        "number": 2,
        "region": "Face & Throat",
        "organs": "Face, neck, throat, larynx, and vocal cords",
        "symbol": "♉\uFE0E"
    },
    {
        "sign": "Gemini",
        "number": 3,
        "region": "Shoulders & Lungs",
        "organs": "Shoulders, arms, hands, and upper chest/lungs",
        "symbol": "♊\uFE0E"
    },
    {
        "sign": "Cancer",
        "number": 4,
        "region": "Chest & Stomach",
        "organs": "Chest, breasts, stomach, and ribs",
        "symbol": "♋\uFE0E"
    },
    {
        "sign": "Leo",
        "number": 5,
        "region": "Heart & Upper Back",
        "organs": "Heart, solar plexus, and upper back",
        "symbol": "♌\uFE0E"
    },
    {
        "sign": "Virgo",
        "number": 6,
        "region": "Navel & Digestive Tract",
        "organs": "Navel, small intestines, colon, and digestive tract",
        "symbol": "♍\uFE0E"
    },
    {
        "sign": "Libra",
        "number": 7,
        "region": "Lower Abdomen & Kidneys",
        "organs": "Lower abdomen, lumbar region, and kidneys",
        "symbol": "♎\uFE0E"
    },
    {
        "sign": "Scorpio",
        "number": 8,
        "region": "Pelvis & Reproductive",
        "organs": "Excretory and reproductive organs, pelvic base",
        "symbol": "♏\uFE0E"
    },
    {
        "sign": "Sagittarius",
        "number": 9,
        "region": "Hips & Thighs",
        "organs": "Hips, thighs, and arterial system",
        "symbol": "♐\uFE0E"
    },
    {
        "sign": "Capricorn",
        "number": 10,
        "region": "Knees & Joints",
        "organs": "Knees, kneecaps, and skeletal joints",
        "symbol": "♑\uFE0E"
    },
    {
        "sign": "Aquarius",
        "number": 11,
        "region": "Calves, Ankles & Skin",
        "organs": "Calves, shins, ankles, and skin",
        "symbol": "♒\uFE0E"
    },
    {
        "sign": "Pisces",
        "number": 12,
        "region": "Feet & Lymphatics",
        "organs": "Feet, toes, and the lymphatic fluid system",
        "symbol": "♓\uFE0E"
    }
]

# The standard 9 Jyotish Grahas
STANDARD_GRAHAS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]

# The 4x3 Matrix mapping: Row = Element (Fire, Earth, Air, Water), Col = Mobility (Movable, Fixed, Dual)
# Every sign is a unique combination of 1 Element and 1 Mobility!
MATRIX_4X3_LAYOUT = [
    {"element": "Fire", "signs": [("Aries", "Movable"), ("Leo", "Fixed"), ("Sagittarius", "Dual")]},
    {"element": "Earth", "signs": [("Capricorn", "Movable"), ("Taurus", "Fixed"), ("Virgo", "Dual")]},
    {"element": "Air", "signs": [("Libra", "Movable"), ("Aquarius", "Fixed"), ("Gemini", "Dual")]},
    {"element": "Water", "signs": [("Cancer", "Movable"), ("Scorpio", "Fixed"), ("Pisces", "Dual")]}
]


def calculate_sign_distributions(varga_data, count_lagna=False):
    """
    Calculates planetary distributions across all sign attributes for a given varga.
    
    Args:
        varga_data (dict): Varga dictionary containing 'lagna' and 'grahas'.
        count_lagna (bool): If True, Lagna is included in the total numerical counts (total 10).
                           If False, only the 9 standard grahas are counted, while Lagna
                           is tracked as a distinct marker/presence.
                           
    Returns:
        dict: Complete mathematical distribution breakdown across all dimensions.
    """
    grahas_data = varga_data.get("grahas", {})
    lagna_data = varga_data.get("lagna", {})
    lagna_sign = lagna_data.get("sign", "Aries")
    
    # Map planets by sign
    planets_by_sign = {s: [] for s in SIGNS}
    for p_name in STANDARD_GRAHAS:
        if p_name in grahas_data:
            s_name = grahas_data[p_name].get("sign")
            if s_name in planets_by_sign:
                planets_by_sign[s_name].append(p_name)
                
    # 1. 4x3 Matrix (Element x Mobility)
    matrix_rows = []
    for row_def in MATRIX_4X3_LAYOUT:
        elem = row_def["element"]
        elem_meta = ELEMENT_ATTRIBUTES[elem]
        row_cells = []
        row_grahas = []
        row_has_lagna = False
        
        for sign_name, mobility in row_def["signs"]:
            s_grahas = planets_by_sign.get(sign_name, [])
            has_l = (sign_name == lagna_sign)
            if has_l:
                row_has_lagna = True
            row_grahas.extend(s_grahas)
            
            count = len(s_grahas) + (1 if (has_l and count_lagna) else 0)
            row_cells.append({
                "sign": sign_name,
                "number": SIGN_NUMBERS[sign_name],
                "mobility": mobility,
                "grahas": s_grahas,
                "has_lagna": has_l,
                "count": count
            })
            
        row_count = len(row_grahas) + (1 if (row_has_lagna and count_lagna) else 0)
        matrix_rows.append({
            "element": elem,
            "sanskrit": elem_meta["sanskrit"],
            "varna": elem_meta["varna"],
            "dosha": elem_meta["dosha"],
            "color": elem_meta["color"],
            "cells": row_cells,
            "total_count": row_count,
            "all_grahas": row_grahas,
            "has_lagna": row_has_lagna
        })

    # 2. Element Totals
    element_totals = {}
    for elem, meta in ELEMENT_ATTRIBUTES.items():
        elem_signs = [s for s, e in ELEMENT_MAP.items() if e == elem]
        e_grahas = []
        has_l = False
        for s in elem_signs:
            e_grahas.extend(planets_by_sign[s])
            if s == lagna_sign:
                has_l = True
        count = len(e_grahas) + (1 if (has_l and count_lagna) else 0)
        element_totals[elem] = {
            "count": count,
            "grahas": e_grahas,
            "has_lagna": has_l,
            "sanskrit": meta["sanskrit"],
            "varna": meta["varna"],
            "varna_desc": meta["varna_desc"],
            "dosha": meta["dosha"],
            "dosha_desc": meta["dosha_desc"],
            "traits": meta["traits"],
            "signs": elem_signs,
            "color": meta["color"]
        }

    # 3. Mobility Totals
    mobility_totals = {}
    for mob, meta in MOBILITY_ATTRIBUTES.items():
        mob_signs = [s for s, m in MOBILITY_MAP.items() if m == mob]
        m_grahas = []
        has_l = False
        for s in mob_signs:
            m_grahas.extend(planets_by_sign[s])
            if s == lagna_sign:
                has_l = True
        count = len(m_grahas) + (1 if (has_l and count_lagna) else 0)
        mobility_totals[mob] = {
            "count": count,
            "grahas": m_grahas,
            "has_lagna": has_l,
            "sanskrit": meta["sanskrit"],
            "english": meta["english"],
            "nature": meta["nature"],
            "signs": mob_signs
        }

    # 4. Polarity Totals
    polarity_totals = {}
    for pol, meta in POLARITY_ATTRIBUTES.items():
        pol_signs = [s for s, p in POLARITY_MAP.items() if p == pol]
        p_grahas = []
        has_l = False
        for s in pol_signs:
            p_grahas.extend(planets_by_sign[s])
            if s == lagna_sign:
                has_l = True
        count = len(p_grahas) + (1 if (has_l and count_lagna) else 0)
        polarity_totals[pol] = {
            "count": count,
            "grahas": p_grahas,
            "has_lagna": has_l,
            "sanskrit": meta["sanskrit"],
            "nature": meta["nature"],
            "signs": pol_signs
        }

    # 5. Varna Totals
    varna_totals = {
        "Kshatriya": {
            "element": "Fire",
            "count": element_totals["Fire"]["count"],
            "grahas": element_totals["Fire"]["grahas"],
            "has_lagna": element_totals["Fire"]["has_lagna"],
            "desc": ELEMENT_ATTRIBUTES["Fire"]["varna_desc"]
        },
        "Shudra": {
            "element": "Earth",
            "count": element_totals["Earth"]["count"],
            "grahas": element_totals["Earth"]["grahas"],
            "has_lagna": element_totals["Earth"]["has_lagna"],
            "desc": ELEMENT_ATTRIBUTES["Earth"]["varna_desc"]
        },
        "Vaishya": {
            "element": "Air",
            "count": element_totals["Air"]["count"],
            "grahas": element_totals["Air"]["grahas"],
            "has_lagna": element_totals["Air"]["has_lagna"],
            "desc": ELEMENT_ATTRIBUTES["Air"]["varna_desc"]
        },
        "Brahmin": {
            "element": "Water",
            "count": element_totals["Water"]["count"],
            "grahas": element_totals["Water"]["grahas"],
            "has_lagna": element_totals["Water"]["has_lagna"],
            "desc": ELEMENT_ATTRIBUTES["Water"]["varna_desc"]
        }
    }

    # 6. Dosha Totals
    dosha_totals = {
        "Pitta": {
            "source": "Fire signs",
            "count": element_totals["Fire"]["count"],
            "grahas": element_totals["Fire"]["grahas"],
            "has_lagna": element_totals["Fire"]["has_lagna"],
            "desc": ELEMENT_ATTRIBUTES["Fire"]["dosha_desc"]
        },
        "Vata": {
            "source": "Air signs",
            "count": element_totals["Air"]["count"],
            "grahas": element_totals["Air"]["grahas"],
            "has_lagna": element_totals["Air"]["has_lagna"],
            "desc": ELEMENT_ATTRIBUTES["Air"]["dosha_desc"]
        },
        "Kapha": {
            "source": "Earth & Water signs",
            "count": element_totals["Earth"]["count"] + element_totals["Water"]["count"],
            "grahas": element_totals["Earth"]["grahas"] + element_totals["Water"]["grahas"],
            "has_lagna": element_totals["Earth"]["has_lagna"] or element_totals["Water"]["has_lagna"],
            "desc": "Physical mass, bodily fluids, lubrication, and endurance"
        }
    }

    # 7. Rising Orientation Totals
    rising_totals = {}
    for rise, meta in RISING_ATTRIBUTES.items():
        r_signs = [s for s, r in RISING_MAP.items() if r == rise]
        r_grahas = []
        has_l = False
        for s in r_signs:
            r_grahas.extend(planets_by_sign[s])
            if s == lagna_sign:
                has_l = True
        count = len(r_grahas) + (1 if (has_l and count_lagna) else 0)
        rising_totals[rise] = {
            "count": count,
            "grahas": r_grahas,
            "has_lagna": has_l,
            "sanskrit": meta["sanskrit"],
            "nature": meta["nature"],
            "signs": r_signs
        }

    # 8. Kalapurusha Anatomy List (Head to Feet)
    anatomy_list = []
    for item in KALAPURUSHA_ANATOMY:
        s_name = item["sign"]
        s_grahas = planets_by_sign.get(s_name, [])
        has_l = (s_name == lagna_sign)
        count = len(s_grahas) + (1 if (has_l and count_lagna) else 0)
        anatomy_list.append({
            "sign": s_name,
            "number": item["number"],
            "symbol": item["symbol"],
            "region": item["region"],
            "organs": item["organs"],
            "element": ELEMENT_MAP[s_name],
            "mobility": MOBILITY_MAP[s_name],
            "grahas": s_grahas,
            "has_lagna": has_l,
            "count": count
        })

    return {
        "lagna_sign": lagna_sign,
        "count_lagna": count_lagna,
        "total_counted": sum(e["count"] for e in element_totals.values()),
        "matrix_4x3": matrix_rows,
        "elements": element_totals,
        "mobility": mobility_totals,
        "polarity": polarity_totals,
        "varnas": varna_totals,
        "doshas": dosha_totals,
        "rising": rising_totals,
        "anatomy": anatomy_list
    }
