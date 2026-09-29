"""
tests/test_bundle_folder.py
===========================
Unit and regression tests for scripts/bundle_folder.py.
Verifies:
- Universal folder bundling (discovers Python and Markdown files)
- Strict .gitignore adherence (excludes __pycache__, .pytest_cache, *.pyc, etc.)
- Custom extension filtering (--ext py,md)
- Output formatting (Master header, Table of Contents, file delimiter banners)
"""

import os
import pytest
from scripts.bundle_folder import (
    collect_folder_files,
    generate_bundle,
    is_binary_file,
    format_file_type,
)

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_collect_folder_files_yogas():
    """Verify that bundle_folder collects all yogas files and excludes pycache."""
    yogas_dir = os.path.join(_PROJECT_ROOT, "jyotish", "yogas")
    base_dir, files = collect_folder_files(yogas_dir)

    assert len(files) >= 15, "Should find all yogas files"

    rel_names = [rel for rel, full in files]
    assert "yogas.md" in rel_names
    assert "yoga_rule_book.md" in rel_names
    assert "raja_yogas.py" in rel_names
    assert "breakers.py" in rel_names

    # Ensure cache/binary exclusions
    for rel, full in files:
        assert "__pycache__" not in rel, f"__pycache__ should be excluded from {rel}"
        assert not rel.endswith(".pyc"), f".pyc should be excluded from {rel}"
        assert not rel.endswith(".DS_Store"), f".DS_Store should be excluded from {rel}"


def test_custom_extension_filtering():
    """Verify that extension filtering isolates only specified types."""
    yogas_dir = os.path.join(_PROJECT_ROOT, "jyotish", "yogas")
    base_dir, files = collect_folder_files(yogas_dir, extensions=["md"])

    rel_names = [rel for rel, full in files]
    for rel in rel_names:
        assert rel.endswith(".md"), f"Expected only .md files, got {rel}"

    assert "yogas.md" in rel_names
    assert "yoga_rule_book.md" in rel_names
    assert "raja_yogas.py" not in rel_names


def test_binary_file_detection(tmp_path):
    """Verify binary probe accurately catches binary files and permits text files."""
    text_file = str(tmp_path / "hello.txt")
    with open(text_file, "w", encoding="utf-8") as f:
        f.write("Hello world!\nThis is plain text.")

    bin_file = str(tmp_path / "data.bin")
    with open(bin_file, "wb") as f:
        f.write(b"Hello\x00World\xff\xfe")

    assert not is_binary_file(text_file), "Text file should not be flagged as binary"
    assert is_binary_file(bin_file), "File with null bytes should be flagged as binary"


def test_generate_bundle_execution(tmp_path):
    """Verify full bundle generation with master header and delimiters."""
    yogas_dir = os.path.join(_PROJECT_ROOT, "jyotish", "yogas")
    out_file = str(tmp_path / "test_yogas_bundle.txt")

    result = generate_bundle(
        target_folder=yogas_dir,
        output_path=out_file,
        extensions=["py", "md"],
    )

    assert os.path.exists(out_file), "Bundle output file must exist"
    assert result["files_count"] >= 15
    assert result["total_lines"] > 1000
    assert result["total_bytes"] > 50000

    with open(out_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Verify master header elements
    assert "ASTRA CODEBASE FOLDER BUNDLE" in content
    assert "TABLE OF CONTENTS" in content
    assert "yogas.md" in content
    assert "raja_yogas.py" in content

    # Verify individual file separator banners
    assert "FILE: yogas.md" in content
    assert "TYPE: Markdown Document" in content
    assert "FILE: raja_yogas.py" in content
    assert "TYPE: Python Source" in content
