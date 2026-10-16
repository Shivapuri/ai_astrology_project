import json
import os
import asyncio
from playwright.async_api import async_playwright
from jyotish.generate_jyotish import generate_kala_chart

def generate_audit_report():
    print("Generating Angelina Jolie chart...")
    chart = generate_kala_chart(
        name="Angelina Jolie",
        year=1975,
        month=6,
        day=4,
        hour=9,
        minute=9,
        second=0,
        latitude=34.0522,
        longitude=-118.2437,
        timezone_offset=-7.0,
        place="Los Angeles, CA"
    )

    hol = chart.get("houses_of_life", {})
    bb = chart.get("bhava_bala", {})
    meta = hol.get("metadata", {})
    rankings = hol.get("summary_rankings", {})
    planets = hol.get("planets", {})
    houses = hol.get("houses", {})

    lines = []
    lines.append("=" * 90)
    lines.append("ASTRA PRECISION ASTROLOGICAL ENGINE — HOUSES OF LIFE DIAGNOSTIC AUDIT REPORT")
    lines.append("Vic DiCara Methodology (Phaladīpikā Chapter 15 Evaluation System)")
    lines.append("=" * 90)
    lines.append("")
    lines.append("1. NATIVE & COMPUTATION BASELINE")
    lines.append("-" * 90)
    lines.append("Name:                 Angelina Jolie")
    lines.append("Date of Birth:        June 4, 1975 (04/06/1975)")
    lines.append("Time of Birth:        09:09:00 AM (Local Time)")
    lines.append("Location:             Los Angeles, California, USA (34.0522° N, 118.2437° W)")
    lines.append("Timezone:             UTC-07:00 (Pacific Daylight Time)")
    lines.append("Astrological Zodiac:  Tropical Signs (Rāśis) with Whole Sign Bhāvas")
    lines.append("Sensitive Cusp:       Ascendant Longitude projected across all 12 signs")
    lines.append("House System:         Whole Sign Rāśi Bhāvas (with Campanus 3D Cusp Cross-Reference)")
    lines.append("Nakshatra System:     Sidereal Equatorial Dhruva Galactic Center Anchor")
    asc_deg = meta.get('ascendant_degree', 0.0)
    lines.append(f"Ascendant (Lagna):    {meta.get('ascendant_sign')} at {asc_deg:.4f}° (Sensitive Cusp Degree in Sign: {asc_deg:.4f}°)")
    lines.append("")
    lines.append("EXECUTIVE SUMMARY RANKINGS:")
    lines.append(f"  Top Flourishing Houses:  {', '.join(['H' + str(h) for h in rankings.get('top_flourishing_houses', [])])}")
    lines.append(f"  Most Challenged Houses:  {', '.join(['H' + str(h) for h in rankings.get('most_challenged_houses', [])])}")
    lines.append(f"  Composite House Mean:    {rankings.get('composite_mean_score', 0.0):+.2f} points")
    lines.append("")
    lines.append("=" * 90)
    lines.append("2. PHASE 1: WHOLE SIGN GEOMETRY & SENSITIVE HOUSE CUSPS")
    lines.append("-" * 90)
    lines.append(f"{'Bhāva':<7} | {'Rāśi':<13} | {'Cusp Longitude':<15} | {'Cusp Deg:Min':<14} | {'Lord':<10} | {'Occupants':<20}")
    lines.append("-" * 90)
    for h in range(1, 13):
        h_info = houses[str(h)]
        c_lon = h_info["cusp_longitude"]
        deg_in_sign = c_lon % 30.0
        d = int(deg_in_sign)
        m = int(round((deg_in_sign - d) * 60))
        deg_min = f"{d}°{m:02d}'"
        occs = ", ".join(h_info.get("occupants", [])) or "None"
        lines.append(f"H{h:<5} | {h_info['sign']:<13} | {c_lon:>12.4f}° | {deg_min:<14} | {h_info['lord']:<10} | {occs:<20}")
    lines.append("")
    lines.append("=" * 90)
    lines.append("3. PHASE 2: PLANETARY FUNCTIONAL NATURE QUANTIFICATION (F_P)")
    lines.append("Phaladīpikā 15.1 Rules:")
    lines.append("  Rule 1: 1st House Lord -> +3 (Unconditional benefic short-circuit)")
    lines.append("  Rule 2: Trine Lord (5, 9) -> Mūlatrikoṇa: +2, Domicile: +1")
    lines.append("  Rule 3: Dusthāna Lord (6, 8, 12) -> Mūlatrikoṇa: -2, Domicile: -1")
    lines.append("  Rule 4: Inherent Temperament -> Benefic (Jup, Ven): +1, Malefic (Mar, Sat): -1, Neutral (Sun, Moo, Mer): 0")
    lines.append("-" * 90)
    lines.append(f"{'Graha':<9} | {'F_P Score':<10} | {'Classification':<15} | {'Rules Triggered & Proof':<50}")
    lines.append("-" * 90)
    for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
        fn = planets[p]["functional_nature"]
        rb = fn.get("rule_breakdown", {})
        rules = []
        if rb.get("is_first_lord"):
            rules.append("Rule 1: 1st Lord (+3)")
        if rb.get("trine_score"):
            rules.append(f"Rule 2: Trine ({rb['trine_score']:+d})")
        if rb.get("dusthana_score"):
            rules.append(f"Rule 3: Dusthāna ({rb['dusthana_score']:+d})")
        if rb.get("inherent_score"):
            rules.append(f"Rule 4: Inherent ({rb['inherent_score']:+d})")
        rule_str = ", ".join(rules) if rules else "Neutral (no trine/dusthana)"
        lines.append(f"{p:<9} | {fn['score']:>+9} | {fn['classification']:<15} | {rule_str:<50}")
    lines.append("")
    lines.append("=" * 90)
    lines.append("4. PHASE 3 & PHASE 5: 7-GRAHA OPERATIONAL LEDGER (PLANETARY CONDITION)")
    lines.append("-" * 90)
    lines.append(f"{'Graha':<8} | {'Sign (House)':<18} | {'D1 Dignity':<15} | {'Comb Inf':<10} | {'Cusp Align':<13} | {'Base Avg':<10} | {'Sandhi x Comb':<14} | {'Final Score':<12}")
    lines.append("-" * 90)
    for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
        p_info = planets[p]
        sign_h = f"{p_info['sign']} (H{p_info['house']})"
        dig = f"{p_info['dignity']['pct_score']:+.0f}% ({p_info['dignity']['status'][:8]})"
        cinf = f"{p_info['combined_influences']['net_score']:+.1f}"
        al = f"{p_info['cusp_alignment']['alignment_score']:+.0f} ({p_info['cusp_alignment']['house_multiplier']:.1f}x)"
        bavg = f"{p_info['base_average_score']:+.1f}"
        sandhi_comb = f"{p_info['bhava_sandhi']['retention_multiplier']:.2f}x · {p_info['combustion']['combustion_multiplier']:.2f}x"
        fscore = f"{p_info['final_assessment_score']:+.2f}"
        lines.append(f"{p:<8} | {sign_h:<18} | {dig:<15} | {cinf:>10} | {al:>13} | {bavg:>10} | {sandhi_comb:>14} | {fscore:>12}")
    lines.append("")
    lines.append("=" * 90)
    lines.append("5. 12-BHĀVA QUANTITATIVE SYNTHESIS MATRIX (ALL 5 LAYERS & COMPOSITE)")
    lines.append("-" * 90)
    lines.append(f"{'Bhāva':<6} | {'Rāśi':<11} | {'Lord':<8} | {'Basic':<8} | {'Lord/Occ':<9} | {'Bhavāt':<8} | {'Kartarī':<8} | {'Yogas':<8} | {'Composite':<10} | {'Health Tier':<22}")
    lines.append("-" * 90)
    for h in range(1, 13):
        h_info = houses[str(h)]
        c = h_info["components"]
        s = h_info["synthesis"]
        b_sc = f"{c['basic_house_condition']['score']:>+7.1f}"
        l_sc = f"{c['lord_assessment'].get('combined_score', c['lord_assessment']['lord_final_score']):>+8.1f}"
        bh_sc = f"{c['relative_house_bhavat_bhavam']['score']:>+7.1f}"
        w_sc = f"{c['house_walls_kartari']['score']:>+7.1f}"
        y_sc = f"{c['house_yogas']['total_yoga_score']:>+7.1f}"
        comp = f"{s['composite_score']:>+9.2f}"
        tier = f"{s['classical_tier']} ({s['health_rating']})"
        lines.append(f"H{h:<5} | {h_info['sign']:<11} | {h_info['lord']:<8} | {b_sc} | {l_sc} | {bh_sc} | {w_sc} | {y_sc} | {comp} | {tier:<22}")
    lines.append("")
    lines.append("=" * 90)
    lines.append("6. DEEP DIVE: HOUSE-BY-HOUSE DETAILED MATHEMATICAL AUDIT RECEIPTS")
    lines.append("=" * 90)
    for h in range(1, 13):
        h_info = houses[str(h)]
        c = h_info["components"]
        s = h_info["synthesis"]
        lines.append("")
        lines.append(f"--- [ HOUSE {h}: {h_info['sign'].upper()} (RULED BY {h_info['lord'].upper()}) ] ---")
        lines.append(f"Composite Score: {s['composite_score']:+.2f} | Classical Tier: {s['classical_tier']} | Rating: {s['health_rating']}")
        lines.append(f"Sensitive Cusp Degree: {h_info['cusp_longitude']:.4f}° ({h_info['sign']} {h_info['cusp_longitude'] % 30.0:.2f}°)")
        lines.append(f"Occupants: {', '.join(h_info.get('occupants', [])) or 'None'}")
        lines.append("")
        lines.append("  1. Direct Cusp Rays (Phase 6):")
        lines.append(f"     Direct Basic Score: {c['basic_house_condition']['score']:+.2f}")
        contribs = c["basic_house_condition"].get("planet_contributions", {})
        if contribs:
            for p, val in contribs.items():
                is_lord = " [HOUSE LORD]" if p == h_info['lord'] else ""
                lines.append(f"       * {p:<9}: {val:>+7.2f} pts{is_lord}")
        else:
            lines.append("       * No direct planetary rays on cusp")

        lines.append("")
        lines.append("  2. Lord & Occupant Condition (Phase 5):")
        la = c["lord_assessment"]
        lord_sc = la["lord_final_score"]
        occ_scs = la.get("occupants_final_scores", {})
        occ_avg = sum(occ_scs.values()) / len(occ_scs) if occ_scs else 0.0
        comb_sc = (lord_sc + sum(occ_scs.values())) / (1.0 + len(occ_scs)) if occ_scs else lord_sc
        lines.append(f"     Lord ({h_info['lord']}) Final Score:       {lord_sc:+.2f}")
        if occ_scs:
            occ_str = ", ".join([f"{p} ({sc:+.2f})" for p, sc in occ_scs.items()])
            lines.append(f"     Occupants Final Scores:   {occ_str}")
            lines.append(f"     Occupants Average Score:  {occ_avg:+.2f}")
        else:
            lines.append("     Occupants Final Scores:   None")
        lines.append(f"     Combined Lord/Occ Score:  {comb_sc:+.2f}")

        lines.append("")
        lines.append("  3. Bhavāt Bhavam Neighborhood (Phase 7):")
        bh = c["relative_house_bhavat_bhavam"]
        lines.append(f"     Relative Score:           {bh['score']:+.2f}")
        lines.append(f"     KK Group Points:          {bh['kk_group_points']:+.2f}")
        lines.append(f"     Raw Dusthāna Points:      {bh['dusthana_raw_points']:+.2f}")
        lines.append(f"     Benefic Mitigation Pct:   {bh['benefic_mitigation_pct']:.1f}%")
        lines.append(f"     Mitigated Dusthāna:       {bh['dusthana_mitigated_points']:+.2f}")
        lines.append(f"     Active Planets Count:     {bh['active_planets_count']}")

        lines.append("")
        lines.append("  4. 30° Cusp Walls / Kartarī Yoga (Phase 8):")
        w = c["house_walls_kartari"]
        lines.append(f"     Wall Type:                {w['wall_type']}")
        lines.append(f"     Wall Score:               {w['score']:+.2f}")
        lines.append(f"     Is Flanked/Walled:        {w['is_walled']}")
        if w.get("planet_before"):
            lines.append(f"     Planet Before Cusp:       {w['planet_before']}")
        if w.get("planet_after"):
            lines.append(f"     Planet After Cusp:        {w['planet_after']}")

        lines.append("")
        lines.append("  5. Structural House Yogas (Phase 9):")
        y = c["house_yogas"]
        lines.append(f"     Total Yoga Score:         {y['total_yoga_score']:+.2f}")
        lines.append(f"       - Parivartana Points:   {y['parivartana_score']:+.2f}")
        lines.append(f"       - Rāja Yoga Points:     {y['raja_yoga_score']:+.2f}")
        lines.append(f"       - Mahāpuruṣa Points:    {y['mahapurusha_score']:+.2f}")
        lines.append(f"       - Daridra Points:       {y['daridra_yoga_score']:+.2f}")
        active_y = y.get("active_yogas", [])
        if active_y:
            lines.append("     Active Structural Yogas:")
            for ay in active_y:
                planets_str = " + ".join(ay.get("planets", []))
                lines.append(f"       * {ay['type']} [{ay['role']}] ({planets_str}): {ay['points']:+.0f} pts")
        else:
            lines.append("     Active Structural Yogas: None")

        lines.append("")
        lines.append("  6. Synthesis & Dominant Drivers:")
        drivers = s.get("dominant_drivers", [])
        for d in drivers:
            lines.append(f"     • {d}")

    lines.append("")
    lines.append("=" * 90)
    lines.append("7. CROSS-SYSTEM CONCORDANCE: STAGE 3 BHĀVA BALA VS. STAGE 4 HOUSES OF LIFE")
    lines.append("-" * 90)
    lines.append(f"{'Bhāva':<6} | {'Rāśi (Lord)':<18} | {'Stage 3 Virūpas':<16} | {'Stage 3 Rūpas':<14} | {'Stage 3 Tier':<13} | {'Stage 4 Score':<14} | {'Stage 4 Tier':<13} | {'Diagnosis'}")
    lines.append("-" * 90)
    for h in range(1, 13):
        h_info = houses[str(h)]
        s = h_info["synthesis"]
        bb_h = bb.get(h) or bb.get(str(h)) or {}
        v_vir = bb_h.get("total_virupas", 0.0)
        v_rup = bb_h.get("total_rupas", v_vir / 60.0)
        st3_tier = bb_h.get("classification", "Puṣṭa" if v_rup >= 8.0 else ("Hīna" if v_rup < 6.0 else "Miśra"))
        st4_score = s["composite_score"]
        st4_tier = s["classical_tier"]

        t3 = st3_tier.lower()
        t4 = st4_tier.lower()
        if (("puṣṭa" in t3 and "puṣṭa" in t4) or ("hīna" in t3 and "hīna" in t4) or ("miśra" in t3 and "miśra" in t4)):
            diag = f"Harmonic Agreement ({st4_tier})"
        elif st4_score >= 25.0 and "puṣṭa" not in t3:
            diag = "Divergent: Stage 4 Elevated by Yogas / Kartarī Wall"
        elif st4_score <= -20.1 and "hīna" not in t3:
            diag = "Divergent: Stage 4 Strained by Cusp Pressure / Daridra"
        else:
            diag = f"Stage 3 {st3_tier} <-> Stage 4 {st4_tier}"

        lines.append(f"H{h:<5} | {h_info['sign'] + ' (' + h_info['lord'] + ')':<18} | {v_vir:>14.1f}v | {v_rup:>12.2f}R | {st3_tier:<13} | {st4_score:>+12.2f} | {st4_tier:<13} | {diag}")

    lines.append("")
    lines.append("=" * 90)
    lines.append("8. COMPLETE MACHINE-READABLE JSON DUMP (HOUSES OF LIFE ENGINE)")
    lines.append("=" * 90)
    lines.append(json.dumps(hol, indent=2))

    output_path = os.path.abspath("houses_of_life_angelina_jolie_report.txt")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Report written successfully to: {output_path}")
    return output_path

