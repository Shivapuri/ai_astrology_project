import re

with open("jyotish/generate_jyotish.py", "r") as f:
    content = f.read()

# We need to change the single `avastha_matrix` into a dictionary of matrices per varga
old_logic = """
    # 6. Quantitative Lajjitadi Avasthas
    from jyotish.avasthas.quantitative import calculate_avastha_matrix
    avastha_results = calculate_avastha_matrix(vargas_data["D1"]["grahas"], shadbala_data, vargas_data["D1"]["grahas"])
    
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

new_logic = """
    # 6. Quantitative Lajjitadi Avasthas
    from jyotish.avasthas.quantitative import calculate_avastha_matrix
    
    avastha_matrices = {}
    planets_list = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    
    for v_key in vargas_data.keys():
        avastha_results = calculate_avastha_matrix(vargas_data[v_key]["grahas"], shadbala_data, vargas_data["D1"]["grahas"])
        v_matrix = {}
        for p_receive in planets_list:
            v_matrix[p_receive] = {}
            for p_give in planets_list:
                data = avastha_results['matrix'][p_give][p_receive]
                
                if p_give == p_receive:
                    v_matrix[p_receive][p_give] = {
                        "top": None,
                        "bottom": f"{data['total']:.1f}",
                        "color": "black",
                        "tooltip": f"{p_receive} Base Starting Strength."
                    }
                    continue
                    
                pull = data['pull']
                if pull <= 0.001:
                    v_matrix[p_receive][p_give] = None
                    continue
                    
                sign_mult = data['sign_mult']
                total = data['total']
                
                color = "blue"
                if sign_mult > 0: color = "green"
                if sign_mult < 0: color = "red"
                
                if color == "green":
                    display_top = f"{pull:.1f}"
                    tooltip = f"{p_give} Delights (Mudita) {p_receive}. Adds {pull:.1f} points."
                elif color == "red":
                    display_top = f"{pull:.1f}"
                    tooltip = f"{p_give} Starves/Agitates {p_receive}. Subtracts {pull:.1f} points."
                else: # blue
                    display_top = f"{pull:.1f}"
                    tooltip = f"{p_give} influence on {p_receive} is neutralized. Adds 0."
                    
                bottom_str = f"{total:.1f}"
                if color != "blue":
                    bottom_str = f"+{total:.1f}" if total > avastha_results['bases'][p_receive] else f"{total:.1f}"
                    
                v_matrix[p_receive][p_give] = {
                    "top": display_top,
                    "bottom": bottom_str,
                    "color": color,
                    "tooltip": tooltip
                }
        avastha_matrices[v_key] = v_matrix
"""
content = content.replace(old_logic, new_logic)

content = content.replace('"avastha_matrix": avastha_matrix,', '"avastha_matrix": avastha_matrices,')

with open("jyotish/generate_jyotish.py", "w") as f:
    f.write(content)
print("Fixed generate_jyotish to output matrices for all vargas")
