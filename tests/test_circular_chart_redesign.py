import pytest
from jyotish.draw_chart import generate_circular_chart, generate_biwheel_chart

SAMPLE_ITEMS = [
    {"type": "planet", "name": "Lagna", "sign": "Leo", "degree": 9, "minute": 35, "is_retrograde": False},
    {"type": "planet", "name": "Sun", "sign": "Scorpio", "degree": 17, "minute": 54, "is_retrograde": False},
    {"type": "planet", "name": "Moon", "sign": "Aquarius", "degree": 28, "minute": 34, "is_retrograde": False},
    {"type": "planet", "name": "Mars", "sign": "Virgo", "degree": 25, "minute": 31, "is_retrograde": False},
    {"type": "planet", "name": "Mercury", "sign": "Scorpio", "degree": 24, "minute": 35, "is_retrograde": False},
    {"type": "planet", "name": "Jupiter", "sign": "Sagittarius", "degree": 14, "minute": 28, "is_retrograde": False},
    {"type": "planet", "name": "Venus", "sign": "Virgo", "degree": 1, "minute": 29, "is_retrograde": False},
    {"type": "planet", "name": "Saturn", "sign": "Scorpio", "degree": 8, "minute": 30, "is_retrograde": False},
    {"type": "planet", "name": "Rahu", "sign": "Gemini", "degree": 16, "minute": 13, "is_retrograde": True},
    {"type": "planet", "name": "Ketu", "sign": "Sagittarius", "degree": 16, "minute": 13, "is_retrograde": True},
    {"type": "cusp", "text": "1", "sign": "Leo", "degree": 9, "minute": 35},
    {"type": "cusp", "text": "2", "sign": "Virgo", "degree": 3, "minute": 20},
    {"type": "cusp", "text": "3", "sign": "Virgo", "degree": 29, "minute": 40},
    {"type": "cusp", "text": "4", "sign": "Libra", "degree": 28, "minute": 58},
    {"type": "cusp", "text": "5", "sign": "Scorpio", "degree": 29, "minute": 15},
    {"type": "cusp", "text": "6", "sign": "Sagittarius", "degree": 1, "minute": 5},
    {"type": "cusp", "text": "7", "sign": "Aquarius", "degree": 9, "minute": 35},
    {"type": "cusp", "text": "8", "sign": "Pisces", "degree": 3, "minute": 20},
    {"type": "cusp", "text": "9", "sign": "Pisces", "degree": 29, "minute": 40},
    {"type": "cusp", "text": "10", "sign": "Aries", "degree": 18, "minute": 58},
    {"type": "cusp", "text": "11", "sign": "Taurus", "degree": 29, "minute": 15},
    {"type": "cusp", "text": "12", "sign": "Gemini", "degree": 1, "minute": 5}
]

def test_circular_chart_whole_sign_houses_and_radii():
    svg = generate_circular_chart(SAMPLE_ITEMS, mode="symbol", varga_name="D1", ayanamsha=19.33, root_planet="Lagna")
    
    # 1. Inner radius geometry: widened inner ring & flatter house ring (r_inner=56, r_outer=72)
    assert '<circle class="interactive-center-circle" cx="0" cy="0" r="56"' in svg
    assert '<circle cx="0" cy="0" r="72"' in svg
    
    # 2. Crisp unshaded canvas: no colored Kendra/Trikona background fills
    assert 'class="house-bg house-kendra"' not in svg
    assert 'class="house-bg house-trikona"' not in svg
    assert 'class="house-bg house-other"' not in svg
    
    # 3. Exactly 12 equal 30° Whole Sign Houses with green fine dotted boundary lines
    for h in range(1, 13):
        assert f'class="whole-sign-cusp" data-house="{h}"' in svg
        assert f'class="house-divider" data-house="{h}"' in svg
        assert f'class="interactive house-num" data-type="house" data-id="{h}"' in svg
        assert 'stroke-dasharray="1,2.5"' in svg

def test_circular_chart_inward_planet_ticks():
    svg = generate_circular_chart(SAMPLE_ITEMS, mode="symbol", varga_name="D1", ayanamsha=19.33, root_planet="Lagna", show_inner_ticks=True)
    
    # Inward planet ticks must exist and point inward into center aspect hub
    assert '<g class="inner-planet-ticks">' in svg
    assert 'class="inner-tick" data-planet="Mars"' in svg
    assert 'class="inner-tick" data-planet="Jupiter"' in svg
    assert 'class="inner-tick" data-planet="Venus"' in svg
    assert 'class="inner-tick" data-planet="Saturn"' in svg
    assert 'class="inner-tick" data-planet="Sun"' in svg
    assert 'class="inner-tick" data-planet="Moon"' in svg
    assert 'class="inner-tick" data-planet="Lagna"' in svg

