import os
import pytest
from scripts.export_codebase import export_codebase, collect_codebase_files, get_file_metadata, DEFAULT_MAX_SIZE_MB

def test_collect_codebase_files():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    files = collect_codebase_files(project_root)
    
    assert len(files) > 50, "Should collect all essential codebase files"
    assert "jyotish/generate_jyotish.py" in files
    assert "app.py" in files
    assert "templates/index.html" in files
    assert "jyotish/shadbala/shadbala.py" in files
    assert "jyotish/shadbala/shadbala.md" in files
    assert "tests/test_shadbala.py" in files
    
    # Assert exclusions
    for f in files:
        assert not f.endswith((".pdf", ".epub", ".mp3", ".pyc")), f"Binary file {f} should be excluded"
        assert "transcript.txt" not in f, "Raw transcripts should be excluded"
        assert "va_text.txt" not in f, "Raw text dumps should be excluded"

def test_file_metadata():
    cat, desc = get_file_metadata("jyotish/generate_jyotish.py")
    assert cat == "Core Math Engine"
    assert len(desc) > 10

    cat_adr, desc_adr = get_file_metadata("documentations/adr/001-house-system-campanus.md")
    assert cat_adr == "Architecture Decisions"

def test_export_codebase_execution(tmp_path):
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    test_output = str(tmp_path / "test_export.txt")
    
    result = export_codebase(output_file=test_output, max_size_mb=DEFAULT_MAX_SIZE_MB, project_root=project_root)
    
    assert os.path.exists(test_output), "Export file should be created"
    size_bytes = os.path.getsize(test_output)
    size_mb = size_bytes / (1024 * 1024)
    
    # Strict size assertions: MUST be under 1.2 megabytes
    assert size_mb < DEFAULT_MAX_SIZE_MB, f"Export size {size_mb:.2f} MB exceeds {DEFAULT_MAX_SIZE_MB} MB limit"
    assert size_bytes > 500 * 1024, f"Export size {size_bytes} bytes is suspiciously small"
    
    with open(test_output, "r", encoding="utf-8") as f:
        content = f.read()
        
    assert "# ASTRA PRECISION ASTROLOGICAL ENGINE - CODEBASE EXPORT" in content
    assert "Campanus House System" in content
    assert "Dhruva Galactic Center" in content
    assert "The Twin Markdown Pattern" in content
    assert "FILE: jyotish/generate_jyotish.py" in content
    assert "FILE: templates/index.html" in content
    assert "FILE: tests/test_shadbala.py" in content


def test_collect_codebase_files_scopes():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    fe_files = collect_codebase_files(project_root, scope="frontend")
    be_files = collect_codebase_files(project_root, scope="backend")

    assert len(fe_files) > 30, "Frontend scope should collect all UI/template/style files"
    assert "templates/index.html" in fe_files
    assert "static/css/pergamon-theme.css" in fe_files
    assert "static/js/widget_registry.js" in fe_files
    assert "jyotish/generate_jyotish.py" not in fe_files

    assert len(be_files) > 50, "Backend scope should collect all math/API/doc files"
    assert "jyotish/generate_jyotish.py" in be_files
    assert "app.py" in be_files
    assert "jyotish/shadbala/shadbala.py" in be_files
    assert "static/css/pergamon-theme.css" not in be_files


def test_export_frontend_and_backend(tmp_path):
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    fe_out = str(tmp_path / "frontend.txt")
    fe_res = export_codebase(output_file=fe_out, project_root=project_root, scope="frontend")
    assert os.path.exists(fe_out)
    assert fe_res["total_bytes"] < 1.0 * 1024 * 1024, "Frontend export must stay under 1.0 MB"

    with open(fe_out, "r", encoding="utf-8") as f:
        fe_content = f.read()
    assert "FRONTEND CODEBASE EXPORT" in fe_content
    assert "\nFILE: templates/index.html\n" in fe_content
    assert "\nFILE: jyotish/generate_jyotish.py\n" not in fe_content

    be_out = str(tmp_path / "backend.txt")
    be_res = export_codebase(output_file=be_out, project_root=project_root, scope="backend")
    assert os.path.exists(be_out)
    assert be_res["total_bytes"] < 1.5 * 1024 * 1024, "Backend export must stay under 1.5 MB"

    with open(be_out, "r", encoding="utf-8") as f:
        be_content = f.read()
    assert "BACKEND CODEBASE EXPORT" in be_content
    assert "\nFILE: jyotish/generate_jyotish.py\n" in be_content
    assert "\nFILE: templates/index.html\n" not in be_content


def test_export_split_mode(tmp_path):
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    test_out = str(tmp_path / "export.txt")

    res = export_codebase(output_file=test_out, project_root=project_root, scope="split")
    assert "frontend" in res
    assert "backend" in res

    fe_file = str(tmp_path / "export_frontend.txt")
    be_file = str(tmp_path / "export_backend.txt")
    assert os.path.exists(fe_file)
    assert os.path.exists(be_file)

