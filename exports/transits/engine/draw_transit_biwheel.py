"""
Transit Bi-Wheel SVG Generation (Level 8 Presentation)
=====================================================

This module renders the dual-ring Transit Bi-Wheel in pure SVG (Kala style):
- Inner Ring (Radius ~30 to ~136): Natal Chart (Houses 1-12, Natal Planets).
- Inner Dots (Radius 136): Exact astronomical positions of natal planets on the Rashi circle.
- Middle Zodiac Ring (Radius ~136 to ~150): Clean Tropical Rasi border without harmonic clutter.
- Outer Ring (Radius ~150 to ~206): Date-specific transiting planets with sign and degree.
- Outer Dots (Radius 206): Exact astronomical positions of transiting planets on the outer rim.
- Background Aspect Lines: Thin, clear lines connecting outer transit dots to inner natal dots.
  * Applying aspects: solid stroke, high opacity, scaled width up to 2.4px.
  * Separating aspects: dashed stroke (3,3), low opacity (0.45), 0.95px width.
- Outer Rim Station Pins: Diamond markers nestled on the outer rim (r = 206) at future SR/SD points.
- Stationary Halos & Badges: Double halos and bold 'SR' / 'SD' text for stationary planets.
"""

import math
from typing import List, Dict, Any, Optional

