"""
jyotish/planetary_evaluation/lagna_evaluation.py

Precision diagnostic engine for evaluating the strength, vitality, and yoga-actualization
capacity of the Ascendant (Lagna / Tanū Bhāva).

Epistemological Foundations:
- Ryan Kurczak (The Art and Science of Vedic Astrology Ch. 7 & 9, Lessons 25 & 39):
  The "Invalid in a Palace" & "Million-Dollar Grant" principles: even if a chart promises
  immense wealth or power through yogas, an afflicted Lagna cannot manifest or sustain it.
- Vic DiCara (Foundations of Phaladeepika Lessons 10 & 13):
  The Lagna Lord (Lagneśa / Lagna-isha) dictates holistic life mastery and fortune (Bhagyavān Prabhu).
- Classical Vedic Sourcing:
  Brihat Jataka 1.19: "The Ascendant becomes strong and powerful only if aspected or occupied
  by its lord, Jupiter or Mercury, but not by other planets."
  Phaladeepika 15.9: "Whichever house is occupied by the lord of the Ascendant, the well-being
  of that house is assured."
  BPHS Chapters 11-14, 28 (Bhava Evaluation & Bhava Bala).

5 Classical Diagnostic Pillars:
1. The Captain (Lagneśa Dignity, Shadbala Muscle, and Avasthā Mood)
2. The Field (Lagneśa House Placement: Kendra/Trikona vs. Dusthāna)
3. The Horizon Occupants (Benefics as protective armor vs. Malefics as stress/grit)
4. The Sky-Light (Net Graha Dṛṣṭi on Cusp 1, Jupiter's healing ray, own lord's aspect)
5. The Enclosure (Śubha Kartarī vs. Pāpa Kartarī hemming of House 1)
"""

from typing import Dict, List, Any, Optional
import jyotish.relationships.relationships as rel

ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

SIGN_LORDS = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury", "Cancer": "Moon",
    "Leo": "Sun", "Virgo": "Mercury", "Libra": "Venus", "Scorpio": "Mars",
    "Sagittarius": "Jupiter", "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter"
}

NATURAL_BENEFICS = {"Jupiter", "Venus", "Mercury", "Moon"}
NATURAL_MALEFICS = {"Saturn", "Mars", "Rahu", "Ketu", "Sun"}

def clamp(val: float, min_val: float, max_val: float) -> float:
    return max(min_val, min(max_val, val))

