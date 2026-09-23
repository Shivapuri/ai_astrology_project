"""
Unit tests for Continuous Vedic Aspect (Drishti) Line Graph Component (Brihat Jataka 2.13).
Verifies:
1. Standard Planet Aspect Curve (Sun, Moon, Mercury, Venus) anchor points and linear interpolation.
2. Special Aspects (Visesha Drishti) Curves for Mars, Jupiter, Saturn (and Rahu/Ketu).
3. Intermediate In-Between Planet Placement (e.g. Sun at 0°, Moon at 165° -> x=332.5, y=70.0, pct=50.0).
4. build_aspect_graph_data SVG polyline and target marker geometry.
"""

import pytest
from jyotish.planetary_evaluation import (
    ANCHOR_DEGREES,
    get_aspect_anchor_points,
    calculate_continuous_drishti,
    build_aspect_graph_data
)


def test_standard_planet_anchor_points():
    """Verify Sun/Moon/Mercury/Venus anchor points match Brihat Jataka 2.13."""
    for p in ["Sun", "Moon", "Mercury", "Venus"]:
        anchors = dict(get_aspect_anchor_points(p))
        
        # Zero aspect points
        for d in [0, 30, 150, 300, 330, 360]:
            assert anchors[d] == 0.0, f"{p} at {d}° should be 0%, got {anchors[d]}"
            
        # Peak aspect at 180° (7th house)
        assert anchors[180] == 100.0, f"{p} at 180° should be 100%, got {anchors[180]}"
        
        # Intermediate anchors
        assert anchors[60] == 25.0, f"{p} at 60° should be 25%"
        assert anchors[90] == 75.0, f"{p} at 90° should be 75%"
        assert anchors[120] == 50.0, f"{p} at 120° should be 50%"
        assert anchors[210] == 75.0, f"{p} at 210° should be 75%"
        assert anchors[240] == 50.0, f"{p} at 240° should be 50%"
        assert anchors[270] == 25.0, f"{p} at 270° should be 25%"


def test_special_aspect_mars():
    """Mars (Mangala) must peak at 100% on 4th (90°), 7th (180°), and 8th (210°)."""
    anchors = dict(get_aspect_anchor_points("Mars"))
    assert anchors[90] == 100.0, "Mars 4th aspect (90°) must be 100%"
    assert anchors[180] == 100.0, "Mars 7th aspect (180°) must be 100%"
    assert anchors[210] == 100.0, "Mars 8th aspect (210°) must be 100%"
    assert anchors[60] == 25.0
    assert anchors[120] == 50.0
    assert anchors[240] == 50.0
    assert anchors[270] == 25.0


def test_special_aspect_jupiter():
    """Jupiter (Guru) must peak at 100% on 5th (120°), 7th (180°), and 9th (240°)."""
    anchors = dict(get_aspect_anchor_points("Jupiter"))
    assert anchors[120] == 100.0, "Jupiter 5th aspect (120°) must be 100%"
    assert anchors[180] == 100.0, "Jupiter 7th aspect (180°) must be 100%"
    assert anchors[240] == 100.0, "Jupiter 9th aspect (240°) must be 100%"
    assert anchors[90] == 75.0
    assert anchors[210] == 75.0
    assert anchors[60] == 25.0
    assert anchors[270] == 25.0


def test_special_aspect_saturn():
    """Saturn (Shani) must peak at 100% on 3rd (60°), 7th (180°), and 10th (270°)."""
    anchors = dict(get_aspect_anchor_points("Saturn"))
    assert anchors[60] == 100.0, "Saturn 3rd aspect (60°) must be 100%"
    assert anchors[180] == 100.0, "Saturn 7th aspect (180°) must be 100%"
    assert anchors[270] == 100.0, "Saturn 10th aspect (270°) must be 100%"
    assert anchors[90] == 75.0
    assert anchors[120] == 50.0
    assert anchors[210] == 75.0
    assert anchors[240] == 50.0


