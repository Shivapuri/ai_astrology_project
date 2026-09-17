# ADR-005: Option A Recursive Drishti (Distorted Guidance from Debilitated Benefics)

## Context & The Shortcoming in the Naive Model
In standard aspect calculation (*Graha Drishti*), natural benefics (Jupiter and Venus) always cast positive Virūpas of aspectual sky-light (+15 to +60 Virūpas) onto whatever planet they aspect.

### The Real-Life Astrological Failure
* **The Scenario:** Suppose Jupiter is debilitated in Capricorn (*Neecha*, 12.5% dignity), or Venus is debilitated in Virgo.
* **The Failure:** In naive software, a debilitated Jupiter still casts a 100% pure, flaw-dissolving ray of divine wisdom (+30 Virūpas). In real human life, an advisor whose own moral judgment is compromised or corrupt cannot provide pure, objective guidance. Their counsel will be dogmatic, hypocritical, or short-sighted. Treating their ray as identical to an exalted Guru's blessing creates major interpretive errors.

## Decision
1. **Adopt Option A (Recursive Drishti Dampening):**
   When a natural benefic (Jupiter or Venus) is debilitated ($\le 25\%$ dignity, or in true signs of fall Capricorn/Virgo):
   - Its positive aspect Virūpas are **dampened by 50%** (e.g. +30 Virūpas is reduced to +15 Virūpas effective light).
2. **Attach Transparent Warning Badges:**
   - **For Debilitated Jupiter:** Attach badge **`⚠️ Compromised Guidance / Dogmatic Light`**.
   - **For Debilitated Venus:** Attach badge **`⚠️ Corrupted Indulgence / Compromised Harmony`**.
3. **Preserve Neutral Ray Structure:**
   This dampening strictly affects positive benefic rays. Negative malefic pressure from Mars or Saturn is not dampened, as cruelty remains sharp regardless of dignity.

## Proof & Validation
Automated unit tests in `tests/test_planetary_evaluation.py` (`test_option_a_recursive_drishti_dampening`) verify that an aspect from exalted Jupiter delivers 30.0 adjusted Virūpas, whereas an aspect from debilitated Jupiter is dampened to 15.0 Virūpas and flagged with the distorted ray badge. This guarantees that planetary guidance reflects the true ethical standing of the casting planet.
