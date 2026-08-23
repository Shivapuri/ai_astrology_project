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
    for i, cusp in enumerate(varga_data.get("cusps", [])):
        c_deg = cusp.get("degree_0_to_30", 0)
        items.append({
            "type": "cusp",
            "text": str(i + 1),
            "sign": cusp["sign"],
            "degree": int(c_deg),
            "minute": int((c_deg - int(c_deg)) * 60),
            "longitude": cusp.get("longitude", 0),
            "color": "#7d3c98"
        })
        
    return items

def get_south_indian_positions(num_planets, cell_x, cell_y, has_cusps=False):
    positions = []
    if num_planets == 1:
        positions.append((cell_x + 50, cell_y + 44))
    elif num_planets == 2:
        positions.append((cell_x + 30, cell_y + 44))
        positions.append((cell_x + 70, cell_y + 44))
    elif num_planets == 3:
        positions.append((cell_x + 30, cell_y + 35))
        positions.append((cell_x + 70, cell_y + 35))
        positions.append((cell_x + 50, cell_y + 65))
    elif num_planets == 4:
        positions.append((cell_x + 30, cell_y + 35))
        positions.append((cell_x + 70, cell_y + 35))
        positions.append((cell_x + 30, cell_y + 65))
        positions.append((cell_x + 70, cell_y + 65))
    elif num_planets == 5:
        positions.append((cell_x + 20, cell_y + 35))
        positions.append((cell_x + 50, cell_y + 35))
        positions.append((cell_x + 80, cell_y + 35))
        positions.append((cell_x + 35, cell_y + 65))
        positions.append((cell_x + 65, cell_y + 65))
    elif num_planets == 6:
        positions.append((cell_x + 20, cell_y + 35))
        positions.append((cell_x + 50, cell_y + 35))
        positions.append((cell_x + 80, cell_y + 35))
        positions.append((cell_x + 20, cell_y + 65))
        positions.append((cell_x + 50, cell_y + 65))
        positions.append((cell_x + 80, cell_y + 65))
    elif num_planets == 7:
        positions.append((cell_x + 20, cell_y + 25))
        positions.append((cell_x + 50, cell_y + 25))
        positions.append((cell_x + 80, cell_y + 25))
        positions.append((cell_x + 35, cell_y + 50))
        positions.append((cell_x + 65, cell_y + 50))
        positions.append((cell_x + 30, cell_y + 75))
        positions.append((cell_x + 70, cell_y + 75))
    else:
        positions.append((cell_x + 20, cell_y + 25))
        positions.append((cell_x + 50, cell_y + 25))
        positions.append((cell_x + 80, cell_y + 25))
        positions.append((cell_x + 20, cell_y + 50))
        positions.append((cell_x + 50, cell_y + 50))
        positions.append((cell_x + 80, cell_y + 50))
        positions.append((cell_x + 35, cell_y + 75))
        positions.append((cell_x + 65, cell_y + 75))
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
        r1_y = cy - (20 if has_cusps else 16)
        r2_y = cy + (14 if has_cusps else 18)
        positions.append((cx - 22, r1_y))
        positions.append((cx, r1_y))
        positions.append((cx + 22, r1_y))
        positions.append((cx - 14, r2_y))
        positions.append((cx + 14, r2_y))
    else:
        r1_y = cy - (20 if has_cusps else 16)
        r2_y = cy + (14 if has_cusps else 18)
        positions.append((cx - 22, r1_y))
        positions.append((cx, r1_y))
        positions.append((cx + 22, r1_y))
        positions.append((cx - 22, r2_y))
        positions.append((cx, r2_y))
        positions.append((cx + 22, r2_y))
    return positions

