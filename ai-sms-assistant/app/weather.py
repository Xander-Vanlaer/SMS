import math
import os
import re
from collections import defaultdict
from datetime import datetime, timezone

import httpx

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
OPENWEATHER_BASE_URL = "https://api.openweathermap.org"

WEATHER_HELP = (
    "Weather usage:\n"
    "  weather brussels\n"
    "  weather 3 days brussels\n"
)


def _parse_weather_query(text: str):
    """Return (days, city) or None if the text doesn't match a weather command."""
    m = re.match(
        r"^\s*weather(?:\s+(\d+)\s*(?:day|days))?\s+(.+?)\s*$",
        text,
        re.IGNORECASE,
    )
    if not m:
        return None
    days = int(m.group(1)) if m.group(1) else 1
    days = max(1, min(days, 5))
    city = m.group(2).strip()
    return days, city


async def _geocode_city(client: httpx.AsyncClient, city: str):
    url = f"{OPENWEATHER_BASE_URL}/geo/1.0/direct"
    r = await client.get(
        url,
        params={"q": city, "limit": 1, "appid": OPENWEATHER_API_KEY},
        timeout=20,
    )
    r.raise_for_status()
    data = r.json()
    if not data:
        return None
    return data[0]


async def _forecast(client: httpx.AsyncClient, lat: float, lon: float):
    url = f"{OPENWEATHER_BASE_URL}/data/2.5/forecast"
    r = await client.get(
        url,
        params={
            "lat": lat,
            "lon": lon,
            "appid": OPENWEATHER_API_KEY,
            "units": "metric",
        },
        timeout=20,
    )
    r.raise_for_status()
    return r.json()


def _summarize_forecast(forecast_json: dict, days: int, place_label: str) -> str:
    items = forecast_json.get("list", [])
    if not items:
        return f"No forecast data found for {place_label}."

    by_date: dict = defaultdict(list)
    for it in items:
        dt = datetime.fromtimestamp(it["dt"], tz=timezone.utc)
        by_date[dt.date().isoformat()].append(it)

    dates = sorted(by_date.keys())[:days]
    lines = [f"Forecast for {place_label} ({len(dates)} day(s)):"]
    for d in dates:
        temps = [
            x["main"]["temp"]
            for x in by_date[d]
            if "main" in x and "temp" in x["main"]
        ]
        descs = [x["weather"][0]["description"] for x in by_date[d] if x.get("weather")]
        tmin = math.floor(min(temps)) if temps else None
        tmax = math.ceil(max(temps)) if temps else None
        desc = max(set(descs), key=descs.count) if descs else "n/a"
        if tmin is not None and tmax is not None:
            lines.append(f"{d}: {desc}, {tmin}-{tmax}C")
        else:
            lines.append(f"{d}: {desc}")
    return "\n".join(lines)


async def handle_weather(text: str) -> str:
    if not OPENWEATHER_API_KEY:
        return "Server missing OPENWEATHER_API_KEY. Ask admin to configure it."

    parsed = _parse_weather_query(text)
    if not parsed:
        return WEATHER_HELP

    days, city = parsed

    async with httpx.AsyncClient() as client:
        geo = await _geocode_city(client, city)
        if not geo:
            return f"Could not find location '{city}'. Try e.g. 'weather brussels'."

        lat, lon = geo["lat"], geo["lon"]
        name = geo.get("name", city)
        country = geo.get("country", "").strip()
        place = f"{name}, {country}".strip().strip(",") if country else name

        forecast_json = await _forecast(client, lat, lon)
        return _summarize_forecast(forecast_json, days=days, place_label=place)
