import json
import os

planet_symbols = {
    "Lagna": ("Asc", "#c0392b"),
    "Sun": ("☉\uFE0E", "#d35400"),  
    "Moon": ("☽\uFE0E", "#7f8c8d"),  
    "Mars": ("♂\uFE0E", "#c0392b"),  
    "Mercury": ("☿\uFE0E", "#27ae60"),  
    "Jupiter": ("♃\uFE0E", "#f39c12"),  
    "Venus": ("♀\uFE0E", "#b08d6a"),  
    "Saturn": ("♄\uFE0E", "#2c3e50"),  
    "Rahu": ("☊\uFE0E", "#7f8c8d"),  
    "Ketu": ("☋\uFE0E", "#34495e")
}

sign_symbols = {
    "Aries": ("♈\uFE0E", "#e74c3c", "Ar"), 
    "Taurus": ("♉\uFE0E", "#2ecc71", "Ta"), 
    "Gemini": ("♊\uFE0E", "#f1c40f", "Ge"), 
    "Cancer": ("♋\uFE0E", "#3498db", "Cn"), 
    "Leo": ("♌\uFE0E", "#e74c3c", "Le"), 
    "Virgo": ("♍\uFE0E", "#2ecc71", "Vi"), 
    "Libra": ("♎\uFE0E", "#f1c40f", "Li"), 
    "Scorpio": ("♏\uFE0E", "#3498db", "Sc"), 
    "Sagittarius": ("♐\uFE0E", "#e74c3c", "Sg"), 
    "Capricorn": ("♑\uFE0E", "#2ecc71", "Cp"), 
    "Aquarius": ("♒\uFE0E", "#f1c40f", "Aq"), 
    "Pisces": ("♓\uFE0E", "#3498db", "Pi")  
}

signs_list = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

