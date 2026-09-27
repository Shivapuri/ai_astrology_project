#!/usr/bin/env python3
"""
scripts/export_codebase.py
==========================
Aggregates Astra's complete codebase into a single, high-density, structured text export
optimized for AI evaluation, architectural auditing, and pair-programming ingestion.

Scopes supported:
- 'all': Unified application export (backend engines + frontend UI, tests excluded by default)
- 'jyotish': Pure calculation engine (/jyotish/) sorted into 14 pedagogical chapters with section headers
- 'backend': Jyotish engines + Flask application server and blueprints (tests excluded)
- 'frontend': Split.js workspace layout, CSS design tokens, HTML partials, and JS widgets
- 'report': Synthesis report desk (Polarity core, 4-step Nakshatra scoring, and interactive cockpit)
- 'split': Generates both frontend and backend exports in a single command
"""

import os
import sys
import argparse
import re

DEFAULT_OUTPUT_FILE = "codebase_export.txt"
DEFAULT_FRONTEND_OUTPUT_FILE = "codebase_export_frontend.txt"
DEFAULT_BACKEND_OUTPUT_FILE = "codebase_export_backend.txt"
DEFAULT_REPORT_OUTPUT_FILE = "codebase_export_report.txt"
DEFAULT_JYOTISH_OUTPUT_FILE = "codebase_export_jyotish.txt"

DEFAULT_MAX_SIZE_MB = 2.8
DEFAULT_FRONTEND_MAX_SIZE_MB = 1.0
DEFAULT_BACKEND_MAX_SIZE_MB = 1.6
DEFAULT_REPORT_MAX_SIZE_MB = 0.5
DEFAULT_JYOTISH_MAX_SIZE_MB = 2.0

EXCLUDED_DIRS = {
    ".git",
    "venv",
    "env",
    ".venv",
    "node_modules",
    "__pycache__",
    "cache",
    "ephe",
    "database",
    "anki_decks",
    "sanskrit_texts",
    "staticfiles",
    ".idea",
    ".pytest_cache",
    ".ruff_cache",
    "backups",
    ".gemini",
    ".agents",
    "angelina-jolie-pdfs",
    "knowledge_base",
    "lajjitadi_transcription",
    "ascendant_reports",
    "scratch",
    "tests",  # Automated test suites excluded by default from production exports
}

EXCLUDED_FILES = {
    "code_export.txt",
    "codebase_export.txt",
    "codebase_export_frontend.txt",
    "codebase_export_backend.txt",
    "codebase_export_report.txt",
    "codebase_export_jyotish.txt",
    "commits_export.txt",
    "commits_export.md",
    "package-lock.json",
    "yarn.lock",
    ".env",
    ".DS_Store",
    "server.log",
    "server.pid",
    "va_text.txt",
    "transcript.txt",
    "build_vedic_astrology_epub_master.py",
    "generate_agnidevi_learning_style_pdf.py",
    "generate_first_house_pdf.py",
    "generate_learning_style_pdf.py",
    "build_full_epub.py",
    "generate_epub.py",
    "build_bphs_database.py",
    "build_all_databases.py",
    "build_kb_json.py",
    "export_commits.py",
    "Shivapuri_Learning_Style_Analysis.md",
    "angelina_jolie_shayanadi_vargas.json",
    "angelina_jolie_shayanadi_vargas.csv",
    "analyze_learning_style.py",
    "audit_shadbala.py",
    "session_handoff.md",
    "angelina_jolie_proof_catalog.md",
    "build_proof_catalog.py",
    "screenshot.py",
    "screenshot_master_diag.py",
    "screenshot_aspects_interactive.py",
    "screenshot_shivapuri_mars.py",
    "screenshot_report_widget.py",
    "screenshot_cockpit_drawer.py",
    "search_krishna_chart.py",
    "test_diagnostics_edge_cases.py",
    "angelina_jolie_baselines.json",
    "astra_verification_task_list.md",
    "knowledge_base.json",
    "generate_ascendant_report.py",
    "analyze_ascendant.py",
    # Scratch & developer verification tools
    "verify_all_chart_clicks.py",
    "verify_context_ui.py",
    "verify_stepper_visuals.py",
    "take_diagnostic_screenshot.py",
    "scratch.py",
    # Historical / superseded documentation notes
    "HANDOFF.md",
    "avasthas_remaining_tasks.md",
    "shadbala_audit_report.md",
    "master_graha_diagnostics_table.md",
    "matrix_reading_guide.md",
    "ui_scaling_guidelines.md",
    # Playwright browser UI clicker tests
    "test_ui_e2e.py",
    "test_new_widgets_ui.py",
    "test_workspaces_and_kala_menu.py",
    "test_aspect_tables_ui.py",
    "test_aspects_interactive.py",
    "test_open_chart_library.py",
    "test_time_stepper.py",
    "test_planetary_evaluation_ui.py",
    "test_time_stepper_ui.py",
    "test_shadbala_widget_ui.py",
    "test_search_krishna_chart.py",
    "test_master_diagnostic_ui.py",
    # Sub-unit tests
    "test_planetary_evaluation.py",
    "test_tripod_and_interpretations.py",
    "test_varga_avasthas.py",
    "test_vimshottari_timeline.py",
    "test_quantitative_subvalues.py",
    "test_varga_lajjitadi_transcription.py",
    "test_sign_attributes.py",
    "test_aspects.py",
    "test_ascendant_analysis.py",
    "test_varga_shadbala_transcription.py",
    "test_d10_mode.py",
    "test_nakshatra_system.py",
    "test_combustion.py",
    "test_house_aspects.py",
    "test_karakas.py",
    "test_basic_placements.py",
    "test_vimshopaka.py",
    "test_dignities.py",
    "test_svg_generation.py",
}

EXCLUDED_EXTENSIONS = {
    ".pdf",
    ".epub",
    ".mp3",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".ico",
    ".svg",
    ".bin",
    ".dat",
    ".bsp",
    ".sqlite",
    ".pyc",
    ".csv",
}

ALLOWED_EXTENSIONS = {
    ".py",
    ".md",
    ".html",
    ".js",
    ".css",
    ".json",
    ".txt",
    ".ini",
    ".conf",
    ".toml",
    ".sh",
    ".csv",
    ".yml",
    ".yaml",
}

