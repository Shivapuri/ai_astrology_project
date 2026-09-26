/**
 * Astra Classical Yogas & Breakers Widget
 * 
 * Evaluates and displays classical Parashara and Mantreshwara planetary combinations,
 * including Yoga status (Pure, Stained, Rescued, Broken) and breaker penalties.
 */

(function() {
    function updateClassicalYogasWidget(cell, chartData) {
        const currentData = chartData || window.currentChartData;
        let target = cell;
        if (!target) {
            target = document.querySelector('.grid-cell[data-widget="classical-yogas"]') ||
                     document.getElementById('widgetMaximizeContainer') ||
                     document.getElementById('widget-classical-yogas');
        }
        if (!target || !currentData || !currentData.yogas) return;
        populateClassicalYogasTable(target, currentData);
    }

    function populateClassicalYogasTable(container, chartData) {
        const currentData = chartData || window.currentChartData;
        const targetEl = container.querySelector('#widget-classical-yogas') || container;
        const tbody = targetEl.querySelector('tbody');
        if (!tbody || !currentData || !currentData.yogas) return;

        const yogasData = currentData.yogas;
        const allYogas = yogasData.yogas || [];
        const summary = yogasData.summary || { pure: 0, stained: 0, rescued: 0, broken: 0 };

        const summaryContainer = targetEl.querySelector('.yoga-summary-badges');
        if (summaryContainer) {
            summaryContainer.innerHTML = `
                <span class="badge badge-yoga-pure" style="font-size:10px; padding:2px 6px;">Pure: ${summary.pure || 0}</span>
                <span class="badge badge-yoga-stained" style="font-size:10px; padding:2px 6px;">Stained: ${summary.stained || 0}</span>
                <span class="badge badge-yoga-rescued" style="font-size:10px; padding:2px 6px;">Rescued: ${summary.rescued || 0}</span>
                <span class="badge badge-yoga-broken" style="font-size:10px; padding:2px 6px;">Broken: ${summary.broken || 0}</span>
            `;
        }

        const catSelect = targetEl.querySelector('.yoga-category-filter');
        const statusSelect = targetEl.querySelector('.yoga-status-filter');
        const catFilter = catSelect ? catSelect.value : 'all';
        const statusFilter = statusSelect ? statusSelect.value : 'all';

        tbody.innerHTML = '';

        const filtered = allYogas.filter(y => {
            if (catFilter !== 'all' && y.category !== catFilter) return false;
            if (statusFilter !== 'all') {
                if (statusFilter === 'Pure' && !y.status.includes('Pure')) return false;
                if (statusFilter === 'Stained' && !y.status.includes('Stained')) return false;
                if (statusFilter === 'Rescued' && !y.status.includes('Rescued')) return false;
                if (statusFilter === 'Broken' && !y.status.includes('Broken')) return false;
            }
            return true;
        });

        if (filtered.length === 0) {
            tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; padding:20px; color:#78716c; font-style:italic;">No yogas match the selected filter criteria.</td></tr>`;
            return;
        }

        filtered.forEach(y => {
            const tr = document.createElement('tr');
            
            let statusBadgeClass = 'badge-yoga-pure';
            let barColor = '#16a34a';
            if (y.status.includes('Stained')) {
                statusBadgeClass = 'badge-yoga-stained';
                barColor = '#d97706';
            } else if (y.status.includes('Rescued')) {
                statusBadgeClass = 'badge-yoga-rescued';
                barColor = '#4f46e5';
            } else if (y.status.includes('Broken')) {
                statusBadgeClass = 'badge-yoga-broken';
                barColor = '#dc2626';
            }

            const planetsHtml = (y.participating_planets || []).map(p => `<span class="planet-badge" style="display:inline-flex; align-items:center; gap:2px; font-weight:600; color:#4a3325; background:#f7f2ea; border:1px solid #e5dccb; border-radius:3px; padding:1px 4px; margin:1px;">${p}</span>`).join(' ');
            const housesStr = (y.participating_houses || []).filter(h => h > 0).map(h => `H${h}`).join(', ') || '-';

            let breakersHtml = '<span style="color:#16a34a; font-weight:600; font-size:11px;">✓ Pristine (No Breakers)</span>';
            if (y.breakers && y.breakers.length > 0) {
                breakersHtml = y.breakers.map(b => `
                    <div style="background:#fff1f2; border:1px solid #fecdd3; border-radius:4px; padding:3px 6px; margin-bottom:3px; font-size:10.5px;">
                        <div style="font-weight:700; color:#991b1b;">⚠️ ${b.factor} (-${Math.round(b.penalty)}%)</div>
                        <div style="color:#475569; font-size:10px;">${b.description}</div>
                    </div>
                `).join('');
            }

            let positiveHtml = '';
            if (y.positive_factors && y.positive_factors.length > 0) {
                positiveHtml = y.positive_factors.slice(0, 2).map(pf => `
                    <div style="color:#166534; font-size:10px; margin-top:2px;">✓ ${pf}</div>
                `).join('');
            }

            const effectsStr = (y.manifestation_effects || []).join(' ') || '';

            tr.innerHTML = `
                <td style="vertical-align:top;">
                    <div style="font-weight:700; color:#4a3325; font-size:12px;">${y.name}</div>
                    <div style="font-size:10.5px; color:#78716c; margin-top:2px;">${y.category}</div>
                    <div style="font-size:9.5px; color:#b45309; margin-top:1px;">📜 ${y.scripture_ref || ''}</div>
                </td>
                <td style="vertical-align:top;">
                    <span class="badge ${statusBadgeClass}" style="display:inline-block; font-size:10.5px; font-weight:700; padding:2px 7px; border-radius:4px; white-space:nowrap;">${y.status}</span>
                </td>
                <td style="vertical-align:top;">
                    <div style="display:flex; align-items:center; gap:6px;">
                        <div style="flex:1; height:8px; background:#e2e8f0; border-radius:4px; overflow:hidden; min-width:45px;">
                            <div style="width:${y.plausibility_score}%; height:100%; background:${barColor}; border-radius:4px;"></div>
                        </div>
                        <span style="font-weight:700; font-size:11.5px; color:${barColor}; font-family:monospace;">${y.plausibility_score}%</span>
                    </div>
                </td>
                <td style="vertical-align:top;">
                    <div>${planetsHtml}</div>
                    <div style="font-size:10px; color:#64748b; margin-top:3px;"><strong>Houses:</strong> ${housesStr}</div>
                </td>
                <td style="vertical-align:top;">
                    <div style="font-weight:600; color:#1e293b; font-size:11.5px; margin-bottom:3px;">${y.archetype || ''}</div>
                    <div style="color:#475569; font-size:11px; line-height:1.35;">${effectsStr}</div>
                    ${positiveHtml}
                </td>
                <td style="vertical-align:top;">
                    ${breakersHtml}
                </td>
            `;
            tbody.appendChild(tr);
        });
    }

    function filterClassicalYogas(el) {
        const container = el.closest('.grid-cell') || el.closest('#widgetMaximizeModal') || el.closest('#widget-classical-yogas');
        if (container) {
            populateClassicalYogasTable(container);
        }
    }

    function openFloatingClassicalYogas() {
        if (typeof closeKalaMenu === 'function') closeKalaMenu();
        const modal = document.getElementById('widgetMaximizeModal');
        const titleEl = document.getElementById('widgetMaximizeModalTitle');
        const container = document.getElementById('widgetMaximizeContainer');
        const currentData = window.currentChartData;
        if (!modal || !titleEl || !container || !currentData) return;

        if (typeof setActiveFloatingNav === 'function') setActiveFloatingNav('nav-btn-classical-yogas');
        const name = currentData.subject_info ? currentData.subject_info.name : 'Chart';
        titleEl.textContent = name + " — Classical Astrological Yogas & Breakers (Parashara & Mantreshwara)";

        const tmpl = document.getElementById('tmpl-classical-yogas');
        if (tmpl) {
            container.innerHTML = '';
            container.appendChild(tmpl.content.cloneNode(true));
            populateClassicalYogasTable(container, currentData);
        }

        modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
    }

    if (window.widgetRegistry) {
        window.widgetRegistry.register('classical-yogas', {
            id: 'classical-yogas',
            title: 'Classical Yogas & Breakers',
            icon: '👑',
            category: 'Yogas',
            isScrollable: true,
            render: function(container, chartData, options) {
                updateClassicalYogasWidget(container, chartData);
            },
            onUpdate: function(cell, chartData) {
                updateClassicalYogasWidget(cell, chartData);
            }
        });
    }

    window.updateClassicalYogasWidget = updateClassicalYogasWidget;
    window.populateClassicalYogasTable = populateClassicalYogasTable;
    window.filterClassicalYogas = filterClassicalYogas;
    window.openFloatingClassicalYogas = openFloatingClassicalYogas;
})();
