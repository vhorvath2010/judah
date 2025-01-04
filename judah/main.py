import logging
from time import sleep
import warnings

import speech_recognition as sr
from speech_recognition import Microphone, Recognizer

from judah.dependencies import openai_connector

logging.basicConfig(level=logging.INFO)
warnings.filterwarnings("ignore", category=FutureWarning)  # Ignore annoying PyTorch warning from Whisper


def select_microphone():
    microphones = sr.Microphone.list_microphone_names()
    print("Working microphones found:")
    for i, mic in enumerate(microphones):
        print(f"{i}: {mic}")
    microphone_index = int(input("Please select a microphone (by index): "))
    return sr.Microphone(device_index=microphone_index)


def setup_voice_recognizer(microphone: Microphone):
    recognizer = sr.Recognizer()
    recognizer.adjust_for_ambient_noise(microphone)
    recognizer.pause_threshold = 1.5
    sleep(1)  # Wait for the recognizer to adjust to the ambient noise
    return recognizer


def get_next_command(recognizer: Recognizer, microphone: Microphone):
    while True:
        try:
            audio = recognizer.listen(microphone, timeout=None)
            result = str(recognizer.recognize_whisper(
                audio, language="english", model="base.en"
            ))
            if "judah" in result.lower():
                return result
        except sr.UnknownValueError:
            print("Whisper could not understand the audio.")
        except sr.RequestError as e:
            print(f"Could not request results from Whisper; {e}")
        except KeyboardInterrupt:
            print("\nExiting...")
            break


if __name__ == '__main__':
    with select_microphone() as user_microphone:
        voice_recognizer = setup_voice_recognizer(user_microphone)
        print(
            'J.U.D.A.H. is active! Speak into the selected microphone using the "Judah" wake word anywhere in your commands.')
        while True:
            command = get_next_command(recognizer=voice_recognizer, microphone=user_microphone)
            print(f"You: {command}")
            stream = openai_connector.create_completion(
                messages=[{"role": "user", "content": command}])
            print("Judah: ", end="")
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    print(chunk.choices[0].delta.content, end="")
            print("\n")
