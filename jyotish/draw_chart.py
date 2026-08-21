planet_symbols = {
    "Lagna": ("Asc", "#b03a2e"),
    "Sun": ("☉\uFE0E", "#d35400"),  
    "Moon": ("☽\uFE0E", "#4a5568"),  
    "Mars": ("♂\uFE0E", "#c0392b"),  
    "Mercury": ("☿\uFE0E", "#1e824c"),  
    "Jupiter": ("♃\uFE0E", "#d68910"),  
    "Venus": ("♀\uFE0E", "#996515"),  
    "Saturn": ("♄\uFE0E", "#2c3e50"),  
    "Rahu": ("☊\uFE0E", "#5d6d7e"),  
    "Ketu": ("☋\uFE0E", "#34495e")
}

sign_symbols = {
    "Aries": ("♈\uFE0E", "#d35400", "Ar"), 
    "Taurus": ("♉\uFE0E", "#d35400", "Ta"), 
    "Gemini": ("♊\uFE0E", "#d35400", "Ge"), 
    "Cancer": ("♋\uFE0E", "#d35400", "Cn"), 
    "Leo": ("♌\uFE0E", "#d35400", "Le"), 
    "Virgo": ("♍\uFE0E", "#d35400", "Vi"), 
    "Libra": ("♎\uFE0E", "#d35400", "Li"), 
    "Scorpio": ("♏\uFE0E", "#d35400", "Sc"), 
    "Sagittarius": ("♐\uFE0E", "#d35400", "Sg"), 
    "Capricorn": ("♑\uFE0E", "#d35400", "Cp"), 
    "Aquarius": ("♒\uFE0E", "#d35400", "Aq"), 
    "Pisces": ("♓\uFE0E", "#d35400", "Pi")  
}

signs_list = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

