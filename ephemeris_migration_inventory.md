# Astra Ephemeris Migration Inventory

Total Direct Ephemeris Calls: **64**  
Total Files Affected: **14**  
Total Parent Directories: **8**  

## 📊 Summary by Parent Directory

| Parent Folder | Affected Files | Direct Calls | Primary Migration Targets |
| :--- | :---: | :---: | :--- |
| `📁 jyotish/` | 3 | 29 | `calc_utils.py`, `draw_chart.py`, `generate_jyotish.py` |
| `📁 scripts/` | 2 | 12 | `generate_nakshatra_preview.py`, `search_krishna_chart.py` |
| `📁 tests/` | 4 | 9 | `test_math_engines.py`, `test_search_krishna_chart.py`, `test_stage2b_shadbala.py`, `test_vimshottari_timeline.py` |
| `📁 jyotish/dashas/` | 1 | 6 | `vimshottari.py` |
| `📁 [Project Root]` | 1 | 3 | `app.py` |
| `📁 jyotish/report/` | 1 | 2 | `prominence.py` |
| `📁 jyotish/shadbala/` | 1 | 2 | `shadbala.py` |
| `📁 jyotish/transits/` | 1 | 1 | `transits.py` |

---

## 📁 Directory: `[Project Root]`

**Total Calls in Folder:** 3 across 1 file(s)

### 📄 `app.py` (`app.py`)

| Line | Symbol | Current Code | Baseline Replacement |
| :---: | :--- | :--- | :--- |
| 13 | `swisseph` | `import swisseph as swe` | `from jyotish.baseline import ChartBaseline` |
| 55 | `swe.julday` | `jd_base = swe.julday(year, month, day, local_hf, cal_flag)` | `baseline.astronomical_anchors['jd_utc'\|'jd_local']` |
| 57 | `swe.revjul` | `s_year, s_month, s_day, s_hf = swe.revjul(jd_shifted, cal_flag)` | `baseline.astronomical_anchors['jd_utc'\|'cal_flag']` |

## 📁 Directory: `jyotish/`

**Total Calls in Folder:** 29 across 3 file(s)

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

### 📄 `generate_jyotish.py` (`jyotish/generate_jyotish.py`)