async def capture_complete_screenshot():
    print("Launching Playwright to capture complete high-resolution screenshot...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # 1920x1080 full desktop canvas
        page = await browser.new_page(viewport={"width": 1920, "height": 1080}, device_scale_factor=2)
        await page.goto("http://127.0.0.1:5001")
        await page.wait_for_timeout(1000)

        # Load Angelina Jolie chart
        await page.evaluate("loadChart('angelina-jolie')")
        await page.wait_for_timeout(1500)

        # Assign houses-of-life to cell 0
        await page.evaluate("""
            const cell = document.querySelector('.grid-cell');
            if (cell) assignWidget('houses-of-life', cell);
        """)
        await page.wait_for_timeout(1000)

        # Open the complete maximized split window (1480px width)
        await page.evaluate("""
            const maxBtn = document.querySelector('.btn-widget-maximize');
            if (maxBtn) maxBtn.click();
            else if (typeof openFloatingHousesOfLife === 'function') openFloatingHousesOfLife();
        """)
        await page.wait_for_timeout(1000)

        # Select House 10 to demonstrate Rāja Yoga hosting + lordship in receipt
        await page.evaluate("""
            const modal = document.getElementById('widgetMaximizeModal');
            if (modal) {
                const row10 = modal.querySelector('.hol-house-row[data-house=\"10\"]');
                if (row10) row10.click();
            }
        """)
        await page.wait_for_timeout(600)

        # Capture complete split screenshot
        screenshot_path = os.path.abspath("angelina_jolie_houses_of_life_complete.png")
        await page.screenshot(path=screenshot_path)
        print(f"Complete screenshot saved to: {screenshot_path}")

        # Also capture focused close-up of the maximized modal card
        card_el = page.locator("#widgetMaximizeCard")
        card_path = os.path.abspath("angelina_jolie_houses_of_life_cockpit_card.png")
        await card_el.screenshot(path=card_path)
        print(f"Cockpit card screenshot saved to: {card_path}")

        await browser.close()

if __name__ == '__main__':
    generate_audit_report()
    asyncio.run(capture_complete_screenshot())
