from fastapi import FastAPI, WebSocket
from starlette.websockets import WebSocketDisconnect
from starlette.responses import StreamingResponse
from websocket_manager import WebSocketConnectionManager
from rabbitmq import setup_rabbitmq_consumer
import json
import asyncio
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ws_manager = WebSocketConnectionManager()

@app.websocket("/ws/{language}/{speaker}")
async def websocket_endpoint(websocket: WebSocket, language: str = "fr" , speaker: str = "John Doe"):
    await ws_manager.connect(websocket, language , speaker)
    consumer_task = asyncio.create_task(setup_rabbitmq_consumer(language, ws_manager))

    try:
        while True:
            # Keeping the connection open
            await asyncio.sleep(10)
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, language)
    finally:
        consumer_task.cancel()


@app.get("/speakers")
async def get_speakers():
    async def event_stream():
        while True:
            # Assuming you have a method in WebSocketConnectionManager to get all speakers
            speakers = ws_manager.get_all_speakers()
            data = json.dumps(speakers)
            yield f"data: {data}\n\n"
            await asyncio.sleep(1)  # Adjust the sleep time as needed

    return StreamingResponse(event_stream(), media_type="text/event-stream")
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="10.0.0.52", port=8001)
