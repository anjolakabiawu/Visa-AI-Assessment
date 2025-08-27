import sys
import os
from document_parser import extract_text_from_docx, extract_text_from_pdf, extract_text_from_txt, segment_petition
from ai_analyzer import analyze_text_with_rag
from report_generator import create_rfe_risk_report
from rag_enhancer import RAGSystem

# The main function takes the file path directly 
def main(input_file_path):
    """
    Main function to orchestrate the RFE analysis process.
    """
    
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    faiss_index_path = os.path.join(project_root, 'faiss_index')
    output_dir = os.path.join(project_root, 'output')

    # --- Initialize the RAG system by loading the pre-built index ---
    try:
        rag_system = RAGSystem(faiss_index_path)
    except FileNotFoundError as e:
        print(f"\nFATAL ERROR: {e}")
        print("Please run 'python src/build_knowledge_base.py' to create the knowledge base first.")
        return
    
    print(f"Starting analysis for: {input_file_path}")

    # Ingest Document
    if input_file_path.lower().endswith('.docx'):
        full_text = extract_text_from_docx(input_file_path)
    elif input_file_path.lower().endswith('.pdf'):
        full_text = extract_text_from_pdf(input_file_path)
    elif input_file_path.lower().endswith('.txt'):
        full_text = extract_text_from_txt(input_file_path)
    else:
        print("Error: Unsupported file format. Please use .docx, .pdf, or .txt")
        return
    
    if not full_text:
        print("Error: Could not extract text from the document.")
        return
    
    # Segment Document
    segments = segment_petition(full_text)
    if not segments:
        print("Error: Could not segment the document. Analyzing as a whole.")
        segments = {"Full Petition": full_text}
    
    # Analyze Each Segment with the RAG Powered System
    all_analyses = {}
    for header, text_chunk in segments.items():
        print(f"\n--- Analyzing Segment: {header}  ---")
        if len(text_chunk) > 100:
            analysis = analyze_text_with_rag(text_chunk, rag_system)
            if analysis:
                all_analyses[header] = analysis
        else:
            print(" - Segment too short, skipping analysis.")
    
    # Generate Final Report
    if all_analyses:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        output_filename = os.path.join(output_dir, 'RFE_Risk_Report_Real.docx')
        create_rfe_risk_report(all_analyses, output_filename=output_filename)
    else:
        print("No analysis was generated. The report will not be created.")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python src/main.py <path/to/your/file>")
        print("Example (from root folder): python src/main.py samples/sample_petition.docx")
    else:
        input_path = sys.argv[1]
        main(input_path)