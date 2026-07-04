import chromadb
import ollama

CHROMA_DB_DIR = "data/chroma_db"

def run_rag_pipeline(user_question):
    # 1. Connect to our existing ChromaDB setup
    chroma_client = chromadb.PersistentClient(path=CHROMA_DB_DIR)
    collection = chroma_client.get_collection(name="microfinance_policies")
    
    # 2. Convert the user's question into the 768-number layout vector
    response = ollama.embeddings(
        model="nomic-embed-text",
        prompt=user_question
    )
    query_vector = response["embedding"]
    
    # 3. Retrieve the top 2 closest matching policy paragraphs
    results = collection.query(
        query_embeddings=[query_vector],
        n_results=2
    )
    
    # Combine the retrieved text chunks into a single reference block
    retrieved_context = "\n\n".join(results['documents'][0])
    
    # 4. Construct the prompt blueprint for the LLM
    system_prompt = f"""
    You are an expert compliance officer for a Microfinance Institution (MFI). 
    Answer the user's question accurately and professionally using the official policy context provided below.
    
    Guidelines:
    1. Base your answer strictly on the provided context. 
    2. If the document addresses the concept under a broader term (like 'household' instead of 'individual'), explain that distinction clearly to the user.
    3. Only say you cannot find the answer if the topic is completely unmentioned.
    
    Official Policy Context:
    {retrieved_context}
    """
    
    # 5. Send everything to our local conversational model
    chat_response = ollama.chat(
        model="llama3.2:1b",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_question}
        ]
    )
    
    # 6. Return the response string to be displayed in the UI
    return chat_response['message']['content']

# This block allows you to still test the backend from the terminal
if __name__ == "__main__":
    test_query = "What is the ceiling limit for an individual borrowing a small loan?"
    print(run_rag_pipeline(test_query))