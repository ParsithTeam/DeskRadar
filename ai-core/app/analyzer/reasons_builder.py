def normalize_value(value: str) -> str:
    if not value:
        return ""

    return str(value).strip().lower()


def add_reason(reasons: list, reason: str) -> None:
    if not reason:
        return

    clean_reason = str(reason).strip()

    if clean_reason and clean_reason not in reasons:
        reasons.append(clean_reason)


def add_reasons(reasons: list, new_reasons) -> None:
    if not new_reasons:
        return

    if isinstance(new_reasons, str):
        add_reason(reasons, new_reasons)
        return

    if isinstance(new_reasons, list):
        for reason in new_reasons:
            add_reason(reasons, reason)


def build_category_reasons(category_result: dict) -> list:
    reasons = []

    if not category_result:
        return ["نتیجه دسته‌بندی category در دسترس نیست."]

    category = normalize_value(category_result.get("category", ""))
    category_label = category_result.get("category_label_fa", "")
    category_score = category_result.get("category_score", 0)
    category_source = category_result.get("category_source", "unknown")
    matched_keywords = category_result.get("matched_keywords", [])
    top_labels = category_result.get("top_labels", [])

    if category and category != "unknown":
        add_reason(
            reasons,
            f"دسته‌بندی تیکت به‌عنوان {category_label or category} تشخیص داده شد.",
        )
    else:
        add_reason(reasons, "دسته‌بندی تیکت با اطمینان کافی تشخیص داده نشد.")

    add_reason(
        reasons,
        f"منبع تشخیص category برابر {category_source} و امتیاز آن {category_score} است.",
    )

    if matched_keywords:
        add_reason(
            reasons,
            f"کلمات کلیدی مؤثر در تشخیص category: {', '.join(matched_keywords)}",
        )

    if top_labels:
        top_text = []
        for item in top_labels[:3]:
            label = item.get("category_label_fa") or item.get("category_en")
            score = item.get("score")
            top_text.append(f"{label}: {score}")

        if top_text:
            add_reason(
                reasons,
                f"سه دسته‌بندی احتمالی برتر: {', '.join(top_text)}",
            )

    add_reason(reasons, category_result.get("reason", ""))

    return reasons


def build_intent_reasons(intent_result: dict) -> list:
    reasons = []

    if not intent_result:
        return ["نتیجه intent در دسترس نیست."]

    intent = normalize_value(intent_result.get("intent", ""))
    intent_label = intent_result.get("intent_label_fa", "")
    intent_score = intent_result.get("intent_score", 0)
    matched_keywords = intent_result.get("matched_keywords", [])

    if intent and intent != "unknown_intent":
        add_reason(
            reasons,
            f"هدف تیکت به‌عنوان {intent_label or intent} تشخیص داده شد.",
        )
    else:
        add_reason(reasons, "هدف دقیق تیکت تشخیص داده نشد.")

    add_reason(reasons, f"امتیاز intent برابر {intent_score} است.")

    if matched_keywords:
        add_reason(
            reasons,
            f"کلمات کلیدی مؤثر در تشخیص intent: {', '.join(matched_keywords)}",
        )

    add_reason(reasons, intent_result.get("reason", ""))

    return reasons


def build_urgency_reasons(urgency_result: dict) -> list:
    reasons = []

    if not urgency_result:
        return ["نتیجه urgency در دسترس نیست."]

    urgency_level = normalize_value(urgency_result.get("urgency_level", "unknown"))
    urgency_label = urgency_result.get("urgency_label_fa", "")
    urgency_score = urgency_result.get("urgency_score", 0)
    urgency_reasons = urgency_result.get("urgency_reasons", [])
    impact_patterns = urgency_result.get("impact_patterns", [])

    if urgency_level and urgency_level != "unknown":
        add_reason(
            reasons,
            f"سطح فوریت تیکت {urgency_label or urgency_level} تشخیص داده شد.",
        )
    else:
        add_reason(reasons, "سطح فوریت تیکت مشخص نیست.")

    add_reason(reasons, f"امتیاز فوریت برابر {urgency_score} از 100 است.")
    add_reasons(reasons, urgency_reasons)

    if impact_patterns:
        add_reason(
            reasons,
            f"الگوهای اثرگذاری تشخیص داده‌شده: {', '.join(impact_patterns)}",
        )

    return reasons


