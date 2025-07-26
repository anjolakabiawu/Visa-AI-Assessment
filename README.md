# VisaCompanion RFE Risk Analyzer

This project is a prototype of an AI-powered tool designed to analyze draft EB-1A petitions for potential weaknesses that could trigger a Request for Evidence (RFE) from USCIS. The tool ingests petition documents, segments them by criteria, and uses a Large Language Model (LLM) to generate a detailed risk analysis report in the style of a professional legal memo.

### Features

-   **Multi-Format Ingestion:** Reads petition drafts from both `.docx` and `.pdf` files.
-   **Intelligent Segmentation:** Automatically identifies and separates sections of the petition corresponding to specific EB-1A criteria.
-   **AI-Powered Analysis:** Leverages a powerful LLM with a specialized prompt to act as a USCIS adjudicator, identifying weaknesses in claims.
-   **Actionable Reporting:** Generates a professional, human-readable `.docx` report that includes severity ratings, problematic excerpts, and concrete suggestions for improvement.
-   **Adjudicator Persona Simulation:** Includes a "Creative Bonus" section with narrative notes from the perspective of the reviewing officer.

### Setup Instructions

**1. Clone the Repository**
```bash
git clone <your-repository-url>
cd VisaCompanion_RFE_Analyzer
```

**2. Create a Python Virtual Environment**
It is highly recommended to use a virtual environment to manage dependencies.
```bash
# For Mac/Linux
python3 -m venv venv
source venv/bin/activate

# For Windows
python -m venv venv
venv\Scripts\activate
```

**3. Install Dependencies**
Install all the required Python packages.
```bash
pip install -r requirements.txt
```
*(Note: You will need to create a `requirements.txt` file containing `openai`, `python-docx`, and `PyMuPDF`)*

**4. Set Environment Variable**
The application requires an OpenAI API key. Set it as an environment variable for security.
```bash
# For Mac/Linux
export OPENAI_API_KEY='your-secret-key-here'

# For Windows
set OPENAI_API_KEY='your-secret-key-here'
```

### Usage

Run the analysis from your terminal by passing the path to the petition file as an argument.

```bash
python main.py path/to/your/sample_petition.docx
```
or
```bash
python main.py path/to/your/sample_petition_2.pdf
```
or
```bash
python main.py path/to/your/sample_petition.txt
```

The script will process the file and generate a report named `RFE_Risk_Report.docx` in the root directory.

### Project Structure

```
VisaCompanion_RFE_Analyzer/
├── main.py                # Main script to orchestrate the analysis
├── document_parser.py     # Functions to read and segment documents
├── ai_analyzer.py         # Handles the LLM prompt and API communication
├── report_generator.py    # Builds the final DOCX report
├── requirements.txt       # List of Python dependencies
└── sample_petition.docx   # An example petition file for testing
```