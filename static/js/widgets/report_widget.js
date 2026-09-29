/**
 * Astra Chart Assessment Report Widget (static/js/widgets/report_widget.js)
 * Clean, streamlined implementation matching the notebook assessment structure:
 * 1. Ascendant & Moon Nakshatras Side-by-Side Descriptive Dossiers (No Automated Synthesis)
 * 2. Rising Rāśi ($D_1$) & Rising Navāṁśa ($D_9$) Interactive Flowchart Stage
 * 3. Nakshatra Dominance Leaderboard (Prominence-scaled empirical occupancy)
 * 4. Balance of Nakshatra Types (6-Class Model evaluated against 16.7% baseline)
 * 5. Planet ⟷ Sign ⟷ House Interactive Planetary Synthesis Flowchart Desk
 */

const SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer",
    "Leo", "Virgo", "Libra", "Scorpio",
    "Sagittarius", "Capricorn", "Aquarius", "Pisces"
];

let _cachedSignificationsData = null;

function escapeHtml(str) {
    if (!str) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

async function getSignificationsData(chartData) {
    if (_cachedSignificationsData) return _cachedSignificationsData;
    try {
        const resp = await fetch('/static/data/significations_data.json');
        if (resp.ok) {
            _cachedSignificationsData = await resp.json();
            return _cachedSignificationsData;
        }
    } catch (err) {
        console.warn("Could not fetch /static/data/significations_data.json:", err);
    }
    if (chartData && chartData.report && chartData.report.significations_data && chartData.report.significations_data.planets) {
        _cachedSignificationsData = chartData.report.significations_data;
        return _cachedSignificationsData;
    }
    return { planets: {}, signs: {}, houses: {} };
}

function getPlanetPlacement(chartData, planetName) {
    const vargas = chartData.vargas || {};
    const d1 = vargas.D1 || {};
    const lagnaSign = (d1.lagna && d1.lagna.sign) || 'Aries';
    const lagnaIdx = SIGNS.indexOf(lagnaSign);

    const grahaD1 = (d1.grahas && d1.grahas[planetName]) || {};
    const sign = grahaD1.sign || 'Aries';
    const pIdx = SIGNS.indexOf(sign);
    const house = (lagnaIdx >= 0 && pIdx >= 0) ? (((pIdx - lagnaIdx + 12) % 12) + 1) : 1;

    const nakData = (chartData.nakshatras_grahas && chartData.nakshatras_grahas[planetName]) || {};
    const nakshatra = nakData.nakshatra || grahaD1.nakshatra || '--';
    const nakshatraLord = nakData.nakshatra_lord || grahaD1.nakshatra_lord || '--';
    const pada = nakData.pada || grahaD1.pada || 1;

    return {
        planet: planetName,
        sign,
        house,
        nakshatra,
        nakshatraLord,
        pada
    };
}

// ----------------------------------------------------------------------------
// Section 1: Ascendant & Moon Nakshatra Cards
// ----------------------------------------------------------------------------

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

// ----------------------------------------------------------------------------
// Flowchart Card Rendering Engine (Banners, Notes, Badges, Columns)
// ----------------------------------------------------------------------------

function renderEntityFlowchartCard(targetCol, cardData, entityType, displayTitle, symbol, idPrefix = '', extraHeaderHtml = '') {
    if (!targetCol || !cardData) return;
    targetCol._entityData = cardData;
    targetCol._idPrefix = idPrefix;

    const sym = symbol || cardData.symbol || '';
    const title = displayTitle || cardData.title || cardData.name || '';
    const sanskrit = cardData.sanskrit || '';
    const formula = cardData.formula || '';
    const pinnedNote = cardData.pinned_note || cardData.sticky_note || '';
    const banner = cardData.banner || '';
    const rawCallout = cardData.callout || '';
    const callout = (typeof rawCallout === 'object' && rawCallout.text) ? rawCallout.text : (typeof rawCallout === 'string' ? rawCallout : '');
    const anatomy = cardData.anatomy || '';

    let html = `
        <div class="synth-card-header" style="display: flex; justify-content: space-between; align-items: flex-start; gap: 8px; border-bottom: 1px solid #e2e8f0; padding-bottom: 8px;">
            <div style="display: flex; align-items: center; gap: 8px;">
                ${sym ? `<span class="synth-card-symbol" style="font-family: var(--font-astro-glyphs, serif); font-variant-emoji: text; font-size: 18px;">${escapeHtml(sym)}</span>` : ''}
                <div>
                    <div class="synth-card-title" style="font-size: 14px; font-weight: 700; color: #0f172a;">${escapeHtml(title)}</div>
                    ${sanskrit ? `<div style="font-size: 12px; color: #64748b; font-style: italic;">${escapeHtml(sanskrit)}</div>` : ''}
                </div>
            </div>
            <div style="display: flex; flex-direction: column; align-items: flex-end; gap: 4px;">
                ${extraHeaderHtml || ''}
                ${formula ? `<span class="synth-card-formula" style="font-size: 12px; color: #475569; font-style: italic; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 4px; padding: 2px 6px;" title="${escapeHtml(formula)}">${escapeHtml(formula)}</span>` : ''}
            </div>
        </div>
    `;

    if (pinnedNote) {
        html += `
            <div class="synth-pinned-note" style="background: #fffbeb; border: 1px solid #fef3c7; border-left: 3px solid #f59e0b; padding: 6px 10px; border-radius: 4px; font-size: 12px; color: #92400e; display: flex; gap: 6px;">
                <span>${escapeHtml(pinnedNote)}</span>
            </div>
        `;
    }

    if (banner) {
        html += `<div class="synth-banner-header" style="background: #f1f5f9; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: 700; color: #475569; text-transform: uppercase; letter-spacing: 0.5px; text-align: center;">${escapeHtml(banner)}</div>`;
    }

    html += `<div class="synth-pillars-container" style="display: flex; gap: 10px; justify-content: space-between;">`;

    const cols = cardData.columns || cardData.pillars || cardData.subgraphs || [];
    const genericColNames = ['left', 'center', 'right', 'main', 'col', 'column', 'default'];
    cols.forEach(col => {
        const rawColName = (col.name || '').trim();
        const hasDedicatedSubheader = rawColName && !genericColNames.includes(rawColName.toLowerCase());
        html += `
            <div class="synth-pillar-col" style="flex: 1; display: flex; flex-direction: column; gap: 10px;">
                ${hasDedicatedSubheader ? `<div class="synth-pillar-title" style="font-size: 12px; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.4px; border-bottom: 1px dashed #cbd5e1; padding-bottom: 2px;" title="${escapeHtml(rawColName)}">${escapeHtml(rawColName)}</div>` : ''}
                <div class="synth-node-list" style="display: flex; flex-direction: column; gap: 18px;">
        `;
        const nodes = col.nodes || col.items || [];
        nodes.forEach(item => {
            const badge = item.badge || '';
            const colorClass = item.color ? `color-${item.color}` : '';
            const circledClass = badge === 'Circled' ? 'badge-circled' : '';
            const nodeId = `${idPrefix}${item.id}`;

            html += `
                <div class="synth-node-box ${colorClass} ${circledClass}" data-node-id="${escapeHtml(nodeId)}" data-node-title="${escapeHtml(item.title)}" data-node-sub="${escapeHtml(item.sub || '')}" data-node-group="${escapeHtml(displayTitle || cardData.title || cardData.name || entityType)}" style="cursor: pointer; user-select: none;">
                    ${badge && badge !== 'Circled' ? `<span class="synth-node-badge">${escapeHtml(badge)}</span>` : ''}
                    <div class="synth-node-title" style="font-size: 12px; font-weight: 700;">${escapeHtml(item.title)}</div>
                    ${item.sub ? `<div class="synth-node-sub" style="font-size: 12px; color: #64748b;">${escapeHtml(item.sub)}</div>` : ''}
                </div>
            `;
        });
        html += `
                </div>
            </div>
        `;
    });

    html += `</div>`;

    if (callout) {
        html += `
            <div class="synth-callout-bubble" style="background: #f8fafc; border: 1px dashed #cbd5e1; padding: 6px 10px; border-radius: 4px; font-size: 12px; color: #334155;">
                ${escapeHtml(callout)}
            </div>
        `;
    }

    if (anatomy) {
        html += `
            <div class="synth-anatomy-footer" style="border-top: 1px solid #f1f5f9; padding-top: 6px; font-size: 12px; color: #64748b;">
                <strong>Kalapurusha Anatomy:</strong> ${escapeHtml(anatomy)}
            </div>
        `;
    }

    targetCol.innerHTML = html;
}

const renderPillarCard = renderEntityFlowchartCard;

// ----------------------------------------------------------------------------
// Perimeter Docking Coordinates & Internal Base Tree Flow Math
// ----------------------------------------------------------------------------

function getNodeDockPoint(nodeRect, stageRect, dockSide) {
    switch (dockSide) {
        case 'top':
            return {
                x: nodeRect.left + nodeRect.width / 2 - stageRect.left,
                y: nodeRect.top - stageRect.top
            };
        case 'bottom':
            return {
                x: nodeRect.left + nodeRect.width / 2 - stageRect.left,
                y: nodeRect.bottom - stageRect.top
            };
        case 'left':
            return {
                x: nodeRect.left - stageRect.left,
                y: nodeRect.top + nodeRect.height / 2 - stageRect.top
            };
        case 'right':
        default:
            return {
                x: nodeRect.right - stageRect.left,
                y: nodeRect.top + nodeRect.height / 2 - stageRect.top
            };
    }
}

function drawBaseInternalArrows(cardElement, entityData, baseGroup, stageRect, idPrefix = '', markerBase = 'url(#arrow-base-slate)', markerLoop = 'url(#arrow-base-loop)') {
    if (!cardElement || !entityData || !baseGroup || !stageRect) return;
    const edges = entityData.edges || [];
    if (!edges.length) return;

    edges.forEach(edge => {
        const fromId = `${idPrefix}${edge.from}`;
        const toId = `${idPrefix}${edge.to}`;
        const fromEl = cardElement.querySelector(`.synth-node-box[data-node-id="${fromId}"]`);
        const toEl = cardElement.querySelector(`.synth-node-box[data-node-id="${toId}"]`);
        if (!fromEl || !toEl) return;

        const r1 = fromEl.getBoundingClientRect();
        const r2 = toEl.getBoundingClientRect();
        if (r1.width === 0 || r2.width === 0) return;

        let d = '';
        let strokeColor = '#94a3b8';
        let strokeWidth = '1.5';
        let strokeDash = '';
        let markerUrl = markerBase;

        // Feedback loop
        if (edge.type === 'dashed_loop' || edge.style === 'dashed_loop') {
            const p1 = getNodeDockPoint(r1, stageRect, 'left');
            const p2 = getNodeDockPoint(r2, stageRect, 'left');
            const loopX = Math.min(p1.x, p2.x) - 22;
            d = `M ${p1.x} ${p1.y} C ${loopX} ${p1.y}, ${loopX} ${p2.y}, ${p2.x} ${p2.y}`;
            strokeColor = '#ea580c';
            strokeDash = '4 3';
            markerUrl = markerLoop;
        } else if (r1.bottom <= r2.top + 6) {
            // Vertical descent
            const p1 = getNodeDockPoint(r1, stageRect, 'bottom');
            const p2 = getNodeDockPoint(r2, stageRect, 'top');
            const dy = Math.max(14, (p2.y - p1.y) * 0.5);
            d = `M ${p1.x} ${p1.y} C ${p1.x} ${p1.y + dy}, ${p2.x} ${p2.y - dy}, ${p2.x} ${p2.y}`;
        } else if (r1.right < r2.left) {
            // Side branch: left to right
            const p1 = getNodeDockPoint(r1, stageRect, 'right');
            const p2 = getNodeDockPoint(r2, stageRect, 'left');
            const dx = Math.max(14, (p2.x - p1.x) * 0.5);
            d = `M ${p1.x} ${p1.y} C ${p1.x + dx} ${p1.y}, ${p2.x - dx} ${p2.y}, ${p2.x} ${p2.y}`;
        } else {
            // Side branch: right to left
            const p1 = getNodeDockPoint(r1, stageRect, 'left');
            const p2 = getNodeDockPoint(r2, stageRect, 'right');
            const dx = Math.max(14, (p1.x - p2.x) * 0.5);
            d = `M ${p1.x} ${p1.y} C ${p1.x - dx} ${p1.y}, ${p2.x + dx} ${p2.y}, ${p2.x} ${p2.y}`;
        }

        const pathEl = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        pathEl.setAttribute('d', d);
        pathEl.setAttribute('fill', 'none');
        pathEl.setAttribute('stroke', strokeColor);
        pathEl.setAttribute('stroke-width', strokeWidth);
        if (strokeDash) {
            pathEl.setAttribute('stroke-dasharray', strokeDash);
        }
        pathEl.setAttribute('marker-end', markerUrl);
        pathEl.setAttribute('data-from', fromId);
        pathEl.setAttribute('data-to', toId);
        baseGroup.appendChild(pathEl);
    });
}

// ----------------------------------------------------------------------------
// SVG Connector Overlay: Bézier Curve Math & Path Rendering
// ----------------------------------------------------------------------------

function redrawStageConnections(stageWrapper, baseGroup, userGroup, cardConfigs, links, markerHarmonic = 'url(#arrow-harmonic)', markerDissonant = 'url(#arrow-dissonant)') {
    if (!stageWrapper || !userGroup) return;

    const stageRect = stageWrapper.getBoundingClientRect();
    if (stageRect.width === 0 || stageRect.height === 0) return;

    // 1. Draw base internal arrows inside each card
    if (baseGroup) {
        baseGroup.innerHTML = '';
        (cardConfigs || []).forEach(cfg => {
            const cardEl = cfg.cardEl;
            if (cardEl && cardEl._entityData) {
                drawBaseInternalArrows(
                    cardEl, 
                    cardEl._entityData, 
                    baseGroup, 
                    stageRect, 
                    cardEl._idPrefix || cfg.idPrefix || '',
                    cfg.markerBase || 'url(#arrow-base-slate)',
                    cfg.markerLoop || 'url(#arrow-base-loop)'
                );
            }
        });
    }

    // 2. Draw user cross-connections
    userGroup.innerHTML = '';
    if (!links || links.length === 0) return;

    links.forEach(link => {
        const fromEl = stageWrapper.querySelector(`.synth-node-box[data-node-id="${link.from}"]`);
        const toEl = stageWrapper.querySelector(`.synth-node-box[data-node-id="${link.to}"]`);
        if (!fromEl || !toEl) return;

        const r1 = fromEl.getBoundingClientRect();
        const r2 = toEl.getBoundingClientRect();
        if (r1.width === 0 || r2.width === 0) return;

        let p1, p2, d;
        const isDissonance = link.type === 'dissonance';
        const strokeColor = isDissonance ? '#b91c1c' : '#15803d';
        const markerUrl = isDissonance ? markerDissonant : markerHarmonic;

        // Docking logic: outer perimeter docking with zero text occlusion
        if (Math.abs(r1.left - r2.left) < 40) {
            // Vertically aligned / same column: loop out to the right gutter
            p1 = getNodeDockPoint(r1, stageRect, 'right');
            p2 = getNodeDockPoint(r2, stageRect, 'right');
            const loopX = Math.max(p1.x, p2.x) + 36;
            d = `M ${p1.x} ${p1.y} C ${loopX} ${p1.y}, ${loopX} ${p2.y}, ${p2.x} ${p2.y}`;
        } else if (r1.right + 20 < r2.left) {
            // Source is to the left: dock right edge of source to left edge of target
            p1 = getNodeDockPoint(r1, stageRect, 'right');
            p2 = getNodeDockPoint(r2, stageRect, 'left');
            const dx = Math.max(35, (p2.x - p1.x) * 0.45);
            d = `M ${p1.x} ${p1.y} C ${p1.x + dx} ${p1.y}, ${p2.x - dx} ${p2.y}, ${p2.x} ${p2.y}`;
        } else if (r2.right + 20 < r1.left) {
            // Source is to the right: dock left edge of source to right edge of target
            p1 = getNodeDockPoint(r1, stageRect, 'left');
            p2 = getNodeDockPoint(r2, stageRect, 'right');
            const dx = Math.max(35, (p1.x - p2.x) * 0.45);
            d = `M ${p1.x} ${p1.y} C ${p1.x - dx} ${p1.y}, ${p2.x + dx} ${p2.y}, ${p2.x} ${p2.y}`;
        } else {
            p1 = getNodeDockPoint(r1, stageRect, 'right');
            p2 = getNodeDockPoint(r2, stageRect, 'left');
            const dx = Math.max(25, Math.abs(p2.x - p1.x) * 0.5);
            d = `M ${p1.x} ${p1.y} C ${p1.x + dx} ${p1.y}, ${p2.x - dx} ${p2.y}, ${p2.x} ${p2.y}`;
        }

        // Layer 1 halo (white under-path for maximum contrast and zero text clash)
        const haloEl = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        haloEl.setAttribute('d', d);
        haloEl.setAttribute('fill', 'none');
        haloEl.setAttribute('stroke', '#ffffff');
        haloEl.setAttribute('stroke-width', '5.5');
        haloEl.setAttribute('stroke-linecap', 'round');
        haloEl.setAttribute('opacity', '0.9');
        userGroup.appendChild(haloEl);

        // Layer 2 core vector connector
        const pathEl = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        pathEl.setAttribute('d', d);
        pathEl.setAttribute('fill', 'none');
        pathEl.setAttribute('stroke', strokeColor);
        pathEl.setAttribute('stroke-width', '2.5');
        if (isDissonance) {
            pathEl.setAttribute('stroke-dasharray', '6 4');
        }
        pathEl.setAttribute('marker-end', markerUrl);
        pathEl.setAttribute('data-from', link.from);
        pathEl.setAttribute('data-to', link.to);
        userGroup.appendChild(pathEl);
    });
}

function renderStageChipsList(listEl, links, onRemove) {
    if (!listEl) return;
    if (!links || links.length === 0) {
        listEl.innerHTML = `<span class="no-links-msg" style="font-size: 12px; color: #94a3b8; font-style: italic;">No cross-symbol links created yet. Click any two boxes across the cards to link them.</span>`;
        return;
    }

    let html = '';
    links.forEach((l, idx) => {
        const isDis = l.type === 'dissonance';
        const typeLabel = isDis ? 'Dissonant' : 'Harmonic';
        html += `
            <div class="synth-conn-chip ${escapeHtml(l.type)}" data-idx="${idx}">
                <span><strong>${escapeHtml(l.fromLabel || l.from)}</strong> ⟷ <strong>${escapeHtml(l.toLabel || l.to)}</strong> (${typeLabel})</span>
                <button type="button" class="btn-del-conn" data-idx="${idx}" title="Remove link">×</button>
            </div>
        `;
    });
    listEl.innerHTML = html;

    listEl.querySelectorAll('.btn-del-conn').forEach(btn => {
        btn.onclick = (e) => {
            e.stopPropagation();
            const idx = parseInt(btn.getAttribute('data-idx'), 10);
            if (!isNaN(idx) && onRemove) {
                onRemove(idx);
            }
        };
    });
}

// ----------------------------------------------------------------------------
// Interactive Stage Selection Engine & Shared Floating Action Bar
// ----------------------------------------------------------------------------

let _globalActiveStageSelection = null;
let _globalActionBarWired = false;

function getGlobalActionBar() {
    let actionBar = document.getElementById('synth-action-bar');
    if (!actionBar) {
        actionBar = document.createElement('div');
        actionBar.id = 'synth-action-bar';
        actionBar.className = 'synth-action-bar';
        actionBar.style.cssText = 'display: none; position: fixed; bottom: 24px; left: 50%; transform: translateX(-50%); background: #0f172a; color: #ffffff; border-radius: 30px; padding: 8px 18px; box-shadow: 0 8px 24px rgba(0,0,0,0.35); z-index: 999999; align-items: center; gap: 12px;';
        actionBar.innerHTML = `
            <span id="synth-selection-label" class="synth-selection-label" style="font-size: 12.5px; font-weight: 600;"></span>
            <button type="button" id="btn-action-res" class="btn-action-res" style="background: #15803d; color: #ffffff; border: none; border-radius: 16px; padding: 6px 14px; font-size: 12px; font-weight: 700; cursor: pointer; transition: background 0.15s ease;">+ Resonates (Harmonic)</button>
            <button type="button" id="btn-action-dis" class="btn-action-dis" style="background: #b91c1c; color: #ffffff; border: none; border-radius: 16px; padding: 6px 14px; font-size: 12px; font-weight: 700; cursor: pointer; transition: background 0.15s ease;">− Clashes (Dissonant)</button>
            <button type="button" id="btn-action-cancel" class="btn-action-cancel" style="background: transparent; color: #94a3b8; border: none; font-size: 14px; cursor: pointer; padding: 0 4px;" title="Cancel selection">✕</button>
        `;
        document.body.appendChild(actionBar);
    } else if (actionBar.parentElement !== document.body) {
        document.body.appendChild(actionBar);
    }
    const selLabel = actionBar.querySelector('.synth-selection-label, #synth-selection-label');
    return { actionBar, selLabel };
}

function clearGlobalSelection() {
    if (_globalActiveStageSelection) {
        if (_globalActiveStageSelection.stageWrapper) {
            _globalActiveStageSelection.stageWrapper.querySelectorAll('.synth-node-box').forEach(b => {
                b.classList.remove('selected-first', 'selected-second');
            });
        }
        if (_globalActiveStageSelection.actionBar) {
            _globalActiveStageSelection.actionBar.style.display = 'none';
        }
        _globalActiveStageSelection = null;
    }
    const { actionBar } = getGlobalActionBar();
    if (actionBar) actionBar.style.display = 'none';
}

function ensureActionBarWired() {
    if (_globalActionBarWired) return;
    _globalActionBarWired = true;

    // Ensure the action bar exists in document.body
    getGlobalActionBar();

    document.addEventListener('click', (e) => {
        const btnRes = e.target.closest('.btn-action-res, #btn-action-res');
        const btnDis = e.target.closest('.btn-action-dis, #btn-action-dis');
        const btnCancel = e.target.closest('.btn-action-cancel, #btn-action-cancel');

        if (btnRes) {
            e.preventDefault();
            e.stopPropagation();
            if (_globalActiveStageSelection && _globalActiveStageSelection.commitLink) {
                _globalActiveStageSelection.commitLink('resonance');
            }
        } else if (btnDis) {
            e.preventDefault();
            e.stopPropagation();
            if (_globalActiveStageSelection && _globalActiveStageSelection.commitLink) {
                _globalActiveStageSelection.commitLink('dissonance');
            }
        } else if (btnCancel) {
            e.preventDefault();
            e.stopPropagation();
            clearGlobalSelection();
        }
    });
}

function setupInteractiveStageSelection({
    stageId,
    stageWrapper,
    chipsListEl,
    clearBtnEl,
    getLinks,
    saveLinks,
    redrawFn,
    onLinkAdded
}) {
    if (!stageWrapper) return;

    let selectedBoxes = [];

    const updateVisuals = () => {
        const allBoxes = stageWrapper.querySelectorAll('.synth-node-box');
        allBoxes.forEach(b => b.classList.remove('selected-first', 'selected-second'));

        if (selectedBoxes[0] && selectedBoxes[0].el) {
            selectedBoxes[0].el.classList.add('selected-first');
        }
        if (selectedBoxes[1] && selectedBoxes[1].el) {
            selectedBoxes[1].el.classList.add('selected-second');
        }

        const { actionBar, selLabel } = getGlobalActionBar();
        if (actionBar && selLabel) {
            if (selectedBoxes.length === 2) {
                selLabel.textContent = `${selectedBoxes[0].group}: ${selectedBoxes[0].title} ⟷ ${selectedBoxes[1].group}: ${selectedBoxes[1].title}`;
                actionBar.style.display = 'flex';
                _globalActiveStageSelection = {
                    stageId,
                    stageWrapper,
                    actionBar,
                    selectedBoxes,
                    commitLink,
                    clearSelection: () => {
                        selectedBoxes = [];
                        updateVisuals();
                    }
                };
            } else if (selectedBoxes.length === 0 && _globalActiveStageSelection && _globalActiveStageSelection.stageId === stageId) {
                actionBar.style.display = 'none';
                _globalActiveStageSelection = null;
            }
        }
    };

    const attachClicks = () => {
        const boxes = stageWrapper.querySelectorAll('.synth-node-box');
        boxes.forEach(box => {
            box.onclick = (e) => {
                e.stopPropagation();
                if (_globalActiveStageSelection && _globalActiveStageSelection.stageId !== stageId) {
                    clearGlobalSelection();
                }

                const id = box.getAttribute('data-node-id');
                const title = box.getAttribute('data-node-title');
                const sub = box.getAttribute('data-node-sub');
                const group = box.getAttribute('data-node-group');

                const existingIdx = selectedBoxes.findIndex(b => b.id === id);
                if (existingIdx >= 0) {
                    selectedBoxes.splice(existingIdx, 1);
                } else {
                    if (selectedBoxes.length >= 2) {
                        selectedBoxes = [{ id, title, sub, group, el: box }];
                    } else {
                        selectedBoxes.push({ id, title, sub, group, el: box });
                    }
                }
                updateVisuals();
            };
        });
    };

    const onRemoveLink = (idx) => {
        let links = getLinks();
        links.splice(idx, 1);
        saveLinks(links);
        renderStageChipsList(chipsListEl, links, onRemoveLink);
        redrawFn();
    };

    const commitLink = (type) => {
        if (selectedBoxes.length < 2) return;
        const b1 = selectedBoxes[0];
        const b2 = selectedBoxes[1];
        const fromLabel = `${b1.group}: ${b1.title}`;
        const toLabel = `${b2.group}: ${b2.title}`;

        let links = getLinks();
        const existingIdx = links.findIndex(l => (l.from === b1.id && l.to === b2.id) || (l.from === b2.id && l.to === b1.id));
        if (existingIdx >= 0) {
            links[existingIdx].type = type;
            links[existingIdx].fromLabel = fromLabel;
            links[existingIdx].toLabel = toLabel;
        } else {
            links.push({
                from: b1.id,
                to: b2.id,
                fromLabel: fromLabel,
                toLabel: toLabel,
                type: type
            });
        }
        saveLinks(links);

        if (onLinkAdded) {
            onLinkAdded(type, b1, b2, fromLabel, toLabel);
        }

        selectedBoxes = [];
        updateVisuals();
        renderStageChipsList(chipsListEl, links, onRemoveLink);
        redrawFn();
    };

    if (clearBtnEl) {
        clearBtnEl.onclick = (e) => {
            e.preventDefault();
            saveLinks([]);
            selectedBoxes = [];
            updateVisuals();
            renderStageChipsList(chipsListEl, [], onRemoveLink);
            redrawFn();
        };
    }

    attachClicks();
    updateVisuals();

    const currentLinks = getLinks();
    renderStageChipsList(chipsListEl, currentLinks, onRemoveLink);
    setTimeout(() => { redrawFn(); }, 60);
}

// ----------------------------------------------------------------------------
// Section 3: Nakshatra Dominance Leaderboard
// ----------------------------------------------------------------------------

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

// ----------------------------------------------------------------------------
// Section 4: Balance of Nakshatra Types (6-Class Model)
// ----------------------------------------------------------------------------

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
                <td style="padding:10px; min-width:160px;">
                    <div style="font-weight:700; color:#0f172a; font-size:13px;">${escapeHtml(item.display_name)}</div>
                    <div style="font-size:12px; color:#64748b;">${escapeHtml(item.sanskrit)}</div>
                </td>
                <td style="padding:10px; color:#334155; font-size:12.5px; min-width:200px;">
                    ${escapeHtml(item.nature || '--')}
                </td>
                <td style="padding:10px; min-width:180px;">
                    <div style="display:flex; align-items:center; gap:10px;">
                        <div style="position:relative; flex:1; height:12px; background:#e2e8f0; border-radius:6px; overflow:hidden;" title="16.7% Baseline Indicator">
                            <div style="width:${barWidth}%; height:100%; background:${barColor}; border-radius:6px; transition:width 0.3s ease;"></div>
                            <div style="position:absolute; left:16.7%; top:0; bottom:0; width:2px; background:#0f172a; z-index:2;" title="Uniform Baseline: 16.7%"></div>
                        </div>
                        <span style="font-size:12.5px; font-weight:700; color:#0f172a; font-variant-numeric:tabular-nums; min-width:44px; text-align:right;">
                            ${pct.toFixed(1)}%
                        </span>
                    </div>
                </td>
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

// ----------------------------------------------------------------------------
// Section 5: Planet ⟷ Sign ⟷ House Interactive Planetary Synthesis Desk
// ----------------------------------------------------------------------------

async function renderSynthesisCockpit(container, planetName, chartData) {
    const cockpitContainer = container.querySelector('.synthesis-cockpit-container');
    if (!cockpitContainer) return;

    const currentData = chartData || window.currentChartData;
    if (!currentData) return;

    const pl = getPlanetPlacement(currentData, planetName);

    // 1. Placement flavor strip
    const focusText = cockpitContainer.querySelector('.context-focus-text');
    if (focusText) {
        focusText.innerHTML = `<strong>${escapeHtml(planetName)}</strong> in <strong>${escapeHtml(pl.sign)}</strong> (House ${pl.house}) • <em>${escapeHtml(pl.nakshatra)}</em> (Lord: ${escapeHtml(pl.nakshatraLord)})`;
    }

    // 2. Setup Scratchpad Notes Persistence
    const nativeId = (currentData.subject_info && currentData.subject_info.name)
        ? currentData.subject_info.name.replace(/[^a-zA-Z0-9_-]/g, '_')
        : (currentData.id || 'default_chart');
    const noteKey = `astra_synth_notes_${nativeId}_${planetName}`;
    const txtResonance = cockpitContainer.querySelector('#txt-resonance') || cockpitContainer.querySelector('.txt-resonance');
    const txtDissonance = cockpitContainer.querySelector('#txt-dissonance') || cockpitContainer.querySelector('.txt-dissonance');
    const txtSynthesis = cockpitContainer.querySelector('#txt-synthesis') || cockpitContainer.querySelector('.txt-synthesis');
    const btnSave = cockpitContainer.querySelector('.btn-save-synthesis');
    const saveStatus = cockpitContainer.querySelector('.synth-save-status');

    const saveNotes = () => {
        const payload = {
            resonance: txtResonance ? txtResonance.value : '',
            dissonance: txtDissonance ? txtDissonance.value : '',
            synthesis: txtSynthesis ? txtSynthesis.value : '',
            updatedAt: new Date().toISOString()
        };
        try {
            localStorage.setItem(noteKey, JSON.stringify(payload));
            if (saveStatus) {
                saveStatus.textContent = 'Saved to local cache ✓';
                saveStatus.style.opacity = '1';
                setTimeout(() => { if (saveStatus) saveStatus.style.opacity = '0'; }, 2000);
            }
        } catch (e) {
            console.error("Error writing notes to localStorage:", e);
        }
    };

    if (btnSave) {
        btnSave.onclick = (e) => {
            e.preventDefault();
            saveNotes();
        };
    }

    let debounceTimer = null;
    const triggerAutoSave = () => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(saveNotes, 600);
    };

    if (txtResonance) txtResonance.oninput = triggerAutoSave;
    if (txtDissonance) txtDissonance.oninput = triggerAutoSave;
    if (txtSynthesis) txtSynthesis.oninput = triggerAutoSave;

    try {
        const rawNote = localStorage.getItem(noteKey);
        if (rawNote) {
            const parsed = JSON.parse(rawNote);
            if (txtResonance) txtResonance.value = parsed.resonance || '';
            if (txtDissonance) txtDissonance.value = parsed.dissonance || '';
            if (txtSynthesis) txtSynthesis.value = parsed.synthesis || '';
        } else {
            if (txtResonance) txtResonance.value = '';
            if (txtDissonance) txtDissonance.value = '';
            if (txtSynthesis) txtSynthesis.value = '';
        }
    } catch (e) {
        console.warn("Could not read notes from localStorage:", e);
    }

    // 3. Load Significations Data
    const data = await getSignificationsData(currentData);
    const pData = (data.planets && data.planets[planetName]) || {};
    const sData = (data.signs && data.signs[pl.sign]) || {};
    const hData = (data.houses && data.houses[String(pl.house)]) || {};

    // 4. Render Fixed HTML/CSS Flowchart Cards
    const cardColPlanet = cockpitContainer.querySelector('#card-col-planet');
    const cardColSign = cockpitContainer.querySelector('#card-col-sign');
    const cardColHouse = cockpitContainer.querySelector('#card-col-house');

    if (cardColPlanet) {
        renderEntityFlowchartCard(cardColPlanet, pData, 'planet', pData.title || `Planet: ${planetName}`, pData.symbol || '');
    }
    if (cardColSign) {
        renderEntityFlowchartCard(cardColSign, sData, 'sign', sData.title || `Sign: ${pl.sign}`, sData.symbol || '♈');
    }
    if (cardColHouse) {
        renderEntityFlowchartCard(cardColHouse, hData, 'house', hData.title || `House ${pl.house}`, hData.symbol || '⌂');
    }

    // 5. Setup Stage Connections & Interactive Selection
    const stageWrapper = cockpitContainer.querySelector('#synth-stage-wrapper');
    const baseGroup = cockpitContainer.querySelector('#synth-base-arrows-group');
    const userGroup = cockpitContainer.querySelector('#synth-user-arrows-group');
    const chipsListEl = cockpitContainer.querySelector('#cockpit-connections-list');
    const clearBtnEl = cockpitContainer.querySelector('#btn-clear-connections');

    const linksKey = `astra_synth_links_${nativeId}_${planetName}`;
    const getLinks = () => {
        try {
            const raw = localStorage.getItem(linksKey);
            return raw ? JSON.parse(raw) : [];
        } catch (e) {
            return [];
        }
    };
    const saveLinks = (links) => {
        try {
            localStorage.setItem(linksKey, JSON.stringify(links));
        } catch (e) {
            console.error("Error saving links:", e);
        }
    };

    const cardConfigs = [
        { cardEl: cardColPlanet, markerBase: 'url(#arrow-base-slate)', markerLoop: 'url(#arrow-base-loop)' },
        { cardEl: cardColSign, markerBase: 'url(#arrow-base-slate)', markerLoop: 'url(#arrow-base-loop)' },
        { cardEl: cardColHouse, markerBase: 'url(#arrow-base-slate)', markerLoop: 'url(#arrow-base-loop)' }
    ];

    const redrawFn = () => {
        const links = getLinks();
        redrawStageConnections(stageWrapper, baseGroup, userGroup, cardConfigs, links, 'url(#arrow-harmonic)', 'url(#arrow-dissonant)');
    };

    const onLinkAdded = (type, b1, b2, fromLabel, toLabel) => {
        if (type === 'resonance' && txtResonance) {
            const bullet = `• Harmonic: ${fromLabel} resonates with ${toLabel}`;
            if (!txtResonance.value.includes(b1.title) || !txtResonance.value.includes(b2.title)) {
                txtResonance.value = txtResonance.value ? `${txtResonance.value.trim()}\n${bullet}: ` : `${bullet}: `;
                triggerAutoSave();
            }
        } else if (type === 'dissonance' && txtDissonance) {
            const bullet = `• Dissonant: ${fromLabel} clashes with ${toLabel}`;
            if (!txtDissonance.value.includes(b1.title) || !txtDissonance.value.includes(b2.title)) {
                txtDissonance.value = txtDissonance.value ? `${txtDissonance.value.trim()}\n${bullet}: ` : `${bullet}: `;
                triggerAutoSave();
            }
        }
    };

    setupInteractiveStageSelection({
        stageId: `synth_${planetName}`,
        stageWrapper,
        chipsListEl,
        clearBtnEl,
        getLinks,
        saveLinks,
        redrawFn,
        onLinkAdded
    });

    if (stageWrapper && window.ResizeObserver) {
        if (cockpitContainer._synthResizeObserver) {
            cockpitContainer._synthResizeObserver.disconnect();
        }
        cockpitContainer._synthResizeObserver = new ResizeObserver(() => {
            redrawFn();
        });
        cockpitContainer._synthResizeObserver.observe(stageWrapper);
    }
}

