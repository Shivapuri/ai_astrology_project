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

def generate_human_readable_report(subject, ai_payload, output_dir):
    """Generates an SVG visual chart and a human-readable Markdown data sheet."""
    
    # 1. Generate the visual SVG Chart
    # Kerykeion automatically creates a file named "{SubjectName}Chart.svg" in the current directory
    chart = KerykeionChartSVG(subject)
    chart.makeSVG()
    
    # Define clean filenames
    safe_name = subject.name.replace(" ", "_")
    svg_filename = f"{safe_name}_chart.svg"
    svg_path = os.path.join(output_dir, svg_filename)
    
    # Move the generated SVG to our target output directory
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

    # 2. Generate the Markdown (.md) Data Sheet
    md_filename = os.path.join(output_dir, f"{safe_name}_data_sheet.md")

    with open(md_filename, "w", encoding="utf-8") as f:
        f.write(f"# Astrological Data Sheet: {subject.name}\n\n")
        
        # Embed the SVG graphic via Markdown image syntax
        f.write(f"![Birth Chart]({svg_filename})\n\n")
        
        f.write("## 1. Core Architecture\n")
        f.write(f"- **Ascendant (Rising Sign):** {ai_payload['native_details']['ascendant']}\n")
        f.write(f"- **Sect:** {ai_payload['native_details']['sect']}\n")
        f.write(f"- **House System:** {ai_payload['native_details']['house_system']}\n\n")
        
        f.write("## 2. Planetary Placements & Dignities\n")
        f.write("| Planet | Sign | House | Degree | Dignity | Phasis (Visibility) |\n")
        f.write("|---|---|---|---|---|---|\n")
        
        for planet, data in ai_payload['traditional_planets'].items():
            f.write(f"| **{planet}** | {data['sign']} | {data['whole_sign_house'].replace('_', ' ')} | {data['degree_0_to_30']}° | {data['essential_dignity']} | {data['solar_phasis']} |\n")
        
        f.write("\n## 3. Major Aspects (Friction & Flow)\n")
        if ai_payload['whole_sign_aspects']:
            for aspect in ai_payload['whole_sign_aspects']:
                f.write(f"- **{aspect['planet_1']}** is in a **{aspect['aspect_type'].title()}** with **{aspect['planet_2']}**\n")
        else:
            f.write("- No major traditional whole sign aspects found.\n")
            
        f.write("\n## 4. Hermetic Lots\n")
        for lot, data in ai_payload['7_hermetic_lots'].items():
            f.write(f"- **{lot.replace('_', ' ')}**: {data['sign']} ({data['degree_0_to_30']}°) in {data['whole_sign_house'].replace('_', ' ')}\n")

    return md_filename

# --- MAIN GENERATOR ---
def generate_ai_json(
    name: str = "User", year: int = 1983, month: int = 11, day: int = 10, hour: int = 4, minute: int = 20,
    city: str = "Georgsmarienhütte", country_code: str = "DE", output_filename: str = "chart_context.json", silent: bool = False
):
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

    ai_payload = {
        "native_details": {
            "name": subject.name,
            "ascendant": asc_sign,
            "sect": "Day Chart" if is_day_chart else "Night Chart",
            "house_system": "Whole Sign Houses (WSH)"
        },
        "traditional_planets": planets_data,
        "7_hermetic_lots": lots,
        "whole_sign_aspects": get_whole_sign_aspects(planets_data),
        "prenatal_syzygy": get_prenatal_syzygy(year, month, day, hour, minute, subject.tz_str)
    }

    with open(output_filename, "w") as outfile:
        json.dump(ai_payload, outfile, indent=4)

    # --- NEW: Generate Human-Readable Markdown and SVG ---
    # Figure out where we are saving the JSON, so we can save the MD and SVG in the same place
    output_dir = os.path.dirname(os.path.abspath(output_filename))
    if not output_dir:
        output_dir = "."
        
    try:
        md_file = generate_human_readable_report(subject, ai_payload, output_dir)
        success_msg = f"✅ Success! Data saved to {output_filename}\n✅ Human Data Sheet & SVG saved to {md_file}"
    except Exception as e:
        success_msg = f"✅ JSON saved, but failed to generate SVG/MD report: {e}"

    if not silent:
        print(success_msg)

if __name__ == "__main__":
    generate_ai_json()
