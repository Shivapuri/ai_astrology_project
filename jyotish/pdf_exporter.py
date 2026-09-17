#!/usr/bin/env python3
"""
jyotish/pdf_exporter.py
Publication-Grade Astrological PDF Report Generator for Astra.
Following Ernst Wilhelm's Kala Methodology:
- Tropical Rasis (Signs)
- Campanus House System
- Sidereal Equatorial Nakshatras (Dhruva Galactic Center at Middle of Mula)
- Swiss Ephemeris dynamic computation
"""

import os
import io
import datetime
from typing import Dict, Any, Optional, List
from playwright.sync_api import sync_playwright

from jyotish import draw_chart
from jyotish.relationships.relationships import SIGN_LORDS
from jyotish.planetary_evaluation import (
    calculate_baladi_avastha,
    classify_graha_quadrant,
    calculate_graha_vitality
)
from jyotish.planetary_evaluation.planetary_evaluation import get_dignity_score

# Standard Parashara Shadbala minimum benchmarks (in Virupas)
SHADBALA_REQUIRED = {
    "Sun": 390.0,
    "Moon": 360.0,
    "Mars": 300.0,
    "Mercury": 420.0,
    "Jupiter": 390.0,
    "Venus": 330.0,
    "Saturn": 300.0
}

VARGA_TITLES = {
    "D1": "D1 - Rāśi (Root Life)",
    "D9": "D9 - Navāṃśa (Dharma & Destiny)",
    "D10": "D10 - Daśāṃśa (Career & Karma)",
    "D7": "D7 - Saptāṃśa (Progeny & Partnerships)",
    "D2": "D2 - Horā (Wealth & Resources)",
    "D3": "D3 - Drekkāṇa (Siblings & Courage)",
    "D4": "D4 - Caturthāṃśa (Property & Fortune)",
    "D12": "D12 - Dvādaśāṃśa (Parents & Lineage)",
    "D16": "D16 - Ṣoḍaśāṃśa (Vehicles & Pleasures)",
    "D20": "D20 - Viṃśāṃśa (Spiritual Progress)",
    "D24": "D24 - Siddhāṃśa (Higher Learning & Intellect)",
    "D27": "D27 - Bhamśa (Strengths & Weaknesses)",
    "D30": "D30 - Triṃśāṃśa (Arishta & Misfortune)",
    "D40": "D40 - Khavedāṃśa (Auspicious Effects)",
    "D45": "D45 - Akṣavedāṃśa (General Well-being)",
    "D60": "D60 - Ṣaṣṭyāṃśa (Karmic Blueprint)"
}

ALL_VARGAS_ORDER = [
    "D1", "D2", "D3", "D4", "D7", "D9", "D10", "D12",
    "D16", "D20", "D24", "D27", "D30", "D40", "D45", "D60"
]

PLANETS_ORDER = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
CLASSICAL_PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]


def format_deg(val: Optional[float]) -> str:
    """Formats decimal degrees into clean DD° MM' SS\"."""
    if val is None:
        return "-"
    deg = int(val)
    rem = (val - deg) * 60.0
    mins = int(rem)
    secs = int(round((rem - mins) * 60.0))
    if secs >= 60:
        secs = 0
        mins += 1
    if mins >= 60:
        mins = 0
        deg += 1
    return f"{deg}° {mins:02d}' {secs:02d}\""


def format_deg_short(val: Optional[float]) -> str:
    """Formats decimal degrees into compact DD°MM'."""
    if val is None:
        return "-"
    deg = int(val)
    mins = int(round((val - deg) * 60.0))
    if mins >= 60:
        mins = 0
        deg += 1
    return f"{deg}°{mins:02d}'"


def dignity_badge(dignity_str: Optional[str]) -> str:
    """Returns styled HTML badge for planetary dignity."""
    if not dignity_str or dignity_str == "-":
        return '<span class="badge neutral">-</span>'
    d = dignity_str.lower()
    if "exalt" in d or "uccha" in d:
        return f'<span class="badge exalt">{dignity_str}</span>'
    if "moola" in d:
        return f'<span class="badge moola">{dignity_str}</span>'
    if "own" in d or "sva" in d:
        return f'<span class="badge own">{dignity_str}</span>'
    if "great friend" in d or "adhi mitra" in d:
        return f'<span class="badge great-friend">{dignity_str}</span>'
    if "friend" in d or "mitra" in d:
        return f'<span class="badge friend">{dignity_str}</span>'
    if "neutral" in d or "sama" in d:
        return f'<span class="badge neutral">{dignity_str}</span>'
    if "great enemy" in d or "adhi shatru" in d:
        return f'<span class="badge great-enemy">{dignity_str}</span>'
    if "enemy" in d or "shatru" in d:
        return f'<span class="badge enemy">{dignity_str}</span>'
    if "debilitat" in d or "neecha" in d:
        return f'<span class="badge debil">{dignity_str}</span>'
    return f'<span class="badge neutral">{dignity_str}</span>'


def lajjitadi_badge(state: str) -> str:
    """Returns styled HTML badge for Lajjitadi feeling states."""
    s = state.lower()
    if "proud" in s or "garvita" in s:
        return f'<span class="badge state-proud">{state}</span>'
    if "delight" in s or "mudita" in s:
        return f'<span class="badge state-delighted">{state}</span>'
    if "ashamed" in s or "lajjita" in s:
        return f'<span class="badge state-ashamed">{state}</span>'
    if "agitat" in s or "kshobhita" in s:
        return f'<span class="badge state-agitated">{state}</span>'
    if "starv" in s or "kshudhita" in s:
        return f'<span class="badge state-starved">{state}</span>'
    if "thirst" in s or "trushita" in s:
        return f'<span class="badge state-thirsty">{state}</span>'
    return f'<span class="badge neutral">{state}</span>'


def get_planet_glyph(p: str, notation: str = "symbol") -> str:
    """Returns planet glyph or formatted text representation."""
    if p in draw_chart.planet_notations:
        glyph = draw_chart.planet_notations[p].get(notation, p)
        return glyph
    return p


def get_chart_svg(
    varga_key: str,
    chart_data: Dict[str, Any],
    chart_style: str = "north",
    notation: str = "symbol",
    width: int = 330,
    height: int = 330,
    biwheel_outer: str = "D9"
) -> str:
    """Generates clean, embedded SVG string for a given varga."""
    v_data = chart_data.get("vargas", {}).get(varga_key)
    if not v_data and chart_style != "biwheel":
        return f"<div style='width:{width}px; height:{height}px; display:flex; align-items:center; justify-content:center; background:#f1f5f9; color:#64748b;'>{varga_key} Data Unavailable</div>"
    
    items = draw_chart.parse_varga_data(v_data) if v_data else []
    v_title = VARGA_TITLES.get(varga_key, varga_key)
    
    if chart_style == "south":
        svg = draw_chart.generate_south_indian(items, mode=notation, varga_name=v_title)
    elif chart_style == "circular":
        ayanamsa = chart_data.get("astronomy", {}).get("equatorial_ayanamsa_value", 0.0)
        svg = draw_chart.generate_circular_chart(items, mode=notation, varga_name=v_title, ayanamsha=ayanamsa)
    elif chart_style == "biwheel":
        inner_k = "D1"
        outer_k = biwheel_outer if varga_key == "D1" else varga_key
        inner_v = chart_data.get("vargas", {}).get(inner_k, {})
        outer_v = chart_data.get("vargas", {}).get(outer_k, chart_data.get("vargas", {}).get("D9", {}))
        inner_items = draw_chart.parse_varga_data(inner_v) if inner_v else []
        outer_items = draw_chart.parse_varga_data(outer_v) if outer_v else []
        ayanamsa = chart_data.get("astronomy", {}).get("equatorial_ayanamsa_value", 0.0)
        svg = draw_chart.generate_biwheel_chart(
            inner_items=inner_items,
            outer_items=outer_items,
            inner_name=inner_k,
            outer_name=outer_k,
            mode=notation,
            ayanamsha=ayanamsa,
            root_planet="Lagna"
        )
    else:
        svg = draw_chart.generate_north_indian(items, mode=notation, varga_name=v_title)
        
    svg_clean = svg.replace('width="100%"', f'width="{width}"').replace('height="100%"', f'height="{height}"')
    return svg_clean



