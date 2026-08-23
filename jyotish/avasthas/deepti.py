"""
Deeptadi Avasthas (Internal Mental States / Moods)
==================================================
This module calculates the Deeptadi Avastha (mood) of a planet.

Determined by the planet's specific placement and calculated using its 
Compound Friendship (Panchadha Maitri) and physical afflictions.

The states (priority order typically handles physical conditions first):
1. Sakta (Powerful): Retrograde.
2. Mushita / Kopa (Angry): Combust.
3. Vikala (Mutilated / Agitated): Conjoined with a natural malefic.
4. Deepta (Radiant): Exalted.
5. Svastha (Confident): In Own sign.
6. Mudita (Rejoicing): In Great Friend's sign.
7. Shanta (Serene): In Friend's sign.
8. Dina (Scarce / Depressed): In Neutral's sign.
9. Dukhita (Miserable): In Enemy's sign.
10. Khala (Cruel): In Great Enemy's sign.
11. Bhita (Alarmed): Debilitated.
"""

def get_deeptadi_avastha(dignity: str, is_retrograde: bool, is_combust: bool, is_conjunct_malefic: bool) -> dict:
    """
    Calculates the Deeptadi Avastha for a given planet based on its dignity and physical state.
    
    Args:
        dignity (str): The final dignity string (e.g., 'Exalted', "Great Friend's Sign").
        is_retrograde (bool): True if the planet is retrograde.
        is_combust (bool): True if the planet is combust (too close to the Sun).
        is_conjunct_malefic (bool): True if conjoined with a natural malefic (Sun, Mars, Saturn, Rahu, Ketu) in the same sign.
                       
    Returns:
        dict: A dictionary containing the 'state' (Sanskrit and English) and condition that triggered it.
    """
    # Physical/Astronomical states take precedence in mood
    if is_retrograde:
        return {"state": "Sakta (Powerful / Driven)", "condition": "Retrograde"}
    
    if is_combust:
        return {"state": "Kopa / Mushita (Angry / Robbed)", "condition": "Combust"}
        
    if is_conjunct_malefic:
        return {"state": "Vikala (Mutilated / Agitated)", "condition": "Conjunct Malefic"}
        
    # Dignity-based states (Compound Friendship)
    if dignity == "Exalted":
        return {"state": "Deepta (Radiant)", "condition": "Exalted"}
    elif dignity == "Own Sign":
        return {"state": "Svastha (Confident)", "condition": "Own Sign"}
    elif dignity == "Great Friend's Sign":
        return {"state": "Mudita (Rejoicing)", "condition": "Great Friend's Sign"}
    elif dignity == "Friend's Sign":
        return {"state": "Shanta (Serene)", "condition": "Friend's Sign"}
    elif dignity == "Neutral's Sign":
        return {"state": "Dina (Scarce / Depressed)", "condition": "Neutral's Sign"}
    elif dignity == "Enemy's Sign":
        return {"state": "Dukhita (Miserable)", "condition": "Enemy's Sign"}
    elif dignity == "Great Enemy's Sign":
        return {"state": "Khala (Cruel)", "condition": "Great Enemy's Sign"}
    elif dignity == "Debilitated":
        return {"state": "Bhita (Alarmed / Fearful)", "condition": "Debilitated"}
        
    return {"state": "Unknown", "condition": dignity}
