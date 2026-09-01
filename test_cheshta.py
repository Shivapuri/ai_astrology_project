import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from jyotish.generate_jyotish import generate_kala_chart

chart = generate_kala_chart(
    name="Angelina", year=1975, month=6, day=4,
    hour=9, minute=9, latitude=34.0522, longitude=-118.2437, timezone_offset=-7.0
)
print("Planets:", chart['planet_positions']['D1'])
print("Sun Geo:", chart['planet_positions']['D1']['Sun'])
