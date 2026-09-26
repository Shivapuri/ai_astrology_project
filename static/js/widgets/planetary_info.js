/**
 * Astra Planetary Information & Nakshatras Widget
 * 
 * Renders positions, Tropical signs, dignity, Nakshatra mansions, padas,
 * star lords / sublords, astronomical motion speed, and Tara Bala.
 */

function populatePlanetaryInfoTable(cell, chartData) {
    const currentData = chartData || window.currentChartData;
    const tbody = cell.querySelector("tbody");
    if (!tbody || !currentData || !currentData.nakshatras) return;
    tbody.innerHTML = "";

    const naks = currentData.nakshatras.grahas;
    const d1_grahas = currentData.vargas.D1.grahas;
    const d1_lagna = currentData.vargas.D1.lagna;

            function formatDeg(deg_float) {
                if (deg_float === undefined || deg_float === null) return '--';
                let d = Math.floor(deg_float);
                let m = Math.round((deg_float - d) * 60);
                if (m === 60) { d += 1; m = 0; }
                return `${d.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}`;
            }

            const taraAbbreviations = {
                1: "Jan", 2: "Sam", 3: "Vip", 4: "Ksh", 5: "Prt",
                6: "Sad", 7: "Nai", 8: "Mit", 9: "PrM"
            };

            function cleanDignity(dig) {
                if (!dig || dig === '--') return '--';
                let d = dig.replace("'s Sign", "").replace(" Sign", " House").trim();
                if (d === "Own") d = "Own House";
                return d;
            }

            function getDignityStyle(dig) {
                if (!dig || dig === '--') return 'color: #7f8c8d;';
                if (dig.includes('Own') || dig.includes('Exalt') || dig.includes('Moola')) return 'color: #15803d; font-weight: bold;';
                if (dig.includes('Great Friend') || dig.includes('Friend')) return 'color: #0369a1; font-weight: bold;';
                if (dig.includes('Enemy') || dig.includes('Debilit')) return 'color: #b91c1c; font-weight: bold;';
                return 'color: #4a3325;';
            }

            const taraMeanings = {
                1: "Janma (Birth): Core identity, mind, and physical vitality.",
                2: "Sampat (Wealth): Material prosperity, resource growth, and financial ease.",
                3: "Vipat (Danger): Obstacles, hazards, or unexpected friction to overcome.",
                4: "Kshema (Well-being): Safety, comfort, health, and smooth flow.",
                5: "Pratyak (Opposition): Testing of resolve, obstacles, and resistance.",
                6: "Sadhana (Achievement): Focused effort, discipline, and milestone success.",
                7: "Naidhana (Critical): Sensitive karmic junction; requires care and discernment.",
                8: "Mitra (Friend): Harmonious allies, ease of communication, and support.",
                9: "Parama Mitra (Supreme Friend): Unconditional cosmic support and best blessings."
            };

            // 1. Lagna Row
            if (naks["Lagna"]) {
                const lgNak = naks["Lagna"];
                const tNum = lgNak.tara_number || lgNak.tara || 9;
                const tAbbr = taraAbbreviations[tNum] || '';
                const lordSub = (lgNak.lord_sublord || 'Sa/Ve').replace('/', ' / ');

                tbody.innerHTML += `<tr class="interactive-table-row" data-type="planet" data-id="Lagna" style="cursor: pointer;">
                    <td class="tooltip-target" data-tooltip="<strong>Ascendant (Lagna)</strong><br>Rising degree on the eastern horizon at birth. Defines the 1st house, body, and overall life path." style="cursor:help;"><strong>Lagna</strong></td>
                    <td class="tooltip-target" data-tooltip="<strong>Lagna Degree: ${formatDeg(d1_lagna.degree_0_to_30)}</strong><br>Exact degree rising within ${d1_lagna.sign}." style="cursor:help;">${formatDeg(d1_lagna.degree_0_to_30)}</td>
                    <td class="tooltip-target" data-tooltip="<strong>Lagna Sign: ${d1_lagna.sign}</strong><br>The rising sign setting the core lens of personality and vitality." style="cursor:help;">${d1_lagna.sign}</td>
                    <td style="color: #7f8c8d;">--</td>
                    <td class="tooltip-target" data-tooltip="<strong>Rising Nakshatra: ${lgNak.nakshatra}</strong><br>Sidereal equatorial lunar mansion rising on the eastern horizon." style="cursor:help;">${lgNak.nakshatra}</td>
                    <td class="tooltip-target" data-tooltip="<strong>Pada ${lgNak.pada}</strong><br>Quarter (3°20') of the Nakshatra, mapping into the Navamsha (D9) chart." style="cursor:help;">${lgNak.pada}</td>
                    <td class="tooltip-target" data-tooltip="<strong>Lord & Sublord: ${lordSub}</strong><br>Star lord colors primary nature; Sublord determines event fruition." style="cursor:help;">${lordSub}</td>
                    <td style="color: #7f8c8d;">--</td>
                    <td class="tooltip-target" data-tooltip="<strong>Lagna Tara: ${tNum} (${tAbbr})</strong><br>${taraMeanings[tNum] || 'Navatara baseline position.'}" style="cursor:help;"><span class="badge" style="background:#eadecc; color:#5a4233; font-weight:600;">${tNum} (${tAbbr})</span></td>
                    <td class="tooltip-target" data-tooltip="<strong>Ascendant Motion: Direct</strong><br>The eastern horizon continuously moves forward with Earth's rotation." style="cursor:help;"><span style="color:#64748b;">Direct</span></td>
                </tr>`;
            }

            // 2. Grahas in classical order
            const grahaOrder = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"];
            grahaOrder.forEach(graha => {
                if (!naks[graha] || !d1_grahas[graha]) return;
                const data = naks[graha];
                const gD1 = d1_grahas[graha];
                const isRetro = !!gD1.is_retrograde;
                const isCombust = !!gD1.is_combust;

                // Status Badge & Rich Combustion / Motion Tooltip
                let statusHtml = '<span style="color:#64748b;">Direct</span>';
                let statusDesc = '<strong>Status: Direct Motion</strong><br>• Normal forward planetary progression along the zodiac.';

                const sunDist = (gD1.sun_distance !== undefined && gD1.sun_distance !== null) ? Number(gD1.sun_distance) : null;
                const combOrb = (gD1.combustion_orb !== undefined && gD1.combustion_orb !== null) ? Number(gD1.combustion_orb) : null;
                const combRange = gD1.combustion_range || (combOrb ? `${combOrb}°` : '--');
                const dDeg = sunDist !== null ? Math.floor(sunDist) : 0;
                const dMin = sunDist !== null ? Math.round((sunDist - dDeg) * 60) : 0;
                const sunDistFormatted = sunDist !== null ? `${dDeg}° ${dMin.toString().padStart(2, '0')}' (${sunDist.toFixed(2)}°)` : '--';

                const fnRole = gD1.functional_role || (currentData.karakas && currentData.karakas.functional && currentData.karakas.functional[graha]) || null;
                const rHouses = (fnRole && fnRole.ruled_houses) || gD1.ruled_houses || [];
                const houseCombustDict = {
                    1: "H1 (Tanū): Weakens physical constitution, vitality, and personal stamina.",
                    2: "H2 (Dhana): Weaker family ties, resource friction, and strained speech.",
                    3: "H3 (Sahaja): Challenges for younger siblings; friction in courage and self-effort.",
                    4: "H4 (Sukha): Causes emotional distress, mother to suffer, or domestic unrest.",
                    5: "H5 (Putra): Trouble or delays with children; creative and intellectual strain.",
                    6: "H6 (Ari): Friction with subordinates/employees; weakened vitality and disease resistance.",
                    7: "H7 (Yuvati): Problems in marriage and intimate partnerships; ego friction.",
                    8: "H8 (Randhra): Strains longevity and vitality; chronic stressors and joint financial strain.",
                    9: "H9 (Bhāgya): Harmful or difficult for father, spiritual mentors (Gurus), or higher dharma.",
                    10: "H10 (Karma): Strained relations with bosses or authority figures; public status hurdles.",
                    11: "H11 (Lābha): Difficult for elder siblings; friction in achieving public titles or major gains.",
                    12: "H12 (Vyaya): Feelings of loss, solitude, retreat, or difficulty managing expenses."
                };
                let houseImpactLines = '';
                if (rHouses.length > 0) {
                    houseImpactLines = rHouses.map(h => houseCombustDict[h] ? `• <strong>${houseCombustDict[h]}</strong>` : `• <strong>House ${h} Lord:</strong> Domain requires ego sacrifice.`).join('<br>');
                }

                let combustSection = '';
                if (isCombust && sunDist !== null) {
                    const sevNote = (sunDist < 3.0) 
                        ? '<strong>Deep Combustion (&lt; 3°):</strong> Severe. Planetary rays are incinerated; outer tangible expression is burned away.' 
                        : '<strong>Moderate Combustion:</strong> Within solar orb. Worldly visibility is obscured by the Sun.';
                    
                    combustSection = `<strong>Status: Combust [C] (Astangata / Asta)</strong><br>` +
                        `• <strong>Distance to Sun:</strong> ${sunDistFormatted} separation from Sun<br>` +
                        `• <strong>Combustion Orbit:</strong> Within ${combOrb !== null ? combOrb.toFixed(1) + '°' : '--'} threshold (Surya Siddhanta baseline${isRetro ? ', contracted for Retrograde' : ''})<br>` +
                        `• <strong>Art &amp; Science Range:</strong> ${combRange} (Fish &amp; Kurczak: typical combustion window)<br>` +
                        `• <strong>Combustion State:</strong> ${sevNote}<br>` +
                        (houseImpactLines ? `• <strong>Affected Ruled Houses (Art &amp; Science):</strong><br>${houseImpactLines}<br>` : '') +
                        `• <strong>Core Principle:</strong> Combust planets mainly weaken or harm the houses they rule (particularly relationships and health/vitality), while outer ego pride is surrendered for inward spiritual depth.`;
                }

                let retroSection = '';
                if (isRetro) {
                    retroSection = `<strong>Retrograde [R] (Vakra Motion)</strong><br>` +
                        `• <strong>Motional Power:</strong> Apparent backward movement places ${graha} closest to Earth (high Cheṣṭa Bala).<br>` +
                        `• <strong>Psychological Meaning:</strong> Deeply introspective, non-linear, and unconventional; challenges standard norms and re-evaluates its significations.`;
                }

                if (graha === "Sun") {
                    statusHtml = '<span style="color:#64748b;">Direct</span>';
                    statusDesc = `<strong>Status: Direct Motion (Sun)</strong><br>• The Sun is the self-luminous King and soul of the solar system; cannot be combust.<br>• Moves in continuous direct motion across the ecliptic.`;
                } else if (graha === "Rahu" || graha === "Ketu") {
                    statusHtml = '<span class="badge" style="background:#fee2e2; color:#991b1b; border:1px solid #fca5a5; font-size:10px; font-weight:bold;">Retro [R]</span>';
                    statusDesc = `<strong>Status: Retrograde [R] (Shadow Node)</strong><br>• ${graha} is a mathematical intersection point of orbital planes (chaya graha); always retrograde.<br>• Immune to combustion because it has no physical body or light to be burned.`;
                } else if (isRetro && isCombust) {
                    statusHtml = '<span class="badge" style="background:#fee2e2; color:#991b1b; border:1px solid #fca5a5; font-size:10px; font-weight:bold;">Retro [R]</span> <span class="badge" style="background:#ffedd5; color:#9a3412; border:1px solid #fed7aa; font-size:10px; font-weight:bold;">Cb [C]</span>';
                    statusDesc = `${combustSection}<br><br>${retroSection}`;
                } else if (isRetro) {
                    statusHtml = '<span class="badge" style="background:#fee2e2; color:#991b1b; border:1px solid #fca5a5; font-size:10px; font-weight:bold;">Retro [R]</span>';
                    const proxNote = (sunDist !== null && combOrb !== null) ? `<br>• <strong>Solar Separation:</strong> ${sunDistFormatted} — Safe outside combustion orb (${combOrb.toFixed(1)}°)` : '';
                    statusDesc = `<strong>Status:</strong> ${retroSection}${proxNote}`;
                } else if (isCombust) {
                    statusHtml = '<span class="badge" style="background:#ffedd5; color:#9a3412; border:1px solid #fed7aa; font-size:10px; font-weight:bold;">Combust [C]</span>';
                    statusDesc = combustSection;
                } else {
                    const proxNote = (sunDist !== null && combOrb !== null) ? `<br>• <strong>Distance to Sun:</strong> ${sunDistFormatted} — Safe outside combustion orb (${combOrb.toFixed(1)}°)` : '';
                    statusDesc = `<strong>Status: Direct Motion</strong><br>• Normal forward planetary progression along the zodiac.${proxNote}`;
                }

                // Speed Display
                let speedHtml = '--';
                let speedDesc = 'Standard average daily speed';
                let spdVal = null;
                if (gD1.relative_speed_pct !== undefined) {
                    spdVal = Number(gD1.relative_speed_pct);
                } else if (gD1.relative_speed !== undefined && gD1.relative_speed !== '--') {
                    spdVal = parseFloat(gD1.relative_speed);
                }

                if (spdVal !== null && !isNaN(spdVal)) {
                    let speedColor = '#4a3325';
                    let speedLabel = '';
                    if (spdVal > 115) {
                        speedColor = '#15803d';
                        speedLabel = ' (Fast)';
                        speedDesc = `Fast motion (${spdVal.toFixed(1)}% of mean speed). Indicates swift action, enthusiasm, and rapid results.`;
                    } else if (spdVal < 0) {
                        speedColor = '#b91c1c';
                        speedLabel = ' (Slow)';
                        speedDesc = `Retrograde / negative speed (${spdVal.toFixed(1)}%). Indicates deep introspection, persistent effort, and unconventional methods.`;
                    } else {
                        speedDesc = `Normal daily motion (${spdVal.toFixed(1)}% of mean speed).`;
                    }
                    speedHtml = `<span style="color:${speedColor}; font-weight:bold;">${spdVal.toFixed(1)}%${speedLabel}</span>`;
                }

                // Dignity
                let rawDig = (gD1.dignity_breakdown && gD1.dignity_breakdown.final_dignity) ? gD1.dignity_breakdown.final_dignity : (gD1.dignity || '--');
                if (graha === "Rahu" || graha === "Ketu") rawDig = '--';
                const dignityStr = cleanDignity(rawDig);
                const digStyle = getDignityStyle(dignityStr);
                const digDesc = `<strong>${graha} Dignity: ${dignityStr}</strong><br>Derived from 5-fold compound relationship (Panchadha Sambandha) with host sign lord. Measures ease and confidence.`;

                // Tara
                const tNum = data.tara_number || data.tara || '-';
                const tAbbr = taraAbbreviations[tNum] ? ` (${taraAbbreviations[tNum]})` : '';
                const taraDesc = `<strong>Tara Bala: ${tNum}${tAbbr}</strong><br>${taraMeanings[tNum] || 'Distance in the 9-fold Navatara cycle measured from the natal Moon.'}`;

                // Lord/Sublord format
                const lordSub = (data.lord_sublord || '-').replace('/', ' / ');
                const lsDesc = `<strong>Nakshatra Lord & KP Sublord: ${lordSub}</strong><br>• Star lord gives primary foundational quality.<br>• Sublord determines specific event timing and whether matters bear fruit.`;

                tbody.innerHTML += `<tr class="interactive-table-row" data-type="planet" data-id="${graha}" style="cursor: pointer;">
                    <td class="tooltip-target" data-tooltip="<strong>${graha}</strong><br>Click to inspect details and highlights across all charts." style="cursor:help;"><strong>${graha}</strong></td>
                    <td class="tooltip-target" data-tooltip="<strong>${graha} Position: ${formatDeg(gD1.degree_0_to_30)}</strong><br>Exact degree within ${gD1.sign}." style="cursor:help;">${formatDeg(gD1.degree_0_to_30)}</td>
                    <td class="tooltip-target" data-tooltip="<strong>Sign: ${gD1.sign}</strong><br>Constellation occupied in the Tropical Zodiac." style="cursor:help;">${gD1.sign}</td>
                    <td class="tooltip-target" data-tooltip="${digDesc}" style="${digStyle} cursor:help;">${dignityStr}</td>
                    <td class="tooltip-target" data-tooltip="<strong>Nakshatra: ${data.nakshatra}</strong><br>Sidereal equatorial lunar mansion anchored to Galactic Center." style="cursor:help;">${data.nakshatra}</td>
                    <td class="tooltip-target" data-tooltip="<strong>Pada ${data.pada}</strong><br>Quarter (3°20') of the Nakshatra, mapping into the Navamsha (D9) chart." style="cursor:help;">${data.pada}</td>
                    <td class="tooltip-target" data-tooltip="${lsDesc}" style="cursor:help;">${lordSub}</td>
                    <td class="tooltip-target" data-tooltip="${speedDesc}" style="cursor:help;">${speedHtml}</td>
                    <td class="tooltip-target" data-tooltip="${taraDesc}" style="cursor:help;"><span class="badge" style="background:#f5ede0; color:#4a3325; font-weight:600;">${tNum}${tAbbr}</span></td>
                    <td class="tooltip-target" data-tooltip="${statusDesc}" style="cursor:help;">${statusHtml}</td>
                </tr>`;
            });
        }

        function updatePlanetaryInfoWidgetForCell(cell) {
            populatePlanetaryInfoTable(cell);
        }

        function updateNakshatraWidgetForCell(cell) {
            populatePlanetaryInfoTable(cell);
        }

// Register with WidgetRegistry
if (typeof window !== 'undefined' && window.widgetRegistry) {
    window.widgetRegistry.register('planetary-info', {
        id: 'planetary-info',
        title: 'Planetary Information',
        icon: '🪐',
        category: 'Positions',
        render: function(container, chartData, options) {
            populatePlanetaryInfoTable(container, chartData);
        },
        onUpdate: function(cell, chartData) {
            populatePlanetaryInfoTable(cell, chartData);
        }
    });

    window.widgetRegistry.register('nakshatras', {
        id: 'nakshatras',
        title: 'Nakshatras & Speed',
        icon: '✨',
        category: 'Positions',
        render: function(container, chartData, options) {
            populatePlanetaryInfoTable(container, chartData);
        },
        onUpdate: function(cell, chartData) {
            populatePlanetaryInfoTable(cell, chartData);
        }
    });
}

// Global exports
if (typeof window !== 'undefined') {
    window.populatePlanetaryInfoTable = populatePlanetaryInfoTable;
    window.updatePlanetaryInfoWidgetForCell = updatePlanetaryInfoWidgetForCell;
    window.updateNakshatraWidgetForCell = updateNakshatraWidgetForCell;
}
