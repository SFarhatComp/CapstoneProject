from fastapi import FastAPI, WebSocket
from threading import Thread
import requests
import pika

app = FastAPI()
URL = "http://localhost:5000/translate"

channel, exchange_name = None, None


class TranslationConsumer:
    def __init__(self, language , websocket):
        self.language = language
        self.websocket = websocket

    async def translate(self, ch, method, properties, body):
        text_to_translate = body.decode()

        # Your data payload
        data = {
            "q": text_to_translate,
            "source": "en",
            "target": self.language,
            "format": "text",
            "api_key": ""
        }

        # Send the POST request
        response = requests.post(URL, json=data)

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the response
            translated_text = response.json()
            await self.websocket.send("Your message here")
            print(translated_text)
            
        else:
            print("Failed to translate. Status code:", response.status_code)

        ch.basic_ack(delivery_tag=method.delivery_tag)


def genereal_set_up():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    exchange_name = 'translate_exchange'
    # Declare the exchange (this will only create it if it doesn't already exist)

    return channel , exchange_name

def main(language: str = "fr"):
    global channel, exchange_name
    print("general set up initialized")
    channel, exchange_name = genereal_set_up()

    
@app.websocket("/ws/{language}")
async def websocket_endpoint(websocket: WebSocket, language: str = "fr"):
    await websocket.accept()
    # Start a new thread running the consumer for each request to this endpoint
    result = channel.queue_declare('', exclusive=True)
    queue_name = result.method.queue
    channel.queue_bind(exchange=exchange_name, queue=queue_name)
    channel.basic_qos(prefetch_count=1)

    consumer = TranslationConsumer(language, websocket)
    channel.basic_consume(queue=queue_name, on_message_callback=consumer.translate)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("\nInterrupted by user. Stopping...")
        channel.stop_consuming()

if __name__ == "__main__":
    main()
    import uvicorn
    uvicorn.run(app, host="localhost", port=8001)
