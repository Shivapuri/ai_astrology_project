planet_notations = {
    "Lagna": {
        "symbol": "Asc",
        "english": "Asc",
        "devanagari": "ल",
        "translit": "Lag",
        "full_en": "Ascendant",
        "full_sa": "Lagna",
        "dev_full": "लग्न",
        "color": "#a93226"
    },
    "Sun": {
        "symbol": "☉\uFE0E",
        "english": "Su",
        "devanagari": "सू",
        "translit": "Sū",
        "full_en": "Sun",
        "full_sa": "Sūrya",
        "dev_full": "सूर्य",
        "color": "#d35400"
    },
    "Moon": {
        "symbol": "☽\uFE0E",
        "english": "Mo",
        "devanagari": "चं",
        "translit": "Ca",
        "full_en": "Moon",
        "full_sa": "Chandra",
        "dev_full": "चन्द्र",
        "color": "#4a5568"
    },
    "Mars": {
        "symbol": "♂\uFE0E",
        "english": "Ma",
        "devanagari": "मं",
        "translit": "Ma",
        "full_en": "Mars",
        "full_sa": "Mangala",
        "dev_full": "मङ्गल",
        "color": "#c0392b"
    },
    "Mercury": {
        "symbol": "☿\uFE0E",
        "english": "Me",
        "devanagari": "बु",
        "translit": "Bu",
        "full_en": "Mercury",
        "full_sa": "Budha",
        "dev_full": "बुध",
        "color": "#1e824c"
    },
    "Jupiter": {
        "symbol": "♃\uFE0E",
        "english": "Ju",
        "devanagari": "गु",
        "translit": "Gu",
        "full_en": "Jupiter",
        "full_sa": "Guru",
        "dev_full": "गुरु",
        "color": "#b7791f"
    },
    "Venus": {
        "symbol": "♀\uFE0E",
        "english": "Ve",
        "devanagari": "शु",
        "translit": "Śu",
        "full_en": "Venus",
        "full_sa": "Śukra",
        "dev_full": "शुक्र",
        "color": "#8d6e63"
    },
    "Saturn": {
        "symbol": "♄\uFE0E",
        "english": "Sa",
        "devanagari": "श",
        "translit": "Śa",
        "full_en": "Saturn",
        "full_sa": "Śani",
        "dev_full": "शनि",
        "color": "#2c3e50"
    },
    "Rahu": {
        "symbol": "☊\uFE0E",
        "english": "Ra",
        "devanagari": "रा",
        "translit": "Rā",
        "full_en": "North Node",
        "full_sa": "Rāhu",
        "dev_full": "राहु",
        "color": "#5d6d7e"
    },
    "Ketu": {
        "symbol": "☋\uFE0E",
        "english": "Ke",
        "devanagari": "के",
        "translit": "Ke",
        "full_en": "South Node",
        "full_sa": "Ketu",
        "dev_full": "केतु",
        "color": "#34495e"
    }
}

# Compatibility mapping
planet_symbols = {k: (v["symbol"], v["color"]) for k, v in planet_notations.items()}

# Soft antique parchment tone for Rashi signs so they blend elegantly into the background
RASHI_SIGN_COLOR = "#b59472"

sign_symbols = {
    "Aries": ("♈\uFE0E", RASHI_SIGN_COLOR, "Ar"), 
    "Taurus": ("♉\uFE0E", RASHI_SIGN_COLOR, "Ta"), 
    "Gemini": ("♊\uFE0E", RASHI_SIGN_COLOR, "Ge"), 
    "Cancer": ("♋\uFE0E", RASHI_SIGN_COLOR, "Cn"), 
    "Leo": ("♌\uFE0E", RASHI_SIGN_COLOR, "Le"), 
    "Virgo": ("♍\uFE0E", RASHI_SIGN_COLOR, "Vi"), 
    "Libra": ("♎\uFE0E", RASHI_SIGN_COLOR, "Li"), 
    "Scorpio": ("♏\uFE0E", RASHI_SIGN_COLOR, "Sc"), 
    "Sagittarius": ("♐\uFE0E", RASHI_SIGN_COLOR, "Sg"), 
    "Capricorn": ("♑\uFE0E", RASHI_SIGN_COLOR, "Cp"), 
    "Aquarius": ("♒\uFE0E", RASHI_SIGN_COLOR, "Aq"), 
    "Pisces": ("♓\uFE0E", RASHI_SIGN_COLOR, "Pi")  
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
            "minute": minutes,
            "is_retrograde": p_data.get("is_retrograde", False)
        })
        
    # House Cusps
    for i, cusp in enumerate(varga_data["cusps"]):
        items.append({
            "type": "cusp",
            "text": str(i + 1),
            "sign": cusp["sign"],
            "color": "#7d3c98"
        })
        
    return items