# 14 Pedagogical Chapters for Jyotish Calculation Engine Export
JYOTISH_SECTIONS = [
    (
        "1. Core Astronomical Math & Calculation Orchestrator",
        [
            "jyotish/GEMINI.md",
            "jyotish/jyotish_rules.txt",
            "jyotish/calc_utils.py",
            "jyotish/generate_jyotish.md",
            "jyotish/generate_jyotish.py",
            "jyotish/draw_chart.py",
        ],
    ),
    (
        "2. Planetary Relationships & Aspects (Maitri & Drishti)",
        [
            "jyotish/relationships/relationships.md",
            "jyotish/relationships/relationships.py",
            "jyotish/aspects/aspects.md",
            "jyotish/aspects/aspects.py",
        ],
    ),
    (
        "3. Planetary & House Strengths (Shadbala & Bhava Bala)",
        [
            "jyotish/shadbala/__init__.py",
            "jyotish/shadbala/shadbala.md",
            "jyotish/shadbala/shadbala.py",
            "jyotish/shadbala/bhava_bala.py",
        ],
    ),
    (
        "4. Planetary Conditions & States (Avasthas)",
        [
            "jyotish/avasthas/GEMINI.md",
            "jyotish/avasthas/__init__.py",
            "jyotish/avasthas/quantitative.md",
            "jyotish/avasthas/quantitative.py",
            "jyotish/avasthas/bala.md",
            "jyotish/avasthas/bala.py",
            "jyotish/avasthas/jagrat.md",
            "jyotish/avasthas/jagrat.py",
            "jyotish/avasthas/deepti.md",
            "jyotish/avasthas/deepti.py",
            "jyotish/avasthas/lajjita.md",
            "jyotish/avasthas/lajjita.py",
            "jyotish/avasthas/shayana.md",
            "jyotish/avasthas/shayana.py",
        ],
    ),
    (
        "5. Divisional Harmonic Strength (Vimshopaka Bala)",
        [
            "jyotish/vimshopaka/__init__.py",
            "jyotish/vimshopaka/vimshopaka.md",
            "jyotish/vimshopaka/vimshopaka.py",
        ],
    ),
    (
        "6. Planetary Evaluation, Nine-Tier Archetypes & Lagna Vitality",
        [
            "jyotish/planetary_evaluation/__init__.py",
            "jyotish/planetary_evaluation/planetary_evaluation.md",
            "jyotish/planetary_evaluation/planetary_evaluation.py",
            "jyotish/planetary_evaluation/lagna_evaluation.py",
            "jyotish/planetary_evaluation/adr/README.md",
            "jyotish/planetary_evaluation/adr/001-nine-tier-archetype-and-neutral-tilt.md",
            "jyotish/planetary_evaluation/adr/002-strict-neecha-bhanga-exclusivity.md",
            "jyotish/planetary_evaluation/adr/003-functional-ascendant-and-chandal-resynthesis.md",
            "jyotish/planetary_evaluation/adr/004-graha-yuddha-and-venus-invariance.md",
            "jyotish/planetary_evaluation/adr/005-recursive-drishti-dampening.md",
            "jyotish/planetary_evaluation/adr/006-inherent-dignity-vs-house-field.md",
            "jyotish/planetary_evaluation/adr/007-nodal-dispositor-proxy-and-conjunction-orbs.md",
            "jyotish/planetary_evaluation/adr/008-baladi-avastha-biological-efficiency.md",
            "jyotish/planetary_evaluation/adr/009-audit-metered-twice-decoupling.md",
            "jyotish/planetary_evaluation/adr/010-aspect-vision-badges-and-twenty-virupa-rule.md",
        ],
    ),
    (
        "7. Classical Yogas & Breakers",
        [
            "jyotish/yogas/__init__.py",
            "jyotish/yogas/yogas.md",
            "jyotish/yogas/models.py",
            "jyotish/yogas/evaluator.py",
            "jyotish/yogas/raja_yogas.py",
            "jyotish/yogas/dhana_daridrya.py",
            "jyotish/yogas/pancha_mahapurusha.py",
            "jyotish/yogas/lunar_solar_yogas.py",
            "jyotish/yogas/viparita.py",
            "jyotish/yogas/parivartana.py",
            "jyotish/yogas/kartari.py",
            "jyotish/yogas/chandal_yogas.py",
            "jyotish/yogas/breakers.py",
        ],
    ),
    (
        "8. Ashtakavarga Assessment",
        [
            "jyotish/ashtakavarga/__init__.py",
            "jyotish/ashtakavarga/ashtakavarga.md",
            "jyotish/ashtakavarga/ashtakavarga.py",
        ],
    ),
    (
        "9. Equatorial Sidereal Nakshatras & Lore",
        [
            "jyotish/nakshatra_metadata.md",
            "jyotish/nakshatra_metadata.py",
            "jyotish/nakshatras/__init__.py",
            "jyotish/nakshatras/lore.py",
            "jyotish/nakshatras/nakshatra_data.py",
            "jyotish/nakshatras/nakshatra_database.json",
        ],
    ),
    (
        "10. Vimshottari Dasha Progression",
        [
            "jyotish/dashas/__init__.py",
            "jyotish/dashas/vimshottari.md",
            "jyotish/dashas/vimshottari.py",
        ],
    ),
    (
        "11. Karakas & Sign Attributes",
        [
            "jyotish/karakas.md",
            "jyotish/karakas.py",
            "jyotish/sign_attributes.md",
            "jyotish/sign_attributes.py",
        ],
    ),
    (
        "12. Astrological Synthesis Report Subsystem",
        [
            "jyotish/report/__init__.py",
            "jyotish/report/report_engine.py",
            "jyotish/report/significations_data.json",
            "jyotish/report/significations_flowcharts.json",
        ],
    ),
    (
        "13. Scripture Databases & Native Management",
        [
            "jyotish/bphs_db.py",
            "jyotish/scripture_db.py",
            "jyotish/native_manager.py",
        ],
    ),
    (
        "14. Publication-Grade PDF Exporter",
        [
            "jyotish/pdf_exporter.md",
            "jyotish/pdf_exporter.py",
        ],
    ),
]

JYOTISH_FILE_SECTION_MAP = {}
JYOTISH_SORT_KEY_MAP = {}
for _sec_idx, (_sec_title, _flist) in enumerate(JYOTISH_SECTIONS, 1):
    for _f_idx, _fpath in enumerate(_flist, 1):
        JYOTISH_FILE_SECTION_MAP[_fpath] = _sec_title
        JYOTISH_SORT_KEY_MAP[_fpath] = (_sec_idx, _f_idx)


def get_jyotish_sort_key(rel_path: str):
    if rel_path in JYOTISH_SORT_KEY_MAP:
        return JYOTISH_SORT_KEY_MAP[rel_path]
    return (99, 99, rel_path)


