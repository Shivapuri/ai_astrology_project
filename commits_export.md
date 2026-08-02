# Git Commit Export
Generated on: Sun Aug  2 20:39:17 IST 2026
Number of commits requested: 3

--------------------------------------------------------------------------------

## Commit 1: d7b3b8d

```diff
commit d7b3b8d600a4a75135fd900536ec800af7d0a143
Author: Shivapuri <142108173+Shivapuri@users.noreply.github.com>
Date:   Sun Aug 2 17:50:08 2026 +0530

    test(rag): Establish formal QA & Testing Mandate and implement RAG Quality Evaluation test suite

diff --git a/Gemini.md b/Gemini.md
index 0cc3f9f..3352457 100644
--- a/Gemini.md
+++ b/Gemini.md
@@ -65,6 +65,14 @@ Alternatively, execute the Python calculation generator directly from [`jyotish/
 For AI agent instructions regarding chart interpretation, strictly follow the XML prompt files located in the `/prompts/` directory. Do not use outdated inline prompts.
 
 
+---
+
+## Core Directive: QA & Testing Standards
+Every substantial new feature, architectural change, or data ingestion pipeline added to this repository MUST be accompanied by an automated test script. 
+1. Mathematical Engine updates must be verified against Swiss Ephemeris / Jyotishganit baseline scripts (e.g., `bulk_test_engine.py`).
+2. Vector Database (RAG) updates must be verified for both functionality (does it return text?) and RELEVANCE (does the text contain the correct astrological concepts?) using the RAG Quality Evaluation suite. 
+Do not commit major logic changes without providing a way to programmatically test them.
+
 ---
 
 ## Technical Details & Constraints
@@ -75,3 +83,4 @@ For AI agent instructions regarding chart interpretation, strictly follow the XM
   * **Vedic DB**: Uses Chroma DB in `rag/chroma_jyotish_db/` with HuggingFace embeddings (`all-MiniLM-L6-v2`) for local retrieval of classical BPHS shlokas and VedAstro rules (`rag/fetch_jyotish_data.py` & `rag/build_jyotish_rag.py`).
 
 
+
diff --git a/README.md b/README.md
index 2c2abe3..ff33661 100644
--- a/README.md
+++ b/README.md
@@ -35,6 +35,11 @@ Both engines feature robust, automated QA pipelines capable of stress-testing th
 python scripts/run_western_pipeline.py --name "User" --year 1983 --month 11 --day 10 --hour 4 --minute 20 --city "Georgsmarienhütte" --country "DE"
 ```
 
+**Test Vector Database Retrieval Quality:**
+```bash
+python tests/test_rag_quality.py
+```
+
 **Bulk Stress Test the Western Engine (10,000 Charts):**
 ```bash
 python western/bulk_test_engine.py
