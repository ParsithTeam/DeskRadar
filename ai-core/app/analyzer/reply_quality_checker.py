from .normalizer import normalize_persian_text


def check_reply_quality(reply: str) -> dict:
    text = str(reply or "").strip()
    normalized = normalize_persian_text(text)
    issues: list[str] = []

    if len(text) < 50:
        issues.append("پاسخ بیش از حد کوتاه است.")
    if len(text) > 900:
        issues.append("پاسخ برای نمایش در رابط کاربری بیش از حد طولانی است.")
    if not text.startswith("سلام"):
        issues.append("پاسخ با سلام حرفه‌ای شروع نشده است.")
    if "لطفا" not in normalized:
        issues.append("اقدام یا درخواست بعدی به‌صورت شفاف بیان نشده است.")
    if not any(term in normalized for term in ("ارسال", "بررسی", "اعلام", "مشخص")):
        issues.append("گام بعدی قابل اقدام در پاسخ دیده نشد.")

    score = max(0, 100 - len(issues) * 20)
    return {
        "reply_quality_score": score,
        "reply_quality_passed": not issues,
        "reply_quality_issues": issues,
    }
