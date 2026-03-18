// frontend/src/services/api.js
const API_BASE_URL = "http://localhost:8000/api";

export const medicationService = {
  // Logic for Part 1: Medication Reconciliation [cite: 16]
  reconcile: async (payload) => {
    const response = await fetch(`${API_BASE_URL}/reconcile/medication`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!response.ok) throw new Error("Reconciliation failed");
    return response.json();
  },

  // Logic for Part 1: Data Quality Validation [cite: 61]
  validateQuality: async (patientRecord) => {
    const response = await fetch(`${API_BASE_URL}/validate/data-quality`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(patientRecord),
    });
    if (!response.ok) throw new Error("Quality validation failed");
    return response.json();
  }
};