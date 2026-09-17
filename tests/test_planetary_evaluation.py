"""
Unit and regression tests for Vic DiCara's Planetary Evaluation & Positive-to-Negative Scale.
Validates:
1. Completely independent evaluation engine; zero mutation of existing chart calculations.
2. 4-step diagnostic algorithm: Shadvarga base, Dispositor host rescue, Drishti aspect gradients, House fields.
3. 4-Quadrant archetype classifications (King with Armies, Dictator, Sincere Friend, Bully Behind Bars).
4. The Three Master Lords of Destiny (Lagna Lord, Navamsha Lord, Drekkana Lord - Phaladeepika 3.11).
5. Mathematical audit trail and equation generation.
"""

import pytest
from jyotish.generate_jyotish import generate_kala_chart
from jyotish.planetary_evaluation import calculate_planetary_evaluation

DOB_YEAR = 1975
DOB_MONTH = 6
DOB_DAY = 4
DOB_HOUR = 9
DOB_MINUTE = 9
LAT = 34.0522
LON = -118.2437
TZ = -7.0

@pytest.fixture(scope='module')
def test_chart():
    return generate_kala_chart(
        name='Angelina Jolie',
        year=DOB_YEAR, month=DOB_MONTH, day=DOB_DAY,
        hour=DOB_HOUR, minute=DOB_MINUTE,
        latitude=LAT, longitude=LON, timezone_offset=TZ
    )

def test_planetary_evaluation_presence(test_chart):
    """Verify that planetary_evaluation key is generated and populated."""
    assert "planetary_evaluation" in test_chart
    eval_data = test_chart["planetary_evaluation"]
    assert "summary" in eval_data
    assert "planets" in eval_data

def test_master_lords_destiny(test_chart):
    """Verify that the Three Master Lords (Phaladeepika 3.11) are accurately resolved."""
    eval_data = test_chart["planetary_evaluation"]
    master_lords = eval_data["summary"]["master_lords"]
    
    assert "lagna_lord" in master_lords
    assert "navamsha_lord" in master_lords
    assert "drekkana_lord" in master_lords
    
    for k in ["lagna_lord", "navamsha_lord", "drekkana_lord"]:
        lord_info = master_lords[k]
        assert "planet" in lord_info
        assert "scale_score" in lord_info
        assert "expression_mode" in lord_info
        assert "governs" in lord_info
        assert -100.0 <= lord_info["scale_score"] <= 100.0

def test_planets_structure_and_bounds(test_chart):
    """Verify all 7 classical grahas (+ nodes) have complete evaluation and bounded scores."""
    eval_data = test_chart["planetary_evaluation"]
    planets = eval_data["planets"]
    
    expected_grahas = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
    for p in expected_grahas:
        assert p in planets, f"Missing planet {p} in planetary evaluation"
        p_data = planets[p]
        
        # Scale score bounded [-100.0, 100.0]
        score = p_data["net_scale_score"]
        assert -100.0 <= score <= 100.0
        
        # Expression mode consistent with score
        mode = p_data["expression_mode"]
        if score > 30.0:
            assert "High Expression" in mode
        elif score < -30.0:
            assert "Low Expression" in mode
        else:
            assert "Mixed Expression" in mode
            
        # 4-Quadrant Archetype
        archetype = p_data["archetype"]
        assert archetype["title"] in [
            "Generous King with Armies",
            "Ruthless Armed Dictator",
            "Sincere Friend with No Money",
            "Toothless Bully Behind Bars"
        ]
        assert archetype["icon"] in ["🌟", "💣", "🕊️", "🪰"]
        
        # Step 1 Shadvarga Breakdown
        s1 = p_data["step1_shadvarga"]
        assert 0.0 <= s1["average_dignity_pct"] <= 100.0
        assert -100.0 <= s1["base_centered_score"] <= 100.0
        assert len(s1["varga_breakdown"]) == 6
        for v in ["D1", "D2", "D3", "D9", "D12", "D30"]:
            assert v in s1["varga_breakdown"]
            assert "score" in s1["varga_breakdown"][v]
            
        # Step 2 Host Rescue
        s2 = p_data["step2_host_rescue"]
        assert "host_planet" in s2
        assert "rescue_status" in s2
        assert "bonus_pct" in s2
        
        # Step 3 Aspects
        s3 = p_data["step3_aspects"]
        assert "benefic_rays_pct" in s3
        assert "malefic_pressure_pct" in s3
        assert "net_aspect_pct" in s3
        assert -40.0 <= s3["net_aspect_pct"] <= 40.0
        
        # Step 4 House Field
        s4 = p_data["step4_house_field"]
        assert 1 <= s4["house_num"] <= 12
        assert "house_type" in s4
        assert "bonus_pct" in s4
        
        # Calculation Audit Trail
        trail = p_data["calculation_trail"]
        assert "formula" in trail
        assert "equation_parts" in trail
        assert len(trail["equation_parts"]) == 4
        assert "clamped_result" in trail
        assert trail["clamped_result"] == score
        assert "human_readable" in trail