FILE_METADATA_REGISTRY = {
    "Gemini.md": (
        "AI Agent Guidelines",
        "Root project conventions, core philosophy, and AI operating rules",
    ),
    "README.md": (
        "Project Documentation",
        "Project overview, repository structure, and setup instructions",
    ),
    "app.py": (
        "Web Application",
        "Flask application exposing REST endpoints for calculations, SVGs, and data",
    ),
    "run.py": (
        "Web Application",
        "Application launcher and environment bootstrapper",
    ),
    "screenshot.py": (
        "Developer Tooling",
        "Playwright automated screenshot capture for visual regression testing",
    ),
    "astra_verification_task_list.md": (
        "Project Roadmap",
        "Mathematical and functional verification checklist against Kala",
    ),
    "session_handoff.md": (
        "Project Roadmap",
        "Session handoff document recording recent mathematical changes",
    ),
    ".gitignore": (
        "Configuration",
        "Git ignore patterns for ephemeris cache, virtualenvs, and temp files",
    ),
    # Section 1: Core Orchestration & Astronomy
    "jyotish/GEMINI.md": (
        "AI Agent Guidelines",
        "Module-specific calculation rules, scriptural authority, and architecture instructions for Jyotish engine",
    ),
    "jyotish/jyotish_rules.txt": (
        "Core Math Spec",
        "Concise foundational rules for vargas, planetary relationships, karakas, and aspects",
    ),
    "jyotish/calc_utils.py": (
        "Core Math Engine",
        "Astronomical coordinate transformations, angle normalizations, cusp utilities, and speed calculations",
    ),
    "jyotish/generate_jyotish.md": (
        "Core Math Spec",
        "Mathematical specification, Campanus house algorithm, coordinate foundations, and varga algorithms",
    ),
    "jyotish/generate_jyotish.py": (
        "Core Math Engine",
        "Central calculation orchestrator computing tropical placements, harmonic vargas, Campanus bhavas, dignities, and dashas",
    ),
    "jyotish/draw_chart.py": (
        "Chart Visualization",
        "SVG chart diagram generator (North and South Indian styles, planetary glyphs, dynamic house sizing)",
    ),
    # Section 2: Relationships & Aspects
    "jyotish/relationships/relationships.md": (
        "Core Math Spec",
        "Mathematical specification for Panchadha Maitri (5-fold natural, temporary, and compound friendship)",
    ),
    "jyotish/relationships/relationships.py": (
        "Core Math: Maitri",
        "Planetary friendship engine calculating natural (naisargika), temporary (tatkalika), and 5-fold (panchadha) maitri",
    ),
    "jyotish/aspects/aspects.md": (
        "Core Math Spec",
        "Parashari Drishti (aspect rays) mathematical formulas and degree-based aspect weights",
    ),
    "jyotish/aspects/aspects.py": (
        "Core Math: Drishti",
        "Planetary and house aspect calculation engine according to classical Parashari rules",
    ),
    # Section 3: Shadbala & Bhava Bala
    "jyotish/shadbala/__init__.py": (
        "Core Math: Shadbala",
        "Package initialization for 6-fold planetary strength calculation",
    ),
    "jyotish/shadbala/shadbala.md": (
        "Core Math Spec",
        "Mathematical formulas and Sanskrit proofs for all 6 Shadbala strengths (Sthana, Dig, Kala, Cheshta, Naisargika, Drik)",
    ),
    "jyotish/shadbala/shadbala.py": (
        "Core Math: Shadbala",
        "Complete 6-fold planetary strength calculation engine validating against Kala software baselines",
    ),
    "jyotish/shadbala/bhava_bala.py": (
        "Core Math: Shadbala",
        "Comprehensive 12-house strength assessment (Bhava Adhipati, Bhava Dig, Bhava Drishti Bala)",
    ),
    # Section 4: Avasthas
    "jyotish/avasthas/GEMINI.md": (
        "AI Agent Guidelines",
        "Module-specific guidelines and scriptural baselines for planetary avastha implementations",
    ),
    "jyotish/avasthas/__init__.py": (
        "Core Math: Avasthas",
        "Package initialization for planetary conditions and states (Avasthas)",
    ),
    "jyotish/avasthas/quantitative.md": (
        "Core Math Spec",
        "Mathematical specification for quantitative avastha matrices and net operational modifiers",
    ),
    "jyotish/avasthas/quantitative.py": (
        "Core Math: Avasthas",
        "Quantitative avasthas matrix calculations (Uccha, Dig, Cheshta, Subha, Ishta, Drishti Yuti, Veda)",
    ),
    "jyotish/avasthas/bala.md": (
        "Core Math Spec",
        "Mathematical rules and degree bands for Baladi avasthas (Infant, Youthful, Adolescent, Old, Dead)",
    ),
    "jyotish/avasthas/bala.py": (
        "Core Math: Avasthas",
        "Baladi avasthas calculation engine measuring physical/biological maturity",
    ),
    "jyotish/avasthas/jagrat.md": (
        "Core Math Spec",
        "Mathematical rules linking planetary dignities to Jagrat (Awake), Svapna (Dreaming), and Sushupti (Sleeping) states",
    ),
    "jyotish/avasthas/jagrat.py": (
        "Core Math: Avasthas",
        "Jagradadi avasthas calculation engine measuring alertness and consciousness",
    ),
    "jyotish/avasthas/deepti.md": (
        "Core Math Spec",
        "Sanskrit definitions and rules for Deeptadi 9 essential dignities (Exalted to Debilitated)",
    ),
    "jyotish/avasthas/deepti.py": (
        "Core Math: Avasthas",
        "Deeptadi avasthas calculation engine determining planetary luminous condition",
    ),
    "jyotish/avasthas/lajjita.md": (
        "Core Math Spec",
        "Sanskrit definitions and planetary condition rules for Lajjitadi avasthas (Proud, Starved, Thirsty, Agitated, Ashamed, Delighted)",
    ),
    "jyotish/avasthas/lajjita.py": (
        "Core Math: Avasthas",
        "Lajjitadi avasthas calculation engine measuring emotional and psychological feeling states",
    ),
    "jyotish/avasthas/shayana.md": (
        "Core Math Spec",
        "Formulas and modifier calculations for Shayanadi 12 avasthas (Resting, Sitting, Eating, Pleasure, etc.)",
    ),
    "jyotish/avasthas/shayana.py": (
        "Core Math: Avasthas",
        "Shayanadi 12 avasthas calculation engine determining day-to-day behavioral activities",
    ),
    # Section 5: Vimshopaka Bala
    "jyotish/vimshopaka/__init__.py": (
        "Core Math: Vimshopaka",
        "Package initialization for divisional varga harmonic strength assessment",
    ),
    "jyotish/vimshopaka/vimshopaka.md": (
        "Core Math Spec",
        "20-point divisional varga weighting specification across Shadvarga, Saptavarga, Dashavarga, and Shodashavarga",
    ),
    "jyotish/vimshopaka/vimshopaka.py": (
        "Core Math: Vimshopaka",
        "Vimshopaka Bala calculation engine computing planetary strength across divisional harmonic charts",
    ),
    # Section 6: Planetary Evaluation & Dignities
    "jyotish/planetary_evaluation/__init__.py": (
        "Planetary Evaluation",
        "Package initialization for planetary evaluation and archetype assessment",
    ),
    "jyotish/planetary_evaluation/planetary_evaluation.md": (
        "Planetary Evaluation Spec",
        "Nine-tier dignity archetype specification, directional tilts, Neecha Bhanga, and Graha Yuddha rules",
    ),
    "jyotish/planetary_evaluation/planetary_evaluation.py": (
        "Planetary Evaluation Engine",
        "Comprehensive planetary dignity evaluation engine classifying grahas into 9 classical archetypes with vitality scoring",
    ),
    "jyotish/planetary_evaluation/lagna_evaluation.py": (
        "Planetary Evaluation Engine",
        "Ascendant vitality, physical body resilience, and life force assessment",
    ),
    "jyotish/planetary_evaluation/adr/README.md": (
        "Architecture Decisions",
        "Index of Architectural Decision Records for planetary evaluation rules",
    ),
    "jyotish/planetary_evaluation/adr/001-nine-tier-archetype-and-neutral-tilt.md": (
        "Architecture Decisions",
        "ADR 001: Nine-tier dignity archetype spectrum and neutral directional tilt",
    ),
    "jyotish/planetary_evaluation/adr/002-strict-neecha-bhanga-exclusivity.md": (
        "Architecture Decisions",
        "ADR 002: Strict Neecha Bhanga cancellation exclusivity and dignity upgrade rules",
    ),
    "jyotish/planetary_evaluation/adr/003-functional-ascendant-and-chandal-resynthesis.md": (
        "Architecture Decisions",
        "ADR 003: Functional nature by Ascendant and Guru-Chandal yoga resynthesis",
    ),
    "jyotish/planetary_evaluation/adr/004-graha-yuddha-and-venus-invariance.md": (
        "Architecture Decisions",
        "ADR 004: Planetary war (Graha Yuddha) victor determination and Venus invariance",
    ),
    "jyotish/planetary_evaluation/adr/005-recursive-drishti-dampening.md": (
        "Architecture Decisions",
        "ADR 005: Recursive aspectual drishti dampening to prevent feedback oscillations",
    ),
    "jyotish/planetary_evaluation/adr/006-inherent-dignity-vs-house-field.md": (
        "Architecture Decisions",
        "ADR 006: Inherent planetary dignity vs accidental house placement field separation",
    ),
    "jyotish/planetary_evaluation/adr/007-nodal-dispositor-proxy-and-conjunction-orbs.md": (
        "Architecture Decisions",
        "ADR 007: Rahu/Ketu dispositor proxy behavior and conjunction orb thresholds",
    ),
    "jyotish/planetary_evaluation/adr/008-baladi-avastha-biological-efficiency.md": (
        "Architecture Decisions",
        "ADR 008: Baladi avastha biological efficiency modifiers on functional expression",
    ),
    "jyotish/planetary_evaluation/adr/009-audit-metered-twice-decoupling.md": (
        "Architecture Decisions",
        "ADR 009: Decoupling of evaluation meter audits from raw calculation pipelines",
    ),
    "jyotish/planetary_evaluation/adr/010-aspect-vision-badges-and-twenty-virupa-rule.md": (
        "Architecture Decisions",
        "ADR 010: Aspect vision badge display and 20-virupa significance threshold",
    ),
    # Section 7: Classical Yogas & Breakers
    "jyotish/yogas/__init__.py": (
        "Classical Yogas",
        "Package initialization for classical planetary yoga detection",
    ),
    "jyotish/yogas/yogas.md": (
        "Classical Yogas Spec",
        "Comprehensive catalog and mathematical logic for classical Parashari yogas and breakers",
    ),
    "jyotish/yogas/models.py": (
        "Classical Yogas",
        "Data structures, enums, and dataclasses representing detected yogas and their attributes",
    ),
    "jyotish/yogas/evaluator.py": (
        "Classical Yogas",
        "Master yoga evaluation orchestrator running detection pipelines across all yoga categories",
    ),
    "jyotish/yogas/raja_yogas.py": (
        "Classical Yogas",
        "Detection engine for Kendra and Trikona lord associations forming Raja Yogas",
    ),
    "jyotish/yogas/dhana_daridrya.py": (
        "Classical Yogas",
        "Detection engine for Dhana (wealth-producing) and Daridrya (poverty/deprivation) yogas",
    ),
    "jyotish/yogas/pancha_mahapurusha.py": (
        "Classical Yogas",
        "Detection engine for 5 Great Person yogas (Ruchaka, Bhadra, Hamsa, Malavya, Sasa)",
    ),
    "jyotish/yogas/lunar_solar_yogas.py": (
        "Classical Yogas",
        "Detection engine for Sun and Moon phase combinations (Sunapha, Anapha, Durudhara, Kemadruma, etc.)",
    ),
    "jyotish/yogas/viparita.py": (
        "Classical Yogas",
        "Detection engine for Viparita Raja Yogas (Harsha, Sarala, Vimala through 6th, 8th, 12th lords in Dusthanas)",
    ),
    "jyotish/yogas/parivartana.py": (
        "Classical Yogas",
        "Detection engine for mutual house exchanges (Maha, Khala, and Dainya Parivartana)",
    ),
    "jyotish/yogas/kartari.py": (
        "Classical Yogas",
        "Detection engine for beneficial (Shubha Kartari) and malefic (Papa Kartari) hemming conditions",
    ),
    "jyotish/yogas/chandal_yogas.py": (
        "Classical Yogas",
        "Detection engine for Guru Chandal and nodal contamination yogas",
    ),
    "jyotish/yogas/breakers.py": (
        "Classical Yogas",
        "Classical yoga cancellation engine (Yoga Bhanga) evaluating debilitation, combustion, and malefic aspects",
    ),
    # Section 8: Ashtakavarga
    "jyotish/ashtakavarga/__init__.py": (
        "Ashtakavarga",
        "Package initialization for Ashtakavarga 8-fold assessment",
    ),
    "jyotish/ashtakavarga/ashtakavarga.md": (
        "Ashtakavarga Spec",
        "Classical rules and bindu distribution matrices for Bhinnashtakavarga and Sarvashtakavarga",
    ),
    "jyotish/ashtakavarga/ashtakavarga.py": (
        "Ashtakavarga Engine",
        "Complete Ashtakavarga calculation engine computing individual and total bindu scores for transit evaluation",
    ),
    # Section 9: Nakshatras & Lore
    "jyotish/nakshatra_metadata.md": (
        "Nakshatras & Lore Spec",
        "Astronomical anchor specification for Dhruva Galactic Center equatorial sidereal nakshatras",
    ),
    "jyotish/nakshatra_metadata.py": (
        "Nakshatras & Lore",
        "Star coordinate mappings, ecliptic projections, and nakshatra boundary algorithms",
    ),
    "jyotish/nakshatras/__init__.py": (
        "Nakshatras & Lore",
        "Package initialization exposing Nakshatra query and lookup APIs",
    ),
    "jyotish/nakshatras/lore.py": (
        "Nakshatras & Lore",
        "Authoritative lookup and normalization module for all 27 Nakshatras and 7 temperament groups",
    ),
    "jyotish/nakshatras/nakshatra_data.py": (
        "Nakshatras & Lore",
        "Authoritative data store containing Sanskrit lore, deities, symbols, and psychological profiles",
    ),
    "jyotish/nakshatras/nakshatra_database.json": (
        "Nakshatras & Lore Data",
        "Structured JSON database containing complete botanical, animal, deity, and directional nakshatra correspondences",
    ),
    # Section 10: Dashas
    "jyotish/dashas/__init__.py": (
        "Dashas & Timelines",
        "Package initialization for planetary period calculation",
    ),
    "jyotish/dashas/vimshottari.md": (
        "Dashas & Timelines Spec",
        "Mathematical formulas for the 120-year Vimshottari Dasha progression and balance of dasha at birth",
    ),
    "jyotish/dashas/vimshottari.py": (
        "Dashas & Timelines Engine",
        "Vimshottari Dasha engine computing Mahadasha, Antardasha, and Pratyantardasha periods with exact date intervals",
    ),
    # Section 11: Karakas & Sign Attributes
    "jyotish/karakas.md": (
        "Karakas Spec",
        "Classical Parashari and Jaimini rules for Sthira (fixed) and Chara (variable 7/8) Karakas",
    ),
    "jyotish/karakas.py": (
        "Karakas Engine",
        "Calculation engine determining Atmakaraka, Amatyakaraka, and remaining significators according to Parashara and Jaimini",
    ),
    "jyotish/sign_attributes.md": (
        "Sign Attributes Spec",
        "Mathematical specification for 12 zodiac sign distributions (Elements, Mobility, Polarity, Varnas, Doshas) and Kalapurusha anatomy",
    ),
    "jyotish/sign_attributes.py": (
        "Sign Attributes Engine",
        "Calculates element, modality, and guna balances along with Kalapurusha bodily governance mappings",
    ),
    # Section 12: Astrological Synthesis Report Subsystem
    "jyotish/report/__init__.py": (
        "Report Subsystem",
        "Package initialization exposing generate_report_payload",
    ),
    "jyotish/report/report_engine.py": (
        "Synthesis Report Engine",
        "Synthesizes Polarity Core (Ahamkara ⟷ Manas), 4-step Nakshatra scoring, Operational Axis, Macro Environment, and Planetary Prominence",
    ),
    "jyotish/report/significations_data.json": (
        "Synthesis Report Data",
        "Structured database of planetary and house significations, anatomical correlations, and psychological themes",
    ),
    "jyotish/report/significations_flowcharts.json": (
        "Synthesis Report Flowcharts",
        "Authentic flowchart triptych nodes and interactive dependency edges for deep visual synthesis",
    ),
    # Section 13: Scripture Databases & Native Management
    "jyotish/bphs_db.py": (
        "Scripture & Database",
        "Brihat Parashara Hora Shastra SQLite query layer providing textual shloka references for calculated yogas and avasthas",
    ),
    "jyotish/scripture_db.py": (
        "Scripture & Database",
        "Sanskrit scripture database query interface and translation mappings",
    ),
    "jyotish/native_manager.py": (
        "Data Management",
        "Native profile and birth data persistence manager handling chart storage and retrieval",
    ),
    # Section 14: PDF Exporter
    "jyotish/pdf_exporter.md": (
        "Report Generation Spec",
        "Architectural specification for publication-grade astrological PDF export (A3 Master Plan and A4 Dossier)",
    ),
    "jyotish/pdf_exporter.py": (
        "Report Generation Engine",
        "Publication-grade astrological PDF export engine rendering vector SVGs, diagnostic tables, and typography",
    ),
    # Frontend Architecture & Modular UI
    "templates/index.html": (
        "Frontend Layout Skeleton",
        "Clean HTML shell coordinating Split.js resizable workspace layout, modular partials, and hotkeys",
    ),
    "static/js/widget_registry.js": (
        "Frontend Architecture",
        "Pluggable Widget Registry managing dynamic widget registration and rendering lifecycle",
    ),
    "static/js/components/table_builder.js": (
        "Frontend Architecture",
        "Declarative DOM builder helpers for tables, status badges, and strength meters",
    ),
    "static/css/base.css": (
        "Frontend Styles",
        "Global resets, typography, input fields, and custom scrollbars",
    ),
    "static/css/pergamon-theme.css": (
        "Frontend Styles",
        "Authentic Pergamon warm parchment color palette tokens, highlights, and status badges",
    ),
    "static/css/layout-grid.css": (
        "Frontend Styles",
        "Split.js resizable gutters, 2x2/3x3 grid geometry, and toolbar controls",
    ),
    "static/css/widgets.css": (
        "Frontend Styles",
        "Shared table layout, sticky headers, strength progress bars, and SVG chart wrappers",
    ),
    "static/css/modals.css": (
        "Frontend Styles",
        "Draggable floating windows, modal overlays, and contextual dropdown menus",
    ),
    "templates/partials/top_toolbar.html": (
        "Frontend Partials",
        "Top navigation menubar, native chart dropdown, and quick action controls",
    ),
    "templates/partials/context_menu.html": (
        "Frontend Partials",
        "Right-click context menu for dynamic grid cell assignment",
    ),
    "templates/partials/widget_templates.html": (
        "Frontend Partials",
        "Unified registry assembling all modular HTML widget templates",
    ),
    "static/js/widgets/report_widget.js": (
        "Frontend Widget",
        "Interactive synthesis report desk controller with tabs, dynamic scoring, and cards",
    ),
    "templates/widget_templates/tmpl_report.html": (
        "Widget Templates",
        "HTML5 blueprint for the 4-tab astrological synthesis report",
    ),
    # Scripts
    "scripts/audit_shadbala.py": (
        "Developer Tooling",
        "CLI audit tool validating Shadbala calculations against reference matrices",
    ),
    "scripts/build_kb_json.py": (
        "Developer Tooling",
        "Compiles markdown knowledge base files into jyotish/knowledge_base.json",
    ),
    "scripts/build_bphs_database.py": (
        "Developer Tooling",
        "Builds SQLite scripture database from BPHS text sources",
    ),
    "scripts/build_all_databases.py": (
        "Developer Tooling",
        "Master orchestrator for building scripture and reference databases",
    ),
    "scripts/export_codebase.py": (
        "Developer Tooling",
        "High-density codebase aggregator with architecture manifest and size limits",
    ),
    "scripts/export_jyotish.py": (
        "Developer Tooling",
        "Dedicated Jyotish calculation engine exporter with pedagogical section sorting",
    ),
    "scripts/export_report_codebase.py": (
        "Developer Tooling",
        "Dedicated Astrological Synthesis Report subsystem aggregator",
    ),
    "scripts/export_commits.py": (
        "Developer Tooling",
        "Git commit history exporter",
    ),
    # Configuration baseline & test fixtures
    "source-material/software-setup/calculation_hierarchy.md": (
        "Configuration Baseline",
        "Precedence and dependency tree of all astrological calculations",
    ),
    "source-material/software-setup/ui_scaling_guidelines.md": (
        "Configuration Baseline",
        "UI layout and dynamic scaling guidelines",
    ),
    "source-material/software-setup/software-parameters/settings_documentation.md": (
        "Configuration Baseline",
        "Documented software parameters matching Ernst Wilhelm's Kala",
    ),
    "source-material/software-setup/sample-case/matrix_reading_guide.md": (
        "Ground Truth Baselines",
        "Guide for reading Kala baseline verification matrices",
    ),
    "source-material/software-setup/sample-case/angelina_jolie_baselines.json": (
        "Ground Truth Baselines",
        "Ground-truth test fixture for Angelina Jolie chart subvalues and drishti",
    ),
}


