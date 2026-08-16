import re

from .normalizer import find_normalized_matches, normalize_persian_text

IMPACT_LABELS_FA = {
    "single_user": "یک کاربر",
    "team_level": "سطح تیم یا واحد",
    "organization_level": "سطح سازمان",
    "unknown": "نامشخص",
}

ORGANIZATION_PHRASES = [
    "کل شرکت",
    "کل سازمان",
    "تمام شرکت",
    "تمام سازمان",
    "همه کاربران",
    "هیچکس دسترسی ندارد",
    "هیچ کس دسترسی ندارد",
    "سراسری",
    "organization wide",
    "company wide",
    "all users",
]

TEAM_PHRASES = [
    "کل تیم",
    "همه تیم",
    "کل واحد",
    "همه واحد",
    "کل دپارتمان",
    "همه دپارتمان",
    "کل طبقه",
    "چند کاربر",
    "چند نفر",
    "چند سیستم",
    "several users",
    "multiple users",
    "whole team",
]

COUNT_PATTERN = re.compile(r"(?<!\w)([2-9]|[1-9][0-9]+)\s*(نفر|کاربر|سیستم|دستگاه)(?!\w)")


def analyze_impact(text: str) -> dict:
    """Estimate the affected scope with an explainable, deterministic rule set."""
    clean_text = normalize_persian_text(text)
    if not clean_text:
        return {
            "impact_label": "unknown",
            "impact_label_fa": IMPACT_LABELS_FA["unknown"],
            "impact_score": 0,
            "impact_reasons": ["متن تیکت خالی است و دامنه اثر مشخص نیست."],
            "matched_patterns": [],
        }

    organization_matches = find_normalized_matches(clean_text, ORGANIZATION_PHRASES)
    team_matches = find_normalized_matches(clean_text, TEAM_PHRASES)
    count_match = COUNT_PATTERN.search(clean_text)

    if organization_matches:
        label = "organization_level"
        score = 25
        matches = ["organization_scope", *organization_matches]
        reasons = ["متن نشان می‌دهد مشکل در سطح گسترده سازمانی رخ داده است."]
    elif team_matches or count_match:
        label = "team_level"
        score = 15
        matches = ["team_scope", *team_matches]
        if count_match:
            matches.append(f"affected_count:{count_match.group(1)}")
        reasons = ["متن نشان می‌دهد چند کاربر، سیستم یا یک بخش سازمان درگیر است."]
    else:
        label = "single_user"
        score = 0
        matches = []
        reasons = ["نشانه‌ای از درگیری چند کاربر دیده نشد؛ دامنه اثر یک کاربر در نظر گرفته شد."]

    return {
        "impact_label": label,
        "impact_label_fa": IMPACT_LABELS_FA[label],
        "impact_score": score,
        "impact_reasons": reasons,
        "matched_patterns": matches,
    }
