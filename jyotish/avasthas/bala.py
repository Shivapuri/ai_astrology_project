"""
Bala Avastha (Age / Vitality)
=============================
This module calculates the Bala Avastha (Age/Vitality state) of a planet.

How it is calculated:
The Bala Avastha divides a 30-degree sign into five equal parts of 6 degrees each. 
The state and strength depend on whether the planet is placed in an Odd sign or an Even sign.

Odd Signs (Masculine): Aries, Gemini, Leo, Libra, Sagittarius, Aquarius
Even Signs (Feminine): Taurus, Cancer, Virgo, Scorpio, Capricorn, Pisces

Degrees for Odd Signs:
- 0° to 6°: Bala (Infant) - Yields 1/4 strength (25%)
- 6° to 12°: Kumara (Youth) - Yields 1/2 strength (50%)
- 12° to 18°: Yuva (Adult/Prime) - Yields full strength (100%)
- 18° to 24°: Vriddha (Elderly) - Yields minimal strength (~10%)
- 24° to 30°: Mrita (Dead) - Yields 0 strength (0%)

Degrees for Even Signs (Reversed):
- 0° to 6°: Mrita (Dead) - Yields 0 strength (0%)
- 6° to 12°: Vriddha (Elderly) - Yields minimal strength (~10%)
- 12° to 18°: Yuva (Adult/Prime) - Yields full strength (100%)
- 18° to 24°: Kumara (Youth) - Yields 1/2 strength (50%)
- 24° to 30°: Bala (Infant) - Yields 1/4 strength (25%)

Implementation and Use:
This state determines the physical capacity and vitality of a planet to yield its karmic results.
For example, an "Infant" planet has the potential to grow but currently offers limited output (like a baby), 
while a "Dead" planet is completely devoid of energy to manifest its physical results.
This metric is used as a baseline modifier when evaluating a planet's strength to do work in a chart.
"""

ODD_SIGNS = {"Aries", "Gemini", "Leo", "Libra", "Sagittarius", "Aquarius"}
EVEN_SIGNS = {"Taurus", "Cancer", "Virgo", "Scorpio", "Capricorn", "Pisces"}

def get_bala_avastha(degree: float, sign_name: str) -> dict:
    """
    Calculates the Bala Avastha for a given planet's degree and sign.
    
    Args:
        degree (float): The degree of the planet within the sign (0.0 up to 30.0).
        sign_name (str): The name of the sign (e.g., 'Aries').
        
    Returns:
        dict: A dictionary containing the 'state' (Sanskrit and English) and its 'strength' (multiplier).
    """
    # Normalize degree to handle edge cases exactly at 30.0 (treated as end of the 5th segment)
    if degree >= 30.0:
        degree = 29.9999
        
    # Determine which of the 5 segments (0-4) the degree falls into
    segment = int(degree // 6)
    
    is_odd = sign_name in ODD_SIGNS
    
    if is_odd:
        # Odd sign logic
        if segment == 0:
            return {"state": "Bala (Infant)", "strength": 0.25, "condition": f"between 0° and 6° in an Odd sign ({sign_name})"}
        elif segment == 1:
            return {"state": "Kumara (Youth)", "strength": 0.50, "condition": f"between 6° and 12° in an Odd sign ({sign_name})"}
        elif segment == 2:
            return {"state": "Yuva (Adult/Prime)", "strength": 1.00, "condition": f"between 12° and 18° in an Odd sign ({sign_name})"}
        elif segment == 3:
            return {"state": "Vriddha (Elderly)", "strength": 0.10, "condition": f"between 18° and 24° in an Odd sign ({sign_name})"}
        else: # segment == 4
            return {"state": "Mrita (Dead)", "strength": 0.00, "condition": f"between 24° and 30° in an Odd sign ({sign_name})"}
    else:
        # Even sign logic (reversed)
        if segment == 0:
            return {"state": "Mrita (Dead)", "strength": 0.00, "condition": f"between 0° and 6° in an Even sign ({sign_name})"}
        elif segment == 1:
            return {"state": "Vriddha (Elderly)", "strength": 0.10, "condition": f"between 6° and 12° in an Even sign ({sign_name})"}
        elif segment == 2:
            return {"state": "Yuva (Adult/Prime)", "strength": 1.00, "condition": f"between 12° and 18° in an Even sign ({sign_name})"}
        elif segment == 3:
            return {"state": "Kumara (Youth)", "strength": 0.50, "condition": f"between 18° and 24° in an Even sign ({sign_name})"}
        else: # segment == 4
            return {"state": "Bala (Infant)", "strength": 0.25, "condition": f"between 24° and 30° in an Even sign ({sign_name})"}
