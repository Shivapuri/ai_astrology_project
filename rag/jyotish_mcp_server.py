import os
import sys
import json

# Support both FastMCP (mcp < 2.0) and MCPServer (mcp >= 2.0)
try:
    from mcp.server import FastMCP
except ImportError:
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError:
        from mcp.server import MCPServer as FastMCP

# Ensure root modules can be imported relative to project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from jyotish.generate_jyotish import generate_vedic_chart
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

JYOTISH_INSTRUCTIONS = """
You are a Master Jyotishi (Senior Vedic Astrologer) operating Astra's Parashari Vedic Astrology System.
You operate purely within the Parashari system using Sidereal signs, Lahiri Ayanamsa, and Vimshottari Dashas.
NEVER use Western astrology, outer planets (Uranus, Neptune, Pluto), or psychological frameworks like Noel Tyl / Demetra George.

==============================================================================
VEDIC / JYOTISH ASTROLOGY WORKFLOW
==============================================================================
When a user requests a Vedic / Jyotish reading, follow this 4-Step ReAct workflow:

Step 1 (Action - Vedic Calculation):
  Call `calculate_vedic_chart` with native's birth details (latitude, longitude, timezone offset) to compute True Chitra Paksha (Lahiri) Ayanamsa, Panchanga, D1 Rasi, D9 Navamsa, and Vimshottari Dasha timeline.

Step 2 (Reasoning - Target Identification):
  Analyze the JSON and isolate key Jyotish placements:
  - Lagna & Moon Nakshatra: Ascendant sign/nakshatra, Moon sign/nakshatra/pada.
  - D9 Navamsa: Soul purpose, hidden strengths, and planet dignities in D9.
  - Dasha Timeline: Running Mahadasha, Antardasha, and Pratyantardasha periods.

Step 3 (Action - Classical & VedAstro Book Research):
  Call `query_vedic_astrology_books` 1 to 3 times to retrieve authentic classical shlokas (BPHS, Brihat Jataka) and VedAstro rules.

Step 4 (Synthesis - Empowering 4-Part Vedic Reading):
  Synthesize an empowering 4-part reading focusing on Karma, Dharma, and Timelines, translating ancient fatalistic language into modern constructive guidance:
  
  Part 1: Panchanga & Lagna Architecture
  (Explain Lagna sign, Nakshatra, Moon Pada, Tithi, and core physical/mental temperament).
  
  Part 2: D1 Rasi & D9 Navamsa Placements
  (Analyze dominant planets in D1 Rasi and their internal soul evolution in D9 Navamsa).
  
  Part 3: Vimshottari Dasha Timeline & Karmic Evolution
  (Analyze current running Dasha period, timing of major life shifts, and active karmic lessons).
  
  Part 4: Practical Dharma & Remedies
  (Offer constructive guidance for growth, ethical living, emotional resilience, and boundary management).
"""

try:
    mcp = FastMCP(
        "Astra Vedic Jyotish Server",
        instructions=JYOTISH_INSTRUCTIONS
    )
except TypeError:
    mcp = FastMCP("Astra Vedic Jyotish Server")

JYOTISH_CHROMA_DB_DIR = os.path.join(BASE_DIR, "rag", "chroma_jyotish_db")


@mcp.tool()
def calculate_vedic_chart(
    name: str = "Subject",
    year: int = 1995,
    month: int = 5,
    day: int = 15,
    hour: int = 14,
    minute: int = 30,
    latitude: float = 51.5074,
    longitude: float = -0.1278,
    timezone_offset: float = 1.0
) -> str:
    """
    [VEDIC/JYOTISH ENGINE ONLY - DO NOT USE FOR WESTERN]
    Calculates a mathematically precise Parashari Vedic (Sidereal) Astrology Chart using jyotishganit.
    Returns structured JSON containing True Chitra Paksha (Lahiri) Ayanamsa, Panchanga, D1 Rasi Chart, 
    D9 Navamsa Chart, and Vimshottari Dasha timeline.
    
    Vedic CoT Step 1: Execute this tool first when analyzing a Vedic chart.
    """
    output_path = os.path.join(BASE_DIR, "jyotish", "vedic_context.json")
    try:
        chart_data = generate_vedic_chart(
            name=name,
            year=year,
            month=month,
            day=day,
            hour=hour,
            minute=minute,
            latitude=latitude,
            longitude=longitude,
            timezone_offset=timezone_offset,
            output_filepath=output_path
        )
        return json.dumps(chart_data, indent=2, ensure_ascii=False)
    except Exception as e:
        return f"Error generating Vedic chart: {str(e)}"


@mcp.tool()
def query_vedic_astrology_books(query: str) -> str:
    """
    [VEDIC/JYOTISH ENGINE ONLY - DO NOT USE FOR WESTERN]
    Queries the local Jyotish Vector Database (containing WisdomLib BPHS texts and VedAstro rules).
    Use this to look up Nakshatras, Dashas, and Parashari rules.
    Pass targeted Vedic queries such as 'Lagna in Aries Ashwini' or 'Vimshottari Dasha Saturn Mahadasha'.
    
    Vedic CoT Step 3: Call this tool 1 to 3 times for key Vedic chart placements and Dashas.
    """
    try:
        if not os.path.exists(JYOTISH_CHROMA_DB_DIR):
            return "Vedic Vector database not found. Please run fetch_jyotish_data.py and build_jyotish_rag.py first."
            
        embedding_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        vector_store = Chroma(
            persist_directory=JYOTISH_CHROMA_DB_DIR,
            embedding_function=embedding_model
        )
        results = vector_store.similarity_search(query, k=4)
        
        output = f"=== VEDIC / JYOTISH RAG SEARCH RESULTS FOR: '{query}' ===\n\n"
        for idx, doc in enumerate(results, 1):
            source = os.path.basename(doc.metadata.get("source", "jyotish_text"))
            output += f"--- Result {idx} [Source: {source}] ---\n{doc.page_content}\n\n"
        return output
    except Exception as e:
        return f"Error querying Vedic vector database: {str(e)}"


if __name__ == "__main__":
    mcp.run()
