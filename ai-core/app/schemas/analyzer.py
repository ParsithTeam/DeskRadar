from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class AnalyzeRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    ticket_id: str | None = Field(default=None, max_length=100)
    title: str = Field(default="", max_length=300)
    description: str = Field(default="", max_length=10_000)
    debug: bool = False

    @model_validator(mode="after")
    def validate_content(self) -> "AnalyzeRequest":
        if not self.title and not self.description:
            raise ValueError("حداقل یکی از title یا description باید مقدار داشته باشد.")
        return self

    def to_analysis_text(self) -> str:
        return "\n".join(part for part in (self.title, self.description) if part)


class AnalyzerResponse(BaseModel):
    """Stable public contract; internal diagnostic fields remain extensible."""

    model_config = ConfigDict(extra="allow")

    ticket_id: str | None = None
    analysis_status: Literal["completed"]
    category: str
    category_label_fa: str
    category_score: float = Field(ge=0, le=1)
    category_source: str
    intent: str
    intent_label_fa: str
    intent_score: float = Field(ge=0, le=1)
    urgency: str
    urgency_score: int = Field(ge=0, le=100)
    impact_label: str
    sentiment: str
    frustration_score: int = Field(ge=0, le=100)
    summary_fa: str
    suggested_reply_fa: str
    reply_tone: str
    confidence: float = Field(ge=0, le=1)
    confidence_percent: int = Field(ge=0, le=100)
    reasons_fa: list[str]
    should_escalate: bool
    escalation_reason_fa: str
    needs_more_info: bool
    clarification_question_fa: str | None = None
    ui_labels: dict[str, str]
    model_version: str
    analyzed_at: str
    details: dict[str, Any]
    raw_ai_response: dict[str, Any] | None = None
