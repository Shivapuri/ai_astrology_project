# AI Agent Instructions for Astra Repository

If you are an AI assistant (like Gemini, Claude, or ChatGPT) reading this file, these are your core instructions and context for working in this repository.

## Project Context
Astra is a dual-engine astrology computation project. It houses two entirely independent astrological frameworks:
1.  **Hellenistic Western Astrology** (Tropical zodiac, Placidus/Whole Sign houses, standard western aspects, classical dignities, and Hermetic Lots)
2.  **Parashari Vedic Astrology / Jyotish** (Sidereal zodiac, Lahiri ayanamsha, Vimshottari Dasha, planetary dignities according to Parashara)

---

## Core Directive: Strict Separation
**DO NOT CONFLATE THE TWO ENGINES.** 
When working on one engine, you must ignore the rules, calculations, and terminologies of the other.

*   When the user asks for "Western" or "Hellenistic" calculations, you must only work within the `/western/` and `/rag/` directories.
*   When the user asks for "Jyotish", "Vedic", or "Parashari" calculations, you must only work within the `/jyotish/` directory and use the `jyotishganit` library.

---

## Western Horoscope RAG Execution & Interpretation Workflow

### 1. Running the Western RAG Pipeline Shell Script
To generate a Western horoscope and perform Retrieval-Augmented Generation (RAG) against the local classical vector database (`rag/chroma_astrology_db`), execute the shell script [`run_western_rag.sh`](file:///Users/hajnaljanos/PycharmProjects/astra/run_western_rag.sh):

```bash
./run_western_rag.sh [Name] [Year] [Month] [Day] [Hour] [Minute] [City] [CountryCode]
```

*Example for Georgsmarienhütte, Germany (November 10, 1983 at 04:20 AM):*
```bash
./run_western_rag.sh "User" 1983 11 10 4 20 "Georgsmarienhütte" "DE"
```

Alternatively, invoke the MCP server tools in [`rag/astrology_mcp_server.py`](file:///Users/hajnaljanos/PycharmProjects/astra/rag/astrology_mcp_server.py):
* `calculate_birth_chart(name, year, month, day, hour, minute, city, country_code)`
* `query_ancient_texts(query)`

---

### 2. Formulating Easy-to-Understand Interpretations

When presenting the generated Western chart and RAG insights to the user, follow these guidelines:

1. **Sect Analysis**: Explain whether the chart is a **Day Chart** or **Night Chart** (based on whether the Sun is above or below the horizon) and which luminary (Sun or Moon) leads the chart.
2. **Ascendant & Chart Ruler**: Explain the **Ascendant** (the rising sign) and its ruling planet, including its house position and **Essential Dignity** (Domicile, Exaltation, Detriment, Fall, or Peregrine).
3. **Planetary Placements & Solar Phasis**: Detail all 7 traditional planets (Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn) by sign, Whole Sign House, dignity, and solar phasis (e.g. Cazimi, Combust, Under the Beams).
4. **Major Whole Sign Aspects**: Interpret planetary relationships (conjunctions, sextiles, squares, trines, oppositions) based on sign distance.
5. **Hermetic Lots**: Interpret key mathematical points, specifically the **Lot of Fortune** (material well-being/body) and **Lot of Spirit** (intellect/purpose/career).

---

### 3. Explanation Style & Communication Rules
* **Explain simply and intuitively**: Avoid overwhelming technical jargon. Use everyday analogies and clear English.
* **Introduce technical terms incrementally**: On first introduction of any technical term, immediately provide a brief, easy-to-understand definition in parentheses.
  * *Example*: **Ascendant** *(the zodiac sign rising on the eastern horizon at birth, representing your core identity)*.
  * *Example*: **Domicile** *(when a planet is in the sign it naturally rules, acting like a king in their own castle)*.
  * *Example*: **Combust** *(when a planet is so close to the Sun that its visible rays are hidden)*.
* **Grounding**: Base all interpretations strictly on the retrieved classical RAG context from ancient authorities (Ptolemy, Vettius Valens, Dorotheus of Sidon) and the generated [`western/chart_context.json`](file:///Users/hajnaljanos/PycharmProjects/astra/western/chart_context.json).
* **Verify Cache & Downloads**: Do not repeatedly download astronomical dataset files (`.dat`, `.bsp`). Use local cached files (`hip_main.dat`, `de421.bsp`).

---

## Technical Details & Constraints
* **Vedic Engine (`/jyotish/`)**: Uses `jyotishganit` and `skyfield`. Relies on cached NASA JPL DE421 ephemeris and Hipparcos catalog (`hip_main.dat`).
* **Western Engine (`/western/`)**: Uses `kerykeion` and `swisseph` for tropical calculations and Whole Sign Houses.
* **RAG Vector Base (`/rag/`)**: Uses Chroma DB in `rag/chroma_astrology_db/` with HuggingFace embeddings (`all-MiniLM-L6-v2`) for local retrieval.

