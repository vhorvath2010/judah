import speech_recognition as sr


class AudioInputEngine:
    def __init__(self):
        microphones = sr.Microphone.list_microphone_names()
        print("Working microphones found:")
        for i, mic in enumerate(microphones):
            print(f"{i}: {mic}")
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
            audio = self._recognizer.listen(active_microphone, timeout=None)
            result = str(
                self._recognizer.recognize_whisper(
                    audio, language="english", model="small.en"
                )
            )
            while result == "":
                audio = self._recognizer.listen(active_microphone, timeout=None)
                result = str(
                    self._recognizer.recognize_whisper(
                        audio, language="english", model="base.en"
                    )
                )
            return result
