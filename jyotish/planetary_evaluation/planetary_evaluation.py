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
from jyotish.planetary_evaluation.lagna_evaluation import evaluate_lagna_vitality

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

# Dignity Score mapping based on Ryan Kurczak (The Art and Science of Vedic Astrology Vol 1 Ch 6)
# and classical Panchadha Maitri 5-fold compound relationships:
# Exalted: 100%, Moolatrikona: 87.5%, Own Positive: 75%, Own Negative: 62.5%,
# Great Friend: 60%, Friend: 50%, Neutral: 37.5%, Enemy: 25%, Great Enemy: 20%, Debilitated: 12.5%
DIGNITY_SCORE_MAP: Dict[str, float] = {
    "Exalted": 100.0,
    "Exaltation": 100.0,
    "Paramoccha": 100.0,
    "Uccha": 100.0,
    "Moolatrikona": 87.5,
    "Own Positive Sign": 75.0,
    "Own Negative Sign": 62.5,
    "Own Sign": 68.75,  # Balanced midpoint if gender is unspecified
    "Own House": 68.75,
    "Sva-kshetra": 68.75,
    "Great Friend's Sign": 60.0,
    "Great Friend": 60.0,
    "Adhi-mitra": 60.0,
    "Friend's Sign": 50.0,
    "Friend": 50.0,
    "Mitra": 50.0,
    "Neutral's Sign": 37.5,
    "Neutral": 37.5,
    "Sama": 37.5,
    "Enemy's Sign": 25.0,
    "Enemy": 25.0,
    "Shatru": 25.0,
    "Great Enemy's Sign": 20.0,
    "Great Enemy": 20.0,
    "Adhi-shatru": 20.0,
    "Debilitated": 12.5,
    "Debilitation": 12.5,
    "Neecha": 12.5
}

ODD_SIGNS = {"Aries", "Gemini", "Leo", "Libra", "Sagittarius", "Aquarius"}
EVEN_SIGNS = {"Taurus", "Cancer", "Virgo", "Scorpio", "Capricorn", "Pisces"}

MOOLATRIKONA_RANGES = {
    "Sun": ("Leo", 0.0, 20.0),
    "Moon": ("Taurus", 3.0, 30.0),
    "Mars": ("Aries", 0.0, 12.0),
    "Mercury": ("Virgo", 15.0, 20.0),
    "Jupiter": ("Sagittarius", 0.0, 10.0),
    "Venus": ("Libra", 0.0, 15.0),
    "Saturn": ("Aquarius", 0.0, 20.0),
}

TRUE_DEBILITATION_MAP = {
    "Sun": "Libra",
    "Moon": "Scorpio",
    "Mars": "Cancer",
    "Mercury": "Pisces",
    "Jupiter": "Capricorn",
    "Venus": "Virgo",
    "Saturn": "Aries",
    "Rahu": "Scorpio",
    "Ketu": "Taurus"
}

# Signs where nodes gain special strength (Phaladeepika 4.5 & Lesson 19)
RAHU_STRONG_SIGNS = {"Aries", "Taurus", "Cancer", "Scorpio", "Aquarius"}
KETU_STRONG_SIGNS = {"Taurus", "Gemini", "Virgo", "Sagittarius", "Pisces"}

SHADVARGA_LIST = ["D1", "D2", "D3", "D9", "D12", "D30"]

def get_dignity_score(
    dignity_str: str,
    planet: Optional[str] = None,
    sign: Optional[str] = None,
    degree: float = 0.0
) -> float:
    """
    Normalizes dignity string and returns its 0-100% score per Ryan Kurczak's 12.5% step scale
    and classical Panchadha Maitri. Dynamically handles own positive/negative signs and moolatrikona.
    """
    if not dignity_str:
        return 37.5
    cleaned = dignity_str.strip()
    c_low = cleaned.lower()

    if "exalt" in c_low:
        return 100.0
    if "moola" in c_low:
        if planet and degree is not None and planet in MOOLATRIKONA_RANGES:
            mt_sign, min_d, max_d = MOOLATRIKONA_RANGES[planet]
            if sign and sign == mt_sign and (degree < min_d or degree > max_d):
                return 75.0 if sign in ODD_SIGNS else 62.5
        return 87.5
    if "own" in c_low or "svastha" in c_low or "house" in c_low:
        if sign and sign in ODD_SIGNS:
            return 75.0
        elif sign and sign in EVEN_SIGNS:
            return 62.5
        return 68.75
    if "great friend" in c_low or "adhi-mitra" in c_low:
        return 60.0
    if "friend" in c_low and "great" not in c_low:
        return 50.0
    if "neutral" in c_low or "sama" in c_low:
        return 37.5
    if "great enemy" in c_low or "adhi-shatru" in c_low:
        return 20.0
    if "enemy" in c_low:
        return 25.0
    if "debilit" in c_low or "neecha" in c_low:
        return 12.5

    if cleaned in DIGNITY_SCORE_MAP:
        return DIGNITY_SCORE_MAP[cleaned]
    for key, val in DIGNITY_SCORE_MAP.items():
        if key.lower() == c_low:
            return val

    return 37.5


