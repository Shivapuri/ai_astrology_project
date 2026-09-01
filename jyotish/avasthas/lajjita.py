"""
Lajjitadi Avasthas (Social/Relationship States)
===============================================
This module calculates the Lajjitadi Avasthas (Shame, Pride, Starvation, Thirst, Delight, Agitation).

These states are highly interactive and depend on conjunctions, Graha aspects, and Natural Friendships.

States (can have multiple active):
- Lajjita (Ashamed): (5th house AND conjunct Sun, Mars, or Saturn) OR (Conjunct Rahu/Ketu AND conjunct Sun, Mars, or Saturn in any house).
- Garvita (Proud): Exaltation or Moolatrikona sign.
- Kshudhita (Starved): In natural enemy's sign OR conjunct/aspected by enemy OR conjunct Saturn. 
  (Note: aspected by cruel enemy causes Kshobhita instead of Kshudhita according to EW).
- Trushita (Thirsty): In a watery sign (Cancer, Scorpio, Pisces) AND aspected by natural enemy AND NOT aspected by natural benefic.
- Mudita (Delighted): In natural friend's sign OR conjunct/aspected by friend OR conjunct Jupiter. Saturn is never a friend.
- Kshobhita (Agitated): Conjunct Sun OR aspected by enemy cruel planet (Sun, Mars, Saturn, waning Moon).
"""

