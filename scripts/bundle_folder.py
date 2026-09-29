#!/usr/bin/env python3
"""
scripts/bundle_folder.py
========================
Bundles all code, markdown, and text files from any repository folder into a single,
beautifully formatted text file with clean headers and a Table of Contents.

Key Features:
- Respects .gitignore: Uses Git to automatically ignore cache files (__pycache__, .pytest_cache, .DS_Store, etc.).
- Universal Folder Support: Works on any folder (e.g., `jyotish/yogas`, `jyotish/avasthas`, `static/js`).
- Clean Visual Headers: Every file has a clear delimiter banner showing its name, lines, and size.
- Binary Guard: Automatically skips binary files (images, audio, compiled binaries).
- Flexible Filtering: Filter by extensions (e.g. `--ext py,md`) or bundle all text files by default.

Usage Examples:
    python scripts/bundle_folder.py jyotish/yogas
    python scripts/bundle_folder.py jyotish/yogas --ext py,md -o yogas_bundle.txt
    python scripts/bundle_folder.py static/js --summary
"""

import os
import sys
import argparse
import subprocess
from datetime import datetime
from typing import List, Dict, Any, Optional, Set, Tuple

# Default text and code file extensions to include
DEFAULT_TEXT_EXTENSIONS = {
    ".py",
    ".md",
    ".txt",
    ".json",
    ".html",
    ".js",
    ".css",
    ".yaml",
    ".yml",
    ".sh",
    ".sql",
    ".csv",
    ".toml",
    ".ini",
    ".xml",
}

# Known binary extensions to strictly avoid
BINARY_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".svg",
    ".ico",
    ".pdf",
    ".epub",
    ".mp3",
    ".wav",
    ".ogg",
    ".pyc",
    ".pyd",
    ".so",
    ".dylib",
    ".dll",
    ".exe",
    ".db",
    ".sqlite",
    ".sqlite3",
    ".se1",
    ".bin",
    ".zip",
    ".tar",
    ".gz",
    ".tar.gz",
    ".DS_Store",
    ".woff",
    ".woff2",
    ".ttf",
    ".eot",
}

# Fallback ignore directories if not in a Git repository
FALLBACK_IGNORE_DIRS = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    "node_modules",
    "venv",
    ".venv",
    "env",
    ".idea",
    ".vscode",
}


def is_binary_file(filepath: str) -> bool:
    """Checks if a file is binary based on extension and first byte probe."""
    ext = os.path.splitext(filepath)[1].lower()
    if ext in BINARY_EXTENSIONS:
        return True

    # Check first 1024 bytes for null byte
    try:
        with open(filepath, "rb") as f:
            chunk = f.read(1024)
            if b"\x00" in chunk:
                return True
    except Exception:
        return True

    return False


