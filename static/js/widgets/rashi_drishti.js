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

        const SIGNS = [
            'Aries', 'Taurus', 'Gemini', 'Cancer',
            'Leo', 'Virgo', 'Libra', 'Scorpio',
            'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
        ];

        const SIGN_SYMBOLS = {
            'Aries': '♈ Aries', 'Taurus': '♉ Taurus', 'Gemini': '♊ Gemini', 'Cancer': '♋ Cancer',
            'Leo': '♌ Leo', 'Virgo': '♍ Virgo', 'Libra': '♎ Libra', 'Scorpio': '♏ Scorpio',
            'Sagittarius': '♐ Sagittarius', 'Capricorn': '♑ Capricorn', 'Aquarius': '♒ Aquarius', 'Pisces': '♓ Pisces'
        };

        const SIGN_MODALITY = {
            'Aries': { type: 'Chara', label: 'Movable', color: '#b91c1c', bg: '#fee2e2' },
            'Taurus': { type: 'Sthira', label: 'Fixed', color: '#1e40af', bg: '#dbeafe' },
            'Gemini': { type: 'Dwisvabhava', label: 'Dual', color: '#065f46', bg: '#d1fae5' },
            'Cancer': { type: 'Chara', label: 'Movable', color: '#b91c1c', bg: '#fee2e2' },
            'Leo': { type: 'Sthira', label: 'Fixed', color: '#1e40af', bg: '#dbeafe' },
            'Virgo': { type: 'Dwisvabhava', label: 'Dual', color: '#065f46', bg: '#d1fae5' },
            'Libra': { type: 'Chara', label: 'Movable', color: '#b91c1c', bg: '#fee2e2' },
            'Scorpio': { type: 'Sthira', label: 'Fixed', color: '#1e40af', bg: '#dbeafe' },
            'Sagittarius': { type: 'Dwisvabhava', label: 'Dual', color: '#065f46', bg: '#d1fae5' },
            'Capricorn': { type: 'Chara', label: 'Movable', color: '#b91c1c', bg: '#fee2e2' },
            'Aquarius': { type: 'Sthira', label: 'Fixed', color: '#1e40af', bg: '#dbeafe' },
            'Pisces': { type: 'Dwisvabhava', label: 'Dual', color: '#065f46', bg: '#d1fae5' }
        };

        const SIGN_ASPECTS = {
            'Aries': ['Leo', 'Scorpio', 'Aquarius'],
            'Taurus': ['Cancer', 'Libra', 'Capricorn'],
            'Gemini': ['Virgo', 'Sagittarius', 'Pisces'],
            'Cancer': ['Scorpio', 'Aquarius', 'Taurus'],
            'Leo': ['Libra', 'Capricorn', 'Aries'],
            'Virgo': ['Gemini', 'Sagittarius', 'Pisces'],
            'Libra': ['Aquarius', 'Taurus', 'Leo'],
            'Scorpio': ['Capricorn', 'Aries', 'Cancer'],
            'Sagittarius': ['Gemini', 'Virgo', 'Pisces'],
            'Capricorn': ['Taurus', 'Leo', 'Scorpio'],
            'Aquarius': ['Aries', 'Cancer', 'Libra'],
            'Pisces': ['Gemini', 'Virgo', 'Sagittarius']
        };

        const occupantsMap = {};
        SIGNS.forEach(s => { occupantsMap[s] = []; });
        if (currentData && currentData.vargas && currentData.vargas[varga]) {
            const grahas = currentData.vargas[varga].grahas || {};
            for (const [pName, pData] of Object.entries(grahas)) {
                if (pData.sign && occupantsMap[pData.sign]) {
                    occupantsMap[pData.sign].push(pName);
                }
            }
        }

        SIGNS.forEach(sign => {
            const tr = document.createElement('tr');
            tr.className = 'interactive-table-row';
            tr.dataset.type = 'sign';
            tr.dataset.id = sign;
            tr.style.cursor = 'pointer';
            const mod = SIGN_MODALITY[sign];
            const aspects = SIGN_ASPECTS[sign] || [];
            const occupants = occupantsMap[sign] || [];

            const aspectedPlanets = [];
            aspects.forEach(asSign => {
                const occ = occupantsMap[asSign] || [];
                occ.forEach(p => {
                    aspectedPlanets.push(`${p} (${asSign.substring(0, 3)})`);
                });
            });

            const signTip = `<strong>${sign} (${mod.label})</strong><br>In Jaimini astrology, signs cast direct sight (Rāśi Dṛṣṭi) on other signs according to modality.`;
            const modTip = `<strong>${mod.label} (${mod.type}) Sign</strong><br>${mod.label === 'Movable' ? 'Movable signs aspect all fixed signs except the one immediately adjacent to them.' : (mod.label === 'Fixed' ? 'Fixed signs aspect all movable signs except the one immediately adjacent to them.' : 'Dual signs aspect all other three dual signs.')}`;
            const occTip = `<strong>Occupants in ${sign}: ${occupants.join(', ') || 'None'}</strong><br>${occupants.length > 0 ? 'These planets cast Rāśi Dṛṣṭi alongside the sign itself.' : 'No planets occupy ' + sign + '.'}`;
            const aspTip = `<strong>Signs Aspected by ${sign}</strong><br>${aspects.join(', ')} receive the direct energetic influence of ${sign}.`;
            const aspPlanetsTip = `<strong>Planets Aspected by ${sign}</strong><br>${aspectedPlanets.length > 0 ? aspectedPlanets.join(', ') + ' receive direct Rāśi Dṛṣṭi.' : 'No planets reside in the aspected signs.'}`;

            const signCell = `<td class="tooltip-target" data-tooltip="${signTip}" style="font-weight: 700; color: #4a3325; background: #fcfaf5; text-align: left; padding: 5px 8px; cursor:help;">${SIGN_SYMBOLS[sign] || sign}</td>`;
            const modBadge = `<span style="display: inline-block; font-size: 10px; font-weight: 700; padding: 2px 6px; border-radius: 4px; color: ${mod.color}; background: ${mod.bg}; border: 1px solid ${mod.color}33;">${mod.label}</span>`;
            const modCell = `<td class="tooltip-target" data-tooltip="${modTip}" style="padding: 4px 6px; cursor:help;">${modBadge}</td>`;
            
            const occText = occupants.length > 0 
                ? `<strong style="color: #2b1810;">${occupants.join(', ')}</strong>` 
                : `<span style="color: #9ca3af;">—</span>`;
            const occCell = `<td class="tooltip-target" data-tooltip="${occTip}" style="padding: 4px 6px; font-size: 11.5px; cursor:help;">${occText}</td>`;

            const aspSignsText = aspects.join(', ');
            const aspCell = `<td class="tooltip-target" data-tooltip="${aspTip}" style="padding: 4px 6px; font-size: 11.5px; color: #4b5563; cursor:help;">${aspSignsText}</td>`;

            const aspPlanetsText = aspectedPlanets.length > 0
                ? `<strong style="color: #1e3a8a;">${aspectedPlanets.join(', ')}</strong>`
                : `<span style="color: #9ca3af;">—</span>`;
            const aspPlanetsCell = `<td class="tooltip-target" data-tooltip="${aspPlanetsTip}" style="padding: 4px 6px; font-size: 11.5px; cursor:help;">${aspPlanetsText}</td>`;

            tr.innerHTML = signCell + modCell + occCell + aspCell + aspPlanetsCell;
            tbody.appendChild(tr);
        });
    }

    if (window.widgetRegistry) {
        window.widgetRegistry.register('rashi-drishti', {
            id: 'rashi-drishti',
            title: 'Rāśi Dṛṣṭi (Sign Aspects)',
            icon: '👁️',
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
