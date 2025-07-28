import docx
import fitz
import re

def extract_text_from_docx(file_path):
    """Extracts text from a DOCX file."""
    try:
        doc = docx.Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs])
    except Exception as e:
        print(f"Error reading DOCX file: {e}")
        return None

def extract_text_from_pdf(file_path):
    """Extracts text from a PDF file"""
    try:
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    except Exception as e:
        print(f"Error reading PDF file: {e}")

def extract_text_from_txt(file_path):
    """Extracts text from a plaintext TXT file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading TXT file: {e}")
        return None

def segment_petition(full_text):
    """
    Segments the petition into a dictionary based on EB-1A criteria keywords.
    This uses regular expressions to find section headers.
    """
    print("Segmenting document...")
    segments = {}
    # Regex to find "Criterion X", "Criterion X:", "Evidence for X", etc.
    # It captures the criterion name and the text that follows it.
    pattern = re.compile(
        r"(Criterion \d{1,2}:?[\s\w,]+|Personal Statement|Background|Summary of Evidence)",
        re.IGNORECASE
    )
    
    parts = pattern.split(full_text)
    if len(parts) < 3:
        # If no sections are found, treat the whole document as one segment
        return {"Full Petition": full_text}

    # The split results in [text_before_first_match, match1, text1, match2, text2, ...]
    # We iterate through the matches and their corresponding texts.
    for i in range(1, len(parts), 2):
        header = parts[i].strip()
        content = parts[i+1].strip()
        if content: # Only add sections with content
            segments[header] = content
            print(f"  - Found segment: '{header}'")
            
    return segments