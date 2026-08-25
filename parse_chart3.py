import json

with open("shiva_chart.json") as f:
    chart = json.load(f)

for graha in chart["vargas"]["D1"]["grahas"]:
    print(f"{graha.get('name')}: {graha.get('dignity')} in {graha.get('sign')} (Lord: {graha.get('sign_lord')})")
