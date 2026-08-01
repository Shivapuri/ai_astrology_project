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

# 1. Instantiate MCP Server
mcp = FastMCP("Astra Hellenistic Astrology RAG Engine")

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
    Calculates a mathematically precise Hellenistic Western Astrology Chart.
    Returns structured JSON with Ascendant, Sect (Day/Night), 7 Traditional Planets 
    (with Signs, Whole Sign Houses, Essential Dignities, Egyptian Terms, Dodecatemoria), 
    and 7 Hermetic Lots.
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
def query_ancient_texts(query: str) -> str:
    """
    Queries the local Hellenistic Vector RAG Database (containing Ptolemy's Tetrabiblos, 
    Vettius Valens, and Dorotheus ground truth rules).
    Pass a query like 'What does Mars in Fall in Cancer in 6th house mean in a Day Chart?'
    """
    try:
        embedding_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        vector_store = Chroma(
            persist_directory=CHROMA_DB_DIR,
            embedding_function=embedding_model
        )
        results = vector_store.similarity_search(query, k=4)
        
        output = f"=== CLASSICAL RAG SEARCH RESULTS FOR: '{query}' ===\n\n"
        for idx, doc in enumerate(results, 1):
            output += f"--- Result {idx} ---\n{doc.page_content}\n\n"
        return output
    except Exception as e:
        return f"Error querying vector database: {str(e)}"

if __name__ == "__main__":
    mcp.run()
