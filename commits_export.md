# Git Commit Export
Generated on: Sun Aug  2 17:45:55 IST 2026
Number of commits requested: 3

--------------------------------------------------------------------------------

## Commit 1: 3d31e0e

```diff
commit 3d31e0eca081c4132052f336621a46995e4ad22c
Author: Shivapuri <142108173+Shivapuri@users.noreply.github.com>
Date:   Sun Aug 2 17:43:58 2026 +0530

    perf(western): Optimize dynamic RAG queries and double context retrieval volume in pipeline

diff --git a/scripts/run_western_pipeline.py b/scripts/run_western_pipeline.py
index 3557929..d2efecd 100644
--- a/scripts/run_western_pipeline.py
+++ b/scripts/run_western_pipeline.py
@@ -23,7 +23,7 @@ BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
 if BASE_DIR not in sys.path:
     sys.path.insert(0, BASE_DIR)
 
-from western.generate_chart import generate_ai_json
+from western.generate_chart import generate_ai_json, DOMICILES
 from scripts.generate_pdf import generate_pdf
 from langchain_chroma import Chroma
 from langchain_huggingface import HuggingFaceEmbeddings
@@ -177,27 +177,55 @@ def run_pipeline(
 
     native = chart_data.get("native_details", {})
     planets = chart_data.get("traditional_planets", {})
+    aspects = chart_data.get("whole_sign_aspects", [])
+    
     asc_sign = native.get("ascendant", "Ascendant")
-    sect = native.get("sect", "Chart Sect")
+    sect = native.get("sect", "Day Chart")
     
+    # Dynamically find the Chart Ruler (Steersman)
+    chart_ruler = DOMICILES.get(asc_sign, "Sun")
+    ruler_data = planets.get(chart_ruler, {})
+    ruler_sign = ruler_data.get("sign", "")
+    ruler_house = ruler_data.get("whole_sign_house", "").replace("_", " ")
+
+    # Extract specific planetary signs
+    sun_sign = planets.get("Sun", {}).get("sign", "")
+    moon_sign = planets.get("Moon", {}).get("sign", "")
+    saturn_sign = planets.get("Saturn", {}).get("sign", "")
+    mars_sign = planets.get("Mars", {}).get("sign", "")
+    venus_sign = planets.get("Venus", {}).get("sign", "")
+
+    # Dynamically extract the tightest hard aspects for the Pain Body
+    hard_aspects = [asp for asp in aspects if asp.get("aspect_type") in ["square", "opposition", "conjunction"]]
+    aspect_queries = []
+    for asp in hard_aspects[:2]:  # Take the top 2 hardest aspects to avoid query bloat
+        aspect_queries.append(f"Psychological tension {asp['planet_1']} {asp['aspect_type']} {asp['planet_2']}")
+
     # STEP 2: Pre-fetch Domain-Isolated Vector DB Context for Agent 1 & Agent 2
     print("\n📚 Step 2: Querying Domain-Isolated Chroma DBs (Structural & Modern Psychological)...")
+    
+    # Highly targeted Structural Queries (for Demetra George framework)
     struct_queries = [
-        f"Ascendant in {asc_sign} in a {sect}",
-        f"Chart ruler position in {asc_sign} whole sign house",
-        "Essential dignities domicile detriment fall classical mechanics",
-        f"Sun in {planets.get('Sun', {}).get('sign')} Moon in {planets.get('Moon', {}).get('sign')}"
-    ]
-    psych_queries = [
-        f"Solar-Lunar blend Sun in {planets.get('Sun', {}).get('sign')} Moon in {planets.get('Moon', {}).get('sign')}",
-        "Hard aspect developmental tension square opposition conjunction",
-        f"Saturn placement in {planets.get('Saturn', {}).get('sign')} emotional defenses pain body",
-        f"Mars placement in {planets.get('Mars', {}).get('sign')} internal conflicts"
+        f"Ascendant in {asc_sign} physical temperament",
+        f"Chart ruler {chart_ruler} in the {ruler_house}",
+        f"Planet in {ruler_sign} essential dignity",
+        f"{chart_ruler} in aversion to Ascendant meaning",
+        f"{sect} planetary strength and malefic behavior"
     ]
     
-    structural_rag_context = query_local_rag_db(CHROMA_STRUCTURAL_DB_DIR, struct_queries, max_results_per_query=2)
-    psychological_rag_context = query_local_rag_db(CHROMA_MODERN_DB_DIR, psych_queries, max_results_per_query=2)
-    print("✅ Domain-isolated Vector DB contexts extracted natively.")
+    # Highly targeted Psychological Queries (for Noel Tyl / Robert Hand framework)
+    psych_queries = [
+        f"Sun in {sun_sign} core identity",
+        f"Moon in {moon_sign} reigning emotional need",
+        f"Saturn in {saturn_sign} emotional defenses and pain body",
+        f"Mars in {mars_sign} conflict resolution and anger",
+        f"Venus in {venus_sign} intimate relationships and love"
+    ] + aspect_queries
+
+    # STEP 3: Increase Context Volume (max_results_per_query=4)
+    structural_rag_context = query_local_rag_db(CHROMA_STRUCTURAL_DB_DIR, struct_queries, max_results_per_query=4)
+    psychological_rag_context = query_local_rag_db(CHROMA_MODERN_DB_DIR, psych_queries, max_results_per_query=4)
+    print("✅ Domain-isolated Vector DB contexts extracted natively (Optimized Volume).")
 
     # STEP 3: Run Agent 1 (Structural & Hellenistic Profiler via Headless AGY)
     print("\n🏛️ Step 3: Executing Agent 1 (Structural Profiler - Demetra George Framework)...")

```

