from fastapi import FastAPI, WebSocket
from threading import Thread
import requests
import json
import pika
import asyncio
from starlette.websockets import WebSocketDisconnect
import queue as async_queue

app = FastAPI()
URL = "http://localhost:5000/translate"

channel, exchange_name = None, None

# Asynchronous Queue to pass messages between threads
websocket_message_queue = async_queue.Queue()

class TranslationConsumer:
    def __init__(self, language, websocket_queue):
        """
        Initializes a TranslationConsumer object.

        Args:
            language (str): The target language for translation.
            websocket_queue (Queue): The queue to pass translated messages to the WebSocket.
        """
        self.language = language
        self.websocket_queue = websocket_queue

    def translate(self, ch, method, properties, body):
        """
        Translates the given text using an external translation service.

        Args:
            ch: The RabbitMQ channel.
            method: The RabbitMQ method.
            properties: The RabbitMQ properties.
            body (bytes): The text to be translated.

        Returns:
            None
        """
        text_to_translate = body.decode()
        data = {
            "q": text_to_translate,
            "source": "en",
            "target": self.language,
            "format": "text",
            "api_key": ""
        }
        response = requests.post(URL, json=data)
        if response.status_code == 200:
            try:
                translated_data = response.json()

                # Extract the 'translatedText' field
                translated_text_json = translated_data.get("translatedText", "{}")

                # Parse the 'translatedText' string as JSON
                inner_translated_data = json.loads(translated_text_json)

                # Extract the actual text (e.g., "texte") from the inner JSON
                actual_translated_text = str(inner_translated_data.get("texte", ""))

                print("Translated text:", actual_translated_text)

                if actual_translated_text:
                    # Put the actual translated text into the WebSocket queue
                    self.websocket_queue.put(actual_translated_text)
                else:
                    print("No actual translated text found in the response.")
            except json.JSONDecodeError:
                print("Error parsing the JSON response.")
        else:
            print("Failed to translate. Status code:", response.status_code)
        ch.basic_ack(delivery_tag=method.delivery_tag)

def general_set_up():
    """
    Performs general setup for RabbitMQ connection.

    Returns:
        channel: The RabbitMQ channel.
        exchange_name: The name of the exchange.
    """
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    exchange_name = 'translate_exchange'
    return channel, exchange_name

def start_rabbitmq_consumer(language, websocket_queue):
    """
    Starts the RabbitMQ consumer for translating messages.

    Args:
        language (str): The target language for translation.
        websocket_queue (Queue): The queue to pass translated messages to the WebSocket.

    Returns:
        None
    """
    channel, exchange_name = general_set_up()
    result = channel.queue_declare('', exclusive=True)
    queue_name = result.method.queue
    channel.queue_bind(exchange=exchange_name, queue=queue_name)
    channel.basic_qos(prefetch_count=1)
    consumer = TranslationConsumer(language, websocket_queue)
    channel.basic_consume(queue=queue_name, on_message_callback=consumer.translate)
    channel.start_consuming()

@app.websocket("/ws/{language}")
async def websocket_endpoint(websocket: WebSocket, language: str = "fr"):
    """
    WebSocket endpoint for receiving and sending translated messages.

    Args:
        websocket (WebSocket): The WebSocket connection.
        language (str, optional): The target language for translation. Defaults to "fr".

    Returns:
        None
    """
    await websocket.accept()
    websocket_queue = async_queue.Queue()

    # Start RabbitMQ consumer in a separate thread
    consumer_thread = Thread(target=start_rabbitmq_consumer, args=(language, websocket_queue,))
    consumer_thread.start()

    try:
        while True:
            # Wait for a message from the RabbitMQ consumer
            message = await asyncio.get_event_loop().run_in_executor(None, websocket_queue.get)
            print("Sending message to WebSocket:", message)
            await websocket.send_text(message)
    except WebSocketDisconnect:
        print("WebSocket disconnected")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8001)
