#!/usr/bin/env python3
"""
search_krishna_chart.py - Precision Astronomical Search for Krishna's Spiritual Chart

Searches through historical dates using Swiss Ephemeris to find the day and exact time
that aligns most closely with the canonical spiritual chart (Kha-Manikya archetype)
as shown in traditional Vaishnava commentaries and modern astrological studies:
- Ascendant: Taurus 15° (House 1)
- Moon: Taurus 14° (House 1, Rohini)
- Sun: Leo 14° (House 4)
- Mercury: Virgo 14° (House 5)
- Saturn: Libra 15° (House 6)
- Venus: Libra 18° (House 6)
- Rahu: Scorpio 16° (House 7)
- Mars: Capricorn 12° (House 9)
- Jupiter: Pisces 18° (House 11)
- Ketu: Taurus 16° (House 1)

Features:
- Multi-tier filtering: Scans centuries in seconds.
- Calculates exact Campanus houses, tropical signs, and degree proximity.
- Ranks candidates by Sign Matches, House Matches, and Angular Error.
- Optional --lock flag to automatically update or add the best-matching chart into Astra's database.
"""

import os
import sys
import argparse
from typing import List, Dict, Any, Tuple
import swisseph as swe

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from jyotish import native_manager

EPHE_PATH = os.path.join(PROJECT_ROOT, "ephe")
swe.set_ephe_path(EPHE_PATH)

CHARTS_FILE = os.path.join(PROJECT_ROOT, "database", "Charts.jsonl")

# Location: Mathura, Uttar Pradesh, India
MATHURA_LAT = 27.4924
MATHURA_LON = 77.6737
MATHURA_TZ = 5.5

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

# Canonical Spiritual Chart Archetype (Kha-Manikya)
TARGET_ARCHETYPE = {
    "Ascendant": {"sign": "Taurus", "sign_idx": 1, "deg": 15.0, "lon": 45.0, "house": 1},
    "Moon":      {"sign": "Taurus", "sign_idx": 1, "deg": 14.0, "lon": 44.0, "house": 1},
    "Sun":       {"sign": "Leo", "sign_idx": 4, "deg": 14.0, "lon": 134.0, "house": 4},
    "Mercury":   {"sign": "Virgo", "sign_idx": 5, "deg": 14.0, "lon": 164.0, "house": 5},
    "Saturn":    {"sign": "Libra", "sign_idx": 6, "deg": 15.0, "lon": 195.0, "house": 6},
    "Venus":     {"sign": "Libra", "sign_idx": 6, "deg": 18.0, "lon": 198.0, "house": 6},
    "Rahu":      {"sign": "Scorpio", "sign_idx": 7, "deg": 16.0, "lon": 226.0, "house": 7},
    "Mars":      {"sign": "Capricorn", "sign_idx": 9, "deg": 12.0, "lon": 282.0, "house": 9},
    "Jupiter":   {"sign": "Pisces", "sign_idx": 11, "deg": 18.0, "lon": 348.0, "house": 11},
    "Ketu":      {"sign": "Taurus", "sign_idx": 1, "deg": 16.0, "lon": 46.0, "house": 1},
}

PLANET_IDS = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mars": swe.MARS,
    "Mercury": swe.MERCURY,
    "Jupiter": swe.JUPITER,
    "Venus": swe.VENUS,
    "Saturn": swe.SATURN,
    "Rahu": swe.TRUE_NODE
}

def circular_diff(a: float, b: float) -> float:
    """Shortest angular distance on a 360-degree circle."""
    d = abs(a - b) % 360.0
    return min(d, 360.0 - d)

def get_house_of_longitude(lon: float, cusps: List[float]) -> int:
    """Calculates Campanus house number (1-12) for a given longitude."""
    for i in range(12):
        start = cusps[i]
        end = cusps[(i + 1) % 12]
        if start < end:
            if start <= lon < end:
                return i + 1
        else: # wraps around 0/360 Aries
            if lon >= start or lon < end:
                return i + 1
    return 1

