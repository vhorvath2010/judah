from judah.openai_connector import OpenAIConnector


class ConversationManager:
    def __init__(self, openai_connector: OpenAIConnector):
        self.openai_connector = openai_connector

    def run_conversation_to_completion(self, starting_user_message: str):
        self._run_user_command(user_message=starting_user_message)
        # TODO: continue running user queries until JUDAH emits an end conversation function call

    def _run_user_command(self, user_message: str):
        print(f"You: {user_message}")
        stream = self.openai_connector.create_completion(
            messages=[{"role": "user", "content": user_message}])
        print("Judah: ", end="")
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                print(chunk.choices[0].delta.content, end="")
        print("\n")
