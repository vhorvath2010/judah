from judah.audio.audio_input_engine import AudioInputEngine
from judah.openai_connector import OpenAIConnector


class ConversationRunner:
    def __init__(self, openai_connector: OpenAIConnector, audio_input_engine: AudioInputEngine):
        self._openai_connector = openai_connector
        self._audio_input_engine = audio_input_engine

    def run_conversation_to_completion(self, starting_user_message: str):
        self._run_user_command(user_message=starting_user_message)
        while True:
            user_message = self._audio_input_engine.listen_for_user_message()
            if "exit" in user_message.lower():  # TODO: Replace with dynamic OpenAI "exit conversation" function call
                print("Judah: Goodbye!")
                break
            self._run_user_command(user_message=user_message)

    def _run_user_command(self, user_message: str):
        print(f"You: {user_message}")
        stream = self._openai_connector.create_completion(
            messages=[{"role": "user", "content": user_message}])
        print("Judah: ", end="")
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                print(chunk.choices[0].delta.content, end="")
        print("\n")
