"""Simple helper functions for MET weather data.

This file does two main things:
1. Download weather data from MET.
2. Convert the MET data into CSV text for the TTF calculator.
"""

import csv
import io
import requests
from app.services.weather import weather_static

MET_HEADERS = weather_static.met_required_headers
MET_URL = weather_static.met_base_url
MET_TIMEOUT_SECONDS = 10
INVALID_PAYLOAD_MESSAGE = "Invalid MET payload: missing properties.timeseries list"

def get_weather_data_for_coordinates(latitude: float, longitude: float) -> dict:
    """Get MET weather data for one latitude/longitude pair.

    Args:
        latitude (float): Latitude value.
        longitude (float): Longitude value.

    Returns:
        dict: MET response as JSON.

    Raises:
        requests.RequestException: Raised if the HTTP request fails.
    """
    # Build query values MET expects.
    params = {"lat": latitude, "lon": longitude}

    # Call MET API.
    response = requests.get(MET_URL, params=params, headers=MET_HEADERS, timeout=MET_TIMEOUT_SECONDS)

    # Raise an error for non-200 responses.
    response.raise_for_status()

    # Convert response body to Python dict.
    return response.json()

def process_weather_data(raw_data: dict) -> str:
    """Turn MET JSON data into CSV text.

    The CSV output has these columns:
    `timestamp`, `temperature`, `humidity`, `wind_speed`.

    Args:
        raw_data (dict): MET response data.

    Returns:
        str: CSV text.

    Raises:
        ValueError: If `properties.timeseries` is missing or wrong type.
        KeyError: If a required weather value is missing in an item.
    """
    # First check: the MET data must be a dictionary.
    if not isinstance(raw_data, dict):
        raise ValueError(INVALID_PAYLOAD_MESSAGE)

    # Next check: MET should include a 'properties' section.
    properties = raw_data.get("properties")
    if not isinstance(properties, dict):
        raise ValueError(INVALID_PAYLOAD_MESSAGE)

    # Final check: 'timeseries' must be a list of weather time points.
    timeseries = properties.get("timeseries")
    if not isinstance(timeseries, list):
        raise ValueError(INVALID_PAYLOAD_MESSAGE)

    # Create CSV in memory.
    output = io.StringIO()
    writer = csv.writer(output)

    # Write CSV header.
    writer.writerow(["timestamp", "temperature", "humidity", "wind_speed"])

    # Write one CSV row per MET timeseries item.
    for item in timeseries:
        timestamp = item["time"]
        details = item["data"]["instant"]["details"]
        temperature = details["air_temperature"]
        humidity = details["relative_humidity"]
        wind_speed = details["wind_speed"]
        writer.writerow([timestamp, temperature, humidity, wind_speed])

    # Return finished CSV text.
    return output.getvalue()
