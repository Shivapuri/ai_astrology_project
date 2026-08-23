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
    l_sign = data["vargas"]["D1"]["lagna"]["sign"]
    l_deg = data["vargas"]["D1"]["lagna"]["degree_0_to_30"]
    minutes = int((l_deg - int(l_deg)) * 60)
    items.append({
        "type": "planet",
        "name": "Lagna",
        "sign": l_sign,
        "degree": int(l_deg),
        "minute": minutes
    })
    
    # Grahas
    for p_name, p_data in data["vargas"]["D1"]["grahas"].items():
        deg = p_data["degree_0_to_30"]
        minutes = int((deg - int(deg)) * 60)
        items.append({
            "type": "planet",
            "name": p_name,
            "sign": p_data["sign"],
            "degree": int(deg),
            "minute": minutes
        })
        
    # House Cusps (Assuming campanus_cusps in D1)
    # We will just fetch them from data["astronomy"]["campanus_cusps"] or similar
    # Let's check what is in vedic_context.json for cusps. 
    # Actually wait, D1 might have a 'cusps' list? If not, we will pull from astronomy.
    cusps_list = data["vargas"]["D1"].get("campanus_cusps", data["vargas"]["D1"].get("placidus_cusps", []))
    for i, c_lon in enumerate(cusps_list):
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

    svg = '<svg width="100%" height="100%" viewBox="0 0 400 400" preserveAspectRatio="xMidYMid meet" xmlns="http://www.w3.org/2000/svg" style="background:#fff; border-radius:8px; max-height:100%; max-width:100%;">\n'
    svg += '<rect x="0" y="0" width="400" height="400" fill="none" stroke="#CBD5E1" stroke-width="2"/>\n'
    svg += '<rect x="100" y="100" width="200" height="200" fill="none" stroke="#CBD5E1" stroke-width="2"/>\n'
    svg += '<line x1="100" y1="0" x2="100" y2="100" stroke="#CBD5E1" stroke-width="2"/>\n'
    svg += '<line x1="100" y1="300" x2="100" y2="400" stroke="#CBD5E1" stroke-width="2"/>\n'
    svg += '<line x1="200" y1="0" x2="200" y2="100" stroke="#CBD5E1" stroke-width="2"/>\n'
    svg += '<line x1="200" y1="300" x2="200" y2="400" stroke="#CBD5E1" stroke-width="2"/>\n'
    svg += '<line x1="300" y1="0" x2="300" y2="100" stroke="#CBD5E1" stroke-width="2"/>\n'
    svg += '<line x1="300" y1="300" x2="300" y2="400" stroke="#CBD5E1" stroke-width="2"/>\n'
    svg += '<line x1="0" y1="100" x2="100" y2="100" stroke="#CBD5E1" stroke-width="2"/>\n'
    svg += '<line x1="300" y1="100" x2="400" y2="100" stroke="#CBD5E1" stroke-width="2"/>\n'
    svg += '<line x1="0" y1="200" x2="100" y2="200" stroke="#CBD5E1" stroke-width="2"/>\n'
    svg += '<line x1="300" y1="200" x2="400" y2="200" stroke="#CBD5E1" stroke-width="2"/>\n'
    svg += '<line x1="0" y1="300" x2="100" y2="300" stroke="#CBD5E1" stroke-width="2"/>\n'
    svg += '<line x1="300" y1="300" x2="400" y2="300" stroke="#CBD5E1" stroke-width="2"/>\n'

    items_by_sign = {s: [] for s in signs_list}
    for item in items:
        if item.get("type") == "cusp":
            items_by_sign[item["sign"]].append(item)
        else:
            sym, color = planet_symbols.get(item["name"], (item["name"], "#000"))
            items_by_sign[item["sign"]].append({
                "type": "planet",
                "name": item["name"],
                "sym": sym,
                "color": color,
                "deg": f"{item['degree']}°{item['minute']:02d}'"
            })

    # Quadrant Map: (cusp_dx, cusp_dy, sign_dx, sign_dy)
    quadrant_map = {
        "Pisces": (14, 14, 86, 86),
        "Aries": (14, 14, 86, 86),
        "Aquarius": (14, 14, 86, 86),
        "Taurus": (86, 14, 14, 86),
        "Gemini": (86, 14, 14, 86),
        "Cancer": (86, 14, 14, 86),
        "Leo": (86, 86, 14, 14),
        "Virgo": (86, 86, 14, 14),
        "Libra": (86, 86, 14, 14),
        "Scorpio": (14, 86, 86, 14),
        "Sagittarius": (14, 86, 86, 14),
        "Capricorn": (14, 86, 86, 14),
    }

    for sign, (x, y) in cell_coords.items():
        items = items_by_sign[sign]
        
        c_dx, c_dy, s_dx, s_dy = quadrant_map[sign]
        
        s_sym, _, _ = sign_symbols[sign]
        svg += f'<text class="interactive" data-type="sign" data-id="{sign}" x="{x + s_dx}" y="{y + s_dy}" font-size="14" font-family="sans-serif" font-weight="bold" fill="#bdc3c7" opacity="0.6" text-anchor="middle" dominant-baseline="central">{s_sym}</text>\n'

        planets = [it for it in items if it["type"] != "cusp"]
        cusps = [it for it in items if it["type"] == "cusp"]
        
        if cusps:
            cusp_texts = [c["text"] for c in cusps]
            if len(cusp_texts) > 3:
                mid = len(cusp_texts) // 2
                l1 = " ".join(cusp_texts[:mid])
                l2 = " ".join(cusp_texts[mid:])
                svg += f'<text class="interactive" data-type="house" data-id="{" ".join(cusp_texts)}" x="{x + c_dx}" y="{y + c_dy - 6}" font-size="14" font-weight="bold" font-family="sans-serif" fill="{cusps[0]["color"]}" text-anchor="middle" dominant-baseline="central">{l1}</text>\n'
                svg += f'<text class="interactive" data-type="house" data-id="{" ".join(cusp_texts)}" x="{x + c_dx}" y="{y + c_dy + 6}" font-size="14" font-weight="bold" font-family="sans-serif" fill="{cusps[0]["color"]}" text-anchor="middle" dominant-baseline="central">{l2}</text>\n'
            else:
                svg += f'<text class="interactive" data-type="house" data-id="{" ".join(cusp_texts)}" x="{x + c_dx}" y="{y + c_dy}" font-size="14" font-weight="bold" font-family="sans-serif" fill="{cusps[0]["color"]}" text-anchor="middle" dominant-baseline="central">{" ".join(cusp_texts)}</text>\n'

        # Basic linear layout for planets in generate_html_chart.py for now
        # Centering planets in the middle zone
        cy = y + 25
        for item in planets:
            cx = x + 50
            sym_size = "18" if item["sym"] != "Asc" else "14"
            svg += f'<text class="interactive" data-type="planet" data-id="{item["name"]}" x="{cx}" y="{cy}" font-family="sans-serif" text-anchor="middle" dominant-baseline="central">\n'
            svg += f'  <tspan font-size="{sym_size}" fill="{item["color"]}">{item["sym"]}</tspan>\n'
            svg += f'  <tspan font-size="11" fill="#7f8c8d"> {item["deg"]}</tspan>\n'
            svg += f'</text>\n'
            cy += 18

    svg += '</svg>\n'
    return svg

