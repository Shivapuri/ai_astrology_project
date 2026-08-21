import swisseph as swe
from datetime import datetime, timedelta
jd = swe.julday(1983, 11, 10, 21.333333333333332)
cusps, ascmc = swe.houses(jd, 52.202961, 8.0448, b'P')
print(f"Length of cusps: {len(cusps)}")
for i, c in enumerate(cusps):
    print(f"Index {i}: {c:.4f}")
