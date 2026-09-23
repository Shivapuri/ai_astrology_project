/**
 * Astra Yoga Judgment Widget
 * 
 * Computes and displays the classical Kala Yoga Judgment Screen
 * evaluating Ishta / Kashta Phala, Subha / Asubha Phala, and Subha / Asubha Dig Bala.
 */

(function() {
    function updateYogaJudgmentWidget(cell, chartData) {
        const currentData = chartData || window.currentChartData;
        const tbody = cell.querySelector('.yoga-judgment-table tbody') || cell.querySelector('tbody');
        if (!tbody || !currentData || !currentData.shadbala) return;
        tbody.innerHTML = '';

        const sb = currentData.shadbala;
        const planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"];

        // Extract values for all 7 planets
        const rowData = {
            'I': [], 'K': [], 'S': [], 'A': [], 'SD': [], 'AD': [],
            '+': [], '-': [], 'IxSxSD': [], 'KxAxAD': [], 'Uccha': [], 'Cheshta': []
        };

        planets.forEach(p => {
            const pData = sb[p] || {};
            const uccha = pData.Uccha_Bala !== undefined ? pData.Uccha_Bala : 0.0;
            const cheshta = pData.Cheshta_Bala !== undefined ? pData.Cheshta_Bala : 0.0;
            const ishta = pData.Ishta_Phala !== undefined ? pData.Ishta_Phala : ((uccha + cheshta) / 2.0);
            const kashta = pData.Kashta_Phala !== undefined ? pData.Kashta_Phala : (60.0 - ishta);
            const subha = pData.Subha_Phala !== undefined ? pData.Subha_Phala : 0.0;
            const asubha = pData.Asubha_Phala !== undefined ? pData.Asubha_Phala : (60.0 - subha);
            const sd = pData.Dig_Bala !== undefined ? pData.Dig_Bala : 0.0;
            const ad = Math.max(0.0, 60.0 - sd);
            const plus = ishta + subha + sd;
            const minus = kashta + asubha + ad;
            const ix_sx_sd = (ishta * subha * sd) / 3600.0;
            const kx_ax_ad = (kashta * asubha * ad) / 3600.0;

            rowData['I'].push({ val: ishta, p, uccha, cheshta });
            rowData['K'].push({ val: kashta, p, ishta });
            rowData['S'].push({ val: subha, p });
            rowData['A'].push({ val: asubha, p, subha });
            rowData['SD'].push({ val: sd, p });
            rowData['AD'].push({ val: ad, p, sd });
            rowData['+'].push({ val: plus, p, ishta, subha, sd });
            rowData['-'].push({ val: minus, p, kashta, asubha, ad });
            rowData['IxSxSD'].push({ val: ix_sx_sd, p, ishta, subha, sd });
            rowData['KxAxAD'].push({ val: kx_ax_ad, p, kashta, asubha, ad });
            rowData['Uccha'].push({ val: uccha, p });
            rowData['Cheshta'].push({ val: cheshta, p });
        });

        const sections = [
            {
                title: "Ishta and Kashta",
                rows: [
                    { key: "I", label: "I", isNeg: false },
                    { key: "K", label: "K", isNeg: true }
                ]
            },
            {
                title: "Subha and Asubha",
                rows: [
                    { key: "S", label: "S", isNeg: false },
                    { key: "A", label: "A", isNeg: true }
                ]
            },
            {
                title: "Subha and Asubha Dig Bala",
                rows: [
                    { key: "SD", label: "SD", isNeg: false },
                    { key: "AD", label: "AD", isNeg: true },
                    { key: "+", label: "+", isNeg: false },
                    { key: "-", label: "-", isNeg: true },
                    { key: "IxSxSD", label: "IxSxSD", isNeg: false },
                    { key: "KxAxAD", label: "KxAxAD", isNeg: true },
                    { key: "Uccha", label: "Uccha", isNeg: false },
                    { key: "Cheshta", label: "Cheshta", isNeg: false }
                ]
            }
        ];

        sections.forEach(sec => {
            const trSec = document.createElement('tr');
            trSec.innerHTML = `<td colspan="9" class="sec-header">${sec.title}</td>`;
            tbody.appendChild(trSec);

            sec.rows.forEach(r => {
                const tr = document.createElement('tr');
                let html = `<td class="row-lbl tooltip-target" data-tooltip="<strong>${r.label} Row</strong><br>Click or hover over individual values to see how each planet's score is formed.">${r.label}</td>`;

                const items = rowData[r.key];
                let sum = 0.0;

                items.forEach(item => {
                    sum += item.val;
                    const vStr = item.val.toFixed(1);
                    const valClass = r.isNeg ? 'val-neg' : 'val-pos';
                    let tooltip = '';

                    if (r.key === 'I') {
                        tooltip = `<strong>${item.p} — Ishta Phala (Auspicious Capacity): ${vStr}</strong><br>• <strong>Formula:</strong> (Uccha Bala ${item.uccha.toFixed(1)} + Cheshta Bala ${item.cheshta.toFixed(1)}) / 2<br>• <strong>Meaning:</strong> Measures the planet's capacity to give auspicious, beneficial results and blessings during its periods.`;
                    } else if (r.key === 'K') {
                        tooltip = `<strong>${item.p} — Kashta Phala (Inauspicious Capacity): ${vStr}</strong><br>• <strong>Formula:</strong> 60 - Ishta Phala (${item.ishta.toFixed(1)})<br>• <strong>Meaning:</strong> Measures the planet's propensity to produce struggles, delays, or difficult lessons during its periods.`;
                    } else if (r.key === 'S') {
                        tooltip = `<strong>${item.p} — Subha Phala (Benefic Nature): ${vStr}</strong><br>• <strong>Evaluation:</strong> Derived from the planet's dignity across the 7 divisional charts (Vargas).<br>• <strong>Meaning:</strong> Measures how purely helpful, benevolent, and supportive the planet behaves.`;
                    } else if (r.key === 'A') {
                        tooltip = `<strong>${item.p} — Asubha Phala (Malefic Nature): ${vStr}</strong><br>• <strong>Formula:</strong> 60 - Subha Phala (${item.subha.toFixed(1)})<br>• <strong>Meaning:</strong> Measures the planet's harshness, affliction, or karmic obstacles.`;
                    } else if (r.key === 'SD') {
                        tooltip = `<strong>${item.p} — Subha Dig Bala (Directional Strength): ${vStr} Virūpas</strong><br>• <strong>Evaluation:</strong> Standard Dig Bala from Shadbala.<br>• <strong>Meaning:</strong> Measures alignment with its optimal sky quadrant (e.g. 10th for Sun/Mars, 4th for Moon/Venus, 1st for Jup/Merc, 7th for Saturn). Direction gives environmental confidence.`;
                    } else if (r.key === 'AD') {
                        tooltip = `<strong>${item.p} — Asubha Dig Bala (Directional Weakness): ${vStr} Virūpas</strong><br>• <strong>Formula:</strong> 60 - Subha Dig Bala (${item.sd.toFixed(1)})<br>• <strong>Meaning:</strong> Measures lack of directional grounding or environmental disorientation.`;
                    } else if (r.key === '+') {
                        tooltip = `<strong>${item.p} — Total Auspicious Score (+): ${vStr}</strong><br>• <strong>Formula:</strong> Ishta (${item.ishta.toFixed(1)}) + Subha (${item.subha.toFixed(1)}) + Subha Dig Bala (${item.sd.toFixed(1)})<br>• <strong>Meaning:</strong> Synthesis of all three positive strength dimensions. A high positive score indicates strong capacity to manifest good fortune.`;
                    } else if (r.key === '-') {
                        tooltip = `<strong>${item.p} — Total Inauspicious Score (-): ${vStr}</strong><br>• <strong>Formula:</strong> Kashta (${item.kashta.toFixed(1)}) + Asubha (${item.asubha.toFixed(1)}) + Asubha Dig Bala (${item.ad.toFixed(1)})<br>• <strong>Meaning:</strong> Synthesis of all three negative/resistant dimensions. Reflects the level of karma, friction, or obstacles to overcome.`;
                    } else if (r.key === 'IxSxSD') {
                        tooltip = `<strong>${item.p} — Combined Auspicious Impact: ${vStr} Virūpas</strong><br>• <strong>Formula:</strong> (Ishta × Subha × Subha Dig Bala) / 3600<br>• <strong>Meaning:</strong> Scaled product of all three auspicious factors. A concentrated index representing pure auspicious power in action.`;
                    } else if (r.key === 'KxAxAD') {
                        tooltip = `<strong>${item.p} — Combined Inauspicious Impact: ${vStr} Virūpas</strong><br>• <strong>Formula:</strong> (Kashta × Asubha × Asubha Dig Bala) / 3600<br>• <strong>Meaning:</strong> Scaled product of all three difficulty factors. A concentrated index representing the net severity of difficult karma.`;
                    } else if (r.key === 'Uccha') {
                        tooltip = `<strong>${item.p} — Uccha Bala (Exaltation Strength): ${vStr} Virūpas</strong><br>• <strong>Evaluation:</strong> Distance from deep debilitation point towards deep exaltation (0 to 60 Virūpas).<br>• <strong>Meaning:</strong> Reflects dignity, self-respect, authority, and noble quality.`;
                    } else if (r.key === 'Cheshta') {
                        tooltip = `<strong>${item.p} — Cheshta Bala (Motional Strength): ${vStr} Virūpas</strong><br>• <strong>Evaluation:</strong> Speed, retrograde motion, and proximity to Earth (Sun uses Ayana, Moon uses Paksha).<br>• <strong>Meaning:</strong> Reflects determination, persistent effort, and drive to conquer objectives.`;
                    }

                    html += `<td class="${valClass} tooltip-target" data-tooltip="${tooltip}" style="cursor:help;">${vStr}</td>`;
                });

                const avgVal = (sum / items.length).toFixed(1);
                const avgClass = r.isNeg ? 'val-neg' : 'val-pos';
                const avgTooltip = `<strong>Average ${r.label}: ${avgVal}</strong><br>• Average across all 7 classical planets for ${r.label}. Serves as the chart baseline.`;
                html += `<td class="${avgClass} tooltip-target" data-tooltip="${avgTooltip}" style="font-weight: bold; cursor:help;">${avgVal}</td>`;

                tr.innerHTML = html;
                tbody.appendChild(tr);
            });
        });
    }

    function openFloatingYogaJudgment() {
        if (typeof closeKalaMenu === 'function') closeKalaMenu();
        const modal = document.getElementById('widgetMaximizeModal');
        const titleEl = document.getElementById('widgetMaximizeModalTitle');
        const container = document.getElementById('widgetMaximizeContainer');
        const currentData = window.currentChartData;
        if (!modal || !titleEl || !container || !currentData) return;

        if (typeof setActiveFloatingNav === 'function') setActiveFloatingNav('nav-btn-yoga');
        const name = currentData.subject_info ? currentData.subject_info.name : 'Chart';
        titleEl.textContent = name + " — Yoga Judgment Screen (Ishta/Kashta & Subha/Asubha Dig Bala)";

        container.innerHTML = `
            <div class="scale-wrapper" style="width: 100%; max-width: 720px; margin: 0 auto; padding: 10px;">
                <table class="yoga-judgment-table" style="width: 100%; border-collapse: collapse; border: 2px solid #b86829; text-align: center; font-family: sans-serif; background: #ffffff;">
                    <thead>
                        <tr style="border-bottom: 2px solid #b86829; background: #fffdfa;">
                            <th style="border-right: 1px solid #b86829; width: 85px; padding: 6px;"></th>
                            <th style="border-right: 1px solid #b86829; color: #1a4a82; font-size: 17px; font-weight: bold; padding: 6px;" title="Sun (Surya)">☉</th>
                            <th style="border-right: 1px solid #b86829; color: #1a4a82; font-size: 17px; font-weight: bold; padding: 6px;" title="Moon (Chandra)">☽</th>
                            <th style="border-right: 1px solid #b86829; color: #1a4a82; font-size: 17px; font-weight: bold; padding: 6px;" title="Mars (Mangala)">♂</th>
                            <th style="border-right: 1px solid #b86829; color: #1a4a82; font-size: 17px; font-weight: bold; padding: 6px;" title="Mercury (Budha)">☿</th>
                            <th style="border-right: 1px solid #b86829; color: #1a4a82; font-size: 17px; font-weight: bold; padding: 6px;" title="Jupiter (Guru)">♃</th>
                            <th style="border-right: 1px solid #b86829; color: #1a4a82; font-size: 17px; font-weight: bold; padding: 6px;" title="Venus (Shukra)">♀</th>
                            <th style="border-right: 1px solid #b86829; color: #1a4a82; font-size: 17px; font-weight: bold; padding: 6px;" title="Saturn (Shani)">♄</th>
                            <th style="color: #1a4a82; font-size: 14px; font-weight: bold; padding: 6px;">Avg.</th>
                        </tr>
                    </thead>
                    <tbody></tbody>
                </table>
            </div>
        `;

        updateYogaJudgmentWidget(container, currentData);

        modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
    }

    if (window.widgetRegistry) {
        window.widgetRegistry.register('yoga-judgment', {
            id: 'yoga-judgment',
            title: 'Yoga Judgment (Ishta/Kashta)',
            icon: '⚖️',
            category: 'Strengths',
            onUpdate: function(cell, chartData) {
                updateYogaJudgmentWidget(cell, chartData);
            }
        });
    }

    window.updateYogaJudgmentWidget = updateYogaJudgmentWidget;
    window.openFloatingYogaJudgment = openFloatingYogaJudgment;
})();