def test_continuous_interpolation_in_between_placement():
    """
    Acceptance Criteria 3:
    If Sun is at 0° and Moon is placed at 165°, Moon is halfway between 150° (0%) and 180° (100%),
    yielding 50% aspect strength, cx = 380.0, cy = 110.0 in 820x260 canvas.
    """
    pct = calculate_continuous_drishti("Sun", 165.0)
    assert pct == 50.0, f"Expected 50.0% at 165° for Sun, got {pct}"

    graph = build_aspect_graph_data(
        source_planet="Sun",
        source_deg=0.0,
        aspected_planets=[{"name": "Moon", "longitude": 165.0, "symbol": "Mo"}]
    )

    assert graph["source_planet"] == "Sun"
    assert len(graph["targets"]) == 1
    tgt = graph["targets"][0]

    assert tgt["name"] == "Moon"
    assert tgt["symbol"] == "Mo"
    assert tgt["rel_deg"] == 165.0
    assert tgt["pct"] == 50.0
    assert tgt["cx"] == 380.0
    assert tgt["cy"] == 110.0


def test_build_aspect_graph_data_polyline():
    """Verify SVG polyline coordinates are strictly bounded between Y:180 (0%) and Y:40 (100%)."""
    graph = build_aspect_graph_data("Mars", 100.0, [])
    points_str = graph["polyline_points"]
    pairs = [p.split(",") for p in points_str.split(" ")]

    assert len(pairs) == 13, "Should have 13 anchor points from 0° to 360°"
    
    # Check start and end
    assert pairs[0] == ["50.0", "180.0"]
    assert pairs[-1] == ["770.0", "180.0"]

    # Check Mars 4th aspect (90° from seat): d=90 -> x = 50 + (90/360)*720 = 230.0, y=40.0
    # In pairs list, d=90 is index 3 (0, 30, 60, 90)
    assert pairs[3] == ["230.0", "40.0"]
    
    # Mars 7th aspect (180° from seat): index 6
    assert pairs[6] == ["410.0", "40.0"]
    
    # Mars 8th aspect (210° from seat): index 7 -> x = 50 + (210/360)*720 = 470.0, y=40.0
    assert pairs[7] == ["470.0", "40.0"]

    # Check anchor nodes export
    assert "anchors" in graph
    assert len(graph["anchors"]) == 7  # 60, 90, 120, 180, 210, 240, 270
    anchor_degs = [a["deg"] for a in graph["anchors"]]
    assert anchor_degs == [60, 90, 120, 180, 210, 240, 270]


def test_chart_aspect_graphs_integration():
    """Verify that generate_kala_chart populates aspect_graph and incoming_aspect_graphs isolating target planet."""
    from jyotish.generate_jyotish import generate_kala_chart
    chart = generate_kala_chart(
        name="Angelina Jolie",
        year=1975, month=6, day=4,
        hour=9, minute=9,
        latitude=34.0522, longitude=-118.2437, timezone_offset=-7.0
    )
    p_eval = chart.get("planetary_evaluation", {}).get("planets", {})
    assert len(p_eval) > 0

    for p, data in p_eval.items():
        assert "aspect_graph" in data, f"Planet {p} should have aspect_graph"
        assert "incoming_aspect_graphs" in data, f"Planet {p} should have incoming_aspect_graphs"
        g = data["aspect_graph"]
        assert g["source_planet"] == p
        assert len(g["polyline_points"]) > 0
        assert "anchors" in g

        # Verify incoming aspect graphs isolate ONLY the target planet (p)
        inc_graphs = data["incoming_aspect_graphs"]
        for src_planet, inc_g in inc_graphs.items():
            assert "targets" in inc_g
            assert len(inc_g["targets"]) == 1, f"Incoming aspect to {p} from {src_planet} should only target {p}"
            assert inc_g["targets"][0]["name"] == p
            assert inc_g["targets"][0]["is_target"] is True

