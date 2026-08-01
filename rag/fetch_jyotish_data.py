"""
Jyotish Data Fetcher
Autonomously fetches authentic classical Vedic astrology texts from WisdomLib
and open-source Jyotish dataset interpretations from VedAstro into /rag/jyotish_rag_data/
with OCR noise cleaning, smart sentence line-wrap unwrapping, numerical sorting, and structured formatting.
"""

import os
import sys
import re
import json
import xml.etree.ElementTree as ET
import requests
import unicodedata
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "jyotish_rag_data")
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def clean_and_format_text(text: str) -> str:
    """
    Normalizes Unicode text, removes WisdomLib OCR page noise & UI warnings,
    rejoins broken line-wrapped words/sentences, and formats clean paragraphs.
    """
    if not text:
        return ""
    
    # 1. Normalize Unicode (NFKD)
    normalized = unicodedata.normalize("NFKD", text)
    
    # 2. Remove OCR page warning blocks and UI notices
    cleaned = re.sub(
        r'Warning!\s*Page\s*nr\.\s*\d+.*?original\s*PDF\.?', 
        '', 
        normalized, 
        flags=re.DOTALL | re.IGNORECASE
    )
    
    # 3. Filter out specific repetitive UI boilerplate
    noise_patterns = [
        r'Buy\s+relevant\s+books',
        r'Support\s+me\s+on\s+Patreon',
        r'Click\s+the\s+page\s+link\s+to\s+verify.*',
        r'Last\s+Updated:\s*\d+\s+\w+,\s*\d+'
    ]
    for pat in noise_patterns:
        cleaned = re.sub(pat, '', cleaned, flags=re.IGNORECASE)

    # 4. Filter raw lines and remove standalone UI tokens
    raw_lines = [l.strip() for l in cleaned.splitlines() if l.strip()]
    filtered_lines = []
    for line in raw_lines:
        if line.lower() in ['resources', 'buddhism', 'hinduism', 'jainism', 'jyotisha', 'sanskrit', 'next >', '< previous']:
            continue
        filtered_lines.append(line)

    # 5. Smart line-unwrapping to fix awkward line breaks inside sentences
    formatted_paragraphs = []
    curr = ""
    
    for line in filtered_lines:
        if not curr:
            curr = line
            continue
            
        # Rejoin hyphenated word split across lines (e.g. "pranahani-\nbhupalatvam")
        if curr.endswith("-") and not curr.endswith(" -"):
            curr = curr[:-1] + line
        # If current line ends with sentence punctuation or verse end OR next line is a header/verse delimiter
        elif curr.endswith(("||", "|", ".", "!", "?", ":")) or re.match(r'^(===|Sloka|Verse|Adhyaya|Chapter|\|\|)', line, re.IGNORECASE):
            formatted_paragraphs.append(curr)
            curr = line
        else:
            # Join unwrapped sentence fragment cleanly with space
            curr = curr + " " + line
            
    if curr:
        formatted_paragraphs.append(curr)
        
    return "\n\n".join(formatted_paragraphs)


def parse_section_key(title: str, slug: str):
    """Extracts (slug, chapter_num, verse_num) for deterministic numerical sorting."""
    m_verse = re.search(r'Verse\s+(\d+)\.(\d+)', title, re.IGNORECASE)
    if m_verse:
        return (slug, int(m_verse.group(1)), int(m_verse.group(2)))
    
    m_chap = re.search(r'(?:Chapter|Adhyaya|Adh\.?)\s+(\d+)(?:[,\s]+Verse\s+(\d+))?', title, re.IGNORECASE)
    if m_chap:
        c_num = int(m_chap.group(1))
        v_num = int(m_chap.group(2)) if m_chap.group(2) else 0
        return (slug, c_num, v_num)
        
    m_num = re.search(r'(\d+)\.(\d+)', title)
    if m_num:
        return (slug, int(m_num.group(1)), int(m_num.group(2)))

    return (slug, 999, 999)


