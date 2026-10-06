/**
 * Astra Rāśi Dṛṣṭi (Sign Aspects) Widget
 * 
 * Implements Jaimini sign-to-sign visual aspect calculations:
 * Movable signs aspect fixed signs (except adjacent);
 * Fixed signs aspect movable signs (except adjacent);
 * Dual signs aspect all other dual signs.
 */

(function() {
    function updateRashiDrishtiWidget(cell, chartData) {
        if (!cell) {
            cell = document.getElementById('widgetMaximizeContainer') || document.querySelector('.grid-cell[data-widget="rashi-drishti"]');
        }
        if (!cell) return;
        const currentData = chartData || window.currentChartData;
        const tbody = cell.querySelector('.rashi-drishti-table tbody');
        if (!tbody) return;
        tbody.innerHTML = '';

        const vargaSelect = cell.querySelector('.varga-select');
        const varga = vargaSelect ? vargaSelect.value : 'D1';

        if (vargaSelect && !vargaSelect.dataset.listenerBound) {
            vargaSelect.dataset.listenerBound = 'true';
            vargaSelect.addEventListener('change', () => {
                updateRashiDrishtiWidget(cell, chartData);
            });
        }

        const catalogSigns = (typeof window !== 'undefined' && window.AstroCatalog)
            ? window.AstroCatalog.signs
            : [
                { name: 'Aries', modality: 'Movable' }, { name: 'Taurus', modality: 'Fixed' },
                { name: 'Gemini', modality: 'Dual' }, { name: 'Cancer', modality: 'Movable' },
                { name: 'Leo', modality: 'Fixed' }, { name: 'Virgo', modality: 'Dual' },
                { name: 'Libra', modality: 'Movable' }, { name: 'Scorpio', modality: 'Fixed' },
                { name: 'Sagittarius', modality: 'Dual' }, { name: 'Capricorn', modality: 'Movable' },
                { name: 'Aquarius', modality: 'Fixed' }, { name: 'Pisces', modality: 'Dual' }
            ];

        const occupantsMap = {};
        catalogSigns.forEach(s => { occupantsMap[s.name] = []; });
        if (currentData && currentData.vargas && currentData.vargas[varga]) {
            const grahas = currentData.vargas[varga].grahas || {};
            for (const [pName, pData] of Object.entries(grahas)) {
                if (pData.sign && occupantsMap[pData.sign]) {
                    occupantsMap[pData.sign].push(pName);
                }
            }
        }

        catalogSigns.forEach(signObj => {
            const sign = signObj.name;
            const tr = document.createElement('tr');
            tr.className = 'interactive-table-row';
            tr.dataset.type = 'sign';
            tr.dataset.id = sign;
            tr.style.cursor = 'pointer';

            const modMeta = (window.AstroCatalog && window.AstroCatalog.modalities[signObj.modality])
                ? window.AstroCatalog.modalities[signObj.modality]
                : { sanskrit: signObj.modality, label: signObj.modality, color: '#4a3325', bg: '#f5f0eb' };
            const modLabel = modMeta.label || signObj.modality;
            const modSanskrit = modMeta.sanskrit || '';

            let aspects = null;
            if (currentData && currentData.aspect_matrices && currentData.aspect_matrices.rasi_drishti) {
                const rd = currentData.aspect_matrices.rasi_drishti;
                aspects = (rd.sign_to_signs && rd.sign_to_signs[sign])
                    || rd[sign]
                    || (rd.by_sign && rd.by_sign[sign])
                    || null;
            }
            if (!aspects && window.AstroCatalog && window.AstroCatalog.getAspectingSigns) {
                aspects = window.AstroCatalog.getAspectingSigns(sign);
            }
            if (!aspects) aspects = [];
            const occupants = occupantsMap[sign] || [];

            const aspectedPlanets = [];
            aspects.forEach(asSign => {
                const occ = occupantsMap[asSign] || [];
                occ.forEach(p => {
                    aspectedPlanets.push(`${p} (${asSign.substring(0, 3)})`);
                });
            });

            const signTip = `<strong>${sign} (${modLabel})</strong><br>In Jaimini astrology, signs cast direct sight (Rāśi Dṛṣṭi) on other signs according to modality.`;
            const modTip = `<strong>${modLabel} (${modSanskrit}) Sign</strong><br>${modLabel === 'Movable' ? 'Movable signs aspect all fixed signs except the one immediately adjacent to them.' : (modLabel === 'Fixed' ? 'Fixed signs aspect all movable signs except the one immediately adjacent to them.' : 'Dual signs aspect all other three dual signs.')}`;
            const occTip = `<strong>Occupants in ${sign}: ${occupants.join(', ') || 'None'}</strong><br>${occupants.length > 0 ? 'These planets cast Rāśi Dṛṣṭi alongside the sign itself.' : 'No planets occupy ' + sign + '.'}`;
            const aspTip = `<strong>Signs Aspected by ${sign}</strong><br>${aspects.join(', ')} receive the direct energetic influence of ${sign}.`;
            const aspPlanetsTip = `<strong>Planets Aspected by ${sign}</strong><br>${aspectedPlanets.length > 0 ? aspectedPlanets.join(', ') + ' receive direct Rāśi Dṛṣṭi.' : 'No planets reside in the aspected signs.'}`;

            const glyphHtml = (typeof TableBuilder !== 'undefined' && TableBuilder.renderZodiacGlyph) ? TableBuilder.renderZodiacGlyph(sign) : '';
            const signCell = `<td class="tooltip-target" data-tooltip="${signTip}" style="font-weight: 700; color: #4a3325; background: #fcfaf5; text-align: left; padding: 5px 8px; cursor:help; font-size: 12px;">${glyphHtml} ${sign}</td>`;
            const modBadge = `<span style="display: inline-block; font-size: 12px; font-weight: 700; padding: 2px 6px; border-radius: 4px; color: ${modMeta.color}; background: ${modMeta.bg}; border: 1px solid ${modMeta.color}33;">${modLabel}</span>`;
            const modCell = `<td class="tooltip-target" data-tooltip="${modTip}" style="padding: 4px 6px; cursor:help;">${modBadge}</td>`;
            
            const occText = occupants.length > 0 
                ? `<strong style="color: #2b1810; font-size: 12px;">${occupants.join(', ')}</strong>` 
                : `<span style="color: #9ca3af; font-size: 12px;">—</span>`;
            const occCell = `<td class="tooltip-target" data-tooltip="${occTip}" style="padding: 4px 6px; font-size: 12px; cursor:help;">${occText}</td>`;

            const aspSignsText = aspects.join(', ');
            const aspCell = `<td class="tooltip-target" data-tooltip="${aspTip}" style="padding: 4px 6px; font-size: 12px; color: #4b5563; cursor:help;">${aspSignsText}</td>`;

            const aspPlanetsText = aspectedPlanets.length > 0
                ? `<strong style="color: #1e3a8a; font-size: 12px;">${aspectedPlanets.join(', ')}</strong>` 
                : `<span style="color: #9ca3af; font-size: 12px;">—</span>`;
            const aspPlanetsCell = `<td class="tooltip-target" data-tooltip="${aspPlanetsTip}" style="padding: 4px 6px; font-size: 12px; cursor:help;">${aspPlanetsText}</td>`;

            tr.innerHTML = signCell + modCell + occCell + aspCell + aspPlanetsCell;
            tbody.appendChild(tr);
        });
    }

    if (window.widgetRegistry) {
        window.widgetRegistry.register('rashi-drishti', {
            id: 'rashi-drishti',
            title: 'Rāśi Dṛṣṭi (Sign Aspects)',
            icon: '️',
            category: 'Aspects',
            render: function(container, chartData, options) {
                updateRashiDrishtiWidget(container, chartData);
            },
            onUpdate: function(cell, chartData) {
                updateRashiDrishtiWidget(cell, chartData);
            }
        });
    }

    window.updateRashiDrishtiWidget = updateRashiDrishtiWidget;
})();
