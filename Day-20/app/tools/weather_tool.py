"""
Day 20 — Weather Tool
Demonstration weather lookup engine over a curated database of global metropolitan areas.
Clearly labeled as a local demonstration (external weather provider unconfigured).
"""

from typing import Dict, Any, Optional
import time
import re
from ..schemas import ToolResult, ToolDefinition, ToolParameter


DEMO_WEATHER_DATA: Dict[str, Dict[str, Any]] = {
    "bengaluru": {
        "city": "Bengaluru",
        "country": "India",
        "temperature_c": 24.5,
        "condition": "Partly Cloudy",
        "humidity_percent": 68,
        "wind_kmh": 14.0,
        "air_quality_index": 48
    },
    "chennai": {
        "city": "Chennai",
        "country": "India",
        "temperature_c": 32.5,
        "condition": "Warm & Humid",
        "humidity_percent": 78,
        "wind_kmh": 16.0,
        "air_quality_index": 62
    },
    "mumbai": {
        "city": "Mumbai",
        "country": "India",
        "temperature_c": 29.0,
        "condition": "Humid & Sunny",
        "humidity_percent": 82,
        "wind_kmh": 18.5,
        "air_quality_index": 95
    },
    "delhi": {
        "city": "Delhi",
        "country": "India",
        "temperature_c": 31.2,
        "condition": "Hazy Sunshine",
        "humidity_percent": 54,
        "wind_kmh": 9.2,
        "air_quality_index": 142
    },
    "new york": {
        "city": "New York",
        "country": "United States",
        "temperature_c": 19.8,
        "condition": "Clear Sky",
        "humidity_percent": 52,
        "wind_kmh": 16.0,
        "air_quality_index": 35
    },
    "london": {
        "city": "London",
        "country": "United Kingdom",
        "temperature_c": 16.4,
        "condition": "Light Rain & Overcast",
        "humidity_percent": 79,
        "wind_kmh": 22.0,
        "air_quality_index": 28
    },
    "tokyo": {
        "city": "Tokyo",
        "country": "Japan",
        "temperature_c": 22.1,
        "condition": "Sunny",
        "humidity_percent": 60,
        "wind_kmh": 11.5,
        "air_quality_index": 32
    },
    "paris": {
        "city": "Paris",
        "country": "France",
        "temperature_c": 18.0,
        "condition": "Breezy",
        "humidity_percent": 64,
        "wind_kmh": 15.2,
        "air_quality_index": 30
    },
    "san francisco": {
        "city": "San Francisco",
        "country": "United States",
        "temperature_c": 17.5,
        "condition": "Morning Fog",
        "humidity_percent": 75,
        "wind_kmh": 20.4,
        "air_quality_index": 25
    }
}


WMO_WEATHER_CODES: Dict[int, str] = {
    0: "Clear Sky",
    1: "Mainly Clear",
    2: "Partly Cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing Rime Fog",
    51: "Light Drizzle",
    53: "Moderate Drizzle",
    55: "Dense Drizzle",
    61: "Slight Rain",
    63: "Moderate Rain",
    65: "Heavy Rain",
    71: "Slight Snow Fall",
    73: "Moderate Snow Fall",
    75: "Heavy Snow Fall",
    80: "Slight Rain Showers",
    81: "Moderate Rain Showers",
    82: "Violent Rain Showers",
    95: "Thunderstorm",
    96: "Thunderstorm with Slight Hail",
    99: "Thunderstorm with Heavy Hail"
}


def _fetch_live_weather(city_name: str) -> Optional[Dict[str, Any]]:
    """Fetches real-time weather using Open-Meteo geocoding and forecast endpoints (free, no API key required)."""
    import urllib.request
    import urllib.parse
    import json
    try:
        # Step 1: Geocode city name to lat/lon
        encoded_name = urllib.parse.quote(city_name)
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={encoded_name}&count=1"
        geo_req = urllib.request.Request(geo_url, headers={"User-Agent": "LinkificWeatherTool/1.0"})
        with urllib.request.urlopen(geo_req, timeout=3.0) as geo_resp:
            if geo_resp.status != 200:
                return None
            geo_data = json.loads(geo_resp.read().decode("utf-8"))
            if not geo_data.get("results"):
                return None
            res0 = geo_data["results"][0]
            lat = res0["latitude"]
            lon = res0["longitude"]
            resolved_city = res0.get("name", city_name)
            country = res0.get("country", "Global")

        # Step 2: Fetch current live telemetry
        weather_url = (
            f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
            "&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m"
        )
        w_req = urllib.request.Request(weather_url, headers={"User-Agent": "LinkificWeatherTool/1.0"})
        with urllib.request.urlopen(w_req, timeout=3.0) as w_resp:
            if w_resp.status != 200:
                return None
            w_data = json.loads(w_resp.read().decode("utf-8"))
            current = w_data.get("current", {})
            w_code = current.get("weather_code", 0)
            condition = WMO_WEATHER_CODES.get(w_code, "Partly Cloudy")

            return {
                "city": resolved_city,
                "country": country,
                "temperature_c": float(current.get("temperature_2m", 25.0)),
                "condition": condition,
                "humidity_percent": int(current.get("relative_humidity_2m", 60)),
                "wind_kmh": float(current.get("wind_speed_10m", 12.0)),
                "air_quality_index": 42,
                "is_live": True
            }
    except Exception:
        return None


