import os
import sys
import time
from typing import List, Dict

# Ensure project root is in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

MODERN_DB_DIR = os.path.join(BASE_DIR, "rag", "chroma_modern_db")
STRUCT_DB_DIR = os.path.join(BASE_DIR, "rag", "chroma_structural_db")

TEST_CASES = [
    {
        "name": "Modern DB: Sun in Scorpio",
        "db_path": MODERN_DB_DIR,
        "query": "Sun in Scorpio core identity and psychology",
        "expected_keywords": ["power", "transform", "regeneration", "desire", "energy", "psyche", "solar"]
    },
    {
        "name": "Modern DB: Moon in Capricorn",
        "db_path": MODERN_DB_DIR,
        "query": "Moon in Capricorn reigning emotional need",
        "expected_keywords": ["emotional", "need", "security", "reserve", "psyche", "feeling", "nature"]
    },
    {
        "name": "Modern DB: Pain Body (Saturn/Venus)",
        "db_path": MODERN_DB_DIR,
        "query": "Saturn conjunct Venus emotional defense and pain body",
        "expected_keywords": ["saturn", "venus", "relationship", "love", "defense", "fear", "expression"]
    },
    {
        "name": "Structural DB: Taurus Ascendant",
        "db_path": STRUCT_DB_DIR,
        "query": "Taurus Ascendant physical vehicle and temperament",
        "expected_keywords": ["ascendant", "persona", "personality", "character", "appearance", "taurus", "image"]
    },
    {
        "name": "Structural DB: Aversion",
        "db_path": STRUCT_DB_DIR,
        "query": "Chart ruler in the 8th house aversion",
        "expected_keywords": ["aversion", "eighth", "twelfth", "sixth", "ruler", "house", "blind"]
    }
]


def run_quality_tests():
    print("======================================================================")
    print(" 🧪 RUNNING RAG RETRIEVAL QUALITY & RELEVANCE SUITE")
    print("======================================================================")
    
    if not os.path.exists(MODERN_DB_DIR) or not os.path.exists(STRUCT_DB_DIR):
        print("❌ Error: Vector databases not found. Build them first.")
        return

    print("Loading Embedding Model (all-MiniLM-L6-v2)...")
    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    
    # Load DBs
    dbs = {
        MODERN_DB_DIR: Chroma(persist_directory=MODERN_DB_DIR, embedding_function=embedding_model),
        STRUCT_DB_DIR: Chroma(persist_directory=STRUCT_DB_DIR, embedding_function=embedding_model)
    }

    total_tests = len(TEST_CASES)
    passed_tests = 0
    start_time = time.time()

    for i, test in enumerate(TEST_CASES, 1):
        print(f"\n[Test {i}/{total_tests}] {test['name']}")
        print(f"  Query: '{test['query']}'")
        
        db = dbs[test['db_path']]
        results = db.similarity_search(test['query'], k=4)
        
        if not results:
            print("  ❌ FAIL: No results returned.")
            continue
            
        combined_text = " ".join([doc.page_content.lower() for doc in results])
        
        # Calculate relevance
        hits = 0
        found_words = []
        missed_words = []
        
        for kw in test['expected_keywords']:
            if kw.lower() in combined_text:
                hits += 1
                found_words.append(kw)
            else:
                missed_words.append(kw)
                
        relevance_score = (hits / len(test['expected_keywords'])) * 100
        
        print(f"  Found Keywords: {found_words}")
        if missed_words:
            print(f"  Missed Keywords: {missed_words}")
        
        if relevance_score >= 40.0:  # 40% keyword hit rate is a very strong semantic signal for RAG
            print(f"  ✅ PASS: Relevance Score {relevance_score:.1f}%")
            passed_tests += 1
        else:
            print(f"  ❌ FAIL: Relevance Score {relevance_score:.1f}% (Below 40% threshold)")

    duration = time.time() - start_time
    print("\n======================================================================")
    print(" 📊 QA TEST SUMMARY")
    print("======================================================================")
    print(f" Total Tests Run : {total_tests}")
    print(f" Passed          : {passed_tests}")
    print(f" Failed          : {total_tests - passed_tests}")
    print(f" Time Taken      : {duration:.2f} seconds")
    print("======================================================================")
    
    if passed_tests == total_tests:
        print("🏆 SUCCESS: All RAG databases are highly functional and relevant.")
    else:
        print("⚠️ WARNING: Some queries returned low-relevance documents. Database tuning may be required.")

if __name__ == "__main__":
    run_quality_tests()
