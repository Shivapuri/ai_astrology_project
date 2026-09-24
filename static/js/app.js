/**
 * Astra Main Application Controller
 *
 * Coordinates Split.js workspace geometry, pluggable widget assignment,
 * birth time rectification navigation, calculation modes, hotkeys,
 * and application bootstrap.
 */

// ==========================================
// Global Application State & Storage Keys
// ==========================================
var currentChartData = window.currentChartData || null;
var currentSvgs = window.currentSvgs || null;
let currentLoadedNative = window.currentLoadedNative || null;
let activePreviewOffsetSeconds = window.activePreviewOffsetSeconds || 0;
let currentPreviewTime = window.currentPreviewTime || null;
let currentPreviewDate = window.currentPreviewDate || null;
let stepperAbortController = null;

let currentNotation = localStorage.getItem('astra_notation') || "symbol";
let showSiSigns = true;
let currentD10Mode = localStorage.getItem('astra_d10_mode') || "reverse";
let currentD24Mode = localStorage.getItem('astra_d24_mode') || "reverse";
let currentNakshatraSystem = localStorage.getItem('astra_nakshatra_system') || "ERNST_DHRUVA";

let currentActiveCell = null;
let splitInstances = [];
let splitInstance = null;
let infoSplitInstance = null;

// ==========================================
// UI Helpers & Toggles
// ==========================================
function toggleHelp(id) {
    const el = document.getElementById(id);
    if (!el) return;
    el.style.display = (el.style.display === 'none') ? 'block' : 'none';
}

function formatToDDMMYYYY(dateStr) {
    if (!dateStr) return '';
    dateStr = String(dateStr).trim();

    // 1. Slashes: YYYY/MM/DD or DD/MM/YYYY
    if (dateStr.includes('/')) {
        const parts = dateStr.split('/');
        if (parts.length === 3) {
            if (parts[0].length === 4 || Math.abs(parseInt(parts[0], 10)) > 31) {
                const y = parts[0];
                const m = parts[1].padStart(2, '0');
                const d = parts[2].padStart(2, '0');
                return `${d}/${m}/${y}`;
            } else {
                const d = parts[0].padStart(2, '0');
                const m = parts[1].padStart(2, '0');
                const y = parts[2];
                return `${d}/${m}/${y}`;
            }
        }
    }

    // 2. Dots: DD.MM.YYYY
    if (dateStr.includes('.')) {
        const parts = dateStr.split('.');
        if (parts.length === 3) {
            const d = parts[0].padStart(2, '0');
            const m = parts[1].padStart(2, '0');
            const y = parts[2];
            return `${d}/${m}/${y}`;
        }
    }

    // 3. Dashes: YYYY-MM-DD
    if (dateStr.includes('-')) {
        const parts = dateStr.split('-');
        if (parts.length === 3) {
            if (parts[0].length === 4) {
                const y = parts[0];
                const m = parts[1].padStart(2, '0');
                const d = parts[2].padStart(2, '0');
                return `${d}/${m}/${y}`;
            } else {
                const d = parts[0].padStart(2, '0');
                const m = parts[1].padStart(2, '0');
                const y = parts[2];
                return `${d}/${m}/${y}`;
            }
        }
    }
    return dateStr;
}

// ==========================================
// Width-Adaptive Scaling for Data Tables
// ==========================================
const scaleObserver = new ResizeObserver(entries => {
    for (let entry of entries) {
        const cell = entry.target;
        const contentDiv = cell.querySelector('.grid-cell-content');
        if (!contentDiv) continue;

        const wrapper = contentDiv.querySelector('.scale-wrapper');
        if (!wrapper) continue;

        // Reset transform to measure natural size
        wrapper.style.transform = 'none';

        const table = wrapper.querySelector('table');
        if (!table) continue;

        const container = wrapper.closest('.responsive-table-container') || contentDiv;
        const availW = container.clientWidth - 4;
        const naturalW = table.scrollWidth || table.offsetWidth;

        if (naturalW > 0 && availW > 0) {
            if (naturalW > availW) {
                // Fit to width down to a legible floor of 0.78
                const scale = Math.max(0.78, availW / naturalW);
                wrapper.style.transform = `scale(${scale})`;
                wrapper.style.transformOrigin = 'top left';
            } else {
                wrapper.style.transform = 'none';
            }
        }
    }
});

function observeGridCells() {
    document.querySelectorAll('.grid-cell').forEach(cell => {
        scaleObserver.observe(cell);
    });
}

function attachGutterAutoFit() {
    document.querySelectorAll('.gutter.gutter-horizontal').forEach(gutter => {
        if (gutter._hasAutoFit) return;
        gutter._hasAutoFit = true;
        gutter.title = "Drag to resize | Double-click to auto-fit to table width";
        gutter.addEventListener('dblclick', function() {
            const prevCol = gutter.previousElementSibling;
            if (!prevCol) return;

            let maxTableW = 0;
            prevCol.querySelectorAll('table').forEach(tbl => {
                const w = tbl.scrollWidth;
                if (w > maxTableW) maxTableW = w;
            });

            if (maxTableW > 0) {
                const containerW = document.getElementById('grid-container').clientWidth;
                const desiredPx = maxTableW + 20;
                const desiredPct = Math.min(60, Math.max(20, (desiredPx / containerW) * 100));

                const mainSplit = splitInstances[0];
                if (mainSplit) {
                    const currentSizes = mainSplit.getSizes();
                    const cols = Array.from(document.querySelectorAll('#grid-container > .split-col'));
                    const idx = cols.indexOf(prevCol);
                    if (idx !== -1 && currentSizes.length > idx) {
                        const oldSize = currentSizes[idx];
                        const diff = desiredPct - oldSize;
                        currentSizes[idx] = desiredPct;
                        const adjIdx = (idx === currentSizes.length - 1) ? idx - 1 : idx + 1;
                        currentSizes[adjIdx] = Math.max(15, currentSizes[adjIdx] - diff);
                        mainSplit.setSizes(currentSizes);
                        saveLayoutState();
                    }
                }
            }
        });
    });
}

// ==========================================
// Split.js Workspace Geometry & Layouts
// ==========================================
function saveLayoutState() {
    const layoutType = document.getElementById('layoutSelect')?.value;
    if (!layoutType) return;
    const cells = Array.from(document.querySelectorAll('.grid-cell')).map(c => {
        const vSel = c.querySelector('.varga-select');
        const outerSel = c.querySelector('.biwheel-outer-select');
        let chartStyle = 'south';
        if (c.querySelector('.view-north.active')) chartStyle = 'north';
        else if (c.querySelector('.view-circular.active')) chartStyle = 'circular';
        else if (c.querySelector('.view-biwheel.active')) chartStyle = 'biwheel';
        return {
            id: c.id,
            widget: c.dataset.widget || 'empty',
            varga: vSel ? vSel.value : 'D1',
            biwheel_outer: outerSel ? outerSel.value : 'D9',
            chart_style: chartStyle,
            root_planet: c.dataset.rootPlanet || 'Lagna'
        };
    });
    localStorage.setItem('astra_layout_' + layoutType, JSON.stringify(cells));
    localStorage.setItem('astra_current_layout', layoutType);
}

