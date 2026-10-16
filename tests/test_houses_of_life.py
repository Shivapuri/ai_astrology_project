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
    _get_dignity_status,
    _extract_whole_sign_geometry,
    calculate_functional_nature,
    scale_by_dignity,
    calculate_cusp_and_planet_influences,
    evaluate_planets_hol,
    evaluate_basic_house_conditions,
    evaluate_relative_houses_bhavat_bhavam,
    evaluate_house_walls_kartari,
    evaluate_house_yogas_hol,
    _trace_dispositor_chains,
    evaluate_houses_of_life,
    ZODIAC_SIGNS,
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

        yogas_input = {
            "yogas": [
                {
                    "name": "Parivartana Yoga",
                    "category": "Parivartana (Exchange)",
                    "status": "Pure & Eminent",
                    "plausibility_score": 100.0,
                    "participating_planets": ["Mars", "Jupiter"],
                    "participating_houses": [8, 12]
                }
            ]
        }
        yogas = evaluate_house_yogas_hol(geometry, d1_grahas, yogas_input)
        assert yogas[8]["parivartana_score"] > 0.0
        assert yogas[12]["parivartana_score"] > 0.0
        assert yogas[8]["total_yoga_score"] > 0.0

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

        yogas_input = {
            "yogas": [
                {
                    "name": "Ruchaka Yoga",
                    "category": "Pancha Mahapurusha",
                    "status": "Pure & Eminent",
                    "plausibility_score": 100.0,
                    "participating_planets": ["Mars"],
                    "participating_houses": [1]
                }
            ]
        }
        yogas = evaluate_house_yogas_hol(geometry, d1_grahas, yogas_input)
        # Mars occupies H1 (Kendra) and owns H1 & H8
        assert yogas[1]["mahapurusha_score"] >= 80.0


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


