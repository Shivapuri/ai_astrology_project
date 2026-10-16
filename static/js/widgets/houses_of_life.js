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
 * - Diverging 12-Bhāva Horizon, Live Audit Receipt with SVG 30° strip,
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
            return '<span class="status-indicator" style="display:inline-block; width:7px; height:7px; border-radius:50%; background:var(--status-benefic-dark, #15803d); margin-right:5px;"></span>';
        } else if (tier.includes('hīna') || tier.includes('hina')) {
            return '<span class="status-indicator" style="display:inline-block; width:7px; height:7px; border-radius:50%; background:var(--status-malefic-dark, #b91c1c); margin-right:5px;"></span>';
        }
        return '<span class="status-indicator" style="display:inline-block; width:7px; height:7px; border-radius:50%; background:var(--text-subtle, #8c7b64); margin-right:5px;"></span>';
    }

    function getScoreColor(val) {
        if (val >= 25.0) return 'var(--status-benefic-dark, #15803d)';
        if (val <= -20.1) return 'var(--status-malefic-dark, #b91c1c)';
        return 'var(--text-heading, #4a3325)';
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

        // Prev & Next Buttons in Receipt Inspector
        const prevBtn = root.querySelector('.hol-receipt-prev-btn');
        if (prevBtn && prevBtn.dataset.bound !== 'true') {
            prevBtn.dataset.bound = 'true';
            prevBtn.addEventListener('click', (e) => {
                e.preventDefault();
                let cur = _selectedHouseState.get(root) || 1;
                cur = cur <= 1 ? 12 : cur - 1;
                selectHouse(root, hol, cur, false);
            });
        }

        const nextBtn = root.querySelector('.hol-receipt-next-btn');
        if (nextBtn && nextBtn.dataset.bound !== 'true') {
            nextBtn.dataset.bound = 'true';
            nextBtn.addEventListener('click', (e) => {
                e.preventDefault();
                let cur = _selectedHouseState.get(root) || 1;
                cur = cur >= 12 ? 1 : cur + 1;
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

        // Render Diverging Bar Chart Horizon
        const barsGrid = root.querySelector('.hol-bars-grid');
        if (!barsGrid) return;
        barsGrid.innerHTML = '';

        const houses = hol.houses || {};
        for (let h = 1; h <= 12; h++) {
            const hData = houses[String(h)] || {};
            const synth = hData.synthesis || {};
            const score = synth.composite_score !== undefined ? synth.composite_score : 0.0;
            const sign = hData.sign || '';
            const sGlyph = getSignGlyph(sign);

            // Normalize score (-150 to +150) to percentage from center (50%)
            const clamped = Math.max(-150, Math.min(150, score));
            const barPct = (Math.abs(clamped) / 150.0) * 45; // max 45% width from center

            const isPositive = clamped >= 0;
            const barColor = isPositive ? 'var(--status-benefic-dark, #15803d)' : 'var(--status-malefic-dark, #b91c1c)';

            const col = document.createElement('div');
            col.style.cssText = 'display:flex; flex-direction:column; align-items:center; height:100%; justify-content:center; cursor:pointer; position:relative;';
            col.title = `House ${h} (${sign}): ${score >= 0 ? '+' : ''}${score.toFixed(1)} (${synth.health_rating || ''})`;

            col.innerHTML = `
                <div style="font-size:12px; font-weight:700; line-height:1; color:var(--text-heading); display:flex; align-items:center; gap:2px;">
                    <span>H${h}</span>
                    <span style="font-family:var(--font-astro-glyphs); font-size:12px;">${sGlyph}</span>
                </div>
                <div style="width:100%; height:12px; position:relative; background:#e2d7c3; border-radius:2px; margin-top:2px; overflow:hidden;">
                    <!-- Zero Axis Line -->
                    <div style="position:absolute; left:50%; top:0; bottom:0; width:1px; background:#8c7b64; z-index:2;"></div>
                    <!-- Value Bar -->
                    <div style="position:absolute; top:1px; bottom:1px; ${isPositive ? `left:50%; width:${barPct}%;` : `right:50%; width:${barPct}%;`} background:${barColor}; border-radius:1px; z-index:1;"></div>
                </div>
                <div style="font-size:12px; font-family:var(--font-mono); font-weight:600; line-height:1; margin-top:2px; color:${barColor};">
                    ${score >= 0 ? '+' : ''}${Math.round(score)}
                </div>
            `;

            col.addEventListener('click', () => {
                selectHouse(root, hol, h, true);
            });

            barsGrid.appendChild(col);
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

            const basicScore = comps.basic_house_condition ? comps.basic_house_condition.score : 0.0;
            const lordScore = comps.lord_assessment ? comps.lord_assessment.lord_final_score : 0.0;
            const bhavatScore = comps.relative_house_bhavat_bhavam ? comps.relative_house_bhavat_bhavam.score : 0.0;
            const wallScore = comps.house_walls_kartari ? comps.house_walls_kartari.score : 0.0;
            const yogaScore = comps.house_yogas ? comps.house_yogas.total_yoga_score : 0.0;
            const composite = synth.composite_score !== undefined ? synth.composite_score : 0.0;
            const tier = synth.classical_tier || 'Miśra';
            const tierDot = getTierDotHtml(tier);

            const isSelected = (h === selectedHouse);

            const tr = document.createElement('tr');
            tr.className = `interactive-table-row hol-house-row ${isSelected ? 'active-row' : ''}`;
            tr.dataset.house = String(h);
            tr.style.cssText = `border-bottom: 1px solid var(--border-subtle, #e5dccb); cursor: pointer; transition: background 0.15s ease; ${isSelected ? 'background: var(--bg-surface-muted, #eee5d3); font-weight: 600;' : ''}`;

            tr.innerHTML = `
                <td style="padding: 6px 8px; text-align: center; font-weight: 700; font-family: var(--font-mono);">${String(h).padStart(2, '0')}</td>
                <td style="padding: 6px 8px;"><span style="font-family: var(--font-astro-glyphs); margin-right: 4px;">${sGlyph}</span>${sign}</td>
                <td style="padding: 6px 8px;"><span style="font-family: var(--font-astro-glyphs); margin-right: 4px;">${lGlyph}</span>${lord}</td>
                <td style="padding: 6px 8px; text-align: right; font-family: var(--font-mono); color: ${getScoreColor(basicScore)};">${basicScore >= 0 ? '+' : ''}${basicScore.toFixed(1)}</td>
                <td style="padding: 6px 8px; text-align: right; font-family: var(--font-mono); color: ${getScoreColor(lordScore)};">${lordScore >= 0 ? '+' : ''}${lordScore.toFixed(1)}</td>
                <td style="padding: 6px 8px; text-align: right; font-family: var(--font-mono); color: ${getScoreColor(bhavatScore)};">${bhavatScore >= 0 ? '+' : ''}${bhavatScore.toFixed(1)}</td>
                <td style="padding: 6px 8px; text-align: right; font-family: var(--font-mono); color: ${getScoreColor(wallScore)};">${wallScore >= 0 ? '+' : ''}${wallScore.toFixed(1)}</td>
                <td style="padding: 6px 8px; text-align: right; font-family: var(--font-mono); color: ${getScoreColor(yogaScore)};">${yogaScore >= 0 ? '+' : ''}${yogaScore.toFixed(1)}</td>
                <td style="padding: 6px 8px; text-align: right; font-family: var(--font-mono); font-weight: 700; font-size: 13px; color: ${getScoreColor(composite)};">${composite >= 0 ? '+' : ''}${composite.toFixed(2)}</td>
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
            titleEl.innerHTML = `House ${houseNum} (${sign} <span style="font-family:var(--font-astro-glyphs);">${sGlyph}</span>)`;
        }

        const subtitleEl = root.querySelector('.hol-receipt-subtitle');
        if (subtitleEl) {
            subtitleEl.innerHTML = `Cusp Door: ${cuspDeg} · Ruled by ${lord} <span style="font-family:var(--font-astro-glyphs);">${lGlyph}</span>`;
        }

        const compValEl = root.querySelector('.hol-receipt-composite-val');
        if (compValEl) {
            compValEl.textContent = `${composite >= 0 ? '+' : ''}${composite.toFixed(2)}`;
            compValEl.style.color = getScoreColor(composite);
        }

        const tierTagEl = root.querySelector('.hol-receipt-tier-tag');
        if (tierTagEl) {
            tierTagEl.innerHTML = `${tierDot}<strong style="color:var(--text-heading);">${tier}</strong> (${synth.health_rating || ''})`;
        }

        // 1. Direct Cusp Rays Breakdown
        const basicData = comps.basic_house_condition || {};
        const valBasic = root.querySelector('.hol-val-basic');
        if (valBasic) {
            const bSc = basicData.score || 0.0;
            valBasic.textContent = `${bSc >= 0 ? '+' : ''}${bSc.toFixed(1)}`;
            valBasic.style.color = getScoreColor(bSc);
        }

        const raysContainer = root.querySelector('.hol-cusp-rays-breakdown');
        if (raysContainer) {
            raysContainer.innerHTML = '';
            const contribs = basicData.planet_contributions || {};
            const planets = Object.keys(contribs);
            if (planets.length === 0) {
                raysContainer.innerHTML = '<span style="color:var(--text-muted); padding: 4px 0;">No direct rays active on cusp</span>';
            } else {
                planets.forEach(p => {
                    const cVal = contribs[p];
                    const pGlyph = getPlanetGlyph(p);
                    const isLord = (p === lord);
                    const item = document.createElement('div');
                    item.style.cssText = 'display:flex; justify-content:space-between; align-items:center; padding:3px 0; border-bottom:1px dashed var(--border-subtle);';
                    item.innerHTML = `
                        <div style="display:flex; align-items:center; gap:5px;">
                            <span style="font-family:var(--font-astro-glyphs);">${pGlyph}</span>
                            <span>${p}</span>
                            ${isLord ? '<span class="micro-tag" style="font-size:12px; background:var(--bg-surface-muted);">LORD</span>' : ''}
                        </div>
                        <strong style="color:${getScoreColor(cVal)}; font-size:12px;">${cVal >= 0 ? '+' : ''}${cVal.toFixed(1)}</strong>
                    `;
                    raysContainer.appendChild(item);
                });
            }
        }

        // 2. 30° Cusp Bracket & Wall Strip Visualizer
        const wallData = comps.house_walls_kartari || {};
        const valWall = root.querySelector('.hol-val-wall');
        if (valWall) {
            const wSc = wallData.score || 0.0;
            valWall.textContent = `${wSc >= 0 ? '+' : ''}${wSc.toFixed(1)}`;
            valWall.style.color = getScoreColor(wSc);
        }

        const wallTypeTag = root.querySelector('.hol-wall-type-tag');
        if (wallTypeTag) {
            const wType = wallData.wall_type || 'None';
            wallTypeTag.textContent = wType;
            if (wType === 'Shubha Kartari') {
                wallTypeTag.className = 'hol-wall-type-tag micro-tag tag-benefic';
            } else if (wType === 'Papa Kartari') {
                wallTypeTag.className = 'hol-wall-type-tag micro-tag tag-malefic';
            } else if (wType === 'Mishra Kartari') {
                wallTypeTag.className = 'hol-wall-type-tag micro-tag tag-neutral';
            } else {
                wallTypeTag.className = 'hol-wall-type-tag micro-tag';
            }
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

        // 3. Bhavāt Bhavam Neighborhood Breakdown
        const bhavatData = comps.relative_house_bhavat_bhavam || {};
        const valBhavat = root.querySelector('.hol-val-bhavat');
        if (valBhavat) {
            const bhSc = bhavatData.score || 0.0;
            valBhavat.textContent = `${bhSc >= 0 ? '+' : ''}${bhSc.toFixed(1)}`;
            valBhavat.style.color = getScoreColor(bhSc);
        }

        const valKk = root.querySelector('.hol-val-kk');
        if (valKk) {
            const v = bhavatData.kk_group_points || 0.0;
            valKk.textContent = `${v >= 0 ? '+' : ''}${v.toFixed(1)}`;
            valKk.style.color = getScoreColor(v);
        }

        const valDustRaw = root.querySelector('.hol-val-dust-raw');
        if (valDustRaw) {
            const v = bhavatData.dusthana_raw_points || 0.0;
            valDustRaw.textContent = `${v >= 0 ? '+' : ''}${v.toFixed(1)}`;
            valDustRaw.style.color = getScoreColor(v);
        }

        const valMitPct = root.querySelector('.hol-val-mit-pct');
        if (valMitPct) {
            valMitPct.textContent = `${(bhavatData.benefic_mitigation_pct || 0.0).toFixed(1)}%`;
        }

        const valDustNet = root.querySelector('.hol-val-dust-net');
        if (valDustNet) {
            const v = bhavatData.dusthana_mitigated_points || 0.0;
            valDustNet.textContent = `${v >= 0 ? '+' : ''}${v.toFixed(1)}`;
            valDustNet.style.color = getScoreColor(v);
        }

        // 4. Structural House Yogas
        const yogaData = comps.house_yogas || {};
        const valYoga = root.querySelector('.hol-val-yoga');
        if (valYoga) {
            const ySc = yogaData.total_yoga_score || 0.0;
            valYoga.textContent = `${ySc >= 0 ? '+' : ''}${ySc.toFixed(1)}`;
            valYoga.style.color = getScoreColor(ySc);
        }

        const yogasList = root.querySelector('.hol-active-yogas-list');
        if (yogasList) {
            yogasList.innerHTML = '';
            const activeY = yogaData.active_yogas || [];
            if (activeY.length === 0) {
                yogasList.innerHTML = '<span style="color:var(--text-muted); padding: 4px 0;">No structural yogas active for this house</span>';
            } else {
                activeY.forEach(y => {
                    const row = document.createElement('div');
                    row.style.cssText = 'display:flex; justify-content:space-between; align-items:center; padding:3px 0; border-bottom:1px dashed var(--border-subtle);';
                    const isPos = y.points >= 0;
                    const roleTag = y.role.includes('Occupied') ? 'OCCUPIED' : 'OWNED';
                    row.innerHTML = `
                        <div style="display:flex; align-items:center; gap:6px;">
                            <strong>${y.type}</strong>
                            <span class="micro-tag" style="font-size:12px;">${roleTag}</span>
                            <span style="color:var(--text-muted); font-size:12px;">(${y.planets.join(' + ')})</span>
                        </div>
                        <strong style="color:${isPos ? 'var(--status-benefic-dark)' : 'var(--status-malefic-dark)'}; font-family:var(--font-mono); font-size:12px;">${y.points >= 0 ? '+' : ''}${y.points.toFixed(0)}</strong>
                    `;
                    yogasList.appendChild(row);
                });
            }
        }

        // 5. Dominant Drivers
        const driversList = root.querySelector('.hol-dominant-drivers-list');
        if (driversList) {
            driversList.innerHTML = '';
            const drivers = synth.dominant_drivers || [];
            if (drivers.length === 0) {
                driversList.innerHTML = '<li>Balanced planetary influences with moderate environmental friction.</li>';
            } else {
                drivers.forEach(d => {
                    const li = document.createElement('li');
                    li.style.marginBottom = '4px';
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

            const fn = pData.functional_nature || {};
            const fnScore = fn.score !== undefined ? fn.score : 0;
            const fnClass = fn.classification || 'Neutral';
            let fnTagClass = 'tag-neutral';
            if (fnClass === 'Benefic') fnTagClass = 'tag-benefic';
            else if (fnClass === 'Malefic') fnTagClass = 'tag-malefic';

            const dig = pData.dignity || {};
            const digPct = dig.pct_score !== undefined ? dig.pct_score : 0.0;
            const digStatus = dig.status || 'Neutral';

            const combInf = pData.combined_influences || {};
            const infNet = combInf.net_score !== undefined ? combInf.net_score : 0.0;

            const cuspAl = pData.cusp_alignment || {};
            const alScore = cuspAl.alignment_score !== undefined ? cuspAl.alignment_score : 0.0;
            const alMult = cuspAl.house_multiplier !== undefined ? cuspAl.house_multiplier : 1.0;

            const baseAvg = pData.base_average_score !== undefined ? pData.base_average_score : 0.0;

            const sandhi = pData.bhava_sandhi || {};
            const sandhiMult = sandhi.retention_multiplier !== undefined ? sandhi.retention_multiplier : 1.0;

            const comb = pData.combustion || {};
            const combMult = comb.combustion_multiplier !== undefined ? comb.combustion_multiplier : 1.0;

            const finalScore = pData.final_assessment_score !== undefined ? pData.final_assessment_score : 0.0;

            const tr = document.createElement('tr');
            tr.style.cssText = 'border-bottom: 1px solid var(--border-subtle, #e5dccb);';

            tr.innerHTML = `
                <td style="padding: 6px 8px; font-weight: 700;"><span style="font-family: var(--font-astro-glyphs); margin-right: 4px;">${pGlyph}</span>${p}</td>
                <td style="padding: 6px 8px;">H${house} · <span style="font-family: var(--font-astro-glyphs);">${sGlyph}</span> ${sign} ${deg}</td>
                <td style="padding: 6px 8px;"><span class="micro-tag ${fnTagClass}" style="font-size:12px;">${fnScore >= 0 ? '+' : ''}${fnScore} ${fnClass}</span></td>
                <td style="padding: 6px 8px; text-align: right; font-family: var(--font-mono); color: ${getScoreColor(digPct)};">${digPct >= 0 ? '+' : ''}${digPct.toFixed(0)}% <span style="color:var(--text-muted); font-size:12px;">(${digStatus})</span></td>
                <td style="padding: 6px 8px; text-align: right; font-family: var(--font-mono); color: ${getScoreColor(infNet)};">${infNet >= 0 ? '+' : ''}${infNet.toFixed(1)}</td>
                <td style="padding: 6px 8px; text-align: right; font-family: var(--font-mono);">${alScore >= 0 ? '+' : ''}${alScore.toFixed(0)} <span style="color:var(--text-muted); font-size:12px;">(${alMult.toFixed(2)}×)</span></td>
                <td style="padding: 6px 8px; text-align: right; font-family: var(--font-mono);">${baseAvg >= 0 ? '+' : ''}${baseAvg.toFixed(1)}</td>
                <td style="padding: 6px 8px; text-align: right; font-family: var(--font-mono); font-size:12px; color:var(--text-muted);">${sandhiMult.toFixed(2)}× · ${combMult.toFixed(2)}×</td>
                <td style="padding: 6px 8px; text-align: right; font-family: var(--font-mono); font-weight: 700; font-size: 13px; color: ${getScoreColor(finalScore)};">${finalScore >= 0 ? '+' : ''}${finalScore.toFixed(2)}</td>
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

            // Diagnosis
            let diagnosis = '';
            const t3 = st3Tier.toLowerCase();
            const t4 = st4Tier.toLowerCase();

            if ((t3.includes('puṣṭa') && t4.includes('puṣṭa')) ||
                (t3.includes('hīna') && t4.includes('hīna')) ||
                (t3.includes('miśra') && t4.includes('miśra'))) {
                diagnosis = `<span class="micro-tag tag-benefic" style="font-size:12px;">Harmonic Agreement (${st4Tier})</span>`;
            } else if (score4 >= 25.0 && !t3.includes('puṣṭa')) {
                diagnosis = '<span class="micro-tag tag-neutral" style="font-size:12px;">Divergent: Stage 4 Elevated by Yogas / Kartarī Wall</span>';
            } else if (score4 <= -20.1 && !t3.includes('hīna')) {
                diagnosis = '<span class="micro-tag tag-alert" style="font-size:12px;">Divergent: Stage 4 Strained by Cusp Pressure / Daridra</span>';
            } else {
                diagnosis = `<span class="micro-tag" style="font-size:12px;">Stage 3 ${st3Tier} ↔ Stage 4 ${st4Tier}</span>`;
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
                <td style="padding: 6px 8px;">${diagnosis}</td>
            `;

            tbody.appendChild(tr);
        }
    }

    // Register widget with WidgetRegistry
    if (window.widgetRegistry) {
        window.widgetRegistry.register('houses-of-life', {
            id: 'houses-of-life',
            title: 'Houses of Life (Phaladīpikā 15)',
            icon: '🏛\uFE0E',
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
