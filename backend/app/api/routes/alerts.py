from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status, HTTPException
from app.websocket.manager import ws_manager
from app.schemas.alert import AlertCreate, AlertResponse
from typing import List

# ایجاد سرویس (در آینده با Depends انجام می‌شود)
from app.api.routes.tickets import alert_serv as alert_service

router = APIRouter(prefix="/alerts", tags=["Alerts"])

@router.websocket("/ws")
async def websocket_alert(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)

# روت استاندارد برای دریافت تاریخچه هشدارها
@router.get("/", response_model=List[AlertResponse])
async def get_alerts(unread_only: bool = False):
    return await alert_service.fetch_alerts(unread_only=unread_only)

# روت استاندارد برای خوانده‌شده کردن هشدار
@router.post("/{alert_id}/mark-read", response_model=AlertResponse)
async def mark_alert_as_read(alert_id: int):
    try:
        alert = await alert_service.mark_alert_read(alert_id)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"{str(e)}")
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert

# روت تستی برای تریگر کردن هشدار
@router.post("/test-trigger", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
async def trigger_test_alert(alert_in: AlertCreate):
    # حالا به جای پخش مستقیم، سرویس را صدا می‌زنیم تا هم ذخیره کند و هم پخش
    return await alert_service.create_and_broadcast(alert_in)