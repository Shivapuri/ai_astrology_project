"""
Vedic Jyotish Chart Generator (jyotishganit Engine)
Generates high-precision Vedic astrological context (vedic_context.json) using True Chitra Paksha Ayanamsa,
Panchanga, D1 Rasi Chart, D9 Navamsa Chart, and Vimshottari Dasha timeline.
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, Any, Optional

try:
    from jyotishganit import calculate_birth_chart
except ImportError:
    print("Error: 'jyotishganit' package is not installed. Please run 'pip install jyotishganit skyfield'.")
    sys.exit(1)


def generate_vedic_chart(
    name: str = "Subject",
    year: int = 1995,
    month: int = 5,
    day: int = 15,
    hour: int = 14,
    minute: int = 30,
    latitude: float = 51.5074,
    longitude: float = -0.1278,
    timezone_offset: float = 1.0,
    output_filepath: str = "vedic_context.json"
) -> Dict[str, Any]:
    """
    Calculates complete Vedic astrology chart using jyotishganit library and exports JSON.

    :param name: Person's name
    :param year: Birth year
    :param month: Birth month (1-12)
    :param day: Birth day (1-31)
    :param hour: Birth hour (0-23)
    :param minute: Birth minute (0-59)
    :param latitude: Latitude in decimal degrees (+ North, - South)
    :param longitude: Longitude in decimal degrees (+ East, - West)
    :param timezone_offset: Timezone offset from UTC in hours (e.g. +5.5 for IST)
    :param output_filepath: Path to save the resulting JSON file
    :return: Dictionary of structured Vedic context data
    """
    birth_dt = datetime(year, month, day, hour, minute)
    
    # 1. Calculate complete birth chart using jyotishganit
    chart = calculate_birth_chart(
        birth_date=birth_dt,
        latitude=latitude,
        longitude=longitude,
        timezone_offset=timezone_offset,
        name=name
    )

    # 2. Extract Panchanga
    pancha_obj = chart.panchanga
    panchanga = {
        "tithi": getattr(pancha_obj, "tithi", None),
        "karana": getattr(pancha_obj, "karana", None),
        "yoga": getattr(pancha_obj, "yoga", None),
        "vara": getattr(pancha_obj, "vaara", getattr(pancha_obj, "vara", None)),
        "moon_nakshatra": getattr(pancha_obj, "nakshatra", getattr(pancha_obj, "moon_nakshatra", None))
    }

    # Find Moon pada from D1 planets
    moon_pada = None
    for p in chart.d1_chart.planets:
        if p.celestial_body == "Moon":
            moon_pada = getattr(p, "pada", None)
            break
    panchanga["pada"] = moon_pada

    # 3. Extract D1 Rasi Chart
    h1 = chart.d1_chart.houses[0] if chart.d1_chart.houses else None
    lagna_d1 = {}
    if h1:
        lagna_d1 = {
            "sign": getattr(h1, "sign", None),
            "degree_0_to_30": round(float(getattr(h1, "sign_degrees", 0.0)), 2),
            "nakshatra": getattr(h1, "nakshatra", None),
            "pada": getattr(h1, "pada", None)
        }

    grahas_d1 = {}
    for p in chart.d1_chart.planets:
        p_name = p.celestial_body
        dignity_obj = getattr(p, "dignities", None)
        dignity_val = getattr(dignity_obj, "dignity", str(dignity_obj)) if dignity_obj else "none"

        grahas_d1[p_name] = {
            "sign": p.sign,
            "degree_0_to_30": round(float(p.sign_degrees), 2),
            "house": p.house,
            "nakshatra": p.nakshatra,
            "pada": p.pada,
            "motion_type": getattr(p, "motion_type", "direct"),
            "dignity": dignity_val
        }

    # 4. Extract D9 Navamsa Chart
    d9_chart = chart.divisional_charts.get("d9")
    lagna_d9 = {}
    grahas_d9 = {}

    if d9_chart:
        asc_obj = getattr(d9_chart, "ascendant", None)
        if asc_obj:
            lagna_d9 = {
                "sign": getattr(asc_obj, "sign", None),
                "house": 1
            }

        # Map occupants from D9 houses
        for h in d9_chart.houses:
            h_sign = h.sign
            h_num = h.number
            for occ in h.occupants:
                grahas_d9[occ.celestial_body] = {
                    "sign": h_sign,
                    "house": h_num
                }

    # 5. Extract Vimshottari Dasha (At Birth & Current Running)
    dashas_dict = chart.dashas.to_dict()
    all_mds = dashas_dict.get("all", {}).get("mahadashas", {})

    # At Birth Dasha
    birth_md = None
    birth_ad = None
    birth_md_span = None
    birth_ad_span = None
    birth_str = birth_dt.strftime("%Y-%m-%d")

    for md_lord, md_data in all_mds.items():
        md_start = str(md_data.get("start"))[:10]
        md_end = str(md_data.get("end"))[:10]

        if md_start <= birth_str <= md_end:
            birth_md = md_lord
            birth_md_span = f"{md_start} to {md_end}"
            ads = md_data.get("antardashas", {})
            for ad_lord, ad_data in ads.items():
                ad_start = str(ad_data.get("start"))[:10]
                ad_end = str(ad_data.get("end"))[:10]
                if ad_start <= birth_str <= ad_end:
                    birth_ad = ad_lord
                    birth_ad_span = f"{ad_start} to {ad_end}"
                    break
            break

    # Current Running Dasha
    curr_dict = dashas_dict.get("current", {}).get("mahadashas", {})
    curr_md = None
    curr_ad = None
    curr_pd = None
    curr_md_end = None
    curr_ad_end = None
    curr_pd_end = None

    if curr_dict:
        for md_lord, md_data in curr_dict.items():
            curr_md = md_lord
            curr_md_end = str(md_data.get("end"))[:10]
            ads = md_data.get("antardashas", {})
            for ad_lord, ad_data in ads.items():
                curr_ad = ad_lord
                curr_ad_end = str(ad_data.get("end"))[:10]
                pds = ad_data.get("pratyantardashas", {})
                for pd_lord, pd_data in pds.items():
                    curr_pd = pd_lord
                    curr_pd_end = str(pd_data.get("end"))[:10]
                    break
                break
            break

    # 6. Assemble Final Clean JSON Context Structure
    vedic_context = {
        "subject_info": {
            "name": name,
            "birth_datetime": birth_dt.isoformat(),
            "latitude": latitude,
            "longitude": longitude,
            "timezone_offset": timezone_offset
        },
        "ayanamsa": {
            "name": getattr(chart.ayanamsa, "name", "True Chitra Paksha (Lahiri)"),
            "value_degrees": round(float(getattr(chart.ayanamsa, "value", 0.0)), 4)
        },
        "panchanga": panchanga,
        "d1_rasi_chart": {
            "lagna": lagna_d1,
            "grahas": grahas_d1
        },
        "d9_navamsa_chart": {
            "lagna": lagna_d9,
            "grahas": grahas_d9
        },
        "vimshottari_dasha": {
            "at_birth": {
                "mahadasha": birth_md,
                "antardasha": birth_ad,
                "mahadasha_period": birth_md_span,
                "antardasha_period": birth_ad_span
            },
            "current_running": {
                "calculated_date": datetime.now().strftime("%Y-%m-%d"),
                "mahadasha": curr_md,
                "antardasha": curr_ad,
                "pratyantardasha": curr_pd,
                "mahadasha_ends": curr_md_end,
                "antardasha_ends": curr_ad_end,
                "pratyantardasha_ends": curr_pd_end
            }
        }
    }

    # 7. Write to file
    with open(output_filepath, "w", encoding="utf-8") as f:
        json.dump(vedic_context, f, indent=2, ensure_ascii=False)

    print(f"Successfully generated Vedic astrology context: {output_filepath}")
    return vedic_context


if __name__ == "__main__":
    generate_vedic_chart(
        name="Arjuna",
        year=1995,
        month=5,
        day=15,
        hour=14,
        minute=30,
        latitude=28.6139,   # New Delhi
        longitude=77.2090,
        timezone_offset=5.5,
        output_filepath="vedic_context.json"
    )
