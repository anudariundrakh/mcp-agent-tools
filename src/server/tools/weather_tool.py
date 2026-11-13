from __future__ import annotations

import html

import httpx


GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"


class WeatherToolError(RuntimeError):
    pass


async def get_current_weather(city: str, client: httpx.AsyncClient | None = None) -> str:
    """Fetch sanitized current conditions from Open-Meteo for a normalized city name."""
    clean_city = " ".join(city.strip().split())[:100]
    if not clean_city:
        raise WeatherToolError("City is required")

    owns_client = client is None
    if owns_client:
        client = httpx.AsyncClient(
    timeout=httpx.Timeout(20.0, connect=20.0),
    follow_redirects=False,
)
    assert client is not None

    try:
        geo = await client.get(GEOCODE_URL, params={"name": clean_city, "count": 1, "language": "en", "format": "json"})
        geo.raise_for_status()
        results = geo.json().get("results") or []
        if not results:
            raise WeatherToolError("City was not found")
        place = results[0]
        lat, lon = float(place["latitude"]), float(place["longitude"])

        wx = await client.get(
            FORECAST_URL,
            params={
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,precipitation,rain,weather_code,wind_speed_10m",
                "timezone": "auto",
            },
        )
        wx.raise_for_status()
        current = wx.json().get("current") or {}
        name = html.escape(str(place.get("name", clean_city)), quote=False)
        country = html.escape(str(place.get("country", "")), quote=False)
        return (
            f"Location: {name}, {country}\n"
            f"Temperature: {current.get('temperature_2m')} °C\n"
            f"Precipitation: {current.get('precipitation')} mm\n"
            f"Rain: {current.get('rain')} mm\n"
            f"Wind: {current.get('wind_speed_10m')} km/h\n"
            f"Weather code: {current.get('weather_code')}"
        )
    except (httpx.HTTPError, ValueError, KeyError) as exc:
        raise WeatherToolError("Weather service request failed safely") from exc
    finally:
        if owns_client:
            await client.aclose()
