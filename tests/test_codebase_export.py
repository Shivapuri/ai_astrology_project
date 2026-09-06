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
    
    result = export_codebase(output_file=test_output, max_size_mb=1.5, project_root=project_root)
    
    assert os.path.exists(test_output), "Export file should be created"
    size_bytes = os.path.getsize(test_output)
    size_mb = size_bytes / (1024 * 1024)
    
    # Strict size assertions: MUST be under 1.5 megabytes
    assert size_mb < 1.5, f"Export size {size_mb:.2f} MB exceeds 1.5 MB limit"
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
