import asyncio
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters, stdio_client


class MCPConnector:
    def __init__(self):
        self.sessions: list[ClientSession] = []
        self.exit_stack = AsyncExitStack

    def connect_to_server(self, server_params: StdioServerParameters):
        """
        Connect to a server using the given parameters.
        """
        stdio, write = self.exit_stack.enter_context(stdio_client(server_params))
        session: ClientSession = self.exit_stack.enter_context(
            ClientSession(stdio, write)
        )
        self.sessions.append(session)

        res = asyncio.run(session.list_tools())
        tools = res.tools
        print("\nConnected to server with tools:", [tool.name for tool in tools])