def fetch_single_doc(doc_url: str, slug: str):
    """Scrapes a single WisdomLib document page and extracts clean text content."""
    try:
        d_resp = requests.get(doc_url, headers=HEADERS, timeout=8)
        if d_resp.status_code != 200:
            return None
        
        d_soup = BeautifulSoup(d_resp.text, "html.parser")
        raw_title = d_soup.title.string.strip() if d_soup.title else doc_url.split("/")[-1]
        
        # Clean title header (remove site suffixes)
        clean_title = re.sub(r'\s*\[.*?\]', '', raw_title).strip()
        
        content_div = d_soup.find(id="scontent") or d_soup.find(class_="chapter-content")
        if not content_div:
            content_div = d_soup.find("article") or d_soup.find("main")
        
        if content_div:
            raw_paragraph = content_div.get_text("\n").strip()
            cleaned_p = clean_and_format_text(raw_paragraph)
            if len(cleaned_p) > 30:
                key = parse_section_key(clean_title, slug)
                
                # Format clean, human-readable section header
                book_name = slug.replace("-", " ").title()
                formatted_header = f"=== BOOK: {book_name} | SECTION: {clean_title} ==="
                
                return {
                    "key": key,
                    "content": f"{formatted_header}\n\n{cleaned_p}\n"
                }
    except Exception:
        pass
    return None


def fetch_wisdomlib_texts(output_filepath: str):
    """
    Scrapes classical Jyotish books from WisdomLib (BPHS, Brihat Jataka, Phaladeepika).
    Parses, cleans OCR noise, fixes line wrapping, sorts sections numerically, and saves to file.
    """
    print("--- Starting Enhanced WisdomLib Classical Vedic Scraper ---", flush=True)
    
    book_urls = [
        "https://www.wisdomlib.org/hinduism/book/brihat-parasara-hora-shastra",
        "https://www.wisdomlib.org/hinduism/book/brihat-jataka-by-varahamihira-sanskrit-english",
        "https://www.wisdomlib.org/hinduism/book/phaladeepika-by-mantreswara-text-and-translation",
        "https://www.wisdomlib.org/hinduism/book/brihat-samhita"
    ]
    
    scraped_sections = []
    
    for book_url in book_urls:
        slug = book_url.split("/")[-1]
        print(f"Checking WisdomLib book: {slug}...", flush=True)
        try:
            resp = requests.get(book_url, headers=HEADERS, timeout=10)
            if resp.status_code != 200:
                print(f"  -> Skipping {slug} (Status code: {resp.status_code})", flush=True)
                continue
            
            soup = BeautifulSoup(resp.text, "html.parser")
            doc_links = []
            for a in soup.find_all("a", href=True):
                href = a["href"]
                if "/d/doc" in href and slug in href:
                    full_link = href if href.startswith("http") else f"https://www.wisdomlib.org{href}"
                    if full_link not in doc_links:
                        doc_links.append(full_link)
            
            print(f"  -> Found {len(doc_links)} document links for {slug}. Fetching content...", flush=True)
            
            target_docs = doc_links[:60]
            with ThreadPoolExecutor(max_workers=8) as executor:
                futures = [executor.submit(fetch_single_doc, url, slug) for url in target_docs]
                for future in as_completed(futures):
                    result = future.result()
                    if result:
                        scraped_sections.append(result)
                        
        except Exception as err:
            print(f"  -> Error fetching book {slug}: {err}", flush=True)
            continue

    if not scraped_sections:
        print("Warning: No paragraphs scraped from WisdomLib. Creating fallback context.", flush=True)
        fallback_entry = {
            "key": ("fallback", 0, 0),
            "content": (
                "=== BOOK: Brihat Parashara Hora Shastra | SECTION: Core Principles ===\n\n"
                "Classical Parashari Principles dictate that the Lagna represents core destiny, "
                "the Moon nakshatra and pada reveal emotional karma, and running Vimshottari Dasha "
                "dictates active karmic periods."
            )
        }
        scraped_sections.append(fallback_entry)

    # Sort sections numerically by (slug, chapter_number, verse_number)
    scraped_sections.sort(key=lambda item: item["key"])
    
    formatted_contents = [sec["content"] for sec in scraped_sections]
    full_text = "\n\n".join(formatted_contents)
    
    with open(output_filepath, "w", encoding="utf-8") as f:
        f.write(full_text)
    
    print(f"Successfully saved {len(formatted_contents)} numerically sorted, line-unwrapped & cleaned sections to {output_filepath}", flush=True)


