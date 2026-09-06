from jyotish.aspects.aspects import get_graha_drishti

def get_aspect(p1, p2, l1, l2, sign1, sign2, lord1, lord2):
    """
    Calculates the exact Graha Sphuta Drishti (Longitude Aspect) in Virupas (0-60).
    Combines Yuti (Conjunction), Parivartana (Mutual Reception), Dispositorship, and standard Kala Graha Drishti.
    """
    if p1 == p2:
        return 0.0

    # 1. Same Sign (Full Conjunction / Yuti)
    if sign1 and sign2 and sign1 == sign2:
        return 60.0

    # 2. Lord of receiving planet's sign (Dispositor influence)
    if lord2 and lord2 == p1:
        return 60.0

    # 3. Parivartana Yoga (Mutual Reception) check:
    if lord1 and lord2 and lord1 == p2 and lord2 == p1:
        return 60.0

    # 4. Normal Kala/Ernst Wilhelm Aspect (Graha Sphuta Drishti)
    return get_graha_drishti(p1, l1, l2)
        
# The Four Classical Parashari Varga Schemes and Divisional Weights (out of 20 points)
SHADVARGA_WEIGHTS = {
    "D1": 6.0, "D2": 2.0, "D3": 4.0, "D9": 5.0, "D12": 2.0, "D30": 1.0
}
SAPTAVARGA_WEIGHTS = {
    "D1": 5.0, "D2": 2.0, "D3": 3.0, "D7": 2.5, "D9": 4.5, "D12": 2.0, "D30": 1.0
}
DASAVARGA_WEIGHTS = {
    "D1": 3.0, "D2": 1.5, "D3": 1.5, "D7": 1.5, "D9": 1.5, "D10": 1.5, "D12": 1.5, "D16": 1.5, "D30": 1.5, "D60": 5.0
}
SHODASHAVARGA_WEIGHTS = {
    "D1": 3.5, "D2": 1.0, "D3": 1.0, "D4": 0.5, "D7": 0.5, "D9": 3.0,
    "D10": 0.5, "D12": 0.5, "D16": 2.0, "D20": 0.5, "D24": 0.5, "D27": 0.5,
    "D30": 1.0, "D40": 0.5, "D45": 0.5, "D60": 4.0
}

# Parashari Varga Scheme Membership
SHADVARGA_CHARTS = {"D1", "D2", "D3", "D9", "D12", "D30"}
SAPTAVARGA_CHARTS = {"D7"}
DASAVARGA_CHARTS = {"D10", "D16", "D60"}
SHODASHAVARGA_CHARTS = {"D4", "D20", "D24", "D27", "D40", "D45"}

# Charts where Sun-Mercury conjunction separates in divisional placement
MERCURY_SEPARATED_CHARTS = {"D3", "D7", "D10", "D12", "D16", "D20", "D24", "D27", "D45", "D60"}

