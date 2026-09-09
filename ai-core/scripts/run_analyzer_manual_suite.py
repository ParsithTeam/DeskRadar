import json
import sys
import time
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ai_core_root = str(Path(__file__).resolve().parents[1])
if ai_core_root not in sys.path:
    sys.path.insert(0, ai_core_root)

from app.analyzer.analyzer_service import analyze_batch, analyze_ticket

SCENARIOS = [
    {
        "ticket_id": "TEST-001",
        "name": "VPN authentication with high urgency",
        "text": "سلام، من نیم ساعت دیگه جلسه دارم ولی وی پی ان قطعه و احراز هویت نمیکنه",
        "expected_category": "vpn",
        "expected_intents": [
            "vpn_authentication_error",
            "vpn_connection_issue",
        ],
        "expected_urgency_levels": [
            "high",
            "critical",
        ],
        "expected_sentiments": [
            "negative",
            "frustrated",
            "angry",
            "neutral",
        ],
    },
    {
        "ticket_id": "TEST-002",
        "name": "Email quota issue",
        "text": "حجم ایمیل من پر شده و نمی تونم پیام جدید دریافت کنم",
        "expected_category": "email",
        "expected_intents": [
            "email_quota_issue",
            "email_send_receive_issue",
        ],
        "expected_urgency_levels": [
            "medium",
            "high",
        ],
        "expected_sentiments": [
            "negative",
            "neutral",
        ],
    },
    {
        "ticket_id": "TEST-003",
        "name": "Critical network outage",
        "text": "کل شرکت اینترنت ندارد و همه کاربران دچار مشکل شده اند. کارها کاملا متوقف شده",
        "expected_category": "network",
        "expected_intents": [
            "network_drop",
        ],
        "expected_urgency_levels": [
            "critical",
            "high",
        ],
        "expected_sentiments": [
            "negative",
            "frustrated",
            "angry",
        ],
    },
    {
        "ticket_id": "TEST-004",
        "name": "Low priority printer issue",
        "text": "هر وقت فرصت داشتید لطفا پرینتر اتاق من را بررسی کنید، فوری نیست",
        "expected_category": "printer",
        "expected_intents": [
            "printer_error",
            "general_printer_issue",
        ],
        "expected_urgency_levels": [
            "low",
            "medium",
        ],
        "expected_sentiments": [
            "positive",
            "neutral",
            "negative",
        ],
    },
    {
        "ticket_id": "TEST-005",
        "name": "Account password reset",
        "text": "رمز سامانه را فراموش کردم و وارد حساب کاربری نمی شود",
        "expected_category": "account",
        "expected_intents": [
            "account_lock",
            "account_access_issue",
        ],
        "expected_urgency_levels": [
            "medium",
            "high",
        ],
        "expected_sentiments": [
            "negative",
            "neutral",
        ],
    },
    {
        "ticket_id": "TEST-006",
        "name": "Permission denied",
        "text": "برای پوشه اشتراکی واحد مالی خطای access denied میگیرم و دسترسی ندارم",
        "expected_category": "permission",
        "expected_intents": [
            "permission_denied",
            "shared_folder_issue",
        ],
        "expected_urgency_levels": [
            "medium",
            "high",
        ],
        "expected_sentiments": [
            "negative",
            "neutral",
            "frustrated",
        ],
    },
    {
        "ticket_id": "TEST-007",
        "name": "Software install request",
        "text": "لطفا نرم افزار جدید مورد نیاز تیم فروش را روی سیستم من نصب کنید",
        "expected_category": "software",
        "expected_intents": [
            "software_install",
            "software_access_request",
        ],
        "expected_urgency_levels": [
            "low",
            "medium",
        ],
        "expected_sentiments": [
            "positive",
            "neutral",
        ],
    },
    {
        "ticket_id": "TEST-008",
        "name": "Hardware failure",
        "text": "لپ تاپ من روشن نمی شود و چراغ پاور هم خاموش است",
        "expected_category": "hardware",
        "expected_intents": [
            "hardware_failure",
        ],
        "expected_urgency_levels": [
            "medium",
            "high",
        ],
        "expected_sentiments": [
            "negative",
            "neutral",
        ],
    },
    {
        "ticket_id": "TEST-009",
        "name": "Frustrated repeated issue",
        "text": "چند بار اعلام کردم هنوز مشکل ایمیل من درست نشده و کسی جواب نمیده",
        "expected_category": "email",
        "expected_intents": [
            "email_access_issue",
            "email_send_receive_issue",
            "general_email_issue",
        ],
        "expected_urgency_levels": [
            "medium",
            "high",
        ],
        "expected_sentiments": [
            "frustrated",
            "angry",
            "negative",
        ],
    },
    {
        "ticket_id": "TEST-010",
        "name": "Empty ticket",
        "text": "",
        "expected_category": "unknown",
        "expected_intents": [
            "unknown_intent",
        ],
        "expected_urgency_levels": [
            "unknown",
        ],
        "expected_sentiments": [
            "unknown",
        ],
    },
]


