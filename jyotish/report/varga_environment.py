"""
jyotish/report/varga_environment.py
Dedicated 10-Varga (Daśavarga) Macro Environment & Thermodynamic Balance Engine.

Implements Vic DiCara's exact 10-Varga Daśavarga weighting model, scaling planetary
and Ascendant contributions by Parāśarī Prominence. Evaluates the aggregate thermodynamic
balance of Elements (Mahābhūtas), Modalities (Guṇas), Polarities, and Ayurvedic Doshas (Prakṛti).

Daśavarga Weight Distribution (Sum = 13.33):
- D1 (Rāśi / Physical Environment): 2.00
- D60 (Ṣaṣṭyaṁśa / Root Karmic Blueprint & Destiny Seeds): 3.33 (3 1/3)
- 8 Other Vargas (D2, D3, D7, D9, D10, D12, D16, D30): 1.00 each
"""

from typing import Dict, Any, List, Optional

# Vic DiCara's 10-Varga Daśavarga weighting distribution
DASAVARGA_ENVIRONMENTAL_WEIGHTS: Dict[str, float] = {
    "D1": 2.0,
    "D60": 3.33,
    "D2": 1.0,
    "D3": 1.0,
    "D7": 1.0,
    "D9": 1.0,
    "D10": 1.0,
    "D12": 1.0,
    "D16": 1.0,
    "D30": 1.0
}

TOTAL_DASAVARGA_WEIGHT: float = 13.33

ELEMENT_MAP: Dict[str, str] = {
    "Aries": "Fire", "Leo": "Fire", "Sagittarius": "Fire",
    "Taurus": "Earth", "Virgo": "Earth", "Capricorn": "Earth",
    "Gemini": "Air", "Libra": "Air", "Aquarius": "Air",
    "Cancer": "Water", "Scorpio": "Water", "Pisces": "Water"
}

GUNA_MAP: Dict[str, str] = {
    "Aries": "Rajas (Movable)", "Cancer": "Rajas (Movable)",
    "Libra": "Rajas (Movable)", "Capricorn": "Rajas (Movable)",
    "Taurus": "Tamas (Fixed)", "Leo": "Tamas (Fixed)",
    "Scorpio": "Tamas (Fixed)", "Aquarius": "Tamas (Fixed)",
    "Gemini": "Sattva (Dual)", "Virgo": "Sattva (Dual)",
    "Sagittarius": "Sattva (Dual)", "Pisces": "Sattva (Dual)"
}

POLARITY_MAP: Dict[str, str] = {
    "Aries": "Active", "Gemini": "Active", "Leo": "Active",
    "Libra": "Active", "Sagittarius": "Active", "Aquarius": "Active",
    "Taurus": "Passive", "Cancer": "Passive", "Virgo": "Passive",
    "Scorpio": "Passive", "Capricorn": "Passive", "Pisces": "Passive"
}

RISING_MODE_MAP: Dict[str, str] = {
    "Gemini": "Shirshodaya", "Leo": "Shirshodaya", "Virgo": "Shirshodaya",
    "Libra": "Shirshodaya", "Scorpio": "Shirshodaya", "Aquarius": "Shirshodaya",
    "Aries": "Prishtodaya", "Taurus": "Prishtodaya", "Cancer": "Prishtodaya",
    "Sagittarius": "Prishtodaya", "Capricorn": "Prishtodaya",
    "Pisces": "Ubhayodaya"
}

ELEMENTS_METADATA: List[Dict[str, str]] = [
    {"key": "Fire", "display_name": "Fire (Agni)", "sanskrit": "Tejas / Agni", "icon": "🔥", "accent_color": "#ea580c"},
    {"key": "Earth", "display_name": "Earth (Pṛthvī)", "sanskrit": "Pṛthvī", "icon": "🌍", "accent_color": "#059669"},
    {"key": "Air", "display_name": "Air (Vāyu)", "sanskrit": "Vāyu", "icon": "💨", "accent_color": "#0284c7"},
    {"key": "Water", "display_name": "Water (Jala)", "sanskrit": "Āpas / Jala", "icon": "💧", "accent_color": "#2563eb"}
]

GUNAS_METADATA: List[Dict[str, str]] = [
    {"key": "Rajas (Movable)", "display_name": "Rajas (Movable)", "sanskrit": "Cara", "icon": "⚡", "accent_color": "#d97706"},
    {"key": "Tamas (Fixed)", "display_name": "Tamas (Fixed)", "sanskrit": "Sthira", "icon": "🏔️", "accent_color": "#475569"},
    {"key": "Sattva (Dual)", "display_name": "Sattva (Dual)", "sanskrit": "Dvisvabhāva", "icon": "⚖️", "accent_color": "#0d9488"}
]

