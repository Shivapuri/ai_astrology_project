import pytest
from jyotish.shadbala.shadbala import calculate_drishti_value, calculate_cheshta_bala, calculate_nathonnatha_bala

def test_drishti_value():
    # 180 degrees should be 60
    assert calculate_drishti_value(0, 180) == 60.0
    # 120 degrees should be 30
    assert calculate_drishti_value(0, 120) == 30.0
    # < 30 degrees should be 0
    assert calculate_drishti_value(0, 15) == 0.0
    
def test_nathonnatha_bala():
    # Sun at MC (Midday) gets 60
    assert calculate_nathonnatha_bala("Sun", 90.0, 90.0) == 60.0
    # Moon at IC (Midnight) gets 60
    assert calculate_nathonnatha_bala("Moon", 270.0, 90.0) == 60.0
    # Mercury always 60
    assert calculate_nathonnatha_bala("Mercury", 45.0, 100.0) == 60.0
