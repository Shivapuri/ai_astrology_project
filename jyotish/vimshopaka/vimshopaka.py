"""
Precision Varga Vimshopaka Engine for Astra (Ernst Wilhelm's Kala Methodology).

Calculates:
1. 20-point Vimshopaka dignity scoring across four classical Parashari schemes:
   - Shadvarga (6 charts)
   - Saptavarga (7 charts)
   - Dasavarga (10 charts)
   - Shodashavarga (16 charts)
2. Vaisheshikamsa honorific classifications (BPHS Chapter 6, Verses 42-52):
   - Kimsuka, Vyanjana, Uttama, Gopura, Nagapushpa, Kanduka, Kerala, etc.
"""

from typing import Dict, List, Tuple, Any, Optional

# Parashari 20-point dignity values (BPHS Chapter 46, Verses 24-25)
DIGNITY_POINTS: Dict[str, float] = {
    'EX': 20.0,
    'MT': 20.0,
    'OH': 20.0,
    'GF': 18.0,
    'F':  15.0,
    'N':  10.0,
    'E':  7.0,
    'GE': 5.0,
    'DB': 0.0
}

# Dignity string mapping from Astra's dignity_breakdown
DIGNITY_NAME_TO_CODE: Dict[str, str] = {
    'Exalted': 'EX',
    'Exaltation': 'EX',
    'Moolatrikona': 'MT',
    'Own Sign': 'OH',
    "Own House": 'OH',
    "Great Friend's Sign": 'GF',
    "Friend's Sign": 'F',
    "Neutral's Sign": 'N',
    "Enemy's Sign": 'E',
    "Great Enemy's Sign": 'GE',
    'Debilitated': 'DB',
    'Debilitation': 'DB'
}

# Parashari Varga Scheme Weights (Totaling 20.0 points each)
SCHEME_WEIGHTS: Dict[str, Dict[str, float]] = {
    'Shadvarga': {
        'D1': 6.0, 'D2': 2.0, 'D3': 4.0, 'D9': 5.0, 'D12': 2.0, 'D30': 1.0
    },
    'Saptavarga': {
        'D1': 5.0, 'D2': 2.0, 'D3': 3.0, 'D7': 1.0, 'D9': 2.5, 'D12': 4.5, 'D30': 2.0
    },
    'Dasavarga': {
        'D1': 3.0, 'D2': 1.5, 'D3': 1.5, 'D7': 1.5, 'D9': 1.5,
        'D10': 1.5, 'D12': 1.5, 'D16': 1.5, 'D30': 1.5, 'D60': 5.0
    },
    'Shodasavarga': {
        'D1': 3.5, 'D2': 1.0, 'D3': 1.0, 'D4': 0.5, 'D7': 0.5, 'D9': 3.0,
        'D10': 0.5, 'D12': 0.5, 'D16': 2.0, 'D20': 0.5, 'D24': 0.5, 'D27': 0.5,
        'D30': 1.0, 'D40': 0.5, 'D45': 0.5, 'D60': 4.0
    }
}