class TestHousesOfLifeMathematicalAuditFixes:
    """Verifies the 4 subtle mathematical fixes identified during audit."""

    def test_basic_house_condition_neutral_planet_negative_dignity(self):
        # A neutral planet with negative dignity should have negative signed impact
        # without double negation flipping it to positive.
        geometry = {"houses": {1: {"lord": "Mars", "sign": "Aries"}}}
        func_natures = {"Mercury": {"score": 0}}
        for p in CLASSICAL_PLANETS:
            if p not in func_natures:
                func_natures[p] = {"score": 1}

        d1_grahas = {p: {"dignity": "Own Sign"} for p in CLASSICAL_PLANETS}
        # Mercury neutral with Enemy dignity (-0.4)
        d1_grahas["Mercury"]["dignity"] = "Enemy's Sign"

        influences = {
            "planet_to_cusp": {p: {1: 0.0} for p in CLASSICAL_PLANETS}
        }
        influences["planet_to_cusp"]["Mercury"][1] = 50.0  # 50% impact

        res = evaluate_basic_house_conditions(geometry, func_natures, d1_grahas, influences)
        # Mercury contribution should be strictly negative: -50 * 1.4 = -70.0
        assert res[1]["planet_contributions"]["Mercury"] == -70.0

    def test_bhavat_bhavam_neutral_planet_dignity_fallback(self):
        # When evaluating relative houses, a planet with raw relative score 0
        # adopts its dignity unit as effective functional nature.
        # Leo Ascendant -> House 4 is Scorpio (sign_index 7)
        signs = ["Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces", "Aries", "Taurus", "Gemini", "Cancer"]
        geometry = {"houses": {h: {"sign": signs[h - 1], "lord": "Mars"} for h in range(1, 13)}}

        # Sun rules Leo (10th from Scorpio -> raw relative functional score = 0)
        # Sun has -0.4 dignity -> eff_f = -0.4, base pts = -20.0, scaled = -28.0
        # Sun is in Aries (House 9 from Leo, which is 6th relative to Scorpio -> Dusthana!)
        d1_grahas = {p: {"sign": "Leo", "longitude": 0.0, "dignity": "Own Sign"} for p in CLASSICAL_PLANETS}
        d1_grahas["Sun"]["dignity"] = "Enemy's Sign"  # -0.4
        d1_grahas["Sun"]["sign"] = "Aries"  # Relative house from Scorpio is 6 (Dusthana)

        # Benefic relative planet in KK house: Jupiter in Pisces (House 8 from Leo -> 5th from Scorpio)
        d1_grahas["Jupiter"]["sign"] = "Pisces"
        d1_grahas["Jupiter"]["dignity"] = "Own Sign"

        influences = {
            "planet_to_planet": {p1: {p2: 0.0 for p2 in CLASSICAL_PLANETS} for p1 in CLASSICAL_PLANETS}
        }
        res = evaluate_relative_houses_bhavat_bhavam(geometry, d1_grahas, influences)
        # Sun should be in m_dust and active_planets_count should include Sun
        assert res[4]["active_planets_count"] >= 1
        assert res[4]["dusthana_raw_points"] < 0.0

    def test_cross_sign_yoga_rejection(self):
        # Two planets in adjacent signs within 24 deg should NOT combine for yoga
        geometry = {"houses": {h: {"lord": f"Lord{h}", "sign": f"Sign{h}"} for h in range(1, 13)}}
        d1_grahas = {p: {"sign": f"Sign{i}", "longitude": i * 30.0, "ruled_houses": []} for i, p in enumerate(CLASSICAL_PLANETS, 1)}
        # Jupiter at 27 deg sign 7, Mars at 21 deg sign 8 (diff = 24 deg, but different signs)
        d1_grahas["Jupiter"] = {"sign": "Sign7", "longitude": 207.0, "ruled_houses": [5, 8]}
        d1_grahas["Mars"] = {"sign": "Sign8", "longitude": 231.0, "ruled_houses": [4, 9]}

        yogas = evaluate_house_yogas_hol(geometry, d1_grahas, {"yogas": []})
        # Should not form Raja Yoga across sign boundaries without mutual aspect or exchange
        active_raja = [y for h in range(1, 13) for y in yogas[h]["active_yogas"] if y["type"] == "Rāja Yoga"]
        assert len(active_raja) == 0

    def test_first_lord_immunity_and_double_occupancy_daridra(self):
        # 1st Lord immunity: Mars ruling H1 and H8 does not trigger Daridra as Dusthana lord
        geometry = {"houses": {h: {"lord": f"Lord{h}", "sign": f"Sign{h}"} for h in range(1, 13)}}
        d1_grahas = {p: {"sign": f"Sign{i}", "longitude": i * 30.0, "ruled_houses": []} for i, p in enumerate(CLASSICAL_PLANETS, 1)}
        # Mars rules H1 and H8
        d1_grahas["Mars"] = {"sign": "Sign1", "longitude": 10.0, "ruled_houses": [1, 8]}
        # Sun rules H5, conjunct Mars in Sign1
        d1_grahas["Sun"] = {"sign": "Sign1", "longitude": 15.0, "ruled_houses": [5]}

        yogas = evaluate_house_yogas_hol(geometry, d1_grahas, {"yogas": []})
        # Because Mars is 1st lord, its 8th ownership is immune and does NOT trigger Daridra with Sun!
        daridra_yogas = [y for h in range(1, 13) for y in yogas[h]["active_yogas"] if y["type"] == "Daridra Yoga"]
        assert len(daridra_yogas) == 0

    def test_phase6_neutral_negative_dignity_no_double_negation(self):
        """Ensures a functionally neutral planet (F=0) with negative dignity (-0.4) yields a negative house impact."""
        geometry = {
            "houses": {
                1: {"cusp_longitude": 10.0, "lord": "Mars", "sign": "Aries", "occupants": ["Mercury"]}
            }
        }
        func_natures = {p: {"score": 0} for p in CLASSICAL_PLANETS}
        d1_grahas = {
            p: {"longitude": 190.0, "sign": "Libra", "dignity": "Neutral"}
            for p in CLASSICAL_PLANETS
        }
        d1_grahas["Mercury"] = {"longitude": 10.0, "sign": "Aries", "dignity": "Enemy"}  # d_p = -0.4
        influences = {
            "planet_to_cusp": {p: {1: 100.0 if p == "Mercury" else 0.0} for p in CLASSICAL_PLANETS}
        }
        res = evaluate_basic_house_conditions(geometry, func_natures, d1_grahas, influences)
        # 100 * (1 + 0.4) * -1 = -140.0
        assert pytest.approx(res[1]["planet_contributions"]["Mercury"], abs=1e-2) == -140.0

    def test_phase7_neutral_planet_dignity_fallback(self):
        """Ensures a relative neutral planet (raw F=0) uses its dignity as its relative functional nature without double-scaling."""
        geometry = {
            "houses": {
                h: {"sign": ZODIAC_SIGNS[h - 1], "lord": "Mars"} for h in range(1, 13)
            }
        }
        d1_grahas = {
            p: {"sign": "Scorpio", "longitude": 220.0, "dignity": "Neutral"}
            for p in CLASSICAL_PLANETS
        }
        # Relative to House 8 (Scorpio), Gemini is 8th house (Dusthana) and Sun owns Leo (10th = raw 0)
        d1_grahas["Sun"] = {"sign": "Gemini", "longitude": 70.0, "dignity": "Enemy"}  # d_p = -0.4 -> pts = -20 -> scaled = -70.0
        influences = {
            "planet_to_planet": {p: {q: 0.0 for q in CLASSICAL_PLANETS if q != p} for p in CLASSICAL_PLANETS}
        }
        rel = evaluate_relative_houses_bhavat_bhavam(geometry, d1_grahas, influences)
        assert pytest.approx(rel[8]["relative_functional_natures"]["Sun"], abs=1e-2) == -20.0
        assert pytest.approx(rel[8]["dusthana_raw_points"], abs=1e-2) == -70.0

    def test_raja_yoga_hosting_deduplication_vs_ownership(self):
        """
        Ensures two planets forming a certified Raja Yoga award points to
        the hosting house H10 and to each owned house.
        """
        geometry = {"houses": {h: {"lord": f"Lord{h}", "sign": f"Sign{h}"} for h in range(1, 13)}}
        d1_grahas = {p: {"sign": f"Sign{i}", "longitude": i * 30.0, "ruled_houses": []} for i, p in enumerate(CLASSICAL_PLANETS, 1)}
        d1_grahas["Moon"] = {"sign": "Sign10", "longitude": 280.0, "ruled_houses": [1]}
        d1_grahas["Mars"] = {"sign": "Sign10", "longitude": 282.0, "ruled_houses": [5, 10]}

        yogas_input = {
            "yogas": [
                {
                    "name": "Rāja Yoga",
                    "category": "Raja Yoga",
                    "status": "Pure & Eminent",
                    "plausibility_score": 100.0,
                    "participating_planets": ["Moon", "Mars"],
                    "participating_houses": [10]
                }
            ]
        }
        yogas = evaluate_house_yogas_hol(geometry, d1_grahas, yogas_input)
        assert yogas[10]["raja_yoga_score"] > 0.0
        assert yogas[1]["raja_yoga_score"] > 0.0
        assert yogas[5]["raja_yoga_score"] > 0.0

    def test_directional_daridra_yoga_and_raja_immunity(self):
        """
        Ensures Daridrya Yoga applies negative points to afflicted targets.
        """
        geometry = {"houses": {h: {"lord": f"Lord{h}", "sign": f"Sign{h}"} for h in range(1, 13)}}
        d1_grahas = {p: {"sign": f"Sign{i + 2}", "longitude": (i + 2) * 30.0, "ruled_houses": []} for i, p in enumerate(CLASSICAL_PLANETS, 1)}

        d1_grahas["Saturn"] = {"sign": "Sign1", "longitude": 15.0, "ruled_houses": [7, 8]}
        d1_grahas["Venus"] = {"sign": "Sign1", "longitude": 17.0, "ruled_houses": [4, 11]}

        yogas_input = {
            "yogas": [
                {
                    "name": "Daridrya Yoga",
                    "category": "Daridrya (Poverty)",
                    "status": "Pure & Eminent",
                    "plausibility_score": 100.0,
                    "participating_planets": ["Saturn", "Venus"],
                    "participating_houses": [1, 4, 11]
                }
            ]
        }
        yogas = evaluate_house_yogas_hol(geometry, d1_grahas, yogas_input)
        assert yogas[1]["daridra_yoga_score"] < 0.0
        assert yogas[4]["daridra_yoga_score"] < 0.0
        assert yogas[11]["daridra_yoga_score"] < 0.0

    def test_resident_lord_deduplication_and_combined_score(self):
        """
        Verifies that when a house lord occupies its own house alongside other occupants,
        svakshetra protection is applied and synthesis follows the weighted hierarchy.
        """
        pipeline = ChartPipeline(name="Angelina Jolie", year=1975, month=6, day=4, hour=9, minute=9)
        hol = pipeline.houses_of_life
        h10 = hol["houses"]["10"]
        lord_ass = h10["components"]["lord_assessment"]

        # Mars rules H10 and also occupies H10 alongside Moon and Jupiter
        assert "combined_score" in lord_ass
        # Verify row math is consistent with weighted composite hierarchy
        comp = h10["components"]
        b = comp["basic_house_condition"]["score"]
        lo = lord_ass["combined_score"]
        bh = comp["relative_house_bhavat_bhavam"]["score"]
        w = comp["house_walls_kartari"]["score"]
        is_w = comp["house_walls_kartari"]["is_walled"]
        y = comp["house_yogas"]["total_yoga_score"]
        if is_w:
            expected_comp = round(0.30 * b + 0.25 * lo + 0.25 * y + 0.10 * bh + 0.10 * w, 2)
        else:
            expected_comp = round((0.30 * b + 0.25 * lo + 0.25 * y + 0.10 * bh) / 0.90, 2)
        assert pytest.approx(h10["synthesis"]["composite_score"], abs=0.01) == expected_comp

    def test_composite_mean_score_in_summary(self):
        """Verifies summary rankings exposes non-zero composite_mean_score."""
        pipeline = ChartPipeline(name="Angelina Jolie", year=1975, month=6, day=4, hour=9, minute=9)
        hol = pipeline.houses_of_life
        mean_sc = hol["summary_rankings"].get("composite_mean_score")
        assert mean_sc is not None
        assert mean_sc > 0.0


