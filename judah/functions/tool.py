from abc import abstractmethod, ABC

from openai.types.chat import ChatCompletionToolParam

from judah.functions.function_result import FunctionResult


class Tool(ABC):
    @abstractmethod
    def get_openai_description() -> ChatCompletionToolParam:
        """Get the OpenAI function description for this tool"""

    @abstractmethod
    def invoke(self, arguments: dict) -> FunctionResult:
        """Invoke the function"""

    # Example of how this could be extended to support other providers
    def get_claude_description(self) -> dict:
        """Get the Claude tool description for this tool"""
        raise NotImplementedError("Claude description not implemented for this tool")
