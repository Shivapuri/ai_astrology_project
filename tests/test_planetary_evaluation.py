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


def test_detect_planetary_wars():
    """Verify Graha Yuddha (Phaladeepika 4.2 & BPHS) mechanics:
    1. Venus Invariance Rule (Venus never loses).
    2. Northern Celestial Latitude Victor determination.
    3. Shadbala fallback when latitudes are identical/unavailable.
    4. Exempt bodies (Sun, Moon, Rahu, Ketu do not engage in war).
    5. Orb threshold (<= 1°00').
    """
    from jyotish.planetary_evaluation.planetary_evaluation import detect_planetary_wars

    # 1. Venus vs Mars within 0°15' in Taurus (Hitler's configuration)
    hitler_grahas = {
        "Mars": {"sign": "Taurus", "degree_0_to_30": 24.10, "latitude": -0.50},
        "Venus": {"sign": "Taurus", "degree_0_to_30": 24.35, "latitude": +1.20},
        "Sun": {"sign": "Taurus", "degree_0_to_30": 24.20} # Sun combusts, does NOT fight
    }
    wars = detect_planetary_wars(hitler_grahas)
    assert "Venus" in wars
    assert "Mars" in wars
    assert "Sun" not in wars # Sun is exempt

    venus_war = wars["Venus"]
    mars_war = wars["Mars"]

    assert venus_war["is_winner"]
    assert not venus_war["is_loser"]
    assert venus_war["opponent"] == "Mars"
    assert venus_war["war_mod"] == 0.30
    assert "🏆 War Victor (Combat Stain: Mars)" in venus_war["badge"]

    assert mars_war["is_loser"]
    assert not mars_war["is_winner"]
    assert mars_war["opponent"] == "Venus"
    assert mars_war["war_mod"] == -0.60
    assert "⚔️ Nipidita (War Defeat via Venus)" in mars_war["badge"]

    # 2. Mars vs Saturn: Northern celestial latitude wins
    grahas_lat = {
        "Mars": {"sign": "Capricorn", "degree_0_to_30": 10.20, "latitude": +1.80},
        "Saturn": {"sign": "Capricorn", "degree_0_to_30": 10.70, "latitude": -1.20}
    }
    wars_lat = detect_planetary_wars(grahas_lat)
    assert wars_lat["Mars"]["is_winner"]
    assert wars_lat["Saturn"]["is_loser"]
    assert "Northern Celestial Latitude" in wars_lat["Mars"]["reason"]

    # 3. Different signs or wide orb (> 1°00') -> No war
    grahas_peace = {
        "Mars": {"sign": "Aries", "degree_0_to_30": 10.0},
        "Saturn": {"sign": "Aries", "degree_0_to_30": 11.5} # 1.5° apart
    }
    assert detect_planetary_wars(grahas_peace) == {}


def test_option_a_recursive_drishti_dampening():
    """Verify Option A: Debilitated benefic aspects (Jupiter/Venus) are dampened by 50%
    in positive virūpas and flagged with a distinctive warning badge."""
    from jyotish.planetary_evaluation.planetary_evaluation import calculate_graha_vitality

    # Case 1: Healthy Jupiter (Exalted, 100%) aspecting with +30 virūpas
    healthy_asp = [{
        "from_planet": "Jupiter",
        "virupas": 30.0,
        "from_dignity_pct": 100.0,
        "from_dignity_name": "Exalted",
        "is_debilitated": False
    }]
    vit_healthy = calculate_graha_vitality(
        planet="Mars", sign="Aries", degree_in_sign=15.0,
        dignity_name="Own Sign", dignity_pct=75.0,
        host_planet="Mars", host_dignity_pct=75.0, host_shadbala_pct=100.0,
        planet_shadbala_pct=100.0, aspect_details=healthy_asp
    )
    assert not vit_healthy["aspect_details"][0]["is_distorted"]
    assert vit_healthy["aspect_details"][0]["adjusted_virupas"] == 30.0

    # Case 2: Debilitated Jupiter (Capricorn, 12.5%) aspecting with +30 virūpas (Option A)
    debilitated_asp = [{
        "from_planet": "Jupiter",
        "virupas": 30.0,
        "from_dignity_pct": 12.5,
        "from_dignity_name": "Debilitated",
        "is_debilitated": True
    }]
    vit_debilitated = calculate_graha_vitality(
        planet="Mars", sign="Aries", degree_in_sign=15.0,
        dignity_name="Own Sign", dignity_pct=75.0,
        host_planet="Mars", host_dignity_pct=75.0, host_shadbala_pct=100.0,
        planet_shadbala_pct=100.0, aspect_details=debilitated_asp
    )
    asp_res = vit_debilitated["aspect_details"][0]
    assert asp_res["is_distorted"]
    # Positive virūpas must be dampened by exactly 50%: 30.0 -> 15.0
    assert asp_res["adjusted_virupas"] == 15.0
    assert "⚠️ Compromised Guidance / Dogmatic Light" in asp_res["badge"]
    # Environmental modifier should be lower for distorted benefic light
    assert vit_debilitated["env_mod"] < vit_healthy["env_mod"]


