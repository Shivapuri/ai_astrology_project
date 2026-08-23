from flask import Flask, render_template, request, jsonify
import os
import sys
from jyotish import native_manager
from jyotish import generate_jyotish
from jyotish import draw_chart
import geonamescache
from timezonefinder import TimezoneFinder
from datetime import datetime
import pytz

gc = geonamescache.GeonamesCache()
tf = TimezoneFinder()

app = Flask(__name__)
CHARTS_FILE = os.path.join(os.path.dirname(__file__), "database", "Charts.jsonl")

import json

@app.route('/')
def index():
    natives = native_manager.load_natives(CHARTS_FILE)
    kb_path = os.path.join(os.path.dirname(__file__), "jyotish", "knowledge_base.json")
    try:
        with open(kb_path, 'r', encoding='utf-8') as f:
            knowledge_base = json.load(f)
    except Exception as e:
        knowledge_base = {}
        
    return render_template('index.html', natives=natives, knowledge_base=knowledge_base)

@app.route('/api/chart/<native_id>')
def get_chart(native_id):
    native = native_manager.get_native_by_id(CHARTS_FILE, native_id)
    if not native:
        return jsonify({"error": "Native not found"}), 404
        
    date_str = native['date']
    if date_str.startswith('-'):
        parts = date_str[1:].split('-')
        year = -int(parts[0])
        month = int(parts[1])
        day = int(parts[2])
    else:
        parts = date_str.split('-')
        year = int(parts[0])
        month = int(parts[1])
        day = int(parts[2])
        
    time_parts = native['time'].split(':')
    
    tz_str = str(native['tz'])
    if tz_str.startswith('+'):
        tz_offset = float(tz_str[1:3]) + float(tz_str[4:6])/60.0
    elif tz_str.startswith('-'):
        tz_offset = -(float(tz_str[1:3]) + float(tz_str[4:6])/60.0)
    elif tz_str == 'Z':
        tz_offset = 0.0
    else:
        tz_offset = 0.0

    chart_data = generate_jyotish.generate_kala_chart(
        name=native['name'],
        year=year,
        month=month,
        day=day,
        hour=int(time_parts[0]),
        minute=int(time_parts[1]),
        latitude=float(native['lat']),
        longitude=float(native['lon']),
        timezone_offset=tz_offset,
        output_filepath="cache/current_chart.json"
    )
    
    # Generate SVGs for all vargas and all notation modes
    svgs = {}
    modes = ["symbol", "english", "devanagari", "translit"]
    for v_name, v_data in chart_data["vargas"].items():
        parsed_items = draw_chart.parse_varga_data(v_data)
        svgs[v_name] = {}
        for m in modes:
            svgs[v_name][m] = {
                "circular": draw_chart.generate_circular_chart(parsed_items, mode=m, varga_name=v_name, ayanamsha=chart_data["astronomy"]["equatorial_ayanamsa_value"]),
                "south": draw_chart.generate_south_indian(parsed_items, mode=m, varga_name=v_name),
                "north": draw_chart.generate_north_indian(parsed_items, mode=m, varga_name=v_name)
            }
        # Default top-level shortcuts for backward compatibility
        svgs[v_name]["south"] = svgs[v_name]["symbol"]["south"]
        svgs[v_name]["north"] = svgs[v_name]["symbol"]["north"]
        svgs[v_name]["circular"] = svgs[v_name]["symbol"]["circular"]
        
    return jsonify({
        "data": chart_data,
        "svgs": svgs,
        "native": native
    })

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
        country=data.get('country', '')
    )
    return jsonify(new_native)

@app.route('/api/update_native/<native_id>', methods=['POST'])
def update_native(native_id):
    data = request.json
    updated = native_manager.update_native(CHARTS_FILE, native_id, data)
    if updated:
        return jsonify(updated)
    else:
        return jsonify({"error": "Native not found"}), 404

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
    data = request.json
    lat = float(data['lat'])
    lon = float(data['lon'])
    date_str = data['date']  # e.g., "1990-01-01" or "-3102-02-18"
    time_str = data['time']  # e.g., "14:30"
    
    # Try to find timezone name
    tz_name = tf.timezone_at(lng=lon, lat=lat)
    if not tz_name:
        return jsonify({"offset": "+00:00", "tz_name": "UTC"})
        
    try:
        # Parse date to datetime if possible, otherwise use a default for BCE to get rough offset
        # Historical BCE offsets were purely LMT (Local Mean Time) anyway, 
        # but let's try to parse the date to handle daylight saving if applicable.
        if date_str.startswith('-'):
            # It's BCE, daylight saving didn't exist, just use LMT or standard offset for that zone.
            # We'll calculate a standard offset using a modern winter date to avoid DST.
            dt = datetime(2000, 1, 1, 12, 0)
        else:
            parts = date_str.split('-')
            t_parts = time_str.split(':')
            dt = datetime(int(parts[0]), int(parts[1]), int(parts[2]), int(t_parts[0]), int(t_parts[1]))
            
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