--------------------------------------------------------------------------------

## Commit 2: 84868c1

```diff
commit 84868c11609d05d4f3157b7f427464b446daa4ac
Author: Shivapuri <142108173+Shivapuri@users.noreply.github.com>
Date:   Sun Aug 2 17:38:55 2026 +0530

    refactor(rag): Clean up legacy scripts and update documentation for dual-camp RAG architecture

diff --git a/Gemini.md b/Gemini.md
index 3efb5a7..0cc3f9f 100644
--- a/Gemini.md
+++ b/Gemini.md
@@ -13,10 +13,10 @@ Astra is a dual-engine astrology computation project. It houses two entirely ind
 **DO NOT CONFLATE THE TWO ENGINES. YOU MUST MAINTAIN ABSOLUTE PARADIGM ISOLATION.** 
 Astra houses two entirely independent astrological frameworks. When working on a chart, you must pick ONE system and strictly isolate your tools, prompts, and terminology.
 
-**1. The Western Framework (Tropical, Modern Psychological)**
-* **Domain:** `/western/` and `/rag/astrology_rag_data/`
+**1. The Western Framework (Tropical, Modern Psychological & Hellenistic Structural)**
+* **Domain:** `/western/`, `/rag/modern_rag_data/`, and `/rag/structural_rag_data/`
 * **Calculations Tool:** You MUST ONLY use `calculate_birth_chart`.
-* **Vector Database Tool:** You MUST ONLY use `query_modern_astrology_books` (queries `chroma_astrology_db`).
+* **Vector Database Tools:** You MUST ONLY use `query_modern_astrology_books` (queries `chroma_modern_db` and `chroma_structural_db`).
 * **Rule:** NEVER mention Vimshottari Dashas, Nakshatras, or Jyotish dignities.
 
 **2. The Vedic / Jyotish Framework (Sidereal, Parashari)**
@@ -29,16 +29,11 @@ Astra houses two entirely independent astrological frameworks. When working on a
 
 ## Western Horoscope RAG Execution & Interpretation Workflow
 
-### 1. Running the Western RAG Pipeline Shell Script
-To generate a Western horoscope and perform Retrieval-Augmented Generation (RAG) against the local classical vector database (`rag/chroma_astrology_db`), execute the shell script [`run_western_rag.sh`](file:///Users/hajnaljanos/PycharmProjects/astra/run_western_rag.sh):
+### 1. Running the Western Multi-Agent Headless Pipeline
+To generate a Western horoscope and run the complete 3-Stage Headless Multi-Agent Pipeline against the domain-isolated vector databases (`rag/chroma_structural_db` for Agent 1 and `rag/chroma_modern_db` for Agent 2), execute [`scripts/run_western_pipeline.py`](file:///Users/hajnaljanos/PycharmProjects/astra/scripts/run_western_pipeline.py):
 
 ```bash
-./run_western_rag.sh [Name] [Year] [Month] [Day] [Hour] [Minute] [City] [CountryCode]
-```
-
-*Example for Georgsmarienhütte, Germany (November 10, 1983 at 04:20 AM):*
-```bash
-./run_western_rag.sh "User" 1983 11 10 4 20 "Georgsmarienhütte" "DE"
+python scripts/run_western_pipeline.py --name "User" --year 1983 --month 11 --day 10 --hour 4 --minute 20 --city "Georgsmarienhütte" --country "DE"
 ```
 
 Alternatively, invoke the MCP server tools in [`rag/western_mcp_server.py`](file:///Users/hajnaljanos/PycharmProjects/astra/rag/western_mcp_server.py):
@@ -48,7 +43,7 @@ Alternatively, invoke the MCP server tools in [`rag/western_mcp_server.py`](file
 ---
 
 ### 2. Chart Interpretation Instructions
-For AI agent instructions regarding chart interpretation, strictly follow the XML prompt files located in the `/prompts/` directory. Do not use outdated inline prompts.
+For AI agent instructions regarding chart interpretation, strictly follow the XML prompt files located in the `/prompts/` directory (`agent1_structural.xml`, `agent2_psychological.xml`, and `agent3_synthesizer.xml`). Do not use outdated inline prompts.
 
 ---
 
@@ -76,6 +71,7 @@ For AI agent instructions regarding chart interpretation, strictly follow the XM
 * **Vedic Engine (`/jyotish/`)**: Uses `jyotishganit` and `skyfield` for sidereal computations. Relies on cached NASA JPL DE421 ephemeris and Hipparcos catalog (`hip_main.dat`).
 * **Western Engine (`/western/`)**: Uses `kerykeion` and `swisseph` for tropical calculations and Whole Sign Houses.
 * **RAG Vector Bases (`/rag/`)**: 
-  * **Western DB**: Uses Chroma DB in `rag/chroma_astrology_db/` with HuggingFace embeddings (`all-MiniLM-L6-v2`) for local retrieval of modern literature.
+  * **Western DBs**: Uses dual-camp Chroma DBs (`rag/chroma_structural_db/` for Demetra George's Hellenistic mechanics and `rag/chroma_modern_db/` for Hand, Arroyo, and Marks) with HuggingFace embeddings (`all-MiniLM-L6-v2`).
   * **Vedic DB**: Uses Chroma DB in `rag/chroma_jyotish_db/` with HuggingFace embeddings (`all-MiniLM-L6-v2`) for local retrieval of classical BPHS shlokas and VedAstro rules (`rag/fetch_jyotish_data.py` & `rag/build_jyotish_rag.py`).
 
+
diff --git a/README.md b/README.md
index f1cc09c..2c2abe3 100644
--- a/README.md
+++ b/README.md
@@ -26,16 +26,22 @@ This project uses Python 3.12.
     ```
 3.  Ensure you have the required dependencies (e.g., `skyfield`, `jyotishganit`).
 
