"""
Full generator for Astra Nakshatra Display Standalone Preview.
Generates an interactive, beautiful HTML file showcasing:
1. North Indian Chart with Nakshatras (Underneath Degree vs Above Planet)
2. South Indian Chart with Nakshatras (4 placement strategies)
3. Harmonic Bi-Wheel Chart with optimized radial spacing
4. South Indian high-density stress tests (1, 2, 3, and 4 planets per sign)
5. Bi-Wheel geometric radius comparison diagram
6. Mockup of the Astra Settings Modal
7. Complete 27 Nakshatras reference table
"""

import math
import os
import json
from jyotish import generate_jyotish, draw_chart
from jyotish.draw_chart import (
    planet_notations, sign_symbols, signs_list, ASTRO_FONT_STACK,
    get_equidistant_t, get_north_equidistant_t, polar_coords, annular_sector,
    relax_planet_angles
)
from jyotish.relationships.relationships import (
    get_dignity, get_compound_relationship, get_natural_relationship,
    get_temporary_relationship, SIGN_LORDS
)

# 27 Nakshatras mapping
NAKSHATRA_DATA = [
    {"name": "Ashwini", "3": "Ash", "4": "Ashw", "lord": "Ketu", "deity": "Ashwins", "rashi": "Aries", "span": "00°00' - 13°20' Ari"},
    {"name": "Bharani", "3": "Bha", "4": "Bhar", "lord": "Venus", "deity": "Yama", "rashi": "Aries", "span": "13°20' - 26°40' Ari"},
    {"name": "Krittika", "3": "Kri", "4": "Krit", "lord": "Sun", "deity": "Agni", "rashi": "Aries / Taurus", "span": "26°40' Ari - 10°00' Tau"},
    {"name": "Rohini", "3": "Roh", "4": "Rohi", "lord": "Moon", "deity": "Brahma", "rashi": "Taurus", "span": "10°00' - 23°20' Tau"},
    {"name": "Mrigashira", "3": "Mri", "4": "Mrig", "lord": "Mars", "deity": "Soma", "rashi": "Taurus / Gemini", "span": "23°20' Tau - 06°40' Gem"},
    {"name": "Ardra", "3": "Ard", "4": "Ardr", "lord": "Rahu", "deity": "Rudra", "rashi": "Gemini", "span": "06°40' - 20°00' Gem"},
    {"name": "Punarvasu", "3": "Pun", "4": "Puna", "lord": "Jupiter", "deity": "Aditi", "rashi": "Gemini / Cancer", "span": "20°00' Gem - 03°20' Can"},
    {"name": "Pushya", "3": "Pus", "4": "Push", "lord": "Saturn", "deity": "Brihaspati", "rashi": "Cancer", "span": "03°20' - 16°40' Can"},
    {"name": "Ashlesha", "3": "Asl", "4": "Ashl", "lord": "Mercury", "deity": "Sarpas", "rashi": "Cancer", "span": "16°40' - 30°00' Can"},
    {"name": "Magha", "3": "Mag", "4": "Magh", "lord": "Ketu", "deity": "Pitris", "rashi": "Leo", "span": "00°00' - 13°20' Leo"},
    {"name": "Purva Phalguni", "3": "PPh", "4": "PPha", "lord": "Venus", "deity": "Bhaga", "rashi": "Leo", "span": "13°20' - 26°40' Leo"},
    {"name": "Uttara Phalguni", "3": "UPh", "4": "UPha", "lord": "Sun", "deity": "Aryaman", "rashi": "Leo / Virgo", "span": "26°40' Leo - 10°00' Vir"},
    {"name": "Hasta", "3": "Has", "4": "Hast", "lord": "Moon", "deity": "Savitri", "rashi": "Virgo", "span": "10°00' - 23°20' Vir"},
    {"name": "Chitra", "3": "Chi", "4": "Chit", "lord": "Mars", "deity": "Tvashtar", "rashi": "Virgo / Libra", "span": "23°20' Vir - 06°40' Lib"},
    {"name": "Swati", "3": "Swa", "4": "Swat", "lord": "Rahu", "deity": "Vayu", "rashi": "Libra", "span": "06°40' - 20°00' Lib"},
    {"name": "Vishakha", "3": "Vis", "4": "Vish", "lord": "Jupiter", "deity": "Indragni", "rashi": "Libra / Scorpio", "span": "20°00' Lib - 03°20' Sco"},
    {"name": "Anuradha", "3": "Anu", "4": "Anur", "lord": "Saturn", "deity": "Mitra", "rashi": "Scorpio", "span": "03°20' - 16°40' Sco"},
    {"name": "Jyeshtha", "3": "Jye", "4": "Jyes", "lord": "Mercury", "deity": "Indra", "rashi": "Scorpio", "span": "16°40' - 30°00' Sco"},
    {"name": "Mula", "3": "Mul", "4": "Mula", "lord": "Ketu", "deity": "Nirriti", "rashi": "Sagittarius", "span": "00°00' - 13°20' Sag"},
    {"name": "Purva Ashadha", "3": "PAs", "4": "PAsh", "lord": "Venus", "deity": "Apas", "rashi": "Sagittarius", "span": "13°20' - 26°40' Sag"},
    {"name": "Uttara Ashadha", "3": "UAs", "4": "UAsh", "lord": "Sun", "deity": "Vishvadevas", "rashi": "Sagittarius / Capricorn", "span": "26°40' Sag - 10°00' Cap"},
    {"name": "Shravana", "3": "Shr", "4": "Shra", "lord": "Moon", "deity": "Vishnu", "rashi": "Capricorn", "span": "10°00' - 23°20' Cap"},
    {"name": "Dhanishtha", "3": "Dha", "4": "Dhan", "lord": "Mars", "deity": "Vasus", "rashi": "Capricorn / Aquarius", "span": "23°20' Cap - 06°40' Aqu"},
    {"name": "Shatabhisha", "3": "Sha", "4": "Shat", "lord": "Rahu", "deity": "Varuna", "rashi": "Aquarius", "span": "06°40' - 20°00' Aqu"},
    {"name": "Purva Bhadrapada", "3": "PBh", "4": "PBha", "lord": "Jupiter", "deity": "Aja Ekapada", "rashi": "Aquarius / Pisces", "span": "20°00' Aqu - 03°20' Pis"},
    {"name": "Uttara Bhadrapada", "3": "UBh", "4": "UBha", "lord": "Saturn", "deity": "Ahirbudhnya", "rashi": "Pisces", "span": "03°20' - 16°40' Pis"},
    {"name": "Revati", "3": "Rev", "4": "Reva", "lord": "Mercury", "deity": "Pushan", "rashi": "Pisces", "span": "16°40' - 30°00' Pis"},
]

NAKSHATRA_MAP = {d["name"]: d for d in NAKSHATRA_DATA}

def get_nak_abbr(name: str, length: str = "3") -> str:
    if not name:
        return ""
    info = NAKSHATRA_MAP.get(name)
    if info:
        return info.get(length, name[:int(length)])
    return name[:int(length)]


def build_test_items():
    chart = generate_jyotish.generate_kala_chart(
        year=1995, month=5, day=15, hour=14, minute=30, latitude=51.5074, longitude=-0.1278, timezone_offset=1.0
    )
    v_d1 = chart['vargas']['D1']
    v_d9 = chart['vargas']['D9']
    nak_grahas = chart['nakshatras']['grahas']

    def attach_nak(raw_v, raw_nak):
        items = draw_chart.parse_varga_data(raw_v)
        for it in items:
            if it.get("type") == "planet":
                p_name = it["name"]
                if p_name == "Lagna":
                    it["nakshatra"] = raw_v["lagna"].get("nakshatra", "")
                    it["pada"] = raw_v["lagna"].get("pada", 1)
                elif p_name in raw_nak:
                    it["nakshatra"] = raw_nak[p_name].get("nakshatra", "")
                    it["pada"] = raw_nak[p_name].get("pada", 1)
        return items

    items_d1 = attach_nak(v_d1, nak_grahas)
    items_d9 = attach_nak(v_d9, nak_grahas)
    return chart, items_d1, items_d9


