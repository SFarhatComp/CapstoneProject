import requests
import json
import pika

URL = "http://localhost:5000/translate"

class TranslationConsumer:
    def __init__(self, language, websocket_queue):

        self.language = language
        self.websocket_queue = websocket_queue

    def translate(self, ch, method, properties, body):

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
                inner_original_data = json.loads(text_to_translate)
                actual_original_text = str(inner_original_data.get("text", ""))
                print("Original text:", actual_original_text)
                # Parse the 'translatedText' string as JSON
                inner_translated_data = json.loads(translated_text_json)
                
                # Extract the actual text (e.g., "texte") from the inner JSON
                actual_translated_text = str(inner_translated_data.get("texte", ""))
                
                print("Translated text:", actual_translated_text)

                if actual_translated_text:
                    # Create a JSON object with the original text, translated text, and speaker name
                    data_to_send = {
                        "originalText": actual_original_text,
                        "translatedText": actual_translated_text,

                    }

                    # Put the actual translated text into the WebSocket queue
                    
                    json_data_to_send = json.dumps(data_to_send)
                    
                    self.websocket_queue.put(json_data_to_send)
                else:
                    print("No actual translated text found in the response.")
            except json.JSONDecodeError:
                print("Error parsing the JSON response.")
        else:
            print("Failed to translate. Status code:", response.status_code)
        ch.basic_ack(delivery_tag=method.delivery_tag)

def general_set_up():

    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    exchange_name = 'translate_exchange'
    return channel, exchange_name

def start_rabbitmq_consumer(language, websocket_queue):

    channel, exchange_name = general_set_up()
    result = channel.queue_declare('', exclusive=True)
    queue_name = result.method.queue
    channel.queue_bind(exchange=exchange_name, queue=queue_name)
    channel.basic_qos(prefetch_count=1)
    consumer = TranslationConsumer(language, websocket_queue)
    channel.basic_consume(queue=queue_name, on_message_callback=consumer.translate)
    channel.start_consuming()