def get_file_metadata(rel_path: str):
    """
    Returns (Subsystem, Description) for any relative file path.
    Uses explicit registry first, then pattern rules.
    """
    if rel_path in FILE_METADATA_REGISTRY:
        return FILE_METADATA_REGISTRY[rel_path]

    # Pattern matching
    if rel_path.startswith("static/css/"):
        return ("Frontend Styles", "Modular stylesheet component (Pergamon tokens, layout, widgets, modals)")

    if rel_path.startswith("static/js/widgets/"):
        name = os.path.basename(rel_path).replace(".js", "").replace("_", " ").title()
        return ("Frontend Widget", f"Pluggable widget controller module for {name}")

    if rel_path.startswith("static/js/components/"):
        return ("Frontend Architecture", "Declarative UI component and table builder helpers")

    if rel_path.startswith("static/js/"):
        return ("Frontend Architecture", "Pluggable Widget Registry and core client state")

    if rel_path.startswith("templates/partials/modals/"):
        name = os.path.basename(rel_path).replace(".html", "").replace("_", " ").title()
        return ("Frontend Modals", f"Modular modal dialog partial for {name}")

    if rel_path.startswith("templates/partials/"):
        return ("Frontend Partials", "Modular Jinja2 interface partial (toolbars, menus, templates)")

    if rel_path.startswith("templates/widget_templates/"):
        name = os.path.basename(rel_path).replace("tmpl_", "").replace(".html", "").replace("_", " ").title()
        return ("Widget Templates", f"Reusable HTML widget template for {name}")

    if rel_path.startswith("source-material/software-setup/sample-case/angelina_jolie_") and rel_path.endswith(".csv"):
        name = os.path.basename(rel_path).replace("angelina_jolie_", "").replace(".csv", "").replace("_", " ")
        return ("Ground Truth Baselines", f"Kala software reference matrix for {name} (Angelina Jolie baseline chart)")

    if rel_path.startswith("documentations/adr/"):
        return ("Architecture Decisions", "Architecture Decision Record")

    if rel_path.startswith("tests/"):
        return ("Verification Suite", "Automated test suite component")

    if rel_path.startswith("jyotish/avasthas/"):
        return ("Core Math: Avasthas", "Planetary avastha calculation module")

    if rel_path.startswith("jyotish/shadbala/"):
        return ("Core Math: Shadbala", "Shadbala planetary strength module")

    if rel_path.startswith("jyotish/yogas/"):
        return ("Classical Yogas", "Classical yoga detection and analysis module")

    if rel_path.startswith("jyotish/planetary_evaluation/"):
        return ("Planetary Evaluation", "Planetary dignity archetype and vitality evaluation module")

    if rel_path.startswith("jyotish/nakshatras/"):
        return ("Nakshatras & Lore", "Equatorial sidereal nakshatra calculation and star lore module")

    if rel_path.startswith("jyotish/"):
        return ("Core Math Engine", "Jyotish calculation engine component")

    if rel_path.startswith("knowledge_base/"):
        return ("Astrological Reference", "Astrological reference documentation")

    if rel_path.startswith("scripts/"):
        return ("Developer Tooling", "Developer or audit script")

    if rel_path.startswith("documentations/"):
        return ("Architecture & Design", "Project architectural documentation")

    return ("General Codebase", "Project source file")


