# Session Handoff

## 1. Current State
- **Phase 3 (Aspects) is 100% COMPLETE & VERIFIED:** We achieved a massive breakthrough in calculating Graha Drishti. Our engine now perfectly matches Kala's Aspect tables (Planets, Equal Houses, Bhava Chalita) cell-by-cell with 0 mismatches.
- **UI Persistence & Cleanup:** The frontend grid layout system was completely overhauled. It now uses `localStorage` to save and persist the exact widget layout across chart reloads and page refreshes. The 11-Cell Grid layout was fully implemented.
- **UI Strictness & Python-Only Math:** All calculations have been strictly moved to the Python backend. The frontend JS is now 100% "dumb" display logic. For example, `Yuti` (conjunction) calculation was removed from JS and added to the backend API response. Unverified widgets (Dashas, Shadbala, etc.) were stripped from the UI.
- **Aspect Table Rendering Fix & Tests:** The `renderKalaAspectTable` JS function was rewritten to display the backend's `totals` and `yutis` directly. To prevent silent failures or regressions, 8 Playwright E2E tests (`tests/test_aspect_tables_ui.py`) and 3 Python unit tests (`tests/test_drishti.py`) have been added. The system will now sound an alarm and block development if any underlying math change breaks the display or shifts a decimal.

## 2. Mathematical Discoveries & Edge Cases (CRITICAL)
- **The Triangle Wave Discovery (Visesha Drishti):** We solved the great mystery of Kala's special aspects. Kala evaluates special aspects (Mars 4/8, Jupiter 5/9, Saturn 3/10) using a strict **Triangle Wave interpolation**, not the standard continuous BPHS formula. The bonus (+15, +30, or +45) peaks *exactly* at the targeted house cusp degree and drops linearly to 0 over a span of exactly 30 degrees in both directions. `bonus = max(0.0, peak_bonus * (1.0 - distance_from_peak / 30.0))`. This is now hard-documented in `GEMINI.md`.
- **Conjunctions (Yuti):** Kala treats conjunctions as 0.0 virupas for the mathematical totals (`+` and `-` columns) but labels them as `Y` in the UI. We replicated this exact behavior.
- **Shadbala Dig Bala Anomaly:** A preliminary run of `compare_shadbala.py` against the Angelina Jolie chart revealed that Kala calculates Dig Bala vastly differently than classical texts. (e.g., Mars is exactly conjunct the MC, which classically yields full 60 Dig Bala, but Kala assigns it 20.0). This points to Kala using a modified coordinate framework (perhaps Chalit house distances rather than ecliptic degrees).

## 3. Known Backend Gaps
- None for Phase 3. The backend perfectly outputs raw values, `equal_cusps`, binary Paksha totals, and Yutis directly.

## 4. Next Steps
- **Start Phase 4 (Level 5 Verification - Shadbala):** The next grand objective is reverse-engineering Kala's Shadbala calculations.
- We have the total overview table (`angelina_jolie_shadbala.csv`) which currently shows 42 out of 49 cells mismatching.
- The next step is for the user to provide the granular baseline screenshots/CSVs from Kala for the individual Shadbala components (Sthana Bala, Dig Bala, Kala Bala, etc.). Once provided, we must analyze the discrepancies component-by-component.

## 5. Documentation Check
- [x] Triangle Wave math documented in `GEMINI.md`.
- [x] UI/Verification changes noted.
- [x] Phase 3 marked as completely finished.
- [x] Regression test `tests/test_aspect_tables_ui.py` (8 Playwright tests) guards aspect table rendering.
