import re

with open("jyotish/generate_jyotish.py", "r") as f:
    content = f.read()

old_call = 'avastha_results = calculate_avastha_matrix(vargas_data["D1"]["grahas"], shadbala_data)'
new_call = 'avastha_results = calculate_avastha_matrix(vargas_data["D1"]["grahas"], shadbala_data, vargas_data["D1"]["grahas"])'
content = content.replace(old_call, new_call)

with open("jyotish/generate_jyotish.py", "w") as f:
    f.write(content)
print("Fixed generate_jyotish")
