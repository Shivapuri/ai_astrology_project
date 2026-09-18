import io
import pytest
from app import app, CHARTS_FILE
from jyotish.generate_jyotish import generate_kala_chart
from jyotish.pdf_exporter import generate_report_html, export_chart_pdf
from jyotish import native_manager

@pytest.fixture(scope="module")
def sample_chart():
    return generate_kala_chart("Swami Shivapuri", 1983, 11, 10, 22, 20, 52.20296, 8.0448, 1.0)

def test_generate_report_html(sample_chart):
    options = {
        "page_size": "A3",
        "chart_style": "north",
        "notation": "symbol",
        "include_d1": True,
        "include_d9": True,
        "include_d10": True,
        "include_d7": True,
        "include_placements": True,
        "include_cusps": True,
        "include_dignities": True,
        "include_avasthas": True,
        "include_lajjitadi": True,
        "include_shadbala": True,
        "include_dasha": True,
        "include_vimshopaka": True
    }
    html = generate_report_html(sample_chart, options)
    assert "<!DOCTYPE html>" in html
    assert "Swami Shivapuri" in html
    assert "Campanus Bhava Cusps" in html
    assert "Planetary Placements &amp; Nakshatras" in html or "Planetary Placements & Nakshatras" in html
    assert "Pañcadhā Sambandha" in html
    assert "Qualitative Avasthās" in html
    assert "Lajjitādi Avasthās" in html
    assert "Ṣaḍbala Strength Matrix" in html
    assert "Vimśottarī Daśā Major Cycles" in html
    assert "D9 Navāṃśa" in html
    assert "D10 Daśāṃśa" in html
    assert "D7 Saptāṃśa" in html
    assert "16-Varga Dignity" in html
    assert "Strengths Matrix • Yoga Judgment" in html
    assert "Classical Yogas" in html
    assert "Yoga Bhanga" in html
    assert "Master Graha Diagnostics" in html
    assert "Horizon Vitality Architecture" in html
    assert "Master Astrological Diagnostic Key" in html

def test_export_chart_pdf(sample_chart):
    options = {
        "page_size": "A3",
        "chart_style": "north",
        "notation": "symbol"
    }
    pdf_bytes = export_chart_pdf(sample_chart, options)
    assert isinstance(pdf_bytes, bytes)
    assert pdf_bytes.startswith(b"%PDF-")
    assert len(pdf_bytes) > 50000

def test_export_chart_pdf_master_dossier_a4(sample_chart):
    options = {
        "page_size": "A4",
        "chart_style": "north",
        "notation": "symbol",
        "include_master_diagnostics": True,
        "include_diagnostic_key": True,
        "include_yogas": True
    }
    pdf_bytes = export_chart_pdf(sample_chart, options)
    assert isinstance(pdf_bytes, bytes)
    assert pdf_bytes.startswith(b"%PDF-")
    assert len(pdf_bytes) > 50000

def test_api_export_preview_endpoint():
    client = app.test_client()
    natives = native_manager.load_natives(CHARTS_FILE)
    assert len(natives) > 0
    native_id = natives[0]["id"]
    
    response = client.post('/api/export_preview', json={
        "native_id": native_id,
        "options": {
            "page_size": "A3",
            "chart_style": "north",
            "notation": "symbol"
        }
    })
    assert response.status_code == 200
    assert "text/html" in response.content_type
    assert "Astra Integrated Astrological Master Plan" in response.get_data(as_text=True)

def test_api_export_pdf_endpoint():
    client = app.test_client()
    natives = native_manager.load_natives(CHARTS_FILE)
    assert len(natives) > 0
    native_id = natives[0]["id"]
    
    response = client.post('/api/export_pdf', json={
        "native_id": native_id,
        "options": {
            "page_size": "A3",
            "chart_style": "north",
            "notation": "symbol"
        }
    })
    assert response.status_code == 200
    assert response.content_type == "application/pdf"
    assert response.data.startswith(b"%PDF-")
    assert "attachment" in response.headers.get("Content-Disposition", "")


