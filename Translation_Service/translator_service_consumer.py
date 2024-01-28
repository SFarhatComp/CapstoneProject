import requests
import json
import pika
import pprint
URL = "http://localhost:5000/translate"

def translate(ch, method, properties, body):
    
    text_to_translate = body.decode()
    # print(f"Translating: {text_to_translate}")
    
    # Your data payload
    data = {
        "q": text_to_translate,
        "source": "en",
        "target": "fr",
        "format": "text",
        "api_key": ""
    }

    # Send the POST request
    response = requests.post(URL, json=data)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the response
        translated_text = response.json()
        print(translated_text)
        #inner_json = json.loads(translated_text['translatedText'])
        #print(f"Translated : {inner_json['texte']} ")
    else:
        print("Failed to translate. Status code:", response.status_code)

    ch.basic_ack(delivery_tag = method.delivery_tag)


def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    # Declare the queue (this will only create it if it doesn't already exist)
    queue_name = 'translate'
    channel.queue_declare(queue=queue_name)


    # Declare the exchange (this will only create it if it doesn't already exist)
    exchange_name = 'translate_exchange'
    channel.queue_bind(exchange=exchange_name, queue=queue_name)


    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='translate', on_message_callback=translate)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("\nInterrupted by user. Stopping...")
        channel.stop_consuming()
        connection.close()

if __name__== "__main__":
    main()
