from .normalizer import normalize_persian_text

QUESTIONS_BY_CATEGORY = {
    "vpn": "لطفاً متن خطا، نام کلاینت VPN و زمان شروع مشکل را اعلام کنید.",
    "email": "لطفاً مشخص کنید مشکل مربوط به ورود، ارسال، دریافت یا حجم صندوق پستی است.",
    "network": "لطفاً محل، نوع اتصال و تعداد کاربران درگیر را اعلام کنید.",
    "printer": "لطفاً نام پرینتر، محل آن و پیام خطای نمایش‌داده‌شده را ارسال کنید.",
    "account": "لطفاً نام سامانه، نام کاربری و پیام خطای ورود را اعلام کنید.",
    "hardware": "لطفاً نوع دستگاه، شماره اموال و نشانه خرابی را اعلام کنید.",
    "software": "لطفاً نام و نسخه نرم‌افزار و متن خطا را ارسال کنید.",
    "permission": "لطفاً مسیر منبع، نام کاربری و نوع دسترسی موردنیاز را اعلام کنید.",
    "unknown": "لطفاً نام سرویس، شرح دقیق مشکل، زمان شروع و متن خطا را ارسال کنید.",
}


def detect_ambiguity(
    text: str,
    category: str = "",
    intent: str = "",
    confidence: float = 0.0,
) -> dict:
    clean_text = normalize_persian_text(text)
    category_code = str(category or "unknown").strip().lower()
    intent_code = str(intent or "unknown_intent").strip().lower()
    token_count = len(clean_text.split())

    reasons: list[str] = []
    if token_count < 4:
        reasons.append("متن تیکت بسیار کوتاه است.")
    if category_code in {"", "unknown"}:
        reasons.append("دسته‌بندی تیکت مشخص نیست.")
    if intent_code in {"", "unknown_intent"} or intent_code.startswith("general_"):
        reasons.append("هدف دقیق تیکت مشخص نیست.")
    if float(confidence or 0.0) < 0.55:
        reasons.append("اطمینان تحلیل پایین‌تر از حد قابل اتکا است.")

    needs_more_info = bool(reasons)
    question = QUESTIONS_BY_CATEGORY.get(category_code, QUESTIONS_BY_CATEGORY["unknown"])
    return {
        "needs_more_info": needs_more_info,
        "clarification_question_fa": question if needs_more_info else None,
        "ambiguity_reasons": reasons,
    }
