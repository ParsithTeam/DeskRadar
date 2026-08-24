import logging
import threading

from . import config
from .normalizer import find_normalized_matches, normalize_persian_text

logger = logging.getLogger(__name__)

CATEGORY_FALLBACK_THRESHOLD = getattr(config, "CATEGORY_FALLBACK_THRESHOLD", 0.55)
CATEGORY_MAP = config.CATEGORY_MAP
CATEGORY_LABELS_FA = config.CATEGORY_LABELS_FA
CATEGORY_THRESHOLD = getattr(config, "CATEGORY_THRESHOLD", 0.70)
CATEGORY_KEYWORDS = getattr(config, "CATEGORY_KEYWORDS", {})
CATEGORY_LABEL_BY_CODE = getattr(config, "CATEGORY_LABEL_BY_CODE", {})
CATEGORY_TOP_K = getattr(config, "CATEGORY_TOP_K", 3)
UNKNOWN_CATEGORY = getattr(config, "UNKNOWN_CATEGORY", "unknown")
MODEL_NAME = getattr(
    config,
    "ZERO_SHOT_MODEL_NAME",
    "MoritzLaurer/multilingual-MiniLMv2-L6-mnli-xnli",
)
HYPOTHESIS_TEMPLATE = getattr(
    config,
    "ZERO_SHOT_HYPOTHESIS_TEMPLATE",
    "موضوع این تیکت مربوط به {} است.",
)

MODEL_STRONG_CONFIDENCE = 0.90
RULE_OVERRIDE_MODEL_LIMIT = 0.85

STRONG_CATEGORY_KEYWORDS = {
    "vpn": {"vpn", "remote access", "anyconnect", "forticlient", "openvpn"},
    "email": {"email", "outlook", "mailbox"},
    "network": {"internet", "wifi", "lan", "ssid", "ethernet", "dns", "dhcp"},
    "printer": {"printer", "print", "تونر", "کارتریج"},
    "account": {"account", "password", "login", "حساب", "پورتال"},
    "hardware": {"hardware", "laptop", "monitor", "هارد", "هدست", "وبکم"},
    "software": {"software", "برنامه", "اپلیکیشن", "لایسنس", "activation", "crm"},
    "permission": {"access", "permission", "file", "folder"},
}

DOMINANT_CATEGORY_KEYWORDS = {
    "vpn": {"vpn", "remote access", "anyconnect", "forticlient", "openvpn"},
    "email": {"email", "outlook", "mailbox"},
    "network": {"internet", "wifi", "lan", "ssid", "ethernet"},
    "printer": {"printer"},
    "account": {"account", "password", "login", "پورتال"},
    "hardware": {"hardware", "laptop", "monitor", "هارد"},
    "software": {"software", "اپلیکیشن", "لایسنس", "crm"},
    "permission": {"access denied", "permission denied", "shared folder"},
}

_classifier = None
_classifier_lock = threading.Lock()
_inference_lock = threading.Lock()


def get_classifier():
    global _classifier

    if _classifier is None:
        with _classifier_lock:
            if _classifier is None:
                try:
                    from transformers import pipeline
                except ImportError as exc:
                    raise RuntimeError("کتابخانه‌های لازم برای مدل zero-shot نصب نیستند.") from exc

                _classifier = pipeline(
                    "zero-shot-classification",
                    model=MODEL_NAME,
                )

    return _classifier


def preload_classifier() -> bool:
    """Load the classifier once during application startup."""
    get_classifier()
    return True


def is_classifier_loaded() -> bool:
    return _classifier is not None


def get_category_label_fa(category_code: str) -> str:
    return CATEGORY_LABEL_BY_CODE.get(category_code, category_code)


def normalize_score(score) -> float:
    try:
        return round(float(score), 2)
    except (TypeError, ValueError):
        return 0.0


def build_empty_result(reason: str = "متن تیکت خالی است.") -> dict:
    return {
        "category": UNKNOWN_CATEGORY,
        "category_label_fa": get_category_label_fa(UNKNOWN_CATEGORY),
        "category_score": 0.0,
        "category_source": "empty",
        "top_labels": [],
        "matched_keywords": [],
        "reason": reason,
        "model_name": MODEL_NAME,
    }


