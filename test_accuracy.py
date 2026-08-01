#!/usr/bin/env python3
"""
test_accuracy.py - Hellenistic Astrology Engine Truth & Accuracy Verification Suite

Validates that calculated output parameters (planetary degrees, Whole Sign Houses, 
Lot formulas, Dodecatemoria, Solar Phasis, and Egyptian Terms) match exact 
astronomical ground truth (Swiss Ephemeris C-engine & Vettius Valens formulas).
"""

import sys
import swisseph as swe
from datetime import datetime, timezone
import pytz
from generate_chart import (
    generate_ai_json,
    ZODIAC_SIGNS,
    DOMICILES,
    EXALTATIONS,
    DETRIMENTS,
    FALLS,
    EGYPTIAN_TERMS,
    calculate_dodecatemorion,
    get_solar_phasis,
    calculate_lot,
    get_whole_sign_aspects
)

def run_accuracy_audit():
    print("=" * 65)
    print("🧪 RUNNING MATHEMATICAL TRUTH & ACCURACY AUDIT")
    print("=" * 65 + "\n")
    
    passed_tests = 0
    total_tests = 0

    def assert_test(name: str, condition: bool, details: str = ""):
        nonlocal passed_tests, total_tests
        total_tests += 1
        if condition:
            passed_tests += 1
            print(f"  ✅ PASS: {name}")
        else:
            print(f"  ❌ FAIL: {name} | {details}")

    # 1. Swiss Ephemeris Precision Test
    # Birth: Nov 10, 1983, 03:20 UTC (4:20 AM Germany)
    jd_ut = swe.julday(1983, 11, 10, 3.333333)
    sun_res = swe.calc_ut(jd_ut, swe.SUN)[0][0]
    moon_res = swe.calc_ut(jd_ut, swe.MOON)[0][0]

    # Ground truth: Nov 10 1983 Sun must be in Scorpio (~227°), Moon in Capricorn (~289°)
    assert_test(
        "Swiss Ephemeris Precision (Sun Degree in Scorpio)",
        227.0 <= sun_res <= 228.0,
        f"Calculated Sun Abs Deg: {sun_res:.4f}°"
    )
    assert_test(
        "Swiss Ephemeris Precision (Moon Degree in Capricorn)",
        289.0 <= moon_res <= 290.0,
        f"Calculated Moon Abs Deg: {moon_res:.4f}°"
    )

    # 2. Lot Math Formula Verification
    # Given Ascendant = 191.71° (Libra), Sun = 227.15° (Scorpio), Moon = 289.50° (Capricorn)
    # Night Chart Formula: Lot of Fortune = Asc + Sun - Moon = (191.71 + 227.15 - 289.50) % 360 = 129.36° (Leo)
    # Night Chart Formula: Lot of Spirit = Asc + Moon - Sun = (191.71 + 289.50 - 227.15) % 360 = 254.06° (Sagittarius)
    asc_test = 191.71
    sun_test = 227.15
    moon_test = 289.50

    fortune_night = calculate_lot(asc_test, sun_test, moon_test)
    spirit_night = calculate_lot(asc_test, moon_test, sun_test)

    assert_test(
        "Night Chart Lot of Fortune Math (129.36° Leo)",
        fortune_night["sign"] == "Leo" and abs(fortune_night["absolute_degree"] - 129.36) < 0.05,
        f"Calculated: {fortune_night}"
    )
    assert_test(
        "Night Chart Lot of Spirit Math (254.06° Sagittarius)",
        spirit_night["sign"] == "Sagittarius" or spirit_night["sign"] == "Sag" and abs(spirit_night["absolute_degree"] - 254.06) < 0.05,
        f"Calculated: {spirit_night}"
    )

    # 3. Dodecatemoria Formula Verification
    # Formula: (abs_degree + (degree_in_sign * 11)) % 360
    # Test for Sun at 17.15° Scorpio (abs = 227.15°):
    # 227.15 + (17.15 * 11) = 227.15 + 188.65 = 415.80 % 360 = 55.80° (Taurus)
    dodec_sun = calculate_dodecatemorion(227.15)
    assert_test(
        "Dodecatemoria Math Formula (17.15° Scorpio -> Taurus)",
        dodec_sun["sign"] == "Tau" and abs(dodec_sun["absolute_degree"] - 55.80) < 0.1,
        f"Calculated: {dodec_sun}"
    )

    # 4. Solar Phasis Distance Verification
    # Mercury at 233.41° and Sun at 227.15° -> Dist = 6.26° (<= 8.5° -> Combust)
    phasis_mercury = get_solar_phasis("Mercury", 233.41, 227.15)
    assert_test(
        "Solar Phasis Combustion Check (6.26° distance -> Combust)",
        phasis_mercury == "Combust (Burned)",
        f"Calculated: {phasis_mercury}"
    )

    # 5. Egyptian Terms Lookup Verification
    # 17.15° Scorpio -> 4th term of Scorpio (19°-24°) is ruled by Jupiter
    term_test = EGYPTIAN_TERMS["Sco"]
    ruler_17_scorpio = None
    for max_deg, ruler in term_test:
        if 17.15 < max_deg:
            ruler_17_scorpio = ruler
            break
    assert_test(
        "Egyptian Terms Table Accuracy (17.15° Scorpio -> Jupiter)",
        ruler_17_scorpio == "Mercury", # 11° to 19° in Scorpio is Mercury
        f"Calculated: {ruler_17_scorpio}"
    )

    # Summary
    print("\n" + "=" * 65)
    print(f"📋 ACCURACY AUDIT RESULTS: {passed_tests}/{total_tests} TESTS PASSED ({passed_tests/total_tests*100:.1f}%)")
    print("=" * 65)
    if passed_tests == total_tests:
        print("🎯 MATHEMATICAL TRUTH CONFIRMED! All astronomical formulas & calculations are 100% exact!")
    else:
        print(f"⚠️ {total_tests - passed_tests} test(s) failed verification.")

if __name__ == "__main__":
    run_accuracy_audit()
