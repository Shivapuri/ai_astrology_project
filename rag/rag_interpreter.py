import os
import json
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

CHROMA_DB_DIR = os.path.join(os.path.dirname(__file__), "chroma_astrology_db")
CHART_JSON_PATH = os.path.join(os.path.dirname(__file__), "..", "western", "chart_context.json")

def load_chart_json(file_path=CHART_JSON_PATH):
    """Load and parse the chart context JSON file."""
    if not os.path.exists(file_path):
        # Fallback check for root or rag folder
        alt_path = os.path.join(os.path.dirname(__file__), "chart_context.json")
        if os.path.exists(alt_path):
            file_path = alt_path
        else:
            raise FileNotFoundError(f"Chart file not found at {file_path} or {alt_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def retrieve_classical_context(vector_store, native_details, planet_name, planet_data):
    """Perform a multi-query semantic search for high-accuracy RAG retrieval."""
    sign = planet_data.get("sign", "")
    house = planet_data.get("whole_sign_house", "").replace("_", " ") # Convert "House_2" to "House 2"
    dignity = planet_data.get("essential_dignity", "").split(" ")[0] # Extract just "Detriment" or "Domicile"
    sect = native_details.get("sect", "")
    
    # MULTI-QUERY STRATEGY: Vector DBs respond better to specific semantic questions
    queries = [
        f"What is the astrological meaning of {planet_name} in the sign of {sign}?",
        f"How does {planet_name} behave in the {house}?",
        f"What happens when {planet_name} is in {dignity} dignity in a {sect}?"
    ]
    
    retrieved_texts = []
    seen = set()
    
    # Query the DB for each semantic question
    for q in queries:
        results = vector_store.similarity_search(q, k=2) # Get top 2 for each specific question
        for doc in results:
            content = doc.page_content.strip()
            if content not in seen:
                seen.add(content)
                retrieved_texts.append(content)
                
    # Return the combined context
    return " | ".join(queries), retrieved_texts[:4]

def interpret_chart_with_rag():
    print("--- Phase 3: Classical RAG Chart Interpreter ---")
    
    # 1. Load Chart JSON
    chart_data = load_chart_json()
    native = chart_data.get("native_details", {})
    planets = chart_data.get("traditional_planets", {})
    
    print(f"Loaded Chart for Ascendant: {native.get('ascendant')} | Sect: {native.get('sect')}")

    # 2. Connect to Chroma Vector Store
    print("Connecting to local Chroma Vector Database...")
    embedding_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    vector_store = Chroma(
        persist_directory=CHROMA_DB_DIR,
        embedding_function=embedding_model
    )

    # 3. Retrieve context for all traditional placements
    retrieved_knowledge = []
    
    print("\nExtracting placements and querying RAG DB...")
    for planet_name, planet_info in planets.items():
        query, context_chunks = retrieve_classical_context(vector_store, native, planet_name, planet_info)
        context_str = "\n".join([f"   - {chunk}" for chunk in context_chunks])
        retrieved_knowledge.append({
            "planet": planet_name,
            "placement": f"{planet_name} in {planet_info.get('sign')} ({planet_info.get('whole_sign_house')}) - Dignity: {planet_info.get('essential_dignity')}",
            "query": query,
            "retrieved_context": context_str
        })

    # 4. Construct Strict System Prompt & Full LLM Payload
    system_prompt = (
        "STRICT SYSTEM PROMPT:\n"
        "You are a Hellenistic Astrologer. You must ONLY use the provided classical RAG context "
        "and chart JSON below to interpret this chart.\n"
        "DO NOT use modern psychological astrology, pop astrology, outer planets, or unverified outside knowledge.\n"
        "Base all judgments strictly on Essential Dignities, Chart Sect (Day/Night), and Whole Sign House topology."
    )

    prompt_payload = f"=== SYSTEM INSTRUCTION ===\n{system_prompt}\n\n"
    prompt_payload += f"=== NATIVE CHART DETAILS ===\n{json.dumps(native, indent=2)}\n\n"
    prompt_payload += "=== RETRIEVED CLASSICAL GROUND TRUTH (RAG CONTEXT) ===\n"
    
    for item in retrieved_knowledge:
        prompt_payload += f"\nPlacement: {item['placement']}\n"
        prompt_payload += f"Retrieved Context:\n{item['retrieved_context']}\n"

    print("\n" + "="*60)
    print("FINAL LLM PROMPT (READY FOR INFERENCE):")
    print("="*60)
    print(prompt_payload)
    print("="*60)

    # 5. Execute LLM Call if API key present, else display payload
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if openai_api_key:
        try:
            from langchain_openai import ChatOpenAI
            llm = ChatOpenAI(model="gpt-4o", temperature=0.2)
            response = llm.invoke(prompt_payload)
            print("\n=== HELLENISTIC ASTROLOGY INTERPRETATION ===")
            print(response.content)
        except Exception as e:
            print(f"\nCould not call OpenAI API automatically: {e}")
    else:
        print("\nNOTE: Set your OPENAI_API_KEY environment variable to get automated LLM output.")
        print("The RAG retrieval payload above is fully formatted and ready for strict classical interpretation!")

def main():
    interpret_chart_with_rag()

if __name__ == "__main__":
    main()
