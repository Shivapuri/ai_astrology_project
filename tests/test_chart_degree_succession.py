import re
import pytest
from jyotish.draw_chart import (
    generate_south_indian,
    generate_north_indian,
    get_equidistant_t,
    get_north_equidistant_t
)

def extract_planet_pos(svg_str, planet_name):
    """Helper to extract (x, y) coordinates of a planet glyph from chart SVG."""
    pattern = rf'data-id="{planet_name}"[^>]*>.*?<text[^>]*x="([0-9.]+)"[^>]*y="([0-9.]+)"'
    match = re.search(pattern, svg_str, re.DOTALL)
    assert match, f"Planet '{planet_name}' not found in SVG"
    return float(match.group(1)), float(match.group(2))


def test_south_indian_all_four_triplets_degree_succession():
    """
    Safeguards that South Indian chart strictly progresses clockwise from
    preceding house (lower degree) to succeeding house (higher degree)
    across all 4 triplets.
    """
    items = [
        # Triplet 1: Aries (Top row, Left -> Right)
        {"type": "planet", "name": "Moon", "sign": "Aries", "degree": 5, "minute": 0, "is_retrograde": False},
        {"type": "planet", "name": "Mars", "sign": "Aries", "degree": 25, "minute": 0, "is_retrograde": False},
        {"type": "cusp", "text": "1", "sign": "Aries"},

        # Triplet 2: Leo (Right column, Top -> Bottom)
        {"type": "planet", "name": "Sun", "sign": "Leo", "degree": 5, "minute": 0, "is_retrograde": False},
        {"type": "planet", "name": "Venus", "sign": "Leo", "degree": 25, "minute": 0, "is_retrograde": False},
        {"type": "cusp", "text": "5", "sign": "Leo"},

        # Triplet 3: Scorpio (Bottom row, Right -> Left)
        {"type": "planet", "name": "Saturn", "sign": "Scorpio", "degree": 5, "minute": 0, "is_retrograde": False},
        {"type": "planet", "name": "Mercury", "sign": "Scorpio", "degree": 25, "minute": 0, "is_retrograde": False},
        {"type": "cusp", "text": "8", "sign": "Scorpio"},

        # Triplet 4: Aquarius (Left column, Bottom -> Top)
        {"type": "planet", "name": "Jupiter", "sign": "Aquarius", "degree": 5, "minute": 0, "is_retrograde": False},
        {"type": "planet", "name": "Rahu", "sign": "Aquarius", "degree": 25, "minute": 0, "is_retrograde": True},
        {"type": "cusp", "text": "11", "sign": "Aquarius"},
    ]

    svg = generate_south_indian(items, varga_name="D1")

    # 1. Triplet 1 (Aries: TL -> BR, Left to Right)
    moon_x, moon_y = extract_planet_pos(svg, "Moon")
    mars_x, mars_y = extract_planet_pos(svg, "Mars")
    assert moon_x < mars_x, f"Triplet 1 (Aries): lower deg Moon x ({moon_x}) must be < higher deg Mars x ({mars_x})"
    assert moon_y < mars_y, f"Triplet 1 (Aries): lower deg Moon y ({moon_y}) must be < higher deg Mars y ({mars_y})"

    # 2. Triplet 2 (Leo: TR -> BL, Top to Bottom)
    sun_x, sun_y = extract_planet_pos(svg, "Sun")
    venus_x, venus_y = extract_planet_pos(svg, "Venus")
    assert sun_y < venus_y, f"Triplet 2 (Leo): lower deg Sun y ({sun_y}) must be < higher deg Venus y ({venus_y})"
    assert sun_x > venus_x, f"Triplet 2 (Leo): lower deg Sun x ({sun_x}) must be > higher deg Venus x ({venus_x})"

    # 3. Triplet 3 (Scorpio: BR -> TL, Right to Left)
    sat_x, sat_y = extract_planet_pos(svg, "Saturn")
    merc_x, merc_y = extract_planet_pos(svg, "Mercury")
    assert sat_x > merc_x, f"Triplet 3 (Scorpio): lower deg Saturn x ({sat_x}) must be > higher deg Mercury x ({merc_x})"
    assert sat_y > merc_y, f"Triplet 3 (Scorpio): lower deg Saturn y ({sat_y}) must be > higher deg Mercury y ({merc_y})"

    # 4. Triplet 4 (Aquarius: BL -> TR, Bottom to Top)
    jup_x, jup_y = extract_planet_pos(svg, "Jupiter")
    rahu_x, rahu_y = extract_planet_pos(svg, "Rahu")
    assert jup_y > rahu_y, f"Triplet 4 (Aquarius): lower deg Jupiter y ({jup_y}) must be > higher deg Rahu y ({rahu_y})"
    assert jup_x < rahu_x, f"Triplet 4 (Aquarius): lower deg Jupiter x ({jup_x}) must be < higher deg Rahu x ({rahu_x})"


