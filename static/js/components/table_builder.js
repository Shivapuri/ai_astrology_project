/**
 * Declarative Table & UI Component Helpers
 * 
 * Eliminates thousands of lines of fragile imperative string concatenation
 * (`html += '<tr><td>...'`) with reusable, type-safe, declarative helpers.
 */

/**
 * Builds a declarative HTML table string.
 * @param {Object} options
 * @param {Array<{label: string, className?: string, style?: string, colSpan?: number}>} options.headers
 * @param {Array<{cells: Array<{content: string|number, className?: string, style?: string, colSpan?: number}>, className?: string, style?: string, attributes?: string}>} options.rows
 * @param {string} [options.className='data-table']
 * @param {string} [options.style='']
 * @returns {string} HTML table string
 */
function createTable({ headers = [], rows = [], className = 'data-table compact', style = '' }) {
    const ths = headers.map(h => {
        const cls = h.className ? ` class="${h.className}"` : '';
        const st = h.style ? ` style="${h.style}"` : '';
        const cs = h.colSpan ? ` colspan="${h.colSpan}"` : '';
        return `<th${cls}${st}${cs}>${h.label}</th>`;
    }).join('');

    const thead = headers.length > 0 ? `<thead><tr>${ths}</tr></thead>` : '';

    const trs = rows.map(row => {
        const rCls = row.className ? ` class="${row.className}"` : '';
        const rSt = row.style ? ` style="${row.style}"` : '';
        const rAttrs = row.attributes ? ` ${row.attributes}` : '';
        const cells = (row.cells || []).map(c => {
            const cCls = c.className ? ` class="${c.className}"` : '';
            const cSt = c.style ? ` style="${c.style}"` : '';
            const cCs = c.colSpan ? ` colspan="${c.colSpan}"` : '';
            const cContent = c.content !== undefined && c.content !== null ? c.content : '';
            return `<td${cCls}${cSt}${cCs}>${cContent}</td>`;
        }).join('');
        return `<tr${rCls}${rSt}${rAttrs}>${cells}</tr>`;
    }).join('');

    const tbody = `<tbody>${trs}</tbody>`;
    const stAttr = style ? ` style="${style}"` : '';

    return `<table class="${className}"${stAttr}>${thead}${tbody}</table>`;
}

/**
 * Creates a standard Astra badge component.
 */
function createBadge({ text, className = 'badge', style = '', icon = '', title = '' }) {
    const titleAttr = title ? ` title="${title}"` : '';
    const styleAttr = style ? ` style="${style}"` : '';
    const iconHtml = icon ? `<span class="badge-icon">${icon}</span> ` : '';
    return `<span class="${className}"${styleAttr}${titleAttr}>${iconHtml}${text}</span>`;
}

/**
 * Creates a standard Astra progress bar / strength meter.
 */
function createStrengthMeter({ value, max = 100, label = '', color = '#15803d', height = '6px' }) {
    const pct = Math.min(100, Math.max(0, (value / max) * 100));
    return `
        <div class="strength-meter-wrap" style="display:flex; flex-direction:column; gap:2px; min-width:60px;">
            ${label ? `<span style="font-size:12px; color:#6b5a4b;">${label}</span>` : ''}
            <div style="background:#e5dccb; border-radius:3px; height:${height}; width:100%; overflow:hidden;">
                <div style="background:${color}; width:${pct}%; height:100%; border-radius:3px; transition:width 0.3s ease;"></div>
            </div>
        </div>
    `;
}

/**
 * Master Map of 12 Zodiac Line Glyphs with Unicode Variation Selector 15 (\uFE0E)
 * Forces all Chromium and CoreText engines into monochrome text presentation.
 */
const ZODIAC_LINE_GLYPHS = (typeof window !== 'undefined' && window.AstroCatalog)
    ? Object.fromEntries(window.AstroCatalog.signs.map(s => [s.name, s.glyph]))
    : {
        'Aries':       '\u2648\uFE0E',
        'Taurus':      '\u2649\uFE0E',
        'Gemini':      '\u264A\uFE0E',
        'Cancer':      '\u264B\uFE0E',
        'Leo':         '\u264C\uFE0E',
        'Virgo':       '\u264D\uFE0E',
        'Libra':       '\u264E\uFE0E',
        'Scorpio':     '\u264F\uFE0E',
        'Sagittarius': '\u2650\uFE0E',
        'Capricorn':   '\u2651\uFE0E',
        'Aquarius':    '\u2652\uFE0E',
        'Pisces':      '\u2653\uFE0E'
    };

