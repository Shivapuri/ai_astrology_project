import re

with open("jyotish/avasthas/quantitative.py", "r") as f:
    content = f.read()

new_logic = """
            # Fetch relationships
            from jyotish.relationships import get_natural_relationship
            rel = get_natural_relationship(p_recv, p_give) # How does recv view giving?
            
            # Default to 0
            sign_mult = 0
            
            # Mudita (Delighted): Planet is aspected/conjoined by a Great Friend, Friend, or Jupiter. Adds points.
            if rel in ["Friend", "Great Friend"] or p_give == "Jupiter":
                sign_mult = 1
                
            # Kshudhita (Starved): Planet is aspected/conjoined by an Enemy, or Saturn. Subtracts points.
            # Kshobhita (Agitated): Planet is aspected/conjoined by Sun, Mars, or Saturn. Subtracts points.
            # Note: Kshudhita/Kshobhita override Mudita (if Sun is a friend, it still Agitates and subtracts).
            if rel in ["Enemy", "Great Enemy"] or p_give in ["Sun", "Mars", "Saturn"]:
                sign_mult = -1
"""

start_idx = content.find("            # Fetch relationships")
end_idx = content.find("            total = bases[p_recv] + (sign_mult * pull)")

if start_idx != -1 and end_idx != -1:
    content = content[:start_idx] + new_logic + content[end_idx:]
    with open("jyotish/avasthas/quantitative.py", "w") as f:
        f.write(content)
    print("Fixed quantitative.py signs")
else:
    print("Could not find block")
