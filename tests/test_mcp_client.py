import asyncio

from src.client.agent_loop import AgentLoop
from src.client.mcp_client import MCPToolClient


def test_dynamic_tool_discovery():
    tools = asyncio.run(MCPToolClient().list_tools())
    names = {t["name"] for t in tools}
    assert {"query_sql_database", "get_live_weather", "evaluate_math_expression"} <= names
    assert all(t["inputSchema"].get("type") == "object" for t in tools)


def test_multi_step_chained_loop_terminates(monkeypatch):
    async def fake_call(self, name, arguments):
        if name == "query_sql_database":
            return "order_id | order_value | quantity | sku | city | stock_quantity\n4492 | 1250.0 | 50 | SKU-90210 | Seattle | 80"
        if name == "get_live_weather":
            return "Location: Seattle\nPrecipitation: 0.0 mm"
        if name == "evaluate_math_expression":
            return "43.75"
        raise AssertionError(name)

    monkeypatch.setattr(MCPToolClient, "call_tool", fake_call)
    result = asyncio.run(AgentLoop(max_turns=5).run("Check Seattle order #4492 SKU-90210 and calculate 3.5%", force_demo=True))
    assert len(result["steps"]) == 3
    assert "43.75" in result["answer"]
