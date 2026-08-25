import json
with open("shiva_chart.json") as f:
    chart = json.load(f)

print(chart["vargas"]["D1"]["grahas"]["Jupiter"])
