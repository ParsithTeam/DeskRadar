import json
import logging
from collections.abc import Iterable
from datetime import datetime, timezone

from . import config
from .ambiguity_detector import detect_ambiguity
from .confidence_builder import build_confidence
from .escalation_detector import detect_escalation
from .intent_detector import analyze_intent
from .normalizer import normalize_persian_text
from .reasons_builder import build_final_reasons
from .reply_builder import build_reply
from .reply_quality_checker import check_reply_quality
from .sentiment_detector import detect_sentiment
from .summary_builder import build_summary
from .urgency_detector import detect_urgency
from .zero_shot_category import classify_category

logger = logging.getLogger(__name__)

ANALYZER_MODEL_VERSION = getattr(config, "ANALYZER_MODEL_VERSION", "ai-analyzer-fa-v1")


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def build_error_result(text: str, error: Exception, ticket_id: str | None = None) -> dict:
    logger.exception("Analyzer failed for ticket_id=%s", ticket_id)
    return {
        "ticket_id": ticket_id,
        "input_text": text,
        "normalized_text": normalize_persian_text(text),
        "analysis_status": "failed",
        "error_code": "analysis_failed",
        "error": "تحلیل تیکت به دلیل خطای داخلی تکمیل نشد.",
        "analyzer_model_version": ANALYZER_MODEL_VERSION,
        "model_version": ANALYZER_MODEL_VERSION,
        "analyzed_at": utc_now_iso(),
    }


def build_ui_labels(
    category_result: dict,
    urgency_result: dict,
    sentiment_result: dict,
    confidence_result: dict,
    escalation_result: dict,
    ambiguity_result: dict,
) -> dict:
    return {
        "category": category_result.get("category_label_fa") or "نامشخص",
        "urgency": urgency_result.get("urgency_label_fa") or "نامشخص",
        "sentiment": sentiment_result.get("sentiment_label_fa") or "نامشخص",
        "impact": urgency_result.get("impact_label_fa") or "نامشخص",
        "confidence": confidence_result.get("confidence_label_fa") or "نامشخص",
        "escalation": (
            "نیاز به ارجاع" if escalation_result.get("should_escalate") else "ارجاع فوری لازم نیست"
        ),
        "more_info": (
            "نیاز به اطلاعات بیشتر" if ambiguity_result.get("needs_more_info") else "اطلاعات کافی"
        ),
    }


def build_debug_payload(
    normalized_text: str,
    category_result: dict,
    intent_result: dict,
    urgency_result: dict,
    sentiment_result: dict,
    reply_result: dict,
) -> dict:
    return {
        "decision_trace": [
            {
                "stage": "normalization",
                "normalized_text": normalized_text,
            },
            {
                "stage": "category",
                "source": category_result.get("category_source"),
                "score": category_result.get("category_score"),
                "top_labels": category_result.get("top_labels", []),
                "matched_keywords": category_result.get("matched_keywords", []),
                "model_debug": category_result.get("debug"),
            },
            {
                "stage": "intent",
                "intent": intent_result.get("intent"),
                "score": intent_result.get("intent_score"),
                "matched_keywords": intent_result.get("matched_keywords", []),
            },
            {
                "stage": "urgency",
                "level": urgency_result.get("urgency_level"),
                "score": urgency_result.get("urgency_score"),
                "weights": urgency_result.get("score_breakdown", {}),
            },
            {
                "stage": "sentiment",
                "sentiment": sentiment_result.get("sentiment"),
                "score": sentiment_result.get("sentiment_score"),
                "weights": sentiment_result.get("score_breakdown", {}),
            },
            {
                "stage": "reply",
                "template": reply_result.get("reply_title"),
                "tone": reply_result.get("reply_tone"),
            },
        ]
    }


def flatten_analysis(
    *,
    ticket_id: str | None,
    text: str,
    normalized_text: str,
    category_result: dict,
    intent_result: dict,
    urgency_result: dict,
    sentiment_result: dict,
    summary_result: dict,
    reply_result: dict,
    confidence_result: dict,
    reasons_result: dict,
    escalation_result: dict,
    ambiguity_result: dict,
    reply_quality_result: dict,
    debug: bool,
) -> dict:
    summary = summary_result.get("summary")
    suggested_reply = reply_result.get("suggested_reply")
    reasons = reasons_result.get("reasons", [])
    ui_labels = build_ui_labels(
        category_result,
        urgency_result,
        sentiment_result,
        confidence_result,
        escalation_result,
        ambiguity_result,
    )

    result = {
        "ticket_id": ticket_id,
        "input_text": text,
        "normalized_text": normalized_text,
        "analysis_status": "completed",
        "category": category_result.get("category"),
        "category_label_fa": category_result.get("category_label_fa"),
        "category_score": category_result.get("category_score"),
        "category_source": category_result.get("category_source"),
        "intent": intent_result.get("intent"),
        "intent_label_fa": intent_result.get("intent_label_fa"),
        "intent_score": intent_result.get("intent_score"),
        "urgency": urgency_result.get("urgency_level"),
        "urgency_level": urgency_result.get("urgency_level"),
        "urgency_label_fa": urgency_result.get("urgency_label_fa"),
        "urgency_score": urgency_result.get("urgency_score"),
        "impact_label": urgency_result.get("impact_label"),
        "impact_label_fa": urgency_result.get("impact_label_fa"),
        "sentiment": sentiment_result.get("sentiment"),
        "sentiment_label_fa": sentiment_result.get("sentiment_label_fa"),
        "sentiment_score": sentiment_result.get("sentiment_score"),
        "frustration_level": sentiment_result.get("frustration_level"),
        "frustration_level_fa": sentiment_result.get("frustration_level_fa"),
        "frustration_score": sentiment_result.get("frustration_score"),
        "summary": summary,
        "summary_fa": summary,
        "short_summary": summary_result.get("short_summary"),
        "reply_title": reply_result.get("reply_title"),
        "suggested_reply": suggested_reply,
        "suggested_reply_fa": suggested_reply,
        "reply_tone": reply_result.get("reply_tone"),
        "reply_tone_label_fa": reply_result.get("reply_tone_label_fa"),
        "required_info": reply_result.get("required_info", []),
        "escalation_hint": reply_result.get("escalation_hint"),
        **escalation_result,
        **ambiguity_result,
        **reply_quality_result,
        "confidence": confidence_result.get("confidence"),
        "confidence_percent": confidence_result.get("confidence_percent"),
        "confidence_level": confidence_result.get("confidence_level"),
        "confidence_label_fa": confidence_result.get("confidence_label_fa"),
        "reasons": reasons,
        "reasons_fa": reasons,
        "ui_labels": ui_labels,
        "analyzer_model_version": ANALYZER_MODEL_VERSION,
        "model_version": ANALYZER_MODEL_VERSION,
        "analyzed_at": utc_now_iso(),
        "details": {
            "category_analysis": category_result,
            "intent_analysis": intent_result,
            "urgency_analysis": urgency_result,
            "sentiment_analysis": sentiment_result,
            "summary_analysis": summary_result,
            "reply_analysis": reply_result,
            "confidence_analysis": confidence_result,
            "reasons_analysis": reasons_result,
            "escalation_analysis": escalation_result,
            "ambiguity_analysis": ambiguity_result,
            "reply_quality_analysis": reply_quality_result,
        },
    }

    if debug:
        result["raw_ai_response"] = build_debug_payload(
            normalized_text,
            category_result,
            intent_result,
            urgency_result,
            sentiment_result,
            reply_result,
        )

    return result


