#!/usr/bin/env python3
"""
jyotish/text_exporter.py
Publication-Grade Markdown & Text Dossier Exporter for Astra.

Generates dense, structured, AI-ready astrological dossiers following
Ernst Wilhelm's Kala Integrated Methodology:
- Tropical Signs (Sayana) for Rasi and Divisional Vargas
- Campanus 3D House System for true spatial Bhava Cusps
- Sidereal Equatorial Nakshatras anchored to Dhruva Galactic Center (0° Mula)

Formats the complete 9-column Master Graha Diagnostics, Chara Karakas,
Master Lords, D9 Navamsha, D10 Dashamsha, Campanus Cusps, Vimshottari Dashas,
and Classical Yogas into a format optimized for deep LLM interpretation.
"""

import datetime
from typing import Dict, Any, Optional, List

from jyotish.relationships.relationships import SIGN_LORDS
from jyotish.planetary_evaluation import (
    calculate_baladi_avastha,
    classify_graha_quadrant,
    calculate_graha_vitality,
    detect_planetary_wars
)
from jyotish.planetary_evaluation.planetary_evaluation import get_dignity_score
from jyotish.nakshatra_metadata import get_nakshatra_metadata

SIGNS_LIST = [
    "Aries", "Taurus", "Gemini", "Cancer",
    "Leo", "Virgo", "Libra", "Scorpio",
    "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

PLANETS_ORDER = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]

HOUSE_SIGNIFICATIONS = {
    1: "Tanu (Self, physical vitality, constitution, overall life direction)",
    2: "Dhana (Wealth, earned assets, family lineage, speech, truthfulness)",
    3: "Sahaja (Courage, initiatives, younger siblings, fine skills, effort)",
    4: "Bandhu (Home, emotional peace, mother, landed property, conveyances)",
    5: "Putra (Creativity, intelligence, children, past life merit, devotion)",
    6: "Ari (Daily work, service, obstacles, debts, health management, debts)",
    7: "Yuvati (Partnership, marriage, contracts, interpersonal diplomacy)",
    8: "Randhra (Longevity, transformations, shared assets, occult research)",
    9: "Dharma (Higher wisdom, father/guru, spiritual purpose, fortune)",
    10: "Karma (Career, public status, executive leadership, visible contribution)",
    11: "Labha (Gains, aspirations, professional network, elder siblings, income)",
    12: "Vyaya (Liberation, foreign lands, expenditure, solitude, subconscious)"
}


def format_deg(val: float) -> str:
    """Formats decimal degree (0.0 - 30.0) into clean deg°min' string."""
    d = int(val)
    m = int(round((val - d) * 60.0))
    if m >= 60:
        d += 1
        m -= 60
    return f"{d:02d}°{m:02d}'"


def get_campanus_house_num(planet_name: str, default_house: int, bhavas: List[Dict[str, Any]]) -> int:
    """Returns the Campanus house number for a planet from bhavas list."""
    if not bhavas:
        return default_house
    for b in bhavas:
        if planet_name in b.get("planets", []):
            return int(b.get("house", default_house))
    return default_house


def clean_dignity_name(dig_str: str) -> str:
    """Cleans raw dignity strings like 'Own's Sign' -> 'Own Sign'."""
    raw = (dig_str or "Neutral").replace("'s Sign", "").replace(" Sign", "").strip()
    return raw if raw else "Neutral"


