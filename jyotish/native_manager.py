import json
import os
import uuid

def load_natives(filepath):
    natives = []
    if not os.path.exists(filepath):
        return natives
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                try:
                    natives.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    continue
    return natives

def get_native_by_id(filepath, native_id):
    natives = load_natives(filepath)
    for n in natives:
        if n.get("id") == native_id:
            return n
    return None

def save_native(filepath, name, date, time, lat, lon, tz):
    new_native = {
        "v": 1,
        "id": str(uuid.uuid4()),
        "name": name,
        "type": "radix",
        "male": True,
        "date": date,
        "time": time,
        "tz": tz,
        "tz_name": "",
        "tzid": "",
        "tzauto": False,
        "cal": "gregorian",
        "zt": "zone",
        "bc": False,
        "dst": False,
        "place": "Custom",
        "country": "",
        "lat": float(lat),
        "lon": float(lon),
        "alt": 0.0,
        "notes": "",
        "modified_at": ""
    }
    
    with open(filepath, 'a', encoding='utf-8') as f:
        f.write(json.dumps(new_native) + "\n")
    return new_native
