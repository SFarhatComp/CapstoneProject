import time
import pika
import threading
import os
import vosk
import asyncio
import pyaudio
from fastapi import FastAPI
from pydantic import BaseModel
from starlette.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

status_var = False

recognizer, stream , exchange_name, chanel = None, None, None, None


origins = [
    "http://localhost:5173",  # Replace with the origin of your frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Item(BaseModel):

    name : str
    language: str



def general_set_up():
    
    # Set up the Vosk model and recognizer
    model_path = "Models/vosk-model-small-en-us-0.15"
    
    if not os.path.exists(model_path):
        print("Please download the model from https://alphacephei.com/vosk/models and unpack as 'model' in the current folder.")
        exit(1) 
    
    # Initialize the Vosk recognizer with the model
    vosk.SetLogLevel(-1)
    recognizer = vosk.KaldiRecognizer(vosk.Model(model_path), 16000)

    # Set up audio input from microphone
    audio_input = pyaudio.PyAudio()
    stream = audio_input.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=2000)

    # Establish a connection with RabbitMQ server
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    # Declare the exchange (this will only create it if it doesn't already exist)
    exchange_name = 'translate_exchange'
    channel.exchange_declare(exchange=exchange_name, exchange_type='fanout')

    return recognizer, stream, exchange_name, channel

def send_message(recognizer, stream , exchange_name, channel):
    
    while status_var:
        try:
            # This is mic 
            data = stream.read(2000)         
            if len(data) > 0:
                if recognizer.AcceptWaveform(data):
                    result = recognizer.Result()
                    print(result)
                    # Sending a message to the Exchange
                    channel.basic_publish(exchange=exchange_name,routing_key='', body=result)

        except KeyboardInterrupt:
            print("\nInterrupted by user. Stopping...")
            break
    # Send a message to the 'translate' queue
    print("Closing the connection")
    


active_speaker = None
@app.post("/speak")
async def speak(item: Item):
    global status_var
    global active_speaker
    if not status_var:
        print("Received request to speak from {item.name}")
        active_speaker = item.name
        print("Buffer cleared")
        stream.stop_stream()
        stream.start_stream()
        status_var = True 
        thread = threading.Thread(target=send_message, args=(recognizer, stream , exchange_name, chanel))
        thread.start()
        
    else:
        print("Stopping to send messages...")
        status_var = False

    return {"success": True}


@app.get("/stream_speaker/")
async def stream_speaker():
    async def event_stream():
        while True:
            if active_speaker is not None:
                yield f"data: {active_speaker}\n\n"
            await asyncio.sleep(1)

    return StreamingResponse(event_stream(), media_type="text/event-stream")



def main():
    global recognizer, stream , exchange_name, chanel
    recognizer, stream , exchange_name, chanel = general_set_up()
    import uvicorn
    uvicorn.run(app, host="10.0.0.100", port=8000)

if __name__== "__main__":
    main()
    
    
    



