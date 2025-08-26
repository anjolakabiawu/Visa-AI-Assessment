import os
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser

class RAGSystem:
    def __init__(self, index_path):
        print("Initializing RAG S ystem by loading from disk...")
        if not os.path.exists(index_path):
            raise FileNotFoundError(f"FAISS index not found at {index_path}. Please run 'src/build_knowledge_base.py' first.")
        
        # Step 1: Load the pre-built vector store from disk
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.vectorstore = FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)
        self.retriever = self.vectorstore.as_retriever()
        print("  - Vector store loaded successfully.")
        
        # Step 2: Set up LLM and prompt template
        