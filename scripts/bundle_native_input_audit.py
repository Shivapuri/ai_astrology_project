#!/usr/bin/env python3
"""
scripts/bundle_native_input_audit.py
====================================
Generates a comprehensive, self-contained audit text bundle of all code and
specifications concerning native birth details, coordinates, timezones,
persistence, and the foundational astronomical calculations in Astra.

Target Audience: External AI / Expert Human Auditor reviewing coordinate order,
timezone mathematics, date formatting, and Swiss Ephemeris integration.
"""

import os
import sys
import json
from datetime import datetime

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_FILE = os.path.join(ROOT_DIR, "bundle_native_details_and_calculations.txt")

AUDIT_FILES = [
    {
        "path": "templates/partials/modals/add_person_modal.html",
        "category": "1. FRONTEND USER INPUT FORM",
        "role": "HTML Modal interface where user enters Full Name, Date (DD/MM/YYYY), Time (HH:MM:SS), City/Place, Country, Decimal Latitude, Decimal Longitude, and Timezone (±HH:MM) with Auto-detect button."
    },
    {
        "path": "templates/partials/top_toolbar.html",
        "category": "1. FRONTEND USER INPUT FORM",
        "role": "Top navigation bar containing the native selection dropdown (#nativeSelect), edit button triggers, and active native status."
    },
    {
        "path": "static/js/ui/library_modal.js",
        "category": "2. FRONTEND LOGIC & GEOCODING",
        "role": "Manages modal state, GeoNames city/country lookups (loadCountries, loadCities), auto-detecting timezone via POST /api/timezone (detectTimezoneFromCoords, fetchTimezone), and canonical DD/MM/YYYY date formatting (formatToDDMMYYYY)."
    },
    {
        "path": "static/js/core/api.js",
        "category": "2. FRONTEND LOGIC & GEOCODING",
        "role": "Client-side API orchestration: saveNative() parses and validates form inputs, transmits JSON payloads to /api/add_native or /api/update_native; loadChart() requests chart calculation; renders formatted coordinate strings (e.g. 52.2030° N, 8.0448° E)."
    },
    {
        "path": "app.py",
        "category": "3. BACKEND SERVER API & DISPATCH",
        "role": "Flask web server. Houses /api/timezone (TimezoneFinder lat/lon lookup + pytz UTC offset), /api/add_native, /api/update_native, /api/countries, /api/cities, compute_chart_data() (parses date/time/tz string into numbers, handles time stepper offset_seconds, calls generate_kala_chart), and /api/chart/<native_id>."
    },
    {
        "path": "jyotish/native_manager.py",
        "category": "4. DATA STORAGE & PERSISTENCE",
        "role": "Core persistence engine for database/Charts.jsonl. Implements parse_date_to_parts() (handling DD/MM/YYYY, ISO, dots, slashes, and historical/astronomical BCE negative years), to_standard_date(), save_native(), update_native(), atomic file writes with file locking, and automatic backups."
    },
    {
        "path": "jyotish/generate_jyotish.py",
        "category": "5. ASTROLOGICAL ORCHESTRATION",
        "role": "Master Orchestrator entry point. Defines generate_kala_chart(name, year, month, day, hour, minute, second, latitude, longitude, timezone_offset, ...) and delegates execution to ChartPipeline."
    },
    {
        "path": "jyotish/generate_jyotish.md",
        "category": "5. ASTROLOGICAL ORCHESTRATION",
        "role": "Architectural documentation and mathematical blueprint companion for generate_jyotish.py and the Stage 1-6 pipeline."
    },
    {
        "path": "jyotish/pipeline.py",
        "category": "5. ASTROLOGICAL ORCHESTRATION",
        "role": "Directed Acyclic Graph (DAG) pipeline container. ChartPipeline receives birth inputs, initializes ChartBaseline (Stage 1), caches intermediate results, and serializes subject_info and astronomical positions to JSON."
    },
    {
        "path": "jyotish/baseline.py",
        "category": "6. FOUNDATIONAL ASTRONOMICAL CALCULATIONS (STAGE 1)",
        "role": "Immutable Stage 1 Coordinate Container. Computes Julian Day (swe.julday), converts Local to UTC Julian Day via timezone offset (jd_utc = jd_local - tz/24.0), calls swe.houses for Campanus cusps & Ascendant, calculates sunrise/sunset via swe.rise_trans with disc center, calculates planetary geocentric coordinates via swe.calc_ut, and computes ancient temporal lords at Yamakoti meridian."
    },
    {
        "path": "jyotish/baseline_math.py",
        "category": "6. FOUNDATIONAL ASTRONOMICAL CALCULATIONS (STAGE 1)",
        "role": "Pure mathematical utilities: ecliptic to equatorial 3D coordinate transformations (get_eq_from_ecl), solar crossing root finding for temporal lords (find_preceding_solar_crossing), and True Node interpolation."
    },
    {
        "path": "documentations/adr/001-house-system-campanus.md",
        "category": "7. ARCHITECTURAL DECISION RECORDS",
        "role": "ADR-001: Mandates the Campanus House System across the entire Astra engine as required by Ernst Wilhelm's Kala methodology."
    },
    {
        "path": "source-material/software-setup/calculation_hierarchy.md",
        "category": "7. ARCHITECTURAL DECISION RECORDS",
        "role": "Official calculation hierarchy and dependency graph establishing Core Astronomy (Level 1) as the strict prerequisite for all downstream Jyotish calculations."
    },
    {
        "path": "tests/test_basic_placements.py",
        "category": "8. REGRESSION & VERIFICATION TEST SUITE",
        "role": "Pytest verification of Angelina Jolie's chart coordinates against ground truth CSV exported directly from Ernst Wilhelm's Kala software."
    },
    {
        "path": "tests/test_stage1_baseline.py",
        "category": "8. REGRESSION & VERIFICATION TEST SUITE",
        "role": "Pytest verification of ChartBaseline pure astronomy: Julian day calculation, 3D declinations, Campanus cusps, and temporal lords."
    },
    {
        "path": "tests/test_api.py",
        "category": "8. REGRESSION & VERIFICATION TEST SUITE",
        "role": "Pytest verification of date standardization helpers, native CRUD endpoints, timezone handling, and chart API response schemas."
    },
    {
        "path": "tests/test_time_stepper.py",
        "category": "8. REGRESSION & VERIFICATION TEST SUITE",
        "role": "Pytest verification of sub-second time precision, offset_seconds date rollover across midnight, and stepper API responses."
    }
]