def test_south_indian_single_planet_centering():
    """Safeguards that a single planet in a cell is placed at the exact dead center (t=0.50)."""
    items = [
        {"type": "planet", "name": "Sun", "sign": "Aries", "degree": 14, "minute": 0, "is_retrograde": False},
        {"type": "cusp", "text": "1", "sign": "Aries"}
    ]
    svg = generate_south_indian(items, varga_name="D1")
    sun_x, sun_y = extract_planet_pos(svg, "Sun")

    # Aries cell is at x in [100, 200], y in [0, 100]. Dead center is (150, 50).
    # With start=(16, 16) and end=(84, 84), midpoint is (100+50, 0+50) = (150, 50).
    # Accounting for text label y offset (-2), px=150, py=48.
    assert abs(sun_x - 150.0) < 0.1, f"Expected Sun x at dead center (150), got {sun_x}"
    assert abs(sun_y - 48.0) < 0.1, f"Expected Sun y at dead center (48), got {sun_y}"


def test_south_indian_cross_diagonal_sign_and_cusp_anchors():
    """Safeguards that Sign and Cusp numbers are anchored at opposite cross-diagonal corners."""
    items = [
        {"type": "cusp", "text": "1", "sign": "Aries"},       # T1: Cusp BL (13, 87), Sign TR (87, 13)
        {"type": "cusp", "text": "4", "sign": "Cancer"},      # T2: Cusp TL (13, 13), Sign BR (87, 87)
        {"type": "cusp", "text": "7", "sign": "Libra"},       # T3: Cusp TR (87, 13), Sign BL (13, 87)
        {"type": "cusp", "text": "10", "sign": "Capricorn"},  # T4: Cusp BR (87, 87), Sign TL (13, 13)
    ]
    svg = generate_south_indian(items, varga_name="D1")

    # Aries (cell x=100, y=0): Sign TR at (187, 13), Cusp BL at (113, 87)
    assert 'x="187" y="13"' in svg, "Aries sign glyph must be at TR (187, 13)"
    assert 'x="113" y="87"' in svg, "Aries cusp must be at BL (113, 87)"

    # Cancer (cell x=300, y=100): Sign BR at (387, 187), Cusp TL at (313, 113)
    assert 'x="387" y="187"' in svg, "Cancer sign glyph must be at BR (387, 187)"
    assert 'x="313" y="113"' in svg, "Cancer cusp must be at TL (313, 113)"

    # Libra (cell x=200, y=300): Sign BL at (213, 387), Cusp TR at (287, 313)
    assert 'x="213" y="387"' in svg, "Libra sign glyph must be at BL (213, 387)"
    assert 'x="287" y="313"' in svg, "Libra cusp must be at TR (287, 313)"

    # Capricorn (cell x=0, y=200): Sign TL at (13, 213), Cusp BR at (87, 287)
    assert 'x="13" y="213"' in svg, "Capricorn sign glyph must be at TL (13, 213)"
    assert 'x="87" y="287"' in svg, "Capricorn cusp must be at BR (87, 287)"


