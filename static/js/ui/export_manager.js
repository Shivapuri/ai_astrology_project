/**
 * Astra PDF & Print Export Manager
 * 
 * Handles PDF export presets (Master Dossier, Standard, Single Page, Current View),
 * option toggles, browser print preview, and communication with /api/export_pdf.
 */

(function() {
    function onExportPresetChange(preset) {
        const secToggle = document.getElementById('exportSectionsToggle');
        const tblToggle = document.getElementById('exportTablesToggle');
        const visToggle = document.getElementById('exportVisualOptions');
        if (preset === 'current_view') {
            if (secToggle) secToggle.style.opacity = '0.5';
            if (tblToggle) tblToggle.style.opacity = '0.5';
            if (visToggle) visToggle.style.opacity = '0.5';
        } else {
            if (secToggle) secToggle.style.opacity = '1';
            if (tblToggle) tblToggle.style.opacity = '1';
            if (visToggle) visToggle.style.opacity = '1';
            if (preset === 'master_dossier_a4') {
                const bw = document.getElementById('expIncBiwheel');
                if (bw) bw.checked = true;
            }
        }
    }

    async function triggerPdfExport(previewOnly = false) {
        const currentData = window.currentChartData;
        if (!currentData) {
            alert("Please load a birth chart first before exporting.");
            return;
        }

        const preset = document.querySelector('input[name="exportPreset"]:checked')?.value || 'master_dossier_a4';
        
        // If current view selected and preview requested, open native print
        if (preset === 'current_view' && previewOnly) {
            if (typeof window.closeExportModal === 'function') window.closeExportModal();
            window.print();
            return;
        }

        const chartStyle = document.getElementById('exportChartStyle')?.value || 'north';
        const notation = document.getElementById('exportNotation')?.value || 'symbol';
        const pageSize = (preset === 'master_a3') ? 'A3' : 'A4';

        const additionalVargas = [];
        if (document.getElementById('expIncD2')?.checked) additionalVargas.push('D2');
        if (document.getElementById('expIncD3')?.checked) additionalVargas.push('D3');
        if (document.getElementById('expIncD12')?.checked) additionalVargas.push('D12');
        if (document.getElementById('expIncD24')?.checked) additionalVargas.push('D24');

        const currentNakshatraSystem = window.currentNakshatraSystem || 'ERNST_DHRUVA';

        const options = {
            preset: preset,
            page_size: pageSize,
            landscape: true,
            chart_style: chartStyle,
            notation: notation,
            include_d1: document.getElementById('expIncD1')?.checked ?? true,
            include_biwheel: document.getElementById('expIncBiwheel')?.checked ?? true,
            biwheel_outer: document.getElementById('exportBiwheelOuter')?.value || 'D9',
            include_d9: document.getElementById('expIncD9')?.checked ?? true,
            include_d10: document.getElementById('expIncD10')?.checked ?? true,
            include_d7: document.getElementById('expIncD7')?.checked ?? true,
            include_dual_vargas: document.getElementById('expIncDualVargas')?.checked ?? true,
            include_master_diagnostics: document.getElementById('expIncMasterDiagnostics')?.checked ?? true,
            include_d9_diagnostics: document.getElementById('expIncMasterDiagnostics')?.checked ?? true,
            include_d10_diagnostics: document.getElementById('expIncMasterDiagnostics')?.checked ?? true,
            include_diagnostic_key: document.getElementById('expIncDiagnosticKey')?.checked ?? true,
            include_timeline: document.getElementById('expIncTimeline')?.checked ?? true,
            include_yogas: document.getElementById('expIncYogas')?.checked ?? true,
            include_placements: document.getElementById('expIncPlacements')?.checked ?? true,
            include_cusps: document.getElementById('expIncCusps')?.checked ?? true,
            include_dignities: document.getElementById('expIncDignities')?.checked ?? true,
            include_avasthas: document.getElementById('expIncAvasthas')?.checked ?? true,
            include_lajjitadi: document.getElementById('expIncAvasthas')?.checked ?? true,
            include_yoga_judgment: document.getElementById('expIncYogaJudgment')?.checked ?? true,
            include_shadbala: document.getElementById('expIncShadbala')?.checked ?? true,
            include_dasha: true,
            include_vimshopaka: document.getElementById('expIncVimshopaka')?.checked ?? true,
            additional_vargas: additionalVargas,
            nakshatra_system: currentNakshatraSystem
        };

        const nativeId = document.getElementById('editNativeId')?.value || document.getElementById('nativeSelect')?.value;

        const payload = {
            native_id: nativeId,
            chart_data: currentData,
            options: options,
            nakshatra_system: currentNakshatraSystem
        };

        const statusMsg = document.getElementById('exportStatusMsg');
        const exportBtn = document.getElementById('btnDoExportPdf');

        if (previewOnly) {
            try {
                if (statusMsg) statusMsg.style.display = 'flex';
                const response = await fetch('/api/export_preview', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const html = await response.text();
                const previewWindow = window.open('', '_blank');
                if (previewWindow) {
                    previewWindow.document.write(html);
                    previewWindow.document.close();
                } else {
                    alert('Pop-up blocked. Please allow pop-ups for this site to view the print preview.');
                }
            } catch (err) {
                alert('Failed to generate print preview: ' + err);
            } finally {
                if (statusMsg) statusMsg.style.display = 'none';
            }
        } else {
            try {
                if (statusMsg) statusMsg.style.display = 'flex';
                if (exportBtn) exportBtn.disabled = true;
                
                const response = await fetch('/api/export_pdf', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });

                if (!response.ok) {
                    const errJson = await response.json();
                    throw new Error(errJson.error || 'Server error generating PDF');
                }

                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.style.display = 'none';
                a.href = url;
                const subjectName = (currentData.subject_info?.name || 'Chart').replace(/[^a-zA-Z0-9_-]/g, '_');
                a.download = `${subjectName}_Astra_Master_Plan.pdf`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                a.remove();
                if (typeof window.closeExportModal === 'function') window.closeExportModal();
            } catch (err) {
                alert('PDF Export Error: ' + err.message);
            } finally {
                if (statusMsg) statusMsg.style.display = 'none';
                if (exportBtn) exportBtn.disabled = false;
            }
        }
    }

    window.onExportPresetChange = onExportPresetChange;
    window.triggerPdfExport = triggerPdfExport;
})();
