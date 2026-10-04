#!/usr/bin/env python3
"""
scripts/audit_ephemeris_usage.py
Astra Repository Ephemeris & Redundant Calculation Auditor.

Scans the entire Astra codebase using Python's Abstract Syntax Tree (AST) to:
1. Group and display all direct Swiss Ephemeris (`swe.*` / `swisseph.*`) calls by PARENT FOLDER.
2. Identify redundant coordinate, distance, and varga calculations.
3. Generate a structured terminal output and markdown inventory (`ephemeris_migration_inventory.md`).
"""

import os
import sys
import ast
from pathlib import Path
from typing import List, Dict, Any

# Swiss Ephemeris function mappings to ChartBaseline replacements
SWE_MAPPING = {
    "calc_ut": "baseline.coordinates[planet]['longitude'|'latitude'|'speed'] or ['declination'|'right_ascension']",
    "calc": "baseline.coordinates[planet]['longitude']",
    "houses": "baseline.astronomical_anchors['asc_longitude'|'mc_longitude'|'campanus_display_cusps']",
    "houses_armc": "baseline.astronomical_anchors['campanus_display_cusps']",
    "house_pos": "baseline.astronomical_anchors['campanus_display_cusps']",
    "julday": "baseline.astronomical_anchors['jd_utc'|'jd_local']",
    "revjul": "baseline.astronomical_anchors['jd_utc'|'cal_flag']",
    "rise_trans": "baseline.astronomical_anchors['sunrise_jd'|'sunset_jd']",
    "solcross_ut": "baseline.astronomical_anchors['temporal_lords']['Masa'|'Varsha']",
    "fixstar2_ut": "baseline.nakshatras['equatorial_ayanamsa'|'ecliptic_ayanamsa']",
    "fixstar_ut": "baseline.nakshatras['equatorial_ayanamsa']",
    "get_ayanamsa_ut": "baseline.nakshatras['equatorial_ayanamsa'|'ecliptic_ayanamsa']",
    "set_sid_mode": "baseline.nakshatras['system']",
    "get_orbital_elements": "baseline.coordinates[planet]['speed'] / baseline.astronomical_anchors"
}


class EphemerisVisitor(ast.NodeVisitor):
    def __init__(self, filename: str, lines: List[str]):
        self.filename = filename
        self.lines = lines
        self.swe_aliases = set()
        self.findings = []

    def visit_Import(self, node):
        for alias in node.names:
            if "swisseph" in alias.name:
                asname = alias.asname or alias.name
                self.swe_aliases.add(asname)
                self.findings.append({
                    "type": "IMPORT",
                    "line": node.lineno,
                    "symbol": alias.name,
                    "code": self.lines[node.lineno - 1].strip(),
                    "category": "Ephemeris Import",
                    "replacement": "from jyotish.baseline import ChartBaseline"
                })
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module and "swisseph" in node.module:
            for alias in node.names:
                asname = alias.asname or alias.name
                self.swe_aliases.add(asname)
                self.findings.append({
                    "type": "IMPORT_FROM",
                    "line": node.lineno,
                    "symbol": f"{node.module}.{alias.name}",
                    "code": self.lines[node.lineno - 1].strip(),
                    "category": "Ephemeris Import",
                    "replacement": "from jyotish.baseline import ChartBaseline"
                })
        self.generic_visit(node)

    def visit_Call(self, node):
        call_name = ""
        # Match `swe.function(...)`
        if isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                module_name = node.func.value.id
                func_name = node.func.attr
                if module_name in self.swe_aliases or module_name in ("swe", "swisseph"):
                    snippet = self.lines[node.lineno - 1].strip()
                    replacement = SWE_MAPPING.get(func_name, "baseline.<property>")
                    self.findings.append({
                        "type": "SWE_CALL",
                        "line": node.lineno,
                        "symbol": f"{module_name}.{func_name}",
                        "code": snippet,
                        "category": "Direct Ephemeris Calculation",
                        "replacement": replacement
                    })
        # Match direct imported calls e.g., `calc_ut(...)`
        elif isinstance(node.func, ast.Name):
            func_name = node.func.id
            if func_name in self.swe_aliases or func_name in SWE_MAPPING:
                snippet = self.lines[node.lineno - 1].strip()
                replacement = SWE_MAPPING.get(func_name, "baseline.<property>")
                self.findings.append({
                    "type": "SWE_CALL",
                    "line": node.lineno,
                    "symbol": func_name,
                    "code": snippet,
                    "category": "Direct Ephemeris Calculation",
                    "replacement": replacement
                })
            # Match redundant calculate_varga_longitude loops
            elif func_name == "calculate_varga_longitude":
                snippet = self.lines[node.lineno - 1].strip()
                self.findings.append({
                    "type": "REDUNDANT_VARGA",
                    "line": node.lineno,
                    "symbol": "calculate_varga_longitude",
                    "code": snippet,
                    "category": "Redundant Varga Projection",
                    "replacement": "baseline.vargas[varga_name]['grahas'][planet]['longitude']"
                })
        self.generic_visit(node)


def scan_file(filepath: Path) -> List[Dict[str, Any]]:
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            lines = content.splitlines()
        tree = ast.parse(content, filename=str(filepath))
        visitor = EphemerisVisitor(str(filepath), lines)
        visitor.visit(tree)
        return visitor.findings
    except Exception:
        return []


