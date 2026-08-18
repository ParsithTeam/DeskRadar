from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.websocket.manager import websocket_manager

router = APIRouter()

@router.websocket("/ws/alerts")
async def websocket_alert(websocket: WebSocket):
    await websocket_manager.connect(websocket)
    try:
        while True:
            # گوش دادم مداوم برای حفظ اتصال و تشخیص قطع
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)