def generate_south_indian(items, mode="symbol", varga_name="D1"):
    cell_coords = {
        "Pisces": (0, 0), "Aries": (100, 0), "Taurus": (200, 0), "Gemini": (300, 0),
        "Aquarius": (0, 100), "Cancer": (300, 100),
        "Capricorn": (0, 200), "Leo": (300, 200),
        "Sagittarius": (0, 300), "Scorpio": (100, 300), "Libra": (200, 300), "Virgo": (300, 300)
    }

    svg = '<svg width="100%" height="100%" viewBox="-10 -10 420 420" preserveAspectRatio="xMidYMid meet" xmlns="http://www.w3.org/2000/svg" style="background:transparent;">\n'
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
    
    # Center Chart Title
    svg += f'<text x="200" y="190" font-family="sans-serif" font-size="18" font-weight="bold" fill="#4a3325" text-anchor="middle">{varga_name}</text>\n'
    svg += f'<text x="200" y="215" font-family="sans-serif" font-size="13" fill="#8c7b64" text-anchor="middle">Tropical South Indian</text>\n'

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
        cell_items = items_by_sign[sign]
        planets = [it for it in cell_items if it["type"] == "planet"]
        cusps = [it for it in cell_items if it["type"] == "cusp"]
        
        c_dx, c_dy, s_dx, s_dy = quadrant_map[sign]
        
        # Draw Rasi Sign (Inner Corner)
        s_sym, s_col, _ = sign_symbols[sign]
        svg += f'<text class="interactive" data-type="sign" data-id="{sign}" x="{x + s_dx}" y="{y + s_dy}" font-size="14" font-family="sans-serif" font-weight="bold" fill="{s_col}" opacity="0.85" text-anchor="middle" dominant-baseline="central" style="cursor: pointer;">{s_sym}</text>\n'

        # Draw House Cusps (Outer Corner)
        if cusps:
            cusp_texts = [c["text"] for c in cusps]
            cusp_tooltip = f"House Cusps: {', '.join(cusp_texts)} in {sign}"
            svg += f'<g class="interactive" data-type="house" data-id="{cusp_texts[0]}" style="cursor: pointer;"><title>{cusp_tooltip}</title>\n'
            
            if len(cusp_texts) > 3:
                mid = len(cusp_texts) // 2
                l1 = " ".join(cusp_texts[:mid])
                l2 = " ".join(cusp_texts[mid:])
                svg += f'<text x="{x + c_dx}" y="{y + c_dy - 6}" font-family="sans-serif" font-size="12" font-weight="bold" fill="#7D3C98" text-anchor="middle" dominant-baseline="central">{l1}</text>\n'
                svg += f'<text x="{x + c_dx}" y="{y + c_dy + 6}" font-family="sans-serif" font-size="12" font-weight="bold" fill="#7D3C98" text-anchor="middle" dominant-baseline="central">{l2}</text>\n'
            else:
                svg += f'<text x="{x + c_dx}" y="{y + c_dy}" font-family="sans-serif" font-size="12" font-weight="bold" fill="#7D3C98" text-anchor="middle" dominant-baseline="central">{" ".join(cusp_texts)}</text>\n'
                
            svg += '</g>\n'

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
            
            svg += f'<g class="interactive" data-type="planet" data-id="{p["name"]}" style="cursor: pointer;"><title>{tooltip}</title>\n'
            svg += f'<text x="{px}" y="{py - 2}" font-family="sans-serif" font-size="{font_sz}" font-weight="bold" fill="{info["color"]}" text-anchor="middle" dominant-baseline="central">{label}</text>\n'
            svg += f'<text x="{px}" y="{py + 15}" font-family="sans-serif" font-size="10" font-weight="normal" fill="#5C4433" text-anchor="middle" dominant-baseline="central">'
            svg += f'<tspan>{p["deg"]}</tspan>'
            if is_retro:
                svg += f'<tspan font-size="9" font-weight="bold" fill="#C0392B"> R</tspan>'
            svg += '</text>\n'
            svg += '</g>\n'
            
        # (Cusps are now drawn at the beginning of the cell block in the outer corner)

    svg += '</svg>\n'
    return svg

