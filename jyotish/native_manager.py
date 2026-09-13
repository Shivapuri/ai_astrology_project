import json
import os
import shutil
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
import time

BACKUP_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "database", "backups")
DOCUMENTS_MIRROR = os.path.expanduser("~/Documents/Aries/Charts/Charts.jsonl")

def _acquire_lock(filepath: str, timeout=5.0) -> bool:
    lockfile = f"{filepath}.lock"
    start = time.time()
    while time.time() - start < timeout:
        try:
            fd = os.open(lockfile, os.O_CREAT | os.O_EXCL | os.O_RDWR)
            os.close(fd)
            return True
        except FileExistsError:
            time.sleep(0.1)
    return False

def _release_lock(filepath: str):
    lockfile = f"{filepath}.lock"
    try:
        os.remove(lockfile)
    except FileNotFoundError:
        pass

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

def parse_date_to_parts(date_str: Any) -> tuple:
    """
    Parses any date format into (year, month, day).
    Supports:
      - Standard DD/MM/YYYY, DD.MM.YYYY, DD-MM-YYYY
      - ISO: YYYY-MM-DD, YYYY/MM/DD
      - Astronomical BCE: -YYYY-MM-DD, -YYYY/MM/DD, DD/MM/-YYYY, DD-MM--YYYY
      - Historical textual BCE: e.g. '28/08/3256 BCE'
    """
    if not date_str:
        return 2000, 1, 1
    
    s = str(date_str).strip()
    
    # Check textual BCE
    is_bce_text = False
    if 'bce' in s.lower() or 'bc' in s.lower():
        is_bce_text = True
        s = s.lower().replace('bce', '').replace('bc', '').strip()
        
    # 1. Slashes: DD/MM/YYYY, YYYY/MM/DD, DD/MM/-YYYY
    if '/' in s:
        parts = [p.strip() for p in s.split('/')]
        if len(parts) == 3:
            p0 = parts[0]
            # If p0 has 4 digits or magnitude > 31, it is YYYY/MM/DD
            if len(p0.lstrip('-')) == 4 or abs(int(float(p0))) > 31:
                year = int(p0)
                month = int(parts[1])
                day = int(parts[2])
            else:
                day = int(parts[0])
                month = int(parts[1])
                year = int(parts[2])
            if is_bce_text and year > 0:
                year = -(year - 1)  # 3256 BCE = -3255 astronomical
            return year, month, day

    # 2. Dots: DD.MM.YYYY
    if '.' in s:
        parts = [p.strip() for p in s.split('.')]
        if len(parts) == 3:
            p0 = parts[0]
            if len(p0.lstrip('-')) == 4 or abs(int(float(p0))) > 31:
                year = int(p0)
                month = int(parts[1])
                day = int(parts[2])
            else:
                day = int(parts[0])
                month = int(parts[1])
                year = int(parts[2])
            if is_bce_text and year > 0:
                year = -(year - 1)
            return year, month, day

    # 3. Dashes: YYYY-MM-DD, -YYYY-MM-DD, DD-MM-YYYY, DD-MM--YYYY
    if '-' in s:
        if s.startswith('-'):
            # e.g. -3255-08-28
            clean = s[1:]
            parts = [p.strip() for p in clean.split('-')]
            if len(parts) == 3:
                year = -int(parts[0])
                month = int(parts[1])
                day = int(parts[2])
                return year, month, day
        else:
            parts = [p.strip() for p in s.split('-')]
            if len(parts) == 3:
                p0 = parts[0]
                if len(p0) == 4 or int(float(p0)) > 31:
                    year = int(p0)
                    month = int(parts[1])
                    day = int(parts[2])
                else:
                    day = int(parts[0])
                    month = int(parts[1])
                    year = int(parts[2])
                if is_bce_text and year > 0:
                    year = -(year - 1)
                return year, month, day

    return 2000, 1, 1

