"""
Astra Chart Assessment Report Engine (jyotish/report/report_engine.py)

Master orchestrator for the streamlined Chart Assessment Report:
1. Ascendant Nakshatra & Moon Nakshatra (pure side-by-side descriptive dossiers)
2. Rising Rāśi & Rising Navāṁśa (pure side-by-side descriptive sign dossiers)
3. Nakshatra Dominance Leaderboard (Prominence-scaled empirical occupancy)
4. Balance of Nakshatra Types (6-Group Model evaluated against 16.7% baseline)
"""

import os
import json
from typing import Dict, Any, List, Optional
from jyotish.nakshatras.lore import (
    get_nakshatra_lore,
    get_nakshatra_group,
    get_temperament_relationship,
    normalize_nakshatra_name,
    NAKSHATRA_GROUP_METADATA,
    NAKSHATRA_TEMPERAMENT_DOSSIER,
    ALL_NAKSHATRA_GROUPS
)
from jyotish.report.prominence import compute_planetary_prominence
from jyotish.report.varga_environment import compute_varga_environment


ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

NAKSHATRA_KEYWORDS: Dict[str, List[str]] = {
    "Ashwini": ["Miraculous Healing", "Pioneering Speed", "Agile Vitality", "Spirited Autonomy"],
    "Bharani": ["Primal Restraint", "Transformative Endurance", "Fierce Discipline", "Sacred Crucible"],
    "Krittika": ["Sacred Flame", "Discriminating Blade", "Universal Catalysis", "Purifying Courage"],
    "Rohini": ["Sensual Creativity", "Fertile Growth", "Magnetic Allure", "Material Realization"],
    "Mrigashira": ["Inquisitive Searching", "Restless Exploration", "Gentle Sensitivity", "Erotic Playfulness"],
    "Ardra": ["Cathartic Dissolution", "Penetrating Truth", "Storm Wisdom", "Emotional Purge"],
    "Punarvasu": ["Restoration & Renewal", "Benevolent Abundance", "Spiritual Return", "Nourishing Safety"],
    "Pushya": ["Supreme Nourishment", "Spiritual Wisdom", "Inner Solace", "Generous Stewardship"],
    "Ashlesha": ["Penetrating Intuition", "Hypnotic Allure", "Esoteric Wisdom", "Shedding Limitations"],
    "Magha": ["Ancestral Authority", "Royal Dignity", "Lineage Legacy", "Sovereign Pride"],
    "Purva Phalguni": ["Relaxation & Pleasure", "Creative Enjoyment", "Social Charm", "Marital Romance"],
    "Uttara Phalguni": ["Steadfast Loyalty", "Contractual Honor", "Chivalric Protection", "Generous Patronage"],
    "Hasta": ["Dexterous Craftsmanship", "Strategic Calculation", "Manifestation", "Humorous Resourcefulness"],
    "Chitra": ["Aesthetic Perfection", "Architectural Mastery", "Brilliant Radiance", "Structural Design"],
    "Swati": ["Independent Individuation", "Dynamic Versatility", "Restless Freedom", "Diplomatic Agility"],
    "Vishakha": ["One-Pointed Determination", "Triumphant Harvesting", "Strategic Coupling", "Focused Will"],
    "Anuradha": ["Deep Devotion", "Organizational Bridge-Building", "Loyal Friendship", "Esoteric Resilience"],
    "Jyeshtha": ["Senior Authority", "Protective Shield", "Elder Strategy", "Sovereign Grit"],
    "Mula": ["Root-Cause Inquiry", "Radical Uprooting", "Bedrock Truth", "Philosophical Detachment"],
    "Purva Ashadha": ["Invincible Conviction", "Purifying Waters", "Unyielding Pride", "Philosophical Idealism"],
    "Uttara Ashadha": ["Fortified Determination", "Tenacity", "Consolidation", "Unshakeable Victory"],
    "Shravana": ["Attentive Listening", "Oral Tradition", "Scholarly Erudition", "Receptive Wisdom"],
    "Dhanishtha": ["Rhythmic Harmony", "Material Wealth", "Unifying Symphony", "Benevolent Fortune"],
    "Dhanishta": ["Rhythmic Harmony", "Material Wealth", "Unifying Symphony", "Benevolent Fortune"],
    "Shatabhisha": ["100 Remedies", "Mystic Veiling", "Profound Solitude", "Universal Healing"],
    "Purva Bhadrapada": ["Ascetic Intensity", "Two-Faced Fire", "Spiritual Penance", "Evolutionary Crucible"],
    "Uttara Bhadrapada": ["Deep Wisdom", "Serenity & Stillness", "Patient Benevolence", "Cosmic Grounding"],
    "Revati": ["Compassionate Safe Passage", "Universal Guidance", "Prosperous Journey", "Transcendent Completion"]
}


