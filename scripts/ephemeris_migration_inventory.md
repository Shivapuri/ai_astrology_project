# Astra Ephemeris Migration Inventory

Total Files Affected: **2**  
Total Direct Calls: **12**  

> **Note:** All calls listed below must be decoupled and replaced with direct reads from `ChartBaseline`.

### `generate_nakshatra_preview.py`

| Line | Type | Current Code | Baseline Replacement |
| :---: | :--- | :--- | :--- |
| 499 | `calculate_varga_longitude` | `div_v_lon = calculate_varga_longitude(div_mid_lon, "D9")` | `baseline.vargas[varga_name]['grahas'][planet]['longitude']` |

### `search_krishna_chart.py`

| Line | Type | Current Code | Baseline Replacement |
| :---: | :--- | :--- | :--- |
| 30 | `swisseph` | `import swisseph as swe` | `from jyotish.baseline import ChartBaseline` |
| 40 | `swe.set_ephe_path` | `swe.set_ephe_path(EPHE_PATH)` | `baseline.<property>` |
| 99 | `swe.houses` | `cusps, ascmc = swe.houses(jd, MATHURA_LAT, MATHURA_LON, b'C')` | `baseline.astronomical_anchors['asc_longitude'\|'mc_longitude'\|'campanus_display_cusps']` |
| 107 | `swe.calc_ut` | `res, _ = swe.calc_ut(jd, pid)` | `baseline.coordinates[planet]['longitude'\|'latitude'\|'speed'] or ['declination'\|'right_ascension']` |
| 192 | `swe.julday` | `jd_mid = swe.julday(y, 7, 1, 0, swe.JUL_CAL)` | `baseline.astronomical_anchors['jd_utc'\|'jd_local']` |
| 193 | `swe.calc_ut` | `sat_lon = swe.calc_ut(jd_mid, swe.SATURN)[0][0] % 360.0` | `baseline.coordinates[planet]['longitude'\|'latitude'\|'speed'] or ['declination'\|'right_ascension']` |
| 194 | `swe.calc_ut` | `jup_lon = swe.calc_ut(jd_mid, swe.JUPITER)[0][0] % 360.0` | `baseline.coordinates[planet]['longitude'\|'latitude'\|'speed'] or ['declination'\|'right_ascension']` |
| 213 | `swe.julday` | `jd = swe.julday(y, m, d, 18.5, swe.JUL_CAL)` | `baseline.astronomical_anchors['jd_utc'\|'jd_local']` |
| 217 | `swe.calc_ut` | `sun_lon = swe.calc_ut(jd, swe.SUN)[0][0] % 360.0` | `baseline.coordinates[planet]['longitude'\|'latitude'\|'speed'] or ['declination'\|'right_ascension']` |
| 222 | `swe.calc_ut` | `moon_lon = swe.calc_ut(jd, swe.MOON)[0][0] % 360.0` | `baseline.coordinates[planet]['longitude'\|'latitude'\|'speed'] or ['declination'\|'right_ascension']` |
| 240 | `swe.julday` | `jd = swe.julday(y, m, d, utc_hour, swe.JUL_CAL)` | `baseline.astronomical_anchors['jd_utc'\|'jd_local']` |

