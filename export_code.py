#!/usr/bin/env python3
"""
Astra Repository Code Exporter
Combines key code files into a single text file for AI analysis.
Filters out export artifacts, large dataset files, and unnecessary binary/cache files.
"""

import os
import argparse
from pathlib import Path

# Directories to ignore during export
DEFAULT_EXCLUDE_DIRS = {
    ".git", ".idea", "__pycache__", "venv", ".venv", 
    "cache", "chroma_astrology_db", "astrology_rag_data",
    ".pytest_cache", ".mypy_cache", "node_modules", "dist", "build"
}

# Extensions to explicitly ignore
DEFAULT_EXCLUDE_EXTENSIONS = {
    ".dat", ".bsp", ".download", ".log", ".db", ".sqlite", ".sqlite3", 
    ".pyc", ".png", ".jpg", ".jpeg", ".gif", ".pdf", ".bin", ".pickle",
    ".zip", ".tar", ".gz"
}

# Explicit filenames to exclude (export outputs, temporary files)
DEFAULT_EXCLUDE_FILES = {
    "code_export.txt", "commits_export.md"
}

# Extensions to include
DEFAULT_INCLUDE_EXTENSIONS = {
    ".py", ".md", ".json", ".txt", ".sh", ".yaml", ".yml"
}

def is_export_artifact(file_path: Path, output_file: Path) -> bool:
    """Checks if a file is an export artifact or generated output file."""
    file_name = file_path.name.lower()
    
    # Exclude target output file
    if file_path.resolve() == output_file.resolve():
        return True

    # Exclude known export files
    if file_name in DEFAULT_EXCLUDE_FILES:
        return True

    # Exclude pattern-matched export files (e.g. *_export.txt, *_export.md)
    if (file_name.endswith("_export.txt") or file_name.endswith("_export.md") or 
        file_name.endswith("_export.json") or (file_name.startswith("export_") and file_name.endswith((".txt", ".md")))):
        return True

    return False


def export_repository(
    root_dir: str = ".",
    output_file: str = "code_export.txt",
    target_folder: str = None,
    include_extensions: set = DEFAULT_INCLUDE_EXTENSIONS,
    max_size_kb: int = 500
):
    """
    Scans the repository and aggregates relevant source files into a single text file.
    """
    root_path = Path(root_dir).resolve()
    out_path = Path(output_file).resolve()
    max_file_size_bytes = max_size_kb * 1024
    
    if target_folder:
        search_path = (root_path / target_folder).resolve()
        if not search_path.exists():
            print(f"Error: Directory '{target_folder}' does not exist.")
            return
    else:
        search_path = root_path

    print(f"Scanning directory: {search_path}")
    print(f"Max file size limit: {max_size_kb} KB")
    
    exported_files_count = 0
    total_lines = 0

    with open(out_path, "w", encoding="utf-8") as out:
        out.write("=================================================================\n")
        out.write(f" ASTRA REPOSITORY CODE EXPORT\n")
        out.write(f" Target Path: {search_path.relative_to(root_path) if search_path != root_path else '.'}\n")
        out.write("=================================================================\n\n")

        for current_root, dirs, files in os.walk(search_path):
            # Exclude ignored directories in-place so os.walk doesn't enter them
            dirs[:] = [d for d in dirs if d not in DEFAULT_EXCLUDE_DIRS and not d.startswith('.')]

            for file_name in sorted(files):
                file_path = Path(current_root) / file_name
                rel_path = file_path.relative_to(root_path)

                # Skip export output files and artifacts
                if is_export_artifact(file_path, out_path):
                    print(f"  [-] Skipped artifact: {rel_path}")
                    continue

                # Check extension filter
                if file_path.suffix.lower() not in include_extensions:
                    continue

                if file_path.suffix.lower() in DEFAULT_EXCLUDE_EXTENSIONS:
                    continue

                # Check file size limit
                file_size = file_path.stat().st_size
                if file_size > max_file_size_bytes:
                    print(f"  [-] Skipped large file: {rel_path} ({file_size / 1024:.1f} KB > {max_size_kb} KB)")
                    continue

                try:
                    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                        content = f.read()
                        line_count = len(content.splitlines())

                    out.write(f"\n{'='*70}\n")
                    out.write(f"FILE: {rel_path} ({line_count} lines)\n")
                    out.write(f"{'='*70}\n\n")
                    out.write(content)
                    out.write("\n\n")

                    exported_files_count += 1
                    total_lines += line_count
                    print(f"  [+] Included: {rel_path} ({line_count} lines)")

                except Exception as e:
                    print(f"  [-] Skipped {rel_path} due to error: {e}")

    print("\n-----------------------------------------------------------------")
    print(f"Export Complete! Exported {exported_files_count} files ({total_lines} lines).")
    print(f"Output saved to: {out_path}")
    print("-----------------------------------------------------------------")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export project code into a single text file for AI analysis.")
    parser.add_argument("-o", "--output", default="code_export.txt", help="Output text file path (default: code_export.txt)")
    parser.add_argument("-f", "--folder", default=None, help="Export only a specific subfolder (e.g. western, jyotish, rag)")
    parser.add_argument("-s", "--max-size", type=int, default=500, help="Maximum file size in KB to include (default: 500 KB)")
    
    args = parser.parse_args()
    export_repository(output_file=args.output, target_folder=args.folder, max_size_kb=args.max_size)
