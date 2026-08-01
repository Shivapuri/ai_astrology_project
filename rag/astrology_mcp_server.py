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
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

COT_SYSTEM_INSTRUCTIONS = """
You are a Principal Modern Psychological Astrologer and AI Agent driven by a strict Chain of Thought (CoT) / ReAct reasoning protocol.

Whenever a user requests a birth chart reading, you MUST autonomously execute this 4-step workflow:

Step 1 (Action - Mathematical Calculation):
  Call the `calculate_birth_chart` tool with the native's birth details to compute the exact planetary positions, dignities, sect, and lots.

Step 2 (Reasoning - Target Identification):
  Analyze the JSON and isolate the planets that trigger the psychological framework:
  - Identity: Ascendant, Chart Ruler, and Sect Light.
  - Pain Body & Trauma: The Moon, planets in Detriment/Fall, or the out-of-sect Malefic.
  - Social & Conflict: Venus (connection), Mars (boundaries/anger), and hard aspects (Squares/Oppositions).
  - Flow State: Domicile planets, Jupiter, and the Lot of Fortune.

Step 3 (Action - Psychological Book Research):
  Call `query_modern_astrology_books` 2 to 3 times to research these specific placements in the local vector database.

Step 4 (Synthesis - The Extended Reading):
  Output a highly empathetic, modern reading that strictly follows this 5-part structure:
  
  Part 1: The Core Architecture of the Chart
  (Explain Ascendant, Sect, and House layout in simple terms).
  
  Part 2: The Dominant Placements & Psychological Reading
  (First provide an educational overview of the general characteristics and archetypes of the dominant zodiac signs active in the chart—such as their element, ruling planets, and overall psychological themes. Then analyze the top 3 specific placements using bullet points for 'Mathematical Placement' and 'What It Means for You'. Address the native's "Pain Body" and emotional shadows here using their most difficult placement).
  
  Part 3: Behavioral Psychology (Socialization & Conflict)
  (NEW EXTENSION: Explicitly analyze how they make friends and experience intimacy based on Venus/11th House, and how they resolve conflict, fight, or protect boundaries based on Mars/Aspects).
  
  Part 4: Supporting Strengths & Fortune
  (Analyze Jupiter, the Lot of Fortune, and where they naturally hit a "Flow State").
  
  Summary Checklist of Your Chart Profile
  (Provide a quick bulleted list: Their Archetype, their Superpower, and their Core Life Lesson).
"""

# 1. Instantiate MCP Server with Chain of Thought instructions
try:
    mcp = FastMCP(
        "Astra Modern Psychological Astrology RAG Engine",
        instructions=COT_SYSTEM_INSTRUCTIONS
    )
except TypeError:
    mcp = FastMCP("Astra Modern Psychological Astrology RAG Engine")

CHROMA_DB_DIR = os.path.join(BASE_DIR, "rag", "chroma_astrology_db")

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
    Calculates a mathematically precise Western Astrology Chart.
    Returns structured JSON containing the Ascendant, Sect (Day/Night), traditional and modern planetary placements 
    (with Signs, Whole Sign Houses, and Dignities), and Hermetic Lots.
    
    Chain of Thought Step 1: Execute this tool first when analyzing a user's chart.
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
        return f"Error generating chart: {str(e)}"

@mcp.tool()
def query_modern_astrology_books(query: str) -> str:
    """
    Queries the local Modern Psychological Astrology Vector Database (containing digitized modern books).
    Pass targeted psychological queries such as 'Moon in Taurus in 2nd House' or 'Saturn transit square Sun'.
    
    Chain of Thought Step 3: Call this tool 1 to 3 times for key chart placements identified in Step 2.
    """
    try:
        if not os.path.exists(CHROMA_DB_DIR):
            return "Vector database not found. Please ensure build_rag_pipeline.py has completed building ChromaDB."
            
        embedding_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        vector_store = Chroma(
            persist_directory=CHROMA_DB_DIR,
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
        return f"Error querying vector database: {str(e)}"

if __name__ == "__main__":
    mcp.run()
