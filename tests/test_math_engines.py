import pytest
from jyotish.generate_jyotish import generate_kala_chart, calculate_varga_longitude
from jyotish.avasthas.bala import get_bala_avastha
from jyotish.avasthas.jagrat import get_jagrat_avastha

def test_generate_kala_chart():
    # Test default Swami Shivapuri chart
    chart_data = generate_kala_chart(
        name="Test", year=1983, month=11, day=10, 
        hour=22, minute=20, latitude=52.20296, longitude=8.0448, timezone_offset=1.0
    )
    
    assert chart_data["subject_info"]["name"] == "Test"
    assert "vargas" in chart_data
    assert "D1" in chart_data["vargas"]
    assert "D9" in chart_data["vargas"]
    
    # Check Lagna degree in D1 (Ascendant)
    d1 = chart_data["vargas"]["D1"]
    assert "lagna" in d1
    assert "grahas" in d1
    
    # Ensure all 16 vargas are present
    vargas_list = ["D1", "D2", "D3", "D4", "D7", "D9", "D10", "D12", "D16", "D20", "D24", "D27", "D30", "D40", "D45", "D60"]
    for v in vargas_list:
        assert v in chart_data["vargas"], f"Missing varga {v}"

def test_varga_calculations():
    # Simple calculation checks for uniform vargas
    # 0 to 3.33 degrees in Aries (D1) -> Aries (D9)
    lon_aries = 2.0  # 2 degrees in Aries
    v_lon_d9 = calculate_varga_longitude(lon_aries, "D9")
    assert v_lon_d9 == 18.0  # (2.0 / 3.333) = fraction inside Aries. 2.0 % 3.333 = 2.0. Fraction = 2.0/3.333 = 0.6. 0.6*30 = 18 degrees

def test_baladi_avastha():
    # Odd signs (e.g. Aries) -> 0-6 Bala, 6-12 Kumara, 12-18 Yuva, 18-24 Vriddha, 24-30 Mrita
    assert "Bala" in get_bala_avastha(3.0, "Aries")["state"]
    assert "Yuva" in get_bala_avastha(15.0, "Aries")["state"]
    assert "Mrita" in get_bala_avastha(28.0, "Aries")["state"]
    
    # Even signs (e.g. Taurus) -> Reversed
    assert "Mrita" in get_bala_avastha(3.0, "Taurus")["state"]
    assert "Yuva" in get_bala_avastha(15.0, "Taurus")["state"]
    assert "Bala" in get_bala_avastha(28.0, "Taurus")["state"]

def test_jagradadi_avastha():
    # Exalted/Own = Jagrat
    assert "Jagrat" in get_jagrat_avastha("Exalted")["state"]
    assert "Jagrat" in get_jagrat_avastha("Moolatrikona")["state"]
    assert "Jagrat" in get_jagrat_avastha("Own Sign")["state"]
    # Friend/Neutral = Swapna
    assert "Svapna" in get_jagrat_avastha("Great Friend's Sign")["state"]
    assert "Svapna" in get_jagrat_avastha("Friend's Sign")["state"]
    assert "Svapna" in get_jagrat_avastha("Neutral Sign")["state"]
    # Enemy/Debilitated = Susupti
    assert "Sushupti" in get_jagrat_avastha("Enemy's Sign")["state"]
    assert "Sushupti" in get_jagrat_avastha("Great Enemy's Sign")["state"]
    assert "Sushupti" in get_jagrat_avastha("Debilitated")["state"]
