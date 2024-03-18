from fastapi import WebSocket
import json
class WebSocketConnectionManager:
    def __init__(self):
        self.active_connections = {}

    async def connect(self, websocket: WebSocket, language: str, speaker: str):
        await websocket.accept()
        if language not in self.active_connections:
            self.active_connections[language] = {}
        self.active_connections[language][speaker] = websocket

    def disconnect(self, websocket: WebSocket, language: str, speaker: str):
        if language in self.active_connections and speaker in self.active_connections[language]:
            del self.active_connections[language][speaker]
            if not self.active_connections[language]:
                del self.active_connections[language]

    async def broadcast(self, message: str, language: str):
        if language in self.active_connections:
            for speaker in self.active_connections[language]:
                await self.active_connections[language][speaker].send_text(message)

    def get_all_speakers(self):
        speakers = []
        for language in self.active_connections:
            for speaker in self.active_connections[language]:
                speaker_data = f"{speaker} - {language}"
                speakers.append(speaker_data)
        return speakers