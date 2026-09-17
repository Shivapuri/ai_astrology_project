# ADR-009: Decoupling Overlapping Additive Modifiers & Audit Harmonization

## Context & The Shortcoming Identified in Audit
An independent mathematical audit of Astra's Master Graha Diagnostics identified three critical issues of "double and triple metering":
1. **Retrograde Motion Double-Counting:** `mot_mod` was adding `+0.3` to vitality for retrograde planets, even though retrograde planets already receive near-maximum *Cheṣṭa Bala* (motional strength) inside their core Shadbala virūpas.
2. **Aspect/Conjunction Stacking with Lajjitādi:** A single malefic conjunction was being penalized in `conj_mod`, in `drishti_mod`, in `psy_mod` (as *Kshudhita* or *Kshobhita*), and in `vikala_mod`, causing an artificial triple/quadruple mathematical penalty.
3. **Black-Box Vitality Score:** The 1.0 to 10.0 score lacked an exposed mathematical receipt, leaving users unsure how the score was assembled.

## Decision
1. **Remove Retrograde Bonus from `mot_mod`:**
   - Cease adding `+0.3` for retrograde motion in `calculate_graha_vitality`. Let *Cheṣṭa Bala* inside Shadbala naturally express the motional horsepower.
   - Retain the combustion (*Astangata*) penalty, as combustion physically strips a planet's rays and is not subtracted from classical Shadbala virūpas.
2. **Shift Lajjitādi Avasthās to Qualitative Badges:**
   - Stop applying additive numeric modifiers (`psy_mod`) for feeling states that are already physical derivations of conjunctions and aspects.
   - Treat *Lajjitādi Avasthās* as psychological and behavioral diagnoses (displayed via color-coded badges and narrative tooltips).
3. **Expose Mathematical Calculation Receipt:**
   - Return structured equation parts from Python backend so the frontend hover tooltip provides a step-by-step receipt (Base Engine 5.0, Quality/Dignity contribution, Muscle/Shadbala contribution, Host rescue, and Environmental weather).
4. **Single Source of Truth for D1 Diagnostics:**
   - Streamline frontend JavaScript to directly consume the authoritative Python JSON (`peData.planets[graha]`), while preserving lightweight fallback bridges for multi-Varga dropdown exploration.

## Proof & Validation
This eliminates all redundant additive stacking while maintaining 100% mathematical transparency and scriptural integrity across both backend API and frontend UI.