def test_circular_chart_single_ac_badge_and_no_duplicate_asc():
    svg = generate_circular_chart(SAMPLE_ITEMS, mode="symbol", varga_name="D1", ayanamsha=19.33, root_planet="Lagna")
    
    # Single clean AC badge and degree readout along horizontal 180° spoke
    assert 'class="angle-ac-badge"' in svg
    assert '>AC</text>' in svg
    assert '9° 35\'' in svg
    
    # Ascendant glyph not duplicated in planetary stack
    assert 'data-id="Lagna"' not in svg

def test_circular_chart_campanus_cusps_toggle():
    # When ON (default)
    svg_on = generate_circular_chart(SAMPLE_ITEMS, mode="symbol", varga_name="D1", ayanamsha=19.33, root_planet="Lagna", show_campanus_cusps=True)
    assert 'class="angle-line angle-mc"' in svg_on
    assert 'class="angle-mc-badge"' in svg_on
    assert 'class="angle-line angle-dc"' in svg_on
    assert 'class="angle-line angle-ic"' in svg_on
    assert 'class="interactive cusp-number"' in svg_on

    # When OFF: intermediate Campanus numbers hidden, but cardinal angles (AC, DC, MC, IC) remain present without obstructing
    svg_off = generate_circular_chart(SAMPLE_ITEMS, mode="symbol", varga_name="D1", ayanamsha=19.33, root_planet="Lagna", show_campanus_cusps=False)
    assert 'class="interactive cusp-number"' not in svg_off
    assert 'class="angle-line angle-mc"' in svg_off
    assert 'class="angle-mc-badge"' in svg_off
    assert 'class="angle-line angle-dc"' in svg_off
    assert 'class="angle-line angle-ic"' in svg_off
    assert 'class="angle-ac-badge"' in svg_off
    assert 'class="whole-sign-cusp" data-house="1"' in svg_off

def test_circular_chart_radial_sightlines_and_shields():
    svg = generate_circular_chart(SAMPLE_ITEMS, mode="symbol", varga_name="D1", ayanamsha=19.33, root_planet="Lagna", show_sightlines=True)
    
    # Radial sightlines present
    assert 'class="planetary-sightlines"' in svg
    assert 'class="radial-sightline ray-inner" data-planet="Mars"' in svg
    assert 'class="radial-sightline ray-outer" data-planet="Mars"' in svg
    assert 'class="outer-alignment-dot" data-planet="Mars"' in svg
    
    # Text shielding present on text elements
    assert 'class="interactive text-shield"' in svg
    assert 'class="interactive sign-shield"' in svg

def test_biwheel_inner_chart_redesign():
    svg_bi = generate_biwheel_chart(SAMPLE_ITEMS, SAMPLE_ITEMS, inner_name="D1", outer_name="D9", mode="symbol", ayanamsha=19.33, root_planet="Lagna")
    
    # Inner chart has clean unshaded canvas (no colored Kendra/Trikona fills)
    assert 'class="house-bg house-kendra"' not in svg_bi
    assert 'class="house-bg house-trikona"' not in svg_bi
    assert '<path class="house-bg"' in svg_bi
    assert 'fill="none"' in svg_bi
    
    # Inward planet ticks pointing inward into aspect hub
    assert '<g class="inner-planet-ticks">' in svg_bi
    assert 'class="inner-tick" data-planet="Sun"' in svg_bi
    assert 'class="inner-tick" data-planet="Moon"' in svg_bi
    assert 'class="inner-tick" data-planet="Mars"' in svg_bi
    assert 'class="inner-tick" data-planet="Lagna"' in svg_bi

    # Ascendant uses identical AC text without box and no inner D1 Lagna duplicate glyph
    assert 'class="angle-ac-badge"' in svg_bi
    assert '>AC</text>' in svg_bi
    assert 'data-varga="D1" data-id="Lagna"' not in svg_bi

    # Natal aspects present inside aspect circle
    assert '<g class="aspect-lines">' in svg_bi
    assert 'class="interactive-aspect"' in svg_bi
    # Aspects are strictly natal (inner D1 to inner D1)
    aspect_block = svg_bi.split('<g class="aspect-lines">')[1].split('</g>')[0]
    assert 'data-varga="D9"' not in aspect_block

    # Harmonic outer sign separation lines do NOT shoot diagonally (fixed y2=y_out2 typo)
    import re
    # Check that outer dividers have proper polar coordinates and no y2==x2 runaway lines
    outer_divider_lines = re.findall(r'<line x1=\"([^\"]+)\" y1=\"([^\"]+)\" x2=\"([^\"]+)\" y2=\"([^\"]+)\" stroke=\"#d5c8b2\"', svg_bi)
    assert len(outer_divider_lines) == 12
    for x1, y1, x2, y2 in outer_divider_lines:
        r2 = (float(x2)**2 + float(y2)**2)**0.5
        assert 205.0 <= r2 <= 207.0, f"Outer sign divider radius {r2} not on outer rim"
