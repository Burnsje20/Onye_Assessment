from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

# 🛑 CRITICAL: This allows your React app (port 3000) to talk to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

# This defines what the incoming data should look like
class MedicationRequest(BaseModel):
    patient_context: dict
    sources: List[dict]

@app.post("/api/reconcile/medication")
async def reconcile_medication(data: MedicationRequest):
    # This is where your AI logic will eventually go!
    # For now, we return "mock" data to test the connection.
    return {
        "reconciled_medication": "Metformin 500mg twice daily",
        "confidence_score": 0.88,
        "reasoning": "Mock response: Connection successful!"
    }