-## Testing
+## Testing and Execution
 
-Both engines feature robust, automated QA pipelines capable of stress-testing thousands of charts globally.
+Both engines feature robust, automated QA pipelines capable of stress-testing thousands of charts globally, alongside a 3-Stage Headless Multi-Agent Pipeline for Western astrology.
 
-**Test the Western Engine:**
+**Run the Western 3-Stage Headless Multi-Agent Pipeline:**
+```bash
+python scripts/run_western_pipeline.py --name "User" --year 1983 --month 11 --day 10 --hour 4 --minute 20 --city "Georgsmarienhütte" --country "DE"
+```
+
+**Bulk Stress Test the Western Engine (10,000 Charts):**
 ```bash
 python western/bulk_test_engine.py
 ```
 
-**Test the Jyotish Engine:**
+**Bulk Stress Test the Jyotish Engine (10,000 Charts):**
 ```bash
 python jyotish/bulk_test_jyotish.py
 ```
+
diff --git a/rag/cleanup_data.py b/rag/cleanup_data.py
index e44f587..83a5cef 100644
--- a/rag/cleanup_data.py
+++ b/rag/cleanup_data.py
@@ -3,68 +3,53 @@ import shutil
 import glob
 
 RAG_DIR = os.path.dirname(os.path.abspath(__file__))
-DATA_DIR = os.path.join(RAG_DIR, "astrology_rag_data")
-CHROMA_DB_DIR = os.path.join(RAG_DIR, "chroma_astrology_db")
+MODERN_DATA_DIR = os.path.join(RAG_DIR, "modern_rag_data")
+STRUCTURAL_DATA_DIR = os.path.join(RAG_DIR, "structural_rag_data")
 
-def cleanup():
-    print("--- Phase 1: Data Cleanup & Renaming Script ---")
-    
-    # 1. Delete old ancient text files
-    ancient_files = ["tetrabiblos.txt", "hellenistic_core_rules.txt", "classical_interpretations.csv"]
-    for filename in ancient_files:
-        filepath = os.path.join(DATA_DIR, filename)
-        if os.path.exists(filepath):
-            os.remove(filepath)
-            print(f"Deleted ancient file: {filename}")
-        else:
-            print(f"File not found (already deleted): {filename}")
+CHROMA_MODERN_DB = os.path.join(RAG_DIR, "chroma_modern_db")
+CHROMA_STRUCTURAL_DB = os.path.join(RAG_DIR, "chroma_structural_db")
 
-    # 2. Find, deduplicate, and rename modern PDF books
-    pdf_files = glob.glob(os.path.join(DATA_DIR, "*.pdf"))
-    
-    # Separate any already standardized files from messily named files
-    standard_names = ["modern_astrology_book_1.pdf", "modern_astrology_book_2.pdf", "modern_astrology_book_3.pdf"]
-    
-    # Track unique files by size to remove duplicates
-    seen_sizes = {}
-    unique_pdfs = []
-    
-    for pdf_path in sorted(pdf_files):
-        size = os.path.getsize(pdf_path)
-        base_name = os.path.basename(pdf_path)
-        if size in seen_sizes:
-            print(f"Removing duplicate PDF: {base_name}")
-            os.remove(pdf_path)
-        else:
-            seen_sizes[size] = pdf_path
-            unique_pdfs.append(pdf_path)
 
