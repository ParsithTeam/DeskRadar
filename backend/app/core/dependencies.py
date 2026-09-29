# app/api/dependencies.py
from fastapi import Depends, HTTPException, status as http_status
from fastapi.security import OAuth2PasswordBearer
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.security import decode_access_token
from app.repositories.knowledge_base_repository import KnowledgeBaseRepository
from app.repositories.ticket_repository import TicketRepository
from app.repositories.incident_repository import IncidentRepository
from app.repositories.alert_repository import AlertRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth import TokenPayload
from app.schemas.user import Role
from app.services.alert_service import AlertService
from app.services.analysis_service import AnalysisService
from app.services.auth_service import AuthService
from app.services.incident_service import IncidentService
from app.services.knowledge_base_service import KnowledgeBaseService
from app.services.ticket_service import TicketService


# ---------- Repositories ----------

def get_ticket_repository(
    session: AsyncSession | None = Depends(get_session),
) -> TicketRepository:
    return TicketRepository(session=session)


def get_incident_repository(
    session: AsyncSession | None = Depends(get_session),
) -> IncidentRepository:
    return IncidentRepository(session=session)


def get_alert_repository(
    session: AsyncSession | None = Depends(get_session),
) -> AlertRepository:
    return AlertRepository(session=session)

# def get_kb_repository(
#     session: AsyncSession | None = Depends(get_session),
# ) -> AlertRepository:
#     return AlertRepository(session=session)

def get_kb_repository(
    session: AsyncSession | None = Depends(get_session),
) -> KnowledgeBaseRepository:
    return KnowledgeBaseRepository(session=session)








def get_user_repository(
    session: AsyncSession | None = Depends(get_session),
) -> UserRepository:
    return UserRepository(session=session)

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

def get_auth_service(
        user_repo: UserRepository = Depends(get_user_repository),
) -> AuthService:
    return AuthService(user_repo=user_repo)

#------------ Auth -----------------
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user(
        token: str = Depends(oauth2_scheme)
) -> dict:
    #TODO: اضافه کردن منطق چک با دیتابیس در صورت نیاز در آینده
    credentials_exception = HTTPException(
        status_code=http_status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    raw = decode_access_token(token=token)
    if not raw:
        print("Auth Exception: not valid raw!")
        raise credentials_exception

    try:
        payload = TokenPayload.model_validate(raw)
    except ValidationError:
        print("Auth Exception: not valid payload!")
        raise credentials_exception

    return {"user_id": payload.sub, "role": payload.role}

def get_current_admin(
        current_user: dict = Depends(get_current_user)
) -> dict:
    if current_user["role"] != Role.ADMIN:
        raise HTTPException(status_code=http_status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return current_user



#------------ wrapper----------------
def buil_ticket_service(session: AsyncSession | None)->TicketService:
    ticket_repo = TicketRepository(session)
    incident_repo = IncidentRepository(session)
    alert_repo = AlertRepository(session)
    alert_serv = AlertService(alert_repo)
    incident_serv = IncidentService(incident_repo, alert_serv, ticket_repo)
    analysis_serv = AnalysisService()
    return TicketService(ticket_repo, analysis_serv, incident_serv)