def test_conjunction_dynamics_and_nodal_possession():
    """Verify conjunction orbs, commanding precedence by Shadbala, and intimate nodal possession."""
    from jyotish.planetary_evaluation.planetary_evaluation import calculate_graha_vitality

    # 1. Ketu intimate conjunction (within 3°20' / one Navamsha):
    # Suppresses outward expression: efficiency *= 0.80, node_mod = -0.25
    ketu_conj = [{
        "planet": "Ketu",
        "degree_diff": 1.5,
        "shadbala_pct": 90.0
    }]
    vit_ketu = calculate_graha_vitality(
        planet="Sun", sign="Leo", degree_in_sign=15.0,
        dignity_name="Own Sign", dignity_pct=75.0,
        host_planet="Sun", host_dignity_pct=75.0, host_shadbala_pct=110.0,
        planet_shadbala_pct=110.0, conjunction_details=ketu_conj
    )
    assert vit_ketu["conjunction_details"][0]["orb_band"] == "Exact (Intimate)"
    assert vit_ketu["node_mod"] == -0.25

    # 2. Conjunction Precedence: higher Shadbala planet commands
    saturn_conj = [{
        "planet": "Saturn",
        "degree_diff": 5.0,
        "shadbala_pct": 130.0 # Saturn has higher Shadbala than Sun (100.0)
    }]
    vit_prec = calculate_graha_vitality(
        planet="Sun", sign="Leo", degree_in_sign=15.0,
        dignity_name="Own Sign", dignity_pct=75.0,
        host_planet="Sun", host_dignity_pct=75.0, host_shadbala_pct=100.0,
        planet_shadbala_pct=100.0, conjunction_details=saturn_conj
    )
    assert vit_prec["conjunction_details"][0]["commands"] is True


def test_himmler_jupiter_evaluation_and_chandal_badges():
    """Verify Heinrich Himmler's Jupiter configuration:
    - Aquarius Lagna -> Jupiter rules 11th (Trishadāya) and 2nd -> Functional Malefic.
    - Moolatrikona Sagittarius with High Shadbala (112%).
    - Conjoined Rahu (within 4.9°) -> Guru-Chāṇḍāla Yoga.
    - Conjoined Saturn & Rahu (2 cruel malefics) -> Vikala Avasthā.
    - High horsepower preserved (~7.0 / 10 Capable) with prominent warning badges and 'Ideological Mobilizer' archetype.
    """
    from jyotish.planetary_evaluation.planetary_evaluation import calculate_graha_vitality

    fn_role = {
        "status": "Functional Malefic",
        "badge": "⚡ Functional Malefic (Trishadāya)",
        "is_trishadaya": True,
        "houses_ruled": [2, 11]
    }
    jup_conj = [
        {"planet": "Rahu", "degree_diff": 4.87, "shadbala_pct": 100.0},
        {"planet": "Saturn", "degree_diff": 21.64, "shadbala_pct": 105.0}
    ]

    vit_jup = calculate_graha_vitality(
        planet="Jupiter", sign="Sagittarius", degree_in_sign=7.77,
        dignity_name="Moolatrikona", dignity_pct=87.5,
        host_planet="Jupiter", host_dignity_pct=87.5, host_shadbala_pct=112.0,
        planet_shadbala_pct=112.0, net_drishti_virupas=0.0,
        conjunctions=["Rahu", "Saturn"], conjunction_details=jup_conj,
        functional_role=fn_role,
        lagna_sign="Aquarius", lagna_lord="Saturn"
    )

    # 1. Guru-Chandal and Vikala flags
    assert vit_jup["is_guru_chandal"] is True, "Must identify Guru-Chāṇḍāla Yoga"
    assert vit_jup["is_guru_ketu"] is False
    assert vit_jup["is_vikala"] is True, "Must identify Vikala Avasthā (2 cruel malefics)"

    # 2. Affliction badges
    badges = vit_jup["affliction_badges"]
    assert any("Guru-Chāṇḍāla" in b for b in badges), "Must include Guru-Chāṇḍāla badge"
    assert any("Vikala" in b for b in badges), "Must include Vikala badge"

    # 3. High horsepower maintained (~7.0 - 7.9 / 10 Capable)
    assert 7.0 <= vit_jup["vitality_score"] <= 8.0, f"Expected ~7.0-8.0, got {vit_jup['vitality_score']}"
    assert "Capable" in vit_jup["vitality_tier"]

    # 4. Archetype re-calibrated from innocent King to Ideological Mobilizer
    archetype_title = vit_jup["quadrant"]["archetype"]
    assert "Ideological Mobilizer" in archetype_title, f"Archetype should be Ideological Mobilizer, got {archetype_title}"
    assert vit_jup["functional_role"]["status"] == "Functional Malefic"


def test_guru_ketu_jnana_badge_evaluation():
    """Verify Jupiter + Ketu conjunction produces pure spiritual contemplation (Jñāna Catalyst)
    without toxic Chāṇḍāla stigma."""
    from jyotish.planetary_evaluation.planetary_evaluation import calculate_graha_vitality

    fn_role = {
        "status": "Functional Benefic",
        "badge": "✨ Functional Benefic (Kona Lord)",
        "is_trishadaya": False,
        "houses_ruled": [1, 4]
    }
    jup_conj = [
        {"planet": "Ketu", "degree_diff": 2.0, "shadbala_pct": 95.0}
    ]

    vit_jup = calculate_graha_vitality(
        planet="Jupiter", sign="Pisces", degree_in_sign=15.0,
        dignity_name="Own Sign", dignity_pct=75.0,
        host_planet="Jupiter", host_dignity_pct=75.0, host_shadbala_pct=100.0,
        planet_shadbala_pct=100.0,
        conjunctions=["Ketu"], conjunction_details=jup_conj,
        functional_role=fn_role,
        lagna_sign="Sagittarius", lagna_lord="Jupiter"
    )

    assert vit_jup["is_guru_ketu"] is True
    assert vit_jup["is_guru_chandal"] is False
    assert any("Jñāna Catalyst" in b for b in vit_jup["affliction_badges"])
    assert "Ideological Mobilizer" not in vit_jup["quadrant"]["archetype"]
    assert vit_jup["vitality_score"] >= 7.0


