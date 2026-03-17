import React, { useState } from 'react';

function App() {
  const [result, setResult] = useState(null);

  const handleReconcile = async () => {
    const testData = {
      patient_context: { age: 67, conditions: ["Type 2 Diabetes"] },
      sources: [{ system: "Pharmacy", medication: "Metformin 1000mg" }]
    };

    try {
      const response = await fetch("http://localhost:8000/api/reconcile/medication", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(testData),
      });

      const data = await response.json();
      setResult(data); // Store the "reconciled" data in our state
    } catch (error) {
      console.error("Error connecting to backend:", error);
    }
  };

  return (
    <div style={{ padding: '20px' }}>
      <h1>Clinical Data Engine</h1>
      <button onClick={handleReconcile}>Test Reconciliation</button>
      
      {result && (
        <div style={{ marginTop: '20px', border: '1px solid green', padding: '10px' }}>
          <h3>Result: {result.reconciled_medication}</h3>
          <p>Confidence: {result.confidence_score * 100}%</p>
          <p>Reasoning: {result.reasoning}</p>
        </div>
      )}
    </div>
  );
}

export default App;