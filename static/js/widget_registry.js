/**
 * Astra Pluggable Widget Registry
 * 
 * Provides a decoupled, dynamic registration and lifecycle manager
 * for all astrological views, charts, and diagnostic widgets.
 */

class WidgetRegistry {
    constructor() {
        this.widgets = new Map();
    }

    /**
     * Register a new astrological widget definition.
     * @param {string} id - Unique identifier (e.g. 'shadbala-table', 'master-diagnostic')
     * @param {Object} definition - Widget configuration object:
     *   - id: string
     *   - title: string
     *   - icon: string (emoji or glyph)
     *   - category: string ('Strengths', 'Diagnostics', 'Charts', 'Yogas', etc.)
     *   - templateId: string (optional, defaults to 'tmpl-' + id)
     *   - isScrollable: boolean (optional)
     *   - render: function(container, chartData, options)
     *   - onUpdate: function(cell, chartData)
     *   - onResize: function(cell) (optional)
     */
    register(id, definition) {
        if (!id || typeof id !== 'string') {
            throw new Error(`WidgetRegistry: Invalid widget ID: ${id}`);
        }
        this.widgets.set(id, {
            id,
            templateId: definition.templateId || `tmpl-${id}`,
            isScrollable: !!definition.isScrollable,
            ...definition
        });
    }

    get(id) {
        return this.widgets.get(id);
    }

    has(id) {
        return this.widgets.has(id);
    }

    getAll() {
        return Array.from(this.widgets.values());
    }

    getByCategory(category) {
        return this.getAll().filter(w => w.category === category);
    }

    /**
     * Renders or mounts a widget inside a container element.
     */
    renderWidget(id, container, chartData, options = {}) {
        const def = this.get(id);
        if (!def) {
            container.innerHTML = `<div class="p-4 text-muted" style="padding:15px; color:#888;">Widget [${id}] not registered</div>`;
            return false;
        }

        if (container && container.dataset) {
            container.dataset.widget = id;
        }

        if (typeof def.render === 'function') {
            def.render(container, chartData, options);
            return true;
        } else if (typeof def.onUpdate === 'function') {
            def.onUpdate(container, chartData);
            return true;
        }
        return false;
    }

    /**
     * Updates an active widget cell when chart data changes.
     */
    updateWidget(cell, chartData) {
        const id = cell?.dataset?.widget;
        if (!id) return false;
        const def = this.get(id);
        if (def && typeof def.onUpdate === 'function') {
            def.onUpdate(cell, chartData);
            return true;
        }
        return false;
    }
}

// Attach globally for browser environment & export for ES modules
if (typeof window !== 'undefined') {
    window.WidgetRegistry = WidgetRegistry;
    window.widgetRegistry = window.widgetRegistry || new WidgetRegistry();
}

if (typeof module !== 'undefined' && module.exports) {
    module.exports = { WidgetRegistry };
}