def is_frontend_file(rel_path: str) -> bool:
    if rel_path.startswith("static/data/"):
        return False
    if rel_path.startswith(("static/", "templates/")):
        return True
    if rel_path in ("screenshot.py", "Gemini.md", "README.md"):
        return True
    return False


def is_backend_file(rel_path: str) -> bool:
    if rel_path.startswith("jyotish/"):
        return True
    if rel_path in ("app.py", "run.py", "Gemini.md", "README.md"):
        return True
    if rel_path.startswith(("documentations/", "knowledge_base/", "source-material/")):
        return True
    # Tests are NOT included in backend production export
    return False


def is_report_file(rel_path: str) -> bool:
    if rel_path.startswith(("jyotish/report/", "jyotish/nakshatras/")):
        return True
    if rel_path in (
        "static/js/widgets/report_widget.js",
        "templates/widget_templates/tmpl_report.html",
        "templates/partials/context_menu.html",
        "templates/partials/top_toolbar.html",
        "templates/partials/widget_templates.html",
    ):
        return True
    return False


def collect_codebase_files(project_root: str, scope: str = "all", include_tests: bool = False):
    """
    Collects essential codebase files filtered by subsystem scope:
    - 'jyotish': Pure calculation engine (/jyotish/), sorted pedagogically across 14 chapters
    - 'report': Synthesis report engine, nakshatra lore, and report widget
    - 'frontend': UI templates, stylesheets, and widget controllers
    - 'backend': Jyotish engines + Flask app server and blueprints (tests excluded)
    - 'all': Unified application export (tests excluded unless include_tests=True)
    """
    if scope == "jyotish":
        jyotish_files = []
        for root, dirs, files in os.walk(os.path.join(project_root, "jyotish")):
            dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
            for file in sorted(files):
                if file in EXCLUDED_FILES or file.startswith(("codebase_export", "code_export", "commits_export")):
                    continue
                _, ext = os.path.splitext(file)
                ext_lower = ext.lower()
                if ext_lower in EXCLUDED_EXTENSIONS or ext_lower not in ALLOWED_EXTENSIONS:
                    continue
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, project_root)
                jyotish_files.append(rel_path)
        jyotish_files.sort(key=get_jyotish_sort_key)
        return jyotish_files

    if scope == "report":
        report_files = [
            # Core Report Engine
            "jyotish/report/__init__.py",
            "jyotish/report/report_engine.py",
            "jyotish/report/significations_data.json",
            "jyotish/report/significations_flowcharts.json",
            # Nakshatra Lore & Database
            "jyotish/nakshatras/__init__.py",
            "jyotish/nakshatras/lore.py",
            "jyotish/nakshatras/nakshatra_data.py",
            "jyotish/nakshatras/nakshatra_database.json",
            # Foundational Mathematical Dependencies
            "jyotish/relationships/relationships.py",
            "jyotish/relationships/relationships.md",
            "jyotish/sign_attributes.py",
            "jyotish/sign_attributes.md",
            # Frontend Interactive Desk & Layout
            "static/js/widgets/report_widget.js",
            "templates/widget_templates/tmpl_report.html",
            "templates/partials/context_menu.html",
            "templates/partials/top_toolbar.html",
            "templates/partials/widget_templates.html",
        ]
        return [f for f in report_files if os.path.exists(os.path.join(project_root, f))]

    files_to_export = []

    for root, dirs, files in os.walk(project_root):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]

        for file in sorted(files):
            if file in EXCLUDED_FILES or file.startswith(("codebase_export", "code_export", "commits_export")):
                continue
            if file.endswith((".min.js", ".min.css", "-lock.json")):
                continue

            _, ext = os.path.splitext(file)
            ext_lower = ext.lower()

            if ext_lower in EXCLUDED_EXTENSIONS:
                continue
            if ext_lower not in ALLOWED_EXTENSIONS:
                continue

            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, project_root)

            # Avoid root duplicate file
            if rel_path == "Shivapuri_Learning_Style_Analysis.md":
                continue

            # Exclude duplicate static data files (already in jyotish/report/)
            if rel_path.startswith("static/data/"):
                continue

            # Exclude tests by default from exports
            if not include_tests and rel_path.startswith("tests/"):
                continue

            # In source-material, strictly include relevant setup docs and test fixtures
            if "source-material" in rel_path:
                if not (
                    "software-setup" in rel_path
                    and (
                        ext_lower in {".md", ".csv"}
                        or file == "angelina_jolie_baselines.json"
                    )
                ):
                    continue

            # Scope filtering
            if scope == "frontend" and not is_frontend_file(rel_path):
                continue
            elif scope == "backend" and not is_backend_file(rel_path):
                continue

            files_to_export.append(rel_path)

    files_to_export.sort()
    return files_to_export


