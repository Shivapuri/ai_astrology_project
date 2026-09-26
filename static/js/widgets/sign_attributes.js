/**
 * Astra Sign Attributes & Kalapurusha Anatomy Widget
 * 
 * Provides Triad Matrix (4x3), Elements, Modalities, Varnas, Doshas,
 * Gunas, and detailed Kalapurusha bodily anatomy inspections.
 */

        // --- SIGN ATTRIBUTES, MATRIX (4x3), VARNAS, DOSHAS & KALAPURUSHA ANATOMY ---

        const SIGN_ATTR_CONSTANTS = {
            signs: ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'],
            signNumbers: {'Aries': 1, 'Taurus': 2, 'Gemini': 3, 'Cancer': 4, 'Leo': 5, 'Virgo': 6, 'Libra': 7, 'Scorpio': 8, 'Sagittarius': 9, 'Capricorn': 10, 'Aquarius': 11, 'Pisces': 12},
            signAbbr: {'Aries': 'Ar', 'Taurus': 'Ta', 'Gemini': 'Ge', 'Cancer': 'Cn', 'Leo': 'Le', 'Virgo': 'Vi', 'Libra': 'Li', 'Scorpio': 'Sc', 'Sagittarius': 'Sg', 'Capricorn': 'Cp', 'Aquarius': 'Aq', 'Pisces': 'Pi'},
            elementMap: {
                'Aries': 'Fire', 'Leo': 'Fire', 'Sagittarius': 'Fire',
                'Taurus': 'Earth', 'Virgo': 'Earth', 'Capricorn': 'Earth',
                'Gemini': 'Air', 'Libra': 'Air', 'Aquarius': 'Air',
                'Cancer': 'Water', 'Scorpio': 'Water', 'Pisces': 'Water'
            },
            mobilityMap: {
                'Aries': 'Movable', 'Cancer': 'Movable', 'Libra': 'Movable', 'Capricorn': 'Movable',
                'Taurus': 'Fixed', 'Leo': 'Fixed', 'Scorpio': 'Fixed', 'Aquarius': 'Fixed',
                'Gemini': 'Dual', 'Virgo': 'Dual', 'Sagittarius': 'Dual', 'Pisces': 'Dual'
            },
            polarityMap: {
                'Aries': 'Active', 'Gemini': 'Active', 'Leo': 'Active', 'Libra': 'Active', 'Sagittarius': 'Active', 'Aquarius': 'Active',
                'Taurus': 'Passive', 'Cancer': 'Passive', 'Virgo': 'Passive', 'Scorpio': 'Passive', 'Capricorn': 'Passive', 'Pisces': 'Passive'
            },
            risingMap: {
                'Gemini': 'Shirshodaya', 'Leo': 'Shirshodaya', 'Virgo': 'Shirshodaya', 'Libra': 'Shirshodaya', 'Scorpio': 'Shirshodaya', 'Aquarius': 'Shirshodaya',
                'Aries': 'Prishtodaya', 'Taurus': 'Prishtodaya', 'Cancer': 'Prishtodaya', 'Sagittarius': 'Prishtodaya', 'Capricorn': 'Prishtodaya',
                'Pisces': 'Ubhayodaya'
            },
            elementsMeta: {
                'Fire': { sanskrit: 'Agni', varna: 'Kshatriya', varnaDesc: 'Leaders & Protectors (courage, executive action)', dosha: 'Pitta', doshaDesc: 'Metabolic fire & vitality', color: '#c0392b', bg: '#fdf2f0', icon: '' },
                'Earth': { sanskrit: 'Prithvi', varna: 'Shudra', varnaDesc: 'Craftsmen & Builders (service, stability, craftsmanship)', dosha: 'Kapha', doshaDesc: 'Physical mass & endurance', color: '#795548', bg: '#f5f0eb', icon: '' },
                'Air': { sanskrit: 'Vayu', varna: 'Vaishya', varnaDesc: 'Merchants & Communicators (commerce, trade, intellect)', dosha: 'Vata', doshaDesc: 'Nervous movement & curiosity', color: '#1976d2', bg: '#f0f7fe', icon: '' },
                'Water': { sanskrit: 'Jala', varna: 'Brahmin', varnaDesc: 'Scholars & Counselors (teaching, wisdom, spirituality)', dosha: 'Kapha', doshaDesc: 'Fluids, lubrication & intuition', color: '#00897b', bg: '#eef8f7', icon: '' }
            },
            mobilityMeta: {
                'Movable': { sanskrit: 'Chara', label: 'Movable (Initiatory)', nature: 'Outgoing, enterprising, initiatory, indicates sudden movement or change', color: '#b91c1c', icon: '' },
                'Fixed': { sanskrit: 'Sthira', label: 'Fixed (Steadfast)', nature: 'Steadfast, resistant to sudden change, preserving the status quo', color: '#1e40af', icon: '' },
                'Dual': { sanskrit: 'Dvisvabhava', label: 'Dual (Adaptable)', nature: 'Adaptable, flexible junction points balancing change and stability', color: '#065f46', icon: '' }
            },
            anatomy: [
                { sign: 'Aries', num: 1, abbr: 'Ar', region: 'Head, Brain, Scalp & Eyes', organs: 'Cranium, cerebral hemispheres, optic nerves, facial motor control' },
                { sign: 'Taurus', num: 2, abbr: 'Ta', region: 'Face, Neck, Throat & Vocal Cords', organs: 'Larynx, pharynx, vocal apparatus, thyroid, cervical vertebrae' },
                { sign: 'Gemini', num: 3, abbr: 'Ge', region: 'Shoulders, Arms, Hands & Upper Chest', organs: 'Upper bronchial tubes, lungs, shoulders, collarbones, nervous coordination' },
                { sign: 'Cancer', num: 4, abbr: 'Cn', region: 'Chest, Breasts, Stomach & Ribs', organs: 'Stomach lining, esophagus, diaphragm, thoracic ribcage, alimentary reception' },
                { sign: 'Leo', num: 5, abbr: 'Le', region: 'Heart, Solar Plexus & Upper Back', organs: 'Cardiac muscle, aorta, solar plexus nerve cluster, spine and thoracic vertebrae' },
                { sign: 'Virgo', num: 6, abbr: 'Vi', region: 'Navel, Small Intestines & Digestive Tract', organs: 'Abdominal digestive organs, duodenum, spleen, intestinal assimilation' },
                { sign: 'Libra', num: 7, abbr: 'Li', region: 'Lower Abdomen, Lumbar & Kidneys', organs: 'Renal glands, kidneys, lumbar spine, urinary filtration and fluid balance' },
                { sign: 'Scorpio', num: 8, abbr: 'Sc', region: 'Pelvis, Excretory & Reproductive', organs: 'Genitalia, prostate, ovaries, rectum, pelvic floor and reproductive seed' },
                { sign: 'Sagittarius', num: 9, abbr: 'Sg', region: 'Hips, Thighs & Arterial System', organs: 'Femoral arteries, pelvic girdle, hips, sciatic nerves, locomotor drive' },
                { sign: 'Capricorn', num: 10, abbr: 'Cp', region: 'Knees, Kneecaps & Skeletal Joints', organs: 'Patella, skeletal joint ligaments, cartilage, structural bone density' },
                { sign: 'Aquarius', num: 11, abbr: 'Aq', region: 'Calves, Shins, Ankles & Skin', organs: 'Achilles tendons, shins, peripheral circulation, skin respiration' },
                { sign: 'Pisces', num: 12, abbr: 'Pi', region: 'Feet, Toes & Lymphatics', organs: 'Tarsals, metatarsals, lymphatic fluid nodes, immune defense fluids' }
            ]
        };

        const GRAHA_COLORS = {
            'Sun': '#d35400', 'Moon': '#4a5568', 'Mars': '#c0392b', 'Mercury': '#1e824c',
            'Jupiter': '#b7791f', 'Venus': '#8d6e63', 'Saturn': '#2c3e50', 'Rahu': '#5d6d7e',
            'Ketu': '#34495e', 'Lagna': '#a93226'
        };

        const GRAHA_SHORT_NAMES = {
            'Sun': 'Su', 'Moon': 'Mo', 'Mars': 'Ma', 'Mercury': 'Me',
            'Jupiter': 'Ju', 'Venus': 'Ve', 'Saturn': 'Sa', 'Rahu': 'Ra',
            'Ketu': 'Ke', 'Lagna': 'Asc'
        };

        window.cycleSouthCenter = function(container) {
            if (!container) return;
            const views = ['title', 'matrix', 'anatomy'];
            let cur = container.dataset.view || 'title';
            let next = views[(views.indexOf(cur) + 1) % views.length];
            container.dataset.view = next;
            container.querySelectorAll('.si-center-view').forEach(v => v.style.display = 'none');
            const target = container.querySelector('.si-view-' + next);
            if (target) target.style.display = '';
        };

        window.cycleSouthCenterFromWidget = function(btn) {
            const widget = btn.closest('.widget-chart');
            if (!widget) return;
            const container = widget.querySelector('.svg-south .si-center-container');
            if (container) {
                window.cycleSouthCenter(container);
            }
        };

        window.switchSignAttrTab = function(btn, tabName) {
            const widget = btn.closest('.widget-sign-attributes');
            if (!widget) return;
            widget.querySelectorAll('.sign-attr-pill-btn').forEach(b => {
                b.classList.remove('active');
                b.style.background = 'transparent';
                b.style.color = '#6b5a4b';
            });
            btn.classList.add('active');
            btn.style.background = '#fffdfa';
            btn.style.color = '#4a3325';
            widget.dataset.activeTab = tabName;
            updateSignAttributesWidget(btn.closest('.grid-cell') || btn.closest('#widgetMaximizeContainer') || widget);
        };

        function calculateClientSignDistributions(varga = 'D1', countLagna = false) {
            const signs = SIGN_ATTR_CONSTANTS.signs;
            const occupants = {};
            signs.forEach(s => { occupants[s] = []; });
            let lagnaSign = 'Aries';
            let lagnaDegStr = '0°00\'';

            if (currentChartData && currentChartData.vargas && currentChartData.vargas[varga]) {
                const vData = currentChartData.vargas[varga];
                if (vData.lagna) {
                    lagnaSign = vData.lagna.sign || 'Aries';
                    const lDeg = vData.lagna.degree_0_to_30 || 0;
                    lagnaDegStr = `${Math.floor(lDeg)}°${Math.round((lDeg % 1) * 60).toString().padStart(2, '0')}'`;
                }
                const grahas = vData.grahas || {};
                const stdGrahas = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu'];
                stdGrahas.forEach(pName => {
                    if (grahas[pName] && grahas[pName].sign) {
                        const s = grahas[pName].sign;
                        const deg = grahas[pName].degree_0_to_30 || 0;
                        const degStr = `${Math.floor(deg)}°${Math.round((deg % 1) * 60).toString().padStart(2, '0')}'`;
                        if (occupants[s]) {
                            occupants[s].push({
                                name: pName,
                                sign: s,
                                deg: deg,
                                degStr: degStr,
                                isRetro: grahas[pName].is_retrograde || false
                            });
                        }
                    }
                });
            }

            // Groupings
            const matrixRows = [
                { element: 'Fire', signs: ['Aries', 'Leo', 'Sagittarius'] },
                { element: 'Earth', signs: ['Capricorn', 'Taurus', 'Virgo'] },
                { element: 'Air', signs: ['Libra', 'Aquarius', 'Gemini'] },
                { element: 'Water', signs: ['Cancer', 'Scorpio', 'Pisces'] }
            ];

            const elementTotals = { 'Fire': 0, 'Earth': 0, 'Air': 0, 'Water': 0 };
            const mobilityTotals = { 'Movable': 0, 'Fixed': 0, 'Dual': 0 };
            const polarityTotals = { 'Active': 0, 'Passive': 0 };
            const risingTotals = { 'Shirshodaya': 0, 'Prishtodaya': 0, 'Ubhayodaya': 0 };

            signs.forEach(s => {
                let cnt = occupants[s].length;
                if (countLagna && s === lagnaSign) cnt += 1;
                const elem = SIGN_ATTR_CONSTANTS.elementMap[s];
                const mob = SIGN_ATTR_CONSTANTS.mobilityMap[s];
                const pol = SIGN_ATTR_CONSTANTS.polarityMap[s];
                const rise = SIGN_ATTR_CONSTANTS.risingMap[s];

                elementTotals[elem] += cnt;
                mobilityTotals[mob] += cnt;
                polarityTotals[pol] += cnt;
                risingTotals[rise] += cnt;
            });

            return {
                varga: varga,
                lagnaSign: lagnaSign,
                lagnaDegStr: lagnaDegStr,
                countLagna: countLagna,
                occupants: occupants,
                matrixRows: matrixRows,
                elementTotals: elementTotals,
                mobilityTotals: mobilityTotals,
                polarityTotals: polarityTotals,
                risingTotals: risingTotals,
                totalPlanets: Object.values(elementTotals).reduce((a, b) => a + b, 0)
            };
        }

        function renderSignAttributesHtml(varga = 'D1', activeTab = 'matrix', countLagna = false) {
            const data = calculateClientSignDistributions(varga, countLagna);
            const C = SIGN_ATTR_CONSTANTS;

            // Helper to render clean planet badge without heavy drop-shadows
            const renderPlanetBadge = (p) => {
                const col = GRAHA_COLORS[p.name] || '#4a3325';
                const abbr = GRAHA_SHORT_NAMES[p.name] || p.name.substring(0, 2);
                const retro = p.isRetro ? ' <span style="color:#b45309; font-size:9.5px; font-weight:bold;">R</span>' : '';
                const tip = `${p.name} at ${p.degStr} in ${p.sign}${p.isRetro ? ' [Retrograde]' : ''}`;
                return `<span class="sign-attr-planet-pill tooltip-target" data-tooltip="${tip}" style="background:#f4ece1; color:${col}; border:1px solid #d5c8b2; padding:1px 5px; border-radius:3px; font-size:10.5px; font-weight:700; margin:1px 2px; display:inline-flex; align-items:center; cursor:default;">${abbr}${retro}</span>`;
            };

            const renderLagnaBadge = (signName) => {
                if (signName !== data.lagnaSign) return '';
                const tip = `Ascendant (Lagna) at ${data.lagnaDegStr} in ${signName}`;
                return `<span class="sign-attr-planet-pill tooltip-target" data-tooltip="${tip}" style="background:#fdf2f0; color:#c0392b; border:1px solid #e5b8b2; padding:1px 5px; border-radius:3px; font-size:10.5px; font-weight:700; margin:1px 2px; display:inline-flex; align-items:center; cursor:default;">Asc</span>`;
            };

            let html = '';

            if (activeTab === 'matrix') {
                // TAB 1: SIMPLIFIED 4x3 MATRIX
                html += `
                <div style="display:flex; flex-direction:column; gap:8px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; font-size:11.5px; color:#6b5a4b; padding:0 2px;">
                        <span><strong>4×3 Sign Matrix:</strong> Distribution of grahas by Element and Mobility</span>
                        <span>Total Grahas: <strong style="color:#4a3325; font-size:12px;">${data.totalPlanets}</strong></span>
                    </div>

                    <div style="overflow-x:auto;">
                        <table class="sign-attr-matrix-table" style="width:100%; border-collapse:collapse;">
                            <thead>
                                <tr>
                                    <th style="width:20%; text-align:left; padding-left:8px;">Element</th>
                                    <th style="width:24%;">Movable (Chara)</th>
                                    <th style="width:24%;">Fixed (Sthira)</th>
                                    <th style="width:24%;">Dual (Dvisvabhava)</th>
                                    <th style="width:8%;">Total</th>
                                </tr>
                            </thead>
                            <tbody>
                `;

                data.matrixRows.forEach(rowDef => {
                    const elem = rowDef.element;
                    const meta = C.elementsMeta[elem];
                    const eTot = data.elementTotals[elem];
                    html += `<tr>`;
                    html += `
                        <td style="background:#faf7f2; text-align:left; padding:6px 8px;">
                            <div style="font-weight:700; color:${meta.color}; font-size:12px;">${elem} (${meta.sanskrit})</div>
                            <div style="font-size:10px; color:#7a6756;">${meta.varna} · ${meta.dosha}</div>
                        </td>
                    `;

                    rowDef.signs.forEach(signName => {
                        const occupantsList = data.occupants[signName] || [];
                        const signAbbr = C.signAbbr[signName];
                        const hasLagna = (signName === data.lagnaSign);
                        const isHighlight = occupantsList.length > 0 || hasLagna;
                        const cellBg = isHighlight ? '#ffffff' : '#faf8f5';

                        let badgesHtml = occupantsList.map(renderPlanetBadge).join('');
                        badgesHtml += renderLagnaBadge(signName);
                        if (!badgesHtml) badgesHtml = `<span style="color:#a8a29e; font-size:11px;">—</span>`;

                        const cellCount = occupantsList.length + (data.countLagna && hasLagna ? 1 : 0);
                        const countBadge = cellCount > 0 ? `<span style="font-size:10px; font-weight:700; color:${meta.color}; margin-left:4px;">(${cellCount})</span>` : '';

                        html += `
                            <td class="interactive" data-type="sign" data-id="${signName}" style="background:${cellBg}; cursor: pointer;">
                                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:3px; padding-bottom:2px; border-bottom:1px solid #f0e6d5;">
                                    <span style="font-weight:700; color:#4a3325; font-size:11px;"><span style="color:#b59472; font-weight:800; margin-right:4px;">${signAbbr}</span>${signName}</span>
                                    ${countBadge}
                                </div>
                                <div style="display:flex; flex-wrap:wrap; align-items:center; min-height:20px;">
                                    ${badgesHtml}
                                </div>
                            </td>
                        `;
                    });

                    html += `
                        <td style="background:#faf7f2; text-align:center; font-weight:bold; font-size:13px; color:${meta.color}; vertical-align:middle;">
                            ${eTot}
                        </td>
                    `;
                    html += `</tr>`;
                });

                html += `
                            </tbody>
                            <tfoot>
                                <tr style="background:#eee5d3; font-weight:bold; color:#4a3325;">
                                    <td style="padding:6px 8px; text-align:left;">Total</td>
                                    <td style="text-align:center; font-size:12px; color:#b91c1c;">${data.mobilityTotals['Movable']}</td>
                                    <td style="text-align:center; font-size:12px; color:#1e40af;">${data.mobilityTotals['Fixed']}</td>
                                    <td style="text-align:center; font-size:12px; color:#065f46;">${data.mobilityTotals['Dual']}</td>
                                    <td style="text-align:center; font-size:13px; color:#4a3325;">${data.totalPlanets}</td>
                                </tr>
                            </tfoot>
                        </table>
                    </div>

                    <!-- Clean Single Summary Bar -->
                    <div style="display:flex; flex-wrap:wrap; gap:12px; font-size:11px; color:#5c4433; background:#fffdfa; border:1px solid #dcb594; border-radius:6px; padding:6px 10px; justify-content:space-between;">
                        <div>
                            <strong style="color:#78350f;">Polarity:</strong>
                            Active (Odd): <strong style="color:#b45309;">${data.polarityTotals['Active']}</strong> ·
                            Passive (Even): <strong style="color:#4b5563;">${data.polarityTotals['Passive']}</strong>
                        </div>
                        <div>
                            <strong style="color:#78350f;">Social Roles (Varnas):</strong>
                            Kshatriya (Fire): <strong>${data.elementTotals['Fire']}</strong> ·
                            Shudra (Earth): <strong>${data.elementTotals['Earth']}</strong> ·
                            Vaishya (Air): <strong>${data.elementTotals['Air']}</strong> ·
                            Brahmin (Water): <strong>${data.elementTotals['Water']}</strong>
                        </div>
                    </div>
                </div>
                `;
            } else if (activeTab === 'anatomy') {
                // TAB 2: STREAMLINED 4-COLUMN KALAPURUSHA ANATOMY
                let activeLimbsCount = 0;
                let rowsHtml = '';

                C.anatomy.forEach(item => {
                    const occupantsList = data.occupants[item.sign] || [];
                    const hasLagna = (item.sign === data.lagnaSign);
                    const isActive = occupantsList.length > 0 || hasLagna;
                    if (isActive) activeLimbsCount++;

                    let occupantsBadges = occupantsList.map(renderPlanetBadge).join('');
                    occupantsBadges += renderLagnaBadge(item.sign);
                    if (!occupantsBadges) occupantsBadges = `<span style="color:#a8a29e; font-size:11px;">—</span>`;

                    const countVal = occupantsList.length + (data.countLagna && hasLagna ? 1 : 0);
                    const countStr = countVal > 0 ? `<strong style="color:#c0392b;">${countVal}</strong>` : `<span style="color:#a8a29e;">0</span>`;
                    const rowBg = isActive ? '#fffdfa' : '#faf8f5';

                    rowsHtml += `
                        <tr class="interactive-table-row" data-type="sign" data-id="${item.sign}" style="background:${rowBg}; cursor: pointer;">
                            <td style="font-weight:700; color:#4a3325; white-space:nowrap; padding:5px 8px;">
                                <span style="color:#b59472; font-weight:800; margin-right:4px;">${item.abbr}</span>${item.sign} <small style="color:#8c7b64; font-weight:normal;">(${item.num})</small>
                            </td>
                            <td style="padding:5px 8px;">
                                <div style="font-weight:600; color:#4a3325; font-size:11px;">${item.region}</div>
                                <div style="font-size:10px; color:#8c7b64; margin-top:1px;">${item.organs}</div>
                            </td>
                            <td style="padding:5px 8px;">
                                <div style="display:flex; flex-wrap:wrap; align-items:center;">
                                    ${occupantsBadges}
                                </div>
                            </td>
                            <td style="text-align:center; font-size:12px; padding:5px 8px;">
                                ${countStr}
                            </td>
                        </tr>
                    `;
                });

                html += `
                <div style="display:flex; flex-direction:column; gap:8px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; background:#fffdfa; padding:5px 10px; border-radius:6px; border:1px solid #dcb594; font-size:11.5px;">
                        <span><strong style="color:#78350f;">Kalapurusha Anatomy:</strong> 12 signs as cosmic human body limbs</span>
                        <span style="font-weight:700; color:#4a3325;">Active: <span style="color:#c0392b;">${activeLimbsCount}/12</span> body regions (${data.totalPlanets} grahas)</span>
                    </div>

                    <div style="overflow-x:auto;">
                        <table class="sign-attr-anatomy-table" style="width:100%; border-collapse:collapse;">
                            <thead>
                                <tr>
                                    <th style="width:20%; text-align:left; padding-left:8px;">Sign</th>
                                    <th style="width:46%;">Body Region & Organs</th>
                                    <th style="width:26%;">Planets</th>
                                    <th style="width:8%; text-align:center;">Total</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${rowsHtml}
                            </tbody>
                        </table>
                    </div>
                </div>
                `;
            } else if (activeTab === 'polarity') {
                // TAB 3: CLEAN POLARITY & RISING
                const activeSigns = ['Aries', 'Gemini', 'Leo', 'Libra', 'Sagittarius', 'Aquarius'];
                const passiveSigns = ['Taurus', 'Cancer', 'Virgo', 'Scorpio', 'Capricorn', 'Pisces'];

                let activePlanetsBadges = '';
                let passivePlanetsBadges = '';
                activeSigns.forEach(s => {
                    activePlanetsBadges += (data.occupants[s] || []).map(renderPlanetBadge).join('');
                    activePlanetsBadges += renderLagnaBadge(s);
                });
                passiveSigns.forEach(s => {
                    passivePlanetsBadges += (data.occupants[s] || []).map(renderPlanetBadge).join('');
                    passivePlanetsBadges += renderLagnaBadge(s);
                });

                const shirshoSigns = ['Gemini', 'Leo', 'Virgo', 'Libra', 'Scorpio', 'Aquarius'];
                const prishtoSigns = ['Aries', 'Taurus', 'Cancer', 'Sagittarius', 'Capricorn'];
                const ubhayaSigns = ['Pisces'];

                let shirshoBadges = '';
                let prishtoBadges = '';
                let ubhayaBadges = '';
                shirshoSigns.forEach(s => {
                    shirshoBadges += (data.occupants[s] || []).map(renderPlanetBadge).join('');
                    shirshoBadges += renderLagnaBadge(s);
                });
                prishtoSigns.forEach(s => {
                    prishtoBadges += (data.occupants[s] || []).map(renderPlanetBadge).join('');
                    prishtoBadges += renderLagnaBadge(s);
                });
                ubhayaSigns.forEach(s => {
                    ubhayaBadges += (data.occupants[s] || []).map(renderPlanetBadge).join('');
                    ubhayaBadges += renderLagnaBadge(s);
                });

                html += `
                <div style="display:flex; flex-direction:column; gap:10px;">
                    <!-- Polarity Section -->
                    <div style="font-weight:bold; color:#78350f; font-size:12px;">1. Polarity & Gender (Active vs. Passive)</div>
                    <div style="display:grid; grid-template-columns:1fr 1fr; gap:8px;">
                        <div class="sign-attr-summary-card" style="border-top:3px solid #b45309;">
                            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
                                <strong style="color:#b45309; font-size:12px;">Active / Masculine / Day Signs</strong>
                                <span style="font-size:13px; font-weight:bold; color:#b45309;">${data.polarityTotals['Active']} grahas</span>
                            </div>
                            <div style="font-size:10.5px; color:#78350f; margin-bottom:6px;">
                                <strong>Odd Signs (1, 3, 5, 7, 9, 11):</strong> Aries, Gemini, Leo, Libra, Sagittarius, Aquarius.<br>
                                Extroverted, expressive, direct. Masculine planets (Sun, Mars, Jupiter) function with natural ease here.
                            </div>
                            <div style="display:flex; flex-wrap:wrap; align-items:center; min-height:22px;">
                                ${activePlanetsBadges || '<span style="color:#a8a29e; font-size:11px;">None</span>'}
                            </div>
                        </div>

                        <div class="sign-attr-summary-card" style="border-top:3px solid #4b5563;">
                            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
                                <strong style="color:#4b5563; font-size:12px;">Passive / Feminine / Night Signs</strong>
                                <span style="font-size:13px; font-weight:bold; color:#4b5563;">${data.polarityTotals['Passive']} grahas</span>
                            </div>
                            <div style="font-size:10.5px; color:#374151; margin-bottom:6px;">
                                <strong>Even Signs (2, 4, 6, 8, 10, 12):</strong> Taurus, Cancer, Virgo, Scorpio, Capricorn, Pisces.<br>
                                Introverted, reflective, receptive. Feminine planets (Moon, Venus) feel more at home here.
                            </div>
                            <div style="display:flex; flex-wrap:wrap; align-items:center; min-height:22px;">
                                ${passivePlanetsBadges || '<span style="color:#a8a29e; font-size:11px;">None</span>'}
                            </div>
                        </div>
                    </div>

                    <!-- Rising Orientation Section -->
                    <div style="font-weight:bold; color:#78350f; font-size:12px; margin-top:4px;">2. Rising Orientation (Udaya)</div>
                    <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(180px, 1fr)); gap:8px;">
                        <div class="sign-attr-summary-card" style="border-left:3px solid #059669;">
                            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:3px;">
                                <strong style="color:#059669; font-size:11.5px;">Head-rising (Shirshodaya)</strong>
                                <span style="font-size:13px; font-weight:bold; color:#059669;">${data.risingTotals['Shirshodaya']}</span>
                            </div>
                            <div style="font-size:10px; color:#065f46; margin-bottom:4px;">
                                <strong>Signs:</strong> Ge, Le, Vi, Li, Sc, Aq<br>
                                Yields benefits early in life or beginning of planetary cycles (Dashas).
                            </div>
                            <div style="display:flex; flex-wrap:wrap; align-items:center;">
                                ${shirshoBadges || '<span style="color:#a8a29e; font-size:11px;">None</span>'}
                            </div>
                        </div>

                        <div class="sign-attr-summary-card" style="border-left:3px solid #d97706;">
                            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:3px;">
                                <strong style="color:#d97706; font-size:11.5px;">Back-rising (Prishtodaya)</strong>
                                <span style="font-size:13px; font-weight:bold; color:#d97706;">${data.risingTotals['Prishtodaya']}</span>
                            </div>
                            <div style="font-size:10px; color:#92400e; margin-bottom:4px;">
                                <strong>Signs:</strong> Ar, Ta, Cn, Sg, Cp<br>
                                Yields results through sustained effort, maturing later in life.
                            </div>
                            <div style="display:flex; flex-wrap:wrap; align-items:center;">
                                ${prishtoBadges || '<span style="color:#a8a29e; font-size:11px;">None</span>'}
                            </div>
                        </div>

                        <div class="sign-attr-summary-card" style="border-left:3px solid #7c3aed;">
                            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:3px;">
                                <strong style="color:#7c3aed; font-size:11.5px;">Both-ways rising (Ubhayodaya)</strong>
                                <span style="font-size:13px; font-weight:bold; color:#7c3aed;">${data.risingTotals['Ubhayodaya']}</span>
                            </div>
                            <div style="font-size:10px; color:#5b21b6; margin-bottom:4px;">
                                <strong>Sign:</strong> Pisces (Meena)<br>
                                Fruitful and adaptable throughout life.
                            </div>
                            <div style="display:flex; flex-wrap:wrap; align-items:center;">
                                ${ubhayaBadges || '<span style="color:#a8a29e; font-size:11px;">None</span>'}
                            </div>
                        </div>
                    </div>
                </div>
                `;
            }

            return html;
        }

        function updateSignAttributesWidget(cell, chartData) {
            if (!cell) {
                cell = document.getElementById('widgetMaximizeContainer') || document.querySelector('.grid-cell[data-widget="sign-attributes"]');
            }
            if (!cell) return;
            const content = cell.querySelector('.sign-attr-content');
            if (!content) return;

            const vargaSelect = cell.querySelector('.varga-select');
            const varga = vargaSelect ? vargaSelect.value : 'D1';

            const widgetEl = cell.querySelector('.widget-sign-attributes');
            const activeTab = widgetEl ? (widgetEl.dataset.activeTab || 'matrix') : 'matrix';

            const chkLagna = cell.querySelector('.chk-count-lagna');
            const countLagna = chkLagna ? chkLagna.checked : false;

            content.innerHTML = renderSignAttributesHtml(varga, activeTab, countLagna);
        }

        window.openFloatingSignAttributes = function(varga = 'D1') {
            const modal = document.getElementById('widgetMaximizeModal');
            const titleEl = document.getElementById('widgetMaximizeModalTitle');
            const container = document.getElementById('widgetMaximizeContainer');
            if (!modal || !titleEl || !container) return;

            const subjectName = currentChartData?.subject_info?.name || '';
            titleEl.textContent = subjectName ? `${subjectName} — Sign Attributes & Anatomy (${varga})` : `Sign Attributes & Anatomy (${varga})`;

            container.innerHTML = `
                <div class="widget-sign-attributes" data-active-tab="matrix" style="display:flex; flex-direction:column; width:100%; height:100%;">
                    <div style="margin-bottom:10px; display:flex; align-items:center; gap:10px; flex-wrap:wrap; background:#f7f3eb; padding:6px 10px; border-radius:6px; border:1px solid #dcb594;">
                        <label style="font-size:11.5px; font-weight:bold; color:#4a3325;">Varga:
                            <select id="floatingSignAttrVargaSelect" onchange="renderFloatingSignAttributesContent()" style="margin-left:4px; padding:2px 6px; font-size:11px; border-radius:4px; border:1px solid #d5c8b2; background:#fffdfa; font-weight:600;">
                                <option value="D1" ${varga === 'D1' ? 'selected' : ''}>D1 - Rāśi</option>
                                <option value="D2" ${varga === 'D2' ? 'selected' : ''}>D2 - Horā</option>
                                <option value="D3" ${varga === 'D3' ? 'selected' : ''}>D3 - Drekkāṇa</option>
                                <option value="D4" ${varga === 'D4' ? 'selected' : ''}>D4 - Caturthāṁśa</option>
                                <option value="D7" ${varga === 'D7' ? 'selected' : ''}>D7 - Saptāṁśa</option>
                                <option value="D9" ${varga === 'D9' ? 'selected' : ''}>D9 - Navāṁśa</option>
                                <option value="D10" ${varga === 'D10' ? 'selected' : ''}>D10 - Daśāṁśa</option>
                                <option value="D12" ${varga === 'D12' ? 'selected' : ''}>D12 - Dvādaśāṁśa</option>
                                <option value="D16" ${varga === 'D16' ? 'selected' : ''}>D16 - Ṣoḍaśāṁśa</option>
                                <option value="D20" ${varga === 'D20' ? 'selected' : ''}>D20 - Viṁśāṁśa</option>
                                <option value="D24" ${varga === 'D24' ? 'selected' : ''}>D24 - Caturviṁśāṁśa</option>
                                <option value="D27" ${varga === 'D27' ? 'selected' : ''}>D27 - Saptaviṁśāṁśa</option>
                                <option value="D30" ${varga === 'D30' ? 'selected' : ''}>D30 - Triṁśāṁśa</option>
                                <option value="D40" ${varga === 'D40' ? 'selected' : ''}>D40 - Khavedāṁśa</option>
                                <option value="D45" ${varga === 'D45' ? 'selected' : ''}>D45 - Akṣavedāṁśa</option>
                                <option value="D60" ${varga === 'D60' ? 'selected' : ''}>D60 - Ṣaṣṭyāṁśa</option>
                            </select>
                        </label>
                        <div class="sign-attr-pills" style="display:inline-flex; background:#eae1d1; border-radius:4px; padding:1px; gap:1px;">
                            <button type="button" class="sign-attr-pill-btn active" onclick="switchFloatingSignAttrTab(this, 'matrix')" style="border:none; background:#fffdfa; color:#4a3325; font-weight:bold; font-size:11px; padding:2px 8px; border-radius:3px; cursor:pointer;">Triad Matrix (4×3)</button>
                            <button type="button" class="sign-attr-pill-btn" onclick="switchFloatingSignAttrTab(this, 'anatomy')" style="border:none; background:transparent; color:#6b5a4b; font-weight:bold; font-size:11px; padding:2px 8px; border-radius:3px; cursor:pointer;">Kalapurusha Anatomy</button>
                            <button type="button" class="sign-attr-pill-btn" onclick="switchFloatingSignAttrTab(this, 'polarity')" style="border:none; background:transparent; color:#6b5a4b; font-weight:bold; font-size:11px; padding:2px 8px; border-radius:3px; cursor:pointer;">Polarity & Rising</button>
                        </div>
                        <label style="font-size:11px; font-weight:600; color:#6b5a4b; display:flex; align-items:center; gap:4px; cursor:pointer;">
                            <input type="checkbox" id="floatingCountLagna" onchange="renderFloatingSignAttributesContent()" style="cursor:pointer;"/> + Lagna
                        </label>
                    </div>
                    <div id="floatingSignAttrContent" style="overflow-y:auto; max-height:68vh; padding:4px;"></div>
                </div>
            `;

            window.switchFloatingSignAttrTab = function(btn, tab) {
                btn.closest('.sign-attr-pills').querySelectorAll('.sign-attr-pill-btn').forEach(b => {
                    b.classList.remove('active');
                    b.style.background = 'transparent';
                    b.style.color = '#6b5a4b';
                });
                btn.classList.add('active');
                btn.style.background = '#fffdfa';
                btn.style.color = '#4a3325';
                container.querySelector('.widget-sign-attributes').dataset.activeTab = tab;
                window.renderFloatingSignAttributesContent();
            };

            window.renderFloatingSignAttributesContent = function() {
                const vSel = document.getElementById('floatingSignAttrVargaSelect');
                const v = vSel ? vSel.value : 'D1';
                const tab = container.querySelector('.widget-sign-attributes')?.dataset?.activeTab || 'matrix';
                const cLagna = document.getElementById('floatingCountLagna')?.checked || false;
                const target = document.getElementById('floatingSignAttrContent');
                if (target) {
                    target.innerHTML = renderSignAttributesHtml(v, tab, cLagna);
                }
            };

            window.renderFloatingSignAttributesContent();
            modal.style.display = 'flex';
        };


// Register with WidgetRegistry
if (typeof window !== 'undefined' && window.widgetRegistry) {
    window.widgetRegistry.register('sign-attributes', {
        id: 'sign-attributes',
        title: 'Sign Attributes & Anatomy',
        icon: '♈',
        category: 'Signs',
        render: function(container, chartData, options) {
            updateSignAttributesWidget(container, chartData);
        },
        onUpdate: function(cell, chartData) {
            updateSignAttributesWidget(cell, chartData);
        }
    });
}

// Global exports
if (typeof window !== 'undefined') {
    window.SIGN_ATTR_CONSTANTS = SIGN_ATTR_CONSTANTS;
    window.renderSignAttributesHtml = renderSignAttributesHtml;
    window.updateSignAttributesWidget = updateSignAttributesWidget;
    window.openFloatingSignAttributes = openFloatingSignAttributes;
}
