import pika
import os
import vosk
import pyaudio
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()
class Item(BaseModel):
    name : str
    language: str


def general_set_up(language):
    
    if language == "en":
        # Set up the Vosk model and recognizer
        model_path = "Models/vosk-model-small-en-us-0.15"
        if not os.path.exists(model_path):
            print("Please download the model from https://alphacephei.com/vosk/models and unpack as 'model' in the current folder.")
            exit(1) 
    else:
        print("Language not supported")
        return
    
    # Initialize the Vosk recognizer with the model
    vosk.SetLogLevel(-1)
    recognizer = vosk.KaldiRecognizer(vosk.Model(model_path), 16000)

    # Set up audio input from microphone
    audio_input = pyaudio.PyAudio()
    stream = audio_input.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)

    return recognizer, stream

def send_message(recognizer,stream):
    # Establish a connection with RabbitMQ server
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    # Declare the exchange (this will only create it if it doesn't already exist)
    exchange_name = 'translate_exchange'
    channel.exchange_declare(exchange=exchange_name, exchange_type='fanout')

    print(f"Starting Input from Mic : ")
    while True:
        
        try:
            data = stream.read(8000) 
        
            if len(data) > 0:
                if recognizer.AcceptWaveform(data):
                    result = recognizer.Result()
                    print(result)
                    # Sending a message to the Exchange
                    channel.basic_publish(exchange=exchange_name, routing_key='', body=result)

        except KeyboardInterrupt:
            print("\nInterrupted by user. Stopping...")
            break
    # Send a message to the 'translate' queue

    # Close the connection
    connection.close()

@app.post("/speak")
async def speak(item: Item):
    # Your existing code to set up and send message
    recognizer, stream = general_set_up(item.language)
    print("Starting to send messages...")
    send_message(recognizer, stream)

    return {"success": True}


if __name__== "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)



    
    
    
