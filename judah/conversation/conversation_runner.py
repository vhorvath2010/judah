import json
from typing import Optional

from openai.types.chat import (
    ChatCompletionMessageParam,
)

from judah.audio.audio_input_engine import AudioInputEngine
from judah.audio.audio_output_engine import AudioOutputEngine
from judah.conversation.prompt_builder import ChatMessageFactory
from judah.functions.function_invoker import FunctionInvoker
from judah.functions.function_result import FunctionSignal, FunctionResult
from judah.connectors.openai_connector import OpenAIConnector

MAX_HISTORY_MESSAGES_FOR_CONTEXT = 10


class ConversationRunner:
    def __init__(
        self,
        openai_connector: OpenAIConnector,
        audio_input_engine: AudioInputEngine,
        audio_output_engine: AudioOutputEngine,
        function_invoker: FunctionInvoker,
    ):
        self._openai_connector = openai_connector
        self._audio_input_engine = audio_input_engine
        self._audio_output_engine = audio_output_engine
        self._function_invoker = function_invoker
        self._history: list[ChatCompletionMessageParam] = []

    def run_conversation_to_completion(self, user_message: str):
        while True:
            command_result = self._run_user_command(user_message=user_message)
            if command_result:
                if command_result.signal == FunctionSignal.STOP_CONVERSATION:
                    print("Goodbye!")
                    self._audio_output_engine.say("Goodbye!")
                    break
                if command_result.context:
                    self._answer_from_context(
                        function_call_context=command_result.context,
                    )
            user_message = self._audio_input_engine.listen_for_user_message()

    def _run_user_command(self, user_message: str) -> Optional[FunctionResult]:
        print(f"You: {user_message}")
        user_message_for_model = ChatMessageFactory.from_user(user_message)
        stream = self._openai_connector.create_completion(
            messages=self._build_messages(current_message=user_message_for_model)
        )
        self._history.append(user_message_for_model)
        print("Judah: ", end="")
        function_name = None
        function_arguments = ""
        for chunk in stream:
            delta = chunk.choices[0].delta
            if delta.content is not None:
                self._audio_output_engine.say(delta.content)
                print(delta.content, end="")
            if delta.tool_calls is not None:
                for tool_call in delta.tool_calls:
                    if tool_call.function.name:
                        function_name = tool_call.function.name
                    if tool_call.function.arguments:
                        function_arguments += tool_call.function.arguments
        if function_name:
            return self._function_invoker.invoke_function_by_name(
                function_name=function_name,
                arguments=(
                    json.loads(function_arguments) if function_arguments else {}
                ),
            )
        print("\n")  # TODO: save J.U.D.A.H.'s message to history
        return None

    def _answer_from_context(self, function_call_context: str):
        function_call_context_for_model = ChatMessageFactory.from_function_call_context(
            function_call_context
        )
        stream = self._openai_connector.create_completion(
            messages=self._build_messages(
                current_message=function_call_context_for_model
            )
        )
        self._history.append(function_call_context_for_model)
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                self._audio_output_engine.say(chunk.choices[0].delta.content)
                print(chunk.choices[0].delta.content, end="")
        print("\n")  # TODO: save J.U.D.A.H.'s message to history

    def _build_messages(
        self,
        current_message=ChatCompletionMessageParam,
    ) -> list[ChatCompletionMessageParam]:
        messages = [
            ChatMessageFactory.get_base_instructions(),
            *self._history[-MAX_HISTORY_MESSAGES_FOR_CONTEXT:],
            current_message,
        ]
        return messages
