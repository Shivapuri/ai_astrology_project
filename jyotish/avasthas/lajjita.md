# AI Documentation: lajjita.py (Lajjitadi Avasthas)

## Logic constraints for AI
* **Base Engine:** Uses **Natural Friendship (Naisargika)** exclusively. NEVER use Compound Friendship here.
* **Aspect Rule:** Evaluated using **Rasi Aspects** (whole sign aspects), not standard planetary degree aspects.
* **Simultaneity:** A planet can have *multiple* Lajjitadi states at the same time (e.g., both Proud and Delighted). Ensure the function returns a `list` of states, not just a single string.
* **Hardcoded Rules:**
  - Jupiter is NEVER an enemy for Kshudhita (Starved).
  - Saturn is NEVER a friend for Mudita (Delighted).
