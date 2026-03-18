// frontend/src/services/api.js
const API_BASE_URL = "http://localhost:8000/api";

async function request(path, payload, fallbackMessage) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  const data = await response.json().catch(() => null);

  if (!response.ok) {
    throw new Error(data?.detail || fallbackMessage);
  }

  return data;
}

export const medicationService = {
  reconcile: async (payload) => {
    return request("/reconcile/medication", payload, "Reconciliation failed");
  },

  validateQuality: async (patientRecord) => {
    return request("/validate/data-quality", patientRecord, "Quality validation failed");
  },
};
