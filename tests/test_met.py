import json
import unittest
from unittest.mock import patch, MagicMock
from app.main import app
from app.services.weather.weather_get import process_weather_data
from app.services.weather.weather_get import get_weather_data
from fastapi.testclient import TestClient

lat = 21.37852609079965
lon = 39.79370287864698

class TestMetClient(unittest.TestCase):
    #Mock json/api test
    """def getJson(self):
        with open ('tests/data/test_data_api.json', 'r') as f:
            self.mock_json_data = json.load(f)


    @patch('app.services.weather.weather_get.requests.get')
    def test_get_met(self, mock_get):
        mock_get.return_value.json.return_value = self.mock_json_data
        mock_get.return_value.status_code = 200"""
    
    #CSV parsing test
    #get reference file
    def get_csv_reference(self):
        with open ('tests/data/csv_reference.csv', 'r') as f:
            expected_data = f.read()
            
        self.assertEqual()
