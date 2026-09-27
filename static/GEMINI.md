# Astra Frontend Architecture & Typography Protocol

This rulebook applies to all files inside `static/` and `templates/`. It enters memory specifically when frontend presentation code is modified.

## 1. Strict Typography Floor (Rule of 9–10 PT)
- **Hard Floor**: NEVER write or generate CSS font sizes below `12px` (equivalent to 9 pt).
- **Scale Standard**:
  - Micro-badges, secondary tags, and captions: **`12px`** (9 pt floor).
  - Table data cells, body text, and mini-tables: **`13px` – `13.5px`** (~10 pt).
  - Headers, card titles, and section labels: **`14px` – `16px`** (10.5 pt – 12 pt).
- Sub-pixel text (`7px`, `8px`, `9px`, `9.5px`, `10px`, `10.5px`, `11px`) is strictly prohibited.

## 2. Separation of Chart Zooming vs. Table Scrolling
- **Astrological Charts (SVGs)**: Zoom and pan are handled by `initWidgetChartZoomAndPan`. Chart zooming must remain responsive and unconstrained.
- **Data Tables & Diagnostics**: Must NEVER be shrunk using CSS `transform: scale(...)`. Tables must render at 100% true scale with `overflow: auto` (horizontal and vertical scrolling) and sticky headers/anchor columns.

## 3. Waveform & 360° Graph Clearance
- A 360° zodiac continuous aspect curve requires horizontal resolution to display 13 house/degree markers without collision.
- Never squeeze full-zodiac continuous wave graphs into a 1-column slot in a 4-column grid (sub-350px).
- Continuous wave cards must span at least 2 columns (`grid-column: span 2`, >= 600px) or provide an instant full-width expansion button (`[⛶]`) and dedicated tab view.

## 4. Pluggable Widget Registry & Zero Monolith
- All new views must register through `window.widgetRegistry.register(id, definition)`.
- No inline `<style>` tags in HTML. All styles belong in `static/css/` tokens and modular sheets.
- Always verify visually via Playwright screenshot (`python screenshot.py`) before completing tasks.

## 5. Modular Jinja2 Partials
- **Navigation & Toolbars**: Reside in `templates/partials/` (e.g. `top_toolbar.html`, `context_menu.html`).
- **Modal Dialogs**: Every modal must be an isolated partial in `templates/partials/modals/<modal_name>.html` and included using `{% include 'partials/modals/<modal_name>.html' %}`.
- **Widget Templates**: Reusable `<template id="tmpl-...">` DOM blueprints must reside in `templates/widget_templates/tmpl_<name>.html` and be registered in `templates/partials/widget_templates.html`.

## 6. Structured CSS Token System
- Inline `<style>` blocks in HTML are forbidden.
- All styling must be added to the appropriate stylesheet in `static/css/`:
  - `base.css`: Global typography, layout reset, and custom scrollbars.
  - `pergamon-theme.css`: Pergamon color tokens (warm parchment palette, antique accents, badges).
  - `layout-grid.css`: Split.js gutters, resizable cell geometry, and toolbars.
  - `widgets.css`: Shared tables, sticky headers, strength meters, and SVG chart wrappers.
  - `modals.css`: Draggable floating dialogs, maximize overlays, and dropdown menus.

## 7. Declarative Table Builder (`static/js/components/table_builder.js`)
- Avoid manual, error-prone HTML string concatenation (`+= '<tr><td>...'`).
- Use declarative helpers (`createTable`, `createBadge`, `createStrengthMeter`) to ensure consistent DOM markup and safe attribute rendering.

## 8. On-Demand Lazy SVG Generation (`/api/chart/<native_id>/svg`)
- Never eagerly generate hundreds of SVG permutations upfront on the backend.
- Initial chart loads pre-render only the active workspace views. Additional vargas, modes (`symbol`, `english`, `devanagari`), styles (`south`, `north`, `circular`, `biwheel`), and root perspectives (`Lagna`, `Moon`, `Sun`) must be requested on-demand via the `/api/chart/<native_id>/svg` endpoint.

