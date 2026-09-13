# 🏛️ Angelina Jolie Benchmark & Proof Catalog

This document provides the definitive verification inventory, cryptographic manifest (MD5 checksums), and testing architecture for the **Angelina Jolie ground-truth benchmarks** in the Astra engine.

---

## 1. Multi-Layer Verification Pyramid

Astra validates astrological calculations across five independent layers of verification:

| Layer | Verification Mechanism | Artifacts / Evidence | Tolerance |
| :--- | :--- | :--- | :--- |
| **Layer 1: Ground Truth** | Direct Kala software exports & high-res screenshots | PDF reports & raw Kala PNGs | Ground Truth |
| **Layer 2: Transcribed CSVs** | Machine-readable tabular datasets | 36 normalized CSV benchmark files | 0 discrepancies |
| **Layer 3: Automated Pytest** | Continuous test suite execution | 157 automated unit & regression tests | $\le 0.15$ virūpas |
| **Layer 4: Visual Side-by-Side** | Headless Playwright UI screenshot capture | 32 composite side-by-side comparison images | Visual parity |
| **Layer 5: Interactive Viewer** | Standalone multi-mode proof browser | `astra_vargas_side_by_side_proof.html` | Interactive review |

---

## 2. Core Benchmark Datasets (Primary Files)

| Category | File Name | Size (Bytes) | Lines | MD5 Checksum | Astrological Scope |
| :--- | :--- | :---: | :---: | :--- | :--- |
| **Ashtakavarga** | `angelina_jolie_ashtakavarga_sarva.csv` | 474 | 12 | `10809b0cc5b73f357a07e49f15f1a802` | Sarvashtakavarga bindus across all 12 signs |
| **Aspects** | `angelina_jolie_aspects_bhava_chalita.csv` | 352 | 10 | `6a49fb6e92e6a72a3e56447c5b706bfc` | Planetary aspects onto Campanus house cusps |
| **Aspects** | `angelina_jolie_aspects_equal_houses.csv` | 352 | 10 | `ad1543427bab0dc3f3b5f4bfc303f891` | Planetary aspects onto Equal House cusps |
| **Aspects** | `angelina_jolie_aspects_planets.csv` | 305 | 10 | `837b5d7104b495a16b6e9fc118a6fd0b` | Planetary aspect matrix (Graha Drishti in Virūpas) |
| **Consolidated** | `angelina_jolie_baselines.json` | 75,056 | 4,871 | `e3b0b9124506bffe4b37cb8ca48b84f1` | Full consolidated JSON export of all Kala baselines |
| **Placements** | `angelina_jolie_basic_placements.csv` | 691 | 11 | `cde86e623869c47cf8f245c786dc8002` | D1 longitudes, signs, houses, nakshatras, and speed |
| **Avasthas** | `angelina_jolie_cheshta.csv` | 1,013 | 61 | `708d9b3dcd3b690b08216b6dbe833aa9` | Cheshta Bala quantitative avastha table |
| **Avasthas** | `angelina_jolie_dig.csv` | 1,010 | 61 | `b3d916127d183a11f49f7b4abad95663` | Dig Bala quantitative avastha table |
| **Dignities** | `angelina_jolie_dignities.csv` | 373 | 17 | `5826cba0ebf1e5c8f0860c1737f4131b` | Planetary dignities (Exaltation, Moolatrikona, Own, Friends, Enemies) |
| **Avasthas** | `angelina_jolie_drishti_yuti.csv` | 459 | 10 | `83704b5ba3dc57a99062eac49c74bbbc` | D1 Drishti Yuti mood table |
| **Avasthas** | `angelina_jolie_ishta.csv` | 1,010 | 61 | `8b07d596c97e8e9bcd5bd6a572329b63` | Ishta/Kashta Phala quantitative avastha table |
| **Avasthas** | `angelina_jolie_lajjitadi_matrix.csv` | 405 | 9 | `03315d11553027cad6f6f43a63151231` | Qualitative Lajjitadi Avasthas states (Proud, Delighted, Starved, Agitated, etc.) |
| **Avasthas** | `angelina_jolie_lajjitadi_varga_net_modifiers.csv` | 678 | 17 | `b5c74c27ee4d6ad6eb6842739a6f42d4` | Net modifiers summary across all 16 divisional charts |
| **ShadBala** | `angelina_jolie_shadbala.csv` | 956 | 47 | `d88b685738b33983ea8578560c365442` | D1 baseline ShadBala matrix with positive/negative pulls |
| **ShadBala** | `angelina_jolie_shadbala_breakdown.csv` | 1,561 | 36 | `db569601b9334dab4d0ee32838f6571b` | Detailed 6-fold breakdown (Sthana, Dig, Kaala, Cheshta, Drig, Naisargika) |
| **Avasthas** | `angelina_jolie_shayanadi_vargas.csv` | 47,664 | 1,297 | `a7e07fa46d45b5b6e9673284e91756ce` | Shayanadi avasthas across all 16 vargas |
| **Avasthas** | `angelina_jolie_subha.csv` | 1,024 | 61 | `3bbc3164b0f548292e1cb566995e18de` | Subha/Asubha Phala quantitative avastha table |
| **Avasthas** | `angelina_jolie_uccha.csv` | 1,020 | 61 | `aa1d5af5d48e59eb7e71304da6da9c25` | Uccha Bala quantitative avastha table |
| **Vimshopaka** | `angelina_jolie_varga_vimshopaka.csv` | 619 | 9 | `e3040751b819758ee07a219d8c8af621` | Dignity scores on 20-point scale across Shadvarga, Saptavarga, Dasavarga, Shodashavarga |
| **Avasthas** | `angelina_jolie_veda.csv` | 1,013 | 61 | `93fabb326cd046aa1344079682d38a58` | Veda Bala quantitative avastha table |
| **Dashas** | `angelina_jolie_vimshottari_antardasas.csv` | 2,407 | 82 | `8feb507c7f2be621c14488f46bdf2c56` | Complete breakdown of all Antardashas |
| **Dashas** | `angelina_jolie_vimshottari_dasa.csv` | 678 | 22 | `e7b2c5ad53215d29329257bf68676ee0` | Vimshottari Mahadasha start and end dates (120-year cycle) |

