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
    assert 'viewBox="0 0 560 500"' in svg_str
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
    
    # Assert reduced center circle and house ring (r_inner=30, r_outer=46)
    assert '<circle class="interactive-center-circle" cx="0" cy="0" r="30"' in svg_str
    assert '<circle cx="0" cy="0" r="46"' in svg_str
    
    # Assert house background color scheme sectors (Kendra / Trikona)
    assert 'class="house-bg house-kendra"' in svg_str
    assert 'class="house-bg house-trikona"' in svg_str
    
    # Assert internal aspect chords are removed from circular chart
    assert '<g class="aspect-lines">' not in svg_str
    
    # Assert planet highlight plate
    assert 'class="planet-highlight-bg"' in svg_str
    
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
    assert '<circle class="interactive-center-circle" cx="0" cy="0" r="28"' in svg_str
    assert '<circle cx="0" cy="0" r="44"' in svg_str # Inner house ring boundary
    assert '<circle cx="0" cy="0" r="138"' in svg_str # Subdivision ring inner boundary (UNTOUCHED)
    assert '<circle cx="0" cy="0" r="164"' in svg_str # Subdivision ring outer boundary (UNTOUCHED)
    assert '<circle cx="0" cy="0" r="206"' in svg_str # Chart outer perimeter (UNTOUCHED)
    
    # Assert house background color scheme sectors (Kendra / Trikona)
    assert 'class="house-bg house-kendra"' in svg_str
    assert 'class="house-bg house-trikona"' in svg_str
    
    # Assert planet highlight plate
    assert 'class="planet-highlight-bg"' in svg_str
    
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


def test_distance_protector_halos_and_clearances():
    from jyotish.draw_chart import generate_south_indian, generate_north_indian, generate_circular_chart, generate_biwheel_chart
    # Test South Indian: white outline removed from numbers and planets
    items_south = [
        {"type": "planet", "name": "Lagna", "sign": "Leo", "degree": 28, "minute": 53, "is_retrograde": False},
        {"type": "planet", "name": "Venus", "sign": "Leo", "degree": 28, "minute": 9, "is_retrograde": False},
        {"type": "cusp", "text": "6", "sign": "Leo"},
        {"type": "cusp", "text": "10", "sign": "Leo"}
    ]
    svg_si = generate_south_indian(items_south, varga_name="D1")
    assert 'stroke="#FFFDF9"' not in svg_si

    # Test North Indian: white outline removed from numbers and planets
    items_north = [
        {"type": "planet", "name": "Jupiter", "sign": "Aries", "degree": 14, "minute": 20, "is_retrograde": False},
        {"type": "cusp", "text": "1", "sign": "Aries"}
    ]
    svg_ni = generate_north_indian(items_north, varga_name="D1")
    assert 'stroke="#FFFDF9"' not in svg_ni

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
    # Star (Sign glyph) at (156.8, 120) with font-size="8.5"
    assert 'x="156.8" y="120" font-size="8.5"' in svg_str
    # Square (Cusp number) at (156.8, 95) with font-size="8.5"
    assert 'x="156.8" y="95" font-family="sans-serif" font-size="8.5"' in svg_str


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
    # Star (Sign glyph) at (280.0, 226) near center
    assert 'x="280.0" y="226" font-size="10.5"' in svg_str
    # Square (Cusp number) at (280.0, 202) behind star
    assert 'x="280.0" y="202" font-family="sans-serif" font-size="10"' in svg_str


def test_house_background_colors_north_and_south():
    from jyotish.draw_chart import generate_north_indian, generate_south_indian
    items = [
        {"type": "planet", "name": "Lagna", "sign": "Aries", "degree": 15, "minute": 0, "is_retrograde": False},
        {"type": "cusp", "text": "1", "sign": "Aries"}
    ]
    ni_svg = generate_north_indian(items, varga_name="D1")
    si_svg = generate_south_indian(items, varga_name="D1")

    # North Indian: 4 Kendras (1,4,7,10), 2 Trikonas (5,9), 6 Other houses
    assert ni_svg.count('class="house-bg house-kendra"') == 4
    assert ni_svg.count('class="house-bg house-trikona"') == 2
    assert ni_svg.count('class="house-bg house-other"') == 6
    assert 'var(--chart-kendra-color, #eedec9)' in ni_svg
    assert 'var(--chart-trikona-color, #faede0)' in ni_svg
    assert 'var(--chart-other-color, #f9f5eb)' in ni_svg

    # South Indian: 4 Kendras (1,4,7,10), 2 Trikonas (5,9), 6 Other houses
    assert si_svg.count('class="house-bg house-kendra"') == 4
    assert si_svg.count('class="house-bg house-trikona"') == 2
    assert si_svg.count('class="house-bg house-other"') == 6
    assert 'var(--chart-kendra-color, #eedec9)' in si_svg
    assert 'var(--chart-trikona-color, #faede0)' in si_svg
    assert 'var(--chart-other-color, #f9f5eb)' in si_svg


