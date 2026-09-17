import math
from typing import Dict, Any, List, Optional
from jyotish.aspects.aspects import get_graha_drishti, get_aspect_explanation
from jyotish.relationships.relationships import (
    get_dignity, get_compound_relationship, get_natural_relationship, 
    get_temporary_relationship, SIGN_LORDS
)

planet_notations = {
    "Lagna": {
        "symbol": "Asc",
        "english": "Asc",
        "devanagari": "ल",
        "translit": "Lag",
        "full_en": "Ascendant",
        "full_sa": "Lagna",
        "dev_full": "लग्न",
        "color": "#a93226"
    },
    "Sun": {
        "symbol": "☉\uFE0E",
        "english": "Su",
        "devanagari": "सू",
        "translit": "Sū",
        "full_en": "Sun",
        "full_sa": "Sūrya",
        "dev_full": "सूर्य",
        "color": "#d35400"
    },
    "Moon": {
        "symbol": "☽\uFE0E",
        "english": "Mo",
        "devanagari": "चं",
        "translit": "Ca",
        "full_en": "Moon",
        "full_sa": "Chandra",
        "dev_full": "चन्द्र",
        "color": "#4a5568"
    },
    "Mars": {
        "symbol": "♂\uFE0E",
        "english": "Ma",
        "devanagari": "मं",
        "translit": "Ma",
        "full_en": "Mars",
        "full_sa": "Mangala",
        "dev_full": "मङ्गल",
        "color": "#c0392b"
    },
    "Mercury": {
        "symbol": "☿\uFE0E",
        "english": "Me",
        "devanagari": "बु",
        "translit": "Bu",
        "full_en": "Mercury",
        "full_sa": "Budha",
        "dev_full": "बुध",
        "color": "#1e824c"
    },
    "Jupiter": {
        "symbol": "♃\uFE0E",
        "english": "Ju",
        "devanagari": "गु",
        "translit": "Gu",
        "full_en": "Jupiter",
        "full_sa": "Guru",
        "dev_full": "गुरु",
        "color": "#b7791f"
    },
    "Venus": {
        "symbol": "♀\uFE0E",
        "english": "Ve",
        "devanagari": "शु",
        "translit": "Śu",
        "full_en": "Venus",
        "full_sa": "Śukra",
        "dev_full": "शुक्र",
        "color": "#8d6e63"
    },
    "Saturn": {
        "symbol": "♄\uFE0E",
        "english": "Sa",
        "devanagari": "श",
        "translit": "Śa",
        "full_en": "Saturn",
        "full_sa": "Śani",
        "dev_full": "शनि",
        "color": "#2c3e50"
    },
    "Rahu": {
        "symbol": "☊\uFE0E",
        "english": "Ra",
        "devanagari": "रा",
        "translit": "Rā",
        "full_en": "North Node",
        "full_sa": "Rāhu",
        "dev_full": "राहु",
        "color": "#5d6d7e"
    },
    "Ketu": {
        "symbol": "☋\uFE0E",
        "english": "Ke",
        "devanagari": "के",
        "translit": "Ke",
        "full_en": "South Node",
        "full_sa": "Ketu",
        "dev_full": "केतु",
        "color": "#34495e"
    }
}

# Compatibility mapping
planet_symbols = {k: (v["symbol"], v["color"]) for k, v in planet_notations.items()}

# Soft antique parchment tone for Rashi signs so they blend elegantly into the background
RASHI_SIGN_COLOR = "#b59472"

sign_symbols = {
    "Aries": ("♈\uFE0E", RASHI_SIGN_COLOR, "Ar"), 
    "Taurus": ("♉\uFE0E", RASHI_SIGN_COLOR, "Ta"), 
    "Gemini": ("♊\uFE0E", RASHI_SIGN_COLOR, "Ge"), 
    "Cancer": ("♋\uFE0E", RASHI_SIGN_COLOR, "Cn"), 
    "Leo": ("♌\uFE0E", RASHI_SIGN_COLOR, "Le"), 
    "Virgo": ("♍\uFE0E", RASHI_SIGN_COLOR, "Vi"), 
    "Libra": ("♎\uFE0E", RASHI_SIGN_COLOR, "Li"), 
    "Scorpio": ("♏\uFE0E", RASHI_SIGN_COLOR, "Sc"), 
    "Sagittarius": ("♐\uFE0E", RASHI_SIGN_COLOR, "Sg"), 
    "Capricorn": ("♑\uFE0E", RASHI_SIGN_COLOR, "Cp"), 
    "Aquarius": ("♒\uFE0E", RASHI_SIGN_COLOR, "Aq"), 
    "Pisces": ("♓\uFE0E", RASHI_SIGN_COLOR, "Pi")  
}

signs_list = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

def parse_varga_data(varga_data):
    items = []
    
    # Lagna
    l_sign = varga_data["lagna"]["sign"]
    l_deg = varga_data["lagna"]["degree_0_to_30"]
    minutes = int((l_deg - int(l_deg)) * 60)
    items.append({
        "type": "planet",
        "name": "Lagna",
        "sign": l_sign,
        "degree": int(l_deg),
        "minute": minutes
    })
    
    # Grahas
    for p_name, p_data in varga_data["grahas"].items():
        deg = p_data["degree_0_to_30"]
        minutes = int((deg - int(deg)) * 60)
        items.append({
            "type": "planet",
            "name": p_name,
            "sign": p_data["sign"],
            "degree": int(deg),
            "minute": minutes,
            "is_retrograde": p_data.get("is_retrograde", False)
        })
        
    # House Cusps
    for i, cusp in enumerate(varga_data.get("cusps", [])):
        c_deg = cusp.get("degree_0_to_30", 0)
        items.append({
            "type": "cusp",
            "text": str(i + 1),
            "sign": cusp["sign"],
            "degree": int(c_deg),
            "minute": int((c_deg - int(c_deg)) * 60),
            "longitude": cusp.get("longitude", 0),
            "color": "#7d3c98"
        })
        
    return items

def get_south_indian_positions(num_planets, cell_x, cell_y, has_cusps=False, cusp_side=None):
    positions = []
    # If cusps or badges are on top or bottom, adjust row heights so planet labels and degrees
    # never collide with corner cusp numbers (preserving a clean >=16px distance protector).
    if cusp_side == "bottom":
        y_r1 = cell_y + 32
        y_r2 = cell_y + 56
        y_single = cell_y + 40
    elif cusp_side == "top":
        y_r1 = cell_y + 40
        y_r2 = cell_y + 66
        y_single = cell_y + 48
    else:
        y_r1 = cell_y + 35
        y_r2 = cell_y + 65
        y_single = cell_y + 44

    if num_planets == 1:
        positions.append((cell_x + 50, y_single))
    elif num_planets == 2:
        positions.append((cell_x + 30, y_single))
        positions.append((cell_x + 70, y_single))
    elif num_planets == 3:
        positions.append((cell_x + 30, y_r1))
        positions.append((cell_x + 70, y_r1))
        positions.append((cell_x + 50, y_r2))
    elif num_planets == 4:
        positions.append((cell_x + 30, y_r1))
        positions.append((cell_x + 70, y_r1))
        positions.append((cell_x + 30, y_r2))
        positions.append((cell_x + 70, y_r2))
    elif num_planets == 5:
        positions.append((cell_x + 20, y_r1))
        positions.append((cell_x + 50, y_r1))
        positions.append((cell_x + 80, y_r1))
        positions.append((cell_x + 35, y_r2))
        positions.append((cell_x + 65, y_r2))
    elif num_planets == 6:
        positions.append((cell_x + 20, y_r1))
        positions.append((cell_x + 50, y_r1))
        positions.append((cell_x + 80, y_r1))
        positions.append((cell_x + 20, y_r2))
        positions.append((cell_x + 50, y_r2))
        positions.append((cell_x + 80, y_r2))
    elif num_planets == 7:
        positions.append((cell_x + 20, cell_y + 25))
        positions.append((cell_x + 50, cell_y + 25))
        positions.append((cell_x + 80, cell_y + 25))
        positions.append((cell_x + 35, cell_y + 50))
        positions.append((cell_x + 65, cell_y + 50))
        positions.append((cell_x + 30, cell_y + 75))
        positions.append((cell_x + 70, cell_y + 75))
    else:
        positions.append((cell_x + 20, cell_y + 25))
        positions.append((cell_x + 50, cell_y + 25))
        positions.append((cell_x + 80, cell_y + 25))
        positions.append((cell_x + 20, cell_y + 50))
        positions.append((cell_x + 50, cell_y + 50))
        positions.append((cell_x + 80, cell_y + 50))
        positions.append((cell_x + 35, cell_y + 75))
        positions.append((cell_x + 65, cell_y + 75))
    return positions

def get_north_indian_positions(num_planets, cx, cy, has_cusps=False):
    positions = []
    if num_planets == 1:
        py = cy - (14 if has_cusps else 8)
        positions.append((cx, py))
    elif num_planets == 2:
        py = cy - (14 if has_cusps else 8)
        positions.append((cx - 24, py))
        positions.append((cx + 24, py))
    elif num_planets == 3:
        r1_y = cy - (22 if has_cusps else 18)
        r2_y = cy + (5 if has_cusps else 16)
        positions.append((cx - 24, r1_y))
        positions.append((cx + 24, r1_y))
        positions.append((cx, r2_y))
    elif num_planets == 4:
        r1_y = cy - (22 if has_cusps else 18)
        r2_y = cy + (5 if has_cusps else 16)
        positions.append((cx - 24, r1_y))
        positions.append((cx + 24, r1_y))
        positions.append((cx - 24, r2_y))
        positions.append((cx + 24, r2_y))
    elif num_planets == 5:
        r1_y = cy - (22 if has_cusps else 16)
        r2_y = cy + (5 if has_cusps else 18)
        positions.append((cx - 22, r1_y))
        positions.append((cx, r1_y))
        positions.append((cx + 22, r1_y))
        positions.append((cx - 14, r2_y))
        positions.append((cx + 14, r2_y))
    else:
        r1_y = cy - (22 if has_cusps else 16)
        r2_y = cy + (5 if has_cusps else 18)
        positions.append((cx - 22, r1_y))
        positions.append((cx, r1_y))
        positions.append((cx + 22, r1_y))
        positions.append((cx - 22, r2_y))
        positions.append((cx, r2_y))
        positions.append((cx + 22, r2_y))
    return positions

