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
