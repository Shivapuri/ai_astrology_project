from flask import Flask, render_template, request, jsonify, send_file
import os
import sys
import io
from jyotish import native_manager
from jyotish import generate_jyotish
from jyotish import draw_chart
from jyotish import pdf_exporter
import geonamescache
from timezonefinder import TimezoneFinder
from datetime import datetime
import pytz
import swisseph as swe

gc = geonamescache.GeonamesCache()
tf = TimezoneFinder()

app = Flask(__name__)
CHARTS_FILE = os.path.join(os.path.dirname(__file__), "database", "Charts.jsonl")

import json

@app.route('/')
def index():
    all_natives = native_manager.load_natives(CHARTS_FILE)
    dropdown_natives = [n for n in all_natives if n.get('in_dropdown', True) is not False]
    kb_path = os.path.join(os.path.dirname(__file__), "jyotish", "knowledge_base.json")
    try:
        with open(kb_path, 'r', encoding='utf-8') as f:
            knowledge_base = json.load(f)
    except Exception as e:
        knowledge_base = {}
        
    return render_template('index.html', natives=dropdown_natives, all_natives=all_natives, knowledge_base=knowledge_base)

def compute_chart_data(native, d10_mode="reverse", d24_mode="reverse", date_override=None, time_override=None, offset_seconds=0, nakshatra_system="ERNST_DHRUVA"):
    try:
        date_str = str(date_override) if date_override else str(native.get('date', '01/01/2000'))
        year, month, day = native_manager.parse_date_to_parts(date_str)
            
        time_str = str(time_override) if time_override else str(native.get('time', '12:00'))
        time_parts = time_str.split(':')
        hour = int(time_parts[0]) if len(time_parts) > 0 else 12
        minute = int(time_parts[1]) if len(time_parts) > 1 else 0
        second = int(float(time_parts[2])) if len(time_parts) > 2 else 0
    except Exception:
        year, month, day = 2000, 1, 1
        hour, minute, second = 12, 0, 0
    
    # Handle continuous astronomical time offset via Swiss Ephemeris
    is_preview = bool(offset_seconds != 0 or time_override or date_override)
    if offset_seconds != 0:
        local_hf = hour + (minute / 60.0) + (second / 3600.0)
        cal_flag = swe.JUL_CAL if (year < 1582 or (year == 1582 and month < 10) or (year == 1582 and month == 10 and day < 15)) else swe.GREG_CAL
        jd_base = swe.julday(year, month, day, local_hf, cal_flag)
        jd_shifted = jd_base + (float(offset_seconds) / 86400.0)
        s_year, s_month, s_day, s_hf = swe.revjul(jd_shifted, cal_flag)
        s_hour = int(s_hf)
        rem_m = (s_hf - s_hour) * 60.0
        s_minute = int(rem_m)
        s_sec = int(round((rem_m - s_minute) * 60.0))
        if s_sec >= 60:
            s_sec -= 60
            s_minute += 1
        if s_minute >= 60:
            s_minute -= 60
            s_hour += 1
        year, month, day, hour, minute, second = s_year, s_month, s_day, s_hour, s_minute, s_sec

    preview_time_str = f"{hour:02d}:{minute:02d}:{second:02d}"
    if year < 0:
        preview_date_str = f"{day:02d}/{month:02d}/{year}"
    else:
        preview_date_str = f"{day:02d}/{month:02d}/{year:04d}"

    tz_str = str(native.get('tz', '+00:00'))
    try:
        tz_offset = float(tz_str)
    except ValueError:
        try:
            if tz_str.upper() == 'Z':
                tz_offset = 0.0
            else:
                sign = -1 if tz_str.startswith('-') else 1
                tz_parts = tz_str.lstrip('+-').split(':')
                hours = float(tz_parts[0])
                minutes = float(tz_parts[1]) if len(tz_parts) > 1 else 0.0
                tz_offset = sign * (hours + minutes / 60.0)
        except Exception:
            tz_offset = 0.0

    chart = generate_jyotish.generate_kala_chart(
        name=native['name'],
        year=year,
        month=month,
        day=day,
        hour=hour,
        minute=minute,
        second=second,
        latitude=float(native['lat']),
        longitude=float(native['lon']),
        timezone_offset=tz_offset,
        name_sound_value=native.get('name_sound_value', 0),
        d10_mode=d10_mode,
        d24_mode=d24_mode,
        place=native.get('place', ''),
        nakshatra_system=nakshatra_system
    )
    chart["preview_info"] = {
        "is_preview": is_preview,
        "preview_time": preview_time_str,
        "preview_date": preview_date_str,
        "offset_seconds": offset_seconds
    }
    return chart

