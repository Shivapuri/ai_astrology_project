"""
Precision Ashtakavarga Engine for Astra (Ernst Wilhelm's Kala Methodology).

Calculates:
1. Bhinnashtakavarga (BAV) for all 7 planets (Surya to Shani) and Lagna across 12 signs.
2. Prastarashtakavarga: 8-fold contributor grid for each planet.
3. Sarvashtakavarga (SAV): Total benefic points (337 points).
4. Trikona Shodhana: Reduction across mutual trines (Fire, Earth, Air, Water).
5. Ekadhipatya Shodhana: Reduction across dual-owned signs (BPHS Chapter 68).
6. Shodhya Pindas: Rasi Pinda, Graha Pinda, and Yoga Pinda (BPHS Chapter 69).
"""

from typing import Dict, List, Tuple, Set, Any

ZODIAC_SIGNS = [
    'Aries', 'Taurus', 'Gemini', 'Cancer',
    'Leo', 'Virgo', 'Libra', 'Scorpio',
    'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
]

SIGN_TO_INDEX = {name: idx for idx, name in enumerate(ZODIAC_SIGNS)}

# Authenticated Parashari Ashtakavarga tables adhering to Ernst Wilhelm's Kala configuration
# Note critical Parashara vs Varahamihira distinctions:
# - Moon from Jupiter: 2nd house is benefic (not 12th)
# - Venus from Mars: 4th house is benefic (not 5th)
BENEFIC_HOUSES: Dict[str, Dict[str, List[int]]] = {
    'Sun': {
        'Sun': [1, 2, 4, 7, 8, 9, 10, 11],
        'Moon': [3, 6, 10, 11],
        'Mars': [1, 2, 4, 7, 8, 9, 10, 11],
        'Mercury': [3, 5, 6, 9, 10, 11, 12],
        'Jupiter': [5, 6, 9, 11],
        'Venus': [6, 7, 12],
        'Saturn': [1, 2, 4, 7, 8, 9, 10, 11],
        'Lagna': [3, 4, 6, 10, 11, 12]
    },
    'Moon': {
        'Sun': [3, 6, 7, 8, 10, 11],
        'Moon': [1, 3, 6, 7, 10, 11],
        'Mars': [2, 3, 5, 6, 9, 10, 11],
        'Mercury': [1, 3, 4, 5, 7, 8, 10, 11],
        'Jupiter': [1, 2, 4, 7, 8, 10, 11],
        'Venus': [3, 4, 5, 7, 9, 10, 11],
        'Saturn': [3, 5, 6, 11],
        'Lagna': [3, 6, 10, 11]
    },
    'Mars': {
        'Sun': [3, 5, 6, 10, 11],
        'Moon': [3, 6, 11],
        'Mars': [1, 2, 4, 7, 8, 10, 11],
        'Mercury': [3, 5, 6, 11],
        'Jupiter': [6, 10, 11, 12],
        'Venus': [6, 8, 11, 12],
        'Saturn': [1, 4, 7, 8, 9, 10, 11],
        'Lagna': [1, 3, 6, 10, 11]
    },
    'Mercury': {
        'Sun': [5, 6, 9, 11, 12],
        'Moon': [2, 4, 6, 8, 10, 11],
        'Mars': [1, 2, 4, 7, 8, 9, 10, 11],
        'Mercury': [1, 3, 5, 6, 9, 10, 11, 12],
        'Jupiter': [6, 8, 11, 12],
        'Venus': [1, 2, 3, 4, 5, 8, 9, 11],
        'Saturn': [1, 2, 4, 7, 8, 9, 10, 11],
        'Lagna': [1, 2, 4, 6, 8, 10, 11]
    },
    'Jupiter': {
        'Sun': [1, 2, 3, 4, 7, 8, 9, 10, 11],
        'Moon': [2, 5, 7, 9, 11],
        'Mars': [1, 2, 4, 7, 8, 10, 11],
        'Mercury': [1, 2, 4, 5, 6, 9, 10, 11],
        'Jupiter': [1, 2, 3, 4, 7, 8, 10, 11],
        'Venus': [2, 5, 6, 9, 10, 11],
        'Saturn': [3, 5, 6, 12],
        'Lagna': [1, 2, 4, 5, 6, 7, 9, 10, 11]
    },
    'Venus': {
        'Sun': [8, 11, 12],
        'Moon': [1, 2, 3, 4, 5, 8, 9, 11, 12],
        'Mars': [3, 4, 6, 9, 11, 12],
        'Mercury': [3, 5, 6, 9, 11],
        'Jupiter': [5, 8, 9, 10, 11],
        'Venus': [1, 2, 3, 4, 5, 8, 9, 10, 11],
        'Saturn': [3, 4, 5, 8, 9, 10, 11],
        'Lagna': [1, 2, 3, 4, 5, 8, 9, 11]
    },
    'Saturn': {
        'Sun': [1, 2, 4, 7, 8, 10, 11],
        'Moon': [3, 6, 11],
        'Mars': [3, 5, 6, 10, 11, 12],
        'Mercury': [6, 8, 9, 10, 11, 12],
        'Jupiter': [5, 6, 11, 12],
        'Venus': [6, 11, 12],
        'Saturn': [3, 5, 6, 11],
        'Lagna': [1, 3, 4, 6, 10, 11]
    },
    'Lagna': {
        'Sun': [3, 4, 6, 10, 11, 12],
        'Moon': [3, 6, 10, 11, 12],
        'Mars': [1, 3, 6, 10, 11],
        'Mercury': [1, 2, 4, 6, 8, 10, 11],
        'Jupiter': [1, 2, 4, 5, 6, 7, 9, 10, 11],
        'Venus': [1, 2, 3, 4, 5, 8, 9],
        'Saturn': [1, 3, 4, 6, 10, 11],
        'Lagna': [3, 6, 10, 11]
    }
}

