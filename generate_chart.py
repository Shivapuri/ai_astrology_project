from kerykeion import AstrologicalSubject
import json
import swisseph as swe
from datetime import datetime, timezone
import pytz

# Sign names list (360° zodiac order)
ZODIAC_SIGNS = ["Ari", "Tau", "Gem", "Can", "Leo", "Vir", "Lib", "Sco", "Sag", "Cap", "Aqu", "Pis"]

# Egyptian Terms (Bounds) lookup table
# Structure: Sign -> list of (max_degree, planet_ruler)
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

def get_egyptian_term(sign: str, degree_in_sign: float) -> str:
    """Returns the ruling planet of the Egyptian Term for a given degree within a sign."""
    terms = EGYPTIAN_TERMS.get(sign, [])
    for max_deg, ruler in terms:
        if degree_in_sign < max_deg:
            return ruler
    return terms[-1][1] if terms else "Unknown"

def calculate_dodecatemorion(abs_degree: float):
    """Calculates Dodecatemorion (12th part) sign and degrees."""
    deg_in_sign = abs_degree % 30
    dodec_abs = (abs_degree + (deg_in_sign * 11)) % 360
    sign_idx = int(dodec_abs // 30)
    return {
        "sign": ZODIAC_SIGNS[sign_idx],
        "degree_0_to_30": round(dodec_abs % 30, 2),
        "absolute_degree": round(dodec_abs, 2)
    }

def get_whole_sign_aspects(points_dict: dict) -> list:
    """Calculates Whole Sign Aspects between all 7 traditional planets."""
    aspects = []
    keys = list(points_dict.keys())
    
    aspect_map = {
        0: "conjunction",
        2: "sextile",
        3: "square",
        4: "trine",
        6: "opposition"
    }

    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            p1_name = keys[i]
            p2_name = keys[j]
            p1_sign = points_dict[p1_name]["sign"]
            p2_sign = points_dict[p2_name]["sign"]

            idx1 = ZODIAC_SIGNS.index(p1_sign)
            idx2 = ZODIAC_SIGNS.index(p2_sign)

            sign_dist = abs(idx1 - idx2)
            if sign_dist > 6:
                sign_dist = 12 - sign_dist

            if sign_dist in aspect_map:
                aspects.append({
                    "planet_1": p1_name,
                    "planet_2": p2_name,
                    "aspect_type": aspect_map[sign_dist],
                    "sign_distance": sign_dist
                })
    return aspects

def get_prenatal_syzygy(year: int, month: int, day: int, hour: int, minute: int, tz_str: str) -> dict:
    """Calculates the Prenatal Syzygy (New Moon or Full Moon immediately preceding birth)."""
    try:
        if not tz_str or tz_str == "None":
            tz_str = "UTC"
        tz = pytz.timezone(tz_str)
    except Exception:
        tz = timezone.utc

    try:
        local_dt = tz.localize(datetime(year, month, day, hour, minute))
        utc_dt = local_dt.astimezone(timezone.utc)
    except Exception:
        utc_dt = datetime(year, month, day, hour, minute, tzinfo=timezone.utc)

    jd_ut = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, utc_dt.hour + utc_dt.minute / 60.0)

    t = jd_ut
    step = 0.1
    prev_phase = (swe.calc_ut(t, swe.MOON)[0][0] - swe.calc_ut(t, swe.SUN)[0][0]) % 360
    prev_t = t
    target_angle = None

    while t > jd_ut - 32:
        t -= step
        phase = (swe.calc_ut(t, swe.MOON)[0][0] - swe.calc_ut(t, swe.SUN)[0][0]) % 360

        if prev_phase >= 180 and phase < 180:
            target_angle = 180.0
            t_low, t_high = t, prev_t
            break
        if prev_phase < 90 and phase > 270:
            target_angle = 0.0
            t_low, t_high = t, prev_t
            break
        prev_phase = phase
        prev_t = t

    if target_angle is None:
        return {"prenatal_syzygy": "Unknown"}

    for _ in range(25):
        t_mid = (t_low + t_high) / 2.0
        phase_m = (swe.calc_ut(t_mid, swe.MOON)[0][0] - swe.calc_ut(t_mid, swe.SUN)[0][0]) % 360
        if target_angle == 180.0:
            if phase_m >= 180.0:
                t_high = t_mid
            else:
                t_low = t_mid
        else:
            if phase_m > 180.0:
                t_high = t_mid
            else:
                t_low = t_mid

    exact_t = (t_low + t_high) / 2.0
    syz_sun = swe.calc_ut(exact_t, swe.SUN)[0][0]
    syz_moon = swe.calc_ut(exact_t, swe.MOON)[0][0]
    syz_deg = syz_moon if target_angle == 180.0 else syz_sun

    sign_idx = int(syz_deg // 30)
    return {
        "type": "Full Moon" if target_angle == 180.0 else "New Moon",
        "sign": ZODIAC_SIGNS[sign_idx],
        "degree_0_to_30": round(syz_deg % 30, 2),
        "absolute_degree": round(syz_deg, 2)
    }

def generate_ai_json(
    name: str = "User",
    year: int = 1983,
    month: int = 11,
    day: int = 10,
    hour: int = 4,
    minute: int = 20,
    city: str = "Georgsmarienhütte",
    country_code: str = "DE",
    output_filename: str = "chart_context.json"
):
    # 1. Create AstrologicalSubject
    subject = AstrologicalSubject(name, year, month, day, hour, minute, city, country_code)

    # 7 Traditional Planets only
    traditional_planets = ["sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn"]

    # Ascendant Details
    asc_sign = subject.first_house.sign
    asc_abs_deg = subject.first_house.abs_pos
    asc_sign_idx = ZODIAC_SIGNS.index(asc_sign)

    # 2. Whole Sign Houses (WSH) Calculation
    wsh_houses = {}
    for i in range(12):
        house_num = i + 1
        sign_idx = (asc_sign_idx + i) % 12
        wsh_houses[f"House_{house_num}"] = {
            "sign": ZODIAC_SIGNS[sign_idx],
            "degree_range": f"0° - 30° {ZODIAC_SIGNS[sign_idx]}"
        }

    # Helper function to compute Whole Sign House for a planet
    def get_wsh_house(planet_sign: str) -> int:
        p_sign_idx = ZODIAC_SIGNS.index(planet_sign)
        return ((p_sign_idx - asc_sign_idx) % 12) + 1

    # 3. Traditional Planets Data
    planets_data = {}
    for p in traditional_planets:
        obj = getattr(subject, p)
        abs_deg = obj.abs_pos
        deg_30 = round(obj.position, 2)
        sign = obj.sign
        wsh_h = get_wsh_house(sign)

        planets_data[obj.name] = {
            "sign": sign,
            "whole_sign_house": f"House_{wsh_h}",
            "degree_0_to_30": deg_30,
            "absolute_degree": round(abs_deg, 2),
            "is_retrograde": obj.retrograde,
            "egyptian_term_ruler": get_egyptian_term(sign, deg_30),
            "dodecatemorion": calculate_dodecatemorion(abs_deg)
        }

    # 4. Chart Sect (Day vs Night using Whole Sign Houses)
    sun_wsh = get_wsh_house(subject.sun.sign)
    is_day_chart = sun_wsh in [7, 8, 9, 10, 11, 12]
    sect_str = "Day Chart" if is_day_chart else "Night Chart"

    # 5. Calculate Lots (Fortune & Spirit)
    sun_abs = subject.sun.abs_pos
    moon_abs = subject.moon.abs_pos

    if is_day_chart:
        fortune_abs = (asc_abs_deg + moon_abs - sun_abs) % 360
        spirit_abs = (asc_abs_deg + sun_abs - moon_abs) % 360
    else:
        fortune_abs = (asc_abs_deg + sun_abs - moon_abs) % 360
        spirit_abs = (asc_abs_deg + moon_abs - sun_abs) % 360

    fortune_sign = ZODIAC_SIGNS[int(fortune_abs // 30)]
    spirit_sign = ZODIAC_SIGNS[int(spirit_abs // 30)]

    lot_of_fortune = {
        "sign": fortune_sign,
        "degree_0_to_30": round(fortune_abs % 30, 2),
        "absolute_degree": round(fortune_abs, 2),
        "whole_sign_house": f"House_{get_wsh_house(fortune_sign)}",
        "dodecatemorion": calculate_dodecatemorion(fortune_abs)
    }

    lot_of_spirit = {
        "sign": spirit_sign,
        "degree_0_to_30": round(spirit_abs % 30, 2),
        "absolute_degree": round(spirit_abs, 2),
        "whole_sign_house": f"House_{get_wsh_house(spirit_sign)}",
        "dodecatemorion": calculate_dodecatemorion(spirit_abs)
    }

    # Ascendant Dodecatemorion & Terms
    ascendant_data = {
        "sign": asc_sign,
        "degree_0_to_30": round(subject.first_house.position, 2),
        "absolute_degree": round(asc_abs_deg, 2),
        "egyptian_term_ruler": get_egyptian_term(asc_sign, round(subject.first_house.position, 2)),
        "dodecatemorion": calculate_dodecatemorion(asc_abs_deg)
    }

    # 6. Prenatal Syzygy (SAN)
    prenatal_syzygy = get_prenatal_syzygy(year, month, day, hour, minute, subject.tz_str)

    # 7. Build Hellenistic AI Payload
    ai_payload = {
        "native_details": {
            "name": subject.name,
            "sun_sign": subject.sun.sign,
            "moon_sign": subject.moon.sign,
            "ascendant": asc_sign,
            "birth_time": f"{hour:02d}:{minute:02d}",
            "location": f"{city}, {country_code}",
            "sect": sect_str,
            "house_system": "Whole Sign Houses (WSH)"
        },
        "ascendant": ascendant_data,
        "traditional_planets": planets_data,
        "lots": {
            "lot_of_fortune": lot_of_fortune,
            "lot_of_spirit": lot_of_spirit
        },
        "whole_sign_houses": wsh_houses,
        "whole_sign_aspects": get_whole_sign_aspects(planets_data),
        "prenatal_syzygy": prenatal_syzygy
    }

    # 8. Output to JSON
    with open(output_filename, "w") as outfile:
        json.dump(ai_payload, outfile, indent=4)

    print(f"✅ Success! Hellenistic astrology JSON saved to {output_filename}")

if __name__ == "__main__":
    generate_ai_json()
