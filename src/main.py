import sys
import os
from document_parser import extract_text_from_docx, extract_text_from_pdf, extract_text_from_txt, segment_petition
from ai_analyzer import analyze_text_with_llm
from report_generator import create_rfe_risk_report

# The main function takes the file path directly 
def main(input_file_path):
    """
    Main function to orchestrate the RFE analysis process.
    """
    
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
    
    # Analyze Each Segment with AI
    all_analyses = {}
    for header, text_chunk in segments.items():
        print(f"\n--- Analyzing Segment: {header}  ---")
        if len(text_chunk) > 100:
            analysis = analyze_text_with_llm(text_chunk)
            if analysis:
                all_analyses[header] = analysis
        else:
            print(" - Segment too short, skipping analysis.")
    
    # Generate Final Report
    if all_analyses:
        # We only use this logic to reliably find the output folder
        project_root = os.path.dirname(os.path.abspath(__file__)) # Go to src/
        project_root = os.path.dirname(project_root) # Go to project root
        output_filename = os.path.join(project_root, 'output', 'RFE_Risk_Report.docx')
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