def build_sentiment_reasons(sentiment_result: dict) -> list:
    reasons = []

    if not sentiment_result:
        return ["نتیجه sentiment در دسترس نیست."]

    sentiment = normalize_value(sentiment_result.get("sentiment", "unknown"))
    sentiment_label = sentiment_result.get("sentiment_label_fa", "")
    frustration_level = sentiment_result.get("frustration_level", "none")
    frustration_label = sentiment_result.get("frustration_level_fa", "")
    frustration_score = sentiment_result.get("frustration_score", 0)
    sentiment_reasons = sentiment_result.get("sentiment_reasons", [])
    repetition_patterns = sentiment_result.get("repetition_patterns", [])

    if sentiment and sentiment != "unknown":
        add_reason(
            reasons,
            f"لحن کاربر {sentiment_label or sentiment} تشخیص داده شد.",
        )
    else:
        add_reason(reasons, "لحن کاربر با اطمینان کافی تشخیص داده نشد.")

    add_reason(
        reasons,
        f"سطح نارضایتی {frustration_label or frustration_level} و امتیاز آن {frustration_score} از 100 است.",
    )

    add_reasons(reasons, sentiment_reasons)

    if repetition_patterns:
        add_reason(reasons, "در متن نشانه‌هایی از تکرار یا پیگیری مجدد مشکل دیده شد.")

    return reasons


def build_confidence_reasons(confidence_result: dict) -> list:
    reasons = []

    if not confidence_result:
        return ["نتیجه confidence در دسترس نیست."]

    confidence = confidence_result.get("confidence", 0)
    confidence_percent = confidence_result.get("confidence_percent", 0)
    confidence_level = confidence_result.get("confidence_level", "")
    confidence_label = confidence_result.get("confidence_label_fa", "")
    confidence_reasons = confidence_result.get("confidence_reasons", [])
    confidence_factors = confidence_result.get("confidence_factors", {})

    add_reason(
        reasons,
        f"اطمینان نهایی تحلیل {confidence_percent}% و سطح آن {confidence_label or confidence_level} است.",
    )

    if confidence_factors:
        category_conf = confidence_factors.get("category_confidence")
        intent_conf = confidence_factors.get("intent_confidence")
        urgency_conf = confidence_factors.get("urgency_confidence")
        sentiment_conf = confidence_factors.get("sentiment_confidence")

        add_reason(
            reasons,
            (
                "عوامل confidence شامل "
                f"category={category_conf}, intent={intent_conf}, "
                f"urgency={urgency_conf}, sentiment={sentiment_conf} هستند."
            ),
        )

    add_reasons(reasons, confidence_reasons)

    if confidence < 0.55:
        add_reason(reasons, "به دلیل confidence پایین، بررسی انسانی پیشنهاد می‌شود.")

    return reasons


def build_reply_reasons(reply_result: dict) -> list:
    reasons = []

    if not reply_result:
        return []

    reply_title = reply_result.get("reply_title", "")
    escalation_hint = reply_result.get("escalation_hint", "")
    required_info = reply_result.get("required_info", [])

    if reply_title:
        add_reason(reasons, f"پاسخ پیشنهادی براساس قالب «{reply_title}» ساخته شد.")

    if required_info:
        add_reason(
            reasons,
            f"اطلاعات تکمیلی موردنیاز از کاربر: {', '.join(required_info)}",
        )

    if escalation_hint:
        add_reason(reasons, escalation_hint)

    return reasons


def build_escalation_reasons(escalation_result: dict) -> list:
    if not escalation_result:
        return []

    reason = escalation_result.get("escalation_reason_fa")
    if not reason:
        return []
    return [reason]


def build_ambiguity_reasons(ambiguity_result: dict) -> list:
    if not ambiguity_result or not ambiguity_result.get("needs_more_info"):
        return []

    reasons = list(ambiguity_result.get("ambiguity_reasons", []))
    question = ambiguity_result.get("clarification_question_fa")
    if question:
        reasons.append(f"سؤال تکمیلی پیشنهادی: {question}")
    return reasons