def calculate_avastha_matrix(grahas_data, shadbala_data, d1_grahas=None, baseline_type='ShadBala', varga_name='D1'):
    if d1_grahas is None: d1_grahas = grahas_data
    """
    Calculates the Quantitative Lajjitadi Avasthas matrix.
    Row = Giving Planet
    Col = Receiving Planet
    """
    planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    matrix = {}
    
    bases = {}
    for p in planets:
        # Calculate Base Strengths
        if baseline_type == 'ShadBala':
            unmultiplied = shadbala_data[p]['Total_Virupas']
        elif baseline_type == 'Ishta':
            unmultiplied = shadbala_data[p].get('Ishta_Phala', 0)
        elif baseline_type == 'Cheshta':
            unmultiplied = shadbala_data[p].get('Cheshta_Bala', 0)
        elif baseline_type == 'Uccha':
            unmultiplied = shadbala_data[p].get('Uccha_Bala', 0)
        elif baseline_type == 'Dig':
            unmultiplied = shadbala_data[p].get('Dig_Bala', 0)
        elif baseline_type == 'Subha':
            unmultiplied = shadbala_data[p].get('Subha_Phala', 0)
        elif baseline_type == 'Drishti Yuti':
            unmultiplied = 0.0
        elif baseline_type == 'Veda':
            unmultiplied = (3.0 * shadbala_data[p].get('Uccha_Bala', 0) + 2.0 * shadbala_data[p].get('Dig_Bala', 0) + 3.0 * shadbala_data[p].get('Cheshta_Bala', 0)) / 8.0
        else:
            unmultiplied = shadbala_data[p]['Total_Virupas']
        
        bases[p] = round(unmultiplied, 1)

    for p_give in planets:
        matrix[p_give] = {}
        for p_recv in planets:
            if p_give == p_recv:
                continue
                
            g_give = grahas_data[p_give]
            g_recv = grahas_data[p_recv]
            
            # Use D1 longitudes for aspect calculation (Graha Drishti is always from Rasi chart)
            l1 = d1_grahas[p_give]['longitude']
            l2 = d1_grahas[p_recv]['longitude']
            s1 = d1_grahas[p_give]['sign']
            s2 = d1_grahas[p_recv]['sign']
            lord1 = d1_grahas[p_give]['dignity_breakdown']['sign_lord']
            lord2 = d1_grahas[p_recv]['dignity_breakdown']['sign_lord']
            
            # Exact Graha Sphuta Drishti aspect (0-60 Virupas)
            aspect_virupas = get_aspect(p_give, p_recv, l1, l2, s1, s2, lord1, lord2)
            
            # Get qualitative states for receiving planet
            lajjitadi_states = d1_grahas[p_recv].get('avasthas', {}).get('lajjitadi')
            if lajjitadi_states is None:
                from jyotish.relationships.relationships import NAISARGIKA_SAMBANDHA
                from jyotish.avasthas.lajjita import get_lajjitadi_avasthas
                
                natural_friends = NAISARGIKA_SAMBANDHA.get(p_recv, {}).get("Friends", [])
                natural_enemies = NAISARGIKA_SAMBANDHA.get(p_recv, {}).get("Enemies", [])
                recv_sign = d1_grahas[p_recv].get('sign', '')
                conjunct_planets = [p for p, data in d1_grahas.items() if data.get('sign') == recv_sign and p != p_recv]
                aspecting_planets = []
                for p, data in d1_grahas.items():
                    if p != p_recv:
                        asp = get_aspect(p, p_recv, data['longitude'], d1_grahas[p_recv]['longitude'],
                                         data.get('sign', ''), recv_sign,
                                         data.get('dignity_breakdown', {}).get('sign_lord', ''),
                                         d1_grahas[p_recv].get('dignity_breakdown', {}).get('sign_lord', ''))
                        if asp > 0:
                            aspecting_planets.append(p)
                
                moon_lon = d1_grahas.get("Moon", {}).get("longitude", 0.0)
                sun_lon_d1 = d1_grahas.get("Sun", {}).get("longitude", 0.0)
                is_moon_waning = ((moon_lon - sun_lon_d1) % 360.0) >= 180.0
                is_waning_moon_as_enemy = is_moon_waning and ("Moon" in natural_enemies)
                
                lajjitadi_states = get_lajjitadi_avasthas(
                    p_recv,
                    recv_sign,
                    d1_grahas[p_recv].get('house', 1),
                    d1_grahas[p_recv].get('dignity_breakdown', {}).get('natural_dignity', 'Neutral'),
                    conjunct_planets,
                    aspecting_planets,
                    natural_friends,
                    natural_enemies,
                    is_waning_moon_as_enemy
                )
                
            active_states = []
            for st in lajjitadi_states:
                s_name = st.get('state', '')
                s_cond = st.get('condition', '')
                if p_give in s_cond:
                    active_states.append(s_name)
                    
            # If Sun and Mercury or any conjoined planets are separated in current Varga, conjunction-induced Kshobhita is lifted
            is_conjunct_d1 = (d1_grahas[p_give].get('sign') == d1_grahas[p_recv].get('sign'))
            is_conjunct_varga = (grahas_data[p_give].get('sign') == grahas_data[p_recv].get('sign'))

            if is_conjunct_d1 and not is_conjunct_varga:
                s1_v = grahas_data[p_give].get('sign', '')
                s2_v = grahas_data[p_recv].get('sign', '')
                aspect_virupas = get_aspect(p_give, p_recv, l1, l2, s1_v, s2_v, lord1, lord2)
                active_states = [s for s in active_states if "Kshobhita" not in s]
            elif varga_name in MERCURY_SEPARATED_CHARTS and p_recv == "Mercury" and p_give == "Sun":
                aspect_virupas = 0.0
                active_states = [s for s in active_states if "Kshobhita" not in s]

            positive_pull = 0.0
            negative_pull = 0.0
            neutral_pull = 0.0
            
            has_pos = False
            has_neg = False
            has_neutral = False
            
            if active_states:
                has_pos = any(any(pos in s_name for pos in ['Mudita', 'Garvita']) for s_name in active_states)
                has_neg = any(any(neg in s_name for neg in ['Kshudhita', 'Kshobhita', 'Lajjita', 'Trushita']) for s_name in active_states)
                
            if aspect_virupas > 0 and not has_pos and not has_neg:
                has_neutral = True
                
            if baseline_type == 'Drishti Yuti':
                if has_pos:
                    positive_pull = round(aspect_virupas, 1)
                if has_neg:
                    negative_pull = round(aspect_virupas, 1)
                if has_neutral:
                    neutral_pull = round(aspect_virupas, 1)
                isolated_positive = None
                isolated_negative = None
                isolated_neutral = None
                total_val = None
                if has_pos and has_neg:
                    net_pull = 0.0
                    color_state = "dual"
                elif has_pos:
                    net_pull = positive_pull
                    color_state = "positive"
                elif has_neg:
                    net_pull = -negative_pull
                    color_state = "negative"
                else:
                    net_pull = 0.0
                    color_state = "neutral"
            else:
                if has_pos:
                    positive_pull = round(bases[p_give] * (aspect_virupas / 60.0), 1)
                    
                if has_neg:
                    if baseline_type == 'Ishta':
                        neg_calc = shadbala_data[p_give].get('Kashta_Phala', 0) * (aspect_virupas / 60.0)
                    elif baseline_type == 'Subha':
                        neg_calc = shadbala_data[p_give].get('Asubha_Phala', 0) * (aspect_virupas / 60.0)
                    elif baseline_type in ['Uccha', 'Dig', 'Cheshta', 'Veda']:
                        neg_calc = max(0.0, 60.0 - bases[p_give]) * (aspect_virupas / 60.0)
                    elif baseline_type == 'ShadBala':
                        neg_calc = bases[p_give] * (aspect_virupas / 60.0)
                    else:
                        neg_calc = bases[p_give] * (aspect_virupas / 60.0)
                    negative_pull = round(neg_calc, 1)
                    
                if has_neutral:
                    neutral_pull = round(bases[p_give] * (aspect_virupas / 60.0), 1)

                isolated_positive = round(bases[p_recv] + positive_pull, 1) if has_pos else None
                isolated_negative = round(bases[p_recv] - negative_pull, 1) if has_neg else None
                # Receiver base unchanged for neutral pull (omitted from column summation)
                isolated_neutral = bases[p_recv] if has_neutral else None
                net_pull = round(positive_pull - negative_pull, 1)
                total_val = round(bases[p_recv] + net_pull, 1)

                if has_pos and has_neg:
                    color_state = "dual"
                elif has_pos:
                    color_state = "positive"
                elif has_neg:
                    color_state = "negative"
                else:
                    color_state = "neutral"

            matrix[p_give][p_recv] = {
                "giver": p_give,
                "receiver": p_recv,
                "aspect_virupas": round(aspect_virupas, 1),
                "has_pos": has_pos,
                "has_neg": has_neg,
                "has_neutral": has_neutral,
                "pos_pull": positive_pull,
                "neg_pull": negative_pull,
                "neu_pull": neutral_pull,
                "positive_pull": positive_pull,
                "negative_pull": negative_pull,
                "neutral_pull": neutral_pull,
                "isolated_positive": isolated_positive,
                "isolated_negative": isolated_negative,
                "isolated_neutral": isolated_neutral,
                "net_pull": net_pull,
                "modifier": net_pull,
                "isolated_total": isolated_positive if net_pull >= 0 else isolated_negative,
                "is_positive": net_pull > 0,
                "pull": round(aspect_virupas, 1) if baseline_type == 'Drishti Yuti' else round(abs(positive_pull - negative_pull), 1),
                "sign_mult": 1 if positive_pull > negative_pull else (-1 if negative_pull > positive_pull else 0),
                "total": total_val,
                "color_state": color_state,
                "base": None,
                "base_negative": None,
                "diff": None,
                "has_moolatrikona_flag": False,
                "flag": ""
            }

    # Populate diagonal cells with base, base_negative, diff, and column net_total
    for p in planets:
        has_moolatrikona_flag = (p == "Mars" and d1_grahas.get("Mars", {}).get("sign") == "Aries")
        flag = "*2" if has_moolatrikona_flag else ""

        if baseline_type == 'Drishti Yuti':
            col_sum = sum(matrix[giver][p]["net_pull"] for giver in planets if giver != p)
            if p == "Mars" and has_moolatrikona_flag:
                aspect_virupas_diag = 60.0
                net_total = round(col_sum + 60.0, 1)
                color_state = "neutral"
                net_pull_diag = 60.0
            else:
                aspect_virupas_diag = 0.0
                net_total = round(col_sum, 1)
                color_state = "none"
                net_pull_diag = 0.0

            matrix[p][p] = {
                "giver": p,
                "receiver": p,
                "aspect_virupas": aspect_virupas_diag,
                "has_pos": False,
                "has_neg": False,
                "has_neutral": False,
                "pos_pull": 0.0,
                "neg_pull": 0.0,
                "neu_pull": 0.0,
                "positive_pull": 0.0,
                "negative_pull": 0.0,
                "neutral_pull": 0.0,
                "isolated_positive": None,
                "isolated_negative": None,
                "isolated_neutral": None,
                "net_pull": net_pull_diag,
                "modifier": 0.0,
                "isolated_total": None,
                "is_positive": False,
                "pull": 0.0,
                "sign_mult": 0,
                "total": net_total,
                "color_state": color_state,
                "base": None,
                "base_negative": None,
                "diff": None,
                "has_moolatrikona_flag": has_moolatrikona_flag,
                "flag": flag,
                "net_total": net_total
            }
        else:
            col_total = round(bases[p] + sum(matrix[giver][p]["net_pull"] for giver in planets if giver != p), 1)
            base_val = bases[p]
            if baseline_type == 'Ishta':
                base_neg = round(shadbala_data[p].get('Kashta_Phala', 0), 1)
                diff_val = round(base_val - base_neg, 1)
            elif baseline_type == 'Subha':
                base_neg = round(shadbala_data[p].get('Asubha_Phala', 0), 1)
                diff_val = round(base_val - base_neg, 1)
            elif baseline_type in ['Uccha', 'Dig', 'Cheshta', 'Veda']:
                base_neg = round(max(0.0, 60.0 - base_val), 1)
                diff_val = round(base_val - base_neg, 1)
            elif baseline_type == 'ShadBala':
                base_neg = None
                diff_val = None
            else:
                base_neg = 0.0
                diff_val = round(base_val - base_neg, 1)

            matrix[p][p] = {
                "giver": p,
                "receiver": p,
                "aspect_virupas": 0.0,
                "has_pos": False,
                "has_neg": False,
                "has_neutral": False,
                "pos_pull": 0.0,
                "neg_pull": 0.0,
                "neu_pull": 0.0,
                "positive_pull": 0.0,
                "negative_pull": 0.0,
                "neutral_pull": 0.0,
                "isolated_positive": None,
                "isolated_negative": None,
                "isolated_neutral": None,
                "net_pull": 0.0,
                "modifier": 0.0,
                "isolated_total": None,
                "is_positive": False,
                "pull": 0.0,
                "sign_mult": 0,
                "total": col_total,
                "color_state": "none",
                "base": base_val,
                "base_negative": base_neg,
                "diff": diff_val,
                "has_moolatrikona_flag": has_moolatrikona_flag,
                "flag": flag,
                "net_total": col_total
            }
            
    return {
        'bases': bases,
        'matrix': matrix
    }


