#!/usr/bin/env python3
"""
scripts/bundle_houses_of_life.py
================================
Generates a comprehensive, self-contained audit text bundle of all code,
mathematical specifications, frontend display blueprints, and test suites
for the "Houses of Life" (Phaladīpikā Chapter 15 Evaluation System).

Target Audience: External AI / Expert Human Auditor reviewing:
  1. The 10-phase mathematical calculation engine in Python (Hemisphere B).
  2. How the calculations are structured, serialized, and served via API.
  3. How the houses, scores, and diagnostics are displayed and visualized in the frontend
     (Matrix table, Diverging Bar Chart Horizon, Interactive Audit Receipt with SVG 30° strip,
      7-Graha Ledger, and Concordance view).
  4. Strict adherence to the Astra Editorial Design System (static/GEMINI.md & ADR-006):
     Strict 12px font floor, STIX Two Math monochrome glyphs (\\uFE0E), anti-pill protocol,
     and zero consumer emojis.
"""

import os
import sys
import json
from datetime import datetime

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_FILE = os.path.join(ROOT_DIR, "bundle_houses_of_life.txt")
ARTIFACT_DIR = "/Users/hajnaljanos/.gemini/antigravity-cli/brain/3ad7be36-fa44-4b21-8b28-018fc3f5c4a3"

AUDIT_FILES = [
    {
        "path": "jyotish/report/houses_of_life.md",
        "category": "1. MATHEMATICAL & CLASSICAL SPECIFICATION",
        "role": "Mantreśvara's Phaladīpikā (Chapters 3, 4, 6, and 15) Twin Markdown specification. Defines the 10-phase quantitative calculation pipeline, Parāśara exact Sphuṭa Dṛṣṭi degree aspects, multi-varga dignity (D1+D9), directional strength (Digbala), condition gating (amūḍha-hīnāḥ), Upacaya malefic boost, Bhavāt Bhavam relative houses, Kāraka Lagna, Chandra Lagna, Kartarī walls, Yogas, and Dispositor chain dynamics."
    },
    {
        "path": "jyotish/report/houses_of_life.py",
        "category": "2. BACKEND ENGINE & CALCULUS",
        "role": "Core computational engine (Phases 1–10). Extracts Whole Sign geometry with sensitive Ascendant degree cusps, computes functional natures with Svakṣetra dual-lordship overrides, continuous degree aspects, planetary evaluation (intrinsic quality vs. prominence), basic house condition, relative houses, Kāraka Lagna, Chandra Lagna, Kartarī walls, certified Yogas, dispositor chains, and composite synthesis scores."
    },
    {
        "path": "jyotish/pipeline.py",
        "category": "3. REPORT PIPELINE & API SERIALIZATION",
        "role": "Directed Acyclic Graph (DAG) pipeline orchestrator. Executes evaluate_houses_of_life(chart_input) during Stage 4, attaches it to the Vedic context dictionary under 'houses_of_life', and exposes it through Flask endpoint /api/chart/<native_id>."
    },
    {
        "path": "templates/widget_templates/tmpl_houses_of_life.html",
        "category": "4. FRONTEND HTML DOM BLUEPRINT",
        "role": "Reusable widget DOM blueprint (<template id=\"tmpl-houses-of-life\">). Declares top toolbar with view switcher (12-House Matrix, Audit Receipt, 7-Graha Ledger, Concordance), Zone 1 Executive Horizon Ribbon with diverging bar container (-150 to +150), and Zone 2 multi-view containers."
    },
    {
        "path": "static/js/widgets/houses_of_life.js",
        "category": "5. FRONTEND DISPLAY & INTERACTION CONTROLLER",
        "role": "Client-side JavaScript widget controller. Manages widget lifecycle, dual-mode responsive layout (side-by-side split in wide cells vs tabbed in compact cells), diverging bar chart rendering with color interpolation, 12-House Matrix rendering, dynamic Audit Receipt with interactive 30° degree strip SVG, 7-Graha Ledger table, and Concordance view."
    },
    {
        "path": "templates/partials/context_menu.html",
        "category": "6. UI REGISTRATION & WORKSPACE DISPATCH",
        "role": "Context menu and widget picker entry assigning 'houses-of-life' widget to grid cells."
    },
    {
        "path": "static/GEMINI.md",
        "category": "7. FRONTEND DESIGN SYSTEM & TYPOGRAPHY PROTOCOL",
        "role": "Mandatory frontend engineering rules: strict 12px font floor, monochrome line glyphs (\\uFE0E) via STIX Two Math font stack, de-badged tabular numbers, semantic CSS micro-dots, zero consumer emoji."
    },
    {
        "path": "documentations/adr/ADR-006-professional-editorial-design-system.md",
        "category": "7. FRONTEND DESIGN SYSTEM & TYPOGRAPHY PROTOCOL",
        "role": "ADR-006: Architectural decision record establishing the professional editorial publication design standard, warm parchment palette, anti-pill rules, and mathematical typography."
    },
    {
        "path": "tests/test_houses_of_life.py",
        "category": "8. AUTOMATED VERIFICATION TEST SUITE",
        "role": "Pytest test suite containing 62 unit tests verifying all 10 phases, dignity fallbacks, combustion gating, Upacaya malefic conversion, Bhavāt Bhavam, Kartarī walls, Yogas, classical refinements, and Donald Trump real-chart regressions."
    },
    {
        "path": "tests/test_houses_of_life_ui.py",
        "category": "8. AUTOMATED VERIFICATION TEST SUITE",
        "role": "Playwright end-to-end browser test suite verifying Houses of Life widget rendering, row selection, audit receipt drilldowns, tab switching, and Kala menu integration."
    },
    {
        "path": "houses_of_life_evaluation_donald_trump.txt",
        "category": "9. GROUND TRUTH DIAGNOSTIC EVALUATION DOSSIER",
        "role": "Comprehensive real-world diagnostic printout of Donald Trump's chart (14/06/1946 10:54 NY, Leo Ascendant 29°58'). Documents all planetary quality/prominence ratings, 12 house scores, and detailed component scorecards."
    }
]


