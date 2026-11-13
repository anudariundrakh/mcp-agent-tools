from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from src.server.tools.math_tool import calculate_expression
from src.server.tools.sql_tool import query_database
from src.server.tools.weather_tool import get_current_weather


mcp = FastMCP("Enterprise Operations MCP")


@mcp.tool()
def query_sql_database(sql_query: str) -> str:
    """Run one read-only SELECT against the enterprise SQLite database. Never writes data."""
    try:
        return query_database(sql_query)
    except Exception as exc:
        return f"SECURITY_REJECTION: {exc}"


@mcp.tool()
async def get_live_weather(city: str) -> str:
    """Get current temperature, precipitation, rain, weather code, and wind for a city."""
    try:
        return await get_current_weather(city)
    except Exception as exc:
        return f"TOOL_ERROR: {exc}"


@mcp.tool()
def evaluate_math_expression(expression: str) -> str:
    """Evaluate safe arithmetic with a Python AST whitelist; eval/exec are never used."""
    try:
        return calculate_expression(expression)
    except Exception as exc:
        return f"SECURITY_REJECTION: {exc}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
