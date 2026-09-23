/**
 * Astra Astrological Notes & Journal System Widget
 * 
 * Provides an integrated study journal per native and 12-house cards
 * with real-time saving and debounce.
 */

        function openNotesFromChart(btn, targetHouseNum = null) {
            let notesCell = document.querySelector('.grid-cell[data-widget="notes"]');
            if (!notesCell) {
                // Check for empty cell
                const emptyCell = document.querySelector('.grid-cell[data-widget="empty"]');
                if (emptyCell) {
                    notesCell = emptyCell;
                    assignWidget('notes', notesCell);
                } else {
                    const activeCell = btn ? btn.closest('.grid-cell') : currentActiveCell;
                    if (activeCell) {
                        notesCell = activeCell;
                        assignWidget('notes', notesCell);
                    }
                }
            }
            
            if (notesCell) {
                notesCell.scrollIntoView({ behavior: 'smooth', block: 'center' });
                if (targetHouseNum) {
                    setTimeout(() => {
                        const card = notesCell.querySelector(`.notes-card[data-house="${targetHouseNum}"]`);
                        if (card) {
                            card.scrollIntoView({ behavior: 'smooth', block: 'center' });
                            const ta = card.querySelector('textarea');
                            if (ta) ta.focus();
                        }
                    }, 150);
                }
            }
        }

        // ==========================================
        // ASTROLOGICAL NOTES & JOURNAL SYSTEM
        // ==========================================
        const BHAVA_METADATA = {
            1: { name: "Tanu Bhava", domain: "Self, Physical Body, Vitality & Dharma", categories: ["kendra", "trikona"] },
            2: { name: "Dhana Bhava", domain: "Wealth, Family, Speech & Resources", categories: [] },
            3: { name: "Sahaja Bhava", domain: "Siblings, Courage, Initiative & Skills", categories: ["upachaya"] },
            4: { name: "Sukha / Bandhu Bhava", domain: "Mother, Inner Peace, Home & Vehicles", categories: ["kendra"] },
            5: { name: "Putra Bhava", domain: "Children, Intellect, Poorva Punya & Creativity", categories: ["trikona"] },
            6: { name: "Ari / Satru Bhava", domain: "Debts, Diseases, Enemies & Service", categories: ["dusthana", "upachaya"] },
            7: { name: "Kalatra / Jaya Bhava", domain: "Spouse, Relationships & Partnerships", categories: ["kendra"] },
            8: { name: "Randhra Bhava", domain: "Longevity, Transformation, Secrets & Vulnerability", categories: ["dusthana"] },
            9: { name: "Bhagya / Dharma Bhava", domain: "Higher Wisdom, Fortune, Father & Guru", categories: ["trikona"] },
            10: { name: "Karma Bhava", domain: "Career, Social Status, Action & Authority", categories: ["kendra", "upachaya"] },
            11: { name: "Labha Bhava", domain: "Gains, Aspirations, Income & Networks", categories: ["upachaya"] },
            12: { name: "Vyaya Bhava", domain: "Losses, Moksha, Solitude & Foreign Lands", categories: ["dusthana"] }
        };

        let notesDebounceTimer = null;

        function normalizeNativeNotes(notes) {
            if (!notes) return { general: "", houses: {} };
            if (typeof notes === 'string') {
                const trimmed = notes.trim();
                if (trimmed.startsWith('{') && trimmed.endsWith('}')) {
                    try {
                        const parsed = JSON.parse(trimmed);
                        if (parsed && typeof parsed === 'object') {
                            return { general: parsed.general || "", houses: parsed.houses || {} };
                        }
                    } catch(e) {}
                }
                return { general: notes, houses: {} };
            }
            if (typeof notes === 'object') {
                return { general: notes.general || "", houses: notes.houses || {} };
            }
            return { general: "", houses: {} };
        }

        function updateNotesWidget(cell, chartData) {
            if (!cell) return;
            const native = window.currentLoadedNative;
            const chart = chartData || window.currentChartData;
            
            const nameEl = cell.querySelector('.notes-native-name');
            if (nameEl) {
                nameEl.textContent = native ? `Notes: ${native.name}` : "Native Notes";
            }
            
            const notesData = native ? normalizeNativeNotes(native.notes) : { general: "", houses: {} };
            if (native) native.notes = notesData;

            // 1. General Synthesis Card
            const genCard = cell.querySelector('.notes-card.general-card');
            if (genCard) {
                const genTa = genCard.querySelector('.general-notes-input');
                if (genTa) {
                    genTa.value = notesData.general || "";
                    if (genTa.value.trim().length > 0) genCard.classList.add('has-notes');
                    else genCard.classList.remove('has-notes');
                }
                
                // General context
                const akEl = genCard.querySelector('.context-atmakaraka');
                const lagnaLordEl = genCard.querySelector('.context-lagna-lord');
                const dashaEl = genCard.querySelector('.context-dasha');
                
                if (chart && chart.vargas && chart.vargas.D1) {
                    const d1 = chart.vargas.D1;
                    const lagnaSign = d1.lagna ? d1.lagna.sign : "";
                    const signLords = { 'Aries': 'Mars', 'Taurus': 'Venus', 'Gemini': 'Mercury', 'Cancer': 'Moon', 'Leo': 'Sun', 'Virgo': 'Mercury', 'Libra': 'Venus', 'Scorpio': 'Mars', 'Sagittarius': 'Jupiter', 'Capricorn': 'Saturn', 'Aquarius': 'Saturn', 'Pisces': 'Jupiter' };
                    const lLord = signLords[lagnaSign] || "";
                    let lLordPlacement = "";
                    if (lLord && d1.grahas && d1.grahas[lLord]) {
                        lLordPlacement = `${lLord} in ${d1.grahas[lLord].sign}`;
                    }
                    if (lagnaLordEl) lagnaLordEl.innerHTML = `<strong>Lagna Lord:</strong> ${lLordPlacement || lagnaSign || '—'}`;
                    
                    // Atmakaraka
                    let akName = "";
                    if (chart.karakas && chart.karakas.AK) akName = chart.karakas.AK;
                    else if (chart.jaimini_karakas && chart.jaimini_karakas.AK) akName = chart.jaimini_karakas.AK;
                    else if (d1.grahas) {
                        let maxDeg = -1;
                        for (const [gName, gData] of Object.entries(d1.grahas)) {
                            if (['Rahu', 'Ketu', 'Lagna'].includes(gName)) continue;
                            const deg = (gData.degree || 0) + (gData.minute || 0)/60;
                            if (deg > maxDeg) { maxDeg = deg; akName = gName; }
                        }
                    }
                    if (akEl) akEl.innerHTML = `<strong>Atmakaraka:</strong> ${akName || '—'}`;

                    // Current Dasha
                    let curDashaStr = "—";
                    if (chart.vimshottari_dasha && chart.vimshottari_dasha.mahadashas) {
                        const now = new Date();
                        const activeMD = chart.vimshottari_dasha.mahadashas.find(m => {
                            const s = new Date(m.start);
                            const e = new Date(m.end);
                            return now >= s && now <= e;
                        });
                        if (activeMD) curDashaStr = `${activeMD.planet} Mahādaśā`;
                    }
                    if (dashaEl) dashaEl.innerHTML = `<strong>Current Daśā:</strong> ${curDashaStr}`;
                }
            }

            // 2. 12 House Cards
            const housesContainer = cell.querySelector('.notes-houses-container');
            if (!housesContainer) return;
            housesContainer.innerHTML = '';

            const signsList = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"];
            const signLords = { 'Aries': 'Mars', 'Taurus': 'Venus', 'Gemini': 'Mercury', 'Cancer': 'Moon', 'Leo': 'Sun', 'Virgo': 'Mercury', 'Libra': 'Venus', 'Scorpio': 'Mars', 'Sagittarius': 'Jupiter', 'Capricorn': 'Saturn', 'Aquarius': 'Saturn', 'Pisces': 'Jupiter' };

            const d1Data = (chart && chart.vargas && chart.vargas.D1) ? chart.vargas.D1 : null;
            const bhavas = d1Data ? (d1Data.bhavas || []) : [];
            const d1Grahas = d1Data ? (d1Data.grahas || {}) : {};
            const d1Lagna = d1Data ? (d1Data.lagna || {}) : {};
            const lagnaSign = d1Lagna.sign || "Aries";
            const lagnaIdx = signsList.indexOf(lagnaSign);

            for (let h = 1; h <= 12; h++) {
                const meta = BHAVA_METADATA[h] || { name: `House ${h}`, domain: "", categories: [] };
                const bhava = bhavas[h - 1] || null;
                
                let signName = "";
                let cuspDegStr = "";
                if (bhava && bhava.cusp !== undefined) {
                    const cLon = bhava.cusp;
                    const sIdx = Math.floor(cLon / 30);
                    signName = signsList[sIdx];
                    const degInSign = cLon % 30;
                    const d = Math.floor(degInSign);
                    const m = Math.round((degInSign - d) * 60);
                    cuspDegStr = `${d}°${m.toString().padStart(2, '0')}'`;
                } else {
                    const sIdx = (lagnaIdx + h - 1) % 12;
                    signName = signsList[sIdx];
                }

                // Lord of house and placement
                const lord = signLords[signName] || "";
                let lordPlacementStr = "";
                if (lord && d1Grahas[lord]) {
                    const lData = d1Grahas[lord];
                    const lSign = lData.sign;
                    const lH = (signsList.indexOf(lSign) - lagnaIdx + 12) % 12 + 1;
                    lordPlacementStr = `${lord} in H${lH} (${lSign})`;
                }

                // Resident planets in this house
                let residentPlanets = [];
                if (bhava && Array.isArray(bhava.planets)) {
                    residentPlanets = bhava.planets;
                } else if (d1Grahas) {
                    for (const [pName, pData] of Object.entries(d1Grahas)) {
                        if (pData.sign === signName) residentPlanets.push(pName);
                    }
                }
                const occupantsStr = residentPlanets.length > 0 ? residentPlanets.join(', ') : 'None';

                // Badges
                let catBadgesHtml = '';
                if (meta.categories.includes('kendra')) {
                    catBadgesHtml += `<span style="background:#e0f2fe; color:#0369a1; border:1px solid #7dd3fc; border-radius:3px; padding:1px 5px; font-size:9.5px; font-weight:700;">Kendra</span> `;
                }
                if (meta.categories.includes('trikona')) {
                    catBadgesHtml += `<span style="background:#fef3c7; color:#92400e; border:1px solid #fcd34d; border-radius:3px; padding:1px 5px; font-size:9.5px; font-weight:700;">Trikona</span> `;
                }
                if (meta.categories.includes('dusthana')) {
                    catBadgesHtml += `<span style="background:#fee2e2; color:#991b1b; border:1px solid #fca5a5; border-radius:3px; padding:1px 5px; font-size:9.5px; font-weight:700;">Dusthana</span> `;
                }
                if (meta.categories.includes('upachaya')) {
                    catBadgesHtml += `<span style="background:#dcfce7; color:#166534; border:1px solid #86efac; border-radius:3px; padding:1px 5px; font-size:9.5px; font-weight:700;">Upachaya</span> `;
                }

                const existingText = (notesData.houses && notesData.houses[h]) ? notesData.houses[h] : "";
                const hasNotesClass = existingText.trim().length > 0 ? " has-notes" : "";
                const writtenBadgeHtml = existingText.trim().length > 0 
                    ? `<span class="notes-status-badge" style="color:#0284c7; font-size:10px; font-weight:700;">✓ Notes Written</span>` 
                    : `<span class="notes-status-badge" style="color:#94a3b8; font-size:10px;">Empty</span>`;

                const cardHtml = `
                    <div class="notes-card house-card${hasNotesClass}" data-house="${h}" data-categories="${meta.categories.join(' ')}">
                        <div class="notes-card-header">
                            <div class="notes-card-title">
                                <span style="background:#4a3325; color:#fffdfa; border-radius:4px; padding:1px 6px; font-size:11px; font-weight:bold;">H${h}</span>
                                <span>${meta.name}</span>
                                <span style="font-size:11px; font-weight:normal; color:#78716c;">— ${meta.domain}</span>
                            </div>
                            <div style="display:flex; align-items:center; gap:6px;">
                                ${catBadgesHtml}
                                ${writtenBadgeHtml}
                            </div>
                        </div>
                        <div class="notes-card-context">
                            <span><strong>Cusp:</strong> ${signName} ${cuspDegStr}</span>
                            <span>•</span>
                            <span><strong>Lord:</strong> ${lordPlacementStr || lord || '—'}</span>
                            <span>•</span>
                            <span><strong>Occupants:</strong> ${occupantsStr}</span>
                        </div>
                        <textarea class="notes-textarea house-notes-input" placeholder="Notes, significations, transits, or analysis for House ${h} (${meta.name})..." oninput="handleNoteTyping(this, 'house', ${h})">${existingText}</textarea>
                    </div>
                `;
                housesContainer.insertAdjacentHTML('beforeend', cardHtml);
            }
        }

        function handleNoteTyping(textarea, type, houseNum = null) {
            if (!currentLoadedNative) return;
            const native = currentLoadedNative;
            if (!native.notes || typeof native.notes !== 'object') {
                native.notes = { general: "", houses: {} };
            }
            if (!native.notes.houses) native.notes.houses = {};

            const card = textarea.closest('.notes-card');
            const val = textarea.value;

            if (type === 'general') {
                native.notes.general = val;
            } else if (type === 'house' && houseNum) {
                native.notes.houses[houseNum] = val;
            }

            if (card) {
                const statusBadge = card.querySelector('.notes-status-badge');
                if (val.trim().length > 0) {
                    card.classList.add('has-notes');
                    if (statusBadge) {
                        statusBadge.textContent = '✓ Notes Written';
                        statusBadge.style.color = '#0284c7';
                        statusBadge.style.fontWeight = '700';
                    }
                } else {
                    card.classList.remove('has-notes');
                    if (statusBadge) {
                        statusBadge.textContent = 'Empty';
                        statusBadge.style.color = '#94a3b8';
                        statusBadge.style.fontWeight = 'normal';
                    }
                }
            }

            // Update save status indicator
            document.querySelectorAll('.notes-save-badge').forEach(b => {
                b.textContent = 'Saving... ⏳';
                b.style.color = '#d97706';
            });

            // Debounce save to server
            clearTimeout(notesDebounceTimer);
            notesDebounceTimer = setTimeout(() => {
                saveNativeNotesToServer(native.id);
            }, 800);
        }

        async function saveNativeNotesToServer(nativeId) {
            if (!nativeId || !currentLoadedNative) return;
            try {
                const res = await fetch(`/api/native/${nativeId}/notes`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(currentLoadedNative.notes)
                });
                if (res.ok) {
                    document.querySelectorAll('.notes-save-badge').forEach(b => {
                        b.textContent = 'All changes saved ✓';
                        b.style.color = '#16a34a';
                    });
                } else {
                    document.querySelectorAll('.notes-save-badge').forEach(b => {
                        b.textContent = 'Save failed ⚠️';
                        b.style.color = '#dc2626';
                    });
                }
            } catch(e) {
                console.error("Error saving notes:", e);
                document.querySelectorAll('.notes-save-badge').forEach(b => {
                    b.textContent = 'Save failed ⚠️';
                    b.style.color = '#dc2626';
                });
            }
        }

        function filterNotesCategory(btn, filterType) {
            const widget = btn.closest('.widget-notes');
            if (!widget) return;
            
            widget.querySelectorAll('.notes-filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            const genCard = widget.querySelector('.notes-card.general-card');
            const houseCards = widget.querySelectorAll('.notes-card.house-card');

            if (filterType === 'all') {
                if (genCard) genCard.style.display = 'block';
                houseCards.forEach(c => c.style.display = 'block');
            } else if (filterType === 'general') {
                if (genCard) genCard.style.display = 'block';
                houseCards.forEach(c => c.style.display = 'none');
            } else {
                if (genCard) genCard.style.display = 'none';
                const targets = HOUSE_CATEGORIES[filterType] || [];
                houseCards.forEach(c => {
                    const hNum = parseInt(c.dataset.house, 10);
                    if (targets.includes(hNum)) {
                        c.style.display = 'block';
                    } else {
                        c.style.display = 'none';
                    }
                });
            }
        }

        function maximizeNotesFromWidget(btn) {
            const cell = btn.closest('.grid-cell');
            if (!cell) return;
            const content = cell.querySelector('.grid-cell-content');
            if (!content) return;
            const modal = document.getElementById('widgetMaximizeModal');
            const body = document.getElementById('maximizeModalBody');
            const title = document.getElementById('maximizeModalTitle');
            if (!modal || !body) return;
            
            title.textContent = `📝 Astrological Notes & Journal — ${currentLoadedNative ? currentLoadedNative.name : ''}`;
            body.innerHTML = '';
            
            // Clone notes widget into modal body
            const clone = content.cloneNode(true);
            body.appendChild(clone);
            modal.style.display = 'flex';
        }


// Register with WidgetRegistry
if (typeof window !== 'undefined' && window.widgetRegistry) {
    window.widgetRegistry.register('notes', {
        id: 'notes',
        title: 'Astrological Notes & Journal',
        icon: '📝',
        category: 'Journal',
        isScrollable: true,
        onUpdate: function(cell, chartData) {
            updateNotesWidget(cell, chartData);
        }
    });
}

// Global exports
if (typeof window !== 'undefined') {
    window.openNotesFromChart = openNotesFromChart;
    window.updateNotesWidget = updateNotesWidget;
    window.maximizeNotesFromWidget = maximizeNotesFromWidget;
    window.normalizeNativeNotes = normalizeNativeNotes;
    window.BHAVA_METADATA = BHAVA_METADATA;
}
