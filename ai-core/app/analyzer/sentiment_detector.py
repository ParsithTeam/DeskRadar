import re

from .normalizer import find_normalized_matches, normalize_persian_text

SENTIMENT_LABELS_FA = {
    "positive": "مثبت",
    "neutral": "خنثی",
    "negative": "منفی",
    "frustrated": "ناراضی",
    "angry": "عصبانی",
    "unknown": "نامشخص",
}


FRUSTRATION_LEVELS_FA = {
    "none": "بدون ناراحتی",
    "low": "کم",
    "medium": "متوسط",
    "high": "زیاد",
    "critical": "خیلی زیاد",
}


ANGRY_KEYWORDS = [
    "عصبانی",
    "اعصاب",
    "خسته شدم",
    "دیگه خسته شدم",
    "واقعا خسته شدم",
    "واقعا دیگه",
    "افتضاح",
    "خیلی بد",
    "بی مسئولیتی",
    "بی‌مسئولیتی",
    "جوابگو نیستید",
    "angry",
    "mad",
    "terrible",
    "awful",
    "unacceptable",
    "very bad",
]


FRUSTRATION_KEYWORDS = [
    "چند بار",
    "چندین بار",
    "بارها",
    "دوباره",
    "باز هم",
    "بازم",
    "هنوز",
    "هنوز درست نشده",
    "قبلا اعلام کردم",
    "قبلاً اعلام کردم",
    "پیگیری نکردید",
    "رسیدگی نشده",
    "حل نشده",
    "مشکل تکرار شده",
    "هر روز",
    "مدام",
    "مداوم",
    "کلافه",
    "معطل",
    "منتظر",
    "repeated",
    "again",
    "still",
    "not fixed",
    "not resolved",
    "no response",
    "waiting",
    "کسی جواب نمیده",
    "کسی پاسخ نمیده",
]


NEGATIVE_KEYWORDS = [
    "مشکل",
    "خراب",
    "قطع",
    "error",
    "باز نمیشه",
    "باز نمی شود",
    "وصل نمیشه",
    "وصل نمی شود",
    "کار نمیکنه",
    "کار نمی کند",
    "اجرا نمیشه",
    "اجرا نمی شود",
    "دریافت نمیکنم",
    "دریافت نمی کنم",
    "ارسال نمیشه",
    "ارسال نمی شود",
    "access ندارم",
    "login نمیشه",
    "login نمی شود",
    "کند",
    "کندی",
    "اختلال",
    "ناموفق",
    "failed",
    "failure",
    "problem",
    "issue",
    "broken",
    "down",
    "slow",
    "denied",
]


BLOCKING_KEYWORDS = [
    "نمی توانم کار کنم",
    "نمیتوانم کار کنم",
    "نمی تونم کار کنم",
    "نمیتونم کار کنم",
    "کارم متوقف شده",
    "کارم خوابیده",
    "کارم عقب افتاده",
    "دسترسی ندارم",
    "امکان کار ندارم",
    "blocked",
    "cannot work",
    "can't work",
    "unable to work",
]


POSITIVE_KEYWORDS = [
    "ممنون",
    "متشکرم",
    "تشکر",
    "سپاس",
    "لطفا",
    "لطفاً",
    "خواهش می کنم",
    "خواهش میکنم",
    "thanks",
    "thank you",
    "please",
]


URGENCY_SENTIMENT_BOOSTS = {
    "critical": 15,
    "high": 10,
    "medium": 5,
    "low": 0,
    "unknown": 0,
}


INTENT_SENTIMENT_BOOSTS = {
    "vpn_connection_issue": 5,
    "vpn_authentication_error": 5,
    "network_drop": 8,
    "account_lock": 6,
    "account_access_issue": 6,
    "permission_denied": 6,
    "email_access_issue": 4,
    "email_send_receive_issue": 4,
    "hardware_failure": 5,
    "software_error": 4,
    "printer_error": 3,
}


def normalize_value(value: str) -> str:
    if not value:
        return ""

    return str(value).strip().lower()


def get_sentiment_label_fa(sentiment: str) -> str:
    return SENTIMENT_LABELS_FA.get(sentiment, sentiment)


