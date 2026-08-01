import os
import shutil
import glob

RAG_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(RAG_DIR, "astrology_rag_data")
CHROMA_DB_DIR = os.path.join(RAG_DIR, "chroma_astrology_db")

def cleanup():
    print("--- Phase 1: Data Cleanup & Renaming Script ---")
    
    # 1. Delete old ancient text files
    ancient_files = ["tetrabiblos.txt", "hellenistic_core_rules.txt", "classical_interpretations.csv"]
    for filename in ancient_files:
        filepath = os.path.join(DATA_DIR, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            print(f"Deleted ancient file: {filename}")
        else:
            print(f"File not found (already deleted): {filename}")

    # 2. Find, deduplicate, and rename modern PDF books
    pdf_files = glob.glob(os.path.join(DATA_DIR, "*.pdf"))
    
    # Separate any already standardized files from messily named files
    standard_names = ["modern_astrology_book_1.pdf", "modern_astrology_book_2.pdf", "modern_astrology_book_3.pdf"]
    
    # Track unique files by size to remove duplicates
    seen_sizes = {}
    unique_pdfs = []
    
    for pdf_path in sorted(pdf_files):
        size = os.path.getsize(pdf_path)
        base_name = os.path.basename(pdf_path)
        if size in seen_sizes:
            print(f"Removing duplicate PDF: {base_name}")
            os.remove(pdf_path)
        else:
            seen_sizes[size] = pdf_path
            unique_pdfs.append(pdf_path)

    # Rename up to 3 PDFs to modern_astrology_book_X.pdf
    for idx, pdf_path in enumerate(unique_pdfs[:3], start=1):
        new_name = f"modern_astrology_book_{idx}.pdf"
        target_path = os.path.join(DATA_DIR, new_name)
        if pdf_path != target_path:
            # If target already exists from earlier run, overwrite carefully
            if os.path.exists(target_path):
                os.remove(target_path)
            os.rename(pdf_path, target_path)
            print(f"Renamed '{os.path.basename(pdf_path)}' -> '{new_name}'")
        else:
            print(f"File already standardized: '{new_name}'")

    # Clean up any leftover PDFs beyond the top 3
    for pdf_path in unique_pdfs[3:]:
        print(f"Removing extra PDF: {os.path.basename(pdf_path)}")
        os.remove(pdf_path)

    # 3. Delete old ChromaDB directory cache
    if os.path.exists(CHROMA_DB_DIR):
        shutil.rmtree(CHROMA_DB_DIR)
        print(f"Deleted old vector database directory at {CHROMA_DB_DIR}")
    else:
        print("No existing vector database found to delete.")

    print("--- Phase 1 Cleanup Complete! ---")

if __name__ == "__main__":
    cleanup()