def generate_chart_ai_markdown(chart_data: Dict[str, Any], options: Optional[Dict[str, Any]] = None) -> str:
    """
    Serializes complete Astra chart data into a high-density, structured Markdown dossier.
    Optimized for modern AI assistants (Claude, ChatGPT, Gemini) to interpret deeply.
    """
    if not chart_data:
        return "# Astrological Chart Dossier\n\n*No chart data provided.*"

    opts = options or {}
    preset = opts.get("preset", "full")  # 'full', 'diagnostics_only', 'summary'

    include_prompt_header = opts.get("include_prompt_header", True) if preset != "diagnostics_only" else False
    include_master_diagnostics = opts.get("include_master_diagnostics", True)
    include_archetypes = opts.get("include_archetypes", True) if preset == "full" else False
    include_vargas = opts.get("include_vargas", True) if preset == "full" else False
    include_cusps = opts.get("include_cusps", True) if preset != "diagnostics_only" else False
    include_dashas = opts.get("include_dashas", True) if preset != "diagnostics_only" else False
    include_yogas = opts.get("include_yogas", True) if preset == "full" else False

    subject_info = chart_data.get("subject_info", {})
    name = subject_info.get("name", "Subject")
    birth_dt = str(subject_info.get("birth_datetime", "")).strip()
    if birth_dt and " " in birth_dt:
        dt_parts = birth_dt.split(" ", 1)
        calc_date = dt_parts[0]
        calc_time = dt_parts[1]
    else:
        calc_date = birth_dt
        calc_time = "-"

    date_str = subject_info.get("date") or calc_date or "-"
    time_str = subject_info.get("time") or calc_time or "-"
    place_str = subject_info.get("place") or chart_data.get("astronomy", {}).get("place") or "Coordinates"
    lat_val = subject_info.get("lat") if subject_info.get("lat") is not None else subject_info.get("latitude", "-")
    lon_val = subject_info.get("lon") if subject_info.get("lon") is not None else subject_info.get("longitude", "-")
    tz_val = subject_info.get("tz") if subject_info.get("tz") is not None else subject_info.get("timezone_offset", "-")

    vargas = chart_data.get("vargas", {})
    d1 = vargas.get("D1", {})
    d1_grahas = d1.get("grahas", {})
    d1_lagna = d1.get("lagna", {})
    d1_bhavas = d1.get("bhavas", [])
    d1_cusps = d1.get("cusps", [])

    shadbala = chart_data.get("shadbala", {})
    naks = chart_data.get("nakshatras", {}).get("grahas", {})
    adv_aspects = chart_data.get("advanced_aspects", {})
    pe = chart_data.get("planetary_evaluation", {})
    karakas = chart_data.get("karakas", {})
    chara_karakas = karakas.get("chara", {})
    functional_karakas = karakas.get("functional", {})

    master_lords = pe.get("summary", {}).get("master_lords", {})
    lagna_lord_p = master_lords.get("lagna_lord", {}).get("planet", "")
    drekkana_lord_p = master_lords.get("drekkana_lord", {}).get("planet", "")
    navamsha_lord_p = master_lords.get("navamsha_lord", {}).get("planet", "")

    lg_sign = d1_lagna.get("sign", "Aries")
    lg_deg_val = float(d1_lagna.get("degree_0_to_30", 0.0))
    lg_deg_str = format_deg(lg_deg_val)
    lg_lord = SIGN_LORDS.get(lg_sign, d1_lagna.get("lord", "-"))
    lg_nak_data = naks.get("Lagna", {})
    lg_nak_name = lg_nak_data.get("nakshatra") or d1_lagna.get("nakshatra", "-")
    lg_nak_pada = lg_nak_data.get("pada") or d1_lagna.get("nakshatra_pada", 1)

    sections = []

    # =========================================================================
    # Header & Calculation Metadata
    # =========================================================================
    header_lines = [
        f"# Astrological Master Dossier: {name}",
        f"**Engine**: Astra Precision Kala Computation (`swisseph`)",
        "",
        "### Astrological Calculation Framework",
        "- **Zodiac**: **Tropical Signs (Sāyana)** for Rasi and all Divisional Vargas (BPHS / Ernst Wilhelm Kala methodology).",
        "- **House System**: **Campanus 3D House System** (true spatial horizon cusps).",
        "- **Nakshatras**: **Sidereal Equatorial Nakshatras** anchored to the **Dhruva Galactic Center** (0°00' Mūla).",
        "",
        "### Birth & Chart Coordinates",
        f"- **Native**: {name}",
        f"- **Birth Date & Time**: {date_str} at {time_str} (Local Time)",
        f"- **Location**: {place_str} (Lat: {lat_val}, Lon: {lon_val}, TZ: {tz_val})",
        f"- **Ascendant (Lagna)**: **{lg_sign} {lg_deg_str}** | Nakshatra: **{lg_nak_name}** (Pada {lg_nak_pada}) | Captain (Lagneśa): **{lg_lord}**",
        ""
    ]
    sections.append("\n".join(header_lines))

    # =========================================================================
    # AI System Prompt & Guidance Framing
    # =========================================================================
    if include_prompt_header:
        prompt_lines = [
            "---",
            "",
            "## 0. AI Interpretation Directive & Prompt Header",
            "> **Role**: You are an enlightened, compassionate, and precise Vedic astrologer evaluating this natal horoscope.",
            "> **Critical Technical Context**: This chart is calculated using **Ernst Wilhelm's Kala integrated paradigm**:",
            "> 1. Signs are **Tropical** (the solstices define 0° Cancer/Capricorn; signs describe psychological seasons & physical vehicles).",
            "> 2. House Cusps are **Campanus 3D** (the true physical horizon and prime vertical).",
            "> 3. Nakshatras are **Sidereal Equatorial** (the cosmic background star field anchored to the Galactic Center).",
            "> *Do not convert these Tropical placements back into sidereal signs; analyze the signs, houses, and nakshatras exactly as given below.*",
            ">",
            "> **Interpretation Protocol**:",
            "> - **Core Horizon Vitality**: First analyze the Ascendant, its Lord (Lagneśa), and the Moon to evaluate mental temperament, biological vitality, and emotional baseline.",
            "> - **Soul Purpose & Swāṃśa**: Interpret the Ātmakāraka (Soul significator) and its placement in D1 and D9 (Kārakāṃśa/Svāṃśa).",
            "> - **Career & Worldly Karma**: Synthesize the 10th house, D10 Daśāṃśa, and Amātyakāraka (career intellect).",
            "> - **Relationships & Partnerships**: Evaluate the 7th house, Venus, D9 Navāṃśa, and Dārākāraka.",
            "> - **Timing of Life Cycles**: Synthesize the active Vimśottarī Daśā climate to identify currently triggered karmic lessons.",
            "> - **Constructive Remediation**: Conclude with grounded, practical lifestyle guidance to harmonize challenged planets.",
            ""
        ]
        sections.append("\n".join(prompt_lines))

    # =========================================================================
    # 1. Master Graha Diagnostics (D1 Root Chart)
    # =========================================================================
    if include_master_diagnostics:
        diag_lines = [
            "---",
            "",
            "## 1. Master Graha Diagnostics (D1 Root Chart)",
            "The table below synthesizes the complete 9-column Master Diagnostic matrix for the Ascendant and all 9 Grahas:",
            "",
            "| Graha & Role | Longitude & Bhāva | Dignity & Sambandha | Dispositor (Rāśi Lord) | Ṣaḍbala Strength | Dṛṣṭi & Yuti (Aspects) | Nakṣatra & Overlord | Avasthās (State) | Archetype & Vitality |",
            "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |"
        ]

        # 1. Lagna Row
        lg_baladi = calculate_baladi_avastha(lg_sign, lg_deg_val)
        lg_nak_meta = get_nakshatra_metadata(lg_nak_name)
        lg_deity = lg_nak_meta.get("deity", "—")
        lg_ruler = lg_nak_data.get("nakshatra_lord") or lg_nak_meta.get("ruler", "—")

        # Lagna Lord info
        lord_graha = d1_grahas.get(lg_lord, {})
        lord_sign = lord_graha.get("sign", "")
        lord_deg_val = float(lord_graha.get("degree_0_to_30", 15.0))
        lagna_idx = SIGNS_LIST.index(lg_sign) if lg_sign in SIGNS_LIST else 0
        lord_sign_idx = SIGNS_LIST.index(lord_sign) if lord_sign in SIGNS_LIST else 0
        lord_w_house = ((lord_sign_idx - lagna_idx + 12) % 12 + 1) if (lg_sign in SIGNS_LIST and lord_sign in SIGNS_LIST) else 1
        lord_c_house = get_campanus_house_num(lg_lord, lord_w_house, d1_bhavas)
        lord_shift = f" (Chalita H{lord_c_house})" if lord_c_house != lord_w_house else ""

        lord_dig_raw = lord_graha.get("dignity_breakdown", {}).get("final_dignity", lord_graha.get("dignity", "Neutral"))
        clean_lord_dig = clean_dignity_name(lord_dig_raw)
        lord_dig_pct = get_dignity_score(clean_lord_dig, planet=lg_lord, sign=lord_sign, degree=lord_deg_val)
        lord_host = SIGN_LORDS.get(lord_sign, lg_lord)

        sb_lord = shadbala.get(lg_lord, {})
        sb_vir_lg = f"{sb_lord.get('Total_Virupas', 0.0):.1f}v" if "Total_Virupas" in sb_lord else "—"
        sb_pct_lg = f"{int(round(sb_lord.get('Pct_Required_Total', 0.0)))}%" if "Pct_Required_Total" in sb_lord else "—"
        sb_rank_lg = f"#{sb_lord.get('Relative_Rank', '—')}"

        # Occupants in H1
        h1_occupants = [p for p in PLANETS_ORDER if d1_grahas.get(p, {}).get("sign") == lg_sign]
        h1_occ_str = f"Occupants: {', '.join(h1_occupants)}" if h1_occupants else "Clean Horizon (Unoccupied)"

        # Inflowing rays on Cusp 1
        c1_totals = adv_aspects.get("totals", {}).get("cusps", {}).get(1, adv_aspects.get("totals", {}).get("cusps", {}).get("1", {}))
        c1_net = float(c1_totals.get("net", 0.0))
        c1_net_str = f"+{c1_net:.1f}v Śubha" if c1_net > 0 else (f"{c1_net:.1f}v Aśubha" if c1_net < 0 else "0v Neutral")

        # Lagna Vitality
        lagna_eval = pe.get("lagna_evaluation", {})
        lagna_vit = lagna_eval.get("vitality_score", 5.0)
        lagna_tier = lagna_eval.get("vitality_tier", "Capable Vessel")
        lagna_arch = lagna_eval.get("archetype", "The Steady Navigator")

        diag_lines.append(
            f"| **Lagna (Ascendant)** | {lg_sign} {lg_deg_str}<br>House 1 (Tanū Bhāva) | "
            f"Captain: **{lg_lord}** in {lord_sign} ({clean_lord_dig} {lord_dig_pct:.0f}%) | "
            f"Host: **{lord_host}** | "
            f"Captain: {sb_vir_lg} ({sb_pct_lg} • Rank {sb_rank_lg}) | "
            f"Net: {c1_net_str}<br>{h1_occ_str} | "
            f"**{lg_nak_name}** (Pada {lg_nak_pada})<br>Ruler: {lg_ruler} • Deity: {lg_deity} | "
            f"Age: {lg_baladi.get('state', '—')} ({lg_baladi.get('efficiency_pct', 100)}%)<br>Lord in H{lord_w_house}{lord_shift} | "
            f"**{lagna_arch}**<br>★ {lagna_vit:.1f} / 10 ({lagna_tier}) |"
        )

        # 2. Planetary Rows (Sun through Ketu)
        planetary_wars = detect_planetary_wars(d1_grahas, shadbala)

        for p in PLANETS_ORDER:
            if p not in d1_grahas:
                continue
            g = d1_grahas[p]
            is_node = p in ["Rahu", "Ketu"]
            pe_p = pe.get("planets", {}).get(p, {})

            sign = g.get("sign", "-")
            deg_val = float(g.get("degree_0_to_30", 0.0))
            deg_str = format_deg(deg_val)
            baladi = calculate_baladi_avastha(sign, deg_val)

            # Houses: Whole Sign and Campanus
            p_idx = SIGNS_LIST.index(sign) if sign in SIGNS_LIST else 0
            w_house = ((p_idx - lagna_idx + 12) % 12 + 1) if (lg_sign in SIGNS_LIST and sign in SIGNS_LIST) else 1
            c_house = get_campanus_house_num(p, w_house, d1_bhavas)
            c_shift_str = f" → Chalita H{c_house}" if c_house != w_house else ""

            # Roles & Motion
            role_tags = []
            if g.get("is_retrograde"):
                role_tags.append("[R]")
            if g.get("is_combust"):
                role_tags.append("[C]")

            # Chara Karaka
            ck_data = g.get("chara_karaka") or chara_karakas.get(p, {})
            ck_tag = ck_data.get("karaka", "")
            if ck_tag:
                role_tags.append(f"({ck_tag})")

            # Master Lords
            if p == lagna_lord_p:
                role_tags.append("[LL]")
            if p == navamsha_lord_p:
                role_tags.append("[D9L]")
            if p == drekkana_lord_p:
                role_tags.append("[D3L]")

            fn_data = g.get("functional_role") or functional_karakas.get(p, {})
            fn_role = fn_data.get("role", "")
            if fn_role and fn_role != "Neutral":
                role_tags.append(fn_role)

            role_str = " " + " ".join(role_tags) if role_tags else ""

            # Dignity & Sambandha
            d_break = g.get("dignity_breakdown", {})
            sign_lord = d_break.get("sign_lord", SIGN_LORDS.get(sign, "-"))
            raw_dig = d_break.get("final_dignity", g.get("dignity", "Neutral"))
            clean_dig = clean_dignity_name(raw_dig)
            dig_pct = get_dignity_score(clean_dig, planet=p, sign=sign, degree=deg_val)
            shadvarga_pct = float(pe_p.get("step1_shadvarga", {}).get("weighted_dignity_pct", dig_pct))

            nat_rel = d_break.get("natural_relationship", "-")
            tmp_rel = d_break.get("temporary_relationship", "-")
            rel_note = f"Nat: {nat_rel[:3]} • Tmp: {tmp_rel[:3]}" if not is_node else f"via {sign_lord}"

            # Host Dispositor
            host_graha = d1_grahas.get(sign_lord, {})
            host_sign = host_graha.get("sign", "")
            host_deg_val = float(host_graha.get("degree_0_to_30", 15.0))
            host_dig_raw = host_graha.get("dignity_breakdown", {}).get("final_dignity", host_graha.get("dignity", "Neutral"))
            host_dig = get_dignity_score(host_dig_raw, planet=sign_lord, sign=host_sign, degree=host_deg_val)
            host_sb_entry = shadbala.get(sign_lord, {})
            host_sb_pct = float(host_sb_entry.get("Pct_Required_Total", 100.0))

            host_status = "Fortified Host" if host_dig >= 70.0 else ("Strained Host" if host_dig < 40.0 else "Neutral Host")
            if sign_lord == p:
                host_status = "Self-Hosted"

            # Shadbala
            sb_p = shadbala.get(p, {})
            if is_node:
                sb_str = f"Proxy ({sign_lord}): {host_sb_pct:.0f}% req"
            else:
                vir_val = sb_p.get("Total_Virupas", 0.0)
                pct_val = sb_p.get("Pct_Required_Total", 0.0)
                rank_val = sb_p.get("Relative_Rank", "—")
                ishta = sb_p.get("Ishta_Phala_Geometric", sb_p.get("Ishta_Phala", 0.0))
                kashta = sb_p.get("Kashta_Phala_Geometric", sb_p.get("Kashta_Phala", 0.0))
                sb_str = f"{vir_val:.1f}v ({pct_val:.0f}% req • #{rank_val})<br>Ishta: {ishta:.1f} / Kashta: {kashta:.1f}"

            # Aspects & Conjunctions
            conjuncts = [other for other in PLANETS_ORDER if other != p and d1_grahas.get(other, {}).get("sign") == sign]
            conj_str = f"Yuti: {', '.join(conjuncts)}" if conjuncts else "No Yuti"

            asp_rec = adv_aspects.get("planets", {}).get(p, {})
            tot_rec = adv_aspects.get("totals", {}).get("planets", {}).get(p, {})
            net_drishti = float(tot_rec.get("net", 0.0))
            drishti_net_str = f"+{net_drishti:.1f}v Śubha" if net_drishti > 0 else (f"{net_drishti:.1f}v Aśubha" if net_drishti < 0 else "0v Neutral")

            # Inflowing major aspects (> 15 virupas)
            major_asps = []
            for from_p in PLANETS_ORDER:
                if from_p != p and from_p in asp_rec:
                    raw_v = float(asp_rec[from_p].get("raw", 0.0))
                    if raw_v >= 15.0:
                        is_plus = asp_rec[from_p].get("plus", 0.0) > 0
                        sign_char = "+" if is_plus else "-"
                        major_asps.append(f"{from_p} ({sign_char}{raw_v:.0f}v)")
            asp_summary = f"{conj_str}<br>Net: {drishti_net_str}"
            if major_asps:
                asp_summary += f"<br>Gaze: {', '.join(major_asps[:3])}"

            # Planetary War note
            war_info = planetary_wars.get(p, {})
            if war_info.get("is_winner"):
                asp_summary += f"<br>⚔ War Winner vs {war_info.get('opponent')}"
            elif war_info.get("is_loser"):
                asp_summary += f"<br>⚔ War Defeated by {war_info.get('opponent')}"

            # Nakshatra
            nak_p = naks.get(p, {})
            nak_name = nak_p.get("nakshatra", "-")
            nak_pada = nak_p.get("pada", "-")
            nak_meta = get_nakshatra_metadata(nak_name)
            nak_ruler = nak_p.get("nakshatra_lord") or nak_meta.get("ruler", "—")
            nak_deity = nak_meta.get("deity", "—")

            # Avasthas
            bal_state = baladi.get("state", "—")
            bal_eff = baladi.get("efficiency_pct", 100)
            av_dict = g.get("avasthas", {})
            jagrat_state = av_dict.get("jagrat", {}).get("state", "—") if isinstance(av_dict.get("jagrat"), dict) else str(av_dict.get("jagrat", "—"))
            deeptadi_state = av_dict.get("deeptadi", {}).get("state", "—") if isinstance(av_dict.get("deeptadi"), dict) else str(av_dict.get("deeptadi", "—"))

            lajjitadi_list = av_dict.get("lajjitadi", [])
            lajj_items = []
            for item in lajjitadi_list:
                if isinstance(item, dict):
                    lajj_items.append(item.get("state", ""))
                elif isinstance(item, str):
                    lajj_items.append(item)
            lajj_str = ", ".join([x for x in lajj_items if x]) if lajj_items else "Placid / Neutral"
            avastha_summary = f"Age: {bal_state} ({bal_eff}%)<br>Alertness: {jagrat_state}<br>Mood: {deeptadi_state}<br>Social: {lajj_str}"

            # Archetype & Vitality Score
            vit_res = calculate_graha_vitality(
                planet=p,
                sign=sign,
                degree_in_sign=deg_val,
                dignity_name=clean_dig,
                dignity_pct=dig_pct,
                host_planet=sign_lord,
                host_dignity_pct=host_dig,
                host_shadbala_pct=host_sb_pct,
                planet_shadbala_pct=float(sb_p.get("Pct_Required_Total", 100.0)),
                net_drishti_virupas=net_drishti,
                conjunctions=conjuncts,
                lajjitadi_states=lajjitadi_list,
                is_retrograde=bool(g.get("is_retrograde")),
                is_combust=bool(g.get("is_combust")),
                is_node=is_node,
                lagna_sign=lg_sign,
                lagna_lord=lg_lord,
                is_war_winner=war_info.get("is_winner", False),
                is_war_loser=war_info.get("is_loser", False),
                war_opponent=war_info.get("opponent"),
                functional_role=g.get("functional_role")
            )
            archetype_name = vit_res.get("archetype", "Dutiful Realist")
            vit_score = vit_res.get("vitality_score", 5.0)
            vit_tier = vit_res.get("vitality_tier", "Capable")
            rescue_badge = vit_res.get("rescue_badge", "")
            rescue_note = f"<br>({rescue_badge})" if rescue_badge else ""

            diag_lines.append(
                f"| **{p}**{role_str} | {sign} {deg_str}<br>House {w_house}{c_shift_str} | "
                f"**{clean_dig}** ({dig_pct:.0f}% / Shadvarga: {shadvarga_pct:.1f}%)<br>{rel_note} | "
                f"**{sign_lord}** in {host_sign} ({host_dig:.0f}%)<br>{host_status} | "
                f"{sb_str} | "
                f"{asp_summary} | "
                f"**{nak_name}** (Pada {nak_pada})<br>Lord: {nak_ruler} • Deity: {nak_deity} | "
                f"{avastha_summary} | "
                f"**{archetype_name}**<br>★ {vit_score:.1f} / 10 ({vit_tier}){rescue_note} |"
            )

        diag_lines.append("")
        sections.append("\n".join(diag_lines))

    # =========================================================================
    # 2. Core Roles & Soul Archetypes (Chara Karakas & Master Lords)
    # =========================================================================
    if include_archetypes and chara_karakas:
        ck_names = {
            "AK": "Ātmakāraka (Soul Purpose & Core Evolution)",
            "AmK": "Amātyakāraka (Career, Intellect & Executive Capacity)",
            "BK": "Bhrātṛkāraka (Guru, Mentors, Dharma & Siblings)",
            "MK": "Mātṛkāraka (Mother, Emotional Sustenance & Mind)",
            "PK": "Pitṛkāraka (Father, Intelligence, Children & Lineage)",
            "GK": "Jñātikāraka (Obstacles, Competition, Debts & Resilience)",
            "DK": "Dārākāraka (Spouse, Long-term Partnerships & Contracts)"
        }
        arch_lines = [
            "---",
            "",
            "## 2. Core Archetypes & Functional Authority",
            "### Soul Signifiers (Chara Kāraka System - BPHS Chapter 32)",
            "The Chara Karakas reveal the evolutionary priorities of the soul ranked by descending degree in sign:"
        ]
        for tag, title in ck_names.items():
            for pl, c_info in chara_karakas.items():
                if isinstance(c_info, dict) and c_info.get("karaka") == tag:
                    g_info = d1_grahas.get(pl, {})
                    p_sign = g_info.get("sign", "")
                    p_deg = format_deg(float(g_info.get("degree_0_to_30", 0.0)))
                    arch_lines.append(f"- **{tag} • {title}**: **{pl}** at {p_sign} {p_deg}")

        arch_lines.append("")
        arch_lines.append("### Master Pillar Lords (Phaladīpikā 3.11)")
        arch_lines.append(f"- **Lagneśa (D1 Ascendant Lord)**: **{lagna_lord_p}** (Physical constitution, health, stamina, overall vehicle).")
        arch_lines.append(f"- **Navāṁśeśa (D9 Dharma Lord)**: **{navamsha_lord_p}** (Internal happiness, soul destiny, marital fortune).")
        arch_lines.append(f"- **Drekkāṇeśa (D3 Courage Lord)**: **{drekkana_lord_p}** (Decisive drive, physical courage, brothers, execution).")
        arch_lines.append("")
        sections.append("\n".join(arch_lines))

    # =========================================================================
    # 3. Key Divisional Charts (D9 Navamsha & D10 Dashamsha)
    # =========================================================================
    if include_vargas:
        varga_lines = [
            "---",
            "",
            "## 3. Key Divisional Charts (Vargas)",
        ]

        # D9 Navamsha
        d9 = vargas.get("D9", {})
        if d9:
            d9_lagna = d9.get("lagna", {})
            d9_lg_sign = d9_lagna.get("sign", "-")
            d9_lg_deg = format_deg(float(d9_lagna.get("degree_0_to_30", 0.0)))
            d9_lg_lord = SIGN_LORDS.get(d9_lg_sign, "-")

            # Karakamsa / Swamsha
            ak_planet = None
            for pl, c_info in chara_karakas.items():
                if isinstance(c_info, dict) and c_info.get("karaka") == "AK":
                    ak_planet = pl
                    break
            karakamsa_sign = d9.get("grahas", {}).get(ak_planet, {}).get("sign", "—") if ak_planet else "—"

            varga_lines.append("### D9 Navāṃśa (Dharma, Soul Blueprint & Partnerships)")
            varga_lines.append(f"- **Navāṃśa Ascendant (Svāṃśa)**: **{d9_lg_sign} {d9_lg_deg}** | Lord: **{d9_lg_lord}**")
            varga_lines.append(f"- **Kārakāṃśa (AK {ak_planet} in D9)**: **{karakamsa_sign}** (The primary signpost of spiritual evolution and soul vocation).")
            varga_lines.append("")
            varga_lines.append("| Graha | D9 Sign & Degree | D9 House | D9 Dignity | Note / Vargottama |")
            varga_lines.append("| :--- | :--- | :--- | :--- | :--- |")

            d9_grahas = d9.get("grahas", {})
            d9_lg_idx = SIGNS_LIST.index(d9_lg_sign) if d9_lg_sign in SIGNS_LIST else 0

            for p in PLANETS_ORDER:
                if p not in d9_grahas:
                    continue
                g9 = d9_grahas[p]
                s9 = g9.get("sign", "-")
                deg9 = format_deg(float(g9.get("degree_0_to_30", 0.0)))
                s9_idx = SIGNS_LIST.index(s9) if s9 in SIGNS_LIST else 0
                h9 = ((s9_idx - d9_lg_idx + 12) % 12 + 1) if (d9_lg_sign in SIGNS_LIST and s9 in SIGNS_LIST) else 1
                dig9 = clean_dignity_name(g9.get("dignity", "Neutral"))
                is_vargottama = (s9 == d1_grahas.get(p, {}).get("sign"))
                v_note = "**Vargottama** (Fortified)" if is_vargottama else "—"
                varga_lines.append(f"| **{p}** | {s9} {deg9} | House {h9} | {dig9} | {v_note} |")
            varga_lines.append("")

        # D10 Dashamsha
        d10 = vargas.get("D10", {})
        if d10:
            d10_lagna = d10.get("lagna", {})
            d10_lg_sign = d10_lagna.get("sign", "-")
            d10_lg_deg = format_deg(float(d10_lagna.get("degree_0_to_30", 0.0)))
            d10_lg_lord = SIGN_LORDS.get(d10_lg_sign, "-")

            varga_lines.append("### D10 Daśāṃśa (Career, Status & Executive Action)")
            varga_lines.append(f"- **Daśāṃśa Ascendant**: **{d10_lg_sign} {d10_lg_deg}** | Lord: **{d10_lg_lord}**")
            varga_lines.append("")
            varga_lines.append("| Graha | D10 Sign & Degree | D10 House | D10 Dignity |")
            varga_lines.append("| :--- | :--- | :--- | :--- |")

            d10_grahas = d10.get("grahas", {})
            d10_lg_idx = SIGNS_LIST.index(d10_lg_sign) if d10_lg_sign in SIGNS_LIST else 0

            for p in PLANETS_ORDER:
                if p not in d10_grahas:
                    continue
                g10 = d10_grahas[p]
                s10 = g10.get("sign", "-")
                deg10 = format_deg(float(g10.get("degree_0_to_30", 0.0)))
                s10_idx = SIGNS_LIST.index(s10) if s10 in SIGNS_LIST else 0
                h10 = ((s10_idx - d10_lg_idx + 12) % 12 + 1) if (d10_lg_sign in SIGNS_LIST and s10 in SIGNS_LIST) else 1
                dig10 = clean_dignity_name(g10.get("dignity", "Neutral"))
                varga_lines.append(f"| **{p}** | {s10} {deg10} | House {h10} | {dig10} |")
            varga_lines.append("")

        sections.append("\n".join(varga_lines))

    # =========================================================================
    # 4. Campanus 3D Bhava Chalita Cusps
    # =========================================================================
    if include_cusps and d1_cusps:
        cusp_lines = [
            "---",
            "",
            "## 4. Campanus 3D Bhava Chalita Cusps",
            "Campanus houses divide the prime vertical into 30° spatial wedges, reflecting the exact physical horizon of the birth location:",
            "",
            "| Bhāva | Cusp Sign & Degree | Cusp Lord | Occupants (In-House Grahas) | Life Significations |",
            "| :---: | :--- | :--- | :--- | :--- |"
        ]
        for idx, c in enumerate(d1_cusps, 1):
            h_sign = c.get("sign", "-")
            h_deg = format_deg(float(c.get("degree_0_to_30", 0.0)))
            h_lord = SIGN_LORDS.get(h_sign, "-")

            occ_names = []
            if idx - 1 < len(d1_bhavas):
                occ_names = d1_bhavas[idx - 1].get("planets", [])
            occ_str = ", ".join(occ_names) if occ_names else "—"
            sig_str = HOUSE_SIGNIFICATIONS.get(idx, "")

            cusp_lines.append(f"| **House {idx}** | {h_sign} {h_deg} | **{h_lord}** | {occ_str} | {sig_str} |")

        cusp_lines.append("")
        sections.append("\n".join(cusp_lines))

    # =========================================================================
    # 5. Vimśottarī Daśā Timeline (120-Year Cycle)
    # =========================================================================
    if include_dashas:
        vd = chart_data.get("vimshottari_dasha", {})
        mds = vd.get("mahadashas", []) if vd else []
        at_birth = vd.get("at_birth", {}) if vd else {}

        if mds:
            dasha_lines = [
                "---",
                "",
                "## 5. Vimśottarī Daśā Timeline (120-Year Cycle)",
            ]
            start_lord = at_birth.get("mahadasha", "-")
            bal_yrs = at_birth.get("mahadasha_balance_years", 0.0)
            dasha_lines.append(f"- **Balance at Birth**: **{start_lord}** Mahādaśā with **{bal_yrs:.2f} years** remaining.")

            now = datetime.datetime.now()
            active_md = None
            active_ad = None

            for md in mds:
                try:
                    sd = datetime.datetime.strptime(md.get("start", "").split()[0], "%Y-%m-%d")
                    ed = datetime.datetime.strptime(md.get("end", "").split()[0], "%Y-%m-%d")
                    if sd <= now <= ed:
                        active_md = md
                        for ad in md.get("antardashas", []):
                            ad_s = datetime.datetime.strptime((ad.get("start_date") or ad.get("start", "")).split()[0], "%Y-%m-%d")
                            ad_e = datetime.datetime.strptime((ad.get("end_date") or ad.get("end", "")).split()[0], "%Y-%m-%d")
                            if ad_s <= now <= ad_e:
                                active_ad = ad
                                break
                        break
                except Exception:
                    pass

            if active_md:
                md_p = active_md.get("planet", "-")
                ad_p = (active_ad.get("period") or active_ad.get("antardasha_lord", "-")) if active_ad else "-"
                ad_s = (active_ad.get("start_date") or active_ad.get("start", "-")) if active_ad else "-"
                ad_e = (active_ad.get("end_date") or active_ad.get("end", "-")) if active_ad else "-"
                dasha_lines.append(f"- **Current Active Operating Climate**: **{md_p} / {ad_p}** (Active Antardaśā: {ad_s} to {ad_e})")
            dasha_lines.append("")

            dasha_lines.append("### Chronological Mahādaśā Cycles")
            dasha_lines.append("| Planet | Start Date | End Date | Duration | Status |")
            dasha_lines.append("| :--- | :--- | :--- | :--- | :--- |")

            for md in mds:
                p = md.get("planet", "")
                s_str = md.get("start", "")
                e_str = md.get("end", "")
                yrs = md.get("years", "")
                is_active = (active_md and active_md.get("planet") == p)

                status_tag = "**ACTIVE NOW**" if is_active else "Future"
                try:
                    ed = datetime.datetime.strptime(e_str.split()[0], "%Y-%m-%d")
                    if ed < now and not is_active:
                        status_tag = "Completed"
                except Exception:
                    pass

                dasha_lines.append(f"| **{p}** | {s_str} | {e_str} | {yrs} years | {status_tag} |")

            dasha_lines.append("")
            sections.append("\n".join(dasha_lines))

    # =========================================================================
    # 6. Classical Yogas & Breakers (Yoga Bhaṅga)
    # =========================================================================
    if include_yogas:
        yogas_data = chart_data.get("yogas", {})
        y_list = yogas_data.get("yogas", []) if yogas_data else []

        if y_list:
            yoga_lines = [
                "---",
                "",
                "## 6. Classical Yogas & Breakers (Yoga Bhaṅga Audit)",
                "Classical planetary combinations evaluated with rigorous Parashari breaker mechanics:",
                "",
                "| Yoga Name | Status | Participating Grahas | Houses | Manifesting Archetype & Mechanics | Breakers (Bhaṅga) |",
                "| :--- | :--- | :--- | :--- | :--- | :--- |"
            ]

            for y in y_list:
                y_name = y.get("name", "Yoga")
                y_status = y.get("status", "Pure & Eminent")
                pls = ", ".join(y.get("participating_planets", [])) or "—"
                hs = ", ".join([f"H{h}" for h in y.get("participating_houses", []) if h > 0]) or "—"
                arch = y.get("archetype", "") or "—"

                breakers = y.get("breakers", [])
                if breakers:
                    b_notes = []
                    for b in breakers:
                        fac = b.get("factor", "Affliction")
                        pen = b.get("penalty", 0.0)
                        b_notes.append(f"{fac} (-{pen:.0f}%)")
                    b_str = "; ".join(b_notes)
                else:
                    b_str = "None (Pristine)"

                yoga_lines.append(f"| **{y_name}** | {y_status} | {pls} | {hs} | {arch} | {b_str} |")

            yoga_lines.append("")
            sections.append("\n".join(yoga_lines))

    return "\n\n".join(sections)
