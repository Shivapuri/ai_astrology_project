#!/usr/bin/env python3
"""
Parallel Specialized Multi-Agent Western Astrology Pipeline Orchestrator (Headless AGY Mode).

Architecture:
- Step 1: Python calculates birth chart JSON natively via Western engine.
- Step 2: Python queries local Chroma Vector DB (chroma_astrology_db) natively for targeted structural & psychological excerpts.
- Step 3: Agent 1 (Structural & Hellenistic Profiler) executes headlessly via AGY using Gemini 3.1 Pro (High).
- Step 4: Agent 2 (Psychological & Aspect Profiler) executes headlessly via AGY using Gemini 3.1 Pro (High).
- Step 5: Agent 3 (Master Astrologer Synthesizer) executes headlessly via AGY using Gemini 3.1 Pro (High) to weave reports into a comprehensive narrative.
- Step 6: Automatically generates publication-grade PDF report and cleans up intermediate artifacts.
"""

import os
import sys
import json
import argparse
import subprocess
from typing import Dict, Any, List

# Ensure project root is in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from western.generate_chart import generate_ai_json
from scripts.generate_pdf import generate_pdf
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

CHROMA_STRUCTURAL_DB_DIR = os.path.join(BASE_DIR, "rag", "chroma_structural_db")
CHROMA_MODERN_DB_DIR = os.path.join(BASE_DIR, "rag", "chroma_modern_db")


def load_prompt(filename: str) -> str:
    """Loads prompt XML file from the /prompts/ directory."""
    path = os.path.join(BASE_DIR, "prompts", filename)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Prompt file not found at {path}")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def query_local_rag_db(db_dir: str, queries: List[str], max_results_per_query: int = 3) -> str:
    """Queries a specific local Chroma Vector DB directly without API calls."""
    if not os.path.exists(db_dir):
        return f"⚠️ Vector database not found at {db_dir}."
        
    try:
        embedding_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        vector_store = Chroma(
            persist_directory=db_dir,
            embedding_function=embedding_model
        )
        
        output_chunks = []
        seen = set()
        
        for q in queries:
            results = vector_store.similarity_search(q, k=max_results_per_query)
            output_chunks.append(f"### Search Topic: '{q}'")
            for idx, doc in enumerate(results, 1):
                content = doc.page_content.strip()
                if content not in seen:
                    seen.add(content)
                    source = os.path.basename(doc.metadata.get("source", "Classical Text"))
                    page = doc.metadata.get("page", "N/A")
                    output_chunks.append(f"--- [Source: {source}, Page: {page}] ---\n{content}\n")
                    
        return "\n".join(output_chunks)
    except Exception as e:
        return f"Error querying local Chroma DB at {db_dir}: {e}"


def run_agent_headless(
    agent_name: str, 
    system_prompt: str, 
    user_payload: str, 
    model_name: str, 
    trace_log_path: str, 
    timeout_seconds: int = 600
) -> str:
    """
    Runs an AI agent via the Antigravity CLI (agy) in headless mode.
    No API keys or billed network calls are used.
    """
    print(f"\n🤖 Starting headless AGY execution for agent: {agent_name}")
    print(f"   Model: {model_name} | Timeout: {timeout_seconds}s")
    
    os.makedirs(os.path.dirname(os.path.abspath(trace_log_path)), exist_ok=True)
    full_prompt = f"{system_prompt}\n\n{user_payload}"
    
    cli_path = "/Users/hajnaljanos/.local/bin/agy"
    if not os.path.exists(cli_path):
        cli_path = "agy"
        
    cmd = [
        cli_path,
        "--dangerously-skip-permissions",
        "--log-file",
        trace_log_path,
        "--model",
        model_name,
        "--print",
        full_prompt
    ]
    
    try:
        result = subprocess.run(
            cmd,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            timeout=timeout_seconds
        )
        
        output_text = result.stdout.strip()
        if not output_text and os.path.exists(trace_log_path):
            with open(trace_log_path, "r", encoding="utf-8") as f:
                output_text = f.read()
                
        return output_text
        
    except subprocess.TimeoutExpired as e:
        with open(trace_log_path, "w", encoding="utf-8") as f:
            f.write(f"TimeoutExpired: Process timed out after {e.timeout} seconds.")
        raise RuntimeError(f"CLI execution for {agent_name} timed out after {e.timeout} seconds.")


