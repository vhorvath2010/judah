import re

import speech_recognition as sr


class AudioInputEngine:
    def __init__(self):
        microphones = sr.Microphone.list_working_microphones()
        print("Working microphones found:")
        for index, name in microphones.items():
            print(f"{index}: {name}")
        microphone_index = int(input("Please select a microphone (by index): "))
        self._microphone = sr.Microphone(device_index=microphone_index)
        print(
            "Adjusting for ambient noise, please do not speak for the next couple of seconds..."
        )
        recognizer = sr.Recognizer()
        with self._microphone as active_microphone:
            recognizer.adjust_for_ambient_noise(source=active_microphone)
        recognizer.pause_threshold = 1
        print("Ambient noise adjustment complete!")
        self._recognizer = recognizer

    def listen_for_user_message(self) -> str:
        with self._microphone as active_microphone:
            user_message = ""
            while not self._is_user_message_valid(user_message=user_message):
                audio = self._recognizer.listen(active_microphone, timeout=None)
                user_message = str(
                    self._recognizer.recognize_whisper(
                        audio, language="english", model="base.en"
                    )
                )
            return user_message

    @staticmethod
    def _is_user_message_valid(user_message: str) -> bool:
        return bool(re.search(r"\w+", user_message))
