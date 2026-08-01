import os
import glob
from langchain_community.document_loaders import TextLoader, CSVLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

DATA_DIR = os.path.join(os.path.dirname(__file__), "astrology_rag_data")
CHROMA_DB_DIR = os.path.join(os.path.dirname(__file__), "chroma_astrology_db")

def load_documents():
    """Ingest all text files and CSVs from data directory."""
    documents = []
    print(f"Ingesting files from {DATA_DIR}...")
    
    # 1. Load Text files
    txt_files = glob.glob(os.path.join(DATA_DIR, "*.txt"))
    for file_path in txt_files:
        try:
            loader = TextLoader(file_path, encoding="utf-8")
            docs = loader.load()
            print(f"Loaded {len(docs)} text document(s) from {os.path.basename(file_path)}")
            documents.extend(docs)
        except Exception as e:
            print(f"Error loading {file_path}: {e}")

    # 2. Load CSV files
    csv_files = glob.glob(os.path.join(DATA_DIR, "*.csv"))
    for file_path in csv_files:
        try:
            loader = CSVLoader(file_path, encoding="utf-8")
            docs = loader.load()
            print(f"Loaded {len(docs)} CSV record(s) from {os.path.basename(file_path)}")
            documents.extend(docs)
        except Exception as e:
            print(f"Error loading {file_path}: {e}")

    return documents

def build_vector_store(documents):
    """Split text into chunks and embed into local ChromaDB vector database."""
    print("Splitting documents into searchable text chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500,     # INCREASED from 500 to 1500 characters
        chunk_overlap=250,   # INCREASED to maintain context between chunks
        separators=["\n\n", "\n", ".", " ", ""] # Forces it to split at paragraphs first
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Created {len(chunks)} total text chunks.")

    print("Initializing HuggingFace embedding model (all-MiniLM-L6-v2)...")
    embedding_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    print(f"Embedding chunks into Chroma Vector DB at {CHROMA_DB_DIR}...")
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_model,
        persist_directory=CHROMA_DB_DIR
    )
    print("Vector database successfully built and persisted!")
    return vector_store

def main():
    print("--- Phase 2: Building Local Hellenistic RAG Database ---")
    docs = load_documents()
    if not docs:
        print("No documents found in astrology_rag_data directory. Run Phase 1 first.")
        return
    build_vector_store(docs)
    print("--- Phase 2 Complete! Vector store saved in /chroma_astrology_db/ ---")

if __name__ == "__main__":
    main()
