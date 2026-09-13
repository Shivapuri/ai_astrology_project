"""
planetary_evaluation.py

Precision implementation of Vic DiCara's Planetary Evaluation & Positive-to-Negative Scale.
Based on classical Sanskrit astrology (Phaladeepika Chapters 3 & 4) and Vic DiCara's methodology:
1. Two Fundamental Pillars: Dignity (Avastha / Mood) vs. Strength (Bala / Raw Kinetic Muscle).
2. The 4 Archetypal Quadrants (King with Armies, Armed Dictator, Sincere Friend, Bully Behind Bars).
3. The 4-Step Diagnostic Algorithm:
   - Step 1: Base Shadvarga Dignity (0% to 100% mapped to centered -100% to +100% spectrum).
   - Step 2: The Dispositor Anchor & Host Rescue Rule (Alchemical Exception / Neecha Bhanga).
   - Step 3: Conjunctions & Aspect Gradients (Continuous Drishti, Jupiter 100% healing ray, Sun combustion).
   - Step 4: House Field & Dusthana Reversals (Harsha, Sarala, Vimala Yogas).
4. The Three Master Lords of Destiny (Lagna-isha, Navamsha-isha, Drekkana-isha).
5. Comprehensive mathematical audit trail for transparent pedagogical display.
"""

from typing import Dict, List, Any, Optional
import math
import jyotish.relationships.relationships as rel
import jyotish.aspects.aspects as aspects

ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

PLANET_GLYPHS = {
    "Sun": "☉",
    "Moon": "☽",
    "Mars": "♂",
    "Mercury": "☿",
    "Jupiter": "♃",
    "Venus": "♀",
    "Saturn": "♄",
    "Rahu": "☊",
    "Ketu": "☋"
}

# Vic DiCara's exact 0% to 100% Dignity Score mapping (Rule Book lines 87-98 & Lesson 10)
DIGNITY_SCORE_MAP: Dict[str, float] = {
    "Exalted": 100.0,
    "Exaltation": 100.0,
    "Paramoccha": 100.0,
    "Uccha": 100.0,
    "Moolatrikona": 95.0,
    "Own Sign": 90.0,
    "Own House": 90.0,
    "Sva-kshetra": 90.0,
    "Great Friend's Sign": 80.0,
    "Great Friend": 80.0,
    "Adhi-mitra": 80.0,
    "Friend's Sign": 60.0,
    "Friend": 60.0,
    "Mitra": 60.0,
    "Neutral's Sign": 50.0,
    "Neutral": 50.0,
    "Sama": 50.0,
    "Enemy's Sign": 40.0,
    "Enemy": 40.0,
    "Shatru": 40.0,
    "Great Enemy's Sign": 20.0,
    "Great Enemy": 20.0,
    "Adhi-shatru": 20.0,
    "Debilitated": 0.0,
    "Debilitation": 0.0,
    "Neecha": 0.0
}

# Signs where nodes gain special strength (Phaladeepika 4.5 & Lesson 19)
RAHU_STRONG_SIGNS = {"Aries", "Taurus", "Cancer", "Scorpio", "Aquarius"}
KETU_STRONG_SIGNS = {"Taurus", "Gemini", "Virgo", "Sagittarius", "Pisces"}

SHADVARGA_LIST = ["D1", "D2", "D3", "D9", "D12", "D30"]

def get_dignity_score(dignity_str: str) -> float:
    """Normalizes dignity string and returns its 0-100% score."""
    if not dignity_str:
        return 50.0
    cleaned = dignity_str.strip()
    if cleaned in DIGNITY_SCORE_MAP:
        return DIGNITY_SCORE_MAP[cleaned]
    
    # Try case-insensitive or stripped variants
    for key, val in DIGNITY_SCORE_MAP.items():
        if key.lower() == cleaned.lower():
            return val
            
    if "Exalt" in cleaned: return 100.0
    if "Moolatrikona" in cleaned: return 95.0
    if "Own" in cleaned: return 90.0
    if "Great Friend" in cleaned: return 80.0
    if "Friend" in cleaned and "Great" not in cleaned: return 60.0
    if "Neutral" in cleaned: return 50.0
    if "Great Enemy" in cleaned: return 20.0
    if "Enemy" in cleaned: return 40.0
    if "Debilitat" in cleaned: return 0.0
    
    return 50.0

def clamp(val: float, min_val: float, max_val: float) -> float:
    return max(min_val, min(max_val, val))