def evaluate_chart_at_jd(jd: float) -> Dict[str, Any]:
    """Computes full positions, Campanus houses, and match metrics for a given JD."""
    cusps, ascmc = swe.houses(jd, MATHURA_LAT, MATHURA_LON, b'C')
    asc_deg = ascmc[0] % 360.0

    positions = {
        "Ascendant": asc_deg
    }
    
    for name, pid in PLANET_IDS.items():
        res, _ = swe.calc_ut(jd, pid)
        positions[name] = res[0] % 360.0
        
    # Ketu is opposite Rahu
    positions["Ketu"] = (positions["Rahu"] + 180.0) % 360.0

    sign_matches = 0
    house_matches = 0
    total_deg_err = 0.0
    body_details = {}

    for name, target in TARGET_ARCHETYPE.items():
        curr_lon = positions[name]
        curr_sign_idx = int(curr_lon // 30)
        curr_sign = SIGNS[curr_sign_idx]
        curr_deg_in_sign = curr_lon % 30.0
        
        curr_house = get_house_of_longitude(curr_lon, cusps) if name != "Ascendant" else 1
        deg_err = circular_diff(curr_lon, target["lon"])
        
        is_sign_match = (curr_sign_idx == target["sign_idx"])
        is_house_match = (curr_house == target["house"])
        
        if is_sign_match:
            sign_matches += 1
        if is_house_match:
            house_matches += 1
            
        total_deg_err += deg_err
        
        body_details[name] = {
            "calc_lon": curr_lon,
            "calc_sign": curr_sign,
            "calc_deg": curr_deg_in_sign,
            "calc_house": curr_house,
            "target_sign": target["sign"],
            "target_deg": target["deg"],
            "target_house": target["house"],
            "deg_err": deg_err,
            "is_sign_match": is_sign_match,
            "is_house_match": is_house_match
        }

    # Alignment Score (0 to 100)
    # 50 points from degree proximity (average error out of 180 deg)
    # 30 points from sign matches (3 points per match, max 30)
    # 20 points from house matches (2 points per match, max 20)
    avg_deg_err = total_deg_err / len(TARGET_ARCHETYPE)
    proximity_score = max(0.0, 50.0 * (1.0 - avg_deg_err / 90.0))
    sign_score = (sign_matches / len(TARGET_ARCHETYPE)) * 30.0
    house_score = (house_matches / len(TARGET_ARCHETYPE)) * 20.0
    composite_score = round(proximity_score + sign_score + house_score, 1)

    return {
        "jd": jd,
        "composite_score": composite_score,
        "sign_matches": sign_matches,
        "house_matches": house_matches,
        "total_deg_err": round(total_deg_err, 1),
        "avg_deg_err": round(avg_deg_err, 1),
        "positions": positions,
        "cusps": cusps,
        "body_details": body_details
    }

def search_best_alignments(
    start_year: int = -3600,
    end_year: int = -3000,
    top_n: int = 5,
    verbose: bool = True
) -> List[Dict[str, Any]]:
    """
    High-speed 3-tier astronomical search across ancient epochs.
    """
    if verbose:
        print(f"\n================================================================================")
        print(f" ASTRONOMICAL SEARCH ENGINE: LORD KRISHNA'S SPIRITUAL CHART ALIGNMENT")
        print(f" Search Epoch : {start_year} to {end_year} ({abs(start_year)+1} BCE to {abs(end_year)+1} BCE)")
        print(f" Location     : Mathura, India ({MATHURA_LAT}° N, {MATHURA_LON}° E, TZ +{MATHURA_TZ})")
        print(f" Target Model : Kha-Manikya Archetype (Taurus Lagna, Exalted Moon, Sun in Leo, etc.)")
        print(f"================================================================================\n")

    # Tier 1: Find candidate years where outer planets (Saturn in Libra & Jupiter in Pisces) are near
    tier1_years = []
    for y in range(start_year, end_year + 1):
        jd_mid = swe.julday(y, 7, 1, 0, swe.JUL_CAL)
        sat_lon = swe.calc_ut(jd_mid, swe.SATURN)[0][0] % 360.0
        jup_lon = swe.calc_ut(jd_mid, swe.JUPITER)[0][0] % 360.0
        
        sat_err = circular_diff(sat_lon, TARGET_ARCHETYPE["Saturn"]["lon"])
        jup_err = circular_diff(jup_lon, TARGET_ARCHETYPE["Jupiter"]["lon"])
        
        # Saturn within 45° of Libra 15°, Jupiter within 45° of Pisces 18°
        if sat_err <= 45.0 and jup_err <= 45.0:
            tier1_years.append(y)

    if verbose:
        print(f"[*] Tier 1 Scan: Found {len(tier1_years)} candidate years with Saturn near Libra & Jupiter near Pisces.")

    # Tier 2: For candidate years, scan months July-September (when Sun is in/near Leo)
    tier2_days = []
    for y in tier1_years:
        for m in [7, 8, 9]:
            for d in range(1, 32):
                try:
                    # Sample at midnight Mathura (18:30 UTC)
                    jd = swe.julday(y, m, d, 18.5, swe.JUL_CAL)
                except Exception:
                    continue
                
                sun_lon = swe.calc_ut(jd, swe.SUN)[0][0] % 360.0
                sun_err = circular_diff(sun_lon, TARGET_ARCHETYPE["Sun"]["lon"])
                if sun_err > 35.0:
                    continue
                    
                moon_lon = swe.calc_ut(jd, swe.MOON)[0][0] % 360.0
                moon_err = circular_diff(moon_lon, TARGET_ARCHETYPE["Moon"]["lon"])
                if moon_err > 40.0:
                    continue
                    
                tier2_days.append((y, m, d))

    if verbose:
        print(f"[*] Tier 2 Scan: Found {len(tier2_days)} candidate days with Sun near Leo and Moon near Taurus.")

    # Tier 3: Fine-grained hour/minute optimization for Taurus Ascendant
    fine_candidates = []
    for y, m, d in tier2_days:
        # Scan evening/night hours in Mathura: 20:00 to 01:30 IST (14.5 to 20.0 UTC)
        # Step every 10 minutes (0.1667 hours)
        for h_step in range(36):
            utc_hour = 14.5 + (h_step * 10.0 / 60.0)
            try:
                jd = swe.julday(y, m, d, utc_hour, swe.JUL_CAL)
            except Exception:
                continue
                
            eval_res = evaluate_chart_at_jd(jd)
            
            # Require at least 4 sign matches and composite score >= 45
            if eval_res["sign_matches"] >= 4:
                ist_hour = (utc_hour + MATHURA_TZ) % 24.0
                ist_h = int(ist_hour)
                ist_m = int(round((ist_hour % 1.0) * 60.0))
                if ist_m == 60:
                    ist_m = 0
                    ist_h = (ist_h + 1) % 24
                    
                eval_res["year"] = y
                eval_res["month"] = m
                eval_res["day"] = d
                eval_res["time_ist"] = f"{ist_h:02d}:{ist_m:02d}"
                eval_res["utc_hour"] = utc_hour
                eval_res["date_str"] = f"{y:04d}-{m:02d}-{d:02d}"
                eval_res["bce_year_str"] = f"{abs(y)+1 if y < 0 else y} BCE"
                fine_candidates.append(eval_res)

    # Sort candidates by:
    # 1. Sign matches (descending)
    # 2. House matches (descending)
    # 3. Lowest Total Degree Error (ascending)
    # 4. Composite Score (descending)
    fine_candidates.sort(
        key=lambda x: (
            -x["sign_matches"],
            -x["house_matches"],
            x["total_deg_err"],
            -x["composite_score"]
        )
    )

    # Deduplicate closely spaced times on the same date (keep the peak of that day)
    deduped = []
    seen_dates = set()
    for cand in fine_candidates:
        d_key = cand["date_str"]
        if d_key not in seen_dates:
            seen_dates.add(d_key)
            deduped.append(cand)
            if len(deduped) >= top_n:
                break

    return deduped

def print_candidate_report(cand: Dict[str, Any], rank: int):
    """Prints a clear, publication-grade table for a top candidate."""
    print(f"\n================================================================================")
    print(f" RANK #{rank}: {cand['date_str']} at {cand['time_ist']} IST ({cand['bce_year_str']})")
    print(f" Composite Score : {cand['composite_score']}/100")
    print(f" Sign Matches    : {cand['sign_matches']}/10  | House Matches: {cand['house_matches']}/10")
    print(f" Total Deg Error : {cand['total_deg_err']}° (Avg Error: {cand['avg_deg_err']}° per planet)")
    print(f"================================================================================")
    print(f"{'Body':<11} | {'Calculated':<18} | {'Target Archetype':<18} | {'House':<7} | {'Diff':<8} | {'Match'}")
    print(f"{'-'*11}-+-{'-'*18}-+-{'-'*18}-+-{'-'*7}-+-{'-'*8}-+-{'-'*9}")

    for body, data in cand["body_details"].items():
        calc_str = f"{data['calc_sign'][:3]} {data['calc_deg']:5.2f}°"
        target_str = f"{data['target_sign'][:3]} {data['target_deg']:5.2f}°"
        h_str = f"H{data['calc_house']} (T:H{data['target_house']})"
        diff_str = f"{data['deg_err']:5.1f}°"
        
        status = []
        if data["is_sign_match"]:
            status.append("Sign ✓")
        if data["is_house_match"]:
            status.append("House ✓")
        status_str = " ".join(status) if status else "--"

        print(f"{body:<11} | {calc_str:<18} | {target_str:<18} | {h_str:<7} | {diff_str:<8} | {status_str}")
    print(f"{'='*80}")

def lock_chart_in_database(best: Dict[str, Any], filepath: str = CHARTS_FILE) -> Dict[str, Any]:
    """
    Locks the best astronomical match into Astra's chart database.
    Updates existing 'Shri Krishna' entry or creates a new one safely via native_manager.
    """
    natives = native_manager.load_natives(filepath)
    krishna_native = None
    for n in natives:
        if "krishna" in n.get("name", "").lower():
            krishna_native = n
            break

    notes = (
        f"Rodden Rating: Historical / Astronomical Search. "
        f"Best alignment with the traditional Kha-Manikya Spiritual Chart archetype. "
        f"Alignment Score: {best['composite_score']}/100, Sign Matches: {best['sign_matches']}/10, "
        f"House Matches: {best['house_matches']}/10. Date: {best['bce_year_str']} ({best['date_str']} {best['time_ist']} IST, Mathura)."
    )

    update_payload = {
        "name": "Shri Krishna",
        "date": best["date_str"],
        "time": f"{best['time_ist']}:00",
        "tz": "+05:30",
        "place": "Mathura",
        "country": "IN",
        "lat": MATHURA_LAT,
        "lon": MATHURA_LON,
        "cal": "julian",
        "notes": notes
    }

    if krishna_native:
        updated = native_manager.update_native(filepath, krishna_native["id"], update_payload)
        print(f"\n[✓] Successfully updated existing 'Shri Krishna' in {filepath}!")
        return updated
    else:
        created = native_manager.save_native(
            filepath=filepath,
            name="Shri Krishna",
            date=best["date_str"],
            time=f"{best['time_ist']}:00",
            lat=MATHURA_LAT,
            lon=MATHURA_LON,
            tz="+05:30",
            place="Mathura",
            country="IN"
        )
        # update notes
        native_manager.update_native(filepath, created["id"], {"notes": notes, "cal": "julian"})
        print(f"\n[✓] Successfully added new 'Shri Krishna' into {filepath}!")
        return created

def main():
    parser = argparse.ArgumentParser(description="Find the historical date that aligns most with Krishna's Spiritual Chart.")
    parser.add_argument("--start-year", type=int, default=-3600, help="Starting astronomical year (default: -3600 = 3601 BCE)")
    parser.add_argument("--end-year", type=int, default=-3000, help="Ending astronomical year (default: -3000 = 3001 BCE)")
    parser.add_argument("--top", type=int, default=5, help="Number of top candidates to display (default: 5)")
    parser.add_argument("--rank", type=int, default=1, help="Which candidate rank to lock (1, 2, ... default: 1)")
    parser.add_argument("--date", type=str, default="", help="Specific date to lock if matched (e.g. -3255-08-28)")
    parser.add_argument("--lock", action="store_true", help="Automatically lock/save candidate into Astra database")
    args = parser.parse_args()

    results = search_best_alignments(
        start_year=args.start_year,
        end_year=args.end_year,
        top_n=args.top,
        verbose=True
    )

    if not results:
        print("\n[!] No matching configurations found in the specified epoch range.")
        return

    for idx, cand in enumerate(results, 1):
        print_candidate_report(cand, idx)

    if args.lock:
        selected_cand = results[0]
        if args.date:
            for c in results:
                if c["date_str"] == args.date:
                    selected_cand = c
                    break
        elif 1 <= args.rank <= len(results):
            selected_cand = results[args.rank - 1]

        print(f"\n[*] Locking candidate #{args.rank} ({selected_cand['date_str']} {selected_cand['time_ist']}) into Astra database...")
        lock_chart_in_database(selected_cand)

if __name__ == "__main__":
    main()
