# AI Agent Instructions for Astra Repository

If you are an AI assistant (like Gemini, Claude, or ChatGPT) reading this file, these are your core instructions and context for working in this repository.

## Project Context
Astra is a dual-engine astrology computation project. It houses two entirely independent astrological frameworks:
1.  **Hellenistic Western Astrology** (Tropical zodiac, Placidus/Whole Sign houses, standard western aspects, classical dignities, and Hermetic Lots)
2.  **Parashari Vedic Astrology / Jyotish** (Sidereal zodiac, Lahiri ayanamsha, Vimshottari Dasha, planetary dignities according to Parashara)

---

## Core Directive: Strict Engine & Database Firewall
**DO NOT CONFLATE THE TWO ENGINES. YOU MUST MAINTAIN ABSOLUTE PARADIGM ISOLATION.** 
Astra houses two entirely independent astrological frameworks. When working on a chart, you must pick ONE system and strictly isolate your tools, prompts, and terminology.

**1. The Western Framework (Tropical, Modern Psychological & Hellenistic Structural)**
* **Domain:** `/western/`, `/rag/modern_rag_data/`, and `/rag/structural_rag_data/`
* **Calculations Tool:** You MUST ONLY use `calculate_birth_chart`.
* **Vector Database Tools:** You MUST ONLY use `query_modern_astrology_books` (queries `chroma_modern_db` and `chroma_structural_db`).
* **Rule:** NEVER mention Vimshottari Dashas, Nakshatras, or Jyotish dignities.

**2. The Vedic / Jyotish Framework (Sidereal, Parashari)**
* **Domain:** `/jyotish/` and `/rag/jyotish_rag_data/`
* **Calculations Tool:** You MUST ONLY use `calculate_vedic_chart`.
* **Vector Database Tool:** You MUST ONLY use `query_vedic_astrology_books` (queries `chroma_jyotish_db`).
* **Rule:** NEVER mention outer planets (Uranus, Neptune, Pluto), Tropical house rules, or psychological frameworks like Noel Tyl/Demetra George.

---

## Western Horoscope RAG Execution & Interpretation Workflow

### 1. Running the Western Multi-Agent Headless Pipeline
To generate a Western horoscope and run the complete 3-Stage Headless Multi-Agent Pipeline against the domain-isolated vector databases (`rag/chroma_structural_db` for Agent 1 and `rag/chroma_modern_db` for Agent 2), execute [`scripts/run_western_pipeline.py`](file:///Users/hajnaljanos/PycharmProjects/astra/scripts/run_western_pipeline.py):

```bash
python scripts/run_western_pipeline.py --name "User" --year 1983 --month 11 --day 10 --hour 4 --minute 20 --city "Georgsmarienhütte" --country "DE"
```

Alternatively, invoke the MCP server tools in [`rag/western_mcp_server.py`](file:///Users/hajnaljanos/PycharmProjects/astra/rag/western_mcp_server.py):
* `calculate_birth_chart(name, year, month, day, hour, minute, city, country_code)`
* `query_modern_astrology_books(query)`

---

### 2. Chart Interpretation Instructions
For AI agent instructions regarding chart interpretation, strictly follow the XML prompt files located in the `/prompts/` directory (`agent1_structural.xml`, `agent2_psychological.xml`, and `agent3_synthesizer.xml`). Do not use outdated inline prompts.

---

## Vedic Horoscope RAG Execution & Interpretation Workflow

### 1. Running Vedic Calculations & Vector Database Queries
To generate a mathematically precise Parashari Vedic horoscope (using sidereal calculations and True Chitra Paksha / Lahiri ayanamsha) and perform Retrieval-Augmented Generation (RAG) against the local classical Vedic vector database (`rag/chroma_jyotish_db`), invoke the MCP server tools in [`rag/jyotish_mcp_server.py`](file:///Users/hajnaljanos/PycharmProjects/astra/rag/jyotish_mcp_server.py):
* `calculate_vedic_chart(name, year, month, day, hour, minute, latitude, longitude, timezone_offset)`
* `query_vedic_astrology_books(query)`

Alternatively, execute the Python calculation generator directly from [`jyotish/generate_jyotish.py`](file:///Users/hajnaljanos/PycharmProjects/astra/jyotish/generate_jyotish.py) to populate [`jyotish/vedic_context.json`](file:///Users/hajnaljanos/PycharmProjects/astra/jyotish/vedic_context.json).

*Example parameters for Georgsmarienhütte, Lower Saxony, Germany (November 10, 1983 at 04:20 AM):*
* `name="User"`, `year=1983`, `month=11`, `day=10`, `hour=4`, `minute=20`, `latitude=52.2045`, `longitude=8.0494`, `timezone_offset=1.0`

---

### 2. Chart Interpretation Instructions
For AI agent instructions regarding chart interpretation, strictly follow the XML prompt files located in the `/prompts/` directory. Do not use outdated inline prompts.


---

## Core Directive: QA & Testing Standards
Every substantial new feature, architectural change, or data ingestion pipeline added to this repository MUST be accompanied by an automated test script. 
1. Mathematical Engine updates must be verified against Swiss Ephemeris / Jyotishganit baseline scripts (e.g., `bulk_test_engine.py`).
2. Vector Database (RAG) updates must be verified for both functionality (does it return text?) and RELEVANCE (does the text contain the correct astrological concepts?) using the RAG Quality Evaluation suite. 
Do not commit major logic changes without providing a way to programmatically test them.

---

## Technical Details & Constraints
* **Vedic Engine (`/jyotish/`)**: Uses `jyotishganit` and `skyfield` for sidereal computations. Relies on cached NASA JPL DE421 ephemeris and Hipparcos catalog (`hip_main.dat`).
* **Western Engine (`/western/`)**: Uses `kerykeion` and `swisseph` for tropical calculations and Whole Sign Houses.
* **RAG Vector Bases (`/rag/`)**: 
  * **Western DBs**: Uses dual-camp Chroma DBs (`rag/chroma_structural_db/` for Demetra George's Hellenistic mechanics and `rag/chroma_modern_db/` for Hand, Arroyo, and Marks) with HuggingFace embeddings (`all-MiniLM-L6-v2`).
  * **Vedic DB**: Uses Chroma DB in `rag/chroma_jyotish_db/` with HuggingFace embeddings (`all-MiniLM-L6-v2`) for local retrieval of classical BPHS shlokas and VedAstro rules (`rag/fetch_jyotish_data.py` & `rag/build_jyotish_rag.py`).