async function initSynthesisCockpit(container, chartData) {
    const cockpitContainer = container.querySelector('.synthesis-cockpit-container');
    if (!cockpitContainer) return;

    const selectPlanet = cockpitContainer.querySelector('#select-focus-planet') || cockpitContainer.querySelector('.select-focus-planet');
    if (!selectPlanet) return;

    const currentData = chartData || window.currentChartData;
    if (!currentData) return;

    const classicalPlanets = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn'];
    const currentVal = selectPlanet.value;
    const initialPlanet = (currentVal && classicalPlanets.includes(currentVal)) ? currentVal : 'Sun';

    // Populate dropdown
    let optionsHtml = '';
    classicalPlanets.forEach(p => {
        const pl = getPlanetPlacement(currentData, p);
        const isSel = p === initialPlanet ? 'selected' : '';
        optionsHtml += `<option value="${p}" ${isSel}>${p} in ${pl.sign} (House ${pl.house}) — ${pl.nakshatra}</option>`;
    });
    selectPlanet.innerHTML = optionsHtml;
    selectPlanet.value = initialPlanet;

    selectPlanet.onchange = () => {
        clearGlobalSelection();
        renderSynthesisCockpit(container, selectPlanet.value, currentData);
    };

    await renderSynthesisCockpit(container, initialPlanet, currentData);
}

