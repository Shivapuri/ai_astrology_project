#!/usr/bin/env python3
"""
generate_ascendant_report.py
----------------------------
Automated Ascendant (Lagna) Synthesis & Study Guide Generator for Astra.
1. Computes the chart and runs Astra's official 5-pillar Lagna vitality evaluation.
2. Evaluates the 6-Tier Prominence Hierarchy:
   - Tier 1: Horizon Degree (< 5° from Campanus Cusp)
   - Tier 2: The Ascendant Lord (Lagnesha Placement, Dignity, Conjunctions)
   - Tier 3: The Sthira Karaka (Sun - The Engine & Battery)
   - Tier 4: 1st Whole-Sign Field Inhabitants
   - Tier 5: Direct Aspects & Sky-Light (Virūpas & Guru Dṛṣṭi)
   - Tier 6: Rising Sign & Nakshatra
3. Locates all matching high-fidelity video lecture notes and source texts in the Vedic Astrology Vault.
4. Archives the raw source notes into organized tier folders:
   ascendant_reports/{Native_Name}/raw_sources/tier_1.../
5. In each tier, extracts direct source condensations (Executive Summaries and Key Takeaways)
   directly from the archived vault source files (mandatory collection phase).
6. Generates a comprehensive, pedagogical master interpretation document:
   ascendant_reports/{Native_Name}/Ascendant_Interpretation.md
   With rich psychological portraiture, behavioral habits, and character disciplines (Dinacharya).
"""

import os
import re
import sys
import shutil
import argparse
import urllib.parse
from typing import Dict, Any, List, Optional

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from jyotish import native_manager
from app import compute_chart_data
from jyotish.generate_jyotish import generate_kala_chart
from scripts.analyze_ascendant import evaluate_ascendant, SIGN_METADATA, SIGN_LIST

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHARTS_FILE = os.path.join(PROJECT_ROOT, "database", "Charts.jsonl")
VAULT_DIR = "/Users/hajnaljanos/PycharmProjects/vedic-astrology-vault/vault"
REPORTS_DIR = os.path.join(PROJECT_ROOT, "ascendant_reports")

def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)

def find_vault_files(patterns: List[str]) -> List[str]:
    """Finds matching files in the vault based on filename substrings."""
    matches = []
    if not os.path.exists(VAULT_DIR):
        return matches
    for root, _, files in os.walk(VAULT_DIR):
        for f in files:
            if not f.endswith(".md"):
                continue
            for pat in patterns:
                if pat.lower() in f.lower():
                    matches.append(os.path.join(root, f))
                    break
    return list(set(matches))

def copy_raw_sources(tier_folder: str, file_paths: List[str]):
    ensure_dir(tier_folder)
    for src in file_paths:
        if os.path.exists(src):
            dst = os.path.join(tier_folder, os.path.basename(src))
            shutil.copy2(src, dst)

def extract_source_condensations(tier_dir: str, preferred_patterns: Optional[List[str]] = None, max_files: int = 3) -> str:
    """Reads the archived vault files in tier_dir matching preferred_patterns and formats their
    Executive Summary and Key Takeaways as high-fidelity direct source text."""
    if not os.path.exists(tier_dir):
        return "*(No archived source text available)*"
    
    all_files = sorted([f for f in os.listdir(tier_dir) if f.endswith(".md")])
    if not all_files:
        return "*(No archived source files found)*"
    
    selected_files = []
    if preferred_patterns:
        for pat in preferred_patterns:
            for f in all_files:
                if pat.lower() in f.lower() and f not in selected_files:
                    selected_files.append(f)
                    break
    # Fill remaining slots with other files if available
    for f in all_files:
        if f not in selected_files:
            selected_files.append(f)
        if len(selected_files) >= max_files:
            break
            
    selected_files = selected_files[:max_files]
    extracted_blocks = []
    folder_name = os.path.basename(tier_dir)

    for fname in selected_files:
        fpath = os.path.join(tier_dir, fname)
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()

            title_m = re.search(r'^title:\s*[\"|\']?(.*?)[\"|\']?$', content, re.M)
            author_m = re.search(r'^author:\s*[\"|\']?(.*?)[\"|\']?$', content, re.M)
            url_m = re.search(r'^url:\s*[\"|\']?(.*?)[\"|\']?$', content, re.M)

            title = title_m.group(1).strip() if title_m else fname.replace(".md", "")
            author = author_m.group(1).strip() if author_m else "Vedic Astrology Knowledge Vault"
            url = url_m.group(1).strip() if url_m else ""

            sum_m = re.search(r'## 📌 2-Minute Executive Summary\s*\n+(.*?)(?=\n+##|\Z)', content, re.S)
            summary = sum_m.group(1).strip() if sum_m else ""

            take_m = re.search(r'## 🔑 Key Astrological Takeaways\s*\n+(.*?)(?=\n+##|\Z)', content, re.S)
            takeaways = take_m.group(1).strip() if take_m else ""

            encoded_fn = urllib.parse.quote(fname)
            rel_link = f"raw_sources/{folder_name}/{encoded_fn}"

            block = f"> #### 📖 Primary Vault Source: [{title}]({rel_link})  \n> **Author / Lineage:** {author}"
            if url:
                block += f" | **Lecture:** [Watch on YouTube]({url})"
            block += "\n>\n"
            if summary:
                block += f"> **📌 High-Fidelity Executive Summary (Direct from Source):**  \n> {summary.replace(chr(10), chr(10) + '> ')}\n>\n"
            if takeaways:
                block += f"> **🔑 Core Principles & Takeaways (Direct from Source):**  \n> {takeaways.replace(chr(10), chr(10) + '> ')}\n"

            extracted_blocks.append(block)
        except Exception:
            continue

    if not extracted_blocks:
        return "*(Source summaries could not be parsed)*"
    return "\n\n".join(extracted_blocks)

