import pytest
from unittest.mock import patch

from app.analyzer.analyzer_service import analyze_ticket
from scripts.run_analyzer_manual_suite import SCENARIOS
from tests.test_analyzer_service import fake_classifier


@pytest.mark.parametrize("scenario", SCENARIOS, ids=[s["ticket_id"] for s in SCENARIOS])
def test_analyzer_golden_scenarios(scenario):
    """
    Automated regression test over the 15 enterprise IT service desk scenarios.
    Validates category, intent, urgency, sentiment, summary, and reply quality.
    """
    with patch(
        "app.analyzer.zero_shot_category.get_classifier",
        return_value=fake_classifier,
    ):
        result = analyze_ticket(
            scenario["text"],
            ticket_id=scenario["ticket_id"],
            debug=False,
        )

    assert result["analysis_status"] == "completed"
    assert result["category"] == scenario["expected_category"], (
        f"Category mismatch for {scenario['ticket_id']}: {result['category']} != {scenario['expected_category']}"
    )
    assert result["intent"] in scenario["expected_intents"], (
        f"Intent mismatch for {scenario['ticket_id']}: {result['intent']} not in {scenario['expected_intents']}"
    )
    assert result["urgency"] in scenario["expected_urgency_levels"], (
        f"Urgency mismatch for {scenario['ticket_id']}: {result['urgency']} not in {scenario['expected_urgency_levels']}"
    )
    assert result["sentiment"] in scenario["expected_sentiments"], (
        f"Sentiment mismatch for {scenario['ticket_id']}: {result['sentiment']} not in {scenario['expected_sentiments']}"
    )
    assert len(result["summary_fa"]) > 5
    assert len(result["suggested_reply_fa"]) > 10
