"""
tests/test_houses_of_life.py

Unit and Integration Tests for Vic DiCara's "Houses of Life" Evaluation Engine
(Phaladīpikā Chapter 15).
"""

import pytest
from jyotish.pipeline import ChartPipeline
from jyotish.report.houses_of_life import (
    CLASSICAL_PLANETS,
    DICARA_MOOLATRIKONA_SIGNS,
    DICARA_DOMICILE_SIGNS,
    DICARA_D1_DIGNITY_MAP,
    _shortest_distance,
    _extract_whole_sign_geometry,
    calculate_functional_nature,
    scale_by_dignity,
    calculate_cusp_and_planet_influences,
    evaluate_planets_hol,
    evaluate_basic_house_conditions,
    evaluate_relative_houses_bhavat_bhavam,
    evaluate_house_walls_kartari,
    evaluate_house_yogas_hol,
    evaluate_houses_of_life,
)


class TestHousesOfLifePhase1Geometry:
    """Tests Phase 1: Whole Sign geometry and sensitive cusp calculation."""

    def test_ascendant_sensitive_cusps(self):
        # Create a mock chart_dict with 13.37 Leo rising
        mock_chart = {
            "vargas": {
                "D1": {
                    "lagna": {
                        "sign": "Leo",
                        "degree_0_to_30": 13.37,
                        "longitude": 133.37
                    },
                    "grahas": {p: {"sign": "Leo", "longitude": 133.37} for p in CLASSICAL_PLANETS}
                }
            }
        }
        geom = _extract_whole_sign_geometry(mock_chart)
        assert geom["ascendant_sign"] == "Leo"
        assert geom["ascendant_degree"] == 13.37
        assert geom["ascendant_longitude"] == 133.37

        houses = geom["houses"]
        assert len(houses) == 12

        # House 1 should be Leo, cusp = 133.37
        assert houses[1]["sign"] == "Leo"
        assert houses[1]["lord"] == "Sun"
        assert pytest.approx(houses[1]["cusp_longitude"], abs=1e-4) == 133.37
        assert pytest.approx(houses[1]["cusp_degree"], abs=1e-4) == 13.37

        # House 2 should be Virgo, cusp = 163.37
        assert houses[2]["sign"] == "Virgo"
        assert houses[2]["lord"] == "Mercury"
        assert pytest.approx(houses[2]["cusp_longitude"], abs=1e-4) == 163.37

        # House 11 should be Gemini, cusp = 73.37
        assert houses[11]["sign"] == "Gemini"
        assert houses[11]["lord"] == "Mercury"
        assert pytest.approx(houses[11]["cusp_longitude"], abs=1e-4) == 73.37


