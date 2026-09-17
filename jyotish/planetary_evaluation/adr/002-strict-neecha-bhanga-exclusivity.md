# ADR-002: Strict Neecha Bhanga Exclusivity (True Signs of Fall vs. Enemy Signs)

## Context & The Shortcoming in the Naive Model
*Neecha Bhanga* (cancellation of debility) is an alchemical rule where a fallen planet's weakness is transmuted into profound strength if its sign ruler (*dispositor*) is dignified and strong. 

However, earlier iterations of software engines had loose logic that checked if a planet was under stress or in an enemy sign (*Shatru*), and if the host was strong, awarded it "Neecha Bhanga". This caused false positives, treating ordinary difficult placements as miraculous alchemical cancellations.

### The Real-Life Case: Swami Hari Om Puri
* **Chart:** Swami Hari Om Puri (Vedic teacher and spiritual ascetic).
* **Placement:** Mars in Virgo at 10° conjoined Ketu and Sun, under heavy malefic pressure. Host Mercury is in Gemini (strong).
* **The Failure:** If the engine loosely assumed that Mars in Virgo was "fallen" because it was strained and conjoined by Ketu, a strong host Mercury would grant it "Neecha Bhanga" and elevate it to a heroic status.

## Decision
1. **Enforce the Classical Exclusivity Rule:**
   *Neecha Bhanga* is **strictly and exclusively** eligible for planets residing in their true classical signs of fall (*Neecha*):
   - **Sun:** Libra ($10^\circ$)
   - **Moon:** Scorpio ($3^\circ$)
   - **Mars:** Cancer ($28^\circ$)
   - **Mercury:** Pisces ($15^\circ$)
   - **Jupiter:** Capricorn ($5^\circ$)
   - **Venus:** Virgo ($27^\circ$)
   - **Saturn:** Aries ($20^\circ$)
   - **Rahu:** Scorpio / **Ketu:** Taurus
2. **Enemy Signs are NOT Debilitated:**
   A planet in an enemy sign (like Mars in Virgo or Saturn in Cancer) is facing friction, but it is not in fall (*Neecha*). It cannot and must not receive *Neecha Bhanga*.

## Proof & Validation
Swami Hari Om Puri's Mars in Virgo is recognized as an enemy sign with conjunction friction. It is strictly denied *Neecha Bhanga* and diagnosed honestly as **`🌪️ The Embattled Striver`** with a vitality score of **★ 4.4 / 10 Strained**. This preserves rigorous scriptural integrity (*Phaladeepika* Ch. 6 and *BPHS* Ch. 41).
