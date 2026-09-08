# AI Documentation: quantitative.py (Quantitative Lajjitadi Avasthas Engine)

## Methodology & Epistemology
Calculates the quantitative modification of planetary strengths through Lajjitadi Avasthas based on Ernst Wilhelm's Kala methodology.
Every cell provides complete sub-values matching Kala software down to 0.1 precision.

## Mathematical & Structural Rules
1. **Matrix Dimensions:**
   - Rows: Giving Planet (`p_give`)
   - Columns: Receiving Planet (`p_recv`)
   - 7 Classical Grahas: Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn.

2. **Aspect Strength (0-60 Virupas):**
   - Full conjunction (same sign): 60.0 Virupas.
   - Lord of receiving planet's sign (Dispositorship): 60.0 Virupas.
   - Mutual Reception (Parivartana Yoga): 60.0 Virupas.
   - Otherwise: Exact Graha Sphuta Drishti (Ernst Wilhelm / Kala longitude aspect calculation).

3. **Qualitative State Classification:**
   - **Positive Pull (`has_pos`):** Mudita (Delighted), Garvita (Proud).
   - **Negative Pull (`has_neg`):** Kshudhita (Starved), Kshobhita (Agitated), Lajjita (Ashamed), Trushita (Thirsty).
   - **Neutral Pull (`has_neutral`):** Active aspect (> 0 Virupas) where neither positive nor negative conditions exist.

4. **Cell Anatomies (5 Discrete Layouts):**
   - **Pure Positive Cell:** Top = Pull Modifier `+Δ` (Green), Bottom = Isolated Total Base `+ Δ` (Green, prefixed with `+`).
   - **Pure Negative Cell:** Top = Pull Modifier `-Δ` (Red), Bottom = Isolated Total Base `- Δ` (Red).
   - **Neutral Cell:** Top = Neutral Pull `Δ` (Blue), Bottom = Receiver Base Unchanged (Blue). Excluded from column net sum.
   - **Dual-Polarity Cell (4 numbers):**
     - Top-Left: `-Neg Pull` (Red)
     - Top-Right: `+Pos Pull` (Green)
     - Bottom-Left: `Isolated Negative` (Red)
     - Bottom-Right: `Isolated Positive` (Green with `+`)
   - **Diagonal Self-Cell (3-tier stack):**
     - Top: Base Score (Green / Black)
     - Middle: Net Difference `Base - Base_Negative` (Bold Black, suffixed with `*2` if Mars in Moolatrikona)
     - Bottom: Negative Base Score (Red)
      - *(Note: In ShadBala Mode for D1, the diagonal displays a single bold black Base number with `*2` flag for Mars; in divisional charts ($V \ne \text{D1}$), the diagonal displays the planet's Vimshopaka dignity for that Varga's Parashari scheme).*
      - *(Note: In Vimshopaka Mode, the diagonal displays the Parashari Vimshopaka dignity).*
      - *(Note: In Drishti Yuti Mode, the diagonal displays the `Vimsho.` dignity score while keeping raw base None for D1 aspect summation).*

   - **ShadBala & Vimshopaka Pull Rules:**
      - Both positive and negative pulls pull the giving planet's baseline score:
        $$\text{Pull} = \text{Base}(p_{\text{give}}) \cdot \frac{\text{Aspect Virupas}}{60.0}$$

5. **Mars Moolatrikona & Dignity Rules:**
   - When Mars is in Aries (its Moolatrikona sign), a visual flag `*2` is attached to its diagonal difference/base.
   - The column total for Mars strictly uses the unmultiplied base (e.g. 454.6 in Shadbala, 31.5 in Ishta, etc.).
   - In **Drishti Yuti Mode**, Mars receives a self-aspect dignity of `60.0` Virupas on its diagonal, which adds directly to the Mars column total ($175.5$).

6. **Veda Bala Exact Classical Formula:**
   - Veda Bala weights the three personal planetary strengths with classical Sanskrit meter proportions:
     $$\text{Veda} = \frac{3 \cdot \text{Uccha Bala} + 2 \cdot \text{Dig Bala} + 3 \cdot \text{Cheshta Bala}}{8}$$
   - Perfectly matches Kala's baseline values for all 7 planets.

7. **Column Net Totals (`+` Summary Row):**
   $$\text{Column Total} = \text{Receiver Base} + \sum \text{Pos Pulls} - \sum \text{Neg Pulls}$$
   (Neutral blue pulls are strictly excluded from the sum).

8. **Multi-Varga Avasthas Calibration (The Four Parashari Varga Schemes):**
   - Planetary social states (*Lajjitadi Avasthas*) function across all 16 divisional charts (*Shodashavargas*).
   - In Ernst Wilhelm's Kala methodology, the net modifier scores across divisional charts group into the four classical Parashari schemes (*Varga Bhedas*):
     - **Shadvarga (6 charts)**: D1 (6), D2 (2), D3 (4), D9 (5), D12 (2), D30 (1). Total = 20 points.
     - **Saptavarga (7 charts)**: D1 (5), D2 (2), D3 (3), D7 (2.5), D9 (4.5), D12 (2), D30 (1). Total = 20 points.
     - **Dasavarga (10 charts)**: D1 (3), D2 (1.5), D3 (1.5), D7 (1.5), D9 (1.5), D10 (1.5), D12 (1.5), D16 (1.5), D30 (1.5), D60 (5). Total = 20 points.
     - **Shodashavarga (16 charts)**: D1 (3.5), D2 (1), D3 (1), D4 (0.5), D7 (0.5), D9 (3), D10 (0.5), D12 (0.5), D16 (2), D20 (0.5), D24 (0.5), D27 (0.5), D30 (1), D40 (0.5), D45 (0.5), D60 (4). Total = 20 points.
   - **Vimshopaka Coupling Factor**: The planetary strength interaction is modulated by the planet's Vimshopaka dignity scale ($0.0$ to $1.0$, derived from the 20-point system).
   - **Conjunction Dissolution (e.g. Mercury +60.0 Shift)**:
     - In D1, Mercury conjoined Sun incurs a $-60.0$ *Kshobhita* (Agitated) penalty (net modifier $-14.7$).
     - In D3 (and other separated divisions like D12), Mercury and Sun separate into different signs. The $-60.0$ penalty dissolves, shifting Mercury by exactly $+60.0$ to $+45.3$ (down to 0.1 decimal precision).
   - **Engine Function**: `calculate_varga_lajjitadi_net_modifiers(chart_data)` computes the full $16 \times 7$ modifier matrix for all divisional charts.

