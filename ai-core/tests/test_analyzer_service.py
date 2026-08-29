import unittest
from unittest.mock import patch

from app.analyzer import analyze_batch, analyze_ticket, config


def fake_classifier(text, candidate_labels, **_):
    keyword_to_code = {
        "vpn": "vpn",
        "email": "email",
        "internet": "network",
        "wifi": "network",
        "printer": "printer",
        "password": "account",
        "account": "account",
        "hardware": "hardware",
        "software": "software",
        "access": "permission",
        "permission": "permission",
        "file": "permission",
    }
    selected_code = next(
        (code for keyword, code in keyword_to_code.items() if keyword in text),
        None,
    )
    selected_label = config.CATEGORY_LABEL_BY_CODE.get(selected_code)
    labels = list(candidate_labels)
    if selected_label:
        labels.remove(selected_label)
        labels.insert(0, selected_label)
        scores = [0.92] + [0.08 / (len(labels) - 1)] * (len(labels) - 1)
    else:
        scores = [0.30] + [0.70 / (len(labels) - 1)] * (len(labels) - 1)
    return {"labels": labels, "scores": scores}


class AnalyzerServiceTests(unittest.TestCase):
    def analyze(self, text, **kwargs):
        with patch(
            "app.analyzer.zero_shot_category.get_classifier",
            return_value=fake_classifier,
        ):
            return analyze_ticket(text, **kwargs)

    def test_full_output_contract_and_debug_trace(self):
        result = self.analyze(
            "وی پی ان من وصل نمی‌شود و احراز هویت خطا می‌دهد",
            ticket_id="T-1",
            debug=True,
        )
        self.assertEqual(result["analysis_status"], "completed")
        self.assertEqual(result["category"], "vpn")
        self.assertEqual(result["intent"], "vpn_authentication_error")
        self.assertEqual(result["summary"], result["summary_fa"])
        self.assertEqual(result["suggested_reply"], result["suggested_reply_fa"])
        self.assertEqual(result["reasons"], result["reasons_fa"])
        self.assertGreaterEqual(len(result["reasons_fa"]), 2)
        self.assertIn("decision_trace", result["raw_ai_response"])
        self.assertTrue(result["suggested_reply_fa"].startswith("سلام"))
        self.assertTrue(result["reply_quality_passed"])

    def test_organization_outage_is_critical_and_escalated(self):
        result = self.analyze("کل شرکت اینترنت ندارد و همه کاربران نمی‌توانند کار کنند")
        self.assertEqual(result["category"], "network")
        self.assertEqual(result["impact_label"], "organization_level")
        self.assertEqual(result["urgency"], "critical")
        self.assertTrue(result["should_escalate"])

    def test_repeated_unresolved_issue_uses_empathetic_tone(self):
        result = self.analyze("چند بار اعلام کردم هنوز مشکل ایمیل درست نشده و کسی جواب نمیده")
        self.assertIn(result["sentiment"], {"frustrated", "angry"})
        self.assertIn(result["reply_tone"], {"empathetic", "empathetic_urgent"})
        self.assertIn("عذرخواهی", result["suggested_reply_fa"])

    def test_ambiguous_short_ticket_requests_clarification(self):
        result = self.analyze("کار نمیکنه")
        self.assertEqual(result["category"], "unknown")
        self.assertTrue(result["needs_more_info"])
        self.assertIsNotNone(result["clarification_question_fa"])
        self.assertLess(result["confidence"], 0.55)

    def test_debug_output_is_absent_by_default(self):
        result = self.analyze("پرینتر چاپ نمی‌کند")
        self.assertNotIn("raw_ai_response", result)

    def test_model_error_details_are_not_leaked_without_debug(self):
        with (
            self.assertLogs("app.analyzer.zero_shot_category", level="WARNING"),
            patch(
                "app.analyzer.zero_shot_category.get_classifier",
                side_effect=RuntimeError("SECRET_PATH"),
            ),
        ):
            result = analyze_ticket("vpn وصل نمی‌شود")
        self.assertEqual(result["category"], "vpn")
        self.assertNotIn("SECRET_PATH", result["details"]["category_analysis"]["reason"])

    def test_batch_rejects_accidental_string_input(self):
        with self.assertRaises(TypeError):
            analyze_batch("vpn وصل نمی‌شود")


if __name__ == "__main__":
    unittest.main()