def generate_south_indian_center(items_by_sign, chart_title, chart_sub, mode="symbol"):
    planet_abbr = {
        "Sun": "Su", "Moon": "Mo", "Mars": "Ma", "Mercury": "Me",
        "Jupiter": "Ju", "Venus": "Ve", "Saturn": "Sa", "Rahu": "Ra", "Ketu": "Ke"
    }
    
    # Sign breakdown
    sign_data = {}
    for s in signs_list:
        planets = [it for it in items_by_sign[s] if it.get("type") == "planet" and it.get("name") != "Lagna"]
        has_lagna = any(it.get("type") == "planet" and it.get("name") == "Lagna" for it in items_by_sign[s])
        sign_data[s] = {
            "planets": planets,
            "has_lagna": has_lagna,
            "count": len(planets)
        }

    matrix_defs = [
        ("Fire", "#c0392b", [("Aries", "Ar"), ("Leo", "Le"), ("Sagittarius", "Sg")]),
        ("Earth", "#795548", [("Capricorn", "Cp"), ("Taurus", "Ta"), ("Virgo", "Vi")]),
        ("Air", "#1976d2", [("Libra", "Li"), ("Aquarius", "Aq"), ("Gemini", "Ge")]),
        ("Water", "#00897b", [("Cancer", "Cn"), ("Scorpio", "Sc"), ("Pisces", "Pi")])
    ]

    row_totals = [sum(sign_data[s]["count"] for s, _ in signs) for _, _, signs in matrix_defs]
    col_totals = [sum(sign_data[signs[c][0]]["count"] for _, _, signs in matrix_defs) for c in range(3)]
    grand_total = sum(row_totals)

    svg = '<g class="si-center-container" style="cursor: pointer;" onclick="if(window.cycleSouthCenter)window.cycleSouthCenter(this);" data-view="title">\n'
    svg += '<rect x="100" y="100" width="200" height="200" fill="#fdfbf7" fill-opacity="0.01"/>\n'

    # VIEW 1: TITLE
    svg += '  <g class="si-center-view si-view-title">\n'
    svg += f'    <text x="200" y="182" font-family="sans-serif" font-size="17" font-weight="bold" fill="#4a3325" text-anchor="middle">{chart_title}</text>\n'
    svg += f'    <text x="200" y="206" font-family="sans-serif" font-size="12" fill="#8c7b64" text-anchor="middle">{chart_sub}</text>\n'
    svg += '    <g transform="translate(134, 232)">\n'
    svg += '      <rect x="0" y="0" width="132" height="22" rx="11" fill="#f7f3eb" stroke="#d5c8b2" stroke-width="1.2"/>\n'
    svg += '      <text x="66" y="15" font-family="sans-serif" font-size="10" font-weight="bold" fill="#6b5a4b" text-anchor="middle">Sign Matrix [↺]</text>\n'
    svg += '    </g>\n'
    svg += '  </g>\n'

    # VIEW 2: SIMPLISTIC 3x4 MATRIX (Matching user preference)
    # Columns: C (Cardinal/Chara), F (Fixed/Sthira), M (Mutable/Dual)
    # Rows: F (Fire), A (Air), E (Earth), W (Water)
    svg += '  <g class="si-center-view si-view-matrix" style="display:none;">\n'
    svg += '    <rect x="102" y="102" width="196" height="196" rx="4" fill="#fdfbf7" stroke="#d5c8b2" stroke-width="1"/>\n'
    svg += '    <text x="112" y="121" font-family="sans-serif" font-size="8.5" font-weight="bold" fill="#6b5a4b" letter-spacing="0.5">SIGN MATRIX</text>\n'
    svg += '    <text x="290" y="121" font-family="sans-serif" font-size="8" fill="#8c7b64" text-anchor="end">[↺ Anatomy]</text>\n'

    # Mapping based on user example:
    # Top headers: C, F, M
    # Left headers: F (Fire), A (Air), E (Earth), W (Water)
    matrix_defs = [
        ("Fire", "F", "#c0392b", [("Aries", "Cardinal"), ("Leo", "Fixed"), ("Sagittarius", "Mutable")]),
        ("Air", "A", "#d97706", [("Libra", "Cardinal"), ("Aquarius", "Fixed"), ("Gemini", "Mutable")]),
        ("Earth", "E", "#2e7d32", [("Capricorn", "Cardinal"), ("Taurus", "Fixed"), ("Virgo", "Mutable")]),
        ("Water", "W", "#1976d2", [("Cancer", "Cardinal"), ("Scorpio", "Fixed"), ("Pisces", "Mutable")])
    ]

    col_headers = [
        ("C", "Cardinal / Movable (Chara): Aries, Libra, Capricorn, Cancer"),
        ("F", "Fixed (Sthira): Leo, Aquarius, Taurus, Scorpio"),
        ("M", "Mutable / Dual (Dvisvabhava): Sagittarius, Gemini, Virgo, Pisces")
    ]

    def get_planet_glyph(p_name):
        info = planet_notations.get(p_name, {})
        if mode == "devanagari":
            return info.get("devanagari", p_name[:2])
        elif mode == "english":
            return info.get("english", p_name[:2])
        else:
            return info.get("symbol", p_name[:2])

    lagna_glyph = "ल" if mode == "devanagari" else ("Asc" if mode == "english" else "AC")

    col_xs = [149, 189, 229]
    row_ys = [157, 183, 209, 235]
    col_w = 40
    row_h = 26

    # 1. Top column headers: C, F, M
    for c_idx, (col_letter, col_tip) in enumerate(col_headers):
        cx = col_xs[c_idx] + col_w / 2
        svg += f'    <g><title>{col_tip}</title><text x="{cx}" y="148" font-family="sans-serif" font-size="10" font-weight="bold" fill="#5c4433" text-anchor="middle" dominant-baseline="central">{col_letter}</text></g>\n'

    # 2. Grid base background
    svg += f'    <rect x="149" y="157" width="120" height="104" fill="#faf8f2"/>\n'

    # 3. Cells and left row headers
    for r_idx, (elem_name, elem_code, elem_color, signs) in enumerate(matrix_defs):
        ry = row_ys[r_idx]
        row_tip = f"{elem_name} (Agni/Vayu/Prithvi/Jala): {', '.join([s[0] for s in signs])}"
        svg += f'    <g><title>{row_tip}</title><text x="139" y="{ry + row_h/2}" font-family="sans-serif" font-size="10" font-weight="bold" fill="{elem_color}" text-anchor="middle" dominant-baseline="central">{elem_code}</text></g>\n'

        for c_idx, (s_name, s_quality) in enumerate(signs):
            cx = col_xs[c_idx]
            s_info = sign_data[s_name]
            p_list = s_info["planets"]
            has_l = s_info["has_lagna"]

            # Highlight cell background if occupied
            if p_list or has_l:
                svg += f'    <rect x="{cx}" y="{ry}" width="{col_w}" height="{row_h}" fill="#ffffff"/>\n'

            def render_tspan(glyph, p_n, base_sz):
                if mode == "symbol" and p_n in ["Mars", "Venus"]:
                    adj_sz = round(base_sz * 0.82, 1)
                    sw = 0.55 if base_sz <= 10 else 0.7
                    return f'<tspan font-size="{adj_sz}" stroke="{elem_color}" stroke-width="{sw}" paint-order="stroke fill">{glyph}</tspan>'
                return f'<tspan font-size="{base_sz}">{glyph}</tspan>'

            items_to_render = [(get_planet_glyph(p["name"]), p["name"]) for p in p_list]
            if has_l:
                items_to_render.append((lagna_glyph, "Lagna"))

            p_details = [f"{p['name']} ({p['deg']}{' R' if p.get('is_retrograde') else ''})" for p in p_list]
            if has_l:
                p_details.append("Ascendant (AC)")
            tooltip_str = f"{s_name} ({elem_name} / {s_quality}): {', '.join(p_details) if p_details else 'Empty'}"

            center_x = cx + col_w / 2
            center_y = ry + row_h / 2

            if not items_to_render:
                svg += f'    <g><title>{tooltip_str}</title><rect x="{cx}" y="{ry}" width="{col_w}" height="{row_h}" fill="transparent"/></g>\n'
            elif len(items_to_render) == 1:
                tspan_str = render_tspan(items_to_render[0][0], items_to_render[0][1], 11.5)
                svg += f'    <g><title>{tooltip_str}</title><text x="{center_x}" y="{center_y}" font-family="sans-serif" font-weight="bold" fill="{elem_color}" text-anchor="middle" dominant-baseline="central">{tspan_str}</text></g>\n'
            elif len(items_to_render) == 2:
                tspan_str = "  ".join([render_tspan(g, n, 10.5) for g, n in items_to_render])
                svg += f'    <g><title>{tooltip_str}</title><text x="{center_x}" y="{center_y}" font-family="sans-serif" font-weight="bold" fill="{elem_color}" text-anchor="middle" dominant-baseline="central">{tspan_str}</text></g>\n'
            elif len(items_to_render) == 3:
                tspan_str = " ".join([render_tspan(g, n, 9.5) for g, n in items_to_render])
                svg += f'    <g><title>{tooltip_str}</title><text x="{center_x}" y="{center_y}" font-family="sans-serif" font-weight="bold" fill="{elem_color}" text-anchor="middle" dominant-baseline="central">{tspan_str}</text></g>\n'
            else:
                mid = (len(items_to_render) + 1) // 2
                line1 = " ".join([render_tspan(g, n, 8.5) for g, n in items_to_render[:mid]])
                line2 = " ".join([render_tspan(g, n, 8.5) for g, n in items_to_render[mid:]])
                svg += f'    <g><title>{tooltip_str}</title><text x="{center_x}" y="{center_y - 5}" font-family="sans-serif" font-weight="bold" fill="{elem_color}" text-anchor="middle" dominant-baseline="central">{line1}</text><text x="{center_x}" y="{center_y + 6}" font-family="sans-serif" font-weight="bold" fill="{elem_color}" text-anchor="middle" dominant-baseline="central">{line2}</text></g>\n'

    # 4. Grid lines
    svg += f'    <line x1="189" y1="157" x2="189" y2="261" stroke="#d5c8b2" stroke-width="0.8"/>\n'
    svg += f'    <line x1="229" y1="157" x2="229" y2="261" stroke="#d5c8b2" stroke-width="0.8"/>\n'
    svg += f'    <line x1="149" y1="183" x2="269" y2="183" stroke="#d5c8b2" stroke-width="0.8"/>\n'
    svg += f'    <line x1="149" y1="209" x2="269" y2="209" stroke="#d5c8b2" stroke-width="0.8"/>\n'
    svg += f'    <line x1="149" y1="235" x2="269" y2="235" stroke="#d5c8b2" stroke-width="0.8"/>\n'
    svg += f'    <rect x="149" y="157" width="120" height="104" fill="none" stroke="#b59472" stroke-width="1"/>\n'

    svg += '    <text x="200" y="281" font-family="sans-serif" font-size="7.5" fill="#8c7b64" text-anchor="middle">Click to view Kalapurusha Anatomy ➔</text>\n'
    svg += '  </g>\n'

    # VIEW 3: KALAPURUSHA ANATOMY
    from jyotish.sign_attributes import KALAPURUSHA_ANATOMY
    svg += '  <g class="si-center-view si-view-anatomy" style="display:none;">\n'
    svg += '    <rect x="102" y="102" width="196" height="196" rx="4" fill="#fdfbf7" stroke="#d5c8b2" stroke-width="1"/>\n'
    svg += '    <rect x="102" y="102" width="196" height="18" rx="4" fill="#eae1d1"/>\n'
    svg += '    <text x="108" y="115" font-family="sans-serif" font-size="9.5" font-weight="bold" fill="#4a3325">KALAPURUSHA ANATOMY</text>\n'
    svg += '    <text x="292" y="115" font-family="sans-serif" font-size="9" fill="#8c7b64" text-anchor="end">[↺ Title]</text>\n'

    active_regions = [item for item in KALAPURUSHA_ANATOMY if sign_data[item["sign"]]["count"] > 0 or sign_data[item["sign"]]["has_lagna"]]
    if not active_regions:
        active_regions = KALAPURUSHA_ANATOMY[:5]

    y_anat = 124
    row_anat_h = 24
    for idx, item in enumerate(active_regions[:6]):
        s_name = item["sign"]
        s_info = sign_data[s_name]
        p_list = s_info["planets"]
        has_l = s_info["has_lagna"]
        p_names = [planet_abbr.get(p["name"], p["name"][:2]) for p in p_list]
        if has_l:
            p_names.append("Asc")
        p_str = ", ".join(p_names) if p_names else "—"
        sign_abbr = sign_symbols[s_name][2]
        
        bg_a = "#ffffff" if idx % 2 == 0 else "#fcf9f4"
        svg += f'    <rect x="104" y="{y_anat}" width="192" height="{row_anat_h}" fill="{bg_a}"/>\n'
        tooltip = f"{item['sign']}: {item['organs']} — {p_str}"
        svg += f'    <g><title>{tooltip}</title>\n'
        svg += f'      <text x="108" y="{y_anat + 11}" font-family="sans-serif" font-size="8.5" font-weight="bold" fill="#4a3325"><tspan fill="#b59472">{sign_abbr}</tspan> {item["region"]}</text>\n'
        svg += f'      <text x="108" y="{y_anat + 21}" font-family="sans-serif" font-size="7.5" fill="#6b5a4b">{p_str}</text>\n'
        svg += f'      <text x="290" y="{y_anat + 16}" font-family="sans-serif" font-size="8.5" font-weight="bold" fill="#a93226" text-anchor="end">({len(p_list)})</text>\n'
        svg += f'    </g>\n'
        y_anat += row_anat_h

    svg += f'    <rect x="102" y="268" width="196" height="16" fill="#eae1d1"/>\n'
    svg += f'    <text x="200" y="280" font-family="sans-serif" font-size="8" font-weight="bold" fill="#4a3325" text-anchor="middle">Active: {len(active_regions)}/12 Body Limbs</text>\n'
    svg += '    <text x="200" y="294" font-family="sans-serif" font-size="7.5" fill="#8c7b64" text-anchor="middle">Click to return to Title ➔</text>\n'
    svg += '  </g>\n'

    svg += '</g>\n'
    return svg

def polar_coords(r, angle_deg):
    rad = math.radians(angle_deg)
    return r * math.cos(rad), r * math.sin(rad)

def get_aspect_defs_svg():
    return (
        '  <defs>\n'
        '    <style>\n'
        '      .aspects-hidden:not(.aspects-filtered) .aspect-lines { display: none; }\n'
        '    </style>\n'
        '    <marker id="arrow-benefic" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#16a34a"/></marker>\n'
        '    <marker id="arrow-exalted" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#D4AC0D"/></marker>\n'
        '    <marker id="arrow-malefic" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#dc2626"/></marker>\n'
        '    <marker id="arrow-neutral" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#2563eb"/></marker>\n'
        '    <marker id="arrow-cross" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M 0 2 L 7 5 L 0 8 z" fill="#8E44AD"/></marker>\n'
        '  </defs>\n'
    )

