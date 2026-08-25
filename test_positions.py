import jyotish.generate_jyotish as gj
res = gj.generate_kala_chart("Shivapuri", year=1983, month=11, day=10, hour=22, minute=20, latitude=52.2, longitude=8.0, timezone_offset=1.0)
for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
    print(f"{p}: {res['vargas']['D1']['grahas'][p]['sign']} {res['vargas']['D1']['grahas'][p]['degree_0_to_30']}")
