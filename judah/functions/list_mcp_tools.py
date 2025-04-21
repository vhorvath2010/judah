# type: ignore
from openai.types.chat import ChatCompletionToolParam

from judah.functions.function_result import FunctionResult
from judah.functions.openai_function import OpenAIFunction

class ListMCPToolsFunction(OpenAIFunction):
    def __init__(self, mcp_connector):
        self._mcp_connector = mcp_connector

    @staticmethod
    def get_description() -> ChatCompletionToolParam:
        return {
            "type": "function",
            "function": {
                "name": "list_mcp_tools",
                "description": "List available tools on the MCP server",
            },
        }

    def invoke(self, arguments: dict) -> FunctionResult:
        tools = self._mcp_connector.list_tools()
        return FunctionResult(context=f"Tools: {tools}")
