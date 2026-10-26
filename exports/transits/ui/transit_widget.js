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
            orb: 3.3333,
            isPlaying: false,
            playTimer: null,
            root: 'Lagna',
            showTable: false,
            showRadar: true,
            radarFilter: 'all',
            milestones: [],
            upcomingStations: [],
            isFetching: false,
            abortController: null
        };
    }

    function pulseLiveBadge(cell) {
        if (!cell) return;
        const badge = cell.querySelector('.transit-live-badge');
        if (badge) {
            badge.style.transition = 'all 0.15s ease';
            badge.style.borderColor = '#d35400';
            badge.style.background = '#faede0';
            setTimeout(() => {
                badge.style.borderColor = '#d5c8b2';
                badge.style.background = '#fffdfa';
            }, 250);
        }
    }

    function stepTime(state, direction, multiplier = 1, onComplete = null) {
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

        pulseLiveBadge(state.cell);
        syncInputsFromState(state);
        fetchAndRender(state, onComplete);
    }

    function syncInputsFromState(state) {
        const cell = state.cell;
        if (!cell) return;
        const dateInput = cell.querySelector('.transit-date-input');
        const timeInput = cell.querySelector('.transit-time-input');
        const displayLabel = cell.querySelector('.transit-date-display-text');
        const intervalSelect = cell.querySelector('.transit-interval-select');
        const orbSelect = cell.querySelector('.transit-orb-select');

        if (dateInput) dateInput.value = formatLocalDate(state.currentDate);
        if (timeInput) timeInput.value = formatLocalTime(state.currentDate);
        if (displayLabel) displayLabel.textContent = formatFullDateTime(state.currentDate);
        if (intervalSelect && state.interval) intervalSelect.value = state.interval;
        if (orbSelect && state.orb) orbSelect.value = String(state.orb);
    }

    function scheduleNextPlay(state) {
        if (!state.isPlaying) return;
        let speedMs = 300;
        if (state.interval === 'realtime') speedMs = 1000;
        else if (['1w', '30d'].includes(state.interval)) speedMs = 350;
        else if (state.interval === '365d') speedMs = 450;

        state.playTimer = setTimeout(() => {
            if (!state.isPlaying) return;
            stepTime(state, 1, 1, () => {
                if (state.isPlaying) {
                    scheduleNextPlay(state);
                }
            });
        }, speedMs);
    }

    function togglePlay(state) {
        const cell = state.cell;
        const playBtn = cell.querySelector('.btn-transit-play-pause');
        const dot = cell.querySelector('.transit-status-dot');

        if (state.isPlaying) {
            // Stop
            if (state.playTimer) clearTimeout(state.playTimer);
            state.playTimer = null;
            state.isPlaying = false;
            if (playBtn) {
                playBtn.innerHTML = '&#9654; Play';
                playBtn.style.background = '#d35400';
            }
            if (dot) dot.style.color = '#27ae60';
        } else {
            // Start
            state.isPlaying = true;
            if (playBtn) {
                playBtn.innerHTML = '&#10074;&#10074; Pause';
                playBtn.style.background = '#c0392b';
            }
            if (dot) dot.style.color = '#e74c3c';
            scheduleNextPlay(state);
        }
    }

    function jumpToMilestone(state, dateStr, timeStr) {
        if (!dateStr) return;
        const parsed = parseDateString(dateStr);
        if (timeStr) {
            const parts = timeStr.split(':');
            parsed.setHours(
                parseInt(parts[0], 10) || 0,
                parseInt(parts[1], 10) || 0,
                parseInt(parts[2], 10) || 0
            );
        }
        state.currentDate = parsed;
        pulseLiveBadge(state.cell);
        syncInputsFromState(state);
        fetchAndRender(state);
    }

    function stepMilestone(state, direction) {
        if (!state.milestones || state.milestones.length === 0) return;
        const curTime = state.currentDate.getTime();
        const thresholdMs = 45 * 1000;

        if (direction > 0) {
            let nextM = state.milestones.find(m => {
                const mDt = parseDateString(m.jump_date);
                if (m.jump_time) {
                    const p = m.jump_time.split(':');
                    mDt.setHours(parseInt(p[0], 10) || 0, parseInt(p[1], 10) || 0, parseInt(p[2], 10) || 0);
                }
                return mDt.getTime() > curTime + thresholdMs;
            });
            if (!nextM) nextM = state.milestones[state.milestones.length - 1];
            if (nextM) jumpToMilestone(state, nextM.jump_date, nextM.jump_time);
        } else {
            let prevM = null;
            for (let i = state.milestones.length - 1; i >= 0; i--) {
                const m = state.milestones[i];
                const mDt = parseDateString(m.jump_date);
                if (m.jump_time) {
                    const p = m.jump_time.split(':');
                    mDt.setHours(parseInt(p[0], 10) || 0, parseInt(p[1], 10) || 0, parseInt(p[2], 10) || 0);
                }
                if (mDt.getTime() < curTime - thresholdMs) {
                    prevM = m;
                    break;
                }
            }
            if (!prevM) prevM = state.milestones[0];
            if (prevM) jumpToMilestone(state, prevM.jump_date, prevM.jump_time);
        }
    }

    function renderMilestones(state) {
        const cell = state.cell;
        if (!cell) return;
        const listContainer = cell.querySelector('.transit-radar-list');
        const countBadge = cell.querySelector('.transit-radar-count');
        if (!listContainer) return;

        const allMilestones = state.milestones || [];
        if (countBadge) countBadge.textContent = allMilestones.length;

        const filter = state.radarFilter || 'all';
        let filtered = allMilestones;
        if (filter === 'stations') {
            filtered = allMilestones.filter(m => m.category === 'NATAL_STATION' || m.category === 'SKY_STATION');
        } else if (filter === 'natal_hits') {
            filtered = allMilestones.filter(m => m.category === 'NATAL_STATION' || m.category === 'EXACT_ASPECT');
        } else if (filter === 'ingresses') {
            filtered = allMilestones.filter(m => m.category === 'SIGN_INGRESS');
        }

        listContainer.innerHTML = '';
        if (filtered.length === 0) {
            listContainer.innerHTML = '<div style="font-size:12px; color:#8c7b64; text-align:center; padding:15px;">No milestones found in this filter category.</div>';
            return;
        }

        const curTime = state.currentDate.getTime();
        let closestDist = Infinity;
        let closestCard = null;

        filtered.forEach(m => {
            const card = document.createElement('div');
            card.className = 'transit-milestone-card';
            card.dataset.category = m.category;
            card.dataset.jumpDate = m.jump_date;
            card.dataset.jumpTime = m.jump_time;

            const mDt = parseDateString(m.jump_date);
            if (m.jump_time) {
                const p = m.jump_time.split(':');
                mDt.setHours(parseInt(p[0], 10) || 0, parseInt(p[1], 10) || 0, parseInt(p[2], 10) || 0);
            }
            const dist = Math.abs(mDt.getTime() - curTime);

            let leftAccent = '#94a3b8';
            let labelClass = 'radar-label-sky-station';
            let labelText = '';

            if (m.category === 'NATAL_STATION') {
                leftAccent = '#b91c1c';
                labelClass = 'radar-label-natal-station';
                labelText = '★ STATION ON NATAL';
            } else if (m.category === 'EXACT_ASPECT') {
                leftAccent = '#b45309';
                labelClass = 'radar-label-exact-aspect';
                const passStr = (m.total_passes && m.total_passes > 1) ? ` (Pass ${m.pass_number}/${m.total_passes})` : '';
                labelText = `◎ EXACT HIT${passStr}`;
            } else if (m.category === 'SIGN_INGRESS') {
                leftAccent = '#0f766e';
                labelClass = 'radar-label-ingress';
                labelText = '→ INGRESS';
            } else {
                leftAccent = '#64748b';
                labelClass = 'radar-label-sky-station';
                const stStr = m.station_type ? ` · ${m.station_type}` : '';
                labelText = `⟲ STATION${stStr}`;
            }

            const timeLabel = `${m.formatted_date} · ${String(m.hour).padStart(2, '0')}:${String(m.minute).padStart(2, '0')}`;

            card.style.border = '1px solid #eae2d3';
            card.style.borderLeft = `3px solid ${leftAccent}`;
            card.style.background = '#fffdfa';
            card.style.borderRadius = '2px';
            card.style.padding = '5px 8px';
            card.style.cursor = 'pointer';
            card.style.display = 'flex';
            card.style.flexDirection = 'column';
            card.style.gap = '3px';
            card.style.fontFamily = 'var(--font-german-din, "DIN Alternate", -apple-system, sans-serif)';
            card.style.transition = 'background 0.12s ease, border-color 0.12s ease';

            card.innerHTML = `
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-size:12px; font-weight:600; color:#5c4433; font-variant-numeric:tabular-nums; letter-spacing:0.3px;">${timeLabel}</span>
                    <span class="${labelClass}" style="font-size:12px; font-weight:700; letter-spacing:0.5px; text-transform:uppercase;">${labelText}</span>
                </div>
                <div style="font-size:12.5px; font-weight:500; color:#2c221b; line-height:1.35; font-family:var(--font-german-din, 'DIN Alternate', -apple-system, sans-serif);">
                    ${m.description}
                </div>
            `;

            if (dist < closestDist) {
                closestDist = dist;
                closestCard = card;
            }

            card.addEventListener('click', () => {
                jumpToMilestone(state, m.jump_date, m.jump_time);
            });

            card.addEventListener('mouseenter', () => {
                if (m.planet && m.natal_target) {
                    highlightTransitAspect(cell, m.planet, m.natal_target);
                }
            });

            card.addEventListener('mouseleave', () => {
                resetTransitAspectHighlights(cell);
            });

            listContainer.appendChild(card);
        });

        // Highlight closest card within 24 hours
        if (closestCard && closestDist < (24 * 3600 * 1000)) {
            closestCard.classList.add('active-jumped');
            closestCard.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
        }
    }

    function fetchAndRender(state, onComplete = null) {
        const cell = state.cell;
        if (!cell) {
            if (typeof onComplete === 'function') onComplete();
            return;
        }

        const natId = getActiveNativeId();
        if (!natId) {
            const svgContainer = cell.querySelector('.transit-svg-container');
            if (svgContainer) {
                svgContainer.innerHTML = '<div style="font-size:13px; color:#8c7b64; padding:20px; text-align:center;">Please load or select a person from the top toolbar to view transits.</div>';
            }
            if (typeof onComplete === 'function') onComplete();
            return;
        }

        // Cancel previous pending fetch only if NOT in play loop
        if (!state.isPlaying && state.abortController) {
            state.abortController.abort();
            state.abortController = null;
        }
        if (!state.abortController) {
            state.abortController = new AbortController();
        }

        const dateStr = formatLocalDate(state.currentDate);
        const timeStr = formatLocalTime(state.currentDate);
        const nakSys = window.currentNakshatraSystem || 'ERNST_DHRUVA';
        const debMode = window.currentDebilitationMode || 'kala_degree';
        const notation = window.currentNotation || 'symbol';
        const showNak = (typeof window.currentShowNakshatras !== 'undefined') ? window.currentShowNakshatras : false;

        const orbVal = state.orb || 3.3333;
        const url = `/api/chart/${natId}/transit?transit_date=${dateStr}&transit_time=${timeStr}&orb=${orbVal}&nakshatra_system=${nakSys}&debilitation_mode=${debMode}&mode=${notation}&root=${state.root}&show_nakshatras=${showNak}`;

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
                        tbody.innerHTML = `<tr><td colspan="6" style="padding:6px; color:#8c7b64; text-align:center; font-size:12px;">No active transit triggers within ${orbVal === 3.3333 ? "3°20' Navāmśa" : orbVal + "°"} orb.</td></tr>`;
                    } else {
                        aspects.forEach(asp => {
                            const tr = document.createElement('tr');
                            tr.className = 'transit-aspect-row';
                            tr.style.borderBottom = '1px solid #edece6';
                            tr.style.cursor = 'pointer';
                            tr.dataset.from = asp.aspecting;
                            tr.dataset.to = asp.target;

                            const col = asp.is_benefic ? '#27ae60' : (asp.code === 'CONJ' ? '#8e44ad' : '#c0392b');
                            const motionText = asp.motion_status || (asp.is_applying ? 'Applying' : 'Separating');
                            const motionColor = asp.is_applying ? '#2e7d32' : '#795548';
                            const motionArrow = asp.is_applying ? '→' : '←';

                            tr.innerHTML = `
                                <td style="padding:3px 6px; font-weight:bold; color:${col}; font-size:12px;">${asp.aspecting}</td>
                                <td style="padding:3px 6px; font-size:12px;">${asp.type}</td>
                                <td style="padding:3px 6px; font-weight:600; font-size:12px;">Natal ${asp.target}</td>
                                <td style="padding:3px 6px; font-variant-numeric:tabular-nums; font-size:12px;">${asp.orb}°</td>
                                <td style="padding:3px 6px; font-variant-numeric:tabular-nums; font-size:12px;">${asp.virupas} V</td>
                                <td style="padding:3px 6px; font-size:12px; font-weight:600; color:${motionColor}; font-variant-numeric:tabular-nums;">${motionArrow} ${motionText}</td>
                            `;

                            tr.addEventListener('mouseenter', () => {
                                tr.style.background = '#f5eedb';
                                highlightTransitAspect(cell, asp.aspecting, asp.target);
                            });
                            tr.addEventListener('mouseleave', () => {
                                tr.style.background = 'transparent';
                                resetTransitAspectHighlights(cell);
                            });

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

                // Update Milestones & Upcoming Stations in the Gochara Radar Panel
                state.milestones = data.milestones || [];
                state.upcomingStations = data.upcoming_stations || [];
                renderMilestones(state);
            })
            .catch(err => {
                if (err.name === 'AbortError') return; // Expected cancellation on fast step
                console.error("Error fetching transit chart:", err);
            })
            .finally(() => {
                if (typeof onComplete === 'function') {
                    onComplete();
                }
            });
    }

    function highlightTransitAspect(cell, fromPlanet, toPlanet) {
        const svg = cell.querySelector('.transit-biwheel-svg');
        if (!svg) return;

        const lines = svg.querySelectorAll('.transit-aspect-line');
        lines.forEach(l => {
            const match = (l.getAttribute('data-from') === fromPlanet && l.getAttribute('data-to') === toPlanet);
            l.style.opacity = match ? '1.0' : '0.12';
            l.style.strokeWidth = match ? '2.4px' : '0.8px';
        });

        // Highlight matching dots
        svg.querySelectorAll('.transit-planet-dot').forEach(d => {
            d.style.strokeWidth = (d.getAttribute('data-planet') === fromPlanet) ? '2.0px' : '0.8px';
            d.style.r = (d.getAttribute('data-planet') === fromPlanet) ? '4.0' : '2.8';
        });
        svg.querySelectorAll('.natal-planet-dot').forEach(d => {
            d.style.strokeWidth = (d.getAttribute('data-planet') === toPlanet) ? '2.0px' : '0.8px';
            d.style.r = (d.getAttribute('data-planet') === toPlanet) ? '4.0' : '2.8';
        });
    }

    function resetTransitAspectHighlights(cell) {
        const svg = cell.querySelector('.transit-biwheel-svg');
        if (!svg) return;

        svg.querySelectorAll('.transit-aspect-line').forEach(l => {
            l.style.opacity = '';
            l.style.strokeWidth = '';
        });
        svg.querySelectorAll('.transit-planet-dot').forEach(d => {
            d.style.strokeWidth = '';
            d.style.r = '';
        });
        svg.querySelectorAll('.natal-planet-dot').forEach(d => {
            d.style.strokeWidth = '';
            d.style.r = '';
        });
    }

    function attachSvgInteractivity(cell) {
        const svg = cell.querySelector('.transit-biwheel-svg');
        if (!svg) return;
        const state = activeInstances.get(cell);
        if (!state) return;

        const outerPlanets = svg.querySelectorAll('.outer-planet, .transit-planet');
        const innerPlanets = svg.querySelectorAll('.inner-planet, .natal-planet');
        const aspectLines = svg.querySelectorAll('.transit-aspect-line');

        // 1. Hover on Outer Transiting Planet -> Highlight outbound aspects
        outerPlanets.forEach(p => {
            const pName = p.getAttribute('data-planet');
            if (!pName) return;

            p.addEventListener('mouseenter', () => {
                let hitCount = 0;
                aspectLines.forEach(line => {
                    if (line.getAttribute('data-from') === pName) {
                        line.style.opacity = '1.0';
                        line.style.strokeWidth = '2.2px';
                        hitCount++;
                    } else {
                        line.style.opacity = '0.12';
                        line.style.strokeWidth = '0.8px';
                    }
                });
            });

            p.addEventListener('mouseleave', () => resetTransitAspectHighlights(cell));
        });

        // 2. Hover on Inner Natal Planet -> Highlight inbound aspects to this target
        innerPlanets.forEach(p => {
            const pName = p.getAttribute('data-planet') || p.getAttribute('data-id');
            if (!pName) return;

            p.addEventListener('mouseenter', () => {
                aspectLines.forEach(line => {
                    if (line.getAttribute('data-to') === pName) {
                        line.style.opacity = '1.0';
                        line.style.strokeWidth = '2.2px';
                    } else {
                        line.style.opacity = '0.12';
                        line.style.strokeWidth = '0.8px';
                    }
                });
            });

            p.addEventListener('mouseleave', () => resetTransitAspectHighlights(cell));
        });

        // 3. Hover directly on Aspect Line
        aspectLines.forEach(line => {
            line.addEventListener('mouseenter', () => {
                aspectLines.forEach(l => {
                    if (l === line) {
                        l.style.opacity = '1.0';
                        l.style.strokeWidth = '2.5px';
                    } else {
                        l.style.opacity = '0.15';
                        l.style.strokeWidth = '0.8px';
                    }
                });
            });
            line.addEventListener('mouseleave', () => resetTransitAspectHighlights(cell));
        });

        // 4. Station Pins on Outer Rim (Click to jump, Hover for feedback)
        const stationPins = svg.querySelectorAll('.station-pin, .interactive-station-pin');
        stationPins.forEach(pin => {
            pin.addEventListener('click', (e) => {
                e.stopPropagation();
                const jDate = pin.getAttribute('data-jump-date');
                const jTime = pin.getAttribute('data-jump-time');
                if (jDate) {
                    jumpToMilestone(state, jDate, jTime || '12:00:00');
                }
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
            if (state.playTimer) clearTimeout(state.playTimer);
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

        const btnSyncNatal = cell.querySelector('.btn-transit-sync-natal');
        const orbSelect = cell.querySelector('.transit-orb-select');

        if (btnStepBack) btnStepBack.onclick = () => stepTime(state, -1, 1);
        if (btnStepFwd) btnStepFwd.onclick = () => stepTime(state, 1, 1);
        if (btnFastBack) btnFastBack.onclick = () => stepTime(state, -1, 5);
        if (btnFastFwd) btnFastFwd.onclick = () => stepTime(state, 1, 5);

        if (btnNow) {
            btnNow.onclick = () => {
                state.currentDate = new Date();
                pulseLiveBadge(cell);
                syncInputsFromState(state);
                fetchAndRender(state);
            };
        }

        if (btnSyncNatal) {
            btnSyncNatal.onclick = () => {
                const subj = (window.currentChartData && window.currentChartData.subject_info) || window.currentLoadedNative;
                if (subj && subj.date) {
                    const parsedDate = parseDateString(subj.date);
                    if (subj.time) {
                        const parts = subj.time.split(':');
                        parsedDate.setHours(parseInt(parts[0], 10) || 12, parseInt(parts[1], 10) || 0, parseInt(parts[2], 10) || 0);
                    }
                    state.currentDate = parsedDate;
                    pulseLiveBadge(cell);
                    syncInputsFromState(state);
                    fetchAndRender(state);
                }
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

        if (orbSelect) {
            orbSelect.value = String(state.orb || 3.3333);
            orbSelect.onchange = () => {
                state.orb = parseFloat(orbSelect.value) || 3.3333;
                fetchAndRender(state);
            };
        }

        const handleDateChange = () => {
            if (dateInput && dateInput.value) {
                const parts = dateInput.value.split('-');
                if (parts.length === 3) {
                    const y = parseInt(parts[0], 10);
                    const m = parseInt(parts[1], 10) - 1;
                    const d = parseInt(parts[2], 10);
                    if (!isNaN(y) && !isNaN(m) && !isNaN(d) && y > 100 && d > 0 && d <= 31) {
                        state.currentDate.setFullYear(y, m, d);
                        pulseLiveBadge(cell);
                        syncInputsFromState(state);
                        fetchAndRender(state);
                    }
                }
            }
        };

        if (dateInput) {
            dateInput.onchange = handleDateChange;
            dateInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') handleDateChange();
            });
        }

        const handleTimeChange = () => {
            if (timeInput && timeInput.value) {
                const parts = timeInput.value.split(':');
                if (parts.length >= 2) {
                    const h = parseInt(parts[0], 10);
                    const m = parseInt(parts[1], 10);
                    const s = parts.length > 2 ? parseInt(parts[2], 10) : 0;
                    if (!isNaN(h) && !isNaN(m)) {
                        state.currentDate.setHours(h, m, isNaN(s) ? 0 : s);
                        pulseLiveBadge(cell);
                        syncInputsFromState(state);
                        fetchAndRender(state);
                    }
                }
            }
        };

        if (timeInput) {
            timeInput.onchange = handleTimeChange;
            timeInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') handleTimeChange();
            });
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

        // Bind Milestone Step and Radar Controls
        const btnMilestonePrev = cell.querySelector('.btn-transit-step-milestone-prev');
        const btnMilestoneNext = cell.querySelector('.btn-transit-step-milestone-next');
        const btnToggleRadar = cell.querySelector('.btn-transit-toggle-radar');
        const radarPanel = cell.querySelector('.transit-radar-panel');

        if (btnMilestonePrev) btnMilestonePrev.onclick = () => stepMilestone(state, -1);
        if (btnMilestoneNext) btnMilestoneNext.onclick = () => stepMilestone(state, 1);

        if (btnToggleRadar && radarPanel) {
            btnToggleRadar.onclick = () => {
                state.showRadar = !state.showRadar;
                radarPanel.style.display = state.showRadar ? 'flex' : 'none';
                if (state.showRadar) {
                    btnToggleRadar.classList.add('active');
                    btnToggleRadar.style.background = '#fff8f0';
                    btnToggleRadar.style.borderColor = '#c2410c';
                    btnToggleRadar.style.color = '#c2410c';
                } else {
                    btnToggleRadar.classList.remove('active');
                    btnToggleRadar.style.background = '#fffdfa';
                    btnToggleRadar.style.borderColor = '#d5c8b2';
                    btnToggleRadar.style.color = '#4a3325';
                }
            };
        }

        const filterTabs = cell.querySelectorAll('.radar-filter-tab, .radar-filter-pill');
        filterTabs.forEach(tab => {
            tab.onclick = () => {
                filterTabs.forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                state.radarFilter = tab.getAttribute('data-filter') || 'all';
                renderMilestones(state);
            };
        });

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
                initTransitWidget(cell);
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

    // Switch from transit widget back to normal chart widget with requested style
    function switchTransitToChart(btn, style) {
        const cell = btn.closest('.grid-cell');
        if (!cell) return;
        const state = activeInstances.get(cell);
        if (state && state.playTimer) {
            clearTimeout(state.playTimer);
            state.playTimer = null;
            state.isPlaying = false;
        }
        if (typeof window.assignWidget === 'function') {
            window.assignWidget('chart', cell, { chart_style: style });
        }
    }

    function maximizeTransitFromWidget(btn) {
        if (typeof openFloatingTransit === 'function') {
            openFloatingTransit();
        }
    }

    // Export globally for testing / manual invocation
    if (typeof window !== 'undefined') {
        window.initTransitWidget = initTransitWidget;
        window.openFloatingTransit = openFloatingTransit;
        window.switchTransitToChart = switchTransitToChart;
        window.maximizeTransitFromWidget = maximizeTransitFromWidget;
    }
})();
