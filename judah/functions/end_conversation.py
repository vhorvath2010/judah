from openai.types.chat import ChatCompletionToolParam

from judah.functions.function_signal import FunctionSignal
from judah.functions.openai_function import OpenAIFunction


class EndConversationFunction(OpenAIFunction):
    @staticmethod
    def get_description() -> ChatCompletionToolParam:
        return {
            "type": "function",
            "function": {
                "name": "end_conversation",
                "description": "Ends the current conversation with the user. Should be called either when the user asks to end the conversation or the conversation has reached a natural conclusion.",
            }
        }

    def invoke(self):
        return FunctionSignal.STOP_CONVERSATION