def generate_north_indian(items, mode="symbol", varga_name="D1"):
    svg = '<svg width="100%" height="100%" viewBox="-10 -10 420 420" preserveAspectRatio="xMidYMid meet" xmlns="http://www.w3.org/2000/svg" style="background:transparent;">\n'
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
        svg += f'<text class="interactive" data-type="sign" data-id="{sign}" x="{sx}" y="{sy}" font-size="14" font-family="sans-serif" fill="{s_col}" opacity="0.85" font-weight="bold" text-anchor="middle" dominant-baseline="central" style="cursor: pointer;">{s_sym}</text>\n'

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
            if len(planets) > 4:
                font_sz = "16" if (mode == "symbol" and p["name"] != "Lagna") else ("12" if mode == "devanagari" else "11")
                deg_sz = "9"
                retro_sz = "8"
            else:
                font_sz = "20" if (mode == "symbol" and p["name"] != "Lagna") else ("14" if mode == "devanagari" else "13")
                deg_sz = "10"
                retro_sz = "9"
                
            dev_name = info.get('dev_full', '')
            is_retro = p.get("is_retrograde", False)
            retro_badge = " R" if is_retro else ""
            retro_label = " [Retrograde (R)]" if is_retro else ""
            tooltip = f"{dev_name} / {info['full_sa']} ({info['full_en']}){retro_label} — {p['deg']}{retro_badge} {p['sign']}"
            
            svg += f'<g class="interactive" data-type="planet" data-id="{p["name"]}" style="cursor: pointer;"><title>{tooltip}</title>\n'
            svg += f'<text x="{px}" y="{py - 2}" text-anchor="middle" dominant-baseline="central" font-family="sans-serif" font-size="{font_sz}" font-weight="bold" fill="{info["color"]}">{label}</text>\n'
            svg += f'<text x="{px}" y="{py + 15}" text-anchor="middle" dominant-baseline="central" font-family="sans-serif" font-size="{deg_sz}" font-weight="normal" fill="#5C4433">'
            svg += f'<tspan>{p["deg"]}</tspan>'
            if is_retro:
                svg += f'<tspan font-size="{retro_sz}" font-weight="bold" fill="#C0392B"> R</tspan>'
            svg += '</text></g>\n'
            
        if cusps:
            cusp_texts = [c["text"] for c in cusps]
            cusp_tooltip = f"House Cusps: {', '.join(cusp_texts)} in {sign}"
            cusp_y = cy + 28 if planets else cy
            svg += f'<g class="interactive" data-type="house" data-id="{cusp_texts[0]}" style="cursor: pointer;"><title>{cusp_tooltip}</title>\n'
            svg += f'<text x="{cx}" y="{cusp_y}" font-family="sans-serif" font-size="12" font-weight="bold" fill="#7D3C98" text-anchor="middle" dominant-baseline="central">{" ".join(cusp_texts)}</text>\n'
            svg += '</g>\n'

    svg += '</svg>\n'
    return svg

def generate_bhava_chalita_north(bhavas, mode="symbol"):
    svg = '<svg width="100%" height="100%" viewBox="-10 -10 420 420" preserveAspectRatio="xMidYMid meet" xmlns="http://www.w3.org/2000/svg" style="background:transparent;">\n'
    svg += '<rect x="0" y="0" width="400" height="400" fill="none" stroke="#5C4433" stroke-width="2"/>\n'
    svg += '<line x1="0" y1="0" x2="400" y2="400" stroke="#5C4433" stroke-width="2"/>\n'
    svg += '<line x1="400" y1="0" x2="0" y2="400" stroke="#5C4433" stroke-width="2"/>\n'
    svg += '<line x1="200" y1="0" x2="400" y2="200" stroke="#5C4433" stroke-width="2"/>\n'
    svg += '<line x1="400" y1="200" x2="200" y2="400" stroke="#5C4433" stroke-width="2"/>\n'
    svg += '<line x1="200" y1="400" x2="0" y2="200" stroke="#5C4433" stroke-width="2"/>\n'
    svg += '<line x1="0" y1="200" x2="200" y2="0" stroke="#5C4433" stroke-width="2"/>\n'
    
    # ... rest remains unmodified for bhava_chalita
    
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
        svg += f'<text class="interactive" data-type="sign" data-id="{signs_list[sign_idx]}" x="{sx}" y="{sy}" font-size="14" font-family="sans-serif" fill="{s_col}" opacity="0.85" font-weight="bold" text-anchor="middle" dominant-baseline="central" style="cursor: pointer;">{s_sym}</text>\n'

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
            
            svg += f'<g class="interactive" data-type="planet" data-id="{p_name}" style="cursor: pointer;"><title>{tooltip}</title>\n'
            svg += f'<text x="{cx}" y="{curr_y}" text-anchor="middle" dominant-baseline="central" font-family="sans-serif">\n'
            svg += f'  <tspan font-size="{font_sz}" font-weight="bold" fill="{info["color"]}">{label}</tspan>\n'
            svg += f'</text></g>\n'
            curr_y += item_height

    svg += "</svg>\n"
    return svg