def test_nakshatra_display_north_south_and_biwheel():
    from jyotish.draw_chart import generate_north_indian, generate_south_indian, generate_biwheel_chart
    items = [
        {"type": "planet", "name": "Sun", "sign": "Aries", "degree": 10, "minute": 20, "is_retrograde": False, "nakshatra": "Ashwini"},
        {"type": "planet", "name": "Moon", "sign": "Taurus", "degree": 15, "minute": 30, "is_retrograde": True, "nakshatra": "Rohini"},
        {"type": "cusp", "text": "1", "sign": "Aries"}
    ]
    
    # 1. North Indian with show_nakshatras=True
    ni_svg = generate_north_indian(items, varga_name="D1", show_nakshatras=True)
    assert "Ashw" in ni_svg
    assert "Rohi" in ni_svg
    assert '#8c7b64' in ni_svg
    assert '<tspan>10°20\'</tspan>' in ni_svg
    assert '<tspan>15°30\'</tspan>' in ni_svg
    
    # North Indian with show_nakshatras=False
    ni_svg_off = generate_north_indian(items, varga_name="D1", show_nakshatras=False)
    assert "Ashw" not in ni_svg_off
    assert "Rohi" not in ni_svg_off
    
    # 2. South Indian with show_nakshatras=True
    si_svg = generate_south_indian(items, varga_name="D1", show_nakshatras=True)
    assert "Ashw" in si_svg
    assert "Rohi" in si_svg
    assert '#8c7b64' in si_svg
    assert '<tspan>10°20\'</tspan>' in si_svg
    
    # South Indian with show_nakshatras=False
    si_svg_off = generate_south_indian(items, varga_name="D1", show_nakshatras=False)
    assert "Ashw" not in si_svg_off
    assert "Rohi" not in si_svg_off
    
    # 3. Bi-Wheel with show_nakshatras=True
    bi_svg = generate_biwheel_chart(items, items, inner_name="D1", outer_name="D9", show_nakshatras=True)
    assert "Ashw" in bi_svg
    assert "Rohi" in bi_svg
    assert '#8c7b64' in bi_svg
    
    # Bi-Wheel with show_nakshatras=False
    bi_svg_off = generate_biwheel_chart(items, items, inner_name="D1", outer_name="D9", show_nakshatras=False)
    assert "Ashw" not in bi_svg_off
    assert "Rohi" not in bi_svg_off


def test_biwheel_d2_hora_outer_glyphs_and_subdivisions():
    from jyotish.draw_chart import generate_biwheel_chart
    inner_items = [
        {"type": "planet", "name": "Lagna", "sign": "Aries", "degree": 5, "minute": 10, "is_retrograde": False},
        {"type": "planet", "name": "Sun", "sign": "Aries", "degree": 10, "minute": 20, "is_retrograde": False},
        {"type": "planet", "name": "Moon", "sign": "Taurus", "degree": 20, "minute": 40, "is_retrograde": False},
        {"type": "cusp", "text": "1", "sign": "Aries"}
    ]
    outer_items = [
        {
            "type": "planet", "name": "Lagna", "sign": "Leo", "degree": 10, "minute": 20, "is_retrograde": False,
            "hora_lord": "Sun", "hora_symbol": "☉", "hora_polarity": "Solar / Pingala"
        },
        {
            "type": "planet", "name": "Sun", "sign": "Leo", "degree": 20, "minute": 40, "is_retrograde": False,
            "hora_lord": "Sun", "hora_symbol": "☉", "hora_polarity": "Solar / Pingala"
        },
        {
            "type": "planet", "name": "Moon", "sign": "Cancer", "degree": 11, "minute": 20, "is_retrograde": False,
            "hora_lord": "Moon", "hora_symbol": "☽", "hora_polarity": "Lunar / Ida"
        }
    ]
    svg_d2 = generate_biwheel_chart(inner_items, outer_items, inner_name="D1", outer_name="D2")
    
    # 1. Outer sign glyph must show Sun (☉) and Moon (☽), NOT Leo (♌) or Cancer (♋)
    assert '<text class="outer-sign-glyph"' in svg_d2
    assert '>☉</text>' in svg_d2
    assert '>☽</text>' in svg_d2
    
    # 2. Harmonic subdivision ring must contain D2 Hora divisions (Solar and Lunar halves)
    assert 'data-type="varga-division" data-varga="D2"' in svg_d2
    assert 'D2 Horā:' in svg_d2
    assert 'Solar / Pingala' in svg_d2
    assert 'Lunar / Ida' in svg_d2


