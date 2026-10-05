"""
tests/test_pipeline.py
Unit and Integration Tests for ChartPipeline (Single Source of Truth DAG Engine).
"""

import pytest
from jyotish.pipeline import ChartPipeline
from jyotish.baseline import ChartBaseline
from jyotish.yogas import detect_all_yogas
from jyotish.generate_jyotish import generate_kala_chart


@pytest.fixture(scope="module")
def default_pipeline():
    return ChartPipeline(
        name="Arjuna",
        year=1995,
        month=5,
        day=15,
        hour=14,
        minute=30,
        latitude=28.6139,
        longitude=77.2090,
        timezone_offset=5.5
    )


def test_pipeline_instantiation_and_lazy_baseline(default_pipeline):
    """Verifies that baseline is lazy and accessible as a typed ChartBaseline."""
    assert isinstance(default_pipeline.baseline, ChartBaseline)
    assert default_pipeline.baseline.name == "Arjuna"
    assert "Sun" in default_pipeline.baseline.coordinates


def test_pipeline_stage2_stage3_properties(default_pipeline):
    """Verifies typed accessors for Stage 2A, 2B, and 3 engines."""
    # Stage 2A
    assert "varga_dignities" in default_pipeline.dignities
    assert "D1" in default_pipeline.dignities["varga_dignities"]
    assert "graha_drishti" in default_pipeline.aspect_matrices

    # Stage 2B
    assert "Sun" in default_pipeline.shadbala
    assert default_pipeline.shadbala["Sun"]["Total_Virupas"] > 0

    # Stage 3
    assert 1 in default_pipeline.bhava_bala
    assert 6 in default_pipeline.harsha_bala["dusthana_joy"]
    assert 1 in default_pipeline.house_atmosphere
    assert len(default_pipeline.master_diagnostic["columns"]) == 9
    assert len(default_pipeline.master_diagnostic["rows"]) == 9


def test_pipeline_stage4_yogas_accepts_pipeline_directly(default_pipeline):
    """Verifies that detect_all_yogas natively consumes a ChartPipeline instance."""
    yogas = detect_all_yogas(default_pipeline)
    assert isinstance(yogas, dict)
    assert "total_count" in yogas
    assert "yogas" in yogas


def test_pipeline_external_baseline_injection():
    """Verifies that an existing ChartBaseline can be injected directly into ChartPipeline."""
    base = ChartBaseline(
        name="Karna",
        year=1990,
        month=1,
        day=1,
        hour=12,
        minute=0,
        latitude=20.0,
        longitude=80.0,
        timezone_offset=5.5
    )
    p = ChartPipeline(baseline=base)
    assert p.baseline is base
    assert p.baseline.name == "Karna"
    assert p.shadbala["Sun"]["Total_Virupas"] > 0


def test_pipeline_exact_parity_with_generate_kala_chart():
    """Verifies that ChartPipeline.to_dict() matches generate_kala_chart() output."""
    c_func = generate_kala_chart(
        name="Angelina Jolie",
        year=1975,
        month=6,
        day=4,
        hour=9,
        minute=9,
        latitude=34.0522,
        longitude=-118.2437,
        timezone_offset=-7.0
    )
    p = ChartPipeline(
        name="Angelina Jolie",
        year=1975,
        month=6,
        day=4,
        hour=9,
        minute=9,
        latitude=34.0522,
        longitude=-118.2437,
        timezone_offset=-7.0
    )
    c_pipe = p.to_dict()

    assert set(c_func.keys()) == set(c_pipe.keys())
    for k in ["subject_info", "calculation_settings", "astronomy", "nakshatras", "shadbala", "bhava_bala"]:
        assert c_func[k] == c_pipe[k]
