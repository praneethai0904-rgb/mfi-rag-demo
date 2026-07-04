import streamlit as st
import sys
import os
import shutil
import chromadb
from scripts.rag_backend import run_rag_pipeline
from scripts.chunk_policies import process_single_file
from scripts.pdf_to_json import convert_pdf_to_json
from scripts.store_vectors import initialize_vector_db

sys.path.append(os.path.join(os.getcwd(), 'scripts'))

st.set_page_config(page_title="MFI Policy Assistant", layout="wide")

# --- SIDEBAR: PIPELINE MONITORING ---
with st.sidebar:
    st.header("Pipeline Status")
    
    # Placeholder for status updates
    status_container = st.empty()
    
    st.divider()
    uploaded_file = st.file_uploader("Upload MFI Policy PDF", type=["pdf"])
    
    if uploaded_file and st.button("Process & Vectorize Document"):
        with status_container.status("Starting Ingestion...", expanded=True) as status:
            try:
                save_path = os.path.join("data", "raw", uploaded_file.name)
                os.makedirs("data/raw", exist_ok=True)
                with open(save_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                status.write("🧹 Cleaning old indexes...")
                if os.path.exists("data/chroma_db"):
                    shutil.rmtree("data/chroma_db")
                
                status.write("📄 1. Document Parsing...")
                json_name = uploaded_file.name.replace(".pdf", ".json")
                embedded_name = json_name.replace(".json", "_embedded.json")
                json_path = os.path.join("data/processed/", json_name)
                convert_pdf_to_json(save_path, json_path)
                
                status.write("✂️ 2. Window Chunking...")
                process_single_file(json_name)
                
                status.write("🔢 3. Vectorization (Embedding)...")
                status.write("🗄️ 4. Bulk Document Seeding...")
                initialize_vector_db(specific_filename=embedded_name)
                
                status.update(label="✅ Ingestion Complete!", state="complete", expanded=False)
            except Exception as e:
                status.update(label="❌ Pipeline Failed", state="error")
                st.error(str(e))

# --- MAIN AREA: CHAT INTERFACE ---
st.title("MFI Client Demo: Policy RAG Engine")
st.subheader("💬 Policy Assistant Chat")

# Retrieval & Generation visualization
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if query := st.chat_input("Ask a question about the loan policy..."):
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        with st.spinner("Retrieving facts..."):
            # 5. Retrieval & 6. Generation
            response = run_rag_pipeline(query)
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})