import re

with open("jyotish/generate_jyotish.py", "r") as f:
    content = f.read()

# We need to replace everything from:
# # --- DYNAMIC 4th-DEGREE ALGEBRAIC POLYNOMIAL FOR TRUE 3D BASE SCORES ---
# to
#         "lajjitadi_matrix": lajjitadi_matrix,
#         "avastha_matrix": avastha_matrix,

# Actually, let's find the indices.
start_idx = content.find("# --- DYNAMIC 4th-DEGREE ALGEBRAIC POLYNOMIAL FOR TRUE 3D BASE SCORES ---")
end_idx = content.find("vedic_context = {")

new_logic = """
    # 6. Quantitative Lajjitadi Avasthas
    from jyotish.avasthas.quantitative import calculate_avastha_matrix
    avastha_results = calculate_avastha_matrix(vargas_data["D1"]["grahas"], shadbala_data)
    
    avastha_matrix = {}
    planets_list = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    
    for p_receive in planets_list:
        avastha_matrix[p_receive] = {}
        for p_give in planets_list:
            data = avastha_results['matrix'][p_give][p_receive]
            
            if p_give == p_receive:
                avastha_matrix[p_receive][p_give] = {
                    "top": None,
                    "bottom": f"{data['total']:.1f}",
                    "color": "black",
                    "tooltip": f"{p_receive} Base Starting Strength."
                }
                continue
                
            pull = data['pull']
            if pull <= 0.001:
                avastha_matrix[p_receive][p_give] = None
                continue
                
            sign_mult = data['sign_mult']
            total = data['total']
            
            color = "blue"
            if sign_mult > 0: color = "green"
            if sign_mult < 0: color = "red"
            
            if color == "green":
                display_top = f"+{pull:.1f}"
                tooltip = f"{p_give} Delights (Mudita) {p_receive}. Adds {pull:.1f} points."
            elif color == "red":
                display_top = f"-{pull:.1f}"
                tooltip = f"{p_give} Starves/Agitates {p_receive}. Subtracts {pull:.1f} points."
            else: # blue
                display_top = f"{pull:.1f}"
                tooltip = f"{p_give} influence on {p_receive} is neutralized. Adds 0."
                
            bottom_str = f"{total:.1f}"
            if color != "blue":
                bottom_str = f"+{total:.1f}" if total > avastha_results['bases'][p_receive] else f"{total:.1f}"
                
            avastha_matrix[p_receive][p_give] = {
                "top": display_top,
                "bottom": bottom_str,
                "color": color,
                "tooltip": tooltip
            }
            
    """

if start_idx != -1 and end_idx != -1:
    new_content = content[:start_idx] + new_logic + content[end_idx:]
    
    # Also fix the duplicate lajjitadi_matrix key I accidentally added earlier
    new_content = new_content.replace('        "lajjitadi_matrix": lajjitadi_matrix,\n', '')
    
    with open("jyotish/generate_jyotish.py", "w") as f:
        f.write(new_content)
    print("Fixed generate_jyotish.py")
else:
    print("Could not find markers")
