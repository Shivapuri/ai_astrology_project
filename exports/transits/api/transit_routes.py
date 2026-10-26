"""
Flask API Transit Endpoints (Extracted from app.py)
===================================================

This module illustrates how the transit calculus (Hemisphere A) and 
SVG Bi-Wheel generator (Level 8 Presentation) are exposed via REST API.

Endpoints:
1. GET /api/chart/<native_id>/transit
   - Computes real-time or user-selected transit snapshot.
   - Calculates planetary speeds, station states (SR/SD), and aspect intensity.
   - Triggers the 360-day milestone scanner (-90 to +270 days).
   - Generates and returns the Bi-Wheel SVG + JSON radar payload.

2. GET /api/chart/<native_id>/transit/milestones
   - Standalone milestone scanner endpoint with custom scanning horizons
     (days_back, days_forward).
"""

from datetime import datetime
import re
from flask import Blueprint, jsonify, request

transit_blueprint = Blueprint('transit_api', __name__)

# In-memory LRU or dictionary caches to prevent recalculating static natal charts
# and expensive ephemeris scans across consecutive date scrub requests.
_NATAL_CHART_CACHE = {}
_TRANSIT_MILESTONES_CACHE = {}

@transit_blueprint.route('/api/chart/<native_id>/transit')
def get_chart_transit(native_id):
    """
    Returns real-time or date-specific transit bi-wheel SVG and aspect data.
    """
    # 1. Retrieve natal profile
    # (Assuming native_manager.get_native_by_id)
    native = {"id": native_id} # mock or lookup
    if not native:
        return jsonify({"error": "Native not found"}), 404

    now = datetime.now()
    transit_date_str = request.args.get('transit_date')
    transit_time_str = request.args.get('transit_time')
    
    # Parse transit date and time safely
    if transit_date_str:
        try:
            nums = [int(n) for n in re.findall(r'\d+', str(transit_date_str))]
            if len(nums) >= 3:
                if nums[0] > 1000:
                    t_year, t_month, t_day = nums[0], nums[1], nums[2]
                else:
                    t_day, t_month, t_year = nums[0], nums[1], nums[2]
            else:
                t_year, t_month, t_day = now.year, now.month, now.day
        except Exception:
            t_year, t_month, t_day = now.year, now.month, now.day
    else:
        t_year, t_month, t_day = now.year, now.month, now.day

    if transit_time_str:
        try:
            t_nums = [int(n) for n in re.findall(r'\d+', str(transit_time_str))]
            t_hour = t_nums[0] if len(t_nums) > 0 else now.hour
            t_min = t_nums[1] if len(t_nums) > 1 else 0
            t_sec = t_nums[2] if len(t_nums) > 2 else 0
        except Exception:
            t_hour, t_min, t_sec = now.hour, now.minute, now.second
    else:
        t_hour, t_min, t_sec = now.hour, now.minute, now.second

    t_lat = request.args.get('lat', default=float(native.get('lat', 51.5074)), type=float)
    t_lon = request.args.get('lon', default=float(native.get('lon', -0.1278)), type=float)
    
    tz_str = str(request.args.get('tz', native.get('tz', '+00:00')))
    try:
        t_tz = float(tz_str)
    except ValueError:
        try:
            sign = -1 if tz_str.startswith('-') else 1
            tz_parts = tz_str.lstrip('+-').split(':')
            t_tz = sign * (float(tz_parts[0]) + float(tz_parts[1]) / 60.0)
        except Exception:
            t_tz = 0.0

    nakshatra_system = request.args.get('nakshatra_system', 'ERNST_DHRUVA')
    debilitation_mode = request.args.get('debilitation_mode', 'kala_degree')
    mode = request.args.get('mode', 'symbol')
    root = request.args.get('root', 'Lagna')
    show_nakshatras = request.args.get('show_nakshatras', 'false').lower() == 'true'
    aspect_orb_degrees = request.args.get('orb', default=3.3333, type=float)

    # 2. Compute or load cached Natal Baseline
    # (compute_chart_data calculates D1 and Divisional Vargas via Swiss Ephemeris)
    natal_chart = {} # compute_chart_data(...)

    # 3. Calculate Transits (Hemisphere A Pure Math)
    from jyotish.transits.transits import calculate_transits
    transit_res = calculate_transits(
        natal_chart=natal_chart,
        transit_year=t_year,
        transit_month=t_month,
        transit_day=t_day,
        transit_hour=t_hour,
        transit_minute=t_min,
        transit_second=t_sec,
        transit_latitude=t_lat,
        transit_longitude=t_lon,
        transit_timezone=t_tz,
        nakshatra_system=nakshatra_system,
        debilitation_mode=debilitation_mode,
        aspect_orb_degrees=aspect_orb_degrees
    )

    # 4. Scan Milestones for the 360-day horizon (-90d to +270d)
    from jyotish.transits.milestone_scanner import scan_transit_milestones
    m_cache_key = (native_id, t_year, t_month, nakshatra_system, debilitation_mode, round(aspect_orb_degrees, 2))
    if m_cache_key in _TRANSIT_MILESTONES_CACHE:
        scan_res = _TRANSIT_MILESTONES_CACHE[m_cache_key]
    else:
        scan_res = scan_transit_milestones(
            natal_chart=natal_chart,
            start_year=t_year,
            start_month=t_month,
            start_day=t_day,
            start_hour=t_hour,
            start_minute=t_min,
            days_back=90,
            days_forward=270,
            transit_latitude=t_lat,
            transit_longitude=t_lon,
            transit_timezone=t_tz,
            nakshatra_system=nakshatra_system,
            aspect_orb_degrees=aspect_orb_degrees
        )
        _TRANSIT_MILESTONES_CACHE[m_cache_key] = scan_res

    # 5. Generate SVG Bi-Wheel (Level 8 Presentation)
    # from jyotish.draw_chart import generate_transit_biwheel, parse_varga_data
    # svg = generate_transit_biwheel(...)
    svg = "<svg>...</svg>"

    return jsonify({
        "svg": svg,
        "transit_planets": transit_res["transit_planets"],
        "active_aspects": transit_res["active_aspects"],
        "transit_time_info": transit_res["transit_time_info"],
        "milestones": scan_res.get("milestones", []),
        "upcoming_stations": scan_res.get("upcoming_stations", []),
        "root": root,
        "mode": mode,
        "orb": aspect_orb_degrees
    })
