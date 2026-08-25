import sys, json
sys.path.insert(0, '/Users/hajnaljanos/PycharmProjects/astra')
from jyotish.generate_jyotish import generate_kala_chart
from jyotish.avasthas.quantitative import calculate_avastha_matrix

res = generate_kala_chart("Shivapuri", 1983, 11, 10, 22, 20, 52.2, 8.0, 1.0)
d1_grahas = res['vargas']['D1']['grahas']
sb = res['shadbala']

matrix_res = calculate_avastha_matrix(d1_grahas, sb)
matrix = matrix_res['matrix']
print("D1 Moon -> Sun: Top", matrix['Moon']['Sun']['pull'])