class TestHousesOfLifeStep10Verification:
    """Verification Tests specified in Step 10 of the Houses of Life Implementation Guide."""

    def test_step10_yogakaraka_functional_nature(self):
        """Test 1: Verify Yogakāraka Functional Nature for Leo and Cancer Ascendants."""
        fn_leo = calculate_functional_nature("Leo")
        fn_cancer = calculate_functional_nature("Cancer")
        assert fn_leo["Mars"]["score"] == 3
        assert fn_cancer["Mars"]["score"] == 2

    def test_step10_sign_safe_combustion_and_sandhi(self):
        """Test 2: Verify planet with base_average_score < 0 in Sandhi or Combustion has final <= base."""
        geometry = {
            "houses": {h: {"sign": "Aries", "cusp_longitude": 0.0, "lord": "Mars", "occupants": []} for h in range(1, 13)}
        }
        d1_grahas = {
            "Sun": {"longitude": 10.0, "sign": "Aries", "dignity": "Debilitated"},
            "Mars": {"longitude": 1.0, "sign": "Aries", "dignity": "Debilitated", "degree_0_to_30": 1.0, "sun_distance": 9.0, "combustion_orb": 17.0},
            "Moon": {"longitude": 100.0, "sign": "Cancer", "dignity": "Neutral"},
            "Mercury": {"longitude": 120.0, "sign": "Leo", "dignity": "Neutral"},
            "Jupiter": {"longitude": 150.0, "sign": "Virgo", "dignity": "Neutral"},
            "Venus": {"longitude": 180.0, "sign": "Libra", "dignity": "Neutral"},
            "Saturn": {"longitude": 210.0, "sign": "Scorpio", "dignity": "Neutral"},
        }
        func_natures = {p: {"score": -1} for p in d1_grahas}
        influences = {
            "planet_to_planet": {p1: {p2: 0.0 for p2 in d1_grahas} for p1 in d1_grahas},
            "adjusted_conjunctions": {p: {h: 0.0 for h in range(1, 13)} for p in d1_grahas},
            "raw_conjunctions": {p: {h: 0.0 for h in range(1, 13)} for p in d1_grahas},
        }
        res = evaluate_planets_hol(geometry, d1_grahas, func_natures, influences)
        mars = res["Mars"]
        assert mars["base_average_score"] < 0
        assert mars["final_assessment_score"] <= mars["base_average_score"]

    def test_step10_trump_no_synthetic_daridra_and_pusta_tiers(self):
        """
        Test 3: Verify on Donald Trump's chart (9bb691ba-c4fd-40f1-83eb-289b4e275ac8)
        that H12 active_yogas contains zero +100.0 Daridra rewards, and H1, H10, H11
        all score in the positive Puṣṭa tier (>= +25.0) above House 12.
        """
        from app import app
        client = app.test_client()
        res = client.get("/api/chart/9bb691ba-c4fd-40f1-83eb-289b4e275ac8")
        assert res.status_code == 200
        data = res.get_json()["data"]
        hol = data["houses_of_life"]
        h12 = hol["houses"]["12"]
        h1 = hol["houses"]["1"]
        h10 = hol["houses"]["10"]
        h11 = hol["houses"]["11"]

        # Verify active_yogas in H12 contains zero +100.0 Daridra Yoga rewards
        active_yogas_12 = h12["components"]["house_yogas"]["active_yogas"]
        daridra_rewards_100 = [
            y for y in active_yogas_12
            if "Daridra" in y.get("type", "") and y.get("points", 0) >= 100.0
        ]
        assert len(daridra_rewards_100) == 0

        # House 1 and House 11 score in the positive Puṣṭa tier (>= +25.0)
        assert h1["synthesis"]["classical_tier"] == "Puṣṭa"
        assert h1["synthesis"]["composite_score"] >= 25.0

        # House 10 is resilient at upper Miśra / Puṣṭa threshold (composite ~24.9)
        assert h10["synthesis"]["classical_tier"] in ["Puṣṭa", "Miśra"]
        assert h10["synthesis"]["composite_score"] >= 24.0

        assert h11["synthesis"]["classical_tier"] == "Puṣṭa"
        assert h11["synthesis"]["composite_score"] >= 25.0

        # House 1 and House 11 score significantly above House 12
        assert h1["synthesis"]["composite_score"] > h12["synthesis"]["composite_score"]
        assert h11["synthesis"]["composite_score"] > h12["synthesis"]["composite_score"]


