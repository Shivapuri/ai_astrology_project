/**
 * Astra Transit Bi-Wheel Widget (Gochara)
 * 
 * Provides an interactive 2-ring Transit Bi-Wheel (Kala style):
 * - Real-time and date-stepper controls (minutely, 10-min, hourly, daily, weekly, monthly, yearly)
 * - Continuous Play / Pause animation loop
 * - Dynamic aspect chords connecting transiting planets to natal targets (Phaladeepika 3°20' orb)
 * - Triple perspective: Lagna, Chandra Lagna (Moon), and Surya Lagna (Sun)
 * - Bulletproof date parsing & live date readout
 */

(function() {
    // Registry of active widget instances mapped by container element
    const activeInstances = new Map();

    function getActiveNativeId() {
        if (window.currentLoadedNative && window.currentLoadedNative.id) {
            return window.currentLoadedNative.id;
        }
        if (window.astraStore && window.astraStore.state && window.astraStore.state.currentNative && window.astraStore.state.currentNative.id) {
            return window.astraStore.state.currentNative.id;
        }
        if (window.currentChartData && window.currentChartData.subject_info && window.currentChartData.subject_info.id) {
            return window.currentChartData.subject_info.id;
        }
        const select = document.getElementById('nativeSelect');
        if (select && select.value && select.value !== '__open_chart_dialog__') {
            return select.value;
        }
        if (select && select.options && select.options.length > 1) {
            for (let i = 1; i < select.options.length; i++) {
                const val = select.options[i].value;
                if (val && val !== '__open_chart_dialog__') {
                    return val;
                }
            }
        }
        return '';
    }

    function formatLocalDate(d) {
        if (!d || isNaN(d.getTime())) d = new Date();
        const y = d.getFullYear();
        const m = String(d.getMonth() + 1).padStart(2, '0');
        const day = String(d.getDate()).padStart(2, '0');
        return `${y}-${m}-${day}`;
    }

    function formatDisplayDate(d) {
        if (!d || isNaN(d.getTime())) d = new Date();
        const y = d.getFullYear();
        const m = String(d.getMonth() + 1).padStart(2, '0');
        const day = String(d.getDate()).padStart(2, '0');
        return `${day}/${m}/${y}`;
    }

    function formatLocalTime(d) {
        if (!d || isNaN(d.getTime())) d = new Date();
        const h = String(d.getHours()).padStart(2, '0');
        const m = String(d.getMinutes()).padStart(2, '0');
        const s = String(d.getSeconds()).padStart(2, '0');
        return `${h}:${m}:${s}`;
    }

    function formatFullDateTime(d) {
        if (!d || isNaN(d.getTime())) d = new Date();
        return `${formatDisplayDate(d)} ${formatLocalTime(d)}`;
    }

    function parseDateString(str) {
        if (!str) return new Date();
        const clean = str.trim();
        // 1. Matches YYYY-MM-DD or YYYY.MM.DD or YYYY/MM/DD
        let match = clean.match(/^(\d{4})[-./\s]+(\d{1,2})[-./\s]+(\d{1,2})\.?$/);
        if (match) {
            const y = parseInt(match[1], 10);
            const m = parseInt(match[2], 10) - 1;
            const d = parseInt(match[3], 10);
            const dt = new Date(y, m, d);
            return isNaN(dt.getTime()) ? new Date() : dt;
        }
        // 2. Matches DD/MM/YYYY or DD-MM-YYYY or DD.MM.YYYY
        match = clean.match(/^(\d{1,2})[-./\s]+(\d{1,2})[-./\s]+(\d{4})$/);
        if (match) {
            const d = parseInt(match[1], 10);
            const m = parseInt(match[2], 10) - 1;
            const y = parseInt(match[3], 10);
            const dt = new Date(y, m, d);
            return isNaN(dt.getTime()) ? new Date() : dt;
        }
        const parsed = new Date(clean);
        return isNaN(parsed.getTime()) ? new Date() : parsed;
    }

    function createInstanceState(cell) {
        return {
            cell: cell,
            currentDate: new Date(),
            interval: '1d',
            isPlaying: false,
            playTimer: null,
            root: 'Lagna',
            showTable: false,
            isFetching: false,
            abortController: null
        };
    }

    function stepTime(state, direction, multiplier = 1) {
        if (!state.currentDate || isNaN(state.currentDate.getTime())) {
            state.currentDate = new Date();
        }
        const d = new Date(state.currentDate.getTime());
        const stepVal = direction * multiplier;

        switch (state.interval) {
            case 'realtime':
                state.currentDate = new Date();
                break;
            case '1m':
                d.setMinutes(d.getMinutes() + stepVal * 1);
                state.currentDate = d;
                break;
            case '10m':
                d.setMinutes(d.getMinutes() + stepVal * 10);
                state.currentDate = d;
                break;
            case '1h':
                d.setHours(d.getHours() + stepVal * 1);
                state.currentDate = d;
                break;
            case '1d':
                d.setDate(d.getDate() + stepVal * 1);
                state.currentDate = d;
                break;
            case '1w':
                d.setDate(d.getDate() + stepVal * 7);
                state.currentDate = d;
                break;
            case '30d':
                d.setDate(d.getDate() + stepVal * 30);
                state.currentDate = d;
                break;
            case '365d':
                d.setFullYear(d.getFullYear() + stepVal * 1);
                state.currentDate = d;
                break;
            default:
                d.setDate(d.getDate() + stepVal * 1);
                state.currentDate = d;
        }

        syncInputsFromState(state);
        fetchAndRender(state);
    }

    function syncInputsFromState(state) {
        const cell = state.cell;
        if (!cell) return;
        const dateInput = cell.querySelector('.transit-date-input');
        const timeInput = cell.querySelector('.transit-time-input');
        const displayLabel = cell.querySelector('.transit-date-display-text');

        if (dateInput) dateInput.value = formatLocalDate(state.currentDate);
        if (timeInput) timeInput.value = formatLocalTime(state.currentDate);
        if (displayLabel) displayLabel.textContent = formatFullDateTime(state.currentDate);
    }

    function togglePlay(state) {
        const cell = state.cell;
        const playBtn = cell.querySelector('.btn-transit-play-pause');

        if (state.isPlaying) {
            // Stop
            if (state.playTimer) clearInterval(state.playTimer);
            state.playTimer = null;
            state.isPlaying = false;
            if (playBtn) {
                playBtn.innerHTML = '&#9654; Play';
                playBtn.style.background = '#d35400';
            }
        } else {
            // Start
            state.isPlaying = true;
            if (playBtn) {
                playBtn.innerHTML = '&#10074;&#10074; Pause';
                playBtn.style.background = '#c0392b';
            }
            let speedMs = 300;
            if (state.interval === 'realtime') speedMs = 1000;
            else if (['1w', '30d'].includes(state.interval)) speedMs = 350;
            else if (state.interval === '365d') speedMs = 450;

            state.playTimer = setInterval(() => {
                stepTime(state, 1, 1);
            }, speedMs);
        }
    }

    function fetchAndRender(state) {
        const cell = state.cell;
        if (!cell) return;

        const natId = getActiveNativeId();
        if (!natId) {
            const svgContainer = cell.querySelector('.transit-svg-container');
            if (svgContainer) {
                svgContainer.innerHTML = '<div style="font-size:13px; color:#8c7b64; padding:20px; text-align:center;">Please load or select a person from the top toolbar to view transits.</div>';
            }
            return;
        }

        // Cancel previous pending fetch so rapid navigation never queues or freezes
        if (state.abortController) {
            state.abortController.abort();
        }
        state.abortController = new AbortController();

        const dateStr = formatLocalDate(state.currentDate);
        const timeStr = formatLocalTime(state.currentDate);
        const nakSys = window.currentNakshatraSystem || 'ERNST_DHRUVA';
        const debMode = window.currentDebilitationMode || 'kala_degree';
        const notation = window.currentNotation || 'symbol';
        const showNak = (typeof window.currentShowNakshatras !== 'undefined') ? window.currentShowNakshatras : false;

        const url = `/api/chart/${natId}/transit?transit_date=${dateStr}&transit_time=${timeStr}&nakshatra_system=${nakSys}&debilitation_mode=${debMode}&mode=${notation}&root=${state.root}&show_nakshatras=${showNak}`;

        fetch(url, { signal: state.abortController.signal })
            .then(res => {
                if (!res.ok) throw new Error(`HTTP ${res.status}`);
                return res.json();
            })
            .then(data => {
                if (!data || !data.svg) return;

                const svgContainer = cell.querySelector('.transit-svg-container');
                if (svgContainer) {
                    svgContainer.innerHTML = data.svg;
                    attachSvgInteractivity(cell);
                }

                // Update aspects table & badge
                const countBadge = cell.querySelector('.transit-aspect-count');
                const aspects = data.active_aspects || [];
                if (countBadge) countBadge.textContent = aspects.length;

                const tbody = cell.querySelector('.transit-aspects-tbody');
                if (tbody) {
                    tbody.innerHTML = '';
                    if (aspects.length === 0) {
                        tbody.innerHTML = '<tr><td colspan="5" style="padding:6px; color:#8c7b64; text-align:center;">No active transit triggers within 3°20\' orb.</td></tr>';
                    } else {
                        aspects.forEach(asp => {
                            const tr = document.createElement('tr');
                            tr.style.borderBottom = '1px solid #edece6';
                            const col = asp.is_benefic ? '#27ae60' : (asp.code === 'CONJ' ? '#8e44ad' : '#c0392b');
                            tr.innerHTML = `
                                <td style="padding:4px 6px; font-weight:bold; color:${col};">${asp.aspecting}</td>
                                <td style="padding:4px 6px;">${asp.type}</td>
                                <td style="padding:4px 6px; font-weight:600;">Natal ${asp.target}</td>
                                <td style="padding:4px 6px; font-variant-numeric:tabular-nums;">${asp.orb}°</td>
                                <td style="padding:4px 6px; font-variant-numeric:tabular-nums;">${asp.virupas} V</td>
                            `;
                            tbody.appendChild(tr);
                        });
                    }
                }

                const tsBadge = cell.querySelector('.transit-timestamp-badge');
                if (tsBadge && data.transit_time_info) {
                    tsBadge.textContent = data.transit_time_info.formatted;
                }

                // Update the live formatted date display badge
                const displayLabel = cell.querySelector('.transit-date-display-text');
                if (displayLabel) {
                    displayLabel.textContent = formatFullDateTime(state.currentDate);
                }
            })
            .catch(err => {
                if (err.name === 'AbortError') return; // Expected cancellation on fast step
                console.error("Error fetching transit chart:", err);
            });
    }

    function attachSvgInteractivity(cell) {
        const svg = cell.querySelector('.transit-biwheel-svg');
        if (!svg) return;

        const outerPlanets = svg.querySelectorAll('.transit-planet');
        const aspectLines = svg.querySelectorAll('.transit-aspect-line');

        outerPlanets.forEach(p => {
            const pName = p.getAttribute('data-planet');
            p.addEventListener('mouseenter', () => {
                aspectLines.forEach(line => {
                    const fromP = line.getAttribute('data-from');
                    if (fromP === pName) {
                        line.style.opacity = '1.0';
                        line.style.strokeWidth = '2.2px';
                    } else {
                        line.style.opacity = '0.15';
                    }
                });
            });

            p.addEventListener('mouseleave', () => {
                aspectLines.forEach(line => {
                    line.style.opacity = '0.75';
                    line.style.strokeWidth = '0.9px';
                });
            });
        });
    }

    function setRootPerspective(state, root) {
        state.root = root;
        const cell = state.cell;
        const btnLagna = cell.querySelector('.btn-transit-root-lagna');
        const btnMoon = cell.querySelector('.btn-transit-root-moon');
        const btnSun = cell.querySelector('.btn-transit-root-sun');

        [btnLagna, btnMoon, btnSun].forEach(b => {
            if (!b) return;
            const isMatch = b.getAttribute('data-root') === root;
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

        fetchAndRender(state);
    }

    function initTransitWidget(cell) {
        let state = activeInstances.get(cell);
        if (state) {
            // Clean up any existing playback timers on re-initialization
            if (state.playTimer) clearInterval(state.playTimer);
            state.playTimer = null;
            state.isPlaying = false;
            state.cell = cell;
        } else {
            state = createInstanceState(cell);
            activeInstances.set(cell, state);
        }

        syncInputsFromState(state);

        // Bind Stepper Controls
        const btnStepBack = cell.querySelector('.btn-transit-step-back');
        const btnStepFwd = cell.querySelector('.btn-transit-step-fwd');
        const btnFastBack = cell.querySelector('.btn-transit-step-fast-back');
        const btnFastFwd = cell.querySelector('.btn-transit-step-fast-fwd');
        const btnNow = cell.querySelector('.btn-transit-now');
        const btnPlay = cell.querySelector('.btn-transit-play-pause');
        const intervalSelect = cell.querySelector('.transit-interval-select');
        const dateInput = cell.querySelector('.transit-date-input');
        const timeInput = cell.querySelector('.transit-time-input');
        const btnRootLagna = cell.querySelector('.btn-transit-root-lagna');
        const btnRootMoon = cell.querySelector('.btn-transit-root-moon');
        const btnRootSun = cell.querySelector('.btn-transit-root-sun');
        const btnToggleTable = cell.querySelector('.btn-transit-toggle-table');
        const drawer = cell.querySelector('.transit-aspects-drawer');

        if (btnStepBack) btnStepBack.onclick = () => stepTime(state, -1, 1);
        if (btnStepFwd) btnStepFwd.onclick = () => stepTime(state, 1, 1);
        if (btnFastBack) btnFastBack.onclick = () => stepTime(state, -1, 5);
        if (btnFastFwd) btnFastFwd.onclick = () => stepTime(state, 1, 5);

        if (btnNow) {
            btnNow.onclick = () => {
                state.currentDate = new Date();
                syncInputsFromState(state);
                fetchAndRender(state);
            };
        }

        if (btnPlay) {
            btnPlay.onclick = () => togglePlay(state);
        }

        if (intervalSelect) {
            intervalSelect.value = state.interval;
            intervalSelect.onchange = () => {
                state.interval = intervalSelect.value;
                if (state.isPlaying) {
                    togglePlay(state); // Stop
                    togglePlay(state); // Restart with new interval speed
                }
            };
        }

        const handleDateChange = () => {
            if (dateInput && dateInput.value) {
                const parsed = parseDateString(dateInput.value);
                state.currentDate.setFullYear(parsed.getFullYear(), parsed.getMonth(), parsed.getDate());
                syncInputsFromState(state);
                fetchAndRender(state);
            }
        };

        if (dateInput) {
            dateInput.onchange = handleDateChange;
            dateInput.oninput = handleDateChange;
        }

        const handleTimeChange = () => {
            if (timeInput && timeInput.value) {
                const parts = timeInput.value.split(':');
                state.currentDate.setHours(parseInt(parts[0], 10) || 0, parseInt(parts[1], 10) || 0, parseInt(parts[2], 10) || 0);
                syncInputsFromState(state);
                fetchAndRender(state);
            }
        };

        if (timeInput) {
            timeInput.onchange = handleTimeChange;
            timeInput.oninput = handleTimeChange;
        }

        if (btnRootLagna) btnRootLagna.onclick = () => setRootPerspective(state, 'Lagna');
        if (btnRootMoon) btnRootMoon.onclick = () => setRootPerspective(state, 'Moon');
        if (btnRootSun) btnRootSun.onclick = () => setRootPerspective(state, 'Sun');

        if (btnToggleTable && drawer) {
            btnToggleTable.onclick = () => {
                state.showTable = !state.showTable;
                drawer.style.display = state.showTable ? 'block' : 'none';
            };
        }

        fetchAndRender(state);
    }

    // Register widget in WidgetRegistry
    if (typeof window !== 'undefined' && window.widgetRegistry) {
        window.widgetRegistry.register('transit-chart', {
            id: 'transit-chart',
            title: 'Transit Bi-Wheel',
            icon: '🪐',
            category: 'Charts',
            templateId: 'tmpl-transit-chart',
            render: function(container, chartData, options) {
                const tmpl = document.getElementById('tmpl-transit-chart');
                if (tmpl) {
                    container.innerHTML = tmpl.innerHTML;
                    initTransitWidget(container);
                }
            },
            onUpdate: function(cell, chartData) {
                const state = activeInstances.get(cell);
                if (state) {
                    fetchAndRender(state);
                } else {
                    initTransitWidget(cell);
                }
            }
        });
    }

    // Open Transit Bi-Wheel in a Floating Modal Window
    function openFloatingTransit() {
        const modal = document.getElementById('widgetMaximizeModal');
        const card = document.getElementById('widgetMaximizeCard');
        const titleEl = document.getElementById('widgetMaximizeModalTitle');
        const container = document.getElementById('widgetMaximizeContainer');
        if (!modal || !titleEl || !container) return;

        if (typeof resetFloatingWindowPosition === 'function') resetFloatingWindowPosition();
        if (card) {
            const w = Math.min(1050, window.innerWidth - 40);
            const h = Math.min(860, window.innerHeight - 60);
            card.style.width = w + 'px';
            card.style.height = h + 'px';
            card.style.left = Math.max(20, Math.round((window.innerWidth - w) / 2)) + 'px';
            card.style.top = Math.max(30, Math.round((window.innerHeight - h) / 2)) + 'px';
        }

        titleEl.textContent = '🪐 Animated Transit Bi-Wheel (Gochara)';
        modal.style.display = 'block';

        const tmpl = document.getElementById('tmpl-transit-chart');
        if (tmpl) {
            container.innerHTML = tmpl.innerHTML;
            initTransitWidget(container);
        }

        // Highlight nav pill if present
        const navPills = document.querySelectorAll('.floating-nav-pill');
        navPills.forEach(p => p.classList.remove('active'));
        const transitPill = document.getElementById('nav-btn-transit');
        if (transitPill) transitPill.classList.add('active');
    }

    // Export globally for testing / manual invocation
    if (typeof window !== 'undefined') {
        window.initTransitWidget = initTransitWidget;
        window.openFloatingTransit = openFloatingTransit;
    }
})();
