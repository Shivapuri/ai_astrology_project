# Astra Precision Verification & Development Roadmap

This master roadmap outlines our step-by-step plan to verify and expand Astra's calculations against Ernst Wilhelm's Kala software ground-truth datasets. Every phase follows a strict Directed Acyclic Graph (DAG): lower astronomical foundations must be green before higher-level scoring systems are refined.

---

## 🏛️ Completed Foundation Phases

### Phase 1: Architecture & Directory Refactoring
- [x] **Calculation Hierarchy:** Created `calculation_hierarchy.md` defining the calculation order (Ephemeris -> Vargas -> Aspects -> Balas -> Avasthas -> Dashas).
- [x] **Module Reorganization:** Moved core engines into modular directories (`/jyotish/relationships/`, `/jyotish/aspects/`, `/jyotish/shadbala/`, `/jyotish/avasthas/`).
- [x] **Documentation Alignment:** Added plain-English definitions and mathematical specifications to companion `.md` files.

### Phase 2: Levels 3 & 4 (Dignities, Relationships & Aspects)
- [x] **Dignities Test Suite:** Built `test_dignities.py` checking planetary dignities across all 16 Vargas.
- [x] **Compound Friendship:** Calibrated Natural (*Naisargika*) and Temporary (*Tatkalika*) friendship logic in `relationships.py`.
- [x] **Degree-Specific Debilitations:** Enforced 0-3° boundary for Moon and 0-15° boundary for Mercury debilitation.
- [x] **Even Varga Reversals:** Implemented Parashari reverse counting for even signs in D10 and D24.
- [x] **Drishti Verification:** Built `test_drishti.py` verifying Rasi Drishti and 0-60 Virupa Graha Drishti against Kala baselines.

---

## 🚀 Active Roadmap: Precision Calibration & New Engines

### Phase 3: Astronomical & Basic Placements Baseline (Level 1 & 2)
*Dataset: `angelina_jolie_basic_placements.csv` (Extracted from `angelina_jolie_basic_printout.pdf`)*
- [x] **Test Core Coordinates:** Verified D1 longitudes, signs, arcminutes, and retrogrades in `tests/test_basic_placements.py`.
- [x] **Test Nakshatras & Padas:** Calibrated Ecliptic Lagna Nakshatra (Pushya Pada 2) and Equatorial Graha Nakshatras.
- [x] **Verify Campanus House Cusps:** Verified all 12 cusps against Kala within arcsecond tolerance.
- [x] **Calibrate Node Aspect Reception:** Fixed `aspects.py` line 209 to calculate Rahu (+96 / -127) and Ketu (+7 / -19).

### Phase 4: Shadbala Sub-Pillars Precision Calibration (Level 5)
*Dataset: `angelina_jolie_shadbala_breakdown.csv` (Extracted from `angelina_jolie_shadbala.pdf`)*
- [ ] **Comprehensive Sub-Pillar Tests:** Update `tests/test_shadbala.py` to assert all 35 sub-metrics (Sthana, Dig, Kaala, Ayana, Cheshta, Drik, Naisargika, Total Virupas, Rupas, and Relative Ranks).
- [ ] **Calibrate Mercury Cheshta Bala:** Refine Mercury motional strength calculation in `jyotish/shadbala/shadbala.py` to eliminate the remaining 1.19 Virupa difference.
- [ ] **Audit Saptavargaja Bala:** Ensure planetary strength contributions across the 7 primary Vargas match Kala exactly.

### Phase 5: Vimshottari Dasa Full Cycle Timeline (Level 7)
*Dataset: `angelina_jolie_vimshottari_antardasas.csv` (Extracted from `angelina_jolie_vimshottari_dasa_full.pdf`)*
- [ ] **Timeline Test Suite:** Create `tests/test_vimshottari_timeline.py` testing all 9 Mahadashas and all 81 Antardashas over the 120-year cycle.
- [ ] **Year-Length Precision:** Fine-tune the Dasha year constant (Saura 360-day vs. 365.2422 tropical year) so start dates match Kala down to the day.

### Phase 6: Multi-Varga Avasthas Calibration (Level 6)
*Datasets: `angelina_jolie_lajjitadi_varga_net_modifiers.csv` & `angelina_jolie_shayanadi_vargas.csv`*
- [ ] **Quantitative Lajjitadi Matrix Refactor:** Update `jyotish/avasthas/quantitative.py` to consume the new `lajjita.py` qualitative rules and verify net modifier outputs across all 16 Vargas.
- [ ] **Shayanadi Multi-Varga Engine:** Update `jyotish/avasthas/shayana.py` to dynamically support divisional chart inputs and test against all 1,296 state combinations across all 16 Vargas and 9 Mahadashas.

### Phase 7: New Classical Engines Implementation
*Datasets: `angelina_jolie_ashtakavarga_sarva.csv` & `angelina_jolie_varga_vimshopaka.csv`*
- [ ] **Ashtakavarga Engine (`jyotish/ashtakavarga/`):**
  - Implement 8-fold benefic point (*Bindu*) grid for all 7 planets + Lagna across all 12 signs.
  - Implement *Trikona Shodhana* (reduction across trines).
  - Implement *Ekadhipatya Shodhana* (reduction for signs with the same planetary lord).
  - Test against `angelina_jolie_ashtakavarga_sarva.csv` (337 total points).
- [ ] **Varga Vimshopaka Engine (`jyotish/vimshopaka/`):**
  - Implement 20-point dignity scoring across Shadvarga, Saptavarga, Dasavarga, and Shodasavarga.
  - Implement Vaisheshikamsa honorific classifications (*Kimsuka, Vyanjana, Uttama, Gopura, Nagapushpa, Kanduka*).
  - Test against `angelina_jolie_varga_vimshopaka.csv`.