def build_top_labels(labels: list, scores: list) -> list:
    top_labels = []

    for label, score in zip(labels[:CATEGORY_TOP_K], scores[:CATEGORY_TOP_K], strict=False):
        category_code = CATEGORY_MAP.get(label, UNKNOWN_CATEGORY)

        top_labels.append(
            {
                "category_en": category_code,
                "category_label_fa": get_category_label_fa(category_code),
                "score": normalize_score(score),
            }
        )

    return top_labels


def find_keyword_category(clean_text: str) -> dict:
    best_category = UNKNOWN_CATEGORY
    best_matches = []
    best_score = 0.0

    for category_code, keywords in CATEGORY_KEYWORDS.items():
        matches = find_normalized_matches(clean_text, keywords)

        if not matches:
            continue

        score = 0.55 + (len(matches) * 0.10)
        if any(match in STRONG_CATEGORY_KEYWORDS.get(category_code, set()) for match in matches):
            score += 0.20
        if any(match in DOMINANT_CATEGORY_KEYWORDS.get(category_code, set()) for match in matches):
            score += 0.15
        score = min(1.0, score)

        if score > best_score or (score == best_score and len(matches) > len(best_matches)):
            best_category = category_code
            best_matches = matches
            best_score = score

    return {
        "category": best_category,
        "score": round(best_score, 2),
        "matched_keywords": best_matches,
    }


def classify_with_model(clean_text: str) -> dict:
    classifier = get_classifier()

    with _inference_lock:
        result = classifier(
            clean_text,
            candidate_labels=CATEGORY_LABELS_FA,
            hypothesis_template=HYPOTHESIS_TEMPLATE,
            multi_label=False,
        )

    labels = result.get("labels", [])
    scores = result.get("scores", [])

    if not labels or not scores:
        return build_empty_result("مدل zero-shot خروجی معتبری تولید نکرد.")

    best_label = labels[0]
    best_score = normalize_score(scores[0])
    category_code = CATEGORY_MAP.get(best_label, UNKNOWN_CATEGORY)

    return {
        "category": category_code,
        "category_label_fa": get_category_label_fa(category_code),
        "category_score": best_score,
        "category_source": "zero_shot_model",
        "top_labels": build_top_labels(labels, scores),
        "matched_keywords": [],
        "reason": "دسته‌بندی با مدل zero-shot انجام شد.",
        "model_name": MODEL_NAME,
    }


def build_rule_result(
    keyword_result: dict,
    category_source: str,
    reason: str,
    top_labels: list = None,
) -> dict:
    category_code = keyword_result.get("category", UNKNOWN_CATEGORY)
    keyword_score = keyword_result.get("score", 0.0)

    return {
        "category": category_code,
        "category_label_fa": get_category_label_fa(category_code),
        "category_score": keyword_score,
        "category_source": category_source,
        "top_labels": top_labels or [],
        "matched_keywords": keyword_result.get("matched_keywords", []),
        "reason": reason,
        "model_name": MODEL_NAME,
    }


