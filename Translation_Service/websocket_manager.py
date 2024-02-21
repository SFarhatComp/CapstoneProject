from fastapi import WebSocket
from typing import Dict, Set
import logging
import traceback
logging.basicConfig(level=logging.INFO)

class WebSocketConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, language: str):
        await websocket.accept()
        if language not in self.active_connections:
            self.active_connections[language] = set()
        self.active_connections[language].add(websocket)

    def disconnect(self, websocket: WebSocket, language: str):
        if language in self.active_connections:
            self.active_connections[language].remove(websocket)
            if not self.active_connections[language]:
                del self.active_connections[language]

    async def broadcast(self, message: str, language: str):
        if language in self.active_connections:
            for connection in self.active_connections[language]:
                await connection.send_text(message)