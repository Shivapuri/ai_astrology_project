/**
 * Astra Varga Dignities Matrix Widget
 *
 * Implements:
 * 1. Ṣaḍvarga Weighted Matrix (Phaladīpikā 3.1–4 & Vic DiCara Methodology):
 *    - Canonical integer weights: D1: 2, D2: 1, D3: 1, D5 (D30): 1, D9: 2, D12: 1 (Divisor: 8)
 *    - Sign glyph + exact dignity score per cell
 *    - Bottom weighted total row (W) with Auspicious (≥50) vs Inauspicious (<50) indicators
 *    - Dispositor rescue annotations
 * 2. Ṣoḍaśavarga Complete 16-Harmonics Grid:
 *    - Comprehensive 16-division grid (D1 through D60) with sign glyphs, scores, and relationship tooltips
 */

function switchVargaDignitiesView(btn, viewName) {
    if (!btn) return;
    const widgetContent = btn.closest('#tab-varga-dignities') || btn.closest('.widget-content') || document;
    
    // Toggle active state on buttons
    const buttons = widgetContent.querySelectorAll('.varga-dignities-tab-btn');
    buttons.forEach(b => {
        if (b.dataset.view === viewName) {
            b.classList.add('active');
            b.style.background = '#4a3325';
            b.style.color = '#fffdfa';
        } else {
            b.classList.remove('active');
            b.style.background = 'transparent';
            b.style.color = '#4a3325';
        }
    });

    // Toggle panes
    const paneShadvarga = widgetContent.querySelector('#pane-shadvarga');
    const paneShodasha = widgetContent.querySelector('#pane-shodashavarga');
    
    if (paneShadvarga && paneShodasha) {
        if (viewName === 'shadvarga') {
            paneShadvarga.style.display = 'block';
            paneShodasha.style.display = 'none';
        } else {
            paneShadvarga.style.display = 'none';
            paneShodasha.style.display = 'block';
        }
    }

    try {
        localStorage.setItem('astra_varga_dignities_view', viewName);
    } catch (e) {}
}

