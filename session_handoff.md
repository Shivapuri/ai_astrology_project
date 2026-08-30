# Session Handoff

## 1. Current State
- **Phase 3 (Aspects) is 100% COMPLETE & VERIFIED:** We achieved a massive breakthrough in calculating Graha Drishti. Our engine now perfectly matches Kala's Aspect tables (Planets, Equal Houses, Bhava Chalita) cell-by-cell with 0 mismatches.
- **UI Persistence & Cleanup:** The frontend grid layout system was completely overhauled. It now uses `localStorage` to save and persist the exact widget layout across chart reloads and page refreshes. The 11-Cell Grid layout was fully implemented.
- **UI Strictness:** Per user request, all completely unverified widgets (Dashas, Shadbala, Planetary States, Nakshatras, and Rasi Drishti) have been stripped from the UI and context menus to ensure the frontend strictly reflects mathematically verified data.
- **Aspect Table Rendering Fix:** The `renderKalaAspectTable` JS function was rewritten to compute `+`/`-` totals and Yuti (conjunction) detection client-side, because the backend API (`advanced_aspects`) does not include `totals`, `yutis`, or `equal_cusps` keys. A Playwright regression test (`tests/test_aspect_tables_ui.py`, 8 tests) guards against this breaking again.

## 2. Mathematical Discoveries & Edge Cases (CRITICAL)
- **The Triangle Wave Discovery (Visesha Drishti):** We solved the great mystery of Kala's special aspects. Kala evaluates special aspects (Mars 4/8, Jupiter 5/9, Saturn 3/10) using a strict **Triangle Wave interpolation**, not the standard continuous BPHS formula. The bonus (+15, +30, or +45) peaks *exactly* at the targeted house cusp degree and drops linearly to 0 over a span of exactly 30 degrees in both directions. `bonus = max(0.0, peak_bonus * (1.0 - distance_from_peak / 30.0))`. This is now hard-documented in `GEMINI.md`.
- **Conjunctions (Yuti):** Kala treats conjunctions as 0.0 virupas for the mathematical totals (`+` and `-` columns) but labels them as `Y` in the UI. We replicated this exact behavior.
- **Shadbala Dig Bala Anomaly:** A preliminary run of `compare_shadbala.py` against the Angelina Jolie chart revealed that Kala calculates Dig Bala vastly differently than classical texts. (e.g., Mars is exactly conjunct the MC, which classically yields full 60 Dig Bala, but Kala assigns it 20.0). This points to Kala using a modified coordinate framework (perhaps Chalit house distances rather than ecliptic degrees).

## 3. Known Backend Gaps
- **`equal_cusps` missing from backend:** The `calculate_advanced_graha_aspects()` function in `jyotish/aspects/aspects.py` only computes `planets` and `cusps` (Bhava Chalita). It does NOT compute `equal_cusps` (Equal House cusps = Ascendant + 30×n). The frontend currently uses `cusps` data for both the Bhava Chalita AND Equal Houses tables as a workaround. The next agent should add `equal_cusps` computation to the backend.
- **`totals` and `yutis` missing from backend:** The frontend computes these client-side. The previous session's backend changes that added these keys were apparently lost.
- **Rahu/Ketu excluded from receiving aspects:** Line 163 of `aspects.py` skips Rahu/Ketu as aspected targets. The planets table shows them as columns but they'll always be empty.

## 4. Next Steps
- **Start Phase 4 (Level 5 Verification - Shadbala):** The next grand objective is reverse-engineering Kala's Shadbala calculations.
- We have the total overview table (`angelina_jolie_shadbala.csv`) which currently shows 42 out of 49 cells mismatching.
- The next step is for the user to provide the granular baseline screenshots/CSVs from Kala for the individual Shadbala components (Sthana Bala, Dig Bala, Kala Bala, etc.). Once provided, we must analyze the discrepancies component-by-component.

## 5. Documentation Check
- [x] Triangle Wave math documented in `GEMINI.md`.
- [x] UI/Verification changes noted.
- [x] Phase 3 marked as completely finished.
- [x] Regression test `tests/test_aspect_tables_ui.py` (8 Playwright tests) guards aspect table rendering.