def test_north_indian_all_four_kendras_degree_succession():
    """
    Safeguards that North Indian Kendras progress strictly from entrance to exit
    with outward-pushed tracks:
    - H1: Right -> Left along y=144
    - H4: Top -> Bottom along x=144
    - H7: Left -> Right along y=356
    - H10: Bottom -> Top along x=356
    """
    items = [
        # H1 (Aries): Sun 5°, Moon 25°
        {"type": "planet", "name": "Sun", "sign": "Aries", "degree": 5, "minute": 0, "is_retrograde": False},
        {"type": "planet", "name": "Moon", "sign": "Aries", "degree": 25, "minute": 0, "is_retrograde": False},
        {"type": "cusp", "text": "1", "sign": "Aries"},

        # H4 (Cancer): Mars 5°, Mercury 25°
        {"type": "planet", "name": "Mars", "sign": "Cancer", "degree": 5, "minute": 0, "is_retrograde": False},
        {"type": "planet", "name": "Mercury", "sign": "Cancer", "degree": 25, "minute": 0, "is_retrograde": False},
        {"type": "cusp", "text": "4", "sign": "Cancer"},

        # H7 (Libra): Jupiter 5°, Venus 25°
        {"type": "planet", "name": "Jupiter", "sign": "Libra", "degree": 5, "minute": 0, "is_retrograde": False},
        {"type": "planet", "name": "Venus", "sign": "Libra", "degree": 25, "minute": 0, "is_retrograde": False},
        {"type": "cusp", "text": "7", "sign": "Libra"},

        # H10 (Capricorn): Saturn 5°, Rahu 25°
        {"type": "planet", "name": "Saturn", "sign": "Capricorn", "degree": 5, "minute": 0, "is_retrograde": False},
        {"type": "planet", "name": "Rahu", "sign": "Capricorn", "degree": 25, "minute": 0, "is_retrograde": True},
        {"type": "cusp", "text": "10", "sign": "Capricorn"},
    ]

    svg = generate_north_indian(items, varga_name="D1")

    # H1: Right to Left (lower degree Sun x > higher degree Moon x), y=144
    sun_x, sun_y = extract_planet_pos(svg, "Sun")
    moon_x, moon_y = extract_planet_pos(svg, "Moon")
    assert sun_x > moon_x, f"H1: lower deg Sun x ({sun_x}) must be > higher deg Moon x ({moon_x})"
    assert abs(sun_y - 142.0) < 0.1 and abs(moon_y - 142.0) < 0.1, "H1 track must be horizontal at y=144 (text y=142)"

    # H4: Top to Bottom (lower degree Mars y < higher degree Mercury y), x=144
    mars_x, mars_y = extract_planet_pos(svg, "Mars")
    merc_x, merc_y = extract_planet_pos(svg, "Mercury")
    assert mars_y < merc_y, f"H4: lower deg Mars y ({mars_y}) must be < higher deg Mercury y ({merc_y})"
    assert abs(mars_x - 144.0) < 0.1 and abs(merc_x - 144.0) < 0.1, "H4 track must be vertical at x=144"

    # H7: Left to Right (lower degree Jupiter x < higher degree Venus x), y=356
    jup_x, jup_y = extract_planet_pos(svg, "Jupiter")
    venus_x, venus_y = extract_planet_pos(svg, "Venus")
    assert jup_x < venus_x, f"H7: lower deg Jupiter x ({jup_x}) must be < higher deg Venus x ({venus_x})"
    assert abs(jup_y - 354.0) < 0.1 and abs(venus_y - 354.0) < 0.1, "H7 track must be horizontal at y=356 (text y=354)"

    # H10: Bottom to Top (lower degree Saturn y > higher degree Rahu y), x=356
    sat_x, sat_y = extract_planet_pos(svg, "Saturn")
    rahu_x, rahu_y = extract_planet_pos(svg, "Rahu")
    assert sat_y > rahu_y, f"H10: lower deg Saturn y ({sat_y}) must be > higher deg Rahu y ({rahu_y})"
    assert abs(sat_x - 356.0) < 0.1 and abs(rahu_x - 356.0) < 0.1, "H10 track must be vertical at x=356"


