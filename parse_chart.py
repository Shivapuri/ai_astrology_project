import json

with open("shiva_chart.json") as f:
    chart = json.load(f)

# Print keys to understand structure
print(list(chart.keys()))
if "vargas" in chart:
    print(list(chart["vargas"].keys()))
    if "D1" in chart["vargas"]:
        print(chart["vargas"]["D1"]["Sun"])

