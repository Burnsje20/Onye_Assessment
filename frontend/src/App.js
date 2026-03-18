// frontend/src/App.js
import React, { useState } from 'react';
import { medicationService } from './services/api';

function App() {
  const [reconciledData, setReconciledData] = useState(null);
  const [status, setStatus] = useState("pending"); // pending, approved, rejected

  const handleReconcile = async () => {
    try {
      // Example input from the assessment PDF [cite: 21-47]
      const payload = {
        patient_context: { age: 67 },
        recent_labs: { eGFR: 45 },
        sources: [
          { system: "Primary Care", medication: "Metformin 500mg twice daily", last_updated: "2025-01-20", source_reliability: "high" },
          { system: "Pharmacy", medication: "Metformin 1000mg daily", last_filled: "2025-01-25", source_reliability: "medium" }
        ]
      };

      const data = await medicationService.reconcile(payload);
      setReconciledData(data);
      setStatus("pending"); 
    } catch (err) {
      console.error("Failed to reconcile:", err);
    }
  };

  return (
    <div style={{ padding: '40px', maxWidth: '800px', margin: '0 auto' }}>
      <h1>Clinical Reconciliation Engine</h1>
      <button onClick={handleReconcile}>Run AI Reconciliation</button>

      {reconciledData && (
        <div style={{ 
          marginTop: '30px', 
          padding: '20px', 
          border: '1px solid #ccc',
          borderRadius: '8px',
          backgroundColor: status === 'approved' ? '#e6fffa' : status === 'rejected' ? '#fff5f5' : '#fff'
        }}>
          <h2>AI Suggestion: {reconciledData.reconciled_medication}</h2>
          
          {/* Visualizing Confidence Score  */}
          <div style={{ marginBottom: '15px' }}>
            <strong>Confidence Score:</strong> {(reconciledData.confidence_score * 100).toFixed(0)}%
            <div style={{ width: '100%', bg: '#eee', height: '10px', borderRadius: '5px', marginTop: '5px' }}>
              <div style={{ 
                width: `${reconciledData.confidence_score * 100}%`, 
                height: '100%', 
                backgroundColor: reconciledData.confidence_score > 0.8 ? '#48bb78' : '#ed8936',
                borderRadius: '5px' 
              }} />
            </div>
          </div>

          <p><strong>Reasoning:</strong> {reconciledData.reasoning}</p>
          <p><strong>Safety Check:</strong> {reconciledData.clinical_safety_check}</p>

          {/* Approve/Reject Buttons  */}
          {status === "pending" ? (
            <div style={{ marginTop: '20px', display: 'flex', gap: '10px' }}>
              <button 
                onClick={() => setStatus("approved")}
                style={{ backgroundColor: '#48bb78', color: 'white', border: 'none', padding: '10px 20px', cursor: 'pointer' }}
              >
                Approve Suggestion
              </button>
              <button 
                onClick={() => setStatus("rejected")}
                style={{ backgroundColor: '#f56565', color: 'white', border: 'none', padding: '10px 20px', cursor: 'pointer' }}
              >
                Reject Suggestion
              </button>
            </div>
          ) : (
            <div style={{ marginTop: '20px', fontWeight: 'bold' }}>
              Decision Recorded: {status.toUpperCase()}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default App;