| Line | Symbol | Current Code | Baseline Replacement |
| :---: | :--- | :--- | :--- |
| 21 | `swisseph` | `import swisseph as swe` | `from jyotish.baseline import ChartBaseline` |
| 24 | `swe.set_ephe_path` | `swe.set_ephe_path(os.path.join(base_dir, 'ephe'))` | `baseline.<property>` |
| 116 | `swe.julday` | `jd_local = swe.julday(year, month, day, local_hour_fraction, cal_flag)` | `baseline.astronomical_anchors['jd_utc'\|'jd_local']` |
| 132 | `swe.houses` | `cusps, ascmc = swe.houses(jd, latitude, longitude, b'C')` | `baseline.astronomical_anchors['asc_longitude'\|'mc_longitude'\|'campanus_display_cusps']` |
| 162 | `swe.calc_ut` | `res_node, _ = swe.calc_ut(jd, swe.TRUE_NODE, flags_ecliptic)` | `baseline.coordinates[planet]['longitude'\|'latitude'\|'speed'] or ['declination'\|'right_ascension']` |
| 171 | `swe.calc_ut` | `res, _ = swe.calc_ut(jd, p_id, flags_ecliptic)` | `baseline.coordinates[planet]['longitude'\|'latitude'\|'speed'] or ['declination'\|'right_ascension']` |
| 188 | `calculate_varga_longitude` | `l_lon = calculate_varga_longitude(d1_longitudes["Lagna"], v_name, d10_mode=d10_mode, d24_mode=d24_mode)` | `baseline.vargas[varga_name]['grahas'][planet]['longitude']` |
| 198 | `calculate_varga_longitude` | `p_lon = calculate_varga_longitude(d1_longitudes[p_name], v_name, d10_mode=d10_mode, d24_mode=d24_mode)` | `baseline.vargas[varga_name]['grahas'][planet]['longitude']` |
| 213 | `calculate_varga_longitude` | `c_lon = calculate_varga_longitude(c, v_name, d10_mode=d10_mode, d24_mode=d24_mode)` | `baseline.vargas[varga_name]['grahas'][planet]['longitude']` |
| 481 | `swe.set_sid_mode` | `swe.set_sid_mode(swe.SIDM_LAHIRI)` | `baseline.nakshatras['system']` |
| 482 | `swe.get_ayanamsa_ut` | `ayanamsa_lahiri = swe.get_ayanamsa_ut(jd)` | `baseline.nakshatras['equatorial_ayanamsa'\|'ecliptic_ayanamsa']` |
| 503 | `swe.calc_ut` | `res_sid, _ = swe.calc_ut(jd, swe.TRUE_NODE, swe.FLG_SWIEPH \| swe.FLG_SIDEREAL)` | `baseline.coordinates[planet]['longitude'\|'latitude'\|'speed'] or ['declination'\|'right_ascension']` |
| 506 | `swe.calc_ut` | `res_sid, _ = swe.calc_ut(jd, p_id, swe.FLG_SWIEPH \| swe.FLG_SIDEREAL)` | `baseline.coordinates[planet]['longitude'\|'latitude'\|'speed'] or ['declination'\|'right_ascension']` |
| 536 | `swe.fixstar2_ut` | `res_gc, name_gc, _ = swe.fixstar2_ut("Galactic Center", jd, flags_equatorial)` | `baseline.nakshatras['equatorial_ayanamsa'\|'ecliptic_ayanamsa']` |
| 538 | `swe.fixstar2_ut` | `res_gc_ecl, _, _ = swe.fixstar2_ut("Galactic Center", jd, flags_ecliptic_gc)` | `baseline.nakshatras['equatorial_ayanamsa'\|'ecliptic_ayanamsa']` |
| 564 | `swe.calc_ut` | `res_eq, _ = swe.calc_ut(jd, swe.TRUE_NODE, flags_equatorial)` | `baseline.coordinates[planet]['longitude'\|'latitude'\|'speed'] or ['declination'\|'right_ascension']` |
| 567 | `swe.calc_ut` | `res_eq, _ = swe.calc_ut(jd, p_id, flags_equatorial)` | `baseline.coordinates[planet]['longitude'\|'latitude'\|'speed'] or ['declination'\|'right_ascension']` |
| 598 | `swe.calc_ut` | `p_eq = swe.calc_ut(jd + 0.5, swe.TRUE_NODE, swe.FLG_SWIEPH \| swe.FLG_EQUATORIAL)[0][0]` | `baseline.coordinates[planet]['longitude'\|'latitude'\|'speed'] or ['declination'\|'right_ascension']` |
| 599 | `swe.calc_ut` | `m_eq = swe.calc_ut(jd - 0.5, swe.TRUE_NODE, swe.FLG_SWIEPH \| swe.FLG_EQUATORIAL)[0][0]` | `baseline.coordinates[planet]['longitude'\|'latitude'\|'speed'] or ['declination'\|'right_ascension']` |
| 609 | `swe.calc_ut` | `res, _ = swe.calc_ut(jd, p_id, flags_ecliptic)` | `baseline.coordinates[planet]['longitude'\|'latitude'\|'speed'] or ['declination'\|'right_ascension']` |
| 660 | `swe.rise_trans` | `res_rise = swe.rise_trans(jd, swe.SUN, swe.CALC_RISE \| swe.BIT_DISC_CENTER, (longitude, latitude, 0.0), 0.0, 0.0)` | `baseline.astronomical_anchors['sunrise_jd'\|'sunset_jd']` |
| 665 | `swe.rise_trans` | `res_rise = swe.rise_trans(jd - 1.0, swe.SUN, swe.CALC_RISE \| swe.BIT_DISC_CENTER, (longitude, latitude, 0.0), 0.0, 0.0)` | `baseline.astronomical_anchors['sunrise_jd'\|'sunset_jd']` |
| 705 | `swe.set_sid_mode` | `swe.set_sid_mode(swe.SIDM_LAHIRI)` | `baseline.nakshatras['system']` |
| 706 | `swe.calc_ut` | `res_moon, _ = swe.calc_ut(jd, swe.MOON, swe.FLG_SWIEPH \| swe.FLG_SIDEREAL)` | `baseline.coordinates[planet]['longitude'\|'latitude'\|'speed'] or ['declination'\|'right_ascension']` |
| 721 | `swe.calc_ut` | `res_moon, _ = swe.calc_ut(jd, swe.MOON, flags_equatorial)` | `baseline.coordinates[planet]['longitude'\|'latitude'\|'speed'] or ['declination'\|'right_ascension']` |

