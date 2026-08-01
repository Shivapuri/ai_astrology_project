#!/usr/bin/env python3
"""
Astra Repository Code Exporter
Combines key code files into a single text file for AI analysis.
"""

import os
import argparse
from pathlib import Path

# Directories and files to ignore during export
DEFAULT_EXCLUDE_DIRS = {
    ".git", ".idea", "__pycache__", "venv", ".venv", 
    "cache", "chroma_astrology_db", "astrology_rag_data"
}

DEFAULT_EXCLUDE_EXTENSIONS = {
    ".dat", ".bsp", ".download", ".log", ".db", ".sqlite", ".pyc", ".png", ".jpg"
}

# Key text/code extensions to include
DEFAULT_INCLUDE_EXTENSIONS = {
    ".py", ".md", ".json", ".txt"
}

def export_repository(
    root_dir: str = ".",
    output_file: str = "code_export.txt",
    target_folder: str = None,
    include_extensions: set = DEFAULT_INCLUDE_EXTENSIONS
):
    """
    Scans the repository and aggregates relevant source files into a single text file.
    """
    root_path = Path(root_dir).resolve()
    
    if target_folder:
        search_path = (root_path / target_folder).resolve()
        if not search_path.exists():
            print(f"Error: Directory '{target_folder}' does not exist.")
            return
    else:
        search_path = root_path

    print(f"Scanning directory: {search_path}")
    
    exported_files_count = 0
    total_lines = 0

    with open(output_file, "w", encoding="utf-8") as out:
        out.write("=================================================================\n")
        out.write(f" ASTRA REPOSITORY CODE EXPORT\n")
        out.write(f" Target Path: {search_path.relative_to(root_path) if search_path != root_path else '.'}\n")
        out.write("=================================================================\n\n")

        for current_root, dirs, files in os.walk(search_path):
            # Exclude ignored directories in-place so os.walk doesn't enter them
            dirs[:] = [d for d in dirs if d not in DEFAULT_EXCLUDE_DIRS]

            for file_name in sorted(files):
                file_path = Path(current_root) / file_name
                rel_path = file_path.relative_to(root_path)

                # Skip output file itself
                if file_path.name == Path(output_file).name:
                    continue

                # Check extension filter
                if file_path.suffix.lower() not in include_extensions:
                    continue

                if file_path.suffix.lower() in DEFAULT_EXCLUDE_EXTENSIONS:
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
    print(f"Output saved to: {Path(output_file).resolve()}")
    print("-----------------------------------------------------------------")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export project code into a single text file for AI analysis.")
    parser.add_argument("-o", "--output", default="code_export.txt", help="Output text file path (default: code_export.txt)")
    parser.add_argument("-f", "--folder", default=None, help="Export only a specific subfolder (e.g. western, jyotish, rag)")
    
    args = parser.parse_args()
    export_repository(output_file=args.output, target_folder=args.folder)
