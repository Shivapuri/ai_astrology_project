/**
 * Astra Varga Vimshopaka Widget
 * 
 * Computes and displays the 20-point Vimshopaka dignity scale
 * across Shadvarga (6), Saptavarga (7), Dasavarga (10), and Shodashavarga (16),
 * along with Vaisheshikamsa honorific dignity titles.
 */

(function() {
    function updateVimshopakaWidget(cell, chartData) {
        if (!cell) {
            cell = document.getElementById('widgetMaximizeContainer') || document.querySelector('.grid-cell[data-widget="vimshopaka"]');
        }
        if (!cell) return;
        const currentData = chartData || window.currentChartData;
        const tbody = cell.querySelector('tbody');
        if (!tbody || !currentData) return;
        const vData = currentData.vimshopaka || currentData.varga_vimshopaka;
        if (!vData) return;
        tbody.innerHTML = '';

        const planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"];
        const schemes = [
            { key: "shadvarga", altKey: "Shadvarga", label: "Shadvarga (6 Charts)" },
            { key: "saptavarga", altKey: "Saptavarga", label: "Saptavarga (7 Charts)" },
            { key: "dasavarga", altKey: "Dasavarga", label: "Dasavarga (10 Charts)" },
            { key: "shodashavarga", altKey: "Shodasavarga", label: "Shodashavarga (16 Charts)" }
        ];

        const scores = vData.scores || vData;

        schemes.forEach(sc => {
            const scMap = vData[sc.key] || scores[sc.key] || scores[sc.altKey] || vData[sc.altKey] || {};
            const tr = document.createElement('tr');
            const scTip = `<strong>${sc.label}</strong><br>Evaluates planetary dignity across divisional harmonics on a 20-point scale (20 = maximum dignity).`;
            let html = `<td class="tooltip-target" data-tooltip="${scTip}" style="text-align: left; cursor:help;"><strong>${sc.label}</strong></td>`;

            planets.forEach(p => {
                const rawVal = scMap[p];
                const val = rawVal !== undefined ? Number(rawVal).toFixed(1) : '-';
                const numVal = Number(val);
                const color = (val !== '-' && numVal >= 15) ? '#15803d' : ((val !== '-' && numVal < 10) ? '#b91c1c' : '#334155');
                let pTip = '';
                if (val !== '-') {
                    let quality = numVal >= 15 ? 'Ati-Pūrṇa (Excellent, 15-20). Highly dignified and noble across subtle divisions.' :
                                  (numVal >= 10 ? 'Madhyama (Good / Moderate, 10-15). Capable, stable, and supportive.' :
                                  'Alpa (Weak, <10). Strained dignity in divisional harmonics.');
                    pTip = `<strong>${p} — ${sc.label}: ${val} / 20</strong><br>• <strong>Grade:</strong> ${quality}<br>• <strong>Systematic:</strong> Weighted composite score based on whether the planet occupies friendly, own, or exaltation signs in each chart of this group.`;
                }
                html += `<td class="tooltip-target" data-tooltip="${pTip}" style="color:${color}; font-weight:bold; cursor:help;">${val}</td>`;
            });

            tr.innerHTML = html;
            tbody.appendChild(tr);
        });

        // Vaisheshikamsa Honorific Row
        if (vData.vaisheshikamsa) {
            const trHonor = document.createElement('tr');
            trHonor.style.backgroundColor = '#fdf6e2';
            const vTip = `<strong>Vaiśeṣikāṁśa Dignity Titles</strong><br>Honorific titles conferred when a planet occupies favorable dignity (own/exalted/moolatrikona) in multiple divisional charts.`;
            let html = `<td class="tooltip-target" data-tooltip="${vTip}" style="text-align: left; cursor:help;"><strong>Vaisheshikamsa</strong></td>`;

            planets.forEach(p => {
                let title = '-';
                if (typeof vData.vaisheshikamsa[p] === 'string') {
                    title = vData.vaisheshikamsa[p];
                } else if (vData.vaisheshikamsa[p] && vData.vaisheshikamsa[p].honorific) {
                    title = vData.vaisheshikamsa[p].honorific;
                } else if (vData.vaisheshikamsa.Shodasavarga && vData.vaisheshikamsa.Shodasavarga[p]) {
                    title = vData.vaisheshikamsa.Shodasavarga[p].honorific || '-';
                }
                const honorTip = `<strong>${p} — Vaiśeṣikāṁśa Title: ${title}</strong><br>Conferred for exceptional dignity across multiple harmonic divisions. Bestows royal honor, lasting respect, and distinct capability.`;
                html += `<td class="tooltip-target" data-tooltip="${honorTip}" style="cursor:help;"><span class="badge" style="background:#e0f2fe; color:#0369a1; border:1px solid #bae6fd; font-size:8px;">${title}</span></td>`;
            });

            trHonor.innerHTML = html;
            tbody.appendChild(trHonor);
        }
    }

    if (window.widgetRegistry) {
        window.widgetRegistry.register('vimshopaka', {
            id: 'vimshopaka',
            title: 'Varga Vimshopaka (20pt)',
            icon: '⭐',
            category: 'Strengths',
            render: function(container, chartData, options) {
                updateVimshopakaWidget(container, chartData);
            },
            onUpdate: function(cell, chartData) {
                updateVimshopakaWidget(cell, chartData);
            }
        });
    }

    window.updateVimshopakaWidget = updateVimshopakaWidget;
})();
