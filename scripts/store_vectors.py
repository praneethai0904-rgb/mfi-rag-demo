import os
import json
import chromadb

CHUNKS_DIR = "data/chunks/"
CHROMA_DB_DIR = "data/chroma_db"

def initialize_vector_db(specific_filename=None):
    """
    Initializes ChromaDB and seeds chunks. 
    If specific_filename is provided, it ONLY processes that file.
    """
    print(f"📦 Initializing Persistent ChromaDB at: {CHROMA_DB_DIR}")
    client = chromadb.PersistentClient(path=CHROMA_DB_DIR)
    collection = client.get_or_create_collection(name="microfinance_policies")
    
    # Determine which files to process
    files_to_process = [specific_filename] if specific_filename else os.listdir(CHUNKS_DIR)

    for filename in files_to_process:
        if filename.endswith("_embedded.json"):
            file_path = os.path.join(CHUNKS_DIR, filename)
            print(f"\n📂 Injecting embedded chunks from: {filename}")
            
            with open(file_path, "r") as f:
                embedded_chunks = json.load(f)
                
            documents, embeddings, metadatas, ids = [], [], [], []
            
            for idx, chunk in enumerate(embedded_chunks):
                # Safely access metadata
                meta = chunk.get("metadata", {})
                
                documents.append(chunk["text"])
                embeddings.append(chunk["embedding"])
                metadatas.append({
                    "section": chunk.get("section", "N/A"),
                    "filename": meta.get("filename", "unknown"),
                    "page_number": str(meta.get("page_number", "1"))
                })
                
                unique_id = f"{meta.get('filename', 'doc')}_p{meta.get('page_number', '0')}_c{idx}"
                ids.append(unique_id)
                
            if ids:
                collection.upsert(ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas)
                print(f"✅ Successfully indexed {len(ids)} chunks.")

    print(f"\n🏁 Database update complete! Total Size: {collection.count()} chunks.")