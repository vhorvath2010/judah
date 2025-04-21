# type: ignore
from openai.types.chat import ChatCompletionToolParam

from judah.functions.function_result import FunctionResult
from judah.functions.openai_function import OpenAIFunction

class CallMCPToolFunction(OpenAIFunction):
    def __init__(self, mcp_connector):
        self._mcp_connector = mcp_connector

    @staticmethod
    def get_description() -> ChatCompletionToolParam:
        return {
            "type": "function",
            "function": {
                "name": "call_mcp_tool",
                "description": "Call a tool on the MCP server with specific arguments",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "tool_name": {"type": "string"},
                        "arguments": {"type": "object"}
                    },
                    "required": ["tool_name", "arguments"],
                    "additionalProperties": False
                },
                "strict": True
            },
        }

    def invoke(self, arguments: dict) -> FunctionResult:
        result = self._mcp_connector.call_tool(
            tool_name=arguments["tool_name"],
            arguments=arguments.get("arguments", {})
        )
        return FunctionResult(context=f"Result: {result}")
