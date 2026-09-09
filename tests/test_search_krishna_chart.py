import pytest
from scripts.search_krishna_chart import search_best_alignments, evaluate_chart_at_jd, circular_diff
import swisseph as swe

def test_circular_diff():
    assert circular_diff(10.0, 20.0) == 10.0
    assert circular_diff(350.0, 10.0) == 20.0
    assert circular_diff(0.0, 180.0) == 180.0

def test_evaluate_chart_at_jd():
    # Test year -3255-08-28 at 23:50 IST (18.333 UTC)
    jd = swe.julday(-3255, 8, 28, 18.333, swe.JUL_CAL)
    res = evaluate_chart_at_jd(jd)
    assert res["sign_matches"] >= 6
    assert res["house_matches"] >= 6
    assert "Ascendant" in res["body_details"]
    assert res["body_details"]["Ascendant"]["calc_sign"] == "Taurus"
    assert res["body_details"]["Saturn"]["calc_sign"] == "Libra"
    assert res["body_details"]["Jupiter"]["calc_sign"] == "Pisces"

def test_search_best_alignments():
    # Narrow window search around -3260 to -3250
    results = search_best_alignments(start_year=-3260, end_year=-3250, top_n=2, verbose=False)
    assert len(results) > 0
    top = results[0]
    assert top["sign_matches"] >= 6
    assert top["composite_score"] > 60.0
