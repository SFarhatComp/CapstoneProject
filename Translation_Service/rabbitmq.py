import aio_pika
import httpx
import requests
import json
from redis import asyncio as aioredis

URL = "http://0.0.0.0:5000/translate"

class TranslationConsumer:
    def __init__(self, language, websocket_manager, redis):
        self.language = language
        self.websocket_manager = websocket_manager
        self.redis = redis  # Initialize Redis connection as None


    async def translate(self, message: aio_pika.IncomingMessage):
        print("Received message")
        async with message.process():
            print("Starting translation")
            text_to_translate = message.body.decode()
            inner_original_data = json.loads(text_to_translate)
            actual_original_text = str(inner_original_data.get("text", ""))
            translated_text = ""
            actual_translated_text = ""
            # Check if translation exists in Redis
            cache_key = f"{self.language}:{text_to_translate}"
            cached_translation = await self.redis.get(cache_key)
            if cached_translation:
                print("Cache hit")
                print(cached_translation)
                actual_translated_text = cached_translation
            else:
                print("no cache hit")
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
                            
                            translated_text_json = response_data.get("translatedText", "")
                            

                            if self.language == "fr":
                                # French translation logic
                                translated_text = response_data.get("translatedText", "")
                                inner_translated_data = json.loads(translated_text)
                                actual_translated_text = str(inner_translated_data.get("texte", ""))
                                await self.redis.set(cache_key, actual_translated_text)

                            elif self.language == "es":
                                # Spanish translation logic
                                    translated_text_str = response_data.get('translatedText').replace('{}\n', '').replace('\n}', '')
                                    translated_text_json = '{' + translated_text_str + '}'
                                    inner_translated_data = json.loads(translated_text_json)
                                    actual_translated_text = str(inner_translated_data.get("texto", ""))
                                    print("setting cache key", cache_key)
                                    print(f"Text {actual_translated_text}")
                                    await self.redis.set(cache_key, actual_translated_text)
                                    print("Text was cached")

                            else:
                                print("No translating text available.")
                        except json.JSONDecodeError:
                            print("Error parsing the JSON response.")
            if actual_translated_text:
                data_to_send = {
                "originalText": actual_original_text,
                "translatedText": actual_translated_text,
                }
                json_data_to_send = json.dumps(data_to_send)
                print(f"Translated text {actual_translated_text}")
                await self.websocket_manager.broadcast(json_data_to_send, self.language)

async def setup_rabbitmq_consumer(language, websocket_manager):
    connection = await aio_pika.connect_robust("amqp://guest:guest@localhost/")
    channel = await connection.channel()

    exchange_name = 'translate_exchange'
    await channel.declare_exchange(exchange_name, aio_pika.ExchangeType.FANOUT)

    queue = await channel.declare_queue(exclusive=True)
    await queue.bind(exchange_name)
    print("Initialing Redis")
    redis = aioredis.from_url("redis://localhost:6379", encoding="utf-8", decode_responses=True)
    print("Initialized Redis")
    consumer = TranslationConsumer(language, websocket_manager, redis) 
    await queue.consume(consumer.translate)