def run_audit(project_root: Path) -> Dict[str, Any]:
    # Exclude virtual environments, cache, and certified Stage 1 files
    ignored_dirs = {".git", ".venv", "venv", "__pycache__", ".pytest_cache", "site-packages", "build", "dist"}
    certified_baseline_files = {"baseline.py", "baseline_tables.py", "baseline_math.py"}

    # Grouping structure: by_folder[parent_folder][file_path] = list_of_findings
    by_folder: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}
    total_calls = 0
    total_files = 0

    for py_file in sorted(project_root.rglob("*.py")):
        if any(part in ignored_dirs for part in py_file.parts):
            continue
        # Exclude certified Stage 1 baseline files
        if py_file.name in certified_baseline_files:
            continue

        findings = scan_file(py_file)
        if findings:
            rel_file_path = str(py_file.relative_to(project_root))
            rel_parent = str(py_file.parent.relative_to(project_root))
            if rel_parent == ".":
                rel_parent = "[Project Root]"
            else:
                rel_parent = rel_parent.rstrip("/") + "/"

            if rel_parent not in by_folder:
                by_folder[rel_parent] = {}

            by_folder[rel_parent][rel_file_path] = findings
            total_calls += len(findings)
            total_files += 1

    return {
        "by_folder": by_folder,
        "total_files": total_files,
        "total_ephemeris_points": total_calls,
        "total_folders": len(by_folder)
    }


def main():
    # Smart root detection: check current directory or parent directory for 'jyotish'
    if len(sys.argv) > 1:
        root = Path(sys.argv[1]).resolve()
    else:
        cwd = Path.cwd().resolve()
        if (cwd / "jyotish").exists():
            root = cwd
        elif (cwd.parent / "jyotish").exists():
            root = cwd.parent
        else:
            root = cwd

    print("=" * 85)
    print(f"  ASTRA EPHEMERIS USAGE AUDITOR (GROUPED BY PARENT FOLDER)")
    print(f"  Root Directory: {root}")
    print("=" * 85)

    report = run_audit(root)

    by_folder = report["by_folder"]
    total_calls = report["total_ephemeris_points"]
    total_files = report["total_files"]
    total_folders = report["total_folders"]

    if not by_folder:
        print("\n✅ Zero redundant Swiss Ephemeris calls found outside the certified Stage 1 baseline!")
        return

    print(f"\n⚠️  Found {total_calls} direct calls across {total_files} files in {total_folders} parent folders.\n")

    # 1. High-level Summary Breakdown by Parent Folder
    print("📊 DIRECTORY-LEVEL BREAKDOWN:")
    print("-" * 85)
    for folder, files_dict in sorted(by_folder.items(), key=lambda x: sum(len(f) for f in x[1].values()), reverse=True):
        folder_calls = sum(len(f) for f in files_dict.values())
        print(f"  📁 {folder:<38} : {len(files_dict):>2} file(s) | {folder_calls:>3} ephemeris calls")
    print("-" * 85)
    print()

    # 2. Detailed Findings Grouped by Parent Folder
    for folder, files_dict in sorted(by_folder.items()):
        folder_calls = sum(len(f) for f in files_dict.values())
        print("=" * 85)
        print(f"📁 PARENT FOLDER: {folder} ({len(files_dict)} file(s), {folder_calls} calls)")
        print("=" * 85)

        for file_path, findings in files_dict.items():
            file_name = Path(file_path).name
            print(f"\n  📄 FILE: {file_name}  (Path: {file_path})")
            print(f"  {'-' * 80}")
            for item in findings:
                print(f"    • Line {item['line']:<4} | [{item['category']}]")
                print(f"      Current:     {item['code']}")
                print(f"      Replacement: ➔ {item['replacement']}")
                print()

    # 3. Export to Markdown Inventory
    report_file = root / "ephemeris_migration_inventory.md"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write("# Astra Ephemeris Migration Inventory\n\n")
        f.write(f"Total Direct Ephemeris Calls: **{total_calls}**  \n")
        f.write(f"Total Files Affected: **{total_files}**  \n")
        f.write(f"Total Parent Directories: **{total_folders}**  \n\n")

        f.write("## 📊 Summary by Parent Directory\n\n")
        f.write("| Parent Folder | Affected Files | Direct Calls | Primary Migration Targets |\n")
        f.write("| :--- | :---: | :---: | :--- |\n")
        for folder, files_dict in sorted(by_folder.items(), key=lambda x: sum(len(f) for f in x[1].values()), reverse=True):
            f_calls = sum(len(f) for f in files_dict.values())
            file_names = ", ".join(f"`{Path(fp).name}`" for fp in files_dict.keys())
            f.write(f"| `📁 {folder}` | {len(files_dict)} | {f_calls} | {file_names} |\n")
        f.write("\n---\n\n")

        for folder, files_dict in sorted(by_folder.items()):
            folder_calls = sum(len(f) for f in files_dict.values())
            f.write(f"## 📁 Directory: `{folder}`\n\n")
            f.write(f"**Total Calls in Folder:** {folder_calls} across {len(files_dict)} file(s)\n\n")

            for file_path, findings in files_dict.items():
                file_name = Path(file_path).name
                f.write(f"### 📄 `{file_name}` (`{file_path}`)\n\n")
                f.write("| Line | Symbol | Current Code | Baseline Replacement |\n")
                f.write("| :---: | :--- | :--- | :--- |\n")
                for item in findings:
                    code_esc = item["code"].replace("|", "\\|")
                    repl_esc = item["replacement"].replace("|", "\\|")
                    f.write(f"| {item['line']} | `{item['symbol']}` | `{code_esc}` | `{repl_esc}` |\n")
                f.write("\n")

    print("=" * 85)
    print(f"📄 Detailed inventory grouped by parent folder saved to: {report_file.name}")
    print("=" * 85)


if __name__ == "__main__":
    main()
