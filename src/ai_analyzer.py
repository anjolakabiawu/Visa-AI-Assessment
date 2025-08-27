import openai
import os
from dotenv import load_dotenv
from rag_enhancer import RAGSystem

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def get_eb1a_analysis_prompt():
    """
    This function contains the master prompt for the LLM.
    It defines the role, context, instructions, and output format.
    """
    
    return """
    **Role**: You are a meticulous and experienced USCIS Adjudicator reviewing an EB-1A, Alien of Extraordinary Ability, petition. You are fair but skeptical, and your goal is to identify any statement or claim that is not supported by strong, quantifiable evidence, as this could trigger a Request for Evidence (RFE).

    **Context**: Your analysis must be based on the official standards for the EB-1A category. The petitioner must prove they meet the requirements through sustained national or international acclaim.

     ---
    **Official EB-1A Standards and Criteria (Your Guide for Evaluation):**

    You must be able to demonstrate extraordinary ability in the sciences, arts, education, business, or athletics through sustained national or international acclaim.

    To demonstrate this, you must meet at least 3 of the 10 criteria below, or provide evidence of a one-time achievement (i.e., Pulitzer, Oscar, Olympic Medal).

    1.  Evidence of receipt of lesser nationally or internationally recognized prizes or awards for excellence
    2.  Evidence of your membership in associations in the field which demand outstanding achievement of their members
    3.  Evidence of published material about you in professional or major trade publications or other major media
    4.  Evidence that you have been asked to judge the work of others, either individually or on a panel
    5.  Evidence of your original scientific, scholarly, artistic, athletic, or business-related contributions of major significance to the field
    6.  Evidence of your authorship of scholarly articles in professional or major trade publications or other major media
    7.  Evidence that your work has been displayed at artistic exhibitions or showcases
    8.  Evidence of your performance of a leading or critical role in distinguished organizations
    9.  Evidence that you command a high salary or other significantly high remuneration in relation to others in the field
    10. Evidence of your commercial successes in the performing arts
    ---

    **Instructions**:
    1.  Read the following text excerpt from the petition carefully.
    2.  First, identify which single EB-1A criterion the text is attempting to satisfy.
    3.  Analyze the text for specific weaknesses. Look for:
        - Vague or generalized claims (e.g., "significant contribution", "important work").
        - Lack of quantifiable data (e.g., numbers, percentages, rankings).
        - Insufficient evidence of impact beyond the applicant's immediate institution.
        - Use of weak, self-serving language or template-like phrases.
        - Claims that don't match the standard of the criterion (e.g., a local award for the 'Awards' criterion).
    4.  If no significant weaknesses are found, state that the section is strong.
    5.  For each weakness found, generate a detailed risk entry.

    **Output Format**:
    Provide your entire response in a single, clean Markdown block. Do not include any text before or after the markdown block.

    ```markdown
    **Criterion Identification**: Criterion [Number]: [Name of Criterion]

    **Overall Assessment**: [A brief, one-sentence summary of the section's strength or weakness.]

    | Severity | Weakness Description | Problematic Excerpt | Suggested Improvement |
    | :--- | :--- | :--- | :--- |
    | **High** | The claim of 'major significance' is conclusory and lacks independent, quantifiable evidence of field-wide adoption or impact. | "The applicant's development of the algorithm was a major contribution to the field." | "Strengthen this claim by providing specific evidence. For instance: 'This algorithm was subsequently licensed by 3 competing firms (see Exhibit D) and cited as foundational in 50+ academic papers, demonstrating its field-wide impact.'" |
    | **Medium** | The letter of support is from a direct supervisor, which may be perceived as biased by USCIS. | "As his manager, I can attest that his work was critical to our team." | "Supplement this letter with 2-3 letters from independent experts in the field who have not directly worked with you but are familiar with your contributions and can attest to their significance from an objective viewpoint." |
    | **Low** | The language used is slightly generic and could be more impactful. | "The applicant did an excellent job on this project." | "Replace with more active and specific language. For example: 'The applicant single-handedly led the project, reducing production costs by 15% in the first quarter.'" |
    
    **Adjudicator's Persona Notes**: [Adopt the persona of a skeptical USCIS adjudicator. Write 2-3 sentences of your internal thoughts. e.g., 'This looks like standard work for a senior professional, not extraordinary ability. The letters all sound the same. I'm leaning towards an RFE on the 'Original Contributions' claim unless they provide more concrete proof of impact.']
    ```

    **Analyze the following text**:
    """

def analyze_text_with_llm(text_segment):
    """
    Sends a text segment to the OpenAI API for analysis.
    """
    if not OPENAI_API_KEY:
        return "Error: OPENAI_API_KEY environment variable not set."
    
    print(" > Sending segment to AI for analysis...")
    prompt = get_eb1a_analysis_prompt() + text_segment

    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=1000
        )
        analysis = response.choices[0].message.content
        print(" < Analysis received.")
        return analysis
    except Exception as e:
        print(f"An error occurred with the OpenAI API: {e}")
        return f"Error: Could not get analysis. Details: {e}"
    
def  analyze_text_with_rag(text_segment, rag_system):
    """
    Analyzes a text segment by first getting a baseline analysis,
    then using RAG to enhance the suggestions in the table.
    """
    print("=== Running Initial Analysis ===")
    initial_analysis_md = analyze_text_with_llm(text_segment)
    
    if not initial_analysis_md or '|' not in initial_analysis_md:
        return initial_analysis_md
    
    print("\n=== Enhancing Suggestions with RAG ===")
    
    lines = initial_analysis_md.strip().split('\n')
    new_lines = []
    
    for line in lines:
        # Check for a valid markdown table row
        if line.startswith('|') and '===' not in line and 'Severity' not in line:
            parts = [p.strip() for p in line.strip('|').split('|')]
            if len(parts) == 4:
                severity, weakness, exercpt, old_suggestion = parts
                
                enhanced_suggestion = rag_system.get_enhanced_suggestion(weakness)
                clean_suggestion = enhanced_suggestion.replace('\n', '').replace('|', ' ')
                
                new_line = f"| {severity} | {weakness} | {exercpt} | {clean_suggestion} |"
                new_lines.append(new_line)
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)
    return "\n".join(new_lines)