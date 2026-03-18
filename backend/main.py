from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from services.gemini_service import (
    get_data_quality_from_gemini,
    get_reconciliation_from_gemini,
)

app = FastAPI(title="Clinical Data Reconciliation Engine", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MedicationSource(BaseModel):
    system: str
    medication: str
    last_updated: Optional[str] = None
    last_filled: Optional[str] = None
    source_reliability: str

class ReconcileRequest(BaseModel):
    patient_context: Dict[str, Any]
    recent_labs: Optional[Dict[str, Any]] = None
    sources: List[MedicationSource]


@app.post("/api/reconcile/medication")
async def reconcile_medication(request: ReconcileRequest):
    try:
        return get_reconciliation_from_gemini(request.model_dump())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Medication reconciliation failed: {e}")


@app.post("/api/validate/data-quality")
async def validate_quality(request: Dict[str, Any]):
    try:
        return get_data_quality_from_gemini(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Data quality validation failed: {e}")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