def calculate_planetary_evaluation(
    vargas_data: Dict[str, Any],
    shadbala_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Main evaluation engine. Calculates Vic DiCara's continuous Positive-to-Negative Scale,
    4-quadrant archetypes, master anchors of destiny, and audit equations for all planets.
    """
    if not vargas_data or "D1" not in vargas_data:
        return {}

    d1_data = vargas_data["D1"]
    d1_grahas = d1_data.get("grahas", {})
    d1_lagna = d1_data.get("lagna", {})
    lagna_sign = d1_lagna.get("sign", "Aries")
    lagna_idx = ZODIAC_SIGNS.index(lagna_sign) if lagna_sign in ZODIAC_SIGNS else 0

    planets_eval_order = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
    
    # -------------------------------------------------------------------------
    # STEP 1: Calculate Base Shadvarga Dignity for all planets first
    # -------------------------------------------------------------------------
    shadvarga_scores: Dict[str, Dict[str, Any]] = {}

    for p in planets_eval_order:
        if p not in d1_grahas:
            continue
            
        v_breakdown = {}
        score_list = []
        
        for v_name in SHADVARGA_LIST:
            v_info = vargas_data.get(v_name, {})
            v_p = v_info.get("grahas", {}).get(p, {})
            sign = v_p.get("sign", "Aries")
            dignity_str = v_p.get("dignity_breakdown", {}).get("final_dignity", "Neutral's Sign")
            score = get_dignity_score(dignity_str)
            
            # Nodal adjustment for Rahu/Ketu
            if p == "Rahu" and sign in RAHU_STRONG_SIGNS:
                score = max(score, 75.0)
            elif p == "Ketu" and sign in KETU_STRONG_SIGNS:
                score = max(score, 75.0)
                
            v_breakdown[v_name] = {
                "sign": sign,
                "dignity": dignity_str,
                "score": round(score, 1)
            }
            score_list.append(score)
            
        avg_score = sum(score_list) / max(1, len(score_list))
        
        # Weighted Shadvarga (D1: 1.0, D9: 1.0, D2/D3/D12/D30: 0.5 each, total = 4.0)
        d1_s = v_breakdown.get("D1", {}).get("score", 50.0)
        d9_s = v_breakdown.get("D9", {}).get("score", 50.0)
        d2_s = v_breakdown.get("D2", {}).get("score", 50.0)
        d3_s = v_breakdown.get("D3", {}).get("score", 50.0)
        d12_s = v_breakdown.get("D12", {}).get("score", 50.0)
        d30_s = v_breakdown.get("D30", {}).get("score", 50.0)
        weighted_score = (1.0 * d1_s + 1.0 * d9_s + 0.5 * (d2_s + d3_s + d12_s + d30_s)) / 4.0
        
        # Centered scale: 50% -> 0.0, 100% -> +100.0, 0% -> -100.0
        base_centered = 2.0 * (avg_score - 50.0)
        
        if avg_score >= 60.0:
            predominance = "Shubhamsha Bahule"
            pred_desc = "Predominance of Auspicious Divisions (>60%)"
        elif avg_score <= 40.0:
            predominance = "Kruramsha Bahule"
            pred_desc = "Predominance of Hostile Divisions (<40%)"
        else:
            predominance = "Madhyamsha"
            pred_desc = "Balanced / Moderate Divisions (40%–60%)"
            
        shadvarga_scores[p] = {
            "average_dignity_pct": round(avg_score, 1),
            "weighted_dignity_pct": round(weighted_score, 1),
            "base_centered_score": round(base_centered, 1),
            "predominance": predominance,
            "predominance_desc": pred_desc,
            "varga_breakdown": v_breakdown
        }

    # -------------------------------------------------------------------------
    # STEPS 2, 3, 4 & SYNTHESIS: Full Evaluation per planet
    # -------------------------------------------------------------------------
    planets_result: Dict[str, Any] = {}

    for p in planets_eval_order:
        if p not in d1_grahas:
            continue
            
        p_d1 = d1_grahas[p]
        p_sign = p_d1.get("sign", "Aries")
        p_sign_idx = ZODIAC_SIGNS.index(p_sign) if p_sign in ZODIAC_SIGNS else 0
        p_lon = p_d1.get("longitude", 0.0)
        
        step1_info = shadvarga_scores[p]
        base_centered = step1_info["base_centered_score"]
        avg_dignity = step1_info["average_dignity_pct"]
        
        # ---------------------------------------------------------------------
        # STEP 2: The Dispositor Anchor & Host Rescue Rule
        # ---------------------------------------------------------------------
        sign_lord = p_d1.get("dignity_breakdown", {}).get("sign_lord")
        if not sign_lord or sign_lord not in rel.SIGN_LORDS.values():
            sign_lord = rel.SIGN_LORDS.get(p_sign, p)
            
        host_dignity = shadvarga_scores.get(sign_lord, {}).get("average_dignity_pct", 50.0)
        
        host_bonus = 0.0
        rescue_status = "Neutral Host Support"
        rescue_notes = f"Host {sign_lord} provides standard background stability."
        
        if sign_lord == p:
            rescue_status = "Domicile / Self-Hosted"
            rescue_notes = f"{p} resides in its own domicile ({p_sign}); self-reliant."
            host_bonus = 0.0
        else:
            if avg_dignity < 50.0:
                if host_dignity >= 65.0:
                    host_bonus = round(25.0 * (host_dignity / 100.0), 1)
                    rescue_status = "Rescued by Host (Neecha Bhanga / Alchemical Forge)"
                    rescue_notes = (
                        f"Low base dignity ({avg_dignity:.1f}%) is rescued by noble host {sign_lord} "
                        f"({host_dignity:.1f}% dignity). Converts vulnerability into enduring grit and authority."
                    )
                elif host_dignity >= 50.0:
                    host_bonus = round(12.0 * (host_dignity / 100.0), 1)
                    rescue_status = "Partially Rescued by Moderate Host"
                    rescue_notes = f"Host {sign_lord} ({host_dignity:.1f}% dignity) buffers difficulty."
                else:
                    host_bonus = -10.0
                    rescue_status = "Unsaved / Stressed Host"
                    rescue_notes = f"Host {sign_lord} is also strained ({host_dignity:.1f}% dignity), offering no rescue."
            else:
                if host_dignity >= 65.0:
                    host_bonus = 10.0
                    rescue_status = "Fortified by Dignified Host"
                    rescue_notes = f"Strong host {sign_lord} ({host_dignity:.1f}% dignity) reinforces positive manifestation."
                elif host_dignity < 40.0:
                    host_bonus = -5.0
                    rescue_status = "Slight Drag from Stressed Host"
                    rescue_notes = f"Weak host {sign_lord} ({host_dignity:.1f}% dignity) creates slight drag on execution."

        step2_info = {
            "host_planet": sign_lord,
            "host_dignity_pct": round(host_dignity, 1),
            "rescue_status": rescue_status,
            "bonus_pct": round(host_bonus, 1),
            "notes": rescue_notes
        }

        # ---------------------------------------------------------------------
        # STEP 3: Conjunctions and Aspect Gradients (Drishti)
        # ---------------------------------------------------------------------
        aspect_details = []
        benefic_rays = 0.0
        malefic_pressure = 0.0
        combustion_penalty = 0.0
        nodal_penalty = 0.0

        # Calculate Moon Paksha Bala ratio for benefic Moon capacity
        sun_lon = d1_grahas.get("Sun", {}).get("longitude", 0.0)
        moon_lon = d1_grahas.get("Moon", {}).get("longitude", 0.0)
        moon_elongation = (moon_lon - sun_lon) % 360.0
        paksha_ratio = 1.0 - abs(moon_elongation - 180.0) / 180.0  # 1.0 = Full, 0.0 = New

        for other_p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
            if other_p == p or other_p not in d1_grahas:
                continue
                
            o_d1 = d1_grahas[other_p]
            o_lon = o_d1.get("longitude", 0.0)
            
            # Aspect Virupas (0 to 60)
            drishti_virupas = aspects.get_graha_drishti(other_p, o_lon, p_lon)
            drishti_fraction = drishti_virupas / 60.0
            
            # Conjunction distance (linear drop within 30°)
            dist = min(abs(o_lon - p_lon), 360.0 - abs(o_lon - p_lon))
            conj_fraction = max(0.0, 1.0 - (dist / 30.0)) if dist < 30.0 else 0.0
            
            influence = max(drishti_fraction, conj_fraction)
            if influence < 0.05:
                continue
                
            inf_type = "Conjunction" if conj_fraction >= drishti_fraction else "Aspect (Drishti)"
            
            # Jupiter: 100% capacity to dissolve flaws & nourish (Phaladeepika 4.11)
            if other_p == "Jupiter":
                pts = round(35.0 * influence * 1.00, 1)
                benefic_rays += pts
                aspect_details.append({
                    "source": "Jupiter",
                    "type": inf_type,
                    "power_pct": round(influence * 100.0, 1),
                    "impact": f"+{pts}% (Guru 100% flaw-destroying & nourishing ray)"
                })
            # Venus: 50% capacity
            elif other_p == "Venus":
                pts = round(35.0 * influence * 0.50, 1)
                benefic_rays += pts
                aspect_details.append({
                    "source": "Venus",
                    "type": inf_type,
                    "power_pct": round(influence * 100.0, 1),
                    "impact": f"+{pts}% (Shukra 50% harmonic ray)"
                })
            # Moon: Waxing / Bright provides gentle nourishment
            elif other_p == "Moon":
                if paksha_ratio >= 0.4:
                    pts = round(35.0 * influence * 0.35 * paksha_ratio, 1)
                    if pts > 0.5:
                        benefic_rays += pts
                        aspect_details.append({
                            "source": "Moon",
                            "type": inf_type,
                            "power_pct": round(influence * 100.0, 1),
                            "impact": f"+{pts}% (Chandra gentle emotional care, {round(paksha_ratio*100)}% bright)"
                        })
            # Mercury: 25% capacity
            elif other_p == "Mercury":
                pts = round(35.0 * influence * 0.25, 1)
                benefic_rays += pts
                aspect_details.append({
                    "source": "Mercury",
                    "type": inf_type,
                    "power_pct": round(influence * 100.0, 1),
                    "impact": f"+{pts}% (Budha 25% intellect & tact ray)"
                })
            # Saturn: -100% malefic pressure
            elif other_p == "Saturn":
                pts = round(35.0 * influence * 1.00, 1)
                malefic_pressure += pts
                aspect_details.append({
                    "source": "Saturn",
                    "type": inf_type,
                    "power_pct": round(influence * 100.0, 1),
                    "impact": f"-{pts}% (Shani contraction & delay pressure)"
                })
            # Mars: -100% malefic pressure
            elif other_p == "Mars":
                pts = round(35.0 * influence * 1.00, 1)
                malefic_pressure += pts
                aspect_details.append({
                    "source": "Mars",
                    "type": inf_type,
                    "power_pct": round(influence * 100.0, 1),
                    "impact": f"-{pts}% (Mangala friction & aggression pressure)"
                })

        # Sun Combustion (within 8° for physical planets)
        if p not in ["Sun", "Rahu", "Ketu"]:
            sun_dist = min(abs(sun_lon - p_lon), 360.0 - abs(sun_lon - p_lon))
            if sun_dist < 8.0:
                comb_pts = round(30.0 * (1.0 - (sun_dist / 8.0)), 1)
                combustion_penalty = comb_pts
                aspect_details.append({
                    "source": "Sun (Surya)",
                    "type": "Combustion (Astangata)",
                    "power_pct": round((1.0 - (sun_dist / 8.0)) * 100.0, 1),
                    "impact": f"-{comb_pts}% (Combust within {sun_dist:.1f}° of Sun)"
                })

        # Nodal Conjunction Affliction (within 12°)
        for node in ["Rahu", "Ketu"]:
            if p not in ["Rahu", "Ketu"] and node in d1_grahas:
                node_lon = d1_grahas[node].get("longitude", 0.0)
                node_dist = min(abs(node_lon - p_lon), 360.0 - abs(node_lon - p_lon))
                if node_dist < 12.0:
                    n_pts = round(15.0 * (1.0 - (node_dist / 12.0)), 1)
                    nodal_penalty += n_pts
                    aspect_details.append({
                        "source": node,
                        "type": "Nodal Eclipse / Shadow",
                        "power_pct": round((1.0 - (node_dist / 12.0)) * 100.0, 1),
                        "impact": f"-{n_pts}% (Afflicted by {node} within {node_dist:.1f}°)"
                    })

        raw_aspect_net = benefic_rays - malefic_pressure - combustion_penalty - nodal_penalty
        clamped_aspect_net = clamp(raw_aspect_net, -40.0, 40.0)

        step3_info = {
            "benefic_rays_pct": round(benefic_rays, 1),
            "malefic_pressure_pct": round(-malefic_pressure, 1),
            "combustion_penalty_pct": round(-combustion_penalty, 1),
            "nodal_penalty_pct": round(-nodal_penalty, 1),
            "net_aspect_pct": round(clamped_aspect_net, 1),
            "details": aspect_details
        }

        # ---------------------------------------------------------------------
        # STEP 4: House Field & Dusthana Reversal Rule
        # ---------------------------------------------------------------------
        house_num = (p_sign_idx - lagna_idx) % 12 + 1
        
        # Check what houses this planet rules in D1
        ruled_houses = []
        for s_idx, s_name in enumerate(ZODIAC_SIGNS):
            if rel.SIGN_LORDS.get(s_name) == p:
                h_num = (s_idx - lagna_idx) % 12 + 1
                ruled_houses.append(h_num)

        house_type = "Ordinary House"
        kendra_rank = None
        house_bonus = 0.0
        viparita_yoga = None
        house_notes = ""

        # Kendra (Angles: 1, 4, 7, 10 - Phaladeepika 4.8)
        if house_num in [1, 4, 7, 10]:
            house_type = "Kendra (Angular Pivot)"
            if house_num == 1:
                kendra_rank = "1st Rank (100% Kendra Leverage - Lagna)"
                house_bonus = 20.0
                house_notes = "1st House Ascendant: Supreme visibility, physical agency, and personal presence."
            elif house_num == 10:
                kendra_rank = "2nd Rank (75% Kendra Leverage - Midheaven / MC)"
                house_bonus = 15.0
                house_notes = "10th House Zenith: Prominent career execution and high public authority."
            elif house_num == 7:
                kendra_rank = "3rd Rank (50% Kendra Leverage - Descendant / DC)"
                house_bonus = 10.0
                house_notes = "7th House Pivot: Strong social, contractual, and partnership engagement."
            elif house_num == 4:
                kendra_rank = "4th Rank (25% Kendra Leverage - Nadir / IC)"
                house_bonus = 5.0
                house_notes = "4th House Base: Solid domestic grounding and emotional stability."
        # Trikona (Trines: 5, 9 - 1st already counted in kendra)
        elif house_num in [5, 9]:
            house_type = "Trikona (Auspicious Trine)"
            house_bonus = 15.0
            house_notes = f"{house_num}th House Trine: Natural flow of past merit (Purva Punya), ethical alignment, and creative grace."
        # Upachaya (Growth Houses: 3, 11 - 10th in kendra, 6th is dusthana)
        elif house_num in [3, 11]:
            house_type = "Upachaya (Growth & Accumulation)"
            house_bonus = 10.0
            house_notes = f"{house_num}th House Upachaya: Steady improvement, courage, and accumulation over time."
        elif house_num == 2:
            house_type = "Sustenance House"
            house_bonus = 5.0
            house_notes = "2nd House: Financial and family resources supporting the planet."
        # Dusthana (6, 8, 12 - The Reversal Rule)
        elif house_num in [6, 8, 12]:
            house_type = "Dusthana (Difficult House)"
            # Check Viparita Raja Yoga first
            if 6 in ruled_houses:
                viparita_yoga = "Harsha Yoga (6th Lord in Dusthana)"
                house_bonus = 20.0
                house_notes = "Harsha Yoga: Defeats rivals effortlessly, strong physical immunity, cheerful in crisis."
            elif 8 in ruled_houses:
                viparita_yoga = "Sarala Yoga (8th Lord in Dusthana)"
                house_bonus = 20.0
                house_notes = "Sarala Yoga: Fearless under crisis, resilient longevity, turning setbacks into decisive victory."
            elif 12 in ruled_houses:
                viparita_yoga = "Vimala Yoga (12th Lord in Dusthana)"
                house_bonus = 20.0
                house_notes = "Vimala Yoga: Frugal, spiritually detached and independent, avoids destructive expenditures."
            else:
                # Normal dusthana rule
                if p in ["Mars", "Saturn", "Sun", "Rahu", "Ketu"]:
                    house_bonus = 10.0
                    house_notes = f"Protective Shield: Natural malefic {p} in {house_num}th house aggressively combats crisis and enemies."
                else:
                    house_bonus = -15.0
                    house_notes = f"Soft natural benefic in {house_num}th house can be overly accommodating; vulnerable to exploitation or loss."

        step4_info = {
            "house_num": house_num,
            "house_type": house_type,
            "kendra_rank": kendra_rank,
            "bonus_pct": round(house_bonus, 1),
            "viparita_yoga": viparita_yoga,
            "ruled_houses": ruled_houses,
            "notes": house_notes
        }

        # ---------------------------------------------------------------------
        # FINAL SCALE SYNTHESIS & AUDIT TRAIL
        # ---------------------------------------------------------------------
        net_score = base_centered + host_bonus + clamped_aspect_net + house_bonus
        clamped_final = clamp(round(net_score, 1), -100.0, 100.0)

        # Expression Mode
        if clamped_final > 30.0:
            expr_mode = "High Expression (Constructive & Flourishing)"
            expr_class = "positive"
        elif clamped_final < -30.0:
            expr_mode = "Low Expression (Stressed & Disruptive)"
            expr_class = "negative"
        else:
            expr_mode = "Mixed Expression (Routine & Balanced)"
            expr_class = "mixed"

        # Raw Strength (Virya / Bala)
        sb_entry = (shadbala_data or {}).get(p, {})
        tot_virupas = sb_entry.get("Total_Virupas", sb_entry.get("total_virupas", 0.0))
        tot_rupas = sb_entry.get("Total_Rupas", sb_entry.get("total_rupas", 0.0))

        # Required virupas according to BPHS / Kala methodology:
        required_virupas_map = {
            "Sun": 390.0,
            "Moon": 360.0,
            "Mars": 300.0,
            "Mercury": 420.0,
            "Jupiter": 390.0,
            "Venus": 330.0,
            "Saturn": 300.0
        }
        req_virupas = required_virupas_map.get(p, 360.0)
        sb_ratio = round(tot_virupas / req_virupas, 2) if req_virupas > 0 and tot_virupas > 0 else 1.0

        # High vs. Low Strength threshold (ratio >= 1.00 or virupas >= required virupas)
        is_high_strength = (sb_ratio >= 1.0) or (tot_virupas >= req_virupas)

        # Inherent Planetary Dignity (Step 1 Shadvarga + Step 2 Host Rescue)
        # Dignity measures the internal mood/character (Avastha/Sthana),
        # which is strictly independent of external aspect pressure (Step 3) or house field (Step 4).
        net_dignity = base_centered + host_bonus
        d1_varga_info = step1_info.get("varga_breakdown", {}).get("D1", {})
        d1_score = d1_varga_info.get("score", 50.0)
        d1_dignity_name = d1_varga_info.get("dignity", "Neutral's Sign")
        avg_dignity = step1_info.get("average_dignity_pct", 50.0)
        weighted_dignity = step1_info.get("weighted_dignity_pct", 50.0)

        # A planet has High Dignity if:
        # 1. Its net dignity (base centered + host rescue) is positive (>= 0.0), OR
        # 2. Its average or weighted Shadvarga dignity is >= 50.0% (neutral or auspicious), OR
        # 3. It is exalted or in own sign in D1 (d1_score >= 80.0).
        is_high_dignity = (net_dignity >= 0.0) or (avg_dignity >= 50.0) or (d1_score >= 80.0)

        # 4-Quadrant Archetype Matrix & Expression Narrative
        if is_high_dignity and is_high_strength:
            arch_title = "Generous King with Armies"
            arch_icon = "🌟"
            if expr_class == "positive":
                arch_desc = "Noble, benevolent intentions AND the brute kinetic muscle to manifest massive, lasting blessings."
            elif expr_class == "mixed":
                arch_desc = "Noble, benevolent core character with strong executive muscle; operates in demanding or complex terrain requiring patient, balanced effort."
            else:
                arch_desc = "Benevolent, high-minded character possessing immense force, but facing severe environmental constraints or trials."
        elif not is_high_dignity and is_high_strength:
            arch_title = "Ruthless Armed Dictator"
            arch_icon = "💣"
            if expr_class == "negative":
                arch_desc = "Bitter, malevolent intentions AND the raw muscle to force real damage into reality (worst-case scenario)."
            elif expr_class == "mixed":
                arch_desc = "Demanding, defensive impulses with high physical drive; tempered into practical functionality by routine reality."
            else:
                arch_desc = "Intense worldly drive and aggressive power, channeled constructively through strong external support."
        elif is_high_dignity and not is_high_strength:
            arch_title = "Sincere Friend with No Money"
            arch_icon = "🕊️"
            if expr_class == "positive":
                arch_desc = "Wonderful heart and pure ethical vision; achieves gentle harmony despite limited physical horsepower."
            elif expr_class == "mixed":
                arch_desc = "Kind, supportive intentions with moderate resources; operates through gentle, steady cooperation."
            else:
                arch_desc = "Has goodwill and high ideals, but feels constrained or fatigued under heavy external demands."
        else:
            arch_title = "Toothless Bully Behind Bars"
            arch_icon = "🪰"
            if expr_class == "negative":
                arch_desc = "Petty, spiteful intentions, but powerless to execute them (easily mitigated nuisance)."
            elif expr_class == "mixed":
                arch_desc = "Vulnerable, easily frustrated disposition; lacks the stamina or authority to cause significant disturbance."
            else:
                arch_desc = "Stressed core disposition, but supported into harmless, quiet productivity by favorable external conditions."

        motional_factors = []
        if p_d1.get("is_retrograde"):
            motional_factors.append("Retrograde (Vakra - Maximum Kinetic Muscle)")
        if p_d1.get("is_combust"):
            motional_factors.append("Combust (Astangata - Stripped of Light)")
        if p == "Moon":
            if paksha_ratio >= 0.6:
                motional_factors.append(f"Bright / Waxing Moon ({round(paksha_ratio*100)}% Full)")
            else:
                motional_factors.append(f"Waning / Dim Moon ({round(paksha_ratio*100)}% Full)")
        if p == "Sun" and house_num == 10:
            motional_factors.append("Supreme Dig Bala (Midday Apex / Noon)")

        strength_info = {
            "total_virupas": round(tot_virupas, 1),
            "shadbala_ratio": round(sb_ratio, 2),
            "strength_level": "High Strength" if is_high_strength else "Low Strength",
            "motional_factors": motional_factors
        }

        # Human-readable calculation trail equation
        eq_parts = [
            {"label": "Base Shadvarga", "value": round(base_centered, 1), "op": ""},
            {"label": "Host Anchor", "value": round(host_bonus, 1), "op": "+" if host_bonus >= 0 else "-"},
            {"label": "Aspect Rays", "value": round(clamped_aspect_net, 1), "op": "+" if clamped_aspect_net >= 0 else "-"},
            {"label": "House Field", "value": round(house_bonus, 1), "op": "+" if house_bonus >= 0 else "-"}
        ]
        
        formula_str = (
            f"Final ({clamped_final:+.1f}%) = Base ({base_centered:+.1f}%) "
            f"{'+' if host_bonus >= 0 else '-'} Host ({abs(host_bonus):.1f}%) "
            f"{'+' if clamped_aspect_net >= 0 else '-'} Aspects ({abs(clamped_aspect_net):.1f}%) "
            f"{'+' if house_bonus >= 0 else '-'} House ({abs(house_bonus):.1f}%)"
        )

        human_readable = (
            f"1. Base Shadvarga dignity across D1, D2, D3, D9, D12, D30 averages {avg_dignity:.1f}% ({step1_info['predominance']}), "
            f"giving a centered base score of {base_centered:+.1f}%.\n"
            f"2. {rescue_notes} [{host_bonus:+.1f}%].\n"
            f"3. Aspect rays from benefics/malefics modify by {clamped_aspect_net:+.1f}%.\n"
            f"4. Placed in House {house_num} ({house_type}), adding {house_bonus:+.1f}%.\n"
            f"➔ Total Net Scale: {clamped_final:+.1f}% ({expr_mode})."
        )

        calc_trail = {
            "formula": formula_str,
            "equation_parts": eq_parts,
            "raw_result": round(net_score, 1),
            "clamped_result": clamped_final,
            "human_readable": human_readable
        }

        planets_result[p] = {
            "planet": p,
            "glyph": PLANET_GLYPHS.get(p, ""),
            "sign": p_sign,
            "longitude": round(p_lon, 2),
            "net_scale_score": clamped_final,
            "expression_mode": expr_mode,
            "expression_class": expr_class,
            "archetype": {
                "title": arch_title,
                "icon": arch_icon,
                "dignity_status": f"High Dignity ({d1_dignity_name})" if is_high_dignity else f"Low Dignity ({d1_dignity_name})",
                "strength_status": "High Strength" if is_high_strength else "Low Strength",
                "description": arch_desc
            },
            "step1_shadvarga": step1_info,
            "step2_host_rescue": step2_info,
            "step3_aspects": step3_info,
            "step4_house_field": step4_info,
            "strength": strength_info,
            "calculation_trail": calc_trail
        }

    # -------------------------------------------------------------------------
    # MASTER ANCHORS OF DESTINY (Phaladeepika 3.11)
    # -------------------------------------------------------------------------
    # 1. Lagna Lord (D1) -> Overall Life Mastery
    lagna_lord = rel.SIGN_LORDS.get(lagna_sign, "Mars")
    lagna_eval = planets_result.get(lagna_lord, {})
    
    # 2. Navamsha Lord (D9) -> Inner Contentment & Dharma
    d9_lagna_sign = vargas_data.get("D9", {}).get("lagna", {}).get("sign", "Aries")
    navamsha_lord = rel.SIGN_LORDS.get(d9_lagna_sign, "Mars")
    navamsha_eval = planets_result.get(navamsha_lord, {})
    
    # 3. Drekkana Lord (D3) -> Physical Courage & Power
    d3_lagna_sign = vargas_data.get("D3", {}).get("lagna", {}).get("sign", "Aries")
    drekkana_lord = rel.SIGN_LORDS.get(d3_lagna_sign, "Mars")
    drekkana_eval = planets_result.get(drekkana_lord, {})

    master_lords = {
        "lagna_lord": {
            "planet": lagna_lord,
            "varga": "D1",
            "rising_sign": lagna_sign,
            "placed_sign": lagna_eval.get("sign", ""),
            "placed_degree": lagna_eval.get("longitude", 0.0),
            "scale_score": lagna_eval.get("net_scale_score", 0.0),
            "expression_mode": lagna_eval.get("expression_mode", "Mixed"),
            "expression_class": lagna_eval.get("expression_class", "mixed"),
            "title": "Lagna Lord (Lagna-Isha)",
            "governs": "Overall Life Mastery, Health & Holistic Fortune (Bhagyavan Prabhu)"
        },
        "navamsha_lord": {
            "planet": navamsha_lord,
            "varga": "D9",
            "rising_sign": d9_lagna_sign,
            "placed_sign": navamsha_eval.get("sign", ""),
            "placed_degree": navamsha_eval.get("longitude", 0.0),
            "scale_score": navamsha_eval.get("net_scale_score", 0.0),
            "expression_mode": navamsha_eval.get("expression_mode", "Mixed"),
            "expression_class": navamsha_eval.get("expression_class", "mixed"),
            "title": "Navamsha Lord (Navamsha-Isha)",
            "governs": "Internal Contentment, Soul-level Dharma & Spiritual Happiness (Sukhi)"
        },
        "drekkana_lord": {
            "planet": drekkana_lord,
            "varga": "D3",
            "rising_sign": d3_lagna_sign,
            "placed_sign": drekkana_eval.get("sign", ""),
            "placed_degree": drekkana_eval.get("longitude", 0.0),
            "scale_score": drekkana_eval.get("net_scale_score", 0.0),
            "expression_mode": drekkana_eval.get("expression_mode", "Mixed"),
            "expression_class": drekkana_eval.get("expression_class", "mixed"),
            "title": "Drekkana Lord (Drekkana-Isha)",
            "governs": "External Force, Bodily Courage, Competitiveness & Worldly Drive (Prabhu)"
        }
    }

    # Chart Predominance Summary
    auspicious_count = sum(1 for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
                          if shadvarga_scores.get(p, {}).get("average_dignity_pct", 50.0) >= 60.0)
    hostile_count = sum(1 for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
                        if shadvarga_scores.get(p, {}).get("average_dignity_pct", 50.0) <= 40.0)

    if auspicious_count >= 4:
        overall_pred = "Shubhamsha Bahule (Predominance of Auspicious Divisions)"
        overall_meaning = "Chiranjeevi & Shrimat: Fortunate longevity, elegance, and enduring prosperity."
    elif hostile_count >= 4:
        overall_pred = "Kruramsha Bahule (Predominance of Strained Divisions)"
        overall_meaning = "Requires reliance on strong dispositors to forge struggle into authority."
    else:
        overall_pred = "Madhyamsha (Balanced Divisional Distribution)"
        overall_meaning = "Dynamic mixture of opportunities and worldly responsibilities."

    return {
        "summary": {
            "title": "Vic DiCara's Planetary Evaluation & Positive-to-Negative Scale",
            "subtitle": "Continuous diagnostic spectrum (-100% to +100%) and 4-Quadrant Archetypes (Phaladeepika Chapters 3 & 4)",
            "master_lords": master_lords,
            "chart_predominance": {
                "auspicious_count": auspicious_count,
                "hostile_count": hostile_count,
                "overall_status": overall_pred,
                "meaning": overall_meaning
            }
        },
        "planets": planets_result
    }
