import chromadb
import ollama

CHROMA_DB_DIR = "data/chroma_db"

def search_database(user_query):
    # 1. Connect to the existing persistent database folder
    chroma_client = chromadb.PersistentClient(path=CHROMA_DB_DIR)
    
    # 2. Grab the collection as-is without overriding any internal settings
    collection = chroma_client.get_collection(name="microfinance_policies")
    
    print(f"🔍 Asking Ollama to convert query: \"{user_query}\" into 768 coordinates...\n")
    
    # 3. Use Ollama directly to get the 768-number vector for our question
    response = ollama.embeddings(
        model="nomic-embed-text",
        prompt=user_query
    )
    query_vector = response["embedding"]
    
    # 4. Pass the RAW vector list directly into ChromaDB using query_embeddings
    results = collection.query(
        query_embeddings=[query_vector],
        n_results=2
    )
    
    # 5. Print out the closest semantic matches discovered on the map
    for idx, (doc, meta) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
        print(f"--- MATCH #{idx + 1} ---")
        print(f"📄 Source File: {meta['filename']} (Page {meta['page_number']})")
        print(f"🔖 Section: {meta['section']}")
        print(f"💬 Found Content:\n{doc}\n")

if __name__ == "__main__":
    test_question = "What is the ceiling limit for an individual borrowing a small loan?"
    search_database(test_question)