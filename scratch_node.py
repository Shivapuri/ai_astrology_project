import swisseph as swe
import scipy.optimize as opt
from datetime import datetime, timedelta

def get_moon_lat(jd):
    res, _ = swe.calc_ut(jd, swe.MOON, swe.FLG_SWIEPH)
    return res[1] # latitude

def get_moon_lon(jd):
    res, _ = swe.calc_ut(jd, swe.MOON, swe.FLG_SWIEPH)
    return res[0]

year, month, day, hour, minute = 1983, 11, 10, 22, 20
utc_dt = datetime(year, month, day, hour, minute) - timedelta(hours=1.0)
utc_hour_fraction = utc_dt.hour + utc_dt.minute / 60.0
target_jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, utc_hour_fraction)

# Find previous crossing (t1) and next crossing (t2)
# Moon period is ~27.3 days, crossing every ~13.6 days.
# Step back day by day until sign of latitude changes
jd = target_jd
while get_moon_lat(jd) * get_moon_lat(jd - 1) > 0:
    jd -= 1

# Root finding for exact t1
t1 = opt.brentq(get_moon_lat, jd - 1, jd)

jd = target_jd
while get_moon_lat(jd) * get_moon_lat(jd + 1) > 0:
    jd += 1
    
# Root finding for exact t2
t2 = opt.brentq(get_moon_lat, jd, jd + 1)

lat_before_t1 = get_moon_lat(t1 - 0.1)
is_ascending_t1 = lat_before_t1 < 0

lat_before_t2 = get_moon_lat(t2 - 0.1)
is_ascending_t2 = lat_before_t2 < 0

def get_rahu_at_crossing(t, is_asc):
    moon_lon = get_moon_lon(t)
    if is_asc:
        return moon_lon
    else:
        return (moon_lon + 180.0) % 360.0

rahu_1 = get_rahu_at_crossing(t1, is_ascending_t1)
rahu_2 = get_rahu_at_crossing(t2, is_ascending_t2)

# Handle wrap around
if rahu_1 - rahu_2 > 180:
    rahu_2 += 360
elif rahu_2 - rahu_1 > 180:
    rahu_1 += 360

fraction = (target_jd - t1) / (t2 - t1)
interp_rahu = rahu_1 + fraction * (rahu_2 - rahu_1)
interp_rahu %= 360.0

print(f"Interpolated Rahu: {interp_rahu}")
def to_dms(deg):
    d = int(deg % 30)
    m = int(((deg % 30) - d) * 60)
    return d, m
print(f"Interpolated Rahu (DMS): {to_dms(interp_rahu)}")

