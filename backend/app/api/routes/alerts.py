from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
from app.websocket.manager import ws_manager
from app.schemas.alert import AlertCreate

router = APIRouter(prefix="/alerts", tags=["Alerts"])


# ۱. روت وب‌سوکت (فرانت‌اند به این مسیر گوش می‌دهد)
@router.websocket("/ws")
async def websocket_alert(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            # منتظر ماندن برای تشخیص قطع اتصال از سمت مرورگر
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
        print("websocket disconnected.")


# ۲. روت تستی برای شبیه‌سازی (از Swagger صدا زده می‌شود)
@router.post("/test-trigger", status_code=status.HTTP_200_OK)
async def trigger_test_alert(alert_in: AlertCreate):
    """
    این روت صرفاً برای تست ماژولار است.
    در سیستم نهایی، این منطق داخل AlertService و پس از تشخیص AI صدا زده می‌شود.
    """
    # تبدیل داده‌های Pydantic به دیکشنری و ارسال به تمام کلاینت‌های متصل
    await ws_manager.broadcast_alert(alert_in.model_dump())
    return {"status": "success", "detail": "Alert broadcasted to all connected clients."}