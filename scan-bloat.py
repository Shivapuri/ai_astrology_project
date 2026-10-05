#!/usr/bin/env python3
"""
scan_bloat.py — Astra Codebase Size & Bloat Profiler
====================================================
A standalone zero-dependency diagnostic tool to pinpoint why your codebase
or export bundle is ballooning in size.

Usage:
    python scan_bloat.py
    python scan_bloat.py --path ./jyotish
    python scan_bloat.py --top 25
    python scan_bloat.py --include-all  # Includes .git, .venv, etc.
"""

import os
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Standard directories to skip by default so they don't skew code analysis
DEFAULT_EXCLUDES = {
    ".git", ".venv", "venv", "env", "__pycache__", ".pytest_cache",
    ".idea", ".vscode", "node_modules", "dist", "build", ".mypy_cache"
}

# ANSI color codes for terminal display
CLR_RESET  = "\033[0m"
CLR_BOLD   = "\033[1m"
CLR_RED    = "\033[31m"
CLR_GREEN  = "\033[32m"
CLR_YELLOW = "\033[33m"
CLR_BLUE   = "\033[34m"
CLR_CYAN   = "\033[36m"
CLR_GRAY   = "\033[90m"

def disable_colors():
    global CLR_RESET, CLR_BOLD, CLR_RED, CLR_GREEN, CLR_YELLOW, CLR_BLUE, CLR_CYAN, CLR_GRAY
    CLR_RESET = CLR_BOLD = CLR_RED = CLR_GREEN = CLR_YELLOW = CLR_BLUE = CLR_CYAN = CLR_GRAY = ""

def format_size(bytes_val: int) -> str:
    """Formats bytes into human-readable B, KB, MB, GB."""
    if bytes_val < 1024:
        return f"{bytes_val} B"
    elif bytes_val < 1024 * 1024:
        return f"{bytes_val / 1024:.1f} KB"
    elif bytes_val < 1024 * 1024 * 1024:
        return f"{bytes_val / (1024 * 1024):.2f} MB"
    else:
        return f"{bytes_val / (1024 * 1024 * 1024):.2f} GB"

def count_lines(filepath: Path) -> Optional[int]:
    """Safely counts lines in text files. Returns None if binary or unreadable."""
    try:
        with open(filepath, "rb") as f:
            # Quick binary check: read first 1024 bytes and check for null bytes
            chunk = f.read(1024)
            if b"\x00" in chunk:
                return None
            f.seek(0)
            return sum(1 for _ in f)
    except Exception:
        return None