def fetch_vedastro_data(output_filepath: str):
    """
    Fetches open-source Jyotish datasets from VedAstro GitHub repository.
    Parses JSON and XML dataset files into clean, structured interpretation text.
    """
    print("--- Starting VedAstro Open-Source Data Fetcher ---", flush=True)
    
    urls = {
        "bvraman_horoscope": "https://raw.githubusercontent.com/VedAstro/VedAstro/master/HuggingFace/alpaca_bvraman_horoscope_data.json",
        "event_data": "https://raw.githubusercontent.com/VedAstro/VedAstro/master/Library/XMLData/EventDataList.xml",
        "horoscope_data": "https://raw.githubusercontent.com/VedAstro/VedAstro/master/Library/XMLData/HoroscopeDataList.xml"
    }
    
    formatted_entries = []
    
    # 1. Fetch Alpaca B.V. Raman Horoscope JSON Data
    try:
        print("Fetching B.V. Raman Horoscope Dataset...", flush=True)
        r = requests.get(urls["bvraman_horoscope"], headers=HEADERS, timeout=10)
        if r.status_code == 200:
            json_data = r.json()
            for item in json_data:
                inst = item.get("instruction", "").strip()
                inp = item.get("input", "").strip()
                out = item.get("output", "").strip()
                
                context_str = f"Rule/Placement: {inst}"
                if inp:
                    context_str += f" ({inp})"
                
                entry = f"VEDASTRO HOROSCOPE RULE: {context_str}\nInterpretation: {out}"
                formatted_entries.append(clean_and_format_text(entry))
            print(f"  -> Added {len(json_data)} B.V. Raman horoscope rules.", flush=True)
    except Exception as e:
        print(f"  -> Error fetching B.V. Raman JSON: {e}", flush=True)

    # 2. Fetch Event Data List XML
    try:
        print("Fetching VedAstro Event Data XML...", flush=True)
        r = requests.get(urls["event_data"], headers=HEADERS, timeout=10)
        if r.status_code == 200:
            root = ET.fromstring(r.content)
            events = root.findall("Event")
            for ev in events:
                name = ev.findtext("Name", "").strip()
                nature = ev.findtext("Nature", "").strip()
                desc = ev.findtext("Description", "").strip()
                if name and desc:
                    entry = f"VEDASTRO ASTROLOGICAL EVENT: {name} [Nature: {nature}]\nDescription: {desc}"
                    formatted_entries.append(clean_and_format_text(entry))
            print(f"  -> Added {len(events)} VedAstro event rules.", flush=True)
    except Exception as e:
        print(f"  -> Error fetching Event Data XML: {e}", flush=True)

    # 3. Fetch Horoscope Data List XML
    try:
        print("Fetching VedAstro Horoscope Data XML...", flush=True)
        r = requests.get(urls["horoscope_data"], headers=HEADERS, timeout=10)
        if r.status_code == 200:
            root = ET.fromstring(r.content)
            horoscopes = root.findall("Horoscope")
            for h in horoscopes:
                name = h.findtext("Name", "").strip()
                desc = h.findtext("Description", "").strip()
                if name and desc:
                    entry = f"VEDASTRO HOROSCOPE COMBINATION: {name}\nDescription: {desc}"
                    formatted_entries.append(clean_and_format_text(entry))
            print(f"  -> Added {len(horoscopes)} VedAstro horoscope combinations.", flush=True)
    except Exception as e:
        print(f"  -> Error fetching Horoscope Data XML: {e}", flush=True)

    if not formatted_entries:
        print("Warning: No entries retrieved from VedAstro. Adding fallback data.", flush=True)
        formatted_entries.append(
            "VEDASTRO INTERPRETATION RULE: Sun in 10th House\n"
            "Interpretation: Gives administrative authority, high career visibility, and leadership karma."
        )

    full_text = "\n\n".join(formatted_entries)
    with open(output_filepath, "w", encoding="utf-8") as f:
        f.write(full_text)
        
    print(f"Successfully saved {len(formatted_entries)} interpretation entries to {output_filepath}", flush=True)


def main():
    print("=== Phase 1: Ingesting Authentic Jyotish Texts & Datasets ===", flush=True)
    os.makedirs(DATA_DIR, exist_ok=True)
    
    wisdomlib_path = os.path.join(DATA_DIR, "bphs_wisdomlib.txt")
    vedastro_path = os.path.join(DATA_DIR, "vedastro_interpretations.txt")
    
    fetch_wisdomlib_texts(wisdomlib_path)
    fetch_vedastro_data(vedastro_path)
    
    print("=== Phase 1 Complete! Text files ready in /rag/jyotish_rag_data/ ===", flush=True)


if __name__ == "__main__":
    main()