REQUIRED_TOP_LEVEL_KEYS = [
    "ticket_id",
    "input_text",
    "normalized_text",
    "analysis_status",
    "category",
    "category_label_fa",
    "category_score",
    "category_source",
    "intent",
    "intent_label_fa",
    "intent_score",
    "urgency_level",
    "urgency_score",
    "sentiment",
    "frustration_score",
    "summary",
    "short_summary",
    "suggested_reply",
    "required_info",
    "escalation_hint",
    "confidence",
    "confidence_percent",
    "confidence_level",
    "reasons",
    "details",
]


def is_missing(value) -> bool:
    return value is None or value == "" or value == [] or value == {}


def check_required_keys(result: dict) -> list:
    issues = []

    for key in REQUIRED_TOP_LEVEL_KEYS:
        if key not in result:
            issues.append(f"missing_key:{key}")

    return issues


def check_expected_value(result: dict, field: str, expected_values) -> str:
    actual_value = result.get(field)

    if isinstance(expected_values, list):
        if actual_value not in expected_values:
            return f"{field}: expected one of {expected_values}, got {actual_value}"
        return ""

    if actual_value != expected_values:
        return f"{field}: expected {expected_values}, got {actual_value}"

    return ""


def evaluate_result(scenario: dict, result: dict) -> dict:
    errors = []
    warnings = []

    errors.extend(check_required_keys(result))

    if result.get("analysis_status") != "completed":
        errors.append(f"analysis_status is {result.get('analysis_status')}")

    category_warning = check_expected_value(
        result,
        "category",
        scenario["expected_category"],
    )
    if category_warning:
        warnings.append(category_warning)

    intent_warning = check_expected_value(
        result,
        "intent",
        scenario["expected_intents"],
    )
    if intent_warning:
        warnings.append(intent_warning)

    urgency_warning = check_expected_value(
        result,
        "urgency_level",
        scenario["expected_urgency_levels"],
    )
    if urgency_warning:
        warnings.append(urgency_warning)

    sentiment_warning = check_expected_value(
        result,
        "sentiment",
        scenario["expected_sentiments"],
    )
    if sentiment_warning:
        warnings.append(sentiment_warning)

    if is_missing(result.get("summary")):
        errors.append("summary is empty")

    if is_missing(result.get("suggested_reply")):
        errors.append("suggested_reply is empty")

    if is_missing(result.get("reasons")):
        errors.append("reasons is empty")

    confidence = result.get("confidence")

    if confidence is None:
        errors.append("confidence is missing")
    elif not 0 <= float(confidence) <= 1:
        errors.append(f"confidence out of range: {confidence}")

    return {
        "passed": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
    }


