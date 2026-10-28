#!/usr/bin/env python3
"""
Regenerates houses_of_life_evaluation_donald_trump.txt using Astra's ChartPipeline
and text exporter, perfectly reflecting the updated Houses of Life engine.
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app
from jyotish.text_exporter import generate_chart_ai_markdown

CLASSICAL_PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

def generate_dossier():
    client = app.test_client()
    res = client.get('/api/chart/9bb691ba-c4fd-40f1-83eb-289b4e275ac8')
    assert res.status_code == 200, f"Failed to fetch chart: {res.status_code}"
    data = res.get_json()['data']
    hol = data['houses_of_life']
    planets = hol['planets']
    houses = hol['houses']
    rankings = hol['summary_rankings']

    lines = []
    lines.append("=" * 95)
    lines.append("                     ASTRA PRECISION HOUSES OF LIFE EVALUATION")
    lines.append("             Mantreśvara's Phaladīpikā (Chapters 3, 4, 6, and 15) Engine")
    lines.append("                  Vic DiCara Quantitative Astrological Framework")
    lines.append("=" * 95)
    lines.append("Native Name   : Donald Trump")
    lines.append("Birth Data    : 14/06/1946 at 10:54:00 (TZ: -04:00)")
    lines.append("Coordinates   : Jamaica, Queens, NY (Lat: 40.6833, Lon: -73.8)")
    lines.append("Ascendant     : Leo 29°58' | Lagneśa (Ascendant Lord): Sun")
    lines.append("Zodiac Frame  : Tropical Signs (Sāyana) | Campanus 3D Bhāvas | Dhruva Galactic Nakshatras")
    lines.append(f"Composite Mean: {rankings['composite_mean_score']:.2f} / 100.0")
    lines.append("=" * 95)
    lines.append("")

    # Section 1
    lines.append("=" * 95)
    lines.append("1. EXECUTIVE SUMMARY & GLOBAL RANKINGS")
    lines.append("=" * 95)
    lines.append("Houses Ranked by Composite Score (Descending):")
    for rank, h in enumerate(rankings['houses_by_composite_score'], start=1):
        h_data = houses[str(h)]
        sign = h_data['sign']
        lord = h_data['lord']
        occupants = h_data['occupants']
        occ_str = ", ".join(occupants) if occupants else "None"
        comp = h_data['synthesis']['composite_score']
        rating = h_data['synthesis']['health_rating']
        tier = h_data['synthesis']['classical_tier']
        lines.append(f"  Rank {rank:2d} | House {h:2d} ({sign:<11s} - Lord: {lord:<7s} | Occupants: {occ_str:<16s}) : {comp:6.2f} [{rating} • {tier}]")

    lines.append("")
    lines.append("Planets Ranked by Final Assessment Score (Descending):")
    for rank, p in enumerate(rankings['planets_by_final_score'], start=1):
        p_data = planets[p]
        sign = p_data['sign']
        h = p_data['house']
        dignity = p_data['dignity']['status']
        final_sc = p_data['final_assessment_score']
        lines.append(f"  Rank {rank:2d} | {p:<8s} in {sign:<13s} (House {h:2d} • Dignity: {dignity:<20s}) : {final_sc:6.2f}")

    lines.append("")

    # Section 2
    lines.append("=" * 95)
    lines.append("2. PLANETARY EVALUATIONS — INTRINSIC QUALITY VS. PROMINENCE")
    lines.append("=" * 95)
    lines.append("Planet   | Sign        | H  | Dignity Status      | D_Unit | Aspects | DigBala | Quality | CuspProx | H_Mult | Combust | Sandhi | Eclipse | Final ")
    lines.append("-" * 145)
    for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
        p_data = planets[p]
        sign = p_data['sign']
        h = p_data['house']
        d_status = p_data['dignity']['status']
        d_unit = p_data['dignity']['unit_score']
        aspects = p_data['combined_influences']['net_score']
        digbala = p_data['cusp_alignment']['digbala_points']
        quality = p_data['quality_base_score']
        cusp_prox = p_data['cusp_proximity_factor']
        h_mult = p_data['cusp_alignment']['house_multiplier']
        combust = p_data['combustion']['loss_ratio']
        sandhi = p_data['bhava_sandhi']['penalty_ratio']
        eclipse = p_data['eclipse']['loss_ratio']
        final_sc = p_data['final_assessment_score']
        lines.append(f"{p:<8s} | {sign:<11s} | {h:2d} | {d_status:<19s} | {d_unit:6.2f} | {aspects:7.1f} | {digbala:7.1f} | {quality:7.1f} | {cusp_prox:8.2f} | {h_mult:6.2f} | {combust:7.2f} | {sandhi:6.2f} | {eclipse:7.2f} | {final_sc:6.1f}")

    lines.append("")

    # Section 3
    lines.append("=" * 95)
    lines.append("3. DETAILED 12 HOUSES OF LIFE EVALUATION BREAKDOWN")
    lines.append("=" * 95)

    for h in range(1, 13):
        h_data = houses[str(h)]
        sign = h_data['sign']
        lord = h_data['lord']
        cusp_deg = h_data['cusp_degree']
        cusp_lon = h_data['cusp_longitude']
        occupants = h_data['occupants']
        synth = h_data['synthesis']
        comp = synth['composite_score']
        rating = synth['health_rating']
        tier = synth['classical_tier']
        drivers = synth['dominant_drivers']

        comps = h_data['components']
        b_cond = comps['basic_house_condition']
        l_eval = comps['lord_assessment']
        rel_eval = comps['relative_house_bhavat_bhavam']
        karaka_eval = comps['karaka_assessment']
        chandra_eval = comps['chandra_lagna_assessment']
        wall_eval = comps['house_walls_kartari']
        yoga_eval = comps['house_yogas']

        lines.append("-" * 95)
        lines.append(f"HOUSE {h:2d} : {sign.upper()} ({sign} {cusp_deg:.2f}° | Longitude: {cusp_lon:.2f}°)")
        lines.append(f"Lord: {lord} | Physical Occupants: {occupants}")
        lines.append(f"SYNTHESIS SCORE: {comp:.2f} | Health Rating: {rating} | Classical Tier: {tier}")
        lines.append("Dominant Astrological Drivers:")
        for driver in drivers:
            lines.append(f"  • {driver}")
        lines.append("")

        # Component 1
        lines.append(f"  [Component 1] Basic House Condition (Weight: 30%) : Score = {b_cond['score']:.2f}")
        lines.append("    Planet Cusp Contributions (Direct Rays & Dominance):")
        for p in CLASSICAL_PLANETS:
            val = b_cond['planet_contributions'].get(p, 0.0)
            lines.append(f"      - {p:<7s}: {val:+7.2f}")

        # Component 2
        lines.append(f"  [Component 2] Lord & Occupants Assessment (Weight: 30%) : Combined Score = {l_eval['combined_score']:.2f}")
        lines.append(f"    House Lord                : {lord} (Lord Final Assessment Score: {l_eval['lord_final_score']:.2f})")
        lines.append(f"    Immediate Dispositor      : {l_eval['immediate_dispositor']}")
        lines.append(f"    Final Dispositor          : {l_eval['final_dispositor']}")
        lines.append(f"    Effective Lord Score      : {l_eval['effective_lord_score']:.2f} (buffered via Dispositor Chain & Digbala bonus)")
        lines.append(f"    Occupants Final Scores    : {l_eval['occupants_final_scores']}")

        # Component 3
        lines.append(f"  [Component 3] Relative Houses / Bhavāt Bhavam (Weight: 15% Base) : Score = {rel_eval['score']:.2f}")
        lines.append(f"    Kendra/Trine/2nd/11th Pts : {rel_eval['kk_group_points']:+.2f}")
        lines.append(f"    Dusthāna Raw Penalty      : {rel_eval['dusthana_raw_points']:+.2f}")
        lines.append(f"    Benefic Mitigation Pct    : {rel_eval['benefic_mitigation_pct']:.2f}%")
        lines.append(f"    Mitigated Dusthāna Pts    : {rel_eval['dusthana_mitigated_points']:+.2f}")
        lines.append(f"    Active Count              : {rel_eval['active_planets_count']}")

        # Component 4
        lines.append(f"  [Component 4] Bhāva Kāraka Assessment (Weight: 10%) : Score = {karaka_eval['score']:.2f}")
        lines.append(f"    Primary Kārakas           : {', '.join(karaka_eval['karakas'])}")
        lines.append(f"    Individual Kāraka Scores  : {karaka_eval['karaka_planet_scores']}")
        lines.append(f"    Kāraka Lagna House & Sc   : House {karaka_eval['karaka_lagna_house']} -> Score {karaka_eval['karaka_lagna_score']:.1f}")

        # Component 5
        lines.append(f"  [Component 5] Chandra Lagna Assessment (Blended 20% into Relative House) : Score = {chandra_eval['score']:.2f}")
        lines.append(f"    Moon's Occupied House     : House {chandra_eval['moon_occupied_house']}")
        lines.append(f"    Chandra House Number      : House {chandra_eval['chandra_house_number']}")
        lines.append(f"    Chandra House Score       : {chandra_eval['score']:.2f}")
        lines.append(f"    Combined Relative+Chandra : {chandra_eval['combined_relative_score']:.2f}")

        # Component 6
        lines.append(f"  [Component 6] House Walls / Kartarī Yoga (Weight: 5% when active) : Score = {wall_eval['score']:.2f}")
        lines.append(f"    Is Walled (Both Flanks)   : {wall_eval['is_walled']}")

        # Component 7
        lines.append(f"  [Component 7] Certified House Yogas (Weight: 10%) : Score = {yoga_eval['total_yoga_score']:.2f}")
        lines.append(f"    Sub-Scores                : Rāja={yoga_eval['raja_yoga_score']:.2f}, Daridra={yoga_eval['daridra_yoga_score']:.2f}, Parivartana={yoga_eval['parivartana_score']:.2f}, Mahāpuruṣa={yoga_eval['mahapurusha_score']:.2f}")
        active_yogas = yoga_eval.get('active_yogas', [])
        lines.append(f"    Total Active Yogas Count  : {len(active_yogas)}")
        for y in active_yogas:
            lines.append(f"      * [{y['role']}] {y['type']}: {y['points']:+6.1f} pts (Planets: {y['planets']})")

        lines.append("")

    # Section 4
    lines.append("=" * 95)
    lines.append("4. COMPLETE RAW ASTRA EXPORT DOSSIER (FRONTEND 'EXPORT TEXT FORALL')")
    lines.append("=" * 95)
    md_dossier = generate_chart_ai_markdown(data)
    lines.append(md_dossier)

    output_text = "\n".join(lines) + "\n"
    with open("houses_of_life_evaluation_donald_trump.txt", "w", encoding="utf-8") as f:
        f.write(output_text)
    print(f"Generated houses_of_life_evaluation_donald_trump.txt ({len(output_text)} bytes, {len(lines)} lines)")

if __name__ == "__main__":
    generate_dossier()