def parse_astra_json(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
        
    items = []
    
    # Lagna
    l_sign = data["d1_rasi_chart"]["lagna"]["sign"]
    l_deg = data["d1_rasi_chart"]["lagna"]["degree_0_to_30"]
    minutes = int((l_deg - int(l_deg)) * 60)
    items.append({
        "type": "planet",
        "name": "Lagna",
        "sign": l_sign,
        "degree": int(l_deg),
        "minute": minutes
    })
    
    # Grahas
    for p_name, p_data in data["d1_rasi_chart"]["grahas"].items():
        deg = p_data["degree_0_to_30"]
        minutes = int((deg - int(deg)) * 60)
        items.append({
            "type": "planet",
            "name": p_name,
            "sign": p_data["sign"],
            "degree": int(deg),
            "minute": minutes
        })
        
    # House Cusps
    for i, c_lon in enumerate(data["d1_rasi_chart"]["placidus_cusps"]):
        c_sign_idx = int(c_lon // 30)
        c_sign = signs_list[c_sign_idx]
        items.append({
            "type": "cusp",
            "text": str(i + 1),
            "sign": c_sign,
            "color": "#8e44ad"
        })
        
    return items

def generate_south_indian(items):
    cell_coords = {
        "Pisces": (0, 0), "Aries": (100, 0), "Taurus": (200, 0), "Gemini": (300, 0),
        "Aquarius": (0, 100), "Cancer": (300, 100),
        "Capricorn": (0, 200), "Leo": (300, 200),
        "Sagittarius": (0, 300), "Scorpio": (100, 300), "Libra": (200, 300), "Virgo": (300, 300)
    }

    svg = '<svg width="400" height="400" viewBox="0 0 400 400" xmlns="http://www.w3.org/2000/svg" style="background:#fff; border-radius:8px;">\n'
    svg += '<rect x="0" y="0" width="400" height="400" fill="none" stroke="#2c3e50" stroke-width="2"/>\n'
    svg += '<rect x="100" y="100" width="200" height="200" fill="none" stroke="#2c3e50" stroke-width="2"/>\n'
    svg += '<line x1="100" y1="0" x2="100" y2="100" stroke="#2c3e50" stroke-width="2"/>\n'
    svg += '<line x1="100" y1="300" x2="100" y2="400" stroke="#2c3e50" stroke-width="2"/>\n'
    svg += '<line x1="200" y1="0" x2="200" y2="100" stroke="#2c3e50" stroke-width="2"/>\n'
    svg += '<line x1="200" y1="300" x2="200" y2="400" stroke="#2c3e50" stroke-width="2"/>\n'
    svg += '<line x1="300" y1="0" x2="300" y2="100" stroke="#2c3e50" stroke-width="2"/>\n'
    svg += '<line x1="300" y1="300" x2="300" y2="400" stroke="#2c3e50" stroke-width="2"/>\n'
    svg += '<line x1="0" y1="100" x2="100" y2="100" stroke="#2c3e50" stroke-width="2"/>\n'
    svg += '<line x1="300" y1="100" x2="400" y2="100" stroke="#2c3e50" stroke-width="2"/>\n'
    svg += '<line x1="0" y1="200" x2="100" y2="200" stroke="#2c3e50" stroke-width="2"/>\n'
    svg += '<line x1="300" y1="200" x2="400" y2="200" stroke="#2c3e50" stroke-width="2"/>\n'
    svg += '<line x1="0" y1="300" x2="100" y2="300" stroke="#2c3e50" stroke-width="2"/>\n'
    svg += '<line x1="300" y1="300" x2="400" y2="300" stroke="#2c3e50" stroke-width="2"/>\n'

    items_by_sign = {s: [] for s in signs_list}
    for item in items:
        if item.get("type") == "cusp":
            items_by_sign[item["sign"]].append(item)
        else:
            sym, color = planet_symbols.get(item["name"], (item["name"], "#000"))
            items_by_sign[item["sign"]].append({
                "type": "planet",
                "sym": sym,
                "color": color,
                "deg": f"{item['degree']}°{item['minute']:02d}'"
            })

    svg += '<g id="si-signs" style="display: none;">\n'
    for sign, (x, y) in cell_coords.items():
        s_sym, _, _ = sign_symbols[sign]
        svg += f'<text x="{x+50}" y="{y+65}" font-size="50" font-family="sans-serif" fill="#bdc3c7" opacity="0.2" text-anchor="middle">{s_sym}</text>\n'
    svg += '</g>\n'

    for sign, (x, y) in cell_coords.items():
        items = items_by_sign[sign]
        
        cx = x + 5
        cy = y + 18
        for item in items:
            if item["type"] == "cusp":
                svg += f'<text x="{cx}" y="{cy}" font-size="14" font-weight="bold" font-family="sans-serif" fill="{item["color"]}">{item["text"]}</text>\n'
            else:
                sym_size = "18" if item["sym"] != "Asc" else "14"
                svg += f'<text x="{cx}" y="{cy}" font-family="sans-serif">\n'
                svg += f'  <tspan font-size="{sym_size}" fill="{item["color"]}">{item["sym"]}</tspan>\n'
                svg += f'  <tspan font-size="11" fill="#7f8c8d"> {item["deg"]}</tspan>\n'
                svg += f'</text>\n'
            cy += 18

    svg += '</svg>\n'
    return svg

def generate_north_indian(items):
    svg = '<svg width="400" height="400" viewBox="0 0 400 400" xmlns="http://www.w3.org/2000/svg" style="background:#fff; border-radius:8px;">\n'
    svg += '<rect x="0" y="0" width="400" height="400" fill="none" stroke="#2c3e50" stroke-width="2"/>\n'
    svg += '<line x1="0" y1="0" x2="400" y2="400" stroke="#2c3e50" stroke-width="2"/>\n'
    svg += '<line x1="400" y1="0" x2="0" y2="400" stroke="#2c3e50" stroke-width="2"/>\n'
    svg += '<line x1="200" y1="0" x2="400" y2="200" stroke="#2c3e50" stroke-width="2"/>\n'
    svg += '<line x1="400" y1="200" x2="200" y2="400" stroke="#2c3e50" stroke-width="2"/>\n'
    svg += '<line x1="200" y1="400" x2="0" y2="200" stroke="#2c3e50" stroke-width="2"/>\n'
    svg += '<line x1="0" y1="200" x2="200" y2="0" stroke="#2c3e50" stroke-width="2"/>\n'

    ni_centers = [
        (200, 100), (100, 50), (50, 100), (100, 200),
        (50, 300), (100, 350), (200, 300), (300, 350),
        (350, 300), (300, 200), (350, 100), (300, 50)
    ]
    
    sign_pos = [
        (200, 180), (150, 20),  (20, 150),  (180, 200),
        (20, 250),  (150, 380), (200, 220), (250, 380),
        (380, 250), (220, 200), (380, 150), (250, 20)
    ]

    asc = next((p for p in items if p.get("name") == "Lagna"), None)
    asc_sign = asc["sign"] if asc else "Aries"
    asc_index = signs_list.index(asc_sign)

    items_by_house = [[] for _ in range(12)]
    
    for item in items:
        s_idx = signs_list.index(item["sign"])
        h_idx = (s_idx - asc_index + 12) % 12
        if item.get("type") == "cusp":
            items_by_house[h_idx].append(item)
        else:
            sym, color = planet_symbols.get(item["name"], (item["name"], "#000"))
            items_by_house[h_idx].append({
                "type": "planet",
                "sym": sym,
                "color": color,
                "deg": f"{item['degree']}°{item['minute']:02d}'"
            })

    for h in range(12):
        s_idx = (asc_index + h) % 12
        sign = signs_list[s_idx]
        s_sym, _, short_name = sign_symbols[sign]
        
        sx, sy = sign_pos[h]
        svg += f'<text x="{sx}" y="{sy}" font-size="16" font-family="sans-serif" fill="#7f8c8d" font-weight="bold" text-anchor="middle" dominant-baseline="central">{s_sym}</text>\n'

        cx, cy = ni_centers[h]
        items = items_by_house[h]
        
        item_height = 18
        total_h = len(items) * item_height
        start_y = cy - (total_h / 2) + (item_height / 2)
        
        curr_y = start_y
        for item in items:
            if item["type"] == "cusp":
                svg += f'<text x="{cx}" y="{curr_y}" font-size="14" font-weight="bold" font-family="sans-serif" fill="{item["color"]}" text-anchor="middle" dominant-baseline="central">{item["text"]}</text>\n'
            else:
                sym_size = "20" if item["sym"] != "Asc" else "14"
                svg += f'<text x="{cx}" y="{curr_y}" text-anchor="middle" dominant-baseline="central" font-family="sans-serif">\n'
                svg += f'  <tspan font-size="{sym_size}" fill="{item["color"]}">{item["sym"]}</tspan>\n'
                svg += f'  <tspan font-size="11" fill="#7f8c8d"> {item["deg"]}</tspan>\n'
                svg += f'</text>\n'
            curr_y += item_height

    svg += '</svg>\n'
    return svg

def create_html(south_svg, north_svg, json_file, output_file):
    with open(json_file, 'r') as f:
        data = json.load(f)
        
    subject = data["subject_info"]
    nakshatras = data["nakshatras"]["grahas"]
    d1 = data["d1_rasi_chart"]["grahas"]
    lagna = data["d1_rasi_chart"]["lagna"]
    
    # Create Nakshatra Table
    nak_html = "<table><thead><tr><th>Graha</th><th>Deg</th><th>Sign</th><th>Nakshatra</th><th>Pada</th></tr></thead><tbody>"
    
    def format_deg(deg_float):
        d = int(deg_float)
        m = int(round((deg_float - d) * 60))
        if m == 60:
            d += 1
            m = 0
        return f"{d:02d}:{m:02d}"

    # Lagna
    if "Lagna" in nakshatras:
        l_info = nakshatras["Lagna"]
        nak_html += f"<tr><td><strong>Asc</strong></td><td>{format_deg(lagna['degree_0_to_30'])}</td><td>{lagna['sign']}</td><td>{l_info['nakshatra']}</td><td>{l_info['pada']}</td></tr>"

    for graha, info in nakshatras.items():
        if graha == "Lagna":
            continue
        g_deg = d1[graha]["degree_0_to_30"]
        g_sign = d1[graha]["sign"]
        nak_html += f"<tr><td><strong>{graha}</strong></td><td>{format_deg(g_deg)}</td><td>{g_sign}</td><td>{info['nakshatra']}</td><td>{info['pada']}</td></tr>"
        
    nak_html += "</tbody></table>"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ernst Wilhelm Kala Chart</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f5f7fa;
            color: #333;
            margin: 0;
            padding: 40px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }}
        h1 {{
            color: #2c3e50;
        }}
        .controls {{
            margin-bottom: 20px;
            font-size: 16px;
        }}
        .charts-container {{
            display: flex;
            flex-wrap: wrap;
            gap: 40px;
            justify-content: center;
            margin-top: 20px;
        }}
        .chart-box {{
            background: #fff;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            display: flex;
            flex-direction: column;
            align-items: center;
        }}
        .chart-box h2 {{
            margin-top: 0;
            color: #2c3e50;
        }}
        svg {{
            background-color: #fff;
        }}
        .info-panel {{
            background: #fff;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            margin-top: 40px;
            width: 80%;
            max-width: 800px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th, td {{
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #f5f7fa;
        }}
    </style>
</head>
<body>
    <h1>{subject['name']} - Birth Chart</h1>
    <p>{subject['birth_datetime']} | {subject['latitude']} N, {subject['longitude']} E</p>
    
    <div class="controls">
        <label style="cursor: pointer; background: #fff; padding: 10px 15px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
            <input type="checkbox" id="toggleSigns" onchange="document.getElementById('si-signs').style.display = this.checked ? 'block' : 'none';"> 
            Show Zodiac Signs in South Indian Chart
        </label>
    </div>
    
    <div class="charts-container">
        <div class="chart-box">
            <h2>Tropical South Indian</h2>
            {south_svg}
        </div>
        <div class="chart-box">
            <h2>Tropical North Indian</h2>
            {north_svg}
        </div>
    </div>
    
    <div class="info-panel">
        <h2>Equatorial Sidereal Nakshatras</h2>
        <p><strong>Ayanamsa:</strong> {data['astronomy']['ayanamsa_name']} ({data['astronomy']['equatorial_ayanamsa_value']}°)</p>
        {nak_html}
    </div>
</body>
</html>
"""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"Chart generated successfully: {output_file}")

if __name__ == "__main__":
    planets = parse_astra_json("vedic_context.json")
    south_svg = generate_south_indian(planets)
    north_svg = generate_north_indian(planets)
    create_html(south_svg, north_svg, "vedic_context.json", "index.html")