-    # Rename up to 3 PDFs to modern_astrology_book_X.pdf
-    for idx, pdf_path in enumerate(unique_pdfs[:3], start=1):
-        new_name = f"modern_astrology_book_{idx}.pdf"
-        target_path = os.path.join(DATA_DIR, new_name)
-        if pdf_path != target_path:
-            # If target already exists from earlier run, overwrite carefully
-            if os.path.exists(target_path):
-                os.remove(target_path)
-            os.rename(pdf_path, target_path)
-            print(f"Renamed '{os.path.basename(pdf_path)}' -> '{new_name}'")
+def cleanup():
+    print("--- Phase 1: Dual RAG Data Cleanup Script ---")
+    
+    # 1. Clean up duplicate PDFs in modern_rag_data
+    if os.path.exists(MODERN_DATA_DIR):
+        pdf_files = glob.glob(os.path.join(MODERN_DATA_DIR, "*.pdf"))
+        seen_sizes = {}
+        for pdf_path in sorted(pdf_files):
+            size = os.path.getsize(pdf_path)
+            base_name = os.path.basename(pdf_path)
+            if size in seen_sizes:
+                print(f"Removing duplicate PDF in modern_rag_data: {base_name}")
+                os.remove(pdf_path)
+            else:
+                seen_sizes[size] = pdf_path
+
+    # 2. Clean up duplicate PDFs in structural_rag_data
+    if os.path.exists(STRUCTURAL_DATA_DIR):
+        pdf_files = glob.glob(os.path.join(STRUCTURAL_DATA_DIR, "*.pdf"))
+        seen_sizes = {}
+        for pdf_path in sorted(pdf_files):
+            size = os.path.getsize(pdf_path)
+            base_name = os.path.basename(pdf_path)
+            if size in seen_sizes:
+                print(f"Removing duplicate PDF in structural_rag_data: {base_name}")
+                os.remove(pdf_path)
+            else:
+                seen_sizes[size] = pdf_path
+
+    # 3. Delete old ChromaDB directory caches if requested
+    for db_dir, name in [(CHROMA_MODERN_DB, "Chroma Modern DB"), (CHROMA_STRUCTURAL_DB, "Chroma Structural DB")]:
+        if os.path.exists(db_dir):
+            shutil.rmtree(db_dir)
+            print(f"Deleted vector database directory: {name} at {db_dir}")
         else:
-            print(f"File already standardized: '{new_name}'")
-
-    # Clean up any leftover PDFs beyond the top 3
-    for pdf_path in unique_pdfs[3:]:
-        print(f"Removing extra PDF: {os.path.basename(pdf_path)}")
-        os.remove(pdf_path)
-
-    # 3. Delete old ChromaDB directory cache
-    if os.path.exists(CHROMA_DB_DIR):
-        shutil.rmtree(CHROMA_DB_DIR)
-        print(f"Deleted old vector database directory at {CHROMA_DB_DIR}")
-    else:
-        print("No existing vector database found to delete.")
+            print(f"No existing {name} directory found to delete.")
 
     print("--- Phase 1 Cleanup Complete! ---")
 
+
 if __name__ == "__main__":
     cleanup()