def test_full_chart_functional_role_pipeline(test_chart):
    """Verify that calculate_planetary_evaluation attaches functional_role, vitality_score,
    and affliction flags to all planets in a real chart."""
    eval_data = test_chart["planetary_evaluation"]
    planets = eval_data["planets"]

    for p_name, p_data in planets.items():
        assert "functional_role" in p_data, f"Missing functional_role on {p_name}"
        assert "vitality_score" in p_data, f"Missing vitality_score on {p_name}"
        assert "vitality_tier" in p_data, f"Missing vitality_tier on {p_name}"
        assert "is_guru_chandal" in p_data, f"Missing is_guru_chandal on {p_name}"
        assert "is_guru_ketu" in p_data, f"Missing is_guru_ketu on {p_name}"
        assert "is_vikala" in p_data, f"Missing is_vikala on {p_name}"
        assert "deepthaadi" in p_data, f"Missing deepthaadi on {p_name}"
        assert "jagradaadi" in p_data, f"Missing jagradaadi on {p_name}"
        assert "calibrated_lajjitadi" in p_data, f"Missing calibrated_lajjitadi on {p_name}"
        assert "psychological_narrative" in p_data, f"Missing psychological_narrative on {p_name}"
        assert 1.0 <= p_data["vitality_score"] <= 10.0


def test_deepthaadi_avastha_9_canonical_states():
    """Verify all 9 canonical Saravali / Vol 2 Ch. 4 Deepthaadi states."""
    from jyotish.planetary_evaluation import calculate_deepthaadi_avastha

    # 1. Nipeedita (War Defeat)
    d1 = calculate_deepthaadi_avastha("Mars", "Capricorn", "Exalted", is_war_loser=True, war_opponent="Saturn")
    assert d1["sanskrit"] == "Nipeedita"
    assert "Nipeedita" in d1["badge"]

    # 2. Vikala (Combustion)
    d2 = calculate_deepthaadi_avastha("Venus", "Pisces", "Exalted", is_combust=True)
    assert d2["sanskrit"] == "Vikala"
    assert "Vikala" in d2["badge"]

    # 3. Bhita (Fall / Debilitation)
    d3 = calculate_deepthaadi_avastha("Sun", "Libra", "Debilitated")
    assert d3["sanskrit"] == "Bhita"
    assert "Bhita" in d3["badge"]

    # 4. Deeptha (Exalted)
    d4 = calculate_deepthaadi_avastha("Sun", "Aries", "Exalted")
    assert d4["sanskrit"] == "Deeptha"
    assert "Deeptha" in d4["badge"]

    # 5. Swastha (Own / Moolatrikona)
    d5 = calculate_deepthaadi_avastha("Mars", "Aries", "Own Sign")
    assert d5["sanskrit"] == "Swastha"
    assert "Swastha" in d5["badge"]

    # 6. Sakta (Retrograde)
    d6 = calculate_deepthaadi_avastha("Jupiter", "Taurus", "Enemy's Sign", is_retrograde=True)
    assert d6["sanskrit"] == "Sakta"
    assert "Sakta" in d6["badge"]

    # 7. Pramudita (Friend's Sign - BPHS 45.7)
    d7 = calculate_deepthaadi_avastha("Sun", "Scorpio", "Friend's Sign")
    assert d7["sanskrit"] == "Pramudita"
    assert "Pramudita" in d7["badge"]

    # 8. Khala (Enemy's Sign)
    d8 = calculate_deepthaadi_avastha("Saturn", "Scorpio", "Enemy's Sign")
    assert d8["sanskrit"] == "Khala"
    assert "Khala" in d8["badge"]

    # 9. Santa (Neutral Sign)
    d9 = calculate_deepthaadi_avastha("Mercury", "Aries", "Neutral's Sign")
    assert d9["sanskrit"] == "Santa"
    assert "Santa" in d9["badge"]


def test_jagradaadi_avastha_capacities():
    """Verify Jagradaadi Avastha 3 states (Jagrat, Svapna, Sushupti) per Vol 2 Ch. 10."""
    from jyotish.planetary_evaluation import calculate_jagradaadi_avastha

    # Jagrat: Exalted / Own / Moolatrikona -> 1.00 (100%)
    j_exalt = calculate_jagradaadi_avastha("Jupiter", "Cancer", "Exalted")
    assert j_exalt["multiplier"] == 1.00
    assert j_exalt["capacity_pct"] == 100
    assert "Jagrat" in j_exalt["state"]

    # Svapna: Friend / Neutral -> 0.50 (50%)
    j_friend = calculate_jagradaadi_avastha("Sun", "Scorpio", "Friend's Sign")
    assert j_friend["multiplier"] == 0.50
    assert j_friend["capacity_pct"] == 50
    assert "Svapna" in j_friend["state"]

    # Sushupti: Enemy / Debilitated -> 0.10 (10%)
    j_enemy = calculate_jagradaadi_avastha("Saturn", "Scorpio", "Enemy's Sign")
    assert j_enemy["multiplier"] == 0.10
    assert j_enemy["capacity_pct"] == 10
    assert "Sushupti" in j_enemy["state"]


def test_lajjitadi_alertness_calibration():
    """Verify that interacting planet alertness governs Lajjitadi severity per Vol 2 pp. 136-139."""
    from jyotish.planetary_evaluation import calibrate_lajjitadi_states

    jag_map = {
        "Saturn": {"multiplier": 0.10, "english": "Asleep"},
        "Venus": {"multiplier": 1.00, "english": "Awake"},
        "Sun": {"multiplier": 0.50, "english": "Sleepy"}
    }

    # Case A: Starved by sleeping Saturn (sluggish impact)
    raw_a = [{"state": "Kshudhita (Starved)", "condition": "conjoined enemy Saturn"}]
    cal_a = calibrate_lajjitadi_states("Sun", "Scorpio", raw_a, jag_map, jag_map["Sun"])
    assert len(cal_a) == 1
    assert cal_a[0]["effective_intensity"] == 0.10
    assert "Sluggish" in cal_a[0]["severity"]

    # Case B: Starved by awake Venus (acute impact)
    raw_b = [{"state": "Kshudhita (Starved)", "condition": "aspected by enemy Venus"}]
    cal_b = calibrate_lajjitadi_states("Sun", "Scorpio", raw_b, jag_map, jag_map["Sun"])
    assert len(cal_b) == 1
    assert cal_b[0]["effective_intensity"] == 1.00
    assert "Acute" in cal_b[0]["severity"]

    # Case C: Self is Jagrat (Awake) facing negative state -> 25% resilience dampening
    self_jagrat = {"multiplier": 1.00, "english": "Awake"}
    cal_c = calibrate_lajjitadi_states("Sun", "Aries", raw_b, jag_map, self_jagrat)
    assert cal_c[0]["effective_intensity"] == 0.75  # 1.00 * 0.75


