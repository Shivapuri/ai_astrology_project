import pytest
from app import app, CHARTS_FILE
from jyotish.generate_jyotish import generate_kala_chart
from jyotish.text_exporter import generate_chart_ai_markdown


@pytest.fixture(scope="module")
def sample_chart():
    return generate_kala_chart("Swami Shivapuri", 1983, 11, 10, 22, 20, 52.20296, 8.0448, 1.0)


def test_generate_chart_ai_markdown_full(sample_chart):
    options = {
        "preset": "full",
        "include_prompt_header": True,
        "include_master_diagnostics": True,
        "include_archetypes": True,
        "include_vargas": True,
        "include_cusps": True,
        "include_dashas": True,
        "include_yogas": True
    }
    md = generate_chart_ai_markdown(sample_chart, options)

    # 1. Verification of Header and Subject Details
    assert "# Astrological Master Dossier: Swami Shivapuri" in md
    assert "Tropical Signs (Sāyana)" in md
    assert "Campanus 3D House System" in md
    assert "Sidereal Equatorial Nakshatras" in md
    assert "Ascendant (Lagna)" in md

    # 2. AI Directive / Prompt Header
    assert "AI Interpretation Directive & Prompt Header" in md
    assert "Ernst Wilhelm's Kala integrated paradigm" in md

    # 3. Master Graha Diagnostics 9-Column Table
    assert "Master Graha Diagnostics (D1 Root Chart)" in md
    assert "| Graha & Role | Longitude & Bhāva | Dignity & Sambandha | Dispositor (Rāśi Lord) | Ṣaḍbala Strength | Dṛṣṭi & Yuti (Aspects) | Nakṣatra & Overlord | Avasthās (State) | Archetype & Vitality |" in md
    assert "| **Lagna (Ascendant)** |" in md
    assert "| **Sun**" in md
    assert "| **Moon**" in md
    assert "| **Mars**" in md
    assert "| **Mercury**" in md
    assert "| **Jupiter**" in md
    assert "| **Venus**" in md
    assert "| **Saturn**" in md
    assert "| **Rahu**" in md
    assert "| **Ketu**" in md

    # 4. Master Lords & Chara Karakas
    assert "Core Archetypes & Functional Authority" in md
    assert "Soul Signifiers (Chara Kāraka System" in md
    assert "Lagneśa (D1 Ascendant Lord)" in md
    assert "Navāṁśeśa (D9 Dharma Lord)" in md
    assert "Drekkāṇeśa (D3 Courage Lord)" in md

    # 5. Key Divisional Charts
    assert "Key Divisional Charts (Vargas)" in md
    assert "D9 Navāṃśa (Dharma, Soul Blueprint & Partnerships)" in md
    assert "D10 Daśāṃśa (Career, Status & Executive Action)" in md

    # 6. Campanus Cusps
    assert "Campanus 3D Bhava Chalita Cusps" in md
    for h in range(1, 13):
        assert f"| **House {h}** |" in md

    # 7. Vimshottari Dasha Timeline
    assert "Vimśottarī Daśā Timeline" in md
    assert "Chronological Mahādaśā Cycles" in md

    # 8. Classical Yogas
    assert "Classical Yogas & Breakers" in md


def test_generate_chart_ai_markdown_diagnostics_only(sample_chart):
    options = {
        "preset": "diagnostics_only",
        "include_prompt_header": False,
        "include_master_diagnostics": True,
        "include_archetypes": False,
        "include_vargas": False,
        "include_cusps": False,
        "include_dashas": False,
        "include_yogas": False
    }
    md = generate_chart_ai_markdown(sample_chart, options)
    assert "Master Graha Diagnostics (D1 Root Chart)" in md
    assert "| **Sun**" in md
    assert "AI Interpretation Directive" not in md
    assert "D10 Daśāṃśa" not in md


def test_api_export_text_endpoint(sample_chart):
    client = app.test_client()

    # 1. Test missing payload
    res = client.post('/api/export_text', json={})
    assert res.status_code == 400

    # 2. Test valid chart_data
    res = client.post('/api/export_text', json={
        "chart_data": sample_chart,
        "options": {"preset": "full"}
    })
    assert res.status_code == 200
    data = res.get_json()
    assert "text" in data
    assert "Swami Shivapuri" in data["text"]
    assert "filename" in data
    assert data["filename"].endswith(".md")
    assert data["subject_name"] == "Swami Shivapuri"
