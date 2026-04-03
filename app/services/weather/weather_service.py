"""Weather service for fetching and processing MET weather data.

This service provides methods to:
1. Fetch weather data from the MET API
2. Process weather data into CSV format
3. Get weather information for specific coordinates
"""

import csv
import io
import requests


class WeatherService:
    """Service for interacting with MET weather API and processing weather data."""

    INVALID_PAYLOAD_MESSAGE = "Invalid MET payload: missing properties.timeseries list"

    def __init__(
        self,
        base_url: str,
        headers: dict,
        timeout: int = 10,
    ):
        """Initialize the weather service.

        Args:
            base_url: MET API URL
            headers: HTTP headers for MET API requests
            timeout: Request timeout in seconds (defaults to 10)
        """
        self.base_url = base_url
        self.headers = headers
        self.timeout = timeout

    def get_weather_at_location(self, lat: float, lon: float) -> str:
        """Get weather data as CSV for given coordinates.

        This is the main public API method that fetches and processes weather data.

        Args:
            lat: Latitude value
            lon: Longitude value

        Returns:
            str: CSV formatted weather data with columns:
                timestamp, temperature, humidity, wind_speed

        Raises:
            requests.RequestException: If the HTTP request fails
            ValueError: If the response data is invalid
        """
        data = self.fetch_weather_data(lat, lon)
        csv_output = self.process_to_csv(data)
        return csv_output

    def fetch_weather_data(self, latitude: float, longitude: float) -> dict:
        """Fetch MET weather data for one latitude/longitude pair.

        Args:
            latitude: Latitude value
            longitude: Longitude value

        Returns:
            dict: MET response as JSON

        Raises:
            requests.RequestException: Raised if the HTTP request fails
        """
        # Build query values MET expects
        params = {"lat": latitude, "lon": longitude}

        # Call MET API
        response = requests.get(
            self.base_url,
            params=params,
            headers=self.headers,
            timeout=self.timeout,
        )

        # Raise an error for non-200 responses
        response.raise_for_status()

        # Convert response body to Python dict
        return response.json()

    def process_to_csv(self, raw_data: dict) -> str:
        """Convert MET JSON data into CSV text.

        The CSV output has these columns:
        `timestamp`, `temperature`, `humidity`, `wind_speed`.

        Args:
            raw_data: MET response data

        Returns:
            str: CSV text

        Raises:
            ValueError: If `properties.timeseries` is missing or wrong type
            KeyError: If a required weather value is missing in an item
        """
        # First check: the MET data must be a dictionary
        if not isinstance(raw_data, dict):
            raise ValueError(self.INVALID_PAYLOAD_MESSAGE)

        # Next check: MET should include a 'properties' section
        properties = raw_data.get("properties")
        if not isinstance(properties, dict):
            raise ValueError(self.INVALID_PAYLOAD_MESSAGE)

        # Final check: 'timeseries' must be a list of weather time points
        timeseries = properties.get("timeseries")
        if not isinstance(timeseries, list):
            raise ValueError(self.INVALID_PAYLOAD_MESSAGE)

        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)

        # Write CSV header
        writer.writerow(["timestamp", "temperature", "humidity", "wind_speed"])

        # Write one CSV row per MET timeseries item
        for item in timeseries:
            timestamp = item["time"]
            details = item["data"]["instant"]["details"]
            temperature = details["air_temperature"]
            humidity = details["relative_humidity"]
            wind_speed = details["wind_speed"]
            writer.writerow([timestamp, temperature, humidity, wind_speed])

        # Return finished CSV text
        return output.getvalue()