def test_psychological_narrative_synthesis():
    """Verify rich 3-sentence developmental narrative synthesis."""
    from jyotish.planetary_evaluation import (
        calculate_deepthaadi_avastha,
        calculate_jagradaadi_avastha,
        calibrate_lajjitadi_states,
        synthesize_psychological_narrative
    )

    d = calculate_deepthaadi_avastha("Sun", "Scorpio", "Friend's Sign")
    j = calculate_jagradaadi_avastha("Sun", "Scorpio", "Friend's Sign")
    jag_map = {"Saturn": {"multiplier": 0.10, "english": "Asleep"}}
    raw_l = [{"state": "Kshudhita (Starved)", "condition": "conjoined enemy Saturn"}]
    cal_l = calibrate_lajjitadi_states("Sun", "Scorpio", raw_l, jag_map, j)

    narrative = synthesize_psychological_narrative("Sun", "Scorpio", d, j, cal_l)
    assert "Pramudita" in narrative
    assert "Half Capacity" in narrative or "50%" in narrative
    assert "Kshudhita" in narrative
    assert "Saturn" in narrative
    assert "Builds authentic authority" in narrative


def test_baladi_avastha_bphs_naming():
    """Verify Baladi Avastha uses classical BPHS & Kurczak Vol 2 names: Yuva and Vriddha."""
    from jyotish.planetary_evaluation import calculate_baladi_avastha

    # Odd sign tests (Aries)
    assert calculate_baladi_avastha("Aries", 2.0)["state"] == "Bala"
    assert calculate_baladi_avastha("Aries", 8.0)["state"] == "Kumara"
    assert calculate_baladi_avastha("Aries", 14.0)["state"] == "Yuva"
    assert calculate_baladi_avastha("Aries", 20.0)["state"] == "Vriddha"
    assert calculate_baladi_avastha("Aries", 26.0)["state"] == "Mrita"

    # Even sign tests (Taurus - inverted)
    assert calculate_baladi_avastha("Taurus", 2.0)["state"] == "Mrita"
    assert calculate_baladi_avastha("Taurus", 8.0)["state"] == "Vriddha"
    assert calculate_baladi_avastha("Taurus", 14.0)["state"] == "Yuva"
    assert calculate_baladi_avastha("Taurus", 20.0)["state"] == "Kumara"
    assert calculate_baladi_avastha("Taurus", 26.0)["state"] == "Bala"


