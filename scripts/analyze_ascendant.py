#!/usr/bin/env python3
"""
analyze_ascendant.py
--------------------
Precision Ascendant (Lagna) and 1st House analysis engine for Astra.
Synthesizes classical Parashari principles, Vic DiCara's solar sky mechanics,
Ryan Kurczak's teachings, and Ernst Wilhelm's Kala integrated approach.

Evaluates the 7 core pillars:
1. Rising Sign (Rasi) & Environmental Container
2. Campanus Cusp Degree & Exact 3D Focus Point
3. Ascendant Nakshatra, Pada, and Mythic Archetype
4. Inhabiting Planets & Aspectual Pressure (Virupas & Kartari)
5. Ascendant Lord (Lagnesha) Dignity, Placement & Avasthas
6. The Sun (Surya) as Sthira Karaka & Sudarshana Chakra Alignment
7. Functional Planetary Matrix (Yoga Karakas, Trishadaya & Marakas)
"""

import os
import sys
import json
import argparse
from typing import Dict, Any, List, Optional

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from jyotish.generate_jyotish import generate_kala_chart
from jyotish import native_manager
from app import compute_chart_data

CHARTS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "database", "Charts.jsonl")

SIGN_METADATA = {
    "Aries": {"element": "Fire (Agni)", "modality": "Cardinal (Chara)", "polarity": "Odd / Externalizing", "ruler": "Mars", "archetype": "Pioneering warrior, bold initiative, action-oriented catalyst"},
    "Taurus": {"element": "Earth (Prithvi)", "modality": "Fixed (Sthira)", "polarity": "Even / Internalizing", "ruler": "Venus", "archetype": "Grounded builder, steady endurance, aesthetic stability"},
    "Gemini": {"element": "Air (Vayu)", "modality": "Mutable (Dwisvabhava)", "polarity": "Odd / Externalizing", "ruler": "Mercury", "archetype": "Inquisitive connector, versatile intellect, communication"},
    "Cancer": {"element": "Water (Jala)", "modality": "Cardinal (Chara)", "polarity": "Even / Internalizing", "ruler": "Moon", "archetype": "Nurturing protector, emotional intuition, protective sanctuary"},
    "Leo": {"element": "Fire (Agni)", "modality": "Fixed (Sthira)", "polarity": "Odd / Externalizing", "ruler": "Sun", "archetype": "Sovereign leader, radiant magnanimity, dignified nobility"},
    "Virgo": {"element": "Earth (Prithvi)", "modality": "Mutable (Dwisvabhava)", "polarity": "Even / Internalizing", "ruler": "Mercury", "archetype": "Analytical craftsman, diagnostic precision, practical service"},
    "Libra": {"element": "Air (Vayu)", "modality": "Cardinal (Chara)", "polarity": "Odd / Externalizing", "ruler": "Venus", "archetype": "Diplomatic harmonizer, ethical balance, social architect"},
    "Scorpio": {"element": "Water (Jala)", "modality": "Fixed (Sthira)", "polarity": "Even / Internalizing", "ruler": "Mars", "archetype": "Penetrating investigator, emotional depth, alchemical transformer"},
    "Sagittarius": {"element": "Fire (Agni)", "modality": "Mutable (Dwisvabhava)", "polarity": "Odd / Externalizing", "ruler": "Jupiter", "archetype": "Philosophical explorer, higher truth seeker, inspirational mentor"},
    "Capricorn": {"element": "Earth (Prithvi)", "modality": "Cardinal (Chara)", "polarity": "Even / Internalizing", "ruler": "Saturn", "archetype": "Pragmatic strategist, disciplined perseverance, systemic achievement"},
    "Aquarius": {"element": "Air (Vayu)", "modality": "Fixed (Sthira)", "polarity": "Odd / Externalizing", "ruler": "Saturn", "archetype": "Universal visionary, humanitarian networker, structural reformer"},
    "Pisces": {"element": "Water (Jala)", "modality": "Mutable (Dwisvabhava)", "polarity": "Even / Internalizing", "ruler": "Jupiter", "archetype": "Transcendental mystic, boundless compassion, spiritual surrender"}
}

SIGN_LIST = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

