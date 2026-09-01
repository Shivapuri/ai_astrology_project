# Shadbala & Avastha Audit Report

This report systematically compares the Backend's generated Quantitative Avastha matrices with the true baseline CSVs.

## Shadbala 6 Pillars Micro-Audit Breakdown
| Planet | Sthana | Dig | Kala | Cheshta | Naisargika | Drik | Total (Virupas) | Total (Rupas) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Sun | 145.86 | 41.48 | 139.39 | 58.02 | 60.00 | 12.07 | 456.82 | 7.6137 |
| Moon | 296.36 | 1.60 | 57.67 | 20.11 | 51.40 | -3.71 | 423.43 | 7.0572 |
| Mars | 275.76 | 57.61 | 91.80 | 20.90 | 17.10 | -1.93 | 461.24 | 7.6873 |
| Mercury | 212.44 | 47.81 | 272.35 | 56.36 | 25.70 | 17.86 | 632.52 | 10.5420 |
| Jupiter | 199.14 | 26.18 | 233.77 | 18.67 | 34.30 | -7.44 | 504.62 | 8.4103 |
| Venus | 199.61 | 33.43 | 120.29 | 42.31 | 42.80 | 50.17 | 488.61 | 8.1435 |
| Saturn | 224.13 | 3.84 | 60.64 | 11.32 | 8.60 | 41.85 | 350.38 | 5.8397 |

## Shadbala Matrix Audit
❌ **Status:** 30 Discrepancies Found.
- **Sun Total Baseline**: Expected `794.2`, Got `456.8` (Diff: `337.40`)
- **Moon Total Baseline**: Expected `900.1`, Got `423.4` (Diff: `476.70`)
- **Mars Total Baseline**: Expected `1252.7`, Got `461.2` (Diff: `791.50`)
- **Mercury Total Baseline**: Expected `483.5`, Got `632.5` (Diff: `149.00`)
- **Jupiter Total Baseline**: Expected `1116.6`, Got `504.6` (Diff: `612.00`)
- **Venus Total Baseline**: Expected `-276.1`, Got `488.6` (Diff: `764.70`)
- **Saturn Total Baseline**: Expected `18.3`, Got `350.4` (Diff: `332.10`)
- **Sun → Moon (Net Modifier)**: Expected `0.0`, Got `1.3` (Diff: `1.30`)
- **Sun → Mars (Net Modifier)**: Expected `0.0`, Got `10.3` (Diff: `10.30`)
- **Sun → Venus (Net Modifier)**: Expected `0.0`, Got `-56.1` (Diff: `56.10`)
- **Sun → Saturn (Net Modifier)**: Expected `0.0`, Got `-15.1` (Diff: `15.10`)
- **Moon → Sun (Net Modifier)**: Expected `0.0`, Got `108.2` (Diff: `108.20`)
- **Moon → Mars (Net Modifier)**: Expected `0.0`, Got `423.4` (Diff: `423.40`)
- **Moon → Mercury (Net Modifier)**: Expected `0.0`, Got `-171.1` (Diff: `171.10`)
- **Moon → Jupiter (Net Modifier)**: Expected `0.0`, Got `423.4` (Diff: `423.40`)
- **Moon → Venus (Net Modifier)**: Expected `0.0`, Got `-423.4` (Diff: `423.40`)
- **Moon → Saturn (Net Modifier)**: Expected `0.0`, Got `-423.4` (Diff: `423.40`)
- **Mars → Sun (Net Modifier)**: Expected `0.0`, Got `146.6` (Diff: `146.60`)
- **Mars → Jupiter (Net Modifier)**: Expected `0.0`, Got `461.2` (Diff: `461.20`)
- **Mars → Saturn (Net Modifier)**: Expected `0.0`, Got `-409.9` (Diff: `409.90`)
- **Mercury → Moon (Net Modifier)**: Expected `0.0`, Got `48.7` (Diff: `48.70`)
- **Mercury → Mars (Net Modifier)**: Expected `0.0`, Got `-61.2` (Diff: `61.20`)
- **Mercury → Jupiter (Net Modifier)**: Expected `0.0`, Got `-25.8` (Diff: `25.80`)
- **Mercury → Venus (Net Modifier)**: Expected `0.0`, Got `30.7` (Diff: `30.70`)
- **Jupiter → Sun (Net Modifier)**: Expected `0.0`, Got `109.3` (Diff: `109.30`)
- **Jupiter → Moon (Net Modifier)**: Expected `0.0`, Got `504.6` (Diff: `504.60`)
- **Jupiter → Mars (Net Modifier)**: Expected `0.0`, Got `504.6` (Diff: `504.60`)
- **Venus → Jupiter (Net Modifier)**: Expected `0.0`, Got `-165.8` (Diff: `165.80`)
- **Venus → Saturn (Net Modifier)**: Expected `0.0`, Got `488.6` (Diff: `488.60`)
- **Saturn → Venus (Net Modifier)**: Expected `0.0`, Got `-350.4` (Diff: `350.40`)

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
❌ **Status:** 8 Discrepancies Found.
- **Mars → Sun (Net Modifier)**: Expected `8.7`, Got `6.6` (Diff: `2.10`)
- **Mars → Jupiter (Net Modifier)**: Expected `27.2`, Got `20.9` (Diff: `6.30`)
- **Mars → Saturn (Net Modifier)**: Expected `-29.1`, Got `-34.7` (Diff: `5.60`)
- **Jupiter → Moon (Net Modifier)**: Expected `19.9`, Got `18.7` (Diff: `1.20`)
- **Jupiter → Mars (Net Modifier)**: Expected `19.9`, Got `18.7` (Diff: `1.20`)
- **Venus → Jupiter (Net Modifier)**: Expected `-8.5`, Got `-6.0` (Diff: `2.50`)
- **Venus → Saturn (Net Modifier)**: Expected `35.1`, Got `42.3` (Diff: `7.20`)
- **Saturn → Venus (Net Modifier)**: Expected `-48.0`, Got `-48.7` (Diff: `0.70`)