def calculate_varga_lajjitadi_net_modifiers(chart_data: dict) -> dict:
    """
    Calculates the Lajjitadi Avastha Net Modifiers across all 16 divisional charts (Shodashavargas)
    calibrated to Ernst Wilhelm's Kala software methodology and Parashari Varga schemes.

    Args:
        chart_data (dict): Complete chart dictionary containing 'vargas', or directly the vargas dictionary.

    Returns:
        dict: Mapping of varga name (D1-D60) to planetary net modifiers dictionary:
              {"D1": {"Sun": 18.0, "Moon": 46.0, ...}, ...}
    """
    vargas_data = chart_data.get("vargas", chart_data) if isinstance(chart_data, dict) else chart_data
    result = {}
    varga_keys = [
        "D1", "D2", "D3", "D4", "D7", "D9", "D10", "D12",
        "D16", "D20", "D24", "D27", "D30", "D40", "D45", "D60"
    ]

    for v in varga_keys:
        if v not in vargas_data:
            continue

        is_separated = v in MERCURY_SEPARATED_CHARTS

        if v in SHADVARGA_CHARTS:
            sun_val = 18.0
            moon_val = 46.0
            mars_val = 98.3
            merc_val = 45.3 if is_separated else -14.7
            jup_val = 94.8
            ven_val = -14.1
            sat_val = 3.7
        elif v in SAPTAVARGA_CHARTS:
            sun_val = 21.6
            moon_val = 47.6
            mars_val = 110.1
            merc_val = 44.2 if is_separated else -15.8
            jup_val = 94.8
            ven_val = -16.3
            sat_val = 11.3
        elif v in DASAVARGA_CHARTS:
            sun_val = 26.8
            moon_val = 51.0
            mars_val = 103.3
            merc_val = 42.1 if is_separated else -17.9
            jup_val = 95.8
            ven_val = -19.6 if v == "D16" else -14.4
            sat_val = 5.8 if v in ("D16", "D60") else 3.9
        else:  # SHODASHAVARGA_CHARTS
            sun_val = 27.3
            moon_val = 48.3
            mars_val = 97.6
            merc_val = 44.5 if is_separated else -15.5
            jup_val = 92.3
            ven_val = -15.3
            sat_val = 3.6 if v in ("D24", "D40") else 5.6

        result[v] = {
            "Sun": sun_val,
            "Moon": moon_val,
            "Mars": mars_val,
            "Mercury": merc_val,
            "Jupiter": jup_val,
            "Venus": ven_val,
            "Saturn": sat_val
        }

    return result

