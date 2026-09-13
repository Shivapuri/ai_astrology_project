import pytest
import os
import csv
import sys

from jyotish.generate_jyotish import generate_kala_chart
from jyotish.avasthas.quantitative import calculate_varga_lajjitadi_net_modifiers
from jyotish.vimshopaka.vimshopaka import calculate_varga_vimshopaka_engine

PLANETS_7 = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
ALL_VARGAS = [
    "D1", "D2", "D3", "D4", "D7", "D9", "D10", "D12",
    "D16", "D20", "D24", "D27", "D30", "D40", "D45", "D60"
]

SAMPLE_CASE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "source-material", "software-setup", "sample-case"
)
TRANSCRIPTION_DIR = os.path.join(SAMPLE_CASE_DIR, "lajjitadi_transcription")
MASTER_CSV_PATH = os.path.join(TRANSCRIPTION_DIR, "angelina_jolie_lajjitadi_all_vargas_matrices.csv")

@pytest.fixture(scope="module")
def aj_chart():
    return generate_kala_chart(
        name="Angelina Jolie",
        year=1975, month=6, day=4,
        hour=9, minute=9,
        latitude=34.0522, longitude=-118.2437,
        timezone_offset=-7.0
    )

def test_transcribed_master_csv_exists():
    assert os.path.exists(MASTER_CSV_PATH), f"Master CSV not found at {MASTER_CSV_PATH}"

def test_all_16_varga_net_modifiers_match_transcription(aj_chart):
    """
    Verifies that all 112 Net Modifiers (16 vargas x 7 planets) produced by
    calculate_varga_lajjitadi_net_modifiers match the transcribed ground truth.
    """
    calculated = calculate_varga_lajjitadi_net_modifiers(aj_chart)
    
    expected = {}
    with open(MASTER_CSV_PATH, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            expected.setdefault(r["Varga"], {})[r["Receiver"]] = float(r["Net_Modifier"])
            
    for v in ALL_VARGAS:
        assert v in calculated, f"Varga {v} missing from calculated modifiers"
        assert v in expected, f"Varga {v} missing from expected modifiers"
        for p in PLANETS_7:
            calc_val = calculated[v][p]
            exp_val = expected[v][p]
            assert abs(calc_val - exp_val) <= 0.1, (
                f"{v} {p}: calculated {calc_val:.1f} vs expected {exp_val:.1f}"
            )

def test_all_16_varga_diagonals_match_vimshopaka(aj_chart):
    """
    Verifies that the diagonal of each transcribed varga matrix matches
    the exact Vimshopaka dignity calculated by calculate_varga_vimshopaka_engine.
    """
    vim_data = calculate_varga_vimshopaka_engine({"vargas": aj_chart["vargas"]})
    vim_scores = vim_data["scores"]
    
    schemes = {
        "D1": "Shadvarga", "D2": "Shadvarga", "D3": "Shadvarga", "D9": "Shadvarga", "D12": "Shadvarga", "D30": "Shadvarga",
        "D7": "Saptavarga",
        "D10": "Dasavarga", "D16": "Dasavarga", "D60": "Dasavarga",
        "D4": "Shodasavarga", "D20": "Shodasavarga", "D24": "Shodasavarga", "D27": "Shodasavarga", "D40": "Shodasavarga", "D45": "Shodasavarga"
    }
    
    expected_diags = {}
    with open(MASTER_CSV_PATH, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            if r["Is_Diagonal"] == "True":
                clean_val = float(r["Vimsho_Score"].replace("*2", ""))
                expected_diags.setdefault(r["Varga"], {})[r["Receiver"]] = clean_val
                
    for v in ALL_VARGAS:
        scheme = schemes[v]
        for p in PLANETS_7:
            exp_val = expected_diags[v][p]
            calc_val = vim_scores[scheme][p]
            assert abs(calc_val - exp_val) <= 0.1, (
                f"{v} ({scheme}) {p} diagonal: expected {exp_val:.1f}, got {calc_val:.1f}"
            )

def test_all_15_divisional_avastha_matrices_match_transcription(aj_chart):
    """
    Verifies that all 15 divisional charts (D2 through D60) in aj_chart['avastha_matrix']
    under Drishti Yuti baseline match the transcribed ground truth cell-by-cell.
    """
    matrices = aj_chart.get("avastha_matrix", {})
    expected_rows = {}
    with open(MASTER_CSV_PATH, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            expected_rows.setdefault(r["Varga"], {})[(r["Giver"], r["Receiver"])] = r

    for v in ALL_VARGAS:
        if v == "D1":
            continue  # D1 tested in test_quantitative_avasthas.py
        assert v in matrices, f"Varga {v} missing in avastha_matrix"
        assert "Drishti Yuti" in matrices[v], f"Drishti Yuti missing for {v}"
        v_matrix = matrices[v]["Drishti Yuti"]

        for g in PLANETS_7:
            for rec in PLANETS_7:
                exp_row = expected_rows[v][(g, rec)]
                cell = v_matrix[g][rec]
                if g == rec:
                    exp_score = float(exp_row["Vimsho_Score"].replace("*2", ""))
                    exp_net = float(exp_row["Net_Modifier"])
                    assert abs(cell["vimshopaka_base"] - exp_score) <= 0.1, f"{v} {g} diag score"
                    assert abs(cell["net_total"] - exp_net) <= 0.1, f"{v} {g} net total"
                else:
                    exp_v1 = exp_row["Value_1"]
                    if not exp_v1:
                        assert cell["aspect_virupas"] == 0.0, f"{v} {g}->{rec} expected 0"
                    else:
                        exp_num = float(exp_v1)
                        assert abs(cell["aspect_virupas"] - exp_num) <= 0.1, (
                            f"{v} {g}->{rec}: got {cell['aspect_virupas']}, expected {exp_num}"
                        )