+
diff --git a/rag/rag_interpreter.py b/rag/rag_interpreter.py
deleted file mode 100644
index 2f27ad1..0000000
--- a/rag/rag_interpreter.py
+++ /dev/null
@@ -1,126 +0,0 @@
-import os
-import json
-from langchain_chroma import Chroma
-from langchain_huggingface import HuggingFaceEmbeddings
-
-CHROMA_DB_DIR = os.path.join(os.path.dirname(__file__), "chroma_astrology_db")
-CHART_JSON_PATH = os.path.join(os.path.dirname(__file__), "..", "western", "chart_context.json")
-
-def load_chart_json(file_path=CHART_JSON_PATH):
-    """Load and parse the chart context JSON file."""
-    if not os.path.exists(file_path):
-        # Fallback check for root or rag folder
-        alt_path = os.path.join(os.path.dirname(__file__), "chart_context.json")
-        if os.path.exists(alt_path):
-            file_path = alt_path
-        else:
-            raise FileNotFoundError(f"Chart file not found at {file_path} or {alt_path}")
-    with open(file_path, "r", encoding="utf-8") as f:
-        return json.load(f)
-
-def retrieve_classical_context(vector_store, native_details, planet_name, planet_data):
-    """Perform a multi-query semantic search for high-accuracy RAG retrieval."""
-    sign = planet_data.get("sign", "")
-    house = planet_data.get("whole_sign_house", "").replace("_", " ") # Convert "House_2" to "House 2"
-    dignity = planet_data.get("essential_dignity", "").split(" ")[0] # Extract just "Detriment" or "Domicile"
-    sect = native_details.get("sect", "")
-    
-    # MULTI-QUERY STRATEGY: Vector DBs respond better to specific semantic questions
-    queries = [
-        f"What is the astrological meaning of {planet_name} in the sign of {sign}?",
-        f"How does {planet_name} behave in the {house}?",
-        f"What happens when {planet_name} is in {dignity} dignity in a {sect}?"
-    ]
-    
-    retrieved_texts = []
-    seen = set()
-    
-    # Query the DB for each semantic question
-    for q in queries:
-        results = vector_store.similarity_search(q, k=2) # Get top 2 for each specific question
-        for doc in results:
-            content = doc.page_content.strip()
-            if content not in seen:
-                seen.add(content)
-                retrieved_texts.append(content)
-                
-    # Return the combined context
-    return " | ".join(queries), retrieved_texts[:4]
-
-def interpret_chart_with_rag():
-    print("--- Phase 3: Classical RAG Chart Interpreter ---")
-    
-    # 1. Load Chart JSON
-    chart_data = load_chart_json()
-    native = chart_data.get("native_details", {})
-    planets = chart_data.get("traditional_planets", {})
-    
-    print(f"Loaded Chart for Ascendant: {native.get('ascendant')} | Sect: {native.get('sect')}")
-
-    # 2. Connect to Chroma Vector Store
-    print("Connecting to local Chroma Vector Database...")
-    embedding_model = HuggingFaceEmbeddings(
-        model_name="sentence-transformers/all-MiniLM-L6-v2"
-    )
-    vector_store = Chroma(
-        persist_directory=CHROMA_DB_DIR,
-        embedding_function=embedding_model
-    )
-
-    # 3. Retrieve context for all traditional placements
-    retrieved_knowledge = []
-    
-    print("\nExtracting placements and querying RAG DB...")
-    for planet_name, planet_info in planets.items():
-        query, context_chunks = retrieve_classical_context(vector_store, native, planet_name, planet_info)
-        context_str = "\n".join([f"   - {chunk}" for chunk in context_chunks])
-        retrieved_knowledge.append({
-            "planet": planet_name,
-            "placement": f"{planet_name} in {planet_info.get('sign')} ({planet_info.get('whole_sign_house')}) - Dignity: {planet_info.get('essential_dignity')}",
-            "query": query,
-            "retrieved_context": context_str
-        })
-
-    # 4. Construct Strict System Prompt & Full LLM Payload
-    system_prompt = (
-        "STRICT SYSTEM PROMPT:\n"
-        "You are a Hellenistic Astrologer. You must ONLY use the provided classical RAG context "
-        "and chart JSON below to interpret this chart.\n"
-        "DO NOT use modern psychological astrology, pop astrology, outer planets, or unverified outside knowledge.\n"
-        "Base all judgments strictly on Essential Dignities, Chart Sect (Day/Night), and Whole Sign House topology."
-    )
-
-    prompt_payload = f"=== SYSTEM INSTRUCTION ===\n{system_prompt}\n\n"
-    prompt_payload += f"=== NATIVE CHART DETAILS ===\n{json.dumps(native, indent=2)}\n\n"
-    prompt_payload += "=== RETRIEVED CLASSICAL GROUND TRUTH (RAG CONTEXT) ===\n"
-    
-    for item in retrieved_knowledge:
-        prompt_payload += f"\nPlacement: {item['placement']}\n"
-        prompt_payload += f"Retrieved Context:\n{item['retrieved_context']}\n"
-
-    print("\n" + "="*60)
-    print("FINAL LLM PROMPT (READY FOR INFERENCE):")
-    print("="*60)
-    print(prompt_payload)
-    print("="*60)
-
-    # 5. Execute LLM Call if API key present, else display payload
-    openai_api_key = os.getenv("OPENAI_API_KEY")
-    if openai_api_key:
-        try:
-            from langchain_openai import ChatOpenAI
-            llm = ChatOpenAI(model="gpt-4o", temperature=0.2)
-            response = llm.invoke(prompt_payload)
-            print("\n=== HELLENISTIC ASTROLOGY INTERPRETATION ===")
-            print(response.content)
-        except Exception as e:
-            print(f"\nCould not call OpenAI API automatically: {e}")
-    else:
-        print("\nNOTE: Set your OPENAI_API_KEY environment variable to get automated LLM output.")
-        print("The RAG retrieval payload above is fully formatted and ready for strict classical interpretation!")
-
-def main():
-    interpret_chart_with_rag()
-
-if __name__ == "__main__":
-    main()
diff --git a/rag/western_mcp_server.py b/rag/western_mcp_server.py
index eacda4a..95c3f9f 100644
--- a/rag/western_mcp_server.py
+++ b/rag/western_mcp_server.py
@@ -33,7 +33,8 @@ try:
 except TypeError:
     mcp = FastMCP("Astra Western Astrology Server")
 
-WESTERN_CHROMA_DB_DIR = os.path.join(BASE_DIR, "rag", "chroma_astrology_db")
+WESTERN_CHROMA_MODERN_DB_DIR = os.path.join(BASE_DIR, "rag", "chroma_modern_db")
+WESTERN_CHROMA_STRUCTURAL_DB_DIR = os.path.join(BASE_DIR, "rag", "chroma_structural_db")
 
 
 @mcp.tool()
