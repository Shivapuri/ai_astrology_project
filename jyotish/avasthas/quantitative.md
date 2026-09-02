# AI Documentation: quantitative.py (Quantitative Lajjitadi Avasthas Engine)

## Methodology & Epistemology
Calculates the quantitative modification of planetary strengths through Lajjitadi Avasthas based on Ernst Wilhelm's Kala methodology.

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

4. **Pull Computations:**
   - **Drishti Yuti Mode:** Raw aspect virupas assigned directly to positive, negative, or neutral pull.
   - **Weighted Modes (ShadBala, Ishta, Subha, Uccha, Dig, Cheshta, Veda):**
     - Positive pull = `Base(giver) * (aspect_virupas / 60.0)`
     - Negative pull = `Kashta/Asubha/Deficit(giver) * (aspect_virupas / 60.0)`
     - Neutral pull = `Base(giver) * (aspect_virupas / 60.0)`
   - **Net Pull:** `positive_pull - negative_pull` (Neutral pull is strictly omitted from column total modification to preserve net column balance).

5. **Diagonal Stacks (Giver == Receiver):**
   - Renders Base Strength, Difference (`Base - Base_Negative`), and Base Negative (Red).
   - Column Net Total is calculated from `Base + sum(net_pulls)`.
