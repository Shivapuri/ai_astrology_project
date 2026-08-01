import os
import glob
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

DATA_DIR = os.path.join(os.path.dirname(__file__), "astrology_rag_data")
CHROMA_DB_DIR = os.path.join(os.path.dirname(__file__), "chroma_astrology_db")

def load_pdf_documents():
    """Ingest all modern astrology PDF books from data directory."""
    documents = []
    print(f"Ingesting PDF files from {DATA_DIR}...")
    
    pdf_files = glob.glob(os.path.join(DATA_DIR, "*.pdf"))
    for file_path in pdf_files:
        try:
            print(f"Loading PDF: {os.path.basename(file_path)}...")
            loader = PyPDFLoader(file_path)
            docs = loader.load()
            print(f"  -> Loaded {len(docs)} pages from {os.path.basename(file_path)}")
            documents.extend(docs)
        except Exception as e:
            print(f"Error loading {file_path}: {e}")

    return documents

def build_vector_store(documents):
    """Split PDF pages into chunks and embed into local ChromaDB vector database."""
    print("Splitting documents into searchable text chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500,
        chunk_overlap=250,
        separators=["\n\n", "\n", ".", " ", ""]
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
    print("--- Phase 2: Building Modern Astrology RAG Database ---")
    docs = load_pdf_documents()
    if not docs:
        print("No PDF documents found in astrology_rag_data directory. Run Phase 1 first.")
        return
    build_vector_store(docs)
    print("--- Phase 2 Complete! Vector store saved in /chroma_astrology_db/ ---")

if __name__ == "__main__":
    main()