def generate_report(native_id: str = "Shivapuri") -> str:
    print(f"Loading native '{native_id}'...")
    native = native_manager.get_native_by_id(CHARTS_FILE, native_id)
    if not native:
        raise ValueError(f"Native '{native_id}' not found in {CHARTS_FILE}")

    clean_name = native.get("name", "Native").replace(" ", "_").replace("(", "").replace(")", "").replace("/", "_")
    person_dir = os.path.join(REPORTS_DIR, clean_name)
    raw_dir = os.path.join(person_dir, "raw_sources")
    ensure_dir(person_dir)
    if os.path.exists(raw_dir):
        shutil.rmtree(raw_dir, ignore_errors=True)
    ensure_dir(raw_dir)

    print("Computing Astra chart and Master Graha Diagnostics...")
    chart = compute_chart_data(native)
    data = evaluate_ascendant(chart)

    rising_sign = data["rising_sign"]
    rising_deg = data["rising_degree"]
    nakshatra = data["nakshatra"]
    pada = data["pada"]
    lord = data["lagnesha"]["planet"]
    lord_sign = data["lagnesha"]["sign"]
    lord_house_ws = data["lagnesha"]["house_whole_sign"]
    lord_house_camp = data["lagnesha"]["house_campanus"]
    lord_dignity = data["lagnesha"]["dignity"]
    lord_sb_pct = data["lagnesha"]["shadbala_pct"]
    
    # 1. TIER 1 SOURCES: Horizon Degree (<5° from Cusp)
    t1_dir = os.path.join(raw_dir, "tier_1_horizon_degree")
    t1_cusp_planets = [occ["graha"] for occ in data["whole_sign_occupants"] if occ["is_conjoined_cusp"]]
    t1_files = []
    if t1_cusp_planets:
        for p in t1_cusp_planets:
            t1_files.extend(find_vault_files([f"{p} in Every House", f"{p} in All Houses", f"{p} in All 12 Houses", f"{p} in All Twelve Houses"]))
    else:
        t1_files.extend(find_vault_files(["What If There Are No Planets in a Sign or House"]))
    copy_raw_sources(t1_dir, t1_files)

    # 2. TIER 2 SOURCES: The Lagnesha (Placement, Sign, Conjunctions)
    t2_dir = os.path.join(raw_dir, "tier_2_lagnesha")
    t2_files = []
    t2_files.extend(find_vault_files([f"{lord} in Every House", f"{lord} in All Houses", f"{lord} in All 12 Houses", f"{lord} in All Twelve Houses", f"{lord} in the Twelve Houses"]))
    t2_files.extend(find_vault_files([f"{lord} in {lord_sign}", f"{lord} in All 12 Signs", f"{lord} in All Zodiac Signs"]))
    d1_grahas = chart["vargas"]["D1"]["grahas"]
    conjoined_with_lord = [g for g, gd in d1_grahas.items() if g != lord and gd.get("sign") == lord_sign]
    for c_g in conjoined_with_lord:
        pair1 = f"{lord} and {c_g}"
        pair2 = f"{c_g} and {lord}"
        t2_files.extend(find_vault_files([pair1, pair2, f"Planets Conjunct {lord}"]))
    t2_files.extend(find_vault_files([f"{lord} for {rising_sign} Ascendant"]))
    copy_raw_sources(t2_dir, t2_files)

    # 3. TIER 3 SOURCES: The Sthira Karaka (The Sun - The Battery & Soul Core)
    t3_dir = os.path.join(raw_dir, "tier_3_sun_karaka")
    t3_files = []
    sun_info = data["sun_karaka"]
    sun_sign = sun_info["sign"]
    sun_ws_house = sun_info["house_whole_sign"]
    t3_files.extend(find_vault_files([f"Sun in the {sun_ws_house}", "The Sun in All Houses", "Sun in the Twelve Houses"]))
    t3_files.extend(find_vault_files([f"Sun in {sun_sign}", "The Sun in All 12 Signs", f"Sun for {sun_sign} Ascendant"]))
    for c_g in sun_info.get("conjunctions", []):
        pair1 = f"Sun and {c_g}"
        pair2 = f"{c_g} and Sun"
        t3_files.extend(find_vault_files([pair1, pair2, "Planets Conjunct Sun"]))
    t3_files.extend(find_vault_files([
        "Sun (Surya)", 
        "Surya - The Sun in Vedic Astrology", 
        "AtmaKaraka and Jaimini Karakas in Vedic Astrology",
        "9 Very Important Fundamental Yogas for the Sun and Ascendant",
        "Importance of the Sun and the Moon in Vedic Astrology",
        "First House (Tanu Bhava)"
    ]))
    copy_raw_sources(t3_dir, t3_files)

    # 4. TIER 4 SOURCES: Field Inhabitants (Whole-Sign House 1)
    t4_dir = os.path.join(raw_dir, "tier_4_field_inhabitants")
    t4_files = []
    ws_occupants = [occ["graha"] for occ in data["whole_sign_occupants"]]
    if ws_occupants:
        for p in ws_occupants:
            t4_files.extend(find_vault_files([f"{p} in Every House", f"{p} in All Houses", f"{p} in All 12 Houses", f"{p} in All Twelve Houses", f"{p} in the Twelve Houses"]))
            t4_files.extend(find_vault_files([f"{p} in {rising_sign}", f"{p} in All 12 Signs"]))
            t4_files.extend(find_vault_files([f"{p} for {rising_sign} Ascendant"]))
    else:
        t4_files.extend(find_vault_files(["What If There Are No Planets in a Sign or House"]))
    copy_raw_sources(t4_dir, t4_files)

    # 5. TIER 5 SOURCES: Direct Aspects & Sky-Light
    t5_dir = os.path.join(raw_dir, "tier_5_aspects_skylight")
    t5_files = []
    t5_files.extend(find_vault_files(["First House (Tanu Bhava)", "The Best and Worst Planets for Health", "The 6 Astrological Strengths", "The Seven Faces of Astrological Shame"]))
    copy_raw_sources(t5_dir, t5_files)

    # 6. TIER 6 SOURCES: Rising Sign & Nakshatra
    t6_dir = os.path.join(raw_dir, "tier_6_rising_sign_nakshatra")
    t6_files = []
    t6_files.extend(find_vault_files([f"{rising_sign} Rising", "Symbolic Recipes", "What is the Zodiac"]))
    t6_files.extend(find_vault_files([f"{nakshatra} Nakshatra Description", f"{nakshatra} Nakshatra"]))
    copy_raw_sources(t6_dir, t6_files)

    tier_sources = {
        "tier_1_horizon_degree": sorted([os.path.basename(f) for f in os.listdir(t1_dir) if f.endswith(".md")]),
        "tier_2_lagnesha": sorted([os.path.basename(f) for f in os.listdir(t2_dir) if f.endswith(".md")]),
        "tier_3_sun_karaka": sorted([os.path.basename(f) for f in os.listdir(t3_dir) if f.endswith(".md")]),
        "tier_4_field_inhabitants": sorted([os.path.basename(f) for f in os.listdir(t4_dir) if f.endswith(".md")]),
        "tier_5_aspects_skylight": sorted([os.path.basename(f) for f in os.listdir(t5_dir) if f.endswith(".md")]),
        "tier_6_rising_sign_nakshatra": sorted([os.path.basename(f) for f in os.listdir(t6_dir) if f.endswith(".md")]),
    }

    tier_dirs = {
        "tier_1": t1_dir,
        "tier_2": t2_dir,
        "tier_3": t3_dir,
        "tier_4": t4_dir,
        "tier_5": t5_dir,
        "tier_6": t6_dir,
    }

    print("Synthesizing comprehensive Ascendant Interpretation Report with direct source collection...")
    # Generate the Markdown document
    md_content = build_markdown_report(data, native, t1_cusp_planets, conjoined_with_lord, tier_sources, tier_dirs)

    out_file = os.path.join(person_dir, "Ascendant_Interpretation.md")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(md_content)

    print(f"✅ Successfully created Ascendant Interpretation Dossier in:\n   {person_dir}")
    print(f"   • Master Report: {out_file}")
    print(f"   • Raw Sources:   {raw_dir}")
    return out_file

def build_tier_1_synthesis(t1_cusp_planets: List[str], rising_sign: str, cusp_deg: float) -> str:
    """Generates detailed, high-fidelity paraphrasing for Tier 1."""
    if not t1_cusp_planets:
        return f"""* **The Unencumbered Crystal Window (Ryan Kurczak & Vic DiCara Principle):**
  * *High-Fidelity Vault Paraphrase (Lesson 02 - What If There Are No Planets in a Sign or House):* In Western or pop astrology, an empty horizon often triggers anxiety that one lacks presence or personality. Ryan Kurczak dispels this myth entirely: there are 12 houses and only 7-9 planets; mathematically, most people have multiple empty houses. An unoccupied rising degree (< 5° orb) is not a void; it is a **supreme blessing of clarity**.
  * *The Lack of Personal Pretense:* When a dominant planet sits right on the cusp (e.g., Mars producing immediate defensive combativeness, or Venus projecting seductive charm), the person wears a heavy theatrical mask before speaking a single word. Without planets on the cusp, the native's eastern horizon acts as an unclouded crystal window.
  * *Clean Executive Handoff:* There is no internal 'committee' fighting over how the physical vehicle presents itself. The rising degree cleanly channels the pure elemental nature of **{rising_sign}** and transfers 100% of executive life direction directly to Tier 2 (the Ascendant Lord)."""
    else:
        planets_str = ", ".join(t1_cusp_planets)
        return f"""* **Dominant Cusp Inhabitant ({planets_str} at the Threshold):**
  * *Immediate Physical Projection:* Sitting within 5° of the Campanus horizon cusp ({cusp_deg}°), **{planets_str}** acts as the supreme megaphone of the incarnation. Before the native utters a word, this planet's elemental frequency commands the room.
  * *Bodily Imprint:* It directly imprints upon facial bone structure, autonomic reflexes, nervous reactions, and physical carriage."""

