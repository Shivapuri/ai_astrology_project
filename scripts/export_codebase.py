#!/usr/bin/env python3
"""
scripts/export_codebase.py
==========================
Aggregates Astra's complete codebase into a single, high-density, structured text export
optimized for AI evaluation, architectural auditing, and pair-programming ingestion.

Features:
- Strict size enforcement (< 1.5 MB hard cap)
- Executive Architecture Guide & Data Flow Map for evaluating AIs
- Detailed Table of Contents / File Manifest with line counts, byte sizes, and subsystem roles
- Standardized machine-readable file delimiters with contextual metadata
- Complete inclusion of:
  * Core Jyotish mathematical engines & twin markdown specifications
  * Flask REST API, application server, and interactive HTML UI
  * Automated regression, math, API, and UI test suites
  * Architecture Decision Records (ADRs 001-008) and system blueprints
  * Astrological knowledge base references & Kala software verification baselines
- Intelligent exclusion of:
  * Binary formats (.pdf, .epub, .mp3, .png, etc.)
  * External book text dumps and raw audio transcripts
  * Duplicate files and peripheral third-party tools
"""

import os
import sys
import argparse

DEFAULT_OUTPUT_FILE = "codebase_export.txt"
DEFAULT_MAX_SIZE_MB = 1.5

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
    "angelina-jolie-pdfs",
    "knowledge_base",
}

