from typing import List
from fastapi import APIRouter, Header, HTTPException, Query, WebSocket, WebSocketDisconnect, status

from app.repositories.alert_repository import AlertRepository
from app.schemas.alert import AlertCreate, AlertResponse
from app.services.alert_service import AlertService
from app.websocket.manager import ws_manager

router = APIRouter(prefix="/alerts", tags=["Alerts"])

alert_repo = AlertRepository()
alert_service = AlertService(alert_repo=alert_repo)


@router.websocket("/ws")
async def websocket_alert(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)


@router.get(
    "",
    response_model=List[AlertResponse],
    summary="دریافت لیست هشدارها",
)
@router.get(
    "/",
    response_model=List[AlertResponse],
    include_in_schema=False,
)
async def get_alerts(unread_only: bool = False):
    return await alert_service.fetch_alerts(unread_only=unread_only)


@router.post(
    "/{alert_id}/read",
    response_model=AlertResponse,
    status_code=status.HTTP_200_OK,
    summary="خواندن هشدار و ثبت اولین ادمین به عنوان مسئول (First-Read)",
)
@router.post(
    "/{alert_id}/mark-read",
    response_model=AlertResponse,
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
)
async def mark_alert_as_read(
    alert_id: int,
    admin_id: str | None = Query(default=None, description="شناسه ادمین خواننده"),
    admin_name: str | None = Query(default=None, description="نام ادمین خواننده"),
    x_admin_id: str | None = Header(default=None, alias="X-Admin-Id"),
    x_admin_name: str | None = Header(default=None, alias="X-Admin-Name"),
):
    effective_admin_id = admin_id or x_admin_id or "admin-1"
    effective_admin_name = admin_name or x_admin_name or "مدیر پشتیبانی"

    try:
        alert = await alert_service.mark_alert_read(
            alert_id=alert_id,
            admin_id=effective_admin_id,
            admin_name=effective_admin_name,
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"{str(e)}")

    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="هشدار یافت نشد.")

    return alert


@router.post(
    "/test-trigger",
    response_model=AlertResponse,
    status_code=status.HTTP_201_CREATED,
    summary="ایجاد و انتشار هشدار تستی",
)
async def trigger_test_alert(alert_in: AlertCreate):
    return await alert_service.create_and_broadcast(alert_in)