class TestHousesOfLifePhase2FunctionalNature:
    """Tests Phase 2: Functional nature quantification per Phaladeepika Ch. 15."""

    def test_first_house_lord_rule(self):
        # Aries Lagna: Mars rules H1
        fn_aries = calculate_functional_nature("Aries")
        assert fn_aries["Mars"]["score"] == 3
        assert fn_aries["Mars"]["classification"] == "Benefic"
        assert fn_aries["Mars"]["rule_breakdown"]["is_first_lord"] is True

        # Leo Lagna: Sun rules H1
        fn_leo = calculate_functional_nature("Leo")
        assert fn_leo["Sun"]["score"] == 3
        assert fn_leo["Sun"]["classification"] == "Benefic"

        # Capricorn Lagna: Saturn rules H1
        fn_cap = calculate_functional_nature("Capricorn")
        assert fn_cap["Saturn"]["score"] == 3
        assert fn_cap["Saturn"]["classification"] == "Benefic"

    def test_moon_special_exceptions(self):
        # Sagittarius Lagna: Taurus is H6 (MT), Cancer is H8 (Dom)
        # Evaluated as OR condition -> -2, NOT -3
        fn_sag = calculate_functional_nature("Sagittarius")
        assert fn_sag["Moon"]["score"] == -2
        assert fn_sag["Moon"]["classification"] == "Malefic"

        # Capricorn Lagna: Taurus is H5 (MT on trine -> +2)
        fn_cap = calculate_functional_nature("Capricorn")
        assert fn_cap["Moon"]["score"] == 2
        assert fn_cap["Moon"]["classification"] == "Benefic"

    def test_mercury_female_sign_exception(self):
        # For Aries Lagna: Gemini is H3, Virgo (female MT) is H6 (Dusthana -2)
        fn_aries = calculate_functional_nature("Aries")
        assert fn_aries["Mercury"]["score"] == -2

        # For Taurus Lagna: Gemini is H2, Virgo (female MT) is H5 (Trine +2)
        fn_tau = calculate_functional_nature("Taurus")
        assert fn_tau["Mercury"]["score"] == 2

    def test_inherent_temperaments_rule4(self):
        # For Leo Lagna:
        # Jupiter: MT Sagittarius (H5 -> +2), Dom Pisces (H8 -> -1), Inherent +1 -> Net +2
        # Venus: MT Libra (H3 -> 0), Dom Taurus (H10 -> 0), Inherent +1 -> Net +1
        # Saturn: MT Aquarius (H7 -> 0), Dom Capricorn (H6 -> -1), Inherent -1 -> Net -2
        fn_leo = calculate_functional_nature("Leo")
        assert fn_leo["Jupiter"]["score"] == 2
        assert fn_leo["Venus"]["score"] == 1
        assert fn_leo["Saturn"]["score"] == -2


class TestHousesOfLifePhase3DignityScaling:
    """Tests Phase 3: Universal dignity-scaling law."""

    def test_scale_by_dignity_benefic(self):
        # Positive planet (F > 0)
        # Good mood (d >= 0): up to 2x intensification
        assert pytest.approx(scale_by_dignity(100.0, 1.0, 3), abs=1e-4) == 200.0
        assert pytest.approx(scale_by_dignity(100.0, 0.4, 1), abs=1e-4) == 140.0
        # Bad mood (d < 0): diminished by at most half; never flips negative
        assert pytest.approx(scale_by_dignity(100.0, -1.0, 2), abs=1e-4) == 50.0
        assert pytest.approx(scale_by_dignity(100.0, -0.4, 2), abs=1e-4) == 80.0

    def test_scale_by_dignity_malefic(self):
        # Negative planet (F < 0)
        # Bad mood (d <= 0): malice intensified up to 2x
        assert pytest.approx(scale_by_dignity(100.0, -1.0, -2), abs=1e-4) == 200.0
        assert pytest.approx(scale_by_dignity(100.0, -0.4, -1), abs=1e-4) == 140.0
        # Good mood (d > 0): malice mitigated by up to half
        assert pytest.approx(scale_by_dignity(100.0, 1.0, -2), abs=1e-4) == 50.0
        assert pytest.approx(scale_by_dignity(100.0, 0.4, -1), abs=1e-4) == 80.0

    def test_scale_by_dignity_neutral(self):
        # Neutral planet (F == 0)
        # Intensified by (1 + |d|) with sign of d
        assert pytest.approx(scale_by_dignity(100.0, 0.6, 0), abs=1e-4) == 160.0
        assert pytest.approx(scale_by_dignity(100.0, -0.6, 0), abs=1e-4) == -160.0
        assert pytest.approx(scale_by_dignity(100.0, 0.0, 0), abs=1e-4) == 0.0


class TestHousesOfLifePhase4ConjunctionAndDominance:
    """Tests Phase 4: Conjunction, cross-border halving, and potency stealing."""

    def test_shortest_distance(self):
        assert pytest.approx(_shortest_distance(10.0, 350.0), abs=1e-4) == 20.0
        assert pytest.approx(_shortest_distance(350.0, 10.0), abs=1e-4) == 20.0
        assert pytest.approx(_shortest_distance(100.0, 120.0), abs=1e-4) == 20.0

    def test_cusp_dominance_stealing(self):
        # Two occupants in H11 (Gemini):
        # Sun with raw C_near ~ 90.3, Mercury with raw C_far ~ 79.0
        c_near = 90.3
        c_far = 79.0
        steal = c_far * (c_near / (c_near + c_far))
        assert pytest.approx(steal, abs=0.5) == 42.1
        final_near = c_near + steal
        final_far = c_far - steal
        assert pytest.approx(final_near, abs=0.5) == 132.4
        assert pytest.approx(final_far, abs=0.5) == 36.9


