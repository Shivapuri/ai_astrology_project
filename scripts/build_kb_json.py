import os
import json
import re
import markdown

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KB_DIR = os.path.join(BASE_DIR, "knowledge_base")
OUTPUT_JSON = os.path.join(BASE_DIR, "jyotish", "knowledge_base.json")

def render_md(text):
    # Ensure lists have a blank line before them
    text = re.sub(r"([^\n])\n(\s*[\*\-]\s)", r"\1\n\n\2", text)
    # Ensure table start has a blank line before it if preceded by non-pipe and non-empty line
    text = re.sub(r"([^\n|])\n(\s*\|)", r"\1\n\n\2", text)
    # Convert markdown to HTML including tables
    return markdown.markdown(text, extensions=['tables'])

def parse_graha_sutras():
    file_path = os.path.join(KB_DIR, "Graha_Sutras_Reference.md")
    if not os.path.exists(file_path): return {}
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    planets = {}
    pattern = re.compile(r"## \d+\.\s+(\w+)\s+\((?:The\s+)?([\w\s]+)\):\s+([^\n]+)(.*?)(?=\n## \d+|$)", re.DOTALL)
    for match in pattern.finditer(content):
        sanskrit_name = match.group(1).strip()
        english_name = match.group(2).strip()
        description = match.group(3).strip()
        body = match.group(4).strip()
        
        body = re.sub(r"^\s*---\s*", "", body)
        body = re.sub(r"\s*---\s*$", "", body)
        
        key = english_name if english_name not in ["North Node", "South Node"] else sanskrit_name
        
        planets[key] = {
            "sanskrit_name": sanskrit_name,
            "title": description,
            "content": render_md(body)
        }
    return planets

def parse_rasis():
    file_path = os.path.join(KB_DIR, "The_Twelve_Rasis_Reference.md")
    if not os.path.exists(file_path): return {}
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    signs = {}
    pattern = re.compile(r"### 3\.\d+\s+(\w+)\s+\((.*?)\)(.*?)(?=\n### 3\.\d+|$)", re.DOTALL)
    for match in pattern.finditer(content):
        sanskrit_name = match.group(1).strip()
        english_name = match.group(2).strip()
        body = match.group(3).strip()
        
        signs[english_name] = {
            "sanskrit_name": sanskrit_name,
            "content": render_md(body)
        }
    return signs

def parse_bhavas():
    file_path = os.path.join(KB_DIR, "The_Twelve_Bhavas_Reference.md")
    if not os.path.exists(file_path): return {}
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    houses = {}
    pattern = re.compile(r"### (\d+)\.\s+(\w+)\s+House:\s+(.*?)\n(.*?)(?=\n### \d+\.|$)", re.DOTALL)
    for match in pattern.finditer(content):
        house_num = match.group(1).strip()
        title = match.group(3).strip()
        body = match.group(4).strip()
        
        houses[house_num] = {
            "title": title,
            "content": render_md(body)
        }
    return houses

def parse_nakshatras():
    file_path = os.path.join(KB_DIR, "The_Twenty_Seven_Nakshatras_Reference.md")
    if not os.path.exists(file_path): return {}
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    nak_names = ["Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", 
                 "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni", 
                 "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha", 
                 "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha", 
                 "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"]

    nakshatras = {}
    pattern = re.compile(r"### 2\.(\d+)\.\s+(.*?)\n(.*?)(?=\n### 2\.\d+\.|$)", re.DOTALL)
    for match in pattern.finditer(content):
        num = int(match.group(1).strip())
        name_raw = match.group(2).strip()
        body = match.group(3).strip()
        
        name = nak_names[num - 1]
        nakshatras[name] = {
            "number": str(num),
            "content": render_md(body)
        }
    return nakshatras

def build_kb():
    db = {
        "planet": parse_graha_sutras(),
        "sign": parse_rasis(),
        "house": parse_bhavas(),
        "nakshatra": parse_nakshatras()
    }
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2, ensure_ascii=False)
    print(f"Generated {OUTPUT_JSON}")

if __name__ == "__main__":
    build_kb()