def get_lajjitadi_avasthas(planet: str, sign: str, house_num: int, 
                           natural_dignity: str, 
                           conjunct_planets: list[str], 
                           aspecting_planets: list[str],
                           natural_friends: list[str],
                           natural_enemies: list[str],
                           is_waning_moon_as_enemy: bool = False) -> list[dict]:
    """
    Calculates the active Lajjitadi Avasthas for a planet based on Graha Drishti.
    A planet can experience multiple social states at once.
    
    Args:
        planet: The planet name (e.g. "Sun").
        sign: The sign it is in.
        house_num: The house number (1-12) it occupies.
        natural_dignity: Its natural dignity (Exalted, Moolatrikona, etc.).
        conjunct_planets: List of planets in the same sign.
        aspecting_planets: List of planets aspecting this planet via Graha Drishti.
        natural_friends: List of planet's natural friends.
        natural_enemies: List of planet's natural enemies.
        is_waning_moon_as_enemy: True if the Moon is waning AND an enemy.
        
    Returns:
        list[dict]: A list of active Lajjitadi Avasthas (e.g., [{"state": "Mudita (Delighted)", "condition": "..."}]).
    """
    states = []
    
    natural_benefics = ["Jupiter", "Venus", "Mercury", "Moon"] # Broadly speaking
    cruel_planets = ["Sun", "Mars", "Saturn"]
    if is_waning_moon_as_enemy:
        cruel_planets.append("Moon")
    pure_malefics = ["Sun", "Mars", "Saturn"]
        
    # 1. Garvita (Proud): Exaltation or Moolatrikona
    if natural_dignity in ["Exalted", "Moolatrikona"]:
        states.append({"state": "Garvita (Proud)", "condition": f"In {natural_dignity} ({sign})"})
        
    # 2. Lajjita (Ashamed)
    # Rule A: 5th house AND conjunct Sun, Mars, or Saturn
    # Rule B: Conjunct Rahu/Ketu AND conjunct Sun, Mars, or Saturn in any house
    conjunct_pure_malefics = [p for p in conjunct_planets if p in pure_malefics]
    has_node = "Rahu" in conjunct_planets or "Ketu" in conjunct_planets
    
    if conjunct_pure_malefics:
        malefic_str = ", ".join(conjunct_pure_malefics)
        if house_num == 5:
            states.append({"state": "Lajjita (Ashamed)", "condition": f"In 5th House conjoined with {malefic_str}"})
        elif has_node:
            node_str = "Rahu" if "Rahu" in conjunct_planets else "Ketu"
            states.append({"state": "Lajjita (Ashamed)", "condition": f"Conjoined {node_str} and {malefic_str}"})
            
    # Helper definitions
    in_enemy_sign = natural_dignity in ["Enemy's Sign", "Great Enemy's Sign"]
    conjunct_enemies = [p for p in conjunct_planets if p in natural_enemies and p != "Jupiter"]
    aspecting_enemies = [p for p in aspecting_planets if p in natural_enemies and p != "Jupiter"]
    
    # 3. Kshobhita (Agitated)
    # Rule: Conjunct Sun OR aspected by an enemy that is a cruel planet.
    aspecting_enemy_cruel = [p for p in aspecting_enemies if p in cruel_planets]
    is_kshobhita = False
    kshobhita_reasons = []
    if "Sun" in conjunct_planets:
        kshobhita_reasons.append("conjoined Sun")
    if aspecting_enemy_cruel:
        kshobhita_reasons.append(f"aspected by cruel enemy {', '.join(aspecting_enemy_cruel)}")
        
    if kshobhita_reasons:
        is_kshobhita = True
        states.append({"state": "Kshobhita (Agitated)", "condition": " and ".join(kshobhita_reasons)})
        
    # 4. Kshudhita (Starved)
    # Rule: In enemy sign OR conjunct enemy OR aspected by enemy OR conjunct Saturn.
    # Caveat: Aspect from a cruel enemy causes Kshobhita instead. So we filter those out for Kshudhita.
    aspecting_enemy_non_cruel = [p for p in aspecting_enemies if p not in cruel_planets]
    
    is_starved = False
    starved_reasons = []
    if in_enemy_sign: starved_reasons.append(f"in Enemy sign ({sign})")
    if conjunct_enemies: starved_reasons.append(f"conjoined enemy {', '.join(conjunct_enemies)}")
    if aspecting_enemy_non_cruel: starved_reasons.append(f"aspected by enemy {', '.join(aspecting_enemy_non_cruel)}")
    if "Saturn" in conjunct_planets: starved_reasons.append("conjoined Saturn")
    
    if starved_reasons:
        states.append({"state": "Kshudhita (Starved)", "condition": ", ".join(starved_reasons)})
        
    # 5. Trushita (Thirsty)
    # Rule: In water sign AND aspected by enemy AND NO benefic aspect
    water_signs = ["Cancer", "Scorpio", "Pisces"]
    if sign in water_signs:
        aspected_by_benefic = any(p in natural_benefics for p in aspecting_planets)
        if aspecting_enemies and not aspected_by_benefic:
            enemy_str = ", ".join(aspecting_enemies)
            states.append({"state": "Trushita (Thirsty)", "condition": f"In Water sign ({sign}), aspected by {enemy_str}, lacking benefic aspect"})
            
    # 6. Mudita (Delighted)
    # Rule: In friend sign OR conjunct friend OR aspected by friend OR conjunct Jupiter.
    # Exclude Saturn as a friend. Sun conjunction causes Kshobhita (don't count for Mudita).
    friends_no_sat = [f for f in natural_friends if f != "Saturn"]
    in_friend_sign = natural_dignity in ["Friend's Sign", "Great Friend's Sign"]
    conjunct_friends = [p for p in conjunct_planets if p in friends_no_sat]
    aspecting_friends = [p for p in aspecting_planets if p in friends_no_sat]
    
    mudita_reasons = []
    if in_friend_sign: mudita_reasons.append(f"in Friend's sign ({sign})")
    if conjunct_friends: mudita_reasons.append(f"conjoined friend {', '.join(conjunct_friends)}")
    if aspecting_friends: mudita_reasons.append(f"aspected by friend {', '.join(aspecting_friends)}")
    if "Jupiter" in conjunct_planets: mudita_reasons.append("conjoined Jupiter")
    
    if mudita_reasons:
        states.append({"state": "Mudita (Delighted)", "condition": ", ".join(mudita_reasons)})
            
    if not states:
        states.append({"state": "Neutral (None)", "condition": "No special social conditions met"})
        
    return states
