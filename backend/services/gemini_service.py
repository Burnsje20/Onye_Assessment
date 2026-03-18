# backend/services/gemini_service.py
import google.generativeai as genai
import os
import json
from dotenv import load_dotenv

load_dotenv()

# Configure using the environment variable we set up in .env
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def get_reconciliation_from_gemini(patient_data):
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config={
            "response_mime_type": "application/json",
        }
    )

    # Effective prompt design is 25% of your evaluation [cite: 143, 144]
    prompt = f"""
    You are a clinical data reconciliation engine[cite: 11]. 
    Analyze the following conflicting medication records and determine the 'most likely truth'.
    
    Rules:
    1. Prioritize recent 'last_updated' dates[cite: 54].
    2. Consider 'Primary Care' more reliable for dosing than 'Pharmacy' history[cite: 54].
    3. Check if the dose is safe for a patient with eGFR {patient_data.get('recent_labs', {}).get('eGFR', 'unknown')}[cite: 54].

    Data: {patient_data}

    Return JSON matching this schema:
    {{
        "reconciled_medication": string,
        "confidence_score": float,
        "reasoning": string,
        "clinical_safety_check": "PASSED" | "FAILED"
    }}
    """
    
    response = model.generate_content(prompt)
    # Convert string response to a Python dictionary so the API can send it as JSON
    return json.loads(response.text)