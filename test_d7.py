import sys, json
sys.path.insert(0, '/Users/hajnaljanos/PycharmProjects/astra')
from jyotish.generate_jyotish import generate_kala_chart
res = generate_kala_chart("Shivapuri", 1983, 11, 10, 22, 20, 52.2, 8.0, 1.0)
sb = res['shadbala']

print("--- SHADBALA ---")
for p in ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']:
    print(f"{p}: Total_Virupas = {sb[p]['Total_Virupas']}, Ishta = {sb[p]['Ishta_Phala']}, Kashta = {sb[p]['Kashta_Phala']}")

print("\n--- D1 AVASTHAS ---")
d1 = res['vargas']['D1']['grahas']
for p in ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']:
    jagrat = d1[p]['avasthas']['jagrat']['alertness']
    bala = d1[p]['avasthas']['bala']['strength']
    print(f"{p}: Jagrat = {jagrat}, Bala = {bala}, Sign = {d1[p]['sign']}, Dignity = {d1[p]['dignity_breakdown']['natural_dignity']}")

print("\n--- D7 AVASTHAS ---")
d7 = res['vargas']['D7']['grahas']
for p in ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']:
    jagrat = d7[p]['avasthas']['jagrat']['alertness']
    bala = d7[p]['avasthas']['bala']['strength']
    print(f"{p}: Jagrat = {jagrat}, Bala = {bala}, Sign = {d7[p]['sign']}, Dignity = {d7[p]['dignity_breakdown']['natural_dignity']}")