def test_vic_dicara_house_terrain_and_lordship_modifiers():
    """
    Validates Vic DiCara's exact video formulas:
    1. Terrain compatibility (+25% in Upachayas for Malefics, -25% in 1,4,5,9;
       +25% in 1,4,5,9,10 for Benefics, -25% in 3,6).
    2. Lordship modifiers: +20% for 1st Lord (Lagnesha), +15% for Trine lords (5/9),
       +5% for Angle lords (4/10), -15% for Dusthana lords (6/8/12),
       and +15% Viparita reversal loophole when occupying 6/8/12.
    3. Mathematical breakdown string generation.
    """
    # Create synthetic vargas data for test case 1: Jupiter in Cancer in 3rd House (Taurus Lagna)
    vargas_case1 = {
        "D1": {
            "lagna": {"sign": "Taurus", "degree_0_to_30": 15.0},
            "grahas": {
                "Jupiter": {"sign": "Cancer", "degree_0_to_30": 5.0, "longitude": 95.0, "dignity": "Exalted"},
                "Sun": {"sign": "Aries", "degree_0_to_30": 10.0, "longitude": 10.0, "dignity": "Exalted"},
                "Moon": {"sign": "Taurus", "degree_0_to_30": 3.0, "longitude": 33.0, "dignity": "Exalted"},
                "Mars": {"sign": "Capricorn", "degree_0_to_30": 28.0, "longitude": 298.0, "dignity": "Exalted"},
                "Mercury": {"sign": "Virgo", "degree_0_to_30": 15.0, "longitude": 165.0, "dignity": "Exalted"},
                "Venus": {"sign": "Pisces", "degree_0_to_30": 27.0, "longitude": 357.0, "dignity": "Exalted"},
                "Saturn": {"sign": "Libra", "degree_0_to_30": 20.0, "longitude": 200.0, "dignity": "Exalted"},
                "Rahu": {"sign": "Taurus", "degree_0_to_30": 20.0, "longitude": 50.0, "dignity": "Exalted"},
                "Ketu": {"sign": "Scorpio", "degree_0_to_30": 20.0, "longitude": 230.0, "dignity": "Exalted"}
            }
        }
    }

    eval_case1 = calculate_planetary_evaluation(vargas_case1)
    jup_res = eval_case1["planets"]["Jupiter"]
    s4_jup = jup_res["step4_house_field"]
    fd_jup = jup_res["functional_dignity"]

    # In D1, Jupiter in Cancer is Exalted (100% base)
    assert s4_jup["house_num"] == 3
    assert s4_jup["terrain_mod_pct"] == -25.0  # Benefic in 3rd house
    # Taurus Lagna: Jupiter rules 8th (Sagittarius) and 11th (Pisces) -> 8th lord gives -15.0%
    assert s4_jup["lordship_mod_pct"] == -15.0
    # Net functional dignity: 100% - 25% - 15% = 60.0%
    assert fd_jup["functional_dignity_pct"] == 60.0
    assert "Base Dignity: 100.0%" in fd_jup["math_steps"][0]
    assert "-25.0%" in fd_jup["math_steps"][1]
    assert "-15.0%" in fd_jup["math_steps"][2]
    assert "60.0% Functional Dignity" in fd_jup["math_formula"]

    # Test Case 2: Saturn in Aries in 10th House (Cancer Lagna)
    vargas_case2 = {
        "D1": {
            "lagna": {"sign": "Cancer", "degree_0_to_30": 15.0},
            "grahas": {
                "Saturn": {"sign": "Aries", "degree_0_to_30": 20.0, "longitude": 20.0, "dignity": "Debilitated"},
                "Sun": {"sign": "Leo", "degree_0_to_30": 10.0, "longitude": 130.0, "dignity": "Moolatrikona"},
                "Moon": {"sign": "Cancer", "degree_0_to_30": 15.0, "longitude": 105.0, "dignity": "Own Sign"},
                "Mars": {"sign": "Aries", "degree_0_to_30": 5.0, "longitude": 5.0, "dignity": "Own Sign"},
                "Mercury": {"sign": "Virgo", "degree_0_to_30": 16.0, "longitude": 166.0, "dignity": "Exalted"},
                "Jupiter": {"sign": "Sagittarius", "degree_0_to_30": 5.0, "longitude": 245.0, "dignity": "Own Sign"},
                "Venus": {"sign": "Taurus", "degree_0_to_30": 10.0, "longitude": 40.0, "dignity": "Own Sign"},
                "Rahu": {"sign": "Gemini", "degree_0_to_30": 15.0, "longitude": 75.0, "dignity": "Exalted"},
                "Ketu": {"sign": "Sagittarius", "degree_0_to_30": 15.0, "longitude": 255.0, "dignity": "Exalted"}
            }
        }
    }

    eval_case2 = calculate_planetary_evaluation(vargas_case2)
    sat_res = eval_case2["planets"]["Saturn"]
    s4_sat = sat_res["step4_house_field"]
    fd_sat = sat_res["functional_dignity"]

    # In D1, Saturn in Aries is Debilitated (12.5% base in Kurczak scale)
    assert s4_sat["house_num"] == 10
    assert s4_sat["terrain_mod_pct"] == 25.0  # Malefic in 10th house Upachaya
    # Cancer Lagna: Saturn rules 7th (Capricorn) and 8th (Aquarius) -> 8th lord gives -15.0%
    assert s4_sat["lordship_mod_pct"] == -15.0
    # Net functional dignity: 12.5% + 25.0% - 15.0% = 22.5%
    assert fd_sat["functional_dignity_pct"] == 22.5
    assert "22.5% Functional Dignity" in fd_sat["math_formula"]

    # Test Case 3: Saturn in Aries in 8th House (Virgo Lagna) - Viparita Loophole
    vargas_case3 = {
        "D1": {
            "lagna": {"sign": "Virgo", "degree_0_to_30": 15.0},
            "grahas": {
                "Saturn": {"sign": "Aries", "degree_0_to_30": 20.0, "longitude": 20.0, "dignity": "Debilitated"},
                "Sun": {"sign": "Leo", "degree_0_to_30": 10.0, "longitude": 130.0, "dignity": "Moolatrikona"},
                "Moon": {"sign": "Cancer", "degree_0_to_30": 15.0, "longitude": 105.0, "dignity": "Own Sign"},
                "Mars": {"sign": "Aries", "degree_0_to_30": 5.0, "longitude": 5.0, "dignity": "Own Sign"},
                "Mercury": {"sign": "Virgo", "degree_0_to_30": 16.0, "longitude": 166.0, "dignity": "Exalted"},
                "Jupiter": {"sign": "Sagittarius", "degree_0_to_30": 5.0, "longitude": 245.0, "dignity": "Own Sign"},
                "Venus": {"sign": "Taurus", "degree_0_to_30": 10.0, "longitude": 40.0, "dignity": "Own Sign"},
                "Rahu": {"sign": "Gemini", "degree_0_to_30": 15.0, "longitude": 75.0, "dignity": "Exalted"},
                "Ketu": {"sign": "Sagittarius", "degree_0_to_30": 15.0, "longitude": 255.0, "dignity": "Exalted"}
            }
        }
    }

    eval_case3 = calculate_planetary_evaluation(vargas_case3)
    sat_res3 = eval_case3["planets"]["Saturn"]
    s4_sat3 = sat_res3["step4_house_field"]
    fd_sat3 = sat_res3["functional_dignity"]

    # In D1, Saturn is in 8th house (Intermediate field: 0.0%)
    assert s4_sat3["house_num"] == 8
    assert s4_sat3["terrain_mod_pct"] == 0.0
    # Virgo Lagna: Saturn rules 5th (Capricorn, Trine: +15.0%) and 6th (Aquarius, Dusthana).
    # Since Saturn occupies 8th (Dusthana) while ruling 6th (Dusthana), Viparita Reversal applies (+15.0%)!
    # Total lordship = +15.0% (Trine) + 15.0% (Viparita Reversal) = +30.0%
    assert s4_sat3["lordship_mod_pct"] == 30.0
    assert s4_sat3["viparita_yoga"] is not None
    # Net functional dignity: 12.5% + 0.0% + 30.0% = 42.5%
    assert fd_sat3["functional_dignity_pct"] == 42.5
    assert "42.5% Functional Dignity" in fd_sat3["math_formula"]


