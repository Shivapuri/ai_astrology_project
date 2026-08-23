"""
Lajjitadi Avasthas (Social/Relationship States)
===============================================
This module calculates the Lajjitadi Avasthas (Shame, Pride, Starvation, Thirst, Delight, Agitation).

These states are highly interactive and depend on conjunctions, Rasi aspects, and Natural Friendships.

States (can have multiple active):
- Lajjita (Ashamed): In 5th house conjoined with Rahu, Ketu, Sun, Saturn, or Mars.
- Garvita (Proud): Exaltation or Moolatrikona sign.
- Kshudhita (Starved): In natural enemy's sign, AND (conjunct/aspected by enemy OR conjunct/aspected by Saturn). Jupiter is never an enemy.
- Trushita (Thirsty): In a watery sign (Cancer, Scorpio, Pisces), aspected by natural enemy, NOT aspected by natural benefic.
- Mudita (Delighted): In natural friend's sign, AND (conjunct/aspected by friend OR conjunct/aspected by Jupiter). Saturn is never a friend.
- Kshobhita (Agitated): Conjunct Sun, aspected by natural enemies or malefics.
"""

def get_lajjitadi_avasthas(planet: str, sign: str, house_num: int, 
                           natural_dignity: str, 
                           conjunct_planets: list[str], 
                           aspecting_planets: list[str],
                           natural_friends: list[str],
                           natural_enemies: list[str]) -> list[str]:
    """
    Calculates the active Lajjitadi Avasthas for a planet.
    A planet can experience multiple social states at once.
    
    Args:
        planet: The planet name (e.g. "Sun").
        sign: The sign it is in.
        house_num: The house number (1-12) it occupies.
        natural_dignity: Its natural dignity (Exalted, Moolatrikona, etc.).
        conjunct_planets: List of planets in the same sign.
        aspecting_planets: List of planets aspecting this sign (via Rasi Drishti).
        natural_friends: List of planet's natural friends.
        natural_enemies: List of planet's natural enemies.
        
    Returns:
        list[str]: A list of active Lajjitadi Avasthas (e.g., ["Mudita (Delighted)", "Garvita (Proud)"]).
    """
    states = []
    
    all_influences = conjunct_planets + aspecting_planets
    natural_benefics = ["Jupiter", "Venus", "Mercury", "Moon"] # Broadly speaking, though Moon/Mercury are conditional
    
    # 1. Garvita (Proud): Exaltation or Moolatrikona
    if natural_dignity in ["Exalted", "Moolatrikona"]:
        states.append("Garvita (Proud)")
        
    # 2. Lajjita (Ashamed): In 5th house with malefics
    malefics = ["Sun", "Mars", "Saturn", "Rahu", "Ketu"]
    has_malefic_conjunct = any(p in malefics for p in conjunct_planets)
    if house_num == 5 and has_malefic_conjunct:
        states.append("Lajjita (Ashamed)")
        
    # 3. Kshudhita (Starved)
    # Rule: In enemy sign AND (influenced by enemy OR influenced by Saturn)
    # Jupiter is never considered an enemy here.
    enemies_no_jup = [e for e in natural_enemies if e != "Jupiter"]
    in_enemy_sign = natural_dignity == "Enemy's Sign"
    influenced_by_enemy = any(p in enemies_no_jup for p in all_influences)
    influenced_by_saturn = "Saturn" in all_influences
    
    if in_enemy_sign and (influenced_by_enemy or influenced_by_saturn):
        states.append("Kshudhita (Starved)")
        
    # 4. Trushita (Thirsty)
    # Rule: In water sign, aspected by enemy, NOT aspected by benefic.
    water_signs = ["Cancer", "Scorpio", "Pisces"]
    if sign in water_signs:
        aspected_by_enemy = any(p in natural_enemies for p in aspecting_planets)
        aspected_by_benefic = any(p in natural_benefics for p in aspecting_planets)
        if aspected_by_enemy and not aspected_by_benefic:
            states.append("Trushita (Thirsty)")
            
    # 5. Mudita (Delighted)
    # Rule: In friend sign AND (influenced by friend OR influenced by Jupiter)
    # Saturn is never considered a friend here.
    friends_no_sat = [f for f in natural_friends if f != "Saturn"]
    in_friend_sign = natural_dignity == "Friend's Sign" or natural_dignity == "Great Friend's Sign"
    influenced_by_friend = any(p in friends_no_sat for p in all_influences)
    influenced_by_jupiter = "Jupiter" in all_influences
    
    if in_friend_sign and (influenced_by_friend or influenced_by_jupiter):
        states.append("Mudita (Delighted)")
        
    # 6. Kshobhita (Agitated)
    # Rule: Conjunct Sun AND aspected by malefic or enemy.
    if "Sun" in conjunct_planets:
        aspected_by_enemy_or_malefic = any(p in natural_enemies or p in malefics for p in aspecting_planets)
        if aspected_by_enemy_or_malefic:
            states.append("Kshobhita (Agitated)")
            
    if not states:
        states.append("Neutral (None)")
        
    return states