def to_standard_date(date_str: Any) -> str:
    """
    Standardizes any date representation into canonical DD/MM/YYYY format.
    Preserves negative years for astronomical BCE dates: DD/MM/-YYYY.
    """
    if not date_str:
        return "01/01/2000"
    year, month, day = parse_date_to_parts(date_str)
    if year < 0:
        return f"{day:02d}/{month:02d}/{year}"
    else:
        return f"{day:02d}/{month:02d}/{year:04d}"

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
    """Loads all natives with automatic self-healing, recovery, and standard DD/MM/YYYY formatting."""
    natives = _read_jsonl(filepath)
    if not natives:
        # File is missing or empty, attempt self-healing recovery
        recovered = recover_from_backups_or_mirror(filepath)
        if recovered:
            natives = recovered
            
    for n in natives:
        if 'date' in n:
            n['date'] = to_standard_date(n['date'])
    return natives

def get_native_by_id(filepath: str, native_id: str) -> Optional[Dict[str, Any]]:
    natives = load_natives(filepath)
    # 1. Exact ID match
    for n in natives:
        if n.get("id") == native_id:
            return n
    
    # 2. Case-insensitive slug / name match (e.g. 'goebbels', 'shri-krishna', 'krishna')
    clean_target = str(native_id).lower().replace("-", " ").replace("_", " ").strip()
    for n in natives:
        n_name = n.get("name", "").lower().strip()
        n_id = str(n.get("id", "")).lower().strip()
        if n_name == clean_target or n_id == clean_target:
            return n
        # Also check substring / word matches (e.g. 'deep-narayan-mahaprabhuji' matches 'Bhagwan Sri Deep Narayan Mahaprabhuji')
        words = [w for w in n_name.replace("-", " ").split()]
        if clean_target in words or clean_target in n_name or clean_target == "".join(words):
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

def save_native(filepath: str, name: str, date: str, time: str, lat: float, lon: float, tz: str, place: str = "Custom", country: str = "", name_sound_value: int = 0, notes: str = "") -> Dict[str, Any]:
    """Adds a new native with atomic safety and standard DD/MM/YYYY date."""
    if not _acquire_lock(filepath):
        raise RuntimeError("Could not acquire lock to save native")
    try:
        natives = load_natives(filepath)
        std_date = to_standard_date(date)
        new_native = {
            "v": 1,
            "id": str(uuid.uuid4()),
            "name": name,
            "type": "radix",
            "male": True,
            "date": std_date,
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
            "name_sound_value": int(name_sound_value),
            "notes": str(notes or ""),
            "modified_at": datetime.now().isoformat()
        }
        
        natives.append(new_native)
        atomic_write_natives(filepath, natives)
        return new_native
    finally:
        _release_lock(filepath)

def update_native(filepath: str, native_id: str, updated_fields: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Updates an existing native by ID with atomic safety and standard DD/MM/YYYY date."""
    if not _acquire_lock(filepath):
        raise RuntimeError("Could not acquire lock to update native")
    try:
        natives = load_natives(filepath)
        updated_native = None
        for i, n in enumerate(natives):
            if n.get("id") == native_id:
                for k, v in updated_fields.items():
                    if k in ['lat', 'lon']:
                        n[k] = float(v)
                    elif k == 'name_sound_value':
                        n[k] = int(v)
                    elif k == 'date':
                        n[k] = to_standard_date(v)
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
    finally:
        _release_lock(filepath)

def delete_native(filepath: str, native_id: str) -> bool:
    """Deletes a native by ID safely with atomic backup."""
    if not _acquire_lock(filepath):
        raise RuntimeError("Could not acquire lock to delete native")
    try:
        natives = load_natives(filepath)
        filtered = [n for n in natives if n.get("id") != native_id]
        if len(filtered) < len(natives):
            return atomic_write_natives(filepath, filtered, allow_empty=True)
        return False
    finally:
        _release_lock(filepath)
