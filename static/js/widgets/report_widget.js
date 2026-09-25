/**
 * Astra Astrological Synthesis Report Widget (report_widget.js)
 * 
 * Provides an interactive Master Ingredients Desk for astrological synthesis:
 * 1. Polarity Core (Ascendant Nakshatra ⟷ Moon Nakshatra with Panchadha Maitri & Tattvas)
 * 2. Canonical 4-Step Nakshatra Dominance & 7-Temperament Distribution
 * 3. Operational Axis (Rising Rashi ⟷ Rising Navamsha Pada with Vargottama check)
 * 4. Macro Environmental Tallies (Elements, Gunas, Rising Mode, Ayurvedic Doshas)
 * 5. Planetary Prominence & Dignity Leaderboard (Highlighting #1 Chart Commander)
 * 6. Synthesis Desk (Aggregated ingredients checklist)
 * 
 * Strictly adheres to Astra's Pergamon warm parchment theme and >= 12px font floor.
 */

function switchReportTab(btn, tabId) {
    const widget = btn.closest('.widget-synthesis-report') || document.getElementById('widgetMaximizeModal');
    if (!widget) return;

    // Update buttons
    widget.querySelectorAll('.report-pill-btn').forEach(b => {
        b.classList.remove('active');
        b.style.background = 'transparent';
        b.style.color = '#6b5a4b';
    });
    btn.classList.add('active');
    btn.style.background = '#fffdfa';
    btn.style.color = '#4a3325';

    // Update panes
    widget.querySelectorAll('.report-tab-pane').forEach(p => {
        p.style.display = 'none';
        p.classList.remove('active');
    });
    const targetPane = widget.querySelector(`.tab-${tabId}`);
    if (targetPane) {
        targetPane.style.display = 'flex';
        targetPane.classList.add('active');
    }
}