def render_aspect_lines_group(planet_coords, dignity_map=None, is_circular=False, r_inner=76):
    """
    Renders Graha Drishti aspect lines and degree badges for SVG charts.
    planet_coords: dict { name: {"x": px, "y": py, "lon": lon, "true_angle": angle (if circular)} }
    """
    if not dignity_map:
        dignity_map = {}
    classical_planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    targets = [p for p in planet_coords.keys() if p in classical_planets + ["Lagna", "Rahu", "Ketu"]]
    
    sun_lon = planet_coords.get("Sun", {}).get("lon", 0.0)
    moon_lon = planet_coords.get("Moon", {}).get("lon", 0.0)
    
    lines_svg = '  <g class="aspect-lines">\n'
    badges_svg = ''
    
    for name_from in classical_planets:
        if name_from not in planet_coords:
            continue
        p_from = planet_coords[name_from]
        lon_from = p_from["lon"]
        dignity_from = dignity_map.get(name_from, "Neutral")
        
        # Determine Benefic vs Malefic for Graha Drishti
        if name_from in ["Jupiter", "Venus"]:
            is_benefic = True
        elif name_from == "Moon":
            diff_sun = (moon_lon - sun_lon) % 360.0
            is_benefic = diff_sun < 180.0
        elif name_from == "Mercury":
            is_benefic = dignity_from not in ["Debilitated", "Enemy", "Great Enemy"]
        else:
            is_benefic = False
            
        # Collect valid aspects from this planet first so we can stagger badge positions for co-present targets
        # Collect valid aspects from this planet first
        valid_aspects = []
        for name_to in targets:
            if name_from == name_to or name_to not in planet_coords:
                continue
            p_to = planet_coords[name_to]
            lon_to = p_to["lon"]
            virupas = get_graha_drishti(name_from, lon_from, lon_to)
            if virupas < 1.0:
                continue
            diff = (lon_to - lon_from) % 360.0
            target_sign = int(lon_to // 30)
            
            # Check mutual aspect (bidirectional)
            is_mutual = False
            if name_to in classical_planets and name_to in planet_coords:
                ret_vir = get_graha_drishti(name_to, lon_to, lon_from)
                if ret_vir >= 1.0:
                    is_mutual = True

            # Calculate geometric vector and angle from source to target
            if is_circular:
                x1_t, y1_t = polar_coords(r_inner, p_from.get("true_angle", 0))
                x2_t, y2_t = polar_coords(r_inner, p_to.get("true_angle", 0))
            else:
                x1_t, y1_t = p_from["x"], p_from["y"]
                x2_t, y2_t = p_to["x"], p_to["y"]
            dx_t = x2_t - x1_t
            dy_t = y2_t - y1_t
            dist_t = math.hypot(dx_t, dy_t)
            angle_deg = (math.degrees(math.atan2(dy_t, dx_t)) + 360.0) % 360.0
            # 8 sectors (45 deg each)
            dir_sector = int((angle_deg + 22.5) // 45.0) % 8

            valid_aspects.append({
                "name_to": name_to,
                "p_to": p_to,
                "lon_to": lon_to,
                "virupas": virupas,
                "diff": diff,
                "target_sign": target_sign,
                "is_mutual": is_mutual,
                "dir_sector": dir_sector,
                "dist": dist_t
            })

        # Group aspects by directional sector
        by_sector = {}
        for a in valid_aspects:
            sec = a["dir_sector"]
            if sec not in by_sector:
                by_sector[sec] = []
            by_sector[sec].append(a)

        # For each sector, assign distinct curve_amount to every line so lines and badges never overlap
        for sec, sec_items in by_sector.items():
            if len(sec_items) == 1:
                item = sec_items[0]
                if item["is_mutual"]:
                    item["curve_amount"] = 18.0 if is_circular else 34.0
                else:
                    item["curve_amount"] = 0.0
            else:
                # Multiple lines heading in this direction:
                # Mutual aspects always curve positive (+34px) so return arrow bows away.
                # Non-mutual aspects alternate negative and positive curvatures so all lines fan out.
                if is_circular:
                    non_mut_pool = [-16.0, 16.0, -28.0, 28.0, 0.0, -38.0, 38.0]
                else:
                    non_mut_pool = [-30.0, 52.0, -50.0, 0.0, 70.0, -68.0]
                
                nm_idx = 0
                for item in sec_items:
                    if item["is_mutual"]:
                        item["curve_amount"] = 18.0 if is_circular else 34.0
                    else:
                        item["curve_amount"] = non_mut_pool[nm_idx % len(non_mut_pool)]
                        nm_idx += 1

        # Also count aspects per target sign for chord staggering
        sign_counts = {}
        for a in valid_aspects:
            s = a["target_sign"]
            sign_counts[s] = sign_counts.get(s, 0) + 1
        sign_indices = {}

        for a in valid_aspects:
            name_to = a["name_to"]
            p_to = a["p_to"]
            lon_to = a["lon_to"]
            virupas = a["virupas"]
            diff = a["diff"]
            s = a["target_sign"]
            is_mutual = a["is_mutual"]
            curve_amount = a.get("curve_amount", 0.0)
            
            s_count = sign_counts[s]
            s_idx = sign_indices.get(s, 0)
            sign_indices[s] = s_idx + 1
            
            houses_away = int(diff // 30) + 1
            deg_round = round(diff, 1)
            vir_round = round(virupas, 1)
            
            if houses_away == 7:
                rule_exp = "7th House Full Opposition (100% full mutual sight)"
            elif name_from == "Mars" and houses_away in [4, 8]:
                rule_exp = f"Mars Special {houses_away}th House Glance (Chaturasra/Randhra Drishti)"
            elif name_from == "Jupiter" and houses_away in [5, 9]:
                rule_exp = f"Jupiter Special {houses_away}th House Glance (Trikona Dharma & Wisdom Drishti)"
            elif name_from == "Saturn" and houses_away in [3, 10]:
                rule_exp = f"Saturn Special {houses_away}th House Glance (Upachaya Duty & Persistence Drishti)"
            else:
                rule_exp = f"Partial Parāśari Angle ({deg_round}° separation, {houses_away}th house away)"
                
            if is_benefic:
                col = "#D4AC0D" if dignity_from == "Exalted" else "#16a34a"
                marker = "url(#arrow-exalted)" if dignity_from == "Exalted" else "url(#arrow-benefic)"
                stroke_dash = "none"
                nature_label = f"Benefic Light ({name_from} Subha Dṛṣṭi — Continuous)"
            else:
                col = "#dc2626"
                marker = "url(#arrow-malefic)"
                stroke_dash = "6,4"
                nature_label = f"Malefic Tension ({name_from} Aśubha Dṛṣṭi — Dashed)"
                
            # Dynamic stroke width strongly proportional to Virupas (range: 1.2px at 8v to 4.5px at 60v)
            stroke_w = f"{max(1.2, min(4.5, 0.6 + (virupas / 60.0) * 3.9)):.1f}"

            # Stagger chord fraction along arrow to distribute badges
            if is_circular:
                if s_count == 1:
                    t_frac = 0.38
                elif s_count == 2:
                    t_frac = 0.30 + s_idx * 0.18
                else:
                    t_frac = 0.25 + s_idx * 0.15
                x1, y1 = polar_coords(r_inner, p_from.get("true_angle", 0))
                x2, y2 = polar_coords(r_inner, p_to.get("true_angle", 0))
                dx, dy = x2 - x1, y2 - y1
                dist = math.hypot(dx, dy)
                if dist > 8:
                    ux, uy = dx / dist, dy / dist
                    x1_arr = x1
                    y1_arr = y1
                    x2_arr = x1 + dx * ((dist - 6.0) / dist)
                    y2_arr = y1 + dy * ((dist - 6.0) / dist)
                else:
                    ux, uy = 1.0, 0.0
                    x1_arr, y1_arr, x2_arr, y2_arr = x1, y1, x2, y2
                
                # Normal vector pointing to the right of travel direction
                nx, ny = -uy, ux
                cx = (x1_arr + x2_arr) / 2.0 + nx * curve_amount
                cy = (y1_arr + y2_arr) / 2.0 + ny * curve_amount
                
                t = t_frac
                t_inv = 1.0 - t
                badge_x = round((t_inv ** 2) * x1_arr + 2 * t_inv * t * cx + (t ** 2) * x2_arr, 1)
                badge_y = round((t_inv ** 2) * y1_arr + 2 * t_inv * t * cy + (t ** 2) * y2_arr, 1)
            else:
                if s_count == 1:
                    t_frac = 0.45
                elif s_count == 2:
                    t_frac = 0.32 + s_idx * 0.20
                else:
                    t_frac = 0.26 + s_idx * 0.15
                x1, y1 = p_from["x"], p_from["y"]
                x2, y2 = p_to["x"], p_to["y"]
                dx, dy = x2 - x1, y2 - y1
                dist = math.hypot(dx, dy)
                if dist > 26:
                    ux, uy = dx / dist, dy / dist
                    x1_arr = x1 + dx * (13.0 / dist)
                    y1_arr = y1 + dy * (13.0 / dist)
                    x2_arr = x1 + dx * ((dist - 13.0) / dist)
                    y2_arr = y1 + dy * ((dist - 13.0) / dist)
                else:
                    ux, uy = 1.0, 0.0
                    x1_arr, y1_arr, x2_arr, y2_arr = x1, y1, x2, y2
                
                # Normal vector pointing to the right of travel direction
                nx, ny = -uy, ux
                cx = (x1_arr + x2_arr) / 2.0 + nx * curve_amount
                cy = (y1_arr + y2_arr) / 2.0 + ny * curve_amount
                
                t = t_frac
                t_inv = 1.0 - t
                badge_x = round((t_inv ** 2) * x1_arr + 2 * t_inv * t * cx + (t ** 2) * x2_arr, 1)
                badge_y = round((t_inv ** 2) * y1_arr + 2 * t_inv * t * cy + (t ** 2) * y2_arr, 1)
                
            tip = (
                f"{name_from} ➔ {name_to}: {vir_round} Virūpas ({deg_round}° separation)\n"
                f"• Rule: {rule_exp}\n"
                f"• Potency: {vir_round} / 60 Virūpas\n"
                f"• Influence: {nature_label}\n"
                f"• Dignity: {dignity_from}"
            )
            
            lines_svg += f'    <path class="interactive-aspect" data-from="{name_from}" data-to="{name_to}" data-virupas="{vir_round}" data-deg="{deg_round}" data-rule="{rule_exp}" data-nature="{nature_label}" data-benefic="{"true" if is_benefic else "false"}" d="M {x1_arr:.1f},{y1_arr:.1f} Q {cx:.1f},{cy:.1f} {x2_arr:.1f},{y2_arr:.1f}" fill="none" stroke="{col}" stroke-width="{stroke_w}" stroke-dasharray="{stroke_dash}" marker-end="{marker}" stroke-opacity="0.9"><title>{tip}</title></path>\n'
            
            vir_str = f"{round(virupas)}v"
            badge_w = 26 if len(vir_str) <= 3 else 32
            badges_svg += (
                f'    <g class="interactive-aspect-badge" data-from="{name_from}" data-to="{name_to}" data-virupas="{vir_round}" data-deg="{deg_round}" style="cursor: pointer;">'
                f'<rect x="{badge_x - badge_w/2:.1f}" y="{badge_y - 7:.1f}" width="{badge_w}" height="14" rx="3" fill="#FFFDF9" fill-opacity="0.95" stroke="{col}" stroke-width="0.8" stroke-dasharray="none"/>'
                f'<text x="{badge_x:.1f}" y="{badge_y + 0.5:.1f}" text-anchor="middle" dominant-baseline="central" font-family="sans-serif" font-size="8.5" font-weight="bold" fill="{col}">{vir_str}</text>'
                f'<title>{tip}</title>'
                f'</g>\n'
            )
            
    lines_svg += badges_svg
    lines_svg += '  </g>\n'
    return lines_svg

def generate_south_indian(items, mode="symbol", varga_name="D1", root_planet="Lagna"):
    cell_coords = {
        "Pisces": (0, 0), "Aries": (100, 0), "Taurus": (200, 0), "Gemini": (300, 0),
        "Aquarius": (0, 100), "Cancer": (300, 100),
        "Capricorn": (0, 200), "Leo": (300, 200),
        "Sagittarius": (0, 300), "Scorpio": (100, 300), "Libra": (200, 300), "Virgo": (300, 300)
    }

    anchor_item = next((it for it in items if it.get("name") == root_planet), None)
    if not anchor_item:
        anchor_item = next((it for it in items if it.get("name") == "Lagna"), None)
    anchor_sign = anchor_item["sign"] if anchor_item else "Aries"
    anchor_index = signs_list.index(anchor_sign)

    # Populate items by sign first so center view can use distribution data
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
                "is_retrograde": item.get("is_retrograde", False)
            })

    svg = '<svg width="100%" height="100%" viewBox="-10 -10 420 420" class="aspects-hidden" preserveAspectRatio="xMidYMid meet" xmlns="http://www.w3.org/2000/svg" style="background:transparent;">\n'
    planet_coords = {}
    svg += '<rect x="0" y="0" width="400" height="400" fill="none" stroke="#5C4433" stroke-width="2"/>\n'
    svg += '<rect x="100" y="100" width="200" height="200" fill="none" stroke="#5C4433" stroke-width="2"/>\n'
    svg += '<line x1="100" y1="0" x2="100" y2="100" stroke="#5C4433" stroke-width="2"/>\n'
    svg += '<line x1="100" y1="300" x2="100" y2="400" stroke="#5C4433" stroke-width="2"/>\n'
    svg += '<line x1="200" y1="0" x2="200" y2="100" stroke="#5C4433" stroke-width="2"/>\n'
    svg += '<line x1="200" y1="300" x2="200" y2="400" stroke="#5C4433" stroke-width="2"/>\n'
    svg += '<line x1="300" y1="0" x2="300" y2="100" stroke="#5C4433" stroke-width="2"/>\n'
    svg += '<line x1="300" y1="300" x2="300" y2="400" stroke="#5C4433" stroke-width="2"/>\n'
    svg += '<line x1="0" y1="100" x2="100" y2="100" stroke="#5C4433" stroke-width="2"/>\n'
    svg += '<line x1="300" y1="100" x2="400" y2="100" stroke="#5C4433" stroke-width="2"/>\n'
    svg += '<line x1="0" y1="200" x2="100" y2="200" stroke="#5C4433" stroke-width="2"/>\n'
    svg += '<line x1="300" y1="200" x2="400" y2="200" stroke="#5C4433" stroke-width="2"/>\n'
    svg += '<line x1="0" y1="300" x2="100" y2="300" stroke="#5C4433" stroke-width="2"/>\n'
    svg += '<line x1="300" y1="300" x2="400" y2="300" stroke="#5C4433" stroke-width="2"/>\n'
    
    # Center Chart Interactive Area (Title / 4x3 Matrix / Anatomy)
    chart_title = varga_name
    chart_sub = "Tropical South Indian"
    if root_planet == "Moon":
        chart_title = f"{varga_name} Chandra Lagna"
        chart_sub = "Moon as Ascendant (H1)"
    elif root_planet == "Sun":
        chart_title = f"{varga_name} Surya Lagna"
        chart_sub = "Sun as Ascendant (H1)"

    svg += generate_south_indian_center(items_by_sign, chart_title, chart_sub, mode=mode)

    # Quadrant Map: (cusp_dx, cusp_dy, sign_dx, sign_dy)
    quadrant_map = {
        "Pisces": (14, 14, 86, 86),
        "Aries": (14, 14, 86, 86),
        "Aquarius": (14, 14, 86, 86),
        "Taurus": (86, 14, 14, 86),
        "Gemini": (86, 14, 14, 86),
        "Cancer": (86, 14, 14, 86),
        "Leo": (86, 86, 14, 14),
        "Virgo": (86, 86, 14, 14),
        "Libra": (86, 86, 14, 14),
        "Scorpio": (14, 86, 86, 14),
        "Sagittarius": (14, 86, 86, 14),
        "Capricorn": (14, 86, 86, 14),
    }

    for sign, (x, y) in cell_coords.items():
        cell_items = items_by_sign[sign]
        planets = [it for it in cell_items if it["type"] == "planet"]
        cusps = [it for it in cell_items if it["type"] == "cusp"]
        
        c_dx, c_dy, s_dx, s_dy = quadrant_map[sign]
        
        h_num = (signs_list.index(sign) - anchor_index + 12) % 12 + 1
        # Background hit rect for interactive sign selection and highlighting
        svg += f'<rect class="interactive sign-cell-bg" data-type="sign" data-id="{sign}" data-house="{h_num}" x="{x}" y="{y}" width="100" height="100" fill="transparent" style="cursor: pointer;"><title>House {h_num} ({sign})</title></rect>\n'

        # Draw Rasi Sign (Inner Corner)
        s_sym, s_col, _ = sign_symbols[sign]
        svg += f'<text class="interactive" data-type="sign" data-id="{sign}" x="{x + s_dx}" y="{y + s_dy}" font-size="14" font-family="sans-serif" font-weight="bold" fill="{s_col}" opacity="0.85" text-anchor="middle" dominant-baseline="central" style="cursor: pointer;">{s_sym}</text>\n'

        # If this is anchor sign for non-Lagna root, draw the diagonal badge
        if root_planet != "Lagna" and sign == anchor_sign:
            badge_text = "CL" if root_planet == "Moon" else ("SL" if root_planet == "Sun" else "L")
            svg += f'<line x1="{x}" y1="{y + 26}" x2="{x + 26}" y2="{y}" stroke="#C0392B" stroke-width="2.5" />\n'
            svg += f'<rect x="{x + 2}" y="{y + 2}" width="22" height="14" rx="3" fill="#C0392B"/>\n'
            svg += f'<text x="{x + 13}" y="{y + 9}" font-family="sans-serif" font-size="9" font-weight="bold" fill="#FFFFFF" text-anchor="middle" dominant-baseline="central">{badge_text}</text>\n'

        # Draw House Cusps (Outer Corner)
        if root_planet == "Lagna":
            if cusps:
                num_c = len(cusps)
                for c_idx, c in enumerate(cusps):
                    c_num = c["text"]
                    c_tooltip = f"House Cusp {c_num} in {sign}"
                    
                    if num_c == 1:
                        cx_pos = x + c_dx
                        cy_pos = y + c_dy
                    else:
                        # Spread cusps horizontally so each separate number is independently clickable
                        if c_dx < 50:  # left corner (14, 14) or (14, 86)
                            cx_pos = x + 14 + (c_idx * 16)
                            cy_pos = y + c_dy
                        else:  # right corner (86, 14) or (86, 86)
                            cx_pos = x + 86 - ((num_c - 1 - c_idx) * 16)
                            cy_pos = y + c_dy
                            
                    svg += f'<g class="interactive" data-type="house" data-id="{c_num}" style="cursor: pointer;"><title>{c_tooltip}</title>\n'
                    svg += f'<text x="{cx_pos}" y="{cy_pos}" font-family="sans-serif" font-size="12" font-weight="bold" stroke="#FFFDF9" stroke-width="2.5" paint-order="stroke fill" fill="#7D3C98" text-anchor="middle" dominant-baseline="central">{c_num}</text>\n'
                    svg += '</g>\n'
        else:
            # Whole Sign House number relative to anchor planet
            h_num = (signs_list.index(sign) - anchor_index + 12) % 12 + 1
            h_tooltip = f"House {h_num} from {root_planet} in {sign}"
            is_kendra = h_num in [1, 4, 7, 10]
            col = "#C0392B" if is_kendra else "#7D3C98"
            bx = x + c_dx
            by = y + c_dy
            if sign == anchor_sign and c_dx < 50 and c_dy < 50:
                bx += 16
            svg += f'<g class="interactive" data-type="house" data-id="{h_num}" style="cursor: pointer;"><title>{h_tooltip}</title>\n'
            svg += f'<text x="{bx}" y="{by}" font-family="sans-serif" font-size="12" font-weight="bold" stroke="#FFFDF9" stroke-width="2.5" paint-order="stroke fill" fill="{col}" text-anchor="middle" dominant-baseline="central">H{h_num}</text>\n'
            svg += '</g>\n'

        has_cell_cusps = bool(cusps or root_planet != "Lagna")
        cusp_side = ("top" if c_dy < 50 else "bottom") if has_cell_cusps else None
        positions = get_south_indian_positions(len(planets), x, y, has_cusps=has_cell_cusps, cusp_side=cusp_side)
        
        for idx, p in enumerate(planets):
            if idx >= len(positions):
                break
            px, py = positions[idx]
            info = planet_notations.get(p["name"], {
                "symbol": p["name"][:2],
                "english": p["name"][:2],
                "devanagari": p["name"][:2],
                "translit": p["name"][:2],
                "full_en": p["name"],
                "full_sa": p["name"],
                "color": "#000"
            })
            label = info.get(mode, info["symbol"])
            dev_name = info.get('dev_full', '')
            is_retro = p.get("is_retrograde", False)
            retro_badge = " R" if is_retro else ""
            retro_label = " [Retrograde (R)]" if is_retro else ""
            tooltip = f"{dev_name} / {info['full_sa']} ({info['full_en']}){retro_label} — {p['deg']}{retro_badge} {p['sign']}"
            
            font_sz = "20" if (mode == "symbol" and p["name"] != "Lagna") else ("14" if mode == "devanagari" else "13")
            extra_stroke = ""
            if mode == "symbol" and p["name"] in ["Mars", "Venus"]:
                font_sz = "16"
                extra_stroke = f' stroke="{info["color"]}" stroke-width="0.8" paint-order="stroke fill"'
            
            svg += f'<g class="interactive" data-type="planet" data-id="{p["name"]}" style="cursor: pointer;"><title>{tooltip}</title>\n'
            svg += f'<text x="{px}" y="{py - 2}" font-family="sans-serif" font-size="{font_sz}" font-weight="bold" fill="{info["color"]}"{extra_stroke} text-anchor="middle" dominant-baseline="central">{label}</text>\n'
            svg += f'<text x="{px}" y="{py + 14}" font-family="sans-serif" font-size="10" font-weight="normal" stroke="#FFFDF9" stroke-width="2.0" paint-order="stroke fill" fill="#5C4433" text-anchor="middle" dominant-baseline="central">'
            svg += f'<tspan>{p["deg"]}</tspan>'
            if is_retro:
                svg += f'<tspan font-size="9" font-weight="bold" fill="#C0392B"> R</tspan>'
            svg += '</text>\n'
            svg += '</g>\n'
            
            s_idx = signs_list.index(sign)
            p_deg_val = 0.0
            for orig_it in items:
                if orig_it.get("type") != "cusp" and orig_it.get("name") == p["name"] and orig_it.get("sign") == sign:
                    p_deg_val = orig_it.get("degree", 0) + orig_it.get("minute", 0) / 60.0
                    break
            p_lon = s_idx * 30 + p_deg_val
            planet_coords[p["name"]] = {"x": px, "y": py, "lon": p_lon, "sign": sign}

    # Graha Drishti Aspect Lines & Badges
    dignity_map = {}
    classical_planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    for p_name, p_info in planet_coords.items():
        if p_name in classical_planets:
            p_sign = p_info["sign"]
            sign_lord = SIGN_LORDS.get(p_sign, "Sun")
            if sign_lord == p_name:
                dignity_map[p_name] = "Own Sign"
            else:
                lord_p = planet_coords.get(sign_lord)
                if lord_p:
                    nat = get_natural_relationship(p_name, sign_lord)
                    temp = get_temporary_relationship(signs_list.index(p_sign), signs_list.index(lord_p["sign"]))
                    compound = get_compound_relationship(nat, temp)
                    deg = p_info["lon"] % 30.0
                    dignity_map[p_name] = get_dignity(p_name, p_sign, compound, deg)
                else:
                    dignity_map[p_name] = "Neutral"

    svg += get_aspect_defs_svg()
    svg += render_aspect_lines_group(planet_coords, dignity_map, is_circular=False)

    svg += '</svg>\n'
    return svg

def generate_north_indian(items, mode="symbol", varga_name="D1", root_planet="Lagna"):
    svg = '<svg width="100%" height="100%" viewBox="-10 -10 420 420" class="aspects-hidden" preserveAspectRatio="xMidYMid meet" xmlns="http://www.w3.org/2000/svg" style="background:transparent;">\n'
    planet_coords = {}
    svg += '<rect x="0" y="0" width="400" height="400" fill="none" stroke="#5C4433" stroke-width="2"/>\n'
    svg += '<line x1="0" y1="0" x2="400" y2="400" stroke="#5C4433" stroke-width="2"/>\n'
    svg += '<line x1="400" y1="0" x2="0" y2="400" stroke="#5C4433" stroke-width="2"/>\n'
    svg += '<line x1="200" y1="0" x2="400" y2="200" stroke="#5C4433" stroke-width="2"/>\n'
    svg += '<line x1="400" y1="200" x2="200" y2="400" stroke="#5C4433" stroke-width="2"/>\n'
    svg += '<line x1="200" y1="400" x2="0" y2="200" stroke="#5C4433" stroke-width="2"/>\n'
    svg += '<line x1="0" y1="200" x2="200" y2="0" stroke="#5C4433" stroke-width="2"/>\n'

    anchor_item = next((it for it in items if it.get("name") == root_planet), None)
    if not anchor_item:
        anchor_item = next((it for it in items if it.get("name") == "Lagna"), None)
    anchor_sign = anchor_item["sign"] if anchor_item else "Aries"
    anchor_index = signs_list.index(anchor_sign)

    ni_centers = [
        (200, 100), (100, 45),  (48, 100),  (100, 200),
        (48, 300),  (100, 355), (200, 300), (300, 355),
        (352, 300), (300, 200), (352, 100), (300, 45)
    ]
    sign_pos = [
        (200, 175), (145, 25),  (25, 145),  (175, 200),
        (25, 255),  (145, 375), (200, 225), (255, 375),
        (375, 255), (225, 200), (375, 145), (255, 25)
    ]

    # Header label in House 1 if non-Lagna root
    if root_planet != "Lagna":
        badge_title = "Chandra Lagna" if root_planet == "Moon" else ("Surya Lagna" if root_planet == "Sun" else root_planet)
        svg += f'<text x="200" y="24" font-family="sans-serif" font-size="11" font-weight="bold" fill="#C0392B" text-anchor="middle">{badge_title}</text>\n'

    items_by_house = [[] for _ in range(12)]
    
    for item in items:
        s_idx = signs_list.index(item["sign"])
        h_idx = (s_idx - anchor_index + 12) % 12
        if item.get("type") == "cusp":
            if root_planet == "Lagna":
                items_by_house[h_idx].append(item)
        else:
            items_by_house[h_idx].append({
                "type": "planet",
                "name": item["name"],
                "sign": item["sign"],
                "deg": f"{item['degree']}°{item['minute']:02d}'",
                "is_retrograde": item.get("is_retrograde", False)
            })

    ni_polys = [
        "200,0 100,100 200,200 300,100",  # H1 (top diamond)
        "0,0 200,0 100,100",              # H2 (top left triangle)
        "0,0 100,100 0,200",              # H3 (left top triangle)
        "0,200 100,100 200,200 100,300",  # H4 (left diamond)
        "0,200 100,300 0,400",            # H5 (left bottom triangle)
        "0,400 100,300 200,400",          # H6 (bottom left triangle)
        "200,200 100,300 200,400 300,300",# H7 (bottom diamond)
        "200,400 300,300 400,400",        # H8 (bottom right triangle)
        "400,400 300,300 400,200",        # H9 (right bottom triangle)
        "200,200 300,100 400,200 300,300",# H10 (right diamond)
        "400,200 300,100 400,0",          # H11 (right top triangle)
        "400,0 300,100 200,0"             # H12 (top right triangle)
    ]

    for h in range(12):
        s_idx = (anchor_index + h) % 12
        sign = signs_list[s_idx]
        s_sym, s_col, _ = sign_symbols[sign]
        
        # Background hit polygon for interactive sign selection and highlighting
        svg += f'<polygon class="interactive sign-cell-bg" data-type="sign" data-id="{sign}" data-house="{h + 1}" points="{ni_polys[h]}" fill="transparent" style="cursor: pointer;"><title>House {h + 1} ({sign})</title></polygon>\n'

        sx, sy = sign_pos[h]
        svg += f'<text class="interactive" data-type="sign" data-id="{sign}" x="{sx}" y="{sy}" font-size="14" font-family="sans-serif" fill="{s_col}" opacity="0.85" font-weight="bold" text-anchor="middle" dominant-baseline="central" style="cursor: pointer;">{s_sym}</text>\n'

        cx, cy = ni_centers[h]
        house_items = items_by_house[h]
        planets = [it for it in house_items if it["type"] == "planet"]
        cusps = [it for it in house_items if it["type"] == "cusp"]
        
        positions = get_north_indian_positions(len(planets), cx, cy, has_cusps=bool(cusps))
        
        for idx, p in enumerate(planets):
            if idx >= len(positions):
                break
            px, py = positions[idx]
            info = planet_notations.get(p["name"], {
                "symbol": p["name"][:2],
                "english": p["name"][:2],
                "devanagari": p["name"][:2],
                "translit": p["name"][:2],
                "full_en": p["name"],
                "full_sa": p["name"],
                "color": "#000"
            })
            label = info.get(mode, info["symbol"])
            if len(planets) > 4:
                font_sz = "16" if (mode == "symbol" and p["name"] != "Lagna") else ("12" if mode == "devanagari" else "11")
                deg_sz = "9"
                retro_sz = "8"
            else:
                font_sz = "20" if (mode == "symbol" and p["name"] != "Lagna") else ("14" if mode == "devanagari" else "13")
                deg_sz = "10"
                retro_sz = "9"
            
            extra_stroke = ""
            if mode == "symbol" and p["name"] in ["Mars", "Venus"]:
                font_sz = "16"
                extra_stroke = f' stroke="{info["color"]}" stroke-width="0.8" paint-order="stroke fill"'
                
            dev_name = info.get('dev_full', '')
            is_retro = p.get("is_retrograde", False)
            retro_badge = " R" if is_retro else ""
            retro_label = " [Retrograde (R)]" if is_retro else ""
            tooltip = f"{dev_name} / {info['full_sa']} ({info['full_en']}){retro_label} — {p['deg']}{retro_badge} {p['sign']}"
            
            svg += f'<g class="interactive" data-type="planet" data-id="{p["name"]}" style="cursor: pointer;"><title>{tooltip}</title>\n'
            svg += f'<text x="{px}" y="{py - 2}" text-anchor="middle" dominant-baseline="central" font-family="sans-serif" font-size="{font_sz}" font-weight="bold" stroke="#FFFDF9" stroke-width="2.0" paint-order="stroke fill" fill="{info["color"]}"{extra_stroke}>{label}</text>\n'
            svg += f'<text x="{px}" y="{py + 14}" text-anchor="middle" dominant-baseline="central" font-family="sans-serif" font-size="{deg_sz}" font-weight="normal" stroke="#FFFDF9" stroke-width="2.0" paint-order="stroke fill" fill="#5C4433">'
            svg += f'<tspan>{p["deg"]}</tspan>'
            if is_retro:
                svg += f'<tspan font-size="{retro_sz}" font-weight="bold" fill="#C0392B"> R</tspan>'
            svg += '</text></g>\n'
            
            s_idx = signs_list.index(p["sign"])
            p_deg_val = 0.0
            for orig_it in items:
                if orig_it.get("type") != "cusp" and orig_it.get("name") == p["name"] and orig_it.get("sign") == p["sign"]:
                    p_deg_val = orig_it.get("degree", 0) + orig_it.get("minute", 0) / 60.0
                    break
            p_lon = s_idx * 30 + p_deg_val
            planet_coords[p["name"]] = {"x": px, "y": py, "lon": p_lon, "sign": p["sign"]}

        if cusps:
            if not planets:
                cusp_y = cy
            elif len(planets) <= 2:
                cusp_y = cy + 24
            else:
                cusp_y = cy + 34
            num_c = len(cusps)
            spacing = 16
            start_x = cx - ((num_c - 1) * spacing) / 2
            for c_idx, c in enumerate(cusps):
                c_num = c["text"]
                c_x = start_x + (c_idx * spacing)
                c_tooltip = f"House Cusp {c_num} in {sign}"
                svg += f'<g class="interactive" data-type="house" data-id="{c_num}" style="cursor: pointer;"><title>{c_tooltip}</title>\n'
                svg += f'<text x="{c_x}" y="{cusp_y}" font-family="sans-serif" font-size="12" font-weight="bold" stroke="#FFFDF9" stroke-width="2.5" paint-order="stroke fill" fill="#7D3C98" text-anchor="middle" dominant-baseline="central">{c_num}</text>\n'
                svg += '</g>\n'

    # Graha Drishti Aspect Lines & Badges
    dignity_map = {}
    classical_planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    for p_name, p_info in planet_coords.items():
        if p_name in classical_planets:
            p_sign = p_info["sign"]
            sign_lord = SIGN_LORDS.get(p_sign, "Sun")
            if sign_lord == p_name:
                dignity_map[p_name] = "Own Sign"
            else:
                lord_p = planet_coords.get(sign_lord)
                if lord_p:
                    nat = get_natural_relationship(p_name, sign_lord)
                    temp = get_temporary_relationship(signs_list.index(p_sign), signs_list.index(lord_p["sign"]))
                    compound = get_compound_relationship(nat, temp)
                    deg = p_info["lon"] % 30.0
                    dignity_map[p_name] = get_dignity(p_name, p_sign, compound, deg)
                else:
                    dignity_map[p_name] = "Neutral"

    svg += get_aspect_defs_svg()
    svg += render_aspect_lines_group(planet_coords, dignity_map, is_circular=False)

    svg += '</svg>\n'
    return svg

def generate_bhava_chalita_north(bhavas, mode="symbol"):
    svg = '<svg width="100%" height="100%" viewBox="-10 -10 420 420" preserveAspectRatio="xMidYMid meet" xmlns="http://www.w3.org/2000/svg" style="background:transparent;">\n'
    svg += '<rect x="0" y="0" width="400" height="400" fill="none" stroke="#5C4433" stroke-width="2"/>\n'
    svg += '<line x1="0" y1="0" x2="400" y2="400" stroke="#5C4433" stroke-width="2"/>\n'
    svg += '<line x1="400" y1="0" x2="0" y2="400" stroke="#5C4433" stroke-width="2"/>\n'
    svg += '<line x1="200" y1="0" x2="400" y2="200" stroke="#5C4433" stroke-width="2"/>\n'
    svg += '<line x1="400" y1="200" x2="200" y2="400" stroke="#5C4433" stroke-width="2"/>\n'
    svg += '<line x1="200" y1="400" x2="0" y2="200" stroke="#5C4433" stroke-width="2"/>\n'
    svg += '<line x1="0" y1="200" x2="200" y2="0" stroke="#5C4433" stroke-width="2"/>\n'
    
    ni_centers = [
        (200, 100), (100, 45),  (48, 100),  (100, 200),
        (48, 300),  (100, 355), (200, 300), (300, 355),
        (352, 300), (300, 200), (352, 100), (300, 45)
    ]
    
    sign_pos = [
        (200, 175), (145, 25),  (25, 145),  (175, 200),
        (25, 255),  (145, 375), (200, 225), (255, 375),
        (375, 255), (225, 200), (375, 145), (255, 25)
    ]
    
    ni_polys = [
        "200,0 100,100 200,200 300,100",  # H1 (top diamond)
        "0,0 200,0 100,100",              # H2 (top left triangle)
        "0,0 100,100 0,200",              # H3 (left top triangle)
        "0,200 100,100 200,200 100,300",  # H4 (left diamond)
        "0,200 100,300 0,400",            # H5 (left bottom triangle)
        "0,400 100,300 200,400",          # H6 (bottom left triangle)
        "200,200 100,300 200,400 300,300",# H7 (bottom diamond)
        "200,400 300,300 400,400",        # H8 (bottom right triangle)
        "400,400 300,300 400,200",        # H9 (right bottom triangle)
        "200,200 300,100 400,200 300,300",# H10 (right diamond)
        "400,200 300,100 400,0",          # H11 (right top triangle)
        "400,0 300,100 200,0"             # H12 (top right triangle)
    ]
    
    for h_idx in range(12):
        cx, cy = ni_centers[h_idx]
        bhava = bhavas[h_idx]
        
        cusp_lon = bhava["cusp"]
        sign_idx = int(cusp_lon // 30)
        s_sym, s_col, _ = sign_symbols[signs_list[sign_idx]]
        
        svg += f'<polygon class="interactive sign-cell-bg" data-type="sign" data-id="{signs_list[sign_idx]}" data-house="{h_idx + 1}" points="{ni_polys[h_idx]}" fill="transparent" style="cursor: pointer;"><title>House {h_idx + 1} ({signs_list[sign_idx]})</title></polygon>\n'
        
        sx, sy = sign_pos[h_idx]
        svg += f'<text class="interactive" data-type="sign" data-id="{signs_list[sign_idx]}" x="{sx}" y="{sy}" font-size="14" font-family="sans-serif" fill="{s_col}" opacity="0.85" font-weight="bold" text-anchor="middle" dominant-baseline="central" style="cursor: pointer;">{s_sym}</text>\n'

        items_in_house = bhava["planets"]
        
        item_height = 21
        total_h = len(items_in_house) * item_height
        start_y = cy - (total_h / 2) + (item_height / 2)
        
        curr_y = start_y
        for p_name in items_in_house:
            info = planet_notations.get(p_name, {
                "symbol": p_name[:2],
                "english": p_name[:2],
                "devanagari": p_name[:2],
                "translit": p_name[:2],
                "full_en": p_name,
                "full_sa": p_name,
                "color": "#000"
            })
            label = info.get(mode, info["symbol"])
            font_sz = "24" if (mode == "symbol" and p_name != "Lagna") else ("16" if mode == "devanagari" else "14")
            tooltip = f"{info['full_sa']} ({info['full_en']})"
            
            svg += f'<g class="interactive" data-type="planet" data-id="{p_name}" style="cursor: pointer;"><title>{tooltip}</title>\n'
            svg += f'<text x="{cx}" y="{curr_y}" text-anchor="middle" dominant-baseline="central" font-family="sans-serif">\n'
            svg += f'  <tspan font-size="{font_sz}" font-weight="bold" fill="{info["color"]}">{label}</tspan>\n'
            svg += f'</text></g>\n'
            curr_y += item_height

    svg += "</svg>\n"
    return svg


import math

from jyotish.aspects.aspects import get_graha_drishti
from jyotish.relationships.relationships import (
    get_dignity, get_compound_relationship, get_natural_relationship, 
    get_temporary_relationship, SIGN_LORDS
)

def relax_planet_angles(planets, has_ascendant_barrier=True, is_outer=False):
    """
    Relaxes planet draw angles around a 360-degree circle to eliminate overlaps
    while strictly preserving their monotonic angular order (planets never swap relative order).
    """
    if not planets or len(planets) <= 1:
        return

    # Pre-offset Lagna away from red arrow at 180° if needed
    for p in planets:
        if p.get("is_lagna") and abs((p["draw_angle"] % 360) - 180.0) < 8.0:
            p["draw_angle"] = 188.0

    # Sort strictly by true_angle once to lock in the true astronomical cyclic order
    planets.sort(key=lambda p: (p["true_angle"] % 360))
    n = len(planets)

    # Unwrap angles into continuous 1D monotonic space
    unwrapped = [planets[0]["true_angle"] % 360]
    for i in range(1, n):
        diff = (planets[i]["true_angle"] - unwrapped[-1]) % 360
        unwrapped.append(unwrapped[-1] + diff)

    pos = list(unwrapped)
    orig = list(unwrapped)

    for _ in range(80):
        # Enforce minimum separation between adjacent planets cyclically
        for i in range(n):
            next_i = (i + 1) % n
            p1 = planets[i]
            p2 = planets[next_i]
            is_wide1 = p1.get("is_lagna", False) or p1["item"].get("is_retrograde", False)
            is_wide2 = p2.get("is_lagna", False) or p2["item"].get("is_retrograde", False)
            if p1.get("is_lagna", False) or p2.get("is_lagna", False):
                min_sep = 11.5
            elif is_wide1 or is_wide2:
                min_sep = 8.6 if is_outer else 8.2
            else:
                min_sep = 7.2 if is_outer else 6.8

            d = (pos[next_i] - pos[i]) if next_i > i else (pos[0] + 360.0 - pos[i])
            if d < min_sep:
                push = (min_sep - d) * 0.5
                pos[i] -= push
                if next_i > i:
                    pos[next_i] += push
                else:
                    pos[0] += push
                    for k in range(1, n):
                        pos[k] += push

        # Restoring spring towards true angle to prevent artificial house drift
        for i in range(n):
            pos[i] += (orig[i] - pos[i]) * 0.08

        # Ascendant barrier zone [172.5, 187.5]
        if has_ascendant_barrier:
            for i in range(n):
                ang = pos[i] % 360
                if 172.5 <= ang < 180.0:
                    pos[i] -= (ang - 172.0)
                elif 180.0 <= ang < 187.5:
                    pos[i] += (188.0 - ang)

    for i in range(n):
        planets[i]["draw_angle"] = pos[i] % 360

def generate_circular_chart(items, mode="symbol", varga_name="D1", ayanamsha=0, root_planet="Lagna"):
    svg = '<svg width="100%" height="100%" viewBox="-210 -210 420 420" class="aspects-hidden" preserveAspectRatio="xMidYMid meet" xmlns="http://www.w3.org/2000/svg" style="background:transparent; font-family: sans-serif;">\n'
    
    # SVG Defs for Aspect Arrowheads (Benefic/Exalted/Malefic/Neutral)
    svg += '<defs>\n'
    svg += '  <style>\n'
    svg += '    .aspects-hidden:not(.aspects-filtered) .aspect-lines { display: none; }\n'
    svg += '  </style>\n'
    svg += '  <marker id="arrow-benefic" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#27AE60"/></marker>\n'
    svg += '  <marker id="arrow-exalted" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#D4AC0D"/></marker>\n'
    svg += '  <marker id="arrow-malefic" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#C0392B"/></marker>\n'
    svg += '  <marker id="arrow-neutral" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#2980B9"/></marker>\n'
    svg += '</defs>\n'
    
    r_nak_outer = 200
    r_nak_inner = 175
    r_rasi_inner = 155
    r_bhava_outer = 92
    r_bhava_inner = 76
    
    root_title = "Chandra Lagna" if root_planet == "Moon" else ("Surya Lagna" if root_planet == "Sun" else "Circular Chart")
    svg += f'<title>{varga_name} {root_title}</title>\n'
    
    # Outer house circuits
    circle_stroke = "0.7"
    svg += f'<circle cx="0" cy="0" r="{r_nak_outer}" fill="none" stroke="#5C4433" stroke-width="{circle_stroke}"/>\n'
    svg += f'<circle cx="0" cy="0" r="{r_nak_inner}" fill="none" stroke="#5C4433" stroke-width="{circle_stroke}"/>\n'
    svg += f'<circle cx="0" cy="0" r="{r_rasi_inner}" fill="none" stroke="#5C4433" stroke-width="{circle_stroke}"/>\n'
    svg += f'<circle cx="0" cy="0" r="{r_bhava_outer}" fill="none" stroke="#27AE60" stroke-width="{circle_stroke}"/>\n'
    # Inner aspect boundary circle
    svg += f'<circle class="interactive-center-circle" cx="0" cy="0" r="{r_bhava_inner}" fill="#faf7f0" fill-opacity="0.55" stroke="#5C4433" stroke-width="0.8" style="cursor: pointer;"><title>Click to toggle aspects or clear filter</title></circle>\n'
    
    anchor_item = next((it for it in items if it.get("name") == root_planet), None)
    if not anchor_item:
        anchor_item = next((it for it in items if it.get("name") == "Lagna"), None)
    if anchor_item:
        anchor_s_idx = signs_list.index(anchor_item["sign"])
        anchor_lon = anchor_s_idx * 30 + anchor_item["degree"] + anchor_item["minute"] / 60.0
    else:
        anchor_s_idx = 0
        anchor_lon = 0
            
    def lon_to_angle(lon):
        return 180 + anchor_lon - lon

    def polar_coords(r, angle_deg):
        rad = math.radians(angle_deg)
        return r * math.cos(rad), r * math.sin(rad)

    # 1. Nakshatras
    nak_names = ["Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", 
                 "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni", 
                 "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha", 
                 "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha", 
                 "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"]
                 
    for i in range(27):
        start_lon = ayanamsha + i * (360.0 / 27.0)
        angle_start = lon_to_angle(start_lon)
        angle_mid = lon_to_angle(start_lon + (360.0 / 54.0))
        
        x1, y1 = polar_coords(r_nak_inner, angle_start)
        x2, y2 = polar_coords(r_nak_outer, angle_start)
        svg += f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#5C4433" stroke-width="0.5" stroke-dasharray="2,2"/>\n'
        
        lx, ly = polar_coords( (r_nak_inner + r_nak_outer)/2, angle_mid)
        rot = angle_mid if (angle_mid % 360) > 90 and (angle_mid % 360) < 270 else angle_mid + 180
        svg += f'<text class="interactive" data-type="nakshatra" data-id="{nak_names[i]}" x="{lx}" y="{ly}" font-size="7" fill="#5C4433" text-anchor="middle" dominant-baseline="central" transform="rotate({rot} {lx} {ly})" style="cursor: pointer;">{nak_names[i][:4]}.</text>\n'

    # 2 & 3. Tropical Rasis and Bhavas (Whole Signs)
    for i in range(12):
        start_lon = i * 30.0
        angle_start = lon_to_angle(start_lon)
        angle_mid = lon_to_angle(start_lon + 15.0)
        
        # Draw Rasi separator line
        x1, y1 = polar_coords(r_rasi_inner, angle_start)
        x2, y2 = polar_coords(r_nak_inner, angle_start)
        svg += f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#5C4433" stroke-width="1"/>\n'
        
        # Whole House boundaries (Bhavas) - Green dense dashed line
        x3, y3 = polar_coords(r_bhava_outer, angle_start)
        x4, y4 = polar_coords(r_rasi_inner, angle_start)
        svg += f'<line x1="{x3}" y1="{y3}" x2="{x4}" y2="{y4}" stroke="#27AE60" stroke-width="0.8" stroke-dasharray="3,2"/>\n'
        
        # Bhava inner circle separator
        x5, y5 = polar_coords(r_bhava_inner, angle_start)
        x6, y6 = polar_coords(r_bhava_outer, angle_start)
        svg += f'<line x1="{x5}" y1="{y5}" x2="{x6}" y2="{y6}" stroke="#000000" stroke-width="0.8"/>\n'
        
        # Rasi symbol label
        lx, ly = polar_coords( (r_rasi_inner + r_nak_inner)/2, angle_mid)
        sign_name = signs_list[i]
        s_sym, s_col, _ = sign_symbols[sign_name]
        svg += f'<text class="interactive" data-type="sign" data-id="{sign_name}" x="{lx}" y="{ly}" font-size="14" fill="{s_col}" text-anchor="middle" dominant-baseline="central" style="cursor: pointer;">{s_sym}</text>\n'

        # Bhava number label (Whole Sign) in the middle of the bhava ring
        bhava_num = (i - anchor_s_idx + 12) % 12 + 1
        bx, by = polar_coords( (r_bhava_inner + r_bhava_outer)/2, angle_mid)
        svg += f'<text class="interactive" data-type="house" data-id="{bhava_num}" x="{bx}" y="{by}" font-size="9.5" font-weight="600" fill="#2980B9" text-anchor="middle" dominant-baseline="central" style="cursor: pointer;">{bhava_num}</text>\n'

    # 4. House Cusps (Campanus lines in D1, only for physical Lagna root)
    cusps = [it for it in items if it.get("type") == "cusp"]
    
    # Always draw Ascendant red arrow at 180 degrees
    ax1, ay1 = polar_coords(r_bhava_outer, 180)
    ax2, ay2 = polar_coords(r_rasi_inner, 180)
    svg += f'<line x1="{ax1}" y1="{ay1}" x2="{ax2}" y2="{ay2}" stroke="#C0392B" stroke-width="1.5" />\n'
    tx1, ty1 = polar_coords(r_rasi_inner - 6, 178)
    tx2, ty2 = polar_coords(r_rasi_inner - 6, 182)
    svg += f'<polygon points="{ax2},{ay2} {tx1},{ty1} {tx2},{ty2}" fill="#C0392B" />\n'

    # In D1, draw lines ONLY for the 4 cardinal angle stations (1: Asc, 4: IC, 7: Dsc, 10: MC) for Lagna root
    if root_planet == "Lagna" and varga_name == "D1" and cusps and len(cusps) >= 12:
        for i in range(12):
            c = cusps[i]
            house_num = i + 1
            if house_num not in [4, 7, 10]:
                continue
                
            lon = c.get("longitude")
            if lon is None:
                s_idx = signs_list.index(c["sign"])
                lon = s_idx * 30 + c["degree"] + c["minute"] / 60.0
                
            angle_start = lon_to_angle(lon)
            x1, y1 = polar_coords(r_bhava_outer, angle_start)
            x2, y2 = polar_coords(r_rasi_inner, angle_start)
            svg += f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#C0392B" stroke-width="1.0"/>\n'

    # Draw cusp numbers clearly positioned within each sign sector for Lagna root
    if root_planet == "Lagna" and cusps:
        cusps_by_sign = {s: [] for s in signs_list}
        for c in cusps:
            if c.get("sign") in cusps_by_sign:
                cusps_by_sign[c["sign"]].append(c)

        for i in range(12):
            sign_name = signs_list[i]
            sign_cusps = cusps_by_sign[sign_name]
            if not sign_cusps:
                continue
            
            # Sort cusps by house number
            sign_cusps.sort(key=lambda c: int(c.get("text", 0)))
            
            start_lon = i * 30.0
            angle_mid = lon_to_angle(start_lon + 15.0)
            
            count = len(sign_cusps)
            spacing = 0 if count == 1 else min(24.0 / (count - 1), 9.0)
            start_offset = 0 if count == 1 else -(count - 1) * spacing / 2.0
            
            for idx, c in enumerate(sign_cusps):
                house_num = int(c.get("text", 0))
                cusp_angle = angle_mid + start_offset + idx * spacing
                cx, cy = polar_coords(r_bhava_outer + 8, cusp_angle)
                
                is_angle = house_num in [1, 4, 7, 10]
                color = "#C0392B" if is_angle else "#7D3C98"
                fw = "bold" if is_angle else "600"
                fs = "11" if is_angle else "9.5"
                
                tooltip = f"House Cusp {house_num} in {sign_name}"
                svg += f'<text class="interactive" data-type="house" data-id="{house_num}" x="{cx}" y="{cy}" font-size="{fs}" font-weight="{fw}" stroke="#FAF7F0" stroke-width="2.5" paint-order="stroke fill" fill="{color}" text-anchor="middle" dominant-baseline="central" style="cursor: pointer;"><title>{tooltip}</title>{house_num}</text>\n'

    # 5. Planets & Dignity Calculation
    planets_to_draw = []
    planets_dict = {}
    classical_planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    dignity_map = {}
    
    for item in items:
        if item.get("type") == "planet":
            p_name = item["name"]
            s_idx = signs_list.index(item["sign"])
            pl_lon = s_idx * 30 + item["degree"] + item["minute"] / 60.0
            p_data = {
                "item": item, 
                "lon": pl_lon, 
                "draw_angle": lon_to_angle(pl_lon), 
                "true_angle": lon_to_angle(pl_lon),
                "is_lagna": (p_name == root_planet),
                "sign_idx": s_idx
            }
            planets_to_draw.append(p_data)
            planets_dict[p_name] = p_data

    # Calculate 5-fold dignity for classical planets
    for p_name, p_info in planets_dict.items():
        if p_name in classical_planets:
            sign = p_info["item"]["sign"]
            sign_lord = SIGN_LORDS.get(sign, "Sun")
            if sign_lord == p_name:
                dignity_map[p_name] = "Own Sign"
            else:
                lord_p = planets_dict.get(sign_lord)
                if lord_p:
                    nat = get_natural_relationship(p_name, sign_lord)
                    temp = get_temporary_relationship(p_info["sign_idx"], lord_p["sign_idx"])
                    compound = get_compound_relationship(nat, temp)
                    deg = p_info["item"]["degree"] + p_info["item"]["minute"] / 60.0
                    dignity_map[p_name] = get_dignity(p_name, sign, compound, deg)
                else:
                    dignity_map[p_name] = "Neutral"

    # Relaxation for overlap with strictly preserved cyclic order
    relax_planet_angles(planets_to_draw, has_ascendant_barrier=True, is_outer=False)

    # 6. Graha Drishti (Planetary Aspect Chords with Directional Dignity Arrows & Degree Badges)
    circular_coords = {}
    for p_data in planets_to_draw:
        p_name = p_data["item"]["name"]
        circular_coords[p_name] = {
            "lon": p_data["lon"],
            "true_angle": p_data["true_angle"],
            "sign": p_data["item"]["sign"]
        }
    svg += get_aspect_defs_svg()
    svg += render_aspect_lines_group(circular_coords, dignity_map, is_circular=True, r_inner=r_bhava_inner)

    # 7. Planets (radially stacked, without redundant sign symbol)
    r_pl_base = r_rasi_inner - 9 # 146

    for p in planets_to_draw:
        item = p["item"]
        angle = p["draw_angle"]
        p_name = item["name"]
        info = planet_notations.get(p_name, {})
        label = info.get(mode, info.get("symbol", p_name[:2]))
        color = info.get("color", "#000")
        
        is_retro = item.get("is_retrograde", False)
        retro_badge = "R" if is_retro else ""
        
        px, py = polar_coords(r_pl_base, angle)

        font_sz = 10 if p_name == "Lagna" else (13.5 if mode == "devanagari" else 13)
        if mode == "symbol" and p_name in ["Mars", "Venus"]:
            font_sz = "10.5"
        
        dignity_str = dignity_map.get(p_name, "")
        dignity_tag = f" [{dignity_str}]" if dignity_str else ""
        tooltip = f"{info.get('full_sa', p_name)}{dignity_tag} — {item['degree']}° {item['minute']:02d}'{retro_badge} in {item['sign']}"
        svg += f'<g class="interactive planet-glyph" data-type="planet" data-id="{p_name}" style="cursor: pointer;"><title>{tooltip}</title>\n'

        r_deg_base = r_rasi_inner - 21
        r_min_base = r_rasi_inner - 32
        
        # 1. Minute text
        mx, my = polar_coords(r_min_base, angle)
        svg += f'<text x="{mx}" y="{my}" font-size="6.0" stroke="#F7F3EB" stroke-width="1.0" paint-order="stroke" stroke-linejoin="round" fill="{color}" text-anchor="middle" dominant-baseline="central">{item["minute"]:02d}\'{" R" if is_retro else ""}</text>\n'

        # 2. Degree text
        dx, dy = polar_coords(r_deg_base, angle)
        svg += f'<text x="{dx}" y="{dy}" font-size="7.0" stroke="#F7F3EB" stroke-width="1.2" paint-order="stroke" stroke-linejoin="round" fill="{color}" text-anchor="middle" dominant-baseline="central">{item["degree"]}°</text>\n'

        # 3. Planet Glyph (Drawn on top with protective halo)
        svg += f'<text class="glyph-symbol" x="{px}" y="{py}" font-size="{font_sz}" stroke="#F7F3EB" stroke-width="2.2" paint-order="stroke" stroke-linejoin="round" fill="{color}" font-weight="bold" text-anchor="middle" dominant-baseline="central">{label}</text>\n'
        
        svg += f'</g>\n'
        
        true_angle = lon_to_angle(p["lon"])
        if abs((angle - true_angle) % 360) > 0.5 and abs((angle - true_angle) % 360) < 359.5:
            cx, cy = polar_coords(r_rasi_inner, true_angle)
            svg += f'<line x1="{px}" y1="{py}" x2="{cx}" y2="{cy}" stroke="{color}" stroke-width="0.5" opacity="0.35"/>\n'

    svg += '</svg>\n'
    return svg


def generate_biwheel_chart(inner_items, outer_items, inner_name="D1", outer_name="D9", mode="symbol", ayanamsha=0, root_planet="Lagna"):
    """
    Generates a concentric dual-wheel Harmonic Bi-Wheel SVG chart (Vic DiCara / Ernst Wilhelm style).
    - Inner Ring (Radius ~62 to ~138): Natal Chart (D1 / Rashi).
      * Native signs (♈︎ - ♓︎) placed prominently inside the 30° sectors at r=125.
      * Campanus house cusps, whole sign bhava numbers (1 to 12) at r=72.
      * Natal planets (glyph at r=108, degree at r=95, minute at r=85).
    - Harmonic Subdivision Ring (Radius ~138 to ~164):
      * Sits between physical reality (D1) and divisional harmonic reality (outer Varga).
      * Subdivides each 30° sign into N harmonic divisions (e.g., 9 for D9, 10 for D10, 7 for D7).
      * Displays the divisional sign glyph in each harmonic slice (e.g. Cap, Aqu, Pis... for Virgo in D9).
      * 30° boundary marks and '30°' label at each sign junction.
    - Outer Ring (Radius ~164 to ~206):
      * Harmonic planets anchored radially to their natal longitude.
      * Displays: (a) base tick in subdivision ring, (b) minute at r=173, (c) degree at r=181,
        (d) planet glyph at r=191, (e) divisional sign glyph at r=200.
    - Center Circle (Radius 0 to ~62):
      * Graha Drishti aspect chords including cross-chart harmonic aspects.
      * Center toggle button.
    - Vargottama Highlight:
      * Radiant golden beam connecting inner and outer planet directly through the matching subdivision slice,
        with dual golden halos.
    """
    from jyotish.generate_jyotish import calculate_varga_longitude

    svg = '<svg width="100%" height="100%" viewBox="-210 -210 420 420" class="aspects-hidden" preserveAspectRatio="xMidYMid meet" xmlns="http://www.w3.org/2000/svg" style="background:transparent; font-family: sans-serif;">\n'
    
    # SVG Defs for Aspect Arrowheads & Golden Vargottama Glow
    svg += '<defs>\n'
    svg += '  <style>\n'
    svg += '    .aspects-hidden:not(.aspects-filtered) .aspect-lines { display: none; }\n'
    svg += '  </style>\n'
    svg += '  <marker id="arrow-benefic" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#27AE60"/></marker>\n'
    svg += '  <marker id="arrow-exalted" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#D4AC0D"/></marker>\n'
    svg += '  <marker id="arrow-malefic" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#C0392B"/></marker>\n'
    svg += '  <marker id="arrow-neutral" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#2980B9"/></marker>\n'
    svg += '  <marker id="arrow-cross" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M 0 2 L 7 5 L 0 8 z" fill="#8E44AD"/></marker>\n'
    svg += '  <marker id="arrow-pointer-in" viewBox="0 0 8 8" refX="6" refY="4" markerWidth="4.5" markerHeight="4.5" orient="auto"><path d="M 0 1.5 L 7 4 L 0 6.5 z" fill="#5C4433"/></marker>\n'
    svg += '  <marker id="arrow-pointer-out" viewBox="0 0 8 8" refX="6" refY="4" markerWidth="4.5" markerHeight="4.5" orient="auto"><path d="M 0 1.5 L 7 4 L 0 6.5 z" fill="#5C4433"/></marker>\n'
    svg += '  <filter id="gold-halo" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="1.5" result="blur"/><feComposite in="SourceGraphic" in2="blur" operator="over"/></filter>\n'
    svg += '</defs>\n'
    
    r_chart_outer = 206
    r_divider_outer = 164
    r_divider_inner = 138
    r_bhava_circle = 80
    r_aspect_inner = 62
    
    root_title = "Chandra Lagna" if root_planet == "Moon" else ("Surya Lagna" if root_planet == "Sun" else "Ascendant")
    svg += f'<title>{inner_name} / {outer_name} Harmonic Bi-Wheel ({root_title})</title>\n'
    
    # Outer bounding circle & tinted background for outer harmonic planet ring
    svg += f'<circle cx="0" cy="0" r="{r_chart_outer}" fill="#faf7f2" fill-opacity="0.25" stroke="#5C4433" stroke-width="1.0"/>\n'
    
    # Harmonic subdivision ring background band & concentric borders
    svg += f'<circle cx="0" cy="0" r="{r_divider_outer}" fill="#edece6" fill-opacity="0.65" stroke="#8c7b64" stroke-width="1.2"/>\n'
    svg += f'<circle cx="0" cy="0" r="{r_divider_inner}" fill="#ffffff" fill-opacity="0.95" stroke="#8c7b64" stroke-width="1.2"/>\n'
    
    # Inner D1 Bhava dashed circle
    svg += f'<circle cx="0" cy="0" r="{r_bhava_circle}" fill="none" stroke="#27AE60" stroke-width="0.6" stroke-dasharray="3,2"/>\n'
    
    # Aspect boundary interactive center circle
    svg += f'<circle class="interactive-center-circle" cx="0" cy="0" r="{r_aspect_inner}" fill="#faf7f0" fill-opacity="0.85" stroke="#5C4433" stroke-width="0.8" style="cursor: pointer;"><title>Click to toggle aspects or clear filter</title></circle>\n'
    
    # Center text labels
    svg += f'<text x="0" y="-7" font-size="9.5" font-weight="bold" fill="#4a3325" text-anchor="middle" pointer-events="none">{inner_name} · {outer_name}</text>\n'
    svg += f'<text x="0" y="7" font-size="7.5" font-weight="600" fill="#8c7b64" text-anchor="middle" pointer-events="none">Bi-Wheel</text>\n'
    
    anchor_item = next((it for it in inner_items if it.get("name") == root_planet), None)
    if not anchor_item:
        anchor_item = next((it for it in inner_items if it.get("name") == "Lagna"), None)
    if anchor_item:
        anchor_s_idx = signs_list.index(anchor_item["sign"])
        anchor_lon = anchor_s_idx * 30 + anchor_item["degree"] + anchor_item["minute"] / 60.0
    else:
        anchor_s_idx = 0
        anchor_lon = 0
            
    def lon_to_angle(lon):
        return 180.0 + anchor_lon - lon

    def polar_coords(r, angle_deg):
        rad = math.radians(angle_deg)
        return r * math.cos(rad), r * math.sin(rad)

    # Harmonic number of divisions per 30° sign
    harmonic_map = {
        "D1": 1, "D2": 2, "D3": 3, "D4": 4, "D7": 7, "D9": 9, "D10": 10,
        "D12": 12, "D16": 16, "D20": 20, "D24": 24, "D27": 27, "D30": 30,
        "D40": 40, "D45": 45, "D60": 60
    }
    if outer_name in harmonic_map:
        harmonic_n = harmonic_map[outer_name]
    elif outer_name.startswith("D") and outer_name[1:].isdigit():
        harmonic_n = int(outer_name[1:])
    else:
        harmonic_n = 9

    # 1. Tropical Rasis in Central Border Ring and Harmonic Subdivisions for learning
    for i in range(12):
        sign_start_lon = i * 30.0
        angle_start = lon_to_angle(sign_start_lon)
        angle_mid = lon_to_angle(sign_start_lon + 15.0)
        sign_name = signs_list[i]
        s_sym, s_col, _ = sign_symbols[sign_name]
        
        # Natal sign divider extending inward across inner ring (r_aspect_inner to r_divider_inner)
        x_in1, y_in1 = polar_coords(r_aspect_inner, angle_start)
        x_in2, y_in2 = polar_coords(r_divider_inner, angle_start)
        svg += f'<line x1="{x_in1}" y1="{y_in1}" x2="{x_in2}" y2="{y_in2}" stroke="#d5c8b2" stroke-width="0.8" stroke-dasharray="2,3"/>\n'
        
        # Outer sign divider extending outward across outer comparison ring (r_divider_outer to r_chart_outer)
        x_out1, y_out1 = polar_coords(r_divider_outer, angle_start)
        x_out2, y_out2 = polar_coords(r_chart_outer, angle_start)
        svg += f'<line x1="{x_out1}" y1="{y_out1}" x2="{x_out2}" y2="{y_out2}" stroke="#d5c8b2" stroke-width="0.8" stroke-dasharray="2,3"/>\n'

        # Central Zodiac Sign Symbol inside Border Ring (midpoint between 138 and 164 -> r=148)
        lx_sign, ly_sign = polar_coords(148, angle_mid)
        svg += f'<text class="interactive natal-sign-glyph" data-type="sign" data-id="{sign_name}" x="{lx_sign}" y="{ly_sign}" font-size="14" stroke="#ffffff" stroke-width="2.5" paint-order="stroke fill" fill="{s_col}" text-anchor="middle" dominant-baseline="central" style="cursor: pointer;"><title>{sign_name} (Zodiac Sign)</title>{s_sym}</text>\n'
        
        # Bhava number label (Whole Sign) in the inner bhava ring (radius ~69)
        bhava_num = (i - anchor_s_idx + 12) % 12 + 1
        bx, by = polar_coords(69, angle_mid)
        svg += f'<text class="interactive" data-type="house" data-id="{bhava_num}" x="{bx}" y="{by}" font-size="8.5" font-weight="600" stroke="#FAF7F0" stroke-width="2.0" paint-order="stroke fill" fill="#2980B9" text-anchor="middle" dominant-baseline="central" style="cursor: pointer;">{bhava_num}</text>\n'

        # Sign boundary line across Central Zodiac Border Ring (r_divider_inner to r_divider_outer)
        sx1, sy1 = polar_coords(r_divider_inner, angle_start)
        sx2, sy2 = polar_coords(r_divider_outer, angle_start)
        svg += f'<line x1="{sx1}" y1="{sy1}" x2="{sx2}" y2="{sy2}" stroke="#5C4433" stroke-width="1.3"/>\n'
        
        # Boundary T-bar anchor tick at inner edge (r_divider_inner)
        tx1, ty1 = polar_coords(r_divider_inner, angle_start - 1.2)
        tx2, ty2 = polar_coords(r_divider_inner, angle_start + 1.2)
        svg += f'<line x1="{tx1}" y1="{ty1}" x2="{tx2}" y2="{ty2}" stroke="#5C4433" stroke-width="1.3"/>\n'

        # Boundary T-bar anchor tick at outer edge (r_divider_outer)
        tx3, ty3 = polar_coords(r_divider_outer, angle_start - 1.0)
        tx4, ty4 = polar_coords(r_divider_outer, angle_start + 1.0)
        svg += f'<line x1="{tx3}" y1="{ty3}" x2="{tx4}" y2="{ty4}" stroke="#5C4433" stroke-width="1.3"/>\n'
        
        # 30° Sign Boundary Label in inner white band (just before the division ring)
        ang_30 = angle_start + 2.2
        r_30 = r_divider_inner - 6.5
        if abs((ang_30 - 180.0) % 360) < 3.5:
            r_30 -= 4.5
        lx30, ly30 = polar_coords(r_30, ang_30)
        rot30 = angle_start if (angle_start % 360) > 90 and (angle_start % 360) < 270 else angle_start + 180
        svg += f'<text x="{lx30}" y="{ly30}" font-size="5.5" font-weight="600" fill="#5C4433" text-anchor="middle" dominant-baseline="central" transform="rotate({rot30} {lx30} {ly30})">30°</text>\n'

        # Harmonic Subdivisions within this sign (for learning purposes)
        for k in range(harmonic_n):
            div_start_lon = sign_start_lon + k * (30.0 / harmonic_n)
            div_end_lon = sign_start_lon + (k + 1) * (30.0 / harmonic_n)
            div_mid_lon = (div_start_lon + div_end_lon) / 2.0
            angle_div_start = lon_to_angle(div_start_lon)
            angle_div_mid = lon_to_angle(div_mid_lon)
            
            # Sub-slice divider tick line across the Zodiac border ring
            if k > 0:
                dx1, dy1 = polar_coords(r_divider_inner, angle_div_start)
                dx2, dy2 = polar_coords(r_divider_outer, angle_div_start)
                svg += f'<line class="harmonic-subdivision-tick" x1="{dx1}" y1="{dy1}" x2="{dx2}" y2="{dy2}" stroke="#b8af9f" stroke-width="0.6" stroke-dasharray="2,2"/>\n'
                
            # Divisional sign determination
            div_v_lon = calculate_varga_longitude(div_mid_lon, outer_name)
            sub_s_idx = int(div_v_lon // 30) % 12
            sub_sign_name = signs_list[sub_s_idx]
            sub_sym, sub_col, _ = sign_symbols[sub_sign_name]
            
            # Subtle sub-sign glyph near outer edge of Zodiac border (radius ~159.5) for learning
            if harmonic_n <= 12:
                sub_font_sz = "5.5" if harmonic_n <= 9 else "4.5"
                smx, smy = polar_coords(r_divider_outer - 4.5, angle_div_mid)
                rot_sub = angle_div_mid if (angle_div_mid % 360) > 90 and (angle_div_mid % 360) < 270 else angle_div_mid + 180
                svg += f'<text class="interactive sub-sign-symbol" data-type="varga-division" data-varga="{outer_name}" data-sign="{sub_sign_name}" x="{smx}" y="{smy}" font-size="{sub_font_sz}" fill="{sub_col}" opacity="0.8" text-anchor="middle" dominant-baseline="central" transform="rotate({rot_sub} {smx} {smy})" style="cursor: pointer;"><title>{outer_name} division: {sub_sign_name} ({round(k * 30.0 / harmonic_n, 1)}° - {round((k + 1) * 30.0 / harmonic_n, 1)}° of {sign_name})</title>{sub_sym}</text>\n'

    # 2. House Cusps (Campanus lines in D1, only for physical Lagna root)
    inner_cusps = [it for it in inner_items if it.get("type") == "cusp"]
    
    # Always draw Ascendant red arrow at 180 degrees (inner ring)
    ax1, ay1 = polar_coords(r_aspect_inner, 180)
    ax2, ay2 = polar_coords(r_divider_inner, 180)
    svg += f'<line x1="{ax1}" y1="{ay1}" x2="{ax2}" y2="{ay2}" stroke="#C0392B" stroke-width="1.6" />\n'
    tx1, ty1 = polar_coords(r_divider_inner - 5, 177.5)
    tx2, ty2 = polar_coords(r_divider_inner - 5, 182.5)
    svg += f'<polygon points="{ax2},{ay2} {tx1},{ty1} {tx2},{ty2}" fill="#C0392B" />\n'

    # In D1, draw lines for cardinal angle stations (4: IC, 7: Dsc, 10: MC) for Lagna root
    if root_planet == "Lagna" and inner_cusps and len(inner_cusps) >= 12:
        for i in range(12):
            c = inner_cusps[i]
            house_num = i + 1
            if house_num not in [4, 7, 10]:
                continue
                
            lon = c.get("longitude")
            if lon is None:
                s_idx = signs_list.index(c["sign"])
                lon = s_idx * 30 + c["degree"] + c["minute"] / 60.0
                
            angle_start = lon_to_angle(lon)
            x1, y1 = polar_coords(r_aspect_inner, angle_start)
            x2, y2 = polar_coords(r_divider_inner, angle_start)
            svg += f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#C0392B" stroke-width="1.0"/>\n'

    # 3. Extract and process Planets (Inner Natal + Outer Harmonic)
    inner_planets = []
    inner_planets_dict = {}
    classical_planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    
    for item in inner_items:
        if item.get("type") == "planet":
            p_name = item["name"]
            s_idx = signs_list.index(item["sign"])
            pl_lon = s_idx * 30 + item["degree"] + item["minute"] / 60.0
            p_data = {
                "item": item, 
                "lon": pl_lon, 
                "draw_angle": lon_to_angle(pl_lon), 
                "true_angle": lon_to_angle(pl_lon),
                "is_lagna": (p_name == root_planet),
                "sign_idx": s_idx,
                "sign": item["sign"],
                "varga": inner_name
            }
            inner_planets.append(p_data)
            inner_planets_dict[p_name] = p_data

    outer_planets = []
    outer_planets_dict = {}
    for item in outer_items:
        if item.get("type") == "planet":
            p_name = item["name"]
            s_idx = signs_list.index(item["sign"])
            pl_lon = s_idx * 30 + item["degree"] + item["minute"] / 60.0
            
            # Outer planet is positioned at its ACTUAL divisional longitude
            outer_angle = lon_to_angle(pl_lon)
            natal_p = inner_planets_dict.get(p_name)
            base_lon = natal_p["lon"] if natal_p else pl_lon
            
            p_data = {
                "item": item, 
                "lon": pl_lon, 
                "natal_lon": base_lon, 
                "draw_angle": outer_angle, 
                "true_angle": outer_angle, 
                "is_lagna": (p_name == root_planet),
                "sign_idx": s_idx,
                "sign": item["sign"],
                "varga": outer_name
            }
            outer_planets.append(p_data)
            outer_planets_dict[p_name] = p_data

    # Vargottama Detection: Planet occupies the exact same sign in D1 and outer Varga
    vargottama_planets = set()
    for p_name, out_p in outer_planets_dict.items():
        if p_name in inner_planets_dict:
            in_p = inner_planets_dict[p_name]
            if in_p["sign"] == out_p["sign"]:
                vargottama_planets.add(p_name)

    # 5-fold dignity for inner classical planets
    dignity_map = {}
    for p_name, p_info in inner_planets_dict.items():
        if p_name in classical_planets:
            sign = p_info["item"]["sign"]
            sign_lord = SIGN_LORDS.get(sign, "Sun")
            if sign_lord == p_name:
                dignity_map[p_name] = "Own Sign"
            else:
                lord_p = inner_planets_dict.get(sign_lord)
                if lord_p:
                    nat = get_natural_relationship(p_name, sign_lord)
                    temp = get_temporary_relationship(p_info["sign_idx"], lord_p["sign_idx"])
                    compound = get_compound_relationship(nat, temp)
                    deg = p_info["item"]["degree"] + p_info["item"]["minute"] / 60.0
                    dignity_map[p_name] = get_dignity(p_name, sign, compound, deg)
                else:
                    dignity_map[p_name] = "Neutral"

    # Relaxation for overlap with strictly preserved cyclic order
    relax_planet_angles(inner_planets, has_ascendant_barrier=True, is_outer=False)
    relax_planet_angles(outer_planets, has_ascendant_barrier=False, is_outer=True)

    # 4. Graha Drishti (Planetary Aspect Chords in Center Circle)
    svg += '<g class="aspect-lines">\n'
    targets = [p for p in inner_planets if p["item"]["name"] in classical_planets + ["Lagna", "Rahu", "Ketu"]]
    
    # 4a. Natal D1 to D1 Aspects
    for p_from in inner_planets:
        name_from = p_from["item"]["name"]
        if name_from not in classical_planets:
            continue
            
        dignity_from = dignity_map.get(name_from, "Neutral")
        is_dignified = dignity_from in ["Exalted", "Moolatrikona", "Own Sign", "Great Friend"]
        is_debilitated = dignity_from in ["Debilitated", "Enemy", "Great Enemy"]
        is_natural_benefic = name_from in ["Jupiter", "Venus"]
        is_natural_malefic = name_from in ["Saturn", "Mars"]
        
        for p_to in targets:
            name_to = p_to["item"]["name"]
            if name_from == name_to:
                continue
                
            virupas = get_graha_drishti(name_from, p_from["lon"], p_to["lon"])
            if virupas >= 25.0:
                if is_dignified or (is_natural_benefic and not is_debilitated):
                    col = "#27AE60" if dignity_from != "Exalted" else "#D4AC0D"
                    marker = "url(#arrow-exalted)" if dignity_from == "Exalted" else "url(#arrow-benefic)"
                    stroke_w = "1.3" if virupas > 45 else "1.0"
                    aspect_nature = f"Uplifting Blessing ({dignity_from})"
                elif is_natural_malefic or is_debilitated:
                    col = "#C0392B"
                    marker = "url(#arrow-malefic)"
                    stroke_w = "1.3" if virupas > 45 else "1.0"
                    aspect_nature = f"Pressure Glance ({dignity_from})"
                else:
                    col = "#2980B9"
                    marker = "url(#arrow-neutral)"
                    stroke_w = "0.9"
                    aspect_nature = f"Glance ({dignity_from})"
                    
                x1, y1 = polar_coords(r_aspect_inner, p_from["true_angle"])
                x2, y2 = polar_coords(r_aspect_inner, p_to["true_angle"])
                
                dx, dy = x2 - x1, y2 - y1
                dist = math.hypot(dx, dy)
                if dist > 8:
                    x2_arr = x1 + dx * ((dist - 5) / dist)
                    y2_arr = y1 + dy * ((dist - 5) / dist)
                else:
                    x2_arr, y2_arr = x2, y2
                    
                tip = f"Natal {name_from} ({dignity_from}) casts {round(virupas, 1)}v Drishti on Natal {name_to} — {aspect_nature}"
                svg += f'<line class="interactive-aspect natal-aspect" data-from="{name_from}" data-from-varga="{inner_name}" data-to="{name_to}" data-to-varga="{inner_name}" data-virupas="{round(virupas, 1)}" data-nature="{aspect_nature}" x1="{x1}" y1="{y1}" x2="{x2_arr}" y2="{y2_arr}" stroke="{col}" stroke-width="{stroke_w}" marker-end="{marker}" stroke-opacity="0.85"><title>{tip}</title></line>\n'

    # 4b. Cross-Chart Aspects (Outer Harmonic Planet -> Inner Natal Planet)
    for p_from in outer_planets:
        name_from = p_from["item"]["name"]
        if name_from not in classical_planets:
            continue
            
        is_natural_benefic = name_from in ["Jupiter", "Venus"]
        is_natural_malefic = name_from in ["Saturn", "Mars"]
        
        for p_to in targets:
            name_to = p_to["item"]["name"]
            if name_from == name_to:
                continue
                
            virupas = get_graha_drishti(name_from, p_from["lon"], p_to["lon"])
            if virupas >= 25.0:
                if is_natural_benefic:
                    col = "#1E8449"
                    marker = "url(#arrow-benefic)"
                    aspect_nature = f"Harmonic Blessing ({outer_name} ➔ {inner_name})"
                elif is_natural_malefic:
                    col = "#922B21"
                    marker = "url(#arrow-malefic)"
                    aspect_nature = f"Harmonic Pressure ({outer_name} ➔ {inner_name})"
                else:
                    col = "#8E44AD"
                    marker = "url(#arrow-cross)"
                    aspect_nature = f"Harmonic Glance ({outer_name} ➔ {inner_name})"
                    
                x1, y1 = polar_coords(r_aspect_inner, p_from["true_angle"])
                x2, y2 = polar_coords(r_aspect_inner, p_to["true_angle"])
                
                dx, dy = x2 - x1, y2 - y1
                dist = math.hypot(dx, dy)
                if dist > 8:
                    x2_arr = x1 + dx * ((dist - 5) / dist)
                    y2_arr = y1 + dy * ((dist - 5) / dist)
                else:
                    x2_arr, y2_arr = x2, y2
                    
                tip = f"[{outer_name} ➔ {inner_name}] {name_from} casts {round(virupas, 1)}v Drishti on Natal {name_to} — {aspect_nature}"
                svg += f'<line class="interactive-aspect cross-aspect" data-from="{name_from}" data-from-varga="{outer_name}" data-to="{name_to}" data-to-varga="{inner_name}" data-virupas="{round(virupas, 1)}" data-nature="{aspect_nature}" x1="{x1}" y1="{y1}" x2="{x2_arr}" y2="{y2_arr}" stroke="{col}" stroke-width="1.1" stroke-dasharray="3,2" marker-end="{marker}" stroke-opacity="0.8"><title>{tip}</title></line>\n'
    svg += '</g>\n'

    # 4c. Radial Degree Alignment Projection Rays, Leader Lines & Alignment Dots
    # Invisible inside the zodiac sign band (r = 138 to 164)
    svg += '<g class="radial-projection-rays" opacity="0.85">\n'
    for p in inner_planets:
        ang = p["true_angle"]
        draw_ang = p["draw_angle"]
        p_name = p["item"]["name"]
        p_col = planet_notations.get(p_name, {}).get("color", "#795548")
        tip = f"{inner_name} {p_name} True Degree Alignment ({p['item']['degree']}° {p['item']['minute']:02d}' {p['sign']})"
        
        # Connection leader line from displaced planet glyph (r = 118, draw_angle) to start of true ray (r = 122, true_angle)
        ang_diff = abs((draw_ang - ang + 180.0) % 360.0 - 180.0)
        if ang_diff > 1.2:
            lx1, ly1 = polar_coords(118, draw_ang)
            lx2, ly2 = polar_coords(122, ang)
            svg += f'<line class="radial-alignment-leader inner-leader" data-planet="{p_name}" x1="{lx1}" y1="{ly1}" x2="{lx2}" y2="{ly2}" stroke="{p_col}" stroke-width="0.75" stroke-dasharray="1.5,1.5" opacity="0.55"><title>{tip}</title></line>\n'

        # Segment 1: Inner pointer from planet perimeter to inner border of zodiac band (r = 122 to 138)
        x1_in, y1_in = polar_coords(122, ang)
        x2_in, y2_in = polar_coords(138, ang)
        svg += f'<line class="radial-alignment-ray inner-ray-inner" data-planet="{p_name}" data-varga="{inner_name}" x1="{x1_in}" y1="{y1_in}" x2="{x2_in}" y2="{y2_in}" stroke="{p_col}" stroke-width="0.75" stroke-dasharray="2,2" opacity="0.65"><title>{tip}</title></line>\n'
        # Alignment dot on the inner border of the zodiac ring (r = 138)
        svg += f'<circle class="radial-alignment-dot inner-dot" data-planet="{p_name}" cx="{x2_in}" cy="{y2_in}" r="1.8" fill="{p_col}" stroke="#FFFFFF" stroke-width="0.3"><title>{tip}</title></circle>\n'
        # Gap across Zodiac band (r = 138 to 164 is invisible)
        # Segment 2: Pointer emerging on outer side of zodiac band (r = 164 to 170.5) with arrow pointing outward
        x1_out, y1_out = polar_coords(164, ang)
        x2_out, y2_out = polar_coords(170.5, ang)
        svg += f'<line class="radial-alignment-ray inner-ray-outer" data-planet="{p_name}" data-varga="{inner_name}" x1="{x1_out}" y1="{y1_out}" x2="{x2_out}" y2="{y2_out}" stroke="{p_col}" stroke-width="0.75" stroke-dasharray="2,2" opacity="0.75" marker-end="url(#arrow-pointer-in)"><title>{tip}</title></line>\n'

    for p in outer_planets:
        ang = p["true_angle"]
        draw_ang = p["draw_angle"]
        p_name = p["item"]["name"]
        p_col = planet_notations.get(p_name, {}).get("color", "#795548")
        tip = f"{outer_name} {p_name} True Degree Alignment ({p['item']['degree']}° {p['item']['minute']:02d}' {p['sign']})"
        
        # Connection leader line from displaced outer planet glyph (r = 171, draw_angle) to start of ray (r = 168.5, true_angle)
        ang_diff = abs((draw_ang - ang + 180.0) % 360.0 - 180.0)
        if ang_diff > 1.2:
            lx1, ly1 = polar_coords(171, draw_ang)
            lx2, ly2 = polar_coords(168.5, ang)
            svg += f'<line class="radial-alignment-leader outer-leader" data-planet="{p_name}" x1="{lx1}" y1="{ly1}" x2="{lx2}" y2="{ly2}" stroke="{p_col}" stroke-width="0.75" stroke-dasharray="1.5,1.5" opacity="0.55"><title>{tip}</title></line>\n'
            # Outer rim leader line from outer sign glyph (r = 201) to outer rim ray (r = 204)
            ox1, oy1 = polar_coords(201, draw_ang)
            ox2, oy2 = polar_coords(204, ang)
            svg += f'<line class="radial-alignment-leader outer-leader-rim" data-planet="{p_name}" x1="{ox1}" y1="{oy1}" x2="{ox2}" y2="{oy2}" stroke="{p_col}" stroke-width="0.75" stroke-dasharray="1.5,1.5" opacity="0.55"><title>{tip}</title></line>\n'

        # Segment continuing from near outer planet perimeter (r = 168.5) inward to the outer border of the zodiac band (r = 164)
        x1_to_zodiac, y1_to_zodiac = polar_coords(168.5, ang)
        x2_to_zodiac, y2_to_zodiac = polar_coords(164, ang)
        svg += f'<line class="radial-alignment-ray outer-ray outer-ray-in" data-planet="{p_name}" data-varga="{outer_name}" x1="{x1_to_zodiac}" y1="{y1_to_zodiac}" x2="{x2_to_zodiac}" y2="{y2_to_zodiac}" stroke="{p_col}" stroke-width="0.75" stroke-dasharray="2,2" opacity="0.75" marker-end="url(#arrow-pointer-in)"><title>{tip}</title></line>\n'
        # Alignment dot on the outer border of the zodiac ring (r = 164)
        svg += f'<circle class="radial-alignment-dot outer-dot" data-planet="{p_name}" cx="{x2_to_zodiac}" cy="{y2_to_zodiac}" r="1.8" fill="{p_col}" stroke="#FFFFFF" stroke-width="0.3"><title>{tip}</title></circle>\n'
        # Outer outward pointer at the outermost rim (r = 204 to 208.5) so it never overlays any text or symbols
        x1_rim, y1_rim = polar_coords(204, ang)
        x2_rim, y2_rim = polar_coords(208.5, ang)
        svg += f'<line class="radial-alignment-ray outer-ray outer-ray-rim" data-planet="{p_name}" data-varga="{outer_name}" x1="{x1_rim}" y1="{y1_rim}" x2="{x2_rim}" y2="{y2_rim}" stroke="{p_col}" stroke-width="0.75" stroke-dasharray="2,2" opacity="0.8" marker-end="url(#arrow-pointer-out)"><title>{tip}</title></line>\n'
    svg += '</g>\n'

    # Radial Positions for stacking
    r_in_min = 85
    r_in_deg = 98
    r_in_pl = 115

    r_out_pl = 172
    r_out_deg = 181
    r_out_min = 190
    r_out_sign = 199

    # 6. Inner Ring: Natal Planets (D1)
    svg += '<g class="inner-planets-group">\n'
    for p in inner_planets:
        item = p["item"]
        angle = p["draw_angle"]
        p_name = item["name"]
        info = planet_notations.get(p_name, {})
        label = info.get(mode, info.get("symbol", p_name[:2]))
        color = info.get("color", "#000")
        
        is_retro = item.get("is_retrograde", False)
        retro_badge = "R" if is_retro else ""
        
        px, py = polar_coords(r_in_pl, angle)

        font_sz = 9.5 if p_name == "Lagna" else (12.5 if mode == "devanagari" else 12)
        if mode == "symbol" and p_name in ["Mars", "Venus"]:
            font_sz = "10.0"
        
        dignity_str = dignity_map.get(p_name, "")
        dignity_tag = f" [{dignity_str}]" if dignity_str else ""
        tooltip = f"Natal ({inner_name}) {info.get('full_sa', p_name)}{dignity_tag} — {item['degree']}° {item['minute']:02d}'{retro_badge} in {item['sign']}"
        
        svg += f'<g class="interactive planet-glyph inner-planet" data-type="planet" data-varga="{inner_name}" data-id="{p_name}" style="cursor: pointer;"><title>{tooltip}</title>\n'

        # Minute text
        mx, my = polar_coords(r_in_min, angle)
        svg += f'<text x="{mx}" y="{my}" font-size="5.8" stroke="#F7F3EB" stroke-width="1.0" paint-order="stroke" stroke-linejoin="round" fill="{color}" text-anchor="middle" dominant-baseline="central">{item["minute"]:02d}\'{" R" if is_retro else ""}</text>\n'

        # Degree text
        dx, dy = polar_coords(r_in_deg, angle)
        svg += f'<text x="{dx}" y="{dy}" font-size="6.8" stroke="#F7F3EB" stroke-width="1.2" paint-order="stroke" stroke-linejoin="round" fill="{color}" text-anchor="middle" dominant-baseline="central">{item["degree"]}°</text>\n'

        # Planet Glyph
        svg += f'<text class="glyph-symbol" x="{px}" y="{py}" font-size="{font_sz}" stroke="#F7F3EB" stroke-width="2.2" paint-order="stroke" stroke-linejoin="round" fill="{color}" font-weight="bold" text-anchor="middle" dominant-baseline="central">{label}</text>\n'
        svg += '</g>\n'
    svg += '</g>\n'

    # 7. Outer Ring: Harmonic / Divisional Planets (D9 / Varga)
    svg += '<g class="outer-planets-group">\n'
    for p in outer_planets:
        item = p["item"]
        angle = p["draw_angle"]
        true_angle = p["true_angle"]
        p_name = item["name"]
        info = planet_notations.get(p_name, {})
        label = info.get(mode, info.get("symbol", p_name[:2]))
        color = info.get("color", "#000")
        
        is_retro = item.get("is_retrograde", False)
        retro_badge = "R" if is_retro else ""
        
        # Lagna is a 3-letter label ('Asc'), slightly inset to prevent touching degree numbers
        pl_r = (r_out_pl - 1.5) if p_name == "Lagna" else r_out_pl
        px, py = polar_coords(pl_r, angle)

        font_sz = 7.8 if p_name == "Lagna" else (11.5 if mode == "devanagari" else 11.0)
        if mode == "symbol" and p_name in ["Mars", "Venus"]:
            font_sz = "9.5"
            
        # Natal House alignment
        d1_house = ((p["sign_idx"] - anchor_s_idx + 12) % 12) + 1
        tooltip = f"{outer_name} {info.get('full_sa', p_name)} in {item['sign']} {item['degree']}° {item['minute']:02d}'{retro_badge} (Natal House {d1_house})"
        
        # Divisional Sign symbol and color for outer planet
        s_sym, s_col, _ = sign_symbols.get(item["sign"], ("?", "#000", "?"))
        
        svg += f'<g class="interactive planet-glyph outer-planet" data-type="planet" data-varga="{outer_name}" data-id="{p_name}" style="cursor: pointer;"><title>{tooltip}</title>\n'

        # Minute text
        mx, my = polar_coords(r_out_min, angle)
        svg += f'<text x="{mx}" y="{my}" font-size="5.2" stroke="#FAF6F0" stroke-width="0.8" paint-order="stroke" stroke-linejoin="round" fill="{color}" text-anchor="middle" dominant-baseline="central">{item["minute"]:02d}\'{" R" if is_retro else ""}</text>\n'

        # Degree text
        dx, dy = polar_coords(r_out_deg, angle)
        svg += f'<text x="{dx}" y="{dy}" font-size="6.2" stroke="#FAF6F0" stroke-width="0.9" paint-order="stroke" stroke-linejoin="round" fill="{color}" text-anchor="middle" dominant-baseline="central">{item["degree"]}°</text>\n'

        # Planet Glyph
        svg += f'<text class="glyph-symbol outer-glyph" x="{px}" y="{py}" font-size="{font_sz}" stroke="#FAF6F0" stroke-width="2.2" paint-order="stroke" stroke-linejoin="round" fill="{color}" font-weight="600" text-anchor="middle" dominant-baseline="central">{label}</text>\n'
        
        # Divisional Sign Glyph in outer ring (so user immediately sees which sign outer planet occupies)
        sx, sy = polar_coords(r_out_sign, angle)
        svg += f'<text class="outer-sign-glyph" x="{sx}" y="{sy}" font-size="6.5" stroke="#FAF6F0" stroke-width="0.9" paint-order="stroke" stroke-linejoin="round" fill="{s_col}" font-weight="bold" text-anchor="middle" dominant-baseline="central">{s_sym}</text>\n'
        
        svg += '</g>\n'
    svg += '</g>\n'

    svg += '</svg>\n'
    return svg


