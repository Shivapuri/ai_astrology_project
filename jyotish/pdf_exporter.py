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
    height: int = 330
) -> str:
    """Generates clean, embedded SVG string for a given varga."""
    v_data = chart_data.get("vargas", {}).get(varga_key)
    if not v_data:
        return f"<div style='width:{width}px; height:{height}px; display:flex; align-items:center; justify-content:center; background:#f1f5f9; color:#64748b;'>{varga_key} Data Unavailable</div>"
    
    items = draw_chart.parse_varga_data(v_data)
    v_title = VARGA_TITLES.get(varga_key, varga_key)
    
    if chart_style == "south":
        svg = draw_chart.generate_south_indian(items, mode=notation, varga_name=v_title)
    elif chart_style == "circular":
        ayanamsa = chart_data.get("astronomy", {}).get("equatorial_ayanamsa_value", 0.0)
        svg = draw_chart.generate_circular_chart(items, mode=notation, varga_name=v_title, ayanamsha=ayanamsa)
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
    varga_svg_size = 240 if is_a3 else 220

    # 1. Generate D1 SVG
    d1_svg = get_chart_svg("D1", chart_data, chart_style, notation, width=d1_svg_size, height=d1_svg_size) if include_d1 else ""
    
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

  .layout-vargas {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 8px;
    margin-bottom: 8px;
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
    flex-direction: row;
    gap: 6px;
    padding: 4px;
  }}

  .varga-svg-container {{
    flex: 0 0 {varga_svg_size}px;
    display: flex;
    justify-content: center;
    align-items: center;
  }}

  .varga-table-container {{
    flex: 1;
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

  <!-- PAGE 1: D1 RASI MASTER DIAGNOSTIC -->
  <div class="page-container avoid-break">
    
    <!-- Master Header Banner -->
    <div class="master-header">
      <div class="header-left">
        <div class="native-title">{name}</div>
        <div class="native-meta">
          <span>📅 {birth_dt}</span>
          <span>📍 {lat_str}, {lon_str}</span>
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

    <!-- 3-Column Core Predictive Architecture -->
    <div class="layout-3col">
      
      <!-- COLUMN 1: D1 Chart, Campanus Cusps & Vimshottari Dasha -->
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

      <!-- COLUMN 2: Placements, Dignities, Qualitative Avasthas & Yoga Judgment -->
      <div class="column">
        {f'''
        <div class="card">
          <div class="card-header">
            <h3>🌟 Planetary Placements & Nakshatras</h3>
            <span class="card-sub">Sidereal Nakshatras & Pada</span>
          </div>
          <div class="card-body">
            <table class="data-table">
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
            <table class="data-table">
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
            <h3>🌿 Qualitative Avasthās & Lajjitādi Avasthās</h3>
            <span class="card-sub">Alertness, Vitality, Mood & Feelings</span>
          </div>
          <div class="card-body">
            {avasthas_calc_html}
          </div>
        </div>
        ''' if include_avasthas else ''}

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

      <!-- COLUMN 3: Shadbala Strength Breakdown Grid -->
      <div class="column">
        {f'''
        <div class="card">
          <div class="card-header">
            <h3>⚖️ Ṣaḍbala Strength Matrix & Breakdown Grid</h3>
            <span class="card-sub">Parashara 6-Fold Potencies & Minimum Thresholds</span>
          </div>
          <div class="card-body">
            {shadbala_breakdown_html}
          </div>
        </div>
        ''' if include_shadbala else ''}
      </div>

    </div>

    <div class="footer-note">
      Astra Precision Astrological Computation • Page 1: Root Rāśi Chart & Core Diagnostics • Report Generated for {name}
    </div>

  </div>

  {f'''
  <!-- PAGE 2: DIVISIONAL ARCHITECTURE (VARGAS) -->
  <div class="page-container page-break avoid-break">
    
    <!-- Page 2 Header Banner -->
    <div class="master-header">
      <div class="header-left">
        <div class="native-title">{name} • Divisional Architecture (Vargas)</div>
        <div class="native-meta">
          <span>Soul Trajectory (D9)</span>
          <span>Career & Great Status (D10)</span>
          <span>Progeny & Relationships (D7)</span>
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
      Astra Precision Astrological Computation • Page 2: Divisional Architecture & 16-Varga Viṃśopaka Scoring • Report Generated for {name}
    </div>

  </div>
  ''' if (include_d9 or include_d10 or include_d7 or include_vimshopaka or additional_vargas) else ''}

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
