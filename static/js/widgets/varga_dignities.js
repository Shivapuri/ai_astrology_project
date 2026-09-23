/**
 * Astra Varga Dignities Matrix Widget
 *
 * Displays a comprehensive grid of the 16 Shodasa Vargas and the Panchadha Sambandha
 * (5-fold compound dignity) of the 7 classical planets (Sun through Saturn).
 */

function updateVargaDignitiesTable(cell, chartData) {
    const currentData = chartData || window.currentChartData;
    let tbodies = [];

    if (cell) {
        const tbody = cell.querySelector('tbody');
        if (tbody) tbodies.push(tbody);
    } else {
        tbodies = Array.from(document.querySelectorAll('#vargaDignitiesTable tbody, .grid-cell[data-widget="dignities"] tbody'));
    }

    if (tbodies.length === 0) return;

    const vargasList = [
        'D1', 'D2', 'D3', 'D4', 'D7', 'D9', 'D10', 'D12',
        'D16', 'D20', 'D24', 'D27', 'D30', 'D40', 'D45', 'D60'
    ];
    const planets = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn'];

    const mapDig = (fullStr) => {
        if (!fullStr) return '-';
        const s = fullStr.toLowerCase();
        if (s.includes('exalt')) return 'EX';
        if (s.includes('debilitat')) return 'DB';
        if (s.includes('mool') || s.includes('mul')) return 'MT';
        if (s.includes('own')) return 'OH';
        if (s.includes('great friend')) return 'GF';
        if (s.includes('great enemy')) return 'GE';
        if (s.includes('friend')) return 'F';
        if (s.includes('enemy')) return 'E';
        if (s.includes('neutral')) return 'N';
        return '-';
    };

    const getFullName = (abbrev) => {
        const map = {
            'EX': 'Exalted',
            'DB': 'Debilitated',
            'MT': 'Moolatrikona',
            'OH': 'Own House',
            'GF': 'Great Friend',
            'GE': 'Great Enemy',
            'F':  'Friend',
            'E':  'Enemy',
            'N':  'Neutral'
        };
        return map[abbrev] || abbrev;
    };

    const getColorForAbbrev = (abbrev) => {
        switch (abbrev) {
            case 'EX': return 'var(--dignity-exalted, #16a34a)';
            case 'DB': return 'var(--dignity-debilitated, #dc2626)';
            case 'OH':
            case 'MT': return 'var(--dignity-own, #0284c7)';
            case 'GF': return 'var(--dignity-great-friend, #0d9488)';
            case 'GE': return 'var(--dignity-great-enemy, #ea580c)';
            case 'F':  return 'var(--dignity-friend, #22c55e)';
            case 'E':  return 'var(--dignity-enemy, #f97316)';
            case 'N':  return 'var(--dignity-neutral, #64748b)';
            default:   return 'inherit';
        }
    };

    const vargaDescriptions = {
        'D1': 'Rāśi (Physical Existence & Baseline Life)',
        'D2': 'Horā (Wealth, Resources & Speech)',
        'D3': 'Drekkāṇa (Siblings, Courage & Vitality)',
        'D4': 'Chaturthāṁśa (Home, Fixed Property & Comfort)',
        'D7': 'Saptāṁśa (Children, Progeny & Creative Flow)',
        'D9': 'Navāṁśa (Dharma, Marriage, Inner Essence & Destiny)',
        'D10': 'Daśāṁśa (Career, Leadership & Social Impact)',
        'D12': 'Dvādaśāṁśa (Parents, Heritage & Ancestral Lineage)',
        'D16': 'Ṣoḍaśāṁśa (Vehicles, Pleasures & Heart Comfort)',
        'D20': 'Viṁśāṁśa (Spiritual Life, Devotion & Meditation)',
        'D24': 'Chaturviṁśāṁśa (Higher Education, Skill & Scholarship)',
        'D27': 'Saptaviṁśāṁśa (Subconscious Strengths & Vulnerabilities)',
        'D30': 'Triṁśāṁśa (Misfortune, Hidden Flaws & Health Trials)',
        'D40': 'Khavedāṁśa (Auspicious / Inauspicious Karmic Blessings)',
        'D45': 'Akṣavedāṁśa (Moral Character, Integrity & Purity)',
        'D60': 'Ṣaṣṭyāṁśa (Root Past-Life Karmas & Destiny Seeds)'
    };

    tbodies.forEach(tbody => {
        tbody.innerHTML = '';

        vargasList.forEach(v => {
            const tr = document.createElement('tr');
            tr.style.cursor = 'pointer';
            tr.title = `Click to view ${v} in main chart`;
            tr.onclick = function() {
                const chartCell = (window.currentActiveCell && window.currentActiveCell.dataset.widget === 'chart')
                    ? window.currentActiveCell
                    : document.querySelector('.grid-cell[data-widget="chart"]');
                if (chartCell) {
                    const select = chartCell.querySelector('.varga-select');
                    if (select) {
                        select.value = v;
                        if (typeof window.updateWidget === 'function') {
                            window.updateWidget(chartCell);
                        }
                    }
                }
            };

            const vDesc = vargaDescriptions[v] || v;
            let html = `<td class="tooltip-target" data-tooltip="<strong>${v} — ${vDesc}</strong><br>Click to display this harmonic chart in the main window." style="cursor:help;"><strong>${v.replace('D', '')}</strong></td>`;

            const vData = (currentData && currentData.vargas) ? currentData.vargas[v] : null;
            if (vData && vData.grahas) {
                planets.forEach(p => {
                    let digStr = '';
                    let tooltip = '';
                    if (vData.grahas[p] && vData.grahas[p].dignity_breakdown) {
                        const d = vData.grahas[p].dignity_breakdown;
                        digStr = d.final_dignity;
                        const abbrev = mapDig(digStr);
                        const fullName = getFullName(abbrev);

                        tooltip = `<strong>${p} in ${v} (${vData.grahas[p].sign})</strong><br>• <strong>Dignity:</strong> ${fullName} (${abbrev})<br>• <strong>Host Lord:</strong> ${d.sign_lord}<br>• <strong>Natural Bond:</strong> ${d.natural_relationship}<br>• <strong>Temporary Position:</strong> ${d.temporary_relationship}<br>• <strong>Compound Relationship:</strong> ${d.compound_relationship}`;
                    }

                    const abbrev = mapDig(digStr);
                    const color = getColorForAbbrev(abbrev);

                    html += `<td class="tooltip-target" data-tooltip="${tooltip}" style="color:${color}; font-weight:bold; cursor:help;">${abbrev}</td>`;
                });
            } else {
                html += `<td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td>`;
            }
            tr.innerHTML = html;
            tbody.appendChild(tr);
        });
    });
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
        if (typeof window.refreshContextInfoForCell === 'function') {
            window.refreshContextInfoForCell(ic);
        }
    });
}

// Register with WidgetRegistry
if (typeof window !== 'undefined' && window.widgetRegistry) {
    window.widgetRegistry.register('dignities', {
        id: 'dignities',
        title: 'Dignities in Vargas',
        icon: '👑',
        category: 'Dignity',
        onUpdate: function(cell, chartData) {
            updateVargaDignitiesTable(cell, chartData);
        }
    });
}

// Global exports
if (typeof window !== 'undefined') {
    window.updateVargaDignitiesTable = updateVargaDignitiesTable;
    window.openVargaFromInspector = openVargaFromInspector;
}