## 📁 Directory: `jyotish/dashas/`

**Total Calls in Folder:** 6 across 1 file(s)

### 📄 `vimshottari.py` (`jyotish/dashas/vimshottari.py`)

| Line | Symbol | Current Code | Baseline Replacement |
| :---: | :--- | :--- | :--- |
| 16 | `swisseph` | `import swisseph as swe` | `from jyotish.baseline import ChartBaseline` |
| 68 | `swe.revjul` | `year, month, day, ut_hour_frac = swe.revjul(jd, cal_flag)` | `baseline.astronomical_anchors['jd_utc'\|'cal_flag']` |
| 76 | `swe.julday` | `next_jd = swe.julday(year, month, day, 0.0, cal_flag) + (hh / 24.0)` | `baseline.astronomical_anchors['jd_utc'\|'jd_local']` |
| 77 | `swe.revjul` | `year, month, day, ut_hour_frac = swe.revjul(next_jd, cal_flag)` | `baseline.astronomical_anchors['jd_utc'\|'cal_flag']` |
| 127 | `swe.set_sid_mode` | `swe.set_sid_mode(swe.SIDM_LAHIRI)` | `baseline.nakshatras['system']` |
| 128 | `swe.calc_ut` | `res_m, _ = swe.calc_ut(birth_jd_utc, swe.MOON, swe.FLG_SWIEPH \| swe.FLG_SIDEREAL)` | `baseline.coordinates[planet]['longitude'\|'latitude'\|'speed'] or ['declination'\|'right_ascension']` |

## 📁 Directory: `jyotish/report/`

**Total Calls in Folder:** 2 across 1 file(s)

### 📄 `prominence.py` (`jyotish/report/prominence.py`)

| Line | Symbol | Current Code | Baseline Replacement |
| :---: | :--- | :--- | :--- |
| 50 | `swisseph` | `import swisseph as swe` | `from jyotish.baseline import ChartBaseline` |
| 103 | `swe.calc_ut` | `res, _ = swe.calc_ut(jd, p_map[planet], swe.FLG_SWIEPH \| swe.FLG_EQUATORIAL)` | `baseline.coordinates[planet]['longitude'\|'latitude'\|'speed'] or ['declination'\|'right_ascension']` |

## 📁 Directory: `jyotish/shadbala/`

**Total Calls in Folder:** 2 across 1 file(s)

### 📄 `shadbala.py` (`jyotish/shadbala/shadbala.py`)

| Line | Symbol | Current Code | Baseline Replacement |
| :---: | :--- | :--- | :--- |
| 145 | `calculate_varga_longitude` | `varga_lon = calculate_varga_longitude(p1_d1_lon, varga)` | `baseline.vargas[varga_name]['grahas'][planet]['longitude']` |
| 775 | `calculate_varga_longitude` | `varga_lon = calculate_varga_longitude(p1_d1_lon, varga)` | `baseline.vargas[varga_name]['grahas'][planet]['longitude']` |

## 📁 Directory: `jyotish/transits/`

**Total Calls in Folder:** 1 across 1 file(s)

### 📄 `transits.py` (`jyotish/transits/transits.py`)

| Line | Symbol | Current Code | Baseline Replacement |
| :---: | :--- | :--- | :--- |
| 11 | `swisseph` | `import swisseph as swe` | `from jyotish.baseline import ChartBaseline` |

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

