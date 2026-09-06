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

