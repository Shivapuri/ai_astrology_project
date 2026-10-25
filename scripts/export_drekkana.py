#!/usr/bin/env python3
"""
scripts/export_drekkana.py
==========================
Exports Astra's complete Drekkana (D3) Varga package into a single, high-density,
beautifully structured text export file (`codebase_export_drekkana.txt`).

Covers both dimensions needed to judge the Drekkana Varga:
1. Backend Calculation Engine:
   - Pure harmonic coordinate calculation (10° decans, trine sign mapping per BPHS)
   - Classical Whole Sign Houses (Rāśi Bhāva) anchored to the D3 Ascendant
   - Panchadha Maitri 5-fold compound dignities in D3
   - Graha & Rāśi Drishti aspect rays in D3
   - Avasthas & combustion/conjunction separation in D3
   - Sthana Bala: Drekkana Bala 15 Virūpas award based on gender & decanate
   - Saptavarga Bala contribution of D3
   - 20-point Vimshopaka Bala weights (Shadvarga, Saptavarga, Dashavarga, Shodashavarga)
   - The Three Master Anchors of Destiny (Lagna, Navamsha, Drekkana Lords - Phaladeepika 3.11)
   - Dynamic Vector SVG chart generation (North Indian diamond, South Indian box, Circular decan slices)

2. Frontend Presentation & Interactive Judgment UI:
   - Interactive Chart Viewport (varga selector, outer bi-wheel, house highlight bar)
   - Quick-Access Kala menu modal
   - Varga Dignities Matrix (Ṣaḍvarga and Ṣoḍaśavarga views)
   - Planetary Evaluation Cockpit (Drekkana Lord Worldly Courage card)
   - Master Diagnostic 9-Column Table (Drekkana Lord identification & coordinates)
   - Shadbala Table (Drekkana Bala Virūpas readout)
   - Vimshopaka Bala Widget (20-point gauge breakdown)

Usage:
    python scripts/export_drekkana.py
    python scripts/export_drekkana.py --summary
    python scripts/export_drekkana.py -o custom_drekkana_export.txt
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
    DEFAULT_DREKKANA_OUTPUT_FILE,
    DEFAULT_DREKKANA_MAX_SIZE_MB,
)


def main():
    parser = argparse.ArgumentParser(
        description="Export Astra Drekkana (D3) Varga calculation and presentation package into an AI-optimized file."
    )
    parser.add_argument(
        "-o",
        "--output",
        default=DEFAULT_DREKKANA_OUTPUT_FILE,
        help=f"Target output file name (default: {DEFAULT_DREKKANA_OUTPUT_FILE})",
    )
    parser.add_argument(
        "-m",
        "--max-size-mb",
        type=float,
        default=DEFAULT_DREKKANA_MAX_SIZE_MB,
        help=f"Maximum allowable output size in megabytes (default: {DEFAULT_DREKKANA_MAX_SIZE_MB} MB)",
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
        scope="drekkana",
    )


if __name__ == "__main__":
    main()
