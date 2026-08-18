from fastapi import WebSocket
import json

class ConnectionManager:
    def __init__(self):
        # لیست کانکشن ها
        self.active_connections = list[WebSocket]()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if(websocket in self.active_connections):
            self.active_connections.remove(websocket)

    async def broadcast_alert(self, alert: dict):
        message = json.dumps(alert, ensure_ascii=False)
        for connection in self.active_connections:
            await connection.send_json(message)

websocket_manager = ConnectionManager()