def get_frustration_level_fa(level: str) -> str:
    return FRUSTRATION_LEVELS_FA.get(level, level)


def clamp_score(score: int) -> int:
    return max(0, min(100, int(score)))


def find_keyword_matches(text: str, keywords: list) -> list:
    return find_normalized_matches(text, keywords)


def detect_repetition_pattern(clean_text: str) -> dict:
    patterns = [
        r"\b(چند|چندین)\s*بار\b",
        r"\b(دوباره|بازم|باز هم)\b",
        r"\b(هنوز|قبلا|قبلاً)\b",
        r"\b(هر روز|مدام|مداوم)\b",
        r"\b(still|again|repeated)\b",
    ]

    matched_patterns = []

    for pattern in patterns:
        if re.search(pattern, clean_text):
            matched_patterns.append(pattern)

    return {
        "has_repetition": bool(matched_patterns),
        "matched_patterns": matched_patterns,
    }


def get_sentiment_from_score(
    frustration_score: int,
    angry_matches: list,
    frustration_matches: list,
    negative_matches: list,
    positive_matches: list,
) -> str:
    if frustration_score >= 85 or angry_matches:
        return "angry"

    if frustration_score >= 60 or frustration_matches:
        return "frustrated"

    if frustration_score >= 35 or negative_matches:
        return "negative"

    if positive_matches:
        return "positive"

    return "neutral"


def get_frustration_level(score: int) -> str:
    if score >= 85:
        return "critical"

    if score >= 65:
        return "high"

    if score >= 40:
        return "medium"

    if score >= 15:
        return "low"

    return "none"


def build_sentiment_reasons(
    angry_matches: list,
    frustration_matches: list,
    negative_matches: list,
    blocking_matches: list,
    positive_matches: list,
    repetition_result: dict,
    urgency_level: str,
    intent: str,
) -> list:
    reasons = []

    if angry_matches:
        reasons.append(f"نشانه‌های عصبانیت در متن دیده شد: {', '.join(angry_matches)}")

    if frustration_matches:
        reasons.append(
            f"نشانه‌های نارضایتی یا پیگیری تکراری دیده شد: {', '.join(frustration_matches)}"
        )

    if negative_matches:
        reasons.append(f"نشانه‌های منفی مرتبط با مشکل دیده شد: {', '.join(negative_matches)}")

    if blocking_matches:
        reasons.append(f"متن نشان می‌دهد مشکل مانع انجام کار شده است: {', '.join(blocking_matches)}")

    if repetition_result["has_repetition"]:
        reasons.append("در متن نشانه تکرار یا حل‌نشدن مشکل دیده شد.")

    if urgency_level in URGENCY_SENTIMENT_BOOSTS and URGENCY_SENTIMENT_BOOSTS[urgency_level] > 0:
        reasons.append(f"سطح فوریت {urgency_level} باعث افزایش امتیاز ناراحتی شد.")

    if intent in INTENT_SENTIMENT_BOOSTS:
        reasons.append(f"intent تشخیص‌داده‌شده ({intent}) روی امتیاز ناراحتی اثر گذاشت.")

    if positive_matches and not reasons:
        reasons.append(f"لحن متن محترمانه یا مثبت است: {', '.join(positive_matches)}")

    if not reasons:
        reasons.append("نشانه مشخصی از ناراحتی یا عصبانیت در متن پیدا نشد.")

    return reasons


