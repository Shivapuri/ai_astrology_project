/**
 * Astra Stage 3: Bhāva Bala & House Capacity Widget
 * 
 * Provides comprehensive 12-house diagnostic synthesis:
 * - Parāśara 3 Pillars: Bhāvādhipati Bala (Lord), Bhāva Digbala, Bhāva Dṛṣṭi Bala
 * - Harṣa Bala & Dusthana Planetary Joy (Harsha, Sarala, Vimala)
 * - House Atmosphere (Environmental Weather, Net Score, Auspicious/Inauspicious factors)
 * - Augmented Virūpas & Capacity Verdicts (Puṣṭa / Fortified vs Hīna / Depleted)
 */

(function() {
    function updateBhavaBalaWidget(container, chartData) {
        const currentData = chartData || window.currentChartData;
        const root = container || document;
        if (!currentData) return;

        const bb = currentData.bhava_bala;
        if (!bb) return;

        const tbody = root.querySelector('.bhava-bala-grid tbody');
        if (!tbody) return;
        tbody.innerHTML = '';

        const harshaData = currentData.harsha_bala || {};
        const dusthanaJoy = harshaData.dusthana_joy || {};
        const atmosphere = currentData.house_atmosphere || {};

        for (let h = 1; h <= 12; h++) {
            const hData = bb[h] || bb[String(h)] || {};
            const hAtm = atmosphere[h] || atmosphere[String(h)] || {};
            const hJoy = dusthanaJoy[h] || null;

            const sign = hData.sign || '--';
            const lord = hData.lord || '--';
            const lordBala = hData.bhavadhipathi_bala !== undefined ? hData.bhavadhipathi_bala.toFixed(1) : '--';
            const digBala = hData.bhava_digbala !== undefined ? hData.bhava_digbala.toFixed(1) : '--';
            const drishtiBala = hData.bhava_drishti_bala !== undefined ? ((hData.bhava_drishti_bala >= 0 ? '+' : '') + hData.bhava_drishti_bala.toFixed(1)) : '--';
            const totVir = hData.total_virupas !== undefined ? hData.total_virupas.toFixed(1) : '--';
            const totRup = hData.total_rupas !== undefined ? hData.total_rupas.toFixed(2) : (hData.total_virupas !== undefined ? (hData.total_virupas / 60).toFixed(2) : '--');
            const augVir = hData.augmented_virupas !== undefined ? hData.augmented_virupas.toFixed(1) : totVir;

            let joyText = '—';
            let joyColor = 'var(--text-muted)';
            if (hJoy && hJoy.is_active) {
                joyText = `${hJoy.yoga_name} (+${hJoy.bonus_units}u)`;
                joyColor = 'var(--status-benefic)';
            } else if (hJoy) {
                joyText = hJoy.is_active ? 'Active' : 'Neutral';
            }

            const weather = hAtm.environmental_weather || 'Neutral';
            const score = hAtm.net_atmosphere_score !== undefined ? ((hAtm.net_atmosphere_score >= 0 ? '+' : '') + hAtm.net_atmosphere_score.toFixed(0)) : '--';
            const classification = hAtm.classification || hData.classification || 'Neutral';

            // Styling based on capacity
            const isPusta = classification.toLowerCase().includes('puṣṭa') || classification.toLowerCase().includes('pusta') || (parseFloat(totRup) >= 8.0);
            const isHina = classification.toLowerCase().includes('hīna') || classification.toLowerCase().includes('hina') || (parseFloat(totRup) < 6.0);
            const statusColor = isPusta ? 'var(--status-benefic)' : (isHina ? 'var(--status-malefic)' : 'var(--text-primary)');

            const tr = document.createElement('tr');
            tr.className = 'interactive-table-row';
            tr.dataset.type = 'house';
            tr.dataset.id = h;
            tr.style.cursor = 'pointer';

            const tipH = `<strong>House ${h} (${sign})</strong><br>Ruled by ${lord}. Click to inspect house details in the Context Inspector.`;
            const tipLord = `<strong>Bhāvādhipati Bala: ${lordBala} Virūpas</strong><br>Strength contributed by house ruler ${lord} based on its Shadbala.`;
            const tipDig = `<strong>Bhāva Digbala: ${digBala} Virūpas</strong><br>Directional strength based on the genus of ${sign} and house angle.`;
            const tipDrishti = `<strong>Bhāva Dṛṣṭi Bala: ${drishtiBala} Virūpas</strong><br>Net aspectual rays cast onto the house cusp by all planets.`;
            const tipTot = `<strong>Total Bhāva Bala: ${totVir} Virūpas (${totRup} Rūpas)</strong><br>Base capacity across all 3 classical Parāśara pillars.`;
            const tipAug = `<strong>Augmented Virūpas: ${augVir} Virūpas</strong><br>Capacity adjusted for Lord Digbala bonus, sect bonus, and Sandhi wall leakages.`;
            const tipJoy = `<strong>Harṣa Bala: ${joyText}</strong><br>${hJoy ? hJoy.effect : 'Applies to Dusthana houses 6, 8, and 12.'}`;
            const tipAtm = `<strong>Atmosphere: ${weather} (${score})</strong><br>${(hAtm.auspicious_influences || []).slice(0, 3).join('<br>• ') || 'Standard cosmic weather'}`;

            tr.innerHTML = `
                <td class="tooltip-target" data-tooltip="${tipH}" style="padding: 6px 8px; font-weight: bold;">H${h}</td>
                <td class="tooltip-target" data-tooltip="${tipH}" style="padding: 6px 8px;"><strong>${sign}</strong> (${lord})</td>
                <td class="tooltip-target" data-tooltip="${tipLord}" style="text-align: right; padding: 6px 8px; font-family: monospace;">${lordBala}</td>
                <td class="tooltip-target" data-tooltip="${tipDig}" style="text-align: right; padding: 6px 8px; font-family: monospace;">${digBala}</td>
                <td class="tooltip-target" data-tooltip="${tipDrishti}" style="text-align: right; padding: 6px 8px; font-family: monospace;">${drishtiBala}</td>
                <td class="tooltip-target" data-tooltip="${tipTot}" style="text-align: right; padding: 6px 8px; font-family: monospace; font-weight: bold;">${totVir}</td>
                <td class="tooltip-target" data-tooltip="${tipTot}" style="text-align: right; padding: 6px 8px; font-family: monospace; font-weight: bold; color: ${statusColor};">${totRup}</td>
                <td class="tooltip-target" data-tooltip="${tipAug}" style="text-align: right; padding: 6px 8px; font-family: monospace; color: var(--text-heading); font-weight: 600;">${augVir}</td>
                <td class="tooltip-target" data-tooltip="${tipJoy}" style="padding: 6px 8px; color: ${joyColor}; font-weight: 600;">${joyText}</td>
                <td class="tooltip-target" data-tooltip="${tipAtm}" style="padding: 6px 8px;">${weather} <span style="font-family: monospace; color: var(--text-muted); font-size: 12px;">(${score})</span></td>
                <td class="tooltip-target" data-tooltip="${tipAtm}" style="padding: 6px 8px; font-weight: 600; color: ${statusColor};">${classification}</td>
            `;

            tr.onclick = function() {
                if (typeof window.selectEntity === 'function') {
                    window.selectEntity('house', h);
                }
            };

            tbody.appendChild(tr);
        }
    }

    if (window.widgetRegistry) {
        window.widgetRegistry.register('bhava-bala', {
            id: 'bhava-bala',
            title: 'Bhāva Bala & House Capacity',
            icon: '🏛',
            category: 'Strengths',
            render: function(container, chartData, options) {
                updateBhavaBalaWidget(container, chartData);
            },
            onUpdate: function(cell, chartData) {
                updateBhavaBalaWidget(cell, chartData);
            }
        });
    }

    window.updateBhavaBalaWidget = updateBhavaBalaWidget;
})();
