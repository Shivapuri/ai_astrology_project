import swisseph as swe
jd = swe.julday(1983, 11, 10, 21.333333333333332)
cusps_p, ascmc = swe.houses(jd, 52.202961, 8.0448, b'P')
cusps_c, _ = swe.houses(jd, 52.202961, 8.0448, b'C')
cusps_r, _ = swe.houses(jd, 52.202961, 8.0448, b'R')
cusps_k, _ = swe.houses(jd, 52.202961, 8.0448, b'K')

signs = ["Ar", "Ta", "Ge", "Cn", "Le", "Vi", "Li", "Sc", "Sg", "Cp", "Aq", "Pi"]
def to_str(deg):
    return signs[int(deg/30)]

print("Placidus: ", [to_str(c) for c in cusps_p])
print("Campanus: ", [to_str(c) for c in cusps_c])
print("Regiomontanus: ", [to_str(c) for c in cusps_r])
print("Koch: ", [to_str(c) for c in cusps_k])
