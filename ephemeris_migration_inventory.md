# Astra Ephemeris Migration Inventory

Total Direct Ephemeris Calls: **27**  
Total Files Affected: **9**  
Total Parent Directories: **4**  

## 📊 Summary by Parent Directory

| Parent Folder | Affected Files | Direct Calls | Primary Migration Targets |
| :--- | :---: | :---: | :--- |
| `📁 scripts/` | 2 | 12 | `generate_nakshatra_preview.py`, `search_krishna_chart.py` |
| `📁 tests/` | 4 | 9 | `test_math_engines.py`, `test_search_krishna_chart.py`, `test_stage2b_shadbala.py`, `test_vimshottari_timeline.py` |
| `📁 jyotish/` | 2 | 4 | `calc_utils.py`, `draw_chart.py` |
| `📁 jyotish/shadbala/` | 1 | 2 | `shadbala.py` |

---

## 📁 Directory: `jyotish/`

**Total Calls in Folder:** 4 across 2 file(s)

### 📄 `calc_utils.py` (`jyotish/calc_utils.py`)

| Line | Symbol | Current Code | Baseline Replacement |
| :---: | :--- | :--- | :--- |
| 1 | `swisseph` | `import swisseph as swe` | `from jyotish.baseline import ChartBaseline` |
| 5 | `swe.calc_ut` | `res, _ = swe.calc_ut(jd, swe.MOON, swe.FLG_SWIEPH)` | `baseline.coordinates[planet]['longitude'\|'latitude'\|'speed'] or ['declination'\|'right_ascension']` |
| 9 | `swe.calc_ut` | `res, _ = swe.calc_ut(jd, swe.MOON, swe.FLG_SWIEPH)` | `baseline.coordinates[planet]['longitude'\|'latitude'\|'speed'] or ['declination'\|'right_ascension']` |

### 📄 `draw_chart.py` (`jyotish/draw_chart.py`)

| Line | Symbol | Current Code | Baseline Replacement |
| :---: | :--- | :--- | :--- |
| 2136 | `calculate_varga_longitude` | `div_v_lon = calculate_varga_longitude(div_mid_lon, outer_name)` | `baseline.vargas[varga_name]['grahas'][planet]['longitude']` |

## 📁 Directory: `jyotish/shadbala/`

**Total Calls in Folder:** 2 across 1 file(s)

### 📄 `shadbala.py` (`jyotish/shadbala/shadbala.py`)

| Line | Symbol | Current Code | Baseline Replacement |
| :---: | :--- | :--- | :--- |
| 145 | `calculate_varga_longitude` | `varga_lon = calculate_varga_longitude(p1_d1_lon, varga)` | `baseline.vargas[varga_name]['grahas'][planet]['longitude']` |
| 775 | `calculate_varga_longitude` | `varga_lon = calculate_varga_longitude(p1_d1_lon, varga)` | `baseline.vargas[varga_name]['grahas'][planet]['longitude']` |

## 📁 Directory: `scripts/`

**Total Calls in Folder:** 12 across 2 file(s)

### 📄 `generate_nakshatra_preview.py` (`scripts/generate_nakshatra_preview.py`)

| Line | Symbol | Current Code | Baseline Replacement |
| :---: | :--- | :--- | :--- |
| 499 | `calculate_varga_longitude` | `div_v_lon = calculate_varga_longitude(div_mid_lon, "D9")` | `baseline.vargas[varga_name]['grahas'][planet]['longitude']` |

### 📄 `search_krishna_chart.py` (`scripts/search_krishna_chart.py`)

| Line | Symbol | Current Code | Baseline Replacement |
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

## 📁 Directory: `tests/`

**Total Calls in Folder:** 9 across 4 file(s)

### 📄 `test_math_engines.py` (`tests/test_math_engines.py`)

| Line | Symbol | Current Code | Baseline Replacement |
| :---: | :--- | :--- | :--- |
| 32 | `calculate_varga_longitude` | `v_lon_d9 = calculate_varga_longitude(lon_aries, "D9")` | `baseline.vargas[varga_name]['grahas'][planet]['longitude']` |

### 📄 `test_search_krishna_chart.py` (`tests/test_search_krishna_chart.py`)

| Line | Symbol | Current Code | Baseline Replacement |
| :---: | :--- | :--- | :--- |
| 3 | `swisseph` | `import swisseph as swe` | `from jyotish.baseline import ChartBaseline` |
| 12 | `swe.julday` | `jd = swe.julday(-3255, 8, 28, 18.333, swe.JUL_CAL)` | `baseline.astronomical_anchors['jd_utc'\|'jd_local']` |

### 📄 `test_stage2b_shadbala.py` (`tests/test_stage2b_shadbala.py`)

| Line | Symbol | Current Code | Baseline Replacement |
| :---: | :--- | :--- | :--- |
| 181 | `swisseph` | `import swisseph as swe` | `from jyotish.baseline import ChartBaseline` |

### 📄 `test_vimshottari_timeline.py` (`tests/test_vimshottari_timeline.py`)

| Line | Symbol | Current Code | Baseline Replacement |
| :---: | :--- | :--- | :--- |
| 12 | `swisseph` | `import swisseph as swe` | `from jyotish.baseline import ChartBaseline` |
| 111 | `swe.julday` | `exp_jd = swe.julday(exp_y, exp_m, exp_d, exp_hh + exp_mm / 60.0, swe.GREG_CAL)` | `baseline.astronomical_anchors['jd_utc'\|'jd_local']` |
| 138 | `swe.julday` | `first_jd = swe.julday(1969, 9, 26, 0 + 3 / 60.0, swe.GREG_CAL)` | `baseline.astronomical_anchors['jd_utc'\|'jd_local']` |
| 159 | `swe.julday` | `exp_jd = swe.julday(exp_y, exp_m, exp_d, exp_hh + exp_mm / 60.0, swe.GREG_CAL)` | `baseline.astronomical_anchors['jd_utc'\|'jd_local']` |
| 168 | `swe.revjul` | `y, m, d, _ = swe.revjul(current_jd, swe.GREG_CAL)` | `baseline.astronomical_anchors['jd_utc'\|'cal_flag']` |

