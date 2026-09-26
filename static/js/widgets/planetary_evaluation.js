/**
 * Astra Planetary Evaluation & Positive-Negative Scale Widget
 * 
 * Implements Vic DiCara's continuous dignitary diagnostic scale,
 * evaluating functional role, shadvarga intent, peer modifier shifts,
 * house terrain expression, and step-by-step audit trails.
 */

function updatePlanetaryEvaluationWidget(cell, chartData) {
    if (!cell) {
        cell = document.getElementById('widgetMaximizeContainer') || document.querySelector('.grid-cell[data-widget="planetary-evaluation"]');
    }
    if (!cell) return;
    const currentData = chartData || window.currentChartData;
    if (!currentData || !currentData.planetary_evaluation) return;
    const evalData = currentData.planetary_evaluation;
    const summary = evalData.summary || {};
    const planets = evalData.planets || {};

            // Render Master Lords Banner
            const banner = cell.querySelector('.master-lords-banner');
            if (banner && summary.master_lords) {
                const ml = summary.master_lords;
                const lagnaLord = ml.lagna_lord || {};
                const navLord = ml.navamsha_lord || {};
                const drekLord = ml.drekkana_lord || {};
                const pred = summary.chart_predominance || {};
                const mp = summary.moon_phase || null;

                let moonPhaseCardHtml = '';
                if (mp) {
                    const isWax = mp.is_waxing;
                    const illum = Number(mp.illumination_pct || 0);
                    const gFac = Number(mp.gradual_factor !== undefined ? mp.gradual_factor : (illum >= 50 ? (illum - 50)/50 : (50 - illum)/50));
                    const effMaxMod = (25.0 * gFac).toFixed(1);
                    let mBorder = '#2563eb';
                    let mBg = '#ffffff';
                    let mClass = 'mixed';
                    if (illum >= 50.0) {
                        mBorder = illum >= 65.0 ? '#16a34a' : '#0d9488';
                        mBg = illum >= 65.0 ? '#f0fdf4' : '#f0fdfa';
                        mClass = 'positive';
                    } else {
                        mBorder = illum < 35.0 ? '#dc2626' : '#d97706';
                        mBg = illum < 35.0 ? '#fef2f2' : '#fffbeb';
                        mClass = 'negative';
                    }
                    moonPhaseCardHtml = `
                        <div class="eval-master-card" style="border-left: 3px solid ${mBorder}; background:${mBg};">
                            <div style="font-size:10px; text-transform:uppercase; color:#475569; font-weight:bold;">🌙 Lunar Phase &amp; Continuous Spectrum</div>
                            <div style="display:flex; align-items:center; justify-content:space-between; margin-top:3px;">
                                <strong style="font-size:13px; color:#1e293b;">${mp.badge || `${isWax ? '🌔 Waxing' : '🌘 Waning'} (${illum.toFixed(0)}%)`}</strong>
                                <span class="eval-scale-badge ${mClass}" style="font-size:10px; padding:1px 6px;">${mp.paksha}</span>
                            </div>
                            <div style="font-size:11px; font-weight:600; color:#334155; margin-top:2px;">${mp.light_type}</div>
                            <div style="font-size:9.5px; color:#64748b; margin-top:2px;">Elongation: ${mp.elongation_deg}° • Scaling Factor: ${gFac.toFixed(2)}x (±${effMaxMod}% max terrain mod, BPHS 28.10-11)</div>
                        </div>
                    `;
                }

                banner.innerHTML = `
                    <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap:8px; width:100%; margin-bottom:10px;">
                        <div class="eval-master-card" style="border-left: 3px solid #2563eb;">
                            <div style="font-size:10px; text-transform:uppercase; color:#64748b; font-weight:bold;">🚩 Lagna Lord (D1) — Life Mastery</div>
                            <div style="display:flex; align-items:center; justify-content:space-between; margin-top:3px;">
                                <strong style="font-size:13.5px; color:#1e293b;">${lagnaLord.planet || '-'}</strong>
                                <span class="eval-scale-badge ${lagnaLord.expression_class || 'mixed'}">${lagnaLord.scale_score >= 0 ? '+' : ''}${Number(lagnaLord.scale_score || 0).toFixed(1)}%</span>
                            </div>
                            <div style="font-size:11px; color:#0369a1; font-weight:600; margin-top:2px;">
                                Rules ${lagnaLord.rising_sign || ''} Ascendant • in ${lagnaLord.placed_sign || ''}
                            </div>
                            <div style="font-size:10px; color:#475569; margin-top:2px;">${lagnaLord.governs || ''}</div>
                        </div>

                        <div class="eval-master-card" style="border-left: 3px solid #7c3aed;">
                            <div style="font-size:10px; text-transform:uppercase; color:#64748b; font-weight:bold;">☸️ Navamsha Lord (D9) — Soul Happiness</div>
                            <div style="display:flex; align-items:center; justify-content:space-between; margin-top:3px;">
                                <strong style="font-size:13.5px; color:#1e293b;">${navLord.planet || '-'}</strong>
                                <span class="eval-scale-badge ${navLord.expression_class || 'mixed'}">${navLord.scale_score >= 0 ? '+' : ''}${Number(navLord.scale_score || 0).toFixed(1)}%</span>
                            </div>
                            <div style="font-size:11px; color:#6d28d9; font-weight:600; margin-top:2px;">
                                Rules ${navLord.rising_sign || ''} D9 Lagna • in ${navLord.placed_sign || ''}
                            </div>
                            <div style="font-size:10px; color:#475569; margin-top:2px;">${navLord.governs || ''}</div>
                        </div>

                        <div class="eval-master-card" style="border-left: 3px solid #b45309;">
                            <div style="font-size:10px; text-transform:uppercase; color:#64748b; font-weight:bold;">⚔️ Drekkana Lord (D3) — Worldly Courage</div>
                            <div style="display:flex; align-items:center; justify-content:space-between; margin-top:3px;">
                                <strong style="font-size:13.5px; color:#1e293b;">${drekLord.planet || '-'}</strong>
                                <span class="eval-scale-badge ${drekLord.expression_class || 'mixed'}">${drekLord.scale_score >= 0 ? '+' : ''}${Number(drekLord.scale_score || 0).toFixed(1)}%</span>
                            </div>
                            <div style="font-size:11px; color:#b45309; font-weight:600; margin-top:2px;">
                                Rules ${drekLord.rising_sign || ''} D3 Lagna • in ${drekLord.placed_sign || ''}
                            </div>
                            <div style="font-size:10px; color:#475569; margin-top:2px;">${drekLord.governs || ''}</div>
                        </div>

                        <div class="eval-master-card" style="border-left: 3px solid #16a34a; background:#f0fdf4;">
                            <div style="font-size:10px; text-transform:uppercase; color:#166534; font-weight:bold;">📜 Shadvarga Predominance</div>
                            <div style="font-size:12px; font-weight:bold; color:#14532d; margin-top:3px;">${pred.overall_status || 'Shadvarga Balance'}</div>
                            <div style="font-size:10px; color:#166534; margin-top:2px;">${pred.meaning || ''}</div>
                        </div>

                        ${moonPhaseCardHtml}
                    </div>
                `;
            }

            // Render Table Body
            const tbody = cell.querySelector('.planetary-eval-table tbody') || cell.querySelector('tbody');
            if (!tbody) return;
            tbody.innerHTML = '';

            const showTrailAll = cell.querySelector('.toggle-calc-trail')?.checked || false;
            const planetOrder = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"];
            const cellPrefix = cell.id || ('eval-' + Math.floor(Math.random() * 10000));

            planetOrder.forEach(p => {
                const data = planets[p];
                if (!data) return;

                const score = Number(data.net_scale_score || 0);
                const scoreSign = score >= 0 ? '+' : '';
                const exprClass = data.expression_class || 'mixed';
                const arch = data.archetype || {};
                const archClass = arch.title.includes('King') ? 'king' : (arch.title.includes('Dictator') ? 'dictator' : (arch.title.includes('Friend') ? 'friend' : 'bully'));

                // Tooltip for Shadvarga
                const s1 = data.step1_shadvarga || {};
                const vb = s1.varga_breakdown || {};
                let shadvargaTip = `<strong>${p} Shadvarga Breakdown (Avg: ${s1.average_dignity_pct}%)</strong><br>`;
                shadvargaTip += `• D1 Rashi: ${vb.D1?.sign || '-'} (${vb.D1?.dignity || '-'}, ${vb.D1?.score || 0}%)<br>`;
                shadvargaTip += `• D2 Hora: ${vb.D2?.sign || '-'} (${vb.D2?.dignity || '-'}, ${vb.D2?.score || 0}%)<br>`;
                shadvargaTip += `• D3 Drekkana: ${vb.D3?.sign || '-'} (${vb.D3?.dignity || '-'}, ${vb.D3?.score || 0}%)<br>`;
                shadvargaTip += `• D9 Navamsha: ${vb.D9?.sign || '-'} (${vb.D9?.dignity || '-'}, ${vb.D9?.score || 0}%)<br>`;
                shadvargaTip += `• D12 Dwadashamsha: ${vb.D12?.sign || '-'} (${vb.D12?.dignity || '-'}, ${vb.D12?.score || 0}%)<br>`;
                shadvargaTip += `• D30 Trimshamsha: ${vb.D30?.sign || '-'} (${vb.D30?.dignity || '-'}, ${vb.D30?.score || 0}%)<br>`;
                shadvargaTip += `<em>Centered Base Score: ${s1.base_centered_score >= 0 ? '+' : ''}${s1.base_centered_score}%</em>`;

                // Tooltip for Host Rescue
                const s2 = data.step2_host_rescue || {};
                let hostTip = `<strong>Host (Dispositor) Anchor: ${s2.host_planet || '-'}</strong><br>`;
                hostTip += `• Host Shadvarga Dignity: ${s2.host_dignity_pct || 0}%<br>`;
                hostTip += `• Status: ${s2.rescue_status || '-'} (${s2.bonus_pct >= 0 ? '+' : ''}${s2.bonus_pct || 0}%)<br>`;
                hostTip += `• ${s2.notes || ''}`;

                // Tooltip for Step 3: Conjunctions & Aspects (Partitioned)
                const EVAL_PLANET_GLYPHS = {
                    'Sun': '☉', 'Moon': '☽', 'Mars': '♂', 'Mercury': '☿',
                    'Jupiter': '♃', 'Venus': '♀', 'Saturn': '♄', 'Rahu': '☊', 'Ketu': '☋'
                };
                const s3 = data.step3_aspects || {};
                const conjList = s3.conjunctions || (s3.details ? s3.details.filter(d => (d.type || '').toLowerCase().includes('conjunction')) : []);
                const aspList = s3.aspects || (s3.details ? s3.details.filter(d => !(d.type || '').toLowerCase().includes('conjunction')) : []);

                let aspectTip = `<strong>Drishti & Conjunction Rays (Net: ${s3.net_aspect_pct >= 0 ? '+' : ''}${s3.net_aspect_pct || 0}%)</strong><br>`;

                if (conjList.length > 0) {
                    aspectTip += `<br><strong>Conjunctions (Co-occupants in the Same House):</strong><br>`;
                    conjList.forEach(c => {
                        const pName = c.planet || c.source || c.from_planet;
                        const glyph = EVAL_PLANET_GLYPHS[pName] ? `${EVAL_PLANET_GLYPHS[pName]} ` : '';
                        const degDiff = c.degree_diff !== undefined ? `${c.degree_diff}°` : '';
                        const orbStr = c.orb_band || c.type || '';
                        const distStr = degDiff ? `Distance ${degDiff} (${orbStr})` : orbStr;
                        aspectTip += `• ${glyph}${pName}: ${distStr} ➔ ${c.impact || ''}<br>`;
                    });
                }

                if (aspList.length > 0) {
                    aspectTip += `<br><strong>Aspects (Rays from Other Houses):</strong><br>`;
                    aspList.forEach(a => {
                        const pName = a.planet || a.source || a.from_planet;
                        const glyph = EVAL_PLANET_GLYPHS[pName] ? `${EVAL_PLANET_GLYPHS[pName]} ` : '';
                        const virStr = a.virupas !== undefined ? `${a.virupas} Virūpas` : `${a.power_pct || 0}%`;
                        aspectTip += `• ${glyph}${pName}: ${a.type} (${virStr}) ➔ ${a.impact || ''}<br>`;
                    });
                }

                if (conjList.length === 0 && aspList.length === 0) {
                    aspectTip += `• No significant incoming rays.<br>`;
                }

                // Tooltip for House Field
                const s4 = data.step4_house_field || {};
                let houseTip = `<strong>House Field: ${s4.house_num}th House</strong><br>`;
                houseTip += `• Type: ${s4.house_type || '-'}<br>`;
                if (s4.kendra_rank) houseTip += `• Rank: ${s4.kendra_rank}<br>`;
                if (s4.viparita_yoga) houseTip += `• Special Yoga: <strong>${s4.viparita_yoga}</strong><br>`;
                houseTip += `• Bonus: ${s4.bonus_pct >= 0 ? '+' : ''}${s4.bonus_pct || 0}%<br>`;
                if (s4.math_steps && s4.math_steps.length > 0) {
                    houseTip += `<br><strong>📐 Functional Dignity Formula:</strong><br>` +
                        s4.math_steps.map(st => `• ${st}`).join('<br>') +
                        `<br>➔ <code>${s4.math_formula || ''}</code><br>`;
                }
                houseTip += `• ${s4.notes || ''}`;

                // Tooltip for Strength
                const st = data.strength || {};
                let strTip = `<strong>Planetary Strength (Virya)</strong><br>`;
                strTip += `• Total Virupas: ${st.total_virupas || 0} V (Ratio: ${st.shadbala_ratio || 0}x required)<br>`;
                strTip += `• Level: ${st.strength_level || '-'}<br>`;
                if (st.motional_factors && st.motional_factors.length > 0) {
                    strTip += `• Motional Factors: ${st.motional_factors.join(', ')}<br>`;
                }

                // Archetype Tooltip
                const archTip = `<strong>Archetype: ${arch.title || '-'}</strong><br>• Dignity: ${arch.dignity_status || '-'}<br>• Strength: ${arch.strength_status || '-'}<br>• Meaning: ${arch.description || ''}`;

                const drawerId = `${cellPrefix}-drawer-${p.toLowerCase()}`;

                const tr = document.createElement('tr');
                tr.className = 'eval-planet-row';
                tr.dataset.planet = p;
                tr.setAttribute('onclick', `if (!event.target.closest('button, a, input')) togglePlanetEvalRow('${drawerId}')`);
                tr.style.cursor = 'pointer';
                tr.title = 'Click to toggle step-by-step mathematical formula';
                tr.innerHTML = `
                    <td style="font-weight:bold; color:#1a4a82; white-space:nowrap;">
                        <span style="font-size:14px;">${data.glyph || ''}</span> ${p}
                        <span style="font-size:10px; color:#64748b; display:block;">${data.sign || ''} ${data.longitude || 0}°</span>
                        ${p === 'Moon' && data.moon_phase ? `<span style="display:inline-block; margin-top:2px; font-size:9px; padding:1px 4px; border-radius:3px; background:${data.moon_phase.terrain_spectrum === 'bright_benefic' ? '#ecfdf5' : (data.moon_phase.terrain_spectrum === 'dark_malefic' ? '#fef2f2' : '#f8fafc')}; color:${data.moon_phase.terrain_spectrum === 'bright_benefic' ? '#065f46' : (data.moon_phase.terrain_spectrum === 'dark_malefic' ? '#991b1b' : '#475569')}; border:1px solid ${data.moon_phase.terrain_spectrum === 'bright_benefic' ? '#a7f3d0' : (data.moon_phase.terrain_spectrum === 'dark_malefic' ? '#fecaca' : '#cbd5e1')}; font-weight:600;">${data.moon_phase.badge || (data.moon_phase.is_waxing ? '🌔 Waxing' : '🌘 Waning') + ' ' + (data.moon_phase.illumination_pct || 0).toFixed(0) + '%'}</span>` : ''}
                    </td>
                    <td style="white-space:nowrap;">
                        <span class="eval-scale-badge ${exprClass}" title="Net Score on -100% to +100% continuous spectrum">
                            ${scoreSign}${score.toFixed(1)}%
                        </span>
                    </td>
                    <td style="font-size:11px; white-space:nowrap;">
                        <span style="font-weight:600; color:${exprClass === 'positive' ? '#166534' : (exprClass === 'negative' ? '#991b1b' : '#854d0e')};">
                            ${(data.expression_mode || '').split('(')[0].trim()}
                        </span>
                        <div style="font-size:9.5px; color:#64748b;">${exprClass === 'positive' ? 'Constructive' : (exprClass === 'negative' ? 'Disruptive' : 'Balanced')}</div>
                    </td>
                    <td class="tooltip-target" data-tooltip="${archTip}" style="cursor:help; white-space:nowrap;">
                        <span class="eval-quadrant-pill ${archClass}">
                            <span>${arch.icon || ''}</span> ${arch.title || '-'}
                        </span>
                    </td>
                    <td class="tooltip-target" data-tooltip="${shadvargaTip}" style="cursor:help; white-space:nowrap;">
                        <strong>${s1.average_dignity_pct || 0}%</strong>
                        <span style="font-size:9.5px; color:#64748b; display:block;">(${s1.base_centered_score >= 0 ? '+' : ''}${s1.base_centered_score || 0}%)</span>
                    </td>
                    <td class="tooltip-target" data-tooltip="${hostTip}" style="cursor:help; white-space:nowrap;">
                        <span>${s2.host_planet || '-'} (${s2.bonus_pct >= 0 ? '+' : ''}${s2.bonus_pct || 0}%)</span>
                        <span style="font-size:9.5px; color:${(s2.bonus_pct || 0) > 10 ? '#166534' : ((s2.bonus_pct || 0) < 0 ? '#991b1b' : '#64748b')}; display:block;">
                            ${(s2.rescue_status || '-').split('(')[0].trim()}
                        </span>
                    </td>
                    <td class="tooltip-target" data-tooltip="${aspectTip}" style="cursor:help; white-space:nowrap;">
                        <strong style="color:${(s3.net_aspect_pct || 0) > 0 ? '#166534' : ((s3.net_aspect_pct || 0) < 0 ? '#991b1b' : '#334155')};">
                            ${(s3.net_aspect_pct || 0) >= 0 ? '+' : ''}${s3.net_aspect_pct || 0}%
                        </strong>
                        <span style="font-size:9.5px; color:#64748b; display:block;">+${s3.benefic_rays_pct || 0}% / ${s3.malefic_pressure_pct || 0}%</span>
                    </td>
                    <td class="tooltip-target" data-tooltip="${houseTip}" style="cursor:help; white-space:nowrap;">
                        <span>H${s4.house_num || '-'} (${s4.bonus_pct >= 0 ? '+' : ''}${s4.bonus_pct || 0}%)</span>
                        ${s4.viparita_yoga ? `<span style="font-size:9px; background:#fef3c7; color:#92400e; padding:1px 3px; border-radius:3px; font-weight:bold; display:block;">${s4.viparita_yoga.split('(')[0].trim()}</span>` : `<span style="font-size:9.5px; color:#64748b; display:block;">${(s4.house_type || '-').split('(')[0].trim()}</span>`}
                    </td>
                    <td class="tooltip-target" data-tooltip="${strTip}" style="cursor:help; white-space:nowrap;">
                        <span>${st.total_virupas || 0} V</span>
                        <span style="font-size:9.5px; font-weight:600; color:${st.strength_level === 'High Strength' ? '#15803d' : '#b91c1c'}; display:block;">
                            ${st.shadbala_ratio || 0}x ${st.strength_level === 'High Strength' ? 'High' : 'Low'}
                        </span>
                    </td>
                    <td style="text-align:center; white-space:nowrap;">
                        <button type="button" class="btn-toggle-row-drawer" onclick="togglePlanetEvalRow('${drawerId}')" style="background:#f1f5f9; border:1px solid #cbd5e1; border-radius:4px; font-size:10.5px; padding:2px 7px; cursor:pointer; color:#334155;" title="Toggle Step-by-Step Mathematical Formula">
                            📐 Math
                        </button>
                    </td>
                `;

                tbody.appendChild(tr);

                // Calculation Trail Drawer Row
                const trail = data.calculation_trail || {};
                const trDrawer = document.createElement('tr');
                trDrawer.id = drawerId;
                trDrawer.className = 'eval-calc-drawer-row';
                trDrawer.style.display = showTrailAll ? 'table-row' : 'none';
                trDrawer.innerHTML = `
                    <td colspan="10" style="padding: 8px 14px; background: #fdfbf7; border-bottom: 2px solid #dcb594;">
                        <div class="eval-calc-drawer">
                            <div style="font-weight: bold; color: #1e293b; margin-bottom: 5px; display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:4px;">
                                <span style="font-size:12px;">📐 Step-by-Step Calculation for ${data.glyph || ''} ${p}:</span>
                                <span style="font-size:10px; background:#e2e8f0; color:#475569; padding:2px 6px; border-radius:3px;">Vic DiCara Continuous Diagnostic Scale</span>
                            </div>
                            <div style="background:#ffffff; border:1px solid #cbd5e1; border-radius:4px; padding:6px 10px; font-family:monospace; font-size:11.5px; color:#0f172a; margin-bottom:6px; overflow-x:auto;">
                                <strong>${trail.formula || ''}</strong>
                                ${s4.math_formula ? `<div style="font-size:10.5px; color:#2563eb; margin-top:4px;"><strong>Functional Dignity:</strong> ${s4.math_formula}</div>` : ''}
                            </div>
                            <div style="font-family:sans-serif; font-size:11px; color:#475569; white-space:pre-line; line-height:1.5;">
                                ${trail.human_readable || ''}
                            </div>
                        </div>
                    </td>
                `;
                tbody.appendChild(trDrawer);
            });
        }

        function togglePlanetEvalRow(drawerId) {
            const drawer = document.getElementById(drawerId);
            if (!drawer) return;
            drawer.style.display = (drawer.style.display === 'none' || !drawer.style.display) ? 'table-row' : 'none';
        }

        function togglePlanetaryEvalTrail(checkbox) {
            const container = checkbox.closest('.widget-content') || document;
            const drawers = container.querySelectorAll('.eval-calc-drawer-row');
            drawers.forEach(d => {
                d.style.display = checkbox.checked ? 'table-row' : 'none';
            });
        }



        function openFloatingPlanetaryEvaluation() {
            closeKalaMenu();
            const modal = document.getElementById('widgetMaximizeModal');
            const card = document.getElementById('widgetMaximizeCard');
            const titleEl = document.getElementById('widgetMaximizeModalTitle');
            const container = document.getElementById('widgetMaximizeContainer');
            if (!modal || !titleEl || !container || !currentChartData) return;

            resetFloatingWindowPosition();
            if (card) {
                const w = Math.min(1020, window.innerWidth - 40);
                const h = Math.min(700, window.innerHeight - 60);
                card.style.width = w + 'px';
                card.style.height = h + 'px';
                card.style.left = Math.max(20, Math.round((window.innerWidth - w) / 2)) + 'px';
                card.style.top = Math.max(30, Math.round((window.innerHeight - h) / 2)) + 'px';
            }

            setActiveFloatingNav('nav-btn-evaluation');
            const subjectName = (currentChartData.subject_info && currentChartData.subject_info.name) ? currentChartData.subject_info.name : 'Chart';
            titleEl.textContent = subjectName + " — Planetary Evaluation & Positive-Negative Scale";

            const tmpl = document.getElementById('tmpl-planetary-evaluation');
            if (tmpl) {
                container.innerHTML = '';
                container.appendChild(tmpl.content.cloneNode(true));
                updatePlanetaryEvaluationWidget(container);
            }

            modal.style.display = 'flex';
            document.body.style.overflow = 'hidden';
        }

// Register with WidgetRegistry
if (typeof window !== 'undefined' && window.widgetRegistry) {
    window.widgetRegistry.register('planetary-evaluation', {
        id: 'planetary-evaluation',
        title: 'Planetary Evaluation',
        icon: '🌟',
        category: 'Diagnostics',
        isScrollable: true,
        render: function(container, chartData, options) {
            updatePlanetaryEvaluationWidget(container, chartData);
        },
        onUpdate: function(cell, chartData) {
            updatePlanetaryEvaluationWidget(cell, chartData);
        }
    });
}

// Global exports
if (typeof window !== 'undefined') {
    window.updatePlanetaryEvaluationWidget = updatePlanetaryEvaluationWidget;
    window.togglePlanetEvalRow = togglePlanetEvalRow;
    window.togglePlanetaryEvalTrail = togglePlanetaryEvalTrail;
    window.openFloatingPlanetaryEvaluation = openFloatingPlanetaryEvaluation;
}
