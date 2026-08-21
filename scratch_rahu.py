import swisseph as swe
from datetime import datetime, timedelta

year, month, day, hour, minute = 1983, 11, 10, 22, 20
dt = datetime(year, month, day, hour, minute)
utc_dt = dt - timedelta(hours=1.0)
utc_hour_fraction = utc_dt.hour + utc_dt.minute / 60.0
jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, utc_hour_fraction)

res_true, _ = swe.calc_ut(jd, swe.TRUE_NODE, swe.FLG_SWIEPH)
res_mean, _ = swe.calc_ut(jd, swe.MEAN_NODE, swe.FLG_SWIEPH)

print(f"True Node float: {res_true[0]}")
print(f"Mean Node float: {res_mean[0]}")

