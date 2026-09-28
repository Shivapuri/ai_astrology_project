"""
jyotish/report/interpretation_engine.py
Sequential Planetary Interpretation & Macro Canvas Synthesis Engine.

Implements Stages 2, 3, and 4 of Astra's chart assessment methodology:
1. Macrocosmic Background Canvas Synthesis (4 Foundational Spectrums).
2. Sequential 5-Pillar Planetary Decomposition in Prominence Order.
3. Semantic Commonalities vs. Clashes (Elements and Modalities only).
4. "Look Backwards" Macro Canvas Filtering.
5. Psychological Tone Modulation via Existing Read-Only Dignity.
6. Degree-Specific Harmonic Varga Overlays (D9, D7, D10 projected onto D1).
"""

from typing import Dict, Any, List, Optional, Tuple
import math

from jyotish.report.varga_environment import (
    ELEMENT_MAP, GUNA_MAP, POLARITY_MAP
)

ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

# Natural Archetypal Significations of Grahas
GRAHA_ARCHETYPES: Dict[str, Dict[str, Any]] = {
    "Sun": {
        "title": "Sūrya (Soul & Vitality)",
        "natural_element": "Fire",
        "natural_modality": "Fixed",
        "essence": "Vitality, authority, core self-worth, leadership, sovereignty, and father."
    },
    "Moon": {
        "title": "Candra (Mind & Perception)",
        "natural_element": "Water",
        "natural_modality": "Movable",
        "essence": "Sensory mind (Manas), emotional digest, mother, empathy, nurturance, and rhythm."
    },
    "Mars": {
        "title": "Maṅgala (Courage & Drive)",
        "natural_element": "Fire",
        "natural_modality": "Movable",
        "essence": "Focused courage, physical drive, technical execution, boundary defense, and ambition."
    },
    "Mercury": {
        "title": "Budha (Intellect & Commerce)",
        "natural_element": "Earth",
        "natural_modality": "Dual",
        "essence": "Discerning intellect (Buddhi), communication, analysis, adaptability, commerce, and speech."
    },
    "Jupiter": {
        "title": "Guru (Wisdom & Grace)",
        "natural_element": "Air",
        "natural_modality": "Dual",
        "essence": "Higher wisdom, expansive philosophy, ethical counsel, children, wealth, and grace."
    },
    "Venus": {
        "title": "Śukra (Desire & Refinement)",
        "natural_element": "Water",
        "natural_modality": "Fixed",
        "essence": "Aesthetic appreciation, relational diplomacy, sensual refinement, romance, and artistic creation."
    },
    "Saturn": {
        "title": "Śani (Discipline & Time)",
        "natural_element": "Air",
        "natural_modality": "Fixed",
        "essence": "Sober realism, perseverance, disciplined austerity (Tapas), structural longevity, and time (Kāla)."
    },
    "Rahu": {
        "title": "Rāhu (Ambition & Breakthrough)",
        "natural_element": "Air",
        "natural_modality": "Movable",
        "essence": "Intense worldly hunger, unconventional breakthroughs, obsessive innovation, and edge-pushing."
    },
    "Ketu": {
        "title": "Ketu (Mokṣa & Discernment)",
        "natural_element": "Fire",
        "natural_modality": "Dual",
        "essence": "Spiritual detachment (Mokṣa), deep insight, technical mastery, and dissolving worldly illusions."
    }
}

