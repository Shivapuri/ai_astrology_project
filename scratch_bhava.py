import swisseph as swe

swe.set_ephe_path('cache')

jd = swe.julday(1983, 11, 10, 21.333333333333332)
lat = 52.202961
lon = 8.0448

# Calculate Campanus Houses
cusps, ascmc = swe.houses(jd, lat, lon, b'C')

bhavas = []
for i in range(12):
    prev_cusp = cusps[(i - 1) % 12]
    curr_cusp = cusps[i]
    next_cusp = cusps[(i + 1) % 12]
    
    # Calculate start (midpoint of prev and curr)
    diff_prev = (curr_cusp - prev_cusp) % 360
    start = (prev_cusp + diff_prev / 2.0) % 360
    
    # Calculate end (midpoint of curr and next)
    diff_next = (next_cusp - curr_cusp) % 360
    end = (curr_cusp + diff_next / 2.0) % 360
    
    bhavas.append({
        "house": i + 1,
        "start": start,
        "cusp": curr_cusp,
        "end": end
    })

planets = {
    "Asc": ascmc[0],
    "Sun": 227.9139,
    "Moon": 298.578,
    "Mars": 175.5362,
    "Venus": 181.497,
    "Mercury": 234.5999,
    "Jupiter": 254.4802,
    "Saturn": 218.5238,
    "Rahu": 76.0859,
    "Ketu": 256.0859
}

for b in bhavas:
    in_house = []
    for p, p_lon in planets.items():
        if b["start"] < b["end"]:
            if b["start"] <= p_lon < b["end"]:
                in_house.append(p)
        else: # wraps around 360
            if p_lon >= b["start"] or p_lon < b["end"]:
                in_house.append(p)
    print(f'House {b["house"]}: Start {b["start"]:.2f}, Cusp {b["cusp"]:.2f}, End {b["end"]:.2f} -> {in_house}')
