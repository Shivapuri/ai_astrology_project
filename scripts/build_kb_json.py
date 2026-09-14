import os
import json
import re
import yaml
import markdown

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KB_DIR = os.path.join(BASE_DIR, "knowledge_base")
OUTPUT_JSON = os.path.join(BASE_DIR, "jyotish", "knowledge_base.json")

def parse_continuum_block(text):
    pattern = re.compile(r"```[^\n]*\n\s*([^\n]+?)\s*\n\s*┌─+┐\n(.*?)\s*└─+┘\s*\n```", re.DOTALL)
    
    def repl(m):
        title = m.group(1).strip()
        body = m.group(2)
        raw_tiers = re.split(r"\s*├─+┤\s*", body)
        
        tier_items = []
        for raw_tier in raw_tiers:
            lines = [re.sub(r"^[│\s]+|[│\s]+$", "", line).strip() for line in raw_tier.strip().split("\n") if line.strip()]
            if not lines:
                continue
            header = lines[0]
            desc = " ".join(lines[1:]) if len(lines) > 1 else ""
            
            hl = header.lower()
            if "high" in hl or "flourishing" in hl or "exalted" in hl or "friends" in hl:
                t_class = "tier-high"
            elif "moderate" in hl or "balanced" in hl:
                t_class = "tier-moderate"
            elif "neutral" in hl or "steady" in hl or "enemies" in hl:
                t_class = "tier-neutral"
            elif "low" in hl or "pressured" in hl:
                t_class = "tier-low"
            elif "debilitated" in hl or "afflicted" in hl or "fall" in hl or "obstructed" in hl:
                t_class = "tier-afflicted"
            else:
                t_class = "tier-neutral"
                
            tier_items.append(f"""
                <div class="continuum-tier {t_class}">
                    <div class="tier-header">{header}</div>
                    <div class="tier-desc">{desc}</div>
                </div>""")
        
        tiers_html = "\n".join(tier_items)
        return f"""
<div class="dignity-continuum-card">
    <div class="continuum-title">📊 {title}</div>
    <div class="continuum-track">
{tiers_html}
    </div>
</div>
"""
    return pattern.sub(repl, text)

def render_md(text):
    if not text:
        return ""
    # Transform ASCII continuum boxes into beautiful HTML components before markdown processing
    text = parse_continuum_block(text)
    # Ensure lists have a blank line before them
    text = re.sub(r"([^\n])\n(\s*[\*\-]\s)", r"\1\n\n\2", text)
    # Ensure table start has a blank line before it if preceded by non-pipe and non-empty line
    text = re.sub(r"([^\n|])\n(\s*\|)", r"\1\n\n\2", text)
    # Convert markdown to HTML including tables
    return markdown.markdown(text, extensions=['tables'])

def parse_frontmatter(content):
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", content, re.DOTALL)
    if match:
        raw_yaml = match.group(1).strip()
        body = match.group(2).strip()
        try:
            props = yaml.safe_load(raw_yaml)
        except Exception as e:
            props = {}
        return raw_yaml, props, body
    return "", {}, content.strip()

def split_sections(body):
    parts = re.split(r"\n(?=## )", body)
    intro = ""
    sections = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        if part.startswith("## "):
            sections.append(part)
        else:
            intro = f"{intro}\n\n{part}".strip()
    return intro, sections

