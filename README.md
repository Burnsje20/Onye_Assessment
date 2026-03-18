# Clinical Data Reconciliation Engine

Mini full-stack submission for the EHR Integration Intern take-home assessment. The application reconciles conflicting medication records with an LLM, audits record quality, and presents both workflows in a clinician-friendly dashboard.

## What the app does

- `POST /api/reconcile/medication` accepts conflicting medication records and returns the most likely truth, a confidence score, reasoning, recommended actions, and a safety check.
- `POST /api/validate/data-quality` scores a patient record across completeness, accuracy, timeliness, and clinical plausibility.
- The React dashboard lets a user run both workflows, see loading state while AI is working, review confidence and quality indicators, and approve or reject the medication recommendation.

## Tech stack

- Backend: FastAPI + Pydantic
- Frontend: React
- LLM: Google Gemini (`gemini-2.5-flash`)
- Test tooling: `pytest`, `pytest-mock`, React Testing Library

## Why Gemini

I used Google Gemini because it offered a fast response profile for prompt-driven structured output and fit the needs of a small take-home project well. The backend keeps the provider API key on the server in `backend/.env`, so the frontend never exposes the Gemini key directly.

## Project structure

```text
.
|-- backend
|   |-- main.py
|   |-- requirements.txt
|   |-- services
|   |   `-- gemini_service.py
|   `-- tests
|       `-- test_gemini.py
|-- frontend
|   |-- package.json
|   |-- public
|   `-- src
|       |-- components
|       |   `-- LoadingRing.js
|       |-- data
|       |   `-- samplePayload.js
|       |-- services
|       |   `-- api.js
|       |-- App.css
|       |-- App.js
|       |-- App.test.js
|       |-- index.css
|       `-- index.js
`-- README.md
```

## Local setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- A Gemini API key

### Backend

1. Create and activate a virtual environment.
2. Install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r backend\requirements.txt
```

3. Create `backend/.env`:

```env
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.5-flash
```

4. Start the API:

```powershell
cd backend
python -m uvicorn main:app --reload --port 8000
```

### Frontend

```powershell
cd frontend
npm install
npm start
```

Open `http://localhost:3000`.

## Running tests

### Backend

```powershell
cd backend
python -m pytest tests -q
```

### Frontend

```powershell
cd frontend
npm test -- --watchAll=false
```

## API examples

### Medication reconciliation

```json
{
  "patient_context": {
    "age": 67,
    "conditions": ["Type 2 Diabetes", "Hypertension"],
    "recent_labs": { "eGFR": 45 }
  },
  "sources": [
    {
      "system": "Hospital EHR",
      "medication": "Metformin 1000mg twice daily",
      "last_updated": "2024-10-15",
      "source_reliability": "high"
    },
    {
      "system": "Primary Care",
      "medication": "Metformin 500mg twice daily",
      "last_updated": "2025-01-20",
      "source_reliability": "high"
    },
    {
      "system": "Pharmacy",
      "medication": "Metformin 1000mg daily",
      "last_filled": "2025-01-25",
      "source_reliability": "medium"
    }
  ]
}
```

### Data quality validation

```json
{
  "demographics": { "name": "John Doe", "dob": "1955-03-15", "gender": "M" },
  "medications": ["Metformin 500mg", "Lisinopril 10mg"],
  "allergies": [],
  "conditions": ["Type 2 Diabetes"],
  "vital_signs": { "blood_pressure": "340/180", "heart_rate": 72 },
  "last_updated": "2024-06-15"
}
```

## Prompt engineering approach

- The medication prompt explicitly weighs source recency, source reliability, and renal safety context.
- The data-quality prompt checks the four rubric dimensions from the assessment: completeness, accuracy, timeliness, and clinical plausibility.
- Both prompts ask for strict JSON output so the backend can safely return structured responses to the frontend.

## Key design decisions and trade-offs

- I kept the backend thin and moved LLM-specific logic into `backend/services/gemini_service.py` to keep the API layer readable.
- I used fixed sample inputs in the dashboard so the project is easy to demo locally without needing form building or persistence.
- I kept storage in-memory because the assessment allows it and a database would add setup cost without improving the core reconciliation workflow.
- I stayed with the existing `google-generativeai` SDK to minimize migration risk during the assignment.

## What I would improve with more time

- Add request caching and stronger rate-limit handling around the LLM calls.
- Add real user input forms instead of sample payload buttons.
- Add backend authentication for application requests, not just provider key protection.
- Containerize the stack with Docker and add a deployment target.
- Migrate from the deprecated `google-generativeai` package to the newer Google Gen AI SDK.

## Estimated time spent
- 17 hours