def get_south_indian_positions(num_planets, cell_x, cell_y, has_cusps=False):
    positions = []
    if num_planets == 1:
        py = cell_y + (36 if has_cusps else 42)
        positions.append((cell_x + 50, py))
    elif num_planets == 2:
        py = cell_y + (36 if has_cusps else 42)
        positions.append((cell_x + 28, py))
        positions.append((cell_x + 72, py))
    elif num_planets == 3:
        r1_y = cell_y + 24
        r2_y = cell_y + (58 if has_cusps else 64)
        positions.append((cell_x + 28, r1_y))
        positions.append((cell_x + 72, r1_y))
        positions.append((cell_x + 50, r2_y))
    elif num_planets == 4:
        r1_y = cell_y + 24
        r2_y = cell_y + (58 if has_cusps else 64)
        positions.append((cell_x + 28, r1_y))
        positions.append((cell_x + 72, r1_y))
        positions.append((cell_x + 28, r2_y))
        positions.append((cell_x + 72, r2_y))
    elif num_planets == 5:
        r1_y = cell_y + 24
        r2_y = cell_y + (58 if has_cusps else 64)
        positions.append((cell_x + 20, r1_y))
        positions.append((cell_x + 50, r1_y))
        positions.append((cell_x + 80, r1_y))
        positions.append((cell_x + 32, r2_y))
        positions.append((cell_x + 68, r2_y))
    else:
        r1_y = cell_y + 24
        r2_y = cell_y + (58 if has_cusps else 64)
        positions.append((cell_x + 20, r1_y))
        positions.append((cell_x + 50, r1_y))
        positions.append((cell_x + 80, r1_y))
        positions.append((cell_x + 20, r2_y))
        positions.append((cell_x + 50, r2_y))
        positions.append((cell_x + 80, r2_y))
    return positions

def get_north_indian_positions(num_planets, cx, cy, has_cusps=False):
    positions = []
    if num_planets == 1:
        py = cy - (12 if has_cusps else 8)
        positions.append((cx, py))
    elif num_planets == 2:
        py = cy - (12 if has_cusps else 8)
        positions.append((cx - 24, py))
        positions.append((cx + 24, py))
    elif num_planets == 3:
        r1_y = cy - (22 if has_cusps else 18)
        r2_y = cy + (12 if has_cusps else 16)
        positions.append((cx - 24, r1_y))
        positions.append((cx + 24, r1_y))
        positions.append((cx, r2_y))
    elif num_planets == 4:
        r1_y = cy - (22 if has_cusps else 18)
        r2_y = cy + (12 if has_cusps else 16)
        positions.append((cx - 24, r1_y))
        positions.append((cx + 24, r1_y))
        positions.append((cx - 24, r2_y))
        positions.append((cx + 24, r2_y))
    elif num_planets == 5:
        r1_y = cy - (22 if has_cusps else 18)
        r2_y = cy + (12 if has_cusps else 16)
        positions.append((cx - 28, r1_y))
        positions.append((cx, r1_y))
        positions.append((cx + 28, r1_y))
        positions.append((cx - 18, r2_y))
        positions.append((cx + 18, r2_y))
    else:
        r1_y = cy - (22 if has_cusps else 18)
        r2_y = cy + (12 if has_cusps else 16)
        positions.append((cx - 28, r1_y))
        positions.append((cx, r1_y))
        positions.append((cx + 28, r1_y))
        positions.append((cx - 28, r2_y))
        positions.append((cx, r2_y))
        positions.append((cx + 28, r2_y))
    return positions