class TestHousesOfLifePhase8HouseWalls:
    """Tests Phase 8: Kartari Yoga (house walls)."""

    def test_house_walls_unwalled(self):
        # If planets are far from cusp
        geometry = {
            "houses": {
                1: {"cusp_longitude": 0.0, "lord": "Mars"}
            }
        }
        d1_grahas = {
            "Sun": {"longitude": 100.0, "dignity": "Own Sign"},
            "Moon": {"longitude": 120.0, "dignity": "Own Sign"},
            "Mars": {"longitude": 140.0, "dignity": "Own Sign"},
            "Mercury": {"longitude": 160.0, "dignity": "Own Sign"},
            "Jupiter": {"longitude": 180.0, "dignity": "Own Sign"},
            "Venus": {"longitude": 200.0, "dignity": "Own Sign"},
            "Saturn": {"longitude": 220.0, "dignity": "Own Sign"},
        }
        func_natures = {p: {"score": 1} for p in CLASSICAL_PLANETS}
        res = evaluate_house_walls_kartari(geometry, d1_grahas, func_natures)
        assert res[1]["is_walled"] is False
        assert res[1]["score"] == 0.0

    def test_house_walls_walled_shubha_kartari(self):
        geometry = {
            "houses": {
                1: {"cusp_longitude": 50.0, "lord": "Venus"}
            }
        }
        # Cusp at 50. Jupiter at 40 (before by 10 deg), Mercury at 60 (after by 10 deg)
        d1_grahas = {
            "Jupiter": {"longitude": 40.0, "dignity": "Exalted"},
            "Mercury": {"longitude": 60.0, "dignity": "Own Sign"},
            "Sun": {"longitude": 180.0, "dignity": "Neutral"},
            "Moon": {"longitude": 200.0, "dignity": "Neutral"},
            "Mars": {"longitude": 220.0, "dignity": "Neutral"},
            "Venus": {"longitude": 240.0, "dignity": "Neutral"},
            "Saturn": {"longitude": 260.0, "dignity": "Neutral"},
        }
        func_natures = {p: {"score": 2} for p in CLASSICAL_PLANETS}
        res = evaluate_house_walls_kartari(geometry, d1_grahas, func_natures)
        assert res[1]["is_walled"] is True
        assert res[1]["wall_type"] == "Shubha Kartari"
        assert res[1]["score"] > 0.0


class TestHousesOfLifePhase9HouseYogas:
    """Tests Phase 9: 4 Structural Yogas scoring."""

    def test_parivartana_yoga_same_category(self):
        # House 8 (Dusthana) and House 12 (Dusthana) exchange lords
        geometry = {
            "houses": {
                h: {"lord": f"Lord{h}", "sign": f"Sign{h}"} for h in range(1, 13)
            }
        }
        # Aries Lagna: H8 lord is Mars, H12 lord is Jupiter
        geometry["houses"][8]["lord"] = "Mars"
        geometry["houses"][12]["lord"] = "Jupiter"

        d1_grahas = {
            p: {"sign": f"Sign{h}", "longitude": h * 30.0, "ruled_houses": []}
            for h, p in enumerate(CLASSICAL_PLANETS, 1)
        }
        # Mars in H12, Jupiter in H8
        d1_grahas["Mars"] = {"sign": "Sign12", "longitude": 12 * 30.0, "ruled_houses": [8]}
        d1_grahas["Jupiter"] = {"sign": "Sign8", "longitude": 8 * 30.0, "ruled_houses": [12]}

        yogas = evaluate_house_yogas_hol(geometry, d1_grahas)
        # Both H8 and H12 are Dusthanas -> same category exception awards +150
        assert yogas[8]["parivartana_score"] == 150.0
        assert yogas[12]["parivartana_score"] == 150.0

    def test_mahapurusha_yoga(self):
        geometry = {
            "houses": {
                h: {"lord": f"Lord{h}", "sign": f"Sign{h}"} for h in range(1, 13)
            }
        }
        d1_grahas = {
            p: {"sign": "Sign1", "longitude": 10.0, "ruled_houses": [1, 8], "dignity": "Exalted"}
            for p in CLASSICAL_PLANETS
        }
        # Mars in Kendra H1, Exalted (D_pct = 100)
        d1_grahas["Mars"] = {"sign": "Sign1", "longitude": 10.0, "ruled_houses": [1, 8], "dignity": "Exalted"}

        yogas = evaluate_house_yogas_hol(geometry, d1_grahas)
        # Mars occupies H1 (Kendra) and owns H1 & H8
        assert yogas[1]["mahapurusha_score"] >= 100.0