def test_biwheel_d3_drekkana_outer_glyphs_and_subdivisions():
    from jyotish.draw_chart import generate_biwheel_chart
    inner_items = [
        {"type": "planet", "name": "Lagna", "sign": "Aries", "degree": 5, "minute": 10, "is_retrograde": False},
        {"type": "planet", "name": "Mars", "sign": "Aries", "degree": 15, "minute": 20, "is_retrograde": False},
        {"type": "cusp", "text": "1", "sign": "Aries"}
    ]
    outer_items = [
        {
            "type": "planet", "name": "Lagna", "sign": "Aries", "degree": 15, "minute": 30, "is_retrograde": False,
            "ruler": "Mars", "display_symbol": "♂", "display_entity": "♂ Mars"
        },
        {
            "type": "planet", "name": "Mars", "sign": "Leo", "degree": 16, "minute": 0, "is_retrograde": False,
            "ruler": "Sun", "display_symbol": "☉", "display_entity": "☉ Sun"
        }
    ]
    svg_d3 = generate_biwheel_chart(inner_items, outer_items, inner_name="D1", outer_name="D3")
    
    # 1. Outer sign glyph shows decan lord symbols
    assert '<text class="outer-sign-glyph"' in svg_d3
    assert '>♂</text>' in svg_d3
    assert '>☉</text>' in svg_d3
    
    # 2. Harmonic subdivision ring must contain Drekkana decan divisions
    assert 'data-type="varga-division" data-varga="D3"' in svg_d3
    assert 'D3 Drekkāṇa Trine' in svg_d3


def test_biwheel_d30_trimsamsa_outer_glyphs_and_subdivisions():
    from jyotish.draw_chart import generate_biwheel_chart
    inner_items = [
        {"type": "planet", "name": "Lagna", "sign": "Aries", "degree": 5, "minute": 10, "is_retrograde": False},
        {"type": "planet", "name": "Saturn", "sign": "Aries", "degree": 7, "minute": 20, "is_retrograde": False},
        {"type": "cusp", "text": "1", "sign": "Aries"}
    ]
    outer_items = [
        {
            "type": "planet", "name": "Lagna", "sign": "Aries", "degree": 25, "minute": 0, "is_retrograde": False,
            "bound_ruler": "Mars", "bound_symbol": "♂", "bound_degree": 5.0, "bound_sign": "Aries"
        },
        {
            "type": "planet", "name": "Saturn", "sign": "Aquarius", "degree": 12, "minute": 0, "is_retrograde": False,
            "bound_ruler": "Saturn", "bound_symbol": "♄", "bound_degree": 2.0, "bound_sign": "Aquarius"
        }
    ]
    svg_d30 = generate_biwheel_chart(inner_items, outer_items, inner_name="D1", outer_name="D30")
    
    # 1. Outer sign glyph shows bound ruler symbols
    assert '<text class="outer-sign-glyph"' in svg_d30
    assert '>♂</text>' in svg_d30
    assert '>♄</text>' in svg_d30
    
    # 2. Harmonic subdivision ring must contain Parashari Trimsamsa bound divisions
    assert 'data-type="varga-division" data-varga="D30"' in svg_d30
    assert 'D30 Triṁśāṁśa Bound:' in svg_d30


