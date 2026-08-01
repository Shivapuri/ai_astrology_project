"""
Jyotish RAG Builder
Ingests pristine digital Jyotish text files from /rag/jyotish_rag_data/
and builds an isolated ChromaDB vector database in /rag/chroma_jyotish_db/.
"""

import os
import glob
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "jyotish_rag_data")
CHROMA_DB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chroma_jyotish_db")


def load_text_documents():
    """Ingest clean text files from jyotish_rag_data directory."""
    documents = []
    print(f"Ingesting text files from {DATA_DIR}...")
    
    txt_files = glob.glob(os.path.join(DATA_DIR, "*.txt"))
    for file_path in txt_files:
        try:
            print(f"Loading document: {os.path.basename(file_path)}...")
            loader = TextLoader(file_path, encoding="utf-8")
            docs = loader.load()
            print(f"  -> Loaded document with {len(docs[0].page_content)} characters.")
            documents.extend(docs)
        except Exception as e:
            print(f"Error loading {file_path}: {e}")

    return documents


def build_jyotish_vector_store(documents):
    """Split text documents into chunks and embed into ChromaDB."""
    print("Splitting Jyotish documents into search-ready chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500,
        chunk_overlap=250,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Created {len(chunks)} total text chunks for Jyotish RAG.")

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
    print("Jyotish Vector Database successfully built and persisted!")
    return vector_store


def main():
    print("=== Phase 2: Building Jyotish RAG Vector Database ===")
    docs = load_text_documents()
    if not docs:
        print("No text documents found in jyotish_rag_data directory. Please run fetch_jyotish_data.py first.")
        return
    build_jyotish_vector_store(docs)
    print("=== Phase 2 Complete! Vector store saved in /rag/chroma_jyotish_db/ ===")


if __name__ == "__main__":
    main()
