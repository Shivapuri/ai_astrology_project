"""
jyotish/baseline.py
Stage 1: Master Astronomical & Coordinate Baseline Engine for Astra.

Orchestrates the single-pass ephemeris extraction, True 3D coordinates,
Dhruva Nakshatras, Upagrahas, Pañcāṅga, Core Sphutas, and 16 Divisional Vargas.

Re-exports all static catalogs from jyotish.baseline_tables and pure
mathematical algorithms from jyotish.baseline_math for zero breaking changes.
"""

from functools import cached_property
from typing import Dict, List, Any, Optional, Tuple
import os
import math
import swisseph as swe

# Set ephemeris path to absolute path of 'ephe' directory in project root
_base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_ephe_path = os.path.join(_base_dir, 'ephe')
if os.path.exists(_ephe_path):
    swe.set_ephe_path(_ephe_path)

# =============================================================================
# RE-EXPORTS: STATIC REFERENCE CATALOGS & PURE MATHEMATICAL ALGORITHMS
# =============================================================================
from jyotish.baseline_tables import (
    PLANETS_ORDER,
    ALL_BODIES,
    TARA_GRAHAS,
    PLANET_ABBREVIATIONS,
    ZODIAC_SIGNS,
    SIGN_LORDS,
    NAKSHATRAS,
    NITYA_YOGAS,
    VIMSHOTTARI_SEQUENCE,
    VIMSHOTTARI_YEARS,
    COMBUSTION_ORBS,
    VARGAS_LIST,
    SHASTIAMSA_DEITIES,
    SHASTIAMSA_MALEFIC_ODD,
    CHANDRA_KRIYAS_DATA,
    CHANDRA_AVASTHAS_DATA,
    CHANDRA_VELAS_DATA,
)

from jyotish.baseline_math import (
    calculate_sub_lord,
    calculate_varga_longitude,
    calculate_unequal_trimsamsa,
    calculate_shastiamsa_details,
    calculate_baladi_state,
    get_eq_from_ecl,
    find_preceding_solar_crossing,
)