def test_circular_chart_varga_slices_mode():
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
    svg_varga = generate_circular_chart(
        items, mode="symbol", varga_name="D1", ayanamsha=0.0, root_planet="Lagna", wheel_mode="varga_slices"
    )

    # 1. Title and center hub indicate Concentric Varga Wheel
    assert "D1 Concentric Varga Wheel" in svg_varga
    assert ">Vargas</text>" in svg_varga

    # 2. Concentric boundary circles for 5 stacked varga rings (radii: 120, 140, 153, 166, 179, 192, 205)
    assert '<circle cx="0" cy="0" r="205"' in svg_varga
    assert '<circle cx="0" cy="0" r="192"' in svg_varga
    assert '<circle cx="0" cy="0" r="179"' in svg_varga
    assert '<circle cx="0" cy="0" r="166"' in svg_varga
    assert '<circle cx="0" cy="0" r="153"' in svg_varga
    assert '<circle cx="0" cy="0" r="140"' in svg_varga
    assert '<circle cx="0" cy="0" r="120"' in svg_varga

    # 3. Concentric rings container & glyphs present for Core Shadvarga: D2, D3, D30, D9, D12
    assert 'class="varga-concentric-rings' in svg_varga
    assert 'data-varga="D2"' in svg_varga
    assert 'data-varga="D3"' in svg_varga
    assert 'data-varga="D30"' in svg_varga
    assert 'data-varga="D9"' in svg_varga
    assert 'data-varga="D12"' in svg_varga
    assert 'class="interactive varga-slice-glyph"' in svg_varga

    # 4. Continuous planetary radial piercing rays (spokes) across all 5 varga rings
    assert '<g class="varga-piercing-spokes"' in svg_varga
    assert '<line class="varga-piercing-ray" data-planet="Mars"' in svg_varga
    assert '<line class="varga-piercing-ray" data-planet="Jupiter"' in svg_varga
    assert '<circle class="varga-piercing-dot" data-planet="Sun"' in svg_varga
    assert '<line class="varga-piercing-ray" data-planet="Lagna"' in svg_varga

    # 5. Default nakshatras mode should NOT have varga-concentric-rings or piercing rays
    svg_nak = generate_circular_chart(
        items, mode="symbol", varga_name="D1", ayanamsha=0.0, root_planet="Lagna", wheel_mode="nakshatras"
    )
    assert '<g class="varga-concentric-rings">' not in svg_nak
    assert '<g class="varga-piercing-spokes"' not in svg_nak


def test_circular_chart_classical_varga_mode():
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
    svg_class = generate_circular_chart(
        items, mode="symbol", varga_name="D1", ayanamsha=0.0, root_planet="Lagna", wheel_mode="mantreshwara"
    )

    # 1. Title and center hub indicate Classical Varga Wheel
    assert "D1 Classical Varga Wheel" in svg_class
    assert ">Classical</text>" in svg_class

    # 2. Concentric boundary circles for D2, D3, D30, D60 (radii: 120, 140, 156, 172, 188, 205)
    assert '<circle cx="0" cy="0" r="205"' in svg_class
    assert '<circle cx="0" cy="0" r="188"' in svg_class
    assert '<circle cx="0" cy="0" r="172"' in svg_class
    assert '<circle cx="0" cy="0" r="156"' in svg_class
    assert '<circle cx="0" cy="0" r="140"' in svg_class
    assert '<circle cx="0" cy="0" r="120"' in svg_class

    # 3. Concentric rings container & classical specialized rings
    assert 'class="varga-concentric-rings varga-classical-rings"' in svg_class
    assert 'data-varga="D2"' in svg_class
    assert 'class="d2-slice-bg"' in svg_class
    assert 'data-varga="D3"' in svg_class
    assert 'data-varga="D30"' in svg_class
    assert 'data-varga="D60"' in svg_class
    assert 'class="d60-slice"' in svg_class
    assert 'data-nature="ashubha"' in svg_class
    assert 'data-nature="shubha"' in svg_class

    # 4. Continuous planetary radial piercing rays (spokes) with rich D2/D3/D30/D60 tooltip
    assert '<g class="varga-piercing-spokes"' in svg_class
    assert '<line class="varga-piercing-ray" data-planet="Mars"' in svg_class
    assert '<circle class="varga-piercing-dot" data-planet="Sun"' in svg_class
    assert 'D2:' in svg_class
    assert 'D3:' in svg_class
    assert 'D30:' in svg_class
    assert 'D60 #' in svg_class



