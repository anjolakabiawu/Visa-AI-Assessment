import os
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# --- SETTINGS ---
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
POLICY_MANUAL_PATH = os.path.join(project_root, 'eb1a_policy_manual.txt')
FAISS_INDEX_PATH = os.path.join(project_root, 'faiss_index')
# Number of PDFs to process (starting with a small number for testing)
#PDFS_TO_PROCESS = 20

def main():
    """Main function to build and save the knowledge base from the local policy manual file."""
    print("=== Starting Knowledge Base Construction from USCIS Policy Manual ===")
    
    # Step 1: Load the source document
    if not os.path.exists(POLICY_MANUAL_PATH):
        print(f"Error: Policy manual file not found at '{POLICY_MANUAL_PATH}'")
        print("Please create the file and paste the USCIS EB-1A policy manual text into it.")
        return
    
    loader = TextLoader(POLICY_MANUAL_PATH, encoding="utf-8")
    documents = loader.load()
    print(f"Succesfully loaded the policy manual.")
    
    # Step 2: Split documents into chunks
    print("Splitting documents into chunks...")
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = text_splitter.split_documents(documents)
    print(f"Created {len(chunks)} text chunks.")
    
    # Step 3: Create embeddings and build FAISS vector store
    print("Creating embeddings and building the FAISS vector store...")
    print("(This may take some time and download a model on the first run)")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = FAISS.from_documents(chunks, embeddings)
    print("Vector store created successfully.")
    
    # Step 4: Save the vector store to disk
    if os.path.exists(FAISS_INDEX_PATH):
        print(f"Note: Overwriting exisiting index at '{FAISS_INDEX_PATH}'")
    vectorstore.save_local(FAISS_INDEX_PATH)
    print(f"✅ Knowledge base successfully built and saved to '{FAISS_INDEX_PATH}'")

if __name__ == "__main__":
    main()