def build_tier_2_synthesis(lord: Dict[str, Any], rising_sign: str, conjoined_with_lord: List[str]) -> Dict[str, str]:
    """Generates detailed, high-fidelity paraphrasing for Tier 2."""
    planet = lord["planet"]
    sign = lord["sign"]
    house_ws = lord["house_whole_sign"]
    dignity = lord["dignity"]

    # 1. House Domain Paraphrasing
    house_paraphrases = {
        1: ("Autonomy, Self-Cultivation & Independent Pioneering",
            "The Ascendant Lord in the 1st House places 100% of life focus on physical self-definition, vital health, and personal autonomy. The native cannot be placed into someone else's box; they chart their own course with fierce self-reliance."),
        2: ("Resources, Speech & Lineage Preservation",
            "The Ascendant Lord in the 2nd House channels vitality into cultivating durable family resources, personal speech, and moral values. The native's identity is intimately tied to tangible security and articulate communication."),
        3: ("Tactical Initiative, Craftsmanship & Courageous Self-Effort",
            "The Ascendant Lord in the 3rd House engages in hands-on manual skill, creative writing, athletic initiative, and determined self-effort. They thrive on tactical problem solving rather than waiting for handouts."),
        4: ("The Inner Sanctuary & Contemplative Peace (Midnight Nadir)",
            "The Ascendant Lord in the 4th House draws life energy into deep interior contemplation, emotional sanctuary, and private study. Classical texts emphasize that the 4th house is the deepest, lowest point of the sky—the midnight nadir. Worldly noise is secondary; emotional peace and inner contentment are the native's true kingdom."),
        5: ("Creative Intellect, Offspring & Divine Merit (Purva Punya)",
            "The Ascendant Lord in the 5th House flourishes in creative intelligence, counsel, philosophical speculation, and joy. The mind naturally aligns with higher principles and artistic generation."),
        6: ("Problem-Solving, Service & Overcoming Obstacles",
            "The Ascendant Lord in the 6th House thrives in the arena of daily friction, diagnostic analysis, health discipline, and service. They build character by rolling up their sleeves and solving difficult problems."),
        7: ("Relational Mirrors & Diplomatic Alliances",
            "The Ascendant Lord in the 7th House directs identity through partnerships, public diplomacy, and interpersonal trade. Self-discovery occurs in the mirror of the other."),
        8: ("Transformation, Research & Esoteric Depth",
            "The Ascendant Lord in the 8th House plunges into occult mysteries, depth psychology, crisis management, and transformative regeneration. They thrive in unmasking what is hidden beneath the surface."),
        9: ("Higher Ethics, Dharma & Sacred Mentorship",
            "The Ascendant Lord in the 9th House aligns with higher philosophical principles, long-distance exploration, teaching, and divine grace. Life is experienced as an ongoing sacred pilgrimage."),
        10: ("Midday Zenith, Professional Stature & Social Leadership",
            "The Ascendant Lord in the 10th House propels the native into the public eye, career mastery, and visible responsibility. Like the sun at noon, they are built to lead and bear public authority."),
        11: ("Aspirations, Progressive Networks & Collective Expansion",
            "The Ascendant Lord in the 11th House expands into large-scale communities, progressive social vision, and the realization of ambitious lifetime dreams."),
        12: ("The Realm of Transcendence, Solitude & Esoteric Imagination",
            f"""*Vic DiCara's High-Fidelity Paraphrase (Lesson 05 - {planet} in Every House):*
  * **The Contradiction of Growth in Decline:** {planet} signifies growth, expansion, and surplus, while the 12th house (*Vyaya Bhava*) signifies decline, surrender, and expenditure. This creates an alternating rhythm: the native's vitality and outward achievements move in cyclical waves. Periods of intense creative or intellectual expansion are followed by essential retreats into decline, where energy is internalized and cleansed.
  * **Esoteric Imagination & Mystical Trust:** The 12th house governs what is invisible and hard to believe. With {planet} here, the native easily believes in things that are not immediately demonstrable to the physical senses. They possess an extraordinary, fertile imagination (sharing this placement with profound visionary authors like Carlos Castaneda, H.G. Wells, and Frank Herbert).
  * **Clash of Faith and Criticism:** {planet} represents faith, teachers, and conventional religion, while the 12th house represents enemies and skepticism. This creates a deeply independent thinker who is skeptical of conventional dogmas, shallow religious dogmas, or superficial authority figures. They cannot be spoon-fed beliefs; they must test and verify truth through personal, solitary experience.""")
    }
    h_title, h_body = house_paraphrases.get(house_ws, ("Active Domain", "Focuses energy in this house domain."))

    # 2. Sign Paraphrasing
    sign_paraphrases = {
        "Scorpio": f"""*Vic DiCara's High-Fidelity Paraphrase (Lesson 08 - {planet} in Scorpio):*
  * **Wisdom in the Depths:** Scorpio is fixed water ruled by Mars—the alchemical laboratory of psychological trauma, vulnerability, and transformative rebirth. In Scorpio, {planet} is not a detached academic philosopher; it is an occult researcher, depth psychologist, or strategic healer.
  * **Unshakeable Faith in Crisis:** When catastrophe strikes and others panic, {planet} in Scorpio remains intensely calm. The native understands instinctively that the death of the old ego is the mandatory prerequisite for resurrection.
  * **Penetrating Psychological Radar:** The native possesses an almost uncomfortable ability to see through deception, hidden motives, and polite social masks. They demand absolute truth and cannot tolerate superficial small talk.""",
        "Leo": f"""*Regal Nobility & Radiant Self-Respect:* In Leo, {planet} operates through dignified fixed fire, radiating executive magnanimity, moral self-respect, and protective leadership.""",
        "Sagittarius": f"""*The Cosmic Arrow of Truth:* In Sagittarius, {planet} aims its vision toward higher wisdom, ethical education, and expansive philosophical adventure.""",
        "Capricorn": f"""*Tenacious Cardinal Earth:* In Capricorn, {planet} is anchored in structural discipline, administrative patience, duty-bound labor, and resilient endurance."""
    }
    s_body = sign_paraphrases.get(sign, f"Operates through the elemental lens of {sign}, grounding {planet}'s expression in this environment.")

    # 3. Conjunction Analysis
    conjunction_body = ""
    if "Mars" in conjoined_with_lord and planet == "Jupiter":
        conjunction_body = f"""* **Guru-Mangala Yoga (Mars-Jupiter Union - Lesson 18):**
  * *The Dharmic Warrior Archetype:* The ruler of the Ascendant ({planet}) joins forces with Mars in {sign}. In Vedic astrology, this is the celebrated *Guru-Mangala Yoga*. Jupiter provides higher wisdom, ethical vision, and the capacity to see the big picture; Mars provides tactical logic, decisive initiative, and the physical courage to lead the army.
  * *Ethical Action & Execution:* Mars's raw aggression is tempered by Jupiter's grace, preventing cruelty while ensuring that noble ideals do not remain mere daydreaming. The native fights for righteous causes and executes complex, challenging projects.
  * *Lifelong Student vs. Know-It-All Syndrome:* Ryan Kurczak notes that natives with this yoga possess an insatiable appetite for lifelong learning. A common pitfall in youth is intellectual impatience or a 'know-it-all' attitude, which matures over time into humble tactical mastery and the ability to balance personal willpower with surrender to grace."""
    elif "Saturn" in conjoined_with_lord and planet == "Sun":
        conjunction_body = """* **The Sun-Saturn Union (The Great Taskmaster - Lesson 07):**
  * *The Monk Meets the King:* The tight bond between Sun and Saturn is one of the most powerful spiritual signatures in Vedic astrology. The Sun is radiant divine royalty; Saturn is the ascetic monk in rags. Saturn forces the Sun to burn away petty vanity, shallow ambitions, and the need for external applause.
  * *Overcoming the Inner Critic:* Early life is colored by a deep internal feeling of not being good enough, driving the native to overcompensate through fierce self-discipline, reliability, and perfectionism.
  * *Enduring Tapas:* This produces an extraordinary capacity for solitary meditation, disciplined scholarship, and unwavering spiritual loyalty (*Tapas*)."""
    elif conjoined_with_lord:
        conjunction_body = f"* **Planetary Conjunction:** Conjoined with **{', '.join(conjoined_with_lord)}** in {sign}, blending their distinct archetypal agendas directly into the steering wheel of the life path."
    else:
        conjunction_body = f"* **Autonomous Captain:** {planet} sits unaccompanied by conjunction in {sign}, directing life without competing planetary noise."

    # 4. Ascendant Specific Rulership
    asc_role_body = ""
    if rising_sign == "Sagittarius" and planet == "Jupiter":
        asc_role_body = """* **Jupiter for Sagittarius Ascendant (Ryan Kurczak - Lesson 58):**
  * *Dual Kendra Command (1st & 4th Houses):* Jupiter commands both the physical body (*Tanu Bhava*) and the inner emotional heart/domestic sanctuary (*Bandhu Bhava*). The outer life and the inner life are intimately linked.
  * *Body Care Rooted in Wisdom:* Unlike a Venusian approach that cares for the body out of aesthetic vanity, a Sagittarius native cares for their health, nutrition, and physical vehicle out of *wisdom*—recognizing that a clean, vibrant organism is the indispensable launchpad for fulfilling higher *Dharma*.
  * *Emotional Peace as Foundation:* Inner contentment is not an indulgence; it is the prerequisite for clear vision. The mother or maternal lineage often plays an instrumental role in fostering the native's philosophical framework.
  * *Exaltation in 8th & Fall in 2nd:* Jupiter reaches highest emotional maturity not by shouldering heavy financial survival burdens alone in isolation (debilitation in 2nd/Capricorn), but by collaborating with trusted partners and embracing transformative psychological depths (exaltation in 8th/Cancer)."""
    elif rising_sign == "Leo" and planet == "Sun":
        asc_role_body = """* **The Solar Sovereign for Leo Ascendant:**
  * The Sun commands 100% of the executive life engine as both the 1st house ruler and the natural *Sthira Karaka* of vitality. Its strength directly dictates constitutional stamina, self-worth, and moral integrity."""

    return {
        "house_title": h_title,
        "house_body": h_body,
        "sign_body": s_body,
        "conjunction_body": conjunction_body,
        "asc_role_body": asc_role_body
    }

