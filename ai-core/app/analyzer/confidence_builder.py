import math

CONFIDENCE_LABELS_FA = {
    "very_high": "خیلی زیاد",
    "high": "زیاد",
    "medium": "متوسط",
    "low": "کم",
    "very_low": "خیلی کم",
}


CATEGORY_SOURCE_BASE = {
    "zero_shot_model": 1.0,
    "model_rule_agreement": 0.95,
    "rule_override": 0.80,
    "rule_fallback": 0.78,
    "rule_only_fallback": 0.65,
    "model_failed": 0.35,
    "model_unavailable": 0.30,
    "unknown": 0.15,
    "empty": 0.0,
}


def clamp_float(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    number = float(value)
    if not math.isfinite(number):
        return minimum
    return max(minimum, min(maximum, number))


def normalize_score(value, default: float = 0.0) -> float:
    try:
        score = float(value)
    except (TypeError, ValueError):
        return default

    if score > 1:
        score = score / 100

    return clamp_float(score)


def normalize_value(value: str) -> str:
    if not value:
        return ""

    return str(value).strip().lower()


def has_keyword_matches(value) -> bool:
    if not value:
        return False

    if isinstance(value, list):
        return len(value) > 0

    if isinstance(value, dict):
        for item in value.values():
            if isinstance(item, list) and item:
                return True
            if isinstance(item, str) and item.strip():
                return True

    return False


def get_confidence_level(confidence: float) -> str:
    if confidence >= 0.90:
        return "very_high"

    if confidence >= 0.75:
        return "high"

    if confidence >= 0.55:
        return "medium"

    if confidence >= 0.35:
        return "low"

    return "very_low"


def get_confidence_label_fa(level: str) -> str:
    return CONFIDENCE_LABELS_FA.get(level, level)


def calculate_category_confidence(category_result: dict) -> dict:
    if not category_result:
        return {
            "score": 0.0,
            "reason": "نتیجه category وجود ندارد.",
        }

    category = normalize_value(category_result.get("category", ""))
    category_score = normalize_score(category_result.get("category_score", 0.0))
    category_source = normalize_value(category_result.get("category_source", "unknown"))
    source_factor = CATEGORY_SOURCE_BASE.get(category_source, 0.50)

    if category in ["", "unknown"]:
        final_score = min(category_score, 0.20)
        reason = "category نامشخص است."
    else:
        final_score = category_score * source_factor

        if has_keyword_matches(category_result.get("matched_keywords")):
            final_score += 0.08

        if category_result.get("top_labels"):
            final_score += 0.04

        reason = f"category با منبع {category_source or 'unknown'} و امتیاز {category_score:.2f} محاسبه شد."

    return {
        "score": round(clamp_float(final_score), 2),
        "reason": reason,
    }


def calculate_intent_confidence(intent_result: dict) -> dict:
    if not intent_result:
        return {
            "score": 0.0,
            "reason": "نتیجه intent وجود ندارد.",
        }

    intent = normalize_value(intent_result.get("intent", ""))
    intent_score = normalize_score(intent_result.get("intent_score", 0.0))

    if intent in ["", "unknown_intent"]:
        return {
            "score": 0.10,
            "reason": "intent نامشخص است.",
        }

    if intent.startswith("general_"):
        return {
            "score": round(min(intent_score, 0.45), 2),
            "reason": "intent فقط به‌صورت عمومی تشخیص داده شده است.",
        }

    final_score = intent_score

    if has_keyword_matches(intent_result.get("matched_keywords")):
        final_score += 0.10

    return {
        "score": round(clamp_float(final_score), 2),
        "reason": f"intent با امتیاز {intent_score:.2f} محاسبه شد.",
    }


def calculate_urgency_confidence(urgency_result: dict) -> dict:
    if not urgency_result:
        return {
            "score": 0.0,
            "reason": "نتیجه urgency وجود ندارد.",
        }

    urgency_level = normalize_value(urgency_result.get("urgency_level", "unknown"))
    urgency_score = urgency_result.get("urgency_score", 0)
    reasons = urgency_result.get("urgency_reasons", [])

    if urgency_level in ["", "unknown"]:
        return {
            "score": 0.20,
            "reason": "سطح فوریت نامشخص است.",
        }

    final_score = 0.55

    if has_keyword_matches(urgency_result.get("matched_keywords")):
        final_score += 0.18

    if urgency_result.get("impact_patterns"):
        final_score += 0.12

    if isinstance(reasons, list) and reasons:
        final_score += 0.10

    try:
        numeric_urgency_score = int(float(urgency_score or 0))
    except (TypeError, ValueError):
        numeric_urgency_score = 0

    if urgency_level in ["critical", "high"] and numeric_urgency_score >= 65:
        final_score += 0.05

    return {
        "score": round(clamp_float(final_score), 2),
        "reason": f"urgency با سطح {urgency_level} و امتیاز {urgency_score} محاسبه شد.",
    }


def calculate_sentiment_confidence(sentiment_result: dict) -> dict:
    if not sentiment_result:
        return {
            "score": 0.0,
            "reason": "نتیجه sentiment وجود ندارد.",
        }

    sentiment = normalize_value(sentiment_result.get("sentiment", "unknown"))

    if sentiment in ["", "unknown"]:
        return {
            "score": 0.20,
            "reason": "sentiment نامشخص است.",
        }

    final_score = 0.55

    if sentiment == "neutral":
        final_score = 0.50

    if has_keyword_matches(sentiment_result.get("matched_keywords")):
        final_score += 0.20

    if sentiment_result.get("repetition_patterns"):
        final_score += 0.10

    if sentiment_result.get("sentiment_reasons"):
        final_score += 0.08

    return {
        "score": round(clamp_float(final_score), 2),
        "reason": f"sentiment با مقدار {sentiment} محاسبه شد.",
    }


def build_confidence_reasons(
    category_part: dict,
    intent_part: dict,
    urgency_part: dict,
    sentiment_part: dict,
    final_confidence: float,
) -> list:
    reasons = [
        category_part["reason"],
        intent_part["reason"],
        urgency_part["reason"],
        sentiment_part["reason"],
    ]

    if final_confidence >= 0.75:
        reasons.append("اطلاعات کافی برای اعتماد بالا به تحلیل وجود دارد.")
    elif final_confidence >= 0.55:
        reasons.append("تحلیل قابل قبول است اما بهتر است در صورت نیاز توسط کارشناس بررسی شود.")
    else:
        reasons.append("اطمینان تحلیل پایین است و بررسی انسانی پیشنهاد می‌شود.")

    return reasons


def build_confidence(
    category_result: dict = None,
    intent_result: dict = None,
    urgency_result: dict = None,
    sentiment_result: dict = None,
) -> dict:
    category_part = calculate_category_confidence(category_result or {})
    intent_part = calculate_intent_confidence(intent_result or {})
    urgency_part = calculate_urgency_confidence(urgency_result or {})
    sentiment_part = calculate_sentiment_confidence(sentiment_result or {})

    final_confidence = (
        category_part["score"] * 0.40
        + intent_part["score"] * 0.30
        + urgency_part["score"] * 0.15
        + sentiment_part["score"] * 0.15
    )

    if category_part["score"] < 0.30:
        final_confidence -= 0.10

    if intent_part["score"] < 0.30:
        final_confidence -= 0.05

    final_confidence = round(clamp_float(final_confidence), 2)
    confidence_level = get_confidence_level(final_confidence)

    return {
        "confidence": final_confidence,
        "confidence_percent": int(round(final_confidence * 100)),
        "confidence_level": confidence_level,
        "confidence_label_fa": get_confidence_label_fa(confidence_level),
        "confidence_factors": {
            "category_confidence": category_part["score"],
            "intent_confidence": intent_part["score"],
            "urgency_confidence": urgency_part["score"],
            "sentiment_confidence": sentiment_part["score"],
        },
        "confidence_reasons": build_confidence_reasons(
            category_part=category_part,
            intent_part=intent_part,
            urgency_part=urgency_part,
            sentiment_part=sentiment_part,
            final_confidence=final_confidence,
        ),
    }


def calculate_confidence(
    category_result: dict = None,
    intent_result: dict = None,
    urgency_result: dict = None,
    sentiment_result: dict = None,
) -> float:
    return build_confidence(
        category_result=category_result,
        intent_result=intent_result,
        urgency_result=urgency_result,
        sentiment_result=sentiment_result,
    )["confidence"]


if __name__ == "__main__":
    sample_category = {
        "category": "vpn",
        "category_score": 0.86,
        "category_source": "zero_shot_model",
        "top_labels": [
            {"category_en": "vpn", "score": 0.86},
            {"category_en": "network", "score": 0.31},
        ],
        "matched_keywords": [],
    }

    sample_intent = {
        "intent": "vpn_authentication_error",
        "intent_score": 0.85,
        "matched_keywords": ["authentication"],
    }

    sample_urgency = {
        "urgency_level": "high",
        "urgency_score": 80,
        "urgency_reasons": ["نشانه فوریت بالا در متن دیده شد."],
        "matched_keywords": {
            "critical": [],
            "high": ["جلسه"],
            "medium": [],
            "low": [],
        },
        "impact_patterns": [],
    }

    sample_sentiment = {
        "sentiment": "negative",
        "sentiment_score": 45,
        "sentiment_reasons": ["نشانه منفی مرتبط با مشکل دیده شد."],
        "matched_keywords": {
            "angry": [],
            "frustration": [],
            "negative": ["قطع"],
            "blocking": [],
            "positive": [],
        },
        "repetition_patterns": [],
    }

    print(
        build_confidence(
            category_result=sample_category,
            intent_result=sample_intent,
            urgency_result=sample_urgency,
            sentiment_result=sample_sentiment,
        )
    )
