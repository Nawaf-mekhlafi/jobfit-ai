import os
import json
import logging
from openai import OpenAI
from dotenv import load_dotenv

# Initialize environment variables
load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class JobMatchAgent:
    def __init__(self):
        """
        Initializes the Production AI Agent using Groq's high-speed inference engine.
        Powered by Meta's Llama-3.3-70B for Enterprise-grade semantic analysis.
        """
        self.api_key = os.environ.get("GROQ_API_KEY")
        if not self.api_key:
            logging.error("CRITICAL: GROQ_API_KEY is missing from environment variables.")
            raise ValueError("Production environment requires a valid GROQ_API_KEY.")
            
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.groq.com/openai/v1"
        )

    def analyze_cv_against_job(self, cv_text: str, job_desc: str) -> dict:
        """
        Executes a massive parallel evaluation using highly optimized Prompt Engineering.
        Forces the LLM to return a complex JSON object containing all actionable insights.
        """
        
        system_prompt = """
        You are an elite Enterprise ATS Analyzer, a Senior Career Coach, and an Expert Copywriter.
        Your task is to deeply analyze the candidate's CV against the target Job Description and output ONLY a valid JSON object.
        
        CRITICAL INSTRUCTIONS FOR EACH MODULE:
        1. match_score: Calculate a strict, realistic match percentage (0-100) based on actual technical and soft skill overlap.
        2. overall_summary: Write a highly accurate, professional paragraph (3-4 sentences) assessing the fit. Be honest but constructive.
        3. matching_keywords: List exact skills present in BOTH the CV and Job Description.
        4. missing_keywords: List critical skills required by the job but missing from the CV. Return as a list of dictionaries [{"skill": "str", "platform": "str"}]. For EACH skill, accurately recommend the BEST educational platform to learn it (e.g., 'Coursera' for AI/Data, 'HubSpot' for Marketing, 'AWS Skill Builder' for Cloud, 'Udemy' for Design).
        5. ats_improvements: Provide 3 highly actionable, specific tips to modify the CV to pass ATS filters for this specific role.
        6. bullet_improvements: Select 2-3 weak achievements from the CV and rewrite them using the STAR method (Situation, Task, Action, Result). Add quantifiable metrics where plausible based on context.
        7. reverse_job_recommendations: Based solely on the CV's strengths, suggest 3-4 alternative, high-paying job titles the candidate is highly qualified for.
        8. cover_letter_draft: Write a premium, 3-paragraph Cover Letter. 
           - Extract the candidate's full name from the CV to use in the sign-off. 
           - Infer the company name from the Job Description (use 'Hiring Manager' if company is unknown). 
           - The letter MUST bridge the candidate's actual background to the target role's needs persuasively. 
           - Use proper paragraph breaks (\\n\\n). 
           - CRITICAL FORMATTING: The sign-off MUST be placed on entirely new lines at the very end. Format exactly like this:
             [End of last paragraph]
             \\n\\n
             Sincerely,
             \\n
             [Candidate Name]
           - NEVER use generic placeholders like [Company Name] or [Date].
        
        OUTPUT SCHEMA (Strict JSON Format):
        {
            "match_score": int,
            "overall_summary": "str",
            "matching_keywords": ["str"],
            "missing_keywords": [{"skill": "str", "platform": "str"}],
            "ats_improvements": ["str"],
            "bullet_improvements": ["str"],
            "reverse_job_recommendations": ["str"],
            "cover_letter_draft": "str"
        }
        """

        user_prompt = f"""
        --- CANDIDATE CV TEXT ---
        {cv_text}
        
        --- TARGET JOB DESCRIPTION ---
        {job_desc}
        """

        try:
            logging.info("Executing Enterprise API call to Groq (Llama 3.3 70B)...")
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.15 
            )
            
            raw_response = response.choices[0].message.content
            result_json = json.loads(raw_response)
            
            logging.info(f"AI Inference completed. Computed Match Score: {result_json.get('match_score')}%")
            return result_json
            
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse LLM response into JSON framework: {e}")
            raise
        except Exception as e:
            logging.error(f"Groq API Inference encountered an error: {e}")
            raise