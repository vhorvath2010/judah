from typing import Optional

from judah.audio.audio_input_engine import AudioInputEngine
from judah.functions.function_invoker import FunctionInvoker
from judah.functions.function_signal import FunctionSignal
from judah.openai_connector import OpenAIConnector


class ConversationRunner:
    def __init__(self, openai_connector: OpenAIConnector, audio_input_engine: AudioInputEngine,
                 function_invoker: FunctionInvoker):
        self._openai_connector = openai_connector
        self._audio_input_engine = audio_input_engine
        self._function_invoker = function_invoker

    def run_conversation_to_completion(self, starting_user_message: str):
        self._run_user_command(user_message=starting_user_message)
        while True:
            user_message = self._audio_input_engine.listen_for_user_message()
            command_result = self._run_user_command(user_message=user_message)
            if command_result == FunctionSignal.STOP_CONVERSATION:
                print("Judah: Goodbye!")
                break

    def _run_user_command(self, user_message: str) -> Optional[FunctionSignal]:
        print(f"You: {user_message}")
        stream = self._openai_connector.create_completion(
            messages=[{"role": "user", "content": user_message}])
        print("Judah: ", end="")
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                print(chunk.choices[0].delta.content, end="")
            if chunk.choices[0].delta.tool_calls is not None:
                for tool_call in chunk.choices[0].delta.tool_calls:
                    return self._function_invoker.invoke_function_by_name(tool_call.function.name)
        print("\n")
