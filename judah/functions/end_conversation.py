from openai.types.chat import ChatCompletionToolParam

from judah.functions.function_result import FunctionSignal, FunctionResult
from judah.functions.openai_function import OpenAIFunction


class EndConversationFunction(OpenAIFunction):
    @staticmethod
    def get_description() -> ChatCompletionToolParam:
        return {
            "type": "function",
            "function": {
                "name": "end_conversation",
                "description": "Should be called when the user says they want to end the conversation",
            },
        }

    def invoke(self, arguments: dict) -> FunctionResult:
        return FunctionResult(signal=FunctionSignal.STOP_CONVERSATION)