def build_tier_3_synthesis(sun: Dict[str, Any], lord: Dict[str, Any]) -> str:
    """Generates detailed, high-fidelity paraphrasing for Tier 3 (Sun Karaka)."""
    sign = sun["sign"]
    house_ws = sun["house_whole_sign"]
    dignity = sun["dignity"]
    conjoined = sun.get("conjunctions", [])
    is_identical = sun.get("is_karaka_lagnesha_identical", False)

    conjunction_texts = []
    if "Saturn" in conjoined:
        conjunction_texts.append("""* **Sun-Saturn Conjunction (The Great Taskmaster - Lesson 07):**
  * *The Core Internal Conflict:* The Sun represents natural self-esteem, divine inspiration, and radiant authority; Saturn represents cold reality, duty, delays, and forces that humble the ego.
  * *The Psychology of Overcompensation:* Ryan Kurczak explains that individuals with Sun-Saturn often carry an early subconscious conviction that they are 'not good enough'. This internal pressure drives them to overcompensate through relentless discipline, formidable work ethic, and fierce self-reliance.
  * *Maturity Through Trial:* While early life feels heavy and burdened with responsibility, Saturn's touch strips away arrogance. After age 36, this conjunction produces unwavering reliability, gravitas, and deep organizational authority.""")
    if "Venus" in conjoined:
        conjunction_texts.append("""* **Sun-Venus Conjunction & Combustion (Lesson 06):**
  * *King and Diplomatic Advisor:* The Sun is sovereign purpose; Venus is comfort, diplomacy, and relational compromise. In close conjunction, Venus is combust (*Asta*), meaning personal aesthetic desires and relationship compromise are absorbed into the solar will.
  * *Refining Pride into Grace:* Creative and artistic discernment is refined, but the native must guard against expecting others to cater to their sovereign standards.""")

    conjunction_synthesis = "\n".join(conjunction_texts) if conjunction_texts else "* **Autonomous Solar Core:** The Sun sits free from tight conjunctions, radiating its vital prana cleanly."

    vasi_desc = ""
    if "Vasi Yoga" in sun.get("solar_yogas", []):
        vasi_desc = """* **Vasi Yoga (Phaladeepika 6.8):** A planet sits in the 12th house from the Sun (Mercury). In classical astrology, this forms *Vasi Yoga*, indicating that the solar willpower is preceded and guided by an alert, strategic, communicative intelligence. The native thinks and strategizes before taking sovereign action."""

    return f"""* **Essential Dignity & Placement:** The Sun resides in House {sun['house_whole_sign']} in **{sun['sign']}** ({sun['degree']}°), operating with **{sun['dignity']}**.
* **Directional Strength (*Digbala*):** **{sun['digbala_pct']}%** of required quota. The Sun attains maximum directional strength in the 10th house (midday) and minimum in the 4th house (midnight). Operating with {sun['digbala_pct']}%, solar fire is focused into practical, sustained application.
* **Kinetic Stamina (*Shadbala*):** **{sun['shadbala_pct']}%** of required quota, providing a steady baseline of constitutional endurance.
* **Grahas Conjoined with the Sun:** {', '.join(conjoined) if conjoined else 'None'}
* **Combustion Inflicted (*Asta*):** {', '.join(sun.get('combust_planets', [])) if sun.get('combust_planets') else 'None'}
{conjunction_synthesis}
* **Planetary Yogas Flanking the Sun:** **{', '.join(sun.get('solar_yogas', [])) if sun.get('solar_yogas') else 'None'}**
{vasi_desc}"""

def build_tier_4_synthesis(occupants: List[Dict[str, Any]], rising_sign: str) -> str:
    """Generates detailed, high-fidelity paraphrasing for Tier 4 (1st House Inhabitants)."""
    if not occupants:
        return f"""* **The Clean Horizon Container (Ryan Kurczak Masterclass):**
  * There are no planets seated directly in the 1st House. As Ryan Kurczak explains (*What If There Are No Planets in a Sign or House*), an unoccupied 1st house represents an unconflicted personal container.
  * There is no competing internal committee pulling the native's immediate behavioral reflexes in divergent directions. The Ascendant filters cosmic light cleanly through the rising sign and transfers 100% of executive authority directly to its ruling lord."""

    texts = []
    for occ in occupants:
        g = occ["graha"]
        deg = occ["degree"]
        if g == "Mercury":
            texts.append(f"""* **Mercury in the 1st House (Supreme Directional Strength / Digbala - Lesson 04):**
  * *Peak Directional Force:* Mercury attains supreme *Digbala* (directional strength) in the 1st House. Seated directly on the dashboard of the physical vehicle, Mercury blesses the native with youthful posture, bright sparkling eyes, rapid cognitive reflexes, versatile adaptability, and articulate speech.
  * *Vic DiCara's Insight (Lesson 09 - Mercury in Sagittarius):* In Sagittarius, Mercury is in planetary *detriment* (opposite its home of Gemini). This creates a fascinating mental dynamic: Mercury loves facts, data, and fine print; Sagittarius loves grand vision, philosophy, and the distant horizon. As a result, the native skips over tedious micro-details and pedantic bureaucracy to focus on the big-picture truth, higher education, and candid, blunt honesty.
  * *Ryan Kurczak's Insight (Lesson 62 - Mercury for Sagittarius Ascendant):*
    * **Dual Kendra Lordship (7th & 10th Houses):** For a Sagittarius Ascendant, Mercury commands two vital angular houses—the 7th house of partnerships/trade (Gemini) and the 10th house of career/public status (Virgo).
    * **The Swiss Army Knife Persona:** Placed in the 1st house, Mercury channels professional ambition, organizational craft, and relational diplomacy directly into the physical persona. The native displays vocational polyvalence (able to excel across diverse careers) and refuses to compromise on ethical and communicative standards.
  * *Observant Wit & Communicative Dexterity:* Like historical figures with 1st-house Mercury (George Lucas, Steve Martin, Jimi Hendrix), the native possesses remarkable verbal timing, pattern recognition, and an infectious, youthful curiosity that keeps the mind sharp throughout life.""")
        elif g == "Jupiter":
            texts.append(f"* **Jupiter in the 1st House (Supreme Digbala):** Expands benevolence, wisdom, optimism, and physical dignity.")
        elif g == "Venus":
            texts.append(f"* **Venus in the 1st House:** Imparts magnetic grace, artistic refinement, social charm, and aesthetic discernment.")
        elif g == "Mars":
            texts.append(f"* **Mars in the 1st House:** Imparts dynamic physical courage, athletic vigor, competitive drive, and decisive momentum.")
        elif g == "Saturn":
            texts.append(f"* **Saturn in the 1st House:** Imparts lean endurance, disciplined gravity, emotional sobriety, and patient perseverance.")
        elif g == "Sun":
            texts.append(f"* **Sun in the 1st House:** Imparts radiant executive dignity, natural leadership, physical vitality, and strong self-reliance.")
        elif g == "Moon":
            texts.append(f"* **Moon in the 1st House:** Imparts receptive emotional sensitivity, fluctuating moods, intuitive empathy, and public visibility.")
        else:
            texts.append(f"* **{g} in the 1st House ({deg}°):** Shapes the physical demeanor and daily reflexes through its elemental archetype.")
    return "\n\n".join(texts)

def build_tier_5_synthesis(aspects: Dict[str, Any], totals: Dict[str, Any]) -> str:
    """Generates detailed, high-fidelity paraphrasing for Tier 5 (Aspects & Sky-Light)."""
    descriptions = []
    
    if "Moon" in aspects and (aspects["Moon"].get("plus", 0.0) > 5.0 or aspects["Moon"].get("minus", 0.0) > 5.0):
        net_m = aspects["Moon"].get("net", 0.0)
        descriptions.append(f"""* **The Lunar Mirror (Net {net_m:+.1f} Virūpas from the Moon):**
  * *Psychic & Emotional Impressionability:* The Moon casts its ray directly onto the horizon degree. The Moon is the *Manas* (sensory mind) and emotional weather. When the Moon aspects the Ascendant, the native acts as an emotional sponge—instinctively feeling the room's atmosphere, subtle interpersonal shifts, and unspoken group dynamics.
  * *Biological Necessity of Solitude:* Because the native absorbs emotional currents so rapidly, regular periods of quiet solitude are not an anti-social retreat; they are a biological imperative to clear psychic static and reset the nervous system.""")

    if "Jupiter" in aspects and aspects["Jupiter"].get("plus", 0.0) > 10.0:
        descriptions.append(f"""* **The Golden Shield (Guru Drishti - +{aspects['Jupiter'].get('plus', 0.0):.1f} Virūpas):**
  * *Brihat Jataka 1.19 Supreme Protection:* Jupiter casts a direct, protective aspect onto the eastern horizon. Classical authorities consider *Guru Drishti* the foremost celestial shield, protecting constitutional health, elevating moral judgment, and mitigating harsh planetary transits.""")

    if "Saturn" in aspects and aspects["Saturn"].get("minus", 0.0) > 10.0:
        descriptions.append(f"""* **Saturn's Sobering Gaze (-{aspects['Saturn'].get('minus', 0.0):.1f} Virūpas):**
  * Saturn enforces realism, patience, and caution, preventing reckless physical gambles.""")

    if "Mars" in aspects and aspects["Mars"].get("minus", 0.0) > 10.0:
        descriptions.append(f"""* **Mars' Kinetic Heat (-{aspects['Mars'].get('minus', 0.0):.1f} Virūpas):**
  * Mars injects kinetic restlessness and urgency, demanding constructive physical channels.""")

    if not descriptions:
        return "* **Even Aspectual Field:** The horizon receives balanced ambient planetary rays without severe distortion."
    return "\n\n".join(descriptions)

