from __future__ import annotations

from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.infrastructure.schemas import (
    InfrastructureResult,
    OldTicketRecord,
    OpenIncidentRecord,
)


class UnifiedAnalyzeRequest(BaseModel):
    """
    Unified request payload for analyzing a support ticket across both
    Analyzer AI and Infrastructure AI.
    """
    model_config = ConfigDict(str_strip_whitespace=True, extra="allow")

    ticket_id: int | None = Field(default=None, gt=0, description="Unique ticket ID")
    title: str = Field(min_length=1, max_length=300, description="Ticket title / summary")
    description: str = Field(default="", max_length=10_000, description="Ticket full description")
    category: str | None = Field(default=None, description="Optional category hint (if known)")
    old_tickets: list[OldTicketRecord] = Field(
        default_factory=list,
        description="Pool of active/recent tickets for semantic similarity and incident clustering",
    )
    open_incidents: list[OpenIncidentRecord] = Field(
        default_factory=list,
        description="List of open incidents for deduplication",
    )
    debug: bool = Field(default=False, description="Whether to include detailed debug diagnostics")

    @model_validator(mode="after")
    def validate_content(self) -> "UnifiedAnalyzeRequest":
        if not self.title.strip() and not self.description.strip():
            raise ValueError("حداقل یکی از title یا description باید مقدار داشته باشد.")
        return self

    def to_analysis_text(self) -> str:
        parts = [self.title.strip(), self.description.strip()]
        return "\n".join(p for p in parts if p)


class UnifiedAnalyzeResponse(BaseModel):
    """
    Unified response payload containing both the Persian text analysis (Analyzer)
    and the semantic intelligence block (Infrastructure).
    """
    model_config = ConfigDict(extra="allow")

    ticket_id: int | str | None = None
    status: Literal["completed", "partial", "failed"] = "completed"
    analysis: dict[str, Any] = Field(
        description="Persian NLP analysis: category, intent, urgency, sentiment, summary, suggested reply",
    )
    intelligence: InfrastructureResult = Field(
        description="Semantic infrastructure: similar tickets, KB retrieval, incident detection & dedup",
    )
    meta: dict[str, Any] = Field(
        default_factory=dict,
        description="Execution metadata: model versions, latency, timestamp, status",
    )
