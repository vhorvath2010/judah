import asyncio
from mcp import ClientSession, StdioServerParameters

class MCPConnector:
    def __init__(self, command: str, args: list[str] = None, env: dict[str, str] = None):
        params = StdioServerParameters(command=command, args=args or [], env=env)
        self._session = asyncio.run(ClientSession.create(params))

    def list_resources(self) -> list:
        """List available resources on the MCP server"""
        return asyncio.run(self._session.list_resources())

    def list_tools(self) -> list:
        """List available tools on the MCP server"""
        return asyncio.run(self._session.list_tools())

    def call_tool(self, tool_name: str, arguments: dict) -> any:
        """Call a named tool on the MCP server with given arguments"""
        return asyncio.run(self._session.call_tool(tool_name, arguments=arguments))
