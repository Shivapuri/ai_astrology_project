import os
import shutil
from kerykeion import AstrologicalSubject, KerykeionChartSVG
import json
import swisseph as swe
from datetime import datetime, timezone
import pytz
import logging
import warnings

# Suppress GeoNames warning popups/logs
logging.disable(logging.WARNING)
warnings.filterwarnings("ignore")

# --- CONSTANTS & HELLENISTIC LOOKUPS ---
ZODIAC_SIGNS = ["Ari", "Tau", "Gem", "Can", "Leo", "Vir", "Lib", "Sco", "Sag", "Cap", "Aqu", "Pis"]

DOMICILES = {"Ari": "Mars", "Tau": "Venus", "Gem": "Mercury", "Can": "Moon", "Leo": "Sun", "Vir": "Mercury", "Lib": "Venus", "Sco": "Mars", "Sag": "Jupiter", "Cap": "Saturn", "Aqu": "Saturn", "Pis": "Jupiter"}
EXALTATIONS = {"Ari": "Sun", "Tau": "Moon", "Can": "Jupiter", "Vir": "Mercury", "Lib": "Saturn", "Cap": "Mars", "Pis": "Venus"}
DETRIMENTS = {"Ari": "Venus", "Tau": "Mars", "Gem": "Jupiter", "Can": "Saturn", "Leo": "Saturn", "Vir": "Jupiter", "Lib": "Mars", "Sco": "Venus", "Sag": "Mercury", "Cap": "Moon", "Aqu": "Sun", "Pis": "Mercury"}
FALLS = {"Ari": "Saturn", "Tau": "Unknown", "Gem": "Unknown", "Can": "Mars", "Leo": "Unknown", "Vir": "Venus", "Lib": "Sun", "Sco": "Moon", "Sag": "Unknown", "Cap": "Jupiter", "Aqu": "Unknown", "Pis": "Mercury"}

EGYPTIAN_TERMS = {
    "Ari": [(6, "Jupiter"), (12, "Venus"), (20, "Mercury"), (25, "Mars"), (30, "Saturn")],
    "Tau": [(8, "Venus"), (14, "Mercury"), (22, "Jupiter"), (27, "Saturn"), (30, "Mars")],
    "Gem": [(6, "Mercury"), (12, "Jupiter"), (17, "Venus"), (24, "Mars"), (30, "Saturn")],
    "Can": [(7, "Mars"), (13, "Venus"), (19, "Mercury"), (26, "Jupiter"), (30, "Saturn")],
    "Leo": [(6, "Jupiter"), (11, "Venus"), (18, "Saturn"), (24, "Mercury"), (30, "Mars")],
    "Vir": [(7, "Mercury"), (17, "Venus"), (21, "Jupiter"), (28, "Mars"), (30, "Saturn")],
    "Lib": [(6, "Saturn"), (14, "Mercury"), (21, "Jupiter"), (28, "Venus"), (30, "Mars")],
    "Sco": [(7, "Mars"), (11, "Venus"), (19, "Mercury"), (24, "Jupiter"), (30, "Saturn")],
    "Sag": [(12, "Jupiter"), (17, "Venus"), (21, "Mercury"), (26, "Saturn"), (30, "Mars")],
    "Cap": [(7, "Mercury"), (14, "Jupiter"), (22, "Venus"), (26, "Saturn"), (30, "Mars")],
    "Aqu": [(7, "Saturn"), (13, "Mercury"), (20, "Venus"), (25, "Jupiter"), (30, "Mars")],
    "Pis": [(12, "Venus"), (16, "Jupiter"), (19, "Mercury"), (28, "Mars"), (30, "Saturn")]
}

# --- HELPER FUNCTIONS ---
def get_egyptian_term(sign: str, degree_in_sign: float) -> str:
    terms = EGYPTIAN_TERMS.get(sign, [])
    for max_deg, ruler in terms:
        if degree_in_sign < max_deg:
            return ruler
    return terms[-1][1] if terms else "Unknown"

