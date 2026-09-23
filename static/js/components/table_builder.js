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
            ${label ? `<span style="font-size:10px; color:#6b5a4b;">${label}</span>` : ''}
            <div style="background:#e5dccb; border-radius:3px; height:${height}; width:100%; overflow:hidden;">
                <div style="background:${color}; width:${pct}%; height:100%; border-radius:3px; transition:width 0.3s ease;"></div>
            </div>
        </div>
    `;
}

// Attach globally for browser use & export for ES modules
if (typeof window !== 'undefined') {
    window.TableBuilder = {
        createTable,
        createBadge,
        createStrengthMeter
    };
}

if (typeof module !== 'undefined' && module.exports) {
    module.exports = { createTable, createBadge, createStrengthMeter };
}
