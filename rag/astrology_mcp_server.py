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

from western.generate_chart import generate_ai_json
from jyotish.generate_jyotish import generate_vedic_chart
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

COT_SYSTEM_INSTRUCTIONS = """
You are a Principal AI Architect and Master Astrologer operating Astra's Dual-Engine Astrology System.
You support both Western Psychological Astrology and Parashari Vedic Astrology (Jyotish) via strict Chain of Thought (CoT) protocols.

==============================================================================
WESTERN / PSYCHOLOGICAL ASTROLOGY WORKFLOW
==============================================================================
When a user requests a Western chart reading, follow this 4-Step ReAct workflow:

Step 1 (Action - Mathematical Calculation):
  Call `calculate_birth_chart` with native's birth details to compute exact tropical placements, Whole Sign houses, dignities, sect, and hermetic lots.

Step 2 (Reasoning - The 'Mask vs. Fortress' Framework):
  Analyze the JSON to understand the native's psychological layers. NEVER read placements in isolated silos.
  - Layer 1: The Social Mask (Ascendant & Chart Ruler). How do they interact superficially? (e.g., Libra Rising + Venus in 1st = Charming, diplomatic, polite).
  - Layer 2: The Inner Fortress (The Moon & The Sun). How do they actually process trust, vulnerability, and safety? (e.g., Scorpio Sun + Capricorn Moon = Guarded, private, slow to trust).
  - The Synthesis (Friction/Resolution): You MUST explicitly contrast Layer 1 and Layer 2. Explain how the Mask protects the Fortress. (e.g., "You use your polite Libra charm to navigate crowds smoothly, but because of your Scorpio/Capricorn core, you keep high walls up and require a long time before letting anyone truly know you.")
  - Also identify: Pain Body (Detriment/Fall planets), Conflict style (Mars), and Flow State (Jupiter/Fortune).

Step 3 (Action - Western Book Research):
  Call `query_modern_astrology_books` 1 to 3 times for target placements.

Step 4 (Synthesis - Modern Psychological Reading):
  Synthesize a 5-part empathetic, highly cohesive reading:
  Part 1: The Core Architecture & The "Mask vs. Fortress" Dynamic (Explain their Ascendant, but immediately contrast it with their inner Sun/Moon reality to show how they actually operate).
  Part 2: The Inner World & The Pain Body (Deep dive into the Sun, Moon, and their hardest emotional placements/defenses).
  Part 3: Behavioral Psychology (Socialization, Trust, Intimacy & Conflict Resolution - based on your synthesis from Step 2).
  Part 4: Supporting Strengths & Fortune (Jupiter, Lot of Fortune, and Flow States).
  Summary Checklist of Your Chart Profile (Archetype, Superpower, Core Life Lesson).

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

# 1. Instantiate MCP Server with Dual-Engine Chain of Thought instructions
try:
    mcp = FastMCP(
        "Astra Dual-Engine Astrology RAG Server",
        instructions=COT_SYSTEM_INSTRUCTIONS
    )
except TypeError:
    mcp = FastMCP("Astra Dual-Engine Astrology RAG Server")

WESTERN_CHROMA_DB_DIR = os.path.join(BASE_DIR, "rag", "chroma_astrology_db")
JYOTISH_CHROMA_DB_DIR = os.path.join(BASE_DIR, "rag", "chroma_jyotish_db")


# ------------------------------------------------------------------------------
# WESTERN ASTROLOGY TOOLS
# ------------------------------------------------------------------------------

@mcp.tool()
def calculate_birth_chart(
    name: str = "User",
    year: int = 1990,
    month: int = 1,
    day: int = 1,
    hour: int = 12,
    minute: int = 0,
    city: str = "London",
    country_code: str = "GB"
) -> str:
    """
    Calculates a mathematically precise Western (Tropical) Astrology Chart.
    Returns structured JSON containing the Ascendant, Sect (Day/Night), traditional and modern planetary placements
    (with Signs, Whole Sign Houses, and Dignities), and Hermetic Lots.
    
    Western CoT Step 1: Execute this tool first when analyzing a Western chart.
    """
    output_path = os.path.join(BASE_DIR, "western", "chart_context.json")
    try:
        generate_ai_json(
            name=name,
            year=year,
            month=month,
            day=day,
            hour=hour,
            minute=minute,
            city=city,
            country_code=country_code,
            output_filename=output_path,
            silent=True
        )
        with open(output_path, "r", encoding="utf-8") as f:
            chart_data = json.load(f)
        return json.dumps(chart_data, indent=2)
    except Exception as e:
        return f"Error generating Western chart: {str(e)}"


@mcp.tool()
def query_modern_astrology_books(query: str) -> str:
    """
    Queries the local Modern Psychological Astrology Vector Database (containing modern Western books).
    Pass targeted psychological queries such as 'Moon in Taurus in 2nd House' or 'Saturn transit square Sun'.
    
    Western CoT Step 3: Call this tool 1 to 3 times for key chart placements.
    """
    try:
        if not os.path.exists(WESTERN_CHROMA_DB_DIR):
            return "Western Vector database not found. Please run build_rag_pipeline.py first."
            
        embedding_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        vector_store = Chroma(
            persist_directory=WESTERN_CHROMA_DB_DIR,
            embedding_function=embedding_model
        )
        results = vector_store.similarity_search(query, k=4)
        
        output = f"=== MODERN PSYCHOLOGICAL ASTROLOGY RAG SEARCH RESULTS FOR: '{query}' ===\n\n"
        for idx, doc in enumerate(results, 1):
            source = os.path.basename(doc.metadata.get("source", "modern_astrology_book"))
            page = doc.metadata.get("page", "N/A")
            output += f"--- Result {idx} [Source: {source}, Page: {page}] ---\n{doc.page_content}\n\n"
        return output
    except Exception as e:
        return f"Error querying Western vector database: {str(e)}"


# ------------------------------------------------------------------------------
# VEDIC / JYOTISH ASTROLOGY TOOLS
# ------------------------------------------------------------------------------

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
    Queries the local Jyotish Vector Database (containing WisdomLib BPHS texts and VedAstro rules).
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