EXCLUDED_FILES = {
    "codebase_export.txt",
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
    # Core engines
    "jyotish/generate_jyotish.py": (
        "Core Math Engine",
        "Central orchestrator computing tropical placements, harmonic vargas, Campanus cusps, dignities, and dashas",
    ),
    "jyotish/generate_jyotish.md": (
        "Core Math Spec",
        "Mathematical specification, Campanus house algorithm, and coordinate foundations",
    ),
    "jyotish/calc_utils.py": (
        "Core Math Engine",
        "High-precision coordinate transformation, angle normalizations, and cusp utilities",
    ),
    "jyotish/draw_chart.py": (
        "Chart Visualization",
        "SVG chart diagram generator (North/South Indian styles, glyphs, dynamic house sizing)",
    ),
    "jyotish/pdf_exporter.py": (
        "Report Generation",
        "Publication-grade astrological PDF export engine (A3 Master Plan and A4 Dossier with vector SVGs)",
    ),
    "jyotish/pdf_exporter.md": (
        "Architecture & Design",
        "Architectural specification for the publication-grade PDF exporter",
    ),
    "jyotish/scripture_db.py": (
        "Scripture & Database",
        "Sanskrit scripture database query interface and translation mappings",
    ),
    "jyotish/bphs_db.py": (
        "Scripture & Database",
        "Brihat Parashara Hora Shastra SQLite query layer",
    ),
    "jyotish/native_manager.py": (
        "Data Management",
        "Native profile and birth data persistence manager",
    ),
    "jyotish/jyotish_rules.txt": (
        "Core Math Spec",
        "Concise rule definitions for vargas, relationships, and karakas",
    ),
    "jyotish/knowledge_base.json": (
        "Astrological Reference",
        "Precompiled JSON database of planets, signs, houses, and nakshatras",
    ),
    "jyotish/GEMINI.md": (
        "AI Agent Guidelines",
        "Module-specific instructions for jyotish calculation engine",
    ),
    # Shadbala
    "jyotish/shadbala/__init__.py": (
        "Core Math: Shadbala",
        "Shadbala module initialization",
    ),
    "jyotish/shadbala/shadbala.py": (
        "Core Math: Shadbala",
        "Complete 6-fold planetary strength calculation (Sthana, Dig, Kala, Cheshta, Naisargika, Drik)",
    ),
    "jyotish/shadbala/shadbala.md": (
        "Core Math Spec",
        "Mathematical formulas and Sanskrit definitions for all Shadbala components",
    ),
    # Avasthas
    "jyotish/avasthas/__init__.py": (
        "Core Math: Avasthas",
        "Avasthas module initialization",
    ),
    "jyotish/avasthas/GEMINI.md": (
        "AI Agent Guidelines",
        "Module-specific guidelines for avastha implementations",
    ),
    "jyotish/avasthas/quantitative.py": (
        "Core Math: Avasthas",
        "Quantitative avasthas matrix calculations (Uccha, Dig, Cheshta, Subha, Ishta, Drishti Yuti, Veda)",
    ),
    "jyotish/avasthas/quantitative.md": (
        "Core Math Spec",
        "Mathematical specification for quantitative avasthas matrices and net modifiers",
    ),
    "jyotish/avasthas/bala.py": (
        "Core Math: Avasthas",
        "Baladi avasthas calculation (Infant, Youthful, Adolescent, Old, Dead)",
    ),
    "jyotish/avasthas/bala.md": (
        "Core Math Spec",
        "Mathematical rules and degree bands for Baladi avasthas",
    ),
    "jyotish/avasthas/jagrat.py": (
        "Core Math: Avasthas",
        "Jagradadi avasthas calculation (Awake, Dreaming, Sleeping)",
    ),
    "jyotish/avasthas/jagrat.md": (
        "Core Math Spec",
        "Rules linking dignities to Jagrat, Svapna, and Sushupti states",
    ),
    "jyotish/avasthas/deepti.py": (
        "Core Math: Avasthas",
        "Deeptadi avasthas calculation (9 dignities from Exalted to Debilitated)",
    ),
    "jyotish/avasthas/deepti.md": (
        "Core Math Spec",
        "Sanskrit definitions and rules for Deeptadi dignities",
    ),
    "jyotish/avasthas/lajjita.py": (
        "Core Math: Avasthas",
        "Lajjitadi avasthas calculation (Proud, Starved, Thirsty, Agitated, Ashamed, Delighted)",
    ),
    "jyotish/avasthas/lajjita.md": (
        "Core Math Spec",
        "Sanskrit definitions and planetary condition rules for Lajjitadi avasthas",
    ),
    "jyotish/avasthas/shayana.py": (
        "Core Math: Avasthas",
        "Shayanadi 12 avasthas calculation (Resting, Sitting, Eating, Pleasure, etc.)",
    ),
    "jyotish/avasthas/shayana.md": (
        "Core Math Spec",
        "Formulas and modifier calculations for Shayanadi avasthas",
    ),
    # Relationships & Aspects
    "jyotish/relationships/relationships.py": (
        "Core Math: Maitri",
        "Natural, temporary (tatkalika), and compound five-fold (panchadha maitri) relationships",
    ),
    "jyotish/relationships/relationships.md": (
        "Core Math Spec",
        "Mathematical matrix rules for planetary friendships",
    ),
    "jyotish/aspects/aspects.py": (
        "Core Math: Drishti",
        "Planetary and house aspect calculation engine according to classical Parashari rules",
    ),
    "jyotish/aspects/aspects.md": (
        "Core Math Spec",
        "Drishti computation formulas and degree-based aspect weights",
    ),
    # Sign Attributes & Kalapurusha
    "jyotish/sign_attributes.py": (
        "Core Math Engine",
        "Sign distributions (Elements, Mobility, Polarity, Varnas, Doshas, Rising) and Kalapurusha anatomy",
    ),
    "jyotish/sign_attributes.md": (
        "Core Math Spec",
        "Mathematical specification and classical definitions for sign attributes and anatomy",
    ),
    # Frontend UI
    "templates/index.html": (
        "Frontend UI",
        "Interactive web interface featuring Split.js resizable panes, SVG charts, tables, and hotkeys",
    ),
    # Tests
    "tests/__init__.py": (
        "Verification Suite",
        "Test package initialization",
    ),
    "tests/test_api.py": (
        "Verification Suite",
        "Flask REST API endpoint tests validating status codes and response schemas",
    ),
    "tests/test_math_engines.py": (
        "Verification Suite",
        "Regression tests verifying core vargas, lagna, and avasthas against reference charts",
    ),
    "tests/test_quantitative_avasthas.py": (
        "Verification Suite",
        "Regression tests verifying quantitative avasthas against Kala ground truth",
    ),
    "tests/test_quantitative_subvalues.py": (
        "Verification Suite",
        "Unit tests validating individual subvalues of quantitative avasthas",
    ),
    "tests/test_shadbala.py": (
        "Verification Suite",
        "Unit tests validating all 6 Shadbala strengths against benchmark calculations",
    ),
    "tests/test_dignities.py": (
        "Verification Suite",
        "Unit tests validating essential and temporal dignities",
    ),
    "tests/test_drishti.py": (
        "Verification Suite",
        "Unit tests validating planetary aspect rays and mutual drishti matrices",
    ),
    "tests/test_aspects.py": (
        "Verification Suite",
        "Unit tests validating planetary and special aspects",
    ),
    "tests/test_house_aspects.py": (
        "Verification Suite",
        "Unit tests validating Bhava Chalita and equal house aspects",
    ),
    "tests/test_svg_generation.py": (
        "Verification Suite",
        "Unit tests validating SVG chart structure, viewBox, and transparency",
    ),
    "tests/test_sign_attributes.py": (
        "Verification Suite",
        "Unit tests validating sign attributes, matrix distributions, and Kalapurusha anatomy",
    ),
    "tests/test_ui_e2e.py": (
        "Verification Suite",
        "Playwright end-to-end tests verifying UI layout, Split.js, tabs, and hotkeys",
    ),
    "tests/test_aspect_tables_ui.py": (
        "Verification Suite",
        "UI tests verifying aspect table rendering in frontend",
    ),
    "tests/test_shadbala_widget_ui.py": (
        "Verification Suite",
        "UI tests verifying Shadbala widget display and data binding",
    ),
    # Documentations
    "documentations/BLUEPRINT.md": (
        "Architecture & Design",
        "Comprehensive system architecture and technical roadmap",
    ),
    "documentations/HANDOFF.md": (
        "Architecture & Design",
        "Context handoff detailing recent mathematical refinements",
    ),
    "documentations/ASTRO_ENGINES_OVERVIEW.md": (
        "Architecture & Design",
        "Overview of astronomical and astrological computation engines",
    ),
    "documentations/reference_kala_software_system.md": (
        "Architecture & Design",
        "Detailed comparative analysis against Ernst Wilhelm's Kala software",
    ),
    "documentations/vargas_functioning.md": (
        "Architecture & Design",
        "Mathematical principles of harmonic varga divisions and deity rulers",
    ),
    "documentations/shadbala_audit_report.md": (
        "Architecture & Design",
        "Audit report on Shadbala calculations, deviations, and fixes",
    ),
    "documentations/avasthas.md": (
        "Architecture & Design",
        "Comprehensive overview of all avastha systems implemented in Astra",
    ),
    "documentations/avasthas_remaining_tasks.md": (
        "Architecture & Design",
        "Task list for remaining avastha enhancements",
    ),
    "documentations/Horoscope_Interpretation_Framework.md": (
        "Architecture & Design",
        "Framework for holistic horoscope interpretation based on calculated values",
    ),
    # ADRs
    "documentations/adr/001-house-system-campanus.md": (
        "Architecture Decisions",
        "ADR 001: Selection of Campanus house system",
    ),
    "documentations/adr/002-nakshatra-equatorial-sidereal.md": (
        "Architecture Decisions",
        "ADR 002: Equatorial sidereal nakshatras anchored to Dhruva Galactic Center",
    ),
    "documentations/adr/003-visual-chart-rendering-and-intercepted-signs.md": (
        "Architecture Decisions",
        "ADR 003: Visual chart rendering and intercepted signs",
    ),
    "documentations/adr/004-unified-engine-architecture.md": (
        "Architecture Decisions",
        "ADR 004: Unified engine architecture and deprecation of dual engines",
    ),
    "documentations/adr/005-vargas-functioning-and-calculations.md": (
        "Architecture Decisions",
        "ADR 005: Divisional charts (vargas) mathematical formulation",
    ),
    "documentations/adr/006-circular-chart-ui-and-text-alignment.md": (
        "Architecture Decisions",
        "ADR 006: Circular chart UI design and text alignment",
    ),
    "documentations/adr/007-temporary-friendship-rasi.md": (
        "Architecture Decisions",
        "ADR 007: Temporary friendship based on rasi placements",
    ),
    "documentations/adr/008-lajjitadi-natural-friendship.md": (
        "Architecture Decisions",
        "ADR 008: Lajjitadi avasthas using natural vs compound friendship",
    ),
    # Knowledge Base
    "knowledge_base/GEMINI.md": (
        "AI Agent Guidelines",
        "Guidelines for knowledge base maintenance",
    ),
    "knowledge_base/Graha_Sutras_Reference.md": (
        "Astrological Reference",
        "Classical planetary characteristics, deities, gunas, and significations",
    ),
    "knowledge_base/The_Twelve_Bhavas_Reference.md": (
        "Astrological Reference",
        "Significations, themes, and anatomical correlations for all 12 houses",
    ),
    "knowledge_base/The_Twelve_Rasis_Reference.md": (
        "Astrological Reference",
        "Detailed profiles of the 12 tropical zodiac signs",
    ),
    "knowledge_base/The_Twenty_Seven_Nakshatras_Reference.md": (
        "Astrological Reference",
        "Reference guide for the 27 Dhruva Galactic Center nakshatras",
    ),
    "knowledge_base/Simple_House_Explanation.md": (
        "Astrological Reference",
        "Introductory guide to house meanings and classifications",
    ),
    "knowledge_base/simple_calculations/avasthas_explained.md": (
        "Astrological Reference",
        "Calculation walk-through for Baladi, Jagradadi, and Deeptadi avasthas",
    ),
    "knowledge_base/simple_calculations/shayanadi_explained.md": (
        "Astrological Reference",
        "Calculation walk-through for Shayanadi avasthas",
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
    "scripts/build_full_epub.py": (
        "Developer Tooling",
        "Epub compilation utility",
    ),
    "scripts/generate_epub.py": (
        "Developer Tooling",
        "Epub builder script",
    ),
    "scripts/generate_first_house_pdf.py": (
        "Developer Tooling",
        "Publication-grade first house chart PDF report generator using Playwright",
    ),
    "scripts/generate_learning_style_pdf.py": (
        "Developer Tooling",
        "Publication-grade learning style chart PDF report generator using Playwright",
    ),
    "scripts/export_codebase.py": (
        "Developer Tooling",
        "High-density codebase aggregator with architecture manifest and size limits",
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

    if rel_path.startswith("jyotish/"):
        return ("Core Math Engine", "Jyotish calculation engine component")

    if rel_path.startswith("knowledge_base/"):
        return ("Astrological Reference", "Astrological reference documentation")

    if rel_path.startswith("scripts/"):
        return ("Developer Tooling", "Developer or audit script")

    if rel_path.startswith("documentations/"):
        return ("Architecture & Design", "Project architectural documentation")

    return ("General Codebase", "Project source file")


def collect_codebase_files(project_root: str):
    """
    Collects all essential codebase files while filtering out binaries, caches,
    raw books, transcripts, and duplicates.
    """
    files_to_export = []

    for root, dirs, files in os.walk(project_root):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]

        for file in sorted(files):
            if file in EXCLUDED_FILES:
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

            files_to_export.append(rel_path)

    files_to_export.sort()
    return files_to_export


def generate_executive_header(manifest, project_root):
    """
    Generates an executive architecture guide, system paradigm summary,
    and structured Table of Contents for AI evaluation.
    """
    total_files = len(manifest)
    total_lines = sum(item["lines"] for item in manifest)
    total_bytes = sum(item["bytes"] for item in manifest)
    total_kb = total_bytes / 1024
    total_mb = total_bytes / (1024 * 1024)

    header = []
    header.append("# ASTRA PRECISION ASTROLOGICAL ENGINE - CODEBASE EXPORT")
    header.append("=" * 80)
    header.append("SYSTEM ARCHITECTURE & CODEBASE MANIFEST")
    header.append("Generated by: scripts/export_codebase.py")
    header.append(f"Total Files: {total_files} | Total Lines: {total_lines:,} | Size: {total_kb:.1f} KB ({total_mb:.2f} MB)")
    header.append("=" * 80)
    header.append("")
    header.append("## 1. Executive Summary & Astrological Paradigm")
    header.append("Astra is a precision astrological calculation engine and interactive chart viewer")
    header.append("built in Python and JavaScript. It strictly implements Ernst Wilhelm's 'Kala' methodology:")
    header.append("- **Tropical Rasis (Signs)**: Used for all core planetary placements and harmonic Vargas (divisional charts).")
    header.append("- **Campanus House System**: Houses are computed by dividing the prime vertical into 30° equal segments,")
    header.append("  projected onto the ecliptic. Accurately handles intercepted signs and house shifts.")
    header.append("- **Sidereal Equatorial Nakshatras**: Nakshatras are equatorial and anchored to the Dhruva Galactic Center")
    header.append("  (Middle of Mula at 0° Sagittarius / Galactic Center).")
    header.append("- **Swiss Ephemeris (`pyswisseph`) Base**: Pure astronomical calculation using True Node and high-precision")
    header.append("  planetary ephemerides. Strictly ZERO hardcoded outputs.")
    header.append("")
    header.append("## 2. Core Architectural Invariants")
    header.append("1. **The Twin Markdown Pattern**: Every core mathematical module in `jyotish/` is paired with an authoritative")
    header.append("   companion `.md` file containing mathematical formulas, algorithm steps, and classical BPHS Sanskrit shloka references.")
    header.append("2. **Zero Hard-Coding**: Values must NEVER be faked to pass tests. All outputs are dynamically derived.")
    header.append("3. **Test-Driven Rigor**: Includes 13 automated test suites covering core math, avasthas, shadbala, drishti,")
    header.append("   dignities, API schemas, and SVG generation, validated against Kala ground-truth fixtures.")
    header.append("")
    header.append("## 3. Subsystem Architecture Map")
    header.append("- **`jyotish/` (Core Math Engine)**: Central calculation orchestrator (`generate_jyotish.py`), SVG chart generator")
    header.append("  (`draw_chart.py`), coordinate math (`calc_utils.py`), and BPHS scripture database querying (`bphs_db.py`).")
    header.append("- **`jyotish/shadbala/`**: Complete 6-fold planetary strength calculation (Sthana, Dig, Kala, Cheshta, Naisargika, Drik).")
    header.append("- **`jyotish/avasthas/`**: Comprehensive planetary states (Baladi, Jagradadi, Deeptadi, Lajjitadi, Shayanadi, and Quantitative matrices).")
    header.append("- **`jyotish/relationships/` & `jyotish/aspects/`**: Panchadha Maitri (five-fold friendship) and Parashari Drishti (aspect rays).")
    header.append("- **`app.py` & `templates/index.html`**: Flask REST API server and interactive single-page UI with Split.js and SVG rendering.")
    header.append("- **`tests/`**: Automated verification test suites matching Kala reference outputs.")
    header.append("- **`documentations/adr/`**: Architecture Decision Records (ADRs 001-008) explaining foundational technical choices.")
    header.append("- **`knowledge_base/`**: Curated astrological definitions and classical significations.")
    header.append("- **`source-material/software-setup/sample-case/`**: Ground-truth numerical baselines from Kala (Angelina Jolie benchmark).")
    header.append("")
    header.append("## 4. Codebase Table of Contents / File Manifest")
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


def export_codebase(
    output_file: str = DEFAULT_OUTPUT_FILE,
    max_size_mb: float = DEFAULT_MAX_SIZE_MB,
    project_root: str = None,
    summary_only: bool = False,
):
    """
    Executes the codebase export.
    Returns a dict with statistics: {files_count, total_lines, total_bytes, output_path}.
    """
    if project_root is None:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    output_path = os.path.join(project_root, output_file)
    rel_files = collect_codebase_files(project_root)

    manifest = []
    for rel in rel_files:
        full_path = os.path.join(project_root, rel)
        size_bytes = os.path.getsize(full_path)
        subsystem, desc = get_file_metadata(rel)
        try:
            with open(full_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            lines = len(content.splitlines())
        except Exception:
            lines = 0

        manifest.append({
            "rel_path": rel,
            "full_path": full_path,
            "bytes": size_bytes,
            "lines": lines,
            "subsystem": subsystem,
            "description": desc,
        })

    if summary_only:
        print(f"Astra Codebase Export Summary ({len(manifest)} files):")
        for item in manifest:
            print(f"[{item['subsystem']}] {item['rel_path']} ({item['lines']} lines, {item['bytes']/1024:.1f} KB)")
        tot_bytes = sum(item['bytes'] for item in manifest)
        print(f"\nEstimated pure file size: {tot_bytes / (1024*1024):.2f} MB")
        return {"files_count": len(manifest), "total_lines": sum(item["lines"] for item in manifest), "total_bytes": tot_bytes}

    header_text = generate_executive_header(manifest, project_root)

    with open(output_path, "w", encoding="utf-8") as out:
        out.write(header_text)

        for item in manifest:
            rel = item["rel_path"]
            subsystem = item["subsystem"]
            lines = item["lines"]
            size_kb = item["bytes"] / 1024
            desc = item["description"]

            # File separator banner
            out.write("=" * 80 + "\n")
            out.write(f"FILE: {rel}\n")
            out.write(f"SUBSYSTEM: {subsystem}\n")
            out.write(f"LINES: {lines} | SIZE: {size_kb:.1f} KB\n")
            out.write(f"ROLE: {desc}\n")
            out.write("=" * 80 + "\n")

            try:
                with open(item["full_path"], "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
                out.write(content)
            except Exception as e:
                out.write(f"# Error reading file {rel}: {e}\n")

            out.write("\n\n")

    final_size_bytes = os.path.getsize(output_path)
    final_size_mb = final_size_bytes / (1024 * 1024)
    max_bytes = max_size_mb * 1024 * 1024

    print(f"\nSuccessfully generated codebase export: {output_path}")
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
        description="Aggregate Astra codebase into a single AI-optimized export file under 1.5 MB."
    )
    parser.add_argument(
        "-o",
        "--output",
        default=DEFAULT_OUTPUT_FILE,
        help=f"Target output file name (default: {DEFAULT_OUTPUT_FILE})",
    )
    parser.add_argument(
        "-m",
        "--max-size-mb",
        type=float,
        default=DEFAULT_MAX_SIZE_MB,
        help=f"Maximum allowable output size in megabytes (default: {DEFAULT_MAX_SIZE_MB})",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Print manifest summary without writing export file",
    )
    args = parser.parse_args()

    export_codebase(
        output_file=args.output,
        max_size_mb=args.max_size_mb,
        summary_only=args.summary,
    )


if __name__ == "__main__":
    main()