## 9. Monochrome Line Glyphs (STIX Two Math Standard)
- **Eliminate OS Emoji Boxes**: Never allow native OS color emoji presentation (such as Apple's purple zodiac squares or colored emoji planets) in tables, headers, or diagnostics.
- **Unicode Variation Selector 15 (`\uFE0E`)**: All astrological zodiac and planetary symbols must be suffixed with `\uFE0E` to force monochrome text presentation.
- **Font Stack & Spec**: Use `var(--font-astro-glyphs)` (`"STIX Two Math", "Cambria Math", "DejaVu Sans", "Noto Sans Symbols 2", "Apple Symbols", "Segoe UI Symbol", sans-serif`) and `font-variant-emoji: text;`.
- **Classes**: Apply `.zodiac-line-glyph`, `.graha-glyph`, or `.glyph-symbol` to ensure clean monochrome rendering across macOS, Windows, and Linux/CI.

## 10. De-Badging & Emoji Purge Protocol
- **De-Badging Routine Data**: Routine tabular information (degrees, sign coordinates, house numbers, dispositor names, nakshatras) must NEVER be enclosed in colorful rounded pill badges (`.pill`, `.badge-pill`). Present clean tabular text with `font-variant-numeric: tabular-nums;`.
- **Micro-Tag Semantic Scope**: Badges are strictly reserved for high-salience status indicators:
  - Functional dignity: `.micro-tag.tag-benefic`, `.micro-tag.tag-malefic`, `.micro-tag.tag-neutral`, `.micro-tag.tag-alert`.
  - Chara Karakas: `.micro-tag.tag-karaka`.
  - Minimum font floor: All `.micro-tag` elements must strictly be at least `12px` (Rule 1).
- **Emoji Purge**: Consumer emojis (`🔴`, `🟢`, `🟠`, `🟡`, `👑`, `💣`, `✨`, `🔥`, `🛡`, `😴`, `💤`, `⚡`, `⚔`) are strictly prohibited in data tables, drawers, and diagnostics.
- **Semantic Micro-Dots**: Use `.status-indicator` with `.indicator-dot` (6px dot) for net aspect balance, dignity shifts, and vitality scores.
- **Typographic Arrows**: Replace heavy or non-standard arrows (`➔`, `⬅`) with standard Unicode typographic arrows (`→`, `←`, `↔`).
- **Exact Master Diagnostic Table Geometry**: The Master Diagnostic table (`tmpl_master_diagnostic.html` and `master_diagnostic.js`) has exactly **9 columns**. All 9 columns must be preserved with authoritative Sanskrit/Jyotish and Western technical headings; never drop the 9th column (*Archetype & Vitality*).

## 11. Single Source of Truth (SSOT) for Astrological Catalog
- **Zero Local Dictionaries**: NEVER declare private dictionaries or arrays for signs, planets, lords, elements, or glyphs inside individual widget files (e.g., `const signs = [...]`, `const signLords = {...}`, `const SIGN_SYMBOLS = {...}`).
- **Mandatory Use of `window.AstroCatalog`**:
  - Signs, modalities, elements, and lordships MUST be accessed via `window.AstroCatalog.getSign(nameOrNum)` or `window.AstroCatalog.getSignLord(signName)`.
  - Planet glyphs, abbreviations, and colors MUST be accessed via `window.AstroCatalog.getPlanet(planetName)`.
  - Rendering glyphs in DOM tables MUST go through `TableBuilder.renderZodiacGlyph(sign)` and `TableBuilder.renderPlanetGlyph(planet)`.
- **Modifying Metadata**: Any global changes to glyph formatting, transliteration, or Sanskrit terms MUST be executed solely in `static/js/core/astro_constants.js`.
