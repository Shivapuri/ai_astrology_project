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
                
                # Extract all numbers and tags from the cell (e.g. '11.7[R]', '32.7[R]+92.7[G]')
                import re
                # Find all occurrences of number optionally preceded by + or - and followed by [TAG]
                matches = re.findall(r'([+-]?\d+\.?\d*)\s*\[([A-Z])\]', cell)
                cell_data = []
                for val_str, tag in matches:
                    try:
                        val = float(val_str)
                        cell_data.append({'value': abs(val), 'color': tag})
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
    report_lines.append("| Planet | Sthana | Dig | Kala | Cheshta | Naisarg | Drik | Total (V) | Subha | Asubha | Ishta | Kashta |")
    report_lines.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
    
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
        subha = p_sb.get('Subha_Phala', 0.0)
        asubha = p_sb.get('Asubha_Phala', 0.0)
        ishta = p_sb.get('Ishta_Phala', 0.0)
        kashta = p_sb.get('Kashta_Phala', 0.0)
        report_lines.append(f"| {p} | {sthana:.2f} | {dig:.2f} | {kala:.2f} | {cheshta:.2f} | {naisarg:.2f} | {drik:.2f} | {tot_v:.2f} | {subha:.2f} | {asubha:.2f} | {ishta:.2f} | {kashta:.2f} |")
    
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
                try:
                    calc_tot = float(calc_matrix[p][p]['bottom'])
                except (KeyError, TypeError, ValueError):
                    calc_tot = 0.0
                for giver in PLANETS:
                    if giver != p:
                        # Add the modifiers which are the off-diagonals
                        try:
                            val = float(calc_matrix[giver][p]['top'])
                            color = calc_matrix[giver][p]['color']
                            if color == 'green':
                                calc_tot += val
                            elif color == 'red':
                                calc_tot -= val
                        except (KeyError, TypeError, ValueError):
                            pass
                            
                if abs(exp_tot - calc_tot) > 0.5:
                    failures.append(f"- **{p} Total Baseline**: Expected `{exp_tot}`, Got `{calc_tot:.1f}` (Diff: `{abs(exp_tot - calc_tot):.2f}`)")

        # Check Off-Diagonals (Modifiers)
        for giver in PLANETS:
            for receiver in PLANETS:
                if giver == receiver:
                    # Diagonal is just the base score, already logged/checked or structurally different
                    continue
                    
                total_cells_checked += 1
                exp_cell = expected_matrix[giver][receiver]
                calc_cell = calc_matrix.get(receiver, {}).get(giver)
                
                exp_net = 0.0
                if exp_cell:
                    num_mods = len(exp_cell) // 2
                    modifiers = exp_cell[:num_mods]
                    for item in modifiers:
                        val = item['value']
                        color = item['color']
                        if color == 'G':
                            exp_net += val
                        elif color == 'R' or color == 'K':
                            exp_net -= val
                        # 'B' means neutral, so it adds/subtracts 0.
                        
                calc_net = 0.0
                if calc_cell:
                    try:
                        top_val = float(calc_cell.get('top', 0))
                        color = calc_cell.get('color', '')
                        if color == 'green':
                            calc_net = top_val
                        elif color == 'red':
                            calc_net = -top_val
                    except (ValueError, TypeError):
                        calc_net = 0.0
                
                if abs(exp_net - calc_net) > 0.5:
                    failures.append(f"- **{giver} → {receiver} (Net Modifier)**: Expected `{exp_net:.1f}`, Got `{calc_net:.1f}` (Diff: `{abs(exp_net - calc_net):.2f}`)")

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
