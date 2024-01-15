import vosk
import sys
import os
import pyaudio

# Set up the Vosk model and recognizer
model_path = "/home/briquet/Desktop/Capstone/CapstoneProject/Models/vosk-model-small-en-us-0.15"
if not os.path.exists(model_path):
    print("Please download the model from https://alphacephei.com/vosk/models and unpack as 'model' in the current folder.")
    exit(1)

# Initialize the Vosk recognizer with the model
vosk.SetLogLevel(-1)
recognizer = vosk.KaldiRecognizer(vosk.Model(model_path), 16000)

# Set up audio input from microphone
audio_input = pyaudio.PyAudio()
stream = audio_input.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)

# Process the audio data from microphone
while True:
    data = stream.read(8000)
    if len(data) > 0:
        if recognizer.AcceptWaveform(data):
            result = recognizer.Result()
            print(result)
        else:
            print(recognizer.PartialResult())

# Cleanup
stream.stop_stream()
stream.close()
audio_input.terminate()