POLARITY_METADATA: List[Dict[str, str]] = [
    {"key": "Active", "display_name": "Active / Masculine (Odd)", "sanskrit": "Odd / Puruṣa / Day", "icon": "☀️", "accent_color": "#ea580c"},
    {"key": "Passive", "display_name": "Passive / Feminine (Even)", "sanskrit": "Even / Strī / Night", "icon": "🌙", "accent_color": "#6366f1"}
]

DOSHAS_METADATA: List[Dict[str, str]] = [
    {"key": "Vata", "display_name": "Vāta (Air)", "sanskrit": "Vāta", "icon": "🌬️", "accent_color": "#0284c7"},
    {"key": "Pitta", "display_name": "Pitta (Fire)", "sanskrit": "Pitta", "icon": "🔥", "accent_color": "#ea580c"},
    {"key": "Kapha", "display_name": "Kapha (Earth/Water)", "sanskrit": "Kapha", "icon": "🌊", "accent_color": "#2563eb"}
]


def compute_varga_environment(
    vargas_data: Dict[str, Any],
    prominence_map: Optional[Dict[str, float]] = None,
    lagna_boost: float = 1.0
) -> Dict[str, Any]:
    """
    Computes the 10-Varga (Daśavarga) Macro Environmental Tally.

    Args:
        vargas_data: Dictionary of divisional charts (D1, D2, D3, D7, D9, D10, D12, D16, D30, D60).
        prominence_map: Optional mapping of graha -> prominence score. Defaults to 1.0 for each graha.
        lagna_boost: Prominence boost multiplier for the Ascendant (defaults to 1.0, representing an average strong planet).

    Returns:
        Structured thermodynamic balance dictionary covering Elements, Modalities (Guṇas),
        Polarities, Ayurvedic Doshas, and Rising Modes.
    """
    d1_data = vargas_data.get("D1", {})
    d1_grahas = d1_data.get("grahas", {})
    d1_lagna = d1_data.get("lagna", {})

    entities = ["Lagna", "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]

    # 1. D1 physical placement counts (for direct empirical reference)
    elements_count = {"Fire": 0, "Earth": 0, "Air": 0, "Water": 0}
    gunas_count = {"Rajas (Movable)": 0, "Tamas (Fixed)": 0, "Sattva (Dual)": 0}
    polarity_count = {"Active": 0, "Passive": 0}
    rising_mode_count = {"Shirshodaya": 0, "Prishtodaya": 0, "Ubhayodaya": 0}
    dosha_count = {"Vata": 0, "Pitta": 0, "Kapha": 0}

    # 2. Daśavarga-weighted thermodynamic points
    elements_points = {"Fire": 0.0, "Earth": 0.0, "Air": 0.0, "Water": 0.0}
    gunas_points = {"Rajas (Movable)": 0.0, "Tamas (Fixed)": 0.0, "Sattva (Dual)": 0.0}
    polarity_points = {"Active": 0.0, "Passive": 0.0}
    rising_mode_points = {"Shirshodaya": 0.0, "Prishtodaya": 0.0, "Ubhayodaya": 0.0}
    dosha_points = {"Vata": 0.0, "Pitta": 0.0, "Kapha": 0.0}

    grand_total = 0.0

    for ent in entities:
        # Determine Prominence and D1 physical sign
        if ent == "Lagna":
            prom = 1.0 * lagna_boost
            d1_sign = d1_lagna.get("sign", "Aries")
        else:
            prom = float(prominence_map.get(ent, 1.0)) if prominence_map is not None else 1.0
            d1_sign = d1_grahas.get(ent, {}).get("sign", "Aries")

        # Tally D1 physical counts
        elem_d1 = ELEMENT_MAP.get(d1_sign, "Fire")
        elements_count[elem_d1] += 1

        guna_d1 = GUNA_MAP.get(d1_sign, "Rajas (Movable)")
        gunas_count[guna_d1] += 1

        pol_d1 = POLARITY_MAP.get(d1_sign, "Active")
        polarity_count[pol_d1] += 1

        rm_d1 = RISING_MODE_MAP.get(d1_sign, "Shirshodaya")
        if "Shirshodaya" in rm_d1:
            rising_mode_count["Shirshodaya"] += 1
        elif "Prishtodaya" in rm_d1:
            rising_mode_count["Prishtodaya"] += 1
        else:
            rising_mode_count["Ubhayodaya"] += 1

        if elem_d1 == "Fire":
            dosha_count["Pitta"] += 1
        elif elem_d1 == "Air":
            dosha_count["Vata"] += 1
        else:
            dosha_count["Kapha"] += 1

        # Accumulate weighted contributions across Daśavarga
        for v_code, v_weight in DASAVARGA_ENVIRONMENTAL_WEIGHTS.items():
            v_data = vargas_data.get(v_code, {})
            if ent == "Lagna":
                v_sign = v_data.get("lagna", {}).get("sign") or d1_sign
            else:
                v_sign = v_data.get("grahas", {}).get(ent, {}).get("sign") or d1_sign

            # Scaled contribution: Prominence × (W_v / 13.33)
            v_contrib = prom * (v_weight / TOTAL_DASAVARGA_WEIGHT)
            grand_total += v_contrib

            # Element
            elem = ELEMENT_MAP.get(v_sign, "Fire")
            elements_points[elem] += v_contrib

            # Guna / Modality
            guna = GUNA_MAP.get(v_sign, "Rajas (Movable)")
            gunas_points[guna] += v_contrib

            # Polarity
            pol = POLARITY_MAP.get(v_sign, "Active")
            polarity_points[pol] += v_contrib

            # Rising Mode
            rm = RISING_MODE_MAP.get(v_sign, "Shirshodaya")
            if "Shirshodaya" in rm:
                rising_mode_points["Shirshodaya"] += v_contrib
            elif "Prishtodaya" in rm:
                rising_mode_points["Prishtodaya"] += v_contrib
            else:
                rising_mode_points["Ubhayodaya"] += v_contrib

            # Ayurvedic Dosha
            if elem == "Fire":
                dosha_points["Pitta"] += v_contrib
            elif elem == "Air":
                dosha_points["Vata"] += v_contrib
            else:
                dosha_points["Kapha"] += v_contrib

    tot_elem_pts = sum(elements_points.values()) or 1.0
    tot_guna_pts = sum(gunas_points.values()) or 1.0
    tot_pol_pts = sum(polarity_points.values()) or 1.0
    tot_rm_pts = sum(rising_mode_points.values()) or 1.0
    tot_dosha_pts = sum(dosha_points.values()) or 1.0

    dominant_element = max(elements_points, key=elements_points.get)
    dominant_guna = max(gunas_points, key=gunas_points.get)
    dominant_polarity = max(polarity_points, key=polarity_points.get)
    dominant_dosha = max(dosha_points, key=dosha_points.get)

    # 3. Structured breakdowns with deviation and status flags
    expected_elem_baseline = 25.0
    elements_breakdown = []
    for meta in ELEMENTS_METADATA:
        k = meta["key"]
        pts = round(elements_points[k], 2)
        pct = round((elements_points[k] / tot_elem_pts) * 100.0, 1)
        dev = round(pct - expected_elem_baseline, 1)
        d1_c = elements_count.get(k, 0)
        status = "Surplus" if dev > 2.0 else ("Deficit" if dev < -2.0 else "Balanced")
        elements_breakdown.append({
            "key": k,
            "display_name": meta["display_name"],
            "sanskrit": meta["sanskrit"],
            "icon": meta["icon"],
            "accent_color": meta["accent_color"],
            "points": pts,
            "d1_count": d1_c,
            "percentage": pct,
            "baseline_pct": expected_elem_baseline,
            "deviation_pct": dev,
            "status": status
        })

    expected_guna_baseline = 33.3
    gunas_breakdown = []
    for meta in GUNAS_METADATA:
        k = meta["key"]
        pts = round(gunas_points[k], 2)
        pct = round((gunas_points[k] / tot_guna_pts) * 100.0, 1)
        dev = round(pct - expected_guna_baseline, 1)
        d1_c = gunas_count.get(k, 0)
        status = "Surplus" if dev > 2.0 else ("Deficit" if dev < -2.0 else "Balanced")
        gunas_breakdown.append({
            "key": k,
            "display_name": meta["display_name"],
            "sanskrit": meta["sanskrit"],
            "icon": meta["icon"],
            "accent_color": meta["accent_color"],
            "points": pts,
            "d1_count": d1_c,
            "percentage": pct,
            "baseline_pct": expected_guna_baseline,
            "deviation_pct": dev,
            "status": status
        })

    expected_pol_baseline = 50.0
    polarity_breakdown = []
    for meta in POLARITY_METADATA:
        k = meta["key"]
        pts = round(polarity_points[k], 2)
        pct = round((polarity_points[k] / tot_pol_pts) * 100.0, 1)
        dev = round(pct - expected_pol_baseline, 1)
        d1_c = polarity_count.get(k, 0)
        status = "Surplus" if dev > 2.0 else ("Deficit" if dev < -2.0 else "Balanced")
        polarity_breakdown.append({
            "key": k,
            "display_name": meta["display_name"],
            "sanskrit": meta["sanskrit"],
            "icon": meta["icon"],
            "accent_color": meta["accent_color"],
            "points": pts,
            "d1_count": d1_c,
            "percentage": pct,
            "baseline_pct": expected_pol_baseline,
            "deviation_pct": dev,
            "status": status
        })

    expected_dosha_baseline = 33.3
    doshas_breakdown = []
    for meta in DOSHAS_METADATA:
        k = meta["key"]
        pts = round(dosha_points[k], 2)
        pct = round((dosha_points[k] / tot_dosha_pts) * 100.0, 1)
        dev = round(pct - expected_dosha_baseline, 1)
        d1_c = dosha_count.get(k, 0)
        status = "Surplus" if dev > 2.0 else ("Deficit" if dev < -2.0 else "Balanced")
        doshas_breakdown.append({
            "key": k,
            "display_name": meta["display_name"],
            "sanskrit": meta["sanskrit"],
            "icon": meta["icon"],
            "accent_color": meta["accent_color"],
            "points": pts,
            "d1_count": d1_c,
            "percentage": pct,
            "baseline_pct": expected_dosha_baseline,
            "deviation_pct": dev,
            "status": status
        })

    return {
        "elements": {
            "counts": elements_count,
            "points": {k: round(v, 2) for k, v in elements_points.items()},
            "percentages": {k: round((v / tot_elem_pts) * 100.0, 1) for k, v in elements_points.items()},
            "dominant": dominant_element,
            "breakdown": elements_breakdown
        },
        "gunas": {
            "counts": gunas_count,
            "points": {k: round(v, 2) for k, v in gunas_points.items()},
            "percentages": {k: round((v / tot_guna_pts) * 100.0, 1) for k, v in gunas_points.items()},
            "dominant": dominant_guna,
            "breakdown": gunas_breakdown
        },
        "polarity": {
            "counts": polarity_count,
            "points": {k: round(v, 2) for k, v in polarity_points.items()},
            "percentages": {k: round((v / tot_pol_pts) * 100.0, 1) for k, v in polarity_points.items()},
            "dominant": dominant_polarity,
            "breakdown": polarity_breakdown
        },
        "rising_modes": {
            "counts": rising_mode_count,
            "points": {k: round(v, 2) for k, v in rising_mode_points.items()},
            "percentages": {k: round((v / tot_rm_pts) * 100.0, 1) for k, v in rising_mode_points.items()}
        },
        "ayurvedic_doshas": {
            "counts": dosha_count,
            "points": {k: round(v, 2) for k, v in dosha_points.items()},
            "percentages": {k: round((v / tot_dosha_pts) * 100.0, 1) for k, v in dosha_points.items()},
            "dominant": dominant_dosha,
            "breakdown": doshas_breakdown
        },
        "grand_total_points": round(grand_total, 2),
        "varga_weights": DASAVARGA_ENVIRONMENTAL_WEIGHTS,
        "total_varga_weight": TOTAL_DASAVARGA_WEIGHT,
        "elements_breakdown": elements_breakdown,
        "gunas_breakdown": gunas_breakdown,
        "polarity_breakdown": polarity_breakdown,
        "doshas_breakdown": doshas_breakdown,
        "methodology": "Vic DiCara 10-Varga (D1:2.0, D60:3.33, D2,3,7,9,10,12,16,30:1.0) scaled by Prominence"
    }


# Backward compatibility alias
def compute_environmental_tally(
    vargas_data: Dict[str, Any],
    prominence_map: Optional[Dict[str, float]] = None,
    lagna_boost: float = 1.0
) -> Dict[str, Any]:
    """Compatibility alias mapping to compute_varga_environment."""
    return compute_varga_environment(vargas_data, prominence_map=prominence_map, lagna_boost=lagna_boost)