function changeLayout(layoutType) {
    // Destroy old splits
    splitInstances.forEach(s => {
        try { s.destroy(); } catch(e) {}
    });
    splitInstances = [];

    const container = document.getElementById('grid-container');
    if (!container) return;
    container.innerHTML = '';
    if (layoutType === 'tripod-of-life' || layoutType === '8cell' || layoutType === 'big-four') {
        container.style.flexDirection = 'column';
    } else {
        container.style.flexDirection = 'row';
    }

    if (layoutType === 'kala') {
        container.innerHTML = `
            <div id="col1" class="split-col" style="height:100%; display:flex; flex-direction:column;">
                <div class="grid-cell" id="cell1" style="height:100%;"><div class="grid-cell-content"></div></div>
            </div>
            <div id="col2" class="split-col" style="height:100%; display:flex; flex-direction:column;">
                <div class="grid-cell" id="cell2"><div class="grid-cell-content"></div></div>
                <div class="grid-cell" id="cell3"><div class="grid-cell-content"></div></div>
                <div class="grid-cell" id="cell4"><div class="grid-cell-content"></div></div>
            </div>
            <div id="col3" class="split-col" style="height:100%; display:flex; flex-direction:column;">
                <div class="grid-cell" id="cell5"><div class="grid-cell-content"></div></div>
                <div class="grid-cell" id="cell6"><div class="grid-cell-content"></div></div>
                <div class="grid-cell" id="cell7"><div class="grid-cell-content"></div></div>
            </div>
        `;
        splitInstances.push(Split(['#col1', '#col2', '#col3'], { sizes: [50, 25, 25], minSize: [360, 260, 260], gutterSize: 4 }));
        splitInstances.push(Split(['#cell2', '#cell3', '#cell4'], { direction: 'vertical', sizes: [33, 33, 34], minSize: [110, 110, 110], gutterSize: 4 }));
        splitInstances.push(Split(['#cell5', '#cell6', '#cell7'], { direction: 'vertical', sizes: [33, 33, 34], minSize: [110, 110, 110], gutterSize: 4 }));

    } else if (layoutType === '11cell') {
        container.innerHTML = `
            <div id="col1" class="split-col" style="height:100%; display:flex; flex-direction:column;">
                <div class="grid-cell" id="c1" style="height:100%;"><div class="grid-cell-content"></div></div>
            </div>
            <div id="col2" class="split-col" style="height:100%; display:flex; flex-direction:column;">
                <div class="grid-cell" id="c2"><div class="grid-cell-content"></div></div>
                <div class="grid-cell" id="c3"><div class="grid-cell-content"></div></div>
                <div class="grid-cell" id="c4"><div class="grid-cell-content"></div></div>
                <div class="grid-cell" id="c5"><div class="grid-cell-content"></div></div>
            </div>
            <div id="col3" class="split-col" style="height:100%; display:flex; flex-direction:column;">
                <div class="grid-cell" id="c6"><div class="grid-cell-content"></div></div>
                <div class="grid-cell" id="c7"><div class="grid-cell-content"></div></div>
                <div class="grid-cell" id="c8"><div class="grid-cell-content"></div></div>
            </div>
            <div id="col4" class="split-col" style="height:100%; display:flex; flex-direction:column;">
                <div class="grid-cell" id="c9"><div class="grid-cell-content"></div></div>
                <div class="grid-cell" id="c10"><div class="grid-cell-content"></div></div>
                <div class="grid-cell" id="c11"><div class="grid-cell-content"></div></div>
            </div>
        `;
        splitInstances.push(Split(['#col1', '#col2', '#col3', '#col4'], { sizes: [40, 20, 20, 20], minSize: [320, 200, 200, 200], gutterSize: 4 }));
        splitInstances.push(Split(['#c2', '#c3', '#c4', '#c5'], { direction: 'vertical', sizes: [25, 25, 25, 25], minSize: [90, 90, 90, 90], gutterSize: 4 }));
        splitInstances.push(Split(['#c6', '#c7', '#c8'], { direction: 'vertical', sizes: [33, 33, 34], minSize: [100, 100, 100], gutterSize: 4 }));
        splitInstances.push(Split(['#c9', '#c10', '#c11'], { direction: 'vertical', sizes: [33, 33, 34], minSize: [100, 100, 100], gutterSize: 4 }));

    } else if (layoutType === '8cell') {
        container.innerHTML = `
            <div id="row1" class="split-row" style="display:flex; height:100%;">
                <div class="grid-cell" id="c1"><div class="grid-cell-content"></div></div>
                <div class="grid-cell" id="c2"><div class="grid-cell-content"></div></div>
                <div class="grid-cell" id="c3"><div class="grid-cell-content"></div></div>
                <div class="grid-cell" id="c4"><div class="grid-cell-content"></div></div>
            </div>
            <div id="row2" class="split-row" style="display:flex; height:100%;">
                <div class="grid-cell" id="c5"><div class="grid-cell-content"></div></div>
                <div class="grid-cell" id="c6"><div class="grid-cell-content"></div></div>
                <div class="grid-cell" id="c7"><div class="grid-cell-content"></div></div>
                <div class="grid-cell" id="c8"><div class="grid-cell-content"></div></div>
            </div>
        `;
        splitInstances.push(Split(['#row1', '#row2'], { direction: 'vertical', sizes: [50, 50], minSize: [160, 160], gutterSize: 4 }));
        splitInstances.push(Split(['#c1', '#c2', '#c3', '#c4'], { sizes: [25, 25, 25, 25], minSize: [220, 220, 220, 220], gutterSize: 4 }));
        splitInstances.push(Split(['#c5', '#c6', '#c7', '#c8'], { sizes: [25, 25, 25, 25], minSize: [220, 220, 220, 220], gutterSize: 4 }));

    } else if (layoutType === '2chart') {
        container.innerHTML = `
            <div class="grid-cell" id="c1" style="height:100%;"><div class="grid-cell-content"></div></div>
            <div class="grid-cell" id="c2" style="height:100%;"><div class="grid-cell-content"></div></div>
        `;
        splitInstances.push(Split(['#c1', '#c2'], { sizes: [50, 50], minSize: [340, 340], gutterSize: 4 }));

    } else if (layoutType === 'tripod-of-life') {
        container.innerHTML = `
            <div id="row-top" class="split-row" style="display:flex; height:58%; width:100%;">
                <div class="grid-cell" id="c1" style="height:100%;"><div class="grid-cell-content"></div></div>
                <div class="grid-cell" id="c2" style="height:100%;"><div class="grid-cell-content"></div></div>
                <div class="grid-cell" id="c3" style="height:100%;"><div class="grid-cell-content"></div></div>
            </div>
            <div id="row-bot" class="split-row" style="display:flex; height:42%; width:100%;">
                <div class="grid-cell" id="c4" style="height:100%; width:100%; flex:1;"><div class="grid-cell-content" style="height:100%; width:100%;"></div></div>
            </div>
        `;
        splitInstances.push(Split(['#row-top', '#row-bot'], { direction: 'vertical', sizes: [58, 42], minSize: [200, 150], gutterSize: 5 }));
        splitInstances.push(Split(['#c1', '#c2', '#c3'], { sizes: [33.33, 33.33, 33.34], minSize: [220, 220, 220], gutterSize: 5 }));
    } else if (layoutType === 'core-predictive') {
        container.innerHTML = `
            <div id="col1" class="split-col" style="height:100%; display:flex; flex-direction:column; overflow:hidden;">
                <div class="grid-cell" id="cell1" style="height:58%; overflow:hidden;"><div class="grid-cell-content"></div></div>
                <div class="grid-cell" id="cell5" style="height:42%; overflow:hidden;"><div class="grid-cell-content"></div></div>
            </div>
            <div id="col2" class="split-col" style="height:100%; display:flex; flex-direction:column; overflow:hidden;">
                <div class="grid-cell" id="cell2" style="height:46%; overflow:hidden;"><div class="grid-cell-content"></div></div>
                <div id="row-sub" class="split-row" style="height:54%; display:flex; flex-direction:row; overflow:hidden;">
                    <div class="grid-cell" id="cell3" style="height:100%;"><div class="grid-cell-content"></div></div>
                    <div class="grid-cell" id="cell4" style="height:100%;"><div class="grid-cell-content"></div></div>
                </div>
            </div>
        `;
        splitInstances.push(Split(['#col1', '#col2'], { sizes: [30, 70], minSize: [260, 480], gutterSize: 5 }));
        splitInstances.push(Split(['#cell1', '#cell5'], { direction: 'vertical', sizes: [58, 42], minSize: [180, 140], gutterSize: 5 }));
        splitInstances.push(Split(['#cell2', '#row-sub'], { direction: 'vertical', sizes: [46, 54], minSize: [160, 180], gutterSize: 5 }));
        splitInstances.push(Split(['#cell3', '#cell4'], { sizes: [50, 50], minSize: [180, 180], gutterSize: 5 }));

    } else if (layoutType === 'big-four') {
        container.innerHTML = `
            <div id="row1" class="split-row" style="display:flex; height:50%; width:100%;">
                <div class="grid-cell" id="c1" style="height:100%;"><div class="grid-cell-content"></div></div>
                <div class="grid-cell" id="c2" style="height:100%;"><div class="grid-cell-content"></div></div>
            </div>
            <div id="row2" class="split-row" style="display:flex; height:50%; width:100%;">
                <div class="grid-cell" id="c3" style="height:100%;"><div class="grid-cell-content"></div></div>
                <div class="grid-cell" id="c4" style="height:100%;"><div class="grid-cell-content"></div></div>
            </div>
        `;
        splitInstances.push(Split(['#row1', '#row2'], { direction: 'vertical', sizes: [50, 50], minSize: [180, 180], gutterSize: 5 }));
        splitInstances.push(Split(['#c1', '#c2'], { sizes: [50, 50], minSize: [250, 250], gutterSize: 5 }));
        splitInstances.push(Split(['#c3', '#c4'], { sizes: [50, 50], minSize: [250, 250], gutterSize: 5 }));
    }

    const savedStateStr = localStorage.getItem('astra_layout_' + layoutType);
    let stateLoaded = false;
    if (savedStateStr) {
        try {
            const savedCells = JSON.parse(savedStateStr);
            if (savedCells && savedCells.length > 0) {
                window._tempSave = saveLayoutState;
                saveLayoutState = function() {}; 

                savedCells.forEach(sc => {
                    if (layoutType === 'core-predictive') {
                        if (sc.id === 'cell2' && (sc.widget === 'planetary-info' || sc.widget === 'empty')) sc.widget = 'master-diagnostic';
                        if (sc.id === 'cell4' && (sc.widget === 'dashas-timeline' || sc.widget === 'empty')) sc.widget = 'dignities';
                    }
                    const cell = document.getElementById(sc.id);
                    if (cell) assignWidget(sc.widget, cell, { varga: sc.varga, root_planet: sc.root_planet });
                });
                if (layoutType === 'core-predictive') {
                    const c5 = document.getElementById('cell5');
                    if (c5 && (!c5.dataset.widget || c5.dataset.widget === 'empty')) {
                        assignWidget('dashas-timeline', c5);
                    }
                }

                saveLayoutState = window._tempSave;
                stateLoaded = true;
            }
        } catch(e) {}
    }

    if (!stateLoaded) {
        if (layoutType === 'kala') {
            assignWidget('chart', document.getElementById('cell1'));
            assignWidget('aspects-planets', document.getElementById('cell2'));
            assignWidget('aspects-bhava-chalita', document.getElementById('cell3'));
            assignWidget('aspects-equal-houses', document.getElementById('cell4'));
            assignWidget('avasthas-calc', document.getElementById('cell5'));
            assignWidget('dignities', document.getElementById('cell6'));
            assignWidget('empty', document.getElementById('cell7'));
        } else if (layoutType === 'tripod-of-life') {
            assignWidget('chart', document.getElementById('c1'), { varga: 'D1', root_planet: 'Lagna' });
            assignWidget('chart', document.getElementById('c2'), { varga: 'D1', root_planet: 'Moon' });
            assignWidget('chart', document.getElementById('c3'), { varga: 'D1', root_planet: 'Sun' });
            assignWidget('planetary-info', document.getElementById('c4'));
        } else if (layoutType === 'core-predictive') {
            assignWidget('chart', document.getElementById('cell1'));
            assignWidget('dashas-timeline', document.getElementById('cell5'));
            assignWidget('master-diagnostic', document.getElementById('cell2'));
            assignWidget('chart', document.getElementById('cell3'));
            const sel3 = document.querySelector('#cell3 .varga-select');
            if (sel3) sel3.value = 'D9';
            updateWidget(document.getElementById('cell3'));
            assignWidget('dignities', document.getElementById('cell4'));
        } else if (layoutType === 'big-four') {
            assignWidget('chart', document.getElementById('c1'));
            assignWidget('chart', document.getElementById('c2'));
            const s2 = document.querySelector('#c2 .varga-select');
            if (s2) s2.value = 'D9';
            updateWidget(document.getElementById('c2'));
            assignWidget('chart', document.getElementById('c3'));
            const s3 = document.querySelector('#c3 .varga-select');
            if (s3) s3.value = 'D10';
            updateWidget(document.getElementById('c3'));
            assignWidget('chart', document.getElementById('c4'));
            const s4 = document.querySelector('#c4 .varga-select');
            if (s4) s4.value = 'D3';
            updateWidget(document.getElementById('c4'));
        } else if (layoutType === '11cell') {
            assignWidget('chart', document.getElementById('c1'));
            assignWidget('aspects-planets', document.getElementById('c2'));
            assignWidget('aspects-bhava-chalita', document.getElementById('c3'));
            assignWidget('aspects-equal-houses', document.getElementById('c4'));
            for(let i=5; i<=11; i++) assignWidget('empty', document.getElementById('c'+i));
        } else if (layoutType === '8cell') {
            assignWidget('chart', document.getElementById('c1'));
            assignWidget('chart', document.getElementById('c2'));
            assignWidget('aspects-planets', document.getElementById('c3'));
            assignWidget('aspects-bhava-chalita', document.getElementById('c4'));
            assignWidget('aspects-equal-houses', document.getElementById('c5'));
            assignWidget('empty', document.getElementById('c6'));
            assignWidget('empty', document.getElementById('c7'));
            assignWidget('empty', document.getElementById('c8'));
        } else if (layoutType === '2chart') {
            assignWidget('chart', document.getElementById('c1'));
            assignWidget('chart', document.getElementById('c2'));
        }
    }
    observeGridCells();
    attachGutterAutoFit();
    if (typeof updateMenuCheckmarks === 'function') updateMenuCheckmarks();
}