const PLANET_LINE_GLYPHS = (typeof window !== 'undefined' && window.AstroCatalog)
    ? Object.fromEntries(Object.entries(window.AstroCatalog.planets).map(([k, v]) => [k, v.glyph]))
    : {
        'Sun':     '☉',
        'Moon':    '☽',
        'Mars':    '♂',
        'Mercury': '☿',
        'Jupiter': '♃',
        'Venus':   '♀',
        'Saturn':  '♄',
        'Rahu':    '☊',
        'Ketu':    '☋',
        'Uranus':  '♅',
        'Neptune': '♆',
        'Pluto':   '♇',
        'Chiron':  '⚷',
        'Ceres':   '⚳',
        'Pallas':  '⚴',
        'Juno':    '⚵',
        'Vesta':   '⚶',
        'Lagna':   'Asc'
    };

function renderZodiacGlyph(signName) {
    const s = (typeof window !== 'undefined' && window.AstroCatalog) ? window.AstroCatalog.getSign(signName) : null;
    const glyph = s ? s.glyph : (ZODIAC_LINE_GLYPHS[signName] || '');
    return `<span class="zodiac-line-glyph" title="${signName}">${glyph}</span>`;
}

function renderPlanetGlyph(planetName) {
    const p = (typeof window !== 'undefined' && window.AstroCatalog) ? window.AstroCatalog.getPlanet(planetName) : null;
    const glyph = p ? p.glyph : (PLANET_LINE_GLYPHS[planetName] || planetName);
    return `<span class="graha-glyph" title="${planetName}">${glyph}</span>`;
}

function renderPlanetPill(planetName, degStr = '', isRetro = false) {
    const p = (typeof window !== 'undefined' && window.AstroCatalog) ? window.AstroCatalog.getPlanet(planetName) : null;
    const abbr = p ? p.abbr : planetName.substring(0, 2);
    const col = p ? p.colorToken : 'var(--text-heading)';
    const retro = isRetro ? ' <span style="color:var(--status-alert); font-size:12px; font-weight:bold;">R</span>' : '';
    return `<span class="micro-tag" style="color:${col}; margin:1px 2px;">${abbr}${retro}</span>`;
}

function createStatusIndicator({ type = 'neutral', text = '', value = '', tooltip = '' }) {
    const titleAttr = tooltip ? ` title="${tooltip}"` : '';
    const valHtml = value ? ` <strong>${value}</strong>` : '';
    return `<span class="status-indicator ${type}"${titleAttr}><span class="indicator-dot"></span><span>${text}${valHtml}</span></span>`;
}

function createMicroTag({ text, variant = 'neutral', tooltip = '' }) {
    const titleAttr = tooltip ? ` title="${tooltip}"` : '';
    return `<span class="micro-tag tag-${variant}"${titleAttr}>${text}</span>`;
}

// Attach globally for browser use & export for ES modules
if (typeof window !== 'undefined') {
    window.TableBuilder = window.TableBuilder || {};
    window.TableBuilder.createTable = createTable;
    window.TableBuilder.createBadge = createBadge;
    window.TableBuilder.createStrengthMeter = createStrengthMeter;
    window.TableBuilder.ZODIAC_LINE_GLYPHS = ZODIAC_LINE_GLYPHS;
    window.TableBuilder.PLANET_LINE_GLYPHS = PLANET_LINE_GLYPHS;
    window.TableBuilder.renderZodiacGlyph = renderZodiacGlyph;
    window.TableBuilder.renderPlanetGlyph = renderPlanetGlyph;
    window.TableBuilder.renderPlanetPill = renderPlanetPill;
    window.TableBuilder.createStatusIndicator = createStatusIndicator;
    window.TableBuilder.createMicroTag = createMicroTag;
}

if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        createTable,
        createBadge,
        createStrengthMeter,
        ZODIAC_LINE_GLYPHS,
        PLANET_LINE_GLYPHS,
        renderZodiacGlyph,
        renderPlanetGlyph,
        renderPlanetPill,
        createStatusIndicator,
        createMicroTag
    };
}
