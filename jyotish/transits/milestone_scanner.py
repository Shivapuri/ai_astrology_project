"""
Transit Milestone Scanner Engine for Astra (Kala Methodology)

Performs high-speed coarse-to-fine ephemeris scans across a date horizon
to precompute jumpable keyframes without manual day-by-day scrubbing:
1. NATAL_STATION (Tier 1 - Critical): Stambhana on or aspecting a natal point within 3°20' Navamsha orb.
2. EXACT_ASPECT (Tier 2 - High): Exact 0°00' Conjunction or Graha Drishti hit (Pass 1, 2, 3).
3. SKY_STATION (Tier 3 - Medium): Stationary Retrograde (SR) / Direct (SD) pivots in the sky.
4. SIGN_INGRESS (Tier 3 - Medium): Major slow planet crossing 0°00' into a new Tropical sign.

Strictly adheres to Hemisphere A (pure mathematical calculus; zero HTML, zero CSS).
"""

import math
from typing import Dict, Any, List, Optional, Tuple, Set
import swisseph as swe

SIGNS_LIST = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

SWE_PLANET_MAP = {
    "Mars": swe.MARS,
    "Mercury": swe.MERCURY,
    "Jupiter": swe.JUPITER,
    "Venus": swe.VENUS,
    "Saturn": swe.SATURN,
    "Sun": swe.SUN,
    "Moon": swe.MOON
}

