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
* `query_modern_astrology_books(query)`

---

### 2. Modern Psychological RAG & Chain of Thought (CoT) Workflow

When performing chart readings, follow the 4-step ReAct workflow embedded in the FastMCP server instructions:
1. **Step 1 (Calculate Chart)**: Call `calculate_birth_chart` to get exact mathematical placements in JSON format.
2. **Step 2 (Identify Placements)**: Isolate the top 3 dominant placements (e.g. Sun sign/house, Moon sign/house, Ascendant ruler).
3. **Step 3 (Research Books)**: Call `query_modern_astrology_books` 1 to 3 times to retrieve psychological interpretations.
4. **Step 4 (Synthesize)**: Blend mathematical JSON data with modern psychological literature for an empathetic, step-by-step reading.

---

### 3. Explanation Style & Communication Rules
* **Explain simply and intuitively**: Avoid overwhelming technical jargon. Use everyday analogies and clear English.
* **Introduce technical terms incrementally**: On first introduction of any technical term, immediately provide a brief, easy-to-understand definition in parentheses.
  * *Example*: **Ascendant** *(the zodiac sign rising on the eastern horizon at birth, representing your core identity)*.
  * *Example*: **Domicile** *(when a planet is in the sign it naturally rules, acting like a king in their own castle)*.
  * *Example*: **Combust** *(when a planet is so close to the Sun that its visible rays are hidden)*.
* **Dominant Zodiac Sign Overviews**: Before analyzing specific house placements or aspects, always provide a general overview of the characteristics, element, ruling planet, and archetypal theme of the chart's dominant zodiac signs (e.g., explaining Scorpio as an archetypal sign before interpreting Sun conjunct Saturn in Scorpio).
* **The Extended Psychological Lens**: Keep your beautiful formatting (Core Architecture, Dominant Placements, Strengths, Summary Checklist), but ensure you always spotlight:
  1. **The Pain Body**: Where they hold trauma or emotional armor (using debilitated planets or the Moon).
  2. **Socialization**: How they make friends and open up (using Venus/11th House).
  3. **Conflict Resolution**: How they fight or protect boundaries (using Mars and hard aspects).
