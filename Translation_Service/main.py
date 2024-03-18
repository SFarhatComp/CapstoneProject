from fastapi import FastAPI, WebSocket, Response 
from threading import Thread
from websocket_manager import WebSocketConnectionManager
from rabbitmq import start_rabbitmq_consumer
from starlette.websockets import WebSocketDisconnect
from starlette.responses import StreamingResponse
import asyncio
import json
from typing import Generator
import queue as async_queue
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

ws_manager = WebSocketConnectionManager()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.websocket("/ws/{language}/{speaker}")
async def websocket_endpoint(websocket: WebSocket, language: str = "fr" , speaker: str = "John Doe"):
    print(f"Connected to WebSocket with language {language} and speaker {speaker}")
    print(f"Current Active Connections {ws_manager.active_connections}")
    await ws_manager.connect(websocket, language, speaker)
    
    websocket_queue = async_queue.Queue()

    consumer_thread = Thread(target=start_rabbitmq_consumer, args=(language, websocket_queue,))
    consumer_thread.start()

    try:
        while True:
            message = await asyncio.get_event_loop().run_in_executor(None, websocket_queue.get)
            print("Sending message to WebSocket:", message)
            await ws_manager.broadcast(message, language)
    except WebSocketDisconnect:
        print("WebSocket disconnected")
        ws_manager.disconnect(websocket, language)


@app.get("/speakers")
async def get_speakers():
    async def event_stream():
        while True:
            speakers = ws_manager.get_all_speakers()
            data = json.dumps(speakers)
            yield f"data: {data}\n\n"
            await asyncio.sleep(1)  # Adjust the sleep time as needed

    return StreamingResponse(event_stream(), media_type="text/event-stream")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="10.0.0.52", port=8001)