function changeWorkspace(wsName) {
    localStorage.setItem('astra_current_workspace', wsName);
    const wsSelect = document.getElementById('workspaceSelect');
    if (wsSelect) wsSelect.value = wsName;

    const layoutSelect = document.getElementById('layoutSelect');

    if (wsName === 'core-predictive') {
        if (layoutSelect) layoutSelect.value = 'core-predictive';
        changeLayout('core-predictive');
        assignWidget('chart', document.getElementById('cell1'));
        assignWidget('dashas-timeline', document.getElementById('cell5'));
        assignWidget('master-diagnostic', document.getElementById('cell2'));
        assignWidget('chart', document.getElementById('cell3'));
        const sel = document.querySelector('#cell3 .varga-select');
        if (sel) sel.value = 'D9';
        updateWidget(document.getElementById('cell3'));
        assignWidget('dignities', document.getElementById('cell4'));
        saveLayoutState();
    } else if (wsName === 'tripod-of-life') {
        if (layoutSelect) layoutSelect.value = 'tripod-of-life';
        changeLayout('tripod-of-life');
        assignWidget('chart', document.getElementById('c1'), { varga: 'D1', root_planet: 'Lagna' });
        assignWidget('chart', document.getElementById('c2'), { varga: 'D1', root_planet: 'Moon' });
        assignWidget('chart', document.getElementById('c3'), { varga: 'D1', root_planet: 'Sun' });
        assignWidget('planetary-info', document.getElementById('c4'));
    } else if (wsName === 'big-four') {
        if (layoutSelect) layoutSelect.value = 'big-four';
        changeLayout('big-four');
        assignWidget('chart', document.getElementById('c1'));
        assignWidget('chart', document.getElementById('c2'));
        const s2 = document.querySelector('#c2 .varga-select');
        if (s2) s2.value = 'D9';
        updateWidget(document.getElementById('c2'));
        assignWidget('chart', document.getElementById('c3'));
        const s3 = document.querySelector('#c3 .varga-select');
        if (s3) s3.value = 'D10';
        updateWidget(document.getElementById('c3'));
        assignWidget('chart', document.getElementById('c4'));
        const s4 = document.querySelector('#c4 .varga-select');
        if (s4) s4.value = 'D3';
        updateWidget(document.getElementById('c4'));
    } else if (wsName === 'strengths' || wsName === 'kala') {
        if (layoutSelect) layoutSelect.value = 'kala';
        changeLayout('kala');
        assignWidget('chart', document.getElementById('cell1'));
        assignWidget('shadbala-table', document.getElementById('cell2'));
        assignWidget('quant-matrices', document.getElementById('cell3'));
        assignWidget('vimshopaka', document.getElementById('cell4'));
        assignWidget('avasthas-calc', document.getElementById('cell5'));
        assignWidget('dignities', document.getElementById('cell6'));
        assignWidget('aspects-planets', document.getElementById('cell7'));
    } else if (wsName === 'timing') {
        if (layoutSelect) layoutSelect.value = 'kala';
        changeLayout('kala');
        assignWidget('chart', document.getElementById('cell1'));
        assignWidget('dashas-timeline', document.getElementById('cell2'));
        assignWidget('ashtakavarga', document.getElementById('cell3'));
        assignWidget('planetary-info', document.getElementById('cell4'));
        assignWidget('vimshopaka', document.getElementById('cell5'));
        assignWidget('dignities', document.getElementById('cell6'));
        assignWidget('empty', document.getElementById('cell7'));
    } else if (wsName === 'custom') {
        const savedLayout = localStorage.getItem('astra_current_layout') || 'kala';
        if (layoutSelect) layoutSelect.value = savedLayout;
        changeLayout(savedLayout);
    }
    saveLayoutState();
    if (typeof updateMenuCheckmarks === 'function') updateMenuCheckmarks();
}

function setupSplit() {
    const mainCont = document.getElementById('main-container');
    if (mainCont) mainCont.style.display = 'flex';
    if (splitInstances.length === 0) {
        const savedWs = localStorage.getItem('astra_current_workspace') || 'core-predictive';
        const wsSelect = document.getElementById('workspaceSelect');
        if (wsSelect) wsSelect.value = savedWs;
        changeWorkspace(savedWs);
    }
    observeGridCells();
}

function setupSplit_old() {
    const mainCont = document.getElementById('main-container');
    if (mainCont) mainCont.style.display = 'flex';
    if (!splitInstance && typeof Split !== 'undefined') {
        splitInstance = Split(['#chart-pane', '#info-pane'], {
            sizes: [60, 40],
            minSize: [400, 300],
            gutterSize: 8,
            cursor: 'col-resize'
        });
    }
    if (!infoSplitInstance && typeof Split !== 'undefined') {
        infoSplitInstance = Split(['#info-top', '#info-bottom'], {
            direction: 'vertical',
            sizes: [60, 40],
            minSize: [150, 200],
            gutterSize: 8,
            cursor: 'row-resize'
        });
    }

    const tabBtns = document.querySelectorAll('.tab-btn');
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            btn.classList.add('active');
            const targetEl = document.getElementById(btn.dataset.target);
            if (targetEl) targetEl.classList.add('active');
        });
    });
}

// ==========================================
// Widget Assignment & Lifecycle Updates
// ==========================================
function assignWidget(widgetType, targetCell = null, options = {}) {
    const cell = targetCell || currentActiveCell;
    if (!cell) return;

    cell.dataset.widget = widgetType;
    if (options && options.root_planet) {
        cell.dataset.rootPlanet = options.root_planet;
    } else if (widgetType === 'chart') {
        cell.dataset.rootPlanet = 'Lagna';
    } else if (!cell.dataset.rootPlanet) {
        cell.dataset.rootPlanet = 'Lagna';
    }

    const contentDiv = cell.querySelector('.grid-cell-content');
    if (contentDiv) {
        contentDiv.innerHTML = '';

        if (widgetType !== 'empty') {
            const tmpl = document.getElementById('tmpl-' + widgetType);
            if (tmpl) {
                contentDiv.appendChild(tmpl.content.cloneNode(true));
                if (['info', 'planetary-evaluation', 'classical-yogas', 'notes'].includes(widgetType)) {
                    contentDiv.classList.add('scrollable');
                } else {
                    contentDiv.classList.remove('scrollable');
                }
            }
        }
    }

    if (options && options.varga) {
        const sel = cell.querySelector('.varga-select');
        if (sel) sel.value = options.varga;
    }
    if (options && options.biwheel_outer) {
        const outerSel = cell.querySelector('.biwheel-outer-select');
        if (outerSel) outerSel.value = options.biwheel_outer;
    }
    if (options && options.chart_style) {
        const btn = cell.querySelector('.btn-' + options.chart_style);
        if (btn) switchWidgetChartType(btn, options.chart_style);
    }

    updateWidget(cell);
    saveLayoutState();
}

function switchWidgetRootPlanet(btn, rootPlanet) {
    const cell = btn.closest('.grid-cell');
    if (!cell) return;
    cell.dataset.rootPlanet = rootPlanet;

    const toolbar = btn.closest('.chart-toolbar');
    if (toolbar) {
        toolbar.querySelectorAll('.root-pill-btn').forEach(b => {
            b.classList.remove('active');
            b.style.background = 'transparent';
            b.style.color = '#6b5a4b';
        });
        btn.classList.add('active');
        btn.style.background = '#fffdfa';
        btn.style.color = '#4a3325';
    }

    updateWidget(cell);
    saveLayoutState();
}

function switchWidgetChartType(btn, type) {
    const widget = btn.closest('.widget-chart');
    if (!widget) return;
    widget.querySelectorAll('.chart-view').forEach(v => {
        v.style.display = 'none';
        v.classList.remove('active');
    });
    widget.querySelectorAll('.hotkey-btn').forEach(b => b.classList.remove('active'));

    const targetView = widget.querySelector('.view-' + type);
    if (targetView) {
        targetView.style.display = 'flex';
        targetView.classList.add('active');
    }

    btn.classList.add('active');

    const biwheelControls = widget.querySelector('.biwheel-outer-controls');
    const biwheelInnerLabel = widget.querySelector('.biwheel-inner-label');
    if (biwheelControls) {
        biwheelControls.style.display = (type === 'biwheel') ? 'inline-flex' : 'none';
    }
    if (biwheelInnerLabel) {
        biwheelInnerLabel.style.display = (type === 'biwheel') ? 'inline' : 'none';
    }

    const cell = widget.closest('.grid-cell');
    if (cell) {
        updateWidget(cell);
        if (typeof applyWidgetChartZoom === 'function') applyWidgetChartZoom(cell);
        saveLayoutState();
    }
}