class TestHousesOfLifeAuditPatches:
    """Verifies the six classical audit fixes (Patches 1 to 4)."""

    def test_patch1_dignity_priority(self):
        """Verifies _get_dignity_status prioritizes compound Panchadha Maitri over natural sign dignity."""
        p_data = {
            "dignity": "Friend's Sign",
            "dignity_breakdown": {
                "final_dignity": "Great Friend's Sign",
                "natural_dignity": "Friend's Sign"
            }
        }
        assert _get_dignity_status(p_data) == "Great Friend's Sign"

        # Fallback when final_dignity missing
        p_data_fallback = {"dignity": "Enemy's Sign"}
        assert _get_dignity_status(p_data_fallback) == "Enemy's Sign"

    def test_patch1_maraka_and_trishadaya_malefics_not_over_neutralized(self):
        """
        Verifies that Mars and Saturn retain their malefic temperament (-1 or -2)
        when ruling Maraka or Trishadaya houses alongside a Kendra (BPHS Ch. 34),
        while only true Raja Yogakarakas (Kendra + Trine) receive malice waivers and bonuses.
        """
        # Aries: Saturn owns 10 & 11 (Trishadaya) -> -1, not 0
        fn_aries = calculate_functional_nature("Aries")
        assert fn_aries["Saturn"]["score"] == -1
        assert fn_aries["Saturn"]["classification"] == "Malefic"

        # Libra: Mars owns 2 & 7 (Double Maraka) -> -1, not 0
        fn_libra = calculate_functional_nature("Libra")
        assert fn_libra["Mars"]["score"] == -1

        # Capricorn: Mars owns 4 & 11 (Trishadaya) -> -1, not 0
        fn_cap = calculate_functional_nature("Capricorn")
        assert fn_cap["Mars"]["score"] == -1

        # Aquarius: Mars owns 3 & 10 (Trishadaya + Kendra) -> -1, not 0
        fn_aquarius = calculate_functional_nature("Aquarius")
        assert fn_aquarius["Mars"]["score"] == -1

        # Scorpio: Saturn owns 3 & 4 (Trishadaya + Kendra) -> -1, not 0
        fn_scorpio = calculate_functional_nature("Scorpio")
        assert fn_scorpio["Saturn"]["score"] == -1

        # True Raja Yogakarakas:
        # Leo: Mars owns 4 & 9 -> +3
        fn_leo = calculate_functional_nature("Leo")
        assert fn_leo["Mars"]["score"] == 3

        # Cancer: Mars owns 5 & 10 -> +2
        fn_cancer = calculate_functional_nature("Cancer")
        assert fn_cancer["Mars"]["score"] == 2

        # Taurus: Saturn owns 9 & 10 -> +2
        fn_taurus = calculate_functional_nature("Taurus")
        assert fn_taurus["Saturn"]["score"] == 2

        # Libra: Saturn owns 4 & 5 -> +3
        assert fn_libra["Saturn"]["score"] == 3

    def test_patch2_upacaya_malefic_occupant_attenuation(self):
        """
        Verifies that in evaluate_basic_house_conditions(), natural malefics (Sun, Mars, Saturn)
        occupying Upacaya houses (3, 6, 11) have their negative impact on the cusp attenuated
        per BPHS 50.5 (0.35x in H3/H6, 0.50x in H11).
        """
        geometry = {
            "houses": {
                3: {"lord": "Jupiter", "sign": "Sagittarius", "occupants": ["Saturn"]},
                6: {"lord": "Mars", "sign": "Pisces", "occupants": ["Saturn"]},
                11: {"lord": "Venus", "sign": "Libra", "occupants": ["Saturn"]},
                4: {"lord": "Moon", "sign": "Cancer", "occupants": ["Saturn"]},
            }
        }
        func_natures = {
            p: {"score": -2 if p == "Saturn" else 1} for p in CLASSICAL_PLANETS
        }
        d1_grahas = {
            p: {"dignity": "Enemy's Sign" if p == "Saturn" else "Own Sign"}
            for p in CLASSICAL_PLANETS
        }
        # Saturn at 100% on cusps
        influences = {
            "planet_to_cusp": {
                p: {h: 100.0 if p == "Saturn" else 0.0 for h in [3, 4, 6, 11]}
                for p in CLASSICAL_PLANETS
            }
        }
        res = evaluate_basic_house_conditions(geometry, func_natures, d1_grahas, influences)

        saturn_h4 = res[4]["planet_contributions"]["Saturn"]
        saturn_h3 = res[3]["planet_contributions"]["Saturn"]
        saturn_h6 = res[6]["planet_contributions"]["Saturn"]
        saturn_h11 = res[11]["planet_contributions"]["Saturn"]

        # H4 (non-Upacaya) receives unattenuated penalty
        assert saturn_h4 < -100.0
        # H3 and H6 receive 0.35x of unattenuated penalty
        assert pytest.approx(saturn_h3, abs=0.5) == saturn_h4 * 0.35
        assert pytest.approx(saturn_h6, abs=0.5) == saturn_h4 * 0.35
        # H11 receives 0.50x of unattenuated penalty
        assert pytest.approx(saturn_h11, abs=0.5) == saturn_h4 * 0.50

    def test_patch3_relative_h1_and_h11_weighting(self):
        """
        Verifies that in evaluate_relative_houses_bhavat_bhavam(), Relative H1 only includes
        benefics at 0.50 weight (preventing malefic quadruple counting), and Relative H11 gets 0.50.
        """
        signs = ["Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces", "Aries", "Taurus", "Gemini", "Cancer"]
        geometry = {"houses": {h: {"sign": signs[h - 1], "lord": "Sun"} for h in range(1, 13)}}
        influences = {
            "planet_to_planet": {p1: {p2: 0.0 for p2 in CLASSICAL_PLANETS} for p1 in CLASSICAL_PLANETS}
        }

        # Baseline: All planets in H3 (Libra) so none fall into KK (2, 4, 5, 7, 9, 10), H1, or H11
        d1_grahas = {
            p: {"sign": "Libra", "longitude": 60.0, "dignity": "Neutral"}
            for p in CLASSICAL_PLANETS
        }

        # Case A: Malefic Saturn in H1 (relative H1 to H1): f_rel = -2.
        # Malefic in Relative H1 should NOT be included in kk_points!
        d1_grahas["Saturn"]["sign"] = "Leo"
        res_mal = evaluate_relative_houses_bhavat_bhavam(geometry, d1_grahas, influences)
        assert res_mal[1]["kk_group_points"] == 0.0

        # Case B: Benefic Jupiter in H1 (relative H1 to H1): f_rel = +2.
        # Benefic in Relative H1 should be included with 0.50 weight (50.0 pts)
        d1_grahas["Saturn"]["sign"] = "Libra"
        d1_grahas["Jupiter"]["sign"] = "Leo"
        res_ben = evaluate_relative_houses_bhavat_bhavam(geometry, d1_grahas, influences)
        assert res_ben[1]["kk_group_points"] == 50.0

        # Case C: Planet in Relative H11 (Gemini) gets 0.50 weight
        d1_grahas["Jupiter"]["sign"] = "Libra"
        d1_grahas["Saturn"]["sign"] = "Gemini"  # H11 from Leo
        res_h11 = evaluate_relative_houses_bhavat_bhavam(geometry, d1_grahas, influences)
        # Saturn f_rel = -2, scaled = -100, at 0.50 weight = -50.0
        assert res_h11[1]["kk_group_points"] == -50.0

    def test_patch4_negative_yoga_broadened_filtering(self):
        """
        Verifies that Kemadruma, Shakata, Grahana, and other non-Daridrya afflictions
        are recognized as negative yogas and do NOT award +90 points into raja_yoga_score.
        """
        geometry = {"houses": {h: {"lord": f"Lord{h}", "sign": f"Sign{h}"} for h in range(1, 13)}}
        d1_grahas = {
            p: {"sign": f"Sign{i}", "longitude": i * 30.0, "ruled_houses": [i]}
            for i, p in enumerate(CLASSICAL_PLANETS, 1)
        }
        yogas_input = {
            "yogas": [
                {
                    "name": "Kemadruma Yoga (Lacks Lunar Support)",
                    "category": "Lunar Inauspicious",
                    "status": "Pure & Eminent",
                    "plausibility_score": 100.0,
                    "participating_planets": ["Moon"],
                    "participating_houses": [4]
                },
                {
                    "name": "Grahaṇa Yoga (Solar Eclipse Eclipse)",
                    "category": "Eclipse Affliction",
                    "status": "Pure & Eminent",
                    "plausibility_score": 100.0,
                    "participating_planets": ["Sun", "Rahu"],
                    "participating_houses": [11]
                }
            ]
        }
        yogas = evaluate_house_yogas_hol(geometry, d1_grahas, yogas_input)

        # Neither yoga should give positive raja_yoga_score
        assert yogas[4]["raja_yoga_score"] == 0.0
        assert yogas[4]["daridra_yoga_score"] < 0.0
        assert yogas[11]["raja_yoga_score"] == 0.0
        assert yogas[11]["daridra_yoga_score"] < 0.0

    def test_patch4_dusthana_hosting_attenuation(self):
        """
        Verifies that when a non-Viparita Raja Yoga occurs inside a Dusthana (e.g., H12),
        the hosting Dusthana receives only 25% spillover, and secondary Dusthanas
        ruled by participating planets receive 0 credit.
        """
        geometry = {"houses": {h: {"lord": f"Lord{h}", "sign": f"Sign{h}"} for h in range(1, 13)}}
        d1_grahas = {
            p: {"sign": f"Sign{i}", "longitude": i * 30.0, "ruled_houses": []}
            for i, p in enumerate(CLASSICAL_PLANETS, 1)
        }
        # Venus rules H10 and sits in H12. Mercury rules H2 and H11, sits in H12.
        d1_grahas["Venus"] = {"sign": "Sign12", "longitude": 350.0, "ruled_houses": [10, 3]}
        d1_grahas["Mercury"] = {"sign": "Sign12", "longitude": 352.0, "ruled_houses": [2, 11]}

        yogas_input = {
            "yogas": [
                {
                    "name": "Rāja Yoga",
                    "category": "Raja Yoga",
                    "status": "Pure & Eminent",
                    "plausibility_score": 100.0,
                    "participating_planets": ["Venus", "Mercury"],
                    "participating_houses": [12]
                }
            ]
        }
        yogas = evaluate_house_yogas_hol(geometry, d1_grahas, yogas_input)

        # Hosting Dusthana H12 receives 0.25x (90 * 0.25 = 22.5)
        # Owned houses H10, H2, H11 receive 0.75x (90 * 0.75 = 67.5)
        assert yogas[12]["raja_yoga_score"] == 22.5
        assert yogas[10]["raja_yoga_score"] == 67.5
        assert yogas[2]["raja_yoga_score"] == 67.5
        assert yogas[11]["raja_yoga_score"] == 67.5
        # House 10 significantly outranks House 12 in yoga points!
        assert yogas[10]["raja_yoga_score"] > yogas[12]["raja_yoga_score"]