def test_moon_phase_and_illumination_spectrum():
    """
    Verifies continuous gradual Moon illumination scaling (BPHS 28.10-11 & 35.9):
    - 50% to 100% illumination: scales gradually from 0.0% to ±25.0% benefic terrain.
    - 50% down to 0% illumination: scales gradually from 0.0% to ±25.0% malefic terrain (Ksheenendu).
    - 50% illumination (half moon): perfectly neutral (0.0% modifier).
    """
    from jyotish.planetary_evaluation.planetary_evaluation import calculate_planetary_evaluation

    # Test Case A: 100% Full Moon (Sun in Aries 0°, Moon in Libra 180°)
    # Aries Lagna -> Libra is 7th house (Intermediate: 0.0%)
    chart_100 = {
        "D1": {
            "lagna": {"sign": "Aries", "degree_0_to_30": 15.0},
            "grahas": {
                "Sun": {"sign": "Aries", "degree_0_to_30": 0.0, "longitude": 0.0, "dignity": "Exalted"},
                "Moon": {"sign": "Libra", "degree_0_to_30": 0.0, "longitude": 180.0, "dignity": "Neutral"},
                "Mars": {"sign": "Aries", "degree_0_to_30": 5.0, "longitude": 5.0, "dignity": "Own Sign"},
                "Mercury": {"sign": "Taurus", "degree_0_to_30": 10.0, "longitude": 40.0, "dignity": "Friend"},
                "Jupiter": {"sign": "Sagittarius", "degree_0_to_30": 10.0, "longitude": 250.0, "dignity": "Own Sign"},
                "Venus": {"sign": "Taurus", "degree_0_to_30": 15.0, "longitude": 45.0, "dignity": "Own Sign"},
                "Saturn": {"sign": "Aquarius", "degree_0_to_30": 20.0, "longitude": 320.0, "dignity": "Moolatrikona"},
                "Rahu": {"sign": "Gemini", "degree_0_to_30": 15.0, "longitude": 75.0, "dignity": "Exalted"},
                "Ketu": {"sign": "Sagittarius", "degree_0_to_30": 15.0, "longitude": 255.0, "dignity": "Exalted"}
            }
        }
    }
    eval_100 = calculate_planetary_evaluation(chart_100)
    m_100 = eval_100["planets"]["Moon"]
    assert m_100["moon_phase"]["illumination_pct"] == 100.0
    assert m_100["moon_phase"]["gradual_factor"] == 1.0
    assert m_100["moon_phase"]["terrain_spectrum"] == "bright_gradual"

    # Test Case B: 75% Waxing Moon in 4th house (Cancer) -> Factor = 0.50 -> +12.5% modifier
    # Sun in Aries 0°, Moon in Scorpio 15° (elongation 225° or 135° from other side: 135° elongation = Leo 15°)
    # For Aries Lagna, Cancer is 4th house. Let Sun be Aries 0°, Moon in Cancer 15° (elongation 105° -> 58.3%)
    # Let Sun be Pisces 15° (345°), Moon in Cancer 0° (90°): elongation = (90 - 345) % 360 = 105°
    # Better yet: Sun in Pisces 0° (330°), Moon in Cancer 15° (105°): elongation = 135° -> paksha ratio = 1 - 45/180 = 0.75 (75%)
    chart_75 = {
        "D1": {
            "lagna": {"sign": "Aries", "degree_0_to_30": 15.0},
            "grahas": {
                "Sun": {"sign": "Pisces", "degree_0_to_30": 0.0, "longitude": 330.0, "dignity": "Friend"},
                "Moon": {"sign": "Cancer", "degree_0_to_30": 15.0, "longitude": 105.0, "dignity": "Own Sign"}, # 135° elongation = 75.0%
                "Mars": {"sign": "Aries", "degree_0_to_30": 5.0, "longitude": 5.0, "dignity": "Own Sign"},
                "Mercury": {"sign": "Taurus", "degree_0_to_30": 10.0, "longitude": 40.0, "dignity": "Friend"},
                "Jupiter": {"sign": "Sagittarius", "degree_0_to_30": 10.0, "longitude": 250.0, "dignity": "Own Sign"},
                "Venus": {"sign": "Taurus", "degree_0_to_30": 15.0, "longitude": 45.0, "dignity": "Own Sign"},
                "Saturn": {"sign": "Aquarius", "degree_0_to_30": 20.0, "longitude": 320.0, "dignity": "Moolatrikona"},
                "Rahu": {"sign": "Gemini", "degree_0_to_30": 15.0, "longitude": 75.0, "dignity": "Exalted"},
                "Ketu": {"sign": "Sagittarius", "degree_0_to_30": 15.0, "longitude": 255.0, "dignity": "Exalted"}
            }
        }
    }
    eval_75 = calculate_planetary_evaluation(chart_75)
    m_75 = eval_75["planets"]["Moon"]
    assert m_75["moon_phase"]["illumination_pct"] == 75.0
    assert m_75["moon_phase"]["gradual_factor"] == 0.5
    # Moon in Cancer is 4th house for Aries Lagna -> Noble field: +25% * 0.50 = +12.5%
    assert m_75["step4_house_field"]["house_num"] == 4
    assert m_75["step4_house_field"]["terrain_mod_pct"] == 12.5
    assert "Noble Flourishing Field (Gradual Lunar Light)" in m_75["step4_house_field"]["terrain_type"]

    # Test Case C: 50% Half Moon in 4th house (Cancer) -> Factor = 0.0 -> 0.0% modifier
    # Sun in Aries 0°, Moon in Cancer 0° (90° elongation = 50.0% half moon)
    chart_50 = {
        "D1": {
            "lagna": {"sign": "Aries", "degree_0_to_30": 15.0},
            "grahas": {
                "Sun": {"sign": "Aries", "degree_0_to_30": 0.0, "longitude": 0.0, "dignity": "Exalted"},
                "Moon": {"sign": "Cancer", "degree_0_to_30": 0.0, "longitude": 90.0, "dignity": "Own Sign"},
                "Mars": {"sign": "Aries", "degree_0_to_30": 5.0, "longitude": 5.0, "dignity": "Own Sign"},
                "Mercury": {"sign": "Taurus", "degree_0_to_30": 10.0, "longitude": 40.0, "dignity": "Friend"},
                "Jupiter": {"sign": "Sagittarius", "degree_0_to_30": 10.0, "longitude": 250.0, "dignity": "Own Sign"},
                "Venus": {"sign": "Taurus", "degree_0_to_30": 15.0, "longitude": 45.0, "dignity": "Own Sign"},
                "Saturn": {"sign": "Aquarius", "degree_0_to_30": 20.0, "longitude": 320.0, "dignity": "Moolatrikona"},
                "Rahu": {"sign": "Gemini", "degree_0_to_30": 15.0, "longitude": 75.0, "dignity": "Exalted"},
                "Ketu": {"sign": "Sagittarius", "degree_0_to_30": 15.0, "longitude": 255.0, "dignity": "Exalted"}
            }
        }
    }
    eval_50 = calculate_planetary_evaluation(chart_50)
    m_50 = eval_50["planets"]["Moon"]
    assert m_50["moon_phase"]["illumination_pct"] == 50.0
    assert m_50["moon_phase"]["gradual_factor"] == 0.0
    assert m_50["step4_house_field"]["terrain_mod_pct"] == 0.0

    # Test Case D: 25% Dark Moon in 4th house (Cancer) -> Factor = 0.50 -> -12.5% modifier
    # Elongation 45°: Sun in Taurus 15° (45°), Moon in Cancer 0° (90°) -> elongation = 45° -> paksha ratio = 45/180 = 0.25 (25%)
    chart_25 = {
        "D1": {
            "lagna": {"sign": "Aries", "degree_0_to_30": 15.0},
            "grahas": {
                "Sun": {"sign": "Taurus", "degree_0_to_30": 15.0, "longitude": 45.0, "dignity": "Enemy"},
                "Moon": {"sign": "Cancer", "degree_0_to_30": 0.0, "longitude": 90.0, "dignity": "Own Sign"},
                "Mars": {"sign": "Aries", "degree_0_to_30": 5.0, "longitude": 5.0, "dignity": "Own Sign"},
                "Mercury": {"sign": "Taurus", "degree_0_to_30": 10.0, "longitude": 40.0, "dignity": "Friend"},
                "Jupiter": {"sign": "Sagittarius", "degree_0_to_30": 10.0, "longitude": 250.0, "dignity": "Own Sign"},
                "Venus": {"sign": "Taurus", "degree_0_to_30": 15.0, "longitude": 45.0, "dignity": "Own Sign"},
                "Saturn": {"sign": "Aquarius", "degree_0_to_30": 20.0, "longitude": 320.0, "dignity": "Moolatrikona"},
                "Rahu": {"sign": "Gemini", "degree_0_to_30": 15.0, "longitude": 75.0, "dignity": "Exalted"},
                "Ketu": {"sign": "Sagittarius", "degree_0_to_30": 15.0, "longitude": 255.0, "dignity": "Exalted"}
            }
        }
    }
    eval_25 = calculate_planetary_evaluation(chart_25)
    m_25 = eval_25["planets"]["Moon"]
    assert m_25["moon_phase"]["illumination_pct"] == 25.0
    assert m_25["moon_phase"]["gradual_factor"] == 0.5
    assert m_25["moon_phase"]["terrain_spectrum"] == "dark_gradual"
    # Moon in 4th house (Tender Field Strain): -25% * 0.50 = -12.5%
    assert m_25["step4_house_field"]["terrain_mod_pct"] == -12.5
    assert "Tender Field Strain (Gradual Dark Moon)" in m_25["step4_house_field"]["terrain_type"]

    # Test Case E: 0% New Moon in 3rd house (Gemini) -> Upachaya Growth: +25% * 1.0 = +25.0%
    # Sun in Gemini 15° (75°), Moon in Gemini 15° (75°) -> elongation 0°
    chart_0 = {
        "D1": {
            "lagna": {"sign": "Aries", "degree_0_to_30": 15.0},
            "grahas": {
                "Sun": {"sign": "Gemini", "degree_0_to_30": 15.0, "longitude": 75.0, "dignity": "Neutral"},
                "Moon": {"sign": "Gemini", "degree_0_to_30": 15.0, "longitude": 75.0, "dignity": "Friend"},
                "Mars": {"sign": "Aries", "degree_0_to_30": 5.0, "longitude": 5.0, "dignity": "Own Sign"},
                "Mercury": {"sign": "Taurus", "degree_0_to_30": 10.0, "longitude": 40.0, "dignity": "Friend"},
                "Jupiter": {"sign": "Sagittarius", "degree_0_to_30": 10.0, "longitude": 250.0, "dignity": "Own Sign"},
                "Venus": {"sign": "Taurus", "degree_0_to_30": 15.0, "longitude": 45.0, "dignity": "Own Sign"},
                "Saturn": {"sign": "Aquarius", "degree_0_to_30": 20.0, "longitude": 320.0, "dignity": "Moolatrikona"},
                "Rahu": {"sign": "Taurus", "degree_0_to_30": 15.0, "longitude": 45.0, "dignity": "Exalted"},
                "Ketu": {"sign": "Scorpio", "degree_0_to_30": 15.0, "longitude": 225.0, "dignity": "Exalted"}
            }
        }
    }
    eval_0 = calculate_planetary_evaluation(chart_0)
    m_0 = eval_0["planets"]["Moon"]
    assert m_0["moon_phase"]["illumination_pct"] == 0.0
    assert m_0["moon_phase"]["gradual_factor"] == 1.0
    # Gemini is 3rd house for Aries Lagna -> Upachaya Growth for dark moon: +25.0%
    assert m_0["step4_house_field"]["house_num"] == 3
    assert m_0["step4_house_field"]["terrain_mod_pct"] == 25.0
    assert "Upachaya Growth Field (Gradual Dark Moon)" in m_0["step4_house_field"]["terrain_type"]


