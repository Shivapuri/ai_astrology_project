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

PROMPT_PATH = os.path.join(BASE_DIR, "prompts", "western_analysis.xml")
with open(PROMPT_PATH, "r", encoding="utf-8") as f:
    WESTERN_INSTRUCTIONS = f.read()


try:
    mcp = FastMCP(
        "Astra Western Astrology Server",
        instructions=WESTERN_INSTRUCTIONS
    )
except TypeError:
    mcp = FastMCP("Astra Western Astrology Server")

WESTERN_CHROMA_MODERN_DB_DIR = os.path.join(BASE_DIR, "rag", "chroma_modern_db")
WESTERN_CHROMA_STRUCTURAL_DB_DIR = os.path.join(BASE_DIR, "rag", "chroma_structural_db")


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
    [WESTERN ENGINE ONLY - DO NOT USE FOR JYOTISH]
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
    [WESTERN ENGINE ONLY - DO NOT USE FOR JYOTISH]
    Queries the local Modern Psychological & Structural Astrology Vector Databases.
    Use this to look up Demetra George, Robert Hand, Stephen Arroyo, and Tracy Marks.
    Pass targeted queries such as 'Moon in Taurus in 2nd House' or 'Saturn transit square Sun'.
    
    Western CoT Step 3: Call this tool 1 to 3 times for key chart placements.
    """
    try:
        target_db = WESTERN_CHROMA_MODERN_DB_DIR if os.path.exists(WESTERN_CHROMA_MODERN_DB_DIR) else WESTERN_CHROMA_STRUCTURAL_DB_DIR
        if not os.path.exists(target_db):
            return "Western Vector database not found. Please run build_rag_pipeline.py first."
            
        embedding_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        vector_store = Chroma(
            persist_directory=target_db,
            embedding_function=embedding_model
        )
        results = vector_store.similarity_search(query, k=4)
        
        output = f"=== WESTERN ASTROLOGY RAG SEARCH RESULTS FOR: '{query}' ===\n\n"
        for idx, doc in enumerate(results, 1):
            source = os.path.basename(doc.metadata.get("source", "astrology_book"))
            page = doc.metadata.get("page", "N/A")
            output += f"--- Result {idx} [Source: {source}, Page: {page}] ---\n{doc.page_content}\n\n"
        return output
    except Exception as e:
        return f"Error querying Western vector database: {str(e)}"



if __name__ == "__main__":
    mcp.run()
