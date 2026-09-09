from .normalizer import find_normalized_matches, normalize_persian_text

SECURITY_KEYWORDS = [
    "هک",
    "نشت اطلاعات",
    "رخداد امنیتی",
    "دسترسی غیرمجاز",
    "بدافزار",
    "باج افزار",
    "phishing",
    "malware",
    "ransomware",
    "security incident",
    "data leak",
    "breach",
]


def detect_escalation(
    text: str,
    urgency_level: str = "",
    sentiment: str = "",
    impact_label: str = "",
) -> dict:
    clean_text = normalize_persian_text(text)
    urgency_code = str(urgency_level or "").strip().lower()
    sentiment_code = str(sentiment or "").strip().lower()
    impact_code = str(impact_label or "").strip().lower()
    security_matches = find_normalized_matches(clean_text, SECURITY_KEYWORDS)

    reasons: list[str] = []
    if security_matches:
        reasons.append(f"نشانه امنیتی در متن دیده شد: {', '.join(security_matches)}.")
    if urgency_code in {"critical", "high"}:
        reasons.append(f"سطح فوریت تیکت {urgency_code} است.")
    if impact_code == "organization_level":
        reasons.append("دامنه اثر تیکت در سطح سازمان تشخیص داده شد.")
    if sentiment_code in {"angry", "frustrated"} and urgency_code not in {"low", "unknown"}:
        reasons.append("لحن کاربر ناراضی است و نیاز به رسیدگی فعال دارد.")

    should_escalate = bool(reasons)
    return {
        "should_escalate": should_escalate,
        "escalation_reason_fa": (
            " ".join(reasons) if reasons else "نشانه‌ای برای ارجاع فوری به سطح بالاتر دیده نشد."
        ),
        "security_issue": bool(security_matches),
        "security_matches": security_matches,
    }
