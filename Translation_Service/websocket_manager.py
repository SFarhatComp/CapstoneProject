from fastapi import WebSocket
from typing import Dict, Set
import os
import logging
import traceback
from datetime import datetime
logging.basicConfig(level=logging.INFO)

class WebSocketConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Dict[str, WebSocket]] = {}

    async def connect(self, websocket: WebSocket, language: str, speaker: str):
        await websocket.accept()
        if language not in self.active_connections:
            self.active_connections[language] = {}
        self.active_connections[language][speaker] = websocket
        print(f"List of connected speakers : {self.active_connections}")

    def disconnect(self, websocket: WebSocket, language: str, speaker: str):
        if language in self.active_connections and speaker in self.active_connections[language]:
            del self.active_connections[language][speaker]
            if not self.active_connections[language]:
                del self.active_connections[language]


    async def broadcast(self, message: str, language: str , active_speaker: str):
        if language in self.active_connections:
            disconnected_websockets = set()
            for speaker, websocket in self.active_connections[language].items():
                try:
                    print(f"Sending message to {speaker}")
                    print(message)
                    await websocket.send_text(message)

                    today = datetime.now().strftime('%Y-%m-%d')

                    with open(f"{speaker}_{language}_{today}.txt", "a") as log_file:
                        log_file.write(f"{active_speaker} : {message}" + os.linesep)
                except Exception as e:
                    # Assuming you want to log or handle the exception
                    print(f"Error sending message to {speaker}: {e}")
                    self.disconnect(websocket, language, speaker)
            


    def get_all_speakers(self):
        speakers = []
        for language, speakers_dict in self.active_connections.items():
            for speaker in speakers_dict:
                speakers.append(f"{speaker}-{language}")
        return speakers