def build_tier_6_synthesis(rising_sign: str, nakshatra: str, pada: int, swamsa: str, nak_lord: str, sub_lord: str) -> str:
    """Generates detailed, high-fidelity paraphrasing for Tier 6 (Rasi & Nakshatra)."""
    rasi_text = ""
    if rising_sign == "Sagittarius":
        rasi_text = """### 6.1 Rasi Architecture: Sagittarius (Dhanu Lagna)
*Vic DiCara's High-Fidelity Paraphrase (Lesson 09 - Sagittarius Rising):*
* **The Master Archetypes of Growth & Expansion:** Sagittarius is dual fire (*Dvisvabhava Agni*) ruled by Jupiter (*Guru*). At its root, Sagittarius represents high biological and intellectual metabolism—the capacity to rapidly ingest fuel, ideas, or experiences, burn them cleanly, and convert them into enthusiastic forward momentum.
* **The Centaur Archer Symbolism:** Half horse, half human aiming an arrow toward the heavens. The horse represents robust physical vitality, speed, and animal stamina; the human archer represents ethical aim, higher philosophy, and transcendental aspiration.
* **The 6 Master Archetypal Polarities (Potential vs Expression):**
  1. *High Metabolism & Rapid Healing* (High Dignity) vs. *Excessive Appetite & Weight Fluctuations* (Low Dignity)
  2. *Zest for Experience & Deep Appetite for Life* vs. *Uncritical Consumption & Naivety*
  3. *Boundless Energy & Output* vs. *Impatience & Abandoned Unfinished Projects*
  4. *Inspiring Optimism & Morale Booster* vs. *Overstepping Boundaries & Meddling*
  5. *Rich Pluralistic Learning* vs. *Impractical Theoretical Obsession*
  6. *Uplifting Mentor & Guide* vs. *Intrusive, Preachy Authoritarian*"""
    else:
        rasi_text = f"""### 6.1 Rasi Architecture: {rising_sign}
* **Elemental Blueprint:** Operating through {rising_sign}, the native engages the world with the foundational traits of this sign, establishing the perceptual lens of the physical incarnation."""

    nak_text = ""
    if nakshatra == "Jyeshtha":
        nak_text = f"""### 6.2 Nakshatra Alignment: Jyeshtha (Pada {pada}, Swamsa {swamsa})
*High-Fidelity Paraphrase (Michael Reed & Ryan Kurczak - Lesson 19 - Jyeshtha Nakshatra):*
* **Zodiac Coordinates & Ruling Graha:** 16°40' - 30°00' Scorpio, ruled by **Mercury**. Associated with the star **Antares** (*the rival of Mars*), symbolizing formidable courage and strength rivaling the god of war.
* **Deity & Symbolism:** Presided over by **Indra** (King of the Gods) and symbolized by a **Protective Circular Amulet / Talisman**. Symbolically represents the middle finger, which in yogic *pranayama* (breath control) is used to block the nostril—signifying supreme self-control and mastery over sensory impulses.
* **Conquering the Senses & The Neutral Mind:** 
  * Indra conquered the senses through severe austerities and was granted the *Sudarshana Chakra*. Conquering the senses does not mean ascetic self-denial; it means establishing the *right relationship* with them, seeing through changing sensory illusions into absolute truth.
  * Jyeshtha operates through the **Neutral Mind**—rising above the positive mind (which sees only advantages) and the negative mind (which sees only dangers) to view circumstances with complete, objective clarity.
* **The True Warrior Who Surrenders:** The *Shakti* of Jyeshtha is "the power to rise and conquer." This power comes not from stubborn brute force, but from perspective. A true warrior knows when to withdraw from the battlefield to reorganize, surrendering personal pride and illusions so that they can rise renewed."""
    else:
        nak_text = f"""### 6.2 Nakshatra Alignment: {nakshatra} (Pada {pada})
* **Galactic Anchor:** Dhruva Middle Mula (Sidereal Equatorial Nakshatra)
* **Ruling Graha:** {nak_lord} | **Sub-Lord:** {sub_lord}
* **Esoteric Impress:** Channels deep subconscious currents guiding the soul's karmic evolution."""

    return f"{rasi_text}\n\n{nak_text}"

