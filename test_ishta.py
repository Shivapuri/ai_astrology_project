from datetime import datetime
import jyotish.generate_jyotish as gj
import jyotish.shadbala.shadbala as sb
from jyotish.astronomy import calculate_planetary_positions

res = gj.generate_kala_chart(
    name="Shivapuri",
    year=1983,
    month=11,
    day=10,
    hour=22,
    minute=20,
    latitude=52.20296,
    longitude=8.0448,
    timezone_offset=1.0
)
jd = res["astronomy"]["julian_day"]
pl_pos, _ = calculate_planetary_positions(jd)

for p, data in res["shadbala"].items():
    if p in ["Total_Virupas", "Total_Rupas"]: continue
    lon = pl_pos[p]
    uccha = sb.calculate_uccha_bala(p, lon)
    print(f"{p}: Uccha={uccha}, Cheshta={data.get('Cheshta_Bala')}")
