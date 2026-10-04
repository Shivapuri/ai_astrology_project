import math
import re
from typing import Dict, Any, List, Optional
from jyotish.aspects.aspects import get_graha_drishti, get_aspect_explanation
from jyotish.relationships.relationships import (
    get_dignity, get_compound_relationship, get_natural_relationship, 
    get_temporary_relationship, SIGN_LORDS
)

ASTRO_FONT_STACK = 'STIX Two Math, Cambria Math, DejaVu Sans, Noto Sans Symbols 2, Apple Symbols, Segoe UI Symbol, sans-serif'

planet_notations = {
    "Lagna": {
        "symbol": "Asc",
        "english": "Asc",
        "devanagari": "ल",
        "translit": "Lag",
        "full_en": "Ascendant",
        "full_sa": "Lagna",
        "dev_full": "लग्न",
        "color": "#0284c7"
    },
    "Sun": {
        "symbol": "☉\uFE0E",
        "english": "Su",
        "devanagari": "सू",
        "translit": "Sū",
        "full_en": "Sun",
        "full_sa": "Sūrya",
        "dev_full": "सूर्य",
        "color": "#ea580c"
    },
    "Moon": {
        "symbol": "☽\uFE0E",
        "english": "Mo",
        "devanagari": "चं",
        "translit": "Ca",
        "full_en": "Moon",
        "full_sa": "Chandra",
        "dev_full": "चन्द्र",
        "color": "#475569"
    },
    "Mars": {
        "symbol": "♂\uFE0E",
        "english": "Ma",
        "devanagari": "मं",
        "translit": "Ma",
        "full_en": "Mars",
        "full_sa": "Mangala",
        "dev_full": "मङ्गल",
        "color": "#dc2626"
    },
    "Mercury": {
        "symbol": "☿\uFE0E",
        "english": "Me",
        "devanagari": "बु",
        "translit": "Bu",
        "full_en": "Mercury",
        "full_sa": "Budha",
        "dev_full": "बुध",
        "color": "#16a34a"
    },
    "Jupiter": {
        "symbol": "♃\uFE0E",
        "english": "Ju",
        "devanagari": "गु",
        "translit": "Gu",
        "full_en": "Jupiter",
        "full_sa": "Guru",
        "dev_full": "गुरु",
        "color": "#d97706"
    },
    "Venus": {
        "symbol": "♀\uFE0E",
        "english": "Ve",
        "devanagari": "शु",
        "translit": "Śu",
        "full_en": "Venus",
        "full_sa": "Śukra",
        "dev_full": "शुक्र",
        "color": "#db2777"
    },
    "Saturn": {
        "symbol": "♄\uFE0E",
        "english": "Sa",
        "devanagari": "श",
        "translit": "Śa",
        "full_en": "Saturn",
        "full_sa": "Śani",
        "dev_full": "शनि",
        "color": "#334155"
    },
    "Rahu": {
        "symbol": "☊\uFE0E",
        "english": "Ra",
        "devanagari": "रा",
        "translit": "Rā",
        "full_en": "North Node",
        "full_sa": "Rāhu",
        "dev_full": "राहु",
        "color": "#4f46e5"
    },
    "Ketu": {
        "symbol": "☋\uFE0E",
        "english": "Ke",
        "devanagari": "के",
        "translit": "Ke",
        "full_en": "South Node",
        "full_sa": "Ketu",
        "dev_full": "केतु",
        "color": "#78716c"
    },
    "Uranus": {
        "symbol": "♅\uFE0E",
        "english": "Ur",
        "devanagari": "यू",
        "translit": "Ur",
        "full_en": "Uranus",
        "full_sa": "Harṣala",
        "dev_full": "हर्षल",
        "color": "#0284c7"
    },
    "Neptune": {
        "symbol": "♆\uFE0E",
        "english": "Ne",
        "devanagari": "ने",
        "translit": "Ne",
        "full_en": "Neptune",
        "full_sa": "Varuṇa",
        "dev_full": "वरुण",
        "color": "#0d9488"
    },
    "Pluto": {
        "symbol": "♇\uFE0E",
        "english": "Pl",
        "devanagari": "प्ल",
        "translit": "Pl",
        "full_en": "Pluto",
        "full_sa": "Yama",
        "dev_full": "यम",
        "color": "#7c3aed"
    }
}

# Compatibility mapping
planet_symbols = {k: (v["symbol"], v["color"]) for k, v in planet_notations.items()}

# Warm antique umber tone for Rashi signs with crisp legibility against house fills
RASHI_SIGN_COLOR = "#7a5535"

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

NAKSHATRA_ABBREVIATIONS = {
    "Ashwini": "Ashw",
    "Bharani": "Bhar",
    "Krittika": "Krit",
    "Rohini": "Rohi",
    "Mrigashira": "Mrig",
    "Ardra": "Ardr",
    "Punarvasu": "Puna",
    "Pushya": "Push",
    "Ashlesha": "Ashl",
    "Magha": "Magh",
    "Purva Phalguni": "PPha",
    "Uttara Phalguni": "UPha",
    "Hasta": "Hast",
    "Chitra": "Chit",
    "Swati": "Swat",
    "Vishakha": "Vish",
    "Anuradha": "Anur",
    "Jyeshtha": "Jyes",
    "Mula": "Mula",
    "Purva Ashadha": "PAsh",
    "Uttara Ashadha": "UAsh",
    "Shravana": "Shra",
    "Dhanishtha": "Dhan",
    "Shatabhisha": "Shat",
    "Purva Bhadrapada": "PBha",
    "Uttara Bhadrapada": "UBha",
    "Revati": "Reva",
}

def get_nakshatra_abbreviation(name: str, length: int = 4) -> str:
    """Returns the standardized abbreviation for a nakshatra name."""
    if not name:
        return ""
    abbr = NAKSHATRA_ABBREVIATIONS.get(name)
    if abbr:
        return abbr if length == 4 else abbr[:length]
    return name[:length]

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
        "minute": minutes,
        "nakshatra": varga_data["lagna"].get("nakshatra", "")
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
            "is_retrograde": p_data.get("is_retrograde", False),
            "nakshatra": p_data.get("nakshatra", "")
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

def get_equidistant_t(num_planets: int) -> List[float]:
    """
    Computes deterministic, evenly-spaced normalized positions (t in [0.0, 1.0])
    along a house track or diagonal.
    - 1 planet: Dead center (0.50)
    - 2 planets: [0.18, 0.82]
    - 3 planets: [0.10, 0.50, 0.90]
    - 4 planets: [0.06, 0.35, 0.65, 0.94]
    - 5+ planets: Linear interpolation across [0.06, 0.94]
    """
    if num_planets <= 0:
        return []
    if num_planets == 1:
        return [0.50]
    if num_planets == 2:
        return [0.18, 0.82]
    if num_planets == 3:
        return [0.10, 0.50, 0.90]
    if num_planets == 4:
        return [0.06, 0.35, 0.65, 0.94]
    return [0.06 + 0.88 * (i / (num_planets - 1)) for i in range(num_planets)]

def get_north_equidistant_t(num_planets: int) -> List[float]:
    """
    Computes deterministic, evenly-spaced normalized positions (t in [0.0, 1.0])
    specifically along North Indian tracks.
    For 3 and 4 planets, spacing is tighter so they don't sit too close to the outside borders.
    - 1 planet: Dead center (0.50)
    - 2 planets: [0.26, 0.74]
    - 3 planets: [0.20, 0.50, 0.80]
    - 4 planets: [0.12, 0.37, 0.63, 0.88]
    - 5+ planets: Linear interpolation across [0.10, 0.90]
    """
    if num_planets <= 0:
        return []
    if num_planets == 1:
        return [0.50]
    if num_planets == 2:
        return [0.26, 0.74]
    if num_planets == 3:
        return [0.20, 0.50, 0.80]
    if num_planets == 4:
        return [0.12, 0.37, 0.63, 0.88]
    return [0.10 + 0.80 * (i / (num_planets - 1)) for i in range(num_planets)]

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

            font_fam = ASTRO_FONT_STACK if mode == "symbol" else "sans-serif"
            if not items_to_render:
                svg += f'    <g><title>{tooltip_str}</title><rect x="{cx}" y="{ry}" width="{col_w}" height="{row_h}" fill="transparent"/></g>\n'
            elif len(items_to_render) == 1:
                tspan_str = render_tspan(items_to_render[0][0], items_to_render[0][1], 11.5)
                svg += f'    <g><title>{tooltip_str}</title><text x="{center_x}" y="{center_y}" font-family="{font_fam}" font-weight="bold" fill="{elem_color}" text-anchor="middle" dominant-baseline="central" style="font-variant-emoji: text;">{tspan_str}</text></g>\n'
            elif len(items_to_render) == 2:
                tspan_str = "  ".join([render_tspan(g, n, 10.5) for g, n in items_to_render])
                svg += f'    <g><title>{tooltip_str}</title><text x="{center_x}" y="{center_y}" font-family="{font_fam}" font-weight="bold" fill="{elem_color}" text-anchor="middle" dominant-baseline="central" style="font-variant-emoji: text;">{tspan_str}</text></g>\n'
            elif len(items_to_render) == 3:
                tspan_str = " ".join([render_tspan(g, n, 9.5) for g, n in items_to_render])
                svg += f'    <g><title>{tooltip_str}</title><text x="{center_x}" y="{center_y}" font-family="{font_fam}" font-weight="bold" fill="{elem_color}" text-anchor="middle" dominant-baseline="central" style="font-variant-emoji: text;">{tspan_str}</text></g>\n'
            else:
                mid = (len(items_to_render) + 1) // 2
                line1 = " ".join([render_tspan(g, n, 8.5) for g, n in items_to_render[:mid]])
                line2 = " ".join([render_tspan(g, n, 8.5) for g, n in items_to_render[mid:]])
                svg += f'    <g><title>{tooltip_str}</title><text x="{center_x}" y="{center_y - 5}" font-family="{font_fam}" font-weight="bold" fill="{elem_color}" text-anchor="middle" dominant-baseline="central" style="font-variant-emoji: text;">{line1}</text><text x="{center_x}" y="{center_y + 6}" font-family="{font_fam}" font-weight="bold" fill="{elem_color}" text-anchor="middle" dominant-baseline="central" style="font-variant-emoji: text;">{line2}</text></g>\n'

    # 4. Grid lines
    svg += f'    <line x1="189" y1="157" x2="189" y2="261" stroke="#d5c8b2" stroke-width="0.8"/>\n'
    svg += f'    <line x1="229" y1="157" x2="229" y2="261" stroke="#d5c8b2" stroke-width="0.8"/>\n'
    svg += f'    <line x1="149" y1="183" x2="269" y2="183" stroke="#d5c8b2" stroke-width="0.8"/>\n'
    svg += f'    <line x1="149" y1="209" x2="269" y2="209" stroke="#d5c8b2" stroke-width="0.8"/>\n'
    svg += f'    <line x1="149" y1="235" x2="269" y2="235" stroke="#d5c8b2" stroke-width="0.8"/>\n'
    svg += f'    <rect x="149" y="157" width="120" height="104" fill="none" stroke="#b59472" stroke-width="1"/>\n'

    svg += '    <text x="200" y="281" font-family="sans-serif" font-size="7.5" fill="#8c7b64" text-anchor="middle">Click to view Kalapurusha Anatomy →</text>\n'
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
        region_safe = item["region"].replace("&", "&amp;")
        svg += f'      <text x="108" y="{y_anat + 11}" font-family="sans-serif" font-size="8.5" font-weight="bold" fill="#4a3325"><tspan fill="#b59472">{sign_abbr}</tspan> {region_safe}</text>\n'
        svg += f'      <text x="108" y="{y_anat + 21}" font-family="sans-serif" font-size="7.5" fill="#6b5a4b">{p_str}</text>\n'
        svg += f'      <text x="290" y="{y_anat + 16}" font-family="sans-serif" font-size="8.5" font-weight="bold" fill="#a93226" text-anchor="end">({len(p_list)})</text>\n'
        svg += f'    </g>\n'
        y_anat += row_anat_h

    svg += f'    <rect x="102" y="268" width="196" height="16" fill="#eae1d1"/>\n'
    svg += f'    <text x="200" y="280" font-family="sans-serif" font-size="8" font-weight="bold" fill="#4a3325" text-anchor="middle">Active: {len(active_regions)}/12 Body Limbs</text>\n'
    svg += '    <text x="200" y="294" font-family="sans-serif" font-size="7.5" fill="#8c7b64" text-anchor="middle">Click to return to Title →</text>\n'
    svg += '  </g>\n'

    svg += '</g>\n'
    return svg

