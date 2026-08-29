REPLY_TONE_LABELS_FA = {
    "standard": "عادی",
    "formal": "رسمی",
    "urgent": "فوری",
    "empathetic": "همدلانه",
    "empathetic_urgent": "همدلانه و فوری",
}


def select_reply_tone(
    sentiment: str = "",
    urgency_level: str = "",
    category: str = "",
) -> dict:
    sentiment_code = str(sentiment or "").strip().lower()
    urgency_code = str(urgency_level or "").strip().lower()
    category_code = str(category or "").strip().lower()

    needs_empathy = sentiment_code in {"angry", "frustrated"}
    is_urgent = urgency_code in {"critical", "high"}

    if needs_empathy and is_urgent:
        tone = "empathetic_urgent"
    elif needs_empathy:
        tone = "empathetic"
    elif is_urgent:
        tone = "urgent"
    elif category_code in {"account", "permission"}:
        tone = "formal"
    else:
        tone = "standard"

    return {
        "reply_tone": tone,
        "reply_tone_label_fa": REPLY_TONE_LABELS_FA[tone],
    }