def test_calculation_independence(test_chart):
    """Verify that adding planetary_evaluation did NOT alter any existing Kala computations."""
    # Shadbala remains intact
    assert "shadbala" in test_chart
    assert "Sun" in test_chart["shadbala"]
    assert "Total_Virupas" in test_chart["shadbala"]["Sun"]
    
    # Vimshopaka remains intact
    assert "vimshopaka" in test_chart
    assert "Shadvarga" in test_chart["vimshopaka"]["scores"]
    
    # Ashtakavarga remains intact
    assert "ashtakavarga" in test_chart
    assert "sarvashtakavarga" in test_chart["ashtakavarga"]
    
    # Vargas remain intact
    assert "D1" in test_chart["vargas"]
    assert "D9" in test_chart["vargas"]

def test_dayalpuri_jupiter_exalted_archetype():
    """Verify that an exalted planet with high strength (like Dayalpuri's Jupiter in Cancer)
    is recognized as High Dignity (Generous King with Armies), and NOT misclassified as a
    Ruthless Dictator due to 8th house placement or aspect penalties."""
    chart = generate_kala_chart(
        name="Swami Dayalpuri",
        year=1967, month=1, day=24, hour=4, minute=23,
        latitude=47.49835, longitude=19.04045, timezone_offset=1.0
    )
    jup = chart["planetary_evaluation"]["planets"]["Jupiter"]
    
    # In D1, Jupiter is Exalted in Cancer
    assert jup["step1_shadvarga"]["varga_breakdown"]["D1"]["dignity"] == "Exalted"
    assert jup["step1_shadvarga"]["varga_breakdown"]["D1"]["score"] == 100.0
    
    # Inherent Dignity is High Dignity
    assert "High Dignity" in jup["archetype"]["dignity_status"]
    assert jup["archetype"]["strength_status"] == "High Strength"
    
    # Must be Generous King with Armies, NOT Ruthless Armed Dictator
    assert jup["archetype"]["title"] == "Generous King with Armies"
    assert jup["archetype"]["icon"] == "🌟"
    
    # Located in 8th house, so its final situational score is Mixed Expression
    assert jup["step4_house_field"]["house_num"] == 8
    assert jup["expression_class"] == "mixed"
    assert -30.0 <= jup["net_scale_score"] <= 30.0


def test_kurczak_dignity_scale_and_moolatrikona():
    """Verify Kurczak 12.5% step scale, odd/even sign polarity, and Moolatrikona degree bounds."""
    from jyotish.planetary_evaluation.planetary_evaluation import get_dignity_score
    
    assert get_dignity_score("Exalted") == 100.0
    assert get_dignity_score("Great Friend") == 60.0
    assert get_dignity_score("Friend") == 50.0
    assert get_dignity_score("Neutral") == 37.5
    assert get_dignity_score("Enemy") == 25.0
    assert get_dignity_score("Great Enemy") == 20.0
    assert get_dignity_score("Debilitated") == 12.5

    # Own Sign Polarity: Odd sign = 75.0%, Even sign = 62.5%
    assert get_dignity_score("Own Sign", planet="Mars", sign="Aries") == 75.0
    assert get_dignity_score("Own Sign", planet="Mars", sign="Scorpio") == 62.5

    # Moolatrikona degree ranges:
    # Mars MT in Aries 0°-12° -> 87.5%; beyond 12° -> Own positive sign 75.0%
    assert get_dignity_score("Moolatrikona", planet="Mars", sign="Aries", degree=5.0) == 87.5
    assert get_dignity_score("Moolatrikona", planet="Mars", sign="Aries", degree=18.0) == 75.0


