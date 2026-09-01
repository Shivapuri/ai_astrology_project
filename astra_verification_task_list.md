# Astra Verification & Refactoring Task List

This tracker outlines the strict hierarchical approach we are taking to verify the engine, ensuring no higher-level calculation is debugged before its underlying foundation is rock-solid.

## Phase 1: Architecture & Baseline Organization
- [x] **Establish Hierarchy:** Create `calculation_hierarchy.md` to define the DAG (Ephemeris -> Vargas -> Aspects -> Balas -> Avasthas).
- [x] **Consolidate Baseline Data:** Extract all image targets and compile them into `angelina_jolie_baselines.json`.
- [x] **Directory Refactoring:** Moved flat scripts in `/jyotish/` into dedicated directories (`/jyotish/relationships/`, `/jyotish/aspects/`).
- [x] **Dual-Level Documentation:** Ensured `relationships.md` contains plain-English explanations for users and strict mathematical constraints (like the degree limits and even varga reversals) for AI.

## Phase 2: Level 3 Verification (Dignities & Relationships)
- [x] **Write Dignities Test:** Create `test_dignities.py` checking all 16 Vargas against the baseline CSV.
- [x] **Fix Compound Friendship Logic:** Debug `relationships.py` (specifically `get_compound_relationship`) to fix the failing test.
- [x] **Fix D1 vs Varga Distances:** Ensure Tatkalika (Temporary Friendship) is being calculated correctly for Vargas.
- [x] **Fix Degree Limits:** Added 0-3° limit for Moon Debilitation and 0-15° limit for Mercury Debilitation.
- [x] **Fix Varga Reversals:** Implemented Parashara "Reverse for Even Rasis" logic for D10 and D24 calculations.

## Phase 3: Level 4 Verification (Aspects/Drishti)
- [x] **Write Drishti Test:** Build tests against `angelina_jolie_drishti_yuti.csv`.
- [x] **Verify Rasi Drishti:** Ensure whole-sign aspects are firing correctly.
- [x] **Verify Graha Drishti:** Fix the 0-60 Virupa calculations in `aspects.py`.

## Phase 4: Level 5 Verification (Strengths/Shadbala)
- [x] **Audit Shadbala Core:** Created `audit_shadbala.py` and implemented Ahargana Time Lords.
- [x] **Verify Uccha Bala:** Test against `angelina_jolie_uccha.csv`.
- [x] **Verify Dig Bala:** Test against `angelina_jolie_dig.csv`.
- [x] **Verify Cheshta Bala:** Test against `angelina_jolie_cheshta.csv`.

## Phase 5: Level 6 Verification (Avasthas)
- [x] **Verify Ishta Phala:** Test against `angelina_jolie_ishta.csv`.
- [x] **Verify Subha Phala:** Test against `angelina_jolie_subha.csv`.
- [x] **Verify Lajjitadi Avasthas:** Use the fully nested JSON matrix to test the final addition/subtraction modifiers.
- [x] **Verify Shayanadi Avasthas:** Ensure Nakshatra/Navamsa calculations yield correct Shayanadi states.