---

## 3. Divisional Chart (*Varga*) Transcribed Benchmarks

### A. Master Multi-Varga Datasets
| Master File | Size (Bytes) | Records / Lines | MD5 Checksum | Purpose |
| :--- | :---: | :---: | :--- | :--- |
| `angelina_jolie_lajjitadi_all_vargas_matrices.csv` | 38,882 | 784 cells (16 vargas × 49 cells) | `503ea6abfeca2ca497e31f842091ad59` | Drishti Yuti mode ground-truth matrices across D1–D60 |
| `angelina_jolie_lajjitadi_bhava_cusp_influences.csv` | 46,532 | House Cusp Influences | `ad3416bb9b5b9414846278f530b845a4` | Aspect and conjunction pulls on all 12 Campanus house cusps across vargas |
| `angelina_jolie_lajjitadi_node_influences.csv` | 12,612 | Nodal Influences | `f4a420c7450d8cd0002264303db33207` | Aspect and conjunction pulls on Rahu and Ketu across vargas |
| `angelina_jolie_shadbala_all_vargas_matrices.csv` | 49,870 | 784 cells (16 vargas × 49 cells) | `5f17ae311e77163a8e80e29a0155530b` | ShadBala mode ground-truth matrices across D1–D60 |
| `angelina_jolie_varga_planetary_positions.csv` | 2,579 | 17 lines (16 vargas + header) | `a36c16cf41f38f875397e4bc47294894` | Planetary signs and degrees across all 16 divisional charts |

### B. Individual Varga CSV Matrices (All 16 Divisional Charts)

All individual divisional chart CSVs are located in two synchronized directories:
* **Drishti Yuti Mode (16 CSVs)**: `source-material/software-setup/sample-case/lajjitadi_transcription/varga_matrices/`
* **ShadBala Mode (15 CSVs)**: `source-material/software-setup/sample-case/lajjitadi_transcription/varga_shadbala_matrices/`