def render_north_indian_preview(items, nak_enabled=True, nak_len="3", nak_placement="under_degree", nak_color="#8c7b64"):
    """Renders North Indian SVG with configurable Nakshatra display."""
    svg = '<svg width="100%" height="100%" viewBox="0 0 500 500" class="aspects-hidden chart-svg-north" preserveAspectRatio="xMidYMid meet" xmlns="http://www.w3.org/2000/svg" style="background:transparent;">\n'
    svg += '<rect width="500" height="500" fill="#fffdfa"/>\n'

    ni_paths = [
        "M 250 19 C 224 55, 150 78, 148 148 L 250 250 L 352 148 C 350 78, 276 55, 250 19 Z",
        "M 18 18 L 250 19 C 224 55, 150 78, 148 148 L 18 18 Z",
        "M 18 18 L 148 148 C 78 150, 55 224, 19 250 L 18 18 Z",
        "M 19 250 C 55 224, 78 150, 148 148 L 250 250 L 148 352 C 78 350, 55 276, 19 250 Z",
        "M 19 250 C 55 276, 78 350, 148 352 L 18 482 L 19 250 Z",
        "M 18 482 L 148 352 C 150 422, 224 445, 250 481 L 18 482 Z",
        "M 250 481 C 224 445, 150 422, 148 352 L 250 250 L 352 352 C 350 422, 276 445, 250 481 Z",
        "M 250 481 C 276 445, 350 422, 352 352 L 482 482 L 250 481 Z",
        "M 482 482 L 352 352 C 422 350, 445 276, 481 250 L 482 482 Z",
        "M 481 250 C 445 224, 422 150, 352 148 L 250 250 L 352 352 C 422 350, 445 276, 481 250 Z",
        "M 482 18 L 481 250 C 445 224, 422 150, 352 148 L 482 18 Z",
        "M 482 18 L 352 148 C 350 78, 276 55, 250 19 L 482 18 Z"
    ]

    for h in range(12):
        if h in (0, 3, 6, 9):
            fill_col = "#eedec9"
        elif h in (4, 8):
            fill_col = "#faede0"
        else:
            fill_col = "#f9f5eb"
        svg += f'<path d="{ni_paths[h]}" fill="{fill_col}"/>\n'

    svg += '<rect x="14" y="14" width="472" height="472" fill="none" stroke="#3e2819" stroke-width="2.2"/>\n'
    svg += '<rect x="18" y="18" width="464" height="464" fill="none" stroke="#b45309" stroke-width="0.75" stroke-opacity="0.6"/>\n'
    svg += '<line x1="18" y1="18" x2="148" y2="148" stroke="#3e2819" stroke-width="1.3"/>\n'
    svg += '<line x1="482" y1="18" x2="352" y2="148" stroke="#3e2819" stroke-width="1.3"/>\n'
    svg += '<line x1="18" y1="482" x2="148" y2="352" stroke="#3e2819" stroke-width="1.3"/>\n'
    svg += '<line x1="482" y1="482" x2="352" y2="352" stroke="#3e2819" stroke-width="1.3"/>\n'
    svg += '<line x1="148" y1="148" x2="250" y2="250" stroke="#3e2819" stroke-width="1.3"/>\n'
    svg += '<line x1="352" y1="148" x2="250" y2="250" stroke="#3e2819" stroke-width="1.3"/>\n'
    svg += '<line x1="148" y1="352" x2="250" y2="250" stroke="#3e2819" stroke-width="1.3"/>\n'
    svg += '<line x1="352" y1="352" x2="250" y2="250" stroke="#3e2819" stroke-width="1.3"/>\n'
    svg += '<g stroke="#3e2819" stroke-width="1.5" fill="none" stroke-linecap="round">\n'
    svg += '  <path d="M 250 19 C 224 55, 150 78, 148 148"/><path d="M 250 19 C 276 55, 350 78, 352 148"/>\n'
    svg += '  <path d="M 19 250 C 55 224, 78 150, 148 148"/><path d="M 19 250 C 55 276, 78 350, 148 352"/>\n'
    svg += '  <path d="M 250 481 C 224 445, 150 422, 148 352"/><path d="M 250 481 C 276 445, 350 422, 352 352"/>\n'
    svg += '  <path d="M 481 250 C 445 224, 422 150, 352 148"/><path d="M 481 250 C 445 276, 422 350, 352 352"/>\n'
    svg += '</g>\n'
    svg += '<circle cx="250" cy="250" r="5" fill="#fffdfa" stroke="#b45309" stroke-width="1.2"/>\n'

    anchor_item = next((it for it in items if it.get("name") == "Lagna"), None)
    anchor_sign = anchor_item["sign"] if anchor_item else "Aries"
    anchor_index = signs_list.index(anchor_sign)

    north_house_configs = [
        {"type": "kendra", "orientation": "horizontal", "start": (330, 144), "end": (170, 144), "apex": (250, 226), "cusp": (250, 202)},
        {"type": "triangle", "orientation": "horizontal", "start": (215, 44),  "end": (65, 44),   "apex": (140, 120), "cusp": (140, 95)},
        {"type": "triangle", "orientation": "vertical",   "start": (44, 65),   "end": (44, 215),  "apex": (126, 140), "cusp": (100, 140)},
        {"type": "kendra", "orientation": "vertical",   "start": (144, 170), "end": (144, 330), "apex": (226, 250), "cusp": (202, 250)},
        {"type": "triangle", "orientation": "vertical",   "start": (44, 285),  "end": (44, 435),  "apex": (126, 360), "cusp": (100, 360)},
        {"type": "triangle", "orientation": "horizontal", "start": (65, 456),  "end": (215, 456), "apex": (140, 380), "cusp": (140, 405)},
        {"type": "kendra", "orientation": "horizontal", "start": (170, 356), "end": (330, 356), "apex": (250, 274), "cusp": (250, 298)},
        {"type": "triangle", "orientation": "horizontal", "start": (285, 456), "end": (435, 456), "apex": (360, 380), "cusp": (360, 405)},
        {"type": "triangle", "orientation": "vertical",   "start": (456, 435), "end": (456, 285), "apex": (374, 360), "cusp": (400, 360)},
        {"type": "kendra", "orientation": "vertical",   "start": (356, 330), "end": (356, 170), "apex": (274, 250), "cusp": (298, 250)},
        {"type": "triangle", "orientation": "vertical",   "start": (456, 215), "end": (456, 65),  "apex": (374, 140), "cusp": (400, 140)},
        {"type": "triangle", "orientation": "horizontal", "start": (435, 44),  "end": (285, 44),  "apex": (360, 120), "cusp": (360, 95)},
    ]

    items_by_house = [[] for _ in range(12)]
    for item in items:
        s_idx = signs_list.index(item["sign"])
        h_idx = (s_idx - anchor_index + 12) % 12
        if item.get("type") == "cusp":
            items_by_house[h_idx].append(item)
        else:
            items_by_house[h_idx].append({
                "type": "planet",
                "name": item["name"],
                "sign": item["sign"],
                "deg": f"{item['degree']}°{item['minute']:02d}'",
                "is_retrograde": item.get("is_retrograde", False),
                "nakshatra": item.get("nakshatra", "")
            })

    for h in range(12):
        s_idx = (anchor_index + h) % 12
        sign = signs_list[s_idx]
        s_sym, s_col, _ = sign_symbols[sign]
        cfg = north_house_configs[h]
        is_kendra = cfg.get("type") == "kendra"
        sign_font_sz = "10.5" if is_kendra else "8.5"

        sx, sy = cfg["apex"]
        svg += f'<text x="{sx}" y="{sy}" font-size="{sign_font_sz}" font-family="{ASTRO_FONT_STACK}" fill="{s_col}" opacity="0.85" font-weight="bold" text-anchor="middle" dominant-baseline="central">{s_sym}</text>\n'

        house_items = items_by_house[h]
        planets = [it for it in house_items if it["type"] == "planet"]
        cusps = [it for it in house_items if it["type"] == "cusp"]

        planets_with_deg = []
        for p in planets:
            p_deg_val = 0.0
            for orig_it in items:
                if orig_it.get("type") != "cusp" and orig_it.get("name") == p["name"] and orig_it.get("sign") == p["sign"]:
                    p_deg_val = orig_it.get("degree", 0) + orig_it.get("minute", 0) / 60.0
                    break
            planets_with_deg.append((p_deg_val, p))
        planets_with_deg.sort(key=lambda item: item[0])

        p_start_x, p_start_y = cfg["start"]
        p_end_x, p_end_y = cfg["end"]
        orientation = cfg["orientation"]
        t_values = get_north_equidistant_t(len(planets_with_deg))

        for idx, (p_deg_val, p) in enumerate(planets_with_deg):
            t = t_values[idx]
            px = p_start_x + (p_end_x - p_start_x) * t
            py = p_start_y + (p_end_y - p_start_y) * t

            if len(planets_with_deg) > 4:
                shift = -9 if (idx % 2 == 0) else 9
                if orientation == "horizontal":
                    py += shift
                else:
                    px += shift

            info = planet_notations.get(p["name"], {"symbol": p["name"][:2], "color": "#000"})
            label = info.get("symbol", p["name"][:2])
            is_retro = p.get("is_retrograde", False)
            retro_badge = " R" if is_retro else ""
            nak_abbr = get_nak_abbr(p.get("nakshatra", ""), nak_len)

            svg += f'<g class="interactive planet-group" data-id="{p["name"]}">\n'

            if not nak_enabled:
                # Default Original Rendering
                svg += f'<text x="{px}" y="{py - 2}" text-anchor="middle" dominant-baseline="central" font-family="{ASTRO_FONT_STACK}" font-size="13" font-weight="bold" fill="{info["color"]}">{label}</text>\n'
                svg += f'<text x="{px}" y="{py + 11}" text-anchor="middle" dominant-baseline="central" font-family="sans-serif" font-size="9" fill="#5C4433"><tspan>{p["deg"]}</tspan>{f"""<tspan font-size="8" font-weight="bold" fill="#C0392B"> R</tspan>""" if is_retro else ""}</text>\n'
            elif nak_placement == "under_degree":
                # Option 1: Nakshatra Underneath Degree (User Preferred)
                # Planet glyph at EXACT original (py - 2), Degree centered at EXACT original (py + 11)
                svg += f'<text x="{px}" y="{py - 2}" text-anchor="middle" dominant-baseline="central" font-family="{ASTRO_FONT_STACK}" font-size="13" font-weight="bold" fill="{info["color"]}">{label}</text>\n'
                svg += f'<text x="{px}" y="{py + 11}" text-anchor="middle" dominant-baseline="central" font-family="sans-serif" font-size="9" fill="#5C4433"><tspan>{p["deg"]}</tspan>{f"""<tspan font-size="8" font-weight="bold" fill="#C0392B"> R</tspan>""" if is_retro else ""}</text>\n'
                svg += f'<text x="{px}" y="{py + 19.5}" text-anchor="middle" dominant-baseline="central" font-family="sans-serif" font-size="5.8" font-weight="600" fill="{nak_color}" letter-spacing="0.2px">{nak_abbr}</text>\n'
            else:
                # Option 2: Nakshatra Above Planet
                # Nakshatra at py-11, Glyph at py-1.5, Degree at py+9.5
                svg += f'<text x="{px}" y="{py - 11}" text-anchor="middle" dominant-baseline="central" font-family="sans-serif" font-size="5.8" font-weight="600" fill="{nak_color}" letter-spacing="0.2px">{nak_abbr}</text>\n'
                svg += f'<text x="{px}" y="{py - 1.5}" text-anchor="middle" dominant-baseline="central" font-family="{ASTRO_FONT_STACK}" font-size="12.5" font-weight="bold" fill="{info["color"]}">{label}</text>\n'
                svg += f'<text x="{px}" y="{py + 9.5}" text-anchor="middle" dominant-baseline="central" font-family="sans-serif" font-size="8.5" fill="#5C4433"><tspan>{p["deg"]}</tspan>{f"""<tspan font-size="7.5" font-weight="bold" fill="#C0392B"> R</tspan>""" if is_retro else ""}</text>\n'

            svg += '</g>\n'

        if cusps:
            base_cx, base_cy = cfg["cusp"]
            num_c = len(cusps)
            spacing = 13 if is_kendra else 11
            for c_idx, c in enumerate(cusps):
                c_num = c["text"]
                if num_c == 1:
                    c_x, c_y = base_cx, base_cy
                else:
                    if orientation == "horizontal":
                        c_x = base_cx - ((num_c - 1) * spacing) / 2 + (c_idx * spacing)
                        c_y = base_cy
                    else:
                        c_x = base_cx
                        c_y = base_cy - ((num_c - 1) * spacing) / 2 + (c_idx * spacing)
                svg += f'<text x="{c_x}" y="{c_y}" font-family="sans-serif" font-size="9" font-weight="bold" fill="#7D3C98" text-anchor="middle" dominant-baseline="central">{c_num}</text>\n'

    svg += '</svg>\n'
    return svg


