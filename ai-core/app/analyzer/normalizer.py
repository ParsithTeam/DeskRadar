import re
import unicodedata
from collections.abc import Iterable

CHARACTER_REPLACEMENTS = {
    "ي": "ی",
    "ى": "ی",
    "ك": "ک",
    "ة": "ه",
    "ۀ": "ه",
    "ؤ": "و",
    "أ": "ا",
    "إ": "ا",
    "ٱ": "ا",
    "\u200c": " ",
    "\u200f": " ",
    "\u200e": " ",
}


PERSIAN_DIGITS = "۰۱۲۳۴۵۶۷۸۹"
ARABIC_DIGITS = "٠١٢٣٤٥٦٧٨٩"
ENGLISH_DIGITS = "0123456789"


PHRASE_REPLACEMENTS = {
    r"\bوی\s*پی\s*ان\b": "vpn",
    r"\bفیلتر\s*شکن\b": "vpn",
    r"\bوی\s*پی\s*ان\s*ها\b": "vpn",
    r"\bvpn\b": "vpn",
    r"\bوی\s*فای\b": "wifi",
    r"\bوای\s*فای\b": "wifi",
    r"\bwi\s*fi\b": "wifi",
    r"\bwifi\b": "wifi",
    r"\bاینترنت\b": "internet",
    r"\bنت\b": "internet",
    r"\bایمیل\b": "email",
    r"\bای\s*میل\b": "email",
    r"\bپست\s*الکترونیک\b": "email",
    r"\bاوتلوک\b": "outlook",
    r"\boutlook\b": "outlook",
    r"\bرمز\s*عبور\b": "password",
    r"\bکلمه\s*عبور\b": "password",
    r"\bپسورد\b": "password",
    r"\bرمز\b": "password",
    r"\bپرینتر\b": "printer",
    r"\bچاپگر\b": "printer",
    r"\bپرینت\b": "print",
    r"\bچاپ\b": "print",
    r"\bلپ\s*تاپ\b": "laptop",
    r"\bنوت\s*بوک\b": "laptop",
    r"\bمانیتور\b": "monitor",
    r"\bنمایشگر\b": "monitor",
    r"\bموس\b": "mouse",
    r"\bماوس\b": "mouse",
    r"\bکیبورد\b": "keyboard",
    r"\bصفحه\s*کلید\b": "keyboard",
    r"\bفولدر\b": "folder",
    r"\bپوشه\b": "folder",
    r"\bفایل\b": "file",
    r"\bنرم\s*افزار\b": "software",
    r"\bسخت\s*افزار\b": "hardware",
    r"\bاکانت\b": "account",
    r"\bحساب\s*کاربری\b": "account",
    r"\bکاربر\b": "user",
    r"\bلاگین\b": "login",
    r"\bورود\b": "login",
    r"\bدسترسی\b": "access",
    r"\bمجوز\b": "permission",
    r"\bارور\b": "error",
    r"\bخطا\b": "error",
    r"\bآپدیت\b": "update",
    r"\bبروزرسانی\b": "update",
    r"\bبه\s*روزرسانی\b": "update",
    r"\bاحراز\s*هویت\b": "authentication",
    r"\bتایید\b": "تأیید",
}


def replace_characters(text: str) -> str:
    for old_char, new_char in CHARACTER_REPLACEMENTS.items():
        text = text.replace(old_char, new_char)

    return text


def remove_diacritics(text: str) -> str:
    return "".join(char for char in text if unicodedata.category(char) != "Mn")


def normalize_digits(text: str) -> str:
    translation_table = str.maketrans(
        PERSIAN_DIGITS + ARABIC_DIGITS,
        ENGLISH_DIGITS + ENGLISH_DIGITS,
    )

    return text.translate(translation_table)


def normalize_punctuation(text: str) -> str:
    text = re.sub(r"[ـ]+", "", text)
    text = re.sub(r"[-_/\\|]+", " ", text)
    text = re.sub(r"[،؛:؛؟!?,;()\[\]{}<>\"'`~@#$%^&*=+]+", " ", text)
    text = re.sub(r"[.]+", " ", text)

    return text


def apply_phrase_replacements(text: str) -> str:
    for pattern, replacement in PHRASE_REPLACEMENTS.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    return text


def collapse_spaces(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def normalize_persian_text(text: str) -> str:
    if text is None:
        return ""

    text = str(text)
    text = replace_characters(text)
    text = remove_diacritics(text)
    text = normalize_digits(text)
    text = text.lower()
    text = normalize_punctuation(text)
    text = collapse_spaces(text)
    text = apply_phrase_replacements(text)
    text = collapse_spaces(text)

    return text


def contains_normalized_phrase(text: str, phrase: str) -> bool:
    """Return whether a normalized phrase exists as complete token(s).

    Plain substring checks create false positives for short rules such as ``ip``
    or ``رمز``. Both values are normalized here and token boundaries are enforced
    while still allowing flexible whitespace inside multi-word phrases.
    """
    clean_text = normalize_persian_text(text)
    clean_phrase = normalize_persian_text(phrase)

    if not clean_text or not clean_phrase:
        return False

    pattern = re.escape(clean_phrase).replace(r"\ ", r"\s+")
    return re.search(rf"(?<!\w){pattern}(?!\w)", clean_text) is not None


def find_normalized_matches(text: str, phrases: Iterable[str]) -> list[str]:
    """Return unique normalized rules that match *text*, preserving rule order."""
    clean_text = normalize_persian_text(text)
    matches: list[str] = []
    seen: set[str] = set()

    for phrase in phrases:
        clean_phrase = normalize_persian_text(phrase)
        if (
            clean_phrase
            and clean_phrase not in seen
            and contains_normalized_phrase(clean_text, clean_phrase)
        ):
            matches.append(clean_phrase)
            seen.add(clean_phrase)

    return matches

