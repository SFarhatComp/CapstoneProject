from fastapi import WebSocket
from typing import Dict, Set
import logging
import traceback
logging.basicConfig(level=logging.INFO)

class WebSocketConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Dict[str, WebSocket]] = {}

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
            disconnected_websockets = set()
            for speaker, websocket in self.active_connections[language].items():
                try:
                    print(f"Sending message to {speaker}")
                    print(message)
                    await websocket.send_text(message)
                except Exception as e:
                    # Assuming you want to log or handle the exception
                    print(f"Error sending message to {speaker}: {e}")
                    self.disconnect(websocket, language, speaker)
            


    def get_all_speakers(self):
        speakers = []
        for language, speakers_dict in self.active_connections.items():
            for speaker in speakers_dict:
                speakers.append(f"{speaker} - {language}")
        return speakers
