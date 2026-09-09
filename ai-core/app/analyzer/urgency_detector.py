from .impact_detector import analyze_impact
from .normalizer import find_normalized_matches, normalize_persian_text

URGENCY_LABELS_FA = {
    "critical": "بحرانی",
    "high": "زیاد",
    "medium": "متوسط",
    "low": "کم",
    "unknown": "نامشخص",
}


CRITICAL_KEYWORDS = [
    "بحرانی",
    "قطعی کامل",
    "از کار افتاده",
    "کل شرکت",
    "کل سازمان",
    "کل واحد",
    "همه کاربران",
    "همه سیستم ها",
    "همه سیستم‌ها",
    "همه کاربرها",
    "هیچکس دسترسی ندارد",
    "هیچ کس دسترسی ندارد",
    "incident",
    "outage",
    "system down",
    "network down",
    "internet down",
    "production down",
    "major incident",
    "security incident",
    "data leak",
    "breach",
    "هک",
    "نشت اطلاعات",
    "رخداد امنیتی",
]


HIGH_KEYWORDS = [
    "فوری",
    "اضطراری",
    "خیلی مهم",
    "الان",
    "همین الان",
    "سریع",
    "سریعا",
    "سریعاً",
    "asap",
    "urgent",
    "immediately",
    "جلسه",
    "جلسه دارم",
    "نیم ساعت",
    "یک ساعت",
    "تا یک ساعت",
    "امروز",
    "تا امروز",
    "ددلاین",
    "deadline",
    "ارائه",
    "تحویل",
    "کارم متوقف شده",
    "کارم خوابیده",
    "کار نمی توانم انجام بدهم",
    "نمی توانم کار کنم",
    "نمی تونم کار کنم",
    "نمیتونم کار کنم",
    "دسترسی ندارم",
    "access ندارم",
    "وصل نمیشه",
    "وصل نمی شود",
    "قطع",
    "قطع شده",
    "down",
    "blocked",
    "متوقف شده",
    "کاملا متوقف",
    "کاملاً متوقف",
]


MEDIUM_KEYWORDS = [
    "پیگیری",
    "لطفا پیگیری",
    "نیاز دارم",
    "مشکل دارم",
    "اختلال",
    "کند",
    "کندی",
    "تکرار شده",
    "چند بار",
    "چندین بار",
    "تا آخر وقت",
    "تا پایان روز",
    "امکان پذیر نیست",
    "درگیرم",
    "کارم عقب افتاده",
    "slow",
    "issue",
    "problem",
    "delay",
    "repeated",
    "هنوز",
    "جواب نمیده",
    "پاسخ نمیده",
    "رسیدگی نشده",
    "درست نشده",
    "حل نشده",
    "نمی تونم",
    "نمیتونم",
    "نمی توانم",
    "نمی‌توانم",
    "نمی شود",
    "نمی‌شود",
    "کار نمی کند",
    "کار نمیکنه",
]


LOW_KEYWORDS = [
    "فوری نیست",
    "ضروری نیست",
    "عجله نیست",
    "اولویت پایین",
    "کم اهمیت",
    "هر وقت",
    "هر زمان",
    "فرصت داشتید",
    "در فرصت مناسب",
    "بعدا",
    "بعداً",
    "فعلا مهم نیست",
    "not urgent",
    "low priority",
    "when possible",
    "no rush",
]


CATEGORY_BOOSTS = {
    "network": 6,
    "vpn": 5,
    "account": 5,
    "permission": 5,
    "email": 4,
    "software": 3,
    "hardware": 3,
    "printer": 2,
}


INTENT_BOOSTS = {
    "network_drop": 15,
    "vpn_connection_issue": 12,
    "vpn_authentication_error": 10,
    "account_lock": 12,
    "account_access_issue": 10,
    "permission_denied": 8,
    "permission_request": 6,
    "shared_folder_issue": 6,
    "email_access_issue": 8,
    "email_send_receive_issue": 8,
    "email_quota_issue": 8,
    "hardware_failure": 10,
    "hardware_display_issue": 7,
    "software_error": 5,
    "software_license_issue": 5,
    "printer_error": 4,
    "print_queue": 3,
}


SENTIMENT_BOOSTS = {
    "angry": 10,
    "frustrated": 6,
    "negative": 3,
}


def normalize_value(value: str) -> str:
    if not value:
        return ""

    return str(value).strip().lower()


def get_urgency_label_fa(level: str) -> str:
    return URGENCY_LABELS_FA.get(level, level)


def get_urgency_level(score: int) -> str:
    if score >= 85:
        return "critical"

    if score >= 65:
        return "high"

    if score >= 40:
        return "medium"

    return "low"


def clamp_score(score: int) -> int:
    return max(0, min(100, int(score)))


def is_inside_excluded_phrase(keyword: str, excluded_phrases: list) -> bool:
    return any(keyword and phrase and keyword in phrase for phrase in excluded_phrases)


def find_keyword_matches(text: str, keywords: list, excluded_phrases: list = None) -> list:
    excluded_phrases = excluded_phrases or []
    return [
        match
        for match in find_normalized_matches(text, keywords)
        if not is_inside_excluded_phrase(match, excluded_phrases)
    ]