def generate_north_indian(items):
    svg = '<svg width="100%" height="100%" viewBox="0 0 400 400" preserveAspectRatio="xMidYMid meet" xmlns="http://www.w3.org/2000/svg" style="background:#fff; border-radius:8px; max-height:100%; max-width:100%;">\n'
    svg += '<rect x="0" y="0" width="400" height="400" fill="none" stroke="#CBD5E1" stroke-width="2"/>\n'
    svg += '<line x1="0" y1="0" x2="400" y2="400" stroke="#CBD5E1" stroke-width="2"/>\n'
    svg += '<line x1="400" y1="0" x2="0" y2="400" stroke="#CBD5E1" stroke-width="2"/>\n'
    svg += '<line x1="200" y1="0" x2="400" y2="200" stroke="#CBD5E1" stroke-width="2"/>\n'
    svg += '<line x1="400" y1="200" x2="200" y2="400" stroke="#CBD5E1" stroke-width="2"/>\n'
    svg += '<line x1="200" y1="400" x2="0" y2="200" stroke="#CBD5E1" stroke-width="2"/>\n'
    svg += '<line x1="0" y1="200" x2="200" y2="0" stroke="#CBD5E1" stroke-width="2"/>\n'

    ni_centers = [
        (200, 100), (100, 50), (50, 100), (100, 200),
        (50, 300), (100, 350), (200, 300), (300, 350),
        (350, 300), (300, 200), (350, 100), (300, 50)
    ]
    
    sign_pos = [
        (200, 175), (145, 25),  (25, 145),  (175, 200),
        (25, 255),  (145, 375), (200, 225), (255, 375),
        (375, 255), (225, 200), (375, 145), (255, 25)
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
                "name": item["name"],
                "sym": sym,
                "color": color,
                "deg": f"{item['degree']}°{item['minute']:02d}'"
            })

    for h in range(12):
        s_idx = (asc_index + h) % 12
        sign = signs_list[s_idx]
        s_sym, _, short_name = sign_symbols[sign]
        
        sx, sy = sign_pos[h]
        svg += f'<text class="interactive" data-type="sign" data-id="{sign}" x="{sx}" y="{sy}" font-size="16" font-family="sans-serif" fill="#7f8c8d" font-weight="bold" text-anchor="middle" dominant-baseline="central">{s_sym}</text>\n'

        cx, cy = ni_centers[h]
        items = items_by_house[h]
        planets = [it for it in items if it["type"] != "cusp"]
        cusps = [it for it in items if it["type"] == "cusp"]
        
        item_height = 18
        total_h = len(items) * item_height
        start_y = cy - (total_h / 2) + (item_height / 2)
        
        curr_y = start_y
        if cusps:
            cusp_texts = [c["text"] for c in cusps]
            if len(cusp_texts) > 3:
                mid = len(cusp_texts) // 2
                l1 = " ".join(cusp_texts[:mid])
                l2 = " ".join(cusp_texts[mid:])
                svg += f'<text class="interactive" data-type="house" data-id="{" ".join(cusp_texts)}" x="{cx}" y="{curr_y - 6}" font-size="14" font-weight="bold" font-family="sans-serif" fill="{cusps[0]["color"]}" text-anchor="middle" dominant-baseline="central">{l1}</text>\n'
                svg += f'<text class="interactive" data-type="house" data-id="{" ".join(cusp_texts)}" x="{cx}" y="{curr_y + 6}" font-size="14" font-weight="bold" font-family="sans-serif" fill="{cusps[0]["color"]}" text-anchor="middle" dominant-baseline="central">{l2}</text>\n'
            else:
                svg += f'<text class="interactive" data-type="house" data-id="{" ".join(cusp_texts)}" x="{cx}" y="{curr_y}" font-size="14" font-weight="bold" font-family="sans-serif" fill="{cusps[0]["color"]}" text-anchor="middle" dominant-baseline="central">{" ".join(cusp_texts)}</text>\n'
            curr_y += item_height
        
        for item in planets:
            if len(planets) > 4:
                sym_size = "16" if item["sym"] != "Asc" else "12"
                deg_sz = "9"
                y_offset = 12
            else:
                sym_size = "20" if item["sym"] != "Asc" else "14"
                deg_sz = "11"
                y_offset = 18

            svg += f'<text class="interactive" data-type="planet" data-id="{item["name"]}" x="{cx}" y="{curr_y}" text-anchor="middle" dominant-baseline="central" font-family="sans-serif">\n'
            svg += f'  <tspan font-size="{sym_size}" fill="{item["color"]}">{item["sym"]}</tspan>\n'
            svg += f'  <tspan font-size="{deg_sz}" fill="#7f8c8d"> {item["deg"]}</tspan>\n'
            svg += f'</text>\n'
            curr_y += y_offset

    svg += '</svg>\n'
    return svg

