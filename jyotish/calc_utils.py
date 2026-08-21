import swisseph as swe
import scipy.optimize as opt

def get_moon_lat(jd):
    res, _ = swe.calc_ut(jd, swe.MOON, swe.FLG_SWIEPH)
    return res[1]

def get_moon_lon(jd):
    res, _ = swe.calc_ut(jd, swe.MOON, swe.FLG_SWIEPH)
    return res[0]

def calculate_interpolated_node(target_jd):
    """
    Calculates Ernst Wilhelm's 'Interpolated True Node'.
    This is found by determining the exact moments of the Moon's previous and next 
    ecliptic crossings (where latitude = 0) and linearly interpolating the node's 
    longitude between those two points.
    """
    jd = target_jd
    while get_moon_lat(jd) * get_moon_lat(jd - 1) > 0:
        jd -= 1
    t1 = opt.brentq(get_moon_lat, jd - 1, jd)

    jd = target_jd
    while get_moon_lat(jd) * get_moon_lat(jd + 1) > 0:
        jd += 1
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

    # Handle 360 degree wrap around
    if rahu_1 - rahu_2 > 180:
        rahu_2 += 360
    elif rahu_2 - rahu_1 > 180:
        rahu_1 += 360

    fraction = (target_jd - t1) / (t2 - t1)
    interp_rahu = rahu_1 + fraction * (rahu_2 - rahu_1)
    return interp_rahu % 360.0

