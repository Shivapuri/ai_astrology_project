# Astra Project Handoff: Shadbala & Quantitative Avasthas

## 📍 Where We Are Currently
We successfully diagnosed and largely resolved the massive discrepancies in the engine's Shadbala calculations.

**What we accomplished today:**
1. **Identified the Root Cause:** The `angelina_jolie_*.csv` matrices use raw, unmultiplied Shadbala values for their diagonals. Our engine was missing critical Time Lords (Abda, Masa, Vara, Hora) and incorrectly multiplying the base by `Jagrat` and `Bala`.
2. **Fixed the Time Lords:** We implemented the Srishti Ahargana math inside `jyotish/shadbala/shadbala.py` to calculate the exact Lord of the Year, Month, Day, and Hour based on B.V. Raman's epoch (May 2, 1827).
3. **Fixed the Multiplier Bug:** We removed the incorrect Jagrat/Bala multipliers from the raw baseline matrix initialization in `jyotish/avasthas/quantitative.py`.
4. **Current Accuracy:** We brought the core Shadbala `Total_Virupas` calculation from being ~200+ points off, to being within a microscopic **~5 to 40 points** of the exact Kala software output for almost every planet.

## 🔍 The Remaining Minor Discrepancies
Our `audit_shadbala.py` script now reports the following differences for the Shadbala base (Diagonal):
*   **Sun**: +6.2
*   **Moon**: +39.9
*   **Mars**: +6.6
*   **Mercury**: -9.0
*   **Jupiter**: +38.4
*   **Venus**: -2.5
*   **Saturn**: +5.9

## 🚀 How to Continue Tomorrow (Next Steps)

### Step 1: Sub-Component Isolation (Phase 4)
Right now, we know the *Total* Shadbala is off by a few points, but Shadbala is made of 6 pillars (Sthana, Dig, Kala, Cheshta, Naisargika, Drik). 
*   **Task:** To fix the remaining 5-39 points, you will need to compare the breakdown of these 6 pillars. You can do this by modifying `scripts/audit_shadbala.py` to print out `chart["shadbala"]["Planet"]["Sthana_Bala"]`, etc., and manually comparing them against Kala Software's Shadbala breakdown screen to see exactly which pillar is carrying the offset.
*   **Likely Culprit:** The `+39.9` on Moon and `+38.4` on Jupiter heavily implies the **Hora Lord** (worth 60 points) or **Paksha Bala** is calculated slightly differently in Kala due to Sunrise calculation boundaries.

### Step 2: Update Pytest Suite (Phase 4)
*   **Task:** Once the sub-components perfectly match Kala, un-skip the test in `tests/test_quantitative_avasthas.py` and write formal assertions for Phase 4 in the test suite so the pre-commit hook protects it.

### Step 3: Avastha Matrix Logic (Phase 5)
*   **Task:** Currently, `audit_shadbala.py` reports failures for the *off-diagonal* cells in the matrices (the "Pulls" and "Modifiers"). Now that the raw Shadbala base is mostly correct, the next step is debugging `calc_pull()` and the `sign_mult` logic inside `jyotish/avasthas/quantitative.py` (Lajjitadi Delighted/Starved boolean logic) to ensure the modifier matrices perfectly align with the CSVs.
