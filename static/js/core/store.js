/**
 * Astra Centralized State Store & Event Bus
 * 
 * Provides an observable state container for astrological chart state,
 * active vargas, calculation modes, time stepper preview, and selection.
 */

class Store {
    constructor() {
        this.listeners = new Map();
        this.state = {
            currentNative: null,
            chartData: null,
            svgs: null,
            activeVarga: 'D1',
            activeStyle: 'south',
            previewOffsetSeconds: 0,
            previewDate: null,
            previewTime: null,
            selectedEntity: null,
            d10Mode: localStorage.getItem('astra_d10_mode') || 'reverse',
            d24Mode: localStorage.getItem('astra_d24_mode') || 'reverse',
            d2Mode: localStorage.getItem('astra_d2_mode') || 'parashari',
            trimsamsaMode: localStorage.getItem('astra_trimsamsa_mode') || 'parashari',
            nakshatraSystem: localStorage.getItem('astra_nakshatra_system') || 'ERNST_DHRUVA',
            debilitationMode: localStorage.getItem('astra_debilitation_mode') || 'kala_degree',
            notation: localStorage.getItem('astra_notation') || 'symbol',
            showSiSigns: localStorage.getItem('astra_show_si_signs') !== 'false',
            showNakshatras: localStorage.getItem('astra_show_nakshatras') === 'true',
            circularWheelMode: localStorage.getItem('astra_circular_wheel_mode') || 'nakshatras'
        };
    }

    getState() {
        return this.state;
    }

    setState(updates = {}) {
        const prevState = { ...this.state };
        this.state = { ...this.state, ...updates };

        // Keep backward-compatible window variables synchronized
        if (updates.chartData !== undefined) {
            window.currentChartData = updates.chartData;
        }
        if (updates.svgs !== undefined) {
            window.currentSvgs = updates.svgs;
        }
        if (updates.currentNative !== undefined) {
            window.currentLoadedNative = updates.currentNative;
        }
        if (updates.previewOffsetSeconds !== undefined) {
            window.activePreviewOffsetSeconds = updates.previewOffsetSeconds;
        }
        if (updates.previewTime !== undefined) {
            window.currentPreviewTime = updates.previewTime;
        }
        if (updates.previewDate !== undefined) {
            window.currentPreviewDate = updates.previewDate;
        }
        if (updates.d10Mode !== undefined) {
            window.currentD10Mode = updates.d10Mode;
            localStorage.setItem('astra_d10_mode', updates.d10Mode);
        }
        if (updates.d24Mode !== undefined) {
            window.currentD24Mode = updates.d24Mode;
            localStorage.setItem('astra_d24_mode', updates.d24Mode);
        }
        if (updates.d2Mode !== undefined) {
            window.currentD2Mode = updates.d2Mode;
            localStorage.setItem('astra_d2_mode', updates.d2Mode);
        }
        if (updates.trimsamsaMode !== undefined) {
            window.currentTrimsamsaMode = updates.trimsamsaMode;
            localStorage.setItem('astra_trimsamsa_mode', updates.trimsamsaMode);
        }
        if (updates.nakshatraSystem !== undefined) {
            window.currentNakshatraSystem = updates.nakshatraSystem;
            localStorage.setItem('astra_nakshatra_system', updates.nakshatraSystem);
        }
        if (updates.debilitationMode !== undefined) {
            window.currentDebilitationMode = updates.debilitationMode;
            localStorage.setItem('astra_debilitation_mode', updates.debilitationMode);
        }
        if (updates.notation !== undefined) {
            window.currentNotation = updates.notation;
            localStorage.setItem('astra_notation', updates.notation);
        }
        if (updates.showNakshatras !== undefined) {
            window.currentShowNakshatras = updates.showNakshatras;
            localStorage.setItem('astra_show_nakshatras', updates.showNakshatras);
        }
        if (updates.circularWheelMode !== undefined) {
            window.currentCircularWheelMode = updates.circularWheelMode;
            localStorage.setItem('astra_circular_wheel_mode', updates.circularWheelMode);
        }

        // Notify specific keys and general state change
        for (const [key, value] of Object.entries(updates)) {
            if (prevState[key] !== value) {
                this.emit(`change:${key}`, value, prevState[key]);
            }
        }
        this.emit('change', this.state, prevState);
    }

    on(event, callback) {
        if (!this.listeners.has(event)) {
            this.listeners.set(event, new Set());
        }
        this.listeners.get(event).add(callback);
        return () => this.off(event, callback);
    }

    off(event, callback) {
        if (this.listeners.has(event)) {
            this.listeners.get(event).delete(callback);
        }
    }

    emit(event, ...args) {
        if (this.listeners.has(event)) {
            for (const cb of Array.from(this.listeners.get(event))) {
                try {
                    cb(...args);
                } catch (err) {
                    console.error(`Store event error [${event}]:`, err);
                }
            }
        }
    }
}

// Global Singleton
const store = new Store();

// Backward compatibility bridge
if (typeof window !== 'undefined') {
    window.astraStore = store;
    window.currentD10Mode = store.state.d10Mode;
    window.currentD24Mode = store.state.d24Mode;
    window.currentD2Mode = store.state.d2Mode;
    window.currentTrimsamsaMode = store.state.trimsamsaMode;
    window.currentNakshatraSystem = store.state.nakshatraSystem;
    window.currentNotation = store.state.notation;
    window.showSiSigns = store.state.showSiSigns;
    window.currentCircularWheelMode = store.state.circularWheelMode;
    window.currentChartData = null;
    window.currentSvgs = null;
    window.currentLoadedNative = null;
    window.activePreviewOffsetSeconds = 0;
}