def test_north_indian_kendra_center_sign_and_cusp_anchors():
    """
    Safeguards that in Kendras:
    - Zodiac sign glyph (Star) is centered near the medallion (24px offset)
    - House cusp number (Square) sits behind the sign (48px offset)
    """
    items = [
        {"type": "cusp", "text": "1", "sign": "Aries"},
        {"type": "cusp", "text": "4", "sign": "Cancer"},
        {"type": "cusp", "text": "7", "sign": "Libra"},
        {"type": "cusp", "text": "10", "sign": "Capricorn"},
    ]
    svg = generate_north_indian(items, varga_name="D1")

    # H1 (Top): Sign at (250, 226), Cusp at (250, 202)
    assert 'x="250" y="226" font-size="10.5"' in svg
    assert 'x="250" y="202" font-family="sans-serif" font-size="10"' in svg

    # H4 (Left): Sign at (226, 250), Cusp at (202, 250)
    assert 'x="226" y="250" font-size="10.5"' in svg
    assert 'x="202" y="250" font-family="sans-serif" font-size="10"' in svg

    # H7 (Bottom): Sign at (250, 274), Cusp at (250, 298)
    assert 'x="250" y="274" font-size="10.5"' in svg
    assert 'x="250" y="298" font-family="sans-serif" font-size="10"' in svg

    # H10 (Right): Sign at (274, 250), Cusp at (298, 250)
    assert 'x="274" y="250" font-size="10.5"' in svg
    assert 'x="298" y="250" font-family="sans-serif" font-size="10"' in svg


def test_north_indian_outer_houses_geometry():
    """
    Safeguards the exact geometry of outer triangle houses:
    - Safe border track at 44px
    - Sign glyph (Star) in inner corner (font-size 8.5)
    - Cusp number (Square) radially outward (font-size 8.5)
    """
    items = [
        {"type": "planet", "name": "Mars", "sign": "Taurus", "degree": 10, "minute": 0, "is_retrograde": False},
        {"type": "planet", "name": "Venus", "sign": "Taurus", "degree": 20, "minute": 0, "is_retrograde": False},
        {"type": "cusp", "text": "2", "sign": "Taurus"}
    ]
    # Lagna in Aries -> Taurus is House 2 (Top outer triangle)
    svg = generate_north_indian(items, varga_name="D1")

    # In H2: track is at y=44, running from x=215 (0°) to x=65 (30°)
    mars_x, mars_y = extract_planet_pos(svg, "Mars")
    venus_x, venus_y = extract_planet_pos(svg, "Venus")
    assert mars_x > venus_x, f"H2: lower deg Mars x ({mars_x}) must be > higher deg Venus x ({venus_x})"
    assert abs(mars_y - 42.0) < 0.1 and abs(venus_y - 42.0) < 0.1, "H2 track must be at y=44 (text y=42)"

    # Sign at (140, 120), Cusp at (140, 95)
    assert 'x="140" y="120" font-size="8.5"' in svg
    assert 'x="140" y="95" font-family="sans-serif" font-size="8.5"' in svg


def test_equidistant_spacing_algorithms():
    """Safeguards the equidistant normalized spacing coefficients for both styles."""
    # South Indian: optimal corner utilization
    assert get_equidistant_t(1) == [0.50]
    assert get_equidistant_t(2) == [0.18, 0.82]
    assert get_equidistant_t(3) == [0.10, 0.50, 0.90]
    assert get_equidistant_t(4) == [0.06, 0.35, 0.65, 0.94]

    # North Indian: tighter spacing for 3 & 4 planets
    assert get_north_equidistant_t(1) == [0.50]
    assert get_north_equidistant_t(2) == [0.26, 0.74]
    assert get_north_equidistant_t(3) == [0.20, 0.50, 0.80]
    assert get_north_equidistant_t(4) == [0.12, 0.37, 0.63, 0.88]
