/**
 * Astra Nakshatra Foundation Report Widget (static/js/widgets/report_widget.js)
 * Clean, streamlined implementation matching the notebook assessment structure:
 * 1. Ascendant & Moon Nakshatras Side-by-Side Descriptive Dossiers (No Automated Synthesis)
 * 2. Nakshatra Dominance Leaderboard (Prominence-scaled empirical occupancy)
 * 3. Balance of Nakshatra Types (6-Class Model evaluated against 16.7% baseline)
 */

function escapeHtml(str) {
    if (!str) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

function renderAscMoonDossierCard(dossier, isMoon = false) {
    if (!dossier) return '';

    const roleTitle = isMoon 
        ? "Moon (Perception / Manas)" 
        : "Ascendant (Action / Ahaṃkāra)";
    const accentColor = isMoon ? "#7c3aed" : "#2563eb";
    const badgeBg = isMoon ? "#f5f3ff" : "#eff6ff";
    const badgeBorder = isMoon ? "#ddd6fe" : "#bfdbfe";

    const keywordsHtml = (dossier.keywords || []).map(kw => `
        <span class="micro-tag" style="display:inline-block; font-size:12px; font-weight:600; padding:2px 8px; border-radius:4px; background:#f1f5f9; color:#334155; border:1px solid #cbd5e1; margin:2px 4px 2px 0;">
            ${escapeHtml(kw)}
        </span>
    `).join('');

    return `
        <div class="nakshatra-dossier-card" style="background:#ffffff; border:1px solid #e2e8f0; border-left:4px solid ${accentColor}; border-radius:8px; padding:16px; display:flex; flex-direction:column; gap:12px; box-shadow:0 1px 3px rgba(0,0,0,0.02);">
            <!-- Header -->
            <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:8px;">
                <div>
                    <span style="font-size:12px; font-weight:700; text-transform:uppercase; letter-spacing:0.5px; padding:2px 8px; border-radius:4px; background:${badgeBg}; color:${accentColor}; border:1px solid ${badgeBorder}; display:inline-block;">
                        ${roleTitle}
                    </span>
                    <div style="font-size:18px; font-weight:800; color:#0f172a; margin-top:6px; letter-spacing:-0.2px;">
                        ${escapeHtml(dossier.name)} <span style="font-size:13px; font-weight:600; color:#64748b;">(Pada ${dossier.pada})</span>
                    </div>
                </div>
                <span style="font-size:12px; font-weight:700; padding:3px 8px; border-radius:4px; background:#f8fafc; color:#475569; border:1px solid #e2e8f0;">
                    ${escapeHtml(dossier.group_label || dossier.group)}
                </span>
            </div>

            <!-- Key Archetypal Properties Grid -->
            <div style="background:#f8fafc; border:1px solid #edf2f7; border-radius:6px; padding:12px; display:flex; flex-direction:column; gap:6px; font-size:12.5px;">
                <div>
                    <strong style="color:#475569;">Meaning:</strong> 
                    <span style="color:#0f172a;">${escapeHtml(dossier.sanskrit_meaning || '--')}</span>
                </div>
                <div>
                    <strong style="color:#475569;">Deity:</strong> 
                    <span style="color:#0f172a;">${escapeHtml(dossier.deity || '--')}</span>
                </div>
                <div>
                    <strong style="color:#475569;">Symbol:</strong> 
                    <span style="color:#0f172a;">${escapeHtml(dossier.symbol || '--')}</span>
                </div>
                <div>
                    <strong style="color:#475569;">Class:</strong> 
                    <span style="color:#0f172a;">${escapeHtml(dossier.group_label || dossier.group)}</span>
                    <span style="color:#64748b; margin-left:4px;">(${escapeHtml(dossier.group_nature || '')})</span>
                </div>
            </div>

            <!-- Keywords -->
            ${keywordsHtml ? `
                <div>
                    <div style="font-size:12px; font-weight:700; color:#475569; margin-bottom:4px; text-transform:uppercase; letter-spacing:0.4px;">Keywords</div>
                    <div style="display:flex; flex-wrap:wrap; gap:4px;">
                        ${keywordsHtml}
                    </div>
                </div>
            ` : ''}

            <!-- Core Description -->
            <div>
                <div style="font-size:12px; font-weight:700; color:#475569; margin-bottom:4px; text-transform:uppercase; letter-spacing:0.4px;">Core Archetype &amp; Lore</div>
                <div style="font-size:13px; color:#1e293b; line-height:1.55;">
                    ${escapeHtml(dossier.description || '--')}
                </div>
            </div>
        </div>
    `;
}

function renderDominanceLeaderboard(nakDominance) {
    const leaderboard = (nakDominance && nakDominance.leaderboard) || [];
    if (!leaderboard.length) {
        return '<div style="padding:16px; text-align:center; color:#64748b; font-size:13px;">No occupied nakshatras found.</div>';
    }

    let rowsHtml = leaderboard.map(item => {
        const occList = (item.occupants || []).map(occ => {
            return `<strong>${escapeHtml(occ.entity)}</strong> (P${occ.pada}) [${occ.weight} pts]`;
        }).join(', ');

        const isRank1 = item.rank === 1;
        const rowBg = isRank1 ? "background:#fffdf5;" : "";
        const rankDisplay = isRank1 ? `<strong>#1 ★</strong>` : `#${item.rank}`;

        return `
            <tr style="border-bottom:1px solid #f1f5f9; ${rowBg}">
                <td style="padding:8px 10px; font-weight:700; color:${isRank1 ? '#b45309' : '#64748b'}; text-align:center; font-size:12.5px;">${rankDisplay}</td>
                <td style="padding:8px 10px; font-weight:700; color:#0f172a; font-size:13px;">${escapeHtml(item.nakshatra)}</td>
                <td style="padding:8px 10px; color:#475569; font-size:12.5px;">${escapeHtml(item.group || '--')}</td>
                <td style="padding:8px 10px; color:#334155; font-size:12.5px;">${occList || '--'}</td>
                <td style="padding:8px 10px; font-weight:700; color:#0f172a; text-align:right; font-variant-numeric:tabular-nums; font-size:13px;">${item.total_points.toFixed(2)}</td>
                <td style="padding:8px 10px; font-weight:700; color:#0284c7; text-align:right; font-variant-numeric:tabular-nums; font-size:13px;">${item.dominance_pct.toFixed(1)}%</td>
            </tr>
        `;
    }).join('');

    return `
        <table style="width:100%; border-collapse:collapse; text-align:left; font-size:12.5px;">
            <thead>
                <tr style="border-bottom:2px solid #e2e8f0; background:#f8fafc; color:#475569; font-size:12px; text-transform:uppercase; letter-spacing:0.5px;">
                    <th style="padding:8px 10px; text-align:center; width:50px;">Rank</th>
                    <th style="padding:8px 10px; min-width:130px;">Nakshatra</th>
                    <th style="padding:8px 10px; min-width:90px;">Class</th>
                    <th style="padding:8px 10px;">Occupants (Grahas &amp; Padas)</th>
                    <th style="padding:8px 10px; text-align:right; width:80px;">Points</th>
                    <th style="padding:8px 10px; text-align:right; width:80px;">Share (%)</th>
                </tr>
            </thead>
            <tbody>
                ${rowsHtml}
            </tbody>
        </table>
    `;
}

function renderTemperamentBreakdown(balanceData) {
    const breakdown = (balanceData && balanceData.temperament_breakdown) || [];
    if (!breakdown.length) {
        return '<div style="padding:16px; text-align:center; color:#64748b; font-size:13px;">No temperament breakdown data.</div>';
    }

    const rowsHtml = breakdown.map(item => {
        const pct = item.percentage || 0;
        const diff = pct - 16.7;
        const diffSign = diff > 0 ? `+${diff.toFixed(1)}%` : `${diff.toFixed(1)}%`;
        
        let badgeHtml = '';
        let barColor = item.color || '#3b82f6';
        if (pct > 18.7) {
            badgeHtml = `<span style="font-size:12px; font-weight:700; padding:2px 8px; border-radius:4px; background:#dcfce7; color:#16a34a; border:1px solid #bbf7d0; white-space:nowrap;">Surplus (${diffSign})</span>`;
            barColor = '#16a34a';
        } else if (pct < 14.7) {
            badgeHtml = `<span style="font-size:12px; font-weight:700; padding:2px 8px; border-radius:4px; background:#fee2e2; color:#dc2626; border:1px solid #fecaca; white-space:nowrap;">Deficit (${diffSign})</span>`;
            barColor = '#dc2626';
        } else {
            badgeHtml = `<span style="font-size:12px; font-weight:600; padding:2px 8px; border-radius:4px; background:#f1f5f9; color:#64748b; border:1px solid #cbd5e1; white-space:nowrap;">Balanced</span>`;
            barColor = '#64748b';
        }

        const barWidth = Math.min(100, Math.max(0, pct));

        return `
            <tr class="temperament-row" data-group="${escapeHtml(item.group)}" onclick="selectTemperamentClass('${escapeHtml(item.group)}')" style="border-bottom:1px solid #f1f5f9; cursor:pointer; transition:background 0.15s ease;">
                <!-- 1. Class Name & Sanskrit -->
                <td style="padding:10px; min-width:160px;">
                    <div style="font-weight:700; color:#0f172a; font-size:13px;">${escapeHtml(item.display_name)}</div>
                    <div style="font-size:12px; color:#64748b;">${escapeHtml(item.sanskrit)}</div>
                </td>
                <!-- 2. Nature -->
                <td style="padding:10px; color:#334155; font-size:12.5px; min-width:200px;">
                    ${escapeHtml(item.nature || '--')}
                </td>
                <!-- 3. Percentage Bar -->
                <td style="padding:10px; min-width:180px;">
                    <div style="display:flex; align-items:center; gap:10px;">
                        <div style="position:relative; flex:1; height:12px; background:#e2e8f0; border-radius:6px; overflow:hidden;" title="16.7% Baseline Indicator">
                            <!-- Filled bar -->
                            <div style="width:${barWidth}%; height:100%; background:${barColor}; border-radius:6px; transition:width 0.3s ease;"></div>
                            <!-- 16.7% vertical baseline marker -->
                            <div style="position:absolute; left:16.7%; top:0; bottom:0; width:2px; background:#0f172a; z-index:2;" title="Uniform Baseline: 16.7%"></div>
                        </div>
                        <span style="font-size:12.5px; font-weight:700; color:#0f172a; font-variant-numeric:tabular-nums; min-width:44px; text-align:right;">
                            ${pct.toFixed(1)}%
                        </span>
                    </div>
                </td>
                <!-- 4. Status Badge -->
                <td style="padding:10px; text-align:right; width:130px;">
                    ${badgeHtml}
                </td>
            </tr>
        `;
    }).join('');

    return `
        <table style="width:100%; border-collapse:collapse; text-align:left; font-size:12.5px;">
            <thead>
                <tr style="border-bottom:2px solid #e2e8f0; background:#f8fafc; color:#475569; font-size:12px; text-transform:uppercase; letter-spacing:0.5px;">
                    <th style="padding:8px 10px;">Class &amp; Sanskrit</th>
                    <th style="padding:8px 10px;">Nature</th>
                    <th style="padding:8px 10px;">Relative Share (vs 16.7% Benchmark)</th>
                    <th style="padding:8px 10px; text-align:right;">Status</th>
                </tr>
            </thead>
            <tbody>
                ${rowsHtml}
            </tbody>
        </table>
    `;
}

function selectTemperamentClass(group) {
    if (!group) return;
    const containers = document.querySelectorAll('.widget-synthesis-report, #widgetMaximizeModal');
    containers.forEach(cnt => {
        const drawer = cnt.querySelector('.temperament-dossier-drawer');
        if (!drawer) return;
        const current = drawer.dataset.activeGroup;
        if (current === group && drawer.style.display !== 'none') {
            drawer.style.display = 'none';
            drawer.dataset.activeGroup = '';
            return;
        }
        drawer.dataset.activeGroup = group;
        drawer.style.display = 'block';

        const tb = cnt._temperamentBreakdown || [];
        const item = tb.find(t => t.group === group);
        const dossier = (item && item.dossier) || {};
        const stars = (dossier.nakshatras || []).join(', ');
        const positives = (dossier.positives || []).map(p => `<li style="margin-bottom:3px;">${escapeHtml(p)}</li>`).join('');
        const negatives = (dossier.negatives || []).map(n => `<li style="margin-bottom:3px;">${escapeHtml(n)}</li>`).join('');

        drawer.innerHTML = `
            <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:6px; padding:12px; font-size:12.5px;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                    <div style="font-size:13.5px; font-weight:700; color:#0f172a;">
                        ${escapeHtml(item ? item.display_name : group)} Archetype Details
                    </div>
                    <button type="button" onclick="this.closest('.temperament-dossier-drawer').style.display='none'" style="background:transparent; border:none; color:#64748b; font-size:14px; cursor:pointer;" title="Close">✕</button>
                </div>
                <div style="margin-bottom:8px; color:#475569;">
                    <strong>Member Nakshatras:</strong> ${escapeHtml(stars || '--')}
                </div>
                <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(240px, 1fr)); gap:12px; margin-top:8px;">
                    <div style="background:#f0fdf4; border:1px solid #bbf7d0; border-radius:6px; padding:10px;">
                        <div style="font-weight:700; color:#15803d; margin-bottom:4px;">Constructive Potentials (Positives)</div>
                        <ul style="margin:0; padding-left:18px; color:#166534; font-size:12px;">
                            ${positives || '<li>--</li>'}
                        </ul>
                    </div>
                    <div style="background:#fef2f2; border:1px solid #fecaca; border-radius:6px; padding:10px;">
                        <div style="font-weight:700; color:#b91c1c; margin-bottom:4px;">Developmental Pitfalls (Negatives)</div>
                        <ul style="margin:0; padding-left:18px; color:#991b1b; font-size:12px;">
                            ${negatives || '<li>--</li>'}
                        </ul>
                    </div>
                </div>
            </div>
        `;
    });
}

function updateReportWidget(container, chartData) {
    const currentData = chartData || window.currentChartData;
    if (!currentData) return;

    const report = currentData.report;
    const body = container.querySelector('.report-body');
    if (!report) {
        if (body) {
            body.innerHTML = '<div style="padding:20px; text-align:center; color:#888; font-size:13.5px;">Calculating report data...</div>';
        }
        return;
    }

    const ascMoon = report.ascendant_and_moon || {};
    const nakDominance = report.nakshatra_dominance || {};
    const balanceTypes = report.balance_of_nakshatra_types || {};

    // 0. Update Toolbar Dominant Badge
    const domBadge = container.querySelector('.report-dominant-badge');
    if (domBadge && nakDominance.dominant_nakshatra) {
        const dNak = nakDominance.dominant_nakshatra.nakshatra;
        const dPct = nakDominance.dominant_nakshatra.dominance_pct;
        const dTemp = (balanceTypes.dominant_temperament && balanceTypes.dominant_temperament.label) 
            ? balanceTypes.dominant_temperament.label.split(' ')[0] 
            : '';
        domBadge.textContent = `★ Dominant: ${dNak} (${dPct}%) • ${dTemp}`;
    }

    // 1. Section 1: Ascendant & Moon Nakshatras Side-by-Side
    const grid = container.querySelector('.asc-moon-grid');
    if (grid) {
        grid.innerHTML = `
            ${renderAscMoonDossierCard(ascMoon.ascendant, false)}
            ${renderAscMoonDossierCard(ascMoon.moon, true)}
        `;
    }

    // 2. Section 2: Dominance Leaderboard
    const tableWrap = container.querySelector('.dominance-table-wrapper');
    if (tableWrap) {
        tableWrap.innerHTML = renderDominanceLeaderboard(nakDominance);
    }
    const totalPtsEl = container.querySelector('.report-total-points');
    if (totalPtsEl && nakDominance.total_points !== undefined) {
        totalPtsEl.textContent = `Total Points: ${nakDominance.total_points.toFixed(2)}`;
    }

    // 3. Section 3: Balance of Nakshatra Types
    const tempWrap = container.querySelector('.temperament-breakdown-wrapper');
    if (tempWrap) {
        container._temperamentBreakdown = balanceTypes.temperament_breakdown || [];
        tempWrap.innerHTML = renderTemperamentBreakdown(balanceTypes);
    }
    const footnoteEl = container.querySelector('.temperament-footnote');
    if (footnoteEl) {
        const catalysts = balanceTypes.universal_catalysts || [];
        if (catalysts.length > 0) {
            footnoteEl.textContent = `Universal Catalyst: Placements in Krittika or Vishakha (${catalysts.join(', ')}) distribute points equally across all 6 classes.`;
            footnoteEl.style.display = 'block';
        } else {
            footnoteEl.style.display = 'none';
        }
    }
}

function openFloatingReport() {
    if (typeof closeKalaMenu === 'function') closeKalaMenu();
    const modal = document.getElementById('widgetMaximizeModal');
    const card = document.getElementById('widgetMaximizeCard');
    const titleEl = document.getElementById('widgetMaximizeModalTitle');
    const container = document.getElementById('widgetMaximizeContainer');
    if (!modal || !titleEl || !container || !window.currentChartData) return;

    if (typeof resetFloatingWindowPosition === 'function') resetFloatingWindowPosition();
    if (card) {
        const w = Math.min(1380, window.innerWidth - 40);
        const h = Math.min(840, window.innerHeight - 60);
        card.style.width = w + 'px';
        card.style.height = h + 'px';
        card.style.left = Math.max(20, Math.round((window.innerWidth - w) / 2)) + 'px';
        card.style.top = Math.max(30, Math.round((window.innerHeight - h) / 2)) + 'px';
    }

    const subjectName = (window.currentChartData.subject_info && window.currentChartData.subject_info.name) 
        ? window.currentChartData.subject_info.name 
        : 'Chart';
    titleEl.textContent = subjectName + " — Nakshatra Foundation Report";

    const tmpl = document.getElementById('tmpl-report');
    if (tmpl) {
        container.innerHTML = '';
        container.appendChild(tmpl.content.cloneNode(true));
        updateReportWidget(container, window.currentChartData);
    }

    modal.style.display = 'block';
    modal.classList.add('active');
}

// Pluggable Widget Registration
if (typeof window !== 'undefined' && window.widgetRegistry) {
    window.widgetRegistry.register('report', {
        id: 'report',
        title: 'Nakshatra Foundation Report',
        icon: '',
        category: 'Diagnostics',
        templateId: 'tmpl-report',
        isScrollable: true,
        render: function(container, chartData, options) {
            const tmpl = document.getElementById('tmpl-report');
            if (tmpl) {
                container.innerHTML = '';
                container.appendChild(tmpl.content.cloneNode(true));
                updateReportWidget(container, chartData);
            }
        },
        onUpdate: function(cell, chartData) {
            updateReportWidget(cell, chartData);
        }
    });

    window.openFloatingReport = openFloatingReport;
    window.updateReportWidget = updateReportWidget;
    window.selectTemperamentClass = selectTemperamentClass;
    window.selectTemperamentDossier = selectTemperamentClass;
}
