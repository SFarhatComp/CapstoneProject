import aio_pika
import httpx
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
            
            async with httpx.AsyncClient() as client:
                response = await client.post(URL, json=data)
                if response.status_code == 200:
                    try:
                        response_data = response.json()
                        translated_text = ""
                        actual_translated_text = ""
                        translated_text_json = response_data.get("translatedText", "")
                        inner_original_data = json.loads(text_to_translate)
                        actual_original_text = str(inner_original_data.get("text", ""))


                        if self.language == "fr":
                            # French translation logic
                            translated_text = response_data.get("translatedText", "")
                            inner_translated_data = json.loads(translated_text)
                            actual_translated_text = str(inner_translated_data.get("texte", ""))
                        elif self.language == "es":
                            # Spanish translation logic
                                translated_text_str = response_data.get('translatedText').replace('{}\n', '').replace('\n}', '')
                                translated_text_json = '{' + translated_text_str + '}'
                                inner_translated_data = json.loads(translated_text_json)
                                actual_translated_text = str(inner_translated_data.get("texto", ""))

                        if actual_translated_text:
                            data_to_send = {
                            "originalText": actual_original_text,
                            "translatedText": actual_translated_text,
                            }
                            json_data_to_send = json.dumps(data_to_send)

                            await self.websocket_manager.broadcast(json_data_to_send, self.language)
                        else:
                            print("No translating text available.")
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






