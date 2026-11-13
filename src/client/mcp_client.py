from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


ROOT = Path(__file__).resolve().parents[2]


def _text_from_result(result: Any) -> str:
    parts: list[str] = []
    for item in getattr(result, "content", []) or []:
        text = getattr(item, "text", None)
        if text is not None:
            parts.append(text)
    return "\n".join(parts) if parts else json.dumps(getattr(result, "model_dump", lambda: str(result))(), default=str)


class MCPToolClient:
    """Small stdio MCP client that launches the local server as a child process."""

    def __init__(self) -> None:
        self.params = StdioServerParameters(
            command=sys.executable,
            args=["-m", "src.server.mcp_server"],
            cwd=str(ROOT),
        )

    async def list_tools(self) -> list[dict[str, Any]]:
        async with stdio_client(self.params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.list_tools()
                return [
                    {
                        "name": tool.name,
                        "description": tool.description or "",
                        "inputSchema": tool.inputSchema,
                    }
                    for tool in result.tools
                ]

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> str:
        async with stdio_client(self.params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(name, arguments)
                return _text_from_result(result)

    async def openai_tools(self) -> list[dict[str, Any]]:
        tools = await self.list_tools()
        return [
            {
                "type": "function",
                "function": {
                    "name": t["name"],
                    "description": t["description"],
                    "parameters": t["inputSchema"],
                },
            }
            for t in tools
        ]