# The order of the 8 contributors as displayed in classical tables
CONTRIBUTORS = ['Saturn', 'Jupiter', 'Mars', 'Sun', 'Venus', 'Mercury', 'Moon', 'Lagna']

# Mutual elemental trines (Fire, Earth, Air, Water)
TRINAL_GROUPS = [
    [0, 4, 8],   # Aries, Leo, Sagittarius (Fire)
    [1, 5, 9],   # Taurus, Virgo, Capricorn (Earth)
    [2, 6, 10],  # Gemini, Libra, Aquarius (Air)
    [3, 7, 11],  # Cancer, Scorpio, Pisces (Water)
]

# Dual-ownership sign pairs (Mars, Venus, Mercury, Jupiter, Saturn)
# Note: Cancer (Moon) and Leo (Sun) are exempt from Ekadhipatya Shodhana
DUAL_RULED_PAIRS = [
    (0, 7),   # Mars: Aries, Scorpio
    (1, 6),   # Venus: Taurus, Libra
    (2, 5),   # Mercury: Gemini, Virgo
    (8, 11),  # Jupiter: Sagittarius, Pisces
    (9, 10),  # Saturn: Capricorn, Aquarius
]

# BPHS Multipliers for Shodhya Pinda (Chapter 69)
RASI_MULTIPLIERS = [7, 10, 8, 4, 10, 6, 7, 8, 9, 5, 11, 12]
GRAHA_MULTIPLIERS = {
    'Sun': 5, 'Moon': 5, 'Mars': 8, 'Mercury': 5,
    'Jupiter': 10, 'Venus': 7, 'Saturn': 5
}


def calculate_bav(entity: str, natal_sign_indices: Dict[str, int]) -> List[int]:
    """
    Calculates the Bhinnashtakavarga (BAV) 12-sign bindu list for an entity (planet or Lagna).
    """
    bindus = [0] * 12
    if entity not in BENEFIC_HOUSES:
        return bindus

    entity_table = BENEFIC_HOUSES[entity]
    for contributor, houses in entity_table.items():
        if contributor in natal_sign_indices:
            c_sign = natal_sign_indices[contributor]
            for h in houses:
                target_sign = (c_sign + h - 1) % 12
                bindus[target_sign] += 1

    return bindus


def calculate_prastara(entity: str, natal_sign_indices: Dict[str, int]) -> Dict[str, List[int]]:
    """
    Calculates the Prastarashtakavarga contributor matrix (8 rows x 12 signs).
    """
    grid = {}
    entity_table = BENEFIC_HOUSES.get(entity, {})
    for contributor in CONTRIBUTORS:
        row = [0] * 12
        if contributor in entity_table and contributor in natal_sign_indices:
            c_sign = natal_sign_indices[contributor]
            for h in entity_table[contributor]:
                target_sign = (c_sign + h - 1) % 12
                row[target_sign] = 1
        grid[contributor] = row
    return grid


def trikona_shodhana(bav_values: List[int]) -> List[int]:
    """
    Applies Trikona Shodhana (trinal reduction) across the 4 elemental triads.
    In each triad, subtracts the minimum value among the 3 signs from all 3 signs:
    x_i' = x_i - min(x_1, x_2, x_3).
    """
    reduced = list(bav_values)
    for triad in TRINAL_GROUPS:
        min_val = min(bav_values[s] for s in triad)
        for s in triad:
            reduced[s] = bav_values[s] - min_val
    return reduced


def ekadhipatya_shodhana(trikona_values: List[int], occupied_sign_indices: Set[int]) -> List[int]:
    """
    Applies Ekadhipatya Shodhana (reduction for signs with the same planetary lord)
    according to Maharishi Parashara's BPHS Chapter 68:
    - Cancer (Moon) and Leo (Sun) are exempt.
    - If either sign in a pair has 0 bindus, no reduction is made.
    - If both signs are occupied by planets, no reduction is made.
    - If neither sign is occupied:
        Subtract the minimum bindu count from both signs (x' = x - min(x, y), y' = y - min(x, y)).
    - If one sign is occupied and one is empty:
        If occupied has >= bindus than empty: empty becomes 0.
        If occupied has < bindus than empty: empty is reduced to equal occupied.
    """
    reduced = list(trikona_values)
    for s1, s2 in DUAL_RULED_PAIRS:
        v1, v2 = reduced[s1], reduced[s2]
        if v1 == 0 or v2 == 0:
            continue

        occ1 = s1 in occupied_sign_indices
        occ2 = s2 in occupied_sign_indices

        # Both occupied -> no reduction
        if occ1 and occ2:
            continue

        # Neither occupied -> subtract min from both
        if not occ1 and not occ2:
            m = min(v1, v2)
            reduced[s1] = v1 - m
            reduced[s2] = v2 - m
            continue

        # One occupied, one empty
        if occ1:
            occ_s, unocc_s = s1, s2
            occ_v, unocc_v = v1, v2
        else:
            occ_s, unocc_s = s2, s1
            occ_v, unocc_v = v2, v1

        if occ_v >= unocc_v:
            reduced[unocc_s] = 0
        else:
            reduced[unocc_s] = occ_v

    return reduced


