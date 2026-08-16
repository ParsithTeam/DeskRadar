from .intent_config import (
    GENERAL_INTENT_TEMPLATE,
    INTENT_LABELS_FA,
    INTENT_RULES,
    UNKNOWN_INTENT,
)
from .normalizer import find_normalized_matches, normalize_persian_text

INTENT_SPECIFICITY_BOOSTS = {
    "vpn_authentication_error": 0.16,
    "email_quota_issue": 0.10,
    "account_lock": 0.10,
    "software_license_issue": 0.10,
    "printer_supply_issue": 0.08,
    "print_queue": 0.08,
    "network_wifi_issue": 0.10,
    "network_lan_issue": 0.10,
    "hardware_peripheral_issue": 0.10,
    "hardware_request": 0.15,
    "permission_remove_access": 0.25,
    "permission_denied": 0.08,
}


def normalize_category(category: str) -> str:
    if not category:
        return ""

    return str(category).strip().lower()


def normalize_keyword(keyword: str) -> str:
    return normalize_persian_text(str(keyword))


def get_general_intent(category: str) -> str:
    category_code = normalize_category(category)

    if not category_code or category_code == "unknown":
        return UNKNOWN_INTENT

    return GENERAL_INTENT_TEMPLATE.format(category=category_code)


def get_intent_label_fa(intent: str) -> str:
    return INTENT_LABELS_FA.get(intent, intent)


def find_keyword_matches(text: str, keywords: list) -> list:
    return find_normalized_matches(text, keywords)


def analyze_intent(text: str, category: str) -> dict:
    clean_text = normalize_persian_text(text)
    category_code = normalize_category(category)

    if not clean_text:
        return {
            "intent": UNKNOWN_INTENT,
            "intent_label_fa": get_intent_label_fa(UNKNOWN_INTENT),
            "intent_score": 0.0,
            "matched_keywords": [],
            "reason": "متن تیکت خالی است.",
        }

    if not category_code or category_code == "unknown":
        return {
            "intent": UNKNOWN_INTENT,
            "intent_label_fa": get_intent_label_fa(UNKNOWN_INTENT),
            "intent_score": 0.0,
            "matched_keywords": [],
            "reason": "دسته‌بندی تیکت مشخص نیست.",
        }

    category_rules = INTENT_RULES.get(category_code)

    if not category_rules:
        general_intent = get_general_intent(category_code)

        return {
            "intent": general_intent,
            "intent_label_fa": get_intent_label_fa(general_intent),
            "intent_score": 0.3,
            "matched_keywords": [],
            "reason": "برای این دسته‌بندی قانون intent تعریف نشده است.",
        }

    best_intent = None
    best_matches = []
    best_score = 0.0

    for intent, keywords in category_rules.items():
        matches = find_keyword_matches(clean_text, keywords)

        if not matches:
            continue

        score = min(
            1.0,
            0.55 + (len(matches) * 0.15) + INTENT_SPECIFICITY_BOOSTS.get(intent, 0.0),
        )

        if score > best_score:
            best_intent = intent
            best_matches = matches
            best_score = score

    if best_intent:
        return {
            "intent": best_intent,
            "intent_label_fa": get_intent_label_fa(best_intent),
            "intent_score": round(best_score, 2),
            "matched_keywords": best_matches,
            "reason": f"intent با کلمات کلیدی {', '.join(best_matches)} تشخیص داده شد.",
        }

    general_intent = get_general_intent(category_code)

    return {
        "intent": general_intent,
        "intent_label_fa": get_intent_label_fa(general_intent),
        "intent_score": 0.4,
        "matched_keywords": [],
        "reason": "هیچ کلمه کلیدی مشخصی برای intent پیدا نشد.",
    }


def detect_intent(text: str, category: str) -> str:
    return analyze_intent(text, category)["intent"]


if __name__ == "__main__":
    tickets = [
        {
            "text": "سلام وی پی ان من قطع شده و ارور میده",
            "category": "vpn",
        },
        {
            "text": "لطفا فضا یا حجم ایمیل من رو ارتقا بدید",
            "category": "email",
        },
        {
            "text": "تیکت نمونه بدون هیچ کلمه خاصی",
            "category": "network",
        },
    ]

    for ticket in tickets:
        print(analyze_intent(ticket["text"], ticket["category"]))
