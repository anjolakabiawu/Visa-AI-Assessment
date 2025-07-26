import sys
from document_parser import extract_text_from_docx, extract_text_from_pdf, extract_text_from_txt, segment_petition
from ai_analyzer import analyze_text_with_llm
from report_generator import create_rfe_risk_report

def main(file_path):
    """
    Main function to orchestrate the RFE analysis process.
    """
    print(f"Starting analysis for: {file_path}")

    # Ingest Document
    if file_path.lower().endswith('.docx'):
        full_text = extract_text_from_docx(file_path)
    elif file_path.lower().endswith('.pdf'):
        full_text = extract_text_from_pdf(file_path)
    elif file_path.lower().endswith('.txt'):
        full_text = extract_text_from_txt(file_path)
    else:
        print("Error: Unsupported file format. Please use .docx or .pdf")
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
        create_rfe_risk_report(all_analyses)
    else:
        print("No analysis was generated. The report will not be created.")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: python main.py <path_to_your_petition_file>')
    else:
        file_path = sys.argv[1]
        main(file_path)