def parse_varga_data(varga_data):
    items = []
    
    # Lagna
    l_sign = varga_data["lagna"]["sign"]
    l_deg = varga_data["lagna"]["degree_0_to_30"]
    minutes = int((l_deg - int(l_deg)) * 60)
    items.append({
        "type": "planet",
        "name": "Lagna",
        "sign": l_sign,
        "degree": int(l_deg),
        "minute": minutes
    })
    
    # Grahas
    for p_name, p_data in varga_data["grahas"].items():
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
    for i, cusp in enumerate(varga_data["cusps"]):
        items.append({
            "type": "cusp",
            "text": str(i + 1),
            "sign": cusp["sign"],
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

    svg = '<svg width="400" height="400" viewBox="0 0 400 400" xmlns="http://www.w3.org/2000/svg" style="background:#FAF5EB; border-radius:8px; border:1px solid #D0C5B4;">\n'
    svg += '<rect x="0" y="0" width="400" height="400" fill="none" stroke="#5C4433" stroke-width="2"/>\n'
    svg += '<rect x="100" y="100" width="200" height="200" fill="none" stroke="#5C4433" stroke-width="2"/>\n'
    svg += '<line x1="100" y1="0" x2="100" y2="100" stroke="#5C4433" stroke-width="2"/>\n'
    svg += '<line x1="100" y1="300" x2="100" y2="400" stroke="#5C4433" stroke-width="2"/>\n'
    svg += '<line x1="200" y1="0" x2="200" y2="100" stroke="#5C4433" stroke-width="2"/>\n'
    svg += '<line x1="200" y1="300" x2="200" y2="400" stroke="#5C4433" stroke-width="2"/>\n'
    svg += '<line x1="300" y1="0" x2="300" y2="100" stroke="#5C4433" stroke-width="2"/>\n'
    svg += '<line x1="300" y1="300" x2="300" y2="400" stroke="#5C4433" stroke-width="2"/>\n'
    svg += '<line x1="0" y1="100" x2="100" y2="100" stroke="#5C4433" stroke-width="2"/>\n'
    svg += '<line x1="300" y1="100" x2="400" y2="100" stroke="#5C4433" stroke-width="2"/>\n'
    svg += '<line x1="0" y1="200" x2="100" y2="200" stroke="#5C4433" stroke-width="2"/>\n'
    svg += '<line x1="300" y1="200" x2="400" y2="200" stroke="#5C4433" stroke-width="2"/>\n'
    svg += '<line x1="0" y1="300" x2="100" y2="300" stroke="#5C4433" stroke-width="2"/>\n'
    svg += '<line x1="300" y1="300" x2="400" y2="300" stroke="#5C4433" stroke-width="2"/>\n'

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

    # Corner sign badge in top-right of each cell
    svg += '<g id="si-signs" style="display: block;">\n'
    for sign, (x, y) in cell_coords.items():
        s_sym, _, _ = sign_symbols[sign]
        svg += f'<text x="{x+84}" y="{y+16}" font-size="14" font-family="sans-serif" font-weight="bold" fill="#D35400" text-anchor="middle" dominant-baseline="central">{s_sym}</text>\n'
    svg += '</g>\n'

    for sign, (x, y) in cell_coords.items():
        items = items_by_sign[sign]
        
        cx = x + 6
        cy = y + 17
        for item in items:
            if item["type"] == "cusp":
                svg += f'<text x="{cx}" y="{cy}" font-size="13" font-weight="bold" font-family="sans-serif" fill="{item["color"]}">{item["text"]}</text>\n'
            else:
                sym_size = "24" if item["sym"] != "Asc" else "14"
                svg += f'<text x="{cx}" y="{cy}" font-family="sans-serif">\n'
                svg += f'  <tspan font-size="{sym_size}" font-weight="bold" fill="{item["color"]}">{item["sym"]}</tspan>\n'
                svg += f'  <tspan font-size="11" font-weight="normal" fill="#4A3B32"> {item["deg"]}</tspan>\n'
                svg += f'</text>\n'
            cy += 20

    svg += '</svg>\n'
    return svg

def generate_north_indian(items):
    svg = '<svg width="400" height="400" viewBox="0 0 400 400" xmlns="http://www.w3.org/2000/svg" style="background:#FAF5EB; border-radius:8px; border:1px solid #D0C5B4;">\n'
    svg += '<rect x="0" y="0" width="400" height="400" fill="none" stroke="#5C4433" stroke-width="2"/>\n'
    svg += '<line x1="0" y1="0" x2="400" y2="400" stroke="#5C4433" stroke-width="2"/>\n'
    svg += '<line x1="400" y1="0" x2="0" y2="400" stroke="#5C4433" stroke-width="2"/>\n'
    svg += '<line x1="200" y1="0" x2="400" y2="200" stroke="#5C4433" stroke-width="2"/>\n'
    svg += '<line x1="400" y1="200" x2="200" y2="400" stroke="#5C4433" stroke-width="2"/>\n'
    svg += '<line x1="200" y1="400" x2="0" y2="200" stroke="#5C4433" stroke-width="2"/>\n'
    svg += '<line x1="0" y1="200" x2="200" y2="0" stroke="#5C4433" stroke-width="2"/>\n'

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
        s_sym, _, _ = sign_symbols[sign]
        
        sx, sy = sign_pos[h]
        svg += f'<text x="{sx}" y="{sy}" font-size="16" font-family="sans-serif" fill="#D35400" font-weight="bold" text-anchor="middle" dominant-baseline="central">{s_sym}</text>\n'

        cx, cy = ni_centers[h]
        items_in_house = items_by_house[h]
        
        item_height = 21
        total_h = len(items_in_house) * item_height
        start_y = cy - (total_h / 2) + (item_height / 2)
        
        curr_y = start_y
        for item in items_in_house:
            if item["type"] == "cusp":
                svg += f'<text x="{cx}" y="{curr_y}" font-size="13" font-weight="bold" font-family="sans-serif" fill="{item["color"]}" text-anchor="middle" dominant-baseline="central">{item["text"]}</text>\n'
            else:
                sym_size = "24" if item["sym"] != "Asc" else "14"
                svg += f'<text x="{cx}" y="{curr_y}" text-anchor="middle" dominant-baseline="central" font-family="sans-serif">\n'
                svg += f'  <tspan font-size="{sym_size}" font-weight="bold" fill="{item["color"]}">{item["sym"]}</tspan>\n'
                svg += f'  <tspan font-size="11" font-weight="normal" fill="#4A3B32"> {item["deg"]}</tspan>\n'
                svg += f'</text>\n'
            curr_y += item_height

    svg += '</svg>\n'
    return svg

def generate_bhava_chalita_north(bhavas):
    svg = '<svg width="400" height="400" viewBox="0 0 400 400" xmlns="http://www.w3.org/2000/svg" style="background:#FAF5EB; border-radius:8px; border:1px solid #D0C5B4;">\n'
    svg += '<rect x="0" y="0" width="400" height="400" fill="none" stroke="#5C4433" stroke-width="2"/>\n'
    svg += '<line x1="0" y1="0" x2="400" y2="400" stroke="#5C4433" stroke-width="2"/>\n'
    svg += '<line x1="400" y1="0" x2="0" y2="400" stroke="#5C4433" stroke-width="2"/>\n'
    svg += '<line x1="200" y1="0" x2="400" y2="200" stroke="#5C4433" stroke-width="2"/>\n'
    svg += '<line x1="400" y1="200" x2="200" y2="400" stroke="#5C4433" stroke-width="2"/>\n'
    svg += '<line x1="200" y1="400" x2="0" y2="200" stroke="#5C4433" stroke-width="2"/>\n'
    svg += '<line x1="0" y1="200" x2="200" y2="0" stroke="#5C4433" stroke-width="2"/>\n'

    ni_centers = [
        (200, 100), (100, 50), (50, 100), (100, 200),
        (50, 300), (100, 350), (200, 300), (300, 350),
        (350, 300), (300, 200), (350, 100), (300, 50)
    ]
    
    for h_idx in range(12):
        cx, cy = ni_centers[h_idx]
        bhava = bhavas[h_idx]
        
        cusp_lon = bhava["cusp"]
        sign_idx = int(cusp_lon // 30)
        s_sym = sign_symbols[signs_list[sign_idx]][0]
        
        sign_pos = [
            (200, 180), (150, 20),  (20, 150),  (180, 200),
            (20, 250),  (150, 380), (200, 220), (250, 380),
            (380, 250), (220, 200), (380, 150), (250, 20)
        ]
        sx, sy = sign_pos[h_idx]
        svg += f'<text x="{sx}" y="{sy}" font-size="16" font-family="sans-serif" fill="#D35400" font-weight="bold" text-anchor="middle" dominant-baseline="central">{s_sym}</text>\n'

        items_in_house = bhava["planets"]
        
        item_height = 21
        total_h = len(items_in_house) * item_height
        start_y = cy - (total_h / 2) + (item_height / 2)
        
        curr_y = start_y
        for p_name in items_in_house:
            sym, color = planet_symbols.get(p_name, (p_name, "#000"))
            sym_size = "24" if sym != "Asc" else "14"
            svg += f'<text x="{cx}" y="{curr_y}" text-anchor="middle" dominant-baseline="central" font-family="sans-serif">\n'
            svg += f'  <tspan font-size="{sym_size}" font-weight="bold" fill="{color}">{sym}</tspan>\n'
            svg += f'</text>\n'
            curr_y += item_height

    svg += "</svg>\n"
    return svg
