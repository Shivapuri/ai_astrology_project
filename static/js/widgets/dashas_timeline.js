/**
 * Astra Vimshottari Dasha Timeline Widget
 * 
 * Renders hierarchical 120-year Vimshottari Mahadashas and Antardashas
 * with active timeline indicator and accordion view.
 */

(function() {
    function updateDashaTimelineWidget(cell, chartData) {
        const currentData = chartData || window.currentChartData;
        const tbody = cell.querySelector('tbody');
        if (!tbody || !currentData || !currentData.vimshottari_dasha) return;
        tbody.innerHTML = '';

        const dashaData = currentData.vimshottari_dasha;
        const mds = dashaData.mahadashas || [];
        const now = new Date();

        mds.forEach((md, mdIdx) => {
            const startDate = new Date(md.start);
            const endDate = new Date(md.end);
            const isCurrentMD = (now >= startDate && now <= endDate);

            // Mahadasha Master Row (Clickable accordion)
            const trMD = document.createElement('tr');
            trMD.className = 'md-row tooltip-target' + (isCurrentMD ? ' active-dasa-row' : '');
            trMD.style.cursor = 'pointer';
            trMD.style.backgroundColor = isCurrentMD ? 'var(--bg-surface-hover)' : 'var(--bg-surface-muted)';
            trMD.setAttribute('data-tooltip', `<strong>${md.planet} Mahādaśā (${md.years || ''} Years)</strong><br>• <strong>Period:</strong> ${md.start} to ${md.end}<br>• <strong>Role:</strong> Major life chapter governed by ${md.planet}. Click to expand/collapse Antardashas.`);

            const currentBadge = isCurrentMD ? '<span class="badge badge-benefic" style="margin-left:6px;">ACTIVE</span>' : '';
            const arrow = isCurrentMD ? '▼ ' : '▶ ';

            trMD.innerHTML = `
                <td><strong>${arrow}${md.planet} (${md.years || ''} yrs)</strong></td>
                <td><strong>${md.start}</strong></td>
                <td><strong>${md.end}</strong></td>
                <td>${currentBadge}</td>
            `;

            tbody.appendChild(trMD);

            // Nested Container for Antardashas
            const antardashas = md.antardashas || [];
            antardashas.forEach(ad => {
                const adStart = new Date(ad.start_date || ad.start);
                const adEnd = new Date(ad.end_date || ad.end);
                const isCurrentAD = (now >= adStart && now <= adEnd);

                const trAD = document.createElement('tr');
                trAD.className = `ad-subrow md-group-${mdIdx} tooltip-target`;
                trAD.style.display = isCurrentMD ? 'table-row' : 'none';
                trAD.style.backgroundColor = isCurrentAD ? 'var(--status-neutral-bg)' : 'var(--bg-surface)';
                trAD.setAttribute('data-tooltip', `<strong>${ad.period || ad.antardasha_lord} Antardaśā</strong><br>• <strong>Sub-period:</strong> ${ad.start_date || ad.start} to ${ad.end_date || ad.end}<br>• <strong>Influence:</strong> Secondary timing window delivering specific events through ${md.planet} and sub-lord.`);

                const adBadge = isCurrentAD ? '<span class="badge badge-neutral" style="font-size:9px;">CURRENT</span>' : '';

                trAD.innerHTML = `
                    <td style="padding-left: 24px; color: var(--text-heading);">${ad.period || ad.antardasha_lord}</td>
                    <td>${ad.start_date || ad.start} ${ad.start_time || ''}</td>
                    <td>${ad.end_date || ad.end || ''}</td>
                    <td>${adBadge}</td>
                `;
                tbody.appendChild(trAD);
            });

            // Click event to toggle accordion
            trMD.addEventListener('click', () => {
                const subRows = tbody.querySelectorAll(`.md-group-${mdIdx}`);
                const isHidden = subRows[0] && subRows[0].style.display === 'none';
                subRows.forEach(r => r.style.display = isHidden ? 'table-row' : 'none');
                trMD.querySelector('td strong').textContent = (isHidden ? '▼ ' : '▶ ') + `${md.planet} (${md.years || ''} yrs)`;
            });
        });
    }

    if (window.widgetRegistry) {
        window.widgetRegistry.register('dashas-timeline', {
            id: 'dashas-timeline',
            title: 'Daśā Timeline',
            icon: '⏳',
            category: 'Strengths',
            onUpdate: function(cell, chartData) {
                updateDashaTimelineWidget(cell, chartData);
            }
        });
    }

    window.updateDashaTimelineWidget = updateDashaTimelineWidget;
})();
