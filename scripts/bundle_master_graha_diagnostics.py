#!/usr/bin/env python3
"""
scripts/bundle_master_graha_diagnostics.py
==========================================
Generates a comprehensive, self-contained, and reusable audit text bundle of all code,
mathematical specifications, frontend display blueprints, design protocols, and test suites
for the "Master Graha Diagnostics" system in Astra.

Target Audience / Use Cases:
  1. Complete ingestion and reuse by another AI coding assistant or human developer.
  2. Full architectural and mathematical audit of planetary dignity, power, avasthas,
     aspects, and vitality calculations.
  3. Reusable reference for the exact 9-column frontend presentation layer, deep drawer cockpit,
     and multi-varga divisional chart selector (D1 to D60).
  4. Adherence to the Astra Editorial Design System (static/GEMINI.md & ADR-006):
     Strict 12px font floor, STIX Two Math monochrome glyphs (\\uFE0E), anti-pill protocol,
     and zero consumer emojis.
"""

import os
import sys
import json
from datetime import datetime

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_FILE = os.path.join(ROOT_DIR, "bundle_master_graha_diagnostics.txt")
ARTIFACT_DIR = "/Users/hajnaljanos/.gemini/antigravity-cli/brain/9d41ddc5-f846-4641-b17d-1bd4dbdc71a5"

