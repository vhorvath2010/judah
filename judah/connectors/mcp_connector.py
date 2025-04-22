from dataclasses import dataclass
import asyncio
from typing import Any, Dict, List
from mcp import ClientSession, StdioServerParameters
from openai.types.chat import ChatCompletionToolParam


@dataclass
class ServerConfig:
    name: str
    command: str
    args: List[str] = None
    env: Dict[str, str] = None


class MCPConnector:
    def __init__(self, configs: List[ServerConfig] = None):
        configs = configs or [
            ServerConfig(name="default", command="mcp", args=[], env=None)
        ]
        self._sessions: Dict[str, ClientSession] = {}
        for cfg in configs:
            params = StdioServerParameters(
                command=cfg.command, args=cfg.args or [], env=cfg.env
            )
            session = asyncio.run(ClientSession.create(params))
            self._sessions[cfg.name] = session

    def list_resources(self) -> Dict[str, Any]:
        """List available resources on all MCP servers"""
        return {
            name: asyncio.run(sess.list_resources())
            for name, sess in self._sessions.items()
        }

    def list_tools(self) -> Dict[str, Any]:
        """List available tools on all MCP servers"""
        return {
            name: asyncio.run(sess.list_tools())
            for name, sess in self._sessions.items()
        }

    def call_tool(self, server_name: str, tool_name: str, arguments: dict) -> Any:
        """Call a named tool on the specified MCP server"""
        session = self._sessions.get(server_name)
        if not session:
            raise ValueError(f"MCP server '{server_name}' not found")
        return asyncio.run(session.call_tool(tool_name, arguments=arguments))

    def get_openai_function_descriptions(self) -> list[ChatCompletionToolParam]:
        """Transform available MCP tools into OpenAI function definitions"""
        descriptions: list[ChatCompletionToolParam] = []
        for server_name, session in self._sessions.items():
            tools = asyncio.run(session.list_tools())
            for tool in tools:
                # assume tool has name, description, and parameters attributes
                descriptions.append(
                    {
                        "type": "function",
                        "function": {
                            "name": f"{server_name}_{tool.name}",
                            "description": tool.description,
                            "parameters": getattr(tool, "parameters", {}),
                            "strict": True,
                        },
                    }
                )
        return descriptions
