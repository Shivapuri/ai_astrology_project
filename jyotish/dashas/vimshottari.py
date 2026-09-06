"""
Vimshottari Dasa Calculation Engine.

Implements the 120-year Parashari Vimshottari Dasa timeline calibrated to Ernst Wilhelm's
Kala software setup.

Ground Truth & Astronomical Authority:
- Brihat Parashara Hora Shastra (BPHS), Chapters 46 & 49: Dasha order, ruler years, and
  proportional Antardasha (Bhukti) division.
- Kala System Configuration:
  * Year Length: Saura (Solar Year) = 365.2422 days (Surya Siddhanta).
  * Zodiac / Anchor: Moon Sidereal Equatorial Right Ascension (Dhruva Galactic Center, Middle of Mula).
"""

from typing import List, Dict, Any, Tuple
import swisseph as swe

# 1. Classical Vimshottari Configuration
DASHA_LORDS: List[str] = [
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"
]

DASHA_YEARS: Dict[str, int] = {
    "Ketu": 7,
    "Venus": 20,
    "Sun": 6,
    "Moon": 10,
    "Mars": 7,
    "Rahu": 18,
    "Jupiter": 16,
    "Saturn": 19,
    "Mercury": 17,
}

VIMSHOTTARI_CYCLE_YEARS: int = 120

# Saura Year length in days (Surya Siddhanta solar year as configured in Kala)
SAURA_YEAR_DAYS: float = 365.2422

# Nakshatra span in degrees (360° / 27 = 13° 20' = 13.333333333333334°)
NAKSHATRA_SPAN: float = 360.0 / 27.0

# Two-letter abbreviations for compact period notation (e.g. Me/Me, Me/Ke)
LORD_TO_ABBR: Dict[str, str] = {
    "Sun": "Su",
    "Moon": "Mo",
    "Mars": "Ma",
    "Mercury": "Me",
    "Jupiter": "Ju",
    "Venus": "Ve",
    "Saturn": "Sa",
    "Rahu": "Ra",
    "Ketu": "Ke"
}

ABBR_TO_LORD: Dict[str, str] = {v: k for k, v in LORD_TO_ABBR.items()}


def format_jd_datetime(jd: float, cal_flag: int = swe.GREG_CAL) -> Tuple[str, str, str]:
    """
    Converts a Julian Day to formatted ISO date (YYYY-MM-DD), US date (MM/DD/YYYY),
    and 24-hour time (HH:MM).
    """
    year, month, day, ut_hour_frac = swe.revjul(jd, cal_flag)
    hh = int(ut_hour_frac)
    mm = int(round((ut_hour_frac - hh) * 60.0))
    if mm >= 60:
        hh += 1
        mm = 0
    if hh >= 24:
        # Wrap day if clock rounds past midnight
        next_jd = swe.julday(year, month, day, 0.0, cal_flag) + (hh / 24.0)
        year, month, day, ut_hour_frac = swe.revjul(next_jd, cal_flag)
        hh = int(ut_hour_frac)
        mm = int(round((ut_hour_frac - hh) * 60.0))

    iso_date = f"{year:04d}-{month:02d}-{day:02d}"
    us_date = f"{month:02d}/{day:02d}/{year:04d}"
    time_str = f"{hh:02d}:{mm:02d}"
    return iso_date, us_date, time_str