| Varga | Harmonic Chart Name | Drishti Yuti CSV MD5 | ShadBala CSV MD5 |
| :--- | :--- | :--- | :--- |
| **D1** | Rasi | `55417e6b21d85c3ec7d1b3ffdd78d677` | `d88b685738b33983ea8578560c365442` |
| **D2** | Hora | `55417e6b21d85c3ec7d1b3ffdd78d677` | `10ce5a87d78a37658da9fac8759d059a` |
| **D3** | Drekkana | `cc64170086a11e47f5c2f3254b5a4648` | `49f942909bffff584a995a98ef991177` |
| **D4** | Chaturthamsa | `8696eccf3917629922739d1aeea44114` | `33f95a21c1a28605d3204d7a11f757db` |
| **D7** | Saptamsa | `8b82fd9af71d2cac2ac13b2af1361b6b` | `4393de77f7636548290127c777636cab` |
| **D9** | Navamsha | `55417e6b21d85c3ec7d1b3ffdd78d677` | `10ce5a87d78a37658da9fac8759d059a` |
| **D10** | Dasamsa | `7116ad40523a2af9135e9f38ef075aac` | `e97f0cbd8bb017073032321e2cb359d8` |
| **D12** | Dvadasamsa | `cc64170086a11e47f5c2f3254b5a4648` | `49f942909bffff584a995a98ef991177` |
| **D16** | Shodamsa | `f2014a14d0faaea3bb9cb8bb91f35229` | `d349f68af30fb6dd774df644e93d0875` |
| **D20** | Vimsamsa | `7112d9ed1c621a130cdf03f3dcd9639e` | `ec1a2a41fed0582cf84bd4e5863bd146` |
| **D24** | Chaturvimsamsa | `9f4878b240fe517b31e85dd295fc7017` | `896c5b2611ed86e49db753b067659613` |
| **D27** | Bhamsa / Saptavimsamsa | `7112d9ed1c621a130cdf03f3dcd9639e` | `ec1a2a41fed0582cf84bd4e5863bd146` |
| **D30** | Trimsamsa | `55417e6b21d85c3ec7d1b3ffdd78d677` | `10ce5a87d78a37658da9fac8759d059a` |
| **D40** | Khavedamsa | `d9fabb75347ef4d574ce45b8af330aee` | `69ee3803015e883f3bd9f87e434853e2` |
| **D45** | Akshavedamsa | `7112d9ed1c621a130cdf03f3dcd9639e` | `ec1a2a41fed0582cf84bd4e5863bd146` |
| **D60** | Shastiamsa | `157361fbb9780b044262831d0d6db063` | `250afb71f207090a438f426a06d79fe8` |

---

## 4. Automated Testing Suite Proofs

The Astra test suite runs 157 automated tests verifying the engine against these datasets:

| Test Suite File | Tested Subsystem | Proof Mechanism | Status |
| :--- | :--- | :--- | :---: |
| `tests/test_varga_shadbala_transcription.py` | All 16 Vargas (ShadBala) | Direct cell-by-cell & column net total comparison vs transcribed CSVs | ✅ Passed (16/16) |
| `tests/test_varga_lajjitadi_transcription.py` | All 16 Vargas (Drishti Yuti) | Cell-by-cell matrix & column total comparison vs transcribed CSVs | ✅ Passed (16/16) |
| `tests/test_varga_avasthas.py` | Varga Net Modifiers & Dynamic Scaling | Compares calculated varga modifiers against Kala reference values | ✅ Passed (7/7) |
| `tests/test_shadbala.py` | D1 ShadBala & 6-fold components | Validates Sthana, Dig, Kaala, Cheshta, Drig, and Naisargika bala | ✅ Passed (6/6) |
| `tests/test_aspects.py` | Graha Sphuta Drishti | Verifies continuous Virūpa aspects for special and general angles | ✅ Passed (8/8) |
| `tests/test_vimshottari_timeline.py` | Vimshottari Dashas | Validates solar year scaling (365.2422 days) and exact calendar dates | ✅ Passed (4/4) |
| `tests/test_basic_placements.py` | Tropical Zodiac & Cusps | Campanus house projection and Swiss Ephemeris longitudes | ✅ Passed (5/5) |
| `tests/test_dignities.py` | Compound Sambandha | Natural and temporal friendships (Mitra, Satru, Sama) | ✅ Passed (1/1) |

Execute full automated verification with:
```bash
pytest
```

---

## 5. Visual Proofs & Interactive Viewer

To eliminate any ambiguity between raw numbers and user interface rendering, visual side-by-side proofs capture Astra's live screen rendering directly adjacent to Kala's ground-truth tables:

1. **Side-by-Side Proof Generator Scripts:**
   * `vedic-astrology-vault/scripts/generate_all_varga_proofs.py` (Drishti Yuti mode)
   * `vedic-astrology-vault/scripts/generate_all_varga_shadbala_proofs.py` (ShadBala mode)
2. **Unified Interactive Proof Viewer:**
   * **File Path**: `astra_vargas_side_by_side_proof.html`
   * **Features**: Live toggle between Drishti Yuti and ShadBala modes, responsive varga selector tabs (D1 through D60), and side-by-side visual panels comparing live UI screenshots with parsed ground-truth CSV tables.
