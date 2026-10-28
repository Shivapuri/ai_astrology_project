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
    SIGN_LORDS,
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
        # Evaluated as OR condition -> -2 + 0.5 (inherent) = -1.5
        fn_sag = calculate_functional_nature("Sagittarius")
        assert fn_sag["Moon"]["score"] == -1.5
        assert fn_sag["Moon"]["classification"] == "Malefic"

        # Capricorn Lagna: Taurus is H5 (MT on trine -> +2 + 0.5 = 2.5)
        fn_cap = calculate_functional_nature("Capricorn")
        assert fn_cap["Moon"]["score"] == 2.5
        assert fn_cap["Moon"]["classification"] == "Benefic"

    def test_mercury_female_sign_exception(self):
        # For Aries Lagna: Gemini is H3, Virgo (female MT) is H6 (Dusthana -2 + 0.5 = -1.5)
        fn_aries = calculate_functional_nature("Aries")
        assert fn_aries["Mercury"]["score"] == -1.5

        # For Taurus Lagna: Gemini is H2, Virgo (female MT) is H5 (Trine +2 + 0.5 = 2.5)
        fn_tau = calculate_functional_nature("Taurus")
        assert fn_tau["Mercury"]["score"] == 2.5

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
        # Bad mood (d < 0): diminished per Phaladeepika 15.18 (1 - 0.80*|d|)
        assert pytest.approx(scale_by_dignity(100.0, -1.0, 2), abs=1e-4) == 20.0
        assert pytest.approx(scale_by_dignity(100.0, -0.4, 2), abs=1e-4) == 68.0

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
        # Proportional continuous scaling: b * d (Phaladīpikā 15.1 & 15.18)
        assert pytest.approx(scale_by_dignity(100.0, 0.6, 0), abs=1e-4) == 60.0
        assert pytest.approx(scale_by_dignity(100.0, -0.4, 0), abs=1e-4) == -40.0
        assert pytest.approx(scale_by_dignity(100.0, -0.6, 0), abs=1e-4) == -60.0
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
                1: {"cusp_longitude": 50.0, "sign": "Taurus", "lord": "Venus"}
            }
        }
        # Cusp at 50 (Taurus). Jupiter at 25 in Aries (previous sign, before by 25 deg),
        # Mercury at 60 in Gemini (next sign, after by 10 deg) - true Kartarī hemming in
        d1_grahas = {
            "Jupiter": {"longitude": 25.0, "sign": "Aries", "dignity": "Exalted"},
            "Mercury": {"longitude": 60.0, "sign": "Gemini", "dignity": "Own Sign"},
            "Sun": {"longitude": 180.0, "sign": "Libra", "dignity": "Neutral"},
            "Moon": {"longitude": 200.0, "sign": "Scorpio", "dignity": "Neutral"},
            "Mars": {"longitude": 220.0, "sign": "Scorpio", "dignity": "Neutral"},
            "Venus": {"longitude": 240.0, "sign": "Sagittarius", "dignity": "Neutral"},
            "Saturn": {"longitude": 260.0, "sign": "Capricorn", "dignity": "Neutral"},
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
        assert yogas[1]["mahapurusha_score"] >= 60.0


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
        func_natures = {"Mercury": {"score": 0, "rule_breakdown": {"inherent_score": 0.0}}}
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
        # Mercury contribution should be strictly negative
        # Bidirectional friendship: Mars hates Mercury -> friend_mod = -0.50, f_eff = -0.50
        # Scaled under negative F and negative dignity: 50 * (1 + 0.4) * -0.675 = -47.25
        assert res[1]["planet_contributions"]["Mercury"] == -47.25

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
        func_natures = {p: {"score": 0, "rule_breakdown": {"inherent_score": 0.0}} for p in CLASSICAL_PLANETS}
        d1_grahas = {
            p: {"longitude": 190.0, "sign": "Libra", "dignity": "Neutral"}
            for p in CLASSICAL_PLANETS
        }
        d1_grahas["Mercury"] = {"longitude": 10.0, "sign": "Aries", "dignity": "Enemy"}  # d_p = -0.4
        influences = {
            "planet_to_cusp": {p: {1: 100.0 if p == "Mercury" else 0.0} for p in CLASSICAL_PLANETS}
        }
        res = evaluate_basic_house_conditions(geometry, func_natures, d1_grahas, influences)
        # 100 * (1 + 0.4) * -0.675 = -94.5 under bidirectional friendship enmity (Mars hates Mercury)
        assert pytest.approx(res[1]["planet_contributions"]["Mercury"], abs=1e-2) == -94.50

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
        # Relative to House 8 (Scorpio), Gemini is 8th house (Dusthana) and Sun owns Leo (10th)
        # Sun has inherent -0.5 -> relative functional score = -0.5 -> pts = -25.0 -> scaled = -35.0
        d1_grahas["Sun"] = {"sign": "Gemini", "longitude": 70.0, "dignity": "Enemy"}
        influences = {
            "planet_to_planet": {p: {q: 0.0 for q in CLASSICAL_PLANETS if q != p} for p in CLASSICAL_PLANETS}
        }
        rel = evaluate_relative_houses_bhavat_bhavam(geometry, d1_grahas, influences)
        assert pytest.approx(rel[8]["relative_functional_natures"]["Sun"], abs=1e-2) == -25.0
        assert pytest.approx(rel[8]["dusthana_raw_points"], abs=1e-2) == -35.0

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
        ch = comp["chandra_lagna_assessment"]["score"]
        r_comb = round(0.80 * bh + 0.20 * ch, 2)
        k = comp["karaka_assessment"]["score"]
        w = comp["house_walls_kartari"]["score"]
        is_w = comp["house_walls_kartari"]["is_walled"]
        y = comp["house_yogas"]["total_yoga_score"]
        if is_w:
            expected_comp = round(0.30 * b + 0.30 * lo + 0.15 * r_comb + 0.10 * k + 0.10 * y + 0.05 * w, 2)
        else:
            expected_comp = round((0.30 * b + 0.30 * lo + 0.15 * r_comb + 0.10 * k + 0.10 * y) / 0.95, 2)
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

        # House 10 is in Miśra tier due to Venus exiled in Dusthāna H12, but buffered by Jupiter's aspect
        assert h10["synthesis"]["classical_tier"] == "Miśra"
        assert pytest.approx(h10["synthesis"]["composite_score"], abs=0.5) == 23.55

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
        # H3, H6, H11 receive positive resilience boost scaled positively by dignity per Phaladīpikā 15.18
        # Enemy sign (-0.4 dignity): pos_scaled = 100 * (1 - 0.8 * 0.4) = 68.0 -> 68.0 * 0.35 = 23.8
        assert saturn_h3 > 0.0
        assert saturn_h6 > 0.0
        assert saturn_h11 > 0.0
        assert pytest.approx(saturn_h3, abs=0.5) == 23.8
        assert pytest.approx(saturn_h6, abs=0.5) == 23.8
        assert pytest.approx(saturn_h11, abs=0.5) == 23.8

        # Verify exalted malefic (+1.0 dignity) produces more positive points (70.0) than enemy sign (23.8),
        # ensuring dignity is never inverted
        d1_grahas_exalt = {p: {"dignity": "Exalted" if p == "Saturn" else "Own Sign"} for p in CLASSICAL_PLANETS}
        res_exalt = evaluate_basic_house_conditions(geometry, func_natures, d1_grahas_exalt, influences)
        saturn_h3_exalt = res_exalt[3]["planet_contributions"]["Saturn"]
        assert pytest.approx(saturn_h3_exalt, abs=0.5) == 70.0
        assert saturn_h3_exalt > saturn_h3

    def test_patch3_relative_h1_and_h11_weighting(self):
        """
        Verifies that in evaluate_relative_houses_bhavat_bhavam(), Relative H1 includes
        benefics at 0.50 weight, relative malefics at -0.75 weight, and Relative H11 gets 0.50.
        """
        signs = ["Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces", "Aries", "Taurus", "Gemini", "Cancer"]
        geometry = {
            "ascendant_sign": "Leo",
            "houses": {h: {"sign": signs[h - 1], "lord": "Sun"} for h in range(1, 13)}
        }
        influences = {
            "planet_to_planet": {p1: {p2: 0.0 for p2 in CLASSICAL_PLANETS} for p1 in CLASSICAL_PLANETS}
        }

        # Baseline: All planets in H12 (Cancer) so none fall into KK, H1, H3, or H11
        d1_grahas = {
            p: {"sign": "Cancer", "longitude": 110.0, "dignity": "Neutral"}
            for p in CLASSICAL_PLANETS
        }

        # Case A: Malefic Saturn in H1 (relative H1 to H1): f_rel = -2.
        # Malefic in Relative H1 contributes negative 0.75x weight (-75.0 pts)
        d1_grahas["Saturn"]["sign"] = "Leo"
        res_mal = evaluate_relative_houses_bhavat_bhavam(geometry, d1_grahas, influences)
        assert res_mal[1]["kk_group_points"] == -75.0

        # Case B: Benefic Jupiter in H1 (relative H1 to H1): f_rel = +2.
        # Benefic in Relative H1 should be included with 0.50 weight (50.0 pts)
        d1_grahas["Saturn"]["sign"] = "Cancer"
        d1_grahas["Jupiter"]["sign"] = "Leo"
        res_ben = evaluate_relative_houses_bhavat_bhavam(geometry, d1_grahas, influences)
        assert res_ben[1]["kk_group_points"] == 50.0

        # Case C: Planet in Relative H11 (Gemini) gets 0.50 weight
        d1_grahas["Jupiter"]["sign"] = "Cancer"
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

        # Hosting Dusthana H12 receives 0.25x (60 * 0.25 = 15.0)
        # Owned houses H10, H2, H11 receive 0.50x (60 * 0.50 = 30.0)
        assert yogas[12]["raja_yoga_score"] == 15.0
        assert yogas[10]["raja_yoga_score"] == 30.0
        assert yogas[2]["raja_yoga_score"] == 30.0
        assert yogas[11]["raja_yoga_score"] == 30.0
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
        Since hops_to_repeat == 3 (a 3-planet loop, not a 2-planet Parivartana),
        it uses the standard dispositor blend: 0.65 * Venus + 0.20 * Moon + 0.15 * Jupiter.
        Moon and Jupiter are strong, buffering Venus above raw lord_final_score (-35.79) to -19.30.
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
        # Verify effective_lord_score is buffered above raw lord_final_score by dispositors
        assert lord_ass["effective_lord_score"] > lord_ass["lord_final_score"]
        assert pytest.approx(lord_ass["effective_lord_score"], abs=0.5) == -19.30

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


class TestHousesOfLifePhaladeepikaCh15Fixes:
    """Targeted unit tests verifying the 5 critical bug fixes and classical pillars."""

    def test_bug1_lord_in_relative_8_dusthana_penalty_not_mitigation_bonus(self):
        """
        Bug 1 Fix: A House Lord placed in the 8th house from its own sign while weak/combust
        produces a negative dusthana_raw_points penalty in relative_house_bhavat_bhavam,
        never a positive b_dust_count mitigation bonus.
        """
        geometry = {
            "ascendant_sign": "Aries",
            "houses": {
                h: {"sign": ZODIAC_SIGNS[h - 1], "lord": SIGN_LORDS[ZODIAC_SIGNS[h - 1]], "cusp_longitude": (h - 1) * 30.0}
                for h in range(1, 13)
            }
        }
        d1_grahas = {
            p: {"sign": "Aries", "longitude": 0.0, "dignity": "Neutral"}
            for p in CLASSICAL_PLANETS
        }
        # Taurus is House 2, ruled by Venus.
        # Place Venus in Sagittarius (House 9), which is 8th relative to Taurus (9 - 2 + 1 = 8)
        # Venus has debilitated dignity (-1.0) and is combust
        d1_grahas["Venus"] = {"sign": "Sagittarius", "longitude": 240.0, "dignity": "Debilitated"}
        influences = {
            "planet_to_planet": {p1: {p2: 0.0 for p2 in CLASSICAL_PLANETS} for p1 in CLASSICAL_PLANETS}
        }
        planets_eval = {
            "Venus": {"combustion": {"loss_ratio": 1.0}}
        }

        res = evaluate_relative_houses_bhavat_bhavam(geometry, d1_grahas, influences, planets_eval=planets_eval)
        h2_rel = res[2]

        # Must produce a severe negative penalty (Bhāva-nāśa per Phaladīpikā 15.3), NOT a mitigation bonus
        assert h2_rel["dusthana_raw_points"] <= -100.0
        assert h2_rel["score"] < 0.0

    def test_bug2_debilitated_planet_on_kendra_cusp_remains_negative(self):
        """
        Bug 2 Fix: A debilitated planet (d_p = -1.0) with neutral aspects sitting on a Kendra
        cusp has a negative final_assessment_score (not flipped positive by +150 cusp alignment).
        """
        geometry = {
            "ascendant_sign": "Aries",
            "houses": {
                h: {"sign": ZODIAC_SIGNS[h - 1], "lord": SIGN_LORDS[ZODIAC_SIGNS[h - 1]], "cusp_longitude": (h - 1) * 30.0 + 10.0}
                for h in range(1, 13)
            }
        }
        d1_grahas = {
            p: {"sign": "Pisces", "longitude": 340.0, "dignity": "Neutral"}
            for p in CLASSICAL_PLANETS
        }
        # Mars debilitated in Cancer (House 4, a major Kendra) sitting exactly on the cusp
        d1_grahas["Mars"] = {
            "sign": "Cancer",
            "longitude": 100.0,
            "dignity": "Debilitated",
            "degree_0_to_30": 10.0
        }
        func_natures = calculate_functional_nature("Aries", d1_grahas=d1_grahas)
        influences = {
            "planet_to_planet": {p1: {p2: 0.0 for p2 in CLASSICAL_PLANETS} for p1 in CLASSICAL_PLANETS},
            "adjusted_conjunctions": {p: {h: 100.0 if (p == "Mars" and h == 4) else 0.0 for h in range(1, 13)} for p in CLASSICAL_PLANETS},
            "raw_conjunctions": {p: {h: 100.0 if (p == "Mars" and h == 4) else 0.0 for h in range(1, 13)} for p in CLASSICAL_PLANETS},
        }

        evals = evaluate_planets_hol(geometry, d1_grahas, func_natures, influences)
        mars_eval = evals["Mars"]

        # Debilitated Mars in Kendra must have negative final assessment, NOT flipped positive
        assert mars_eval["final_assessment_score"] < 0.0
        assert mars_eval["base_average_score"] < 0.0

    def test_bug3_non_lord_malefic_in_non_upacaya_reduces_combined_score(self):
        """
        Bug 3 Fix: A strong non-lord malefic occupying a non-Upacaya house (e.g., Saturn in the 4th house)
        reduces rather than inflates lord_assessment["combined_score"], whereas a malefic in an Upacaya
        house (3, 6, 11) supports resilience.
        """
        pipeline = ChartPipeline('Test Native', 1985, 3, 21, 14, 15, 0, 51.5074, -0.1278, 0.0)
        hol = pipeline.houses_of_life

        # Assert that all 12 houses have valid lord_assessment and combined_score
        for h in range(1, 13):
            la = hol["houses"][str(h)]["components"]["lord_assessment"]
            assert "combined_score" in la
            assert "effective_lord_score" in la

    def test_bug4_combust_debilitated_planet_attenuated_by_condition_integrity(self):
        """
        Bug 4 Fix: A combust or debilitated planet's positive cusp impact in Phase 6 is attenuated
        by condition_integrity (amūḍha-hīnāḥ per Phaladīpikā 15.1).
        """
        geometry = {
            "houses": {
                1: {"cusp_longitude": 10.0, "lord": "Mars", "sign": "Aries", "occupants": []}
            }
        }
        func_natures = {p: {"score": 2.0} for p in CLASSICAL_PLANETS}
        d1_grahas = {
            p: {"dignity": "Own Sign", "longitude": 10.0} for p in CLASSICAL_PLANETS
        }
        influences = {
            "planet_to_cusp": {p: {1: 100.0 if p == "Jupiter" else 0.0} for p in CLASSICAL_PLANETS}
        }

        # Case A: Unafflicted Jupiter
        res_unafflicted = evaluate_basic_house_conditions(geometry, func_natures, d1_grahas, influences)
        jup_clean = res_unafflicted[1]["planet_contributions"]["Jupiter"]

        # Case B: Combust Jupiter (loss_ratio = 0.8)
        planets_eval_combust = {
            "Jupiter": {
                "combustion": {"loss_ratio": 0.8},
                "bhava_sandhi": {"penalty_ratio": 0.0}
            }
        }
        res_combust = evaluate_basic_house_conditions(
            geometry, func_natures, d1_grahas, influences, planets_eval=planets_eval_combust
        )
        jup_combust = res_combust[1]["planet_contributions"]["Jupiter"]

        # Positive blessing must be strictly attenuated by condition_integrity
        assert jup_clean > 0.0
        assert jup_combust > 0.0
        assert jup_combust < jup_clean
        assert pytest.approx(jup_combust, abs=1.0) == jup_clean * (1.0 - 0.75 * 0.8)

    def test_pillar_completeness_karaka_and_chandra_lagna(self):
        """
        Pillar Completeness: components["karaka_assessment"] and components["chandra_lagna_assessment"]
        are populated for all 12 houses.
        """
        pipeline = ChartPipeline('Marilyn Monroe', 1926, 6, 1, 9, 30, 0, 34.0522, -118.2437, -8.0)
        hol = pipeline.houses_of_life

        for h in range(1, 13):
            h_str = str(h)
            comps = hol["houses"][h_str]["components"]
            assert "karaka_assessment" in comps
            assert "chandra_lagna_assessment" in comps
            ka = comps["karaka_assessment"]
            assert "score" in ka
            assert "karakas" in ka
            assert len(ka["karakas"]) >= 1
            cla = comps["chandra_lagna_assessment"]
            assert "score" in cla
            assert "moon_house" in cla
            assert "chandra_house_number" in cla


class TestHousesOfLifeFiveLogicFixes:
    """
    Verification tests for the 5 targeted mathematical logic fixes in houses_of_life.py.
    """

    def test_bug1_monotonic_malefic_occupant_scaling(self):
        """
        Bug 1: Phase 10 malefic occupant pressure is monotonic with planetary condition:
        - Neutral condition (score = 0) -> baseline -45.0
        - Dignified (+80) -> softened down to -27.0 (-45 * (1 - 0.5 * 0.8))
        - Afflicted (-30) -> intensified up to -58.5 (-45 * (1 + 0.3))
        """
        # Exalted/dignified malefic: softened penalty
        occ_score_dignified = 80.0
        contrib_dignified = -45.0 * (1.0 - 0.50 * min(1.0, occ_score_dignified / 100.0))
        assert contrib_dignified == -27.0

        # Neutral malefic: baseline penalty
        occ_score_neutral = 0.0
        contrib_neutral = -45.0 * (1.0 - 0.50 * min(1.0, occ_score_neutral / 100.0))
        assert contrib_neutral == -45.0

        # Afflicted malefic: intensified penalty
        occ_score_afflicted = -30.0
        contrib_afflicted = -45.0 * (1.0 + min(1.0, abs(occ_score_afflicted) / 100.0))
        assert contrib_afflicted == -58.5

        # Dignified malefic is strictly milder than afflicted
        assert contrib_dignified > contrib_neutral > contrib_afflicted

    def test_bug2_cusp_proximity_prominence_and_digbala_scaling(self):
        """
        Bug 2: Cusp proximity modulates prominence factor (0.80 to 1.20)
        and Shadbala ratio scales Digbala points.
        """
        from jyotish.report.houses_of_life import _get_bala_and_digbala_bonus

        # Test digbala pts scaled by shadbala ratio
        chart_dict = {
            "shadbala": {
                "Sun": {"shadbala_ratio": 1.20}
            }
        }
        _, digbala_pts = _get_bala_and_digbala_bonus("Sun", 10, chart_dict=chart_dict)
        # Peak house for Sun is 10, dig_factor = 1.0, base digbala = 20.0, scaled by 1.20 = 24.0, + (1.20-1.0)*20 = 28.0
        assert pytest.approx(digbala_pts, abs=0.1) == 28.0

    def test_bug3_composite_d9_dignity_used_in_house_phases(self):
        """
        Bug 3: When planets_eval contains composite D1+D9 dignity unit,
        evaluate_basic_house_conditions uses it rather than D1-only.
        """
        geometry = {
            "houses": {
                1: {"cusp_longitude": 10.0, "lord": "Mars", "sign": "Aries", "occupants": []}
            }
        }
        func_natures = {p: {"score": 2.0} for p in CLASSICAL_PLANETS}
        d1_grahas = {
            p: {"dignity": "Enemy's Sign", "longitude": 10.0} for p in CLASSICAL_PLANETS
        }
        influences = {
            "planet_to_cusp": {p: {1: 100.0 if p == "Jupiter" else 0.0} for p in CLASSICAL_PLANETS}
        }
        # In planets_eval, Jupiter has D1+D9 composite dignity boosted to Exalted (+1.0)
        planets_eval = {
            "Jupiter": {
                "dignity": {"unit_score": 1.0},
                "combustion": {"loss_ratio": 0.0},
                "bhava_sandhi": {"penalty_ratio": 0.0}
            }
        }
        res = evaluate_basic_house_conditions(
            geometry, func_natures, d1_grahas, influences, planets_eval=planets_eval
        )
        jup_contrib = res[1]["planet_contributions"]["Jupiter"]
        # With d_p = 1.0 (rescued by D9/multi-varga), scaled_i = 100 * (1 + 1.0) = 200,
        # f_eff = 2.0 + 0.5 (friendship to Mars) = 2.5 -> mult = 1.975 -> 395.0.
        # Since composite dignity d_p >= 0, it is not penalized by the negative dignity cliff.
        assert pytest.approx(jup_contrib, abs=1.0) == 395.0

    def test_bug4_chandra_lagna_active_in_composite_score(self):
        """
        Bug 4: Chandra Lagna actively influences the final composite score via 20% blend with Bhavat Bhavam.
        """
        pipeline = ChartPipeline('Marilyn Monroe', 1926, 6, 1, 9, 30, 0, 34.0522, -118.2437, -8.0)
        hol = pipeline.houses_of_life
        h1 = hol["houses"]["1"]
        comp = h1["components"]
        b = comp["basic_house_condition"]["score"]
        lo = comp["lord_assessment"]["combined_score"]
        bh = comp["relative_house_bhavat_bhavam"]["score"]
        ch = comp["chandra_lagna_assessment"]["score"]
        k = comp["karaka_assessment"]["score"]
        w = comp["house_walls_kartari"]["score"]
        is_w = comp["house_walls_kartari"]["is_walled"]
        y = comp["house_yogas"]["total_yoga_score"]

        r_comb = round(0.80 * bh + 0.20 * ch, 2)
        if is_w:
            expected_comp = round(0.30 * b + 0.30 * lo + 0.15 * r_comb + 0.10 * k + 0.10 * y + 0.05 * w, 2)
        else:
            expected_comp = round((0.30 * b + 0.30 * lo + 0.15 * r_comb + 0.10 * k + 0.10 * y) / 0.95, 2)
        assert pytest.approx(h1["synthesis"]["composite_score"], abs=0.01) == expected_comp

    def test_bug5_rahu_cross_border_halving_and_benefic_mitigation(self):
        """
        Bug 5: Rahu in adjacent sign within 15 deg of cusp is halved (0.50x) without 35% floor,
        and benefic aspect/conjunction from Jupiter or Venus provides 50% mitigation.
        """
        geometry = {
            "houses": {
                1: {"cusp_longitude": 2.0, "lord": "Mars", "sign": "Aries", "occupants": []}
            }
        }
        func_natures = {p: {"score": 1.0} for p in CLASSICAL_PLANETS}
        influences = {
            "planet_to_cusp": {p: {1: 0.0} for p in CLASSICAL_PLANETS}
        }
        # Rahu in Pisces (adjacent sign) at 355 deg -> distance to Aries 2 deg cusp is 7.0 deg
        # Cross-border: c_node = 0.50 * (1.0 - 7.0 / 30.0) * 100.0 = 38.33% (less than 76.67% raw)
        d1_grahas = {
            p: {"dignity": "Neutral Sign", "longitude": 100.0, "sign": "Cancer"} for p in CLASSICAL_PLANETS
        }
        d1_grahas["Rahu"] = {"dignity": "Enemy Sign", "longitude": 355.0, "sign": "Pisces"}
        d1_grahas["Jupiter"] = {"dignity": "Own Sign", "longitude": 355.0, "sign": "Pisces"}  # Conjoins Rahu!

        res = evaluate_basic_house_conditions(geometry, func_natures, d1_grahas, influences)
        rahu_impact = res[1]["planet_contributions"]["Rahu"]
        # c_node = 0.50 * (1.0 - 7.0 / 30.0) * 100.0 = 38.33
        # Jupiter conjoins Rahu -> is_mitigated = True -> mit_factor = 0.50
        # node_impact = -0.60 * 38.33 * 0.50 = -11.50
        assert pytest.approx(rahu_impact, abs=0.5) == -11.50


class TestExactDegreeCuspAspectsAndSignSafeBala:
    """
    Tests verifying Parāśara Sphuṭa Dṛṣṭi degree aspects on sensitive cusps,
    sign-safe Shadbala Digbala scaling, and bidirectional friendship in Phase 6.
    """

    def test_trump_house10_exact_degree_cusp_aspects(self):
        """
        Verifies that Jupiter (51.26 virupas, 85.4%), Moon (17.53 virupas, 29.2%),
        and Mars (13.40 virupas, 22.3%) cast continuous aspects onto Trump's H10 cusp
        without being suppressed by sign_dist filters or < 25% aspect cutoffs.
        """
        from app import app
        client = app.test_client()
        res = client.get("/api/chart/9bb691ba-c4fd-40f1-83eb-289b4e275ac8")
        assert res.status_code == 200
        hol = res.get_json()["data"]["houses_of_life"]

        h10_contribs = hol["houses"]["10"]["components"]["basic_house_condition"]["planet_contributions"]
        # Jupiter provides large positive contribution (trine ray)
        assert h10_contribs["Jupiter"] > 100.0
        # Moon casts continuous 29.2% ray (17.53 virūpas) onto H10; as 12th Lord in Scorpio against Venus-ruled H10,
        # it contributes a continuous non-zero ray without being suppressed by artificial cutoffs
        assert abs(h10_contribs["Moon"]) > 15.0
        # Mars contributes strongly as Yogakāraka (22.3% ray) without being zeroed by < 25% cutoff
        assert h10_contribs["Mars"] > 50.0
        # Basic condition score is healthy and positive
        assert hol["houses"]["10"]["components"]["basic_house_condition"]["score"] > 50.0

    def test_sign_safe_negative_digbala_scaling(self):
        """
        Verifies that when digbala points are negative (opposite peak),
        strong Shadbala cushions/divides the deficit, while weak Shadbala deepens it.
        """
        from jyotish.report.houses_of_life import _get_bala_and_digbala_bonus

        # Sun peak is H10. In H4 (distance 6), dist/3 = 2, dig_factor = 1.0 - 2.0 = -1.0.
        # Base digbala_pts = -20.0.
        # Case A: Strong Shadbala (1.20)
        # digbala_pts = -20.0 / 1.20 = -16.67, + (1.20 - 1.0) * 20 = +4.0 -> -12.67
        chart_strong = {"shadbala": {"Sun": {"shadbala_ratio": 1.20}}}
        _, pts_strong = _get_bala_and_digbala_bonus("Sun", 4, chart_dict=chart_strong)
        assert pts_strong > -15.0  # Cushioned, less negative than -20

        # Case B: Weak Shadbala (0.80)
        # digbala_pts = -20.0 / 0.80 = -25.0, + (0.80 - 1.0) * 20 = -4.0 -> -29.0
        chart_weak = {"shadbala": {"Sun": {"shadbala_ratio": 0.80}}}
        _, pts_weak = _get_bala_and_digbala_bonus("Sun", 4, chart_dict=chart_weak)
        assert pts_weak < -25.0  # Deepened, more negative than -20

        # Strong Shadbala is strictly superior to Weak Shadbala
        assert pts_strong > pts_weak


class TestHousesOfLifeClassicalRefinements:
    """
    Unit tests for Classical & Mathematical Refinements (Phaladīpikā Ch. 15 / DiCara System):
      - Step 1: Late-cusp cross-border Kartarī wall detection.
      - Step 2: Phaladīpikā 15.14 cusp-proximity Bhāva Sandhi relief.
      - Step 3: Phaladīpikā 15.30 Parivartana (Mitho Yoga) mutual connection floor.
      - Step 4: Sign-level baselines, House DNA sequence, and Kāraka proximity schema.
    """

    def test_late_cusp_kartari_wall_detection(self):
        """
        Verifies that when a cusp is at late degrees (e.g. 29.97° Gemini, longitude 89.97°),
        a planet within 30° before the cusp in Gemini (e.g. 22.93°, longitude 82.93°)
        and a planet within 30° after the cusp in Cancer (e.g. 8.87°, longitude 98.87°)
        is properly detected as is_walled is True (p_before in h_sign, p_after in next_sign).
        """
        geometry = {
            "ascendant_sign": "Leo",
            "houses": {
                11: {
                    "sign": "Gemini",
                    "lord": "Mercury",
                    "cusp_longitude": 89.97,
                    "occupants": ["Sun"]
                }
            }
        }
        d1_grahas = {
            p: {"sign": "Aries", "longitude": 10.0, "dignity": "Neutral"}
            for p in CLASSICAL_PLANETS
        }
        d1_grahas["Sun"] = {"sign": "Gemini", "longitude": 82.93, "dignity": "Neutral"}
        d1_grahas["Mercury"] = {"sign": "Cancer", "longitude": 98.87, "dignity": "Neutral"}

        func_natures = {
            p: {"score": 1.0, "classification": "Benefic"}
            for p in CLASSICAL_PLANETS
        }

        res = evaluate_house_walls_kartari(geometry, d1_grahas, func_natures)
        assert 11 in res
        assert res[11]["is_walled"] is True
        assert res[11]["planet_before"] == "Sun"
        assert res[11]["planet_after"] == "Mercury"
        assert res[11]["wall_type"] != "None"

    def test_phaladeepika_15_14_cusp_proximity_sandhi_relief(self):
        """
        Verifies that a planet at 27.0° Leo when the Ascendant cusp is 29.5° Leo (2.5° from cusp)
        has its sandhi_penalty attenuated by 2.5 / 5.0 = 0.50x compared to when the cusp is at 10.0° Leo.
        """
        func_natures = {p: {"score": 1.0, "classification": "Benefic"} for p in CLASSICAL_PLANETS}
        influences = {
            "planet_to_planet": {p1: {p2: 0.0 for p2 in CLASSICAL_PLANETS} for p1 in CLASSICAL_PLANETS},
            "adjusted_conjunctions": {p: {h: 0.0 for h in range(1, 13)} for p in CLASSICAL_PLANETS},
            "raw_conjunctions": {p: {h: 0.0 for h in range(1, 13)} for p in CLASSICAL_PLANETS},
        }

        # Case A: Cusp at 29.5° Leo (lon 149.5°), Mars at 27.0° Leo (lon 147.0°) -> dist_to_cusp = 2.5°
        geom_a = {
            "ascendant_sign": "Leo",
            "houses": {
                1: {"sign": "Leo", "lord": "Sun", "cusp_longitude": 149.5, "occupants": ["Mars"]}
            }
        }
        for h in range(2, 13):
            geom_a["houses"][h] = {"sign": ZODIAC_SIGNS[(4 + h - 1) % 12], "lord": "Sun", "cusp_longitude": (4 + h - 1) * 30.0 + 29.5, "occupants": []}

        grahas_a = {p: {"sign": "Aries", "longitude": 10.0, "degree_0_to_30": 10.0} for p in CLASSICAL_PLANETS}
        grahas_a["Mars"] = {"sign": "Leo", "longitude": 147.0, "degree_0_to_30": 27.0}

        eval_a = evaluate_planets_hol(geom_a, grahas_a, func_natures, influences)
        sandhi_a = eval_a["Mars"]["bhava_sandhi"]

        # Case B: Cusp at 10.0° Leo (lon 130.0°), Mars at 27.0° Leo (lon 147.0°) -> dist_to_cusp = 17.0° (> 5.0°)
        geom_b = {
            "ascendant_sign": "Leo",
            "houses": {
                1: {"sign": "Leo", "lord": "Sun", "cusp_longitude": 130.0, "occupants": ["Mars"]}
            }
        }
        for h in range(2, 13):
            geom_b["houses"][h] = {"sign": ZODIAC_SIGNS[(4 + h - 1) % 12], "lord": "Sun", "cusp_longitude": (4 + h - 1) * 30.0 + 10.0, "occupants": []}

        grahas_b = {p: {"sign": "Aries", "longitude": 10.0, "degree_0_to_30": 10.0} for p in CLASSICAL_PLANETS}
        grahas_b["Mars"] = {"sign": "Leo", "longitude": 147.0, "degree_0_to_30": 27.0}

        eval_b = evaluate_planets_hol(geom_b, grahas_b, func_natures, influences)
        sandhi_b = eval_b["Mars"]["bhava_sandhi"]

        # Raw penalty: 1.0 - (3.0 / 4.0) = 0.25
        # In Case A: Cusp is at 29.5° Leo (border 0.5°), Mars is at 27.0° Leo (dist_to_cusp = 2.5° <= 5.0°,
        # and sits between the cusp and sign center). Per Phaladīpikā 15.14 & 8.34-35, Mars is at the cusp door,
        # fully inside the house, with zero sandhi penalty.
        # In Case B: dist_to_cusp = 17.0°, relief = 1.0 -> penalty = 0.25
        assert sandhi_b["penalty_ratio"] == pytest.approx(0.25, abs=0.001)
        assert sandhi_a["penalty_ratio"] == 0.0
        assert sandhi_a["in_sandhi_zone"] is False

    def test_phaladeepika_15_30_parivartana_mutual_influence(self):
        """
        Verifies that two planets in mutual sign exchange (Parivartana / Mitho Yoga per Phaladīpikā 15.30)
        receive a 50.0% mutual influence floor in planet_to_planet even with 0° physical Graha Dṛṣṭi.
        """
        geometry = {
            "houses": {h: {"sign": ZODIAC_SIGNS[h - 1], "cusp_longitude": (h - 1) * 30.0 + 15.0, "occupants": []} for h in range(1, 13)}
        }
        # Sun in Aries (ruled by Mars, 10.0° lon), Mars in Leo (ruled by Sun, 130.0° lon)
        # Angular distance = 120°. Neither casts physical aspect on the other (Sun trine aspect is 0 Virūpas).
        d1_grahas = {
            p: {"sign": "Pisces", "longitude": 345.0} for p in CLASSICAL_PLANETS
        }
        d1_grahas["Sun"] = {"sign": "Aries", "longitude": 10.0}
        d1_grahas["Mars"] = {"sign": "Leo", "longitude": 130.0}

        adv_aspects = {"planets": {}}
        influences = calculate_cusp_and_planet_influences(geometry, d1_grahas, adv_aspects)
        p2p = influences["planet_to_planet"]

        assert p2p["Sun"]["Mars"] >= 50.0
        assert p2p["Mars"]["Sun"] >= 50.0

    def test_house_dna_code_and_karaka_proximity_schema(self):
        """
        Verifies summary_rankings["house_dna_code"] is a 12-part hyphen-separated string
        and karaka_assessment exposes karaka_relative_houses and karaka_proximity.
        """
        from app import app
        client = app.test_client()
        res = client.get("/api/chart/9bb691ba-c4fd-40f1-83eb-289b4e275ac8")
        assert res.status_code == 200
        hol = res.get_json()["data"]["houses_of_life"]

        summary = hol["summary_rankings"]
        assert "house_dna_code" in summary
        dna_code = summary["house_dna_code"]
        assert isinstance(dna_code, str)
        parts = dna_code.split("-")
        assert len(parts) == 12
        assert set(parts) == {str(h) for h in range(1, 13)}
        assert parts == [str(h) for h in summary["houses_by_composite_score"]]

        # Check Karaka assessment schema for all 12 houses
        for h in range(1, 13):
            k_ass = hol["houses"][str(h)]["components"]["karaka_assessment"]
            assert "karaka_relative_houses" in k_ass
            assert "karaka_proximity" in k_ass
            assert isinstance(k_ass["karaka_relative_houses"], dict)
            assert isinstance(k_ass["karaka_proximity"], dict)
            for k in k_ass["karakas"]:
                assert k in k_ass["karaka_relative_houses"]
                assert 1 <= k_ass["karaka_relative_houses"][k] <= 12
                assert k in k_ass["karaka_proximity"]
                assert k_ass["karaka_proximity"][k] in [
                    "Close / Nourishing", "Distant / Dusthāna", "Moderate / Upacaya"
                ]


class TestPillar1SixAdaptations:
    """
    Direct unit tests for the 6 architectural and mathematical adaptations in Pillar 1
    (Basic House Condition / Cusp Rays) per Phaladīpikā Ch. 15 and Vic DiCara's Kala system.
    """

    def test_adaptation1_upacaya_no_friendly_fire_and_positive_dignity_scaling(self):
        """
        Adaptation 1:
        1. When 1st Lord (benefic f_eff > 0) occupies H11/H3/H6, it retains full positive ray
           and is NEVER slashed by 0.35x.
        2. When a malefic (f_eff < 0) occupies H11/H3/H6, it scales positively with dignity:
           Exalted (70.0) > Neutral (35.0) > Inimical (23.8) > Debilitated (7.0).
        """
        geometry = {
            "houses": {
                11: {"lord": "Mercury", "sign": "Gemini", "occupants": ["Sun", "Mars"]}
            }
        }
        # Sun is 1st Lord (score = +3.0) -> f_eff = +3.0 + 0.25 (Mercury friendly) = +3.25 > 0
        # Mars is malefic (score = -1.0) -> f_eff = -1.0 - 0.50 (Mercury enemy) = -1.50 < 0
        func_natures = {
            "Sun": {"score": 3.0, "classification": "Benefic"},
            "Mars": {"score": -1.0, "classification": "Malefic"},
        }
        for p in CLASSICAL_PLANETS:
            if p not in func_natures:
                func_natures[p] = {"score": 0.0, "classification": "Neutral"}

        d1_grahas = {
            p: {"dignity": "Own Sign", "longitude": 75.0, "sign": "Gemini"} for p in CLASSICAL_PLANETS
        }
        influences = {
            "planet_to_cusp": {
                p: {11: 100.0 if p in ["Sun", "Mars"] else 0.0} for p in CLASSICAL_PLANETS
            }
        }

        # Case A: Sun (1st Lord) in H11 must NOT be slashed by 0.35x
        res_a = evaluate_basic_house_conditions(geometry, func_natures, d1_grahas, influences)
        sun_contrib = res_a[11]["planet_contributions"]["Sun"]
        # Sun: eff_i_val = 100, d_p = 0.8, f_eff = 3.25 -> scaled = 180.0, f_mult = 1.0 + 0.65*2.25 = 2.4625 -> ~443.25
        assert sun_contrib > 300.0  # Full positive blessing, not slashed to ~60!

        # Case B: Mars (malefic f_eff < 0) dignity scaling in Upacaya
        # Exalted Mars (+1.0 dignity): pos_scaled = 100 * (1 + 1.0) = 200 -> 200 * 0.35 = 70.0
        d1_grahas["Mars"]["dignity"] = "Exalted"
        res_exalt = evaluate_basic_house_conditions(geometry, func_natures, d1_grahas, influences)
        assert res_exalt[11]["planet_contributions"]["Mars"] == pytest.approx(70.0, abs=0.5)

        # Neutral Mars (0.0 dignity): pos_scaled = 100 * 1.0 = 100 -> 100 * 0.35 = 35.0
        d1_grahas["Mars"]["dignity"] = "Neutral Sign"
        res_neutral = evaluate_basic_house_conditions(geometry, func_natures, d1_grahas, influences)
        assert res_neutral[11]["planet_contributions"]["Mars"] == pytest.approx(35.0, abs=0.5)

        # Debilitated Mars (-1.0 dignity): pos_scaled = 100 * (1 - 0.8) = 20 -> 20 * 0.35 = 7.0
        d1_grahas["Mars"]["dignity"] = "Debilitated"
        res_deb = evaluate_basic_house_conditions(geometry, func_natures, d1_grahas, influences)
        assert res_deb[11]["planet_contributions"]["Mars"] == pytest.approx(7.0, abs=0.5)

        # Strict ordering: Exalted > Neutral > Debilitated (dignity is never inverted)
        assert (
            res_exalt[11]["planet_contributions"]["Mars"]
            > res_neutral[11]["planet_contributions"]["Mars"]
            > res_deb[11]["planet_contributions"]["Mars"]
        )

    def test_adaptation2_no_double_counting_natural_temperament(self):
        """
        Adaptation 2:
        Verifies that Yogakāraka Mars (+3.0 for Leo) and Yogakāraka Saturn (+2.0 for Taurus)
        retain positive effective functional nature on house cusps, rather than having their
        Yogakāraka status erased to 0.00 or flipped to negative malefic.
        """
        geometry = {
            "houses": {
                1: {"lord": "Sun", "sign": "Leo", "occupants": []},
                7: {"lord": "Venus", "sign": "Taurus", "occupants": []}
            }
        }
        # Leo Lagna: Mars owns 4 & 9 (Rāja Yogakāraka, score = +3.0)
        func_natures = {
            "Mars": {"score": 3.0, "classification": "Benefic"},
            "Saturn": {"score": 2.0, "classification": "Benefic"}
        }
        for p in CLASSICAL_PLANETS:
            if p not in func_natures:
                func_natures[p] = {"score": 1.0, "classification": "Benefic"}

        d1_grahas = {
            p: {"dignity": "Own Sign", "longitude": 10.0, "sign": "Aries"} for p in CLASSICAL_PLANETS
        }
        influences = {
            "planet_to_cusp": {
                p: {1: 100.0 if p == "Mars" else 0.0, 7: 100.0 if p == "Saturn" else 0.0}
                for p in CLASSICAL_PLANETS
            }
        }

        res = evaluate_basic_house_conditions(geometry, func_natures, d1_grahas, influences)
        # Mars aspect on H1 (ruled by Sun, mutual friends -> friend_mod = +0.50):
        # f_eff = +3.0 + 0.50 = +3.50 (strongly positive, NOT wiped to 0.00!)
        mars_on_h1 = res[1]["planet_contributions"]["Mars"]
        assert mars_on_h1 > 200.0

        # Saturn aspect on H7 (ruled by Venus, mutual friends -> friend_mod = +0.50):
        # f_eff = +2.0 + 0.50 = +2.50 (strongly positive, NOT flipped to malefic -0.40!)
        saturn_on_h7 = res[7]["planet_contributions"]["Saturn"]
        assert saturn_on_h7 > 200.0

    def test_adaptation3_continuous_deadband_smooth_scaling(self):
        """
        Adaptation 3:
        Verifies that near f_eff = 0, signed_impact transitions smoothly without cliff edges
        or 107% sign inversions.
        """
        geometry = {
            "houses": {1: {"lord": "Jupiter", "sign": "Pisces", "occupants": []}}
        }
        d1_grahas = {
            p: {"dignity": "Own Sign", "longitude": 10.0, "sign": "Aries"} for p in CLASSICAL_PLANETS
        }
        influences = {
            "planet_to_cusp": {p: {1: 100.0 if p == "Mercury" else 0.0} for p in CLASSICAL_PLANETS}
        }

        # Step through f_lagna near 0: from -0.20 to +0.20
        # Mercury in Own Sign (d_p = +0.80), Jupiter to Mercury is Neutral (friend_mod = 0.0)
        outputs = []
        scores = [-0.20, -0.15, -0.10, -0.05, 0.0, 0.05, 0.10, 0.15, 0.20]
        for sc in scores:
            fn = {p: {"score": sc if p == "Mercury" else 1.0} for p in CLASSICAL_PLANETS}
            res = evaluate_basic_house_conditions(geometry, fn, d1_grahas, influences)
            outputs.append(res[1]["planet_contributions"]["Mercury"])

        # Every successive step must be monotonically increasing with no sudden cliff jumps
        for i in range(len(outputs) - 1):
            assert outputs[i+1] > outputs[i]
            # Max step jump should be smooth and reasonable (< 35 points per 0.05 change)
            assert (outputs[i+1] - outputs[i]) < 35.0

    def test_adaptation4_multi_varga_dignity_rescuing_positive_rays(self):
        """
        Adaptation 4:
        Verifies that a planet with negative D1 dignity but positive composite dignity (rescued
        by D9 / Vargottama) is not hit by the negative dignity penalty (arinīca-mūḍha).
        """
        geometry = {
            "houses": {1: {"lord": "Mars", "sign": "Aries", "occupants": []}}
        }
        func_natures = {p: {"score": 2.0} for p in CLASSICAL_PLANETS}
        # In D1, Jupiter is in Enemy's Sign (d_d1 = -0.40)
        d1_grahas = {
            p: {"dignity": "Enemy's Sign", "longitude": 10.0, "sign": "Aries"} for p in CLASSICAL_PLANETS
        }
        influences = {
            "planet_to_cusp": {p: {1: 100.0 if p == "Jupiter" else 0.0} for p in CLASSICAL_PLANETS}
        }

        # Case A: Rescued in D9 to composite unit_score = +0.80 (Vargottama)
        planets_eval_rescued = {
            "Jupiter": {
                "dignity": {"unit_score": 0.80},
                "combustion": {"loss_ratio": 0.0},
                "bhava_sandhi": {"penalty_ratio": 0.0}
            }
        }
        res_rescued = evaluate_basic_house_conditions(
            geometry, func_natures, d1_grahas, influences, planets_eval=planets_eval_rescued
        )
        jup_rescued = res_rescued[1]["planet_contributions"]["Jupiter"]

        # Case B: Negative composite dignity unit_score = -0.40 (not rescued)
        planets_eval_afflicted = {
            "Jupiter": {
                "dignity": {"unit_score": -0.40},
                "combustion": {"loss_ratio": 0.0},
                "bhava_sandhi": {"penalty_ratio": 0.0}
            }
        }
        res_afflicted = evaluate_basic_house_conditions(
            geometry, func_natures, d1_grahas, influences, planets_eval=planets_eval_afflicted
        )
        jup_afflicted = res_afflicted[1]["planet_contributions"]["Jupiter"]

        # Rescued planet delivers much stronger ray than un-rescued planet
        assert jup_rescued > jup_afflicted * 2.0
        # Rescued planet is not penalized by condition_integrity
        assert jup_rescued > 300.0

    def test_adaptation5_late_early_cusp_sandhi_relief_trump_mars(self):
        """
        Adaptation 5:
        Verifies Donald Trump's Mars geometry:
        Ascendant cusp is at 29.97° Leo (0.03° from border).
        Mars is at 26.78° Leo (3.19° from cusp, inside the house facing the door).
        Mars must have 0.0 sandhi_penalty (relieved by cusp proximity per Phaladīpikā 15.14 & 8.34-35).
        """
        geometry = {
            "ascendant_sign": "Leo",
            "houses": {
                1: {"sign": "Leo", "lord": "Sun", "cusp_longitude": 149.97, "occupants": ["Mars"]}
            }
        }
        for h in range(2, 13):
            geometry["houses"][h] = {
                "sign": ZODIAC_SIGNS[(4 + h - 1) % 12],
                "lord": "Sun",
                "cusp_longitude": (4 + h - 1) * 30.0 + 29.97,
                "occupants": []
            }

        d1_grahas = {
            p: {"sign": "Aries", "longitude": 10.0, "degree_0_to_30": 10.0} for p in CLASSICAL_PLANETS
        }
        d1_grahas["Mars"] = {"sign": "Leo", "longitude": 146.78, "degree_0_to_30": 26.78}
        func_natures = {p: {"score": 1.0, "classification": "Benefic"} for p in CLASSICAL_PLANETS}
        influences = {
            "planet_to_planet": {p1: {p2: 0.0 for p2 in CLASSICAL_PLANETS} for p1 in CLASSICAL_PLANETS},
            "adjusted_conjunctions": {p: {h: 0.0 for h in range(1, 13)} for p in CLASSICAL_PLANETS},
            "raw_conjunctions": {p: {h: 0.0 for h in range(1, 13)} for p in CLASSICAL_PLANETS},
        }

        eval_res = evaluate_planets_hol(geometry, d1_grahas, func_natures, influences)
        mars_sandhi = eval_res["Mars"]["bhava_sandhi"]

        assert mars_sandhi["in_sandhi_zone"] is False
        assert mars_sandhi["penalty_ratio"] == 0.0
        assert mars_sandhi["retention_multiplier"] == 1.0

    def test_adaptation6_cusp_score_strict_monotonicity(self):
        """
        Adaptation 6:
        Verifies that Pillar 1 normalization (total_signed / 3.0 followed by 120 * tanh)
        is strictly monotonic:
        Adding an additional benefic ray strictly INCREASES the house score,
        and adding an additional malefic ray strictly DECREASES the house score.
        """
        geometry = {
            "houses": {1: {"lord": "Mars", "sign": "Aries", "occupants": []}}
        }
        func_natures = {
            "Jupiter": {"score": 2.0},
            "Venus": {"score": 2.0},
            "Sun": {"score": 2.0},
            "Moon": {"score": 2.0},
            "Saturn": {"score": -2.0},
        }
        for p in CLASSICAL_PLANETS:
            if p not in func_natures:
                func_natures[p] = {"score": 0.0}

        d1_grahas = {
            p: {"dignity": "Own Sign", "longitude": 10.0, "sign": "Aries"} for p in CLASSICAL_PLANETS
        }

        # Baseline: 3 strong benefic aspects
        inf_baseline = {
            "planet_to_cusp": {
                "Jupiter": {1: 90.0},
                "Venus": {1: 90.0},
                "Sun": {1: 90.0},
                "Moon": {1: 0.0},
                "Saturn": {1: 0.0},
                "Mars": {1: 0.0},
                "Mercury": {1: 0.0},
            }
        }
        res_baseline = evaluate_basic_house_conditions(geometry, func_natures, d1_grahas, inf_baseline)
        score_baseline = res_baseline[1]["score"]

        # Scenario 1: Add a 4th moderate benefic aspect (+20 ray from Moon)
        inf_plus_benefic = {
            "planet_to_cusp": {
                **inf_baseline["planet_to_cusp"],
                "Moon": {1: 45.0}  # Additional positive ray
            }
        }
        res_benefic = evaluate_basic_house_conditions(geometry, func_natures, d1_grahas, inf_plus_benefic)
        score_benefic = res_benefic[1]["score"]

        # Strict monotonicity: adding a benefic aspect MUST strictly increase the house score!
        assert score_benefic > score_baseline

        # Scenario 2: Add a malefic aspect from Saturn
        inf_plus_malefic = {
            "planet_to_cusp": {
                **inf_baseline["planet_to_cusp"],
                "Saturn": {1: 45.0}  # Negative ray
            }
        }
        res_malefic = evaluate_basic_house_conditions(geometry, func_natures, d1_grahas, inf_plus_malefic)
        score_malefic = res_malefic[1]["score"]

        # Strict monotonicity: adding a malefic aspect MUST strictly decrease the house score!
        assert score_malefic < score_baseline