def parse_rich_planets():
    planets_dir = os.path.join(KB_DIR, "planets")
    if not os.path.isdir(planets_dir):
        return None

    planets = {}
    valid_planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]

    for fname in sorted(os.listdir(planets_dir)):
        if not fname.endswith(".md") or fname.startswith("_"):
            continue
        file_path = os.path.join(planets_dir, fname)
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        raw_yaml, props, body = parse_frontmatter(content)
        p_name = props.get("planet")
        if not p_name:
            for vp in valid_planets:
                if vp.lower() in fname.lower():
                    p_name = vp
                    break
        if not p_name:
            continue

        intro, secs = split_sections(body)

        # Map sections into 6 tabs
        tabs = {}
        if len(secs) >= 6:
            tabs["essence"] = render_md(secs[0])
            tabs["psychology"] = render_md(secs[1])
            tabs["dignity"] = render_md(secs[2])
            tabs["realworld"] = render_md(secs[3])
            tabs["lagnas"] = render_md(secs[4])
            tabs["remedies"] = render_md(secs[5])
        else:
            for idx, sec in enumerate(secs):
                tabs[f"section_{idx+1}"] = render_md(sec)

        planets[p_name] = {
            "name": p_name,
            "sanskrit_name": props.get("sanskrit_name", ""),
            "title": props.get("archetype", props.get("title", f"{p_name} Guide")),
            "archetype": props.get("archetype", ""),
            "raw_yaml": raw_yaml,
            "properties": props,
            "intro": render_md(intro),
            "tabs": tabs,
            "content": render_md(body)
        }

    return planets if len(planets) >= 9 else None

def parse_graha_sutras():
    # Check for rich notes first
    rich = parse_rich_planets()
    if rich:
        print(f"Loaded {len(rich)} rich planet profiles from knowledge_base/planets/")
        return rich

    file_path = os.path.join(KB_DIR, "Graha_Sutras_Reference.md")
    if not os.path.exists(file_path):
        return {}
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

def parse_rich_houses():
    houses_dir = os.path.join(KB_DIR, "houses")
    if not os.path.isdir(houses_dir):
        return None

    houses = {}
    for fname in sorted(os.listdir(houses_dir)):
        if not fname.endswith(".md") or fname.startswith("_"):
            continue
        file_path = os.path.join(houses_dir, fname)
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        raw_yaml, props, body = parse_frontmatter(content)
        h_num = str(props.get("house_number", ""))
        if not h_num:
            match = re.search(r"(\d+)", fname)
            if match:
                h_num = str(int(match.group(1)))
        if not h_num:
            continue

        intro, secs = split_sections(body)

        # Map sections into 5 pedagogical tabs (alongside dynamic Live Chart tab in frontend)
        tabs = {}
        if len(secs) >= 7:
            tabs["essence"] = render_md(secs[0] + "\n\n" + secs[1])
            tabs["condition"] = render_md(secs[2])
            tabs["manifestations"] = render_md(secs[3])
            tabs["diagnosis"] = render_md(secs[4] + "\n\n" + secs[5])
            tabs["remedies"] = render_md(secs[6])
        else:
            for idx, sec in enumerate(secs):
                tabs[f"section_{idx+1}"] = render_md(sec)

        houses[h_num] = {
            "number": h_num,
            "sanskrit_name": props.get("sanskrit_name", ""),
            "title": props.get("archetype", props.get("title", f"House {h_num} Guide")),
            "archetype": props.get("archetype", ""),
            "raw_yaml": raw_yaml,
            "properties": props,
            "intro": render_md(intro),
            "tabs": tabs,
            "content": render_md(body)
        }

    return houses if len(houses) >= 12 else None

def parse_bhavas():
    # Check for rich notes first
    rich = parse_rich_houses()
    if rich:
        print(f"Loaded {len(rich)} rich house profiles from knowledge_base/houses/")
        return rich

    file_path = os.path.join(KB_DIR, "The_Twelve_Bhavas_Reference.md")
    if not os.path.exists(file_path):
        return {}
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

def parse_rasis():
    file_path = os.path.join(KB_DIR, "The_Twelve_Rasis_Reference.md")
    if not os.path.exists(file_path):
        return {}
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

def parse_nakshatras():
    file_path = os.path.join(KB_DIR, "The_Twenty_Seven_Nakshatras_Reference.md")
    if not os.path.exists(file_path):
        return {}
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
    print(f"Generated {OUTPUT_JSON} (Total size: {os.path.getsize(OUTPUT_JSON):,} bytes)")

if __name__ == "__main__":
    build_kb()
