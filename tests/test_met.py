"""Tests for MET weather service.

These tests check that we can:
- fetch data,
- handle request errors,
- convert MET JSON to CSV,
- handle invalid input safely.

Note:
We use Mock/patch to fake MET API calls in tests.
This keeps tests fast and stable without the need for real network requests.
"""

import pandas as pd
from pandas.api.types import is_numeric_dtype
import io
import json
import unittest
from unittest.mock import Mock, patch
import requests

from app.services.weather.weather_service import WeatherService


class TestWeatherService(unittest.TestCase):
    """Tests for WeatherService class methods."""

    def setUp(self):
        """Create a WeatherService instance for each test."""
        self.weather_service = WeatherService(
            base_url="https://api.met.no/weatherapi/locationforecast/2.0/compact",
            headers={"User-Agent": "Firebuster/1.0 (firebuster.no)"},
            timeout=10,
        )

    @patch("app.services.weather.weather_service.requests.get")
    def test_fetch_weather_data_success(self, mock_get):
        """Should return JSON when the MET call is successful."""
        # Arrange
        # Fake API payload we expect back from MET.
        expected_payload = {"properties": {"timeseries": []}}

        # Build a fake HTTP response object.
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = expected_payload
        mock_get.return_value = mock_response

        # Act
        # Run the method under test.
        result = self.weather_service._fetch_weather_data(61.452, 5.857)

        # Assert
        # Check returned JSON data.
        self.assertEqual(expected_payload, result)

        # Check that one HTTP request was made.
        mock_get.assert_called_once()

        # Check that HTTP status validation was called.
        mock_response.raise_for_status.assert_called_once()

        # Read the arguments used in requests.get(...).
        _, kwargs = mock_get.call_args

        # Check that coordinates were passed correctly.
        self.assertEqual({"lat": 61.452, "lon": 5.857}, kwargs["params"])

        # Check that timeout value is sent.
        self.assertEqual(10, kwargs["timeout"])

    @patch("app.services.weather.weather_service.requests.get")
    def test_fetch_weather_data_http_error_raises(self, mock_get):
        """Should raise HTTPError when MET returns an HTTP error."""
        # Arrange
        # Fake response where raise_for_status throws HTTPError.
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.HTTPError(
            "MET API failure"
        )
        mock_get.return_value = mock_response

        # Act + Assert
        # Verify the same error type bubbles up from our method.
        with self.assertRaises(requests.HTTPError):
            self.weather_service._fetch_weather_data(61.452, 5.857)

    @patch("app.services.weather.weather_service.requests.get")
    def test_fetch_weather_data_request_failure_raises(self, mock_get):
        """Should raise RequestException on network/request failure."""
        # Arrange
        # Simulate a network/transport failure before a response is returned.
        mock_get.side_effect = requests.RequestException("Network error")

        # Act + Assert
        # Verify our method does not hide the request exception.
        with self.assertRaises(requests.RequestException):
            self.weather_service._fetch_weather_data(61.452, 5.857)

    def test_process_to_csv_with_real_data(self):
        """Should convert sample MET JSON into valid CSV output."""
        # Arrange
        with open("tests/data/json_reference.json", "r") as f:
            json_data = json.load(f)

        # Act
        # Convert JSON to CSV text.
        csv_output = self.weather_service._process_to_csv(json_data)

        # Assert
        # Check that output is a string.
        self.assertIsInstance(csv_output, str)
        # Check that output is not empty.
        self.assertTrue(csv_output.strip())

        # Read CSV text into a DataFrame.
        df = pd.read_csv(io.StringIO(csv_output))

        # Check expected column names.
        expected_columns = ["timestamp", "temperature", "humidity", "wind_speed"]
        self.assertListEqual(list(df.columns), expected_columns)

        # Check that there are no missing values.
        self.assertFalse(df.isnull().any().any(), "CSV contains missing values")
        # Check that every timestamp is present.
        self.assertTrue(df["timestamp"].astype(str).str.len().gt(0).all())
        # Check that number columns are numeric.
        self.assertTrue(is_numeric_dtype(df["temperature"]))
        self.assertTrue(is_numeric_dtype(df["humidity"]))
        self.assertTrue(is_numeric_dtype(df["wind_speed"]))

    def test_process_to_csv_malformed_payload_raises(self):
        """Should raise ValueError if required MET fields are missing."""
        # Arrange
        # This payload is missing properties.timeseries on purpose.
        malformed_payload = {"type": "Feature"}

        # Act + Assert
        # Verify we get a clear validation error.
        with self.assertRaises(ValueError) as context:
            self.weather_service._process_to_csv(malformed_payload)

        # Assert
        # Check that the message points to the missing field path.
        self.assertIn("properties.timeseries", str(context.exception))

    def test_process_to_csv_empty_timeseries_returns_header_only(self):
        """Should return only the CSV header when timeseries is empty."""
        # Arrange
        # Valid MET shape, but with no rows.
        payload = {"properties": {"timeseries": []}}

        # Act
        # Convert to CSV.
        csv_output = self.weather_service._process_to_csv(payload)

        # Assert
        # With no rows, only header line should be present.
        self.assertEqual("timestamp,temperature,humidity,wind_speed\r\n", csv_output)

    @patch("app.services.weather.weather_service.requests.get")
    def test_get_weather_at_location_integration(self, mock_get):
        """Should fetch and process weather data end-to-end."""
        # Arrange
        # Create a minimal valid MET response.
        api_response = {
            "properties": {
                "timeseries": [
                    {
                        "time": "2024-01-01T12:00:00Z",
                        "data": {
                            "instant": {
                                "details": {
                                    "air_temperature": 5.2,
                                    "relative_humidity": 80.0,
                                    "wind_speed": 3.5,
                                }
                            }
                        },
                    }
                ]
            }
        }

        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = api_response
        mock_get.return_value = mock_response

        # Act
        # Call the main public API method.
        csv_output = self.weather_service.get_weather_at_location(61.452, 5.857)

        # Assert
        # Check that we got CSV output.
        self.assertIsInstance(csv_output, str)
        self.assertIn("timestamp,temperature,humidity,wind_speed", csv_output)
        self.assertIn("2024-01-01T12:00:00Z", csv_output)
        self.assertIn("5.2", csv_output)
        self.assertIn("80.0", csv_output)
        self.assertIn("3.5", csv_output)

    def test_custom_initialization(self):
        """Should allow custom configuration via constructor."""
        # Arrange & Act
        custom_service = WeatherService(
            base_url="https://custom.api.com",
            headers={"Custom-Header": "value"},
            timeout=30,
        )

        # Assert
        self.assertEqual("https://custom.api.com", custom_service.base_url)
        self.assertEqual({"Custom-Header": "value"}, custom_service.headers)
        self.assertEqual(30, custom_service.timeout)