def test_nine_tier_archetype_matrix():
    """Verify the 9-tier (+ Transmuted Hero) archetypal spectrum."""
    from jyotish.planetary_evaluation.planetary_evaluation import classify_graha_archetype

    # 1. High Dignity Tiers
    king = classify_graha_archetype(dignity_pct=85.0, shadbala_pct=120.0)
    assert king["archetype"] == "The Generous King"

    guardian = classify_graha_archetype(dignity_pct=85.0, shadbala_pct=95.0)
    assert guardian["archetype"] == "The Noble Guardian"

    friend = classify_graha_archetype(dignity_pct=85.0, shadbala_pct=75.0)
    assert friend["archetype"] == "The Sincere Friend"

    # 2. Neutral Dignity Tiers
    exec_archetype = classify_graha_archetype(dignity_pct=45.0, shadbala_pct=120.0)
    assert exec_archetype["archetype"] == "The Pragmatic Executive"

    realist = classify_graha_archetype(dignity_pct=45.0, shadbala_pct=95.0)
    assert realist["archetype"] == "The Dutiful Realist"

    citizen = classify_graha_archetype(dignity_pct=45.0, shadbala_pct=75.0)
    assert citizen["archetype"] == "The Modest Citizen"

    # 3. Low Dignity Tiers
    dictator = classify_graha_archetype(dignity_pct=25.0, shadbala_pct=120.0)
    assert dictator["archetype"] == "The Armed Dictator"

    striver = classify_graha_archetype(dignity_pct=25.0, shadbala_pct=95.0)
    assert striver["archetype"] == "The Embattled Striver"

    bully = classify_graha_archetype(dignity_pct=25.0, shadbala_pct=75.0)
    assert bully["archetype"] == "The Toothless Bully"

    # 4. Transmuted Hero (Strict Neecha Bhanga)
    hero = classify_graha_archetype(dignity_pct=25.0, shadbala_pct=120.0, is_neecha_bhanga=True)
    assert hero["archetype"] == "The Transmuted Hero"


def test_shivapuri_and_hariompuri_diagnostic_validations():
    """Verify Shivapuri Baba, Swami Hari Om Puri, and Adolf Hitler diagnostic outcomes."""
    from jyotish.planetary_evaluation.planetary_evaluation import calculate_graha_vitality

    # Shivapuri Baba Mars in Virgo: Neutral sign, high Shadbala (120%), Moon + Jupiter aspect, Mudita
    shiv_mars = calculate_graha_vitality(
        planet="Mars", sign="Virgo", degree_in_sign=15.0,
        dignity_name="Neutral", dignity_pct=37.5,
        host_planet="Mercury", host_dignity_pct=60.0, host_shadbala_pct=105.0,
        planet_shadbala_pct=120.0, net_drishti_virupas=41.0,
        conjunctions=[], lajjitadi_states=["Mudita"],
        is_retrograde=False, is_combust=False, is_node=False,
        lagna_sign="Leo", lagna_lord="Sun"
    )
    assert shiv_mars["quadrant"]["archetype"] == "The Pragmatic Executive"
    assert shiv_mars["vitality_score"] >= 7.0

    # Swami Hari Om Puri Mars in Virgo: Great Enemy, conjunct Ketu, conjunct Sun
    puri_mars = calculate_graha_vitality(
        planet="Mars", sign="Virgo", degree_in_sign=10.0,
        dignity_name="Great Enemy", dignity_pct=20.0,
        host_planet="Mercury", host_dignity_pct=60.0, host_shadbala_pct=100.0,
        planet_shadbala_pct=90.0, net_drishti_virupas=-15.0,
        conjunctions=["Sun", "Ketu"], lajjitadi_states=["Kshobhita"],
        is_retrograde=False, is_combust=False, is_node=False,
        lagna_sign="Sagittarius", lagna_lord="Jupiter"
    )
    # Virgo is NOT Cancer, so Neecha Bhanga must NOT be granted!
    assert not puri_mars["is_neecha_bhanga"]
    assert puri_mars["quadrant"]["archetype"] == "The Embattled Striver"
    assert puri_mars["vitality_score"] < 5.0

    # Adolf Hitler Mars in Taurus: Enemy sign, combust Sun, high Shadbala (120%), harsh pressure
    hitler_mars = calculate_graha_vitality(
        planet="Mars", sign="Taurus", degree_in_sign=24.0,
        dignity_name="Enemy", dignity_pct=25.0,
        host_planet="Venus", host_dignity_pct=25.0, host_shadbala_pct=95.0,
        planet_shadbala_pct=120.0, net_drishti_virupas=-20.0,
        conjunctions=["Sun", "Venus"], lajjitadi_states=["Kshobhita"],
        is_retrograde=False, is_combust=True, is_node=False,
        lagna_sign="Libra", lagna_lord="Venus"
    )
    assert hitler_mars["quadrant"]["archetype"] == "The Armed Dictator"
    assert hitler_mars["vitality_score"] <= 3.5

