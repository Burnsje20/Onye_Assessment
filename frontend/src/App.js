// frontend/src/App.js
import React, { useState } from 'react';
import { medicationService } from './services/api';

function App() {
  const [loading, setLoading] = useState(false);
  const [qualityData, setQualityData] = useState(null);

  const checkQuality = async () => {
    setLoading(true);
    try {
      // Mock data matching the assessment example [cite: 68-73]
      const mockRecord = {
        demographics: { name: "John Doe", dob: "1955-03-15", gender: "M" },
        medications: ["Metformin 500mg"],
        vital_signs: { blood_pressure: "340/180", heart_rate: 72 },
        last_updated: "2024-06-15"
      };

      const data = await medicationService.validateQuality(mockRecord);
      setQualityData(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '40px', fontFamily: 'sans-serif' }}>
      <h1>Clinical Data Dashboard</h1>
      <button onClick={checkQuality} disabled={loading}>
        {loading ? "Analyzing..." : "Run Quality Audit"}
      </button>

      {qualityData && (
        <div style={{ marginTop: '20px' }}>
          <h2>Overall Score: {qualityData.overall_score}/100</h2>
          {/* visual indicators (red/yellow/green)  */}
          <div style={{ 
            height: '20px', 
            width: '200px', 
            backgroundColor: qualityData.overall_score > 70 ? 'green' : 'red',
            borderRadius: '10px'
          }} />
          
          <h3>Issues Detected:</h3>
          <ul>
            {qualityData.issues_detected.map((issue, index) => (
              <li key={index}>
                <strong>{issue.field}</strong>: {issue.issue} ({issue.severity})
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default App;