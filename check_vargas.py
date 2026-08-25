import json
from jyotish.generate_jyotish import generate_kala_chart

chart = generate_kala_chart(
    name="Shiva",
    year=1983,
    month=11,
    day=12,
    hour=22,
    minute=20,
    latitude=52.2, # 52N12'00" = 52 + 12/60 = 52.2
    longitude=8.05, # 008E03'00" = 8 + 3/60 = 8.05
    timezone_offset=1.0, # -1 hour from Kala corresponds to UTC+1
)

with open("shiva_chart.json", "w") as f:
    json.dump(chart, f, indent=4)
