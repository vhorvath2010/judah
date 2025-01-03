import logging
import warnings

import speech_recognition as sr

logging.basicConfig(level=logging.INFO)
# Ignore annoying PyTorch warning from Whisper
warnings.filterwarnings("ignore", category=FutureWarning)

microphones = sr.Microphone().list_working_microphones()
print("Working microphones found: ", microphones)
microphone_index = int(input("Please select a microphone:"))

recognizer = sr.Recognizer()
with sr.Microphone(device_index=microphone_index) as source:
    logging.info("Say something!")
    audio = recognizer.listen(source)
    try:
        print(
            "Whisper thinks you said:",
            recognizer.recognize_whisper(audio, language="english", model="base.en"),
        )
    except sr.UnknownValueError:
        print("Whisper could not understand audio")
    except sr.RequestError as e:
        print(f"Could not request results from Whisper; {e}")
