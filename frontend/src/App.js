import React, { useState } from "react";
import "./App.css";
import LoadingRing from "./components/LoadingRing";
import { sampleDataQualityRecord, sampleMedicationPayload } from "./data/samplePayload";
import { medicationService } from "./services/api";

function getQualityColor(score) {
  if (score >= 80) return "#48bb78";
  if (score >= 60) return "#ed8936";
  return "#f56565";
}

function App() {
  const [reconciledData, setReconciledData] = useState(null);
  const [qualityData, setQualityData] = useState(null);
  const [status, setStatus] = useState("pending");
  const [loadingTask, setLoadingTask] = useState(null);
  const [errorMessage, setErrorMessage] = useState("");

  const isLoading = loadingTask !== null;

  const runTask = async (taskName, task) => {
    setLoadingTask(taskName);
    setErrorMessage("");

    try {
      await task();
    } catch (error) {
      setErrorMessage(error.message || "Request failed.");
    } finally {
      setLoadingTask(null);
    }
  };

  const handleReconcile = async () => {
    await runTask("reconcile", async () => {
      const data = await medicationService.reconcile(sampleMedicationPayload);
      setReconciledData(data);
      setStatus("pending");
    });
  };

  const handleQualityAudit = async () => {
    await runTask("quality", async () => {
      const data = await medicationService.validateQuality(sampleDataQualityRecord);
      setQualityData(data);
    });
  };

  return (
    <div style={{ padding: "40px", maxWidth: "800px", margin: "0 auto" }}>
      <h1>Clinical Reconciliation Engine</h1>

      <div className="action-row">
        <button
          className="reconcile-button"
          disabled={isLoading}
          onClick={handleReconcile}
          type="button"
        >
          {loadingTask === "reconcile" ? <LoadingRing size="small" /> : null}
          <span>{loadingTask === "reconcile" ? "Running AI Reconciliation..." : "Run AI Reconciliation"}</span>
        </button>

        <button
          className="reconcile-button secondary-button"
          disabled={isLoading}
          onClick={handleQualityAudit}
          type="button"
        >
          {loadingTask === "quality" ? <LoadingRing size="small" /> : null}
          <span>{loadingTask === "quality" ? "Running Data Quality Check..." : "Run Data Quality Check"}</span>
        </button>
      </div>

      {isLoading ? (
        <div className="loading-state" role="status" aria-live="polite">
          <LoadingRing size="medium" />
          <span>
            {loadingTask === "quality"
              ? "Checking the record for completeness, accuracy, timeliness, and plausibility."
              : "Checking the medication records now."}
          </span>
        </div>
      ) : null}

      {errorMessage ? (
        <p className="error-message" role="alert">
          {errorMessage}
        </p>
      ) : null}

      {reconciledData ? (
        <div
          style={{
            marginTop: "30px",
            padding: "20px",
            border: "1px solid #ccc",
            borderRadius: "8px",
            backgroundColor:
              status === "approved" ? "#e6fffa" : status === "rejected" ? "#fff5f5" : "#fff",
          }}
        >
          <h2>AI Suggestion: {reconciledData.reconciled_medication}</h2>

          <div style={{ marginBottom: "15px" }}>
            <strong>Confidence Score:</strong> {(reconciledData.confidence_score * 100).toFixed(0)}%
            <div
              style={{
                width: "100%",
                background: "#eee",
                height: "10px",
                borderRadius: "5px",
                marginTop: "5px",
              }}
            >
              <div
                style={{
                  width: `${reconciledData.confidence_score * 100}%`,
                  height: "100%",
                  backgroundColor: reconciledData.confidence_score > 0.8 ? "#48bb78" : "#ed8936",
                  borderRadius: "5px",
                }}
              />
            </div>
          </div>

          <p>
            <strong>Reasoning:</strong> {reconciledData.reasoning}
          </p>
          <p>
            <strong>Safety Check:</strong> {reconciledData.clinical_safety_check}
          </p>

          {reconciledData.recommended_actions?.length ? (
            <div>
              <strong>Recommended Actions:</strong>
              <ul>
                {reconciledData.recommended_actions.map((action) => (
                  <li key={action}>{action}</li>
                ))}
              </ul>
            </div>
          ) : null}

          {status === "pending" ? (
            <div style={{ marginTop: "20px", display: "flex", gap: "10px" }}>
              <button
                onClick={() => setStatus("approved")}
                style={{
                  backgroundColor: "#48bb78",
                  color: "white",
                  border: "none",
                  padding: "10px 20px",
                  cursor: "pointer",
                }}
                type="button"
              >
                Approve Suggestion
              </button>
              <button
                onClick={() => setStatus("rejected")}
                style={{
                  backgroundColor: "#f56565",
                  color: "white",
                  border: "none",
                  padding: "10px 20px",
                  cursor: "pointer",
                }}
                type="button"
              >
                Reject Suggestion
              </button>
            </div>
          ) : (
            <div style={{ marginTop: "20px", fontWeight: "bold" }}>
              Decision Recorded: {status.toUpperCase()}
            </div>
          )}
        </div>
      ) : null}

      {qualityData ? (
        <div
          style={{
            marginTop: "30px",
            padding: "20px",
            border: "1px solid #ccc",
            borderRadius: "8px",
            backgroundColor: "#fff",
          }}
        >
          <h2>Data Quality Score</h2>
          <div className="quality-score-row">
            <span
              className="quality-badge"
              style={{ backgroundColor: getQualityColor(qualityData.overall_score) }}
            >
              {qualityData.overall_score}/100
            </span>
            <span className="quality-score-text">
              {qualityData.overall_score >= 80
                ? "Green: looks strong"
                : qualityData.overall_score >= 60
                  ? "Yellow: needs review"
                  : "Red: high concern"}
            </span>
          </div>

          <div style={{ marginTop: "15px" }}>
            <strong>Breakdown:</strong>
            <ul>
              {Object.entries(qualityData.breakdown || {}).map(([key, value]) => (
                <li key={key}>
                  {key.replaceAll("_", " ")}: {value}
                </li>
              ))}
            </ul>
          </div>

          <div style={{ marginTop: "15px" }}>
            <strong>Issues Detected:</strong>
            <ul>
              {(qualityData.issues_detected || []).map((issue, index) => (
                <li key={`${issue.field}-${index}`}>
                  <strong>{issue.field}</strong>: {issue.issue} ({issue.severity})
                </li>
              ))}
            </ul>
          </div>
        </div>
      ) : null}
    </div>
  );
}

export default App;
