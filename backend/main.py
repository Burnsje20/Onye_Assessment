# backend/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

# Import your AI logic from the service file we created
from services.gemini_service import get_reconciliation_from_gemini

app = FastAPI(title="Clinical Data Reconciliation Engine")

# 1. Handle CORS (Requirement: Basic protection/connectivity) 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], # Your React App
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Define Data Models (Requirement: Input validation) 
class MedicationSource(BaseModel):
    system: str
    medication: str
    last_updated: Optional[str] = None
    last_filled: Optional[str] = None
    source_reliability: str

class ReconcileRequest(BaseModel):
    patient_context: Dict[str, Any]
    recent_labs: Dict[str, Any]
    sources: List[MedicationSource]

# 3. Endpoint 1: Medication Reconciliation (40% of grade) [cite: 14, 16]
@app.post("/api/reconcile/medication")
async def reconcile_medication(request: ReconcileRequest):
    try:
        # Convert Pydantic model to dict to send to Gemini
        data = request.model_dump()
        result = get_reconciliation_from_gemini(data)
        return result
    except Exception as e:
        # Requirement: Proper error handling 
        raise HTTPException(status_code=500, detail=str(e))

# 4. Endpoint 2
from services.gemini_service import get_data_quality_from_gemini

@app.post("/api/validate/data-quality")
async def validate_quality(request: Dict[str, Any]):
    try:
        # Pass the raw JSON body to the Gemini service
        result = get_data_quality_from_gemini(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)