SAMPLE_CHARTS = [
    {
        "note": "Eastern Hemisphere, Modern Gregorian (Shivapuri): Lat +52.2030, Lon +8.0448, Tz +01:00",
        "raw": '{"v": 1, "id": "589fabff-bf49-405a-9372-6d9566bf6955", "name": "Shivapuri", "type": "radix", "male": true, "date": "10/11/1983", "time": "22:20:00", "tz": "+01:00", "place": "Georgsmarienhütte", "country": "DE", "lat": 52.20296, "lon": 8.0448, "category": "Personal"}'
    },
    {
        "note": "Western Hemisphere, Negative Lat/Lon/Tz (Angelina Jolie): Lat +34.0522, Lon -118.2437, Tz -07:00",
        "raw": '{"v": 1, "id": "e43b1234-5678-4321-abcd-ef0123456789", "name": "Angelina Jolie", "type": "radix", "male": false, "date": "04/06/1975", "time": "09:09:00", "tz": "-07:00", "place": "Los Angeles", "country": "US", "lat": 34.0522, "lon": -118.2437, "category": "Historical"}'
    },
    {
        "note": "Southern Hemisphere, Negative Latitude (Lakshman Puriji): Lat -46.183, Lon +168.867, Tz +12:00",
        "raw": '{"v": 1, "id": "0386cfb3-9eb1-4dc2-b7e8-466a01dfb00d", "name": "Lakshman (Australian Swami) Puriji", "type": "radix", "male": true, "date": "14/11/1952", "time": "09:30:00", "tz": "+12:00", "place": "Gore", "country": "NZ", "lat": -46.183, "lon": 168.867, "category": "Spiritual"}'
    },
    {
        "note": "Ancient Astronomical BCE Date (Shri Krishna): Date 28/08/-3255 (3256 BCE), Lat +27.4924, Lon +77.6737, Tz +05:30",
        "raw": '{"v": 1, "id": "8270c2da-98d0-4b39-89ac-a3f5a11ac2b0", "name": "Shri Krishna (Closest Alignment)", "type": "radix", "male": true, "date": "28/08/-3255", "time": "23:50:00", "tz": "+05:30", "place": "Mathura", "country": "IN", "lat": 27.4924, "lon": 77.6737, "category": "Spiritual"}'
    },
    {
        "note": "Julian Calendar Transition (Morinus): Date 23/02/1583, Lat +45.9833, Lon +4.7167, Tz +01:00",
        "raw": '{"v": 1, "id": "a0aab60d-d1c7-4f60-b098-7af7cdaee1ea", "name": "Morinus", "type": "radix", "male": true, "date": "23/02/1583", "time": "08:47:00", "tz": "+01:00", "place": "Villefranche-sur-Saone", "country": "FR", "lat": 45.983333, "lon": 4.716667, "category": "Historical"}'
    }
]


