import unittest
from unittest.mock import patch, MagicMock
from app.main import app
from app.services.weather.weather_get import process_weather_data
from app.services.weather.weather_get import get_weather_data
from fastapi.testclient import TestClient

lat = 21.37852609079965
lon = 39.79370287864698

class TestMet(unittest.TestCase):
    @patch('app.services.weather.weather_get_data_v2.requests')
    def test_get_met(self, mock_requests):
        #configure mock return value
        mock_response = mock_requests.get.return_value