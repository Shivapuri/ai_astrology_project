import swisseph as swe
from datetime import datetime, timedelta

year, month, day, hour, minute = 1983, 11, 10, 22, 20
utc_dt = datetime(year, month, day, hour, minute) - timedelta(hours=1.0)
utc_hour_fraction = utc_dt.hour + utc_dt.minute / 60.0
jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, utc_hour_fraction)

eps = swe.calc_ut(jd, swe.ECL_NUT, 0)[0][0] # true obliquity

cusps, ascmc = swe.houses(jd, 52.2036, 8.0442, b'P')
asc_lon = ascmc[0]

res = swe.cotrans([asc_lon, 0.0, 1.0], -eps) # to equatorial

ra_gc = 266.0
try:
    flags_equatorial = swe.FLG_SWIEPH | swe.FLG_EQUATORIAL
    res_gc, name_gc, _ = swe.fixstar2_ut("Galactic Center", jd, flags_equatorial)
    ra_gc = res_gc[0]
except:
    pass

ayanamsa_eq = ra_gc - 246.6667
sid_ra = (res[0] - ayanamsa_eq) % 360.0

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishtha", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

idx = int(sid_ra / 13.33333333)
pada = int((sid_ra % 13.33333333) / 3.33333333) + 1
print(f"Nakshatra: {NAKSHATRAS[idx]}, Pada: {pada}")