def generate_south_indian(items, mode="symbol"):
    cell_coords = {
        "Pisces": (0, 0), "Aries": (100, 0), "Taurus": (200, 0), "Gemini": (300, 0),
        "Aquarius": (0, 100), "Cancer": (300, 100),
        "Capricorn": (0, 200), "Leo": (300, 200),
        "Sagittarius": (0, 300), "Scorpio": (100, 300), "Libra": (200, 300), "Virgo": (300, 300)
    }

    svg = '<svg width="100%" height="100%" viewBox="0 0 400 400" xmlns="http://www.w3.org/2000/svg" style="background:#FAF5EB; border-radius:8px; border:1px solid #D0C5B4;">\n'
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
            items_by_sign[item["sign"]].append({
                "type": "planet",
                "name": item["name"],
                "sign": item["sign"],
                "deg": f"{item['degree']}°{item['minute']:02d}'",
                "is_retrograde": item.get("is_retrograde", False)
            })

    # Subtle corner sign indicator
    svg += '<g id="si-signs" style="display: block;">\n'
    for sign, (x, y) in cell_coords.items():
        s_sym, s_col, _ = sign_symbols[sign]
        svg += f'<text x="{x+86}" y="{y+15}" font-size="13" font-family="sans-serif" font-weight="bold" fill="{s_col}" opacity="0.85" text-anchor="middle" dominant-baseline="central">{s_sym}</text>\n'
    svg += '</g>\n'

    for sign, (x, y) in cell_coords.items():
        cell_items = items_by_sign[sign]
        planets = [it for it in cell_items if it["type"] == "planet"]
        cusps = [it for it in cell_items if it["type"] == "cusp"]
        
        positions = get_south_indian_positions(len(planets), x, y, has_cusps=bool(cusps))
        
        for idx, p in enumerate(planets):
            if idx >= len(positions):
                break
            px, py = positions[idx]
            info = planet_notations.get(p["name"], {
                "symbol": p["name"][:2],
                "english": p["name"][:2],
                "devanagari": p["name"][:2],
                "translit": p["name"][:2],
                "full_en": p["name"],
                "full_sa": p["name"],
                "color": "#000"
            })
            label = info.get(mode, info["symbol"])
            dev_name = info.get('dev_full', '')
            is_retro = p.get("is_retrograde", False)
            retro_badge = " R" if is_retro else ""
            retro_label = " [Retrograde (R)]" if is_retro else ""
            tooltip = f"{dev_name} / {info['full_sa']} ({info['full_en']}){retro_label} — {p['deg']}{retro_badge} {p['sign']}"
            
            font_sz = "20" if (mode == "symbol" and p["name"] != "Lagna") else ("14" if mode == "devanagari" else "13")
            
            svg += f'<g style="cursor: pointer;"><title>{tooltip}</title>\n'
            svg += f'<text x="{px}" y="{py - 2}" font-family="sans-serif" font-size="{font_sz}" font-weight="bold" fill="{info["color"]}" text-anchor="middle" dominant-baseline="central">{label}</text>\n'
            svg += f'<text x="{px}" y="{py + 15}" font-family="sans-serif" font-size="10" font-weight="normal" fill="#5C4433" text-anchor="middle" dominant-baseline="central">'
            svg += f'<tspan>{p["deg"]}</tspan>'
            if is_retro:
                svg += f'<tspan font-size="9" font-weight="bold" fill="#C0392B"> R</tspan>'
            svg += '</text>\n'
            svg += '</g>\n'
            
        if cusps:
            cusp_texts = [c["text"] for c in cusps]
            cusp_tooltip = f"House Cusps: {', '.join(cusp_texts)} in {sign}"
            svg += f'<g style="cursor: pointer;"><title>{cusp_tooltip}</title>\n'
            svg += f'<text x="{x + 50}" y="{y + 86}" font-family="sans-serif" font-size="12" font-weight="bold" fill="#7D3C98" text-anchor="middle" dominant-baseline="central">{" ".join(cusp_texts)}</text>\n'
            svg += '</g>\n'

    svg += '</svg>\n'
    return svg