@@ -80,28 +81,29 @@ def calculate_birth_chart(
 def query_modern_astrology_books(query: str) -> str:
     """
     [WESTERN ENGINE ONLY - DO NOT USE FOR JYOTISH]
-    Queries the local Modern Psychological Astrology Vector Database (containing modern Western books).
-    Use this to look up Noel Tyl, Demetra George, and modern psychological interpretations.
-    Pass targeted psychological queries such as 'Moon in Taurus in 2nd House' or 'Saturn transit square Sun'.
+    Queries the local Modern Psychological & Structural Astrology Vector Databases.
+    Use this to look up Demetra George, Robert Hand, Stephen Arroyo, and Tracy Marks.
+    Pass targeted queries such as 'Moon in Taurus in 2nd House' or 'Saturn transit square Sun'.
     
     Western CoT Step 3: Call this tool 1 to 3 times for key chart placements.
     """
     try:
-        if not os.path.exists(WESTERN_CHROMA_DB_DIR):
+        target_db = WESTERN_CHROMA_MODERN_DB_DIR if os.path.exists(WESTERN_CHROMA_MODERN_DB_DIR) else WESTERN_CHROMA_STRUCTURAL_DB_DIR
+        if not os.path.exists(target_db):
             return "Western Vector database not found. Please run build_rag_pipeline.py first."
             
         embedding_model = HuggingFaceEmbeddings(
             model_name="sentence-transformers/all-MiniLM-L6-v2"
         )
         vector_store = Chroma(
-            persist_directory=WESTERN_CHROMA_DB_DIR,
+            persist_directory=target_db,
             embedding_function=embedding_model
         )
         results = vector_store.similarity_search(query, k=4)
         
-        output = f"=== MODERN PSYCHOLOGICAL ASTROLOGY RAG SEARCH RESULTS FOR: '{query}' ===\n\n"
+        output = f"=== WESTERN ASTROLOGY RAG SEARCH RESULTS FOR: '{query}' ===\n\n"
         for idx, doc in enumerate(results, 1):
-            source = os.path.basename(doc.metadata.get("source", "modern_astrology_book"))
+            source = os.path.basename(doc.metadata.get("source", "astrology_book"))
             page = doc.metadata.get("page", "N/A")
             output += f"--- Result {idx} [Source: {source}, Page: {page}] ---\n{doc.page_content}\n\n"
         return output
@@ -109,5 +111,6 @@ def query_modern_astrology_books(query: str) -> str:
         return f"Error querying Western vector database: {str(e)}"
 
 
+
 if __name__ == "__main__":
     mcp.run()
diff --git a/run_western_rag.sh b/run_western_rag.sh
deleted file mode 100755
index defe4c9..0000000
--- a/run_western_rag.sh
+++ /dev/null
@@ -1,62 +0,0 @@
-#!/usr/bin/env bash
-# ==============================================================================
-# Western Hellenistic Horoscope RAG Execution Script
-# ==============================================================================
-# Usage:
-#   ./run_western_rag.sh [Name] [Year] [Month] [Day] [Hour] [Minute] [City] [CountryCode]
-# Default parameters:
-#   User 1983 11 10 4 20 Georgsmarienhütte DE
-# ==============================================================================
-
-NAME="${1:-User}"
-YEAR="${2:-1983}"
-MONTH="${3:-11}"
-DAY="${4:-10}"
-HOUR="${5:-4}"
-MINUTE="${6:-20}"
-CITY="${7:-Georgsmarienhütte}"
-COUNTRY="${8:-DE}"
-
-SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
-PYTHON_BIN="${SCRIPT_DIR}/venv/bin/python"
-
-if [ ! -f "$PYTHON_BIN" ]; then
-    PYTHON_BIN="python3"
-fi
-
-echo "======================================================================"
-echo "  Astra Western Hellenistic Astrology Engine & Classical RAG DB"
-echo "======================================================================"
-echo " Calculating Chart for: $NAME"
-echo " Date & Time: $YEAR-$MONTH-$DAY $HOUR:$MINUTE"
-echo " Location: $CITY, $COUNTRY"
-echo "----------------------------------------------------------------------"
-
-# 1. Generate Western Chart JSON
-"$PYTHON_BIN" -c "
-from western.generate_chart import generate_ai_json
-generate_ai_json(
-    name='$NAME',
-    year=$YEAR,
-    month=$MONTH,
-    day=$DAY,
-    hour=$HOUR,
-    minute=$MINUTE,
-    city='$CITY',
-    country_code='$COUNTRY',
-    output_filename='western/chart_context.json',
-    silent=False
-)
-"
-
-# 2. Run RAG Interpreter to query vector database
-echo ""
-echo "----------------------------------------------------------------------"
-echo " Querying Local Vector DB (Chroma) for Classical Ground Truth..."
-echo "----------------------------------------------------------------------"
-"$PYTHON_BIN" rag/rag_interpreter.py
-
-echo ""
-echo "======================================================================"
-echo " Execution Complete! Chart data saved to western/chart_context.json"
-echo "======================================================================"

```

--------------------------------------------------------------------------------

## Commit 3: b02bb44

```diff
commit b02bb4441711ff2f663be87d0af1ed62e29da4d4
Author: Shivapuri <142108173+Shivapuri@users.noreply.github.com>
Date:   Sun Aug 2 17:37:07 2026 +0530

    feat(rag): Upgrade Western RAG pipeline to dual domain-isolated databases (Structural & Modern Psychological)

diff --git a/.gitignore b/.gitignore
index d04f9ae..d7876ed 100644
--- a/.gitignore
+++ b/.gitignore
@@ -11,8 +11,12 @@ cache/
 code_export.txt
 rag/chroma_astrology_db/
 rag/chroma_jyotish_db/
+rag/chroma_structural_db/
+rag/chroma_modern_db/
+
 
 # Prevent large media and binary files from bloating Git repo
+*.pdf
 *.wav
 *.mp3
 *.png
@@ -22,3 +26,4 @@ rag/chroma_jyotish_db/
 *.html
 western/logs/
 .DS_Store
+
diff --git a/prompts/agent1_structural.xml b/prompts/agent1_structural.xml
index c169134..e3c2d8d 100644
--- a/prompts/agent1_structural.xml
+++ b/prompts/agent1_structural.xml
@@ -9,6 +9,7 @@ You are the "Structural & Hellenistic Astrological Profiler". You use Demetra Ge
 </focus_areas>
 <instructions>
 1. Review the raw chart JSON.
-2. Use your Vector DB search tool to research the structural meanings of these placements.
+2. You are receiving RAG context from Demetra George's structural framework. Focus heavily on identifying the Ascendant, the Steersman (Chart Ruler), Essential Dignities, and Aversions.
 3. Output a highly detailed, bulleted report on the "Mechanics of the Chart". DO NOT interpret deep psychological trauma or the Solar-Lunar blend—leave that to Agent 2.
 </instructions>
+
diff --git a/rag/astrology_rag_data/modern_astrology_book_1.pdf b/rag/astrology_rag_data/modern_astrology_book_1.pdf
deleted file mode 100644
index 68caad3..0000000
Binary files a/rag/astrology_rag_data/modern_astrology_book_1.pdf and /dev/null differ
diff --git a/rag/astrology_rag_data/modern_astrology_book_2.pdf b/rag/astrology_rag_data/modern_astrology_book_2.pdf
deleted file mode 100644
index d5a7f28..0000000
Binary files a/rag/astrology_rag_data/modern_astrology_book_2.pdf and /dev/null differ
diff --git a/rag/build_rag_pipeline.py b/rag/build_rag_pipeline.py
index 1762345..eec4012 100644
--- a/rag/build_rag_pipeline.py
+++ b/rag/build_rag_pipeline.py
@@ -5,60 +5,84 @@ from langchain_text_splitters import RecursiveCharacterTextSplitter
 from langchain_chroma import Chroma
 from langchain_huggingface import HuggingFaceEmbeddings
 
-DATA_DIR = os.path.join(os.path.dirname(__file__), "astrology_rag_data")
-CHROMA_DB_DIR = os.path.join(os.path.dirname(__file__), "chroma_astrology_db")
+RAG_DIR = os.path.dirname(os.path.abspath(__file__))
+MODERN_DATA_DIR = os.path.join(RAG_DIR, "modern_rag_data")
+STRUCTURAL_DATA_DIR = os.path.join(RAG_DIR, "structural_rag_data")
 
-def load_pdf_documents():
-    """Ingest all modern astrology PDF books from data directory."""
+CHROMA_MODERN_DB_DIR = os.path.join(RAG_DIR, "chroma_modern_db")
+CHROMA_STRUCTURAL_DB_DIR = os.path.join(RAG_DIR, "chroma_structural_db")
+
+
+def load_pdf_documents_from_dir(data_dir: str):
+    """Ingest all PDF books from a specific data directory."""
     documents = []
-    print(f"Ingesting PDF files from {DATA_DIR}...")
+    print(f"Ingesting PDF files from {data_dir}...")
     
-    pdf_files = glob.glob(os.path.join(DATA_DIR, "*.pdf"))
+    pdf_files = glob.glob(os.path.join(data_dir, "*.pdf"))
     for file_path in pdf_files:
         try:
-            print(f"Loading PDF: {os.path.basename(file_path)}...")
+            print(f"  -> Loading PDF: {os.path.basename(file_path)}...")
             loader = PyPDFLoader(file_path)
             docs = loader.load()
-            print(f"  -> Loaded {len(docs)} pages from {os.path.basename(file_path)}")
+            print(f"     Loaded {len(docs)} pages from {os.path.basename(file_path)}")
             documents.extend(docs)
         except Exception as e:
             print(f"Error loading {file_path}: {e}")
 
     return documents
 
-def build_vector_store(documents):
-    """Split PDF pages into chunks and embed into local ChromaDB vector database."""
-    print("Splitting documents into searchable text chunks...")
+
+def build_vector_store_for_domain(documents, target_db_dir: str, domain_name: str):
+    """Split PDF pages into chunks and embed into specified local ChromaDB vector database."""
+    print(f"\n--- Building {domain_name} Vector DB ---")
+    if not documents:
+        print(f"⚠️ No documents provided for {domain_name}. Skipping build.")
+        return None
+
+    print(f"Splitting {len(documents)} document pages into searchable text chunks...")
     text_splitter = RecursiveCharacterTextSplitter(
         chunk_size=1500,
         chunk_overlap=250,
         separators=["\n\n", "\n", ".", " ", ""]
     )
     chunks = text_splitter.split_documents(documents)
-    print(f"Created {len(chunks)} total text chunks.")
+    print(f"Created {len(chunks)} total text chunks for {domain_name}.")
 
     print("Initializing HuggingFace embedding model (all-MiniLM-L6-v2)...")
     embedding_model = HuggingFaceEmbeddings(
         model_name="sentence-transformers/all-MiniLM-L6-v2"
     )
 
-    print(f"Embedding chunks into Chroma Vector DB at {CHROMA_DB_DIR}...")
+    print(f"Embedding chunks into Chroma Vector DB at {target_db_dir}...")
     vector_store = Chroma.from_documents(
         documents=chunks,
         embedding=embedding_model,
-        persist_directory=CHROMA_DB_DIR
+        persist_directory=target_db_dir
     )
-    print("Vector database successfully built and persisted!")
+    print(f"✅ {domain_name} Vector database successfully built and persisted at {target_db_dir}!")
     return vector_store
 
+
 def main():
-    print("--- Phase 2: Building Modern Astrology RAG Database ---")
-    docs = load_pdf_documents()
-    if not docs:
-        print("No PDF documents found in astrology_rag_data directory. Run Phase 1 first.")
-        return
-    build_vector_store(docs)
-    print("--- Phase 2 Complete! Vector store saved in /chroma_astrology_db/ ---")
+    print("======================================================================")
+    print(" Building Dual-Camp Domain-Isolated Vector Databases")
+    print("======================================================================")
+    
+    # 1. Structural Camp (Demetra George)
+    struct_docs = load_pdf_documents_from_dir(STRUCTURAL_DATA_DIR)
+    build_vector_store_for_domain(struct_docs, CHROMA_STRUCTURAL_DB_DIR, "Structural Camp (Demetra George)")
+    
+    # 2. Modern Psychological Camp (Arroyo, Marks, Hand)
+    modern_docs = load_pdf_documents_from_dir(MODERN_DATA_DIR)
+    build_vector_store_for_domain(modern_docs, CHROMA_MODERN_DB_DIR, "Modern Psychological Camp (Arroyo, Marks, Hand)")
+    
+    print("\n======================================================================")
+    print("🎉 Dual RAG Database Build Complete!")
+    print(f"   Structural DB: {CHROMA_STRUCTURAL_DB_DIR}")
+    print(f"   Modern DB:     {CHROMA_MODERN_DB_DIR}")
+    print("======================================================================")
+
 
 if __name__ == "__main__":
     main()
+
diff --git a/scripts/run_western_pipeline.py b/scripts/run_western_pipeline.py
index 8aad232..3557929 100644
--- a/scripts/run_western_pipeline.py
+++ b/scripts/run_western_pipeline.py
@@ -28,7 +28,8 @@ from scripts.generate_pdf import generate_pdf
 from langchain_chroma import Chroma
 from langchain_huggingface import HuggingFaceEmbeddings
 
-WESTERN_CHROMA_DB_DIR = os.path.join(BASE_DIR, "rag", "chroma_astrology_db")
+CHROMA_STRUCTURAL_DB_DIR = os.path.join(BASE_DIR, "rag", "chroma_structural_db")
+CHROMA_MODERN_DB_DIR = os.path.join(BASE_DIR, "rag", "chroma_modern_db")
 
 
 def load_prompt(filename: str) -> str:
@@ -40,17 +41,17 @@ def load_prompt(filename: str) -> str:
         return f.read()
 
 
-def query_local_rag_db(queries: List[str], max_results_per_query: int = 3) -> str:
-    """Queries the local Chroma Vector DB directly without API calls."""
-    if not os.path.exists(WESTERN_CHROMA_DB_DIR):
-        return "⚠️ Western Vector database not found at rag/chroma_astrology_db."
+def query_local_rag_db(db_dir: str, queries: List[str], max_results_per_query: int = 3) -> str:
+    """Queries a specific local Chroma Vector DB directly without API calls."""
+    if not os.path.exists(db_dir):
+        return f"⚠️ Vector database not found at {db_dir}."
         
     try:
         embedding_model = HuggingFaceEmbeddings(
             model_name="sentence-transformers/all-MiniLM-L6-v2"
         )
         vector_store = Chroma(
-            persist_directory=WESTERN_CHROMA_DB_DIR,
+            persist_directory=db_dir,
             embedding_function=embedding_model
         )
         
@@ -70,7 +71,7 @@ def query_local_rag_db(queries: List[str], max_results_per_query: int = 3) -> st
                     
         return "\n".join(output_chunks)
     except Exception as e:
-        return f"Error querying local Chroma DB: {e}"
+        return f"Error querying local Chroma DB at {db_dir}: {e}"
 
 
 def run_agent_headless(
@@ -179,8 +180,8 @@ def run_pipeline(
     asc_sign = native.get("ascendant", "Ascendant")
     sect = native.get("sect", "Chart Sect")
     
-    # STEP 2: Pre-fetch Vector DB Ground Truth for Agent 1 & Agent 2
-    print("\n📚 Step 2: Querying Local Chroma Vector DB for Classical & Psychological Ground Truth...")
+    # STEP 2: Pre-fetch Domain-Isolated Vector DB Context for Agent 1 & Agent 2
+    print("\n📚 Step 2: Querying Domain-Isolated Chroma DBs (Structural & Modern Psychological)...")
     struct_queries = [
         f"Ascendant in {asc_sign} in a {sect}",
         f"Chart ruler position in {asc_sign} whole sign house",
@@ -194,9 +195,9 @@ def run_pipeline(
         f"Mars placement in {planets.get('Mars', {}).get('sign')} internal conflicts"
     ]
     
-    structural_rag_context = query_local_rag_db(struct_queries, max_results_per_query=2)
-    psychological_rag_context = query_local_rag_db(psych_queries, max_results_per_query=2)
-    print("✅ Local Vector DB context extracted natively.")
+    structural_rag_context = query_local_rag_db(CHROMA_STRUCTURAL_DB_DIR, struct_queries, max_results_per_query=2)
+    psychological_rag_context = query_local_rag_db(CHROMA_MODERN_DB_DIR, psych_queries, max_results_per_query=2)
+    print("✅ Domain-isolated Vector DB contexts extracted natively.")
 
     # STEP 3: Run Agent 1 (Structural & Hellenistic Profiler via Headless AGY)
     print("\n🏛️ Step 3: Executing Agent 1 (Structural Profiler - Demetra George Framework)...")

```

--------------------------------------------------------------------------------

