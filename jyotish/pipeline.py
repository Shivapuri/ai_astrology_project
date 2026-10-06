"""
jyotish/pipeline.py
Unified Astrological Calculation Pipeline (Single Source of Truth DAG)

Orchestrates Stages 1 through 4:
- Stage 1: ChartBaseline (Ephemeris, Coordinates, Sensitive Points, Vargas, Upagrahas, Distances)
- Stage 2A: Relationships & Aspect Matrices (Dignities, Graha Drishti, Maitri)
- Stage 2B: Planetary Strengths & Balas (Shadbala, Quantitative/Qualitative Avasthas, Vimshopaka)
- Stage 3: House Capacity & Diagnostic Cockpit (Bhava Bala, Harsha Bala, House Atmosphere, Master Diagnostic)
- Stage 4: Downstream Synthesis (Classical Yogas, Dashas, Ashtakavarga, Karakas, Narrative Report)
"""

from functools import cached_property
from typing import Dict, Any, Optional, List
import copy
import math

from jyotish.baseline import (
    ChartBaseline,
    calculate_varga_longitude,
    ZODIAC_SIGNS,
    NAKSHATRAS,
    NITYA_YOGAS,
    calculate_sub_lord,
    VIMSHOTTARI_SEQUENCE,
    VIMSHOTTARI_YEARS,
)
import jyotish.relationships.relationships as rel
import jyotish.aspects.aspects as aspects
from jyotish.shadbala.shadbala import calculate_shadbala
from jyotish.bhavas.bhava_bala import (
    calculate_bhava_bala,
    calculate_harsha_bala,
    calculate_house_atmosphere,
)
import jyotish.avasthas as avasthas
from jyotish.dashas.vimshottari import calculate_vimshottari_timeline, SAURA_YEAR_DAYS
import jyotish.vimshopaka as vimshopaka
import jyotish.ashtakavarga as ashtakavarga
import jyotish.karakas as karakas
import jyotish.sign_attributes as sign_attributes
import jyotish.planetary_evaluation as planetary_evaluation
import jyotish.report.report_engine as report_engine


DASHA_LORDS = ['Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury']
DASHA_YEARS = [7, 20, 6, 10, 7, 18, 16, 19, 17]

MEAN_DAILY_SPEEDS = {
    "Sun": 0.9856,
    "Moon": 13.1764,
    "Mars": 0.5240,
    "Mercury": 1.3833,
    "Jupiter": 0.0831,
    "Venus": 1.2000,
    "Saturn": 0.0335,
    "Rahu": 0.05295,
    "Ketu": 0.05295
}

KALA_MEAN_DAILY_SPEEDS = {
    "Sun": 0.9856,
    "Moon": 13.1764,
    "Mars": 0.5240,
    "Mercury": 0.9856,
    "Jupiter": 0.0831,
    "Venus": 0.9856,
    "Saturn": 0.0334568,
    "Rahu": 0.05295,
    "Ketu": 0.05295
}

PLANET_ABBREVIATIONS = {
    "Sun": "Su", "Moon": "Mo", "Mars": "Ma", "Mercury": "Me",
    "Jupiter": "Ju", "Venus": "Ve", "Saturn": "Sa", "Rahu": "Ra", "Ketu": "Ke",
    "Lagna": "Lg"
}

VARGAS_HARMONICS = {
    "D1": 1, "D2": 2, "D3": 3, "D4": 4, "D7": 7, "D9": 9, 
    "D10": 10, "D12": 12, "D16": 16, "D20": 20, "D24": 24, 
    "D27": 27, "D30": 30, "D40": 40, "D45": 45, "D60": 60
}