def run_pipeline(
    name: str = "User",
    year: int = 1983,
    month: int = 11,
    day: int = 10,
    hour: int = 4,
    minute: int = 20,
    city: str = "Georgsmarienhütte",
    country_code: str = "DE",
    structural_model: str = "Gemini 3.1 Pro (High)",
    psychological_model: str = "Gemini 3.1 Pro (High)",
    synthesizer_model: str = "Gemini 3.1 Pro (High)"
):
    date_str = f"{year:04d}-{month:02d}-{day:02d}_{hour:02d}-{minute:02d}"
    print("======================================================================")
    print("  Western Astrology Multi-Agent Parallel Pipeline (Headless AGY)")
    print("======================================================================")
    print(f" Target: {name} | Date/Time: {date_str}")
    print(f" Location: {city}, {country_code}")
    print(f" Models: Agent 1={structural_model} | Agent 2={psychological_model} | Agent 3={synthesizer_model}")
    print("----------------------------------------------------------------------")

    # STEP 1: Generate Raw Chart JSON
    print("\n🔮 Step 1: Calculating Western Chart JSON via Engine...")
    chart_json_filename = f"{name}_{date_str}_chart_context.json"
    chart_json_path = os.path.join(BASE_DIR, "western", chart_json_filename)
    chart_data = generate_ai_json(
        name=name,
        year=year,
        month=month,
        day=day,
        hour=hour,
        minute=minute,
        city=city,
        country_code=country_code,
        output_filename=chart_json_path,
        silent=True
    )
    
    if not chart_data and os.path.exists(chart_json_path):
        with open(chart_json_path, "r", encoding="utf-8") as f:
            chart_data = json.load(f)
            
    chart_json_str = json.dumps(chart_data, indent=2)
    print("✅ Raw Chart JSON successfully generated.")

    native = chart_data.get("native_details", {})
    planets = chart_data.get("traditional_planets", {})
    asc_sign = native.get("ascendant", "Ascendant")
    sect = native.get("sect", "Chart Sect")
    
    # STEP 2: Pre-fetch Domain-Isolated Vector DB Context for Agent 1 & Agent 2
    print("\n📚 Step 2: Querying Domain-Isolated Chroma DBs (Structural & Modern Psychological)...")
    struct_queries = [
        f"Ascendant in {asc_sign} in a {sect}",
        f"Chart ruler position in {asc_sign} whole sign house",
        "Essential dignities domicile detriment fall classical mechanics",
        f"Sun in {planets.get('Sun', {}).get('sign')} Moon in {planets.get('Moon', {}).get('sign')}"
    ]
    psych_queries = [
        f"Solar-Lunar blend Sun in {planets.get('Sun', {}).get('sign')} Moon in {planets.get('Moon', {}).get('sign')}",
        "Hard aspect developmental tension square opposition conjunction",
        f"Saturn placement in {planets.get('Saturn', {}).get('sign')} emotional defenses pain body",
        f"Mars placement in {planets.get('Mars', {}).get('sign')} internal conflicts"
    ]
    
    structural_rag_context = query_local_rag_db(CHROMA_STRUCTURAL_DB_DIR, struct_queries, max_results_per_query=2)
    psychological_rag_context = query_local_rag_db(CHROMA_MODERN_DB_DIR, psych_queries, max_results_per_query=2)
    print("✅ Domain-isolated Vector DB contexts extracted natively.")

    # STEP 3: Run Agent 1 (Structural & Hellenistic Profiler via Headless AGY)
    print("\n🏛️ Step 3: Executing Agent 1 (Structural Profiler - Demetra George Framework)...")
    agent1_prompt = load_prompt("agent1_structural.xml")
    agent1_payload = (
        f"=== RAW CHART JSON ===\n{chart_json_str}\n\n"
        f"=== RETRIEVED VECTOR DB GROUND TRUTH (STRUCTURAL CONTEXT) ===\n{structural_rag_context}\n\n"
        "Please provide a comprehensive, deeply reflective report analyzing the exact objective "
        "mechanics of this chart according to your instructions and focus areas. Do not truncate your analysis."
    )
    agent1_log = os.path.join(BASE_DIR, "western", "logs", f"{name}_agent1_trace.txt")
    structural_report = run_agent_headless(
        agent_name="Agent 1 (Structural)",
        system_prompt=agent1_prompt,
        user_payload=agent1_payload,
        model_name=structural_model,
        trace_log_path=agent1_log,
        timeout_seconds=600
    )

    # STEP 4: Run Agent 2 (Psychological & Aspect Profiler via Headless AGY)
    print("\n🧠 Step 4: Executing Agent 2 (Psychological Profiler - Noel Tyl Framework)...")
    agent2_prompt = load_prompt("agent2_psychological.xml")
    agent2_payload = (
        f"=== RAW CHART JSON ===\n{chart_json_str}\n\n"
        f"=== RETRIEVED VECTOR DB GROUND TRUTH (PSYCHOLOGICAL CONTEXT) ===\n{psychological_rag_context}\n\n"
        "Please provide a comprehensive, deep psychological report analyzing the subjective needs, frictions, "
        "and pain body dynamics according to your instructions."
    )
    agent2_log = os.path.join(BASE_DIR, "western", "logs", f"{name}_agent2_trace.txt")
    psychological_report = run_agent_headless(
        agent_name="Agent 2 (Psychological)",
        system_prompt=agent2_prompt,
        user_payload=agent2_payload,
        model_name=psychological_model,
        trace_log_path=agent2_log,
        timeout_seconds=600
    )

    # STEP 5: Run Agent 3 (Master Astrologer Synthesizer via Headless AGY)
    print("\n✨ Step 5: Executing Agent 3 (Master Astrologer Synthesizer)...")
    agent3_prompt = load_prompt("agent3_synthesizer.xml")
    agent3_payload = (
        f"=== RAW CHART JSON ===\n{chart_json_str}\n\n"
        f"=== AGENT 1: STRUCTURAL REPORT ===\n{structural_report}\n\n"
        f"=== AGENT 2: PSYCHOLOGICAL REPORT ===\n{psychological_report}\n\n"
        "Please synthesize both reports into a rich, deep, conversational astrological reading. "
        "Follow your formatting guidelines strictly, ensuring every concept is followed by a concrete "
        "'Day-in-the-Life Reality' behavioral example."
    )
    agent3_log = os.path.join(BASE_DIR, "western", "logs", f"{name}_agent3_trace.txt")
    final_reading = run_agent_headless(
        agent_name="Agent 3 (Synthesizer)",
        system_prompt=agent3_prompt,
        user_payload=agent3_payload,
        model_name=synthesizer_model,
        trace_log_path=agent3_log,
        timeout_seconds=900
    )

    # STEP 6: Save Final Markdown Output with Date/Time naming convention
    md_filename = f"{name}_{date_str}_Full_Reading.md"
    md_path = os.path.join(BASE_DIR, "western", md_filename)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(final_reading)
    print(f"✅ Saved Markdown Reading: {md_path}")

    # STEP 7: Generate Publication-Grade PDF
    print("\n📄 Step 7: Generating Publication-Grade PDF Report...")
    pdf_filename = f"{name}_{date_str}_Full_Reading.pdf"
    pdf_path = os.path.join(BASE_DIR, "western", pdf_filename)
    generate_pdf(md_path, pdf_path)

    print("\n======================================================================")
    print("🎉 Pipeline Complete!")
    print(f"   Markdown Reading: {md_path}")
    print(f"   PDF Reading:      {pdf_path}")
    print("======================================================================")
    return pdf_path


