# Western Astrology Multi-Agent Pipeline Architecture & Firewall Rules

## Core Directive: Strict Engine & Database Firewall
Astra houses two entirely independent astrological frameworks:
1. **Hellenistic Western Astrology** (Tropical zodiac, Placidus/Whole Sign houses, standard western aspects, classical dignities, Hermetic Lots, Dodecatemoria, Planetary Phasis).
2. **Parashari Vedic Astrology / Jyotish** (Sidereal zodiac, Lahiri ayanamsha, Vimshottari Dasha, planetary dignities according to Parashara).

### Absolute Paradigm Isolation Rules for Western Framework
* **Domain:** `/western/`, `/rag/modern_rag_data/`, and `/rag/structural_rag_data/`
* **Calculations Engine:** You MUST ONLY use `generate_ai_json` from `western/generate_chart.py`.
* **Vector Database Tools:** You MUST ONLY use `chroma_structural_db` (Demetra George Hellenistic mechanics) and `chroma_modern_db` (Noel Tyl, Arroyo, Hand modern psychological astrology).
* **Firewall Rule:** NEVER mention Vimshottari Dashas, Nakshatras, or Jyotish dignities.

---

## 3-Stage Headless Multi-Agent Pipeline Execution Workflow

The Western pipeline ([`scripts/run_western_pipeline.py`](file:///Users/hajnaljanos/PycharmProjects/astra/scripts/run_western_pipeline.py)) executes in an 8-step sequence:

```
[Step 1: Python Engine] ──> Calculates Chart JSON + HTML Dashboard
[Step 2: Vector DB RAG] ──> Extracts Structural (Agent 1) & Modern Psychological (Agent 2) Excerpts
[Step 3: Agent 1 (AGY)] ──> Structural & Hellenistic Profiler (Demetra George Framework)
[Step 4: Agent 2 (AGY)] ──> Psychological & Aspect Profiler (Noel Tyl Framework)
[Step 5: Agent 3 (AGY)] ──> Master Astrologer Synthesizer (Narrative & Day-in-the-Life Reality)
[Step 6: Output Saving]  ──> Saves Full Reading Markdown
[Step 7: PDF Generator] ──> Compiles Publication-Grade PDF
[Step 8: TTS Audio]      ──> Synthesizes Supertonic Vocal Audio Narration (WAV & MP3)
```

---

## Pipeline Prompts Sitemap
1. **`01_Western_Astrology_Master_Methodology.md`**: Theoretical foundation integrating Noel Tyl and Demetra George.
2. **`02_Agent1_Structural_Hellenistic_Profiler_Prompt.md`**: System role and instructions for Agent 1.
3. **`03_Agent2_Psychological_Profiler_Prompt.md`**: System role and instructions for Agent 2.
4. **`04_Agent3_Master_Astrologer_Synthesizer_Prompt.md`**: System role and instructions for Agent 3.