@app.route('/api/chart/<native_id>')
def get_chart(native_id):
    native = native_manager.get_native_by_id(CHARTS_FILE, native_id)
    if not native:
        return jsonify({"error": "Native not found"}), 404
        
    d10_mode = request.args.get('d10_mode', 'reverse')
    d24_mode = request.args.get('d24_mode', 'reverse')
    nakshatra_system = request.args.get('nakshatra_system', 'ERNST_DHRUVA')
    offset_seconds = request.args.get('offset_seconds', default=0, type=int)
    time_override = request.args.get('time')
    date_override = request.args.get('date')

    chart_data = compute_chart_data(
        native,
        d10_mode=d10_mode,
        d24_mode=d24_mode,
        date_override=date_override,
        time_override=time_override,
        offset_seconds=offset_seconds,
        nakshatra_system=nakshatra_system
    )
    
    # Generate SVGs for all vargas, all notation modes, and root planets (Lagna, Moon, Sun)
    svgs = {}
    modes = ["symbol", "english", "devanagari", "translit"]
    roots = ["Lagna", "Moon", "Sun"]
    d1_items = draw_chart.parse_varga_data(chart_data["vargas"]["D1"]) if "D1" in chart_data["vargas"] else []
    d9_items = draw_chart.parse_varga_data(chart_data["vargas"]["D9"]) if "D9" in chart_data["vargas"] else d1_items
    ayan_val = chart_data.get("astronomy", {}).get("equatorial_ayanamsa_value", 0)

    for v_name, v_data in chart_data["vargas"].items():
        parsed_items = draw_chart.parse_varga_data(v_data)
        outer_items = d9_items if v_name == "D1" else parsed_items
        outer_lbl = "D9" if v_name == "D1" else v_name
        svgs[v_name] = {}
        for m in modes:
            roots_dict = {}
            for r in roots:
                roots_dict[r] = {
                    "circular": draw_chart.generate_circular_chart(parsed_items, mode=m, varga_name=v_name, ayanamsha=ayan_val, root_planet=r),
                    "south": draw_chart.generate_south_indian(parsed_items, mode=m, varga_name=v_name, root_planet=r),
                    "north": draw_chart.generate_north_indian(parsed_items, mode=m, varga_name=v_name, root_planet=r),
                    "biwheel": draw_chart.generate_biwheel_chart(d1_items, outer_items, inner_name="D1", outer_name=outer_lbl, mode=m, ayanamsha=ayan_val, root_planet=r)
                }

            svgs[v_name][m] = {
                "circular": roots_dict["Lagna"]["circular"],
                "south": roots_dict["Lagna"]["south"],
                "north": roots_dict["Lagna"]["north"],
                "biwheel": roots_dict["Lagna"]["biwheel"],
                "roots": roots_dict
            }
        # Default top-level shortcuts for backward compatibility
        svgs[v_name]["south"] = svgs[v_name]["symbol"]["south"]
        svgs[v_name]["north"] = svgs[v_name]["symbol"]["north"]
        svgs[v_name]["circular"] = svgs[v_name]["symbol"]["circular"]
        svgs[v_name]["biwheel"] = svgs[v_name]["symbol"]["biwheel"]
        svgs[v_name]["roots"] = svgs[v_name]["symbol"]["roots"]
        
    preview_info = chart_data.get("preview_info", {})
    return jsonify({
        "data": chart_data,
        "svgs": svgs,
        "native": native,
        "is_preview": preview_info.get("is_preview", False),
        "preview_time": preview_info.get("preview_time", native.get("time")),
        "preview_date": preview_info.get("preview_date", native.get("date")),
        "preview_offset_seconds": preview_info.get("offset_seconds", 0)
    })