function updateReportWidget(cell, chartData) {
    const currentData = chartData || window.currentChartData;
    if (!currentData) return;

    const report = currentData.report;
    if (!report) {
        const body = cell.querySelector('.report-body');
        if (body) {
            body.innerHTML = '<div style="padding:20px; text-align:center; color:#888; font-size:13.5px;">Calculating report ingredients...</div>';
        }
        return;
    }

    const polarity = report.polarity_core || {};
    const nakDominance = report.nakshatra_dominance || {};
    const operationalAxis = report.operational_axis || {};
    const envTally = report.environmental_tally || {};
    const planetRank = report.planetary_rankings || {};
    const synthesis = report.synthesis_ingredients || {};

    // 0. Update Toolbar Dominant Badge
    const domBadge = cell.querySelector('.report-dominant-badge');
    if (domBadge && nakDominance.dominant_nakshatra) {
        const dNak = nakDominance.dominant_nakshatra.nakshatra;
        const dPct = nakDominance.dominant_nakshatra.dominance_pct;
        const dTemp = nakDominance.dominant_temperament ? nakDominance.dominant_temperament.label.split(' ')[0] : '';
        domBadge.textContent = `★ Dominant: ${dNak} (${dPct}%) • ${dTemp}`;
    }

    // ==========================================
    // TAB 1: POLARITY CORE & STARS
    // ==========================================

    // 1.1 Polarity Relationship Banner
    const polBanner = cell.querySelector('.polarity-banner-container');
    if (polBanner && polarity.relationship) {
        const rel = polarity.relationship;
        let badgeColor = '#15803d';
        let badgeBg = '#f0fdf4';
        let borderColor = '#86efac';

        if (rel.friction_score > 65) {
            badgeColor = '#b91c1c';
            badgeBg = '#fef2f2';
            borderColor = '#fca5a5';
        } else if (rel.friction_score > 35) {
            badgeColor = '#b45309';
            badgeBg = '#fffbeb';
            borderColor = '#fde68a';
        }

        polBanner.innerHTML = `
            <div style="background:${badgeBg}; border:1.5px solid ${borderColor}; border-radius:6px; padding:10px 14px;">
                <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
                    <div style="display:flex; align-items:center; gap:8px;">
                        <span style="font-size:15px; font-weight:700; color:#1e293b;">⚡ Polarity Core: ${rel.state}</span>
                        <span style="font-size:12px; font-weight:700; padding:2px 8px; border-radius:12px; background:${badgeColor}; color:#ffffff;">Friction: ${rel.friction_score}/100</span>
                    </div>
                    <div style="font-size:12.5px; font-weight:600; color:#475569;">
                        Rulers: <strong>${rel.ruler_asc}</strong> vs <strong>${rel.ruler_moon}</strong> (${rel.panchadha_maitri}) • Elements: <strong>${rel.elements}</strong> (${rel.tattva_status})
                    </div>
                </div>
                <div style="font-size:13px; color:#334155; margin-top:6px; line-height:1.45;">
                    ${rel.summary} <em>(${rel.tattva_note})</em>
                </div>
            </div>
        `;
    }

    // 1.2 Ascendant Nakshatra Card (Ahamkara / Action)
    const ascWrapper = cell.querySelector('.asc-nak-card-wrapper');
    if (ascWrapper && polarity.ascendant_nakshatra) {
        const a = polarity.ascendant_nakshatra;
        const lore = a.lore || {};
        ascWrapper.innerHTML = `
            <div style="background:#ffffff; border:1px solid #e2e8f0; border-left:4px solid #2563eb; border-radius:6px; padding:12px; display:flex; flex-direction:column; gap:8px; height:100%;">
                <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                    <div>
                        <div style="font-size:12px; font-weight:700; text-transform:uppercase; color:#2563eb; letter-spacing:0.5px;">🚩 Ascendant Star (Ahaṃkāra / Bodily Action)</div>
                        <div style="font-size:16px; font-weight:800; color:#0f172a; margin-top:2px;">${a.name} <span style="font-size:13px; font-weight:600; color:#64748b;">(Pada ${a.pada} in ${a.sign})</span></div>
                    </div>
                    <span style="font-size:12px; font-weight:700; padding:2px 8px; border-radius:4px; background:#eff6ff; color:#1d4ed8; border:1px solid #bfdbfe;">${a.group} Class</span>
                </div>
                <div style="font-size:12.5px; color:#475569; background:#f8fafc; border-radius:4px; padding:6px 8px;">
                    <div><strong>Star:</strong> ${lore.astronomical_star || '--'} • <strong>Span:</strong> ${lore.zodiacal_span || '--'}</div>
                    <div style="margin-top:2px;"><strong>Deity:</strong> ${lore.presiding_deity || '--'}</div>
                    <div style="margin-top:2px;"><strong>Symbol:</strong> ${lore.symbol_etymology || '--'}</div>
                    <div style="margin-top:2px;"><strong>Lord/Sublord:</strong> ${a.ruler} / ${a.sub_lord}</div>
                </div>
                <div style="font-size:13px; color:#1e293b; line-height:1.45; margin-top:2px;">
                    <strong>Core Action Drive:</strong> ${lore.core_psychology || '--'}
                </div>
                <div style="font-size:12.5px; color:#475569; margin-top:auto; padding-top:6px; border-top:1px dashed #e2e8f0;">
                    <strong>Real-World Spheres:</strong> ${lore.real_world_manifestations || '--'}
                </div>
            </div>
        `;
    }

    // 1.3 Moon Nakshatra Card (Manas / Perception)
    const moonWrapper = cell.querySelector('.moon-nak-card-wrapper');
    if (moonWrapper && polarity.moon_nakshatra) {
        const m = polarity.moon_nakshatra;
        const lore = m.lore || {};
        moonWrapper.innerHTML = `
            <div style="background:#ffffff; border:1px solid #e2e8f0; border-left:4px solid #7c3aed; border-radius:6px; padding:12px; display:flex; flex-direction:column; gap:8px; height:100%;">
                <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                    <div>
                        <div style="font-size:12px; font-weight:700; text-transform:uppercase; color:#7c3aed; letter-spacing:0.5px;">🌙 Moon Star (Manas / Sensory Mind &amp; Feeling)</div>
                        <div style="font-size:16px; font-weight:800; color:#0f172a; margin-top:2px;">${m.name} <span style="font-size:13px; font-weight:600; color:#64748b;">(Pada ${m.pada} in ${m.sign})</span></div>
                    </div>
                    <span style="font-size:12px; font-weight:700; padding:2px 8px; border-radius:4px; background:#f5f3ff; color:#6d28d9; border:1px solid #ddd6fe;">${m.group} Class</span>
                </div>
                <div style="font-size:12.5px; color:#475569; background:#f8fafc; border-radius:4px; padding:6px 8px;">
                    <div><strong>Star:</strong> ${lore.astronomical_star || '--'} • <strong>Span:</strong> ${lore.zodiacal_span || '--'}</div>
                    <div style="margin-top:2px;"><strong>Deity:</strong> ${lore.presiding_deity || '--'}</div>
                    <div style="margin-top:2px;"><strong>Symbol:</strong> ${lore.symbol_etymology || '--'}</div>
                    <div style="margin-top:2px;"><strong>Lord/Sublord:</strong> ${m.ruler} / ${m.sub_lord}</div>
                </div>
                <div style="font-size:13px; color:#1e293b; line-height:1.45; margin-top:2px;">
                    <strong>Varāhamihira Moon Reading:</strong> <em>"${lore.varahamihira_moon || '--'}"</em>
                </div>
                <div style="font-size:13px; color:#1e293b; line-height:1.45; margin-top:2px;">
                    <strong>Core Emotional Nature:</strong> ${lore.core_psychology || '--'}
                </div>
                <div style="font-size:12.5px; color:#475569; margin-top:auto; padding-top:6px; border-top:1px dashed #e2e8f0;">
                    <strong>Real-World Spheres:</strong> ${lore.real_world_manifestations || '--'}
                </div>
            </div>
        `;
    }

    // 1.4 Nakshatra Dominance Leaderboard (Prominence-Scaled Occupancy)
    const domContainer = cell.querySelector('.nakshatra-dominance-container');
    if (domContainer && nakDominance.leaderboard) {
        let rowsHtml = '';
        nakDominance.leaderboard.forEach(item => {
            const occBadges = item.occupants.map(o => {
                const promTag = (o.prominence && o.prominence !== 1.0) ? ` <span style="font-weight:600; color:#64748b; font-size:11px;">(P:${o.prominence})</span>` : '';
                return `<span style="font-weight:700; background:#e2e8f0; color:#1e293b; padding:1px 6px; border-radius:3px; font-size:12px;">${o.entity} ${o.weight}pt${promTag}</span>`;
            }).join(' ');
            
            rowsHtml += `
                <div style="margin-bottom:8px; padding-bottom:8px; border-bottom:1px solid #f1f5f9;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:3px;">
                        <div style="display:flex; align-items:center; gap:6px;">
                            <strong style="font-size:13.5px; color:#0f172a;">#${item.rank} ${item.nakshatra}</strong>
                            <span style="font-size:12px; padding:1px 6px; border-radius:3px; background:#f1f5f9; color:#475569;">${item.group}</span>
                            <div style="display:inline-flex; gap:4px; margin-left:4px;">${occBadges}</div>
                        </div>
                        <div style="font-size:13px; font-weight:700; color:#1e293b;">
                            ${item.total_points} pts <span style="font-size:12px; font-weight:600; color:#64748b;">(${item.dominance_pct}%)</span>
                        </div>
                    </div>
                    <div style="width:100%; height:8px; background:#e2e8f0; border-radius:4px; overflow:hidden;">
                        <div style="height:100%; width:${Math.min(100, item.dominance_pct)}%; background:#3b82f6; border-radius:4px;"></div>
                    </div>
                </div>
            `;
        });

        domContainer.innerHTML = `
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                <span style="font-size:14px; font-weight:700; color:#1e293b;">📊 Nakshatra Dominance Leaderboard</span>
                <span style="font-size:12px; color:#64748b;">Prominence-Scaled Occupancy: Moon=8×P • Lagna=4pt • Sun=2×P • Grahas=1×P</span>
            </div>
            ${rowsHtml}
        `;
    }

    // 1.5 Balance of Nakṣatra Types (Vic DiCara Style Bi-Directional Chart)
    const tempContainer = cell.querySelector('.temperament-distribution-container');
    if (tempContainer && nakDominance.temperament_breakdown) {
        const tb = nakDominance.temperament_breakdown;

        // 1. Top Proportional Ribbon
        let ribbonCardsHtml = '';
        const maxPct = Math.max(...tb.map(t => t.percentage), 14.3);

        tb.forEach(t => {
            const isDominant = (t.percentage === maxPct && t.percentage > 18.0);
            const isSevereDeficit = (t.percentage <= 2.0);
            
            // Highlight dominant (taller & vivid green) and deficit (pale coral)
            let cardBg = t.percentage > 14.3 ? '#86efac' : '#fecaca';
            let cardText = t.percentage > 14.3 ? '#14532d' : '#7f1d1d';
            let minH = isDominant ? '48px' : '38px';
            let border = isDominant ? '2px solid #16a34a' : '1px solid rgba(0,0,0,0.08)';

            if (isSevereDeficit) {
                cardBg = '#fee2e2';
                cardText = '#991b1b';
            }

            ribbonCardsHtml += `
                <div style="flex: ${Math.max(t.percentage, 7)}; min-height:${minH}; background:${cardBg}; color:${cardText}; border:${border}; border-radius:6px; padding:4px 6px; display:flex; flex-direction:column; justify-content:center; align-items:center; text-align:center; transition:all 0.2s ease;">
                    <span style="font-size:11.5px; font-weight:700; white-space:nowrap;">${t.display_name}</span>
                    <span style="font-size:11px; font-weight:600; opacity:0.9;">${t.percentage}%</span>
                </div>
            `;
        });

        // 2. Bottom Bi-Directional Deviation Rows
        // Center is 14.3% baseline (50% position).
        // Category label is centered above the bar (matching Vic DiCara's chart).
        const MAX_RANGE = 25.0; // +/- 25% deviation covers extreme charts
        const MAX_BAR_WIDTH_PCT = 36; // Leaves 14% breathing room for outer percentage labels

        let deviationRowsHtml = '';
        tb.forEach(t => {
            const dev = t.deviation_pct; // e.g. +12.7% or -13.3%
            const isRight = dev >= 0;
            const absDev = Math.abs(dev);
            
            // Calculate proportional bar width with safe bounds
            let barWidthPct = Math.min(MAX_BAR_WIDTH_PCT, (absDev / MAX_RANGE) * MAX_BAR_WIDTH_PCT);
            if (absDev > 0.1 && barWidthPct < 2.0) {
                barWidthPct = 2.0; // Minimum visible bar indicator
            }

            const barColor = isRight ? '#4ade80' : '#f87171'; // Green for surplus, Salmon/Coral for deficit
            const valueColor = isRight ? '#16a34a' : '#dc2626';

            deviationRowsHtml += `
                <div style="position:relative; margin-bottom:8px;">
                    <!-- Centered Category Label above the bar (matches reference chart) -->
                    <div style="text-align:center; line-height:1.2; margin-bottom:2px;">
                        <span style="font-size:12px; font-weight:700; color:#1e293b; font-family:Georgia, serif; background:rgba(255,255,255,0.9); padding:0 6px; border-radius:3px;">
                            ${t.display_name}
                        </span>
                    </div>

                    <!-- Horizontal Bar & Percentage Row -->
                    <div style="position:relative; height:16px; display:flex; align-items:center;">
                        <!-- Left Deficit Bar (extends left from 50% baseline) -->
                        ${!isRight ? `
                            <div style="position:absolute; right:50%; width:${barWidthPct}%; height:13px; background:${barColor}; border-radius:7px 0 0 7px; box-shadow:0 1px 2px rgba(0,0,0,0.06);"></div>
                            <span style="position:absolute; right:calc(50% + ${barWidthPct}% + 6px); font-size:11px; font-weight:700; color:${valueColor}; white-space:nowrap;">${t.percentage}%</span>
                        ` : ''}

                        <!-- Right Surplus Bar (extends right from 50% baseline) -->
                        ${isRight ? `
                            <div style="position:absolute; left:50%; width:${barWidthPct}%; height:13px; background:${barColor}; border-radius:0 7px 7px 0; box-shadow:0 1px 2px rgba(0,0,0,0.06);"></div>
                            <span style="position:absolute; left:calc(50% + ${barWidthPct}% + 6px); font-size:11px; font-weight:700; color:${valueColor}; white-space:nowrap;">${t.percentage}%</span>
                        ` : ''}
                    </div>
                </div>
            `;
        });

        tempContainer.innerHTML = `
            <div style="font-size:15px; font-weight:700; color:#1e293b; margin-bottom:10px; font-family:Georgia, serif; display:flex; justify-content:space-between; align-items:center;">
                <span>Balance of Nakṣatra Types</span>
                <span style="font-size:11.5px; font-weight:600; color:#64748b; font-family:sans-serif;">Baseline: 14.3% per type</span>
            </div>

            <!-- Top Proportional Ribbon -->
            <div style="display:flex; gap:4px; align-items:flex-end; margin-bottom:14px; background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:6px;">
                ${ribbonCardsHtml}
            </div>

            <!-- Bottom Bi-Directional Deviation Graph -->
            <div style="position:relative; background:#ffffff; border:1px solid #e2e8f0; border-radius:8px; padding:14px 10px; overflow:hidden;">
                <!-- Vertical Background Grid Lines -->
                <div style="position:absolute; top:0; bottom:0; left:14%; width:1px; background:#f1f5f9;"></div>
                <div style="position:absolute; top:0; bottom:0; left:26%; width:1px; background:#f1f5f9;"></div>
                <div style="position:absolute; top:0; bottom:0; left:38%; width:1px; background:#f1f5f9;"></div>
                <div style="position:absolute; top:0; bottom:0; left:50%; width:2px; background:#1e293b; z-index:1;"></div> <!-- Black Center Baseline -->
                <div style="position:absolute; top:0; bottom:0; left:62%; width:1px; background:#f1f5f9;"></div>
                <div style="position:absolute; top:0; bottom:0; left:74%; width:1px; background:#f1f5f9;"></div>
                <div style="position:absolute; top:0; bottom:0; left:86%; width:1px; background:#f1f5f9;"></div>

                <!-- Subtle Background Tints -->
                <div style="position:absolute; top:0; bottom:0; left:0; width:50%; background:rgba(239, 68, 68, 0.02); pointer-events:none;"></div>
                <div style="position:absolute; top:0; bottom:0; left:50%; width:50%; background:rgba(34, 197, 94, 0.02); pointer-events:none;"></div>

                <!-- Rows -->
                <div style="position:relative; z-index:2;">
                    ${deviationRowsHtml}
                </div>
            </div>
        `;
    }

    // 1.6 All Occupied Nakshatras Table
    const tableContainer = cell.querySelector('.all-nakshatras-table-container');
    if (tableContainer) {
        const nakGrahas = currentData.nakshatras ? currentData.nakshatras.grahas || {} : {};
        const d1Grahas = currentData.vargas && currentData.vargas.D1 ? currentData.vargas.D1.grahas || {} : {};
        const d1Lagna = currentData.vargas && currentData.vargas.D1 ? currentData.vargas.D1.lagna || {} : {};

        const nakGroupMap = {};
        if (nakDominance.leaderboard) {
            nakDominance.leaderboard.forEach(item => {
                nakGroupMap[item.nakshatra] = item.group;
            });
        }

        const entitiesList = ["Lagna", "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"];
        let trHtml = '';

        entitiesList.forEach(ent => {
            const nInfo = nakGrahas[ent] || {};
            const nakName = nInfo.nakshatra || '--';
            const grp = nakGroupMap[nakName] || '--';
            const sign = ent === "Lagna" ? (d1Lagna.sign || '--') : (d1Grahas[ent]?.sign || '--');
            const deg = ent === "Lagna" ? (d1Lagna.degree_0_to_30?.toFixed(2) || '--') : (d1Grahas[ent]?.degree_0_to_30?.toFixed(2) || '--');

            trHtml += `
                <tr style="border-bottom:1px solid #f1f5f9; font-size:13px;">
                    <td style="padding:6px 8px; font-weight:700; color:#1e293b;">${ent}</td>
                    <td style="padding:6px 8px; color:#475569;">${sign} ${deg}°</td>
                    <td style="padding:6px 8px; font-weight:600; color:#0f172a;">${nakName}</td>
                    <td style="padding:6px 8px; color:#475569;">Pada ${nInfo.pada || '--'}</td>
                    <td style="padding:6px 8px; color:#475569;">${nInfo.nakshatra_lord || '--'} / ${nInfo.sub_lord || '--'}</td>
                    <td style="padding:6px 8px;"><span style="font-size:12px; font-weight:600; padding:1px 6px; border-radius:3px; background:#f1f5f9; color:#475569;">${grp}</span></td>
                </tr>
            `;
        });

        tableContainer.innerHTML = `
            <div style="font-size:14px; font-weight:700; color:#1e293b; margin-bottom:8px;">✨ Planetary Nakshatras &amp; Overlords</div>
            <table style="width:100%; border-collapse:collapse; text-align:left;">
                <thead>
                    <tr style="background:#f8fafc; border-bottom:1.5px solid #cbd5e1; font-size:12px; color:#475569; text-transform:uppercase;">
                        <th style="padding:6px 8px;">Body</th>
                        <th style="padding:6px 8px;">Rāśi Position</th>
                        <th style="padding:6px 8px;">Nakshatra</th>
                        <th style="padding:6px 8px;">Pada</th>
                        <th style="padding:6px 8px;">Lord / Sublord</th>
                        <th style="padding:6px 8px;">Temperament</th>
                    </tr>
                </thead>
                <tbody>${trHtml}</tbody>
            </table>
        `;
    }

    // ==========================================
    // TAB 2: ELEMENTS & OPERATIONAL AXIS
    // ==========================================
    const axisContainer = cell.querySelector('.operational-axis-container');
    if (axisContainer && operationalAxis.rashi_lagna) {
        const r = operationalAxis.rashi_lagna;
        const n = operationalAxis.navamsha_lagna;
        const vBadge = operationalAxis.is_vargottama 
            ? `<div style="background:#f0fdf4; border:1px solid #86efac; border-radius:4px; padding:6px 10px; margin-top:8px; font-size:13px; font-weight:700; color:#15803d;">🌟 VARGOTTAMA LAGNA DETECTED: +30% Vitality, Inner Consistency &amp; Resilience</div>` 
            : '';

        axisContainer.innerHTML = `
            <div style="font-size:14px; font-weight:700; color:#1e293b; margin-bottom:8px;">🌲 Operational Axis: Rāśi Tree vs. Navāṁśa Fruit</div>
            <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(260px, 1fr)); gap:10px;">
                <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:6px; padding:10px;">
                    <div style="font-size:12px; font-weight:700; color:#2563eb; text-transform:uppercase;">D1 Rising Rāśi (The Outer Tree)</div>
                    <div style="font-size:15px; font-weight:700; color:#0f172a; margin-top:2px;">${r.sign} (Lord: ${r.lord})</div>
                    <div style="font-size:12.5px; color:#475569; margin-top:4px;">${r.element} Element • ${r.guna} • ${r.rising_mode}</div>
                    <div style="font-size:13px; color:#334155; margin-top:6px; line-height:1.4;">${r.interpretation}</div>
                </div>
                <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:6px; padding:10px;">
                    <div style="font-size:12px; font-weight:700; color:#7c3aed; text-transform:uppercase;">D9 Rising Navāṁśa (The Inner Fruit)</div>
                    <div style="font-size:15px; font-weight:700; color:#0f172a; margin-top:2px;">${n.sign} (Lord: ${n.lord})</div>
                    <div style="font-size:12.5px; color:#475569; margin-top:4px;">${n.element} Element • ${n.guna} • Lord D1 Dignity: ${n.lord_d1_dignity}</div>
                    <div style="font-size:13px; color:#334155; margin-top:6px; line-height:1.4;">${n.interpretation}</div>
                </div>
            </div>
            ${vBadge}
        `;
    }

    // 2.2 Balance of Environmental Harmonics (Bi-Directional Graphic with Mode Switcher)
    const envDistContainer = cell.querySelector('.environmental-distribution-container');
    if (envDistContainer && envTally) {
        if (!envDistContainer.dataset.envMode) {
            envDistContainer.dataset.envMode = 'elements';
        }

        const renderEnvDistribution = (mode) => {
            envDistContainer.dataset.envMode = mode;
            let title = 'Balance of Four Elements (Tattvas)';
            let baselineLabel = 'Equilibrium Baseline: 25.0% (1/4th)';
            let baselinePct = 25.0;
            let items = [];

            if (mode === 'elements') {
                title = '🔥 Balance of Four Elements (Tattvas)';
                baselineLabel = 'Equilibrium Baseline: 25.0% (1/4th)';
                baselinePct = 25.0;
                items = envTally.elements?.breakdown || [];
            } else if (mode === 'gunas') {
                title = '🌀 Balance of Three Guṇas (Modalities)';
                baselineLabel = 'Equilibrium Baseline: 33.3% (1/3rd)';
                baselinePct = 33.3;
                items = envTally.gunas?.breakdown || [];
            } else if (mode === 'doshas') {
                title = '🍵 Balance of Ayurvedic Doshas (Prakṛti)';
                baselineLabel = 'Equilibrium Baseline: 33.3% (1/3rd)';
                baselinePct = 33.3;
                items = envTally.ayurvedic_doshas?.breakdown || [];
            }

            if (!items || items.length === 0) return;

            // 1. Top Proportional Ribbon
            let ribbonCardsHtml = '';
            const maxPct = Math.max(...items.map(t => t.percentage), baselinePct);

            items.forEach(t => {
                const isDominant = (t.percentage === maxPct && t.percentage > baselinePct);
                const isSevereDeficit = (t.percentage <= 5.0);

                let cardBg = t.percentage > baselinePct ? '#86efac' : '#fecaca';
                let cardText = t.percentage > baselinePct ? '#14532d' : '#7f1d1d';
                let minH = isDominant ? '48px' : '38px';
                let border = isDominant ? '2px solid #16a34a' : '1px solid rgba(0,0,0,0.08)';

                if (isSevereDeficit) {
                    cardBg = '#fee2e2';
                    cardText = '#991b1b';
                }

                ribbonCardsHtml += `
                    <div style="flex: ${Math.max(t.percentage, 8)}; min-height:${minH}; background:${cardBg}; color:${cardText}; border:${border}; border-radius:6px; padding:4px 6px; display:flex; flex-direction:column; justify-content:center; align-items:center; text-align:center; transition:all 0.2s ease;">
                        <span style="font-size:11.5px; font-weight:700; white-space:nowrap;">${t.icon || ''} ${t.display_name}</span>
                        <span style="font-size:11px; font-weight:600; opacity:0.9;">${t.percentage}% <span style="font-size:10px; opacity:0.8;">(${t.points} pt)</span></span>
                    </div>
                `;
            });

            // 2. Bottom Bi-Directional Deviation Rows
            const MAX_RANGE = 35.0; // +/- 35% covers extreme shifts
            const MAX_BAR_WIDTH_PCT = 36; // Leaves 14% breathing room for labels

            let deviationRowsHtml = '';
            items.forEach(t => {
                const dev = t.deviation_pct; // e.g. +45.0% or -25.0%
                const isRight = dev >= 0;
                const absDev = Math.abs(dev);

                let barWidthPct = Math.min(MAX_BAR_WIDTH_PCT, (absDev / MAX_RANGE) * MAX_BAR_WIDTH_PCT);
                if (absDev > 0.1 && barWidthPct < 2.0) {
                    barWidthPct = 2.0;
                }

                const barColor = isRight ? '#4ade80' : '#f87171'; // Green for surplus, Salmon for deficit
                const valueColor = isRight ? '#16a34a' : '#dc2626';
                const signPrefix = dev > 0 ? '+' : '';
                const d1Info = (t.d1_count !== undefined) ? ` • D1: ${t.d1_count}` : '';

                deviationRowsHtml += `
                    <div style="position:relative; margin-bottom:10px;">
                        <!-- Centered Category Label above the bar -->
                        <div style="text-align:center; line-height:1.2; margin-bottom:2px;">
                            <span style="font-size:12px; font-weight:700; color:#1e293b; font-family:Georgia, serif; background:rgba(255,255,255,0.95); padding:1px 8px; border-radius:3px; border:1px solid #f1f5f9; box-shadow:0 1px 2px rgba(0,0,0,0.03);">
                                ${t.icon || ''} ${t.display_name} <span style="font-size:11px; color:#64748b; font-weight:500;">(${t.sanskrit || ''})</span>
                            </span>
                        </div>

                        <!-- Horizontal Bar & Percentage Row -->
                        <div style="position:relative; height:18px; display:flex; align-items:center;">
                            <!-- Left Deficit Bar -->
                            ${!isRight ? `
                                <div style="position:absolute; right:50%; width:${barWidthPct}%; height:14px; background:${barColor}; border-radius:7px 0 0 7px; box-shadow:0 1px 2px rgba(0,0,0,0.06);"></div>
                                <span style="position:absolute; right:calc(50% + ${barWidthPct}% + 6px); font-size:11px; font-weight:700; color:${valueColor}; white-space:nowrap;">
                                    ${t.percentage}% <span style="font-size:10px; font-weight:600; opacity:0.85;">(${signPrefix}${dev}% | ${t.points} pt${d1Info})</span>
                                </span>
                            ` : ''}

                            <!-- Right Surplus Bar -->
                            ${isRight ? `
                                <div style="position:absolute; left:50%; width:${barWidthPct}%; height:14px; background:${barColor}; border-radius:0 7px 7px 0; box-shadow:0 1px 2px rgba(0,0,0,0.06);"></div>
                                <span style="position:absolute; left:calc(50% + ${barWidthPct}% + 6px); font-size:11px; font-weight:700; color:${valueColor}; white-space:nowrap;">
                                    ${t.percentage}% <span style="font-size:10px; font-weight:600; opacity:0.85;">(${signPrefix}${dev}% | ${t.points} pt${d1Info})</span>
                                </span>
                            ` : ''}
                        </div>
                    </div>
                `;
            });

            // Pills active styles
            const activeElemStyle = mode === 'elements' ? 'background:#ffffff; color:#1e293b; font-weight:700; box-shadow:0 1px 2px rgba(0,0,0,0.08);' : 'background:transparent; color:#64748b; font-weight:600;';
            const activeGunaStyle = mode === 'gunas' ? 'background:#ffffff; color:#1e293b; font-weight:700; box-shadow:0 1px 2px rgba(0,0,0,0.08);' : 'background:transparent; color:#64748b; font-weight:600;';
            const activeDoshaStyle = mode === 'doshas' ? 'background:#ffffff; color:#1e293b; font-weight:700; box-shadow:0 1px 2px rgba(0,0,0,0.08);' : 'background:transparent; color:#64748b; font-weight:600;';

            envDistContainer.innerHTML = `
                <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px; margin-bottom:10px;">
                    <div>
                        <div style="font-size:15px; font-weight:700; color:#1e293b; font-family:Georgia, serif;">${title}</div>
                        <div style="font-size:11.5px; font-weight:600; color:#64748b; font-family:sans-serif; margin-top:1px;">
                            ${baselineLabel} • Ṣaḍvarga (20-pt Harmonic Matrix)
                        </div>
                    </div>

                    <!-- Mode Switcher Pills -->
                    <div class="env-mode-pills" style="display:inline-flex; background:#f1f5f9; border:1px solid #e2e8f0; border-radius:6px; padding:2px; gap:2px;">
                        <button type="button" class="btn-env-mode-elem" style="border:none; border-radius:4px; padding:3px 9px; font-size:11.5px; cursor:pointer; ${activeElemStyle}">🔥 Elements</button>
                        <button type="button" class="btn-env-mode-guna" style="border:none; border-radius:4px; padding:3px 9px; font-size:11.5px; cursor:pointer; ${activeGunaStyle}">🌀 Guṇas</button>
                        <button type="button" class="btn-env-mode-dosha" style="border:none; border-radius:4px; padding:3px 9px; font-size:11.5px; cursor:pointer; ${activeDoshaStyle}">🍵 Doshas</button>
                    </div>
                </div>

                <!-- Top Proportional Ribbon -->
                <div style="display:flex; gap:4px; align-items:flex-end; margin-bottom:14px; background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:6px;">
                    ${ribbonCardsHtml}
                </div>

                <!-- Bottom Bi-Directional Deviation Graph -->
                <div style="position:relative; background:#ffffff; border:1px solid #e2e8f0; border-radius:8px; padding:14px 10px; overflow:hidden;">
                    <!-- Vertical Background Grid Lines -->
                    <div style="position:absolute; top:0; bottom:0; left:14%; width:1px; background:#f1f5f9;"></div>
                    <div style="position:absolute; top:0; bottom:0; left:26%; width:1px; background:#f1f5f9;"></div>
                    <div style="position:absolute; top:0; bottom:0; left:38%; width:1px; background:#f1f5f9;"></div>
                    <div style="position:absolute; top:0; bottom:0; left:50%; width:2px; background:#1e293b; z-index:1;"></div> <!-- Black Center Baseline -->
                    <div style="position:absolute; top:0; bottom:0; left:62%; width:1px; background:#f1f5f9;"></div>
                    <div style="position:absolute; top:0; bottom:0; left:74%; width:1px; background:#f1f5f9;"></div>
                    <div style="position:absolute; top:0; bottom:0; left:86%; width:1px; background:#f1f5f9;"></div>

                    <!-- Subtle Background Tints -->
                    <div style="position:absolute; top:0; bottom:0; left:0; width:50%; background:rgba(239, 68, 68, 0.02); pointer-events:none;"></div>
                    <div style="position:absolute; top:0; bottom:0; left:50%; width:50%; background:rgba(34, 197, 94, 0.02); pointer-events:none;"></div>

                    <!-- Rows -->
                    <div style="position:relative; z-index:2;">
                        ${deviationRowsHtml}
                    </div>
                </div>
            `;

            // Attach click listeners to pills
            const btnElem = envDistContainer.querySelector('.btn-env-mode-elem');
            const btnGuna = envDistContainer.querySelector('.btn-env-mode-guna');
            const btnDosha = envDistContainer.querySelector('.btn-env-mode-dosha');

            if (btnElem) btnElem.onclick = (e) => { e.stopPropagation(); renderEnvDistribution('elements'); };
            if (btnGuna) btnGuna.onclick = (e) => { e.stopPropagation(); renderEnvDistribution('gunas'); };
            if (btnDosha) btnDosha.onclick = (e) => { e.stopPropagation(); renderEnvDistribution('doshas'); };
        };

        // Initial render using stored or default mode
        renderEnvDistribution(envDistContainer.dataset.envMode || 'elements');
    }

    const envContainer = cell.querySelector('.environmental-tallies-container');
    if (envContainer && envTally.elements) {
        const e = envTally.elements;
        const g = envTally.gunas;
        const d = envTally.ayurvedic_doshas;

        envContainer.innerHTML = `
            <div style="font-size:14px; font-weight:700; color:#1e293b; margin-bottom:8px; display:flex; justify-content:space-between; align-items:center;">
                <span>🌿 Macro Environmental Tally (Ṣaḍvarga Weighted)</span>
                <span style="font-size:11.5px; font-weight:600; color:#64748b;">D1:6 • D9:5 • D3:4 • D2:2 • D12:2 • D30:1</span>
            </div>
            <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(220px, 1fr)); gap:10px;">
                <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:6px; padding:10px;">
                    <div style="font-size:13px; font-weight:700; color:#0f172a; margin-bottom:4px;">🔥 Five Great Elements (Tattvas)</div>
                    <div style="font-size:12.5px; color:#475569;">
                        <div>Fire: <strong>${e.percentages.Fire}%</strong> <span style="font-size:11.5px; color:#64748b;">(${e.points.Fire} pt | D1: ${e.counts.Fire})</span></div>
                        <div>Earth: <strong>${e.percentages.Earth}%</strong> <span style="font-size:11.5px; color:#64748b;">(${e.points.Earth} pt | D1: ${e.counts.Earth})</span></div>
                        <div>Air: <strong>${e.percentages.Air}%</strong> <span style="font-size:11.5px; color:#64748b;">(${e.points.Air} pt | D1: ${e.counts.Air})</span></div>
                        <div>Water: <strong>${e.percentages.Water}%</strong> <span style="font-size:11.5px; color:#64748b;">(${e.points.Water} pt | D1: ${e.counts.Water})</span></div>
                    </div>
                    <div style="font-size:13px; font-weight:700; color:#b91c1c; margin-top:6px;">Dominant Tattva: ${e.dominant}</div>
                </div>
                <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:6px; padding:10px;">
                    <div style="font-size:13px; font-weight:700; color:#0f172a; margin-bottom:4px;">🌀 Three Guṇas (Modality)</div>
                    <div style="font-size:12.5px; color:#475569;">
                        <div>Rajas (Movable): <strong>${g.percentages['Rajas (Movable)']}%</strong> <span style="font-size:11.5px; color:#64748b;">(${g.points['Rajas (Movable)']} pt)</span></div>
                        <div>Tamas (Fixed): <strong>${g.percentages['Tamas (Fixed)']}%</strong> <span style="font-size:11.5px; color:#64748b;">(${g.points['Tamas (Fixed)']} pt)</span></div>
                        <div>Sattva (Dual): <strong>${g.percentages['Sattva (Dual)']}%</strong> <span style="font-size:11.5px; color:#64748b;">(${g.points['Sattva (Dual)']} pt)</span></div>
                    </div>
                    <div style="font-size:13px; font-weight:700; color:#0d9488; margin-top:6px;">Dominant Guṇa: ${g.dominant}</div>
                </div>
                <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:6px; padding:10px;">
                    <div style="font-size:13px; font-weight:700; color:#0f172a; margin-bottom:4px;">🍵 Ayurvedic Constitution (Prakṛti)</div>
                    <div style="font-size:12.5px; color:#475569;">
                        <div>Vāta (Air): <strong>${d.percentages.Vata}%</strong> <span style="font-size:11.5px; color:#64748b;">(${d.points.Vata} pt)</span></div>
                        <div>Pitta (Fire): <strong>${d.percentages.Pitta}%</strong> <span style="font-size:11.5px; color:#64748b;">(${d.points.Pitta} pt)</span></div>
                        <div>Kapha (Earth/Water): <strong>${d.percentages.Kapha}%</strong> <span style="font-size:11.5px; color:#64748b;">(${d.points.Kapha} pt)</span></div>
                    </div>
                    <div style="font-size:13px; font-weight:700; color:#2563eb; margin-top:6px;">Prakṛti Baseline: ${d.dominant}</div>
                </div>
            </div>
        `;
    }

    // ==========================================
    // TAB 3: PLANETARY PROMINENCE & DIGNITY
    // ==========================================
    const cmdSpotlight = cell.querySelector('.commander-spotlight-container');
    const formatAvastha = val => (val && typeof val === 'object') ? (val.state || val.name || '--') : (val || '--');

    if (cmdSpotlight && planetRank.chart_commander) {
        const c = planetRank.chart_commander;
        const dMood = formatAvastha(c.dignity_mood);
        const mat = formatAvastha(c.maturity);

        cmdSpotlight.innerHTML = `
            <div style="background:#fffbeb; border:1.5px solid #fde68a; border-radius:6px; padding:12px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <div style="font-size:12px; font-weight:700; color:#92400e; text-transform:uppercase;">👑 #1 Chart Commander (Highest Stage Volume)</div>
                        <div style="font-size:16px; font-weight:800; color:#78350f; margin-top:2px;">${c.planet} in House ${c.house} (${c.sign})</div>
                    </div>
                    <span style="font-size:13px; font-weight:700; padding:2px 8px; border-radius:4px; background:#fef3c7; color:#92400e; border:1px solid #fcd34d;">Score: ${c.prominence_score}</span>
                </div>
                <div style="font-size:13px; color:#451a03; margin-top:6px; line-height:1.45;">
                    Commands the chart via <strong>${c.shadbala_rupas} Rupas</strong> (${c.shadbala_ratio}x required Shadbala) with access bonuses: <em>${c.opportunity_reasons.join(', ') || 'Angular strength'}</em>. Dignity Mood: <strong>${dMood}</strong> (${mat} maturity, Vimshopaka: ${c.vimshopak_score}/20).
                </div>
            </div>
        `;
    }

    const promTable = cell.querySelector('.prominence-table-container');
    if (promTable && planetRank.leaderboard) {
        let pTrHtml = '';
        planetRank.leaderboard.forEach(p => {
            const pMood = formatAvastha(p.dignity_mood);
            pTrHtml += `
                <tr style="border-bottom:1px solid #f1f5f9; font-size:13px;">
                    <td style="padding:6px 8px; font-weight:700; color:#1e293b;">#${p.rank} ${p.planet}</td>
                    <td style="padding:6px 8px; color:#475569;">House ${p.house} (${p.sign})</td>
                    <td style="padding:6px 8px; font-weight:700; color:#0f172a;">${p.prominence_score}</td>
                    <td style="padding:6px 8px; color:#475569;">${p.shadbala_rupas} (${p.shadbala_ratio}x)</td>
                    <td style="padding:6px 8px; color:#0284c7; font-size:12px;">${p.opportunity_reasons.join(', ') || '--'}</td>
                    <td style="padding:6px 8px; font-weight:600; color:#334155;">${pMood}</td>
                    <td style="padding:6px 8px; color:#475569;">${p.vimshopak_score}</td>
                    <td style="padding:6px 8px;"><span style="font-size:12px; font-weight:700; padding:1px 6px; border-radius:3px; background:${p.net_scale_score >= 0 ? '#f0fdf4' : '#fef2f2'}; color:${p.net_scale_score >= 0 ? '#15803d' : '#b91c1c'};">${p.net_scale_score}%</span></td>
                </tr>
            `;
        });

        promTable.innerHTML = `
            <div style="font-size:14px; font-weight:700; color:#1e293b; margin-bottom:8px;">📊 Planetary Prominence vs. Dignity Leaderboard</div>
            <table style="width:100%; border-collapse:collapse; text-align:left;">
                <thead>
                    <tr style="background:#f8fafc; border-bottom:1.5px solid #cbd5e1; font-size:12px; color:#475569; text-transform:uppercase;">
                        <th style="padding:6px 8px;">Rank / Graha</th>
                        <th style="padding:6px 8px;">Placement</th>
                        <th style="padding:6px 8px;">Prominence Score</th>
                        <th style="padding:6px 8px;">Shadbala (SBR)</th>
                        <th style="padding:6px 8px;">Opportunity Center</th>
                        <th style="padding:6px 8px;">Dignity Mood</th>
                        <th style="padding:6px 8px;">Vimshopaka</th>
                        <th style="padding:6px 8px;">Net Scale</th>
                    </tr>
                </thead>
                <tbody>${pTrHtml}</tbody>
            </table>
        `;
    }

    // ==========================================
    // TAB 4: SYNTHESIS DESK
    // ==========================================
    const synDesk = cell.querySelector('.synthesis-desk-container');
    if (synDesk && synthesis.action_mode) {
        synDesk.innerHTML = `
            <div style="font-size:14px; font-weight:700; color:#1e293b; margin-bottom:10px;">🧪 Synthesis Desk: The Master Astrological Recipe</div>
            <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(260px, 1fr)); gap:10px;">
                <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:6px; padding:10px;">
                    <div style="font-size:12px; font-weight:700; color:#64748b; text-transform:uppercase;">1. Bodily Action Vehicle</div>
                    <div style="font-size:15px; font-weight:700; color:#0f172a; margin-top:2px;">${synthesis.action_mode} (${synthesis.action_group})</div>
                    <div style="font-size:12.5px; color:#475569; margin-top:4px;">How you project energy and initiate outer worldly action.</div>
                </div>
                <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:6px; padding:10px;">
                    <div style="font-size:12px; font-weight:700; color:#64748b; text-transform:uppercase;">2. Emotional Mind Filter</div>
                    <div style="font-size:15px; font-weight:700; color:#0f172a; margin-top:2px;">${synthesis.perception_mode} (${synthesis.perception_group})</div>
                    <div style="font-size:12.5px; color:#475569; margin-top:4px;">How you perceive, feel, and digest life events internally.</div>
                </div>
                <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:6px; padding:10px;">
                    <div style="font-size:12px; font-weight:700; color:#64748b; text-transform:uppercase;">3. Core Polarity Friction</div>
                    <div style="font-size:15px; font-weight:700; color:#0f172a; margin-top:2px;">${synthesis.polarity_state} (${synthesis.polarity_friction}/100)</div>
                    <div style="font-size:12.5px; color:#475569; margin-top:4px;">Baseline harmony or creative conflict between action and feeling.</div>
                </div>
                <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:6px; padding:10px;">
                    <div style="font-size:12px; font-weight:700; color:#64748b; text-transform:uppercase;">4. Primary Driving Temperament</div>
                    <div style="font-size:15px; font-weight:700; color:#0f172a; margin-top:2px;">${synthesis.dominant_temperament} (${synthesis.dominant_nakshatra})</div>
                    <div style="font-size:12.5px; color:#475569; margin-top:4px;">The strongest underlying behavioral current in your birth chart.</div>
                </div>
                <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:6px; padding:10px;">
                    <div style="font-size:12px; font-weight:700; color:#64748b; text-transform:uppercase;">5. Environmental Field</div>
                    <div style="font-size:15px; font-weight:700; color:#0f172a; margin-top:2px;">${synthesis.dominant_element} • ${synthesis.dominant_guna}</div>
                    <div style="font-size:12.5px; color:#475569; margin-top:4px;">Prakṛti Dosha: <strong>${synthesis.dominant_dosha}</strong> • Vargottama: ${synthesis.is_vargottama ? 'Yes (+30%)' : 'No'}</div>
                </div>
                <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:6px; padding:10px;">
                    <div style="font-size:12px; font-weight:700; color:#64748b; text-transform:uppercase;">6. Dominant Chart Commander</div>
                    <div style="font-size:15px; font-weight:700; color:#0f172a; margin-top:2px;">${synthesis.chart_commander} (Score: ${synthesis.commander_prominence})</div>
                    <div style="font-size:12.5px; color:#475569; margin-top:4px;">Commands the loudest voice and stage presence across all life areas.</div>
                </div>
            </div>
            <div style="margin-top:14px; padding:12px; background:#fffdf5; border:1px solid #fef3c7; border-radius:6px;">
                <div style="font-size:13.5px; font-weight:700; color:#78350f; margin-bottom:4px;">✨ Astrologer Synthesis Synthesis Blueprint:</div>
                <div style="font-size:13px; color:#451a03; line-height:1.5;">
                    The native acts upon the world through the <strong>${synthesis.action_mode}</strong> archetype (${synthesis.action_group}), while emotionally experiencing reality through <strong>${synthesis.perception_mode}</strong> (${synthesis.perception_group}). With a polarity index of <strong>${synthesis.polarity_friction}/100</strong>, life manifests through <em>${synthesis.polarity_state}</em>. When navigating crises, the chart draws supreme authority from <strong>${synthesis.chart_commander}</strong>, operating within an environment grounded in <strong>${synthesis.dominant_element}</strong> and <strong>${synthesis.dominant_guna}</strong>.
                </div>
            </div>
        `;
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
    titleEl.textContent = subjectName + " — Astrological Synthesis Report";

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
        title: 'Astrological Synthesis Report',
        icon: '📜',
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
    window.switchReportTab = switchReportTab;
}