def test_vitality_functional_dignity_integration():
    """
    Verifies that calculate_graha_vitality integrates functional dignity from Step 4,
    updating the effective dignity, calculation receipt, and vitality score.
    """
    from jyotish.planetary_evaluation.planetary_evaluation import calculate_planetary_evaluation

    # Test with Leo Lagna, Sun in Scorpio (4th House)
    chart = {
        "D1": {
            "lagna": {"sign": "Leo", "degree_0_to_30": 15.0},
            "grahas": {
                "Sun": {"sign": "Scorpio", "degree_0_to_30": 10.0, "longitude": 220.0, "dignity": "Great Friend"},
                "Moon": {"sign": "Taurus", "degree_0_to_30": 10.0, "longitude": 40.0, "dignity": "Exalted"},
                "Mars": {"sign": "Aries", "degree_0_to_30": 5.0, "longitude": 5.0, "dignity": "Own Sign"},
                "Mercury": {"sign": "Virgo", "degree_0_to_30": 10.0, "longitude": 160.0, "dignity": "Exalted"},
                "Jupiter": {"sign": "Sagittarius", "degree_0_to_30": 10.0, "longitude": 250.0, "dignity": "Own Sign"},
                "Venus": {"sign": "Libra", "degree_0_to_30": 15.0, "longitude": 195.0, "dignity": "Own Sign"},
                "Saturn": {"sign": "Aquarius", "degree_0_to_30": 20.0, "longitude": 320.0, "dignity": "Moolatrikona"},
                "Rahu": {"sign": "Gemini", "degree_0_to_30": 15.0, "longitude": 75.0, "dignity": "Exalted"},
                "Ketu": {"sign": "Sagittarius", "degree_0_to_30": 15.0, "longitude": 255.0, "dignity": "Exalted"}
            }
        }
    }
    eval_res = calculate_planetary_evaluation(chart)
    sun = eval_res["planets"]["Sun"]
    vit = sun["vitality"]
    receipt = vit["calculation_receipt"]

    # Sun in H4: -25% (Terrain) + 20% (Lagna Lord) = -5.0% delta
    assert receipt["house_field_delta_pct"] == -5.0
    assert "House Field & Lordship: -5.0%" in receipt["receipt_text"]
    assert "Functional: 55.0%" in receipt["receipt_text"]