# Bhāva (House) Elemental & Modality Affinities
HOUSE_AFFINITIES: Dict[int, Dict[str, str]] = {
    1: {"element": "Fire", "modality": "Movable", "trine": "Dharma", "quad": "Kendra", "department": "Self, vitality, physical appearance"},
    2: {"element": "Earth", "modality": "Fixed", "trine": "Artha", "quad": "Panaphara", "department": "Accumulated wealth, speech, nourishment, lineage"},
    3: {"element": "Air", "modality": "Dual", "trine": "Kama", "quad": "Apoklima", "department": "Initiative, siblings, manual craft, courage"},
    4: {"element": "Water", "modality": "Movable", "trine": "Moksha", "quad": "Kendra", "department": "Inner peace, home, mother, emotional foundation"},
    5: {"element": "Fire", "modality": "Fixed", "trine": "Dharma", "quad": "Panaphara", "department": "Creative intelligence, intellect, children, purva punya"},
    6: {"element": "Earth", "modality": "Dual", "trine": "Artha", "quad": "Apoklima", "department": "Obstacles, daily routine, healing, debt, service"},
    7: {"element": "Air", "modality": "Movable", "trine": "Kama", "quad": "Kendra", "department": "Partnership, marriage, social contracts, public encounter"},
    8: {"element": "Water", "modality": "Fixed", "trine": "Moksha", "quad": "Panaphara", "department": "Transformation, longevity, shared resources, the occult"},
    9: {"element": "Fire", "modality": "Dual", "trine": "Dharma", "quad": "Apoklima", "department": "Higher philosophy, teachers, dharma, fortune, pilgrimage"},
    10: {"element": "Earth", "modality": "Movable", "trine": "Artha", "quad": "Kendra", "department": "Career, public reputation, status, worldly executive action"},
    11: {"element": "Air", "modality": "Fixed", "trine": "Kama", "quad": "Panaphara", "department": "Great gains, social networks, long-term goals, elder siblings"},
    12: {"element": "Water", "modality": "Dual", "trine": "Moksha", "quad": "Apoklima", "department": "Liberation, expenditure, spiritual retreat, foreign lands"}
}


# =============================================================================
# 1. MACROCOSMIC BACKGROUND CANVAS SYNTHESIS
# =============================================================================