def get_atmakaraka_info(chart_data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculates Atmakaraka (highest degree classical planet in D1) and its Karakamsa sign in D9."""
    d1_grahas = chart_data.get("vargas", {}).get("D1", {}).get("grahas", {})
    d9_grahas = chart_data.get("vargas", {}).get("D9", {}).get("grahas", {})
    
    degs = []
    for p in CLASSICAL_PLANETS:
        if p in d1_grahas:
            deg = d1_grahas[p].get("degree_0_to_30", 0.0)
            degs.append((p, deg))
            
    if not degs:
        return {"planet": "None", "d1_degree": 0.0, "karakamsa": "Unknown"}
        
    degs.sort(key=lambda x: x[1], reverse=True)
    ak_planet, ak_deg = degs[0]
    karakamsa_sign = d9_grahas.get(ak_planet, {}).get("sign", "Unknown") if ak_planet in d9_grahas else "Unknown"
    
    return {
        "planet": ak_planet,
        "d1_degree": ak_deg,
        "karakamsa": karakamsa_sign
    }


def get_vargottama_planets(chart_data: Dict[str, Any]) -> List[str]:
    """Finds planets occupying the identical sign in D1 and D9."""
    d1_grahas = chart_data.get("vargas", {}).get("D1", {}).get("grahas", {})
    d9_grahas = chart_data.get("vargas", {}).get("D9", {}).get("grahas", {})
    
    vargottama = []
    for p in PLANETS_ORDER:
        if p in d1_grahas and p in d9_grahas:
            if d1_grahas[p].get("sign") == d9_grahas[p].get("sign"):
                vargottama.append(p)
    return vargottama


def get_current_dasha_badge(chart_data: Dict[str, Any]) -> str:
    """Returns the current active Vimshottari Mahadasha / Antardasha string."""
    vd = chart_data.get("vimshottari_dasha", {})
    mds = vd.get("mahadashas", [])
    now = datetime.datetime.now()
    
    active_md = None
    active_ad = None
    
    for md in mds:
        try:
            s_date = datetime.datetime.strptime(md["start"].split()[0], "%Y-%m-%d")
            e_date = datetime.datetime.strptime(md["end"].split()[0], "%Y-%m-%d")
            if s_date <= now <= e_date:
                active_md = md
                for ad in md.get("antardashas", []):
                    ad_start_str = (ad.get("start_date") or ad.get("start", "")).split()[0]
                    ad_end_str = (ad.get("end_date") or ad.get("end", "")).split()[0]
                    if ad_start_str and ad_end_str:
                        ad_s = datetime.datetime.strptime(ad_start_str, "%Y-%m-%d")
                        ad_e = datetime.datetime.strptime(ad_end_str, "%Y-%m-%d")
                        if ad_s <= now <= ad_e:
                            active_ad = ad
                            break
                break
        except Exception:
            continue
            
    if active_md and active_ad:
        ad_lord = active_ad.get("antardasha_lord") or active_ad.get("period") or ""
        return f"{active_md['planet']} / {ad_lord}"
    elif active_md:
        return f"{active_md['planet']}"
    elif "at_birth" in vd:
        ab = vd["at_birth"]
        return f"{ab.get('mahadasha', '')} (Birth Balance: {ab.get('mahadasha_balance_years', 0):.1f} yrs)"
    return "Calculated"


def render_qualitative_avasthas_table(d1_grahas: Dict[str, Any], notation: str = "symbol") -> str:
    """Renders the software-identical unified Qualitative & Lajjitadi Avasthas table."""
    planets = CLASSICAL_PLANETS
    th_cols = []
    for p in planets:
        glyph = get_planet_glyph(p, notation)
        th_cols.append(f"<th style='color:#1a4a82; border:1px solid #dcb594; font-size:7.5pt; padding:2px 3px; background:#eee5d3;'>{glyph}<br><span style='font-size:6.2pt; color:#4a3325;'>{p[:2]}</span></th>")
    
    bala_cells = []
    for p in planets:
        av = d1_grahas.get(p, {}).get("avasthas", {}).get("bala", {})
        st = av.get("state", "-")
        val = av.get("strength", 0.0)
        pct = int(round(val * 100))
        st_clean = st.split()[0] if st != "-" else "-"
        col = "#16a34a" if val >= 1.0 else ("#d97706" if val >= 0.5 else ("#ea580c" if val > 0 else "#94a3b8"))
        bala_cells.append(f"<td style='padding:1.5px 2px; border:1px solid #e5dccb; background:#fffdfa;'><span style='font-weight:600; color:{col};'>{st_clean}</span><br><span style='font-size:5.8pt; color:#64748b;'>{pct}%</span></td>")
        
    jagrat_cells = []
    for p in planets:
        av = d1_grahas.get(p, {}).get("avasthas", {}).get("jagrat", {})
        st = av.get("state", "-")
        val = av.get("alertness", 0.0)
        pct = int(round(val * 100))
        st_clean = st.split()[0] if st != "-" else "-"
        col = "#16a34a" if val >= 1.0 else ("#d97706" if val >= 0.5 else "#94a3b8")
        jagrat_cells.append(f"<td style='padding:1.5px 2px; border:1px solid #e5dccb; background:#fffdfa;'><span style='font-weight:600; color:{col};'>{st_clean}</span><br><span style='font-size:5.8pt; color:#64748b;'>{pct}%</span></td>")
        
    deepti_cells = []
    for p in planets:
        av = d1_grahas.get(p, {}).get("avasthas", {}).get("deeptadi", {})
        st = av.get("state", "-")
        st_clean = st.split()[0] if st != "-" else "-"
        st_lower = st.lower()
        if any(x in st_lower for x in ["deepta", "swastha", "mudita", "shanta"]):
            col = "#16a34a"
        elif any(x in st_lower for x in ["kopa", "khala", "dukhita", "vikala"]):
            col = "#dc2626"
        else:
            col = "#475569"
        deepti_cells.append(f"<td style='padding:1.5px 2px; border:1px solid #e5dccb; background:#fffdfa;'><span style='font-weight:600; color:{col};'>{st_clean}</span></td>")
        
    lajjitadi_cells = []
    for p in planets:
        l_list = d1_grahas.get(p, {}).get("avasthas", {}).get("lajjitadi", [])
        if isinstance(l_list, list) and l_list:
            badges = []
            for item in l_list:
                st = item.get("state", "") if isinstance(item, dict) else str(item)
                st_short = st.split()[0]
                is_pos = any(x in st.lower() for x in ["proud", "garvita", "delight", "mudita"])
                badge_style = "background:#dcfce7; color:#166534;" if is_pos else "background:#fee2e2; color:#991b1b;"
                badges.append(f"<span style='display:inline-block; font-size:5.5pt; font-weight:600; padding:0.5px 2px; border-radius:2px; {badge_style}; margin:0.5px 0;'>{st_short}</span>")
            lajjitadi_cells.append(f"<td style='padding:1px 2px; border:1px solid #e5dccb; background:#fffdfa;'>{'<br>'.join(badges)}</td>")
        else:
            lajjitadi_cells.append("<td style='padding:1.5px 2px; border:1px solid #e5dccb; background:#fffdfa;'><span style='color:#94a3b8; font-size:6pt;'>Balanced</span></td>")
            
    return f"""
    <table class="dignity-grid avasthas-calc-table" style="width:100%; border-collapse:collapse; font-size:6.5pt; text-align:center;">
        <thead>
            <tr>
                <th style="text-align:left; min-width:85px; padding:2px 4px; background:#eee5d3; color:#4a3325; border:1px solid #dcb594;">Avastha</th>
                {''.join(th_cols)}
            </tr>
        </thead>
        <tbody>
            <tr>
                <td style="text-align:left; font-weight:bold; background:#fcfaf5; color:#4a3325; padding:1.5px 4px; border:1px solid #dcb594;">Bālādi (Vitality)</td>
                {''.join(bala_cells)}
            </tr>
            <tr>
                <td style="text-align:left; font-weight:bold; background:#fcfaf5; color:#4a3325; padding:1.5px 4px; border:1px solid #dcb594;">Jāgradādi (Alertness)</td>
                {''.join(jagrat_cells)}
            </tr>
            <tr>
                <td style="text-align:left; font-weight:bold; background:#fcfaf5; color:#4a3325; padding:1.5px 4px; border:1px solid #dcb594;">Dīptādi (Mood)</td>
                {''.join(deepti_cells)}
            </tr>
            <tr>
                <td style="text-align:left; font-weight:bold; background:#fcfaf5; color:#4a3325; padding:1.5px 4px; border:1px solid #dcb594;">Lajjitādi (Feelings)</td>
                {''.join(lajjitadi_cells)}
            </tr>
        </tbody>
    </table>
    """


def render_shadbala_breakdown_table(shadbala_data: Dict[str, Any], notation: str = "symbol") -> str:
    """Renders the comprehensive 25-row Kala-style Shadbala Breakdown Grid."""
    planets = CLASSICAL_PLANETS
    th_cols = []
    for p in planets:
        glyph = get_planet_glyph(p, notation)
        th_cols.append(f"<th style='color:#1a4a82; border:1px solid #dcb594; font-size:7.5pt; padding:1.5px 2px; background:#eee5d3;'>{glyph}<br><span style='font-size:6.2pt; color:#4a3325;'>{p[:2]}</span></th>")
        
    rows_def = [
        {"type": "header", "title": "Sthāna Bala (Positional Strength)"},
        {"label": "Uccha Bala", "key": "Uccha_Bala", "decimals": 2},
        {"label": "Saptavargaja Bala", "key": "Saptavarga_Bala", "decimals": 0},
        {"label": "Ojhayugmarasyamsa", "key": "Ojhayugma_Bala", "decimals": 0},
        {"label": "Kendrādi Bala", "key": "Kendradi_Bala", "decimals": 0},
        {"label": "Drekkāṇa Bala", "key": "Drekkana_Bala", "decimals": 0},
        {"label": "Total Sthāna Bala", "key": "Sthana_Bala", "decimals": 1, "isSubtotal": True},
        {"label": "Required Sthāna Bala", "key": "Required_Sthana", "decimals": 0, "isRequired": True},
        {"label": "% of Required Sthāna", "key": "Pct_Required_Sthana", "decimals": 1, "isPct": True},
        {"type": "header", "title": "Dig Bala (Directional Strength)"},
        {"label": "Total Dig Bala", "key": "Dig_Bala", "decimals": 2, "isSubtotal": True},
        {"label": "Required Dig Bala", "key": "Required_Dig", "decimals": 0, "isRequired": True},
        {"label": "% of Required Dig", "key": "Pct_Required_Dig", "decimals": 1, "isPct": True},
        {"type": "header", "title": "Kāla Bala (Temporal Strength)"},
        {"label": "Natonnata Bala", "key": "Natonnata_Bala", "decimals": 2},
        {"label": "Pakṣa Bala", "key": "Paksha_Bala", "decimals": 2},
        {"label": "Tribhāga Bala", "key": "Tribhaga_Bala", "decimals": 0},
        {"label": "Varṣa Bala", "key": "Varsha_Bala", "decimals": 0},
        {"label": "Māsa Bala", "key": "Masa_Bala", "decimals": 0},
        {"label": "Dina Bala", "key": "Dina_Bala", "decimals": 0},
        {"label": "Horā Bala", "key": "Hora_Bala", "decimals": 0},
        {"label": "Total Kāla Bala", "key": "Kala_Bala", "decimals": 1, "isSubtotal": True},
        {"label": "Required Kāla Bala", "key": "Required_Kaala", "decimals": 0, "isRequired": True},
        {"label": "% of Required Kāla", "key": "Pct_Required_Kaala", "decimals": 1, "isPct": True},
        {"type": "header", "title": "Ayana Bala (Declination Strength)"},
        {"label": "Total Ayana Bala", "key": "Ayana_Bala", "decimals": 2, "isSubtotal": True},
        {"label": "Required Ayana Bala", "key": "Required_Ayana", "decimals": 0, "isRequired": True},
        {"label": "% of Required Ayana", "key": "Pct_Required_Ayana", "decimals": 1, "isPct": True},
        {"type": "header", "title": "Cheṣṭā Bala (Motional Strength)"},
        {"label": "Total Cheṣṭā Bala", "key": "Cheshta_Bala", "decimals": 2, "isSubtotal": True},
        {"label": "Required Cheṣṭā Bala", "key": "Required_Cheshta", "decimals": 0, "isRequired": True},
        {"label": "% of Required Cheṣṭā", "key": "Pct_Required_Cheshta", "decimals": 1, "isPct": True},
        {"type": "header", "title": "Other Balas"},
        {"label": "Naisargika Bala", "key": "Naisargika_Bala", "decimals": 2},
        {"label": "Dṛk Bala", "key": "Drik_Bala", "decimals": 1},
        {"label": "Yuddha Bala", "key": "Yuddha_Bala", "decimals": 0},
        {"type": "header", "title": "Summary & Rankings"},
        {"label": "Ṣaḍbala Total (Virūpas)", "key": "Total_Virupas", "decimals": 1, "isGrandTotal": True},
        {"label": "Required Ṣaḍbala", "key": "Required_Total", "decimals": 0, "isRequired": True},
        {"label": "% of Required Ṣaḍbala", "key": "Pct_Required_Total", "decimals": 1, "isPct": True},
        {"label": "Ṣaḍbala in Rūpas", "key": "Total_Rupas", "decimals": 2, "isGrandTotal": True},
        {"label": "Relative Rank", "key": "Relative_Rank", "decimals": 0, "isRank": True}
    ]
    tbody_trs = []
    for r in rows_def:
        if r.get("type") == "header":
            tbody_trs.append(f'<tr class="category-header"><td colspan="8" style="background:#f2e8d8; color:#5c3d28; font-weight:bold; text-transform:uppercase; font-size:6pt; letter-spacing:0.4px; padding:1.2px 3px; border:1px solid #dcb594; text-align:left;">{r["title"]}</td></tr>')
            continue
        is_sub = r.get("isSubtotal", False)
        is_grand = r.get("isGrandTotal", False)
        bg = "#ebdcc4" if is_grand else ("#f5ece0" if is_sub else "#fffdfa")
        bdr = "border-top:2px solid #c8ab8d; border-bottom:2px solid #c8ab8d;" if is_grand else ("border-top:1px solid #dcb594; border-bottom:1px solid #dcb594;" if is_sub else "border:1px solid #e5dccb;")
        lbl = r["label"]
        td_lbl = f'<td style="text-align:left; font-weight:{"bold" if (is_sub or is_grand) else "500"}; background:#fcfaf5; color:#4a3325; padding:1px 3px; border:1px solid #dcb594;">{lbl}</td>'
        val_tds = []
        for p in planets:
            p_data = shadbala_data.get(p, {})
            val = p_data.get(r["key"])
            if val is None:
                val_tds.append(f'<td style="padding:1px 2.5px; text-align:right; background:{bg}; {bdr}">-</td>')
            elif r.get("isPct"):
                num = float(val)
                col = "#27ae60" if num >= 100.0 else "#c0392b"
                val_tds.append(f'<td style="padding:1px 2.5px; text-align:right; background:{bg}; {bdr}"><span style="color:{col}; font-weight:bold;">{num:.{r["decimals"]}f}%</span></td>')
            elif r.get("isRank"):
                num = int(val)
                val_tds.append(f'<td style="padding:1px 2.5px; text-align:right; background:{bg}; {bdr}"><span style="color:#d35400; font-weight:bold;">#{num}</span></td>')
            else:
                num = float(val)
                bold_style = ' font-weight:bold;' if (is_sub or is_grand) else ''
                val_tds.append(f'<td style="padding:1px 2.5px; text-align:right; background:{bg}; {bdr}{bold_style}">{num:.{r["decimals"]}f}</td>')
        tbody_trs.append(f'<tr>{td_lbl}{"".join(val_tds)}</tr>')
    return f"""
    <table class="shadbala-breakdown-grid" style="width:100%; border-collapse:separate; border-spacing:0; font-size:6.1pt; line-height:1.15;">
        <thead>
            <tr>
                <th style="text-align:left; min-width:110px; padding:1.5px 3px; background:#eee5d3; color:#4a3325; border:1px solid #dcb594;">Strength Component</th>
                {''.join(th_cols)}
            </tr>
        </thead>
        <tbody>
            {''.join(tbody_trs)}
        </tbody>
    </table>
    """


def render_yoga_judgment_table(shadbala_data: Dict[str, Any], notation: str = "symbol") -> str:
    """Renders the Kala Yoga Judgment / Strengths Matrix table."""
    planets = CLASSICAL_PLANETS
    th_cols = []
    for p in planets:
        glyph = get_planet_glyph(p, notation)
        th_cols.append(f"<th style='color:#1a4a82; border-right:1px solid #b86829; font-size:7.5pt; padding:1.5px 2px;'>{glyph}<br><span style='font-size:6.2pt; color:#4a3325;'>{p[:2]}</span></th>")
    th_cols.append("<th style='color:#1a4a82; font-size:7pt; font-weight:bold; padding:1.5px 3px;'>Avg.</th>")
    row_data = {
        'I': [], 'K': [], 'S': [], 'A': [], 'SD': [], 'AD': [],
        '+': [], '-': [], 'IxSxSD': [], 'KxAxAD': [], 'Uccha': [], 'Cheshta': []
    }
    for p in planets:
        p_data = shadbala_data.get(p, {})
        uccha = float(p_data.get("Uccha_Bala", 0.0))
        cheshta = float(p_data.get("Cheshta_Bala", 0.0))
        ishta = float(p_data.get("Ishta_Phala", (uccha + cheshta) / 2.0))
        kashta = float(p_data.get("Kashta_Phala", 60.0 - ishta))
        subha = float(p_data.get("Subha_Phala", 0.0))
        asubha = float(p_data.get("Asubha_Phala", 60.0 - subha))
        sd = float(p_data.get("Dig_Bala", 0.0))
        ad = max(0.0, 60.0 - sd)
        plus = ishta + subha + sd
        minus = kashta + asubha + ad
        ix_sx_sd = (ishta * subha * sd) / 3600.0
        kx_ax_ad = (kashta * asubha * ad) / 3600.0
        row_data['I'].append(ishta)
        row_data['K'].append(kashta)
        row_data['S'].append(subha)
        row_data['A'].append(asubha)
        row_data['SD'].append(sd)
        row_data['AD'].append(ad)
        row_data['+'].append(plus)
        row_data['-'].append(minus)
        row_data['IxSxSD'].append(ix_sx_sd)
        row_data['KxAxAD'].append(kx_ax_ad)
        row_data['Uccha'].append(uccha)
        row_data['Cheshta'].append(cheshta)
    sections = [
        {"title": "Ishta and Kashta", "rows": [{"key": "I", "label": "I (Ishta)", "isNeg": False}, {"key": "K", "label": "K (Kashta)", "isNeg": True}]},
        {"title": "Subha and Asubha", "rows": [{"key": "S", "label": "S (Subha)", "isNeg": False}, {"key": "A", "label": "A (Asubha)", "isNeg": True}]},
        {"title": "Subha and Asubha Dig Bala", "rows": [
            {"key": "SD", "label": "SD (Subha Dig)", "isNeg": False},
            {"key": "AD", "label": "AD (Asubha Dig)", "isNeg": True},
            {"key": "+", "label": "+ (Total Ausp.)", "isNeg": False, "isBold": True},
            {"key": "-", "label": "- (Total Inausp.)", "isNeg": True, "isBold": True},
            {"key": "IxSxSD", "label": "IxSxSD (Impact)", "isNeg": False},
            {"key": "KxAxAD", "label": "KxAxAD (Impact)", "isNeg": True},
            {"key": "Uccha", "label": "Uccha Bala", "isNeg": False},
            {"key": "Cheshta", "label": "Cheṣṭā Bala", "isNeg": False}
        ]}
    ]
    tbody_trs = []
    for sec in sections:
        tbody_trs.append(f'<tr class="sec-header"><td colspan="9" style="background:#f2e8d8; color:#5c3d28; font-weight:bold; text-transform:uppercase; font-size:5.8pt; padding:1.2px 3px; border:1px solid #dcb594; text-align:left;">{sec["title"]}</td></tr>')
        for r in sec["rows"]:
            is_neg = r["isNeg"]
            is_bold = r.get("isBold", False)
            val_col = "#c0392b" if is_neg else "#27ae60"
            if r["key"] in ["Uccha", "Cheshta"]:
                val_col = "#334155"
            vals = row_data[r["key"]]
            avg_val = sum(vals) / len(vals) if vals else 0.0
            cells = []
            for v in vals:
                b_str = "font-weight:bold;" if is_bold else ""
                cells.append(f'<td style="color:{val_col}; padding:0.8px 2px; text-align:center; border:1px solid #e5dccb; background:#fffdfa;{b_str}">{v:.1f}</td>')
            avg_b_str = "font-weight:bold;" if is_bold else "font-weight:600;"
            cells.append(f'<td style="color:{val_col}; padding:0.8px 2px; text-align:center; border:1px solid #b86829; background:#fcfaf5;{avg_b_str}">{avg_val:.1f}</td>')
            td_lbl = f'<td style="text-align:left; font-weight:bold; background:#fcfaf5; color:#4a3325; padding:0.8px 3px; border:1px solid #dcb594; font-size:6pt;">{r["label"]}</td>'
            tbody_trs.append(f'<tr>{td_lbl}{"".join(cells)}</tr>')
    return f"""
    <table class="yoga-judgment-table" style="width:100%; border-collapse:collapse; border:2px solid #b86829; font-size:6.1pt; line-height:1.15; background:#ffffff;">
        <thead>
            <tr style="border-bottom:2px solid #b86829; background:#fffdfa;">
                <th style="border-right:1px solid #b86829; width:65px; padding:1.5px 3px; text-align:left; color:#4a3325;">Balas</th>
                {''.join(th_cols)}
            </tr>
        </thead>
        <tbody>
            {''.join(tbody_trs)}
        </tbody>
    </table>
    """


def render_classical_yogas_section(yogas_data: Dict[str, Any], notation: str = "symbol") -> str:
    """Renders the Classical Yogas and Yoga Bhanga (Cancellation & Breaker) Audit table."""
    if not yogas_data or not yogas_data.get("yogas"):
        return ""
        
    yogas = yogas_data.get("yogas", [])
    summary = yogas_data.get("summary", {})
    
    rows = []
    for y in yogas:
        status_str = y.get("status", "Pure & Eminent")
        score = float(y.get("plausibility_score", 0.0))
        
        if "Pure" in status_str:
            badge_cls = "yoga-pure"
            bar_color = "#15803d"
        elif "Stained" in status_str:
            badge_cls = "yoga-stained"
            bar_color = "#b45309"
        elif "Rescued" in status_str:
            badge_cls = "yoga-rescued"
            bar_color = "#4338ca"
        else:
            badge_cls = "yoga-broken"
            bar_color = "#991b1b"
            
        planets = y.get("participating_planets", [])
        planet_spans = " ".join([f'<span class="planet-badge">{get_planet_glyph(p, notation)} {p}</span>' for p in planets])
        
        houses = y.get("participating_houses", [])
        houses_str = ", ".join([f"H{h}" for h in houses if h > 0]) or "-"
        
        breakers = y.get("breakers", [])
        breaker_items = []
        for b in breakers:
            factor = b.get("factor", "")
            penalty = b.get("penalty", 0.0)
            desc = b.get("description", "")
            breaker_items.append(f'<div class="yoga-breaker-item"><strong>⚠️ {factor} (-{penalty:.0f}%):</strong> {desc}</div>')
        breaker_html = "".join(breaker_items) if breaker_items else '<span style="color:#15803d; font-size:6.5pt; font-weight:600;">✓ Pristine • Zero Saboteurs</span>'
        
        pos_factors = y.get("positive_factors", [])
        pos_html = "".join([f'<div class="yoga-pos-item">✓ {pf}</div>' for pf in pos_factors[:2]]) if pos_factors else ''
        
        effects = y.get("manifestation_effects", [])
        effects_str = " ".join(effects[:2]) if effects else y.get("archetype", "")
        
        rows.append(f"""
        <tr>
            <td style="font-weight:700; color:#4a3325;">
                <div style="font-size:7.5pt;">{y.get('name', '-')}</div>
                <div style="font-size:6pt; color:#7c6853;">{y.get('category', '-')} • {y.get('scripture_ref', '')}</div>
            </td>
            <td><span class="badge {badge_cls}">{status_str}</span></td>
            <td>
                <div style="display:flex; align-items:center; gap:4px;">
                    <div class="prog-bar" style="width:34px;"><span class="prog-fill" style="width:{score}%; background:{bar_color};"></span></div>
                    <strong class="mono" style="font-size:7pt; color:{bar_color};">{score:.1f}%</strong>
                </div>
            </td>
            <td>{planet_spans}<br><span style="font-size:6.2pt; color:#64748b;">Houses: {houses_str}</span></td>
            <td style="font-size:6.8pt; line-height:1.25; color:#334155;">
                <div style="font-weight:600; color:#1e293b; margin-bottom:2px;">{y.get('archetype', '')}</div>
                <div style="color:#475569;">{effects_str}</div>
                {pos_html}
            </td>
            <td style="font-size:6.3pt; line-height:1.2;">
                {breaker_html}
            </td>
        </tr>
        """)
        
    return f"""
    <div class="card full-width" style="margin-top:6px;">
        <div class="card-header">
            <h3>👑 Classical Yogas & Yoga Bhanga (Cancellation & Breaker) Audit</h3>
            <span class="card-sub">
                Total: {yogas_data.get('total_count', len(yogas))} • 
                <span class="badge yoga-pure" style="margin:0 2px;">Pure: {summary.get('pure', 0)}</span>
                <span class="badge yoga-stained" style="margin:0 2px;">Stained: {summary.get('stained', 0)}</span>
                <span class="badge yoga-rescued" style="margin:0 2px;">Rescued: {summary.get('rescued', 0)}</span>
                <span class="badge yoga-broken" style="margin:0 2px;">Broken: {summary.get('broken', 0)}</span>
            </span>
        </div>
        <div class="card-body">
            <table class="data-table" style="font-size:7pt;">
                <thead>
                    <tr>
                        <th style="width:18%;">Yoga Combination & Source</th>
                        <th style="width:12%;">Status</th>
                        <th style="width:10%;">Plausibility</th>
                        <th style="width:14%;">Grahas & Houses</th>
                        <th style="width:26%;">Archetype & Worldly Manifestation</th>
                        <th style="width:20%;">Yoga Breaker (Bhanga) Audit</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(rows)}
                </tbody>
            </table>
        </div>
    </div>
    """


SIGNS_LIST = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
GRAHA_GLYPHS_MAP = {
    'Lagna': '🌅', 'Sun': '☉', 'Moon': '☽', 'Mars': '♂',
    'Mercury': '☿', 'Jupiter': '♃', 'Venus': '♀', 'Saturn': '♄',
    'Rahu': '☊', 'Ketu': '☋'
}


def get_campanus_house_num(planet_name: str, default_house: int, bhavas: list) -> int:
    """Finds the Campanus house number for a planet or Lagna from bhavas list."""
    if not bhavas:
        return default_house
    for b in bhavas:
        pls = b.get("planets", [])
        if planet_name in pls or (planet_name == "Lagna" and "Asc" in pls):
            return b.get("house", default_house)
    return default_house


def render_harmonic_biwheel_section(
    chart_data: Dict[str, Any],
    outer_varga: str = "D9",
    notation: str = "symbol",
    svg_size: int = 355
) -> str:
    """
    Renders the dedicated Harmonic Bi-Wheel Architecture section.
    Displays:
    1. Concentric dual-wheel vector SVG (D1 Natal + Outer Varga).
    2. Interactive visual reading key decoding the concentric rings and golden Vargottama rays.
    3. Harmonic Cross-Chart Alignment Matrix (Lagna + 9 Grahas with Natal placement,
       harmonic divisional degree, sector slice/pada, whole-sign overlay bhava, and dignity badge).
    4. Subtle Soul Destiny & Vargottama Fortification Synthesis (Swāṃśa, Kārakāṃśa, Vargottama stability).
    5. Kala Epistemological Principle explaining concentric harmonic frequencies in plain English.
    """
    inner_k = "D1"
    outer_k = outer_varga or "D9"
    outer_title = VARGA_TITLES.get(outer_k, f"{outer_k} Harmonic Chart")
    
    inner_v = chart_data.get("vargas", {}).get(inner_k, {})
    outer_v = chart_data.get("vargas", {}).get(outer_k, {})
    
    inner_items = draw_chart.parse_varga_data(inner_v) if inner_v else []
    outer_items = draw_chart.parse_varga_data(outer_v) if outer_v else []
    ayanamsa = chart_data.get("astronomy", {}).get("equatorial_ayanamsa_value", 0.0)
    
    biwheel_svg_raw = draw_chart.generate_biwheel_chart(
        inner_items=inner_items,
        outer_items=outer_items,
        inner_name=inner_k,
        outer_name=outer_k,
        mode=notation,
        ayanamsha=ayanamsa,
        root_planet="Lagna"
    )
    biwheel_svg_clean = biwheel_svg_raw.replace('width="100%"', f'width="{svg_size}"').replace('height="100%"', f'height="{svg_size}"')
    
    harmonic_map = {
        "D1": 1, "D2": 2, "D3": 3, "D4": 4, "D7": 7, "D9": 9, "D10": 10,
        "D12": 12, "D16": 16, "D20": 20, "D24": 24, "D27": 27, "D30": 30,
        "D40": 40, "D45": 45, "D60": 60
    }
    harmonic_n = harmonic_map.get(outer_k, 9)
    if outer_k.startswith("D") and outer_k[1:].isdigit():
        harmonic_n = int(outer_k[1:])
    slice_span = 30.0 / harmonic_n
    
    d1_lagna = inner_v.get("lagna", {})
    d1_lagna_sign = d1_lagna.get("sign", "Aries")
    d1_lagna_idx = SIGNS_LIST.index(d1_lagna_sign) if d1_lagna_sign in SIGNS_LIST else 0
    bhavas = inner_v.get("bhavas", [])
    
    d1_grahas = inner_v.get("grahas", {})
    out_grahas = outer_v.get("grahas", {})
    out_lagna = outer_v.get("lagna", {})
    
    vargottamas = get_vargottama_planets(chart_data) if outer_k == "D9" else [p for p in PLANETS_ORDER if d1_grahas.get(p, {}).get("sign") == out_grahas.get(p, {}).get("sign")]
    ak_info = get_atmakaraka_info(chart_data)
    
    rows_html = []
    
    # 1. Lagna row
    if d1_lagna and d1_lagna.get("sign"):
        in_s = d1_lagna.get("sign", "-")
        in_d = d1_lagna.get("degree_0_to_30", 0.0)
        out_s = out_lagna.get("sign", "-")
        out_d = out_lagna.get("degree_0_to_30", 0.0)
        is_varg = (in_s == out_s and in_s != "-")
        pada_idx = min(harmonic_n, max(1, int(in_d / slice_span) + 1))
        out_s_idx = SIGNS_LIST.index(out_s) if out_s in SIGNS_LIST else 0
        overlay_house = ((out_s_idx - d1_lagna_idx + 12) % 12) + 1
        
        varg_badge = '<span class="badge" style="background:#fef3c7; color:#92400e; border:1px solid #f59e0b; font-weight:700;">🌟 Vargottama</span>' if is_varg else '<span class="badge badge-neutral">Swāṃśa</span>'
        
        rows_html.append(f"""
        <tr style="background:#fcf8f2; font-weight:600;">
            <td><strong>Asc Lagna</strong></td>
            <td><strong>{in_s}</strong> <span class="mono">{format_deg_short(in_d)}</span> <span class="badge badge-neutral" style="font-size:6pt;">H1</span></td>
            <td><strong>{out_s}</strong> <span class="mono">{format_deg_short(out_d)}</span></td>
            <td>Pāda {pada_idx}/{harmonic_n}</td>
            <td>Bhava {overlay_house}</td>
            <td>{varg_badge}</td>
        </tr>
        """)
        
    for p in PLANETS_ORDER:
        if p not in d1_grahas:
            continue
        g_in = d1_grahas[p]
        g_out = out_grahas.get(p, {})
        glyph = get_planet_glyph(p, notation)
        
        in_s = g_in.get("sign", "-")
        in_d = g_in.get("degree_0_to_30", 0.0)
        out_s = g_out.get("sign", "-")
        out_d = g_out.get("degree_0_to_30", 0.0)
        
        in_s_idx = SIGNS_LIST.index(in_s) if in_s in SIGNS_LIST else 0
        w_house = ((in_s_idx - d1_lagna_idx + 12) % 12) + 1
        c_house = get_campanus_house_num(p, w_house, bhavas)
        
        pada_idx = min(harmonic_n, max(1, int(in_d / slice_span) + 1))
        out_s_idx = SIGNS_LIST.index(out_s) if out_s in SIGNS_LIST else 0
        overlay_house = ((out_s_idx - d1_lagna_idx + 12) % 12) + 1
        
        is_varg = (in_s == out_s and in_s != "-")
        out_dig = g_out.get("dignity_breakdown", {}).get("final_dignity", g_out.get("dignity", "-"))
        
        if is_varg:
            varg_badge = '<span class="badge" style="background:#fef3c7; color:#92400e; border:1px solid #f59e0b; font-weight:700;">🌟 Vargottama</span>'
        else:
            varg_badge = dignity_badge(out_dig)
            
        rows_html.append(f"""
        <tr>
            <td>{glyph} {p}</td>
            <td>{in_s} <span class="mono">{format_deg_short(in_d)}</span> <span class="badge badge-neutral" style="font-size:6pt;">H{c_house}</span></td>
            <td><strong>{out_s}</strong> <span class="mono">{format_deg_short(out_d)}</span></td>
            <td>Pāda {pada_idx}/{harmonic_n}</td>
            <td>Bhava {overlay_house}</td>
            <td>{varg_badge}</td>
        </tr>
        """)
        
    varg_str = ", ".join(vargottamas) if vargottamas else "None"
    ak_planet = ak_info.get("planet", "-")
    ak_sign = ak_info.get("karakamsa", "-")
    d9_lagna_sign = out_lagna.get("sign", "-")
    d9_lagna_lord = SIGN_LORDS.get(d9_lagna_sign, "-")
    
    html = f"""
    <div class="layout-2col" style="align-items: stretch; margin-bottom: 8px;">
        <!-- COLUMN 1: BI-WHEEL SVG & LEGEND -->
        <div class="column" style="display: flex; flex-direction: column; gap: 6px;">
            <div class="card chart-card" style="padding: 6px; display: flex; justify-content: center; align-items: center; background: #ffffff;">
                <div style="width:{svg_size}px; height:{svg_size}px; display:flex; align-items:center; justify-content:center;">
                    {biwheel_svg_clean}
                </div>
            </div>
            <div class="key-card" style="font-size: 6.8pt; line-height: 1.35; padding: 6px 10px; background: #fdfbf7; border: 1px solid #e5dccb;">
                <div style="font-weight: 700; color: #4a3325; margin-bottom: 3px; font-size: 7.2pt; display: flex; justify-content: space-between;">
                    <span>Concentric Dual-Wheel Visual Reading Key</span>
                    <span style="color:#d35400;">{inner_k} (Inner) ➔ {outer_k} (Outer)</span>
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 4px;">
                    <div><strong style="color: #795548;">• Inner Ring (r=62–138):</strong> Root Physical Chart (D1 Rāśi) • Signs, Planets & Campanus Cusps</div>
                    <div><strong style="color: #27ae60;">• Middle Ring (r=138–164):</strong> 30° Sign Subdivided into {harmonic_n} Harmonic Slices (Signs)</div>
                    <div><strong style="color: #2980b9;">• Outer Ring (r=164–206):</strong> Subtle Soul Destiny ({outer_k}) • Radially Anchored Planets</div>
                    <div><strong style="color: #d4ac0d;">• Golden Rays (🌟):</strong> Radiant Vargottama Alignment (Identical Sign in Root & Soul)</div>
                </div>
            </div>
        </div>

        <!-- COLUMN 2: ALIGNMENT MATRIX & METHODOLOGY -->
        <div class="column" style="display: flex; flex-direction: column; gap: 6px;">
            <!-- Harmonic Alignment Table -->
            <div class="card">
                <div class="card-header">
                    <h3>🏛️ Harmonic Alignment Matrix</h3>
                    <span class="card-sub">{inner_k} Physical ➔ {outer_k} Harmonic Projections</span>
                </div>
                <div class="card-body">
                    <table class="data-table compact">
                        <thead>
                            <tr>
                                <th>Graha</th>
                                <th>D1 Physical</th>
                                <th>{outer_k} Harmonic</th>
                                <th>Sector</th>
                                <th>Overlay</th>
                                <th>Fortification</th>
                            </tr>
                        </thead>
                        <tbody>
                            {''.join(rows_html)}
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Subtle Soul Destiny & Vargottama Synthesis Card -->
            <div class="card">
                <div class="card-header">
                    <h3>🌟 Subtle Soul Destiny & Vargottama Synthesis</h3>
                    <span class="card-sub">Higher Consciousness Architecture</span>
                </div>
                <div class="card-body" style="padding: 6px 8px; font-size: 7pt; line-height: 1.35; color: #4a3325;">
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 6px; margin-bottom: 4px;">
                        <div style="background: #fdfbf7; padding: 4px 6px; border-radius: 4px; border: 1px solid #ebd9c8;">
                            <strong>Swāṃśa (Soul Sign):</strong> {d9_lagna_sign} (Lord: <em>{d9_lagna_lord}</em>)<br>
                            <span style="color: #64748b; font-size: 6.5pt;">The fundamental character, core archetype, and instinctive dharma of the soul.</span>
                        </div>
                        <div style="background: #fdfbf7; padding: 4px 6px; border-radius: 4px; border: 1px solid #ebd9c8;">
                            <strong>Kārakāṃśa (Soul Mission):</strong> {ak_sign} (AK: <em>{ak_planet}</em>)<br>
                            <span style="color: #64748b; font-size: 6.5pt;">The ultimate lesson and evolutionary ambition chosen by the Ātman (soul) in this life.</span>
                        </div>
                    </div>
                    <div style="background: #fdfbf7; padding: 4px 6px; border-radius: 4px; border: 1px solid #ebd9c8;">
                        <strong>Vargottama Grahas:</strong> <span style="font-weight: 700; color: #b45309;">{varg_str}</span><br>
                        <span style="color: #64748b; font-size: 6.5pt;">Planets occupying the identical sign in both the root tree (D1) and fruit (D9). They possess exceptional mental stability, unyielding focus, and the power to effortlessly convert inner intentions into tangible physical results.</span>
                    </div>
                </div>
            </div>

            <!-- Pedagogical Explanation Card -->
            <div class="key-card" style="padding: 6px 8px; font-size: 6.8pt; line-height: 1.35; background: #faf6f0; border-left: 3px solid #d35400;">
                <strong style="color: #d35400;">📖 Kala Integrated Methodology • Why a Concentric Bi-Wheel?</strong>
                <p style="margin: 2px 0 0 0; color: #4a3325;">
                    In Ernst Wilhelm's Kala methodology, divisional charts (Vargas) are harmonic frequencies rather than separate skies. The inner wheel is the <em>tree trunk</em> (physical body, immediate environment, and action). The outer wheel is the <em>subtle fruit</em> ({outer_k}), revealing what that tree actually yields in character, relationships, and soul destiny. Dividing each 30° Tropical sign into exact harmonic segments reveals how physical actions crystallize into spiritual destiny.
                </p>
            </div>
        </div>
    </div>
    """
    return html


def render_lagna_vitality_card(chart_data: Dict[str, Any], varga: str = "D1") -> str:
    """Renders the executive Lagna Vitality Architecture card with 5-pillar composite scoring."""
    v_data = chart_data.get("vargas", {}).get(varga, chart_data.get("vargas", {}).get("D1", {}))
    v_lagna = v_data.get("lagna", {})
    lg_sign = v_lagna.get("sign", "-")
    lg_deg = v_lagna.get("degree_0_to_30", 0.0)
    lg_lord = SIGN_LORDS.get(lg_sign, v_lagna.get("lord", "-"))
    
    naks = chart_data.get("nakshatras", {}).get("grahas", {})
    lg_nak = naks.get("Lagna", {})
    nak_str = f"{lg_nak.get('nakshatra', '-')} (Pada {lg_nak.get('pada', '-')})" if lg_nak else "-"
    
    pe = chart_data.get("planetary_evaluation", {})
    lagna_eval = pe.get("lagna_evaluation", {}) if varga == "D1" else {}
    
    vit_score = lagna_eval.get("vitality_score", 5.0)
    vit_tier = lagna_eval.get("vitality_tier", "Capable Vessel")
    archetype = lagna_eval.get("archetype", "The Steady Navigator")
    verdict = lagna_eval.get("verdict", "Sound, capable engine; actualizes chart potentials through deliberate effort.")
    pillar_scores = lagna_eval.get("pillar_scores", {})
    audit_trail = lagna_eval.get("audit_trail", {})
    
    # Tier colors
    if vit_score >= 8.8:
        t_bg = "#ecfdf5"; t_col = "#065f46"; t_bdr = "#34d399"
    elif vit_score >= 7.0:
        t_bg = "#f0fdf4"; t_col = "#15803d"; t_bdr = "#86efac"
    elif vit_score >= 5.5:
        t_bg = "#eff6ff"; t_col = "#1d4ed8"; t_bdr = "#93c5fd"
    elif vit_score >= 4.0:
        t_bg = "#fffbeb"; t_col = "#b45309"; t_bdr = "#fcd34d"
    else:
        t_bg = "#fef2f2"; t_col = "#b91c1c"; t_bdr = "#fca5a5"
        
    p1 = pillar_scores.get("pillar_1_captain", 0.0)
    p2 = pillar_scores.get("pillar_2_field", 0.0)
    p3 = pillar_scores.get("pillar_3_occupants", 0.0)
    p4 = pillar_scores.get("pillar_4_skylight", 0.0)
    p5 = pillar_scores.get("pillar_5_enclosure", 0.0)
    
    p1_items = audit_trail.get("p1_captain", ["Captain evaluation baseline"])[:2]
    p2_items = audit_trail.get("p2_field", ["Field evaluation baseline"])[:2]
    p3_items = audit_trail.get("p3_occupants", ["Occupants evaluation baseline"])[:1]
    p4_items = audit_trail.get("p4_skylight", ["Sky-light evaluation baseline"])[:2]
    p5_items = audit_trail.get("p5_enclosure", ["Enclosure evaluation baseline"])[:1]

    def fmt_pts(val):
        return f"+{val:.2f}" if val > 0 else f"{val:.2f}"

    return f"""
    <div class="card" style="margin-bottom:8px; border:1.5px solid #dcb594; background:#fffdfa;">
        <div class="card-header" style="background:#f5ece0; padding:5px 10px; display:flex; justify-content:space-between; align-items:center;">
            <div style="display:flex; align-items:center; gap:8px;">
                <span style="font-size:14pt;">🌅</span>
                <div>
                    <h3 style="font-size:9pt; margin:0; color:#4a3325;">Lagna (Ascendant / Tanū Bhāva) • Horizon Vitality Architecture</h3>
                    <span style="font-size:6.8pt; color:#7c6853;">Rising Sign: <strong>{lg_sign} {format_deg_short(lg_deg)}</strong> • Lagneśa: <strong>{lg_lord}</strong> • Nakshatra: <strong>{nak_str}</strong></span>
                </div>
            </div>
            <div style="display:flex; align-items:center; gap:8px;">
                <span style="background:{t_bg}; color:{t_col}; border:1.5px solid {t_bdr}; padding:3px 10px; border-radius:4px; font-weight:bold; font-size:9.5pt;">
                    ★ {vit_score:.1f} / 10 • {vit_tier}
                </span>
            </div>
        </div>
        <div class="card-body" style="padding:6px 10px;">
            <div style="display:grid; grid-template-columns: 1fr 1.6fr; gap:10px; align-items:start;">
                <!-- Left: Archetype & Verdict -->
                <div style="background:#fcfaf5; border:1px solid #e5dccb; border-radius:4px; padding:6px 8px;">
                    <div style="font-weight:bold; color:#4a3325; font-size:7.5pt; margin-bottom:2px;">👑 Archetype: {archetype}</div>
                    <div style="font-size:6.8pt; color:#475569; line-height:1.3; margin-bottom:4px;">{verdict}</div>
                    <div style="font-size:6.2pt; color:#7c6853; border-top:1px solid #e5dccb; padding-top:3px; font-style:italic;">
                        Core Principle: If the Lagna is underpowered, even brilliant yogas struggle to manifest—like a king bedridden in a golden palace. When Lagna is robust, the native turns celestial potential into worldly reality.
                    </div>
                </div>
                <!-- Right: 5-Pillar Score Grid -->
                <div style="display:grid; grid-template-columns: repeat(5, 1fr); gap:4px; text-align:center;">
                    <div style="background:#fff; border:1px solid #e2e8f0; border-radius:3px; padding:3px 2px;">
                        <div style="font-size:5.8pt; color:#64748b; font-weight:600; text-transform:uppercase;">1. Captain</div>
                        <div style="font-size:8pt; font-weight:bold; color:{'#15803d' if p1 >= 0 else '#b91c1c'};">{fmt_pts(p1)}</div>
                        <div style="font-size:5.5pt; color:#475569; line-height:1.1; margin-top:1px;">{p1_items[0] if p1_items else '-'}</div>
                    </div>
                    <div style="background:#fff; border:1px solid #e2e8f0; border-radius:3px; padding:3px 2px;">
                        <div style="font-size:5.8pt; color:#64748b; font-weight:600; text-transform:uppercase;">2. Field</div>
                        <div style="font-size:8pt; font-weight:bold; color:{'#15803d' if p2 >= 0 else '#b91c1c'};">{fmt_pts(p2)}</div>
                        <div style="font-size:5.5pt; color:#475569; line-height:1.1; margin-top:1px;">{p2_items[0] if p2_items else '-'}</div>
                    </div>
                    <div style="background:#fff; border:1px solid #e2e8f0; border-radius:3px; padding:3px 2px;">
                        <div style="font-size:5.8pt; color:#64748b; font-weight:600; text-transform:uppercase;">3. Occupants</div>
                        <div style="font-size:8pt; font-weight:bold; color:{'#15803d' if p3 >= 0 else '#b91c1c'};">{fmt_pts(p3)}</div>
                        <div style="font-size:5.5pt; color:#475569; line-height:1.1; margin-top:1px;">{p3_items[0] if p3_items else 'Clean H1'}</div>
                    </div>
                    <div style="background:#fff; border:1px solid #e2e8f0; border-radius:3px; padding:3px 2px;">
                        <div style="font-size:5.8pt; color:#64748b; font-weight:600; text-transform:uppercase;">4. Sky-Light</div>
                        <div style="font-size:8pt; font-weight:bold; color:{'#15803d' if p4 >= 0 else '#b91c1c'};">{fmt_pts(p4)}</div>
                        <div style="font-size:5.5pt; color:#475569; line-height:1.1; margin-top:1px;">{p4_items[0] if p4_items else '-'}</div>
                    </div>
                    <div style="background:#fff; border:1px solid #e2e8f0; border-radius:3px; padding:3px 2px;">
                        <div style="font-size:5.8pt; color:#64748b; font-weight:600; text-transform:uppercase;">5. Enclosure</div>
                        <div style="font-size:8pt; font-weight:bold; color:{'#15803d' if p5 >= 0 else '#b91c1c'};">{fmt_pts(p5)}</div>
                        <div style="font-size:5.5pt; color:#475569; line-height:1.1; margin-top:1px;">{p5_items[0] if p5_items else 'Unencumbered'}</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """


def render_master_graha_diagnostics_table(chart_data: Dict[str, Any], varga: str = "D1", notation: str = "symbol") -> str:
    """Renders the comprehensive Master Graha Diagnostics Table matching front-end software with inline decoded tooltips."""
    v_data = chart_data.get("vargas", {}).get(varga, chart_data.get("vargas", {}).get("D1", {}))
    v_grahas = v_data.get("grahas", {})
    v_lagna = v_data.get("lagna", {})
    shadbala = chart_data.get("shadbala", {})
    bhavas = v_data.get("bhavas", [])
    naks = chart_data.get("nakshatras", {}).get("grahas", {})
    adv_aspects = chart_data.get("varga_advanced_aspects", {}).get(varga, chart_data.get("advanced_aspects", {}))
    pe = chart_data.get("planetary_evaluation", {})

    tbody_rows = []

    # 1. LAGNA ROW
    if v_lagna and v_lagna.get("sign"):
        lg_sign = v_lagna.get("sign", "-")
        lg_deg_val = float(v_lagna.get("degree_0_to_30", 0.0))
        lg_deg = format_deg_short(lg_deg_val)
        lg_baladi = calculate_baladi_avastha(lg_sign, lg_deg_val)
        lg_nak_data = naks.get("Lagna", {})
        lg_nak_str = f"{lg_nak_data.get('nakshatra', '-')} ({lg_nak_data.get('pada', '-')})" if lg_nak_data else "-"
        lg_lord = SIGN_LORDS.get(lg_sign, v_lagna.get("lord", "-"))
        lord_graha = v_grahas.get(lg_lord, {})
        
        # Lord placement
        lagna_idx = SIGNS_LIST.index(lg_sign) if lg_sign in SIGNS_LIST else 0
        lord_sign = lord_graha.get("sign", "")
        lord_deg_val = float(lord_graha.get("degree_0_to_30", 15.0))
        lord_sign_idx = SIGNS_LIST.index(lord_sign) if lord_sign in SIGNS_LIST else 0
        lord_w_house = ((lord_sign_idx - lagna_idx + 12) % 12 + 1) if (lg_sign in SIGNS_LIST and lord_sign in SIGNS_LIST) else 1
        lord_c_house = get_campanus_house_num(lg_lord, lord_w_house, bhavas)
        shift_html = f"<span class='badge' style='background:#fef3c7; color:#b45309; border:1px solid #fde68a; font-size:5.5pt;'>➔ B{lord_c_house}</span>" if lord_c_house != lord_w_house else ""

        # Lord dignity
        d_break = lord_graha.get("dignity_breakdown", {})
        lord_dig_raw = d_break.get("final_dignity", lord_graha.get("dignity", "Neutral"))
        clean_lord_dig = lord_dig_raw.replace("'s Sign", "").replace(" Sign", "").strip()
        lord_dig_pct = get_dignity_score(clean_lord_dig, planet=lg_lord, sign=lord_sign, degree=lord_deg_val)

        # Lord Host (Dispositor of the Lagnesha)
        lord_host = SIGN_LORDS.get(lord_sign, lg_lord)
        lord_host_graha = v_grahas.get(lord_host, {})
        lord_host_sign = lord_host_graha.get("sign", "")
        lord_host_deg_val = float(lord_host_graha.get("degree_0_to_30", 15.0))
        lord_host_dig_raw = lord_host_graha.get("dignity_breakdown", {}).get("final_dignity", lord_host_graha.get("dignity", "Neutral"))
        lord_host_dig = get_dignity_score(lord_host_dig_raw, planet=lord_host, sign=lord_host_sign, degree=lord_host_deg_val)
        lord_host_sb_entry = shadbala.get(lord_host, {})
        lord_host_sb = float(lord_host_sb_entry.get("Pct_Required_Total", 100.0))
        
        if lord_host == lg_lord:
            lord_rescue_badge = '<span class="badge own" style="font-size:5.5pt;">🏡 Self-Hosted</span>'
        elif lord_host_dig >= 70.0:
            lord_rescue_badge = '<span class="badge exalt" style="font-size:5.5pt;">🛡️ Fortified Host</span>'
        elif lord_host_dig < 40.0:
            lord_rescue_badge = '<span class="badge debil" style="font-size:5.5pt;">⚠️ Strained Host</span>'
        else:
            lord_rescue_badge = '<span class="badge neutral" style="font-size:5.5pt;">⚖️ Neutral Host</span>'

        # Lord Shadbala
        sb_lord = shadbala.get(lg_lord, {})
        sb_vir = f"{sb_lord.get('Total_Virupas', 0.0):.1f}" if "Total_Virupas" in sb_lord else "-"
        sb_pct = int(round(sb_lord.get("Pct_Required_Total", 0.0))) if "Pct_Required_Total" in sb_lord else None
        sb_rank = sb_lord.get("Relative_Rank", "-")
        ishta = f"{sb_lord.get('Ishta_Phala', 0.0):.1f}" if "Ishta_Phala" in sb_lord else "-"
        kashta = f"{sb_lord.get('Kashta_Phala', 0.0):.1f}" if "Kashta_Phala" in sb_lord else "-"

        # Cusp 1 Aspects
        cusp_totals = adv_aspects.get("totals", {}).get("cusps", {}).get(1, adv_aspects.get("totals", {}).get("cusps", {}).get("1", {}))
        c1_net = float(cusp_totals.get("net", 0.0))
        c1_indiv = adv_aspects.get("cusps", {}).get(1, adv_aspects.get("cusps", {}).get("1", {}))
        jup_aspect = float(c1_indiv.get("Jupiter", {}).get("net", c1_indiv.get("Jupiter", {}).get("plus", 0.0)))
        lord_aspect = float(c1_indiv.get(lg_lord, {}).get("net", c1_indiv.get(lg_lord, {}).get("plus", 0.0)))
        
        # Occupants in H1
        h1_occupants = [p for p in PLANETS_ORDER if v_grahas.get(p, {}).get("sign") == lg_sign]
        occ_spans = []
        for p in h1_occupants:
            glyph = GRAHA_GLYPHS_MAP.get(p, "")
            is_ben = p in ["Jupiter", "Venus", "Mercury", "Moon"]
            col = "#15803d" if is_ben else "#b91c1c"
            occ_spans.append(f"<span style='color:{col}; font-weight:600;'>{glyph} {p}</span>")
        occ_html = ", ".join(occ_spans) if occ_spans else "<span style='color:#94a3b8;'>Clean Horizon</span>"
        
        # Flanking Kartari
        h2_sign = SIGNS_LIST[(lagna_idx + 1) % 12]
        h12_sign = SIGNS_LIST[(lagna_idx + 11) % 12]
        h2_occ = [p for p in PLANETS_ORDER if v_grahas.get(p, {}).get("sign") == h2_sign and p not in ["Rahu", "Ketu"]]
        h12_occ = [p for p in PLANETS_ORDER if v_grahas.get(p, {}).get("sign") == h12_sign and p not in ["Rahu", "Ketu"]]
        h2_ben = [p for p in h2_occ if p in ["Jupiter", "Venus", "Mercury", "Moon"]]
        h2_mal = [p for p in h2_occ if p in ["Saturn", "Mars", "Sun"]]
        h12_ben = [p for p in h12_occ if p in ["Jupiter", "Venus", "Mercury", "Moon"]]
        h12_mal = [p for p in h12_occ if p in ["Saturn", "Mars", "Sun"]]
        
        kartari_badge = ""
        if h2_ben and h12_ben and not h2_mal and not h12_mal:
            kartari_badge = '<span class="badge exalt" style="font-size:5.5pt; margin-left:2px;">✨ Śubha Kartarī</span>'
        elif h2_mal and h12_mal and not h2_ben and not h12_ben:
            kartari_badge = '<span class="badge debil" style="font-size:5.5pt; margin-left:2px;">⚔️ Pāpa Kartarī</span>'
            
        # Cusp net badge
        if c1_net >= 15.0:
            c1_badge = f'<span class="badge exalt">+{c1_net:.1f}v Net Light</span>'
        elif c1_net <= -15.0:
            c1_badge = f'<span class="badge debil">{c1_net:.1f}v Net Pressure</span>'
        else:
            c1_badge = f'<span class="badge neutral">{"+" if c1_net >= 0 else ""}{c1_net:.1f}v Neutral</span>'
        if jup_aspect > 15.0:
            c1_badge += ' <span class="badge exalt" style="font-size:5.5pt;">🛡️ Guru Dṛṣṭi</span>'
        if lord_aspect > 15.0:
            c1_badge += ' <span class="badge own" style="font-size:5.5pt;">👑 Lagneśa Dṛṣṭi</span>'
            
        # Lagna Vitality Score
        lagna_eval = pe.get("lagna_evaluation", {}) if varga == "D1" else {}
        lagna_vit = lagna_eval.get("vitality_score", 5.0)
        lagna_tier = lagna_eval.get("vitality_tier", "Capable Vessel")
        lagna_arch = lagna_eval.get("archetype", "The Steady Navigator")
        
        if lagna_vit >= 8.8:
            l_t_bg = "#ecfdf5"; l_t_col = "#065f46"
        elif lagna_vit >= 7.0:
            l_t_bg = "#f0fdf4"; l_t_col = "#15803d"
        elif lagna_vit >= 5.5:
            l_t_bg = "#eff6ff"; l_t_col = "#1d4ed8"
        elif lagna_vit >= 4.0:
            l_t_bg = "#fffbeb"; l_t_col = "#b45309"
        else:
            l_t_bg = "#fef2f2"; l_t_col = "#b91c1c"

        tbody_rows.append(f"""
        <tr style="background:#faf7f2; border-bottom:2px solid #dcb594; font-weight:500;">
            <td style="padding:2.5px 3px; border:1px solid #dcb594;">
                <div style="display:flex; align-items:center; gap:3px;">
                    <span style="font-size:10pt;">🌅</span>
                    <div>
                        <strong style="color:#4a3325; font-size:7.5pt;">Lagna</strong>
                        <div style="font-size:5.8pt; color:#64748b;">Tanū Bhāva (H1)</div>
                    </div>
                </div>
            </td>
            <td style="padding:2.5px 3px; border:1px solid #dcb594;">
                <strong style="color:#1e293b; font-size:7.2pt;">{lg_sign} {lg_deg}</strong>
                <div style="font-size:5.8pt; color:#64748b;">House 1 (Ascendant)</div>
                <div style="font-size:5.8pt; color:#475569;">Lord: <strong>{lg_lord}</strong></div>
                <div style="font-size:5.5pt; color:#78716c;">{lg_nak_str}</div>
            </td>
            <td style="padding:2.5px 3px; border:1px solid #dcb594; text-align:center;">
                <div>{dignity_badge(clean_lord_dig)}</div>
                <div style="font-size:6pt; font-weight:bold; color:#1e293b; margin-top:1px;">{lord_dig_pct:.0f}% Dignity</div>
                <div style="font-size:5.2pt; color:#64748b;">Captain: {lg_lord}</div>
            </td>
            <td style="padding:2.5px 3px; border:1px solid #dcb594; text-align:center;">
                <div style="font-weight:600; font-size:6.5pt; color:#1e293b;">Host: {lord_host}</div>
                <div style="font-size:5.5pt; color:#64748b;">{lord_host_dig:.0f}% Dignity • {lord_host_sb:.0f}% Musc</div>
                <div style="margin-top:1.5px;">{lord_rescue_badge}</div>
            </td>
            <td style="padding:2.5px 3px; border:1px solid #dcb594;">
                <div style="font-size:7pt; font-weight:bold;">{sb_vir} Vir <span style="font-size:6pt; color:{'#15803d' if (sb_pct or 0) >= 100 else '#b91c1c'}; font-weight:600;">({sb_pct}% req)</span></div>
                <div style="font-size:5.8pt; color:#64748b;">Rank #{sb_rank} • Captain stamina</div>
                <div style="font-size:5.5pt; color:#475569; margin-top:1px;">I: {ishta} / K: {kashta}</div>
            </td>
            <td style="padding:2.5px 3px; border:1px solid #dcb594;">
                <div style="font-size:6pt; margin-bottom:1.5px;"><strong>YUTI:</strong> {occ_html}</div>
                <div style="display:flex; flex-wrap:wrap; gap:2px;">{c1_badge} {kartari_badge}</div>
            </td>
            <td style="padding:2.5px 3px; border:1px solid #dcb594;">
                <div style="font-size:6pt; font-weight:bold; color:#475569;">
                    Age: <span class="badge" style="background:#f1f5f9; color:#334155; font-size:5.5pt;">{lg_baladi['state']} ({lg_baladi['efficiency_pct']}%)</span>
                </div>
                <div style="font-size:5.2pt; color:#64748b; margin-bottom:2px;">{lg_baladi['sanskrit_term'][:18]}</div>
                <div style="font-size:5.8pt; color:#3730a3; font-weight:600;">Lord in H{lord_w_house} {shift_html}</div>
            </td>
            <td style="padding:2.5px 3px; border:1px solid #dcb594; text-align:center;">
                <span style="display:inline-block; background:{l_t_bg}; color:{l_t_col}; border:1px solid {l_t_col}44; font-size:6.8pt; font-weight:bold; padding:1.5px 4px; border-radius:3px;">
                    ★ {lagna_vit:.1f} • {lagna_tier}
                </span>
                <div style="font-size:6pt; font-weight:bold; color:#1e293b; margin-top:2px;">
                    Score: ★ {lagna_vit:.1f} / 10
                </div>
                <div style="font-size:5.2pt; color:#64748b;">{lagna_arch}</div>
            </td>
        </tr>
        """)

    # 2. PLANETARY ROWS (Sun through Ketu)
    for p in PLANETS_ORDER:
        if p not in v_grahas:
            continue
        g = v_grahas[p]
        glyph = GRAHA_GLYPHS_MAP.get(p, get_planet_glyph(p, notation))
        sign = g.get("sign", "-")
        deg_val = float(g.get("degree_0_to_30", 0.0))
        deg = format_deg_short(deg_val)
        baladi = calculate_baladi_avastha(sign, deg_val)
        
        # Whole sign house
        lg_idx = SIGNS_LIST.index(v_lagna.get("sign", "Aries")) if v_lagna.get("sign") in SIGNS_LIST else 0
        p_idx = SIGNS_LIST.index(sign) if sign in SIGNS_LIST else 0
        w_house = ((p_idx - lg_idx + 12) % 12 + 1) if (v_lagna.get("sign") in SIGNS_LIST and sign in SIGNS_LIST) else 1
        c_house = get_campanus_house_num(p, w_house, bhavas)
        shift_badge = f"<span class='badge' style='background:#fef3c7; color:#b45309; border:1px solid #fde68a; font-size:5.5pt;'>➔ B{c_house}</span>" if c_house != w_house else ""
        
        # Chara Karaka
        ck_data = g.get("chara_karaka") or chart_data.get("karakas", {}).get("chara", {}).get(p, {})
        ck_tag = ck_data.get("karaka", "—")
        ck_badge = ""
        if ck_tag and ck_tag != "—":
            ck_badge = f"<span class='badge' style='background:#fef3c7; color:#92400e; border:1px solid #fcd34d; font-size:5.8pt; font-weight:bold;'>👑 {ck_tag}</span>"
            
        # Motional Badges
        mot_badges = []
        if g.get("is_retrograde"):
            mot_badges.append("<span class='badge debil' style='font-size:5.5pt;'>[R] Vakra (Ret.)</span>")
        if g.get("is_combust"):
            s_dist = g.get("sun_distance")
            s_dist_str = f" {s_dist:.1f}°" if s_dist is not None else ""
            mot_badges.append(f"<span class='badge' style='background:#ffedd5; color:#9a3412; border:1px solid #fed7aa; font-size:5.5pt;'>[C] Asta{s_dist_str}</span>")
        mot_html = " ".join(mot_badges)
        
        # Functional Role
        fn_role = g.get("functional_role") or chart_data.get("karakas", {}).get("functional", {}).get(p, {})
        ruled_str = fn_role.get("ruled_houses_str", "")
        ruled_html = f"<div style='font-size:5.8pt; color:#475569;'>Rules: <strong>{ruled_str}</strong></div>" if ruled_str else ""
        
        fn_badges = []
        if fn_role.get("is_yogakaraka"):
            fn_badges.append("<span class='badge' style='background:#fef3c7; color:#92400e; border:1px solid #fcd34d; font-size:5.5pt; font-weight:bold;'>⭐ Yogakāraka</span>")
        elif fn_role.get("is_lagnesha"):
            fn_badges.append("<span class='badge own' style='font-size:5.5pt; font-weight:bold;'>🛡️ Lagneśa</span>")
        if fn_role.get("is_maraka") and not fn_role.get("is_yogakaraka"):
            fn_badges.append("<span class='badge neutral' style='font-size:5.5pt;'>Māraka</span>")
        if fn_role.get("is_badhaka") and not fn_role.get("is_yogakaraka") and not fn_role.get("is_lagnesha"):
            fn_badges.append("<span class='badge' style='background:#ffedd5; color:#9a3412; border:1px solid #fed7aa; font-size:5.5pt;'>Bādhaka</span>")
        fn_badges_html = f"<div style='display:flex; flex-wrap:wrap; gap:1.5px; margin-top:1px;'>{''.join(fn_badges)}</div>" if fn_badges else ""
        
        # Nakshatra
        p_nak_data = naks.get(p, {})
        nak_str = f"{p_nak_data.get('nakshatra', '-')} ({p_nak_data.get('pada', '-')})" if p_nak_data else "-"
        
        # Dignity (5-fold)
        is_node = p in ["Rahu", "Ketu"]
        d_break = g.get("dignity_breakdown", {})
        sign_lord = d_break.get("sign_lord", SIGN_LORDS.get(sign, "-"))
        raw_dig = d_break.get("final_dignity", g.get("dignity", "Neutral"))
        clean_dig = raw_dig.replace("'s Sign", "").replace(" Sign", "").strip()
        dignity_pct = get_dignity_score(clean_dig, planet=p, sign=sign, degree=deg_val)
        
        # Host (Dispositor) Metrics
        host_graha = v_grahas.get(sign_lord, {})
        host_sign = host_graha.get("sign", "")
        host_deg_val = float(host_graha.get("degree_0_to_30", 15.0))
        host_dig_raw = host_graha.get("dignity_breakdown", {}).get("final_dignity", host_graha.get("dignity", "Neutral"))
        host_dig = get_dignity_score(host_dig_raw, planet=sign_lord, sign=host_sign, degree=host_deg_val)
        host_sb_data = shadbala.get(sign_lord, {})
        host_sb = float(host_sb_data.get("Pct_Required_Total", 100.0))
        host_vir = float(host_sb_data.get("Total_Virupas", 360.0))
        
        # Planet Shadbala
        sb = shadbala.get(p, {})
        sb_pct_val = float(sb.get("Pct_Required_Total", 100.0)) if sb else 100.0
        
        # Conjunctions & Drishti
        conjuncts = [other for other in PLANETS_ORDER if other != p and v_grahas.get(other, {}).get("sign") == sign]
        asp_rec = adv_aspects.get("planets", {}).get(p, {})
        tot_rec = adv_aspects.get("totals", {}).get("planets", {}).get(p, {})
        net_val = float(tot_rec.get("net", 0.0))
        
        # Lajjitadi Avasthas
        av_list = g.get("avasthas", {}).get("lajjitadi", [])
        
        # Calibrated Functional Vitality and Archetype Diagnosis
        lagna_sign_val = v_lagna.get("sign", "")
        lagna_lord_val = SIGN_LORDS.get(lagna_sign_val, "")
        vit_res = calculate_graha_vitality(
            planet=p,
            sign=sign,
            degree_in_sign=deg_val,
            dignity_name=clean_dig,
            dignity_pct=dignity_pct,
            host_planet=sign_lord,
            host_dignity_pct=host_dig,
            host_shadbala_pct=host_sb,
            planet_shadbala_pct=sb_pct_val,
            net_drishti_virupas=net_val,
            conjunctions=conjuncts,
            lajjitadi_states=av_list,
            is_retrograde=bool(g.get("is_retrograde")),
            is_combust=bool(g.get("is_combust")),
            is_node=is_node,
            lagna_sign=lagna_sign_val,
            lagna_lord=lagna_lord_val,
        )
        quad = vit_res["quadrant"]
        net_vitality = vit_res["vitality_score"]
        rescue_badge = vit_res["rescue_badge"]
        effective_dignity = vit_res["effective_dignity_pct"]
        
        # Cell 3: Essential Dignity
        if is_node:
            dig_cell_html = f"""
            <div style="text-align:center;">
                <span class="badge neutral" style="font-weight:600; font-size:6.2pt;">Proxy ({sign_lord})</span>
                <div style="font-size:6pt; font-weight:bold; color:#1e293b; margin-top:1px;">{effective_dignity:.0f}% Dignity</div>
                <div style="font-size:5.2pt; color:#64748b;">Chhāyā Reflection</div>
            </div>
            """
        else:
            nat_rel = d_break.get("natural_relationship", "-")
            temp_rel = d_break.get("temporary_relationship", "-")
            dig_cell_html = f"""
            <div style="text-align:center;">
                {dignity_badge(clean_dig)}
                <div style="font-size:6pt; font-weight:bold; color:#1e293b; margin-top:1px;">{dignity_pct:.0f}% Dignity</div>
                <div style="font-size:5pt; color:#78716c;">Nat: {nat_rel[:3]} • Tmp: {temp_rel[:3]}</div>
            </div>
            """

        # Cell 4: Host Dispositor
        rescue_badge_class = "exalt" if "Rescued" in rescue_badge else ("own" if "Self" in rescue_badge or "Fortified" in rescue_badge else ("debil" if "Strained" in rescue_badge else "neutral"))
        rescue_badge_html = f'<span class="badge {rescue_badge_class}" style="font-size:5.5pt;">{rescue_badge}</span>'
        host_cell_html = f"""
        <div style="text-align:center;">
            <div style="font-weight:600; font-size:6.5pt; color:#1e293b;">Host: {sign_lord}</div>
            <div style="font-size:5.5pt; color:#64748b;">{host_dig:.0f}% Dignity • {host_sb:.0f}% Musc</div>
            <div style="margin-top:1.5px;">{rescue_badge_html}</div>
        </div>
        """

        # Cell 5: Shadbala Power
        if is_node:
            nodal_sb_pct = vit_res["effective_shadbala_pct"]
            power_cell_html = f"""
            <div>
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <strong style="font-size:6.8pt;">{nodal_sb_pct:.0f}%</strong>
                    <span class="badge neutral" style="font-size:5.5pt; font-weight:600;">Proxy</span>
                </div>
                <div style="font-size:5.8pt; color:#15803d; font-weight:bold;">via {sign_lord} ({host_vir:.0f}v)</div>
                <div style="font-size:5.2pt; color:#64748b;">Chhāyā Proxy Muscle</div>
            </div>
            """
        elif sb:
            rupas = f"{sb.get('Total_Rupas', 0.0):.2f} R" if "Total_Rupas" in sb else "-"
            virupas = f"{sb.get('Total_Virupas', 0.0):.1f}v" if "Total_Virupas" in sb else "-"
            req_vir = f"{sb.get('Required_Total', 0.0):.0f}v" if "Required_Total" in sb else "-"
            pct_val = float(sb.get("Pct_Required_Total", 0.0))
            rank = sb.get("Relative_Rank", "-")
            
            pct_col = "#15803d" if pct_val >= 100.0 else "#b91c1c"
            rank_badge = f"<span class='badge {'exalt' if rank == 1 else 'neutral'}' style='font-size:5.5pt; font-weight:bold;'>{'👑 ' if rank == 1 else ''}#{rank}</span>"
            cap_desc = "Abundant" if pct_val >= 125 else ("Capable" if pct_val >= 100 else ("Mild Deficit" if pct_val >= 85 else "Deficit"))
            ishta_str = f"I:{float(sb.get('Ishta_Phala', 0.0)):.1f}" if "Ishta_Phala" in sb else ""
            kashta_str = f"K:{float(sb.get('Kashta_Phala', 0.0)):.1f}" if "Kashta_Phala" in sb else ""
            fruit_sub = f" • <span style='font-size:5.2pt;'>{ishta_str}/{kashta_str}</span>" if ishta_str else ""

            power_cell_html = f"""
            <div>
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <strong style="font-size:6.8pt;">{virupas}</strong>
                    {rank_badge}
                </div>
                <div style="font-size:5.8pt; color:{pct_col}; font-weight:bold;">{pct_val:.0f}% of {req_vir}</div>
                <div style="font-size:5.2pt; color:#64748b;">{cap_desc}{fruit_sub}</div>
            </div>
            """
        else:
            power_cell_html = "<div style='color:#94a3b8; font-size:6pt;'>-</div>"

        # Cell 6: Influences & Net Drishti
        if net_val >= 12.0:
            net_pill = f"<span class='badge exalt' style='font-size:5.5pt; font-weight:bold;'>🟢 Net Support (+{net_val:.0f}v)</span>"
        elif net_val <= -12.0:
            net_pill = f"<span class='badge debil' style='font-size:5.5pt; font-weight:bold;'>🔴 Net Pressure ({net_val:.0f}v)</span>"
        else:
            net_pill = f"<span class='badge neutral' style='font-size:5.5pt; font-weight:600;'>⚖️ Balanced ({'+' if net_val >= 0 else ''}{net_val:.0f}v)</span>"

        conj_spans = []
        for cp in conjuncts:
            c_glyph = GRAHA_GLYPHS_MAP.get(cp, "")
            is_b = cp in ["Jupiter", "Venus"]
            is_m = cp in ["Saturn", "Mars", "Rahu", "Ketu"]
            c_col = "#15803d" if is_b else ("#b91c1c" if is_m else "#475569")
            conj_spans.append(f"<span style='color:{c_col}; font-weight:600;'>{c_glyph} {cp[:2]}</span>")
        yuti_html = f"<div style='font-size:5.5pt; color:#64748b;'><strong>YUTI:</strong> {' '.join(conj_spans)}</div>" if conj_spans else ""

        asp_spans = []
        for asp_p in PLANETS_ORDER:
            if asp_p != p and asp_p in asp_rec and asp_rec[asp_p].get("raw", 0.0) > 4.0:
                a_data = asp_rec[asp_p]
                raw_v = int(round(a_data.get("raw", 0.0)))
                is_p = a_data.get("plus", 0.0) > 0
                sign_ch = "+" if is_p else "-"
                a_col = "#15803d" if is_p else "#b91c1c"
                a_glyph = GRAHA_GLYPHS_MAP.get(asp_p, asp_p[:2])
                asp_spans.append(f"<span style='color:{a_col}; font-weight:600;'>{sign_ch}{raw_v}v ({a_glyph})</span>")
        drishti_html = f"<div style='font-size:5.5pt; color:#64748b;'><strong>DRISHTI:</strong> {' '.join(asp_spans[:3])}</div>" if asp_spans else ""

        influences_cell_html = f"""
        <div style="display:flex; flex-direction:column; gap:1.5px;">
            <div>{net_pill}</div>
            {yuti_html}
            {drishti_html}
        </div>
        """

        # Cell 7: Avasthas (State & Age)
        lajjita_badges = []
        for item in av_list:
            st = item.get("state", "") if isinstance(item, dict) else str(item)
            cond = item.get("condition", "") if isinstance(item, dict) else ""
            cause_note = ""
            for cp in CLASSICAL_PLANETS + ["Rahu", "Ketu"]:
                if cp in cond:
                    glyph_c = GRAHA_GLYPHS_MAP.get(cp, cp[:2])
                    cause_note = f" ({glyph_c})"
                    break
            if not cause_note:
                if "Enemy sign" in cond: cause_note = " (Enm. sign)"
                elif "Friend's sign" in cond: cause_note = " (Frn. sign)"
            s_lower = st.lower()
            if "mudita" in s_lower or "delight" in s_lower:
                lajjita_badges.append(f"<span class='badge state-delighted' style='font-size:5.5pt;'>🟢 Mudita{cause_note}</span>")
            elif "garvita" in s_lower or "proud" in s_lower:
                lajjita_badges.append(f"<span class='badge state-proud' style='font-size:5.5pt;'>👑 Garvita{cause_note}</span>")
            elif "kshudhita" in s_lower or "starv" in s_lower:
                lajjita_badges.append(f"<span class='badge state-starved' style='font-size:5.5pt;'>🔴 Kshudhita{cause_note}</span>")
            elif "kshobhita" in s_lower or "agitat" in s_lower:
                lajjita_badges.append(f"<span class='badge state-agitated' style='font-size:5.5pt;'>🟠 Kshobhita{cause_note}</span>")
            elif "lajjita" in s_lower or "ashamed" in s_lower:
                lajjita_badges.append(f"<span class='badge state-ashamed' style='font-size:5.5pt;'>🟣 Lajjita{cause_note}</span>")
            elif "trushita" in s_lower or "thirst" in s_lower:
                lajjita_badges.append(f"<span class='badge state-thirsty' style='font-size:5.5pt;'>💧 Trushita{cause_note}</span>")

        if is_node:
            avasthas_cell_html = f"""
            <div>
                <div style="font-size:6pt; font-weight:bold; color:#475569;">
                    Age: <span class="badge" style="background:#f1f5f9; color:#334155; font-size:5.5pt;">{baladi['state']} ({baladi['efficiency_pct']}%)</span>
                </div>
                <div style="font-size:5.2pt; color:#64748b; margin-bottom:2px;">{baladi['sanskrit_term'][:18]}</div>
                <span style="color:#94a3b8; font-size:5.5pt;">— (Chhāyā Catalyst)</span>
            </div>
            """
        else:
            badges_html = "".join(lajjita_badges) if lajjita_badges else '<span style="color:#a8a29e; font-style:italic; font-size:5.5pt;">Neutral</span>'
            avasthas_cell_html = f"""
            <div>
                <div style="font-size:6pt; font-weight:bold; color:#475569;">
                    Age: <span class="badge" style="background:#f1f5f9; color:#334155; font-size:5.5pt;">{baladi['state']} ({baladi['efficiency_pct']}%)</span>
                </div>
                <div style="font-size:5.2pt; color:#64748b; margin-bottom:2px;">{baladi['sanskrit_term'][:18]}</div>
                <div style="display:flex; flex-direction:column; gap:1.5px;">{badges_html}</div>
            </div>
            """

        # Cell 8: Functional Archetype & Diagnosis
        diag_cell_html = f"""
        <div style="text-align:center;">
            <span style="display:inline-block; background:{quad['bg']}; color:{quad['color']}; border:1px solid {quad['color']}44; font-size:6.5pt; font-weight:bold; padding:1.5px 4px; border-radius:3px;">
                {quad['badge']}
            </span>
            <div style="font-size:6pt; font-weight:bold; color:#1e293b; margin-top:2px;">
                Score: ★ {net_vitality:.1f} / 10
            </div>
            <div style="font-size:5.2pt; color:#64748b;">{quad['tier']}</div>
        </div>
        """

        tbody_rows.append(f"""
        <tr>
            <td style="padding:2px 3px; border:1px solid #e5dccb; background:#fffdfa;">
                <div style="display:flex; align-items:center; gap:3px;">
                    <span style="font-size:9.5pt; color:#1e293b;">{glyph}</span>
                    <div>
                        <div style="display:flex; align-items:center; gap:2px;">
                            <strong style="color:#1e293b; font-size:7.2pt;">{p}</strong>
                            {ck_badge}
                        </div>
                        <div>{mot_html}</div>
                    </div>
                </div>
            </td>
            <td style="padding:2px 3px; border:1px solid #e5dccb; background:#fffdfa;">
                <strong style="color:#1e293b; font-size:7pt;">{sign} {deg}</strong>
                <div style="font-size:5.8pt; color:#64748b;">House {w_house} {shift_badge}</div>
                {ruled_html}
                {fn_badges_html}
                <div style="font-size:5.5pt; color:#78716c; margin-top:1px;">{nak_str}</div>
            </td>
            <td style="padding:2px 3px; border:1px solid #e5dccb; background:#fffdfa;">
                {dig_cell_html}
            </td>
            <td style="padding:2px 3px; border:1px solid #e5dccb; background:#fffdfa;">
                {host_cell_html}
            </td>
            <td style="padding:2px 3px; border:1px solid #e5dccb; background:#fffdfa;">
                {power_cell_html}
            </td>
            <td style="padding:2px 3px; border:1px solid #e5dccb; background:#fffdfa;">
                {influences_cell_html}
            </td>
            <td style="padding:2px 3px; border:1px solid #e5dccb; background:#fffdfa;">
                {avasthas_cell_html}
            </td>
            <td style="padding:2px 3px; border:1px solid #e5dccb; background:#fffdfa;">
                {diag_cell_html}
            </td>
        </tr>
        """)

    return f"""
    <div class="card full-width" style="margin-bottom:8px; border:1px solid #dcb594;">
        <div class="card-header" style="background:#eee5d3; padding:4px 8px; display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #dcb594;">
            <div style="display:flex; align-items:center; gap:6px;">
                <span style="font-size:10pt;">★</span>
                <h3 style="font-size:8.5pt; font-weight:700; color:#4a3325; margin:0;">Master Graha Diagnostics • Unified Planetary Matrix ({varga})</h3>
            </div>
            <span class="card-sub" style="font-size:6.5pt; color:#7c6853;">
                Synthesizing Pañcadhā Dignity • Dispositor Anchor • Ṣaḍbala Muscle • Bālādi Age • Lajjitādi Feelings • 4-Quadrant Diagnosis
            </span>
        </div>
        <div class="card-body" style="padding:2px;">
            <table class="data-table" style="width:100%; border-collapse:collapse; font-size:6.5pt; line-height:1.2;">
                <thead>
                    <tr>
                        <th style="width:11%;">Graha &amp; Soul</th>
                        <th style="width:14%;">Placement &amp; Role</th>
                        <th style="width:11%;">Essential Dign.</th>
                        <th style="width:13%;">Host Dispositor</th>
                        <th style="width:13%;">Ṣaḍbala Power</th>
                        <th style="width:13%;">Aspect Weather</th>
                        <th style="width:13%;">Avastha &amp; Age</th>
                        <th style="width:12%;">★ Functional Archetype</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(tbody_rows)}
                </tbody>
            </table>
        </div>
    </div>
    """


def render_diagnostic_key_section() -> str:
    """Renders the comprehensive Master Astrological Diagnostic Key decoding all tooltips in plain English."""
    return """
    <div class="card full-width" style="border:1px solid #dcb594; margin-bottom:8px;">
        <div class="card-header" style="background:#4a3325; color:#fffdfa; padding:6px 12px; display:flex; justify-content:space-between; align-items:center;">
            <div style="display:flex; align-items:center; gap:8px;">
                <span style="font-size:12pt;">📖</span>
                <div>
                    <h3 style="color:#fdf6e2; font-size:9pt; margin:0;">Master Astrological Diagnostic Key & Pedagogical Reference Guide</h3>
                    <span style="color:#e5dccb; font-size:6.8pt;">Decoding Hidden Principles, Classical Metrics, Feeling States & Synthesis Formulas for Readers</span>
                </div>
            </div>
            <span style="font-size:6.5pt; color:#e5a03b; font-weight:bold; text-transform:uppercase;">Self-Contained Interpretive Key</span>
        </div>
        <div class="card-body" style="padding:8px 10px; background:#fffdfa;">
            <div style="display:grid; grid-template-columns: repeat(3, 1fr); gap:8px;">
                
                <!-- Card 1: Chara Karakas -->
                <div class="key-card" style="background:#fcfaf5; border:1px solid #e5dccb; border-radius:4px; padding:6px 8px;">
                    <div style="font-weight:bold; color:#4a3325; font-size:7.2pt; border-bottom:1px solid #e5dccb; padding-bottom:3px; margin-bottom:4px; display:flex; align-items:center; gap:4px;">
                        <span>👑</span> 1. The 7 Chara Kārakas (Soul Signifiers)
                    </div>
                    <div style="font-size:6.3pt; color:#475569; line-height:1.35;">
                        In Parāśara astrology (BPHS Ch. 32), planets are assigned temporal roles based on who has traveled furthest in their sign:
                        <ul style="margin:3px 0 0 12px; padding:0;">
                            <li><strong>👑 AK (Ātmakāraka / Soul King):</strong> Highest degree; signifies soul mission, spiritual evolution, and core lessons.</li>
                            <li><strong>💼 AmK (Amātyakāraka / Minister):</strong> 2nd highest; career agency, intellect, and social contribution.</li>
                            <li><strong>📿 BK (Bhrātṛkāraka / Guide):</strong> 3rd highest; gurus, mentors, teachers, and courageous brothers.</li>
                            <li><strong>🏡 MK (Mātṛkāraka / Mother):</strong> 4th highest; emotional roots, mother, home, and sanctuary.</li>
                            <li><strong>🌱 PK (Putrakāraka / Intellect):</strong> 5th highest; children, creative genius, and intelligence.</li>
                            <li><strong>⚔️ GK (Jñātikāraka / Obstacles):</strong> 6th highest; trials, rivals, illness, and friction building grit.</li>
                            <li><strong>💍 DK (Dārakāraka / Spouse):</strong> Lowest degree; one-on-one partnerships and marital reflection.</li>
                        </ul>
                    </div>
                </div>

                <!-- Card 2: Motional Dynamics -->
                <div class="key-card" style="background:#fcfaf5; border:1px solid #e5dccb; border-radius:4px; padding:6px 8px;">
                    <div style="font-weight:bold; color:#4a3325; font-size:7.2pt; border-bottom:1px solid #e5dccb; padding-bottom:3px; margin-bottom:4px; display:flex; align-items:center; gap:4px;">
                        <span>⚡</span> 2. Motional Dynamics: Retrograde & Combustion
                    </div>
                    <div style="font-size:6.3pt; color:#475569; line-height:1.35;">
                        Special astronomical conditions modifying planetary behavior:
                        <div style="margin-top:3px;">
                            <strong>[R] Retrograde (Vakra Motion):</strong> Apparent backward motion occurs when a planet is closest to Earth, largest, and brightest. Grants maximum motional power (<em>Cheṣṭa Bala</em>). Energy turns introspective, non-linear, and unconventional; challenges standard norms and re-evaluates significations.
                        </div>
                        <div style="margin-top:4px;">
                            <strong>[C] Combustion (Astangata / Asta):</strong> Proximity within the solar orb. The planet's outward tangible expression is humbled and absorbed by the solar ego, urging the native to seek self-worth internally rather than from external validation. Combust planets primarily weaken the houses they rule.
                        </div>
                    </div>
                </div>

                <!-- Card 3: 5-Fold Dignity -->
                <div class="key-card" style="background:#fcfaf5; border:1px solid #e5dccb; border-radius:4px; padding:6px 8px;">
                    <div style="font-weight:bold; color:#4a3325; font-size:7.2pt; border-bottom:1px solid #e5dccb; padding-bottom:3px; margin-bottom:4px; display:flex; align-items:center; gap:4px;">
                        <span>⚖️</span> 3. Pañcadhā Maitrī (5-Fold Dignity)
                    </div>
                    <div style="font-size:6.3pt; color:#475569; line-height:1.35;">
                        Determines how comfortable and welcomed a planet feels in its host sign:
                        <div style="margin-top:2px;">
                            <strong>Natural Bond (Naisargika):</strong> Permanent friendship between planetary archetypes (e.g. Sun and Mars are natural friends).
                        </div>
                        <div style="margin-top:2px;">
                            <strong>Temporary Bond (Tātkālika):</strong> Distance in the chart (planets in houses 2, 3, 4, 10, 11, 12 from each other are temporary friends; in 1, 5, 6, 7, 8, 9 are enemies).
                        </div>
                        <div style="margin-top:2px;">
                            <strong>5-Fold Synthesis:</strong> Yields 9 dignity levels: Exalted (<em>Uccha</em>), Moolatrikona, Own Sign (<em>Svastha</em>), Great Friend, Friend, Neutral, Enemy, Great Enemy, and Debilitated (<em>Neecha</em>).
                        </div>
                        <div style="margin-top:2px; font-style:italic; color:#78716c;">
                            Rahu & Ketu act as reflection proxies (Chhāyā Grahas), mirroring their dispositor host lord.
                        </div>
                    </div>
                </div>

                <!-- Card 4: Lajjitadi Avasthas -->
                <div class="key-card" style="background:#fcfaf5; border:1px solid #e5dccb; border-radius:4px; padding:6px 8px;">
                    <div style="font-weight:bold; color:#4a3325; font-size:7.2pt; border-bottom:1px solid #e5dccb; padding-bottom:3px; margin-bottom:4px; display:flex; align-items:center; gap:4px;">
                        <span>🌿</span> 4. The 6 Lajjitādi Avasthās (Feelings)
                    </div>
                    <div style="font-size:6.3pt; color:#475569; line-height:1.35;">
                        Sage Parāśara reveals that planets experience psychological moods:
                        <ul style="margin:2px 0 0 12px; padding:0;">
                            <li><strong>🟢 Mudita (Delighted):</strong> Welcomed in friend's sign or aspected by friends; generous and enthusiastic.</li>
                            <li><strong>👑 Garvita (Proud):</strong> Exalted or in own sign; full of regal dignity and confident command.</li>
                            <li><strong>🔴 Kshudhita (Starved):</strong> In enemy sign or pressed by enemy rays; feels drained, struggling for nourishment.</li>
                            <li><strong>🟠 Kshobhita (Agitated):</strong> Conjoined by Sun/malefics or harsh glances; impatient, conflicted, or provoked.</li>
                            <li><strong>🟣 Lajjita (Ashamed):</strong> In 5th/8th house with nodes or malefics; self-conscious or hesitant.</li>
                            <li><strong>💧 Trushita (Thirsty):</strong> In water sign aspected by enemy without benefic help; craving fulfillment.</li>
                        </ul>
                    </div>
                </div>

                <!-- Card 5: Shadbala Power -->
                <div class="key-card" style="background:#fcfaf5; border:1px solid #e5dccb; border-radius:4px; padding:6px 8px;">
                    <div style="font-weight:bold; color:#4a3325; font-size:7.2pt; border-bottom:1px solid #e5dccb; padding-bottom:3px; margin-bottom:4px; display:flex; align-items:center; gap:4px;">
                        <span>🏋️</span> 5. Ṣaḍbala (6-Fold Potency) vs Feelings
                    </div>
                    <div style="font-size:6.3pt; color:#475569; line-height:1.35;">
                        <strong>Engine Stamina vs Emotional Morale:</strong>
                        <div style="margin-top:2px;">
                            • <strong>Ṣaḍbala</strong> is the raw physical horsepower of a car (muscle, capacity to work). Measured in Virūpas (60 Virūpas = 1 Rūpa).
                        </div>
                        <div style="margin-top:2px;">
                            • <strong>Parāśara 100% Minimum:</strong> Sun (390v), Moon (360v), Mars (300v), Mercury (420v), Jupiter (390v), Venus (330v), Saturn (300v).
                        </div>
                        <div style="margin-top:2px;">
                            • <strong>Stamina Tiers:</strong> Abundant Surplus (≥125%), Adequate (≥100%), Mild Deficit (85–99%), Severe Deficit (<85%).
                        </div>
                        <div style="margin-top:2px; font-style:italic; color:#78716c;">
                            A planet can have high Ṣaḍbala (strong engine) but feel starved in Lajjitādi Avasthā (depleted driver morale). Both must be examined together.
                        </div>
                    </div>
                </div>

                <!-- Card 6: Drishti & Aspect Weather -->
                <div class="key-card" style="background:#fcfaf5; border:1px solid #e5dccb; border-radius:4px; padding:6px 8px;">
                    <div style="font-weight:bold; color:#4a3325; font-size:7.2pt; border-bottom:1px solid #e5dccb; padding-bottom:3px; margin-bottom:4px; display:flex; align-items:center; gap:4px;">
                        <span>🌦️</span> 6. Net Dṛṣṭi & Environmental Weather
                    </div>
                    <div style="font-size:6.3pt; color:#475569; line-height:1.35;">
                        Continuous Graha Dṛṣṭi measures the exact aspectual light received:
                        <div style="margin-top:2px;">
                            • <strong>🟢 Net Benefic Support (+Virūpas):</strong> Friendly, protective sky-light from Jupiter and Venus. Calms resistance, opens opportunities, and fosters ease.
                        </div>
                        <div style="margin-top:2px;">
                            • <strong>🔴 Net Malefic Pressure (-Virūpas):</strong> Challenging aspect rays from Saturn and Mars. Introduces discipline, friction, delays, or intense focus.
                        </div>
                        <div style="margin-top:2px;">
                            • <strong>Conjunctions (YUTI):</strong> Living in the same room; planets directly share each other's elemental nature.
                        </div>
                    </div>
                </div>

                <!-- Card 7: Karmic Fruits (I/K) -->
                <div class="key-card" style="background:#fcfaf5; border:1px solid #e5dccb; border-radius:4px; padding:6px 8px;">
                    <div style="font-weight:bold; color:#4a3325; font-size:7.2pt; border-bottom:1px solid #e5dccb; padding-bottom:3px; margin-bottom:4px; display:flex; align-items:center; gap:4px;">
                        <span>🍎</span> 7. Karmic Fruits: Iṣṭa & Kaṣṭa Phala
                    </div>
                    <div style="font-size:6.3pt; color:#475569; line-height:1.35;">
                        Measures the inherent flavor of a planet's karmic harvest (0 to 60 scale):
                        <div style="margin-top:2px;">
                            • <strong>Iṣṭa Phala:</strong> Auspicious capacity. Derived from exaltation strength (Uccha) and motional strength (Cheṣṭa). Produces sweet blessings, joy, and smooth fruition.
                        </div>
                        <div style="margin-top:2px;">
                            • <strong>Kaṣṭa Phala:</strong> Arduous capacity (60 - Iṣṭa). Demands grit, perseverance, overcoming tests, and character-building trials.
                        </div>
                        <div style="margin-top:2px;">
                            • <strong>Balance:</strong> High Iṣṭa brings grace; high Kaṣṭa yields wisdom forged through discipline.
                        </div>
                    </div>
                </div>

                <!-- Card 8: Vitality Score -->
                <div class="key-card" style="background:#fcfaf5; border:1px solid #e5dccb; border-radius:4px; padding:6px 8px;">
                    <div style="font-weight:bold; color:#4a3325; font-size:7.2pt; border-bottom:1px solid #e5dccb; padding-bottom:3px; margin-bottom:4px; display:flex; align-items:center; gap:4px;">
                        <span>⭐</span> 8. ★ Composite Vitality Score (1–10)
                    </div>
                    <div style="font-size:6.3pt; color:#475569; line-height:1.35;">
                        Synthesizes all 5 diagnostic pillars into a single actionable rating:
                        <div style="margin-top:2px;">
                            <strong>5 Pillars:</strong> Sign Dignity (1-10) + Ṣaḍbala Capacity (1-10) + Avasthā Mood (1-10) + Aspect Weather (1-10) + Karmic Fruit (1-10).
                        </div>
                        <div style="margin-top:2px;">
                            • <strong>🌟 Sovereign (8.5–10):</strong> Uncontested strength; manifests results with royal authority.
                        </div>
                        <div style="margin-top:1px;">
                            • <strong>🟢 Capable (7.0–8.4):</strong> Healthy self-worth, resilient, activates yogas easily.
                        </div>
                        <div style="margin-top:1px;">
                            • <strong>🟡 Resilient (5.5–6.9):</strong> Reliable vessel; succeeds through deliberate effort.
                        </div>
                        <div style="margin-top:1px;">
                            • <strong>🟠 Strained (4.0–5.4):</strong> Energy is sensitive or internalized; requires patience.
                        </div>
                        <div style="margin-top:1px;">
                            • <strong>🔴 Fragile (<4.0):</strong> Prone to fatigue; benefits from conscious remediation.
                        </div>
                    </div>
                </div>

                <!-- Card 9: Whole Signs vs Campanus -->
                <div class="key-card" style="background:#fcfaf5; border:1px solid #e5dccb; border-radius:4px; padding:6px 8px;">
                    <div style="font-weight:bold; color:#4a3325; font-size:7.2pt; border-bottom:1px solid #e5dccb; padding-bottom:3px; margin-bottom:4px; display:flex; align-items:center; gap:4px;">
                        <span>🏛️</span> 9. Whole Signs vs 3D Campanus Cusps
                    </div>
                    <div style="font-size:6.3pt; color:#475569; line-height:1.35;">
                        Ernst Wilhelm's Kala methodology uses both perspectives in harmony:
                        <div style="margin-top:2px;">
                            • <strong>Whole Sign Houses (Rāśis):</strong> Outer societal roles, archetypal life arenas, and house rulerships (what society sees you do).
                        </div>
                        <div style="margin-top:2px;">
                            • <strong>3D Campanus Cusps (Bhāvas):</strong> Exact astronomical division of local space. Reveals where a planet physically fell relative to the horizon at your birth.
                        </div>
                        <div style="margin-top:2px;">
                            • <strong>Bhāva Shifts (➔ Bhāva X):</strong> When a planet crosses into an adjacent Campanus house, its inner psychological feeling aligns with that Bhāva while outer circumstances follow the Whole Sign.
                        </div>
                    </div>
                </div>

            </div>
        </div>
    </div>
    """


def generate_report_html(chart_data: Dict[str, Any], options: Optional[Dict[str, Any]] = None) -> str:
    """Generates the complete, self-contained publication-grade HTML report."""
    opts = options or {}
    page_size = opts.get("page_size", "A3")
    chart_style = opts.get("chart_style", "north")  # north, south, circular
    notation = opts.get("notation", "symbol")        # symbol, english, devanagari, translit
    
    include_d1 = opts.get("include_d1", True)
    include_d9 = opts.get("include_d9", True)
    include_d10 = opts.get("include_d10", True)
    include_d7 = opts.get("include_d7", True)
    include_placements = opts.get("include_placements", True)
    include_cusps = opts.get("include_cusps", True)
    include_dignities = opts.get("include_dignities", True)
    include_avasthas = opts.get("include_avasthas", True) or opts.get("include_lajjitadi", True)
    include_lajjitadi = include_avasthas
    include_shadbala = opts.get("include_shadbala", True)
    include_yoga_judgment = opts.get("include_yoga_judgment", True)
    include_dasha = opts.get("include_dasha", True)
    include_vimshopaka = opts.get("include_vimshopaka", True)
    include_yogas = opts.get("include_yogas", True)
    include_master_diagnostics = opts.get("include_master_diagnostics", True)
    include_diagnostic_key = opts.get("include_diagnostic_key", True)
    biwheel_outer = opts.get("biwheel_outer", "D9")
    include_biwheel = opts.get("include_biwheel", True if (opts.get("preset") == "master_dossier_a4" or chart_style == "biwheel") else False)
    additional_vargas = opts.get("additional_vargas", [])
    
    subject = chart_data.get("subject_info", {})
    name = subject.get("name", "Native Chart")
    birth_dt = subject.get("birth_datetime", "").replace("T", " ")
    lat = subject.get("latitude", 0.0)
    lon = subject.get("longitude", 0.0)
    tz = subject.get("timezone_offset", 0.0)
    tz_sign = "+" if tz >= 0 else "-"
    tz_formatted = f"UTC{tz_sign}{abs(int(tz)):02d}:{int(abs(tz)%1*60):02d}"
    lat_str = f"{abs(lat):.4f}° {'N' if lat >= 0 else 'S'}"
    lon_str = f"{abs(lon):.4f}° {'E' if lon >= 0 else 'W'}"
    place = subject.get("place", "")
    place_str = f"{place} • " if place and place != "Custom" else ""
    
    astro = chart_data.get("astronomy", {})
    ayanamsa_name = astro.get("ayanamsa_name", "Dhruva Galactic Center (Middle of Mula)")
    current_dasha = get_current_dasha_badge(chart_data)
    
    # Extract D1 data
    d1_varga = chart_data.get("vargas", {}).get("D1", {})
    d1_grahas = d1_varga.get("grahas", {})
    d1_lagna = d1_varga.get("lagna", {})
    d1_cusps = d1_varga.get("cusps", [])
    d1_bhavas = d1_varga.get("bhavas", [])
    nak_grahas = chart_data.get("nakshatras", {}).get("grahas", {})
    shadbala_data = chart_data.get("shadbala", {})
    vimshottari_data = chart_data.get("vimshottari_dasha", {})
    
    # Map each planet to its Campanus Bhava number
    planet_to_house = {}
    for b in d1_bhavas:
        h_num = b.get("house")
        for pl in b.get("planets", []):
            planet_to_house[pl] = h_num
            
    # CSS size rules
    is_a3 = (page_size == "A3")
    css_page_size = "A3 landscape" if is_a3 else "A4 portrait"
    d1_svg_size = 310 if is_a3 else 260
    varga_svg_size = 220 if is_a3 else 175
    biwheel_svg_size = 400 if is_a3 else 355

    # 1. Generate D1 SVG
    d1_svg = get_chart_svg("D1", chart_data, chart_style, notation, width=d1_svg_size, height=d1_svg_size, biwheel_outer=biwheel_outer) if include_d1 else ""
    
    # 2. Build D1 Campanus Cusps Table
    cusps_rows = []
    if include_cusps and d1_cusps:
        for idx, c in enumerate(d1_cusps, 1):
            h_num = idx
            h_sign = c.get("sign", "-")
            h_deg = c.get("degree_0_to_30", 0.0)
            h_lord = SIGN_LORDS.get(h_sign, "-")
            
            # Find occupants of this Campanus bhava
            occ_list = []
            if idx - 1 < len(d1_bhavas):
                occ_names = d1_bhavas[idx - 1].get("planets", [])
                for pl in occ_names:
                    glyph = get_planet_glyph(pl, notation)
                    occ_list.append(f"<span class='glyph-badge' title='{pl}'>{glyph}</span>")
            occ_str = " ".join(occ_list) if occ_list else "<span style='color:#cbd5e1;'>—</span>"
            
            cusps_rows.append(f"""
            <tr>
                <td style="font-weight:700; color:#2563eb;">H{h_num}</td>
                <td style="font-weight:600;">{h_sign}</td>
                <td class="mono">{format_deg_short(h_deg)}</td>
                <td style="color:#64748b;">{h_lord}</td>
                <td>{occ_str}</td>
            </tr>
            """)
    cusps_html = "".join(cusps_rows)

    # 3. Build Planetary Placements Table
    placements_rows = []
    if include_placements:
        # Include Lagna row
        lagna_deg = d1_lagna.get("degree_0_to_30", 0.0)
        lagna_sign = d1_lagna.get("sign", "-")
        lagna_nak = nak_grahas.get("Lagna", {})
        lagna_glyph = get_planet_glyph("Lagna", notation)
        placements_rows.append(f"""
        <tr style="background-color: #f8fafc; font-weight: 600;">
            <td><span class="planet-badge asc">{lagna_glyph} Ascendant</span></td>
            <td><strong>{lagna_sign}</strong></td>
            <td class="mono">{format_deg(lagna_deg)}</td>
            <td><span class="badge neutral">Dir</span></td>
            <td>{lagna_nak.get('nakshatra', '-')} ({lagna_nak.get('pada', '-')})</td>
            <td style="color:#64748b;">{SIGN_LORDS.get(lagna_sign, '-')}</td>
            <td><span class="badge own">H1</span></td>
        </tr>
        """)
        for p in PLANETS_ORDER:
            if p not in d1_grahas:
                continue
            gdata = d1_grahas[p]
            glyph = get_planet_glyph(p, notation)
            p_sign = gdata.get("sign", "-")
            p_deg = gdata.get("degree_0_to_30", 0.0)
            is_retro = gdata.get("is_retrograde", False)
            retro_badge = '<span class="badge debil">R</span>' if is_retro else '<span class="badge neutral">D</span>'
            p_nak = nak_grahas.get(p, {})
            nak_str = f"{p_nak.get('nakshatra', '-')} ({p_nak.get('pada', '-')})" if p_nak else "-"
            
            h_assigned = planet_to_house.get(p, "-")
            h_str = f"H{h_assigned}" if h_assigned != "-" else "-"
                    
            placements_rows.append(f"""
            <tr>
                <td><span class="planet-badge">{glyph} {p}</span></td>
                <td><strong>{p_sign}</strong></td>
                <td class="mono">{format_deg(p_deg)}</td>
                <td>{retro_badge}</td>
                <td>{nak_str}</td>
                <td style="color:#64748b;">{SIGN_LORDS.get(p_sign, '-')}</td>
                <td><span class="badge neutral">{h_str}</span></td>
            </tr>
            """)
    placements_html = "".join(placements_rows)

    # 4. Build Compound Dignities Table (Panchadha Sambandha)
    dignity_rows = []
    if include_dignities:
        for p in PLANETS_ORDER:
            if p not in d1_grahas:
                continue
            gdata = d1_grahas[p]
            glyph = get_planet_glyph(p, notation)
            dbreak = gdata.get("dignity_breakdown", {})
            lord = dbreak.get("sign_lord", "-")
            nat_rel = dbreak.get("natural_relationship", "-")
            temp_rel = dbreak.get("temporary_relationship", "-")
            comp_rel = dbreak.get("compound_relationship", "-")
            final_dig = dbreak.get("final_dignity", "-")
            
            dignity_rows.append(f"""
            <tr>
                <td><span class="planet-badge">{glyph} {p}</span></td>
                <td style="color:#475569;">{lord}</td>
                <td style="font-size:7.5pt;">{nat_rel}</td>
                <td style="font-size:7.5pt;">{temp_rel}</td>
                <td style="font-weight:600;">{comp_rel}</td>
                <td>{dignity_badge(final_dig)}</td>
            </tr>
            """)
    dignities_html = "".join(dignity_rows)

    # 5. Build Vimshottari Dasha Major Cycles
    dasha_rows = []
    if include_dasha and vimshottari_data:
        mds = vimshottari_data.get("mahadashas", [])
        now = datetime.datetime.now()
        for md in mds:
            p = md.get("planet", "")
            s_str = md.get("start", "")
            e_str = md.get("end", "")
            years = md.get("years", "")
            is_active = False
            try:
                sd = datetime.datetime.strptime(s_str.split()[0], "%Y-%m-%d")
                ed = datetime.datetime.strptime(e_str.split()[0], "%Y-%m-%d")
                is_active = (sd <= now <= ed)
            except Exception:
                pass
                
            active_badge = '<span class="badge active-dasha">ACTIVE</span>' if is_active else ''
            row_bg = "background-color: #fef3c7;" if is_active else ""
            glyph = get_planet_glyph(p, notation)
            
            dasha_rows.append(f"""
            <tr style="{row_bg}">
                <td><span class="planet-badge">{glyph} {p}</span></td>
                <td style="color:#64748b;">{years}y</td>
                <td class="mono">{s_str}</td>
                <td class="mono">{e_str}</td>
                <td>{active_badge}</td>
            </tr>
            """)
    dasha_html = "".join(dasha_rows)

    # 6. Build Shadbala Strengths Table (Comprehensive Kala Breakdown Grid)
    shadbala_breakdown_html = render_shadbala_breakdown_table(shadbala_data, notation) if (include_shadbala and shadbala_data) else ""

    # 7. Build Qualitative & Lajjitādi Avasthās Table (Unified 4-Tier Grid)
    avasthas_calc_html = render_qualitative_avasthas_table(d1_grahas, notation) if include_avasthas else ""

    # 8. Build Strengths Matrix • Yoga Judgment Table
    yoga_judgment_html = render_yoga_judgment_table(shadbala_data, notation) if (include_yoga_judgment and shadbala_data) else ""

    # 8b. Build Classical Yogas & Yoga Bhanga Audit
    yogas_data = chart_data.get("yogas", {})
    yogas_html = render_classical_yogas_section(yogas_data, notation) if (include_yogas and yogas_data) else ""

    # 9. Build Divisional Clusters (D9, D10, D7)
    vargas_cards = []
    
    # D9 Navamsa
    if include_d9:
        d9_svg = get_chart_svg("D9", chart_data, chart_style, notation, width=varga_svg_size, height=varga_svg_size)
        d9_grahas = chart_data.get("vargas", {}).get("D9", {}).get("grahas", {})
        d9_lagna = chart_data.get("vargas", {}).get("D9", {}).get("lagna", {})
        ak_info = get_atmakaraka_info(chart_data)
        vargottamas = get_vargottama_planets(chart_data)
        
        d9_p_rows = []
        for p in PLANETS_ORDER:
            if p not in d9_grahas:
                continue
            g = d9_grahas[p]
            glyph = get_planet_glyph(p, notation)
            sign = g.get("sign", "-")
            deg = g.get("degree_0_to_30", 0.0)
            dig = g.get("dignity_breakdown", {}).get("final_dignity", "-")
            d9_p_rows.append(f"""
            <tr>
                <td>{glyph} {p}</td>
                <td><strong>{sign}</strong></td>
                <td class="mono">{format_deg_short(deg)}</td>
                <td>{dignity_badge(dig)}</td>
            </tr>
            """)
            
        varg_str = ", ".join(vargottamas) if vargottamas else "None"
        vargas_cards.append(f"""
        <div class="varga-card">
            <div class="varga-header">
                <h3>🏛️ D9 Navāṃśa • Dharma & Soul Destiny</h3>
                <span class="varga-sub">Swāṃśa: {d9_lagna.get('sign', '-')} • Kārakāṃśa: {ak_info.get('karakamsa', '-')}</span>
            </div>
            <div class="varga-body">
                <div class="varga-svg-container">{d9_svg}</div>
                <div class="varga-table-container">
                    <table class="data-table compact">
                        <thead><tr><th>Graha</th><th>D9 Sign</th><th>Deg</th><th>D9 Dignity</th></tr></thead>
                        <tbody>{''.join(d9_p_rows)}</tbody>
                    </table>
                    <div class="varga-diagnostics">
                        <div><strong>Swāṃśa (Soul):</strong> {d9_lagna.get('sign', '-')} (Lord: {SIGN_LORDS.get(d9_lagna.get('sign', '-'), '-')})</div>
                        <div><strong>Kārakāṃśa:</strong> {ak_info.get('karakamsa', '-')} (AK: {ak_info.get('planet', '-')})</div>
                        <div><strong>Vargottama:</strong> {varg_str}</div>
                    </div>
                </div>
            </div>
        </div>
        """)

    # D10 Dasamsa
    if include_d10:
        d10_svg = get_chart_svg("D10", chart_data, chart_style, notation, width=varga_svg_size, height=varga_svg_size)
        d10_grahas = chart_data.get("vargas", {}).get("D10", {}).get("grahas", {})
        d10_lagna = chart_data.get("vargas", {}).get("D10", {}).get("lagna", {})
        
        d10_p_rows = []
        for p in PLANETS_ORDER:
            if p not in d10_grahas:
                continue
            g = d10_grahas[p]
            glyph = get_planet_glyph(p, notation)
            sign = g.get("sign", "-")
            deg = g.get("degree_0_to_30", 0.0)
            dig = g.get("dignity_breakdown", {}).get("final_dignity", "-")
            d10_p_rows.append(f"""
            <tr>
                <td>{glyph} {p}</td>
                <td><strong>{sign}</strong></td>
                <td class="mono">{format_deg_short(deg)}</td>
                <td>{dignity_badge(dig)}</td>
            </tr>
            """)
            
        vargas_cards.append(f"""
        <div class="varga-card">
            <div class="varga-header">
                <h3>👑 D10 Daśāṃśa • Career, Status & Karma</h3>
                <span class="varga-sub">Lagna: {d10_lagna.get('sign', '-')} • 10th Lord in D10: {SIGN_LORDS.get(d10_lagna.get('sign', '-'), '-')}</span>
            </div>
            <div class="varga-body">
                <div class="varga-svg-container">{d10_svg}</div>
                <div class="varga-table-container">
                    <table class="data-table compact">
                        <thead><tr><th>Graha</th><th>D10 Sign</th><th>Deg</th><th>D10 Dignity</th></tr></thead>
                        <tbody>{''.join(d10_p_rows)}</tbody>
                    </table>
                    <div class="varga-diagnostics">
                        <div><strong>D10 Lagna:</strong> {d10_lagna.get('sign', '-')}</div>
                        <div><strong>10th House Lord:</strong> {SIGN_LORDS.get(d10_lagna.get('sign', '-'), '-')}</div>
                        <div><strong>Focus:</strong> Professional vocation, legacy & executive authority</div>
                    </div>
                </div>
            </div>
        </div>
        """)

    # D7 Saptamsa
    if include_d7:
        d7_svg = get_chart_svg("D7", chart_data, chart_style, notation, width=varga_svg_size, height=varga_svg_size)
        d7_grahas = chart_data.get("vargas", {}).get("D7", {}).get("grahas", {})
        d7_lagna = chart_data.get("vargas", {}).get("D7", {}).get("lagna", {})
        
        d7_p_rows = []
        for p in PLANETS_ORDER:
            if p not in d7_grahas:
                continue
            g = d7_grahas[p]
            glyph = get_planet_glyph(p, notation)
            sign = g.get("sign", "-")
            deg = g.get("degree_0_to_30", 0.0)
            dig = g.get("dignity_breakdown", {}).get("final_dignity", "-")
            d7_p_rows.append(f"""
            <tr>
                <td>{glyph} {p}</td>
                <td><strong>{sign}</strong></td>
                <td class="mono">{format_deg_short(deg)}</td>
                <td>{dignity_badge(dig)}</td>
            </tr>
            """)
            
        vargas_cards.append(f"""
        <div class="varga-card">
            <div class="varga-header">
                <h3>🌱 D7 Saptāṃśa • Progeny & Creative Fruit</h3>
                <span class="varga-sub">Lagna: {d7_lagna.get('sign', '-')} • 5th/7th Dynamics</span>
            </div>
            <div class="varga-body">
                <div class="varga-svg-container">{d7_svg}</div>
                <div class="varga-table-container">
                    <table class="data-table compact">
                        <thead><tr><th>Graha</th><th>D7 Sign</th><th>Deg</th><th>D7 Dignity</th></tr></thead>
                        <tbody>{''.join(d7_p_rows)}</tbody>
                    </table>
                    <div class="varga-diagnostics">
                        <div><strong>D7 Lagna:</strong> {d7_lagna.get('sign', '-')}</div>
                        <div><strong>5th Progeny Axis:</strong> Creative output, legacy & partnerships</div>
                    </div>
                </div>
            </div>
        </div>
        """)

    # Additional custom vargas if selected
    for extra_v in additional_vargas:
        if extra_v in chart_data.get("vargas", {}) and extra_v not in ["D1", "D9", "D10", "D7"]:
            e_svg = get_chart_svg(extra_v, chart_data, chart_style, notation, width=varga_svg_size, height=varga_svg_size)
            e_grahas = chart_data["vargas"][extra_v].get("grahas", {})
            e_lagna = chart_data["vargas"][extra_v].get("lagna", {})
            e_rows = []
            for p in PLANETS_ORDER:
                if p not in e_grahas:
                    continue
                g = e_grahas[p]
                glyph = get_planet_glyph(p, notation)
                sign = g.get("sign", "-")
                deg = g.get("degree_0_to_30", 0.0)
                dig = g.get("dignity_breakdown", {}).get("final_dignity", "-")
                e_rows.append(f"<tr><td>{glyph} {p}</td><td><strong>{sign}</strong></td><td class='mono'>{format_deg_short(deg)}</td><td>{dignity_badge(dig)}</td></tr>")
            
            v_title_full = VARGA_TITLES.get(extra_v, extra_v)
            vargas_cards.append(f"""
            <div class="varga-card">
                <div class="varga-header">
                    <h3>🏛️ {v_title_full}</h3>
                    <span class="varga-sub">Lagna: {e_lagna.get('sign', '-')}</span>
                </div>
                <div class="varga-body">
                    <div class="varga-svg-container">{e_svg}</div>
                    <div class="varga-table-container">
                        <table class="data-table compact">
                            <thead><tr><th>Graha</th><th>Sign</th><th>Deg</th><th>Dignity</th></tr></thead>
                            <tbody>{''.join(e_rows)}</tbody>
                        </table>
                    </div>
                </div>
            </div>
            """)

    vargas_cards_html = "".join(vargas_cards)

    # 10. Build 16-Varga Vimshopaka Dignity Matrix
    vimshopaka_matrix_html = ""
    if include_vimshopaka:
        v_scores = chart_data.get("varga_vimshopaka", {}).get("scores", {}).get("Shodasavarga", {})
        v_honors = chart_data.get("varga_vimshopaka", {}).get("vaisheshikamsa", {}).get("Shodasavarga", {})
        
        matrix_rows = []
        for p in CLASSICAL_PLANETS:
            glyph = get_planet_glyph(p, notation)
            cells = []
            for v in ALL_VARGAS_ORDER:
                v_g = chart_data.get("vargas", {}).get(v, {}).get("grahas", {}).get(p, {})
                dig = v_g.get("dignity_breakdown", {}).get("final_dignity", "-")
                short_d = dig
                if "Exalt" in dig: short_d = "Ex"
                elif "Moola" in dig: short_d = "MT"
                elif "Own" in dig: short_d = "Sva"
                elif "Great Friend" in dig: short_d = "GF"
                elif "Friend" in dig: short_d = "F"
                elif "Neutral" in dig: short_d = "N"
                elif "Great Enemy" in dig: short_d = "GE"
                elif "Enemy" in dig: short_d = "E"
                elif "Debilitat" in dig: short_d = "Deb"
                
                cell_class = "cell-neutral"
                if short_d in ["Ex", "MT", "Sva"]: cell_class = "cell-exalt"
                elif short_d in ["GF", "F"]: cell_class = "cell-friend"
                elif short_d in ["E", "GE", "Deb"]: cell_class = "cell-enemy"
                
                cells.append(f"<td class='matrix-cell {cell_class}' title='{p} in {v}: {dig}'>{short_d}</td>")
                
            score_val = v_scores.get(p, 0.0)
            raw_honor = v_honors.get(p)
            honor_display = "—"
            if isinstance(raw_honor, dict):
                h_name = raw_honor.get("honorific", "")
                h_meaning = raw_honor.get("meaning", "")
                if h_name and h_name != "--":
                    honor_display = f"<strong>{h_name}</strong>"
                    if h_meaning:
                        honor_display += f" <span style='color:#64748b;'>({h_meaning})</span>"
            elif isinstance(raw_honor, str) and raw_honor != "--":
                honor_display = raw_honor
                
            score_class = "high-score" if score_val >= 15.0 else ("mid-score" if score_val >= 10.0 else "low-score")
            
            matrix_rows.append(f"""
            <tr>
                <td><span class="planet-badge">{glyph} {p}</span></td>
                {''.join(cells)}
                <td class="mono font-bold {score_class}">{score_val:.2f} / 20</td>
                <td style="font-size:7.5pt;">{honor_display}</td>
            </tr>
            """)
            
        headers_th = "".join([f"<th>{v}</th>" for v in ALL_VARGAS_ORDER])
        vimshopaka_matrix_html = f"""
        <div class="card full-width">
            <div class="card-header">
                <h3>⚖️ 16-Varga Dignity & Viṃśopaka Strength Matrix (20-Point Total)</h3>
                <span class="card-sub">Evaluated across all 16 divisional charts with Vaiśeṣikāṃśa honorific classifications</span>
            </div>
            <div class="card-body">
                <table class="data-table matrix-table">
                    <thead>
                        <tr>
                            <th>Graha</th>
                            {headers_th}
                            <th>Viṃśopaka</th>
                            <th>Vaiśeṣikāṃśa Classification</th>
                        </tr>
                    </thead>
                    <tbody>{''.join(matrix_rows)}</tbody>
                </table>
            </div>
        </div>
        """

    # 11. Build Master Graha Diagnostics & Horizon Vitality
    lagna_vitality_card_html = render_lagna_vitality_card(chart_data, "D1") if include_master_diagnostics else ""
    master_diagnostics_table_html = render_master_graha_diagnostics_table(chart_data, "D1", notation) if include_master_diagnostics else ""

    # 12. Build Harmonic Bi-Wheel Section
    harmonic_biwheel_html = render_harmonic_biwheel_section(chart_data, outer_varga=biwheel_outer, notation=notation, svg_size=biwheel_svg_size) if include_biwheel else ""

    # 13. Build Master Astrological Diagnostic Key
    diagnostic_key_html = render_diagnostic_key_section() if include_diagnostic_key else ""

    # Calculate dynamic sequential page numbers for footer notes
    cur_p = 1
    p_d1_num = cur_p; cur_p += 1
    p_biwheel_num = cur_p if (include_biwheel and harmonic_biwheel_html) else 0
    if p_biwheel_num: cur_p += 1
    p_diag_num = cur_p if include_master_diagnostics else 0
    if p_diag_num: cur_p += 1
    p_vargas_num = cur_p if (include_d9 or include_d10 or include_d7 or include_vimshopaka or additional_vargas) else 0
    if p_vargas_num: cur_p += 1
    p_strengths_num = cur_p if (include_shadbala or include_avasthas or include_yoga_judgment) else 0
    if p_strengths_num: cur_p += 1
    p_yogas_num = cur_p if (include_yogas and yogas_html) else 0
    if p_yogas_num: cur_p += 1
    p_key_num = cur_p if (include_diagnostic_key and diagnostic_key_html) else 0
    if p_key_num: cur_p += 1

    # Assemble Full HTML
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Astra Astrological Master Plan - {name}</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700;800&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

  @page {{
    size: {css_page_size};
    margin: 8mm;
    @bottom-right {{
      content: counter(page) " / " counter(pages);
      font-family: 'Plus Jakarta Sans', sans-serif;
      font-size: 8pt;
      color: #94a3b8;
    }}
  }}

  * {{
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }}

  body {{
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    color: #3d312a;
    background-color: #fffdfa;
    font-size: 8pt;
    line-height: 1.35;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }}

  .page-container {{
    width: 100%;
    min-height: 100vh;
    padding: 0;
    margin: 0 auto;
  }}

  .page-break {{
    page-break-before: always;
  }}

  .avoid-break {{
    page-break-inside: avoid;
  }}

  /* Top Banner */
  .master-header {{
    background: #4a3325;
    color: #fffdfa;
    padding: 8px 14px;
    border-radius: 6px;
    margin-bottom: 8px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-left: 5px solid #d35400;
  }}

  .header-left {{
    display: flex;
    flex-direction: column;
    gap: 2px;
  }}

  .native-title {{
    font-family: 'Cinzel', Georgia, serif;
    font-size: 14pt;
    font-weight: 700;
    color: #fdf6e2;
    letter-spacing: 0.5px;
  }}

  .native-meta {{
    font-size: 7.5pt;
    color: #e5dccb;
    display: flex;
    gap: 12px;
  }}

  .header-center {{
    text-align: center;
    font-size: 7.5pt;
    color: #e5dccb;
    line-height: 1.3;
  }}

  .header-center strong {{
    color: #e5a03b;
    font-size: 8pt;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }}

  .header-right {{
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 3px;
  }}

  .dasha-pill {{
    background: rgba(211, 84, 0, 0.3);
    border: 1px solid #d35400;
    color: #fdf6e2;
    padding: 3px 8px;
    border-radius: 20px;
    font-size: 7.5pt;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 5px;
  }}

  /* Grid Layouts */
  .layout-3col {{
    display: grid;
    grid-template-columns: 330px 1.25fr 1.45fr;
    gap: 8px;
    margin-bottom: 8px;
  }}

  .layout-2col {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
    margin-bottom: 8px;
  }}

  .layout-vargas {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 8px;
    margin-bottom: 8px;
  }}

  .key-card {{
    background: #fcfaf5;
    border: 1px solid #e5dccb;
    border-radius: 4px;
    padding: 6px 8px;
    page-break-inside: avoid;
    break-inside: avoid;
  }}

  .column {{
    display: flex;
    flex-direction: column;
    gap: 6px;
  }}

  /* Card Containers */
  .card {{
    background: #ffffff;
    border-radius: 5px;
    border: 1px solid #dcb594;
    overflow: hidden;
  }}

  .card-header {{
    background: #eee5d3;
    padding: 4px 8px;
    border-bottom: 1px solid #dcb594;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }}

  .card-header h3 {{
    font-size: 8pt;
    font-weight: 700;
    color: #4a3325;
    display: flex;
    align-items: center;
    gap: 4px;
  }}

  .card-sub {{
    font-size: 6.5pt;
    color: #7c6853;
  }}

  .card-body {{
    padding: 3px;
  }}

  .full-width {{
    width: 100%;
  }}

  /* Chart SVG Container */
  .chart-card {{
    display: flex;
    justify-content: center;
    align-items: center;
    background: #ffffff;
    padding: 2px;
  }}

  .chart-card svg {{
    max-width: 100%;
    height: auto;
    display: block;
    margin: 0 auto;
  }}

  /* Data Tables */
  .data-table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 7pt;
    text-align: left;
  }}

  .data-table th {{
    background: #eee5d3;
    color: #4a3325;
    font-weight: 600;
    padding: 2.5px 4px;
    border: 1px solid #dcb594;
    text-transform: uppercase;
    font-size: 6.2pt;
    letter-spacing: 0.3px;
  }}

  .data-table td {{
    padding: 2px 4px;
    border: 1px solid #e5dccb;
    background: #fffdfa;
    color: #3d312a;
  }}

  .data-table tr:last-child td {{
    border-bottom: 1px solid #e5dccb;
  }}

  .data-table.compact th, .data-table.compact td {{
    padding: 1.5px 3px;
  }}

  /* Mono & Number formatting */
  .mono {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 7pt;
  }}

  .font-bold {{
    font-weight: 700;
  }}

  /* Badges */
  .badge {{
    display: inline-block;
    padding: 1px 4px;
    border-radius: 3px;
    font-size: 6pt;
    font-weight: 600;
    text-align: center;
    white-space: nowrap;
  }}

  .badge.exalt {{ background: #dcfce7; color: #166534; border: 1px solid #86efac; }}
  .badge.moola {{ background: #ecfdf5; color: #047857; border: 1px solid #a7f3d0; }}
  .badge.own {{ background: #dbeafe; color: #1e40af; border: 1px solid #93c5fd; }}
  .badge.great-friend {{ background: #f0fdf4; color: #15803d; border: 1px solid #bbf7d0; }}
  .badge.friend {{ background: #f8fafc; color: #15803d; border: 1px solid #e2e8f0; }}
  .badge.neutral {{ background: #f1f5f9; color: #475569; border: 1px solid #cbd5e1; }}
  .badge.enemy {{ background: #fff1f2; color: #9f1239; border: 1px solid #fecdd3; }}
  .badge.great-enemy {{ background: #ffedd5; color: #9a3412; border: 1px solid #fdba74; }}
  .badge.debil {{ background: #fee2e2; color: #991b1b; border: 1px solid #fca5a5; }}

  /* Lajjitadi Badges */
  .badge.state-proud {{ background: #dcfce7; color: #166534; border: 1px solid #86efac; }}
  .badge.state-delighted {{ background: #e0e7ff; color: #4338ca; border: 1px solid #c7d2fe; }}
  .badge.state-ashamed {{ background: #fef3c7; color: #b45309; border: 1px solid #fde68a; }}
  .badge.state-agitated {{ background: #fee2e2; color: #b91c1c; border: 1px solid #fca5a5; }}
  .badge.state-starved {{ background: #f3e8ff; color: #7e22ce; border: 1px solid #e9d5ff; }}
  .badge.state-thirsty {{ background: #ffedd5; color: #c2410c; border: 1px solid #fed7aa; }}

  .badge.active-dasha {{ background: #d35400; color: #ffffff; }}

  /* Classical Yoga Badges & Breakers */
  .badge.yoga-pure {{ background: #dcfce7; color: #166534; border: 1px solid #86efac; }}
  .badge.yoga-stained {{ background: #fef3c7; color: #b45309; border: 1px solid #fde68a; }}
  .badge.yoga-rescued {{ background: #e0e7ff; color: #4338ca; border: 1px solid #c7d2fe; }}
  .badge.yoga-broken {{ background: #fee2e2; color: #991b1b; border: 1px solid #fca5a5; }}
  .yoga-breaker-item {{ margin-bottom: 2px; color: #991b1b; }}
  .yoga-pos-item {{ margin-top: 2px; color: #15803d; font-size: 6.2pt; }}

  .planet-badge {{
    font-weight: 600;
    color: #4a3325;
    display: inline-flex;
    align-items: center;
    gap: 3px;
  }}

  .planet-badge.asc {{
    color: #b91c1c;
  }}

  .glyph-badge {{
    display: inline-block;
    background: #eee5d3;
    border-radius: 3px;
    padding: 1px 3px;
    font-size: 7.5pt;
    font-weight: 600;
    color: #1a4a82;
  }}

  /* Progress bar */
  .prog-bar {{
    display: inline-block;
    width: 28px;
    height: 5px;
    background: #e2e8f0;
    border-radius: 2.5px;
    overflow: hidden;
    vertical-align: middle;
  }}

  .prog-fill {{
    display: block;
    height: 100%;
    background: #3b82f6;
    border-radius: 2.5px;
  }}

  /* Varga Cards */
  .varga-card {{
    background: #ffffff;
    border: 1px solid #dcb594;
    border-radius: 5px;
    overflow: hidden;
    display: flex;
    flex-direction: column;
  }}

  .varga-header {{
    background: #eee5d3;
    padding: 4px 8px;
    border-bottom: 1px solid #dcb594;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }}

  .varga-header h3 {{
    font-size: 8pt;
    font-weight: 700;
    color: #4a3325;
  }}

  .varga-sub {{
    font-size: 6.5pt;
    color: #7c6853;
  }}

  .varga-body {{
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
    padding: 4px;
  }}

  .varga-svg-container {{
    width: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
  }}

  .varga-table-container {{
    width: 100%;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }}

  .varga-diagnostics {{
    margin-top: 3px;
    padding: 3px 5px;
    background: #fcfaf5;
    border: 1px solid #e5dccb;
    border-radius: 3px;
    font-size: 6.5pt;
    line-height: 1.25;
    color: #4a3325;
  }}

  /* 16-Varga Matrix Styling */
  .matrix-table th {{
    font-size: 6pt;
    padding: 2px 2px;
    text-align: center;
    background: #eee5d3;
    color: #4a3325;
    border: 1px solid #dcb594;
  }}

  .matrix-cell {{
    text-align: center;
    font-size: 6.2pt;
    font-weight: 600;
    padding: 1.5px 1px;
    border: 1px solid #e5dccb;
  }}

  .cell-exalt {{ background-color: #dcfce7; color: #166534; }}
  .cell-friend {{ background-color: #f0fdf4; color: #15803d; }}
  .cell-neutral {{ background-color: #fffdfa; color: #64748b; }}
  .cell-enemy {{ background-color: #fee2e2; color: #991b1b; }}

  .high-score {{ color: #15803d; }}
  .mid-score {{ color: #b45309; }}
  .low-score {{ color: #b91c1c; }}

  /* Footer note */
  .footer-note {{
    margin-top: 6px;
    text-align: center;
    font-size: 7pt;
    color: #7c6853;
    border-top: 1px solid #dcb594;
    padding-top: 3px;
  }}
</style>
</head>
<body>

  <!-- PAGE 1: D1 RASI ROOT ARCHITECTURE -->
  <div class="page-container avoid-break">
    
    <!-- Master Header Banner -->
    <div class="master-header">
      <div class="header-left">
        <div class="native-title">{name}</div>
        <div class="native-meta">
          <span>📅 {birth_dt}</span>
          <span>📍 {place_str}{lat_str}, {lon_str}</span>
          <span>🌐 {tz_formatted}</span>
        </div>
      </div>
      <div class="header-center">
        <strong>Astra Integrated Astrological Master Plan</strong><br>
        Tropical Signs • Campanus Bhavas • Sidereal Equatorial Nakshatras (Dhruva Center)
      </div>
      <div class="header-right">
        <div class="dasha-pill">
          <span>⏱️ Active Daśā:</span>
          <span>{current_dasha}</span>
        </div>
        <span style="font-size: 6.5pt; color: #e5dccb;">Computed dynamically via Swiss Ephemeris</span>
      </div>
    </div>

    <!-- 2-Column Core Architecture -->
    <div class="layout-2col">
      
      <!-- COLUMN 1: D1 Chart & Campanus Cusps -->
      <div class="column">
        {f'''
        <div class="card chart-card">
          {d1_svg}
        </div>
        ''' if include_d1 else ''}

        {f'''
        <div class="card">
          <div class="card-header">
            <h3>🏛️ Campanus Bhava Cusps</h3>
            <span class="card-sub">12 Primary Life Arenas</span>
          </div>
          <div class="card-body">
            <table class="data-table compact">
              <thead>
                <tr>
                  <th>House</th>
                  <th>Sign</th>
                  <th>Cusp Deg</th>
                  <th>Lord</th>
                  <th>Occupants</th>
                </tr>
              </thead>
              <tbody>
                {cusps_html}
              </tbody>
            </table>
          </div>
        </div>
        ''' if include_cusps else ''}
      </div>

      <!-- COLUMN 2: Placements, 5-Fold Dignities & Vimshottari Dasha -->
      <div class="column">
        {f'''
        <div class="card">
          <div class="card-header">
            <h3>🌟 Planetary Placements & Nakshatras</h3>
            <span class="card-sub">Sidereal Nakshatras & Pada</span>
          </div>
          <div class="card-body">
            <table class="data-table compact">
              <thead>
                <tr>
                  <th>Graha</th>
                  <th>Sign</th>
                  <th>Degree</th>
                  <th>Mot</th>
                  <th>Nakshatra (Pada)</th>
                  <th>Ruler</th>
                  <th>House</th>
                </tr>
              </thead>
              <tbody>
                {placements_html}
              </tbody>
            </table>
          </div>
        </div>
        ''' if include_placements else ''}

        {f'''
        <div class="card">
          <div class="card-header">
            <h3>⚖️ Pañcadhā Sambandha (5-Fold Dignities)</h3>
            <span class="card-sub">Natural + Temporal Relationship</span>
          </div>
          <div class="card-body">
            <table class="data-table compact">
              <thead>
                <tr>
                  <th>Graha</th>
                  <th>Sign Lord</th>
                  <th>Natural</th>
                  <th>Temporal</th>
                  <th>Compound</th>
                  <th>Final Dignity</th>
                </tr>
              </thead>
              <tbody>
                {dignities_html}
              </tbody>
            </table>
          </div>
        </div>
        ''' if include_dignities else ''}

        {f'''
        <div class="card">
          <div class="card-header">
            <h3>⏳ Vimśottarī Daśā Major Cycles</h3>
            <span class="card-sub">120-Year Parashari Timeline</span>
          </div>
          <div class="card-body">
            <table class="data-table compact">
              <thead>
                <tr>
                  <th>Lord</th>
                  <th>Span</th>
                  <th>Period Start</th>
                  <th>Period End</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {dasha_html}
              </tbody>
            </table>
          </div>
        </div>
        ''' if include_dasha else ''}
      </div>

    </div>

    <div class="footer-note">
      Astra Precision Astrological Computation • Page {p_d1_num}: Root Rāśi Chart & Core Astronomy • Report Generated for {name}
    </div>

  </div>

  {f'''
  <!-- HARMONIC BI-WHEEL ARCHITECTURE (CONCENTRIC DUAL-WHEEL & CROSS-VARGA OVERLAY) -->
  <div class="page-container page-break avoid-break">
    
    <!-- Harmonic Bi-Wheel Header Banner -->
    <div class="master-header">
      <div class="header-left">
        <div class="native-title">{name} • Harmonic Bi-Wheel Architecture</div>
        <div class="native-meta">
          <span>D1 Root Natal (Physical Reality) ➔ {biwheel_outer} Harmonic Overlay</span>
          <span>Concentric Dual-Wheel Projection</span>
          <span>Tropical Rāśis & Campanus Bhavas</span>
        </div>
      </div>
      <div class="header-right">
        <span style="font-size: 7.5pt; color: #e5a03b; font-weight:600;">{ayanamsa_name}</span>
        <span style="font-size: 6.5pt; color: #e5dccb;">Vic DiCara & Ernst Wilhelm Kala Harmonic Calibration</span>
      </div>
    </div>

    <!-- Harmonic Bi-Wheel Section Grid -->
    {harmonic_biwheel_html}

    <div class="footer-note">
      Astra Precision Astrological Computation • Page {p_biwheel_num}: Harmonic Bi-Wheel Architecture & Cross-Varga Overlay • Report Generated for {name}
    </div>

  </div>
  ''' if (include_biwheel and harmonic_biwheel_html) else ''}

  {f'''
  <!-- MASTER GRAHA DIAGNOSTICS & HORIZON VITALITY -->
  <div class="page-container page-break avoid-break">
    
    <!-- Header Banner -->
    <div class="master-header">
      <div class="header-left">
        <div class="native-title">{name} • Master Graha Diagnostics & Horizon Vitality</div>
        <div class="native-meta">
          <span>5-Pillar Horizon Vitality</span>
          <span>Pañcadhā Maitrī</span>
          <span>Ṣaḍbala Virūpas & Rank</span>
          <span>Lajjitādi Feelings</span>
          <span>Net Dṛṣṭi Weather</span>
        </div>
      </div>
      <div class="header-right">
        <span style="font-size: 7.5pt; color: #e5a03b; font-weight:600;">Executive Multi-Dimensional Synthesis</span>
        <span style="font-size: 6.5pt; color: #e5dccb;">Dynamic Swiss Ephemeris Computation</span>
      </div>
    </div>

    <!-- Executive Lagna Vitality Architecture Card -->
    {lagna_vitality_card_html}

    <!-- Master Graha Diagnostics Unified Matrix Table -->
    {master_diagnostics_table_html}

    <div class="footer-note">
      Astra Precision Astrological Computation • Page {p_diag_num}: Master Graha Diagnostics & Horizon Vitality • Report Generated for {name}
    </div>

  </div>
  ''' if include_master_diagnostics else ''}

  {f'''
  <!-- DIVISIONAL ARCHITECTURE (VARGAS) -->
  <div class="page-container page-break avoid-break">
    
    <!-- Header Banner -->
    <div class="master-header">
      <div class="header-left">
        <div class="native-title">{name} • Divisional Architecture (Vargas)</div>
        <div class="native-meta">
          <span>Soul Trajectory (D9 Navāṃśa)</span>
          <span>Career & Great Status (D10 Daśāṃśa)</span>
          <span>Progeny & Relationships (D7 Saptāṃśa)</span>
        </div>
      </div>
      <div class="header-right">
        <span style="font-size: 7.5pt; color: #e5a03b; font-weight:600;">16-in-1 Shodashavarga Precision Analysis</span>
        <span style="font-size: 6.5pt; color: #e5dccb;">Campanus House Cusps & Equal Divisions</span>
      </div>
    </div>

    <!-- Vargas Modular Cards (D9, D10, D7) -->
    <div class="layout-vargas">
      {vargas_cards_html}
    </div>

    <!-- 16-Varga Vimshopaka Dignity Matrix -->
    {vimshopaka_matrix_html}

    <div class="footer-note">
      Astra Precision Astrological Computation • Page {p_vargas_num}: Divisional Architecture & 16-Varga Viṃśopaka Scoring • Report Generated for {name}
    </div>

  </div>
  ''' if (include_d9 or include_d10 or include_d7 or include_vimshopaka or additional_vargas) else ''}

  {f'''
  <!-- DEEP PLANETARY STRENGTHS (ṢAḌBALA & QUALITATIVE AVASTHĀS) -->
  <div class="page-container page-break avoid-break">
    
    <!-- Header Banner -->
    <div class="master-header">
      <div class="header-left">
        <div class="native-title">{name} • Deep Planetary Strengths & Potencies</div>
        <div class="native-meta">
          <span>Ṣaḍbala 6-Fold Potency Grid</span>
          <span>Qualitative & Lajjitādi Avasthās</span>
          <span>Kala Yoga Judgment Matrix</span>
        </div>
      </div>
      <div class="header-right">
        <span style="font-size: 7.5pt; color: #e5a03b; font-weight:600;">Mathematical Engine Foundations</span>
        <span style="font-size: 6.5pt; color: #e5dccb;">Parashara Virūpas & Threshold Ratios</span>
      </div>
    </div>

    <!-- Top Row: Qualitative Avasthas & Yoga Judgment in 2 Columns -->
    <div class="layout-2col">
      <div class="column">
        {f'''
        <div class="card">
          <div class="card-header">
            <h3>🌿 Qualitative Avasthās & Lajjitādi Avasthās</h3>
            <span class="card-sub">Alertness, Vitality, Mood & Feelings</span>
          </div>
          <div class="card-body">
            {avasthas_calc_html}
          </div>
        </div>
        ''' if include_avasthas else ''}
      </div>

      <div class="column">
        {f'''
        <div class="card">
          <div class="card-header">
            <h3>🎯 Strengths Matrix • Yoga Judgment</h3>
            <span class="card-sub">Ishta/Kashta & Subha/Asubha Dig Bala</span>
          </div>
          <div class="card-body">
            {yoga_judgment_html}
          </div>
        </div>
        ''' if include_yoga_judgment else ''}
      </div>
    </div>

    <!-- Bottom Row: Shadbala Strength Breakdown Grid (Full Width) -->
    {f'''
    <div class="card full-width" style="margin-top:6px;">
      <div class="card-header">
        <h3>⚖️ Ṣaḍbala Strength Matrix & Breakdown Grid</h3>
        <span class="card-sub">Parashara 6-Fold Potencies & Minimum Thresholds</span>
      </div>
      <div class="card-body">
        {shadbala_breakdown_html}
      </div>
    </div>
    ''' if include_shadbala else ''}

    <div class="footer-note">
      Astra Precision Astrological Computation • Page {p_strengths_num}: Deep Planetary Strengths & Potency Matrix • Report Generated for {name}
    </div>

  </div>
  ''' if (include_shadbala or include_avasthas or include_yoga_judgment) else ''}

  {f'''
  <!-- CLASSICAL YOGAS & YOGA BHANGA AUDIT -->
  <div class="page-container page-break avoid-break">
    
    <!-- Header Banner -->
    <div class="master-header">
      <div class="header-left">
        <div class="native-title">{name} • Classical Yogas & Yoga Bhanga Audit</div>
        <div class="native-meta">
          <span>9 Classical Parāśari Categories</span>
          <span>Trishādaya Intrusion Audit</span>
          <span>Nīca Bhaṅga 6-Fold Redemption</span>
        </div>
      </div>
      <div class="header-right">
        <span style="font-size: 7.5pt; color: #e5a03b; font-weight:600;">Classical Scriptural Authority</span>
        <span style="font-size: 6.5pt; color: #e5dccb;">BPHS Ch. 34-42, 75 • Phaladeepika Ch. 6-7</span>
      </div>
    </div>

    <!-- Classical Yogas Master Table -->
    {yogas_html}

    <div class="footer-note">
      Astra Precision Astrological Computation • Page {p_yogas_num}: Classical Yogas & Plausibility Audit • Report Generated for {name}
    </div>

  </div>
  ''' if (include_yogas and yogas_html) else ''}

  {f'''
  <!-- MASTER ASTROLOGICAL DIAGNOSTIC KEY -->
  <div class="page-container page-break avoid-break">
    
    <!-- Header Banner -->
    <div class="master-header">
      <div class="header-left">
        <div class="native-title">{name} • Astrological Diagnostic Key & Pedagogical Guide</div>
        <div class="native-meta">
          <span>Decoded Tooltips & Inline Badges</span>
          <span>Psychological Feeling States</span>
          <span>Synthesis Formulas for Readers</span>
        </div>
      </div>
      <div class="header-right">
        <span style="font-size: 7.5pt; color: #e5a03b; font-weight:600;">Self-Contained Reader Reference</span>
        <span style="font-size: 6.5pt; color: #e5dccb;">Kala Integrated Methodology Manual</span>
      </div>
    </div>

    <!-- Master Diagnostic Key (9 Educational Cards) -->
    {diagnostic_key_html}

    <div class="footer-note">
      Astra Precision Astrological Computation • Page {p_key_num}: Master Astrological Diagnostic Key & Reference Guide • Report Generated for {name}
    </div>

  </div>
  ''' if (include_diagnostic_key and diagnostic_key_html) else ''}

</body>
</html>
"""
    return html_content