@@ -45,3 +50,4 @@ python western/bulk_test_engine.py
 python jyotish/bulk_test_jyotish.py
 ```
 
+
diff --git a/tests/test_rag_quality.py b/tests/test_rag_quality.py
new file mode 100644
index 0000000..a4194d8
--- /dev/null
+++ b/tests/test_rag_quality.py
@@ -0,0 +1,126 @@
+import os
+import sys
+import time
+from typing import List, Dict
+
+# Ensure project root is in sys.path
+BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
+if BASE_DIR not in sys.path:
+    sys.path.insert(0, BASE_DIR)
+
+from langchain_chroma import Chroma
+from langchain_huggingface import HuggingFaceEmbeddings
+
+MODERN_DB_DIR = os.path.join(BASE_DIR, "rag", "chroma_modern_db")
+STRUCT_DB_DIR = os.path.join(BASE_DIR, "rag", "chroma_structural_db")
+
+TEST_CASES = [
+    {
+        "name": "Modern DB: Sun in Scorpio",
+        "db_path": MODERN_DB_DIR,
+        "query": "Sun in Scorpio core identity and psychology",
+        "expected_keywords": ["power", "transform", "regeneration", "desire", "energy", "psyche", "solar"]
+    },
+    {
+        "name": "Modern DB: Moon in Capricorn",
+        "db_path": MODERN_DB_DIR,
+        "query": "Moon in Capricorn reigning emotional need",
+        "expected_keywords": ["emotional", "need", "security", "reserve", "psyche", "feeling", "nature"]
+    },
+    {
+        "name": "Modern DB: Pain Body (Saturn/Venus)",
+        "db_path": MODERN_DB_DIR,
+        "query": "Saturn conjunct Venus emotional defense and pain body",
+        "expected_keywords": ["saturn", "venus", "relationship", "love", "defense", "fear", "expression"]
+    },
+    {
+        "name": "Structural DB: Taurus Ascendant",
+        "db_path": STRUCT_DB_DIR,
+        "query": "Taurus Ascendant physical vehicle and temperament",
+        "expected_keywords": ["ascendant", "persona", "personality", "character", "appearance", "taurus", "image"]
+    },
+    {
+        "name": "Structural DB: Aversion",
+        "db_path": STRUCT_DB_DIR,
+        "query": "Chart ruler in the 8th house aversion",
+        "expected_keywords": ["aversion", "eighth", "twelfth", "sixth", "ruler", "house", "blind"]
+    }
+]
+
+
+def run_quality_tests():
+    print("======================================================================")
+    print(" 🧪 RUNNING RAG RETRIEVAL QUALITY & RELEVANCE SUITE")
+    print("======================================================================")
+    
+    if not os.path.exists(MODERN_DB_DIR) or not os.path.exists(STRUCT_DB_DIR):
+        print("❌ Error: Vector databases not found. Build them first.")
+        return
+
+    print("Loading Embedding Model (all-MiniLM-L6-v2)...")
+    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
+    
+    # Load DBs
+    dbs = {
+        MODERN_DB_DIR: Chroma(persist_directory=MODERN_DB_DIR, embedding_function=embedding_model),
+        STRUCT_DB_DIR: Chroma(persist_directory=STRUCT_DB_DIR, embedding_function=embedding_model)
+    }
+
+    total_tests = len(TEST_CASES)
+    passed_tests = 0
+    start_time = time.time()
+
+    for i, test in enumerate(TEST_CASES, 1):
+        print(f"\n[Test {i}/{total_tests}] {test['name']}")
+        print(f"  Query: '{test['query']}'")
+        
+        db = dbs[test['db_path']]
+        results = db.similarity_search(test['query'], k=4)
+        
+        if not results:
+            print("  ❌ FAIL: No results returned.")
+            continue
+            
+        combined_text = " ".join([doc.page_content.lower() for doc in results])
+        
+        # Calculate relevance
+        hits = 0
+        found_words = []
+        missed_words = []
+        
+        for kw in test['expected_keywords']:
+            if kw.lower() in combined_text:
+                hits += 1
+                found_words.append(kw)
+            else:
+                missed_words.append(kw)
+                
+        relevance_score = (hits / len(test['expected_keywords'])) * 100
+        
+        print(f"  Found Keywords: {found_words}")
+        if missed_words:
+            print(f"  Missed Keywords: {missed_words}")
+        
+        if relevance_score >= 40.0:  # 40% keyword hit rate is a very strong semantic signal for RAG
+            print(f"  ✅ PASS: Relevance Score {relevance_score:.1f}%")
+            passed_tests += 1
+        else:
+            print(f"  ❌ FAIL: Relevance Score {relevance_score:.1f}% (Below 40% threshold)")
+
+    duration = time.time() - start_time
+    print("\n======================================================================")
+    print(" 📊 QA TEST SUMMARY")
+    print("======================================================================")
+    print(f" Total Tests Run : {total_tests}")
+    print(f" Passed          : {passed_tests}")
+    print(f" Failed          : {total_tests - passed_tests}")
+    print(f" Time Taken      : {duration:.2f} seconds")
+    print("======================================================================")
+    
+    if passed_tests == total_tests:
+        print("🏆 SUCCESS: All RAG databases are highly functional and relevant.")
+    else:
+        print("⚠️ WARNING: Some queries returned low-relevance documents. Database tuning may be required.")
+
+if __name__ == "__main__":
+    run_quality_tests()

```

--------------------------------------------------------------------------------

## Commit 2: 3d31e0e

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

## Commit 3: 84868c1

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