def synthesize_background_canvas(
    polarity_core: Dict[str, Any],
    operational_axis: Dict[str, Any],
    env_tally: Dict[str, Any],
    nak_dominance: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Synthesizes the four foundational strings into a unified baseline personality canvas:
    1. Introversion vs. Extroversion
    2. Practicality vs. Idealism
    3. Individual Defiance vs. Social Cooperation
    4. Intellectual vs. Emotional Processing
    """
    # 1. Introversion vs Extroversion
    pol_pcts = env_tally.get("polarity", {}).get("percentages", {})
    active_pct = float(pol_pcts.get("Active", 50.0))
    passive_pct = float(pol_pcts.get("Passive", 50.0))

    if active_pct >= 58.0:
        ie_state = "Extroverted / Active Engagement"
        ie_summary = "Outwardly directed, proactive, initiates social and physical action readily."
    elif passive_pct >= 58.0:
        ie_state = "Introverted / Receptive Contemplation"
        ie_summary = "Self-contained, observant, processes experiences internally before taking outward action."
    else:
        ie_state = "Balanced Ambivert"
        ie_summary = "Easily balances public dynamic action with private recuperation."

    # 2. Practicality vs Idealism
    elem_pcts = env_tally.get("elements", {}).get("percentages", {})
    earth_pct = float(elem_pcts.get("Earth", 25.0))
    water_pct = float(elem_pcts.get("Water", 25.0))
    fire_pct = float(elem_pcts.get("Fire", 25.0))
    air_pct = float(elem_pcts.get("Air", 25.0))

    practical_pct = round(earth_pct + water_pct, 1)
    idealistic_pct = round(fire_pct + air_pct, 1)

    if practical_pct >= 58.0:
        pi_state = "Pragmatic Realism (Earth/Water Focus)"
        pi_summary = "Grounded in tangible realities, resource cultivation, and emotional stability."
    elif idealistic_pct >= 58.0:
        pi_state = "Visionary Idealism (Fire/Air Focus)"
        pi_summary = "Driven by conceptual possibilities, ethical ideals, inspiration, and bold futures."
    else:
        pi_state = "Balanced Realist-Visionary"
        pi_summary = "Integrates lofty aspirations with practical, step-by-step physical implementation."

    # 3. Individual Defiance vs Social Cooperation
    temp_breakdown = nak_dominance.get("temperament_breakdown", [])
    temp_dict = {item.get("group", ""): float(item.get("percentage", 16.7)) for item in temp_breakdown}

    tikshna_ugra = temp_dict.get("Tikshna", 16.7) + temp_dict.get("Ugra", 16.7)
    mridu_chara = temp_dict.get("Mridu", 16.7) + temp_dict.get("Chara", 16.7)

    if tikshna_ugra > mridu_chara + 8.0:
        dc_state = "Assertive Fortitude & Defiance"
        dc_summary = "Direct, uncompromising willpower that stands firm in adversity and resists easy coercion."
    elif mridu_chara > tikshna_ugra + 8.0:
        dc_state = "Harmonious Social Cooperation"
        dc_summary = "Flexible, tactful, socially graceful, seeking mutually beneficial connections."
    else:
        dc_state = "Balanced Self-Assertion"
        dc_summary = "Gentle and cooperative by default, but fiercely protective and firm when challenged."

    # 4. Intellectual vs Emotional Processing
    intellectual_score = air_pct + (10.0 if "Air" in elem_pcts else 0.0)
    emotional_score = water_pct + (10.0 if "Water" in elem_pcts else 0.0)

    if intellectual_score > emotional_score + 10.0:
        ie_proc_state = "Intellectual & Analytical Processing"
        ie_proc_summary = "Filters experiences through objective logic, mental categorization, and rational frameworks."
    elif emotional_score > intellectual_score + 10.0:
        ie_proc_state = "Emotional & Intuitive Digest"
        ie_proc_summary = "Understands situations through visceral resonance, empathic feeling, and instinctual discernment."
    else:
        ie_proc_state = "Integrated Mind & Emotion"
        ie_proc_summary = "Cognitive logic and deep emotional intuition work as mutual checks and balances."

    # Synthesis statement
    narrative_canvas = (
        f"The native's baseline stage presents as {ie_state.lower()} with {pi_state.lower()}. "
        f"Interpersonally, the operational rhythm favors {dc_state.lower()}, "
        f"while internal experiences are navigated through {ie_proc_state.lower()}."
    )

    return {
        "introversion_extroversion": {
            "active_percentage": active_pct,
            "passive_percentage": passive_pct,
            "state": ie_state,
            "summary": ie_summary
        },
        "practicality_idealism": {
            "practical_percentage": practical_pct,
            "idealistic_percentage": idealistic_pct,
            "state": pi_state,
            "summary": pi_summary
        },
        "defiance_cooperation": {
            "defiance_percentage": round(tikshna_ugra, 1),
            "cooperation_percentage": round(mridu_chara, 1),
            "state": dc_state,
            "summary": dc_summary
        },
        "intellectual_emotional": {
            "intellectual_score": round(intellectual_score, 1),
            "emotional_score": round(emotional_score, 1),
            "state": ie_proc_state,
            "summary": ie_proc_summary
        },
        "narrative_overview": narrative_canvas
    }


# =============================================================================
# 2. 5-PILLAR ARCHETYPAL DECOMPOSITION
# =============================================================================

def decompose_planet_5_pillars(
    planet: str,
    d1_graha: Dict[str, Any],
    nakshatra_data: Dict[str, Any],
    ruled_houses: List[int],
    house_num: int
) -> Dict[str, Any]:
    """
    Decomposes a planet into its 5 structural architectural pillars:
    1. Natural Planetary Symbolism (Naisargika Kāraka)
    2. Rāśi Sign (Kṣetra - Element & Modality)
    3. Bhāva House (Sthāna - Life Department & Trine)
    4. Nakshatra (Tāra - Asterism & Temperament Class)
    5. House Lordships (Adhipatya - Ruled Bhavas)
    """
    # 1. Natural Symbolism
    p_arch = GRAHA_ARCHETYPES.get(planet, {
        "title": planet,
        "natural_element": "Fire",
        "natural_modality": "Movable",
        "essence": "Planetary archetype."
    })

    # 2. Rāśi Sign
    sign = d1_graha.get("sign", "Aries")
    sign_element = ELEMENT_MAP.get(sign, "Fire")
    sign_modality = GUNA_MAP.get(sign, "Rajas (Movable)").split(" ")[1].replace("(", "").replace(")", "")

    # 3. Bhāva House
    h_aff = HOUSE_AFFINITIES.get(house_num, {
        "element": "Fire", "modality": "Movable", "trine": "Dharma", "quad": "Kendra", "department": "General life area"
    })

    # 4. Nakshatra
    nak_name = nakshatra_data.get("nakshatra", "Ashwini")
    nak_pada = nakshatra_data.get("pada", 1)
    nak_lord = nakshatra_data.get("nakshatra_lord", "--")
    nak_class = nakshatra_data.get("group", "Laghu")

    # 5. House Lordships
    lordship_desc = f"Rules House(s) {', '.join(str(h) for h in ruled_houses)}" if ruled_houses else "Rules no classical signs"

    return {
        "pillar_1_symbolism": {
            "title": p_arch["title"],
            "natural_element": p_arch["natural_element"],
            "natural_modality": p_arch["natural_modality"],
            "essence": p_arch["essence"]
        },
        "pillar_2_sign": {
            "sign": sign,
            "element": sign_element,
            "modality": sign_modality,
            "degree": d1_graha.get("degree_0_to_30", d1_graha.get("longitude", 0.0) % 30.0)
        },
        "pillar_3_house": {
            "house": house_num,
            "department": h_aff["department"],
            "house_element": h_aff["element"],
            "house_modality": h_aff["modality"],
            "trine_type": h_aff["trine"],
            "quad_type": h_aff["quad"]
        },
        "pillar_4_nakshatra": {
            "name": nak_name,
            "pada": nak_pada,
            "lord": nak_lord,
            "temperament_class": nak_class
        },
        "pillar_5_lordships": {
            "ruled_houses": ruled_houses,
            "description": lordship_desc
        }
    }


# =============================================================================
# 3. SEMANTIC INTERACTION ENGINE (Elements & Modalities Only)
# =============================================================================

def evaluate_semantic_dynamics(pillars: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compares theme pairs across the 5 pillars strictly using Elements and Modalities:
    - Commonalities (Resonances): Mutual reinforcement fostering clear gifts and flow.
    - Clashes (Dissonances): Conflicting elements/modalities generating creative friction.
    """
    p1 = pillars["pillar_1_symbolism"]
    p2 = pillars["pillar_2_sign"]
    p3 = pillars["pillar_3_house"]

    nat_elem = p1["natural_element"]
    sign_elem = p2["element"]
    house_elem = p3["house_element"]

    nat_mod = p1["natural_modality"]
    sign_mod = p2["modality"]
    house_mod = p3["house_modality"]

    resonances: List[str] = []
    clashes: List[str] = []

    # 1. Elemental Interaction (Natural vs Sign)
    if nat_elem == sign_elem:
        resonances.append(f"Pure Elemental Alignment: Planet natural {nat_elem} operates through resonant {sign_elem} sign, magnifying effortless expression.")
    elif (nat_elem == "Fire" and sign_elem == "Air") or (nat_elem == "Air" and sign_elem == "Fire"):
        resonances.append("Fire-Air Creative Synergy: Air stimulates and circulates the fiery drive, inspiring inventive action.")
    elif (nat_elem == "Earth" and sign_elem == "Water") or (nat_elem == "Water" and sign_elem == "Earth"):
        resonances.append("Earth-Water Fertile Synergy: Water nourishes tangible earth, producing stable materialization and steady depth.")
    elif (nat_elem == "Fire" and sign_elem == "Water") or (nat_elem == "Water" and sign_elem == "Fire"):
        clashes.append("Fire vs. Water Clash: Fiery impulse conflicts with watery emotional sensitivity, creating volatile cycles of passion and retreat.")
    elif (nat_elem == "Fire" and sign_elem == "Earth") or (nat_elem == "Earth" and sign_elem == "Fire"):
        clashes.append("Fire vs. Earth Clash: Impatient ambitious fire is slowed by heavy practical hesitation, requiring disciplined pacing.")
    elif (nat_elem == "Air" and sign_elem == "Earth") or (nat_elem == "Earth" and sign_elem == "Air"):
        clashes.append("Air vs. Earth Clash: Conceptual and theoretical aspirations encounter resistance from stubborn physical limitations.")
    elif (nat_elem == "Air" and sign_elem == "Water") or (nat_elem == "Water" and sign_elem == "Air"):
        clashes.append("Air vs. Water Clash: Intellectual detachment is unsettled by deep subconscious emotional currents.")

    # 2. Elemental Interaction (Sign vs House)
    if sign_elem == house_elem:
        resonances.append(f"Sign-House Elemental Harmony: {p2['sign']} ({sign_elem}) harmonizes with House {p3['house']} ({house_elem} Bhāva).")
    elif (sign_elem == "Fire" and house_elem == "Water") or (sign_elem == "Water" and house_elem == "Fire"):
        clashes.append(f"Sign-House Tension: {sign_elem} sign placed in {house_elem} house department creates environmental turbulence.")

    # 3. Modality Interaction (Planet vs Sign)
    if nat_mod == sign_mod:
        resonances.append(f"Modality Cadence Harmony: Natural {nat_mod} cadence moves in rhythm with {sign_mod} sign energy.")
    elif (nat_mod == "Movable" and sign_mod == "Fixed") or (nat_mod == "Fixed" and sign_mod == "Movable"):
        clashes.append(f"Modality Friction: Movable initiating velocity meets Fixed stubborn resistance, requiring patience.")
    elif (nat_mod == "Fixed" and sign_mod == "Dual") or (nat_mod == "Dual" and sign_mod == "Fixed"):
        clashes.append(f"Modality Friction: Desire for stability clashes with versatile multifaceted change.")

    # Overall Summary
    balance_status = "Harmonic Gift Flow" if len(resonances) > len(clashes) else ("Creative Developmental Tension" if clashes else "Neutral Integration")

    return {
        "resonances": resonances,
        "clashes": clashes,
        "resonance_count": len(resonances),
        "clash_count": len(clashes),
        "balance_status": balance_status
    }


# =============================================================================
# 4. "LOOK BACKWARDS" MACRO CANVAS FILTER
# =============================================================================

def apply_macro_canvas_filter(
    planet: str,
    pillars: Dict[str, Any],
    canvas: Dict[str, Any]
) -> str:
    """
    Filters individual planetary expressions through the background canvas.
    Ensures interpretations stay true to the native's macrocosmic landscape.
    """
    p_name = pillars["pillar_1_symbolism"]["title"].split(" ")[0]
    p_sign = pillars["pillar_2_sign"]["sign"]
    p_house = pillars["pillar_3_house"]["house"]

    ie_state = canvas.get("introversion_extroversion", {}).get("state", "Balanced")
    pi_state = canvas.get("practicality_idealism", {}).get("state", "Balanced")

    canvas_notes = []

    if "Introverted" in ie_state:
        canvas_notes.append(f"Because the background canvas is introverted, {p_name}'s action in House {p_house} operates through disciplined internal cultivation rather than boisterous outward display.")
    elif "Extroverted" in ie_state:
        canvas_notes.append(f"Under an extroverted canvas, {p_name} in {p_sign} projects its significations directly and prominently into public view.")

    if "Pragmatic" in pi_state:
        canvas_notes.append(f"The pragmatic background grounds {p_name}'s expression in measurable real-world outcomes and tangible security.")
    elif "Visionary" in pi_state:
        canvas_notes.append(f"The visionary canvas lifts {p_name} toward innovative concepts, higher ethics, and broad philosophical horizons.")

    return " ".join(canvas_notes) if canvas_notes else f"{p_name} operates with balanced integration across the macro personality canvas."


# =============================================================================
# 5. TONE MODULATION VIA READ-ONLY DIGNITY
# =============================================================================

def modulate_tone_with_dignity(dignity_data: Optional[Dict[str, Any]]) -> Dict[str, str]:
    """
    Ingests existing dignity scores strictly as psychological tone color:
    - expression_mode ("Constructive" vs. "Challenging")
    - net_scale_score
    - deeptadi & balaadi avasthas
    DOES NOT modify any mathematical dignity values.
    """
    if not dignity_data:
        return {
            "mode": "Balanced",
            "tone_color": "Neutral",
            "psychological_state": "Functional Baseline"
        }

    exp_mode = dignity_data.get("expression_mode", "Constructive")
    deeptadi = dignity_data.get("deeptadi", {}).get("state", "Swastha")
    net_score = dignity_data.get("net_scale_score", 0.0)

    if exp_mode == "Constructive" and net_score >= 0.5:
        tone_color = "Noble & Graceful"
        psych_state = f"Confident and self-reliant expression ({deeptadi}), channeling resources generously."
    elif exp_mode == "Challenging" or net_score < -0.5:
        tone_color = "Protective & Defensive"
        psych_state = f"Heightened internal vigilance ({deeptadi}), forging resilience through overcome obstacles."
    else:
        tone_color = "Dynamic Growth"
        psych_state = f"Balanced adaptive functioning ({deeptadi}), continually learning through trial and refinement."

    return {
        "mode": exp_mode,
        "tone_color": tone_color,
        "psychological_state": psych_state
    }


# =============================================================================
# 6. SEQUENTIAL PLANETARY INTERPRETATION ORCHESTRATOR
# =============================================================================

def generate_planetary_interpretations(
    prominence_rankings: Dict[str, Any],
    vargas_data: Dict[str, Any],
    nakshatras_grahas: Dict[str, Any],
    planetary_eval: Optional[Dict[str, Any]],
    canvas: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Sequentially unpacks and synthesizes planets in priority order of Prominence.
    Target 1 is formally designated as the #1 Chart Commander.
    """
    interpretations: List[Dict[str, Any]] = []

    leaderboard = prominence_rankings.get("leaderboard", [])
    d1_grahas = vargas_data.get("D1", {}).get("grahas", {})

    # Map house ownership from D1
    # Simple whole-sign lordship from Lagna
    lagna_sign = vargas_data.get("D1", {}).get("lagna", {}).get("sign", "Aries")
    l_idx = ZODIAC_SIGNS.index(lagna_sign) if lagna_sign in ZODIAC_SIGNS else 0

    SIGN_RULERS = {
        "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury", "Cancer": "Moon",
        "Leo": "Sun", "Virgo": "Mercury", "Libra": "Venus", "Scorpio": "Mars",
        "Sagittarius": "Jupiter", "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter"
    }

    graha_houses_ruled: Dict[str, List[int]] = {p: [] for p in GRAHA_ARCHETYPES}
    for h in range(1, 13):
        h_sign = ZODIAC_SIGNS[(l_idx + h - 1) % 12]
        ruler = SIGN_RULERS.get(h_sign)
        if ruler and ruler in graha_houses_ruled:
            graha_houses_ruled[ruler].append(h)

    for rank_idx, item in enumerate(leaderboard):
        planet = item.get("planet", "")
        prom_score = item.get("prominence_score", 1.0)
        is_commander = (rank_idx == 0)

        d1_g = d1_grahas.get(planet, {})
        nak_g = nakshatras_grahas.get(planet, {})

        p_sign = d1_g.get("sign", "Aries")
        p_idx = ZODIAC_SIGNS.index(p_sign) if p_sign in ZODIAC_SIGNS else 0
        house_num = (p_idx - l_idx) % 12 + 1

        ruled = graha_houses_ruled.get(planet, [])
        pillars = decompose_planet_5_pillars(planet, d1_g, nak_g, ruled, house_num)
        semantics = evaluate_semantic_dynamics(pillars)
        canvas_filter = apply_macro_canvas_filter(planet, pillars, canvas)

        dignity_info = planetary_eval.get(planet, {}) if planetary_eval else {}
        tone = modulate_tone_with_dignity(dignity_info)

        role_designation = "★ #1 Chart Commander (Kārakādhipati)" if is_commander else f"Rank #{rank_idx + 1} Planetary Pillar"

        interpretations.append({
            "planet": planet,
            "rank": rank_idx + 1,
            "role_designation": role_designation,
            "is_chart_commander": is_commander,
            "prominence_score": prom_score,
            "pillars": pillars,
            "semantic_dynamics": semantics,
            "macro_canvas_filter": canvas_filter,
            "tone_modulation": tone
        })

    return interpretations


# =============================================================================
# 7. DEGREE-SPECIFIC HARMONIC VARGA OVERLAYS (D9, D7, D10 onto D1)
# =============================================================================

def compute_harmonic_overlays(
    vargas_data: Dict[str, Any],
    d1_longitudes: Optional[Dict[str, float]] = None
) -> Dict[str, Any]:
    """
    Projects continuous harmonic longitudes for D9 (Navāṁśa), D7 (Saptāṁśa),
    and D10 (Daśāṁśa) onto the 360° natal wheel.
    Flags close conjunctions (<= 3°20' = 3.3333°) between harmonic positions
    and physical natal placements or angles (Ascendant).
    """
    if d1_longitudes is None:
        d1_longitudes = {}
        d1_lagna = vargas_data.get("D1", {}).get("lagna", {})
        if "longitude" in d1_lagna:
            d1_longitudes["Lagna"] = float(d1_lagna["longitude"])
        d1_grahas = vargas_data.get("D1", {}).get("grahas", {})
        for p, data in d1_grahas.items():
            if "longitude" in data:
                d1_longitudes[p] = float(data["longitude"])

    HARMONIC_MULTIPLIERS = {
        "D9": 9,   # Navāṁśa
        "D7": 7,   # Saptāṁśa
        "D10": 10  # Daśāṁśa
    }

    HARMONIC_DESCRIPTIONS = {
        "D9": "Navāṁśa (Soul Purpose & Inner Fruit)",
        "D7": "Saptāṁśa (Creative Legacy & Progeny)",
        "D10": "Daśāṁśa (Public Status & Career Manifestation)"
    }

    contacts: List[Dict[str, Any]] = []

    ORB_DEG = 3.3333333333333335  # Exactly 3°20'

    for v_code, multiplier in HARMONIC_MULTIPLIERS.items():
        v_title = HARMONIC_DESCRIPTIONS[v_code]

        for p_harm, lon_natal in d1_longitudes.items():
            # Continuous harmonic projection formula: (lon * N) % 360
            harm_lon = (lon_natal * multiplier) % 360.0

            # Compare against all physical natal longitudes
            for p_natal, nat_lon in d1_longitudes.items():
                diff = abs(harm_lon - nat_lon)
                shortest_dist = min(diff, 360.0 - diff)

                if shortest_dist <= ORB_DEG:
                    contacts.append({
                        "harmonic_chart": v_code,
                        "harmonic_title": v_title,
                        "harmonic_planet": p_harm,
                        "harmonic_degree": round(harm_lon, 2),
                        "natal_target": p_natal,
                        "natal_degree": round(nat_lon, 2),
                        "orb_separation": round(shortest_dist, 2),
                        "insight": f"{v_code} {p_harm} projects directly onto natal {p_natal} (within {round(shortest_dist, 2)}°), strongly reinforcing {p_harm} themes in {v_title}."
                    })

    return {
        "orb_limit_deg": 3.33,
        "total_contacts": len(contacts),
        "contacts": contacts
    }