def get_git_repo_root(start_dir: str) -> Optional[str]:
    """Finds the root directory of the Git repository, if applicable."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=start_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except Exception:
        return None


def collect_files_via_git(
    folder_abs: str,
    repo_root: str,
    allowed_exts: Optional[Set[str]] = None,
) -> List[str]:
    """
    Uses Git to list all tracked and untracked files while strictly respecting .gitignore.
    Returns sorted list of paths relative to repo_root.
    """
    rel_folder = os.path.relpath(folder_abs, repo_root)
    path_spec = "." if rel_folder == "." else rel_folder

    cmd = ["git", "ls-files", "--cached", "--others", "--exclude-standard", "--", path_spec]
    try:
        proc = subprocess.run(
            cmd,
            cwd=repo_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
        raw_lines = [line.strip() for line in proc.stdout.splitlines() if line.strip()]
    except Exception as e:
        sys.stderr.write(f"Warning: Git command failed ({e}). Falling back to filesystem walk.\n")
        return []

    collected = []
    for rel_path in raw_lines:
        full_path = os.path.join(repo_root, rel_path)
        if not os.path.isfile(full_path):
            continue

        ext = os.path.splitext(rel_path)[1].lower()
        if allowed_exts is not None and ext not in allowed_exts:
            continue

        if is_binary_file(full_path):
            continue

        collected.append(rel_path)

    return sorted(collected, key=lambda p: (os.path.dirname(p), os.path.basename(p) != "__init__.py", p))


def collect_files_fallback(
    folder_abs: str,
    allowed_exts: Optional[Set[str]] = None,
) -> List[str]:
    """
    Fallback filesystem walk when not in a Git repository.
    Returns sorted list of absolute paths.
    """
    collected = []
    for root, dirs, files in os.walk(folder_abs):
        # Prune ignored directory names in-place
        dirs[:] = [d for d in dirs if d not in FALLBACK_IGNORE_DIRS]

        for file in files:
            full_path = os.path.join(root, file)
            ext = os.path.splitext(file)[1].lower()

            if allowed_exts is not None and ext not in allowed_exts:
                continue

            if is_binary_file(full_path):
                continue

            collected.append(full_path)

    return sorted(collected, key=lambda p: (os.path.dirname(p), os.path.basename(p) != "__init__.py", p))


def collect_folder_files(
    target_folder: str,
    extensions: Optional[List[str]] = None,
) -> Tuple[str, List[Tuple[str, str]]]:
    """
    Discovers files in target_folder respecting .gitignore and text filtering.
    Returns:
        (base_dir, [(relative_display_path, absolute_file_path), ...])
    """
    abs_folder = os.path.abspath(target_folder)
    if not os.path.isdir(abs_folder):
        raise ValueError(f"Target path '{target_folder}' is not a valid directory.")

    allowed_exts = None
    if extensions:
        allowed_exts = {ext if ext.startswith(".") else f".{ext}" for ext in extensions}
        allowed_exts = {e.lower() for e in allowed_exts}
    else:
        allowed_exts = DEFAULT_TEXT_EXTENSIONS

    repo_root = get_git_repo_root(abs_folder)
    file_tuples = []

    if repo_root:
        rel_files = collect_files_via_git(abs_folder, repo_root, allowed_exts=allowed_exts)
        for rel in rel_files:
            full = os.path.join(repo_root, rel)
            # Display relative to target folder if folder is inside repo
            rel_display = os.path.relpath(full, abs_folder)
            file_tuples.append((rel_display, full))
        base_dir = abs_folder
    else:
        full_files = collect_files_fallback(abs_folder, allowed_exts=allowed_exts)
        for full in full_files:
            rel_display = os.path.relpath(full, abs_folder)
            file_tuples.append((rel_display, full))
        base_dir = abs_folder

    return base_dir, file_tuples


def format_file_type(filepath: str) -> str:
    """Returns a simple human-readable language/type label."""
    ext = os.path.splitext(filepath)[1].lower()
    mapping = {
        ".py": "Python Source",
        ".md": "Markdown Document",
        ".txt": "Plain Text",
        ".json": "JSON Data",
        ".html": "HTML Template",
        ".js": "JavaScript",
        ".css": "CSS Stylesheet",
        ".yaml": "YAML Configuration",
        ".yml": "YAML Configuration",
        ".sh": "Shell Script",
        ".sql": "SQL Database Script",
    }
    return mapping.get(ext, f"{ext.upper().lstrip('.')} File")


def generate_bundle(
    target_folder: str,
    output_path: Optional[str] = None,
    extensions: Optional[List[str]] = None,
    summary_only: bool = False,
) -> Dict[str, Any]:
    """
    Bundles the target folder into a single structured text file.
    """
    abs_folder, file_entries = collect_folder_files(target_folder, extensions=extensions)

    if not file_entries:
        print(f"No matching text or code files found in '{target_folder}'.")
        return {"files_count": 0, "total_lines": 0, "total_bytes": 0, "output_path": None}

    # Read and inspect files
    manifest = []
    for rel_display, full_path in file_entries:
        try:
            with open(full_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
        except Exception as e:
            content = f"// Error reading file: {e}\n"

        lines = len(content.splitlines())
        raw_bytes = len(content.encode("utf-8"))
        ftype = format_file_type(full_path)

        manifest.append({
            "rel_path": rel_display,
            "full_path": full_path,
            "lines": lines,
            "bytes": raw_bytes,
            "type": ftype,
            "content": content,
        })

    total_lines = sum(item["lines"] for item in manifest)
    total_bytes = sum(item["bytes"] for item in manifest)
    total_kb = total_bytes / 1024
    folder_name = os.path.basename(os.path.normpath(abs_folder)) or "root"

    # Determine default output file name if not provided
    if output_path is None:
        # Generate slug like 'bundle_yogas.txt' or 'bundle_jyotish_yogas.txt'
        rel_to_cwd = os.path.relpath(abs_folder, os.getcwd())
        slug = rel_to_cwd.replace(os.sep, "_").strip("._")
        if not slug:
            slug = folder_name
        output_path = f"bundle_{slug}.txt"

    if summary_only:
        print("=" * 80)
        print(f"BUNDLE SUMMARY: {abs_folder}")
        print(f"Total Files: {len(manifest)} | Total Lines: {total_lines:,} | Size: {total_kb:.1f} KB")
        print("=" * 80)
        for idx, item in enumerate(manifest, 1):
            print(f"  {idx:2d}. {item['rel_path']:<45} [{item['type']}] ({item['lines']:,} lines, {item['bytes']/1024:.1f} KB)")
        print("=" * 80)
        return {
            "files_count": len(manifest),
            "total_lines": total_lines,
            "total_bytes": total_bytes,
            "output_path": None,
        }

    # Generate bundle file with headers
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(output_path, "w", encoding="utf-8") as out:
        # Master Executive Header
        out.write("# " + "=" * 78 + "\n")
        out.write(f"# ASTRA CODEBASE FOLDER BUNDLE\n")
        out.write(f"# FOLDER: {abs_folder}\n")
        out.write(f"# GENERATED: {now_str}\n")
        out.write(f"# TOTAL FILES: {len(manifest)}\n")
        out.write(f"# TOTAL LINES: {total_lines:,}\n")
        out.write(f"# TOTAL SIZE: {total_kb:.1f} KB\n")
        out.write("# " + "=" * 78 + "\n\n")

        # Table of Contents
        out.write("# " + "-" * 78 + "\n")
        out.write("# TABLE OF CONTENTS\n")
        out.write("# " + "-" * 78 + "\n")
        for idx, item in enumerate(manifest, 1):
            out.write(f"# {idx:2d}. {item['rel_path']} ({item['lines']:,} lines | {item['bytes']/1024:.1f} KB | {item['type']})\n")
        out.write("# " + "-" * 78 + "\n\n")

        # Individual File Blocks
        for item in manifest:
            rel = item["rel_path"]
            ftype = item["type"]
            lines = item["lines"]
            size_kb = item["bytes"] / 1024

            out.write("=" * 80 + "\n")
            out.write(f"FILE: {rel}\n")
            out.write(f"TYPE: {ftype} | LINES: {lines:,} | SIZE: {size_kb:.1f} KB\n")
            out.write("=" * 80 + "\n")
            out.write(item["content"])
            out.write("\n\n")

    print("\n" + "=" * 80)
    print(f"🎉 Folder bundle successfully created!")
    print(f"📁 Source Folder: {abs_folder}")
    print(f"📄 Output File:   {os.path.abspath(output_path)}")
    print(f"📊 Statistics:    {len(manifest)} files | {total_lines:,} lines | {total_kb:.1f} KB")
    print("=" * 80 + "\n")

    return {
        "files_count": len(manifest),
        "total_lines": total_lines,
        "total_bytes": total_bytes,
        "output_path": os.path.abspath(output_path),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Bundle any folder's Python, Markdown, and text files into a single structured file with headers."
    )
    parser.add_argument(
        "folder",
        nargs="?",
        default=".",
        help="Target folder to bundle (e.g. 'jyotish/yogas', 'jyotish/avasthas', or '.')",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="Output text file path (default: auto-named 'bundle_<folder_name>.txt')",
    )
    parser.add_argument(
        "-e",
        "--ext",
        default=None,
        help="Comma-separated list of file extensions to include (e.g. 'py,md' or 'py,md,txt')",
    )
    parser.add_argument(
        "-s",
        "--summary",
        action="store_true",
        help="Print file inventory summary without writing bundle",
    )

    args = parser.parse_args()

    ext_list = None
    if args.ext:
        ext_list = [e.strip() for e in args.ext.split(",") if e.strip()]

    generate_bundle(
        target_folder=args.folder,
        output_path=args.output,
        extensions=ext_list,
        summary_only=args.summary,
    )


if __name__ == "__main__":
    main()
