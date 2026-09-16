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


def test_biwheel_chart_svg_structure():
    from jyotish.draw_chart import generate_biwheel_chart
    inner = [
        {"type": "planet", "name": "Lagna", "sign": "Leo", "degree": 9, "minute": 33, "is_retrograde": False},
        {"type": "planet", "name": "Sun", "sign": "Gemini", "degree": 17, "minute": 51, "is_retrograde": False},
        {"type": "planet", "name": "Jupiter", "sign": "Aries", "degree": 18, "minute": 15, "is_retrograde": False},
        {"type": "cusp", "text": "1", "sign": "Leo", "degree": 9, "minute": 33},
        {"type": "cusp", "text": "10", "sign": "Taurus", "degree": 5, "minute": 20}
    ]
    outer = [
        {"type": "planet", "name": "Lagna", "sign": "Aries", "degree": 5, "minute": 10, "is_retrograde": False},
        {"type": "planet", "name": "Sun", "sign": "Gemini", "degree": 10, "minute": 25, "is_retrograde": False}, # Vargottama Sun!
        {"type": "planet", "name": "Jupiter", "sign": "Cancer", "degree": 22, "minute": 40, "is_retrograde": False},
        {"type": "planet", "name": "Saturn", "sign": "Aquarius", "degree": 15, "minute": 0, "is_retrograde": False}
    ]
    svg_str = generate_biwheel_chart(inner, outer, inner_name="D1", outer_name="D9", mode="symbol", ayanamsha=19.33, root_planet="Lagna")
    
    # 1. Dimensions & Background
    assert 'viewBox="-210 -210 420 420"' in svg_str
    assert 'background:transparent' in svg_str
    
    # 2. Key Concentric Rings & Geometry
    assert '<circle class="interactive-center-circle" cx="0" cy="0" r="62"' in svg_str
    assert '<circle cx="0" cy="0" r="138"' in svg_str # Subdivision ring inner boundary
    assert '<circle cx="0" cy="0" r="164"' in svg_str # Subdivision ring outer boundary
    assert '<circle cx="0" cy="0" r="206"' in svg_str # Chart outer perimeter
    
    # Nakshatra perimeter ring removed from Bi-Wheel chart
    assert 'data-type="nakshatra"' not in svg_str

    # 3. Inner Natal Signs & Harmonic Subdivisions
    assert 'class="interactive natal-sign-glyph"' in svg_str
    assert 'class="interactive sub-sign-symbol"' in svg_str
    assert '30°' in svg_str
    
    # 4. Inner and Outer Planet Elements
    assert 'data-varga="D1"' in svg_str
    assert 'data-varga="D9"' in svg_str
    assert 'class="interactive planet-glyph inner-planet' in svg_str
    assert 'class="interactive planet-glyph outer-planet' in svg_str
    assert 'class="outer-sign-glyph"' in svg_str # Divisional sign tag on outer planets
    
    # 5. Radial Alignment Dots & Rays (Inner border r=138, Outer border r=164)
    assert 'class="radial-alignment-dot inner-dot"' in svg_str
    assert 'class="radial-alignment-dot outer-dot"' in svg_str
    assert 'outer-ray-in' in svg_str
    assert 'outer-ray' in svg_str
    assert 'vargottama-beam' not in svg_str
    assert 'vargottama-halo' not in svg_str
    
    # 6. Natal House alignment in outer planet tooltip
    # D9 Saturn in Aquarius with D1 Lagna in Leo -> Aquarius is 7th sign from Leo -> Natal House 7
    assert '(Natal House 7)' in svg_str
    
    # 7. Cross-Chart Aspects
    assert 'class="interactive-aspect cross-aspect"' in svg_str
    assert 'data-from-varga="D9"' in svg_str
    assert 'data-to-varga="D1"' in svg_str


def test_distance_protector_halos_and_clearances():
    from jyotish.draw_chart import generate_south_indian, generate_north_indian, generate_circular_chart, generate_biwheel_chart
    # Test South Indian protective halos
    items_south = [
        {"type": "planet", "name": "Lagna", "sign": "Leo", "degree": 28, "minute": 53, "is_retrograde": False},
        {"type": "planet", "name": "Venus", "sign": "Leo", "degree": 28, "minute": 9, "is_retrograde": False},
        {"type": "cusp", "text": "6", "sign": "Leo"},
        {"type": "cusp", "text": "10", "sign": "Leo"}
    ]
    svg_si = generate_south_indian(items_south, varga_name="D1")
    assert 'stroke="#FFFDF9"' in svg_si
    assert 'paint-order="stroke fill"' in svg_si

    # Test North Indian protective halos
    items_north = [
        {"type": "planet", "name": "Jupiter", "sign": "Aries", "degree": 14, "minute": 20, "is_retrograde": False},
        {"type": "cusp", "text": "1", "sign": "Aries"}
    ]
    svg_ni = generate_north_indian(items_north, varga_name="D1")
    assert 'stroke="#FFFDF9"' in svg_ni
    assert 'paint-order="stroke fill"' in svg_ni

    # Test Circular Chart cusp halos & Lagna obstacle protection
    svg_circ = generate_circular_chart(items_south, varga_name="D1", root_planet="Lagna")
    assert 'stroke="#FAF7F0"' in svg_circ
    assert 'paint-order="stroke fill"' in svg_circ

    # Test Bi-Wheel chart protective halos on inner signs and bhava numbers
    svg_bi = generate_biwheel_chart(items_south, items_south, inner_name="D1", outer_name="D9")
    assert 'class="interactive natal-sign-glyph"' in svg_bi
    assert 'stroke="#ffffff"' in svg_bi
    assert 'stroke="#FAF7F0"' in svg_bi


def test_biwheel_dahmer_zodiac_alignment():
    """
    Verifies that in the Bi-Wheel chart:
    - Inner D1 Lagna is in Libra
    - Outer D9 Lagna is located in Pisces (Natal House 6)
    - D1 Jupiter is in Capricorn
    - Outer D9 Jupiter and D9 Ketu are located in Capricorn (Natal House 4)
    - Jupiter is Vargottama with a connecting beam
    - Harmonic subdivision tick marks exist along the Zodiac border
    """
    import json
    from app import compute_chart_data
    from jyotish import draw_chart

    with open("database/Charts.jsonl") as f:
        target = None
        for line in f:
            d = json.loads(line)
            if "dahmer" in d.get("name", "").lower():
                target = d
                break
    assert target is not None, "Jeffrey Dahmer chart not found in Charts.jsonl"

    chart = compute_chart_data(target)
    d1 = draw_chart.parse_varga_data(chart["vargas"]["D1"])
    d9 = draw_chart.parse_varga_data(chart["vargas"]["D9"])

    svg = draw_chart.generate_biwheel_chart(d1, d9, inner_name="D1", outer_name="D9")
    
    # Outer Lagna in Pisces
    assert "D9 Lagna in Pisces 25° 00' (Natal House 6)" in svg
    # Outer Jupiter & Ketu in Capricorn
    assert "D9 Guru in Capricorn 18° 53'R (Natal House 4)" in svg
    assert "D9 Ketu in Capricorn 21° 34'R (Natal House 4)" in svg
    # Absence of vargottama beam
    assert "vargottama-beam" not in svg
    # Harmonic subdivision ticks along the border
    assert 'class="harmonic-subdivision-tick"' in svg