def analyze_ticket(
    text: str,
    ticket_id: str | None = None,
    *,
    debug: bool = False,
) -> dict:
    text = "" if text is None else str(text)

    try:
        normalized_text = normalize_persian_text(text)
        category_result = classify_category(text, debug=debug)
        category = category_result.get("category", "unknown")

        intent_result = analyze_intent(text, category)
        intent = intent_result.get("intent", "unknown_intent")

        initial_urgency = detect_urgency(text, category, intent)
        initial_sentiment = detect_sentiment(
            text,
            initial_urgency.get("urgency_level", "unknown"),
            category,
            intent,
        )
        urgency_result = detect_urgency(
            text,
            category,
            intent,
            initial_sentiment.get("sentiment", "unknown"),
        )
        sentiment_result = detect_sentiment(
            text,
            urgency_result.get("urgency_level", "unknown"),
            category,
            intent,
        )

        summary_result = build_summary(
            text=text,
            category=category,
            intent=intent,
            urgency_level=urgency_result.get("urgency_level", "unknown"),
            sentiment=sentiment_result.get("sentiment", "unknown"),
        )
        reply_result = build_reply(
            text=text,
            category=category,
            intent=intent,
            urgency_level=urgency_result.get("urgency_level", "unknown"),
            sentiment=sentiment_result.get("sentiment", "unknown"),
        )
        confidence_result = build_confidence(
            category_result=category_result,
            intent_result=intent_result,
            urgency_result=urgency_result,
            sentiment_result=sentiment_result,
        )
        escalation_result = detect_escalation(
            text=text,
            urgency_level=urgency_result.get("urgency_level", "unknown"),
            sentiment=sentiment_result.get("sentiment", "unknown"),
            impact_label=urgency_result.get("impact_label", "unknown"),
        )
        ambiguity_result = detect_ambiguity(
            text=text,
            category=category,
            intent=intent,
            confidence=confidence_result.get("confidence", 0.0),
        )
        reply_quality_result = check_reply_quality(reply_result.get("suggested_reply", ""))
        reasons_result = build_final_reasons(
            category_result=category_result,
            intent_result=intent_result,
            urgency_result=urgency_result,
            sentiment_result=sentiment_result,
            confidence_result=confidence_result,
            reply_result=reply_result,
            escalation_result=escalation_result,
            ambiguity_result=ambiguity_result,
        )

        return flatten_analysis(
            ticket_id=ticket_id,
            text=text,
            normalized_text=normalized_text,
            category_result=category_result,
            intent_result=intent_result,
            urgency_result=urgency_result,
            sentiment_result=sentiment_result,
            summary_result=summary_result,
            reply_result=reply_result,
            confidence_result=confidence_result,
            reasons_result=reasons_result,
            escalation_result=escalation_result,
            ambiguity_result=ambiguity_result,
            reply_quality_result=reply_quality_result,
            debug=debug,
        )
    except Exception as error:  # Service boundary: return a stable failure envelope.
        return build_error_result(text=text, error=error, ticket_id=ticket_id)


def analyze_batch(tickets: Iterable) -> list[dict]:
    if tickets is None:
        return []
    if isinstance(tickets, (str, bytes, dict)):
        raise TypeError("tickets باید یک iterable از متن‌ها یا دیکشنری‌های تیکت باشد.")

    results: list[dict] = []
    for index, ticket in enumerate(tickets, start=1):
        if isinstance(ticket, dict):
            text = ticket.get("text", "")
            ticket_id = ticket.get("ticket_id", f"ticket-{index}")
            debug = bool(ticket.get("debug", False))
        else:
            text = ticket
            ticket_id = f"ticket-{index}"
            debug = False

        results.append(
            analyze_ticket(
                text=text,
                ticket_id=None if ticket_id is None else str(ticket_id),
                debug=debug,
            )
        )

    return results

