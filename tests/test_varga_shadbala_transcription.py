import pytest
import os
import csv
import sys

from jyotish.generate_jyotish import generate_kala_chart
from jyotish.avasthas.quantitative import calculate_avastha_matrix
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
MASTER_SHADBALA_CSV = os.path.join(TRANSCRIPTION_DIR, "angelina_jolie_shadbala_all_vargas_matrices.csv")

@pytest.fixture(scope="module")
def aj_chart():
    return generate_kala_chart(
        name="Angelina Jolie",
        year=1975, month=6, day=4,
        hour=9, minute=9,
        latitude=34.0522, longitude=-118.2437,
        timezone_offset=-7.0
    )

def test_transcribed_master_shadbala_csv_exists():
    assert os.path.exists(MASTER_SHADBALA_CSV), f"Master ShadBala CSV not found at {MASTER_SHADBALA_CSV}"

def test_all_16_varga_shadbala_diagonals_match_ground_truth(aj_chart):
    """
    Verifies that for all 16 vargas, the diagonal baseline for each planet
    matches the transcribed ground truth.
    """
    expected = {}
    with open(MASTER_SHADBALA_CSV, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            if r["Is_Diagonal"] == "True":
                clean_val = float(r["Base_Shadbala"].replace("*2", ""))
                expected.setdefault(r["Varga"], {})[r["Receiver"]] = clean_val

    for v in ALL_VARGAS:
        mat_res = calculate_avastha_matrix(
            grahas_data=aj_chart["vargas"][v]["grahas"],
            shadbala_data=aj_chart["shadbala"],
            d1_grahas=aj_chart["vargas"]["D1"]["grahas"],
            baseline_type="ShadBala",
            varga_name=v,
            vimshopaka_data=aj_chart["vimshopaka"]
        )
        matrix = mat_res["matrix"]
        for p in PLANETS_7:
            calc_val = matrix[p][p]["base"]
            exp_val = expected[v][p]
            assert abs(calc_val - exp_val) <= 0.1, (
                f"{v} {p} diagonal base: calculated {calc_val:.1f} vs expected {exp_val:.1f}"
            )

def test_all_16_varga_shadbala_column_totals_match_ground_truth(aj_chart):
    """
    Verifies that for all 16 vargas under ShadBala baseline, the column net totals
    match the transcribed Kala screenshot totals with zero error.
    """
    expected = {}
    with open(MASTER_SHADBALA_CSV, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            if r["Is_Diagonal"] == "True":
                expected.setdefault(r["Varga"], {})[r["Receiver"]] = float(r["Net_Total"])

    for v in ALL_VARGAS:
        mat_res = calculate_avastha_matrix(
            grahas_data=aj_chart["vargas"][v]["grahas"],
            shadbala_data=aj_chart["shadbala"],
            d1_grahas=aj_chart["vargas"]["D1"]["grahas"],
            baseline_type="ShadBala",
            varga_name=v,
            vimshopaka_data=aj_chart["vimshopaka"]
        )
        matrix = mat_res["matrix"]
        for p in PLANETS_7:
            calc_val = matrix[p][p]["net_total"]
            exp_val = expected[v][p]
            assert abs(calc_val - exp_val) <= 0.15, (
                f"{v} {p} column net total: calculated {calc_val:.1f} vs expected {exp_val:.1f}"
            )
