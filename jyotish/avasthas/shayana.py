"""
Shayanadi Avasthas (The 12 Activity States & Sub-States)
========================================================
This module calculates the Shayanadi Avastha (Activity State) and Cheshtadi Sub-State
for a given planet according to Brihat Parashara Hora Shastra (Chapter 45, Verses 30-38)
and the exact methodology of Ernst Wilhelm's Kala software.

Mathematical Formula:
----------------------
1. Main Avastha Formula:
   Product = Planet Nakshatra Number * Planet Serial Number * Nakshatra Pada
   Raw Sum = Product + Lagna Sign Number + Moon Nakshatra Number + Ishta Ghati
   Avastha Index = (Raw Sum % 12)
   If Avastha Index == 0: Avastha Index = 12

   - Planet Serial Number: Sun=1, Moon=2, Mars=3, Mercury=4, Jupiter=5, Venus=6, Saturn=7, Rahu=8, Ketu=9
   - Amsa Factor: Ernst Wilhelm strictly uses the Nakshatra Pada (1, 2, 3, or 4).
   - Lagna Sign Number: 1 to 12 (Aries=1, Taurus=2, ..., Pisces=12).
   - Moon Nakshatra Number: 1 to 27 (Ashwini=1, ..., Revati=27).
   - Ishta Ghati: Elapsed ghatis (24-minute periods) from sunrise to birth time (math.ceil(elapsed_min / 24.0)).

2. Cheshtadi Sub-State Formula:
   Sub-Sum 1 = ((Avastha Index ^ 2) + Name Sound Value) % 12
   Sub-Sum 2 = Sub-Sum 1 + Planet Kshepaka
   Sub-State Remainder = Sub-Sum 2 % 3

   - Name Sound Value (Varnamashka): 1 to 5 based on Sanskrit phonetic akshara / English first letter sound.
   - Planet Kshepaka (Additive Constant): Sun=5, Moon=2, Mars=2, Mercury=3, Jupiter=5, Venus=3, Saturn=3, Rahu=4, Ketu=4.
   - Sub-State Remainder:
     * 1 -> Drishti (Apparent / Visible) - Medium effect (50% strength)
     * 2 -> Cheshta (Active / Moving) - Great / Full effect (100% strength)
     * 0 -> Vicheshta (Motionless / Inactive) - Minimal effect (10% strength)
"""

import math
from typing import Optional, Dict, Any

# The 12 Shayanadi Activity States (1 to 12)
SHAYANADI_STATES: Dict[int, Dict[str, str]] = {
    1: {
        "sanskrit": "Shayana",
        "name": "Shayana (Lying Down)",
        "meaning": "Resting, inactive, lack of initiative and follow-through."
    },
    2: {
        "sanskrit": "Upaveshana",
        "name": "Upaveshana (Sitting)",
        "meaning": "Sitting, waiting, receptive state."
    },
    3: {
        "sanskrit": "Netrapani",
        "name": "Netrapani (Hand on Eye)",
        "meaning": "Eyes and hands engaged, cautious, observing or distressed."
    },
    4: {
        "sanskrit": "Prakashana",
        "name": "Prakashana (Illuminating)",
        "meaning": "Shining, radiant, expressing virtues and knowledge."
    },
    5: {
        "sanskrit": "Gamana",
        "name": "Gamana (Departing)",
        "meaning": "Departing, moving away, traveling, wanderlust."
    },
    6: {
        "sanskrit": "Agamana",
        "name": "Agamana (Arriving)",
        "meaning": "Arriving, coming back, returning home with gains."
    },
    7: {
        "sanskrit": "Sabhavasati",
        "name": "Sabhavasati (In Assembly)",
        "meaning": "Being in a council, holding court, administrative excellence."
    },
    8: {
        "sanskrit": "Agama",
        "name": "Agama (Acquiring)",
        "meaning": "Acquisition, reapproaching, gathering resources and knowledge."
    },
    9: {
        "sanskrit": "Bhojana",
        "name": "Bhojana (Eating)",
        "meaning": "Feasting, consuming, enjoying physical nourishment or sensuality."
    },
    10: {
        "sanskrit": "Nrityalipsa",
        "name": "Nrityalipsa (Longing to Dance)",
        "meaning": "Longing to dance, artistic enthusiasm, expressive performance."
    },
    11: {
        "sanskrit": "Kautuka",
        "name": "Kautuka (Eagerness)",
        "meaning": "Eager, joyful, curious, engaged in recreational play."
    },
    12: {
        "sanskrit": "Nidra",
        "name": "Nidra (Slumber)",
        "meaning": "Deep sleep, slumber, dormant power or sluggishness."
    }
}

