# backend/tests/test_gemini.py
import pytest
from services.gemini_service import get_reconciliation_from_gemini, get_data_quality_from_gemini

# 1. Test: Reconciliation returns the correct JSON keys
def test_reconcile_structure(mocker):
    # Mocking the AI response so we don't call the real API
    mock_response = mocker.patch('google.generativeai.GenerativeModel.generate_content')
    mock_response.return_value.text = '{"reconciled_medication": "Aspirin 81mg", "confidence_score": 0.9, "reasoning": "Test", "clinical_safety_check": "PASSED"}'
    
    sample_data = {"recent_labs": {"eGFR": 45}, "sources": []}
    result = get_reconciliation_from_gemini(sample_data)
    
    assert "reconciled_medication" in result [cite: 17, 51]
    assert "confidence_score" in result [cite: 17, 52]
    assert result["clinical_safety_check"] == "PASSED" [cite: 60]

# 2. Test: Data Quality catches the required dimensions
def test_quality_dimensions(mocker):
    mock_response = mocker.patch('google.generativeai.GenerativeModel.generate_content')
    mock_response.return_value.text = '{"overall_score": 62, "breakdown": {"accuracy": 50}, "issues_detected": []}'
    
    result = get_data_quality_from_gemini({"vital_signs": {"blood_pressure": "340/180"}})
    
    assert "overall_score" in result [cite: 63, 77]
    assert "breakdown" in result [cite: 63, 78]

# 3. Test: High severity issue detection
def test_severity_logic(mocker):
    mock_response = mocker.patch('google.generativeai.GenerativeModel.generate_content')
    mock_response.return_value.text = '{"issues_detected": [{"field": "bp", "severity": "high"}]}'
    
    result = get_data_quality_from_gemini({})
    assert result["issues_detected"][0]["severity"] == "high" [cite: 98]

# 4. Test: Handling empty medication lists (Edge Case)
def test_empty_sources(mocker):
    mock_response = mocker.patch('google.generativeai.GenerativeModel.generate_content')
    mock_response.return_value.text = '{"reconciled_medication": "None", "confidence_score": 0.0, "reasoning": "No data"}'
    
    result = get_reconciliation_from_gemini({"sources": []})
    assert result["confidence_score"] == 0.0

# 5. Test: Clinical Plausibility score presence
def test_plausibility_metric(mocker):
    mock_response = mocker.patch('google.generativeai.GenerativeModel.generate_content')
    mock_response.return_value.text = '{"breakdown": {"clinical_plausibility": 40}}'
    
    result = get_data_quality_from_gemini({})
    assert "clinical_plausibility" in result["breakdown"] [cite: 82]