STATION_PLANETS = ["Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
INGRESS_PLANETS = ["Saturn", "Jupiter", "Rahu", "Ketu", "Mars", "Sun", "Venus", "Mercury"]
EXACT_ASPECT_PLANETS = ["Mars", "Jupiter", "Saturn", "Rahu", "Ketu", "Sun", "Venus", "Mercury"]

PLANET_SYMBOLS = {
    "Sun": "☉", "Moon": "☽", "Mars": "♂", "Mercury": "☿",
    "Jupiter": "♃", "Venus": "♀", "Saturn": "♄", "Rahu": "☊", "Ketu": "☋"
}


def _get_planet_lon_and_speed(jd: float, p_name: str) -> Tuple[float, float]:
    """Returns (longitude_deg_0_360, daily_speed_deg_per_day) for a planet at Julian Day."""
    if p_name in ["Rahu", "Ketu"]:
        # True node for Kala methodology
        res = swe.calc_ut(jd, swe.TRUE_NODE)
        rahu_lon = res[0][0] % 360.0
        rahu_speed = res[0][3]
        if p_name == "Rahu":
            return rahu_lon, rahu_speed
        else:
            return (rahu_lon + 180.0) % 360.0, rahu_speed
    else:
        pid = SWE_PLANET_MAP.get(p_name, swe.MARS)
        res = swe.calc_ut(jd, pid)
        return res[0][0] % 360.0, res[0][3]


def _revjul_to_dict(jd: float, timezone_hours: float = 0.0) -> Dict[str, Any]:
    """
    Converts Julian Day (in UT) to localized date parts for UI jump and display,
    adding half a minute (0.5 / 1440.0) so Swiss Ephemeris natively handles all
    minute, hour, day, month, and leap-year rollovers without overflow bugs.
    """
    local_jd = jd + (timezone_hours / 24.0) + (0.5 / 1440.0)
    y, m, d, float_hour = swe.revjul(local_jd)
    hour = int(float_hour)
    minute = int((float_hour - hour) * 60.0)
    day = int(d)

    # Also record exact UTC timestamp
    utc_jd = jd + (0.5 / 1440.0)
    uy, um, ud, u_float_h = swe.revjul(utc_jd)
    u_hour = int(u_float_h)
    u_min = int((u_float_h - u_hour) * 60.0)

    tz_sign = "+" if timezone_hours >= 0 else "-"
    abs_tz = abs(timezone_hours)
    tz_h = int(abs_tz)
    tz_m = int(round((abs_tz - tz_h) * 60.0))
    tz_suffix = f"{tz_sign}{tz_h:02d}:{tz_m:02d}"

    return {
        "year": int(y),
        "month": int(m),
        "day": day,
        "hour": hour,
        "minute": minute,
        "timestamp_utc": f"{int(uy):04d}-{int(um):02d}-{int(ud):02d}T{u_hour:02d}:{u_min:02d}:00Z",
        "timestamp_local": f"{int(y):04d}-{int(m):02d}-{day:02d}T{hour:02d}:{minute:02d}:00{tz_suffix}",
        "formatted_date": f"{day:02d}/{int(m):02d}/{int(y):04d}",
        "jump_date": f"{int(y):04d}-{int(m):02d}-{day:02d}",
        "jump_time": f"{hour:02d}:{minute:02d}:00"
    }


def _get_candidate_aspects(planet: str) -> List[Tuple[str, float]]:
    """Returns nominal glance angles for a given planet."""
    aspects = [("Conjunction", 0.0), ("7th Opposition", 180.0)]
    if planet == "Mars":
        aspects.extend([("4th Aspect", 90.0), ("8th Aspect", 210.0)])
    elif planet in ["Jupiter", "Rahu", "Ketu"]:
        aspects.extend([("5th Trine Aspect", 120.0), ("9th Trine Aspect", 240.0)])
    elif planet in ["Sun", "Venus", "Mercury"]:
        aspects.extend([("5th Trine Glance", 120.0), ("9th Trine Glance", 240.0)])
    elif planet == "Saturn":
        aspects.extend([("3rd Aspect", 60.0), ("10th Aspect", 270.0)])
    return aspects


def scan_transit_milestones(
    natal_chart: Dict[str, Any],
    start_year: int,
    start_month: int,
    start_day: int,
    start_hour: int = 12,
    start_minute: int = 0,
    days_back: int = 90,
    days_forward: int = 270,
    transit_latitude: float = 51.5074,
    transit_longitude: float = -0.1278,
    transit_timezone: float = 0.0,
    nakshatra_system: str = "ERNST_DHRUVA",
    aspect_orb_degrees: float = 3.3333
) -> Dict[str, Any]:
    """
    Scans a configurable date window around the target transit date and identifies:
    - NATAL_STATION: Planetary stations within 3°20' of natal planets or Lagna
    - EXACT_ASPECT: 0°00' exact degree aspect hits tagged with retrograde loop passes
    - SKY_STATION: General planetary stations in the sky
    - SIGN_INGRESS: Slow planet sign ingress into 0°00' of a new Tropical sign
    """
    # 1. Extract Natal Targets (Grahas + Lagna)
    natal_d1 = natal_chart.get("vargas", {}).get("D1", {})
    natal_grahas = natal_d1.get("grahas", {})
    natal_lagna = natal_d1.get("lagna", {})

    natal_targets = {}
    for p_name, g in natal_grahas.items():
        natal_targets[p_name] = g.get("longitude", 0.0)
    if natal_lagna:
        natal_targets["Lagna"] = natal_lagna.get("longitude", 0.0)

    natal_lagna_sign = natal_lagna.get("sign", "Aries")
    natal_lagna_idx = SIGNS_LIST.index(natal_lagna_sign) if natal_lagna_sign in SIGNS_LIST else 0
    natal_moon_sign = natal_grahas.get("Moon", {}).get("sign", natal_lagna_sign)
    natal_moon_idx = SIGNS_LIST.index(natal_moon_sign) if natal_moon_sign in SIGNS_LIST else 0

    # 2. Time Window Definition
    anchor_jd = swe.julday(
        start_year,
        start_month,
        start_day,
        start_hour + start_minute / 60.0 - transit_timezone
    )
    scan_start_jd = anchor_jd - days_back
    scan_end_jd = anchor_jd + days_forward
    total_days = int(math.ceil(scan_end_jd - scan_start_jd))

    active_dasha_lords_cfg = set(natal_chart.get("active_dasha_lords", []))
    antardashas_timeline = natal_chart.get("vimshottari_dasha", {}).get("antardashas", [])

    def _get_active_lords_at_jd(event_jd: float) -> Set[str]:
        if active_dasha_lords_cfg:
            return active_dasha_lords_cfg
        if antardashas_timeline:
            for ad in antardashas_timeline:
                if ad.get("start_jd", 0.0) <= event_jd < ad.get("end_jd", 0.0):
                    res = set()
                    m = ad.get("mahadasha_lord")
                    a = ad.get("antardasha_lord")
                    if m: res.add(m)
                    if a: res.add(a)
                    return res
        return set()

    raw_milestones: List[Dict[str, Any]] = []

    # 3. Step Through Ephemeris in 1-Day Increments
    # Pre-sample longitudes and speeds for all bodies at d and d+1
    # Day 0 to total_days
    sample_grid: Dict[str, List[Tuple[float, float]]] = {
        p: [] for p in set(STATION_PLANETS + INGRESS_PLANETS + EXACT_ASPECT_PLANETS)
    }

    for day_i in range(total_days + 1):
        cur_jd = scan_start_jd + day_i
        for p_name in sample_grid.keys():
            lon, sp = _get_planet_lon_and_speed(cur_jd, p_name)
            sample_grid[p_name].append((lon, sp))

    # =========================================================================
    # A. PLANETARY STATIONS (SR / SD)
    # =========================================================================
    for p_name in STATION_PLANETS:
        data_series = sample_grid[p_name]
        for day_i in range(total_days):
            sp1 = data_series[day_i][1]
            sp2 = data_series[day_i + 1][1]

            # Detect sign change of speed (direction reversal)
            if sp1 * sp2 <= 0.0 and sp1 != sp2:
                # Bisection to refine the exact moment speed == 0.0
                jd_a = scan_start_jd + day_i
                jd_b = scan_start_jd + day_i + 1.0
                st_type = "SR" if sp1 > 0 else "SD"

                for _ in range(16):  # 16 iterations gives ~1.3 seconds precision
                    jd_mid = (jd_a + jd_b) / 2.0
                    _, sp_mid = _get_planet_lon_and_speed(jd_mid, p_name)
                    if sp1 * sp_mid <= 0.0:
                        jd_b = jd_mid
                    else:
                        jd_a = jd_mid

                station_jd = (jd_a + jd_b) / 2.0
                station_lon, _ = _get_planet_lon_and_speed(station_jd, p_name)

                # Find if within 3°20' Navamsha orb of any natal target
                best_aspect_target: Optional[str] = None
                best_aspect_type: Optional[str] = None
                best_aspect_orb = 999.0

                candidate_glances = _get_candidate_aspects(p_name)
                for n_target, n_lon in natal_targets.items():
                    diff = (n_lon - station_lon) % 360.0
                    for asp_name, nominal_ang in candidate_glances:
                        signed_err = (diff - nominal_ang + 180.0) % 360.0 - 180.0
                        err = abs(signed_err)
                        if err <= aspect_orb_degrees and err < best_aspect_orb:
                            best_aspect_orb = err
                            best_aspect_target = n_target
                            best_aspect_type = asp_name

                time_dict = _revjul_to_dict(station_jd, transit_timezone)
                s_idx = int(station_lon // 30) % 12
                deg_in_sign = station_lon % 30.0
                deg = int(math.floor(deg_in_sign))
                minute = int(round((deg_in_sign - deg) * 60.0))
                if minute >= 60:
                    deg += 1
                    minute = 0
                if deg >= 30:
                    deg = 0
                    s_idx = (s_idx + 1) % 12
                sign_name = SIGNS_LIST[s_idx]

                h_lagna = ((s_idx - natal_lagna_idx + 12) % 12) + 1
                h_moon = ((s_idx - natal_moon_idx + 12) % 12) + 1

                sym = PLANET_SYMBOLS.get(p_name, p_name[:2])

                active_lords = _get_active_lords_at_jd(station_jd)

                if best_aspect_target is not None:
                    # Tier 1: Station on Natal Point
                    desc = f"{sym} {p_name} {st_type} at {deg}°{minute:02d}' {sign_name} — {best_aspect_type} Natal {best_aspect_target} ({round(best_aspect_orb, 1)}° orb)"
                    is_dasha_synced = bool(active_lords and (p_name in active_lords or best_aspect_target in active_lords))
                    raw_milestones.append({
                        "jd": station_jd,
                        **time_dict,
                        "category": "NATAL_STATION",
                        "tier": 1,
                        "planet": p_name,
                        "is_macro_planet": p_name in ["Saturn", "Jupiter", "Rahu", "Ketu", "Mars"],
                        "is_dasha_synchronized": is_dasha_synced,
                        "station_type": st_type,
                        "sign": sign_name,
                        "degree": deg,
                        "minute_arc": minute,
                        "longitude": round(station_lon, 4),
                        "house_from_lagna": h_lagna,
                        "house_from_moon": h_moon,
                        "natal_target": best_aspect_target,
                        "aspect_type": best_aspect_type,
                        "orb_at_event": round(best_aspect_orb, 2),
                        "pass_number": None,
                        "total_passes": None,
                        "description": desc
                    })
                else:
                    # Tier 3: Sky Station
                    desc = f"{sym} {p_name} {st_type} at {deg}°{minute:02d}' {sign_name} (H{h_lagna} from Lagna, H{h_moon} from Moon)"
                    is_dasha_synced = bool(active_lords and p_name in active_lords)
                    raw_milestones.append({
                        "jd": station_jd,
                        **time_dict,
                        "category": "SKY_STATION",
                        "tier": 3,
                        "planet": p_name,
                        "is_macro_planet": p_name in ["Saturn", "Jupiter", "Rahu", "Ketu", "Mars"],
                        "is_dasha_synchronized": is_dasha_synced,
                        "station_type": st_type,
                        "sign": sign_name,
                        "degree": deg,
                        "minute_arc": minute,
                        "longitude": round(station_lon, 4),
                        "house_from_lagna": h_lagna,
                        "house_from_moon": h_moon,
                        "natal_target": None,
                        "aspect_type": None,
                        "orb_at_event": None,
                        "pass_number": None,
                        "total_passes": None,
                        "description": desc
                    })

    # =========================================================================
    # B. SIGN INGRESSES (Pravesha) FOR SLOW PLANETS
    # =========================================================================
    for p_name in INGRESS_PLANETS:
        data_series = sample_grid[p_name]
        for day_i in range(total_days):
            lon1 = data_series[day_i][0]
            lon2 = data_series[day_i + 1][0]
            sign1 = int(lon1 // 30) % 12
            sign2 = int(lon2 // 30) % 12

            if sign1 != sign2:
                # Sign boundary crossed
                jd_a = scan_start_jd + day_i
                jd_b = scan_start_jd + day_i + 1.0

                # Target boundary longitude
                target_boundary = (sign2 * 30.0) if ((sign2 - sign1) % 12 == 1) else (sign1 * 30.0)

                for _ in range(16):
                    jd_mid = (jd_a + jd_b) / 2.0
                    lon_mid, _ = _get_planet_lon_and_speed(jd_mid, p_name)
                    sign_mid = int(lon_mid // 30) % 12
                    if sign_mid == sign1:
                        jd_a = jd_mid
                    else:
                        jd_b = jd_mid

                ingress_jd = (jd_a + jd_b) / 2.0
                new_sign_idx = sign2
                new_sign_name = SIGNS_LIST[new_sign_idx]
                time_dict = _revjul_to_dict(ingress_jd, transit_timezone)

                h_lagna = ((new_sign_idx - natal_lagna_idx + 12) % 12) + 1
                h_moon = ((new_sign_idx - natal_moon_idx + 12) % 12) + 1
                sym = PLANET_SYMBOLS.get(p_name, p_name[:2])

                is_retro_ingress = ((sign1 - sign2) % 12 == 1)
                boundary_lon = (sign1 * 30.0) if is_retro_ingress else (sign2 * 30.0)
                deg_display = 29 if is_retro_ingress else 0
                min_display = 59 if is_retro_ingress else 0

                active_lords = _get_active_lords_at_jd(ingress_jd)
                is_dasha_synced = bool(active_lords and p_name in active_lords)
                desc = f"{sym} {p_name} Ingress {new_sign_name} (H{h_lagna} from Lagna, H{h_moon} from Moon)"
                raw_milestones.append({
                    "jd": ingress_jd,
                    **time_dict,
                    "category": "SIGN_INGRESS",
                    "tier": 3,
                    "planet": p_name,
                    "is_macro_planet": p_name in ["Saturn", "Jupiter", "Rahu", "Ketu", "Mars"],
                    "is_dasha_synchronized": is_dasha_synced,
                    "station_type": None,
                    "sign": new_sign_name,
                    "degree": deg_display,
                    "minute_arc": min_display,
                    "longitude": float(boundary_lon % 360.0),
                    "house_from_lagna": h_lagna,
                    "house_from_moon": h_moon,
                    "natal_target": None,
                    "aspect_type": "Ingress",
                    "orb_at_event": 0.0,
                    "pass_number": None,
                    "total_passes": None,
                    "description": desc
                })

    # =========================================================================
    # C. EXACT 0°00' ASPECT HITS & RETROGRADE LOOPS
    # =========================================================================
    exact_aspect_hits: List[Dict[str, Any]] = []

    for p_name in EXACT_ASPECT_PLANETS:
        candidate_glances = _get_candidate_aspects(p_name)
        data_series = sample_grid[p_name]

        for n_target, n_lon in natal_targets.items():
            for asp_name, nominal_ang in candidate_glances:
                # Target exact longitude that triggers this aspect
                target_transit_lon = (n_lon - nominal_ang) % 360.0

                for day_i in range(total_days):
                    l1 = data_series[day_i][0]
                    l2 = data_series[day_i + 1][0]

                    # Signed shortest difference to the target longitude
                    d1 = (l1 - target_transit_lon + 180.0) % 360.0 - 180.0
                    d2 = (l2 - target_transit_lon + 180.0) % 360.0 - 180.0

                    # Check for zero crossing without wrapping across 180 deg
                    if d1 * d2 <= 0.0 and abs(d1) < 15.0 and abs(d2) < 15.0 and d1 != d2:
                        jd_a = scan_start_jd + day_i
                        jd_b = scan_start_jd + day_i + 1.0

                        for _ in range(16):
                            jd_mid = (jd_a + jd_b) / 2.0
                            lon_mid, _ = _get_planet_lon_and_speed(jd_mid, p_name)
                            d_mid = (lon_mid - target_transit_lon + 180.0) % 360.0 - 180.0
                            if d1 * d_mid <= 0.0:
                                jd_b = jd_mid
                            else:
                                jd_a = jd_mid

                        hit_jd = (jd_a + jd_b) / 2.0
                        hit_lon, hit_sp = _get_planet_lon_and_speed(hit_jd, p_name)

                        s_idx = int(hit_lon // 30) % 12
                        deg_in_sign = hit_lon % 30.0
                        deg = int(math.floor(deg_in_sign))
                        minute = int(round((deg_in_sign - deg) * 60.0))
                        if minute >= 60:
                            deg += 1
                            minute = 0
                        if deg >= 30:
                            deg = 0
                            s_idx = (s_idx + 1) % 12
                        sign_name = SIGNS_LIST[s_idx]

                        h_lagna = ((s_idx - natal_lagna_idx + 12) % 12) + 1
                        h_moon = ((s_idx - natal_moon_idx + 12) % 12) + 1

                        time_dict = _revjul_to_dict(hit_jd, transit_timezone)
                        is_retro = (hit_sp < 0)

                        active_lords = _get_active_lords_at_jd(hit_jd)
                        is_dasha_synced = bool(active_lords and (p_name in active_lords or n_target in active_lords))

                        exact_aspect_hits.append({
                            "jd": hit_jd,
                            **time_dict,
                            "category": "EXACT_ASPECT",
                            "tier": 2,
                            "planet": p_name,
                            "is_dasha_synchronized": is_dasha_synced,
                            "station_type": None,
                            "is_retrograde_at_hit": is_retro,
                            "sign": sign_name,
                            "degree": deg,
                            "minute_arc": minute,
                            "longitude": round(hit_lon, 4),
                            "house_from_lagna": h_lagna,
                            "house_from_moon": h_moon,
                            "natal_target": n_target,
                            "aspect_type": asp_name,
                            "orb_at_event": 0.0,
                            "group_key": (p_name, n_target, asp_name)
                        })

    # Group exact hits to determine pass numbers (Pass 1, Pass 2, Pass 3)
    exact_aspect_hits.sort(key=lambda x: x["jd"])
    groups: Dict[Tuple[str, str, str, int], List[Dict[str, Any]]] = {}

    # Separate hits occurring in distinct annual orbits (> 150 days apart)
    last_hit_time: Dict[Tuple[str, str, str], float] = {}
    cluster_ids: Dict[Tuple[str, str, str], int] = {}

    for hit in exact_aspect_hits:
        base_k = hit["group_key"]
        prev_jd = last_hit_time.get(base_k)
        if prev_jd is None or (hit["jd"] - prev_jd) > 150.0:
            cluster_ids[base_k] = cluster_ids.get(base_k, 0) + 1
        last_hit_time[base_k] = hit["jd"]
        k = (base_k[0], base_k[1], base_k[2], cluster_ids[base_k])
        groups.setdefault(k, []).append(hit)

    for k, hit_list in groups.items():
        total_p = len(hit_list)
        p_name = hit_list[0]["planet"]
        has_retro = any(h.get("is_retrograde_at_hit", False) for h in hit_list)
        first_is_retro = hit_list[0].get("is_retrograde_at_hit", False)

        # Standard retrograde loop across a degree consists of 3 passes (Direct, Retro, Direct)
        if has_retro and p_name in STATION_PLANETS:
            if first_is_retro:
                offset = 1  # Truncated window: Pass 1 occurred prior to scan_start_jd
                adj_total = max(total_p + offset, 3)
            else:
                offset = 0
                adj_total = max(total_p, 3)
        else:
            offset = 0
            adj_total = total_p

        for idx, hit in enumerate(hit_list):
            pass_num = idx + 1 + offset
            hit["pass_number"] = pass_num
            hit["total_passes"] = adj_total
            hit["is_macro_planet"] = p_name in ["Saturn", "Jupiter", "Rahu", "Ketu", "Mars"]
            n_target = hit["natal_target"]
            asp_name = hit["aspect_type"]
            sym = PLANET_SYMBOLS.get(p_name, p_name[:2])
            pass_str = f" (Pass {pass_num}/{adj_total})" if adj_total > 1 else ""
            hit["description"] = f"{sym} {p_name} {asp_name} Natal {n_target} (0°00'){pass_str}"
            del hit["group_key"]
            if "is_retrograde_at_hit" in hit:
                del hit["is_retrograde_at_hit"]
            raw_milestones.append(hit)

    # =========================================================================
    # D. Deduplication and Chronological Assembly
    # =========================================================================
    raw_milestones.sort(key=lambda x: x["jd"])

    # Remove near-duplicate roots (events within 15 minutes of same planet & category)
    cleaned_milestones: List[Dict[str, Any]] = []
    seen_events = set()

    for m in raw_milestones:
        sig = (m["category"], m["planet"], m["year"], m["month"], m["day"], m["hour"], m["minute"] // 15)
        if sig in seen_events:
            continue
        seen_events.add(sig)
        cleaned_milestones.append(m)

    # Compile upcoming stations for outer rim SVG pins
    upcoming_stations: List[Dict[str, Any]] = []
    seen_station_keys = set()

    for m in cleaned_milestones:
        if m["category"] in ["NATAL_STATION", "SKY_STATION"] and m["jd"] >= (anchor_jd - 0.5):
            st_key = (m["planet"], m["station_type"], m["sign"], m["degree"])
            if st_key not in seen_station_keys:
                seen_station_keys.add(st_key)
                sym = PLANET_SYMBOLS.get(m["planet"], m["planet"][:2])
                upcoming_stations.append({
                    "jd": m["jd"],
                    "planet": m["planet"],
                    "is_dasha_synchronized": m.get("is_dasha_synchronized", False),
                    "station_type": m["station_type"],
                    "longitude": m["longitude"],
                    "sign": m["sign"],
                    "degree": m["degree"],
                    "minute": m["minute_arc"],
                    "year": m["year"],
                    "month": m["month"],
                    "day": m["day"],
                    "hour": m["hour"],
                    "minute_arc": m["minute"],
                    "formatted_date": m["formatted_date"],
                    "tooltip": f"Upcoming {m['planet']} {m['station_type']} at {m['degree']}°{m['minute_arc']:02d}' {m['sign']} on {m['formatted_date']}",
                    "jump_date": m["jump_date"],
                    "jump_time": m["jump_time"]
                })

    return {
        "milestones": cleaned_milestones,
        "upcoming_stations": upcoming_stations,
        "scan_meta": {
            "start_year": start_year,
            "start_month": start_month,
            "start_day": start_day,
            "days_back": days_back,
            "days_forward": days_forward,
            "total_milestones": len(cleaned_milestones),
            "natal_lagna_sign": natal_lagna_sign,
            "natal_moon_sign": natal_moon_sign
        }
    }
