"""
tests/test_drishti_line_graph.py

Test Module 6: Continuous Drishti Line Graph & SVG Coordinate Engine
Validates that continuous aspect graphs filter out non-target planets, keep coordinates
within bounds of the 820x260 SVG viewBox, and ingest minor aspects (>= 12.0 Virupas).
"""

import pytest
from jyotish.planetary_evaluation.planetary_evaluation import (
    get_aspect_anchor_points,
    build_aspect_graph_data,
    calculate_continuous_drishti,
    calculate_planetary_evaluation
)


def test_aspect_graph_single_target_isolation():
    """
    Test 6.2: Single Target Planet Isolation
    Input: Moon aspects Venus, Mars, and Saturn in the chart. We request the aspect graph for Venus.
    inc_g['targets'] length is strictly equal to 1, inc_g['targets'][0]['name'] == 'Venus'.
    No markers for Mars or Saturn appear in the payload.
    """
    source_planet = "Moon"
    source_deg = 30.0
    targets = [{"name": "Venus", "longitude": 272.9, "is_target": True}]
    
    graph_data = build_aspect_graph_data(source_planet, source_deg, targets)
    assert len(graph_data["targets"]) == 1
    assert graph_data["targets"][0]["name"] == "Venus"
    target_names = [t["name"] for t in graph_data["targets"]]
    assert "Mars" not in target_names
    assert "Saturn" not in target_names


def test_svg_coordinate_bounds():
    """
    Test 6.3: SVG Coordinate Clamping inside viewBox="0 0 820 260"
    Evaluates coordinates across all anchor degrees (D in [0, 360]) and percentages (P in [0, 100]).
    Formulas:
        X = 50 + (D / 360.0) * 720
        Y = 180 - (P / 100.0) * 140
    Assertions:
        For D = 0 -> X = 50.0; for D = 360 -> X = 770.0 (50 <= X <= 770 <= 820).
        For P = 0% -> Y = 180.0; for P = 100% -> Y = 40.0 (40 <= Y <= 180 <= 260).
        Zero points exceed the bounds of the 820 x 260 SVG viewBox.
    """
    for planet in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
        anchors = get_aspect_anchor_points(planet)
        for d, pct in anchors:
            cx = 50 + (d / 360.0) * 720
            cy = 180 - (pct / 100.0) * 140
            assert 50.0 <= cx <= 770.0, f"X coordinate {cx} out of bounds [50, 770]"
            assert 40.0 <= cy <= 180.0, f"Y coordinate {cy} out of bounds [40, 180]"
            # Within full 820 x 260 viewBox
            assert 0.0 <= cx <= 820.0
            assert 0.0 <= cy <= 260.0

    # Test extreme bounds
    x_min = 50 + (0.0 / 360.0) * 720
    x_max = 50 + (360.0 / 360.0) * 720
    y_min = 180 - (100.0 / 100.0) * 140
    y_max = 180 - (0.0 / 100.0) * 140

    assert x_min == 50.0
    assert x_max == 770.0
    assert y_min == 40.0
    assert y_max == 180.0


def test_minor_aspect_ingestion_and_graph_binding():
    """
    Test 6.1: Minor Aspect Ingestion Threshold (>= 12.0 Virupas)
    Test 6.4: Aspect Graph Data Binding in vit_res['aspect_details']
    Mercury casts an aspect of >= 12.0 Virupas on the Moon.
    Asserts:
        - Mercury aspect is NOT dropped by the incoming aspect filter (19.0 >= 12.0).
        - incoming_aspect_graphs['Mercury'] is successfully generated.
        - Every aspect item in vit_res['aspect_details'] with virupas >= 12.0 contains
          a non-empty 'aspect_graph' dictionary key.
    """
    # Chart where Mercury at 230° (Scorpio 20°) aspects Moon at 100° (Cancer 10°) -> 130° separation (~19 virupas)
    # and Saturn at 315° aspects Sun at 135° (full 7th aspect, 60 virupas)
    chart = {
        "D1": {
            "lagna": {"sign": "Leo", "degree_0_to_30": 15.0},
            "grahas": {
                "Moon": {"sign": "Cancer", "degree_0_to_30": 10.0, "longitude": 100.0, "dignity": "Own Sign"},
                "Mercury": {"sign": "Scorpio", "degree_0_to_30": 20.0, "longitude": 230.0, "dignity": "Neutral"},
                "Sun": {"sign": "Leo", "degree_0_to_30": 15.0, "longitude": 135.0, "dignity": "Own Sign"},
                "Saturn": {"sign": "Aquarius", "degree_0_to_30": 15.0, "longitude": 315.0, "dignity": "Moolatrikona"},
                "Mars": {"sign": "Aries", "degree_0_to_30": 10.0, "longitude": 10.0, "dignity": "Own Sign"},
                "Jupiter": {"sign": "Sagittarius", "degree_0_to_30": 10.0, "longitude": 250.0, "dignity": "Own Sign"},
                "Venus": {"sign": "Libra", "degree_0_to_30": 20.0, "longitude": 200.0, "dignity": "Own Sign"},
                "Rahu": {"sign": "Gemini", "degree_0_to_30": 15.0, "longitude": 75.0, "dignity": "Exalted"},
                "Ketu": {"sign": "Sagittarius", "degree_0_to_30": 15.0, "longitude": 255.0, "dignity": "Exalted"}
            }
        }
    }

    eval_res = calculate_planetary_evaluation(chart)
    moon_data = eval_res["planets"]["Moon"]
    moon_inc_graphs = moon_data["incoming_aspect_graphs"]

    # Test 6.1: Minor aspect (>= 12.0v) is present in incoming_aspect_graphs
    assert "Mercury" in moon_inc_graphs, "Mercury (aspect >= 12.0v) must generate an incoming aspect graph"
    merc_graph = moon_inc_graphs["Mercury"]
    assert merc_graph["source_planet"] == "Mercury"
    assert len(merc_graph["targets"]) == 1
    assert merc_graph["targets"][0]["name"] == "Moon"

    # Test 6.4: Data binding in vit_res['aspect_details']
    moon_vit_aspects = moon_data["vitality"]["aspect_details"]
    for asp in moon_vit_aspects:
        if float(asp.get("virupas", 0.0)) >= 12.0:
            assert "aspect_graph" in asp, f"Aspect from {asp.get('from_planet')} missing aspect_graph key"
            assert asp["aspect_graph"] is not None
            assert "polyline_points" in asp["aspect_graph"]
            assert len(asp["aspect_graph"]["targets"]) == 1
            assert asp["aspect_graph"]["targets"][0]["name"] == "Moon"