function updateWidget(cell) {
    const chartData = window.currentChartData || currentChartData;
    const svgs = window.currentSvgs || currentSvgs;
    if (!chartData || !svgs) return;
    const widgetType = cell.dataset.widget;
    if (!widgetType) return;

    if (widgetType !== 'chart' && window.widgetRegistry && window.widgetRegistry.updateWidget(cell, chartData)) {
        return;
    }

    if (widgetType === 'chart') {
        const vargaSelect = cell.querySelector('.varga-select');
        const varga = vargaSelect ? vargaSelect.value : 'D1';
        const rootPlanet = cell.dataset.rootPlanet || 'Lagna';

        // Sync toolbar root buttons
        const toolbar = cell.querySelector('.chart-toolbar');
        if (toolbar) {
            toolbar.querySelectorAll('.root-pill-btn').forEach(b => {
                const isMatch = (rootPlanet === 'Lagna' && b.classList.contains('btn-root-lagna')) ||
                                (rootPlanet === 'Moon' && b.classList.contains('btn-root-moon')) ||
                                (rootPlanet === 'Sun' && b.classList.contains('btn-root-sun'));
                if (isMatch) {
                    b.classList.add('active');
                    b.style.background = '#fffdfa';
                    b.style.color = '#4a3325';
                } else {
                    b.classList.remove('active');
                    b.style.background = 'transparent';
                    b.style.color = '#6b5a4b';
                }
            });
        }

        // Sync D10 calculation mode toggle button
        const d10Btn = cell.querySelector('.btn-d10-toggle');
        if (d10Btn) {
            if (varga === 'D10') {
                d10Btn.style.display = 'inline-flex';
                d10Btn.innerHTML = (currentD10Mode === 'direct') ? 'D10: Direct ➔' : 'D10: Kala ↺';
                d10Btn.title = (currentD10Mode === 'direct')
                    ? 'D10: Contemporary Forward (Vic DiCara). Click to switch to Kala Reverse.'
                    : 'D10: Kala Reverse for Even Signs (Ernst Wilhelm). Click to switch to Contemporary Forward.';
                d10Btn.style.background = (currentD10Mode === 'direct') ? '#e0f2fe' : '#fef3c7';
                d10Btn.style.color = (currentD10Mode === 'direct') ? '#0369a1' : '#92400e';
                d10Btn.style.borderColor = (currentD10Mode === 'direct') ? '#7dd3fc' : '#fcd34d';
            } else {
                d10Btn.style.display = 'none';
            }
        }

        const vData = svgs[varga];
        const vSvgMode = (vData && vData[currentNotation]) ? vData[currentNotation] : vData;

        let vSvg = null;
        if (vSvgMode) {
            if (vSvgMode.roots && vSvgMode.roots[rootPlanet]) {
                vSvg = vSvgMode.roots[rootPlanet];
            } else {
                vSvg = vSvgMode;
            }
        }

        if (vSvg) {
            const s = cell.querySelector('.svg-south');
            const n = cell.querySelector('.svg-north');
            const c = cell.querySelector('.svg-circular');
            const b = cell.querySelector('.svg-biwheel');
            if (s) s.innerHTML = vSvg.south;
            if (n) n.innerHTML = vSvg.north;
            if (c) c.innerHTML = vSvg.circular;
            if (b) {
                const outerSelect = cell.querySelector('.biwheel-outer-select');
                const outerVarga = outerSelect ? outerSelect.value : 'D9';
                const innerVarga = varga || 'D1';

                const innerLabel = cell.querySelector('.biwheel-inner-label');
                const biwheelControls = cell.querySelector('.biwheel-outer-controls');
                const isBiwheelActive = cell.querySelector('.view-biwheel.active') !== null;
                if (innerLabel) innerLabel.style.display = isBiwheelActive ? 'inline' : 'none';
                if (biwheelControls) biwheelControls.style.display = isBiwheelActive ? 'inline-flex' : 'none';

                if (innerVarga === 'D1') {
                    let biwheelMarkup = null;
                    if (svgs[outerVarga]) {
                        const outData = svgs[outerVarga];
                        const outSvgMode = (outData && outData[currentNotation]) ? outData[currentNotation] : outData;
                        const outSvgRoot = (outSvgMode && outSvgMode.roots && outSvgMode.roots[rootPlanet]) ? outSvgMode.roots[rootPlanet] : outSvgMode;
                        if (outSvgRoot && outSvgRoot.biwheel) {
                            biwheelMarkup = outSvgRoot.biwheel;
                        }
                    }
                    if (!biwheelMarkup) {
                        biwheelMarkup = vSvg.biwheel || vSvg.circular;
                    }
                    b.innerHTML = biwheelMarkup;
                } else {
                    const natId = (typeof window.currentLoadedNative !== 'undefined' && window.currentLoadedNative?.id) || document.getElementById('nativeSelect')?.value || '';
                    const offsetSec = activePreviewOffsetSeconds || 0;
                    const cacheKey = `${natId}_${innerVarga}_${outerVarga}_${currentNotation}_${rootPlanet}_${currentD10Mode}_${currentNakshatraSystem}_${offsetSec}`;
                    if (window.biwheelDynamicCache && window.biwheelDynamicCache[cacheKey]) {
                        b.innerHTML = window.biwheelDynamicCache[cacheKey];
                    } else if (natId) {
                        if (!window.biwheelDynamicCache) window.biwheelDynamicCache = {};
                        const url = `/api/chart/${natId}/biwheel?inner=${innerVarga}&outer=${outerVarga}&mode=${currentNotation}&root=${rootPlanet}&d10_mode=${currentD10Mode}&nakshatra_system=${currentNakshatraSystem}&offset_seconds=${offsetSec}`;
                        fetch(url)
                            .then(res => res.json())
                            .then(data => {
                                if (data && data.svg) {
                                    window.biwheelDynamicCache[cacheKey] = data.svg;
                                    const currInner = cell.querySelector('.varga-select')?.value;
                                    const currOuter = cell.querySelector('.biwheel-outer-select')?.value;
                                    if (currInner === innerVarga && currOuter === outerVarga) {
                                        b.innerHTML = data.svg;
                                        if (typeof applyWidgetChartZoom === 'function') applyWidgetChartZoom(cell);
                                    }
                                }
                            })
                            .catch(err => console.error("Error fetching custom biwheel:", err));
                    }
                }
            }
        }
        if (typeof applyWidgetChartZoom === 'function') applyWidgetChartZoom(cell);
        applyHouseHighlights(cell);
        syncAllSteppersUI();
    }
}

function updateAllWidgets() {
    const chartData = window.currentChartData || currentChartData;
    if (!chartData) return;

    // Pluggable Registry Update
    document.querySelectorAll('.grid-cell').forEach(cell => {
        const type = cell.dataset.widget;
        if (!type || type === 'empty') return;
        if (type === 'chart') {
            updateWidget(cell);
        } else if (window.widgetRegistry && window.widgetRegistry.has(type)) {
            window.widgetRegistry.updateWidget(cell, chartData);
        } else {
            // Direct function calls fallback
            if (type === 'master-diagnostic' && typeof updateMasterDiagnosticWidget === 'function') updateMasterDiagnosticWidget(cell);
            else if (type === 'planetary-info' && typeof updatePlanetaryInfoWidgetForCell === 'function') updatePlanetaryInfoWidgetForCell(cell);
            else if (type === 'nakshatras' && typeof updateNakshatraWidgetForCell === 'function') updateNakshatraWidgetForCell(cell);
            else if (type === 'dashas-timeline' && typeof updateDashaTimelineWidget === 'function') updateDashaTimelineWidget(cell);
            else if (type === 'ashtakavarga' && typeof updateAshtakavargaWidget === 'function') updateAshtakavargaWidget(cell);
            else if (type === 'vimshopaka' && typeof updateVimshopakaWidget === 'function') updateVimshopakaWidget(cell);
            else if (type === 'yoga-judgment' && typeof updateYogaJudgmentWidget === 'function') updateYogaJudgmentWidget(cell);
            else if (type === 'planetary-evaluation' && typeof updatePlanetaryEvaluationWidget === 'function') updatePlanetaryEvaluationWidget(cell);
            else if (type === 'classical-yogas' && typeof updateClassicalYogasWidget === 'function') updateClassicalYogasWidget(cell);
            else if (type === 'dignities' && typeof updateVargaDignitiesTable === 'function') updateVargaDignitiesTable(cell, chartData);
            else if (type === 'avasthas-calc' && typeof updateAvasthasCalcTableForCell === 'function') updateAvasthasCalcTableForCell(cell);
            else if (type === 'quant-matrices' && typeof updateQuantMatricesTableForCell === 'function') updateQuantMatricesTableForCell(cell);
            else if (type.startsWith('aspects-') && typeof updateAspectsWidgetForCell === 'function') updateAspectsWidgetForCell(cell);
            else if (type === 'info' && typeof refreshContextInfoForCell === 'function') refreshContextInfoForCell(cell);
            else if (type === 'shadbala-table' && typeof updateShadbalaTableWidget === 'function') updateShadbalaTableWidget();
            else if (type === 'notes' && typeof updateNotesWidget === 'function') updateNotesWidget(cell);
            else if (type === 'rashi-drishti' && typeof updateRashiDrishtiWidget === 'function') updateRashiDrishtiWidget(cell);
            else if (type === 'sign-attributes' && typeof updateSignAttributesWidget === 'function') updateSignAttributesWidget(cell);
        }
    });

    // Update floating modal if active
    const modal = document.getElementById('widgetMaximizeModal');
    if (modal && modal.style.display === 'flex') {
        const navBtnDiag = document.getElementById('nav-btn-master-diag');
        if (navBtnDiag?.classList.contains('active')) {
            const cont = document.getElementById('widgetMaximizeContainer');
            if (cont && typeof populateMasterDiagnosticTable === 'function') populateMasterDiagnosticTable(cont);
        }
        const navBtn = document.getElementById('nav-btn-evaluation');
        if (navBtn?.classList.contains('active')) {
            const cont = document.getElementById('widgetMaximizeContainer');
            if (cont && typeof updatePlanetaryEvaluationWidget === 'function') updatePlanetaryEvaluationWidget(cont);
        }
        const navBtnYogas = document.getElementById('nav-btn-classical-yogas');
        if (navBtnYogas?.classList.contains('active')) {
            const cont = document.getElementById('widgetMaximizeContainer');
            if (cont && typeof updateClassicalYogasWidget === 'function') updateClassicalYogasWidget(cont);
        }
    }
}

function updateShadbalaTableWidget() {
    if (typeof updateShadbalaTable === 'function') updateShadbalaTable();
}

function updateDashaTimelineWidget(cell) {
    if (window.widgetRegistry && window.widgetRegistry.has('dashas-timeline')) {
        window.widgetRegistry.updateWidget(cell, window.currentChartData || currentChartData);
    }
}