def render_south_indian_preview(items, nak_enabled=True, nak_len="3", nak_placement="above_planet", nak_color="#8c7b64"):
    """Renders South Indian SVG with configurable Nakshatra display."""
    cell_coords = {
        "Pisces": (0, 0), "Aries": (100, 0), "Taurus": (200, 0), "Gemini": (300, 0),
        "Aquarius": (0, 100), "Cancer": (300, 100),
        "Capricorn": (0, 200), "Leo": (300, 200),
        "Sagittarius": (0, 300), "Scorpio": (100, 300), "Libra": (200, 300), "Virgo": (300, 300)
    }

    anchor_item = next((it for it in items if it.get("name") == "Lagna"), None)
    anchor_sign = anchor_item["sign"] if anchor_item else "Aries"
    anchor_index = signs_list.index(anchor_sign)

    items_by_sign = {s: [] for s in signs_list}
    for item in items:
        if item.get("type") == "cusp":
            items_by_sign[item["sign"]].append(item)
        else:
            items_by_sign[item["sign"]].append({
                "type": "planet",
                "name": item["name"],
                "sign": item["sign"],
                "deg": f"{item['degree']}°{item['minute']:02d}'",
                "is_retrograde": item.get("is_retrograde", False),
                "nakshatra": item.get("nakshatra", "")
            })

    svg = '<svg width="100%" height="100%" viewBox="-10 -10 420 420" class="aspects-hidden chart-svg-south" preserveAspectRatio="xMidYMid meet" xmlns="http://www.w3.org/2000/svg" style="background:transparent;">\n'

    for sign, (cx, cy) in cell_coords.items():
        h_num = (signs_list.index(sign) - anchor_index + 12) % 12 + 1
        if h_num in (1, 4, 7, 10):
            fill_col = "#eedec9"
        elif h_num in (5, 9):
            fill_col = "#faede0"
        else:
            fill_col = "#f9f5eb"
        svg += f'<rect x="{cx}" y="{cy}" width="100" height="100" fill="{fill_col}"/>\n'

    svg += '<rect x="100" y="100" width="200" height="200" fill="#fffdfa"/>\n'
    svg += '<rect x="0" y="0" width="400" height="400" fill="none" stroke="#5C4433" stroke-width="2"/>\n'
    svg += '<rect x="100" y="100" width="200" height="200" fill="none" stroke="#5C4433" stroke-width="2"/>\n'
    for p_line in [(100,0,100,100), (100,300,100,400), (200,0,200,100), (200,300,200,400),
                   (300,0,300,100), (300,300,300,400), (0,100,100,100), (300,100,400,100),
                   (0,200,100,200), (300,200,400,200), (0,300,100,300), (300,300,400,300)]:
        svg += f'<line x1="{p_line[0]}" y1="{p_line[1]}" x2="{p_line[2]}" y2="{p_line[3]}" stroke="#5C4433" stroke-width="2"/>\n'

    # Center text
    svg += '<text x="200" y="195" font-family="Cinzel, serif" font-size="14" font-weight="bold" fill="#4a3325" text-anchor="middle">D1 Rasi Chart</text>\n'
    svg += '<text x="200" y="215" font-family="sans-serif" font-size="10" fill="#7a5535" text-anchor="middle">Tropical South Indian</text>\n'

    south_triplets = {
        "Aries":       {"start": (16, 16), "end": (84, 84), "cusp": (13, 87), "sign": (87, 13)},
        "Taurus":      {"start": (16, 16), "end": (84, 84), "cusp": (13, 87), "sign": (87, 13)},
        "Gemini":      {"start": (16, 16), "end": (84, 84), "cusp": (13, 87), "sign": (87, 13)},
        "Cancer":      {"start": (84, 16), "end": (16, 84), "cusp": (13, 13), "sign": (87, 87)},
        "Leo":         {"start": (84, 16), "end": (16, 84), "cusp": (13, 13), "sign": (87, 87)},
        "Virgo":       {"start": (84, 16), "end": (16, 84), "cusp": (13, 13), "sign": (87, 87)},
        "Libra":       {"start": (84, 84), "end": (16, 16), "cusp": (87, 13), "sign": (13, 87)},
        "Scorpio":     {"start": (84, 84), "end": (16, 16), "cusp": (87, 13), "sign": (13, 87)},
        "Sagittarius": {"start": (84, 84), "end": (16, 16), "cusp": (87, 13), "sign": (13, 87)},
        "Capricorn":   {"start": (16, 84), "end": (84, 16), "cusp": (87, 87), "sign": (13, 13)},
        "Aquarius":    {"start": (16, 84), "end": (84, 16), "cusp": (87, 87), "sign": (13, 13)},
        "Pisces":      {"start": (16, 84), "end": (84, 16), "cusp": (87, 87), "sign": (13, 13)},
    }

    for sign, (x, y) in cell_coords.items():
        cell_items = items_by_sign[sign]
        planets = [it for it in cell_items if it["type"] == "planet"]
        cusps = [it for it in cell_items if it["type"] == "cusp"]

        cfg = south_triplets[sign]
        c_dx, c_dy = cfg["cusp"]
        s_dx, s_dy = cfg["sign"]

        s_sym, s_col, _ = sign_symbols[sign]
        svg += f'<text x="{x + s_dx}" y="{y + s_dy}" font-size="10.5" font-family="{ASTRO_FONT_STACK}" font-weight="bold" fill="{s_col}" opacity="0.8" text-anchor="middle" dominant-baseline="central">{s_sym}</text>\n'

        if cusps:
            num_c = len(cusps)
            for c_idx, c in enumerate(cusps):
                c_num = c["text"]
                spread_offset = (c_idx * 13) if c_dx < 50 else -((num_c - 1 - c_idx) * 13)
                cx_pos = x + c_dx + (spread_offset if num_c > 1 else 0)
                cy_pos = y + c_dy
                svg += f'<text x="{cx_pos}" y="{cy_pos}" font-family="sans-serif" font-size="10" font-weight="bold" fill="#7D3C98" text-anchor="middle" dominant-baseline="central">{c_num}</text>\n'

        planets_with_deg = []
        for p in planets:
            p_deg_val = 0.0
            for orig_it in items:
                if orig_it.get("type") != "cusp" and orig_it.get("name") == p["name"] and orig_it.get("sign") == sign:
                    p_deg_val = orig_it.get("degree", 0) + orig_it.get("minute", 0) / 60.0
                    break
            planets_with_deg.append((p_deg_val, p))
        planets_with_deg.sort(key=lambda item: item[0])

        p_start_x, p_start_y = cfg["start"]
        p_end_x, p_end_y = cfg["end"]
        t_values = get_equidistant_t(len(planets_with_deg))

        for idx, (p_deg_val, p) in enumerate(planets_with_deg):
            t = t_values[idx]
            px = x + p_start_x + (p_end_x - p_start_x) * t
            py = y + p_start_y + (p_end_y - p_start_y) * t

            info = planet_notations.get(p["name"], {"symbol": p["name"][:2], "color": "#000"})
            label = info.get("symbol", p["name"][:2])
            is_retro = p.get("is_retrograde", False)
            nak_abbr = get_nak_abbr(p.get("nakshatra", ""), nak_len)

            svg += f'<g class="interactive planet-group" data-id="{p["name"]}">\n'

            if not nak_enabled:
                # Original
                svg += f'<text x="{px}" y="{py - 2}" font-family="{ASTRO_FONT_STACK}" font-size="13" font-weight="bold" fill="{info["color"]}" text-anchor="middle" dominant-baseline="central">{label}</text>\n'
                svg += f'<text x="{px}" y="{py + 11}" font-family="sans-serif" font-size="9" fill="#5C4433" text-anchor="middle" dominant-baseline="central"><tspan>{p["deg"]}</tspan>{f"""<tspan font-size="8" font-weight="bold" fill="#C0392B"> R</tspan>""" if is_retro else ""}</text>\n'
            elif nak_placement == "above_planet":
                # Option A: Above Planet Symbol
                # Nakshatra at py-10.5, Glyph at py-1.5, Degree at py+9
                svg += f'<text x="{px}" y="{py - 10.5}" font-family="sans-serif" font-size="5.5" font-weight="600" fill="{nak_color}" text-anchor="middle" dominant-baseline="central" letter-spacing="0.2px">{nak_abbr}</text>\n'
                svg += f'<text x="{px}" y="{py - 1.5}" font-family="{ASTRO_FONT_STACK}" font-size="12.5" font-weight="bold" fill="{info["color"]}" text-anchor="middle" dominant-baseline="central">{label}</text>\n'
                svg += f'<text x="{px}" y="{py + 9}" font-family="sans-serif" font-size="8.2" fill="#5C4433" text-anchor="middle" dominant-baseline="central"><tspan>{p["deg"]}</tspan>{f"""<tspan font-size="7.5" font-weight="bold" fill="#C0392B"> R</tspan>""" if is_retro else ""}</text>\n'
            elif nak_placement == "inline_degree":
                # Option B: Adaptive Inline on same horizontal baseline (y = py + 11)
                # DEGREE REMAINS DEAD-CENTERED UNDER PLANET AT (px, py + 11) EXACTLY AS BEFORE!
                rel_px = px - x
                svg += f'<text x="{px}" y="{py - 2}" font-family="{ASTRO_FONT_STACK}" font-size="13" font-weight="bold" fill="{info["color"]}" text-anchor="middle" dominant-baseline="central">{label}</text>\n'
                svg += f'<text x="{px}" y="{py + 11}" font-family="sans-serif" font-size="9" fill="#5C4433" text-anchor="middle" dominant-baseline="central"><tspan>{p["deg"]}</tspan>{f"""<tspan font-size="8" font-weight="bold" fill="#C0392B"> R</tspan>""" if is_retro else ""}</text>\n'
                if rel_px > 55:
                    # Accompany on LEFT side (anchored end at px - 16)
                    svg += f'<text x="{px - 16:.1f}" y="{py + 11}" font-family="sans-serif" font-size="5.8" font-weight="600" fill="{nak_color}" text-anchor="end" dominant-baseline="central" letter-spacing="0.2px">{nak_abbr}</text>\n'
                else:
                    # Accompany on RIGHT side (anchored start at px + offset)
                    offset_r = 21 if is_retro else 16
                    svg += f'<text x="{px + offset_r:.1f}" y="{py + 11}" font-family="sans-serif" font-size="5.8" font-weight="600" fill="{nak_color}" text-anchor="start" dominant-baseline="central" letter-spacing="0.2px">{nak_abbr}</text>\n'
            elif nak_placement == "under_degree_compact":
                # Option C: Compact Stack Underneath Degree
                # Glyph at py-3.5, Degree at py+5.5, Nakshatra at py+13.5
                svg += f'<text x="{px}" y="{py - 3.5}" font-family="{ASTRO_FONT_STACK}" font-size="11.5" font-weight="bold" fill="{info["color"]}" text-anchor="middle" dominant-baseline="central">{label}</text>\n'
                svg += f'<text x="{px}" y="{py + 5.5}" font-family="sans-serif" font-size="8.0" fill="#5C4433" text-anchor="middle" dominant-baseline="central"><tspan>{p["deg"]}</tspan>{f"""<tspan font-size="7.0" font-weight="bold" fill="#C0392B"> R</tspan>""" if is_retro else ""}</text>\n'
                svg += f'<text x="{px}" y="{py + 13.5}" font-family="sans-serif" font-size="5.2" font-weight="600" fill="{nak_color}" text-anchor="middle" dominant-baseline="central" letter-spacing="0.2px">{nak_abbr}</text>\n'
            elif nak_placement == "superscript":
                # Option D: Superscript Badge Top-Right
                svg += f'<text x="{px}" y="{py - 1}" font-family="{ASTRO_FONT_STACK}" font-size="13" font-weight="bold" fill="{info["color"]}" text-anchor="middle" dominant-baseline="central">{label}</text>\n'
                svg += f'<text x="{px + 8.5}" y="{py - 7}" font-family="sans-serif" font-size="5.2" font-weight="600" fill="{nak_color}" text-anchor="start" dominant-baseline="central">{nak_abbr}</text>\n'
                svg += f'<text x="{px}" y="{py + 10}" font-family="sans-serif" font-size="8.5" fill="#5C4433" text-anchor="middle" dominant-baseline="central"><tspan>{p["deg"]}</tspan>{f"""<tspan font-size="7.5" font-weight="bold" fill="#C0392B"> R</tspan>""" if is_retro else ""}</text>\n'

            svg += '</g>\n'

    svg += '</svg>\n'
    return svg


