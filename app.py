from flask import Flask, render_template, request, jsonify
import os
import sys
from jyotish import native_manager
from jyotish import generate_jyotish
from jyotish import draw_chart

app = Flask(__name__)
CHARTS_FILE = "/Users/hajnaljanos/Documents/Aries/Charts/Charts.jsonl"

@app.route('/')
def index():
    natives = native_manager.load_natives(CHARTS_FILE)
    return render_template('index.html', natives=natives)

@app.route('/api/chart/<native_id>')
def get_chart(native_id):
    native = native_manager.get_native_by_id(CHARTS_FILE, native_id)
    if not native:
        return jsonify({"error": "Native not found"}), 404
        
    date_parts = native['date'].split('-')
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
        year=int(date_parts[0]),
        month=int(date_parts[1]),
        day=int(date_parts[2]),
        hour=int(time_parts[0]),
        minute=int(time_parts[1]),
        latitude=float(native['lat']),
        longitude=float(native['lon']),
        timezone_offset=tz_offset,
        output_filepath="cache/current_chart.json"
    )
    
    # Generate SVGs for all vargas
    svgs = {}
    for v_name, v_data in chart_data["vargas"].items():
        parsed_items = draw_chart.parse_varga_data(v_data)
        svgs[v_name] = {
            "south": draw_chart.generate_south_indian(parsed_items),
            "north": draw_chart.generate_north_indian(parsed_items),
            "bhava_north": draw_chart.generate_bhava_chalita_north(v_data["bhavas"])
        }
        
    return jsonify({
        "data": chart_data,
        "svgs": svgs
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
        data['tz']
    )
    return jsonify(new_native)

if __name__ == '__main__':
    os.makedirs("cache", exist_ok=True)
    app.run(debug=True, port=5000)