signs_list = [
    "Aries", "Taurus", "Gemini", "Cancer",
    "Leo", "Virgo", "Libra", "Scorpio",
    "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

sign_symbols = {
    "Aries": ("\u2648", "#C0392B", 1),
    "Taurus": ("\u2649", "#27AE60", 2),
    "Gemini": ("\u264A", "#D4AC0D", 3),
    "Cancer": ("\u264B", "#2980B9", 4),
    "Leo": ("\u264C", "#E67E22", 5),
    "Virgo": ("\u264D", "#16A085", 6),
    "Libra": ("\u264E", "#8E44AD", 7),
    "Scorpio": ("\u264F", "#962D22", 8),
    "Sagittarius": ("\u2650", "#2C3E50", 9),
    "Capricorn": ("\u2651", "#7F8C8D", 10),
    "Aquarius": ("\u2652", "#1F618D", 11),
    "Pisces": ("\u2653", "#117864", 12),
}

planet_notations = {
    "Sun": {"symbol": "\u2609", "devanagari": "\u0938\u0942", "color": "#B7950B", "full_sa": "Surya"},
    "Moon": {"symbol": "\u263D", "devanagari": "\u091a\u0902", "color": "#2874A6", "full_sa": "Chandra"},
    "Mars": {"symbol": "\u2642", "devanagari": "\u092e\u0902", "color": "#922B21", "full_sa": "Mangala"},
    "Mercury": {"symbol": "\u263F", "devanagari": "\u092c\u0941", "color": "#1E8449", "full_sa": "Budha"},
    "Jupiter": {"symbol": "\u2643", "devanagari": "\u0917\u0941", "color": "#B9770E", "full_sa": "Guru"},
    "Venus": {"symbol": "\u2640", "devanagari": "\u0936\u0941", "color": "#6C3483", "full_sa": "Shukra"},
    "Saturn": {"symbol": "\u2644", "devanagari": "\u0936", "color": "#1B2631", "full_sa": "Shani"},
    "Rahu": {"symbol": "\u260A", "devanagari": "\u0930\u093e", "color": "#4A235A", "full_sa": "Rahu"},
    "Ketu": {"symbol": "\u260B", "devanagari": "\u0915\u0947", "color": "#641E16", "full_sa": "Ketu"},
    "Lagna": {"symbol": "Asc", "devanagari": "\u0932", "color": "#784212", "full_sa": "Lagna"}
}

def annular_sector(r_in: float, r_out: float, start_deg: float, end_deg: float) -> str:
    """Helper to generate an SVG path for an annular sector (pie slice band)."""
    rad_s = math.radians(start_deg)
    rad_e = math.radians(end_deg)
    x1_in, y1_in = r_in * math.cos(rad_s), r_in * math.sin(rad_s)
    x2_in, y2_in = r_in * math.cos(rad_e), r_in * math.sin(rad_e)
    x1_out, y1_out = r_out * math.cos(rad_s), r_out * math.sin(rad_s)
    x2_out, y2_out = r_out * math.cos(rad_e), r_out * math.sin(rad_e)
    large_arc = 1 if ((end_deg - start_deg) % 360) > 180 else 0
    return (
        f"M {x1_in:.2f} {y1_in:.2f} "
        f"L {x1_out:.2f} {y1_out:.2f} "
        f"A {r_out:.2f} {r_out:.2f} 0 {large_arc} 1 {x2_out:.2f} {y2_out:.2f} "
        f"L {x2_in:.2f} {y2_in:.2f} "
        f"A {r_in:.2f} {r_in:.2f} 0 {large_arc} 0 {x1_in:.2f} {y1_in:.2f} Z"
    )

def generate_transit_biwheel(
    inner_items: List[Dict[str, Any]],
    outer_items: List[Dict[str, Any]],
    active_aspects: Optional[List[Dict[str, Any]]] = None,
    mode: str = "symbol",
    root_planet: str = "Lagna",
    show_nakshatras: bool = False,
    debilitation_mode: str = "kala_degree",
    transit_time_info: Optional[Dict[str, Any]] = None,
    upcoming_stations: Optional[List[Dict[str, Any]]] = None
) -> str:
    """
    Renders the complete 2-Ring Transit Bi-Wheel in SVG format.
    """
    svg = '<svg width="100%" height="100%" viewBox="-215 -215 430 430" class="transit-biwheel-svg" preserveAspectRatio="xMidYMid meet" xmlns="http://www.w3.org/2000/svg" style="background:transparent; font-family: var(--font-astro-glyphs, STIX Two Math, sans-serif);">\n'

    # Markers for transit aspect lines
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
    r_bhava_circle = 72
    r_aspect_inner = 56

    root_title = "Chandra Lagna" if root_planet == "Moon" else ("Surya Lagna" if root_planet == "Sun" else "Ascendant")
    svg += f'<title>Transit / Natal Bi-Wheel ({root_title})</title>\n'

    # Outer bounding circle & tinted background for outer transit ring
    svg += f'<circle cx="0" cy="0" r="{r_chart_outer}" fill="#faf7f2" fill-opacity="0.20" stroke="#5C4433" stroke-width="1.1"/>\n'

    # Middle Zodiac Sign border ring
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

    # 1. Process Planets
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
                "sign_idx": s_idx,
                "sign": item["sign"]
            }
            inner_planets_dict[p_name] = p_data
            inner_planets.append(p_data)

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
                "sign_idx": s_idx,
                "sign": item["sign"]
            }
            outer_planets.append(p_data)
            outer_planets_dict[p_name] = p_data

    # 2. Aspect Lines Layer (Background behind glyphs and borders)
    svg += '<g class="transit-aspect-lines-layer">\n'
    if active_aspects:
        for asp in active_aspects:
            t_name = asp.get("aspecting")
            n_name = asp.get("target")
            asp_type = asp.get("type", "Aspect")
            orb = asp.get("orb", 0.0)
            is_ben = asp.get("is_benefic", False)
            code = asp.get("code", "")
            motion = asp.get("motion_status", "")
            is_app = asp.get("is_applying", True)
            is_stat = asp.get("aspecting_is_stationary", False)

            if t_name in outer_planets_dict and n_name in inner_planets_dict:
                ang_t = outer_planets_dict[t_name]["true_angle"]
                ang_n = inner_planets_dict[n_name]["true_angle"]

                x1, y1 = polar_coords(r_chart_outer, ang_t)
                x2, y2 = polar_coords(r_divider_inner, ang_n)

                marker_url = ""
                if code == "CONJ":
                    stroke_col = "#8E44AD"
                elif "Trine" in asp_type or (is_ben and t_name == "Jupiter"):
                    stroke_col = "#D4AC0D"
                elif t_name == "Mars":
                    stroke_col = "#C0392B"
                    marker_url = 'marker-end="url(#tr-arrow-malefic)"'
                elif t_name == "Saturn":
                    stroke_col = "#2C3E50"
                    marker_url = 'marker-end="url(#tr-arrow-neutral)"'
                elif is_ben:
                    stroke_col = "#27AE60"
                    marker_url = 'marker-end="url(#tr-arrow-benefic)"'
                else:
                    stroke_col = "#C0392B"
                    marker_url = 'marker-end="url(#tr-arrow-malefic)"'

                max_orb = 3.3333
                if is_app:
                    dash_style = "none"
                    op_val = "0.88"
                    if is_stat or orb < 0.5:
                        sw_val = 2.4
                    else:
                        closeness = max(0.0, min(1.0, (max_orb - orb) / (max_orb - 0.5)))
                        sw_val = round(1.0 + 1.4 * closeness, 2)
                else:
                    dash_style = "3,3"
                    op_val = "0.45"
                    sw_val = 0.95

                motion_str = f", {motion}" if motion else ""
                tip = f"Transit {t_name} \u2192 Natal {n_name} ({asp_type}, Orb: {orb}\u00b0{motion_str})"
                svg += f'  <line class="interactive-aspect transit-aspect-line" data-from="{t_name}" data-to="{n_name}" data-orb="{orb}" data-type="{asp_type}" data-applying="{str(is_app).lower()}" x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke_col}" stroke-width="{sw_val}" stroke-dasharray="{dash_style}" opacity="{op_val}" {marker_url} style="cursor: pointer;"><title>{tip}</title></line>\n'
    svg += '</g>\n'

    # 3. Outer Dot Halos for Stations & Rim Markers
    svg += '<g class="transit-dots-layer">\n'
    for p in outer_planets:
        p_name = p["item"]["name"]
        ang_true = p["true_angle"]
        p_info = planet_notations.get(p_name, {})
        dot_col = p_info.get("color", "#4a3325")
        st_type = p["item"].get("station_type")

        dx, dy = polar_coords(r_chart_outer, ang_true)
        tip = f"Transit {p_name} exact position: {p['item']['degree']}° {p['item']['minute']:02d}' {p['sign']}"
        svg += f'  <circle class="transit-planet-dot" cx="{dx:.1f}" cy="{dy:.1f}" r="2.8" fill="{dot_col}" stroke="#ffffff" stroke-width="0.8"><title>{tip}</title></circle>\n'

        if st_type == "SR":
            svg += f'  <circle class="transit-station-halo halo-sr" cx="{dx:.1f}" cy="{dy:.1f}" r="5.2" fill="none" stroke="#dc2626" stroke-width="1.2" stroke-dasharray="2.5,1.5"><title>Stationary Retrograde (SR)</title></circle>\n'
        elif st_type == "SD":
            svg += f'  <circle class="transit-station-halo halo-sd" cx="{dx:.1f}" cy="{dy:.1f}" r="5.2" fill="none" stroke="#16a34a" stroke-width="1.2"><title>Stationary Direct (SD)</title></circle>\n'
    svg += '</g>\n'

    # 4. Upcoming Station Pins (Outer Rim Diamond Markers)
    if upcoming_stations:
        svg += '<g class="upcoming-stations-layer">\n'
        for st in upcoming_stations:
            st_lon = st.get("longitude", 0.0)
            st_type = st.get("station_type", "SR")
            st_p = st.get("planet", "")
            st_tip = st.get("tooltip", f"Upcoming {st_p} {st_type}")
            j_date = st.get("jump_date", "")
            j_time = st.get("jump_time", "12:00:00")
            pin_ang = lon_to_angle(st_lon)
            px, py = polar_coords(r_chart_outer, pin_ang)
            pin_col = "#dc2626" if st_type == "SR" else "#16a34a"

            rad = math.radians(pin_ang)
            ux, uy = math.cos(rad), math.sin(rad)
            tx, ty = -math.sin(rad), math.cos(rad)

            # Small diamond pin nestled on outer rim pointing inwards
            p_tip = (px - 2.5 * ux, py - 2.5 * uy)
            p_left = (px + 2.5 * ux - 2.8 * tx, py + 2.5 * uy - 2.8 * ty)
            p_back = (px + 6.0 * ux, py + 6.0 * uy)
            p_right = (px + 2.5 * ux + 2.8 * tx, py + 2.5 * uy + 2.8 * ty)
            pts = f"{p_tip[0]:.1f},{p_tip[1]:.1f} {p_left[0]:.1f},{p_left[1]:.1f} {p_back[0]:.1f},{p_back[1]:.1f} {p_right[0]:.1f},{p_right[1]:.1f}"

            svg += f'  <g class="interactive-station-pin station-pin" data-planet="{st_p}" data-type="{st_type}" data-jump-date="{j_date}" data-jump-time="{j_time}" style="cursor: pointer;">\n'
            svg += f'    <title>{st_tip} (Click to jump)</title>\n'
            svg += f'    <polygon points="{pts}" fill="{pin_col}" stroke="#ffffff" stroke-width="0.8"/>\n'
            svg += '  </g>\n'
        svg += '</g>\n'

    svg += '</svg>\n'
    return svg
