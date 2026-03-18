import services.gemini_service as gemini_service
from services.gemini_service import get_reconciliation_from_gemini, get_data_quality_from_gemini


def setup_function():
    gemini_service.PROMPT_CACHE.clear()

def test_reconcile_structure(mocker):
    mock_response = mocker.patch('google.generativeai.GenerativeModel.generate_content')
    mock_response.return_value.text = '{"reconciled_medication": "Aspirin 81mg", "confidence_score": 0.9, "reasoning": "Test", "clinical_safety_check": "PASSED"}'

    sample_data = {"recent_labs": {"eGFR": 45}, "sources": []}
    result = get_reconciliation_from_gemini(sample_data)

    assert "reconciled_medication" in result
    assert "confidence_score" in result
    assert result["clinical_safety_check"] == "PASSED"


def test_quality_dimensions(mocker):
    mock_response = mocker.patch('google.generativeai.GenerativeModel.generate_content')
    mock_response.return_value.text = '{"overall_score": 62, "breakdown": {"accuracy": 50}, "issues_detected": []}'

    result = get_data_quality_from_gemini({"vital_signs": {"blood_pressure": "340/180"}})

    assert "overall_score" in result
    assert "breakdown" in result


def test_severity_logic(mocker):
    mock_response = mocker.patch('google.generativeai.GenerativeModel.generate_content')
    mock_response.return_value.text = '{"issues_detected": [{"field": "bp", "severity": "high"}]}'

    result = get_data_quality_from_gemini({})
    assert result["issues_detected"][0]["severity"] == "high"


def test_empty_sources(mocker):
    mock_response = mocker.patch('google.generativeai.GenerativeModel.generate_content')
    mock_response.return_value.text = '{"reconciled_medication": "None", "confidence_score": 0.0, "reasoning": "No data"}'

    result = get_reconciliation_from_gemini({"sources": []})
    assert result["confidence_score"] == 0.0


def test_plausibility_metric(mocker):
    mock_response = mocker.patch('google.generativeai.GenerativeModel.generate_content')
    mock_response.return_value.text = '{"breakdown": {"clinical_plausibility": 40}}'

    result = get_data_quality_from_gemini({})
    assert "clinical_plausibility" in result["breakdown"]


def test_retry_on_rate_limit(mocker):
    mock_response = mocker.Mock()
    mock_response.text = '{"reconciled_medication": "Aspirin 81mg", "confidence_score": 0.8, "reasoning": "Recovered", "clinical_safety_check": "PASSED"}'
    generate_content = mocker.patch(
        'google.generativeai.GenerativeModel.generate_content',
        side_effect=[RuntimeError("429 rate limit"), mock_response],
    )
    mocker.patch('services.gemini_service.time.sleep')

    result = get_reconciliation_from_gemini({"sources": []})

    assert result["clinical_safety_check"] == "PASSED"
    assert generate_content.call_count == 2


def test_prompt_cache_reuses_previous_response(mocker):
    mock_response = mocker.Mock()
    mock_response.text = '{"overall_score": 75, "breakdown": {"accuracy": 75}, "issues_detected": []}'
    generate_content = mocker.patch(
        'google.generativeai.GenerativeModel.generate_content',
        return_value=mock_response,
    )

    first_result = get_data_quality_from_gemini({"last_updated": "2024-06-15"})
    second_result = get_data_quality_from_gemini({"last_updated": "2024-06-15"})

    assert first_result == second_result
    assert generate_content.call_count == 1