def calculate_dodecatemorion(abs_degree: float):
    deg_in_sign = abs_degree % 30
    dodec_abs = (abs_degree + (deg_in_sign * 11)) % 360
    sign_idx = int(dodec_abs // 30)
    return {
        "sign": ZODIAC_SIGNS[sign_idx],
        "degree_0_to_30": round(dodec_abs % 30, 2),
        "absolute_degree": round(dodec_abs, 2)
    }

def get_essential_dignity(planet: str, sign: str) -> str:
    if DOMICILES.get(sign) == planet: return "Domicile (Home)"
    if EXALTATIONS.get(sign) == planet: return "Exaltation (Honored)"
    if DETRIMENTS.get(sign) == planet: return "Detriment (Exiled)"
    if FALLS.get(sign) == planet: return "Fall (Weakened)"
    return "Peregrine (Wandering)"

def get_dorothean_triplicity(sign: str, is_day_chart: bool) -> dict:
    if sign in ["Ari", "Leo", "Sag"]: # Fire
        return {"day": "Sun", "night": "Jupiter", "participating": "Saturn"}
    elif sign in ["Tau", "Vir", "Cap"]: # Earth
        return {"day": "Venus", "night": "Moon", "participating": "Mars"}
    elif sign in ["Gem", "Lib", "Aqu"]: # Air
        return {"day": "Saturn", "night": "Mercury", "participating": "Jupiter"}
    else: # Water
        return {"day": "Venus", "night": "Mars", "participating": "Moon"}

def get_solar_phasis(planet: str, planet_abs: float, sun_abs: float) -> str:
    if planet in ["Sun", "Moon", "Ascendant"]: return "N/A"
    dist = min(abs(planet_abs - sun_abs), 360 - abs(planet_abs - sun_abs))
    if dist <= (17 / 60): return "Cazimi (In the Heart of the Sun)"
    elif dist <= 8.5: return "Combust (Burned)"
    elif dist <= 15: return "Under the Beams (Hidden)"
    return "Phasis Clear"

def calculate_lot(asc_abs: float, p1_abs: float, p2_abs: float) -> dict:
    lot_abs = (asc_abs + p1_abs - p2_abs) % 360
    lot_sign = ZODIAC_SIGNS[int(lot_abs // 30)]
    return {
        "sign": lot_sign,
        "degree_0_to_30": round(lot_abs % 30, 2),
        "absolute_degree": round(lot_abs, 2)
    }

def get_whole_sign_aspects(points_dict: dict) -> list:
    aspects, aspect_map = [], {0: "conjunction", 2: "sextile", 3: "square", 4: "trine", 6: "opposition"}
    keys = list(points_dict.keys())
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            p1, p2 = keys[i], keys[j]
            idx1, idx2 = ZODIAC_SIGNS.index(points_dict[p1]["sign"]), ZODIAC_SIGNS.index(points_dict[p2]["sign"])
            sign_dist = abs(idx1 - idx2)
            if sign_dist > 6: sign_dist = 12 - sign_dist
            if sign_dist in aspect_map:
                aspects.append({"planet_1": p1, "planet_2": p2, "aspect_type": aspect_map[sign_dist], "sign_distance": sign_dist})
    return aspects

def get_prenatal_syzygy(year, month, day, hour, minute, tz_str) -> dict:
    # Safely calculate SAN
    try: tz = pytz.timezone(tz_str) if tz_str and tz_str != "None" else timezone.utc
    except: tz = timezone.utc
    try: utc_dt = tz.localize(datetime(year, month, day, hour, minute)).astimezone(timezone.utc)
    except: utc_dt = datetime(year, month, day, hour, minute, tzinfo=timezone.utc)
    jd_ut = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, utc_dt.hour + utc_dt.minute / 60.0)
    
    t, step, target_angle = jd_ut, 0.1, None
    prev_phase = (swe.calc_ut(t, swe.MOON)[0][0] - swe.calc_ut(t, swe.SUN)[0][0]) % 360
    while t > jd_ut - 32:
        t -= step
        phase = (swe.calc_ut(t, swe.MOON)[0][0] - swe.calc_ut(t, swe.SUN)[0][0]) % 360
        if prev_phase >= 180 and phase < 180: target_angle = 180.0; t_low, t_high = t, t+step; break
        if prev_phase < 90 and phase > 270: target_angle = 0.0; t_low, t_high = t, t+step; break
        prev_phase = phase

    if target_angle is None: return {"prenatal_syzygy": "Unknown"}

    for _ in range(25):
        t_mid = (t_low + t_high) / 2.0
        phase_m = (swe.calc_ut(t_mid, swe.MOON)[0][0] - swe.calc_ut(t_mid, swe.SUN)[0][0]) % 360
        if target_angle == 180.0:
            if phase_m >= 180.0: t_high = t_mid
            else: t_low = t_mid
        else:
            if phase_m > 180.0: t_high = t_mid
            else: t_low = t_mid

    exact_t = (t_low + t_high) / 2.0
    syz_deg = swe.calc_ut(exact_t, swe.MOON if target_angle == 180.0 else swe.SUN)[0][0]
    return {"type": "Full Moon" if target_angle == 180.0 else "New Moon", "sign": ZODIAC_SIGNS[int(syz_deg // 30)], "degree_0_to_30": round(syz_deg % 30, 2)}

def build_html_dashboard_string(subject_name, ai_payload, svg_raw_xml, chart_ruler):
    """Constructs a simple, elegant warm-ivory HTML dashboard with a large Natal Wheel, zodiac sign explanations, and interactive tooltips."""
    payload_json = json.dumps(ai_payload, indent=2)
    native = ai_payload.get("native_details", {})
    planets = ai_payload.get("traditional_planets", {})
    aspects = ai_payload.get("whole_sign_aspects", [])
    lots = ai_payload.get("7_hermetic_lots", {})
    syzygy = ai_payload.get("prenatal_syzygy", {})

    # Detailed Zodiac Sign Definitions & Explanations
    zodiac_info = {
        "Ari": {"name": "Aries", "symbol": "♈", "element": "Fire", "modality": "Cardinal", "ruler": "Mars", "desc": "The pioneer. Aries brings bold initiative, direct action, and a pioneering drive to start new chapters."},
        "Tau": {"name": "Taurus", "symbol": "♉", "element": "Earth", "modality": "Fixed", "ruler": "Venus", "desc": "The builder. Taurus seeks tangible security, sensory beauty, and steady, unwavering endurance."},
        "Gem": {"name": "Gemini", "symbol": "♊", "element": "Air", "modality": "Mutable", "ruler": "Mercury", "desc": "The messenger. Gemini thrives on mental agility, connecting diverse ideas, and adaptable communication."},
        "Can": {"name": "Cancer", "symbol": "♋", "element": "Water", "modality": "Cardinal", "ruler": "Moon", "desc": "The protector. Cancer guards inner emotional sanctuaries, guided by deep intuition and protective care."},
        "Leo": {"name": "Leo", "symbol": "♌", "element": "Fire", "modality": "Fixed", "ruler": "Sun", "desc": "The sovereign. Leo shines with radiant self-expression, creative warmth, and noble leadership."},
        "Vir": {"name": "Virgo", "symbol": "♍", "element": "Earth", "modality": "Mutable", "ruler": "Mercury", "desc": "The craftsperson. Virgo refines and perfects through careful discernment, practical analysis, and service."},
        "Lib": {"name": "Libra", "symbol": "♎", "element": "Air", "modality": "Cardinal", "ruler": "Venus", "desc": "The diplomat. Libra balances opposing forces to create aesthetic harmony, relational equity, and justice."},
        "Sco": {"name": "Scorpio", "symbol": "♏", "element": "Water", "modality": "Fixed", "ruler": "Mars", "desc": "The alchemist. Scorpio penetrates beneath surfaces to uncover truth, emotional power, and deep transformation."},
        "Sag": {"name": "Sagittarius", "symbol": "♐", "element": "Fire", "modality": "Mutable", "ruler": "Jupiter", "desc": "The seeker. Sagittarius expands horizons through philosophical questing, higher truth, and optimistic exploration."},
        "Cap": {"name": "Capricorn", "symbol": "♑", "element": "Earth", "modality": "Fixed", "ruler": "Saturn", "desc": "The architect. Capricorn builds enduring structures through patient discipline, long-term focus, and mastery."},
        "Aqu": {"name": "Aquarius", "symbol": "♒", "element": "Air", "modality": "Fixed", "ruler": "Saturn", "desc": "The visionary. Aquarius perceives future possibilities, promoting intellectual independence and community vision."},
        "Pis": {"name": "Pisces", "symbol": "♓", "element": "Water", "modality": "Mutable", "ruler": "Jupiter", "desc": "The mystic. Pisces dissolves rigid boundaries to connect with universal empathy, artistic imagination, and spirit."}
    }

    # Identify key active signs in this specific chart
    key_sign_keys = []
    asc_s = native.get('ascendant')
    if asc_s and asc_s in zodiac_info: key_sign_keys.append(asc_s)
    
    for p_name in ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]:
        if p_name in planets:
            p_sign = planets[p_name].get("sign")
            if p_sign and p_sign in zodiac_info and p_sign not in key_sign_keys:
                key_sign_keys.append(p_sign)

    # Build Zodiac Explanations HTML Cards
    zodiac_explained_html = ""
    for s_key in key_sign_keys:
        info = zodiac_info[s_key]
        role = []
        if s_key == asc_s: role.append("Ascendant (Rising Sign)")
        if "Sun" in planets and planets["Sun"].get("sign") == s_key: role.append("Sun Sign")
        if "Moon" in planets and planets["Moon"].get("sign") == s_key: role.append("Moon Sign")
        
        role_tag = f"<span class='zodiac-role-tag'>{' • '.join(role)}</span>" if role else ""

        zodiac_explained_html += f"""
        <div class="zodiac-card">
            <div class="zodiac-header">
                <div class="zodiac-symbol">{info.get('symbol', '✨')}</div>
                <div>
                    <h4 class="zodiac-title">{info['name']} ({s_key})</h4>
                    {role_tag}
                </div>
            </div>
            <div class="zodiac-meta">
                <span class="zodiac-pill pill-element">{info['element']}</span>
                <span class="zodiac-pill pill-modality">{info['modality']}</span>
                <span class="zodiac-pill pill-ruler">Ruled by {info['ruler']}</span>
            </div>
            <p class="zodiac-desc">{info['desc']}</p>
        </div>
        """

    # Definitions for tooltips
    lot_descriptions = {
        "Lot_of_Fortune": "Physical vitality, body health, financial luck, and material circumstances.",
        "Lot_of_Spirit": "Mental purpose, career direction, soul intentions, and active choices.",
        "Lot_of_Necessity": "Karmic constraints, unavoidable duties, and tests of endurance.",
        "Lot_of_Eros": "Emotional passions, romantic attraction, and personal desires.",
        "Lot_of_Courage": "Competitive drive, bravery, self-defense, and bold enterprise.",
        "Lot_of_Victory": "Triumph over adversity, achievement, and divine favor.",
        "Lot_of_Nemesis": "Hidden obstacles, shadow integration, discipline, and karmic boundaries."
    }

    # Generate planet rows
    planet_rows_html = ""
    for planet, data in planets.items():
        dignity = data.get("essential_dignity", "Peregrine")
        dignity_class = "dignity-peregrine"
        if "Domicile" in dignity: dignity_class = "dignity-domicile"
        elif "Exaltation" in dignity: dignity_class = "dignity-exaltation"
        elif "Detriment" in dignity: dignity_class = "dignity-detriment"
        elif "Fall" in dignity: dignity_class = "dignity-fall"

        phasis = data.get("solar_phasis", "Phasis Clear")
        phasis_class = "phasis-clear"
        if "Cazimi" in phasis: phasis_class = "phasis-cazimi"
        elif "Combust" in phasis: phasis_class = "phasis-combust"
        elif "Beams" in phasis: phasis_class = "phasis-beams"

        retro = " <span class='retro-tag' title='Retrograde (moving backward in sky)'>(R)</span>" if data.get("is_retrograde") else ""

        planet_rows_html += f"""
        <tr class="planet-row" data-planet="{planet}">
            <td><strong class="planet-name">{planet}</strong>{retro}</td>
            <td><span class="badge sign-badge">{data.get('sign')}</span></td>
            <td>{data.get('whole_sign_house', '').replace('_', ' ')}</td>
            <td>{data.get('degree_0_to_30')}°</td>
            <td><span class="badge {dignity_class} tooltip-term" data-tooltip="Essential Dignity describes how comfortably a planet operates in its sign.">{dignity}</span></td>
            <td><span class="badge {phasis_class} tooltip-term" data-tooltip="Solar Phasis indicates visibility relative to the Sun.">{phasis}</span></td>
            <td><span class="term-ruler">{data.get('egyptian_term_ruler')}</span></td>
        </tr>
        """

    # Generate aspect chips
    aspect_chips_html = ""
    if aspects:
        for asp in aspects:
            atype = asp.get("aspect_type", "").lower()
            symbol = "☌"
            if atype == "sextile": symbol = "⚹"
            elif atype == "square": symbol = "◽"
            elif atype == "trine": symbol = "△"
            elif atype == "opposition": symbol = "☍"
            
            aspect_chips_html += f"""
            <div class="aspect-chip aspect-{atype}">
                <span class="asp-planets">{asp.get('planet_1')}</span>
                <span class="asp-symbol">{symbol}</span>
                <span class="asp-type">{asp.get('aspect_type', '').title()}</span>
                <span class="asp-planets">{asp.get('planet_2')}</span>
            </div>
            """
    else:
        aspect_chips_html = "<p class='no-data'>No major whole sign aspects found.</p>"

    # Generate lot cards
    lot_cards_html = ""
    for lot_key, lot_data in lots.items():
        clean_name = lot_key.replace('_', ' ')
        desc = lot_descriptions.get(lot_key, "Hermetic Lot calculation.")
        lot_cards_html += f"""
        <div class="lot-card">
            <div class="lot-header">
                <h4>{clean_name}</h4>
                <span class="lot-house">{lot_data.get('whole_sign_house', '').replace('_', ' ')}</span>
            </div>
            <div class="lot-body">
                <span class="badge sign-badge">{lot_data.get('sign')}</span>
                <span class="lot-deg">{lot_data.get('degree_0_to_30')}°</span>
            </div>
            <p class="lot-desc">{desc}</p>
        </div>
        """

    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Natal Astrology Dashboard - {subject_name}</title>
    <!-- Elegant Serif and Clean Sans Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-body: #fcfbf9;
            --bg-card: #ffffff;
            --border-subtle: #e2e8f0;
            --border-gold: #cbd5e1;
            --text-heading: #0f172a;
            --text-body: #334155;
            --text-muted: #64748b;
            --accent-gold: #b45309;
            --accent-emerald: #047857;
            --accent-teal: #0f766e;
            --accent-rose: #be123c;
            --accent-indigo: #4338ca;
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            background-color: var(--bg-body);
            color: var(--text-body);
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
            min-height: 100vh;
            padding: 36px 20px;
            line-height: 1.6;
        }}

        /* Header */
        .header-container {{
            max-width: 1100px;
            margin: 0 auto 36px auto;
            text-align: center;
            padding-bottom: 24px;
            border-bottom: 1px solid var(--border-subtle);
        }}

        .header-title {{
            font-family: 'Cormorant Garamond', Georgia, serif;
            font-size: 2.75rem;
            font-weight: 600;
            color: var(--text-heading);
            letter-spacing: -0.01em;
            margin-bottom: 8px;
        }}

        .header-subtitle {{
            font-size: 0.95rem;
            color: var(--text-muted);
            font-weight: 400;
            margin-bottom: 16px;
        }}

        .header-badges {{
            display: flex;
            justify-content: center;
            gap: 12px;
            flex-wrap: wrap;
        }}

        .header-badge {{
            background: #f1f5f9;
            color: var(--text-heading);
            border: 1px solid var(--border-subtle);
            padding: 5px 14px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 500;
        }}

        /* Main Container */
        .main-container {{
            max-width: 1100px;
            margin: 0 auto;
            display: flex;
            flex-direction: column;
            gap: 36px;
        }}

        /* Large Natal Wheel Section */
        .hero-wheel-section {{
            background: var(--bg-card);
            border: 1px solid var(--border-subtle);
            border-radius: 20px;
            padding: 32px 24px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
            text-align: center;
        }}

        .section-heading {{
            font-family: 'Cormorant Garamond', Georgia, serif;
            font-size: 1.8rem;
            font-weight: 600;
            color: var(--text-heading);
            margin-bottom: 6px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }}

        .section-sub {{
            font-size: 0.88rem;
            color: var(--text-muted);
            margin-bottom: 24px;
        }}

        .large-svg-wrapper {{
            width: 100%;
            max-width: 920px;
            margin: 0 auto;
            display: flex;
            justify-content: center;
            align-items: center;
            background: #ffffff;
            border-radius: 16px;
            padding: 16px;
            border: 1px solid #f1f5f9;
        }}

        .large-svg-wrapper svg {{
            width: 100%;
            height: auto;
            max-height: 800px;
        }}

        /* Hover Glow Effect on SVG */
        .svg-highlight {{
            filter: drop-shadow(0 0 10px rgba(67, 56, 202, 0.6)) brightness(1.2) !important;
            transition: all 0.2s ease;
        }}

        /* Section Cards */
        .card {{
            background: var(--bg-card);
            border: 1px solid var(--border-subtle);
            border-radius: 20px;
            padding: 28px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
        }}

        /* Zodiac Signs Explained Section */
        .zodiac-explained-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 16px;
        }}

        .zodiac-card {{
            background: #fafaf9;
            border: 1px solid #e7e5e4;
            border-radius: 14px;
            padding: 18px;
            transition: border-color 0.2s ease, transform 0.2s ease;
        }}

        .zodiac-card:hover {{
            border-color: #d6d3d1;
            transform: translateY(-2px);
        }}

        .zodiac-header {{
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 12px;
        }}

        .zodiac-symbol {{
            font-size: 2rem;
            font-family: 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol', 'Noto Color Emoji', sans-serif;
            color: var(--accent-gold);
            line-height: 1;
        }}

        .zodiac-title {{
            font-family: 'Cormorant Garamond', Georgia, serif;
            font-size: 1.3rem;
            font-weight: 700;
            color: var(--text-heading);
        }}

        .zodiac-role-tag {{
            display: inline-block;
            font-size: 0.72rem;
            color: var(--accent-indigo);
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }}

        .zodiac-meta {{
            display: flex;
            gap: 6px;
            flex-wrap: wrap;
            margin-bottom: 10px;
        }}

        .zodiac-pill {{
            font-size: 0.72rem;
            padding: 2px 8px;
            border-radius: 12px;
            font-weight: 500;
            background: #f1f5f9;
            color: var(--text-muted);
        }}

        .zodiac-desc {{
            font-size: 0.85rem;
            color: var(--text-body);
            line-height: 1.45;
        }}

        /* Core Architecture Grid */
        .arch-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
        }}

        .arch-item {{
            background: #f8fafc;
            border: 1px solid var(--border-subtle);
            border-radius: 14px;
            padding: 16px;
        }}

        .arch-label {{
            font-size: 0.75rem;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 4px;
            display: flex;
            align-items: center;
            gap: 6px;
        }}

        .arch-val {{
            font-family: 'Cormorant Garamond', Georgia, serif;
            font-size: 1.4rem;
            font-weight: 700;
            color: var(--text-heading);
        }}

        .arch-sub {{
            font-size: 0.8rem;
            color: var(--text-muted);
            margin-top: 2px;
        }}

        /* Help Icon & Tooltip */
        .help-icon {{
            display: inline-flex;
            justify-content: center;
            align-items: center;
            width: 16px;
            height: 16px;
            border-radius: 50%;
            background: #e2e8f0;
            color: var(--text-muted);
            font-size: 10px;
            font-weight: bold;
            cursor: pointer;
        }}

        .help-icon:hover {{
            background: var(--text-heading);
            color: #ffffff;
        }}

        .tooltip-term {{
            cursor: help;
            border-bottom: 1px dotted var(--text-muted);
        }}

        #floating-tooltip {{
            position: fixed;
            background: #0f172a;
            color: #f8fafc;
            padding: 10px 14px;
            border-radius: 8px;
            font-size: 0.85rem;
            max-width: 300px;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
            pointer-events: none;
            z-index: 9999;
            display: none;
            line-height: 1.4;
        }}

        /* Table Design */
        .table-responsive {{
            overflow-x: auto;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            text-align: left;
            font-size: 0.9rem;
        }}

        th {{
            background: #f8fafc;
            color: var(--text-muted);
            font-weight: 600;
            padding: 12px 14px;
            border-bottom: 2px solid var(--border-subtle);
            text-transform: uppercase;
            font-size: 0.75rem;
            letter-spacing: 0.05em;
        }}

        td {{
            padding: 14px;
            border-bottom: 1px solid var(--border-subtle);
            transition: background 0.2s ease;
        }}

        .planet-row {{
            cursor: pointer;
        }}

        .planet-row:hover, .planet-row.row-highlight {{
            background: #f1f5f9 !important;
        }}

        /* Badges */
        .badge {{
            display: inline-block;
            padding: 3px 10px;
            border-radius: 6px;
            font-size: 0.78rem;
            font-weight: 500;
        }}

        .sign-badge {{ background: #eff6ff; color: #1e40af; border: 1px solid #bfdbfe; }}
        .dignity-domicile {{ background: #ecfdf5; color: #047857; border: 1px solid #a7f3d0; }}
        .dignity-exaltation {{ background: #f0fdf4; color: #15803d; border: 1px solid #bbf7d0; }}
        .dignity-detriment {{ background: #fffbeb; color: #b45309; border: 1px solid #fde68a; }}
        .dignity-fall {{ background: #fff1f2; color: #be123c; border: 1px solid #fecdd3; }}
        .dignity-peregrine {{ background: #f8fafc; color: #64748b; border: 1px solid #e2e8f0; }}

        .phasis-cazimi {{ background: #fefce8; color: #a16207; border: 1px solid #fef08a; font-weight: 600; }}
        .phasis-combust {{ background: #fff1f2; color: #be123c; border: 1px solid #fecdd3; }}
        .phasis-beams {{ background: #fff7ed; color: #c2410c; border: 1px solid #ffedd5; }}
        .phasis-clear {{ background: #f8fafc; color: #64748b; }}

        /* Aspects Grid */
        .aspects-container {{
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
        }}

        .aspect-chip {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 8px 16px;
            border-radius: 10px;
            font-size: 0.88rem;
            background: #f8fafc;
            border: 1px solid var(--border-subtle);
        }}

        .asp-symbol {{ font-weight: bold; font-size: 1.1rem; }}
        .aspect-trine .asp-symbol {{ color: var(--accent-emerald); }}
        .aspect-sextile .asp-symbol {{ color: var(--accent-teal); }}
        .aspect-square .asp-symbol {{ color: var(--accent-gold); }}
        .aspect-opposition .asp-symbol {{ color: var(--accent-rose); }}
        .aspect-conjunction .asp-symbol {{ color: var(--accent-indigo); }}

        /* Hermetic Lots Grid */
        .lots-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
            gap: 16px;
        }}

        .lot-card {{
            background: #f8fafc;
            border: 1px solid var(--border-subtle);
            border-radius: 14px;
            padding: 16px;
        }}

        .lot-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }}

        .lot-header h4 {{
            font-family: 'Cormorant Garamond', Georgia, serif;
            font-size: 1.15rem;
            color: var(--text-heading);
            font-weight: 700;
        }}

        .lot-house {{
            font-size: 0.75rem;
            color: var(--text-muted);
        }}

        .lot-body {{
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 8px;
        }}

        .lot-desc {{
            font-size: 0.8rem;
            color: var(--text-body);
            line-height: 1.4;
        }}
    </style>
</head>
<body>

    <!-- Floating Dynamic Tooltip -->
    <div id="floating-tooltip"></div>

    <!-- Header Section -->
    <header class="header-container">
        <h1 class="header-title">Astrological Dashboard</h1>
        <p class="header-subtitle">Subject: <strong>{subject_name}</strong> • Hellenistic Western Astrology (Tropical Zodiac & Whole Sign Houses)</p>
        <div class="header-badges">
            <span class="header-badge">Ascendant: {native.get('ascendant')}</span>
            <span class="header-badge">Chart Ruler: {chart_ruler}</span>
            <span class="header-badge">Sect: {native.get('sect')}</span>
        </div>
    </header>

    <!-- Main Content Container -->
    <main class="main-container">
        
        <!-- Large Natal Wheel Section -->
        <section class="hero-wheel-section">
            <h2 class="section-heading"><span>🪐</span> Natal Wheel</h2>
            <p class="section-sub">Hover over any planet glyph in the wheel or table to inspect degrees, dignities, and aspects.</p>
            <div class="large-svg-wrapper">
                {svg_raw_xml}
            </div>
        </section>

        <!-- Zodiac Signs Explained Section -->
        <section class="card">
            <h2 class="section-heading"><span>✨</span> Dominant Zodiac Signs Explained</h2>
            <p class="section-sub">Overview of the core zodiac archetypes actively influencing this chart.</p>
            <div class="zodiac-explained-grid">
                {zodiac_explained_html}
            </div>
        </section>

        <!-- Core Architecture Card -->
        <section class="card">
            <h2 class="section-heading"><span>🏛️</span> Core Architecture</h2>
            <p class="section-sub">The structural foundation of the birth chart according to Hellenistic principles.</p>
            <div class="arch-grid">
                <div class="arch-item">
                    <div class="arch-label">
                        Ascendant (Rising Sign)
                        <span class="help-icon tooltip-term" data-tooltip="Ascendant (the zodiac sign rising on the eastern horizon at birth, representing your physical orientation and outer social interface).">?</span>
                    </div>
                    <div class="arch-val">{native.get('ascendant')}</div>
                    <div class="arch-sub">The Ship & Interface</div>
                </div>

                <div class="arch-item">
                    <div class="arch-label">
                        Chart Ruler (Captain)
                        <span class="help-icon tooltip-term" data-tooltip="Chart Ruler (the ruling planet of your Ascendant sign, acting as the Steersman/Captain navigating your life path).">?</span>
                    </div>
                    <div class="arch-val">{chart_ruler}</div>
                    <div class="arch-sub">Steersman of the Helm</div>
                </div>

                <div class="arch-item">
                    <div class="arch-label">
                        Sect
                        <span class="help-icon tooltip-term" data-tooltip="Sect (determines whether Sun or Moon leads the chart. A Night Chart means Moon, Venus, and Mars are primary).">?</span>
                    </div>
                    <div class="arch-val">{native.get('sect')}</div>
                    <div class="arch-sub">Diurnal/Nocturnal Light</div>
                </div>

                <div class="arch-item">
                    <div class="arch-label">
                        House System
                        <span class="help-icon tooltip-term" data-tooltip="Whole Sign Houses (WSH) (classical system where the entire Ascendant sign forms the 1st House, and each subsequent sign is a 30° house).">?</span>
                    </div>
                    <div class="arch-val">Whole Sign Houses</div>
                    <div class="arch-sub">Classical 30° Division</div>
                </div>

                <div class="arch-item">
                    <div class="arch-label">
                        Prenatal Syzygy
                        <span class="help-icon tooltip-term" data-tooltip="Prenatal Syzygy (the exact lunation—Full or New Moon—immediately preceding birth, showing foundational soul imprint).">?</span>
                    </div>
                    <div class="arch-val">{syzygy.get('type', 'Unknown')}</div>
                    <div class="arch-sub">{syzygy.get('sign', '')} {syzygy.get('degree_0_to_30', '')}°</div>
                </div>
            </div>
        </section>

        <!-- Planetary Placements Card -->
        <section class="card">
            <h2 class="section-heading"><span>⚡</span> Planetary Placements & Dignities</h2>
            <p class="section-sub">Hover over any row to highlight the planet's exact location on the Natal Wheel above.</p>
            <div class="table-responsive">
                <table>
                    <thead>
                        <tr>
                            <th>Planet</th>
                            <th>Sign</th>
                            <th>House</th>
                            <th>Degree</th>
                            <th>
                                Dignity
                                <span class="help-icon tooltip-term" data-tooltip="Essential Dignity (indicates how comfortably a planet operates in its sign: Domicile=Home, Exaltation=Honored, Detriment=Exiled, Fall=Weakened, Peregrine=Wandering).">?</span>
                            </th>
                            <th>
                                Phasis
                                <span class="help-icon tooltip-term" data-tooltip="Solar Phasis (visibility relative to the Sun: Cazimi=In Heart of Sun, Combust=Hidden by rays, Under Beams=Partially obscured).">?</span>
                            </th>
                            <th>Term Ruler</th>
                        </tr>
                    </thead>
                    <tbody>
                        {planet_rows_html}
                    </tbody>
                </table>
            </div>
        </section>

        <!-- Major Aspects Card -->
        <section class="card">
            <h2 class="section-heading"><span>🔄</span> Major Aspects (Friction & Flow)</h2>
            <p class="section-sub">Whole-sign planetary geometry creating dynamic harmony or psychological tension.</p>
            <div class="aspects-container">
                {aspect_chips_html}
            </div>
        </section>

        <!-- Hermetic Lots Card -->
        <section class="card">
            <h2 class="section-heading"><span>🔮</span> Hermetic Lots</h2>
            <p class="section-sub">Calculated mathematical points revealing specific life themes and destiny focus areas.</p>
            <div class="lots-grid">
                {lot_cards_html}
            </div>
        </section>

    </main>

    <!-- Client-Side Interactivity -->
    <script>
        const chartData = {payload_json};

        // Tooltip handler
        const tooltip = document.getElementById('floating-tooltip');
        document.querySelectorAll('.tooltip-term').forEach(el => {{
            el.addEventListener('mouseenter', (e) => {{
                const text = el.getAttribute('data-tooltip');
                if (text) {{
                    tooltip.innerHTML = text;
                    tooltip.style.display = 'block';
                }}
            }});
            el.addEventListener('mousemove', (e) => {{
                tooltip.style.left = (e.clientX + 14) + 'px';
                tooltip.style.top = (e.clientY + 14) + 'px';
            }});
            el.addEventListener('mouseleave', () => {{
                tooltip.style.display = 'none';
            }});
        }});

        // Bi-directional hover highlighting
        const planetRows = document.querySelectorAll('.planet-row');
        const svgContainer = document.querySelector('.large-svg-wrapper svg');

        function setHighlight(planetName, active) {{
            // Table row
            const row = document.querySelector(`.planet-row[data-planet="${{planetName}}"]`);
            if (row) {{
                if (active) row.classList.add('row-highlight');
                else row.classList.remove('row-highlight');
            }}

            // SVG elements
            if (svgContainer) {{
                const uses = svgContainer.querySelectorAll(`use[href="#${{planetName}}"], use[*|href="#${{planetName}}"]`);
                uses.forEach(u => {{
                    const parentGroup = u.parentElement;
                    if (active) {{
                        if (parentGroup) parentGroup.classList.add('svg-highlight');
                    }} else {{
                        if (parentGroup) parentGroup.classList.remove('svg-highlight');
                    }}
                }});
            }}
        }}

        planetRows.forEach(row => {{
            row.addEventListener('mouseenter', () => {{
                const planet = row.getAttribute('data-planet');
                setHighlight(planet, true);
            }});
            row.addEventListener('mouseleave', () => {{
                const planet = row.getAttribute('data-planet');
                setHighlight(planet, false);
            }});
        }});

        // Attach SVG hover handlers for chart glyphs
        if (svgContainer) {{
            ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn'].forEach(planet => {{
                const uses = svgContainer.querySelectorAll(`use[href="#${{planet}}"], use[*|href="#${{planet}}"]`);
                uses.forEach(u => {{
                    const parentGroup = u.parentElement;
                    if (parentGroup) {{
                        parentGroup.style.cursor = 'pointer';
                        parentGroup.addEventListener('mouseenter', (e) => {{
                            setHighlight(planet, true);
                            const pData = chartData.traditional_planets[planet];
                            if (pData) {{
                                tooltip.innerHTML = `<strong>${{planet}}</strong> in ${{pData.sign}} (${{pData.degree_0_to_30}}°)<br>${{pData.whole_sign_house.replace('_', ' ')}} • ${{pData.essential_dignity}}`;
                                tooltip.style.display = 'block';
                            }}
                        }});
                        parentGroup.addEventListener('mousemove', (e) => {{
                            tooltip.style.left = (e.clientX + 14) + 'px';
                            tooltip.style.top = (e.clientY + 14) + 'px';
                        }});
                        parentGroup.addEventListener('mouseleave', () => {{
                            setHighlight(planet, false);
                            tooltip.style.display = 'none';
                        }});
                    }}
                }});
            }});
        }}
    </script>
</body>
</html>"""
    return html_template

def generate_human_readable_report(subject, ai_payload, output_dir):
    """Generates an SVG visual chart, Markdown data sheet, and an interactive HTML Dashboard."""
    
    # 1. Generate the visual SVG Chart
    chart = KerykeionChartSVG(subject)
    chart.makeSVG()
    
    # Define clean filenames
    safe_name = subject.name.replace(" ", "_")
    svg_filename = f"{safe_name}_chart.svg"
    svg_path = os.path.join(output_dir, svg_filename)
    
    # Move and read the generated SVG
    possible_default_svgs = [
        f"{subject.name}Chart.svg",
        f"{subject.name} - Natal Chart.svg",
        os.path.expanduser(f"~/{subject.name} - Natal Chart.svg"),
        os.path.expanduser(f"~/{subject.name}Chart.svg"),
    ]
    for default_svg in possible_default_svgs:
        if os.path.exists(default_svg):
            shutil.move(default_svg, svg_path)
            break

    # Read raw SVG for inlining if needed
    svg_raw_xml = ""
    if os.path.exists(svg_path):
        with open(svg_path, "r", encoding="utf-8") as svg_file:
            svg_raw_xml = svg_file.read()
        try:
            os.remove(svg_path)
        except Exception:
            pass

    # Clean up any leftover SVG files from Kerykeion in home or current directory
    for default_svg in possible_default_svgs:
        if os.path.exists(default_svg):
            try:
                os.remove(default_svg)
            except Exception:
                pass

    return ""

# --- MAIN GENERATOR ---
def generate_ai_json(
    name: str = "User", year: int = 1983, month: int = 11, day: int = 10, hour: int = 4, minute: int = 20,
    city: str = "Georgsmarienhütte", country_code: str = "DE", output_filename: str = None, silent: bool = False
):
    if not output_filename or output_filename == "chart_context.json":
        safe_name = name.replace(" ", "_")
        output_filename = f"{safe_name}_{year:04d}-{month:02d}-{day:02d}_{hour:02d}-{minute:02d}_chart_context.json"

    try:
        subject = AstrologicalSubject(
            name, year, month, day, hour, minute, city, country_code,
            geonames_username="shivapuri"
        )
    except Exception:
        subject = AstrologicalSubject(name, year, month, day, hour, minute, city, country_code)
    
    asc_sign = subject.first_house.sign
    asc_abs = subject.first_house.abs_pos
    asc_idx = ZODIAC_SIGNS.index(asc_sign)

    def get_wsh(planet_sign: str) -> str:
        return f"House_{((ZODIAC_SIGNS.index(planet_sign) - asc_idx) % 12) + 1}"

    sun_wsh = int(get_wsh(subject.sun.sign).split("_")[1])
    is_day_chart = sun_wsh in [7, 8, 9, 10, 11, 12]
    
    planets_data = {}
    for p in ["sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn"]:
        obj = getattr(subject, p)
        planets_data[obj.name] = {
            "sign": obj.sign,
            "whole_sign_house": get_wsh(obj.sign),
            "degree_0_to_30": round(obj.position, 2),
            "absolute_degree": round(obj.abs_pos, 2),
            "is_retrograde": obj.retrograde,
            "essential_dignity": get_essential_dignity(obj.name, obj.sign),
            "dorothean_triplicity": get_dorothean_triplicity(obj.sign, is_day_chart),
            "solar_phasis": get_solar_phasis(obj.name, obj.abs_pos, subject.sun.abs_pos),
            "egyptian_term_ruler": get_egyptian_term(obj.sign, obj.position),
            "dodecatemorion": calculate_dodecatemorion(obj.abs_pos)
        }

    # Hermetic Lots Calculations
    sun_abs, moon_abs = subject.sun.abs_pos, subject.moon.abs_pos
    mer_abs, ven_abs, mars_abs = subject.mercury.abs_pos, subject.venus.abs_pos, subject.mars.abs_pos
    jup_abs, sat_abs = subject.jupiter.abs_pos, subject.saturn.abs_pos

    lot_fortune = calculate_lot(asc_abs, moon_abs, sun_abs) if is_day_chart else calculate_lot(asc_abs, sun_abs, moon_abs)
    lot_spirit = calculate_lot(asc_abs, sun_abs, moon_abs) if is_day_chart else calculate_lot(asc_abs, moon_abs, sun_abs)
    
    # Advanced Hermetic Lots
    lots = {
        "Lot_of_Fortune": lot_fortune,
        "Lot_of_Spirit": lot_spirit,
        "Lot_of_Necessity": calculate_lot(asc_abs, lot_fortune["absolute_degree"], mer_abs) if is_day_chart else calculate_lot(asc_abs, mer_abs, lot_fortune["absolute_degree"]),
        "Lot_of_Eros": calculate_lot(asc_abs, ven_abs, lot_spirit["absolute_degree"]) if is_day_chart else calculate_lot(asc_abs, lot_spirit["absolute_degree"], ven_abs),
        "Lot_of_Courage": calculate_lot(asc_abs, lot_fortune["absolute_degree"], mars_abs) if is_day_chart else calculate_lot(asc_abs, mars_abs, lot_fortune["absolute_degree"]),
        "Lot_of_Victory": calculate_lot(asc_abs, jup_abs, lot_spirit["absolute_degree"]) if is_day_chart else calculate_lot(asc_abs, lot_spirit["absolute_degree"], jup_abs),
        "Lot_of_Nemesis": calculate_lot(asc_abs, lot_fortune["absolute_degree"], sat_abs) if is_day_chart else calculate_lot(asc_abs, sat_abs, lot_fortune["absolute_degree"]),
    }

    # Add House logic to lots
    for key, lot_data in lots.items():
        lot_data["whole_sign_house"] = get_wsh(lot_data["sign"])

    # --- NET VECTOR ANALYSIS (Pre-calculated Architectural Flags) ---
    chart_ruler = DOMICILES.get(asc_sign, "Sun")
    ruler_house_str = planets_data.get(chart_ruler, {}).get("whole_sign_house", "House_1")
    ruler_wsh_num = int(ruler_house_str.split("_")[1]) if "_" in ruler_house_str else 1
    
    def calculate_dampening(planet_a, planet_b, p_data):
        deg_a = p_data.get(planet_a, {}).get("absolute_degree", 0)
        deg_b = p_data.get(planet_b, {}).get("absolute_degree", 0)
        
        # Shortest distance on a 360-degree wheel
        dist = abs(deg_a - deg_b)
        dist = min(dist, 360 - dist)
        
        aspect = None
        orb = 999
        if dist <= 10:
            aspect, orb = "Conjunction", dist
        elif 80 <= dist <= 100:
            aspect, orb = "Square", abs(dist - 90)
        elif 170 <= dist <= 190:
            aspect, orb = "Opposition", abs(dist - 180)
            
        if aspect:
            intensity = "Extreme" if orb <= 3 else "Moderate" if orb <= 6 else "Mild"
            return {"is_active": True, "aspect": aspect, "orb_degrees": round(orb, 2), "intensity": intensity}
        return {"is_active": False, "aspect": "None", "orb_degrees": 0, "intensity": "None"}

    steersman_dampening = calculate_dampening(chart_ruler, "Saturn", planets_data)
    moon_dampening = calculate_dampening("Moon", "Saturn", planets_data)

    is_private_house = ruler_wsh_num in [4, 6, 8, 12]
    is_aversion = ruler_wsh_num in [2, 6, 8, 12]

    aspects_list = get_whole_sign_aspects(planets_data)

    net_vector_analysis = {
        "chart_ruler_planet": chart_ruler,
        "steersman_dampened_by_saturn": steersman_dampening,
        "moon_dampened_by_saturn": moon_dampening,
        "steersman_in_private_house": is_private_house,
        "steersman_in_aversion_to_ascendant": is_aversion
    }

    systematic_12_point_chart_audit = {
        "1_sect_leader": "Day Chart" if is_day_chart else "Night Chart",
        "2_ascendant_sign_and_degree": f"{asc_sign} ({subject.ascendant.position:.2f}°)",
        "3_steersman_chart_ruler": f"{chart_ruler} in {planets_data.get(chart_ruler, {}).get('sign')} (House {ruler_wsh_num})",
        "4_essential_dignity": planets_data.get(chart_ruler, {}).get("essential_dignity"),
        "5_dispositor_host": planets_data.get(chart_ruler, {}).get("dorothean_triplicity"),
        "6_triplicity_rulers": get_dorothean_triplicity(asc_sign, is_day_chart),
        "7_terms_and_dodecatemoria": {
            "term_ruler": planets_data.get(chart_ruler, {}).get("egyptian_term_ruler"),
            "dodecatemorion": planets_data.get(chart_ruler, {}).get("dodecatemorion")
        },
        "8_solar_phasis": planets_data.get(chart_ruler, {}).get("solar_phasis"),
        "9_hermetic_lots": lots,
        "10_whole_sign_aspects": aspects_list,
        "11_prenatal_syzygy": get_prenatal_syzygy(year, month, day, hour, minute, subject.tz_str),
        "12_net_vector_orbs_and_intensity": net_vector_analysis
    }

    ai_payload = {
        "native_details": {
            "name": subject.name,
            "ascendant": asc_sign,
            "sect": "Day Chart" if is_day_chart else "Night Chart",
            "house_system": "Whole Sign Houses (WSH)"
        },
        "systematic_12_point_chart_audit": systematic_12_point_chart_audit,
        "traditional_planets": planets_data,
        "7_hermetic_lots": lots,
        "whole_sign_aspects": aspects_list,
        "prenatal_syzygy": get_prenatal_syzygy(year, month, day, hour, minute, subject.tz_str),
        "net_vector_analysis": net_vector_analysis
    }

    with open(output_filename, "w") as outfile:
        json.dump(ai_payload, outfile, indent=4)

    # --- NEW: Generate Human-Readable Markdown and SVG ---
    # Figure out where we are saving the JSON, so we can save the MD and SVG in the same place
    output_dir = os.path.dirname(os.path.abspath(output_filename))
    if not output_dir:
        output_dir = "."
        
    try:
        report_file = generate_human_readable_report(subject, ai_payload, output_dir)
        success_msg = f"✅ Success! Data saved to {output_filename}\n✅ Interactive HTML Dashboard saved to {report_file}"
    except Exception as e:
        success_msg = f"✅ JSON saved, but failed to generate SVG/HTML report: {e}"

    if not silent:
        print(success_msg)

    return ai_payload

if __name__ == "__main__":
    generate_ai_json()