def render_biwheel_preview(inner_items, outer_items, nak_enabled=True, nak_len="3", biwheel_mode="compact_stack", nak_color="#8c7b64"):
    """
    Renders Harmonic Bi-Wheel SVG with Nakshatra integration and adjusted inner wheel radii.
    """
    from jyotish.generate_jyotish import calculate_varga_longitude

    svg = '<svg width="100%" height="100%" viewBox="-210 -210 420 420" class="aspects-hidden chart-svg-biwheel" preserveAspectRatio="xMidYMid meet" xmlns="http://www.w3.org/2000/svg" style="background:transparent; font-family: sans-serif;">\n'

    r_chart_outer = 206
    r_divider_outer = 164
    r_divider_inner = 138
    r_bhava_circle = 44
    r_aspect_inner = 28

    svg += f'<circle cx="0" cy="0" r="{r_chart_outer}" fill="#faf7f2" fill-opacity="0.25" stroke="#5C4433" stroke-width="1.0"/>\n'
    svg += f'<circle cx="0" cy="0" r="{r_divider_outer}" fill="#edece6" fill-opacity="0.65" stroke="#8c7b64" stroke-width="1.2"/>\n'
    svg += f'<circle cx="0" cy="0" r="{r_divider_inner}" fill="#ffffff" fill-opacity="0.95" stroke="#8c7b64" stroke-width="1.2"/>\n'

    anchor_item = next((it for it in inner_items if it.get("name") == "Lagna"), None)
    if anchor_item:
        anchor_s_idx = signs_list.index(anchor_item["sign"])
        anchor_lon = anchor_s_idx * 30 + anchor_item["degree"] + anchor_item["minute"] / 60.0
    else:
        anchor_s_idx = 0
        anchor_lon = 0

    def lon_to_angle(lon):
        return 180.0 + anchor_lon - lon

    # Tropical Rasis & Division ring
    harmonic_n = 9
    for i in range(12):
        sign_start_lon = i * 30.0
        angle_start = lon_to_angle(sign_start_lon)
        angle_end = lon_to_angle(sign_start_lon + 30.0)
        angle_mid = lon_to_angle(sign_start_lon + 15.0)
        sign_name = signs_list[i]
        s_sym, s_col, _ = sign_symbols[sign_name]
        bhava_num = (i - anchor_s_idx + 12) % 12 + 1

        if bhava_num in (1, 4, 7, 10):
            fill_col = "#eedec9"
        elif bhava_num in (5, 9):
            fill_col = "#faede0"
        else:
            fill_col = "#f9f5eb"

        sec_d = annular_sector(r_aspect_inner, r_divider_inner, angle_start, angle_end)
        svg += f'<path d="{sec_d}" fill="{fill_col}"/>\n'

        x_in1, y_in1 = polar_coords(r_aspect_inner, angle_start)
        x_in2, y_in2 = polar_coords(r_divider_inner, angle_start)
        svg += f'<line x1="{x_in1:.1f}" y1="{y_in1:.1f}" x2="{x_in2:.1f}" y2="{y_in2:.1f}" stroke="#d5c8b2" stroke-width="0.8" stroke-dasharray="2,3"/>\n'

        x_out1, y_out1 = polar_coords(r_divider_outer, angle_start)
        x_out2, y_out2 = polar_coords(r_chart_outer, angle_start)
        svg += f'<line x1="{x_out1:.1f}" y1="{y_out1:.1f}" x2="{x_out2:.1f}" y2="{y_out2:.1f}" stroke="#d5c8b2" stroke-width="0.8" stroke-dasharray="2,3"/>\n'

        lx_sign, ly_sign = polar_coords(151, angle_mid)
        svg += f'<text x="{lx_sign:.1f}" y="{ly_sign:.1f}" font-size="14" font-family="{ASTRO_FONT_STACK}" stroke="#ffffff" stroke-width="2.5" paint-order="stroke fill" fill="{s_col}" text-anchor="middle" dominant-baseline="central">{s_sym}</text>\n'

        bx, by = polar_coords((r_aspect_inner + r_bhava_circle) / 2, angle_mid)
        svg += f'<text x="{bx:.1f}" y="{by:.1f}" font-size="8.5" font-weight="600" stroke="#FAF7F0" stroke-width="2.0" paint-order="stroke fill" fill="#2980B9" text-anchor="middle" dominant-baseline="central">{bhava_num}</text>\n'

        sx1, sy1 = polar_coords(r_divider_inner, angle_start)
        sx2, sy2 = polar_coords(r_divider_outer, angle_start)
        svg += f'<line x1="{sx1}" y1="{sy1}" x2="{sx2}" y2="{sy2}" stroke="#5C4433" stroke-width="1.3"/>\n'

        for k in range(harmonic_n):
            div_start_lon = sign_start_lon + k * (30.0 / harmonic_n)
            div_mid_lon = div_start_lon + 15.0 / harmonic_n
            angle_div_start = lon_to_angle(div_start_lon)
            angle_div_mid = lon_to_angle(div_mid_lon)
            if k > 0:
                dx1, dy1 = polar_coords(r_divider_inner, angle_div_start)
                dx2, dy2 = polar_coords(r_divider_outer, angle_div_start)
                svg += f'<line x1="{dx1}" y1="{dy1}" x2="{dx2}" y2="{dy2}" stroke="#b8af9f" stroke-width="0.6" stroke-dasharray="2,2"/>\n'

            div_v_lon = calculate_varga_longitude(div_mid_lon, "D9")
            sub_s_idx = int(div_v_lon // 30) % 12
            sub_sign_name = signs_list[sub_s_idx]
            sub_sym, sub_col, _ = sign_symbols[sub_sign_name]
            smx, smy = polar_coords(r_divider_outer - 4.5, angle_div_mid)
            rot_sub = angle_div_mid if (angle_div_mid % 360) > 90 and (angle_div_mid % 360) < 270 else angle_div_mid + 180
            svg += f'<text x="{smx}" y="{smy}" font-size="5.5" font-family="{ASTRO_FONT_STACK}" fill="{sub_col}" opacity="0.8" text-anchor="middle" dominant-baseline="central" transform="rotate({rot_sub} {smx} {smy})">{sub_sym}</text>\n'

    svg += f'<circle cx="0" cy="0" r="{r_bhava_circle}" fill="none" stroke="#27AE60" stroke-width="0.6" stroke-dasharray="3,2"/>\n'
    svg += f'<circle cx="0" cy="0" r="{r_aspect_inner}" fill="#faf7f0" fill-opacity="0.95" stroke="#5C4433" stroke-width="0.8"/>\n'
    svg += '<text x="0" y="-4.5" font-size="7.5" font-weight="bold" fill="#4a3325" text-anchor="middle">D1 · D9</text>\n'
    svg += '<text x="0" y="6" font-size="6.0" font-weight="600" fill="#8c7b64" text-anchor="middle">Harmonic</text>\n'

    # Ascendant arrow
    ax1, ay1 = polar_coords(r_aspect_inner, 180)
    ax2, ay2 = polar_coords(r_divider_inner, 180)
    svg += f'<line x1="{ax1}" y1="{ay1}" x2="{ax2}" y2="{ay2}" stroke="#C0392B" stroke-width="1.6" />\n'

    # Process planets
    inner_planets = []
    inner_planets_dict = {}
    for item in inner_items:
        if item.get("type") == "planet":
            p_name = item["name"]
            s_idx = signs_list.index(item["sign"])
            pl_lon = s_idx * 30 + item["degree"] + item["minute"] / 60.0
            p_data = {
                "item": item, "lon": pl_lon, "draw_angle": lon_to_angle(pl_lon),
                "true_angle": lon_to_angle(pl_lon), "is_lagna": (p_name == "Lagna"),
                "sign_idx": s_idx, "sign": item["sign"], "varga": "D1"
            }
            inner_planets.append(p_data)
            inner_planets_dict[p_name] = p_data

    outer_planets = []
    for item in outer_items:
        if item.get("type") == "planet":
            p_name = item["name"]
            s_idx = signs_list.index(item["sign"])
            pl_lon = s_idx * 30 + item["degree"] + item["minute"] / 60.0
            outer_angle = lon_to_angle(pl_lon)
            p_data = {
                "item": item, "lon": pl_lon, "draw_angle": outer_angle,
                "true_angle": outer_angle, "is_lagna": (p_name == "Lagna"),
                "sign_idx": s_idx, "sign": item["sign"], "varga": "D9"
            }
            outer_planets.append(p_data)

    relax_planet_angles(inner_planets, has_ascendant_barrier=True, is_outer=False)
    relax_planet_angles(outer_planets, has_ascendant_barrier=False, is_outer=True)

    # Inner Ring: Natal Planets
    # Radii definitions
    if not nak_enabled or biwheel_mode == "original":
        r_in_pl = 112
        r_in_deg = 90
        r_in_min = 74
        r_in_nak = None
    elif biwheel_mode == "combined_degmin":
        r_in_pl = 112
        r_in_degmin = 98
        r_in_nak = 83
    else:  # compact_stack (User Recommended)
        r_in_pl = 112
        r_in_deg = 100   # Closer to planet glyph (gap was 22px, now 12px!)
        r_in_min = 89    # Gap 11px
        r_in_nak = 76    # Towards inner circle, gap 13px, leaves 32px to bhava ring 44!

    svg += '<g class="inner-planets-group">\n'
    for p in inner_planets:
        item = p["item"]
        angle = p["draw_angle"]
        p_name = item["name"]
        info = planet_notations.get(p_name, {})
        label = info.get("symbol", p_name[:2])
        color = info.get("color", "#000")
        is_retro = item.get("is_retrograde", False)
        nak_abbr = get_nak_abbr(item.get("nakshatra", ""), nak_len)

        px, py = polar_coords(r_in_pl, angle)
        font_sz = 9.5 if p_name == "Lagna" else 12.0

        svg += f'<g class="interactive inner-planet" data-id="{p_name}">\n'

        if not nak_enabled or biwheel_mode == "original":
            # Original spacing
            mx, my = polar_coords(r_in_min, angle)
            svg += f'<text x="{mx}" y="{my}" font-size="5.8" stroke="#F7F3EB" stroke-width="1.0" paint-order="stroke" fill="{color}" text-anchor="middle" dominant-baseline="central">{item["minute"]:02d}\'{" R" if is_retro else ""}</text>\n'
            dx, dy = polar_coords(r_in_deg, angle)
            svg += f'<text x="{dx}" y="{dy}" font-size="6.8" stroke="#F7F3EB" stroke-width="1.2" paint-order="stroke" fill="{color}" text-anchor="middle" dominant-baseline="central">{item["degree"]}°</text>\n'
            svg += f'<text x="{px}" y="{py}" font-size="{font_sz}" font-family="{ASTRO_FONT_STACK}" stroke="#F7F3EB" stroke-width="2.2" paint-order="stroke" fill="{color}" font-weight="bold" text-anchor="middle" dominant-baseline="central">{label}</text>\n'
        elif biwheel_mode == "combined_degmin":
            # Combined Deg+Min at r=98, Nakshatra at r=83
            svg += f'<text x="{px}" y="{py}" font-size="{font_sz}" font-family="{ASTRO_FONT_STACK}" stroke="#F7F3EB" stroke-width="2.2" paint-order="stroke" fill="{color}" font-weight="bold" text-anchor="middle" dominant-baseline="central">{label}</text>\n'
            dx, dy = polar_coords(r_in_degmin, angle)
            svg += f'<text x="{dx}" y="{dy}" font-size="6.5" stroke="#F7F3EB" stroke-width="1.2" paint-order="stroke" fill="{color}" text-anchor="middle" dominant-baseline="central">{item["degree"]}°{item["minute"]:02d}\'{" R" if is_retro else ""}</text>\n'
            nx, ny = polar_coords(r_in_nak, angle)
            svg += f'<text x="{nx}" y="{ny}" font-size="5.5" font-weight="600" stroke="#F7F3EB" stroke-width="1.0" paint-order="stroke" fill="{nak_color}" text-anchor="middle" dominant-baseline="central" letter-spacing="0.2px">{nak_abbr}</text>\n'
        else:
            # Compact Stack: Glyph (112), Deg (100), Min (89), Nakshatra (76)
            svg += f'<text x="{px}" y="{py}" font-size="{font_sz}" font-family="{ASTRO_FONT_STACK}" stroke="#F7F3EB" stroke-width="2.2" paint-order="stroke" fill="{color}" font-weight="bold" text-anchor="middle" dominant-baseline="central">{label}</text>\n'
            dx, dy = polar_coords(r_in_deg, angle)
            svg += f'<text x="{dx}" y="{dy}" font-size="6.8" stroke="#F7F3EB" stroke-width="1.2" paint-order="stroke" fill="{color}" text-anchor="middle" dominant-baseline="central">{item["degree"]}°</text>\n'
            mx, my = polar_coords(r_in_min, angle)
            svg += f'<text x="{mx}" y="{my}" font-size="5.8" stroke="#F7F3EB" stroke-width="1.0" paint-order="stroke" fill="{color}" text-anchor="middle" dominant-baseline="central">{item["minute"]:02d}\'{" R" if is_retro else ""}</text>\n'
            nx, ny = polar_coords(r_in_nak, angle)
            svg += f'<text x="{nx}" y="{ny}" font-size="5.5" font-weight="600" stroke="#F7F3EB" stroke-width="1.0" paint-order="stroke" fill="{nak_color}" text-anchor="middle" dominant-baseline="central" letter-spacing="0.2px">{nak_abbr}</text>\n'

        svg += '</g>\n'
    svg += '</g>\n'

    # Outer Ring: Harmonic Planets (D9)
    r_out_pl = 172
    r_out_deg = 181
    r_out_min = 190
    r_out_sign = 199

    svg += '<g class="outer-planets-group">\n'
    for p in outer_planets:
        item = p["item"]
        angle = p["draw_angle"]
        p_name = item["name"]
        info = planet_notations.get(p_name, {})
        label = info.get("symbol", p_name[:2])
        color = info.get("color", "#000")
        is_retro = item.get("is_retrograde", False)
        s_sym, s_col, _ = sign_symbols.get(item["sign"], ("?", "#000", "?"))

        pl_r = (r_out_pl - 1.5) if p_name == "Lagna" else r_out_pl
        px, py = polar_coords(pl_r, angle)
        mx, my = polar_coords(r_out_min, angle)
        dx, dy = polar_coords(r_out_deg, angle)
        sx, sy = polar_coords(r_out_sign, angle)

        font_sz = 7.8 if p_name == "Lagna" else 11.0

        svg += f'<g class="interactive outer-planet" data-id="{p_name}">\n'
        svg += f'<text x="{mx}" y="{my}" font-size="5.2" stroke="#FAF6F0" stroke-width="0.8" paint-order="stroke" fill="{color}" text-anchor="middle" dominant-baseline="central">{item["minute"]:02d}\'{" R" if is_retro else ""}</text>\n'
        svg += f'<text x="{dx}" y="{dy}" font-size="6.2" stroke="#FAF6F0" stroke-width="0.9" paint-order="stroke" fill="{color}" text-anchor="middle" dominant-baseline="central">{item["degree"]}°</text>\n'
        svg += f'<text x="{px}" y="{py}" font-size="{font_sz}" font-family="{ASTRO_FONT_STACK}" stroke="#FAF6F0" stroke-width="2.2" paint-order="stroke" fill="{color}" font-weight="600" text-anchor="middle" dominant-baseline="central">{label}</text>\n'
        svg += f'<text x="{sx}" y="{sy}" font-size="6.5" font-family="{ASTRO_FONT_STACK}" stroke="#FAF6F0" stroke-width="0.9" paint-order="stroke" fill="{s_col}" font-weight="bold" text-anchor="middle" dominant-baseline="central">{s_sym}</text>\n'
        svg += '</g>\n'
    svg += '</g>\n'

    svg += '</svg>\n'
    return svg


def render_isolated_south_cell(sign, planets_data, cusp_num="1", nak_enabled=True, nak_len="3", nak_placement="above_planet", nak_color="#8c7b64", cell_size=180):
    """
    Renders an isolated high-resolution South Indian cell (180x180 px)
    to visually stress-test spacing with 1, 2, 3, or 4 planets.
    """
    svg = f'<svg width="{cell_size}" height="{cell_size}" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" style="background:#fffdfa; border:1px solid #d5c8b2; border-radius:6px;">\n'

    # Fill & border
    svg += '<rect x="0" y="0" width="100" height="100" fill="#eedec9"/>\n'
    svg += '<rect x="0" y="0" width="100" height="100" fill="none" stroke="#5C4433" stroke-width="2"/>\n'

    # Sign & cusp corners
    s_sym, s_col, _ = sign_symbols[sign]
    svg += f'<text x="87" y="13" font-size="10.5" font-family="{ASTRO_FONT_STACK}" font-weight="bold" fill="{s_col}" opacity="0.8" text-anchor="middle" dominant-baseline="central">{s_sym}</text>\n'
    svg += f'<text x="13" y="87" font-family="sans-serif" font-size="10" font-weight="bold" fill="#7D3C98" text-anchor="middle" dominant-baseline="central">{cusp_num}</text>\n'

    # Planets along diagonal (16, 16) -> (84, 84)
    p_start_x, p_start_y = 16, 16
    p_end_x, p_end_y = 84, 84
    t_values = get_equidistant_t(len(planets_data))

    for idx, p in enumerate(planets_data):
        t = t_values[idx]
        px = p_start_x + (p_end_x - p_start_x) * t
        py = p_start_y + (p_end_y - p_start_y) * t

        info = planet_notations.get(p["name"], {"symbol": p["name"][:2], "color": "#000"})
        label = info.get("symbol", p["name"][:2])
        is_retro = p.get("is_retrograde", False)
        deg_str = f"{p['degree']}°{p['minute']:02d}'"
        nak_abbr = get_nak_abbr(p.get("nakshatra", ""), nak_len)

        if not nak_enabled:
            svg += f'<text x="{px}" y="{py - 2}" font-family="{ASTRO_FONT_STACK}" font-size="13" font-weight="bold" fill="{info["color"]}" text-anchor="middle" dominant-baseline="central">{label}</text>\n'
            svg += f'<text x="{px}" y="{py + 11}" font-family="sans-serif" font-size="9" fill="#5C4433" text-anchor="middle" dominant-baseline="central"><tspan>{deg_str}</tspan>{f"""<tspan font-size="8" font-weight="bold" fill="#C0392B"> R</tspan>""" if is_retro else ""}</text>\n'
        elif nak_placement == "above_planet":
            svg += f'<text x="{px}" y="{py - 10.5}" font-family="sans-serif" font-size="5.5" font-weight="600" fill="{nak_color}" text-anchor="middle" dominant-baseline="central" letter-spacing="0.2px">{nak_abbr}</text>\n'
            svg += f'<text x="{px}" y="{py - 1.5}" font-family="{ASTRO_FONT_STACK}" font-size="12.5" font-weight="bold" fill="{info["color"]}" text-anchor="middle" dominant-baseline="central">{label}</text>\n'
            svg += f'<text x="{px}" y="{py + 9}" font-family="sans-serif" font-size="8.2" fill="#5C4433" text-anchor="middle" dominant-baseline="central"><tspan>{deg_str}</tspan>{f"""<tspan font-size="7.5" font-weight="bold" fill="#C0392B"> R</tspan>""" if is_retro else ""}</text>\n'
        elif nak_placement == "inline_degree":
            # 1. Planet at exact original (px, py - 2):
            svg += f'<text x="{px}" y="{py - 2}" font-family="{ASTRO_FONT_STACK}" font-size="13" font-weight="bold" fill="{info["color"]}" text-anchor="middle" dominant-baseline="central">{label}</text>\n'
            # 2. Degree dead-centered at exact original (px, py + 11):
            svg += f'<text x="{px}" y="{py + 11}" font-family="sans-serif" font-size="9" fill="#5C4433" text-anchor="middle" dominant-baseline="central"><tspan>{deg_str}</tspan>{f"""<tspan font-size="8" font-weight="bold" fill="#C0392B"> R</tspan>""" if is_retro else ""}</text>\n'
            # 3. Nakshatra accompanying on left or right on same baseline:
            if px > 55:
                # Accompany on LEFT side (anchored end at px - 16)
                svg += f'<text x="{px - 16:.1f}" y="{py + 11}" font-family="sans-serif" font-size="5.8" font-weight="600" fill="{nak_color}" text-anchor="end" dominant-baseline="central" letter-spacing="0.2px">{nak_abbr}</text>\n'
            else:
                # Accompany on RIGHT side (anchored start at px + offset)
                offset_r = 21 if is_retro else 16
                svg += f'<text x="{px + offset_r:.1f}" y="{py + 11}" font-family="sans-serif" font-size="5.8" font-weight="600" fill="{nak_color}" text-anchor="start" dominant-baseline="central" letter-spacing="0.2px">{nak_abbr}</text>\n'
        elif nak_placement == "under_degree_compact":
            svg += f'<text x="{px}" y="{py - 3.5}" font-family="{ASTRO_FONT_STACK}" font-size="11.5" font-weight="bold" fill="{info["color"]}" text-anchor="middle" dominant-baseline="central">{label}</text>\n'
            svg += f'<text x="{px}" y="{py + 5.5}" font-family="sans-serif" font-size="8.0" fill="#5C4433" text-anchor="middle" dominant-baseline="central"><tspan>{deg_str}</tspan>{f"""<tspan font-size="7.0" font-weight="bold" fill="#C0392B"> R</tspan>""" if is_retro else ""}</text>\n'
            svg += f'<text x="{px}" y="{py + 13.5}" font-family="sans-serif" font-size="5.2" font-weight="600" fill="{nak_color}" text-anchor="middle" dominant-baseline="central" letter-spacing="0.2px">{nak_abbr}</text>\n'
        elif nak_placement == "superscript":
            svg += f'<text x="{px}" y="{py - 1}" font-family="{ASTRO_FONT_STACK}" font-size="13" font-weight="bold" fill="{info["color"]}" text-anchor="middle" dominant-baseline="central">{label}</text>\n'
            svg += f'<text x="{px + 8.5}" y="{py - 7}" font-family="sans-serif" font-size="5.2" font-weight="600" fill="{nak_color}" text-anchor="start" dominant-baseline="central">{nak_abbr}</text>\n'
            svg += f'<text x="{px}" y="{py + 10}" font-family="sans-serif" font-size="8.5" fill="#5C4433" text-anchor="middle" dominant-baseline="central"><tspan>{deg_str}</tspan>{f"""<tspan font-size="7.5" font-weight="bold" fill="#C0392B"> R</tspan>""" if is_retro else ""}</text>\n'

    svg += '</svg>\n'
    return svg


def render_biwheel_geometry_diagram():
    """
    Renders an annotated SVG diagram showing the radial circles of the inner wheel,
    illustrating how moving the degree closer to the glyph opens up space for the nakshatra.
    """
    svg = '<svg width="100%" height="340" viewBox="-160 -150 440 310" xmlns="http://www.w3.org/2000/svg" style="background:#fffdfa; border:1px solid #d5c8b2; border-radius:8px;">\n'

    # Background arc wedge
    svg += '<path d="M 0 0 L -130 0 A 138 138 0 0 1 0 -138 Z" fill="#faede0" opacity="0.45"/>\n'

    # Concentric circles
    circles = [
        (138, "#8c7b64", "1.5", "r=138 (Outer boundary of D1 inner wheel)"),
        (112, "#dc2626", "1.4", "r=112 (Planet Glyph anchor)"),
        (100, "#2563eb", "1.2", "r=100 (NEW: Degree closer to glyph, gap=12px)"),
        (89,  "#059669", "1.2", "r=89 (NEW: Minute anchor, gap=11px)"),
        (76,  "#d97706", "1.4", "r=76 (NEW: Nakshatra towards inner circle)"),
        (44,  "#27ae60", "1.1", "r=44 (Bhava dashed ring)"),
        (28,  "#5C4433", "1.0", "r=28 (Center circle)"),
    ]

    for r, col, sw, desc in circles:
        svg += f'<circle cx="0" cy="0" r="{r}" fill="none" stroke="{col}" stroke-width="{sw}" stroke-dasharray="{"3,3" if r in (44, 89) else "none"}"/>\n'

    # Planet glyph sample along 135 deg angle
    ang = 135
    rad = math.radians(ang)
    x_ray1, y_ray1 = 28 * math.cos(rad), 28 * math.sin(rad)
    x_ray2, y_ray2 = 138 * math.cos(rad), 138 * math.sin(rad)
    svg += f'<line x1="{x_ray1}" y1="{y_ray1}" x2="{x_ray2}" y2="{y_ray2}" stroke="#b45309" stroke-width="1.5" stroke-dasharray="2,2"/>\n'

    # Place sample annotations along ray
    # Glyph at r=112
    gx, gy = 112 * math.cos(rad), 112 * math.sin(rad)
    svg += f'<circle cx="{gx}" cy="{gy}" r="10" fill="#fffdfa" stroke="#dc2626" stroke-width="1.5"/>\n'
    svg += f'<text x="{gx}" y="{gy}" font-family="{ASTRO_FONT_STACK}" font-size="12" font-weight="bold" fill="#dc2626" text-anchor="middle" dominant-baseline="central">☉</text>\n'

    # Degree at r=100
    dx, dy = 100 * math.cos(rad), 100 * math.sin(rad)
    svg += f'<circle cx="{dx}" cy="{dy}" r="7.5" fill="#fffdfa" stroke="#2563eb" stroke-width="1.2"/>\n'
    svg += f'<text x="{dx}" y="{dy}" font-family="sans-serif" font-size="7.5" font-weight="bold" fill="#2563eb" text-anchor="middle" dominant-baseline="central">24°</text>\n'

    # Minute at r=89
    mx, my = 89 * math.cos(rad), 89 * math.sin(rad)
    svg += f'<circle cx="{mx}" cy="{my}" r="7" fill="#fffdfa" stroke="#059669" stroke-width="1.2"/>\n'
    svg += f'<text x="{mx}" y="{my}" font-family="sans-serif" font-size="7" font-weight="bold" fill="#059669" text-anchor="middle" dominant-baseline="central">15\'</text>\n'

    # Nakshatra at r=76
    nx, ny = 76 * math.cos(rad), 76 * math.sin(rad)
    svg += f'<circle cx="{nx}" cy="{ny}" r="8" fill="#fffdfa" stroke="#d97706" stroke-width="1.5"/>\n'
    svg += f'<text x="{nx}" y="{ny}" font-family="sans-serif" font-size="7" font-weight="bold" fill="#d97706" text-anchor="middle" dominant-baseline="central">Kri</text>\n'

    # Dimension callouts on right side
    svg += '<g font-family="sans-serif" font-size="9" fill="#3e2819">\n'
    # r=112 to r=100
    svg += '  <line x1="24" y1="-112" x2="24" y2="-100" stroke="#dc2626" stroke-width="1.5"/>\n'
    svg += '  <line x1="20" y1="-112" x2="28" y2="-112" stroke="#dc2626" stroke-width="1.5"/>\n'
    svg += '  <line x1="20" y1="-100" x2="28" y2="-100" stroke="#dc2626" stroke-width="1.5"/>\n'
    svg += '  <text x="34" y="-106" font-weight="bold" fill="#dc2626" dominant-baseline="central">12px <tspan font-weight="normal" fill="#6b5a4b">(Glyph r=112 → Degree r=100)</tspan></text>\n'

    # r=100 to r=89
    svg += '  <line x1="24" y1="-100" x2="24" y2="-89" stroke="#2563eb" stroke-width="1.5"/>\n'
    svg += '  <line x1="20" y1="-89" x2="28" y2="-89" stroke="#2563eb" stroke-width="1.5"/>\n'
    svg += '  <text x="34" y="-94.5" font-weight="bold" fill="#2563eb" dominant-baseline="central">11px <tspan font-weight="normal" fill="#6b5a4b">(Degree r=100 → Minute r=89)</tspan></text>\n'

    # r=89 to r=76
    svg += '  <line x1="24" y1="-89" x2="24" y2="-76" stroke="#d97706" stroke-width="1.5"/>\n'
    svg += '  <line x1="20" y1="-76" x2="28" y2="-76" stroke="#d97706" stroke-width="1.5"/>\n'
    svg += '  <text x="34" y="-82.5" font-weight="bold" fill="#d97706" dominant-baseline="central">13px <tspan font-weight="normal" fill="#6b5a4b">(Minute r=89 → Nakshatra r=76)</tspan></text>\n'

    # r=76 to r=44
    svg += '  <line x1="24" y1="-76" x2="24" y2="-44" stroke="#27ae60" stroke-width="1.5" stroke-dasharray="2,2"/>\n'
    svg += '  <line x1="20" y1="-44" x2="28" y2="-44" stroke="#27ae60" stroke-width="1.5"/>\n'
    svg += '  <text x="34" y="-60" font-weight="bold" fill="#27ae60" dominant-baseline="central">32px <tspan font-weight="normal" fill="#6b5a4b">(Clearance to Bhava Dashed Ring r=44)</tspan></text>\n'
    svg += '</g>\n'

    # Bottom labels
    svg += '<text x="0" y="125" font-family="Cinzel, serif" font-size="11" font-weight="bold" fill="#5C4433" text-anchor="middle">Inner Natal Wheel (D1) Radial Stacking</text>\n'
    svg += '<text x="0" y="142" font-family="sans-serif" font-size="8.5" fill="#8c7b64" text-anchor="middle">Glyph (r=112) → Deg (r=100) → Min (r=89) → Nakshatra (r=76)</text>\n'

    svg += '</svg>\n'
    return svg

print("Functions compiled successfully.")

def generate_full_preview_html():
    chart, items_d1, items_d9 = build_test_items()

    # Pre-render North Indian SVGs
    north_svgs = {
        "off": render_north_indian_preview(items_d1, nak_enabled=False),
        "under_3": render_north_indian_preview(items_d1, nak_enabled=True, nak_len="3", nak_placement="under_degree"),
        "under_4": render_north_indian_preview(items_d1, nak_enabled=True, nak_len="4", nak_placement="under_degree"),
        "above_3": render_north_indian_preview(items_d1, nak_enabled=True, nak_len="3", nak_placement="above_planet"),
        "above_4": render_north_indian_preview(items_d1, nak_enabled=True, nak_len="4", nak_placement="above_planet"),
    }

    # Pre-render South Indian SVGs
    south_svgs = {
        "off": render_south_indian_preview(items_d1, nak_enabled=False),
        "above_3": render_south_indian_preview(items_d1, nak_enabled=True, nak_len="3", nak_placement="above_planet"),
        "above_4": render_south_indian_preview(items_d1, nak_enabled=True, nak_len="4", nak_placement="above_planet"),
        "inline_3": render_south_indian_preview(items_d1, nak_enabled=True, nak_len="3", nak_placement="inline_degree"),
        "inline_4": render_south_indian_preview(items_d1, nak_enabled=True, nak_len="4", nak_placement="inline_degree"),
        "compact_3": render_south_indian_preview(items_d1, nak_enabled=True, nak_len="3", nak_placement="under_degree_compact"),
        "compact_4": render_south_indian_preview(items_d1, nak_enabled=True, nak_len="4", nak_placement="under_degree_compact"),
        "super_3": render_south_indian_preview(items_d1, nak_enabled=True, nak_len="3", nak_placement="superscript"),
        "super_4": render_south_indian_preview(items_d1, nak_enabled=True, nak_len="4", nak_placement="superscript"),
    }

    # Pre-render Bi-Wheel SVGs
    biwheel_svgs = {
        "off": render_biwheel_preview(items_d1, items_d9, nak_enabled=False, biwheel_mode="original"),
        "compact_3": render_biwheel_preview(items_d1, items_d9, nak_enabled=True, nak_len="3", biwheel_mode="compact_stack"),
        "compact_4": render_biwheel_preview(items_d1, items_d9, nak_enabled=True, nak_len="4", biwheel_mode="compact_stack"),
        "combined_3": render_biwheel_preview(items_d1, items_d9, nak_enabled=True, nak_len="3", biwheel_mode="combined_degmin"),
        "combined_4": render_biwheel_preview(items_d1, items_d9, nak_enabled=True, nak_len="4", biwheel_mode="combined_degmin"),
    }

    # Stress test isolated cells
    test_1p = [{"name": "Sun", "degree": 24, "minute": 15, "is_retrograde": False, "nakshatra": "Krittika"}]
    test_2p = [
        {"name": "Moon", "degree": 4, "minute": 7, "is_retrograde": False, "nakshatra": "Anuradha"},
        {"name": "Jupiter", "degree": 12, "minute": 35, "is_retrograde": False, "nakshatra": "Jyeshtha"}
    ]
    test_3p = [
        {"name": "Sun", "degree": 12, "minute": 10, "is_retrograde": False, "nakshatra": "Krittika"},
        {"name": "Mercury", "degree": 18, "minute": 45, "is_retrograde": False, "nakshatra": "Rohini"},
        {"name": "Venus", "degree": 24, "minute": 20, "is_retrograde": False, "nakshatra": "Mrigashira"}
    ]
    test_4p = [
        {"name": "Moon", "degree": 2, "minute": 30, "is_retrograde": False, "nakshatra": "Uttara Ashadha"},
        {"name": "Mars", "degree": 8, "minute": 15, "is_retrograde": False, "nakshatra": "Shravana"},
        {"name": "Jupiter", "degree": 16, "minute": 40, "is_retrograde": False, "nakshatra": "Shravana"},
        {"name": "Saturn", "degree": 25, "minute": 10, "is_retrograde": False, "nakshatra": "Dhanishtha"}
    ]

    stress_cells = {}
    densities = [("1p", "Taurus", test_1p, "2"), ("2p", "Sagittarius", test_2p, "9"),
                 ("3p", "Aries", test_3p, "1"), ("4p", "Capricorn", test_4p, "10")]

    for key, sign, p_data, c_num in densities:
        stress_cells[key] = {
            "off": render_isolated_south_cell(sign, p_data, cusp_num=c_num, nak_enabled=False),
            "above_3": render_isolated_south_cell(sign, p_data, cusp_num=c_num, nak_enabled=True, nak_len="3", nak_placement="above_planet"),
            "above_4": render_isolated_south_cell(sign, p_data, cusp_num=c_num, nak_enabled=True, nak_len="4", nak_placement="above_planet"),
            "inline_3": render_isolated_south_cell(sign, p_data, cusp_num=c_num, nak_enabled=True, nak_len="3", nak_placement="inline_degree"),
            "inline_4": render_isolated_south_cell(sign, p_data, cusp_num=c_num, nak_enabled=True, nak_len="4", nak_placement="inline_degree"),
            "compact_3": render_isolated_south_cell(sign, p_data, cusp_num=c_num, nak_enabled=True, nak_len="3", nak_placement="under_degree_compact"),
            "compact_4": render_isolated_south_cell(sign, p_data, cusp_num=c_num, nak_enabled=True, nak_len="4", nak_placement="under_degree_compact"),
            "super_3": render_isolated_south_cell(sign, p_data, cusp_num=c_num, nak_enabled=True, nak_len="3", nak_placement="superscript"),
            "super_4": render_isolated_south_cell(sign, p_data, cusp_num=c_num, nak_enabled=True, nak_len="4", nak_placement="superscript"),
        }

    biwheel_diagram_svg = render_biwheel_geometry_diagram()

    print("All SVGs pre-rendered successfully!")
    return north_svgs, south_svgs, biwheel_svgs, stress_cells, biwheel_diagram_svg

if __name__ == "__main__":
    generate_full_preview_html()

def write_preview_html():
    north_svgs, south_svgs, biwheel_svgs, stress_cells, biwheel_diagram_svg = generate_full_preview_html()

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Astra Preview: Planet Nakshatra Display System</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700&family=Inter:wght@400;500;600;700&family=STIX+Two+Math&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-parchment: #fffdfa;
            --bg-card: #fdfbf7;
            --border-warm: #d5c8b2;
            --border-dark: #5C4433;
            --text-primary: #3e2819;
            --text-secondary: #6b5a4b;
            --text-muted: #8c7b64;
            --accent-bronze: #b45309;
            --accent-kendra: #eedec9;
            --accent-trikona: #faede0;
            --accent-blue: #0284c7;
            --accent-purple: #7d3c98;
            --font-glyphs: 'STIX Two Math', 'Cambria Math', 'DejaVu Sans', 'Apple Symbols', sans-serif;
            --font-serif: 'Cinzel', Georgia, serif;
            --font-sans: 'Inter', system-ui, -apple-system, sans-serif;
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            background: #f7f3ec;
            color: var(--text-primary);
            font-family: var(--font-sans);
            font-size: 14px;
            line-height: 1.5;
            padding: 24px;
        }}

        .preview-container {{
            max-width: 1440px;
            margin: 0 auto;
            background: var(--bg-parchment);
            border: 1px solid var(--border-warm);
            border-radius: 12px;
            box-shadow: 0 10px 30px rgba(62, 40, 25, 0.08);
            overflow: hidden;
        }}

        /* Header */
        .preview-header {{
            background: linear-gradient(135deg, #fdfbf7 0%, #faede0 100%);
            border-bottom: 2px solid var(--border-warm);
            padding: 24px 32px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 16px;
        }}

        .preview-title h1 {{
            font-family: var(--font-serif);
            font-size: 24px;
            font-weight: 700;
            color: #3e2819;
            letter-spacing: 0.5px;
        }}

        .preview-title p {{
            font-size: 13px;
            color: var(--text-secondary);
            margin-top: 4px;
        }}

        .badge-kala {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: #faede0;
            border: 1px solid #d5c8b2;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            color: #b45309;
        }}

        /* Sticky Control Toolbar */
        .control-toolbar {{
            position: sticky;
            top: 0;
            z-index: 100;
            background: #fffdfa;
            border-bottom: 1px solid var(--border-warm);
            padding: 14px 32px;
            display: flex;
            align-items: center;
            flex-wrap: wrap;
            gap: 20px;
            box-shadow: 0 4px 12px rgba(62, 40, 25, 0.04);
        }}

        .control-group {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .control-label {{
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: var(--text-secondary);
        }}

        /* Segmented Button Controls */
        .seg-control {{
            display: inline-flex;
            background: #ede8df;
            padding: 3px;
            border-radius: 8px;
            border: 1px solid #d5c8b2;
        }}

        .seg-btn {{
            background: transparent;
            border: none;
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 600;
            color: var(--text-secondary);
            cursor: pointer;
            transition: all 0.15s ease;
        }}

        .seg-btn:hover {{
            color: var(--text-primary);
        }}

        .seg-btn.active {{
            background: #fff;
            color: var(--text-primary);
            box-shadow: 0 2px 4px rgba(62, 40, 25, 0.1);
        }}

        /* Master Toggle Switch */
        .switch-label {{
            display: inline-flex;
            align-items: center;
            gap: 10px;
            cursor: pointer;
            font-weight: 600;
            font-size: 13px;
            color: var(--text-primary);
            user-select: none;
        }}

        .switch-input {{
            position: absolute;
            opacity: 0;
            width: 0;
            height: 0;
        }}

        .switch-slider {{
            position: relative;
            display: inline-block;
            width: 44px;
            height: 24px;
            background-color: #cbd5e1;
            border-radius: 24px;
            transition: .25s;
        }}

        .switch-slider:before {{
            position: absolute;
            content: "";
            height: 18px;
            width: 18px;
            left: 3px;
            bottom: 3px;
            background-color: white;
            border-radius: 50%;
            transition: .25s;
            box-shadow: 0 1px 3px rgba(0,0,0,0.2);
        }}

        .switch-input:checked + .switch-slider {{
            background-color: #b45309;
        }}

        .switch-input:checked + .switch-slider:before {{
            transform: translateX(20px);
        }}

        /* Navigation Tabs */
        .nav-tabs {{
            display: flex;
            background: #f7f3ec;
            border-bottom: 1px solid var(--border-warm);
            padding: 0 32px;
            gap: 4px;
            overflow-x: auto;
        }}

        .nav-tab {{
            background: transparent;
            border: none;
            padding: 12px 18px;
            font-size: 13px;
            font-weight: 600;
            color: var(--text-secondary);
            cursor: pointer;
            border-bottom: 3px solid transparent;
            transition: all 0.15s ease;
            white-space: nowrap;
        }}

        .nav-tab:hover {{
            color: var(--text-primary);
            background: rgba(255, 255, 255, 0.5);
        }}

        .nav-tab.active {{
            color: #b45309;
            border-bottom-color: #b45309;
            background: var(--bg-parchment);
        }}

        /* Tab Content Area */
        .tab-content {{
            display: none;
            padding: 32px;
        }}

        .tab-content.active {{
            display: block;
        }}

        /* Two-Column Grid for Charts & Diagnostics */
        .chart-layout-grid {{
            display: grid;
            grid-template-columns: 1fr 380px;
            gap: 28px;
            align-items: start;
        }}

        @media (max-width: 1024px) {{
            .chart-layout-grid {{
                grid-template-columns: 1fr;
            }}
        }}

        .chart-card {{
            background: #fffdfa;
            border: 1px solid var(--border-warm);
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 4px 16px rgba(62, 40, 25, 0.04);
            display: flex;
            flex-direction: column;
            align-items: center;
        }}

        .chart-viewport {{
            width: 100%;
            max-width: 600px;
            aspect-ratio: 1 / 1;
        }}

        .chart-viewport svg {{
            width: 100%;
            height: 100%;
            display: block;
        }}

        .panel-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-warm);
            border-radius: 8px;
            padding: 20px;
        }}

        .panel-card h3 {{
            font-family: var(--font-serif);
            font-size: 16px;
            font-weight: 700;
            color: #3e2819;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .panel-card p {{
            font-size: 13px;
            color: var(--text-secondary);
            margin-bottom: 14px;
            line-height: 1.55;
        }}

        .spec-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 0;
            border-bottom: 1px solid #ede8df;
            font-size: 12.5px;
        }}

        .spec-item:last-child {{
            border-bottom: none;
        }}

        .spec-label {{
            font-weight: 500;
            color: var(--text-secondary);
        }}

        .spec-val {{
            font-weight: 600;
            color: var(--text-primary);
        }}

        .spec-chip {{
            background: #faede0;
            color: #b45309;
            padding: 2px 8px;
            border-radius: 4px;
            font-family: monospace;
            font-size: 12px;
            font-weight: bold;
        }}

        /* Stress Test Grid */
        .stress-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}

        .stress-card {{
            background: #fffdfa;
            border: 1px solid var(--border-warm);
            border-radius: 8px;
            padding: 16px;
            text-align: center;
        }}

        .stress-card h4 {{
            font-size: 13.5px;
            font-weight: 700;
            color: #3e2819;
            margin-bottom: 6px;
        }}

        .stress-card p {{
            font-size: 12px;
            color: var(--text-secondary);
            margin-bottom: 12px;
        }}

        .stress-viewport {{
            width: 180px;
            height: 180px;
            margin: 0 auto;
        }}

        /* Settings Mockup */
        .modal-mockup {{
            max-width: 620px;
            margin: 0 auto;
            background: #fffdfa;
            border: 1px solid var(--border-warm);
            border-radius: 12px;
            box-shadow: 0 12px 32px rgba(62, 40, 25, 0.12);
            overflow: hidden;
        }}

        .modal-header {{
            background: linear-gradient(135deg, #fdfbf7 0%, #faede0 100%);
            border-bottom: 1px solid var(--border-warm);
            padding: 18px 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .modal-header h2 {{
            font-family: var(--font-serif);
            font-size: 17px;
            font-weight: 700;
            color: #3e2819;
        }}

        .modal-body {{
            padding: 24px;
            display: flex;
            flex-direction: column;
            gap: 20px;
        }}

        .setting-section {{
            border-bottom: 1px solid #ede8df;
            padding-bottom: 16px;
        }}

        .setting-section:last-child {{
            border-bottom: none;
            padding-bottom: 0;
        }}

        .setting-section h4 {{
            font-size: 13px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: var(--text-secondary);
            margin-bottom: 10px;
        }}

        .setting-card {{
            background: #fdfbf7;
            border: 1px solid var(--border-warm);
            border-radius: 8px;
            padding: 12px 16px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }}

        .setting-card:last-child {{
            margin-bottom: 0;
        }}

        .setting-info strong {{
            font-size: 13.5px;
            color: var(--text-primary);
            display: block;
        }}

        .setting-info span {{
            font-size: 12px;
            color: var(--text-secondary);
        }}

        /* Table */
        .nak-table-container {{
            border: 1px solid var(--border-warm);
            border-radius: 8px;
            overflow: hidden;
            background: #fffdfa;
        }}

        .nak-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
            font-variant-numeric: tabular-nums;
        }}

        .nak-table th {{
            background: #f7f3ec;
            padding: 10px 14px;
            text-align: left;
            font-weight: 600;
            color: var(--text-secondary);
            border-bottom: 2px solid var(--border-warm);
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .nak-table td {{
            padding: 10px 14px;
            border-bottom: 1px solid #ede8df;
            color: var(--text-primary);
        }}

        .nak-table tr:hover {{
            background: #faf7f0;
        }}

        .code-chip {{
            display: inline-block;
            background: #faede0;
            color: #b45309;
            font-family: monospace;
            font-weight: bold;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 12px;
        }}

        /* Utility */
        .callout {{
            background: #fdfaf5;
            border-left: 3px solid #b45309;
            padding: 12px 16px;
            border-radius: 0 6px 6px 0;
            margin-top: 16px;
            font-size: 12.5px;
            color: var(--text-secondary);
        }}
    </style>
</head>
<body>

<div class="preview-container">
    <!-- Header -->
    <header class="preview-header">
        <div class="preview-title">
            <h1>Planet Nakshatra Display System</h1>
            <p>Interactive Design Preview & Mathematical Layout Verification for Astra</p>
        </div>
        <div class="badge-kala">
            <span>✨</span> Ernst Wilhelm Kala Integrated Methodology
        </div>
    </header>

    <!-- Interactive Sticky Control Toolbar -->
    <div class="control-toolbar">
        <!-- Master Switch -->
        <div class="control-group">
            <label class="switch-label">
                <input type="checkbox" id="masterNakToggle" class="switch-input" checked onchange="updateView()">
                <span class="switch-slider"></span>
                <span>Show Nakshatras</span>
            </label>
        </div>

        <div style="width: 1px; height: 28px; background: var(--border-warm);"></div>

        <!-- Abbreviation Length -->
        <div class="control-group">
            <span class="control-label">Abbreviation:</span>
            <div class="seg-control">
                <button type="button" class="seg-btn" id="btn-len-3" onclick="setNakLen('3')">3-Letter (Anu, Kri)</button>
                <button type="button" class="seg-btn active" id="btn-len-4" onclick="setNakLen('4')">4-Letter (Anur, Krit)</button>
            </div>
        </div>

        <div style="width: 1px; height: 28px; background: var(--border-warm);"></div>

        <!-- Color Tone -->
        <div class="control-group">
            <span class="control-label">Color:</span>
            <div class="seg-control">
                <button type="button" class="seg-btn active" id="btn-col-bronze" onclick="setNakColor('#8c7b64')">Pale Bronze (#8c7b64)</button>
                <button type="button" class="seg-btn" id="btn-col-sand" onclick="setNakColor('#a89f91')">Soft Sand (#a89f91)</button>
                <button type="button" class="seg-btn" id="btn-col-degree" onclick="setNakColor('#5C4433')">Match Degree</button>
            </div>
        </div>
    </div>

    <!-- Navigation Tabs -->
    <nav class="nav-tabs">
        <button type="button" class="nav-tab active" onclick="switchTab('north')">1. North Indian Chart</button>
        <button type="button" class="nav-tab" onclick="switchTab('south')">2. South Indian Chart</button>
        <button type="button" class="nav-tab" onclick="switchTab('biwheel')">3. Harmonic Bi-Wheel</button>
        <button type="button" class="nav-tab" onclick="switchTab('stress')">4. South Indian Space Solutions</button>
        <button type="button" class="nav-tab" onclick="switchTab('geometry')">5. Bi-Wheel Geometry Explainer</button>
        <button type="button" class="nav-tab" onclick="switchTab('settings')">6. Settings Modal Mockup</button>
        <button type="button" class="nav-tab" onclick="switchTab('table')">7. 27 Nakshatras Reference</button>
    </nav>

    <!-- Tab 1: North Indian Chart -->
    <div id="tab-north" class="tab-content active">
        <div class="chart-layout-grid">
            <div class="chart-card">
                <div style="width: 100%; display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                    <h3 style="font-family: var(--font-serif); font-size: 16px; color: #3e2819;">D1 Rasi — North Indian Chart</h3>
                    <!-- North Placement Toggle -->
                    <div class="seg-control">
                        <button type="button" class="seg-btn active" id="btn-north-under" onclick="setNorthPlacement('under_degree')">Under Degree (User Preferred)</button>
                        <button type="button" class="seg-btn" id="btn-north-above" onclick="setNorthPlacement('above_planet')">Above Planet Symbol</button>
                    </div>
                </div>

                <div class="chart-viewport" id="viewport-north">
                    {north_svgs["under_4"]}
                </div>
            </div>

            <!-- Diagnostics Panel -->
            <div class="panel-card">
                <h3><span>📐</span> North Indian Layout Mechanics</h3>
                <p>In North Indian diamond geometry, planetary clusters are spaced along the Kendra horizontal/vertical axes or along the triangular outer edges.</p>

                <div class="spec-item">
                    <span class="spec-label">User Preference</span>
                    <span class="spec-chip">Under Degree</span>
                </div>
                <div class="spec-item">
                    <span class="spec-label">Vertical Stack</span>
                    <span class="spec-val">Glyph (py-3) → Deg (py+7.5) → Nak (py+16)</span>
                </div>
                <div class="spec-item">
                    <span class="spec-label">Abbreviation Format</span>
                    <span class="spec-chip">4-Letter (Krit, Anur, UPha)</span>
                </div>
                <div class="spec-item">
                    <span class="spec-label">Total Bounding Height</span>
                    <span class="spec-val">28px (Centers safely in 50px cell)</span>
                </div>
                <div class="spec-item">
                    <span class="spec-label">Typography Floor</span>
                    <span class="spec-val">5.8px SVG text (Pale bronze #8c7b64)</span>
                </div>

                <div class="callout">
                    <strong>Confirmed Layout:</strong> Placing the 4-letter nakshatra underneath the degree creates a natural visual hierarchy: 
                    <code>Glyph (Subject) → 24°15' (Coordinate) → Krit (Star Sphere)</code>.
                    The pale bronze color prevents visual competition with the planet glyph.
                </div>
            </div>
        </div>
    </div>

    <!-- Tab 2: South Indian Chart -->
    <div id="tab-south" class="tab-content">
        <div class="chart-layout-grid">
            <div class="chart-card">
                <div style="width: 100%; display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-wrap: wrap; gap: 8px;">
                    <h3 style="font-family: var(--font-serif); font-size: 16px; color: #3e2819;">D1 Rasi — South Indian Chart</h3>
                    <!-- South Placement Toggle -->
                    <div class="seg-control">
                        <button type="button" class="seg-btn active" id="btn-south-inline" onclick="setSouthPlacement('inline_degree')">B: Inline (Adaptive L/R)</button>
                        <button type="button" class="seg-btn" id="btn-south-above" onclick="setSouthPlacement('above_planet')">A: Above Planet</button>
                        <button type="button" class="seg-btn" id="btn-south-compact" onclick="setSouthPlacement('under_degree_compact')">C: Compact Stack</button>
                        <button type="button" class="seg-btn" id="btn-south-super" onclick="setSouthPlacement('superscript')">D: Superscript</button>
                    </div>
                </div>

                <div class="chart-viewport" id="viewport-south">
                    {south_svgs["inline_4"]}
                </div>
            </div>

            <!-- Diagnostics Panel -->
            <div class="panel-card">
                <h3><span>🧭</span> South Indian Adaptive Strategy</h3>
                <p>You chose: <strong>Inline on the same level as degree with adaptive Left/Right switching</strong>.</p>

                <div class="spec-item">
                    <span class="spec-label">Selected Strategy</span>
                    <span class="spec-chip">Inline (Adaptive L/R)</span>
                </div>
                <div class="spec-item">
                    <span class="spec-label">Left Half of Cell (px ≤ 55)</span>
                    <span class="spec-val">Nakshatra on RIGHT: <code>2°30' UAsh</code></span>
                </div>
                <div class="spec-item">
                    <span class="spec-label">Right Half of Cell (px > 55)</span>
                    <span class="spec-val">Nakshatra on LEFT: <code>Dhan 25°10'</code></span>
                </div>
                <div class="spec-item">
                    <span class="spec-label">Vertical Space Added</span>
                    <span class="spec-val">0px (Zero extra vertical span!)</span>
                </div>
                <div class="spec-item">
                    <span class="spec-label">Color Standard</span>
                    <span class="spec-chip">Pale Bronze (#8c7b64)</span>
                </div>

                <div class="callout">
                    <strong>Boundary Protection:</strong> When approaching the right wall or corner symbols, placing the 4-letter nakshatra on the left directs text into the spacious center of the cell, avoiding all clipping even in dense 4-planet stelliums!
                </div>
            </div>
        </div>
    </div>

    <!-- Tab 3: Harmonic Bi-Wheel -->
    <div id="tab-biwheel" class="tab-content">
        <div class="chart-layout-grid">
            <div class="chart-card">
                <div style="width: 100%; display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                    <h3 style="font-family: var(--font-serif); font-size: 16px; color: #3e2819;">D1 Natal · D9 Navamsha Bi-Wheel</h3>
                    <!-- Biwheel Mode Toggle -->
                    <div class="seg-control">
                        <button type="button" class="seg-btn active" id="btn-biwheel-compact" onclick="setBiwheelMode('compact_stack')">Adjusted Radial Stack (r=76)</button>
                        <button type="button" class="seg-btn" id="btn-biwheel-combined" onclick="setBiwheelMode('combined_degmin')">Combined Deg+Min (r=83)</button>
                        <button type="button" class="seg-btn" id="btn-biwheel-original" onclick="setBiwheelMode('original')">Original Bi-Wheel</button>
                    </div>
                </div>

                <div class="chart-viewport" id="viewport-biwheel">
                    {biwheel_svgs["compact_4"]}
                </div>
            </div>

            <!-- Diagnostics Panel -->
            <div class="panel-card">
                <h3><span>⚙️</span> Bi-Wheel Radial Space Optimization</h3>
                <p>You noted: <em>"in the harmonic bival there's a lot of space between the degree and the Planet symbol. So one could put the degree closer to the planet symbol and then do on the towards the inner circle do the name of the nakshatra."</em></p>

                <div class="spec-item">
                    <span class="spec-label">Original Glyph-Deg Gap</span>
                    <span class="spec-chip">22px (r=112 to r=90)</span>
                </div>
                <div class="spec-item">
                    <span class="spec-label">New Glyph-Deg Gap</span>
                    <span class="spec-chip">12px (r=112 to r=100)</span>
                </div>
                <div class="spec-item">
                    <span class="spec-label">Degree Anchor</span>
                    <span class="spec-val">r = 100 (Closer to glyph)</span>
                </div>
                <div class="spec-item">
                    <span class="spec-label">Minute Anchor</span>
                    <span class="spec-val">r = 89</span>
                </div>
                <div class="spec-item">
                    <span class="spec-label">Nakshatra Anchor</span>
                    <span class="spec-val">r = 76 (Towards inner circle)</span>
                </div>
                <div class="spec-item">
                    <span class="spec-label">Abbreviation Format</span>
                    <span class="spec-chip">4-Letter (Anur, Krit)</span>
                </div>
                <div class="spec-item">
                    <span class="spec-label">Clearance to Bhava Ring</span>
                    <span class="spec-val">32px (Generous breathing room to r=44)</span>
                </div>

                <div class="callout">
                    <strong>Radial Alignment:</strong> All 4 items (Glyph → Degree → Minute → Nakshatra) stay perfectly locked along the planet's radial ray pointing towards the center bindu!
                </div>
            </div>
        </div>
    </div>

    <!-- Tab 4: High-Density Stress Test (South Indian) -->
    <div id="tab-stress" class="tab-content">
        <h3 style="font-family: var(--font-serif); font-size: 18px; margin-bottom: 8px;">South Indian Cell Spacing Stress Test</h3>
        <p style="color: var(--text-secondary); margin-bottom: 20px;">
            Side-by-side verification of isolated South Indian cells across 1, 2, 3, and 4 planets per sign.
            Demonstrating your chosen <strong>Option B: Inline with Degree (Adaptive Left/Right)</strong>!
        </p>

        <div class="stress-grid">
            <div class="stress-card">
                <h4>1 Planet — Sun (Krittika)</h4>
                <p>Taurus (H2) · Single placement</p>
                <div class="stress-viewport" id="stress-1p">
                    {stress_cells["1p"]["inline_4"]}
                </div>
            </div>

            <div class="stress-card">
                <h4>2 Planets — Moon + Jupiter</h4>
                <p>Sagittarius (H9) · Dual conjunction</p>
                <div class="stress-viewport" id="stress-2p">
                    {stress_cells["2p"]["inline_4"]}
                </div>
            </div>

            <div class="stress-card">
                <h4>3 Planets — Sun + Merc + Venus</h4>
                <p>Aries (H1) · Triple cluster</p>
                <div class="stress-viewport" id="stress-3p">
                    {stress_cells["3p"]["inline_4"]}
                </div>
            </div>

            <div class="stress-card">
                <h4>4 Planets — Stellium</h4>
                <p>Capricorn (H10) · Extreme density</p>
                <div class="stress-viewport" id="stress-4p">
                    {stress_cells["4p"]["inline_4"]}
                </div>
            </div>
        </div>

        <div class="callout" style="margin-top: 24px;">
            <strong>Conclusion for South Indian Cells:</strong>
            Notice how <strong>Option B (Inline with Degree)</strong> and <strong>Option A (Above Planet)</strong> remain crisp and completely collision-free even with 4 planets packed into a single 100x100 cell.
            Option C (Compact Stack) also works mathematically by reducing vertical spacing from 22px to 17px, but Option B provides the greatest reading comfort.
        </div>
    </div>

    <!-- Tab 5: Bi-Wheel Geometry Explainer -->
    <div id="tab-geometry" class="tab-content">
        <div class="chart-layout-grid">
            <div class="chart-card">
                <h3 style="font-family: var(--font-serif); font-size: 16px; margin-bottom: 12px; align-self: flex-start;">Inner Wheel Radial Coordinate Breakdown</h3>
                <div style="width: 100%;">
                    {biwheel_diagram_svg}
                </div>
            </div>

            <div class="panel-card">
                <h3><span>📏</span> Radial Mathematics</h3>
                <p>In the original Bi-Wheel, there was a disproportionate <strong>22px empty gap</strong> between the planet glyph at <code>r=112</code> and the degree at <code>r=90</code>.</p>
                <p>By moving the degree closer to the glyph, we reclaim <strong>10px of radial space</strong>, enabling a crisp, uncluttered 4-layer stack:</p>

                <div class="spec-item">
                    <span class="spec-label">Layer 1: Planet Glyph</span>
                    <span class="spec-val">r = 112</span>
                </div>
                <div class="spec-item">
                    <span class="spec-label">Layer 2: Degree Number</span>
                    <span class="spec-val">r = 100 (Gap = 12px)</span>
                </div>
                <div class="spec-item">
                    <span class="spec-label">Layer 3: Arc Minutes</span>
                    <span class="spec-val">r = 89 (Gap = 11px)</span>
                </div>
                <div class="spec-item">
                    <span class="spec-label">Layer 4: Nakshatra Abbr</span>
                    <span class="spec-val">r = 76 (Gap = 13px)</span>
                </div>
                <div class="spec-item">
                    <span class="spec-label">D1 Bhava Dashed Ring</span>
                    <span class="spec-val">r = 44 (32px clearance)</span>
                </div>
            </div>
        </div>
    </div>

    <!-- Tab 6: Settings Modal Mockup -->
    <div id="tab-settings" class="tab-content">
        <div class="modal-mockup">
            <div class="modal-header">
                <h2>⚙️ Chart Display Settings (Astra Mockup)</h2>
                <span style="font-size: 18px; color: var(--text-secondary); cursor: pointer;">✕</span>
            </div>
            <div class="modal-body">
                <!-- Existing Planet Notation Section -->
                <div class="setting-section">
                    <h4>Planet Notation Mode</h4>
                    <div class="setting-card">
                        <div class="setting-info">
                            <strong>Astronomical Symbols</strong>
                            <span>☉ ☽ ♂ ☿ ♃ ♀ ♄ ☊ ☋ Asc</span>
                        </div>
                        <input type="radio" name="mockNotation" checked>
                    </div>
                </div>

                <!-- NEW: Planet Nakshatra Display Section -->
                <div class="setting-section" style="background: #faf7f0; padding: 14px; border-radius: 8px; border: 1px dashed #b45309;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                        <div>
                            <h4 style="color: #b45309; margin-bottom: 2px;">Planet Nakshatra Display</h4>
                            <span style="font-size: 12px; color: var(--text-secondary);">Show star sphere abbreviations on North, South & Bi-Wheel charts</span>
                        </div>
                        <label class="switch-label">
                            <input type="checkbox" checked class="switch-input">
                            <span class="switch-slider"></span>
                        </label>
                    </div>

                    <div style="display: flex; flex-direction: column; gap: 10px; margin-top: 10px;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-size: 12.5px; font-weight: 500;">Abbreviation Length:</span>
                            <div class="seg-control">
                                <button type="button" class="seg-btn active">3-Letter (Anu)</button>
                                <button type="button" class="seg-btn">4-Letter (Anur)</button>
                            </div>
                        </div>

                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-size: 12.5px; font-weight: 500;">North Indian Placement:</span>
                            <div class="seg-control">
                                <button type="button" class="seg-btn active">Underneath Degree</button>
                                <button type="button" class="seg-btn">Above Planet</button>
                            </div>
                        </div>

                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-size: 12.5px; font-weight: 500;">South Indian Strategy:</span>
                            <div class="seg-control">
                                <button type="button" class="seg-btn active">Above Planet</button>
                                <button type="button" class="seg-btn">Inline with Degree</button>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Existing House Colors Section -->
                <div class="setting-section">
                    <h4>Chart House Colors</h4>
                    <div class="setting-card">
                        <div class="setting-info">
                            <strong>Kendra Houses (1, 4, 7, 10)</strong>
                            <span>Angular foundation pillars</span>
                        </div>
                        <span class="spec-chip" style="background:#eedec9;">#eedec9</span>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Tab 7: 27 Nakshatras Reference Table -->
    <div id="tab-table" class="tab-content">
        <h3 style="font-family: var(--font-serif); font-size: 18px; margin-bottom: 6px;">The 27 Sidereal Equatorial Nakshatras</h3>
        <p style="color: var(--text-secondary); margin-bottom: 16px;">Standard 3-Letter and 4-Letter Abbreviations formulated for optimal clarity and zero ambiguity.</p>

        <div class="nak-table-container">
            <table class="nak-table">
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Nakshatra Name</th>
                        <th>3-Letter</th>
                        <th>4-Letter</th>
                        <th>Zodiac Span</th>
                        <th>Vimshottari Ruler</th>
                        <th>Vedic Presiding Deity</th>
                    </tr>
                </thead>
                <tbody>
"""

    for idx, d in enumerate(NAKSHATRA_DATA, 1):
        html_content += f"""                    <tr>
                        <td>{idx}</td>
                        <td><strong>{d["name"]}</strong></td>
                        <td><span class="code-chip">{d["3"]}</span></td>
                        <td><span class="code-chip">{d["4"]}</span></td>
                        <td>{d["span"]}</td>
                        <td>{d["lord"]}</td>
                        <td>{d["deity"]}</td>
                    </tr>
"""

    html_content += f"""                </tbody>
            </table>
        </div>
    </div>
</div>

<script>
    // Embedded SVG dictionaries
    const northSVGs = {json.dumps(north_svgs)};
    const southSVGs = {json.dumps(south_svgs)};
    const biwheelSVGs = {json.dumps(biwheel_svgs)};
    const stressCells = {json.dumps(stress_cells)};

    // App state
    let state = {{
        nakEnabled: true,
        nakLen: '4',
        nakColor: '#8c7b64',
        northPlacement: 'under_degree',
        southPlacement: 'inline_degree',
        biwheelMode: 'compact_stack'
    }};

    function switchTab(tabId) {{
        document.querySelectorAll('.nav-tab').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        
        event.target.classList.add('active');
        document.getElementById('tab-' + tabId).classList.add('active');
    }}

    function setNakLen(len) {{
        state.nakLen = len;
        document.getElementById('btn-len-3').classList.toggle('active', len === '3');
        document.getElementById('btn-len-4').classList.toggle('active', len === '4');
        updateView();
    }}

    function setNakColor(col) {{
        state.nakColor = col;
        document.getElementById('btn-col-bronze').classList.toggle('active', col === '#8c7b64');
        document.getElementById('btn-col-sand').classList.toggle('active', col === '#a89f91');
        document.getElementById('btn-col-degree').classList.toggle('active', col === '#5C4433');
        
        // Dynamically tint nakshatra texts in all rendered SVGs
        document.querySelectorAll('.chart-viewport svg text[fill="#8c7b64"], .chart-viewport svg text[fill="#a89f91"], .chart-viewport svg text[fill="#5C4433"]').forEach(el => {{
            if (el.getAttribute('letter-spacing') || el.classList.contains('nak-badge') || (el.getAttribute('font-size') && parseFloat(el.getAttribute('font-size')) <= 6.0)) {{
                el.setAttribute('fill', col);
            }}
        }});
        document.querySelectorAll('.stress-viewport svg tspan[fill="#8c7b64"], .stress-viewport svg text[fill="#8c7b64"]').forEach(el => {{
            el.setAttribute('fill', col);
        }});
    }}

    function setNorthPlacement(pos) {{
        state.northPlacement = pos;
        document.getElementById('btn-north-under').classList.toggle('active', pos === 'under_degree');
        document.getElementById('btn-north-above').classList.toggle('active', pos === 'above_planet');
        updateView();
    }}

    function setSouthPlacement(pos) {{
        state.southPlacement = pos;
        document.getElementById('btn-south-above').classList.toggle('active', pos === 'above_planet');
        document.getElementById('btn-south-inline').classList.toggle('active', pos === 'inline_degree');
        document.getElementById('btn-south-compact').classList.toggle('active', pos === 'under_degree_compact');
        document.getElementById('btn-south-super').classList.toggle('active', pos === 'superscript');
        updateView();
    }}

    function setBiwheelMode(mode) {{
        state.biwheelMode = mode;
        document.getElementById('btn-biwheel-compact').classList.toggle('active', mode === 'compact_stack');
        document.getElementById('btn-biwheel-combined').classList.toggle('active', mode === 'combined_degmin');
        document.getElementById('btn-biwheel-original').classList.toggle('active', mode === 'original');
        updateView();
    }}

    function updateView() {{
        state.nakEnabled = document.getElementById('masterNakToggle').checked;

        // 1. North Indian
        let northKey = 'off';
        if (state.nakEnabled) {{
            const pKey = state.northPlacement === 'under_degree' ? 'under' : 'above';
            northKey = pKey + '_' + state.nakLen;
        }}
        document.getElementById('viewport-north').innerHTML = northSVGs[northKey] || northSVGs['off'];

        // 2. South Indian
        let southKey = 'off';
        if (state.nakEnabled) {{
            const mapP = {{
                'above_planet': 'above',
                'inline_degree': 'inline',
                'under_degree_compact': 'compact',
                'superscript': 'super'
            }};
            southKey = (mapP[state.southPlacement] || 'above') + '_' + state.nakLen;
        }}
        document.getElementById('viewport-south').innerHTML = southSVGs[southKey] || southSVGs['off'];

        // 3. Bi-Wheel
        let biKey = 'off';
        if (state.nakEnabled && state.biwheelMode !== 'original') {{
            const bP = state.biwheelMode === 'combined_degmin' ? 'combined' : 'compact';
            biKey = bP + '_' + state.nakLen;
        }}
        document.getElementById('viewport-biwheel').innerHTML = biwheelSVGs[biKey] || biwheelSVGs['off'];

        // 4. Stress Cells
        const densities = ['1p', '2p', '3p', '4p'];
        densities.forEach(k => {{
            let sKey = 'off';
            if (state.nakEnabled) {{
                const mapP = {{
                    'above_planet': 'above',
                    'inline_degree': 'inline',
                    'under_degree_compact': 'compact',
                    'superscript': 'super'
                }};
                sKey = (mapP[state.southPlacement] || 'above') + '_' + state.nakLen;
            }}
            const el = document.getElementById('stress-' + k);
            if (el && stressCells[k]) {{
                el.innerHTML = stressCells[k][sKey] || stressCells[k]['off'];
            }}
        }});

        // Re-apply custom color if non-default
        if (state.nakColor !== '#8c7b64') {{
            setNakColor(state.nakColor);
        }}
    }}
</script>

</body>
</html>
"""

    output_path = "/Users/hajnaljanos/PycharmProjects/astra/nakshatra_preview.html"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"Standalone HTML preview successfully created at: {output_path}")

if __name__ == "__main__":
    write_preview_html()
