import requests
import json
from spellchecker import SpellChecker

URL = "http://localhost:5000/translate"

spell = SpellChecker(language='en')  # English dictionary

def InputText():
    variable = input("Please input text to be translated : ")
    # words = variable.split()
    # corrected_words = str([spell.correction(word) for word in words])
    # corrected_text = " ".join(corrected_words)
    return variable
def main():
    while True :  
        text_to_translate = InputText()
    
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
        
        else:
            print("Failed to translate. Status code:", response.status_code)
        
        print("-----------------------------------")
        
        break

if __name__== "__main__":
    main()