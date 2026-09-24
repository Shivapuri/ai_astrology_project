#!/usr/bin/env python3
"""
scripts/export_report_codebase.py
=================================
Aggregates Astra's complete Astrological Synthesis Report subsystem into a single,
high-density, structured text export file (`codebase_export_report.txt`).

Includes:
- Complete Executive Architecture & Data Flow Guide for AI evaluation
- Core Calculation Engine: Polarity Core, 4-step Nakshatra scoring, Operational Axis,
  Macro Environment, and Planetary Prominence
- Nakshatra Database & Lore: All 27 Nakshatras across 7 classical families
- Interactive UI Desk: Modular HTML5 template, responsive CSS layout, and Widget controller
- Universal Integration: Grid right-click menu, Top Toolbar dropdown, and Template partials
- Regression Tests: Dedicated unit test suite and Playwright visual screenshot script

Usage:
    python scripts/export_report_codebase.py
    python scripts/export_report_codebase.py --summary
    python scripts/export_report_codebase.py -o custom_report_export.txt
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
    DEFAULT_REPORT_OUTPUT_FILE,
    DEFAULT_REPORT_MAX_SIZE_MB,
)


def main():
    parser = argparse.ArgumentParser(
        description="Aggregate Astra Astrological Synthesis Report codebase into an AI-optimized export."
    )
    parser.add_argument(
        "-o",
        "--output",
        default=DEFAULT_REPORT_OUTPUT_FILE,
        help=f"Target output file name (default: {DEFAULT_REPORT_OUTPUT_FILE})",
    )
    parser.add_argument(
        "-m",
        "--max-size-mb",
        type=float,
        default=DEFAULT_REPORT_MAX_SIZE_MB,
        help=f"Maximum allowable output size in megabytes (default: {DEFAULT_REPORT_MAX_SIZE_MB} MB)",
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
        scope="report",
    )


if __name__ == "__main__":
    main()