def get_detailed_nakshatra_dossier(nak_name: str, pada: int = 1) -> Dict[str, Any]:
    """
    Extracts the full descriptive dossier for a nakshatra from lore.
    Provides the archetypal attributes needed for personal synthesis:
    Name, Sanskrit Meaning, Presiding Deity, Symbol, Temperament Class,
    Keywords, and the complete interpretive lore.
    """
    lore = get_nakshatra_lore(nak_name) or {}
    group = get_nakshatra_group(nak_name) or "Dhruva"
    metadata = NAKSHATRA_GROUP_METADATA.get(group, {})
    
    # Parse symbol and Sanskrit meaning
    sym_etym = lore.get("symbol_etymology", "")
    sanskrit_meaning = lore.get("meaning", "")
    symbol = lore.get("symbol", "")
    if not sanskrit_meaning and "; Sanskrit for " in sym_etym:
        parts = sym_etym.split("; Sanskrit for ", 1)
        if not symbol:
            symbol = parts[0].strip()
        raw_mng = parts[1].strip()
        if raw_mng.startswith("'") and raw_mng.endswith("'"):
            raw_mng = raw_mng[1:-1].strip()
        sanskrit_meaning = raw_mng
    elif not sanskrit_meaning and "; Sanskrit " in sym_etym:
        parts = sym_etym.split("; Sanskrit ", 1)
        if not symbol:
            symbol = parts[0].strip()
        raw_mng = parts[1].strip()
        if raw_mng.startswith("'") and raw_mng.endswith("'"):
            raw_mng = raw_mng[1:-1].strip()
        sanskrit_meaning = raw_mng
    elif not sanskrit_meaning:
        sanskrit_meaning = sym_etym
        
    if not symbol:
        symbol = sym_etym

    deity = lore.get("deity") or lore.get("presiding_deity", "")
    keywords = lore.get("keywords") or NAKSHATRA_KEYWORDS.get(normalize_nakshatra_name(nak_name), [])
    description = lore.get("description") or lore.get("essence") or lore.get("core_psychology", "")
    
    return {
        "name": nak_name,
        "pada": pada,
        "sanskrit_meaning": sanskrit_meaning,
        "deity": deity,
        "symbol": symbol,
        "group": group,
        "group_label": metadata.get("label", group),
        "group_nature": metadata.get("nature", ""),
        "keywords": keywords,
        "description": description
    }