def build_part_8_synthesis(data: Dict[str, Any], native: Dict[str, Any], conjoined_with_lord: List[str], t1_cusp_planets: List[str]) -> str:
    """Generates the rich, human-centered Part 8 holistic portrait with character disciplines."""
    name = data["subject_name"]
    rising_sign = data["rising_sign"]
    lord = data["lagnesha"]
    sun = data["sun_karaka"]
    occupants = [o["graha"] for o in data["whole_sign_occupants"]]
    v_score = data["vitality_score"]
    v_tier = data["vitality_tier"]
    archetype = data["archetype"]
    verdict = data["verdict"]

    # Tailored synthesis for Mina (Sagittarius Lagna, Mercury in 1st, Jupiter in 12th Scorpio w/ Mars, Sun in 2nd Capricorn w/ Saturn & Venus)
    if rising_sign == "Sagittarius" and "Mercury" in occupants and lord["planet"] == "Jupiter" and lord["house_whole_sign"] == 12:
        return f"""### 8.1 Seeing {name} in Person: Physical Presence, Demeanor & Living Impression
When you meet {name} in person, you are immediately struck by an intriguing duality between an outward, sparkling youthfulness and a deep, intense interior gravitas:

* **Physical Carriage & Movement:**
  * Moving with light, nimble agility (blessed by **Mercury with supreme Digbala in the 1st House**), {name} possesses an athletic, upright carriage. The body carries the natural kinetic vitality of Sagittarius Fire—always poised as if ready to embark on an intellectual or physical expedition.
* **Facial Expression & Gaze:**
  * The eyes are luminous, highly expressive, and relentlessly observant. Nothing escapes notice. While {name} smiles easily and radiates a warm, approachable curiosity, a closer look reveals a penetrating, analytical gaze (the hallmark of **Jupiter in Scorpio conjoined Mars**). You quickly realize you are not speaking to someone who can be flattered or deceived; {name} instinctively scans beneath the surface of words.
* **Voice, Speech & Conversational Cadence:**
  * Speech is fast-paced, witty, articulate, and disarmingly candid (**Mercury in Sagittarius**). {name} has zero tolerance for tedious bureaucratic small talk or polite hypocrisies. Conversations naturally gravitate toward big ideas, philosophy, psychology, humor, and practical truth. Ideas are delivered with infectious enthusiasm, though occasionally with a bluntness that can startle more delicate temperaments.

---

### 8.2 Core Psychological Architecture & Internal Tensions

Behind the charming, quick-witted exterior lies a complex, formidable internal engine governed by a profound psychological tension:

```
                      THE PSYCHOLOGICAL ENGINE
   ┌─────────────────────────────────────────────────────────────┐
   │ THE OUTWARD PERSONA:                                        │
   │ Sagittarius Rising + Mercury (Digbala in 1st)               │
   │ • Witty, curious, optimistic, articulate, visionary         │
   └──────────────────────────────┬──────────────────────────────┘
                                  │ Tension & Dialectic
   ┌──────────────────────────────▼──────────────────────────────┐
   │ THE EXECUTIVE CORE:                                         │
   │ Jupiter in 12th (Scorpio) + Mars (Guru-Mangala Yoga)        │
   │ • Intensely private, depth psychologist, esoteric researcher│
   │ • Needs profound solitude; skeptical of conventional dogmas │
   └──────────────────────────────┬──────────────────────────────┘
                                  │ Constitutional Anchor
   ┌──────────────────────────────▼──────────────────────────────┐
   │ THE CONSTITUTIONAL TASKMASTER:                              │
   │ Sun in 2nd (Capricorn) conjoined Saturn & Venus             │
   │ • Strict inner critic, fear of inadequacy, iron discipline  │
   │ • Overcompensates through relentless reliability & duty     │
   └─────────────────────────────────────────────────────────────┘
```

1. **The Visionary vs. The Hermit (1st House vs. 12th House):**
   * While the 1st-house Mercury seeks intellectual exchange and social engagement, the Ascendant Lord (Jupiter) resides in the 12th house in Scorpio conjoined Mars. {name} has a profound need for privacy, retreat, and quiet research. If forced into continuous social exposure without solitary downtime, the nervous system quickly becomes depleted and overstimulated.
2. **The Optimist vs. The Taskmaster (Sagittarius Fire vs. Capricorn-Saturn):**
   * The Sagittarius archer wants to dream big and aim for distant horizons. However, the constitutional battery (Sun conjoined Saturn in Capricorn) carries an exacting inner taskmaster. A quiet voice inside warns: *"You haven't done enough; prove yourself through flawless competence."* This creates an internal pressure to over-deliver, ensuring that high philosophical ideals are grounded in uncompromising practical standards.

---

### 8.3 Shadow Triggers & Vulnerability Traps

* **The Know-It-All Truth Trap:** With Mercury in detriment in Sagittarius conjoined with a penetrating Scorpio-Mars executive core, {name} often sees the truth or the solution long before others do. The temptation is to shoot verbal arrows of candid truth with such precision that it bruises sensitive egos.
* **The Overcompensation Burnout Trap:** Driven by the Sun-Saturn signature in the 2nd house, {name} risks ignoring physical exhaustion to fulfill self-imposed duties. Pushing through fatigue out of an unconscious fear of 'not being good enough' can trigger sudden crashes in vitality.
* **The Horizon Restlessness Trap:** The classic shadow of Sagittarius is starting five brilliant new projects with fiery enthusiasm and abandoning them when tedious administrative follow-through is required.

---

### 8.4 The 5 Pillars of Character Discipline (*Dinacharya* Routine)

To harmonize this powerful astrological constitution, {name} must anchor daily life in **five non-negotiable behavioral disciplines**:

1. **The Morning Neutral Mind Inception (*Jyeshtha Breathwork*):**
   * *The Practice:* Spend the first 15 minutes of the morning in silent *Pranayama* using the middle finger for alternate nostril breathing (*Nadi Shodhana*). 
   * *Astrological Rationale:* Jyeshtha Nakshatra is presided over by Indra, whose power is the conquest of the senses through breath control. This stills the fast-paced Mercury intellect and anchors the consciousness in the **Neutral Mind** before external demands or digital screens intrude.
2. **Daily Kinetic Energy Discharge (*Mars-Jupiter in Scorpio*):**
   * *The Practice:* 30–45 minutes of vigorous physical training every single day (fast-paced walking in nature, swimming, martial arts, or resistance training).
   * *Astrological Rationale:* With Mars conjoined Jupiter in fixed water, excess metabolic fire (*Agni*) and mental intensity must be physically discharged; otherwise, it turns inward as nervous tension or restlessness.
3. **The "Finish What You Start" Rule (*Sagittarius Remedy*):**
   * *The Practice:* Adopt a strict single-focus work rule: no new major creative or study project may be initiated until the current one reaches a tangible, completed milestone.
   * *Astrological Rationale:* Transmutes the low-dignity Sagittarius tendency to scatter energy across multiple unfinished horizons into enduring, monumental mastery.
4. **The Solitary Evening Sanctuary (*12th House Jupiter*):**
   * *The Practice:* A mandatory 60-to-90-minute digital blackout each evening before sleep, dedicated to reading, contemplation, journaling, or quiet study in absolute solitude.
   * *Astrological Rationale:* As Vic DiCara notes (*Lesson 05*), 12th-house Jupiter requires quiet decline to digest experiences. This evening retreat cleanses psychic impressionability absorbed from the environment (Moon's aspect) and recharges the soul battery.
5. **The Inner Critic Reality Check (*Sun-Saturn Remedy*):**
   * *The Practice:* Daily conscious reframing: decoupling self-worth from sheer productivity or perfection. Celebrate completed efforts without demanding unattainable perfection.
   * *Astrological Rationale:* Disarms the harsh Saturnian taskmaster in the 2nd house, allowing the native to experience the joy and expansive grace of Jupiter."""

    # General / Shivapuri fallback
    else:
        return f"""### 8.1 Seeing {name} in Person: Physical Presence, Demeanor & Living Impression
When you observe {name}, the immediate impression is shaped by the dignified stillness of {rising_sign}:

* **Physical Carriage & Presence:**
  * Carrying a natural gravity and poise, {name} does not rush. Movements are deliberate, measured, and self-contained.
* **Gaze & Expression:**
  * The expression is quiet, deeply introspective, and reflective. The eyes convey an intense inner life that is not displayed for public spectacle.
* **Speech & Cadence:**
  * Conversational rhythm is calm, thoughtful, and reserved. Words are weighed carefully before being spoken.

---

### 8.2 Core Psychological Architecture & Internal Tensions
* **The Contemplative Sanctuary:** With the Ascendant Lord in House {lord['house_whole_sign']} in {lord['sign']}, vitality is directed into interior mastery, meditation, and study rather than aggressive worldly commerce.
* **The Taskmaster's Forge:** Influenced by Saturnian sobriety and rigorous duties, character is forged through patient perseverance, self-restraint, and devotion to sacred truth.

---

### 8.3 Shadow Triggers & Vulnerability Traps
* **Constitutional Fatigue:** Sensitive physical stamina requiring conscious pacing and avoidance of noisy, chaotic environments.
* **Overly Strict Self-Denial:** Guarding against excessive austerity that neglects simple bodily nourishment.

---

### 8.4 Practical Daily Habits (*Dinacharya* Remedies)
1. **Honor the Morning Inception Window:** The first 60 minutes after waking anchor the Ascendant's trajectory. Dedicate this period to quiet reflection, breathwork, and meditation.
2. **Align Physical Rhythms with Solar Vitality:** Respect the Shadbala stamina quota. Ensure balanced nutrition and restorative rest.
3. **Harmonize the Ascendant Lord:** Engage in conscious activities that fulfill the highest octave of {lord['planet']} (wisdom, contemplative depth, and right livelihood)."""

