import json

with open("shiva_chart.json") as f:
    chart = json.load(f)

grahas = chart["vargas"]["D1"]["grahas"]
print(type(grahas))
if isinstance(grahas, dict):
    print(list(grahas.keys()))
    if "Sun" in grahas:
        print(grahas["Sun"])
