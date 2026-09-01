# Shadbala & Avastha Audit Report

This report systematically compares the Backend's generated Quantitative Avastha matrices with the true baseline CSVs.

## Shadbala 6 Pillars Micro-Audit Breakdown
| Planet | Sthana | Dig | Kala | Cheshta | Naisarg | Drik | Total (V) | Subha | Asubha | Ishta | Kashta |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Sun | 145.86 | 43.50 | 139.39 | 58.02 | 60.00 | 12.07 | 458.84 | 6.56 | 53.44 | 48.44 | 11.56 |
| Moon | 296.36 | 1.82 | 57.67 | 20.11 | 51.40 | -3.71 | 423.65 | 22.03 | 37.97 | 36.73 | 23.27 |
| Mars | 275.76 | 57.28 | 91.80 | 27.16 | 17.10 | -1.93 | 467.17 | 23.44 | 36.56 | 31.46 | 28.54 |
| Mercury | 212.44 | 49.14 | 272.35 | 55.03 | 25.70 | 17.86 | 632.52 | 18.75 | 41.25 | 43.73 | 16.27 |
| Jupiter | 199.14 | 29.83 | 233.77 | 19.84 | 34.30 | -7.44 | 509.44 | 11.25 | 48.75 | 26.99 | 33.01 |
| Venus | 199.61 | 29.78 | 120.29 | 35.01 | 42.80 | 50.17 | 477.66 | 22.50 | 37.50 | 27.31 | 32.69 |
| Saturn | 224.13 | 3.42 | 60.64 | 12.02 | 8.60 | 41.85 | 350.66 | 15.00 | 45.00 | 20.57 | 39.43 |

## Uccha Matrix Audit
❌ **Status:** 1 Discrepancies Found.
- **Sun → Mercury (Net Modifier)**: Expected `17.8`, Got `-21.1` (Diff: `38.90`)

## Dig Matrix Audit
❌ **Status:** 1 Discrepancies Found.
- **Sun → Mercury (Net Modifier)**: Expected `26.8`, Got `-16.5` (Diff: `43.30`)

## Cheshta Matrix Audit
❌ **Status:** 1 Discrepancies Found.
- **Sun → Mercury (Net Modifier)**: Expected `55.6`, Got `-2.0` (Diff: `57.60`)

## Subha Matrix Audit
❌ **Status:** 1 Discrepancies Found.
- **Sun → Mercury (Net Modifier)**: Expected `-46.5`, Got `-53.4` (Diff: `6.90`)

## Ishta Matrix Audit
❌ **Status:** 1 Discrepancies Found.
- **Sun → Mercury (Net Modifier)**: Expected `36.6`, Got `-11.6` (Diff: `48.20`)

## Summary
Checked a total of **210** relational cells across matrices.
Found **5** discrepancies (Delta > 0.5).