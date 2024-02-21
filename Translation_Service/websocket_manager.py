from fastapi import WebSocket
class WebSocketConnectionManager:
    def __init__(self):
        self.active_connections = {}

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

