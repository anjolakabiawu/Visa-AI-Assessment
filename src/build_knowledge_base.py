import os
import requests
import fitz  # PyMuPDF
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document

# --- SETTINGS ---
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
POLICY_MANUAL_PATH = os.path.join(project_root, 'eb1a_policy_manual.txt')
FAISS_INDEX_PATH = os.path.join(project_root, 'faiss_index')
# Number of PDFs to process (starting with a small number for testing)
#PDFS_TO_PROCESS = 20

def extract_text_from_url(url):
    """Downloads a PDF from a URL and extracts its text."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status() # Raise an error for bad responses
        
        with fitz.open(stream=response.content, filetype="pdf") as doc:
            text = ""
            for page in doc:
                text += page.get_text()
        return text
    except requests.exceptions.RequestException as e:
        print(f" - Error fetching URL {url}: {e}")
    except Exception as e:
        print(f" - Error processing PDF from {url}: {e}")
    return None

def main():
    """Main function to build and save the knowledge base."""
    print("=== Starting Knowledge Base Construction ===")
    
    # Step 1: Read URLs from Master_file.txt
    if not os.path.exists(POLICY_MANUAL_PATH):
        print(f"Error: {POLICY_MANUAL_PATH} not found.")
        return
    
    with open(POLICY_MANUAL_PATH, 'r') as f:
        all_links = [line.strip() for line in f if line.strip()]
    
    links_to_process = all_links[:PDFS_TO_PROCESS]
    print(f"Found {len(all_links)} total links. Processing the first {len(links_to_process)}.")
    
    # Step 2: Scrape text and create LangChain Documents
    langchain_docs = []
    for i, link in enumerate(links_to_process):
        print(f"Processing document {i+1}/{len(links_to_process)}: {link}")
        text = extract_text_from_url(link)
        if text:
            # Create a LangChain Document, storing the URL in metadata
            doc = Document(page_content=text, metadata={"source": link})
            langchain_docs.append(doc)
    
    if not langchain_docs:
        print("No documents were processed successfully. Exiting.")
        return
    
    print(f"\nSuccessfully processed {len(langchain_docs)} documents.")
    
    # Step 3: Split documents into chunks
    print("Splitting documents into chunks...")
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = text_splitter.split_documents(langchain_docs)
    print(f"Created {len(chunks)} text chunks.")
    
    # Step 4: Create embeddings and build FAISS vector store
    print("Creating embeddings and building the FAISS vector store...")
    print("(This may take some time and download a model on the first run)")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = FAISS.from_documents(chunks, embeddings)
    print("Vector store created successfully.")
    
    # Step 5: Save the vector store to disk
    if not os.path.exists(FAISS_INDEX_PATH):
        os.makedirs(FAISS_INDEX_PATH)
    vectorstore.save_local(FAISS_INDEX_PATH)
    print(f"✅ Knowledge base successfully built and saved to '{FAISS_INDEX_PATH}'")

if __name__ == "__main__":
    main()