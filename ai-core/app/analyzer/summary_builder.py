import re

from .normalizer import normalize_persian_text

CATEGORY_SUMMARY_LABELS = {
    "vpn": "VPN",
    "email": "ایمیل",
    "network": "شبکه یا اینترنت",
    "printer": "پرینتر یا چاپ",
    "account": "حساب کاربری",
    "hardware": "سخت‌افزار",
    "software": "نرم‌افزار",
    "permission": "دسترسی به فایل یا پوشه",
    "unknown": "موضوع نامشخص",
}


INTENT_SUMMARY_TEMPLATES = {
    "vpn_request": "کاربر درخواست دسترسی یا ایجاد حساب VPN دارد.",
    "vpn_authentication_error": "کاربر در احراز هویت VPN مشکل دارد.",
    "vpn_connection_issue": "کاربر اعلام کرده اتصال VPN برقرار نمی‌شود یا قطع شده است.",
    "vpn_client_issue": "کاربر با نرم‌افزار یا کلاینت VPN مشکل دارد.",
    "email_quota_issue": "کاربر اعلام کرده فضای ایمیل یا صندوق پستی او پر شده است.",
    "email_access_issue": "کاربر برای ورود یا دسترسی به ایمیل مشکل دارد.",
    "email_send_receive_issue": "کاربر در ارسال یا دریافت ایمیل مشکل دارد.",
    "email_outlook_issue": "کاربر با Outlook یا همگام‌سازی ایمیل مشکل دارد.",
    "network_drop": "کاربر قطعی شبکه یا اینترنت را گزارش کرده است.",
    "network_speed": "کاربر کندی شبکه یا اینترنت را گزارش کرده است.",
    "network_wifi_issue": "کاربر با اتصال وای‌فای مشکل دارد.",
    "network_lan_issue": "کاربر با شبکه کابلی، IP، DNS یا اتصال LAN مشکل دارد.",
    "printer_error": "کاربر خطا یا خرابی پرینتر را گزارش کرده است.",
    "print_queue": "کاربر با صف چاپ یا انجام نشدن پرینت مشکل دارد.",
    "printer_supply_issue": "کاربر مشکل تونر، کارتریج یا کیفیت چاپ را گزارش کرده است.",
    "printer_setup_request": "کاربر درخواست نصب یا تعریف پرینتر دارد.",
    "account_lock": "کاربر با قفل شدن حساب یا فراموشی رمز عبور مواجه شده است.",
    "account_creation": "کاربر درخواست ایجاد حساب کاربری جدید دارد.",
    "account_access_issue": "کاربر برای ورود یا دسترسی به سامانه مشکل دارد.",
    "account_deactivation": "کاربر درخواست غیرفعال‌سازی یا حذف حساب کاربری دارد.",
    "hardware_failure": "کاربر خرابی یا روشن نشدن سخت‌افزار را گزارش کرده است.",
    "hardware_request": "کاربر درخواست تجهیزات سخت‌افزاری دارد.",
    "hardware_peripheral_issue": "کاربر با تجهیزات جانبی مانند موس، کیبورد یا هدست مشکل دارد.",
    "hardware_display_issue": "کاربر مشکل تصویر یا نمایشگر را گزارش کرده است.",
    "software_install": "کاربر درخواست نصب یا بروزرسانی نرم‌افزار دارد.",
    "software_error": "کاربر خطا، کرش یا اجرا نشدن نرم‌افزار را گزارش کرده است.",
    "software_license_issue": "کاربر با لایسنس یا فعال‌سازی نرم‌افزار مشکل دارد.",
    "software_access_request": "کاربر درخواست دسترسی به نرم‌افزار دارد.",
    "permission_denied": "کاربر با خطای عدم دسترسی مواجه شده است.",
    "permission_request": "کاربر درخواست مجوز یا دسترسی جدید دارد.",
    "shared_folder_issue": "کاربر با فایل، پوشه یا مسیر اشتراکی مشکل دارد.",
    "permission_remove_access": "کاربر درخواست حذف یا قطع دسترسی دارد.",
}


URGENCY_SUMMARY_TEXT = {
    "critical": "این تیکت از نظر فوریت بحرانی است.",
    "high": "این تیکت فوریت بالایی دارد.",
    "medium": "این تیکت فوریت متوسط دارد.",
    "low": "این تیکت فوریت پایینی دارد.",
    "unknown": "فوریت تیکت مشخص نیست.",
}


