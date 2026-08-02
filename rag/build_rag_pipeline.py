import os
import glob
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

RAG_DIR = os.path.dirname(os.path.abspath(__file__))
MODERN_DATA_DIR = os.path.join(RAG_DIR, "modern_rag_data")
STRUCTURAL_DATA_DIR = os.path.join(RAG_DIR, "structural_rag_data")

CHROMA_MODERN_DB_DIR = os.path.join(RAG_DIR, "chroma_modern_db")
CHROMA_STRUCTURAL_DB_DIR = os.path.join(RAG_DIR, "chroma_structural_db")


def load_pdf_documents_from_dir(data_dir: str):
    """Ingest all PDF books from a specific data directory."""
    documents = []
    print(f"Ingesting PDF files from {data_dir}...")
    
    pdf_files = glob.glob(os.path.join(data_dir, "*.pdf"))
    for file_path in pdf_files:
        try:
            print(f"  -> Loading PDF: {os.path.basename(file_path)}...")
            loader = PyPDFLoader(file_path)
            docs = loader.load()
            print(f"     Loaded {len(docs)} pages from {os.path.basename(file_path)}")
            documents.extend(docs)
        except Exception as e:
            print(f"Error loading {file_path}: {e}")

    return documents


def build_vector_store_for_domain(documents, target_db_dir: str, domain_name: str):
    """Split PDF pages into chunks and embed into specified local ChromaDB vector database."""
    print(f"\n--- Building {domain_name} Vector DB ---")
    if not documents:
        print(f"⚠️ No documents provided for {domain_name}. Skipping build.")
        return None

    print(f"Splitting {len(documents)} document pages into searchable text chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500,
        chunk_overlap=250,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Created {len(chunks)} total text chunks for {domain_name}.")

    print("Initializing HuggingFace embedding model (all-MiniLM-L6-v2)...")
    embedding_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    print(f"Embedding chunks into Chroma Vector DB at {target_db_dir}...")
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_model,
        persist_directory=target_db_dir
    )
    print(f"✅ {domain_name} Vector database successfully built and persisted at {target_db_dir}!")
    return vector_store


def main():
    print("======================================================================")
    print(" Building Dual-Camp Domain-Isolated Vector Databases")
    print("======================================================================")
    
    # 1. Structural Camp (Demetra George)
    struct_docs = load_pdf_documents_from_dir(STRUCTURAL_DATA_DIR)
    build_vector_store_for_domain(struct_docs, CHROMA_STRUCTURAL_DB_DIR, "Structural Camp (Demetra George)")
    
    # 2. Modern Psychological Camp (Arroyo, Marks, Hand)
    modern_docs = load_pdf_documents_from_dir(MODERN_DATA_DIR)
    build_vector_store_for_domain(modern_docs, CHROMA_MODERN_DB_DIR, "Modern Psychological Camp (Arroyo, Marks, Hand)")
    
    print("\n======================================================================")
    print("🎉 Dual RAG Database Build Complete!")
    print(f"   Structural DB: {CHROMA_STRUCTURAL_DB_DIR}")
    print(f"   Modern DB:     {CHROMA_MODERN_DB_DIR}")
    print("======================================================================")


if __name__ == "__main__":
    main()