def evaluate_lagna_vitality(
    vargas_data: Dict[str, Any],
    shadbala_data: Optional[Dict[str, Any]] = None,
    advanced_aspects: Optional[Dict[str, Any]] = None,
    varga: str = "D1"
) -> Dict[str, Any]:
    """
    Evaluates the vitality of the Ascendant (Lagna) across 5 classical diagnostic pillars.
    Returns a composite vitality score (1.0 to 10.0), classification tier, archetype,
    and a granular pedagogical audit trail.
    """
    if not vargas_data:
        return {}

    v_data = vargas_data.get(varga) or vargas_data.get("D1", {})
    if not v_data:
        return {}

    lagna_info = v_data.get("lagna", {})
    lagna_sign = lagna_info.get("sign", "Aries")
    lagna_deg = float(lagna_info.get("degree_0_to_30", 0.0))
    lagna_nak = lagna_info.get("nakshatra", "")
    lagna_pada = lagna_info.get("pada", 1)

    l_idx = ZODIAC_SIGNS.index(lagna_sign) if lagna_sign in ZODIAC_SIGNS else 0
    lord = SIGN_LORDS.get(lagna_sign, "Mars")

    grahas = v_data.get("grahas", {})
    lord_data = grahas.get(lord, {})
    lord_sign = lord_data.get("sign", "")
    lord_deg = float(lord_data.get("degree_0_to_30", 0.0))

    # Whole sign house calculation
    def get_w_house(sign_name: str) -> int:
        if sign_name in ZODIAC_SIGNS:
            p_idx = ZODIAC_SIGNS.index(sign_name)
            return (p_idx - l_idx) % 12 + 1
        return 1

    lord_house = get_w_house(lord_sign) if lord_sign else 1

    # Base starting score is 5.0 (Neutral baseline)
    base_score = 5.0
    p1_score = 0.0
    p2_score = 0.0
    p3_score = 0.0
    p4_score = 0.0
    p5_score = 0.0

    p1_notes = []
    p2_notes = []
    p3_notes = []
    p4_notes = []
    p5_notes = []

    # -------------------------------------------------------------------------
    # PILLAR 1: The Lagna Lord (Lagneśa) — The Captain (Max +/- 2.5 pts)
    # -------------------------------------------------------------------------
    lord_dignity = lord_data.get("dignity_breakdown", {}).get("final_dignity", "Neutral's Sign")
    dignity_lower = lord_dignity.lower()

    if "exalt" in dignity_lower:
        p1_score += 1.2
        p1_notes.append("Lord Exalted (+1.2): Sovereign confidence and peak vitality.")
    elif "moolatrikona" in dignity_lower:
        p1_score += 1.0
        p1_notes.append("Lord in Moolatrikona (+1.0): Strong sense of duty and robust health.")
    elif "own" in dignity_lower:
        p1_score += 0.8
        p1_notes.append("Lord in Own Sign (+0.8): Fully self-reliant and comfortable.")
    elif "great friend" in dignity_lower:
        p1_score += 0.5
        p1_notes.append("Lord in Great Friend's Sign (+0.5): Deeply supported environment.")
    elif "friend" in dignity_lower:
        p1_score += 0.25
        p1_notes.append("Lord in Friend's Sign (+0.25): Favorable conditions.")
    elif "neutral" in dignity_lower:
        p1_notes.append("Lord in Neutral Sign (0.0): Balanced baseline.")
    elif "great enemy" in dignity_lower:
        p1_score -= 0.8
        p1_notes.append("Lord in Great Enemy's Sign (-0.8): Severe environmental resistance.")
    elif "enemy" in dignity_lower:
        p1_score -= 0.4
        p1_notes.append("Lord in Enemy's Sign (-0.4): Frictional surroundings.")
    elif "debilitat" in dignity_lower:
        p1_score -= 1.2
        p1_notes.append("Lord Debilitated (-1.2): Low constitutional confidence or self-sabotage.")

    # Sthana Bala (Positional Foundation)
    sb_lord = shadbala_data.get(lord, {}) if shadbala_data else {}
    sthana_pct = float(sb_lord.get("Pct_Required_Sthana", 100.0))
    if sthana_pct >= 110.0:
        p1_score += 0.3
        p1_notes.append(f"Lord Solid Positional Strength (+0.3): Sthana Bala {sthana_pct:.0f}% provides firm anchorage.")

    # Shadbala Muscle & Rank of Lord
    sb_virupas = float(sb_lord.get("Total_Virupas", 0.0))
    sb_pct = float(sb_lord.get("Pct_Required_Total", 100.0))
    sb_rank = int(sb_lord.get("Relative_Rank", 4))

    if sb_pct >= 130.0:
        if sb_rank == 1:
            p1_score += 1.0
            p1_notes.append(f"Lord Shadbala Champion (+1.0): {sb_virupas:.1f} Virūpas ({sb_pct:.0f}%, Rank #1) gives supreme kinetic stamina.")
        elif sb_rank == 2:
            p1_score += 0.8
            p1_notes.append(f"Lord Shadbala Rank #2 (+0.8): {sb_virupas:.1f} Virūpas ({sb_pct:.0f}%) gives major kinetic horsepower.")
        else:
            p1_score += 0.6
            p1_notes.append(f"Lord Shadbala Surplus (+0.6): {sb_virupas:.1f} Virūpas ({sb_pct:.0f}%) gives abundant stamina.")
    elif sb_pct >= 110.0:
        p1_score += 0.4
        p1_notes.append(f"Lord Shadbala Capable (+0.4): {sb_virupas:.1f} Virūpas ({sb_pct:.0f}%, Rank #{sb_rank}) provides healthy strength.")
    elif sb_pct >= 100.0:
        p1_score += 0.2
        p1_notes.append(f"Lord Shadbala Adequate (+0.2): {sb_virupas:.1f} Virūpas ({sb_pct:.0f}%, Rank #{sb_rank}) meets minimum requirements.")
    elif sb_pct >= 85.0:
        p1_score -= 0.4
        p1_notes.append(f"Lord Shadbala Mild Deficit (-0.4): {sb_virupas:.1f} Virūpas ({sb_pct:.0f}%, Rank #{sb_rank}) requires conscious energy conservation.")
    elif sb_virupas > 0:
        if sb_rank == 7:
            p1_score -= 0.9
            p1_notes.append(f"Lord Shadbala Severe Deficit (-0.9): {sb_virupas:.1f} Virūpas ({sb_pct:.0f}%, Rank #7 of 7) gives an underpowered physical engine prone to fatigue.")
        elif sb_rank == 6:
            p1_score -= 0.7
            p1_notes.append(f"Lord Shadbala Deficit (-0.7): {sb_virupas:.1f} Virūpas ({sb_pct:.0f}%, Rank #{sb_rank}) indicates low physical stamina.")
        else:
            p1_score -= 0.5
            p1_notes.append(f"Lord Shadbala Deficit (-0.5): {sb_virupas:.1f} Virūpas ({sb_pct:.0f}%).")

    # Lajjitādi Avasthā (Feeling States of the Captain)
    lord_avasthas = lord_data.get("avasthas", {})
    lajjitadi_list = lord_avasthas.get("lajjitadi", [])
    is_starved = False
    starved_saturn = False
    is_delighted = False
    is_proud = False
    is_ashamed = False
    is_agitated = False

    for item in lajjitadi_list:
        st = item.get("state", "").lower()
        cond = item.get("condition", "").lower()
        if "kshudhita" in st or "starved" in st:
            is_starved = True
            if "saturn" in cond:
                starved_saturn = True
        if "mudita" in st or "delighted" in st:
            is_delighted = True
        if "garvita" in st or "proud" in st:
            is_proud = True
        if "lajjita" in st or "ashamed" in st:
            is_ashamed = True
        if "kshobhita" in st or "agitated" in st:
            is_agitated = True

    if is_proud:
        p1_score += 0.6
        p1_notes.append("Lord Proud (Garvita) (+0.6): Radiant self-respect and inspiring initiative.")
    if is_delighted:
        p1_score += 0.4
        p1_notes.append("Lord Delighted (Mudita) (+0.4): Receptive, encouraged, and cheered on by friendly allies.")
    if is_starved:
        if starved_saturn:
            p1_score -= 0.8
            p1_notes.append("Lord Starved by Saturn (Kshudhita) (-0.8): Painful inner critic, self-doubt, and persistent feeling of limitation or delay.")
        else:
            p1_score -= 0.5
            p1_notes.append("Lord Starved (Kshudhita) (-0.5): Starved of essential emotional resources by enemies.")
    if is_ashamed:
        p1_score -= 0.8
        p1_notes.append("Lord Ashamed (Lajjita) (-0.8): Shamed in action, fearful of judgment or unworthiness.")
    if is_agitated:
        p1_score -= 0.5
        p1_notes.append("Lord Agitated (Kshobhita) (-0.5): Internal agitation and friction from cruel planetary influences.")

    # Deeptādi / Direct Conjunction with Malefics
    deeptadi = lord_avasthas.get("deeptadi", {})
    d_state = deeptadi.get("state", "").lower()
    d_cond = deeptadi.get("condition", "")
    if "vikala" in d_state or "mutilated" in d_state:
        if "saturn" in d_cond.lower():
            p1_score -= 0.4
            p1_notes.append(f"Lord Conjoined Saturn (Deeptādi Vikala) (-0.4): Direct contact with the Great Taskmaster imposes heavy duties, coldness, and sober pacing.")
        elif "rahu" in d_cond.lower() or "ketu" in d_cond.lower():
            p1_score -= 0.2
            p1_notes.append(f"Lord with Nodal Influence ({d_cond}) (-0.2): Restless intensity or eccentric self-projection.")
        else:
            p1_score -= 0.3
            p1_notes.append(f"Lord Conjoined Malefic ({d_cond}) (-0.3).")

    # Motion & Combustion
    is_retro = bool(lord_data.get("is_retrograde", False))
    is_combust = bool(lord_data.get("is_combust", False))
    sun_dist = float(lord_data.get("sun_distance", 99.0)) if lord_data.get("sun_distance") is not None else 99.0

    if is_retro and lord in ("Mars", "Mercury", "Jupiter", "Venus", "Saturn"):
        p1_score += 0.3
        p1_notes.append("Lord Retrograde (+0.3): High motional power (Cheṣṭa Bala) and unconventional resilience.")

    if is_combust:
        if sun_dist < 3.0:
            p1_score -= 0.6
            p1_notes.append(f"Lord Deeply Combust (-0.6): Within {sun_dist:.1f}° of Sun; ego exhausts vitality.")
        else:
            p1_score -= 0.3
            p1_notes.append(f"Lord Mildly Combust (-0.3): Within {sun_dist:.1f}° of Sun; internalizes self-confidence.")

    # -------------------------------------------------------------------------
    # PILLAR 2: The Captain's Field Placement & Directional Leverage (Max +/- 2.0 pts)
    # -------------------------------------------------------------------------
    is_own_sign_in_house = "own" in dignity_lower

    if lord_house == 1:
        p2_score += 1.5
        p2_notes.append("Lord in House 1 (+1.5): Supreme self-anchoring, autonomy, and vital independence.")
    elif lord_house == 10:
        p2_score += 1.2
        p2_notes.append("Lord in House 10 (Karma Bhāva) (+1.2): Zenith of public action, executive honors, and social visibility.")
    elif lord_house == 4:
        if lord == "Sun":
            p2_score += 0.4
            p2_notes.append("Sun in House 4 (Sukha / Midnight Nadir) (+0.4): Deep interior peace and meditative sanctuary; vital energy is introspective rather than outward.")
        else:
            p2_score += 0.8
            p2_notes.append("Lord in Kendra Bandhu (H4) (+0.8): Deep emotional security, domestic sanctuary, and supportive foundation.")
    elif lord_house == 7:
        p2_score += 0.7
        p2_notes.append("Lord in Kendra Yuvati (H7) (+0.7): Societal engagement and relationship mirror.")
    elif lord_house == 11:
        p2_score += 1.0
        p2_notes.append("Lord in House 11 (Lābha / Mega-gains) (+1.0): Goal actualization, massive worldly returns, and expansive network power.")
    elif lord_house == 9:
        p2_score += 1.2
        p2_notes.append("Lord in House 9 (Dharma / Bhāgya) (+1.2): Divine grace, higher ethics, and natural fortune.")
    elif lord_house == 5:
        p2_score += 1.0
        p2_notes.append("Lord in House 5 (Buddhi / Putra) (+1.0): Creative intelligence and past-life merit.")
    elif lord_house == 3:
        p2_score += 0.4
        p2_notes.append("Lord in House 3 (Sahaja / Upachaya) (+0.4): Courage and progressive improvement through grit.")
    elif lord_house == 6:
        if is_own_sign_in_house:
            p2_notes.append("Lord in House 6 in Own Sign (0.0): Conquers enemies and debts without destroying health.")
        else:
            p2_score -= 0.8
            p2_notes.append("Lord in House 6 (Dusthāna) (-0.8): Vitality drawn into daily struggles, conflict, or health resistance.")
    elif lord_house == 8:
        if is_own_sign_in_house:
            p2_notes.append("Lord in House 8 in Own Sign (0.0): Deep longevity and esoteric resilience.")
        else:
            p2_score -= 1.2
            p2_notes.append("Lord in House 8 (Dusthāna) (-1.2): Vulnerability to sudden crises, chronic fatigue, or radical upheavals.")
    elif lord_house == 12:
        if is_own_sign_in_house:
            p2_notes.append("Lord in House 12 in Own Sign (0.0): Peaceful spiritual detachment.")
        else:
            p2_score -= 0.8
            p2_notes.append("Lord in House 12 (Dusthāna) (-0.8): Vitality dissipated into solitude, expenses, or detachment from worldly competition.")

    # Digbala (Directional Strength) Leverage of Lord
    sb_dig_pct = float(sb_lord.get("Pct_Required_Dig", 100.0))
    if sb_dig_pct >= 120.0:
        p2_score += 0.3
        p2_notes.append(f"Lord High Directional Strength (+0.3): Digbala {sb_dig_pct:.0f}% aligns executive agency with its ideal quadrant.")
    elif sb_dig_pct < 35.0:
        p2_score -= 0.3
        p2_notes.append(f"Lord Directional Deficit (-0.3): Digbala {sb_dig_pct:.0f}% places the captain away from its natural compass point.")

    # -------------------------------------------------------------------------
    # PILLAR 3: Occupants of the 1st House (Bhavastha Grahas) (Max +/- 1.8 pts)
    # -------------------------------------------------------------------------
    h1_occupants = [p for p in grahas if get_w_house(grahas[p].get("sign", "")) == 1]
    
    if not h1_occupants:
        p3_notes.append("No planets in House 1 (0.0): Clean, unencumbered horizon reflecting pure rising sign.")
    else:
        for p in h1_occupants:
            p_dig = grahas[p].get("dignity_breakdown", {}).get("final_dignity", "")
            p_dig_low = p_dig.lower()
            
            if p == "Jupiter":
                p3_score += 1.0
                p3_notes.append("Jupiter in House 1 (+1.0): Directional strength (Digbala); bestows noble wisdom, broad optimism, and cellular immunity.")
            elif p == "Venus":
                p3_score += 0.7
                p3_notes.append("Venus in House 1 (+0.7): Aesthetic grace, bodily contentment, charisma, and peaceful diplomacy.")
            elif p == "Mercury":
                p3_score += 0.6
                p3_notes.append("Mercury in House 1 (+0.6): Directional strength (Digbala); rapid cognitive processing and youthful adaptability.")
            elif p == "Moon":
                p3_score += 0.6
                p3_notes.append("Moon in House 1 (+0.6): Emotional magnetism, popularity, and deep sensitivity to surroundings.")
            elif p == "Mars":
                if "own" in p_dig_low or "exalt" in p_dig_low or lagna_sign in ("Leo", "Cancer"):
                    p3_score += 0.8
                    p3_notes.append(f"Mars in House 1 (Yogakāraka / Dignified) (+0.8): Gladiator willpower, fearless leadership, and impervious physical drive.")
                else:
                    p3_score -= 0.5
                    p3_notes.append("Mars in House 1 (-0.5): Excess bodily heat (Pitta), rash impulsivity, and proneness to cuts, fevers, or injuries.")
            elif p == "Saturn":
                if "own" in p_dig_low or "exalt" in p_dig_low:
                    p3_score += 0.6
                    p3_notes.append("Saturn in House 1 (Śaśa Mahāpuruṣa) (+0.6): Enduring iron discipline, profound realism, and grounded stamina.")
                else:
                    p3_score -= 0.6
                    p3_notes.append("Saturn in House 1 (-0.6): Bodily coldness, stiffness, Vata stress, and aloof or morose projection.")
            elif p == "Sun":
                if p == lord:
                    p3_notes.append("Sun in House 1 (Lagna Lord) (evaluated in Pillar 1 & 2): Radiates sovereign solar authority.")
                else:
                    p3_score -= 0.3
                    p3_notes.append("Sun in House 1 (-0.3): Intense heat and egoic friction in the personal field.")
            elif p == "Rahu":
                p3_score -= 0.5
                p3_notes.append("Rahu in House 1 (-0.5): Identity distortion, restless ambition, and unconventional nervous tension.")
            elif p == "Ketu":
                p3_score -= 0.5
                p3_notes.append("Ketu in House 1 (-0.5): Dissociation from physical needs, ascetic detachment, and enigmatic self-expression.")

    # -------------------------------------------------------------------------
    # PILLAR 4: Sky-Light & The Karaka Factor (Max +/- 1.8 pts)
    # -------------------------------------------------------------------------
    cusp1_net = 0.0
    cusp1_plus = 0.0
    cusp1_minus = 0.0
    has_jupiter_drishti = False
    has_lord_drishti = False

    if advanced_aspects and "totals" in advanced_aspects and "cusps" in advanced_aspects["totals"]:
        cusp_totals = advanced_aspects["totals"]["cusps"]
        c1 = cusp_totals.get(1) or cusp_totals.get("1") or {}
        cusp1_net = float(c1.get("net", 0.0))
        cusp1_plus = float(c1.get("plus", 0.0))
        cusp1_minus = float(c1.get("minus", 0.0))

    # Detailed aspects on cusp 1 from individual planets
    if advanced_aspects and "cusps" in advanced_aspects:
        c1_indiv = advanced_aspects["cusps"].get(1) or advanced_aspects["cusps"].get("1") or {}
        if "Jupiter" in c1_indiv:
            j_net = float(c1_indiv["Jupiter"].get("net", c1_indiv["Jupiter"].get("plus", 0.0)))
            if j_net > 15.0:
                has_jupiter_drishti = True
        if lord in c1_indiv:
            l_net = float(c1_indiv[lord].get("net", c1_indiv[lord].get("plus", 0.0)))
            if l_net > 15.0:
                has_lord_drishti = True

    if cusp1_net >= 40.0:
        p4_score += 0.8
        p4_notes.append(f"Abundant Net Subha Dṛṣṭi (+0.8): +{cusp1_net:.1f} Virūpas of positive sky-light bathe the rising degree.")
    elif cusp1_net >= 15.0:
        p4_score += 0.4
        p4_notes.append(f"Moderate Net Subha Dṛṣṭi (+0.4): +{cusp1_net:.1f} Virūpas of supportive rays.")
    elif cusp1_net <= -40.0:
        p4_score -= 0.8
        p4_notes.append(f"Heavy Net Pāpa Dṛṣṭi (-0.8): {cusp1_net:.1f} Virūpas of malefic pressure fall on the horizon.")
    elif cusp1_net <= -15.0:
        p4_score -= 0.4
        p4_notes.append(f"Moderate Net Pāpa Dṛṣṭi (-0.4): {cusp1_net:.1f} Virūpas of friction on the horizon.")
    else:
        p4_notes.append(f"Balanced Horizon Light (0.0): Net {cusp1_net:+.1f} Virūpas.")

    if has_jupiter_drishti:
        p4_score += 0.6
        p4_notes.append("Jupiter's Protective Gaze (+0.6): Classical sovereign healer aspecting the Ascendant directly (Brihat Jataka 1.19).")

    if has_lord_drishti:
        p4_score += 0.6
        p4_notes.append(f"Lagna Lord's Aspect (+0.6): {lord} gazes directly upon its own rising sign, unconditionally shielding life vitality.")

    # The Karaka Factor: The Sun as Naisargika Karaka of House 1 / Vitality (Vic DiCara 3-Point Rule)
    sun_data = grahas.get("Sun", {})
    sb_sun = shadbala_data.get("Sun", {}) if shadbala_data else {}
    sun_pct = float(sb_sun.get("Pct_Required_Total", 100.0))
    sun_rank = int(sb_sun.get("Relative_Rank", 4))
    sun_laj = sun_data.get("avasthas", {}).get("lajjitadi", [])
    sun_starved_saturn = any("starved" in x.get("state", "").lower() and "saturn" in x.get("condition", "").lower() for x in sun_laj)
    sun_starved = any("starved" in x.get("state", "").lower() or "kshudhita" in x.get("state", "").lower() for x in sun_laj)

    if lord == "Sun":
        # Leo Lagna: Lord IS the Karaka of Vitality
        if sun_starved_saturn and sun_pct < 85.0:
            p4_score -= 0.5
            p4_notes.append(f"Double-Affliction to Lord & Karaka Sun (-0.5): For Leo Lagna, Sun is both Captain and Vitality Karaka. Starvation by Saturn and low Shadbala ({sun_pct:.0f}%, Rank #{sun_rank}) compound constitutional fatigue.")
        elif sun_pct >= 130.0 and not sun_starved:
            p4_score += 0.5
            p4_notes.append(f"Double-Solar Radiance (+0.5): For Leo Lagna, Sun is both Lord and Vitality Karaka. Peak Shadbala ({sun_pct:.0f}%, Rank #1) delivers double vitality and royal charisma.")
    else:
        # Other Lagnas
        if sun_starved_saturn or sun_pct < 85.0:
            p4_score -= 0.3
            p4_notes.append(f"Afflicted Vitality Karaka (Sun) (-0.3): Universal life force suffers from fatigue ({sun_pct:.0f}%) or starvation.")
        elif sun_pct >= 115.0 and not sun_starved:
            p4_score += 0.3
            p4_notes.append(f"Healthy Vitality Karaka (Sun) (+0.3): Universal life force is strong ({sun_pct:.0f}%), supporting bodily health.")

    # -------------------------------------------------------------------------
    # PILLAR 5: Environmental Enclosure (Kartarī Yoga) (Max +/- 1.0 pt)
    # -------------------------------------------------------------------------
    h2_occupants = [p for p in grahas if get_w_house(grahas[p].get("sign", "")) == 2 and p not in ("Rahu", "Ketu")]
    h12_occupants = [p for p in grahas if get_w_house(grahas[p].get("sign", "")) == 12 and p not in ("Rahu", "Ketu")]

    h2_benefics = [p for p in h2_occupants if p in NATURAL_BENEFICS]
    h2_malefics = [p for p in h2_occupants if p in NATURAL_MALEFICS]
    h12_benefics = [p for p in h12_occupants if p in NATURAL_BENEFICS]
    h12_malefics = [p for p in h12_occupants if p in NATURAL_MALEFICS]

    kartari_type = "Neutral"
    if h2_benefics and h12_benefics and not h2_malefics and not h12_malefics:
        p5_score += 0.8
        kartari_type = "Śubha Kartarī"
        p5_notes.append(f"Śubha Kartarī Yoga (+0.8): House 1 is flanked by benefics in 2nd ({h2_benefics}) and 12th ({h12_benefics}), protecting the native like a golden cocoon.")
    elif h2_malefics and h12_malefics and not h2_benefics and not h12_benefics:
        p5_score -= 0.8
        kartari_type = "Pāpa Kartarī"
        p5_notes.append(f"Pāpa Kartarī Yoga (-0.8): House 1 is besieged by malefics in 2nd ({h2_malefics}) and 12th ({h12_malefics}), creating chronic background tension.")
    else:
        p5_notes.append("Unencumbered Flanks (0.0): No extreme hemming around the Ascendant.")

    # -------------------------------------------------------------------------
    # SYNTHESIS: Final Composite Score & Classification
    # -------------------------------------------------------------------------
    raw_score = base_score + p1_score + p2_score + p3_score + p4_score + p5_score
    vitality_score = round(clamp(raw_score, 1.0, 10.0), 1)

    if vitality_score >= 8.8:
        tier = "Sovereign Citadel"
        v_class = "robust"
        archetype = "The Invincible Sovereign"
        verdict = "Supreme constitutional vitality and iron executive agency; chart yogas manifest with maximum real-world force."
    elif vitality_score >= 7.3:
        tier = "Robust Horizon"
        v_class = "robust"
        archetype = "The Resilient Architect"
        verdict = "High resilience, healthy self-worth, and decisive drive; overcomes obstacles and readily activates auspicious yogas."
    elif vitality_score >= 5.5:
        tier = "Capable Vessel"
        v_class = "capable"
        archetype = "The Steady Navigator"
        verdict = "Sound, capable engine; achieves solid worldly success and actualizes yogas through continuous, deliberate effort."
    elif vitality_score >= 4.0:
        tier = "Strained Horizon"
        v_class = "strained"
        archetype = "The Contemplative Seeker"
        verdict = "Vitality is sensitive or internalized; worldly yogas face delays or friction, requiring conscious pacing and health care."
    else:
        tier = "Vulnerable Horizon"
        v_class = "fragile"
        archetype = "The Invalid in a Palace"
        verdict = "Compromised life engine; yogas struggle to manifest externally without significant health discipline, rest, or remedial support."

    return {
        "varga": varga,
        "lagna_sign": lagna_sign,
        "lagna_degree": lagna_deg,
        "nakshatra": lagna_nak,
        "pada": lagna_pada,
        "lord": {
            "name": lord,
            "sign": lord_sign,
            "degree": lord_deg,
            "house": lord_house,
            "dignity": lord_dignity,
            "shadbala_virupas": sb_virupas,
            "shadbala_pct": sb_pct,
            "shadbala_rank": sb_rank,
            "is_retrograde": is_retro,
            "is_combust": is_combust
        },
        "occupants": h1_occupants,
        "aspects": {
            "net_virupas": cusp1_net,
            "plus_virupas": cusp1_plus,
            "minus_virupas": cusp1_minus,
            "has_jupiter_drishti": has_jupiter_drishti,
            "has_lord_drishti": has_lord_drishti
        },
        "kartari": {
            "type": kartari_type,
            "h2_occupants": h2_occupants,
            "h12_occupants": h12_occupants
        },
        "vitality_score": vitality_score,
        "vitality_tier": tier,
        "vitality_class": v_class,
        "archetype": archetype,
        "verdict": verdict,
        "pillar_scores": {
            "pillar_1_captain": round(p1_score, 2),
            "pillar_2_field": round(p2_score, 2),
            "pillar_3_occupants": round(p3_score, 2),
            "pillar_4_skylight": round(p4_score, 2),
            "pillar_5_enclosure": round(p5_score, 2),
            "base_score": base_score
        },
        "audit_trail": {
            "p1_captain": p1_notes,
            "p2_field": p2_notes,
            "p3_occupants": p3_notes,
            "p4_skylight": p4_notes,
            "p5_enclosure": p5_notes
        }
    }