// ----------------------------------------------------------------------------
// Master Report Orchestration
// ----------------------------------------------------------------------------

async function updateReportWidget(container, chartData) {
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
    const risingSigns = report.rising_signs || {};
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

    // 2. Section 2: Rising Rāśi & Rising Navāṁśa Flowchart Stage
    const rashiCol = container.querySelector('#card-col-rashi');
    const navamshaCol = container.querySelector('#card-col-navamsha');
    const risingWrapper = container.querySelector('#rising-stage-wrapper');
    const vargBadge = container.querySelector('.vargottama-header-badge');

    if (vargBadge) {
        if (risingSigns.is_vargottama) {
            vargBadge.innerHTML = `<span class="micro-tag" style="font-size:12px; font-weight:700; padding:3px 8px; border-radius:4px; background:#fef3c7; color:#92400e; border:1px solid #f59e0b; display:inline-block;" title="${escapeHtml(risingSigns.vargottama_note || '')}">★ Vargottama Lagna</span>`;
            vargBadge.style.display = 'block';
        } else {
            vargBadge.style.display = 'none';
        }
    }

    if (rashiCol && navamshaCol && risingWrapper && risingSigns.rashi && risingSigns.navamsha) {
        const sigData = await getSignificationsData(currentData);
        const rashiDossier = risingSigns.rashi;
        const navamshaDossier = risingSigns.navamsha;

        const rashiSignData = (sigData.signs && sigData.signs[rashiDossier.sign]) || {};
        const navamshaSignData = (sigData.signs && sigData.signs[navamshaDossier.sign]) || {};

        // Merge backend dossier with client JSON
        const rashiCardData = Object.assign({}, rashiSignData, rashiDossier);
        const navamshaCardData = Object.assign({}, navamshaSignData, navamshaDossier);

        const isVarg = Boolean(risingSigns.is_vargottama);
        const extraHeaderD1 = `
            <div style="display: flex; gap: 4px; align-items: center; flex-wrap: wrap;">
                <span style="font-size: 12px; font-weight: 700; padding: 2px 6px; border-radius: 4px; background: #f0f9ff; color: #0284c7; border: 1px solid #bae6fd;">D1 Tree</span>
                ${isVarg ? `<span class="micro-tag" style="font-size: 12px; font-weight: 700; padding: 2px 6px; border-radius: 4px; background: #fef3c7; color: #92400e; border: 1px solid #f59e0b;">★ Vargottama</span>` : ''}
                <span style="font-size: 12px; font-weight: 700; padding: 2px 6px; border-radius: 4px; background: #f8fafc; color: #0f172a; border: 1px solid #e2e8f0; font-variant-numeric: tabular-nums;">${escapeHtml(rashiDossier.degree_formatted || '')}</span>
            </div>
        `;
        const extraHeaderD9 = `
            <div style="display: flex; gap: 4px; align-items: center; flex-wrap: wrap;">
                <span style="font-size: 12px; font-weight: 700; padding: 2px 6px; border-radius: 4px; background: #f5f3ff; color: #7c3aed; border: 1px solid #ddd6fe;">D9 Fruit</span>
                ${isVarg ? `<span class="micro-tag" style="font-size: 12px; font-weight: 700; padding: 2px 6px; border-radius: 4px; background: #fef3c7; color: #92400e; border: 1px solid #f59e0b;">★ Vargottama</span>` : ''}
                <span style="font-size: 12px; font-weight: 700; padding: 2px 6px; border-radius: 4px; background: #f8fafc; color: #0f172a; border: 1px solid #e2e8f0; font-variant-numeric: tabular-nums;">${escapeHtml(navamshaDossier.degree_formatted || '')}</span>
            </div>
        `;

        renderEntityFlowchartCard(rashiCol, rashiCardData, 'sign', `D1: ${rashiDossier.sign}`, rashiDossier.symbol || '', 'd1_', extraHeaderD1);
        renderEntityFlowchartCard(navamshaCol, navamshaCardData, 'sign', `D9: ${navamshaDossier.sign}`, navamshaDossier.symbol || '', 'd9_', extraHeaderD9);

        const nativeId = (currentData.subject_info && currentData.subject_info.name)
            ? currentData.subject_info.name.replace(/[^a-zA-Z0-9_-]/g, '_')
            : (currentData.id || 'default_chart');
        const risingLinksKey = `astra_rising_links_${nativeId}`;

        const getRisingLinks = () => {
            try {
                const raw = localStorage.getItem(risingLinksKey);
                return raw ? JSON.parse(raw) : [];
            } catch (e) {
                return [];
            }
        };
        const saveRisingLinks = (links) => {
            try {
                localStorage.setItem(risingLinksKey, JSON.stringify(links));
            } catch (e) {
                console.error("Error saving rising links:", e);
            }
        };

        const risingBaseGroup = container.querySelector('#rising-base-arrows-group');
        const risingUserGroup = container.querySelector('#rising-user-arrows-group');
        const risingChipsListEl = container.querySelector('#rising-connections-list');
        const risingClearBtnEl = container.querySelector('#btn-clear-rising-connections');

        const risingCardConfigs = [
            { cardEl: rashiCol, idPrefix: 'd1_', markerBase: 'url(#rising-arrow-base-slate)', markerLoop: 'url(#rising-arrow-base-loop)' },
            { cardEl: navamshaCol, idPrefix: 'd9_', markerBase: 'url(#rising-arrow-base-slate)', markerLoop: 'url(#rising-arrow-base-loop)' }
        ];

        const redrawRisingFn = () => {
            const links = getRisingLinks();
            redrawStageConnections(risingWrapper, risingBaseGroup, risingUserGroup, risingCardConfigs, links, 'url(#rising-arrow-harmonic)', 'url(#rising-arrow-dissonant)');
        };

        setupInteractiveStageSelection({
            stageId: 'rising_signs',
            stageWrapper: risingWrapper,
            chipsListEl: risingChipsListEl,
            clearBtnEl: risingClearBtnEl,
            getLinks: getRisingLinks,
            saveLinks: saveRisingLinks,
            redrawFn: redrawRisingFn
        });

        if (risingWrapper && window.ResizeObserver) {
            if (container._risingResizeObserver) {
                container._risingResizeObserver.disconnect();
            }
            container._risingResizeObserver = new ResizeObserver(() => {
                redrawRisingFn();
            });
            container._risingResizeObserver.observe(risingWrapper);
        }
    }

    // 3. Section 3: Dominance Leaderboard
    const tableWrap = container.querySelector('.dominance-table-wrapper');
    if (tableWrap) {
        tableWrap.innerHTML = renderDominanceLeaderboard(nakDominance);
    }
    const totalPtsEl = container.querySelector('.report-total-points');
    if (totalPtsEl && nakDominance.total_points !== undefined) {
        totalPtsEl.textContent = `Total Points: ${nakDominance.total_points.toFixed(2)}`;
    }

    // 4. Section 4: Balance of Nakshatra Types
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

    // 5. Section 5: Planet ⟷ Sign ⟷ House Interactive Synthesis Flowchart Desk
    ensureActionBarWired();
    await initSynthesisCockpit(container, currentData);
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
    titleEl.textContent = subjectName + " — Chart Assessment Report";

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
        title: 'Chart Assessment Report',
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
    window.initSynthesisCockpit = initSynthesisCockpit;
    window.renderSynthesisCockpit = renderSynthesisCockpit;
    window.getSignificationsData = getSignificationsData;
    window.redrawStageConnections = redrawStageConnections;
    window.redrawAllConnections = redrawStageConnections;
    window.renderEntityFlowchartCard = renderEntityFlowchartCard;
    window.renderPillarCard = renderEntityFlowchartCard;
    window.drawBaseInternalArrows = drawBaseInternalArrows;
    window.getNodeDockPoint = getNodeDockPoint;
}
