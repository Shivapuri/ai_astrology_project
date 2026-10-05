"""
jyotish/generate_jyotish.py
Ernst Wilhelm Kala Integrated Astrology Master Orchestrator

Thin orchestrator interface that delegates calculation stages to ChartPipeline
(Single Source of Truth DAG pattern).
Maintains 100% backward compatibility for all existing callers, tests, and API routes.
"""

import json
from typing import Dict, Any, Optional

from jyotish.baseline import (
    calculate_varga_longitude,
    ZODIAC_SIGNS,
    NAKSHATRAS,
    NITYA_YOGAS,
    calculate_sub_lord,
    VIMSHOTTARI_SEQUENCE,
    VIMSHOTTARI_YEARS,
    ChartBaseline
)
from jyotish.pipeline import (
    ChartPipeline,
    get_sign,
    DASHA_LORDS,
    DASHA_YEARS,
    MEAN_DAILY_SPEEDS,
    KALA_MEAN_DAILY_SPEEDS,
    PLANET_ABBREVIATIONS,
    VARGAS_HARMONICS
)


def generate_kala_chart(
    name: str = "Subject",
    year: int = 1995,
    month: int = 5,
    day: int = 15,
    hour: int = 14,
    minute: int = 30,
    latitude: float = 51.5074,
    longitude: float = -0.1278,
    timezone_offset: float = 1.0,
    name_sound_value: Optional[int] = None,
    output_filepath: Optional[str] = None,
    d10_mode: str = "reverse",
    d24_mode: str = "reverse",
    place: str = "",
    second: int = 0,
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
    **kwargs
) -> Dict[str, Any]:
    """
    Master Orchestration Interface for Ernst Wilhelm's Kala Vedic Astrology Engine.
    Delegates calculation and stage-caching directly to ChartPipeline.
    """
    pipeline = ChartPipeline(
        name=name,
        year=year,
        month=month,
        day=day,
        hour=hour,
        minute=minute,
        second=second,
        latitude=latitude,
        longitude=longitude,
        timezone_offset=timezone_offset,
        place=place,
        name_sound_value=name_sound_value,
        d10_mode=d10_mode,
        d24_mode=d24_mode,
        nakshatra_system=nakshatra_system,
        debilitation_mode=debilitation_mode,
        dig_bala_mode=dig_bala_mode,
        kendra_bala_mode=kendra_bala_mode,
        phala_mode=phala_mode,
        pillar_mode=pillar_mode,
        trimsamsa_mode=trimsamsa_mode,
        saptavarga_mode=saptavarga_mode,
        drik_mode=drik_mode,
        ayana_tradition=ayana_tradition,
        **kwargs
    )
    result = pipeline.to_dict()

    if output_filepath:
        with open(output_filepath, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"Successfully generated Ernst Wilhelm Kala astrology context: {output_filepath}")

    return result


if __name__ == "__main__":
    generate_kala_chart(
        name="Arjuna",
        year=1995,
        month=5,
        day=15,
        hour=14,
        minute=30,
        latitude=28.6139,
        longitude=77.2090,
        timezone_offset=5.5,
        output_filepath="vedic_context.json"
    )
