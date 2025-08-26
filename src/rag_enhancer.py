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
        self.llm = ChatOpenAI(model_name="gpt-4o")
        self.prompt = self._create_rag_prompt()
        
    def _create_rag_prompt(self):
        template = """
        You are an expert legal assistant. Your task is to provide an enhanced, evidence-based suggestion to fix a weakness in an immigration petition.
        Use the following retrieved context from real USCIS decision documents to provide a highly specific and actionable recommendation.
        Your suggestion should directly reference the standards or failure patterns mentioned in the context.

        CONTEXT FROM REAL CASES:
        {context}

        IDENTIFIED WEAKNESS IN CURRENT PETITION:
        {question}

        ENHANCED, EVIDENCE-BASED SUGGESTION:
        """
        return PromptTemplate(template=template, input_variables=["context", "question"])
    
    def get_enhanced_suggestion(self, weakness_description):
        """
        Takes a weakness description, retrieves relevant context, and generates an enhanced suggestion.
        """
        print(f"  > RAG: Retrieving context for weakness: '{weakness_description}'")
        
        rag_chain = (
            {"context": self.retriever, "question": RunnablePassthrough()}
            | self.prompt
            | self.llm
            | StrOutputParser()
        )
        
        enhanced_suggestion = rag_chain.invoke(weakness_description)
        print("  < RAG: Enhanced suggestion received.")
        return enhanced_suggestion