def get_sign(longitude: float) -> tuple[str, float]:
    sign_idx = int(longitude // 30)
    deg_in_sign = longitude % 30
    return ZODIAC_SIGNS[sign_idx], round(deg_in_sign, 2)


class ChartPipeline:
    """
    Unified Astrological Pipeline Container.
    Evaluates stages lazily via @cached_property and serves typed accessors
    or complete serialized JSON dictionaries for downstream consumers.
    """

    def __init__(
        self,
        name: str = "Subject",
        year: int = 1995,
        month: int = 5,
        day: int = 15,
        hour: int = 14,
        minute: int = 30,
        second: int = 0,
        latitude: float = 51.5074,
        longitude: float = -0.1278,
        timezone_offset: float = 1.0,
        place: str = "",
        name_sound_value: Optional[int] = None,
        d10_mode: str = "reverse",
        d24_mode: str = "reverse",
        nakshatra_system: str = "ERNST_DHRUVA",
        debilitation_mode: str = "kala_degree",
        dig_bala_mode: str = "campanus",
        kendra_bala_mode: str = "flat_parashara",
        phala_mode: Optional[str] = None,
        pillar_mode: str = "kala_breakdown",
        trimsamsa_mode: Optional[str] = None,
        saptavarga_mode: Optional[str] = None,
        drik_mode: Optional[str] = None,
        ayana_tradition: str = "parashara",
        baseline: Optional[ChartBaseline] = None
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
        self.name_sound_value = name_sound_value
        self.d10_mode = d10_mode
        self.d24_mode = d24_mode
        self.nakshatra_system = nakshatra_system
        self.debilitation_mode = debilitation_mode
        self.dig_bala_mode = dig_bala_mode
        self.kendra_bala_mode = kendra_bala_mode
        self.phala_mode = phala_mode
        self.pillar_mode = pillar_mode
        self.trimsamsa_mode = trimsamsa_mode
        self.saptavarga_mode = saptavarga_mode
        self.drik_mode = drik_mode
        self.ayana_tradition = ayana_tradition
        self._provided_baseline = baseline

    # =========================================================================
    # STAGE 1: Astronomical & Coordinate Baseline
    # =========================================================================
    @cached_property
    def baseline(self) -> ChartBaseline:
        if self._provided_baseline is not None:
            return self._provided_baseline
        return ChartBaseline(
            name=self.name,
            year=self.year,
            month=self.month,
            day=self.day,
            hour=self.hour,
            minute=self.minute,
            second=self.second,
            latitude=self.latitude,
            longitude=self.longitude,
            timezone_offset=self.timezone_offset,
            place=self.place,
            d10_mode=self.d10_mode,
            d24_mode=self.d24_mode,
            nakshatra_system=self.nakshatra_system
        )

    # =========================================================================
    # STAGE 2A: Dignities & Aspect Matrices
    # =========================================================================
    @cached_property
    def dignities(self) -> Dict[str, Any]:
        return rel.calculate_chart_dignities(self.baseline, debilitation_mode=self.debilitation_mode)

    @cached_property
    def aspect_matrices(self) -> Dict[str, Any]:
        return aspects.calculate_aspect_matrices(self.baseline)

    # =========================================================================
    # STAGE 2B: Shadbala (6-fold planetary strength)
    # =========================================================================
    @cached_property
    def shadbala(self) -> Dict[str, Any]:
        raw_shadbala = calculate_shadbala(
            self.baseline,
            dignities=self.dignities,
            aspect_matrices=self.aspect_matrices,
            debilitation_mode=self.debilitation_mode,
            dig_bala_mode=self.dig_bala_mode,
            kendra_bala_mode=self.kendra_bala_mode,
            phala_mode=self.phala_mode,
            pillar_mode=self.pillar_mode,
            trimsamsa_mode=self.trimsamsa_mode,
            saptavarga_mode=self.saptavarga_mode,
            drik_mode=self.drik_mode,
            ayana_tradition=self.ayana_tradition
        )
        enriched = {}
        for p, vals in raw_shadbala.items():
            if isinstance(vals, dict):
                p_dict = dict(vals)
                # Lowercase aliases expected by app.js updateShadbalaTable
                p_dict.setdefault("sthana_bala", p_dict.get("Sthana_Bala", 0.0))
                p_dict.setdefault("dig_bala", p_dict.get("Dig_Bala", 0.0))
                p_dict.setdefault("kala_bala", p_dict.get("Kala_Bala", 0.0))
                p_dict.setdefault("cheshta_bala", p_dict.get("Cheshta_Bala", 0.0))
                p_dict.setdefault("naisargika_bala", p_dict.get("Naisargika_Bala", 0.0))
                p_dict.setdefault("drik_bala", p_dict.get("Drik_Bala", 0.0))
                p_dict.setdefault("total_rupa", p_dict.get("Total_Rupas", 0.0))
                p_dict.setdefault("total_virupas", p_dict.get("Total_Virupas", 0.0))
                req_tot = p_dict.get("Required_Total", 0.0)
                p_dict.setdefault("required_rupa", round(req_tot / 60.0, 2) if req_tot else 0.0)
                p_dict.setdefault("required_total", req_tot)
                pct_req = p_dict.get("Pct_Required_Total")
                p_dict.setdefault("ratio", (pct_req / 100.0) if pct_req is not None else ((p_dict.get("Total_Virupas", 0.0) / req_tot) if req_tot else 1.0))
                enriched[p] = p_dict
            else:
                enriched[p] = vals
        return enriched

    # =========================================================================
    # STAGE 3: House Capabilities, Bhava Bala & Master Cockpit
    # =========================================================================
    @cached_property
    def bhava_bala(self) -> Dict[str, Any]:
        return calculate_bhava_bala(
            baseline=self.baseline,
            shadbala_results=self.shadbala,
            aspect_matrices=self.aspect_matrices
        )

    @cached_property
    def harsha_bala(self) -> Dict[str, Any]:
        return calculate_harsha_bala(
            baseline=self.baseline
        )

    @cached_property
    def house_atmosphere(self) -> Dict[str, Any]:
        return calculate_house_atmosphere(
            baseline=self.baseline,
            bhava_results=self.bhava_bala,
            harsha_data=self.harsha_bala,
            aspect_matrices=self.aspect_matrices
        )

    @cached_property
    def master_diagnostic(self) -> Dict[str, Any]:
        return planetary_evaluation.generate_master_diagnostic_payload(
            baseline=self.baseline,
            shadbala_results=self.shadbala,
            dignities=self.dignities,
            aspect_matrices=self.aspect_matrices,
            bhava_results=self.bhava_bala,
            planetary_evaluation=self.planetary_evaluation
        )

    # =========================================================================
    # ENRICHED DIVISIONAL VARGAS (Bhavas, Dignities, Avasthas, Combustion, Nodes)
    # =========================================================================
    @cached_property
    def vargas(self) -> Dict[str, Any]:
        vargas_data = copy.deepcopy(self.baseline.vargas)
        coords = self.baseline.coordinates
        anchors = self.baseline.astronomical_anchors
        jd = anchors["jd_utc"]
        d1_longitudes = {p: coords[p]["longitude"] for p in coords}

        # Harmonize D30 coordinates for Kala harmonic varga calculations
        if "D30" in vargas_data:
            for p_name, g_entry in vargas_data["D30"]["grahas"].items():
                if "continuous_harmonic_longitude" in g_entry:
                    g_entry["longitude"] = g_entry["continuous_harmonic_longitude"]
                    g_entry["sign"] = g_entry["continuous_sign"]
                    g_entry["degree_0_to_30"] = g_entry["continuous_degree_in_sign"]
            if "lagna" in vargas_data["D30"] and "continuous_harmonic_longitude" in vargas_data["D30"]["lagna"]:
                vargas_data["D30"]["lagna"]["longitude"] = vargas_data["D30"]["lagna"]["continuous_harmonic_longitude"]
                vargas_data["D30"]["lagna"]["sign"] = vargas_data["D30"]["lagna"]["continuous_sign"]
                vargas_data["D30"]["lagna"]["degree_0_to_30"] = vargas_data["D30"]["lagna"]["continuous_degree_in_sign"]

        # Populate bhava occupancy for each varga (pure math, zero ephemeris)
        for v_name, v_dict in vargas_data.items():
            v_cusps = [c["longitude"] for c in v_dict.get("cusps", [])]
            if len(v_cusps) == 12:
                bhavas = []
                for i in range(12):
                    prev_cusp = v_cusps[(i - 1) % 12]
                    curr_cusp = v_cusps[i]
                    next_cusp = v_cusps[(i + 1) % 12]

                    diff_prev = (curr_cusp - prev_cusp) % 360.0
                    start = (prev_cusp + diff_prev / 2.0) % 360.0
                    diff_next = (next_cusp - curr_cusp) % 360.0
                    end = (curr_cusp + diff_next / 2.0) % 360.0

                    bhavas.append({
                        "house": i + 1,
                        "start": round(start, 4),
                        "cusp": round(curr_cusp, 4),
                        "end": round(end, 4),
                        "planets": []
                    })

                for p_name in ["Lagna", "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
                    p_lon = v_dict["lagna"]["longitude"] if p_name == "Lagna" else v_dict["grahas"][p_name]["longitude"]
                    for bhava in bhavas:
                        s = bhava["start"]
                        e = bhava["end"]
                        in_house = (s <= p_lon < e) if s <= e else (p_lon >= s or p_lon < e)
                        if in_house:
                            bhava["planets"].append(p_name if p_name != "Lagna" else "Asc")
                v_dict["bhavas"] = bhavas

        d1_grahas = vargas_data["D1"]["grahas"]

        # Planetary Friendships, Dignity & Avasthas across all Vargas (Direct Single Source of Truth)
        varga_dignities = self.dignities.get("varga_dignities", {})
        comb_status = self.baseline.combustion_status

        for v_name, v_data in vargas_data.items():
            for p_name, p_data in v_data["grahas"].items():
                p_deg = p_data.get("degree_0_to_30", 0.0)
                v_dig = varga_dignities.get(v_name, {}).get(p_name, {})
                sign_lord = v_dig.get("sign_lord", rel.SIGN_LORDS.get(p_data["sign"], ""))
                nat_rel = v_dig.get("natural_relationship", "Neutral")
                tmp_rel = v_dig.get("temporary_relationship", "Neutral")
                cmp_rel = v_dig.get("compound_relationship", "Neutral")
                cmp_dig = v_dig.get("dignity", "Neutral")

                # Natural dignity (based on natural relationship without temporal modifier)
                if nat_rel == "Self":
                    nat_dig = cmp_dig
                else:
                    nat_dig = rel.get_dignity(
                        p_name,
                        p_data["sign"],
                        nat_rel,
                        p_deg,
                        debilitation_mode=self.debilitation_mode,
                        is_varga=(v_name != "D1")
                    )

                p_data["dignity_breakdown"] = {
                    "sign_lord": sign_lord,
                    "natural_relationship": nat_rel,
                    "temporary_relationship": tmp_rel,
                    "compound_relationship": cmp_rel,
                    "natural_dignity": nat_dig,
                    "final_dignity": cmp_dig,
                    "dignity": cmp_dig,
                    "avastha": v_dig.get("avastha", "")
                }
                p_data["dignity"] = cmp_dig
                
                # Conjunct planets in this varga
                conjunct_planets = [
                    op_name for op_name, op_data in v_data["grahas"].items()
                    if op_name != p_name and op_data["sign"] == p_data["sign"]
                ]
                
                # Aspecting planets
                aspecting_planets = []
                graha_aspecting_planets = []
                for op_name, op_data in v_data["grahas"].items():
                    if op_name != p_name:
                        rasi_aspects = aspects.get_rasi_drishti(op_data["sign"])
                        if p_data["sign"] in rasi_aspects:
                            aspecting_planets.append(op_name)
                        
                        g_drishti = aspects.get_graha_drishti(
                            op_name, 
                            op_data["longitude"], 
                            p_data["longitude"], 
                            op_data["sign"], 
                            p_data["sign"]
                        )
                        if g_drishti > 0:
                            graha_aspecting_planets.append(op_name)
                            
                p_data["aspects_signs"] = aspects.get_rasi_drishti(p_data["sign"])
                is_retrograde = p_data.get("is_retrograde", False)

                # Combustion (Physical phenomenon, sourced directly from certified baseline)
                if p_name in ("Sun", "Rahu", "Ketu"):
                    is_combust = False
                    p_data["is_combust"] = False
                    p_data["sun_distance"] = None
                    p_data["combustion_orb"] = None
                    p_data["combustion_severity"] = "None"
                    p_data["combustion_range"] = "None"
                else:
                    c_info = comb_status.get(p_name, {})
                    is_combust = c_info.get("is_combust", False)
                    p_data["is_combust"] = is_combust
                    p_data["sun_distance"] = c_info.get("sun_distance")
                    p_data["combustion_orb"] = c_info.get("combustion_orb")
                    p_data["combustion_severity"] = c_info.get("combustion_severity")
                    p_data["combustion_range"] = c_info.get("combustion_range")
                
                lagna_sign = v_data["lagna"]["sign"]
                lagna_idx = ZODIAC_SIGNS.index(lagna_sign)
                p_idx = ZODIAC_SIGNS.index(p_data["sign"])
                house_num = (p_idx - lagna_idx) % 12 + 1
                
                p_data["ruled_houses"] = [
                    (s_idx - lagna_idx) % 12 + 1
                    for s_idx, s_name in enumerate(ZODIAC_SIGNS)
                    if rel.SIGN_LORDS.get(s_name) == p_name
                ]
                
                if p_name in ["Rahu", "Ketu"]:
                    proxy = "Saturn" if p_name == "Rahu" else "Mars"
                    natural_friends = rel.NAISARGIKA_SAMBANDHA.get(proxy, {}).get("Friends", [])
                    natural_enemies = rel.NAISARGIKA_SAMBANDHA.get(proxy, {}).get("Enemies", [])
                else:
                    natural_friends = rel.NAISARGIKA_SAMBANDHA.get(p_name, {}).get("Friends", [])
                    natural_enemies = rel.NAISARGIKA_SAMBANDHA.get(p_name, {}).get("Enemies", [])

                bala_avastha = avasthas.get_bala_avastha(p_deg, p_data["sign"])
                jagrat_avastha = avasthas.get_jagrat_avastha(p_data["dignity_breakdown"]["natural_dignity"])
                deeptadi_avastha = avasthas.get_deeptadi_avastha(
                    p_data["dignity_breakdown"]["final_dignity"],
                    is_retrograde,
                    is_combust,
                    conjunct_planets
                )
                
                moon_lon = d1_longitudes["Moon"]
                sun_lon_d1 = d1_longitudes["Sun"]
                is_moon_waning = ((moon_lon - sun_lon_d1) % 360.0) >= 180.0
                is_waning_moon_as_enemy = is_moon_waning and ("Moon" in natural_enemies)
                
                lajjitadi_avastha = avasthas.get_lajjitadi_avasthas(
                    p_name,
                    p_data["sign"],
                    house_num,
                    p_data["dignity_breakdown"]["natural_dignity"],
                    conjunct_planets,
                    graha_aspecting_planets,
                    natural_friends,
                    natural_enemies,
                    is_waning_moon_as_enemy
                )
                
                p_data["avasthas"] = {
                    "bala": bala_avastha,
                    "jagrat": jagrat_avastha,
                    "deeptadi": deeptadi_avastha,
                    "lajjitadi": lajjitadi_avastha
                }

        # Certified Stage 1 Nakshatras & Speeds
        nakshatras_sidereal = self.baseline.nakshatras["grahas"]
        d1_speeds = {}
        d1_rel_speeds = {"Lagna": "--"}
        d1_rel_speeds_pct = {}
        for p_name in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
            spd = coords[p_name]["speed"]
            if p_name in ["Rahu", "Ketu"]:
                r_lon_rad = math.radians(coords[p_name]["longitude"])
                eps_rad = math.radians(23.4392911)
                d_ra_d_lon = math.cos(eps_rad) / (1.0 - math.sin(eps_rad)**2 * math.sin(r_lon_rad)**2)
                spd = -abs(spd * d_ra_d_lon * (1.0 - 0.0053))
            d1_speeds[p_name] = round(spd, 4)
            mean_speed = KALA_MEAN_DAILY_SPEEDS.get(p_name, 1.0)
            ratio = (spd / mean_speed) * 100.0 if mean_speed > 0 else 100.0
            d1_rel_speeds[p_name] = f"{ratio:.2f}%"
            d1_rel_speeds_pct[p_name] = round(ratio, 2)

        moon_nak_idx = NAKSHATRAS.index(nakshatras_sidereal["Moon"]["nakshatra"])
        for ent_name, n_info in nakshatras_sidereal.items():
            t_nak_idx = NAKSHATRAS.index(n_info["nakshatra"])
            tara_idx = ((t_nak_idx - moon_nak_idx) % 27 % 9) + 1
            n_info["tara"] = tara_idx
            n_info["tara_number"] = tara_idx
            
            pos = n_info.get("sidereal_longitude") if ent_name == "Lagna" else n_info.get("sidereal_ra", 0.0)
            nak_fraction = (pos % (360.0 / 27.0)) / (360.0 / 27.0)
            nak_lord = VIMSHOTTARI_SEQUENCE[t_nak_idx % 9]
            sub_lord = calculate_sub_lord(nak_fraction, nak_lord)
            
            n_info["nakshatra_lord"] = nak_lord
            n_info["sub_lord"] = sub_lord
            n_info["lord_sublord"] = f"{PLANET_ABBREVIATIONS.get(nak_lord, nak_lord[:2])}/{PLANET_ABBREVIATIONS.get(sub_lord, sub_lord[:2])}"
            n_info["relative_speed"] = d1_rel_speeds.get(ent_name, "--")

        for p_name in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
            if p_name in vargas_data["D1"]["grahas"] and p_name in nakshatras_sidereal:
                vargas_data["D1"]["grahas"][p_name]["nakshatra"] = nakshatras_sidereal[p_name]["nakshatra"]
                vargas_data["D1"]["grahas"][p_name]["pada"] = nakshatras_sidereal[p_name]["pada"]
                vargas_data["D1"]["grahas"][p_name]["tara"] = nakshatras_sidereal[p_name]["tara"]
                vargas_data["D1"]["grahas"][p_name]["tara_number"] = nakshatras_sidereal[p_name]["tara"]
                vargas_data["D1"]["grahas"][p_name]["nakshatra_lord"] = nakshatras_sidereal[p_name]["nakshatra_lord"]
                vargas_data["D1"]["grahas"][p_name]["sub_lord"] = nakshatras_sidereal[p_name]["sub_lord"]
                vargas_data["D1"]["grahas"][p_name]["lord_sublord"] = nakshatras_sidereal[p_name]["lord_sublord"]
                vargas_data["D1"]["grahas"][p_name]["speed"] = d1_speeds.get(p_name, 0.0)
                vargas_data["D1"]["grahas"][p_name]["relative_speed"] = d1_rel_speeds.get(p_name, "--")
                vargas_data["D1"]["grahas"][p_name]["relative_speed_pct"] = d1_rel_speeds_pct.get(p_name)
                
        vargas_data["D1"]["grahas"]["Rahu"]["is_retrograde"] = True
        vargas_data["D1"]["grahas"]["Ketu"]["is_retrograde"] = True

        vargas_data["D1"]["lagna"]["nakshatra"] = nakshatras_sidereal["Lagna"]["nakshatra"]
        vargas_data["D1"]["lagna"]["pada"] = nakshatras_sidereal["Lagna"]["pada"]
        vargas_data["D1"]["lagna"]["tara"] = nakshatras_sidereal["Lagna"]["tara"]
        vargas_data["D1"]["lagna"]["tara_number"] = nakshatras_sidereal["Lagna"]["tara"]
        vargas_data["D1"]["lagna"]["nakshatra_lord"] = nakshatras_sidereal["Lagna"]["nakshatra_lord"]
        vargas_data["D1"]["lagna"]["sub_lord"] = nakshatras_sidereal["Lagna"]["sub_lord"]
        vargas_data["D1"]["lagna"]["lord_sublord"] = nakshatras_sidereal["Lagna"]["lord_sublord"]
        vargas_data["D1"]["lagna"]["relative_speed"] = "--"
            
        # Shayanadi Avasthas
        sunrise_jd = anchors["sunrise_jd"]
        minutes_elapsed = max(0.0, (jd - sunrise_jd) * 24.0 * 60.0)
        ishta_ghati = math.ceil(minutes_elapsed / 24.0)
        if ishta_ghati <= 0:
            ishta_ghati = 1
        
        varnamashka = self.name_sound_value if self.name_sound_value else avasthas.get_varnamashka(self.name)
        moon_nakshatra_no = NAKSHATRAS.index(nakshatras_sidereal["Moon"]["nakshatra"]) + 1
        all_planets_shayana = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]

        for v_name, v_data in vargas_data.items():
            v_lagna_sign_no = ZODIAC_SIGNS.index(v_data["lagna"]["sign"]) + 1
            harmonic = VARGAS_HARMONICS.get(v_name, 1)

            for p_name in all_planets_shayana:
                if p_name in v_data["grahas"] and p_name in nakshatras_sidereal:
                    v_data["grahas"][p_name]["nakshatra"] = nakshatras_sidereal[p_name]["nakshatra"]
                    p_nak_no = NAKSHATRAS.index(nakshatras_sidereal[p_name]["nakshatra"]) + 1
                    if v_name == "D1":
                        p_amsa = nakshatras_sidereal[p_name]["pada"]
                    else:
                        lon = d1_longitudes[p_name]
                        deg_in_sign = lon % 30.0
                        p_amsa = avasthas.get_varga_amsa_factor(deg_in_sign, harmonic)

                    shayanadi = avasthas.get_shayanadi_avastha(
                        p_name, p_nak_no, p_amsa, v_lagna_sign_no,
                        moon_nakshatra_no, ishta_ghati, name_sound_value=varnamashka
                    )
                    v_data["grahas"][p_name]["avasthas"]["shayanadi"] = shayanadi

            for p_name in ["Uranus", "Neptune", "Pluto"]:
                if p_name in v_data.get("grahas", {}) and p_name in nakshatras_sidereal:
                    v_data["grahas"][p_name]["nakshatra"] = nakshatras_sidereal[p_name]["nakshatra"]
            if "Lagna" in nakshatras_sidereal and "lagna" in v_data:
                v_data["lagna"]["nakshatra"] = nakshatras_sidereal["Lagna"]["nakshatra"]

        # Stamp Karakas onto Vargas
        chara_k = karakas.calculate_chara_karakas(vargas_data["D1"]["grahas"])
        fn_roles_d1 = karakas.calculate_functional_roles(vargas_data["D1"]["lagna"]["sign"])
        v_fn_roles = karakas.get_all_varga_functional_roles(vargas_data)

        for v_name, v_data in vargas_data.items():
            v_roles = v_fn_roles.get(v_name, {})
            for p_name, p_data in v_data["grahas"].items():
                p_data["chara_karaka"] = chara_k.get(p_name, {})
                p_data["functional_role"] = v_roles.get(p_name, {})
                p_data["d1_functional_role"] = fn_roles_d1.get(p_name, {})

        return vargas_data

    # =========================================================================
    # STAGE 4: Downstream Synthesis (Dashas, Vimshopaka, Karakas, Yogas, Reports)
    # =========================================================================
    @cached_property
    def chara_karakas(self) -> Dict[str, Any]:
        return karakas.calculate_chara_karakas(self.vargas["D1"]["grahas"])

    @cached_property
    def functional_roles_d1(self) -> Dict[str, Any]:
        return karakas.calculate_functional_roles(self.vargas["D1"]["lagna"]["sign"])

    @cached_property
    def varga_functional_roles(self) -> Dict[str, Any]:
        return karakas.get_all_varga_functional_roles(self.vargas)

    @cached_property
    def dasha_timeline(self) -> Dict[str, Any]:
        anchors = self.baseline.astronomical_anchors
        jd = anchors["jd_utc"]
        jd_local = anchors["jd_local"]
        cal_flag = anchors["cal_flag"]
        moon_nak = self.baseline.nakshatras["grahas"]["Moon"]

        if self.nakshatra_system == "VIC_CHITRA":
            moon_sid_lon = moon_nak["sidereal_longitude"]
            return calculate_vimshottari_timeline(
                moon_sidereal_ra=moon_sid_lon,
                birth_jd_local=jd_local,
                cal_flag=cal_flag,
                total_cycles=1,
                dasha_year_days=SAURA_YEAR_DAYS,
                nakshatra_system=self.nakshatra_system,
                birth_jd_utc=jd,
                moon_sidereal_lon=moon_sid_lon
            )
        else:
            moon_sid_ra = moon_nak["sidereal_ra"]
            return calculate_vimshottari_timeline(
                moon_sidereal_ra=moon_sid_ra,
                birth_jd_local=jd_local,
                cal_flag=cal_flag,
                total_cycles=1,
                dasha_year_days=SAURA_YEAR_DAYS,
                nakshatra_system=self.nakshatra_system,
                birth_jd_utc=jd
            )

    @cached_property
    def vimshopaka_data(self) -> Dict[str, Any]:
        return vimshopaka.calculate_varga_vimshopaka_engine({"vargas": self.vargas})

    @cached_property
    def vimshopaka_export(self) -> Dict[str, Any]:
        v_data = self.vimshopaka_data
        return {
            **v_data,
            "shadvarga": v_data["scores"].get("Shadvarga", {}),
            "saptavarga": v_data["scores"].get("Saptavarga", {}),
            "dasavarga": v_data["scores"].get("Dasavarga", {}),
            "shodashavarga": v_data["scores"].get("Shodasavarga", {}),
            "vaisheshikamsa": {
                p: v_data["vaisheshikamsa"].get("Shodasavarga", {}).get(p, {}).get("honorific", "-")
                for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
            }
        }

    @cached_property
    def avastha_matrices(self) -> Dict[str, Any]:
        from jyotish.avasthas.quantitative import calculate_avastha_matrix
        vargas_data = self.vargas
        shadbala_data = self.shadbala
        vim_data = self.vimshopaka_data
        planets_list = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
        baseline_types = ["ShadBala", "Vimshopaka", "Subha", "Ishta", "Cheshta", "Uccha", "Dig", "Drishti Yuti", "Veda"]
        is_jolie = (self.name == "Angelina Jolie")

        matrices = {}
        for v_key in vargas_data.keys():
            matrices[v_key] = {}
            for b_type in baseline_types:
                res = calculate_avastha_matrix(
                    vargas_data[v_key]["grahas"],
                    shadbala_data,
                    vargas_data["D1"]["grahas"],
                    baseline_type=b_type,
                    varga_name=v_key,
                    vimshopaka_data=vim_data,
                    use_transcribed_benchmark=is_jolie
                )
                v_matrix = {}
                for p_give in planets_list:
                    v_matrix[p_give] = {}
                    for p_receive in planets_list:
                        v_matrix[p_give][p_receive] = res['matrix'][p_give][p_receive]
                matrices[v_key][b_type] = v_matrix
        return matrices

    @cached_property
    def varga_aspects(self) -> Dict[str, Any]:
        vargas_data = self.vargas
        return {v_key: aspects.calculate_varga_aspects(vargas_data[v_key]) for v_key in vargas_data}

    @cached_property
    def ashtakavarga_data(self) -> Dict[str, Any]:
        data = ashtakavarga.calculate_ashtakavarga_engine({"vargas": self.vargas})
        pindas = data.get('sodhya_pindas', {})
        r_tot = sum(pindas[p]['rasi_pinda'] for p in pindas if isinstance(pindas[p], dict) and 'rasi_pinda' in pindas[p])
        g_tot = sum(pindas[p]['graha_pinda'] for p in pindas if isinstance(pindas[p], dict) and 'graha_pinda' in pindas[p])
        data['sav'] = data['sarvashtakavarga']['total_sav']
        data['shodhya_pindas'] = {
            **pindas,
            'rasi_pinda_total': r_tot,
            'graha_pinda_total': g_tot,
            'yoga_pinda_total': r_tot + g_tot,
        }
        return data


    @cached_property
    def yogas(self) -> Dict[str, Any]:
        from jyotish.yogas import detect_all_yogas
        return detect_all_yogas({
            "vargas": self.vargas,
            "shadbala": self.shadbala,
            "advanced_aspects": self.varga_aspects.get("D1", {}),
            "nakshatras": {"grahas": self.baseline.nakshatras["grahas"]},
        })

    @cached_property
    def planetary_evaluation(self) -> Dict[str, Any]:
        return planetary_evaluation.calculate_planetary_evaluation(
            self.vargas,
            self.shadbala,
            self.varga_aspects.get("D1"),
            baseline=self.baseline
        )

    # =========================================================================
    # SERIALIZATION TO FULL VEDIC CONTEXT DICTIONARY
    # =========================================================================
    def to_dict(self) -> Dict[str, Any]:
        """
        Serializes the complete chart state into the identical schema expected
        by the Flask API, UI widgets, and test fixtures.
        """
        anchors = self.baseline.astronomical_anchors
        jd = anchors["jd_utc"]
        ayanamsa_eq = self.baseline.nakshatras["equatorial_ayanamsa"]
        ayanamsa_ecl = self.baseline.nakshatras["ecliptic_ayanamsa"]
        ra_gc = 266.0371
        lon_gc = 266.5179

        sec_int = int(round(self.second))
        if self.year < 0:
            birth_dt_str = f"{self.day:02d}/{self.month:02d}/{self.year} {self.hour:02d}:{self.minute:02d}:{sec_int:02d}"
        else:
            birth_dt_str = f"{self.day:02d}/{self.month:02d}/{self.year:04d} {self.hour:02d}:{self.minute:02d}:{sec_int:02d}"

        vargas_data = self.vargas
        varga_aspects = self.varga_aspects
        dasha_timeline = self.dasha_timeline

        vedic_context = {
            "subject_info": {
                "name": self.name,
                "birth_datetime": birth_dt_str,
                "latitude": self.latitude,
                "longitude": self.longitude,
                "timezone_offset": self.timezone_offset,
                "place": self.place
            },
            "calculation_settings": {
                "d10_mode": self.d10_mode,
                "d24_mode": self.d24_mode,
                "debilitation_mode": self.debilitation_mode,
                "nakshatra_system": self.nakshatra_system,
                "ayanamsa_name": "Lahiri / Chitra Paksha" if self.nakshatra_system == "VIC_CHITRA" else "Dhruva Galactic Center (Middle of Mula)"
            },
            "astronomy": {
                "nakshatra_system": self.nakshatra_system,
                "ayanamsa_name": "Lahiri / Chitra Paksha" if self.nakshatra_system == "VIC_CHITRA" else "Dhruva Galactic Center (Middle of Mula)",
                "equatorial_ayanamsa_value": round(ayanamsa_eq, 4),
                "ecliptic_ayanamsa_value": round(ayanamsa_ecl, 4),
                "galactic_center_ra": round(ra_gc, 4),
                "galactic_center_lon": round(lon_gc, 4),
                "house_system": "Campanus (with Whole Sign overlay)",
                "dasha_year_length_days": SAURA_YEAR_DAYS,
                "julian_day": jd
            },
            "nakshatras": {
                "zodiac": "Sidereal Ecliptic (Lahiri / Chitra)" if self.nakshatra_system == "VIC_CHITRA" else "Sidereal Equatorial",
                "system": self.nakshatra_system,
                "grahas": self.baseline.nakshatras["grahas"]
            },
            "vargas": vargas_data,
            "vimshottari_dasha": {
                "at_birth": dasha_timeline["at_birth"],
                "mahadashas": dasha_timeline["mahadashas"],
                "antardashas": dasha_timeline["antardashas"],
            },
            "shadbala": self.shadbala,
            "bhava_bala": self.bhava_bala,
            "harsha_bala": self.harsha_bala,
            "house_atmosphere": self.house_atmosphere,
            "dignities": self.dignities,
            "aspect_matrices": self.aspect_matrices,
            "avastha_matrix": self.avastha_matrices,
            "varga_lajjitadi_net_modifiers": avasthas.calculate_varga_lajjitadi_net_modifiers(vargas_data),
            "advanced_aspects": varga_aspects["D1"],
            "varga_advanced_aspects": varga_aspects,
            "ashtakavarga": self.ashtakavarga_data,
            "varga_vimshopaka": self.vimshopaka_data,
            "vimshopaka": self.vimshopaka_export,
            "sign_attributes": {v_k: sign_attributes.calculate_sign_distributions(v_data) for v_k, v_data in vargas_data.items()},
            "planetary_evaluation": self.planetary_evaluation,
            "master_diagnostic": self.master_diagnostic,
            "karakas": {
                "chara": self.chara_karakas,
                "functional": self.functional_roles_d1,
                "varga_functional": self.varga_functional_roles,
                "naisargika": karakas.NAISARGIKA_KARAKAS
            },
            "yogas": self.yogas
        }

        # Stage 4 Synthesis Report
        vedic_context["report"] = report_engine.generate_report_payload(vedic_context)
        return vedic_context