# Planet Serial Numbers (1 to 9)
PLANET_SERIAL_NUMBERS: Dict[str, int] = {
    "Sun": 1,
    "Moon": 2,
    "Mars": 3,
    "Mercury": 4,
    "Jupiter": 5,
    "Venus": 6,
    "Saturn": 7,
    "Rahu": 8,
    "Ketu": 9
}

# Planet Kshepakas (Additive Constants for Cheshtadi Sub-State)
PLANET_KSHEPAKAS: Dict[str, int] = {
    "Sun": 5,
    "Moon": 2,
    "Mars": 2,
    "Mercury": 3,
    "Jupiter": 5,
    "Venus": 3,
    "Saturn": 3,
    "Rahu": 4,
    "Ketu": 4
}

# Cheshtadi Sub-States
CHESHTADI_SUB_STATES: Dict[int, Dict[str, Any]] = {
    1: {
        "sub_state": "Drishti",
        "label": "Drishti (Apparent / Medium)",
        "strength": "Medium",
        "multiplier": 0.50,
        "description": "Apparent and visible; moderate manifestation of the avastha."
    },
    2: {
        "sub_state": "Cheshta",
        "label": "Cheshta (Active / Strong)",
        "strength": "Great",
        "multiplier": 1.00,
        "description": "Active and moving; powerful and complete manifestation of the avastha."
    },
    0: {
        "sub_state": "Vicheshta",
        "label": "Vicheshta (Motionless / Inactive)",
        "strength": "Minimal",
        "multiplier": 0.10,
        "description": "Motionless and inactive; very slight or dormant manifestation of the avastha."
    }
}


def get_varnamashka_value(name: str) -> int:
    """
    Computes the Varnamashka (name sound / initial letter sound value 1-5)
    according to Sanskrit phonetic classes and Ernst Wilhelm's transliteration mapping.
    
    Args:
        name (str): The native's personal first name.
        
    Returns:
        int: Value between 1 and 5.
    """
    if not name:
        return 1
        
    clean_name = str(name).strip().upper() if name else ""
    if not clean_name:
        return 1
        
    # Digraphs / Trigraphs
    DIGRAPHS = {
        "CHH": 2, "CH": 1, "KH": 2, "TH": 2, "PH": 2,
        "GH": 4, "JH": 4, "DH": 4, "BH": 4, "SH": 1,
        "NG": 5, "NY": 5, "AA": 1, "EE": 2, "OO": 3,
        "AI": 4, "AU": 5, "AE": 4
    }
    
    # Single letters
    SINGLE_LETTERS = {
        "A": 1, "B": 3, "C": 1, "D": 3, "E": 4, "F": 2,
        "G": 3, "H": 4, "I": 2, "J": 3, "K": 1, "L": 3,
        "M": 5, "N": 5, "O": 5, "P": 1, "Q": 1, "R": 2,
        "S": 3, "T": 1, "U": 3, "V": 4, "W": 4, "X": 1,
        "Y": 1, "Z": 3
    }
    
    for prefix_len in (3, 2):
        if len(clean_name) >= prefix_len:
            prefix = clean_name[:prefix_len]
            if prefix in DIGRAPHS:
                return DIGRAPHS[prefix]
                
    first_char = clean_name[0]
    return SINGLE_LETTERS.get(first_char, 1)