def test_mars_in_scorpio_12th_house_dignity():
    """
    Verifies Mina's chart configuration (Sagittarius Lagna, Mars in Scorpio in H12):
    1. Base Dignity: 62.5% (Scorpio is even own sign on Kurczak scale, not 68.8%).
    2. House Terrain: 0.0% (H12 is intermediate).
    3. Trine Lord (H5): +15.0%.
    4. 12th Lord in 12th house: 0.0% (Own Dusthana, at home - NOT a +15% Viparita reversal).
    5. Net Functional Dignity: 77.5% (NOT 98.8%).
    """
    chart = {
        "D1": {
            "lagna": {"sign": "Sagittarius", "degree_0_to_30": 15.0},
            "grahas": {
                "Sun": {"sign": "Aries", "degree_0_to_30": 10.0, "longitude": 10.0, "dignity": "Exalted"},
                "Moon": {"sign": "Taurus", "degree_0_to_30": 10.0, "longitude": 40.0, "dignity": "Exalted"},
                "Mars": {"sign": "Scorpio", "degree_0_to_30": 15.0, "longitude": 225.0, "dignity": "Own Sign"},
                "Mercury": {"sign": "Virgo", "degree_0_to_30": 10.0, "longitude": 160.0, "dignity": "Exalted"},
                "Jupiter": {"sign": "Sagittarius", "degree_0_to_30": 10.0, "longitude": 250.0, "dignity": "Own Sign"},
                "Venus": {"sign": "Libra", "degree_0_to_30": 15.0, "longitude": 195.0, "dignity": "Own Sign"},
                "Saturn": {"sign": "Aquarius", "degree_0_to_30": 20.0, "longitude": 320.0, "dignity": "Moolatrikona"},
                "Rahu": {"sign": "Gemini", "degree_0_to_30": 15.0, "longitude": 75.0, "dignity": "Exalted"},
                "Ketu": {"sign": "Sagittarius", "degree_0_to_30": 15.0, "longitude": 255.0, "dignity": "Exalted"}
            }
        }
    }
    eval_res = calculate_planetary_evaluation(chart)
    mars = eval_res["planets"]["Mars"]
    f_dig = mars["functional_dignity"]

    # 1. Base dignity for Scorpio must be 62.5% (even sign own sign)
    assert f_dig["base_dignity_pct"] == 62.5
    # 2. House Terrain for H12 is 0.0%
    assert f_dig["terrain_mod_pct"] == 0.0
    assert f_dig["terrain_dignity_pct"] == 62.5
    # 3. Lordship: H5 Trine (+15%) + H12 Own Dusthana (0%) = +15% total
    assert f_dig["lordship_mod_pct"] == 15.0
    # 4. Final Functional Dignity = 62.5 + 0.0 + 15.0 = 77.5% (never 98.8%!)
    assert f_dig["functional_dignity_pct"] == 77.5
    assert "Own Dusthana (H12): 0.0%" in f_dig["math_steps"]
    assert "Viparita" not in f_dig["math_steps"]







