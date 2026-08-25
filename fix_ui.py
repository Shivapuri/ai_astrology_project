import re

with open("templates/index.html", "r") as f:
    html = f.read()

# 1. Replace the tab-avasthas-calc div completely
calc_div_start = html.find('<div class="tab-content" id="tab-avasthas-calc">')
# find the next <div class="tab-content" id="tab-avasthas">
calc_div_end = html.find('<div class="tab-content" id="tab-avasthas">')

new_calc_html = """<div class="tab-content" id="tab-avasthas-calc" style="background-color: #ffffcc; padding: 20px; font-family: 'Times New Roman', Times, serif;">
                        <div style="text-align: center; margin-bottom: 20px;">
                            <h3 id="avasthaCalcTitle" style="color: #000099; margin: 0; font-size: 1.3em; font-weight: bold;">Rasi - Avasthas - Calculated</h3>
                        </div>
                        <div style="overflow-x: auto; background-color: #ffffcc;">
                            <style>
                                .kala-matrix {
                                    width: 100%;
                                    border-collapse: collapse;
                                    text-align: center;
                                    background-color: white;
                                    border: 1px solid #e88e55;
                                }
                                .kala-matrix th {
                                    background-color: #ffffcc;
                                    color: #000099;
                                    font-weight: normal;
                                    padding: 15px 5px;
                                    border: 1px solid #e88e55;
                                    position: relative;
                                    min-width: 60px;
                                }
                                .kala-matrix th.kala-header {
                                    border: 2px solid #e88e55;
                                    box-shadow: inset 0 0 0 2px #ffffcc, inset 0 0 0 3px #e88e55;
                                }
                                .kala-matrix td {
                                    border: 1px solid #e88e55;
                                    padding: 10px 5px;
                                    height: 70px;
                                    vertical-align: middle;
                                }
                                .kala-matrix td:first-child {
                                    color: #000099;
                                    width: 50px;
                                }
                            </style>
                            <table id="avasthasCalcTable" class="kala-matrix">
                                <thead>
                                    <tr>
                                        <th style="background-color: #ffffcc; border: none; box-shadow: none;"></th>
                                        <th class="kala-header">Su</th>
                                        <th class="kala-header">Mo</th>
                                        <th class="kala-header">Ma</th>
                                        <th class="kala-header">Me</th>
                                        <th class="kala-header">Ju</th>
                                        <th class="kala-header">Ve</th>
                                        <th class="kala-header">Sa</th>
                                    </tr>
                                </thead>
                                <tbody></tbody>
                            </table>
                        </div>
                    </div>

                    """

if calc_div_start != -1 and calc_div_end != -1:
    html = html[:calc_div_start] + new_calc_html + html[calc_div_end:]

# 2. Replace the JS function updateAvasthasCalcTable
js_start = html.find('function updateAvasthasCalcTable() {')
js_end = html.find('function updateAvasthasTable(varga) {')

new_js = """function updateAvasthasCalcTable(vargaName = "Rasi") {
            const titleEl = document.getElementById('avasthaCalcTitle');
            if (titleEl) {
                // Determine display name for D1 vs others
                const vargaDisplay = vargaName === "D1" ? "Rasi" : 
                                     vargaName === "D9" ? "Navamsa" : 
                                     vargaName === "D7" ? "Saptamsa" : vargaName;
                titleEl.textContent = `${vargaDisplay} - Avasthas - Calculated`;
            }

            const tbody = document.querySelector('#avasthasCalcTable tbody');
            tbody.innerHTML = '';
            
            const planets = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn'];
            const labels = ['Su', 'Mo', 'Ma', 'Me', 'Ju', 'Ve', 'Sa'];
            
            const matrix = currentChartData.avastha_matrix;
            if (!matrix) return;
            
            planets.forEach((p_row, i) => {
                const tr = document.createElement('tr');
                let htmlStr = `<td>${labels[i]}</td>`; // The "Giver" row
                
                planets.forEach((p_col) => {
                    // p_col is receiving, p_row is giving
                    const cell = matrix[p_col][p_row];
                    
                    if (p_col === p_row) {
                        htmlStr += `<td style="color:black; font-size: 0.95em;" title="${cell.tooltip}">
                                    ${cell.bottom}
                                 </td>`;
                    } else if (cell) {
                        let colorHex = cell.color === "green" ? "#006600" : 
                                       cell.color === "red" ? "#cc0000" : 
                                       "#000099"; // blue
                                       
                        htmlStr += `<td style="color:${colorHex}; font-size: 0.9em; line-height: 1.8;" title="${cell.tooltip}">
                                    <div>${cell.top}</div>
                                    <div>${cell.bottom}</div>
                                 </td>`;
                    } else {
                        htmlStr += `<td></td>`;
                    }
                });
                tr.innerHTML = htmlStr;
                tbody.appendChild(tr);
            });
        }

        """

if js_start != -1 and js_end != -1:
    html = html[:js_start] + new_js + html[js_end:]

# Update the call site in renderCharts
call_start = html.find('updateAvasthasCalcTable();')
if call_start != -1:
    html = html.replace('updateAvasthasCalcTable();', 'updateAvasthasCalcTable("Rasi");')

with open("templates/index.html", "w") as f:
    f.write(html)
