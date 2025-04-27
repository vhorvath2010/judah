import asyncio
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters, stdio_client


class MCPConnector:
    def __init__(self):
        self._sessions = []
        self._exit_stack = None
        self._loop = None

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