def generate_bundle():
    print(f"Bundling native detail pipeline files into {OUTPUT_FILE}...")
    
    buf = []
    
    # 1. Main Header
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    buf.append("=" * 80)
    buf.append("ASTRA: NATIVE BIRTH DETAILS & INITIAL CALCULATIONS AUDIT BUNDLE")
    buf.append(f"GENERATED: {now_str}")
    buf.append("METHODOLOGY: Ernst Wilhelm's Kala (Tropical Signs, Campanus Houses, Swiss Ephemeris)")
    buf.append("=" * 80)
    buf.append("")
    buf.append("AUDIT PURPOSE & EXECUTIVE DIRECTIVE FOR EVALUATING AI:")
    buf.append("-" * 80)
    buf.append("You are evaluating the complete, end-to-end data lifecycle of a native's birth details")
    buf.append("in the Astra astrology engine. Your primary mission is to verify that there are ZERO")
    buf.append("coordinate mix-ups, parameter order swaps, timezone calculation inversions, or date")
    buf.append("format ambiguities from user input in the browser to the first Swiss Ephemeris calculations.")
    buf.append("")
    buf.append("CRITICAL TECHNICAL AUDIT CHECKPOINTS TO VERIFY:")
    buf.append("1. GEOGRAPHIC COORDINATE CONVENTIONS (LATITUDE & LONGITUDE):")
    buf.append("   - Latitude: Decimal degrees, positive for North (+), negative for South (-).")
    buf.append("   - Longitude: Decimal degrees, positive for East (+), negative for West (-).")
    buf.append("   - Coordinate Order in External Libraries (POTENTIAL PITFALL CHECK):")
    buf.append("     * TimezoneFinder: tf.timezone_at(lng=lon, lat=lat) -> requires LONGITUDE first!")
    buf.append("     * Swiss Ephemeris swe.houses(jd_utc, lat, lon, b'C') -> requires LATITUDE first!")
    buf.append("     * Swiss Ephemeris swe.rise_trans(..., geopos=(lon, lat, alt)) -> requires LONGITUDE first!")
    buf.append("   - Verify whether every call site in app.py and baseline.py passes (lat, lon) or (lon, lat)")
    buf.append("     strictly according to each library's explicit signature.")
    buf.append("")
    buf.append("2. TIME & TIMEZONE CALCULATIONS:")
    buf.append("   - Timezone string representation: '±HH:MM' (e.g. '+05:30', '-07:00').")
    buf.append("   - Decimal conversion formula: sign * (hours + minutes / 60.0).")
    buf.append("   - UTC Julian Day conversion:")
    buf.append("     jd_utc = jd_local - (timezone_offset / 24.0)")
    buf.append("     Verify the sign: East of Greenwich (+offset) is ahead of UTC, so UTC is earlier.")
    buf.append("     Therefore, subtracting (offset / 24.0) from local Julian Day is mathematically correct.")
    buf.append("   - Timezone auto-detection: Checks date/time with pytz to determine active DST offset.")
    buf.append("")
    buf.append("3. DATE FORMAT & CALENDAR HANDLING:")
    buf.append("   - Canonical UI & persistence format: DD/MM/YYYY.")
    buf.append("   - Multi-format parser (parse_date_to_parts in jyotish/native_manager.py):")
    buf.append("     Handles DD/MM/YYYY, ISO (YYYY-MM-DD), dots (DD.MM.YYYY), and BCE dates.")
    buf.append("   - Astronomical BCE handling: 3256 BCE is stored as year -3255 (astronomical zero-year math).")
    buf.append("   - Gregorian Calendar transition cutoff: Before 1582-10-15 uses swe.JUL_CAL;")
    buf.append("     on or after 1582-10-15 uses swe.GREG_CAL.")
    buf.append("")
    buf.append("4. TIME STEPPER / CONTINUOUS PREVIEW MECHANICS:")
    buf.append("   - In app.py compute_chart_data(): Shifts local time by offset_seconds via")
    buf.append("     _gregorian_to_jd and _jd_to_gregorian to handle calendar day/month/year rollover.")
    buf.append("")
    buf.append("5. FIRST ASTRONOMICAL CALCULATIONS (STAGE 1 BASELINE):")
    buf.append("   - In jyotish/baseline.py ChartBaseline.astronomical_anchors:")
    buf.append("     * Campanus House Cusps & Ascendant (Lagna) via swe.houses(jd_utc, lat, lon, b'C').")
    buf.append("     * Sunrise / Sunset via swe.rise_trans with disc center (swe.BIT_DISC_CENTER).")
    buf.append("     * Planetary positions via swe.calc_ut(jd_utc, body, swe.FLG_SWIEPH | swe.FLG_SPEED).")
    buf.append("     * Ancient prime meridian at Yamakoti (165° 46' E) for temporal lords (Vara, Hora, Masa, Varsha).")
    buf.append("=" * 80)
    buf.append("")

    # 2. Table of Contents
    buf.append("TABLE OF CONTENTS")
    buf.append("-" * 80)
    
    toc_lines = []
    file_contents = []
    total_lines = 0
    total_bytes = 0

    # Add Sample Charts section to TOC
    toc_lines.append(f" 0. [SAMPLE DATABASE RECORDS] database/Charts.jsonl (5 reference records across 4 quadrants)")

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
            
            toc_lines.append(f"{idx:2d}. [{item['category']}] {rel_path} ({line_count:,} lines | {byte_size/1024:.1f} KB)")
            file_contents.append((idx, item, lines, line_count, byte_size))

    buf.extend(toc_lines)
    buf.append("-" * 80)
    buf.append(f"TOTAL: {len(AUDIT_FILES)} files | {total_lines:,} lines | {total_bytes/1024:.1f} KB ({total_bytes/(1024*1024):.2f} MB)")
    buf.append("=" * 80)
    buf.append("")

    # 3. Sample Database Records
    buf.append("=" * 80)
    buf.append("SECTION 0: SAMPLE DATABASE RECORDS (database/Charts.jsonl)")
    buf.append("ROLE: Real-world reference records showing schema across all geographical quadrants,")
    buf.append("      historical BCE dates, and calendar transitions.")
    buf.append("=" * 80)
    for sample in SAMPLE_CHARTS:
        buf.append(f"# {sample['note']}")
        buf.append(sample["raw"])
        buf.append("")
    buf.append("# END OF SECTION 0: SAMPLE DATABASE RECORDS")
    buf.append("=" * 80)
    buf.append("")

    # 4. Each file in order
    for idx, item, lines, line_count, byte_size in file_contents:
        rel_path = item["path"]
        buf.append("=" * 80)
        buf.append(f"SECTION {idx}: {rel_path}")
        buf.append(f"CATEGORY: {item['category']}")
        buf.append(f"SIZE: {line_count:,} lines | {byte_size/1024:.1f} KB")
        buf.append(f"ROLE & CONTEXT IN PIPELINE:")
        buf.append(f"  {item['role']}")
        buf.append("=" * 80)
        buf.append("")
        
        # File contents
        buf.extend(lines)
        buf.append("")
        buf.append(f"# [END OF FILE: {rel_path}]")
        buf.append("=" * 80)
        buf.append("")

    # Write output
    final_text = "\n".join(buf)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        out.write(final_text)

    out_size_kb = os.path.getsize(OUTPUT_FILE) / 1024
    out_lines = len(final_text.splitlines())
    print(f" Successfully generated audit bundle:")
    print(f"  Path: {OUTPUT_FILE}")
    print(f"  Lines: {out_lines:,}")
    print(f"  Size: {out_size_kb:.1f} KB ({out_size_kb/1024:.2f} MB)")


if __name__ == "__main__":
    generate_bundle()