def generate_north_indian(items, mode="symbol"):
    svg = '<svg width="100%" height="100%" viewBox="0 0 400 400" xmlns="http://www.w3.org/2000/svg" style="background:#FAF5EB; border-radius:8px; border:1px solid #D0C5B4;">\n'
    svg += '<rect x="0" y="0" width="400" height="400" fill="none" stroke="#5C4433" stroke-width="2"/>\n'
    svg += '<line x1="0" y1="0" x2="400" y2="400" stroke="#5C4433" stroke-width="2"/>\n'
    svg += '<line x1="400" y1="0" x2="0" y2="400" stroke="#5C4433" stroke-width="2"/>\n'
    svg += '<line x1="200" y1="0" x2="400" y2="200" stroke="#5C4433" stroke-width="2"/>\n'
    svg += '<line x1="400" y1="200" x2="200" y2="400" stroke="#5C4433" stroke-width="2"/>\n'
    svg += '<line x1="200" y1="400" x2="0" y2="200" stroke="#5C4433" stroke-width="2"/>\n'
    svg += '<line x1="0" y1="200" x2="200" y2="0" stroke="#5C4433" stroke-width="2"/>\n'

    ni_centers = [
        (200, 100), (100, 45),  (48, 100),  (100, 200),
        (48, 300),  (100, 355), (200, 300), (300, 355),
        (352, 300), (300, 200), (352, 100), (300, 45)
    ]
    sign_pos = [
        (200, 180), (100, 85),  (180, 100), (115, 180),
        (180, 300), (100, 315), (200, 220), (300, 315),
        (220, 300), (285, 180), (220, 100), (300, 85)
    ]

    asc_item = next(it for it in items if it["name"] == "Lagna")
    asc_sign = asc_item["sign"]
    asc_index = signs_list.index(asc_sign)

    items_by_house = [[] for _ in range(12)]
    
    for item in items:
        s_idx = signs_list.index(item["sign"])
        h_idx = (s_idx - asc_index + 12) % 12
        if item.get("type") == "cusp":
            items_by_house[h_idx].append(item)
        else:
            items_by_house[h_idx].append({
                "type": "planet",
                "name": item["name"],
                "sign": item["sign"],
                "deg": f"{item['degree']}°{item['minute']:02d}'",
                "is_retrograde": item.get("is_retrograde", False)
            })

    for h in range(12):
        s_idx = (asc_index + h) % 12
        sign = signs_list[s_idx]
        s_sym, s_col, _ = sign_symbols[sign]
        
        sx, sy = sign_pos[h]
        svg += f'<text x="{sx}" y="{sy}" font-size="14" font-family="sans-serif" fill="{s_col}" opacity="0.85" font-weight="bold" text-anchor="middle" dominant-baseline="central">{s_sym}</text>\n'

        cx, cy = ni_centers[h]
        house_items = items_by_house[h]
        planets = [it for it in house_items if it["type"] == "planet"]
        cusps = [it for it in house_items if it["type"] == "cusp"]
        
        positions = get_north_indian_positions(len(planets), cx, cy, has_cusps=bool(cusps))
        
        for idx, p in enumerate(planets):
            if idx >= len(positions):
                break
            px, py = positions[idx]
            info = planet_notations.get(p["name"], {
                "symbol": p["name"][:2],
                "english": p["name"][:2],
                "devanagari": p["name"][:2],
                "translit": p["name"][:2],
                "full_en": p["name"],
                "full_sa": p["name"],
                "color": "#000"
            })
            label = info.get(mode, info["symbol"])
            font_sz = "20" if (mode == "symbol" and p["name"] != "Lagna") else ("14" if mode == "devanagari" else "13")
            dev_name = info.get('dev_full', '')
            is_retro = p.get("is_retrograde", False)
            retro_badge = " R" if is_retro else ""
            retro_label = " [Retrograde (R)]" if is_retro else ""
            tooltip = f"{dev_name} / {info['full_sa']} ({info['full_en']}){retro_label} — {p['deg']}{retro_badge} {p['sign']}"
            
            svg += f'<g style="cursor: pointer;"><title>{tooltip}</title>\n'
            svg += f'<text x="{px}" y="{py - 2}" text-anchor="middle" dominant-baseline="central" font-family="sans-serif" font-size="{font_sz}" font-weight="bold" fill="{info["color"]}">{label}</text>\n'
            svg += f'<text x="{px}" y="{py + 15}" text-anchor="middle" dominant-baseline="central" font-family="sans-serif" font-size="10" font-weight="normal" fill="#5C4433">'
            svg += f'<tspan>{p["deg"]}</tspan>'
            if is_retro:
                svg += f'<tspan font-size="9" font-weight="bold" fill="#C0392B"> R</tspan>'
            svg += '</text></g>\n'
            
        if cusps:
            cusp_texts = [c["text"] for c in cusps]
            cusp_tooltip = f"House Cusps: {', '.join(cusp_texts)} in {sign}"
            cusp_y = cy + 28 if planets else cy
            svg += f'<g style="cursor: pointer;"><title>{cusp_tooltip}</title>\n'
            svg += f'<text x="{cx}" y="{cusp_y}" font-family="sans-serif" font-size="12" font-weight="bold" fill="#7D3C98" text-anchor="middle" dominant-baseline="central">{" ".join(cusp_texts)}</text>\n'
            svg += '</g>\n'

    svg += '</svg>\n'
    return svg

