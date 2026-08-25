import json

with open("shiva_chart.json") as f:
    chart = json.load(f)

print(type(chart["vargas"]["D1"]))
if isinstance(chart["vargas"]["D1"], dict):
    print(list(chart["vargas"]["D1"].keys()))
elif isinstance(chart["vargas"]["D1"], list):
    if len(chart["vargas"]["D1"]) > 0:
        print(type(chart["vargas"]["D1"][0]))
        if isinstance(chart["vargas"]["D1"][0], dict):
            print(list(chart["vargas"]["D1"][0].keys()))