SENTIMENT_SUMMARY_TEXT = {
    "angry": "لحن کاربر عصبانی یا بسیار ناراضی است.",
    "frustrated": "لحن کاربر ناراضی یا پیگیرانه است.",
    "negative": "لحن کاربر منفی است.",
    "neutral": "لحن کاربر خنثی است.",
    "positive": "لحن کاربر محترمانه یا مثبت است.",
    "unknown": "لحن کاربر مشخص نیست.",
}


NOISE_PHRASES = [
    "سلام",
    "با سلام",
    "سلام وقت بخیر",
    "وقت بخیر",
    "خسته نباشید",
    "لطفا",
    "لطفاً",
    "ممنون",
    "متشکرم",
    "تشکر",
    "سپاس",
    "با تشکر",
]


def normalize_value(value: str) -> str:
    if not value:
        return ""

    return str(value).strip().lower()


def clean_original_text(text: str) -> str:
    if not text:
        return ""

    clean_text = str(text).strip()

    for phrase in sorted(NOISE_PHRASES, key=len, reverse=True):
        clean_text = re.sub(
            rf"^\s*{re.escape(phrase)}(?:\s*[،,:؛;!-]+)?\s*",
            "",
            clean_text,
            count=1,
            flags=re.IGNORECASE,
        )

    clean_text = " ".join(clean_text.split())
    clean_text = clean_text.strip(" ،,.؛;:!?؟")

    return clean_text


def truncate_text(text: str, max_chars: int = 160) -> str:
    if not text:
        return ""

    text = " ".join(str(text).split())

    if len(text) <= max_chars:
        return text

    truncated = text[:max_chars].rsplit(" ", 1)[0].rstrip()
    return (truncated or text[:max_chars].rstrip()) + "..."


def get_category_summary_label(category: str) -> str:
    category_code = normalize_value(category)
    return CATEGORY_SUMMARY_LABELS.get(category_code, CATEGORY_SUMMARY_LABELS["unknown"])


def get_intent_summary(intent: str, category: str = "") -> str:
    intent_code = normalize_value(intent)

    if intent_code in INTENT_SUMMARY_TEMPLATES:
        return INTENT_SUMMARY_TEMPLATES[intent_code]

    category_label = get_category_summary_label(category)

    if category_label != CATEGORY_SUMMARY_LABELS["unknown"]:
        return f"کاربر مشکلی مرتبط با {category_label} را گزارش کرده است."

    return "کاربر یک مشکل سرویس‌دسک را گزارش کرده است."


def get_urgency_summary(urgency_level: str) -> str:
    urgency_code = normalize_value(urgency_level)
    return URGENCY_SUMMARY_TEXT.get(urgency_code, "")


def get_sentiment_summary(sentiment: str) -> str:
    sentiment_code = normalize_value(sentiment)
    return SENTIMENT_SUMMARY_TEXT.get(sentiment_code, "")


def extract_key_text(text: str, max_chars: int = 120) -> str:
    cleaned_original = clean_original_text(text)

    if cleaned_original:
        return truncate_text(cleaned_original, max_chars=max_chars)

    normalized = normalize_persian_text(text)
    return truncate_text(normalized, max_chars=max_chars)


def build_summary(
    text: str,
    category: str = "",
    intent: str = "",
    urgency_level: str = "",
    sentiment: str = "",
) -> dict:
    clean_text = normalize_persian_text(text)

    if not clean_text:
        return {
            "summary": "متن تیکت خالی است و خلاصه‌ای قابل تولید نیست.",
            "short_summary": "متن تیکت خالی است.",
            "summary_parts": [],
        }

    intent_summary = get_intent_summary(intent, category)
    urgency_summary = get_urgency_summary(urgency_level)
    sentiment_summary = get_sentiment_summary(sentiment)
    key_text = extract_key_text(text)

    summary_parts = [intent_summary]

    if urgency_summary:
        summary_parts.append(urgency_summary)

    if sentiment_summary and sentiment not in ["", "unknown"]:
        summary_parts.append(sentiment_summary)

    if key_text:
        summary_parts.append(f"متن کاربر: «{key_text}»")

    summary = " ".join(summary_parts)
    short_summary = intent_summary

    return {
        "summary": summary,
        "short_summary": short_summary,
        "summary_parts": summary_parts,
    }


def create_summary(
    text: str,
    category: str = "",
    intent: str = "",
    urgency_level: str = "",
    sentiment: str = "",
) -> str:
    return build_summary(
        text=text,
        category=category,
        intent=intent,
        urgency_level=urgency_level,
        sentiment=sentiment,
    )["summary"]