function assignKalaChart(varga, perspective = null) {
    if (typeof closeKalaMenu === 'function') closeKalaMenu();
    if (!currentActiveCell) return;
    const rootPlanet = perspective || 'Lagna';
    assignWidget('chart', currentActiveCell, { varga: varga, root_planet: rootPlanet });
}

function assignKalaWidget(widgetType) {
    if (typeof closeKalaMenu === 'function') closeKalaMenu();
    if (!currentActiveCell) return;
    assignWidget(widgetType, currentActiveCell);
}

function assignKalaPerspective(type) {
    if (typeof closeKalaMenu === 'function') closeKalaMenu();
    if (!currentActiveCell) return;
    const rootPlanet = (type === 'chandra' || type === 'moon') ? 'Moon' : ((type === 'surya' || type === 'sun') ? 'Sun' : 'Lagna');
    const vSel = currentActiveCell.querySelector('.varga-select');
    const currentVarga = vSel ? vSel.value : 'D1';
    assignWidget('chart', currentActiveCell, { varga: currentVarga, root_planet: rootPlanet });
}

function setGlobalChartStyle(style) {
    document.querySelectorAll('.widget-chart').forEach(widget => {
        const btn = widget.querySelector('.btn-' + style);
        if (btn) switchWidgetChartType(btn, style);
    });
    document.querySelectorAll(`input[name="kalaGlobalStyle"][value="${style}"]`).forEach(r => r.checked = true);
    if (typeof switchShodasaStyle === 'function') switchShodasaStyle(style);
}

// ==========================================
// House Classification Highlights (Pastels)
// ==========================================
const HOUSE_CATEGORIES = {
    kendra: [1, 4, 7, 10],
    trikona: [1, 5, 9],
    dusthana: [6, 8, 12],
    upachaya: [3, 6, 10, 11]
};

function toggleHouseHighlight(btn, category) {
    const cell = btn.closest('.grid-cell');
    if (!cell) return;
    btn.classList.toggle('active');

    const bar = btn.closest('.chart-house-highlights-bar');
    const activeCats = [];
    if (bar) {
        bar.querySelectorAll('.house-highlight-btn[data-category]').forEach(b => {
            if (b.classList.contains('active')) {
                activeCats.push(b.dataset.category);
            }
        });
    }
    cell.dataset.houseHighlights = JSON.stringify(activeCats);
    applyHouseHighlights(cell);
}

function clearHouseHighlights(btn) {
    const cell = btn.closest('.grid-cell');
    if (!cell) return;
    const bar = btn.closest('.chart-house-highlights-bar');
    if (bar) {
        bar.querySelectorAll('.house-highlight-btn[data-category]').forEach(b => {
            b.classList.remove('active');
        });
    }
    cell.dataset.houseHighlights = '[]';
    applyHouseHighlights(cell);
}

function applyHouseHighlights(cell) {
    if (!cell) return;
    let activeCats = [];
    try {
        activeCats = JSON.parse(cell.dataset.houseHighlights || '[]');
    } catch(e) {
        activeCats = [];
    }

    const bar = cell.querySelector('.chart-house-highlights-bar');
    if (bar) {
        bar.querySelectorAll('.house-highlight-btn[data-category]').forEach(b => {
            const cat = b.dataset.category;
            const isActive = activeCats.includes(cat);
            b.classList.toggle('active', isActive);
        });
        const clearBtn = bar.querySelector('.btn-highlight-clear');
        if (clearBtn) {
            clearBtn.style.display = activeCats.length > 0 ? 'inline-block' : 'none';
        }
    }

    const bgCells = cell.querySelectorAll('.sign-cell-bg[data-house]');
    bgCells.forEach(bg => {
        bg.classList.remove('house-kendra', 'house-trikona', 'house-dusthana', 'house-upachaya');
        const hNum = parseInt(bg.getAttribute('data-house'), 10);
        if (!hNum) return;

        activeCats.forEach(cat => {
            if (HOUSE_CATEGORIES[cat] && HOUSE_CATEGORIES[cat].includes(hNum)) {
                bg.classList.add(`house-${cat}`);
            }
        });
    });
}

// ==========================================
// Birth Time Rectification Stepper
// ==========================================
function formatOffsetLabel(offsetSec) {
    if (offsetSec === 0) return "Original";
    const sign = offsetSec > 0 ? "+" : "-";
    const absSec = Math.abs(offsetSec);
    const h = Math.floor(absSec / 3600);
    const m = Math.floor((absSec % 3600) / 60);
    const s = absSec % 60;
    if (h > 0) {
        return `${sign}${h}h ${m}m ${s > 0 ? s + 's' : ''}`.trim();
    } else if (m > 0) {
        return `${sign}${m}m ${s > 0 ? s + 's' : ''}`.trim();
    } else {
        return `${sign}${s}s`;
    }
}

function syncAllSteppersUI() {
    const steppers = document.querySelectorAll('.chart-time-stepper');
    const offsetSec = (typeof window.activePreviewOffsetSeconds !== 'undefined') ? window.activePreviewOffsetSeconds : activePreviewOffsetSeconds;
    const isPreview = (offsetSec !== 0);
    const currentNative = window.currentLoadedNative || currentLoadedNative;
    const timeStr = isPreview
        ? (window.currentPreviewTime || currentPreviewTime || (currentNative ? currentNative.time : '12:00:00'))
        : (currentNative ? currentNative.time : '12:00:00');
    const offsetLabel = formatOffsetLabel(offsetSec);

    steppers.forEach(stepper => {
        if (isPreview) {
            stepper.classList.add('is-preview-active');
        } else {
            stepper.classList.remove('is-preview-active');
        }

        const clockEl = stepper.querySelector('.stepper-clock');
        if (clockEl) clockEl.textContent = timeStr;

        const badgeEl = stepper.querySelector('.stepper-offset-badge');
        if (badgeEl) badgeEl.textContent = offsetLabel;

        const resetBtn = stepper.querySelector('.stepper-btn-reset');
        if (resetBtn) resetBtn.style.display = isPreview ? 'inline-block' : 'none';

        const saveBtn = stepper.querySelector('.stepper-btn-save');
        if (saveBtn) saveBtn.style.display = isPreview ? 'inline-block' : 'none';
    });

    const chartData = window.currentChartData || currentChartData;
    if (chartData && chartData.subject_info) {
        const subEl = document.getElementById('chartSubtitle');
        if (subEl) {
            const latVal = parseFloat(chartData.subject_info.latitude);
            const lonVal = parseFloat(chartData.subject_info.longitude);
            const latDir = latVal >= 0 ? 'N' : 'S';
            const lonDir = lonVal >= 0 ? 'E' : 'W';
            const latStr = `${Math.abs(latVal).toFixed(4)}° ${latDir}`;
            const lonStr = `${Math.abs(lonVal).toFixed(4)}° ${lonDir}`;
            const pName = (currentNative && currentNative.place && currentNative.place !== 'Custom')
                ? currentNative.place
                : (chartData.subject_info.place && chartData.subject_info.place !== 'Custom' ? chartData.subject_info.place : '');
            const pStr = pName ? `${pName} • ` : '';
            const prevTag = isPreview ? ` (PREVIEW: ${offsetLabel})` : '';
            subEl.innerText = `${chartData.subject_info.birth_datetime}${prevTag} | ${pStr}${latStr}, ${lonStr}`;
        }
    }
}

async function stepBirthTime(deltaSeconds) {
    const currentNative = window.currentLoadedNative || currentLoadedNative;
    const nativeId = (currentNative && currentNative.id) || document.getElementById('nativeSelect')?.value;
    if (!nativeId) return;

    activePreviewOffsetSeconds += deltaSeconds;
    window.activePreviewOffsetSeconds = activePreviewOffsetSeconds;
    await applyBirthTimeOffset(nativeId, activePreviewOffsetSeconds);
}

async function applyBirthTimeOffset(nativeId, offsetSeconds) {
    if (stepperAbortController) {
        try { stepperAbortController.abort(); } catch(e) {}
    }
    stepperAbortController = new AbortController();

    const loadingEl = document.getElementById('loading');
    if (loadingEl) loadingEl.style.display = 'block';

    try {
        const response = await fetch(
            `/api/chart/${nativeId}?d10_mode=${currentD10Mode}&d24_mode=${currentD24Mode}&nakshatra_system=${currentNakshatraSystem}&offset_seconds=${offsetSeconds}`,
            { signal: stepperAbortController.signal }
        );
        const result = await response.json();
        if (result.error) {
            console.error("Stepper calculation error:", result.error);
            return;
        }

        currentChartData = result.data;
        window.currentChartData = result.data;
        currentSvgs = result.svgs;
        window.currentSvgs = result.svgs;
        currentPreviewTime = result.preview_time;
        window.currentPreviewTime = result.preview_time;
        currentPreviewDate = result.preview_date;
        window.currentPreviewDate = result.preview_date;

        updateAllWidgets();
        syncAllSteppersUI();
    } catch (e) {
        if (e.name === 'AbortError') return;
        console.error("Failed to step birth time:", e);
    } finally {
        if (loadingEl) loadingEl.style.display = 'none';
    }
}

async function resetBirthTimePreview() {
    activePreviewOffsetSeconds = 0;
    window.activePreviewOffsetSeconds = 0;
    currentPreviewTime = null;
    window.currentPreviewTime = null;
    currentPreviewDate = null;
    window.currentPreviewDate = null;
    const currentNative = window.currentLoadedNative || currentLoadedNative;
    const nativeId = (currentNative && currentNative.id) || document.getElementById('nativeSelect')?.value;
    if (nativeId) {
        if (typeof window.loadChart === 'function') {
            await window.loadChart(nativeId);
        }
    }
}