def compute_ascendant_and_moon_nakshatras(
    vargas_data: Dict[str, Any],
    nakshatras_grahas: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Builds side-by-side descriptive dossiers for the Ascendant and Moon Nakshatras.
    Contains NO automated synthesis or friction scoring.
    """
    asc_data = nakshatras_grahas.get("Lagna", {})
    moon_data = nakshatras_grahas.get("Moon", {})
    
    asc_name = asc_data.get("nakshatra", "Ashwini")
    moon_name = moon_data.get("nakshatra", "Ashwini")
    
    asc_dossier = get_detailed_nakshatra_dossier(asc_name, pada=asc_data.get("pada", 1))
    asc_dossier["role"] = "Ascendant (Action / Ahaṃkāra / Bodily Vehicle)"
    
    moon_dossier = get_detailed_nakshatra_dossier(moon_name, pada=moon_data.get("pada", 1))
    moon_dossier["role"] = "Moon (Perception / Manas / Mental & Emotional Filter)"
    
    return {
        "ascendant": asc_dossier,
        "moon": moon_dossier
    }


# Significators JSON Cache
_SIGNIFICATIONS_FLOWCHARTS_CACHE: Optional[Dict[str, Any]] = None
_SIGNIFICATIONS_DATA_CACHE: Optional[Dict[str, Any]] = None


def get_significations_flowcharts() -> Dict[str, Any]:
    """Loads and caches jyotish/report/significations_flowcharts.json."""
    global _SIGNIFICATIONS_FLOWCHARTS_CACHE
    if _SIGNIFICATIONS_FLOWCHARTS_CACHE is not None:
        return _SIGNIFICATIONS_FLOWCHARTS_CACHE

    json_path = os.path.join(os.path.dirname(__file__), "significations_flowcharts.json")
    if os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                _SIGNIFICATIONS_FLOWCHARTS_CACHE = json.load(f)
                return _SIGNIFICATIONS_FLOWCHARTS_CACHE
        except Exception:
            pass
    return {"planets": {}, "signs": {}, "houses": {}}


def get_significations_data() -> Dict[str, Any]:
    """Loads and caches jyotish/report/significations_data.json."""
    global _SIGNIFICATIONS_DATA_CACHE
    if _SIGNIFICATIONS_DATA_CACHE is not None:
        return _SIGNIFICATIONS_DATA_CACHE

    json_path = os.path.join(os.path.dirname(__file__), "significations_data.json")
    if os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                _SIGNIFICATIONS_DATA_CACHE = json.load(f)
                return _SIGNIFICATIONS_DATA_CACHE
        except Exception:
            pass
    return {"planets": {}, "signs": {}, "houses": {}}


def get_detailed_sign_dossier(sign_name: str, degree_in_sign: float, is_navamsha: bool = False) -> Dict[str, Any]:
    """
    Builds a descriptive sign dossier using the structured archetypes
    in significations_data.json.
    """
    sign_data = get_significations_data().get("signs", {}).get(sign_name, {})

    # Fallback mappings if not present in JSON
    ELEMENT_MAP = {
        "Aries": "Fire", "Leo": "Fire", "Sagittarius": "Fire",
        "Taurus": "Earth", "Virgo": "Earth", "Capricorn": "Earth",
        "Gemini": "Air", "Libra": "Air", "Aquarius": "Air",
        "Cancer": "Water", "Scorpio": "Water", "Pisces": "Water"
    }
    GUNA_MAP = {
        "Aries": "Movable (Rajas)", "Cancer": "Movable (Rajas)", "Libra": "Movable (Rajas)", "Capricorn": "Movable (Rajas)",
        "Taurus": "Fixed (Tamas)", "Leo": "Fixed (Tamas)", "Scorpio": "Fixed (Tamas)", "Aquarius": "Fixed (Tamas)",
        "Gemini": "Dual (Sattva)", "Virgo": "Dual (Sattva)", "Sagittarius": "Dual (Sattva)", "Pisces": "Dual (Sattva)"
    }
    RULER_MAP = {
        "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury", "Cancer": "Moon",
        "Leo": "Sun", "Virgo": "Mercury", "Libra": "Venus", "Scorpio": "Mars",
        "Sagittarius": "Jupiter", "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter"
    }

    element = ELEMENT_MAP.get(sign_name, "Fire")
    modality = GUNA_MAP.get(sign_name, "Movable (Rajas)")
    ruler = RULER_MAP.get(sign_name, "Mars")

    # Extract pillars/columns of keywords from significations_data.json
    pillars_raw = sign_data.get("pillars", sign_data.get("columns", []))
    extracted_pillars = []
    for col in pillars_raw:
        col_name = col.get("name", "").capitalize()
        items = [item.get("title", "") for item in col.get("items", []) if item.get("title")]
        if items:
            extracted_pillars.append({
                "category": col_name,
                "keywords": items
            })

    formula = sign_data.get("formula") or f"{ruler} / {element} / {modality.split(' ')[0]}"

    deg = float(degree_in_sign) % 30.0
    deg_int = int(deg)
    minutes = int((deg % 1) * 60)

    return {
        "sign": sign_name,
        "symbol": sign_data.get("symbol", ""),
        "sanskrit": sign_data.get("sanskrit", ""),
        "ruler": ruler,
        "element": element,
        "modality": modality,
        "formula": formula,
        "degree_in_sign": round(degree_in_sign, 2),
        "degree_formatted": f"{deg_int}° {minutes:02d}'",
        "pillars": extracted_pillars,
        "nodes": sign_data.get("nodes", []),
        "edges": sign_data.get("edges", []),
        "columns": sign_data.get("columns", sign_data.get("pillars", [])),
        "banner": sign_data.get("banner", ""),
        "role": "Inner Soul Trajectory & Sub-Flavor (Fruit)" if is_navamsha else "Physical Body & Worldly Stage (Tree)"
    }


def compute_rising_rashi_and_navamsha(vargas_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extracts the D1 Rising Rāśi and D9 Rising Navāṁśa side-by-side.
    Flags Vargottama if both occupy the same sign.
    """
    d1_lagna = vargas_data.get("D1", {}).get("lagna", {})
    d9_lagna = vargas_data.get("D9", {}).get("lagna", {})

    rashi_sign = d1_lagna.get("sign", "Aries")
    rashi_deg = float(d1_lagna.get("degree_0_to_30", float(d1_lagna.get("longitude", 0.0)) % 30.0))

    navamsha_sign = d9_lagna.get("sign", "Aries")
    navamsha_deg = float(d9_lagna.get("degree_0_to_30", float(d9_lagna.get("longitude", 0.0)) % 30.0))

    is_vargottama = (rashi_sign == navamsha_sign)

    return {
        "rashi": get_detailed_sign_dossier(rashi_sign, rashi_deg, is_navamsha=False),
        "navamsha": get_detailed_sign_dossier(navamsha_sign, navamsha_deg, is_navamsha=True),
        "is_vargottama": is_vargottama,
        "vargottama_note": "Vargottama Lagna: Rising sign is identical in both D1 and D9 (+30% vitality & unshakeable inner-outer alignment)." if is_vargottama else None
    }



def compute_nakshatra_dominance(
    vargas_data: Dict[str, Any],
    nakshatras_grahas: Dict[str, Any],
    advanced_aspects: Optional[Dict[str, Any]] = None,
    prominence_map: Optional[Dict[str, float]] = None
) -> Dict[str, Any]:
    """
    Implements empirical Nakshatra dominance via Prominence-Scaled Occupancy:
    1. Filter out unoccupied nakshatras (strictly empirical bodily presence / Sthana).
    2. Key point weights scaled by Planetary Prominence:
       - Moon Nakshatra: 8.0 * Prominence_Moon
       - Lagna Nakshatra: 4.0 * 1.0 (foundational anchor)
       - Sun Nakshatra: 2.0 * Prominence_Sun
       - Ordinary Grahas: 1.0 * Prominence_Graha
    3. Tally multi-occupant nakshatras.
    Aspects are omitted from Nakshatra scoring because Grahas cast aspects, not stars,
    avoiding double-counting prominence and keeping asterisms strictly tied to physical presence.
    """
    occupied: Dict[str, Dict[str, Any]] = {}

    entities = ["Lagna", "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
    base_weights = {
        "Moon": 8.0,
        "Lagna": 4.0,
        "Sun": 2.0,
        "Mars": 1.0,
        "Mercury": 1.0,
        "Jupiter": 1.0,
        "Venus": 1.0,
        "Saturn": 1.0,
        "Rahu": 1.0,
        "Ketu": 1.0
    }

    for ent in entities:
        ent_data = nakshatras_grahas.get(ent, {})
        nak_name = ent_data.get("nakshatra")
        if not nak_name:
            continue

        if nak_name not in occupied:
            occupied[nak_name] = {
                "nakshatra": nak_name,
                "lore": get_nakshatra_lore(nak_name),
                "group": get_nakshatra_group(nak_name),
                "occupants": [],
                "base_points": 0.0,
                "total_points": 0.0,
                "dominance_pct": 0.0
            }

        # Prominence scaling
        prom = 1.0
        if prominence_map is not None:
            prom = float(prominence_map.get(ent, 1.0)) if ent != "Lagna" else 1.0
        base_w = base_weights.get(ent, 1.0)
        effective_weight = round(base_w * prom, 2)

        occupied[nak_name]["occupants"].append({
            "entity": ent,
            "base_weight": base_w,
            "prominence": round(prom, 2),
            "weight": effective_weight,
            "pada": ent_data.get("pada", 1),
            "lord": ent_data.get("nakshatra_lord", "--"),
            "sub_lord": ent_data.get("sub_lord", "--")
        })
        occupied[nak_name]["base_points"] += effective_weight

    # Tally totals
    grand_total = 0.0
    for data in occupied.values():
        data["base_points"] = round(data["base_points"], 2)
        data["total_points"] = data["base_points"]
        grand_total += data["total_points"]

    if grand_total <= 0.0:
        grand_total = 1.0

    # Sort descending
    sorted_nakshatras = sorted(occupied.values(), key=lambda x: x["total_points"], reverse=True)
    for idx, item in enumerate(sorted_nakshatras):
        item["rank"] = idx + 1
        item["dominance_pct"] = round((item["total_points"] / grand_total) * 100.0, 1)

    # Map classical Parashari classes to the 6 canonical display labels (16.7% baseline)
    TEMPERAMENT_CANONICAL = [
        {"group": "Chara", "label": "Mobile", "sanskrit": "Cara / Cala"},
        {"group": "Laghu", "label": "Quick", "sanskrit": "Kṣipra / Laghu"},
        {"group": "Mridu", "label": "Sweet", "sanskrit": "Mṛdu"},
        {"group": "Dhruva", "label": "Enduring", "sanskrit": "Dhruva / Sthira"},
        {"group": "Ugra", "label": "Strong", "sanskrit": "Ugra / Krūra"},
        {"group": "Tikshna", "label": "Bitter", "sanskrit": "Tīkṣṇa / Dāruṇa"}
    ]

    expected_baseline = round(100.0 / 6.0, 1)  # 16.7%
    group_totals: Dict[str, float] = {g["group"]: 0.0 for g in TEMPERAMENT_CANONICAL}
    catalyst_occupants: List[str] = []

    for item in sorted_nakshatras:
        nak_name = item["nakshatra"]
        pts = item["total_points"]
        # Universal Catalyst Rule: Krittika & Vishakha distribute to all 6 groups simultaneously
        if nak_name in ["Krittika", "Vishakha"]:
            catalyst_occupants.append(nak_name)
            for g in group_totals:
                group_totals[g] += pts
        else:
            g = item["group"]
            if g in group_totals:
                group_totals[g] += pts

    tot_temperament_points = sum(group_totals.values())
    if tot_temperament_points <= 0.0:
        tot_temperament_points = 1.0

    temperament_breakdown: List[Dict[str, Any]] = []
    for meta in TEMPERAMENT_CANONICAL:
        g = meta["group"]
        pts = round(group_totals[g], 2)
        pct = round((pts / tot_temperament_points) * 100.0, 1)
        deviation = round(pct - expected_baseline, 1)
        orig_meta = NAKSHATRA_GROUP_METADATA.get(g, {})
        dossier = NAKSHATRA_TEMPERAMENT_DOSSIER.get(g, {})

        if pct > 18.7:
            status = "Surplus"
            color = "#16a34a"  # Green
            bg = "#dcfce7"
        elif pct < 14.7:
            status = "Deficit"
            color = "#dc2626"  # Red
            bg = "#fee2e2"
        else:
            status = "Balanced"
            color = "#64748b"  # Muted Slate
            bg = "#f1f5f9"

        temperament_breakdown.append({
            "group": g,
            "display_name": meta["label"],
            "sanskrit": meta["sanskrit"],
            "label": f"{meta['label']} ({meta['sanskrit']})",
            "nature": orig_meta.get("nature", ""),
            "points": pts,
            "percentage": pct,
            "baseline_pct": expected_baseline,
            "deviation_pct": deviation,
            "status": status,
            "color": color,
            "bg": bg,
            "dossier": dossier
        })

    dominant_temperament = max(temperament_breakdown, key=lambda x: x["points"]) if temperament_breakdown else None
    dominant_nakshatra = sorted_nakshatras[0] if sorted_nakshatras else None

    # Relationship detection (Resonances vs Dissonances between top groups)
    surplus_groups = [item["group"] for item in temperament_breakdown if item["status"] == "Surplus"]
    active_relationships: List[Dict[str, Any]] = []
    if len(surplus_groups) >= 2:
        for i in range(len(surplus_groups)):
            for j in range(i + 1, len(surplus_groups)):
                rel_info = get_temperament_relationship(surplus_groups[i], surplus_groups[j])
                if rel_info:
                    active_relationships.append({
                        "group1": surplus_groups[i],
                        "group2": surplus_groups[j],
                        **rel_info
                    })
    if not active_relationships and len(temperament_breakdown) >= 2:
        sorted_by_pts = sorted(temperament_breakdown, key=lambda x: x["points"], reverse=True)
        rel_info = get_temperament_relationship(sorted_by_pts[0]["group"], sorted_by_pts[1]["group"])
        if rel_info:
            active_relationships.append({
                "group1": sorted_by_pts[0]["group"],
                "group2": sorted_by_pts[1]["group"],
                **rel_info
            })

    return {
        "grand_total_points": round(grand_total, 2),
        "total_temperament_points": round(tot_temperament_points, 2),
        "occupied_count": len(sorted_nakshatras),
        "dominant_nakshatra": dominant_nakshatra,
        "dominant_temperament": dominant_temperament,
        "leaderboard": sorted_nakshatras,
        "temperament_breakdown": temperament_breakdown,
        "active_relationships": active_relationships,
        "universal_catalysts": catalyst_occupants
    }


ELEMENT_LORE = {
    "Fire": {
        "display_name": "Fire",
        "sanskrit": "Tejas / Agni",
        "root_traits": "Bright & Hot",
        "nature": "Decisive, clear, moral discernment (Dharma), and authoritative leadership.",
        "icon": "🔥"
    },
    "Earth": {
        "display_name": "Earth",
        "sanskrit": "Pṛthvī",
        "root_traits": "Solid & Fertile",
        "nature": "Reliable, practical, tangible execution, material wealth (Artha), and endurance.",
        "icon": "🌍"
    },
    "Air": {
        "display_name": "Air",
        "sanskrit": "Vāyu",
        "root_traits": "Pleasant & Moving",
        "nature": "Enlivening, communicative, witty intellect, social networking, and pleasure (Kāma).",
        "icon": "💨"
    },
    "Water": {
        "display_name": "Water",
        "sanskrit": "Āpas / Jala",
        "root_traits": "Reflective & Soft",
        "nature": "Introspective, deep emotional digest, gentle, adaptable, and spiritual release (Mokṣa).",
        "icon": "💧"
    }
}

MODALITY_LORE = {
    "Rajas (Movable)": {
        "display_name": "Movable",
        "sanskrit": "Cara / Rajas",
        "nature": "Initiating dynamic action, adventurous speed, pioneering change, and decisive enterprise.",
        "icon": "⚡"
    },
    "Tamas (Fixed)": {
        "display_name": "Fixed",
        "sanskrit": "Sthira / Tamas",
        "nature": "Enduring stability, steadfast loyalty, unyielding resistance, and structured permanence.",
        "icon": "🏔️"
    },
    "Sattva (Dual)": {
        "display_name": "Dual",
        "sanskrit": "Dvisvabhāva / Sattva",
        "nature": "Versatile adaptation, intellectual fluidity, balance, and thoughtful compromise.",
        "icon": "⚖️"
    }
}


def compute_elemental_and_modal_balance(
    vargas_data: Dict[str, Any],
    prominence_map: Dict[str, float]
) -> Dict[str, Any]:
    """
    Computes Daśavarga-weighted elemental (25% baseline) and modal (33.3% baseline)
    balances, structured identically to the 6-class Nakshatra model.
    """
    env_data = compute_varga_environment(vargas_data, prominence_map=prominence_map)

    # 1. Elements (25.0% baseline)
    elements_table = []
    for item in env_data.get("elements_breakdown", []):
        k = item["key"]
        pct = item["percentage"]
        pts = item["points"]
        dev = round(pct - 25.0, 1)
        lore = ELEMENT_LORE.get(k, {})

        if pct > 27.0:
            status = "Surplus"
            color = "#16a34a"  # Green
            bg = "#dcfce7"
        elif pct < 23.0:
            status = "Deficit"
            color = "#dc2626"  # Red
            bg = "#fee2e2"
        else:
            status = "Balanced"
            color = "#64748b"  # Slate
            bg = "#f1f5f9"

        elements_table.append({
            "element": k,
            "display_name": lore.get("display_name", k),
            "sanskrit": lore.get("sanskrit", ""),
            "root_traits": lore.get("root_traits", ""),
            "nature": lore.get("nature", ""),
            "icon": lore.get("icon", ""),
            "points": pts,
            "percentage": pct,
            "baseline_pct": 25.0,
            "deviation_pct": dev,
            "status": status,
            "color": color,
            "bg": bg
        })

    # 2. Modalities (33.3% baseline)
    modalities_table = []
    for item in env_data.get("gunas_breakdown", []):
        k = item["key"]
        pct = item["percentage"]
        pts = item["points"]
        dev = round(pct - 33.3, 1)
        lore = MODALITY_LORE.get(k, {})

        if pct > 35.3:
            status = "Surplus"
            color = "#16a34a"
            bg = "#dcfce7"
        elif pct < 31.3:
            status = "Deficit"
            color = "#dc2626"
            bg = "#fee2e2"
        else:
            status = "Balanced"
            color = "#64748b"
            bg = "#f1f5f9"

        modalities_table.append({
            "modality": k,
            "display_name": lore.get("display_name", k),
            "sanskrit": lore.get("sanskrit", ""),
            "nature": lore.get("nature", ""),
            "icon": lore.get("icon", ""),
            "points": pts,
            "percentage": pct,
            "baseline_pct": 33.3,
            "deviation_pct": dev,
            "status": status,
            "color": color,
            "bg": bg
        })

    return {
        "elements": {
            "baseline_pct": 25.0,
            "dominant_element": env_data.get("elements", {}).get("dominant", "Fire"),
            "breakdown": elements_table
        },
        "modalities": {
            "baseline_pct": 33.3,
            "dominant_modality": env_data.get("gunas", {}).get("dominant", "Fixed (Tamas)"),
            "breakdown": modalities_table
        },
        "methodology": "Vic DiCara 10-Varga Model (D1: 2.0, D60: 3.33, Others: 1.0) scaled by Parāśarī Prominence"
    }


def generate_report_payload(chart_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Master orchestrator for the Astra Chart Assessment Report.
    Outputs the foundational sections and synthesis assets:
    1. Ascendant Nakshatra & Moon Nakshatra (pure side-by-side descriptive dossiers)
    2. Rising Rāśi ($D_1$) & Rising Navāṁśa ($D_9$) (pure side-by-side descriptive dossiers)
    3. Nakshatra Dominance Leaderboard (Prominence-scaled empirical occupancy)
    4. Balance of Nakshatra Types (6-Class Model evaluated against 16.7% baseline)
    5. Section 5: Elemental & Modal Balance (4 Elements & 3 Modes Tables)
    6. Planetary Rankings (Prominence scores, Shadbala ratio, Opportunity weights & reasons)
    7. Significations Data & Mermaid Flowcharts
    """
    vargas_data = chart_data.get("vargas", {})
    nakshatras_grahas = chart_data.get("nakshatras", {}).get("grahas", {})
    advanced_aspects = chart_data.get("advanced_aspects", {})
    shadbala_data = chart_data.get("shadbala", {})
    planetary_eval = chart_data.get("planetary_evaluation", {})
    vimshottari_at_birth = chart_data.get("vimshottari_dasha", {}).get("at_birth", {})
    vimshopaka_data = chart_data.get("varga_vimshopaka") or chart_data.get("vimshopaka")
    jd = chart_data.get("astronomy", {}).get("julian_day")

    # 1. Compute Prominence Leaderboard & Commander
    planetary_rankings = compute_planetary_prominence(
        vargas_data=vargas_data,
        shadbala_data=shadbala_data,
        advanced_aspects=advanced_aspects,
        nakshatras_grahas=nakshatras_grahas,
        vimshottari_at_birth=vimshottari_at_birth,
        planetary_eval=planetary_eval,
        vimshopaka_data=vimshopaka_data,
        jd=jd
    )
    prominence_map = planetary_rankings.get("prominence_map", {})

    # 2. Section 1: Ascendant & Moon Nakshatras (Side by Side)
    asc_moon_dossiers = compute_ascendant_and_moon_nakshatras(vargas_data, nakshatras_grahas)

    # 3. Section 2: Rising Rāśi & Rising Navāṁśa (Side by Side)
    rising_signs = compute_rising_rashi_and_navamsha(vargas_data)

    # 4. Section 3: Nakshatra Dominance & Section 4: Balance of Types (6-Class Model)
    nak_dominance = compute_nakshatra_dominance(
        vargas_data, nakshatras_grahas, advanced_aspects, prominence_map=prominence_map
    )

    # 5. Section 5: Elemental & Modal Balance (4 Elements & 3 Modes Tables)
    elemental_and_modal = compute_elemental_and_modal_balance(vargas_data, prominence_map)

    return {
        "title": "Astra Chart Assessment Report",
        "ascendant_and_moon": asc_moon_dossiers,
        "rising_signs": rising_signs,
        "nakshatra_dominance": {
            "leaderboard": nak_dominance["leaderboard"],
            "dominant_nakshatra": nak_dominance["dominant_nakshatra"],
            "total_points": nak_dominance["grand_total_points"]
        },
        "balance_of_nakshatra_types": {
            "baseline_pct": 16.7,
            "temperament_breakdown": nak_dominance["temperament_breakdown"],
            "dominant_temperament": nak_dominance["dominant_temperament"],
            "universal_catalysts": nak_dominance.get("universal_catalysts", [])
        },
        "elemental_and_modal_balance": elemental_and_modal,
        "planetary_rankings": planetary_rankings,
        "significations_data": get_significations_data(),
        "flowcharts": get_significations_flowcharts()
    }

