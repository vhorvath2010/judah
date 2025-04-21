# type: ignore
from openai.types.chat import ChatCompletionToolParam

from judah.functions.function_result import FunctionResult
from judah.functions.openai_function import OpenAIFunction

class ListMCPResourcesFunction(OpenAIFunction):
    def __init__(self, mcp_connector):
        self._mcp_connector = mcp_connector

    @staticmethod
    def get_description() -> ChatCompletionToolParam:
        return {
            "type": "function",
            "function": {
                "name": "list_mcp_resources",
                "description": "List available resources on the MCP server",
            },
        }

    def invoke(self, arguments: dict) -> FunctionResult:
        resources = self._mcp_connector.list_resources()
        return FunctionResult(context=f"Resources: {resources}")
