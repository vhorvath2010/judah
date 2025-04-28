import json
import logging
from typing import Optional, List

from openai.types.chat import (
    ChatCompletionMessageParam,
    ChatCompletionAssistantMessageParam,
    ChatCompletionToolMessageParam,
)

from judah.audio.audio_input_engine import AudioInputEngine
from judah.audio.audio_output_engine import AudioOutputEngine
from judah.conversation.prompt_builder import ChatMessageFactory
from judah.functions.function_invoker import FunctionInvoker
from judah.functions.function_result import FunctionSignal, FunctionResult
from judah.connectors.openai_connector import OpenAIConnector

MAX_HISTORY_MESSAGES_FOR_CONTEXT = 25


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
        self._history.clear()
        current_user_message: Optional[str] = user_message
        while True:
            if not current_user_message:
                current_user_message = (
                    self._audio_input_engine.listen_for_user_message()
                )
                self._audio_output_engine.force_stop()

            stop_signal = self._run_interaction(user_message=current_user_message)
            if stop_signal:
                print("Goodbye!")
                self._audio_output_engine.say("Goodbye!")
                break
            # Reset user message for the next loop iteration to listen again
            current_user_message = None

    def _run_interaction(self, user_message: str) -> bool:
        """Runs a single user message interaction, including potential tool calls and responses."""
        print(f"You: {user_message}")
        user_message_for_model = ChatMessageFactory.from_user(user_message)
        self._history.append(user_message_for_model)

        messages_for_api = self._build_messages(current_message=user_message_for_model)

        # --- First LLM Call (User Message -> Assistant Response/Tool Call) ---
        stream = self._openai_connector.create_completion(messages=messages_for_api)

        print("Judah: ", end="", flush=True)
        message_from_judah = ""
        tool_calls_to_make = []

        for chunk in stream:
            delta = chunk.choices[0].delta
            if delta.content is not None:
                self._audio_output_engine.say(delta.content)
                message_from_judah += delta.content
                print(delta.content, end="", flush=True)
            if delta.tool_calls:
                for tool_call_chunk in delta.tool_calls:
                    # Ensure list is long enough
                    while len(tool_calls_to_make) <= tool_call_chunk.index:
                        tool_calls_to_make.append(
                            {
                                "id": None,
                                "function": {"name": "", "arguments": ""},
                                "type": "function",
                            }
                        )
                    current_tool = tool_calls_to_make[tool_call_chunk.index]
                    if tool_call_chunk.id:
                        current_tool["id"] = tool_call_chunk.id
                    if tool_call_chunk.function:
                        if tool_call_chunk.function.name:
                            current_tool["function"][
                                "name"
                            ] += tool_call_chunk.function.name
                        if tool_call_chunk.function.arguments:
                            current_tool["function"][
                                "arguments"
                            ] += tool_call_chunk.function.arguments
        print("\n")

        # --- Store Assistant's Response (Text or Tool Call Intent) ---
        assistant_message: Optional[ChatCompletionAssistantMessageParam] = None
        if message_from_judah or tool_calls_to_make:
            assistant_message = {
                "role": "assistant",
                "content": message_from_judah if message_from_judah else None,
            }
            if tool_calls_to_make:
                # Filter out incomplete tool calls just in case
                valid_tool_calls = [
                    tc
                    for tc in tool_calls_to_make
                    if tc.get("id") and tc["function"].get("name")
                ]
                if valid_tool_calls:
                    assistant_message["tool_calls"] = valid_tool_calls

            if assistant_message.get("content") or assistant_message.get("tool_calls"):
                self._history.append(assistant_message)
        else:
            logging.warning("LLM stream finished without content or tool calls.")

        # --- Execute Tool Calls and Collect Results ---
        tool_results: List[ChatCompletionToolMessageParam] = []
        stop_conversation_signal = False

        if (
            tool_calls_to_make
            and assistant_message
            and assistant_message.get("tool_calls")
        ):
            print("Processing function calls...", flush=True)
            for tool_call in assistant_message["tool_calls"]:
                function_name = tool_call["function"]["name"]
                tool_call_id = tool_call["id"]
                try:
                    arguments_str = tool_call["function"]["arguments"]
                    arguments = json.loads(arguments_str) if arguments_str else {}
                    logging.info(
                        f"Invoking tool: {function_name} with args: {arguments}"
                    )
                    result: Optional[FunctionResult] = (
                        self._function_invoker.invoke_function_by_name(
                            function_name=function_name,
                            arguments=arguments,
                        )
                    )

                    if result:
                        logging.info(
                            f"Tool {function_name} result: Signal={result.signal}, Context={bool(result.context)}"
                        )
                        tool_results.append(
                            {
                                "tool_call_id": tool_call_id,
                                "role": "tool",
                                "name": function_name,
                                "content": result.context
                                or "Function executed successfully.",  # Provide some content even if context is None
                            }
                        )

                        if result.signal == FunctionSignal.STOP_CONVERSATION:
                            stop_conversation_signal = True
                            break
                    else:
                        logging.warning(
                            f"Tool {function_name} did not return a result."
                        )
                        tool_results.append(
                            {
                                "tool_call_id": tool_call_id,
                                "role": "tool",
                                "name": function_name,
                                "content": "Function did not return specific data.",
                            }
                        )

                except json.JSONDecodeError as e:
                    logging.error(
                        f"Error parsing arguments for {function_name}: {e}. Args: '{arguments_str}'"
                    )
                    tool_results.append(
                        {
                            "tool_call_id": tool_call_id,
                            "role": "tool",
                            "name": function_name,
                            "content": f"Error: Could not parse arguments - {e}",
                        }
                    )
                except Exception as e:
                    logging.error(f"Error invoking tool {function_name}: {e}")
                    tool_results.append(
                        {
                            "tool_call_id": tool_call_id,
                            "role": "tool",
                            "name": function_name,
                            "content": f"Error: Failed to execute function - {e}",
                        }
                    )

            # If we need to stop, return True now
            if stop_conversation_signal:
                return True

        # --- Second LLM Call (If Tools Were Called) ---
        if tool_results:
            self._history.extend(tool_results)  # Add tool results to history
            messages_for_final_response = (
                self._build_messages()
            )  # Build messages including tool results

            print("Judah: ", end="", flush=True)
            final_stream = self._openai_connector.create_completion(
                messages=messages_for_final_response
            )
            final_message_from_judah = ""
            for chunk in final_stream:
                delta = chunk.choices[0].delta
                if delta.content is not None:
                    self._audio_output_engine.say(delta.content)
                    final_message_from_judah += delta.content
                    print(delta.content, end="", flush=True)
            print("\n")

            if final_message_from_judah:
                self._history.append(
                    ChatMessageFactory.from_judah(final_message_from_judah)
                )
            else:
                # Handle cases where the second LLM call doesn't produce text
                logging.warning(
                    "LLM stream after tool execution finished without content."
                )
                # You might want to generate a generic confirmation here
                confirmation = "OK, I've processed the request."
                print(f"Judah: {confirmation}\n")
                self._audio_output_engine.say(confirmation)
                self._history.append(ChatMessageFactory.from_judah(confirmation))
        # Return False to indicate conversation should continue
        return False

    def _build_messages(
        self,
        current_message: Optional[ChatCompletionMessageParam] = None,
    ) -> list[ChatCompletionMessageParam]:
        messages = [
            ChatMessageFactory.get_base_instructions(),
            *self._history[
                -(MAX_HISTORY_MESSAGES_FOR_CONTEXT - 1) :
            ],  # Adjust slice if adding current_message
        ]
        if current_message:
            messages.append(current_message)

        total_messages = len(messages)
        if (
            total_messages > MAX_HISTORY_MESSAGES_FOR_CONTEXT + 1
        ):  # +1 for system prompt
            excess = total_messages - (MAX_HISTORY_MESSAGES_FOR_CONTEXT + 1)
            messages = [messages[0]] + messages[1 + excess :]

        return messages