def build_markdown_report(data: Dict[str, Any], native: Dict[str, Any], t1_cusp_planets: List[str], conjoined_with_lord: List[str], tier_sources: Optional[Dict[str, List[str]]] = None, tier_dirs: Optional[Dict[str, str]] = None) -> str:
    name = data["subject_name"]
    rising_sign = data["rising_sign"]
    rising_deg = data["rising_degree"]
    meta = data["sign_meta"]
    cusp_deg = data["bhava_1_campanus"]["cusp"]
    b1_start = data["bhava_1_campanus"]["start"]
    b1_end = data["bhava_1_campanus"]["end"]
    nakshatra = data["nakshatra"]
    pada = data["pada"]
    nak_lord = data["nakshatra_lord"]
    sub_lord = data["sub_lord"]
    swamsa = data["swamsa_d9"]
    
    lord = data["lagnesha"]
    sun = data["sun_karaka"]
    sc = data["sudarshana_chakra"]
    fmat = data["functional_matrix"]
    ps = data["pillar_scores"]
    audit = data["audit_trail"]
    v_score = data["vitality_score"]
    v_tier = data["vitality_tier"]
    v_class = data["vitality_class"]
    archetype = data["archetype"]
    verdict = data["verdict"]

    bars = int(round(v_score))
    bar_str = "█" * bars + "░" * (10 - bars)

    # Determine Prominence Winner
    if t1_cusp_planets:
        prominence_headline = f"Tier 1 Dominance: {', '.join(t1_cusp_planets)} Conjunct Horizon Cusp (<5° Orb)"
        prominence_desc = f"The physical persona and initial impression are directly dominated by {', '.join(t1_cusp_planets)} standing immediately upon the eastern horizon."
    else:
        prominence_headline = f"Tier 2 Dominance: Lagnesha ({lord['planet']}) as Undisputed Primary Voice"
        prominence_desc = f"Because no planets sit directly on the rising degree, the horizon is unencumbered. 100% of the executive life force is concentrated in the Ascendant Lord ({lord['planet']}), placed in House {lord['house_whole_sign']} in {lord['sign']}."

    conjoined_str = ', '.join(conjoined_with_lord) if conjoined_with_lord else 'None (Unaspected by conjunction)'
    occupancy_str = 'None (Clean container)' if not data['whole_sign_occupants'] else ', '.join([f"{o['graha']} ({o['degree']}°)" for o in data['whole_sign_occupants']])
    cusp_planets_str = 'None' if not t1_cusp_planets else ', '.join(t1_cusp_planets)

    # Sun Karaka variables
    sun_conjoined_str = ', '.join(sun.get('conjunctions', [])) if sun.get('conjunctions') else 'None'
    sun_combust_str = ', '.join(sun.get('combust_planets', [])) if sun.get('combust_planets') else 'None'
    sun_yogas_str = ', '.join(sun.get('solar_yogas', [])) if sun.get('solar_yogas') else 'None'
    sun_lajjitadi_str = ', '.join(sun.get('lajjitadi', [])) if sun.get('lajjitadi') else 'None'

    is_identical = sun.get('is_karaka_lagnesha_identical', False)
    if is_identical:
        karaka_rel_badge = "👑 Double Confluence (Karaka-Lord Identity: Sun is both Lagnesha & 1st House Karaka)"
        karaka_synthesis = f"""* **Double Confluence (Karaka-Lord Identity):** In this horoscope, the Sun occupies a position of supreme singular authority—it is *both* the personal Driver (*Lagneśa*) and the eternal Cosmic Ambassador of Vitality (*Sthira Karaka* for the 1st house). 
* **The Concentrated Mandate:** Classical Vedic texts emphasize that when a house lord and its natural significator merge into a single planet, there is no separation between external choices and internal life force. The Sun bears 100% of the internal governance of the self:
  * Its strengths elevate character, physical resilience, and dignity simultaneously.
  * Its constraints (such as conjoining Saturn or receiving malefic rays) double in impact, requiring conscious management of physical stamina and avoiding burnout."""
    else:
        karaka_rel_badge = f"⚖️ Dual Governance (Lagnesha is {lord['planet']}; Sun is independent Sthira Karaka)"
        karaka_synthesis = f"""* **The Dual Governance Matrix (The Driver & The Battery):** In this horoscope, the steering wheel and the engine are divided between two distinct celestial ambassadors:
  * **The Driver (*Lagneśa* - {lord['planet']}):** Dictates conscious choices, personality direction, and daily lifestyle from House {lord['house_whole_sign']} in {lord['sign']}.
  * **The Battery & Soul Core (*Sthira Karaka* - Sun):** Resides in House {sun['house_whole_sign']} (Whole Sign) / House {sun['house_campanus']} (Campanus) in {sun['sign']}, operating with **{sun['dignity']}** and **{sun['shadbala_pct']}%** Shadbala.
* **Vital Reserve Interaction:** While {lord['planet']} manages the vehicle on the road, the Sun provides the underlying constitutional resilience, bone density, and moral conviction. A strong Sun acts as an unshakeable anchor that supports the native even during difficult transits or challenging life cycles of the Lagnesha."""

    # Build rich tier texts
    t1_synthesis = build_tier_1_synthesis(t1_cusp_planets, rising_sign, cusp_deg)
    t2_data = build_tier_2_synthesis(lord, rising_sign, conjoined_with_lord)
    t3_synthesis = build_tier_3_synthesis(sun, lord)
    t4_synthesis = build_tier_4_synthesis(data['whole_sign_occupants'], rising_sign)
    t5_synthesis = build_tier_5_synthesis(data.get('aspects_on_cusp', {}), data.get('aspect_totals', {}))
    t6_synthesis = build_tier_6_synthesis(rising_sign, nakshatra, pada, swamsa, nak_lord, sub_lord)
    part_8_synthesis = build_part_8_synthesis(data, native, conjoined_with_lord, t1_cusp_planets)

    # Extract high-fidelity vault source condensations from local archived files
    if tier_dirs:
        t1_source_text = extract_source_condensations(tier_dirs.get("tier_1", ""), ["What If There Are No Planets"])
        t2_source_text = extract_source_condensations(tier_dirs.get("tier_2", ""), [f"{lord['planet']} for {rising_sign}", f"{lord['planet']} in {lord['sign']}.md", "Mars and Jupiter", "Sun and Saturn", f"{lord['planet']} in Every House"])
        t3_source_text = extract_source_condensations(tier_dirs.get("tier_3", ""), ["Sun and Saturn", "Sun and Venus", f"Sun in {sun['sign']}", "First House (Tanu Bhava)"])
        t4_source_text = extract_source_condensations(tier_dirs.get("tier_4", ""), [f"Mercury for {rising_sign}", f"Mercury in {rising_sign}", "Mercury in All Twelve Houses", "What If There Are No Planets"])
        t5_source_text = extract_source_condensations(tier_dirs.get("tier_5", ""), ["First House (Tanu Bhava)", "The Best and Worst Planets for Health"])
        t6_source_text = extract_source_condensations(tier_dirs.get("tier_6", ""), [f"{rising_sign} Rising", f"{nakshatra} Nakshatra with", f"{nakshatra} Nakshatra Description"])
    else:
        t1_source_text = t2_source_text = t3_source_text = t4_source_text = t5_source_text = t6_source_text = "*(Raw sources archived in local folders)*"

    if tier_sources is None:
        tier_sources = {}

    def make_file_links(folder: str) -> str:
        files = tier_sources.get(folder, [])
        if not files:
            return f"*(No raw vault files currently archived for `{folder}`)*"
        lines = []
        for fn in sorted(files):
            encoded = urllib.parse.quote(fn)
            lines.append(f"* 📄 [{fn}](raw_sources/{folder}/{encoded})")
        return "\n".join(lines)

    t1_links = make_file_links("tier_1_horizon_degree")
    t2_links = make_file_links("tier_2_lagnesha")
    t3_links = make_file_links("tier_3_sun_karaka")
    t4_links = make_file_links("tier_4_field_inhabitants")
    t5_links = make_file_links("tier_5_aspects_skylight")
    t6_links = make_file_links("tier_6_rising_sign_nakshatra")
    total_raw_count = sum(len(v) for v in tier_sources.values())

    clean_name = native.get("name", "Native").replace(" ", "_").replace("(", "").replace(")", "").replace("/", "_")

    md = f"""# 🌅 Precision Ascendant Interpretation: {name}

> **Subject Profile:** {name} | **Birth Coordinates:** {native.get('date')} {native.get('time')} ({native.get('place', '')})  
> **Calculation Engine:** Astra Integrated Approach (Tropical Rasis, Campanus Cusps, Dhruva Nakshatras at 246°40' RA)  
> **Source Provenance:** [Vedic Astrology Knowledge Vault](file:///Users/hajnaljanos/PycharmProjects/vedic-astrology-vault/vault/) (Ryan Kurczak & Vic DiCara)  
> **Dossier Directory:** All materials are self-contained in `ascendant_reports/{clean_name}/`  
> **Master Synthesis Report:** `Ascendant_Interpretation.md` (this dossier)  
> **Archived Raw Sources:** `raw_sources/` ({total_raw_count} original lecture notes in 6 tier folders)

---

## 📊 Part 0: Precision Calculative Snapshot & Master Diagnostics

```text
===========================================================================
       ☀️ ASCENDANT (LAGNA) & 1ST HOUSE SNAPSHOT: {name} ☀️
===========================================================================
🌅 RISING SIGN (RASI):    {rising_sign} ({rising_deg}°)
   • Element & Quality:   {meta.get('element')} | {meta.get('modality')} | {meta.get('polarity')}
   • Core Archetype:      {meta.get('archetype')}
   • Nakshatra (Dhruva):  {nakshatra} (Pada {pada}) [Lord: {nak_lord}, Sub-Lord: {sub_lord}]
   • Campanus 1st Bhava:  Cusp {cusp_deg}° (Span: {b1_start}° -> {b1_end}°)
   • Navamsha Swamsa(D9): {swamsa}

🪐 1ST HOUSE STATUS & ASPECTS:
   • Inhabitants:         {'None (Field is clean)' if not data['whole_sign_occupants'] else ', '.join([o['graha'] for o in data['whole_sign_occupants']])}
   • Hemming (Kartari):   {data['kartari_yoga']}
   • Net Aspect Light:    {data['aspect_totals'].get('net', 0.0):+5.2f} Virupas (Benefic: +{data['aspect_totals'].get('plus', 0.0):.2f}, Malefic: -{data['aspect_totals'].get('minus', 0.0):.2f})

👑 ASCENDANT LORD (LAGNESHA):
   • Ruling Planet:       {lord['planet']}
   • Placement:           House {lord['house_whole_sign']} (Whole Sign) / House {lord['house_campanus']} (Campanus) in {lord['sign']} ({lord['degree']}°)
   • Essential Dignity:   {lord['dignity']}
   • Shadbala Strength:   {lord['shadbala_pct']}% of required minimum
   • Conjunctions:        {conjoined_str}
   • Combustion Status:   {'Combust' if lord['is_combust'] else 'Clear / Free from Combustion'}
   • Lajjitadi States:    {', '.join(lord['avasthas']['lajjitadi']) if lord['avasthas']['lajjitadi'] else 'None'}

☀️ THE SUN (SURYA - 1ST HOUSE KARAKA):
   • Placement:           House {sun['house_whole_sign']} (Whole Sign) / House {sun['house_campanus']} (Campanus) in {sun['sign']} ({sun['degree']}°)
   • Essential Dignity:   {sun['dignity']}
   • Shadbala & Digbala:  Shadbala: {sun['shadbala_pct']}% quota | Digbala: {sun['digbala_pct']}% quota
   • Conjunctions:        {sun_conjoined_str}
   • Combustion Field:    Combusting: {sun_combust_str}
   • Solar Yogas:         {sun_yogas_str}
   • Karaka Relationship: {karaka_rel_badge}
   • Lajjitadi States:    {sun_lajjitadi_str}

===========================================================================
🏛️ OFFICIAL MASTER GRAHA DIAGNOSTICS: LAGNA VITALITY EVALUATION
===========================================================================
🏆 COMPOSITE VITALITY SCORE: {v_score:3.1f} / 10.0 [{bar_str}]
🏷️ VITALITY CLASSIFICATION:   {v_tier.upper()} ({v_class.capitalize()})
🎭 DIAGNOSTIC ARCHETYPE:     {archetype}
📜 CLINICAL VERDICT:         {verdict}

📊 5-PILLAR MATHEMATICAL BREAKDOWN:
   • Base Starting Score:                {ps.get('base_score', 5.0):+4.1f} pts
   • Pillar 1 (The Captain - Lagnesha):  {ps.get('pillar_1_captain', 0.0):+4.1f} pts
   • Pillar 2 (The Field Placement):     {ps.get('pillar_2_field', 0.0):+4.1f} pts
   • Pillar 3 (Horizon Occupants):       {ps.get('pillar_3_occupants', 0.0):+4.1f} pts
   • Pillar 4 (Sky-Light & Vitality):    {ps.get('pillar_4_skylight', 0.0):+4.1f} pts
   • Pillar 5 (Environmental Enclosure): {ps.get('pillar_5_enclosure', 0.0):+4.1f} pts
   ------------------------------------------------
   = TOTAL COMPOSITE SCORE:               {v_score:4.1f} / 10.0
===========================================================================
```

---

## 🎯 Prominence Diagnosis: Who Speaks Loudest?

> **Top Prominence Verdict:** **{prominence_headline}**  
> {prominence_desc}

In classical Vedic interpretation, we evaluate the 6 natural tiers in hierarchical order. Below is the full six-part dossier:

---

## 📢 Part 1: Tier 1 Report — The Horizon Degree (< 5° Cusp Orb)
*Astrological Archetype: The Megaphone (Immediate Physical Presentation)*

### 1.1 Spatial Geometry & Cusp Contact
* **Campanus Cusp Degree:** {cusp_deg}° ({rising_sign})
* **Planets within 5° Orb:** {cusp_planets_str}

### 1.2 📖 Vault Source Text Collection & Direct Paraphrase
{t1_source_text}

### 1.3 🔍 Interpretive Astrological Synthesis & Living Reality
{t1_synthesis}

### 1.4 📁 Archived Raw Source Notes (In this Folder)
{t1_links}

---

## 🚗 Part 2: Tier 2 Report — The Ascendant Lord (*Lagnesha*)
*Astrological Archetype: The Driver of the Vehicle (Conscious Life Path & Stamina)*

The ruler of the Ascendant is **{lord['planet']}** (*Lagneśa*). Classical texts proclaim (*Phaladeepika 15.9*): *"Whichever house is occupied by the lord of the Ascendant, the well-being of that house is assured."*

### 2.1 Astronomical Coordinates & Field Placement
* **Placement:** House {lord['house_whole_sign']} (Whole Sign) / House {lord['house_campanus']} (Campanus) in **{lord['sign']}** ({lord['degree']}°)
* **Essential Dignity:** **{lord['dignity']}**
* **Kinetic Muscle (Shadbala):** **{lord['shadbala_pct']}%** of required minimum ({'solid, capable stamina' if lord['shadbala_pct'] >= 100 else 'sensitive stamina requiring conscious pacing'})
* **Lajjitadi Feeling State:** {', '.join(lord['avasthas']['lajjitadi']) if lord['avasthas']['lajjitadi'] else 'Balanced'}
* **Conjoining Grahas:** {conjoined_str}

### 2.2 📖 Vault Source Text Collection & Direct Paraphrase
{t2_source_text}

### 2.3 🔍 Interpretive Astrological Synthesis & Living Reality
#### The Domain of Life Investment: House {lord['house_whole_sign']} — {t2_data['house_title']}
{t2_data['house_body']}

#### Sign Environment & Dignity: {lord['sign']} ({lord['dignity']})
{t2_data['sign_body']}

#### Planetary Conjunctions to the Lord
{t2_data['conjunction_body']}

{t2_data['asc_role_body'] if t2_data['asc_role_body'] else ''}

### 2.4 📁 Archived Raw Source Notes (In this Folder)
{t2_links}

---

## ☀️ Part 3: Tier 3 Report — The Sthira Karaka (*Surya* / The Sun)
*Astrological Archetype: The Engine & Battery (Constitutional Reserve & Soul Core)*

The Sun (*Sūrya*) is the eternal *Sthira Karaka* (universal fixed significator) of the 1st House (*Tanu Bhāva*). While the Ascendant Lord (*Lagneśa*) represents the conscious driver making lifestyle choices, the Sun represents the constitutional engine under the hood—governing bone health, recuperative vitality (*Prāṇa*), unshakeable self-worth, and soul conviction.

### 3.1 Astronomical Coordinates & House Domain
* **Field Placement:** House {sun['house_whole_sign']} (Whole Sign) / House {sun['house_campanus']} (Campanus) in **{sun['sign']}** ({sun['degree']}°)
* **Essential Dignity:** **{sun['dignity']}**
* **Directional Strength (*Digbala*):** **{sun['digbala_pct']}%** quota
* **Kinetic Stamina (*Shadbala*):** **{sun['shadbala_pct']}%** quota

### 3.2 📖 Vault Source Text Collection & Direct Paraphrase
{t3_source_text}

### 3.3 🔍 Interpretive Astrological Synthesis & Living Reality
{t3_synthesis}

### 3.4 ⚖️ Karaka vs. Lagneśa Synthesis
{karaka_synthesis}

### 3.5 📁 Archived Raw Source Notes (In this Folder)
{t3_links}

---

## 🌿 Part 4: Tier 4 Report — 1st House Whole-Sign Field Inhabitants
*Astrological Archetype: The Room's Atmosphere (Environmental Background)*

### 4.1 Occupancy Diagnostic
* **Whole-Sign Inhabitants:** {occupancy_str}

### 4.2 📖 Vault Source Text Collection & Direct Paraphrase
{t4_source_text}

### 4.3 🔍 Interpretive Astrological Synthesis & Living Reality
{t4_synthesis}

### 4.4 📁 Archived Raw Source Notes (In this Folder)
{t4_links}

---

## 🔦 Part 5: Tier 5 Report — Direct Aspects & Sky-Light (*Drishti*)
*Astrological Archetype: The High-Beam Headlights (Helpful vs Stressful Rays)*

### 5.1 Mathematical Virupas (Astra Engine)
* **Net Horizon Sky-Light:** **{data['aspect_totals'].get('net', 0.0):+5.2f} Virūpas**
* **Benefic Ray Total:** +{data['aspect_totals'].get('plus', 0.0):.2f} Virūpas
* **Malefic Ray Total:** -{data['aspect_totals'].get('minus', 0.0):.2f} Virūpas

### 5.2 📖 Vault Source Text Collection & Direct Paraphrase
{t5_source_text}

### 5.3 🔍 Interpretive Astrological Synthesis & Living Reality
{t5_synthesis}

### 5.4 📁 Archived Raw Source Notes (In this Folder)
{t5_links}

---

## 🎨 Part 6: Tier 6 Report — Rising Sign (*Rasi*) & Nakshatra
*Astrological Archetype: The Canvas & Mythic Impulse (Elemental Blueprint)*

### 6.1 Astronomical Blueprint
* **Rising Sign:** {rising_sign} ({rising_deg}°) | {meta.get('element')} | {meta.get('modality')}
* **Nakshatra:** {nakshatra} (Pada {pada}) | Swamsa(D9): {swamsa}
* **Nakshatra Rulers:** Lord: {nak_lord} | Sub-Lord: {sub_lord}

### 6.2 📖 Vault Source Text Collection & Direct Paraphrase
{t6_source_text}

### 6.3 🔍 Interpretive Astrological Synthesis & Living Reality
{t6_synthesis}

### 6.4 📁 Archived Raw Source Notes (In this Folder)
{t6_links}

---

## ⚖️ Part 7: Functional Planetary Architecture for this Ascendant

The rising sign of {rising_sign} re-aligns the planetary allegiances for this native:

| Planetary Role | Grahas | Function & Life Manifestation |
| :--- | :--- | :--- |
| **👑 Crown Champion (Yoga Karaka)** | **{fmat['yogakaraka'] if fmat['yogakaraka'] else 'None (Power distributed among allies)'}** | Rules both an angle (Kendra) and a trine (Trikona). The single greatest kinetic ally for success. |
| **🌟 Functional Benefics** | {', '.join(fmat['functional_benefics']) if fmat['functional_benefics'] else 'None'} | Natural allies who protect character, ethics, and smooth life expansion. |
| **⚔️ Functional Troublemakers (Trishadaya)** | {', '.join(fmat['trishadaya_troublemakers']) if fmat['trishadaya_troublemakers'] else 'None'} | Lords of houses 3, 6, and 11. Produce delays, debts, physical friction, and competitive strain. |
| **⚠️ Marakas (Longevity Watch)** | {', '.join(fmat['marakas']) if fmat['marakas'] else 'None'} | Lords of houses 2 and 7; govern bodily transitions and physical boundaries. |

---

## 🧘 Part 8: Master Holistic Synthesis & "Seeing the Person in Front of You"

{part_8_synthesis}

---

*Generated by Astra Engine | Integration of Kala Methodology & Vedic Astrology Vault*
"""
    return md

def main():
    parser = argparse.ArgumentParser(description="Generate complete multi-tier Ascendant Interpretation Report.")
    parser.add_argument("--native", type=str, default="Shivapuri", help="Native name or UUID from database/Charts.jsonl")
    args = parser.parse_args()

    generate_report(args.native)

if __name__ == "__main__":
    main()