def generate_executive_header(manifest, project_root, scope: str = "all"):
    """
    Generates an executive architecture guide, system paradigm summary,
    and structured Table of Contents for AI evaluation, tailored to the chosen scope.
    """
    total_files = len(manifest)
    total_lines = sum(item["lines"] for item in manifest)
    total_bytes = sum(item["bytes"] for item in manifest)
    total_kb = total_bytes / 1024
    total_mb = total_bytes / (1024 * 1024)

    header = []
    scope_title = {
        "frontend": "FRONTEND CODEBASE EXPORT",
        "backend": "BACKEND CODEBASE EXPORT",
        "report": "REPORT CODEBASE EXPORT",
        "jyotish": "JYOTISH CALCULATION ENGINE EXPORT",
        "all": "CODEBASE EXPORT",
    }.get(scope, "CODEBASE EXPORT")

    header.append(f"# ASTRA PRECISION ASTROLOGICAL ENGINE - {scope_title}")
    header.append("=" * 80)
    header.append(f"SYSTEM ARCHITECTURE & MANIFEST (SCOPE: {scope.upper()})")
    header.append("Generated by: scripts/export_codebase.py")
    header.append(f"Total Files: {total_files} | Total Lines: {total_lines:,} | Size: {total_kb:.1f} KB ({total_mb:.2f} MB)")
    header.append("=" * 80)
    header.append("")

    if scope == "jyotish":
        header.append("## 1. Executive Summary & Astrological Paradigm")
        header.append("This export aggregates Astra's complete Jyotish calculation engine (/jyotish/).")
        header.append("It contains all core mathematical computation engines, twin markdown specifications,")
        header.append("astronomical coordinate algorithms, and scripture databases. Strictly implements Ernst Wilhelm's 'Kala' methodology:")
        header.append("- **Tropical Rasis (Signs)**: Used for all core planetary placements and harmonic Vargas (divisional charts).")
        header.append("- **Campanus House System**: Houses are computed by dividing the prime vertical into 30° equal segments, projected onto the ecliptic.")
        header.append("- **Sidereal Equatorial Nakshatras**: Nakshatras are equatorial and anchored to the Dhruva Galactic Center (Middle of Mula at 0° Sagittarius).")
        header.append("- **Swiss Ephemeris (`pyswisseph`) Base**: Pure astronomical calculation using True Node and high-precision planetary ephemerides. ZERO hard-coding.")
        header.append("- **The Twin Markdown Pattern**: Every core mathematical module in `jyotish/` is paired with an authoritative companion `.md` file containing mathematical formulas, algorithm steps, and classical BPHS Sanskrit shloka references.")
        header.append("")
        header.append("## 2. Calculation Subsystems Overview (14 Pedagogical Chapters)")
        header.append("1. **Core Astronomical Math & Orchestrator**: High-precision coordinates, Campanus cusps, planetary speeds, vargas, and SVG rendering.")
        header.append("2. **Planetary Relationships & Aspects (Maitri & Drishti)**: 5-fold friendship matrices (Panchadha Maitri) and classical Parashari aspect rays.")
        header.append("3. **Planetary & House Strengths (Shadbala & Bhava Bala)**: Complete 6-fold planetary strength calculation and 12-house strength assessment.")
        header.append("4. **Planetary Conditions & States (Avasthas)**: Baladi, Jagradadi, Deeptadi, Lajjitadi, Shayanadi, and quantitative operational matrices.")
        header.append("5. **Divisional Harmonic Strength (Vimshopaka Bala)**: 20-point divisional varga weighting (Shadvarga, Saptavarga, Dashavarga, Shodashavarga).")
        header.append("6. **Planetary Evaluation & Lagna Vitality**: 9-tier dignity archetypes, directional tilts, Neecha Bhanga, Graha Yuddha, and Ascendant life-force.")
        header.append("7. **Classical Yogas & Breakers**: Kendra/Trikona Raja Yogas, Dhana/Daridrya, Pancha Mahapurusha, Lunar/Solar, Viparita, and cancellation rules.")
        header.append("8. **Ashtakavarga Assessment**: Bhinnashtakavarga and Sarvashtakavarga 8-fold bindu distribution matrices.")
        header.append("9. **Equatorial Sidereal Nakshatras & Lore**: 27 Dhruva Nakshatras across 7 classical families (Tikshna, Ugra, Dhruva, Mridu, Laghu, Chara, Mishra).")
        header.append("10. **Vimshottari Dasha Progression**: 120-year planetary period progression and birth balance timeline.")
        header.append("11. **Karakas & Sign Attributes**: Jaimini Chara Karakas, Parashari Sthira Karakas, and Kalapurusha bodily governance.")
        header.append("12. **Astrological Synthesis Report Subsystem**: Polarity Core, 4-step Nakshatra scoring, Operational Axis, Macro Environmental balances, and Flowcharts.")
        header.append("13. **Scripture Databases & Native Management**: BPHS SQLite database, scripture translation tables, and chart storage.")
        header.append("14. **Publication-Grade PDF Exporter**: Publication-quality vector SVGs, A3 Master Plan, and A4 Dossier reporting.")
        header.append("")
    elif scope == "report":
        header.append("## 1. Executive Summary: Astrological Synthesis Report Subsystem")
        header.append("This export aggregates all files comprising Astra's Astrological Synthesis Report desk,")
        header.append("synthesizing Tropical Signs, Campanus Houses, and Sidereal Dhruva Nakshatras into an interactive cockpit:")
        header.append("- **Polarity Core (Ahaṃkāra ⟷ Manas)**: Evaluates creative tension between Lagna (outer identity)")
        header.append("  and Moon (inner emotional mind), computing elemental and guna harmonies.")
        header.append("- **Authoritative 4-Step Nakshatra Scoring Engine**: Filters unoccupied stars, weights Moon (8 pts),")
        header.append("  Lagna (4 pts), Sun (2 pts), Grahas (1 pt), plus aspectual multipliers on Moon (×8), Lagna (×4), Sun (×2).")
        header.append("  Classifies stars into 7 classical families (Tikshna, Ugra, Dhruva, Mridu, Laghu, Chara, Mishra).")
        header.append("- **Operational Axis (Rāśi Tree ⟷ Navāṁśa Fruit)**: Potential-to-fruition trajectory with Vargottama boost.")
        header.append("- **Macro Environmental Balances**: Elemental (Fire/Earth/Air/Water), Guna, and Doshic breakdowns.")
        header.append("- **Planetary Prominence & Dignity Leaderboard**: Identifies the #1 Chart Commander (Kārakādhipati).")
        header.append("- **Interactive Presentation Desk**: Fully modular HTML5 blueprint, 4 tabs, responsive layout,")
        header.append("  and right-click grid cell assignment.")
        header.append("")
    elif scope == "frontend":
        header.append("## 1. Executive Summary: Frontend & UI Presentation Layer")
        header.append("This export aggregates Astra's complete user interface and client-side presentation layer.")
        header.append("The frontend strictly adheres to the Frontend Architecture & Modularity Protocol (GEMINI.md):")
        header.append("- **Zero Monolith Policy**: templates/index.html serves purely as an HTML layout coordinator.")
        header.append("- **Pluggable Widget Registry (`static/js/widget_registry.js`)**: All views register lifecycle callbacks dynamically.")
        header.append("- **Declarative Table Builder (`static/js/components/table_builder.js`)**: Eliminates manual string concatenation.")
        header.append("- **Structured CSS Token System (`static/css/`)**: 5 theme files (base, pergamon-theme, layout-grid, widgets, modals).")
        header.append("- **Modular Jinja Partials (`templates/partials/`)**: Isolated toolbars, menus, and draggable modal dialogs.")
        header.append("- **Widget Blueprints (`templates/widget_templates/`)**: 21 reusable DOM blueprints.")
        header.append("- **On-Demand Lazy SVGs**: Consumes /api/chart/<native_id>/svg for dynamic vector charts.")
        header.append("")
    elif scope == "backend":
        header.append("## 1. Executive Summary & Astrological Paradigm")
        header.append("This export aggregates Astra's core mathematical computation engines, calculation specifications,")
        header.append("scripture databases, and REST API server. Strictly implements Ernst Wilhelm's 'Kala' methodology:")
        header.append("- **Tropical Rasis (Signs)**: Used for all core planetary placements and harmonic Vargas (divisional charts).")
        header.append("- **Campanus House System**: Houses are computed by dividing the prime vertical into 30° equal segments, projected onto the ecliptic.")
        header.append("- **Sidereal Equatorial Nakshatras**: Nakshatras are equatorial and anchored to the Dhruva Galactic Center (Middle of Mula at 0° Sagittarius).")
        header.append("- **Swiss Ephemeris (`pyswisseph`) Base**: Pure astronomical calculation using True Node and high-precision planetary ephemerides. ZERO hardcoded outputs.")
        header.append("- **The Twin Markdown Pattern**: Every mathematical module in `jyotish/` is paired with an authoritative companion `.md` file containing formulas, algorithms, and classical BPHS shloka references.")
        header.append("- **Flask REST API (`app.py`)**: Exposes chart calculation endpoints and on-demand lazy SVG generation.")
        header.append("")
    else:
        header.append("## 1. Executive Summary & Astrological Paradigm")
        header.append("Astra is a precision astrological calculation engine and interactive chart viewer")
        header.append("built in Python and JavaScript. It strictly implements Ernst Wilhelm's 'Kala' methodology:")
        header.append("- **Tropical Rasis (Signs)**: Used for all core planetary placements and harmonic Vargas (divisional charts).")
        header.append("- **Campanus House System**: Houses are computed by dividing the prime vertical into 30° equal segments, projected onto the ecliptic.")
        header.append("- **Sidereal Equatorial Nakshatras**: Nakshatras are equatorial and anchored to the Dhruva Galactic Center (Middle of Mula at 0° Sagittarius).")
        header.append("- **Swiss Ephemeris (`pyswisseph`) Base**: Pure astronomical calculation using True Node and high-precision planetary ephemerides. ZERO hardcoded outputs.")
        header.append("")
        header.append("## 2. Core Architectural Invariants")
        header.append("1. **The Twin Markdown Pattern**: Every core mathematical module in `jyotish/` is paired with an authoritative")
        header.append("   companion `.md` file containing mathematical formulas, algorithm steps, and classical BPHS Sanskrit shloka references.")
        header.append("2. **Zero Hard-Coding**: Values must NEVER be faked to pass tests. All outputs are dynamically derived.")
        header.append("3. **Decoupled Architecture**: Clear separation between core astronomical calculation (/jyotish/), Flask API (app.py), and modular frontend (static/ & templates/).")
        header.append("")
        header.append("## 3. Subsystem Architecture Map")
        header.append("- **`jyotish/` (Core Math Engine)**: Central calculation orchestrator (`generate_jyotish.py`), SVG chart generator (`draw_chart.py`), coordinate math (`calc_utils.py`), and BPHS scripture database querying (`bphs_db.py`).")
        header.append("- **`jyotish/shadbala/`**: Complete 6-fold planetary strength calculation (Sthana, Dig, Kala, Cheshta, Naisargika, Drik).")
        header.append("- **`jyotish/avasthas/`**: Comprehensive planetary states (Baladi, Jagradadi, Deeptadi, Lajjitadi, Shayanadi, and Quantitative matrices).")
        header.append("- **`app.py` & API**: Flask application server exposing calculation endpoints and on-demand lazy SVG generation (`/api/chart/<id>/svg`).")
        header.append("- **`static/css/` & `static/js/`**: Modular presentation layer featuring 5 Pergamon stylesheets, Pluggable Widget Registry (`widget_registry.js`), declarative table builders, and isolated widget modules.")
        header.append("- **`templates/`**: Decoupled layout skeleton (`index.html`), modular Jinja2 partials (`top_toolbar.html`, `context_menu.html`, `modals/`), and reusable DOM templates (`widget_templates/`).")
        header.append("- **`documentations/adr/`**: Architecture Decision Records (ADRs 001-008) explaining foundational technical choices.")
        header.append("- **`knowledge_base/`**: Curated astrological definitions and classical significations.")
        header.append("- **`source-material/software-setup/sample-case/`**: Ground-truth numerical baselines from Kala (Angelina Jolie benchmark).")
        header.append("")

    header.append("## 4. Codebase Table of Contents / File Manifest")
    if scope == "jyotish":
        header.append("| # | Chapter | Subsystem | Path | Lines | Size (KB) | Role & Description |")
        header.append("|---|---|---|---|---:|---:|---|")
        for i, item in enumerate(manifest, 1):
            rel = item["rel_path"]
            chapter = JYOTISH_FILE_SECTION_MAP.get(rel, "General Jyotish")
            subsystem = item["subsystem"]
            lines = item["lines"]
            size_kb = item["bytes"] / 1024
            desc = item["description"]
            header.append(f"| {i} | {chapter} | {subsystem} | `{rel}` | {lines} | {size_kb:.1f} | {desc} |")
    else:
        header.append("| # | Subsystem | Path | Lines | Size (KB) | Role & Description |")
        header.append("|---|---|---|---:|---:|---|")
        for i, item in enumerate(manifest, 1):
            rel = item["rel_path"]
            subsystem = item["subsystem"]
            lines = item["lines"]
            size_kb = item["bytes"] / 1024
            desc = item["description"]
            header.append(f"| {i} | {subsystem} | `{rel}` | {lines} | {size_kb:.1f} | {desc} |")

    header.append("")
    header.append("=" * 80)
    header.append("END OF MANIFEST - FILE CONTENTS FOLLOW BELOW")
    header.append("=" * 80)
    header.append("\n\n")

    return "\n".join(header)