* **Grounding**: Base interpretations on modern psychological literature retrieved from `rag/chroma_astrology_db` and [`western/chart_context.json`](file:///Users/hajnaljanos/PycharmProjects/astra/western/chart_context.json).
* **Verify Cache & Downloads**: Do not repeatedly download astronomical dataset files (`.dat`, `.bsp`). Use local cached files (`hip_main.dat`, `de421.bsp`).

---

## Vedic Horoscope RAG Execution & Interpretation Workflow

### 1. Running Vedic Calculations & Vector Database Queries
To generate a mathematically precise Parashari Vedic horoscope (using sidereal calculations and True Chitra Paksha / Lahiri ayanamsha) and perform Retrieval-Augmented Generation (RAG) against the local classical Vedic vector database (`rag/chroma_jyotish_db`), invoke the MCP server tools in [`rag/astrology_mcp_server.py`](file:///Users/hajnaljanos/PycharmProjects/astra/rag/astrology_mcp_server.py):
* `calculate_vedic_chart(name, year, month, day, hour, minute, latitude, longitude, timezone_offset)`
* `query_vedic_astrology_books(query)`

Alternatively, execute the Python calculation generator directly from [`jyotish/generate_jyotish.py`](file:///Users/hajnaljanos/PycharmProjects/astra/jyotish/generate_jyotish.py) to populate [`jyotish/vedic_context.json`](file:///Users/hajnaljanos/PycharmProjects/astra/jyotish/vedic_context.json).

*Example parameters for Georgsmarienhütte, Lower Saxony, Germany (November 10, 1983 at 04:20 AM):*
* `name="User"`, `year=1983`, `month=11`, `day=10`, `hour=4`, `minute=20`, `latitude=52.2045`, `longitude=8.0494`, `timezone_offset=1.0`

---

### 2. Parashari Jyotish RAG & Chain of Thought (CoT) Workflow

When performing Vedic astrology chart readings, strictly adhere to the 4-step ReAct workflow embedded in the FastMCP server instructions and [`jyotish/vedic_agent_prompt.txt`](file:///Users/hajnaljanos/PycharmProjects/astra/jyotish/vedic_agent_prompt.txt):
1. **Step 1 (Calculate Vedic Chart)**: Call `calculate_vedic_chart` to compute exact sidereal planetary degrees, Panchanga, D1 Rasi Chart, D9 Navamsa Chart, and Vimshottari Dasha timeline in JSON format.
2. **Step 2 (Internal Analysis & Target Identification)**: Perform a structured internal audit of:
   * **Lagna & Lagna Pati**: Ascendant sign/nakshatra and the position/dignity of its ruling lord in D1 and D9.
   * **Chandra (Moon) & Manas**: Sidereal sign, exact Nakshatra, Pada, Nakshatra Deity, and mental orientation.
   * **Divisional Strength (D1 vs D9)**: Vargottama planets (same zodiac sign in D1 & D9) or Neecha Bhanga (cancellation of debilitation) that unlock hidden strength and soul evolution.
   * **Vimshottari Dasha Timeline**: Identify the birth Dasha and the currently running Mahadasha, Antardasha, and Pratyantardasha periods.
3. **Step 3 (Research Classical Vedic Books)**: Call `query_vedic_astrology_books` 1 to 3 times to retrieve authoritative classical shlokas (Brihat Parashara Hora Shastra, Brihat Jataka) and VedAstro rules from `rag/chroma_jyotish_db`.
4. **Step 4 (Synthesize Empowering 4-Part Reading)**: Blend classical RAG retrievals with exact mathematical calculations to construct an intuitive, empowering 4-part reading focusing on Karma, Dharma, and Timelines, translating ancient fatalistic language into modern constructive self-knowledge.

---

### 3. Vedic Explanation Style & Communication Rules
* **Explain simply and intuitively**: Avoid overwhelming technical or Sanskrit jargon without immediate clarification. Frame concepts using everyday analogies and plain English (similar to explaining to a friendly beginner).
* **Introduce Sanskrit / Jyotish terms incrementally**: On first introduction of any technical Vedic term, immediately provide a brief, easy-to-understand definition in parentheses or a short sentence.
  * *Example*: **Lagna** *(the zodiac sign rising on the eastern horizon at birth, representing your physical orientation in the world and core life path)*.
  * *Example*: **Nakshatra** *(one of 27 lunar constellations along the zodiac that reveal emotional reflexes, inner mindsets, and subconscious memory)*.
  * *Example*: **Vargottama** *(when a planet retains the exact same zodiac sign in both the birth chart and the spiritual D9 Navamsa chart, giving it tremendous steadfast strength)*.
  * *Example*: **Vimshottari Dasha** *(the classic planetary period system that acts as an internal timer, unlocking major karmic chapters and life focus areas over a 120-year timeline)*.
* **Dominant Sidereal Sign & Nakshatra Overviews**: Before analyzing houses or planetary aspects (*Graha Drishti*), always provide a foundational overview of the archetypal nature, element, symbol, and emotional themes of the native's Lagna and Moon Nakshatra.
* **The Karmic & Dharmic Lens**: Translate classical texts into empowering guidance organized across 4 essential areas:
  1. **Lagna & Physical Identity (D1 Rasi)**: Core vitality, motivation, health tendencies, and physical interactions with the real world.
  2. **Chandra & Mental Conditioning (Mind & Emotions)**: Subconscious mental landscape, emotional nutrition, and maintaining internal peace (*Manas*).
  3. **D9 Navamsa & Soul Purpose (Dharma & Destiny)**: Spiritual character maturation, relationship alignment, and inner alignment with personal duty (*Dharma*).
  4. **Vimshottari Dasha Timeline & Karmic Evolution**: Timing of current life chapters, opportunities, challenges, and constructive remedies (*Upayas*) or ethical habits for navigating active cycles.
* **Strict Engine Separation**: Never introduce Western outer planets (Uranus, Neptune, Pluto) or Tropical house rules into a Jyotish analysis. Rely solely on Parashari rules and Whole Sign Graha Drishti.
* **Grounding**: Ensure interpretations are solidly grounded in authenticated classical rules retrieved from `rag/chroma_jyotish_db` and the data in [`jyotish/vedic_context.json`](file:///Users/hajnaljanos/PycharmProjects/astra/jyotish/vedic_context.json).

---

## Technical Details & Constraints
* **Vedic Engine (`/jyotish/`)**: Uses `jyotishganit` and `skyfield` for sidereal computations. Relies on cached NASA JPL DE421 ephemeris and Hipparcos catalog (`hip_main.dat`).
* **Western Engine (`/western/`)**: Uses `kerykeion` and `swisseph` for tropical calculations and Whole Sign Houses.
* **RAG Vector Bases (`/rag/`)**: 
  * **Western DB**: Uses Chroma DB in `rag/chroma_astrology_db/` with HuggingFace embeddings (`all-MiniLM-L6-v2`) for local retrieval of modern literature.
  * **Vedic DB**: Uses Chroma DB in `rag/chroma_jyotish_db/` with HuggingFace embeddings (`all-MiniLM-L6-v2`) for local retrieval of classical BPHS shlokas and VedAstro rules (`rag/fetch_jyotish_data.py` & `rag/build_jyotish_rag.py`).

