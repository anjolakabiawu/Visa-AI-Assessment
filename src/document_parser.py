import docx
import fitz  # PyMuPDF
import re
import openai

# --- The text extraction functions remain the same ---
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
        return None
    
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
    Uses an LLM to read the beginning of a petition and extract the main
    section headers that introduce evidence for the EB-1A criteria.
    """
    print("  - Using LLM to identify document structure...")
    prompt = f"""
    The following is the beginning of an EB-1A petition document.
    Your task is to identify the primary section headers that introduce distinct arguments or criteria.
    
    These headers typically start with a numbering scheme like 'Section X', 'X.Y', or 'X.Y.Z' (e.g., '1.1', '1.2', '2.1.1').
    
    Scan the document from the beginning and list all such headers you find. Do not include items from a table of contents that are just lists; focus on the actual headers in the body of the text that are followed by paragraphs.

    List only the exact, full titles of these sections. Separate each title with a pipe character (|).
    Provide only the pipe-separated list and nothing else.

    DOCUMENT TEXT:
    ---
    {text_sample}
    ---
    """
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
        )
        headers_string = response.choices[0].message.content.strip()
        print(f"  - LLM identified headers: {headers_string}")
        return headers_string.split('|')
    except Exception as e:
        print(f"  - Error during LLM header extraction: {e}")
        return []

def _extract_section_numbers(headers):
    """Extracts patterns like '1.6' or '2.4.1' from a list of headers."""
    section_patterns = []
    for h in headers:
        # Find patterns like 1.6, 2.1, 2.4.1, etc.
        match = re.search(r'^\d+(\.\d+)*', h)
        if match:
            section_patterns.append(match.group(0))
    return section_patterns

def segment_petition(full_text):
    """
    Segments the petition by finding section numbers identified by an LLM.
    """
    if not full_text:
        return {}
        
    print("Segmenting document using intelligent two-pass method...")
    
    text_sample = full_text[:8000]
    llm_headers = _get_dynamic_headers_with_llm(text_sample)
    
    if not llm_headers:
        print("  - LLM could not identify headers. Analyzing as a whole document.")
        return {"Full Petition": full_text}

    # --- THIS IS THE FIX ---
    # Instead of matching text, we extract and match the section numbers.
    section_numbers = _extract_section_numbers(llm_headers)
    
    if not section_numbers:
        print("  - Could not extract section numbers from LLM headers. Analyzing as a whole.")
        return {"Full Petition": full_text}

    print(f"  - Extracted section numbers for splitting: {section_numbers}")

    # Create a regex that looks for the start of a line (^) followed by the section number.
    # This is extremely robust.
    escaped_patterns = [re.escape(sn) for sn in section_numbers]
    pattern_string = "|".join([f"^{p}" for p in escaped_patterns])
    
    # We also include "Exhibit" as a fallback pattern
    pattern_string += "|Exhibit \\d+"
    
    # Use MULTILINE flag to make '^' work on each line
    pattern = re.compile(f"({pattern_string})", re.MULTILINE)
    
    parts = pattern.split(full_text)
    
    segments = {}
    if len(parts) < 3:
        print("  - Regex split failed to find any matching section numbers. Analyzing as a whole document.")
        return {"Full Petition": full_text}

    initial_content = parts[0].strip()
    if initial_content:
        segments["Cover Letter / Introduction"] = initial_content

    headers_found = parts[1::2]
    contents_found = parts[2::2]

    for header_match, content in zip(headers_found, contents_found):
        full_content = (header_match + content).strip()
        first_line_break = full_content.find('\n')
        if first_line_break == -1:
            full_header = full_content[:100] # Limit header length
        else:
            full_header = full_content[:first_line_break].strip()

        if full_content and full_header:
            segments[full_header] = full_content
            print(f"  - Found segment: '{full_header}'")
            
    if not segments:
        print("  - No content found for any identified segments. Analyzing as a whole.")
        return {"Full Petition": full_text}
            
    return segments