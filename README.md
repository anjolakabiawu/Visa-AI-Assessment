# VisaCompanion RFE Risk Analyzer (RAG-Enhanced)

This project is an advanced prototype of an AI-powered tool designed to analyze draft EB-1A petitions for potential weaknesses that could trigger a Request for Evidence (RFE) from USCIS.

This enhanced version uses a **Retrieval-Augmented Generation (RAG)** pipeline. It grounds its analysis in a knowledge base built from thousands of real USCIS Administrative Appeals Office (AAO) decisions, providing truly data-driven and evidence-based feedback.

### Features

-   **Multi-Format Ingestion:** Reads petition drafts from `.docx`, `.pdf`, and `.txt` files.
-   **Data-Driven Knowledge Base:** Includes a script to scrape and process thousands of real AAO decisions into a sophisticated vector store.
-   **RAG-Powered Analysis:** Uses a two-step AI process. An initial analysis identifies weaknesses, and a RAG system then retrieves relevant context from real legal cases to generate highly specific, evidence-based suggestions for improvement.
-   **Actionable Reporting:** Generates a professional, human-readable `.docx` report that includes severity ratings, problematic excerpts, and concrete recommendations grounded in real-world case outcomes.
-   **Adjudicator Persona Simulation:** Includes narrative notes from the perspective of the reviewing officer.

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

### The Two-Step Workflow

This project has two main phases: a one-time data preprocessing step, and the analysis step.

**Step 1: Build the Knowledge Base (Run This Once)**

First, you must process the AAO decision documents into a local vector store.

**⚠️ Warning:** This process can take a long time and will use your OpenAI API credits, depending on the number of documents you process. It's recommended to start with a small number (e.g., 10-50 PDFs) by adjusting the `PDFS_TO_PROCESS` variable in `src/build_knowledge_base.py`.

In your terminal, from the project's root directory, run:
```bash
python src/build_knowledge_base.py
```

**Step 2: Run the RFE Analysis (Run Anytime)**
This will create a faiss_index folder in your project directory. You only need to run this script when you want to create or update your knowledge base.

From the project's root directory, run the analysis from your terminal by passing the path to the petition file as an argument.

Example 1: Running from the project's root folder
```bash
python src/main.py samples/sample_petition_1.docx
```
or
```bash
python src/main.py samples/sample_petition_2.pdf
```
or
```bash
python src/main.py samples/sample_petition_3.txt
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