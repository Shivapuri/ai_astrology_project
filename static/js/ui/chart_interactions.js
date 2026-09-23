/**
 * Astra Chart Interactions, Inspection, Zoom & Pan
 * 
 * Manages interactive chart clicks (aspect lines, planet glyphs, signs, houses),
 * directional ray highlighting, chart zoom & pan, and pop-up inspection windows.
 */

(function() {
    // -------------------------------------------------------------
    // ShodasaVargas 16-in-1 Definitions & Modal
    // -------------------------------------------------------------
    const SHODASAVARGA_DEFS = [
        { key: "D1", name: "Rasi", title: "Physical Reality & Body" },
        { key: "D2", name: "Hora", title: "Wealth & Prosperity" },
        { key: "D3", name: "Drekkana", title: "Energy, Courage & Siblings" },
        { key: "D4", name: "Chaturthamsa", title: "Fortune & Fixed Assets" },
        { key: "D7", name: "Saptamsa", title: "Children & Progeny" },
        { key: "D9", name: "Navamsa", title: "Spouse, Dharma & The Fruit" },
        { key: "D10", name: "Dasamsa", title: "Career, Status & Public Actions" },
        { key: "D12", name: "Dwadasamsa", title: "Parents & Lineage" },
        { key: "D16", name: "Shodamsa", title: "Vehicles & Pleasures" },
        { key: "D20", name: "Vimsamsa", title: "Spiritual Progress" },
        { key: "D24", name: "Siddhamsa", title: "Higher Learning" },
        { key: "D27", name: "Bhamsa", title: "Inherent Strengths" },
        { key: "D30", name: "Trimsamsa", title: "Misfortunes & Evils" },
        { key: "D40", name: "Khavedamsa", title: "Auspicious Results" },
        { key: "D45", name: "Akshavedamsa", title: "All Spheres of Life" },
        { key: "D60", name: "Shastiamsa", title: "Past Karma (Highest Weight)" }
    ];

    let shodasaCurrentStyle = 'south';

    function openShodasaVargasModal() {
        if (typeof window.closeKalaMenu === 'function') window.closeKalaMenu();
        const modal = document.getElementById('shodasaVargasModal');
        const titleEl = document.getElementById('shodasaSubjectTitle');
        if (!modal) return;
        const currentData = window.currentChartData;
        if (currentData && currentData.subject_info && titleEl) {
            titleEl.textContent = `${currentData.subject_info.name} — ${currentData.subject_info.birth_datetime} | 16-in-1 Shodashavarga Grid`;
        }
        renderShodasaGrid();
        modal.style.display = 'flex';
    }

    function closeShodasaVargasModal() {
        const modal = document.getElementById('shodasaVargasModal');
        if (modal) modal.style.display = 'none';
    }

    function switchShodasaStyle(style) {
        shodasaCurrentStyle = style;
        document.querySelectorAll('.shodasa-modal-header .hotkey-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        const activeBtn = document.querySelector(`.shodasa-btn-${style}`);
        if (activeBtn) activeBtn.classList.add('active');
        renderShodasaGrid();
    }

    function renderShodasaGrid() {
        const container = document.getElementById('shodasaGridContainer');
        const currentSvgs = window.currentSvgs;
        if (!container || !currentSvgs) return;
        container.innerHTML = '';
        
        const notation = window.currentNotation || 'symbol';
        
        SHODASAVARGA_DEFS.forEach(def => {
            const vData = currentSvgs[def.key];
            const vSvg = (vData && vData[notation]) ? vData[notation] : vData;
            const svgMarkup = vSvg ? vSvg[shodasaCurrentStyle] : '<div style="color:var(--text-muted); padding:20px;">No SVG</div>';
            
            const card = document.createElement('div');
            card.className = 'shodasa-varga-card';
            card.innerHTML = `
                <div class="shodasa-card-header">
                    <span class="key-title">${def.key} ${def.name}</span>
                    <span class="signif-title" title="${def.title}">${def.title}</span>
                </div>
                <div class="shodasa-svg-wrapper">
                    ${svgMarkup}
                </div>
            `;
            card.style.cursor = 'pointer';
            card.title = `Click to view ${def.key} full size`;
            card.addEventListener('click', () => {
                maximizeChartDirect(def.key, shodasaCurrentStyle);
            });
            container.appendChild(card);
        });
    }

    // -------------------------------------------------------------
    // Maximize Chart Dialog & Pan/Zoom
    // -------------------------------------------------------------
    let currentMaximized = null;
    let maximizeChartZoom = 1.0;
    let maximizeChartPanX = 0;
    let maximizeChartPanY = 0;
    let maximizeChartPositionInitialized = false;

    function resetMaximizeChartPosition() {
        const card = document.getElementById('maximizeChartCard');
        if (!card) return;
        const defaultDim = Math.min(760, Math.min(window.innerWidth - 40, window.innerHeight - 60));
        card.style.width = defaultDim + 'px';
        card.style.height = defaultDim + 'px';
        card.style.left = Math.max(10, Math.round((window.innerWidth - defaultDim) / 2)) + 'px';
        card.style.top = Math.max(20, Math.round((window.innerHeight - defaultDim) / 2)) + 'px';
        maximizeChartPositionInitialized = true;
        resetMaximizeZoom();
    }

    function zoomMaximizeChart(delta) {
        maximizeChartZoom = Math.min(3.0, Math.max(0.4, maximizeChartZoom + delta));
        applyMaximizeChartZoom();
    }

    function resetMaximizeZoom() {
        maximizeChartZoom = 1.0;
        maximizeChartPanX = 0;
        maximizeChartPanY = 0;
        applyMaximizeChartZoom();
    }

    function applyMaximizeChartZoom() {
        const svg = document.querySelector('#maximizeChartContainer svg');
        if (svg) {
            svg.style.transform = `translate(${maximizeChartPanX}px, ${maximizeChartPanY}px) scale(${maximizeChartZoom})`;
        }
        const label = document.getElementById('maximizeZoomLabel');
        if (label) {
            label.textContent = `${Math.round(maximizeChartZoom * 100)}%`;
        }
    }

    function toggleMaximizeAspects() {
        const svg = document.querySelector('#maximizeChartContainer svg');
        if (svg) {
            svg.classList.toggle('aspects-hidden');
            updateMaximizeAspectsBtn();
        }
    }

    function updateMaximizeAspectsBtn() {
        const btn = document.getElementById('maximizeToggleAspectsBtn');
        const svg = document.querySelector('#maximizeChartContainer svg');
        if (!btn) return;
        if (!svg || !svg.querySelector('.aspect-lines')) {
            btn.style.display = 'none';
            return;
        }
        btn.style.display = 'inline-block';
        const isHidden = svg.classList.contains('aspects-hidden');
        btn.textContent = isHidden ? '👁 Aspects: OFF' : '👁 Aspects: ON';
        btn.style.background = isHidden ? 'var(--bg-app)' : 'var(--bg-surface-muted)';
        btn.style.color = isHidden ? 'var(--text-muted)' : 'var(--text-heading)';
    }

    function initMaximizeChartPan() {
        const container = document.getElementById('maximizeChartContainer');
        if (!container) return;

        let isPanning = false;
        let startX = 0, startY = 0;
        let origPanX = 0, origPanY = 0;

        window.addEventListener('keydown', (e) => {
            if (e.key === 'Shift') {
                container.style.cursor = 'grab';
            }
        });
        window.addEventListener('keyup', (e) => {
            if (e.key === 'Shift' && !isPanning) {
                container.style.cursor = (maximizeChartZoom > 1.05) ? 'grab' : 'default';
            }
        });

        container.addEventListener('mousedown', (e) => {
            if (e.target.closest('button, select, input, a')) return;
            const isInteractive = e.target.closest('.interactive, .interactive-aspect, text, .glyph-symbol');
            const isMiddle = (e.button === 1);
            const isShiftLeft = (e.button === 0 && e.shiftKey);
            const isBgDrag = (e.button === 0 && (!isInteractive || maximizeChartZoom > 1.05));

            if (isMiddle || isShiftLeft || isBgDrag) {
                isPanning = true;
                startX = e.clientX;
                startY = e.clientY;
                origPanX = maximizeChartPanX;
                origPanY = maximizeChartPanY;
                container.style.cursor = 'grabbing';
                e.preventDefault();

                function onPanMove(ev) {
                    if (!isPanning) return;
                    const dx = ev.clientX - startX;
                    const dy = ev.clientY - startY;
                    maximizeChartPanX = origPanX + dx;
                    maximizeChartPanY = origPanY + dy;
                    applyMaximizeChartZoom();
                }

                function onPanUp() {
                    if (!isPanning) return;
                    isPanning = false;
                    container.style.cursor = (e.shiftKey || maximizeChartZoom > 1.05) ? 'grab' : 'default';
                    document.removeEventListener('mousemove', onPanMove);
                    document.removeEventListener('mouseup', onPanUp);
                }

                document.addEventListener('mousemove', onPanMove);
                document.addEventListener('mouseup', onPanUp);
            }
        });

        container.addEventListener('wheel', (e) => {
            e.preventDefault();
            if (e.shiftKey) {
                maximizeChartPanX -= (e.deltaY || e.deltaX) * 0.8;
                applyMaximizeChartZoom();
            } else if (e.altKey || e.ctrlKey) {
                maximizeChartPanX -= (e.deltaX || 0) * 0.8;
                maximizeChartPanY -= (e.deltaY || 0) * 0.8;
                applyMaximizeChartZoom();
            } else {
                const delta = e.deltaY < 0 ? 0.08 : -0.08;
                zoomMaximizeChart(delta);
            }
        }, { passive: false });

        container.addEventListener('dblclick', (e) => {
            if (e.target.closest('button, .interactive')) return;
            resetMaximizeZoom();
        });
    }

    function maximizeChartDirect(varga, style = 'south') {
        const currentSvgs = window.currentSvgs;
        if (!currentSvgs || !currentSvgs[varga]) return;
        const vData = currentSvgs[varga];
        const notation = window.currentNotation || 'symbol';
        const vSvg = (vData && vData[notation]) ? vData[notation] : vData;
        if (!vSvg) return;

        const modal = document.getElementById('maximizeModal');
        const titleEl = document.getElementById('maximizeModalTitle');
        const container = document.getElementById('maximizeChartContainer');
        if (!modal || !titleEl || !container) return;

        const currentData = window.currentChartData;
        const subjectName = currentData && currentData.subject_info ? currentData.subject_info.name : '';
        titleEl.textContent = `${subjectName} — ${varga} (${style.toUpperCase()})`;
        container.innerHTML = vSvg[style];
        modal.style.display = 'flex';
        updateMaximizeAspectsBtn();
    }

    function maximizeChart(slot, type) {
        currentMaximized = { slot, type };
        const modal = document.getElementById('maximizeModal');
        const container = document.getElementById('maximizeChartContainer');
        const title = document.getElementById('maximizeModalTitle');
        if (!modal || !container) return;

        if (!maximizeChartPositionInitialized) {
            resetMaximizeChartPosition();
        } else {
            resetMaximizeZoom();
        }

        const currentData = window.currentChartData;
        let varga = 'D1';
        let style = type || 'south';
        const subjectName = currentData && currentData.subject_info ? currentData.subject_info.name : '';
        if (title) title.innerText = `${subjectName} — ${varga} (${style.toUpperCase()})`;

        const currentSvgs = window.currentSvgs;
        const notation = window.currentNotation || 'symbol';
        if (currentSvgs && currentSvgs[varga]) {
            const vData = currentSvgs[varga];
            const vSvg = (vData && vData[notation]) ? vData[notation] : vData;
            if (vSvg && vSvg[style]) {
                container.innerHTML = vSvg[style];
            }
        }
        modal.style.display = 'flex';
        updateMaximizeAspectsBtn();
    }

    function maximizeChartFromWidget(btn) {
        const cell = btn.closest('.grid-cell');
        if (!cell) return;
        const vargaSelect = cell.querySelector('.varga-select');
        const varga = vargaSelect ? vargaSelect.value : 'D1';
        
        let style = 'south';
        if (cell.querySelector('.view-north.active')) style = 'north';
        else if (cell.querySelector('.view-circular.active')) style = 'circular';
        else if (cell.querySelector('.view-biwheel.active')) style = 'biwheel';

        maximizeChartDirect(varga, style);
    }

    // -------------------------------------------------------------
    // Widget Chart Zoom & Pan
    // -------------------------------------------------------------
    function zoomWidgetChart(cell, delta) {
        if (!cell) return;
        const curZoom = cell._chartZoom !== undefined ? cell._chartZoom : 1.0;
        const newZoom = Math.min(4.0, Math.max(0.4, curZoom + delta));
        cell._chartZoom = Math.round(newZoom * 100) / 100;
        if (Math.abs(cell._chartZoom - 1.0) < 0.01 && Math.abs(cell._chartPanX || 0) < 15 && Math.abs(cell._chartPanY || 0) < 15) {
            cell._chartPanX = 0;
            cell._chartPanY = 0;
        }
        applyWidgetChartZoom(cell, true);
    }

    function resetWidgetChartZoom(cell) {
        if (!cell) return;
        cell._chartZoom = 1.0;
        cell._chartPanX = 0;
        cell._chartPanY = 0;
        applyWidgetChartZoom(cell, true);
    }

    function zoomWidgetChartFromBtn(btn, delta) {
        const cell = btn.closest('.grid-cell');
        if (cell) zoomWidgetChart(cell, delta);
    }

    function resetWidgetChartZoomFromBtn(btn) {
        const cell = btn.closest('.grid-cell');
        if (cell) resetWidgetChartZoom(cell);
    }

    function applyWidgetChartZoom(cell, animated = false) {
        if (!cell) return;
        const zoom = cell._chartZoom !== undefined ? cell._chartZoom : 1.0;
        const panX = cell._chartPanX !== undefined ? cell._chartPanX : 0;
        const panY = cell._chartPanY !== undefined ? cell._chartPanY : 0;
        
        const svgs = cell.querySelectorAll('.chart-view .chart-svg-container svg');
        svgs.forEach(svg => {
            svg.style.transformOrigin = 'center center';
            svg.style.transition = animated ? 'transform 0.2s cubic-bezier(0.2, 0, 0, 1)' : 'transform 0.05s ease-out';
            svg.style.transform = `translate(${panX}px, ${panY}px) scale(${zoom})`;
        });

        const activeContainer = cell.querySelector('.chart-view.active .chart-svg-container');
        if (activeContainer) {
            activeContainer.style.cursor = (zoom > 1.05) ? 'grab' : 'default';
        }
        
        const widget = cell.querySelector('.widget-chart');
        if (widget) {
            const label = widget.querySelector('.widget-zoom-label');
            if (label) {
                label.textContent = `${Math.round(zoom * 100)}%`;
            }
            const resetBtn = widget.querySelector('.btn-zoom-reset');
            const isZoomed = (Math.abs(zoom - 1.0) > 0.01 || Math.abs(panX) > 1 || Math.abs(panY) > 1);
            if (resetBtn) {
                resetBtn.style.display = isZoomed ? 'inline-flex' : 'none';
            }
            const badge = widget.querySelector('.widget-chart-zoom-badge');
            if (badge) {
                if (isZoomed) {
                    badge.classList.add('is-zoomed');
                } else {
                    badge.classList.remove('is-zoomed');
                }
            }
        }
    }

    function initWidgetChartZoomAndPan() {
        let widgetPanning = null;

        document.addEventListener('mousedown', (e) => {
            const container = e.target.closest('.chart-svg-container');
            if (!container) return;
            const cell = container.closest('.grid-cell');
            if (!cell) return;

            const isInteractive = e.target.closest('.interactive, .interactive-aspect, text, .glyph-symbol');
            const isMiddle = (e.button === 1);
            const isShiftLeft = (e.button === 0 && e.shiftKey);
            const zoom = cell._chartZoom || 1.0;
            const isBgDrag = (e.button === 0 && (!isInteractive || zoom > 1.05));

            if (isMiddle || isShiftLeft || isBgDrag) {
                widgetPanning = {
                    cell: cell,
                    container: container,
                    startX: e.clientX,
                    startY: e.clientY,
                    origPanX: cell._chartPanX || 0,
                    origPanY: cell._chartPanY || 0
                };
                container.style.cursor = 'grabbing';
                e.preventDefault();
            }
        });

        document.addEventListener('mousemove', (e) => {
            if (!widgetPanning) return;
            const dx = e.clientX - widgetPanning.startX;
            const dy = e.clientY - widgetPanning.startY;
            widgetPanning.cell._chartPanX = widgetPanning.origPanX + dx;
            widgetPanning.cell._chartPanY = widgetPanning.origPanY + dy;
            applyWidgetChartZoom(widgetPanning.cell, false);
        });

        document.addEventListener('mouseup', () => {
            if (!widgetPanning) return;
            const zoom = widgetPanning.cell._chartZoom || 1.0;
            widgetPanning.container.style.cursor = (zoom > 1.05) ? 'grab' : 'default';
            widgetPanning = null;
        });

        document.addEventListener('wheel', (e) => {
            const container = e.target.closest('.chart-svg-container');
            if (!container) return;
            const cell = container.closest('.grid-cell');
            if (!cell) return;

            e.preventDefault();
            const curZoom = cell._chartZoom || 1.0;

            if (e.shiftKey) {
                cell._chartPanX = (cell._chartPanX || 0) - (e.deltaY || e.deltaX) * 0.8;
                applyWidgetChartZoom(cell, false);
            } else if (e.altKey || e.ctrlKey) {
                cell._chartPanX = (cell._chartPanX || 0) - (e.deltaX || 0) * 0.8;
                cell._chartPanY = (cell._chartPanY || 0) - (e.deltaY || 0) * 0.8;
                applyWidgetChartZoom(cell, false);
            } else {
                const delta = e.deltaY < 0 ? 0.08 : -0.08;
                zoomWidgetChart(cell, delta);
            }
        }, { passive: false });
    }

    // -------------------------------------------------------------
    // Floating Inspection Windows
    // -------------------------------------------------------------
    function setActiveFloatingNav(tabId) {
        document.querySelectorAll('.floating-nav-pill').forEach(pill => pill.classList.remove('active'));
        if (tabId) {
            const btn = document.getElementById(tabId);
            if (btn) btn.classList.add('active');
        }
    }

    function resetFloatingWindowPosition() {
        const card = document.getElementById('widgetMaximizeCard');
        if (!card) return;
        const defaultWidth = Math.min(820, window.innerWidth - 40);
        const defaultHeight = Math.min(540, window.innerHeight - 80);
        card.style.width = defaultWidth + 'px';
        card.style.height = defaultHeight + 'px';
        card.style.left = Math.max(20, Math.round((window.innerWidth - defaultWidth) / 2)) + 'px';
        card.style.top = Math.max(40, Math.round((window.innerHeight - defaultHeight) / 2)) + 'px';
        card.classList.remove('collapsed');
        const collapseBtn = document.getElementById('widgetMaximizeCollapseBtn');
        if (collapseBtn) collapseBtn.textContent = '−';
    }

    function toggleFloatingCollapse() {
        const card = document.getElementById('widgetMaximizeCard');
        const collapseBtn = document.getElementById('widgetMaximizeCollapseBtn');
        if (!card) return;
        const isCollapsed = card.classList.toggle('collapsed');
        if (collapseBtn) collapseBtn.textContent = isCollapsed ? '+' : '−';
    }

    function openFloatingPlanetaryInfo() {
        if (typeof window.closeKalaMenu === 'function') window.closeKalaMenu();
        const modal = document.getElementById('widgetMaximizeModal');
        const titleEl = document.getElementById('widgetMaximizeModalTitle');
        const container = document.getElementById('widgetMaximizeContainer');
        if (!modal || !titleEl || !container) return;
        
        setActiveFloatingNav('nav-btn-planet');
        const currentData = window.currentChartData;
        titleEl.textContent = (currentData ? currentData.subject_info.name + " — " : "") + "Planetary Information Table";
        const tmpl = document.getElementById('tmpl-planetary-info');
        if (tmpl) {
            container.innerHTML = '';
            const clone = tmpl.content.cloneNode(true);
            container.appendChild(clone);
            if (typeof window.populatePlanetaryInfoTable === 'function') {
                window.populatePlanetaryInfoTable(container);
            }
            modal.style.display = 'flex';
        }
    }

    function openFloatingAshtakavarga() {
        if (typeof window.closeKalaMenu === 'function') window.closeKalaMenu();
        const modal = document.getElementById('widgetMaximizeModal');
        const titleEl = document.getElementById('widgetMaximizeModalTitle');
        const container = document.getElementById('widgetMaximizeContainer');
        if (!modal || !titleEl || !container) return;
        
        setActiveFloatingNav('nav-btn-ashtaka');
        const currentData = window.currentChartData;
        titleEl.textContent = (currentData ? currentData.subject_info.name + " — " : "") + "AshtakaVarga Transit & Reductions (337 SAV)";
        const tmpl = document.getElementById('tmpl-ashtakavarga');
        if (tmpl) {
            container.innerHTML = '';
            const clone = tmpl.content.cloneNode(true);
            container.appendChild(clone);
            if (typeof window.updateAshtakavargaWidget === 'function') {
                window.updateAshtakavargaWidget(container);
            }
            modal.style.display = 'flex';
        }
    }

    function openFloatingShadbala() {
        if (typeof window.closeKalaMenu === 'function') window.closeKalaMenu();
        const modal = document.getElementById('widgetMaximizeModal');
        const titleEl = document.getElementById('widgetMaximizeModalTitle');
        const container = document.getElementById('widgetMaximizeContainer');
        if (!modal || !titleEl || !container) return;
        
        setActiveFloatingNav('nav-btn-shadbala');
        const currentData = window.currentChartData;
        titleEl.textContent = (currentData ? currentData.subject_info.name + " — " : "") + "Shad Bala Breakdown Details";
        const tmpl = document.getElementById('tmpl-shadbala-table');
        if (tmpl) {
            container.innerHTML = '';
            const clone = tmpl.content.cloneNode(true);
            container.appendChild(clone);
            if (typeof window.updateShadbalaTable === 'function') {
                window.updateShadbalaTable();
            }
            modal.style.display = 'flex';
        }
    }

    function openBhavaCuspsModal() {
        if (typeof window.closeKalaMenu === 'function') window.closeKalaMenu();
        const modal = document.getElementById('widgetMaximizeModal');
        const titleEl = document.getElementById('widgetMaximizeModalTitle');
        const container = document.getElementById('widgetMaximizeContainer');
        const currentData = window.currentChartData;
        if (!modal || !titleEl || !container || !currentData) return;
        
        setActiveFloatingNav('nav-btn-bhava');
        titleEl.textContent = currentData.subject_info.name + " — Bhava Chalita (12 Campanus Cusps)";
        const cusps = (currentData.vargas && currentData.vargas.D1 && currentData.vargas.D1.cusps) || [];
        const bhavas = (currentData.vargas && currentData.vargas.D1 && currentData.vargas.D1.bhavas) || [];
        
        function formatDeg(deg_float) {
            if (deg_float === undefined || deg_float === null) return "00:00";
            let d = Math.floor(deg_float);
            let m = Math.round((deg_float - d) * 60);
            if (m === 60) { d += 1; m = 0; }
            return `${d.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}`;
        }

        const signLords = {
            'Aries': 'Mars', 'Taurus': 'Venus', 'Gemini': 'Mercury', 'Cancer': 'Moon',
            'Leo': 'Sun', 'Virgo': 'Mercury', 'Libra': 'Venus', 'Scorpio': 'Mars',
            'Sagittarius': 'Jupiter', 'Capricorn': 'Saturn', 'Aquarius': 'Saturn', 'Pisces': 'Jupiter'
        };
        const signGlyphs = {
            'Aries': '♈', 'Taurus': '♉', 'Gemini': '♊', 'Cancer': '♋',
            'Leo': '♌', 'Virgo': '♍', 'Libra': '♎', 'Scorpio': '♏',
            'Sagittarius': '♐', 'Capricorn': '♑', 'Aquarius': '♒', 'Pisces': '♓'
        };
        
        let html = `
            <table class="dignity-grid" style="width:100%; border-collapse:collapse; font-size:13px; text-align:center;">
                <thead>
                    <tr>
                        <th style="padding:7px 10px;">Bhava</th>
                        <th style="padding:7px 10px;">Sign</th>
                        <th style="padding:7px 10px;">Lord</th>
                        <th style="padding:7px 10px;">Cusp (Deg:Min)</th>
                        <th style="padding:7px 10px;">Longitude</th>
                        <th style="padding:7px 10px;">Occupants (Campanus)</th>
                    </tr>
                </thead>
                <tbody>
        `;
        cusps.forEach((c, idx) => {
            const lord = signLords[c.sign] || '—';
            const glyph = signGlyphs[c.sign] || '';
            const bhavaData = bhavas[idx] || {};
            const planets = (bhavaData.planets || []).filter(p => p !== 'Asc');
            const planetsStr = planets.length > 0 
                ? planets.map(p => `<span style="display:inline-block; padding:2px 8px; margin:1px; background:var(--bg-surface-muted); border:1px solid var(--border-medium); border-radius:10px; font-size:11px; font-weight:600; color:var(--text-heading);">${p}</span>`).join(' ')
                : `<span style="color:var(--text-subtle);">—</span>`;
            
            html += `
                <tr>
                    <td style="padding:7px 10px;"><strong>House ${idx + 1}</strong></td>
                    <td style="padding:7px 10px;"><span style="color:var(--border-highlight); font-weight:bold; margin-right:4px;">${glyph}</span>${c.sign}</td>
                    <td style="padding:7px 10px; font-weight:600; color:var(--text-heading);">${lord}</td>
                    <td style="padding:7px 10px; font-family:monospace; font-weight:600;">${formatDeg(c.degree_0_to_30)}</td>
                    <td style="padding:7px 10px; font-family:monospace;">${c.longitude.toFixed(2)}°</td>
                    <td style="padding:7px 10px;">${planetsStr}</td>
                </tr>
            `;
        });
        html += `</tbody></table>`;
        container.innerHTML = html;
        modal.style.display = 'flex';
    }

    function maximizeTableFromWidget(btn) {
        const cell = btn.closest('.grid-cell');
        if (!cell) return;
        const widgetType = cell.dataset.widget;
        const modal = document.getElementById('widgetMaximizeModal');
        const titleEl = document.getElementById('widgetMaximizeModalTitle');
        const container = document.getElementById('widgetMaximizeContainer');
        if (!modal || !titleEl || !container) return;

        resetFloatingWindowPosition();

        const titleText = cell.querySelector('.chart-toolbar strong, .chart-toolbar .context-info-title, .chart-toolbar .aspect-table-title')?.textContent || 'Table';
        const currentData = window.currentChartData;
        const subjectPrefix = currentData && currentData.subject_info ? `${currentData.subject_info.name} — ` : '';
        titleEl.textContent = subjectPrefix + titleText;

        const navPills = {
            'planetary-info': 'nav-btn-planet',
            'ashtakavarga': 'nav-btn-ashtaka',
            'shadbala-table': 'nav-btn-shadbala'
        };
        setActiveFloatingNav(navPills[widgetType] || null);

        const tmpl = document.getElementById('tmpl-' + widgetType);
        if (tmpl) {
            container.innerHTML = '';
            const clone = tmpl.content.cloneNode(true);
            container.appendChild(clone);
            
            // Delegate update
            if (window.widgetRegistry) {
                window.widgetRegistry.renderWidget(widgetType, container, currentData);
            }
            modal.style.display = 'flex';
        }
    }

    // -------------------------------------------------------------
    // Astrological Selection & Drishti Aspect Rays
    // -------------------------------------------------------------
    window.clearAstrologicalEntitySelection = function() {
        window.currentSelectedEntity = null;
        
        document.querySelectorAll('svg').forEach(svg => {
            svg.classList.remove('highlight-mode', 'aspects-filtered');
            svg.querySelectorAll('.interactive-aspect').forEach(l => {
                l.classList.remove('aspect-focused', 'aspect-outgoing', 'aspect-incoming');
            });
            svg.querySelectorAll('.interactive-aspect-badge').forEach(b => {
                b.classList.remove('aspect-focused', 'aspect-outgoing', 'aspect-incoming');
            });
            svg.querySelectorAll('.planet-glyph, .interactive[data-type="planet"]').forEach(g => {
                g.classList.remove('planet-focused', 'highlight-source', 'highlight-active');
            });
            svg.querySelectorAll('.interactive[data-type="sign"]').forEach(s => {
                s.classList.remove('highlight-source', 'highlight-active');
            });
            svg.querySelectorAll('.interactive[data-type="house"]').forEach(h => {
                h.classList.remove('highlight-source', 'highlight-active');
            });
        });

        document.querySelectorAll('.interactive-table-row').forEach(row => {
            row.classList.remove('table-row-selected', 'table-row-outgoing', 'table-row-incoming');
            row.querySelectorAll('.aspect-dynamic-badge').forEach(b => b.remove());
        });
    };

    window.selectAstrologicalEntity = function(type, id, clickedVarga = 'D1') {
        if (!type || !id) return;
        
        if (window.currentSelectedEntity && window.currentSelectedEntity.type === type && window.currentSelectedEntity.id === id) {
            window.clearAstrologicalEntitySelection();
            return;
        }

        window.clearAstrologicalEntitySelection();
        window.currentSelectedEntity = { type, id, varga: clickedVarga };

        if (type === 'planet') {
            highlightPlanetAspects(id, clickedVarga);
        } else if (type === 'sign') {
            highlightSignAspects(id, clickedVarga);
        } else if (type === 'house') {
            highlightHouse(id, clickedVarga);
        }

        if (typeof window.updateContextInfoPanel === 'function') {
            window.updateContextInfoPanel(type, id, clickedVarga);
        }
    };

    function highlightPlanetAspects(planetId, varga = 'D1') {
        const currentData = window.currentChartData;
        if (!currentData) return;
        const vData = (currentData.vargas && currentData.vargas[varga]) ? currentData.vargas[varga] : currentData.vargas.D1;
        if (!vData) return;
        const vGrahas = vData.grahas || {};
        const vLagna = vData.lagna || {};
        const adv = (currentData.varga_advanced_aspects && currentData.varga_advanced_aspects[varga])
            ? currentData.varga_advanced_aspects[varga]
            : (currentData ? currentData.advanced_aspects : null);

        const sunLon = (vGrahas.Sun && vGrahas.Sun.longitude) || 0;
        const moonLon = (vGrahas.Moon && vGrahas.Moon.longitude) || 0;

        function isBeneficPlanet(p) {
            if (['Jupiter', 'Venus', 'Mercury'].includes(p)) return true;
            if (p === 'Moon') {
                const diff = (moonLon - sunLon + 360.0) % 360.0;
                return diff < 180.0;
            }
            return false;
        }

        // 1. Chart SVG updates
        document.querySelectorAll('svg').forEach(svg => {
            if (svg.querySelector('.aspect-lines')) {
                svg.classList.add('aspects-filtered');
                svg.querySelectorAll('.interactive-aspect').forEach(l => {
                    const fromP = l.getAttribute('data-from');
                    const toP = l.getAttribute('data-to');
                    const virVal = parseFloat(l.getAttribute('data-virupas') || '0');
                    if (virVal < 30.0) return;
                    if (fromP === planetId) {
                        l.classList.add('aspect-focused', 'aspect-outgoing');
                    } else if (toP === planetId) {
                        l.classList.add('aspect-focused', 'aspect-incoming');
                    }
                });
                svg.querySelectorAll('.interactive-aspect-badge').forEach(b => {
                    const fromP = b.getAttribute('data-from');
                    const toP = b.getAttribute('data-to');
                    const virVal = parseFloat(b.getAttribute('data-virupas') || '0');
                    if (virVal < 30.0) return;
                    if (fromP === planetId) {
                        b.classList.add('aspect-focused', 'aspect-outgoing');
                    } else if (toP === planetId) {
                        b.classList.add('aspect-focused', 'aspect-incoming');
                    }
                });
            }

            svg.querySelectorAll(`.interactive[data-type="planet"][data-id="${planetId}"]`).forEach(node => {
                node.classList.add('planet-focused', 'highlight-source');
            });

            let occupiedSign = null;
            if (planetId === 'Lagna') {
                occupiedSign = vLagna.sign;
            } else if (vGrahas[planetId]) {
                occupiedSign = vGrahas[planetId].sign;
            }

            if (occupiedSign) {
                svg.classList.add('highlight-mode');
                svg.querySelectorAll(`.interactive[data-type="sign"][data-id="${occupiedSign}"]`).forEach(node => {
                    node.classList.add('highlight-source');
                });
            }
        });

        // 2. Table row updates
        let planetLon = 0;
        if (planetId === 'Lagna') {
            planetLon = vLagna.longitude || 0;
        } else if (vGrahas[planetId]) {
            planetLon = vGrahas[planetId].longitude || 0;
        }

        document.querySelectorAll('.interactive-table-row[data-type="planet"]').forEach(row => {
            const rowId = row.getAttribute('data-id');
            const firstCell = row.querySelector('td');
            if (rowId === planetId) {
                row.classList.add('table-row-selected');
                if (firstCell && !firstCell.querySelector('.aspect-selected-tag')) {
                    const badge = document.createElement('span');
                    badge.className = 'aspect-dynamic-badge aspect-selected-tag';
                    badge.style.cssText = 'background:var(--status-neutral-bg); color:var(--status-neutral); border:1px solid var(--status-neutral-border);';
                    badge.textContent = '★ Selected';
                    firstCell.appendChild(badge);
                }
            } else {
                let outVir = 0;
                if (planetId !== 'Lagna' && adv && adv.planets && adv.planets[rowId] && adv.planets[rowId][planetId]) {
                    outVir = Math.round(adv.planets[rowId][planetId].raw || 0);
                }

                let inVir = 0;
                if (planetId === 'Lagna') {
                    if (adv && adv.cusps && (adv.cusps[1] || adv.cusps['1']) && (adv.cusps[1] || adv.cusps['1'])[rowId]) {
                        inVir = Math.round((adv.cusps[1] || adv.cusps['1'])[rowId].raw || 0);
                    }
                } else if (adv && adv.planets && adv.planets[planetId] && adv.planets[planetId][rowId]) {
                    inVir = Math.round(adv.planets[planetId][rowId].raw || 0);
                }

                let rowLon = 0;
                if (rowId === 'Lagna') {
                    rowLon = vLagna.longitude || 0;
                } else if (vGrahas[rowId]) {
                    rowLon = vGrahas[rowId].longitude || 0;
                }

                if (outVir >= 30) {
                    row.classList.add('table-row-outgoing');
                    const isBen = isBeneficPlanet(planetId);
                    const degOut = Math.round((rowLon - planetLon + 360.0) % 360.0);
                    const housesAway = Math.floor(degOut / 30.0) + 1;
                    const tip = `Outgoing glance from ${planetId} to ${rowId}: ${degOut}° (${housesAway} houses away), ${outVir} Virūpas. Line: ${isBen ? 'Benefic (Continuous / Solid)' : 'Malefic (Dashed)'}`;
                    if (firstCell) {
                        const b = document.createElement('span');
                        b.className = `aspect-dynamic-badge aspect-tag-outgoing ${isBen ? 'benefic' : 'malefic'}`;
                        b.title = tip;
                        b.innerHTML = `➔ ${isBen ? 'Solid' : 'Dashed'} ${degOut}° (${outVir}v)`;
                        firstCell.appendChild(b);
                    }
                }

                if (inVir >= 30) {
                    row.classList.add('table-row-incoming');
                    const isInBen = isBeneficPlanet(rowId);
                    const degIn = Math.round((planetLon - rowLon + 360.0) % 360.0);
                    const housesAway = Math.floor(degIn / 30.0) + 1;
                    const tip = `Incoming glance from ${rowId} onto ${planetId}: ${degIn}° (${housesAway} houses away), ${inVir} Virūpas. Line: ${isInBen ? 'Benefic (Continuous / Solid)' : 'Malefic (Dashed)'}`;
                    if (firstCell) {
                        const b = document.createElement('span');
                        b.className = `aspect-dynamic-badge aspect-tag-incoming ${isInBen ? 'benefic' : 'malefic'}`;
                        b.title = tip;
                        b.innerHTML = `⬅ ${isInBen ? 'Solid' : 'Dashed'} ${degIn}° (${inVir}v)`;
                        firstCell.appendChild(b);
                    }
                }
            }
        });
    }

    function highlightSignAspects(signId, varga = 'D1') {
        const currentData = window.currentChartData;
        if (!currentData) return;
        const vData = (currentData.vargas && currentData.vargas[varga]) ? currentData.vargas[varga] : currentData.vargas.D1;
        const vGrahas = (vData && vData.grahas) || {};
        const vLagna = (vData && vData.lagna) || {};

        const SIGN_ASPECTS = {
            'Aries': ['Leo', 'Scorpio', 'Aquarius'],
            'Taurus': ['Cancer', 'Libra', 'Capricorn'],
            'Gemini': ['Virgo', 'Sagittarius', 'Pisces'],
            'Cancer': ['Scorpio', 'Aquarius', 'Taurus'],
            'Leo': ['Libra', 'Capricorn', 'Aries'],
            'Virgo': ['Gemini', 'Sagittarius', 'Pisces'],
            'Libra': ['Aquarius', 'Taurus', 'Leo'],
            'Scorpio': ['Capricorn', 'Aries', 'Cancer'],
            'Sagittarius': ['Pisces', 'Gemini', 'Virgo'],
            'Capricorn': ['Aries', 'Cancer', 'Libra'],
            'Aquarius': ['Taurus', 'Leo', 'Scorpio'],
            'Pisces': ['Virgo', 'Sagittarius', 'Gemini']
        };

        const aspectedSigns = SIGN_ASPECTS[signId] || [];

        document.querySelectorAll('svg').forEach(svg => {
            svg.classList.add('highlight-mode');
            svg.querySelectorAll(`.interactive[data-type="sign"][data-id="${signId}"]`).forEach(node => {
                node.classList.add('highlight-source');
            });
            for (const [pName, pData] of Object.entries(vGrahas)) {
                if (pData.sign === signId) {
                    svg.querySelectorAll(`.interactive[data-type="planet"][data-id="${pName}"]`).forEach(node => {
                        node.classList.add('highlight-source');
                    });
                }
            }
            if (vLagna.sign === signId) {
                svg.querySelectorAll(`.interactive[data-type="planet"][data-id="Lagna"]`).forEach(node => {
                    node.classList.add('highlight-source');
                });
            }

            aspectedSigns.forEach(asSign => {
                svg.querySelectorAll(`.interactive[data-type="sign"][data-id="${asSign}"]`).forEach(node => {
                    node.classList.add('highlight-active');
                });
                for (const [pName, pData] of Object.entries(vGrahas)) {
                    if (pData.sign === asSign) {
                        svg.querySelectorAll(`.interactive[data-type="planet"][data-id="${pName}"]`).forEach(node => {
                            node.classList.add('highlight-active');
                        });
                    }
                }
                if (vLagna.sign === asSign) {
                    svg.querySelectorAll(`.interactive[data-type="planet"][data-id="Lagna"]`).forEach(node => {
                        node.classList.add('highlight-active');
                    });
                }
            });
        });

        document.querySelectorAll('.interactive-table-row[data-type="sign"]').forEach(row => {
            const rowSign = row.getAttribute('data-id');
            const firstCell = row.querySelector('td');
            if (rowSign === signId) {
                row.classList.add('table-row-selected');
                if (firstCell && !firstCell.querySelector('.aspect-selected-tag')) {
                    const b = document.createElement('span');
                    b.className = 'aspect-dynamic-badge aspect-selected-tag';
                    b.style.cssText = 'background:var(--status-neutral-bg); color:var(--status-neutral); border:1px solid var(--status-neutral-border);';
                    b.textContent = '★ Selected Sign';
                    firstCell.appendChild(b);
                }
            } else if (aspectedSigns.includes(rowSign)) {
                row.classList.add('table-row-outgoing');
                if (firstCell) {
                    const b = document.createElement('span');
                    b.className = 'aspect-dynamic-badge aspect-tag-outgoing benefic';
                    b.title = `Mutual Rāśi Dṛṣṭi with ${signId}`;
                    b.textContent = 'Mutual Rāśi Dṛṣṭi';
                    firstCell.appendChild(b);
                }
            }
        });
    }

    function highlightHouse(houseNum, varga = 'D1') {
        const hNum = parseInt(String(houseNum).replace(/[^0-9]/g, ''), 10) || 1;
        document.querySelectorAll('svg').forEach(svg => {
            svg.classList.add('highlight-mode');
            svg.querySelectorAll(`.interactive[data-type="house"][data-id="${hNum}"], .interactive[data-type="house"][data-id="H${hNum}"], .interactive[data-type="house"][data-id="${houseNum}"]`).forEach(node => {
                node.classList.add('highlight-source');
            });
        });
    }

    // -------------------------------------------------------------
    // Delegated Interactive Element Clicks
    // -------------------------------------------------------------
    document.addEventListener('click', (e) => {
        const centerCircle = e.target.closest('.interactive-center-circle');
        if (centerCircle) {
            const parentSvg = centerCircle.closest('svg');
            if (parentSvg && parentSvg.classList.contains('aspects-filtered')) {
                window.clearAstrologicalEntitySelection();
            } else if (parentSvg) {
                parentSvg.classList.toggle('aspects-hidden');
            }
            return;
        }

        const aspectLine = e.target.closest('.interactive-aspect, .interactive-aspect-badge');
        if (aspectLine) {
            const fromP = aspectLine.getAttribute('data-from');
            const toP = aspectLine.getAttribute('data-to');
            const virupas = aspectLine.getAttribute('data-virupas');
            const deg = aspectLine.getAttribute('data-deg');
            const rule = aspectLine.getAttribute('data-rule') || '';
            const nature = aspectLine.getAttribute('data-nature') || '';
            const isBenefic = aspectLine.getAttribute('data-benefic') === 'true';
            
            window.selectAstrologicalEntity('planet', fromP);

            const standaloneInfo = document.getElementById('context-info-content');
            if (standaloneInfo) {
                standaloneInfo.innerHTML = `
                    <h3>Graha Dṛṣṭi Aspect</h3>
                    <div style="font-size: 14px; margin-bottom: 8px;"><strong>From:</strong> ${fromP} &nbsp; ➔ &nbsp; <strong>To:</strong> ${toP}</div>
                    <p><strong>Angular Separation:</strong> ${deg}° (${virupas} / 60 Virūpas)</p>
                    <p><strong>Parāśara Rule:</strong> ${rule}</p>
                    <p><strong>Influence:</strong> <span class="${isBenefic ? 'text-benefic' : 'text-malefic'}" style="font-weight:bold;">${nature}</span> (${isBenefic ? 'Continuous / Solid Line' : 'Dashed Line'})</p>
                `;
            }
            return;
        }

        const el = e.target.closest('.interactive, .interactive-table-row');
        if (el) {
            const type = el.getAttribute('data-type');
            const id = el.getAttribute('data-id');
            if (type && id) {
                let clickedVarga = 'D1';
                const cell = el.closest('.grid-cell');
                if (cell) {
                    const vSel = cell.querySelector('.varga-select');
                    if (vSel) clickedVarga = vSel.value;
                }
                window.selectAstrologicalEntity(type, id, clickedVarga);
                return;
            }
        }

        const cellContainer = e.target.closest('.grid-cell');
        if (cellContainer && !e.target.closest('.interactive, .interactive-table-row, button, input, select, a')) {
            window.clearAstrologicalEntitySelection();
        }
    });

    // Expose functions globally
    window.openShodasaVargasModal = openShodasaVargasModal;
    window.closeShodasaVargasModal = closeShodasaVargasModal;
    window.switchShodasaStyle = switchShodasaStyle;
    window.renderShodasaGrid = renderShodasaGrid;
    window.resetMaximizeChartPosition = resetMaximizeChartPosition;
    window.zoomMaximizeChart = zoomMaximizeChart;
    window.resetMaximizeZoom = resetMaximizeZoom;
    window.applyMaximizeChartZoom = applyMaximizeChartZoom;
    window.toggleMaximizeAspects = toggleMaximizeAspects;
    window.updateMaximizeAspectsBtn = updateMaximizeAspectsBtn;
    window.initMaximizeChartPan = initMaximizeChartPan;
    window.maximizeChartDirect = maximizeChartDirect;
    window.maximizeChart = maximizeChart;
    window.maximizeChartFromWidget = maximizeChartFromWidget;
    window.zoomWidgetChart = zoomWidgetChart;
    window.resetWidgetChartZoom = resetWidgetChartZoom;
    window.zoomWidgetChartFromBtn = zoomWidgetChartFromBtn;
    window.resetWidgetChartZoomFromBtn = resetWidgetChartZoomFromBtn;
    window.applyWidgetChartZoom = applyWidgetChartZoom;
    window.initWidgetChartZoomAndPan = initWidgetChartZoomAndPan;
    window.setActiveFloatingNav = setActiveFloatingNav;
    window.resetFloatingWindowPosition = resetFloatingWindowPosition;
    window.toggleFloatingCollapse = toggleFloatingCollapse;
    window.openFloatingPlanetaryInfo = openFloatingPlanetaryInfo;
    window.openFloatingAshtakavarga = openFloatingAshtakavarga;
    window.openFloatingShadbala = openFloatingShadbala;
    window.openBhavaCuspsModal = openBhavaCuspsModal;
    window.highlightPlanetAspects = highlightPlanetAspects;
    window.highlightSignAspects = highlightSignAspects;
    window.highlightHouse = highlightHouse;
    window.maximizeTableFromWidget = maximizeTableFromWidget;
})();