@app.route('/api/chart/<native_id>/biwheel')
def get_chart_biwheel(native_id):
    native = native_manager.get_native_by_id(CHARTS_FILE, native_id)
    if not native:
        return jsonify({"error": "Native not found"}), 404
        
    inner = request.args.get('inner', 'D1')
    outer = request.args.get('outer', 'D9')
    mode = request.args.get('mode', 'symbol')
    root = request.args.get('root', 'Lagna')
    d10_mode = request.args.get('d10_mode', 'reverse')
    d24_mode = request.args.get('d24_mode', 'reverse')
    nakshatra_system = request.args.get('nakshatra_system', 'ERNST_DHRUVA')
    offset_seconds = request.args.get('offset_seconds', default=0, type=int)
    time_override = request.args.get('time')
    date_override = request.args.get('date')

    chart_data = compute_chart_data(
        native,
        d10_mode=d10_mode,
        d24_mode=d24_mode,
        date_override=date_override,
        time_override=time_override,
        offset_seconds=offset_seconds,
        nakshatra_system=nakshatra_system
    )
    vargas = chart_data.get("vargas", {})
    inner_v = vargas.get(inner, vargas.get("D1", {}))
    outer_v = vargas.get(outer, vargas.get("D9", vargas.get("D1", {})))
    
    inner_items = draw_chart.parse_varga_data(inner_v) if inner_v else []
    outer_items = draw_chart.parse_varga_data(outer_v) if outer_v else []
    ayan = chart_data.get("astronomy", {}).get("equatorial_ayanamsa_value", 0)
    
    biwheel_svg = draw_chart.generate_biwheel_chart(
        inner_items=inner_items,
        outer_items=outer_items,
        inner_name=inner,
        outer_name=outer,
        mode=mode,
        ayanamsha=ayan,
        root_planet=root
    )
    return jsonify({
        "svg": biwheel_svg,
        "inner": inner,
        "outer": outer,
        "mode": mode,
        "root": root
    })

@app.route('/api/export_pdf', methods=['POST'])
def export_pdf():
    req_data = request.json or {}
    native_id = req_data.get('native_id')
    chart_data = req_data.get('chart_data')
    options = req_data.get('options', {})

    if not chart_data:
        if not native_id:
            return jsonify({"error": "No chart data or native_id provided"}), 400
        native = native_manager.get_native_by_id(CHARTS_FILE, native_id)
        if not native:
            return jsonify({"error": "Native not found"}), 404
        d10_mode = options.get('d10_mode', req_data.get('d10_mode', 'reverse'))
        d24_mode = options.get('d24_mode', req_data.get('d24_mode', 'reverse'))
        nakshatra_system = options.get('nakshatra_system', req_data.get('nakshatra_system', 'ERNST_DHRUVA'))
        chart_data = compute_chart_data(native, d10_mode=d10_mode, d24_mode=d24_mode, nakshatra_system=nakshatra_system)

    name = chart_data.get('subject_info', {}).get('name', 'Chart')
    safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '_', '-')).rstrip().replace(' ', '_')
    
    try:
        pdf_bytes = pdf_exporter.export_chart_pdf(chart_data, options)
        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"{safe_name}_Astra_Master_Plan.pdf"
        )
    except Exception as e:
        return jsonify({"error": f"Failed to generate PDF: {str(e)}"}), 500

@app.route('/api/export_preview', methods=['POST'])
def export_preview():
    req_data = request.json or {}
    native_id = req_data.get('native_id')
    chart_data = req_data.get('chart_data')
    options = req_data.get('options', {})

    if not chart_data:
        if not native_id:
            return "No chart data or native_id provided", 400
        native = native_manager.get_native_by_id(CHARTS_FILE, native_id)
        if not native:
            return "Native not found", 404
        d10_mode = options.get('d10_mode', req_data.get('d10_mode', 'reverse'))
        d24_mode = options.get('d24_mode', req_data.get('d24_mode', 'reverse'))
        nakshatra_system = options.get('nakshatra_system', req_data.get('nakshatra_system', 'ERNST_DHRUVA'))
        chart_data = compute_chart_data(native, d10_mode=d10_mode, d24_mode=d24_mode, nakshatra_system=nakshatra_system)

    html = pdf_exporter.generate_report_html(chart_data, options)
    return html, 200, {'Content-Type': 'text/html; charset=utf-8'}

@app.route('/api/natives')
def get_natives():
    natives = native_manager.load_natives(CHARTS_FILE)
    return jsonify(natives)

@app.route('/api/add_native', methods=['POST'])
def add_native():
    data = request.json
    new_native = native_manager.save_native(
        CHARTS_FILE,
        data['name'],
        data['date'],
        data['time'],
        data['lat'],
        data['lon'],
        data['tz'],
        place=data.get('place', 'Custom'),
        country=data.get('country', ''),
        name_sound_value=int(data.get('name_sound_value', 0)),
        notes=data.get('notes', ''),
        category=data.get('category', 'General'),
        in_dropdown=data.get('in_dropdown', True)
    )
    return jsonify(new_native)