def generate_bundle():
    print(f"Bundling Houses of Life calculation and frontend display files into {OUTPUT_FILE}...")
    
    buf = []
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 1. Main Header
    buf.append("=" * 95)
    buf.append("ASTRA: HOUSES OF LIFE (PHALADĪPIKĀ CH. 15) CALCULATION & FRONTEND DISPLAY AUDIT BUNDLE")
    buf.append(f"GENERATED : {now_str}")
    buf.append("FRAMEWORK : Vic DiCara Astrological System & Mantreśvara's Phaladīpikā")
    buf.append("ENGINE    : Swiss Ephemeris (`swisseph`) | Sāyana Tropical Signs | Campanus 3D Cusps")
    buf.append("UI SYSTEM : Astra Editorial Design System (ADR-006 & static/GEMINI.md)")
    buf.append("=" * 95)
    buf.append("")
    buf.append("EXECUTIVE DIRECTIVE FOR EVALUATING AI:")
    buf.append("-" * 95)
    buf.append("You are evaluating the complete architecture of the 'Houses of Life' subsystem in Astra,")
    buf.append("spanning both the backend mathematical calculus (Hemisphere B) and the frontend presentation layer.")
    buf.append("")
    buf.append("Your mission is to evaluate and judge two critical dimensions:")
    buf.append("  DIMENSION A: Mathematical Accuracy & Classical Fidelity")
    buf.append("  DIMENSION B: Frontend Information Architecture, Visual Presentation, and Design Protocol")
    buf.append("")
    buf.append("=" * 95)
    buf.append("DIMENSION A: BACKEND CALCULATION ENGINE & ARCHITECTURE")
    buf.append("=" * 95)
    buf.append("1. WHOLE SIGN GEOMETRY & SENSITIVE CUSPS (Phase 1):")
    buf.append("   - Ascendant degree inside its sign defines the sensitive cusp for all 12 houses.")
    buf.append("   - Target house H is identified by sign: Sign_H = (AscSignIndex + H - 1) % 12.")
    buf.append("   - Cusp longitude: Cusp_H = (Sign_H * 30.0) + AscDegInSign.")
    buf.append("")
    buf.append("2. FUNCTIONAL NATURE RELATIVE TO LAGNA (Phase 2):")
    buf.append("   - Based on Parāśara rulership rules: Trikoṇa (1, 5, 9) lords are auspicious benefics;")
    buf.append("     Dusthāna (6, 8, 12) and Triṣaḍāya (3, 6, 11) lords are malefics;")
    buf.append("     Kendra (1, 4, 7, 10) lords are modified by Kendrādhipati Doṣa.")
    buf.append("   - Moolatrikona sign dictates primary nature; secondary Dusthāna rulership is waived if Lord occupies Svakṣetra (15.29).")
    buf.append("   - Dynamic temperaments: Sun (-0.5), Moon (scaled by Pakṣa Bala: -0.5 New Moon to +1.0 Full Moon),")
    buf.append("     Mercury (conjunction-dependent: +0.5 with benefics, -0.5 with malefics).")
    buf.append("")
    buf.append("3. CONTINUOUS EXACT-DEGREE ASPECTS (*SPHUṬA DṚṢṬI*) & CUSP DOMINANCE (Phase 4):")
    buf.append("   - Aspect percentage is derived continuously from exact angular distance via Parāśara's Sphuṭa Dṛṣṭi:")
    buf.append("     AspectPct = (Virūpas / 60.0) * 100.0.")
    buf.append("   - Blind spots (0°-60°, exact 150°, 300°-360°) are calculated organically by the continuous degree curve.")
    buf.append("   - No artificial sign-distance masks or hard step thresholds suppress continuous aspects.")
    buf.append("   - Multi-planet cusp dominance ('potency stealing') allows closer planets to absorb conjunction intensity.")
    buf.append("")
    buf.append("4. COMPREHENSIVE PLANETARY ASSESSMENT (Phase 5):")
    buf.append("   - Multi-varga dignity: 65% D1 + 35% D9 (Vargottama floored at >= 0.80).")
    buf.append("   - Directional strength (Digbala): Canonical peak houses with sign-safe Shadbala scaling.")
    buf.append("   - Intrinsic Quality (50% Dignity + 35% Aspects + 15% Digbala) is strictly decoupled from Prominence")
    buf.append("     (House category & cusp proximity), preventing Kendra cusps from flipping debilitated planets positive.")
    buf.append("   - Vilagna protection (Phaladīpikā 3.9) softens negative dignity strain in House 1.")
    buf.append("   - Eclipse strain factor (Grahaṇa) attenuates luminaries conjoined with Rahu/Ketu within 12°.")
    buf.append("")
    buf.append("5. DIRECT BASIC HOUSE CONDITIONS (Phase 6):")
    buf.append("   - All continuous degree aspects contribute proportionally without arbitrary step cutoffs.")
    buf.append("   - Bidirectional natural friendship (P -> Lord and Lord -> P) modifies the functional blend:")
    buf.append("     F_eff = F_lagna + FriendMod (eliminating double-counting of inherent temperament).")
    buf.append("   - Smooth continuous functional transition across [-0.25, +0.25] without deadband cliff-edges.")
    buf.append("   - Condition-gating by Combustion & Bhāva Sandhi (amūḍha-hīnāḥ per 15.1, 15.5), relieved at cusp door (15.14).")
    buf.append("   - Multi-varga composite dignity check (d_p < 0.0) so Vargottama / D9-exalted planets are not penalized.")
    buf.append("   - Upacaya (3, 6, 11) malefic occupant rule (15.18): strictly for F_eff < 0, scaled positively with dignity.")
    buf.append("   - Rahu/Ketu node impact with benefic aspect mitigation and Mars/Saturn malefic aggravation check (15.8).")
    buf.append("   - Fixed baseline divisor of 3.0 with hyperbolic tangent saturation: 120.0 * tanh(Total / 360.0),")
    buf.append("     guaranteeing strict mathematical monotonicity across all positive and negative rays.")
    buf.append("")
    buf.append("6. RELATIVE HOUSE TECHNIQUE (*BHAVĀT BHAVAM*) & BHĀVA-NĀŚA FIX (Phase 7):")
    buf.append("   - Evaluates each target house H as House 1.")
    buf.append("   - Lord in relative 6, 8, 12 receives severe Bhāva-nāśa ruination penalty (-70/-110/-80),")
    buf.append("     mitigated if dignified/uncombust, waived if occupying Svakṣetra (15.29), and softened by benefic aspects.")
    buf.append("   - Relative functional natures are blended 70/30 with natal functional nature, protecting Ascendant Lord (Lagneśa).")
    buf.append("")
    buf.append("7. BHĀVA KĀRAKA & KĀRAKA LAGNA (Phase 7B) AND CHANDRA LAGNA (Phase 7C):")
    buf.append("   - Direct condition of natural representative (Kāraka), relative placement, and Kāraka Lagna score.")
    buf.append("   - Lunar frame (Chandra Lagna) blended 20% into relative house assessment.")
    buf.append("")
    buf.append("8. HOUSE WALLS / KARTARĪ YOGA (Phase 8) & YOGAS (Phase 9):")
    buf.append("   - Quantified flanking within 30° before and after cusp; requires true cross-border adjacency (15.6).")
    buf.append("   - Certified Rāja, Daridra, Parivartana, and Mahāpuruṣa yogas saturated via tanh into [-100, +100].")
    buf.append("")
    buf.append("9. COMPOSITE SYNTHESIS & CLASSICAL TIERS (Phase 10):")
    buf.append("   - Weighted sum across 6 components: Basic (30%), Lord/Occupants (30%), Relative (15%), Kāraka (10%), Yogas (10%), Walls (5%).")
    buf.append("   - Classical Tiers: Puṣṭa (Flourishing: >= +25.0), Miśra (Mixed/Resilient: -25.0 to +25.0), Hīna (Depleted/Afflicted: < -25.0).")
    buf.append("")
    buf.append("=" * 95)
    buf.append("DIMENSION B: FRONTEND VISUALIZATION & USER EXPERIENCE (UI/UX)")
    buf.append("=" * 95)
    buf.append("The frontend presentation of Houses of Life is strictly governed by:")
    buf.append("  - static/GEMINI.md (Typography & Layout Protocols)")
    buf.append("  - documentations/adr/ADR-006-professional-editorial-design-system.md (Editorial Publication Standard)")
    buf.append("")
    buf.append("KEY VISUAL COMPONENTS IN tmpl_houses_of_life.html & houses_of_life.js:")
    buf.append("1. TOP TOOLBAR & VIEW SWITCHER:")
    buf.append("   - Title: 'Houses of Life' with micro-tag 'Phaladīpikā Ch. 15'.")
    buf.append("   - View Buttons: [12-House Matrix], [Audit Receipt (H1..H12)], [7-Graha Ledger], [Concordance].")
    buf.append("   - Maximize Button [⛶]: Expands widget into full-screen dialog.")
    buf.append("")
    buf.append("2. ZONE 1: EXECUTIVE HORIZON RIBBON:")
    buf.append("   - Readout Line: Ascendant Anchor degree, Top Flourishing House, Most Challenged House.")
    buf.append("   - Diverging Bar Chart Horizon:")
    buf.append("     * Scale from -150 to +150 with a centered 0.0 baseline.")
    buf.append("     * 12 diverging bars representing each house's composite score.")
    buf.append("     * Continuous color interpolation: Forest green for Puṣṭa, warm amber/ochre for Miśra, crimson for Hīna.")
    buf.append("     * Interactive click: Clicking any bar immediately activates the Audit Receipt drilldown for that house.")
    buf.append("")
    buf.append("3. VIEW 1: 12-HOUSE MATRIX TABLE:")
    buf.append("   - High-density, professional editorial matrix displaying all 12 houses.")
    buf.append("   - Columns: House # & Sanskrit Name, Sign & STIX Two Math glyph, Cusp Longitude & Campanus Deg,")
    buf.append("     Lord & Dispositor, Occupants & Degree Aspect Rays, Component 1–6 Scores, Composite Score, and Classical Tier.")
    buf.append("   - Interactive Row Selection: Highlights active house and opens drilldown receipt.")
    buf.append("")
    buf.append("4. VIEW 2: AUDIT RECEIPT DRILLDOWN:")
    buf.append("   - Responsive Dual Mode:")
    buf.append("     * In wide cells (>= 720px) or maximized view: Renders side-by-side next to the Matrix table.")
    buf.append("     * In compact cells (< 720px): Renders as a dedicated tab with '< Back to Matrix' button and [Prev]/[Next] steppers.")
    buf.append("   - 30° Degree Strip SVG:")
    buf.append("     * Visualizes the 30° span of the target sign.")
    buf.append("     * Renders exact sensitive cusp marker line.")
    buf.append("     * Displays physical occupant planet markers and incoming aspect rays relative to the cusp.")
    buf.append("   - 6-Component Diagnostic Scorecards:")
    buf.append("     * Card 1: Basic House Condition (direct ray contributions table with sign-safe integrity gating).")
    buf.append("     * Card 2: Lord & Occupants (Lord final score, Dispositor chain path, effective buffered score).")
    buf.append("     * Card 3: Bhavāt Bhavam & Chandra Lagna (Kendra/Trine points, Dusthāna penalty, benefic mitigation %).")
    buf.append("     * Card 4: Bhāva Kāraka Assessment (natural significator score, Kāraka Lagna score).")
    buf.append("     * Card 5: House Walls / Kartarī Yoga (before/after flanking degrees, wall classification).")
    buf.append("     * Card 6: Certified House Yogas (Rāja, Daridra, Parivartana, Mahāpuruṣa active point breakdown).")
    buf.append("   - Dispositor Chain Path visualization:")
    buf.append("     * Shows traversed houses and final dispositor loop (e.g., Venus -> Moon -> Jupiter -> Venus).")
    buf.append("")
    buf.append("5. VIEW 3: 7-GRAHA OPERATIONAL LEDGER:")
    buf.append("   - Standalone planetary assessment table for Sun through Saturn.")
    buf.append("   - Columns: Graha, Tropical Sign, House, Multi-Varga Dignity (D1+D9), Aspects Net, Digbala Points,")
    buf.append("     Quality Base, Cusp Proximity Factor, House Multiplier, Combustion Loss, Bhāva Sandhi, Eclipse Loss, Final Score.")
    buf.append("")
    buf.append("6. VIEW 4: STAGE 3 VS. STAGE 4 CONCORDANCE:")
    buf.append("   - Cross-checks Stage 3 qualitative house strengths against Stage 4 quantitative Houses of Life scores,")
    buf.append("     identifying reinforcing strengths or divergence.")
    buf.append("")
    buf.append("7. STRICT ASTRA EDITORIAL DESIGN SYSTEM COMPLIANCE:")
    buf.append("   - Strict 12px Font Floor (Rule 1 of static/GEMINI.md): Zero sub-pixel font sizes.")
    buf.append("   - Monochrome STIX Two Math Line Glyphs (\\uFE0E): Eliminates colored OS emoji boxes for signs/planets.")
    buf.append("   - Anti-Pill Protocol: Routine data (degrees, coordinates, dispositors) rendered as clean tabular numbers.")
    buf.append("   - Zero Consumer Emojis: Replaced by semantic CSS micro-dots (.status-indicator) and square micro-tags (.micro-tag).")
    buf.append("=" * 95)
    buf.append("")

    # 2. Table of Contents
    buf.append("TABLE OF CONTENTS")
    buf.append("-" * 95)
    
    file_records = []
    total_lines = 0
    total_bytes = 0

    for idx, item in enumerate(AUDIT_FILES, 1):
        rel_path = item["path"]
        abs_path = os.path.join(ROOT_DIR, rel_path)
        if not os.path.exists(abs_path):
            print(f"WARNING: File not found: {abs_path}")
            continue
        
        with open(abs_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
            lines = content.splitlines()
            line_count = len(lines)
            byte_size = len(content.encode("utf-8"))
            
            total_lines += line_count
            total_bytes += byte_size
            file_records.append({
                "index": idx,
                "path": rel_path,
                "abs_path": abs_path,
                "category": item["category"],
                "role": item["role"],
                "lines": line_count,
                "bytes": byte_size,
                "content": content
            })
            buf.append(f" {idx:2d}. [{item['category']}] {rel_path} ({line_count} lines, {byte_size:,} bytes)")
            buf.append(f"     Role: {item['role']}")
            buf.append("")

    buf.append("-" * 95)
    buf.append(f"TOTAL AUDITED FILES: {len(file_records)}")
    buf.append(f"TOTAL LINES OF CODE & SPECIFICATIONS: {total_lines:,}")
    buf.append(f"TOTAL UNCOMPRESSED VOLUME: {total_bytes:,} bytes (~{total_bytes / 1024:.1f} KB)")
    buf.append("=" * 95)
    buf.append("")

    # 3. JSON Schema Reference
    buf.append("=" * 95)
    buf.append("HOUSES OF LIFE JSON SCHEMA REFERENCE (chart_dict['houses_of_life'])")
    buf.append("=" * 95)
    buf.append("This is the exact JSON data structure generated by jyotish/report/houses_of_life.py")
    buf.append("and transmitted to the frontend widget (houses_of_life.js):")
    buf.append("")
    buf.append("""{
  "summary_rankings": {
    "composite_mean_score": 32.10,
    "house_dna_code": "1-9-4-11-6-5-2-10-12-8-7-3",
    "houses_by_composite_score": [1, 9, 4, 11, 6, 5, 2, 10, 12, 8, 7, 3],
    "top_flourishing_houses": [1, 9, 4],
    "most_challenged_houses": [8, 7, 3]
  },
  "houses": {
    "1": {
      "house": 1,
      "sign": "Leo",
      "lord": "Sun",
      "cusp_degree": 29.97,
      "cusp_longitude": 149.97,
      "occupants": ["Mars"],
      "components": {
        "basic_house_condition": {
          "score": 58.54,
          "planet_contributions": { "Sun": 97.58, "Moon": 69.58, "Mars": 87.15, "Jupiter": 0.0, "Venus": 0.99, "Saturn": -46.17 }
        },
        "lord_assessment": {
          "lord": "Sun",
          "lord_final_score": 55.20,
          "immediate_dispositor": "Mercury",
          "final_dispositor": "Moon",
          "effective_lord_score": 47.44,
          "occupants_final_scores": { "Mars": 46.54 },
          "combined_score": 47.17
        },
        "relative_house_bhavat_bhavam": {
          "score": 45.87,
          "kk_group_points": 297.95,
          "dusthana_raw_points": -114.00,
          "benefic_mitigation_pct": 39.83,
          "dusthana_mitigated_points": -68.59,
          "active_planets_count": 5
        },
        "karaka_assessment": {
          "score": 55.20,
          "karakas": ["Sun"],
          "karaka_planet_scores": { "Sun": 55.20 },
          "karaka_lagna_house": { "Sun": 11 },
          "karaka_lagna_score": 58.54,
          "karaka_relative_houses": { "Sun": 11 },
          "karaka_proximity": { "Sun": "Close / Nourishing" }
        },
        "chandra_lagna_assessment": {
          "moon_occupied_house": 5,
          "chandra_house_num": 9,
          "chandra_house_score": 49.90,
          "combined_relative_score": 46.68
        },
        "house_walls_kartari": {
          "score": 0.0,
          "is_walled": false,
          "wall_type": "None"
        },
        "house_yogas": {
          "total_yoga_score": 88.42,
          "raja_yoga_score": 140.0,
          "daridra_yoga_score": 0.0,
          "parivartana_score": 0.0,
          "mahapurusha_score": 0.0,
          "active_yogas": [
            { "type": "Rāja Yoga", "role": "Beneficiary", "points": 40.0, "planets": ["Sun", "Mars"] }
          ]
        }
      },
      "synthesis": {
        "composite_score": 55.88,
        "health_rating": "Flourishing / Fortified",
        "classical_tier": "Puṣṭa",
        "dominant_drivers": [
          "House Lord Sun is fortified (+55.2)",
          "Significant aspectual support from Sun on Cusp (+97.6)",
          "Net Structural Yogas (+88.4)"
        ]
      }
    }
  },
  "planets": {
    "Sun": {
      "sign": "Gemini", "house": 11,
      "dignity": { "status": "Friend's Sign", "unit_score": 0.61 },
      "combined_influences": { "net_score": 59.5 },
      "cusp_alignment": { "digbala_points": 13.3, "house_multiplier": 1.11 },
      "quality_base_score": 53.3,
      "cusp_proximity_factor": 1.11,
      "combustion": { "loss_ratio": 0.0 },
      "bhava_sandhi": { "penalty_ratio": 0.0 },
      "eclipse": { "loss_ratio": 0.06 },
      "final_assessment_score": 55.20
    }
  }
}""")
    buf.append("=" * 95)
    buf.append("")

    # 4. Verbatim Code & Specification Files
    for record in file_records:
        idx = record["index"]
        rel_path = record["path"]
        category = record["category"]
        role = record["role"]
        lines = record["lines"]
        bytes_count = record["bytes"]
        content = record["content"]
        
        buf.append("=" * 95)
        buf.append(f"FILE {idx:2d} OF {len(file_records)}: {rel_path}")
        buf.append(f"CATEGORY   : {category}")
        buf.append(f"ROLE       : {role}")
        buf.append(f"METRICS    : {lines:,} lines | {bytes_count:,} bytes")
        buf.append("=" * 95)
        buf.append(f"BEGIN VERBATIM CONTENTS: {rel_path}")
        buf.append("-" * 95)
        buf.append(content)
        if not content.endswith("\n"):
            buf.append("")
        buf.append("-" * 95)
        buf.append(f"END VERBATIM CONTENTS: {rel_path}")
        buf.append("=" * 95)
        buf.append("")

    full_bundle_text = "\n".join(buf)

    # Write workspace bundle
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(full_bundle_text)
    print(f"✅ Successfully wrote workspace bundle: {OUTPUT_FILE} ({len(full_bundle_text):,} bytes)")

    # Write artifact text bundle
    os.makedirs(ARTIFACT_DIR, exist_ok=True)
    artifact_txt = os.path.join(ARTIFACT_DIR, "bundle_houses_of_life.txt")
    with open(artifact_txt, "w", encoding="utf-8") as f:
        f.write(full_bundle_text)
    print(f"✅ Successfully wrote artifact TXT: {artifact_txt}")

    # Write artifact markdown bundle
    artifact_md = os.path.join(ARTIFACT_DIR, "bundle_houses_of_life.md")
    with open(artifact_md, "w", encoding="utf-8") as f:
        f.write(f"# Houses of Life: Calculation & Frontend Display Audit Bundle\n\n```text\n{full_bundle_text[:20000]}\n... [truncated in markdown preview, see bundle_houses_of_life.txt for full {len(full_bundle_text):,} bytes] ...\n```\n")
    print(f"✅ Successfully wrote artifact MD: {artifact_md}")

    print("\nAudited Files Included in Bundle:")
    for rec in file_records:
        print(f"  [{rec['index']:2d}] {rec['path']} ({rec['lines']} lines, {rec['bytes']:,} bytes)")


if __name__ == "__main__":
    generate_bundle()
