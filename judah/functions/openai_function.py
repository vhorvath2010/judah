from abc import abstractmethod, ABC

from openai.types.chat import ChatCompletionToolParam

from judah.functions.function_result import FunctionResult


class OpenAIFunction(ABC):
    @staticmethod
    @abstractmethod
    def get_description() -> ChatCompletionToolParam:
        """Get the openai tool description for the function"""

    @abstractmethod
    def invoke(self, arguments: dict) -> FunctionResult:
        """Invoke the function"""