function updateVargaDignitiesTable(cell, chartData) {
    const currentData = chartData || window.currentChartData;
    if (!currentData) return;

    const root = cell || document;
    const widgetContainers = cell
        ? [cell.querySelector('#tab-varga-dignities') || cell]
        : Array.from(document.querySelectorAll('#tab-varga-dignities, .grid-cell[data-widget="dignities"]'));

    if (widgetContainers.length === 0) return;

    const planets = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn'];

    function escapeTooltipAttr(str) {
        if (!str) return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/"/g, '&quot;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;');
    }

    function getDignityColor(score) {
        const s = Number(score || 0);
        if (s >= 90) return '#15803d'; // Green (Exalted, Moolatrikona, Own)
        if (s >= 70) return '#0d9488'; // Teal (Great Friend, Friend)
        if (s >= 50) return '#475569'; // Slate (Neutral)
        if (s >= 30) return '#d97706'; // Amber (Enemy)
        return '#dc2626';             // Red (Great Enemy, Debilitated, Inauspicious Horā)
    }

    function getZodiacGlyphHtml(signName) {
        if (typeof TableBuilder !== 'undefined' && TableBuilder.renderZodiacGlyph) {
            return TableBuilder.renderZodiacGlyph(signName);
        }
        if (typeof window !== 'undefined' && window.AstroCatalog) {
            const s = window.AstroCatalog.getSign(signName);
            if (s && s.glyph) {
                return `<span class="zodiac-line-glyph" style="font-family:var(--font-astro-glyphs); font-variant-emoji:text;">${s.glyph}</span>`;
            }
        }
        return signName ? signName.slice(0, 2) : '—';
    }

    function mapDigAbbrev(fullStr) {
        if (!fullStr) return 'N';
        const s = fullStr.toLowerCase();
        if (s.includes('exalt') || s.includes('uccha')) return 'EX';
        if (s.includes('debilitat') || s.includes('neecha')) return 'DB';
        if (s.includes('mool') || s.includes('mul')) return 'MT';
        if (s.includes('own') || s.includes('swak') || s.includes('svastha')) return 'OH';
        if (s.includes('great friend') || s.includes('adhi mitra')) return 'GF';
        if (s.includes('great enemy') || s.includes('adhi shatru')) return 'GE';
        if (s.includes('friend') || s.includes('mitra')) return 'F';
        if (s.includes('enemy') || s.includes('shatru')) return 'E';
        if (s.includes('neutral') || s.includes('sama')) return 'N';
        return 'N';
    }

    const vargaDescriptions = {
        'D1': 'Rāśi (Physical Existence & Baseline Life)',
        'D2': 'Horā (Wealth, Resources & Speech)',
        'D3': 'Drekkāṇa (Siblings, Courage & Vitality)',
        'D4': 'Chaturthāṁśa (Home, Fixed Property & Comfort)',
        'D7': 'Saptāṁśa (Children, Progeny & Creative Flow)',
        'D9': 'Navāṁśa (Dharma, Marriage, Inner Essence & Destiny)',
        'D10': 'Daśāṁśa (Career, Leadership & Social Impact)',
        'D12': 'Dvādaśāṁśa (Parents, Heritage & Ancestral Lineage)',
        'D16': 'Ṣoḍaśāṁśa (Vehicles, Pleasures & Heart Comfort)',
        'D20': 'Viṁśāṁśa (Spiritual Life, Devotion & Meditation)',
        'D24': 'Chaturviṁśāṁśa (Higher Education, Skill & Scholarship)',
        'D27': 'Saptaviṁśāṁśa (Subconscious Strengths & Vulnerabilities)',
        'D30': 'Triṁśāṁśa (Misfortune, Hidden Flaws & Health Trials)',
        'D40': 'Khavedāṁśa (Auspicious / Inauspicious Karmic Blessings)',
        'D45': 'Akṣavedāṁśa (Moral Character, Integrity & Purity)',
        'D60': 'Ṣaṣṭyāṁśa (Root Past-Life Karmas & Destiny Seeds)'
    };

    // Ṣaḍvarga Row Definitions (Phaladīpikā 3.1–4 & Vic DiCara Methodology)
    // Ṣaḍvarga Row Definitions (Phaladīpikā 3.1–4 & Vic DiCara Methodology)
    // Note: D5 (Triṁśāṁśa 5 Bounds) sits in sequence between D3 and D9
    const shadvargaRowsDef = [
        { code: 'D1',  displayCode: 'D1', weight: 2, title: 'Rāśi (Physical Baseline)', isPillar: true },
        { code: 'D2',  displayCode: 'D2', weight: 1, title: 'Horā (Solar & Lunar Wealth Chambers)', isPillar: false },
        { code: 'D3',  displayCode: 'D3', weight: 1, title: 'Drekkāṇa (Decanate Initiative)', isPillar: false },
        { code: 'D30', displayCode: 'D5', weight: 1, title: 'Triṁśāṁśa (5 Planetary Bounds / D30)', isPillar: false },
        { code: 'D9',  displayCode: 'D9', weight: 2, title: 'Navāṁśa (Soul Essence & Destiny)', isPillar: true },
        { code: 'D12', displayCode: 'D12', weight: 1, title: 'Dvādaśāṁśa (Ancestral Lineage)', isPillar: false }
    ];

    const shodashavargaList = [
        'D1', 'D2', 'D3', 'D4', 'D7', 'D9', 'D10', 'D12',
        'D16', 'D20', 'D24', 'D27', 'D30', 'D40', 'D45', 'D60'
    ];

    // Master Lagna Lords Detection (D1 Lagneśa, D3 Drekkāṇa Lord, D9 Navāṁśa Lord)
    const signLords = {
        'Aries': 'Mars', 'Taurus': 'Venus', 'Gemini': 'Mercury', 'Cancer': 'Moon',
        'Leo': 'Sun', 'Virgo': 'Mercury', 'Libra': 'Venus', 'Scorpio': 'Mars',
        'Sagittarius': 'Jupiter', 'Capricorn': 'Saturn', 'Aquarius': 'Saturn', 'Pisces': 'Jupiter'
    };

    const peData = currentData.planetary_evaluation || {};
    const masterLords = (peData && peData.summary && peData.summary.master_lords) || {};

    const d1Lagna = (currentData.vargas && currentData.vargas.D1 && currentData.vargas.D1.lagna) || currentData.lagna || {};
    const d1LagnaSign = d1Lagna.sign || '';
    const lagnaLordPlanet = (masterLords.lagna_lord && masterLords.lagna_lord.planet)
        || d1Lagna.lord
        || signLords[d1LagnaSign] || '';

    const d3Lagna = (currentData.vargas && currentData.vargas.D3 && currentData.vargas.D3.lagna) || {};
    const d3LagnaSign = d3Lagna.sign || '';
    const drekkanaLordPlanet = (masterLords.drekkana_lord && masterLords.drekkana_lord.planet)
        || d3Lagna.lord
        || signLords[d3LagnaSign] || '';

    const d9Lagna = (currentData.vargas && currentData.vargas.D9 && currentData.vargas.D9.lagna) || {};
    const d9LagnaSign = d9Lagna.sign || '';
    const navamshaLordPlanet = (masterLords.navamsha_lord && masterLords.navamsha_lord.planet)
        || d9Lagna.lord
        || signLords[d9LagnaSign] || '';

    function getPlanetLordBadges(planetName) {
        const badges = [];
        if (planetName === lagnaLordPlanet) {
            badges.push({
                letter: 'L',
                num: '1',
                title: 'Lagneśa (D1 Lagna Lord)',
                desc: `Rules D1 Ascendant (${d1LagnaSign || '--'}). Master of physical vitality, constitution & life direction.`,
                cls: 'lord-l'
            });
        }
        if (planetName === drekkanaLordPlanet) {
            badges.push({
                letter: 'D',
                num: '3',
                title: 'Drekkāṇa Lord (D3 Lagna Lord)',
                desc: `Rules D3 Ascendant (${d3LagnaSign || '--'}). Master of bodily courage, energy & worldly drive.`,
                cls: 'lord-d'
            });
        }
        if (planetName === navamshaLordPlanet) {
            badges.push({
                letter: 'N',
                num: '9',
                title: 'Navāṁśa Lord (D9 Lagna Lord)',
                desc: `Rules D9 Ascendant (${d9LagnaSign || '--'}). Master of soul dharma, inner contentment & spiritual fortune.`,
                cls: 'lord-n'
            });
        }
        return badges;
    }

    widgetContainers.forEach(container => {
        // ---------------------------------------------------------------------
        // 1. Render Ṣaḍvarga Weighted View (DiCara Table Matching Screenshot)
        // ---------------------------------------------------------------------
        const shadvargaTbody = container.querySelector('.shadvarga-weighted-tbody');
        if (shadvargaTbody) {
            shadvargaTbody.innerHTML = '';
            const planetWeightedSums = { Sun: 0, Moon: 0, Mars: 0, Mercury: 0, Jupiter: 0, Venus: 0, Saturn: 0 };
            const pePlanets = (currentData.planetary_evaluation && currentData.planetary_evaluation.planets) || {};

            // Update column header badges for master lords
            planets.forEach(p => {
                const th = container.querySelector(`.shadvarga-weighted-table th[data-planet="${p}"]`);
                if (th) {
                    const lordBadges = getPlanetLordBadges(p);
                    const tagsContainer = th.querySelector('.th-lord-tags');
                    if (tagsContainer) {
                        tagsContainer.innerHTML = lordBadges.map(b => `
                            <span class="shadvarga-lord-badge ${b.cls} tooltip-target" data-tooltip="<strong>${b.title}</strong><br>${escapeTooltipAttr(b.desc)}" style="cursor:help;">${b.letter}</span>
                        `).join('');
                    }
                }
            });

            shadvargaRowsDef.forEach(rowDef => {
                const tr = document.createElement('tr');
                tr.style.cursor = 'pointer';
                if (rowDef.isPillar) {
                    tr.classList.add('shadvarga-row-pillar');
                }
                tr.onclick = function() {
                    const chartCell = (window.currentActiveCell && window.currentActiveCell.dataset.widget === 'chart')
                        ? window.currentActiveCell
                        : document.querySelector('.grid-cell[data-widget="chart"]');
                    if (chartCell) {
                        const select = chartCell.querySelector('.varga-select');
                        if (select) {
                            select.value = rowDef.code;
                            if (typeof window.updateWidget === 'function') {
                                window.updateWidget(chartCell);
                            }
                        }
                    }
                };

                const wtCellBg = rowDef.isPillar ? '#e0f2fe' : '#faf6ee';
                const wtCellColor = rowDef.isPillar ? '#0284c7' : '#4a3325';
                const lblCellBg = rowDef.isPillar ? '#f8fafc' : '#faf6ee';
                const lblCellColor = rowDef.isPillar ? '#0f172a' : '#4a3325';

                let rowHtml = `
                    <td style="font-weight: 800; color: ${wtCellColor}; background: ${wtCellBg}; padding: 6px 4px; font-size: ${rowDef.isPillar ? '13.5px' : '13px'};">${rowDef.weight}</td>
                    <td style="font-weight: 800; color: ${lblCellColor}; background: ${lblCellBg}; padding: 6px 6px; text-align: left; font-size: 12.5px;">
                        <span class="tooltip-target" data-tooltip="<strong>${rowDef.displayCode} (${rowDef.code}) — ${rowDef.title}</strong><br>• Canonical Weight: <strong>${rowDef.weight}</strong><br>Click to display this chart in the primary view." style="cursor:help;">
                            ${rowDef.displayCode} ${rowDef.isPillar ? '<span class="micro-tag" style="background:#e0f2fe; color:#0369a1; font-weight:800; font-size:12px; padding:1px 3px; border-radius:2px; margin-left:3px;">2× Pillar</span>' : ''}
                        </span>
                    </td>
                `;

                planets.forEach(p => {
                    const pEval = pePlanets[p] || {};
                    const step1 = pEval.step1_shadvarga || {};
                    const vb = step1.varga_breakdown || {};
                    const vEntry = vb[rowDef.code] || {};

                    const vData = (currentData.vargas && currentData.vargas[rowDef.code]) ? currentData.vargas[rowDef.code] : null;
                    const pData = (vData && vData.grahas) ? vData.grahas[p] : null;
                    const signName = vEntry.sign || (pData && pData.sign) || '—';
                    const score = (vEntry.score !== undefined) ? Number(vEntry.score) : 50.0;
                    const dignityName = vEntry.dignity || (pData && pData.dignity) || 'Neutral';
                    const ruler = vEntry.ruler || (pData && pData.ruler) || (pData && pData.dignity_breakdown && pData.dignity_breakdown.sign_lord) || '—';

                    planetWeightedSums[p] += score * rowDef.weight;

                    const glyphHtml = getZodiacGlyphHtml(signName);
                    const col = getDignityColor(score);
                    const tip = `<strong>${p} in ${rowDef.displayCode} (${signName})</strong><br>• <strong>Dignity:</strong> ${dignityName}<br>• <strong>Score:</strong> ${score.toFixed(0)}%<br>• <strong>Division Ruler:</strong> ${ruler}<br>• <strong>Weight Multiplier:</strong> ${rowDef.weight}x (${rowDef.title})`;
                    const cellBg = rowDef.isPillar ? '#f8fafc' : 'transparent';

                    rowHtml += `
                        <td style="padding: 6px 4px; border-right: 1px solid var(--border-subtle, #e2d7c3); border-bottom: 1px solid var(--border-subtle, #e2d7c3); font-variant-numeric: tabular-nums; background: ${cellBg};">
                            <div class="tooltip-target shadvarga-cell-content" data-tooltip="${escapeTooltipAttr(tip)}" style="cursor:help; font-weight: ${rowDef.isPillar ? '800' : '500'};">
                                ${glyphHtml}
                                <span style="font-weight: ${rowDef.isPillar ? '800' : '700'}; font-size: 13px; color: ${col};">${score.toFixed(0)}</span>
                            </div>
                        </td>
                    `;
                });

                tr.innerHTML = rowHtml;
                shadvargaTbody.appendChild(tr);
            });

            // -----------------------------------------------------------------
            // Summary Bottom Row (W: Weighted Dignity with Divisor 8)
            // -----------------------------------------------------------------
            const totalTr = document.createElement('tr');
            totalTr.className = 'weighted-total-row';
            totalTr.style.background = 'var(--bg-surface-alt, #f7f3eb)';
            totalTr.style.borderTop = '2px solid var(--border-strong, #cbd5e1)';

            let totalHtml = `
                <td style="font-weight: 800; font-size: 13.5px; color: #4a3325; background: #eee5d3; padding: 7px 4px;">W</td>
                <td style="font-weight: 800; font-size: 12.5px; color: #4a3325; background: #eee5d3; padding: 7px 6px; text-align: left;">
                    <span class="tooltip-target" data-tooltip="<strong>Weighted Ṣaḍvarga Dignity (Divisor: 8)</strong><br>Formula: (D1×2 + D2×1 + D3×1 + D5×1 + D9×2 + D12×1) ÷ 8<br>• Blue Badge (≥50): Indicates long-life, flourishing, and worldly expansion.<br>• Pink Badge (&lt;50): Indicates foundational vulnerability requiring dispositor rescue." style="cursor:help;">
                        Weighted
                    </span>
                </td>
            `;

            planets.forEach(p => {
                const weightedVal = Math.round(planetWeightedSums[p] / 8.0);
                const isHigh = weightedVal >= 50;
                const badgeClass = isHigh ? 'high' : 'low';
                const tip = `<strong>${p} Weighted Ṣaḍvarga: ${weightedVal}%</strong><br>• Raw Weighted Sum: ${planetWeightedSums[p].toFixed(1)} / 800<br>• Status: ${isHigh ? 'High Dignity (Long-Life & Prosperity)' : 'Vulnerability (Requires Dispositor Support)'}`;
                const lordBadges = getPlanetLordBadges(p);
                const lordBadgesHtml = lordBadges.length > 0 ? `
                    <div class="shadvarga-lord-badges-wrap" style="display:flex; gap:2px; justify-content:center; align-items:center; margin-top:2px;">
                        ${lordBadges.map(b => `<span class="shadvarga-lord-badge ${b.cls} tooltip-target" data-tooltip="<strong>${b.title}</strong><br>${escapeTooltipAttr(b.desc)}" style="cursor:help;">${b.letter}</span>`).join('')}
                    </div>
                ` : '';

                totalHtml += `
                    <td style="padding: 5px 4px; border-right: 1px solid var(--border-subtle, #e2d7c3);">
                        <div class="tooltip-target" data-tooltip="${escapeTooltipAttr(tip)}" style="display:flex; flex-direction:column; justify-content:center; align-items:center; gap:2px; cursor:help;">
                            <span class="shadvarga-score-badge ${badgeClass}">${weightedVal}</span>
                            ${lordBadgesHtml}
                        </div>
                    </td>
                `;
            });

            totalTr.innerHTML = totalHtml;
            shadvargaTbody.appendChild(totalTr);
        }

        // ---------------------------------------------------------------------
        // 2. Render Ṣoḍaśavarga Complete 16-Harmonics Grid
        // ---------------------------------------------------------------------
        const shodashaTbody = container.querySelector('.shodashavarga-tbody') || container.querySelector('#vargaDignitiesTable tbody');
        if (shodashaTbody) {
            shodashaTbody.innerHTML = '';

            shodashavargaList.forEach(v => {
                const tr = document.createElement('tr');
                tr.style.cursor = 'pointer';
                tr.onclick = function() {
                    const chartCell = (window.currentActiveCell && window.currentActiveCell.dataset.widget === 'chart')
                        ? window.currentActiveCell
                        : document.querySelector('.grid-cell[data-widget="chart"]');
                    if (chartCell) {
                        const select = chartCell.querySelector('.varga-select');
                        if (select) {
                            select.value = v;
                            if (typeof window.updateWidget === 'function') {
                                window.updateWidget(chartCell);
                            }
                        }
                    }
                };

                const vDesc = vargaDescriptions[v] || v;
                let html = `
                    <td class="tooltip-target" data-tooltip="<strong>${v} — ${vDesc}</strong><br>Click to display this harmonic chart in the primary view." style="text-align:left; padding:6px 8px; font-weight:700; color:var(--text-heading, #4a3325); cursor:help; background:#faf6ee;">
                        ${v} <span style="font-weight:400; font-size:12px; color:var(--text-muted);">${v === 'D1' ? '(Rāśi)' : (v === 'D9' ? '(Navāṁśa)' : '')}</span>
                    </td>
                `;

                const vData = (currentData.vargas && currentData.vargas[v]) ? currentData.vargas[v] : null;
                const vDignities = (currentData.dignities && currentData.dignities.varga_dignities) ? currentData.dignities.varga_dignities[v] : null;

                planets.forEach(p => {
                    let digStr = '';
                    let pSign = '';
                    let d = (vDignities && vDignities[p])
                        || (vData && vData.grahas && vData.grahas[p] && vData.grahas[p].dignity_breakdown)
                        || null;

                    if (d) {
                        digStr = d.final_dignity || d.dignity || '';
                        pSign = (vData && vData.grahas && vData.grahas[p]) ? vData.grahas[p].sign : (d.sign || '');
                    }

                    const abbrev = mapDigAbbrev(digStr);
                    const glyphHtml = getZodiacGlyphHtml(pSign);
                    const color = (abbrev === 'EX' || abbrev === 'MT' || abbrev === 'OH')
                        ? '#15803d'
                        : (abbrev === 'GF' || abbrev === 'F')
                            ? '#0d9488'
                            : (abbrev === 'DB' || abbrev === 'GE')
                                ? '#dc2626'
                                : (abbrev === 'E')
                                    ? '#d97706'
                                    : '#475569';

                    const tip = `<strong>${p} in ${v} (${pSign || '—'})</strong><br>• <strong>Dignity:</strong> ${digStr || 'Neutral'} (${abbrev})<br>• <strong>Host Lord:</strong> ${(d && d.sign_lord) || '—'}<br>• <strong>Compound Bond:</strong> ${(d && d.compound_relationship) || '—'}`;

                    html += `
                        <td style="padding: 6px 4px; border-right: 1px solid var(--border-subtle, #e2d7c3); border-bottom: 1px solid var(--border-subtle, #e2d7c3); font-variant-numeric: tabular-nums;">
                            <div class="tooltip-target" data-tooltip="${escapeTooltipAttr(tip)}" style="display:flex; justify-content:center; align-items:center; gap:4px; cursor:help;">
                                ${glyphHtml}
                                <span style="font-weight:700; font-size:12.5px; color:${color};">${abbrev}</span>
                            </div>
                        </td>
                    `;
                });

                tr.innerHTML = html;
                shodashaTbody.appendChild(tr);
            });
        }
    });

    // Check saved view preference
    try {
        const savedView = localStorage.getItem('astra_varga_dignities_view');
        if (savedView) {
            const activeBtn = document.querySelector(`.varga-dignities-tab-btn[data-view="${savedView}"]`);
            if (activeBtn) switchVargaDignitiesView(activeBtn, savedView);
        }
    } catch (e) {}
}

// Attach globally for browser use
if (typeof window !== 'undefined') {
    window.switchVargaDignitiesView = switchVargaDignitiesView;
    window.updateVargaDignitiesTable = updateVargaDignitiesTable;

    // Register with WidgetRegistry
    if (window.widgetRegistry) {
        window.widgetRegistry.register('dignities', {
            id: 'dignities',
            title: 'Planetary Dignities (Vargas)',
            icon: '',
            category: 'Dignity',
            render: function(container, chartData, options) {
                updateVargaDignitiesTable(container, chartData);
            },
            onUpdate: function(cell, chartData) {
                updateVargaDignitiesTable(cell, chartData);
            }
        });
    }
}