def generate_bhava_chalita_north(bhavas, mode="symbol"):
    svg = '<svg width="400" height="400" viewBox="0 0 400 400" xmlns="http://www.w3.org/2000/svg" style="background:#FAF5EB; border-radius:8px; border:1px solid #D0C5B4;">\n'
    svg += '<rect x="0" y="0" width="400" height="400" fill="none" stroke="#5C4433" stroke-width="2"/>\n'
    svg += '<line x1="0" y1="0" x2="400" y2="400" stroke="#5C4433" stroke-width="2"/>\n'
    svg += '<line x1="400" y1="0" x2="0" y2="400" stroke="#5C4433" stroke-width="2"/>\n'
    svg += '<line x1="200" y1="0" x2="400" y2="200" stroke="#5C4433" stroke-width="2"/>\n'
    svg += '<line x1="400" y1="200" x2="200" y2="400" stroke="#5C4433" stroke-width="2"/>\n'
    svg += '<line x1="200" y1="400" x2="0" y2="200" stroke="#5C4433" stroke-width="2"/>\n'
    svg += '<line x1="0" y1="200" x2="200" y2="0" stroke="#5C4433" stroke-width="2"/>\n'

    ni_centers = [
        (200, 100), (100, 45),  (48, 100),  (100, 200),
        (48, 300),  (100, 355), (200, 300), (300, 355),
        (352, 300), (300, 200), (352, 100), (300, 45)
    ]
    
    sign_pos = [
        (200, 175), (145, 25),  (25, 145),  (175, 200),
        (25, 255),  (145, 375), (200, 225), (255, 375),
        (375, 255), (225, 200), (375, 145), (255, 25)
    ]
    
    for h_idx in range(12):
        cx, cy = ni_centers[h_idx]
        bhava = bhavas[h_idx]
        
        cusp_lon = bhava["cusp"]
        sign_idx = int(cusp_lon // 30)
        s_sym, s_col, _ = sign_symbols[signs_list[sign_idx]]
        
        sx, sy = sign_pos[h_idx]
        svg += f'<text x="{sx}" y="{sy}" font-size="14" font-family="sans-serif" fill="{s_col}" opacity="0.85" font-weight="bold" text-anchor="middle" dominant-baseline="central">{s_sym}</text>\n'

        items_in_house = bhava["planets"]
        
        item_height = 21
        total_h = len(items_in_house) * item_height
        start_y = cy - (total_h / 2) + (item_height / 2)
        
        curr_y = start_y
        for p_name in items_in_house:
            info = planet_notations.get(p_name, {
                "symbol": p_name[:2],
                "english": p_name[:2],
                "devanagari": p_name[:2],
                "translit": p_name[:2],
                "full_en": p_name,
                "full_sa": p_name,
                "color": "#000"
            })
            label = info.get(mode, info["symbol"])
            font_sz = "24" if (mode == "symbol" and p_name != "Lagna") else ("16" if mode == "devanagari" else "14")
            tooltip = f"{info['full_sa']} ({info['full_en']})"
            
            svg += f'<g style="cursor: pointer;"><title>{tooltip}</title>\n'
            svg += f'<text x="{cx}" y="{curr_y}" text-anchor="middle" dominant-baseline="central" font-family="sans-serif">\n'
            svg += f'  <tspan font-size="{font_sz}" font-weight="bold" fill="{info["color"]}">{label}</tspan>\n'
            svg += f'</text></g>\n'
            curr_y += item_height

    svg += "</svg>\n"
    return svg