def calculate_sarva_shodhana(total_sav: List[int], occupied_signs: Set[int]) -> Tuple[List[int], List[int]]:
    """
    Computes Trikona and Ekadhipatya Shodhana for Sarvashtakavarga (SAV).
    In Kala, SAV Trikona Shodhana reduces each sign's raw SAV count relative to the 26 baseline
    anchor point: (V - 26) % 12.
    Then Ekadhipatya Shodhana is applied to this reduced SAV Trikona array.
    """
    sav_trikona = [(v - 26) % 12 for v in total_sav]
    sav_epatya = ekadhipatya_shodhana(sav_trikona, occupied_signs)
    return sav_trikona, sav_epatya


def calculate_sodhya_pindas(shodhita_bav: List[int], occupied_signs: Dict[str, int]) -> Dict[str, int]:
    """
    Calculates Rasi Pinda, Graha Pinda, and Shodhya Pinda (Yoga Pinda) for a planet
    per BPHS Chapter 69:
    - Rasi Pinda = Sum over all 12 signs of (Shodhita_Bindu[i] * Rasi_Multiplier[i])
    - Graha Pinda = Sum over all 7 planets of (Shodhita_Bindu[planet_sign] * Graha_Multiplier[planet])
    - Shodhya Pinda = Rasi Pinda + Graha Pinda
    """
    rasi_pinda = sum(shodhita_bav[i] * RASI_MULTIPLIERS[i] for i in range(12))
    graha_pinda = 0
    for planet, p_sign in occupied_signs.items():
        if planet in GRAHA_MULTIPLIERS:
            graha_pinda += shodhita_bav[p_sign] * GRAHA_MULTIPLIERS[planet]

    yoga_pinda = rasi_pinda + graha_pinda
    return {
        'rasi_pinda': rasi_pinda,
        'graha_pinda': graha_pinda,
        'yoga_pinda': yoga_pinda
    }


def calculate_ashtakavarga_engine(chart_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Comprehensive entrypoint for Ashtakavarga calculation.
    Accepts chart_data from generate_kala_chart.
    """
    d1 = chart_data['vargas']['D1']
    d1_grahas = d1['grahas']

    natal_signs: Dict[str, int] = {}
    occupied_signs_set: Set[int] = set()
    planet_signs: Dict[str, int] = {}

    for p in ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']:
        sign_name = d1_grahas[p]['sign']
        idx = SIGN_TO_INDEX[sign_name]
        natal_signs[p] = idx
        planet_signs[p] = idx
        occupied_signs_set.add(idx)

    lagna_sign_name = d1['lagna']['sign']
    lagna_idx = SIGN_TO_INDEX[lagna_sign_name]
    natal_signs['Lagna'] = lagna_idx

    # Calculate BAV, Prastara, and Shodhana for all 8 entities
    entities = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Lagna']
    bav: Dict[str, List[int]] = {}
    prastara: Dict[str, Dict[str, List[int]]] = {}
    trikona: Dict[str, List[int]] = {}
    ekadhipatya: Dict[str, List[int]] = {}
    pindas: Dict[str, Dict[str, int]] = {}

    for ent in entities:
        bav[ent] = calculate_bav(ent, natal_signs)
        prastara[ent] = calculate_prastara(ent, natal_signs)
        trikona[ent] = trikona_shodhana(bav[ent])
        ekadhipatya[ent] = ekadhipatya_shodhana(trikona[ent], occupied_signs_set)
        if ent != 'Lagna':
            pindas[ent] = calculate_sodhya_pindas(ekadhipatya[ent], planet_signs)

    # Calculate Sarvashtakavarga (7 planets, sum = 337)
    total_sav = [sum(bav[p][s] for p in ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']) for s in range(12)]
    sav_trikona, sav_epatya = calculate_sarva_shodhana(total_sav, occupied_signs_set)

    return {
        'signs': ZODIAC_SIGNS,
        'bav': bav,
        'prastara': prastara,
        'trikona_shodhana': trikona,
        'ekadhipatya_shodhana': ekadhipatya,
        'sodhya_pindas': pindas,
        'sarvashtakavarga': {
            'total_sav': total_sav,
            'total_points': sum(total_sav),
            'trikona_shodhana': sav_trikona,
            'ekadhipatya_shodhana': sav_epatya
        }
    }
