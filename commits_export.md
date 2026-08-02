# Git Commit Export
Generated on: Sun Aug  2 17:37:09 IST 2026
Number of commits requested: 3

--------------------------------------------------------------------------------

## Commit 1: b02bb44

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

## Commit 2: 7ed6de0

```diff
commit 7ed6de0320a838d062b6b90d4b8196110d1a4ae6
Author: Shivapuri <142108173+Shivapuri@users.noreply.github.com>
Date:   Sun Aug 2 16:06:56 2026 +0530

    Sync repository clean state with remote

diff --git a/western/Christina_1987-11-19_15-50_Western_Analysis.md b/western/Christina_1987-11-19_15-50_Western_Analysis.md
deleted file mode 100644
index c4dc92a..0000000
--- a/western/Christina_1987-11-19_15-50_Western_Analysis.md
+++ /dev/null
@@ -1,51 +0,0 @@
-# Western Psychological Horoscope Analysis for Christina
-**Born:** November 19, 1987 at 15:50 (3:50 PM)  
-**Location:** Georgsmarienhütte, Lower Saxony, Germany  
-**Coordinates Confirmed:** Latitude 52.20296° N, Longitude 8.0448° E  
-**Astrological Framework:** Hellenistic Western & Modern Psychological (Tropical Zodiac, Whole Sign Houses)
-
----
-
-## Part 1: The Psychological Engine (Solar-Lunar Blend)
-
-### Professional Synthesis
-In psychological astrology, your birth chart is a moving map of human growth rather than a fixed destiny. At the heart of this map is your **Solar-Lunar Blend** (the dynamic combination of your Sun and Moon). Think of your Sun as your **Core Identity**—the engine generating your essential vitality, ego-will, and desire to shine. Think of your Moon as your **Reigning Need**—your deepest emotional hunger that must be satisfied for you to feel secure and at peace. 
-
-In your chart, both your Sun and Moon are fused together in the intense, emotional water sign of **Scorpio** in your 7th House (the zone of partnerships and close one-on-one relationships). This creates a highly focused inner engine. Your Scorpio Sun fuels you with deep psychological insight, emotional courage, and a powerful drive for authentic connection. This energy pours directly into feeding your Scorpio Moon's reigning need: a profound craving for unshakeable loyalty, complete vulnerability, and absolute trust in your relationships. Because the Moon in Scorpio is traditionally considered in its **Fall** (a placement requiring extra emotional energy and specialized care to feel safe), your inner radar is exceptionally perceptive. You instinctively cut through superficiality to seek bedrock emotional security.
-
-### Day-in-the-Life Reality
-Imagine you are attending a collaborative project kick-off meeting at work or going out to a casual social mixer. While others are making polite small talk about the weather or surface-level logistics, you feel entirely uninterested in shallow banter. You find a quiet corner with one colleague or partner and immediately tune into what is *really* happening behind the scenes—the interpersonal dynamics, unsaid motivations, and real human feelings. If someone tries to give you flattery without substance, your inner alarm rings and you gently step back. But when a friend confides a deep personal struggle, your attentive, compassionate energy activates instantly. You create a secure sanctuary where they feel completely heard, fulfilling your profound craving for authentic, loyal mutual trust.
-
----
-
-## Part 2: The Vessel and The Steersman (Life Direction)
-
-### Professional Synthesis
-To understand how you actively navigate the world, we use traditional planetary architecture by looking at your **Helm** and your **Steersman**. Your **Helm** is your **Ascendant** (the zodiac sign rising on the eastern horizon at the exact moment of your birth)—this represents your physical ship, your bodily vitality, and your natural outward temperament. Your Ascendant is in **Taurus**, meaning your material vessel is solid, steady, sensory-aware, and exceptionally grounded. You interface with the physical world through calm reliability and patience.
-
-Your ship is captained by **The Steersman**—the planet that rules your Ascendant sign. Since Taurus is ruled by **Venus**, Venus is the captain of your life path! In your chart, Venus travels through visionary **Sagittarius** in your 8th House (the realm of shared resources, deep emotional bonds, and major life transformations). Interestingly, the 8th House is situated in what astrologers call **Aversion** (a blind spot where a house doesn't make a standard visual angle to the Ascendant). This means there can sometimes be a striking contrast between your outwardly tranquil, unflappable Taurus demeanor and the adventurous, deep-diving emotional voyages your inner captain is drawn to explore. You aren't meant for surface cruising; your captain actively guides you into profound psychological and shared emotional depth.
-
-### Day-in-the-Life Reality
-When people meet you for the first time, your Taurus Ascendant gives an impression of absolute serenity and approachable warmth. In a busy room or high-stress environment, colleagues naturally gravitate toward you because you feel like a calm anchor in a storm. Yet, once you enter into an established partnership or project, your Sagittarius Venus take the wheel, showing a surprisingly daring, exploratory side. You are the one willing to dive straight into complicated shared finances, complex psychological matters, or taboo subjects that others shy away from. You might look calm and traditional on the outside, but underneath, you are an adventurous psychological explorer seeking transformative meaning.
-
----
-
-## Part 3: Developmental Tension & The Pain Body
-
-### Professional Synthesis
-In this methodology, challenging astrological angles are not seen as negative roadblocks, but as necessary **Developmental Tension**—the invaluable friction that promotes ego maturity and personal growth. When vulnerable points in the chart are touched by intense structural planets, they form what we call the **Pain Body** (an energized emotional tender spot formed in early development that can trigger defensive behavior under stress). 
-
-In your chart, your Steersman (Venus) sits in a tight conjunction (0° angle of fusion) with **Saturn** in your 8th House. Saturn is the planetary force of boundaries, duty, discipline, and emotional caution. Positioned right next to your heart-ruling Venus in the deep realm of intimacy, Saturn represents a sensitized bruise surrounding trust and shared vulnerability. Early life experiences may have taught you to guard your emotional boundaries fiercely out of a hidden fear of being let down or losing control. Furthermore, your assertive planet **Mars** in diplomatic Libra (in the 6th House of routine tasks) opposes an expansive **Jupiter** in your 12th House (the hidden realm of solitude and spirit), creating tension between your urge to please others in everyday duties and your profound need for quiet personal sanctuary. When feeling threatened or stressed, your instinctive defense mechanism is to become overly cautious, building impenetrable emotional walls or taking on excessive burdens to stay in control.
-
-### Day-in-the-Life Reality
-When a significant conflict arises—such as an intimate partner breaking a small commitment or a business ally making an unexpected financial decision—your first reflex is not loud anger. Instead, your Venus-Saturn defense kicks in: you shut down emotional vulnerability and pull up the heavy fortress drawbridge. You might suddenly become supremely formal, strictly hyper-responsible, and intensely guarded, managing every practical detail yourself so you won't have to rely on anyone else. Recognizing this pattern is your greatest breakthrough. When you notice yourself building an ice wall during an argument, you can consciously step back, soften your protective armor, and express your deep feeling of vulnerability rather than trying to manage the situation through defensive control.
-
----
-
-## Part 4: The Unified Path (Counseling Strategy)
-
-Your birth chart reveals an extraordinary synthesis between a calm, stabilizing exterior and an immensely profound, psychological interior. To align your life trajectory, remember this unifying formula:
-
-* **Use your serene Taurus presence (The Helm) and your deep-diving Sagittarius Venus (The Steersman) to create authentic, enduring bonds of loyalty (your Scorpio Solar-Lunar Reigning Need).**
-* **Reframe your boundaries:** Rather than viewing emotional walls as necessary protection against disappointment, transform your Venus-Saturn tension into healthy, conscious commitment. Use Saturn's discipline to build stable, transparent agreements in your close partnerships rather than emotional barriers.
-* **Honor your depth:** Avoid forcing yourself to thrive in superficial or socially shallow arenas. Your gifts shine brightest in deep one-on-one relationships, therapeutic spaces, research, financial management, and transformative mentorship, where your profound courage and unwavering truth can genuinely enrich lives.
diff --git a/western/Christina_1987-11-19_15-50_Western_Analysis.pdf b/western/Christina_1987-11-19_15-50_Western_Analysis.pdf
deleted file mode 100644
index 9fb63e8..0000000
Binary files a/western/Christina_1987-11-19_15-50_Western_Analysis.pdf and /dev/null differ
diff --git a/western/User_1983-11-10_04-20_Full_Reading.md b/western/User_1983-11-10_04-20_Full_Reading.md
deleted file mode 100644
index 78a7c94..0000000
--- a/western/User_1983-11-10_04-20_Full_Reading.md
+++ /dev/null
@@ -1,24 +0,0 @@
-# Western Astrology Horoscope Reading for User
-
-## Part 1: The Core Engine (Synthesizing the Solar-Lunar Blend)
-Your Sun in Sco drives your core direction, while your Moon in Cap powers your emotional needs.
-
-**Day-in-the-Life Reality:**
-When you enter a room full of people, your immediate instinct is to observe before diving into deep conversation.
-
-## Part 2: The Vessel & Steersman (Synthesizing Ascendant, Ruler, and Dignities)
-With a Lib Ascendant (Rising Sign) in a Night Chart, your chart operates with a strong, focused outward presence.
-
-**Day-in-the-Life Reality:**
-When starting a new project, you take structured, step-by-step actions to ensure everything is built on solid ground.
-
-## Part 3: Tension & Growth (Synthesizing Aspects & the Pain Body)
-The hard aspects between key planets create dynamic growth opportunities.
-
-**Day-in-the-Life Reality:**
-In moments of disagreement, you might step back to reflect deeply before responding.
-
-## Summary
-- **Archetype:** The Strategic Visionary
-- **Superpower:** Analytical Focus and Emotional Resilience
-- **Core Lesson:** Balancing internal reflection with outer action
diff --git a/western/User_1983-11-10_04-20_Full_Reading.pdf b/western/User_1983-11-10_04-20_Full_Reading.pdf
deleted file mode 100644
index dd60443..0000000
Binary files a/western/User_1983-11-10_04-20_Full_Reading.pdf and /dev/null differ

```

