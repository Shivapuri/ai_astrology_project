# Shadbala & Avastha Audit Report

This report systematically compares the Backend's generated Quantitative Avastha matrices with the true baseline CSVs.

## Shadbala 6 Pillars Micro-Audit Breakdown
| Planet | Sthana | Dig | Kala | Cheshta | Naisargika | Drik | Total (Virupas) | Total (Rupas) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Sun | 145.86 | 41.48 | 139.39 | 58.02 | 60.00 | 12.07 | 456.82 | 7.6137 |
| Moon | 296.36 | 1.60 | 57.67 | 20.11 | 51.40 | -3.71 | 423.43 | 7.0572 |
| Mars | 275.76 | 57.61 | 91.80 | 27.16 | 17.10 | -1.93 | 467.50 | 7.7917 |
| Mercury | 212.44 | 47.81 | 272.35 | 55.03 | 25.70 | 17.86 | 631.19 | 10.5198 |
| Jupiter | 199.14 | 26.18 | 233.77 | 19.84 | 34.30 | -7.44 | 505.79 | 8.4298 |
| Venus | 199.61 | 33.43 | 120.29 | 35.01 | 42.80 | 50.17 | 481.31 | 8.0218 |
| Saturn | 224.13 | 3.84 | 60.64 | 12.02 | 8.60 | 41.85 | 351.08 | 5.8513 |

## Shadbala Matrix Audit
❌ **Status:** 29 Discrepancies Found.
- **Sun Total Baseline**: Expected `794.2`, Got `460.9` (Diff: `333.30`)
- **Moon Total Baseline**: Expected `900.1`, Got `915.8` (Diff: `15.70`)
- **Mars Total Baseline**: Expected `1252.7`, Got `591.0` (Diff: `661.70`)
- **Mercury Total Baseline**: Expected `483.5`, Got `77.7` (Diff: `405.80`)
- **Jupiter Total Baseline**: Expected `1116.6`, Got `1121.2` (Diff: `4.60`)
- **Venus Total Baseline**: Expected `-276.1`, Got `470.5` (Diff: `746.60`)
- **Saturn Total Baseline**: Expected `18.3`, Got `-38.5` (Diff: `56.80`)
- **Sun → Moon (Net Modifier)**: Expected `0.0`, Got `1.3` (Diff: `1.30`)
- **Sun → Mars (Net Modifier)**: Expected `0.0`, Got `10.3` (Diff: `10.30`)
- **Sun → Mercury (Net Modifier)**: Expected `0.0`, Got `450.3` (Diff: `450.30`)
- **Sun → Venus (Net Modifier)**: Expected `0.0`, Got `-0.8` (Diff: `0.80`)
- **Moon → Sun (Net Modifier)**: Expected `0.0`, Got `108.2` (Diff: `108.20`)
- **Moon → Mars (Net Modifier)**: Expected `0.0`, Got `423.4` (Diff: `423.40`)
- **Moon → Mercury (Net Modifier)**: Expected `0.0`, Got `-6.6` (Diff: `6.60`)
- **Moon → Jupiter (Net Modifier)**: Expected `0.0`, Got `423.4` (Diff: `423.40`)
- **Moon → Venus (Net Modifier)**: Expected `0.0`, Got `-16.3` (Diff: `16.30`)
- **Moon → Saturn (Net Modifier)**: Expected `0.0`, Got `-16.3` (Diff: `16.30`)
- **Mars → Sun (Net Modifier)**: Expected `0.0`, Got `148.6` (Diff: `148.60`)
- **Mars → Jupiter (Net Modifier)**: Expected `0.0`, Got `467.5` (Diff: `467.50`)
- **Mars → Saturn (Net Modifier)**: Expected `0.0`, Got `-25.1` (Diff: `25.10`)
- **Mercury → Moon (Net Modifier)**: Expected `0.0`, Got `48.6` (Diff: `48.60`)
- **Mercury → Mars (Net Modifier)**: Expected `0.0`, Got `-1.1` (Diff: `1.10`)
- **Mercury → Venus (Net Modifier)**: Expected `0.0`, Got `30.7` (Diff: `30.70`)
- **Jupiter → Sun (Net Modifier)**: Expected `0.0`, Got `109.6` (Diff: `109.60`)
- **Jupiter → Moon (Net Modifier)**: Expected `0.0`, Got `505.8` (Diff: `505.80`)
- **Jupiter → Mars (Net Modifier)**: Expected `0.0`, Got `505.8` (Diff: `505.80`)
- **Venus → Jupiter (Net Modifier)**: Expected `0.0`, Got `-10.8` (Diff: `10.80`)
- **Venus → Saturn (Net Modifier)**: Expected `0.0`, Got `481.3` (Diff: `481.30`)
- **Saturn → Venus (Net Modifier)**: Expected `0.0`, Got `-38.5` (Diff: `38.50`)

## Uccha Matrix Audit
✅ **Status:** Perfectly Aligned.

## Dig Matrix Audit
❌ **Status:** 10 Discrepancies Found.
- **Sun → Mercury (Net Modifier)**: Expected `26.8`, Got `23.0` (Diff: `3.80`)
- **Moon → Mars (Net Modifier)**: Expected `2.2`, Got `1.6` (Diff: `0.60`)
- **Moon → Jupiter (Net Modifier)**: Expected `2.2`, Got `1.6` (Diff: `0.60`)
- **Moon → Venus (Net Modifier)**: Expected `-57.8`, Got `-58.4` (Diff: `0.60`)
- **Moon → Saturn (Net Modifier)**: Expected `-57.8`, Got `-58.4` (Diff: `0.60`)
- **Jupiter → Sun (Net Modifier)**: Expected `6.5`, Got `5.7` (Diff: `0.80`)
- **Jupiter → Moon (Net Modifier)**: Expected `30.0`, Got `26.2` (Diff: `3.80`)
- **Jupiter → Mars (Net Modifier)**: Expected `30.0`, Got `26.2` (Diff: `3.80`)
- **Venus → Jupiter (Net Modifier)**: Expected `-10.4`, Got `-9.0` (Diff: `1.40`)
- **Venus → Saturn (Net Modifier)**: Expected `29.4`, Got `33.4` (Diff: `4.00`)

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
Checked a total of **252** relational cells across matrices.
Found **66** discrepancies (Delta > 0.5).