def get_aspect(p1, p2, l1, l2, sign1, sign2, lord1, lord2):
    """
    Calculates the exact Graha Sphuta Drishti (Longitude Aspect) in Virupas (0-60).
    Implements Ernst Wilhelm's Graha Sutras mathematical logic.
    """
    if p1 == p2:
        return 0.0

    # 1. Parivartana Yoga (Mutual Reception) check:
    if lord1 == p2 and lord2 == p1:
        return 60.0

    diff = (l2 - l1) % 360
    
    # 2. Conjunction (within 30 degrees)
    if diff <= 30:
        return max(0, 60 - 2 * diff)
    elif diff >= 330:
        return max(0, 60 - 2 * (360 - diff))
        
    # 3. Normal Parashari Aspect
    if p1 not in ['Mars', 'Jupiter', 'Saturn']:
        return normal_aspect(diff)
    elif p1 == 'Mars':
        return mars_aspect(diff)
    elif p1 == 'Jupiter':
        return jupiter_aspect(diff)
    elif p1 == 'Saturn':
        return saturn_aspect(diff)

def normal_aspect(diff):
    if 30 < diff <= 60:
        return (diff - 30) / 2.0
    elif 60 < diff <= 90:
        return (diff - 60) + 15.0
    elif 90 < diff <= 120:
        return (120 - diff) / 2.0 + 30.0
    elif 120 < diff <= 150:
        return 150 - diff
    elif 150 < diff <= 180:
        return (diff - 150) * 2.0
    elif 180 < diff <= 300:
        return (300 - diff) / 2.0
    else:
        return 0.0

def mars_aspect(diff):
    if 90 < diff <= 120:
        return 60 - (diff - 90)
    elif 60 < diff <= 90:
        return (diff - 60) / 2.0 + 15.0
    elif 180 < diff <= 210:
        return 60.0
    elif 210 < diff <= 240:
        return 60 - (diff - 210)
    else:
        return normal_aspect(diff)

def jupiter_aspect(diff):
    if 90 < diff <= 120:
        return (diff - 90) / 2.0 + 45.0
    elif 120 < diff <= 150:
        return 60 - (diff - 120) * 2.0
    elif 210 < diff <= 240:
        return (diff - 210) / 2.0 + 45.0
    elif 240 < diff <= 270:
        return (30 - (diff - 240)) * 1.5 + 15.0
    else:
        return normal_aspect(diff)

def saturn_aspect(diff):
    if 60 < diff <= 90:
        return (diff - 60) * 2.0
    elif 270 < diff <= 300:
        return (300 - diff) * 2.0
    elif 30 < diff <= 60:
        return (diff - 30) / 2.0 + 45.0
    elif 240 < diff <= 270:
        return (diff - 240) / 2.0 + 45.0
    else:
        return normal_aspect(diff)
        
def calculate_avastha_matrix(grahas_data, shadbala_data, d1_grahas=None, baseline_type='ShadBala'):
    if d1_grahas is None: d1_grahas = grahas_data
    """
    Calculates the Quantitative Lajjitadi Avasthas matrix.
    Row = Giving Planet
    Col = Receiving Planet
    """
    planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    matrix = {}
    



    # Calculate Base Strengths
    # By default in Kala: Base = Shadbala (in Virupas) * Jagradadi * Baladi
    # This evaluates dynamically per Varga, as Jagrat/Bala change based on Varga Dignity and Varga Degree.
    
    bases = {}
    for p in planets:
        g = grahas_data[p]
        
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
            # Subha Phala is Ishta Phala in some traditions, or base naisargika.
            unmultiplied = shadbala_data[p].get('Ishta_Phala', 0)
        elif baseline_type == 'Drishti Yuti':
            unmultiplied = shadbala_data[p].get('Drik_Bala', 0)
        elif baseline_type == 'Veda':
            unmultiplied = shadbala_data[p]['Total_Virupas'] / 2 # fallback
        else:
            unmultiplied = shadbala_data[p]['Total_Virupas']
        
        jagrat = g['avasthas']['jagrat']['alertness']
        bala = g['avasthas']['bala']['strength']
        
        bases[p] = round(unmultiplied * jagrat * bala, 1)
    for p_give in planets:
        matrix[p_give] = {}
        for p_recv in planets:
            if p_give == p_recv:
                matrix[p_give][p_recv] = {
                    'pull': 0.0,
                    'total': bases[p_recv]
                }
                continue
                
            g_give = grahas_data[p_give]
            g_recv = grahas_data[p_recv]
            
            # Use D1 longitudes for aspect calculation (Graha Drishti is always from Rasi chart)
            l1 = d1_grahas[p_give]['longitude']
            l2 = d1_grahas[p_recv]['longitude']
            # We still use the current varga's signs/lords for Parivartana rules?
            # Wait, Parivartana Yoga (Exchange) for aspects is based on D1 signs!
            s1 = d1_grahas[p_give]['sign']
            s2 = d1_grahas[p_recv]['sign']
            lord1 = d1_grahas[p_give]['dignity_breakdown']['sign_lord']
            lord2 = d1_grahas[p_recv]['dignity_breakdown']['sign_lord']
            
            # Exact Graha Sphuta Drishti aspect (0-60 Virupas)
            aspect_virupas = get_aspect(p_give, p_recv, l1, l2, s1, s2, lord1, lord2)
            
            # Left Number: Pull (Points of Influence)
            pull = bases[p_give] * (aspect_virupas / 60.0)
            
            # Right Number: Determine sign (+/-)
            # This requires analyzing Lajjitadi relationships.
            # Simplified approach for now based on natural friendship.
            # Ernst Wilhelm rule:
            # - Friends / Benefics (Jupiter, Venus) add (+) if friendly/neutral.
            # - Enemies / Malefics (Saturn, Mars, Sun) subtract (-) if enemy.
            # Since we don't have the full boolean rules matrix coded here yet,
            # we provide the raw pull and let the engine or front-end decide,
            # OR we can implement the basic Friend/Enemy logic:
            

            # Fetch relationships
            from jyotish.relationships.relationships import get_natural_relationship
            rel = get_natural_relationship(p_recv, p_give) # How does recv view giving?
            
            # Default to 0
            sign_mult = 0
            
            # Mudita (Delighted): Planet is aspected/conjoined by a Great Friend, Friend, or Jupiter. Adds points.
            if rel in ["Friend", "Great Friend"] or p_give == "Jupiter":
                sign_mult = 1
                
            # Kshudhita (Starved): Planet is aspected/conjoined by an Enemy, or Saturn. Subtracts points.
            # Kshobhita (Agitated): Planet is aspected/conjoined by Sun, Mars, or Saturn. Subtracts points.
            # Note: Kshudhita/Kshobhita override Mudita (if Sun is a friend, it still Agitates and subtracts).
            if rel in ["Enemy", "Great Enemy"] or p_give in ["Sun", "Mars", "Saturn"]:
                sign_mult = -1
            total = bases[p_recv] + (sign_mult * pull)
            
            matrix[p_give][p_recv] = {
                'aspect_virupas': aspect_virupas,
                'pull': pull,
                'sign_mult': sign_mult,
                'total': total
            }
            
    return {
        'bases': bases,
        'matrix': matrix
    }