class ChartBaseline:
    """
    Immutable Stage 1 Coordinate Container.
    Computes all static astronomical facts and geometric coordinates once.
    Strictly isolated from Stage 2/3 house evaluations and dignity scoring.
    """

    def __init__(
        self,
        name: str = "Native",
        year: int = 1995,
        month: int = 5,
        day: int = 15,
        hour: int = 14,
        minute: int = 30,
        second: int = 0,
        latitude: float = 28.6139,
        longitude: float = 77.2090,
        timezone_offset: float = 5.5,
        place: str = "",
        d10_mode: str = "reverse",
        d24_mode: str = "reverse",
        nakshatra_system: str = "ERNST_DHRUVA"
    ):
        self.name = name
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute
        self.second = second
        self.latitude = latitude
        self.longitude = longitude
        self.timezone_offset = timezone_offset
        self.place = place
        self.d10_mode = d10_mode
        self.d24_mode = d24_mode
        self.nakshatra_system = nakshatra_system

    # =========================================================================
    # 1. TIME & ASTRONOMICAL ANCHORS (Swiss Ephemeris called ONCE)
    # =========================================================================
    @cached_property
    def astronomical_anchors(self) -> Dict[str, Any]:
        """Calculates Julian Days, angles, sunrise/sunset, and 3D planetary positions."""
        local_time_frac = self.hour + (self.minute / 60.0) + (self.second / 3600.0)

        # Classical Calendar Flag
        if self.year < 1582 or (self.year == 1582 and self.month < 10) or (self.year == 1582 and self.month == 10 and self.day < 15):
            cal_flag = swe.JUL_CAL
        else:
            cal_flag = swe.GREG_CAL

        jd_local = swe.julday(self.year, self.month, self.day, local_time_frac, cal_flag)
        utc_time_frac = local_time_frac - self.timezone_offset
        jd_utc = swe.julday(self.year, self.month, self.day, utc_time_frac, cal_flag)

        # 1. Angles & Cusps (Campanus: system 'C')
        cusps, ascmc = swe.houses(jd_utc, self.latitude, self.longitude, b'C')
        asc_lon = ascmc[0] % 360.0
        mc_lon = ascmc[1] % 360.0

        # 2. Precision Sunrise / Sunset via Center of Solar Disc (BIT_DISC_CENTER)
        geopos = (self.longitude, self.latitude, 0.0)
        rsmi = swe.CALC_RISE | swe.BIT_DISC_CENTER
        try:
            _, tret_rise = swe.rise_trans(jd_utc, swe.SUN, rsmi, geopos)
            sunrise_jd = tret_rise[0]
            if sunrise_jd > jd_utc:
                _, tret_prev = swe.rise_trans(jd_utc - 1.0, swe.SUN, rsmi, geopos)
                sunrise_jd = tret_prev[0]
            _, tret_set = swe.rise_trans(sunrise_jd, swe.SUN, swe.CALC_SET | swe.BIT_DISC_CENTER, geopos)
            sunset_jd = tret_set[0]
            _, tret_next_rise = swe.rise_trans(sunset_jd, swe.SUN, rsmi, geopos)
            next_sunrise_jd = tret_next_rise[0]
            is_day_birth = (sunrise_jd <= jd_utc <= sunset_jd)
        except Exception:
            sunrise_jd = int(jd_utc) + 0.25
            sunset_jd = int(jd_utc) + 0.75
            next_sunrise_jd = sunrise_jd + 1.0
            is_day_birth = True

        # 3. Temporal Lords for Kala Bala (Vāra, Horā, Māsa, Varṣa)
        planets_by_weekday = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
        hora_sequence = ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon"]

        # Civil weekday from sunrise: Sunday=0, Monday=1, ..., Saturday=6
        lmt_sunrise = sunrise_jd + (self.longitude / 360.0)
        vara_idx = int(lmt_sunrise + 1.5) % 7
        vara_lord = planets_by_weekday[vara_idx]

        # Hora Lord (Unequal planetary hour from sunrise)
        if is_day_birth:
            day_hour_length = (sunset_jd - sunrise_jd) / 12.0
            hours_elapsed = max(0, min(11, int((jd_utc - sunrise_jd) / day_hour_length)))
        else:
            night_hour_length = (next_sunrise_jd - sunset_jd) / 12.0
            hours_elapsed = 12 + max(0, min(11, int((jd_utc - sunset_jd) / night_hour_length)))
        start_hora_idx = hora_sequence.index(vara_lord)
        hora_lord = hora_sequence[(start_hora_idx + hours_elapsed) % 7]

        # Year Lord (Varṣeśa) & Month Lord (Māseśa) via backward root-finding
        sun_res, _ = swe.calc_ut(jd_utc, swe.SUN, swe.FLG_SWIEPH)
        sun_lon = sun_res[0] % 360.0

        try:
            jd_mesha = find_preceding_solar_crossing(0.0, jd_utc, sun_lon)
            lmt_mesha = jd_mesha + (self.longitude / 360.0)
            varsha_lord = planets_by_weekday[int(lmt_mesha + 1.5) % 7]
        except Exception:
            varsha_lord = vara_lord

        try:
            sign_boundary = int(sun_lon // 30) * 30.0
            jd_sankranti = find_preceding_solar_crossing(sign_boundary, jd_utc, sun_lon)
            lmt_sankranti = jd_sankranti + (self.longitude / 360.0)
            mase_lord = planets_by_weekday[int(lmt_sankranti + 1.5) % 7]
        except Exception:
            mase_lord = vara_lord

        temporal_lords = {
            "Vara": vara_lord,
            "Hora": hora_lord,
            "Masa": mase_lord,
            "Varsha": varsha_lord
        }

        # 4. Campanus Display Cusps (Strictly Isolated for SVG Rendering)
        campanus_display = {}
        for i, c_lon in enumerate(cusps):
            h_num = i + 1
            clon = c_lon % 360.0
            s_idx = int(clon // 30)
            campanus_display[h_num] = {
                "house": h_num,
                "absolute_longitude": round(clon, 4),
                "sign_index": s_idx,
                "sign": ZODIAC_SIGNS[s_idx],
                "degree_0_to_30": round(clon % 30.0, 4),
                "degree_in_sign": round(clon % 30.0, 4),
                "is_display_only": True
            }

        # 5. Planetary Coordinates (Ecliptic + True 3D Equatorial)
        flags_ecl = swe.FLG_SWIEPH | swe.FLG_SPEED
        flags_eq = swe.FLG_SWIEPH | swe.FLG_EQUATORIAL | swe.FLG_SPEED

        planet_ids = {
            "Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS,
            "Mercury": swe.MERCURY, "Jupiter": swe.JUPITER,
            "Venus": swe.VENUS, "Saturn": swe.SATURN
        }

        bodies = {}
        for p, pid in planet_ids.items():
            res_ecl, _ = swe.calc_ut(jd_utc, pid, flags_ecl)
            res_eq, _ = swe.calc_ut(jd_utc, pid, flags_eq)
            bodies[p] = {
                "longitude": res_ecl[0] % 360.0,
                "latitude": round(res_ecl[1], 4),
                "speed": res_ecl[3],
                "right_ascension": res_eq[0] % 360.0,
                "declination": round(res_eq[1], 4),
                "is_retrograde": bool(res_ecl[3] < 0 and p not in ("Sun", "Moon"))
            }

        # Nodes
        res_node_ecl, _ = swe.calc_ut(jd_utc, swe.TRUE_NODE, flags_ecl)
        res_node_eq, _ = swe.calc_ut(jd_utc, swe.TRUE_NODE, flags_eq)
        r_lon = res_node_ecl[0] % 360.0
        k_lon = (r_lon + 180.0) % 360.0
        r_ra = res_node_eq[0] % 360.0
        k_ra = (r_ra + 180.0) % 360.0

        node_retro = bool(res_node_ecl[3] < 0)

        bodies["Rahu"] = {
            "longitude": r_lon, "latitude": round(res_node_ecl[1], 4),
            "speed": res_node_ecl[3], "right_ascension": r_ra,
            "declination": round(res_node_eq[1], 4), "is_retrograde": node_retro
        }
        bodies["Ketu"] = {
            "longitude": k_lon, "latitude": round(-res_node_ecl[1], 4),
            "speed": res_node_ecl[3], "right_ascension": k_ra,
            "declination": round(-res_node_eq[1], 4), "is_retrograde": node_retro
        }

        # Spherical transformation for Lagna & MC equatorial coordinates
        try:
            eps_res, _ = swe.calc_ut(jd_utc, swe.ECL_NUT)
            true_eps = eps_res[0]
        except Exception:
            true_eps = 23.4392911

        asc_ra, asc_dec = get_eq_from_ecl(asc_lon, true_eps)
        mc_ra, mc_dec = get_eq_from_ecl(mc_lon, true_eps)

        bodies["Lagna"] = {"longitude": asc_lon, "latitude": 0.0, "speed": 0.0, "right_ascension": asc_ra, "declination": round(asc_dec, 4), "is_retrograde": False}
        bodies["MC"] = {"longitude": mc_lon, "latitude": 0.0, "speed": 0.0, "right_ascension": mc_ra, "declination": round(mc_dec, 4), "is_retrograde": False}

        sensitive_cusp_degree = round(asc_lon % 30.0, 4)

        return {
            "jd_local": jd_local,
            "jd_utc": jd_utc,
            "cal_flag": cal_flag,
            "sunrise_jd": sunrise_jd,
            "sunset_jd": sunset_jd,
            "next_sunrise_jd": next_sunrise_jd,
            "is_day_birth": is_day_birth,
            "asc_longitude": asc_lon,
            "mc_longitude": mc_lon,
            "sensitive_cusp_degree": sensitive_cusp_degree,
            "temporal_lords": temporal_lords,
            "bodies": bodies,
            "raw_campanus_cusps": cusps,
            "campanus_display_cusps": campanus_display
        }

    # =========================================================================
    # 2. UPAGRAHAS: MĀNDI, GULIKA, YAMAKAṆṬAKA, KĀLA, ARDHAPRAHĀRA (Phaladeepika Ch. 25)
    # =========================================================================
    @cached_property
    def upagrahas(self) -> Dict[str, Dict[str, Any]]:
        """Calculates exact rising longitudes and whole-sign house placements for 5 Upagrahas."""
        anchors = self.astronomical_anchors
        sr = anchors["sunrise_jd"]
        ss = anchors["sunset_jd"]
        next_sr = anchors["next_sunrise_jd"]
        is_day = anchors["is_day_birth"]
        weekday = int(sr + (self.longitude / 360.0) + 1.5) % 7
        lagna_s_idx = int(anchors["asc_longitude"] // 30)

        if is_day:
            day_len = ss - sr
            part_len = day_len / 8.0
            kala_part_idx = (0 - weekday) % 7
            ardhaprahara_part_idx = (3 - weekday) % 7
            jupiter_part_idx = (4 - weekday) % 7
            saturn_part_idx = (6 - weekday) % 7

            epoch_kala = sr + kala_part_idx * part_len
            epoch_ardhaprahara = sr + ardhaprahara_part_idx * part_len
            epoch_yamakantaka = sr + jupiter_part_idx * part_len
            epoch_gulika = sr + saturn_part_idx * part_len
            epoch_mandi = epoch_gulika + (part_len / 2.0)
        else:
            night_len = next_sr - ss
            part_len = night_len / 8.0
            kala_part_idx = (3 - weekday) % 7
            ardhaprahara_part_idx = (6 - weekday) % 7
            jupiter_part_idx = (0 - weekday) % 7
            saturn_part_idx = (2 - weekday) % 7

            epoch_kala = ss + kala_part_idx * part_len
            epoch_ardhaprahara = ss + ardhaprahara_part_idx * part_len
            epoch_yamakantaka = ss + jupiter_part_idx * part_len
            epoch_gulika = ss + saturn_part_idx * part_len
            epoch_mandi = epoch_gulika + (part_len / 2.0)

        def get_upagraha_point(epoch_jd: float, name: str) -> Dict[str, Any]:
            _, ascmc = swe.houses(epoch_jd, self.latitude, self.longitude, b'C')
            u_lon = ascmc[0] % 360.0
            s_idx = int(u_lon // 30)
            w_house = ((s_idx - lagna_s_idx) % 12) + 1
            return {
                "name": name,
                "longitude": round(u_lon, 4),
                "sign_index": s_idx,
                "sign": ZODIAC_SIGNS[s_idx],
                "degree_0_to_30": round(u_lon % 30.0, 4),
                "degree_in_sign": round(u_lon % 30.0, 4),
                "whole_sign_house": w_house,
                "epoch_jd": round(epoch_jd, 6)
            }

        return {
            "Gulika": get_upagraha_point(epoch_gulika, "Gulika"),
            "Mandi": get_upagraha_point(epoch_mandi, "Mandi"),
            "Yamakantaka": get_upagraha_point(epoch_yamakantaka, "Yamakantaka"),
            "Kala": get_upagraha_point(epoch_kala, "Kala"),
            "Ardhaprahara": get_upagraha_point(epoch_ardhaprahara, "Ardhaprahara")
        }

    # =========================================================================
    # 3. PAÑCĀṄGA CORE COORDINATES & CHILDBIRTH SPHUTAS (Phaladeepika Ch. 4 & 12)
    # =========================================================================
    @cached_property
    def pancanga(self) -> Dict[str, Any]:
        """Calculates Tithi, Karaṇa, Nityā Yoga (Sidereal), and Vāra."""
        bodies = self.astronomical_anchors["bodies"]
        sun_lon = bodies["Sun"]["longitude"]
        moon_lon = bodies["Moon"]["longitude"]

        diff = (moon_lon - sun_lon) % 360.0

        # Tithi (1 to 30)
        tithi_num = int(diff // 12.0) + 1
        is_shukla = (tithi_num <= 15)
        tithi_in_paksha = tithi_num if is_shukla else (tithi_num - 15)
        chidra_tithis = {4, 6, 8, 9, 12, 14}
        is_chidra = tithi_in_paksha in chidra_tithis

        # Karaṇa (1 to 60)
        karana_num = int(diff // 6.0) + 1
        vishti_indices = {8, 15, 22, 29, 36, 43, 50, 57}
        is_vishti = karana_num in vishti_indices

        # Nityā Yoga (1 to 27) calculated via Sidereal Sum: (Sun_sid + Moon_sid) % 360
        sid_sun = self.nakshatras["grahas"]["Sun"]["position"]
        sid_moon = self.nakshatras["grahas"]["Moon"]["position"]
        yoga_arc = (sid_sun + sid_moon) % 360.0
        yoga_num = int(yoga_arc // (360.0 / 27.0)) + 1
        yoga_num = max(1, min(27, yoga_num))
        yoga_name = NITYA_YOGAS[yoga_num - 1]

        return {
            "tithi": {
                "number": tithi_num,
                "paksha": "Shukla" if is_shukla else "Krishna",
                "tithi_in_paksha": tithi_in_paksha,
                "is_chidra": is_chidra,
                "traversal_pct": round((diff % 12.0) / 12.0 * 100.0, 2)
            },
            "karana": {
                "number": karana_num,
                "is_vishti": is_vishti,
                "is_bhadra": is_vishti
            },
            "nitya_yoga": {
                "number": yoga_num,
                "name": yoga_name,
                "arc_degrees": round(yoga_arc, 4),
                "traversal_pct": round((yoga_arc % (360.0 / 27.0)) / (360.0 / 27.0) * 100.0, 2)
            },
            "vara": self.astronomical_anchors["temporal_lords"]["Vara"]
        }

    @cached_property
    def special_sphutas(self) -> Dict[str, Any]:
        """
        Calculates Santāna Tithi, 3-tier Bīja/Kṣetra Sphutas (Phaladeepika Ch. 12),
        and Trisphuṭa, Catuṣphuṭa, Pañcasphuṭa (Phaladeepika Ch. 17).
        """
        bodies = self.astronomical_anchors["bodies"]
        sun_lon = bodies["Sun"]["longitude"]
        moon_lon = bodies["Moon"]["longitude"]
        mars_lon = bodies["Mars"]["longitude"]
        jup_lon = bodies["Jupiter"]["longitude"]
        ven_lon = bodies["Venus"]["longitude"]

        # 1. Santāna Tithi: 5 * (Moon - Sun) % 360
        santana_diff = (5.0 * (moon_lon - sun_lon)) % 360.0
        santana_tithi = int(santana_diff // 12.0) + 1
        santana_is_shukla = (santana_tithi <= 15)
        santana_tithi_in_paksha = santana_tithi if santana_is_shukla else (santana_tithi - 15)

        # Classical filter: Krishna Paksha Chidra (4, 6, 8, 9, 12, 14) or Amavasya (30)
        santana_is_afflicted = (not santana_is_shukla and santana_tithi_in_paksha in {4, 6, 8, 9, 12, 14}) or (santana_tithi == 30)
        santana_is_propitious = not santana_is_afflicted

        # 2. Bīja Sphuta (Male): (Jupiter + Sun + Venus) % 360
        bija_lon = (jup_lon + sun_lon + ven_lon) % 360.0
        b_sign_idx = int(bija_lon // 30)
        b_d9_lon = calculate_varga_longitude(bija_lon, "D9")
        b_d9_idx = int(b_d9_lon // 30)

        bija_odd_sign = (b_sign_idx % 2 == 0)
        bija_odd_d9 = (b_d9_idx % 2 == 0)
        if bija_odd_sign and bija_odd_d9:
            bija_status = "Virile (Both Odd)"
            bija_tier = "Strong"
        elif bija_odd_sign or bija_odd_d9:
            bija_status = "Mixed (Delayed Progeny)"
            bija_tier = "Moderate"
        else:
            bija_status = "Deficient (Both Even)"
            bija_tier = "Deficient"

        # 3. Kṣetra Sphuta (Female): (Jupiter + Moon + Mars) % 360
        ksetra_lon = (jup_lon + moon_lon + mars_lon) % 360.0
        k_sign_idx = int(ksetra_lon // 30)
        k_d9_lon = calculate_varga_longitude(ksetra_lon, "D9")
        k_d9_idx = int(k_d9_lon // 30)

        ksetra_even_sign = (k_sign_idx % 2 != 0)
        ksetra_even_d9 = (k_d9_idx % 2 != 0)
        if ksetra_even_sign and ksetra_even_d9:
            ksetra_status = "Fertile (Both Even)"
            ksetra_tier = "Strong"
        elif ksetra_even_sign or ksetra_even_d9:
            ksetra_status = "Mixed (Delayed Progeny)"
            ksetra_tier = "Moderate"
        else:
            ksetra_status = "Deficient (Both Odd)"
            ksetra_tier = "Deficient"

        # 4. Trisphuṭa (Phaladeepika Ch. 17): (Lagna + Moon + Māndi) % 360
        asc_lon = self.astronomical_anchors["asc_longitude"]
        mandi_lon = self.upagrahas["Mandi"]["longitude"]
        rahu_lon = bodies["Rahu"]["longitude"]

        trisphuta_lon = (asc_lon + moon_lon + mandi_lon) % 360.0
        t_sign_idx = int(trisphuta_lon // 30)
        t_d9_lon = calculate_varga_longitude(trisphuta_lon, "D9") % 360.0
        t_d9_idx = int(t_d9_lon // 30)

        # 5. Catuṣphuṭa (Phaladeepika Ch. 17): (Trisphuṭa + Sun) % 360
        catusphuta_lon = (trisphuta_lon + sun_lon) % 360.0
        c_sign_idx = int(catusphuta_lon // 30)

        # 6. Pañcasphuṭa (Phaladeepika Ch. 17): (Catuṣphuṭa + Rāhu) % 360
        pancasphuta_lon = (catusphuta_lon + rahu_lon) % 360.0
        p_sign_idx = int(pancasphuta_lon // 30)

        return {
            "santana_tithi": {
                "tithi_number": santana_tithi,
                "arc_degrees": round(santana_diff, 4),
                "paksha": "Shukla" if santana_is_shukla else "Krishna",
                "tithi_in_paksha": santana_tithi_in_paksha,
                "is_afflicted": santana_is_afflicted,
                "is_propitious": santana_is_propitious
            },
            "bija_sphuta_male": {
                "longitude": round(bija_lon, 4),
                "sign": ZODIAC_SIGNS[b_sign_idx],
                "d9_sign": ZODIAC_SIGNS[b_d9_idx],
                "status": bija_status,
                "tier": bija_tier,
                "is_virile": bool(bija_odd_sign and bija_odd_d9)
            },
            "ksetra_sphuta_female": {
                "longitude": round(ksetra_lon, 4),
                "sign": ZODIAC_SIGNS[k_sign_idx],
                "d9_sign": ZODIAC_SIGNS[k_d9_idx],
                "status": ksetra_status,
                "tier": ksetra_tier,
                "is_fertile": bool(ksetra_even_sign and ksetra_even_d9)
            },
            "trisphuta": {
                "longitude": round(trisphuta_lon, 4),
                "sign": ZODIAC_SIGNS[t_sign_idx],
                "sign_index": t_sign_idx,
                "degree_0_to_30": round(trisphuta_lon % 30.0, 4),
                "degree_in_sign": round(trisphuta_lon % 30.0, 4),
                "d9_longitude": round(t_d9_lon, 4),
                "d9_sign": ZODIAC_SIGNS[t_d9_idx],
                "d9_sign_index": t_d9_idx,
                "d9_degree_in_sign": round(t_d9_lon % 30.0, 4)
            },
            "catusphuta": {
                "longitude": round(catusphuta_lon, 4),
                "sign": ZODIAC_SIGNS[c_sign_idx],
                "sign_index": c_sign_idx,
                "degree_0_to_30": round(catusphuta_lon % 30.0, 4),
                "degree_in_sign": round(catusphuta_lon % 30.0, 4)
            },
            "pancasphuta": {
                "longitude": round(pancasphuta_lon, 4),
                "sign": ZODIAC_SIGNS[p_sign_idx],
                "sign_index": p_sign_idx,
                "degree_0_to_30": round(pancasphuta_lon % 30.0, 4),
                "degree_in_sign": round(pancasphuta_lon % 30.0, 4)
            }
        }

    # =========================================================================
    # 4. STATIC GEOMETRIC SEPARATION & INTERACTION MATRICES
    # =========================================================================
    @cached_property
    def separation_matrix(self) -> Dict[str, Dict[str, float]]:
        """11x11 relative angular separation: delta_theta[b1][b2] = (lon2 - lon1) % 360."""
        bodies = self.astronomical_anchors["bodies"]
        matrix = {}
        for b1 in ALL_BODIES:
            matrix[b1] = {}
            lon1 = bodies[b1]["longitude"]
            for b2 in ALL_BODIES:
                lon2 = bodies[b2]["longitude"]
                matrix[b1][b2] = round((lon2 - lon1) % 360.0, 4)
        return matrix

    @cached_property
    def shortest_distance_matrix(self) -> Dict[str, Dict[str, float]]:
        """11x11 symmetric shortest distance: min(sep, 360 - sep)."""
        sep = self.separation_matrix
        matrix = {}
        for b1 in ALL_BODIES:
            matrix[b1] = {}
            for b2 in ALL_BODIES:
                d = sep[b1][b2]
                matrix[b1][b2] = round(min(d, 360.0 - d), 4)
        return matrix

    @cached_property
    def planetary_wars(self) -> List[Dict[str, Any]]:
        """
        Detects Graha Yuddha (planetary war) collisions (<= 1.0° shortest distance)
        among the five classical Tāra Grahas (Mars, Mercury, Jupiter, Venus, Saturn).
        Winner determined by higher Northern declination.
        """
        dist = self.shortest_distance_matrix
        bodies = self.astronomical_anchors["bodies"]
        wars = []

        for i, p1 in enumerate(TARA_GRAHAS):
            for p2 in TARA_GRAHAS[i + 1:]:
                sep = dist[p1][p2]
                if sep <= 1.0:
                    s1 = int(bodies[p1]["longitude"] // 30)
                    s2 = int(bodies[p2]["longitude"] // 30)
                    cross_border = (s1 != s2)

                    # Venus always wins per Surya Siddhanta VII.23
                    if p1 == "Venus":
                        winner, loser = p1, p2
                        reason = "Venus Sovereign Brilliance (SS VII.23)"
                    elif p2 == "Venus":
                        winner, loser = p2, p1
                        reason = "Venus Sovereign Brilliance (SS VII.23)"
                    else:
                        dec1 = bodies[p1]["declination"]
                        dec2 = bodies[p2]["declination"]
                        if dec1 >= dec2:
                            winner, loser = p1, p2
                            reason = f"Northern Declination ({dec1:.2f}° vs {dec2:.2f}°)"
                        else:
                            winner, loser = p2, p1
                            reason = f"Northern Declination ({dec2:.2f}° vs {dec1:.2f}°)"

                    wars.append({
                        "planet1": p1,
                        "planet2": p2,
                        "separation_degrees": round(sep, 4),
                        "cross_border": cross_border,
                        "winner": winner,
                        "loser": loser,
                        "reason": reason
                    })
        return wars

    # =========================================================================
    # 5. COORDINATE & SIGN DECOMPOSITION
    # =========================================================================
    @cached_property
    def coordinates(self) -> Dict[str, Dict[str, Any]]:
        """Decomposes all bodies into Tropical coordinates, 3D declination, Baladi states, and War status."""
        bodies = self.astronomical_anchors["bodies"]
        wars = self.planetary_wars

        # Map planetary war status
        war_status = {}
        for w in wars:
            p1, p2 = w["planet1"], w["planet2"]
            winner, loser = w["winner"], w["loser"]
            war_status[winner] = {
                "is_in_planetary_war": True,
                "is_war_winner": True,
                "is_war_loser": False,
                "war_opponent": loser,
                "war_details": w
            }
            war_status[loser] = {
                "is_in_planetary_war": True,
                "is_war_winner": False,
                "is_war_loser": True,
                "war_opponent": winner,
                "war_details": w
            }

        coords = {}
        for b in ALL_BODIES:
            lon = bodies[b]["longitude"]
            s_idx = int(lon // 30)
            deg_in_sign = round(lon % 30.0, 4)
            baladi = calculate_baladi_state(ZODIAC_SIGNS[s_idx], deg_in_sign)

            p_war = war_status.get(b, {
                "is_in_planetary_war": False,
                "is_war_winner": False,
                "is_war_loser": False,
                "war_opponent": None,
                "war_details": None
            })

            coords[b] = {
                "name": b,
                "longitude": lon,
                "sign_index": s_idx,
                "sign": ZODIAC_SIGNS[s_idx],
                "degree_0_to_30": deg_in_sign,
                "degree_in_sign": deg_in_sign,
                "latitude": bodies[b]["latitude"],
                "right_ascension": bodies[b]["right_ascension"],
                "declination": bodies[b]["declination"],
                "speed": bodies[b]["speed"],
                "is_retrograde": bodies[b]["is_retrograde"],
                "baladi_avastha": baladi,
                "is_in_planetary_war": p_war["is_in_planetary_war"],
                "is_war_winner": p_war["is_war_winner"],
                "is_war_loser": p_war["is_war_loser"],
                "war_opponent": p_war["war_opponent"],
                "war_details": p_war["war_details"]
            }
        return coords

    # =========================================================================
    # 6. SIDEREAL EQUATORIAL NAKSHATRAS & CANDRA KRIYĀDI (Phaladeepika Ch. 4)
    # =========================================================================
    @cached_property
    def nakshatras(self) -> Dict[str, Any]:
        """Calculates Dhruva Equatorial / Lahiri Nakshatras and complete Candra Kriyādi tables."""
        jd_utc = self.astronomical_anchors["jd_utc"]
        asc_lon = self.astronomical_anchors["asc_longitude"]

        if self.nakshatra_system == "VIC_CHITRA":
            swe.set_sid_mode(swe.SIDM_LAHIRI)
            ayanamsa_lahiri = swe.get_ayanamsa_ut(jd_utc)
            ayanamsa_eq = ayanamsa_lahiri
            ayanamsa_ecl = ayanamsa_lahiri
            grahas_nak = {}

            for p in ALL_BODIES:
                sid_pos = (self.coordinates[p]["longitude"] - ayanamsa_lahiri) % 360.0
                n_idx = int(sid_pos / (360.0 / 27.0)) % 27
                pada = int((sid_pos % (360.0 / 27.0)) / (360.0 / 108.0)) + 1
                nak_lord = VIMSHOTTARI_SEQUENCE[n_idx % 9]
                nak_fraction = (sid_pos % (360.0 / 27.0)) / (360.0 / 27.0)
                sub_lord = calculate_sub_lord(nak_fraction, nak_lord)

                grahas_nak[p] = {
                    "nakshatra": NAKSHATRAS[n_idx],
                    "pada": pada,
                    "position": round(sid_pos, 4),
                    "sidereal_ra": round(sid_pos, 4),
                    "sidereal_longitude": round(sid_pos, 4),
                    "nakshatra_lord": nak_lord,
                    "sub_lord": sub_lord,
                    "lord_sublord": f"{PLANET_ABBREVIATIONS.get(nak_lord, nak_lord[:2])}/{PLANET_ABBREVIATIONS.get(sub_lord, sub_lord[:2])}"
                }

        else:
            # Ernst Wilhelm: Dhruva Galactic Center (Middle of Mula = 246°40')
            flags_eq = swe.FLG_SWIEPH | swe.FLG_EQUATORIAL
            try:
                res_gc, _, _ = swe.fixstar2_ut("Galactic Center", jd_utc, flags_eq)
                ra_gc = res_gc[0]
                res_gc_ecl, _, _ = swe.fixstar2_ut("Galactic Center", jd_utc, swe.FLG_SWIEPH)
                lon_gc = res_gc_ecl[0]
            except Exception:
                ra_gc = 266.0371
                lon_gc = 266.5179

            ayanamsa_eq = ra_gc - 246.6667
            ayanamsa_ecl = lon_gc - 246.6667
            ayanamsa_lahiri = ayanamsa_ecl

            grahas_nak = {}
            for p in ALL_BODIES:
                if p in ("Lagna", "MC"):
                    ecl_target = asc_lon if p == "Lagna" else self.astronomical_anchors["mc_longitude"]
                    sid_pos = (ecl_target - ayanamsa_ecl) % 360.0
                    ra_val = sid_pos
                else:
                    ra_val = self.coordinates[p]["right_ascension"]
                    sid_pos = (ra_val - ayanamsa_eq) % 360.0

                n_idx = int(sid_pos / (360.0 / 27.0)) % 27
                pada = int((sid_pos % (360.0 / 27.0)) / (360.0 / 108.0)) + 1
                nak_lord = VIMSHOTTARI_SEQUENCE[n_idx % 9]
                nak_fraction = (sid_pos % (360.0 / 27.0)) / (360.0 / 27.0)
                sub_lord = calculate_sub_lord(nak_fraction, nak_lord)

                grahas_nak[p] = {
                    "nakshatra": NAKSHATRAS[n_idx],
                    "pada": pada,
                    "position": round(sid_pos, 4),
                    "sidereal_ra": round(ra_val, 4),
                    "sidereal_longitude": round(sid_pos, 4),
                    "nakshatra_lord": nak_lord,
                    "sub_lord": sub_lord,
                    "lord_sublord": f"{PLANET_ABBREVIATIONS.get(nak_lord, nak_lord[:2])}/{PLANET_ABBREVIATIONS.get(sub_lord, sub_lord[:2])}"
                }

        # Calculate Navatara (tara and tara_number relative to Moon)
        moon_nak_idx = NAKSHATRAS.index(grahas_nak["Moon"]["nakshatra"])
        for p, n_info in grahas_nak.items():
            t_nak_idx = NAKSHATRAS.index(n_info["nakshatra"])
            tara_idx = ((t_nak_idx - moon_nak_idx) % 27 % 9) + 1
            n_info["tara"] = tara_idx
            n_info["tara_number"] = tara_idx

        # Calculate complete Candra Kriyādi states (Phaladeepika Ch. 4.12–20)
        moon_nak_pos = grahas_nak["Moon"]["position"]
        moon_fraction = (moon_nak_pos % (360.0 / 27.0)) / (360.0 / 27.0)

        kriya_idx = min(59, int(moon_fraction * 60.0))
        k_num, k_name, k_trans, k_benefic = CHANDRA_KRIYAS_DATA[kriya_idx]

        avastha_idx = min(11, int(moon_fraction * 12.0))
        a_num, a_name, a_trans, a_benefic = CHANDRA_AVASTHAS_DATA[avastha_idx]

        vela_idx = min(35, int(moon_fraction * 36.0))
        v_num, v_name, v_trans, v_benefic = CHANDRA_VELAS_DATA[vela_idx]

        grahas_nak["Moon"]["candra_kriyadi"] = {
            "kriya": k_num,
            "kriya_name": k_name,
            "kriya_translation": k_trans,
            "kriya_nature": "Shubha / Auspicious" if k_benefic else "Ashubha / Inauspicious",
            "kriya_is_benefic": k_benefic,
            "avastha": a_num,
            "avastha_name": a_name,
            "avastha_translation": a_trans,
            "avastha_nature": "Shubha / Auspicious" if a_benefic else "Ashubha / Inauspicious",
            "avastha_is_benefic": a_benefic,
            "vela": v_num,
            "vela_name": v_name,
            "vela_translation": v_trans,
            "vela_nature": "Shubha / Auspicious" if v_benefic else "Ashubha / Inauspicious",
            "vela_is_benefic": v_benefic,
            "traversal_fraction": round(moon_fraction, 6)
        }

        return {
            "system": self.nakshatra_system,
            "ayanamsa": round(ayanamsa_lahiri if self.nakshatra_system == "VIC_CHITRA" else ayanamsa_ecl, 4),
            "equatorial_ayanamsa": round(ayanamsa_eq, 4),
            "ecliptic_ayanamsa": round(ayanamsa_ecl, 4),
            "grahas": grahas_nak
        }

    # =========================================================================
    # 7. DIVISIONAL VARGAS (16 Harmonic Charts + D60/D30 Specs on Bodies, Lagna & MC)
    # =========================================================================
    @cached_property
    def vargas(self) -> Dict[str, Dict[str, Any]]:
        """Decomposes coordinates across 16 divisional charts with D60, D30 on Grahas, Lagna, and MC."""
        bodies = self.astronomical_anchors["bodies"]
        d1_lons = {b: bodies[b]["longitude"] for b in ALL_BODIES}
        raw_cusps = self.astronomical_anchors["raw_campanus_cusps"]

        vargas_data = {}
        for v in VARGAS_LIST:
            v_grahas = {}
            for p in PLANETS_ORDER:
                if v == "D30":
                    t_info = calculate_unequal_trimsamsa(d1_lons[p])
                    h_lon = (d1_lons[p] * 30.0) % 360.0
                    h_idx = int(h_lon // 30)
                    g_entry = {
                        "longitude": t_info["longitude"],
                        "sign_index": t_info["sign_index"],
                        "sign": t_info["sign"],
                        "degree_0_to_30": t_info["degree_in_sign"],
                        "degree_in_sign": t_info["degree_in_sign"],
                        "continuous_harmonic_longitude": round(h_lon, 4),
                        "continuous_sign": ZODIAC_SIGNS[h_idx],
                        "continuous_degree_in_sign": round(h_lon % 30.0, 4),
                        "is_retrograde": bodies[p]["is_retrograde"],
                        "parashari_trimsamsa": t_info
                    }
                else:
                    v_lon = calculate_varga_longitude(d1_lons[p], v, self.d10_mode, self.d24_mode) % 360.0
                    s_idx = int(v_lon // 30)
                    deg_in_sign = round(v_lon % 30.0, 4)

                    g_entry = {
                        "longitude": round(v_lon, 4),
                        "sign_index": s_idx,
                        "sign": ZODIAC_SIGNS[s_idx],
                        "degree_0_to_30": deg_in_sign,
                        "degree_in_sign": deg_in_sign,
                        "is_retrograde": bodies[p]["is_retrograde"]
                    }
                    if v == "D1":
                        g_entry["latitude"] = bodies[p]["latitude"]
                    elif v == "D60":
                        g_entry["shastiamsa"] = calculate_shastiamsa_details(d1_lons[p])

                v_grahas[p] = g_entry

            if v == "D30":
                t_lagna = calculate_unequal_trimsamsa(d1_lons["Lagna"])
                h_l_lon = (d1_lons["Lagna"] * 30.0) % 360.0
                h_l_idx = int(h_l_lon // 30)
                v_lagna = {
                    "longitude": t_lagna["longitude"],
                    "sign_index": t_lagna["sign_index"],
                    "sign": t_lagna["sign"],
                    "degree_0_to_30": t_lagna["degree_in_sign"],
                    "degree_in_sign": t_lagna["degree_in_sign"],
                    "continuous_harmonic_longitude": round(h_l_lon, 4),
                    "continuous_sign": ZODIAC_SIGNS[h_l_idx],
                    "continuous_degree_in_sign": round(h_l_lon % 30.0, 4),
                    "parashari_trimsamsa": t_lagna
                }

                t_mc = calculate_unequal_trimsamsa(d1_lons["MC"])
                h_mc_lon = (d1_lons["MC"] * 30.0) % 360.0
                h_mc_idx = int(h_mc_lon // 30)
                v_mc = {
                    "longitude": t_mc["longitude"],
                    "sign_index": t_mc["sign_index"],
                    "sign": t_mc["sign"],
                    "degree_0_to_30": t_mc["degree_in_sign"],
                    "degree_in_sign": t_mc["degree_in_sign"],
                    "continuous_harmonic_longitude": round(h_mc_lon, 4),
                    "continuous_sign": ZODIAC_SIGNS[h_mc_idx],
                    "continuous_degree_in_sign": round(h_mc_lon % 30.0, 4),
                    "parashari_trimsamsa": t_mc
                }
            else:
                l_lon = calculate_varga_longitude(d1_lons["Lagna"], v, self.d10_mode, self.d24_mode) % 360.0
                l_idx = int(l_lon // 30)
                l_deg = round(l_lon % 30.0, 4)
                v_lagna = {
                    "longitude": round(l_lon, 4),
                    "sign_index": l_idx,
                    "sign": ZODIAC_SIGNS[l_idx],
                    "degree_0_to_30": l_deg,
                    "degree_in_sign": l_deg
                }

                # Project MC across all 16 divisional charts
                mc_v_lon = calculate_varga_longitude(d1_lons["MC"], v, self.d10_mode, self.d24_mode) % 360.0
                mc_idx = int(mc_v_lon // 30)
                mc_deg = round(mc_v_lon % 30.0, 4)
                v_mc = {
                    "longitude": round(mc_v_lon, 4),
                    "sign_index": mc_idx,
                    "sign": ZODIAC_SIGNS[mc_idx],
                    "degree_0_to_30": mc_deg,
                    "degree_in_sign": mc_deg
                }

                if v == "D60":
                    v_lagna["shastiamsa"] = calculate_shastiamsa_details(d1_lons["Lagna"])
                    v_mc["shastiamsa"] = calculate_shastiamsa_details(d1_lons["MC"])

            # Divisional projected cusps for SVG rendering
            v_cusps = []
            for c_lon in raw_cusps:
                if v == "D30":
                    t_c = calculate_unequal_trimsamsa(c_lon)
                    h_c_lon = (c_lon * 30.0) % 360.0
                    v_cusps.append({
                        "longitude": t_c["longitude"],
                        "sign_index": t_c["sign_index"],
                        "sign": t_c["sign"],
                        "degree_0_to_30": t_c["degree_in_sign"],
                        "degree_in_sign": t_c["degree_in_sign"],
                        "continuous_harmonic_longitude": round(h_c_lon, 4)
                    })
                else:
                    vc_lon = calculate_varga_longitude(c_lon, v, self.d10_mode, self.d24_mode) % 360.0
                    c_s_idx = int(vc_lon // 30)
                    v_cusps.append({
                        "longitude": round(vc_lon, 4),
                        "sign_index": c_s_idx,
                        "sign": ZODIAC_SIGNS[c_s_idx],
                        "degree_0_to_30": round(vc_lon % 30.0, 4),
                        "degree_in_sign": round(vc_lon % 30.0, 4)
                    })

            vargas_data[v] = {
                "varga": v,
                "lagna": v_lagna,
                "mc": v_mc,
                "grahas": v_grahas,
                "cusps": v_cusps,
                "bhavas": []
            }
        return vargas_data

    # =========================================================================
    # 8. CONJUNCTIONS & CROSS-BORDER WALL LEAKAGE
    # =========================================================================
    @cached_property
    def conjunctions(self) -> List[Dict[str, Any]]:
        """Finds all conjunctions <= 10.0° with cross-border wall leakage attenuation (0.75)."""
        coords = self.coordinates
        dist = self.shortest_distance_matrix
        active_conjunctions = []

        evaluation_bodies = PLANETS_ORDER + ["Lagna"]
        checked_pairs = set()

        for i, b1 in enumerate(evaluation_bodies):
            for j in range(i + 1, len(evaluation_bodies)):
                b2 = evaluation_bodies[j]
                pair = tuple(sorted([b1, b2]))
                if pair in checked_pairs:
                    continue
                checked_pairs.add(pair)

                separation = dist[b1][b2]
                if separation <= 10.0:
                    same_sign = (coords[b1]["sign_index"] == coords[b2]["sign_index"])
                    boundary_factor = 1.0 if same_sign else 0.75
                    proximity_ratio = max(0.0, 1.0 - (separation / 10.0))
                    effective_potency = round(proximity_ratio * boundary_factor, 4)
                    band = "Exact (Intimate)" if separation <= (10.0 / 3.0) else ("Moderate" if separation <= 7.0 else "Wide")

                    active_conjunctions.append({
                        "body1": b1,
                        "body2": b2,
                        "separation_degrees": round(separation, 4),
                        "orb_band": band,
                        "same_sign": same_sign,
                        "cross_border": not same_sign,
                        "boundary_factor": boundary_factor,
                        "effective_potency": effective_potency,
                        "sign1": coords[b1]["sign"],
                        "sign2": coords[b2]["sign"]
                    })
        return active_conjunctions

    @cached_property
    def conjunctions_by_body(self) -> Dict[str, List[Dict[str, Any]]]:
        """O(1) lookup mapping each body to its active conjunctions."""
        by_body: Dict[str, List[Dict[str, Any]]] = {b: [] for b in ALL_BODIES}
        for c in self.conjunctions:
            b1 = c["body1"]
            b2 = c["body2"]
            by_body[b1].append({**c, "other_body": b2})
            by_body[b2].append({**c, "other_body": b1})
        return by_body

    @cached_property
    def combustion_status(self) -> Dict[str, Dict[str, Any]]:
        """Evaluates Surya Siddhanta combustion and orb severity."""
        dist = self.shortest_distance_matrix
        status = {
            "Sun": {"is_combust": False, "separation": 0.0, "sun_distance": 0.0, "orb_limit": 0.0, "combustion_orb": 0.0, "severity": "None", "combustion_severity": "None", "combustion_range": "None"},
            "Rahu": {"is_combust": False, "separation": 0.0, "sun_distance": 0.0, "orb_limit": 0.0, "combustion_orb": 0.0, "severity": "None", "combustion_severity": "None", "combustion_range": "None"},
            "Ketu": {"is_combust": False, "separation": 0.0, "sun_distance": 0.0, "orb_limit": 0.0, "combustion_orb": 0.0, "severity": "None", "combustion_severity": "None", "combustion_range": "None"}
        }

        comb_ranges = {
            "Moon": "12° - 15°", "Mars": "8° - 17°", "Mercury": "2° - 14°",
            "Jupiter": "8° - 11°", "Venus": "4° - 10°", "Saturn": "8° - 15°"
        }

        for p in ["Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
            sep = dist["Sun"][p]
            is_retro = self.coordinates[p]["is_retrograde"]
            orb = COMBUSTION_ORBS[p]
            if p == "Venus" and is_retro:
                orb = 8.0
            elif p == "Mercury" and is_retro:
                orb = 12.0

            is_combust = bool(sep <= orb)
            severity = "Deep (< 3°)" if (is_combust and sep < 3.0) else ("Moderate" if is_combust else "None")

            status[p] = {
                "is_combust": is_combust,
                "separation": round(sep, 4),
                "sun_distance": round(sep, 4),
                "orb_limit": orb,
                "combustion_orb": orb,
                "severity": severity,
                "combustion_severity": severity,
                "combustion_range": comb_ranges.get(p, f"{orb}°")
            }
        return status

    @cached_property
    def lunar_phase(self) -> Dict[str, Any]:
        """Static lunar elongation, illumination, and benefic classification."""
        elongation = self.separation_matrix["Sun"]["Moon"]
        is_waxing = (elongation <= 180.0)
        dist_from_sun = min(elongation, 360.0 - elongation)
        illumination_pct = round((dist_from_sun / 180.0) * 100.0, 1)

        return {
            "elongation_degrees": round(elongation, 2),
            "is_waxing": is_waxing,
            "paksha": "Shukla" if is_waxing else "Krishna",
            "illumination_pct": illumination_pct,
            "is_bright": bool(illumination_pct >= 50.0),
            "is_benefic": bool(illumination_pct >= 50.0)
        }

    # =========================================================================
    # 9. SERIALIZATION & RE-EXPORT
    # =========================================================================
    def to_dict(self) -> Dict[str, Any]:
        """Exports the complete baseline coordinate state as JSON-serializable primitives."""
        return {
            "name": self.name,
            "place": self.place,
            "astronomical_anchors": {
                "jd_local": self.astronomical_anchors["jd_local"],
                "jd_utc": self.astronomical_anchors["jd_utc"],
                "cal_flag": self.astronomical_anchors["cal_flag"],
                "sunrise_jd": self.astronomical_anchors["sunrise_jd"],
                "sunset_jd": self.astronomical_anchors["sunset_jd"],
                "next_sunrise_jd": self.astronomical_anchors["next_sunrise_jd"],
                "is_day_birth": self.astronomical_anchors["is_day_birth"],
                "asc_longitude": self.astronomical_anchors["asc_longitude"],
                "mc_longitude": self.astronomical_anchors["mc_longitude"],
                "sensitive_cusp_degree": self.astronomical_anchors["sensitive_cusp_degree"],
                "temporal_lords": self.astronomical_anchors["temporal_lords"],
                "campanus_display_cusps": self.astronomical_anchors["campanus_display_cusps"]
            },
            "coordinates": self.coordinates,
            "upagrahas": self.upagrahas,
            "pancanga": self.pancanga,
            "special_sphutas": self.special_sphutas,
            "nakshatras": self.nakshatras,
            "vargas": self.vargas,
            "combustion_status": self.combustion_status,
            "lunar_phase": self.lunar_phase,
            "planetary_wars": self.planetary_wars,
            "conjunctions": self.conjunctions
        }


__all__ = [
    "ChartBaseline",
    # Tables & Constants
    "PLANETS_ORDER",
    "ALL_BODIES",
    "TARA_GRAHAS",
    "PLANET_ABBREVIATIONS",
    "ZODIAC_SIGNS",
    "SIGN_LORDS",
    "NAKSHATRAS",
    "NITYA_YOGAS",
    "VIMSHOTTARI_SEQUENCE",
    "VIMSHOTTARI_YEARS",
    "COMBUSTION_ORBS",
    "VARGAS_LIST",
    "SHASTIAMSA_DEITIES",
    "SHASTIAMSA_MALEFIC_ODD",
    "CHANDRA_KRIYAS_DATA",
    "CHANDRA_AVASTHAS_DATA",
    "CHANDRA_VELAS_DATA",
    # Math & Algorithms
    "calculate_sub_lord",
    "calculate_varga_longitude",
    "calculate_unequal_trimsamsa",
    "calculate_shastiamsa_details",
    "calculate_baladi_state",
    "get_eq_from_ecl",
    "find_preceding_solar_crossing",
]