def apply_rule_fallback(clean_text: str, model_result: dict) -> dict:
    model_result = dict(model_result)
    keyword_result = find_keyword_category(clean_text)

    model_category = model_result.get("category", UNKNOWN_CATEGORY)
    model_score = normalize_score(model_result.get("category_score", 0.0))
    keyword_category = keyword_result.get("category", UNKNOWN_CATEGORY)
    keyword_score = normalize_score(keyword_result.get("score", 0.0))
    top_labels = model_result.get("top_labels", [])

    if keyword_category == UNKNOWN_CATEGORY:
        if model_category != UNKNOWN_CATEGORY and model_score >= CATEGORY_THRESHOLD:
            return model_result

        model_result["category"] = UNKNOWN_CATEGORY
        model_result["category_label_fa"] = get_category_label_fa(UNKNOWN_CATEGORY)
        model_result["category_source"] = "unknown"
        model_result["matched_keywords"] = []
        model_result["reason"] = (
            "امتیاز مدل پایین بود و قانون fallback هم دسته‌بندی معتبری پیدا نکرد."
        )

        return model_result

    if model_category == UNKNOWN_CATEGORY:
        if keyword_score >= CATEGORY_FALLBACK_THRESHOLD:
            return build_rule_result(
                keyword_result=keyword_result,
                category_source="rule_fallback",
                reason="به دلیل نامشخص بودن خروجی مدل، دسته‌بندی با rule fallback انجام شد.",
                top_labels=top_labels,
            )

        return build_empty_result("مدل و rule fallback دسته‌بندی معتبری پیدا نکردند.")

    if keyword_score >= 0.85 and keyword_category != model_category:
        return build_rule_result(
            keyword_result=keyword_result,
            category_source="rule_override",
            reason="عبارت صریح دامنه IT از پیشنهاد مدل دقیق‌تر بود و دسته‌بندی را اصلاح کرد.",
            top_labels=top_labels,
        )

    if keyword_category == model_category:
        model_result["matched_keywords"] = keyword_result.get("matched_keywords", [])

        if model_score < CATEGORY_THRESHOLD and keyword_score >= CATEGORY_FALLBACK_THRESHOLD:
            model_result["category_score"] = max(model_score, keyword_score)
            model_result["category_source"] = "model_rule_agreement"
            model_result["reason"] = "مدل و rule fallback روی یک دسته‌بندی توافق داشتند."

        return model_result

    if keyword_score >= CATEGORY_FALLBACK_THRESHOLD and model_score < RULE_OVERRIDE_MODEL_LIMIT:
        return build_rule_result(
            keyword_result=keyword_result,
            category_source="rule_override",
            reason="مدل zero-shot دسته‌بندی متفاوتی پیشنهاد داد، اما keyword rule قوی‌تر بود و category اصلاح شد.",
            top_labels=top_labels,
        )

    if model_score >= MODEL_STRONG_CONFIDENCE:
        return model_result

    if keyword_score >= CATEGORY_FALLBACK_THRESHOLD:
        return build_rule_result(
            keyword_result=keyword_result,
            category_source="rule_override",
            reason="به دلیل تعارض مدل و keyword rule، دسته‌بندی براساس rule قابل اعتمادتر اصلاح شد.",
            top_labels=top_labels,
        )

    return model_result


def classify_category(text: str, debug: bool = False) -> dict:
    clean_text = normalize_persian_text(text)

    if not clean_text:
        return build_empty_result()

    keyword_result = find_keyword_category(clean_text)

    try:
        model_result = classify_with_model(clean_text)
    except Exception as error:
        logger.warning("Zero-shot classification unavailable; using rules: %s", error)
        if (
            keyword_result.get("category") != UNKNOWN_CATEGORY
            and keyword_result.get("score", 0.0) >= CATEGORY_FALLBACK_THRESHOLD
        ):
            result = build_rule_result(
                keyword_result=keyword_result,
                category_source="rule_only_fallback",
                reason="مدل zero-shot در دسترس نبود و دسته‌بندی با rule fallback انجام شد.",
                top_labels=[],
            )
            if debug:
                result["debug"] = {
                    "model_error_type": type(error).__name__,
                    "model_error": str(error),
                }
            return result

        result = {
            "category": UNKNOWN_CATEGORY,
            "category_label_fa": get_category_label_fa(UNKNOWN_CATEGORY),
            "category_score": 0.0,
            "category_source": "model_failed",
            "top_labels": [],
            "matched_keywords": [],
            "reason": "مدل zero-shot در دسترس نبود و rule fallback هم نتیجه معتبری نداشت.",
            "model_name": MODEL_NAME,
        }
        if debug:
            result["debug"] = {
                "model_error_type": type(error).__name__,
                "model_error": str(error),
            }
        return result

    return apply_rule_fallback(clean_text, model_result)


if __name__ == "__main__":
    samples = [
        "سلام، وی پی ان من وصل نمیشه و احراز هویت خطا میده",
        "حجم ایمیل من پر شده و پیام جدید دریافت نمیکنم",
        "کل شرکت اینترنت ندارد و همه کاربران مشکل دارند",
        "پرینتر اتاق مالی چاپ نمیکنه",
        "رمز سامانه را فراموش کردم و وارد حساب کاربری نمیشم",
    ]

    for sample in samples:
        print(classify_category(sample))
