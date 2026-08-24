# Jyotish Engine AI Guardrails (MANDATORY)

If you are an AI modifying or adding files in this directory, you **MUST** adhere to the following:

## 0. THE SANSKRIT VECTOR DATABASE (CRITICAL)
We have a local SQLite vector database containing the main Sanskrit astrological scriptures (BPHS, Jataka Parijata, Phaladeepika, etc.). 
**Every agent must use this database to find original Sanskrit quotes to vouch for the correctness of their calculations.**
To query the database, run the provided python script via the terminal:
`python3 /Users/hajnaljanos/PycharmProjects/astra/jyotish/scripture_db.py search <keyword>`
You can also list chapters and read specific verses to extract the exact Shlokas and their English/ITRANS transliterations.

## 1. Feature Integration Standard (The 4-Part Structure)
Whenever a **new astrological feature** (such as Shad Bala, Ishta/Kashta Phala, Sphuta Drishti, etc.) is integrated, it must follow this exact format:

1. **Separate Python File:** Each distinct mathematical or astrological system must live in its own isolated `.py` file (or subfolder, similar to `avasthas/`).
2. **Twin Markdown Documentation:** Every `.py` file must be accompanied by a matching `.md` file (e.g., `shadbala.md`). This Markdown file MUST contain:
   - **Simple Description:** A plain-English explanation of what the calculation does for a layperson.
   - **AI/Technical Description:** The exact mathematical algorithm and parameters required.
   - **Textual Grounding & Quotations:** (MANDATORY) Explicit quotations and references from the original Sanskrit text retrieved from our vector database (`scripture_db.py`) or Ernst Wilhelm's translations demonstrating exactly where these rules are laid out.

## 2. Separation of Concerns
The calculation of a planet's base status (Friendships, Dignities, Aspects) is done in `relationships.py`. Do NOT calculate friendships or dignities directly inside specific UI scripts or Avastha scripts. Call the functions in `relationships.py`.

## 3. Zero Breakage Policy
This mathematical engine is heavily tested. Ensure you do not change the return types of core functions.

## 4. Current Roadmap (To Be Implemented)
Before starting any of these, check if they exist to avoid duplication. Follow the **Feature Integration Standard** for each:

*   **Quantity Calculations:** `shadbala.py` (6-fold strength), `vimshopaka.py` (20-point Varga strength).
*   **Quality Calculations:** `ishta_kashta.py` (Auspicious/Inauspicious effects), `satya_jatakam.py` (+60 to -60 scoring system).
*   **Timing:** `dasas.py` (Nakshatra Dasas with custom year lengths), `gochara.py` (Transits and Ashtakavarga trigger points).
*   **Advanced Core Mechanics:** `sphuta_drishti.py` (Exact degree aspects), `combustion.py` (True 3D visual combustion based on Surya Siddhanta), and Yamakoti prime meridian integrations for time-based Lagnas.
