from datetime import datetime
from enum import Enum

from pydantic import BaseModel,Field

class SimilarTicket(BaseModel):
    ticket_id: int
    similarity: float = Field(gt=0.0, le=1.0, description="Similarity Score in range of [0.0,1.0]")
    match_level: str  # "very_similar", "similar", "related"
    title: str
    category: str

class RelatedArticle(BaseModel):
    article_id: int
    title: str
    score: float
    category: str | None
    tags: list[str] = []

class IncidentInfo(BaseModel):
    possible_incident: bool
    severity: str  # "critical", "high", "medium", "low"
    fa_title_incident: str
    fa_reason_incident: str
    matched_ticket_ids: list[int] = []
    avg_similarity_score: float
    is_duplicate: bool = False
    duplicate_incident_id: int | None = None



class UILabels(BaseModel):
    category: str
    urgency: str

class AIAnalysisDetails(BaseModel):
    category: str
    category_label_fa: str
    category_score: float
    category_source: str
    intent: str
    intent_label_fa: str
    intent_score: float
    urgency: str
    urgency_score: int
    impact_label: str
    impact_label_fa: str
    sentiment: str
    frustration_score: int
    summary_fa: str
    suggested_reply_fa: str
    reply_tone: str
    confidence: float
    confidence_percent: int
    ui_labels: UILabels

    should_escalate: bool = False
    escalation_reason_fa: str | None = None
    needs_more_info: bool = False
    clarification_question_fa: str | None = None

    reasons_fa: list[str] = Field(default_factory=list)

class AIIntelligenceDetails(BaseModel):
    similar_tickets: list[SimilarTicket] = []
    related_article: RelatedArticle | None = None
    incident: IncidentInfo | None = None
    embedding_model_version: str
    latency_ms: float
    error: str | None = None

class AIResponseStatus(Enum):
    """ وضعیت های خروجی پاسخ ai core"""
    FAILED = "failed"
    PROCESSING = "processing"
    COMPLETED = "completed"

class Meta(BaseModel):
    """متادیتای تحلیل تیکت"""
    status: AIResponseStatus
    embedding_model_version: str
    analyzer_model_version: str
    latency_ms: float
    analyzed_at: datetime
    error: str | None = None

#----------------------------------------
# فرمت خروجی از 
# AI Core
# طبق مستندات پروژه

class AICoreResponse(BaseModel):
    ticket_id: int
    analysis: AIAnalysisDetails
    intelligence: AIIntelligenceDetails

    status: AIResponseStatus
    meta: Meta
#-----------------------------------------


class SimpleRelatedArticle(BaseModel):
    article_id: int
    title: str

class AnalysisRead(BaseModel):
    category: str
    category_label_fa: str

    confidence: float = Field(ge=0.0, le=1.0, description="Confidence Score in range of [0.0,1.0]")

    intent: str
    intent_label_fa: str

    urgency: str

    summary_fa: str
    suggested_reply_fa: str

    reasons_fa: list[str] = []
    related_article: list[SimpleRelatedArticle] = []

class AdminAnalysisRead(AnalysisRead):
    """
    اسکیما مخصوص خروجی دیتا آنالیز برای ادمین
    """
    related_article: list[RelatedArticle] = []
    similar_tickets: list[SimilarTicket] = []