def main():
    parser = argparse.ArgumentParser(description="Run Western Astrology Multi-Agent Pipeline (Headless AGY).")
    parser.add_argument("--name", type=str, default="User", help="Target Name")
    parser.add_argument("--year", type=int, default=1983, help="Birth Year")
    parser.add_argument("--month", type=int, default=11, help="Birth Month")
    parser.add_argument("--day", type=int, default=10, help="Birth Day")
    parser.add_argument("--hour", type=int, default=4, help="Birth Hour (0-23)")
    parser.add_argument("--minute", type=int, default=20, help="Birth Minute")
    parser.add_argument("--city", type=str, default="Georgsmarienhütte", help="Birth City")
    parser.add_argument("--country", type=str, default="DE", help="Country Code")
    
    # Model configuration flags
    parser.add_argument("--model", type=str, help="Blanket model override for all agents")
    parser.add_argument("--structural-model", type=str, default="Gemini 3.1 Pro (High)", help="Model for Agent 1")
    parser.add_argument("--psychological-model", type=str, default="Gemini 3.1 Pro (High)", help="Model for Agent 2")
    parser.add_argument("--synthesizer-model", type=str, default="Gemini 3.1 Pro (High)", help="Model for Agent 3")
    
    args = parser.parse_args()
    
    struct_mod = args.model or args.structural_model
    psych_mod = args.model or args.psychological_model
    synth_mod = args.model or args.synthesizer_model
    
    run_pipeline(
        name=args.name,
        year=args.year,
        month=args.month,
        day=args.day,
        hour=args.hour,
        minute=args.minute,
        city=args.city,
        country_code=args.country,
        structural_model=struct_mod,
        psychological_model=psych_mod,
        synthesizer_model=synth_mod
    )


if __name__ == "__main__":
    main()