# Vaisheshikamsa Honorific Names by scheme and count of auspicious vargas (BPHS 6.42-52)
# Auspicious varga = Exaltation (EX), Moolatrikona (MT), or Own House (OH)
VAISHESHIKAMSA_HONORIFICS: Dict[str, Dict[int, Tuple[str, str]]] = {
    'Shadvarga': {
        2: ('Kimsuka', 'Palash Tree'),
        3: ('Vyanjana', 'Insignia'),
        4: ('Chamara', 'Fly-whisk'),
        5: ('Chatra', 'Parasol/Umbrella'),
        6: ('Kundala', 'Ear-ring')
    },
    'Saptavarga': {
        2: ('Kimsuka', 'Palash Tree'),
        3: ('Vyanjana', 'Insignia'),
        4: ('Gopura', 'Temple gate'),
        5: ('Simhasana', 'Throne'),
        6: ('Paravata', 'Pigeon'),
        7: ('Devaloka', 'Divine realm')
    },
    'Dasavarga': {
        2: ('Kimsuka', 'Palash Tree'),
        3: ('Uttama', 'Excellent'),
        4: ('Gopura', 'Temple gate'),
        5: ('Simhasana', 'Throne'),
        6: ('Paravata', 'Pigeon'),
        7: ('Devaloka', 'Divine realm'),
        8: ('Brahmaloka', 'Realm of Brahma'),
        9: ('Shakravahana', 'Mount of Indra / Airavata'),
        10: ('Shridhama', 'Abode of Lakshmi')
    },
    'Shodasavarga': {
        2: ('Bhedaka', 'Distinctive'),
        3: ('Kusuma', 'Blossom'),
        4: ('Nagapushpa', 'Type of plant'),
        5: ('Kanduka', 'Playing ball'),
        6: ('Kerala', 'a Hora'),
        7: ('Kalpavriksha', 'Wish-fulfilling tree'),
        8: ('Chandanavana', 'Sandalwood forest'),
        9: ('Purnachandra', 'Full Moon'),
        10: ('Uchchaishrava', 'Divine celestial steed'),
        11: ('Dhanvantari', 'Divine Physician'),
        12: ('Suryakanta', 'Sun gem'),
        13: ('Vidruma', 'Coral'),
        14: ('Shakrasimhasana', 'Indra Throne'),
        15: ('Goloka', 'Highest celestial realm'),
        16: ('Shrivallabha', 'Beloved of Lakshmi')
    }
}


def get_dignity_code(dignity_str: str) -> str:
    """
    Converts a dignity name string (e.g. "Enemy's Sign" or "Ge/E") to standard 2-letter code.
    """
    if '/' in dignity_str:
        return dignity_str.split('/')[-1].strip()
    return DIGNITY_NAME_TO_CODE.get(dignity_str, 'N')


def calculate_scheme_score(
    planet_dignities: Dict[str, str],
    scheme_name: str
) -> Tuple[float, int, Optional[str], Optional[str]]:
    """
    Calculates the 20-point Vimshopaka score and Vaisheshikamsa honorific for a single planet.
    """
    weights = SCHEME_WEIGHTS[scheme_name]
    total_score = 0.0
    auspicious_count = 0

    for varga, weight in weights.items():
        dig_raw = planet_dignities.get(varga, 'N')
        dig_code = get_dignity_code(dig_raw)
        pts = DIGNITY_POINTS.get(dig_code, 10.0)
        total_score += weight * pts

        if dig_code in ('EX', 'MT', 'OH'):
            auspicious_count += 1

    final_score = round(total_score / 20.0, 2)

    # Vaisheshikamsa classification
    honorific_info = VAISHESHIKAMSA_HONORIFICS[scheme_name].get(auspicious_count)
    if honorific_info:
        name, meaning = honorific_info
        classification_str = f'({auspicious_count}) {name}'
    else:
        classification_str = '--'
        meaning = None

    return final_score, auspicious_count, classification_str, meaning


def calculate_varga_vimshopaka_engine(chart_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Comprehensive entrypoint for Varga Vimshopaka and Vaisheshikamsa.
    """
    planets = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']
    vargas = chart_data['vargas']

    # Extract dignity code for each planet across all available vargas
    planet_varga_dignities: Dict[str, Dict[str, str]] = {p: {} for p in planets}
    for v_name, v_data in vargas.items():
        v_grahas = v_data.get('grahas', {})
        for p in planets:
            if p in v_grahas:
                dig_full = v_grahas[p].get('dignity_breakdown', {}).get('final_dignity', 'Neutral')
                planet_varga_dignities[p][v_name] = dig_full

    scores: Dict[str, Dict[str, float]] = {s: {} for s in SCHEME_WEIGHTS}
    vaisheshikamsa: Dict[str, Dict[str, Any]] = {s: {} for s in SCHEME_WEIGHTS}

    for scheme_name in SCHEME_WEIGHTS:
        for p in planets:
            final_score, count, class_str, meaning = calculate_scheme_score(
                planet_varga_dignities[p], scheme_name
            )
            scores[scheme_name][p] = final_score
            vaisheshikamsa[scheme_name][p] = {
                'count': count,
                'honorific': class_str,
                'meaning': meaning
            }

    return {
        'scores': scores,
        'vaisheshikamsa': vaisheshikamsa,
        'scheme_weights': SCHEME_WEIGHTS,
        'dignity_points': DIGNITY_POINTS
    }