## Subha Matrix Audit
❌ **Status:** 17 Discrepancies Found.
- **Moon → Sun (Net Modifier)**: Expected `5.6`, Got `4.2` (Diff: `1.40`)
- **Moon → Mars (Net Modifier)**: Expected `22.0`, Got `16.3` (Diff: `5.70`)
- **Moon → Mercury (Net Modifier)**: Expected `-15.4`, Got `-17.7` (Diff: `2.30`)
- **Moon → Jupiter (Net Modifier)**: Expected `22.0`, Got `16.3` (Diff: `5.70`)
- **Moon → Venus (Net Modifier)**: Expected `-38.0`, Got `-43.7` (Diff: `5.70`)
- **Moon → Saturn (Net Modifier)**: Expected `-38.0`, Got `-43.7` (Diff: `5.70`)
- **Mars → Sun (Net Modifier)**: Expected `7.4`, Got `9.8` (Diff: `2.40`)
- **Mars → Jupiter (Net Modifier)**: Expected `23.4`, Got `30.8` (Diff: `7.40`)
- **Mars → Saturn (Net Modifier)**: Expected `-32.5`, Got `-25.9` (Diff: `6.60`)
- **Mercury → Moon (Net Modifier)**: Expected `1.4`, Got `0.8` (Diff: `0.60`)
- **Mercury → Mars (Net Modifier)**: Expected `-4.0`, Got `-4.8` (Diff: `0.80`)
- **Jupiter → Sun (Net Modifier)**: Expected `2.5`, Got `7.1` (Diff: `4.60`)
- **Jupiter → Moon (Net Modifier)**: Expected `11.5`, Got `32.7` (Diff: `21.20`)
- **Jupiter → Mars (Net Modifier)**: Expected `11.5`, Got `32.7` (Diff: `21.20`)
- **Venus → Jupiter (Net Modifier)**: Expected `-12.6`, Got `-11.3` (Diff: `1.30`)
- **Venus → Saturn (Net Modifier)**: Expected `22.8`, Got `26.7` (Diff: `3.90`)
- **Saturn → Venus (Net Modifier)**: Expected `-44.8`, Got `-21.2` (Diff: `23.60`)

## Ishta Matrix Audit
❌ **Status:** 14 Discrepancies Found.
- **Sun → Mercury (Net Modifier)**: Expected `-11.7`, Got `35.0` (Diff: `46.70`)
- **Moon → Sun (Net Modifier)**: Expected `9.4`, Got `8.4` (Diff: `1.00`)
- **Moon → Mars (Net Modifier)**: Expected `36.7`, Got `32.8` (Diff: `3.90`)
- **Moon → Mercury (Net Modifier)**: Expected `-9.4`, Got `-11.0` (Diff: `1.60`)
- **Moon → Jupiter (Net Modifier)**: Expected `36.7`, Got `32.8` (Diff: `3.90`)
- **Moon → Venus (Net Modifier)**: Expected `-23.3`, Got `-27.2` (Diff: `3.90`)
- **Moon → Saturn (Net Modifier)**: Expected `-23.3`, Got `-27.2` (Diff: `3.90`)
- **Mars → Sun (Net Modifier)**: Expected `10.0`, Got `8.7` (Diff: `1.30`)
- **Mars → Jupiter (Net Modifier)**: Expected `31.5`, Got `27.3` (Diff: `4.20`)
- **Mars → Saturn (Net Modifier)**: Expected `-25.3`, Got `-29.1` (Diff: `3.80`)
- **Jupiter → Moon (Net Modifier)**: Expected `27.0`, Got `25.2` (Diff: `1.80`)
- **Jupiter → Mars (Net Modifier)**: Expected `27.0`, Got `25.2` (Diff: `1.80`)
- **Venus → Saturn (Net Modifier)**: Expected `27.4`, Got `28.8` (Diff: `1.40`)
- **Saturn → Venus (Net Modifier)**: Expected `-39.5`, Got `-41.8` (Diff: `2.30`)

## Summary
Checked a total of **252** relational cells across matrices.
Found **79** discrepancies (Delta > 0.5).