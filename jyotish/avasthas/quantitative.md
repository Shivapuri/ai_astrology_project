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
     - *(Note: In ShadBala Mode, the diagonal displays a single bold black Base number with `*2` flag for Mars, as no negative base exists).*

   - **ShadBala Pull Rules:**
     - Both positive and negative pulls pull the giving planet's full ShadBala base:
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