def create_html(south_svg, north_svg, json_file, output_file):
    with open(json_file, 'r') as f:
        data = json.load(f)
        
    subject = data["subject_info"]
    nakshatras = data["nakshatras"]["grahas"]
    d1 = data["vargas"]["D1"]["grahas"]
    lagna = data["vargas"]["D1"]["lagna"]
    
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

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Astra Engine - Jyotish Dashboard</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/split.js/1.6.5/split.min.js"></script>
    <style>
        :root {{
            --bg-color: #F9FAFB;
            --pane-bg: #FFFFFF;
            --text-main: #111827;
            --text-muted: #6B7280;
            --border-color: #E5E7EB;
            --accent-color: #4F46E5;
            --accent-hover: #4338CA;
            --gutter-bg: #F3F4F6;
            --gutter-hover: #E5E7EB;
            --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
            --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            --radius-md: 12px;
            --radius-lg: 16px;
        }}
        
        * {{
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-main);
            margin: 0;
            padding: 0;
            height: 100vh;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            -webkit-font-smoothing: antialiased;
        }}
        
        /* Header */
        header {{
            background: var(--pane-bg);
            padding: 12px 24px;
            border-bottom: 1px solid var(--border-color);
            display: flex;
            justify-content: space-between;
            align-items: center;
            z-index: 10;
        }}
        
        .header-left {{
            display: flex;
            align-items: baseline;
            gap: 16px;
        }}

        header h1 {{
            margin: 0;
            font-size: 1.1rem;
            font-weight: 600;
            color: var(--text-main);
            letter-spacing: -0.01em;
        }}
        
        header .details {{
            font-size: 0.85rem;
            color: var(--text-muted);
            font-weight: 500;
        }}
        
        .shortcuts-hint {{
            font-size: 0.75rem;
            font-weight: 500;
            background: var(--bg-color);
            padding: 6px 12px;
            border-radius: 20px;
            color: var(--text-muted);
            border: 1px solid var(--border-color);
            display: flex;
            gap: 8px;
        }}
        
        .shortcuts-hint kbd {{
            background: #fff;
            border: 1px solid #d1d5db;
            border-radius: 4px;
            padding: 2px 6px;
            font-family: inherit;
            font-size: 0.7rem;
            color: var(--text-main);
            box-shadow: 0 1px 1px rgba(0,0,0,0.05);
        }}
        
        /* Split Layout */
        #main-container {{
            display: flex;
            flex: 1;
            height: calc(100vh - 53px);
            overflow: hidden;
        }}
        
        .split {{
            display: flex;
            flex-direction: column;
            height: 100%;
        }}
        
        #chart-pane {{
            background-color: var(--bg-color);
            padding: 24px;
        }}
        
        #info-pane {{
            background: var(--pane-bg);
            border-left: 1px solid var(--border-color);
        }}
        
        .pane-section {{
            display: flex;
            flex-direction: column;
            overflow: hidden;
            background: var(--pane-bg);
        }}
        
        /* Gutters for Split.js */
        .gutter {{
            background-color: var(--gutter-bg);
            background-repeat: no-repeat;
            background-position: 50%;
            transition: background-color 0.2s ease;
        }}
        .gutter.gutter-horizontal {{
            cursor: col-resize;
            border-left: 1px solid var(--border-color);
            border-right: 1px solid var(--border-color);
        }}
        .gutter.gutter-vertical {{
            cursor: row-resize;
            border-top: 1px solid var(--border-color);
            border-bottom: 1px solid var(--border-color);
        }}
        .gutter:hover, .gutter:active {{
            background-color: var(--gutter-hover);
        }}
        
        /* Chart Views */
        .chart-view {{
            display: none;
            flex-direction: column;
            background: var(--pane-bg);
            border-radius: var(--radius-lg);
            border: 1px solid var(--border-color);
            box-shadow: var(--shadow-sm);
            width: 100%;
            height: 100%;
            overflow: hidden;
            padding: 24px;
        }}
        .chart-view.active {{
            display: flex;
            animation: fadeIn 0.3s ease;
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(4px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        .chart-view h2 {{
            margin-top: 0;
            font-size: 1rem;
            font-weight: 600;
            color: var(--text-main);
            margin-bottom: 16px;
            flex-shrink: 0;
            text-align: center;
        }}
        
        .chart-svg-container {{
            flex: 1;
            width: 100%;
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
        }}
        
        /* Sub-Windows */
        .sub-window {{
            display: flex;
            flex-direction: column;
            height: 100%;
            width: 100%;
        }}
        
        .sub-window-header {{
            padding: 16px 24px;
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            font-weight: 600;
            color: var(--text-muted);
            border-bottom: 1px solid var(--border-color);
            flex-shrink: 0;
            display: flex;
            align-items: center;
        }}
        
        .sub-window-content {{
            padding: 24px;
            flex: 1;
            overflow-y: auto;
            font-size: 0.95rem;
            line-height: 1.5;
        }}
        
        /* Tabs */
        .tabs {{
            display: flex;
            padding: 0 16px;
            border-bottom: 1px solid var(--border-color);
            flex-shrink: 0;
            gap: 16px;
        }}
        
        .tab-btn {{
            padding: 16px 8px;
            border: none;
            background: transparent;
            cursor: pointer;
            font-size: 0.9rem;
            font-weight: 500;
            color: var(--text-muted);
            border-bottom: 2px solid transparent;
            outline: none;
            transition: all 0.2s ease;
            margin-bottom: -1px;
        }}
        
        .tab-btn:hover {{
            color: var(--text-main);
        }}
        
        .tab-btn.active {{
            color: var(--accent-color);
            border-bottom: 2px solid var(--accent-color);
        }}
        
        .tab-content {{
            display: none;
            padding: 24px;
            flex: 1;
            overflow-y: auto;
        }}
        .tab-content.active {{
            display: block;
            animation: fadeIn 0.2s ease;
        }}
        
        /* Tables */
        table {{
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
            font-size: 0.85rem;
        }}
        
        th {{
            text-align: left;
            padding: 12px 16px;
            font-weight: 500;
            color: var(--text-muted);
            border-bottom: 1px solid var(--border-color);
            text-transform: uppercase;
            font-size: 0.75rem;
            letter-spacing: 0.02em;
        }}
        
        td {{
            padding: 12px 16px;
            border-bottom: 1px solid var(--border-color);
            color: var(--text-main);
        }}
        
        tr:last-child td {{
            border-bottom: none;
        }}
        
        tbody tr {{
            transition: background-color 0.15s ease;
        }}
        
        tbody tr:hover {{
            background-color: var(--bg-color);
        }}
        
        /* Interactive elements */
        .interactive {{
            cursor: pointer;
            transition: all 0.2s ease;
        }}
        
        .interactive:hover {{
            filter: brightness(0.8);
            transform: scale(1.05);
        }}
        
        .interactive[data-type="sign"]:hover {{
            opacity: 1 !important;
            fill: var(--accent-color);
        }}
    </style>
</head>
<body>

    <header>
        <h1>{subject['name']} - Astrological Dashboard</h1>
        <div class="details">{subject['birth_datetime']} | {subject['latitude']} N, {subject['longitude']} E</div>
        <div class="shortcuts-hint">
            <strong>Hotkeys:</strong> [S] South Indian | [N] North Indian | [C] Circular
        </div>
    </header>
    
    <div id="main-container">
        <!-- Left Pane: Charts -->
        <div id="chart-pane" class="split">
            
            <div id="view-south" class="chart-view active">
                <h2>Tropical South Indian</h2>
                <div class="chart-svg-container">
                    {south_svg}
                </div>
            </div>
            
            <div id="view-north" class="chart-view">
                <h2>Tropical North Indian</h2>
                <div class="chart-svg-container">
                    {north_svg}
                </div>
            </div>
            
            <div id="view-circle" class="chart-view">
                <h2>Circular Western / Nakshatra (Coming Soon)</h2>
                <div class="chart-svg-container">
                    <div style="width:100%; height:100%; border:2px dashed #ccc; border-radius:50%; display:flex; align-items:center; justify-content:center; color:#999;">
                        Circle Chart Placeholder
                    </div>
                </div>
            </div>
            
        </div>
        
        <!-- Right Pane: Information & Metrics -->
        <div id="info-pane" class="split">
            
            <!-- Top Section: Context Info -->
            <div id="info-top" class="pane-section">
                <div class="sub-window">
                    <div class="sub-window-header">Context Info</div>
                    <div class="sub-window-content" id="context-info-content">
                        <p style="color:#777; font-style:italic;">Click on a planet, sign, or house in the chart to view details here.</p>
                    </div>
                </div>
            </div>
            
            <!-- Bottom Section: Tabs (Nakshatras / Metrics) -->
            <div id="info-bottom" class="pane-section">
                <div class="sub-window">
                    <div class="tabs">
                        <button class="tab-btn active" data-target="tab-nakshatras">Nakshatras</button>
                        <button class="tab-btn" data-target="tab-metrics">Metrics</button>
                    </div>
                    
                    <div class="tab-content active" id="tab-nakshatras">
                        <p style="margin-top:0; font-size:0.85rem;"><strong>Ayanamsa:</strong> {data['astronomy']['ayanamsa_name']} ({data['astronomy']['equatorial_ayanamsa_value']}°)</p>
                        {nak_html}
                    </div>
                    
                    <div class="tab-content" id="tab-metrics">
                        <p style="color:#777; font-style:italic;">Avasthas, Shadbala, and other planet strengths will be displayed here.</p>
                    </div>
                </div>
            </div>
            
        </div>
    </div>

    <script>
        // Store context from python
        const chartData = {json.dumps(data)};

        // Initialize Horizontal Split (Left/Right)
        Split(['#chart-pane', '#info-pane'], {{
            sizes: [65, 35],
            minSize: [400, 300],
            gutterSize: 8,
            cursor: 'col-resize'
        }});

        // Initialize Vertical Split (Top-Right / Bottom-Right)
        Split(['#info-top', '#info-bottom'], {{
            direction: 'vertical',
            sizes: [40, 60],
            minSize: [150, 200],
            gutterSize: 8,
            cursor: 'row-resize'
        }});

        // Tab Switching Logic
        document.querySelectorAll('.tab-btn').forEach(btn => {{
            btn.addEventListener('click', () => {{
                // Remove active class from all tabs
                document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
                document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
                
                // Add active class to clicked tab and its target content
                btn.classList.add('active');
                document.getElementById(btn.getAttribute('data-target')).classList.add('active');
            }});
        }});

        // Hotkey Listener for Chart Switching
        document.addEventListener('keydown', (e) => {{
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;

            const key = e.key.toLowerCase();
            if (['s', 'n', 'c'].includes(key)) {{
                document.querySelectorAll('.chart-view').forEach(el => el.classList.remove('active'));
                
                if (key === 's') document.getElementById('view-south').classList.add('active');
                if (key === 'n') document.getElementById('view-north').classList.add('active');
                if (key === 'c') document.getElementById('view-circle').classList.add('active');
            }}
        }});
        
        // Interactive Elements Click Handler
        document.querySelectorAll('.interactive').forEach(el => {{
            el.addEventListener('click', (e) => {{
                const type = el.getAttribute('data-type');
                const id = el.getAttribute('data-id');
                const infoContent = document.getElementById('context-info-content');
                
                if (type === 'planet') {{
                    const pData = chartData.vargas.D1.grahas[id];
                    let infoHtml = `<h3>${{id}}</h3>`;
                    if (pData) {{
                        infoHtml += `<p><strong>Sign:</strong> ${{pData.sign}}</p>`;
                        infoHtml += `<p><strong>Degree (0-30):</strong> ${{pData.degree_0_to_30.toFixed(2)}}°</p>`;
                        infoHtml += `<p><strong>Nakshatra:</strong> ${{pData.nakshatra || 'N/A'}}</p>`;
                        if (pData.dignity) infoHtml += `<p><strong>Dignity:</strong> ${{pData.dignity}}</p>`;
                    }} else {{
                        infoHtml += `<p>Detailed data not available.</p>`;
                    }}
                    infoContent.innerHTML = infoHtml;
                }} else if (type === 'sign') {{
                    infoContent.innerHTML = `<h3>Sign: ${{id}}</h3><p>General knowledge base for ${{id}} will load here.</p>`;
                }} else if (type === 'house') {{
                    infoContent.innerHTML = `<h3>House Cusp: ${{id}}</h3><p>Details about house ${{id}} will load here.</p>`;
                }}
            }});
        }});
    </script>
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

