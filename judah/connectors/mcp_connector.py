import asyncio
from contextlib import AsyncExitStack
from typing import Dict, Type, Any

from mcp import ClientSession, StdioServerParameters, stdio_client, Tool

from judah.functions.function_result import FunctionResult
from judah.functions.openai_function import OpenAIFunction
from openai.types.chat import ChatCompletionToolParam


class MCPFunctionGenerator:
    """Dynamically generates OpenAIFunction classes for MCP tools."""

    @staticmethod
    def generate_function_class(
        session: ClientSession, tool: Tool
    ) -> Type[OpenAIFunction]:
        """
        Generate an OpenAIFunction class for a specific MCP tool.
        Args:
            session: The MCP client session
            tool: The tool description from MCP
        Returns:
            A new OpenAIFunction class for the tool
        """
        class_name = f"{tool.name.title().replace('-', '_').replace(' ', '_')}Function"

        # Convert MCP tool inputSchema to OpenAI function parameters
        parameters = {"type": "object", "properties": {}, "required": []}

        # The tool.inputSchema contains the schema specification
        if hasattr(tool, "inputSchema") and tool.inputSchema:
            if "properties" in tool.inputSchema:
                parameters["properties"] = tool.inputSchema["properties"]

            if "required" in tool.inputSchema:
                parameters["required"] = tool.inputSchema["required"]

        def create_init(session_param, tool_param):
            def __init__(self):
                self._session = session_param
                self._tool = tool_param

            return __init__

        def create_get_description(tool_param, params):
            def get_description(cls) -> ChatCompletionToolParam:
                return {
                    "type": "function",
                    "function": {
                        "name": tool_param.name,
                        "description": tool_param.description
                        or f"Tool: {tool_param.name}",
                        "parameters": params,
                    },
                }

            return classmethod(get_description)

        def create_invoke(session_param, tool_param):
            def invoke(self, arguments: Dict[str, Any]) -> FunctionResult:
                return MCPFunctionGenerator._invoke_tool(
                    session_param, tool_param, arguments
                )

            return invoke

        class_dict = {
            "__init__": create_init(session, tool),
            "get_description": create_get_description(tool, parameters),
            "invoke": create_invoke(session, tool),
        }

        return type(class_name, (OpenAIFunction,), class_dict)

    @staticmethod
    def _invoke_tool(
        session: ClientSession, tool: Tool, arguments: Dict[str, Any]
    ) -> FunctionResult:
        """
        Invoke an MCP tool and return the result.
        Args:
            session: The MCP client session
            tool: The tool to invoke
            arguments: The arguments to pass to the tool
        Returns:
            A FunctionResult with the tool's output
        """
        loop = asyncio.get_event_loop()

        try:
            result = loop.run_until_complete(session.call_tool(tool.name, arguments))
            return FunctionResult(
                signal=None,
                context=str(result.content),
            )
        except Exception as e:
            return FunctionResult(signal=None, context=str(e))


class MCPConnector:
    def __init__(self):
        self._sessions: list[ClientSession] = []
        self._exit_stack = None
        self._loop = None
        self._function_classes: Dict[str, Type[OpenAIFunction]] = {}

    async def _setup_exit_stack(self):
        self._exit_stack = AsyncExitStack()
        return self._exit_stack

    async def connect_to_server_async(self, server_params: StdioServerParameters):
        """
        Connect to a server using the given parameters (async version).
        """
        if self._exit_stack is None:
            self._exit_stack = await self._setup_exit_stack()

        stdio, write = await self._exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        session = await self._exit_stack.enter_async_context(
            ClientSession(stdio, write)
        )
        self._sessions.append(session)

        res = await session.list_tools()
        tools = res.tools
        print("\nConnected to server with tools:", [tool.name for tool in tools])

        # Generate function classes for each tool
        for tool in tools:
            function_class = MCPFunctionGenerator.generate_function_class(session, tool)
            self._function_classes[tool.name] = function_class

        return session

    def connect_to_server(self, server_params: StdioServerParameters):
        """
        Synchronous wrapper for connect_to_server_async.
        """
        if self._loop is None:
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)

        return self._loop.run_until_complete(
            self.connect_to_server_async(server_params)
        )

    async def get_functions_async(self) -> list[OpenAIFunction]:
        """
        Create and return OpenAIFunction instances for all available tools.
        """
        functions = []
        for session in self._sessions:
            tools_response = await session.list_tools()
            for tool in tools_response.tools:
                # Get the function class for this tool
                function_class = self._function_classes.get(tool.name)
                if function_class:
                    # Instantiate the function
                    function_instance = function_class()
                    functions.append(function_instance)

        return functions

    def get_functions(self) -> list[OpenAIFunction]:
        """Synchronous wrapper for get_functions_async."""
        if self._loop is None:
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)

        return self._loop.run_until_complete(self.get_functions_async())

    async def close_async(self):
        """Close all sessions and the exit stack."""
        if self._exit_stack:
            await self._exit_stack.aclose()
            self._exit_stack = None

    def close(self):
        """Synchronous wrapper for close_async."""
        if self._loop:
            self._loop.run_until_complete(self.close_async())
            self._loop.close()
            self._loop = None
