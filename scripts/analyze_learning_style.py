#!/usr/bin/env python3
"""
analyze_learning_style.py
Evaluates an astrological chart's cognitive blueprint and learning capabilities
across the 8-Pillar Jyotish Cognitive Scale using Astra's calculation engine.
"""

import os
import sys
import argparse

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from jyotish.generate_jyotish import generate_kala_chart

def analyze_learning_style(name="Native", year=1983, month=11, day=10, hour=22, minute=20,
                           lat=52.20296, lon=8.0448, tz=1.0):
    chart = generate_kala_chart(
        name=name,
        year=year,
        month=month,
        day=day,
        hour=hour,
        minute=minute,
        latitude=lat,
        longitude=lon,
        timezone_offset=tz
    )

    d1 = chart["vargas"]["D1"]
    d9 = chart["vargas"]["D9"]
    d24 = chart["vargas"]["D24"]
    nakshatras = chart["nakshatras"]["grahas"]
    shadbala = chart["shadbala"]

    # 1. Auditory Receptive Bandwidth (Moon strength, Shravana nakshatra, Atmakaraka)
    moon_sb = shadbala.get("Moon", {})
    moon_pct = moon_sb.get("Pct_Required_Total", 100.0)
    moon_nak = nakshatras.get("Moon", {}).get("nakshatra", "")
    auditory_score = 7.0
    if moon_nak == "Shravana":
        auditory_score += 2.0
    elif moon_nak in ["Hasta", "Rohini"]:
        auditory_score += 1.0
    if moon_pct >= 140.0:
        auditory_score += 1.0
    auditory_score = min(10.0, auditory_score)

    # 2. Philosophical & Lineage Wisdom (Jupiter + Ketu, D24 Jupiter, 9th/12th)
    jup_sign = d1["grahas"]["Jupiter"]["sign"]
    ketu_sign = d1["grahas"]["Ketu"]["sign"]
    d24_jup_sign = d24["grahas"]["Jupiter"]["sign"]
    wisdom_score = 7.0
    if jup_sign == ketu_sign:
        wisdom_score += 1.5
    if jup_sign in ["Sagittarius", "Pisces"]:
        wisdom_score += 0.5
    if d24_jup_sign == "Cancer":  # Exalted in D24
        wisdom_score += 1.0
    wisdom_score = min(10.0, wisdom_score)

    # 3. Forensic Depth & Problem Solving (5th house, Scorpio, Sun+Mercury, Saturn)
    fifth_sign = ""
    for b in d1["bhavas"]:
        if b["house"] == 5:
            # check sign
            cusp = b["cusp"]
            signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
            fifth_sign = signs[int(cusp // 30)]
            break
    
    forensic_score = 7.0
    if fifth_sign in ["Scorpio", "Virgo"]:
        forensic_score += 1.5
    # check if Sun and Mercury are in 5th or conjoined
    sun_sign = d1["grahas"]["Sun"]["sign"]
    merc_sign = d1["grahas"]["Mercury"]["sign"]
    sat_sign = d1["grahas"]["Saturn"]["sign"]
    if sun_sign == merc_sign:  # Budha-Aditya
        forensic_score += 0.5
    if merc_sign == sat_sign:  # Saturn anchor
        forensic_score += 0.5
    forensic_score = min(10.0, forensic_score)

    # 4. Systems Architecture & Visual Logic (Gemini Swamsa, Air Trine D9, Venus)
    swamsa = d9["lagna"]["sign"]
    air_signs = ["Gemini", "Libra", "Aquarius"]
    systems_score = 6.5
    if swamsa in air_signs:
        systems_score += 1.5
    # check air planets in D9
    d9_air_count = sum(1 for g in d9["grahas"].values() if g["sign"] in air_signs)
    if d9_air_count >= 3:
        systems_score += 1.2
    systems_score = min(10.0, systems_score)

    # 5. Cognitive Endurance & Deep Work (Saturn strength and 5th house/Lagna)
    sat_sb = shadbala.get("Saturn", {})
    sat_pct = sat_sb.get("Pct_Required_Total", 100.0)
    endurance_score = 6.5
    if sat_pct >= 120.0:
        endurance_score += 1.0
    if sat_sign in ["Scorpio", "Capricorn", "Aquarius", "Libra"]:
        endurance_score += 1.3
    endurance_score = min(10.0, endurance_score)

    # 6. Verbal Synthesis & Teaching (Feynman Ability)
    merc_nak_ruler = "Jupiter" if nakshatras.get("Mercury", {}).get("nakshatra") == "Vishakha" else ""
    teaching_score = 7.0
    if merc_nak_ruler == "Jupiter":
        teaching_score += 1.5
    teaching_score = min(10.0, teaching_score)

    # 7. Rapid Rote Recall (Trivia / Speed)
    # Higher Saturn in 5th lowers rote speed in favor of depth
    rote_score = 4.0
    if sat_sign == merc_sign:
        rote_score -= 0.5

    # 8. Collaborative / Group Study
    group_score = 4.0
    if sun_sign in ["Scorpio", "Capricorn"] and d1["lagna"]["sign"] == "Leo":
        group_score -= 1.0

    scores = {
        "Auditory Receptive Bandwidth": auditory_score,
        "Philosophical & Lineage Wisdom": wisdom_score,
        "Forensic Research & Problem Solving": forensic_score,
        "Systems Architecture & Visual Logic": systems_score,
        "Cognitive Endurance & Deep Work": endurance_score,
        "Verbal Synthesis & Teaching": teaching_score,
        "Rapid Rote Recall (Trivia / Speed)": rote_score,
        "Collaborative / Group Study": group_score
    }

    print(f"=== COGNITIVE BLUEPRINT SCORECARD: {name} ===")
    for dim, sc in sorted(scores.items(), key=lambda x: x[1], reverse=True):
        bars = int(round(sc))
        bar_str = "█" * bars + "░" * (10 - bars)
        print(f"{dim:38s}: {sc:4.1f} / 10  [{bar_str}]")

    return scores

if __name__ == "__main__":
    analyze_learning_style()
