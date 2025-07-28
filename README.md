# VisaCompanion RFE Risk Analyzer

This project is a prototype of an AI-powered tool designed to analyze draft EB-1A petitions for potential weaknesses that could trigger a Request for Evidence (RFE) from USCIS. The tool ingests petition documents, segments them by criteria, and uses a Large Language Model (LLM) to generate a detailed risk analysis report in the style of a professional legal memo.

### Features

-   **Multi-Format Ingestion:** Reads petition drafts from `.docx`, `.pdf`, and `.txt` files.
-   **Intelligent Segmentation:** Automatically identifies and separates sections of the petition corresponding to specific EB-1A criteria.
-   **AI-Powered Analysis:** Leverages a powerful LLM with a specialized prompt to act as a USCIS adjudicator, identifying weaknesses in claims.
-   **Actionable Reporting:** Generates a professional, human-readable `.docx` report that includes severity ratings, problematic excerpts, and concrete suggestions for improvement.
-   **Adjudicator Persona Simulation:** Includes a "Creative Bonus" section with narrative notes from the perspective of the reviewing officer.

### Setup Instructions

**1. Clone the Repository**
```bash
git clone <your-repository-url>
cd VisaCompanion_RFE_Analyzer

**2. Create a Python Virtual Environment**
It is highly recommended to use a virtual environment to manage dependencies.
```bash
# For Mac/Linux
python3 -m venv venv
source venv/bin/activate

# For Windows
python -m venv venv
source venv\Scripts\activate
```

**3. Install Dependencies**
Install all the required Python packages.
```bash
pip install -r requirements.txt
```

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

Example 1: Running from the project's root folder
```bash
python src/main.py samples/sample_petition.docx
```
or
```bash
python src/main.py samples/sample_petition_2.pdf
```
or
```bash
python src/main.py samples/sample_petition.txt
```
Example 2: Running from inside the src/ folder
```bash
python main.py path/to/your/samples/sample_petition.docx
```
or
```bash
python main.py path/to/your/samples/sample_petition_2.pdf
```
or
```bash
python main.py path/to/your/samples/sample_petition.txt
```

The script will process the file and generate a report named RFE_Risk_Report.docx in the output/ directory.

### Project Structure

```
VisaCompanion_RFE_Analyzer/
├── .gitignore
├── README.md
├── requirements.txt
├── Technical_Report.pdf
│
├── src/
│   ├── main.py
│   ├── document_parser.py
│   ├── ai_analyzer.py
│   └── report_generator.py
│
├── samples/
│   ├── sample_petition.docx
│   └── sample_petition_2.pdf
│
└── output/
    └── RFE_Risk_Report.docx
```