--------------------------------------------------------------------------------

## Commit 3: 2a95e79

```diff
commit 2a95e79fca58360710ffbae65a4bb5bd7c545b32
Author: Shivapuri <142108173+Shivapuri@users.noreply.github.com>
Date:   Sun Aug 2 16:06:33 2026 +0530

    Format chart context JSON output filenames with name and birth timestamp

diff --git a/scripts/run_western_pipeline.py b/scripts/run_western_pipeline.py
index 39b583c..8aad232 100644
--- a/scripts/run_western_pipeline.py
+++ b/scripts/run_western_pipeline.py
@@ -152,7 +152,8 @@ def run_pipeline(
 
     # STEP 1: Generate Raw Chart JSON
     print("\n🔮 Step 1: Calculating Western Chart JSON via Engine...")
-    chart_json_path = os.path.join(BASE_DIR, "western", "chart_context.json")
+    chart_json_filename = f"{name}_{date_str}_chart_context.json"
+    chart_json_path = os.path.join(BASE_DIR, "western", chart_json_filename)
     chart_data = generate_ai_json(
         name=name,
         year=year,
diff --git a/western/generate_chart.py b/western/generate_chart.py
index 3dccb23..2bf037e 100644
--- a/western/generate_chart.py
+++ b/western/generate_chart.py
@@ -994,8 +994,12 @@ def generate_human_readable_report(subject, ai_payload, output_dir):
 # --- MAIN GENERATOR ---
 def generate_ai_json(
     name: str = "User", year: int = 1983, month: int = 11, day: int = 10, hour: int = 4, minute: int = 20,
-    city: str = "Georgsmarienhütte", country_code: str = "DE", output_filename: str = "chart_context.json", silent: bool = False
+    city: str = "Georgsmarienhütte", country_code: str = "DE", output_filename: str = None, silent: bool = False
 ):
+    if not output_filename or output_filename == "chart_context.json":
+        safe_name = name.replace(" ", "_")
+        output_filename = f"{safe_name}_{year:04d}-{month:02d}-{day:02d}_{hour:02d}-{minute:02d}_chart_context.json"
+
     try:
         subject = AstrologicalSubject(
             name, year, month, day, hour, minute, city, country_code,

```

--------------------------------------------------------------------------------

