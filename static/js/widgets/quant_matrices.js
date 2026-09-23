/**
 * Astra Quantitative Matrices Widget
 * 
 * Renders cross-planetary relational strength matrices for Lajjitadi Avasthas,
 * Drishti Yuti, Shadbala, and Yoga Judgment Balas (Ishta, Subha, Cheshta, etc.).
 */

(function() {
    function updateQuantMatricesTableForCell(cell, chartData) {
        const currentData = chartData || window.currentChartData;
        const tbody = cell.querySelector('tbody');
        const tfoot = cell.querySelector('tfoot');
        const vargaSelect = cell.querySelector('.varga-select');
        const matrixSelect = cell.querySelector('.matrix-type-select');
        
        if (!tbody || !matrixSelect || !currentData) return;
        
        const varga = vargaSelect ? vargaSelect.value : 'D1';
        let matrixType = matrixSelect ? matrixSelect.value : 'Drishti Yuti';
        
        // In divisional charts (D2 to D60), classical Kala software evaluates Lajjitadi Avasthas via Drishti Yuti and ShadBala
        if (varga !== 'D1') {
            if (matrixType !== 'Drishti Yuti' && matrixType !== 'ShadBala') {
                matrixType = 'Drishti Yuti';
                if (matrixSelect) matrixSelect.value = 'Drishti Yuti';
            }
        }

        if (matrixSelect) {
            const optgroups = matrixSelect.querySelectorAll('optgroup');
            optgroups.forEach(og => {
                if (og.label.startsWith('Yoga Judgment Balas')) {
                    if (varga !== 'D1') {
                        og.label = 'Yoga Judgment Balas (D1 Only)';
                        og.querySelectorAll('option').forEach(opt => opt.disabled = true);
                    } else {
                        og.label = 'Yoga Judgment Balas';
                        og.querySelectorAll('option').forEach(opt => opt.disabled = false);
                    }
                }
            });
        }

        const titleEl = cell.querySelector('.quant-matrices-title');
        if (titleEl) {
            if (varga === 'D1') {
                titleEl.textContent = `${varga} - Strength Matrices`;
            } else {
                titleEl.textContent = `${varga} - Strength Matrices (${matrixType})`;
            }
        }
        
        tbody.innerHTML = '';
        if (tfoot) {
            let trFoot = tfoot.querySelector('tr');
            if (trFoot) {
                trFoot.innerHTML = '<td style="background-color: var(--bg-surface-alt);"><strong>+</strong></td>';
            }
        }
        
        const matrices = currentData.avastha_matrix;
        if (!matrices || !matrices[varga] || !matrices[varga][matrixType]) return;
        
        const matrixData = matrices[varga][matrixType];
        const planets = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn'];
        
        planets.forEach(pGive => {
            const tr = document.createElement('tr');
            const thRow = document.createElement('td');
            thRow.innerHTML = `<strong>${pGive}</strong>`;
            thRow.style.backgroundColor = 'var(--bg-surface-alt)';
            tr.appendChild(thRow);
            
            planets.forEach(pRecv => {
                const td = document.createElement('td');
                const data = matrixData[pGive] ? matrixData[pGive][pRecv] : null;
                
                if (pGive === pRecv) {
                    // Diagonal Cells (Giver == Receiver)
                    if (matrixType === 'Drishti Yuti') {
                        const vimBase = data && data.vimshopaka_base !== undefined ? data.vimshopaka_base : (data && data.base !== null && data.base !== undefined ? data.base : null);
                        const moolaFlag = data && data.has_moolatrikona_flag ? '*2' : '';
                        const asp = data && data.aspect_virupas !== undefined ? data.aspect_virupas : 0;
                        
                        if (vimBase !== null && vimBase !== undefined) {
                            td.innerHTML = `
                                <div class="quant-diagonal-stack" style="line-height: 1.1;">
                                    <span style="font-size: 9px; color: var(--text-muted); text-transform: uppercase;">Vimsho.</span>
                                    <span class="text-black-bold" style="font-size: 12px;">${vimBase.toFixed(1)}${moolaFlag}</span>
                                </div>
                            `;
                            td.title = `${pRecv} Vimshopaka Dignity: ${vimBase.toFixed(1)}${moolaFlag}`;
                            td.classList.add('has-tooltip');
                            td.setAttribute('data-tooltip', td.title);
                        } else if (asp > 0.001) {
                            td.innerHTML = `<span class="text-black-bold" style="font-size: 13px;">${asp.toFixed(1)}</span>`;
                            td.title = `${pRecv} Self Aspect: ${asp.toFixed(1)} Virupas`;
                            td.classList.add('has-tooltip');
                            td.setAttribute('data-tooltip', td.title);
                        } else {
                            td.innerHTML = '';
                        }
                    } else if (data && data.base !== null && data.base !== undefined) {
                        if (matrixType !== 'ShadBala' && matrixType !== 'Vimshopaka' && data.base_negative !== null && data.base_negative !== undefined) {
                            const diff = data.diff !== null && data.diff !== undefined ? data.diff : (data.base - data.base_negative);
                            const moolaFlag = data.has_moolatrikona_flag ? '*2' : '';
                            td.innerHTML = `
                                <div class="quant-diagonal-stack">
                                    <span class="text-green">${data.base.toFixed(1)}</span>
                                    <span class="text-black-bold">${diff.toFixed(1)}${moolaFlag}</span>
                                    <span class="text-red">${data.base_negative.toFixed(1)}</span>
                                </div>
                            `;
                            const netTotStr = data.net_total !== null && data.net_total !== undefined ? `. Final Net Total: ${data.net_total.toFixed(1)}` : '';
                            td.title = `${pRecv} Base: ${data.base.toFixed(1)}, Difference: ${diff.toFixed(1)}${moolaFlag}, Negative: ${data.base_negative.toFixed(1)}${netTotStr}`;
                        } else {
                            const moolaFlag = data.has_moolatrikona_flag ? '*2' : '';
                            const label = matrixType === 'Vimshopaka' ? 'Vimshopaka Dignity' : 'Starting Strength';
                            td.innerHTML = `<span class="text-black-bold" style="font-size: 13px;">${data.base.toFixed(1)}${moolaFlag}</span>`;
                            const netTotStr = data.net_total !== null && data.net_total !== undefined ? `. Final Net Total: ${data.net_total.toFixed(1)}` : '';
                            td.title = `${pRecv} ${label}: ${data.base.toFixed(1)}${moolaFlag}${netTotStr}`;
                        }
                        td.classList.add('has-tooltip');
                        td.setAttribute('data-tooltip', td.title);
                    } else {
                        td.innerHTML = '';
                    }
                } else {
                    // Off-Diagonal Cells (Giver != Receiver)
                    if (matrixType === 'Drishti Yuti') {
                        const val = (data && data.pull !== undefined && data.pull !== null) ? data.pull : (data && data.aspect_virupas !== undefined ? data.aspect_virupas : 0);
                        const posVal = (data && data.pos_pull !== undefined && data.pos_pull > 0) ? data.pos_pull : ((data && data.positive_pull !== undefined && data.positive_pull > 0) ? data.positive_pull : val);
                        const negVal = (data && data.neg_pull !== undefined && data.neg_pull > 0) ? data.neg_pull : ((data && data.negative_pull !== undefined && data.negative_pull > 0) ? data.negative_pull : val);

                        if (val > 0.001 || posVal > 0.001 || negVal > 0.001) {
                            if (data.has_pos && data.has_neg) {
                                td.innerHTML = `
                                    <div class="quant-cell-split">
                                        <div class="quant-sub-col text-red">
                                            <span>${negVal.toFixed(1)}</span>
                                        </div>
                                        <div class="quant-sub-col text-green">
                                            <span>${posVal.toFixed(1)}</span>
                                        </div>
                                    </div>
                                `;
                                td.title = `${pGive} affects ${pRecv}: -${negVal.toFixed(1)} (Combustion) / +${posVal.toFixed(1)} (Delight)`;
                            } else if (data.has_pos || data.color_state === 'positive') {
                                const displayVal = posVal > 0.001 ? posVal : val;
                                td.innerHTML = `<span class="text-green">${displayVal.toFixed(1)}</span>`;
                                td.title = `${pGive} delights ${pRecv}: +${displayVal.toFixed(1)} Virupas`;
                            } else if (data.has_neg || data.color_state === 'negative') {
                                const displayVal = negVal > 0.001 ? negVal : val;
                                td.innerHTML = `<span class="text-red">${displayVal.toFixed(1)}</span>`;
                                td.title = `${pGive} starves/agitates ${pRecv}: -${displayVal.toFixed(1)} Virupas`;
                            } else if (data.has_neutral || data.color_state === 'neutral') {
                                td.innerHTML = `<span class="text-blue">${val.toFixed(1)}</span>`;
                                td.title = `${pGive} neutrally aspects ${pRecv}: ${val.toFixed(1)} Virupas`;
                            } else {
                                td.innerHTML = `<span class="text-gray">-</span>`;
                            }
                            td.classList.add('has-tooltip');
                            td.setAttribute('data-tooltip', td.title);
                        } else {
                            td.innerHTML = '<span class="text-gray">-</span>';
                        }
                    } else {
                        const hasPos = data && data.has_pos;
                        const hasNeg = data && data.has_neg;
                        const hasNeu = data && data.has_neutral;
                        
                        const posPull = data && data.pos_pull !== undefined ? data.pos_pull : (data && data.positive_pull !== undefined ? data.positive_pull : 0);
                        const negPull = data && data.neg_pull !== undefined ? data.neg_pull : (data && data.negative_pull !== undefined ? data.negative_pull : 0);
                        const neuPull = data && data.neu_pull !== undefined ? data.neu_pull : (data && data.neutral_pull !== undefined ? data.neutral_pull : 0);
                        
                        const hasIsolatedPos = data && data.isolated_positive !== null && data.isolated_positive !== undefined;
                        const hasIsolatedNeg = data && data.isolated_negative !== null && data.isolated_negative !== undefined;
                        const hasIsolatedNeu = data && data.isolated_neutral !== null && data.isolated_neutral !== undefined;
                        
                        if (hasPos && hasNeg) {
                            td.innerHTML = `
                                <div class="quant-cell-split">
                                    <div class="quant-sub-col text-red">
                                        <span>${negPull.toFixed(1)}</span>
                                        ${hasIsolatedNeg ? `<span>${data.isolated_negative.toFixed(1)}</span>` : ''}
                                    </div>
                                    <div class="quant-sub-col text-green">
                                        <span>${posPull.toFixed(1)}</span>
                                        ${hasIsolatedPos ? `<span>+${data.isolated_positive.toFixed(1)}</span>` : ''}
                                    </div>
                                </div>
                            `;
                            const isoInfo = hasIsolatedNeg && hasIsolatedPos ? ` (Isolated: ${data.isolated_negative.toFixed(1)} / +${data.isolated_positive.toFixed(1)})` : '';
                            td.title = `${pGive} affects ${pRecv}: Negative pull -${negPull.toFixed(1)} | Positive pull +${posPull.toFixed(1)}${isoInfo}`;
                            td.classList.add('has-tooltip');
                            td.setAttribute('data-tooltip', td.title);
                        } else if (hasPos) {
                            td.innerHTML = `
                                <div class="quant-sub-col text-green">
                                    <span>${posPull.toFixed(1)}</span>
                                    ${hasIsolatedPos ? `<span>+${data.isolated_positive.toFixed(1)}</span>` : ''}
                                </div>
                            `;
                            const isoInfo = hasIsolatedPos ? ` (Isolated: +${data.isolated_positive.toFixed(1)})` : '';
                            td.title = `${pGive} delights ${pRecv}: +${posPull.toFixed(1)}${isoInfo}`;
                            td.classList.add('has-tooltip');
                            td.setAttribute('data-tooltip', td.title);
                        } else if (hasNeg) {
                            td.innerHTML = `
                                <div class="quant-sub-col text-red">
                                    <span>${negPull.toFixed(1)}</span>
                                    ${hasIsolatedNeg ? `<span>${data.isolated_negative.toFixed(1)}</span>` : ''}
                                </div>
                            `;
                            const isoInfo = hasIsolatedNeg ? ` (Isolated: ${data.isolated_negative.toFixed(1)})` : '';
                            td.title = `${pGive} starves/agitates ${pRecv}: -${negPull.toFixed(1)}${isoInfo}`;
                            td.classList.add('has-tooltip');
                            td.setAttribute('data-tooltip', td.title);
                        } else if (hasNeu) {
                            td.innerHTML = `
                                <div class="quant-sub-col text-blue">
                                    <span>${neuPull.toFixed(1)}</span>
                                    ${hasIsolatedNeu ? `<span>${data.isolated_neutral.toFixed(1)}</span>` : ''}
                                </div>
                            `;
                            const isoInfo = hasIsolatedNeu ? ` (Base: ${data.isolated_neutral.toFixed(1)})` : '';
                            td.title = `${pGive} neutrally pulls ${pRecv}: ${neuPull.toFixed(1)}${isoInfo}`;
                            td.classList.add('has-tooltip');
                            td.setAttribute('data-tooltip', td.title);
                        } else {
                            td.innerHTML = '<span class="text-gray">-</span>';
                        }
                    }
                }
                tr.appendChild(td);
            });
            tbody.appendChild(tr);
        });
        
        // Bottom Row (<tfoot>)
        if (tfoot) {
            let trFoot = tfoot.querySelector('tr');
            if (!trFoot) {
                trFoot = document.createElement('tr');
                tfoot.appendChild(trFoot);
            }
            trFoot.innerHTML = '<td style="background-color: var(--bg-surface-alt);"><strong>+</strong></td>';
            planets.forEach(pRecv => {
                const diagData = matrixData[pRecv] ? matrixData[pRecv][pRecv] : null;
                const tdFoot = document.createElement('td');
                tdFoot.style.backgroundColor = 'var(--bg-app)';
                if (diagData && diagData.net_total !== undefined && diagData.net_total !== null) {
                    const val = diagData.net_total;
                    const isNeg = val < 0;
                    const sign = val > 0 ? '+' : '';
                    const colorClass = isNeg ? 'text-malefic' : 'text-black-bold';
                    tdFoot.innerHTML = `<span class="${colorClass}" style="font-weight: bold; font-size: 12px;">${sign}${val.toFixed(1)}</span>`;
                    tdFoot.title = `${pRecv} Final Net Total: ${sign}${val.toFixed(1)}`;
                } else {
                    tdFoot.innerHTML = '-';
                }
                tdFoot.classList.add('has-tooltip');
                tdFoot.setAttribute('data-tooltip', tdFoot.title);
                trFoot.appendChild(tdFoot);
            });
        }
    }

    function updateQuantMatricesTable() {
        document.querySelectorAll('.grid-cell[data-widget="quant-matrices"]').forEach(cell => {
            updateQuantMatricesTableForCell(cell);
        });
    }

    if (window.widgetRegistry) {
        window.widgetRegistry.register('quant-matrices', {
            id: 'quant-matrices',
            title: 'Strength Matrices',
            icon: '🔢',
            category: 'Strengths',
            onUpdate: function(cell, chartData) {
                updateQuantMatricesTableForCell(cell, chartData);
            }
        });
    }

    window.updateQuantMatricesTableForCell = updateQuantMatricesTableForCell;
    window.updateQuantMatricesTable = updateQuantMatricesTable;
})();