async function savePreviewedBirthTime() {
    const currentNative = window.currentLoadedNative || currentLoadedNative;
    if (!currentNative || !currentPreviewTime) return;
    const personName = currentNative.name || 'this person';
    const offsetLabel = formatOffsetLabel(activePreviewOffsetSeconds);
    const confirmed = window.confirm(
        `Permanently save rectified birth time for ${personName}?\n\nNew Time: ${currentPreviewTime}\nNew Date: ${currentPreviewDate}\nAdjustment: ${offsetLabel}`
    );
    if (!confirmed) return;

    const loadingEl = document.getElementById('loading');
    if (loadingEl) loadingEl.style.display = 'block';
    try {
        const updatePayload = {
            name: currentNative.name,
            date: currentPreviewDate,
            time: currentPreviewTime,
            lat: currentNative.lat,
            lon: currentNative.lon,
            tz: currentNative.tz,
            place: currentNative.place || '',
            country: currentNative.country || '',
            notes: currentNative.notes || '',
            name_sound_value: currentNative.name_sound_value || 0
        };

        const res = await fetch(`/api/update_native/${currentNative.id}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(updatePayload)
        });
        const updated = await res.json();
        if (updated.error) {
            alert("Failed to save: " + updated.error);
            return;
        }

        currentLoadedNative = updated;
        window.currentLoadedNative = updated;
        activePreviewOffsetSeconds = 0;
        window.activePreviewOffsetSeconds = 0;
        if (typeof window.loadChart === 'function') {
            await window.loadChart(updated.id);
        }
    } catch (err) {
        console.error(err);
        alert("Error saving rectified birth time.");
    } finally {
        if (loadingEl) loadingEl.style.display = 'none';
    }
}

// ==========================================
// Calculation Modes & Notations
// ==========================================
async function setNakshatraSystem(mode) {
    if (currentNakshatraSystem === mode) return;
    currentNakshatraSystem = mode;
    window.currentNakshatraSystem = mode;
    localStorage.setItem('astra_nakshatra_system', currentNakshatraSystem);
    syncNakshatraSystemUI();
    if (typeof window.loadChart === 'function') await window.loadChart();
}

async function toggleNakshatraSystem() {
    const nextMode = (currentNakshatraSystem === 'ERNST_DHRUVA') ? 'VIC_CHITRA' : 'ERNST_DHRUVA';
    await setNakshatraSystem(nextMode);
}

function syncNakshatraSystemUI() {
    const radioDhruva = document.getElementById('radio-nak-dhruva');
    const radioChitra = document.getElementById('radio-nak-chitra');
    if (radioDhruva && radioChitra) {
        if (currentNakshatraSystem === 'VIC_CHITRA') radioChitra.checked = true;
        else radioDhruva.checked = true;
    }
    document.querySelectorAll('.btn-nak-toggle').forEach(btn => {
        const isVic = (currentNakshatraSystem === 'VIC_CHITRA');
        btn.innerHTML = isVic ? '✨ Chitra (Vic)' : '✨ Dhruva (Ernst)';
        btn.style.background = isVic ? '#fdf4ff' : '#ede9fe';
        btn.style.color = isVic ? '#86198f' : '#5b21b6';
        btn.style.borderColor = isVic ? '#f0abfc' : '#c4b5fd';
        btn.title = isVic
            ? 'Chitra Paksha Sidereal Ecliptic (Vic DiCara). Click to switch to Ernst Wilhelm Dhruva Equatorial.'
            : 'Dhruva Galactic Center Equatorial (Ernst Wilhelm). Click to switch to Vic DiCara Chitra Sidereal.';
    });
    updateMenuCheckmarks();
}

async function setD10Mode(mode) {
    if (currentD10Mode === mode) return;
    currentD10Mode = mode;
    window.currentD10Mode = mode;
    localStorage.setItem('astra_d10_mode', currentD10Mode);
    syncD10ModeUI();
    if (typeof window.loadChart === 'function') await window.loadChart();
}

async function toggleD10Mode() {
    const nextMode = (currentD10Mode === 'reverse') ? 'direct' : 'reverse';
    await setD10Mode(nextMode);
}

function syncD10ModeUI() {
    const radioRev = document.getElementById('radio-d10-reverse');
    const radioDir = document.getElementById('radio-d10-direct');
    if (radioRev && radioDir) {
        if (currentD10Mode === 'direct') radioDir.checked = true;
        else radioRev.checked = true;
    }
    document.querySelectorAll('.btn-d10-toggle').forEach(btn => {
        const cell = btn.closest('.grid-cell');
        const vargaSelect = cell ? cell.querySelector('.varga-select') : null;
        if (vargaSelect && vargaSelect.value === 'D10') {
            btn.style.display = 'inline-flex';
            btn.innerHTML = (currentD10Mode === 'direct') ? 'D10: Direct ➔' : 'D10: Kala ↺';
            btn.title = (currentD10Mode === 'direct')
                ? 'D10: Contemporary Forward (Vic DiCara). Click to switch to Kala Reverse.'
                : 'D10: Kala Reverse for Even Signs (Ernst Wilhelm). Click to switch to Contemporary Forward.';
            btn.style.background = (currentD10Mode === 'direct') ? '#e0f2fe' : '#fef3c7';
            btn.style.color = (currentD10Mode === 'direct') ? '#0369a1' : '#92400e';
            btn.style.borderColor = (currentD10Mode === 'direct') ? '#7dd3fc' : '#fcd34d';
        } else {
            btn.style.display = 'none';
        }
    });
    updateMenuCheckmarks();
}

function switchNotation(mode) {
    currentNotation = mode;
    window.currentNotation = mode;
    try { localStorage.setItem('astra_notation', mode); } catch(e){}
    updateSlot(1);
    updateSlot(2);
    document.querySelectorAll('.grid-cell[data-widget="chart"]').forEach(updateWidget);
    if (window.currentMaximized && typeof maximizeChart === 'function') {
        maximizeChart(window.currentMaximized.slot, window.currentMaximized.type);
    }
    updateMenuCheckmarks();
}

function onModalNotationChange(mode) {
    switchNotation(mode);
}

function onModalLayoutChange() {
    const showSouth = document.getElementById('modalToggleSouth')?.checked;
    const showNorth = document.getElementById('modalToggleNorth')?.checked;
    const showRightSlot = document.getElementById('modalToggleRightSlot')?.checked;

    const sb1 = document.getElementById('southBox1');
    const nb1 = document.getElementById('northBox1');
    if(sb1) sb1.style.display = showSouth ? 'flex' : 'none';
    if(nb1) nb1.style.display = showNorth ? 'flex' : 'none';

    const rs = document.getElementById('rightSlot');
    if(rs) {
        rs.style.display = showRightSlot ? 'flex' : 'none';
        const sb2 = document.getElementById('southBox2');
        const nb2 = document.getElementById('northBox2');
        if(sb2) sb2.style.display = showSouth ? 'flex' : 'none';
        if(nb2) nb2.style.display = showNorth ? 'flex' : 'none';
    }
}

function onModalSignToggle(show) {
    toggleSiSigns(show);
}

function toggleSiSigns(show) {
    showSiSigns = show;
    window.showSiSigns = show;
    const els = document.querySelectorAll('#si-signs');
    els.forEach(el => {
        el.style.display = show ? 'block' : 'none';
    });
    updateMenuCheckmarks();
}

function toggleSiSignsFromMenu() {
    toggleSiSigns(!showSiSigns);
}

function updateMenuCheckmarks() {
    const curWs = localStorage.getItem('astra_current_workspace') || 'core-predictive';
    document.querySelectorAll('#workspacesMenuDropdown .menu-row[data-ws]').forEach(row => {
        const isAct = row.getAttribute('data-ws') === curWs;
        row.classList.toggle('active', isAct);
        const check = row.querySelector('.menu-check');
        if (check) check.textContent = isAct ? '✓' : '';
    });

    const curGrid = document.getElementById('layoutSelect')?.value || 'core-predictive';
    document.querySelectorAll('#layoutMenuDropdown .menu-row[data-grid]').forEach(row => {
        const isAct = row.getAttribute('data-grid') === curGrid;
        row.classList.toggle('active', isAct);
        const check = row.querySelector('.menu-check');
        if (check) check.textContent = isAct ? '✓' : '';
    });

    const notMode = currentNotation || (localStorage.getItem('astra_notation') || 'symbol');
    document.querySelectorAll('#settingsMenuDropdown .menu-row[data-notation]').forEach(row => {
        const isAct = row.getAttribute('data-notation') === notMode;
        row.classList.toggle('active', isAct);
        const check = row.querySelector('.menu-check');
        if (check) check.textContent = isAct ? '✓' : '';
    });

    const d10Mode = currentD10Mode || (localStorage.getItem('astra_d10_mode') || 'reverse');
    document.querySelectorAll('#settingsMenuDropdown .menu-row[data-d10]').forEach(row => {
        const isAct = row.getAttribute('data-d10') === d10Mode;
        row.classList.toggle('active', isAct);
        const check = row.querySelector('.menu-check');
        if (check) check.textContent = isAct ? '✓' : '';
    });

    const nakMode = currentNakshatraSystem || (localStorage.getItem('astra_nakshatra_system') || 'ERNST_DHRUVA');
    document.querySelectorAll('#settingsMenuDropdown .menu-row[data-nakshatra-system]').forEach(row => {
        const isAct = row.getAttribute('data-nakshatra-system') === nakMode;
        row.classList.toggle('active', isAct);
        const check = row.querySelector('.menu-check');
        if (check) check.textContent = isAct ? '✓' : '';
    });

    const rowSi = document.getElementById('menuRowSiSigns');
    if (rowSi) {
        const isAct = !!showSiSigns;
        rowSi.classList.toggle('active', isAct);
        const check = rowSi.querySelector('.menu-check');
        if (check) check.textContent = isAct ? '✓' : '';
    }
}

function switchChartType(type) {
    document.getElementById('view-south')?.classList.remove('active');
    document.getElementById('view-north')?.classList.remove('active');
    document.getElementById('view-circular')?.classList.remove('active');
    document.getElementById('view-biwheel')?.classList.remove('active');
    document.getElementById('btn-south')?.classList.remove('active');
    document.getElementById('btn-north')?.classList.remove('active');
    document.getElementById('btn-circular')?.classList.remove('active');
    document.getElementById('btn-biwheel')?.classList.remove('active');

    if (type === 'south') {
        document.getElementById('view-south')?.classList.add('active');
        document.getElementById('btn-south')?.classList.add('active');
    } else if (type === 'north') {
        document.getElementById('view-north')?.classList.add('active');
        document.getElementById('btn-north')?.classList.add('active');
    } else if (type === 'circular') {
        document.getElementById('view-circular')?.classList.add('active');
        document.getElementById('btn-circular')?.classList.add('active');
    } else if (type === 'biwheel') {
        document.getElementById('view-biwheel')?.classList.add('active');
        document.getElementById('btn-biwheel')?.classList.add('active');
    }
}

function updateSlot(slot) {
    const svgs = window.currentSvgs || currentSvgs;
    if (!svgs) return;
    const selectEl = document.getElementById(`vargaSelect${slot}`);
    if (!selectEl) return;
    const varga = selectEl.value;
    const vargaLabel = selectEl.options[selectEl.selectedIndex].text;

    if (slot === 1) {
        const titleEl = document.getElementById('toolbar-chart-title');
        if (titleEl) titleEl.innerText = vargaLabel;

        updateDignityTable(varga);
        if (typeof updateAspectsTable === 'function') updateAspectsTable(varga);
        if (typeof updateAvasthasTable === 'function') updateAvasthasTable(varga);
        if (typeof updateAvasthasCalcTable === 'function') updateAvasthasCalcTable(varga);
    }

    const vData = svgs[varga];
    const vSvg = (vData && vData[currentNotation]) ? vData[currentNotation] : vData;

    if (vSvg) {
        const s = document.getElementById(`southChart${slot}`);
        const n = document.getElementById(`northChart${slot}`);
        const c = document.getElementById(`circularChart${slot}`);
        if (s) s.innerHTML = vSvg.south;
        if (n) n.innerHTML = vSvg.north;
        if (c) c.innerHTML = vSvg.circular;
    }

    toggleSiSigns(showSiSigns);

    if (slot === 1) {
        updateBhavaTable(varga);
    }
}

// ==========================================
// Legacy Tables Compatibility Functions
// ==========================================
function updateBhavaTable(varga) {
    const tbody = document.querySelector('#bhavaTable tbody');
    if (!tbody) return;
    tbody.innerHTML = '';

    const chartData = window.currentChartData || currentChartData;
    if (!chartData || !chartData.vargas[varga]) return;

    const tableTitle = document.querySelector('#infoPanel h2:nth-of-type(2)');
    if (tableTitle) {
        tableTitle.innerText = `Bhava Chalita (Proper House Cusps) - ${varga}`;
    }

    const bhavas = chartData.vargas[varga].bhavas;

    function formatDegSign(lon) {
        const signs = ["Ar", "Ta", "Ge", "Cn", "Le", "Vi", "Li", "Sc", "Sg", "Cp", "Aq", "Pi"];
        const sign_idx = Math.floor(lon / 30);
        const deg = lon % 30;
        let d = Math.floor(deg);
        let m = Math.round((deg - d) * 60);
        if (m === 60) { d += 1; m = 0; }
        return `${signs[sign_idx]} ${d.toString().padStart(2, '0')}°${m.toString().padStart(2, '0')}'`;
    }

    for (let i = 1; i <= 12; i++) {
        const b = bhavas[i];
        if (!b) continue;
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td><strong>House ${i}</strong></td>
            <td>${formatDegSign(b.start_longitude)}</td>
            <td><strong>${formatDegSign(b.mid_longitude)}</strong></td>
            <td>${formatDegSign(b.end_longitude)}</td>
            <td>${b.planets.join(', ') || '-'}</td>
        `;
        tbody.appendChild(tr);
    }
}

function updateDignityTable(varga) {
    const tbody = document.querySelector('#dignityTable tbody');
    const sideTbody = document.querySelector('#dignitySideTable tbody');
    if(tbody) tbody.innerHTML = '';
    if(sideTbody) sideTbody.innerHTML = '';

    const chartData = window.currentChartData || currentChartData;
    if (!chartData || !chartData.vargas[varga]) return;

    const title = document.getElementById('dignityTitle');
    if (title) title.innerText = `Planetary Dignity & Sambandha (Panchadha) - ${varga}`;
    const sideTitle = document.getElementById('dignitySideTitle');
    if (sideTitle) sideTitle.innerText = `Planetary Dignity & Sambandha - ${varga}`;

    const grahas = chartData.vargas[varga].grahas;
    const planetsOrder = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"];

    planetsOrder.forEach(p => {
        if (!grahas[p] || !grahas[p].dignity_breakdown) return;
        const d = grahas[p].dignity_breakdown;

        let pTip = `<strong>${p}</strong><br>Click to inspect across divisional charts.`;
        let lordTip = `<strong>Sign Lord: ${d.sign_lord}</strong><br>Governs the zodiac sign currently occupied by ${p}.`;
        let natTip = `<strong>Natural Relationship: ${d.natural_relationship}</strong><br>Naisargika Sambandha based on permanent planetary archetypes.`;
        let tempTip = `<strong>Temporary Relationship: ${d.temporary_relationship}</strong><br>Tatkalika Sambandha based on house distance (friends in 2, 3, 4, 10, 11, 12; enemies in 1, 5, 6, 7, 8, 9).`;
        let compTip = `<strong>Compound Relationship: ${d.compound_relationship}</strong><br>Panchadha Sambandha combining natural and temporary relationships.`;
        let digTooltip = `<strong>${p} — Final Dignity: ${d.final_dignity}</strong>`;

        const rowHtml = `<td class="tooltip-target" data-tooltip="${pTip}" style="cursor:help;"><strong>${p}</strong></td>
                        <td class="tooltip-target" data-tooltip="${lordTip}" style="cursor:help;">${d.sign_lord}</td>
                        <td class="tooltip-target" data-tooltip="${natTip}" style="cursor:help;">${d.natural_relationship}</td>
                        <td class="tooltip-target" data-tooltip="${tempTip}" style="cursor:help;">${d.temporary_relationship}</td>
                        <td class="tooltip-target" data-tooltip="${compTip}" style="cursor:help;">${d.compound_relationship}</td>
                        <td class="tooltip-target" data-tooltip="${digTooltip}" style="cursor:help;"><strong>${d.final_dignity}</strong></td>`;

        if (tbody) {
            const tr = document.createElement('tr');
            tr.innerHTML = rowHtml;
            tbody.appendChild(tr);
        }

        if (sideTbody) {
            const trSide = document.createElement('tr');
            trSide.innerHTML = rowHtml;
            sideTbody.appendChild(trSide);
        }
    });
}

function updateNakshatraTable() {
    const chartData = window.currentChartData || currentChartData;
    if (!chartData || !chartData.nakshatras) return;
    const info = chartData.astronomy;
    const ayanEl = document.getElementById('ayanamsaName');
    if (ayanEl && info) ayanEl.innerText = `Ayanamsa: ${info.ayanamsa_name} (${info.equatorial_ayanamsa_value}°)`;

    const tbody = document.querySelector('#nakshatraTable tbody');
    if (!tbody) return;
    tbody.innerHTML = '';

    const naks = chartData.nakshatras.grahas;
    const d1_grahas = chartData.vargas.D1.grahas;
    const d1_lagna = chartData.vargas.D1.lagna;

    function formatDeg(deg_float) {
        let d = Math.floor(deg_float);
        let m = Math.round((deg_float - d) * 60);
        if (m === 60) { d += 1; m = 0; }
        return `${d.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}`;
    }

    if (naks["Lagna"] && d1_lagna) {
        const tr = document.createElement('tr');
        tr.innerHTML = `<td><strong>Asc</strong></td><td>${formatDeg(d1_lagna.degree_0_to_30)}</td><td>${d1_lagna.sign}</td><td>${naks["Lagna"].nakshatra}</td><td>${naks["Lagna"].pada}</td>`;
        tbody.appendChild(tr);
    }

    for (const [graha, data] of Object.entries(naks)) {
        if (graha === "Lagna" || !naks[graha] || !d1_grahas[graha]) continue;
        const isRetro = d1_grahas[graha].is_retrograde;
        const retroBadge = isRetro ? ' <span style="color:var(--status-malefic); font-weight:bold;">(R)</span>' : '';
        const tr = document.createElement('tr');
        tr.innerHTML = `<td><strong>${graha}</strong>${retroBadge}</td><td>${formatDeg(d1_grahas[graha].degree_0_to_30)}</td><td>${d1_grahas[graha].sign}</td><td>${naks[graha].nakshatra}</td><td>${naks[graha].pada}</td>`;
        tbody.appendChild(tr);
    }
}

function updateDashaTable() {
    const tbody = document.querySelector("#dashaTable tbody");
    if (!tbody) return;
    tbody.innerHTML = "";
    const chartData = window.currentChartData || currentChartData;
    if (!chartData || !chartData.vimshottari_dasha?.mahadashas) return;

    const dashas = chartData.vimshottari_dasha.mahadashas;
    dashas.forEach(d => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td><strong>${d.planet}</strong></td>
            <td>${formatToDDMMYYYY(d.start)}</td>
            <td>${formatToDDMMYYYY(d.end)}</td>
        `;
        tbody.appendChild(tr);
    });
}

