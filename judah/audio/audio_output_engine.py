import pyttsx3


class AudioOutputEngine:
    def __init__(self):
        self._engine = pyttsx3.init()

    def say(self, text):
        self._engine.say(text)
        self._engine.runAndWait()