def build_final_reasons(
    category_result: dict = None,
    intent_result: dict = None,
    urgency_result: dict = None,
    sentiment_result: dict = None,
    confidence_result: dict = None,
    reply_result: dict = None,
    escalation_result: dict = None,
    ambiguity_result: dict = None,
    max_reasons: int = 18,
) -> dict:
    all_reasons = []

    add_reasons(all_reasons, build_category_reasons(category_result or {}))
    add_reasons(all_reasons, build_intent_reasons(intent_result or {}))
    add_reasons(all_reasons, build_urgency_reasons(urgency_result or {}))
    add_reasons(all_reasons, build_sentiment_reasons(sentiment_result or {}))
    add_reasons(all_reasons, build_escalation_reasons(escalation_result or {}))
    add_reasons(all_reasons, build_ambiguity_reasons(ambiguity_result or {}))
    add_reasons(all_reasons, build_confidence_reasons(confidence_result or {}))
    add_reasons(all_reasons, build_reply_reasons(reply_result or {}))

    limited_reasons = all_reasons[:max_reasons]

    return {
        "reasons": limited_reasons,
        "reason_count": len(limited_reasons),
        "all_reason_count": len(all_reasons),
        "has_more_reasons": len(all_reasons) > max_reasons,
    }


def create_reasons(
    category_result: dict = None,
    intent_result: dict = None,
    urgency_result: dict = None,
    sentiment_result: dict = None,
    confidence_result: dict = None,
    reply_result: dict = None,
    escalation_result: dict = None,
    ambiguity_result: dict = None,
) -> list:
    return build_final_reasons(
        category_result=category_result,
        intent_result=intent_result,
        urgency_result=urgency_result,
        sentiment_result=sentiment_result,
        confidence_result=confidence_result,
        reply_result=reply_result,
        escalation_result=escalation_result,
        ambiguity_result=ambiguity_result,
    )["reasons"]


if __name__ == "__main__":
    sample_category = {
        "category": "vpn",
        "category_label_fa": "اتصال VPN و شبکه راه دور",
        "category_score": 0.86,
        "category_source": "zero_shot_model",
        "top_labels": [
            {"category_en": "vpn", "category_label_fa": "اتصال VPN و شبکه راه دور", "score": 0.86},
            {"category_en": "network", "category_label_fa": "قطعی اینترنت و وای‌فای", "score": 0.31},
        ],
        "matched_keywords": [],
        "reason": "دسته‌بندی با مدل zero-shot انجام شد.",
    }

    sample_intent = {
        "intent": "vpn_authentication_error",
        "intent_label_fa": "خطای احراز هویت VPN",
        "intent_score": 0.85,
        "matched_keywords": ["authentication"],
        "reason": "intent با کلمات کلیدی authentication تشخیص داده شد.",
    }

    sample_urgency = {
        "urgency_level": "high",
        "urgency_label_fa": "زیاد",
        "urgency_score": 80,
        "urgency_reasons": [
            "نشانه‌های فوریت بالا در متن دیده شد: جلسه",
        ],
        "impact_patterns": [],
    }

    sample_sentiment = {
        "sentiment": "negative",
        "sentiment_label_fa": "منفی",
        "frustration_level": "medium",
        "frustration_level_fa": "متوسط",
        "frustration_score": 45,
        "sentiment_reasons": [
            "نشانه‌های منفی مرتبط با مشکل دیده شد: قطع",
        ],
        "repetition_patterns": [],
    }

    sample_confidence = {
        "confidence": 0.82,
        "confidence_percent": 82,
        "confidence_level": "high",
        "confidence_label_fa": "زیاد",
        "confidence_factors": {
            "category_confidence": 0.90,
            "intent_confidence": 0.95,
            "urgency_confidence": 0.80,
            "sentiment_confidence": 0.70,
        },
        "confidence_reasons": [
            "اطلاعات کافی برای اعتماد بالا به تحلیل وجود دارد.",
        ],
    }

    sample_reply = {
        "reply_title": "خطای احراز هویت VPN",
        "required_info": [
            "تصویر خطای احراز هویت",
            "نام کاربری",
            "زمان رخ دادن مشکل",
        ],
        "escalation_hint": "در صورت عدم رفع سریع، ارجاع به تیم تخصصی پیشنهاد می‌شود.",
    }

    print(
        build_final_reasons(
            category_result=sample_category,
            intent_result=sample_intent,
            urgency_result=sample_urgency,
            sentiment_result=sample_sentiment,
            confidence_result=sample_confidence,
            reply_result=sample_reply,
        )
    )