import math

def generate_circular_chart(items, mode="symbol", varga_name="D1", ayanamsha=0):
    svg = '<svg width="100%" height="100%" viewBox="-210 -210 420 420" preserveAspectRatio="xMidYMid meet" xmlns="http://www.w3.org/2000/svg" style="background:transparent; font-family: sans-serif;">\n'
    
    r_nak_outer = 200
    r_nak_inner = 175
    r_rasi_inner = 155
    r_bhava_outer = 60
    r_bhava_inner = 45
    
    # Outer house circuits a little bit thinner
    circle_stroke = "0.7"
    svg += f'<circle cx="0" cy="0" r="{r_nak_outer}" fill="none" stroke="#5C4433" stroke-width="{circle_stroke}"/>\n'
    svg += f'<circle cx="0" cy="0" r="{r_nak_inner}" fill="none" stroke="#5C4433" stroke-width="{circle_stroke}"/>\n'
    svg += f'<circle cx="0" cy="0" r="{r_rasi_inner}" fill="none" stroke="#5C4433" stroke-width="{circle_stroke}"/>\n'
    svg += f'<circle cx="0" cy="0" r="{r_bhava_outer}" fill="none" stroke="#27AE60" stroke-width="{circle_stroke}"/>\n'
    svg += f'<circle cx="0" cy="0" r="{r_bhava_inner}" fill="none" stroke="#000000" stroke-width="{circle_stroke}"/>\n'
    
    asc_item = next((it for it in items if it["name"] == "Lagna"), None)
    if asc_item:
        asc_s_idx = signs_list.index(asc_item["sign"])
        asc_lon = asc_s_idx * 30 + asc_item["degree"] + asc_item["minute"] / 60.0
    else:
        asc_s_idx = 0
        asc_lon = 0
            
    def lon_to_angle(lon):
        return 180 + asc_lon - lon

    def polar_coords(r, angle_deg):
        rad = math.radians(angle_deg)
        return r * math.cos(rad), r * math.sin(rad)

    # 1. Nakshatras
    nak_names = ["Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", 
                 "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni", 
                 "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha", 
                 "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha", 
                 "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"]
                 
    for i in range(27):
        start_lon = ayanamsha + i * (360.0 / 27.0)
        angle_start = lon_to_angle(start_lon)
        angle_mid = lon_to_angle(start_lon + (360.0 / 54.0))
        
        x1, y1 = polar_coords(r_nak_inner, angle_start)
        x2, y2 = polar_coords(r_nak_outer, angle_start)
        svg += f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#5C4433" stroke-width="0.5" stroke-dasharray="2,2"/>\n'
        
        lx, ly = polar_coords( (r_nak_inner + r_nak_outer)/2, angle_mid)
        rot = angle_mid if (angle_mid % 360) > 90 and (angle_mid % 360) < 270 else angle_mid + 180
        svg += f'<text class="interactive" data-type="nakshatra" data-id="{nak_names[i]}" x="{lx}" y="{ly}" font-size="7" fill="#5C4433" text-anchor="middle" dominant-baseline="central" transform="rotate({rot} {lx} {ly})" style="cursor: pointer;">{nak_names[i][:4]}.</text>\n'

    # 2 & 3. Tropical Rasis and Bhavas (Whole Signs)
    for i in range(12):
        start_lon = i * 30.0
        angle_start = lon_to_angle(start_lon)
        angle_mid = lon_to_angle(start_lon + 15.0)
        
        # Draw Rasi separator line
        x1, y1 = polar_coords(r_rasi_inner, angle_start)
        x2, y2 = polar_coords(r_nak_inner, angle_start)
        svg += f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#5C4433" stroke-width="1"/>\n'
        
        # Whole House boundaries (Bhavas) - Green dense dashed line
        x3, y3 = polar_coords(r_bhava_outer, angle_start)
        x4, y4 = polar_coords(r_rasi_inner, angle_start)
        svg += f'<line x1="{x3}" y1="{y3}" x2="{x4}" y2="{y4}" stroke="#27AE60" stroke-width="0.8" stroke-dasharray="3,2"/>\n'
        
        # Bhava inner circle separator
        x5, y5 = polar_coords(r_bhava_inner, angle_start)
        x6, y6 = polar_coords(r_bhava_outer, angle_start)
        svg += f'<line x1="{x5}" y1="{y5}" x2="{x6}" y2="{y6}" stroke="#000000" stroke-width="1"/>\n'
        
        # Rasi symbol label
        lx, ly = polar_coords( (r_rasi_inner + r_nak_inner)/2, angle_mid)
        sign_name = signs_list[i]
        s_sym, s_col, _ = sign_symbols[sign_name]
        svg += f'<text class="interactive" data-type="sign" data-id="{sign_name}" x="{lx}" y="{ly}" font-size="14" fill="{s_col}" text-anchor="middle" dominant-baseline="central" style="cursor: pointer;">{s_sym}</text>\n'

        
        # Bhava number label (Whole Sign)
        bhava_num = (i - asc_s_idx + 12) % 12 + 1
        bx, by = polar_coords( (r_bhava_inner + r_bhava_outer)/2, angle_mid)
        svg += f'<text class="interactive" data-type="house" data-id="{bhava_num}" x="{bx}" y="{by}" font-size="9" fill="#2980B9" text-anchor="middle" dominant-baseline="central" style="cursor: pointer;">{bhava_num}</text>\n'

    # 4. House Cusps (Campanus lines) - Violet spread dash, Red for solar stations
    cusps = [it for it in items if it.get("type") == "cusp"]
    if cusps and len(cusps) >= 12:
        for i in range(12):
            c = cusps[i]
            house_num = i + 1
            lon = c.get("longitude")
            if lon is None:
                s_idx = signs_list.index(c["sign"])
                lon = s_idx * 30 + c["degree"] + c["minute"] / 60.0
                
            angle_start = lon_to_angle(lon)
            
            x1, y1 = polar_coords(r_bhava_outer, angle_start)
            x2, y2 = polar_coords(r_rasi_inner, angle_start)
            
            is_angle = house_num in [1, 4, 7, 10]
            if is_angle:
                # Red for solar stations, not so thick
                color = "#C0392B"
                thickness = "1.0"
                dash = ""
            else:
                # Violet, thin, spreaded dash
                color = "#8E44AD"
                thickness = "0.5"
                dash = 'stroke-dasharray="2,6"'
            
            
            # Draw cusp number closer to center
            cx, cy = polar_coords(r_bhava_outer + 12, angle_start)
            fw = "bold" if is_angle else "normal"
            fs = "12" if is_angle else "10"
            
            # For Ascendant (house 1), draw a red arrow from inner house border to inner sign border
            if house_num == 1:
                # Line from r_bhava_outer to r_rasi_inner
                ax1, ay1 = polar_coords(r_bhava_outer, angle_start)
                ax2, ay2 = polar_coords(r_rasi_inner, angle_start)
                svg += f'<line x1="{ax1}" y1="{ay1}" x2="{ax2}" y2="{ay2}" stroke="#C0392B" stroke-width="1.5" />\n'
                # Arrowhead at r_rasi_inner (touching inner sign border)
                tx1, ty1 = polar_coords(r_rasi_inner - 6, angle_start - 2)
                tx2, ty2 = polar_coords(r_rasi_inner - 6, angle_start + 2)
                svg += f'<polygon points="{ax2},{ay2} {tx1},{ty1} {tx2},{ty2}" fill="#C0392B" />\n'
                
            # Draw the number for all cusps (except maybe 1 if they don't want it, but let's draw it anyway or skip 1)
            if house_num != 1:
                svg += f'<text x="{cx}" y="{cy}" font-size="{fs}" font-weight="{fw}" fill="{color}" text-anchor="middle" dominant-baseline="central">{house_num}</text>\n'


    # 5. Planets (radially stacked)
    planets_to_draw = []
    for item in items:
        if item.get("type") == "planet":
            s_idx = signs_list.index(item["sign"])
            pl_lon = s_idx * 30 + item["degree"] + item["minute"] / 60.0
            planets_to_draw.append({"item": item, "lon": pl_lon, "draw_angle": lon_to_angle(pl_lon)})
            
    # Relaxation for overlap (MIN_SEP degrees)
    MIN_SEP = 4.5
    for _ in range(30):
        planets_to_draw.sort(key=lambda p: (p["draw_angle"] % 360))
        for i in range(len(planets_to_draw)):
            p1 = planets_to_draw[i]
            p2 = planets_to_draw[(i+1) % len(planets_to_draw)]
            
            a1 = p1["draw_angle"] % 360
            a2 = p2["draw_angle"] % 360
            
            diff = (a2 - a1) % 360
            if diff < MIN_SEP:
                push = (MIN_SEP - diff) / 2.0
                p1["draw_angle"] -= push
                p2["draw_angle"] += push

    r_pl_base = r_rasi_inner - 12

    for p in planets_to_draw:
        item = p["item"]
        angle = p["draw_angle"]
        
        p_name = item["name"]
        info = planet_notations.get(p_name, {})
        label = info.get(mode, info.get("symbol", p_name[:2]))
        color = info.get("color", "#000")
        
        is_retro = item.get("is_retrograde", False)
        retro_badge = "R" if is_retro else ""
        s_sym, s_col, _ = sign_symbols[item["sign"]]
        
        if p_name == "Lagna":
            # Lagna is exactly at 180 degrees (left horizontal axis).
            # Shift the angle slightly so the entire stack draws below the red arrow line.
            angle = (angle + 2.2) % 360
            
        px, py = polar_coords(r_pl_base, angle)

        font_sz = 10 if p_name == "Lagna" else 13
        
        tooltip = f"{info.get('full_sa', p_name)} — {item['degree']}° {s_sym} {item['minute']:02d}'{retro_badge} {item['sign']}"
        svg += f'<g class="interactive" data-type="planet" data-id="{p_name}" style="cursor: pointer;"><title>{tooltip}</title>\n'

        


        # Planet Glyph
        svg += f'<text x="{px}" y="{py}" font-size="{font_sz}" stroke="#F7F3EB" stroke-width="2" paint-order="stroke" stroke-linejoin="round" fill="{color}" font-weight="bold" text-anchor="middle" dominant-baseline="central">{label}</text>\n'
            
        r_deg_base = r_rasi_inner - 26 if p_name == 'Lagna' else r_rasi_inner - 22
        r_sign_base = r_rasi_inner - 40 if p_name == 'Lagna' else r_rasi_inner - 32
        r_min_base = r_rasi_inner - 52 if p_name == 'Lagna' else r_rasi_inner - 42
        
        dx, dy = polar_coords(r_deg_base, angle)
        svg += f'<text x="{dx}" y="{dy}" font-size="7" stroke="#F7F3EB" stroke-width="1.5" paint-order="stroke" stroke-linejoin="round" fill="{color}" text-anchor="middle" dominant-baseline="central">{item["degree"]}°</text>\n'
        
        sx, sy = polar_coords(r_sign_base, angle)
        svg += f'<text x="{sx}" y="{sy}" font-size="9" stroke="#F7F3EB" stroke-width="1.5" paint-order="stroke" stroke-linejoin="round" fill="{s_col}" text-anchor="middle" dominant-baseline="central">{s_sym}</text>\n'
        
        mx, my = polar_coords(r_min_base, angle)
        svg += f'<text x="{mx}" y="{my}" font-size="6" stroke="#F7F3EB" stroke-width="1.5" paint-order="stroke" stroke-linejoin="round" fill="{color}" text-anchor="middle" dominant-baseline="central">{item["minute"]:02d}\'{retro_badge}</text>\n'
        
        svg += f'</g>\n'
        
        true_angle = lon_to_angle(p["lon"])
        if abs((angle - true_angle) % 360) > 0.5 and abs((angle - true_angle) % 360) < 359.5:
            cx, cy = polar_coords(r_rasi_inner, true_angle)
            svg += f'<line x1="{px}" y1="{py}" x2="{cx}" y2="{cy}" stroke="{color}" stroke-width="0.5" opacity="0.3"/>\n'

    svg += '</svg>\n'
    return svg

