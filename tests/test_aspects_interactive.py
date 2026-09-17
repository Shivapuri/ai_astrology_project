import pytest
import re
from jyotish.aspects.aspects import get_aspect_explanation, get_graha_drishti
from jyotish.draw_chart import generate_south_indian, generate_north_indian, generate_circular_chart

def test_get_aspect_explanation_benefic_and_malefic():
    # Jupiter (benefic) casting 5th house aspect (120 deg separation)
    exp_jup = get_aspect_explanation("Jupiter", 0.0, 120.0, aspecting_dignity="Own Sign")
    assert exp_jup["is_benefic"] is True
    assert exp_jup["line_style"] == "continuous"
    assert exp_jup["houses_away"] == 5
    assert "Jupiter Special" in exp_jup["rule_name"]
    assert exp_jup["virupas"] == 60.0
    assert exp_jup["separation_deg"] == 120.0

    # Mars (malefic) casting 4th house aspect (90 deg separation)
    exp_mars = get_aspect_explanation("Mars", 0.0, 90.0, aspecting_dignity="Exalted")
    assert exp_mars["is_benefic"] is False
    assert exp_mars["line_style"] == "dashed"
    assert exp_mars["houses_away"] == 4
    assert "Mars Special" in exp_mars["rule_name"]
    assert exp_mars["virupas"] == 60.0

    # Saturn (malefic) casting 10th house aspect (270 deg separation)
    exp_sat = get_aspect_explanation("Saturn", 0.0, 270.0, aspecting_dignity="Neutral")
    assert exp_sat["is_benefic"] is False
    assert exp_sat["line_style"] == "dashed"
    assert exp_sat["houses_away"] == 10
    assert "Saturn Special" in exp_sat["rule_name"]

    # Opposition (180 deg separation)
    exp_opp = get_aspect_explanation("Venus", 0.0, 180.0)
    assert exp_opp["is_benefic"] is True
    assert exp_opp["line_style"] == "continuous"
    assert exp_opp["houses_away"] == 7
    assert "7th House Full Opposition" in exp_opp["rule_name"]

def test_chart_svgs_contain_interactive_aspect_elements():
    # Sample items with planets positioned to produce aspects
    # Sun in Aries (0°), Saturn in Libra (180° opposition), Jupiter in Leo (120° trine)
    items = [
        {"name": "Lagna", "sign": "Aries", "degree": 10, "minute": 30, "type": "planet"},
        {"name": "Sun", "sign": "Aries", "degree": 15, "minute": 0, "type": "planet"},
        {"name": "Jupiter", "sign": "Leo", "degree": 15, "minute": 0, "type": "planet"},
        {"name": "Saturn", "sign": "Libra", "degree": 15, "minute": 0, "type": "planet"},
        {"name": "Mars", "sign": "Cancer", "degree": 15, "minute": 0, "type": "planet"},
        {"name": "Venus", "sign": "Taurus", "degree": 5, "minute": 0, "type": "planet"},
        {"name": "Mercury", "sign": "Gemini", "degree": 20, "minute": 0, "type": "planet"},
        {"name": "Moon", "sign": "Sagittarius", "degree": 15, "minute": 0, "type": "planet"},
        {"name": "Rahu", "sign": "Aquarius", "degree": 8, "minute": 0, "type": "planet"},
        {"name": "Ketu", "sign": "Leo", "degree": 8, "minute": 0, "type": "planet"},
    ]

    # South Indian Chart
    si_svg = generate_south_indian(items)
    assert 'class="aspects-hidden"' in si_svg
    assert 'class="interactive-aspect"' in si_svg
    assert 'class="interactive-aspect-badge"' in si_svg
    assert 'data-virupas=' in si_svg
    assert 'data-deg=' in si_svg
    assert 'data-benefic=' in si_svg
    assert 'marker-end=' in si_svg

    # North Indian Chart
    ni_svg = generate_north_indian(items)
    assert 'class="aspects-hidden"' in ni_svg
    assert 'class="interactive-aspect"' in ni_svg
    assert 'class="interactive-aspect-badge"' in ni_svg
    assert 'data-virupas=' in ni_svg
    assert 'data-deg=' in ni_svg

    # Circular Chart
    circ_svg = generate_circular_chart(items)
    assert 'class="aspects-hidden"' in circ_svg
    assert 'class="interactive-aspect"' in circ_svg
    assert 'class="interactive-aspect-badge"' in circ_svg
    assert 'data-virupas=' in circ_svg
    assert 'data-deg=' in circ_svg

def test_frontend_template_interactive_aspect_attributes():
    with open("templates/index.html", "r", encoding="utf-8") as f:
        html = f.read()

    # Verify interactive table rows
    assert 'interactive-table-row' in html
    assert 'selectAstrologicalEntity' in html
    assert 'clearAstrologicalEntitySelection' in html
    assert 'highlightPlanetAspects' in html
    assert 'highlightSignAspects' in html
    assert 'aspect-dynamic-badge' in html
    assert 'aspect-tag-outgoing' in html
    assert 'aspect-tag-incoming' in html