function updateShadbalaTable() {
    const chartData = window.currentChartData || currentChartData;
    if (!chartData || !chartData.shadbala) return;
    const sb = chartData.shadbala;
    const planetsOrder = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"];

    const legacyTbody = document.querySelector("#shadbalaTable tbody");
    if (legacyTbody) {
        legacyTbody.innerHTML = "";
        planetsOrder.forEach(p => {
            if (!sb[p]) return;
            const data = sb[p];
            const isQualified = data.ratio >= 1.0;
            const statusColor = isQualified ? "var(--status-benefic)" : "var(--status-malefic)";
            const statusText = isQualified ? "Strong" : "Weak";

            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td><strong>${p}</strong></td>
                <td>${data.sthana_bala ? data.sthana_bala.toFixed(1) : '-'}</td>
                <td>${data.dig_bala ? data.dig_bala.toFixed(1) : '-'}</td>
                <td>${data.kala_bala ? data.kala_bala.toFixed(1) : '-'}</td>
                <td>${data.cheshta_bala ? data.cheshta_bala.toFixed(1) : '-'}</td>
                <td>${data.naisargika_bala ? data.naisargika_bala.toFixed(1) : '-'}</td>
                <td>${data.drik_bala ? data.drik_bala.toFixed(1) : '-'}</td>
                <td><strong>${data.total_rupa ? data.total_rupa.toFixed(2) : '-'}</strong></td>
                <td>${data.required_rupa ? data.required_rupa.toFixed(2) : '-'}</td>
                <td><strong style="color: ${statusColor}">${statusText} (${(data.ratio * 100).toFixed(0)}%)</strong></td>
            `;
            legacyTbody.appendChild(tr);
        });
    }
}

// ==========================================
// Tooltip Hover Engine
// ==========================================
(function() {
    function getTooltip() {
        let el = document.getElementById('global-tooltip');
        if (!el && document.body) {
            el = document.createElement('div');
            el.id = 'global-tooltip';
            el.style.display = 'none';
            el.style.position = 'absolute';
            el.style.zIndex = '99999';
            el.style.pointerEvents = 'none';
            document.body.appendChild(el);
        }
        return el;
    }

    let currentTarget = null;

    function positionTooltip(el) {
        const tooltip = getTooltip();
        if (!tooltip) return;
        const rect = el.getBoundingClientRect();
        const tooltipRect = tooltip.getBoundingClientRect();

        let top = rect.top + window.scrollY - tooltipRect.height - 8;
        let left = rect.left + window.scrollX + (rect.width / 2) - (tooltipRect.width / 2);

        if (left < 10) left = 10;
        if (left + tooltipRect.width > window.innerWidth - 10) {
            left = window.innerWidth - tooltipRect.width - 10;
        }

        if (top < window.scrollY + 10) {
            top = rect.bottom + window.scrollY + 8;
        }

        tooltip.style.top = top + 'px';
        tooltip.style.left = left + 'px';
    }

    document.addEventListener('mouseover', function(e) {
        const target = e.target.closest('.tooltip-target, .has-tooltip, [data-tooltip], [data-hint], td[title], th[title]');
        if (target) {
            currentTarget = target;
            if (target.hasAttribute('title')) {
                const rawTitle = target.getAttribute('title');
                if (!target.hasAttribute('data-tooltip') && rawTitle) {
                    target.setAttribute('data-tooltip', rawTitle);
                }
                target._stashedTitle = rawTitle;
                target.removeAttribute('title');
            }

            const text = target.getAttribute('data-tooltip') || target.getAttribute('data-hint');
            if (!text) return;

            const tooltip = getTooltip();
            if (!tooltip) return;
            tooltip.innerHTML = text.includes('<') ? text : text.replace(/\n/g, '<br>');
            tooltip.style.display = 'block';
            positionTooltip(target);
        }
    });

    document.addEventListener('mousemove', function() {
        const tooltip = getTooltip();
        if (currentTarget && tooltip && tooltip.style.display === 'block') {
            positionTooltip(currentTarget);
        }
    });

    document.addEventListener('mouseout', function(e) {
        const target = e.target.closest('.tooltip-target, .has-tooltip, [data-tooltip], [data-hint]');
        if (target) {
            const tooltip = getTooltip();
            if (tooltip) tooltip.style.display = 'none';
            if (target._stashedTitle) {
                target.setAttribute('title', target._stashedTitle);
            }
            currentTarget = null;
        }
    });
})();

// ==========================================
// Keyboard Hotkeys & Menu Event Listeners
// ==========================================
window.addEventListener('keydown', (e) => {
    // Ctrl+O / Cmd+O: Open Chart Library Modal
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'o') {
        e.preventDefault();
        if (typeof window.openChartModal === 'function') window.openChartModal();
        return;
    }

    // Birth Time Navigation Shortcuts (when not in form input)
    const activeTag = document.activeElement ? document.activeElement.tagName.toLowerCase() : '';
    const isInputActive = (activeTag === 'input' || activeTag === 'textarea' || activeTag === 'select');
    if (!isInputActive) {
        if (e.key === '[' && !e.shiftKey && !e.altKey && !e.ctrlKey && !e.metaKey) {
            e.preventDefault();
            stepBirthTime(-60); // -1m
        } else if (e.key === ']' && !e.shiftKey && !e.altKey && !e.ctrlKey && !e.metaKey) {
            e.preventDefault();
            stepBirthTime(60); // +1m
        } else if (e.key === '[' && e.altKey) {
            e.preventDefault();
            stepBirthTime(-1); // -1s
        } else if (e.key === ']' && e.altKey) {
            e.preventDefault();
            stepBirthTime(1); // +1s
        } else if (e.key === '[' && e.shiftKey && !e.ctrlKey) {
            e.preventDefault();
            stepBirthTime(-1800); // -30m
        } else if (e.key === ']' && e.shiftKey && !e.ctrlKey) {
            e.preventDefault();
            stepBirthTime(1800); // +30m
        } else if (e.key === '{' || (e.key === '[' && e.shiftKey && e.ctrlKey)) {
            e.preventDefault();
            stepBirthTime(-3600); // -1h
        } else if (e.key === '}' || (e.key === ']' && e.shiftKey && e.ctrlKey)) {
            e.preventDefault();
            stepBirthTime(3600); // +1h
        }

        // Chart Type Switching Hotkeys (S = South, N = North, C = Circular, B = Bi-Wheel)
        if (!e.ctrlKey && !e.metaKey && !e.altKey && ['s', 'n', 'c', 'b'].includes(e.key.toLowerCase())) {
            const k = e.key.toLowerCase();
            const styleMap = { 's': 'south', 'n': 'north', 'c': 'circular', 'b': 'biwheel' };
            const targetStyle = styleMap[k];
            const chartCell = (currentActiveCell && currentActiveCell.dataset.widget === 'chart')
                ? currentActiveCell
                : document.querySelector('.grid-cell[data-widget="chart"]');
            if (chartCell) {
                const btn = chartCell.querySelector('.btn-' + targetStyle);
                if (btn) switchWidgetChartType(btn, targetStyle);
            } else {
                setGlobalChartStyle(targetStyle);
            }
        }
    }
});

// Context Menu on Grid Cell
document.addEventListener('contextmenu', function(e) {
    const cell = e.target.closest('.grid-cell');
    if (cell) {
        e.preventDefault();
        currentActiveCell = cell;
        window.currentActiveCell = cell;
        if (typeof openKalaMenu === 'function') openKalaMenu(e.pageX, e.pageY);
    }
});

document.addEventListener('click', function(e) {
    const menu = document.getElementById('widget-context-menu');
    if (menu && menu.style.display === 'block') {
        menu.style.display = 'none';
    }

    const btn = e.target.closest('.menu-bar-btn');
    if (btn) {
        const parent = btn.closest('.menu-item-dropdown');
        if (parent) {
            const isOpen = parent.classList.contains('open');
            document.querySelectorAll('.menu-item-dropdown').forEach(m => m.classList.remove('open'));
            if (!isOpen) parent.classList.add('open');
            e.stopPropagation();
            return;
        }
    }

    if (!e.target.closest('.menu-item-dropdown')) {
        document.querySelectorAll('.menu-item-dropdown').forEach(m => m.classList.remove('open'));
    }
});

// ==========================================
// Bootstrap on DOMContentLoaded
// ==========================================
window.addEventListener('DOMContentLoaded', async () => {
    if (typeof initFloatingWindowDrag === 'function') initFloatingWindowDrag();
    if (typeof initFloatingWindowResize === 'function') initFloatingWindowResize();
    if (typeof initMaximizeChartDrag === 'function') initMaximizeChartDrag();
    if (typeof initMaximizeChartResize === 'function') initMaximizeChartResize();
    if (typeof initMaximizeChartPan === 'function') initMaximizeChartPan();
    if (typeof initWidgetChartZoomAndPan === 'function') initWidgetChartZoomAndPan();
    if (typeof loadCountries === 'function') await loadCountries();
    updateMenuCheckmarks();

    const select = document.getElementById('nativeSelect');
    if (select && select.options.length > 1 && select.options[1].value !== '__open_chart_dialog__') {
        select.selectedIndex = 1;
        if (typeof window.loadChart === 'function') {
            await window.loadChart(select.value);
        }
    }
});

// Global exports
if (typeof window !== 'undefined') {
    window.saveLayoutState = saveLayoutState;
    window.changeLayout = changeLayout;
    window.changeWorkspace = changeWorkspace;
    window.setupSplit = setupSplit;
    window.setupSplit_old = setupSplit_old;
    window.observeGridCells = observeGridCells;
    window.attachGutterAutoFit = attachGutterAutoFit;
    window.assignWidget = assignWidget;
    window.switchWidgetRootPlanet = switchWidgetRootPlanet;
    window.switchWidgetChartType = switchWidgetChartType;
    window.updateWidget = updateWidget;
    window.updateAllWidgets = updateAllWidgets;
    window.assignKalaChart = assignKalaChart;
    window.assignKalaWidget = assignKalaWidget;
    window.assignKalaPerspective = assignKalaPerspective;
    window.setGlobalChartStyle = setGlobalChartStyle;
    window.toggleHouseHighlight = toggleHouseHighlight;
    window.clearHouseHighlights = clearHouseHighlights;
    window.applyHouseHighlights = applyHouseHighlights;
    window.stepBirthTime = stepBirthTime;
    window.applyBirthTimeOffset = applyBirthTimeOffset;
    window.resetBirthTimePreview = resetBirthTimePreview;
    window.savePreviewedBirthTime = savePreviewedBirthTime;
    window.syncAllSteppersUI = syncAllSteppersUI;
    window.formatOffsetLabel = formatOffsetLabel;
    window.setNakshatraSystem = setNakshatraSystem;
    window.toggleNakshatraSystem = toggleNakshatraSystem;
    window.syncNakshatraSystemUI = syncNakshatraSystemUI;
    window.setD10Mode = setD10Mode;
    window.toggleD10Mode = toggleD10Mode;
    window.syncD10ModeUI = syncD10ModeUI;
    window.switchNotation = switchNotation;
    window.onModalNotationChange = onModalNotationChange;
    window.onModalLayoutChange = onModalLayoutChange;
    window.onModalSignToggle = onModalSignToggle;
    window.toggleSiSigns = toggleSiSigns;
    window.toggleSiSignsFromMenu = toggleSiSignsFromMenu;
    window.updateMenuCheckmarks = updateMenuCheckmarks;
    window.switchChartType = switchChartType;
    window.updateSlot = updateSlot;
    window.toggleHelp = toggleHelp;
    window.formatToDDMMYYYY = formatToDDMMYYYY;
    window.updateBhavaTable = updateBhavaTable;
    window.updateDignityTable = updateDignityTable;
    window.updateNakshatraTable = updateNakshatraTable;
    window.updateDashaTable = updateDashaTable;
    window.updateShadbalaTable = updateShadbalaTable;
    window.updateShadbalaTableWidget = updateShadbalaTableWidget;
    window.updateDashaTimelineWidget = updateDashaTimelineWidget;
}
