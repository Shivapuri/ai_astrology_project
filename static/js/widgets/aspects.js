/**
 * Astra Aspects Widgets (Planets, Equal Houses, Bhava Chalita)
 * 
 * Renders full classical Kala Graha Drishti aspectual tables and ray strengths
 * across planets, equal cusps, and Campanus bhava chalita cusps.
 */

(function() {
    function renderKalaAspectTable(target, dataKey, columnsList, isHouse = false, customAspects = null) {
        let tables = [];
        if (typeof target === 'string') {
            tables = Array.from(document.querySelectorAll('#' + target));
        } else if (target && target.tagName === 'TABLE') {
            tables = [target];
        } else if (target && target.querySelector) {
            const t = target.querySelector('table');
            if (t) tables = [t];
        }
        if (tables.length === 0) return;
        
        const currentData = window.currentChartData;
        const adv = customAspects || (currentData ? currentData.advanced_aspects : null);
        if (!adv) return;
        
        const aspects = adv[dataKey];
        const totals = adv.totals ? adv.totals[dataKey] : null;
        const yutis = adv.yutis || {};
        if (!aspects) return;
        
        const aspectingPlanets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"];
        const signsList = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"];

        tables.forEach(table => {
            const thead = table.querySelector('thead');
            const tbody = table.querySelector('tbody');
            if (!thead || !tbody) return;
            thead.innerHTML = '';
            tbody.innerHTML = '';
            
            // Header Row
            const trHead = document.createElement('tr');
            trHead.innerHTML = '<th></th>' + columnsList.map(c => {
                const colLabel = c.toString().substring(0, 2);
                const colFull = isHouse ? `House ${c}` : c;
                return `<th class="tooltip-target" data-tooltip="<strong>${colFull}</strong><br>Target receiving Graha Drishti aspects.">${colLabel}</th>`;
            }).join('');
            thead.appendChild(trHead);
            
            // Data Rows (Aspecting Planets)
            aspectingPlanets.forEach(p => {
                const tr = document.createElement('tr');
                tr.className = 'interactive-table-row';
                tr.dataset.type = 'planet';
                tr.dataset.id = p;
                tr.style.cursor = 'pointer';
                const pData = currentData && currentData.vargas && currentData.vargas.D1 && currentData.vargas.D1.grahas && currentData.vargas.D1.grahas[p];
                const pSign = pData ? pData.sign : '';
                const pDeg = pData ? pData.degree_0_to_30 : null;
                const pLon = pData ? pData.longitude : 0;
                const pDegStr = pDeg !== null ? `${Math.floor(pDeg)}°${Math.round((pDeg - Math.floor(pDeg)) * 60)}'` : '';
                
                let html = `<td class="tooltip-target" data-tooltip="<strong>${p} (${pSign} ${pDegStr})</strong><br>Aspecting planet casting sight (Graha Drishti)."><strong>${p.substring(0, 2)}</strong></td>`;
                
                columnsList.forEach(c => {
                    const cKey = c.toString();
                    if (!isHouse && p === c) {
                        html += `<td class="tooltip-target" data-tooltip="<strong>${p} — Self Position</strong><br>A planet resides here and cannot cast an external aspect onto itself." style="color:var(--text-subtle); cursor:help;">--</td>`;
                    } else if (!isHouse && yutis[p] && yutis[p].includes(c)) {
                        const cData = currentData.vargas.D1.grahas && currentData.vargas.D1.grahas[c];
                        const cSign = cData ? cData.sign : pSign;
                        html += `<td class="tooltip-target" data-tooltip="<strong>Conjunction (Yuti): ${p} & ${c}</strong><br>• Both planets occupy <strong>${cSign}</strong>.<br>• In Vedic astrology, sharing a sign creates direct synthesis and intense mutual exchange of energies." style="color:var(--status-malefic); font-weight:bold; cursor:help;">Y</td>`;
                    } else {
                        const entry = aspects[cKey] && aspects[cKey][p] ? aspects[cKey][p] : null;
                        if (entry && entry.raw > 0) {
                            const rawRounded = Math.round(entry.raw);
                            
                            let cLon = 0;
                            let targetName = '';
                            let targetDesc = '';
                            
                            if (isHouse) {
                                targetName = `House ${c}`;
                                if (dataKey === 'equal_cusps') {
                                    const ascLon = (currentData.vargas.D1.lagna && currentData.vargas.D1.lagna.longitude) || 0;
                                    cLon = (ascLon + (c - 1) * 30.0) % 360.0;
                                    const hSign = signsList[Math.floor(cLon / 30.0)];
                                    const hDeg = (cLon % 30.0).toFixed(1);
                                    targetDesc = `Equal House ${c} cusp (${hDeg}° ${hSign})`;
                                } else {
                                    const cuspsList = (currentData.vargas.D1 && currentData.vargas.D1.cusps) || [];
                                    const cuspObj = cuspsList[c - 1] || {};
                                    cLon = cuspObj.longitude !== undefined ? cuspObj.longitude : (((currentData.vargas.D1.lagna?.longitude || 0) + (c - 1) * 30.0) % 360.0);
                                    const hSign = cuspObj.sign || signsList[Math.floor(cLon / 30.0)];
                                    const hDeg = cuspObj.degree_0_to_30 !== undefined ? cuspObj.degree_0_to_30.toFixed(1) : (cLon % 30.0).toFixed(1);
                                    targetDesc = `Bhava Chalita Cusp ${c} (${hDeg}° ${hSign})`;
                                }
                            } else {
                                targetName = c;
                                const cData = currentData.vargas.D1.grahas && currentData.vargas.D1.grahas[c];
                                cLon = cData ? cData.longitude : 0;
                                const cSign = cData ? cData.sign : '';
                                const cDeg = cData && cData.degree_0_to_30 !== undefined ? cData.degree_0_to_30.toFixed(1) : '';
                                targetDesc = `${c} (${cDeg}° ${cSign})`;
                            }
                            
                            let diff = (cLon - pLon + 360.0) % 360.0;
                            const housesAway = Math.floor(diff / 30.0) + 1;
                            const degSep = Math.round(diff);
                            
                            let ruleDesc = '';
                            if (housesAway === 7) {
                                ruleDesc = "7th House Opposition (all planets cast 100% full aspect onto the 7th house / opposite point).";
                            } else if (p === 'Mars' && (housesAway === 4 || housesAway === 8)) {
                                ruleDesc = `Mars Special Full Aspect (${housesAway}th house Chaturasra/Randhra Drishti).`;
                            } else if (p === 'Jupiter' && (housesAway === 5 || housesAway === 9)) {
                                ruleDesc = `Jupiter Special Full Aspect (${housesAway}th house Trikona Drishti).`;
                            } else if (p === 'Saturn' && (housesAway === 3 || housesAway === 10)) {
                                ruleDesc = `Saturn Special Full Aspect (${housesAway}th house Upachaya Drishti).`;
                            } else {
                                ruleDesc = `Partial Parashari angle based on ${degSep}° geometric separation.`;
                            }
                            
                            let effectDesc = '';
                            if (entry.plus > 0) {
                                effectDesc = `Contributes +${Math.round(entry.plus)} Virūpas of auspicious, protective light.`;
                            } else if (entry.minus > 0) {
                                effectDesc = `Imposes -${Math.round(entry.minus)} Virūpas of challenging or frictional tension.`;
                            } else {
                                effectDesc = `Aspect strength: ${rawRounded} Virūpas out of 60.`;
                            }
                            
                            const cellTooltip = `<strong>${p} → ${targetName}: ${rawRounded} Virūpas</strong><br>• <strong>Target:</strong> ${targetDesc}<br>• <strong>Separation:</strong> ${degSep}° (${housesAway} houses away from ${p})<br>• <strong>Rule:</strong> ${ruleDesc}<br>• <strong>Effect:</strong> ${effectDesc}`;
                            
                            html += `<td class="tooltip-target" data-tooltip="${cellTooltip}" style="cursor:help;">${rawRounded}</td>`;
                        } else {
                            html += `<td></td>`;
                        }
                    }
                });
                tr.innerHTML = html;
                tbody.appendChild(tr);
            });
            
            // Totals Row (+)
            const trPlus = document.createElement('tr');
            trPlus.className = 'total-row';
            let plusHtml = `<td class="tooltip-target" data-tooltip="<strong>Total Benefic Aspect (+)</strong><br>Sum of supportive, harmonious aspectual rays received from benefics."><strong style="color: var(--status-benefic);">+</strong></td>`;
            columnsList.forEach(c => {
                const cKey = c.toString();
                const v = totals && totals[cKey] ? Math.round(totals[cKey].plus) : 0;
                const tgt = isHouse ? `House ${c}` : c;
                const tip = `<strong>${tgt} — Total Benefic Aspect (+)</strong><br>Receives a total of <strong>+${v} Virūpas</strong> of auspicious, protective aspectual rays from benefics.`;
                plusHtml += `<td class="tooltip-target" data-tooltip="${tip}" style="color: var(--status-benefic); font-weight: bold; cursor:help;">${v > 0 ? v : ''}</td>`;
            });
            trPlus.innerHTML = plusHtml;
            tbody.appendChild(trPlus);
            
            // Totals Row (-)
            const trMinus = document.createElement('tr');
            trMinus.className = 'total-row';
            let minusHtml = `<td class="tooltip-target" data-tooltip="<strong>Total Malefic Aspect (-)</strong><br>Sum of stressful or frictional aspectual tension received from malefics."><strong style="color: var(--status-malefic);">-</strong></td>`;
            columnsList.forEach(c => {
                const cKey = c.toString();
                const v = totals && totals[cKey] ? Math.round(totals[cKey].minus) : 0;
                const tgt = isHouse ? `House ${c}` : c;
                const tip = `<strong>${tgt} — Total Malefic Aspect (-)</strong><br>Receives a total of <strong>-${v} Virūpas</strong> of challenging, frictional aspectual pressure from malefics.`;
                minusHtml += `<td class="tooltip-target" data-tooltip="${tip}" style="color: var(--status-malefic); font-weight: bold; cursor:help;">${v > 0 ? v : ''}</td>`;
            });
            trMinus.innerHTML = minusHtml;
            tbody.appendChild(trMinus);
        });
    }

    function updateAspectsWidgetForCell(cell) {
        const currentData = window.currentChartData;
        if (!currentData) return;
        const widgetType = cell.dataset.widget;
        const vargaSelect = cell.querySelector('.varga-select');
        const varga = vargaSelect ? vargaSelect.value : 'D1';
        
        let advData = null;
        if (currentData.varga_advanced_aspects && currentData.varga_advanced_aspects[varga]) {
            advData = currentData.varga_advanced_aspects[varga];
        } else {
            advData = currentData.advanced_aspects;
        }
        if (!advData) return;
        
        const table = cell.querySelector('table');
        const titleSpan = cell.querySelector('.aspect-table-title');
        
        const planetsList = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"];
        const housesList = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12];
        
        if (widgetType === 'aspects-planets') {
            if (titleSpan) titleSpan.textContent = `${varga} - Aspects (Planets)`;
            if (table) renderKalaAspectTable(table, 'planets', planetsList, false, advData);
        } else if (widgetType === 'aspects-equal-houses') {
            if (titleSpan) titleSpan.textContent = `${varga} - Aspects to Equal Houses`;
            if (table) renderKalaAspectTable(table, 'equal_cusps', housesList, true, advData);
        } else if (widgetType === 'aspects-bhava-chalita') {
            if (titleSpan) titleSpan.textContent = `${varga} - Aspects to Bhava Chalita`;
            if (table) renderKalaAspectTable(table, 'cusps', housesList, true, advData);
        }
    }

    function updateAspectsTable(varga = 'D1') {
        document.querySelectorAll('.grid-cell[data-widget^="aspects-"]').forEach(cell => {
            updateAspectsWidgetForCell(cell);
        });
        
        const planetsList = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"];
        const housesList = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12];
        const currentData = window.currentChartData;
        const advData = (currentData && currentData.varga_advanced_aspects && currentData.varga_advanced_aspects[varga])
            ? currentData.varga_advanced_aspects[varga]
            : (currentData ? currentData.advanced_aspects : null);
        if (advData) {
            renderKalaAspectTable('kalaAspectsPlanetsTable', 'planets', planetsList, false, advData);
            renderKalaAspectTable('kalaAspectsEqualHousesTable', 'equal_cusps', housesList, true, advData);
            renderKalaAspectTable('kalaAspectsBhavaChalitaTable', 'cusps', housesList, true, advData);
        }
    }

    if (window.widgetRegistry) {
        window.widgetRegistry.register('aspects-planets', {
            id: 'aspects-planets',
            title: 'Aspects (Planets)',
            icon: '👁️',
            category: 'Positions',
            onUpdate: function(cell, chartData) {
                updateAspectsWidgetForCell(cell);
            }
        });

        window.widgetRegistry.register('aspects-equal-houses', {
            id: 'aspects-equal-houses',
            title: 'Aspects (Equal Houses)',
            icon: '📐',
            category: 'Positions',
            onUpdate: function(cell, chartData) {
                updateAspectsWidgetForCell(cell);
            }
        });

        window.widgetRegistry.register('aspects-bhava-chalita', {
            id: 'aspects-bhava-chalita',
            title: 'Aspects (Bhava Chalita)',
            icon: '🏛️',
            category: 'Positions',
            onUpdate: function(cell, chartData) {
                updateAspectsWidgetForCell(cell);
            }
        });
    }

    window.renderKalaAspectTable = renderKalaAspectTable;
    window.updateAspectsWidgetForCell = updateAspectsWidgetForCell;
    window.updateAspectsTable = updateAspectsTable;
})();
