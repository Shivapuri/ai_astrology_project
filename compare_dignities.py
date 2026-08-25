import json

with open("shiva_chart.json") as f:
    chart = json.load(f)

vargas = ['D1', 'D2', 'D3', 'D4', 'D7', 'D9', 'D10', 'D12', 'D16', 'D20', 'D24', 'D27', 'D30', 'D40', 'D45', 'D60']
planets = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']

# User screenshot data for comparison (from the image)
# Format: { varga_num: [Su, Mo, Ma, Me, Ju, Ve, Sa] }
kala_data = {
    1:  ['GF', 'F',  'N',  'F',  'OH', 'MT', 'N'],
    2:  ['N',  'GF', 'GF', 'GF', 'OH', 'MT', 'N'],
    3:  ['GF', 'E',  'F',  'N',  'GF', 'MT', 'N'],
    4:  ['N',  'GF', 'N',  'N',  'OH', 'MT', 'MT'],
    7:  ['E',  'OH', 'N',  'F',  'OH', 'OH', 'N'],
    9:  ['GF', 'E',  'N',  'DB', 'GF', 'F',  'N'],
    10: ['GE', 'GF', 'EX', 'F',  'GF', 'F',  'N'],
    12: ['E',  'E',  'DB', 'GF', 'N',  'F',  'MT'],
    16: ['E',  'OH', 'F',  'GF', 'EX', 'OH', 'F'],
    20: ['GE', 'F',  'EX', 'OH', 'N',  'GF', 'GF'],
    24: ['DB', 'F',  'MT', 'GF', 'EX', 'OH', 'MT'],
    27: ['E',  'GF', 'DB', 'E',  'N',  'GF', 'GE'],
    30: ['N',  'F',  'GF', 'E',  'N',  'GE', 'N'],
    40: ['GF', 'GF', 'N',  'GF', 'GF', 'N',  'N'],
    45: ['GE', 'MT', 'MT', 'E',  'N',  'DB', 'N'],
    60: ['GE', 'E',  'F',  'OH', 'N',  'OH', 'DB']
}

def map_dignity(dignity_str):
    if not dignity_str:
        return '?'
    d = dignity_str.lower()
    if 'exalt' in d: return 'EX'
    if 'debilitat' in d: return 'DB'
    if 'mool' in d or 'mul' in d: return 'MT'
    if 'own' in d: return 'OH'
    if 'great friend' in d: return 'GF'
    if 'great enemy' in d: return 'GE'
    if 'friend' in d and 'great' not in d: return 'F'
    if 'enemy' in d and 'great' not in d: return 'E'
    if 'neutral' in d: return 'N'
    return d

astra_data = {}
for v in vargas:
    v_num = int(v[1:])
    astra_data[v_num] = []
    grahas = chart['vargas'][v].get('grahas', {})
    for p in planets:
        if p in grahas:
            dig_str = grahas[p].get('dignity_breakdown', {}).get('final_dignity', 'Unknown')
            # Some vargas might not have final_dignity calculation if we haven't implemented it for all
            # Wait, dignity_breakdown might not exist.
            if 'dignity_breakdown' not in grahas[p]:
                # Let's try to find it somewhere else or maybe it's not calculated
                astra_data[v_num].append('?')
            else:
                astra_data[v_num].append(map_dignity(dig_str))
        else:
            astra_data[v_num].append('?')

print(f"{'Varga':<5} | {'Planet':<6} | {'Kala':<4} | {'Astra':<4} | Match?")
print("-" * 35)

matches = 0
total = 0

for v_num in sorted(kala_data.keys()):
    kala_row = kala_data[v_num]
    astra_row = astra_data.get(v_num, ['?']*7)
    for i, p in enumerate(planets):
        k = kala_row[i]
        a = astra_row[i]
        match = "YES" if k == a else "NO"
        if k == a:
            matches += 1
        total += 1
        print(f"D{v_num:<4} | {p:<6} | {k:<4} | {a:<4} | {match}")

print(f"\nTotal Matches: {matches} / {total} ({matches/total*100:.1f}%)")