def calculate_vimshottari_timeline(
    moon_sidereal_ra: float,
    birth_jd_local: float,
    cal_flag: int = swe.GREG_CAL,
    total_cycles: int = 1,
    dasha_year_days: float = SAURA_YEAR_DAYS
) -> Dict[str, Any]:
    """
    Calculates the full Vimshottari Dasa timeline (all Mahadashas and Antardashas).

    Args:
        moon_sidereal_ra: Moon's Right Ascension in the Sidereal Equatorial frame (0-360°).
        birth_jd_local: Local Julian Day of birth.
        cal_flag: Calendar flag (swe.GREG_CAL or swe.JUL_CAL).
        total_cycles: Number of 120-year cycles to compute (default 1).
        dasha_year_days: Number of days in one dasha year (default Saura 365.2422).

    Returns:
        Dictionary containing:
        - 'at_birth': Balance of the birth Mahadasha at the exact time of birth.
        - 'year_length_days': Year length constant used.
        - 'mahadashas': List of Mahadasha dictionaries (with nested Antardashas).
        - 'antardashas': Flattened list of all Antardashas across the cycle.
    """
    # 1. Identify Nakshatra and Mahadasha Lord at birth
    nak_idx = int(moon_sidereal_ra / NAKSHATRA_SPAN) % 27
    lord_idx = nak_idx % 9
    birth_md_lord = DASHA_LORDS[lord_idx]

    # 2. Elapsed and Remaining Balance in the birth Nakshatra
    deg_in_nak = moon_sidereal_ra % NAKSHATRA_SPAN
    fraction_passed = deg_in_nak / NAKSHATRA_SPAN
    fraction_left = 1.0 - fraction_passed

    total_birth_md_years = DASHA_YEARS[birth_md_lord]
    balance_years = fraction_left * total_birth_md_years
    balance_days = balance_years * dasha_year_days

    # 3. Establish timeline anchor points
    birth_md_end_jd = birth_jd_local + balance_days
    birth_md_start_jd = birth_md_end_jd - (total_birth_md_years * dasha_year_days)

    mahadashas_list: List[Dict[str, Any]] = []
    antardashas_flat: List[Dict[str, Any]] = []

    current_jd = birth_md_start_jd

    # 4. Generate Mahadashas and nested Antardashas
    for cycle in range(total_cycles):
        for m_offset in range(9):
            m_idx = (lord_idx + m_offset) % 9
            m_lord = DASHA_LORDS[m_idx]
            m_years = DASHA_YEARS[m_lord]
            m_dur_days = m_years * dasha_year_days

            m_start_jd = current_jd
            m_end_jd = m_start_jd + m_dur_days

            m_iso_s, m_us_s, m_time_s = format_jd_datetime(m_start_jd, cal_flag)
            m_iso_e, m_us_e, m_time_e = format_jd_datetime(m_end_jd, cal_flag)

            antardashas_for_md: List[Dict[str, Any]] = []

            # 9 Antardashas within this Mahadasha
            for a_offset in range(9):
                a_idx = (m_idx + a_offset) % 9
                a_lord = DASHA_LORDS[a_idx]
                a_years = DASHA_YEARS[a_lord]
                
                # Proportional duration: (MahaYears * AntarYears / 120) * YearDays
                a_dur_days = (m_years * a_years / 120.0) * dasha_year_days
                a_start_jd = current_jd
                a_end_jd = a_start_jd + a_dur_days

                a_iso_s, a_us_s, a_time_s = format_jd_datetime(a_start_jd, cal_flag)
                a_iso_e, a_us_e, a_time_e = format_jd_datetime(a_end_jd, cal_flag)

                period_code = f"{LORD_TO_ABBR[m_lord]}/{LORD_TO_ABBR[a_lord]}"

                antar_dict = {
                    "period": period_code,
                    "mahadasha_lord": m_lord,
                    "antardasha_lord": a_lord,
                    "duration_days": round(a_dur_days, 4),
                    "start_jd": a_start_jd,
                    "end_jd": a_end_jd,
                    "start_date": a_iso_s,
                    "start_date_us": a_us_s,
                    "start_time": a_time_s,
                    "end_date": a_iso_e,
                    "end_date_us": a_us_e,
                    "end_time": a_time_e,
                    "is_past_at_birth": a_end_jd <= birth_jd_local,
                    "is_current_at_birth": (a_start_jd <= birth_jd_local < a_end_jd),
                }

                antardashas_for_md.append(antar_dict)
                antardashas_flat.append(antar_dict)

                current_jd = a_end_jd

            maha_dict = {
                "planet": m_lord,  # Compatible with existing generate_jyotish keys
                "lord": m_lord,
                "years": m_years,
                "duration_days": round(m_dur_days, 4),
                "start": m_iso_s,   # Compatible with existing generate_jyotish keys ("YYYY-MM-DD")
                "end": m_iso_e,     # Compatible with existing generate_jyotish keys ("YYYY-MM-DD")
                "start_date_us": m_us_s,
                "end_date_us": m_us_e,
                "start_time": m_time_s,
                "end_time": m_time_e,
                "start_jd": m_start_jd,
                "end_jd": m_end_jd,
                "antardashas": antardashas_for_md,
            }
            mahadashas_list.append(maha_dict)

    return {
        "at_birth": {
            "mahadasha": birth_md_lord,
            "mahadasha_balance_years": round(balance_years, 4),
            "mahadasha_balance_days": round(balance_days, 4),
            "fraction_passed": round(fraction_passed, 6),
            "fraction_left": round(fraction_left, 6),
            "birth_jd_local": birth_jd_local,
        },
        "year_length_days": dasha_year_days,
        "mahadashas": mahadashas_list,
        "antardashas": antardashas_flat,
    }
