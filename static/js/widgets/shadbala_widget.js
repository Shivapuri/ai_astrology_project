/**
 * Astra Shadbala Breakdown Widget
 * 
 * Provides comprehensive 25-row breakdown of all six planetary potencies
 * (Sthana, Dig, Kaala, Ayana, Cheshta, Naisargika/Drig) and Parashara requirements.
 */

(function() {
    function updateShadbalaTableWidget(container, chartData) {
        const currentData = chartData || window.currentChartData;
        const root = container || document;
        if (!currentData || !currentData.shadbala) return;
        const sb = currentData.shadbala;
        const planetsOrder = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"];

        // 1. Legacy #shadbalaTable support
        const legacyTbody = root.querySelector("#shadbalaTable tbody") || document.querySelector("#shadbalaTable tbody");
        if (legacyTbody) {
            legacyTbody.innerHTML = "";
            planetsOrder.forEach(p => {
                if (!sb[p]) return;
                const data = sb[p];
                const tr = document.createElement("tr");
                tr.innerHTML = `
                    <td><strong>${p}</strong></td>
                    <td><strong>${data.Total_Rupas !== undefined ? data.Total_Rupas.toFixed(2) : (data.Total_Virupas / 60.0).toFixed(2)}</strong></td>
                    <td>${data.Sthana_Bala.toFixed(2)}</td>
                    <td>${data.Dig_Bala.toFixed(2)}</td>
                    <td>${data.Kala_Bala.toFixed(2)}</td>
                    <td>${data.Cheshta_Bala.toFixed(2)}</td>
                    <td>${data.Naisargika_Bala.toFixed(2)}</td>
                    <td>${data.Drik_Bala.toFixed(2)}</td>
                    <td><span style="color: #27ae60; font-weight: bold;">${(data.Ishta_Phala || 0).toFixed(2)}</span></td>
                    <td><span style="color: #c0392b; font-weight: bold;">${(data.Kashta_Phala || 0).toFixed(2)}</span></td>
                `;
                legacyTbody.appendChild(tr);
            });
        }

        // 2. Comprehensive Kala-style 25-row Breakdown Grids
        const breakdownGrids = root.querySelectorAll(".shadbala-breakdown-grid tbody");
        if (breakdownGrids.length === 0) return;

        const rowsDef = [
            // Sthana Bala
            { type: "header", title: "Sthana Bala (Positional Strength)" },
            { label: "Uccha Bala", key: "Uccha_Bala", decimals: 2, desc: "Exaltation Strength: Closeness to deep exaltation degree (max 60 Virūpas) vs deep debilitation (0 Virūpas)." },
            { label: "Saptavargaja Bala", key: "Saptavarga_Bala", decimals: 0, desc: "Divisional Dignity Strength: Earned from friendly, own, or exaltation signs across the 7 root divisional charts (D1, D2, D3, D7, D9, D12, D30)." },
            { label: "Ojhayugmarasyamsa Bala", key: "Ojhayugma_Bala", decimals: 0, desc: "Odd/Even Sign & Navamsha Strength: Male planets gain 15 Virūpas in odd/masculine signs; female planets in even/feminine signs." },
            { label: "Kendradi Bala", key: "Kendradi_Bala", decimals: 0, desc: "House Angle Strength: Angular houses (1, 4, 7, 10) get 60 Virūpas; Succedent (2, 5, 8, 11) get 30; Cadent (3, 6, 9, 12) get 15." },
            { label: "Drekkana Bala", key: "Drekkana_Bala", decimals: 0, desc: "Decanate Strength: 15 Virūpas awarded based on planet gender and the 1st, 2nd, or 3rd 10° segment of the sign occupied." },
            { label: "Total Sthana Bala", key: "Sthana_Bala", decimals: 1, isSubtotal: true, desc: "Total Positional Strength: Sum of all 5 positional sub-strengths." },
            { label: "Required Sthana Bala", key: "Required_Sthana", decimals: 0, isRequired: true, desc: "Parashara Minimum Positional Benchmark needed for effective functioning." },
            { label: "% of Required Sthana Bala", key: "Pct_Required_Sthana", decimals: 1, isPct: true, desc: "Sufficiency ratio of Positional Strength (≥100% means fully satisfied)." },
            
            // Dig Bala
            { type: "header", title: "Dig Bala (Directional Strength)" },
            { label: "Total Dig Bala", key: "Dig_Bala", decimals: 2, isSubtotal: true, desc: "Directional Strength: Proximity to optimal sky quadrant (10th for Sun/Mars, 4th for Moon/Venus, 1st for Jup/Merc, 7th for Saturn). Max 60 Virūpas." },
            { label: "Required Dig Bala", key: "Required_Dig", decimals: 0, isRequired: true, desc: "Parashara Minimum Directional Benchmark (35 Virūpas for all planets)." },
            { label: "% of Required Dig Bala", key: "Pct_Required_Dig", decimals: 1, isPct: true, desc: "Sufficiency ratio of Directional Strength (≥100% means directional confidence)." },
            
            // Kaala Bala
            { type: "header", title: "Kaala Bala (Time Strength)" },
            { label: "Natonnata Bala", key: "Natonnata_Bala", decimals: 2, desc: "Day/Night Diurnal Strength: Sun, Jupiter, Venus strong by day; Moon, Mars, Saturn strong by night; Mercury always 60." },
            { label: "Paksha Bala", key: "Paksha_Bala", decimals: 2, desc: "Lunar Fortnight Strength: Benefics strong during bright waxing Moon; malefics strong during dark waning Moon." },
            { label: "Tribhaga Bala", key: "Tribhaga_Bala", decimals: 0, desc: "Three-Part Day/Night Strength: 60 Virūpas awarded to the specific planet ruling the 1/3 portion of day/night when birth occurred." },
            { label: "Varsha Bala", key: "Varsha_Bala", decimals: 0, desc: "Year Lord Strength: 15 Virūpas awarded to the ruler of the astrological solar year." },
            { label: "Masa Bala", key: "Masa_Bala", decimals: 0, desc: "Month Lord Strength: 30 Virūpas awarded to the ruler of the solar month (Sun's transit sign)." },
            { label: "Dina Bala", key: "Dina_Bala", decimals: 0, desc: "Day Lord Strength: 45 Virūpas awarded to the ruler of the day of the week." },
            { label: "Hora Bala", key: "Hora_Bala", decimals: 0, desc: "Hour Lord Strength: 60 Virūpas awarded to the ruler of the planetary hour of birth." },
            { label: "Total Kaala Bala", key: "Kala_Bala", decimals: 1, isSubtotal: true, desc: "Total Temporal Strength: Sum of all time-based cosmic alignments." },
            { label: "Required Kaala Bala", key: "Required_Kaala", decimals: 0, isRequired: true, desc: "Parashara Minimum Temporal Benchmark." },
            { label: "% of Required Kaala Bala", key: "Pct_Required_Kaala", decimals: 1, isPct: true, desc: "Sufficiency ratio of Temporal Strength." },
            
            // Ayana Bala
            { type: "header", title: "Ayana Bala (Declination Strength)" },
            { label: "Total Ayana Bala", key: "Ayana_Bala", decimals: 2, isSubtotal: true, desc: "Declination Strength: Distance north or south of celestial equator. Sun, Mars, Jupiter favor North; Moon, Saturn favor South." },
            { label: "Required Ayana Bala", key: "Required_Ayana", decimals: 0, isRequired: true, desc: "Parashara Minimum Declination Benchmark." },
            { label: "% of Required Ayana Bala", key: "Pct_Required_Ayana", decimals: 1, isPct: true, desc: "Sufficiency ratio of Declination Strength." },
            
            // Cheshta Bala
            { type: "header", title: "Cheshta Bala (Motional Strength)" },
            { label: "Total Cheshta Bala", key: "Cheshta_Bala", decimals: 2, isSubtotal: true, desc: "Motional Strength: Measures orbital speed and retrograde motion. Slow or retrograde planets closest to Earth get up to 60 Virūpas." },
            { label: "Required Cheshta Bala", key: "Required_Cheshta", decimals: 0, isRequired: true, desc: "Parashara Minimum Motional Benchmark." },
            { label: "% of Required Cheshta Bala", key: "Pct_Required_Cheshta", decimals: 1, isPct: true, desc: "Sufficiency ratio of Motional Strength." },
            
            // Other Balas
            { type: "header", title: "Other Balas" },
            { label: "Naisargika Bala", key: "Naisargika_Bala", decimals: 2, desc: "Natural Fixed Luminosity: Inherent cosmic brightness rank (Sun 60 > Moon 51.4 > Venus 42.9 > Jupiter 34.3 > Mercury 25.7 > Mars 17.1 > Saturn 8.6)." },
            { label: "Drig Bala", key: "Drik_Bala", decimals: 1, desc: "Aspectual Strength (Drik Bala): Net balance of supportive benefic aspects (+) versus stressful malefic aspects (-) received." },
            { label: "Yuddha Bala", key: "Yuddha_Bala", decimals: 2, desc: "Planetary War Strength: Bonus won or lost when two true planets are within 1° of celestial longitude." },
            
            // Final Summary & Rankings
            { type: "header", title: "Summary & Rankings" },
            { label: "Shad Bala Total", key: "Total_Virupas", decimals: 1, isGrandTotal: true, desc: "Grand Total Shadbala (in Virūpas): Sum of all 6 individual strength dimensions." },
            { label: "Required Shad Bala", key: "Required_Total", decimals: 0, isRequired: true, desc: "Parashara Minimum Total Threshold needed for full operational capability." },
            { label: "% of Required Shad Bala", key: "Pct_Required_Total", decimals: 1, isPct: true, desc: "Overall Sufficiency: Values ≥100% indicate the planet has enough cosmic power to manifest its promises." },
            { label: "Shad Bala in Rupas", key: "Total_Rupas", decimals: 2, isGrandTotal: true, desc: "Shadbala in Rūpas: Total Virūpas divided by 60 (1 Rūpa = 60 Virūpas)." },
            { label: "Relative Rank", key: "Relative_Rank", decimals: 0, isRank: true, desc: "Overall strength rank among the 7 classical planets (#1 = strongest)." }
        ];

        breakdownGrids.forEach(tbody => {
            tbody.innerHTML = "";
            rowsDef.forEach(row => {
                const tr = document.createElement("tr");
                if (row.type === "header") {
                    tr.className = "category-header";
                    tr.innerHTML = `<td colspan="8">${row.title}</td>`;
                } else {
                    if (row.isGrandTotal) tr.className = "grandtotal-row";
                    else if (row.isSubtotal) tr.className = "subtotal-row";
                    
                    let html = `<td class="tooltip-target" data-tooltip="<strong>${row.label}</strong><br>${row.desc}" style="cursor:help;">${row.label}</td>`;
                    planetsOrder.forEach(p => {
                        const pData = sb[p] || {};
                        const val = pData[row.key];
                        if (val === undefined || val === null) {
                            html += `<td>-</td>`;
                        } else if (row.isPct) {
                            const numVal = Number(val);
                            const colorCls = numVal < 100.0 ? "under-req" : "over-req";
                            const tip = `<strong>${p} — ${row.label}: ${numVal.toFixed(row.decimals)}%</strong><br>• ${numVal >= 100 ? 'Meets or exceeds requirement (' + numVal.toFixed(1) + '% ≥ 100%).' : 'Below requirement (' + numVal.toFixed(1) + '% < 100%).'}<br>• ${row.desc}`;
                            html += `<td class="tooltip-target" data-tooltip="${tip}" style="cursor:help;"><span class="pct-val ${colorCls}">${numVal.toFixed(row.decimals)}%</span></td>`;
                        } else if (row.isRank) {
                            const tip = `<strong>${p} — Rank #${val}</strong><br>Ranked #${val} out of 7 planets in overall Shadbala strength.`;
                            html += `<td class="tooltip-target" data-tooltip="${tip}" style="cursor:help;"><span class="rank-val">#${val}</span></td>`;
                        } else {
                            let vFormatted = Number(val).toFixed(row.decimals);
                            if (row.key === "Yuddha_Bala" && Number(val) > 0) {
                                vFormatted = "+" + vFormatted;
                            }
                            const tip = `<strong>${p} — ${row.label}: ${vFormatted}</strong><br>• ${row.desc}`;
                            html += `<td class="tooltip-target" data-tooltip="${tip}" style="cursor:help;">${vFormatted}</td>`;
                        }
                    });
                    tr.innerHTML = html;
                }
                tbody.appendChild(tr);
            });
        });
    }

    if (window.widgetRegistry) {
        window.widgetRegistry.register('shadbala-table', {
            id: 'shadbala-table',
            title: 'Shad Bala Breakdown',
            icon: '⚖️',
            category: 'Strengths',
            render: function(container, chartData, options) {
                updateShadbalaTableWidget(container, chartData);
            },
            onUpdate: function(cell, chartData) {
                updateShadbalaTableWidget(cell, chartData);
            }
        });
    }

    // Export globally for backward compatibility
    window.updateShadbalaTable = updateShadbalaTableWidget;
    window.updateShadbalaTableWidget = updateShadbalaTableWidget;
})();
