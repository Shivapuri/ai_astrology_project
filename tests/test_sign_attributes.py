import pytest
from jyotish.generate_jyotish import generate_kala_chart
from jyotish.sign_attributes import (
    calculate_sign_distributions,
    SIGNS,
    ELEMENT_MAP,
    MOBILITY_MAP,
    POLARITY_MAP,
    RISING_MAP,
    KALAPURUSHA_ANATOMY
)

@pytest.fixture(scope="module")
def aj_chart():
    return generate_kala_chart(
        name="Angelina Jolie",
        year=1975,
        month=6,
        day=4,
        hour=9,
        minute=9,
        latitude=34.0522,
        longitude=-118.2437,
        timezone_offset=-7.0
    )

def test_sign_attributes_angelina_jolie_d1(aj_chart):
    d1 = aj_chart["vargas"]["D1"]
    dist = calculate_sign_distributions(d1, count_lagna=False)
    
    assert dist["total_counted"] == 9
    assert dist["lagna_sign"] == "Cancer"
    
    # Elements
    elem = dist["elements"]
    assert elem["Fire"]["count"] == 4
    assert sorted(elem["Fire"]["grahas"]) == ["Jupiter", "Mars", "Moon", "Rahu"]
    assert elem["Fire"]["has_lagna"] is False
    assert elem["Fire"]["varna"] == "Kshatriya"
    assert elem["Fire"]["dosha"] == "Pitta"
    
    assert elem["Earth"]["count"] == 0
    assert elem["Earth"]["grahas"] == []
    assert elem["Earth"]["varna"] == "Shudra"
    
    assert elem["Air"]["count"] == 3
    assert sorted(elem["Air"]["grahas"]) == ["Ketu", "Mercury", "Sun"]
    assert elem["Air"]["varna"] == "Vaishya"
    assert elem["Air"]["dosha"] == "Vata"
    
    assert elem["Water"]["count"] == 2
    assert sorted(elem["Water"]["grahas"]) == ["Saturn", "Venus"]
    assert elem["Water"]["has_lagna"] is True
    assert elem["Water"]["varna"] == "Brahmin"
    assert elem["Water"]["dosha"] == "Kapha"
    
    # Mobility
    mob = dist["mobility"]
    assert mob["Movable"]["count"] == 5
    assert sorted(mob["Movable"]["grahas"]) == ["Jupiter", "Mars", "Moon", "Saturn", "Venus"]
    assert mob["Movable"]["has_lagna"] is True
    assert mob["Movable"]["sanskrit"] == "Chara"
    
    assert mob["Fixed"]["count"] == 0
    assert mob["Fixed"]["grahas"] == []
    assert mob["Fixed"]["sanskrit"] == "Sthira"
    
    assert mob["Dual"]["count"] == 4
    assert sorted(mob["Dual"]["grahas"]) == ["Ketu", "Mercury", "Rahu", "Sun"]
    assert mob["Dual"]["sanskrit"] == "Dvisvabhava"
    
    # Polarity
    pol = dist["polarity"]
    assert pol["Active"]["count"] == 7  # Fire (4) + Air (3)
    assert pol["Passive"]["count"] == 2  # Earth (0) + Water (2)
    
    # Rising Orientation
    rise = dist["rising"]
    assert rise["Shirshodaya"]["count"] == 3  # Gemini (Sun, Mercury, Ketu)
    assert rise["Prishtodaya"]["count"] == 6   # Aries (Moon, Mars, Jupiter) + Cancer (Venus, Saturn) + Sagittarius (Rahu)
    assert rise["Ubhayodaya"]["count"] == 0
    
    # Varnas
    varna = dist["varnas"]
    assert varna["Kshatriya"]["count"] == 4
    assert varna["Shudra"]["count"] == 0
    assert varna["Vaishya"]["count"] == 3
    assert varna["Brahmin"]["count"] == 2
    
    # Doshas
    dosha = dist["doshas"]
    assert dosha["Pitta"]["count"] == 4
    assert dosha["Vata"]["count"] == 3
    assert dosha["Kapha"]["count"] == 2  # Earth (0) + Water (2)
    
    # Kalapurusha Anatomy
    anatomy = dist["anatomy"]
    assert len(anatomy) == 12
    # Aries: Head & Brain
    assert anatomy[0]["sign"] == "Aries"
    assert anatomy[0]["region"] == "Head & Brain"
    assert anatomy[0]["count"] == 3
    assert sorted(anatomy[0]["grahas"]) == ["Jupiter", "Mars", "Moon"]
    
    # Gemini: Shoulders & Lungs
    assert anatomy[2]["sign"] == "Gemini"
    assert anatomy[2]["count"] == 3
    assert sorted(anatomy[2]["grahas"]) == ["Ketu", "Mercury", "Sun"]
    
    # Cancer: Chest & Stomach
    assert anatomy[3]["sign"] == "Cancer"
    assert anatomy[3]["count"] == 2
    assert sorted(anatomy[3]["grahas"]) == ["Saturn", "Venus"]
    assert anatomy[3]["has_lagna"] is True
    
    # Sagittarius: Hips & Thighs
    assert anatomy[8]["sign"] == "Sagittarius"
    assert anatomy[8]["count"] == 1
    assert anatomy[8]["grahas"] == ["Rahu"]
    
    # Empty regions: Taurus, Leo, Virgo, Libra, Scorpio, Capricorn, Aquarius, Pisces
    for idx in [1, 4, 5, 6, 7, 9, 10, 11]:
        assert anatomy[idx]["count"] == 0
        assert anatomy[idx]["grahas"] == []

def test_sign_attributes_with_lagna_counted(aj_chart):
    d1 = aj_chart["vargas"]["D1"]
    dist = calculate_sign_distributions(d1, count_lagna=True)
    
    assert dist["total_counted"] == 10
    assert dist["elements"]["Water"]["count"] == 3  # 2 grahas + Lagna
    assert dist["mobility"]["Movable"]["count"] == 6 # 5 grahas + Lagna
    assert dist["polarity"]["Passive"]["count"] == 3 # 2 grahas + Lagna

def test_4x3_matrix_integrity(aj_chart):
    d1 = aj_chart["vargas"]["D1"]
    dist = calculate_sign_distributions(d1, count_lagna=False)
    matrix = dist["matrix_4x3"]
    
    assert len(matrix) == 4  # Fire, Earth, Air, Water
    for row in matrix:
        assert len(row["cells"]) == 3  # Movable, Fixed, Dual
        assert row["total_count"] == sum(c["count"] for c in row["cells"])