def polar_coords(r, angle_deg):
    rad = math.radians(angle_deg)
    return r * math.cos(rad), r * math.sin(rad)

def annular_sector(r_in, r_out, a_start, a_end):
    """Generates SVG path d string for an annular sector wedge."""
    x1, y1 = polar_coords(r_in, a_start)
    x2, y2 = polar_coords(r_out, a_start)
    x3, y3 = polar_coords(r_out, a_end)
    x4, y4 = polar_coords(r_in, a_end)
    return f'M {x1:.2f},{y1:.2f} L {x2:.2f},{y2:.2f} A {r_out:.2f} {r_out:.2f} 0 0 0 {x3:.2f},{y3:.2f} L {x4:.2f},{y4:.2f} A {r_in:.2f} {r_in:.2f} 0 0 1 {x1:.2f},{y1:.2f} Z'

def get_aspect_defs_svg():
    return (
        '  <defs>\n'
        '    <style>\n'
        '      .aspects-hidden:not(.aspects-filtered) .aspect-lines { display: none; }\n'
        '      .zodiac-line-glyph, .natal-sign-glyph, .outer-sign-glyph, .sub-sign-symbol, .glyph-symbol, .graha-glyph {\n'
        f'        font-family: var(--font-astro-glyphs, {ASTRO_FONT_STACK}) !important;\n'
        '        font-variant-emoji: text !important;\n'
        '      }\n'
        '    </style>\n'
        '    <marker id="arrow-benefic" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#16a34a"/></marker>\n'
        '    <marker id="arrow-exalted" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#D4AC0D"/></marker>\n'
        '    <marker id="arrow-malefic" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#dc2626"/></marker>\n'
        '    <marker id="arrow-neutral" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#2563eb"/></marker>\n'
        '    <marker id="arrow-cross" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="5" markerHeight="5" orient="auto"><path d="M 0 2 L 7 5 L 0 8 z" fill="#8E44AD"/></marker>\n'
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
                
            # Tangent vector into destination point (x2_arr, y2_arr)
            tx = x2_arr - cx
            ty = y2_arr - cy
            t_len = math.hypot(tx, ty)
            if t_len > 0.001:
                aux = tx / t_len
                auy = ty / t_len
            else:
                aux = ux
                auy = uy
            anx = -auy
            any_ = aux

            # Clean, sleek, universally-rendered SVG arrowhead (7.5px length, 6.4px width)
            arr_len = 7.5
            arr_hw = 3.2
            bx = x2_arr - aux * arr_len
            by = y2_arr - auy * arr_len
            w1x = bx + anx * arr_hw
            w1y = by + any_ * arr_hw
            w2x = bx - anx * arr_hw
            w2y = by - any_ * arr_hw

            tip = (
                f"{name_from} → {name_to}: {vir_round} Virūpas ({deg_round}° separation)\n"
                f"• Rule: {rule_exp}\n"
                f"• Potency: {vir_round} / 60 Virūpas\n"
                f"• Influence: {nature_label}\n"
                f"• Dignity: {dignity_from}"
            )
            
            # Aspect path ends cleanly at the base of the arrowhead (bx, by)
            lines_svg += f'    <path class="interactive-aspect" data-from="{name_from}" data-to="{name_to}" data-virupas="{vir_round}" data-deg="{deg_round}" data-rule="{rule_exp}" data-nature="{nature_label}" data-benefic="{"true" if is_benefic else "false"}" d="M {x1_arr:.1f},{y1_arr:.1f} Q {cx:.1f},{cy:.1f} {bx:.1f},{by:.1f}" fill="none" stroke="{col}" stroke-width="{stroke_w}" stroke-dasharray="{stroke_dash}" stroke-opacity="0.9"><title>{tip}</title></path>\n'
            # Native SVG arrowhead element (works 100% reliably across all browsers including Firefox)
            lines_svg += f'    <path class="interactive-aspect aspect-arrow" data-from="{name_from}" data-to="{name_to}" data-virupas="{vir_round}" d="M {x2_arr:.1f},{y2_arr:.1f} L {w1x:.1f},{w1y:.1f} L {w2x:.1f},{w2y:.1f} Z" fill="{col}" stroke="{col}" stroke-width="0.5" stroke-linejoin="round"><title>{tip}</title></path>\n'
            
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

def generate_south_indian(items, mode="symbol", varga_name="D1", root_planet="Lagna", debilitation_mode: str = "kala_degree", show_nakshatras: bool = False):
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
                "is_retrograde": item.get("is_retrograde", False),
                "nakshatra": item.get("nakshatra", "")
            })

    svg = '<svg width="100%" height="100%" viewBox="-10 -10 420 420" class="aspects-hidden" preserveAspectRatio="xMidYMid meet" xmlns="http://www.w3.org/2000/svg" style="background:transparent;">\n'
    planet_coords = {}

    # Permanent Harmonious House Color Fills (Kendras 1,4,7,10 | Trikonas 5,9 | Other Houses)
    for sign, (cx, cy) in cell_coords.items():
        h_num = (signs_list.index(sign) - anchor_index + 12) % 12 + 1
        if h_num in (1, 4, 7, 10):
            fill_col = "var(--chart-kendra-color, #eedec9)"
            cls = "house-bg house-kendra"
        elif h_num in (5, 9):
            fill_col = "var(--chart-trikona-color, #faede0)"
            cls = "house-bg house-trikona"
        else:
            fill_col = "var(--chart-other-color, #f9f5eb)"
            cls = "house-bg house-other"
        svg += f'<rect class="{cls}" x="{cx}" y="{cy}" width="100" height="100" fill="{fill_col}"/>\n'

    # Center Parchment Ground
    svg += '<rect x="100" y="100" width="200" height="200" fill="#fffdfa"/>\n'

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

    # 4-Triplet Diagonal Configuration (Clockwise progression from preceding sign to succeeding sign)
    # Triplet 1 (Aries, Taurus, Gemini): TL (16, 16) -> BR (84, 84) | Cusp BL (13, 87), Sign TR (87, 13)
    # Triplet 2 (Cancer, Leo, Virgo):    TR (84, 16) -> BL (16, 84) | Cusp TL (13, 13), Sign BR (87, 87)
    # Triplet 3 (Libra, Scorpio, Sag):   BR (84, 84) -> TL (16, 16) | Cusp TR (87, 13), Sign BL (13, 87)
    # Triplet 4 (Cap, Aquarius, Pisces): BL (16, 84) -> TR (84, 16) | Cusp BR (87, 87), Sign TL (13, 13)
    south_triplets = {
        # Triplet 1 (Aries, Taurus, Gemini) -> TL -> BR (\) [Left to Right]
        "Aries":       {"start": (16, 16), "end": (84, 84), "cusp": (13, 87), "sign": (87, 13)},
        "Taurus":      {"start": (16, 16), "end": (84, 84), "cusp": (13, 87), "sign": (87, 13)},
        "Gemini":      {"start": (16, 16), "end": (84, 84), "cusp": (13, 87), "sign": (87, 13)},
        # Triplet 2 (Cancer, Leo, Virgo) -> TR -> BL (/) [Top to Bottom]
        "Cancer":      {"start": (84, 16), "end": (16, 84), "cusp": (13, 13), "sign": (87, 87)},
        "Leo":         {"start": (84, 16), "end": (16, 84), "cusp": (13, 13), "sign": (87, 87)},
        "Virgo":       {"start": (84, 16), "end": (16, 84), "cusp": (13, 13), "sign": (87, 87)},
        # Triplet 3 (Libra, Scorpio, Sagittarius) -> BR -> TL (\) [Right to Left]
        "Libra":       {"start": (84, 84), "end": (16, 16), "cusp": (87, 13), "sign": (13, 87)},
        "Scorpio":     {"start": (84, 84), "end": (16, 16), "cusp": (87, 13), "sign": (13, 87)},
        "Sagittarius": {"start": (84, 84), "end": (16, 16), "cusp": (87, 13), "sign": (13, 87)},
        # Triplet 4 (Capricorn, Aquarius, Pisces) -> BL -> TR (/) [Bottom to Top]
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
        
        h_num = (signs_list.index(sign) - anchor_index + 12) % 12 + 1
        # Background hit rect for interactive sign selection and highlighting
        svg += f'<rect class="interactive sign-cell-bg" data-type="sign" data-id="{sign}" data-house="{h_num}" x="{x}" y="{y}" width="100" height="100" fill="transparent" style="cursor: pointer;"><title>House {h_num} ({sign})</title></rect>\n'

        # Draw Rasi Sign (Cross-Diagonal Corner, subtle 10.5px, STIX Math)
        s_sym, s_col, _ = sign_symbols[sign]
        svg += f'<text class="interactive zodiac-line-glyph" data-type="sign" data-id="{sign}" x="{x + s_dx}" y="{y + s_dy}" font-size="10.5" font-family="{ASTRO_FONT_STACK}" font-weight="bold" fill="{s_col}" opacity="0.8" text-anchor="middle" dominant-baseline="central" style="cursor: pointer; font-variant-emoji: text;">{s_sym}</text>\n'

        # If this is anchor sign for non-Lagna root, draw the diagonal badge
        if root_planet != "Lagna" and sign == anchor_sign:
            badge_text = "CL" if root_planet == "Moon" else ("SL" if root_planet == "Sun" else "L")
            svg += f'<line x1="{x}" y1="{y + 26}" x2="{x + 26}" y2="{y}" stroke="#C0392B" stroke-width="2.5" />\n'
            svg += f'<rect x="{x + 2}" y="{y + 2}" width="22" height="14" rx="3" fill="#C0392B"/>\n'
            svg += f'<text x="{x + 13}" y="{y + 9}" font-family="sans-serif" font-size="9" font-weight="bold" fill="#FFFFFF" text-anchor="middle" dominant-baseline="central">{badge_text}</text>\n'

        # Draw House Cusps (Opposite Cross-Diagonal Corner, pure number, no "H", 10px)
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
                        spread_offset = (c_idx * 13) if c_dx < 50 else -((num_c - 1 - c_idx) * 13)
                        cx_pos = x + c_dx + spread_offset
                        cy_pos = y + c_dy
                            
                    svg += f'<g class="interactive" data-type="house" data-id="{c_num}" style="cursor: pointer;"><title>{c_tooltip}</title>\n'
                    svg += f'<text x="{cx_pos}" y="{cy_pos}" font-family="sans-serif" font-size="10" font-weight="bold" fill="#7D3C98" text-anchor="middle" dominant-baseline="central">{c_num}</text>\n'
                    svg += '</g>\n'
        else:
            # Whole Sign House number relative to anchor planet
            h_num = (signs_list.index(sign) - anchor_index + 12) % 12 + 1
            h_tooltip = f"House {h_num} from {root_planet} in {sign}"
            is_kendra = h_num in [1, 4, 7, 10]
            col = "#C0392B" if is_kendra else "#7D3C98"
            bx = x + c_dx
            by = y + c_dy
            svg += f'<g class="interactive" data-type="house" data-id="{h_num}" style="cursor: pointer;"><title>{h_tooltip}</title>\n'
            svg += f'<text x="{bx}" y="{by}" font-family="sans-serif" font-size="10" font-weight="bold" fill="{col}" text-anchor="middle" dominant-baseline="central">{h_num}</text>\n'
            svg += '</g>\n'

        # Sort planets by degree within sign
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

        # Deterministic equidistant spacing along clear axis
        t_values = get_equidistant_t(len(planets_with_deg))

        for idx, (p_deg_val, p) in enumerate(planets_with_deg):
            t = t_values[idx]
            px = x + p_start_x + (p_end_x - p_start_x) * t
            py = y + p_start_y + (p_end_y - p_start_y) * t

            # Only for 5+ planets: alternate slight perpendicular shift if crowded
            if len(planets_with_deg) > 4:
                shift = -9 if (idx % 2 == 0) else 9
                if sign in ["Aries", "Taurus", "Gemini", "Libra", "Scorpio", "Sagittarius"]:
                    px += shift
                    py -= shift
                else:
                    px += shift
                    py += shift

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
            
            font_sz = "13" if (mode == "symbol" and p["name"] != "Lagna") else ("12" if mode == "devanagari" else "11")
            glyph_cls = "graha-glyph" if mode == "symbol" and p["name"] != "Lagna" else ""
            font_fam = ASTRO_FONT_STACK if (mode == "symbol" and p["name"] != "Lagna") else "sans-serif"
            
            nak_abbr = get_nakshatra_abbreviation(p.get("nakshatra", ""), length=4) if show_nakshatras else ""
            rel_x = px - x
            if show_nakshatras and nak_abbr:
                if rel_x <= 55:
                    nak_x = px + (21 if is_retro else 16)
                    anchor = "start"
                    hl_x = px - 18
                else:
                    nak_x = px - 16
                    anchor = "end"
                    hl_x = px - 32
                svg += f'<g class="interactive {glyph_cls}" data-type="planet" data-id="{p["name"]}" style="cursor: pointer;"><title>{tooltip}</title>\n'
                svg += f'<rect class="planet-highlight-bg" fill="none" stroke="none" x="{hl_x:.1f}" y="{py - 11:.1f}" width="50" height="30" rx="6"/>\n'
            else:
                svg += f'<g class="interactive {glyph_cls}" data-type="planet" data-id="{p["name"]}" style="cursor: pointer;"><title>{tooltip}</title>\n'
                svg += f'<rect class="planet-highlight-bg" fill="none" stroke="none" x="{px - 18:.1f}" y="{py - 11:.1f}" width="36" height="30" rx="6"/>\n'
            svg += f'<text class="{glyph_cls}" x="{px}" y="{py - 2}" font-family="{font_fam}" font-size="{font_sz}" font-weight="bold" fill="{info["color"]}" text-anchor="middle" dominant-baseline="central" style="font-variant-emoji: text;">{label}</text>\n'
            svg += f'<text x="{px}" y="{py + 11}" font-family="sans-serif" font-size="9" font-weight="normal" fill="#5C4433" text-anchor="middle" dominant-baseline="central">'
            svg += f'<tspan>{p["deg"]}</tspan>'
            if is_retro:
                svg += f'<tspan font-size="8" font-weight="bold" fill="#C0392B"> R</tspan>'
            svg += '</text>\n'
            if show_nakshatras and nak_abbr:
                svg += f'<text x="{nak_x}" y="{py + 11}" font-family="sans-serif" font-size="5.8" font-weight="500" fill="#8c7b64" text-anchor="{anchor}" dominant-baseline="central">{nak_abbr}</text>\n'
            svg += '</g>\n'
            
            s_idx = signs_list.index(sign)
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
                    dignity_map[p_name] = get_dignity(p_name, p_sign, compound, deg, debilitation_mode=debilitation_mode)
                else:
                    dignity_map[p_name] = "Neutral"

    svg += get_aspect_defs_svg()
    svg += render_aspect_lines_group(planet_coords, dignity_map, is_circular=False)

    svg += '</svg>\n'
    return svg

NORTH_CHART_SCALE_X = 1.12
NORTH_CHART_VIEW_W = int(round(500 * NORTH_CHART_SCALE_X))  # 560
NORTH_CHART_VIEW_H = 500

def _scale_svg_path_x(d_str: str, sx: float) -> str:
    """Scales all X coordinates in an SVG path string by sx while preserving Y coordinates."""
    tokens = re.split(r'([MCLZz])', d_str)
    out = []
    for token in tokens:
        if not token:
            continue
        if token in "MCLZz":
            out.append(token)
        else:
            parts = token.strip().replace(',', ' ').split()
            scaled_parts = []
            for i, num_str in enumerate(parts):
                val = float(num_str)
                if i % 2 == 0:  # X coordinate
                    scaled_parts.append(f"{val * sx:.1f}".rstrip('0').rstrip('.'))
                else:  # Y coordinate
                    scaled_parts.append(f"{val:.1f}".rstrip('0').rstrip('.'))
            out.append(" " + " ".join(scaled_parts) + " ")
    return "".join(out).strip()

def generate_north_indian(items, mode="symbol", varga_name="D1", root_planet="Lagna", debilitation_mode: str = "kala_degree", show_nakshatras: bool = False):
    svg = f'<svg width="100%" height="100%" viewBox="0 0 {NORTH_CHART_VIEW_W} {NORTH_CHART_VIEW_H}" class="aspects-hidden" preserveAspectRatio="xMidYMid meet" xmlns="http://www.w3.org/2000/svg" style="background:transparent;">\n'
    planet_coords = {}
    # Parchment Ground
    svg += f'<rect width="{NORTH_CHART_VIEW_W}" height="{NORTH_CHART_VIEW_H}" fill="#fffdfa"/>\n'

    ni_paths_base = [
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
    ni_paths = [_scale_svg_path_x(p, NORTH_CHART_SCALE_X) for p in ni_paths_base]

    # Permanent Harmonious House Color Fills (Kendras 1,4,7,10 | Trikonas 5,9 | Other Houses)
    for h in range(12):
        if h in (0, 3, 6, 9):       # Kendras: 1, 4, 7, 10 (Baked Terracotta Sand)
            fill_col = "var(--chart-kendra-color, #eedec9)"
            cls = "house-bg house-kendra"
        elif h in (4, 8):           # Trikonas: 5, 9 (Sunlit Apricot Champagne)
            fill_col = "var(--chart-trikona-color, #faede0)"
            cls = "house-bg house-trikona"
        else:                       # Other houses: 2, 3, 6, 8, 11, 12 (Soft Warm Vellum)
            fill_col = "var(--chart-other-color, #f9f5eb)"
            cls = "house-bg house-other"
        svg += f'<path class="{cls}" d="{ni_paths[h]}" fill="{fill_col}"/>\n'

    # Crisp Double Outer Rect (Clean edges, horizontally stretched)
    r1_x = 14 * NORTH_CHART_SCALE_X
    r1_w = 472 * NORTH_CHART_SCALE_X
    r2_x = 18 * NORTH_CHART_SCALE_X
    r2_w = 464 * NORTH_CHART_SCALE_X
    svg += f'<rect x="{r1_x:.1f}" y="14" width="{r1_w:.1f}" height="472" fill="none" stroke="#3e2819" stroke-width="2.2"/>\n'
    svg += f'<rect x="{r2_x:.1f}" y="18" width="{r2_w:.1f}" height="464" fill="none" stroke="#b45309" stroke-width="0.75" stroke-opacity="0.6"/>\n'

    # 4 Diagonal Spines from Corners to Inner Cusp Vertices
    svg += f'<line x1="{18 * NORTH_CHART_SCALE_X:.1f}" y1="18" x2="{148 * NORTH_CHART_SCALE_X:.1f}" y2="148" stroke="#3e2819" stroke-width="1.3" stroke-linecap="round"/>\n'
    svg += f'<line x1="{482 * NORTH_CHART_SCALE_X:.1f}" y1="18" x2="{352 * NORTH_CHART_SCALE_X:.1f}" y2="148" stroke="#3e2819" stroke-width="1.3" stroke-linecap="round"/>\n'
    svg += f'<line x1="{18 * NORTH_CHART_SCALE_X:.1f}" y1="482" x2="{148 * NORTH_CHART_SCALE_X:.1f}" y2="352" stroke="#3e2819" stroke-width="1.3" stroke-linecap="round"/>\n'
    svg += f'<line x1="{482 * NORTH_CHART_SCALE_X:.1f}" y1="482" x2="{352 * NORTH_CHART_SCALE_X:.1f}" y2="352" stroke="#3e2819" stroke-width="1.3" stroke-linecap="round"/>\n'

    # Diagonal Spines from Cusp Vertices to Center
    center_x = 250 * NORTH_CHART_SCALE_X
    svg += f'<line x1="{148 * NORTH_CHART_SCALE_X:.1f}" y1="148" x2="{center_x:.1f}" y2="250" stroke="#3e2819" stroke-width="1.3" stroke-linecap="round"/>\n'
    svg += f'<line x1="{352 * NORTH_CHART_SCALE_X:.1f}" y1="148" x2="{center_x:.1f}" y2="250" stroke="#3e2819" stroke-width="1.3" stroke-linecap="round"/>\n'
    svg += f'<line x1="{148 * NORTH_CHART_SCALE_X:.1f}" y1="352" x2="{center_x:.1f}" y2="250" stroke="#3e2819" stroke-width="1.3" stroke-linecap="round"/>\n'
    svg += f'<line x1="{352 * NORTH_CHART_SCALE_X:.1f}" y1="352" x2="{center_x:.1f}" y2="250" stroke="#3e2819" stroke-width="1.3" stroke-linecap="round"/>\n'

    # Central Lotus Kendra Petals (Convex Belly Splines)
    petals_base = [
        "M 250 19 C 224 55, 150 78, 148 148",
        "M 250 19 C 276 55, 350 78, 352 148",
        "M 19 250 C 55 224, 78 150, 148 148",
        "M 19 250 C 55 276, 78 350, 148 352",
        "M 250 481 C 224 445, 150 422, 148 352",
        "M 250 481 C 276 445, 350 422, 352 352",
        "M 481 250 C 445 224, 422 150, 352 148",
        "M 481 250 C 445 276, 422 350, 352 352"
    ]
    svg += '<g stroke="#3e2819" stroke-width="1.5" fill="none" stroke-linecap="round">\n'
    for pb in petals_base:
        svg += f'  <path d="{_scale_svg_path_x(pb, NORTH_CHART_SCALE_X)}"/>\n'
    svg += '</g>\n'

    # Center Bindu Medallion Ring (Remains a perfect circle, un-distorted!)
    svg += f'<circle cx="{center_x:.1f}" cy="250" r="5" fill="#fffdfa" stroke="#b45309" stroke-width="1.2"/>\n'

    anchor_item = next((it for it in items if it.get("name") == root_planet), None)
    if not anchor_item:
        anchor_item = next((it for it in items if it.get("name") == "Lagna"), None)
    anchor_sign = anchor_item["sign"] if anchor_item else "Aries"
    anchor_index = signs_list.index(anchor_sign)

    # North Indian Geometry:
    # - Kendras: 1, 4, 7, 10 (Strictly H or V across waist, pushed slightly outward; sign/cusp near center medallion)
    # - Outer Triangles: 2, 3, 5, 6, 8, 9, 11, 12 (Strictly H or V along outer border at 44px offset)
    #   Sign (Star) placed in inner corner, Cusp (Square) placed radially outward
    north_house_configs_base = [
        # H1 (Top Kendra) - Horizontal line pushed slightly up (y=144)
        {"type": "kendra", "orientation": "horizontal", "start": (330, 144), "end": (170, 144), "apex": (250, 226), "cusp": (250, 202)},
        # H2 (Outer Triangle) - Horizontal line near top border (y = 44)
        # Sign (Star) at (140, 120), Cusp (Square) above star at (140, 95)
        {"type": "triangle", "orientation": "horizontal", "start": (215, 44),  "end": (65, 44),   "apex": (140, 120), "cusp": (140, 95)},
        # H3 (Outer Triangle) - Vertical line near left border (x = 44)
        # Sign (Star) at (126, 140), Cusp (Square) left of star at (100, 140)
        {"type": "triangle", "orientation": "vertical",   "start": (44, 65),   "end": (44, 215),  "apex": (126, 140), "cusp": (100, 140)},
        # H4 (Left Kendra) - Vertical line pushed slightly left (x=144)
        {"type": "kendra", "orientation": "vertical",   "start": (144, 170), "end": (144, 330), "apex": (226, 250), "cusp": (202, 250)},
        # H5 (Outer Triangle) - Vertical line near left border (x = 44)
        # Sign (Star) at (126, 360), Cusp (Square) left of star at (100, 360)
        {"type": "triangle", "orientation": "vertical",   "start": (44, 285),  "end": (44, 435),  "apex": (126, 360), "cusp": (100, 360)},
        # H6 (Outer Triangle) - Horizontal line near bottom border (y = 456)
        # Sign (Star) at (140, 380), Cusp (Square) below star at (140, 405)
        {"type": "triangle", "orientation": "horizontal", "start": (65, 456),  "end": (215, 456), "apex": (140, 380), "cusp": (140, 405)},
        # H7 (Bottom Kendra) - Horizontal line pushed slightly down (y=356)
        {"type": "kendra", "orientation": "horizontal", "start": (170, 356), "end": (330, 356), "apex": (250, 274), "cusp": (250, 298)},
        # H8 (Outer Triangle) - Horizontal line near bottom border (y = 456)
        # Sign (Star) at (360, 380), Cusp (Square) below star at (360, 405)
        {"type": "triangle", "orientation": "horizontal", "start": (285, 456), "end": (435, 456), "apex": (360, 380), "cusp": (360, 405)},
        # H9 (Outer Triangle) - Vertical line near right border (x = 456)
        # Sign (Star) at (374, 360), Cusp (Square) right of star at (400, 360)
        {"type": "triangle", "orientation": "vertical",   "start": (456, 435), "end": (456, 285), "apex": (374, 360), "cusp": (400, 360)},
        # H10 (Right Kendra) - Vertical line pushed slightly right (x=356)
        {"type": "kendra", "orientation": "vertical",   "start": (356, 330), "end": (356, 170), "apex": (274, 250), "cusp": (298, 250)},
        # H11 (Outer Triangle) - Vertical line near right border (x = 456)
        # Sign (Star) at (374, 140), Cusp (Square) right of star at (400, 140)
        {"type": "triangle", "orientation": "vertical",   "start": (456, 215), "end": (456, 65),  "apex": (374, 140), "cusp": (400, 140)},
        # H12 (Outer Triangle) - Horizontal line near top border (y = 44)
        # Sign (Star) at (360, 120), Cusp (Square) above star at (360, 95)
        {"type": "triangle", "orientation": "horizontal", "start": (435, 44),  "end": (285, 44),  "apex": (360, 120), "cusp": (360, 95)},
    ]
    north_house_configs = []
    for cfg in north_house_configs_base:
        north_house_configs.append({
            "type": cfg["type"],
            "orientation": cfg["orientation"],
            "start": (round(cfg["start"][0] * NORTH_CHART_SCALE_X, 1), cfg["start"][1]),
            "end": (round(cfg["end"][0] * NORTH_CHART_SCALE_X, 1), cfg["end"][1]),
            "apex": (round(cfg["apex"][0] * NORTH_CHART_SCALE_X, 1), cfg["apex"][1]),
            "cusp": (round(cfg["cusp"][0] * NORTH_CHART_SCALE_X, 1), cfg["cusp"][1]),
        })

    # Header label in House 1 if non-Lagna root
    if root_planet != "Lagna":
        badge_title = "Chandra Lagna" if root_planet == "Moon" else ("Surya Lagna" if root_planet == "Sun" else root_planet)
        svg += f'<text x="{center_x:.1f}" y="34" font-family="sans-serif" font-size="11" font-weight="bold" fill="#C0392B" text-anchor="middle">{badge_title}</text>\n'

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
        cusp_font_sz = "10" if is_kendra else "8.5"
        cusp_stroke_w = "2.0" if is_kendra else "1.5"
        
        # Background hit path for interactive sign selection and highlighting
        svg += f'<path class="interactive sign-cell-bg" data-type="sign" data-id="{sign}" data-house="{h + 1}" d="{ni_paths[h]}" fill="transparent" style="cursor: pointer;"><title>House {h + 1} ({sign})</title></path>\n'

        # Draw Sign Glyph (Star position: subtle, delicate 8.5px in outer, 10.5px in kendra)
        sx, sy = cfg["apex"]
        svg += f'<text class="interactive zodiac-line-glyph" data-type="sign" data-id="{sign}" x="{sx}" y="{sy}" font-size="{sign_font_sz}" font-family="{ASTRO_FONT_STACK}" fill="{s_col}" opacity="0.85" font-weight="bold" text-anchor="middle" dominant-baseline="central" style="cursor: pointer; font-variant-emoji: text;">{s_sym}</text>\n'

        house_items = items_by_house[h]
        planets = [it for it in house_items if it["type"] == "planet"]
        cusps = [it for it in house_items if it["type"] == "cusp"]

        # Sort planets by degree within house
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

        # Deterministic equidistant spacing along clear axis (tighter for 3/4 planets in North Indian)
        t_values = get_north_equidistant_t(len(planets_with_deg))

        for idx, (p_deg_val, p) in enumerate(planets_with_deg):
            t = t_values[idx]
            px = p_start_x + (p_end_x - p_start_x) * t
            py = p_start_y + (p_end_y - p_start_y) * t

            # Only for 5+ planets: alternate slight perpendicular shift if crowded
            if len(planets_with_deg) > 4:
                shift = -9 if (idx % 2 == 0) else 9
                if orientation == "horizontal":
                    py += shift
                else:
                    px += shift

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
            font_sz = "13" if (mode == "symbol" and p["name"] != "Lagna") else ("12" if mode == "devanagari" else "11")
            deg_sz = "9"
            retro_sz = "8"
            
            glyph_cls = "graha-glyph" if mode == "symbol" and p["name"] != "Lagna" else ""
            font_fam = ASTRO_FONT_STACK if (mode == "symbol" and p["name"] != "Lagna") else "sans-serif"
                
            dev_name = info.get('dev_full', '')
            is_retro = p.get("is_retrograde", False)
            retro_badge = " R" if is_retro else ""
            retro_label = " [Retrograde (R)]" if is_retro else ""
            tooltip = f"{dev_name} / {info['full_sa']} ({info['full_en']}){retro_label} — {p['deg']}{retro_badge} {p['sign']}"
            
            nak_abbr = get_nakshatra_abbreviation(p.get("nakshatra", ""), length=4) if show_nakshatras else ""
            rect_h = 38 if (show_nakshatras and nak_abbr) else 30
            svg += f'<g class="interactive {glyph_cls}" data-type="planet" data-id="{p["name"]}" style="cursor: pointer;"><title>{tooltip}</title>\n'
            svg += f'<rect class="planet-highlight-bg" fill="none" stroke="none" x="{px - 18:.1f}" y="{py - 11:.1f}" width="36" height="{rect_h}" rx="6"/>\n'
            svg += f'<text class="{glyph_cls}" x="{px}" y="{py - 2}" text-anchor="middle" dominant-baseline="central" font-family="{font_fam}" font-size="{font_sz}" font-weight="bold" fill="{info["color"]}" style="font-variant-emoji: text;">{label}</text>\n'
            svg += f'<text x="{px}" y="{py + 11}" text-anchor="middle" dominant-baseline="central" font-family="sans-serif" font-size="{deg_sz}" font-weight="normal" fill="#5C4433">'
            svg += f'<tspan>{p["deg"]}</tspan>'
            if is_retro:
                svg += f'<tspan font-size="{retro_sz}" font-weight="bold" fill="#C0392B"> R</tspan>'
            svg += '</text>'
            if show_nakshatras and nak_abbr:
                svg += f'\n<text x="{px}" y="{py + 19.5}" text-anchor="middle" dominant-baseline="central" font-family="sans-serif" font-size="5.8" font-weight="500" fill="#8c7b64">{nak_abbr}</text>'
            svg += '</g>\n'
            
            s_idx = signs_list.index(p["sign"])
            p_lon = s_idx * 30 + p_deg_val
            planet_coords[p["name"]] = {"x": px, "y": py, "lon": p_lon, "sign": p["sign"]}

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
                c_tooltip = f"House Cusp {c_num} in {sign}"
                svg += f'<g class="interactive" data-type="house" data-id="{c_num}" style="cursor: pointer;"><title>{c_tooltip}</title>\n'
                svg += f'<text x="{c_x}" y="{c_y}" font-family="sans-serif" font-size="{cusp_font_sz}" font-weight="bold" fill="#7D3C98" text-anchor="middle" dominant-baseline="central">{c_num}</text>\n'
                svg += '</g>\n'
        elif root_planet != "Lagna":
            base_cx, base_cy = cfg["cusp"]
            h_num = h + 1
            h_tooltip = f"House {h_num} from {root_planet} in {sign}"
            col = "#C0392B" if is_kendra else "#7D3C98"
            svg += f'<g class="interactive" data-type="house" data-id="{h_num}" style="cursor: pointer;"><title>{h_tooltip}</title>\n'
            svg += f'<text x="{base_cx}" y="{base_cy}" font-family="sans-serif" font-size="{cusp_font_sz}" font-weight="bold" fill="{col}" text-anchor="middle" dominant-baseline="central">{h_num}</text>\n'
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
                    dignity_map[p_name] = get_dignity(p_name, p_sign, compound, deg, debilitation_mode=debilitation_mode)
                else:
                    dignity_map[p_name] = "Neutral"

    svg += get_aspect_defs_svg()
    svg += render_aspect_lines_group(planet_coords, dignity_map, is_circular=False)

    svg += '</svg>\n'
    return svg

def generate_bhava_chalita_north(bhavas, mode="symbol"):
    svg = f'<svg width="100%" height="100%" viewBox="0 0 {NORTH_CHART_VIEW_W} {NORTH_CHART_VIEW_H}" preserveAspectRatio="xMidYMid meet" xmlns="http://www.w3.org/2000/svg" style="background:transparent;">\n'
    svg += f'<rect width="{NORTH_CHART_VIEW_W}" height="{NORTH_CHART_VIEW_H}" fill="#fffdfa"/>\n'
    r1_x = 14 * NORTH_CHART_SCALE_X
    r1_w = 472 * NORTH_CHART_SCALE_X
    r2_x = 19 * NORTH_CHART_SCALE_X
    r2_w = 462 * NORTH_CHART_SCALE_X
    svg += f'<rect x="{r1_x:.1f}" y="14" width="{r1_w:.1f}" height="472" fill="none" stroke="#3e2819" stroke-width="2.2"/>\n'
    svg += f'<rect x="{r2_x:.1f}" y="19" width="{r2_w:.1f}" height="462" fill="none" stroke="#b45309" stroke-width="0.75" stroke-opacity="0.6"/>\n'

    # 4 Diagonal Spines from Corners to Inner Cusp Vertices
    svg += f'<line x1="{19 * NORTH_CHART_SCALE_X:.1f}" y1="19" x2="{148 * NORTH_CHART_SCALE_X:.1f}" y2="148" stroke="#3e2819" stroke-width="1.3" stroke-linecap="round"/>\n'
    svg += f'<line x1="{481 * NORTH_CHART_SCALE_X:.1f}" y1="19" x2="{352 * NORTH_CHART_SCALE_X:.1f}" y2="148" stroke="#3e2819" stroke-width="1.3" stroke-linecap="round"/>\n'
    svg += f'<line x1="{19 * NORTH_CHART_SCALE_X:.1f}" y1="481" x2="{148 * NORTH_CHART_SCALE_X:.1f}" y2="352" stroke="#3e2819" stroke-width="1.3" stroke-linecap="round"/>\n'
    svg += f'<line x1="{481 * NORTH_CHART_SCALE_X:.1f}" y1="481" x2="{352 * NORTH_CHART_SCALE_X:.1f}" y2="352" stroke="#3e2819" stroke-width="1.3" stroke-linecap="round"/>\n'

    # Diagonal Spines from Cusp Vertices to Center
    center_x = 250 * NORTH_CHART_SCALE_X
    svg += f'<line x1="{148 * NORTH_CHART_SCALE_X:.1f}" y1="148" x2="{center_x:.1f}" y2="250" stroke="#3e2819" stroke-width="1.3" stroke-linecap="round"/>\n'
    svg += f'<line x1="{352 * NORTH_CHART_SCALE_X:.1f}" y1="148" x2="{center_x:.1f}" y2="250" stroke="#3e2819" stroke-width="1.3" stroke-linecap="round"/>\n'
    svg += f'<line x1="{148 * NORTH_CHART_SCALE_X:.1f}" y1="352" x2="{center_x:.1f}" y2="250" stroke="#3e2819" stroke-width="1.3" stroke-linecap="round"/>\n'
    svg += f'<line x1="{352 * NORTH_CHART_SCALE_X:.1f}" y1="352" x2="{center_x:.1f}" y2="250" stroke="#3e2819" stroke-width="1.3" stroke-linecap="round"/>\n'

    # Central Lotus Kendra Petals (Convex Belly Splines)
    petals_base = [
        "M 250 19 C 224 55, 150 78, 148 148",
        "M 250 19 C 276 55, 350 78, 352 148",
        "M 19 250 C 55 224, 78 150, 148 148",
        "M 19 250 C 55 276, 78 350, 148 352",
        "M 250 481 C 224 445, 150 422, 148 352",
        "M 250 481 C 276 445, 350 422, 352 352",
        "M 481 250 C 445 224, 422 150, 352 148",
        "M 481 250 C 445 276, 422 350, 352 352"
    ]
    svg += '<g stroke="#3e2819" stroke-width="1.5" fill="none" stroke-linecap="round">\n'
    for pb in petals_base:
        svg += f'  <path d="{_scale_svg_path_x(pb, NORTH_CHART_SCALE_X)}"/>\n'
    svg += '</g>\n'

    # Center Bindu Medallion Ring
    svg += f'<circle cx="{center_x:.1f}" cy="250" r="5" fill="#fffdfa" stroke="#b45309" stroke-width="1.2"/>\n'
    
    ni_centers_base = [
        (250, 125), (125, 58),  (60, 125),  (125, 250),
        (60, 375),  (125, 442), (250, 375), (375, 442),
        (440, 375), (375, 250), (440, 125), (375, 58)
    ]
    ni_centers = [(cx * NORTH_CHART_SCALE_X, cy) for cx, cy in ni_centers_base]
    
    sign_pos_base = [
        (250, 218), (180, 35),  (35, 180),  (218, 250),
        (35, 320),  (180, 465), (250, 282), (320, 465),
        (465, 320), (282, 250), (465, 180), (320, 35)
    ]
    sign_pos = [(sx * NORTH_CHART_SCALE_X, sy) for sx, sy in sign_pos_base]
    
    ni_paths_base = [
        "M 250 19 C 224 55, 150 78, 148 148 L 250 250 L 352 148 C 350 78, 276 55, 250 19 Z",
        "M 19 19 L 250 19 C 224 55, 150 78, 148 148 L 19 19 Z",
        "M 19 19 L 148 148 C 78 150, 55 224, 19 250 L 19 19 Z",
        "M 19 250 C 55 224, 78 150, 148 148 L 250 250 L 148 352 C 78 350, 55 276, 19 250 Z",
        "M 19 250 C 55 276, 78 350, 148 352 L 19 481 L 19 250 Z",
        "M 19 481 L 148 352 C 150 422, 224 445, 250 481 L 19 481 Z",
        "M 250 481 C 224 445, 150 422, 148 352 L 250 250 L 352 352 C 350 422, 276 445, 250 481 Z",
        "M 250 481 C 276 445, 350 422, 352 352 L 481 481 L 250 481 Z",
        "M 481 481 L 352 352 C 422 350, 445 276, 481 250 L 481 481 Z",
        "M 481 250 C 445 224, 422 150, 352 148 L 250 250 L 352 352 C 422 350, 445 276, 481 250 Z",
        "M 481 19 L 481 250 C 445 224, 422 150, 352 148 L 481 19 Z",
        "M 481 19 L 352 148 C 350 78, 276 55, 250 19 L 481 19 Z"
    ]
    ni_paths = [_scale_svg_path_x(p, NORTH_CHART_SCALE_X) for p in ni_paths_base]
    
    for h_idx in range(12):
        cx, cy = ni_centers[h_idx]
        bhava = bhavas[h_idx]
        
        cusp_lon = bhava["cusp"]
        sign_idx = int(cusp_lon // 30)
        s_sym, s_col, _ = sign_symbols[signs_list[sign_idx]]
        
        svg += f'<path class="interactive sign-cell-bg" data-type="sign" data-id="{signs_list[sign_idx]}" data-house="{h_idx + 1}" d="{ni_paths[h_idx]}" fill="transparent" style="cursor: pointer;"><title>House {h_idx + 1} ({signs_list[sign_idx]})</title></path>\n'
        
        sx, sy = sign_pos[h_idx]
        svg += f'<text class="interactive zodiac-line-glyph" data-type="sign" data-id="{signs_list[sign_idx]}" x="{sx}" y="{sy}" font-size="14" font-family="{ASTRO_FONT_STACK}" fill="{s_col}" opacity="0.85" font-weight="bold" text-anchor="middle" dominant-baseline="central" style="cursor: pointer; font-variant-emoji: text;">{s_sym}</text>\n'

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
            glyph_cls = "graha-glyph" if mode == "symbol" and p_name != "Lagna" else ""
            font_fam = ASTRO_FONT_STACK if (mode == "symbol" and p_name != "Lagna") else "sans-serif"
            font_sz = "20" if (mode == "symbol" and p_name != "Lagna") else ("16" if mode == "devanagari" else "14")
            tooltip = f"{info['full_sa']} ({info['full_en']})"
            
            svg += f'<g class="interactive {glyph_cls}" data-type="planet" data-id="{p_name}" style="cursor: pointer;"><title>{tooltip}</title>\n'
            svg += f'<rect class="planet-highlight-bg" fill="none" stroke="none" x="{cx - 15:.1f}" y="{curr_y - 12:.1f}" width="30" height="24" rx="4"/>\n'
            svg += f'<text class="{glyph_cls}" x="{cx}" y="{curr_y}" text-anchor="middle" dominant-baseline="central" font-family="{font_fam}" font-size="{font_sz}" font-weight="bold" fill="{info["color"]}" style="font-variant-emoji: text;">{label}</text></g>\n'
            curr_y += item_height

    svg += get_aspect_defs_svg()
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

def generate_circular_chart(items, mode="symbol", varga_name="D1", ayanamsha=0, root_planet="Lagna", debilitation_mode: str = "kala_degree"):
    svg = '<svg width="100%" height="100%" viewBox="-210 -210 420 420" class="aspects-hidden" preserveAspectRatio="xMidYMid meet" xmlns="http://www.w3.org/2000/svg" style="background:transparent; font-family: sans-serif;">\n'
    
    # SVG Defs for Astro Fonts
    svg += '<defs>\n'
    svg += '  <style>\n'
    svg += '    .zodiac-line-glyph, .natal-sign-glyph, .outer-sign-glyph, .sub-sign-symbol, .glyph-symbol, .graha-glyph {\n'
    svg += f'      font-family: var(--font-astro-glyphs, {ASTRO_FONT_STACK}) !important;\n'
    svg += '      font-variant-emoji: text !important;\n'
    svg += '    }\n'
    svg += '  </style>\n'
    svg += '</defs>\n'
    
    r_nak_outer = 200
    r_nak_inner = 175
    r_rasi_inner = 155
    r_bhava_outer = 46
    r_bhava_inner = 30
    
    root_title = "Chandra Lagna" if root_planet == "Moon" else ("Surya Lagna" if root_planet == "Sun" else "Circular Chart")
    svg += f'<title>{varga_name} {root_title}</title>\n'
    
    # Outer circuits
    circle_stroke = "0.7"
    svg += f'<circle cx="0" cy="0" r="{r_nak_outer}" fill="none" stroke="#5C4433" stroke-width="{circle_stroke}"/>\n'
    svg += f'<circle cx="0" cy="0" r="{r_nak_inner}" fill="none" stroke="#5C4433" stroke-width="{circle_stroke}"/>\n'
    svg += f'<circle cx="0" cy="0" r="{r_rasi_inner}" fill="none" stroke="#5C4433" stroke-width="{circle_stroke}"/>\n'
    
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
        angle_end = lon_to_angle(start_lon + 30.0)
        angle_mid = lon_to_angle(start_lon + 15.0)
        bhava_num = (i - anchor_s_idx + 12) % 12 + 1
        
        # Permanent Harmonious House Color Fills (Kendras 1,4,7,10 | Trikonas 5,9 | Other Houses)
        if bhava_num in (1, 4, 7, 10):
            fill_col = "var(--chart-kendra-color, #eedec9)"
            cls = "house-bg house-kendra"
        elif bhava_num in (5, 9):
            fill_col = "var(--chart-trikona-color, #faede0)"
            cls = "house-bg house-trikona"
        else:
            fill_col = "var(--chart-other-color, #f9f5eb)"
            cls = "house-bg house-other"

        # House Annular Sector Wedge spanning from r_bhava_inner to r_rasi_inner
        sec_d = annular_sector(r_bhava_inner, r_rasi_inner, angle_start, angle_end)
        svg += f'<path class="{cls}" d="{sec_d}" fill="{fill_col}"/>\n'

        # Draw Rasi separator line
        x1, y1 = polar_coords(r_rasi_inner, angle_start)
        x2, y2 = polar_coords(r_nak_inner, angle_start)
        svg += f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#5C4433" stroke-width="1"/>\n'
        
        # Whole House boundaries (Bhavas) - Green dense dashed line
        x3, y3 = polar_coords(r_bhava_outer, angle_start)
        x4, y4 = polar_coords(r_rasi_inner, angle_start)
        svg += f'<line x1="{x3:.1f}" y1="{y3:.1f}" x2="{x4:.1f}" y2="{y4:.1f}" stroke="#27AE60" stroke-width="0.8" stroke-dasharray="3,2"/>\n'
        
        # Bhava inner circle separator across the house number ring
        x5, y5 = polar_coords(r_bhava_inner, angle_start)
        x6, y6 = polar_coords(r_bhava_outer, angle_start)
        svg += f'<line x1="{x5:.1f}" y1="{y5:.1f}" x2="{x6:.1f}" y2="{y6:.1f}" stroke="#000000" stroke-width="0.8"/>\n'
        
        # Rasi symbol label
        lx, ly = polar_coords( (r_rasi_inner + r_nak_inner)/2, angle_mid)
        sign_name = signs_list[i]
        s_sym, s_col, _ = sign_symbols[sign_name]
        svg += f'<text class="interactive" data-type="sign" data-id="{sign_name}" x="{lx:.1f}" y="{ly:.1f}" font-size="14" fill="{s_col}" text-anchor="middle" dominant-baseline="central" style="cursor: pointer;">{s_sym}</text>\n'

        # Bhava number label (Whole Sign) in the middle of the bhava ring (r=38)
        bx, by = polar_coords( (r_bhava_inner + r_bhava_outer)/2, angle_mid)
        svg += f'<text class="interactive" data-type="house" data-id="{bhava_num}" x="{bx:.1f}" y="{by:.1f}" font-size="9.0" font-weight="600" fill="#2980B9" text-anchor="middle" dominant-baseline="central" style="cursor: pointer;">{bhava_num}</text>\n'

    # Bhava outer separating circle and inner center circle
    svg += f'<circle cx="0" cy="0" r="{r_bhava_outer}" fill="none" stroke="#27AE60" stroke-width="{circle_stroke}"/>\n'
    svg += f'<circle class="interactive-center-circle" cx="0" cy="0" r="{r_bhava_inner}" fill="#faf7f0" fill-opacity="0.95" stroke="#5C4433" stroke-width="0.8" style="cursor: pointer;"><title>Click to clear filter</title></circle>\n'
    svg += f'<text x="0" y="0" font-size="8.5" font-weight="bold" fill="#4a3325" text-anchor="middle" dominant-baseline="central" pointer-events="none">{varga_name}</text>\n'

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
                    dignity_map[p_name] = get_dignity(p_name, sign, compound, deg, debilitation_mode=debilitation_mode)
                else:
                    dignity_map[p_name] = "Neutral"

    # Relaxation for overlap with strictly preserved cyclic order
    relax_planet_angles(planets_to_draw, has_ascendant_barrier=True, is_outer=False)

    # 6. Planets (radially stacked, without redundant sign symbol)
    r_pl_base = r_rasi_inner - 10 # 145

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
        mid_x, mid_y = polar_coords(r_rasi_inner - 20.5, angle)
        svg += f'<circle class="planet-highlight-bg" fill="none" stroke="none" cx="{mid_x:.1f}" cy="{mid_y:.1f}" r="17"/>\n'

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


def generate_biwheel_chart(inner_items, outer_items, inner_name="D1", outer_name="D9", mode="symbol", ayanamsha=0, root_planet="Lagna", debilitation_mode: str = "kala_degree", show_nakshatras: bool = False):
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
    r_bhava_circle = 44
    r_aspect_inner = 28
    
    root_title = "Chandra Lagna" if root_planet == "Moon" else ("Surya Lagna" if root_planet == "Sun" else "Ascendant")
    svg += f'<title>{inner_name} / {outer_name} Harmonic Bi-Wheel ({root_title})</title>\n'
    
    # Outer bounding circle & tinted background for outer harmonic planet ring
    svg += f'<circle cx="0" cy="0" r="{r_chart_outer}" fill="#faf7f2" fill-opacity="0.25" stroke="#5C4433" stroke-width="1.0"/>\n'
    
    # Harmonic subdivision ring background band & concentric borders
    svg += f'<circle cx="0" cy="0" r="{r_divider_outer}" fill="#edece6" fill-opacity="0.65" stroke="#8c7b64" stroke-width="1.2"/>\n'
    svg += f'<circle cx="0" cy="0" r="{r_divider_inner}" fill="#ffffff" fill-opacity="0.95" stroke="#8c7b64" stroke-width="1.2"/>\n'
    
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
        angle_end = lon_to_angle(sign_start_lon + 30.0)
        angle_mid = lon_to_angle(sign_start_lon + 15.0)
        sign_name = signs_list[i]
        s_sym, s_col, _ = sign_symbols[sign_name]
        bhava_num = (i - anchor_s_idx + 12) % 12 + 1

        # Inner Natal House Color Fills (Kendras 1,4,7,10 | Trikonas 5,9 | Other Houses)
        if bhava_num in (1, 4, 7, 10):
            fill_col = "var(--chart-kendra-color, #eedec9)"
            cls = "house-bg house-kendra"
        elif bhava_num in (5, 9):
            fill_col = "var(--chart-trikona-color, #faede0)"
            cls = "house-bg house-trikona"
        else:
            fill_col = "var(--chart-other-color, #f9f5eb)"
            cls = "house-bg house-other"

        # Inner Natal House Annular Sector Wedge (r_aspect_inner to r_divider_inner)
        sec_d = annular_sector(r_aspect_inner, r_divider_inner, angle_start, angle_end)
        svg += f'<path class="{cls}" d="{sec_d}" fill="{fill_col}"/>\n'

        # Natal sign divider extending inward across inner ring (r_aspect_inner to r_divider_inner)
        x_in1, y_in1 = polar_coords(r_aspect_inner, angle_start)
        x_in2, y_in2 = polar_coords(r_divider_inner, angle_start)
        svg += f'<line x1="{x_in1:.1f}" y1="{y_in1:.1f}" x2="{x_in2:.1f}" y2="{y_in2:.1f}" stroke="#d5c8b2" stroke-width="0.8" stroke-dasharray="2,3"/>\n'
        
        # Outer sign divider extending outward across outer comparison ring (r_divider_outer to r_chart_outer)
        x_out1, y_out1 = polar_coords(r_divider_outer, angle_start)
        x_out2, y_out2 = polar_coords(r_chart_outer, angle_start)
        svg += f'<line x1="{x_out1:.1f}" y1="{y_out1:.1f}" x2="{x_out2:.1f}" y2="{y_out2:.1f}" stroke="#d5c8b2" stroke-width="0.8" stroke-dasharray="2,3"/>\n'

        # Central Zodiac Sign Symbol inside Border Ring (midpoint between 138 and 164 -> r=151)
        lx_sign, ly_sign = polar_coords(151, angle_mid)
        svg += f'<text class="interactive natal-sign-glyph" data-type="sign" data-id="{sign_name}" x="{lx_sign:.1f}" y="{ly_sign:.1f}" font-size="11.5" stroke="#ffffff" stroke-width="2.2" paint-order="stroke fill" fill="{s_col}" text-anchor="middle" dominant-baseline="central" style="cursor: pointer;"><title>{sign_name} (Zodiac Sign)</title>{s_sym}</text>\n'
        
        # Bhava number label (Whole Sign) in the inner bhava ring (radius ~36)
        bx, by = polar_coords((r_aspect_inner + r_bhava_circle) / 2, angle_mid)
        svg += f'<text class="interactive" data-type="house" data-id="{bhava_num}" x="{bx:.1f}" y="{by:.1f}" font-size="8.5" font-weight="600" stroke="#FAF7F0" stroke-width="2.0" paint-order="stroke fill" fill="#2980B9" text-anchor="middle" dominant-baseline="central" style="cursor: pointer;">{bhava_num}</text>\n'

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

    # Inner D1 Bhava dashed circle
    svg += f'<circle cx="0" cy="0" r="{r_bhava_circle}" fill="none" stroke="#27AE60" stroke-width="0.6" stroke-dasharray="3,2"/>\n'
    
    # Aspect boundary interactive center circle
    svg += f'<circle class="interactive-center-circle" cx="0" cy="0" r="{r_aspect_inner}" fill="#faf7f0" fill-opacity="0.95" stroke="#5C4433" stroke-width="0.8" style="cursor: pointer;"><title>Click to clear filter</title></circle>\n'
    
    # Center text labels
    svg += f'<text x="0" y="-4.5" font-size="7.5" font-weight="bold" fill="#4a3325" text-anchor="middle" pointer-events="none">{inner_name} · {outer_name}</text>\n'
    svg += f'<text x="0" y="6" font-size="6.0" font-weight="600" fill="#8c7b64" text-anchor="middle" pointer-events="none">Bi-Wheel</text>\n'

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
                    dignity_map[p_name] = get_dignity(p_name, sign, compound, deg, debilitation_mode=debilitation_mode)
                else:
                    dignity_map[p_name] = "Neutral"

    # Relaxation for overlap with strictly preserved cyclic order
    relax_planet_angles(inner_planets, has_ascendant_barrier=True, is_outer=False)
    relax_planet_angles(outer_planets, has_ascendant_barrier=False, is_outer=True)

    # 4. Radial Degree Alignment Projection Rays, Leader Lines & Alignment Dots
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
    if show_nakshatras:
        r_in_nak = 76
        r_in_min = 89
        r_in_deg = 100
        r_in_pl = 112
    else:
        r_in_min = 74
        r_in_deg = 90
        r_in_pl = 112

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

        font_sz = 7.5 if p_name == "Lagna" else (10.0 if mode == "devanagari" else 9.5)
        if mode == "symbol" and p_name in ["Mars", "Venus"]:
            font_sz = 8.0
        
        dignity_str = dignity_map.get(p_name, "")
        dignity_tag = f" [{dignity_str}]" if dignity_str else ""
        tooltip = f"Natal ({inner_name}) {info.get('full_sa', p_name)}{dignity_tag} — {item['degree']}° {item['minute']:02d}'{retro_badge} in {item['sign']}"
        
        svg += f'<g class="interactive planet-glyph inner-planet" data-type="planet" data-varga="{inner_name}" data-id="{p_name}" style="cursor: pointer;"><title>{tooltip}</title>\n'
        mid_r = 94.0 if show_nakshatras else 93.0
        hl_r = 24 if show_nakshatras else 22
        mid_x, mid_y = polar_coords(mid_r, angle)
        svg += f'<circle class="planet-highlight-bg" fill="none" stroke="none" cx="{mid_x:.1f}" cy="{mid_y:.1f}" r="{hl_r}"/>\n'

        # Nakshatra text (towards inner circle)
        if show_nakshatras:
            nak_abbr = get_nakshatra_abbreviation(item.get("nakshatra", ""), length=4)
            if nak_abbr:
                nx, ny = polar_coords(r_in_nak, angle)
                svg += f'<text x="{nx}" y="{ny}" font-size="5.2" font-weight="500" stroke="#F7F3EB" stroke-width="0.8" paint-order="stroke" stroke-linejoin="round" fill="#8c7b64" text-anchor="middle" dominant-baseline="central">{nak_abbr}</text>\n'

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

        font_sz = 6.8 if p_name == "Lagna" else (9.5 if mode == "devanagari" else 9.0)
        if mode == "symbol" and p_name in ["Mars", "Venus"]:
            font_sz = 7.8
            
        # Natal House alignment
        d1_house = ((p["sign_idx"] - anchor_s_idx + 12) % 12) + 1
        tooltip = f"{outer_name} {info.get('full_sa', p_name)} in {item['sign']} {item['degree']}° {item['minute']:02d}'{retro_badge} (Natal House {d1_house})"
        
        # Divisional Sign symbol and color for outer planet
        s_sym, s_col, _ = sign_symbols.get(item["sign"], ("?", "#000", "?"))
        
        svg += f'<g class="interactive planet-glyph outer-planet" data-type="planet" data-varga="{outer_name}" data-id="{p_name}" style="cursor: pointer;"><title>{tooltip}</title>\n'
        mid_x, mid_y = polar_coords(180.0, angle)
        svg += f'<circle class="planet-highlight-bg" fill="none" stroke="none" cx="{mid_x:.1f}" cy="{mid_y:.1f}" r="14"/>\n'

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
        svg += f'<text class="outer-sign-glyph" x="{sx}" y="{sy}" font-size="5.5" stroke="#FAF6F0" stroke-width="0.9" paint-order="stroke" stroke-linejoin="round" fill="{s_col}" font-weight="bold" text-anchor="middle" dominant-baseline="central">{s_sym}</text>\n'
        
        svg += '</g>\n'
    svg += '</g>\n'

    svg += '</svg>\n'
    return svg


def generate_transit_biwheel(
    inner_items: List[Dict[str, Any]],
    outer_items: List[Dict[str, Any]],
    active_aspects: Optional[List[Dict[str, Any]]] = None,
    mode: str = "symbol",
    root_planet: str = "Lagna",
    show_nakshatras: bool = False,
    debilitation_mode: str = "kala_degree"
) -> str:
    """
    Generates a streamlined 2-ring Transit Bi-Wheel SVG chart (Kala style):
    - Inner Ring (Radius ~30 to ~136): Natal Chart (Houses 1-12, Kendras/Trikonas, Natal Planets).
    - Inner Dots (Radius 136): Exact astronomical positions of natal planets on the Rashi circle.
    - Middle Zodiac Ring (Radius ~136 to ~150): Clean Tropical Rasi border WITHOUT harmonic subdivisions.
    - Outer Ring (Radius ~150 to ~206): Real-time / Date-specific Transiting Planets with sign & degree.
    - Outer Dots (Radius 206): Exact astronomical positions of transiting planets on the outer rim.
    - Background Aspect Lines: Thin, clear lines connecting outer transit dots to inner natal dots (Graha Drishti & Trines).
    - Center Hub (Radius 0 to ~30): Unobstructed center hub with subtle branding.
    """
    svg = '<svg width="100%" height="100%" viewBox="-215 -215 430 430" class="transit-biwheel-svg" preserveAspectRatio="xMidYMid meet" xmlns="http://www.w3.org/2000/svg" style="background:transparent; font-family: var(--font-astro-glyphs, STIX Two Math, sans-serif);">\n'

    # Markers for transit aspect lines (pointing cleanly towards the inner natal dots)
    svg += '<defs>\n'
    svg += '  <marker id="tr-arrow-benefic" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="4.5" markerHeight="4.5" orient="auto"><path d="M 0 2 L 8 5 L 0 8 z" fill="#27AE60"/></marker>\n'
    svg += '  <marker id="tr-arrow-amber" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="4.5" markerHeight="4.5" orient="auto"><path d="M 0 2 L 8 5 L 0 8 z" fill="#D4AC0D"/></marker>\n'
    svg += '  <marker id="tr-arrow-malefic" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="4.5" markerHeight="4.5" orient="auto"><path d="M 0 2 L 8 5 L 0 8 z" fill="#C0392B"/></marker>\n'
    svg += '  <marker id="tr-arrow-conj" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="4.5" markerHeight="4.5" orient="auto"><path d="M 0 2 L 8 5 L 0 8 z" fill="#8E44AD"/></marker>\n'
    svg += '  <marker id="tr-arrow-neutral" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="4.5" markerHeight="4.5" orient="auto"><path d="M 0 2 L 8 5 L 0 8 z" fill="#2980B9"/></marker>\n'
    svg += '</defs>\n'

    r_chart_outer = 206
    r_divider_outer = 150
    r_divider_inner = 136
    r_bhava_circle = 44
    r_aspect_inner = 30

    root_title = "Chandra Lagna" if root_planet == "Moon" else ("Surya Lagna" if root_planet == "Sun" else "Ascendant")
    svg += f'<title>Transit / Natal Bi-Wheel ({root_title})</title>\n'

    # Outer bounding circle & tinted background for outer transit ring
    svg += f'<circle cx="0" cy="0" r="{r_chart_outer}" fill="#faf7f2" fill-opacity="0.20" stroke="#5C4433" stroke-width="1.1"/>\n'

    # Middle Zodiac Sign border ring (clean, no harmonic subdivisions)
    svg += f'<circle cx="0" cy="0" r="{r_divider_outer}" fill="#edece6" fill-opacity="0.75" stroke="#8c7b64" stroke-width="1.1"/>\n'
    svg += f'<circle cx="0" cy="0" r="{r_divider_inner}" fill="#ffffff" fill-opacity="0.95" stroke="#8c7b64" stroke-width="1.1"/>\n'

    # Determine anchor longitude
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

    # 1. Extract and Process Planets First (so angles and aspect endpoints are known)
    inner_planets = []
    inner_planets_dict = {}
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
                "varga": "Natal"
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
            outer_angle = lon_to_angle(pl_lon)
            p_data = {
                "item": item,
                "lon": pl_lon,
                "draw_angle": outer_angle,
                "true_angle": outer_angle,
                "is_lagna": (p_name == root_planet),
                "sign_idx": s_idx,
                "sign": item["sign"],
                "varga": "Transit"
            }
            outer_planets.append(p_data)
            outer_planets_dict[p_name] = p_data

    # Relax angles for overlapping clusters (to prevent text collision)
    relax_planet_angles(inner_planets, has_ascendant_barrier=True, is_outer=False)
    relax_planet_angles(outer_planets, has_ascendant_barrier=False, is_outer=True)

    # 2. Inner Natal House Color Background Wedges (Kendras, Trikonas, Other Houses)
    for i in range(12):
        sign_start_lon = i * 30.0
        angle_start = lon_to_angle(sign_start_lon)
        angle_end = lon_to_angle(sign_start_lon + 30.0)
        bhava_num = (i - anchor_s_idx + 12) % 12 + 1

        if bhava_num in (1, 4, 7, 10):
            fill_col = "var(--chart-kendra-color, #eedec9)"
            cls = "house-bg house-kendra"
        elif bhava_num in (5, 9):
            fill_col = "var(--chart-trikona-color, #faede0)"
            cls = "house-bg house-trikona"
        else:
            fill_col = "var(--chart-other-color, #f9f5eb)"
            cls = "house-bg house-other"

        sec_d = annular_sector(r_aspect_inner, r_divider_inner, angle_start, angle_end)
        svg += f'<path class="{cls}" d="{sec_d}" fill="{fill_col}"/>\n'

    # 3. BACKGROUND LAYER: Aspect Lines connecting Outer Transit Dots to Inner Natal Dots
    # Rendered immediately on top of house colors, strictly behind all dividers, numbers, text & dots
    svg += '<g class="transit-aspect-lines-layer" style="pointer-events: none;">\n'
    if active_aspects:
        for asp in active_aspects:
            t_name = asp.get("aspecting")
            n_name = asp.get("target")
            asp_type = asp.get("type", "Aspect")
            orb = asp.get("orb", 0.0)
            is_ben = asp.get("is_benefic", False)
            code = asp.get("code", "")

            if t_name in outer_planets_dict and n_name in inner_planets_dict:
                ang_t = outer_planets_dict[t_name]["true_angle"]
                ang_n = inner_planets_dict[n_name]["true_angle"]

                # Start: Exact Outer transit dot on r_chart_outer (206)
                # End: Exact Inner natal dot on r_divider_inner (136)
                x1, y1 = polar_coords(r_chart_outer, ang_t)
                x2, y2 = polar_coords(r_divider_inner, ang_n)

                dash_style = "4,3"
                marker_url = ""
                if code == "CONJ":
                    stroke_col = "#8E44AD"
                    dash_style = "none"
                elif "Trine" in asp_type or (is_ben and t_name == "Jupiter"):
                    # Trines: clean dashed warm gold line connecting dots
                    stroke_col = "#D4AC0D"
                    dash_style = "4,3"
                elif t_name == "Mars":
                    # Mars special aspects / glances: crisp red with directional arrow
                    stroke_col = "#C0392B"
                    marker_url = 'marker-end="url(#tr-arrow-malefic)"'
                    dash_style = "3.5,2.5"
                elif t_name == "Saturn":
                    # Saturn special aspects: deep slate with arrow
                    stroke_col = "#2C3E50"
                    marker_url = 'marker-end="url(#tr-arrow-neutral)"'
                    dash_style = "3.5,2.5"
                elif is_ben:
                    stroke_col = "#27AE60"
                    marker_url = 'marker-end="url(#tr-arrow-benefic)"'
                    dash_style = "4,3"
                else:
                    stroke_col = "#C0392B"
                    marker_url = 'marker-end="url(#tr-arrow-malefic)"'
                    dash_style = "4,3"

                tip = f"Transit {t_name} -> Natal {n_name} ({asp_type}, Orb: {orb}°)"
                svg += f'  <line class="transit-aspect-line aspect-tr-{t_name} aspect-nat-{n_name}" data-from="{t_name}" data-to="{n_name}" x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke_col}" stroke-width="0.9" stroke-dasharray="{dash_style}" opacity="0.75" {marker_url}><title>{tip}</title></line>\n'
    svg += '</g>\n'

    # 4. House Dividers, Sign Glyphs, Bhava Numbers, and Ascendant Arrow
    for i in range(12):
        sign_start_lon = i * 30.0
        angle_start = lon_to_angle(sign_start_lon)
        angle_mid = lon_to_angle(sign_start_lon + 15.0)
        sign_name = signs_list[i]
        s_sym, s_col, _ = sign_symbols[sign_name]
        bhava_num = (i - anchor_s_idx + 12) % 12 + 1

        # Radial sign dividers
        x_in1, y_in1 = polar_coords(r_aspect_inner, angle_start)
        x_in2, y_in2 = polar_coords(r_divider_inner, angle_start)
        svg += f'<line x1="{x_in1:.1f}" y1="{y_in1:.1f}" x2="{x_in2:.1f}" y2="{y_in2:.1f}" stroke="#d5c8b2" stroke-width="0.8" stroke-dasharray="2,3"/>\n'

        x_out1, y_out1 = polar_coords(r_divider_outer, angle_start)
        x_out2, y_out2 = polar_coords(r_chart_outer, angle_start)
        svg += f'<line x1="{x_out1:.1f}" y1="{y_out1:.1f}" x2="{x_out2:.1f}" y2="{y_out2:.1f}" stroke="#d5c8b2" stroke-width="0.8" stroke-dasharray="2,3"/>\n'

        # Sign boundary tick in the border ring (r_divider_inner to r_divider_outer)
        sx1, sy1 = polar_coords(r_divider_inner, angle_start)
        sx2, sy2 = polar_coords(r_divider_outer, angle_start)
        svg += f'<line x1="{sx1:.1f}" y1="{sy1:.1f}" x2="{sx2:.1f}" y2="{sy2:.1f}" stroke="#5C4433" stroke-width="1.2"/>\n'

        # Sign Symbol in Border Ring (midpoint between 136 and 150 -> r=143)
        lx_sign, ly_sign = polar_coords(143, angle_mid)
        svg += f'<text class="interactive transit-sign-glyph" data-type="sign" data-id="{sign_name}" x="{lx_sign:.1f}" y="{ly_sign:.1f}" font-size="12" stroke="#ffffff" stroke-width="2.0" paint-order="stroke fill" fill="{s_col}" text-anchor="middle" dominant-baseline="central"><title>{sign_name} (Zodiac Sign)</title>{s_sym}</text>\n'

        # Bhava number label in inner ring (haloed for legibility over lines)
        bx, by = polar_coords((r_aspect_inner + r_bhava_circle) / 2, angle_mid)
        svg += f'<text class="interactive" data-type="house" data-id="{bhava_num}" x="{bx:.1f}" y="{by:.1f}" font-size="8.5" font-weight="600" stroke="#FAF7F0" stroke-width="2.5" paint-order="stroke fill" fill="#2980B9" text-anchor="middle" dominant-baseline="central">{bhava_num}</text>\n'

    # Inner D1 Bhava dashed circle
    svg += f'<circle cx="0" cy="0" r="{r_bhava_circle}" fill="none" stroke="#27AE60" stroke-width="0.6" stroke-dasharray="3,2"/>\n'

    # Ascendant arrow at 180 degrees
    ax1, ay1 = polar_coords(r_aspect_inner, 180)
    ax2, ay2 = polar_coords(r_divider_inner, 180)
    svg += f'<line x1="{ax1:.1f}" y1="{ay1:.1f}" x2="{ax2:.1f}" y2="{ay2:.1f}" stroke="#C0392B" stroke-width="1.6"/>\n'
    tx1, ty1 = polar_coords(r_divider_inner - 5, 177.5)
    tx2, ty2 = polar_coords(r_divider_inner - 5, 182.5)
    svg += f'<polygon points="{ax2:.1f},{ay2:.1f} {tx1:.1f},{ty1:.1f} {tx2:.1f},{ty2:.1f}" fill="#C0392B"/>\n'

    # 5. Center Circle Hub (Radius 30)
    svg += f'<circle class="interactive-center-circle" cx="0" cy="0" r="{r_aspect_inner}" fill="#faf7f0" fill-opacity="0.95" stroke="#5C4433" stroke-width="0.8"/>\n'
    svg += '<text x="0" y="-4.5" font-size="6.8" font-weight="bold" fill="#4a3325" text-anchor="middle" pointer-events="none">Natal · Transit</text>\n'
    svg += '<text x="0" y="5.5" font-size="5.5" font-weight="600" fill="#8c7b64" text-anchor="middle" pointer-events="none">Bi-Wheel</text>\n'

    # 6. INNER DOTS & LEADER LINES: Exact Position of Natal Planets on the Rashi Circle (r = 136)
    svg += '<g class="natal-dots-layer">\n'
    for p in inner_planets:
        p_name = p["item"]["name"]
        ang_true = p["true_angle"]
        ang_draw = p["draw_angle"]
        p_info = planet_notations.get(p_name, {})
        dot_col = p_info.get("color", "#4a3325")

        # Inner Dot on the Rashi boundary circle (r = 136)
        dx, dy = polar_coords(r_divider_inner, ang_true)
        tip = f"Natal {p_name} exact position: {p['item']['degree']}° {p['item']['minute']:02d}' {p['sign']}"
        svg += f'  <circle class="natal-planet-dot dot-natal-{p_name}" data-planet="{p_name}" cx="{dx:.1f}" cy="{dy:.1f}" r="2.8" fill="{dot_col}" stroke="#ffffff" stroke-width="0.8"><title>{tip}</title></circle>\n'

        # Subtle leader line / tick connecting glyph cluster out to the exact dot
        ang_diff = abs((ang_draw - ang_true + 180.0) % 360.0 - 180.0)
        if ang_diff > 0.5:
            gx, gy = polar_coords(118, ang_draw)
            svg += f'  <line class="natal-leader-line" x1="{gx:.1f}" y1="{gy:.1f}" x2="{dx:.1f}" y2="{dy:.1f}" stroke="{dot_col}" stroke-width="0.75" stroke-dasharray="1.5,1.5" opacity="0.55"/>\n'
        else:
            gx, gy = polar_coords(121, ang_true)
            svg += f'  <line class="natal-leader-line" x1="{gx:.1f}" y1="{gy:.1f}" x2="{dx:.1f}" y2="{dy:.1f}" stroke="{dot_col}" stroke-width="0.75" stroke-dasharray="1.5,1.5" opacity="0.45"/>\n'
    svg += '</g>\n'

    # 7. OUTER DOTS & LEADER LINES: Exact Position of Transit Planets on the Outer Rim (r = 206)
    svg += '<g class="transit-dots-layer">\n'
    for p in outer_planets:
        p_name = p["item"]["name"]
        ang_true = p["true_angle"]
        ang_draw = p["draw_angle"]
        p_info = planet_notations.get(p_name, {})
        dot_col = p_info.get("color", "#4a3325")

        # Outer Dot on the chart rim (r = 206)
        dx, dy = polar_coords(r_chart_outer, ang_true)
        tip = f"Transit {p_name} exact position: {p['item']['degree']}° {p['item']['minute']:02d}' {p['sign']}"
        svg += f'  <circle class="transit-planet-dot dot-tr-{p_name}" data-planet="{p_name}" cx="{dx:.1f}" cy="{dy:.1f}" r="2.8" fill="{dot_col}" stroke="#ffffff" stroke-width="0.8"><title>{tip}</title></circle>\n'

        # Subtle leader line / tick connecting transit glyph cluster out to the exact rim dot
        ang_diff = abs((ang_draw - ang_true + 180.0) % 360.0 - 180.0)
        if ang_diff > 0.5:
            gx, gy = polar_coords(172, ang_draw)
            svg += f'  <line class="transit-leader-line" x1="{gx:.1f}" y1="{gy:.1f}" x2="{dx:.1f}" y2="{dy:.1f}" stroke="{dot_col}" stroke-width="0.75" stroke-dasharray="1.5,1.5" opacity="0.55"/>\n'
        else:
            gx, gy = polar_coords(195, ang_true)
            svg += f'  <line class="transit-leader-line" x1="{gx:.1f}" y1="{gy:.1f}" x2="{dx:.1f}" y2="{dy:.1f}" stroke="{dot_col}" stroke-width="0.75" stroke-dasharray="1.5,1.5" opacity="0.45"/>\n'
    svg += '</g>\n'

    # 7. INNER RING: Natal Planets Text & Glyphs (Haloed for crisp readability over lines)
    r_in_nak = 70
    r_in_min = 82
    r_in_deg = 96
    r_in_pl = 112

    svg += '<g class="inner-planets-group">\n'
    for p in inner_planets:
        item = p["item"]
        angle = p["draw_angle"]
        p_name = item["name"]
        info = planet_notations.get(p_name, {})
        label = info.get(mode, info.get("symbol", p_name[:2]))
        color = info.get("color", "#000")
        is_retro = item.get("is_retrograde", False)

        px, py = polar_coords(r_in_pl, angle)
        font_sz = 9.0 if p_name == "Lagna" else (12.0 if mode == "devanagari" else 11.5)

        tooltip = f"Natal {info.get('full_sa', p_name)}: {item['degree']}° {item['minute']:02d}' in {item['sign']}"
        svg += f'<g class="interactive planet-glyph inner-planet" data-type="planet" data-varga="Natal" data-id="{p_name}" style="cursor: pointer;"><title>{tooltip}</title>\n'

        if show_nakshatras:
            nak_abbr = get_nakshatra_abbreviation(item.get("nakshatra", ""), length=4)
            if nak_abbr:
                nx, ny = polar_coords(r_in_nak, angle)
                svg += f'<text x="{nx:.1f}" y="{ny:.1f}" font-size="5.2" stroke="#FAF7F0" stroke-width="1.8" paint-order="stroke fill" fill="#8c7b64" text-anchor="middle" dominant-baseline="central">{nak_abbr}</text>\n'

        mx, my = polar_coords(r_in_min, angle)
        svg += f'<text x="{mx:.1f}" y="{my:.1f}" font-size="5.6" stroke="#FAF7F0" stroke-width="1.8" paint-order="stroke fill" fill="{color}" text-anchor="middle" dominant-baseline="central">{item["minute"]:02d}\'{" R" if is_retro else ""}</text>\n'

        dx, dy = polar_coords(r_in_deg, angle)
        svg += f'<text x="{dx:.1f}" y="{dy:.1f}" font-size="6.5" stroke="#FAF7F0" stroke-width="2.0" paint-order="stroke fill" fill="{color}" text-anchor="middle" dominant-baseline="central">{item["degree"]}°</text>\n'

        svg += f'<text class="glyph-symbol" x="{px:.1f}" y="{py:.1f}" font-size="{font_sz}" stroke="#FAF7F0" stroke-width="2.5" paint-order="stroke fill" fill="{color}" font-weight="bold" text-anchor="middle" dominant-baseline="central">{label}</text>\n'
        svg += '</g>\n'
    svg += '</g>\n'

    # 8. OUTER RING: Transiting Planets Text & Glyphs (Haloed for crisp readability over lines)
    r_out_nak = 163
    r_out_pl = 172
    r_out_deg = 181
    r_out_min = 190
    r_out_sign = 199

    svg += '<g class="outer-planets-group transit-planets-group">\n'
    for p in outer_planets:
        item = p["item"]
        angle = p["draw_angle"]
        p_name = item["name"]
        info = planet_notations.get(p_name, {})
        label = info.get(mode, info.get("symbol", p_name[:2]))
        color = info.get("color", "#000")
        is_retro = item.get("is_retrograde", False)

        px, py = polar_coords(r_out_pl, angle)
        font_sz = 8.0 if p_name == "Lagna" else (11.5 if mode == "devanagari" else 11.0)
        s_sym, s_col, _ = sign_symbols.get(item["sign"], ("?", "#000", "?"))

        d1_house = ((p["sign_idx"] - anchor_s_idx + 12) % 12) + 1
        tooltip = f"Transiting {info.get('full_sa', p_name)} in {item['sign']} {item['degree']}° {item['minute']:02d}'{' [R]' if is_retro else ''} (Natal House {d1_house})"

        svg += f'<g class="interactive planet-glyph outer-planet transit-planet" data-planet="{p_name}" style="cursor: pointer;"><title>{tooltip}</title>\n'

        if show_nakshatras:
            nak_abbr = get_nakshatra_abbreviation(item.get("nakshatra", ""), length=4)
            if nak_abbr:
                nx, ny = polar_coords(r_out_nak, angle)
                svg += f'<text x="{nx:.1f}" y="{ny:.1f}" font-size="5.0" stroke="#FAF7F0" stroke-width="1.8" paint-order="stroke fill" fill="#8c7b64" text-anchor="middle" dominant-baseline="central">{nak_abbr}</text>\n'

        mx, my = polar_coords(r_out_min, angle)
        svg += f'<text x="{mx:.1f}" y="{my:.1f}" font-size="5.2" stroke="#FAF7F0" stroke-width="1.8" paint-order="stroke fill" fill="{color}" text-anchor="middle" dominant-baseline="central">{item["minute"]:02d}\'{" R" if is_retro else ""}</text>\n'

        dx, dy = polar_coords(r_out_deg, angle)
        svg += f'<text x="{dx:.1f}" y="{dy:.1f}" font-size="6.2" stroke="#FAF7F0" stroke-width="2.0" paint-order="stroke fill" fill="{color}" text-anchor="middle" dominant-baseline="central">{item["degree"]}°</text>\n'

        svg += f'<text class="glyph-symbol outer-glyph" x="{px:.1f}" y="{py:.1f}" font-size="{font_sz}" stroke="#FAF7F0" stroke-width="2.5" paint-order="stroke fill" fill="{color}" font-weight="600" text-anchor="middle" dominant-baseline="central">{label}</text>\n'

        sx, sy = polar_coords(r_out_sign, angle)
        svg += f'<text class="outer-sign-glyph" x="{sx:.1f}" y="{sy:.1f}" font-size="6.5" stroke="#FAF7F0" stroke-width="1.8" paint-order="stroke fill" fill="{s_col}" font-weight="bold" text-anchor="middle" dominant-baseline="central">{s_sym}</text>\n'

        svg += '</g>\n'
    svg += '</g>\n'

    svg += '</svg>\n'
    return svg




