import re

with open("jyotish/avasthas/quantitative.py", "r") as f:
    content = f.read()

new_logic = """
    # Calculate Base Strengths
    # By default in Kala: Base = Shadbala (in Virupas) * Jagradadi * Baladi
    # This evaluates dynamically per Varga, as Jagrat/Bala change based on Varga Dignity and Varga Degree.
    
    bases = {}
    for p in planets:
        g = grahas_data[p]
        unmultiplied = shadbala_data[p]['Total_Virupas']
        
        jagrat = g['avasthas']['jagrat']['alertness']
        bala = g['avasthas']['bala']['strength']
        
        bases[p] = round(unmultiplied * jagrat * bala, 1)
"""

start_idx = content.find("    # Calculate Base Strengths")
end_idx = content.find("    for p_give in planets:")

if start_idx != -1 and end_idx != -1:
    content = content[:start_idx] + new_logic + content[end_idx:]
    with open("jyotish/avasthas/quantitative.py", "w") as f:
        f.write(content)
    print("Cleaned quantitative.py - Hardcoding removed")
else:
    print("Could not find block")
