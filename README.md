# Astra: Dual-Engine Astrology Project

Astra is a comprehensive astrology computing project that houses two completely independent, production-grade horoscope engines in a single repository. 

The project is strictly divided into two distinct astrological disciplines:
1.  **Hellenistic Western Astrology**
2.  **Vedic Astrology (Parashari Jyotish)**

## Repository Structure

To maintain clean architecture and prevent any conflation of rules or terminology, the engines and their supporting infrastructure are separated into top-level directories:

*   `/western/` - The Hellenistic Western engine. Contains chart generation logic, house system calculations, and the 10,000-chart QA stress testing pipeline (`bulk_test_engine.py`).
*   `/jyotish/` - The Vedic (Jyotish) engine. Powered by the `jyotishganit` library and Skyfield. Contains calculation logic for sidereal astrology, Vimshottari Dasha, and its own dedicated testing pipeline (`bulk_test_jyotish.py`).
*   `/rag/` - Supporting infrastructure for Retrieval-Augmented Generation, AI interpreters, and knowledge base fetching.
*   `/cache/` - Shared storage for heavy astronomical data files, such as the NASA JPL DE421 ephemeris and the Hipparcos star catalog (`hip_main.dat`), enabling offline computation.

## Setup and Installation

This project uses Python 3.12.

1.  Clone the repository and navigate into it.
2.  Activate the virtual environment:
    ```bash
    source venv/bin/activate
    ```
3.  Ensure you have the required dependencies (e.g., `skyfield`, `jyotishganit`).

## Testing and Execution

Both engines feature robust, automated QA pipelines capable of stress-testing thousands of charts globally, alongside a 3-Stage Headless Multi-Agent Pipeline for Western astrology.

**Run the Western 3-Stage Headless Multi-Agent Pipeline:**
```bash
python scripts/run_western_pipeline.py --name "User" --year 1983 --month 11 --day 10 --hour 4 --minute 20 --city "Georgsmarienhütte" --country "DE"
```

**Test Vector Database Retrieval Quality:**
```bash
python tests/test_rag_quality.py
```

**Bulk Stress Test the Western Engine (10,000 Charts):**
```bash
python western/bulk_test_engine.py
```

**Bulk Stress Test the Jyotish Engine (10,000 Charts):**
```bash
python jyotish/bulk_test_jyotish.py
```