def detect_impact(clean_text: str) -> dict:
    return analyze_impact(clean_text)


def build_reasons(
    critical_matches: list,
    high_matches: list,
    medium_matches: list,
    low_matches: list,
    category: str,
    intent: str,
    impact_result: dict,
    sentiment: str = "",
) -> list:
    reasons = []

    if critical_matches:
        reasons.append(f"نشانه‌های بحرانی در متن دیده شد: {', '.join(critical_matches)}")

    if high_matches:
        reasons.append(f"نشانه‌های فوریت بالا در متن دیده شد: {', '.join(high_matches)}")

    if medium_matches:
        reasons.append(f"نشانه‌های فوریت متوسط در متن دیده شد: {', '.join(medium_matches)}")

    if low_matches:
        reasons.append(f"عبارت‌های کاهش‌دهنده فوریت در متن دیده شد: {', '.join(low_matches)}")

    if category in CATEGORY_BOOSTS:
        reasons.append(f"دسته‌بندی {category} روی امتیاز فوریت اثر گذاشت.")

    if intent in INTENT_BOOSTS:
        reasons.append(f"intent تشخیص‌داده‌شده ({intent}) امتیاز فوریت را افزایش داد.")

    if sentiment in SENTIMENT_BOOSTS:
        reasons.append(f"لحن {sentiment} کاربر امتیاز فوریت را افزایش داد.")

    reasons.extend(impact_result["impact_reasons"])

    if not reasons:
        reasons.append("نشانه مشخصی برای فوریت بالا در متن پیدا نشد.")

    return reasons


def analyze_urgency(
    text: str,
    category: str = "",
    intent: str = "",
    sentiment: str = "",
) -> dict:
    clean_text = normalize_persian_text(text)
    category_code = normalize_value(category)
    intent_code = normalize_value(intent)
    sentiment_code = normalize_value(sentiment)

    if not clean_text:
        return {
            "urgency_level": "unknown",
            "urgency_label_fa": get_urgency_label_fa("unknown"),
            "urgency_score": 0,
            "urgency_reasons": ["متن تیکت خالی است."],
            "matched_keywords": {
                "critical": [],
                "high": [],
                "medium": [],
                "low": [],
            },
            "impact_patterns": [],
            "impact_label": "unknown",
            "impact_label_fa": "نامشخص",
            "score_breakdown": {},
        }

    low_matches = find_keyword_matches(clean_text, LOW_KEYWORDS)
    critical_matches = find_keyword_matches(clean_text, CRITICAL_KEYWORDS)
    high_matches = find_keyword_matches(
        clean_text,
        HIGH_KEYWORDS,
        excluded_phrases=low_matches,
    )
    medium_matches = find_keyword_matches(clean_text, MEDIUM_KEYWORDS)
    impact_result = detect_impact(clean_text)

    score_breakdown = {
        "base": 25,
        "critical_keywords": min(len(critical_matches) * 25, 45),
        "high_keywords": min(len(high_matches) * 15, 35),
        "medium_keywords": min(len(medium_matches) * 8, 20),
        "low_priority_reduction": -min(len(low_matches) * 25, 35),
        "category_boost": CATEGORY_BOOSTS.get(category_code, 0),
        "intent_boost": INTENT_BOOSTS.get(intent_code, 0),
        "impact_boost": impact_result["impact_score"],
        "sentiment_boost": SENTIMENT_BOOSTS.get(sentiment_code, 0),
    }
    score = sum(score_breakdown.values())

    if low_matches and not critical_matches and impact_result["impact_score"] < 20:
        score = min(score, 35)

    if critical_matches and impact_result["impact_score"] >= 18:
        score = max(score, 90)

    if intent_code == "network_drop" and impact_result["impact_score"] >= 18:
        score = max(score, 90)

    if intent_code in ["account_lock", "hardware_failure"] and not low_matches:
        score = max(score, 40)

    score = clamp_score(score)
    level = get_urgency_level(score)

    reasons = build_reasons(
        critical_matches=critical_matches,
        high_matches=high_matches,
        medium_matches=medium_matches,
        low_matches=low_matches,
        category=category_code,
        intent=intent_code,
        impact_result=impact_result,
        sentiment=sentiment_code,
    )

    return {
        "urgency_level": level,
        "urgency_label_fa": get_urgency_label_fa(level),
        "urgency_score": score,
        "urgency_reasons": reasons,
        "matched_keywords": {
            "critical": critical_matches,
            "high": high_matches,
            "medium": medium_matches,
            "low": low_matches,
        },
        "impact_patterns": impact_result["matched_patterns"],
        "impact_label": impact_result["impact_label"],
        "impact_label_fa": impact_result["impact_label_fa"],
        "score_breakdown": {**score_breakdown, "final_score": score},
    }


def detect_urgency(
    text: str,
    category: str = "",
    intent: str = "",
    sentiment: str = "",
) -> dict:
    return analyze_urgency(text, category, intent, sentiment)

