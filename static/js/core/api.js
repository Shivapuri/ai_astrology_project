/**
 * Astra Backend API Client
 * 
 * Centralizes all asynchronous fetch() calls to Flask backend endpoints,
 * coordinating with Astra Store and maintaining global compatibility.
 */

const AstraAPI = {
    /**
     * Load chart calculation data and initial SVGs for a native.
     */
    async loadChart(nativeId = null) {
        const select = document.getElementById('nativeSelect');
        const id = nativeId || (select && select.value && select.value !== '__open_chart_dialog__' ? select.value : null) || (window.currentLoadedNative ? window.currentLoadedNative.id : null);
        if (!id) return null;

        const loadingEl = document.getElementById('loading');
        if (loadingEl) loadingEl.style.display = 'block';

        const store = window.astraStore;
        const d10Mode = (store && store.state.d10Mode) ? store.state.d10Mode : (window.currentD10Mode || 'reverse');
        const d24Mode = (store && store.state.d24Mode) ? store.state.d24Mode : (window.currentD24Mode || 'reverse');
        const nakshatra = (store && store.state.nakshatraSystem) ? store.state.nakshatraSystem : (window.currentNakshatraSystem || 'ERNST_DHRUVA');
        const notation = (store && store.state.notation) ? store.state.notation : (window.currentNotation || 'symbol');

        try {
            const url = `/api/chart/${id}?mode=${notation}&d10_mode=${d10Mode}&d24_mode=${d24Mode}&nakshatra_system=${nakshatra}`;
            const response = await fetch(url);
            const result = await response.json();

            if (result.error) {
                alert(result.error);
                return null;
            }

            // Sync with Store & Window
            const previewTime = result.preview_time || (result.native && result.native.time);
            const previewDate = result.preview_date || (result.native && result.native.date);

            // Merge newly fetched SVGs into existing cache so all fetched notations are preserved
            if (window.currentSvgs && result.svgs) {
                for (const v of Object.keys(result.svgs)) {
                    if (window.currentSvgs[v] && typeof window.currentSvgs[v] === 'object') {
                        result.svgs[v] = { ...window.currentSvgs[v], ...result.svgs[v] };
                    }
                }
            }

            window.currentChartData = result.data;
            window.currentSvgs = result.svgs;
            window.currentLoadedNative = result.native;
            window.activePreviewOffsetSeconds = 0;
            window.currentPreviewTime = previewTime;
            window.currentPreviewDate = previewDate;

            if (store) {
                store.setState({
                    currentNative: result.native,
                    chartData: result.data,
                    svgs: result.svgs,
                    previewOffsetSeconds: 0,
                    previewTime: previewTime,
                    previewDate: previewDate,
                    d10Mode: d10Mode,
                    d24Mode: d24Mode,
                    nakshatraSystem: nakshatra,
                    notation: notation
                });
            }

            // Update DOM title & subtitle
            const titleEl = document.getElementById('chartTitle');
            if (titleEl && result.data?.subject_info?.name) {
                titleEl.innerText = `${result.data.subject_info.name} - Birth Chart`;
            }

            const subEl = document.getElementById('chartSubtitle');
            if (subEl && result.data?.subject_info) {
                const info = result.data.subject_info;
                const latVal = parseFloat(info.latitude);
                const lonVal = parseFloat(info.longitude);
                const latDir = latVal >= 0 ? 'N' : 'S';
                const lonDir = lonVal >= 0 ? 'E' : 'W';
                const latStr = `${Math.abs(latVal).toFixed(4)}° ${latDir}`;
                const lonStr = `${Math.abs(lonVal).toFixed(4)}° ${lonDir}`;
                const pName = (result.native && result.native.place && result.native.place !== 'Custom')
                    ? result.native.place
                    : (info.place && info.place !== 'Custom' ? info.place : '');
                const pStr = pName ? `${pName} • ` : '';
                subEl.innerText = `${info.birth_datetime} | ${pStr}${latStr}, ${lonStr}`;
            }

            // Update edit form if present
            if (result.native) {
                const editIdEl = document.getElementById('editNativeId');
                if (editIdEl) editIdEl.value = result.native.id;
                const newNameEl = document.getElementById('newName');
                if (newNameEl) newNameEl.value = result.native.name;
                const newDateEl = document.getElementById('newDate');
                if (newDateEl && typeof window.formatToDDMMYYYY === 'function') {
                    newDateEl.value = window.formatToDDMMYYYY(result.native.date);
                }
                const newTimeEl = document.getElementById('newTime');
                if (newTimeEl) {
                    let tStr = result.native.time;
                    if (tStr && tStr.length === 5) tStr += ":00";
                    newTimeEl.value = tStr;
                }
                const latEl = document.getElementById('newLat');
                if (latEl) latEl.value = result.native.lat;
                const lonEl = document.getElementById('newLon');
                if (lonEl) lonEl.value = result.native.lon;
                const tzEl = document.getElementById('newTz');
                if (tzEl) tzEl.value = result.native.tz;
                const placeEl = document.getElementById('newPlace');
                if (placeEl) placeEl.value = (result.native.place && result.native.place !== "Custom") ? result.native.place : "";
                const notesEl = document.getElementById('newNotes');
                if (notesEl) notesEl.value = result.native.notes || "";

                if (select) {
                    let opt = Array.from(select.options).find(o => o.value === result.native.id);
                    if (!opt) {
                        opt = document.createElement('option');
                        opt.value = result.native.id;
                        const isPinned = (result.native.in_dropdown !== false);
                        const pinPrefix = isPinned ? '' : '📁 ';
                        const dateFormatted = typeof window.formatToDDMMYYYY === 'function' ? window.formatToDDMMYYYY(result.native.date) : result.native.date;
                        opt.text = `${pinPrefix}${result.native.name} (${dateFormatted})`;
                        const openOpt = select.querySelector('option[value="__open_chart_dialog__"]');
                        if (openOpt) {
                            select.insertBefore(opt, openOpt);
                        } else {
                            select.appendChild(opt);
                        }
                    }
                    select.value = result.native.id;
                }
            }

            // Setup Split before updating widgets so they exist in DOM
            if (typeof window.setupSplit === 'function') window.setupSplit();
            // Refresh widgets
            if (typeof window.updateAllWidgets === 'function') window.updateAllWidgets();
            if (typeof window.syncD10ModeUI === 'function') window.syncD10ModeUI();
            if (typeof window.syncNakshatraSystemUI === 'function') window.syncNakshatraSystemUI();
            if (typeof window.syncAllSteppersUI === 'function') window.syncAllSteppersUI();

            return result;
        } catch (e) {
            console.error("AstraAPI: loadChart failed", e);
            alert("Failed to load chart.");
            return null;
        } finally {
            if (loadingEl) loadingEl.style.display = 'none';
        }
    },

    /**
     * Fetch list of all saved charts in database.
     */
    async fetchAllNatives() {
        try {
            const res = await fetch('/api/natives');
            if (res.ok) {
                const natives = await res.json();
                window.allSavedNatives = natives;
                return natives;
            }
        } catch (err) {
            console.error("AstraAPI: fetchAllNatives failed", err);
        }
        return [];
    },

    /**
     * Add or update native record in database.
     */
    async saveNative(isUpdate = false) {
        const placeInput = document.getElementById('newPlace');
        const cityEl = document.getElementById('citySelect');
        let placeName = placeInput ? placeInput.value.trim() : "";
        if (!placeName) {
            placeName = (cityEl && cityEl.selectedIndex > 0) ? cityEl.options[cityEl.selectedIndex].text : "Custom";
        }
        const rawDate = document.getElementById('newDate')?.value.trim() || '';
        const formattedDate = typeof window.formatToDDMMYYYY === 'function' ? window.formatToDDMMYYYY(rawDate) : rawDate;
        
        const payload = {
            name: document.getElementById('newName')?.value.trim() || '',
            date: formattedDate,
            time: document.getElementById('newTime')?.value.trim() || '',
            lat: document.getElementById('newLat')?.value.trim() || '',
            lon: document.getElementById('newLon')?.value.trim() || '',
            tz: document.getElementById('newTz')?.value.trim() || '',
            country: document.getElementById('countrySelect')?.value || "",
            place: placeName,
            name_sound_value: document.getElementById('newNameSoundValue')?.value || '0',
            notes: document.getElementById('newNotes') ? document.getElementById('newNotes').value.trim() : "",
            category: document.getElementById('newCategory') ? document.getElementById('newCategory').value : "General",
            in_dropdown: document.getElementById('newInDropdown') ? document.getElementById('newInDropdown').checked : true
        };
        
        if (!payload.name || !payload.date || !payload.time || !payload.lat || !payload.lon || !payload.tz) {
            alert("Please fill all required fields (Name, Date in DD/MM/YYYY, Time, Lat, Lon, Timezone)");
            return null;
        }
        
        try {
            let url = '/api/add_native';
            if (isUpdate) {
                const id = document.getElementById('editNativeId')?.value;
                if (!id) { alert("No chart selected to update"); return null; }
                url = `/api/update_native/${id}`;
            }
            
            const response = await fetch(url, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(payload)
            });
            
            const newNative = await response.json();
            
            if (newNative.error) {
                alert(newNative.error);
                return null;
            }
            
            if (window.allSavedNatives) {
                const existingIdx = window.allSavedNatives.findIndex(n => n.id === newNative.id);
                if (existingIdx >= 0) {
                    window.allSavedNatives[existingIdx] = newNative;
                } else {
                    window.allSavedNatives.push(newNative);
                }
            }
            
            if (typeof window.syncNativeSelectOptions === 'function') window.syncNativeSelectOptions();
            if (document.getElementById('openChartModal')?.style.display === 'flex' && typeof window.filterOpenChartsList === 'function') {
                window.filterOpenChartsList();
            }
            
            const addModal = document.getElementById('addPersonModal');
            if (addModal) addModal.style.display = 'none';
            
            await this.loadChart(newNative.id);
            return newNative;
        } catch (e) {
            console.error("AstraAPI: saveNative failed", e);
            alert("Failed to save native");
            return null;
        }
    },

    /**
     * Delete native by ID.
     */
    async deleteNative(id) {
        if (!id) return false;
        try {
            const res = await fetch(`/api/delete_native/${id}`, { method: 'POST' });
            const data = await res.json();
            if (data.error) {
                alert(data.error);
                return false;
            }
            if (window.allSavedNatives) {
                window.allSavedNatives = window.allSavedNatives.filter(n => n.id !== id);
            }
            if (typeof window.syncNativeSelectOptions === 'function') window.syncNativeSelectOptions();
            if (document.getElementById('openChartModal')?.style.display === 'flex' && typeof window.filterOpenChartsList === 'function') {
                window.filterOpenChartsList();
            }
            const modal = document.getElementById('addPersonModal');
            if (modal) modal.style.display = 'none';

            const select = document.getElementById('nativeSelect');
            if (select && select.options.length > 1 && select.options[1].value !== '__open_chart_dialog__') {
                select.selectedIndex = 1;
                await this.loadChart(select.value);
            } else {
                const title = document.getElementById('chartTitle');
                if (title) title.innerText = "No Chart Loaded";
                const sub = document.getElementById('chartSubtitle');
                if (sub) sub.innerText = "";
            }
            return true;
        } catch (e) {
            console.error("AstraAPI: deleteNative failed", e);
            alert("Failed to delete person.");
            return false;
        }
    },

    /**
     * Fetch timezone offset for given coordinates and datetime.
     */
    async fetchTimezone(params) {
        try {
            const response = await fetch('/api/timezone', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(params)
            });
            return await response.json();
        } catch (e) {
            console.error("AstraAPI: fetchTimezone failed", e);
            return null;
        }
    },

    /**
     * Save updated notes structure for a native.
     */
    async saveNotes(nativeId, notes) {
        if (!nativeId) return false;
        try {
            const res = await fetch(`/api/native/${nativeId}/notes`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(notes)
            });
            return res.ok;
        } catch (e) {
            console.error("AstraAPI: saveNotes failed", e);
            return false;
        }
    },

    /**
     * Fetch individual SVG on-demand according to Architecture Rule 8
     */
    async fetchChartSvg(varga = 'D1', mode = 'symbol', root = 'Lagna', style = 'all', outer = 'D9') {
        const nativeId = window.currentLoadedNative?.id || document.getElementById('nativeSelect')?.value;
        if (!nativeId) return null;
        const store = window.astraStore;
        const d10Mode = (store && store.state.d10Mode) ? store.state.d10Mode : (window.currentD10Mode || 'reverse');
        const d24Mode = (store && store.state.d24Mode) ? store.state.d24Mode : (window.currentD24Mode || 'reverse');
        const nakshatra = (store && store.state.nakshatraSystem) ? store.state.nakshatraSystem : (window.currentNakshatraSystem || 'ERNST_DHRUVA');
        const offsetSec = window.activePreviewOffsetSeconds || 0;

        try {
            const url = `/api/chart/${nativeId}/svg?varga=${varga}&mode=${mode}&root=${root}&style=${style}&outer=${outer}&d10_mode=${d10Mode}&d24_mode=${d24Mode}&nakshatra_system=${nakshatra}&offset_seconds=${offsetSec}`;
            const res = await fetch(url);
            return await res.json();
        } catch (e) {
            console.error("AstraAPI: fetchChartSvg failed", e);
            return null;
        }
    }
};

// Global Exposure & function wrappers for backwards compatibility
if (typeof window !== 'undefined') {
    window.AstraAPI = AstraAPI;
    window.loadChart = (id) => AstraAPI.loadChart(id);
    window.saveNative = (isUpdate) => AstraAPI.saveNative(isUpdate);
    window.deleteCurrentNative = () => {
        const id = document.getElementById('editNativeId')?.value;
        const name = document.getElementById('newName')?.value || 'this person';
        if (!id) {
            alert("No person selected to delete.");
            return;
        }
        if (confirm(`Are you sure you want to delete "${name}" permanently?`)) {
            AstraAPI.deleteNative(id);
        }
    };
    window.fetchAllNativesFromServer = () => AstraAPI.fetchAllNatives();
}
