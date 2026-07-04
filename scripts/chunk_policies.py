import os
import json
import requests

CHUNKS_DIR = "data/chunks/"
OLLAMA_URL = "http://localhost:11434/api/embeddings"

# Ensure the output directory exists
os.makedirs(CHUNKS_DIR, exist_ok=True)

def chunk_document(elements):
    """Chunks the list of elements into smaller, semantic units."""
    chunks = []
    current_chunk_elements = []
    current_text_length = 0
    current_section_title = "Introduction"
    MAX_CHUNK_CHARS = 600 

    for el in elements:
        element_type = el.get("type", "NarrativeText")
        element_text = el.get("text", "").strip()
        if not element_text: continue
            
        if element_type == "Title":
            current_section_title = element_text
            
        current_chunk_elements.append(el)
        current_text_length += len(element_text) + 1 
        
        if current_text_length >= MAX_CHUNK_CHARS:
            combined_text = " ".join([item.get("text", "") for item in current_chunk_elements])
            primary_metadata = current_chunk_elements[0].get("metadata", {})
            chunks.append({
                "section": current_section_title,
                "text": combined_text,
                "metadata": {"filename": primary_metadata.get("filename"), "page_number": primary_metadata.get("page_number")}
            })
            current_chunk_elements = []
            current_text_length = 0

    if current_chunk_elements:
        combined_text = " ".join([item.get("text", "") for item in current_chunk_elements])
        chunks.append({"section": current_section_title, "text": combined_text, "metadata": {}})
    return chunks

def process_single_file(json_filename):
    """Processes only the file provided by the UI."""
    file_path = os.path.join("data/processed/", json_filename)
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Processed file not found at {file_path}. Ensure PDF-to-JSON conversion ran first.")

    with open(file_path, "r") as f:
        elements = json.load(f)
    
    document_chunks = chunk_document(elements)
    embedded_chunks = []
    
    print(f"🧠 Generating embeddings for {len(document_chunks)} chunks...")
    for chunk in document_chunks:
        payload = {"model": "nomic-embed-text", "prompt": chunk["text"]}
        response = requests.post(OLLAMA_URL, json=payload)
        if response.status_code == 200:
            chunk["embedding"] = response.json().get("embedding")
            embedded_chunks.append(chunk)
            
    output_path = os.path.join(CHUNKS_DIR, json_filename.replace(".json", "_embedded.json"))
    with open(output_path, "w") as out_f:
        json.dump(embedded_chunks, out_f, indent=2)
    
    print(f"✅ Successfully processed {json_filename}")