def get_shayanadi_avastha(
    planet_name: str,
    planet_nakshatra_num: int,
    planet_pada: int,
    lagna_sign_num: int,
    moon_nakshatra_num: int,
    ishta_ghati: int,
    native_name: str = "",
    name_sound_value: Optional[int] = None
) -> Dict[str, Any]:
    """
    Calculates the Shayanadi Avastha (Activity State) and Cheshtadi Sub-State for a planet.

    Args:
        planet_name (str): Name of the planet (e.g. 'Sun', 'Moon', ..., 'Ketu').
        planet_nakshatra_num (int): Nakshatra serial number of the planet (1 to 27).
        planet_pada (int): Nakshatra Pada of the planet (1, 2, 3, or 4).
        lagna_sign_num (int): Sign number of the Lagna (1 for Aries to 12 for Pisces).
        moon_nakshatra_num (int): Nakshatra serial number of the Moon / Janma Nakshatra (1 to 27).
        ishta_ghati (int): Elapsed Ghatis from sunrise to birth (1 to 60).
        native_name (str, optional): First name of the native for Varnamashka derivation.
        name_sound_value (int, optional): Explicit Varnamashka value (1 to 5). If None, derived from native_name.

    Returns:
        Dict[str, Any]: Dictionary containing the avastha state, meaning, sub-state, and calculation breakdown.
    """
    # 1. Planet Serial Number
    planet_serial = PLANET_SERIAL_NUMBERS.get(planet_name, 1)
    
    # 2. Main Formula: (Planet Nakshatra * Planet Serial * Pada) + Lagna Sign + Moon Nakshatra + Ishta Ghati
    pada_factor = max(1, min(4, int(planet_pada)))
    product = planet_nakshatra_num * planet_serial * pada_factor
    raw_sum = product + lagna_sign_num + moon_nakshatra_num + max(1, int(ishta_ghati))
    
    avastha_idx = raw_sum % 12
    if avastha_idx == 0:
        avastha_idx = 12
        
    state_info = SHAYANADI_STATES.get(avastha_idx, SHAYANADI_STATES[1])
    
    # 3. Cheshtadi Sub-State
    if name_sound_value is None:
        sound_val = get_varnamashka_value(native_name)
    else:
        sound_val = max(1, min(5, int(name_sound_value)))
        
    squared_avastha = avastha_idx ** 2
    sub_sum_1 = (squared_avastha + sound_val) % 12
    kshepaka = PLANET_KSHEPAKAS.get(planet_name, 3)
    sub_sum_2 = sub_sum_1 + kshepaka
    sub_rem = sub_sum_2 % 3
    
    sub_state_info = CHESHTADI_SUB_STATES.get(sub_rem, CHESHTADI_SUB_STATES[0])
    
    return {
        "avastha_number": avastha_idx,
        "state": state_info["name"],
        "sanskrit": state_info["sanskrit"],
        "meaning": state_info["meaning"],
        "sub_state": sub_state_info["label"],
        "sub_state_type": sub_state_info["sub_state"],
        "sub_state_strength": sub_state_info["strength"],
        "sub_state_multiplier": sub_state_info["multiplier"],
        "sub_state_description": sub_state_info["description"],
        "calculation_breakdown": {
            "planet_nakshatra_num": planet_nakshatra_num,
            "planet_serial_num": planet_serial,
            "pada": pada_factor,
            "product": product,
            "lagna_sign_num": lagna_sign_num,
            "moon_nakshatra_num": moon_nakshatra_num,
            "ishta_ghati": ishta_ghati,
            "raw_sum": raw_sum,
            "remainder_12": avastha_idx,
            "name_sound_value": sound_val,
            "squared_avastha": squared_avastha,
            "sub_sum_mod12": sub_sum_1,
            "kshepaka": kshepaka,
            "sub_total_mod3": sub_rem
        }
    }


# Alias for convenience
get_varnamashka = get_varnamashka_value

