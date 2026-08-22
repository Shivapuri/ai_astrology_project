import json
import os
import shutil
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

BACKUP_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "database", "backups")
DOCUMENTS_MIRROR = os.path.expanduser("~/Documents/Aries/Charts/Charts.jsonl")

def get_backup_dir(filepath: str) -> str:
    parent = os.path.dirname(filepath)
    b_dir = os.path.join(parent, "backups")
    os.makedirs(b_dir, exist_ok=True)
    return b_dir

def create_backup(filepath: str) -> Optional[str]:
    """Creates a timestamped backup of the charts file before modification."""
    if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
        return None
    try:
        b_dir = get_backup_dir(filepath)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(b_dir, f"Charts_{timestamp}.jsonl")
        shutil.copy2(filepath, backup_path)
        return backup_path
    except Exception as e:
        print(f"[native_manager] Backup warning: {e}")
        return None

def recover_from_backups_or_mirror(filepath: str) -> List[Dict[str, Any]]:
    """Self-heals and recovers data from recent backups or Documents mirror if main file is lost/empty."""
    recovered = []
    
    # 1. Check backup directory
    b_dir = get_backup_dir(filepath)
    if os.path.exists(b_dir):
        backup_files = sorted(
            [os.path.join(b_dir, f) for f in os.listdir(b_dir) if f.endswith(".jsonl") and os.path.getsize(os.path.join(b_dir, f)) > 0],
            key=os.path.getmtime,
            reverse=True
        )
        if backup_files:
            latest_backup = backup_files[0]
            print(f"[native_manager] Recovering from latest backup: {latest_backup}")
            recovered = _read_jsonl(latest_backup)
            if recovered:
                shutil.copy2(latest_backup, filepath)
                return recovered

    # 2. Check external mirror in Documents
    if os.path.exists(DOCUMENTS_MIRROR) and os.path.getsize(DOCUMENTS_MIRROR) > 0:
        print(f"[native_manager] Recovering from mirror: {DOCUMENTS_MIRROR}")
        recovered = _read_jsonl(DOCUMENTS_MIRROR)
        if recovered:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            shutil.copy2(DOCUMENTS_MIRROR, filepath)
            return recovered

    return recovered

def _read_jsonl(filepath: str) -> List[Dict[str, Any]]:
    natives = []
    if not os.path.exists(filepath):
        return natives
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line_str = line.strip()
            if line_str:
                try:
                    natives.append(json.loads(line_str))
                except json.JSONDecodeError:
                    continue
    return natives

def load_natives(filepath: str) -> List[Dict[str, Any]]:
    """Loads all natives with automatic self-healing and recovery."""
    natives = _read_jsonl(filepath)
    if not natives:
        # File is missing or empty, attempt self-healing recovery
        recovered = recover_from_backups_or_mirror(filepath)
        if recovered:
            return recovered
    return natives

def get_native_by_id(filepath: str, native_id: str) -> Optional[Dict[str, Any]]:
    natives = load_natives(filepath)
    for n in natives:
        if n.get("id") == native_id:
            return n
    return None

def atomic_write_natives(filepath: str, natives: List[Dict[str, Any]], allow_empty: bool = False) -> bool:
    """
    Safely and atomically writes the list of natives to disk.
    - Prevents accidental wipeouts (refuses empty writes unless explicitly permitted).
    - Creates automatic timestamped backups.
    - Uses temporary file + atomic replacement (os.replace).
    - Syncs to external Documents mirror.
    """
    if not natives and not allow_empty:
        # Safety guard: refuse to overwrite with empty data
        print("[native_manager] Refusing to overwrite charts with empty list.")
        return False

    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    # 1. Create backup of existing file if it has data
    create_backup(filepath)

    # 2. Write to temp file
    temp_path = f"{filepath}.tmp"
    with open(temp_path, 'w', encoding='utf-8') as f:
        for n in natives:
            f.write(json.dumps(n, ensure_ascii=False) + "\n")
        f.flush()
        os.fsync(f.fileno())

    # 3. Atomic replace
    os.replace(temp_path, filepath)

    # 4. Mirror to external Documents folder if accessible
    try:
        if os.path.exists(os.path.dirname(DOCUMENTS_MIRROR)):
            shutil.copy2(filepath, DOCUMENTS_MIRROR)
    except Exception as e:
        print(f"[native_manager] Mirror sync warning: {e}")

    return True

def save_native(filepath: str, name: str, date: str, time: str, lat: float, lon: float, tz: str, place: str = "Custom", country: str = "") -> Dict[str, Any]:
    """Adds a new native with atomic safety."""
    natives = load_natives(filepath)
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
        "place": place,
        "country": country,
        "lat": float(lat),
        "lon": float(lon),
        "alt": 0.0,
        "notes": "",
        "modified_at": datetime.now().isoformat()
    }
    
    natives.append(new_native)
    atomic_write_natives(filepath, natives)
    return new_native

def update_native(filepath: str, native_id: str, updated_fields: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Updates an existing native by ID with atomic safety."""
    natives = load_natives(filepath)
    updated_native = None
    for i, n in enumerate(natives):
        if n.get("id") == native_id:
            for k, v in updated_fields.items():
                if k in ['lat', 'lon']:
                    n[k] = float(v)
                else:
                    n[k] = v
            n['modified_at'] = datetime.now().isoformat()
            natives[i] = n
            updated_native = n
            break

    if updated_native:
        atomic_write_natives(filepath, natives)
        return updated_native
    return None

def delete_native(filepath: str, native_id: str) -> bool:
    """Deletes a native by ID safely with atomic backup."""
    natives = load_natives(filepath)
    filtered = [n for n in natives if n.get("id") != native_id]
    if len(filtered) < len(natives):
        return atomic_write_natives(filepath, filtered, allow_empty=True)
    return False
