import re

with open("jyotish/avasthas/quantitative.py", "r") as f:
    content = f.read()

# Change the signature to accept d1_grahas explicitly
old_sig = "def calculate_avastha_matrix(grahas_data, shadbala_data):"
new_sig = "def calculate_avastha_matrix(grahas_data, shadbala_data, d1_grahas=None):\n    if d1_grahas is None: d1_grahas = grahas_data"
content = content.replace(old_sig, new_sig)

# Change the aspect calculation to use d1_grahas
old_aspect = """
            l1, l2 = g_give['longitude'], g_recv['longitude']
            s1, s2 = g_give['sign'], g_recv['sign']
            lord1 = g_give['dignity_breakdown']['sign_lord']
            lord2 = g_recv['dignity_breakdown']['sign_lord']
"""
new_aspect = """
            # Use D1 longitudes for aspect calculation (Graha Drishti is always from Rasi chart)
            l1 = d1_grahas[p_give]['longitude']
            l2 = d1_grahas[p_recv]['longitude']
            # We still use the current varga's signs/lords for Parivartana rules?
            # Wait, Parivartana Yoga (Exchange) for aspects is based on D1 signs!
            s1 = d1_grahas[p_give]['sign']
            s2 = d1_grahas[p_recv]['sign']
            lord1 = d1_grahas[p_give]['dignity_breakdown']['sign_lord']
            lord2 = d1_grahas[p_recv]['dignity_breakdown']['sign_lord']
"""
content = content.replace(old_aspect, new_aspect)

with open("jyotish/avasthas/quantitative.py", "w") as f:
    f.write(content)
print("Fixed quantitative aspects")