def condense_index_html(content: str) -> str:
    """
    Condenses the 13,000+ line templates/index.html file for export budget compliance.
    Preserves page layout, navigation, templates, and script signatures.
    """
    content = re.sub(
        r'<style>.*?</style>',
        '<style>\n    /* [Astra UI CSS styling (Split.js multi-pane, grid cells, dark/light themes, widgets, tables, modals) condensed for export budget] */\n</style>',
        content,
        flags=re.DOTALL,
    )

    def repl_opts(m):
        opts = re.findall(r'<option.*?</option>', m.group(0), flags=re.DOTALL)
        if len(opts) > 3:
            return opts[0] + '\n            <!-- ... [' + str(len(opts)-2) + ' options condensed for export budget] ... -->\n' + opts[-1]
        return m.group(0)
    content = re.sub(r'(<option.*?</option>\s*){4,}', repl_opts, content, flags=re.DOTALL)

    def repl_modal(m):
        m_id = m.group(1)
        body = m.group(2)
        lines = [l for l in body.splitlines() if l.strip()]
        if len(lines) > 15:
            return f'<div class="modal-overlay" id="{m_id}">\n' + '\n'.join(lines[:6]) + f'\n    <!-- ... [{len(lines)-9} lines modal controls condensed for export budget] ... -->\n' + '\n'.join(lines[-3:]) + '\n</div>'
        return m.group(0)
    content = re.sub(r'<div class="modal-overlay[^"]*"\s+id="([^"]+)"[^>]*>(.*?)(?=\n\s*<!--\s*[A-Z]|\n\s*<div id="main-container")', repl_modal, content, flags=re.DOTALL)

    def repl_tmpl(m):
        tmpl_id = m.group(1)
        body = m.group(2)
        lines = [l for l in body.splitlines() if l.strip()]
        if len(lines) > 10:
            return f'<template id="{tmpl_id}">\n' + '\n'.join(lines[:4]) + f'\n    <!-- ... [{len(lines)-6} lines template markup condensed for export budget] ... -->\n' + '\n'.join(lines[-2:]) + '\n</template>'
        return m.group(0)
    content = re.sub(r'<template id="(.*?)">(.*?)</template>', repl_tmpl, content, flags=re.DOTALL)

    marker_start = '<script>\n        let allSavedNatives'
    idx_script = content.find(marker_start)
    if idx_script == -1:
        return content
    pre = content[:idx_script]
    post_marker = '<!-- Global Custom Tooltip Engine -->'
    idx_post = content.find(post_marker)
    if idx_post == -1:
        idx_post = len(content)
    js = content[idx_script:idx_post]
    post = content[idx_post:]

    lines = js.splitlines()
    out = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if (stripped.startswith('function ') or ' = function(' in stripped or ' = async function(' in stripped or stripped.startswith('async function ')) and '{' in line:
            func_sig = line
            out.append(line)
            brace_count = line.count('{') - line.count('}')
            func_lines = [line]
            i += 1
            while i < len(lines) and brace_count > 0:
                brace_count += lines[i].count('{') - lines[i].count('}')
                func_lines.append(lines[i])
                i += 1
            if len(func_lines) <= 3:
                out.extend(func_lines[1:])
            else:
                indent = ' ' * (len(func_sig) - len(stripped) + 4)
                out.append(f'{indent}// ... [{len(func_lines)-2} lines of DOM/rendering logic condensed for export budget; full implementation in repo] ...')
                out.append(func_lines[-1])
            continue
        out.append(line)
        i += 1

    dense = pre + '\n'.join(out) + '\n' + post
    dense_lines = [re.sub(r'\s+', ' ', l).strip() for l in dense.splitlines() if l.strip()]
    return '\n'.join(dense_lines)


def condense_javascript_widget(content: str) -> str:
    """
    Condenses multi-thousand line DOM generation in oversized JS widgets
    while strictly preserving module exports, widget registry calls, and function signatures.
    """
    lines = content.splitlines()
    out = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if (stripped.startswith('function ') or ' = function(' in stripped or ' = async function(' in stripped or stripped.startswith('async function ')) and '{' in line:
            func_sig = line
            out.append(line)
            brace_count = line.count('{') - line.count('}')
            func_lines = [line]
            i += 1
            while i < len(lines) and brace_count > 0:
                brace_count += lines[i].count('{') - lines[i].count('}')
                func_lines.append(lines[i])
                i += 1
            if len(func_lines) <= 6:
                out.extend(func_lines[1:])
            else:
                indent = ' ' * (len(func_sig) - len(stripped) + 4)
                out.append(f'{indent}// ... [{len(func_lines)-2} lines of DOM rendering logic condensed for export budget; full implementation in repo] ...')
                out.append(func_lines[-1])
            continue
        out.append(line)
        i += 1

    dense = '\n'.join(out)
    dense_lines = [re.sub(r'\s+', ' ', l).strip() for l in dense.splitlines() if l.strip()]
    return '\n'.join(dense_lines)


