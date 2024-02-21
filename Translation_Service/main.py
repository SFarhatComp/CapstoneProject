from fastapi import FastAPI, WebSocket
from threading import Thread
from websocket_manager import WebSocketConnectionManager
from rabbitmq import start_rabbitmq_consumer
from starlette.websockets import WebSocketDisconnect
import asyncio
import queue as async_queue

app = FastAPI()
ws_manager = WebSocketConnectionManager()

@app.websocket("/ws/{language}")
async def websocket_endpoint(websocket: WebSocket, language: str = "fr"):
    await ws_manager.connect(websocket, language)
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8001)