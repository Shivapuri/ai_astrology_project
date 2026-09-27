# ADR 006: Professional Editorial Astrological Design System & Typography Protocol

## Status
Accepted

## Context
Astra is a precision astrological computation and visualization platform adhering strictly to Ernst Wilhelm's "Kala" methodology:
- **Tropical Rasis (Signs)** for all basic placements and Vargas.
- **Campanus House System** for all Bhava calculations.
- **Sidereal Equatorial Nakshatras** anchored to the Dhruva Galactic Center (Middle of Mūla).

During rapid prototyping and iterative feature development, several visual design regressions accumulated that detracted from Astra's authoritative, publication-grade standard:
1. **OS-Rendered Emoji Boxes**: Planetary and zodiac symbols defaulted to operating-system emojis (such as Apple's purple emoji squares for zodiac signs or colorful cartoon planet icons), clashing with classical astronomical and astrological aesthetics.
2. **Sub-Pixel Micro-Typography (<12px)**: Multiple UI widgets and table cells used font sizes as small as `9.5px`, `10px`, `10.5px`, and `11px`, causing legibility degradation and eye strain.
3. **Over-Badging ("Badge Fatigue")**: Routine tabular data—such as degrees, house coordinates, dispositor names, and nakshatras—were wrapped in colorful rounded pill badges (`.pill`, `.badge-pill`), creating visual clutter and distracting from significant astrological dignities.
4. **Consumer Emoji Noise**: Status indicators, aspect arrows, and table headers made heavy use of consumer emojis (`🔴`, `🟢`, `🟠`, `🟡`, `👑`, `💣`, `✨`, `🔥`, `🛡`, `😴`, `💤`, `⚡`, `⚔`), giving the interface an informal, game-like appearance.
5. **Master Diagnostic Geometry**: Ensuring all 9 critical diagnostic columns (including the 9th column *Archetype & Vitality*) remain fully visible and properly labeled with authoritative Sanskrit and Western technical terminology.

## Decision
We establish a permanent, mandatory design system across all frontend templates, widgets, and stylesheets:

### 1. Strict 12px Font Floor (`static/GEMINI.md` Rule 1)
- **Hard Floor**: NEVER write or generate CSS font sizes below `12px` (equivalent to 9 pt).
- **Scale Hierarchy**:
  - Micro-tags, secondary captions, status readouts, tooltips: **`12px`** (strict floor).
  - Tabular data cells, body text, and mini-tables: **`13px` – `13.5px`** (~10 pt).
  - Table headers, card titles, section labels: **`14px` – `16px`** (10.5 pt – 12 pt).
- Sub-pixel text (`7px`, `8px`, `9px`, `9.5px`, `10px`, `10.5px`, `11px`) is strictly prohibited.

### 2. Monochrome Astrological Line Glyphs (STIX Two Math Standard)
- **Variation Selector 15 (`\uFE0E`)**: All astrological zodiac and planetary Unicode symbols must be suffixed with `\uFE0E` to instruct text rendering engines to present monochrome outlines rather than colored emoji boxes.
- **Font Stack**: All astrological glyphs use `var(--font-astro-glyphs)`:
  ```css
  --font-astro-glyphs: "STIX Two Math", "Cambria Math", "DejaVu Sans", "Noto Sans Symbols 2", "Apple Symbols", "Segoe UI Symbol", sans-serif;
  ```
- **Monochrome CSS Directive**: Use `font-variant-emoji: text;` on all `.zodiac-line-glyph`, `.graha-glyph`, and `.glyph-symbol` classes.

### 3. De-Badging & Anti-Pill Protocol
- **Tabular Data Cleanliness**: Degrees, coordinates, house numbers, dispositor names, and nakshatras must NOT be wrapped in rounded pill badges. They must render as clean tabular text (`font-variant-numeric: tabular-nums;`).
- **Semantic Micro-Tag Scope**: Badges are strictly reserved as `.micro-tag` components for high-salience status evaluations:
  - Functional dignity: `.micro-tag.tag-benefic`, `.micro-tag.tag-malefic`, `.micro-tag.tag-neutral`, `.micro-tag.tag-alert`.
  - Chara Karakas: `.micro-tag.tag-karaka`.
  - Master Lords: `.micro-tag.tag-neutral.badge` (for `LL`, `D9L`, `D3L`).
- All `.micro-tag` elements strictly adhere to the `12px` typography floor.

### 4. Emoji Purge & Semantic Micro-Indicators
- Consumer emojis (`🔴`, `🟢`, `🟠`, `🟡`, `👑`, `💣`, `✨`, `🔥`, `🛡`, `😴`, `💤`, `⚡`, `⚔`) are purged from all data tables, drawers, and diagnostic headers.
- **Semantic Micro-Dots**: Use `.status-indicator` with a 6px `.indicator-dot` (`.benefic`, `.malefic`, `.neutral`, `.alert`) for balance indicators, dignity shifts, and vitality scores.
- **Typographic Arrows**: Replace heavy or non-standard arrows (`➔`, `⬅`) with standard Unicode typographic arrows (`→`, `←`, `↔`).

### 5. Exact 9-Column Master Diagnostic Table Geometry
The Master Diagnostic table (`tmpl_master_diagnostic.html` and `master_diagnostic.js`) has exactly **9 columns**, labeled with authoritative Sanskrit and Western terminology:
1. `Graha (Planet)`
2. `Spatial Placement (Rāśi & Bhāva)`
3. `Essential Dignity & Lordship (Dignity)`
4. `Host Dispositor (Dispositor)`
5. `Aspect Vision (Graha Drishti)`
6. `Functional State & War (Avastha)`
7. `Equatorial Asterism (Nakshatra)`
8. `Shadbala Rank & Virūpas (Strength)`
9. `Archetype & Vitality (Archetype)`

The 9th column (*Archetype & Vitality*) must never be dropped or merged.

## Consequences & Benefits
- **Editorial Publication Quality**: The user interface matches the visual gravitas of classical astronomical ephemerides and Ernst Wilhelm's Kala desktop software.
- **Zero Cross-Platform Font Mismatch**: By enforcing `\uFE0E` and fallbacks to STIX Two Math, fonts render identically across macOS CoreText, Windows DirectWrite, and headless Linux CI.
- **Accessibility & Cognitive Ergonomics**: Eliminating tiny sub-pixel fonts and visual badge clutter ensures effortless data scanning for professional astrologers.