AUDIT_FILES = [
    {
        "path": "jyotish/planetary_evaluation/planetary_evaluation.md",
        "category": "1. MATHEMATICAL & CLASSICAL SPECIFICATIONS",
        "role": "Definitive mathematical & classical Jyotish specification (Twin Markdown). Defines the 0–100% dignity spectrum (Phaladīpikā Ch. 3), Ṣaḍvarga divisional weighting (D1:2, D2:1, D3:1, D30:1, D9:2, D12:1), strict Neecha Bhanga alchemical rescue, 9-tier behavioral archetypes, calibrated vitality score (1.0 to 10.0), continuous Parāśara Graha Dṛṣṭi degree curve (Brihat Jataka 2.13), and Deeptādi/Jāgradādi/Bālādi/Lajjitādi avasthās."
    },
    {
        "path": "documentations/master_graha_diagnostics_table.md",
        "category": "1. MATHEMATICAL & CLASSICAL SPECIFICATIONS",
        "role": "Master Graha Diagnostics architectural guide. Documents the 9-column unified diagnostic matrix anatomy, classical Sanskrit citations (BPHS Ch. 32, 34, 45; Phaladīpikā Ch. 3; Kurczak & DiCara), multi-Varga support (D1 to D60), and interactive tooltip pedagogical definitions."
    },
    {
        "path": "documentations/master_diagnostic_audit.md",
        "category": "1. MATHEMATICAL & CLASSICAL SPECIFICATIONS",
        "role": "Architectural audit document detailing the elimination of double/triple counting (retrograde Cheshta Bala, aspect Drik Bala, and Lajjitadi states), single source of truth (SSOT) backend math, mathematical receipt breakdown tooltip, and Nakshatra Overlord integration."
    },
    {
        "path": "jyotish/planetary_evaluation/planetary_evaluation.py",
        "category": "2. BACKEND COMPUTATIONAL ENGINE",
        "role": "Core calculation engine (~4,000 lines). Computes 5-fold compound dignity (Pañcadhā Maitrī), canonical Phaladīpikā Ṣaḍvarga weights, Dispositor host bedrock, 9-tier behavioral archetypes, calibrated vitality score (1.0–10.0) with mathematical receipt, continuous degree aspects, avasthā states, and generates the complete 9-column Master Diagnostic payload (generate_master_diagnostic_payload)."
    },
    {
        "path": "jyotish/planetary_evaluation/lagna_evaluation.py",
        "category": "2. BACKEND COMPUTATIONAL ENGINE",
        "role": "Ascendant (Lagna / Tanū Bhāva) precision evaluation engine. Evaluates the 5 classical diagnostic pillars: The Captain (Lagneśa vitality), The Field (House placement), Horizon Occupants (Benefic armor vs. Malefic stress), Sky-Light (Net Graha Dṛṣṭi on cusp), and Enclosure (Kartarī hemming)."
    },
    {
        "path": "jyotish/planetary_evaluation/__init__.py",
        "category": "2. BACKEND COMPUTATIONAL ENGINE",
        "role": "Public package interface exposing all core evaluation algorithms, avastha classifiers, aspect calculations, and master diagnostic payload builders."
    },
    {
        "path": "templates/widget_templates/tmpl_master_diagnostic.html",
        "category": "3. FRONTEND HTML DOM BLUEPRINT",
        "role": "Reusable HTML widget DOM template (<template id=\"tmpl-master-diagnostic\">). Defines top toolbar with Varga selector (D1–D60), maximize button, and exact 9-column table headers with detailed educational data-tooltip definitions."
    },
    {
        "path": "static/js/widgets/master_diagnostic.js",
        "category": "4. FRONTEND DISPLAY & INTERACTION CONTROLLER",
        "role": "Client-side JavaScript controller (~3,900 lines). Renders the 9-column diagnostic table (Lagna row + 9 Graha rows), deep drawer cockpit engine with interactive tabs (Overview, Drishti Line Graph SVG, Avastha Breakdown, Dispositor Tree, Vitality Math Receipt), continuous aspect SVG curves, and multi-varga switching."
    },
    {
        "path": "static/GEMINI.md",
        "category": "5. FRONTEND DESIGN SYSTEM & TYPOGRAPHY PROTOCOL",
        "role": "Mandatory Astra design system rules: strict 12px font floor (zero sub-pixel text), monochrome STIX Two Math line glyphs (\\uFE0E), anti-pill protocol (de-badged tabular numbers), emoji purge (zero consumer emojis), and exact 9-column Master Diagnostic geometry."
    },
    {
        "path": "documentations/adr/ADR-006-professional-editorial-design-system.md",
        "category": "5. FRONTEND DESIGN SYSTEM & TYPOGRAPHY PROTOCOL",
        "role": "ADR-006: Architectural Decision Record establishing the professional editorial publication design standard, warm parchment palette, anti-pill rules, and mathematical typography."
    },
    {
        "path": "tests/test_planetary_evaluation.py",
        "category": "6. AUTOMATED VERIFICATION TEST SUITE",
        "role": "Comprehensive backend pytest suite (52 unit tests). Validates dignity bounds, 9-tier archetypes, the Three Master Lords of Destiny, continuous aspect virūpas, bidirectional drishti, and mathematical receipt accuracy."
    },
    {
        "path": "tests/test_master_diagnostic_ui.py",
        "category": "6. AUTOMATED VERIFICATION TEST SUITE",
        "role": "Playwright end-to-end browser test suite. Verifies 9-column table rendering, 10 rows (Lagna + 9 Grahas), deep drawer toggle, Varga selector switching, and strict 12px font floor compliance."
    },
    {
        "path": "tests/test_diagnostics_edge_cases.py",
        "category": "6. AUTOMATED VERIFICATION TEST SUITE",
        "role": "Pytest suite for edge cases: verifies zero double-counting, exact mathematical sum of equation parts, and Nakshatra payload structure."
    }
]


