/**
 * Astra Modal Manager
 * 
 * Consolidates modal dialog opening, closing, backdrop clicks,
 * and Escape key handling across all modals in the application.
 */

class ModalManager {
    constructor() {
        this.activeModals = [];
        this.init();
    }

    init() {
        // Universal Escape key handler
        window.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                if (this.activeModals.length > 0) {
                    const topModal = this.activeModals[this.activeModals.length - 1];
                    this.closeModal(topModal);
                    e.stopPropagation();
                } else {
                    // Check if any modal is currently visible
                    const modals = [
                        'settingsModal', 'exportPdfModal', 'maximizeModal',
                        'widgetMaximizeModal', 'kalaMenuModal', 'shodasaVargasModal',
                        'openChartModal', 'addPersonModal'
                    ];
                    for (const id of modals) {
                        const el = document.getElementById(id);
                        if (el && el.style.display && el.style.display !== 'none') {
                            this.closeModal(id);
                        }
                    }
                }
            }
        });

        // Universal Backdrop click listener
        document.addEventListener('click', (e) => {
            if (e.target.classList && e.target.classList.contains('modal-overlay')) {
                // If clicked directly on the overlay backdrop
                this.closeModal(e.target.id);
            }
        });
    }

    openModal(modalId) {
        const modal = document.getElementById(modalId);
        if (!modal) return;

        // Custom display type (flex for standard overlays)
        modal.style.display = 'flex';
        if (!this.activeModals.includes(modalId)) {
            this.activeModals.push(modalId);
        }
    }

    closeModal(modalId) {
        const modal = typeof modalId === 'string' ? document.getElementById(modalId) : modalId;
        if (!modal) return;

        modal.style.display = 'none';
        const id = modal.id;
        this.activeModals = this.activeModals.filter(m => m !== id);

        if (id === 'maximizeModal' && typeof window.currentMaximized !== 'undefined') {
            window.currentMaximized = null;
        }
    }

    closeAllModals() {
        const modals = [
            'settingsModal', 'exportPdfModal', 'maximizeModal',
            'widgetMaximizeModal', 'kalaMenuModal', 'shodasaVargasModal',
            'openChartModal', 'addPersonModal'
        ];
        modals.forEach(id => this.closeModal(id));
        this.activeModals = [];
    }
}

// Singleton instance
const modalManager = new ModalManager();

// Global convenience functions for backwards compatibility with HTML inline onclick handlers
function openSettingsModal() {
    // Synchronize modal state with current settings
    const notation = (window.astraStore && window.astraStore.state.notation) || window.currentNotation || 'symbol';
    const radioNot = document.getElementById(`radio-${notation}`);
    if (radioNot) radioNot.checked = true;

    const signCheck = document.getElementById('modalToggleSigns');
    if (signCheck && typeof window.showSiSigns !== 'undefined') {
        signCheck.checked = window.showSiSigns;
    }
    
    const d10 = (window.astraStore && window.astraStore.state.d10Mode) || window.currentD10Mode || 'reverse';
    const radioRev = document.getElementById('radio-d10-reverse');
    const radioDir = document.getElementById('radio-d10-direct');
    if (radioRev && radioDir) {
        if (d10 === 'direct') radioDir.checked = true;
        else radioRev.checked = true;
    }

    const nak = (window.astraStore && window.astraStore.state.nakshatraSystem) || window.currentNakshatraSystem || 'ERNST_DHRUVA';
    const radioDhruva = document.getElementById('radio-nak-dhruva');
    const radioChitra = document.getElementById('radio-nak-chitra');
    if (radioDhruva && radioChitra) {
        if (nak === 'VIC_CHITRA') radioChitra.checked = true;
        else radioDhruva.checked = true;
    }
    
    modalManager.openModal('settingsModal');
}

function closeSettingsModal(e) {
    if (!e || e.target === document.getElementById('settingsModal') || e.target.classList.contains('modal-close-btn') || e.target.innerText === 'Done' || e.target.innerText === '×') {
        modalManager.closeModal('settingsModal');
    }
}

function openExportModal() {
    const styleSel = document.getElementById('exportChartStyle');
    const notSel = document.getElementById('exportNotation');
    if (styleSel) {
        let activeStyle = 'north';
        if (document.getElementById('view-south')?.classList.contains('active')) activeStyle = 'south';
        else if (document.getElementById('view-circular')?.classList.contains('active')) activeStyle = 'circular';
        styleSel.value = activeStyle;
    }
    if (notSel && typeof window.currentNotation !== 'undefined') {
        notSel.value = window.currentNotation;
    }
    modalManager.openModal('exportPdfModal');
}

function closeExportModal(e) {
    const modal = document.getElementById('exportPdfModal');
    if (!modal) return;
    if (!e || e.target === modal || e.target.classList.contains('modal-close-btn') || e.target.innerText === 'Cancel' || e.target.innerText === '×') {
        modalManager.closeModal('exportPdfModal');
    }
}

function closeMaximizeModal(e) {
    if (!e || e.target === document.getElementById('maximizeModal') || e.target.closest('.modal-close-btn') || e.target.closest('.btn-close-floating')) {
        modalManager.closeModal('maximizeModal');
    }
}

function closeWidgetMaximizeModal(e) {
    if (!e || e.target === document.getElementById('widgetMaximizeModal') || e.target.closest('.modal-close-btn') || e.target.closest('.btn-close-floating')) {
        modalManager.closeModal('widgetMaximizeModal');
    }
}

function openKalaMenu(x, y) {
    const modal = document.getElementById('kalaMenuModal');
    if (!modal) return;
    modal.style.display = 'flex';
}

function closeKalaMenu() {
    modalManager.closeModal('kalaMenuModal');
}

function openShodasaVargasModal() {
    modalManager.openModal('shodasaVargasModal');
    if (typeof window.renderShodasaGrid === 'function') {
        window.renderShodasaGrid();
    }
}

function closeShodasaVargasModal() {
    modalManager.closeModal('shodasaVargasModal');
}

function closeOpenChartModal() {
    modalManager.closeModal('openChartModal');
}

// Attach globally
if (typeof window !== 'undefined') {
    window.ModalManager = ModalManager;
    window.modalManager = modalManager;
    window.openSettingsModal = openSettingsModal;
    window.closeSettingsModal = closeSettingsModal;
    window.openExportModal = openExportModal;
    window.closeExportModal = closeExportModal;
    window.closeMaximizeModal = closeMaximizeModal;
    window.closeWidgetMaximizeModal = closeWidgetMaximizeModal;
    window.openKalaMenu = openKalaMenu;
    window.closeKalaMenu = closeKalaMenu;
    window.openShodasaVargasModal = openShodasaVargasModal;
    window.closeShodasaVargasModal = closeShodasaVargasModal;
    window.closeOpenChartModal = closeOpenChartModal;
}
