/**
 * Astra Chart Library Modal & Native Management
 * 
 * Manages the Open Chart dialog, search filtering by category/text,
 * pinning natives to top dropdown, keyboard navigation, and geographic timezone lookup.
 */

(function() {
    let currentOpenChartCategory = 'all';
    let highlightedOpenChartIndex = 0;
    let filteredOpenCharts = [];

    function formatToDDMMYYYY(dateStr) {
        if (!dateStr) return '';
        dateStr = String(dateStr).trim();
        
        // 1. Slashes
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
        
        // 3. Dashes: YYYY-MM-DD, -YYYY-MM-DD, DD-MM-YYYY
        if (dateStr.includes('-')) {
            const isBCE = dateStr.startsWith('-');
            const clean = isBCE ? dateStr.substring(1) : dateStr;
            const parts = clean.split('-');
            if (parts.length === 3) {
                if (parts[0].length === 4 || parseInt(parts[0], 10) > 31) {
                    const y = isBCE ? `-${parts[0]}` : parts[0];
                    const m = parts[1].padStart(2, '0');
                    const d = parts[2].padStart(2, '0');
                    return `${d}/${m}/${y}`;
                } else {
                    const d = parts[0].padStart(2, '0');
                    const m = parts[1].padStart(2, '0');
                    const y = isBCE ? `-${parts[2]}` : parts[2];
                    return `${d}/${m}/${y}`;
                }
            }
        }
        
        return dateStr;
    }

    async function openChartModal() {
        if (!window.allSavedNatives || window.allSavedNatives.length === 0) {
            if (typeof window.fetchAllNativesFromServer === 'function') {
                await window.fetchAllNativesFromServer();
            }
        }
        const modal = document.getElementById('openChartModal');
        if (!modal) return;
        modal.style.display = 'flex';
        
        const searchInput = document.getElementById('openChartSearchInput');
        if (searchInput) {
            searchInput.value = '';
            setTimeout(() => searchInput.focus(), 50);
        }
        currentOpenChartCategory = 'all';
        updateOpenChartCategoryPills();
        filterOpenChartsList();
    }

    function closeOpenChartModal() {
        const modal = document.getElementById('openChartModal');
        if (modal) modal.style.display = 'none';
    }

    function openAddModalFromLibrary() {
        closeOpenChartModal();
        openAddModal();
    }

    function setOpenChartCategory(cat) {
        currentOpenChartCategory = cat;
        updateOpenChartCategoryPills();
        filterOpenChartsList();
    }

    function updateOpenChartCategoryPills() {
        const pills = document.querySelectorAll('.open-chart-pill');
        pills.forEach(p => {
            if (p.getAttribute('data-cat') === currentOpenChartCategory) {
                p.classList.add('active');
            } else {
                p.classList.remove('active');
            }
        });
    }

    function clearOpenChartSearch() {
        const input = document.getElementById('openChartSearchInput');
        if (input) {
            input.value = '';
            input.focus();
            filterOpenChartsList();
        }
    }

    function filterOpenChartsList() {
        const searchInput = document.getElementById('openChartSearchInput');
        const clearBtn = document.getElementById('clearOpenChartSearchBtn');
        const query = searchInput ? searchInput.value.trim().toLowerCase() : '';
        if (clearBtn) {
            clearBtn.style.display = query.length > 0 ? 'block' : 'none';
        }

        updateCategoryPillCounts();

        const allNatives = window.allSavedNatives || [];

        filteredOpenCharts = allNatives.filter(n => {
            if (currentOpenChartCategory === 'dropdown') {
                if (n.in_dropdown === false) return false;
            } else if (currentOpenChartCategory !== 'all') {
                const nCat = (n.category || 'General').toLowerCase();
                if (nCat !== currentOpenChartCategory.toLowerCase()) return false;
            }

            if (!query) return true;
            const matchName = (n.name || '').toLowerCase().includes(query);
            const matchPlace = (n.place || '').toLowerCase().includes(query);
            const matchCountry = (n.country || '').toLowerCase().includes(query);
            const matchDate = (n.date || '').toLowerCase().includes(query);
            const matchNotes = (n.notes || '').toLowerCase().includes(query);
            const matchCat = (n.category || '').toLowerCase().includes(query);
            return matchName || matchPlace || matchCountry || matchDate || matchNotes || matchCat;
        });

        highlightedOpenChartIndex = 0;
        renderOpenChartList();
    }

    function updateCategoryPillCounts() {
        const allNatives = window.allSavedNatives || [];
        const countAll = allNatives.length;
        const countDropdown = allNatives.filter(n => n.in_dropdown !== false).length;
        const countPersonal = allNatives.filter(n => ['personal', 'general'].includes((n.category || 'general').toLowerCase())).length;
        const countSpiritual = allNatives.filter(n => (n.category || '').toLowerCase() === 'spiritual').length;
        const countHistorical = allNatives.filter(n => (n.category || '').toLowerCase() === 'historical').length;
        const countCriminals = allNatives.filter(n => (n.category || '').toLowerCase() === 'criminals').length;

        const elAll = document.getElementById('catCountAll');
        const elDrop = document.getElementById('catCountDropdown');
        const elPers = document.getElementById('catCountPersonal');
        const elSpir = document.getElementById('catCountSpiritual');
        const elHist = document.getElementById('catCountHistorical');
        const elCrim = document.getElementById('catCountCriminals');
        const elBadge = document.getElementById('openChartTotalBadge');

        if (elAll) elAll.innerText = countAll;
        if (elDrop) elDrop.innerText = countDropdown;
        if (elPers) elPers.innerText = countPersonal;
        if (elSpir) elSpir.innerText = countSpiritual;
        if (elHist) elHist.innerText = countHistorical;
        if (elCrim) elCrim.innerText = countCriminals;
        if (elBadge) elBadge.innerText = `${countAll} charts`;
    }

    function getCategoryBadgeHtml(cat) {
        const c = (cat || 'General').toLowerCase();
        if (c === 'criminals') {
            return '<span class="chart-category-tag chart-cat-criminals">⚠️ Criminals</span>';
        } else if (c === 'spiritual') {
            return '<span class="chart-category-tag chart-cat-spiritual">🕉️ Spiritual</span>';
        } else if (c === 'historical') {
            return '<span class="chart-category-tag chart-cat-historical">🏛️ Historical</span>';
        } else if (c === 'personal') {
            return '<span class="chart-category-tag chart-cat-personal">👤 Personal</span>';
        } else {
            return '<span class="chart-category-tag chart-cat-general">General</span>';
        }
    }

    function renderOpenChartList() {
        const container = document.getElementById('openChartListContainer');
        if (!container) return;

        if (filteredOpenCharts.length === 0) {
            container.innerHTML = `
                <div style="padding: 40px 20px; text-align: center; color: var(--text-muted);">
                    <div style="font-size: 32px; margin-bottom: 8px;">🔍</div>
                    <div style="font-size: 14px; font-weight: 600; color: var(--text-heading);">No matching charts found</div>
                    <div style="font-size: 12px; margin-top: 4px;">Try a different search term or category filter.</div>
                </div>
            `;
            return;
        }

        const currentLoadedId = (window.currentLoadedNative && window.currentLoadedNative.id) || '';

        let html = '';
        filteredOpenCharts.forEach((native, idx) => {
            const isLoaded = (native.id === currentLoadedId);
            const isSelected = (idx === highlightedOpenChartIndex);
            const isPinned = (native.in_dropdown !== false);
            const pinBtnClass = isPinned ? 'pin-toggle-btn is-pinned' : 'pin-toggle-btn';
            const pinBtnText = isPinned ? '📌 In Dropdown' : '📍 Pin';
            const pinBtnTitle = isPinned ? 'Click to remove from top dropdown' : 'Click to show in top dropdown';
            const badgeHtml = getCategoryBadgeHtml(native.category);

            const placeStr = (native.place && native.place !== 'Custom') ? `${native.place}, ` : '';
            const countryStr = native.country || '';
            const locationText = (placeStr || countryStr) ? `${placeStr}${countryStr} • ` : '';
            const coordsText = (native.lat !== undefined && native.lon !== undefined) ? `${parseFloat(native.lat).toFixed(2)}°, ${parseFloat(native.lon).toFixed(2)}° • ` : '';
            const tzText = native.tz ? `TZ: ${native.tz}` : '';
            const notesSnippet = native.notes ? `<div style="font-size: 11px; color: var(--text-muted); margin-top: 3px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 500px;">📝 ${escapeHtml(native.notes)}</div>` : '';

            const rowClasses = [
                'open-chart-row',
                isSelected ? 'selected' : '',
                isLoaded ? 'is-active-loaded' : ''
            ].filter(Boolean).join(' ');

            html += `
                <div class="${rowClasses}" 
                     data-idx="${idx}" 
                     data-id="${native.id}"
                     onclick="selectOpenChartRow(${idx})"
                     ondblclick="openChartFromModal('${native.id}')">
                    <div style="flex: 1; min-width: 0; padding-right: 12px;">
                        <div style="display:flex; align-items:center; gap:6px; margin-bottom: 2px;">
                            ${badgeHtml}
                            <span style="font-weight: 700; font-size: 14px; color: var(--text-heading);">${escapeHtml(native.name)}</span>
                            ${isLoaded ? '<span style="font-size:10px; background:var(--status-benefic); color:#ffffff; padding:1px 5px; border-radius:3px; font-weight:700;">ACTIVE</span>' : ''}
                        </div>
                        <div style="font-size: 12px; color: var(--text-primary);">
                            📅 <b>${formatToDDMMYYYY(native.date)}</b> at <b>${native.time || '12:00:00'}</b> | ${locationText}${coordsText}${tzText}
                        </div>
                        ${notesSnippet}
                    </div>
                    <div style="display: flex; align-items: center; gap: 8px; flex-shrink: 0;">
                        <button type="button" class="${pinBtnClass}" title="${pinBtnTitle}" onclick="togglePinFromModal('${native.id}', event)">
                            ${pinBtnText}
                        </button>
                        <button type="button" onclick="editNativeFromModal('${native.id}', event)" 
                                style="background:var(--bg-surface-hover); color:var(--text-heading); border:1px solid var(--border-medium); padding:4px 8px; border-radius:4px; font-size:11px; font-weight:600; cursor:pointer;"
                                title="Edit details">
                            ✏️
                        </button>
                        <button type="button" class="btn-primary" onclick="openChartFromModal('${native.id}')" style="padding: 5px 12px; font-size: 12px; font-weight: 600;">
                            📂 Open
                        </button>
                    </div>
                </div>
            `;
        });

        container.innerHTML = html;

        const selectedRow = container.querySelector('.open-chart-row.selected');
        if (selectedRow) {
            selectedRow.scrollIntoView({ block: 'nearest' });
        }
    }

    function selectOpenChartRow(idx) {
        highlightedOpenChartIndex = idx;
        const rows = document.querySelectorAll('.open-chart-row');
        rows.forEach((r, i) => {
            if (i === idx) {
                r.classList.add('selected');
            } else {
                r.classList.remove('selected');
            }
        });
    }

    function handleOpenChartKeydown(e) {
        if (e.key === 'ArrowDown') {
            e.preventDefault();
            if (highlightedOpenChartIndex < filteredOpenCharts.length - 1) {
                highlightedOpenChartIndex++;
                renderOpenChartList();
            }
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            if (highlightedOpenChartIndex > 0) {
                highlightedOpenChartIndex--;
                renderOpenChartList();
            }
        } else if (e.key === 'Enter') {
            e.preventDefault();
            if (filteredOpenCharts.length > 0 && highlightedOpenChartIndex < filteredOpenCharts.length) {
                const target = filteredOpenCharts[highlightedOpenChartIndex];
                openChartFromModal(target.id);
            }
        } else if (e.key === 'Escape') {
            e.preventDefault();
            closeOpenChartModal();
        }
    }

    async function openChartFromModal(nativeId) {
        closeOpenChartModal();
        if (typeof window.loadChart === 'function') {
            await window.loadChart(nativeId);
        }
    }

    async function togglePinFromModal(nativeId, event) {
        if (event) event.stopPropagation();
        try {
            const res = await fetch(`/api/native/${nativeId}/toggle_dropdown`, { method: 'POST' });
            const data = await res.json();
            if (data.success && window.allSavedNatives) {
                const native = window.allSavedNatives.find(n => n.id === nativeId);
                if (native) {
                    native.in_dropdown = data.in_dropdown;
                }
                syncNativeSelectOptions();
                filterOpenChartsList();
            }
        } catch (err) {
            console.error("Failed to toggle pin state:", err);
        }
    }

    function editNativeFromModal(nativeId, event) {
        if (event) event.stopPropagation();
        closeOpenChartModal();
        const select = document.getElementById('nativeSelect');
        if (select) select.value = nativeId;
        const editIdEl = document.getElementById('editNativeId');
        if (editIdEl) editIdEl.value = nativeId;
        openEditModal();
    }

    function syncNativeSelectOptions() {
        const select = document.getElementById('nativeSelect');
        if (!select) return;
        const currentVal = select.value || (window.currentLoadedNative ? window.currentLoadedNative.id : '');
        select.innerHTML = '<option value="">-- Select Person --</option>';

        const allNatives = window.allSavedNatives || [];
        const dropdownNatives = allNatives.filter(n => n.in_dropdown !== false);
        dropdownNatives.forEach(n => {
            const opt = document.createElement('option');
            opt.value = n.id;
            opt.text = `${n.name} (${formatToDDMMYYYY(n.date)})`;
            select.appendChild(opt);
        });

        if (window.currentLoadedNative && !dropdownNatives.some(n => n.id === window.currentLoadedNative.id)) {
            const opt = document.createElement('option');
            opt.value = window.currentLoadedNative.id;
            opt.text = `📁 ${window.currentLoadedNative.name} (${formatToDDMMYYYY(window.currentLoadedNative.date)})`;
            select.appendChild(opt);
        }

        const openOpt = document.createElement('option');
        openOpt.value = '__open_chart_dialog__';
        openOpt.text = '── 📂 Open Chart... (Ctrl+O) ──';
        select.appendChild(openOpt);

        if (currentVal && Array.from(select.options).some(o => o.value === currentVal)) {
            select.value = currentVal;
        }
    }

    async function populateNativeForm(native) {
        document.getElementById('editNativeId').value = native.id;
        document.getElementById('newName').value = native.name;
        document.getElementById('newDate').value = formatToDDMMYYYY(native.date);
        
        let tStr = native.time || '12:00:00';
        if (tStr.length === 5) tStr += ":00";
        document.getElementById('newTime').value = tStr;
        
        document.getElementById('newLat').value = native.lat;
        document.getElementById('newLon').value = native.lon;
        document.getElementById('newTz').value = native.tz;
        document.getElementById('newNameSoundValue').value = native.name_sound_value !== undefined ? native.name_sound_value : "0";
        if (document.getElementById('newPlace')) {
            document.getElementById('newPlace').value = (native.place && native.place !== "Custom") ? native.place : "";
        }
        if (document.getElementById('newNotes')) {
            document.getElementById('newNotes').value = native.notes || "";
        }
        if (document.getElementById('newCategory')) {
            document.getElementById('newCategory').value = native.category || "General";
        }
        if (document.getElementById('newInDropdown')) {
            document.getElementById('newInDropdown').checked = (native.in_dropdown !== false);
        }
        
        if (native.country) {
            document.getElementById('countrySelect').value = native.country;
            await loadCities();
            if (native.place && native.place !== "Custom") {
                const citySelect = document.getElementById('citySelect');
                for (let i = 0; i < citySelect.options.length; i++) {
                    if (citySelect.options[i].text === native.place) {
                        citySelect.selectedIndex = i;
                        break;
                    }
                }
            }
        } else {
            document.getElementById('countrySelect').value = "";
            document.getElementById('citySelect').innerHTML = '<option value="">-- City --</option>';
            document.getElementById('citySelect').disabled = true;
        }
    }

    async function openEditModal() {
        const select = document.getElementById('nativeSelect');
        let nativeId = document.getElementById('editNativeId')?.value;
        if (!nativeId && select && select.value && select.value !== '__open_chart_dialog__') {
            nativeId = select.value;
        }
        if (!nativeId && select && select.options.length > 1) {
            nativeId = select.options[1].value;
            select.value = nativeId;
        }
        if (!nativeId || nativeId === '__open_chart_dialog__') {
            alert("Please select or load a person first to edit.");
            return;
        }
        
        document.getElementById('nativeModalTitle').innerText = "✏️ Edit Person Details";
        document.getElementById('updateBtn').style.display = 'inline-block';
        document.getElementById('deleteNativeBtn').style.display = 'inline-block';
        document.getElementById('saveAsNewBtn').style.display = 'inline-block';
        document.getElementById('saveAsNewBtn').innerText = 'Save as Copy';
        document.getElementById('saveAsNewBtn').style.backgroundColor = 'var(--bg-surface-hover)';
        document.getElementById('saveAsNewBtn').style.color = 'var(--text-primary)';
        
        try {
            const response = await fetch(`/api/native/${nativeId}`);
            const native = await response.json();
            if (native.error) {
                alert(native.error);
                return;
            }
            await populateNativeForm(native);
            document.getElementById('addPersonModal').style.display = 'flex';
        } catch (e) {
            console.error("Failed to load native for editing", e);
            alert("Could not load person details for editing.");
        }
    }

    function openAddModal() {
        document.getElementById('nativeModalTitle').innerText = "+ Add New Person";
        document.getElementById('editNativeId').value = '';
        document.getElementById('newName').value = '';
        document.getElementById('newDate').value = '';
        document.getElementById('newTime').value = '12:00:00';
        document.getElementById('newLat').value = '';
        document.getElementById('newLon').value = '';
        document.getElementById('newTz').value = '+00:00';
        document.getElementById('newNameSoundValue').value = '0';
        if (document.getElementById('newPlace')) {
            document.getElementById('newPlace').value = '';
        }
        if (document.getElementById('newNotes')) {
            document.getElementById('newNotes').value = '';
        }
        if (document.getElementById('newCategory')) {
            document.getElementById('newCategory').value = 'General';
        }
        if (document.getElementById('newInDropdown')) {
            document.getElementById('newInDropdown').checked = true;
        }
        document.getElementById('countrySelect').value = '';
        document.getElementById('citySelect').innerHTML = '<option value="">-- City --</option>';
        document.getElementById('citySelect').disabled = true;
        document.getElementById('updateBtn').style.display = 'none';
        document.getElementById('deleteNativeBtn').style.display = 'none';
        document.getElementById('saveAsNewBtn').style.display = 'inline-block';
        document.getElementById('saveAsNewBtn').innerText = 'Save Person';
        document.getElementById('saveAsNewBtn').style.backgroundColor = 'var(--accent-primary)';
        document.getElementById('saveAsNewBtn').style.color = '#ffffff';
        document.getElementById('addPersonModal').style.display = 'flex';
    }

    async function loadCountries() {
        try {
            const response = await fetch('/api/countries');
            const countries = await response.json();
            const select = document.getElementById('countrySelect');
            if (!select) return;
            countries.forEach(c => {
                const opt = document.createElement('option');
                opt.value = c.code;
                opt.text = c.name;
                select.appendChild(opt);
            });
        } catch (e) {
            console.error("Failed to load countries", e);
        }
    }
    
    async function loadCities() {
        const countryEl = document.getElementById('countrySelect');
        const countryCode = countryEl ? countryEl.value : '';
        const citySelect = document.getElementById('citySelect');
        if (!citySelect) return;
        citySelect.innerHTML = '<option value="">-- City --</option>';
        if (!countryCode) {
            citySelect.disabled = true;
            return;
        }
        citySelect.disabled = true;
        try {
            const response = await fetch(`/api/cities/${countryCode}`);
            const cities = await response.json();
            cities.forEach(c => {
                const opt = document.createElement('option');
                opt.value = c.id;
                opt.text = c.name;
                opt.dataset.lat = c.lat;
                opt.dataset.lon = c.lon;
                citySelect.appendChild(opt);
            });
            citySelect.disabled = false;
        } catch (e) {
            console.error("Failed to load cities", e);
        }
    }
    
    async function fetchTimezone() {
        const citySelect = document.getElementById('citySelect');
        if (!citySelect || citySelect.selectedIndex < 0) return;
        const opt = citySelect.options[citySelect.selectedIndex];
        if (!opt || !opt.value) return;
        
        const lat = opt.dataset.lat;
        const lon = opt.dataset.lon;
        document.getElementById('newLat').value = lat;
        document.getElementById('newLon').value = lon;
        if (document.getElementById('newPlace')) {
            document.getElementById('newPlace').value = opt.text;
        }
        
        const dateStr = document.getElementById('newDate')?.value || '01/01/2000';
        const timeStr = document.getElementById('newTime')?.value || '12:00:00';
        
        try {
            const response = await fetch('/api/timezone', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ lat, lon, date: dateStr, time: timeStr })
            });
            const res = await response.json();
            if (res.offset) {
                document.getElementById('newTz').value = res.offset;
            }
        } catch (e) {
            console.error("Failed to fetch timezone", e);
        }
    }

    async function detectTimezoneFromCoords() {
        const lat = document.getElementById('newLat')?.value.trim();
        const lon = document.getElementById('newLon')?.value.trim();
        if (!lat || !lon) {
            alert("Please enter Latitude and Longitude first.");
            return;
        }
        const dateStr = document.getElementById('newDate')?.value || '01/01/2000';
        const timeStr = document.getElementById('newTime')?.value || '12:00:00';
        try {
            const response = await fetch('/api/timezone', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ lat, lon, date: dateStr, time: timeStr })
            });
            const res = await response.json();
            if (res.offset) {
                document.getElementById('newTz').value = res.offset;
            }
        } catch (e) {
            console.error("Failed to detect timezone", e);
            alert("Could not detect timezone.");
        }
    }

    document.addEventListener('keydown', function(e) {
        if ((e.ctrlKey || e.metaKey) && e.key && e.key.toLowerCase() === 'o') {
            e.preventDefault();
            openChartModal();
        }
    });

    // Attach to window for global access and HTML onclick
    window.formatToDDMMYYYY = formatToDDMMYYYY;
    window.openChartModal = openChartModal;
    window.closeOpenChartModal = closeOpenChartModal;
    window.openAddModalFromLibrary = openAddModalFromLibrary;
    window.setOpenChartCategory = setOpenChartCategory;
    window.updateOpenChartCategoryPills = updateOpenChartCategoryPills;
    window.clearOpenChartSearch = clearOpenChartSearch;
    window.filterOpenChartsList = filterOpenChartsList;
    window.updateCategoryPillCounts = updateCategoryPillCounts;
    window.getCategoryBadgeHtml = getCategoryBadgeHtml;
    window.renderOpenChartList = renderOpenChartList;
    window.selectOpenChartRow = selectOpenChartRow;
    window.handleOpenChartKeydown = handleOpenChartKeydown;
    window.openChartFromModal = openChartFromModal;
    window.togglePinFromModal = togglePinFromModal;
    window.editNativeFromModal = editNativeFromModal;
    window.syncNativeSelectOptions = syncNativeSelectOptions;
    window.populateNativeForm = populateNativeForm;
    window.openEditModal = openEditModal;
    window.openAddModal = openAddModal;
    window.loadCountries = loadCountries;
    window.loadCities = loadCities;
    window.fetchTimezone = fetchTimezone;
    window.detectTimezoneFromCoords = detectTimezoneFromCoords;
})();
