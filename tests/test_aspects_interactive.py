import pytest
import re
from jyotish.aspects.aspects import get_aspect_explanation, get_graha_drishti
from jyotish.draw_chart import generate_south_indian, generate_north_indian, generate_circular_chart

def test_get_aspect_explanation_benefic_and_malefic():
    # Jupiter (benefic) casting 5th house aspect (120 deg separation)
    exp_jup = get_aspect_explanation("Jupiter", 0.0, 120.0, aspecting_dignity="Own Sign")
    assert exp_jup["is_benefic"] is True
    assert exp_jup["line_style"] == "continuous"
    assert "Jupiter Special 5th Glance / Trikona" in exp_jup["rule_name"]
    assert exp_jup["virupas"] == 60.0
    assert exp_jup["separation_deg"] == 120.0
    assert "houses_away" not in exp_jup

    # Mars (malefic) casting 4th house aspect (90 deg separation)
    exp_mars = get_aspect_explanation("Mars", 0.0, 90.0, aspecting_dignity="Exalted")
    assert exp_mars["is_benefic"] is False
    assert exp_mars["line_style"] == "dashed"
    assert "Mars Special 4th Glance / Caturasra" in exp_mars["rule_name"]
    assert exp_mars["virupas"] == 60.0

    # Mars (malefic) casting 8th house glance at 205 deg separation (Sphuṭa Dṛṣṭi milestone proximity, not 7th opposition)
    exp_mars_8th = get_aspect_explanation("Mars", 0.0, 205.0)
    assert "Mars Special 8th Glance / Randhra" in exp_mars_8th["rule_name"]
    assert exp_mars_8th["virupas"] == 60.0
    assert "7th" not in exp_mars_8th["rule_name"]

    # Saturn (malefic) casting 10th house aspect (270 deg separation)
    exp_sat = get_aspect_explanation("Saturn", 0.0, 270.0, aspecting_dignity="Neutral")
    assert exp_sat["is_benefic"] is False
    assert exp_sat["line_style"] == "dashed"
    assert "Saturn Special 10th Glance / Karma" in exp_sat["rule_name"]

    # Saturn casting 3rd house glance (60 deg separation)
    exp_sat_3rd = get_aspect_explanation("Saturn", 0.0, 60.0)
    assert "Saturn Special 3rd Glance / Upachaya" in exp_sat_3rd["rule_name"]

    # Jupiter casting 9th house glance (240 deg separation)
    exp_jup_9th = get_aspect_explanation("Jupiter", 0.0, 240.0)
    assert "Jupiter Special 9th Glance / Dharma" in exp_jup_9th["rule_name"]

    # Opposition (180 deg separation)
    exp_opp = get_aspect_explanation("Venus", 0.0, 180.0)
    assert exp_opp["is_benefic"] is True
    assert exp_opp["line_style"] == "continuous"
    assert "7th Full Opposition Glance" in exp_opp["rule_name"]

    # General Parashari Graduated Glance
    exp_gen = get_aspect_explanation("Sun", 0.0, 45.0)
    assert "General Parāśarī Graduated Glance" in exp_gen["rule_name"]

    # Bright Moon vs Dark Moon
    assert get_aspect_explanation("Moon", 0.0, 180.0, is_moon_bright=True)["is_benefic"] is True
    assert get_aspect_explanation("Moon", 0.0, 180.0, is_moon_bright=False)["is_benefic"] is False

    # Afflicted Mercury vs Unafflicted Mercury
    assert get_aspect_explanation("Mercury", 0.0, 180.0, is_mercury_afflicted=False)["is_benefic"] is True
    assert get_aspect_explanation("Mercury", 0.0, 180.0, is_mercury_afflicted=True)["is_benefic"] is False

    # Zero-Virupa Aspect Angle (e.g. 10 deg separation)
    exp_zero = get_aspect_explanation("Saturn", 0.0, 10.0)
    assert exp_zero["virupas"] == 0.0
    assert exp_zero["line_style"] == "none"
    assert exp_zero["nature_label"] == "No Aspect (0 Virūpas)"
    assert exp_zero["is_benefic"] is False
    assert "No Aspect / Blind Angle" in exp_zero["rule_name"]

    # Non-Casting Bodies (Rahu, Ketu, Lagna, MC)
    for non_cast in ["Rahu", "Ketu", "Lagna", "MC"]:
        exp_nc = get_aspect_explanation(non_cast, 0.0, 180.0)
        assert exp_nc["virupas"] == 0.0
        assert exp_nc["line_style"] == "none"
        assert exp_nc["nature_label"] == "Non-Casting Point"
        assert exp_nc["is_benefic"] is False
        assert f"{non_cast} does not cast Graha Dṛṣṭi" in exp_nc["rule_name"]

    # Natural Benefic Dignity Preservation (BPHS 3.21: Benefics always cast Subha rays)
    exp_jup_deb = get_aspect_explanation("Jupiter", 0.0, 120.0, aspecting_dignity="Debilitated")
    assert exp_jup_deb["is_benefic"] is True
    assert exp_jup_deb["line_style"] == "continuous"
    assert "Benefic Light" in exp_jup_deb["nature_label"]

    exp_ven_enemy = get_aspect_explanation("Venus", 0.0, 180.0, aspecting_dignity="Great Enemy")
    assert exp_ven_enemy["is_benefic"] is True
    assert exp_ven_enemy["line_style"] == "continuous"

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
    assert 'aspect-arrow' in si_svg

    # North Indian Chart
    ni_svg = generate_north_indian(items)
    assert 'class="aspects-hidden"' in ni_svg
    assert 'class="interactive-aspect"' in ni_svg
    assert 'class="interactive-aspect-badge"' in ni_svg
    assert 'data-virupas=' in ni_svg
    assert 'data-deg=' in ni_svg

    # Circular Chart (aspect lines inside center circle removed by user request)
    circ_svg = generate_circular_chart(items)
    assert 'class="aspects-hidden"' in circ_svg
    assert '<circle class="interactive-center-circle"' in circ_svg
    assert '<circle class="planet-highlight-bg"' in circ_svg
    assert '<g class="aspect-lines">' not in circ_svg

def test_frontend_template_interactive_aspect_attributes():
    with open("templates/index.html", "r", encoding="utf-8") as f:
        html = f.read()
    with open("static/js/ui/chart_interactions.js", "r", encoding="utf-8") as f:
        js = f.read()

    # Verify chart_interactions script inclusion in template
    assert 'chart_interactions.js' in html

    # Verify interactive table rows and handlers in chart_interactions.js
    assert 'interactive-table-row' in js
    assert 'selectAstrologicalEntity' in js
    assert 'clearAstrologicalEntitySelection' in js
    assert 'highlightPlanetAspects' in js
    assert 'highlightSignAspects' in js
    assert 'aspect-dynamic-badge' in js
    assert 'aspect-tag-outgoing' in js
    assert 'aspect-tag-incoming' in js
