import argparse
import json
import sys
from collections import Counter
from pathlib import Path

AI_CORE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(AI_CORE_ROOT))

from app.analyzer import analyze_ticket  # noqa: E402

URGENCY_ORDER = ["low", "medium", "high", "critical"]


def urgency_distance(expected: str, actual: str) -> int | None:
    try:
        return abs(URGENCY_ORDER.index(expected) - URGENCY_ORDER.index(actual))
    except ValueError:
        return None


def percent(value: int, total: int) -> str:
    return f"{(value / total * 100):.1f}%" if total else "0.0%"


def evaluate(dataset: list[dict]) -> dict:
    rows = []
    for item in dataset:
        result = analyze_ticket(item["text"], ticket_id=item["ticket_id"])
        category_ok = result.get("category") == item["expected_category"]
        intent_ok = category_ok and result.get("intent") == item["expected_intent"]
        distance = urgency_distance(item["expected_urgency"], result.get("urgency"))
        rows.append(
            {
                "ticket_id": item["ticket_id"],
                "expected_category": item["expected_category"],
                "actual_category": result.get("category"),
                "category_ok": category_ok,
                "expected_intent": item["expected_intent"],
                "actual_intent": result.get("intent"),
                "intent_ok": intent_ok,
                "expected_urgency": item["expected_urgency"],
                "actual_urgency": result.get("urgency"),
                "urgency_exact": distance == 0,
                "urgency_near": distance is not None and distance <= 1,
                "confidence": result.get("confidence"),
            }
        )

    total = len(rows)
    category_correct = sum(row["category_ok"] for row in rows)
    intent_correct = sum(row["intent_ok"] for row in rows)
    urgency_exact = sum(row["urgency_exact"] for row in rows)
    urgency_near = sum(row["urgency_near"] for row in rows)
    return {
        "total": total,
        "category_correct": category_correct,
        "intent_correct": intent_correct,
        "urgency_exact": urgency_exact,
        "urgency_near": urgency_near,
        "category_errors": Counter(
            f"{row['expected_category']} -> {row['actual_category']}"
            for row in rows
            if not row["category_ok"]
        ),
        "rows": rows,
    }


def build_markdown(report: dict) -> str:
    total = report["total"]
    lines = [
        "# AI Analyzer Quality Report",
        "",
        f"- Evaluation samples: {total}",
        f"- Category accuracy: {report['category_correct']}/{total} ({percent(report['category_correct'], total)})",
        f"- Intent accuracy: {report['intent_correct']}/{total} ({percent(report['intent_correct'], total)})",
        f"- Urgency exact match: {report['urgency_exact']}/{total} ({percent(report['urgency_exact'], total)})",
        f"- Urgency near match: {report['urgency_near']}/{total} ({percent(report['urgency_near'], total)})",
        "",
        "## Frequent category errors",
        "",
    ]
    if report["category_errors"]:
        lines.extend(
            f"- {name}: {count}" for name, count in report["category_errors"].most_common()
        )
    else:
        lines.append("- No category errors in this evaluation run.")

    lines.extend(["", "## Mismatched samples", ""])
    mismatches = [
        row
        for row in report["rows"]
        if not row["category_ok"] or not row["intent_ok"] or not row["urgency_near"]
    ]
    if mismatches:
        lines.extend(
            (
                f"- {row['ticket_id']}: category {row['expected_category']} -> "
                f"{row['actual_category']}; intent {row['expected_intent']} -> "
                f"{row['actual_intent']}; urgency {row['expected_urgency']} -> "
                f"{row['actual_urgency']}"
            )
            for row in mismatches
        )
    else:
        lines.append("- No mismatched samples.")

    lines.extend(
        [
            "",
            "## Calibration guidance",
            "",
            "Review wrong high-confidence predictions first. Keep category threshold changes category-specific and rerun this set after every rule or model update.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dataset",
        type=Path,
        default=AI_CORE_ROOT / "data/evaluation/analyzer_eval_set.json",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=AI_CORE_ROOT / "docs/ai_analyzer_quality_report.md",
    )
    args = parser.parse_args()

    dataset = json.loads(args.dataset.read_text(encoding="utf-8"))
    report = evaluate(dataset)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(build_markdown(report), encoding="utf-8")
    print(build_markdown(report))


if __name__ == "__main__":
    main()
