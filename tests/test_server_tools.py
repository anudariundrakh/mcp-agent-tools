import asyncio

import httpx

from src.server.tools.math_tool import calculate_expression
from src.server.tools.sql_tool import query_database
from src.server.tools.weather_tool import get_current_weather


def test_sql_read_accuracy():
    out = query_database("SELECT id, order_value FROM orders WHERE id = 4492")
    assert "4492" in out
    assert "1250" in out


def test_math_evaluator_precision():
    assert calculate_expression("2 + 3 * (4 - 1) ** 2") == "29"


def test_weather_api_integration_mocked():
    def handler(request: httpx.Request) -> httpx.Response:
        if "geocoding" in str(request.url):
            return httpx.Response(200, json={"results": [{"name": "Seattle", "country": "United States", "latitude": 47.61, "longitude": -122.33}]})
        return httpx.Response(200, json={"current": {"temperature_2m": 10.5, "precipitation": 0.2, "rain": 0.2, "weather_code": 61, "wind_speed_10m": 8.0}})

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await get_current_weather("Seattle", client=client)

    out = asyncio.run(run())
    assert "Seattle" in out and "10.5" in out and "0.2" in out
