/**
 * Astra AI Text & Markdown Export Manager
 * 
 * Manages the AI Text Export modal lifecycle:
 * - Formats complete Master Graha Diagnostics, Vargas, Cusps, Dashas, and Yogas
 * - Communicates with /api/export_text
 * - Provides live preview, token/word counter, one-click copy, and file downloads (.md/.txt)
 */

(function() {
    let currentExportText = "";
    let currentExportFilename = "Astra_Chart_AI_Prompt.md";

    function onTextExportPresetChange(preset) {
        const promptHdr = document.getElementById('expTextPromptHeader');
        const masterDiag = document.getElementById('expTextMasterDiag');
        const arch = document.getElementById('expTextArchetypes');
        const vargas = document.getElementById('expTextVargas');
        const cusps = document.getElementById('expTextCusps');
        const dashas = document.getElementById('expTextDashas');
        const yogas = document.getElementById('expTextYogas');

        if (preset === 'diagnostics_only') {
            if (promptHdr) promptHdr.checked = false;
            if (masterDiag) masterDiag.checked = true;
            if (arch) arch.checked = false;
            if (vargas) vargas.checked = false;
            if (cusps) cusps.checked = false;
            if (dashas) dashas.checked = false;
            if (yogas) yogas.checked = false;
        } else if (preset === 'summary') {
            if (promptHdr) promptHdr.checked = false;
            if (masterDiag) masterDiag.checked = true;
            if (arch) arch.checked = false;
            if (vargas) vargas.checked = false;
            if (cusps) cusps.checked = true;
            if (dashas) dashas.checked = true;
            if (yogas) yogas.checked = false;
        } else {
            // Full dossier (default)
            if (promptHdr) promptHdr.checked = true;
            if (masterDiag) masterDiag.checked = true;
            if (arch) arch.checked = true;
            if (vargas) vargas.checked = true;
            if (cusps) cusps.checked = true;
            if (dashas) dashas.checked = true;
            if (yogas) yogas.checked = true;
        }

        updateTextExportContent();
    }

    async function updateTextExportContent() {
        const previewEl = document.getElementById('exportTextPreview');
        const statsEl = document.getElementById('exportTextStats');
        const chartData = window.currentChartData;

        if (!chartData) {
            if (previewEl) previewEl.value = "Please load a birth chart first before exporting.";
            if (statsEl) statsEl.textContent = "0 words • 0 tokens";
            return;
        }

        if (statsEl) statsEl.textContent = "Generating high-density AI prompt...";

        const preset = document.querySelector('input[name="textExportPreset"]:checked')?.value || 'full';
        const options = {
            preset: preset,
            include_prompt_header: document.getElementById('expTextPromptHeader')?.checked ?? true,
            include_master_diagnostics: document.getElementById('expTextMasterDiag')?.checked ?? true,
            include_archetypes: document.getElementById('expTextArchetypes')?.checked ?? true,
            include_vargas: document.getElementById('expTextVargas')?.checked ?? true,
            include_cusps: document.getElementById('expTextCusps')?.checked ?? true,
            include_dashas: document.getElementById('expTextDashas')?.checked ?? true,
            include_yogas: document.getElementById('expTextYogas')?.checked ?? true
        };

        const nativeId = document.getElementById('editNativeId')?.value || document.getElementById('nativeSelect')?.value;

        try {
            const response = await fetch('/api/export_text', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    native_id: nativeId,
                    chart_data: chartData,
                    options: options
                })
            });

            if (!response.ok) {
                const err = await response.json();
                throw new Error(err.error || 'Server error generating text');
            }

            const data = await response.json();
            currentExportText = data.text || '';
            currentExportFilename = data.filename || 'Astra_Chart_AI_Prompt.md';

            if (previewEl) {
                previewEl.value = currentExportText;
            }

            // Word and Token estimations
            const wordCount = currentExportText.trim().split(/\s+/).filter(Boolean).length;
            const approxTokens = Math.round(currentExportText.length / 3.8);

            if (statsEl) {
                statsEl.textContent = `${wordCount.toLocaleString()} words • ~${approxTokens.toLocaleString()} tokens (Optimal for AI)`;
            }
        } catch (err) {
            console.error("Text export error:", err);
            if (previewEl) previewEl.value = "Failed to generate text export: " + err.message;
            if (statsEl) statsEl.textContent = "Error generating preview";
        }
    }

    function openExportTextModal() {
        const chartData = window.currentChartData;
        if (!chartData) {
            alert("Please load a birth chart first before exporting.");
            return;
        }

        if (window.modalManager) {
            window.modalManager.openModal('exportTextModal');
        } else {
            const modal = document.getElementById('exportTextModal');
            if (modal) modal.style.display = 'flex';
        }

        updateTextExportContent();
    }

    function closeExportTextModal(event) {
        if (event && event.target && event.target !== event.currentTarget) return;
        if (window.modalManager) {
            window.modalManager.closeModal('exportTextModal');
        } else {
            const modal = document.getElementById('exportTextModal');
            if (modal) modal.style.display = 'none';
        }
    }

    async function copyTextToClipboard() {
        const previewEl = document.getElementById('exportTextPreview');
        const textToCopy = (previewEl && previewEl.value) ? previewEl.value : currentExportText;
        const btn = document.getElementById('btnCopyExportText');

        if (!textToCopy) {
            alert("No text available to copy.");
            return;
        }

        try {
            if (navigator.clipboard && navigator.clipboard.writeText) {
                await navigator.clipboard.writeText(textToCopy);
            } else {
                previewEl.select();
                document.execCommand('copy');
            }

            if (btn) {
                const originalHtml = btn.innerHTML;
                const originalBg = btn.style.backgroundColor;
                btn.innerHTML = "✓ Copied to Clipboard!";
                btn.style.backgroundColor = "#16a34a";
                setTimeout(() => {
                    btn.innerHTML = originalHtml;
                    btn.style.backgroundColor = originalBg;
                }, 2000);
            }
        } catch (err) {
            alert("Could not copy automatically: " + err);
        }
    }

    function downloadTextExport(format) {
        const previewEl = document.getElementById('exportTextPreview');
        const textToDownload = (previewEl && previewEl.value) ? previewEl.value : currentExportText;

        if (!textToDownload) {
            alert("No text available to download.");
            return;
        }

        const ext = format === 'txt' ? 'txt' : 'md';
        const mime = format === 'txt' ? 'text/plain;charset=utf-8' : 'text/markdown;charset=utf-8';
        const baseName = currentExportFilename.replace(/\.(md|txt)$/, '');
        const filename = `${baseName}.${ext}`;

        const blob = new Blob([textToDownload], { type: mime });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        URL.revokeObjectURL(url);
        a.remove();
    }

    // Attach to global window scope
    window.openExportTextModal = openExportTextModal;
    window.closeExportTextModal = closeExportTextModal;
    window.onTextExportPresetChange = onTextExportPresetChange;
    window.updateTextExportContent = updateTextExportContent;
    window.copyTextToClipboard = copyTextToClipboard;
    window.downloadTextExport = downloadTextExport;
})();
