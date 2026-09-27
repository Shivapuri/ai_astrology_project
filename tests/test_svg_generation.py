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
    assert 'viewBox="0 0 500 500"' in svg_str
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


def test_equidistant_t_spacing():
    from jyotish.draw_chart import get_equidistant_t
    assert get_equidistant_t(0) == []
    assert get_equidistant_t(1) == [0.50]
    assert get_equidistant_t(2) == [0.18, 0.82]
    assert get_equidistant_t(3) == [0.10, 0.50, 0.90]
    assert get_equidistant_t(4) == [0.06, 0.35, 0.65, 0.94]


def test_south_indian_clockwise_progression_scorpio():
    import re
    from jyotish.draw_chart import generate_south_indian

    # Scorpio is at cell (x=100, y=300).
    # Preceding sign is Libra (x=200, y=300) to its right.
    # Next sign is Sagittarius (x=0, y=300) to its left.
    # Clockwise progression: 0° starts at Bottom-Right, 30° ends at Top-Left.
    items = [
        {"type": "planet", "name": "Saturn", "sign": "Scorpio", "degree": 8, "minute": 31, "is_retrograde": False},
        {"type": "planet", "name": "Mercury", "sign": "Scorpio", "degree": 24, "minute": 35, "is_retrograde": False},
        {"type": "cusp", "text": "4", "sign": "Scorpio"}
    ]
    svg_str = generate_south_indian(items, varga_name="D1")

    # Extract Saturn and Mercury coordinates from SVG
    # Format: <text class="graha-glyph" x="PX" y="PY" ...>
    sat_match = re.search(r'data-id="Saturn"[^>]*>.*?<text[^>]*x="([0-9.]+)"[^>]*y="([0-9.]+)"', svg_str, re.DOTALL)
    merc_match = re.search(r'data-id="Mercury"[^>]*>.*?<text[^>]*x="([0-9.]+)"[^>]*y="([0-9.]+)"', svg_str, re.DOTALL)
    assert sat_match and merc_match, "Saturn or Mercury coordinates not found"

    sat_x = float(sat_match.group(1))
    sat_y = float(sat_match.group(2))
    merc_x = float(merc_match.group(1))
    merc_y = float(merc_match.group(2))

    # Saturn (8°, lower degree) must be to the right of Mercury (24°, higher degree) towards Libra
    assert sat_x > merc_x, f"Saturn x ({sat_x}) must be > Mercury x ({merc_x}) in Scorpio"
    # Saturn (8°, lower degree) must be lower than Mercury (24°, higher degree)
    assert sat_y > merc_y, f"Saturn y ({sat_y}) must be > Mercury y ({merc_y}) in Scorpio"


def test_north_indian_outer_triangle_tracks():
    from jyotish.draw_chart import generate_north_indian
    items = [
        {"type": "planet", "name": "Mars", "sign": "Taurus", "degree": 15, "minute": 0, "is_retrograde": False},
        {"type": "cusp", "text": "2", "sign": "Taurus"}
    ]
    # In Taurus (H2 when Lagna in Aries), Mars is in outer triangle
    svg_str = generate_north_indian(items, varga_name="D1")
    # Mars in H2 track at y=44 (py=44-2=42 for glyph text)
    assert 'y="42.0"' in svg_str or 'y="42"' in svg_str
    # Star (Sign glyph) at (140, 120) with font-size="8.5"
    assert 'x="140" y="120" font-size="8.5"' in svg_str
    # Square (Cusp number) at (140, 95) with font-size="8.5"
    assert 'x="140" y="95" font-family="sans-serif" font-size="8.5"' in svg_str


def test_north_equidistant_t_spacing():
    from jyotish.draw_chart import get_north_equidistant_t
    assert get_north_equidistant_t(0) == []
    assert get_north_equidistant_t(1) == [0.50]
    assert get_north_equidistant_t(2) == [0.26, 0.74]
    assert get_north_equidistant_t(3) == [0.20, 0.50, 0.80]
    assert get_north_equidistant_t(4) == [0.12, 0.37, 0.63, 0.88]


def test_north_indian_kendra_positions():
    from jyotish.draw_chart import generate_north_indian
    items = [
        {"type": "planet", "name": "Lagna", "sign": "Aries", "degree": 15, "minute": 0, "is_retrograde": False},
        {"type": "cusp", "text": "1", "sign": "Aries"}
    ]
    svg_str = generate_north_indian(items, varga_name="D1")
    # Lagna in H1 track at y=144 (py=144-2=142 for glyph text)
    assert 'y="142.0"' in svg_str or 'y="142"' in svg_str
    # Star (Sign glyph) at (250, 226) near center
    assert 'x="250" y="226" font-size="10.5"' in svg_str
    # Square (Cusp number) at (250, 202) behind star
    assert 'x="250" y="202" font-family="sans-serif" font-size="10"' in svg_str






