/**
 * Astra Ashtakavarga & Reductions Widget
 * 
 * Renders the 8-planet Ashtakavarga matrix (BAV, SAV), Trikona Shodhana,
 * Ekadhipatya Shodhana, and Shodhya Pindas (Rāśi, Graha, Yoga Pindas).
 */

(function() {
    function updateAshtakavargaWidget(cell, chartData) {
        if (!cell) {
            cell = document.getElementById('widgetMaximizeContainer') || document.querySelector('.grid-cell[data-widget="ashtakavarga"]');
        }
        if (!cell) return;
        const currentData = chartData || window.currentChartData;
        const tbody = cell.querySelector('tbody');
        if (!tbody || !currentData || !currentData.ashtakavarga) return;
        tbody.innerHTML = '';

        const avData = currentData.ashtakavarga;
        const viewSelect = cell.querySelector('.av-view-select');
        const viewMode = viewSelect ? viewSelect.value : 'raw';

        const planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Lagna"];
        const signNames = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"];
        let grid = (viewMode === 'trikona') ? avData.trikona_shodhana :
                   (viewMode === 'ekadhipatya') ? avData.ekadhipatya_shodhana : avData.bav;

        if (!grid) grid = avData.bav;

        planets.forEach(p => {
            if (!grid[p]) return;
            const pts = grid[p];
            const rowSum = pts.reduce((a, b) => a + b, 0);

            const tr = document.createElement('tr');
            const pName = p === 'Lagna' ? 'Ascendant' : p;
            const rowTip = `<strong>${pName} (${p.substring(0, 2)}) — Bhinnāṣṭakavarga (BAV)</strong><br>Benefic points (bindus) contributed by ${pName} across each sign (0-8 scale).`;
            let html = `<td class="tooltip-target" data-tooltip="${rowTip}" style="cursor:help;"><strong>${p.substring(0, 2)}</strong></td>`;
            
            pts.forEach((val, signIdx) => {
                const signName = signNames[signIdx];
                let color = val >= 5 ? '#15803d' : (val <= 3 ? '#b91c1c' : '#334155');
                const cellTip = `<strong>${pName} in ${signName}: ${val} Bindus</strong><br>• <strong>Score:</strong> ${val} of 8 possible auspicious points.<br>• <strong>Impact:</strong> ${val >= 5 ? 'High support (above average 4). Transits here foster growth, smooth progress, and strength.' : (val <= 3 ? 'Low support (below average 4). Transits require extra discipline, patience, and effort.' : 'Moderate baseline support (neutral flow).')}`;
                html += `<td class="tooltip-target" data-tooltip="${cellTip}" style="color:${color}; font-weight:${val >= 5 || val <= 3 ? 'bold' : 'normal'}; cursor:help;">${val}</td>`;
            });

            const sumTip = `<strong>${pName} — Total BAV Score: ${rowSum}</strong><br>Total benefic bindus contributed across all 12 signs. Average across the zodiac is ~48-54 points.`;
            html += `<td class="tooltip-target" data-tooltip="${sumTip}" style="font-weight:bold; background:#fcfaf5; cursor:help;">${rowSum}</td>`;
            tr.innerHTML = html;
            tbody.appendChild(tr);
        });

        // Populate SAV Row in tfoot
        const sav = (viewMode === 'trikona' && avData.sarvashtakavarga && avData.sarvashtakavarga.trikona_shodhana) ? avData.sarvashtakavarga.trikona_shodhana :
                    (viewMode === 'ekadhipatya' && avData.sarvashtakavarga && avData.sarvashtakavarga.ekadhipatya_shodhana) ? avData.sarvashtakavarga.ekadhipatya_shodhana :
                    (avData.sav || (avData.sarvashtakavarga && avData.sarvashtakavarga.total_sav) || []);

        for (let i = 0; i < 12; i++) {
            const cellSav = cell.querySelector(`.sav-${i}`);
            if (cellSav) {
                const v = sav[i] || 0;
                const signName = signNames[i];
                cellSav.textContent = v;
                cellSav.style.color = v >= 28 ? '#15803d' : (v <= 25 ? '#b91c1c' : '#4a3325');
                cellSav.className = `sav-${i} tooltip-target`;
                cellSav.style.cursor = 'help';
                cellSav.setAttribute('data-tooltip', `<strong>Sarvashtakavarga (SAV) — ${signName}: ${v} Bindus</strong><br>• <strong>Total:</strong> Combined benefic points from all 7 classical planets.<br>• <strong>Benchmark:</strong> Zodiac average is 28 points.<br>• <strong>Impact:</strong> ${v >= 28 ? 'Fortified sign (' + v + ' ≥ 28). Transits through ' + signName + ' produce fruitful, protective results.' : 'Challenged sign (' + v + ' < 28). Transits through ' + signName + ' require care and resilience.'}`);
            }
        }
        const savTotEl = cell.querySelector('.sav-tot');
        if (savTotEl) {
            const totalSAV = sav.reduce((a, b) => a + b, 0);
            savTotEl.textContent = totalSAV;
            savTotEl.className = 'sav-tot tooltip-target';
            savTotEl.style.cursor = 'help';
            savTotEl.setAttribute('data-tooltip', `<strong>Total Sarvashtakavarga Score: ${totalSAV}</strong><br>Sum of all planetary bindus across all 12 signs (standard sum is 337).`);
        }

        // Update Shodhya Pindas
        const pindaData = avData.shodhya_pindas || avData.sodhya_pindas;
        if (pindaData) {
            let rTotal = pindaData.rasi_pinda_total;
            let gTotal = pindaData.graha_pinda_total;
            let yTotal = pindaData.yoga_pinda_total;
            if (rTotal === undefined) {
                let r = 0, g = 0, y = 0, cnt = 0;
                for (const [k, v] of Object.entries(pindaData)) {
                    if (v && typeof v === 'object' && v.rasi_pinda !== undefined) {
                        r += v.rasi_pinda;
                        g += v.graha_pinda;
                        y += v.yoga_pinda;
                        cnt++;
                    }
                }
                if (cnt > 0) { rTotal = r; gTotal = g; yTotal = y; }
            }
            const rEl = cell.querySelector('.val-rasi-pinda');
            const gEl = cell.querySelector('.val-graha-pinda');
            const yEl = cell.querySelector('.val-yoga-pinda');
            if (rEl) {
                rEl.textContent = rTotal !== undefined ? rTotal : '-';
                rEl.className = 'val-rasi-pinda tooltip-target';
                rEl.style.cursor = 'help';
                rEl.setAttribute('data-tooltip', `<strong>Rāśi Piṇḍa (${rTotal})</strong><br>Spatial energy index after Trikona (triplicity) and Ekādhipatya (lordship) reductions. Measures purified zodiacal strength.`);
            }
            if (gEl) {
                gEl.textContent = gTotal !== undefined ? gTotal : '-';
                gEl.className = 'val-graha-pinda tooltip-target';
                gEl.style.cursor = 'help';
                gEl.setAttribute('data-tooltip', `<strong>Graha Piṇḍa (${gTotal})</strong><br>Planetary energy index weighted by each planet's cosmic multiplier. Measures purified planetary vitality.`);
            }
            if (yEl) {
                yEl.textContent = yTotal !== undefined ? yTotal : '-';
                yEl.className = 'val-yoga-pinda tooltip-target';
                yEl.style.cursor = 'help';
                yEl.setAttribute('data-tooltip', `<strong>Yoga Piṇḍa (${yTotal})</strong><br>Combined total of Rāśi Piṇḍa + Graha Piṇḍa. Primary indicator for transit timing and life endurance in classical Jyotish.`);
            }
        }
    }

    if (window.widgetRegistry) {
        window.widgetRegistry.register('ashtakavarga', {
            id: 'ashtakavarga',
            title: 'Ashtakavarga & Reductions',
            icon: '🔢',
            category: 'Strengths',
            render: function(container, chartData, options) {
                updateAshtakavargaWidget(container, chartData);
            },
            onUpdate: function(cell, chartData) {
                updateAshtakavargaWidget(cell, chartData);
            }
        });
    }

    window.updateAshtakavargaWidget = updateAshtakavargaWidget;
})();