def test_generate_report_html_with_biwheel(sample_chart):
    options = {
        "preset": "master_dossier_a4",
        "page_size": "A4",
        "chart_style": "biwheel",
        "notation": "symbol",
        "include_biwheel": True,
        "biwheel_outer": "D9",
        "include_master_diagnostics": True,
        "include_diagnostic_key": True
    }
    html = generate_report_html(sample_chart, options)
    assert "Harmonic Bi-Wheel Architecture" in html
    assert "Harmonic Alignment Matrix" in html
    assert "🌟 Vargottama" in html
    assert "viewBox=\"-210 -210 420 420\"" in html


def test_export_chart_pdf_biwheel(sample_chart):
    options = {
        "preset": "master_dossier_a4",
        "page_size": "A4",
        "chart_style": "biwheel",
        "notation": "symbol",
        "include_biwheel": True,
        "biwheel_outer": "D9"
    }
    pdf_bytes = export_chart_pdf(sample_chart, options)
    assert isinstance(pdf_bytes, bytes)
    assert pdf_bytes.startswith(b"%PDF-")
    assert len(pdf_bytes) > 50000


def test_master_diagnostics_d1_d9_d10_and_subconscious_drive(sample_chart):
    options = {
        "page_size": "A4",
        "landscape": True,
        "include_master_diagnostics": True,
        "include_d9_diagnostics": True,
        "include_d10_diagnostics": True
    }
    html = generate_report_html(sample_chart, options)
    # Check landscape CSS
    assert "A4 landscape" in html
    # Check D1 Master Diagnostics
    assert "Master Graha Diagnostics: D1 Rāśi" in html
    assert "Subconscious Drive (Nakshatra)" in html
    # Check D9 Navamsha Swamsha card & Diagnostics
    assert "Swāṃśa (D9 Navāṃśa Lagna)" in html
    assert "Master Graha Diagnostics: D9 Navāṃśa" in html
    assert "Navāṃśa Lagna (D9)" in html
    # Check D10 Dashamsha Executive card & Diagnostics
    assert "Daśāṃśa Lagna (D10 Career Horizon)" in html
    assert "Master Graha Diagnostics: D10 Daśāṃśa" in html
    assert "Career Seat (D10)" in html


def test_dual_vargas_north_and_south_indian(sample_chart):
    options = {
        "page_size": "A4",
        "landscape": True,
        "include_dual_vargas": True,
        "dual_vargas": ["D10", "D7", "D2", "D3", "D4", "D12", "D30", "D60"]
    }
    html = generate_report_html(sample_chart, options)
    # Check North and South Indian charts side-by-side
    assert "North Indian (Diamond)" in html
    assert "South Indian (Fixed Square)" in html
    assert "D10 Daśāṃśa" in html
    assert "D7 Saptāṃśa" in html
    assert "D2 Horā" in html
    assert "D3 Drekkāṇa" in html
    assert "D4 Caturthāṃśa" in html
    assert "D12 Dvādaśāṃśa" in html
    assert "D30 Triṃśāṃśa" in html
    assert "D60 Ṣaṣṭyāṃśa" in html


def test_vimshottari_timeline_and_16_varga_matrix(sample_chart):
    options = {
        "page_size": "A4",
        "landscape": True,
        "include_timeline": True,
        "include_vimshopaka": True
    }
    html = generate_report_html(sample_chart, options)
    # Check 120-year timeline
    assert "Vimśottarī Daśā 120-Year Parāśari Timeline" in html
    assert "Active Mahādaśā Spotlight" in html
    assert "Full 9 Antardaśā Sub-Periods Schedule" in html
    assert "★ CURRENT" in html
    # Check 16-Varga matrix with Rahu & Ketu and dignity counts
    assert "16-Varga Viṃśopaka Strength &amp; Dignity Matrix" in html or "16-Varga Viṃśopaka Strength & Dignity Matrix" in html
    assert "Dignified / Afflicted" in html
    assert "Rahu" in html
    assert "Ketu" in html