def export_chart_pdf(chart_data: Dict[str, Any], options: Optional[Dict[str, Any]] = None) -> bytes:
    """
    Renders publication-grade PDF bytes using headless Chromium (Playwright).
    Supports A3 landscape master sheets and multi-page dossiers.
    """
    opts = options or {}
    page_size = opts.get("page_size", "A3")
    is_a3 = (page_size == "A3")
    
    html = generate_report_html(chart_data, opts)
    subject_name = chart_data.get("subject_info", {}).get("name", "Native")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        vp_width = 1920 if is_a3 else 1280
        vp_height = 1080 if is_a3 else 1600
        page = browser.new_page(viewport={"width": vp_width, "height": vp_height})
        
        page.set_content(html, wait_until="networkidle")
        
        header_tmpl = f'<div style="font-size: 7pt; color: #94a3b8; width: 100%; text-align: right; padding-right: 8mm; font-family: -apple-system, sans-serif;">{subject_name} • Astra Astrological Master Plan</div>'
        footer_tmpl = '<div style="font-size: 7pt; color: #94a3b8; width: 100%; display: flex; justify-content: space-between; padding: 0 8mm; font-family: -apple-system, sans-serif;"><span>Astra Astrological Computation Engine • Kala Integrated Approach</span><span>Page <span class="pageNumber"></span> of <span class="totalPages"></span></span></div>'
        
        pdf_bytes = page.pdf(
            format=page_size,
            landscape=is_a3,
            print_background=True,
            margin={"top": "8mm", "bottom": "8mm", "left": "8mm", "right": "8mm"},
            display_header_footer=True,
            header_template=header_tmpl,
            footer_template=footer_tmpl
        )
        browser.close()
        
    return pdf_bytes