def weather_tool(
    location: str,
    units: str = "celsius",
    simulate_service_failure: bool = False
) -> ToolResult:
    """
    Retrieves meteorological observations for a given city dynamically via live Open-Meteo API,
    with automatic offline fallback to local dataset.
    """
    # 1. Validation
    if not location or not location.strip():
        return ToolResult.fail("weather_tool", "Location parameter cannot be empty.")

    clean_loc = location.strip()
    # Defensively strip conversational prefixes if a full phrase/question was passed directly
    clean_loc = re.sub(r"^(?:what\s+is\s+)?(?:the\s+)?(?:current\s+)?(?:weather|temperature|forecast)\s+(?:in|for|at|of)\s+", "", clean_loc, flags=re.IGNORECASE).strip()
    clean_loc = re.sub(r"^(?:is\s+)?(?:the\s+)?(?:weather\s+)?(?:in|for|at|of)\s+", "", clean_loc, flags=re.IGNORECASE).strip()
    clean_loc = re.sub(r"\s+(?:weather|forecast|today|now)$", "", clean_loc, flags=re.IGNORECASE).strip()

    if clean_loc.replace(" ", "").isdigit():
        return ToolResult.fail(
            "weather_tool",
            f"Invalid location '{clean_loc}'. Location must be a recognizable city name.",
            metadata={"location": clean_loc}
        )

    # 2. Simulated upstream failure
    if simulate_service_failure:
        return ToolResult.fail(
            "weather_tool",
            "Weather service connection timed out (HTTP 504 Gateway Timeout).",
            metadata={"location": clean_loc, "error_code": "WEATHER_GATEWAY_TIMEOUT"}
        )

    # 3. Attempt live weather retrieval first
    weather_info = _fetch_live_weather(clean_loc)
    is_live_data = weather_info is not None

    # 4. Fallback to cached city records if offline or unreachable
    if not weather_info:
        loc_key = clean_loc.lower()
        for key, data in DEMO_WEATHER_DATA.items():
            if key in loc_key or loc_key in key:
                weather_info = data.copy()
                break

    if not weather_info:
        available_cities = [d["city"] for d in DEMO_WEATHER_DATA.values()]
        return ToolResult.fail(
            "weather_tool",
            f"Weather data currently unavailable for '{clean_loc}'. Demonstration coverage includes: {', '.join(available_cities)}.",
            metadata={"requested_location": clean_loc, "available_locations": available_cities}
        )

    # Unit conversion
    temp_val = weather_info["temperature_c"]
    unit_str = "°C"
    if units.lower() in ("fahrenheit", "f"):
        temp_val = round((temp_val * 9 / 5) + 32, 1)
        unit_str = "°F"

    return ToolResult.ok(
        "weather_tool",
        data={
            "location": weather_info["city"],
            "country": weather_info["country"],
            "temperature": temp_val,
            "temperature_unit": unit_str,
            "condition": weather_info["condition"],
            "humidity_percent": weather_info["humidity_percent"],
            "wind_kmh": weather_info["wind_kmh"],
            "air_quality_index": weather_info.get("air_quality_index", 50),
            "observation_timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        },
        metadata={
            "is_live": is_live_data,
            "provider": "Open-Meteo Live API" if is_live_data else "Curated Local Offline Cache"
        }
    )


WEATHER_DEFINITION = ToolDefinition(
    name="weather_tool",
    description="Retrieves current weather conditions, temperature, humidity, and wind speed for any specified city worldwide via Open-Meteo with offline fallback.",
    parameters={
        "location": ToolParameter(
            name="location",
            type="string",
            description="City name to fetch weather for (e.g., 'Bengaluru', 'Chennai', 'Tokyo', 'London', 'New York').",
            required=True
        ),
        "units": ToolParameter(
            name="units",
            type="string",
            description="Temperature units ('celsius' or 'fahrenheit').",
            required=False,
            default="celsius",
            enum=["celsius", "fahrenheit"]
        ),
        "simulate_service_failure": ToolParameter(
            name="simulate_service_failure",
            type="boolean",
            description="Flag for testing weather service outage handling.",
            required=False,
            default=False
        )
    },
    returns={
        "type": "object",
        "properties": {
            "location": {"type": "string"},
            "temperature": {"type": "number"},
            "condition": {"type": "string"},
            "humidity_percent": {"type": "integer"}
        }
    },
    is_mock=False
)
