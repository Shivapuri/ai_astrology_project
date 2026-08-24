"""
Jagrat Avastha (Consciousness / Alertness)
==========================================
This module calculates the Jagrat Avastha (state of consciousness or alertness) of a planet.

How it is calculated:
This Avastha measures whether a planet is "awake" and fully aware, or if its effects 
are muffled as if "slumbering." It is determined strictly by the planet's dignity (sign placement).

The Dignities map to three states:
1. Jagrat (Awake): The planet is in its Exaltation, Moolatrikona, or Own sign. 
   - Yields 100% active and aware results.
2. Svapna (Dreaming): The planet is in a Great Friend's, Friend's, or Neutral sign. 
   - Yields 50% of its results and operates in a semi-conscious, internal state.
3. Sushupti (Sleeping/Slumbering): The planet is in an Enemy's, Great Enemy's, or Debilitation sign. 
   - Yields 0% results, inactive, and unable to focus its energy.

Implementation and Use:
This Avastha shows the planet's level of awareness and ability to manifest its karmic results in the external world.
An "Awake" planet brings obvious, tangible results. A "Dreaming" planet brings internal or half-manifested results.
A "Sleeping" planet's results are completely muffled and inactive.
"""

def get_jagrat_avastha(dignity: str) -> dict:
    """
    Calculates the Jagrat Avastha for a given planet based on its dignity.
    
    Args:
        dignity (str): The final dignity string of the planet (e.g., 'Exalted', "Friend's Sign").
                       Typically obtained from jyotish.relationships.get_dignity().
                       
    Returns:
        dict: A dictionary containing the 'state' (Sanskrit and English) and its 'alertness' (multiplier).
    """
    # Awake conditions
    if dignity in ["Exalted", "Moolatrikona", "Own Sign"]:
        return {"state": "Jagrat (Awake)", "alertness": 1.00, "condition": f"in {dignity}"}
        
    # Sleeping conditions
    elif dignity in ["Debilitated", "Enemy's Sign", "Great Enemy's Sign"]:
        return {"state": "Sushupti (Sleeping/Slumbering)", "alertness": 0.00, "condition": f"in {dignity}"}
        
    # Dreaming conditions (Neutral, Friend, Great Friend)
    else:
        return {"state": "Svapna (Dreaming)", "alertness": 0.50, "condition": f"in {dignity}"}
