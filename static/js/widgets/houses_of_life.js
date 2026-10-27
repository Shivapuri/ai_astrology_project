/**
 * Astra Stage 4: Vic DiCara's "Houses of Life" Diagnostic Cockpit
 * (Phaladīpikā Chapter 15 Evaluation System)
 * 
 * Complies with static/GEMINI.md & ADR-006:
 * - Strict 12px Font Floor
 * - Monochrome Unicode glyphs (\uFE0E) via STIX Two Math font stack
 * - Anti-Pill & De-Badged clean tabular numerals
 * - Zero consumer emojis; semantic CSS micro-dots and square micro-tags
 * - Responsive Dual-Mode Layout: Side-by-side split in wide cells / maximized view,
 *   seamless tabbed receipt drilldown in compact cells with back button & prev/next stepper
 * - Diverging 12-Bhāva Vertical Skyline Strip, Live Architectural Audit Sheet with SVG 30° strip,
 *   7-Graha Operational Ledger, and Stage 3 vs Stage 4 Concordance
 */

(function() {
    'use strict';

    // Fallback sign & planet catalogs if AstroCatalog is unavailable
    const SIGN_GLYPHS = {
        'Aries': '♈︎\uFE0E', 'Taurus': '♉︎\uFE0E', 'Gemini': '♊︎\uFE0E', 'Cancer': '♋︎\uFE0E',
        'Leo': '♌︎\uFE0E', 'Virgo': '♍︎\uFE0E', 'Libra': '♎︎\uFE0E', 'Scorpio': '♏︎\uFE0E',
        'Sagittarius': '♐︎\uFE0E', 'Capricorn': '♑︎\uFE0E', 'Aquarius': '♒︎\uFE0E', 'Pisces': '♓︎\uFE0E'
    };

    const PLANET_GLYPHS = {
        'Sun': '☉\uFE0E', 'Moon': '☽\uFE0E', 'Mars': '♂\uFE0E', 'Mercury': '☿\uFE0E',
        'Jupiter': '♃\uFE0E', 'Venus': '♀\uFE0E', 'Saturn': '♄\uFE0E',
        'Rahu': '☊\uFE0E', 'Ketu': '☋\uFE0E', 'Lagna': 'Asc'
    };

    function getSignGlyph(name) {
        if (window.AstroCatalog && window.AstroCatalog.signs) {
            const s = window.AstroCatalog.signs.find(x => x.name === name);
            if (s && s.glyph) return s.glyph;
        }
        return SIGN_GLYPHS[name] || '';
    }

    function getPlanetGlyph(name) {
        if (window.AstroCatalog && window.AstroCatalog.planets && window.AstroCatalog.planets[name]) {
            return window.AstroCatalog.planets[name].glyph;
        }
        return PLANET_GLYPHS[name] || name;
    }

    function formatDegMin(degFloat) {
        if (degFloat === undefined || degFloat === null || isNaN(degFloat)) return '--';
        const d = Math.floor(degFloat);
        const m = Math.round((degFloat - d) * 60);
        return `${d}°${String(m).padStart(2, '0')}'`;
    }

    function getTierDotHtml(classicalTier) {
        const tier = (classicalTier || '').toLowerCase();
        if (tier.includes('puṣṭa') || tier.includes('pusta')) {
            return '<span class="status-indicator" style="display:inline-block; width:6px; height:6px; border-radius:50%; background:var(--status-benefic-dark, #15803d); margin-right:5px; vertical-align:middle;"></span>';
        } else if (tier.includes('hīna') || tier.includes('hina')) {
            return '<span class="status-indicator" style="display:inline-block; width:6px; height:6px; border-radius:50%; background:var(--status-malefic-dark, #b91c1c); margin-right:5px; vertical-align:middle;"></span>';
        }
        return '<span class="status-indicator" style="display:inline-block; width:6px; height:6px; border-radius:50%; background:var(--text-subtle, #8c7b64); margin-right:5px; vertical-align:middle;"></span>';
    }

    function getScoreColor(val) {
        if (val >= 25.0) return 'var(--status-benefic-dark, #15803d)';
        if (val <= -20.1) return 'var(--status-malefic-dark, #b91c1c)';
        return 'var(--text-heading, #4a3325)';
    }

    function formatComponentCell(val) {
        if (val === null || val === undefined) {
            return '<span style="color:var(--text-subtle, #9a8a78);">—</span>';
        }
        if (Math.abs(val) < 0.05) {
            return '<span style="color:var(--text-subtle, #9a8a78);">—</span>';
        }
        if (val < 0) {
            return `<span style="color:var(--status-malefic-dark, #b91c1c);">${val.toFixed(1)}</span>`;
        }
        return `<span style="color:var(--text-primary, #3d312a);">+${val.toFixed(1)}</span>`;
    }

    // State per container
    const _selectedHouseState = new WeakMap();
    const _activeViewState = new WeakMap();
    const _resizeObservers = new WeakMap();

    function updateHousesOfLifeWidget(container, chartData) {
        const currentData = chartData || window.currentChartData;
        const root = container || document;
        if (!currentData) return;

        const hol = currentData.houses_of_life;
        if (!hol) return;

        // Initialize state
        if (!_selectedHouseState.has(root)) {
            _selectedHouseState.set(root, 1);
        }
        if (!_activeViewState.has(root)) {
            _activeViewState.set(root, 'matrix');
        }
        const selectedHouse = _selectedHouseState.get(root) || 1;

        // 1. Setup Tab Switching & Controls
        setupTabSwitching(root, hol);

        // 2. Setup Responsive Resize Observer
        setupResponsiveObserver(root);

        // 3. Render Zone 1: Executive Horizon Ribbon
        renderExecutiveHorizon(root, hol);

        // 4. Render Zone 2: 12-House Quantitative Matrix Table
        renderMatrixTable(root, hol, currentData);

        // 5. Render Zone 3: Interactive Live Receipt Inspector
        renderReceiptInspector(root, hol, selectedHouse);

        // 6. Render Zone 4: 7-Graha Operational Ledger
        renderPlanetsTable(root, hol);

        // 7. Render Zone 5: Stage 3 vs Stage 4 Concordance
        renderConcordanceTable(root, hol, currentData);

        // 8. Apply active view layout according to container width
        applyViewLayout(root);
    }

    function setupResponsiveObserver(root) {
        const widgetRoot = root.classList && root.classList.contains('widget-houses-of-life') ? root : root.querySelector('.widget-houses-of-life');
        const target = widgetRoot || root;
        if (!target || !window.ResizeObserver) return;

        if (_resizeObservers.has(target)) return;

        const observer = new ResizeObserver(() => {
            applyViewLayout(root);
        });
        observer.observe(target);
        _resizeObservers.set(target, observer);
    }

    function applyViewLayout(root) {
        const widgetRoot = root.classList && root.classList.contains('widget-houses-of-life') ? root : root.querySelector('.widget-houses-of-life');
        const target = widgetRoot || root;
        const width = target.clientWidth || 600;
        const isWide = width >= 860;

        if (isWide) {
            target.classList.add('hol-wide');
            target.classList.remove('hol-compact');
        } else {
            target.classList.add('hol-compact');
            target.classList.remove('hol-wide');
        }

        const activeView = _activeViewState.get(root) || 'matrix';
        const selectedHouse = _selectedHouseState.get(root) || 1;

        // Update toolbar tab buttons
        const switcher = root.querySelector('.hol-view-switcher');
        if (switcher) {
            const btns = switcher.querySelectorAll('.hol-tab-btn');
            btns.forEach(b => {
                const view = b.dataset.view;
                let isActive = (view === activeView);
                if (isWide && activeView === 'receipt' && view === 'matrix') {
                    isActive = true; // In wide mode, matrix tab displays both table and receipt
                }

                if (isActive) {
                    b.classList.add('active');
                    b.style.background = 'var(--bg-surface-muted, #eee5d3)';
                    b.style.color = 'var(--text-heading, #4a3325)';
                } else {
                    b.classList.remove('active');
                    b.style.background = 'transparent';
                    b.style.color = 'var(--text-muted, #6b5a4b)';
                }
            });

            // Update badge in receipt tab
            const tabBadge = switcher.querySelector('.hol-tab-house-badge');
            if (tabBadge) {
                tabBadge.textContent = `H${selectedHouse}`;
            }
        }

        // Panels
        const matrixPanel = root.querySelector('.hol-matrix-panel');
        const matrixLeft = root.querySelector('.hol-matrix-left');
        const receiptRight = root.querySelector('.hol-receipt-right');
        const planetsPanel = root.querySelector('.hol-planets-panel');
        const concordancePanel = root.querySelector('.hol-concordance-panel');
        const backBtn = root.querySelector('.hol-btn-back-to-matrix');

        if (activeView === 'planets') {
            if (matrixPanel) matrixPanel.style.display = 'none';
            if (planetsPanel) planetsPanel.style.display = 'flex';
            if (concordancePanel) concordancePanel.style.display = 'none';
        } else if (activeView === 'concordance') {
            if (matrixPanel) matrixPanel.style.display = 'none';
            if (planetsPanel) planetsPanel.style.display = 'none';
            if (concordancePanel) concordancePanel.style.display = 'flex';
        } else {
            // matrix or receipt view
            if (planetsPanel) planetsPanel.style.display = 'none';
            if (concordancePanel) concordancePanel.style.display = 'none';
            if (matrixPanel) matrixPanel.style.display = 'flex';

            if (isWide) {
                // Dual-Pane Split Layout
                if (matrixLeft) {
                    matrixLeft.style.display = 'flex';
                    matrixLeft.style.flex = '3';
                }
                if (receiptRight) {
                    receiptRight.style.display = 'flex';
                    receiptRight.style.flex = '2';
                }
                if (backBtn) backBtn.style.display = 'none';
            } else {
                // Compact Single-Pane Mode
                if (activeView === 'receipt') {
                    if (matrixLeft) matrixLeft.style.display = 'none';
                    if (receiptRight) {
                        receiptRight.style.display = 'flex';
                        receiptRight.style.flex = '1';
                    }
                    if (backBtn) backBtn.style.display = 'inline-flex';
                } else {
                    // matrix table
                    if (matrixLeft) {
                        matrixLeft.style.display = 'flex';
                        matrixLeft.style.flex = '1';
                    }
                    if (receiptRight) receiptRight.style.display = 'none';
                    if (backBtn) backBtn.style.display = 'none';
                }
            }
        }
    }

    function setupTabSwitching(root, hol) {
        const switcher = root.querySelector('.hol-view-switcher');
        if (switcher && switcher.dataset.bound !== 'true') {
            switcher.dataset.bound = 'true';
            const btns = switcher.querySelectorAll('.hol-tab-btn');
            btns.forEach(btn => {
                btn.addEventListener('click', (e) => {
                    e.preventDefault();
                    const targetView = btn.dataset.view;
                    _activeViewState.set(root, targetView);
                    applyViewLayout(root);
                });
            });
        }

        // Back to Matrix Button in Receipt Inspector
        const backBtn = root.querySelector('.hol-btn-back-to-matrix');
        if (backBtn && backBtn.dataset.bound !== 'true') {
            backBtn.dataset.bound = 'true';
            backBtn.addEventListener('click', (e) => {
                e.preventDefault();
                _activeViewState.set(root, 'matrix');
                applyViewLayout(root);
            });
        }

        // Next / Prev House Steppers in Receipt Inspector
        const prevBtn = root.querySelector('.hol-receipt-prev-btn');
        const nextBtn = root.querySelector('.hol-receipt-next-btn');

        if (prevBtn && prevBtn.dataset.bound !== 'true') {
            prevBtn.dataset.bound = 'true';
            prevBtn.addEventListener('click', (e) => {
                e.preventDefault();
                let cur = _selectedHouseState.get(root) || 1;
                cur = (cur === 1) ? 12 : (cur - 1);
                selectHouse(root, hol, cur, false);
            });
        }

        if (nextBtn && nextBtn.dataset.bound !== 'true') {
            nextBtn.dataset.bound = 'true';
            nextBtn.addEventListener('click', (e) => {
                e.preventDefault();
                let cur = _selectedHouseState.get(root) || 1;
                cur = (cur === 12) ? 1 : (cur + 1);
                selectHouse(root, hol, cur, false);
            });
        }
    }

    function selectHouse(root, hol, houseNum, switchTabIfCompact = true) {
        _selectedHouseState.set(root, houseNum);

        const widgetRoot = root.classList && root.classList.contains('widget-houses-of-life') ? root : root.querySelector('.widget-houses-of-life');
        const target = widgetRoot || root;
        const width = target.clientWidth || 600;
        const isWide = width >= 860;

        if (!isWide && switchTabIfCompact) {
            _activeViewState.set(root, 'receipt');
        }

        renderReceiptInspector(root, hol, houseNum);
        highlightActiveRow(root, houseNum);
        applyViewLayout(root);
    }

    function renderExecutiveHorizon(root, hol) {
        const meta = hol.metadata || {};
        const ascSign = meta.ascendant_sign || '--';
        const ascGlyph = getSignGlyph(ascSign);
        const ascDeg = formatDegMin(meta.ascendant_degree);

        const ascAnchorEl = root.querySelector('.hol-asc-anchor');
        if (ascAnchorEl) {
            ascAnchorEl.innerHTML = `<span style="font-family:var(--font-astro-glyphs); margin-right:2px;">${ascGlyph}</span>${ascSign} ${ascDeg}`;
        }

        const rankings = hol.summary_rankings || {};
        const meanScore = rankings.composite_mean_score;
        const meanEl = root.querySelector('.hol-mean-score');
        if (meanEl) {
            meanEl.textContent = meanScore !== undefined ? `${meanScore >= 0 ? '+' : ''}${meanScore.toFixed(1)}` : '--';
        }

        const topH = rankings.top_flourishing_houses || [];
        const botH = rankings.most_challenged_houses || [];

        const topEl = root.querySelector('.hol-top-flourishing');
        if (topEl) {
            topEl.textContent = topH.map(h => `H${h}`).join(' · ') || '--';
        }

        const botEl = root.querySelector('.hol-most-challenged');
        if (botEl) {
            botEl.textContent = botH.map(h => `H${h}`).join(' · ') || '--';
        }

        // Render 12-Column Vertical Diverging Skyline
        const skylineGrid = root.querySelector('.hol-skyline-grid') || root.querySelector('.hol-bars-grid');
        if (!skylineGrid) return;
        skylineGrid.innerHTML = '';

        const houses = hol.houses || {};
        const selectedHouse = _selectedHouseState.get(root) || 1;

        for (let h = 1; h <= 12; h++) {
            const hData = houses[String(h)] || {};
            const synth = hData.synthesis || {};
            const score = synth.composite_score !== undefined ? synth.composite_score : 0.0;
            const sign = hData.sign || '';
            const sGlyph = getSignGlyph(sign);

            // Scale height percentage from baseline (0 to 100 max)
            const clamped = Math.max(-100, Math.min(100, score));
            const barHeightPct = Math.max(4, (Math.abs(clamped) / 100.0) * 95);

            const isPositive = clamped >= 0;
            const barColor = isPositive ? 'var(--status-benefic-dark, #15803d)' : 'var(--status-malefic-dark, #b91c1c)';
            const isSelected = (h === selectedHouse);

            const col = document.createElement('div');
            col.className = `hol-skyline-col ${isSelected ? 'active-col' : ''}`;
            col.dataset.house = String(h);
            col.style.cssText = `display:flex; flex-direction:column; align-items:center; justify-content:space-between; height:100%; cursor:pointer; padding:2px 1px; border-radius:3px; position:relative; transition:background 0.15s ease; ${isSelected ? 'background:var(--bg-surface, #fffdfa); box-shadow:0 1px 3px rgba(0,0,0,0.08);' : 'background:transparent;'}`;
            col.title = `House ${h} (${sign}): ${score >= 0 ? '+' : ''}${score.toFixed(1)} (${synth.classical_tier || ''})`;

            col.innerHTML = `
                <div style="font-size:12px; font-weight:700; line-height:1; color:var(--text-heading); display:flex; align-items:center; gap:2px;">
                    <span>H${h}</span>
                    <span style="font-family:var(--font-astro-glyphs); font-size:12px;">${sGlyph}</span>
                </div>
                <div style="width:100%; max-width:28px; height:36px; position:relative; margin:2px 0;">
                    <!-- Zero Axis Baseline across middle -->
                    <div style="position:absolute; left:0; right:0; top:50%; height:1px; background:var(--border-strong, #8c7b64); z-index:2;"></div>
                    <!-- Value Bar: positive grows up, negative grows down -->
                    <div style="position:absolute; left:5px; right:5px; ${isPositive ? `bottom:50%; height:${barHeightPct / 2}%;` : `top:50%; height:${barHeightPct / 2}%;`} background:${barColor}; border-radius:1px; z-index:1;"></div>
                </div>
                <div style="font-size:12px; font-family:var(--font-mono); font-weight:600; line-height:1; color:${barColor};">
                    ${score >= 0 ? '+' : ''}${Math.round(score)}
                </div>
            `;

            col.addEventListener('click', () => {
                selectHouse(root, hol, h, true);
            });

            skylineGrid.appendChild(col);
        }
    }

    function renderMatrixTable(root, hol, chartData) {
        const tbody = root.querySelector('.hol-matrix-table tbody');
        if (!tbody) return;
        tbody.innerHTML = '';

        const houses = hol.houses || {};
        const selectedHouse = _selectedHouseState.get(root) || 1;

        for (let h = 1; h <= 12; h++) {
            const hData = houses[String(h)] || {};
            const comps = hData.components || {};
            const synth = hData.synthesis || {};

            const sign = hData.sign || '--';
            const sGlyph = getSignGlyph(sign);
            const lord = hData.lord || '--';
            const lGlyph = getPlanetGlyph(lord);

            // 6 Classical Pillars
            const basicScore = comps.basic_house_condition ? comps.basic_house_condition.score : 0.0;
            const lordScore = comps.lord_assessment ? (comps.lord_assessment.combined_score ?? comps.lord_assessment.lord_final_score) : 0.0;
            const relMoonScore = comps.relative_houses_combined_score !== undefined
                ? comps.relative_houses_combined_score
                : (comps.chandra_lagna_assessment && comps.chandra_lagna_assessment.combined_relative_score !== undefined
                    ? comps.chandra_lagna_assessment.combined_relative_score
                    : (comps.relative_house_bhavat_bhavam ? comps.relative_house_bhavat_bhavam.score : 0.0));
            const karakaScore = comps.karaka_assessment ? comps.karaka_assessment.score : 0.0;
            const yogaScore = comps.house_yogas ? comps.house_yogas.total_yoga_score : 0.0;
            const wallScore = (comps.house_walls_kartari && comps.house_walls_kartari.is_walled) ? comps.house_walls_kartari.score : null;

            const composite = synth.composite_score !== undefined ? synth.composite_score : 0.0;
            const tier = synth.classical_tier || 'Miśra';
            const tierDot = getTierDotHtml(tier);

            const isSelected = (h === selectedHouse);
            const compColor = composite >= 25.0 
                ? 'var(--status-benefic-dark, #15803d)' 
                : (composite <= -25.0 ? 'var(--status-malefic-dark, #b91c1c)' : 'var(--text-heading, #4a3325)');

            const tr = document.createElement('tr');
            tr.className = `interactive-table-row hol-house-row ${isSelected ? 'active-row' : ''}`;
            tr.dataset.house = String(h);
            tr.style.cssText = `border-bottom: 1px solid var(--border-subtle, #e5dccb); cursor: pointer; transition: background 0.15s ease; ${isSelected ? 'background: var(--bg-surface-muted, #eee5d3); font-weight: 600;' : ''}`;

            tr.innerHTML = `
                <td style="padding: 6px 8px; text-align: center; font-weight: 700; font-family: var(--font-mono);">${String(h).padStart(2, '0')}</td>
                <td style="padding: 6px 8px;"><span style="font-family: var(--font-astro-glyphs); margin-right: 4px;">${sGlyph}</span>${sign}</td>
                <td style="padding: 6px 8px;"><span style="font-family: var(--font-astro-glyphs); margin-right: 4px;">${lGlyph}</span>${lord}</td>
                <td style="padding: 6px 8px; text-align: right; font-family: var(--font-mono);">${formatComponentCell(basicScore)}</td>
                <td style="padding: 6px 8px; text-align: right; font-family: var(--font-mono);">${formatComponentCell(lordScore)}</td>
                <td style="padding: 6px 8px; text-align: right; font-family: var(--font-mono);">${formatComponentCell(relMoonScore)}</td>
                <td style="padding: 6px 8px; text-align: right; font-family: var(--font-mono);">${formatComponentCell(karakaScore)}</td>
                <td style="padding: 6px 8px; text-align: right; font-family: var(--font-mono);">${formatComponentCell(yogaScore)}</td>
                <td style="padding: 6px 8px; text-align: right; font-family: var(--font-mono);">${formatComponentCell(wallScore)}</td>
                <td style="padding: 6px 8px; text-align: right; font-family: var(--font-mono); font-weight: 700; font-size: 13px; color: ${compColor};">${composite >= 0 ? '+' : ''}${composite.toFixed(2)}</td>
                <td style="padding: 6px 8px; text-align: center; font-size: 12px; white-space: nowrap;">${tierDot}<span>${tier}</span></td>
            `;

            tr.addEventListener('click', () => {
                selectHouse(root, hol, h, true);
            });

            tbody.appendChild(tr);
        }
    }

    function highlightActiveRow(root, activeH) {
        const rows = root.querySelectorAll('.hol-house-row');
        rows.forEach(r => {
            const h = parseInt(r.dataset.house, 10);
            if (h === activeH) {
                r.classList.add('active-row');
                r.style.background = 'var(--bg-surface-muted, #eee5d3)';
                r.style.fontWeight = '600';
            } else {
                r.classList.remove('active-row');
                r.style.background = '';
                r.style.fontWeight = '';
            }
        });

        // Also update skyline column highlight
        const skylineCols = root.querySelectorAll('.hol-skyline-col');
        skylineCols.forEach(col => {
            const h = parseInt(col.dataset.house, 10);
            if (h === activeH) {
                col.classList.add('active-col');
                col.style.background = 'var(--bg-surface, #fffdfa)';
                col.style.boxShadow = '0 1px 3px rgba(0,0,0,0.08)';
            } else {
                col.classList.remove('active-col');
                col.style.background = 'transparent';
                col.style.boxShadow = 'none';
            }
        });
    }

    function renderReceiptInspector(root, hol, houseNum) {
        const hData = (hol.houses && hol.houses[String(houseNum)]) || {};
        const comps = hData.components || {};
        const synth = hData.synthesis || {};

        const sign = hData.sign || '--';
        const sGlyph = getSignGlyph(sign);
        const lord = hData.lord || '--';
        const lGlyph = getPlanetGlyph(lord);
        const cuspDeg = formatDegMin(hData.cusp_degree);
        const composite = synth.composite_score !== undefined ? synth.composite_score : 0.0;
        const tier = synth.classical_tier || 'Miśra';
        const tierDot = getTierDotHtml(tier);

        // Header
        const badgeEl = root.querySelector('.hol-selected-house-badge');
        if (badgeEl) badgeEl.textContent = `H${houseNum}`;

        const tabBadge = root.querySelector('.hol-tab-house-badge');
        if (tabBadge) tabBadge.textContent = `H${houseNum}`;

        const titleEl = root.querySelector('.hol-receipt-title');
        if (titleEl) {
            titleEl.innerHTML = `House ${houseNum} · ${sign} <span style="font-family:var(--font-astro-glyphs);">${sGlyph}</span>`;
        }

        const subtitleEl = root.querySelector('.hol-receipt-subtitle');
        if (subtitleEl) {
            subtitleEl.innerHTML = `Cusp Door: ${cuspDeg} · Ruled by ${lord} <span style="font-family:var(--font-astro-glyphs);">${lGlyph}</span>`;
        }

        const compValEl = root.querySelector('.hol-receipt-composite-val');
        if (compValEl) {
            compValEl.textContent = `${composite >= 0 ? '+' : ''}${composite.toFixed(2)}`;
            compValEl.style.color = (composite >= 25.0 ? 'var(--status-benefic-dark)' : (composite <= -25.0 ? 'var(--status-malefic-dark)' : 'var(--text-heading)'));
        }

        const tierTagEl = root.querySelector('.hol-receipt-tier-tag');
        if (tierTagEl) {
            tierTagEl.innerHTML = `${tierDot}<strong style="color:var(--text-heading);">${tier}</strong> (${synth.health_rating || ''})`;
        }

        // 6 Classical Pillar Scores
        const basicScore = comps.basic_house_condition ? comps.basic_house_condition.score : 0.0;
        const lordScore = comps.lord_assessment ? (comps.lord_assessment.combined_score ?? comps.lord_assessment.lord_final_score) : 0.0;
        const relMoonScore = comps.relative_houses_combined_score !== undefined
            ? comps.relative_houses_combined_score
            : (comps.chandra_lagna_assessment && comps.chandra_lagna_assessment.combined_relative_score !== undefined
                ? comps.chandra_lagna_assessment.combined_relative_score
                : (comps.relative_house_bhavat_bhavam ? comps.relative_house_bhavat_bhavam.score : 0.0));
        const karakaScore = comps.karaka_assessment ? comps.karaka_assessment.score : 0.0;
        const yogaScore = comps.house_yogas ? comps.house_yogas.total_yoga_score : 0.0;
        const wallScore = (comps.house_walls_kartari && comps.house_walls_kartari.is_walled) ? comps.house_walls_kartari.score : 0.0;

        // Render 6-Pillar Summary Ledger (Top of Receipt)
        const pillarRows = root.querySelector('.hol-pillar-ledger-rows');
        if (pillarRows) {
            pillarRows.innerHTML = '';
            const pillars = [
                { name: '1. Basic Cusp Condition', weight: 30, score: basicScore },
                { name: '2. Lord & Occupants', weight: 30, score: lordScore },
                { name: '3. Relative & Chandra', weight: 15, score: relMoonScore },
                { name: '4. Bhāva Kāraka', weight: 10, score: karakaScore },
                { name: '5. Structural Yogas', weight: 10, score: yogaScore },
                { name: '6. Kartarī House Walls', weight: 5, score: wallScore }
            ];

            pillars.forEach(p => {
                const sc = p.score || 0.0;
                const isPos = sc >= 0;
                const absSc = Math.abs(sc);
                const barWidthPct = Math.min(50, (absSc / 120.0) * 50);
                const barColor = isPos ? 'var(--status-benefic-dark, #15803d)' : 'var(--status-malefic-dark, #b91c1c)';

                const row = document.createElement('div');
                row.style.cssText = 'display:flex; justify-content:space-between; align-items:center; padding:2px 0; border-bottom:1px solid var(--border-subtle, #f0e9dc);';
                row.innerHTML = `
                    <span style="color:var(--text-heading); font-size:12px;">${p.name} <span style="color:var(--text-muted); font-size:12px;">(${p.weight}%)</span></span>
                    <div style="display:flex; align-items:center; gap:8px;">
                        <div style="width:60px; height:6px; background:#e2d7c3; border-radius:2px; position:relative; overflow:hidden;">
                            <div style="position:absolute; left:50%; top:0; bottom:0; width:1px; background:#8c7b64; z-index:2;"></div>
                            <div style="position:absolute; top:0; bottom:0; ${isPos ? `left:50%; width:${barWidthPct}%;` : `right:50%; width:${barWidthPct}%;`} background:${barColor}; z-index:1;"></div>
                        </div>
                        <strong style="font-family:var(--font-mono); font-size:12px; min-width:44px; text-align:right; color:${isPos ? 'var(--text-primary)' : 'var(--status-malefic-dark)'};">
                            ${sc !== 0 ? (sc >= 0 ? '+' : '') + sc.toFixed(1) : '—'}
                        </strong>
                    </div>
                `;
                pillarRows.appendChild(row);
            });
        }

        // Section 1: Lord, Dispositor Chain & Occupants (30%)
        const lordChainContainer = root.querySelector('.hol-lord-chain-breakdown');
        if (lordChainContainer) {
            lordChainContainer.innerHTML = '';
            const lAss = comps.lord_assessment || {};
            const rawLordSc = lAss.lord_final_score !== undefined ? lAss.lord_final_score : 0.0;
            const effLord = lAss.effective_lord_score !== undefined ? lAss.effective_lord_score : rawLordSc;
            const immDisp = lAss.immediate_dispositor || '--';
            const finalDisp = lAss.final_dispositor || '--';

            // Clean typographic chain
            let chainStr = `Lord ${lord} (${rawLordSc >= 0 ? '+' : ''}${rawLordSc.toFixed(1)})`;
            if (immDisp !== '--' && immDisp !== lord) {
                chainStr += ` → Host ${immDisp}`;
            }
            if (finalDisp !== '--' && finalDisp !== immDisp) {
                chainStr += ` → Final ${finalDisp}`;
            }

            const occs = hData.occupants || [];
            let occsStr = 'None (Unoccupied)';
            if (occs.length > 0) {
                const occScores = lAss.occupants_final_scores || lAss.occupants_scores || {};
                occsStr = occs.map(p => {
                    const pGl = getPlanetGlyph(p);
                    const pSc = occScores[p];
                    const scStr = pSc !== undefined ? ` (${pSc >= 0 ? '+' : ''}${pSc.toFixed(1)})` : '';
                    return `<span style="font-family:var(--font-astro-glyphs);">${pGl}</span><strong>${p}</strong>${scStr}`;
                }).join(', ');
            }

            lordChainContainer.innerHTML = `
                <div style="font-family:var(--font-mono); font-size:12px; color:var(--text-heading); padding:2px 0;">
                    ${chainStr} &nbsp;·&nbsp; Effective Lord: <strong style="color:${effLord >= 0 ? 'var(--text-primary)' : 'var(--status-malefic-dark)'};">${effLord >= 0 ? '+' : ''}${effLord.toFixed(1)}</strong>
                </div>
                <div style="color:var(--text-muted); font-size:12px; padding:2px 0;">
                    Physical Occupants: <span style="color:var(--text-primary);">${occsStr}</span>
                </div>
            `;
        }

        // Section 2: Direct Cusp Rays Breakdown (30%)
        const basicData = comps.basic_house_condition || {};
        const valBasic = root.querySelector('.hol-val-basic');
        if (valBasic) {
            valBasic.textContent = `${basicScore >= 0 ? '+' : ''}${basicScore.toFixed(1)}`;
            valBasic.style.color = getScoreColor(basicScore);
        }

        const raysContainer = root.querySelector('.hol-cusp-rays-breakdown');
        if (raysContainer) {
            raysContainer.innerHTML = '';
            const contribs = basicData.planet_contributions || {};
            // Filter out 0.0 rays and sort descending
            const activePlanets = Object.keys(contribs)
                .filter(p => Math.abs(contribs[p]) >= 0.05)
                .sort((a, b) => Math.abs(contribs[b]) - Math.abs(contribs[a]));

            if (activePlanets.length === 0) {
                raysContainer.innerHTML = '<span style="color:var(--text-muted); padding: 4px 0;">No significant rays active on cusp</span>';
            } else {
                activePlanets.forEach(p => {
                    const cVal = contribs[p];
                    const pGlyph = getPlanetGlyph(p);
                    const isLord = (p === lord);
                    const item = document.createElement('div');
                    item.style.cssText = 'display:flex; justify-content:space-between; align-items:center; padding:2px 0; border-bottom:1px dashed var(--border-subtle);';
                    item.innerHTML = `
                        <div style="display:flex; align-items:center; gap:5px;">
                            <span style="font-family:var(--font-astro-glyphs);">${pGlyph}</span>
                            <span>${p}</span>
                            ${isLord ? '<span style="color:var(--text-muted); font-size:12px;">(Lord)</span>' : ''}
                        </div>
                        <strong style="color:${cVal >= 0 ? 'var(--text-primary)' : 'var(--status-malefic-dark)'}; font-size:12px;">${cVal >= 0 ? '+' : ''}${cVal.toFixed(1)}</strong>
                    `;
                    raysContainer.appendChild(item);
                });
            }
        }

        // Section 3: Bhavāt Bhavam & Chandra Lagna (15%)
        const relContainer = root.querySelector('.hol-relative-lunar-breakdown');
        if (relContainer) {
            const rAss = comps.relative_house_bhavat_bhavam || {};
            const chAss = comps.chandra_lagna_assessment || {};
            const kkPts = rAss.kk_group_points || 0.0;
            const dustRaw = rAss.dusthana_raw_points || 0.0;
            const mitPct = (rAss.benefic_mitigation_pct || 0.0).toFixed(1);
            const dustNet = rAss.dusthana_mitigated_points || 0.0;
            const chNum = chAss.chandra_house_num || chAss.chandra_house_number || '--';
            const chScore = chAss.chandra_house_score !== undefined ? chAss.chandra_house_score : chAss.score;
            const chStr = chScore !== undefined ? `${chScore >= 0 ? '+' : ''}${chScore.toFixed(1)}` : '--';

            relContainer.innerHTML = `
                <div style="display:grid; grid-template-columns:1fr 1fr; gap:4px; font-family:var(--font-mono); font-size:12px;">
                    <div>Kendra/Trine: <strong>${kkPts >= 0 ? '+' : ''}${kkPts.toFixed(1)}</strong></div>
                    <div>Dusthāna: <strong style="color:${dustNet < 0 ? 'var(--status-malefic-dark)' : 'var(--text-primary)'};">${dustNet >= 0 ? '+' : ''}${dustNet.toFixed(1)}</strong> <span style="color:var(--text-muted); font-size:12px;">(${mitPct}% mit)</span></div>
                    <div>Chandra H: <strong>H${chNum}</strong></div>
                    <div>Chandra Score: <strong>${chStr}</strong></div>
                </div>
            `;
        }

        // Section 4: Bhāva Kāraka Assessment (10%)
        const karakaContainer = root.querySelector('.hol-karaka-breakdown');
        if (karakaContainer) {
            const kAss = comps.karaka_assessment || {};
            const karakas = kAss.karakas || [];
            const kScores = kAss.karaka_planet_scores || {};
            const kStr = karakas.map(k => {
                const kGl = getPlanetGlyph(k);
                const sc = kScores[k];
                const scText = sc !== undefined ? ` (${sc >= 0 ? '+' : ''}${sc.toFixed(1)})` : '';
                return `<span style="font-family:var(--font-astro-glyphs);">${kGl}</span><strong>${k}</strong>${scText}`;
            }).join(', ') || 'None';

            const kLagnaH = kAss.karaka_lagna_house;
            const kLagnaSc = kAss.karaka_lagna_score;
            const kLagnaStr = (kLagnaH && kLagnaSc !== undefined) ? `House ${kLagnaH} (${kLagnaSc >= 0 ? '+' : ''}${kLagnaSc.toFixed(1)})` : '--';

            karakaContainer.innerHTML = `
                <div style="font-size:12px; color:var(--text-primary); padding:2px 0;">
                    Significators: ${kStr}
                </div>
                <div style="font-size:12px; color:var(--text-muted); padding:2px 0;">
                    Kāraka Lagna: <span style="font-family:var(--font-mono); color:var(--text-primary);">${kLagnaStr}</span>
                </div>
            `;
        }

        // Section 5: Structural House Yogas (10%)
        const yogaData = comps.house_yogas || {};
        const yogasList = root.querySelector('.hol-active-yogas-list');
        if (yogasList) {
            yogasList.innerHTML = '';
            const activeY = yogaData.active_yogas || [];
            if (activeY.length === 0) {
                yogasList.innerHTML = '<span style="color:var(--text-muted); padding: 4px 0;">No structural yogas active for this house</span>';
            } else {
                activeY.forEach(y => {
                    const row = document.createElement('div');
                    row.style.cssText = 'display:flex; justify-content:space-between; align-items:center; padding:2px 0; border-bottom:1px dashed var(--border-subtle);';
                    const isPos = y.points >= 0;
                    const roleLabel = y.role ? (y.role.includes('Occupied') ? 'Occupied' : 'Owned') : 'Active';
                    row.innerHTML = `
                        <div style="display:flex; align-items:center; gap:6px;">
                            <strong>${y.type}</strong>
                            <span style="color:var(--text-muted); font-size:12px;">· ${roleLabel}</span>
                            <span style="color:var(--text-muted); font-size:12px;">(${y.planets.join(' + ')})</span>
                        </div>
                        <strong style="color:${isPos ? 'var(--text-primary)' : 'var(--status-malefic-dark)'}; font-family:var(--font-mono); font-size:12px;">${y.points >= 0 ? '+' : ''}${y.points.toFixed(0)}</strong>
                    `;
                    yogasList.appendChild(row);
                });
            }
        }

        // Section 6: 30° Cusp Bracket & Kartarī Wall (5%)
        const wallData = comps.house_walls_kartari || {};
        const valWall = root.querySelector('.hol-val-wall');
        if (valWall) {
            valWall.textContent = `${wallScore >= 0 ? '+' : ''}${wallScore.toFixed(1)}`;
            valWall.style.color = getScoreColor(wallScore);
        }

        const wallTypeTag = root.querySelector('.hol-wall-type-tag');
        if (wallTypeTag) {
            const wType = wallData.wall_type || 'None';
            wallTypeTag.textContent = wType === 'None' ? 'Open Cusp (Unwalled)' : wType;
            wallTypeTag.style.color = wType.includes('Shubha') ? 'var(--status-benefic-dark)' : (wType.includes('Papa') ? 'var(--status-malefic-dark)' : 'var(--text-muted)');
        }

        const wallStrip = root.querySelector('.hol-wall-strip-visualizer');
        if (wallStrip) {
            wallStrip.innerHTML = '';
            const pBefore = wallData.planet_before;
            const pAfter = wallData.planet_after;

            let beforeMarker = '';
            let afterMarker = '';

            if (pBefore) {
                const pGlyph = getPlanetGlyph(pBefore);
                beforeMarker = `
                    <g transform="translate(60, 24)">
                        <circle r="10" fill="var(--bg-surface)" stroke="var(--border-medium)" stroke-width="1.5" />
                        <text text-anchor="middle" dy="4" font-family="var(--font-astro-glyphs)" font-size="12" fill="var(--text-heading)">${pGlyph}</text>
                        <text text-anchor="middle" dy="20" font-family="var(--font-sans)" font-size="12" fill="var(--text-muted)">−Before</text>
                    </g>
                `;
            }

            if (pAfter) {
                const pGlyph = getPlanetGlyph(pAfter);
                afterMarker = `
                    <g transform="translate(260, 24)">
                        <circle r="10" fill="var(--bg-surface)" stroke="var(--border-medium)" stroke-width="1.5" />
                        <text text-anchor="middle" dy="4" font-family="var(--font-astro-glyphs)" font-size="12" fill="var(--text-heading)">${pGlyph}</text>
                        <text text-anchor="middle" dy="20" font-family="var(--font-sans)" font-size="12" fill="var(--text-muted)">+After</text>
                    </g>
                `;
            }

            wallStrip.innerHTML = `
                <svg width="100%" height="100%" viewBox="0 0 320 48" preserveAspectRatio="none">
                    <!-- Baseline Ruler -->
                    <line x1="20" y1="24" x2="300" y2="24" stroke="var(--border-medium, #d5c8b2)" stroke-width="1.5" />
                    <!-- Left -30 Bound -->
                    <line x1="20" y1="18" x2="20" y2="30" stroke="var(--border-strong, #dcb594)" stroke-width="2" />
                    <text x="20" y="42" font-size="12" fill="var(--text-subtle)" text-anchor="middle">−30°</text>
                    <!-- Center Cusp -->
                    <line x1="160" y1="12" x2="160" y2="36" stroke="var(--accent-primary, #d35400)" stroke-width="2.5" />
                    <circle cx="160" cy="24" r="3" fill="var(--accent-primary, #d35400)" />
                    <text x="160" y="10" font-size="12" font-weight="700" fill="var(--accent-primary, #d35400)" text-anchor="middle">CUSP</text>
                    <!-- Right +30 Bound -->
                    <line x1="300" y1="18" x2="300" y2="30" stroke="var(--border-strong, #dcb594)" stroke-width="2" />
                    <text x="300" y="42" font-size="12" fill="var(--text-subtle)" text-anchor="middle">+30°</text>
                    <!-- Markers -->
                    ${beforeMarker}
                    ${afterMarker}
                </svg>
            `;
        }

        const wallDesc = root.querySelector('.hol-wall-text-desc');
        if (wallDesc) {
            if (wallData.is_walled) {
                wallDesc.textContent = `House cusp is flanked by ${wallData.planet_before} (before) and ${wallData.planet_after} (after), forming a ${wallData.wall_type}.`;
            } else {
                wallDesc.textContent = 'House cusp is open; not hemmed in by flanking physical planets within 30° arcs.';
            }
        }

        // Section 7: Dominant Drivers
        const driversList = root.querySelector('.hol-dominant-drivers-list');
        if (driversList) {
            driversList.innerHTML = '';
            const drivers = synth.dominant_drivers || [];
            if (drivers.length === 0) {
                driversList.innerHTML = '<li>Balanced planetary influences with moderate environmental friction.</li>';
            } else {
                drivers.forEach(d => {
                    const li = document.createElement('li');
                    li.style.marginBottom = '3px';
                    li.textContent = d;
                    driversList.appendChild(li);
                });
            }
        }
    }

    function renderPlanetsTable(root, hol) {
        const tbody = root.querySelector('.hol-planets-table tbody');
        if (!tbody) return;
        tbody.innerHTML = '';

        const planets = hol.planets || {};
        const pOrder = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn'];

        pOrder.forEach(p => {
            const pData = planets[p] || {};
            const pGlyph = getPlanetGlyph(p);
            const sign = pData.sign || '--';
            const sGlyph = getSignGlyph(sign);
            const house = pData.house || '--';
            const deg = formatDegMin(pData.degree_in_sign);

            // Functional Nature (clean dot + text, no background pill)
            const fn = pData.functional_nature || {};
            const fnScore = fn.score !== undefined ? fn.score : 0;
            const fnClass = fn.classification || 'Neutral';
            const fnDotColor = fnClass === 'Benefic' 
                ? 'var(--status-benefic-dark, #15803d)' 
                : (fnClass === 'Malefic' ? 'var(--status-malefic-dark, #b91c1c)' : 'var(--text-subtle, #8c7b64)');
            const fnDot = `<span class="status-indicator" style="display:inline-block; width:6px; height:6px; border-radius:50%; background:${fnDotColor}; margin-right:5px; vertical-align:middle;"></span>`;

            // D1+D9 Dignity
            const dig = pData.dignity || {};
            const digPct = dig.pct_score !== undefined ? dig.pct_score : 0.0;
            const digStatus = dig.status || 'Neutral';

            // Aspects
            const combInf = pData.combined_influences || {};
            const infNet = combInf.net_score !== undefined ? combInf.net_score : 0.0;

            // Digbala
            const cuspAl = pData.cusp_alignment || {};
            const db = cuspAl.digbala_points !== undefined ? cuspAl.digbala_points : 0.0;

            // Intrinsic Quality
            const qBase = pData.quality_base_score !== undefined ? pData.quality_base_score : (pData.base_average_score || 0.0);

            // Prominence Mult
            const hMult = cuspAl.house_multiplier !== undefined ? cuspAl.house_multiplier : 1.0;
            const hCat = cuspAl.house_category || '';

            // Penalties (Comb / Sandhi / Ecl)
            const combLoss = (pData.combustion && pData.combustion.loss_ratio) ? pData.combustion.loss_ratio : 0.0;
            const sandhiPen = (pData.bhava_sandhi && pData.bhava_sandhi.penalty_ratio) ? pData.bhava_sandhi.penalty_ratio : 0.0;
            const eclLoss = (pData.eclipse && pData.eclipse.loss_ratio) ? pData.eclipse.loss_ratio : 0.0;

            const penaltyParts = [];
            if (combLoss > 0.001) penaltyParts.push(`Comb −${Math.round(combLoss * 100)}%`);
            if (sandhiPen > 0.001) penaltyParts.push(`Sandhi −${Math.round(sandhiPen * 100)}%`);
            if (eclLoss > 0.001) penaltyParts.push(`Ecl −${Math.round(eclLoss * 100)}%`);
            const penaltyText = penaltyParts.length > 0 
                ? `<span style="color:var(--status-malefic-dark, #b91c1c);">${penaltyParts.join(' · ')}</span>`
                : '<span style="color:var(--text-subtle, #9a8a78);">—</span>';

            // Final score
            const finalScore = pData.final_assessment_score !== undefined ? pData.final_assessment_score : 0.0;
            const finalColor = finalScore >= 25.0 
                ? 'var(--status-benefic-dark, #15803d)' 
                : (finalScore <= -20.0 ? 'var(--status-malefic-dark, #b91c1c)' : 'var(--text-heading, #4a3325)');

            const tr = document.createElement('tr');
            tr.style.cssText = 'border-bottom: 1px solid var(--border-subtle, #e5dccb);';

            tr.innerHTML = `
                <td style="padding: 6px 8px; font-weight: 700;"><span style="font-family: var(--font-astro-glyphs); margin-right: 4px;">${pGlyph}</span>${p}</td>
                <td style="padding: 6px 8px;">H${house} · <span style="font-family: var(--font-astro-glyphs);">${sGlyph}</span> ${sign} ${deg}</td>
                <td style="padding: 6px 8px;">${fnDot}<span style="font-family: var(--font-mono); font-weight: 600;">${fnScore >= 0 ? '+' : ''}${fnScore.toFixed(1)}</span> <span style="color:var(--text-muted); font-size:12px;">(${fnClass})</span></td>
                <td style="padding: 6px 8px; text-align: right; font-family: var(--font-mono);">${digPct >= 0 ? '+' : ''}${digPct.toFixed(0)}% <span style="color:var(--text-muted); font-size:12px;">(${digStatus})</span></td>
                <td style="padding: 6px 8px; text-align: right; font-family: var(--font-mono);">${infNet >= 0 ? '+' : ''}${infNet.toFixed(1)}</td>
                <td style="padding: 6px 8px; text-align: right; font-family: var(--font-mono);">${db >= 0 ? '+' : ''}${db.toFixed(1)}</td>
                <td style="padding: 6px 8px; text-align: right; font-family: var(--font-mono); font-weight: 600;">${qBase >= 0 ? '+' : ''}${qBase.toFixed(1)}</td>
                <td style="padding: 6px 8px; text-align: right; font-family: var(--font-mono);">${hMult.toFixed(2)}× <span style="color:var(--text-muted); font-size:12px;">(${hCat})</span></td>
                <td style="padding: 6px 8px; text-align: right; font-family: var(--font-mono); font-size: 12px;">${penaltyText}</td>
                <td style="padding: 6px 8px; text-align: right; font-family: var(--font-mono); font-weight: 700; font-size: 13px; color: ${finalColor};">${finalScore >= 0 ? '+' : ''}${finalScore.toFixed(1)}</td>
            `;

            tbody.appendChild(tr);
        });
    }

    function renderConcordanceTable(root, hol, chartData) {
        const tbody = root.querySelector('.hol-concordance-table tbody');
        if (!tbody) return;
        tbody.innerHTML = '';

        const bb = chartData.bhava_bala || {};
        const houses = hol.houses || {};

        for (let h = 1; h <= 12; h++) {
            const hData = houses[String(h)] || {};
            const synth = hData.synthesis || {};
            const sign = hData.sign || '--';
            const sGlyph = getSignGlyph(sign);
            const lord = hData.lord || '--';
            const lGlyph = getPlanetGlyph(lord);

            // Stage 3 values
            const bbH = bb[h] || bb[String(h)] || {};
            const virupas = bbH.total_virupas !== undefined ? bbH.total_virupas.toFixed(1) : '--';
            const rupas = bbH.total_rupas !== undefined ? bbH.total_rupas.toFixed(2) : (bbH.total_virupas !== undefined ? (bbH.total_virupas / 60).toFixed(2) : '--');
            const st3Tier = bbH.classification || (parseFloat(rupas) >= 8.0 ? 'Puṣṭa' : (parseFloat(rupas) < 6.0 ? 'Hīna' : 'Miśra'));
            const st3Dot = getTierDotHtml(st3Tier);

            // Stage 4 values
            const score4 = synth.composite_score !== undefined ? synth.composite_score : 0.0;
            const st4Tier = synth.classical_tier || 'Miśra';
            const st4Dot = getTierDotHtml(st4Tier);

            // Diagnosis: clean editorial prose with a 6px status indicator dot
            let diagnosis = '';
            const t3 = st3Tier.toLowerCase();
            const t4 = st4Tier.toLowerCase();

            if ((t3.includes('puṣṭa') && t4.includes('puṣṭa')) ||
                (t3.includes('hīna') && t4.includes('hīna')) ||
                (t3.includes('miśra') && t4.includes('miśra'))) {
                diagnosis = `<span class="status-indicator" style="display:inline-block; width:6px; height:6px; border-radius:50%; background:var(--status-benefic-dark, #15803d); margin-right:5px; vertical-align:middle;"></span>Harmonic Agreement (${st4Tier})`;
            } else if (score4 >= 25.0 && !t3.includes('puṣṭa')) {
                diagnosis = '<span class="status-indicator" style="display:inline-block; width:6px; height:6px; border-radius:50%; background:var(--text-subtle, #8c7b64); margin-right:5px; vertical-align:middle;"></span>Divergent: Stage 4 Elevated by Yogas / Kartarī Wall';
            } else if (score4 <= -20.1 && !t3.includes('hīna')) {
                diagnosis = '<span class="status-indicator" style="display:inline-block; width:6px; height:6px; border-radius:50%; background:var(--status-malefic-dark, #b91c1c); margin-right:5px; vertical-align:middle;"></span>Divergent: Stage 4 Strained by Cusp Pressure / Dusthāna';
            } else {
                diagnosis = `<span class="status-indicator" style="display:inline-block; width:6px; height:6px; border-radius:50%; background:var(--border-strong, #8c7b64); margin-right:5px; vertical-align:middle;"></span>Stage 3 ${st3Tier} ↔ Stage 4 ${st4Tier}`;
            }

            const tr = document.createElement('tr');
            tr.style.cssText = 'border-bottom: 1px solid var(--border-subtle, #e5dccb);';

            tr.innerHTML = `
                <td style="padding: 6px 8px; text-align: center; font-weight: 700; font-family: var(--font-mono);">${String(h).padStart(2, '0')}</td>
                <td style="padding: 6px 8px;"><span style="font-family: var(--font-astro-glyphs); margin-right: 4px;">${sGlyph}</span>${sign} (${lord})</td>
                <td style="padding: 6px 8px; text-align: right; font-family: var(--font-mono);">${virupas}</td>
                <td style="padding: 6px 8px; text-align: right; font-family: var(--font-mono); font-weight: 600;">${rupas}</td>
                <td style="padding: 6px 8px; text-align: center; font-size: 12px; white-space: nowrap;">${st3Dot}<span>${st3Tier}</span></td>
                <td style="padding: 6px 8px; text-align: right; font-family: var(--font-mono); font-weight: 700; color: ${getScoreColor(score4)};">${score4 >= 0 ? '+' : ''}${score4.toFixed(2)}</td>
                <td style="padding: 6px 8px; text-align: center; font-size: 12px; white-space: nowrap;">${st4Dot}<span>${st4Tier}</span></td>
                <td style="padding: 6px 8px; font-size: 12px; color: var(--text-primary);">${diagnosis}</td>
            `;

            tbody.appendChild(tr);
        }
    }

    // Register widget with WidgetRegistry (Emoji purged: icon is empty)
    if (window.widgetRegistry) {
        window.widgetRegistry.register('houses-of-life', {
            id: 'houses-of-life',
            title: 'Houses of Life (Phaladīpikā 15)',
            icon: '',
            category: 'Strengths',
            templateId: 'tmpl-houses-of-life',
            isScrollable: true,
            render: function(container, chartData, options) {
                updateHousesOfLifeWidget(container, chartData);
            },
            onUpdate: function(cell, chartData) {
                updateHousesOfLifeWidget(cell, chartData);
            }
        });
    }

    function openFloatingHousesOfLife() {
        if (typeof closeKalaMenu === 'function') closeKalaMenu();
        const modal = document.getElementById('widgetMaximizeModal');
        const card = document.getElementById('widgetMaximizeCard');
        const titleEl = document.getElementById('widgetMaximizeModalTitle');
        const container = document.getElementById('widgetMaximizeContainer');
        const currentData = window.currentChartData;
        if (!modal || !titleEl || !container || !currentData) return;

        if (card) {
            const w = Math.min(1480, window.innerWidth - 40);
            const h = Math.min(840, window.innerHeight - 60);
            card.style.width = w + 'px';
            card.style.height = h + 'px';
            card.style.left = Math.max(20, Math.round((window.innerWidth - w) / 2)) + 'px';
            card.style.top = Math.max(30, Math.round((window.innerHeight - h) / 2)) + 'px';
        }

        if (typeof setActiveFloatingNav === 'function') setActiveFloatingNav(null);
        const name = currentData.subject_info ? currentData.subject_info.name : 'Chart';
        titleEl.textContent = name + " — Houses of Life (Phaladīpikā Ch. 15)";

        const tmpl = document.getElementById('tmpl-houses-of-life');
        if (tmpl) {
            container.innerHTML = '';
            container.appendChild(tmpl.content.cloneNode(true));
            updateHousesOfLifeWidget(container, currentData);
        }

        modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
    }

    window.openFloatingHousesOfLife = openFloatingHousesOfLife;
    window.updateHousesOfLifeWidget = updateHousesOfLifeWidget;
})();
