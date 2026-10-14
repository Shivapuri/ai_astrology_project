/**
 * Astra Aspects Widgets (Planets, Equal Houses, Bhava Chalita)
 * 
 * Renders full classical Kala Graha Drishti aspectual tables and ray strengths
 * across planets, equal cusps, and Campanus bhava chalita cusps.
 */

(function() {
    function escapeTooltipAttr(str) {
        if (!str) return '';
        return String(str).replace(/"/g, '&quot;');
    }

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
        const signsList = (typeof window !== 'undefined' && window.AstroCatalog)
            ? window.AstroCatalog.signs.map(s => s.name)
            : ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"];

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
            
            // Classification map for planets
            const classification = (adv && adv.classification) ||
                (currentData && currentData.aspect_matrices && currentData.aspect_matrices.benefic_malefic_totals && currentData.aspect_matrices.benefic_malefic_totals.classification) || {};

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
                
                let isPlanetBenefic = false;
                if (classification[p] !== undefined) {
                    isPlanetBenefic = Boolean(classification[p]);
                } else if (p === 'Jupiter' || p === 'Venus') {
                    isPlanetBenefic = true;
                } else if (p === 'Sun' || p === 'Mars' || p === 'Saturn' || p === 'Rahu' || p === 'Ketu') {
                    isPlanetBenefic = false;
                } else if (p === 'Moon') {
                    const moonIllum = currentData?.baseline?.lunar_phase?.illumination_pct ?? 50.0;
                    isPlanetBenefic = currentData?.baseline?.lunar_phase?.is_benefic ?? (moonIllum >= 50.0);
                } else if (p === 'Mercury') {
                    isPlanetBenefic = !(currentData?.combustion_status?.Mercury?.is_combust);
                }

                const pColor = isPlanetBenefic ? 'var(--status-benefic)' : 'var(--status-malefic)';
                const pType = isPlanetBenefic ? 'Benefic (Śubha)' : 'Malefic (Aśubha / Krūra)';
                const pTip = `<strong>${p} (${pSign} ${pDegStr}) — <span style="color:${pColor}; font-weight:600;">${pType}</span></strong><br>Aspecting planet casting sight (Graha Drishti).`;
                let html = `<td class="tooltip-target" data-tooltip="${escapeTooltipAttr(pTip)}"><strong style="color:${pColor} !important;">${p.substring(0, 2)}</strong></td>`;
                
                columnsList.forEach(c => {
                    const cKey = c.toString();
                    if (!isHouse && p === c) {
                        html += `<td class="tooltip-target" data-tooltip="<strong>${p} — Self Position</strong><br>A planet resides here and cannot cast an external aspect onto itself." style="color:var(--text-subtle); cursor:help;">--</td>`;
                    } else if (!isHouse && yutis[p] && yutis[p].includes(c)) {
                        const cData = currentData.vargas.D1.grahas && currentData.vargas.D1.grahas[c];
                        const cSign = cData ? cData.sign : pSign;
                        const yutiColor = isPlanetBenefic ? 'var(--status-benefic)' : 'var(--status-malefic)';
                        const yutiClass = isPlanetBenefic ? 'aspect-benefic' : 'aspect-malefic';
                        const yutiLabel = isPlanetBenefic ? 'Benefic Conjunction (+)' : 'Malefic Conjunction (-)';
                        const yutiTip = `<strong>Conjunction (Yuti): ${p} & ${c} — <span style="color:${yutiColor}; font-weight:600;">${yutiLabel}</span></strong><br>• Both planets occupy <strong>${cSign}</strong>.<br>• In Vedic astrology, sharing a sign creates direct synthesis and intense mutual exchange of energies.`;
                        html += `<td class="tooltip-target ${yutiClass}" data-tooltip="${escapeTooltipAttr(yutiTip)}" style="color:${yutiColor} !important; font-weight:bold; cursor:help;">Y</td>`;
                    } else {
                        let entry = aspects && aspects[cKey] && aspects[cKey][p] ? aspects[cKey][p] : null;
                        if (!entry && currentData && currentData.aspect_matrices) {
                            if (!isHouse && currentData.aspect_matrices.graha_drishti && currentData.aspect_matrices.graha_drishti.incoming && currentData.aspect_matrices.graha_drishti.incoming[cKey]) {
                                const rawVal = currentData.aspect_matrices.graha_drishti.incoming[cKey][p];
                                if (rawVal !== undefined) {
                                    const isBenefic = currentData.aspect_matrices.benefic_malefic_totals?.classification?.[p] ?? (p === 'Jupiter' || p === 'Venus');
                                    entry = {
                                        raw: rawVal,
                                        plus: isBenefic ? rawVal : 0,
                                        minus: isBenefic ? 0 : rawVal,
                                        net: isBenefic ? rawVal : -rawVal
                                    };
                                }
                            } else if (isHouse && (dataKey === 'equal_cusps' || dataKey === 'cusps') && currentData.aspect_matrices.cusp_drishti && currentData.aspect_matrices.cusp_drishti.by_house && currentData.aspect_matrices.cusp_drishti.by_house[c]) {
                                const rawVal = currentData.aspect_matrices.cusp_drishti.by_house[c][p];
                                if (rawVal !== undefined) {
                                    const isLord = (currentData.vargas?.D1?.grahas?.[p]?.ruled_houses || []).includes(Number(c));
                                    const isBenefic = isLord || (currentData.aspect_matrices.benefic_malefic_totals?.classification?.[p] ?? (p === 'Jupiter' || p === 'Venus'));
                                    entry = {
                                        raw: rawVal,
                                        plus: isBenefic ? rawVal : 0,
                                        minus: isBenefic ? 0 : rawVal,
                                        net: isBenefic ? rawVal : -rawVal
                                    };
                                }
                            }
                        }
                        if (entry && entry.raw > 0) {
                            const rawRounded = Math.round(entry.raw);
                            const isAspectBenefic = entry.plus > 0;
                            const isAspectMalefic = entry.minus > 0;
                            const aspectClass = isAspectBenefic ? 'aspect-benefic' : (isAspectMalefic ? 'aspect-malefic' : '');
                            const aspectColor = isAspectBenefic ? 'var(--status-benefic)' : (isAspectMalefic ? 'var(--status-malefic)' : 'inherit');
                            
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
                            if (isAspectBenefic) {
                                effectDesc = `<span style="color:var(--status-benefic); font-weight:600;">Contributes +${Math.round(entry.plus)} Virūpas of auspicious, protective light.</span>`;
                            } else if (isAspectMalefic) {
                                effectDesc = `<span style="color:var(--status-malefic); font-weight:600;">Imposes -${Math.round(entry.minus)} Virūpas of challenging or frictional tension.</span>`;
                            } else {
                                effectDesc = `Aspect strength: ${rawRounded} Virūpas out of 60.`;
                            }
                            
                            const cellTooltip = `<strong>${p} → ${targetName}: ${rawRounded} Virūpas</strong><br>• <strong>Target:</strong> ${targetDesc}<br>• <strong>Separation:</strong> ${degSep}° (${housesAway} houses away from ${p})<br>• <strong>Rule:</strong> ${ruleDesc}<br>• <strong>Effect:</strong> ${effectDesc}`;
                            
                            html += `<td class="tooltip-target ${aspectClass}" data-tooltip="${escapeTooltipAttr(cellTooltip)}" style="cursor:help; color:${aspectColor} !important; font-weight:600; font-variant-numeric: tabular-nums;">${rawRounded}</td>`;
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
            let plusHtml = `<td class="tooltip-target" data-tooltip="<strong>Total Benefic Aspect (+)</strong><br>Sum of supportive, harmonious aspectual rays received from benefics."><strong style="color: var(--status-benefic) !important;">+</strong></td>`;
            columnsList.forEach(c => {
                const cKey = c.toString();
                let v = totals && totals[cKey] ? Math.round(totals[cKey].plus) : 0;
                if (!v && currentData && currentData.aspect_matrices && currentData.aspect_matrices.benefic_malefic_totals) {
                    const bm = isHouse ? currentData.aspect_matrices.benefic_malefic_totals.cusps?.[c] : currentData.aspect_matrices.benefic_malefic_totals.planets?.[cKey];
                    if (bm) v = Math.round(bm.plus !== undefined ? bm.plus : (bm.benefic_virupas || 0));
                }
                const tgt = isHouse ? `House ${c}` : c;
                const tip = `<strong>${tgt} — Total Benefic Aspect (+)</strong><br>Receives a total of <strong>+${v} Virūpas</strong> of auspicious, protective aspectual rays from benefics.`;
                plusHtml += `<td class="tooltip-target aspect-benefic text-benefic" data-tooltip="${escapeTooltipAttr(tip)}" style="color: var(--status-benefic) !important; font-weight: bold; cursor:help;">${v > 0 ? v : ''}</td>`;
            });
            trPlus.innerHTML = plusHtml;
            tbody.appendChild(trPlus);
            
            // Totals Row (-)
            const trMinus = document.createElement('tr');
            trMinus.className = 'total-row';
            let minusHtml = `<td class="tooltip-target" data-tooltip="<strong>Total Malefic Aspect (-)</strong><br>Sum of stressful or frictional aspectual tension received from malefics."><strong style="color: var(--status-malefic) !important;">-</strong></td>`;
            columnsList.forEach(c => {
                const cKey = c.toString();
                let v = totals && totals[cKey] ? Math.round(totals[cKey].minus) : 0;
                if (!v && currentData && currentData.aspect_matrices && currentData.aspect_matrices.benefic_malefic_totals) {
                    const bm = isHouse ? currentData.aspect_matrices.benefic_malefic_totals.cusps?.[c] : currentData.aspect_matrices.benefic_malefic_totals.planets?.[cKey];
                    if (bm) v = Math.round(bm.minus !== undefined ? bm.minus : (bm.malefic_virupas || 0));
                }
                const tgt = isHouse ? `House ${c}` : c;
                const tip = `<strong>${tgt} — Total Malefic Aspect (-)</strong><br>Receives a total of <strong>-${v} Virūpas</strong> of challenging, frictional aspectual pressure from malefics.`;
                minusHtml += `<td class="tooltip-target aspect-malefic text-malefic" data-tooltip="${escapeTooltipAttr(tip)}" style="color: var(--status-malefic) !important; font-weight: bold; cursor:help;">${v > 0 ? v : ''}</td>`;
            });
            trMinus.innerHTML = minusHtml;
            tbody.appendChild(trMinus);
        });
    }

    function updateAspectsWidgetForCell(cell) {
        if (!cell) {
            cell = document.getElementById('widgetMaximizeContainer') || document.querySelector('.grid-cell[data-widget^="aspects-"]');
        }
        if (!cell) return;
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
            icon: '️',
            category: 'Positions',
            render: function(container, chartData, options) {
                updateAspectsWidgetForCell(container);
            },
            onUpdate: function(cell, chartData) {
                updateAspectsWidgetForCell(cell);
            }
        });

        window.widgetRegistry.register('aspects-equal-houses', {
            id: 'aspects-equal-houses',
            title: 'Aspects (Equal Houses)',
            icon: '',
            category: 'Positions',
            render: function(container, chartData, options) {
                updateAspectsWidgetForCell(container);
            },
            onUpdate: function(cell, chartData) {
                updateAspectsWidgetForCell(cell);
            }
        });

        window.widgetRegistry.register('aspects-bhava-chalita', {
            id: 'aspects-bhava-chalita',
            title: 'Aspects (Bhava Chalita)',
            icon: '️',
            category: 'Positions',
            render: function(container, chartData, options) {
                updateAspectsWidgetForCell(container);
            },
            onUpdate: function(cell, chartData) {
                updateAspectsWidgetForCell(cell);
            }
        });
    }

    window.renderKalaAspectTable = renderKalaAspectTable;
    window.updateAspectsWidgetForCell = updateAspectsWidgetForCell;
    window.updateAspectsTable = updateAspectsTable;
})();