def get_file_export_content(rel_path: str, full_path: str) -> str:
    """Reads file content and applies high-density condensation for oversized UI templates."""
    try:
        with open(full_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        if rel_path == "templates/index.html":
            content = condense_index_html(content)
        elif rel_path in (
            "static/js/widgets/master_diagnostic.js",
            "static/js/widgets/report_widget.js",
        ):
            content = condense_javascript_widget(content)
        return content
    except Exception as e:
        return f"# Error reading file {rel_path}: {e}\n"


def export_codebase(
    output_file: str = None,
    max_size_mb: float = None,
    project_root: str = None,
    summary_only: bool = False,
    scope: str = "all",
    include_tests: bool = False,
):
    """
    Executes the codebase export for a specified scope:
    - 'all': unified application export (tests excluded by default)
    - 'jyotish': pure calculation engine (/jyotish/) sorted into 14 chapters
    - 'backend': Jyotish math + Flask REST API & blueprints
    - 'frontend': UI templates, stylesheets, and widget controllers
    - 'report': Astrological synthesis report subsystem
    - 'split': generates both frontend and backend exports in a single run
    """
    if project_root is None:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    if scope == "split":
        print("=" * 80)
        print("ASTRA CODEBASE EXPORT: SPLIT MODE (FRONTEND & BACKEND)")
        print("=" * 80)
        fe_out = DEFAULT_FRONTEND_OUTPUT_FILE if output_file is None else output_file.replace(".txt", "_frontend.txt")
        be_out = DEFAULT_BACKEND_OUTPUT_FILE if output_file is None else output_file.replace(".txt", "_backend.txt")
        fe_limit = DEFAULT_FRONTEND_MAX_SIZE_MB if max_size_mb is None else max_size_mb
        be_limit = DEFAULT_BACKEND_MAX_SIZE_MB if max_size_mb is None else max_size_mb

        fe_res = export_codebase(
            output_file=fe_out,
            max_size_mb=fe_limit,
            project_root=project_root,
            summary_only=summary_only,
            scope="frontend",
            include_tests=include_tests,
        )
        print("\n")
        be_res = export_codebase(
            output_file=be_out,
            max_size_mb=be_limit,
            project_root=project_root,
            summary_only=summary_only,
            scope="backend",
            include_tests=include_tests,
        )
        return {
            "frontend": fe_res,
            "backend": be_res,
            "files_count": fe_res["files_count"] + be_res["files_count"],
            "total_lines": fe_res["total_lines"] + be_res["total_lines"],
            "total_bytes": fe_res["total_bytes"] + be_res["total_bytes"],
        }

    # Set scope-specific defaults if output_file or max_size_mb not explicitly passed
    if output_file is None:
        if scope == "frontend":
            output_file = DEFAULT_FRONTEND_OUTPUT_FILE
        elif scope == "backend":
            output_file = DEFAULT_BACKEND_OUTPUT_FILE
        elif scope == "report":
            output_file = DEFAULT_REPORT_OUTPUT_FILE
        elif scope == "jyotish":
            output_file = DEFAULT_JYOTISH_OUTPUT_FILE
        else:
            output_file = DEFAULT_OUTPUT_FILE

    if max_size_mb is None:
        if scope == "frontend":
            max_size_mb = DEFAULT_FRONTEND_MAX_SIZE_MB
        elif scope == "backend":
            max_size_mb = DEFAULT_BACKEND_MAX_SIZE_MB
        elif scope == "report":
            max_size_mb = DEFAULT_REPORT_MAX_SIZE_MB
        elif scope == "jyotish":
            max_size_mb = DEFAULT_JYOTISH_MAX_SIZE_MB
        else:
            max_size_mb = DEFAULT_MAX_SIZE_MB

    if os.path.isabs(output_file):
        output_path = output_file
    else:
        output_path = os.path.join(project_root, output_file)

    rel_files = collect_codebase_files(project_root, scope=scope, include_tests=include_tests)

    manifest = []
    for rel in rel_files:
        full_path = os.path.join(project_root, rel)
        content = get_file_export_content(rel, full_path)
        size_bytes = len(content.encode("utf-8"))
        lines = len(content.splitlines())
        subsystem, desc = get_file_metadata(rel)

        manifest.append({
            "rel_path": rel,
            "full_path": full_path,
            "bytes": size_bytes,
            "lines": lines,
            "subsystem": subsystem,
            "description": desc,
            "content": content,
        })

    if summary_only:
        print(f"Astra Codebase Export Summary [Scope: {scope.upper()}] ({len(manifest)} files):")
        for item in manifest:
            print(f"[{item['subsystem']}] {item['rel_path']} ({item['lines']} lines, {item['bytes']/1024:.1f} KB)")
        tot_bytes = sum(item['bytes'] for item in manifest)
        print(f"\nEstimated pure file size: {tot_bytes / (1024*1024):.2f} MB")
        return {"files_count": len(manifest), "total_lines": sum(item["lines"] for item in manifest), "total_bytes": tot_bytes}

    header_text = generate_executive_header(manifest, project_root, scope=scope)

    last_section = None
    with open(output_path, "w", encoding="utf-8") as out:
        out.write(header_text)

        for item in manifest:
            rel = item["rel_path"]
            subsystem = item["subsystem"]
            lines = item["lines"]
            size_kb = item["bytes"] / 1024
            desc = item["description"]

            # Section header in jyotish scope
            if scope == "jyotish":
                sec_title = JYOTISH_FILE_SECTION_MAP.get(rel, "15. Additional Jyotish Modules")
                if sec_title != last_section:
                    last_section = sec_title
                    out.write("\n" + "#" * 80 + "\n")
                    out.write(f"### CHAPTER: {sec_title.upper()}\n")
                    out.write("#" * 80 + "\n\n")

            # File separator banner
            out.write("=" * 80 + "\n")
            out.write(f"FILE: {rel}\n")
            out.write(f"SUBSYSTEM: {subsystem}\n")
            out.write(f"LINES: {lines} | SIZE: {size_kb:.1f} KB\n")
            out.write(f"ROLE: {desc}\n")
            out.write("=" * 80 + "\n")

            out.write(item["content"])
            out.write("\n\n")

    final_size_bytes = os.path.getsize(output_path)
    final_size_mb = final_size_bytes / (1024 * 1024)
    max_bytes = max_size_mb * 1024 * 1024

    print(f"\nSuccessfully generated codebase export [{scope.upper()}]: {output_path}")
    print(f"Total files included: {len(manifest)}")
    print(f"Total lines: {sum(item['lines'] for item in manifest):,}")
    print(f"Total size: {final_size_mb:.2f} MB ({final_size_bytes:,} bytes)")
    print(f"Configured limit: {max_size_mb:.2f} MB ({int(max_bytes):,} bytes)")

    if final_size_bytes > max_bytes:
        raise ValueError(
            f"Export size {final_size_mb:.2f} MB exceeds maximum allowable threshold of {max_size_mb:.2f} MB! "
            f"Trim additional non-essential files or increase limit."
        )

    print(f"Size check PASSED: {final_size_mb:.2f} MB is within the {max_size_mb:.2f} MB budget.")

    return {
        "files_count": len(manifest),
        "total_lines": sum(item["lines"] for item in manifest),
        "total_bytes": final_size_bytes,
        "output_path": output_path,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Aggregate Astra codebase into AI-optimized export file(s) with scope selection."
    )
    parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="Target output file name (defaults: codebase_export.txt, codebase_export_frontend.txt, codebase_export_backend.txt, codebase_export_report.txt, codebase_export_jyotish.txt)",
    )
    parser.add_argument(
        "-m",
        "--max-size-mb",
        type=float,
        default=None,
        help="Maximum allowable output size in megabytes (defaults: 2.8 for all, 1.0 for frontend, 1.6 for backend, 0.5 for report, 2.0 for jyotish)",
    )
    parser.add_argument(
        "--scope",
        choices=["all", "frontend", "backend", "report", "jyotish", "split"],
        default="all",
        help="Subsystem scope to export: 'all' (unified), 'jyotish' (pure calculation engine), 'frontend' (UI/templates/styles), 'backend' (math/API/engines), 'report' (synthesis report), or 'split' (both files)",
    )
    parser.add_argument(
        "--split",
        action="store_true",
        help="Shorthand for --scope split: generates both frontend and backend exports in a single command",
    )
    parser.add_argument(
        "--include-tests",
        action="store_true",
        help="Include automated test suites in export (default: False)",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Print manifest summary without writing export file",
    )
    args = parser.parse_args()

    effective_scope = "split" if args.split else args.scope

    export_codebase(
        output_file=args.output,
        max_size_mb=args.max_size_mb,
        summary_only=args.summary,
        scope=effective_scope,
        include_tests=args.include_tests,
    )


if __name__ == "__main__":
    main()
