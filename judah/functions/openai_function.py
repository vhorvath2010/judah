from abc import abstractmethod, ABC

from openai.types.chat import ChatCompletionToolParam

from judah.functions.function_signal import FunctionSignal


class OpenAIFunction(ABC):
    @staticmethod
    @abstractmethod
    def get_description() -> ChatCompletionToolParam:
        """Get the openai tool description for the function"""

    @abstractmethod
    def invoke(self) -> FunctionSignal:
        """Invoke the function"""
