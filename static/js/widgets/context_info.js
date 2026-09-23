/**
 * Astra Context Information & Bhava Inspector Widget
 * 
 * Renders in-depth, multi-tabbed astrological analysis for selected
 * planets, houses (bhavas), signs, and nakshatras, integrating live
 * planetary mathematics with the Astra knowledge base.
 */

(function() {
    function escapeHtml(str) {
        if (!str) return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }

    function toggleRawYaml(btn) {
        const card = btn.closest('.astra-props-card');
        if (!card) return;
        const block = card.querySelector('.raw-yaml-block');
        if (!block) return;
        if (block.style.display === 'block') {
            block.style.display = 'none';
            btn.innerHTML = '▾ Show Raw YAML';
        } else {
            block.style.display = 'block';
            btn.innerHTML = '▴ Hide Raw YAML';
        }
    }

    function switchContextInfoTab(containerUid, tabKey) {
        const container = document.getElementById(containerUid);
        if (!container) return;
        
        const btns = container.querySelectorAll('.astra-tab-btn');
        btns.forEach(b => {
            if (b.getAttribute('data-tab') === tabKey) {
                b.classList.add('active');
            } else {
                b.classList.remove('active');
            }
        });

        const panes = container.querySelectorAll('.astra-tab-pane');
        panes.forEach(p => {
            if (p.getAttribute('data-tab-pane') === tabKey) {
                p.classList.add('active');
            } else {
                p.classList.remove('active');
            }
        });

        window._lastContextTab = tabKey;
    }

    function openVargaFromInspector(vargaKey) {
        let chartCell = document.querySelector('.grid-cell.active-cell[data-widget="chart"]');
        if (!chartCell) {
            chartCell = document.querySelector('.grid-cell[data-widget="chart"]');
        }
        if (chartCell) {
            const sel = chartCell.querySelector('.varga-select');
            if (sel) {
                sel.value = vargaKey;
                if (typeof window.updateWidget === 'function') {
                    window.updateWidget(chartCell);
                }
            }
        }
        document.querySelectorAll('.grid-cell[data-widget="info"]').forEach(ic => {
            const s = ic.querySelector('.varga-select');
            if (s) s.value = vargaKey;
            refreshContextInfoForCell(ic);
        });
    }

    function renderYamlPropertiesHeader(type, kbData) {
        if (!kbData || !kbData.properties) return '';
        const p = kbData.properties;
        const rawYaml = kbData.raw_yaml || '';

        let badgesHtml = '';
        let gridHtml = '';

        if (type === 'house') {
            if (p.purushartha) {
                let pClass = 'badge-neutral';
                const pl = p.purushartha.toLowerCase();
                if (pl.includes('dharma')) pClass = 'badge-dharma';
                else if (pl.includes('artha')) pClass = 'badge-artha';
                else if (pl.includes('kama')) pClass = 'badge-kama';
                else if (pl.includes('moksha')) pClass = 'badge-moksha';
                badgesHtml += `<span class="prop-badge ${pClass}">📿 ${escapeHtml(p.purushartha.split(' - ')[0])}</span>`;
            }

            if (Array.isArray(p.structural_classifications)) {
                p.structural_classifications.forEach(sc => {
                    let cClass = 'badge-neutral';
                    const scl = sc.toLowerCase();
                    if (scl.includes('kendra')) cClass = 'badge-kendra';
                    else if (scl.includes('trikona')) cClass = 'badge-trikona';
                    badgesHtml += `<span class="prop-badge ${cClass}">🏛️ ${escapeHtml(sc.split(' (')[0])}</span>`;
                });
            }

            if (p.natural_sign) {
                gridHtml += `<div class="astra-prop-item"><span class="astra-prop-key">Sign / Lord:</span><span class="astra-prop-val">${escapeHtml(p.natural_sign)} (${escapeHtml(p.natural_ruler || '')})</span></div>`;
            }
            if (Array.isArray(p.sthira_karakas) && p.sthira_karakas.length > 0) {
                const karakas = p.sthira_karakas.map(k => typeof k === 'object' ? `${k.planet}` : k).join(', ');
                gridHtml += `<div class="astra-prop-item"><span class="astra-prop-key">Kārakas:</span><span class="astra-prop-val">${escapeHtml(karakas)}</span></div>`;
            }
            if (Array.isArray(p.kalapurusha_anatomy) && p.kalapurusha_anatomy.length > 0) {
                gridHtml += `<div class="astra-prop-item"><span class="astra-prop-key">Anatomy:</span><span class="astra-prop-val">${escapeHtml(p.kalapurusha_anatomy.slice(0, 2).join(', '))}</span></div>`;
            }
            if (p.astra_system_compatibility) {
                gridHtml += `<div class="astra-prop-item"><span class="astra-prop-key">System:</span><span class="astra-prop-val">Whole Sign Container + Campanus Cusp</span></div>`;
            }
        } else if (type === 'planet') {
            if (p.guna) badgesHtml += `<span class="prop-badge badge-guna">🧘 ${escapeHtml(p.guna.split(' (')[0])}</span>`;
            if (p.element) badgesHtml += `<span class="prop-badge badge-element">🔥 ${escapeHtml(p.element.split(' (')[0])}</span>`;
            if (p.caste) badgesHtml += `<span class="prop-badge badge-neutral">🛡️ ${escapeHtml(p.caste.split(' (')[0])}</span>`;
            if (p.gender) badgesHtml += `<span class="prop-badge badge-neutral">⚤ ${escapeHtml(p.gender)}</span>`;

            if (p.exaltation_sign) badgesHtml += `<span class="prop-badge badge-exalted">⬆ Exalted: ${escapeHtml(p.exaltation_sign)}</span>`;
            if (p.debilitation_sign) badgesHtml += `<span class="prop-badge badge-debilitated">⬇ Debilitated: ${escapeHtml(p.debilitation_sign)}</span>`;
            if (p.moolatrikona) badgesHtml += `<span class="prop-badge badge-moola">⚖ Moolatrikona: ${escapeHtml(p.moolatrikona)}</span>`;

            if (Array.isArray(p.natural_karaka) && p.natural_karaka.length > 0) {
                const karakas = p.natural_karaka.slice(0, 3).map(k => k.split(' (')[0]).join(', ');
                gridHtml += `<div class="astra-prop-item"><span class="astra-prop-key">Kārakas:</span><span class="astra-prop-val">${escapeHtml(karakas)}</span></div>`;
            }
            if (p.ruling_sign) {
                gridHtml += `<div class="astra-prop-item"><span class="astra-prop-key">Rulership:</span><span class="astra-prop-val">${escapeHtml(p.ruling_sign)}</span></div>`;
            }
            if (p.dosha) {
                gridHtml += `<div class="astra-prop-item"><span class="astra-prop-key">Dosha:</span><span class="astra-prop-val">${escapeHtml(p.dosha.split(' (')[0])}</span></div>`;
            }
            if (Array.isArray(p.body_parts) && p.body_parts.length > 0) {
                gridHtml += `<div class="astra-prop-item"><span class="astra-prop-key">Body:</span><span class="astra-prop-val">${escapeHtml(p.body_parts.slice(0, 2).join(', '))}</span></div>`;
            }
            if (p.gemstone || p.day) {
                const gems = [p.gemstone ? `Gem: ${p.gemstone}` : '', p.day ? `Day: ${p.day}` : ''].filter(Boolean).join(' | ');
                gridHtml += `<div class="astra-prop-item"><span class="astra-prop-key">Upāya:</span><span class="astra-prop-val">${escapeHtml(gems)}</span></div>`;
            }
        }

        const headerTitle = type === 'house'
            ? `House ${p.house_number || kbData.number} • ${escapeHtml(p.sanskrit_name || kbData.sanskrit_name || '')}`
            : `${escapeHtml(kbData.name || p.planet || '')} (${escapeHtml(p.sanskrit_name || kbData.sanskrit_name || '')})`;

        const archetypeText = p.archetype || kbData.archetype || kbData.title || '';

        return `
            <div class="astra-props-card">
                <div class="astra-props-header">
                    <div class="astra-props-title">🏷️ ${headerTitle}</div>
                    <button type="button" class="raw-yaml-toggle-btn" onclick="toggleRawYaml(this)">▾ Show Raw YAML</button>
                </div>
                ${archetypeText ? `<div class="astra-props-archetype">"${escapeHtml(archetypeText)}"</div>` : ''}
                ${badgesHtml ? `<div class="astra-props-badges">${badgesHtml}</div>` : ''}
                ${gridHtml ? `<div class="astra-props-grid">${gridHtml}</div>` : ''}
                ${rawYaml ? `<div class="raw-yaml-block">${escapeHtml(rawYaml)}</div>` : ''}
            </div>
        `;
    }

    function renderBhavaInspectorHtml(houseId, varga = 'D1', kbData = null) {
        const houseNum = parseInt(String(houseId).replace(/[^0-9]/g, ''), 10) || 1;
        const currentData = window.currentChartData;
        
        // Auto-fetch from knowledge base if not passed
        if (!kbData && window.knowledgeBase && window.knowledgeBase.house) {
            kbData = window.knowledgeBase.house[houseNum];
        }

        const SIGNS = [
            'Aries', 'Taurus', 'Gemini', 'Cancer',
            'Leo', 'Virgo', 'Libra', 'Scorpio',
            'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
        ];
        
        const SIGN_LORDS = {
            'Aries': 'Mars', 'Taurus': 'Venus', 'Gemini': 'Mercury', 'Cancer': 'Moon',
            'Leo': 'Sun', 'Virgo': 'Mercury', 'Libra': 'Venus', 'Scorpio': 'Mars',
            'Sagittarius': 'Jupiter', 'Capricorn': 'Saturn', 'Aquarius': 'Saturn', 'Pisces': 'Jupiter'
        };

        const SIGN_ELEMENTS = {
            'Aries': 'Fire (Agni)', 'Leo': 'Fire (Agni)', 'Sagittarius': 'Fire (Agni)',
            'Taurus': 'Earth (Prithvi)', 'Virgo': 'Earth (Prithvi)', 'Capricorn': 'Earth (Prithvi)',
            'Gemini': 'Air (Vayu)', 'Libra': 'Air (Vayu)', 'Aquarius': 'Air (Vayu)',
            'Cancer': 'Water (Jala)', 'Scorpio': 'Water (Jala)', 'Pisces': 'Water (Jala)'
        };

        const SIGN_MODALITIES = {
            'Aries': 'Movable (Chara)', 'Cancer': 'Movable (Chara)', 'Libra': 'Movable (Chara)', 'Capricorn': 'Movable (Chara)',
            'Taurus': 'Fixed (Sthira)', 'Leo': 'Fixed (Sthira)', 'Scorpio': 'Fixed (Sthira)', 'Aquarius': 'Fixed (Sthira)',
            'Gemini': 'Dual (Dwisvabhava)', 'Virgo': 'Dual (Dwisvabhava)', 'Sagittarius': 'Dual (Dwisvabhava)', 'Pisces': 'Dual (Dwisvabhava)'
        };

        const BHAVA_NAMES = {
            1: { name: 'Tanu Bhāva', theme: 'Physical Self, Vitality & Appearance' },
            2: { name: 'Dhana Bhāva', theme: 'Wealth, Speech, Family & Food' },
            3: { name: 'Sahaja Bhāva', theme: 'Siblings, Courage & Initiative' },
            4: { name: 'Sukha Bhāva', theme: 'Mother, Home, Vehicles & Inner Peace' },
            5: { name: 'Putra Bhāva', theme: 'Children, Intelligence & Purva Punya' },
            6: { name: 'Ari / Shatru Bhāva', theme: 'Obstacles, Health, Debts & Service' },
            7: { name: 'Yuvati / Kalatra Bhāva', theme: 'Spouse, Partnership & Public Relations' },
            8: { name: 'Randhra Bhāva', theme: 'Longevity, Transformation & Hidden Knowledge' },
            9: { name: 'Dharma / Bhagya Bhāva', theme: 'Higher Wisdom, Fortune, Dharma & Guru' },
            10: { name: 'Karma Bhāva', theme: 'Career, Status, Authority & Actions' },
            11: { name: 'Lābha Bhāva', theme: 'Gains, Aspirations, Wealth & Community' },
            12: { name: 'Vyaya Bhāva', theme: 'Liberation (Moksha), Solitude & Loss' }
        };

        const NATURAL_KARAKAS = {
            1: 'Sun (Soul, Vitality, Self)',
            2: 'Jupiter (Wealth), Mercury (Speech)',
            3: 'Mars (Courage, Younger Siblings)',
            4: 'Moon (Mother, Emotional Peace), Venus (Vehicles, Comfort)',
            5: 'Jupiter (Children, Intelligence, Creativity)',
            6: 'Mars (Competitiveness), Saturn (Disease, Hard Labor)',
            7: 'Venus (Spouse, Romantic Partnership)',
            8: 'Saturn (Longevity, Mortality, Vulnerabilities)',
            9: 'Jupiter (Wisdom, Guru), Sun (Father, Cosmic Law)',
            10: 'Sun (Authority), Mercury (Profession), Jupiter (Ethics), Saturn (Labor)',
            11: 'Jupiter (Gains, Expansion, Elder Siblings)',
            12: 'Saturn (Loss, Detachment), Ketu (Spiritual Emancipation)'
        };

        const ARUDHA_NAMES = {
            1: 'AL (Ārūḍha Lagna)', 2: 'A2 (Dhana Pada)', 3: 'A3 (Bhrātri Pada)',
            4: 'A4 (Mātṛ Pada)', 5: 'A5 (Putra Pada)', 6: 'A6 (Śatru Pada)',
            7: 'A7 (Dāra Pada)', 8: 'A8 (Randhra Pada)', 9: 'A9 (Bhāgya Pada)',
            10: 'A10 (Rājya Pada)', 11: 'A11 (Lābha Pada)', 12: 'UL (Upapada Lagna)'
        };

        const VARGA_MAPPING = {
            1: { varga: 'D1', title: 'D1 (Rāśi)', desc: 'Physical Body & Overall Destiny' },
            2: { varga: 'D2', title: 'D2 (Horā)', desc: 'Wealth, Sustenance & Liquid Assets' },
            3: { varga: 'D3', title: 'D3 (Drekkāṇa)', desc: 'Siblings, Energy & Courage' },
            4: { varga: 'D4', title: 'D4 (Caturthāṁśa)', desc: 'Fixed Assets, Real Estate & Home' },
            5: { varga: 'D7', title: 'D7 (Saptāṁśa)', desc: 'Children & Creative Offspring' },
            6: { varga: 'D30', title: 'D30 (Triṁśāṁśa)', desc: 'Adversities, Diseases & Enmity' },
            7: { varga: 'D9', title: 'D9 (Navāṁśa)', desc: 'Spouse, Marriage & Dharma' },
            8: { varga: 'D30', title: 'D30 (Triṁśāṁśa)', desc: 'Hidden Troubles, Arishta & Vulnerability' },
            9: { varga: 'D9', title: 'D9 (Navāṁśa)', desc: 'Higher Dharma, Guru & Spiritual Path' },
            10: { varga: 'D10', title: 'D10 (Daśāṁśa)', desc: 'Career, Professional Achievement & Power' },
            11: { varga: 'D24', title: 'D24 (Caturviṁśāṁśa)', desc: 'Higher Learning, Knowledge & Gains' },
            12: { varga: 'D12', title: 'D12 (Dvādaśāṁśa)', desc: 'Ancestral Lineage & Foreign Residence' }
        };

        const vData = (currentData && currentData.vargas) ? currentData.vargas[varga] : null;
        const lagnaSign = (vData && vData.lagna && vData.lagna.sign) ? vData.lagna.sign : 'Aries';
        const lagnaIdx = SIGNS.indexOf(lagnaSign);
        const houseSignIdx = (lagnaIdx + houseNum - 1) % 12;
        const houseSign = SIGNS[houseSignIdx];
        const bhavaInfo = BHAVA_NAMES[houseNum] || { name: `House ${houseNum}`, theme: '' };

        const occupants = [];
        if (vData && vData.grahas) {
            for (const [pName, pData] of Object.entries(vData.grahas)) {
                if (pData.sign === houseSign) {
                    const deg = pData.degree_0_to_30 !== undefined ? ` (${pData.degree_0_to_30.toFixed(1)}°)` : '';
                    occupants.push(`${pName}${deg}`);
                }
            }
        }

        const lordName = SIGN_LORDS[houseSign] || 'Unknown';
        let lordPlacement = 'Not found';
        let lordDignity = '-';
        let lordHouseNum = null;
        if (vData && vData.grahas && vData.grahas[lordName]) {
            const lg = vData.grahas[lordName];
            const lordSignIdx = SIGNS.indexOf(lg.sign);
            lordHouseNum = ((lordSignIdx - lagnaIdx + 12) % 12) + 1;
            lordDignity = (lg.dignity_breakdown && lg.dignity_breakdown.final_dignity) ? lg.dignity_breakdown.final_dignity : (lg.dignity || 'Neutral');
            const deg = lg.degree_0_to_30 !== undefined ? ` at ${lg.degree_0_to_30.toFixed(1)}°` : '';
            lordPlacement = `House ${lordHouseNum} (${lg.sign}${deg})`;
        }

        let padaSign = 'Unknown';
        let padaHouse = null;
        if (vData && vData.grahas && vData.grahas[lordName]) {
            const lg = vData.grahas[lordName];
            const lordSignIdx = SIGNS.indexOf(lg.sign);
            const dist = (lordSignIdx - houseSignIdx + 12) % 12;
            let rawPadaIdx = (lordSignIdx + dist) % 12;
            const offsetFromHouse = (rawPadaIdx - houseSignIdx + 12) % 12;
            if (offsetFromHouse === 0 || offsetFromHouse === 6) {
                rawPadaIdx = (rawPadaIdx + 9) % 12;
            }
            padaSign = SIGNS[rawPadaIdx];
            padaHouse = ((rawPadaIdx - lagnaIdx + 12) % 12) + 1;
        }

        const arudhaLabel = ARUDHA_NAMES[houseNum] || `A${houseNum}`;
        const targetVarga = VARGA_MAPPING[houseNum] || { varga: 'D1', title: 'D1', desc: '' };

        const containerUid = 'bhava-tabs-' + houseNum + '-' + Math.random().toString(36).substr(2, 6);
        const validTabs = ['live', 'essence', 'condition', 'manifestations', 'diagnosis', 'remedies'];
        const defaultTab = (window._lastContextTab && validTabs.includes(window._lastContextTab)) ? window._lastContextTab : 'live';

        const propsHeader = renderYamlPropertiesHeader('house', kbData);

        const tabsNav = `
            <div class="astra-tab-bar">
                <button type="button" class="astra-tab-btn ${defaultTab === 'live' ? 'active' : ''}" data-tab="live" onclick="switchContextInfoTab('${containerUid}', 'live')">📊 Live Chart</button>
                <button type="button" class="astra-tab-btn ${defaultTab === 'essence' ? 'active' : ''}" data-tab="essence" onclick="switchContextInfoTab('${containerUid}', 'essence')">⚡ Essence & Roots</button>
                <button type="button" class="astra-tab-btn ${defaultTab === 'condition' ? 'active' : ''}" data-tab="condition" onclick="switchContextInfoTab('${containerUid}', 'condition')">⚖️ Condition</button>
                <button type="button" class="astra-tab-btn ${defaultTab === 'manifestations' ? 'active' : ''}" data-tab="manifestations" onclick="switchContextInfoTab('${containerUid}', 'manifestations')">💼 Arenas</button>
                <button type="button" class="astra-tab-btn ${defaultTab === 'diagnosis' ? 'active' : ''}" data-tab="diagnosis" onclick="switchContextInfoTab('${containerUid}', 'diagnosis')">🔗 Diagnosis</button>
                <button type="button" class="astra-tab-btn ${defaultTab === 'remedies' ? 'active' : ''}" data-tab="remedies" onclick="switchContextInfoTab('${containerUid}', 'remedies')">🪔 Remedies</button>
            </div>
        `;

        const liveInspectorHtml = `
            <div class="bhava-inspector-card">
                <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 8px; border-bottom: 1.5px solid var(--border-strong); padding-bottom: 5px;">
                    <span style="font-size: 14px; font-weight: 800; color: var(--text-heading);">House ${houseNum} • ${bhavaInfo.name}</span>
                    <span style="font-size: 11px; background: var(--bg-surface-muted); color: var(--text-heading); padding: 2px 6px; border-radius: 4px; font-weight: 700;">${varga}</span>
                </div>
                <div style="font-size: 11.5px; color: var(--text-muted); margin-bottom: 8px; font-style: italic;">
                    ${bhavaInfo.theme}
                </div>

                <!-- Step 1: The Field -->
                <div class="bhava-step">
                    <div class="bhava-step-title"><span>1. The Field (Kṣetra)</span></div>
                    <div><strong>Sign:</strong> ${houseSign} (${SIGN_ELEMENTS[houseSign] || ''}, ${SIGN_MODALITIES[houseSign] || ''})</div>
                    <div><strong>Occupants:</strong> ${occupants.length > 0 ? `<span style="color: var(--status-benefic-dark); font-weight: 700;">${occupants.join(', ')}</span>` : '<span style="color: var(--text-subtle);">None (Empty House)</span>'}</div>
                </div>

                <!-- Step 2: The Lord -->
                <div class="bhava-step">
                    <div class="bhava-step-title"><span>2. The Lord (Bhāveśa)</span></div>
                    <div><strong>Ruler:</strong> <strong>${lordName}</strong></div>
                    <div><strong>Placement:</strong> ${lordPlacement}</div>
                    <div><strong>Dignity:</strong> <span style="font-weight: 600; color: var(--text-heading);">${lordDignity}</span></div>
                </div>

                <!-- Step 3: Natural Karakas -->
                <div class="bhava-step">
                    <div class="bhava-step-title"><span>3. Natural Karakas (Naisargika)</span></div>
                    <div style="color: var(--text-primary);">${NATURAL_KARAKAS[houseNum] || '—'}</div>
                </div>

                <!-- Step 4: Arudha Pada -->
                <div class="bhava-step">
                    <div class="bhava-step-title"><span>4. Ārūḍha Pada (Manifestation)</span></div>
                    <div><strong>${arudhaLabel}:</strong> Falls in <strong>${padaSign}</strong> ${padaHouse ? `(House ${padaHouse})` : ''}</div>
                </div>

                <!-- Step 5: Corresponding Varga -->
                <div class="bhava-step">
                    <div class="bhava-step-title"><span>5. Divisional Varga Link</span></div>
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 4px;">
                        <div>
                            <strong>${targetVarga.title}</strong>: <span style="font-size: 11px; color: var(--text-muted);">${targetVarga.desc}</span>
                        </div>
                        <button type="button" class="btn-open-varga" onclick="openVargaFromInspector('${targetVarga.varga}')" style="background: var(--text-heading); color: var(--bg-surface); border: none; padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: 700; cursor: pointer; white-space: nowrap;">
                            Open ${targetVarga.varga} ↗
                        </button>
                    </div>
                </div>
            </div>
        `;

        const tabs = (kbData && kbData.tabs) ? kbData.tabs : {};
        const essenceContent = tabs.essence || (kbData ? kbData.content : '<p>No textbook data available.</p>');
        const conditionContent = tabs.condition || '<p>Condition details will appear here.</p>';
        const manifestationsContent = tabs.manifestations || '<p>Manifestations details will appear here.</p>';
        const diagnosisContent = tabs.diagnosis || '<p>Diagnosis details will appear here.</p>';
        const remediesContent = tabs.remedies || '<p>Remedies details will appear here.</p>';

        return `
            <div id="${containerUid}" class="astra-context-container">
                ${propsHeader}
                ${tabsNav}
                <div class="astra-tab-pane ${defaultTab === 'live' ? 'active' : ''}" data-tab-pane="live">
                    ${liveInspectorHtml}
                </div>
                <div class="astra-tab-pane ${defaultTab === 'essence' ? 'active' : ''}" data-tab-pane="essence">
                    <div class="kb-content">${essenceContent}</div>
                </div>
                <div class="astra-tab-pane ${defaultTab === 'condition' ? 'active' : ''}" data-tab-pane="condition">
                    <div class="kb-content">${conditionContent}</div>
                </div>
                <div class="astra-tab-pane ${defaultTab === 'manifestations' ? 'active' : ''}" data-tab-pane="manifestations">
                    <div class="kb-content">${manifestationsContent}</div>
                </div>
                <div class="astra-tab-pane ${defaultTab === 'diagnosis' ? 'active' : ''}" data-tab-pane="diagnosis">
                    <div class="kb-content">${diagnosisContent}</div>
                </div>
                <div class="astra-tab-pane ${defaultTab === 'remedies' ? 'active' : ''}" data-tab-pane="remedies">
                    <div class="kb-content">${remediesContent}</div>
                </div>
            </div>
        `;
    }

    function renderContextInfoHtml(type, id, varga = 'D1') {
        let infoHtml = `<h3>${id}</h3>`;
        let kbData = null;
        if (window.knowledgeBase && window.knowledgeBase[type]) {
            kbData = window.knowledgeBase[type][id];
        }
        
        const currentData = window.currentChartData;

        if (type === 'planet') {
            const mathData = currentData && currentData.vargas && currentData.vargas[varga] && currentData.vargas[varga].grahas && currentData.vargas[varga].grahas[id];
            const vData = currentData && currentData.vargas ? currentData.vargas[varga] : null;
            const lagnaSign = (vData && vData.lagna && vData.lagna.sign) ? vData.lagna.sign : 'Aries';

            const SIGNS = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'];
            const PLANET_SIGNS = {
                'Sun': ['Leo'],
                'Moon': ['Cancer'],
                'Mars': ['Aries', 'Scorpio'],
                'Mercury': ['Gemini', 'Virgo'],
                'Jupiter': ['Sagittarius', 'Pisces'],
                'Venus': ['Taurus', 'Libra'],
                'Saturn': ['Capricorn', 'Aquarius'],
                'Rahu': ['Aquarius'],
                'Ketu': ['Scorpio']
            };

            const ruledHouses = [];
            if (PLANET_SIGNS[id]) {
                const lagnaIdx = SIGNS.indexOf(lagnaSign);
                PLANET_SIGNS[id].forEach(s => {
                    const sIdx = SIGNS.indexOf(s);
                    if (sIdx !== -1 && lagnaIdx !== -1) {
                        const hNum = ((sIdx - lagnaIdx + 12) % 12) + 1;
                        ruledHouses.push(`House ${hNum} (${s})`);
                    }
                });
            }

            if (kbData && kbData.properties) {
                const containerUid = 'planet-tabs-' + id + '-' + Math.random().toString(36).substr(2, 6);
                const validTabs = ['live', 'essence', 'psychology', 'dignity', 'realworld', 'lagnas', 'remedies'];
                const defaultTab = (window._lastContextTab && validTabs.includes(window._lastContextTab)) ? window._lastContextTab : 'live';

                const propsHeader = renderYamlPropertiesHeader('planet', kbData);

                const tabsNav = `
                    <div class="astra-tab-bar">
                        <button type="button" class="astra-tab-btn ${defaultTab === 'live' ? 'active' : ''}" data-tab="live" onclick="switchContextInfoTab('${containerUid}', 'live')">🪐 Live Chart</button>
                        <button type="button" class="astra-tab-btn ${defaultTab === 'essence' ? 'active' : ''}" data-tab="essence" onclick="switchContextInfoTab('${containerUid}', 'essence')">⚡ Essence</button>
                        <button type="button" class="astra-tab-btn ${defaultTab === 'psychology' ? 'active' : ''}" data-tab="psychology" onclick="switchContextInfoTab('${containerUid}', 'psychology')">🧠 Psychology</button>
                        <button type="button" class="astra-tab-btn ${defaultTab === 'dignity' ? 'active' : ''}" data-tab="dignity" onclick="switchContextInfoTab('${containerUid}', 'dignity')">⚖️ Dignity</button>
                        <button type="button" class="astra-tab-btn ${defaultTab === 'realworld' ? 'active' : ''}" data-tab="realworld" onclick="switchContextInfoTab('${containerUid}', 'realworld')">💼 Real-World</button>
                        <button type="button" class="astra-tab-btn ${defaultTab === 'lagnas' ? 'active' : ''}" data-tab="lagnas" onclick="switchContextInfoTab('${containerUid}', 'lagnas')">👑 12 Lagnas</button>
                        <button type="button" class="astra-tab-btn ${defaultTab === 'remedies' ? 'active' : ''}" data-tab="remedies" onclick="switchContextInfoTab('${containerUid}', 'remedies')">🪔 Remedies</button>
                    </div>
                `;

                let liveCardHtml = `
                    <div class="bhava-inspector-card">
                        <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 8px; border-bottom: 1.5px solid var(--border-strong); padding-bottom: 5px;">
                            <span style="font-size: 14px; font-weight: 800; color: var(--text-heading);">${escapeHtml(id)} • Live Placement</span>
                            <span style="font-size: 11px; background: var(--bg-surface-muted); color: var(--text-heading); padding: 2px 6px; border-radius: 4px; font-weight: 700;">${varga}</span>
                        </div>
                `;

                if (mathData) {
                    const nakData = currentData && currentData.nakshatras && currentData.nakshatras.grahas && currentData.nakshatras.grahas[id];
                    const dignityStr = (mathData.dignity_breakdown && mathData.dignity_breakdown.final_dignity) ? mathData.dignity_breakdown.final_dignity : (mathData.dignity || 'Neutral');
                    
                    liveCardHtml += `
                        <div class="bhava-step">
                            <div class="bhava-step-title"><span>1. Position & Motion</span></div>
                            <div><strong>Sign:</strong> ${mathData.sign} at <strong>${mathData.degree_0_to_30.toFixed(2)}°</strong></div>
                            ${nakData ? `<div><strong>Nakshatra:</strong> ${nakData.nakshatra} (Pada ${nakData.pada})</div>` : ''}
                        </div>
                        <div class="bhava-step">
                            <div class="bhava-step-title"><span>2. Dignity in ${varga}</span></div>
                            <div><strong>Status:</strong> <span style="font-weight: 700; color: var(--text-heading);">${dignityStr}</span></div>
                        </div>
                    `;
                }

                if (ruledHouses.length > 0) {
                    liveCardHtml += `
                        <div class="bhava-step">
                            <div class="bhava-step-title"><span>3. Role for ${lagnaSign} Ascendant</span></div>
                            <div><strong>Lord of:</strong> <span style="color: var(--status-benefic-dark); font-weight: 700;">${ruledHouses.join(' & ')}</span></div>
                        </div>
                    `;
                }

                // 4. Graha Drishti Rays
                const advInfo = (currentData && currentData.varga_advanced_aspects && currentData.varga_advanced_aspects[varga])
                    ? currentData.varga_advanced_aspects[varga]
                    : (currentData ? currentData.advanced_aspects : null);
                if (advInfo) {
                    const outgoingRays = [];
                    const incomingRays = [];
                    const plOrder = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"];
                    
                    plOrder.forEach(p => {
                        if (p !== id && advInfo.planets && advInfo.planets[p] && advInfo.planets[p][id]) {
                            const entry = advInfo.planets[p][id];
                            if (entry.raw >= 30) {
                                const isBen = entry.plus > 0;
                                const colorClass = isBen ? 'text-benefic' : 'text-malefic';
                                outgoingRays.push(`<span class="${colorClass}" style="font-weight:600;">➔ ${p} (${Math.round(entry.raw)}v ${isBen ? 'Solid' : 'Dashed'})</span>`);
                            }
                        }
                    });
                    if (advInfo.cusps && (advInfo.cusps[1] || advInfo.cusps['1']) && (advInfo.cusps[1] || advInfo.cusps['1'])[id]) {
                        const entry = (advInfo.cusps[1] || advInfo.cusps['1'])[id];
                        if (entry.raw >= 30) {
                            const isBen = entry.plus > 0;
                            const colorClass = isBen ? 'text-benefic' : 'text-malefic';
                            outgoingRays.push(`<span class="${colorClass}" style="font-weight:600;">➔ Lagna (${Math.round(entry.raw)}v ${isBen ? 'Solid' : 'Dashed'})</span>`);
                        }
                    }

                    plOrder.forEach(p => {
                        if (p !== id && advInfo.planets && advInfo.planets[id] && advInfo.planets[id][p]) {
                            const entry = advInfo.planets[id][p];
                            if (entry.raw >= 30) {
                                const isBen = entry.plus > 0;
                                const colorClass = isBen ? 'text-benefic' : 'text-malefic';
                                incomingRays.push(`<span class="${colorClass}" style="font-weight:600;">⬅ ${p} (${Math.round(entry.raw)}v ${isBen ? 'Solid' : 'Dashed'})</span>`);
                            }
                        }
                    });

                    liveCardHtml += `
                        <div class="bhava-step">
                            <div class="bhava-step-title"><span>4. Graha Dṛṣṭi Rays</span></div>
                            <div style="font-size: 11.5px; line-height: 1.5; margin-top: 4px;">
                                <div><strong>Casting Sight (➔ Outgoing):</strong> ${outgoingRays.length > 0 ? outgoingRays.join(', ') : '<span style="color:var(--text-muted);">None</span>'}</div>
                                <div style="margin-top: 3px;"><strong>Receiving Sight (⬅ Incoming):</strong> ${incomingRays.length > 0 ? incomingRays.join(', ') : '<span style="color:var(--text-muted);">None</span>'}</div>
                            </div>
                        </div>
                    `;
                }

                liveCardHtml += `</div>`;

                const tabs = (kbData && kbData.tabs) ? kbData.tabs : {};
                const essenceContent = tabs.essence || (kbData ? kbData.content : '<p>No textbook data available.</p>');
                const psychologyContent = tabs.psychology || '<p>Psychology details will appear here.</p>';
                const dignityContent = tabs.dignity || '<p>Dignity details will appear here.</p>';
                const realworldContent = tabs.realworld || '<p>Real-world details will appear here.</p>';
                
                let lagnasContent = tabs.lagnas || '<p>Ascendant details will appear here.</p>';
                if (lagnaSign && tabs.lagnas) {
                    const highlightBanner = `
                        <div class="lagna-highlight-box">
                            <div style="font-weight: 800; font-size: 12px; color: var(--status-neutral); margin-bottom: 2px;">
                                👑 Native's Rising Sign: ${lagnaSign} Ascendant
                            </div>
                            <div style="font-size: 11.5px; color: var(--text-heading);">
                                For this chart, ${escapeHtml(id)} governs <strong>${ruledHouses.join(' & ')}</strong>.
                            </div>
                        </div>
                    `;
                    lagnasContent = highlightBanner + lagnasContent;
                }

                const remediesContent = tabs.remedies || '<p>Remedies details will appear here.</p>';

                infoHtml = `
                    <div id="${containerUid}" class="astra-context-container">
                        ${propsHeader}
                        ${tabsNav}
                        <div class="astra-tab-pane ${defaultTab === 'live' ? 'active' : ''}" data-tab-pane="live">
                            ${liveCardHtml}
                        </div>
                        <div class="astra-tab-pane ${defaultTab === 'essence' ? 'active' : ''}" data-tab-pane="essence">
                            <div class="kb-content">${essenceContent}</div>
                        </div>
                        <div class="astra-tab-pane ${defaultTab === 'psychology' ? 'active' : ''}" data-tab-pane="psychology">
                            <div class="kb-content">${psychologyContent}</div>
                        </div>
                        <div class="astra-tab-pane ${defaultTab === 'dignity' ? 'active' : ''}" data-tab-pane="dignity">
                            <div class="kb-content">${dignityContent}</div>
                        </div>
                        <div class="astra-tab-pane ${defaultTab === 'realworld' ? 'active' : ''}" data-tab-pane="realworld">
                            <div class="kb-content">${realworldContent}</div>
                        </div>
                        <div class="astra-tab-pane ${defaultTab === 'lagnas' ? 'active' : ''}" data-tab-pane="lagnas">
                            <div class="kb-content">${lagnasContent}</div>
                        </div>
                        <div class="astra-tab-pane ${defaultTab === 'remedies' ? 'active' : ''}" data-tab-pane="remedies">
                            <div class="kb-content">${remediesContent}</div>
                        </div>
                    </div>
                `;
            } else {
                if (kbData) {
                    infoHtml = `<h3>${id} (${kbData.sanskrit_name})</h3>`;
                    infoHtml += `<div style="font-size: 13px; margin-bottom: 10px;"><i>${kbData.title}</i></div>`;
                }
                
                if (mathData) {
                    infoHtml += `<p><strong>Degree in ${varga}:</strong> ${mathData.degree_0_to_30.toFixed(2)}°</p>`;
                    infoHtml += `<p><strong>Sign:</strong> ${mathData.sign}</p>`;
                    
                    const nakData = currentData && currentData.nakshatras && currentData.nakshatras.grahas && currentData.nakshatras.grahas[id];
                    if (nakData) {
                        infoHtml += `<p><strong>Nakshatra:</strong> ${nakData.nakshatra} (Pada ${nakData.pada})</p>`;
                    }
                    
                    if (mathData.dignity_breakdown && mathData.dignity_breakdown.final_dignity) {
                        infoHtml += `<p><strong>Dignity in ${varga}:</strong> ${mathData.dignity_breakdown.final_dignity}</p>`;
                    }
                }
                
                if (kbData && kbData.content) {
                    infoHtml += `<hr style="border: 0; border-top: 1px solid var(--border-subtle); margin: 15px 0;">`;
                    infoHtml += `<div class="kb-content">${kbData.content}</div>`;
                }
            }
        } else if (type === 'sign') {
            if (kbData) {
                infoHtml = `<h3>${id} (${kbData.sanskrit_name})</h3>`;
                if (kbData.content) {
                    infoHtml += `<hr style="border: 0; border-top: 1px solid var(--border-subtle); margin: 15px 0;">`;
                    infoHtml += `<div class="kb-content">${kbData.content}</div>`;
                }
            } else {
                infoHtml += `<p>General knowledge base for ${id} will load here.</p>`;
            }
        } else if (type === 'house') {
            infoHtml = renderBhavaInspectorHtml(id, varga, kbData);
        } else if (type === 'nakshatra') {
            if (kbData) {
                infoHtml = `<h3>${id} (${kbData.number})</h3>`;
                if (kbData.content) {
                    infoHtml += `<hr style="border: 0; border-top: 1px solid var(--border-subtle); margin: 15px 0;">`;
                    infoHtml += `<div class="kb-content">${kbData.content}</div>`;
                }
            } else {
                infoHtml += `<p>Details about nakshatra ${id} will load here.</p>`;
            }
        }
        return infoHtml;
    }

    function refreshContextInfoForCell(cell) {
        if (!cell) return;
        const vargaSelect = cell.querySelector('.varga-select');
        const varga = vargaSelect ? vargaSelect.value : 'D1';
        const titleEl = cell.querySelector('.context-info-title');
        if (titleEl) {
            titleEl.textContent = `${varga} - Context Info`;
        }
        
        const infoContent = cell.querySelector('#context-info-content') || cell.querySelector('.sub-window-content');
        if (!infoContent) return;
        
        const currentData = window.currentChartData;
        if (window.currentSelectedEntity) {
            infoContent.innerHTML = renderContextInfoHtml(window.currentSelectedEntity.type, window.currentSelectedEntity.id, varga);
        } else if (currentData && currentData.vargas && currentData.vargas[varga]) {
            const lagna = currentData.vargas[varga].lagna;
            let html = `<h3>${varga} Overview</h3>`;
            html += `<p><strong>Ascendant:</strong> ${lagna.sign} (${lagna.degree_0_to_30.toFixed(2)}°)</p>`;
            html += `<hr style="border: 0; border-top: 1px solid var(--border-subtle); margin: 12px 0;">`;
            html += `<p style="font-size: 13px; color: var(--text-subtle); font-style: italic;">Click on any planet, sign, or house in a chart to view details.</p>`;
            infoContent.innerHTML = html;
        }
    }

    function updateContextInfoPanel(type, id, varga = 'D1') {
        document.querySelectorAll('.grid-cell[data-widget="info"]').forEach(infoCell => {
            const sel = infoCell.querySelector('.varga-select');
            if (sel) sel.value = varga;
            refreshContextInfoForCell(infoCell);
        });
        
        const standaloneInfo = document.getElementById('context-info-content');
        if (standaloneInfo) {
            standaloneInfo.innerHTML = renderContextInfoHtml(type, id, varga);
        }
    }

    if (window.widgetRegistry) {
        window.widgetRegistry.register('info', {
            id: 'info',
            title: 'Context Info',
            icon: 'ℹ️',
            category: 'Positions',
            onUpdate: function(cell, chartData) {
                refreshContextInfoForCell(cell);
            }
        });
    }

    window.escapeHtml = escapeHtml;
    window.toggleRawYaml = toggleRawYaml;
    window.switchContextInfoTab = switchContextInfoTab;
    window.openVargaFromInspector = openVargaFromInspector;
    window.renderYamlPropertiesHeader = renderYamlPropertiesHeader;
    window.renderBhavaInspectorHtml = renderBhavaInspectorHtml;
    window.renderContextInfoHtml = renderContextInfoHtml;
    window.refreshContextInfoForCell = refreshContextInfoForCell;
    window.updateContextInfoPanel = updateContextInfoPanel;
})();
