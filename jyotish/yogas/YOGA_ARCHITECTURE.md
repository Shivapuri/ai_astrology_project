# ASTRA YOGA ENGINE: ARCHITECTURAL RULEBOOK & BREAKER SENSITIVITY MATRIX

This document governs `jyotish/yogas/models.py`, `jyotish/yogas/breakers.py`, and all downstream yoga detection modules. Every engineer and AI auditor must enforce these boundaries to prevent cross-yoga interference.

---

## 1. HEMISPHERE A PURITY LAW
`jyotish/yogas/` resides strictly in **Hemisphere A (Foundational Calculus)**:
1. **Pure Data Only:** Modules must return `YogaInstance` and `YogaBreakerDetail` objects containing floats, ints, lists, and classical Sanskrit terms (*Uccha*, *Nīca*, *Svakṣetra*, *Virūpas*, *Rūpas*, *Kendra*, *Trikoṇa*, *Duṣṭhāna*, *Triṣaḍāya*).
2. **Zero UI Formatting:** Never embed HTML tags, CSS classes, hex color codes, or UI table definitions inside `models.py`, `breakers.py`, or any yoga module.
3. **Dependency Direction:** `jyotish/yogas/` must NEVER import from Hemisphere B (`planetary_evaluation/` or `report/`).

---

## 2. STRICT BOUNDARIES OF `models.py`
`models.py` is a **pure schema and serialization module**:
- **Allowed:**
  - `YogaCategory(str, Enum)` and `YogaStatus(str, Enum)` definitions.
  - `@dataclass` definitions (`YogaBreakerDetail`, `YogaInstance`).
  - Null-safe, clamped `[0.0, 100.0]` `.to_dict()` serialization methods.
- **Forbidden:**
  - Astronomical math, chart dictionary traversal, or house/sign lookups.
  - Yoga detection rules or penalty calculations.

---

## 3. TWO-LAYER ARCHITECTURE OF `breakers.py`

Classical Jyotish is not a uniform checklist where every yoga reacts to the same friction in the same way. Therefore, `breakers.py` is partitioned into **Layer 1 (Universal Calculators)** and **Layer 2 (Opt-In Breaker Auditors)**.

### Layer 1: Universal Calculators (Used by ALL Yogas)
These pure functions extract chart state and perform geometric math without judging whether a placement is "good" or "bad":
- `get_lagna_sign(chart) -> str` (returns `""` if missing; never fabricates `"Aries"`).
- `get_planets_data(chart) -> Dict[str, Any]`
- `get_sign_of_planet(chart, planet) -> str`
- `get_house_of_planet(chart, planet) -> int` (`1..12` whole-sign house, or `0` if unresolved).
- `get_aspect_score(chart, giver, receiver) -> float` (Sphuṭa Dṛṣṭi clamped to `[0.0, 60.0]` Virūpas; `>= 45.0` is Palpable, `30.0–44.9` is Marginal).
- `get_house_rulers(chart) -> Dict[int, List[str]]` and `_first_ruler(house_rulers, house) -> Optional[str]`.
- `audit_neecha_bhanga_condition_3(...)` and `audit_neecha_bhanga(...)` (with `!= "Moon"` tautology guards and Mercury self-lordship deduplication).
- `resolve_yoga_score_and_status(pre_breaker_score, breakers, score_cap=100.0) -> Tuple[float, YogaStatus]`.

### Layer 2: Opt-In Breaker Auditors (Subscribed per Yoga Sensitivity Profile)
These functions calculate penalties for specific structural flaws. **Downstream yoga modules must ONLY call the auditors that match their category's sensitivity profile below:**
1. `audit_trishadaya_interference(yoga_planets, chart, is_supreme_pairing=False, exclude_houses=())`
2. `audit_combustion(yoga_planets, chart, deep_only=False)`
3. `audit_dispositor_vitality(yoga_planets, chart)`
4. `audit_dusthana_placement(yoga_houses, category_name)`
5. `audit_shadbala_muscle(yoga_planets, chart)`

---

## 4. MASTER BREAKER SENSITIVITY MATRIX (ANTI-INTERFERENCE RULES)

Never apply Layer 2 breakers blindly across all yogas. Follow this exact matrix for each module:

