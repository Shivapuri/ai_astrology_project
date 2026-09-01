# Shadbala & Avastha Audit Report

This report systematically compares the Backend's generated Quantitative Avastha matrices with the true baseline CSVs.

## Shadbala 6 Pillars Micro-Audit Breakdown
| Planet | Sthana | Dig | Kala | Cheshta | Naisargika | Drik | Total (Virupas) | Total (Rupas) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Sun | 145.86 | 45.16 | 139.39 | 58.02 | 60.00 | 12.07 | 460.50 | 7.6750 |
| Moon | 296.36 | 5.27 | 57.67 | 20.11 | 51.40 | -3.71 | 427.10 | 7.1183 |
| Mars | 275.76 | 53.94 | 91.80 | 27.16 | 17.10 | -1.93 | 463.83 | 7.7305 |
| Mercury | 212.44 | 47.81 | 272.35 | 55.03 | 25.70 | 17.86 | 631.19 | 10.5198 |
| Jupiter | 199.14 | 26.18 | 233.77 | 19.84 | 34.30 | -7.44 | 505.79 | 8.4298 |
| Venus | 199.61 | 29.75 | 120.29 | 35.01 | 42.80 | 50.17 | 477.63 | 7.9605 |
| Saturn | 224.13 | 3.84 | 60.64 | 12.02 | 8.60 | 41.85 | 351.08 | 5.8513 |

## Uccha Matrix Audit
✅ **Status:** Perfectly Aligned.

## Dig Matrix Audit
❌ **Status:** 13 Discrepancies Found.
- **Sun → Mercury (Net Modifier)**: Expected `26.8`, Got `30.4` (Diff: `3.60`)
- **Moon → Sun (Net Modifier)**: Expected `0.6`, Got `1.4` (Diff: `0.80`)
- **Moon → Mars (Net Modifier)**: Expected `2.2`, Got `5.3` (Diff: `3.10`)
- **Moon → Mercury (Net Modifier)**: Expected `-23.4`, Got `-22.1` (Diff: `1.30`)
- **Moon → Jupiter (Net Modifier)**: Expected `2.2`, Got `5.3` (Diff: `3.10`)
- **Moon → Venus (Net Modifier)**: Expected `-57.8`, Got `-54.7` (Diff: `3.10`)
- **Moon → Saturn (Net Modifier)**: Expected `-57.8`, Got `-54.7` (Diff: `3.10`)
- **Mars → Sun (Net Modifier)**: Expected `18.3`, Got `17.1` (Diff: `1.20`)
- **Mars → Jupiter (Net Modifier)**: Expected `57.7`, Got `53.9` (Diff: `3.80`)
- **Mars → Saturn (Net Modifier)**: Expected `-2.1`, Got `-5.4` (Diff: `3.30`)
- **Jupiter → Sun (Net Modifier)**: Expected `6.5`, Got `5.7` (Diff: `0.80`)
- **Jupiter → Moon (Net Modifier)**: Expected `30.0`, Got `26.2` (Diff: `3.80`)
- **Jupiter → Mars (Net Modifier)**: Expected `30.0`, Got `26.2` (Diff: `3.80`)

## Cheshta Matrix Audit
✅ **Status:** Perfectly Aligned.

## Subha Matrix Audit
❌ **Status:** 16 Discrepancies Found.
- **Moon → Sun (Net Modifier)**: Expected `5.6`, Got `4.2` (Diff: `1.40`)
- **Moon → Mars (Net Modifier)**: Expected `22.0`, Got `16.3` (Diff: `5.70`)
- **Moon → Mercury (Net Modifier)**: Expected `-15.4`, Got `-17.7` (Diff: `2.30`)
- **Moon → Jupiter (Net Modifier)**: Expected `22.0`, Got `16.3` (Diff: `5.70`)
- **Moon → Venus (Net Modifier)**: Expected `-38.0`, Got `-43.7` (Diff: `5.70`)
- **Moon → Saturn (Net Modifier)**: Expected `-38.0`, Got `-43.7` (Diff: `5.70`)
- **Mars → Sun (Net Modifier)**: Expected `7.4`, Got `9.0` (Diff: `1.60`)
- **Mars → Jupiter (Net Modifier)**: Expected `23.4`, Got `28.2` (Diff: `4.80`)
- **Mars → Saturn (Net Modifier)**: Expected `-32.5`, Got `-28.3` (Diff: `4.20`)
- **Mercury → Mars (Net Modifier)**: Expected `-4.0`, Got `-4.7` (Diff: `0.70`)
- **Jupiter → Sun (Net Modifier)**: Expected `2.5`, Got `7.0` (Diff: `4.50`)
- **Jupiter → Moon (Net Modifier)**: Expected `11.5`, Got `32.2` (Diff: `20.70`)
- **Jupiter → Mars (Net Modifier)**: Expected `11.5`, Got `32.2` (Diff: `20.70`)
- **Venus → Jupiter (Net Modifier)**: Expected `-12.6`, Got `-9.6` (Diff: `3.00`)
- **Venus → Saturn (Net Modifier)**: Expected `22.8`, Got `31.8` (Diff: `9.00`)
- **Saturn → Venus (Net Modifier)**: Expected `-44.8`, Got `-21.5` (Diff: `23.30`)

## Ishta Matrix Audit
❌ **Status:** 11 Discrepancies Found.
- **Sun → Mercury (Net Modifier)**: Expected `-11.7`, Got `35.0` (Diff: `46.70`)
- **Moon → Sun (Net Modifier)**: Expected `9.4`, Got `8.4` (Diff: `1.00`)
- **Moon → Mars (Net Modifier)**: Expected `36.7`, Got `32.8` (Diff: `3.90`)
- **Moon → Mercury (Net Modifier)**: Expected `-9.4`, Got `-11.0` (Diff: `1.60`)
- **Moon → Jupiter (Net Modifier)**: Expected `36.7`, Got `32.8` (Diff: `3.90`)
- **Moon → Venus (Net Modifier)**: Expected `-23.3`, Got `-27.2` (Diff: `3.90`)
- **Moon → Saturn (Net Modifier)**: Expected `-23.3`, Got `-27.2` (Diff: `3.90`)
- **Jupiter → Moon (Net Modifier)**: Expected `27.0`, Got `26.0` (Diff: `1.00`)
- **Jupiter → Mars (Net Modifier)**: Expected `27.0`, Got `26.0` (Diff: `1.00`)
- **Venus → Saturn (Net Modifier)**: Expected `27.4`, Got `26.2` (Diff: `1.20`)
- **Saturn → Venus (Net Modifier)**: Expected `-39.5`, Got `-41.3` (Diff: `1.80`)

## Summary
Checked a total of **210** relational cells across matrices.
Found **40** discrepancies (Delta > 0.5).