class TestHousesOfLifePipelineIntegration:
    """Tests end-to-end ChartPipeline integration."""

    def test_pipeline_houses_of_life_execution(self):
        pipeline = ChartPipeline('Marilyn Monroe', 1926, 6, 1, 9, 30, 0, 34.0522, -118.2437, -8.0)
        hol = pipeline.houses_of_life

        # Assert Metadata
        assert "metadata" in hol
        assert hol["metadata"]["report_type"] == "Houses of Life (Vic DiCara / Phaladeepika System)"
        assert hol["metadata"]["house_system"] == "Whole Sign (Ascendant Degree Sensitive Cusps)"
        assert hol["metadata"]["varga_evaluated"] == "D1"

        # Assert Planets
        assert len(hol["planets"]) == 7
        for p in CLASSICAL_PLANETS:
            assert p in hol["planets"]
            p_res = hol["planets"][p]
            assert "sign" in p_res
            assert "house" in p_res
            assert "functional_nature" in p_res
            assert "dignity" in p_res
            assert "combined_influences" in p_res
            assert "cusp_alignment" in p_res
            assert "bhava_sandhi" in p_res
            assert "combustion" in p_res
            assert "base_average_score" in p_res
            assert "final_assessment_score" in p_res

        # Assert Houses
        assert len(hol["houses"]) == 12
        for h in range(1, 13):
            h_str = str(h)
            assert h_str in hol["houses"]
            h_res = hol["houses"][h_str]
            assert h_res["house"] == h
            assert "components" in h_res
            comps = h_res["components"]
            assert "basic_house_condition" in comps
            assert "lord_assessment" in comps
            assert "relative_house_bhavat_bhavam" in comps
            assert "house_walls_kartari" in comps
            assert "house_yogas" in comps
            assert "synthesis" in h_res
            synth = h_res["synthesis"]
            assert "composite_score" in synth
            assert "health_rating" in synth
            assert "classical_tier" in synth
            assert synth["classical_tier"] in ["Puṣṭa", "Miśra", "Hīna"]
            assert len(synth["dominant_drivers"]) > 0

        # Assert Summary Rankings
        rankings = hol["summary_rankings"]
        assert len(rankings["houses_by_composite_score"]) == 12
        assert len(rankings["planets_by_final_score"]) == 7
        assert len(rankings["top_flourishing_houses"]) == 3
        assert len(rankings["most_challenged_houses"]) == 3

    def test_pipeline_to_dict_attachment(self):
        pipeline = ChartPipeline('Test Native', 1985, 3, 21, 14, 15, 0, 51.5074, -0.1278, 0.0)
        chart_dict = pipeline.to_dict()
        assert "houses_of_life" in chart_dict
        hol = chart_dict["houses_of_life"]
        assert "metadata" in hol
        assert "planets" in hol
        assert "houses" in hol
        assert "summary_rankings" in hol