| Yoga Category / Module | `audit_trishadaya` (3, 6, 11) | `audit_dusthana` (6, 8, 12) | `audit_combustion` | `audit_dispositor` | `audit_shadbala` | Special / Inverse Breaker Rules |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **1. `MAHAPURUSHA`** (`pancha_mahapurusha.py`) | YES | YES *(Chandra-only in 6/8/12)* | YES | YES *(if exalted)* | YES | Cap pre-breaker score at `100.0`; gate `PURE` on no breaker `>= 20.0`. |
| **2. `NEECHABHANGA`** (`neechabhanga.py`) | NO | Cap score `<= 65.0` in 6/8/12 | YES | NO *(dispositor is rescuer)* | YES | Kendra/Koṇa (`1,4,5,7,9,10`) upgrades to *Nīcabhaṅga Rāja Yoga*; `6,8,12` is Simple Cancellation. |
| **3. `RAJA`** (`raja_yogas.py`) | YES (`is_supreme_pairing=True` for 9+10) | YES | YES | YES | YES | Distinguish True *Rāja Yoga* (9L+10L) from *Śaṅkha Yoga* (other Kendra+Koṇa pairs). |
| **4. `PARIVARTANA`** (`parivartana.py`) | YES *(Mahā only)* | NO *(classified by pair type)* | YES | NO *(mutual hosts)* | YES | 28 *Mahā* (auspicious), 8 *Khala* (3rd house), 30 *Dainya* (6, 8, 12). Resolve dual-lordship via actual occupied houses (`anyonyam`). |
| **5. `VIPARITA`** (`viparita.py`) | NO | **FORBIDDEN** *(requires 6, 8, 12!)* | YES | YES | YES | **Inverse Breaker:** Penalize if a Kendra/Trikoṇa lord conjoins or palpably aspects the Duṣṭhāna lord. |
| **6. `DHANA`** (`dhana_daridrya.py`) | `exclude_houses=(11,)` *(11L is wealth giver!)* | YES | YES | YES | YES | **NEVER penalize the 11th lord** in Dhana yogas; penalize 6/8/12 financial leakage. |
| **7. `DARIDRYA` & `CHANDAL`** (`dhana_daridrya.py`, `chandal_yogas.py`) | NO | **FORBIDDEN** *(affliction yoga)* | NO | NO | NO | Affliction yogas: Benefic aspect/Neecha Bhanga acts as a **mitigation** (moving status to `RESCUED`), never `"Pure & Eminent"`. |
| **8. `LUNAR`** (`lunar_solar_yogas.py`: *Sunaphā, Anaphā, Durudharā, Kemadruma*) | NO | NO | YES *(on 2nd/12th planets)* | YES *(on 2nd/12th planets)* | YES | *Kemadruma* uses its dedicated **4-Tier Bhaṅga Hierarchy** (Lagna Kendra, Moon Kendra, Modality, D9). |
| **9. `SOLAR`** (`lunar_solar_yogas.py`: *Veśi, Vāsi, Ubhayacarī, Budhāditya*) | NO | YES *(for Budhāditya)* | `deep_only=True` (`< 3.0°` only) | YES | YES | Moderate proximity (`3.0°–8.0°`) is astronomically normal for Solar yogas; only deep combustion (`< 3.0°`) penalizes. |
| **10. `KARTARI`** (`kartari.py`) | NO | NO | NO | NO | NO | Check benefic/malefic purity of 2nd and 12th houses from Lagna/Moon/Sun and opposing aspects (`Suśubha`). |
| **11. `CONTEXTUAL`** (`contextual_yogas.py`: *Sāṅkhya, Ādhi, Mahābhāgya*) | NO | **FORBIDDEN** *(Ādhi requires 6, 7, 8!)* | YES *(Ādhi only)* | NO | YES *(Ādhi only)* | **Sāṅkhya Yogas** (*Phaladīpikā* 6.39) stand completely alone—apply **ZERO** breakers to Sāṅkhya. |
| **12. `DISPOSITOR_ROOT`** (`dispositor_root_yogas.py`: *Kāhala, Parvata, Puṣkala*) | YES | YES | YES | YES | YES | Prevent "1st Lord in 1st House" trivial self-dispositor loophole from scoring equal to multi-planet *Parvata*. |
| **13. `CHARACTER`** (`character_growth_yogas.py`: *Kesari, Śakaṭa, Vasumatī, Amala*) | `exclude_houses=(3,6,11)` for *Vasumatī* | YES *(Kesari)* | YES | YES | YES | *Vasumatī* requires Upacayas (`3,6,10,11`); *Śakaṭa* is cancelled when Moon is in Lagna Kendra (`1,4,7,10`). |
| **14. `DEITY`** (`deity_yogas.py`: *Trimūrti, Tridevī, Mālā*) | NO | **FORBIDDEN** on *Aśubha Mālā* (`6,8,12`) & *Śubha Mālā* (`5,6,7`) | YES *(Trimūrti / Tridevī)* | NO | YES *(Trimūrti / Tridevī)* | *Trimūrti* & *Tridevī* already mandate own/exalted/friendly dignity + Kendra/Koṇa placement. |
| **15. `POWER` & `BHAVA`** (`power_yogas.py`, `bhava_yogas.py`) | NO | Built into formation rules | YES *(on positive Bhava lords)* | NO | YES | For the 24 Bhava Yogas, Houses `6, 8, 12` invert positive/negative conditions (*Harṣa, Sarala, Vimala* vs *Asura, Musala*). |

---

## 5. SCORING & STATUS INVARIANTS
1. **Pre-Breaker Score Cap:** Always cap positive confluence scores at `100.0` *before* subtracting breaker penalties (`resolve_yoga_score_and_status`).
2. **Major Breaker Gate:** Any yoga with an active breaker of `penalty >= 20.0` can NEVER receive `YogaStatus.PURE` ("Pure & Eminent"), even if its net score is `>= 75.0`.
3. **Affliction Yoga Semantics:** Negative/affliction combinations (*Kemadruma*, *Śakaṭa*, *Daridrya*, *Chāṇḍāla*, *Pāpa Kartarī*, *Dainya Parivartana*, Converse Bhava Yogas) must use `YogaStatus.STAINED` when active/unmitigated and `YogaStatus.RESCUED` or `YogaStatus.BROKEN` when cancelled—never `YogaStatus.PURE` ("Pure & Eminent").
