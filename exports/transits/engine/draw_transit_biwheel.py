"""
Transit Bi-Wheel SVG Generation (Level 8 Presentation)
=====================================================

Standalone module for rendering the dual-ring Transit Bi-Wheel in pure SVG (Kala style):
- Inner Ring (Radius ~30 to ~136): Natal Chart (Houses 1-12, Kendras/Trikonas, Natal Planets).
- Inner Dots (Radius 136): Exact astronomical positions of natal planets on the Rashi circle.
- Middle Zodiac Ring (Radius ~136 to ~150): Clean Tropical Rasi border WITHOUT harmonic subdivisions.
- Outer Ring (Radius ~150 to ~206): Real-time / Date-specific Transiting Planets with sign & degree.
- Outer Dots (Radius 206): Exact astronomical positions of transiting planets on the outer rim.
- Background Aspect Lines: Thin, clear lines connecting outer transit dots to inner natal dots.
- Center Hub (Radius 0 to ~56): Unobstructed center hub with live dynamic transit readout.
- Outer Rim Station Pins: Diamond markers nestled on the outer rim (r = 206) at future SR/SD points.
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

def annular_sector(r_in, r_out, a_start, a_end):
    rad_s = math.radians(a_start)
    rad_e = math.radians(a_end)
    x1_in = r_in * math.cos(rad_s)
    y1_in = r_in * math.sin(rad_s)
    x2_in = r_in * math.cos(rad_e)
    y2_in = r_in * math.sin(rad_e)
    x1_out = r_out * math.cos(rad_s)
    y1_out = r_out * math.sin(rad_s)
    x2_out = r_out * math.cos(rad_e)
    y2_out = r_out * math.sin(rad_e)
    large_arc = 1 if ((a_end - a_start) % 360) > 180 else 0
    return (
        f"M {x1_in:.2f} {y1_in:.2f} "
        f"L {x1_out:.2f} {y1_out:.2f} "
        f"A {r_out:.2f} {r_out:.2f} 0 {large_arc} 1 {x2_out:.2f} {y2_out:.2f} "
        f"L {x2_in:.2f} {y2_in:.2f} "
        f"A {r_in:.2f} {r_in:.2f} 0 {large_arc} 0 {x1_in:.2f} {y1_in:.2f} Z"
    )

def get_nakshatra_abbreviation(name: str, length: int = 4) -> str:
    if not name:
        return ""
    clean = re.sub(r"[^a-zA-Z]", "", name)
    return clean[:length].capitalize()

def relax_planet_angles(planets, has_ascendant_barrier=True, is_outer=False):
    if not planets:
        return
    min_dist = 8.5 if not is_outer else 8.0
    planets_sorted = sorted(planets, key=lambda p: p["true_angle"])
    n = len(planets_sorted)
    angles = [p["true_angle"] for p in planets_sorted]
    for _ in range(35):
        for i in range(n):
            j = (i + 1) % n
            diff = (angles[j] - angles[i]) % 360.0
            if diff < min_dist:
                overlap = min_dist - diff
                angles[i] = (angles[i] - overlap * 0.5) % 360.0
                angles[j] = (angles[j] + overlap * 0.5) % 360.0
    for i, p in enumerate(planets_sorted):
        p["draw_angle"] = angles[i]


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
    r_bhava_circle = 72
    r_aspect_inner = 56

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
            inner_planets_dict[p_name] = p_data
            if p_name == "Lagna" and root_planet == "Lagna":
                continue
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

    # 2. Inner Natal House Background Wedges (unshaded clean canvas)
    for i in range(12):
        sign_start_lon = i * 30.0
        angle_start = lon_to_angle(sign_start_lon)
        angle_end = lon_to_angle(sign_start_lon + 30.0)
        sec_d = annular_sector(r_aspect_inner, r_divider_inner, angle_start, angle_end)
        svg += f'<path class="house-bg" d="{sec_d}" fill="none"/>\n'

    # 3. BACKGROUND LAYER: Aspect Lines connecting Outer Transit Dots to Inner Natal Dots
    # Rendered immediately on top of house colors, strictly behind all dividers, numbers, text & dots
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

                # Start: Exact Outer transit dot on r_chart_outer (206)
                # End: Exact Inner natal dot on r_divider_inner (136)
                x1, y1 = polar_coords(r_chart_outer, ang_t)
                x2, y2 = polar_coords(r_divider_inner, ang_n)

                marker_url = ""
                if code == "CONJ":
                    stroke_col = "#8E44AD"
                    marker_url = 'marker-end="url(#tr-arrow-conj)"'
                elif "Trine" in asp_type or (is_ben and t_name == "Jupiter"):
                    stroke_col = "#D4AC0D"
                    marker_url = 'marker-end="url(#tr-arrow-amber)"'
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
                svg += f'  <line class="interactive-aspect transit-aspect-line aspect-tr-{t_name} aspect-nat-{n_name}" data-from="{t_name}" data-to="{n_name}" data-orb="{orb}" data-type="{asp_type}" data-applying="{str(is_app).lower()}" x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke_col}" stroke-width="{sw_val}" stroke-dasharray="{dash_style}" opacity="{op_val}" {marker_url} style="cursor: pointer; pointer-events: stroke;"><title>{tip}</title></line>\n'
    svg += '</g>\n'

    # 4. House Dividers, Sign Glyphs, Bhava Numbers, and Ascendant Arrow
    for i in range(12):
        sign_start_lon = i * 30.0
        angle_start = lon_to_angle(sign_start_lon)
        angle_mid = lon_to_angle(sign_start_lon + 15.0)
        sign_name = signs_list[i]
        s_sym, s_col, _ = sign_symbols[sign_name]
        bhava_num = (i - anchor_s_idx + 12) % 12 + 1

        # Natal whole sign boundary extending across inner ring (Fine green dots as in Adius)
        x_in1, y_in1 = polar_coords(r_bhava_circle, angle_start)
        x_in2, y_in2 = polar_coords(r_divider_inner, angle_start)
        svg += f'<line x1="{x_in1:.1f}" y1="{y_in1:.1f}" x2="{x_in2:.1f}" y2="{y_in2:.1f}" stroke="#27AE60" stroke-width="0.75" stroke-dasharray="1,2.5" stroke-linecap="round"/>\n'

        # House ring radial divider
        hx1, hy1 = polar_coords(r_aspect_inner, angle_start)
        hx2, hy2 = polar_coords(r_bhava_circle, angle_start)
        svg += f'<line x1="{hx1:.1f}" y1="{hy1:.1f}" x2="{hx2:.1f}" y2="{hy2:.1f}" stroke="#27AE60" stroke-width="0.75" stroke-opacity="0.8"/>\n'

        # Outer sign divider extending outward across outer transit ring (r_divider_outer to r_chart_outer)
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

        # Bhava number label in inner ring (Whole Sign, clean tabular numbers)
        bx, by = polar_coords((r_aspect_inner + r_bhava_circle) / 2, angle_mid)
        svg += f'<text class="interactive house-num" data-type="house" data-id="{bhava_num}" x="{bx:.1f}" y="{by:.1f}" font-size="8.5" font-weight="600" stroke="#FAF7F0" stroke-width="2.0" paint-order="stroke fill" fill="#2980B9" text-anchor="middle" dominant-baseline="central">{bhava_num}</text>\n'

    # Inner D1 Bhava circle
    svg += f'<circle cx="0" cy="0" r="{r_bhava_circle}" fill="none" stroke="#27AE60" stroke-width="0.75"/>\n'

    # Ascendant arrow at 180 degrees
    ax1, ay1 = polar_coords(r_bhava_circle, 180)
    ax2, ay2 = polar_coords(r_divider_inner, 180)
    svg += f'<line class="angle-line angle-ac" x1="{ax1:.1f}" y1="{ay1:.1f}" x2="{ax2:.1f}" y2="{ay2:.1f}" stroke="#C0392B" stroke-width="1.6"/>\n'
    tx1, ty1 = polar_coords(r_divider_inner - 5, 177.5)
    tx2, ty2 = polar_coords(r_divider_inner - 5, 182.5)
    svg += f'<polygon points="{ax2:.1f},{ay2:.1f} {tx1:.1f},{ty1:.1f} {tx2:.1f},{ty2:.1f}" fill="#C0392B"/>\n'

    # AC label (clean bold red typography, NO box, identical to circular chart)
    ac_lbl_x, ac_lbl_y = polar_coords(r_divider_inner - 10.0, 180.0)
    svg += f'<g class="angle-ac-badge" style="cursor: pointer;">\n'
    svg += f'  <title>Ascendant / Lagna — Click to view incoming aspects</title>\n'
    svg += f'  <circle class="planet-highlight-bg" fill="none" stroke="none" cx="{ac_lbl_x:.1f}" cy="{ac_lbl_y - 8.0:.1f}" r="15"/>\n'
    svg += f'  <text class="text-shield" x="{ac_lbl_x:.1f}" y="{ac_lbl_y - 8.0:.1f}" font-size="9.5" font-weight="bold" fill="#C0392B" text-anchor="middle">AC</text>\n'
    svg += f'</g>\n'

    # Degree readout along horizontal spoke
    if anchor_item:
        deg_str = f"{anchor_item['degree']}°"
        min_str = f"{anchor_item['minute']:02d}'"
        deg_x, deg_y = polar_coords((r_bhava_circle + r_divider_inner) / 2.0, 180.0)
        svg += f'<text class="text-shield" x="{deg_x:.1f}" y="{deg_y - 6.0:.1f}" font-size="8.0" font-weight="600" fill="#C0392B" text-anchor="middle">{deg_str} {min_str}</text>\n'

    # Descendant (DC at 0°)
    dc1, dc1_y = polar_coords(r_bhava_circle, 0.0)
    dc2, dc2_y = polar_coords(r_divider_inner, 0.0)
    svg += f'<line class="angle-line angle-dc" x1="{dc1:.1f}" y1="{dc1_y:.1f}" x2="{dc2:.1f}" y2="{dc2_y:.1f}" stroke="#C0392B" stroke-width="1.2"/>\n'

    # 5. Center Circle Hub (Radius 56) - Live Dynamic Transit Readout
    svg += f'<circle class="interactive-center-circle" cx="0" cy="0" r="{r_aspect_inner}" fill="#faf7f0" fill-opacity="0.95" stroke="#5C4433" stroke-width="0.8"/>\n'
    if transit_time_info and "formatted" in transit_time_info:
        parts = transit_time_info["formatted"].split(" ")
        date_part = parts[0] if len(parts) > 0 else ""
        time_part = parts[1][:5] if len(parts) > 1 else ""
        svg += '<text class="text-shield" x="0" y="-14" font-size="6.5" font-weight="bold" fill="#8c7b64" letter-spacing="0.8" text-anchor="middle" pointer-events="none">GOCHARA</text>\n'
        svg += f'<text class="text-shield" x="0" y="-1" font-size="9.5" font-weight="bold" fill="#4a3325" font-variant-numeric="tabular-nums" text-anchor="middle" pointer-events="none">{date_part}</text>\n'
        svg += f'<text class="text-shield" x="0" y="13" font-size="8.5" font-weight="600" fill="#2980B9" font-variant-numeric="tabular-nums" text-anchor="middle" pointer-events="none">{time_part}</text>\n'
    else:
        svg += '<text class="text-shield" x="0" y="-3.5" font-size="8.5" font-weight="bold" fill="#4a3325" text-anchor="middle" pointer-events="none">Natal · Transit</text>\n'
        svg += '<text class="text-shield" x="0" y="9" font-size="7.0" font-weight="600" fill="#8c7b64" text-anchor="middle" pointer-events="none">Bi-Wheel</text>\n'

    # Inward Planetary Ticks on r_aspect_inner = 56
    svg += '<g class="inner-planet-ticks">\n'
    for p in inner_planets:
        t_ang = p["true_angle"]
        p_name = p["item"]["name"]
        p_col = planet_notations.get(p_name, {}).get("color", "#222222")
        tx1, ty1 = polar_coords(r_aspect_inner, t_ang)
        tx2, ty2 = polar_coords(r_aspect_inner - 4.0, t_ang)
        svg += f'<line class="inner-tick" data-planet="{p_name}" x1="{tx1:.1f}" y1="{ty1:.1f}" x2="{tx2:.1f}" y2="{ty2:.1f}" stroke="{p_col}" stroke-width="0.75"><title>{p_name} aspect anchor tick</title></line>\n'
    if root_planet == "Lagna":
        tx1, ty1 = polar_coords(r_aspect_inner, 180.0)
        tx2, ty2 = polar_coords(r_aspect_inner - 4.0, 180.0)
        svg += f'<line class="inner-tick" data-planet="Lagna" x1="{tx1:.1f}" y1="{ty1:.1f}" x2="{tx2:.1f}" y2="{ty2:.1f}" stroke="#C0392B" stroke-width="0.8"><title>Ascendant aspect anchor tick</title></line>\n'
    svg += '</g>\n'

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
        st_type = p["item"].get("station_type")

        # Outer Dot on the chart rim (r = 206)
        dx, dy = polar_coords(r_chart_outer, ang_true)
        tip = f"Transit {p_name} exact position: {p['item']['degree']}° {p['item']['minute']:02d}' {p['sign']}"
        svg += f'  <circle class="transit-planet-dot dot-tr-{p_name}" data-planet="{p_name}" cx="{dx:.1f}" cy="{dy:.1f}" r="2.8" fill="{dot_col}" stroke="#ffffff" stroke-width="0.8"><title>{tip}</title></circle>\n'

        # Subtle pulsing / double halo ring around outer rim dot when stationary
        if st_type == "SR":
            svg += f'  <circle class="transit-station-halo halo-sr" cx="{dx:.1f}" cy="{dy:.1f}" r="5.2" fill="none" stroke="#dc2626" stroke-width="1.2" stroke-dasharray="2.5,1.5"><title>Stationary Retrograde (SR)</title></circle>\n'
        elif st_type == "SD":
            svg += f'  <circle class="transit-station-halo halo-sd" cx="{dx:.1f}" cy="{dy:.1f}" r="5.2" fill="none" stroke="#16a34a" stroke-width="1.2"><title>Stationary Direct (SD)</title></circle>\n'

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
    r_in_nak = 78
    r_in_min = 89
    r_in_deg = 101
    r_in_pl = 118

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
        svg += f'<g class="interactive planet-glyph inner-planet natal-planet" data-type="planet" data-varga="Natal" data-id="{p_name}" data-planet="{p_name}" style="cursor: pointer;"><title>{tooltip}</title>\n'

        if show_nakshatras:
            nak_abbr = get_nakshatra_abbreviation(item.get("nakshatra", ""), length=4)
            if nak_abbr:
                nx, ny = polar_coords(r_in_nak, angle)
                svg += f'<text class="text-shield" x="{nx:.1f}" y="{ny:.1f}" font-size="5.2" stroke="#FAF7F0" stroke-width="1.8" paint-order="stroke fill" fill="#8c7b64" text-anchor="middle" dominant-baseline="central">{nak_abbr}</text>\n'

        mx, my = polar_coords(r_in_min, angle)
        svg += f'<text class="text-shield" x="{mx:.1f}" y="{my:.1f}" font-size="5.8" stroke="#FAF7F0" stroke-width="2.0" paint-order="stroke fill" fill="{color}" text-anchor="middle" dominant-baseline="central">{item["minute"]:02d}\'{" R" if is_retro else ""}</text>\n'

        dx, dy = polar_coords(r_in_deg, angle)
        svg += f'<text class="text-shield" x="{dx:.1f}" y="{dy:.1f}" font-size="6.8" stroke="#FAF7F0" stroke-width="2.2" paint-order="stroke fill" fill="{color}" text-anchor="middle" dominant-baseline="central">{item["degree"]}°</text>\n'

        svg += f'<text class="glyph-symbol text-shield" x="{px:.1f}" y="{py:.1f}" font-size="{font_sz}" stroke="#FAF7F0" stroke-width="2.8" paint-order="stroke fill" fill="{color}" font-weight="bold" text-anchor="middle" dominant-baseline="central">{label}</text>\n'
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
        st_type = item.get("station_type")

        px, py = polar_coords(r_out_pl, angle)
        font_sz = 8.5 if p_name == "Lagna" else (12.0 if mode == "devanagari" else 11.5)
        s_sym, s_col, _ = sign_symbols.get(item["sign"], ("?", "#000", "?"))

        d1_house = ((p["sign_idx"] - anchor_s_idx + 12) % 12) + 1
        st_desc = f" [{st_type}]" if st_type else (" [R]" if is_retro else "")
        tooltip = f"Transiting {info.get('full_sa', p_name)} in {item['sign']} {item['degree']}° {item['minute']:02d}'{st_desc} (Natal House {d1_house})"

        svg += f'<g class="interactive planet-glyph outer-planet transit-planet" data-planet="{p_name}" style="cursor: pointer;"><title>{tooltip}</title>\n'

        if show_nakshatras:
            nak_abbr = get_nakshatra_abbreviation(item.get("nakshatra", ""), length=4)
            if nak_abbr:
                nx, ny = polar_coords(r_out_nak, angle)
                svg += f'<text x="{nx:.1f}" y="{ny:.1f}" font-size="5.2" stroke="#FAF7F0" stroke-width="1.8" paint-order="stroke fill" fill="#8c7b64" text-anchor="middle" dominant-baseline="central">{nak_abbr}</text>\n'

        mx, my = polar_coords(r_out_min, angle)
        if st_type == "SR":
            svg += f'<text x="{mx:.1f}" y="{my:.1f}" font-size="6.0" font-weight="bold" stroke="#FAF7F0" stroke-width="1.8" paint-order="stroke fill" fill="#dc2626" text-anchor="middle" dominant-baseline="central">{item["minute"]:02d}\' SR</text>\n'
        elif st_type == "SD":
            svg += f'<text x="{mx:.1f}" y="{my:.1f}" font-size="6.0" font-weight="bold" stroke="#FAF7F0" stroke-width="1.8" paint-order="stroke fill" fill="#16a34a" text-anchor="middle" dominant-baseline="central">{item["minute"]:02d}\' SD</text>\n'
        elif is_retro:
            svg += f'<text x="{mx:.1f}" y="{my:.1f}" font-size="6.0" font-weight="600" stroke="#FAF7F0" stroke-width="1.8" paint-order="stroke fill" fill="{color}" text-anchor="middle" dominant-baseline="central">{item["minute"]:02d}\' R</text>\n'
        else:
            svg += f'<text x="{mx:.1f}" y="{my:.1f}" font-size="6.0" font-weight="600" stroke="#FAF7F0" stroke-width="1.8" paint-order="stroke fill" fill="{color}" text-anchor="middle" dominant-baseline="central">{item["minute"]:02d}\'</text>\n'

        dx, dy = polar_coords(r_out_deg, angle)
        svg += f'<text x="{dx:.1f}" y="{dy:.1f}" font-size="7.0" font-weight="600" stroke="#FAF7F0" stroke-width="2.0" paint-order="stroke fill" fill="{color}" text-anchor="middle" dominant-baseline="central">{item["degree"]}°</text>\n'

        svg += f'<text class="glyph-symbol outer-glyph" x="{px:.1f}" y="{py:.1f}" font-size="{font_sz}" stroke="#FAF7F0" stroke-width="2.5" paint-order="stroke fill" fill="{color}" font-weight="600" text-anchor="middle" dominant-baseline="central">{label}</text>\n'

        sx, sy = polar_coords(r_out_sign, angle)
        svg += f'<text class="outer-sign-glyph" x="{sx:.1f}" y="{sy:.1f}" font-size="7.2" stroke="#FAF7F0" stroke-width="1.8" paint-order="stroke fill" fill="{s_col}" font-weight="bold" text-anchor="middle" dominant-baseline="central">{s_sym}</text>\n'

        svg += '</g>\n'
    svg += '</g>\n'

    # 9. UPCOMING STATIONS LAYER: Outer Rim Station Pins (r = 206)
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