def clamp(val: float, min_val: float, max_val: float) -> float:
    return max(min_val, min(max_val, val))


def calculate_baladi_avastha(sign: str, degree_in_sign: float) -> Dict[str, Any]:
    """
    Calculates Baladi Avastha (Phaladeepika 3.10) with odd/even sign reversal.
    Odd signs (Aries, Gemini, Leo, Libra, Sagittarius, Aquarius):
      0-6°: Bala (Infant), 6-12°: Kumara (Child), 12-18°: Taruna (Prime Adult),
      18-24°: Pravaya (Aging/Elder), 24-30°: Mrita (Dead/Incapacitated).
    Even signs (Taurus, Cancer, Virgo, Scorpio, Capricorn, Pisces):
      Inverts from death to birth:
      0-6°: Mrita, 6-12°: Pravaya, 12-18°: Taruna, 18-24°: Kumara, 24-30°: Bala.
    """
    odd_signs = {"Aries", "Gemini", "Leo", "Libra", "Sagittarius", "Aquarius"}
    is_odd = sign in odd_signs
    deg = max(0.0, min(29.9999, float(degree_in_sign)))
    segment = int(deg // 6.0)  # 0 to 4
    segment = max(0, min(4, segment))

    if is_odd:
        states = ["Bala", "Kumara", "Taruna", "Pravaya", "Mrita"]
        efficiency = [0.50, 0.75, 1.00, 0.50, 0.25]
        sanskrit_terms = [
            "Vadhishnu (Needy/Student)",
            "Sukhi (Carefree/Playful)",
            "Nripa (King/Master)",
            "Gada (Fatigued/Mace)",
            "Mrita (Incapacitated)"
        ]
        degree_ranges = ["0°00' - 5°59'", "6°00' - 11°59'", "12°00' - 17°59'", "18°00' - 23°59'", "24°00' - 29°59'"]
    else:
        states = ["Mrita", "Pravaya", "Taruna", "Kumara", "Bala"]
        efficiency = [0.25, 0.50, 1.00, 0.75, 0.50]
        sanskrit_terms = [
            "Mrita (Incapacitated)",
            "Gada (Fatigued/Mace)",
            "Nripa (King/Master)",
            "Sukhi (Carefree/Playful)",
            "Vadhishnu (Needy/Student)"
        ]
        degree_ranges = ["0°00' - 5°59'", "6°00' - 11°59'", "12°00' - 17°59'", "18°00' - 23°59'", "24°00' - 29°59'"]

    state_name = states[segment]
    return {
        "state": state_name,
        "segment": segment,
        "degree_range": degree_ranges[segment],
        "efficiency_factor": efficiency[segment],
        "efficiency_pct": int(efficiency[segment] * 100),
        "sanskrit_term": sanskrit_terms[segment],
        "is_odd_sign": is_odd
    }


def classify_graha_archetype(
    effective_dignity: Optional[float] = None,
    effective_shadbala: Optional[float] = None,
    is_rescued: bool = False,
    is_node: bool = False,
    dignity_name: str = "",
    *,
    dignity_pct: Optional[float] = None,
    shadbala_pct: Optional[float] = None,
    is_neecha_bhanga: Optional[bool] = None
) -> Dict[str, Any]:
    """
    Classifies a planet into the refined 9-Tier Behavioral Archetype Spectrum (+ Transmuted Hero):
    Cross-references Moral Intent / Quality (Dignity) with Kinetic Power / Stamina (Shadbala).

    1. High Dignity + High Muscle: The Generous King (Sovereign Benefactor)
    2. High Dignity + Balanced Muscle: The Noble Guardian (Constructive Ally)
    3. High Dignity + Low Muscle: The Sincere Friend (Noble Intent / Low Muscle)
    4. Neutral Dignity + High Muscle: The Pragmatic Executive (Tireless Champion)
    5. Neutral Dignity + Balanced Muscle: The Dutiful Realist (Steady Craftsman)
    6. Neutral Dignity + Low Muscle: The Modest Citizen (Quiet Baseline)
    7. Low Dignity + High Muscle: The Armed Dictator (Severe Hazard)
    8. Low Dignity + Balanced Muscle: The Embattled Striver (Strained Fighter)
    9. Low Dignity + Low Muscle: The Toothless Bully (Harmless Adversary)
    10. True Debilitation + Exalted/Fortified Host: The Transmuted Hero (Alchemical Raja Yoga)
    """
    if effective_dignity is None and dignity_pct is not None:
        effective_dignity = dignity_pct
    if effective_shadbala is None and shadbala_pct is not None:
        effective_shadbala = shadbala_pct
    if is_neecha_bhanga is not None:
        is_rescued = is_neecha_bhanga
    effective_dignity = 37.5 if effective_dignity is None else effective_dignity
    effective_shadbala = 100.0 if effective_shadbala is None else effective_shadbala
    if is_rescued:
        return {
            "archetype": "The Transmuted Hero",
            "badge": "✨ Transmuted Hero",
            "tier": "Alchemical Raja Yoga",
            "description": "Initial vulnerability transformed by a noble host into profound resilience and hard-won wisdom.",
            "color": "#7c3aed",
            "bg": "#f3e8ff",
            "is_high_dignity": True,
            "is_high_strength": (effective_shadbala >= 95.0)
        }

    is_high_dig = effective_dignity >= 55.0
    is_neutral_dig = 35.0 <= effective_dignity < 55.0
    is_low_dig = effective_dignity < 35.0

    is_high_musc = effective_shadbala >= 110.0
    is_bal_musc = 88.0 <= effective_shadbala < 110.0
    is_low_musc = effective_shadbala < 88.0

    if is_high_dig:
        if is_high_musc:
            archetype = "The Generous King"
            badge = "🌟 Generous King"
            tier = "Sovereign Benefactor"
            desc = "High moral character equipped with immense executive power. Grants durable, honorable triumphs."
            color = "#15803d"
            bg = "#dcfce7"
        elif is_bal_musc:
            archetype = "The Noble Guardian"
            badge = "🛡️ Noble Guardian"
            tier = "Constructive Ally"
            desc = "Sincere ethical intentions with steady real-world capability. Provides consistent, harmonious progress."
            color = "#0284c7"
            bg = "#e0f2fe"
        else:
            archetype = "The Sincere Friend"
            badge = "🤝 Sincere Friend"
            tier = "Noble Intent / Low Muscle"
            desc = "Deep goodwill and spiritual integrity, but lacks physical muscle. Provides peace, but limited worldly output."
            color = "#4f46e5"
            bg = "#eef2ff"
    elif is_neutral_dig:
        if is_high_musc:
            archetype = "The Pragmatic Executive"
            badge = "⚒️ Pragmatic Executive"
            tier = "Tireless Champion"
            desc = "Unpretentious, highly productive powerhouse. Fulfills duties with tireless endurance and practical mastery."
            color = "#0f766e"
            bg = "#ccfbf1"
        elif is_bal_musc:
            archetype = "The Dutiful Realist"
            badge = "⚖️ Dutiful Realist"
            tier = "Steady Craftsman"
            desc = "Pragmatic and balanced; operates without drama or malice. Delivers solid, reliable everyday results."
            color = "#475569"
            bg = "#f1f5f9"
        else:
            archetype = "The Modest Citizen"
            badge = "🌾 Modest Citizen"
            tier = "Quiet Baseline"
            desc = "Low-profile and harmless. Operates within familiar routines without seeking grand worldly conquest."
            color = "#a16207"
            bg = "#fef9c3"
    else:
        if is_high_musc:
            archetype = "The Armed Dictator"
            badge = "⚔️ Armed Dictator"
            tier = "Severe Hazard"
            desc = "Corrupt or rash intent armed with devastating kinetic force. Demands extreme vigilance and conscious discipline."
            color = "#b91c1c"
            bg = "#fee2e2"
        elif is_bal_musc:
            archetype = "The Embattled Striver"
            badge = "🌪️ Embattled Striver"
            tier = "Strained Fighter"
            desc = "Under heavy friction and internal conflict. Requires hard labor and constant caution to avert missteps."
            color = "#c2410c"
            bg = "#ffedd5"
        else:
            archetype = "The Toothless Bully"
            badge = "⛓️ Toothless Bully"
            tier = "Harmless Adversary"
            desc = "Strained or hostile intent, but powerless and behind bars. Petty irritations without lasting material ruin."
            color = "#854d0e"
            bg = "#fef3c7"

    return {
        "archetype": archetype,
        "badge": badge,
        "tier": tier,
        "description": desc,
        "color": color,
        "bg": bg,
        "is_high_dignity": is_high_dig,
        "is_high_strength": is_high_musc
    }


def classify_graha_quadrant(
    dignity_pct: float,
    shadbala_pct: float,
    is_node: bool = False,
    is_rescued: bool = False,
    dignity_name: str = ""
) -> Dict[str, Any]:
    """Preserves backward compatibility while forwarding to the 9-tier archetype classifier."""
    return classify_graha_archetype(
        effective_dignity=dignity_pct,
        effective_shadbala=shadbala_pct,
        is_rescued=is_rescued,
        is_node=is_node,
        dignity_name=dignity_name
    )


TARA_GRAHAS = ["Mars", "Mercury", "Jupiter", "Venus", "Saturn"]


def detect_planetary_wars(
    grahas_data: Dict[str, Any],
    shadbala_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Dict[str, Any]]:
    """
    Detects Graha Yuddha (Planetary War) per Phaladeepika 4.2 & BPHS.

    Rules of Engagement:
    1. Only the 5 Tara Grahas engage in war: Mars, Mercury, Jupiter, Venus, Saturn.
       (Sun combusts, Moon occults, Rahu/Ketu swallow/shadow).
    2. Threshold: Residing in the SAME SIGN within <= 1°00' (60 arcminutes) of each other.
    3. Determination of Victor:
       - Venus Invariance: Venus NEVER loses a planetary war (peerless luminosity / Bahula-Ruchi).
       - For other pairs: The planet with the northern celestial latitude (higher numerical value) wins.
       - Fallback (if latitudes unavailable/equal): Higher Shadbala virupas / percentage wins.
         If still tied, natural brightness order: Jupiter > Mercury > Mars > Saturn.
    4. Consequences:
       - Victor (Jayi): war_mod = +0.30, inherits Combat Stain badge: '🏆 War Victor (Combat Stain: {loser})'
       - Defeated (Nipidita): war_mod = -0.60, badge: '⚔️ Nipidita (War Defeat via {winner})'
    """
    if not grahas_data:
        return {}

    war_results: Dict[str, Dict[str, Any]] = {}
    eligible = [p for p in TARA_GRAHAS if p in grahas_data]

    for i in range(len(eligible)):
        p1 = eligible[i]
        g1 = grahas_data[p1]
        s1 = g1.get("sign")
        d1 = float(g1.get("degree_0_to_30", g1.get("longitude", 0.0) % 30.0))
        lat1 = g1.get("latitude", g1.get("lat"))

        for j in range(i + 1, len(eligible)):
            p2 = eligible[j]
            g2 = grahas_data[p2]
            s2 = g2.get("sign")
            d2 = float(g2.get("degree_0_to_30", g2.get("longitude", 0.0) % 30.0))
            lat2 = g2.get("latitude", g2.get("lat"))

            if s1 != s2:
                continue

            deg_diff = abs(d1 - d2)
            if deg_diff <= 1.0:
                # Determine winner
                if p1 == "Venus":
                    winner, loser = p1, p2
                    reason = "Venus Invariance Rule (Supreme Natural Brilliance)"
                elif p2 == "Venus":
                    winner, loser = p2, p1
                    reason = "Venus Invariance Rule (Supreme Natural Brilliance)"
                else:
                    # Northern celestial latitude
                    if lat1 is not None and lat2 is not None and abs(float(lat1) - float(lat2)) > 0.001:
                        if float(lat1) > float(lat2):
                            winner, loser = p1, p2
                            reason = f"Northern Celestial Latitude ({float(lat1):+.2f}° vs {float(lat2):+.2f}°)"
                        else:
                            winner, loser = p2, p1
                            reason = f"Northern Celestial Latitude ({float(lat2):+.2f}° vs {float(lat1):+.2f}°)"
                    else:
                        sb1 = (shadbala_data or {}).get(p1, {})
                        sb2 = (shadbala_data or {}).get(p2, {})
                        v1 = float(sb1.get("Total_Virupas", sb1.get("Pct_Required_Total", 0.0)))
                        v2 = float(sb2.get("Total_Virupas", sb2.get("Pct_Required_Total", 0.0)))
                        if abs(v1 - v2) > 0.1:
                            if v1 > v2:
                                winner, loser = p1, p2
                                reason = f"Higher Shadbala Virupas ({v1:.1f}v vs {v2:.1f}v)"
                            else:
                                winner, loser = p2, p1
                                reason = f"Higher Shadbala Virupas ({v2:.1f}v vs {v1:.1f}v)"
                        else:
                            brightness_rank = {"Jupiter": 4, "Mercury": 3, "Mars": 2, "Saturn": 1}
                            if brightness_rank.get(p1, 0) >= brightness_rank.get(p2, 0):
                                winner, loser = p1, p2
                            else:
                                winner, loser = p2, p1
                            reason = "Natural Luminosity Order"

                war_results[winner] = {
                    "in_war": True,
                    "is_winner": True,
                    "is_loser": False,
                    "opponent": loser,
                    "war_mod": 0.30,
                    "badge": f"🏆 War Victor (Combat Stain: {loser})",
                    "reason": reason,
                    "orb_deg": round(deg_diff, 3),
                    "sign": s1,
                    "details": f"{winner} defeated {loser} in Graha Yuddha (orb: {deg_diff:.2f}° in {s1}) via {reason}."
                }
                war_results[loser] = {
                    "in_war": True,
                    "is_winner": False,
                    "is_loser": True,
                    "opponent": winner,
                    "war_mod": -0.60,
                    "badge": f"⚔️ Nipidita (War Defeat via {winner})",
                    "reason": reason,
                    "orb_deg": round(deg_diff, 3),
                    "sign": s1,
                    "details": f"{loser} defeated by {winner} in Graha Yuddha (orb: {deg_diff:.2f}° in {s1}) entering Nipidita Avastha."
                }

    return war_results


def calculate_graha_vitality(
    planet: str,
    sign: str,
    degree_in_sign: float,
    dignity_name: str,
    dignity_pct: float,
    host_planet: str,
    host_dignity_pct: float,
    host_shadbala_pct: float,
    planet_shadbala_pct: float,
    net_drishti_virupas: float = 0.0,
    conjunctions: Optional[List[str]] = None,
    lajjitadi_states: Optional[List[Any]] = None,
    is_retrograde: bool = False,
    is_combust: bool = False,
    is_node: bool = False,
    lagna_sign: str = "Leo",
    lagna_lord: Optional[str] = None,
    # New parameters for Graha Yuddha, Recursive Drishti (Option A), & Conjunction Orbs
    is_war_winner: bool = False,
    is_war_loser: bool = False,
    war_opponent: Optional[str] = None,
    war_badge: Optional[str] = None,
    conjunction_details: Optional[List[Dict[str, Any]]] = None,
    aspect_details: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Calibrated Net Functional Vitality calculation resolving architectural flaws:
    1. Replaces flat 1/5th average with true 9-Tier Quality vs Muscle dynamics.
    2. Enforces strict Neecha Bhanga exclusively for classical signs of fall.
    3. Factors Baladi biological efficiency (Phaladeepika 3.10).
    4. Dynamically tilts neutral signs based on host dispositor, benefic rays, and Lagnesha protection.
    5. Evaluates Rahu and Ketu through their dispositor proxy.
    6. Balances psychological feeling states (Lajjitadi) with physical stamina.
    7. Integrates Graha Yuddha (Planetary War): Nipidita (-0.60) / War Victor (+0.30) with Combat Stain.
    8. Integrates Recursive Drishti (Option A): Debilitated benefic rays dampened by 50% with distorted badge.
    9. Integrates Conjunction Dynamics: Nodal possession within 3°20' (Ketu suppression / Rahu obsession).
    """
    conjunctions = conjunctions or []
    lajjitadi_states = lajjitadi_states or []

    # 1. Baladi Avastha
    baladi = calculate_baladi_avastha(sign, degree_in_sign)
    efficiency = baladi["efficiency_factor"]

    # 2. Host Dispositor & Strict Debilitation Evaluation
    is_debilitated = (planet in TRUE_DEBILITATION_MAP and sign == TRUE_DEBILITATION_MAP[planet]) or \
                     ("debilit" in dignity_name.lower()) or ("neecha" in dignity_name.lower())
    is_self_hosted = (host_planet == planet)
    is_rescued = False
    effective_dignity = dignity_pct
    rescue_status = "Neutral Host Foundation"
    rescue_badge = "⚖️ Neutral Host"

    if is_node:
        affinity = 15.0 if ((planet == "Rahu" and sign in RAHU_STRONG_SIGNS) or (planet == "Ketu" and sign in KETU_STRONG_SIGNS)) else 0.0
        effective_dignity = clamp(host_dignity_pct * 0.85 + affinity, 15.0, 100.0)
        effective_shadbala = max(60.0, host_shadbala_pct * 0.90)
        rescue_status = f"Chhāyā Proxy via {host_planet}"
        rescue_badge = f"Reflects {host_planet}"
    elif is_self_hosted:
        rescue_status = "Self-Hosted / Domicile"
        rescue_badge = "🏡 Self-Hosted"
        effective_dignity = dignity_pct
        effective_shadbala = planet_shadbala_pct
    elif is_debilitated:
        if host_dignity_pct >= 62.5 and host_shadbala_pct >= 90.0:
            rescue_status = "Full Alchemical Rescue (Neecha Bhanga)"
            rescue_badge = "✨ Rescued (Neecha Bhanga)"
            effective_dignity = clamp(dignity_pct + 50.0 * (host_dignity_pct / 100.0), 20.0, 85.0)
            is_rescued = True
        elif host_dignity_pct >= 50.0:
            rescue_status = "Partially Rescued by Capable Host"
            rescue_badge = "✨ Partial Rescue"
            effective_dignity = clamp(dignity_pct + 25.0 * (host_dignity_pct / 100.0), 15.0, 65.0)
        elif host_dignity_pct < 25.0:
            rescue_status = "Unsaved / Strained Host"
            rescue_badge = "⚠️ Strained Host"
            effective_dignity = max(10.0, dignity_pct - 5.0)
        else:
            rescue_status = "Neutral Host Foundation"
            rescue_badge = "⚖️ Neutral Host"
            effective_dignity = dignity_pct
        effective_shadbala = planet_shadbala_pct
    else:
        if host_dignity_pct >= 60.0:
            if dignity_pct <= 25.0:
                effective_dignity = min(40.0, dignity_pct + 10.0 * (host_dignity_pct / 100.0))
                rescue_status = f"Stabilized by Exalted Host {host_planet}" if host_dignity_pct >= 85.0 else f"Stabilized by Fortified Host {host_planet}"
                rescue_badge = "🛡️ Fortified Host"
            else:
                effective_dignity = min(100.0, dignity_pct + 12.0 * (host_dignity_pct / 100.0))
                rescue_status = "Fortified by Dignified Host"
                rescue_badge = "🛡️ Fortified Host"
        elif host_dignity_pct < 25.0:
            rescue_status = "Slight Drag from Strained Host"
            rescue_badge = "⚠️ Strained Host"
            effective_dignity = max(10.0, dignity_pct - 6.0)
        else:
            rescue_status = "Neutral Host Foundation"
            rescue_badge = "⚖️ Neutral Host"
            effective_dignity = dignity_pct
        effective_shadbala = planet_shadbala_pct

    # Neutral Sign Tilting (Sama Kshetra)
    if "neutral" in dignity_name.lower() or "sama" in dignity_name.lower() or (35.0 <= dignity_pct <= 50.0):
        if net_drishti_virupas > 0:
            effective_dignity += min(12.0, (net_drishti_virupas / 35.0) * 10.0)
        for item in lajjitadi_states:
            st = (item.get("state", "") if isinstance(item, dict) else str(item)).lower()
            if "mudita" in st or "garvita" in st:
                effective_dignity += 4.0
                break
        effective_dignity = min(54.9, effective_dignity)

    # 3. 9-Tier Behavioral Archetype Classification
    quad = classify_graha_archetype(
        effective_dignity,
        effective_shadbala,
        is_rescued=is_rescued,
        is_node=is_node,
        dignity_name=dignity_name
    )

    # 4. Calibrated Functional Vitality Score (1.0 to 10.0)
    q_norm = effective_dignity / 10.0  # 1.0 to 10.0
    m_ratio = effective_shadbala / 100.0  # 1.0 = baseline (100%)

    if is_rescued:
        base_vit = 7.5 + (m_ratio - 1.0) * 0.8
    elif q_norm >= 5.5:
        base_vit = 5.5 + (q_norm - 5.5) * 0.8 + (m_ratio - 1.0) * 1.2
    elif q_norm >= 3.5:
        base_vit = 5.0 + (q_norm - 3.5) * 0.5 + (m_ratio - 1.0) * 1.5
    else:
        q_deficit = 3.5 - q_norm
        if effective_shadbala >= 110.0:
            hazard_mult = min(1.3, 0.75 + 0.25 * m_ratio)
            base_vit = 3.8 - (q_deficit * hazard_mult) - (m_ratio - 1.0) * 1.0
        elif effective_shadbala < 88.0:
            base_vit = 3.5 - (q_deficit * 0.5) - max(0.0, 1.0 - m_ratio) * 0.5
        else:
            base_vit = 4.2 - (q_deficit * 0.6) + (m_ratio - 1.0) * 0.5

    # 5. Environmental Modifications (Option A Recursive Drishti & Conjunction Dynamics)
    processed_aspect_details = []
    if aspect_details:
        total_adj_virupas = 0.0
        for asp in aspect_details:
            from_p = asp.get("from_planet", "")
            vir = float(asp.get("virupas", 0.0))
            from_dig_pct = float(asp.get("from_dignity_pct", 50.0))
            from_dig_name = str(asp.get("from_dignity_name", ""))
            is_deb = asp.get("is_debilitated", (from_dig_pct <= 25.0) or ("debilit" in from_dig_name.lower()) or ("neecha" in from_dig_name.lower()))
            is_distorted = False
            badge = ""

            # Option A: Debilitated benefics (Jupiter, Venus) transmit distorted rays
            if from_p in ["Jupiter", "Venus"] and is_deb:
                is_distorted = True
                adj_vir = (vir * 0.5) if vir > 0 else vir  # 50% positive dampening
                if from_p == "Jupiter":
                    badge = "⚠️ Distorted Ideology / Dogmatic Light"
                else:
                    badge = "⚠️ Corrupted Indulgence"
            else:
                adj_vir = vir

            total_adj_virupas += adj_vir
            processed_aspect_details.append({
                "from_planet": from_p,
                "raw_virupas": vir,
                "adjusted_virupas": adj_vir,
                "from_dignity_pct": from_dig_pct,
                "from_dignity_name": from_dig_name,
                "is_debilitated": is_deb,
                "is_distorted": is_distorted,
                "badge": badge
            })
        drishti_mod = clamp(total_adj_virupas / 35.0, -1.0, 1.0) * 0.7
    else:
        drishti_mod = clamp(net_drishti_virupas / 35.0, -1.0, 1.0) * 0.7

    # Conjunction Dynamics & Nodal Possession
    conj_mod = 0.0
    node_mod = 0.0
    processed_conjunction_details = []

    if conjunction_details:
        for c_item in conjunction_details:
            cp = c_item.get("planet", "")
            diff = float(c_item.get("degree_diff", 5.0))
            cp_sb = float(c_item.get("shadbala_pct", 100.0))
            band = "Exact (Intimate)" if diff <= (10.0 / 3.0) else ("Moderate" if diff <= 10.0 else "Wide")
            commands = (cp_sb > planet_shadbala_pct)

            # Close Nodal Possession (within 3°20')
            if cp == "Ketu" and diff <= (10.0 / 3.0):
                efficiency *= 0.80  # biological/external suppression
                node_mod -= 0.25
            elif cp == "Rahu" and diff <= (10.0 / 3.0):
                if host_dignity_pct >= 60.0 and host_shadbala_pct >= 90.0:
                    node_mod += 0.20  # constructive worldly amplification
                else:
                    node_mod -= 0.35  # toxic obsession / delusion
            elif cp in ["Jupiter", "Venus"]:
                conj_mod += 0.30
            elif cp == lagna_lord:
                conj_mod += 0.35
            elif cp in ["Saturn", "Mars"]:
                conj_mod -= 0.30
            elif cp in ["Rahu", "Ketu"] and diff > (10.0 / 3.0):
                conj_mod -= 0.20

            processed_conjunction_details.append({
                "planet": cp,
                "degree_diff": diff,
                "orb_band": band,
                "shadbala_pct": cp_sb,
                "commands": commands
            })
    else:
        for cp in conjunctions:
            if cp in ["Jupiter", "Venus"]:
                conj_mod += 0.30
            elif cp == lagna_lord:
                conj_mod += 0.35
            elif cp in ["Saturn", "Mars", "Rahu", "Ketu"]:
                conj_mod -= 0.30

    env_mod = clamp(drishti_mod + conj_mod, -1.2, 1.2)

    # 6. Motional Modifiers
    mot_mod = 0.0
    if is_retrograde and planet in ["Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
        mot_mod += 0.3
    if is_combust:
        mot_mod -= 0.5

    # 7. Planetary War (Graha Yuddha) Modifier
    war_mod = 0.0
    if is_war_loser:
        war_mod = -0.60
        if not war_badge:
            war_badge = f"⚔️ Nipidita (War Defeat via {war_opponent})" if war_opponent else "⚔️ Nipidita (War Defeat)"
    elif is_war_winner:
        war_mod = 0.30
        if not war_badge:
            war_badge = f"🏆 War Victor (Combat Stain: {war_opponent})" if war_opponent else "🏆 War Victor"

    # 8. Psychological Feeling State (Lajjitadi)
    psy_mod = 0.0
    has_garvita = False
    for item in lajjitadi_states:
        st = (item.get("state", "") if isinstance(item, dict) else str(item)).lower()
        if "garvita" in st:
            has_garvita = True
            psy_mod += 0.35
        elif "mudita" in st:
            psy_mod += 0.30
        elif "kshudhita" in st:
            psy_mod -= 0.35
        elif "kshobhita" in st:
            psy_mod -= 0.25
        elif "lajjita" in st:
            psy_mod -= (0.20 if has_garvita else 0.45)
        elif "trushita" in st:
            psy_mod -= 0.20
    psy_mod = clamp(psy_mod, -1.0, 1.0)

    pre_score = base_vit + env_mod + mot_mod + psy_mod + war_mod + node_mod
    final_score = 5.0 + (pre_score - 5.0) * (0.6 + 0.4 * efficiency)
    final_score = clamp(round(final_score, 1), 1.0, 10.0)

    if final_score >= 8.5:
        v_tier = "🌟 Sovereign"
        v_bg = "#fef3c7"; v_col = "#92400e"
    elif final_score >= 7.0:
        v_tier = "🟢 Capable"
        v_bg = "#dcfce7"; v_col = "#15803d"
    elif final_score >= 5.5:
        v_tier = "🟡 Resilient"
        v_bg = "#fef9c3"; v_col = "#854d0e"
    elif final_score >= 4.0:
        v_tier = "🟠 Strained"
        v_bg = "#ffedd5"; v_col = "#9a3412"
    else:
        v_tier = "🔴 Severe Hazard" if quad["archetype"] == "The Armed Dictator" else "🔴 Fragile"
        v_bg = "#fee2e2"; v_col = "#991b1b"

    return {
        "vitality_score": final_score,
        "vitality_tier": v_tier,
        "vitality_bg": v_bg,
        "vitality_col": v_col,
        "effective_dignity_pct": round(effective_dignity, 1),
        "effective_shadbala_pct": round(effective_shadbala, 1),
        "rescue_status": rescue_status,
        "rescue_badge": rescue_badge,
        "is_rescued": is_rescued,
        "is_neecha_bhanga": is_rescued,
        "baladi": baladi,
        "quadrant": quad,
        "base_vitality": round(base_vit, 1),
        "env_mod": round(env_mod, 1),
        "mot_mod": round(mot_mod, 1),
        "psy_mod": round(psy_mod, 1),
        "war_mod": round(war_mod, 1),
        "node_mod": round(node_mod, 2),
        "is_war_winner": is_war_winner,
        "is_war_loser": is_war_loser,
        "war_opponent": war_opponent,
        "war_badge": war_badge,
        "aspect_details": processed_aspect_details,
        "conjunction_details": processed_conjunction_details
    }


def calculate_planetary_evaluation(
    vargas_data: Dict[str, Any],
    shadbala_data: Optional[Dict[str, Any]] = None,
    advanced_aspects: Optional[Dict[str, Any]] = None
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
        if p in ["Rahu", "Ketu"]:
            host_sb = (shadbala_data or {}).get(sign_lord, {})
            host_virupas = host_sb.get("Total_Virupas", host_sb.get("total_virupas", 360.0))
            host_pct = host_sb.get("Pct_Required_Total", 100.0)
            tot_virupas = host_virupas * 0.90
            tot_rupas = tot_virupas / 60.0
            req_virupas = 360.0
            sb_ratio = round((host_pct / 100.0) * 0.90, 2)
            is_high_strength = (sb_ratio >= 0.95)
        else:
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
            "motional_factors": motional_factors,
            "is_proxy": p in ["Rahu", "Ketu"],
            "proxy_host": sign_lord if p in ["Rahu", "Ketu"] else None
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

        baladi_res = calculate_baladi_avastha(p_sign, p_d1.get("degree_0_to_30", p_lon % 30.0))
        quad_dig_pct = avg_dignity if p not in ["Rahu", "Ketu"] else clamp(host_dignity * 0.85 + (15.0 if ((p == "Rahu" and p_sign in RAHU_STRONG_SIGNS) or (p == "Ketu" and p_sign in KETU_STRONG_SIGNS)) else 0.0), 10.0, 100.0)
        quad_sb_pct = sb_ratio * 100.0
        quad_res = classify_graha_quadrant(quad_dig_pct, quad_sb_pct, is_node=(p in ["Rahu", "Ketu"]))

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
            "quadrant": quad_res,
            "baladi_avastha": baladi_res,
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
    lagna_lord_eval = planets_result.get(lagna_lord, {})
    
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
            "placed_sign": lagna_lord_eval.get("sign", ""),
            "placed_degree": lagna_lord_eval.get("longitude", 0.0),
            "scale_score": lagna_lord_eval.get("net_scale_score", 0.0),
            "expression_mode": lagna_lord_eval.get("expression_mode", "Mixed"),
            "expression_class": lagna_lord_eval.get("expression_class", "mixed"),
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

    lagna_eval = evaluate_lagna_vitality(vargas_data, shadbala_data, advanced_aspects, "D1")

    planetary_wars = detect_planetary_wars(d1_grahas, shadbala_data)
    for p, war_info in planetary_wars.items():
        if p in planets_result:
            planets_result[p]["planetary_war"] = war_info

    return {
        "summary": {
            "title": "Vic DiCara's Planetary Evaluation & Positive-to-Negative Scale",
            "subtitle": "Continuous diagnostic spectrum (-100% to +100%) and 4-Quadrant Archetypes (Phaladeepika Chapters 3 & 4)",
            "master_lords": master_lords,
            "lagna_evaluation": lagna_eval,
            "planetary_wars": planetary_wars,
            "chart_predominance": {
                "auspicious_count": auspicious_count,
                "hostile_count": hostile_count,
                "overall_status": overall_pred,
                "meaning": overall_meaning
            }
        },
        "lagna_evaluation": lagna_eval,
        "planetary_wars": planetary_wars,
        "planets": planets_result
    }
