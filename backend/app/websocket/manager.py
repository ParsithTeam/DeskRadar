import asyncio
from fastapi import WebSocket, WebSocketException
from typing import Optional
import json


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
        self.default_timeout: float = 5.0  # زمان پیش فرض برای اتصال

    async def connect(self, websocket: WebSocket, timeout: Optional[float] = None):
        timeout = timeout or self.default_timeout
        try:
            await asyncio.wait_for(websocket.accept(), timeout=timeout)
            self.active_connections.append(websocket)
            print(f"New Connection accepted. Active: {len(self.active_connections)}")

        except asyncio.TimeoutError:
            try:
                await websocket.close(code=1008, reason="Connection timeout")
            except Exception:
                pass  # ignore if socket is already closed

            raise WebSocketException(
                code=1008,
                reason=f"Connection timeout after {timeout} seconds"
            )
        except Exception as e:
            raise WebSocketException(
                code=1011,
                reason=f"Connection error: {str(e)}"
            )

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            print(f"Connection closed. Active: {len(self.active_connections)}")

    async def broadcast_alert(self, alert_data: dict):
        message = json.dumps(alert_data, ensure_ascii=False)
        # برای ایمنی بیشتر، اگر ارسال به یک کلاینت خطا داد، بقیه کلاینت‌ها مختل نشوند
        for connection in list(self.active_connections):
            try:
                await connection.send_text(message)
            except Exception:
                self.disconnect(connection)


ws_manager = ConnectionManager()