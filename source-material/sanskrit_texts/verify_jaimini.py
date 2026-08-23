import re

def verify_jaimini():
    with open("jaimini_sutras/jaimini_clean2.md", "r", encoding="utf-8") as f:
        text = f.read()

    lines = text.splitlines()

    sutras_by_pada = []
    curr_pada = []

    pada_names = [
        "Adhyaya 1, Pada 1 (Argalas, Aspects, Karakas)",
        "Adhyaya 1, Pada 2 (Karakamsha & Results)",
        "Adhyaya 1, Pada 3 (Arudha Lagna & Results)",
        "Adhyaya 1, Pada 4 (Upapada Lagna & Marriage)",
        "Adhyaya 2, Pada 1 (Ayurdaya: Rudra, Brahma, Maheshwara)",
        "Adhyaya 2, Pada 2 (Kakshya Calculations & Death Timing)",
        "Adhyaya 2, Pada 3 (Shoola, Sthira & Navamsha Dashas)",
        "Adhyaya 2, Pada 4 (Varnada Lagna & Longevity Determinations)"
    ]

    for line in lines:
        if "**" in line and "॥" in line:
            # find all sutra matches in the line
            matches = re.finditer(r"([^\n।॥\*]+?)\s*॥\s*([०-९\d]+)\s*॥", line)
            for m in matches:
                s_text = m.group(1).strip()
                num_str = m.group(2)
                num = int(num_str.translate(str.maketrans("०१२३४५६७८९", "0123456789")))
                
                # Check if this indicates reset to 1
                if num == 1 and curr_pada and len(curr_pada) > 10:
                    sutras_by_pada.append(curr_pada)
                    curr_pada = []
                    
                curr_pada.append((num, s_text))

    if curr_pada:
        sutras_by_pada.append(curr_pada)

    print(f"Total Pādas (Sections) extracted: {len(sutras_by_pada)}")
    total_all = 0
    for idx, pada in enumerate(sutras_by_pada):
        nums = [x[0] for x in pada]
        name = pada_names[idx] if idx < len(pada_names) else f"Section {idx+1}"
        total_all += len(nums)
        missing = [n for n in range(1, max(nums) + 1) if n not in nums]
        print(f"\n[{idx+1}] {name}")
        print(f"    Total Sutras: {len(nums)} (Sutra 1 to {max(nums)})")
        if missing:
            print(f"    Gaps detected in numbering: {missing}")
        else:
            print(f"    Integrity: Complete & Continuous (no gaps)")
            
    print(f"\n=======================================================")
    print(f"GRAND TOTAL SUTRAS: {total_all}")
    print(f"=======================================================")

if __name__ == "__main__":
    verify_jaimini()
