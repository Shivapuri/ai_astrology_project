# Shadbala & Avastha Audit Report

This report systematically compares the Backend's generated Quantitative Avastha matrices with the true baseline CSVs.

## Shadbala 6 Pillars Micro-Audit Breakdown
| Planet | Sthana | Dig | Kala | Cheshta | Naisargika | Drik | Total (Virupas) | Total (Rupas) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Sun | 145.86 | 43.50 | 139.39 | 58.02 | 60.00 | 12.07 | 458.84 | 7.6473 |
| Moon | 296.36 | 1.82 | 57.67 | 20.11 | 51.40 | -3.71 | 423.65 | 7.0608 |
| Mars | 275.76 | 57.28 | 91.80 | 27.16 | 17.10 | -1.93 | 467.17 | 7.7862 |
| Mercury | 212.44 | 49.14 | 272.35 | 55.03 | 25.70 | 17.86 | 632.52 | 10.5420 |
| Jupiter | 199.14 | 29.83 | 233.77 | 19.84 | 34.30 | -7.44 | 509.44 | 8.4907 |
| Venus | 199.61 | 29.78 | 120.29 | 35.01 | 42.80 | 50.17 | 477.66 | 7.9610 |
| Saturn | 224.13 | 3.42 | 60.64 | 12.02 | 8.60 | 41.85 | 350.66 | 5.8443 |

## Uccha Matrix Audit
✅ **Status:** Perfectly Aligned.

## Dig Matrix Audit
✅ **Status:** Perfectly Aligned.

## Cheshta Matrix Audit
✅ **Status:** Perfectly Aligned.

## Subha Matrix Audit
❌ **Status:** 20 Discrepancies Found.
- **Sun → Mercury (Net Modifier)**: Expected `-46.5`, Got `0.0` (Diff: `46.50`)
- **Sun → Venus (Net Modifier)**: Expected `-6.5`, Got `-0.8` (Diff: `5.70`)
- **Sun → Saturn (Net Modifier)**: Expected `-1.8`, Got `-0.2` (Diff: `1.60`)
- **Moon → Sun (Net Modifier)**: Expected `5.6`, Got `4.2` (Diff: `1.40`)
- **Moon → Mars (Net Modifier)**: Expected `22.0`, Got `16.3` (Diff: `5.70`)
- **Moon → Mercury (Net Modifier)**: Expected `-15.4`, Got `-6.6` (Diff: `8.80`)
- **Moon → Jupiter (Net Modifier)**: Expected `22.0`, Got `16.3` (Diff: `5.70`)
- **Moon → Venus (Net Modifier)**: Expected `-38.0`, Got `-16.3` (Diff: `21.70`)
- **Moon → Saturn (Net Modifier)**: Expected `-38.0`, Got `-16.3` (Diff: `21.70`)
- **Mars → Sun (Net Modifier)**: Expected `7.4`, Got `9.0` (Diff: `1.60`)
- **Mars → Jupiter (Net Modifier)**: Expected `23.4`, Got `28.2` (Diff: `4.80`)
- **Mars → Saturn (Net Modifier)**: Expected `-32.5`, Got `-25.1` (Diff: `7.40`)
- **Mercury → Mars (Net Modifier)**: Expected `-4.0`, Got `-1.1` (Diff: `2.90`)
- **Mercury → Jupiter (Net Modifier)**: Expected `-1.7`, Got `-0.5` (Diff: `1.20`)
- **Jupiter → Sun (Net Modifier)**: Expected `2.5`, Got `7.0` (Diff: `4.50`)
- **Jupiter → Moon (Net Modifier)**: Expected `11.5`, Got `32.2` (Diff: `20.70`)
- **Jupiter → Mars (Net Modifier)**: Expected `11.5`, Got `32.2` (Diff: `20.70`)
- **Venus → Jupiter (Net Modifier)**: Expected `-12.6`, Got `-10.8` (Diff: `1.80`)
- **Venus → Saturn (Net Modifier)**: Expected `22.8`, Got `31.8` (Diff: `9.00`)
- **Saturn → Venus (Net Modifier)**: Expected `-44.8`, Got `-38.5` (Diff: `6.30`)

## Ishta Matrix Audit
❌ **Status:** 12 Discrepancies Found.
- **Sun → Mercury (Net Modifier)**: Expected `36.6`, Got `41.0` (Diff: `4.40`)
- **Sun → Venus (Net Modifier)**: Expected `-1.4`, Got `-0.8` (Diff: `0.60`)
- **Moon → Sun (Net Modifier)**: Expected `9.4`, Got `8.4` (Diff: `1.00`)
- **Moon → Mars (Net Modifier)**: Expected `36.7`, Got `32.8` (Diff: `3.90`)
- **Moon → Mercury (Net Modifier)**: Expected `-9.4`, Got `-6.6` (Diff: `2.80`)
- **Moon → Jupiter (Net Modifier)**: Expected `36.7`, Got `32.8` (Diff: `3.90`)
- **Moon → Venus (Net Modifier)**: Expected `-23.3`, Got `-16.3` (Diff: `7.00`)
- **Moon → Saturn (Net Modifier)**: Expected `-23.3`, Got `-16.3` (Diff: `7.00`)
- **Jupiter → Moon (Net Modifier)**: Expected `27.0`, Got `26.0` (Diff: `1.00`)
- **Jupiter → Mars (Net Modifier)**: Expected `27.0`, Got `26.0` (Diff: `1.00`)
- **Venus → Saturn (Net Modifier)**: Expected `27.4`, Got `26.2` (Diff: `1.20`)
- **Saturn → Venus (Net Modifier)**: Expected `-39.5`, Got `-38.5` (Diff: `1.00`)

## Summary
Checked a total of **210** relational cells across matrices.
Found **32** discrepancies (Delta > 0.5).