def analyze_directory(root_path: Path, exclude_dirs: set, top_n: int = 20):
    total_project_bytes = 0
    total_project_files = 0
    total_project_lines = 0

    all_files: List[Dict] = []
    dir_sizes: Dict[str, int] = {}
    ext_stats: Dict[str, Dict] = {}

    print(f"{CLR_CYAN}Scanning: {CLR_BOLD}{root_path.resolve()}{CLR_RESET}...\n")

    for dirpath, dirnames, filenames in os.walk(root_path):
        # In-place modify dirnames to skip excluded folders
        if exclude_dirs:
            dirnames[:] = [d for d in dirnames if d not in exclude_dirs]

        rel_dir = os.path.relpath(dirpath, root_path)
        if rel_dir == ".":
            rel_dir = "[root]"

        current_dir_bytes = 0

        for fname in filenames:
            fpath = Path(dirpath) / fname
            try:
                stat = fpath.stat()
                size = stat.st_size
            except Exception:
                continue

            total_project_bytes += size
            total_project_files += 1
            current_dir_bytes += size

            ext = fpath.suffix.lower() or "[no ext]"
            lines = count_lines(fpath)

            if lines is not None:
                total_project_lines += lines

            # Track extension stats
            if ext not in ext_stats:
                ext_stats[ext] = {"size": 0, "count": 0, "lines": 0}
            ext_stats[ext]["size"] += size
            ext_stats[ext]["count"] += 1
            if lines is not None:
                ext_stats[ext]["lines"] += lines

            all_files.append({
                "path": str(fpath.relative_to(root_path)),
                "size": size,
                "lines": lines,
                "ext": ext,
                "is_binary": (lines is None)
            })

        # Add size to directory tree
        dir_sizes[rel_dir] = dir_sizes.get(rel_dir, 0) + current_dir_bytes

    if total_project_files == 0:
        print(f"{CLR_RED}No files found in {root_path}{CLR_RESET}")
        return

    # -------------------------------------------------------------------------
    # 1. SUMMARY OVERVIEW
    # -------------------------------------------------------------------------
    print(f"{CLR_BOLD}{'=' * 85}{CLR_RESET}")
    print(f" {CLR_BOLD}{CLR_GREEN}PROJECT SUMMARY OVERVIEW{CLR_RESET}")
    print(f"{CLR_BOLD}{'=' * 85}{CLR_RESET}")
    print(f" • Total Scanned Size : {CLR_BOLD}{CLR_YELLOW}{format_size(total_project_bytes)}{CLR_RESET}")
    print(f" • Total File Count   : {CLR_BOLD}{total_project_files:,}{CLR_RESET} files")
    print(f" • Total Code/Text    : {CLR_BOLD}{total_project_lines:,}{CLR_RESET} lines")
    print(f"{CLR_BOLD}{'-' * 85}{CLR_RESET}\n")

    # -------------------------------------------------------------------------
    # 2. BREAKDOWN BY FILE TYPE / EXTENSION
    # -------------------------------------------------------------------------
    print(f"{CLR_BOLD}{'=' * 85}{CLR_RESET}")
    print(f" {CLR_BOLD}{CLR_CYAN}SPACE CONSUMPTION BY FILE EXTENSION{CLR_RESET}")
    print(f"{CLR_BOLD}{'=' * 85}{CLR_RESET}")
    print(f" {'EXT':<12} {'TOTAL SIZE':<15} {'% OF TOTAL':<12} {'FILES':<10} {'LINES':<12}")
    print(f" {'-' * 10}   {'-' * 12}    {'-' * 10}   {'-' * 8}   {'-' * 10}")

    sorted_exts = sorted(ext_stats.items(), key=lambda x: x[1]["size"], reverse=True)
    for ext, stats in sorted_exts[:12]:
        pct = (stats["size"] / total_project_bytes * 100) if total_project_bytes else 0
        line_str = f"{stats['lines']:,}" if stats["lines"] > 0 else "— (binary)"
        color = CLR_RED if pct >= 25 else (CLR_YELLOW if pct >= 10 else CLR_RESET)
        print(f" {ext:<12} {format_size(stats['size']):<15} {color}{pct:>5.1f} %{CLR_RESET}     {stats['count']:<10} {line_str:<12}")
    print(f"{CLR_BOLD}{'-' * 85}{CLR_RESET}\n")

    # -------------------------------------------------------------------------
    # 3. TOP HEAVIEST DIRECTORIES
    # -------------------------------------------------------------------------
    print(f"{CLR_BOLD}{'=' * 85}{CLR_RESET}")
    print(f" {CLR_BOLD}{CLR_BLUE}TOP {min(top_n, len(dir_sizes))} HEAVIEST DIRECTORIES (IMMEDIATE FOLDER SIZE){CLR_RESET}")
    print(f"{CLR_BOLD}{'=' * 85}{CLR_RESET}")
    print(f" {'SIZE':<14} {'% OF PROJECT':<14} {'DIRECTORY PATH'}")
    print(f" {'-' * 12}   {'-' * 12}   {'-' * 55}")

    sorted_dirs = sorted(dir_sizes.items(), key=lambda x: x[1], reverse=True)
    for dname, dsize in sorted_dirs[:top_n]:
        if dsize == 0:
            continue
        pct = (dsize / total_project_bytes * 100) if total_project_bytes else 0
        d_col = CLR_RED if pct >= 20 else (CLR_YELLOW if pct >= 8 else CLR_RESET)
        print(f" {format_size(dsize):<14} {d_col}{pct:>5.1f} %{CLR_RESET}        {dname}")
    print(f"{CLR_BOLD}{'-' * 85}{CLR_RESET}\n")

    # -------------------------------------------------------------------------
    # 4. TOP LARGEST INDIVIDUAL FILES
    # -------------------------------------------------------------------------
    print(f"{CLR_BOLD}{'=' * 85}{CLR_RESET}")
    print(f" {CLR_BOLD}{CLR_YELLOW}TOP {min(top_n, len(all_files))} LARGEST INDIVIDUAL FILES{CLR_RESET}")
    print(f"{CLR_BOLD}{'=' * 85}{CLR_RESET}")
    print(f" {'SIZE':<12} {'LINES':<10} {'TYPE':<10} {'FILE PATH'}")
    print(f" {'-' * 10}   {'-' * 8}   {'-' * 8}   {'-' * 55}")

    all_files.sort(key=lambda x: x["size"], reverse=True)
    for f in all_files[:top_n]:
        size_str = format_size(f["size"])
        lines_str = f"{f['lines']:,}" if f["lines"] is not None else "binary"
        kind = "Binary" if f["is_binary"] else "Text/Code"
        color = CLR_RED if f["size"] >= 200 * 1024 else (CLR_YELLOW if f["size"] >= 80 * 1024 else CLR_RESET)
        print(f" {color}{size_str:<12}{CLR_RESET} {lines_str:<10} {kind:<10} {f['path']}")
    print(f"{CLR_BOLD}{'-' * 85}{CLR_RESET}\n")

    # -------------------------------------------------------------------------
    # 5. BUNDLE BLOAT DIAGNOSTIC (Why is your export > 3MB?)
    # -------------------------------------------------------------------------
    bloaters = [f for f in all_files if f["size"] >= 80 * 1024 or f["ext"] in {".db", ".sqlite", ".sqlite3", ".se1", ".pdf", ".png", ".jpg", ".tar", ".zip"}]

    if bloaters:
        print(f"{CLR_BOLD}{'=' * 85}{CLR_RESET}")
        print(f" {CLR_BOLD}{CLR_RED}⚠️ BUNDLE BLOAT DIAGNOSTIC (PRIMARY CULPRITS BEHIND LARGE EXPORTS){CLR_RESET}")
        print(f"{CLR_BOLD}{'=' * 85}{CLR_RESET}")
        print(" These files disproportionately bloat your codebase export bundles:\n")
        for b in bloaters[:15]:
            reason = "Binary Database" if b["ext"] in {".db", ".sqlite", ".sqlite3"} else (
                "Swiss Ephemeris Data" if b["ext"] == ".se1" else (
                    "Large JSON Data Dump" if b["ext"] == ".json" else (
                        "Heavy Monolithic Python File" if b["ext"] == ".py" else "Large Asset"
                    )
                )
            )
            print(f" • {CLR_BOLD}{format_size(b['size']):<10}{CLR_RESET} [{reason:<26}] {b['path']}")
        print(f"{CLR_BOLD}{'-' * 85}{CLR_RESET}\n")

def main():
    parser = argparse.ArgumentParser(description="Astra Codebase Size & Bloat Scanner")
    parser.add_argument("--path", "-p", type=str, default=".", help="Root directory to analyze (default: current directory)")
    parser.add_argument("--top", "-t", type=int, default=20, help="Number of top files and folders to display (default: 20)")
    parser.add_argument("--include-all", "-a", action="store_true", help="Include .git, .venv, and other caches")
    parser.add_argument("--no-color", action="store_true", help="Disable colored terminal output")

    args = parser.parse_args()

    if args.no_color or not sys.stdout.isatty():
        disable_colors()

    root = Path(args.path)
    if not root.exists():
        print(f"Error: Path '{args.path}' does not exist.")
        sys.exit(1)

    excludes = set() if args.include_all else DEFAULT_EXCLUDES
    analyze_directory(root, excludes, top_n=args.top)

if __name__ == "__main__":
    main()