# backend/services/gemini_service.py
import json
import os
import time
from pathlib import Path

import google.generativeai as genai
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[1]
ENV_PATH = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)
DEFAULT_MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
RETRY_DELAYS_SECONDS = (1, 2)
PROMPT_CACHE = {}

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


def _extract_recent_labs(patient_data):
    patient_context = patient_data.get("patient_context", {}) or {}
    return patient_context.get("recent_labs") or patient_data.get("recent_labs", {}) or {}


def _build_model():
    if not os.getenv("GEMINI_API_KEY"):
        raise RuntimeError(f"Missing GEMINI_API_KEY in {ENV_PATH}")

    return genai.GenerativeModel(
        model_name=DEFAULT_MODEL_NAME,
        generation_config={"response_mime_type": "application/json"},
    )


def _clone_data(data):
    return json.loads(json.dumps(data))


def _is_retryable_error(error):
    message = str(error).lower()
    return any(keyword in message for keyword in ("429", "quota", "rate limit", "resourceexhausted"))


def _parse_json_response(response):
    raw_text = (response.text or "").strip()
    if not raw_text:
        raise RuntimeError("Gemini returned an empty response")

    cleaned_text = raw_text.removeprefix("```json").removeprefix("```").removesuffix("```").strip()

    try:
        return json.loads(cleaned_text)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Gemini returned invalid JSON: {raw_text}") from exc


def _generate_json_from_prompt(prompt):
    cached_response = PROMPT_CACHE.get(prompt)
    if cached_response is not None:
        return _clone_data(cached_response)

    model = _build_model()
    last_error = None

    for attempt in range(len(RETRY_DELAYS_SECONDS) + 1):
        try:
            response = model.generate_content(prompt)
            parsed_response = _parse_json_response(response)
            PROMPT_CACHE[prompt] = _clone_data(parsed_response)
            return parsed_response
        except Exception as exc:
            last_error = exc
            if attempt >= len(RETRY_DELAYS_SECONDS) or not _is_retryable_error(exc):
                raise

            time.sleep(RETRY_DELAYS_SECONDS[attempt])

    raise last_error


def get_reconciliation_from_gemini(patient_data):
    recent_labs = _extract_recent_labs(patient_data)

    prompt = f"""
    You are a clinical data reconciliation engine.
    Analyze the following conflicting medication records and determine the most likely truth.

    Rules:
    1. Prioritize recent clinical updates over older records.
    2. Consider primary care or clinician-authored sources more reliable for dosing than pharmacy history alone.
    3. Consider the patient's renal safety context using eGFR {recent_labs.get('eGFR', 'unknown')}.
    4. Return concise reasoning that a clinician can scan quickly.
    5. Recommend follow-up actions when source conflicts remain.

    Data: {patient_data}

    Return JSON matching this schema:
    {{
        "reconciled_medication": string,
        "confidence_score": float,
        "reasoning": string,
        "recommended_actions": [string],
        "clinical_safety_check": "PASSED" | "FAILED"
    }}
    """

    return _generate_json_from_prompt(prompt)


def get_data_quality_from_gemini(patient_record):
    prompt = f"""
    You are a clinical data auditor. Analyze the following patient record for quality.

    Check for:
    1. Accuracy: Are values like blood pressure or heart rate physiologically possible?
    2. Completeness: Are essential fields like allergies empty?
    3. Timeliness: Is the last_updated date too old (for example, older than six months)?
    4. Clinical Plausibility: Do the medications match the conditions?

    Record: {patient_record}

    Return JSON matching this schema:
    {{
        "overall_score": integer (0-100),
        "breakdown": {{
            "completeness": int,
            "accuracy": int,
            "timeliness": int,
            "clinical_plausibility": int
        }},
        "issues_detected": [
            {{ "field": string, "issue": string, "severity": "low" | "medium" | "high" }}
        ]
    }}
    """

    return _generate_json_from_prompt(prompt)