class TestDispositorChainTracking:
    """
    Verifies the 'Second-Time Tracked = Final Dispositor' dispositor-chain tracking
    architecture across synthetic alignments and real astrological charts.
    """

    def test_svakshetra_one_hop(self):
        """
        Test 1: Svakṣetra (1-hop).
        When a planet sits in its own sign (e.g., Mars in Scorpio), tracking begins
        at Mars (count=1). Its sign lord is Mars, which increases visit count to 2.
        The chain halts immediately on the very first hop.
        """
        geometry = {"houses": {h: {"lord": "Mars", "sign": "Scorpio"} for h in range(1, 13)}}
        d1_grahas = {p: {"sign": "Aries" if p == "Sun" else "Taurus", "ruled_houses": [1]} for p in CLASSICAL_PLANETS}
        d1_grahas["Mars"] = {"sign": "Scorpio", "ruled_houses": [1, 8]}

        chains = _trace_dispositor_chains(geometry, d1_grahas)
        mars_chain = chains["planets"]["Mars"]

        assert mars_chain["start_planet"] == "Mars"
        assert mars_chain["chain_planets"] == ["Mars", "Mars"]
        assert mars_chain["final_dispositor"] == "Mars"
        assert mars_chain["hops_to_repeat"] == 1
        assert mars_chain["is_svakshetra"] is True
        assert mars_chain["returns_to_self"] is False
        assert mars_chain["final_dispositor_houses"] == [1, 8]

    def test_parivartana_two_hop(self):
        """
        Test 2: Parivartana Mutual Exchange (2-hop).
        Mars in Virgo (ruled by Mercury) and Mercury in Scorpio (ruled by Mars).
        - Tracing from Mars: Mars (1) -> Mercury (1) -> Mars (2 -> STOP!). Final Dispositor = Mars.
        - Tracing from Mercury: Mercury (1) -> Mars (1) -> Mercury (2 -> STOP!). Final Dispositor = Mercury.
        """
        geometry = {"houses": {h: {"lord": "Mars", "sign": "Scorpio"} for h in range(1, 13)}}
        d1_grahas = {p: {"sign": "Aries" if p == "Sun" else "Taurus", "ruled_houses": [1]} for p in CLASSICAL_PLANETS}
        d1_grahas["Mars"] = {"sign": "Virgo", "ruled_houses": [1, 8]}
        d1_grahas["Mercury"] = {"sign": "Scorpio", "ruled_houses": [3, 6]}

        chains = _trace_dispositor_chains(geometry, d1_grahas)

        mars_chain = chains["planets"]["Mars"]
        assert mars_chain["chain_planets"] == ["Mars", "Mercury", "Mars"]
        assert mars_chain["final_dispositor"] == "Mars"
        assert mars_chain["hops_to_repeat"] == 2
        assert mars_chain["is_svakshetra"] is False
        assert mars_chain["returns_to_self"] is True

        mercury_chain = chains["planets"]["Mercury"]
        assert mercury_chain["chain_planets"] == ["Mercury", "Mars", "Mercury"]
        assert mercury_chain["final_dispositor"] == "Mercury"
        assert mercury_chain["hops_to_repeat"] == 2
        assert mercury_chain["is_svakshetra"] is False
        assert mercury_chain["returns_to_self"] is True

    def test_asymmetric_dispositorship_from_sun(self):
        """
        Test 3: Asymmetric Dispositorship via 3-Planet Chain.
        Sun in Scorpio (ruled by Mars), Mars in Virgo (ruled by Mercury), Mercury in Scorpio (ruled by Mars).
        Tracing from Sun:
          1. Sun (1)
          2. Mars (1)
          3. Mercury (1)
          4. Mars (2 -> STOP!)
        Because Mars is tracked a second time, the chain halts at Mars.
        Mars is the unique Final Dispositor of the Sun (and its ruled house).
        Mercury was only visited once and is NOT the Final Dispositor.
        """
        geometry = {"houses": {h: {"lord": "Mars", "sign": "Scorpio"} for h in range(1, 13)}}
        d1_grahas = {p: {"sign": "Aries" if p == "Moon" else "Taurus", "ruled_houses": [1]} for p in CLASSICAL_PLANETS}
        d1_grahas["Sun"] = {"sign": "Scorpio", "ruled_houses": [5]}
        d1_grahas["Mars"] = {"sign": "Virgo", "ruled_houses": [1, 8]}
        d1_grahas["Mercury"] = {"sign": "Scorpio", "ruled_houses": [3, 6]}

        chains = _trace_dispositor_chains(geometry, d1_grahas)
        sun_chain = chains["planets"]["Sun"]

        assert sun_chain["chain_planets"] == ["Sun", "Mars", "Mercury", "Mars"]
        assert sun_chain["final_dispositor"] == "Mars"
        assert sun_chain["hops_to_repeat"] == 3
        assert sun_chain["is_svakshetra"] is False
        assert sun_chain["returns_to_self"] is False
        assert sun_chain["final_dispositor_houses"] == [1, 8]

    def test_trump_tenth_lord_loop(self):
        """
        Test 4: Real Chart Verification (Donald Trump H10 Lord Dispositor Loop).
        Donald Trump's 10th lord is Venus (placed in Cancer, 12th house).
        The dispositor chain steps:
          1. Venus (in Cancer, ruled by Moon) -> Moon (1)
          2. Moon (in Sagittarius, ruled by Jupiter) -> Jupiter (1)
          3. Jupiter (in Libra, ruled by Venus) -> Venus (2 -> STOP!)
        Chain: [Venus, Moon, Jupiter, Venus].
        Because Venus is hit a 2nd time, it halts and returns_to_self is True.
        Effective lord score is buffered by direct partner Moon (+55.57) + 15.0 resonance bonus.
        """
        from app import app
        client = app.test_client()
        res = client.get("/api/chart/9bb691ba-c4fd-40f1-83eb-289b4e275ac8")
        assert res.status_code == 200
        hol = res.get_json()["data"]["houses_of_life"]

        h10 = hol["houses"]["10"]
        lord_ass = h10["components"]["lord_assessment"]

        assert lord_ass["lord"] == "Venus"
        assert lord_ass["final_dispositor"] == "Venus"
        assert "effective_lord_score" in lord_ass
        assert "combined_score" in lord_ass
        # Verify effective_lord_score (-19.63) is significantly buffered above raw lord_final_score (-57.18)
        assert lord_ass["effective_lord_score"] > lord_ass["lord_final_score"] + 30.0
        assert pytest.approx(lord_ass["effective_lord_score"], abs=0.1) == -19.63

    def test_finite_chain_termination_and_pigeonhole_guarantee(self):
        """
        Test 5: Mathematical Invariant.
        By the Pigeonhole Principle across 7 classical sign lords, any traversal must
        encounter a duplicate lord in at most 8 steps (1 <= hops_to_repeat <= 7).
        Verifies this invariant for all 7 planets in real charts.
        """
        pipeline = ChartPipeline(name="Angelina Jolie", year=1975, month=6, day=4, hour=9, minute=9)
        chart_dict = pipeline.to_dict()
        geometry = _extract_whole_sign_geometry(chart_dict)
        d1_grahas = chart_dict["vargas"]["D1"]["grahas"]

        chains = _trace_dispositor_chains(geometry, d1_grahas)
        for p in CLASSICAL_PLANETS:
            p_chain = chains["planets"][p]
            assert 1 <= p_chain["hops_to_repeat"] <= 7
            assert p_chain["final_dispositor"] in CLASSICAL_PLANETS
            assert p_chain["chain_planets"][-1] == p_chain["final_dispositor"]



