import os
import shutil
import glob

RAG_DIR = os.path.dirname(os.path.abspath(__file__))
MODERN_DATA_DIR = os.path.join(RAG_DIR, "modern_rag_data")
STRUCTURAL_DATA_DIR = os.path.join(RAG_DIR, "structural_rag_data")

CHROMA_MODERN_DB = os.path.join(RAG_DIR, "chroma_modern_db")
CHROMA_STRUCTURAL_DB = os.path.join(RAG_DIR, "chroma_structural_db")


def cleanup():
    print("--- Phase 1: Dual RAG Data Cleanup Script ---")
    
    # 1. Clean up duplicate PDFs in modern_rag_data
    if os.path.exists(MODERN_DATA_DIR):
        pdf_files = glob.glob(os.path.join(MODERN_DATA_DIR, "*.pdf"))
        seen_sizes = {}
        for pdf_path in sorted(pdf_files):
            size = os.path.getsize(pdf_path)
            base_name = os.path.basename(pdf_path)
            if size in seen_sizes:
                print(f"Removing duplicate PDF in modern_rag_data: {base_name}")
                os.remove(pdf_path)
            else:
                seen_sizes[size] = pdf_path

    # 2. Clean up duplicate PDFs in structural_rag_data
    if os.path.exists(STRUCTURAL_DATA_DIR):
        pdf_files = glob.glob(os.path.join(STRUCTURAL_DATA_DIR, "*.pdf"))
        seen_sizes = {}
        for pdf_path in sorted(pdf_files):
            size = os.path.getsize(pdf_path)
            base_name = os.path.basename(pdf_path)
            if size in seen_sizes:
                print(f"Removing duplicate PDF in structural_rag_data: {base_name}")
                os.remove(pdf_path)
            else:
                seen_sizes[size] = pdf_path

    # 3. Delete old ChromaDB directory caches if requested
    for db_dir, name in [(CHROMA_MODERN_DB, "Chroma Modern DB"), (CHROMA_STRUCTURAL_DB, "Chroma Structural DB")]:
        if os.path.exists(db_dir):
            shutil.rmtree(db_dir)
            print(f"Deleted vector database directory: {name} at {db_dir}")
        else:
            print(f"No existing {name} directory found to delete.")

    print("--- Phase 1 Cleanup Complete! ---")


if __name__ == "__main__":
    cleanup()