def evaluate_ascendant(chart: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyzes all dimensions of the Ascendant and 1st House from an Astra chart payload.
    """
    d1 = chart["vargas"]["D1"]
    lagna_info = d1["lagna"]
    rising_sign = lagna_info["sign"]
    rising_deg = lagna_info["degree_0_to_30"]
    rising_lon = lagna_info["longitude"]
    nakshatra = lagna_info.get("nakshatra", "Unknown")
    pada = lagna_info.get("pada", 1)
    nak_lord = lagna_info.get("nakshatra_lord", "Unknown")
    sub_lord = lagna_info.get("sub_lord", "Unknown")
    
    # 1. Sign Meta
    meta = SIGN_METADATA.get(rising_sign, {})
    lagnesha_name = meta.get("ruler", "Unknown")

    # 2. Bhava 1 Campanus Geometry
    bhava_1 = next((b for b in d1.get("bhavas", []) if b["house"] == 1), {})
    cusp_deg = bhava_1.get("cusp", rising_lon)
    b1_start = bhava_1.get("start", (rising_lon - 15) % 360)
    b1_end = bhava_1.get("end", (rising_lon + 15) % 360)

    # 3. Inhabitants of 1st House
    # A) Whole sign occupants
    whole_sign_occupants = []
    # B) Campanus bhava occupants
    campanus_occupants = []
    
    for g_name, g_data in d1.get("grahas", {}).items():
        # Whole sign check
        if g_data.get("sign") == rising_sign:
            # Distance from rising cusp degree
            dist_to_cusp = abs(g_data.get("degree_0_to_30", 0.0) - rising_deg)
            whole_sign_occupants.append({
                "graha": g_name,
                "degree": g_data.get("degree_0_to_30", 0.0),
                "distance_to_cusp": round(dist_to_cusp, 2),
                "is_conjoined_cusp": dist_to_cusp <= 5.0,
                "is_retrograde": g_data.get("is_retrograde", False),
                "dignity": g_data.get("dignity_breakdown", {}).get("final_dignity", "Neutral")
            })
        
        # Campanus Bhava check
        g_lon = g_data.get("longitude", 0.0)
        # Check if g_lon falls between b1_start and b1_end
        in_campanus = False
        if b1_start < b1_end:
            in_campanus = (b1_start <= g_lon <= b1_end)
        else:
            in_campanus = (g_lon >= b1_start or g_lon <= b1_end)
        if in_campanus:
            campanus_occupants.append(g_name)

    # 4. Aspects on 1st Cusp / Lagna
    adv_aspects = chart.get("advanced_aspects", {})
    h1_cusp_aspects = adv_aspects.get("cusps", {}).get(1, {}) or adv_aspects.get("cusps", {}).get("1", {})
    cusp_totals = adv_aspects.get("totals", {}).get("cusps", {}).get(1, {}) or adv_aspects.get("totals", {}).get("cusps", {}).get("1", {})

    # Kartari Yoga check (adjacent signs 12 and 2)
    sign_idx = SIGN_LIST.index(rising_sign)
    sign_12 = SIGN_LIST[(sign_idx - 1) % 12]
    sign_2 = SIGN_LIST[(sign_idx + 1) % 12]

    planets_12 = [g for g, d in d1.get("grahas", {}).items() if d.get("sign") == sign_12]
    planets_2 = [g for g, d in d1.get("grahas", {}).items() if d.get("sign") == sign_2]

    natural_malefics = ["Mars", "Saturn", "Sun", "Rahu", "Ketu"]
    natural_benefics = ["Jupiter", "Venus", "Moon", "Mercury"]

    malefics_in_12 = [p for p in planets_12 if p in natural_malefics]
    malefics_in_2 = [p for p in planets_2 if p in natural_malefics]
    benefics_in_12 = [p for p in planets_12 if p in natural_benefics]
    benefics_in_2 = [p for p in planets_2 if p in natural_benefics]

    kartari = "Neutral / Free"
    if malefics_in_12 and malefics_in_2:
        kartari = "Papa Kartari (Hemmed by Malefics - Obstacles & Pressure)"
    elif benefics_in_12 and benefics_in_2:
        kartari = "Shubha Kartari (Hemmed by Benefics - Protected & Nourished)"
    elif malefics_in_12 or malefics_in_2:
        kartari = "Partial Malefic Hemming"

    # 5. Ascendant Lord (Lagnesha) Status
    lagnesha_data = d1.get("grahas", {}).get(lagnesha_name, {})
    lagnesha_sign = lagnesha_data.get("sign", "Unknown")
    lagnesha_deg = lagnesha_data.get("degree_0_to_30", 0.0)
    lagnesha_sign_idx = SIGN_LIST.index(lagnesha_sign) if lagnesha_sign in SIGN_LIST else 0
    lagnesha_house_ws = ((lagnesha_sign_idx - sign_idx) % 12) + 1
    
    # Campanus house of Lagnesha
    lagnesha_house_camp = 1
    for b in d1.get("bhavas", []):
        h_num = b["house"]
        s = b["start"]
        e = b["end"]
        g_lon = lagnesha_data.get("longitude", 0.0)
        if s < e:
            if s <= g_lon <= e:
                lagnesha_house_camp = h_num
                break
        else:
            if g_lon >= s or g_lon <= e:
                lagnesha_house_camp = h_num
                break

    lagnesha_dignity = lagnesha_data.get("dignity_breakdown", {}).get("final_dignity", "Neutral")
    lagnesha_avasthas = lagnesha_data.get("avasthas", {})
    
    # Shadbala
    shadbala_all = chart.get("shadbala", {})
    lagnesha_sb = shadbala_all.get(lagnesha_name, {})
    lagnesha_sb_pct = lagnesha_sb.get("Pct_Required_Total", 100.0)

    is_lagnesha_combust = lagnesha_data.get("is_combust", False)

    # 6. The Sun (Surya) as Sthira Karaka & Sudarshana Chakra
    sun_data = d1.get("grahas", {}).get("Sun", {})
    sun_sign = sun_data.get("sign", "Unknown")
    sun_deg = sun_data.get("degree_0_to_30", 0.0)
    sun_sign_idx = SIGN_LIST.index(sun_sign) if sun_sign in SIGN_LIST else 0
    sun_house_ws = ((sun_sign_idx - sign_idx) % 12) + 1
    
    # Campanus house of Sun
    sun_house_camp = 1
    for b in d1.get("bhavas", []):
        h_num = b["house"]
        s = b["start"]
        e = b["end"]
        g_lon = sun_data.get("longitude", 0.0)
        if s < e:
            if s <= g_lon <= e:
                sun_house_camp = h_num
                break
        else:
            if g_lon >= s or g_lon <= e:
                sun_house_camp = h_num
                break

    sun_dignity = sun_data.get("dignity_breakdown", {}).get("final_dignity", "Neutral")
    sun_sb = shadbala_all.get("Sun", {})
    sun_sb_pct = sun_sb.get("Pct_Required_Total", 100.0)
    sun_digbala_pct = sun_sb.get("Pct_Required_Dig", 0.0)
    sun_lajjitadi = [av.get("state") for av in sun_data.get("avasthas", {}).get("lajjitadi", [])]

    # Sun Conjunctions & Combustion Field
    sun_conjunctions = [g for g, gd in d1.get("grahas", {}).items() if g != "Sun" and gd.get("sign") == sun_sign]
    combust_planets = [g for g, gd in d1.get("grahas", {}).items() if g != "Sun" and gd.get("is_combust", False)]
    is_karaka_lagnesha_identical = (lagnesha_name == "Sun")

    # Solar Yogas (Phaladeepika 6.8-13: Vesi, Vasi, Ubhayachari)
    sign_2nd_from_sun = SIGN_LIST[(sun_sign_idx + 1) % 12]
    sign_12th_from_sun = SIGN_LIST[(sun_sign_idx - 1) % 12]
    planets_2nd_from_sun = [g for g, gd in d1.get("grahas", {}).items() if g not in ["Sun", "Moon", "Rahu", "Ketu"] and gd.get("sign") == sign_2nd_from_sun]
    planets_12th_from_sun = [g for g, gd in d1.get("grahas", {}).items() if g not in ["Sun", "Moon", "Rahu", "Ketu"] and gd.get("sign") == sign_12th_from_sun]

    solar_yogas = []
    if planets_2nd_from_sun and planets_12th_from_sun:
        solar_yogas.append(f"Ubhayachari Yoga (Flanked by {', '.join(planets_12th_from_sun)} in 12th & {', '.join(planets_2nd_from_sun)} in 2nd)")
    elif planets_2nd_from_sun:
        solar_yogas.append(f"Vesi Yoga (Supported by {', '.join(planets_2nd_from_sun)} in 2nd from Sun)")
    elif planets_12th_from_sun:
        solar_yogas.append(f"Vasi Yoga (Guided by {', '.join(planets_12th_from_sun)} in 12th from Sun)")
    else:
        solar_yogas.append("None")


    # Moon (Chandra Lagna)
    moon_data = d1.get("grahas", {}).get("Moon", {})
    moon_sign = moon_data.get("sign", "Unknown")

    # 7. Functional Roles Matrix
    functional_matrix = {
        "yogakaraka": None,
        "functional_benefics": [],
        "functional_malefics": [],
        "trishadaya_troublemakers": [],
        "marakas": [],
        "dusthana_lords": []
    }

    for g_name, g_info in d1.get("grahas", {}).items():
        f_role = g_info.get("functional_role", {})
        if f_role.get("is_yogakaraka"):
            functional_matrix["yogakaraka"] = g_name
        if f_role.get("is_trishadaya"):
            functional_matrix["trishadaya_troublemakers"].append(g_name)
        if f_role.get("is_maraka"):
            functional_matrix["marakas"].append(g_name)
        if f_role.get("is_dusthana"):
            functional_matrix["dusthana_lords"].append(g_name)
        
        status = f_role.get("status", "")
        if "Benefic" in status and g_name not in functional_matrix["functional_benefics"]:
            functional_matrix["functional_benefics"].append(g_name)
        elif "Malefic" in status and g_name not in functional_matrix["functional_malefics"]:
            functional_matrix["functional_malefics"].append(g_name)

    # D9 Navamsa Lagna (Swamsa)
    d9 = chart.get("vargas", {}).get("D9", {})
    swamsa = d9.get("lagna", {}).get("sign", "Unknown")

    # Official Astra Lagna Vitality & Diagnostic Engine (jyotish.planetary_evaluation.lagna_evaluation)
    lagna_eval = chart.get("planetary_evaluation", {}).get("lagna_evaluation")
    if not lagna_eval:
        from jyotish.planetary_evaluation.lagna_evaluation import evaluate_lagna_vitality
        lagna_eval = evaluate_lagna_vitality(
            chart.get("vargas", {}),
            chart.get("shadbala"),
            chart.get("advanced_aspects"),
            varga="D1"
        )

    vitality_score = lagna_eval.get("vitality_score", 5.0)
    vitality_tier = lagna_eval.get("vitality_tier", "Capable Vessel")
    vitality_class = lagna_eval.get("vitality_class", "capable")
    archetype = lagna_eval.get("archetype", "The Steady Navigator")
    verdict = lagna_eval.get("verdict", "")
    pillar_scores = lagna_eval.get("pillar_scores", {})
    audit_trail = lagna_eval.get("audit_trail", {})

    return {
        "subject_name": chart.get("subject_info", {}).get("name", "Native"),
        "rising_sign": rising_sign,
        "rising_degree": round(rising_deg, 2),
        "rising_longitude": round(rising_lon, 2),
        "sign_meta": meta,
        "nakshatra": nakshatra,
        "pada": pada,
        "nakshatra_lord": nak_lord,
        "sub_lord": sub_lord,
        "bhava_1_campanus": {
            "cusp": round(cusp_deg, 2),
            "start": round(b1_start, 2),
            "end": round(b1_end, 2),
            "campanus_occupants": campanus_occupants
        },
        "whole_sign_occupants": whole_sign_occupants,
        "kartari_yoga": kartari,
        "aspects_on_cusp": h1_cusp_aspects,
        "aspect_totals": cusp_totals,
        "lagnesha": {
            "planet": lagnesha_name,
            "sign": lagnesha_sign,
            "degree": round(lagnesha_deg, 2),
            "house_whole_sign": lagnesha_house_ws,
            "house_campanus": lagnesha_house_camp,
            "dignity": lagnesha_dignity,
            "shadbala_pct": round(lagnesha_sb_pct, 1),
            "is_combust": is_lagnesha_combust,
            "avasthas": {
                "bala": lagnesha_avasthas.get("bala", {}).get("state"),
                "jagrat": lagnesha_avasthas.get("jagrat", {}).get("state"),
                "deeptadi": lagnesha_avasthas.get("deeptadi", {}).get("state"),
                "lajjitadi": [av.get("state") for av in lagnesha_avasthas.get("lajjitadi", [])]
            }
        },
        "sun_karaka": {
            "sign": sun_sign,
            "degree": round(sun_deg, 2),
            "house_whole_sign": sun_house_ws,
            "house_campanus": sun_house_camp,
            "dignity": sun_dignity,
            "shadbala_pct": round(sun_sb_pct, 1),
            "digbala_pct": round(sun_digbala_pct, 1),
            "lajjitadi": sun_lajjitadi,
            "conjunctions": sun_conjunctions,
            "combust_planets": combust_planets,
            "is_karaka_lagnesha_identical": is_karaka_lagnesha_identical,
            "solar_yogas": solar_yogas
        },
        "sudarshana_chakra": {
            "janma_lagna": rising_sign,
            "chandra_lagna": moon_sign,
            "surya_lagna": sun_sign
        },
        "swamsa_d9": swamsa,
        "functional_matrix": functional_matrix,
        "vitality_score": vitality_score,
        "vitality_tier": vitality_tier,
        "vitality_class": vitality_class,
        "archetype": archetype,
        "verdict": verdict,
        "pillar_scores": pillar_scores,
        "audit_trail": audit_trail
    }

def print_cli_report(res: Dict[str, Any]):
    print("=" * 75)
    print(f"       ☀️ ASCENDANT (LAGNA) & 1ST HOUSE REPORT: {res['subject_name']} ☀️")
    print("=" * 75)
    print(f"🌅 RISING SIGN (RASI):    {res['rising_sign']} ({res['rising_degree']}°)")
    meta = res['sign_meta']
    print(f"   • Element & Quality:   {meta.get('element')} | {meta.get('modality')} | {meta.get('polarity')}")
    print(f"   • Core Archetype:      {meta.get('archetype')}")
    print(f"   • Nakshatra (Middle Mula / Dhruva): {res['nakshatra']} (Pada {res['pada']}) [Lord: {res['nakshatra_lord']}, Sub-Lord: {res['sub_lord']}]")
    print(f"   • Campanus 1st Bhava:  Cusp {res['bhava_1_campanus']['cusp']}° (Span: {res['bhava_1_campanus']['start']}° -> {res['bhava_1_campanus']['end']}°)")
    print(f"   • Navamsha Swamsa(D9): {res['swamsa_d9']}")

    print("\n" + "-" * 75)
    print("🪐 1ST HOUSE INHABITANTS & CUSP CONTACT")
    print("-" * 75)
    ws_occ = res['whole_sign_occupants']
    if ws_occ:
        for occ in ws_occ:
            conjoint_str = "🔥 CRITICAL CONJUNCTION (<5° from Cusp)" if occ['is_conjoined_cusp'] else "Normal Sign Presence"
            retro_str = " [Rx]" if occ['is_retrograde'] else ""
            print(f"   • {occ['graha']}{retro_str} at {occ['degree']}° {res['rising_sign']} | Dignity: {occ['dignity']}")
            print(f"     -> Distance to Cusp: {occ['distance_to_cusp']}° | Status: {conjoint_str}")
    else:
        print("   • No planets in the 1st Whole-Sign house (Field is clean; results filtered via Lord).")
    
    camp_occ = res['bhava_1_campanus']['campanus_occupants']
    print(f"   • Campanus Bhava 1 Occupants: {', '.join(camp_occ) if camp_occ else 'None (Empty 3D Sector)'}")
    print(f"   • Hemming (Kartari Yoga):    {res['kartari_yoga']}")

    print("\n" + "-" * 75)
    print("👁️ ASPECTS (DRISHTI) ON 1ST HOUSE CUSP (VIRUPAS: 0-60)")
    print("-" * 75)
    totals = res['aspect_totals']
    print(f"   • Net Aspect Strength: {totals.get('net', 0.0):+5.2f} Virupas (Benefic Ray: +{totals.get('plus', 0.0):.2f}, Malefic Ray: -{totals.get('minus', 0.0):.2f})")
    for g, asp in res['aspects_on_cusp'].items():
        if asp.get('raw', 0) > 0:
            print(f"   • {g:9s}: Raw {asp['raw']:5.2f} | Benefic +{asp['plus']:5.2f} | Malefic -{asp['minus']:5.2f} | Net {asp['net']:+5.2f}")

    print("\n" + "-" * 75)
    print("👑 ASCENDANT LORD (LAGNESHA) - THE DRIVER OF THE VEHICLE")
    print("-" * 75)
    lord = res['lagnesha']
    print(f"   • Ruling Planet:       {lord['planet']}")
    print(f"   • Placement:           House {lord['house_whole_sign']} (Whole Sign) / House {lord['house_campanus']} (Campanus) in {lord['sign']} ({lord['degree']}°)")
    print(f"   • Essential Dignity:   {lord['dignity']}")
    print(f"   • Shadbala Strength:   {lord['shadbala_pct']}% of required minimum")
    print(f"   • Combustion Status:   {'Combust (Scorched by Sun)' if lord['is_combust'] else 'Clear / Free from Combustion'}")
    av = lord['avasthas']
    print(f"   • Avasthas:            Bala: {av['bala']} | Jagrat: {av['jagrat']} | Deeptadi: {av['deeptadi']}")
    print(f"                          Lajjitadi States: {', '.join(av['lajjitadi']) if av['lajjitadi'] else 'None'}")

    print("\n" + "-" * 75)
    print("☀️ THE SUN (SURYA) - 1ST HOUSE KARAKA & SOUL VITALITY")
    print("-" * 75)
    sun = res['sun_karaka']
    print(f"   • Placement:           House {sun['house_whole_sign']} (Whole Sign) / House {sun['house_campanus']} (Campanus) in {sun['sign']} ({sun['degree']}°)")
    print(f"   • Essential Dignity:   {sun['dignity']}")
    print(f"   • Shadbala & Digbala:  Shadbala: {sun['shadbala_pct']}% quota | Digbala: {sun['digbala_pct']}% quota")
    print(f"   • Conjunctions:        {', '.join(sun['conjunctions']) if sun['conjunctions'] else 'None'}")
    print(f"   • Combustion Field:    Combusting: {', '.join(sun['combust_planets']) if sun['combust_planets'] else 'None'}")
    print(f"   • Solar Yogas:         {', '.join(sun['solar_yogas'])}")
    confl_str = "👑 Double Confluence (Karaka-Lord Identity: Sun is both Lagnesha & 1st House Karaka)" if sun['is_karaka_lagnesha_identical'] else f"⚖️ Dual Governance (Lagnesha is {res['lagnesha']['planet']}; Sun is independent Sthira Karaka)"
    print(f"   • Karaka Relationship: {confl_str}")
    print(f"   • Lajjitadi States:    {', '.join(sun['lajjitadi']) if sun['lajjitadi'] else 'None'}")

    print("\n" + "-" * 75)
    print("☸️ SUDARSHANA CHAKRA (THE THREE-FOLD VISION)")
    print("-" * 75)
    sc = res['sudarshana_chakra']
    print(f"   • Janma Lagna (Physical Body / Events):  {sc['janma_lagna']}")
    print(f"   • Chandra Lagna (Emotional Mind / Mood): {sc['chandra_lagna']}")
    print(f"   • Surya Lagna (Soul Purpose / Stature):  {sc['surya_lagna']}")

    print("\n" + "-" * 75)
    print("⚖️ FUNCTIONAL PLANETARY ALLIANCES FOR THIS ASCENDANT")
    print("-" * 75)
    fmat = res['functional_matrix']
    yk = fmat['yogakaraka']
    print(f"   • Yoga Karaka (Crown Champion):     {yk if yk else 'None (Power distributed among allies)'}")
    print(f"   • Functional Benefics (Trines):     {', '.join(fmat['functional_benefics'])}")
    print(f"   • Functional Malefics:              {', '.join(fmat['functional_malefics'])}")
    print(f"   • Trishadaya Lords (Hurdles 3/6/11):{', '.join(fmat['trishadaya_troublemakers'])}")
    print(f"   • Maraka Lords (Health/Longevity):  {', '.join(fmat['marakas'])}")

    print("\n" + "=" * 75)
    print("🏛️ OFFICIAL MASTER GRAHA DIAGNOSTICS: LAGNA VITALITY EVALUATION")
    print("=" * 75)
    v_score = res['vitality_score']
    bars = int(round(v_score))
    bar_str = "█" * bars + "░" * (10 - bars)
    print(f"🏆 COMPOSITE VITALITY SCORE: {v_score:3.1f} / 10.0 [{bar_str}]")
    print(f"🏷️ VITALITY CLASSIFICATION:   {res['vitality_tier'].upper()} ({res['vitality_class'].capitalize()})")
    print(f"🎭 DIAGNOSTIC ARCHETYPE:     {res['archetype']}")
    print(f"📜 CLINICAL VERDICT:         {res['verdict']}")
    
    ps = res.get('pillar_scores', {})
    print("\n📊 5-PILLAR MATHEMATICAL AUDIT BREAKDOWN:")
    print(f"   • Base Starting Score:                {ps.get('base_score', 5.0):+4.1f} pts")
    print(f"   • Pillar 1 (The Captain - Lagnesha):  {ps.get('pillar_1_captain', 0.0):+4.1f} pts")
    print(f"   • Pillar 2 (The Field Placement):     {ps.get('pillar_2_field', 0.0):+4.1f} pts")
    print(f"   • Pillar 3 (Horizon Occupants):       {ps.get('pillar_3_occupants', 0.0):+4.1f} pts")
    print(f"   • Pillar 4 (Sky-Light & Vitality):    {ps.get('pillar_4_skylight', 0.0):+4.1f} pts")
    print(f"   • Pillar 5 (Environmental Enclosure): {ps.get('pillar_5_enclosure', 0.0):+4.1f} pts")
    print(f"   ------------------------------------------------")
    print(f"   = TOTAL COMPOSITE SCORE:               {v_score:4.1f} / 10.0")

    audit = res.get('audit_trail', {})
    if audit:
        print("\n🔍 DETAILED CLINICAL AUDIT TRAIL:")
        for p_name, notes in [
            ("Pillar 1 (The Captain)", audit.get("p1_captain", [])),
            ("Pillar 2 (The Field)", audit.get("p2_field", [])),
            ("Pillar 3 (The Occupants)", audit.get("p3_occupants", [])),
            ("Pillar 4 (Sky-Light & Karaka)", audit.get("p4_skylight", [])),
            ("Pillar 5 (The Enclosure)", audit.get("p5_enclosure", []))
        ]:
            if notes:
                print(f"   [{p_name}]")
                for n in notes:
                    print(f"     • {n}")
    print("=" * 75)

def main():
    parser = argparse.ArgumentParser(description="Analyze Ascendant (Lagna) and 1st House for a native.")
    parser.add_argument("--native", type=str, default="Shivapuri", help="Name or UUID of native from database/Charts.jsonl")
    parser.add_argument("--json", action="store_true", help="Output raw JSON data payload")
    parser.add_argument("--year", type=int, help="Year of birth")
    parser.add_argument("--month", type=int, help="Month of birth")
    parser.add_argument("--day", type=int, help="Day of birth")
    parser.add_argument("--hour", type=int, help="Hour of birth (0-23)")
    parser.add_argument("--minute", type=int, help="Minute of birth (0-59)")
    parser.add_argument("--lat", type=float, help="Latitude")
    parser.add_argument("--lon", type=float, help="Longitude")
    parser.add_argument("--tz", type=float, help="Timezone offset")
    args = parser.parse_args()

    if args.year and args.month and args.day and args.lat is not None and args.lon is not None:
        chart = generate_kala_chart(
            name="Custom Native",
            year=args.year,
            month=args.month,
            day=args.day,
            hour=args.hour or 12,
            minute=args.minute or 0,
            latitude=args.lat,
            longitude=args.lon,
            timezone_offset=args.tz if args.tz is not None else 0.0
        )
    else:
        native = native_manager.get_native_by_id(CHARTS_FILE, args.native)
        if not native:
            print(f"Error: Native '{args.native}' not found in {CHARTS_FILE}")
            sys.exit(1)
        chart = compute_chart_data(native)

    res = evaluate_ascendant(chart)

    if args.json:
        print(json.dumps(res, indent=2))
    else:
        print_cli_report(res)

if __name__ == "__main__":
    main()
