import aio_pika
import requests
import json

URL = "http://localhost:5000/translate"

class TranslationConsumer:
    def __init__(self, language, websocket_manager):
        self.language = language
        self.websocket_manager = websocket_manager

    async def translate(self, message: aio_pika.IncomingMessage):
        async with message.process():
            text_to_translate = message.body.decode()
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
                    translated_text = response.json().get("translatedText", "")
                    if translated_text:
                        await self.websocket_manager.broadcast(translated_text, self.language)
                except json.JSONDecodeError:
                    print("Error parsing the JSON response.")

async def setup_rabbitmq_consumer(language, websocket_manager):
    connection = await aio_pika.connect_robust("amqp://guest:guest@localhost/")
    channel = await connection.channel()

    exchange_name = 'translate_exchange'
    await channel.declare_exchange(exchange_name, aio_pika.ExchangeType.FANOUT)

    queue = await channel.declare_queue(exclusive=True)
    await queue.bind(exchange_name)
    print("Queue bound to exchange")
    consumer = TranslationConsumer(language, websocket_manager)
    await queue.consume(consumer.translate)






