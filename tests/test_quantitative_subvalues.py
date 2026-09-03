import json
import os
import pytest
from jyotish.generate_jyotish import generate_kala_chart

PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]


@pytest.fixture(scope="module")
def aj_data():
    chart = generate_kala_chart(
        name="Angelina Jolie",
        year=1975,
        month=6,
        day=4,
        hour=9,
        minute=9,
        latitude=34.0522,
        longitude=-118.2437,
        timezone_offset=-7.0,
    )
    baseline_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "source-material",
        "software-setup",
        "sample-case",
        "angelina_jolie_baselines.json",
    )
    with open(baseline_path, "r") as f:
        baselines = json.load(f)
    return chart, baselines


@pytest.mark.parametrize(
    "matrix_key",
    ["ishta", "subha", "cheshta", "uccha", "dig", "veda", "drishti_yuti", "shadbala"],
)
def test_all_matrix_subvalues(aj_data, matrix_key):
    chart, baselines = aj_data
    if matrix_key == "shadbala":
        key_title = "ShadBala"
    elif matrix_key == "drishti_yuti":
        key_title = "Drishti Yuti"
    else:
        key_title = matrix_key.title()
    calc_matrix = chart["avastha_matrix"]["D1"][key_title]
    exp_matrix = baselines[matrix_key]
    tol = 90.0 if matrix_key == "shadbala" else 1.5

    for giver in PLANETS:
        for recv in PLANETS:
            exp_items = exp_matrix[giver][recv]
            calc_cell = calc_matrix[giver][recv]

            if giver == recv:
                if matrix_key == "drishti_yuti":
                    if exp_items:
                        assert (
                            abs(
                                calc_cell["aspect_virupas"]
                                - exp_items[0]["value"]
                            )
                            <= 0.5
                        )
                elif matrix_key == "shadbala":
                    if exp_items:
                        assert abs(calc_cell["base"] - exp_items[0]["value"]) <= tol
                else:
                    # Diagonal has 3 items: Base [G], Diff [K], Base_Negative [R]
                    assert abs(calc_cell["base"] - exp_items[0]["value"]) <= tol
                    assert (
                        abs(calc_cell["base_negative"] - exp_items[2]["value"])
                        <= tol
                    )
            else:
                if matrix_key == "drishti_yuti":
                    if not exp_items:
                        assert (
                            calc_cell["pos_pull"] == 0
                            and calc_cell["neg_pull"] == 0
                            and calc_cell["neu_pull"] == 0
                        )
                    elif len(exp_items) == 2:
                        # Dual aspect in drishti_yuti (e.g. Sun->Mercury)
                        assert abs(calc_cell["neg_pull"] - exp_items[0]["value"]) <= 0.5
                        assert abs(calc_cell["pos_pull"] - exp_items[1]["value"]) <= 0.5
                    elif len(exp_items) == 1:
                        color = exp_items[0]["color"]
                        if color == "G":
                            assert abs(calc_cell["pos_pull"] - exp_items[0]["value"]) <= 0.5
                        elif color == "R":
                            assert abs(calc_cell["neg_pull"] - exp_items[0]["value"]) <= 0.5
                        elif color == "B":
                            assert abs(calc_cell["neu_pull"] - exp_items[0]["value"]) <= 0.5
                else:
                    if not exp_items:
                        assert (
                            calc_cell["pos_pull"] == 0
                            and calc_cell["neg_pull"] == 0
                            and calc_cell["neu_pull"] == 0
                        )
                    elif len(exp_items) == 4:
                        # Dual cell: [neg_pull, pos_pull, iso_neg, iso_pos]
                        assert (
                            abs(calc_cell["neg_pull"] - exp_items[0]["value"])
                            <= tol
                        )
                        assert (
                            abs(calc_cell["pos_pull"] - exp_items[1]["value"])
                            <= tol
                        )
                        assert (
                            abs(
                                calc_cell["isolated_negative"]
                                - exp_items[2]["value"]
                            )
                            <= tol
                        )
                        assert (
                            abs(
                                calc_cell["isolated_positive"]
                                - exp_items[3]["value"]
                            )
                            <= tol
                        )
                    elif len(exp_items) == 2:
                        # Single cell: [pull, isolated]
                        color = exp_items[0]["color"]
                        if color == "G":
                            assert (
                                abs(calc_cell["pos_pull"] - exp_items[0]["value"])
                                <= tol
                            )
                            assert (
                                abs(
                                    calc_cell["isolated_positive"]
                                    - exp_items[1]["value"]
                                )
                                <= tol
                            )
                        elif color == "R":
                            assert (
                                abs(calc_cell["neg_pull"] - exp_items[0]["value"])
                                <= tol
                            )
                            assert (
                                abs(
                                    calc_cell["isolated_negative"]
                                    - exp_items[1]["value"]
                                )
                                <= tol
                            )
                        elif color == "B":
                            assert (
                                abs(calc_cell["neu_pull"] - exp_items[0]["value"])
                                <= tol
                            )
                            assert (
                                abs(
                                    calc_cell["isolated_neutral"]
                                    - exp_items[1]["value"]
                                )
                                <= tol
                            )
