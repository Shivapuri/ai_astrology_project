# AI Documentation: lajjita.py (Lajjitadi Avasthas)

## Logic constraints for AI
* **Base Engine:** Uses **Natural Friendship (Naisargika)** exclusively. NEVER use Compound Friendship here.
* **Aspect Rule:** Evaluated strictly using **Degree-based Planetary Aspects (Graha Drishti)** and Conjunctions. This is an Ernst Wilhelm / Kala rule. Do NOT use Rasi Aspects (whole sign aspects).
* **Simultaneity:** A planet can have *multiple* Lajjitadi states at the same time (e.g., both Proud and Delighted). Ensure the function returns a `list` of state dictionaries, not just a single string.
* **Hardcoded Rules based on Ernst Wilhelm / NotebookLM:**
  1. **Lajjita (Ashamed):** (In 5th house AND conjunct Sun, Mars, Saturn) OR (Conjunct Rahu/Ketu AND conjunct Sun, Mars, Saturn).
  2. **Garvita (Proud):** Exaltation or Moolatrikona sign.
  3. **Kshudhita (Starved):** In enemy sign OR conjunct enemy OR aspected by enemy OR conjunct Saturn. (OR logic, not AND logic).
     *Caveat:* If the aspect is from a cruel enemy (Sun, Mars, Saturn, Waning Moon), it causes Kshobhita instead of Starvation.
  4. **Trushita (Thirsty):** In water sign (Cancer, Scorpio, Pisces) AND aspected by enemy AND NOT aspected by benefic.
  5. **Mudita (Delighted):** In friend sign OR conjunct friend OR aspected by friend OR conjunct Jupiter.
     *Caveats:* Saturn is never a friend. Conjunct Sun causes Kshobhita, not Mudita.
  6. **Kshobhita (Agitated):** Conjunct Sun OR aspected by enemy cruel planet (Sun, Mars, Saturn, Waning Moon).
