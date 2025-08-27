import docx
import fitz
import re
import openai

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

def _get_dynamic_headers_with_llm(text_sample):
    """
    Uses an LLM to read the beginning of a petition and extract the main section headers
    that introduce the evidence for the EB-1A criteria.
    """
    print("  - Using LLM to identify document structure...")
    prompt = f"""
    The following is the beginning of an EB-1A petition.
    Read it carefully and identify the exact titles of the main sections that present the evidence for the claimed criteria.
    Examples might look like "2.1 Evidence of original scientific contributions..." or "1.6 Dr. Doe has widely published..."
    
    List only the exact, full titles of these sections. Separate each title with a pipe character (|).
    Provide only the pipe-separated list and nothing else.
    
    DOCUMENT TEXT:
    ===
    {text_sample}
    ===
    """
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": prompt}],
            temperature=0.0,
        )
        headers_string = response.choices[0].message.content.strip()
        print(f"  - LLM identified headers: {headers_string}")
        return headers_string.split('|')
    except Exception as e:
        print(f"  - Error during LLM header extraction: {e}")
        return []

def segment_petition(full_text):
    """
    Segments the petition using intelligent two-pass method...
    """
    if not full_text:
        return {}
    
    print("Segmenting document...")
    
    # Step 1: Get the dynamic headers from the first ~8000 characters
    text_sample = full_text[:8000]
    headers = _get_dynamic_headers_with_llm(text_sample)
    
    # Clean up any empty strings that might result from splitting
    cleaned_headers = [h.strip() for h in headers if h.strip()]
    
    if not cleaned_headers:
        print("  - LLM could not identify headers. Analyzing as a whole document.")
        return {"Full Petition": full_text}
    
    # Step 2: Dynamically build a regex and split the document
    short_headers = [" ".join(h.split()[:5]) for h in cleaned_headers]
    
    escaped_headers = [re.escape(h) for h in cleaned_headers]
    # Included Exhibits as a fallback
    base_patterns = ["Exhibits? \\d+"]
    
    pattern_string = "|".join(escaped_headers + base_patterns)
    pattern = re.compile(f"{pattern_string}", re.IGNORECASE)
    
    parts = pattern.split(full_text)
    
    segments = {}
    if len(parts) < 3:
        print("  - Regex split failed to find any matching headers. Analyzing as a whole document.")
        return {"Full Petition": full_text}

    headers_found = parts[1::2]
    contents_found = parts[2:2]
    
    for header, content in zip(headers_found, contents_found):
        header = header.strip()
        content = content.strip()
        if content: # Only add sections with content
            segments[header] = content
            print(f"  - Found segment: '{header}'")
    
    if not segments:
        print("  - No content found for any identified segments. Analyzing as a whole document.")
        return {"Full Petition": full_text}
            
    return segments