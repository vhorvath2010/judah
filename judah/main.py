import logging
from time import sleep
import warnings

import speech_recognition as sr

logging.basicConfig(level=logging.INFO)
# Ignore annoying PyTorch warning from Whisper
warnings.filterwarnings("ignore", category=FutureWarning)

microphones = sr.Microphone.list_microphone_names()
print("Working microphones found:")
for i, mic in enumerate(microphones):
    print(f"{i}: {mic}")
microphone_index = int(input("Please select a microphone (by index): "))

recognizer = sr.Recognizer()
try:
    with sr.Microphone(device_index=microphone_index) as source:
        recognizer.adjust_for_ambient_noise(source)
        recognizer.pause_threshold = 1.5
        sleep(1)  # Wait for the recognizer to adjust to the ambient noise
        logging.info("Listening... Speak into the microphone.")
        # Continuous listening
        while True:
            try:
                logging.info("Listening for a phrase...")
                audio = recognizer.listen(source, timeout=None)
                result = recognizer.recognize_whisper(
                    audio, language="english", model="base.en"
                )
                print("Whisper thinks you said:", result)
            except sr.UnknownValueError:
                print("Whisper could not understand the audio.")
            except sr.RequestError as e:
                print(f"Could not request results from Whisper; {e}")
            except KeyboardInterrupt:
                print("\nExiting...")
                break

except Exception as e:
    logging.error(f"An error occurred: {e}")
