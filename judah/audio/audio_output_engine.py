from RealtimeTTS import SystemEngine, TextToAudioStream


class AudioOutputEngine:
    def __init__(self):
        self._engine = SystemEngine(voice="David")
        self._stream = TextToAudioStream(engine=self._engine)

    def say(self, text_chunk):
        self._stream.feed(text_chunk)
        if not self._stream.is_playing():
            self._stream.play_async(fast_sentence_fragment_allsentences_multiple=True)
