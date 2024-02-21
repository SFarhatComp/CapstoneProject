from fastapi import FastAPI, WebSocket
from starlette.websockets import WebSocketDisconnect
from websocket_manager import WebSocketConnectionManager
from rabbitmq import setup_rabbitmq_consumer
import asyncio

app = FastAPI()
ws_manager = WebSocketConnectionManager()

@app.websocket("/ws/{language}")
async def websocket_endpoint(websocket: WebSocket, language: str = "fr"):
    await ws_manager.connect(websocket, language)
    consumer_task = asyncio.create_task(setup_rabbitmq_consumer(language, ws_manager))

    try:
        while True:
            # Keeping the connection open
            await asyncio.sleep(10)
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, language)
    finally:
        consumer_task.cancel()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8001)