#!/usr/bin/env python3
"""
scripts/export_jyotish.py
=========================
Exports Astra's complete Jyotish calculation engine (/jyotish/) into a single,
high-density, beautifully structured and labeled text export file (`codebase_export_jyotish.txt`).

Features:
- Pure Calculation Engine: Focuses strictly on /jyotish/, excluding all frontend UI and tests.
- Pedagogical Section Sorting: Files are ordered into 14 distinct logical calculation chapters:
  1. Core Astronomical Math & Calculation Orchestrator
  2. Planetary Relationships & Aspects (Maitri & Drishti)
  3. Planetary & House Strengths (Shadbala & Bhava Bala)
  4. Planetary Conditions & States (Avasthas)
  5. Divisional Harmonic Strength (Vimshopaka Bala)
  6. Planetary Evaluation, Nine-Tier Archetypes & Lagna Vitality
  7. Classical Yogas & Breakers
  8. Ashtakavarga Assessment
  9. Equatorial Sidereal Nakshatras & Lore
  10. Vimshottari Dasha Progression
  11. Karakas & Sign Attributes
  12. Astrological Synthesis Report Subsystem
  13. Scripture Databases & Native Management
  14. Publication-Grade PDF Exporter
- Distinct Section Dividers & Table of Contents: Every section has bold demarcation banners and line/size counts.
- Strict Scriptural Integrity: Preserves full mathematical formulas, algorithms, and twin markdown proofs.

Usage:
    python scripts/export_jyotish.py
    python scripts/export_jyotish.py --summary
    python scripts/export_jyotish.py -o custom_jyotish_export.txt
"""

import os
import sys
import argparse

# Add project root to sys.path
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from scripts.export_codebase import (
    export_codebase,
    DEFAULT_JYOTISH_OUTPUT_FILE,
    DEFAULT_JYOTISH_MAX_SIZE_MB,
)


def main():
    parser = argparse.ArgumentParser(
        description="Export all Jyotish calculation engines and twin specifications, nicely sorted and labeled."
    )
    parser.add_argument(
        "-o",
        "--output",
        default=DEFAULT_JYOTISH_OUTPUT_FILE,
        help=f"Target output file name (default: {DEFAULT_JYOTISH_OUTPUT_FILE})",
    )
    parser.add_argument(
        "-m",
        "--max-size-mb",
        type=float,
        default=DEFAULT_JYOTISH_MAX_SIZE_MB,
        help=f"Maximum allowable output size in megabytes (default: {DEFAULT_JYOTISH_MAX_SIZE_MB} MB)",
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
        project_root=_PROJECT_ROOT,
        summary_only=args.summary,
        scope="jyotish",
    )


if __name__ == "__main__":
    main()
