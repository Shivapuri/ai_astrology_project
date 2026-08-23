import json
with open("taittiriya_nakshatra_database.json") as f:
    data = json.load(f)
    for v in data[0].get("verses"):
        if v.get('verse_num') in [14, 15, 16]:
            print(f"Verse {v.get('verse_num')}: {v.get('translit')}")