def analyze_sentiment(
    text: str,
    urgency_level: str = "",
    category: str = "",
    intent: str = "",
) -> dict:
    clean_text = normalize_persian_text(text)
    urgency_code = normalize_value(urgency_level)
    category_code = normalize_value(category)
    intent_code = normalize_value(intent)

    if not clean_text:
        return {
            "sentiment": "unknown",
            "sentiment_label_fa": get_sentiment_label_fa("unknown"),
            "sentiment_score": 0,
            "frustration_level": "none",
            "frustration_level_fa": get_frustration_level_fa("none"),
            "frustration_score": 0,
            "sentiment_reasons": ["متن تیکت خالی است."],
            "matched_keywords": {
                "angry": [],
                "frustration": [],
                "negative": [],
                "blocking": [],
                "positive": [],
            },
            "repetition_patterns": [],
            "score_breakdown": {},
        }

    angry_matches = find_keyword_matches(clean_text, ANGRY_KEYWORDS)
    frustration_matches = find_keyword_matches(clean_text, FRUSTRATION_KEYWORDS)
    negative_matches = find_keyword_matches(clean_text, NEGATIVE_KEYWORDS)
    blocking_matches = find_keyword_matches(clean_text, BLOCKING_KEYWORDS)
    positive_matches = find_keyword_matches(clean_text, POSITIVE_KEYWORDS)
    repetition_result = detect_repetition_pattern(clean_text)

    score_breakdown = {
        "base": 10,
        "angry_keywords": min(len(angry_matches) * 30, 50),
        "frustration_keywords": min(len(frustration_matches) * 18, 45),
        "negative_keywords": min(len(negative_matches) * 10, 30),
        "blocking_keywords": min(len(blocking_matches) * 15, 25),
        "repetition_boost": 15 if repetition_result["has_repetition"] else 0,
        "urgency_boost": URGENCY_SENTIMENT_BOOSTS.get(urgency_code, 0),
        "intent_boost": INTENT_SENTIMENT_BOOSTS.get(intent_code, 0),
        "courtesy_reduction": (
            -min(len(positive_matches) * 5, 10)
            if positive_matches and not angry_matches and not frustration_matches
            else 0
        ),
        "printer_context_reduction": (
            -3
            if category_code == "printer" and not angry_matches and not frustration_matches
            else 0
        ),
    }
    score = sum(score_breakdown.values())

    score = clamp_score(score)
    sentiment = get_sentiment_from_score(
        frustration_score=score,
        angry_matches=angry_matches,
        frustration_matches=frustration_matches,
        negative_matches=negative_matches,
        positive_matches=positive_matches,
    )
    frustration_level = get_frustration_level(score)

    reasons = build_sentiment_reasons(
        angry_matches=angry_matches,
        frustration_matches=frustration_matches,
        negative_matches=negative_matches,
        blocking_matches=blocking_matches,
        positive_matches=positive_matches,
        repetition_result=repetition_result,
        urgency_level=urgency_code,
        intent=intent_code,
    )

    return {
        "sentiment": sentiment,
        "sentiment_label_fa": get_sentiment_label_fa(sentiment),
        "sentiment_score": score,
        "frustration_level": frustration_level,
        "frustration_level_fa": get_frustration_level_fa(frustration_level),
        "frustration_score": score,
        "sentiment_reasons": reasons,
        "matched_keywords": {
            "angry": angry_matches,
            "frustration": frustration_matches,
            "negative": negative_matches,
            "blocking": blocking_matches,
            "positive": positive_matches,
        },
        "repetition_patterns": repetition_result["matched_patterns"],
        "score_breakdown": {**score_breakdown, "final_score": score},
    }


def detect_sentiment(
    text: str,
    urgency_level: str = "",
    category: str = "",
    intent: str = "",
) -> dict:
    return analyze_sentiment(text, urgency_level, category, intent)


if __name__ == "__main__":
    samples = [
        {
            "text": "لطفا بررسی کنید، vpn من وصل نمیشه",
            "urgency_level": "medium",
            "category": "vpn",
            "intent": "vpn_connection_issue",
        },
        {
            "text": "چند بار اعلام کردم هنوز ایمیل من درست نشده و کسی جواب نمیده",
            "urgency_level": "high",
            "category": "email",
            "intent": "email_access_issue",
        },
        {
            "text": "واقعا دیگه خسته شدم، کل روزه اینترنت قطع شده و نمی تونم کار کنم",
            "urgency_level": "critical",
            "category": "network",
            "intent": "network_drop",
        },
        {
            "text": "ممنون میشم هر وقت فرصت داشتید پرینتر اتاق من رو بررسی کنید",
            "urgency_level": "low",
            "category": "printer",
            "intent": "printer_error",
        },
    ]

    for sample in samples:
        print(
            detect_sentiment(
                sample["text"],
                sample["urgency_level"],
                sample["category"],
                sample["intent"],
            )
        )
