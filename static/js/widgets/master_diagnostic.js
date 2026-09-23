/**
 * Astra Master Graha Diagnostic Table & Deep Drawer Engine
 * 
 * Synthesizes planetary dignity, power, qualitative avasthas, continuous drishti,
 * and 4-quadrant psychological archetypes into a unified diagnostic view.
 */

        function openFloatingMasterDiagnostic(varga = 'D1') {
            closeKalaMenu();
            const modal = document.getElementById('widgetMaximizeModal');
            const card = document.getElementById('widgetMaximizeCard');
            const titleEl = document.getElementById('widgetMaximizeModalTitle');
            const container = document.getElementById('widgetMaximizeContainer');
            if (!modal || !titleEl || !container || !currentChartData) return;

            resetFloatingWindowPosition();
            if (card) {
                const w = Math.min(1480, window.innerWidth - 40);
                const h = Math.min(820, window.innerHeight - 60);
                card.style.width = w + 'px';
                card.style.height = h + 'px';
                card.style.left = Math.max(20, Math.round((window.innerWidth - w) / 2)) + 'px';
                card.style.top = Math.max(30, Math.round((window.innerHeight - h) / 2)) + 'px';
            }

            setActiveFloatingNav('nav-btn-master-diag');
            const subjectName = (currentChartData.subject_info && currentChartData.subject_info.name) ? currentChartData.subject_info.name : 'Chart';
            titleEl.textContent = subjectName + " — Master Graha Diagnostics (Unified Dignity, Power, Avasthas & Drishti)";

            const tmpl = document.getElementById('tmpl-master-diagnostic');
            if (tmpl) {
                container.innerHTML = '';
                container.appendChild(tmpl.content.cloneNode(true));
                populateMasterDiagnosticTable(container, varga);
            }

            modal.style.display = 'flex';
            document.body.style.overflow = 'hidden';
        }

        const DIGNITY_MEANINGS = {
            "Exalted": "Operates at its absolute highest potential with royal honor, confidence, and uncontested clarity.",
            "Moolatrikona": "Feels purposeful, duty-bound, and cheerful, working energetically on its primary cosmic mission.",
            "Own Sign": "Master of its own household; secure, self-sufficient, and fully in control of its resources.",
            "Own": "Master of its own household; secure, self-sufficient, and fully in control of its resources.",
            "Great Friend's Sign": "Receives exceptional warmth, hospitality, and enthusiastic backing as an honored VIP guest.",
            "Great Friend": "Receives exceptional warmth, hospitality, and enthusiastic backing as an honored VIP guest.",
            "Friend's Sign": "Enjoys a peaceful, cordial, and cooperative environment.",
            "Friend": "Enjoys a peaceful, cordial, and cooperative environment.",
            "Neutral's Sign": "Receives standard, no-frills hospitality; self-reliant and matter-of-fact.",
            "Neutral": "Receives standard, no-frills hospitality; self-reliant and matter-of-fact.",
            "Enemy's Sign": "Feels unwelcome, stressed, and restricted; requires extra grit and effort to overcome environmental resistance.",
            "Enemy": "Feels unwelcome, stressed, and restricted; requires extra grit and effort to overcome environmental resistance.",
            "Great Enemy's Sign": "Faces intense friction, discomfort, and active opposition; high karmic resistance demands resilience.",
            "Great Enemy": "Faces intense friction, discomfort, and active opposition; high karmic resistance demands resilience.",
            "Debilitated": "Having hit rock bottom, outer worldly confidence is depleted, urging the native to cultivate humble, non-material inner strengths."
        };

        const NAKSHATRA_DATA = {
            "Ashwini": { name: "Ashwini", deity: "Ashwini Kumaras", ruler: "Ketu", nature: "Laghu / Light & Swift", core_drive: "Swift healing, pioneering initiative, and vitality restoration." },
            "Bharani": { name: "Bharani", deity: "Yama", ruler: "Venus", nature: "Ugra / Fierce & Severe", core_drive: "Bearing cosmic burdens, radical transformation, and enduring restraint." },
            "Krittika": { name: "Krittika", deity: "Agni", ruler: "Sun", nature: "Mishra / Mixed (Sharp & Soft)", core_drive: "Purifying fire, cutting through illusions, and digestive power." },
            "Rohini": { name: "Rohini", deity: "Prajapati", ruler: "Moon", nature: "Sthira / Fixed & Enduring", core_drive: "Fertile growth, sensory beauty, charm, and artistic creation." },
            "Mrigashira": { name: "Mrigashira", deity: "Soma", ruler: "Mars", nature: "Mridu / Soft & Gentle", core_drive: "Restless searching, seeking spiritual nectar, and gentle curiosity." },
            "Ardra": { name: "Ardra", deity: "Rudra", ruler: "Rahu", nature: "Tikshna / Sharp & Dreadful", core_drive: "Cathartic storms, emotional breakthrough, and overcoming suffering." },
            "Punarvasu": { name: "Punarvasu", deity: "Aditi", ruler: "Jupiter", nature: "Chara / Movable & Ephemeral", core_drive: "Renewal of light, restorative sanctuary, and return of goodness." },
            "Pushya": { name: "Pushya", deity: "Brihaspati", ruler: "Saturn", nature: "Laghu / Light & Nurturing", core_drive: "Spiritual nourishment, wisdom cultivation, and ethical protection." },
            "Ashlesha": { name: "Ashlesha", deity: "Sarpas", ruler: "Mercury", nature: "Tikshna / Sharp & Dreadful", core_drive: "Kundalini awakening, intuitive perception, and psychological defense." },
            "Magha": { name: "Magha", deity: "Pitris", ruler: "Ketu", nature: "Ugra / Fierce & Severe", core_drive: "Ancestral honor, regal authority, tradition, and lineage pride." },
            "Purva Phalguni": { name: "Purva Phalguni", deity: "Bhaga", ruler: "Venus", nature: "Ugra / Fierce & Severe", core_drive: "Creative recreation, marital affection, passion, and gracious living." },
            "Uttara Phalguni": { name: "Uttara Phalguni", deity: "Aryaman", ruler: "Sun", nature: "Sthira / Fixed & Enduring", core_drive: "Noble contracts, benevolent leadership, and lasting social alliances." },
            "Hasta": { name: "Hasta", deity: "Savitar", ruler: "Moon", nature: "Laghu / Light & Swift", core_drive: "Dexterous craftsmanship, skillful hands, healing, and manifest detail." },
            "Chitra": { name: "Chitra", deity: "Tvashtar", ruler: "Mars", nature: "Mridu / Soft", core_drive: "Intellectual design and craftsmanship." },
            "Swati": { name: "Swati", deity: "Vayu", ruler: "Rahu", nature: "Chara / Movable & Ephemeral", core_drive: "Independent movement, flexible diplomacy, and freedom of expression." },
            "Vishakha": { name: "Vishakha", deity: "Indragni", ruler: "Jupiter", nature: "Mishra / Mixed (Sharp & Soft)", core_drive: "Single-pointed ambition, focused triumph, and overcoming hurdles." },
            "Anuradha": { name: "Anuradha", deity: "Mitra", ruler: "Saturn", nature: "Mridu / Soft & Tender", core_drive: "Devotional allegiance, harmonious fellowship, and organizational loyalty." },
            "Jyeshtha": { name: "Jyeshtha", deity: "Indra", ruler: "Mercury", nature: "Tikshna / Sharp & Dreadful", core_drive: "Elder guardianship, protective sovereignty, and safeguarding status." },
            "Mula": { name: "Mula", deity: "Nirriti", ruler: "Ketu", nature: "Tikshna / Sharp & Dreadful", core_drive: "Root investigation, shattering superficiality, and transformative truth." },
            "Purva Ashadha": { name: "Purva Ashadha", deity: "Apas", ruler: "Venus", nature: "Ugra / Fierce & Severe", core_drive: "Invincible confidence, purifying renewal, and unyielding conviction." },
            "Uttara Ashadha": { name: "Uttara Ashadha", deity: "Vishvedevas", ruler: "Sun", nature: "Sthira / Fixed & Enduring", core_drive: "Universal integrity, permanent achievement, and righteous victory." },
            "Shravana": { name: "Shravana", deity: "Vishnu", ruler: "Moon", nature: "Chara / Movable & Ephemeral", core_drive: "Attentive listening, oral tradition transmission, and preservation of order." },
            "Dhanishtha": { name: "Dhanishtha", deity: "Vasus", ruler: "Mars", nature: "Chara / Movable & Ephemeral", core_drive: "Rhythmic harmony, material abundance, fame, and orchestral coordination." },
            "Shatabhisha": { name: "Shatabhisha", deity: "Varuna", ruler: "Rahu", nature: "Chara / Movable & Ephemeral", core_drive: "Secret healing, 100 remedies, veiled contemplation, and cosmic laws." },
            "Purva Bhadrapada": { name: "Purva Bhadrapada", deity: "Aja Ekapada", ruler: "Jupiter", nature: "Ugra / Fierce & Severe", core_drive: "Ascetic tapas, intense purification, and spiritual zeal." },
            "Uttara Bhadrapada": { name: "Uttara Bhadrapada", deity: "Ahirbudhnya", ruler: "Saturn", nature: "Sthira / Fixed & Enduring", core_drive: "Deep ocean stability, serene wisdom, and grounded contemplation." },
            "Revati": { name: "Revati", deity: "Pushan", ruler: "Mercury", nature: "Mridu / Soft & Gentle", core_drive: "Gentle nourishment, safe guidance of journeys, and spiritual release." }
        };

        function renderNakshatraCell(nakName, deity, ruler, nature, coreDrive) {
            const rawName = String(nakName || '—');
            const cleanUpper = rawName.toUpperCase();
            const receiptText = `✨ ${cleanUpper}\n------------------------------------\n• Deity: ${deity || '—'}\n• Overlord: ${ruler || '—'} (Drives the underlying agenda)\n• Nature: ${nature || '—'}\n• Core Drive: ${coreDrive || 'Subconscious motivation and cosmic trajectory.'}`;
            const escReceipt = receiptText
                .replace(/&/g, '&amp;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;')
                .replace(/\n/g, '<br>');
            const tooltipHtml = `<div style="font-family:monospace; font-size:10.5px; line-height:1.4; text-align:left;">${escReceipt}</div>`;

            function escAttr(str) {
                if (!str) return '';
                return String(str).replace(/"/g, '&quot;');
            }

            return `
                <div class="tooltip-target" data-tooltip="${escAttr(tooltipHtml)}" style="display:flex; flex-direction:column; gap:2px; cursor:help;">
                    <div>
                        <span class="badge" style="background:#f5f3ff; color:#6d28d9; border:1px solid #ddd6fe; font-weight:600; font-size:10px; padding:2px 6px;">✨ ${rawName} (${deity || '—'})</span>
                    </div>
                    <div style="font-size:11px; color:#64748b; padding-left:2px;">
                        ↳ Overlord: <strong style="color:#475569;">${ruler || '—'}</strong>
                    </div>
                </div>
            `;
        }

        function toggleDiagnosticDrawer(drawerId, rowEl) {
            let drawer = (rowEl && rowEl.nextElementSibling && rowEl.nextElementSibling.classList.contains('diagnostic-drawer-row'))
                ? rowEl.nextElementSibling
                : document.getElementById(drawerId);
            if (!drawer) return;
            const isHidden = (drawer.style.display === 'none' || !drawer.style.display);
            
            // Accordion behavior: close other open drawers in this table
            const tbody = drawer.closest('tbody');
            if (tbody) {
                tbody.querySelectorAll('.diagnostic-drawer-row').forEach(d => {
                    if (d !== drawer) d.style.display = 'none';
                });
                tbody.querySelectorAll('.diagnostic-row').forEach(r => {
                    if (r !== rowEl) r.classList.remove('drawer-open');
                });
            }
            
            if (isHidden) {
                drawer.style.display = 'table-row';
                if (rowEl) rowEl.classList.add('drawer-open');
            } else {
                drawer.style.display = 'none';
                if (rowEl) rowEl.classList.remove('drawer-open');
            }
        }

        function updateMasterDiagnosticWidget(cell) {
            if (!cell) {
                cell = document.querySelector('.grid-cell[data-widget="master-diagnostic"]') ||
                       document.getElementById('widgetMaximizeContainer') ||
                       document.getElementById('widget-master-diagnostic');
            }
            if (!cell) return;
            populateMasterDiagnosticTable(cell);
        }

        function populateMasterDiagnosticTable(container, selectedVarga) {
            if (!container || !currentChartData || !currentChartData.vargas) return;
            const targetEl = container.querySelector('#widget-master-diagnostic') || container;
            const tbody = targetEl.querySelector('tbody');
            if (!tbody) return;

            function escapeTooltipAttr(str) {
                if (!str) return '';
                return String(str).replace(/"/g, '&quot;');
            }

            const vSelect = targetEl.querySelector('.varga-select');
            let varga = selectedVarga || (vSelect ? vSelect.value : 'D1');
            if (vSelect && selectedVarga) {
                vSelect.value = selectedVarga;
            }

            const subTitle = targetEl.querySelector('.varga-subtitle');
            if (subTitle) {
                subTitle.textContent = `${varga} • Dignity • Dispositor • Ṣaḍbala • Bālādi/Lajjitādi • 4-Quadrant Diagnosis`;
            }

            tbody.innerHTML = '';

            const vData = (currentChartData.vargas && currentChartData.vargas[varga]) ? currentChartData.vargas[varga] : (currentChartData.vargas ? currentChartData.vargas.D1 : null);
            if (!vData) return;

            const v_grahas = vData.grahas || {};
            const v_lagna = vData.lagna || {};
            const shadbala = currentChartData.shadbala || {};
            const naks = (currentChartData.nakshatras && currentChartData.nakshatras.grahas) || {};
            const bhavas = vData.bhavas || (currentChartData.vargas.D1 && currentChartData.vargas.D1.bhavas) || [];
            const adv_aspects = (currentChartData.varga_advanced_aspects && currentChartData.varga_advanced_aspects[varga])
                ? currentChartData.varga_advanced_aspects[varga]
                : (currentChartData.advanced_aspects || (currentChartData.varga_advanced_aspects && currentChartData.varga_advanced_aspects.D1) || null);

            const peData = currentChartData.planetary_evaluation || {};

            const signsList = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"];
            const signLords = {
                'Aries': 'Mars', 'Taurus': 'Venus', 'Gemini': 'Mercury', 'Cancer': 'Moon',
                'Leo': 'Sun', 'Virgo': 'Mercury', 'Libra': 'Venus', 'Scorpio': 'Mars',
                'Sagittarius': 'Jupiter', 'Capricorn': 'Saturn', 'Aquarius': 'Saturn', 'Pisces': 'Jupiter'
            };

            const oddSigns = new Set(["Aries", "Gemini", "Leo", "Libra", "Sagittarius", "Aquarius"]);
            const rahuStrongSigns = new Set(["Taurus", "Gemini", "Virgo", "Aquarius"]);
            const ketuStrongSigns = new Set(["Scorpio", "Sagittarius", "Pisces"]);

            function formatDeg(deg_float) {
                if (deg_float === undefined || deg_float === null) return '--';
                let d = Math.floor(deg_float);
                let m = Math.round((deg_float - d) * 60);
                if (m === 60) { d += 1; m = 0; }
                return `${d.toString().padStart(2, '0')}°${m.toString().padStart(2, '0')}'`;
            }

            function getCampanusHouse(planetName, defaultHouse) {
                if (!bhavas || bhavas.length === 0) return defaultHouse;
                for (let i = 0; i < bhavas.length; i++) {
                    const b = bhavas[i];
                    if (b.planets && (b.planets.includes(planetName) || (planetName === 'Lagna' && b.planets.includes('Asc')))) {
                        return b.house;
                    }
                }
                return defaultHouse;
            }

            function calculateBaladiAvastha(signName, degFloat) {
                const isOdd = oddSigns.has(signName);
                const deg = Math.max(0.0, Math.min(29.9999, Number(degFloat) || 0.0));
                let seg = Math.floor(deg / 6.0);
                if (seg < 0) seg = 0;
                if (seg > 4) seg = 4;

                const oddStates = ["Bala", "Kumara", "Yuva", "Vriddha", "Mrita"];
                const oddEff = [0.50, 0.75, 1.00, 0.50, 0.25];
                const oddTerms = [
                    "Bāla (Infant / Learning)",
                    "Kumāra (Youth / Playful)",
                    "Yuvā (Prime Adult / Master)",
                    "Vṛddha (Elder / Waning)",
                    "Mṛta (Dormant / Incapacitated)"
                ];

                const evenStates = ["Mrita", "Vriddha", "Yuva", "Kumara", "Bala"];
                const evenEff = [0.25, 0.50, 1.00, 0.75, 0.50];
                const evenTerms = [
                    "Mṛta (Dormant / Incapacitated)",
                    "Vṛddha (Elder / Waning)",
                    "Yuvā (Prime Adult / Master)",
                    "Kumāra (Youth / Playful)",
                    "Bāla (Infant / Learning)"
                ];

                const states = isOdd ? oddStates : evenStates;
                const eff = isOdd ? oddEff : evenEff;
                const terms = isOdd ? oddTerms : evenTerms;

                return {
                    state: states[seg],
                    segment: seg,
                    efficiency_factor: eff[seg],
                    efficiency_pct: Math.round(eff[seg] * 100),
                    sanskrit_term: terms[seg],
                    is_odd_sign: isOdd
                };
            }

            const TRUE_DEBILITATION_SIGNS = {
                'Sun': 'Libra', 'Moon': 'Scorpio', 'Mars': 'Cancer', 'Mercury': 'Pisces',
                'Jupiter': 'Capricorn', 'Venus': 'Virgo', 'Saturn': 'Aries',
                'Rahu': 'Scorpio', 'Ketu': 'Taurus'
            };

            const MOOLATRIKONA_RANGES_JS = {
                'Sun': ['Leo', 0.0, 20.0],
                'Moon': ['Taurus', 3.0, 30.0],
                'Mars': ['Aries', 0.0, 12.0],
                'Mercury': ['Virgo', 15.0, 20.0],
                'Jupiter': ['Sagittarius', 0.0, 10.0],
                'Venus': ['Libra', 0.0, 15.0],
                'Saturn': ['Aquarius', 0.0, 20.0]
            };

            function getDignityScore(digName, planet = null, sign = null, degree = null) {
                if (!digName) return 37.5;
                const cleaned = digName.replace("'s Sign", "").replace(" Sign", "").trim().toLowerCase();
                
                // Exaltation
                if (cleaned.includes('exalt') || cleaned.includes('uccha')) return 100.0;
                
                // Moolatrikona
                if (cleaned.includes('moolatrikona') || cleaned.includes('moola')) {
                    if (planet && degree !== null && degree !== undefined && MOOLATRIKONA_RANGES_JS[planet]) {
                        const [mtSign, minD, maxD] = MOOLATRIKONA_RANGES_JS[planet];
                        if (sign && sign === mtSign && (degree < minD || degree > maxD)) {
                            return (sign && oddSigns.has(sign)) ? 75.0 : 62.5;
                        }
                    }
                    return 87.5;
                }
                
                // Own Sign
                if (cleaned.includes('own')) {
                    if (sign) {
                        return oddSigns.has(sign) ? 75.0 : 62.5;
                    }
                    return 68.75;
                }
                
                // Compound Relationships (Panchadha Maitri)
                if (cleaned.includes('great friend') || cleaned.includes('adhi mitra')) return 60.0;
                if (cleaned.includes('friend') || cleaned.includes('mitra')) return 50.0;
                if (cleaned.includes('neutral') || cleaned.includes('sama')) return 37.5;
                if (cleaned.includes('great enemy') || cleaned.includes('adhi shatru')) return 20.0;
                if (cleaned.includes('enemy') || cleaned.includes('shatru')) return 25.0;
                if (cleaned.includes('debilit') || cleaned.includes('neecha') || cleaned.includes('fall')) return 12.5;
                
                return 37.5;
            }

            function classifyGrahaArchetype(dignityPct, shadbalaPct, isNeechaBhanga = false, isNode = false) {
                if (isNeechaBhanga) {
                    return {
                        archetype: "The Transmuted Hero",
                        badge: "⚡ Transmuted Hero",
                        tier: "Alchemical Triumph",
                        subtext: "Alchemical Rescue (Neecha Bhanga)",
                        desc: "Transmuted weakness into sovereign brilliance. Rises through severe adversity with unbreakable resilience.",
                        color: "#7c3aed",
                        bg: "#f5f3ff"
                    };
                }

                // Shadbala Muscle Tiers
                const isHighMuscle = shadbalaPct >= 110.0;
                const isBalancedMuscle = shadbalaPct >= 85.0 && shadbalaPct < 110.0;
                const isLowMuscle = shadbalaPct < 85.0;

                // Dignity Quality Tiers
                if (dignityPct >= 55.0) {
                    // High Dignity
                    if (isHighMuscle) {
                        return {
                            archetype: "The Generous King",
                            badge: "🌟 Generous King",
                            tier: "Sovereign Blessing",
                            subtext: "High Quality + High Muscle",
                            desc: "High moral character equipped with immense executive horsepower. Bestows noble, durable, and expansive prosperity.",
                            color: "#15803d",
                            bg: "#dcfce7"
                        };
                    } else if (isBalancedMuscle) {
                        return {
                            archetype: "The Noble Guardian",
                            badge: "🛡️ Noble Guardian",
                            tier: "Steadfast Protector",
                            subtext: "High Quality + Balanced Muscle",
                            desc: "High moral integrity with capable functional strength. Delivers steady, ethical results with dependability.",
                            color: "#047857",
                            bg: "#ecfdf5"
                        };
                    } else {
                        return {
                            archetype: "The Sincere Friend",
                            badge: "🤝 Sincere Friend",
                            tier: "Noble Intent / Low Muscle",
                            subtext: "High Quality + Low Muscle",
                            desc: "Pure intentions and spiritual grace, but constrained kinetic stamina. Offers genuine solace and peace with modest worldly output.",
                            color: "#1d4ed8",
                            bg: "#eff6ff"
                        };
                    }
                } else if (dignityPct >= 35.0) {
                    // Neutral Dignity
                    if (isHighMuscle) {
                        return {
                            archetype: "The Pragmatic Executive",
                            badge: "⚒️ Pragmatic Executive",
                            tier: "Tireless Champion",
                            subtext: "Neutral Quality + High Muscle",
                            desc: "Pragmatic balance equipped with formidable kinetic drive. A focused problem-solver who accomplishes ambitious tasks through relentless stamina.",
                            color: "#0284c7",
                            bg: "#f0f9ff"
                        };
                    } else if (isBalancedMuscle) {
                        return {
                            archetype: "The Dutiful Realist",
                            badge: "⚖️ Dutiful Realist",
                            tier: "Functional Workhorse",
                            subtext: "Neutral Quality + Balanced Muscle",
                            desc: "Balanced perspective with adequate strength. Reliable execution without dramatic highs or disruptive lows.",
                            color: "#475569",
                            bg: "#f8fafc"
                        };
                    } else {
                        return {
                            archetype: "The Modest Citizen",
                            badge: "🌱 Modest Citizen",
                            tier: "Quiet Observer",
                            subtext: "Neutral Quality + Low Muscle",
                            desc: "Moderate outlook with limited energy reserves. Functions quietly in low-pressure settings; avoids conflicts.",
                            color: "#64748b",
                            bg: "#f1f5f9"
                        };
                    }
                } else {
                    // Low Dignity
                    if (isHighMuscle) {
                        return {
                            archetype: "The Armed Dictator",
                            badge: "⚔️ Armed Dictator",
                            tier: "Severe Hazard",
                            subtext: "Low Quality + High Muscle",
                            desc: "Severe inner frustration armed with dangerous kinetic weaponry. High risk of destructive aggression or collateral damage without conscious restraint.",
                            color: "#b91c1c",
                            bg: "#fee2e2"
                        };
                    } else if (isBalancedMuscle) {
                        return {
                            archetype: "The Embattled Striver",
                            badge: "🌪️ Embattled Striver",
                            tier: "Strained Fighter",
                            subtext: "Low Quality + Balanced Muscle",
                            desc: "Compromised foundation battling through resistance. Works with effort and friction, bearing scars but enduring.",
                            color: "#c2410c",
                            bg: "#fff7ed"
                        };
                    } else {
                        return {
                            archetype: "The Toothless Bully",
                            badge: "⛓️ Toothless Bully",
                            tier: "Harmless Adversary",
                            subtext: "Low Quality + Low Muscle",
                            desc: "Frustrated disposition but completely deprived of physical muscle. Creates minor friction or internal complaints, but lacks power to cause real harm.",
                            color: "#854d0e",
                            bg: "#fef3c7"
                        };
                    }
                }
            }

            function classifyGrahaQuadrant(dignityPct, shadbalaPct, isNode = false) {
                return classifyGrahaArchetype(dignityPct, shadbalaPct, false, isNode);
            }

            const TARA_GRAHAS = ["Mars", "Mercury", "Jupiter", "Venus", "Saturn"];

            function detectPlanetaryWars(grahasObj, shadbalaObj) {
                if (!grahasObj) return {};
                const warResults = {};
                const eligible = TARA_GRAHAS.filter(p => grahasObj[p]);

                for (let i = 0; i < eligible.length; i++) {
                    const p1 = eligible[i];
                    const g1 = grahasObj[p1];
                    const s1 = g1.sign;
                    const d1 = (g1.degree_0_to_30 !== undefined) ? Number(g1.degree_0_to_30) : (Number(g1.longitude || 0) % 30.0);
                    const lat1 = (g1.latitude !== undefined && g1.latitude !== null) ? Number(g1.latitude) : ((g1.lat !== undefined && g1.lat !== null) ? Number(g1.lat) : null);

                    for (let j = i + 1; j < eligible.length; j++) {
                        const p2 = eligible[j];
                        const g2 = grahasObj[p2];
                        const s2 = g2.sign;
                        const d2 = (g2.degree_0_to_30 !== undefined) ? Number(g2.degree_0_to_30) : (Number(g2.longitude || 0) % 30.0);
                        const lat2 = (g2.latitude !== undefined && g2.latitude !== null) ? Number(g2.latitude) : ((g2.lat !== undefined && g2.lat !== null) ? Number(g2.lat) : null);

                        if (s1 !== s2) continue;
                        const degDiff = Math.abs(d1 - d2);
                        if (degDiff <= 1.0) {
                            let winner, loser, reason;
                            if (p1 === "Venus") {
                                winner = p1; loser = p2;
                                reason = "Venus Invariance Rule (Supreme Natural Brilliance)";
                            } else if (p2 === "Venus") {
                                winner = p2; loser = p1;
                                reason = "Venus Invariance Rule (Supreme Natural Brilliance)";
                            } else if (lat1 !== null && lat2 !== null && Math.abs(lat1 - lat2) > 0.001) {
                                if (lat1 > lat2) {
                                    winner = p1; loser = p2;
                                    reason = `Northern Celestial Latitude (${lat1 >= 0 ? '+' : ''}${lat1.toFixed(2)}° vs ${lat2 >= 0 ? '+' : ''}${lat2.toFixed(2)}°)`;
                                } else {
                                    winner = p2; loser = p1;
                                    reason = `Northern Celestial Latitude (${lat2 >= 0 ? '+' : ''}${lat2.toFixed(2)}° vs ${lat1 >= 0 ? '+' : ''}${lat1.toFixed(2)}°)`;
                                }
                            } else {
                                const sb1 = (shadbalaObj && shadbalaObj[p1]) ? Number(shadbalaObj[p1].Total_Virupas || shadbalaObj[p1].Pct_Required_Total || 0) : 0;
                                const sb2 = (shadbalaObj && shadbalaObj[p2]) ? Number(shadbalaObj[p2].Total_Virupas || shadbalaObj[p2].Pct_Required_Total || 0) : 0;
                                if (Math.abs(sb1 - sb2) > 0.1) {
                                    if (sb1 > sb2) {
                                        winner = p1; loser = p2;
                                        reason = `Higher Shadbala Virūpas (${sb1.toFixed(1)}v vs ${sb2.toFixed(1)}v)`;
                                    } else {
                                        winner = p2; loser = p1;
                                        reason = `Higher Shadbala Virūpas (${sb2.toFixed(1)}v vs ${sb1.toFixed(1)}v)`;
                                    }
                                } else {
                                    const rank = {"Jupiter": 4, "Mercury": 3, "Mars": 2, "Saturn": 1};
                                    if ((rank[p1] || 0) >= (rank[p2] || 0)) {
                                        winner = p1; loser = p2;
                                    } else {
                                        winner = p2; loser = p1;
                                    }
                                    reason = "Natural Luminosity Order";
                                }
                            }

                            warResults[winner] = {
                                in_war: true,
                                is_winner: true,
                                is_loser: false,
                                opponent: loser,
                                war_mod: 0.30,
                                badge: `🏆 War Victor (Combat Stain: ${loser})`,
                                reason: reason,
                                orb_deg: Math.round(degDiff * 1000) / 1000,
                                sign: s1,
                                details: `${winner} defeated ${loser} in Graha Yuddha (orb: ${degDiff.toFixed(2)}° in ${s1}) via ${reason}.`
                            };
                            warResults[loser] = {
                                in_war: true,
                                is_winner: false,
                                is_loser: true,
                                opponent: winner,
                                war_mod: -0.60,
                                badge: `⚔️ Nipidita (War Defeat via ${winner})`,
                                reason: reason,
                                orb_deg: Math.round(degDiff * 1000) / 1000,
                                sign: s1,
                                details: `${loser} defeated by ${winner} in Graha Yuddha (orb: ${degDiff.toFixed(2)}° in ${s1}) entering Nipidita Avastha.`
                            };
                        }
                    }
                }
                return warResults;
            }

            function calculateGrahaVitality(pName, sName, degInSign, digName, digPct, hName, hDigPct, hSbPct, pSbPct, netDrishtiVir, conjList, avList, isRet, isComb, isNod, lagnaSign = '', lagnaLord = '', warInfo = null, conjDetails = null, aspDetails = null, fnRole = null) {
                const baladi = calculateBaladiAvastha(sName, degInSign);
                let efficiency = baladi.efficiency_factor;

                const isTrueDebilSign = (TRUE_DEBILITATION_SIGNS[pName] && sName === TRUE_DEBILITATION_SIGNS[pName]);
                const isDebil = isTrueDebilSign || (digName && (digName.toLowerCase().includes('debilit') || digName.toLowerCase().includes('neecha')));
                const isSelfHosted = (hName === pName);
                let effDig = digPct;
                let effSb = pSbPct;
                let rescueBadge = "⚖️ Neutral Host";
                let rescueClass = "neutral";
                let rescueDesc = "Neutral host support; steady baseline.";
                let isNeechaBhanga = false;

                if (isNod) {
                    const affinity = ((pName === 'Rahu' && rahuStrongSigns.has(sName)) || (pName === 'Ketu' && ketuStrongSigns.has(sName))) ? 15.0 : 0.0;
                    effDig = Math.max(12.5, Math.min(100.0, hDigPct * 0.85 + affinity));
                    effSb = Math.max(60.0, hSbPct * 0.90);
                    rescueBadge = `Reflects ${hName}`;
                    rescueClass = "neutral";
                    rescueDesc = `Acts as proxy mirroring ${hName}.`;
                } else if (isSelfHosted) {
                    effDig = digPct;
                    effSb = pSbPct;
                    rescueBadge = "🏡 Self-Hosted";
                    rescueClass = "own";
                    rescueDesc = "Full domicile autonomy in own sign.";
                } else if (isDebil) {
                    if (hDigPct >= 75.0 && hSbPct >= 90.0) {
                        isNeechaBhanga = true;
                        effDig = Math.max(12.5, Math.min(85.0, digPct + 45.0 * (hDigPct / 100.0)));
                        rescueBadge = "✨ Rescued (Neecha Bhanga)";
                        rescueClass = "exalt";
                        rescueDesc = `Full alchemical cancellation: host ${hName} is dignified (${hDigPct.toFixed(0)}%) and potent (${hSbPct.toFixed(0)}% Shadbala).`;
                    } else if (hDigPct >= 55.0) {
                        effDig = Math.max(12.5, Math.min(65.0, digPct + 25.0 * (hDigPct / 100.0)));
                        rescueBadge = "✨ Partial Rescue";
                        rescueClass = "exalt";
                        rescueDesc = `Partially rescued: host ${hName} provides capable backing (${hDigPct.toFixed(0)}% dignity).`;
                    } else if (hDigPct < 30.0) {
                        effDig = Math.max(5.0, digPct - 10.0);
                        rescueBadge = "⚠️ Strained Host";
                        rescueClass = "debil";
                        rescueDesc = `Unsaved: host ${hName} is also debilitated/enemy sign, worsening distress.`;
                    } else {
                        rescueBadge = "⚖️ Neutral Host";
                        rescueClass = "neutral";
                        rescueDesc = "Neutral host backing.";
                    }
                } else {
                    if (hDigPct >= 70.0) {
                        effDig = Math.min(100.0, digPct + 10.0 * (hDigPct / 100.0));
                        rescueBadge = "🛡️ Fortified Host";
                        rescueClass = "own";
                        rescueDesc = `Reinforced by dignified host ${hName}.`;
                    } else if (hDigPct < 35.0) {
                        effDig = Math.max(10.0, digPct - 8.0);
                        rescueBadge = "⚠️ Strained Host";
                        rescueClass = "debil";
                        rescueDesc = `Under drag from strained host ${hName}.`;
                    } else if (hDigPct >= 50.0 && digPct < 35.0) {
                        effDig = Math.min(45.0, digPct + 6.0 * (hDigPct / 100.0));
                        rescueBadge = "🌱 Stabilized Host";
                        rescueClass = "neutral";
                        rescueDesc = `Supported by competent host ${hName}.`;
                    } else {
                        rescueBadge = "⚖️ Neutral Host";
                        rescueClass = "neutral";
                        rescueDesc = "Neutral host foundation.";
                    }
                }

                // Neutral sign dynamic tilt
                const cleanDigLow = (digName || '').toLowerCase();
                const isNeutralSign = cleanDigLow.includes('neutral') || cleanDigLow.includes('sama') || (digPct >= 35.0 && digPct <= 45.0);
                if (isNeutralSign && !isNod && !isDebil) {
                    if (netDrishtiVir > 5.0) {
                        effDig += Math.min(10.0, (netDrishtiVir / 35.0) * 8.0);
                    }
                    let hasDelight = false;
                    (avList || []).forEach(item => {
                        const st = ((item && item.state) ? item.state : String(item)).toLowerCase();
                        if (st.includes('mudita') || st.includes('garvita')) hasDelight = true;
                    });
                    if (hasDelight) effDig += 5.0;
                    effDig = Math.min(54.9, effDig);
                }

                const quad = classifyGrahaArchetype(effDig, effSb, isNeechaBhanga, isNod);

                // Calibrated Vitality Score (1.0 - 10.0)
                const qNorm = effDig / 10.0;
                const mRatio = effSb / 100.0;
                let baseVit = 5.0;

                if (isNeechaBhanga) {
                    baseVit = Math.min(9.0, Math.max(4.5, 5.5 + (qNorm - 5.5) * 0.8 + (mRatio - 1.0) * 1.0 + 0.5));
                } else if (qNorm >= 5.5) {
                    baseVit = 5.5 + (qNorm - 5.5) * 0.8 + (mRatio - 1.0) * 1.2;
                } else if (qNorm >= 3.5) {
                    baseVit = 5.0 + (qNorm - 3.5) * 0.5 + (mRatio - 1.0) * 1.5;
                } else {
                    const qDeficit = 3.5 - qNorm;
                    if (effSb >= 110.0) {
                        const hazardMult = Math.min(1.3, 0.75 + 0.25 * mRatio);
                        baseVit = 3.8 - (qDeficit * hazardMult) - (mRatio - 1.0) * 1.0;
                    } else if (effSb < 88.0) {
                        baseVit = 3.5 - (qDeficit * 0.5) - Math.max(0.0, 1.0 - mRatio) * 0.5;
                    } else {
                        baseVit = 4.2 - (qDeficit * 0.6) + (mRatio - 1.0) * 0.5;
                    }
                }

                // Environmental Modifications (Option A Recursive Drishti & Conjunction Dynamics)
                let drishtiMod = 0.0;
                const processedAspDetails = [];
                if (aspDetails && aspDetails.length > 0) {
                    let totalAdjVir = 0.0;
                    aspDetails.forEach(asp => {
                        const fromP = asp.from_planet;
                        const vir = Number(asp.virupas || 0);
                        const isDeb = !!asp.is_debilitated;
                        let isDistorted = false;
                        let badge = '';
                        let adjVir = vir;
                        if (['Jupiter', 'Venus'].includes(fromP) && isDeb) {
                            isDistorted = true;
                            adjVir = (vir > 0) ? (vir * 0.5) : vir; // 50% positive dampening
                            badge = (fromP === 'Jupiter') ? '⚠️ Compromised Guidance / Dogmatic Light' : '⚠️ Corrupted Indulgence / Compromised Harmony';
                        }
                        totalAdjVir += adjVir;
                        processedAspDetails.push({
                            from_planet: fromP,
                            raw_virupas: vir,
                            adjusted_virupas: adjVir,
                            from_dignity_pct: Number(asp.from_dignity_pct || 50.0),
                            from_dignity_name: String(asp.from_dignity_name || ''),
                            is_debilitated: isDeb,
                            is_distorted: isDistorted,
                            badge: badge
                        });
                    });
                    drishtiMod = Math.max(-1.0, Math.min(1.0, totalAdjVir / 35.0)) * 0.7;
                } else {
                    drishtiMod = Math.max(-1.0, Math.min(1.0, netDrishtiVir / 35.0)) * 0.7;
                }

                let conjMod = 0.0;
                let nodeMod = 0.0;
                const processedConjDetails = [];

                let isGuruChandal = false;
                let guruChandalBadge = null;
                let isGuruKetu = false;
                let guruKetuBadge = null;

                const cruelMaleficsSet = new Set(['Saturn', 'Mars', 'Rahu', 'Ketu', 'Sun']);
                const cruelConjoinedNames = [];

                if (conjDetails && conjDetails.length > 0) {
                    conjDetails.forEach(cItem => {
                        const cp = cItem.planet;
                        const diff = Number(cItem.degree_diff || 5.0);
                        const cpSb = Number(cItem.shadbala_pct || 100.0);
                        const band = (diff <= (10.0 / 3.0)) ? "Exact (Intimate)" : ((diff <= 10.0) ? "Moderate" : "Wide");
                        const commands = (cpSb > pSbPct);

                        if (cruelMaleficsSet.has(cp) && cp !== pName) {
                            cruelConjoinedNames.push(cp);
                        }

                        // 1. Jupiter + Rahu (Guru-Chāṇḍāla Yoga)
                        if ((pName === 'Jupiter' && cp === 'Rahu') || (pName === 'Rahu' && cp === 'Jupiter')) {
                            isGuruChandal = true;
                            if (diff <= (10.0 / 3.0)) {
                                guruChandalBadge = "⚡ Guru-Chāṇḍāla (Ideological Eclipse)";
                                nodeMod -= 0.35;
                            } else if (diff <= 10.0) {
                                guruChandalBadge = "⚡ Guru-Chāṇḍāla (Taboo Zeal / High Ambition)";
                                nodeMod -= 0.20;
                            } else {
                                guruChandalBadge = "⚡ Guru-Chāṇḍāla (Unorthodox Doctrine)";
                                conjMod -= 0.10;
                            }
                        }
                        // 2. Jupiter + Ketu (Guru-Ketu Jñāna Yoga)
                        else if ((pName === 'Jupiter' && cp === 'Ketu') || (pName === 'Ketu' && cp === 'Jupiter')) {
                            isGuruKetu = true;
                            guruKetuBadge = "🕉️ Jñāna Catalyst (Inward Contemplation / Spiritualization)";
                            nodeMod += 0.15;
                        }
                        // 3. Standard Nodal Dynamics for other planets
                        else if (cp === 'Ketu') {
                            if (diff <= (10.0 / 3.0)) {
                                efficiency *= 0.80; // Biological & worldly suppression
                                nodeMod -= 0.25;
                            } else if (diff <= 10.0) {
                                conjMod -= 0.15;
                            }
                        } else if (cp === 'Rahu') {
                            if (diff <= (10.0 / 3.0)) {
                                if (hDigPct >= 60.0 && hSbPct >= 90.0) {
                                    nodeMod += 0.20; // Constructive worldly amplification
                                } else {
                                    nodeMod -= 0.35; // Toxic obsession / delusion
                                }
                            } else if (diff <= 10.0) {
                                conjMod -= 0.15;
                            }
                        } else if (['Jupiter', 'Venus'].includes(cp)) {
                            conjMod += 0.30;
                        } else if (lagnaLord && cp === lagnaLord) {
                            conjMod += 0.35;
                        } else if (['Saturn', 'Mars'].includes(cp)) {
                            conjMod -= 0.30;
                        } else if (['Rahu', 'Ketu'].includes(cp) && diff > 10.0) {
                            conjMod -= 0.10;
                        }

                        processedConjDetails.push({
                            planet: cp,
                            degree_diff: diff,
                            orb_band: band,
                            shadbala_pct: cpSb,
                            commands: commands
                        });
                    });
                } else {
                    (conjList || []).forEach(cp => {
                        if (cruelMaleficsSet.has(cp) && cp !== pName) {
                            cruelConjoinedNames.push(cp);
                        }
                        if ((pName === 'Jupiter' && cp === 'Rahu') || (pName === 'Rahu' && cp === 'Jupiter')) {
                            isGuruChandal = true;
                            guruChandalBadge = "⚡ Guru-Chāṇḍāla (Taboo Zeal / High Ambition)";
                            nodeMod -= 0.20;
                        } else if ((pName === 'Jupiter' && cp === 'Ketu') || (pName === 'Ketu' && cp === 'Jupiter')) {
                            isGuruKetu = true;
                            guruKetuBadge = "🕉️ Jñāna Catalyst (Inward Contemplation / Spiritualization)";
                            nodeMod += 0.15;
                        } else if (lagnaLord && cp === lagnaLord) {
                            conjMod += 0.35;
                        } else if (['Jupiter', 'Venus'].includes(cp)) {
                            conjMod += 0.30;
                        } else if (['Saturn', 'Mars', 'Rahu', 'Ketu'].includes(cp)) {
                            conjMod -= 0.30;
                        }
                    });
                }

                // 4. Deeptādi Vikala Avasthā (Besieged by 2+ cruel malefics)
                let isVikala = false;
                let vikalaBadge = null;
                let vikalaMod = 0.0;
                if (cruelConjoinedNames.length >= 2 && !['Rahu', 'Ketu'].includes(pName)) {
                    isVikala = true;
                    vikalaBadge = `🩸 Vikala (Besieged by ${cruelConjoinedNames.join(', ')})`;
                    vikalaMod = -0.30;
                }

                let envMod = Math.max(-1.3, Math.min(1.3, drishtiMod + conjMod));

                let combustMod = isComb ? -0.50 : 0.0;
                let motMod = combustMod; // ADR-009: Decouple retrograde double-counting

                // Planetary War Modifier
                let warMod = 0.0;
                if (warInfo) {
                    if (warInfo.is_loser) warMod = -0.60;
                    else if (warInfo.is_winner) warMod = 0.30;
                }

                // Psychological Feeling State (Lajjitadi - ADR-009)
                let psyMod = 0.0;
                let hasGarvita = false;
                (avList || []).forEach(item => {
                    const st = ((item && item.state) ? item.state : String(item)).toLowerCase();
                    if (st.includes('garvita')) { hasGarvita = true; psyMod += 0.15; }
                    else if (st.includes('mudita')) { psyMod += 0.15; }
                    else if (st.includes('kshudhita')) { psyMod -= 0.15; }
                    else if (st.includes('kshobhita')) { psyMod -= 0.10; }
                    else if (st.includes('lajjita')) { psyMod -= (hasGarvita ? 0.10 : 0.15); }
                    else if (st.includes('trushita')) { psyMod -= 0.10; }
                });
                psyMod = Math.max(-0.20, Math.min(0.20, psyMod));

                // Functional role narrative update
                const isTrishadaya = fnRole && fnRole.is_trishadaya;
                const isFunctionalMalefic = fnRole && (fnRole.status === 'Functional Malefic');
                if (quad.archetype === 'The Generous King') {
                    if (isGuruChandal) {
                        quad.desc = `High executive capability and expansive mobilization muscle (rules ${(fnRole && fnRole.ruled_houses_str) || 'H11'}), harnessed to unorthodox, dogmatic, or ruthless ideological ambition (Guru-Chāṇḍāla). Massive administrative scale with high risk of ethical blind spots.`;
                        quad.tier = 'Ideological Mobilizer';
                        quad.badge = '⚡ Ideological Mobilizer';
                    } else if (isFunctionalMalefic && isTrishadaya && isVikala) {
                        quad.desc = `High organizational competence and resource power (rules ${(fnRole && fnRole.ruled_houses_str) || ''}), besieged by cruel planets into aggressive worldly appetite and intense friction.`;
                        quad.tier = 'Embattled Executive';
                        quad.badge = '⚡ Embattled Executive';
                    }
                }

                const preScore = baseVit + envMod + motMod + psyMod + warMod + nodeMod + vikalaMod;
                let finalScore = 5.0 + (preScore - 5.0) * (0.6 + 0.4 * efficiency);
                finalScore = Math.max(1.0, Math.min(10.0, Math.round(finalScore * 10) / 10));

                let vTier = "🟡 Resilient";
                let vBg = "#fef9c3";
                let vCol = "#854d0e";
                if (finalScore >= 8.5) {
                    vTier = "🌟 Sovereign";
                    vBg = "#fef3c7"; vCol = "#92400e";
                } else if (finalScore >= 7.0) {
                    vTier = "🟢 Capable";
                    vBg = "#dcfce7"; vCol = "#15803d";
                } else if (finalScore >= 5.5) {
                    vTier = "🟡 Resilient";
                    vBg = "#fef9c3"; vCol = "#854d0e";
                } else if (finalScore >= 4.0) {
                    vTier = "🟠 Strained";
                    vBg = "#ffedd5"; vCol = "#9a3412";
                } else {
                    vTier = (quad.archetype === "The Armed Dictator") ? "🔴 Severe Hazard" : "🔴 Fragile";
                    vBg = "#fee2e2"; vCol = "#991b1b";
                }

                const receiptLines = [
                    "🧮 VITALITY SCORE CALCULATION RECEIPT",
                    "------------------------------------",
                    `1. Base Engine:          ${baseVit.toFixed(1)} (${quad.archetype || 'Neutral'})`,
                    `   • Moral Intent / Dignity: ${effDig.toFixed(1)}% (${digName})`,
                    `   • Kinetic Muscle / Power: ${effSb.toFixed(1)}% of required`,
                    `   • Host Dispositor:        ${rescueDesc}`,
                    `2. Environmental Weather:  ${envMod >= 0 ? '+' : ''}${envMod.toFixed(1)} pts (Aspects & Conjunctions)`,
                    `   • Aspect Vision (Dṛṣṭi):  ${drishtiMod >= 0 ? '+' : ''}${drishtiMod.toFixed(1)} pts`,
                    `   • Conjunctions (Yuti):    ${conjMod >= 0 ? '+' : ''}${conjMod.toFixed(1)} pts`
                ];
                if (isComb) receiptLines.push(`   • Combustion (Astangata): -0.5 pts (Blinded by Sun)`);
                if (warInfo) receiptLines.push(`   • Planetary War (Yuddha): ${warMod >= 0 ? '+' : ''}${warMod.toFixed(1)} pts (${warInfo.is_winner ? 'Victor' : 'Defeated'})`);
                if (nodeMod !== 0.0) receiptLines.push(`   • Nodal Influence:        ${nodeMod >= 0 ? '+' : ''}${nodeMod.toFixed(2)} pts`);
                if (isVikala) receiptLines.push(`   • Besieged State (Vikala): -0.30 pts (2+ Cruel Planets)`);
                if (psyMod !== 0.0) receiptLines.push(`   • Psychological State:    ${psyMod >= 0 ? '+' : ''}${psyMod.toFixed(2)} pts (Lajjitādi Mood)`);
                receiptLines.push(`3. Biological Efficiency:   ${baladi.efficiency_pct}% (${baladi.state} stage)`);
                receiptLines.push(`------------------------------------`);
                receiptLines.push(`★ Final Actualized Vitality: ★ ${finalScore.toFixed(1)} / 10 (${vTier})`);

                const calcReceipt = {
                    base_vitality: Math.round(baseVit * 10) / 10,
                    effective_dignity_pct: Math.round(effDig * 10) / 10,
                    effective_shadbala_pct: Math.round(effSb * 10) / 10,
                    env_mod: Math.round(envMod * 10) / 10,
                    drishti_mod: Math.round(drishtiMod * 10) / 10,
                    conj_mod: Math.round(conjMod * 10) / 10,
                    combust_mod: combustMod,
                    war_mod: warMod,
                    node_mod: Math.round(nodeMod * 100) / 100,
                    vikala_mod: Math.round(vikalaMod * 100) / 100,
                    efficiency_pct: baladi.efficiency_pct,
                    final_score: finalScore,
                    receipt_text: receiptLines.join("\n")
                };

                return {
                    baladi: baladi,
                    effective_dignity_pct: effDig,
                    effective_shadbala_pct: effSb,
                    rescue_badge: rescueBadge,
                    rescue_class: rescueClass,
                    rescue_desc: rescueDesc,
                    is_neecha_bhanga: isNeechaBhanga,
                    quadrant: quad,
                    vitality_score: finalScore,
                    vitality_tier: vTier,
                    vitality_bg: vBg,
                    vitality_col: vCol,
                    war_info: warInfo,
                    war_mod: warMod,
                    node_mod: nodeMod,
                    vikala_mod: vikalaMod,
                    is_guru_chandal: isGuruChandal,
                    guru_chandal_badge: guruChandalBadge,
                    is_guru_ketu: isGuruKetu,
                    guru_ketu_badge: guruKetuBadge,
                    is_vikala: isVikala,
                    vikala_badge: vikalaBadge,
                    functional_role: fnRole,
                    aspect_details: processedAspDetails,
                    conjunction_details: processedConjDetails,
                    calculation_receipt: calcReceipt
                };
            }

            const grahaGlyphs = {
                'Lagna': '🌅', 'Sun': '☉', 'Moon': '☽', 'Mars': '♂',
                'Mercury': '☿', 'Jupiter': '♃', 'Venus': '♀', 'Saturn': '♄',
                'Rahu': '☊', 'Ketu': '☋'
            };

            const grahaOrder = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"];

            const grahaArchetypes = {
                'Sun': '<strong>☉ Sun (Sūrya) — Soul & Vital Will</strong><br>• <strong>Core Nature:</strong> Soul essence (Ātman), self-identity, confidence, vital energy, authority, leadership, father, and dharmic purpose.',
                'Moon': '<strong>☽ Moon (Chandra) — Mind & Feeling Consciousness</strong><br>• <strong>Core Nature:</strong> Mind (Manas), emotions, intuitive responsiveness, peace of heart, mother, and public connection.',
                'Mars': '<strong>♂ Mars (Mangala) — Focused Drive & Courage</strong><br>• <strong>Core Nature:</strong> Courage, decisive physical action, engineering/technical logic, protective strength, brothers, and willpower.',
                'Mercury': '<strong>☿ Mercury (Budha) — Discernment & Intellect</strong><br>• <strong>Core Nature:</strong> Intellect (Buddhi), analytical communication, speech, learning, commercial skill, and adaptability.',
                'Jupiter': '<strong>♃ Jupiter (Guru) — Wisdom & Divine Grace</strong><br>• <strong>Core Nature:</strong> Higher wisdom, dharma, guru/counselors, spiritual expansion, optimism, ethics, wealth, and children.',
                'Venus': '<strong>♀ Venus (Shukra) — Love, Beauty & Refinement</strong><br>• <strong>Core Nature:</strong> Devotion (Bhakti), relationships, aesthetic arts, diplomacy, life comforts, vehicles, and harmony.',
                'Saturn': '<strong>♄ Saturn (Shani) — Endurance & Mastery of Time</strong><br>• <strong>Core Nature:</strong> Discipline, patience, hard labor, realism, organizational structure, humility, and karmic lessons.',
                'Rahu': '<strong>☊ Rahu (North Node) — The Ambitious Catalyst</strong><br>• <strong>Core Nature:</strong> Future-oriented growth, worldly ambition, innovation, foreign connections, and intense drive for mastery.',
                'Ketu': '<strong>☋ Ketu (South Node) — The Spiritual Liberator</strong><br>• <strong>Core Nature:</strong> Past-life mastery, spiritual detachment (Vairāgya), subtle perception, introspection, and ultimate liberation (Moksha).'
            };

            const signInfo = {
                'Aries': { element: 'Fire', quality: 'Movable (Cardinal)', ruler: 'Mars' },
                'Taurus': { element: 'Earth', quality: 'Fixed', ruler: 'Venus' },
                'Gemini': { element: 'Air', quality: 'Dual (Mutable)', ruler: 'Mercury' },
                'Cancer': { element: 'Water', quality: 'Movable (Cardinal)', ruler: 'Moon' },
                'Leo': { element: 'Fire', quality: 'Fixed', ruler: 'Sun' },
                'Virgo': { element: 'Earth', quality: 'Dual (Mutable)', ruler: 'Mercury' },
                'Libra': { element: 'Air', quality: 'Movable (Cardinal)', ruler: 'Venus' },
                'Scorpio': { element: 'Water', quality: 'Fixed', ruler: 'Mars' },
                'Sagittarius': { element: 'Fire', quality: 'Dual (Mutable)', ruler: 'Jupiter' },
                'Capricorn': { element: 'Earth', quality: 'Movable (Cardinal)', ruler: 'Saturn' },
                'Aquarius': { element: 'Air', quality: 'Fixed', ruler: 'Saturn' },
                'Pisces': { element: 'Water', quality: 'Dual (Mutable)', ruler: 'Jupiter' }
            };

            const houseMeanings = {
                1: "House 1 (Tanū Bhāva): Self, vitality, appearance, perspective, and life foundation (Kendra / Dharma).",
                2: "House 2 (Dhana Bhāva): Wealth, speech, family, resource acquisition, and values (Artha / Māraka).",
                3: "House 3 (Sahaja Bhāva): Courage, siblings, willpower, fine skills, and enterprise (Upachaya / Kāma).",
                4: "House 4 (Sukha Bhāva): Home, mother, emotional heart, inner peace, and real estate (Kendra / Moksha).",
                5: "House 5 (Putra Bhāva): Intelligence, creativity, good karma (Purva Punya), children, and joy (Trikona / Dharma).",
                6: "House 6 (Ari Bhāva): Overcoming obstacles, daily work, healing, enemies, and debts (Dusthāna / Upachaya).",
                7: "House 7 (Yuvati Bhāva): Partnerships, marriage, one-on-one trade, and social contracts (Kendra / Kāma / Māraka).",
                8: "House 8 (Randhra Bhāva): Transformation, longevity, secret knowledge, and deep changes (Dusthāna / Moksha).",
                9: "House 9 (Bhāgya Bhāva): Higher dharma, divine grace, fortune, father, and spiritual wisdom (Trikona / Dharma).",
                10: "House 10 (Karma Bhāva): Career, social status, leadership, public action, and honors (Kendra / Artha).",
                11: "House 11 (Lābha Bhāva): Major gains, goals achieved, elder siblings, and social network (Upachaya / Kāma).",
                12: "House 12 (Vyaya Bhāva): Solitude, spiritual liberation (Moksha), sleep, retreat, and expenses (Dusthāna / Moksha)."
            };

            function getDignityIcon(digStr) {
                const d = (digStr || '').toLowerCase();
                if (d.includes('exalt') || d.includes('uccha')) return '👑';
                if (d.includes('moola')) return '🏛️';
                if (d.includes('own') || d.includes('svastha')) return '🏡';
                if (d.includes('great friend') || d.includes('adhi-mitra')) return '🤝';
                if (d.includes('friend') || d.includes('mitra')) return '🙂';
                if (d.includes('great enemy') || d.includes('adhi-shatru')) return '⚔️';
                if (d.includes('enemy') || d.includes('shatru')) return '⚠️';
                if (d.includes('debilit') || d.includes('neecha')) return '🔻';
                return '⚖️';
            }

            function renderAspectVisionBadges(aspList) {
                if (!aspList || aspList.length === 0) {
                    return '<div style="color:#94a3b8; font-size:9.5px; font-style:italic;">No decisive aspects</div>';
                }

                const tier3DecisiveAsps = [];
                const tier2BackgroundAsps = [];

                aspList.forEach(asp => {
                    const rawV = Math.abs(Math.round(asp.raw_virupas !== undefined ? asp.raw_virupas : (asp.virupas || 0)));
                    if (rawV < 20) return;
                    if (rawV < 45) {
                        tier2BackgroundAsps.push(asp);
                    } else {
                        tier3DecisiveAsps.push(asp);
                    }
                });

                let tier2Tip = '';
                if (tier2BackgroundAsps.length > 0) {
                    const t2Lines = tier2BackgroundAsps.map(asp => {
                        const aspG = asp.from_planet;
                        const rawV = Math.abs(Math.round(asp.raw_virupas !== undefined ? asp.raw_virupas : (asp.virupas || 0)));
                        const isNaturalBen = ['Jupiter', 'Venus', 'Mercury', 'Moon'].includes(aspG);
                        const natIcon = isNaturalBen ? '🟢' : '🔴';
                        const visionType = isNaturalBen ? 'Śubha Dṛṣṭi (Supportive Vision)' : 'Pāpa Dṛṣṭi (Confrontational Vision)';
                        const digIcon = getDignityIcon(asp.from_dignity_name);
                        return `• ${natIcon} <strong>${aspG}:</strong> ${rawV} Virūpas (${digIcon} ${asp.from_dignity_name || 'Neutral'}) — <em>${visionType}</em>`;
                    }).join('<br>');
                    tier2Tip = `<strong>Subtle Background Vision (20–44 Virūpas)</strong><br>${t2Lines}<br>• <em>Secondary background vision influencing environmental temperament without decisive dominance.</em>`;
                }

                const badgeElements = tier3DecisiveAsps.map(asp => {
                    const aspG = asp.from_planet;
                    const rawV = Math.abs(Math.round(asp.raw_virupas !== undefined ? asp.raw_virupas : (asp.virupas || 0)));
                    const isNaturalBen = ['Jupiter', 'Venus', 'Mercury', 'Moon'].includes(aspG);
                    const natIcon = isNaturalBen ? '🟢' : '🔴';
                    const digIcon = getDignityIcon(asp.from_dignity_name);

                    const dName = (asp.from_dignity_name || '').toLowerCase();
                    const dPct = Number(asp.from_dignity_pct !== undefined ? asp.from_dignity_pct : 50);

                    const isExaltedOrMoola = dName.includes('exalt') || dName.includes('uccha') || dName.includes('moola');
                    const isOwnOrFriend = dName.includes('own') || dName.includes('svastha') || dName.includes('friend') || dName.includes('mitra');
                    const isDebilitated = dName.includes('debilit') || dName.includes('neecha') || Boolean(asp.is_debilitated) || Boolean(asp.is_distorted);
                    const isEnemy = dName.includes('enemy') || dName.includes('shatru');

                    let synthesisText = '';
                    let bBg = '#f8fafc', bBorder = '#cbd5e1', hCol = '#334155', sCol = '#64748b';

                    if (isNaturalBen) {
                        if (isDebilitated) {
                            synthesisText = 'Compromised Support';
                            bBg = '#fefce8'; bBorder = '#fef08a'; hCol = '#854d0e'; sCol = '#a16207';
                        } else if (isEnemy) {
                            synthesisText = 'Misguided Help';
                            bBg = '#fefce8'; bBorder = '#fef08a'; hCol = '#854d0e'; sCol = '#a16207';
                        } else if (isExaltedOrMoola) {
                            synthesisText = 'Pure Grace';
                            bBg = '#ecfdf5'; bBorder = '#a7f3d0'; hCol = '#065f46'; sCol = '#047857';
                        } else if (isOwnOrFriend || dPct >= 55) {
                            synthesisText = 'Strong Support';
                            bBg = '#f0fdf4'; bBorder = '#bbf7d0'; hCol = '#166534'; sCol = '#15803d';
                        } else {
                            synthesisText = 'Supportive Gaze';
                            bBg = '#f0fdf4'; bBorder = '#bbf7d0'; hCol = '#166534'; sCol = '#15803d';
                        }
                    } else {
                        if (isDebilitated) {
                            synthesisText = 'Toxic Friction';
                            bBg = '#fef2f2'; bBorder = '#fca5a5'; hCol = '#991b1b'; sCol = '#b91c1c';
                        } else if (isEnemy) {
                            synthesisText = 'Destructive Pressure';
                            bBg = '#fff1f2'; bBorder = '#fecdd3'; hCol = '#be123c'; sCol = '#9f1239';
                        } else if (isExaltedOrMoola || isOwnOrFriend || dPct >= 55) {
                            synthesisText = (isExaltedOrMoola || dName.includes('own') || dName.includes('svastha'))
                                ? 'Strict Discipline'
                                : 'Constructive Pressure';
                            bBg = '#eff6ff'; bBorder = '#bfdbfe'; hCol = '#1e40af'; sCol = '#1d4ed8';
                        } else {
                            synthesisText = 'Harsh Demand';
                            bBg = '#f8fafc'; bBorder = '#cbd5e1'; hCol = '#334155'; sCol = '#475569';
                        }
                    }

                    const distortNote = asp.is_distorted ? `<br>• <strong>Option A (Distorted Ray):</strong> ${asp.badge}. Originates from debilitated ${aspG}; positive light dampened by 50% (${(rawV * 0.5).toFixed(0)}v effective).` : '';
                    const aspTip = `<strong>${asp.is_distorted ? '⚠️ ' : ''}${natIcon} ${aspG} (${rawV}v)</strong><br>` +
                        `• <strong>Vision Type:</strong> ${isNaturalBen ? 'Śubha Dṛṣṭi (Supportive Vision)' : 'Pāpa Dṛṣṭi (Confrontational Vision)'}<br>` +
                        `• <strong>${aspG} Dignity:</strong> ${digIcon} ${asp.from_dignity_name || 'Neutral'} (${asp.from_dignity_pct ? asp.from_dignity_pct.toFixed(0) : '50'}%)<br>` +
                        `• <strong>Qualitative Effect:</strong> ${synthesisText}${distortNote}<br>` +
                        `• <strong>Force Intensity:</strong> ${rawV} / 60 Virūpas (${((rawV / 60) * 100).toFixed(0)}% Decisive Force).`;

                    return `
                        <div class="tooltip-target aspect-badge-main" style="border: 1px solid ${bBorder}; background: ${bBg}; border-radius: 4px; padding: 2px 6px; margin: 2px 0; cursor: help;" data-tooltip="${escapeTooltipAttr(aspTip)}">
                            <div style="display: flex; align-items: center; gap: 4px; font-weight: bold; font-size: 10px; color: ${hCol};">
                                <span>${natIcon} ${aspG} (${rawV}v)</span>
                            </div>
                            <div style="font-size: 9px; color: ${sCol}; font-weight: 500; line-height: 1.2; margin-top: 1px;">
                                ↳ ${synthesisText}
                            </div>
                        </div>
                    `;
                });

                let drishtiHtml = '';
                if (tier3DecisiveAsps.length > 0) {
                    let innerHtml = badgeElements.join('');
                    if (tier2BackgroundAsps.length > 0) {
                        innerHtml += `
                            <div class="tooltip-target" style="font-size: 8.5px; color: #64748b; font-style: italic; margin-top: 2px; cursor: help;" data-tooltip="${escapeTooltipAttr(tier2Tip)}">
                                + ${tier2BackgroundAsps.length} background aspect${tier2BackgroundAsps.length > 1 ? 's' : ''} (20–44v in tooltip)
                            </div>
                        `;
                    }
                    drishtiHtml = `<div style="display: flex; flex-direction: column; gap: 1px;">${innerHtml}</div>`;
                } else if (tier2BackgroundAsps.length > 0) {
                    drishtiHtml = `
                        <div class="tooltip-target" style="font-size: 9.5px; color: #64748b; font-style: italic; cursor: help; padding: 2px 0;" data-tooltip="${escapeTooltipAttr(tier2Tip)}">
                            Subtle background (${tier2BackgroundAsps.length} aspect${tier2BackgroundAsps.length > 1 ? 's' : ''} 20–44v in tooltip)
                        </div>
                    `;
                } else {
                    drishtiHtml = '<div style="color:#94a3b8; font-size:9.5px; font-style:italic;">No decisive aspects</div>';
                }
                return drishtiHtml;
            }

            // =========================================================================
            // Continuous Vedic Aspect (Drishti) Line Graph Engine (Brihat Jataka 2.13)
            // =========================================================================
            const ANCHOR_DEGREES = [0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330, 360];

            function getAspectAnchorPoints(planet) {
                const p = (planet || '').trim();
                const pCap = p.charAt(0).toUpperCase() + p.slice(1).toLowerCase();
                const anchors = [];
                ANCHOR_DEGREES.forEach(d => {
                    let pct = 0.0;
                    if (d === 0 || d === 30 || d === 150 || d === 300 || d === 330 || d === 360) {
                        pct = 0.0;
                    } else if (d === 180) {
                        pct = 100.0;
                    } else if (d === 90 || d === 210) {
                        pct = (pCap === "Mars") ? 100.0 : 75.0;
                    } else if (d === 120 || d === 240) {
                        pct = (pCap === "Jupiter" || pCap === "Rahu" || pCap === "Ketu") ? 100.0 : 50.0;
                    } else if (d === 60 || d === 270) {
                        pct = (pCap === "Saturn") ? 100.0 : 25.0;
                    }
                    anchors.push([d, pct]);
                });
                return anchors;
            }

            function calculateContinuousDrishti(planet, relativeDeg) {
                const d = ((relativeDeg % 360) + 360) % 360;
                const anchors = getAspectAnchorPoints(planet);
                for (let i = 0; i < anchors.length - 1; i++) {
                    const [d1, p1] = anchors[i];
                    const [d2, p2] = anchors[i + 1];
                    if (d >= d1 && d <= d2) {
                        if (d2 === d1) return p1;
                        return p1 + ((d - d1) / (d2 - d1)) * (p2 - p1);
                    }
                }
                return 0.0;
            }

            function buildAspectGraphData(sourcePlanet, sourceDeg, aspectedPlanets) {
                const anchors = getAspectAnchorPoints(sourcePlanet);
                const pointsStr = anchors.map(([d, pct]) => {
                    const x = 30 + (d / 360.0) * 660;
                    const y = 120 - (pct / 100.0) * 100;
                    return `${x.toFixed(1)},${y.toFixed(1)}`;
                }).join(' ');

                const targetMarkers = [];
                (aspectedPlanets || []).forEach(tgt => {
                    const tgtName = tgt.name;
                    const tgtAbsDeg = Number(tgt.longitude !== undefined ? tgt.longitude : 0);
                    const relDeg = ((tgtAbsDeg - sourceDeg) % 360 + 360) % 360;
                    const pct = calculateContinuousDrishti(sourcePlanet, relDeg);
                    const isFocus = Boolean(tgt.is_target);

                    // Only plot planets that are actively aspected (pct > 0) or the primary target
                    if (pct <= 0.0 && !isFocus) return;

                    const x = 30 + (relDeg / 360.0) * 660;
                    const y = 120 - (pct / 100.0) * 100;
                    targetMarkers.push({
                        name: tgtName,
                        symbol: tgt.symbol || (tgtName ? tgtName.slice(0, 2) : ''),
                        rel_deg: Math.round(relDeg * 10) / 10,
                        pct: Math.round(pct * 10) / 10,
                        cx: Math.round(x * 10) / 10,
                        cy: Math.round(y * 10) / 10,
                        is_target: isFocus
                    });
                });

                return {
                    source_planet: sourcePlanet,
                    polyline_points: pointsStr,
                    targets: targetMarkers
                };
            }

            function renderContinuousAspectSvg(graph, focusPlanetName) {
                if (!graph || !graph.polyline_points) return '';
                const labels = [
                    [30, '0°', 'H1'], [85, '30°', 'H2'], [140, '60°', 'H3'], [195, '90°', 'H4'],
                    [250, '120°', 'H5'], [305, '150°', 'H6'], [360, '180°', 'H7'], [415, '210°', 'H8'],
                    [470, '240°', 'H9'], [525, '270°', 'H10'], [580, '300°', 'H11'], [635, '330°', 'H12'],
                    [690, '360°', 'H1']
                ];

                const ticksHtml = labels.map(([x, deg, h]) => `
                    <line x1="${x}" y1="120" x2="${x}" y2="124" stroke="#94a3b8" stroke-width="1" />
                    <text x="${x}" y="138" font-size="10" font-weight="600" fill="#0f172a" text-anchor="middle">${deg}</text>
                    <text x="${x}" y="152" font-size="9" fill="#64748b" text-anchor="middle">${h}</text>
                `).join('');

                const srcGlyph = grahaGlyphs[graph.source_planet] ? `${grahaGlyphs[graph.source_planet]} ` : '';
                const srcLabel = `${srcGlyph}${graph.source_planet}`;

                // Sort targets by cx to detect and avoid label collisions
                const sortedTargets = [...(graph.targets || [])].sort((a, b) => a.cx - b.cx);
                const targetsHtml = sortedTargets.map((tgt, idx) => {
                    const isFocus = focusPlanetName && (tgt.name === focusPlanetName);
                    const circleFill = isFocus ? "#d97706" : "#2563eb";
                    const strokeAttr = isFocus ? 'stroke="#b45309" stroke-width="1.5"' : '';
                    const radius = isFocus ? "5.5" : "4.5";
                    const textFill = isFocus ? "#b45309" : "#2563eb";
                    const fontWeight = isFocus ? "800" : "bold";
                    
                    let yOffset = isFocus ? 9 : 7;
                    if (idx > 0 && Math.abs(tgt.cx - sortedTargets[idx - 1].cx) < 32) {
                        yOffset += 12;
                    }
                    const labelText = isFocus
                        ? `🎯 ${tgt.symbol} (${tgt.rel_deg}° • ${tgt.pct}%)`
                        : `${tgt.symbol} (${tgt.rel_deg}°)`;

                    return `
                        <line x1="${tgt.cx}" y1="${tgt.cy}" x2="${tgt.cx}" y2="120" 
                              stroke="#64748b" stroke-width="1" stroke-dasharray="2 2" />
                        <circle cx="${tgt.cx}" cy="${tgt.cy}" r="${radius}" fill="${circleFill}" ${strokeAttr} />
                        <text x="${tgt.cx}" y="${tgt.cy - yOffset}" font-size="10" font-weight="${fontWeight}" fill="${textFill}" text-anchor="middle">
                          ${labelText}
                        </text>
                    `;
                }).join('');

                return `
                    <div style="background: #ffffff; padding: 10px; width: 100%; max-width: 720px; font-family: -apple-system, BlinkMacSystemFont, sans-serif; box-sizing: border-box;">
                      <svg viewBox="0 0 720 170" style="width: 100%; height: auto; display: block; overflow: visible;">
                        <!-- Baseline (0% aspect) -->
                        <line x1="30" y1="120" x2="690" y2="120" stroke="#0f172a" stroke-width="1.5" />

                        <!-- Continuous Aspect Polyline -->
                        <polyline points="${graph.polyline_points}" 
                                  fill="none" 
                                  stroke="#2563eb" 
                                  stroke-width="2.2" 
                                  stroke-linejoin="round" 
                                  stroke-linecap="round" />

                        <!-- Degree Ticks & X-Labels (30px to 690px, step = 55px) -->
                        ${ticksHtml}

                        <!-- Source Planet at 0° (Baseline) -->
                        <circle cx="30" cy="120" r="4.5" fill="#d97706" />
                        <text x="36" y="112" font-size="10" font-weight="bold" fill="#d97706" text-anchor="start">
                          ${srcLabel}
                        </text>

                        <!-- Aspected Target Planets Placed on Continuous Curve -->
                        ${targetsHtml}
                      </svg>
                    </div>
                `;
            }

            // 1. Lagna Row
            const lagnaSign = (v_lagna && v_lagna.sign) ? v_lagna.sign : '';
            const lagnaLord = lagnaSign ? (signLords[lagnaSign] || (v_lagna && v_lagna.lord) || '') : '';

            if (v_lagna && v_lagna.sign) {
                const lgSign = v_lagna.sign;
                const lgDegVal = Number(v_lagna.degree_0_to_30 || 0.0);
                const lgDeg = formatDeg(lgDegVal);
                const lgBaladi = calculateBaladiAvastha(lgSign, lgDegVal);
                const lgNak = (varga === 'D1' && naks["Lagna"]) 
                    ? `${naks["Lagna"].nakshatra} (${naks["Lagna"].pada})` 
                    : (naks["Lagna"] ? `D1: ${naks["Lagna"].nakshatra} (${naks["Lagna"].pada})` : '--');
                const lgLord = signLords[lgSign] || v_lagna.lord || '--';
                const lordGraha = v_grahas[lgLord] || {};
                
                // Lord House Placement
                const lagnaIdx = signsList.indexOf(lgSign);
                const lordSign = lordGraha.sign || '';
                const lordDegVal = Number(lordGraha.degree_0_to_30 || 15.0);
                const lordSignIdx = signsList.indexOf(lordSign);
                const lordWHouse = (lagnaIdx >= 0 && lordSignIdx >= 0) ? ((lordSignIdx - lagnaIdx + 12) % 12 + 1) : 1;
                const lordCHouse = getCampanusHouse(lgLord, lordWHouse);

                // Lord Dignity & Styling
                const dBreak = lordGraha.dignity_breakdown || {};
                const lordDigRaw = dBreak.final_dignity || lordGraha.dignity || 'Neutral';
                const cleanLordDig = lordDigRaw.replace("'s Sign", "").replace(" Sign", "").trim();
                const lordDigPct = getDignityScore(cleanLordDig, lgLord, lordSign, lordDegVal);
                let lordDigColor = '#475569';
                let lordDigBg = '#f8fafc';
                let lordDigBorder = '#cbd5e1';
                const lDigLow = lordDigRaw.toLowerCase();
                if (lDigLow.includes('exalt') || lDigLow.includes('moolatrikona') || lDigLow.includes('own')) {
                    lordDigColor = '#065f46'; lordDigBg = '#ecfdf5'; lordDigBorder = '#6ee7b7';
                } else if (lDigLow.includes('great friend') || lDigLow.includes('friend')) {
                    lordDigColor = '#15803d'; lordDigBg = '#f0fdf4'; lordDigBorder = '#86efac';
                } else if (lDigLow.includes('great enemy') || lDigLow.includes('enemy')) {
                    lordDigColor = '#b91c1c'; lordDigBg = '#fef2f2'; lordDigBorder = '#fca5a5';
                } else if (lDigLow.includes('debilitat')) {
                    lordDigColor = '#991b1b'; lordDigBg = '#fee2e2'; lordDigBorder = '#f87171';
                }

                // Lord's Host (Dispositor of the Lagnesha)
                const lordHost = signLords[lordSign] || lgLord;
                const lordHostGraha = v_grahas[lordHost] || {};
                const lordHostSign = lordHostGraha.sign || '';
                const lordHostDegVal = Number(lordHostGraha.degree_0_to_30 || 15.0);
                const lordHostDigRaw = (lordHostGraha.dignity_breakdown && lordHostGraha.dignity_breakdown.final_dignity) ? lordHostGraha.dignity_breakdown.final_dignity : (lordHostGraha.dignity || 'Neutral');
                const lordHostDig = getDignityScore(lordHostDigRaw, lordHost, lordHostSign, lordHostDegVal);
                const lordHostSbEntry = shadbala[lordHost] || {};
                const lordHostSb = Number(lordHostSbEntry.Pct_Required_Total !== undefined ? lordHostSbEntry.Pct_Required_Total : 100.0);

                let lordRescueBadge = '<span class="badge" style="background:#f8fafc; color:#475569; border:1px solid #cbd5e1; font-size:9px;">⚖️ Neutral Host</span>';
                if (lordHost === lgLord) {
                    lordRescueBadge = '<span class="badge" style="background:#ecfdf5; color:#065f46; border:1px solid #a7f3d0; font-size:9px; font-weight:bold;">🏡 Self-Hosted</span>';
                } else if (lordHostDig >= 70.0) {
                    lordRescueBadge = '<span class="badge" style="background:#ecfdf5; color:#065f46; border:1px solid #a7f3d0; font-size:9px; font-weight:bold;">🛡️ Fortified Host</span>';
                } else if (lordHostDig < 40.0) {
                    lordRescueBadge = '<span class="badge" style="background:#fef2f2; color:#b91c1c; border:1px solid #fca5a5; font-size:9px; font-weight:bold;">⚠️ Strained Host</span>';
                }

                // Lord Shadbala Power
                const sbLord = shadbala[lgLord] || {};
                const sbVir = (sbLord.Total_Virupas !== undefined) ? Number(sbLord.Total_Virupas).toFixed(1) : '--';
                const sbPct = (sbLord.Pct_Required_Total !== undefined) ? Math.round(sbLord.Pct_Required_Total) : null;
                const sbRank = sbLord.Relative_Rank !== undefined ? sbLord.Relative_Rank : null;
                const ishta = (sbLord.Ishta_Phala !== undefined) ? Number(sbLord.Ishta_Phala).toFixed(1) : '--';
                const kashta = (sbLord.Kashta_Phala !== undefined) ? Number(sbLord.Kashta_Phala).toFixed(1) : '--';

                // Aspects on Cusp 1
                const cuspTotals = adv_aspects && adv_aspects.totals && adv_aspects.totals.cusps ? (adv_aspects.totals.cusps[1] || adv_aspects.totals.cusps['1'] || {}) : {};
                const c1Net = cuspTotals.net !== undefined ? Number(cuspTotals.net) : 0.0;
                const c1Plus = cuspTotals.plus !== undefined ? Number(cuspTotals.plus) : 0.0;
                const c1Minus = cuspTotals.minus !== undefined ? Number(cuspTotals.minus) : 0.0;
                
                // Special Cusp Aspects
                const c1Indiv = adv_aspects && adv_aspects.cusps ? (adv_aspects.cusps[1] || adv_aspects.cusps['1'] || {}) : {};
                const jupAspectVir = c1Indiv.Jupiter ? Number(c1Indiv.Jupiter.net || c1Indiv.Jupiter.plus || 0) : 0;
                const lordAspectVir = c1Indiv[lgLord] ? Number(c1Indiv[lgLord].net || c1Indiv[lgLord].plus || 0) : 0;

                // Occupants of H1
                const lagnaConj = [];
                grahaOrder.forEach(p => {
                    if (v_grahas[p] && v_grahas[p].sign === lgSign) lagnaConj.push(p);
                });
                const lgConjBadges = lagnaConj.map(cp => {
                    const isBen = ['Jupiter', 'Venus', 'Mercury', 'Moon'].includes(cp);
                    const isMal = ['Saturn', 'Mars', 'Rahu', 'Ketu', 'Sun'].includes(cp);
                    const cColor = isBen ? '#15803d' : (isMal ? '#b91c1c' : '#475569');
                    const cIcon = isBen ? '🤝' : (isMal ? '⚔️' : '•');
                    const tip = `<strong>${cp} in House 1 (Ascendant)</strong><br>• Directly stamps its constitutional nature onto the physical body and personal perspective in ${varga}.`;
                    return `<span class="tooltip-target" style="color:${cColor}; font-weight:600; cursor:help;" data-tooltip="${tip}">${cIcon} ${cp}</span>`;
                }).join(', ');

                // Flanking Kartari around H1
                const h2Sign = signsList[(lagnaIdx + 1) % 12];
                const h12Sign = signsList[(lagnaIdx + 11) % 12];
                const h2Occupants = grahaOrder.filter(p => v_grahas[p] && v_grahas[p].sign === h2Sign && !['Rahu', 'Ketu'].includes(p));
                const h12Occupants = grahaOrder.filter(p => v_grahas[p] && v_grahas[p].sign === h12Sign && !['Rahu', 'Ketu'].includes(p));
                const h2Bens = h2Occupants.filter(p => ['Jupiter', 'Venus', 'Mercury', 'Moon'].includes(p));
                const h2Mals = h2Occupants.filter(p => ['Saturn', 'Mars', 'Sun'].includes(p));
                const h12Bens = h12Occupants.filter(p => ['Jupiter', 'Venus', 'Mercury', 'Moon'].includes(p));
                const h12Mals = h12Occupants.filter(p => ['Saturn', 'Mars', 'Sun'].includes(p));
                let kartariBadge = '';
                let kartariType = 'Neutral';
                if (h2Bens.length > 0 && h12Bens.length > 0 && h2Mals.length === 0 && h12Mals.length === 0) {
                    kartariType = 'Śubha Kartarī';
                    kartariBadge = `<span class="badge tooltip-target" style="background:#ecfdf5; color:#065f46; border:1px solid #a7f3d0; font-size:9px; font-weight:bold; cursor:help;" data-tooltip="<strong>✨ Śubha Kartarī Yoga (Protective Hemming)</strong><br>• Benefics flank both H2 (${h2Bens.join(', ')}) and H12 (${h12Bens.join(', ')}), nurturing vitality and shielding destiny.">✨ Śubha Kartarī</span>`;
                } else if (h2Mals.length > 0 && h12Mals.length > 0 && h2Bens.length === 0 && h12Bens.length === 0) {
                    kartariType = 'Pāpa Kartarī';
                    kartariBadge = `<span class="badge tooltip-target" style="background:#fef2f2; color:#b91c1c; border:1px solid #fca5a5; font-size:9px; font-weight:bold; cursor:help;" data-tooltip="<strong>⚔️ Pāpa Kartarī Yoga (Malefic Hemming)</strong><br>• Malefics flank both H2 (${h2Mals.join(', ')}) and H12 (${h12Mals.join(', ')}), pinching the personal field with chronic resistance.">⚔️ Pāpa Kartarī</span>`;
                }

                // -------------------------------------------------------------
                // Lagna Vitality Score (1.0 - 10.0)
                // -------------------------------------------------------------
                const backendLagna = (varga === 'D1' && peData && peData.lagna_evaluation)
                    ? peData.lagna_evaluation
                    : null;

                let lagnaVitScore = 5.0;
                let lagnaTier = 'Capable Vessel';
                let lagnaTierColor = '#1d4ed8';
                let lagnaTierBg = '#eff6ff';
                let lagnaTierBorder = '#93c5fd';
                let lagnaArchetype = 'The Steady Navigator';
                let lagnaVerdict = 'Sound, capable engine; achieves solid worldly success and actualizes yogas through deliberate effort.';

                if (backendLagna) {
                    lagnaVitScore = backendLagna.vitality_score || 5.0;
                    lagnaTier = backendLagna.vitality_tier || 'Capable Vessel';
                    lagnaArchetype = backendLagna.archetype || 'The Steady Navigator';
                    lagnaVerdict = backendLagna.verdict || '';
                } else {
                    let p1 = 0, p2 = 0, p3 = 0, p4 = 0, p5 = 0;
                    if (lDigLow.includes('exalt')) p1 += 1.2;
                    else if (lDigLow.includes('moolatrikona')) p1 += 1.0;
                    else if (lDigLow.includes('own')) p1 += 0.8;
                    else if (lDigLow.includes('great friend')) p1 += 0.5;
                    else if (lDigLow.includes('friend')) p1 += 0.25;
                    else if (lDigLow.includes('great enemy')) p1 -= 0.8;
                    else if (lDigLow.includes('enemy')) p1 -= 0.4;
                    else if (lDigLow.includes('debilitat')) p1 -= 1.2;

                    if (sbPct !== null) {
                        if (sbPct >= 130) p1 += (sbRank === 1 ? 1.0 : (sbRank === 2 ? 0.8 : 0.6));
                        else if (sbPct >= 110) p1 += 0.4;
                        else if (sbPct >= 100) p1 += 0.2;
                        else if (sbPct >= 85) p1 -= 0.4;
                        else p1 -= (sbRank === 7 ? 0.9 : 0.6);
                    }

                    if (lordWHouse === 1) p2 += 1.5;
                    else if (lordWHouse === 10) p2 += 1.2;
                    else if (lordWHouse === 4) p2 += 0.8;
                    else if (lordWHouse === 11) p2 += 1.0;
                    else if (lordWHouse === 9) p2 += 1.2;
                    else if (lordWHouse === 5) p2 += 1.0;
                    else if ([6, 8, 12].includes(lordWHouse)) p2 -= 0.8;

                    if (c1Net >= 15.0) p4 += 0.4;
                    else if (c1Net <= -15.0) p4 -= 0.4;
                    if (jupAspectVir > 15.0) p4 += 0.6;
                    if (lordAspectVir > 15.0) p4 += 0.6;

                    if (kartariType === 'Śubha Kartarī') p5 += 0.8;
                    else if (kartariType === 'Pāpa Kartarī') p5 -= 0.8;

                    lagnaVitScore = Math.max(1.0, Math.min(10.0, 5.0 + p1 + p2 + p3 + p4 + p5));
                    lagnaVitScore = Math.round(lagnaVitScore * 10) / 10;
                }

                if (lagnaVitScore >= 8.8) {
                    lagnaTier = 'Sovereign Citadel';
                    lagnaTierColor = '#065f46'; lagnaTierBg = '#ecfdf5'; lagnaTierBorder = '#34d399';
                    lagnaArchetype = 'The Invincible Sovereign';
                } else if (lagnaVitScore >= 7.0) {
                    lagnaTier = 'Robust Horizon';
                    lagnaTierColor = '#15803d'; lagnaTierBg = '#f0fdf4'; lagnaTierBorder = '#86efac';
                    lagnaArchetype = 'The Resilient Architect';
                } else if (lagnaVitScore >= 5.5) {
                    lagnaTier = 'Capable Vessel';
                    lagnaTierColor = '#1d4ed8'; lagnaTierBg = '#eff6ff'; lagnaTierBorder = '#93c5fd';
                    lagnaArchetype = 'The Steady Navigator';
                } else if (lagnaVitScore >= 4.0) {
                    lagnaTier = 'Strained Horizon';
                    lagnaTierColor = '#b45309'; lagnaTierBg = '#fffbeb'; lagnaTierBorder = '#fcd34d';
                    lagnaArchetype = 'The Contemplative Seeker';
                } else {
                    lagnaTier = 'Vulnerable Horizon';
                    lagnaTierColor = '#b91c1c'; lagnaTierBg = '#fef2f2'; lagnaTierBorder = '#fca5a5';
                    lagnaArchetype = 'The Invalid in a Palace';
                }

                // Cusp aspect badges
                let cuspDrishtiBadge = '';
                if (c1Net >= 15.0) {
                    cuspDrishtiBadge = `<span class="badge" style="background:#f0fdf4; color:#15803d; border:1px solid #86efac; font-size:9px; font-weight:bold;">+${c1Net.toFixed(1)} Vir Net Śubha Dṛṣṭi</span>`;
                } else if (c1Net <= -15.0) {
                    cuspDrishtiBadge = `<span class="badge" style="background:#fef2f2; color:#b91c1c; border:1px solid #fca5a5; font-size:9px; font-weight:bold;">${c1Net.toFixed(1)} Vir Net Pāpa Dṛṣṭi</span>`;
                } else {
                    cuspDrishtiBadge = `<span class="badge" style="background:#f8fafc; color:#64748b; border:1px solid #e2e8f0; font-size:9px;">${c1Net >= 0 ? '+' : ''}${c1Net.toFixed(1)} Vir Net Neutral</span>`;
                }
                
                const lagnaAspList = [];
                Object.keys(c1Indiv).forEach(aspG => {
                    const rawV = Math.abs(c1Indiv[aspG].net || c1Indiv[aspG].plus || c1Indiv[aspG].minus || 0);
                    if (rawV > 0) {
                        const fromPlanetData = v_grahas[aspG] || {};
                        const fromDignityBreakdown = fromPlanetData.dignity_breakdown || {};
                        const fromDignityName = fromDignityBreakdown.final_dignity || fromPlanetData.dignity || 'Neutral';
                        const fromDignityClean = fromDignityName.replace("'s Sign", "").replace(" Sign", "").trim();
                        const fromDignityPct = getDignityScore(fromDignityClean, aspG, fromPlanetData.sign || '', fromPlanetData.degree_0_to_30 || 15.0);
                        
                        lagnaAspList.push({
                            from_planet: aspG,
                            raw_virupas: rawV,
                            virupas: rawV,
                            from_dignity_name: fromDignityClean,
                            from_dignity_pct: fromDignityPct,
                            is_debilitated: fromDignityClean.toLowerCase().includes('debilitat'),
                            is_distorted: false
                        });
                    }
                });
                const lagnaDrishtiHtml = renderAspectVisionBadges(lagnaAspList);

                let lagnaAspectGraphsHtml = '';
                if (lagnaAspList && lagnaAspList.length > 0) {
                    const decisiveLg = lagnaAspList.filter(asp => {
                        const rawV = Math.abs(Math.round(asp.raw_virupas !== undefined ? asp.raw_virupas : (asp.virupas || 0)));
                        return rawV >= 20;
                    });
                    if (decisiveLg.length > 0) {
                        const cards = [];
                        decisiveLg.forEach(asp => {
                            const rawV = Math.abs(Math.round(asp.raw_virupas !== undefined ? asp.raw_virupas : (asp.virupas || 0)));
                            const aspG = asp.from_planet;
                            const isNaturalBen = ['Jupiter', 'Venus', 'Mercury', 'Moon'].includes(aspG);
                            const natIcon = isNaturalBen ? '🟢' : '🔴';
                            const optANote = asp.is_distorted ? ' (Option A: Dampened 50%)' : '';
                            const aspStrengthPct = Math.round((rawV / 60.0) * 100);

                            if (v_grahas[aspG] && v_grahas[aspG].longitude !== undefined && v_lagna && v_lagna.longitude !== undefined) {
                                const aspGLon = Number(v_grahas[aspG].longitude);
                                const lgLon = Number(v_lagna.longitude);
                                const aspectedTargets = [
                                    {
                                        name: 'Lagna',
                                        longitude: lgLon,
                                        symbol: '🌅 Lagna',
                                        is_target: true
                                    }
                                ];
                                grahaOrder.forEach(tp => {
                                    if (tp !== aspG && v_grahas[tp] && v_grahas[tp].longitude !== undefined) {
                                        aspectedTargets.push({
                                            name: tp,
                                            longitude: Number(v_grahas[tp].longitude),
                                            symbol: (grahaGlyphs[tp] ? `${grahaGlyphs[tp]} ` : '') + tp.slice(0, 2),
                                            is_target: false
                                        });
                                    }
                                });
                                const incGraph = buildAspectGraphData(aspG, aspGLon, aspectedTargets);
                                if (incGraph) {
                                    cards.push(`
                                        <div class="incoming-aspect-graph-card" style="margin-top: 6px; border: 1px solid #e2e8f0; border-radius: 6px; overflow: hidden; background: #ffffff;">
                                            <div style="background: #f8fafc; padding: 4px 8px; border-bottom: 1px solid #e2e8f0; display: flex; justify-content: space-between; align-items: center; font-size: 10px;">
                                                <div>
                                                    <span>${natIcon} <strong>${aspG}</strong> Aspect on Horizon</span>
                                                    <span style="color: #64748b; font-size: 9px; margin-left: 4px;">(${rawV} Virūpas • ${aspStrengthPct}% strength)</span>
                                                </div>
                                                <div style="font-size: 9.5px; font-weight: 600; color: #475569;">
                                                    ${asp.from_dignity_name || 'Neutral'}${optANote}
                                                </div>
                                            </div>
                                            ${renderContinuousAspectSvg(incGraph, 'Lagna')}
                                        </div>
                                    `);
                                }
                            }
                        });
                        lagnaAspectGraphsHtml = cards.join('');
                    }
                }

                const lagnaTip = `<strong>Ascendant (Lagna / Tanū Bhāva)</strong><br>• Rising degree on the eastern horizon at birth in ${varga}.<br>• The foundational engine and reference frame against which all 12 houses and yogas manifest.`;
                const lgPlacementTip = `<strong>Lagna: ${lgSign} ${lgDeg} (House 1)</strong><br>• <strong>Rising Sign:</strong> Core zodiac archetype of self-expression in ${varga}.<br>• <strong>Ascendant Lord:</strong> <strong>${lgLord}</strong> (Lagneśa).<br>• <strong>Nakshatra:</strong> ${lgNak}.`;
                const lgLordTip = `<strong>Lagneśa (Ascendant Lord): ${lgLord} [${cleanLordDig}]</strong><br>• <strong>5-Fold Dignity:</strong> ${lordDigRaw} in ${lordSign} (${lordWHouse}th house from Lagna).<br>• <strong>Dignity Score:</strong> ${lordDigPct.toFixed(0)}% essential dignity.<br>• <strong>Core Teaching:</strong> The Lagna Lord is the captain of the ship.`;
                const lgHostTip = `<strong>Lagna Lord Host Dispositor: ${lordHost}</strong><br>• <strong>Host Condition:</strong> ${lordHostDig.toFixed(0)}% Dignity • ${lordHostSb.toFixed(0)}% Muscle.<br>• <strong>Anchor Status:</strong> Evaluates foundational support underpinning the captain's vessel.`;
                const lgPowerTip = `<strong>Lagna Vitality & Muscle Engine</strong><br>• <strong>Captain's Shadbala:</strong> ${sbVir} Virūpas (${sbPct !== null ? sbPct + '%' : '--'} of required, Rank #${sbRank || '--'}).<br>• <strong>Horizon Sky-Light:</strong> Net ${c1Net >= 0 ? '+' : ''}${c1Net.toFixed(1)} Virūpas (Benefic: +${c1Plus.toFixed(1)}, Malefic: -${c1Minus.toFixed(1)}).`;
                const lgInfluencesTip = `<strong>Horizon Influences & Aspects</strong><br>• <strong>Occupants in H1:</strong> ${lagnaConj.length > 0 ? lagnaConj.join(', ') : 'None (clean horizon)'}.<br>• <strong>Net Dṛṣṭi:</strong> ${c1Net >= 0 ? '+' : ''}${c1Net.toFixed(1)} Virūpas.<br>• <strong>Enclosure:</strong> ${kartariType}.`;
                const lgAvasthaTip = `<strong>Lagna Bālādi Avasthā & Lord Field</strong><br>• <strong>Biological Age:</strong> ${lgBaladi.state} (${lgBaladi.efficiency_pct}% operational efficiency).<br>• <strong>Term:</strong> ${lgBaladi.sanskrit_term}.<br>• <strong>Lord in House:</strong> Whole Sign H${lordWHouse}${lordCHouse !== lordWHouse ? ' (Campanus Bhava ' + lordCHouse + ')' : ''}.`;
                const lgRawNak = (naks["Lagna"] && naks["Lagna"].nakshatra) || (v_lagna && v_lagna.nakshatra) || '';
                const lgMeta = NAKSHATRA_DATA[lgRawNak] || {};
                const lgNakName = lgMeta.name || lgRawNak || '—';
                const lgNakDeity = lgMeta.deity || '—';
                const lgNakRuler = (naks["Lagna"] && naks["Lagna"].nakshatra_lord) || lgMeta.ruler || '—';
                const lgNakNature = lgMeta.nature || '—';
                const lgNakDrive = lgMeta.core_drive || 'Rising subconscious orientation and vital lens.';
                const lgNakshatraCellHtml = renderNakshatraCell(lgNakName, lgNakDeity, lgNakRuler, lgNakNature, lgNakDrive);

                const lgVitalityTip = `<strong>★ Lagna Vitality Score: ${lagnaVitScore.toFixed(1)} / 10 • ${lagnaTier}</strong><br>• <strong>Archetype:</strong> ${lagnaArchetype}<br>• <strong>Verdict:</strong> ${lagnaVerdict}`;

                const lgShortSign = `${lgSign} ${lgDeg} • H1`;
                const lgExprBadge = `<span class="badge" style="background:#dcfce7; color:#15803d; border:1px solid #86efac; font-size:8.5px; font-weight:700;">High Expression (+25%)</span>`;
                const lgCaptainBadge = `<span class="badge" style="background:${lordDigBg}; color:${lordDigColor}; border:1px solid ${lordDigBorder}; font-weight:bold; font-size:9px; padding:1px 5px;">${cleanLordDig} ${lordDigPct.toFixed(0)}%</span>`;

                tbody.innerHTML += `
                    <tr class="interactive-table-row diagnostic-row" data-type="planet" data-id="Lagna" style="background:#faf7f2; border-bottom: 2px solid #dcb594; cursor: pointer;" onclick="toggleDiagnosticDrawer('drawer-Lagna', this)">
                        <td style="padding: 4px 6px;">
                            <div class="diagnostic-table-cell-2line">
                                <div style="display:flex; align-items:center; gap:4px; font-weight:700; font-size:12px; color:#4a3325;">
                                    <span style="font-size:14px;">🌅</span>
                                    <span class="tooltip-target" data-tooltip="${escapeTooltipAttr(lagnaTip)}" style="cursor:help;">Lagna</span>
                                </div>
                                <div>
                                    <span class="badge" style="background:#e0e7ff; color:#3730a3; border:1px solid #c7d2fe; font-size:8.5px; font-weight:bold;">Tanū Bhāva (H1)</span>
                                </div>
                            </div>
                        </td>
                        <td style="padding: 4px 6px;">
                            <div class="diagnostic-table-cell-2line">
                                <div style="font-size:11px; font-weight:700; color:#1e293b; white-space:nowrap;">
                                    <span class="tooltip-target" data-tooltip="${escapeTooltipAttr(lgPlacementTip)}" style="cursor:help;">${lgShortSign}</span>
                                </div>
                                <div>${lgExprBadge}</div>
                            </div>
                        </td>
                        <td style="padding: 4px 6px; text-align: center;">
                            <div class="diagnostic-table-cell-2line" style="align-items:center;">
                                <div style="font-size:10.5px; font-weight:700; white-space:nowrap;">
                                    Captain: ${lgCaptainBadge}
                                </div>
                                <div style="font-size:9.5px; color:#475569; font-weight:600;">
                                    ↳ Lord: <strong>${lgLord}</strong>
                                </div>
                            </div>
                        </td>
                        <td style="padding: 4px 6px; text-align: center;">
                            <div class="diagnostic-table-cell-2line" style="align-items:center;">
                                <div style="font-size:11px; font-weight:700; color:#1e293b; white-space:nowrap;">Host: <strong>${lordHost}</strong></div>
                                <div>${lordRescueBadge}</div>
                            </div>
                        </td>
                        <td style="padding: 4px 6px;">
                            <div class="diagnostic-table-cell-2line">
                                <div style="font-size:11px; font-weight:700; color:#1e293b; white-space:nowrap;">
                                    <strong>${sbVir}v</strong> <span style="font-size:9.5px; color:${(sbPct || 0) >= 100 ? '#15803d' : '#b91c1c'}; font-weight:600;">(${sbPct !== null ? sbPct + '%' : '--'})</span>
                                </div>
                                <div style="font-size:9px; color:#64748b; font-weight:600; white-space:nowrap;">
                                    ${sbRank ? 'Rank #' + sbRank + ' • ' : ''}Captain Stamina
                                </div>
                            </div>
                        </td>
                        <td style="padding: 4px 6px;">
                            <div class="diagnostic-table-cell-2line">
                                <div>${cuspDrishtiBadge}</div>
                                <div style="font-size:9px; color:#64748b; font-weight:600; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">
                                    ${kartariBadge || (lagnaConj.length > 0 ? 'Yuti: ' + lagnaConj.join(', ') : 'Clean Horizon')}
                                </div>
                            </div>
                        </td>
                        <td style="padding: 4px 6px;">
                            ${lgNakshatraCellHtml}
                        </td>
                        <td style="padding: 4px 6px;">
                            <div class="diagnostic-table-cell-2line">
                                <div>
                                    <span class="badge tooltip-target" style="background:#ffffff; color:#1e293b; border:1px solid #cbd5e1; font-size:9px; font-weight:700; padding:1px 5px; cursor:help;" data-tooltip="${escapeTooltipAttr(lgAvasthaTip)}">${lgBaladi.state} (${lgBaladi.efficiency_pct}%)</span>
                                </div>
                                <div style="font-size:9px; color:#3730a3; font-weight:600;">
                                    Lord in H${lordWHouse}${lordCHouse !== lordWHouse ? ' (➔ B' + lordCHouse + ')' : ''}
                                </div>
                            </div>
                        </td>
                        <td style="padding: 4px 6px; text-align: center;">
                            <div class="diagnostic-table-cell-2line" style="align-items:center;">
                                <div>
                                    <span class="badge tooltip-target" style="background:${lagnaTierBg}; color:${lagnaTierColor}; border:1px solid ${lagnaTierBorder}; font-size:9.5px; font-weight:bold; padding:1px 6px; cursor:help;" data-tooltip="${escapeTooltipAttr(lgVitalityTip)}">★ ${lagnaVitScore.toFixed(1)} • ${lagnaArchetype}</span>
                                </div>
                                <div style="font-size:9.5px; color:#475569; font-weight:600; white-space:nowrap;">
                                    ★ <strong style="color:#1e293b; font-size:11px;">${lagnaVitScore.toFixed(1)}</strong> / 10 • <span style="font-size:8.5px; color:#64748b;">Intent: ${lordDigPct.toFixed(0)}% | Power: ${sbPct !== null ? sbPct : '--'}%</span>
                                </div>
                            </div>
                        </td>
                    </tr>
                    <tr id="drawer-Lagna" class="diagnostic-drawer-row" style="display:none;">
                        <td colspan="9">
                            <div class="drawer-container">
                                <div class="drawer-grid">
                                    <div class="drawer-card">
                                        <div class="drawer-card-title">
                                            <span>👑 Lagna Lord Foundation</span>
                                            <span style="font-size:9.5px; color:#78716c; font-weight:normal;">Lagneśa Authority</span>
                                        </div>
                                        <div class="drawer-card-body">
                                            <div><strong>Lagneśa (Ascendant Lord):</strong> ${lgLord} in ${lordSign} (House ${lordWHouse})</div>
                                            <div style="margin-top:2px;"><strong>Essential Dignity:</strong> <span class="badge" style="background:${lordDigBg}; color:${lordDigColor}; border:1px solid ${lordDigBorder}; font-weight:bold; font-size:9px;">${cleanLordDig} (${lordDigPct.toFixed(0)}%)</span></div>
                                            <div style="margin-top:2px;"><strong>Dispositor of Captain:</strong> ${lordHost} (${lordHostDig.toFixed(0)}% dignity, ${lordHostSb.toFixed(0)}% muscle)</div>
                                            <div style="margin-top:4px; font-size:9.5px; color:#64748b;">The Lagna Lord serves as the captain of the physical vessel. Its dignity and stamina set the baseline capacity to manifest destiny.</div>
                                        </div>
                                    </div>
                                    <div class="drawer-card">
                                        <div class="drawer-card-title">
                                            <span>🏡 Rising Field (Tanū Bhāva)</span>
                                            <span style="font-size:9.5px; color:#78716c; font-weight:normal;">Physical Horizon</span>
                                        </div>
                                        <div class="drawer-card-body">
                                            <div><strong>Rising Sign:</strong> ${lgSign} ${lgDeg} (${(signInfo[lgSign] || {}).element || '--'} • ${(signInfo[lgSign] || {}).quality || '--'})</div>
                                            <div style="margin-top:2px;"><strong>House Structure:</strong> Whole Sign H1, Campanus Bhava 1 Cusp</div>
                                            <div style="margin-top:2px;"><strong>Flanking Enclosure:</strong> ${kartariBadge || kartariType}</div>
                                            <div style="margin-top:4px; font-size:9.5px; color:#64748b;">House 1 governs vitality, self-identity, physical health, and personal perspective. Benefics flanking H2 and H12 shield the horizon.</div>
                                        </div>
                                    </div>
                                    <div class="drawer-card">
                                        <div class="drawer-card-title">
                                            <span>⚡ Horizon Inflowing Aspects</span>
                                            <span style="font-size:9.5px; color:#78716c; font-weight:normal;">Dṛṣṭi on Cusp 1</span>
                                        </div>
                                        <div class="drawer-card-body">
                                            <div><strong>Net Vision on Cusp 1:</strong> ${cuspDrishtiBadge} (Benefic: +${c1Plus.toFixed(1)}v, Malefic: -${c1Minus.toFixed(1)}v)</div>
                                            <div style="margin-top:4px;"><strong>Occupants in H1:</strong> ${lagnaConj.length > 0 ? lgConjBadges : 'None (clean horizon)'}</div>
                                            <div style="margin-top:4px;"><strong>Aspect Rays:</strong></div>
                                            <div style="margin-top:2px;">${lagnaDrishtiHtml}</div>
                                            ${lagnaAspectGraphsHtml}
                                        </div>
                                    </div>
                                    <div class="drawer-card">
                                        <div class="drawer-card-title">
                                            <span>🧠 Biological Fuel &amp; Archetype</span>
                                            <span style="font-size:9.5px; color:#78716c; font-weight:normal;">Physical Vessel</span>
                                        </div>
                                        <div class="drawer-card-body">
                                            <div><strong>Biological Age:</strong> ${lgBaladi.state} (${lgBaladi.efficiency_pct}% operational efficiency)</div>
                                            <div style="font-size:9.5px; color:#64748b; font-style:italic;">${lgBaladi.sanskrit_term}</div>
                                            <div style="margin-top:4px;"><strong>Ascendant Archetype:</strong> <span class="badge" style="background:${lagnaTierBg}; color:${lagnaTierColor}; border:1px solid ${lagnaTierBorder}; font-size:9.5px; font-weight:bold;">${lagnaArchetype}</span></div>
                                            <div style="margin-top:4px; font-style:italic; line-height:1.4; background:#fffdfa; padding:6px 8px; border-left:3px solid #dcb594; border-radius:3px;">🧠 ${lagnaVerdict}</div>
                                        </div>
                                    </div>
                                </div>
                                <div class="drawer-receipt">
                                    <div class="drawer-receipt-header">🧮 Ascendant (Lagna) Vitality Audit Receipt</div>
                                    <pre class="drawer-receipt-content">🧮 LAGNA VITALITY AUDIT RECEIPT
------------------------------------
• Ascendant Degree:  ${lgSign} ${lgDeg} (House 1)
• Captain (Lagneśa): ${lgLord} in ${lordSign} [${cleanLordDig} ${lordDigPct.toFixed(0)}%]
• Captain Muscle:    ${sbVir} Virūpas (${sbPct !== null ? sbPct + '%' : '--'} of required, Rank #${sbRank || '--'})
• Host Bedrock:      ${lordHost} [${lordHostDig.toFixed(0)}% Dignity, ${lordHostSb.toFixed(0)}% Muscle]
• Horizon Skylight:  Net ${c1Net >= 0 ? '+' : ''}${c1Net.toFixed(1)} Virūpas (${kartariType})
• Biological Age:    ${lgBaladi.state} (${lgBaladi.efficiency_pct}% operational efficiency)
------------------------------------
★ Final Vitality:    ★ ${lagnaVitScore.toFixed(1)} / 10 (${lagnaTier})
• Archetype:         ${lagnaArchetype}
• Verdict:           ${lagnaVerdict}</pre>
                                </div>
                            </div>
                        </td>
                    </tr>
                `;
            }

            // 2. Graha Rows (Sun through Ketu)
            const planetaryWars = detectPlanetaryWars(v_grahas, (currentChartData.shadbala || {}));

            const masterLords = (peData && peData.summary && peData.summary.master_lords) || {};
            const lagnaLordPlanet = (masterLords.lagna_lord && masterLords.lagna_lord.planet) || signLords[v_lagna.sign] || (v_lagna && v_lagna.lord) || '';
            const navamshaLordPlanet = (masterLords.navamsha_lord && masterLords.navamsha_lord.planet) || (currentChartData.vargas && currentChartData.vargas.D9 && currentChartData.vargas.D9.lagna && currentChartData.vargas.D9.lagna.lord) || (currentChartData.vargas && currentChartData.vargas.D9 && currentChartData.vargas.D9.lagna && signLords[currentChartData.vargas.D9.lagna.sign]) || '';
            const drekkanaLordPlanet = (masterLords.drekkana_lord && masterLords.drekkana_lord.planet) || (currentChartData.vargas && currentChartData.vargas.D3 && currentChartData.vargas.D3.lagna && currentChartData.vargas.D3.lagna.lord) || (currentChartData.vargas && currentChartData.vargas.D3 && currentChartData.vargas.D3.lagna && signLords[currentChartData.vargas.D3.lagna.sign]) || '';

            grahaOrder.forEach(graha => {
                if (!v_grahas[graha]) return;

                // Master Lords Badges (Phaladeepika 3.11)
                let masterLordBadgesHtml = '';
                const mlBadges = [];
                if (graha === lagnaLordPlanet) {
                    const mlTip = `<strong>👑 Lagneśa (Ascendant Lord - D1)</strong><br>• Governs the D1 rising sign (${v_lagna.sign || '--'}).<br>• <strong>Master Authority:</strong> Physical vitality, constitution, and overall life mastery (Bhāgyavān Prabhu).`;
                    mlBadges.push(`<span class="badge tooltip-target" style="background:#ede9fe; color:#5b21b6; border:1px solid #c4b5fd; font-size:8.5px; font-weight:bold; cursor:help;" data-tooltip="${mlTip}">👑 Lagneśa</span>`);
                }
                if (graha === navamshaLordPlanet) {
                    const d9LgSign = (currentChartData.vargas && currentChartData.vargas.D9 && currentChartData.vargas.D9.lagna && currentChartData.vargas.D9.lagna.sign) || '';
                    const mlTip = `<strong>👑 Navāṁśa Lord (D9 Lord of Fortune)</strong><br>• Rules the Navāṁśa rising sign (${d9LgSign || '--'}).<br>• <strong>Master Authority:</strong> Internal contentment, soul-level dharma, and spiritual happiness (Sukhī).`;
                    mlBadges.push(`<span class="badge tooltip-target" style="background:#fdf4ff; color:#86198f; border:1px solid #f0abfc; font-size:8.5px; font-weight:bold; cursor:help;" data-tooltip="${mlTip}">👑 Navāṁśa Lord</span>`);
                }
                if (graha === drekkanaLordPlanet) {
                    const d3LgSign = (currentChartData.vargas && currentChartData.vargas.D3 && currentChartData.vargas.D3.lagna && currentChartData.vargas.D3.lagna.sign) || '';
                    const mlTip = `<strong>👑 Drekkāṇa Lord (D3 Lord of Courage)</strong><br>• Rules the Drekkāṇa rising sign (${d3LgSign || '--'}).<br>• <strong>Master Authority:</strong> Bodily courage, competitiveness, and decisive worldly drive (Prabhu).`;
                    mlBadges.push(`<span class="badge tooltip-target" style="background:#fef3c7; color:#92400e; border:1px solid #fcd34d; font-size:8.5px; font-weight:bold; cursor:help;" data-tooltip="${mlTip}">👑 Drekkāṇa Lord</span>`);
                }
                if (mlBadges.length > 0) {
                    masterLordBadgesHtml = `<div style="display:flex; flex-wrap:wrap; gap:2px; margin-top:2px;">${mlBadges.join('')}</div>`;
                }
                const gData = v_grahas[graha];
                const glyph = grahaGlyphs[graha] || '★';
                const sign = gData.sign || '--';
                const degVal = Number(gData.degree_0_to_30 || 0.0);
                const deg = formatDeg(degVal);
                const lagnaIdx = signsList.indexOf(v_lagna.sign);
                const pIdx = signsList.indexOf(sign);
                const wHouse = (lagnaIdx >= 0 && pIdx >= 0) ? ((pIdx - lagnaIdx + 12) % 12 + 1) : (gData.house || 1);
                const cHouse = getCampanusHouse(graha, wHouse);
                const nakData = naks[graha];
                const nakStr = (varga === 'D1')
                    ? (nakData ? `${nakData.nakshatra} (${nakData.pada})` : '--')
                    : (nakData ? `D1: ${nakData.nakshatra} (${nakData.pada})` : `${varga} Division`);

                // Motion & Combustion
                const isRetro = !!gData.is_retrograde;
                const isCombust = !!gData.is_combust;
                let statusBadges = '';
                if (isRetro) {
                    const rTip = `<strong>Retrograde [R] (Vakra Motion)</strong><br>• <strong>Motional Power:</strong> Apparent backward movement places ${graha} closest to Earth, largest, and brightest (high Cheṣṭa Bala).<br>• <strong>Psychological Meaning:</strong> Energy turns deeply introspective, non-linear, and unconventional; challenges standard norms and re-evaluates its significations.`;
                    statusBadges += ` <span class="badge tooltip-target" style="background:#fee2e2; color:#991b1b; border:1px solid #fca5a5; font-size:9.5px; font-weight:bold; cursor:help;" data-tooltip="${rTip}">[R]</span>`;
                }
                if (isCombust) {
                    const sunDist = (gData.sun_distance !== undefined && gData.sun_distance !== null) ? Number(gData.sun_distance) : null;
                    const combOrb = (gData.combustion_orb !== undefined && gData.combustion_orb !== null) ? Number(gData.combustion_orb) : null;
                    const combRange = gData.combustion_range || (combOrb ? `${combOrb}°` : '--');
                    const sevNote = (sunDist !== null && sunDist < 3.0) 
                        ? '<strong>Deep Combustion (&lt; 3°):</strong> Severe. Planetary rays are incinerated; outer tangible expression is burned away.' 
                        : '<strong>Moderate Combustion:</strong> Within solar orb. Outward worldly visibility is obscured by the Sun.';
                    
                    const fnRoleLocal = gData.functional_role || (currentChartData.karakas && currentChartData.karakas.functional && currentChartData.karakas.functional[graha]) || null;
                    const rHousesLocal = (fnRoleLocal && fnRoleLocal.ruled_houses) || gData.ruled_houses || [];
                    const rHousesText = rHousesLocal.length > 0 ? `Rules House ${rHousesLocal.join(' &amp; House ')}` : '';
                    
                    const dDeg = sunDist !== null ? Math.floor(sunDist) : 0;
                    const dMin = sunDist !== null ? Math.round((sunDist - dDeg) * 60) : 0;
                    const sunDistFormatted = sunDist !== null ? `${dDeg}° ${dMin.toString().padStart(2, '0')}' (${sunDist.toFixed(2)}°)` : '--';
                    
                    const cTip = `<strong>Combust [C] (Astangata / Asta)</strong><br>` +
                        `• <strong>Distance to Sun:</strong> ${sunDistFormatted}<br>` +
                        `• <strong>Combustion Orbit:</strong> ${combOrb !== null ? combOrb.toFixed(1) + '°' : '--'} threshold (Surya Siddhanta / Kala baseline)<br>` +
                        `• <strong>Art &amp; Science Range:</strong> ${combRange} (Fish &amp; Kurczak: typical combustion window)<br>` +
                        `• <strong>Severity:</strong> ${sevNote}<br>` +
                        (rHousesText ? `• <strong>Ruled Houses:</strong> ${rHousesText} (Combust planets mainly weaken or harm the houses they rule)<br>` : '') +
                        `• <strong>Core Teaching:</strong> Outward ego expression is absorbed and humbled by the solar will; urges the native to seek self-worth internally rather than from external validation.`;
                    statusBadges += ` <span class="badge tooltip-target" style="background:#ffedd5; color:#9a3412; border:1px solid #fed7aa; font-size:9.5px; font-weight:bold; cursor:help;" data-tooltip="${cTip}">[C]</span>`;
                }

                // Moon Illumination & Phase (Graha & Soul column badge)
                let moonPhaseBadgeHtml = '';
                if (graha === 'Moon') {
                    let mPhase = (peData.planets && peData.planets['Moon'] && peData.planets['Moon'].moon_phase)
                        || (peData.summary && peData.summary.moon_phase) || null;

                    // Fallback calculation if mPhase is not directly available
                    if (!mPhase && v_grahas['Sun'] && v_grahas['Moon']) {
                        const sLon = Number(v_grahas['Sun'].longitude || 0.0);
                        const mLon = Number(v_grahas['Moon'].longitude || 0.0);
                        const elong = (mLon - sLon + 360) % 360;
                        const isWax = elong < 180;
                        const illum = (1 - Math.cos(elong * Math.PI / 180)) / 2 * 100;
                        const sType = illum >= 60.0 ? 'bright_benefic' : (illum < 40.0 ? 'dark_malefic' : 'balanced_neutral');
                        const lType = sType === 'bright_benefic' ? 'Bright Benefic Light (Pūrṇendu)' : (sType === 'dark_malefic' ? 'Dim/Dark Malefic Light (Kṣīṇendu)' : 'Balanced Intermediate Light');
                        mPhase = {
                            is_waxing: isWax,
                            paksha: isWax ? 'Shukla' : 'Krishna',
                            paksha_name: isWax ? 'Shukla Paksha (Bright Fortnight / Waxing)' : 'Krishna Paksha (Dark Fortnight / Waning)',
                            elongation_deg: Math.round(elong * 10) / 10,
                            illumination_pct: Math.round(illum * 10) / 10,
                            light_type: lType,
                            terrain_spectrum: sType,
                            badge: `${isWax ? (illum > 80 ? '🌕' : '🌔') : (illum < 20 ? '🌑' : '🌘')} ${isWax ? 'Waxing' : 'Waning'} (${Math.round(illum)}%)`
                        };
                    }

                    if (mPhase) {
                        const isWax = mPhase.is_waxing;
                        const illum = Number(mPhase.illumination_pct || 0);
                        const gFac = Number(mPhase.gradual_factor !== undefined ? mPhase.gradual_factor : (illum >= 50 ? (illum - 50)/50 : (50 - illum)/50));
                        const effMaxMod = (25.0 * gFac).toFixed(1);

                        let badgeBg = '#f1f5f9';
                        let badgeColor = '#475569';
                        let badgeBorder = '#cbd5e1';
                        let spectrumLabel = '';
                        let spectrumDesc = '';

                        if (illum >= 50.0) {
                            badgeBg = illum >= 65.0 ? '#ecfdf5' : '#f0fdfa';
                            badgeColor = illum >= 65.0 ? '#065f46' : '#0f766e';
                            badgeBorder = illum >= 65.0 ? '#a7f3d0' : '#99f6e4';
                            spectrumLabel = `Bright Benefic Spectrum (${(gFac * 100).toFixed(0)}% Light Scale)`;
                            spectrumDesc = `<strong>Continuous Benefic Scaling (Illum ≥ 50%):</strong> Scales gradually from 0.0% at 50% half-moon up to +25.0% at 100% full moon (BPHS 28.10-11 &amp; 35.9). Current factor: <strong>${gFac.toFixed(2)}x</strong> produces <strong>+${effMaxMod}%</strong> in Kendras/Trikonas (1, 4, 5, 9, 10) and <strong>-${effMaxMod}%</strong> in struggle houses (3, 6).`;
                        } else {
                            badgeBg = illum < 35.0 ? '#fef2f2' : '#fffbeb';
                            badgeColor = illum < 35.0 ? '#991b1b' : '#92400e';
                            badgeBorder = illum < 35.0 ? '#fecaca' : '#fde68a';
                            spectrumLabel = `Dark Malefic Spectrum (${(gFac * 100).toFixed(0)}% Dark Scale, Kṣīṇendu)`;
                            spectrumDesc = `<strong>Continuous Malefic Scaling (Illum &lt; 50%):</strong> Scales gradually from 0.0% at 50% half-moon up to +25.0% at 0% new moon (BPHS 3.11 &amp; 28.11). Current factor: <strong>${gFac.toFixed(2)}x</strong> produces <strong>+${effMaxMod}%</strong> in Upachayas (3, 6, 10, 11) and <strong>-${effMaxMod}%</strong> in tender houses (1, 4, 5, 9).`;
                        }

                        const moonTooltip = `<strong>${isWax ? '🌔 Shukla Paksha (Waxing Moon)' : '🌘 Krishna Paksha (Waning Moon)'}</strong><br>` +
                            `• <strong>Illumination:</strong> ${illum.toFixed(1)}% illuminated (${mPhase.elongation_deg}° from Sun)<br>` +
                            `• <strong>Light Category:</strong> ${mPhase.light_type || '--'}<br>` +
                            `• <strong>Continuous Spectrum:</strong> ${spectrumLabel}<br>` +
                            `• <strong>House Terrain Rule:</strong> ${spectrumDesc}<br>` +
                            `• <strong>Scriptural Proof:</strong> BPHS 28.10-11 (Paksha Bala Virupas), BPHS 35.9 (Pūrṇendu vs Kṣīṇendu), Saravali 5.43.`;

                        const phaseIcon = isWax ? (illum > 80 ? '🌕' : '🌔') : (illum < 20 ? '🌑' : '🌘');
                        const phaseName = isWax ? 'Waxing' : 'Waning';

                        moonPhaseBadgeHtml = `<div style="margin-top:2px;">` +
                            `<span class="badge tooltip-target" style="background:${badgeBg}; color:${badgeColor}; border:1px solid ${badgeBorder}; font-size:9px; padding:1px 5px; border-radius:3px; cursor:help; font-weight:600; display:inline-flex; align-items:center; gap:2px;" data-tooltip="${escapeTooltipAttr(moonTooltip)}">` +
                            `${phaseIcon} ${phaseName} ${illum.toFixed(0)}%` +
                            `</span>` +
                            `</div>`;
                    }
                }

                // Cusp shift & House Details
                const hDesc = houseMeanings[wHouse] || `House ${wHouse}`;
                const houseTooltip = `<strong>${hDesc}</strong><br>• Whole Sign house placement counted from Lagna in ${varga}.`;
                let houseHtml = `<span class="tooltip-target" data-tooltip="${houseTooltip}" style="cursor:help;">House ${wHouse}</span>`;
                if (cHouse !== wHouse) {
                    const shiftTip = `<strong>Campanus 3D Bhava Shift (➔ Bhava ${cHouse})</strong><br>• Whole sign is House ${wHouse}, but the 3D Campanus house cusp crosses into Bhava ${cHouse}.<br>• <strong>Interpretation:</strong> Outer circumstances follow House ${wHouse}, while internal psychological experience aligns with Bhava ${cHouse}.`;
                    houseHtml += ` <span class="badge tooltip-target" style="background:#fef3c7; color:#b45309; border:1px solid #fde68a; font-size:10px; font-weight:bold; cursor:help;" data-tooltip="${shiftTip}">➔ Bhava ${cHouse}</span>`;
                }

                // Chara Karaka
                const ck = gData.chara_karaka || (currentChartData.karakas && currentChartData.karakas.chara && currentChartData.karakas.chara[graha]) || null;
                let ckBadge = '';
                if (ck && ck.karaka && ck.karaka !== '—') {
                    let ckStyle = 'background:#f1f5f9; color:#334155; border:1px solid #cbd5e1;';
                    let ckIcon = '';
                    if (ck.karaka === 'AK') {
                        ckStyle = 'background:#fef3c7; color:#92400e; border:1px solid #fcd34d; font-weight:bold;';
                        ckIcon = '👑 ';
                    } else if (ck.karaka === 'AmK') {
                        ckStyle = 'background:#ecfdf5; color:#065f46; border:1px solid #a7f3d0; font-weight:bold;';
                        ckIcon = '💼 ';
                    } else if (ck.karaka === 'DK') {
                        ckStyle = 'background:#fdf2f8; color:#9d174d; border:1px solid #fbcfe8; font-weight:bold;';
                        ckIcon = '💍 ';
                    } else if (ck.karaka === 'BK') {
                        ckStyle = 'background:#eff6ff; color:#1e40af; border:1px solid #bfdbfe; font-weight:600;';
                        ckIcon = '📿 ';
                    } else if (ck.karaka === 'MK') {
                        ckStyle = 'background:#f5f3ff; color:#5b21b6; border:1px solid #ddd6fe; font-weight:600;';
                        ckIcon = '🏡 ';
                    } else if (ck.karaka === 'PK') {
                        ckStyle = 'background:#fefce8; color:#854d0e; border:1px solid #fef08a; font-weight:600;';
                        ckIcon = '🌱 ';
                    } else if (ck.karaka === 'GK') {
                        ckStyle = 'background:#fff1f2; color:#9f1239; border:1px solid #fecdd3; font-weight:600;';
                        ckIcon = '⚔️ ';
                    }
                    const ckTooltip = `<strong>${ckIcon}${ck.name} (${ck.karaka}) • ${ck.title}</strong><br>• Rank: #${ck.rank} (Traversed ${ck.degree_in_sign}° in sign)<br>• ${ck.description}`;
                    ckBadge = `<span class="badge tooltip-target" style="${ckStyle} font-size:9.5px; padding:1px 5px; border-radius:3px; cursor:help;" data-tooltip="${ckTooltip}">${ckIcon}${ck.karaka}</span>`;
                }

                // Functional Role
                const fnRole = gData.functional_role || (currentChartData.karakas && currentChartData.karakas.functional && currentChartData.karakas.functional[graha]) || null;
                let ruledHousesHtml = '';
                let fnBadgesHtml = '';
                if (fnRole && fnRole.ruled_houses && fnRole.ruled_houses.length > 0) {
                    const ruledHousesTip = `<strong>House Rulership: ${fnRole.ruled_houses_str}</strong><br>• ${graha} owns and manages the affairs of House ${fnRole.ruled_houses.join(' and House ')}.<br>• Its placement and dignity directly govern the prosperity of these domains.`;
                    ruledHousesHtml = `<div class="tooltip-target" data-tooltip="${ruledHousesTip}" style="font-size:9.5px; color:#475569; margin-top:2px; cursor:help;">Rules: <strong>${fnRole.ruled_houses_str}</strong></div>`;
                    
                    const bList = [];
                    if (fnRole.is_yogakaraka) {
                        bList.push(`<span class="badge tooltip-target" style="background:#fef3c7; color:#92400e; border:1px solid #fcd34d; font-size:9px; font-weight:bold; cursor:help;" data-tooltip="<strong>⭐ Yogakāraka (Supreme Benefic)</strong><br>• Simultaneously rules Kendra & Trikona (${fnRole.ruled_houses_str})<br>• Unites action with divine grace, conferring high worldly and dharmic achievement.">⭐ Yogakāraka</span>`);
                    } else if (fnRole.is_lagnesha) {
                        bList.push(`<span class="badge tooltip-target" style="background:#ede9fe; color:#5b21b6; border:1px solid #c4b5fd; font-size:9px; font-weight:bold; cursor:help;" data-tooltip="<strong>🛡️ Lagneśa (Ascendant Lord)</strong><br>• Rules House 1 (${fnRole.ruled_houses_str})<br>• Primary protector of self, health, and vitality.">🛡️ Lagneśa</span>`);
                    }
                    
                    if (fnRole.is_maraka && !fnRole.is_yogakaraka) {
                        const marakaH = fnRole.ruled_houses.filter(h => h === 2 || h === 7);
                        bList.push(`<span class="badge tooltip-target" style="background:#f1f5f9; color:#475569; border:1px solid #cbd5e1; font-size:8.5px; font-weight:600; cursor:help;" data-tooltip="<strong>Māraka (H${marakaH.join('/')})</strong><br>• Rules death/transformation threshold houses (H2/H7)<br>• Demands resource stewardship and governs transformative thresholds.">Māraka</span>`);
                    }
                    
                    if (fnRole.is_badhaka && !fnRole.is_yogakaraka && !fnRole.is_lagnesha) {
                        bList.push(`<span class="badge tooltip-target" style="background:#ffedd5; color:#9a3412; border:1px solid #fed7aa; font-size:8.5px; font-weight:600; cursor:help;" data-tooltip="<strong>Bādhaka (Obstacle Maker)</strong><br>• Rules the specific testing house for this sign<br>• Creates subtle karmic friction or blind spots requiring self-reflection.">Bādhaka</span>`);
                    }

                    if (fnRole.is_trishadaya && !fnRole.is_yogakaraka && !fnRole.is_lagnesha) {
                        const trishH = fnRole.ruled_houses.filter(h => [3, 6, 11].includes(h));
                        bList.push(`<span class="badge tooltip-target" style="background:#fef2f2; color:#991b1b; border:1px solid #fecaca; font-size:8.5px; font-weight:600; cursor:help;" data-tooltip="<strong>⚡ Functional Malefic (Trishadāya H${trishH.join('/')})</strong><br>• Rules houses of intense worldly ambition, desire, or competitive drive (BPHS Ch. 34).<br>• Worldly appetite requires strong moral anchoring to prevent self-serving excess.">Trishadāya (H${trishH.join('/')})</span>`);
                    }
                    
                    if (bList.length > 0) {
                        fnBadgesHtml = `<div style="display:flex; flex-wrap:wrap; gap:2px; margin-top:2px;">${bList.join('')}</div>`;
                    }
                }

                // Placement Sign & Nakshatra Tooltips
                const sMeta = signInfo[sign] || { element: '--', quality: '--', ruler: '--' };
                const signTooltip = `<strong>${sign} ${deg} in ${varga}</strong><br>• <strong>Element:</strong> ${sMeta.element} | <strong>Modality:</strong> ${sMeta.quality}<br>• <strong>Sign Lord (Host):</strong> <strong>${sMeta.ruler}</strong>`;
                const nakTooltip = `<strong>Nakshatra: ${nakStr}</strong><br>` + 
                    (nakData ? `• <strong>Sidereal Lunar Mansion:</strong> Anchored to galactic center.<br>• <strong>Navāṁśa Pada:</strong> Pada ${nakData.pada} maps into D9 Navamsha.` : `• Divisional position in ${varga}.`);

                // Dignity (5-fold)
                const isNode = (graha === 'Rahu' || graha === 'Ketu');
                const dBreak = gData.dignity_breakdown || {};
                const signLord = dBreak.sign_lord || signLords[sign] || '--';
                const natRel = dBreak.natural_relationship || 'Neutral';
                const tempRel = dBreak.temporary_relationship || 'Neutral';
                const compRel = dBreak.compound_relationship || 'Neutral';
                const rawDig = dBreak.final_dignity || gData.dignity || '--';
                const cleanDig = rawDig.replace("'s Sign", "").replace(" Sign", "").trim();
                const dignityPct = getDignityScore(cleanDig, graha, sign, degVal);
                const digMeaning = DIGNITY_MEANINGS[rawDig] || DIGNITY_MEANINGS[cleanDig] || DIGNITY_MEANINGS[rawDig + "'s Sign"] || '';

                // Host Dispositor Metrics
                const hostGraha = v_grahas[signLord] || {};
                const hostSign = hostGraha.sign || '';
                const hostDegVal = Number(hostGraha.degree_0_to_30 || 15.0);
                const hostDigRaw = (hostGraha.dignity_breakdown && hostGraha.dignity_breakdown.final_dignity) ? hostGraha.dignity_breakdown.final_dignity : (hostGraha.dignity || 'Neutral');
                const hostDig = getDignityScore(hostDigRaw, signLord, hostSign, hostDegVal);
                const hostSbData = shadbala[signLord] || {};
                const hostSb = Number(hostSbData.Pct_Required_Total !== undefined ? hostSbData.Pct_Required_Total : 100.0);
                const hostVir = Number(hostSbData.Total_Virupas !== undefined ? hostSbData.Total_Virupas : 360.0);

                // Planet Shadbala
                const sb = shadbala[graha] || {};
                const sbPctVal = Number(sb.Pct_Required_Total !== undefined ? sb.Pct_Required_Total : 100.0);

                // Conjunctions & Aspect Weather
                const conjunctList = [];
                grahaOrder.forEach(otherP => {
                    if (otherP !== graha && v_grahas[otherP] && v_grahas[otherP].sign === sign) {
                        conjunctList.push(otherP);
                    }
                });

                // Conjunction Details with Orbs & Precedence
                const conjDetails = [];
                conjunctList.forEach(cp => {
                    const cpG = v_grahas[cp] || {};
                    const cpDeg = (cpG.degree_0_to_30 !== undefined) ? Number(cpG.degree_0_to_30) : 0.0;
                    const degDiff = Math.abs(degVal - cpDeg);
                    const cpSbData = shadbala[cp] || {};
                    const cpSb = Number(cpSbData.Pct_Required_Total !== undefined ? cpSbData.Pct_Required_Total : 100.0);
                    const band = degDiff <= (10.0 / 3.0) ? "Exact (Intimate)" : (degDiff <= 10.0 ? "Moderate" : "Wide");
                    const commands = cpSb > sbPctVal;
                    conjDetails.push({
                        planet: cp,
                        degree_diff: degDiff,
                        orb_band: band,
                        shadbala_pct: cpSb,
                        commands: commands
                    });
                });

                const aspectList = [];
                let netVal = 0;
                let plusVal = 0;
                let minusVal = 0;
                if (adv_aspects && adv_aspects.totals && adv_aspects.totals.planets && adv_aspects.totals.planets[graha]) {
                    const tot = adv_aspects.totals.planets[graha];
                    netVal = tot.net || 0;
                    plusVal = Math.round(tot.plus || 0);
                    minusVal = Math.round(tot.minus || 0);
                }

                // Aspect Details with Option A
                const aspDetails = [];
                if (adv_aspects && adv_aspects.planets && adv_aspects.planets[graha]) {
                    const aspRecv = adv_aspects.planets[graha];
                    grahaOrder.forEach(aspG => {
                        if (aspG !== graha && aspRecv[aspG] && aspRecv[aspG].raw > 3.0) {
                            const aspData = aspRecv[aspG];
                            const rawV = Math.round(aspData.raw);
                            const isPlus = aspData.plus > 0;
                            const aspGData = v_grahas[aspG] || {};
                            const aspDigRaw = (aspGData.dignity_breakdown && aspGData.dignity_breakdown.final_dignity) ? aspGData.dignity_breakdown.final_dignity : (aspGData.dignity || 'Neutral');
                            const aspDegVal = Number(aspGData.degree_0_to_30 || 15.0);
                            const aspDigPct = getDignityScore(aspDigRaw, aspG, aspGData.sign, aspDegVal);
                            const isDeb = (aspDigPct <= 25.0) || aspDigRaw.toLowerCase().includes('debilit') || aspDigRaw.toLowerCase().includes('neecha');
                            aspDetails.push({
                                from_planet: aspG,
                                virupas: isPlus ? rawV : -rawV,
                                raw_virupas: rawV,
                                from_dignity_pct: aspDigPct,
                                from_dignity_name: aspDigRaw,
                                is_debilitated: isDeb
                            });
                        }
                    });
                }

                // Planetary War Details
                const warInfo = planetaryWars[graha] || null;

                // Lajjitadi Avasthas
                const avList = (gData.avasthas && gData.avasthas.lajjitadi) || [];
                const pEval = (peData && peData.planets && peData.planets[graha]) || {};

                // Calibrated Vitality & Archetype Classification
                let vitRes;
                if (varga === 'D1' && pEval.vitality) {
                    vitRes = pEval.vitality;
                } else {
                    vitRes = calculateGrahaVitality(
                        graha, sign, degVal, cleanDig, dignityPct, signLord,
                        hostDig, hostSb, sbPctVal, netVal, conjunctList, avList,
                        isRetro, isCombust, isNode, lagnaSign, lagnaLord,
                        warInfo, conjDetails, aspDetails, fnRole
                    );
                }
                const quad = vitRes.quadrant;
                const netVitality = vitRes.vitality_score;
                const rescueBadge = vitRes.rescue_badge;
                const rescueClass = vitRes.rescue_class;
                const baladi = vitRes.baladi;
                const effDig = vitRes.effective_dignity_pct;
                const effSb = vitRes.effective_shadbala_pct;

                // Cell 3: Essential Dignity HTML
                let digBadge = '';
                const funcDig = pEval.functional_dignity || (pEval.step4_house_field ? {
                    base_dignity_pct: dignityPct,
                    base_dignity_name: cleanDig,
                    terrain_mod_pct: pEval.step4_house_field.terrain_mod_pct || 0,
                    lordship_mod_pct: pEval.step4_house_field.lordship_mod_pct || 0,
                    functional_dignity_pct: pEval.step4_house_field.functional_dignity_pct || dignityPct,
                    math_formula: pEval.step4_house_field.math_formula || '',
                    math_steps: pEval.step4_house_field.math_steps || []
                } : null);

                let funcDigMathBlock = '';
                if (funcDig && varga === 'D1') {
                    const stepItems = (funcDig.math_steps || []).map(step => {
                        let iconMark = '🔹 ';
                        if (step.includes('+')) iconMark = '➕ ';
                        else if (step.includes('-')) iconMark = '➖ ';
                        return `&nbsp;&nbsp;${iconMark}<strong>${step}</strong>`;
                    }).join('<br>');

                    funcDigMathBlock = `<br><br>` +
                        `<div style="border-top:1px dashed rgba(255,255,255,0.35); padding-top:6px; margin-top:6px;">` +
                        `<strong>📐 Functional Dignity & Lordship Evaluation:</strong><br>` +
                        `${stepItems}<br>` +
                        `<div style="margin:4px 0; border-top:1px solid rgba(255,255,255,0.25); width:100%;"></div>` +
                        `➔ <strong>Final Functional Evaluation: ${Number(funcDig.functional_dignity_pct).toFixed(1)}%</strong><br>` +
                        `<span style="font-size:9.5px; opacity:0.9; font-family:monospace;">${escapeTooltipAttr(funcDig.math_formula)}</span>` +
                        `</div>`;
                }

                let digStyle = 'background:#f8fafc; color:#334155; border:1px solid #cbd5e1; font-weight:600;';
                let digIcon = '';
                if (isNode) {
                    digStyle = 'background:#f8fafc; color:#334155; border:1px solid #cbd5e1; font-weight:600;';
                    digIcon = '';
                    const nodeDigTip = `<strong>${graha} Dispositor Reflection (${signLord})</strong><br>` +
                        `• <strong>Why No 5-Fold Dignity:</strong> As shadow mathematical nodes (Chhāyā Grahas), Rahu & Ketu have no physical body or own sign.<br>` +
                        `• <strong>Effective Dignity:</strong> ${effDig.toFixed(0)}% (reflecting host ${signLord}'s ${hostDig.toFixed(0)}% dignity with sign affinity).<br>` +
                        `• <strong>Current Sign:</strong> Residing in ${sign}, mirroring ${signLord}'s state.` +
                        funcDigMathBlock;
                    digBadge = `
                        <div class="tooltip-target" style="text-align:center; cursor:help;" data-tooltip="${escapeTooltipAttr(nodeDigTip)}">
                            <span class="badge" style="background:#f8fafc; color:#334155; border:1px solid #cbd5e1; font-weight:600; font-size:10px;">Proxy (${signLord})</span>
                            <div style="font-size:10px; font-weight:bold; color:#1e293b; margin-top:2px;">${effDig.toFixed(0)}% Dignity</div>
                            ${funcDig && varga === 'D1' ? `<div style="font-size:9.5px; font-weight:700; color:#2563eb; margin-top:1px;" title="Functional Dignity after House Terrain">Func: ${Number(funcDig.functional_dignity_pct).toFixed(1)}%</div>` : `<div style="font-size:9px; color:#64748b;">Chhāyā Reflection</div>`}
                        </div>
                    `;
                } else {
                    let whyReason = '';
                    if (rawDig.includes('Exalt')) {
                        whyReason = `• <strong>Highest Elevation (Uccha):</strong> ${graha} reaches its peak coronation degrees in ${sign}. Operates with uncontested clarity, maximum dignity, and noble confidence.`;
                    } else if (rawDig.includes('Moola')) {
                        whyReason = `• <strong>Executive Office (Moolatrikona):</strong> ${graha} is in its prime mission degrees in ${sign}. Energetic, duty-bound, and happy working on its core purpose.`;
                    } else if (rawDig.includes('Own')) {
                        whyReason = `• <strong>Master of Own Domain (Svastha):</strong> ${graha} is the lord of ${sign}. It is fully at home, independent, secure, and has effortless command over its resources.`;
                    } else if (rawDig.includes('Debilit')) {
                        whyReason = `• <strong>Deepest Valley (Neecha):</strong> ${graha} sits directly opposite its exaltation point. Outer material ego is depleted, redirecting the native to build deep humility and inner non-material resilience.`;
                    } else {
                        whyReason = `• <strong>Sign Lord (Host):</strong> Governed by <strong>${signLord}</strong>.<br>` +
                            `• <strong>Natural Bond (Naisargika):</strong> <em>${natRel}</em>.<br>` +
                            `• <strong>Temporary Bond (Tātkālika):</strong> <em>${tempRel}</em>.<br>` +
                            `• <strong>5-Fold Synthesis (Panchadhā):</strong> ${natRel} + ${tempRel} ➔ <strong>${compRel} (${cleanDig})</strong>.`;
                    }

                    const digTooltip = `<strong>👑 ${graha} Dignity in ${varga}: ${cleanDig} (${dignityPct.toFixed(0)}%)</strong><br>` +
                        `${whyReason}<br><br>` +
                        `• <strong>How it feels:</strong> ${digMeaning}` +
                        funcDigMathBlock;

                    if (rawDig.includes('Exalt')) {
                        digIcon = '👑 '; digStyle = 'background:#dcfce7; color:#15803d; border:1px solid #86efac; font-weight:bold;';
                    } else if (rawDig.includes('Moola')) {
                        digIcon = '🏛️ '; digStyle = 'background:#dcfce7; color:#15803d; border:1px solid #86efac; font-weight:bold;';
                    } else if (rawDig.includes('Own')) {
                        digIcon = '🏡 '; digStyle = 'background:#ecfdf5; color:#047857; border:1px solid #a7f3d0; font-weight:bold;';
                    } else if (rawDig.includes('Great Friend')) {
                        digIcon = '🤝 '; digStyle = 'background:#e0f2fe; color:#0369a1; border:1px solid #bae6fd; font-weight:bold;';
                    } else if (rawDig.includes('Friend')) {
                        digIcon = '🙂 '; digStyle = 'background:#f0f9ff; color:#0284c7; border:1px solid #e0f2fe; font-weight:bold;';
                    } else if (rawDig.includes('Neutral')) {
                        digIcon = '⚖️ '; digStyle = 'background:#f5f5f4; color:#57534e; border:1px solid #e7e5e4; font-weight:600;';
                    } else if (rawDig.includes('Great Enemy')) {
                        digIcon = '⚔️ '; digStyle = 'background:#fee2e2; color:#991b1b; border:1px solid #fca5a5; font-weight:bold;';
                    } else if (rawDig.includes('Enemy')) {
                        digIcon = '⚠️ '; digStyle = 'background:#fff1f2; color:#be123c; border:1px solid #fecdd3; font-weight:bold;';
                    } else if (rawDig.includes('Debilit')) {
                        digIcon = '🔻 '; digStyle = 'background:#fef2f2; color:#b91c1c; border:1px solid #f87171; font-weight:bold;';
                    } else {
                        digStyle = 'color:#78716c;';
                    }

                    digBadge = `
                        <div class="tooltip-target" style="text-align:center; cursor:help;" data-tooltip="${escapeTooltipAttr(digTooltip)}">
                            <span class="badge" style="${digStyle}">${digIcon}${cleanDig}</span>
                            <div style="font-size:10px; font-weight:bold; color:#1e293b; margin-top:2px;">${dignityPct.toFixed(0)}% Dignity</div>
                            ${funcDig && varga === 'D1' ? `<div style="font-size:9.5px; font-weight:700; color:#2563eb; margin-top:1px;" title="Functional Dignity after House Terrain & Lordship">Func: ${Number(funcDig.functional_dignity_pct).toFixed(1)}%</div>` : `<div style="font-size:9px; color:#78716c;">Nat: ${natRel.slice(0,3)} • Tmp: ${tempRel.slice(0,3)}</div>`}
                        </div>
                    `;
                }

                // Cell 4: Host Dispositor HTML
                let hostBadgeStyle = 'background:#f8fafc; color:#475569; border:1px solid #cbd5e1;';
                if (rescueClass === 'exalt') hostBadgeStyle = 'background:#dcfce7; color:#15803d; border:1px solid #86efac; font-weight:bold;';
                else if (rescueClass === 'own') hostBadgeStyle = 'background:#ecfdf5; color:#047857; border:1px solid #a7f3d0; font-weight:bold;';
                else if (rescueClass === 'debil') hostBadgeStyle = 'background:#fee2e2; color:#991b1b; border:1px solid #fca5a5; font-weight:bold;';

                const hostTooltip = `<strong>Host Dispositor: ${signLord} for ${graha}</strong><br>` +
                    `• <strong>Host Essential Dignity:</strong> ${hostDig.toFixed(0)}% (${hostDigRaw})<br>` +
                    `• <strong>Host Shadbala Muscle:</strong> ${hostSb.toFixed(0)}% of required minimum (${hostVir.toFixed(0)} Virūpas)<br>` +
                    `• <strong>Foundational Status:</strong> ${vitRes.rescue_desc}<br>` +
                    `• <strong>Core Principle:</strong> No planet can rise higher than the bedrock its host provides. A fortified host acts as a savior, while a broken host pulls the tenant down.`;

                const hostHtml = `
                    <div style="text-align:center;">
                        <div style="font-weight:600; font-size:11px; color:#1e293b;">Host: ${signLord}</div>
                        <div style="font-size:9.5px; color:#64748b;">${hostDig.toFixed(0)}% Dignity • ${hostSb.toFixed(0)}% Musc</div>
                        <div style="margin-top:2px;">
                            <span class="badge tooltip-target" style="${hostBadgeStyle} font-size:9px; cursor:help;" data-tooltip="${hostTooltip}">${rescueBadge}</span>
                        </div>
                    </div>
                `;

                // Cell 5: Shadbala Power HTML
                let powerHtml = '';
                if (isNode) {
                    const nodeSbTip = `<strong>⚡ ${graha} — Shadbala Proxy Muscle</strong><br>` +
                        `• <strong>Why Proxy:</strong> Shadow nodes (Chhāyā Grahas) have no physical discs or independent orbital mass.<br>` +
                        `• <strong>Inherited Stamina:</strong> Inherits ~${effSb.toFixed(0)}% muscle from host <strong>${signLord}</strong> (${hostVir.toFixed(0)} Virūpas).`;
                    powerHtml = `
                        <div class="tooltip-target" data-tooltip="${nodeSbTip}" style="display:flex; flex-direction:column; gap:2px; cursor:help;">
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                                <strong style="font-size:11.5px;">${effSb.toFixed(0)}%</strong>
                                <span class="badge" style="background:#f1f5f9; color:#475569; font-size:9px; font-weight:600;">Proxy</span>
                            </div>
                            <div style="font-size:10px; color:#15803d; font-weight:bold;">via ${signLord} (${hostVir.toFixed(0)}v)</div>
                            <div style="font-size:9px; color:#64748b;">Chhāyā Proxy Muscle</div>
                        </div>
                    `;
                } else if (sb) {
                    const rupas = sb.Total_Rupas ? sb.Total_Rupas.toFixed(2) + ' R' : '--';
                    const virupas = sb.Total_Virupas ? sb.Total_Virupas.toFixed(1) : '--';
                    const reqVirupas = sb.Required_Total ? sb.Required_Total : '--';
                    const pctVal = sb.Pct_Required_Total ? sb.Pct_Required_Total.toFixed(1) : '--';
                    const rank = sb.Relative_Rank || '--';
                    const isHigh = (sb.Pct_Required_Total >= 115);
                    const isLow = (sb.Pct_Required_Total < 100);

                    let rankBadge = `<span class="badge" style="background:#f1f5f9; color:#334155; font-weight:bold; font-size:9.5px;">#${rank}</span>`;
                    if (rank === 1) rankBadge = `<span class="badge" style="background:#fef3c7; color:#92400e; border:1px solid #fcd34d; font-weight:bold; font-size:9.5px;">👑 Rank 1</span>`;
                    else if (rank === 7) rankBadge = `<span class="badge" style="background:#fee2e2; color:#991b1b; border:1px solid #fca5a5; font-weight:bold; font-size:9.5px;">Rank 7</span>`;

                    const pctColor = isHigh ? '#15803d' : (isLow ? '#b91c1c' : '#0369a1');
                    const capDesc = (sb.Pct_Required_Total >= 125) ? "Abundant" : ((sb.Pct_Required_Total >= 100) ? "Capable" : ((sb.Pct_Required_Total >= 85) ? "Mild Deficit" : "Deficit"));
                    const ishta = (sb.Ishta_Phala !== undefined) ? Number(sb.Ishta_Phala).toFixed(1) : '--';
                    const kashta = (sb.Kashta_Phala !== undefined) ? Number(sb.Kashta_Phala).toFixed(1) : '--';

                    const sbTooltip = `<strong>⚡ ${graha} — Shadbala (6-Fold Potency): ${rupas} (${pctVal}%)</strong><br>` +
                        `• <strong>Chart Ranking:</strong> Rank #${rank} of 7 physical planets<br>` +
                        `• <strong>Total Virūpas:</strong> ${virupas} / ${reqVirupas} required minimum (${pctVal}%)<br>` +
                        `• <strong>Karmic Harvest:</strong> Ishta ${ishta} / Kashta ${kashta}<br><br>` +
                        `<strong>6 Pillars of Strength (Virūpas):</strong><br>` +
                        `• Positional (Sthāna): ${sb.Sthana_Bala !== undefined ? sb.Sthana_Bala.toFixed(1) + 'v' : '--'}<br>` +
                        `• Directional (Dig): ${sb.Dig_Bala !== undefined ? sb.Dig_Bala.toFixed(1) + 'v' : '--'}<br>` +
                        `• Temporal (Kāla): ${(sb.Kala_Bala !== undefined ? sb.Kala_Bala : sb.Kaala_Bala) !== undefined ? (sb.Kala_Bala !== undefined ? sb.Kala_Bala : sb.Kaala_Bala).toFixed(1) + 'v' : '--'}<br>` +
                        `• Motional (Cheṣṭa): ${sb.Cheshta_Bala !== undefined ? sb.Cheshta_Bala.toFixed(1) + 'v' : '--'}<br>` +
                        `• Natural (Naisargika): ${sb.Naisargika_Bala !== undefined ? sb.Naisargika_Bala.toFixed(1) + 'v' : '--'}<br>` +
                        `• Aspectual (Dṛk): ${sb.Drik_Bala !== undefined ? (sb.Drik_Bala >= 0 ? '+' : '') + sb.Drik_Bala.toFixed(1) + 'v' : '--'}`;

                    powerHtml = `
                        <div class="tooltip-target" data-tooltip="${sbTooltip}" style="display:flex; flex-direction:column; gap:2px; cursor:help;">
                            <div style="display:flex; align-items:center; justify-content:space-between; gap:4px;">
                                <strong style="font-size:11.5px;">${virupas}v</strong>
                                ${rankBadge}
                            </div>
                            <div style="font-size:10px; color:${pctColor}; font-weight:bold;">${pctVal}% req (${rupas})</div>
                            <div style="font-size:9px; color:#64748b;">${capDesc} • I: ${ishta} / K: ${kashta}</div>
                        </div>
                    `;
                } else {
                    powerHtml = '<span style="color:#94a3b8; font-size:10px;">—</span>';
                }

                // Cell 6: Aspect Weather & Environmental Badges HTML (ADR-010)
                let netDrishtiBadge = '';
                if (netVal >= 12.0) {
                    const netTip = `<strong>🟢 Net Śubha Dṛṣṭi (+${Math.round(netVal)} Virūpas)</strong><br>• <strong>Śubha Dṛṣṭi (Supportive Vision, +${plusVal}v):</strong> Gentle, supportive rays from friendly allies.<br>• <strong>Pāpa Dṛṣṭi (Confrontational Vision, -${minusVal}v):</strong> Demanding friction from tough aspects.<br>• <strong>Atmosphere:</strong> Clear skies and encouraging vision predominate.`;
                    netDrishtiBadge = `<span class="badge tooltip-target" style="background:#dcfce7; color:#166534; border:1px solid #86efac; font-weight:bold; font-size:9.5px; cursor:help;" data-tooltip="${escapeTooltipAttr(netTip)}">🟢 Net Śubha Dṛṣṭi (+${Math.round(netVal)}v)</span>`;
                } else if (netVal <= -12.0) {
                    const netTip = `<strong>🔴 Net Pāpa Dṛṣṭi (${Math.round(netVal)} Virūpas)</strong><br>• <strong>Pāpa Dṛṣṭi (Confrontational Vision, -${minusVal}v):</strong> Heavy demands, delays, or friction from difficult aspects.<br>• <strong>Śubha Dṛṣṭi (Supportive Vision, +${plusVal}v):</strong> Gentle support received.<br>• <strong>Atmosphere:</strong> High-resistance vision; demands extra discipline and mindful patience.`;
                    netDrishtiBadge = `<span class="badge tooltip-target" style="background:#fee2e2; color:#991b1b; border:1px solid #fca5a5; font-weight:bold; font-size:9.5px; cursor:help;" data-tooltip="${escapeTooltipAttr(netTip)}">🔴 Net Pāpa Dṛṣṭi (${Math.round(netVal)}v)</span>`;
                } else {
                    const netTip = `<strong>⚖️ Net Neutral Vision (${netVal >= 0 ? '+' : ''}${Math.round(netVal)} Virūpas)</strong><br>• <strong>Śubha Dṛṣṭi (Supportive Vision, +${plusVal}v) vs Pāpa Dṛṣṭi (Confrontational Vision, -${minusVal}v)</strong><br>• <strong>Atmosphere:</strong> Moderate, balanced environmental vision without extreme bias.`;
                    netDrishtiBadge = `<span class="badge tooltip-target" style="background:#fef9c3; color:#854d0e; border:1px solid #fef08a; font-weight:bold; font-size:9.5px; cursor:help;" data-tooltip="${escapeTooltipAttr(netTip)}">⚖️ Net Neutral (${netVal >= 0 ? '+' : ''}${Math.round(netVal)}v)</span>`;
                }

                // Planetary War Environmental Badge
                let warBadgeHtml = '';
                const wInfo = vitRes.war_info || warInfo;
                if (wInfo && wInfo.badge) {
                    const wBg = wInfo.is_loser ? '#fee2e2' : '#eff6ff';
                    const wCol = wInfo.is_loser ? '#991b1b' : '#1d4ed8';
                    const wBorder = wInfo.is_loser ? '#fca5a5' : '#93c5fd';
                    const warTip = `<strong>${wInfo.badge}</strong><br>• <strong>Graha Yuddha (Phaladeepika 4.2):</strong> ${wInfo.details}<br>• <strong>Determination:</strong> ${wInfo.reason}<br>• <strong>Vitality Impact:</strong> ${wInfo.war_mod >= 0 ? '+' : ''}${Number(wInfo.war_mod).toFixed(2)} pts.`;
                    warBadgeHtml = `<div><span class="badge tooltip-target" style="background:${wBg}; color:${wCol}; border:1px solid ${wBorder}; font-size:9px; font-weight:bold; cursor:help;" data-tooltip="${escapeTooltipAttr(warTip)}">${wInfo.badge}</span></div>`;
                }

                // Combustion Environmental Badge
                let combustionBadgeHtml = '';
                if (isCombust) {
                    const sunDist = (gData.sun_distance !== undefined && gData.sun_distance !== null) ? Number(gData.sun_distance) : null;
                    const combOrb = (gData.combustion_orb !== undefined && gData.combustion_orb !== null) ? Number(gData.combustion_orb) : null;
                    const dDeg = sunDist !== null ? Math.floor(sunDist) : 0;
                    const dMin = sunDist !== null ? Math.round((sunDist - dDeg) * 60) : 0;
                    const sunDistFormatted = sunDist !== null ? `${dDeg}° ${dMin.toString().padStart(2, '0')}' (${sunDist.toFixed(2)}°)` : '--';
                    const sevNote = (sunDist !== null && sunDist < 3.0) 
                        ? 'Deep Combustion (&lt; 3°): Severe. Outward tangible expression is burned away.' 
                        : 'Moderate Combustion: Within solar orb. Worldly visibility obscured by the Sun.';
                    const fnRoleLocal = gData.functional_role || (currentChartData.karakas && currentChartData.karakas.functional && currentChartData.karakas.functional[graha]) || null;
                    const rHousesLocal = (fnRoleLocal && fnRoleLocal.ruled_houses) || gData.ruled_houses || [];
                    const rHousesText = rHousesLocal.length > 0 ? `Rules House ${rHousesLocal.join(' &amp; House ')}` : '';
                    const combTip = `<strong>🔥 Combust [C] (Asta / Astangata)</strong><br>` +
                        `• <strong>Distance to Sun:</strong> ${sunDistFormatted}<br>` +
                        `• <strong>Combustion Orbit:</strong> ${combOrb !== null ? combOrb.toFixed(1) + '°' : '--'} threshold (Surya Siddhanta baseline)<br>` +
                        `• <strong>Severity:</strong> ${sevNote}<br>` +
                        (rHousesText ? `• <strong>Ruled Houses:</strong> ${rHousesText} (harms outward manifestation)<br>` : '') +
                        `• <strong>Vitality Impact:</strong> -0.50 pts (Sun absorbs outward rays).`;
                    combustionBadgeHtml = `<div><span class="badge tooltip-target" style="background:#ffedd5; color:#9a3412; border:1px solid #fed7aa; font-size:9px; font-weight:bold; cursor:help;" data-tooltip="${escapeTooltipAttr(combTip)}">🔥 Combust (${sunDist !== null ? sunDist.toFixed(1) + '°' : ''} to ☉)</span></div>`;
                }

                // Classical Affliction Badges
                let afflictionBadgesHtml = '';
                const affList = [];
                if (vitRes.guru_chandal_badge) {
                    const gcTip = `<strong>${vitRes.guru_chandal_badge}</strong><br>• <strong>Guru-Chāṇḍāla Yoga (Phaladeepika 6.34):</strong> Conjoined with Rahu, eclipsing traditional philosophy into unconventional, dogmatic, or revolutionary crusades.<br>• <strong>Vitality Impact:</strong> Modifies ethical expression and executive alignment.`;
                    affList.push(`<div><span class="badge tooltip-target" style="background:#fef2f2; color:#991b1b; border:1px solid #fecaca; font-size:8.5px; font-weight:bold; cursor:help;" data-tooltip="${escapeTooltipAttr(gcTip)}">${vitRes.guru_chandal_badge}</span></div>`);
                }
                if (vitRes.guru_ketu_badge) {
                    const gkTip = `<strong>${vitRes.guru_ketu_badge}</strong><br>• <strong>Guru-Ketu Jñāna Yoga:</strong> Conjoined with Ketu, spiritualizing philosophical wisdom into deep inward contemplation, esoteric research, and detachment from worldly dogma.`;
                    affList.push(`<div><span class="badge tooltip-target" style="background:#f0fdf4; color:#166534; border:1px solid #bbf7d0; font-size:8.5px; font-weight:bold; cursor:help;" data-tooltip="${escapeTooltipAttr(gkTip)}">${vitRes.guru_ketu_badge}</span></div>`);
                }
                if (vitRes.vikala_badge) {
                    const vkTip = `<strong>${vitRes.vikala_badge}</strong><br>• <strong>Deeptādi Vikala Avasthā (BPHS Ch. 45):</strong> Besieged by multiple cruel malefics (Bahu-Pāpa-Yuta), inducing severe environmental friction and harshness into planetary expression.<br>• <strong>Vitality Impact:</strong> -0.30 pts.`;
                    affList.push(`<div><span class="badge tooltip-target" style="background:#fff1f2; color:#be123c; border:1px solid #fecdd3; font-size:8.5px; font-weight:bold; cursor:help;" data-tooltip="${escapeTooltipAttr(vkTip)}">${vitRes.vikala_badge}</span></div>`);
                }
                if (affList.length > 0) {
                    afflictionBadgesHtml = affList.join('');
                }

                let yutiHtml = '';
                if (conjDetails.length > 0) {
                    const companionBadges = conjDetails.map(cItem => {
                        const cp = cItem.planet;
                        const isBen = ['Jupiter', 'Venus'].includes(cp);
                        const isMal = ['Saturn', 'Mars', 'Rahu', 'Ketu'].includes(cp);
                        const cColor = isBen ? '#15803d' : (isMal ? '#b91c1c' : '#475569');
                        const orbTag = cItem.orb_band.startsWith("Exact") ? "⚡" : "";
                        const cmdTag = cItem.commands ? "👑 " : "";
                        const nature = isBen ? 'Benefic ally: offers grace, diplomacy, and resources.' : (isMal ? 'Malefic pressure: introduces intensity, demands, or discipline.' : 'Neutral companion.');
                        const cmdNote = cItem.commands ? `<br>• <strong>Commanding Precedence:</strong> ${cp} has higher Shadbala (${cItem.shadbala_pct.toFixed(0)}%) and dominates the house agenda.` : '';
                        const orbNote = `<br>• <strong>Orb:</strong> ${cItem.degree_diff.toFixed(2)}° (${cItem.orb_band})`;
                        const yTip = `<strong>${cmdTag}Conjunction (Yuti) with ${cp}</strong><br>• Sharing the same sign and space in ${varga}.${orbNote}${cmdNote}<br>• ${nature}`;
                        return `<span class="tooltip-target" style="color:${cColor}; font-weight:600; cursor:help;" data-tooltip="${escapeTooltipAttr(yTip)}">${orbTag}${cmdTag}${cp}</span>`;
                    }).join(', ');
                    yutiHtml = `<div><span style="color:#64748b; font-size:9.5px; font-weight:bold;">YUTI:</span> ${companionBadges}</div>`;
                }

                // Cell 6: Aspect Vision (The 3-Tier Filter & 2-Line Gaze Badges)
                let drishtiHtml = '';
                const allAspList = (vitRes.aspect_details && vitRes.aspect_details.length > 0)
                    ? vitRes.aspect_details
                    : (aspDetails || []);

                if (allAspList.length > 0) {
                    drishtiHtml = renderAspectVisionBadges(allAspList);
                } else if (aspectList.length > 0) {
                    drishtiHtml = `<div><span style="color:#64748b; font-size:9.5px; font-weight:bold;">DRISHTI:</span> ${aspectList.join(' ')}</div>`;
                } else {
                    drishtiHtml = '<div style="color:#94a3b8; font-size:9.5px; font-style:italic;">No decisive aspects</div>';
                }

                const influencesHtml = `
                    <div style="display:flex; flex-direction:column; gap:2px; font-size:10.5px;">
                        <div>${netDrishtiBadge}</div>
                        ${warBadgeHtml}
                        ${combustionBadgeHtml}
                        ${afflictionBadgesHtml}
                        ${yutiHtml}
                        ${drishtiHtml}
                    </div>
                `;

                // Cell 7: Avastha & Age HTML
                const baladiTip = `<strong>Bālādi Avasthā: ${baladi.state} (${baladi.efficiency_pct}% Efficiency)</strong><br>` +
                    `• <strong>Phaladeepika 3.10:</strong> Governs physical maturity and biological capacity based on degrees in ${baladi.is_odd_sign ? 'Odd' : 'Even'} signs.<br>` +
                    `• <strong>Sanskrit Class:</strong> ${baladi.sanskrit_term}<br>` +
                    `• <strong>Degree Arc:</strong> ${degVal.toFixed(2)}° in sign.<br>` +
                    `• <strong>Real-World Impact:</strong> Baladi determines how much of a planet's promised fruit can physically manifest before fatigue or inexperience sets in.`;

                let avasthasHtml = '';
                if (isNode) {
                    const nodeAvaTip = `<strong>Chhāyā Catalyst (Rahu / Ketu)</strong><br>` +
                        `• <strong>Classical Citation:</strong> Sage Parashara applies the 6 Lajjitādi feeling states exclusively to the 7 physical Grahas.<br>` +
                        `• <strong>Role:</strong> Nodes act as powerful external agitators and catalysts rather than feeling beings.`;
                    avasthasHtml = `<span class="badge tooltip-target" style="background:#f1f5f9; color:#64748b; border:1px solid #e2e8f0; font-size:9.5px; font-weight:600; cursor:help;" data-tooltip="${nodeAvaTip}">— (Chhāyā Catalyst)</span>`;
                } else if (pEval.calibrated_lajjitadi && pEval.calibrated_lajjitadi.length > 0) {
                    const badges = pEval.calibrated_lajjitadi.map(cItem => {
                        let style = 'background:#f1f5f9; color:#475569; border:1px solid #cbd5e1;';
                        let borderCol = '#cbd5e1';
                        let titleColor = '#475569';
                        if (cItem.base_state === 'Mudita') { style = 'background:#dcfce7; color:#166534; border:1px solid #86efac;'; borderCol = '#86efac'; titleColor = '#166534'; }
                        else if (cItem.base_state === 'Garvita') { style = 'background:#fef3c7; color:#92400e; border:1px solid #fcd34d;'; borderCol = '#fcd34d'; titleColor = '#92400e'; }
                        else if (cItem.base_state === 'Kshudhita') { style = 'background:#fee2e2; color:#991b1b; border:1px solid #fca5a5;'; borderCol = '#fca5a5'; titleColor = '#991b1b'; }
                        else if (cItem.base_state === 'Kshobhita') { style = 'background:#ffedd5; color:#9a3412; border:1px solid #fed7aa;'; borderCol = '#fed7aa'; titleColor = '#9a3412'; }
                        else if (cItem.base_state === 'Lajjita') { style = 'background:#f3e8ff; color:#6b21a8; border:1px solid #d8b4fe;'; borderCol = '#d8b4fe'; titleColor = '#6b21a8'; }
                        else if (cItem.base_state === 'Trushita') { style = 'background:#e0f2fe; color:#0369a1; border:1px solid #bae6fd;'; borderCol = '#bae6fd'; titleColor = '#0369a1'; }

                        let influencerChipsHtml = '';
                        let infLines = '';
                        if (cItem.influencing_planets && cItem.influencing_planets.length > 0) {
                            const chips = cItem.influencing_planets.map(inf => {
                                const isMajor = inf.is_major; // virupas >= 30
                                const chipStyle = isMajor
                                    ? `background:#ffffff; border:1px solid ${borderCol}; color:#1e293b; font-weight:700; font-size:8px;`
                                    : `background:rgba(255,255,255,0.65); border:1px dashed #94a3b8; color:#64748b; font-weight:500; font-size:7.5px;`;
                                const titleStr = `${inf.planet}: ${inf.mechanism} (${inf.virupas.toFixed(1)}v) • Alertness: ${inf.alertness_state} (${inf.alertness_pct}% force)`;
                                return `<span style="${chipStyle} padding:1px 3px; border-radius:3px; display:inline-flex; align-items:center; gap:2px;" title="${titleStr}">${inf.glyph} ${inf.symbol} ${inf.virupas.toFixed(0)}v <span style="font-size:7px; opacity:0.85;">(${inf.alertness_state.split(' ')[0]})</span></span>`;
                            }).join('');
                            influencerChipsHtml = `<div style="display:flex; flex-wrap:wrap; gap:2px; margin-top:2px;">${chips}</div>`;

                            infLines = '<br>• <strong>Influencing Grahas &amp; Force:</strong><br>' + cItem.influencing_planets.map(inf => {
                                const tierBadge = inf.is_major ? '<strong>[MAJOR DRIVER ≥ 30v]</strong>' : '<span style="color:#94a3b8;">[Minor Aspect &lt; 30v]</span>';
                                return `&nbsp;&nbsp;• <strong>${inf.glyph} ${inf.planet}:</strong> ${inf.mechanism} (${inf.symbol} ${inf.virupas.toFixed(1)} / 60.0 Virupas) ${tierBadge}<br>` +
                                       `&nbsp;&nbsp;&nbsp;&nbsp;Alertness: <em>${inf.alertness_state}</em> (${inf.alertness_pct}% force) ➔ Effective Force: <strong>${inf.combined_pct}%</strong>`;
                            }).join('<br>');
                        } else if (cItem.base_state === 'Garvita') {
                            influencerChipsHtml = `<div style="font-size:8px; opacity:0.85; font-style:italic; margin-top:1px;">In ${cItem.condition || 'Own Office'}</div>`;
                        }

                        const bTip = `<strong>${cItem.icon} ${cItem.state}</strong><br>` +
                            `• <strong>Condition:</strong> ${cItem.condition}<br>` +
                            `• <strong>Overall Severity:</strong> ${cItem.severity} (Intensity: ${(cItem.effective_intensity * 100).toFixed(0)}%)` +
                            infLines + `<br>` +
                            `• <strong>Epistemology:</strong> Combining Sage Parashara (BPHS Ch. 45 Graha Drishti Virupas) + Ryan Kurczak Vol 2 (Jagradādi Alertness Calibration).`;

                        return `
                            <div class="tooltip-target" style="${style} border-radius:4px; padding:3px 5px; cursor:help; display:flex; flex-direction:column; gap:1px;" data-tooltip="${escapeTooltipAttr(bTip)}">
                                <div style="display:flex; align-items:center; justify-content:space-between; gap:4px;">
                                    <span style="font-weight:700; font-size:9px; display:flex; align-items:center; gap:3px;">
                                        ${cItem.icon} ${cItem.base_state}
                                    </span>
                                    <span style="font-size:7px; font-weight:700; white-space:nowrap; opacity:0.9; padding:1px 3px; border-radius:2px; background:rgba(255,255,255,0.75);">${cItem.severity.split(' ')[0]}</span>
                                </div>
                                ${influencerChipsHtml}
                            </div>
                        `;
                    });
                    avasthasHtml = `<div style="display:flex; flex-direction:column; gap:3px;">${badges.join('')}</div>`;
                } else if (avList.length === 0) {
                    const neutralAvaTip = `<strong>Neutral (Unstirred Avasthā)</strong><br>` +
                        `• ${graha} is not subjected to starving enemy rays or agitating conjunctions in ${varga}.<br>` +
                        `• Operates in a peaceful, undisturbed baseline state.`;
                    avasthasHtml = `<span class="tooltip-target" style="color:#a8a29e; font-style:italic; font-size:9.5px; cursor:help;" data-tooltip="${neutralAvaTip}">Neutral (Unstirred)</span>`;
                } else {
                    const badges = avList.map(item => {
                        const st = item.state || '';
                        const cond = item.condition || '';
                        let label = st.split(' ')[0];
                        let style = '';
                        let icon = '';
                        let nuanceNote = '';
                        let feelingExp = '';

                        const causeGlyphs = {
                            'Sun': '☉', 'Moon': '☽', 'Mars': '♂', 'Mercury': '☿',
                            'Jupiter': '♃', 'Venus': '♀', 'Saturn': '♄', 'Rahu': '☊', 'Ketu': '☋'
                        };
                        const foundCauses = Object.keys(causeGlyphs).filter(p => cond.includes(p));
                        if (foundCauses.length > 0) {
                            nuanceNote = ` (${foundCauses.map(p => causeGlyphs[p]).join(' ')})`;
                        } else if (cond.includes('Enemy sign')) {
                            nuanceNote = ' (Enemy sign)';
                        } else if (cond.includes('Friend\'s sign')) {
                            nuanceNote = ' (Friend sign)';
                        }

                        if (st.includes('Mudita')) {
                            icon = '🟢'; style = 'background:#dcfce7; color:#166534; border:1px solid #86efac;';
                            feelingExp = 'Delighted & Joyful: Feels welcomed and generous. Delivers gifts happily.';
                        } else if (st.includes('Garvita')) {
                            icon = '👑'; style = 'background:#fef3c7; color:#92400e; border:1px solid #fcd34d;';
                            feelingExp = 'Proud & Noble: Full of royal dignity and command. Operates with regal assurance.';
                        } else if (st.includes('Kshudhita')) {
                            icon = '🔴'; style = 'background:#fee2e2; color:#991b1b; border:1px solid #fca5a5;';
                            feelingExp = 'Starved & Depleted: Feels drained by enemy pressure. Struggles for fuel.';
                        } else if (st.includes('Kshobhita')) {
                            icon = '🟠'; style = 'background:#ffedd5; color:#9a3412; border:1px solid #fed7aa;';
                            feelingExp = 'Agitated & Provoked: Shaken or conflicted by harsh aspects or solar heat.';
                        } else if (st.includes('Lajjita')) {
                            icon = '🟣'; style = 'background:#f3e8ff; color:#6b21a8; border:1px solid #d8b4fe;';
                            feelingExp = 'Ashamed & Inhibited: Feels bashful or self-conscious about expressing gifts.';
                        } else if (st.includes('Trushita')) {
                            icon = '💧'; style = 'background:#e0f2fe; color:#0369a1; border:1px solid #bae6fd;';
                            feelingExp = 'Thirsty & Yearning: Yearns for nourishment from water signs or benefic aspects.';
                        } else {
                            icon = '⚪'; style = 'background:#f1f5f9; color:#475569; border:1px solid #cbd5e1;';
                            feelingExp = 'Special condition.';
                        }

                        const avaTip = `<strong>${icon} ${st}</strong><br>• <strong>Condition:</strong> ${cond}<br>• <strong>Psychological Impact:</strong> ${feelingExp}`;
                        return `<span class="badge tooltip-target" style="${style} font-size:9.5px; cursor:help;" data-tooltip="${escapeTooltipAttr(avaTip)}">${icon} ${label}${nuanceNote}</span>`;
                    });
                    avasthasHtml = `<div style="display:flex; flex-wrap:wrap; gap:2px;">${badges.join('')}</div>`;
                }

                // Deeptādi (Internal Mood) & Jagradādi (Alertness) Badges
                let deepthaadiHtml = '';
                if (pEval.deepthaadi) {
                    const dTip = `<strong>${pEval.deepthaadi.icon} Deeptādi Mood: ${pEval.deepthaadi.state}</strong><br>` +
                        `• <strong>Condition:</strong> ${pEval.deepthaadi.condition}<br>` +
                        `• <strong>Innate Feeling:</strong> ${pEval.deepthaadi.meaning}<br>` +
                        `• <strong>Source:</strong> BPHS Ch. 45.7 / Saravali Ch. 5 / Vol 2 Ch. 4.`;
                    deepthaadiHtml = `<span class="badge tooltip-target" style="background:#f8fafc; color:#334155; border:1px solid #cbd5e1; font-size:9px; font-weight:600; cursor:help;" data-tooltip="${escapeTooltipAttr(dTip)}">${pEval.deepthaadi.badge}</span>`;
                }

                let jagradaadiHtml = '';
                if (pEval.jagradaadi) {
                    const jTip = `<strong>${pEval.jagradaadi.icon} Jagradādi Alertness: ${pEval.jagradaadi.state} (${pEval.jagradaadi.capacity_pct}%)</strong><br>` +
                        `• <strong>House Management:</strong> ${pEval.jagradaadi.house_management}<br>` +
                        `• <strong>Relational Impact:</strong> Exerts ${(pEval.jagradaadi.multiplier * 100).toFixed(0)}% force in Lajjitādi states.<br>` +
                        `• <strong>Source:</strong> BPHS Ch. 45.5 / The Art & Science of Vedic Astrology, Vol 2 Ch. 10.`;
                    jagradaadiHtml = `<span class="badge tooltip-target" style="background:#f8fafc; color:#334155; border:1px solid #cbd5e1; font-size:9px; font-weight:600; cursor:help;" data-tooltip="${escapeTooltipAttr(jTip)}">${pEval.jagradaadi.badge}</span>`;
                }

                const avasthasCellHtml = `
                    <div style="display:flex; flex-direction:column; gap:5px; font-size:10px; min-width:180px;">
                        <!-- Compartment 1: Physical Fuel & Alertness -->
                        <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:4px; padding:3px 5px; display:flex; flex-direction:column; gap:2px;">
                            <div style="font-size:7.5px; font-weight:700; color:#64748b; text-transform:uppercase; letter-spacing:0.5px;">⚡ Fuel &amp; Alertness</div>
                            <div style="display:flex; flex-wrap:wrap; align-items:center; gap:3px;">
                                <span class="badge tooltip-target" style="background:#ffffff; color:#1e293b; border:1px solid #cbd5e1; font-size:9.5px; font-weight:700; cursor:help;" data-tooltip="${escapeTooltipAttr(baladiTip)}">Age: ${baladi.state} (${baladi.efficiency_pct}%)</span>
                                ${jagradaadiHtml}
                            </div>
                            <div style="font-size:8.5px; color:#64748b; font-style:italic;">${baladi.sanskrit_term}</div>
                        </div>

                        <!-- Compartment 2: Innate Dignity Mood (Dīptādi) -->
                        ${deepthaadiHtml ? `
                        <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:4px; padding:3px 5px; display:flex; flex-direction:column; gap:2px;">
                            <div style="font-size:7.5px; font-weight:700; color:#64748b; text-transform:uppercase; letter-spacing:0.5px;">🧘 Innate Mood</div>
                            <div style="display:flex; align-items:center;">${deepthaadiHtml}</div>
                        </div>
                        ` : ''}

                        <!-- Compartment 3: Social & Relational Weather (Lajjitādi) -->
                        <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:4px; padding:3px 5px; display:flex; flex-direction:column; gap:2px;">
                            <div style="font-size:7.5px; font-weight:700; color:#64748b; text-transform:uppercase; letter-spacing:0.5px;">🤝 Social Relations</div>
                            <div>${avasthasHtml}</div>
                        </div>
                    </div>
                `;

                // Cell 8: Functional Archetype & Calibrated Vitality HTML
                const receiptText = (vitRes.calculation_receipt && vitRes.calculation_receipt.receipt_text)
                    ? vitRes.calculation_receipt.receipt_text
                    : '';
                const escReceipt = receiptText
                    .replace(/&/g, '&amp;')
                    .replace(/</g, '&lt;')
                    .replace(/>/g, '&gt;')
                    .replace(/\n/g, '<br>');
                const receiptTooltip = `<div style="font-family:monospace; font-size:10.5px; line-height:1.4; text-align:left;">${escReceipt}</div>`;

                const quadTooltip = `<strong>★ ${graha} Diagnostics</strong><br>` +
                    `• <strong>Inherent Engine:</strong> ${quad.badge} (${quad.tier})<br>` +
                    (quad.subtext ? `• <strong>Engine Matrix:</strong> ${quad.subtext}<br>` : '') +
                    `• <strong>Engine Definition:</strong> ${quad.desc || quad.description || ''}<br>` +
                    (pEval.psychological_narrative ? `• <strong>Psychological Diagnosis (Vol 2):</strong> <em>${pEval.psychological_narrative}</em><br>` : '') +
                    `• <strong>Effective Dignity (Quality):</strong> ${effDig.toFixed(0)}% (Moral integrity & motive)<br>` +
                    `• <strong>Effective Shadbala (Muscle):</strong> ${effSb.toFixed(0)}% of required (Physical horsepower)<br>` +
                    `• <strong>Foundational Host Anchor:</strong> ${rescueBadge} (${vitRes.rescue_desc || vitRes.rescue_status || ''})<br>` +
                    `• <strong>Actualized Vitality:</strong> ★ ${netVitality.toFixed(1)} / 10 (${vitRes.vitality_tier || quad.tier})<br>` +
                    (receiptText ? `<hr style="margin:6px 0; border:0; border-top:1px solid rgba(255,255,255,0.2);"><div style="font-family:monospace; font-size:10px; line-height:1.3; text-align:left;">${escReceipt}</div>` : '');

                const diagHtml = `
                    <div style="text-align:center;">
                        <span class="badge tooltip-target" style="background:${quad.bg}; color:${quad.color}; border:1px solid ${quad.color}44; font-size:10px; font-weight:bold; padding:2px 6px; cursor:help;" data-tooltip="${escapeTooltipAttr(quadTooltip)}">
                            ${quad.badge}
                        </span>
                        ${quad.subtext ? `<div style="font-size:9px; color:#64748b; margin-top:2px; font-weight:500;">${quad.subtext}</div>` : ''}
                        <div style="font-size:10.5px; font-weight:bold; color:#1e293b; margin-top:2px;">
                            <strong style="font-size:13px;">★ ${netVitality.toFixed(1)}</strong> <span style="font-size:10px; color:#64748b;">/ 10</span>
                        </div>
                        <div style="font-size:9px; color:#64748b; font-weight:500; margin-top:1px;">Intent: ${effDig.toFixed(0)}% | Power: ${effSb.toFixed(0)}%</div>
                        <div style="display:flex; align-items:center; justify-content:center; gap:4px; margin-top:2px;">
                            <span style="font-size:9.5px; font-weight:600; color:${vitRes.vitality_col || '#64748b'};">${vitRes.vitality_tier || quad.tier}</span>
                            ${receiptText ? `<span class="badge tooltip-target" style="background:#f8fafc; color:#475569; border:1px solid #cbd5e1; font-size:8.5px; cursor:help; padding:0 3px;" data-tooltip="${escapeTooltipAttr(receiptTooltip)}">🧾 Receipt</span>` : ''}
                        </div>
                        ${pEval.psychological_narrative ? `<div class="tooltip-target" style="font-size:8.5px; color:#475569; font-style:italic; margin-top:3px; max-width:135px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; cursor:help;" data-tooltip="<strong>🧠 Psychological Diagnosis (Vol 2):</strong><br>${escapeTooltipAttr(pEval.psychological_narrative)}">🧠 ${escapeHtml(pEval.psychological_narrative)}</div>` : ''}
                    </div>
                `;
                const pNak = pEval.nakshatra || {};
                const nFallback = NAKSHATRA_DATA[pNak.name || (naks[graha] && naks[graha].nakshatra) || ''] || {};
                const nakName = pNak.name || nFallback.name || (naks[graha] && naks[graha].nakshatra) || '—';
                const nakDeity = pNak.deity || nFallback.deity || '—';
                const nakRuler = pNak.ruler || nFallback.ruler || (naks[graha] && naks[graha].nakshatra_lord) || '—';
                const nakNature = pNak.nature || nFallback.nature || '—';
                const nakCoreDrive = pNak.core_drive || nFallback.core_drive || 'Subconscious motivation and cosmic trajectory.';
                const nakshatraCellHtml = renderNakshatraCell(nakName, nakDeity, nakRuler, nakNature, nakCoreDrive);

                const grahaTip = grahaArchetypes[graha] || `<strong>${graha}</strong>`;

                // Expression mode badge for Col 2
                const exprScore = (pEval.step4_house_field && pEval.step4_house_field.expression_score !== undefined) ? Number(pEval.step4_house_field.expression_score) : 0;
                const exprScoreStr = (exprScore >= 0 ? '+' : '') + Math.round(exprScore) + '%';
                const exprModeStr = pEval.expression_mode || '';
                let expressionBadgeHtml = '';
                if (exprModeStr.includes('High')) {
                    expressionBadgeHtml = `<span class="badge" style="background:#dcfce7; color:#15803d; border:1px solid #86efac; font-size:8.5px; font-weight:700;">High Expression (${exprScoreStr})</span>`;
                } else if (exprModeStr.includes('Mixed')) {
                    expressionBadgeHtml = `<span class="badge" style="background:#f0f9ff; color:#0369a1; border:1px solid #bae6fd; font-size:8.5px; font-weight:700;">Mixed Expression (${exprScoreStr})</span>`;
                } else if (exprModeStr.includes('Low')) {
                    expressionBadgeHtml = `<span class="badge" style="background:#fee2e2; color:#991b1b; border:1px solid #fca5a5; font-size:8.5px; font-weight:700;">Low Expression (${exprScoreStr})</span>`;
                } else {
                    expressionBadgeHtml = `<span class="badge" style="background:#f8fafc; color:#64748b; border:1px solid #cbd5e1; font-size:8.5px; font-weight:600;">Neutral Expression</span>`;
                }

                // Peer shift for Col 3
                let peerShiftVal = 0.0;
                let peerShiftLeader = '';
                if (pEval.functional_dignity && pEval.functional_dignity.peer_shift !== undefined) {
                    peerShiftVal = Number(pEval.functional_dignity.peer_shift);
                } else {
                    peerShiftVal = effDig - dignityPct;
                }
                if (pEval.step3_aspects && pEval.step3_aspects.details && pEval.step3_aspects.details.length > 0) {
                    let maxShift = 0.0;
                    pEval.step3_aspects.details.forEach(d => {
                        if (Math.abs(d.shift) > Math.abs(maxShift)) {
                            maxShift = d.shift;
                            const srcGlyph = grahaGlyphs[d.source] || d.source;
                            if (d.shift > 0) {
                                peerShiftLeader = `Delighted by ${srcGlyph}`;
                            } else {
                                peerShiftLeader = `Starved by ${srcGlyph}`;
                            }
                        }
                    });
                }
                if (!peerShiftLeader) {
                    peerShiftLeader = peerShiftVal > 0 ? 'Supported' : (peerShiftVal < 0 ? 'Pressure' : '');
                }

                let peerShiftHtml = '';
                if (peerShiftVal > 0.5) {
                    peerShiftHtml = `<span style="color:#15803d; font-size:9.5px; font-weight:600;">↳ +${peerShiftVal.toFixed(0)}% (${peerShiftLeader})</span>`;
                } else if (peerShiftVal < -0.5) {
                    peerShiftHtml = `<span style="color:#b91c1c; font-size:9.5px; font-weight:600;">↳ ${peerShiftVal.toFixed(0)}% (${peerShiftLeader})</span>`;
                } else {
                    peerShiftHtml = `<span style="color:#64748b; font-size:9.5px;">↳ Balanced (±0%)</span>`;
                }

                // Decisive Aspect for Col 6 Line 2 (>= 45v) and Background Aspects (20-44v)
                let decisiveAspectBadge = '';
                let bgBadgeHtml = '';
                const decisiveAsps = allAspList.filter(asp => {
                    const rawV = Math.abs(Math.round(asp.raw_virupas !== undefined ? asp.raw_virupas : (asp.virupas || 0)));
                    return rawV >= 45;
                });
                const bgAsps = allAspList.filter(asp => {
                    const rawV = Math.abs(Math.round(asp.raw_virupas !== undefined ? asp.raw_virupas : (asp.virupas || 0)));
                    return rawV >= 20 && rawV < 45;
                });

                let tier2Tip = '';
                if (bgAsps.length > 0) {
                    const t2Lines = bgAsps.map(asp => {
                        const aspG = asp.from_planet;
                        const rawV = Math.abs(Math.round(asp.raw_virupas !== undefined ? asp.raw_virupas : (asp.virupas || 0)));
                        const isNaturalBen = ['Jupiter', 'Venus', 'Mercury', 'Moon'].includes(aspG);
                        const natIcon = isNaturalBen ? '🟢' : '🔴';
                        const visionType = isNaturalBen ? 'Śubha Dṛṣṭi (Supportive Vision)' : 'Pāpa Dṛṣṭi (Confrontational Vision)';
                        const digIcon = getDignityIcon(asp.from_dignity_name);
                        return `• ${natIcon} <strong>${aspG}:</strong> ${rawV} Virūpas (${digIcon} ${asp.from_dignity_name || 'Neutral'}) — <em>${visionType}</em>`;
                    }).join('<br>');
                    tier2Tip = `<strong>Subtle Background Vision (20–44 Virūpas)</strong><br>${t2Lines}<br>• <em>Secondary background vision influencing environmental temperament without decisive dominance.</em>`;
                    bgBadgeHtml = `<span class="tooltip-target" style="color:#64748b; font-size:8.5px; margin-left:3px; cursor:help;" data-tooltip="${escapeTooltipAttr(tier2Tip)}">+${bgAsps.length} bg</span>`;
                }

                if (decisiveAsps.length > 0) {
                    decisiveAsps.sort((a, b) => {
                        const vA = Math.abs(a.raw_virupas !== undefined ? a.raw_virupas : (a.virupas || 0));
                        const vB = Math.abs(b.raw_virupas !== undefined ? b.raw_virupas : (b.virupas || 0));
                        return vB - vA;
                    });
                    const topAsp = decisiveAsps[0];
                    const aspG = topAsp.from_planet;
                    const rawV = Math.abs(Math.round(topAsp.raw_virupas !== undefined ? topAsp.raw_virupas : (topAsp.virupas || 0)));
                    const isNaturalBen = ['Jupiter', 'Venus', 'Mercury', 'Moon'].includes(aspG);
                    const natIcon = isNaturalBen ? '🟢' : '🔴';
                    const dName = (topAsp.from_dignity_name || '').toLowerCase();
                    const isExaltedOrMoola = dName.includes('exalt') || dName.includes('uccha') || dName.includes('moola');
                    const isOwnOrFriend = dName.includes('own') || dName.includes('svastha') || dName.includes('friend') || dName.includes('mitra');
                    const isDebilitated = dName.includes('debilit') || dName.includes('neecha') || Boolean(topAsp.is_debilitated) || Boolean(topAsp.is_distorted);
                    const isEnemy = dName.includes('enemy') || dName.includes('shatru');
                    let synth = '';
                    if (isNaturalBen) {
                        if (isDebilitated || isEnemy) synth = 'Compromised Support';
                        else if (isExaltedOrMoola) synth = 'Pure Grace';
                        else synth = 'Strong Support';
                    } else {
                        if (isDebilitated) synth = 'Toxic Friction';
                        else if (isEnemy) synth = 'Destructive Pressure';
                        else if (isExaltedOrMoola || isOwnOrFriend) synth = 'Constructive Pressure';
                        else synth = 'Harsh Demand';
                    }
                    decisiveAspectBadge = `<span class="aspect-badge-main" style="color:${isNaturalBen ? '#15803d' : '#991b1b'}; font-weight:600; font-size:9px;">${natIcon} ${aspG} (${rawV}v) ↳ ${synth}</span>`;
                } else if (bgAsps.length > 0) {
                    decisiveAspectBadge = `<span class="tooltip-target" style="color:#64748b; font-style:italic; font-size:8.5px; cursor:help;" data-tooltip="${escapeTooltipAttr(tier2Tip)}">${bgAsps.length} background aspect${bgAsps.length > 1 ? 's' : ''} (20–44v)</span>`;
                    bgBadgeHtml = '';
                } else {
                    decisiveAspectBadge = `<span style="color:#94a3b8; font-style:italic; font-size:8.5px;">No decisive gaze (drawer)</span>`;
                }

                // Primary Lajjitadi mood for Col 8 Line 2
                let primaryMoodPill = '';
                if (pEval.calibrated_lajjitadi && pEval.calibrated_lajjitadi.length > 0) {
                    const topMood = pEval.calibrated_lajjitadi[0];
                    let mStyle = 'background:#f1f5f9; color:#475569; border:1px solid #cbd5e1;';
                    if (topMood.base_state === 'Mudita') mStyle = 'background:#dcfce7; color:#166534; border:1px solid #86efac;';
                    else if (topMood.base_state === 'Garvita') mStyle = 'background:#fef3c7; color:#92400e; border:1px solid #fcd34d;';
                    else if (topMood.base_state === 'Kshudhita') mStyle = 'background:#fee2e2; color:#991b1b; border:1px solid #fca5a5;';
                    else if (topMood.base_state === 'Kshobhita') mStyle = 'background:#ffedd5; color:#9a3412; border:1px solid #fed7aa;';
                    else if (topMood.base_state === 'Lajjita') mStyle = 'background:#f3e8ff; color:#6b21a8; border:1px solid #d8b4fe;';
                    else if (topMood.base_state === 'Trushita') mStyle = 'background:#e0f2fe; color:#0369a1; border:1px solid #bae6fd;';
                    primaryMoodPill = `<span class="badge" style="${mStyle} font-size:8.5px; font-weight:700; padding:1px 5px;">${topMood.icon} ${topMood.base_state}</span>`;
                } else if (avList && avList.length > 0) {
                    const firstAv = avList[0];
                    const st = firstAv.state || String(firstAv);
                    let mIcon = '🟡';
                    let mStyle = 'background:#f1f5f9; color:#475569; border:1px solid #cbd5e1;';
                    if (st.includes('Mudita')) { mIcon = '🟢'; mStyle = 'background:#dcfce7; color:#166534; border:1px solid #86efac;'; }
                    else if (st.includes('Garvita')) { mIcon = '👑'; mStyle = 'background:#fef3c7; color:#92400e; border:1px solid #fcd34d;'; }
                    else if (st.includes('Kshudhita')) { mIcon = '🔴'; mStyle = 'background:#fee2e2; color:#991b1b; border:1px solid #fca5a5;'; }
                    else if (st.includes('Kshobhita')) { mIcon = '🟠'; mStyle = 'background:#ffedd5; color:#9a3412; border:1px solid #fed7aa;'; }
                    primaryMoodPill = `<span class="badge" style="${mStyle} font-size:8.5px; font-weight:700; padding:1px 5px;">${mIcon} ${st.split(' ')[0]}</span>`;
                } else {
                    primaryMoodPill = `<span style="color:#94a3b8; font-style:italic; font-size:8.5px;">🟡 Neutral (Unstirred)</span>`;
                }

                // Subcaption for Col 9 Line 2
                const subcaptionText = pEval.subcaption_text || `Intent: ${Math.round(effDig)}% | Power: ${Math.round(effSb)}%`;

                // Drawer Details Construction
                // Box 1: Shadvarga mini table
                let shadvargaHtml = '';
                if (pEval.step1_shadvarga && pEval.step1_shadvarga.varga_breakdown) {
                    const vb = pEval.step1_shadvarga.varga_breakdown;
                    const vWeights = { 'D1': 6, 'D2': 2, 'D3': 4, 'D9': 5, 'D12': 2, 'D30': 1 };
                    const vRows = Object.keys(vWeights).map(vgKey => {
                        const item = vb[vgKey] || {};
                        return `<tr>
                            <td style="font-weight:700;">${vgKey}</td>
                            <td>${item.sign || '--'}</td>
                            <td>${item.dignity || '--'}</td>
                            <td style="text-align:right;">${item.score !== undefined ? item.score.toFixed(1) + '%' : '--'}</td>
                            <td style="text-align:right; color:#78716c;">${vWeights[vgKey]}</td>
                        </tr>`;
                    }).join('');
                    shadvargaHtml = `
                        <table class="drawer-mini-table">
                            <thead>
                                <tr>
                                    <th>Varga</th>
                                    <th>Sign</th>
                                    <th>Dignity</th>
                                    <th style="text-align:right;">Score</th>
                                    <th style="text-align:right;">Pts</th>
                                </tr>
                            </thead>
                            <tbody>${vRows}</tbody>
                        </table>
                        <div style="font-size:9.5px; margin-top:2px;">
                            <strong>Viṁśopaka:</strong> ${pEval.step1_shadvarga.weighted_dignity_pct || dignityPct}% (${pEval.step1_shadvarga.predominance_desc || ''})
                        </div>
                    `;
                } else {
                    shadvargaHtml = `<div><strong>D1 Dignity:</strong> ${cleanDig} (${dignityPct.toFixed(0)}%)</div>`;
                }

                // Itemized peer shifts for Box 1
                let peerShiftsDetailHtml = '';
                if (pEval.step3_aspects && pEval.step3_aspects.details && pEval.step3_aspects.details.length > 0) {
                    const pItems = pEval.step3_aspects.details.map(d => {
                        const shiftNum = (typeof d.shift === 'number') ? d.shift : Number(d.shift || 0);
                        const signChar = shiftNum >= 0 ? '+' : '';
                        const color = shiftNum > 0 ? '#15803d' : (shiftNum < 0 ? '#b91c1c' : '#64748b');
                        return `<div style="display:flex; justify-content:space-between; font-size:9.5px; padding:1px 0;">
                            <span>${d.source || '--'} (${d.type || '--'}):</span>
                            <strong style="color:${color};">${signChar}${shiftNum.toFixed(1)}% (${d.sambhanda || ''})</strong>
                        </div>`;
                    }).join('');
                    peerShiftsDetailHtml = `
                        <div style="margin-top:4px; border-top:1px dashed #e2d7c3; padding-top:4px;">
                            <div style="font-size:9.5px; font-weight:700; color:#4a3325; margin-bottom:2px;">Peer Sambandha Shifts:</div>
                            ${pItems}
                            <div style="margin-top:3px; font-weight:700; color:#1e293b; font-size:10px;">
                                ➔ Final Functional Dignity: ${(typeof effDig === 'number' ? effDig : 50).toFixed(1)}%
                            </div>
                        </div>
                    `;
                }

                // Box 2: House Placement & Lordship Agenda
                const houseType = (pEval.step4_house_field && pEval.step4_house_field.house_type) || `House ${wHouse}`;
                const lordshipMod = (pEval.step4_house_field && pEval.step4_house_field.lordship_mod_pct !== undefined) ? pEval.step4_house_field.lordship_mod_pct : 0;

                const card2Html = `
                    <div><strong>House Placement:</strong> House ${wHouse} (${houseType})</div>
                    <div style="margin-top:4px;"><strong>Lordship Agenda:</strong> <span style="font-weight:700; color:${lordshipMod >= 0 ? '#15803d' : '#b91c1c'};">${lordshipMod >= 0 ? '+' : ''}${lordshipMod}%</span></div>
                    ${ruledHousesHtml}
                    ${fnBadgesHtml}
                    <div style="margin-top:4px;">
                        <strong>Special Conditions:</strong>
                        ${pEval.viparita_badge ? `<div>${pEval.viparita_badge}</div>` : ''}
                        ${pEval.bhava_madhya_badge ? `<div>${pEval.bhava_madhya_badge}</div>` : ''}
                        ${!pEval.viparita_badge && !pEval.bhava_madhya_badge ? '<span style="font-size:9.5px; color:#64748b;">None</span>' : ''}
                    </div>
                    <div style="margin-top:4px; font-weight:700;">
                        Resulting Expression: ${expressionBadgeHtml}
                    </div>
                `;

                // Box 3: Aspect & Conjunction Weather
                let allAspectsRowsHtml = '';
                let incomingGraphsHtml = '';

                // Prepare targets for aspect graph rendering
                const allTargetsData = grahaOrder
                    .filter(tp => v_grahas[tp] && v_grahas[tp].longitude !== undefined)
                    .map(tp => ({
                        name: tp,
                        longitude: Number(v_grahas[tp].longitude),
                        symbol: (grahaGlyphs[tp] ? `${grahaGlyphs[tp]} ` : '') + tp.slice(0, 2)
                    }));

                if (allAspList && allAspList.length > 0) {
                    const decisiveIncoming = [];
                    allAspList.forEach(asp => {
                        const rawV = Math.abs(Math.round(asp.raw_virupas !== undefined ? asp.raw_virupas : (asp.virupas || 0)));
                        if (rawV < 20) return;
                        decisiveIncoming.push(asp);
                    });

                    if (decisiveIncoming.length > 0) {
                        const summaryRows = [];
                        const graphCards = [];

                        decisiveIncoming.forEach(asp => {
                            const rawV = Math.abs(Math.round(asp.raw_virupas !== undefined ? asp.raw_virupas : (asp.virupas || 0)));
                            const aspG = asp.from_planet;
                            const isNaturalBen = ['Jupiter', 'Venus', 'Mercury', 'Moon'].includes(aspG);
                            const natIcon = isNaturalBen ? '🟢' : '🔴';
                            const optANote = asp.is_distorted ? ' (Option A: Dampened 50%)' : '';
                            const aspStrengthPct = Math.round((rawV / 60.0) * 100);

                            summaryRows.push(`
                                <div style="display:flex; justify-content:space-between; font-size:9.5px; padding:1px 0;">
                                    <span>${natIcon} <strong>${aspG}</strong> (${rawV}v / ${aspStrengthPct}%):</span>
                                    <span style="font-weight:600;">${asp.from_dignity_name || 'Neutral'}${optANote}</span>
                                </div>
                            `);

                            // Retrieve precomputed incoming graph or generate dynamically
                            let incGraph = (pEval.incoming_aspect_graphs && pEval.incoming_aspect_graphs[aspG]) || asp.aspect_graph;
                            if (!incGraph && v_grahas[aspG] && v_grahas[aspG].longitude !== undefined) {
                                const aspGLon = Number(v_grahas[aspG].longitude);
                                const aspectedTargets = allTargetsData
                                    .filter(t => t.name !== aspG)
                                    .map(t => ({
                                        ...t,
                                        is_target: (t.name === graha)
                                    }));
                                incGraph = buildAspectGraphData(aspG, aspGLon, aspectedTargets);
                            }

                            if (incGraph) {
                                graphCards.push(`
                                    <div class="incoming-aspect-graph-card" style="margin-top: 6px; border: 1px solid #e2e8f0; border-radius: 6px; overflow: hidden; background: #ffffff;">
                                        <div style="background: #f8fafc; padding: 4px 8px; border-bottom: 1px solid #e2e8f0; display: flex; justify-content: space-between; align-items: center; font-size: 10px;">
                                            <div>
                                                <span>${natIcon} <strong>${aspG}</strong> Aspect Ray</span>
                                                <span style="color: #64748b; font-size: 9px; margin-left: 4px;">(${rawV} Virūpas • ${aspStrengthPct}% strength)</span>
                                            </div>
                                            <div style="font-size: 9.5px; font-weight: 600; color: #475569;">
                                                ${asp.from_dignity_name || 'Neutral'}${optANote}
                                            </div>
                                        </div>
                                        ${renderContinuousAspectSvg(incGraph, graha)}
                                    </div>
                                `);
                            }
                        });

                        allAspectsRowsHtml = summaryRows.join('');
                        incomingGraphsHtml = graphCards.join('');
                    }
                }

                let conjItemsHtml = '';
                if (conjDetails && conjDetails.length > 0) {
                    conjItemsHtml = conjDetails.map(c => {
                        const degStr = (c.degree_diff !== undefined && c.degree_diff !== null) ? Number(c.degree_diff).toFixed(2) + '°' : '';
                        return `<div style="display:flex; justify-content:space-between; font-size:9.5px; padding:1px 0;">
                            <span>${c.commands ? '👑 ' : ''}${c.planet}${degStr ? ` (${degStr})` : ''}:</span>
                            <span>${c.orb_band || ''} ${c.commands ? '• Commands' : ''}</span>
                        </div>`;
                    }).join('');
                }

                // Outgoing aspect graph cast by this planet across the 12 Bhavas
                let outgoingAspectGraphHtml = '';
                let outGraph = (pEval && pEval.aspect_graph) ? pEval.aspect_graph : null;
                if (!outGraph && v_grahas[graha] && v_grahas[graha].longitude !== undefined) {
                    const gLon = Number(v_grahas[graha].longitude);
                    const targetsForOut = allTargetsData.filter(t => t.name !== graha);
                    outGraph = buildAspectGraphData(graha, gLon, targetsForOut);
                }
                if (outGraph) {
                    outgoingAspectGraphHtml = `
                        <div style="margin-top: 8px; border-top: 1px dashed #e2e8f0; padding-top: 6px;">
                            <div style="font-size: 10px; font-weight: 700; color: #475569; margin-bottom: 4px;">
                                👁 Outgoing Aspects Cast by ${graha} (Dṛṣṭi across Zodiac):
                            </div>
                            <div style="border: 1px solid #e2e8f0; border-radius: 6px; overflow: hidden; background: #ffffff;">
                                ${renderContinuousAspectSvg(outGraph, null)}
                            </div>
                        </div>
                    `;
                }

                const card3Html = `
                    <div><strong>Incoming Aspects (Dṛṣṭi):</strong></div>
                    ${allAspectsRowsHtml || '<div style="font-size:9.5px; color:#94a3b8; font-style:italic;">No decisive aspects (≥20v)</div>'}
                    ${incomingGraphsHtml}
                    ${conjItemsHtml ? `<div style="margin-top:6px;"><strong>Conjunctions (Yuti):</strong></div>${conjItemsHtml}` : ''}
                    <div style="margin-top:4px; display:flex; flex-direction:column; gap:2px;">
                        ${warBadgeHtml}
                        ${combustionBadgeHtml}
                        ${afflictionBadgesHtml}
                    </div>
                    ${outgoingAspectGraphHtml}
                `;

                // Box 4: Deep Avasthās & Psychology
                const card4Html = `
                    <div><strong>Biological Maturity (Bālādi):</strong> ${baladi.state} (${baladi.efficiency_pct}%)</div>
                    <div style="font-size:9.5px; color:#64748b; font-style:italic;">${baladi.sanskrit_term}</div>
                    ${pEval.baladi_avastha && pEval.baladi_avastha.is_sandhi ? '<div style="color:#b45309; font-size:9.5px; font-weight:700;">⚠️ Rāśi Sandhi (Edge of Sign)</div>' : ''}
                    ${pEval.baladi_avastha && pEval.baladi_avastha.is_gandanta ? '<div style="color:#b91c1c; font-size:9.5px; font-weight:700;">⚡ Gaṇḍānta Knot (Water-Fire Border)</div>' : ''}
                    <div style="margin-top:4px; display:flex; flex-wrap:wrap; gap:3px;">
                        ${deepthaadiHtml}
                        ${jagradaadiHtml}
                    </div>
                    <div style="margin-top:4px;">
                        <strong>Social Relations (Lajjitādi):</strong>
                        <div style="margin-top:2px;">${avasthasHtml}</div>
                    </div>
                    <div style="margin-top:5px; font-style:italic; line-height:1.4; background:#fffdfa; padding:6px 8px; border-left:3px solid #dcb594; border-radius:3px;">
                        🧠 ${pEval.psychological_narrative || quad.desc || ''}
                    </div>
                `;

                tbody.innerHTML += `
                    <tr class="interactive-table-row diagnostic-row" data-type="planet" data-id="${graha}" style="cursor: pointer;" onclick="toggleDiagnosticDrawer('drawer-${graha}', this)">
                        <td style="padding: 4px 6px;">
                            <div class="diagnostic-table-cell-2line">
                                <div style="display:flex; align-items:center; gap:4px; font-weight:700; font-size:12px; color:#1e293b;">
                                    <span style="font-size:14px;">${glyph}</span>
                                    <span class="tooltip-target" data-tooltip="${escapeTooltipAttr(grahaTip)}" style="cursor:help;">${graha}</span>
                                </div>
                                <div style="display:flex; align-items:center; gap:2px; flex-wrap:nowrap; overflow:hidden;">
                                    ${ckBadge}
                                    ${statusBadges}
                                    ${moonPhaseBadgeHtml}
                                    ${masterLordBadgesHtml}
                                </div>
                            </div>
                        </td>
                        <td style="padding: 4px 6px;">
                            <div class="diagnostic-table-cell-2line">
                                <div style="font-size:11px; font-weight:700; color:#1e293b; white-space:nowrap;">
                                    <span class="tooltip-target" data-tooltip="${escapeTooltipAttr(signTooltip)}" style="cursor:help;">${sign} ${deg} • ${houseHtml}</span>
                                </div>
                                <div>
                                    ${expressionBadgeHtml}
                                </div>
                            </div>
                        </td>
                        <td style="padding: 4px 6px; text-align: center;">
                            <div class="diagnostic-table-cell-2line" style="align-items:center;">
                                <div style="font-size:10.5px; font-weight:700; white-space:nowrap;">
                                    ${isNode ? `<span class="badge" style="${digStyle} font-size:9px; padding:1px 5px;">Proxy (${signLord})</span>` : `<span class="badge" style="${digStyle} font-size:9px; padding:1px 5px;">${digIcon}${cleanDig} ${dignityPct.toFixed(0)}%</span>`}
                                    <span style="color:#64748b; font-size:10px; margin:0 1px;">➔</span>
                                    <strong style="color:#1e293b; font-size:11px;">${Math.round(effDig)}%</strong>
                                </div>
                                <div style="font-size:9px; font-weight:600; white-space:nowrap;">
                                    ${peerShiftHtml}
                                </div>
                            </div>
                        </td>
                        <td style="padding: 4px 6px; text-align: center;">
                            <div class="diagnostic-table-cell-2line" style="align-items:center;">
                                <div style="font-weight:700; font-size:11px; color:#1e293b; white-space:nowrap;">
                                    Host: <strong>${signLord}</strong>
                                </div>
                                <div>
                                    <span class="badge tooltip-target" style="${hostBadgeStyle} font-size:8.5px; font-weight:600; padding:1px 5px; cursor:help;" data-tooltip="${escapeTooltipAttr(hostTooltip)}">${rescueBadge}</span>
                                </div>
                            </div>
                        </td>
                        <td style="padding: 4px 6px;">
                            <div class="diagnostic-table-cell-2line">
                                ${isNode ? `
                                    <div style="font-size:11px; font-weight:700; color:#1e293b; white-space:nowrap;">
                                        <strong>Proxy ${effSb.toFixed(0)}%</strong>
                                    </div>
                                    <div style="font-size:9px; color:#15803d; font-weight:600; white-space:nowrap;">
                                        via ${signLord} (${hostVir.toFixed(0)}v)
                                    </div>
                                ` : `
                                    <div style="font-size:11px; font-weight:700; color:#1e293b; white-space:nowrap;">
                                        <strong>${sb.Total_Virupas ? sb.Total_Virupas.toFixed(1) : '--'}v</strong> <span style="font-size:9.5px; color:${(sb.Pct_Required_Total >= 115) ? '#15803d' : ((sb.Pct_Required_Total < 100) ? '#b91c1c' : '#0369a1')}; font-weight:600;">(${sb.Pct_Required_Total ? sb.Pct_Required_Total.toFixed(1) : '--'}%)</span>
                                    </div>
                                    <div style="font-size:9px; color:#64748b; font-weight:600; white-space:nowrap;">
                                        ${sb.Relative_Rank ? 'Rank #' + sb.Relative_Rank + ' • ' : ''}${(sb.Pct_Required_Total >= 125) ? "Abundant" : ((sb.Pct_Required_Total >= 100) ? "Capable" : ((sb.Pct_Required_Total >= 85) ? "Mild Deficit" : "Deficit"))}
                                    </div>
                                `}
                            </div>
                        </td>
                        <td style="padding: 4px 6px;">
                            <div class="diagnostic-table-cell-2line">
                                <div>
                                    ${netDrishtiBadge}
                                </div>
                                <div style="font-size:9px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:145px;">
                                    ${decisiveAspectBadge}${bgBadgeHtml}
                                </div>
                            </div>
                        </td>
                        <td style="padding: 4px 6px;">
                            ${nakshatraCellHtml}
                        </td>
                        <td style="padding: 4px 6px;">
                            <div class="diagnostic-table-cell-2line">
                                <div>
                                    <span class="badge tooltip-target" style="background:#ffffff; color:#1e293b; border:1px solid #cbd5e1; font-size:9px; font-weight:700; padding:1px 5px; cursor:help;" data-tooltip="${escapeTooltipAttr(baladiTip)}">${baladi.state} (${baladi.efficiency_pct}%)</span>
                                </div>
                                <div style="font-size:9px; font-weight:600; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">
                                    ${primaryMoodPill}
                                </div>
                            </div>
                        </td>
                        <td style="padding: 4px 6px; text-align: center;">
                            <div class="diagnostic-table-cell-2line" style="align-items:center;">
                                <div>
                                    <span class="badge tooltip-target" style="background:${quad.bg}; color:${quad.color}; border:1px solid ${quad.color}44; font-size:9.5px; font-weight:bold; padding:1px 6px; cursor:help;" data-tooltip="${escapeTooltipAttr(quadTooltip)}">${quad.badge}</span>
                                </div>
                                <div style="font-size:9.5px; color:#475569; font-weight:600; white-space:nowrap;">
                                    ★ <strong style="color:#1e293b; font-size:11px;">${netVitality.toFixed(1)}</strong> / 10 • <span style="font-size:8.5px; color:#64748b;">${subcaptionText}</span>
                                </div>
                            </div>
                        </td>
                    </tr>
                    <tr id="drawer-${graha}" class="diagnostic-drawer-row" style="display:none;">
                        <td colspan="9">
                            <div class="drawer-container">
                                <div class="drawer-grid">
                                    <div class="drawer-card">
                                        <div class="drawer-card-title">
                                            <span>👑 Dignity &amp; Peer Bridge</span>
                                            <span style="font-size:9.5px; color:#78716c; font-weight:normal;">Inborn ➔ Functional Mindset</span>
                                        </div>
                                        <div class="drawer-card-body">
                                            ${shadvargaHtml}
                                            <div style="background:#fbf7ef; border:1px solid #ebdcc5; border-radius:4px; padding:4px 6px; margin:4px 0;">
                                                <strong>Host Bedrock (${signLord}):</strong> ${hostDig.toFixed(0)}% dignity • ${hostSb.toFixed(0)}% muscle<br>
                                                <span style="font-size:9.5px; color:#64748b;">${vitRes.rescue_desc || ''}</span>
                                            </div>
                                            ${peerShiftsDetailHtml}
                                        </div>
                                    </div>
                                    <div class="drawer-card">
                                        <div class="drawer-card-title">
                                            <span>🏡 House Placement &amp; Lordship Agenda</span>
                                            <span style="font-size:9.5px; color:#78716c; font-weight:normal;">Layer 4 Operational Field</span>
                                        </div>
                                        <div class="drawer-card-body">
                                            ${card2Html}
                                        </div>
                                    </div>
                                    <div class="drawer-card">
                                        <div class="drawer-card-title">
                                            <span>⚡ Aspect &amp; Conjunction Weather</span>
                                            <span style="font-size:9.5px; color:#78716c; font-weight:normal;">Environmental Pressures</span>
                                        </div>
                                        <div class="drawer-card-body">
                                            ${card3Html}
                                        </div>
                                    </div>
                                    <div class="drawer-card">
                                        <div class="drawer-card-title">
                                            <span>🧠 Deep Avasthās &amp; Psychology</span>
                                            <span style="font-size:9.5px; color:#78716c; font-weight:normal;">Maturity, Mood &amp; Drive</span>
                                        </div>
                                        <div class="drawer-card-body">
                                            ${card4Html}
                                        </div>
                                    </div>
                                </div>
                                <div class="drawer-receipt">
                                    <div class="drawer-receipt-header">🧮 Mathematical Audit Receipt (Zero Double-Counting)</div>
                                    <pre class="drawer-receipt-content">${receiptText ? receiptText : 'No calculation receipt available.'}</pre>
                                </div>
                            </div>
                        </td>
                    </tr>
                `;
            });
        }


// Register with WidgetRegistry if present
if (typeof window !== 'undefined' && window.widgetRegistry) {
    window.widgetRegistry.register('master-diagnostic', {
        id: 'master-diagnostic',
        title: 'Master Graha Diagnostics',
        icon: '★',
        category: 'Diagnostics',
        onUpdate: function(cell, chartData) {
            updateMasterDiagnosticWidget(cell);
        }
    });
}

// Global exports for window context & compatibility
if (typeof window !== 'undefined') {
    window.openFloatingMasterDiagnostic = openFloatingMasterDiagnostic;
    window.updateMasterDiagnosticWidget = updateMasterDiagnosticWidget;
    window.populateMasterDiagnosticTable = populateMasterDiagnosticTable;
    window.toggleDiagnosticDrawer = toggleDiagnosticDrawer;
    window.renderNakshatraCell = renderNakshatraCell;
    window.renderContinuousAspectSvg = renderContinuousAspectSvg;
    window.calculateContinuousDrishti = calculateContinuousDrishti;
    window.DIGNITY_MEANINGS = DIGNITY_MEANINGS;
    window.NAKSHATRA_DATA = NAKSHATRA_DATA;
}
