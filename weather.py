import logging
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("weather")

# Set up logging to stderr (important for stdio servers)
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Constants
NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"


async def make_nws_request(url: str) -> dict[str, Any] | None:
    """Make a request to the NWS API with proper error handling."""
    headers = {"User-Agent": USER_AGENT, "Accept": "application/geo+json"}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code} for {url}: {e.response.text[:200]}")
            return None
        except httpx.RequestError as e:
            logger.error(f"Request error for {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error for {url}: {e}")
            return None


def format_alert(feature: dict) -> str:
    """Format an alert feature into a readable string."""
    props = feature["properties"]
    return f"""
Event: {props.get("event", "Unknown")}
Area: {props.get("areaDesc", "Unknown")}
Severity: {props.get("severity", "Unknown")}
Description: {props.get("description", "No description available")}
Instructions: {props.get("instruction", "No specific instructions provided")}
"""


@mcp.tool()
async def get_alerts(state: str) -> str:
    """Get weather alerts for a US state.

    Args:
        state: Two-letter US state code (e.g. CA, NY)
    """
    # Validate state code format
    state = state.upper().strip()
    if len(state) != 2 or not state.isalpha():
        return f"Error: Invalid state code '{state}'. Please use a two-letter US state code (e.g., CA, NY, TX)."

    url = f"{NWS_API_BASE}/alerts/active/area/{state}"
    data = await make_nws_request(url)

    if not data:
        return f"Error: Unable to fetch alerts for state '{state}'. This may be due to network issues or the NWS API being temporarily unavailable."

    if "features" not in data:
        return f"Error: Invalid response format when fetching alerts for state '{state}'."

    if not data["features"]:
        return f"No active weather alerts for state '{state}'."

    alerts = [format_alert(feature) for feature in data["features"]]
    return "\n---\n".join(alerts)


@mcp.tool()
async def get_forecast(latitude: float, longitude: float) -> str:
    """Get weather forecast for a location.

    Args:
        latitude: Latitude of the location
        longitude: Longitude of the location
    """
    # Validate coordinates are within US bounds (rough check)
    if not (24.0 <= latitude <= 50.0) or not (-125.0 <= longitude <= -66.0):
        return f"Error: The National Weather Service API only provides forecasts for locations within the United States. The coordinates ({latitude}, {longitude}) appear to be outside this range. Please use US coordinates."

    # First get the forecast grid endpoint
    points_url = f"{NWS_API_BASE}/points/{latitude},{longitude}"
    points_data = await make_nws_request(points_url)

    if not points_data:
        return f"Error: Unable to fetch forecast data for location ({latitude}, {longitude}). This may be because:\n- The location is outside the United States (NWS API only covers US territories)\n- Network connectivity issues\n- The NWS API is temporarily unavailable\n\nPlease verify the coordinates are within the US and try again."

    # Check if we got a valid response structure
    if "properties" not in points_data:
        return f"Error: Invalid response from weather service for location ({latitude}, {longitude})."

    # Get the forecast URL from the points response
    if "forecast" not in points_data["properties"]:
        return f"Error: No forecast available for location ({latitude}, {longitude}). This location may not be covered by the National Weather Service."

    forecast_url = points_data["properties"]["forecast"]
    forecast_data = await make_nws_request(forecast_url)

    if not forecast_data:
        return f"Error: Unable to fetch detailed forecast for location ({latitude}, {longitude}). The forecast service may be temporarily unavailable."

    # Validate forecast data structure
    if "properties" not in forecast_data or "periods" not in forecast_data["properties"]:
        return f"Error: Invalid forecast data structure received for location ({latitude}, {longitude})."

    # Format the periods into a readable forecast
    periods = forecast_data["properties"]["periods"]
    if not periods:
        return f"No forecast periods available for location ({latitude}, {longitude})."

    forecasts = []
    for period in periods[:5]:  # Only show next 5 periods
        forecast = f"""
{period["name"]}:
Temperature: {period["temperature"]}°{period["temperatureUnit"]}
Wind: {period["windSpeed"]} {period["windDirection"]}
Forecast: {period["detailedForecast"]}
"""
        forecasts.append(forecast)

    return "\n---\n".join(forecasts)


def main():
    # Initialize and run the server
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