def generate_bundle():
    print(f"Bundling Master Graha Diagnostics calculation and frontend presentation files into {OUTPUT_FILE}...")

    buf = []
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 1. Main Header
    buf.append("=" * 95)
    buf.append("ASTRA: MASTER GRAHA DIAGNOSTICS REUSABLE CODEBASE & ARCHITECTURE BUNDLE")
    buf.append(f"GENERATED : {now_str}")
    buf.append("FRAMEWORK : Ernst Wilhelm's Kala Methodology & Classical Parāśari Jyotish")
    buf.append("CORE MATH : Swiss Ephemeris (`swisseph`) | Sāyana Tropical Signs | Campanus 3D Cusps")
    buf.append("UI SYSTEM : Astra Editorial Design System (ADR-006 & static/GEMINI.md)")
    buf.append("=" * 95)
    buf.append("")
    buf.append("EXECUTIVE DIRECTIVE FOR EVALUATING AI / DEVELOPER REUSING THIS BUNDLE:")
    buf.append("-" * 95)
    buf.append("This bundle contains everything required to understand, calculate, serialize, and visually present")
    buf.append("the Master Graha Diagnostics table and its deep drawer cockpit in Astra.")
    buf.append("")
    buf.append("The system solves the fundamental challenge of astrological diagnosis: synthesizing multiple")
    buf.append("isolated strengths (Shadbala, Dignity, Avasthas, Drishti, and House roles) into a single unified,")
    buf.append("coherent, and mathematically transparent diagnostic matrix.")
    buf.append("")
    buf.append("=" * 95)
    buf.append("DIMENSION A: BACKEND CALCULATION ENGINE & ASTROLOGICAL RULES")
    buf.append("=" * 95)
    buf.append("1. ESSENTIAL DIGNITY SPECTRUM (Pañcadhā Maitrī & Phaladīpikā Ch. 3):")
    buf.append("   - Continuous percentage scale: Exalted (100%), Moolatrikona (95%), Own Sign (90%),")
    buf.append("     Great Friend (80%), Friend (60%), Neutral (50%), Enemy (40%), Great Enemy (20%), Debilitated (0%).")
    buf.append("   - Pañcadhā Maitrī: Synthesizes permanent Natural Relationship (Naisargika) with chart-specific")
    buf.append("     Temporary Relationship (Tātkālika: houses 2, 3, 4, 10, 11, 12 from sign lord = Friend; others = Enemy).")
    buf.append("   - Canonical Phaladīpikā Ṣaḍvarga Weighted Dignity:")
    buf.append("     Weights: D1 (2x), D2 (1x), D3 (1x), D30 (1x), D9 (2x), D12 (1x) -> Divisor = 8.")
    buf.append("")
    buf.append("2. DISPOSITOR BEDROCK & ALCHEMICAL RESCUE (Neecha Bhanga):")
    buf.append("   - Host sign lord provides foundational resources.")
    buf.append("   - Strict Neecha Bhanga: Granted strictly to true signs of fall (e.g. Sun in Libra, Moon in Scorpio).")
    buf.append("   - If host dispositor has Dignity >= 62.5% AND Shadbala >= 90%, the debility is alchemically transmuted")
    buf.append("     into extraordinary grit, humility, and mastery (unlocking '⚡ The Transmuted Hero').")
    buf.append("   - Host tiers: Fortified (>=65%), Friendly (50–65%), Neutral (25–50%, 0.0% modifier), Stressed (<25%).")
    buf.append("")
    buf.append("3. SHADBALA CUMULATIVE POTENCY (6 Classical Pillars):")
    buf.append("   - Total Virūpas (60 Virūpas = 1 Rūpa) compared against Parāśara's canonical thresholds:")
    buf.append("     Sun (390v), Moon (360v), Mars (300v), Mercury (420v), Jupiter (390v), Venus (330v), Saturn (300v).")
    buf.append("   - Relative chart rank (#1 to #7) and capacity tiers (Abundant >=125%, Capable >=100%, Deficit <100%).")
    buf.append("   - Rahu and Ketu inherit proxy muscle from their host sign dispositor.")
    buf.append("")
    buf.append("4. CONTINUOUS GRAHA DṚṢṬI (Line-of-Sight Gaze per Brihat Jataka 2.13):")
    buf.append("   - Unbroken aspect curve across 0°–360° relative degrees from source planet:")
    buf.append("     Special full aspects: Mars (4th & 8th / 90° & 210°), Jupiter (5th & 9th / 120° & 240°), Saturn (3rd & 10th / 60° & 270°).")
    buf.append("   - Continuous linear interpolation between anchor points.")
    buf.append("   - Net Dṛṣṭi balance: Supportive (Śubha) vs. Confrontational (Pāpa) in Virūpas.")
    buf.append("")
    buf.append("5. COMPREHENSIVE AVASTHĀ COCKPIT (4 Interlocking Layers):")
    buf.append("   - Layer 1: Biological Age & Fuel (Bālādi - BPHS 45.3 / Vol 2): Bāla (50%), Kumāra (75%), Yuvā (100%), Vṛddha (50%), Mṛta (25%).")
    buf.append("   - Layer 2: Conscious Alertness (Jāgradādi - BPHS 45.5): Jāgrat (100%), Svapna (50%), Suṣupti (10%).")
    buf.append("   - Layer 3: Innate Mood (Dīptādi - BPHS 45.7): Pramudita, Dīpta, Svastha, Śānta, Bhīta, Vikala, Nīpīḍita.")
    buf.append("   - Layer 4: Social Feeling States (Lajjitādi - BPHS 45.11): Mudita, Garvita, Kṣudhita, Kṣobhita, Lajjita, Tṛṣita.")
    buf.append("     Crucial Innovation: Relational severity is dynamically calibrated by the influencer's Jāgradādi alertness.")
    buf.append("")
    buf.append("6. THE REFINED 9-TIER BEHAVIORAL ARCHETYPES & CALIBRATED VITALITY SCORE (1.0 to 10.0):")
    buf.append("   - Cross-references Moral Intent / Quality (Dignity) with Kinetic Power / Stamina (Shadbala):")
    buf.append("     * Royal Dignity (>=75%): High Muscle -> Generous King; Balanced -> Noble Guardian; Low -> Sincere Friend.")
    buf.append("     * High/Friendly (55–74%): High -> Noble Guardian; Balanced -> Capable Executive; Low -> Quiet Supporter.")
    buf.append("     * Neutral Dignity (35–54%): High -> Pragmatic Executive; Balanced -> Dutiful Realist; Low -> Modest Citizen.")
    buf.append("     * Low Dignity (<35%): High -> Armed Dictator; Balanced -> Embattled Striver; Low -> Toothless Bully.")
    buf.append("     * Alchemical Rescue: Transmuted Hero.")
    buf.append("   - Calibrated Vitality Formula:")
    buf.append("     Final Score = clamp(5.0 + (PreScore - 5.0) * (0.8 + 0.2 * E_baladi), 1.0, 10.0)")
    buf.append("   - Complete mathematical audit trail (Receipt) breaks down base, quality, muscle, host, and modifiers.")
    buf.append("")
    buf.append("=" * 95)
    buf.append("DIMENSION B: FRONTEND PRESENTATION LAYER & INFORMATION ARCHITECTURE")
    buf.append("=" * 95)
    buf.append("The frontend presentation is governed strictly by static/GEMINI.md and ADR-006:")
    buf.append("  - Strict 12px Font Floor: Zero sub-pixel typography (< 12px is prohibited).")
    buf.append("  - Monochrome STIX Two Math Line Glyphs (\\uFE0E): No colored OS emoji boxes.")
    buf.append("  - Anti-Pill Protocol: Routine tabular data (degrees, coordinates, dispositors) rendered as clean tabular numbers.")
    buf.append("  - Emoji Purge: Zero consumer emojis; replaced with semantic CSS micro-dots and square micro-tags.")
    buf.append("  - Exact 9-Column Master Diagnostic Geometry: Retain all 9 columns in HTML template and JS.")
    buf.append("")
    buf.append("THE 9 TABLE COLUMNS:")
    buf.append("  Col 1: Graha & Kāraka (Planet glyph, motion [R]/[C], Chara Kāraka soul role, Master Lord badges)")
    buf.append("  Col 2: Longitude & Bhāva (Exact tropical coordinate, sign, Whole Sign house, Campanus Bhava Chalita shift)")
    buf.append("  Col 3: Dignity & Sambandha (5-Fold dignity status, %, natural/temporary/compound relationship)")
    buf.append("  Col 4: Dispositor (Rāśi Lord) (Host sign lord, placed sign & house, host dignity & Shadbala, rescue status)")
    buf.append("  Col 5: Ṣaḍbala Strength (Total Virūpas & Rūpas, % of required quota, chart rank #1–#7, Ishta/Kashta fruit)")
    buf.append("  Col 6: Dṛṣṭi & Yuti (Aspects) (Conjunction companions, incoming/outgoing/mutual aspect rays with +/- Virūpas)")
    buf.append("  Col 7: Nakṣatra & Pada (Lunar mansion, pada 1–4, presiding deity, planetary Overlord driving Vimshottari)")
    buf.append("  Col 8: Avasthās (Bālādi biological age, Jāgradādi alertness, Dīptādi innate mood, Lajjitādi feeling states)")
    buf.append("  Col 9: Archetype & Vitality (1–10) (9-tier behavioral archetype title, calibrated vitality score, hover receipt)")
    buf.append("")
    buf.append("DEEP DRAWER COCKPIT (INTERACTIVE ROW EXPANSION):")
    buf.append("  Clicking any planet row smoothly expands the Deep Drawer Cockpit containing 5 detailed diagnostic tabs:")
    buf.append("  1. Overview: Executive summary scorecard, dignity breakdown, and functional role.")
    buf.append("  2. Continuous Dṛṣṭi Line Graph: Full 360° SVG curve showing exact aspect vision cast and received.")
    buf.append("  3. Avasthā Breakdown: Complete 4-layer avasthā diagnosis with alertness calibration.")
    buf.append("  4. Dispositor Tree: Recursive host dispositor chain tracking foundational stability.")
    buf.append("  5. Vitality Math Receipt: Step-by-step arithmetic equation breakdown demystifying the final 1–10 score.")
    buf.append("")
    buf.append("MULTI-VARGA DIVISIONAL CHARTS (D1 THROUGH D60):")
    buf.append("  The top toolbar features a native Varga selector dropdown. Selecting D1 through D60 dynamically")
    buf.append("  recalculates and re-renders all 9 columns for the selected harmonic chart.")
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
            buf.append(f" {idx:2d}. [{item['category']}] {rel_path} ({line_count:,} lines, {byte_size:,} bytes)")
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
    buf.append("MASTER GRAHA DIAGNOSTICS JSON SCHEMA REFERENCE (chart_dict['master_diagnostic'])")
    buf.append("=" * 95)
    buf.append("This is the exact JSON structure generated by jyotish/planetary_evaluation/planetary_evaluation.py")
    buf.append("and transmitted to the frontend widget (master_diagnostic.js):")
    buf.append("")
    buf.append("""{
  "varga": "D1",
  "subject_name": "Angelina Jolie",
  "columns": [
    "Graha & Kāraka",
    "Longitude & Bhāva",
    "Dignity & Sambandha",
    "Dispositor (Rāśi Lord)",
    "Ṣaḍbala Strength",
    "Dṛṣṭi & Yuti (Aspects)",
    "Nakṣatra & Pada",
    "Avasthās",
    "Archetype & Vitality"
  ],
  "rows": [
    {
      "planet": "Sun",
      "glyph": "☉︎",
      "graha_karaka": {
        "planet": "Sun",
        "glyph": "☉︎",
        "is_retrograde": false,
        "is_combust": false,
        "chara_karaka": "Bhatrikaraka (Siblings)",
        "is_lagna_lord": false,
        "badge": "Sun"
      },
      "longitude_bhava": {
        "longitude": 73.3421,
        "sign": "Gemini",
        "degree_in_sign": 13.3421,
        "formatted": "13° Gemini 21'",
        "whole_sign_house": 11,
        "expression": "House 11 (Gemini)"
      },
      "dignity_sambandha": {
        "dignity": "Friend's Sign",
        "dignity_clean": "Friend",
        "dignity_score": 60.0,
        "shadvarga_dignity_pct": 61.25,
        "natural_relationship": "Friend",
        "temporary_relationship": "Friend",
        "compound_relationship": "Great Friend",
        "summary": "Friend 60 / 61.2"
      },
      "dispositor": {
        "dispositor": "Mercury",
        "placed_sign": "Gemini",
        "placed_house": 11,
        "is_rescued": false,
        "summary": "Mercury in H11 (Gemini)"
      },
      "shadbala": {
        "total_virupas": 412.35,
        "total_rupas": 6.87,
        "pct_required": 105.7,
        "chart_rank": 3,
        "ishta_phala": 28.45,
        "kashta_phala": 14.22,
        "summary": "412.4v (106%) #3"
      },
      "drishti_yuti": {
        "conjunctions": [
          {
            "other_planet": "Mercury",
            "separation_degrees": 2.15,
            "formatted_orb": "2°09'",
            "orb_band": "Close Conjunction",
            "power_pct": 82.5,
            "display": "Mercury (Close Conjunction, 2°09')"
          }
        ],
        "incoming_aspects": [
          { "planet": "Jupiter", "virupas": 42.5, "is_benefic": true, "display": "Jupiter (+43v)" }
        ],
        "outgoing_aspects": [
          { "planet": "Moon", "virupas": 58.1, "is_benefic": false, "display": "Moon (58v)" }
        ],
        "mutual_aspects": [],
        "has_mutual_aspect": false,
        "in_war": false,
        "summary": "Yuti: Mercury (Close Conjunction, 2°09') | Incoming: Jupiter (43v)"
      },
      "nakshatra_pada": {
        "nakshatra": "Ardra",
        "pada": 3,
        "lord": "Rahu",
        "sub_lord": "Moon",
        "tara_number": 6,
        "summary": "Ardra P3 (Rahu)"
      },
      "avasthas": {
        "baladi": "Yuva (Prime / Mature)",
        "jagradadi": "Jagrat (Awake)",
        "deeptadi": "Mudita (Delighted / Joyful)",
        "lajjitadi": ["Mudita"],
        "summary": "Yuva • Jagrat • Mudita"
      },
      "archetype_vitality": {
        "archetype": "The Noble Guardian",
        "vitality_score": 7.8,
        "receipt": "Intent: 61% | Power: 106% -> 7.8/10"
      },
      "unified_cockpit": {
        "stage1_essence": { "status": "Friend", "score": 60.0 },
        "stage2_environment": { "drishti_net": 42.5 },
        "stage3_operational": { "vitality_score": 7.8, "archetype": "The Noble Guardian" }
      }
    }
  ],
  "summary": {
    "total_grahas": 9,
    "varga": "D1",
    "ascendant_sign": "Leo",
    "highest_vitality": "Venus",
    "lowest_vitality": "Saturn"
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
    artifact_txt = os.path.join(ARTIFACT_DIR, "bundle_master_graha_diagnostics.txt")
    with open(artifact_txt, "w", encoding="utf-8") as f:
        f.write(full_bundle_text)
    print(f"✅ Successfully wrote artifact TXT: {artifact_txt}")

    # Write artifact markdown bundle
    artifact_md = os.path.join(ARTIFACT_DIR, "bundle_master_graha_diagnostics.md")
    with open(artifact_md, "w", encoding="utf-8") as f:
        f.write(f"# Master Graha Diagnostics: Complete Calculation & Presentation Audit Bundle\n\n```text\n{full_bundle_text[:25000]}\n... [truncated in markdown preview, see bundle_master_graha_diagnostics.txt for full {len(full_bundle_text):,} bytes] ...\n```\n")
    print(f"✅ Successfully wrote artifact MD: {artifact_md}")

    print("\nAudited Files Included in Bundle:")
    for rec in file_records:
        print(f"  [{rec['index']:2d}] {rec['path']} ({rec['lines']:,} lines, {rec['bytes']:,} bytes)")


if __name__ == "__main__":
    generate_bundle()