def print_case_report(scenario: dict, result: dict, evaluation: dict) -> None:
    status = "PASS" if evaluation["passed"] else "FAIL"

    print("=" * 90)
    print(f"{status} | {scenario['ticket_id']} | {scenario['name']}")
    print("-" * 90)
    print(f"Text: {scenario['text']}")
    print(
        f"Category: {result.get('category')} | {result.get('category_label_fa')} | score={result.get('category_score')}"
    )
    print(
        f"Intent: {result.get('intent')} | {result.get('intent_label_fa')} | score={result.get('intent_score')}"
    )
    print(f"Urgency: {result.get('urgency_level')} | score={result.get('urgency_score')}")
    print(f"Sentiment: {result.get('sentiment')} | frustration={result.get('frustration_score')}")
    print(
        f"Confidence: {result.get('confidence')} | {result.get('confidence_percent')}% | {result.get('confidence_level')}"
    )
    print(f"Short summary: {result.get('short_summary')}")
    print(f"Suggested reply: {result.get('suggested_reply')}")
    print(f"Escalation: {result.get('escalation_hint')}")

    if evaluation["warnings"]:
        print("Warnings:")
        for warning in evaluation["warnings"]:
            print(f"  - {warning}")

    if evaluation["errors"]:
        print("Errors:")
        for error in evaluation["errors"]:
            print(f"  - {error}")

    print()


def run_single_tests() -> dict:
    start_time = time.time()
    results = []
    evaluations = []

    for scenario in SCENARIOS:
        result = analyze_ticket(
            text=scenario["text"],
            ticket_id=scenario["ticket_id"],
        )
        evaluation = evaluate_result(scenario, result)

        results.append(result)
        evaluations.append(
            {
                "ticket_id": scenario["ticket_id"],
                "name": scenario["name"],
                "passed": evaluation["passed"],
                "errors": evaluation["errors"],
                "warnings": evaluation["warnings"],
            }
        )

        print_case_report(scenario, result, evaluation)

    passed_count = sum(1 for item in evaluations if item["passed"])
    failed_count = len(evaluations) - passed_count
    warning_count = sum(len(item["warnings"]) for item in evaluations)

    return {
        "mode": "single",
        "total": len(evaluations),
        "passed": passed_count,
        "failed": failed_count,
        "warnings": warning_count,
        "duration_seconds": round(time.time() - start_time, 2),
        "evaluations": evaluations,
        "results": results,
    }


def run_batch_test() -> dict:
    batch_input = [
        {
            "ticket_id": scenario["ticket_id"],
            "text": scenario["text"],
        }
        for scenario in SCENARIOS
    ]

    start_time = time.time()
    batch_results = analyze_batch(batch_input)

    return {
        "mode": "batch",
        "total": len(batch_results),
        "completed": sum(1 for item in batch_results if item.get("analysis_status") == "completed"),
        "failed": sum(1 for item in batch_results if item.get("analysis_status") != "completed"),
        "duration_seconds": round(time.time() - start_time, 2),
        "results": batch_results,
    }


def save_report(report: dict, filename: str = "test_analyzer_results.json") -> Path:
    output_path = Path(__file__).resolve().parent / filename

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(report, file, ensure_ascii=False, indent=2)

    return output_path


def print_final_summary(single_report: dict, batch_report: dict, output_path: Path) -> None:
    print("=" * 90)
    print("FINAL TEST SUMMARY")
    print("=" * 90)
    print(f"Single tests total: {single_report['total']}")
    print(f"Single tests passed: {single_report['passed']}")
    print(f"Single tests failed: {single_report['failed']}")
    print(f"Single tests warnings: {single_report['warnings']}")
    print(f"Single tests duration: {single_report['duration_seconds']}s")
    print("-" * 90)
    print(f"Batch tests total: {batch_report['total']}")
    print(f"Batch tests completed: {batch_report['completed']}")
    print(f"Batch tests failed: {batch_report['failed']}")
    print(f"Batch tests duration: {batch_report['duration_seconds']}s")
    print("-" * 90)
    print(f"Report saved to: {output_path}")

    if single_report["failed"] == 0 and batch_report["failed"] == 0:
        print("Overall result: PASS")
    else:
        print("Overall result: FAIL")


def main() -> None:
    single_report = run_single_tests()
    batch_report = run_batch_test()

    full_report = {
        "single_report": single_report,
        "batch_report": batch_report,
    }

    output_path = save_report(full_report)
    print_final_summary(single_report, batch_report, output_path)


if __name__ == "__main__":
    main()
