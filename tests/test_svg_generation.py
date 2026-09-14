import pytest
from jyotish.draw_chart import generate_south_indian, generate_north_indian

def test_south_indian_svg():
    # Provide a simple mock items list
    items = [
        {"type": "planet", "name": "Sun", "sign": "Aries", "degree": 10, "minute": 20, "is_retrograde": False},
        {"type": "cusp", "text": "1", "sign": "Aries"}
    ]
    svg_str = generate_south_indian(items, varga_name="D1 - Rasi")
    
    # Assert background is transparent and viewBox provides safe margin
    assert 'viewBox="-10 -10 420 420"' in svg_str
    assert 'background:transparent' in svg_str
    
    # Assert center title is embedded
    assert 'D1 - Rasi' in svg_str
    
def test_north_indian_svg():
    items = [
        {"type": "planet", "name": "Lagna", "sign": "Aries", "degree": 5, "minute": 10, "is_retrograde": False},
        {"type": "planet", "name": "Sun", "sign": "Aries", "degree": 10, "minute": 20, "is_retrograde": False},
        {"type": "cusp", "text": "1", "sign": "Aries"}
    ]
    svg_str = generate_north_indian(items, varga_name="D9 - Navamsa")
    
    # Assert background is transparent and viewBox provides safe margin
    assert 'viewBox="-10 -10 420 420"' in svg_str
    assert 'background:transparent' in svg_str

def test_south_indian_multiple_cusps_separated():
    items = [
        {"type": "planet", "name": "Lagna", "sign": "Aries", "degree": 5, "minute": 10, "is_retrograde": False},
        {"type": "cusp", "text": "1", "sign": "Aries"},
        {"type": "cusp", "text": "2", "sign": "Gemini"},
        {"type": "cusp", "text": "3", "sign": "Gemini"},
    ]
    svg_str = generate_south_indian(items, varga_name="D1")
    
    # Assert both cusp 2 and cusp 3 are rendered as independent interactive elements with distinct data-ids
    assert '<g class="interactive" data-type="house" data-id="2"' in svg_str
    assert '<g class="interactive" data-type="house" data-id="3"' in svg_str
    # Assert background is not cluttered with house-cell rects
    assert 'class="interactive house-cell"' not in svg_str

def test_north_indian_multiple_cusps_separated():
    items = [
        {"type": "planet", "name": "Lagna", "sign": "Aries", "degree": 5, "minute": 10, "is_retrograde": False},
        {"type": "cusp", "text": "1", "sign": "Aries"},
        {"type": "cusp", "text": "2", "sign": "Taurus"},
        {"type": "cusp", "text": "3", "sign": "Taurus"},
    ]
    svg_str = generate_north_indian(items, varga_name="D1")
    
    # Assert both cusp 2 and cusp 3 are rendered as independent interactive elements
    assert '<g class="interactive" data-type="house" data-id="2"' in svg_str
    assert '<g class="interactive" data-type="house" data-id="3"' in svg_str
    # Assert background is not cluttered with house-cell polygons
    assert 'class="interactive house-cell"' not in svg_str

def test_circular_chart_aspects_and_radii():
    from jyotish.draw_chart import generate_circular_chart
    items = [
        {"type": "planet", "name": "Lagna", "sign": "Leo", "degree": 9, "minute": 33, "is_retrograde": False},
        {"type": "planet", "name": "Jupiter", "sign": "Aries", "degree": 18, "minute": 15, "is_retrograde": False},
        {"type": "planet", "name": "Mars", "sign": "Aries", "degree": 14, "minute": 8, "is_retrograde": False},
        {"type": "planet", "name": "Moon", "sign": "Gemini", "degree": 11, "minute": 54, "is_retrograde": False},
        {"type": "planet", "name": "Sun", "sign": "Gemini", "degree": 17, "minute": 51, "is_retrograde": False},
        {"type": "planet", "name": "Saturn", "sign": "Cancer", "degree": 17, "minute": 55, "is_retrograde": False},
        {"type": "cusp", "text": "1", "sign": "Leo", "degree": 9, "minute": 33},
        {"type": "cusp", "text": "10", "sign": "Taurus", "degree": 5, "minute": 20}
    ]
    svg_str = generate_circular_chart(items, mode="symbol", varga_name="D1", ayanamsha=19.33, root_planet="Lagna")
    
    # Assert enlarged aspect circle
    assert '<circle class="interactive-center-circle" cx="0" cy="0" r="76"' in svg_str
    assert '<circle cx="0" cy="0" r="92"' in svg_str
    
    # Assert aspect markers and aspect group
    assert '<marker id="arrow-benefic"' in svg_str
    assert '<g class="aspect-lines">' in svg_str
    assert 'class="interactive-aspect"' in svg_str
    assert 'data-from=' in svg_str
    assert 'data-to=' in svg_str
    
    # Assert planet stack has glyph, degree, minute but NOT redundant sign symbol
    assert 'data-id="Mars"' in svg_str
    assert '14°' in svg_str
    assert "08'" in svg_str
    # In circular chart, Mars's group should not contain sign symbol ♈
    mars_block = svg_str.split('data-id="Mars"')[1].split('</g>')[0]
    assert "♈" not in mars_block


