/**
 * Astra Qualitative Avasthas Calculation Widget
 * 
 * Computes and renders Qualitative Avasthas (Jagradadi, Baladi, Deeptadi, Lajjitadi)
 * across D1 and divisional vargas, plus Shayanadi states.
 */

(function() {
    const AVASHTHA_MEANINGS = {
        "Deepta (Radiant)": "It experiences supreme confidence and noble clarity, effortlessly expressing its highest virtues and joy.",
        "Pramudita (Joyous)": "It feels inspired, aligned with its true purpose, and cheerful in taking action.",
        "Svastha (Confident)": "It feels secure, relaxed, and fully in control of its own domain.",
        "Mudita (Rejoicing)": "It feels welcomed, appreciated, and happy with its surroundings.",
        "Shanta (Serene)": "It enjoys a harmonious, cooperative atmosphere without pressure.",
        "Dina (Scarce / Depressed)": "It feels modest, having to scrape by with basic resources and lacking special backing.",
        "Dukhita (Miserable)": "It feels unwelcome and uneasy, encountering emotional struggle and grief.",
        "Khala (Cruel)": "It feels defensive and harsh, having to fight through severe obstacles and hostility.",
        "Bhita (Alarmed)": "Having hit rock bottom, it feels exposed and insecure, panicked into dealing with pressing crises or deficiencies.",
        "Garvita (Proud)": "It feels dignified, self-respecting, and noble, powerfully enriching its house.",
        "Lajjita (Ashamed)": "It brings a sense of embarrassment, shame, or reluctance, causing hesitation in taking worthy action.",
        "Kshudhita (Starved)": "It feels starved of essential nourishment and resources, severely damaging or draining its affairs.",
        "Trushita (Thirsty)": "It feels parched and emotionally unfulfilled, leaving the native craving satisfaction.",
        "Mudita (Delighted)": "It feels loved and abundantly nourished, allowing its house to produce full, joyful blessings.",
        "Kshobhita (Agitated)": "It suffers extreme agitation and conflict, tending to destroy or destabilize its house."
    };

    function escapeTooltipAttr(str) {
        if (!str) return '';
        return String(str).replace(/"/g, '&quot;').replace(/'/g, '&#39;');
    }

    function formatSentence(planet, state, condition, category) {
        if (!state || state === "N/A" || state === "Neutral (None)" || state === "Unknown") return "";
        let lookupState = state;
        
        if (category === "Bala") {
            return `${planet} is in a ${state} state (${condition}). This determines its sheer physical vitality and stamina to produce results.`;
        } else if (category === "Jagrat") {
            return `${planet} is ${state} (${condition}). This reflects its level of consciousness and readiness to act.`;
        } else if (category === "Deeptadi") {
            let meaning = AVASHTHA_MEANINGS[lookupState] || "";
            return `While producing results, ${planet} operates in a ${state} mood (${condition.toLowerCase()}), coloring how the event will ultimately feel. ${meaning}`;
        } else if (category === "Lajjitadi") {
            let meaning = AVASHTHA_MEANINGS[lookupState] || "";
            return `${planet} is ultimately affected by its ${state} state, indicating concrete help or hindrance from others (${condition}). ${meaning}`;
        }
        return condition;
    }

    function updateAvasthasCalcTableForCell(cell, chartData) {
        const currentData = chartData || window.currentChartData;
        const vargaSelect = cell.querySelector('.varga-select');
        const varga = vargaSelect ? vargaSelect.value : 'D1';
        const titleEl = cell.querySelector('.avastha-calc-title') || cell.querySelector('#avasthaCalcTitle');
        if (titleEl) {
            titleEl.textContent = `${varga} - Qualitative Avasthas`;
        }

        const tbody = cell.querySelector('.avasthas-calc-table tbody') || cell.querySelector('tbody');
        if (!tbody || !currentData || !currentData.vargas || !currentData.vargas[varga]) return;
        tbody.innerHTML = '';

        const planets = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn'];
        const avasthaTypes = [
            { key: 'jagrat', label: 'Jagradādi', desc: 'Alertness / Consciousness: Jagrata (Awake = 100%), Swapna (Dreaming = 50%), Sushupti (Sleeping = minimal).' },
            { key: 'bala', label: 'Bālādi', desc: 'Age / Physical Vitality: Bāla (Infant = 25%), Kumāra (Youth = 50%), Yuva (Prime Adult = 100%), Vṛddha (Elder = minimal), Mṛta (Dormant = 0%).' },
            { key: 'deeptadi', label: 'Dīptādi', desc: 'Dignity Radiance / Mental Mood: 9 moods from Dīpta (Exalted radiance) to Swastha (Content) to Kopa/Dina (Afflicted).' },
            { key: 'lajjitadi', label: 'Lajjitādi', desc: 'Feeling States & Psychological Complexes: Garvita (Proud), Lajjita (Ashamed), Kshudhita (Starved), Kshobhita (Agitated), Mudita (Delighted), Trushita (Thirsty).' }
        ];

        const vargaGrahas = currentData.vargas[varga].grahas;

        avasthaTypes.forEach(avType => {
            const tr = document.createElement('tr');
            let htmlStr = `<td class="tooltip-target" data-tooltip="<strong>${avType.label} Avasthas</strong><br>${avType.desc}" style="cursor:help;"><strong>${avType.label}</strong></td>`;

            planets.forEach(p => {
                if (!vargaGrahas[p] || !vargaGrahas[p].avasthas) {
                    htmlStr += `<td>-</td>`;
                    return;
                }
                const avData = vargaGrahas[p].avasthas[avType.key];
                let stateStr = '-';
                let cellTip = '';

                if (Array.isArray(avData)) {
                    stateStr = avData.length > 0 ? avData.map(a => a.state.split(' ')[0]).join(',<br/>') : '-';
                    cellTip = `<strong>${p} — ${avType.label}</strong><br>` + avData.map(a => {
                        let meaning = AVASHTHA_MEANINGS[a.state] || '';
                        return `• <strong>${a.state}:</strong> ${a.condition}${meaning ? '<br><em>' + meaning + '</em>' : ''}`;
                    }).join('<br>');
                } else if (avData && avData.state) {
                    stateStr = avData.state.split(' ')[0];
                    let meaning = AVASHTHA_MEANINGS[avData.state] || '';
                    cellTip = `<strong>${p} — ${avType.label}: ${avData.state}</strong><br>• <strong>Condition:</strong> ${avData.condition || ''}${meaning ? '<br>• <em>' + meaning + '</em>' : ''}`;
                }

                htmlStr += `<td class="tooltip-target" data-tooltip="${cellTip}" style="cursor: help;">${stateStr}</td>`;
            });

            tr.innerHTML = htmlStr;
            tbody.appendChild(tr);
        });
    }

    function updateAvasthasCalcTable(vargaName) {
        document.querySelectorAll('.grid-cell[data-widget="avasthas-calc"]').forEach(cell => {
            if (vargaName) {
                const select = cell.querySelector('.varga-select');
                if (select) select.value = vargaName;
            }
            updateAvasthasCalcTableForCell(cell);
        });
    }

    function updateAvasthasTable(varga) {
        const tbody = document.querySelector('#avasthasTable tbody');
        const shWidget = document.getElementById('shayanadiWidget');
        if (tbody) tbody.innerHTML = '';
        if (shWidget) shWidget.innerHTML = '';
        
        const currentData = window.currentChartData;
        if (!currentData || !currentData.vargas || !currentData.vargas[varga]) return;

        const grahas = currentData.vargas[varga].grahas;
        const planetsOrder = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"];
        
        function getBarColor(val) {
            if (val >= 1.0) return "var(--status-benefic)";
            if (val >= 0.5) return "var(--status-neutral)";
            if (val > 0) return "var(--status-alert)";
            return "var(--text-subtle)";
        }

        planetsOrder.forEach(p => {
            if (!grahas[p] || !grahas[p].avasthas) return;
            const av = grahas[p].avasthas;
            
            // Bala
            let balaState = av.bala ? av.bala.state : "N/A";
            let balaVal = av.bala ? av.bala.strength : 0;
            let balaPct = Math.round(balaVal * 100);
            let balaCond = av.bala && av.bala.condition ? av.bala.condition : "";
            let balaTooltip = formatSentence(p, balaState, balaCond, "Bala");
            
            const pePlanets = (currentData.planetary_evaluation && currentData.planetary_evaluation.planets) || {};
            const peP = pePlanets[p] || {};

            // Jagrat
            let jagratState = av.jagrat ? av.jagrat.state : "N/A";
            let jagratVal = av.jagrat ? av.jagrat.alertness : 0;
            let jagratCond = av.jagrat && av.jagrat.condition ? av.jagrat.condition : "";
            if (peP.jagradaadi) {
                jagratState = peP.jagradaadi.badge || peP.jagradaadi.state;
                jagratVal = peP.jagradaadi.multiplier;
                jagratCond = peP.jagradaadi.house_management || "";
            }
            let jagratPct = Math.round(jagratVal * 100);
            let jagratTooltip = formatSentence(p, jagratState, jagratCond, "Jagrat");
            
            // Deeptadi
            let deepState = "N/A";
            let deepTooltip = "";
            if (peP.deepthaadi) {
                deepState = peP.deepthaadi.badge || peP.deepthaadi.state;
                deepTooltip = `<strong>${peP.deepthaadi.icon || '👑'} Deeptādi Mood: ${peP.deepthaadi.state}</strong><br>• Condition: ${peP.deepthaadi.condition}<br>• Meaning: ${peP.deepthaadi.meaning}`;
            } else if (av.deeptadi) {
                deepState = av.deeptadi.state || "N/A";
                let deepCond = av.deeptadi.condition || "";
                deepTooltip = formatSentence(p, deepState, deepCond, "Deeptadi");
            }
            
            // Lajjitadi
            let lajjitadiHtml = "";
            if (peP.calibrated_lajjitadi && Array.isArray(peP.calibrated_lajjitadi) && peP.calibrated_lajjitadi.length > 0) {
                lajjitadiHtml = peP.calibrated_lajjitadi.map(item => {
                    const lTooltip = `<strong>${item.icon} ${item.state}</strong><br>• Condition: ${item.condition}<br>• Severity: ${item.severity} (Intensity: ${(item.effective_intensity * 100).toFixed(0)}%)<br>• Source: Vol 2 Ch. 10 & 11`;
                    return `<span class="badge tooltip-target" style="background:var(--bg-surface); border:1px solid var(--border-subtle); font-size:9.5px; margin-right:3px;" data-tooltip="${escapeTooltipAttr(lTooltip)}">${item.badge}</span>`;
                }).join(" ");
            } else if (av.lajjitadi && Array.isArray(av.lajjitadi)) {
                lajjitadiHtml = av.lajjitadi.map(item => {
                    if (typeof item === 'object') {
                        let lTooltip = formatSentence(p, item.state, item.condition, "Lajjitadi");
                        return `<span class="tooltip-target" data-tooltip="${lTooltip}">${item.state}</span>`;
                    } else {
                        return `<span>${item}</span>`;
                    }
                }).join(", ");
            }
            
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><strong>${p}</strong></td>
                <td>
                    <div style="display: flex; align-items: center;" class="tooltip-target" data-tooltip="${balaTooltip}">
                        <div class="avastha-bar-container" style="width: 40px; height: 6px; margin-right: 8px; background-color: var(--border-subtle); border-radius: 3px; overflow: hidden;">
                            <div style="width: ${balaPct}%; height: 100%; background-color: ${getBarColor(balaVal)}"></div>
                        </div>
                        <span>${balaState}</span>
                    </div>
                </td>
                <td>
                    <div style="display: flex; align-items: center;" class="tooltip-target" data-tooltip="${jagratTooltip}">
                        <div class="avastha-bar-container" style="width: 40px; height: 6px; margin-right: 8px; background-color: var(--border-subtle); border-radius: 3px; overflow: hidden;">
                            <div style="width: ${jagratPct}%; height: 100%; background-color: ${getBarColor(jagratVal)}"></div>
                        </div>
                        <span>${jagratState}</span>
                    </div>
                </td>
                <td><span class="tooltip-target" data-tooltip="${deepTooltip}">${deepState}</span></td>
                <td>${lajjitadiHtml}</td>
            `;
            if (tbody) tbody.appendChild(tr);
            
            // Shayanadi
            if (av.shayanadi) {
                const shItem = document.createElement('div');
                shItem.className = 'shayanadi-item tooltip-target';
                
                let shState = typeof av.shayanadi === 'object' ? av.shayanadi.state : av.shayanadi;
                let shSub = typeof av.shayanadi === 'object' ? av.shayanadi.sub_state : '';
                let shMeaning = typeof av.shayanadi === 'object' && av.shayanadi.meaning ? av.shayanadi.meaning : '';
                let shSubDesc = typeof av.shayanadi === 'object' && av.shayanadi.sub_state_description ? av.shayanadi.sub_state_description : '';
                
                let titleStr = '';
                if (shState && shMeaning) titleStr += `${p} seizes your mind with ${shState}. ${shMeaning}`;
                if (shSubDesc) titleStr += `\nModified by ${shSub}: ${shSubDesc}`;
                
                let shDisp = shSub ? `${shState} - <em>${shSub}</em>` : shState;
                shItem.innerHTML = `<strong>${p}</strong>: ${shDisp}`;
                shItem.setAttribute('data-tooltip', titleStr);

                if (shWidget) shWidget.appendChild(shItem);
            }
        });
    }

    if (window.widgetRegistry) {
        window.widgetRegistry.register('avasthas-calc', {
            id: 'avasthas-calc',
            title: 'Qualitative Avasthas',
            icon: '🧘',
            category: 'Strengths',
            onUpdate: function(cell, chartData) {
                updateAvasthasCalcTableForCell(cell, chartData);
            }
        });
    }

    window.AVASHTHA_MEANINGS = AVASHTHA_MEANINGS;
    window.escapeTooltipAttr = escapeTooltipAttr;
    window.formatSentence = formatSentence;
    window.updateAvasthasCalcTableForCell = updateAvasthasCalcTableForCell;
    window.updateAvasthasCalcTable = updateAvasthasCalcTable;
    window.updateAvasthasTable = updateAvasthasTable;
})();