@app.route('/api/native/<native_id>')
def get_native(native_id):
    native = native_manager.get_native_by_id(CHARTS_FILE, native_id)
    if native:
        return jsonify(native)
    return jsonify({"error": "Native not found"}), 404

@app.route('/api/native/<native_id>/toggle_dropdown', methods=['POST'])
def toggle_native_dropdown(native_id):
    new_val = native_manager.toggle_in_dropdown(CHARTS_FILE, native_id)
    if new_val is not None:
        return jsonify({"success": True, "id": native_id, "in_dropdown": new_val})
    return jsonify({"error": "Native not found"}), 404

@app.route('/api/update_native/<native_id>', methods=['POST'])
def update_native(native_id):
    data = request.json
    updated = native_manager.update_native(CHARTS_FILE, native_id, data)
    if updated:
        return jsonify(updated)
    else:
        return jsonify({"error": "Native not found"}), 404

@app.route('/api/delete_native/<native_id>', methods=['POST', 'DELETE'])
def delete_native(native_id):
    success = native_manager.delete_native(CHARTS_FILE, native_id)
    if success:
        return jsonify({"success": True, "id": native_id})
    else:
        return jsonify({"error": "Native not found or could not be deleted"}), 404

@app.route('/api/countries')
def get_countries():
    countries = gc.get_countries()
    # Return as a list of dicts: { "code": "US", "name": "United States" }
    result = [{"code": c["iso"], "name": c["name"]} for c in countries.values()]
    # Sort alphabetically by name
    result.sort(key=lambda x: x["name"])
    return jsonify(result)

@app.route('/api/cities/<country_code>')
def get_cities(country_code):
    cities = gc.get_cities()
    # Filter cities by country_code
    result = []
    for city in cities.values():
        if city["countrycode"] == country_code:
            result.append({
                "id": city["geonameid"],
                "name": city["name"],
                "lat": city["latitude"],
                "lon": city["longitude"],
                "timezone": city["timezone"]
            })
    # Sort by name
    result.sort(key=lambda x: x["name"])
    return jsonify(result)

@app.route('/api/timezone', methods=['POST'])
def get_timezone():
    try:
        data = request.json
        lat = float(data['lat'])
        lon = float(data['lon'])
        date_str = str(data.get('date', '01/01/2000')).strip()
        time_str = str(data.get('time', '12:00:00')).strip()
    except (KeyError, ValueError, TypeError) as e:
        return jsonify({"offset": "+00:00", "tz_name": "UTC", "error": f"Invalid input: {e}"})
        
    # Try to find timezone name
    tz_name = tf.timezone_at(lng=lon, lat=lat)
    if not tz_name:
        return jsonify({"offset": "+00:00", "tz_name": "UTC"})
        
    try:
        year, month, day = native_manager.parse_date_to_parts(date_str)
        if year < 1:
            # Historical BCE offsets were purely LMT anyway, use modern date to avoid DST
            dt = datetime(2000, 1, 1, 12, 0)
        else:
            t_parts = time_str.split(':')
            h = int(t_parts[0]) if len(t_parts) > 0 else 12
            m = int(t_parts[1]) if len(t_parts) > 1 else 0
            s = int(t_parts[2]) if len(t_parts) > 2 else 0
            dt = datetime(year, month, day, h, m, s)
            
        tz = pytz.timezone(tz_name)
        localized = tz.localize(dt)
        offset_total_seconds = localized.utcoffset().total_seconds()
        
        # Format offset as +HH:MM or -HH:MM
        hours = int(abs(offset_total_seconds) // 3600)
        minutes = int((abs(offset_total_seconds) % 3600) // 60)
        sign = "+" if offset_total_seconds >= 0 else "-"
        offset_str = f"{sign}{hours:02d}:{minutes:02d}"
        
        return jsonify({"offset": offset_str, "tz_name": tz_name})
    except Exception as e:
        return jsonify({"offset": "+00:00", "tz_name": "UTC", "error": str(e)})

if __name__ == '__main__':
    os.makedirs("cache", exist_ok=True)
    port = int(os.environ.get("PORT", 5001))
    print(f"\n✨ Astra Kala Astrology Server running at: http://127.0.0.1:{port}\n")
    app.run(debug=True, host="127.0.0.1", port=port)
