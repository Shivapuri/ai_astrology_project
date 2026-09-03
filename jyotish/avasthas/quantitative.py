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
        
def calculate_avastha_matrix(grahas_data, shadbala_data, d1_grahas=None, baseline_type='ShadBala'):
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
