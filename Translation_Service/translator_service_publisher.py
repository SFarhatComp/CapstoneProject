import pika
import asyncio
import sys
import tty
import termios
import os
import vosk
import pyaudio
import websockets       
            
async def audio_stream(websocket, path, recognizer):
    # Establish a connection with RabbitMQ server
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    # Declare the exchange
    exchange_name = 'translate_exchange'
    channel.exchange_declare(exchange=exchange_name, exchange_type='fanout')

    try:
        async for message in websocket:
            print("Received audio data chunk")
            # Assuming message is binary audio data
            if isinstance(message, bytes):
                if recognizer.AcceptWaveform(message):
                    result = recognizer.Result()
                    print(f"Recognized Text: {result}")
                    # Extracting text from result
                    result_dict = json.loads(result)
                    text = result_dict.get("text", "")
                    
                    # Publishing recognized text to RabbitMQ
                    if text:
                        print(f"Publishing recognized text to RabbitMQ: {text}")
                        channel.basic_publish(exchange=exchange_name, routing_key='', body=text)
            else:
                print("Non-binary message received, not processed.")
    finally:
        # Close the connection
        connection.close()

async def main():
    # Set up the Vosk recognizer
    model_path = "Models/vosk-model-small-en-us-0.15"
    if not os.path.exists(model_path):
        print("Model path does not exist, please check the model directory.")
        return
    
    vosk.SetLogLevel(-1)
    recognizer = vosk.KaldiRecognizer(vosk.Model(model_path), 16000)

    async with websockets.serve(lambda ws, path: audio_stream(ws, path, recognizer), "localhost", 8000):
        await asyncio.Future()  # This keeps the server running


if __name__== "__main__":
    asyncio.run(main())


    
    
    
