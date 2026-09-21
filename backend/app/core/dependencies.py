# app/api/dependencies.py
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.repositories.knowledge_base_repository import KnowledgeBaseRepository
from app.repositories.ticket_repository import TicketRepository
from app.repositories.incident_repository import IncidentRepository
from app.repositories.alert_repository import AlertRepository
from app.services.alert_service import AlertService
from app.services.analysis_service import AnalysisService
from app.services.incident_service import IncidentService
from app.services.knowledge_base_service import KnowledgeBaseService
from app.services.ticket_service import TicketService


# ---------- Repositories ----------

def get_ticket_repository(
    session: AsyncSession = Depends(get_session),
) -> TicketRepository:
    return TicketRepository(session=session)


def get_incident_repository(
    session: AsyncSession = Depends(get_session),
) -> IncidentRepository:
    return IncidentRepository(session=session)


def get_alert_repository(
    session: AsyncSession = Depends(get_session),
) -> AlertRepository:
    return AlertRepository(session=session)

def get_kb_repository(
    session: AsyncSession = Depends(get_session),
) -> AlertRepository:
    return AlertRepository(session=session)

# ---------- Services ----------

def get_alert_service(
    alert_repo: AlertRepository = Depends(get_alert_repository),
) -> AlertService:
    return AlertService(alert_repo=alert_repo)


def get_analysis_service() -> AnalysisService:
    return AnalysisService()


def get_incident_service(
    incident_repo: IncidentRepository = Depends(get_incident_repository),
    alert_serv: AlertService = Depends(get_alert_service),
    ticket_repo: TicketRepository = Depends(get_ticket_repository),
) -> IncidentService:
    return IncidentService(
        incident_repo=incident_repo,
        alert_serv=alert_serv,
        ticket_repo=ticket_repo,
    )


def get_ticket_service(
    ticket_repo: TicketRepository = Depends(get_ticket_repository),
    analysis_serv: AnalysisService = Depends(get_analysis_service),
    incident_serv: IncidentService = Depends(get_incident_service),
) -> TicketService:
    return TicketService(
        ticket_repo=ticket_repo,
        analysis_serv=analysis_serv,
        incident_serv=incident_serv,
    )

def get_kb_service(
    kb_repo: KnowledgeBaseRepository = Depends(get_kb_repository),
) -> KnowledgeBaseService:
    return KnowledgeBaseService(kb_repo=kb_repo)