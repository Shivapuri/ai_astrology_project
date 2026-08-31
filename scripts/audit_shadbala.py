import csv
import os
import re
import json

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from jyotish.generate_jyotish import generate_kala_chart

CSV_DIR = os.path.join("source-material", "software-setup", "sample-case")
PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

def parse_tagged_csv(filename):
    """
    Parses a tagged CSV file (e.g. angelina_jolie_cheshta.csv).
    Returns a dictionary matrix: matrix[giving_planet][receiving_planet] = parsed_data_list
    Also captures any 'Total' row at the bottom if it exists.
    """
    matrix = {p: {} for p in PLANETS}
    totals = {}
    filepath = os.path.join(CSV_DIR, filename)
    
    if not os.path.exists(filepath):
        print(f"Warning: Baseline CSV {filename} not found.")
        return matrix, totals
        
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        headers = next(reader)
        col_planets = headers[1:8] # Extract exactly 7 planets
        
        for row in reader:
            giving_planet = row[0].strip()
            if giving_planet == "Total":
                for i, cell in enumerate(row[1:8]):
                    receiving_planet = col_planets[i].strip()
                    if receiving_planet in PLANETS:
                        try:
                            totals[receiving_planet] = float(cell.replace('*', '').strip())
                        except ValueError:
                            pass
                continue

            if giving_planet not in PLANETS:
                continue 
                
            for i, cell in enumerate(row[1:8]):
                receiving_planet = col_planets[i].strip()
                if receiving_planet not in PLANETS:
                    continue
                
                # Extract all numbers and tags from the cell
                lines = cell.strip().split('\n')
                cell_data = []
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    
                    match = re.search(r'(.*?)(?:\[([GRBK])\])?$', line)
                    if match:
                        val_str = match.group(1).strip()
                        tag = match.group(2)
                        
                        try:
                            val_str = val_str.replace('*', '').replace('+', '')
                            val = float(val_str)
                            cell_data.append({'value': val, 'color': tag})
                        except ValueError:
                            pass
                            
                matrix[giving_planet][receiving_planet] = cell_data
                
    return matrix, totals

def run_audit():
    print("Generating Chart Data...")
    chart = generate_kala_chart(
        name="Angelina Jolie", year=1975, month=6, day=4,
        hour=9, minute=9, latitude=34.0522, longitude=-118.2437, timezone_offset=-7.0
    )
    
    calc_matrices = chart.get('avastha_matrix', {}).get('D1', {})
    
    # Map CSV names to Backend Baseline Types
    targets = {
        "Shadbala": ("angelina_jolie_shadbala.csv", "ShadBala"),
        "Uccha": ("angelina_jolie_uccha.csv", "Uccha"),
        "Dig": ("angelina_jolie_dig.csv", "Dig"),
        "Cheshta": ("angelina_jolie_cheshta.csv", "Cheshta"),
        "Subha": ("angelina_jolie_subha.csv", "Subha"),
        "Ishta": ("angelina_jolie_ishta.csv", "Ishta")
    }

    report_lines = []
    report_lines.append("# Shadbala & Avastha Audit Report")
    report_lines.append("\nThis report systematically compares the Backend's generated Quantitative Avastha matrices with the true baseline CSVs.")
    
    # 6 Pillars Micro-Audit
    report_lines.append("\n## Shadbala 6 Pillars Micro-Audit Breakdown")
    report_lines.append("| Planet | Sthana | Dig | Kala | Cheshta | Naisargika | Drik | Total (Virupas) | Total (Rupas) |")
    report_lines.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
    
    shadbala_data = chart.get('shadbala', {})
    for p in PLANETS:
        p_sb = shadbala_data.get(p, {})
        sthana = p_sb.get('Sthana_Bala', 0.0)
        dig = p_sb.get('Dig_Bala', 0.0)
        kala = p_sb.get('Kala_Bala', 0.0)
        cheshta = p_sb.get('Cheshta_Bala', 0.0)
        naisarg = p_sb.get('Naisargika_Bala', 0.0)
        drik = p_sb.get('Drik_Bala', 0.0)
        tot_v = p_sb.get('Total_Virupas', 0.0)
        tot_r = p_sb.get('Total_Rupas', 0.0)
        report_lines.append(f"| {p} | {sthana:.2f} | {dig:.2f} | {kala:.2f} | {cheshta:.2f} | {naisarg:.2f} | {drik:.2f} | {tot_v:.2f} | {tot_r:.4f} |")
    
    total_cells_checked = 0
    total_failures = 0
    
    for display_name, (csv_name, backend_key) in targets.items():
        report_lines.append(f"\n## {display_name} Matrix Audit")
        
        expected_matrix, expected_totals = parse_tagged_csv(csv_name)
        calc_matrix = calc_matrices.get(backend_key, {})
        
        if not calc_matrix:
            report_lines.append(f"**ERROR:** Matrix for {backend_key} not generated by backend!")
            total_failures += 1
            continue
            
        failures = []
        
        # Check Totals (Diagonal or bottom totals depending on the matrix type)
        # Note: In Kala CSVs, the diagonal usually matches the backend's "bottom" for (P, P).
        # Sometimes there's a explicit Total row.
        if expected_totals:
            for p in PLANETS:
                exp_tot = expected_totals.get(p, 0)
                # In the backend, the base strength of the planet is at (p, p) bottom
                try:
                    calc_tot = float(calc_matrix[p][p]['bottom'])
                except (KeyError, TypeError, ValueError):
                    calc_tot = 0.0
                    
                if abs(exp_tot - calc_tot) > 0.5:
                    failures.append(f"- **{p} Total Baseline**: Expected `{exp_tot}`, Got `{calc_tot}` (Diff: `{abs(exp_tot - calc_tot):.2f}`)")

        # Check Off-Diagonals (Modifiers)
        for giver in PLANETS:
            for receiver in PLANETS:
                if giver == receiver:
                    # Diagonal is just the base score, already logged/checked or structurally different
                    continue
                    
                total_cells_checked += 1
                exp_cell = expected_matrix[giver][receiver]
                calc_cell = calc_matrix.get(receiver, {}).get(giver)
                
                exp_mod = 0.0
                if exp_cell and len(exp_cell) > 0:
                    exp_mod = exp_cell[0]['value']
                    
                calc_mod = 0.0
                if calc_cell:
                    try:
                        calc_mod = float(calc_cell.get('top', 0))
                    except (ValueError, TypeError):
                        calc_mod = 0.0
                
                if abs(exp_mod - calc_mod) > 0.5:
                    failures.append(f"- **{giver} → {receiver} (Pull/Modifier)**: Expected `{exp_mod}`, Got `{calc_mod}` (Diff: `{abs(exp_mod - calc_mod):.2f}`)")

        if not failures:
            report_lines.append("✅ **Status:** Perfectly Aligned.")
        else:
            report_lines.append(f"❌ **Status:** {len(failures)} Discrepancies Found.")
            report_lines.extend(failures)
            total_failures += len(failures)

    report_lines.append("\n## Summary")
    report_lines.append(f"Checked a total of **{total_cells_checked}** relational cells across matrices.")
    report_lines.append(f"Found **{total_failures}** discrepancies (Delta > 0.5).")
    
    report_text = "\n".join(report_lines)
    print(report_text)
    
    os.makedirs("documentations", exist_ok=True)
    with open("documentations/shadbala_audit_report.md", "w", encoding="utf-8") as f:
        f.write(report_text)
        
    print("Audit Report Saved to documentations/shadbala_audit_report.md")

if __name__ == "__main__":
    run_audit()
